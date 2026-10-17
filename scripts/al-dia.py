#!/usr/bin/env python3
"""Pone la vault al dia: todo lo que los scripts saben rellenar, en su orden.

Despues de importar, o de escribir fichas a mano, quedaban seis comandos que
habia que recordar y lanzar en orden. El orden importa: las paginas de autor
se escriben despues de datos.py, que es quien pone el autor de lo importado.

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

from idioma import opciones, ayuda
from vitrina import SECCIONES, _

SCRIPTS = Path(__file__).resolve().parent

# (script, para que, si pregunta a la red, si admite --seccion)
PASOS = [
    ("secciones.py", _("cuelga cada ficha de su sección"), False, False),
    ("fechas.py", _("apunta la fecha de alta que falte"), False, False),
    ("enmarcar.py", _("convierte en opinión lo que hayas escrito suelto"), False, False),
    ("portadas.py", _("baja las carátulas que falten"), True, True),
    ("datos.py", _("rellena año, autor y tags"), True, True),
    ("textos.py", _("escribe el «De qué va»"), True, True),
    ("enlazar.py", _("une cada ficha con Wikidata: de qué otra viene"), True, False),
    ("cuando.py", _("apunta cuándo terminaste o empezaste cada cosa"), True, False),
    ("autores.py", _("escribe las páginas de autor"), False, False),
]


def main():
    p = argparse.ArgumentParser(description=ayuda(__doc__, "al-dia"),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(*opciones("--seccion", "--section"), dest="seccion", choices=list(SECCIONES),
                   help=_("solo una carpeta"))
    p.add_argument(*opciones("--sin-red", "--offline"), dest="sin_red", action="store_true",
                   help=_("salta portadas, datos y textos"))
    p.add_argument("--dry-run", action="store_true", help=_("no escribe nada"))
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

    if fallidos:
        print("\n" + _("Han fallado: {scripts}. El resto ha terminado.").format(scripts=", ".join(fallidos)))
        return 1
    print("\n" + _("Al día. Lo que falta rellenar a mano: scripts/estado.py --detalle"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
