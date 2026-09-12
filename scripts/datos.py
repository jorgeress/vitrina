#!/usr/bin/env python3
"""Rellena los campos que el importador no podia saber.

Ninguna fuente lo da todo, y lo que le falta a cada una no es casualidad. Tu
pagina de juegos de Steam sabe cuanto has jugado pero no de que año es el juego,
quien lo hizo ni de que va; el diario de Letterboxd sabe tu nota pero no quien
dirige. Todo eso esta en otro sitio, publico y sin clave, y esto va a buscarlo.

La regla es la misma en las tres secciones: **no adivinar**. Los juegos se
resuelven por el `appid` que el importador ya guardo, que identifica la obra sin
lugar a dudas; las peliculas por el mismo id de Letterboxd del que sale el
cartel, que Wikidata solo da cuando no hay duda de cual es; los discos por su
`mbid`; y los libros por el `coverid`, que el buscador de Open Library admite
como campo y resuelve a la obra de esa portada. Antes que rellenar una ficha con
los datos de otra obra, se deja vacia.

Como todo lo demas de Vitrina, no pide clave ni registro.

  juegos  Steam, ficha de la tienda: year, autor y tags
  pelis   Letterboxd: autor (la direccion) y tags
  musica  MusicBrainz: tags, en ingles y tal como los da
  libros  Open Library: tags, los que reconoce una lista blanca de generos

Uso:
  scripts/datos.py                    rellena los campos vacios
  scripts/datos.py --force            reescribe tambien los que ya tienen valor
  scripts/datos.py --seccion juegos   solo esa carpeta
  scripts/datos.py --dry-run          dice que pondria, sin tocar nada
  scripts/datos.py content/juegos/Hollow\\ Knight.md   una ficha suelta
"""

import argparse
import re
import sys
import time
from pathlib import Path

from vitrina import (SECCIONES, VAULT, articulo_html, articulos_ingleses,
                       asegurar_letterboxd, escribir_campos, ficha_letterboxd,
                       frontmatter, pedir, vacio)

# La tienda de Steam corta sobre las 200 peticiones cada cinco minutos. Con una
# biblioteca normal no se llega, pero se va sin prisa por si acaso.
ESPERA = 1.5

MAX_TAGS = 4  # los generos de Steam vienen del mas general al mas concreto


def etiqueta(texto):
    """Un genero tal cual viene -> un tag: en minuscula y sin espacios.

    Se dejan los acentos. Son etiquetas que se leen en la ficha y en la pagina
    de tags, y "accion" al lado de "aventura" canta.
    """
    return re.sub(r"\s+", "-", (texto or "").strip().lower())


# --- fuentes -----------------------------------------------------------------

def datos_juego(titulo, campos, md):
    del md
    del titulo  # aqui manda el appid, que identifica el juego sin dudas
    appid = campos.get("appid")
    if not appid:
        return {}, "la ficha no tiene appid; se pone a mano"

    respuesta = pedir("https://store.steampowered.com/api/appdetails"
                      f"?appids={appid}&l=spanish&cc=es") or {}
    entrada = respuesta.get(str(appid)) or {}
    if not entrada.get("success"):
        # Pasa con lo retirado de la tienda y con lo que ya no es una app suya.
        return {}, f"la tienda no tiene ficha del appid {appid}"
    datos = entrada.get("data") or {}

    valores = {}
    # La fecha viene en el idioma pedido y con formatos distintos segun el
    # juego ("22 OCT 2025", "Oct 2025", "Por anunciar"): del año para arriba no
    # hay nada que ordenar en la galeria, asi que solo se saca el año.
    año = re.search(r"\b(1\d{3}|20\d{2})\b", (datos.get("release_date") or {}).get("date") or "")
    if año:
        valores["year"] = int(año.group(1))
    # El estudio antes que la distribuidora: en la ficha `autor` es quien lo
    # hizo, igual que la direccion en una pelicula y no la productora.
    estudios = datos.get("developers") or datos.get("publishers") or []
    if estudios:
        valores["autor"] = ", ".join(estudios[:2])
    # Los generos vienen ya en español, porque la ficha se pide con l=spanish.
    generos = [etiqueta(g.get("description")) for g in datos.get("genres") or []]
    generos = [g for g in generos if g][:MAX_TAGS]
    if generos:
        valores["tags"] = generos
    return valores, f"Steam ({datos.get('name') or appid})"


# En la ficha lateral del articulo en ingles, la fila que dice quien dirige.
DIRECCION_RE = re.compile(r"<th[^>]*>\s*Directed by\s*</th>\s*<td[^>]*>(.*?)</td>",
                          re.S | re.I)


# Los diecinueve generos de Letterboxd, que son lista cerrada, al castellano.
# Una tabla y no una traduccion al vuelo: asi "Action" y el genero de Steam
# caen los dos en `acción` y la pagina de esa etiqueta junta las peliculas con
# los juegos, que es de lo que sirve una etiqueta. Lo que no este aqui se
# escribe tal cual y se nota, que es mejor que inventarselo.
GENEROS_LETTERBOXD = {
    "action": "acción",
    "adventure": "aventura",
    "animation": "animación",
    "comedy": "comedia",
    "crime": "crimen",
    "documentary": "documental",
    "drama": "drama",
    "family": "familia",
    "fantasy": "fantasía",
    "history": "historia",
    "horror": "terror",
    "music": "música",
    "mystery": "misterio",
    "romance": "romance",
    "science fiction": "ciencia-ficción",
    "thriller": "suspense",
    "tv movie": "película-de-tv",
    "war": "guerra",
    "western": "western",
}


def datos_peli(titulo, campos, md):
    """La direccion y los generos, de la ficha de Letterboxd.

    Ni el export de Letterboxd ni su RSS traen el director, asi que las
    peliculas importadas se quedan sin `autor`. Sale de la misma pagina de la
    que ya sale el cartel y de la misma peticion, asi que llega gratis. Si la
    pelicula no se ha podido identificar queda Wikipedia, que lo trae en la
    ficha lateral pero hay que rascarlo del HTML.

    Los generos salen de esa misma peticion y solo de ella: Wikipedia no los
    da en una fila fija que se pueda leer sin adivinar, asi que una pelicula
    sin id de Letterboxd se queda sin etiquetas y con su director.
    """
    slug_lb, detalle = asegurar_letterboxd(md, campos)
    if slug_lb:
        ficha = ficha_letterboxd(slug_lb)
        valores = {}
        direccion = ficha.get("direccion")
        if direccion:
            valores["autor"] = ", ".join(direccion[:2])
        generos = [etiqueta(GENEROS_LETTERBOXD.get(g.strip().lower(), g))
                   for g in ficha.get("generos") or []]
        generos = [g for g in generos if g][:MAX_TAGS]
        if generos:
            valores["tags"] = generos
        if valores:
            return valores, f"Letterboxd ({slug_lb})"

    for articulo in articulos_ingleses(titulo, campos.get("year")):
        m = DIRECCION_RE.search(articulo_html(articulo))
        if not m:
            continue
        # La celda trae enlaces, y con varios directores una lista o <br>. Y a
        # veces un <style> suelto: quitar solo las etiquetas deja el CSS de
        # dentro, que se colaba de director en las peliculas con dos.
        celda = re.sub(r"<(style|script)\b.*?</\1>", " ", m.group(1), flags=re.S | re.I)
        nombres = [re.sub(r"\[\d+\]", "", n).strip()
                   for n in re.sub(r"<[^>]+>", "\n", celda).split("\n")]
        nombres = [n for n in nombres if len(n) > 2 and not re.search(r"[{}:;]", n)][:2]
        if nombres:
            return {"autor": ", ".join(nombres)}, f"Wikipedia ({articulo})"
    return {}, (detalle if not slug_lb else "su ficha de Letterboxd no dice quien dirige")


def datos_album(titulo, campos, md):
    """Los generos del disco, de MusicBrainz.

    Los vota la gente, asi que vienen ordenados por votos y con cola: In
    Rainbows trae diecisiete, de `alternative rock` a `krautrock`. Se cortan
    por MAX_TAGS, que deja los mas votados, que son los que describen el disco.

    **Van en ingles, tal como los da MusicBrainz.** Es lo unico del sitio que
    no esta en castellano, y es a proposito: los generos de Steam y los de
    Letterboxd salen de listas cerradas que se pueden traducir de una vez, y el
    de MusicBrainz es abierto y de miles de entradas. Traducir sobre la marcha
    seria adivinar, y con los generos musicales encima se discute: `emo` o
    `pop punk` no tienen version castellana que nadie use.
    """
    del titulo  # manda el mbid, que identifica el disco sin dudas
    mbid = campos.get("mbid")
    if not mbid:
        return {}, "la ficha no tiene mbid; se pone a mano"
    del md

    datos = pedir(f"https://musicbrainz.org/ws/2/release-group/{mbid}"
                  "?fmt=json&inc=genres")
    if datos is None:
        return {}, f"MusicBrainz no responde por el mbid {mbid}"
    generos = sorted(datos.get("genres") or [],
                     key=lambda g: -(g.get("count") or 0))
    generos = [etiqueta(g.get("name")) for g in generos]
    generos = [g for g in generos if g][:MAX_TAGS]
    if not generos:
        return {}, f"MusicBrainz no tiene generos votados de {mbid}"
    return {"tags": generos}, f"MusicBrainz ({datos.get('title') or mbid})"


# Los generos de Open Library que valen como genero, y a que tag caen. Los
# destinos son los mismos de la tabla de Letterboxd a proposito: asi un libro de
# ciencia-ficcion y una peli de ciencia-ficcion caen en la misma pagina de
# etiqueta, que es de lo que sirve una etiqueta.
#
# Es lista blanca y no traduccion, y esa es la diferencia con las otras tres
# fuentes. Steam y Letterboxd dan generos --lista cerrada, ordenada, y los
# primeros describen la obra-- asi que alli basta con coger los primeros y
# traducirlos. Lo que Open Library llama `subject` no son generos: es la
# catalogacion de una biblioteca, sin orden y de tamaño libre. `L'etranger` trae
# sesenta, y entre ellos estan mezclados el genero de verdad ("Philosophical
# Novels"), el tema del argumento ("Murder", "Young men", "Death"), el idioma de
# una edicion ("French language materials"), el formato ("Large type books") y
# la ficha de catalogo ("Fictional Works [Publication Type]"). Coger los cuatro
# primeros de eso le pondria a Camus `ficcion, asesinato, frances`.
#
# Asi que se busca al reves: de los sesenta, cuales estan en esta tabla. Lo que
# no este no se escribe. Y la mitad de los que valen no vienen sueltos sino
# dentro de una cabecera de BISAC --"Fiction, Mystery & Detective, General"--,
# que es como clasifican las editoriales lo que publican; de partirlas se
# encarga generos_de_subjects. Eso deja libros sin etiquetas --los clasicos
# traducidos, sobre todo, que es justo lo que hay hoy en la vault-- y es la
# decision correcta para este script: una ficha sin tags se ve y se arregla a
# mano; una con `aventura` puesto por una maquina en `El extranjero` se queda
# ahi para siempre.
#
# La tabla es corta a proposito. Cada vez que se le mete un genero blando
# --"classics", "history", "adventure stories", "satire"-- empieza a acertar en
# los libros de genero y a fallar en los demas: con esos cuatro dentro, `1984`
# salia de comedia y `El extranjero` de aventuras.
GENEROS_OPENLIBRARY = {
    "science fiction": "ciencia-ficción",
    "science-fiction": "ciencia-ficción",
    "sci-fi": "ciencia-ficción",
    "hard science-fiction": "ciencia-ficción",
    "ciencia-ficción": "ciencia-ficción",
    "fantasy fiction": "fantasía",
    "epic fiction": "fantasía",
    "horror": "terror",
    "horror fiction": "terror",
    "thrillers": "suspense",
    "suspense": "suspense",
    "mystery": "misterio",
    "mystery fiction": "misterio",
    "detective and mystery stories": "misterio",
    # Los tramos de BISAC, que no aparecen sueltos sino dentro de la cabecera:
    # "Fiction / Mystery & Detective / General".
    "mystery & detective": "misterio",
    "war & military": "guerra",
    "american science fiction": "ciencia-ficción",
    "american fantasy fiction": "fantasía",
    "crime": "crimen",
    "love stories": "romance",
    "romance": "romance",
    "historical fiction": "historia",
    "war stories": "guerra",
    # Los dos unicos "blandos" que sobreviven, y por medido: son los que dejan
    # etiquetado a Camus sin tocar ninguno de los otros trece libros de prueba.
    "philosophical novels": "filosofía",
    "philosophical fiction": "filosofía",
    "biography": "biografía",
    "poetry": "poesía",
}


# Una cabecera de BISAC, que es el vocabulario con el que las editoriales
# clasifican lo que publican: "Fiction / Science Fiction / Hard Science Fiction",
# o con comas, que Open Library escribe de las dos formas. Empiezan siempre por
# una categoria de arriba, y esas son las tres que traen novela.
BISAC_RE = re.compile(r"^(fiction|juvenile fiction|young adult fiction)\b")


def generos_de_subjects(subjects):
    """Los `subject` de Open Library -> los tags que reconoce la tabla.

    Mira cada subject entero y, si es una cabecera de BISAC, tambien sus tramos
    por separado. Eso es lo que saca el genero de la mitad de los libros: lo que
    la editorial declara no viene como `horror` a secas sino como "Fiction,
    Horror", y buscando la cadena entera se tiraba entera. Partirla no es
    adivinar, porque BISAC es una lista cerrada y el tramo del medio es
    justamente el genero.

    Solo se parten las que empiezan por una categoria de BISAC. Un subject
    suelto se queda de una pieza a proposito: `1984` trae "fantasy" por su
    cuenta, y ese sale de que alguien lo puso en un estante, no de la editorial.

    En el orden de la tabla y no en el que vengan: los subjects no traen
    ninguno, asi que el de la fuente no significa nada y el de la tabla al menos
    es siempre el mismo. Sin repetidos, que los hay: "science fiction" y
    "sci-fi" son el mismo tag y un libro suele traer los dos.
    """
    dichos = set()
    for s in subjects or []:
        s = str(s).strip().lower()
        if not s:
            continue
        dichos.add(s)
        if BISAC_RE.match(s):
            dichos.update(t for t in re.split(r"\s*[/,]\s*", s) if t)

    salida = []
    for subject, tag in GENEROS_OPENLIBRARY.items():
        if subject in dichos and tag not in salida:
            salida.append(tag)
    return salida[:MAX_TAGS]


def datos_libro(titulo, campos, md):
    """Los generos del libro, de Open Library.

    Manda el `coverid`, que es lo unico que el importador guardo. Identifica la
    portada y no la obra, pero el buscador de Open Library lo admite como campo
    --`q=cover_i:13151269`-- y devuelve la obra a la que pertenece esa portada,
    una y solo una. Asi que no hay que buscar por titulo, que es lo que este
    script no hace en ninguna de sus fuentes.

    Que devuelva pocos generos, o ninguno, es lo normal y no es un fallo: la
    edicion que dio la portada suele ser la castellana, y las fichas de las
    traducciones estan mucho mas vacias que las inglesas. Cuando no hay, no se
    escribe nada.
    """
    del titulo, md  # manda el coverid, que lleva a una obra y no a dos
    coverid = campos.get("coverid")
    if vacio(coverid):
        return {}, "la ficha no tiene coverid; se pone a mano"

    datos = pedir("https://openlibrary.org/search.json?limit=1"
                  f"&fields=title,key,subject&q=cover_i%3A{coverid}")
    if datos is None:
        return {}, f"Open Library no responde por el coverid {coverid}"
    docs = datos.get("docs") or []
    if not docs:
        return {}, f"Open Library no encuentra la obra del coverid {coverid}"

    obra = docs[0]
    generos = generos_de_subjects(obra.get("subject"))
    if not generos:
        return {}, ("Open Library no dice de que genero es "
                    f"{obra.get('title') or coverid}")
    return {"tags": generos}, f"Open Library ({obra.get('title') or obra.get('key')})"


# Que sabe rellenar cada seccion, y en que campos.
FUENTES = {"juego": (datos_juego, ("year", "autor", "tags")),
           "peli": (datos_peli, ("autor", "tags")),
           "album": (datos_album, ("tags",)),
           "libro": (datos_libro, ("tags",))}


# --- recorrido ---------------------------------------------------------------

def fichas(args):
    if args.ficha:
        return [Path(f).resolve() for f in args.ficha]
    # Sin --seccion se recorre solo lo que tiene fuente, para no listar como
    # fallo lo que no la tiene y se rellena a mano de todos modos.
    carpetas = [args.seccion] if args.seccion else [
        c for c, tipo in SECCIONES.items() if tipo in FUENTES]
    salida = []
    for carpeta in carpetas:
        salida += sorted(p for p in (VAULT / carpeta).glob("*.md") if p.stem != "index")
    return salida


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ficha", nargs="*", help="fichas sueltas; por defecto, todas")
    p.add_argument("--seccion", choices=list(SECCIONES), help="solo una carpeta")
    p.add_argument("--force", action="store_true",
                   help="reescribe los campos que ya tienen valor")
    p.add_argument("--dry-run", action="store_true", help="no consulta ni escribe nada")
    args = p.parse_args()

    hechas = fallidas = saltadas = 0

    for md in fichas(args):
        campos = frontmatter(md.read_text(encoding="utf-8"))
        tipo = campos.get("tipo") or SECCIONES.get(md.parent.name)
        titulo = campos.get("title") or md.stem
        nombre = f"{md.parent.name}/{md.stem}"
        if tipo not in FUENTES:
            print(f"  ?  {nombre}: no hay fuente para '{tipo}'; se rellena a mano")
            fallidas += 1
            continue

        fuente, esperados = FUENTES[tipo]
        faltan = (list(esperados) if args.force
                  else [c for c in esperados if vacio(campos.get(c))])
        if not faltan:
            saltadas += 1
            continue
        if args.dry_run:
            print(f"  ·  {nombre}: buscaría {', '.join(faltan)}")
            continue

        valores, detalle = fuente(titulo, campos, md)
        # Lo que ya estuviera puesto a mano no se pisa salvo con --force.
        valores = {c: v for c, v in valores.items() if c in faltan}
        if not valores:
            print(f"  ✗  {nombre}: {detalle}")
            fallidas += 1
            continue

        escribir_campos(md, valores)
        puesto = ", ".join(f"{c}: {', '.join(v) if isinstance(v, list) else v}"
                           for c, v in valores.items())
        print(f"  ✓  {nombre}: {puesto}  —  {detalle}")
        hechas += 1
        time.sleep(ESPERA)

    print(f"\n{hechas} fichas completadas, {fallidas} sin resolver, "
          f"{saltadas} ya estaban.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
