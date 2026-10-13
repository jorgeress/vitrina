#!/usr/bin/env python3
"""Levanta la web con los borradores incluidos, para verlo antes de publicar.

En la web solo sale lo publicado: se salta todo lo que lleve `draft: true`.
Eso esta bien para publicar y fatal para decidir, porque justo lo que quieres
ver antes de publicar una tanda importada es como queda la sala con ella
dentro.

No toca la vault ni copia nada: construye la web de web/ con la variable
VITRINA_BORRADORES=1, que hace que entren tambien los borradores, marcados
como tales y con un aviso arriba, y la sirve en su propio puerto. Construye en
vez de usar `astro dev` porque Astro solo deja uno por proyecto, y el de la web
de verdad puede estar abierto. Es una foto fija: si tocas una ficha, vuelve a
lanzarlo.

Uso:
  scripts/vistazo.py               en http://localhost:8081/vitrina/
  scripts/vistazo.py --puerto 9000 en otro puerto
  scripts/vistazo.py --solo-build  construye en web/vistazo/ y no sirve
"""

import argparse
import functools
import http.server
import os
import socketserver
import subprocess
import sys

from vitrina import RAIZ

WEB = RAIZ / "web"
PUERTO = 8081  # el 4321 lo usa `npm run dev`, la web de verdad
# Dentro de web/ y no en /tmp: Astro mueve los ficheros con rename, que no
# cruza de un disco a otro, y /tmp suele ser otro. Esta en el .gitignore.
SALIDA = WEB / "vistazo"


def servir(carpeta, puerto):
    """Lo construido, en /vitrina/ como en la web publicada."""

    class Manejador(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, ruta):
            ruta = ruta.removeprefix("/vitrina") or "/"
            return super().translate_path(ruta)

    socketserver.TCPServer.allow_reuse_address = True
    manejador = functools.partial(Manejador, directory=str(carpeta))
    with socketserver.TCPServer(("", puerto), manejador) as srv:
        srv.serve_forever()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--puerto", type=int, default=PUERTO,
                   help=f"puerto del servidor (por defecto {PUERTO})")
    p.add_argument("--solo-build", action="store_true",
                   help="construye en web/vistazo/ y no levanta nada")
    args = p.parse_args()

    if not (WEB / "node_modules").exists():
        print("Falta instalar la web: cd web && npm ci --ignore-scripts --include=optional")
        return 1
    entorno = {**os.environ, "VITRINA_BORRADORES": "1", "ASTRO_TELEMETRY_DISABLED": "1"}

    # A otra carpeta, para no dejar en web/dist una web con borradores que se
    # pudiera publicar por error.
    codigo = subprocess.call(["npx", "astro", "build", "--outDir", str(SALIDA)], cwd=WEB, env=entorno)
    if codigo != 0 or args.solo_build:
        return codigo
    print(f"\nEl vistazo está en http://localhost:{args.puerto}/vitrina/  (Ctrl+C para salir)", flush=True)
    try:
        servir(SALIDA, args.puerto)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
