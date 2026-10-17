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
MusicBrainz por su enlace. Y los de IMDb, TMDB, FilmAffinity, MyAnimeList,
AniList, Goodreads, Apple Music, Deezer, Discogs, IGDB, HowLongToBeat,
Wikipedia y Wikidata, que pasan por Wikidata para llegar a una de las otras.

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
  --estado "en curso" pendiente, en curso, terminado, abandonado (o en ingles)
  --favorito          la marca como favorita: entra en Favoritos
  --elegir 2          sin preguntar: el resultado numero 2
  --fichero "Aku no Hana"  como se llama el fichero cuando del titulo no sale
                      uno: los discos japoneses se catalogan en japones, y de
                      "悪の華" no queda nada al pasar a ASCII. El titulo de
                      verdad se guarda igual, en `title`.
  --borrador          entra con draft: true, o sea sin salir en la web
  --oculta            entra con hidden: true: no sale en la web, pero el
                      fichero esta en el repo y se puede leer en GitHub
  --privada           va a la carpeta privada (content/privado/), que git no
                      sube: ni la web ni GitHub la ven
  --grupo "Anime"     la mete en ese grupo (se puede repetir)
  --terminada 2024-05 cuando la terminaste, para el anuario
  --veces 3           cuantas veces la has terminado: sale "Vista 3 veces"
  --dry-run           dice que crearia, sin tocar nada
"""

import argparse
import contextlib
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import autores
import enlazar
import textos
from idioma import _, ayuda, opciones
from datos import datos_juego, datos_serie
from vitrina import (fichas, portadas_de, ESTADOS, PORTADAS, SECCIONES, UA, VAULT, entrada_steam,
                     estado_de, tipo_de, escribir_campos, escribir_ficha, ficha_letterboxd,
                     frontmatter, nombre_de_fichero, parecidos, pedir, peliculas_wikidata,
                     preguntar, serie_tvmaze, series_tvmaze, sin_letras_latinas, slug, wikidata,
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

NOMBRE_FUENTE = {"game": "Steam", "film": "Wikidata", "series": "TVmaze",
                 "album": "MusicBrainz", "book": "Open Library"}

def candidato(titulo, year=None, autor=None, pista=None, **ids):
    return {"titulo": re.sub(r"\s+", " ", titulo or "").strip(),
            "year": year, "author": autor, "pista": pista, "ids": ids}


def describir(c):
    # Los titulos de catalogo son a veces un parrafo entero ("El Nombre de la
    # Ballena Coleccion Los Especiales de a la Orilla del Viento"), y uno solo
    # descuadra la lista de resultados.
    titulo = c["titulo"] if len(c["titulo"]) <= 70 else c["titulo"][:69].rstrip() + "…"
    partes = [titulo]
    if c["author"]:
        partes.append("— " + c["author"])
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
TIPOS_SERIE = {"Animation": _("animación"), "Documentary": _("documental"),
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
              _("sin estrenar") if serie.get("status") == "In Development" else None,
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
                     pista="" if doc.get("cover_i") else _("(sin portada)"),
                     coverid=doc.get("cover_i"))


BUSCADORES = {"game": buscar_juego, "film": buscar_peli, "series": buscar_serie,
              "album": buscar_album, "book": buscar_libro}
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
    (r"(?:store\.steampowered|steamcommunity)\.com/app/(\d+)", "game", juego_por_appid),
    (r"letterboxd\.com/(?:[^/]+/)?film/([^/?#]+)", "film", peli_por_slug),
    (r"tvmaze\.com/shows/(\d+)", "series", serie_por_id),
    (rf"musicbrainz\.org/release-group/({UUID})", "album", album_por_grupo),
    (rf"musicbrainz\.org/release/({UUID})", "album", album_por_edicion),
    (r"open\.spotify\.com/(?:intl-[a-z]+/)?album/([A-Za-z0-9]+)", "album", album_por_spotify),
    (r"openlibrary\.org/works/(OL\d+W)", "book", libro_por_obra),
    (r"openlibrary\.org/books/(OL\d+M)", "book", libro_por_edicion),
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


# --- por enlace, pasando por Wikidata ----------------------------------------
# IMDb, Filmaffinity, MyAnimeList, Goodreads... no son fuentes de Vitrina: una
# ficha no guarda su id ni se le puede pedir nada sin clave. Pero Wikidata si
# guarda sus ids, y en la misma entidad los de las cinco fuentes que si usamos.
# Asi que el enlace de IMDb de Breaking Bad lleva a la entidad de Breaking Bad,
# y de ahi a su id de TVmaze, que es el enlace que ya sabiamos leer.
#
# Lo que Wikidata no tenga enlazado no se encuentra, y se dice: no se busca
# por el titulo, que es justo lo que el enlace venia a evitar.

# El id de cada fuente de Vitrina en Wikidata, y como se sigue desde el. El
# orden es el de preferencia cuando una entidad trae dos: el anime de Death
# Note lleva el de TVmaze y tambien el de Letterboxd de la pelicula. Serie antes
# que peli porque TVmaze no cataloga peliculas, asi que su id es la señal mas
# fuerte; libro antes que disco por lo mismo con Open Library, que El Hobbit
# trae tambien el disco del audiolibro. `nueva.py peli <enlace>` elige a mano.
NATIVAS = {
    "P1733": ("game", juego_por_appid),
    "P8600": ("series", serie_por_id),
    "P6127": ("film", peli_por_slug),
    "P648": ("book", lambda ol: (libro_por_obra if ol.endswith("W")
                                  else libro_por_edicion)(ol)),
    "P436": ("album", album_por_grupo),
}

# Enlace -> la propiedad de Wikidata que guarda ese id, el sitio, y el tipo que
# suele ser, para decir por donde buscar si Wikidata no llega.
PUENTES = [
    (r"imdb\.com/title/(tt\d+)", "P345", "IMDb", "film"),
    (r"themoviedb\.org/movie/(\d+)", "P4947", "TMDB", "film"),
    (r"themoviedb\.org/tv/(\d+)", "P4983", "TMDB", "series"),
    (r"filmaffinity\.com/[a-z]{2}/film(\d+)\.html", "P480", "FilmAffinity", "film"),
    (r"myanimelist\.net/anime/(\d+)", "P4086", "MyAnimeList", "series"),
    (r"myanimelist\.net/manga/(\d+)", "P4087", "MyAnimeList", "book"),
    (r"anilist\.co/anime/(\d+)", "P8729", "AniList", "series"),
    (r"anilist\.co/manga/(\d+)", "P8731", "AniList", "book"),
    (r"goodreads\.com/(?:[a-z]+/)?book/show/(\d+)", "P2969", "Goodreads", "book"),
    (r"goodreads\.com/work/\w+/(\d+)", "P8383", "Goodreads", "book"),
    (r"music\.apple\.com/[a-z]{2}/album/(?:[^/?#]+/)?(\d+)", "P2281", "Apple Music", "album"),
    (r"deezer\.com/(?:[a-z]{2}/)?album/(\d+)", "P2722", "Deezer", "album"),
    (r"discogs\.com/(?:[a-z]{2}/)?master/(\d+)", "P1954", "Discogs", "album"),
    (r"igdb\.com/games/([a-z0-9-]+)", "P5794", "IGDB", "game"),
    (r"howlongtobeat\.com/game/(\d+)", "P2816", "HowLongToBeat", "game"),
]
WIKIPEDIA_RE = re.compile(r"([a-z-]+)\.(?:m\.)?wikipedia\.org/wiki/([^?#]+)")
WIKIDATA_RE = re.compile(r"wikidata\.org/wiki/(Q\d+)")


def puente_de(enlace):
    """Por donde se entra en Wikidata con ese enlace, o None si no se puede.

    Devuelve los parametros de la consulta, el nombre del sitio y el tipo que
    suele ser (None si puede ser cualquiera), sin preguntar nada todavia: asi
    se prueba sin red.
    """
    for patron, propiedad, sitio, tipo in PUENTES:
        m = re.search(patron, enlace)
        if m:
            return {"propiedad": propiedad, "valor": m.group(1)}, sitio, tipo
    m = WIKIPEDIA_RE.search(enlace)
    if m:
        titulo = urllib.parse.unquote(m.group(2)).replace("_", " ")
        return {"sitio": m.group(1).replace("-", "_") + "wiki", "titulo": titulo}, "Wikipedia", None
    m = WIKIDATA_RE.search(enlace)
    if m:
        return {"entidad": m.group(1)}, "Wikidata", None
    return None


def ids_nativos(entidad):
    """Los ids de las fuentes de Vitrina que trae la entidad, en orden."""
    claims = (entidad or {}).get("claims") or {}
    salida = {}
    for propiedad in NATIVAS:
        for claim in claims.get(propiedad) or []:
            valor = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(valor, str) and valor:
                salida[propiedad] = valor
                break
    return salida


def elegir_nativo(ids, preferido=None):
    """(tipo, fuente, id) del id que manda: el del tipo pedido, o el primero."""
    for propiedad, valor in ids.items():
        tipo, fuente = NATIVAS[propiedad]
        if preferido in (None, tipo):
            return tipo, fuente, valor
    return None


def entidades(ids):
    datos = wikidata({"action": "wbgetentities", "ids": "|".join(ids), "props": "claims"})
    return None if datos is None else list((datos.get("entities") or {}).values())


def por_wikidata(consulta, preferido=None):
    """(tipo, fuente, id) de la obra a la que lleva el enlace, o un porque.

    Devuelve un texto en vez de la tupla cuando no se llega: que Wikidata no
    conteste, que no tenga ese id o que la obra no este en ninguna fuente.
    """
    if "entidad" in consulta:
        encontradas = entidades([consulta["entidad"]])
    elif "sitio" in consulta:
        datos = wikidata({"action": "wbgetentities", "sites": consulta["sitio"],
                          "titles": consulta["titulo"], "props": "claims",
                          "normalize": 1})
        encontradas = None if datos is None else [
            e for e in (datos.get("entities") or {}).values() if "missing" not in e]
    else:
        datos = wikidata({"action": "query", "list": "search", "srlimit": 3,
                          "srsearch": f"haswbstatement:{consulta['propiedad']}="
                                      f"{consulta['valor']}"})
        ids = [r["title"] for r in ((datos or {}).get("query") or {}).get("search") or []]
        encontradas = None if datos is None else (entidades(ids) if ids else [])
    if encontradas is None:
        return _("Wikidata no contesta ahora mismo; inténtalo dentro de un rato")
    if not encontradas:
        return _("Wikidata no tiene esa obra enlazada")
    for entidad in encontradas:
        ids = ids_nativos(entidad)
        # Una edicion de Goodreads es una entidad aparte, sin los ids de la
        # obra: estan en la obra, a la que apunta con "edicion de" (P629).
        if not ids:
            obra = entidad.get("claims", {}).get("P629") or []
            valor = obra[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}) if obra else {}
            if valor.get("id"):
                ids = ids_nativos((entidades([valor["id"]]) or [{}])[0])
        leido = elegir_nativo(ids, preferido)
        if leido:
            return leido
    if preferido:
        return _("Wikidata no enlaza esa obra con la fuente de {carpeta}").format(
            carpeta=CARPETAS[preferido])
    return _("Wikidata la conoce, pero sin id de Steam, Letterboxd, TVmaze, "
             "Open Library ni MusicBrainz")


def resolver_enlace(enlace, preferido=None):
    """(tipo, fuente, id), o (None, porque, tipo probable), o None si no se reconoce."""
    leido = leer_enlace(enlace)
    if leido:
        return leido
    puente = puente_de(enlace)
    if not puente:
        return None
    consulta, sitio, probable = puente
    resultado = por_wikidata(consulta, preferido)
    if isinstance(resultado, str):
        return None, _("{porque} (enlace de {sitio})").format(porque=resultado, sitio=sitio), \
            preferido or probable
    return resultado


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
    if tipo == "game":
        valores, detalle = datos_juego(elegido["titulo"], campos, None)
        return {**campos, **valores}, detalle
    if tipo == "film":
        ficha = ficha_letterboxd(campos.get("letterboxd", ""))
        direccion = ficha.get("direccion") or []
        if direccion:
            return {**campos, "author": ", ".join(direccion[:2])}, "Letterboxd"
        return campos, _("su ficha de Letterboxd no dice quien dirige")
    if tipo == "series":
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
    for md in fichas(carpeta):
        campos = frontmatter(md.read_text(encoding="utf-8"))
        if any(campos.get(c) == v for c, v in buscados):
            return md.relative_to(VAULT.parent)
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
    peso = guardar(img, portadas_de(md) / nombre)
    escribir_campos(md, {"cover": f"[[{nombre}]]"})
    return f"{nombre}, {peso // 1024} KB, {fuente}"


def fecha_parcial(texto):
    """AAAA, AAAA-MM o AAAA-MM-DD: con la precision que se sepa, ni una mas."""
    if not re.fullmatch(r"\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?", texto):
        raise argparse.ArgumentTypeError(_("tiene que ser AAAA, AAAA-MM o AAAA-MM-DD"))
    return texto


def main():
    p = argparse.ArgumentParser(description=ayuda(__doc__, "nueva"),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tipo", metavar=_("tipo|enlace"),
                   help=_("{tipos}, o el enlace de la obra").format(tipos=", ".join(BUSCADORES)))
    p.add_argument("titulo", nargs="?", metavar=_("titulo"), help=_("lo que escribirias en un buscador"))
    p.add_argument(*opciones("--nota", "--rating"), dest="nota", type=int, choices=range(1, 11),
                   metavar="1-10")
    p.add_argument(*opciones("--estado", "--status"), dest="estado", type=estado_de, choices=ESTADOS)
    p.add_argument(*opciones("--favorito", "--favorite"), dest="favorito", action="store_true")
    p.add_argument(*opciones("--elegir", "--pick"), dest="elegir", type=int, metavar="N",
                   help=_("sin preguntar: el resultado numero N"))
    p.add_argument(*opciones("--resultados", "--results"), dest="resultados", type=int, default=8, metavar="N")
    p.add_argument(*opciones("--fichero", "--file"), dest="fichero", metavar=_("NOMBRE"),
                   help=_("como se llama el fichero, si del titulo no sale uno"))
    p.add_argument(*opciones("--borrador", "--draft"), dest="borrador", action="store_true",
                   help=_("entra con draft: true, o sea sin salir en la web"))
    p.add_argument(*opciones("--oculta", "--hidden"), dest="oculta", action="store_true",
                   help=_("entra con hidden: true: no sale en la web, pero esta en el repo"))
    p.add_argument(*opciones("--privada", "--private"), dest="privada", action="store_true",
                   help=_("va a la carpeta privada, que no se sube a ningun sitio"))
    p.add_argument(*opciones("--grupo", "--group"), dest="grupos", action="append", metavar=_("NOMBRE"),
                   help=_("la mete en ese grupo; se puede repetir"))
    p.add_argument(*opciones("--terminada", "--finished-on"), dest="terminada", type=fecha_parcial,
                   metavar=_("AAAA[-MM[-DD]]"), help=_("cuando la terminaste, para el anuario"))
    p.add_argument(*opciones("--veces", "--times"), dest="veces", type=int, metavar="N",
                   help=_("cuantas veces la has terminado: vista, jugada, leida o escuchada"))
    p.add_argument("--informe", help=argparse.SUPPRESS)
    p.add_argument("--dry-run", action="store_true", help=_("no escribe ni baja nada"))
    args = p.parse_args()
    if not es_enlace(args.tipo):
        args.tipo = tipo_de(args.tipo)
    # El enlace puede ir solo o detras del tipo: "nueva.py <enlace>" y
    # "nueva.py peli <enlace>" hacen lo mismo, y el tipo lo dice el enlace.
    escrito = next((a for a in (args.tipo, args.titulo) if es_enlace(a)), None)
    args.enlace = escrito and destino(escrito)
    if args.enlace:
        preferido = args.tipo if args.tipo in BUSCADORES else None
        leido = resolver_enlace(args.enlace, preferido)
        if not leido:
            p.error(_("ese enlace no es de ningún sitio que sepa leer. Los que sí: {sitios}").format(
                sitios="Steam, Letterboxd, TVmaze, MusicBrainz, Spotify, Open Library, IMDb, "
                       "TMDB, FilmAffinity, MyAnimeList, AniList, Goodreads, Apple Music, "
                       "Deezer, Discogs, IGDB, HowLongToBeat, Wikipedia, Wikidata"))
        if leido[0] is None:
            _sin, porque, probable = leido
            print(porque[0].upper() + porque[1:] + ".\n"
                  + _("Búscala por el título: scripts/nueva.py {tipo} \"el título\"").format(
                      tipo=probable or "TIPO"))
            return 1
        if args.tipo != escrito and args.tipo != leido[0]:
            p.error(_("ese enlace es de {suyo}, no de {pedido}").format(
                suyo=CARPETAS[leido[0]], pedido=CARPETAS.get(args.tipo, args.tipo)))
        args.tipo = leido[0]
        args.titulo = args.enlace
        # Resuelto una vez: por Wikidata son dos o tres peticiones.
        args.leido = leido
    elif args.tipo not in BUSCADORES:
        p.error(_("el tipo es uno de estos: {tipos}; o un enlace").format(tipos=", ".join(BUSCADORES)))
    elif not args.titulo:
        p.error(_("falta qué buscar"))
    return alta(args)


def alta(args):
    """El alta en si, ya con las opciones decididas.

    Aparte del parseo porque `importar.py libro` entra por aqui: es la misma
    alta de una obra suelta, con otro nombre y con el borrador por defecto.
    """
    carpeta = CARPETAS[args.tipo]
    enlace = getattr(args, "enlace", None)
    if enlace:
        _sin, fuente, ident = getattr(args, "leido", None) or leer_enlace(enlace)
        candidatos = fuente(ident)
    else:
        candidatos = BUSCADORES[args.tipo](args.titulo, args.resultados)
    if candidatos is None:
        print(_("No he podido hablar con {fuente}. No es que no esté:\n"
                "es que ahora mismo no contesta. Inténtalo dentro de un rato.").format(
                    fuente=NOMBRE_FUENTE[args.tipo]))
        return 1
    if not candidatos and enlace:
        print(_("{fuente} no tiene nada en ese enlace. Prueba a buscarla por el título:\n"
                "  scripts/nueva.py {tipo} \"el título\"").format(
                    fuente=NOMBRE_FUENTE[args.tipo], tipo=args.tipo))
        return 1
    if not candidatos:
        print(_("No encuentro nada con «{titulo}».").format(titulo=args.titulo))
        if args.tipo == "book":
            print(_("Prueba con el título en inglés: el catálogo va casi todo por ahí."))
        if args.tipo == "film":
            print(_("Prueba con el título original: es el que suele estar en Wikidata."))
        return 1

    if enlace:
        # El enlace ya es la eleccion: no hay lista entre la que dudar.
        elegido = candidatos[0]
        print(f"  {describir(elegido)}")
    elif args.elegir:
        if not 1 <= args.elegir <= len(candidatos):
            print(_("Solo hay {n} resultados.").format(n=len(candidatos)))
            return 1
        elegido = candidatos[args.elegir - 1]
        print(f"  {args.elegir}) {describir(elegido)}")
    elif not sys.stdin.isatty():
        for i, c in enumerate(candidatos, 1):
            print(f"  {i}) {describir(c)}")
        print("\n" + _("Sin terminal para preguntar. Repite con --elegir N."))
        return 1
    else:
        elegido = preguntar(candidatos, describir)
        if elegido is None:
            print(_("No se ha creado nada."))
            return 0

    # La misma obra con otro nombre de fichero no la para escribir_ficha, que
    # compara titulos: "Shingeki no Kyojin" a mano y "Attack on Titan" desde
    # TVmaze son dos ficheros y una serie. El id si es el mismo.
    repetida = ficha_con_id(carpeta, elegido["ids"])
    if repetida:
        print("\n" + _("Esa ya la tienes: {ruta} lleva el mismo id.").format(ruta=repetida))
        informar(args, ya_estaba=str(repetida))
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
            print("\n" + _("«{titulo}» no tiene ni una letra latina, y {fuente} no sabe cómo se llama fuera\n"
                          "de su alfabeto, así que de ahí no sale un nombre de fichero.\n"
                          "Dilo tú, repitiendo la orden con --fichero y el nombre que le des:").format(
                              titulo=titulo, fuente=NOMBRE_FUENTE[args.tipo]) + "\n"
                  + (f"  scripts/nueva.py {enlace} --fichero \"Aku no Hana\"\n"
                     if enlace else
                     f"  scripts/nueva.py {args.tipo} \"{args.titulo}\" "
                     f"--elegir {args.elegir or 1} --fichero \"Aku no Hana\"\n")
                  + _("El título de verdad se guarda igual, en `title`."))
            return 1
        print("  " + _("El título no da un nombre de fichero; {fuente} lo llama «{nombre}».").format(
            fuente=NOMBRE_FUENTE[args.tipo], nombre=fichero))
    # En las series la columna de la izquierda es la cadena, que sirve para
    # reconocer cual de las tres "The Office" es y no para firmar la obra: a la
    # ficha solo va si `completar` trae a alguien.
    autor = None if args.tipo == "series" else elegido["author"]
    # Sin estado, lo que ya tiene nota o fecha de terminado esta terminado (la
    # misma regla que repasar.py); lo demas, pendiente.
    estado = args.estado or ("finished" if args.nota or getattr(args, "terminada", None)
                             or getattr(args, "veces", None) else "pending")
    campos = {"type": args.tipo, "year": elegido["year"], "author": autor,
              "rating": args.nota, "status": estado, "favorite": args.favorito,
              "cover": None, "tags": None}
    # Lo que traiga la ficha de la obra manda sobre lo que trajo el buscador:
    # la del juego sabe el estudio y el año, y la lista solo sabia el nombre.
    campos.update({c: v for c, v in extra.items() if v})

    if getattr(args, "oculta", False):
        campos["hidden"] = True
    if getattr(args, "grupos", None):
        campos["groups"] = args.grupos
    if getattr(args, "terminada", None):
        campos["finished_on"] = args.terminada
    if getattr(args, "veces", None):
        campos["times"] = args.veces

    if args.dry_run:
        print("\n" + _("Se crearía {ruta}").format(ruta=f"content/{carpeta}/{nombre_de_fichero(fichero)}.md"))
        for clave, valor in campos.items():
            if valor not in (None, "", False):
                print(f"  {clave}: {valor}")
        if detalle:
            print(f"  ({detalle})")
        return 0

    md = escribir_ficha(carpeta, titulo, campos, borrador=args.borrador,
                        fichero=fichero, privada=getattr(args, "privada", False))
    if not md:
        print("\n" + _("«{titulo}» ya estaba en {carpeta}.").format(titulo=titulo, carpeta=f"content/{carpeta}/"))
        informar(args, ya_estaba=f"content/{carpeta}/{nombre_de_fichero(fichero)}.md")
        return 0
    print("\n" + _("Creada {ruta}").format(ruta=md.relative_to(VAULT.parent)))
    detalles = []

    hecha = caratula(args.tipo, md, campos, titulo)
    detalles.append(_("portada: {detalle}").format(detalle=hecha or _("no la he encontrado; se pone a mano")))
    print("  " + detalles[-1])
    # El texto, de la misma fuente que pasaria textos.py despues. Con los
    # campos del disco y no los de aqui: la portada y el id ya estan escritos.
    cuerpo, detalle = textos.FUENTES[args.tipo](
        titulo, frontmatter(md.read_text(encoding="utf-8")), md)
    if cuerpo:
        textos.escribir_cuerpo(md, cuerpo)
    detalles.append(_("texto: {detalle}").format(
        detalle=detalle if cuerpo else _("sin texto ({porque})").format(porque=detalle)))
    print("  " + detalles[-1])
    # Lo que la une con otras fichas, de Wikidata. Si no contesta, la ficha ya esta hecha: enlazar.py lo repite.
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            enlazar.main([str(md)])
        except Exception:
            pass
    informar(args, creada=str(md.relative_to(VAULT.parent)), detalles=detalles)
    for aviso in parecidos(carpeta, [titulo]):
        print("  " + _("Se parece a una que ya tenías: {aviso}").format(aviso=aviso))
    if args.borrador:
        print(_("Entra con draft: true, así que no sale en la web hasta que le quites\n"
                "la línea. En Obsidian se ve ya."))
    if args.nota is None:
        print(_("Sin nota: ponla con scripts/repasar.py o en Obsidian cuando la\n"
                "tengas, que es por lo que ordenan las galerías."))
    al_dia()
    return 0


def informar(args, **datos):
    """Lo que ha hecho el alta, en JSON, para quien la lance desde otro script.

    desde_issue.py lo lee en vez de los mensajes, que salen en el idioma de la
    vitrina y podrian cambiar de redaccion cualquier dia.
    """
    if getattr(args, "informe", None):
        Path(args.informe).write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")


def al_dia():
    """Lo que cuelga de la vault y no pide red: las paginas de autor.

    Una ficha nueva puede ser la segunda de un autor, que entonces estrena
    pagina. Se quedaba esperando a que alguien pasara autores.py, y las pruebas
    y el CI lo notaban antes que nadie. Es una pasada sin red que tarda nada.
    """
    with contextlib.redirect_stdout(io.StringIO()):
        autores.main([])


if __name__ == "__main__":
    sys.exit(main())
