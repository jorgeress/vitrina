#!/usr/bin/env python3
"""Empieza una vitrina nueva a partir de esta: la plantilla de Vitrine.

Quien hace un fork, o usa el repo como plantilla en GitHub, se lleva la
coleccion de otro. Esto deja la vault lista para la suya, en castellano o en
ingles:

  - vitrine.config.json con el nombre, el idioma, el dueño y la direccion
    (sale del repo: github.com/alguien/estante -> alguien.github.io/estante);
  - las carpetas de las salas, con el nombre en su idioma (juegos o games...),
    cada una con su index.md y su vista de Obsidian (.base);
  - la entrada (index.md), lo mejor de lo mejor, lo recien llegado, los
    creditos y las plantillas de ficha y de grupo;
  - la plantilla del Issue para añadir desde el movil.

Con --vaciar quita ademas lo que es de la coleccion anterior: las fichas, las
paginas de autor, los grupos y las portadas. Pide --si para hacerlo de
verdad, que es borrar; sin el, dice lo que borraria.

Uso:
  scripts/empezar.py --idioma en --nombre "Vitrine" --dueno "Alex" \\
      --repo https://github.com/alex/vitrine --vaciar --si
  scripts/empezar.py --idioma es --solo-vistas    rehace solo las vistas
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VAULT = RAIZ / "content"
CONFIG = RAIZ / "vitrine.config.json"

TIPOS = ("game", "film", "series", "book", "album")

# Todo lo que cambia con el idioma: carpetas, rotulos de las vistas y textos
# de las notas que se crean.
IDIOMAS = {
    "es": {
        "carpetas": {"game": "juegos", "film": "pelis", "series": "series", "book": "libros",
                     "album": "musica", "author": "autores", "private": "privado",
                     "group": "grupos"},
        "salas": {"game": "Juegos", "film": "Películas", "series": "Series",
                  "book": "Libros", "album": "Música"},
        "bases": {"game": "Juegos", "film": "Peliculas", "series": "Series",
                  "book": "Libros", "album": "Musica", "mejor": "Favoritos",
                  "recientes": "Recientes"},
        "autoria": {"game": "Estudio", "film": "Dirección", "series": "Creación",
                    "book": "Autor", "album": "Artista"},
        "queda": {"game": "Por jugar", "film": "Por ver", "series": "Por ver",
                  "book": "Por leer", "album": "Por escuchar"},
        "titulo": "Título", "año": "Año", "nota": "Nota", "tipo": "Tipo",
        "autoria_mezcla": "Autoría", "seccion": "Sección",
        "galeria": "Galería", "tabla": "Tabla", "favoritos": "Favoritos",
        "todo_junto": "Todo junto", "por_tipo": "Por tipo",
        "recien": "Recién llegadas", "mejor": "Lo mejor de lo mejor",
        "mejor_texto": "Las salas juntas, filtradas a lo marcado como favorito.",
        "presentacion": ("Mi colección de lo que juego, veo, leo y escucho, y por qué "
                         "está cada cosa en la vitrina."),
        "recientes_titulo": "Recién llegadas a la vitrina",
        "autores": "Autores", "grupos": "Grupos",
        "creditos_fichero": "creditos", "creditos": "Créditos",
        "creditos_texto": (
            "Las carátulas son de sus respectivos autores y se usan aquí en miniatura, solo\n"
            "para identificar cada obra dentro del catálogo.\n\n"
            "- Las películas, de [Letterboxd](https://letterboxd.com) y "
            "[Wikidata](https://www.wikidata.org).\n"
            "- Las series, de [TVmaze](https://www.tvmaze.com), CC BY-SA.\n"
            "- Los libros, de [Open Library](https://openlibrary.org).\n"
            "- Los discos, de [Cover Art Archive](https://coverartarchive.org) y "
            "[MusicBrainz](https://musicbrainz.org).\n"
            "- Los juegos, de Steam y [Wikipedia](https://en.wikipedia.org).\n\n"
            "Ninguna de esas fuentes pide clave de API ni registro.\n"),
    },
    "en": {
        "carpetas": {"game": "games", "film": "films", "series": "series", "book": "books",
                     "album": "music", "author": "authors", "private": "private",
                     "group": "groups"},
        "salas": {"game": "Games", "film": "Films", "series": "Series",
                  "book": "Books", "album": "Music"},
        "bases": {"game": "Games", "film": "Films", "series": "Series",
                  "book": "Books", "album": "Music", "mejor": "Favorites",
                  "recientes": "Recent"},
        "autoria": {"game": "Studio", "film": "Director", "series": "Creator",
                    "book": "Author", "album": "Artist"},
        "queda": {"game": "To play", "film": "To watch", "series": "To watch",
                  "book": "To read", "album": "To listen"},
        "titulo": "Title", "año": "Year", "nota": "Rating", "tipo": "Type",
        "autoria_mezcla": "By", "seccion": "Room",
        "galeria": "Gallery", "tabla": "Table", "favoritos": "Favorites",
        "todo_junto": "All together", "por_tipo": "By type",
        "recien": "Just arrived", "mejor": "The best of the best",
        "mejor_texto": "Every room together, filtered to what's marked as a favorite.",
        "presentacion": ("My collection of what I play, watch, read and listen to, and why "
                         "each piece is on display."),
        "recientes_titulo": "Just arrived",
        "autores": "Authors", "grupos": "Groups",
        "creditos_fichero": "credits", "creditos": "Credits",
        "creditos_texto": (
            "Covers belong to their respective owners and are used here as thumbnails,\n"
            "only to identify each work in the catalogue.\n\n"
            "- Films, from [Letterboxd](https://letterboxd.com) and "
            "[Wikidata](https://www.wikidata.org).\n"
            "- Series, from [TVmaze](https://www.tvmaze.com), CC BY-SA.\n"
            "- Books, from [Open Library](https://openlibrary.org).\n"
            "- Albums, from [Cover Art Archive](https://coverartarchive.org) and "
            "[MusicBrainz](https://musicbrainz.org).\n"
            "- Games, from Steam and [Wikipedia](https://en.wikipedia.org).\n\n"
            "None of these sources needs an API key or an account.\n"),
    },
}


# --- las vistas de Obsidian ----------------------------------------------------
# Las mismas que las de la vitrina de partida, sin sus comentarios: la galeria
# por nota, la tabla, los favoritos y lo que queda (pendiente o empezado).

FORMULAS = """formulas:
  puntuacion: if(note.rating, note.rating, -1)
  nota: if(note.rating, note.rating, "—")
"""


def vista_tarjetas(nombre, ratio, filtro="", nota=True, orden="puntuacion"):
    texto = f"""  - type: cards
    name: {nombre}
"""
    if filtro:
        texto += filtro
    texto += """    order:
      - file.name
      - note.author
      - note.year
"""
    if nota:
        texto += "      - formula.nota\n"
    texto += "    sort:\n"
    if orden == "puntuacion":
        texto += "      - property: formula.puntuacion\n        direction: DESC\n"
    texto += f"""      - property: file.name
        direction: ASC
    image: note.cover
    cardSize: 220
    imageAspectRatio: {ratio}
"""
    return texto


def base_sala(tipo, t):
    ratio = 1 if tipo == "album" else 0.67
    return (FORMULAS + f"""filters:
  and:
    - note.type == "{tipo}"
properties:
  file.name:
    displayName: {t["titulo"]}
  note.year:
    displayName: {t["año"]}
  note.author:
    displayName: {t["autoria"][tipo]}
  note.rating:
    displayName: {t["nota"]}
views:
""" + vista_tarjetas(t["galeria"], ratio) + f"""  - type: table
    name: {t["tabla"]}
    order:
      - file.name
      - note.author
      - note.year
      - note.rating
    sort:
      - property: formula.puntuacion
        direction: DESC
      - property: file.name
        direction: ASC
""" + vista_tarjetas(t["favoritos"], ratio, "    filters:\n      and:\n        - note.favorite == true\n")
            + vista_tarjetas(t["queda"][tipo], ratio,
                             "    filters:\n      or:\n        - note.status == \"pending\"\n"
                             "        - note.status == \"in-progress\"\n",
                             nota=False, orden="titulo"))


def formula_sala(t):
    """El nombre de la sala de cada ficha, para las vistas que las mezclan."""
    texto = f'"{t["salas"]["album"]}"'
    for tipo in reversed(TIPOS[:-1]):
        texto = f'if(note.type == "{tipo}", "{t["salas"][tipo]}", {texto})'
    return texto


def base_mejor(t):
    return (FORMULAS + f"""  seccion: {formula_sala(t)}
filters:
  and:
    - note.favorite == true
properties:
  file.name:
    displayName: {t["titulo"]}
  note.author:
    displayName: {t["autoria_mezcla"]}
  note.rating:
    displayName: {t["nota"]}
  note.year:
    displayName: {t["año"]}
views:
  - type: cards
    name: {t["todo_junto"]}
    image: note.cover
    cardSize: 220
    imageAspectRatio: 0.67
    imageFit: contain
    order:
      - file.name
      - note.author
      - note.year
      - formula.nota
    sort:
      - property: formula.puntuacion
        direction: DESC
      - property: file.name
        direction: ASC
  - type: board
    name: {t["por_tipo"]}
    groupBy:
      property: formula.seccion
    order:
      - note.author
      - note.year
      - note.rating
    sort:
      - property: formula.puntuacion
        direction: DESC
      - property: file.name
        direction: ASC
""")


def base_recientes(t):
    tipos = "".join(f'    - note.type == "{tipo}"\n' for tipo in TIPOS)
    return f"""filters:
  or:
{tipos}formulas:
  seccion: {formula_sala(t)}
properties:
  file.name:
    displayName: {t["titulo"]}
  note.author:
    displayName: {t["autoria_mezcla"]}
  formula.seccion:
    displayName: {t["seccion"]}
views:
  - type: cards
    name: {t["recien"]}
    image: note.cover
    cardSize: 220
    imageAspectRatio: 0.67
    imageFit: contain
    limit: 12
    order:
      - file.name
      - formula.seccion
      - note.author
    sort:
      - property: note.added
        direction: DESC
      - property: file.name
        direction: ASC
"""


# --- las notas ------------------------------------------------------------------

def nota(titulo, cuerpo=""):
    return f"---\ntitle: {titulo}\n---\n\n{cuerpo}"


def vistas(idioma):
    """Las vistas y las notas indice de la vault: {ruta relativa: texto}."""
    t = IDIOMAS[idioma]
    c = t["carpetas"]
    b = t["bases"]
    ficheros = {}
    for tipo in TIPOS:
        ficheros[f"{b[tipo]}.base"] = base_sala(tipo, t)
        ficheros[f"{c[tipo]}/index.md"] = nota(t["salas"][tipo], f"![[{b[tipo]}.base]]\n")
    ficheros[f"{b['mejor']}.base"] = base_mejor(t)
    ficheros[f"{b['recientes']}.base"] = base_recientes(t)
    ficheros[f"{b['mejor']}.md"] = nota(t["mejor"], f"{t['mejor_texto']}\n\n![[{b['mejor']}.base]]\n")
    return ficheros


def portada(idioma):
    t = IDIOMAS[idioma]
    c, b = t["carpetas"], t["bases"]
    enlaces = "".join(f"- [[{c[tipo]}/index|{t['salas'][tipo]}]]\n" for tipo in TIPOS)
    enlaces += f"- [[{c['author']}/index|{t['autores']}]]\n- [[{b['mejor']}|{t['mejor']}]]\n"
    return nota("Vitrine" if idioma == "en" else "Vitrina",
                f"{t['presentacion']}\n\n{enlaces}\n## {t['recientes_titulo']}\n\n"
                f"![[{b['recientes']}.base]]\n\n[[{t['creditos_fichero']}|{t['creditos']}]] · "
                "[RSS](index.xml)\n")


def direccion(repo):
    """github.com/alguien/estante -> (https://alguien.github.io, /estante)."""
    m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+?)(?:\.git)?/?$", repo or "")
    if not m:
        return None, None
    usuario, nombre = m.groups()
    if nombre.lower() == f"{usuario.lower()}.github.io":
        return f"https://{usuario.lower()}.github.io", ""
    return f"https://{usuario.lower()}.github.io", f"/{nombre}"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--idioma", "--language", dest="idioma", choices=list(IDIOMAS), required=True)
    p.add_argument("--nombre", "--name", dest="nombre", help="el nombre de la vitrina")
    p.add_argument("--dueno", "--owner", dest="dueno", help="quien firma las notas")
    p.add_argument("--repo", help="https://github.com/usuario/repo")
    p.add_argument("--vaciar", "--empty", dest="vaciar", action="store_true",
                   help="quita las fichas, autores, grupos y portadas de la coleccion anterior")
    p.add_argument("--si", "--yes", dest="si", action="store_true",
                   help="borra de verdad; sin esto solo dice que borraria")
    p.add_argument("--solo-vistas", "--views-only", dest="solo_vistas", action="store_true",
                   help="rehace solo las vistas y notas indice, sin tocar la configuracion")
    args = p.parse_args(argv)

    t = IDIOMAS[args.idioma]
    # Habla en el idioma que se le pide: la configuracion aun es la de antes.
    decir = lambda es, en: print(es if args.idioma == "es" else en)  # noqa: E731
    anterior = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}

    if args.vaciar:
        viejas = anterior.get("folders", {})
        borrar = [VAULT / viejas.get(k, "") for k in (*TIPOS, "author", "group") if viejas.get(k)]
        borrar += [VAULT / "assets" / "portadas"]
        borrar += list(VAULT.glob("*.base")) + [VAULT / n for n in (
            "Favoritos.md", "Favorites.md", "creditos.md", "credits.md")]
        borrar = [r for r in dict.fromkeys(borrar) if r.exists()]
        fichas = sum(len(list(r.rglob("*.md"))) for r in borrar if r.is_dir())
        if args.si:
            decir(f"Borro {fichas} notas y estas rutas:", f"Deleting {fichas} notes and these paths:")
        else:
            decir(f"Borraría {fichas} notas y estas rutas:", f"Would delete {fichas} notes and these paths:")
        for r in borrar:
            print(f"  - {r.relative_to(RAIZ)}")
        if not args.si:
            decir("\nNada borrado. Repite con --si para hacerlo.",
                  "\nNothing deleted. Run it again with --yes to do it.")
            return 0
        for r in borrar:
            shutil.rmtree(r) if r.is_dir() else r.unlink()
        (VAULT / "assets" / "portadas").mkdir(parents=True, exist_ok=True)
        (VAULT / "assets" / "portadas" / ".gitkeep").touch()

    if not args.solo_vistas:
        site, base = direccion(args.repo)
        config = {
            "name": args.nombre or anterior.get("name") or ("Vitrina" if args.idioma == "es" else "Vitrine"),
            "owner": args.dueno or anterior.get("owner", ""),
            "language": args.idioma,
            "site": site or anterior.get("site", ""),
            "base": base if base is not None else anterior.get("base", ""),
            "repo": args.repo or anterior.get("repo", ""),
            "folders": t["carpetas"],
        }
        CONFIG.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        decir(f"Escrito {CONFIG.relative_to(RAIZ)}", f"Wrote {CONFIG.relative_to(RAIZ)}")

    for ruta, texto in vistas(args.idioma).items():
        destino = VAULT / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    decir("Escritas las vistas de Obsidian y las notas índice.",
          "Wrote the Obsidian views and index notes.")

    # La entrada y los creditos solo se escriben si no hay, o si se ha vaciado:
    # la presentacion de index.md es del dueño y no se pisa.
    if args.vaciar or not (VAULT / "index.md").exists():
        (VAULT / "index.md").write_text(portada(args.idioma), encoding="utf-8")
        (VAULT / f"{t['creditos_fichero']}.md").write_text(
            nota(t["creditos"], t["creditos_texto"]), encoding="utf-8")
        decir("Escritas la entrada y los créditos: el primer párrafo de content/index.md es "
              "la presentación de la web, cámbialo.",
              "Wrote the home and credits notes: the first paragraph of content/index.md is "
              "the welcome text of the site, change it.")

    if not args.solo_vistas:
        # Lo que depende de la configuracion recien escrita se lanza aparte, para
        # que lo lea de nuevo: la plantilla del Issue y las plantillas de ficha.
        import subprocess
        aqui = Path(__file__).resolve().parent
        subprocess.run([sys.executable, str(aqui / "desde_issue.py"), "--plantilla"], check=True)
        subprocess.run([sys.executable, str(aqui / "plantillas.py")], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
