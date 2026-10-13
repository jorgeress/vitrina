#!/usr/bin/env python3
"""Añade una obra a partir de un Issue de GitHub: lo que usa la Action.

Es la forma de añadir sin terminal, desde el movil: se abre un Issue con la
plantilla "Nueva pieza", se pega el enlace y, si se quiere, la nota, el estado
y por que esta en la vitrina. La Action (.github/workflows/nueva-pieza.yml)
pasa esto, guarda la ficha, publica la web y cierra el Issue con lo que ha
hecho.

Lo que llega del Issue es texto que escribe quien lo abre, asi que no se pega
nunca en una orden: se valida campo a campo y nueva.py se llama con una lista
de argumentos, sin shell. La Action ademas solo corre con los Issues del
dueño del repo.

Uso (lo hace la Action):
  scripts/desde_issue.py evento.json   escribe la ficha y el resumen
  scripts/desde_issue.py evento.json --dry-run
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import textos
from vitrina import VAULT

AQUI = Path(__file__).resolve().parent
ESTADOS = ("pendiente", "en curso", "terminado", "abandonado")
SIN_RESPUESTA = "_No response_"


def campos_del_formulario(cuerpo):
    """El cuerpo de un Issue de formulario -> {titulo de la pregunta: respuesta}.

    GitHub lo escribe como Markdown: cada pregunta es un `### Titulo` y debajo
    va la respuesta, o `_No response_` si se dejo en blanco.
    """
    campos = {}
    for bloque in re.split(r"^### ", cuerpo or "", flags=re.M)[1:]:
        titulo, _, respuesta = bloque.partition("\n")
        respuesta = respuesta.strip()
        campos[titulo.strip()] = "" if respuesta == SIN_RESPUESTA else respuesta
    return campos


def peticion(cuerpo):
    """Lo que pide el Issue, ya comprobado. Lanza ValueError si algo no vale."""
    f = campos_del_formulario(cuerpo)
    enlace = f.get("Enlace", "").strip()
    if not re.fullmatch(r"https?://\S+", enlace):
        raise ValueError("el enlace tiene que ser una dirección web (https://...)")

    nota = f.get("Nota", "").strip()
    if nota in ("", "Sin nota"):
        nota = None
    elif not nota.isdigit() or not 1 <= int(nota) <= 10:
        raise ValueError(f"la nota tiene que ir del 1 al 10, no «{nota}»")

    estado = f.get("Estado", "").strip().lower()
    if estado in ("", "sin estado"):
        estado = None
    elif estado not in ESTADOS:
        raise ValueError(f"el estado «{estado}» no es ninguno de {', '.join(ESTADOS)}")

    favorito = bool(re.search(r"^- \[[xX]\]", f.get("Lo mejor de lo mejor", ""), flags=re.M))
    frase = f.get("Por qué está en la vitrina", "").strip()
    return {"enlace": enlace, "nota": nota, "estado": estado,
            "favorito": favorito, "frase": frase}


def argumentos(pedido):
    """La lista de argumentos de nueva.py, sin pasar por ninguna shell."""
    args = [pedido["enlace"]]
    if pedido["nota"]:
        args += ["--nota", pedido["nota"]]
    if pedido["estado"]:
        args += ["--estado", pedido["estado"]]
    if pedido["favorito"]:
        args.append("--favorito")
    return args


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("evento", help="el JSON del evento de GitHub (GITHUB_EVENT_PATH)")
    p.add_argument("--resumen", help="donde escribir el comentario para el Issue")
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = p.parse_args(argv)

    evento = json.loads(Path(args.evento).read_text(encoding="utf-8"))
    resumen = []

    def decir(texto):
        print(texto)
        resumen.append(texto)

    try:
        pedido = peticion(evento["issue"]["body"])
    except ValueError as e:
        decir(f"No he añadido nada: {e}.")
        escribir(args.resumen, resumen)
        return 1

    orden = [sys.executable, str(AQUI / "nueva.py"), *argumentos(pedido)]
    if args.dry_run:
        orden.append("--dry-run")
    salida = subprocess.run(orden, capture_output=True, text=True)
    print(salida.stdout, salida.stderr, sep="\n")

    creada = re.search(r"^Creada (\S.*\.md)$", salida.stdout, flags=re.M)
    # nueva.py avisa de dos formas de que ya estaba: por el id, que es lo
    # normal con un enlace, o por el nombre del fichero.
    ya = (re.search(r"^Esa ya la tienes: (\S.*\.md) lleva el mismo id", salida.stdout, flags=re.M)
          or re.search(r"^«(.+)» ya estaba", salida.stdout, flags=re.M))
    if salida.returncode != 0 or not (creada or ya or args.dry_run):
        ultimas = "\n".join((salida.stdout + salida.stderr).strip().splitlines()[-6:])
        decir("No he podido añadirla. Lo último que dijo nueva.py:\n\n```\n" + ultimas + "\n```")
        escribir(args.resumen, resumen)
        return 1

    if ya:
        decir(f"Ya estaba en la vitrina ({ya.group(1)}); no he tocado nada.")
    elif creada:
        md = VAULT.parent / creada.group(1)
        decir(f"Añadida: `{creada.group(1)}`.")
        detalles = [l.strip() for l in salida.stdout.splitlines() if l.startswith("  ")]
        resumen.extend(f"- {d}" for d in detalles)
        if pedido["frase"]:
            textos.escribir_lo_suyo(md, pedido["frase"])
            decir("La frase va en su cartela, «Por qué está en la vitrina».")
    else:
        decir("Prueba sin escribir nada:\n\n```\n" + salida.stdout.strip() + "\n```")
    escribir(args.resumen, resumen)
    return 0


def escribir(destino, lineas):
    if destino:
        Path(destino).write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
