#!/usr/bin/env python3
"""Apunta en cada ficha cuando entro en la coleccion: el campo `alta`.

De ahi sale "Ultimas añadidas" en la portada. La fecha va escrita en la ficha y
no se saca del fichero porque la del fichero no sobrevive a un `git clone`,
que las deja todas con la hora del clon, y Obsidian y la web acabarian
ordenando distinto.

Las fichas nuevas ya nacen con ella: la pone `escribir_ficha`. Esto es para las
que ya estaban y para las escritas a mano, y saca la fecha del commit en el que
entro cada una, siguiendo los renombres. Una que todavia no esta en git entra
con la de hoy. Nunca cambia una fecha que ya este puesta.

Uso:
  scripts/fechas.py            la escribe en las que no la tienen
  scripts/fechas.py --dry-run  dice que pondria, sin tocar nada
"""

import argparse
import subprocess
import sys
from datetime import date

from vitrina import RAIZ, SECCIONES, VAULT, escribir_campos, frontmatter, vacio


def alta_en_git(md):
    """La fecha del commit que añadio la ficha, o None si git no la conoce."""
    salida = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%as", "--", str(md)],
        cwd=RAIZ, capture_output=True, text=True).stdout.split()
    # --follow recorre los renombres hacia atras: la ultima linea es la mas
    # antigua, o sea la de cuando entro por primera vez con cualquier nombre.
    return salida[-1] if salida else None


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = p.parse_args()

    hoy = date.today().isoformat()
    puestas = 0
    for carpeta in SECCIONES:
        for md in sorted((VAULT / carpeta).glob("*.md")):
            if md.stem == "index":
                continue
            if not vacio(frontmatter(md.read_text(encoding="utf-8")).get("alta")):
                continue
            fecha = alta_en_git(md) or hoy
            if not args.dry_run:
                escribir_campos(md, {"alta": fecha})
            print(f"  {fecha}  {carpeta}/{md.stem}")
            puestas += 1

    print(f"\n{puestas} fichas {'sin fecha' if args.dry_run else 'fechadas'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
