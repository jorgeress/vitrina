#!/usr/bin/env python3
"""Pone la vault al dia: todo lo que los scripts saben rellenar, en su orden.

Despues de importar, o de escribir fichas a mano, quedaban seis comandos que
habia que recordar y lanzar en orden. El orden importa: las paginas de autor
se escriben despues de datos.py, que es quien pone el autor de lo importado, y
las cifras del README al final, cuando ya no cambia nada mas.

  scripts/al-dia.py                  todo
  scripts/al-dia.py --seccion libros solo esa carpeta, en lo que va por carpeta
  scripts/al-dia.py --sin-red        solo lo que no pregunta a nadie
  scripts/al-dia.py --dry-run        dice que haria cada paso, sin tocar nada

Cada paso solo rellena lo que falta, asi que se puede lanzar cuando quieras:
si no hay nada que hacer, no hace nada.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from vitrina import SECCIONES

SCRIPTS = Path(__file__).resolve().parent

# (script, para que, si pregunta a la red, si admite --seccion)
PASOS = [
    ("secciones.py", "cuelga cada ficha de su sección", False, False),
    ("fechas.py", "apunta la fecha de alta que falte", False, False),
    ("enmarcar.py", "pone en su cartela lo que hayas escrito suelto", False, False),
    ("portadas.py", "baja las carátulas que falten", True, True),
    ("datos.py", "rellena año, autor y tags", True, True),
    ("textos.py", "escribe el «De qué va»", True, True),
    ("autores.py", "escribe las páginas de autor", False, False),
]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seccion", choices=list(SECCIONES), help="solo una carpeta")
    p.add_argument("--sin-red", action="store_true",
                   help="salta portadas, datos y textos")
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = p.parse_args()

    fallidos = []
    for script, que, red, por_seccion in PASOS:
        if red and args.sin_red:
            continue
        orden = [sys.executable, str(SCRIPTS / script)]
        if por_seccion and args.seccion:
            orden += ["--seccion", args.seccion]
        if args.dry_run:
            orden.append("--dry-run")
        print(f"\n── {script}: {que}", flush=True)
        # Sin capturar la salida: los que van por red tardan, y ver cada ficha
        # según sale es lo que dice que no se ha colgado.
        if subprocess.run(orden).returncode:
            fallidos.append(script)

    if not args.dry_run:
        print("\n── estado.py --readme: las cifras del README", flush=True)
        if subprocess.run([sys.executable, str(SCRIPTS / "estado.py"), "--readme"]).returncode:
            fallidos.append("estado.py")

    if fallidos:
        print(f"\nHan fallado: {', '.join(fallidos)}. El resto ha terminado.")
        return 1
    print("\nAl día. Lo que falta rellenar a mano: scripts/estado.py --detalle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
