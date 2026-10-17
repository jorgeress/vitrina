#!/usr/bin/env python3
"""Cuando terminaste o empezaste cada cosa, de los sitios que lo apuntan.

Pone en la cabecera, solo donde este vacio:

  finished_on   peliculas, del diario de Letterboxd (el dia que la viste)
                libros, de la estanteria "read" de Goodreads (el dia que la
                marcaste leida)
  started_on    juegos, del primer logro de Steam (el mes: el primer logro
                llega en la primera partida o poco despues, no el dia exacto)
                discos, de la primera escucha en ListenBrainz o en el
                historial ampliado de Spotify
  times         peliculas, cuantas veces esta en el diario, si es mas de una
                y el diario lo tiene entero (solo el export)

  scripts/cuando.py                          las cuentas de vitrine.local.json
  scripts/cuando.py letterboxd USUARIO       el RSS: las ultimas cincuenta o asi
  scripts/cuando.py letterboxd RUTA          el export (diary.csv), entero
  scripts/cuando.py steam PERFIL             el id de 17 cifras o la direccion
  scripts/cuando.py goodreads USUARIO        el numero de goodreads.com/user/show/
  scripts/cuando.py listenbrainz USUARIO
  scripts/cuando.py spotify RUTA             el zip del historial ampliado
  --dry-run                                  dice que pondria, sin tocar nada

Las cuentas se pueden dejar en vitrine.local.json, en la raiz, que git no sube:

  {"accounts": {"letterboxd": "...", "steam": "7656119...", "goodreads": "...",
                "listenbrainz": "..."}}

Sin nada detras, `cuando.py` pasa por todas las que esten. No van en
vitrine.config.json porque ese se publica, y un perfil de Steam o de Goodreads
dice de quien es la vitrina mas de lo que hace falta.

Antes vacio que equivocado:
  - Una pelicula cuya primera entrada en el diario ya es un revisionado se
    vio antes de que empezara el diario: no se sabe cuando, y no se pone.
  - Un disco cuya primera escucha cae en el primer mes del registro
    probablemente sonaba ya antes de que empezaras a registrar: no se pone.
  - Cada obra se cruza por su id (el slug de Letterboxd, el appid, el mbid);
    los libros y los discos sin id, por titulo y autor a la vez, nunca solo
    por titulo.

Ninguna fuente pide clave. Steam y Goodreads necesitan el perfil publico.
"""
import argparse
import csv
import datetime as dt
import io
import json
import re
import sys
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

from idioma import ayuda
from vitrina import _, CONFIG, RAIZ, SECCIONES, escribir_campos, fichas, frontmatter, normal, pedir, vacio

LB = {"letterboxd": "https://letterboxd.com"}
# Lo que suena en el primer mes de un registro no es tu primera escucha, sino
# el dia en que empezaste a registrar.
MARGEN_REGISTRO = dt.timedelta(days=30)
# Steam estreno los logros en 2007: una fecha anterior es que no la sabe.
LOGROS_DESDE = int(dt.datetime(2007, 1, 1, tzinfo=dt.timezone.utc).timestamp())


# --- las fichas ---------------------------------------------------------------

def todas():
    """(md, campos, titulo) de cada ficha, con su tipo en los campos."""
    lista = []
    for carpeta, tipo in SECCIONES.items():
        for md in fichas(carpeta):
            c = frontmatter(md.read_text(encoding="utf-8"))
            c.setdefault("type", tipo)
            lista.append((md, c, c.get("title") or md.stem))
    return lista


def limpio(titulo):
    """El titulo para comparar: sin lo que cada sitio le cuelga detras.
    «Abbey Road (Remastered)», «Abbey Road - 2019 Mix», «El nombre del viento
    (Crónica del asesino de reyes, #1)» → abbeyroad / elnombredelviento."""
    t = re.sub(r"\s*[\(\[][^)\]]*[\)\]]\s*$", "", titulo or "")
    t = re.sub(r"\s+-\s+.*(remaster|edition|version|mix|deluxe).*$", "", t, flags=re.I)
    return normal(t)


def mismo_autor(de_la_ficha, de_la_fuente):
    """Si comparten autor. La ficha puede llevar varios, separados por coma o
    en lista; basta con que uno coincida entero."""
    autores = de_la_ficha if isinstance(de_la_ficha, list) else re.split(r",\s*|\s+&\s+|\s+y\s+", de_la_ficha or "")
    fuente = normal(de_la_fuente)
    return bool(fuente) and any(normal(a) == fuente for a in autores if a)


def poner(md, c, nuevos, args, cambios):
    """Escribe solo lo que la ficha no tiene ya."""
    nuevos = {k: v for k, v in nuevos.items() if v and vacio(str(c.get(k) or ""))}
    if not nuevos:
        return
    cambios.append(md)
    resumen = ", ".join(f"{k}={v}" for k, v in nuevos.items())
    print(f"  ✓  {md.parent.name}/{md.stem}: {resumen}")
    if not args.dry_run:
        escribir_campos(md, nuevos)


# --- Letterboxd -----------------------------------------------------------------

def diario_rss(usuario):
    """[(slug, fecha, revisionado)] de las ultimas entradas del diario.

    La pagina del diario la cierra Cloudflare a quien no es un navegador (da
    403); el RSS no, pero trae solo las ultimas cincuenta peliculas o asi y no
    pagina (?page=2 devuelve las mismas). Pasandolo de vez en cuando, que es lo
    que hace al-dia.py, no se pierde nada.
    """
    crudo = pedir(f"https://letterboxd.com/{usuario}/rss/", binario=True)
    if not crudo:
        return None
    entradas = []
    for item in ElementTree.fromstring(crudo).iter("item"):
        fecha = item.findtext("letterboxd:watchedDate", namespaces=LB)
        slug = re.search(r"/film/([^/]+)/", item.findtext("link") or "")
        if fecha and slug:
            entradas.append((slug.group(1), fecha, item.findtext("letterboxd:rewatch", namespaces=LB) == "Yes"))
    return entradas


def diario_csv(ruta):
    """[(titulo, año, fecha, revisionado)] del diary.csv del export."""
    from importar import ficheros
    filas = []
    for nombre, datos in ficheros(ruta, r"^diary\.csv$"):
        for f in csv.DictReader(io.StringIO(datos.decode("utf-8-sig"))):
            if f.get("Name") and f.get("Watched Date"):
                filas.append((f["Name"], f.get("Year") or "", f["Watched Date"], (f.get("Rewatch") or "").lower() == "yes"))
    return filas


def primera_vista(entradas):
    """La fecha de la primera vez, o None si la primera entrada ya es un
    revisionado (la viste antes de que empezara el diario)."""
    entradas = sorted(entradas)
    return None if entradas[0][1] else entradas[0][0]


def letterboxd(fuente, lista, args, cambios):
    pelis = [(md, c, t) for md, c, t in lista if c.get("type") == "film"]
    if Path(fuente).expanduser().exists():
        filas = diario_csv(fuente)
        if not filas:
            print(_("No he encontrado diary.csv en esa ruta."))
            return 1
        print(_("Diario de Letterboxd (export): {n} entradas.").format(n=len(filas)))
        por_obra = {}
        for nombre, año, fecha, otra_vez in filas:
            por_obra.setdefault((limpio(nombre), año), []).append((fecha, otra_vez))
        for md, c, titulo in pelis:
            vistas = por_obra.get((limpio(titulo), str(c.get("year") or "")))
            if not vistas:
                continue
            primera = primera_vista(vistas)
            # El export tiene el diario entero: ahi si se pueden contar. Si la
            # primera ya era un revisionado, faltan las de antes y no se cuenta.
            veces = len(vistas) if primera and len(vistas) > 1 else None
            poner(md, c, {"finished_on": primera, "times": veces}, args, cambios)
        return 0

    usuario = fuente.strip().strip("/").split("/")[-1]
    entradas = diario_rss(usuario)
    if entradas is None:
        print(_("No he podido leer el diario de '{usuario}'. Comprueba el nombre y\n"
                "que el perfil no sea privado.").format(usuario=usuario))
        return 1
    print(_("Diario de Letterboxd de {usuario}: {n} entradas.").format(usuario=usuario, n=len(entradas)))
    por_slug = {}
    for slug, fecha, otra_vez in entradas:
        por_slug.setdefault(slug, []).append((fecha, otra_vez))
    for md, c, _t in pelis:
        vistas = por_slug.get(str(c.get("letterboxd") or ""))
        if vistas:
            poner(md, c, {"finished_on": primera_vista(vistas)}, args, cambios)
    return 0


# --- Steam ------------------------------------------------------------------------

def perfil_steam(texto):
    """La direccion de los logros: /profiles/<id> o /id/<nombre>."""
    texto = texto.strip().rstrip("/")
    m = re.search(r"(?:profiles/)?(\d{17})$", texto)
    if m:
        return f"profiles/{m.group(1)}"
    return "id/" + texto.split("/")[-1]


def primer_logro(perfil, appid):
    """La fecha del primer logro de ese juego, o "privado" si Steam no deja verlo.

    Es la pagina publica de logros con ?xml=1, sin clave. El nombre que sale en
    el perfil no tiene por que ser la direccion: /id/<nombre> solo vale si se
    ha puesto una direccion personalizada, y si no puede ser de otra persona.
    Con el id de 17 cifras no hay duda.
    """
    crudo = pedir(f"https://steamcommunity.com/{perfil}/stats/{appid}/achievements/?xml=1", binario=True)
    if not crudo:
        return None
    try:
        raiz = ElementTree.fromstring(crudo)
    except ElementTree.ParseError:
        return None  # sin logros, Steam contesta con la pagina del juego
    if raiz.findtext("privacyState") == "private":
        return "privado"
    marcas = [int(a.findtext("unlockTimestamp") or 0) for a in raiz.iter("achievement") if a.get("closed") == "1"]
    # Algunos logros conseguidos salen con fecha 0 (1970): Steam no sabe
    # cuando. Si hay uno asi, el primero de verdad puede ser ese, y no se pone.
    if not marcas or min(marcas) < LOGROS_DESDE:
        return None
    return dt.datetime.fromtimestamp(min(marcas), dt.timezone.utc)


def steam(fuente, lista, args, cambios):
    perfil = perfil_steam(fuente)
    juegos = [(md, c, t) for md, c, t in lista
              if c.get("type") == "game" and not vacio(str(c.get("appid") or "")) and vacio(str(c.get("started_on") or ""))]
    print(_("Logros de Steam: {n} juegos por mirar.").format(n=len(juegos)))
    for md, c, _t in juegos:
        cuando = primer_logro(perfil, c["appid"])
        if cuando == "privado":
            print(_("Los logros de ese perfil son privados. En Steam: Editar perfil →\n"
                    "Privacidad → Detalles de juegos, en Público."))
            return 1
        if cuando:
            poner(md, c, {"started_on": cuando.strftime("%Y-%m")}, args, cambios)
        time.sleep(0.5)
    return 0


# --- Goodreads -------------------------------------------------------------------

def goodreads(fuente, lista, args, cambios):
    """La estanteria "read", del RSS publico, que si pagina (de cien en cien)."""
    usuario = re.search(r"(\d+)", fuente)
    if not usuario:
        print(_("De Goodreads hace falta el número de usuario: el de goodreads.com/user/show/NÚMERO."))
        return 1
    leidos = []
    for pagina in range(1, 51):
        crudo = pedir(f"https://www.goodreads.com/review/list_rss/{usuario.group(1)}?shelf=read&page={pagina}",
                      binario=True)
        if not crudo:
            break
        items = list(ElementTree.fromstring(crudo).iter("item"))
        for i in items:
            leido = (i.findtext("user_read_at") or "").strip()
            if leido:
                leidos.append((i.findtext("title") or "", i.findtext("author_name") or "",
                               parsedate_to_datetime(leido).strftime("%Y-%m-%d")))
        if len(items) < 100:
            break
    if not leidos:
        print(_("Goodreads no ha devuelto ningún libro con fecha de leído. Comprueba el\n"
                "número y que la estantería sea pública."))
        return 1
    print(_("Goodreads: {n} libros con fecha de leído.").format(n=len(leidos)))
    for md, c, titulo in lista:
        if c.get("type") != "book":
            continue
        # Un libro releido sale una vez por lectura: vale la primera.
        fechas = [f for t, a, f in leidos if limpio(t) == limpio(titulo) and mismo_autor(c.get("author"), a)]
        if fechas:
            poner(md, c, {"finished_on": min(fechas)}, args, cambios)
    return 0


# --- discos: ListenBrainz y Spotify -----------------------------------------------

def primeras_escuchas(escuchas, lista, args, cambios):
    """escuchas: [(datetime, artista, disco, mbid del disco o None)].

    Se cruza por mbid cuando la escucha lo trae y, si no, por disco y artista a
    la vez. Lo que suena en el primer mes del registro no cuenta (ver arriba).
    """
    if not escuchas:
        return
    inicio = min(e[0] for e in escuchas) + MARGEN_REGISTRO
    por_mbid, por_nombre = {}, {}
    for cuando, artista, disco, mbid in escuchas:
        if mbid:
            por_mbid[mbid] = min(cuando, por_mbid.get(mbid, cuando))
        clave = (limpio(disco), normal(artista))
        por_nombre[clave] = min(cuando, por_nombre.get(clave, cuando))
    for md, c, titulo in lista:
        if c.get("type") != "album":
            continue
        candidatas = [por_mbid.get(str(c.get("mbid") or ""))]
        autores = c.get("author") if isinstance(c.get("author"), list) else [c.get("author") or ""]
        candidatas += [por_nombre.get((limpio(titulo), normal(a))) for a in autores]
        candidatas = [x for x in candidatas if x]
        if candidatas and min(candidatas) >= inicio:
            poner(md, c, {"started_on": min(candidatas).strftime("%Y-%m-%d")}, args, cambios)


def listenbrainz(usuario, lista, args, cambios):
    """Todas las escuchas, de mil en mil hacia atras. Sin clave: son publicas."""
    usuario = usuario.strip().strip("/").split("/")[-1]
    escuchas, hasta = [], None
    for _vuelta in range(2000):
        url = f"https://api.listenbrainz.org/1/user/{usuario}/listens?count=1000"
        r = pedir(url + (f"&max_ts={hasta}" if hasta else ""))
        lote = ((r or {}).get("payload") or {}).get("listens") or []
        if not lote:
            break
        for e in lote:
            m = e.get("track_metadata") or {}
            extra = m.get("additional_info") or {}
            escuchas.append((dt.datetime.fromtimestamp(e["listened_at"], dt.timezone.utc),
                             m.get("artist_name") or "", m.get("release_name") or "",
                             extra.get("release_group_mbid")))
        hasta = lote[-1]["listened_at"]
    if not escuchas:
        print(_("ListenBrainz no tiene escuchas de '{usuario}'.").format(usuario=usuario))
        return 1
    print(_("ListenBrainz: {n} escuchas.").format(n=len(escuchas)))
    primeras_escuchas(escuchas, lista, args, cambios)
    return 0


def spotify(ruta, lista, args, cambios):
    """El historial ampliado (Streaming_History_Audio_*.json), que trae el disco
    de cada cancion. El export normal de la cuenta no lo trae, y solo cubre un
    año: con ese no se puede."""
    from importar import ficheros
    escuchas = []
    for _nombre, datos in ficheros(ruta, r"^(Streaming_History_Audio|endsong).*\.json$"):
        for e in json.loads(datos):
            disco = e.get("master_metadata_album_album_name")
            # Menos de treinta segundos es saltarla, no escucharla.
            if disco and (e.get("ms_played") or 0) >= 30000:
                escuchas.append((dt.datetime.fromisoformat(e["ts"].replace("Z", "+00:00")),
                                 e.get("master_metadata_album_artist_name") or "", disco, None))
    if not escuchas:
        print(_("No he encontrado el historial ampliado de Spotify en esa ruta\n"
                "(Streaming_History_Audio_*.json). El export normal no trae los discos."))
        return 1
    print(_("Spotify: {n} escuchas.").format(n=len(escuchas)))
    primeras_escuchas(escuchas, lista, args, cambios)
    return 0


FUENTES = {"letterboxd": letterboxd, "steam": steam, "goodreads": goodreads,
           "listenbrainz": listenbrainz, "spotify": spotify}


def main(argv=None):
    p = argparse.ArgumentParser(description=ayuda(__doc__, "cuando"), formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fuente", nargs="?", choices=sorted(FUENTES), help=_("de dónde; sin nada, las de la config"))
    p.add_argument("cuenta", nargs="?", help=_("usuario, perfil o ruta del export"))
    p.add_argument("--dry-run", action="store_true", help=_("dice que pondria, sin tocar nada"))
    args = p.parse_args(argv)

    local = RAIZ / "vitrine.local.json"
    cuentas = {**(CONFIG.get("accounts") or {}),
               **(json.loads(local.read_text(encoding="utf-8")).get("accounts") or {} if local.exists() else {})}
    if args.fuente:
        pares = [(args.fuente, args.cuenta or cuentas.get(args.fuente))]
    else:
        pares = [(f, v) for f, v in cuentas.items() if f in FUENTES and v]
    pares = [(f, v) for f, v in pares if v]
    if not pares and not args.fuente:
        # Desde al-dia.py, sin cuentas, no hay nada que hacer: no es un fallo.
        print(_("Sin cuentas en vitrine.local.json: nada que mirar."))
        return 0
    if not pares:
        print(_("No sé de dónde sacarlo: pon la cuenta detrás (scripts/cuando.py\n"
                "letterboxd TU_USUARIO) o déjala en vitrine.local.json."))
        return 1

    lista = todas()
    cambios, fallos = [], 0
    for fuente, cuenta in pares:
        fallos += FUENTES[fuente](str(cuenta), lista, args, cambios) or 0
    hecho = _("{n} ficha(s) cambiarían.") if args.dry_run else _("{n} ficha(s) cambiada(s).")
    print(hecho.format(n=len(cambios)))
    return 1 if fallos and not cambios else 0


if __name__ == "__main__":
    sys.exit(main())
