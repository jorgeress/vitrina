#!/usr/bin/env python3
"""Cuelga cada ficha de su seccion: escribe el campo `seccion`.

El grafo de Obsidian dibuja los `[[...]]` de la vault y nada mas. Una ficha no
cita a ninguna otra, y la galeria de su seccion tampoco la cita a ella --el
`![[Juegos.base]]` de /juegos/ no es una lista de enlaces, es una pregunta que
se resuelve al pintar--, asi que las fichas salian sueltas: Vitrina y sus cinco
secciones por un lado y las fichas por otro, unidas solo por las etiquetas.

Este campo es la arista que faltaba. `[[juegos/index|Juegos]]` en la cabecera de
cada juego, y con eso Hollow Knight cuelga de Juegos y Juegos de Vitrina, en
Obsidian igual que en la web.

Va en la cabecera y no en el cuerpo porque es un dato --de que seccion es la
ficha-- y no maquetacion, que es el reparto de toda la vault; Obsidian cuenta
los enlaces de las propiedades igual que los del texto, y en la web no se pinta.
No hay que pasarlo despues de cada alta: `nueva.py` e `importar.py` lo escriben
al crear la ficha. Esto es para las que ya estaban, para una escrita a mano y
para una que cambie de carpeta.

Uso:
  scripts/secciones.py            escribe el campo en las que falte o este mal
  scripts/secciones.py --dry-run  dice que haria, sin tocar nada
  scripts/secciones.py --deshacer quita el campo de todas las fichas
"""

import argparse
import re
import sys

from vitrina import (SECCIONES, VAULT, enlace_seccion, escribir_campos,
                     frontmatter, linea_yaml)

# La clave y su valor, con el salto de linea de delante: asi al quitarla no
# queda una linea en blanco dentro de la cabecera.
CAMPO_RE = re.compile(r"\n?^seccion:.*$", re.M)

# Detras de `tipo`, que es el campo con el que va de la mano, y no al final de
# la cabecera, que es donde lo dejaria escribir_campos: es el orden en el que lo
# escriben las fichas nuevas, y el que Obsidian enseña en sus propiedades.
TIPO_RE = re.compile(r"^tipo:.*$", re.M)


def colgar(md, texto, linea):
    """Escribe la clave debajo de `tipo`. Devuelve False si no encaja."""
    m = TIPO_RE.search(texto)
    if not m:
        return False
    md.write_text(texto[:m.end()] + "\n" + linea + texto[m.end():], encoding="utf-8")
    return True


def fichas():
    for carpeta in SECCIONES:
        for md in sorted((VAULT / carpeta).glob("*.md")):
            if md.stem != "index":
                yield carpeta, md


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--deshacer", action="store_true", help="quita el campo")
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = p.parse_args()

    tocadas = 0
    for carpeta, md in fichas():
        texto = md.read_text(encoding="utf-8")
        actual = frontmatter(texto).get("seccion")
        if args.deshacer:
            if actual is None:
                continue
            if not args.dry_run:
                md.write_text(CAMPO_RE.sub("", texto, count=1), encoding="utf-8")
            print(f"- {md.relative_to(VAULT)}")
        else:
            debido = enlace_seccion(carpeta)
            if actual == debido:
                continue
            if not args.dry_run:
                linea = linea_yaml("seccion", debido)
                # Con la clave ya puesta se cambia donde este; si no la hay, se
                # abre hueco debajo de `tipo`, y solo si falla se va al final.
                if actual is not None or not colgar(md, texto, linea):
                    escribir_campos(md, {"seccion": debido})
            print(f"{'~' if actual else '+'} {md.relative_to(VAULT)}  {debido}")
        tocadas += 1

    verbo = "quitaria" if args.deshacer else "escribiria"
    if args.dry_run:
        print(f"\n{verbo} el campo en {tocadas} fichas")
    else:
        print(f"\n{tocadas} fichas" + (" sin campo" if args.deshacer else " colgadas"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
