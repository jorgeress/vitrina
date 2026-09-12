#!/usr/bin/env python3
"""Levanta el sitio con los borradores incluidos, para verlo antes de ascender.

En la web solo sale lo que has ascendido a mano: Quartz se salta todo lo que
lleve `draft: true`. Eso esta bien para publicar y fatal para decidir, porque
justo lo que quieres ver antes de ascender una tanda es como va a quedar la
galeria con ella dentro.

No toca ni `quartz.config.yaml` ni la vault. Copia el contenido fuera del repo,
le quita la linea `draft` a la copia y construye desde ahi, en su propio
puerto. Aunque se corte a medias, lo que se publica no se entera: la copia es
un callejon sin salida y no esta ni dentro del repositorio.

Uso:
  scripts/vistazo.py               levanta el sitio completo en el 8081
  scripts/vistazo.py --puerto 9000 en otro puerto
  scripts/vistazo.py --solo-build  construye y no levanta el servidor
  scripts/vistazo.py --tema rose-pine   con ese tema de Obsidian, para verlo
"""

import argparse
import contextlib
import functools
import http.server
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
from pathlib import Path

from vitrina import RAIZ, VAULT

# Fuera del repo a proposito, y no en una carpeta oculta de la raiz: el glob de
# Quartz se salta los directorios que empiezan por punto y ademas respeta el
# .gitignore, asi que una copia dentro y anotada ahi no se encontraria sola.
VISTAZO = Path(tempfile.gettempdir()) / "vitrina-vistazo"

PUERTO = 8081  # el 8080 lo usa `npx quartz build --serve`, el sitio de verdad

# Ni el estado local de Obsidian ni la papelera pintan nada en una copia.
FUERA = shutil.ignore_patterns(".obsidian", ".trash", ".git")

DRAFT_RE = re.compile(r"^draft:[ \t]*(?:true|True)[ \t]*\n", re.M)

CONFIG = RAIZ / "quartz.config.yaml"

# El bloque del plugin de temas dentro de quartz.config.yaml. Se toca solo para
# el vistazo y se deja como estaba, pase lo que pase: ver con_tema().
TEMA_RE = re.compile(r'(- source: "@quartz-themes/core"\n\s+enabled: )\w+'
                     r'(\n\s+options:\n\s+theme: )[\w-]+')


@contextlib.contextmanager
def con_tema(tema):
    """Enciende el tema en la config, y la deja como estaba al salir.

    Quartz no tiene `--config`: el tema solo se puede cambiar en el fichero de
    verdad. Asi que se toca lo justo -- mientras dura el build -- y se restaura
    en el `finally`, que salta tambien con Ctrl+C. El que se publica nunca ve
    este cambio, igual que no ve la copia de la vault.
    """
    if not tema:
        yield
        return
    # Lo que si deja rastro es package.json: el cargador de plugins se baja el
    # tema la primera vez y se apunta ahi como dependencia. Es de Quartz y no de
    # aqui, y conviene saberlo -- sale en `git status` -- para poder revertirlo
    # si el tema se queda en prueba: git checkout package.json package-lock.json
    original = CONFIG.read_text(encoding="utf-8")
    nuevo, cambios = TEMA_RE.subn(r"\1true\g<2>" + tema, original)
    if not cambios:
        print("No encuentro el bloque de @quartz-themes/core en "
              "quartz.config.yaml; se construye sin tema.")
        yield
        return
    CONFIG.write_text(nuevo, encoding="utf-8")
    try:
        yield
    finally:
        CONFIG.write_text(original, encoding="utf-8")


def servir(carpeta, puerto):
    """Un servidor de ficheros a secas sobre lo ya construido.

    Con `--tema` no se puede usar el `--serve` de Quartz: ese vuelve a leer la
    configuracion, y para entonces ya esta restaurada y el tema habria
    desaparecido. Las rutas que emite Quartz son relativas, asi que con servir
    la carpeta basta. A cambio no hay recarga automatica, que en un vistazo
    --que ya es una foto fija-- no se echa de menos.
    """
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(carpeta))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", puerto), handler) as srv:
        srv.serve_forever()

AVISO = """
> [!warning] Esto es el vistazo, no el sitio publicado
> Aquí se ven **todas** las fichas, incluidas las que siguen en borrador. La web
> de verdad solo enseña las que has ascendido. Para ascender una, quítale la
> línea `draft: true`.

"""


def copiar_sin_draft():
    if VISTAZO.exists():
        shutil.rmtree(VISTAZO)
    destino = VISTAZO / "content"
    shutil.copytree(VAULT, destino, ignore=FUERA)

    destapadas = 0
    for md in destino.rglob("*.md"):
        limpio, quitadas = DRAFT_RE.subn("", md.read_text(encoding="utf-8"))
        if quitadas:
            md.write_text(limpio, encoding="utf-8")
            destapadas += quitadas

    portada = destino / "index.md"
    if portada.exists():
        texto = portada.read_text(encoding="utf-8")
        # Debajo de la cabecera, que si no se rompe el frontmatter.
        cierre = texto.find("\n---\n", 4) if texto.startswith("---\n") else -1
        corte = cierre + len("\n---\n") if cierre != -1 else 0
        portada.write_text(texto[:corte] + AVISO + texto[corte:], encoding="utf-8")
    return destapadas


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--puerto", type=int, default=PUERTO,
                   help=f"puerto del servidor (por defecto {PUERTO})")
    p.add_argument("--solo-build", action="store_true",
                   help="construye la copia y no levanta ningún servidor")
    p.add_argument("--tema", metavar="NOMBRE",
                   help="un tema de Obsidian, p. ej. rose-pine o tokyo-night")
    args = p.parse_args()

    destapadas = copiar_sin_draft()
    print(f"Copia en {VISTAZO} con {destapadas} fichas en borrador destapadas.\n",
          flush=True)

    orden = ["npx", "quartz", "build",
             "-d", str(VISTAZO / "content"), "-o", str(VISTAZO / "public")]
    # Con tema se construye y luego se sirve aparte, porque el --serve de Quartz
    # releeria la configuracion ya restaurada. Ver servir().
    if not args.solo_build and not args.tema:
        orden += ["--serve", "--port", str(args.puerto),
                  # El de por defecto lo ocupa el servidor del sitio de verdad,
                  # asi que se pueden tener los dos abiertos a la vez.
                  "--wsPort", str(args.puerto + 920)]
        print(f"El vistazo estará en http://localhost:{args.puerto}  (Ctrl+C para salir)")
        print("Es una foto fija: si tocas una ficha, vuelve a lanzarlo.\n", flush=True)

    try:
        with con_tema(args.tema):
            codigo = subprocess.call(orden, cwd=RAIZ)
            # La primera vez que se pide un tema, el plugin se lo baja durante
            # el build y ya no puede cargarlo en esa misma pasada: falla con
            # "was installed but could not be loaded". A la segunda ya esta en
            # disco y entra. Se reintenta una vez en vez de contarselo a nadie.
            if codigo != 0 and args.tema:
                print(f"\nEl tema «{args.tema}» acaba de instalarse. "
                      "Repito el build con él ya en disco.\n", flush=True)
                codigo = subprocess.call(orden, cwd=RAIZ)
        if codigo != 0 or args.solo_build or not args.tema:
            return codigo

        print(f"\nEl vistazo, con el tema «{args.tema}», está en "
              f"http://localhost:{args.puerto}  (Ctrl+C para salir)")
        print("quartz.config.yaml se ha quedado como estaba.\n", flush=True)
        servir(VISTAZO / "public", args.puerto)
        return 0
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
