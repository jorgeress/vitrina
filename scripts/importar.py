#!/usr/bin/env python3
"""Crea fichas en la vault a partir de lo que ya tienes en otros sitios.

  letterboxd-rss USUARIO   peliculas: el diario publico del perfil
  letterboxd-watchlist USUARIO  peliculas: lo que tienes por ver
  letterboxd RUTA          peliculas: el export CSV, si tienes cuenta Pro
  steam RUTA               juegos: la pagina del perfil o el export
  listenbrainz USUARIO     discos: lo mas escuchado, sin clave ninguna
  spotify-export RUTA      discos: lo mismo desde el zip de Spotify
  spotify-export --canciones   tus canciones guardadas, plegadas en discos
  libro TITULO             libros: uno a uno, buscando en Open Library

Las cinco primeras vuelcan de golpe una lista que ya es tuya. Los libros van
aparte porque no hay tal lista: se busca en el catalogo y eliges tu. Eso ultimo
sirve igual para las otras tres secciones, asi que vive en scripts/nueva.py y
`libro` es la misma alta llamando alli.

Ninguna de estas vias pide pagar ni registrar una aplicacion. Se antepone el
nombre del script: scripts/importar.py letterboxd-rss tu_usuario

Por defecto va en modo rapido: solo entra lo que da senal de haberte importado
(8 horas jugadas en Steam, 4 estrellas en Letterboxd). Con --completo entra
todo, y los umbrales se mueven con --min-horas y --min-nota.

Todo entra en borrador: `draft: true`, `rating` vacia y el cuerpo en blanco. La
excepcion son las peliculas, que si traen tu puntuacion porque Letterboxd es la
unica de las tres fuentes que sabe si algo te gusto. La web no publica lo que
lleva `draft`, asi que la web sigue enseñando solo lo que hayas ascendido a
mano; en Obsidian se ven todas. Con --sin-borrador entran publicadas.

Nunca se pisa una ficha que ya exista, asi que se puede repetir cuando quieras
para recoger solo lo nuevo. Despues conviene pasar scripts/portadas.py.
"""

import argparse
import csv
import html
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import estado
import nueva
from idioma import ayuda, opciones
from vitrina import CARPETAS, ESTADOS, _, escribir_ficha, estado_de, parecidos, pedir

# Umbrales del modo rapido. Ninguna fuente sabe si algo te gusto salvo
# Letterboxd, asi que el resto se criba por la unica senal que dan: el uso.
MIN_HORAS = 8
MIN_NOTA = 8  # cuatro estrellas de Letterboxd
MIN_MS = 20 * 60 * 1000  # menos de veinte minutos no es "lo mas escuchado"
MIN_FAVORITAS = 3  # canciones tuyas en un disco para llamarlo favorito


def plural(n, singular, plural_):
    return f"{n} {singular if n == 1 else plural_}"


def ficheros(ruta, patron):
    """Saca los ficheros que encajen, venga la ruta como zip, carpeta o fichero."""
    ruta = Path(ruta).expanduser()
    if ruta.is_file() and ruta.suffix.lower() == ".zip":
        with zipfile.ZipFile(ruta) as z:
            for nombre in z.namelist():
                if re.search(patron, Path(nombre).name, re.I):
                    yield Path(nombre).name, z.read(nombre)
    elif ruta.is_dir():
        for p in sorted(ruta.rglob("*")):
            if p.is_file() and re.search(patron, p.name, re.I):
                yield p.name, p.read_bytes()
    elif ruta.is_file():
        yield ruta.name, ruta.read_bytes()


# --- Letterboxd --------------------------------------------------------------

def importar_letterboxd(args):
    """El export trae un csv por lista; interesan las notas, lo visto y la watchlist."""
    pelis = {}
    encontrados = []
    for nombre, datos in ficheros(args.ruta, r"\.csv$"):
        filas = list(csv.DictReader(io.StringIO(datos.decode("utf-8-sig"))))
        if not filas or "Name" not in filas[0]:
            continue
        encontrados.append(f"{nombre} ({len(filas)})")
        for fila in filas:
            titulo = (fila.get("Name") or "").strip()
            if not titulo:
                continue
            peli = pelis.setdefault(titulo, {"year": fila.get("Year"), "rating": None,
                                             "status": "finished"})
            if "watchlist" in nombre.lower():
                peli["status"] = "pending"
            else:
                peli["status"] = "finished"
            if fila.get("Rating"):
                # Letterboxd puntua de 0,5 a 5 estrellas; aqui la escala es de 1 a 10.
                peli["rating"] = int(round(float(fila["Rating"]) * 2))

    if not encontrados:
        print(_("No he encontrado ningún csv de Letterboxd en esa ruta."))
        return 1
    print(_("Leído: {que}").format(que=", ".join(encontrados)))
    return volcar(pelis, "film", args)


def importar_letterboxd_rss(args):
    """El diario publico del perfil, que no pide cuenta de pago.

    Da menos historial que el export (las ultimas cien entradas mas o menos)
    pero exactamente el mismo dato: titulo, año y tu puntuacion.
    """
    usuario = args.usuario.strip().strip("/").split("/")[-1]
    crudo = pedir(f"https://letterboxd.com/{usuario}/rss/", binario=True)
    if not crudo:
        print(_("No he podido leer el diario de '{usuario}'. Comprueba el nombre y\n"
                "que el perfil no sea privado.").format(usuario=usuario))
        return 1

    espacio = {"letterboxd": "https://letterboxd.com"}
    pelis = {}
    for entrada in ElementTree.fromstring(crudo).iter("item"):
        titulo = entrada.findtext("letterboxd:filmTitle", namespaces=espacio)
        if not titulo:
            continue  # las listas y las reseñas sueltas no traen pelicula
        nota = entrada.findtext("letterboxd:memberRating", namespaces=espacio)
        año = entrada.findtext("letterboxd:filmYear", namespaces=espacio)
        # El enlace de la entrada apunta a la pelicula, asi que el diario ya
        # trae identificada cada una: es de donde sale el cartel, y ahorra
        # tener que volver a dar con ella por titulo y año.
        enlace = re.search(r"/film/([^/]+)/", entrada.findtext("link") or "")
        pelis[titulo] = {
            "year": año,
            "status": "finished",
            "rating": int(round(float(nota) * 2)) if nota else None,
            "letterboxd": enlace.group(1) if enlace else None,
        }

    if not pelis:
        print(_("El diario no tiene entradas de películas."))
        return 1
    print(_("Diario de {usuario}: {n} películas.").format(usuario=usuario, n=len(pelis)))
    return volcar(pelis, "film", args)


# --- Steam -------------------------------------------------------------------

def buscar_juegos(dato, hallados):
    """Recorre el volcado buscando cosas con appid y nombre.

    El export de Steam ha cambiado de forma varias veces, asi que en vez de
    dar por buena una ruta concreta se rastrea el JSON entero.
    """
    if isinstance(dato, dict):
        appid = dato.get("appid") or dato.get("appId") or dato.get("app_id")
        nombre = dato.get("name") or dato.get("game_name") or dato.get("app_name")
        if appid and nombre:
            minutos = (dato.get("playtime_forever") or dato.get("playtime")
                       or dato.get("playtime_minutes") or 0)
            try:
                minutos = int(minutos)
            except (TypeError, ValueError):
                minutos = 0
            previo = hallados.get(str(nombre))
            if previo is None or minutos > previo["minutos"]:
                hallados[str(nombre)] = {"minutos": minutos, "appid": int(appid),
                                         "capsule": dato.get("capsule_filename")}
        for v in dato.values():
            buscar_juegos(v, hallados)
    elif isinstance(dato, list):
        for v in dato:
            buscar_juegos(v, hallados)


def juegos_de_xml(texto, hallados):
    """La pagina de juegos del perfil con ?xml=1, guardada desde el navegador."""
    for juego in ElementTree.fromstring(texto).iter("game"):
        nombre = juego.findtext("name")
        if not nombre:
            continue
        horas = (juego.findtext("hoursOnRecord") or "0").replace(",", "")
        try:
            minutos = int(float(horas) * 60)
        except ValueError:
            minutos = 0
        hallados[nombre] = {"minutos": minutos}


JUEGO_SUELTO = re.compile(r'\{[^{}]*?"appid":\s*\d+[^{}]*?\}')


def juegos_de_html(texto, hallados):
    """La pagina del perfil, guardada desde el navegador.

    La lista no esta en el HTML visible sino en un JSON dentro de un <script>,
    y viene escapada dos veces: una por ser una cadena JSON y otra por ir
    dentro del propio script. Como el numero de vueltas depende de como la
    guarde cada navegador, se desescapa poco a poco y se mira en cada vuelta,
    en vez de dar por buena una forma concreta.
    """
    for patron in (r'data-profile-gameslist="([^"]*)"', r"var rgGames = (\[.*?\]);"):
        m = re.search(patron, texto, re.S)
        if m:
            try:
                buscar_juegos(json.loads(html.unescape(m.group(1))), hallados)
                return
            except json.JSONDecodeError:
                pass

    variante = texto
    for _intento in range(4):
        for trozo in JUEGO_SUELTO.findall(variante):
            try:
                buscar_juegos(json.loads(trozo), hallados)
            except json.JSONDecodeError:
                continue
        siguiente = variante.replace('\\"', '"').replace("\\/", "/")
        if siguiente == variante:
            return
        variante = siguiente


# Cada pelicula de la parrilla, que Letterboxd pinta con el titulo y el slug en
# los atributos del componente: data-item-name="NAZA (2026)" data-item-slug="naza".
# El slug es el mismo id que ya guardan las fichas y del que sale el cartel, asi
# que la watchlist entra identificada y no hay que volver a buscar nada por
# titulo. El orden de los dos atributos es el que pinta la pagina.
WATCHLIST_RE = re.compile(r'data-item-name="([^"]*)"[^>]*?data-item-slug="([^"]*)"')

# La watchlist de alguien que lleva años puede ser larga, pero no infinita: es
# un tope por si la paginacion cambia y el bucle no encuentra donde parar.
MAX_PAGINAS = 60


def importar_letterboxd_watchlist(args):
    """La watchlist publica del perfil, que es la otra mitad de Letterboxd.

    El diario RSS solo sabe lo que ya has visto, asi que importando solo de ahi
    la seccion entra entera como `terminado` y la pestaña "Por ver" se queda
    vacia. Esto es lo que la llena, y sin cuenta de pago: la watchlist es una
    pagina publica como el diario.

    No pasa por la criba de los umbrales. La criba esta para separar lo que de
    verdad has usado de lo que solo estaba en la lista --ocho horas jugadas,
    cuatro estrellas--, y en una watchlist no hay tal señal ni puede haberla:
    nada de lo que hay dentro lo has visto. La lista entera es la señal.
    """
    usuario = args.usuario.strip().strip("/").split("/")[-1]
    pelis = {}
    for pagina in range(1, MAX_PAGINAS + 1):
        url = f"https://letterboxd.com/{usuario}/watchlist/"
        if pagina > 1:
            url += f"page/{pagina}/"
        crudo = pedir(url, binario=True)
        if not crudo:
            if pagina == 1:
                print(_("No he podido leer la watchlist de '{usuario}'. Comprueba el\n"
                        "nombre y que el perfil no sea privado.").format(usuario=usuario))
                return 1
            break  # se acabaron las paginas, o Letterboxd ha dejado de responder

        encontradas = WATCHLIST_RE.findall(crudo.decode("utf-8", "replace"))
        if not encontradas:
            break
        for nombre, slug in encontradas:
            nombre = html.unescape(nombre).strip()
            # "NAZA (2026)": el año va detras, entre parentesis.
            m = re.match(r"^(.*?)\s*\((\d{4})\)$", nombre)
            titulo = (m.group(1) if m else nombre).strip()
            if not titulo:
                continue
            pelis[titulo] = {
                "year": m.group(2) if m else None,
                # Lo que define a la lista: son las que no has visto. La nota se
                # queda vacia, que es lo unico cierto de algo sin ver.
                "status": "pending",
                "rating": None,
                "letterboxd": slug or None,
            }

    if not pelis:
        print(_("La watchlist de '{usuario}' está vacía o no es pública.").format(usuario=usuario))
        return 1
    print(_("Leída la watchlist de {usuario}: {cuantas}.").format(
        usuario=usuario, cuantas=plural(len(pelis), _("película"), _("películas"))))
    return volcar(pelis, "film", args, cribar=False)


def importar_steam(args):
    hallados = {}
    leidos = []
    for nombre, datos in ficheros(args.ruta, r"\.(json|xml|html?)$"):
        texto = datos.decode("utf-8", "replace")
        antes = len(hallados)
        try:
            if texto.lstrip().startswith("<?xml") or "<gamesList" in texto[:2000]:
                juegos_de_xml(texto, hallados)
            elif texto.lstrip().startswith("<"):
                juegos_de_html(texto, hallados)
            else:
                buscar_juegos(json.loads(texto), hallados)
        except (json.JSONDecodeError, ElementTree.ParseError):
            continue
        if len(hallados) > antes:
            leidos.append(nombre)
    if not hallados:
        print(_("No he encontrado juegos en esa ruta. Lo que entiende:\n"
                "  - steamcommunity.com/my/games?tab=all guardada con Ctrl+S,\n"
                "    con la sesión abierta\n"
                "  - el zip del export de datos de Steam"))
        return 1
    print(_("Leído: {que}").format(que=", ".join(leidos[:6]) + (" ..." if len(leidos) > 6 else "")))

    juegos = {}
    for titulo, dato in hallados.items():
        horas = round(dato["minutos"] / 60)
        juegos[titulo] = {
            # Steam sabe cuanto has jugado, no si lo terminaste. Lo que nunca
            # has abierto si es "pending" sin discusion; lo jugado se queda
            # en blanco y lo pones tu. Antes entraba como "in-progress", y como
            # eso le tocaba a todo lo que tuviera una hora, los 44 juegos
            # decian lo mismo: un campo que contesta igual siempre no es un
            # dato, y desde que la ficha lo enseña encima cantaba.
            "status": "pending" if dato["minutos"] == 0 else None,
            # Las horas deciden que entra en el modo rapido, y ahi se quedan:
            # no van a la ficha. Eran el unico campo que solo sabia rellenar
            # una fuente, y ataban la seccion a Steam --un juego apuntado a
            # mano no las traia y caia en "Por jugar" aunque lo hubieras
            # terminado--. Lo que reparte la seccion es `status`, como en las
            # otras cuatro.
            "horas": horas or None,
            "appid": dato.get("appid"),
            "capsule": dato.get("capsule"),
        }
    return volcar(juegos, "game", args)


# --- ListenBrainz ------------------------------------------------------------

# Las ventanas que admite su API de estadisticas.
RANGOS = {"mes": ("month", "del último mes"),
          "trimestre": ("quarter", "del último trimestre"),
          "semestre": ("half_yearly", "del último medio año"),
          "año": ("year", "del último año"),
          "todo": ("all_time", "de siempre")}
# Los mismos, con su nombre en ingles.
RANGOS.update({"month": RANGOS["mes"], "quarter": RANGOS["trimestre"],
               "half": RANGOS["semestre"], "year": RANGOS["año"], "all": RANGOS["todo"]})


def importar_listenbrainz(args):
    """Los discos mas escuchados, de MusicBrainz y sin clave ninguna.

    ListenBrainz es el registro de escuchas de MusicBrainz, la misma gente del
    Cover Art Archive de donde salen las caratulas. Su API de estadisticas se
    lee sin registrarse y ademas devuelve el mbid del disco, asi que la portada
    se baja luego exacta en vez de por busqueda de texto.
    """
    usuario = args.usuario.strip().strip("/").split("/")[-1]
    rango, cuando = RANGOS[args.periodo]
    datos = pedir(f"https://api.listenbrainz.org/1/stats/user/{usuario}/releases"
                  f"?count={args.top}&range={rango}")
    if datos is None:
        print(_("No he podido leer las estadísticas de '{usuario}'. Comprueba el\n"
                "nombre de usuario en listenbrainz.org.").format(usuario=usuario))
        return 1

    lanzamientos = (datos.get("payload") or {}).get("releases") or []
    if not lanzamientos:
        print(_("'{usuario}' no tiene escuchas registradas en esa ventana.\n"
                "Si acabas de crear la cuenta, conecta Spotify o sube tu historial\n"
                "ampliado en listenbrainz.org/settings/import y vuelve luego.").format(usuario=usuario))
        return 1

    discos = {}
    for disco in lanzamientos:
        titulo = disco.get("release_name")
        if not titulo:
            continue
        discos[titulo] = {"author": disco.get("artist_name"), "status": "finished",
                          "mbid": disco.get("caa_release_mbid") or disco.get("release_mbid")}
    print(_("{cuantos} entre lo más escuchado {cuando}.").format(
        cuantos=plural(len(discos), _("disco"), _("discos")), cuando=_(cuando)))
    return volcar(discos, "album", args, cribar=False)


# --- Spotify, por export -----------------------------------------------------

def sacar(fila, *claves):
    for clave in claves:
        if fila.get(clave):
            return fila[clave]
    return None


def canciones_en_discos(contenido, discos):
    """Pliega tus canciones guardadas en los discos que las llevan.

    Spotify guarda las canciones una a una y en ningun sitio dice que disco te
    gusta: eso hay que contarlo. Un disco con once canciones tuyas dentro te
    gusta mas que uno con una, y esa cuenta no es una suposicion, es el dato.
    Por eso este es el unico sitio del repo donde `favorite` sale de un script
    y no de tu mano: porque se mide, no se adivina.
    """
    for pista in contenido.get("tracks") or []:
        titulo = sacar(pista, "album", "album_name", "albumName")
        if not titulo:
            continue
        dato = discos.setdefault(titulo, {"favoritas": 0, "author": None,
                                          "status": "finished"})
        dato["favoritas"] += 1
        dato["author"] = dato["author"] or sacar(
            pista, "artist", "artist_name", "artistName")
    return discos


def importar_spotify_export(args):
    """Lee el zip de Spotify sin necesidad de crear ninguna app.

    Hay dos exports y no dan lo mismo. El de la cuenta trae YourLibrary.json
    (lo guardado) y un historial reciente que NO lleva el nombre del album,
    asi que de ese historial no salen discos. El historial ampliado, que tarda
    hasta un mes, si lleva el album de cada reproduccion, y ese es el que
    permite ordenar por lo mas escuchado de verdad.
    """
    guardados, escuchados, sin_album = {}, {}, 0
    canciones = {}
    leidos, historial_corto = [], False
    for nombre, datos in ficheros(args.ruta, r"\.json$"):
        try:
            contenido = json.loads(datos.decode("utf-8", "replace"))
        except json.JSONDecodeError:
            continue

        if isinstance(contenido, dict) and ("albums" in contenido
                                            or "tracks" in contenido):
            canciones_en_discos(contenido, canciones)
            for album in contenido.get("albums") or []:
                titulo = sacar(album, "album", "album_name", "name")
                if titulo:
                    guardados[titulo] = {"author": sacar(album, "artist", "artist_name"),
                                         "status": "finished"}
            leidos.append(nombre)
            continue

        if isinstance(contenido, list) and contenido and isinstance(contenido[0], dict):
            reproducciones = 0
            for fila in contenido:
                titulo = sacar(fila, "master_metadata_album_album_name", "albumName")
                ms = sacar(fila, "ms_played", "msPlayed") or 0
                if not titulo:
                    if sacar(fila, "master_metadata_track_name", "trackName"):
                        sin_album += 1
                        historial_corto = True
                    continue
                dato = escuchados.setdefault(titulo, {"ms": 0, "author": None,
                                                      "status": "finished"})
                dato["ms"] += int(ms)
                dato["author"] = dato["author"] or sacar(
                    fila, "master_metadata_album_artist_name", "artistName")
                reproducciones += 1
            if reproducciones:
                leidos.append(nombre)

    if not leidos and not historial_corto:
        print(_("No he encontrado datos de Spotify en esa ruta."))
        return 1
    if leidos:
        print(_("Leído: {que}").format(que=", ".join(leidos[:5]) + (" ..." if len(leidos) > 5 else "")))
    if sin_album:
        print(_("{n} reproducción(es) sin nombre de álbum. Eso es el historial\n"
                "corto del export de la cuenta, que no lo trae: para ordenar por lo más\n"
                "escuchado hace falta pedir el historial ampliado, que tarda hasta un mes.").format(
                    n=sin_album))

    if args.canciones:
        if not canciones:
            print(_("No he encontrado canciones guardadas en esa ruta. Van en la\n"
                    "clave tracks de YourLibrary.json, que trae el export de la cuenta."))
            return 1
        for dato in canciones.values():
            dato["favorite"] = dato["favoritas"] >= args.min_favoritas
        total = sum(d["favoritas"] for d in canciones.values())
        marcados = sum(1 for d in canciones.values() if d["favorite"])
        print(_("{canciones} guardadas en {discos}.").format(
            canciones=plural(total, _("canción"), _("canciones")),
            discos=plural(len(canciones), _("disco"), _("discos"))))
        print(_("{n} disco(s) con {minimo} o más entran como favoritos.").format(
            n=marcados, minimo=args.min_favoritas))
        return volcar(canciones, "album", args)

    if args.completo:
        if not guardados:
            print(_("No hay YourLibrary.json en esa ruta, que es donde va lo guardado."))
            return 1
        print(_("{n} álbum(es) guardado(s).").format(n=len(guardados)))
        return volcar(guardados, "album", args, cribar=False)

    if not escuchados:
        print("\n" + _("Sin historial con álbum no puedo ordenar por lo más escuchado.\n"
                       "Con --completo entran los álbumes guardados que traiga el export."))
        return 1
    oidos = {k: v for k, v in escuchados.items() if v["ms"] >= MIN_MS}
    mejores = sorted(oidos, key=lambda k: oidos[k]["ms"], reverse=True)[:args.top]
    discos = {t: {"author": oidos[t]["author"], "status": "finished"} for t in mejores}
    ms = sum(oidos[t]["ms"] for t in mejores)
    tiempo = (plural(round(ms / 3600000), _("hora"), _("horas")) if ms >= 3600000
              else plural(round(ms / 60000), _("minuto"), _("minutos")))
    print(_("{n} disco(s) entre lo más escuchado ({tiempo} en total).").format(
        n=len(discos), tiempo=tiempo))
    return volcar(discos, "album", args, cribar=False)


# --- Open Library, obra a obra -----------------------------------------------

# Lo que hace falta para pintar una linea de resultado y para dejar la ficha
# lista: el cover_i es el identificador de la portada, y con el se baja exacta.
def importar_libro(args):
    """Un libro suelto, que es un alta normal de scripts/nueva.py.

    Las otras fuentes vuelcan tu biblioteca entera de golpe porque es tuya y ya
    esta elegida. Con los libros no hay biblioteca que volcar: hay un catalogo
    publico, asi que la eleccion la haces tu obra a obra, como en un buscador.
    Eso es exactamente lo que hace nueva.py con los cinco tipos, asi que aqui
    solo se traducen las opciones y se llama alli; el nombre se queda por
    costumbre y porque esta documentado.
    """
    args.tipo = "book"
    args.favorito = False
    args.borrador = not args.sin_borrador
    # Open Library devuelve el titulo en latino, asi que aqui nunca hace falta.
    args.fichero = None
    return nueva.alta(args)


# --- comun -------------------------------------------------------------------

def criba(elementos, args):
    """Aparta lo que no llega al umbral. Devuelve lo que entra y lo que no."""
    if args.completo:
        return elementos, {}
    dentro, fuera = {}, {}
    for titulo, dato in elementos.items():
        if dato.get("horas") is not None:
            pasa = dato["horas"] >= args.min_horas
        elif dato.get("favoritas") is not None:
            pasa = dato["favoritas"] >= args.min_favoritas
        elif dato.get("rating") is not None:
            pasa = dato["rating"] >= args.min_nota
        else:
            # Sin horas ni nota no hay con que decidir: fuera del modo rapido.
            pasa = False
        (dentro if pasa else fuera)[titulo] = dato
    return dentro, fuera


def volcar(elementos, tipo, args, cribar=True):
    carpeta = CARPETAS[tipo]
    elementos, apartados = criba(elementos, args) if cribar else (elementos, {})
    avisos = parecidos(carpeta, elementos)
    nuevas = repetidas = 0
    for titulo, dato in sorted(elementos.items()):
        campos = {"type": tipo, "year": dato.get("year"), "author": dato.get("author"),
                  # Sin defecto: una fuente que no sabe el estado lo deja en
                  # blanco, como la nota. Inventarle "pending" a lo que ya
                  # has jugado es tan falso como decir que sigue en curso.
                  "rating": dato.get("rating"), "status": dato.get("status"),
                  "favorite": dato.get("favorite", False),
                  "cover": None, "tags": None}
        if dato.get("favoritas"):
            # Cuantas de tus canciones guardadas lleva el disco. Es lo que
            # ordena la vista "Por tus canciones" de Musica.base.
            campos["favorite_tracks"] = dato["favoritas"]
        if dato.get("mbid"):
            # El identificador del disco en MusicBrainz: con el, la portada se
            # baja exacta y no por parecido de nombre.
            campos["mbid"] = dato["mbid"]
        if dato.get("letterboxd"):
            # Y lo mismo para las peliculas: con el id, el cartel sale de
            # Letterboxd a 1000 px en vez de los 220 a los que lo deja
            # Wikipedia, y la direccion viene en la misma peticion.
            campos["letterboxd"] = dato["letterboxd"]
        if dato.get("appid"):
            # Lo mismo para los juegos: buscar por nombre falla con los
            # free-to-play, y con el appid la caratula sale siempre.
            campos["appid"] = dato["appid"]
        if dato.get("capsule") and "/" in str(dato["capsule"]):
            # Los juegos recientes no estan en la ruta clasica del CDN: su
            # caratula cuelga de un hash que solo aparece en tu propia pagina.
            campos["capsule"] = dato["capsule"]
        if args.dry_run:
            nuevas += 1
            continue
        if escribir_ficha(carpeta, titulo, campos, borrador=not args.sin_borrador):
            nuevas += 1
        else:
            repetidas += 1

    hecho = (_("{n} ficha(s) se crearían en {carpeta}, {ya} ya estaba(n).") if args.dry_run
             else _("{n} ficha(s) creada(s) en {carpeta}, {ya} ya estaba(n)."))
    print("\n" + hecho.format(n=nuevas, carpeta=f"content/{carpeta}/", ya=repetidas))
    if apartados:
        umbral = (_("menos de {n} horas").format(n=args.min_horas) if tipo == "game"
                  else _("menos de {n} canciones tuyas").format(n=args.min_favoritas)
                  if tipo == "album"
                  else _("nota por debajo de {n}, o ninguna").format(n=args.min_nota))
        print(_("{n} ficha(s) apartada(s) por el modo rápido ({umbral}). Con --completo entran todas.").format(
            n=len(apartados), umbral=umbral))
    if avisos:
        print("\n" + _("Se parecen a fichas que ya tenías. Si son la misma obra, únelas:"))
        for aviso in avisos:
            print("  " + aviso)
    if nuevas and not args.dry_run:
        if not args.sin_borrador:
            print(_("Entran con draft: true, así que no salen en la web hasta que les\n"
                    "quites la línea. En Obsidian se ven todas."))
        print(_("Ahora: scripts/al-dia.py"))
    return 0


def main():
    p = argparse.ArgumentParser(description=ayuda(__doc__, "importar"),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help=_("dice qué haría, sin escribir"))
    p.add_argument(*opciones("--completo", "--all"), dest="completo", action="store_true",
                   help=_("sin umbrales: entra todo lo que traiga el export"))
    p.add_argument(*opciones("--min-horas", "--min-hours"), dest="min_horas", type=int, default=MIN_HORAS,
                   help=_("juegos: horas mínimas jugadas (por defecto {n})").format(n=MIN_HORAS))
    p.add_argument(*opciones("--min-favoritas", "--min-favorites"), dest="min_favoritas", type=int,
                   default=MIN_FAVORITAS,
                   help=_("discos: canciones tuyas mínimas (por defecto {n})").format(n=MIN_FAVORITAS))
    p.add_argument(*opciones("--min-nota", "--min-rating"), dest="min_nota", type=int, default=MIN_NOTA,
                   help=_("películas: nota mínima (por defecto {n}, o sea 4 estrellas)").format(n=MIN_NOTA))
    p.add_argument(*opciones("--sin-borrador", "--no-draft"), dest="sin_borrador", action="store_true",
                   help=_("las fichas entran publicadas, sin draft"))
    subs = p.add_subparsers(dest="fuente", required=True)

    lb = subs.add_parser("letterboxd", help=_("export de Letterboxd"))
    lb.add_argument("ruta", help=_("el .zip del export, la carpeta o un csv suelto"))
    lb.set_defaults(func=importar_letterboxd)

    lr = subs.add_parser("letterboxd-rss", help=_("el diario público, sin cuenta Pro"))
    lr.add_argument("usuario", help=_("tu nombre de usuario en Letterboxd"))
    lr.set_defaults(func=importar_letterboxd_rss)

    lw = subs.add_parser("letterboxd-watchlist",
                         help=_("lo que tienes por ver, sin cuenta Pro"))
    lw.add_argument("usuario", help=_("tu nombre de usuario en Letterboxd"))
    lw.set_defaults(func=importar_letterboxd_watchlist)

    st = subs.add_parser("steam", help=_("export de datos de Steam"))
    st.add_argument("ruta", help=_("el .zip del export o la carpeta"))
    st.set_defaults(func=importar_steam)

    lb = subs.add_parser("listenbrainz", help=_("lo más escuchado, sin clave ninguna"))
    lb.add_argument("usuario", help=_("tu nombre de usuario en listenbrainz.org"))
    lb.add_argument(*opciones("--periodo", "--period"), dest="periodo", choices=list(RANGOS), default="año",
                    help=_("ventana (por defecto, año)"))
    lb.add_argument("--top", type=int, default=40, help=_("cuántos discos (por defecto 40)"))
    lb.set_defaults(func=importar_listenbrainz)

    li = subs.add_parser("libro", aliases=["book"], help=_("busca un libro en Open Library y crea la ficha"))
    li.add_argument("titulo", help=_("el título, o título y autor"))
    li.add_argument(*opciones("--elegir", "--pick"), dest="elegir", type=int, metavar="N",
                    help=_("quédate con el resultado N sin preguntar"))
    li.add_argument(*opciones("--resultados", "--results"), dest="resultados", type=int, default=5,
                    help=_("cuántos resultados enseñar (por defecto 5)"))
    li.add_argument(*opciones("--nota", "--rating"), dest="nota", type=int, help=_("ponle ya la nota, del 1 al 10"))
    li.add_argument(*opciones("--estado", "--status"), dest="estado", type=estado_de,
                    choices=ESTADOS, default="pending",
                    help=_("por defecto, pendiente"))
    li.set_defaults(func=importar_libro)

    se = subs.add_parser("spotify-export", help=_("lo mismo desde el zip, sin crear app"))
    se.add_argument("ruta", help=_("el .zip del export de Spotify o la carpeta"))
    se.add_argument("--top", type=int, default=40, help=_("cuántos discos (por defecto 40)"))
    se.add_argument(*opciones("--canciones", "--tracks"), dest="canciones", action="store_true",
                    help=_("pliega tus canciones guardadas en los discos que las llevan"))
    se.set_defaults(func=importar_spotify_export)

    args = p.parse_args()
    salida = args.func(args)
    if not args.dry_run:
        # Lo nuevo cambia las cifras del README aunque entre en borrador. Las
        # paginas de autor no: lo importado llega sin autor hasta datos.py.
        estado.actualizar_readme(callado=True)
    return salida


if __name__ == "__main__":
    sys.exit(main())
