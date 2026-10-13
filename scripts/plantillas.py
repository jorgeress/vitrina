#!/usr/bin/env python3
"""Escribe las plantillas de Obsidian en el idioma de la vitrina.

Las de content/_plantillas/: la de ficha, con todos los campos explicados, y
la de grupo. En Obsidian se insertan con Ctrl+P -> «Insertar plantilla». La
carpeta no se publica: la web solo lee las de las salas.

Las claves de los campos van en ingles en los dos idiomas; lo que cambia es
la explicacion y el titulo de la cartela.
"""

import sys

from vitrina import CARPETAS, IDIOMA, VAULT, _
from idioma import CALLOUT, texto

PLANTILLAS = VAULT / "_plantillas"

FICHA = {
    "es": """---
type:
status: pending
---

Plantilla mínima: de todo lo que puede llevar una ficha, `type` es lo único
que hace falta de verdad, porque es lo que decide en qué sala sale. El resto se
añade cuando se sepa, y los scripts saben crear una clave que no existía.

Las claves van en inglés, también en una vitrina en castellano: así dos
vitrinas en idiomas distintos se pueden comparar, y las vistas de Obsidian
valen para las dos.

Campos:

- `type`: game, film, series, book o album. Debe coincidir con la carpeta.
- `status`: pending (en el almacén), in-progress, finished o dropped (retirado
  de la vitrina). Si no lo sabes, la clave no va.
- `year`: año de la obra, no el de la edición que tengas.
- `author`: estudio, dirección, autor o artista según el caso. Texto plano,
  aunque sean varios separados por comas.
- `rating`: del 1 al 10, en número. Opcional: ordena las galerías.
- `favorite`: true o false. Alimenta «Lo mejor de lo mejor».
- `cover`: enlace a una imagen de `assets/portadas/`, entre corchetes.
- `tags`: géneros, en inglés, en minúscula y sin tildes. Los rellena
  `datos.py`. El manga es un libro y el anime una serie, con su etiqueta.
- `groups`: los grupos que haces tú, en lista: `groups: [Anime y manga]`. Un
  grupo puede tener su nota en la carpeta `{grupos}/`, con un texto; si no la
  tiene, sale igual.
- `finished_on`: cuándo lo terminaste, `2024`, `2024-05` o `2024-05-03`, con
  la precisión que sepas. Es lo que lo pone en el anuario.
- `added`: cuándo entró en la vitrina. Lo ponen los scripts.
- `hidden`: `true` para que no salga en la web, o una lista de lo que no
  quieres enseñar: `hidden: [rating, label]` quita la nota y la cartela. Ojo:
  el fichero sigue en el repo, que es público. Lo que no quieras que vea nadie
  va en la carpeta `{privado}/`, que git no sube.
- `draft`: true mientras es un borrador; lo importado entra así.
- El identificador de la fuente, que lo pone el script y no se toca: `appid`
  (Steam), `letterboxd`, `tvmaze`, `mbid` (MusicBrainz) o `coverid` (Open
  Library), y `wikipedia`, el título del artículo en la Wikipedia en
  castellano cuando Wikidata no lo sabe.

El cuerpo es para lo tuyo: por qué está en la vitrina, lo que te dejó. Es lo
único que ninguna fuente puede rellenar. Va arriba, en su cartela:

> [!{callout}] {cartela}
> Lo que te dejó, en dos frases.

No hace falta escribir el marco: si escribes suelto encima de la cita,
`scripts/al-dia.py` lo mete en él sin cambiar ni una palabra.

Esta carpeta no se publica: la web solo lee las carpetas de las salas.
""",
    "en": """---
type:
status: pending
---

Minimal template: of everything an entry can have, `type` is the only thing
really needed, because it decides which room it goes in. The rest is added
when known, and the scripts can create a key that wasn't there.

Fields:

- `type`: game, film, series, book or album. Must match the folder.
- `status`: pending (in storage), in-progress, finished or dropped (off
  display). If you don't know it, leave the key out.
- `year`: the year of the work, not of the edition you have.
- `author`: studio, director, author or artist. Plain text, even when there
  are several separated by commas.
- `rating`: 1 to 10, as a number. Optional: it sorts the galleries.
- `favorite`: true or false. Feeds “The best of the best”.
- `cover`: link to an image in `assets/portadas/`, in brackets.
- `tags`: genres, lowercase, no accents. `datos.py` fills them in. Manga is a
  book and anime a series, with their tag.
- `groups`: the groups you make, as a list: `groups: [Anime]`. A group can
  have its own note in the `{grupos}/` folder, with a text; without one it
  still shows up.
- `finished_on`: when you finished it, `2024`, `2024-05` or `2024-05-03`,
  as precise as you know. It's what puts it in the yearbook.
- `added`: when it joined the display. The scripts set it.
- `hidden`: `true` to keep it off the site, or a list of what you don't want
  to show: `hidden: [rating, label]` removes the rating and the label. Mind:
  the file is still in the repo, which is public. What nobody should see goes
  in the `{privado}/` folder, which git doesn't upload.
- `draft`: true while it's a draft; imports come in like that.
- The source id, set by the script and not to be touched: `appid` (Steam),
  `letterboxd`, `tvmaze`, `mbid` (MusicBrainz) or `coverid` (Open Library),
  and `wikipedia`, the title of the article in the English Wikipedia when
  Wikidata doesn't know it.

The body is for what's yours: why it's on display, what it left you. It's the
only thing no source can fill in. It goes at the top, in its label:

> [!{callout}] {cartela}
> What it left you, in two sentences.

No need to write the frame: if you write loose text above the quote,
`scripts/al-dia.py` puts it in without changing a word.

This folder isn't published: the site only reads the room folders.
""",
}

GRUPO = {
    "es": """---
title:
featured: false
---

Un grupo es una colección que haces tú y que cruza las salas: «Anime y
manga», «Lo que me recomendó Pablo», «Verano de 2024». Esta nota va en la
carpeta `{grupos}/`, y su título es el nombre que se pone en las fichas con
`groups: [Nombre]`.

- `featured: true` lo saca en la entrada de la web, debajo de las salas.
- `hidden: true` lo quita de la web (la nota sigue en el repo).

Lo que escribas aquí debajo sale en la página del grupo.
""",
    "en": """---
title:
featured: false
---

A group is a collection you make that crosses the rooms: “Anime”, “What
Sam recommended”, “Summer 2024”. This note goes in the `{grupos}/` folder,
and its title is the name you put in entries with `groups: [Name]`.

- `featured: true` shows it on the home page, under the rooms.
- `hidden: true` keeps it off the site (the note is still in the repo).

Whatever you write below shows up on the group's page.
""",
}

LEEME = {
    "es": ("Plantillas de Obsidian: `Ficha.md` para una obra y `Grupo.md` para un\n"
           "grupo. Ctrl+P → «Insertar plantilla». Las escribe `scripts/plantillas.py`.\n\n"
           "Esta carpeta no se publica: la web solo lee las carpetas de las salas.\n"),
    "en": ("Obsidian templates: `Ficha.md` for a work and `Grupo.md` for a group.\n"
           "Ctrl+P → “Insert template”. Written by `scripts/plantillas.py`.\n\n"
           "This folder isn't published: the site only reads the room folders.\n"),
}


def escribir():
    idioma = IDIOMA if IDIOMA in FICHA else "en"
    datos = {"grupos": CARPETAS.get("group", "groups"), "privado": CARPETAS.get("private", "private"),
             "callout": CALLOUT, "cartela": texto("cartela")}
    PLANTILLAS.mkdir(parents=True, exist_ok=True)
    (PLANTILLAS / "Ficha.md").write_text(FICHA[idioma].format(**datos), encoding="utf-8")
    (PLANTILLAS / "Grupo.md").write_text(GRUPO[idioma].format(**datos), encoding="utf-8")
    (PLANTILLAS / "README.md").write_text(LEEME[idioma], encoding="utf-8")


def main():
    escribir()
    print(_("Escritas las plantillas de {carpeta}.").format(carpeta="content/_plantillas/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
