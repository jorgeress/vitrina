#!/usr/bin/env python3
"""Mete en su cartela lo que hayas escrito suelto en una ficha.

Lo tuyo va en un callout propio, "Por qué está en la vitrina", encima de la
cita de la fuente: asi se ve que es tuyo, en Obsidian y en la web. Escribir el
callout a mano es incomodo, asi que no hace falta: escribes encima de la cita,
como siempre, y esto lo enmarca. No cambia ni una palabra, ni los saltos de
linea; solo pone el marco. Lo que ya esta enmarcado no lo toca.

Uso:
  scripts/enmarcar.py            enmarca lo suelto
  scripts/enmarcar.py --dry-run  dice que fichas enmarcaria
"""

import argparse
import sys

import textos
from vitrina import FRONT_RE, SECCIONES, VAULT


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = p.parse_args()

    hechas = 0
    for carpeta in SECCIONES:
        for md in sorted((VAULT / carpeta).glob("*.md")):
            if md.stem == "index":
                continue
            if args.dry_run:
                texto = md.read_text(encoding="utf-8")
                suyo = textos.lo_suyo(FRONT_RE.sub("", texto, count=1))
                if not suyo or textos.enmarcado(suyo):
                    continue
            elif not textos.enmarcar(md):
                continue
            print(f"  ▣  {carpeta}/{md.stem}")
            hechas += 1

    print(f"\n{hechas} fichas {'por enmarcar' if args.dry_run else 'enmarcadas'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
