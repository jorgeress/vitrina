#!/usr/bin/env python3
"""Conecta las fichas que comparten estudio, direccion o artista.

Obsidian agrupa por enlaces, no por campos: dos juegos con `author: FromSoftware`
escrito igual no estan conectados de ninguna manera. La pagina de autor si los
conecta: lista lo suyo, el grafo dibuja el haz y desde una ficha se llega a las
hermanas por los backlinks.

Lo que este script escribe son **las paginas**, no los enlaces. El campo `author`
de la ficha se queda siempre en texto plano -- "QLOC, FromSoftware, Inc." --
porque es un dato, no maquetacion, y porque es lo que escriben tambien
`datos.py`, `nueva.py` e `importar.py`; antes esto le ponia un `[[...]]`
alrededor y los tres se pisaban en cada pasada.

El enlace lo pone la web al pintar: parte el campo con la misma regla que
`separar()` de aqui (web/src/lib/texto.ts, y una prueba comprueba que dan lo
mismo) y enlaza cada nombre a su pagina, cuya direccion sale del nombre de
fichero que le da este script. Partirlo no se puede hacer a ojo: la coma separa
"Mike Johnson, Tim Burton" y no separa "FromSoftware, Inc.".

**Solo tiene pagina quien tenga dos obras o mas** (`--minimo`). Con una sola, la
pagina no agrupa nada, y son 152 autores para 155 fichas: el sitio doblaria de
tamaño en paginas muertas. Al crecer la coleccion basta con volver a pasarlo y
el que llegue a dos la estrena.

Las paginas de `content/autores/` las escribe esto entero en cada pasada, asi
que no se editan a mano.

Uso:
  scripts/autores.py             escribe las paginas de autor
  scripts/autores.py --minimo 1  una pagina por autor, tenga una obra o veinte
  scripts/autores.py --deshacer  borra las paginas de autor
  scripts/autores.py --dry-run   dice que haria, sin tocar nada
"""

import argparse
import re
import shutil
import sys
from collections import defaultdict

from idioma import ayuda, texto
from vitrina import (CARPETAS, _, fichas as de_la_seccion, SECCIONES, VAULT, escribir_campos,
                     frontmatter, nombre_de_fichero)

CARPETA = CARPETAS.get("author", "authors")
AUTORES = VAULT / CARPETA

# El indice de la carpeta, que es solo el titulo: es a donde lleva el enlace
# "Autores" de content/index.md en Obsidian. La web no lo lee; su pagina de
# autores la hace ella con la lista de nombres.
#
# Va aqui y no a mano porque main() borra la carpeta entera en cada pasada.
INDICE = f"""---
title: {texto('autores')}
---
"""

# Un `author` enlazado de cuando el enlace vivia en el campo: "[[autores/X|X]]".
# Se sigue leyendo para poder recuperar el nombre de las fichas que aun lo
# lleven, y para que volver a pasar el script sobre una vault vieja la limpie.
ENLACE_RE = re.compile(r"\[\[" + re.escape(CARPETA) + r"/[^|\]]+\|([^\]]+)\]\]")

# Trozos que son el final de un nombre de empresa y no un autor aparte: sin
# esto, "FromSoftware, Inc." se parte en dos y "Inc." acaba siendo el estudio
# con mas juegos de la coleccion.
SUFIJOS = ("inc.", "inc", "ltd.", "ltd", "llc", "co.", "corp.", "gmbh",
           "s.a.", "s.l.", "b.v.", "pty", "ab", "oy")

# Nombres que llevan una coma dentro y son uno solo. Con los estudios basta la
# lista de arriba, porque lo que va detras de la coma es siempre un sufijo de
# empresa; con las personas y los grupos no hay regla que valga -- "The Creator"
# no es "Inc." --, asi que se nombran. Sin esto, "Tyler, The Creator" entraba
# como dos autores y se llevaba dos paginas, una titulada "Tyler" y otra "The
# Creator", con un disco cada una.
#
# La lista crece cuando aparezca el siguiente: "Earth, Wind & Fire" o
# "Crosby, Stills & Nash" harian lo mismo.
NOMBRES_CON_COMA = ("tyler, the creator",)


def separar(valor):
    """El campo `author` -> la lista de personas o estudios que nombra.

    La coma no basta como separador porque significa las dos cosas:
    "Mike Johnson, Tim Burton" son dos directores y "FromSoftware, Inc." es un
    solo estudio. Lo que decide es si el trozo de despues es un sufijo de
    empresa, en cuyo caso se vuelve a pegar al anterior, o si los dos juntos
    forman un nombre de los que se sabe que llevan coma.
    """
    valor = ENLACE_RE.sub(r"\1", valor or "").strip()
    if not valor:
        return []
    partes = []
    for trozo in [t.strip() for t in valor.split(",")]:
        if not trozo:
            continue
        junto = f"{partes[-1]}, {trozo}".lower() if partes else ""
        if junto in NOMBRES_CON_COMA:
            partes[-1] += ", " + trozo
        elif partes and trozo.lower().rstrip(".") in [s.rstrip(".") for s in SUFIJOS]:
            partes[-1] += ", " + trozo
        else:
            partes.append(trozo)
    return partes


def fichas():
    for carpeta, tipo in SECCIONES.items():
        for md in de_la_seccion(carpeta, privadas=False):
            if md.stem == "index":
                continue
            campos = frontmatter(md.read_text(encoding="utf-8"))
            yield md, carpeta, tipo, campos


def obras_por_autor():
    mapa = defaultdict(list)
    for md, carpeta, _texto, campos in fichas():
        for autor in separar(campos.get("author")):
            mapa[autor].append((carpeta, md.stem, campos.get("year") or ""))
    return mapa


def pagina(autor, obras):
    # `section` cuelga la pagina de Autores, igual que una ficha cuelga de la
    # suya. El titulo no se lee del index.md de la carpeta, que main() borra
    # entera antes de rehacerla y para entonces ya no esta: aqui se sabe, es el
    # de INDICE.
    lineas = [f'---\ntitle: "{autor}"\ntype: author\n'
              f'section: "[[{CARPETA}/index|{texto("autores")}]]"\n---\n',
              # Sin el punto si el nombre ya acaba en uno: "FromSoftware, Inc.."
              texto("lo_que_tengo", autor=autor) + ("" if autor.endswith(".") else ".") + "\n"]
    for carpeta, nombre, year in sorted(obras, key=lambda o: (o[0], o[1])):
        año = f" ({year})" if year else ""
        lineas.append(f"- [[{carpeta}/{nombre}|{nombre}]]{año}")
    lineas.append("\n" + texto("la_escribe") + "\n")
    return "\n".join(lineas)


def main(argv=None):
    p = argparse.ArgumentParser(description=ayuda(__doc__, "autores"),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--minimo", type=int, default=2,
                   help=_("obras que hacen falta para tener pagina (por defecto 2)"))
    p.add_argument("--deshacer", action="store_true",
                   help=_("borra las paginas de autor"))
    p.add_argument("--dry-run", action="store_true", help=_("no escribe nada"))
    args = p.parse_args(argv)

    mapa = obras_por_autor()
    enlazables = ({} if args.deshacer
                  else {a: o for a, o in mapa.items() if len(o) >= args.minimo})

    # Las fichas: solo se les quita el `[[...]]` que dejaron las pasadas de
    # antes, cuando el enlace vivia en el campo. El nombre nunca se cambia.
    tocadas = 0
    for md, _carpeta, _texto, campos in fichas():
        partes = separar(campos.get("author"))
        if not partes:
            continue
        nuevo = ", ".join(partes)
        if nuevo == (campos.get("author") or ""):
            continue
        tocadas += 1
        if args.dry_run:
            print(f"  ·  {md.parent.name}/{md.stem}: {campos.get('author')} -> {nuevo}")
        else:
            escribir_campos(md, {"author": nuevo})

    if args.dry_run:
        print("\n  ·  " + _("{fichas} fichas, {paginas} paginas de autor").format(
            fichas=tocadas, paginas=len(enlazables)))
        return 0

    # Las paginas se reescriben enteras: son derivadas, no fuente.
    if AUTORES.exists():
        shutil.rmtree(AUTORES)
    if enlazables:
        AUTORES.mkdir(parents=True)
        (AUTORES / "index.md").write_text(INDICE, encoding="utf-8")
        for autor, obras in enlazables.items():
            destino = AUTORES / f"{nombre_de_fichero(autor)}.md"
            destino.write_text(pagina(autor, obras), encoding="utf-8")

    print(_("{n} páginas de autor").format(n=len(enlazables))
          + (_(", {n} fichas limpiadas de enlaces viejos.").format(n=tocadas) if tocadas else "."))
    if not args.deshacer:
        sueltos = len(mapa) - len(enlazables)
        print(_("{n} autores con menos de {minimo} obras se quedan en texto, sin página.").format(
            n=sueltos, minimo=args.minimo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
