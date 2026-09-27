#!/usr/bin/env python3
"""Añade una obra suelta: la busca, la eliges tu y deja la ficha entera.

  scripts/nueva.py juego "hollow knight"
  scripts/nueva.py peli "parasite"
  scripts/nueva.py serie "breaking bad"
  scripts/nueva.py album "in rainbows"
  scripts/nueva.py libro "el nombre del viento"
  scripts/nueva.py https://store.steampowered.com/app/367520/Hollow_Knight/

Con el enlace no hay nada que buscar ni que elegir: lleva dentro el
identificador. Valen los de Steam, Letterboxd (tambien los cortos, boxd.it),
TVmaze, MusicBrainz, Open Library y los discos de Spotify, que se buscan en
MusicBrainz por su enlace.

Es lo que hace el buscador de Letterboxd o el de Spotify cuando escribes:
enseñar candidatos con lo justo para distinguirlos, y guardarse el
identificador de lo que elijas en vez del nombre. Eso es lo que hace que la
portada y los datos salgan exactos y se puedan rehacer siempre igual.

Cada tipo pregunta a la fuente que mejor lo conoce, y ninguna pide clave:

  juego  Steam         guarda appid, y trae year, autor y tags
  peli   Wikidata      guarda letterboxd, y trae year y direccion
  serie  TVmaze        guarda tvmaze, y trae year, quien la creo y tags
  album  MusicBrainz   guarda mbid, y trae year y artista
  libro  Open Library  guarda coverid, y trae year y autor

Lo que la fuente no sabe es lo tuyo, y va en las opciones:

  --nota 8            del 1 al 10
  --estado "en curso" pendiente, en curso, terminado, abandonado
  --favorito          la marca como favorita: entra en Favoritos
  --elegir 2          sin preguntar: el resultado numero 2
  --fichero "Aku no Hana"  como se llama el fichero cuando del titulo no sale
                      uno: los discos japoneses se catalogan en japones, y de
                      "悪の華" no queda nada al pasar a ASCII. El titulo de
                      verdad se guarda igual, en `title`.
  --borrador          entra con draft: true, o sea sin salir en la web
  --dry-run           dice que crearia, sin tocar nada
"""

import argparse
import contextlib
import io
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

import autores
import estado
import textos
from datos import datos_juego, datos_serie
from vitrina import (ESTADOS, PORTADAS, SECCIONES, UA, VAULT, entrada_steam,
                       escribir_campos, escribir_ficha, ficha_letterboxd, frontmatter,
                       nombre_de_fichero, parecidos, pedir, peliculas_wikidata,
                       preguntar, serie_tvmaze, series_tvmaze, sin_letras_latinas, slug,
                       año_tvmaze)
from portadas import FUENTES as CARATULAS, guardar

# Tipo de ficha -> carpeta de la vault. SECCIONES va al reves.
CARPETAS = {tipo: carpeta for carpeta, tipo in SECCIONES.items()}


# --- buscadores --------------------------------------------------------------
# Los cinco devuelven lo mismo: una lista de candidatos, cada uno con lo que va
# a la cabecera de la ficha y una linea con la que reconocerlo. Asi el resto del
# script no tiene que saber de que catalogo viene ninguno.
#
# Devolver None es otra cosa que devolver una lista vacia: quiere decir que no
# se ha podido preguntar. No es lo mismo "de eso no hay nada" que "hoy el
# catalogo esta caido", y decir lo primero cuando pasa lo segundo manda a
# buscar el fallo justo donde no esta.

NOMBRE_FUENTE = {"juego": "Steam", "peli": "Wikidata", "serie": "TVmaze",
                 "album": "MusicBrainz", "libro": "Open Library"}

def candidato(titulo, year=None, autor=None, pista=None, **ids):
    return {"titulo": re.sub(r"\s+", " ", titulo or "").strip(),
            "year": year, "autor": autor, "pista": pista, "ids": ids}


def describir(c):
    # Los titulos de catalogo son a veces un parrafo entero ("El Nombre de la
    # Ballena Coleccion Los Especiales de a la Orilla del Viento"), y uno solo
    # descuadra la lista de resultados.
    titulo = c["titulo"] if len(c["titulo"]) <= 70 else c["titulo"][:69].rstrip() + "…"
    partes = [titulo]
    if c["autor"]:
        partes.append("— " + c["autor"])
    if c["year"]:
        partes.append(f"({c['year']})")
    if c["pista"]:
        partes.append("  " + c["pista"])
    return " ".join(partes)


def buscar_juego(consulta, cuantos):
    """El buscador de la tienda de Steam, el mismo que su caja de busqueda.

    Solo da el nombre y el appid: el año y el estudio estan en la ficha de la
    tienda, que son una peticion por juego. Pedirlas para toda la lista seria
    una espera larga antes de enseñar nada, y con los juegos el nombre suele
    bastar para elegir. En cuanto eliges se piden las del que sea, una sola.
    """
    res = pedir("https://steamcommunity.com/actions/SearchApps/"
                + urllib.parse.quote(consulta))
    if res is None:
        return None
    return [candidato(a["name"], pista=f"appid {a['appid']}", appid=a["appid"])
            for a in res[:cuantos] if a.get("appid")]


def buscar_peli(consulta, cuantos):
    """Wikidata, que es quien sabe cual de las homonimas es cual.

    Enseña el año porque es lo unico que las separa: hay tres peliculas
    llamadas "Parasite" y cuatro "Little Women". Del titulo no se puede
    deducir nada, y por eso se elige de una lista y no a ciegas.
    """
    candidatas = peliculas_wikidata(consulta)
    if candidatas is None:
        return None
    return [candidato(c["nombre"], year=c["year"], letterboxd=c["letterboxd"])
            for c in candidatas[:cuantos]]


def buscar_serie(consulta, cuantos):
    """TVmaze, que es un catalogo de television abierto y con el anime dentro.

    Enseña el año, la cadena y el pais porque son lo que separa a las homonimas,
    que en television son mas de las que parece: hay cinco "The Office" --la
    americana, la inglesa, la australiana, la india y una de 1995-- y dos
    "Hunter x Hunter", el del 99 y el del 2011.
    Del titulo no se deduce cual es, y por eso se elige de una lista.
    """
    encontradas = series_tvmaze(consulta)
    if encontradas is None:
        return None
    return [candidato_serie(serie) for serie in encontradas[:cuantos]]


def candidato_serie(serie):
    return candidato(serie.get("name"), year=año_tvmaze(serie),
                     autor=(emisora(serie) or {}).get("name"),
                     pista=pista_serie(serie), tvmaze=serie.get("id"))


def emisora(serie):
    return serie.get("network") or serie.get("webChannel")


# Solo lo que no es una serie de ficcion con actores se dice: eso es lo normal
# y ponerlo en cada linea seria ruido.
TIPOS_SERIE = {"Animation": "animación", "Documentary": "documental",
               "Reality": "reality"}


def pista_serie(serie):
    """El pais, si es de animacion y los generos: lo que separa a las homonimas.

    Con los generos solos no bastaba. Las dos "One Piece" son Action y
    Adventure, y lo que las separa es que una es el anime del 99 y la otra la
    de Netflix con actores; las cuatro "The Office" son Comedy, y lo que las
    separa es el pais. La que todavia no se ha estrenado lo dice, que no tiene
    año con el que reconocerla.
    """
    pais = ((emisora(serie) or {}).get("country") or {}).get("code")
    tipo = serie.get("type")
    partes = [pais or serie.get("language"),
              TIPOS_SERIE.get(tipo, tipo.lower() if tipo and tipo != "Scripted" else None),
              "sin estrenar" if serie.get("status") == "In Development" else None,
              ", ".join(serie.get("genres") or [])]
    return " · ".join(p for p in partes if p)


def buscar_album(consulta, cuantos):
    """MusicBrainz, por grupo de lanzamiento y no por edicion concreta.

    Un disco tiene una edicion por pais, por formato y por reedicion, y todas
    se llaman igual. El grupo de lanzamiento es el disco como obra, que es lo
    que se apunta en una mediateca.
    """
    url = ("https://musicbrainz.org/ws/2/release-group?fmt=json&limit="
           f"{cuantos}&query=" + urllib.parse.quote(consulta))
    datos = pedir(url)
    if datos is None:
        return None
    return [candidato_album(grupo) for grupo in datos.get("release-groups", [])]


def candidato_album(grupo):
    fecha = grupo.get("first-release-date") or ""
    artistas = [a["artist"]["name"] for a in grupo.get("artist-credit", [])
                if isinstance(a, dict) and a.get("artist")]
    return candidato(grupo.get("title"), year=fecha[:4] or None,
                     autor=", ".join(artistas[:2]) or None,
                     pista=grupo.get("primary-type") or "", mbid=grupo["id"])


CAMPOS_OL = "title,author_name,cover_i,first_publish_year"


def buscar_libro(consulta, cuantos):
    """Open Library, que es el catalogo del Internet Archive.

    Devuelve casi siempre la edicion inglesa aunque busques en español, asi
    que "el nombre del viento" sale como "The Name of the Wind". No es un
    fallo: es la ficha de la obra, y la portada que baja es la de esa edicion.
    """
    url = (f"https://openlibrary.org/search.json?limit={cuantos}&fields={CAMPOS_OL}"
           "&q=" + urllib.parse.quote(consulta))
    datos = pedir(url)
    if datos is None:
        return None
    return [candidato_libro(doc) for doc in datos.get("docs") or []]


def candidato_libro(doc):
    return candidato(doc.get("title"), year=doc.get("first_publish_year"),
                     autor=(doc.get("author_name") or [None])[0],
                     pista="" if doc.get("cover_i") else "(sin portada)",
                     coverid=doc.get("cover_i"))


BUSCADORES = {"juego": buscar_juego, "peli": buscar_peli, "serie": buscar_serie,
              "album": buscar_album, "libro": buscar_libro}
assert set(BUSCADORES) == set(NOMBRE_FUENTE)


# --- por enlace --------------------------------------------------------------
# Casi siempre que añades algo lo tienes delante: la pagina de Steam, la de
# Letterboxd, el disco abierto en Spotify. Buscarlo otra vez por el titulo es
# volver a elegir entre las tres "Parasite" algo que ya estaba elegido, porque
# el enlace lleva dentro el identificador. Asi que se saca de ahi y la lista de
# candidatos se queda en uno.
#
# Devuelven lo mismo que los buscadores: None si la fuente no contesta, lista
# vacia si contesta que eso no existe.

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
MUSICBRAINZ = "https://musicbrainz.org/ws/2"


def juego_por_appid(appid):
    # Aqui solo hace falta el nombre: el año, el estudio y los generos los pide
    # `completar`, como con cualquier juego elegido de la lista.
    res = pedir("https://store.steampowered.com/api/appdetails"
                f"?appids={appid}&l=english")
    if res is None:
        return None
    entrada = entrada_steam(res, appid)
    if not entrada.get("success"):
        return []
    nombre = (entrada.get("data") or {}).get("name")
    return [candidato(nombre, pista=f"appid {appid}", appid=int(appid))]


def peli_por_slug(slug):
    # Una pagina que no se ha podido leer y una que no existe dan lo mismo,
    # {}, asi que aqui no se distinguen: las dos acaban en "no encuentro nada".
    ficha = ficha_letterboxd(slug)
    if not ficha.get("titulo"):
        return []
    return [candidato(ficha["titulo"], year=ficha.get("year"),
                      autor=", ".join(ficha.get("direccion", [])[:2]) or None,
                      letterboxd=slug)]


def serie_por_id(tvid):
    serie = serie_tvmaze(tvid)
    if serie is None:
        return None
    return [candidato_serie(serie)] if serie.get("name") else []


def album_por_grupo(mbid):
    grupo = pedir(f"{MUSICBRAINZ}/release-group/{mbid}?fmt=json&inc=artist-credits",
                  no_existe={})
    if grupo is None:
        return None
    return [candidato_album(grupo)] if grupo.get("id") else []


def album_por_edicion(mbid):
    # Una edicion concreta (un /release/) no es lo que se apunta: la ficha va
    # por el grupo, que es el disco como obra. Se sube a el y se sigue igual.
    edicion = pedir(f"{MUSICBRAINZ}/release/{mbid}?fmt=json&inc=release-groups",
                    no_existe={})
    if edicion is None:
        return None
    grupo = (edicion.get("release-group") or {}).get("id")
    return album_por_grupo(grupo) if grupo else []


def album_por_spotify(spotify_id):
    """El disco de MusicBrainz que tiene enlazado ese album de Spotify.

    Spotify no se puede preguntar sin cuenta de desarrollador, pero no hace
    falta: MusicBrainz guarda de cada edicion sus enlaces de streaming, y se le
    puede preguntar al reves, por el enlace. Lo que no este enlazado alli no se
    encuentra, y entonces se busca por el titulo, como siempre.
    """
    url = urllib.parse.quote(f"https://open.spotify.com/album/{spotify_id}", safe="")
    datos = pedir(f"{MUSICBRAINZ}/url?resource={url}&inc=release-rels&fmt=json",
                  no_existe={})
    if datos is None:
        return None
    ediciones = [r["release"]["id"] for r in datos.get("relations") or []
                 if (r.get("release") or {}).get("id")]
    return album_por_edicion(ediciones[0]) if ediciones else []


def libro_por_obra(obra):
    url = (f"https://openlibrary.org/search.json?fields={CAMPOS_OL}"
           f"&q=key:/works/{obra}")
    datos = pedir(url)
    if datos is None:
        return None
    return [candidato_libro(doc) for doc in (datos.get("docs") or [])[:1]]


def libro_por_edicion(edicion):
    # Las paginas de /books/ son una edicion; la ficha va por la obra, que es
    # la que da el año de la primera publicacion y no el de esa reimpresion.
    datos = pedir(f"https://openlibrary.org/books/{edicion}.json", no_existe={})
    if datos is None:
        return None
    obras = [w.get("key", "").rsplit("/", 1)[-1] for w in datos.get("works") or []]
    return libro_por_obra(obras[0]) if obras and obras[0] else []


# Cada fuente, con el trozo del enlace donde va el identificador. En el de
# Letterboxd cabe un usuario delante (letterboxd.com/alguien/film/heat-1995/),
# que es como sale al abrirla desde el diario de otro; y en el de Spotify, el
# idioma (open.spotify.com/intl-es/album/...).
ENLACES = [
    (r"(?:store\.steampowered|steamcommunity)\.com/app/(\d+)", "juego", juego_por_appid),
    (r"letterboxd\.com/(?:[^/]+/)?film/([^/?#]+)", "peli", peli_por_slug),
    (r"tvmaze\.com/shows/(\d+)", "serie", serie_por_id),
    (rf"musicbrainz\.org/release-group/({UUID})", "album", album_por_grupo),
    (rf"musicbrainz\.org/release/({UUID})", "album", album_por_edicion),
    (r"open\.spotify\.com/(?:intl-[a-z]+/)?album/([A-Za-z0-9]+)", "album", album_por_spotify),
    (r"openlibrary\.org/works/(OL\d+W)", "libro", libro_por_obra),
    (r"openlibrary\.org/books/(OL\d+M)", "libro", libro_por_edicion),
]


def es_enlace(texto):
    return bool(re.match(r"https?://|(?:www\.)?[a-z0-9.-]+\.[a-z]{2,}/", texto or ""))


def leer_enlace(enlace):
    """El tipo, la fuente y el id del enlace, o None si no es de ninguna."""
    for patron, tipo, fuente in ENLACES:
        m = re.search(patron, enlace)
        if m:
            return tipo, fuente, m.group(1)
    return None


def destino(enlace):
    """A donde lleva un enlace corto: boxd.it/2bg8 es letterboxd.com/film/heat-1995/.

    Es lo que copia el boton de compartir de Letterboxd en el movil, asi que es
    el enlace que se tiene a mano mas veces. Lo que no redirige se queda igual.
    """
    if not re.match(r"(?:https?://)?boxd\.it/", enlace):
        return enlace
    if not enlace.startswith("http"):
        enlace = "https://" + enlace
    try:
        req = urllib.request.Request(enlace, headers={"User-Agent": UA}, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.geturl()
    except urllib.error.HTTPError as e:
        # Letterboxd contesta a veces un 403 a las peticiones HEAD, pero ya
        # en la pagina de destino: la redireccion se ha seguido igual.
        return e.geturl()
    except (urllib.error.URLError, TimeoutError):
        return enlace


# --- completar ---------------------------------------------------------------
# Lo que el buscador no da y si da la ficha de la obra, una vez elegida. Una
# peticion mas, y solo la del candidato que hayas dicho tu.

def completar(tipo, elegido):
    campos = {c: v for c, v in elegido["ids"].items() if v}
    if tipo == "juego":
        valores, detalle = datos_juego(elegido["titulo"], campos, None)
        return {**campos, **valores}, detalle
    if tipo == "peli":
        ficha = ficha_letterboxd(campos.get("letterboxd", ""))
        direccion = ficha.get("direccion") or []
        if direccion:
            return {**campos, "autor": ", ".join(direccion[:2])}, "Letterboxd"
        return campos, "su ficha de Letterboxd no dice quien dirige"
    if tipo == "serie":
        # La lista ya trajo el año y la cadena; esto pide los generos y a quien
        # se le atribuye la serie, que estan en su ficha y en su equipo. Lo que
        # venga de aqui pisa a la cadena, que no es quien la hizo.
        valores, detalle = datos_serie(elegido["titulo"], campos, None)
        return {**campos, **valores}, detalle
    return campos, None


# --- el nombre en latino -----------------------------------------------------
# De un titulo japones no sale nombre de fichero: "アダンの風" y "悪の華" se
# quedan en nada al pasar a ASCII, y los dos daban el mismo "sin titulo.md".
# El nombre no se inventa ni se translitera, que eso seria adivinar: se le
# pregunta a la misma fuente que ya identifico la obra, que lo tiene apuntado.

def nombre_latino(tipo, elegido):
    """Como se llama esa obra en alfabeto latino, si la fuente lo sabe.

    Solo se pregunta cuando hace falta, que es casi nunca, asi que es una
    peticion mas y solo la del candidato que hayas dicho tu, igual que
    `completar`. Si la fuente no lo sabe se devuelve None y quien llama decide:
    antes un nombre raro que uno inventado.
    """
    if tipo != "album":
        # De las otras cuatro fuentes no ha hecho falta todavia: Steam, TVmaze,
        # Wikidata y Open Library devuelven ya el titulo en latino.
        return None
    datos = pedir(f"https://musicbrainz.org/ws/2/release-group/{elegido['ids']['mbid']}"
                  "?fmt=json&inc=aliases", no_existe={})
    alias = [a.get("name") for a in (datos or {}).get("aliases") or []
             if a.get("locale") == "en" and a.get("name")]
    return next((a for a in alias if not sin_letras_latinas(a)), None)


# --- alta --------------------------------------------------------------------

def ficha_con_id(carpeta, ids):
    """La ficha de la carpeta que ya lleva alguno de esos ids, si la hay."""
    buscados = {(c, str(v)) for c, v in ids.items() if v}
    for md in sorted((VAULT / carpeta).glob("*.md")):
        campos = frontmatter(md.read_text(encoding="utf-8"))
        if any(campos.get(c) == v for c, v in buscados):
            return md.stem
    return None


def caratula(tipo, md, campos, titulo):
    """La portada de la ficha recien creada, con el id que se acaba de guardar.

    La imagen se llama como el fichero de la ficha y no como su titulo, que no
    siempre da un nombre: de "悪の華" sale un `slug` vacio, o sea una portada
    llamada ".webp" que se pisarian entre ellas todas las que cayeran ahi. El
    nombre del fichero, en cambio, siempre vale: de eso se encarga quien lo
    eligio.
    """
    img, fuente = CARATULAS[tipo](titulo, campos, md)
    if not img:
        return None
    nombre = f"{slug(md.stem)}.webp"
    peso = guardar(img, PORTADAS / nombre)
    escribir_campos(md, {"portada": f"[[{nombre}]]"})
    return f"{nombre}, {peso // 1024} KB, {fuente}"


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tipo", metavar="tipo|enlace",
                   help=f"{', '.join(BUSCADORES)}, o el enlace de la obra")
    p.add_argument("titulo", nargs="?", help="lo que escribirias en un buscador")
    p.add_argument("--nota", type=int, choices=range(1, 11), metavar="1-10")
    p.add_argument("--estado", choices=ESTADOS, default="pendiente")
    p.add_argument("--favorito", action="store_true")
    p.add_argument("--elegir", type=int, metavar="N",
                   help="sin preguntar: el resultado numero N")
    p.add_argument("--resultados", type=int, default=8, metavar="N")
    p.add_argument("--fichero", metavar="NOMBRE",
                   help="como se llama el fichero, si del titulo no sale uno")
    p.add_argument("--borrador", action="store_true",
                   help="entra con draft: true, o sea sin salir en la web")
    p.add_argument("--dry-run", action="store_true", help="no escribe ni baja nada")
    args = p.parse_args()
    # El enlace puede ir solo o detras del tipo: "nueva.py <enlace>" y
    # "nueva.py peli <enlace>" hacen lo mismo, y el tipo lo dice el enlace.
    escrito = next((a for a in (args.tipo, args.titulo) if es_enlace(a)), None)
    args.enlace = escrito and destino(escrito)
    if args.enlace:
        leido = leer_enlace(args.enlace)
        if not leido:
            p.error("ese enlace no es de ninguna fuente que sepa leer: Steam, "
                    "Letterboxd, TVmaze, MusicBrainz, Spotify u Open Library")
        if args.tipo != escrito and args.tipo != leido[0]:
            p.error(f"ese enlace es de {CARPETAS[leido[0]]}, no de "
                    f"{CARPETAS.get(args.tipo, args.tipo)}")
        args.tipo = leido[0]
        args.titulo = args.enlace
    elif args.tipo not in BUSCADORES:
        p.error(f"el tipo es uno de estos: {', '.join(BUSCADORES)}; o un enlace")
    elif not args.titulo:
        p.error("falta qué buscar")
    return alta(args)


def alta(args):
    """El alta en si, ya con las opciones decididas.

    Aparte del parseo porque `importar.py libro` entra por aqui: es la misma
    alta de una obra suelta, con otro nombre y con el borrador por defecto.
    """
    carpeta = CARPETAS[args.tipo]
    enlace = getattr(args, "enlace", None)
    if enlace:
        _, fuente, ident = leer_enlace(enlace)
        candidatos = fuente(ident)
    else:
        candidatos = BUSCADORES[args.tipo](args.titulo, args.resultados)
    if candidatos is None:
        print(f"No he podido hablar con {NOMBRE_FUENTE[args.tipo]}. No es que no esté:\n"
              "es que ahora mismo no contesta. Inténtalo dentro de un rato.")
        return 1
    if not candidatos and enlace:
        print(f"{NOMBRE_FUENTE[args.tipo]} no tiene nada en ese enlace. Prueba a "
              "buscarla por el título:\n"
              f"  scripts/nueva.py {args.tipo} \"el título\"")
        return 1
    if not candidatos:
        print(f"No encuentro nada con «{args.titulo}».")
        if args.tipo == "libro":
            print("Prueba con el título en inglés: el catálogo va casi todo por ahí.")
        if args.tipo == "peli":
            print("Prueba con el título original: es el que suele estar en Wikidata.")
        return 1

    if enlace:
        # El enlace ya es la eleccion: no hay lista entre la que dudar.
        elegido = candidatos[0]
        print(f"  {describir(elegido)}")
    elif args.elegir:
        if not 1 <= args.elegir <= len(candidatos):
            print(f"Solo hay {len(candidatos)} resultados.")
            return 1
        elegido = candidatos[args.elegir - 1]
        print(f"  {args.elegir}) {describir(elegido)}")
    elif not sys.stdin.isatty():
        for i, c in enumerate(candidatos, 1):
            print(f"  {i}) {describir(c)}")
        print("\nSin terminal para preguntar. Repite con --elegir N.")
        return 1
    else:
        elegido = preguntar(candidatos, describir)
        if elegido is None:
            print("No se ha creado nada.")
            return 0

    # La misma obra con otro nombre de fichero no la para escribir_ficha, que
    # compara titulos: "Shingeki no Kyojin" a mano y "Attack on Titan" desde
    # TVmaze son dos ficheros y una serie. El id si es el mismo.
    repetida = ficha_con_id(carpeta, elegido["ids"])
    if repetida:
        print(f"\nEsa ya la tienes: content/{carpeta}/{repetida}.md lleva el mismo id.")
        return 0

    extra, detalle = completar(args.tipo, elegido)
    titulo = elegido["titulo"]
    # De donde sale el nombre del fichero. Casi siempre del titulo; cuando el
    # titulo no tiene ni una letra latina, de como lo llame la fuente en ingles.
    fichero = args.fichero or titulo
    if sin_letras_latinas(fichero):
        fichero = nombre_latino(args.tipo, elegido)
        if not fichero:
            # Ni el titulo ni la fuente dan un nombre de fichero. Antes salia
            # "sin titulo.md" con la portada ".webp", que es una ficha que no
            # se llama de nada y una imagen que se pisan entre ellas todas las
            # que caigan ahi. Como llamarla en latino no se adivina: se pide.
            print(f"\n«{titulo}» no tiene ni una letra latina, y "
                  f"{NOMBRE_FUENTE[args.tipo]} no sabe cómo se llama fuera\n"
                  "de su alfabeto, así que de ahí no sale un nombre de fichero.\n"
                  "Dilo tú, repitiendo la orden con --fichero y el nombre que le des:\n"
                  + (f"  scripts/nueva.py {enlace} --fichero \"Aku no Hana\"\n"
                     if enlace else
                     f"  scripts/nueva.py {args.tipo} \"{args.titulo}\" "
                     f"--elegir {args.elegir or 1} --fichero \"Aku no Hana\"\n")
                  + "El título de verdad se guarda igual, en `title`.")
            return 1
        print(f"  El título no da un nombre de fichero; {NOMBRE_FUENTE[args.tipo]}"
              f" lo llama «{fichero}».")
    # En las series la columna de la izquierda es la cadena, que sirve para
    # reconocer cual de las tres "The Office" es y no para firmar la obra: a la
    # ficha solo va si `completar` trae a alguien.
    autor = None if args.tipo == "serie" else elegido["autor"]
    campos = {"tipo": args.tipo, "year": elegido["year"], "autor": autor,
              "nota": args.nota, "estado": args.estado, "favorito": args.favorito,
              "portada": None, "tags": None}
    # Lo que traiga la ficha de la obra manda sobre lo que trajo el buscador:
    # la del juego sabe el estudio y el año, y la lista solo sabia el nombre.
    campos.update({c: v for c, v in extra.items() if v})

    if args.dry_run:
        print(f"\nSe crearía content/{carpeta}/{nombre_de_fichero(fichero)}.md")
        for clave, valor in campos.items():
            if valor not in (None, "", False):
                print(f"  {clave}: {valor}")
        if detalle:
            print(f"  ({detalle})")
        return 0

    md = escribir_ficha(carpeta, titulo, campos, borrador=args.borrador,
                        fichero=fichero)
    if not md:
        print(f"\n«{titulo}» ya estaba en content/{carpeta}/.")
        return 0
    print(f"\nCreada {md.relative_to(VAULT.parent)}")

    hecha = caratula(args.tipo, md, campos, titulo)
    print("  portada: " + (hecha or "no la he encontrado; se pone a mano"))
    # El texto, de la misma fuente que pasaria textos.py despues. Con los
    # campos del disco y no los de aqui: la portada y el id ya estan escritos.
    cuerpo, detalle = textos.FUENTES[args.tipo](
        titulo, frontmatter(md.read_text(encoding="utf-8")), md)
    if cuerpo:
        textos.escribir_cuerpo(md, cuerpo)
    print("  texto: " + (detalle if cuerpo else f"sin texto ({detalle})"))
    for aviso in parecidos(carpeta, [titulo]):
        print("  Se parece a una que ya tenías: " + aviso)
    if args.borrador:
        print("Entra con draft: true, así que no sale en la web hasta que le quites\n"
              "la línea. En Obsidian se ve ya.")
    if args.nota is None:
        print("Sin nota: ponla con scripts/repasar.py o en Obsidian cuando la\n"
              "tengas, que es por lo que ordenan las galerías.")
    al_dia()
    return 0


def al_dia():
    """Lo que cuelga de la vault y no pide red: autores y cifras del README.

    Una ficha nueva puede ser la segunda de un autor, que entonces estrena
    pagina, y siempre cambia las cifras del README. Las dos cosas se quedaban
    esperando a que alguien pasara autores.py y estado.py, y las pruebas y el
    CI lo notaban antes que nadie. Son dos pasadas sin red que tardan nada.
    """
    with contextlib.redirect_stdout(io.StringIO()):
        autores.main([])
    estado.actualizar_readme(callado=True)


if __name__ == "__main__":
    sys.exit(main())
