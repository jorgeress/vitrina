#!/usr/bin/env python3
"""Añade una obra a partir de un Issue de GitHub: lo que usa la Action.

Es la forma de añadir sin terminal, desde el movil: se abre un Issue con la
plantilla "Nueva pieza" ("New piece" en una vitrina en ingles), se pega el
enlace y, si se quiere, la nota, el estado, los grupos y por que esta en la
vitrina. La Action (.github/workflows/nueva-pieza.yml) pasa esto, guarda la
ficha, publica la web y cierra el Issue con lo que ha hecho.

El formulario se define una sola vez, aqui abajo, en los dos idiomas: de ahi
sale la plantilla del Issue (`--plantilla`) y de ahi lee este script las
respuestas. Asi no pueden separarse.

Lo que llega del Issue es texto que escribe quien lo abre, asi que no se pega
nunca en una orden: se valida campo a campo y nueva.py se llama con una lista
de argumentos, sin shell. La Action ademas solo corre con los Issues del
dueño del repo.

Uso (lo hace la Action):
  scripts/desde_issue.py evento.json --resumen r.md --commit c.txt
  scripts/desde_issue.py evento.json --dry-run
  scripts/desde_issue.py --plantilla     reescribe la plantilla del Issue
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import idioma
import textos
from idioma import _
from vitrina import ESTADOS, IDIOMA, RAIZ, VAULT, estado_de

AQUI = Path(__file__).resolve().parent
SIN_RESPUESTA = "_No response_"
PLANTILLAS = RAIZ / ".github" / "ISSUE_TEMPLATE"

# El formulario, en cada idioma. Las claves de `campos` son las de siempre;
# lo que cambia es como se rotula cada pregunta, que es lo que GitHub escribe
# en el cuerpo del Issue y por lo que se lee.
FORMULARIOS = {
    "es": {
        "fichero": "nueva-pieza.yml",
        "nombre": "Nueva pieza",
        "descripcion": "Añade una obra a la vitrina con su enlace. Se guarda y se publica sola.",
        "etiqueta": "nueva-pieza",
        "campos": {
            "enlace": "Enlace",
            "nota": "Nota",
            "estado": "Estado",
            "favorito": "Lo mejor de lo mejor",
            "grupos": "Grupos",
            "terminada": "Cuándo la terminaste",
            "frase": "Por qué está en la vitrina",
            "oculta": "Oculta",
        },
        "enlace_ayuda": ("De Steam, Letterboxd, IMDb, TMDB, FilmAffinity, TVmaze, MyAnimeList, "
                         "AniList, Goodreads, Open Library, Spotify, Apple Music, MusicBrainz, "
                         "Discogs, Wikipedia... El que tengas abierto."),
        "sin_nota": "Sin nota",
        "sin_estado": "Sin estado",
        "estados": {"terminado": "finished", "en curso": "in-progress",
                    "pendiente": "pending", "abandonado": "dropped"},
        "favorito_opcion": "Es de lo mejor de lo mejor",
        "oculta_opcion": "No sale en la web (el fichero sí está en el repo, que es público)",
        "grupos_ayuda": "Separados por comas. Si el grupo no existe, se crea solo.",
        "terminada_ayuda": "AAAA, AAAA-MM o AAAA-MM-DD. Es lo que la pone en el anuario.",
        "frase_ayuda": "Lo que te dejó. Va en su cartela, encima de lo que diga la fuente.",
        "commit": "Entra en la vitrina {titulo}",
        "commit_cuerpo": "Desde el Issue #{numero}.",
    },
    "en": {
        "fichero": "new-piece.yml",
        "nombre": "New piece",
        "descripcion": "Add a work to the display from its link. It is saved and published on its own.",
        "etiqueta": "new-piece",
        "campos": {
            "enlace": "Link",
            "nota": "Rating",
            "estado": "Status",
            "favorito": "The best of the best",
            "grupos": "Groups",
            "terminada": "When you finished it",
            "frase": "Why it's on display",
            "oculta": "Hidden",
        },
        "enlace_ayuda": ("From Steam, Letterboxd, IMDb, TMDB, TVmaze, MyAnimeList, AniList, "
                         "Goodreads, Open Library, Spotify, Apple Music, MusicBrainz, Discogs, "
                         "Wikipedia... Whichever you have open."),
        "sin_nota": "No rating",
        "sin_estado": "No status",
        "estados": {"finished": "finished", "in progress": "in-progress",
                    "pending": "pending", "dropped": "dropped"},
        "favorito_opcion": "It's among the best of the best",
        "oculta_opcion": "Don't show it on the site (the file is still in the repo, which is public)",
        "grupos_ayuda": "Comma separated. A group that doesn't exist yet is created on its own.",
        "terminada_ayuda": "YYYY, YYYY-MM or YYYY-MM-DD. It's what places it in the yearbook.",
        "frase_ayuda": "What it left you. It goes in its label, above what the source says.",
        "commit": "{titulo} joins the display",
        "commit_cuerpo": "From Issue #{numero}.",
    },
}
FORMULARIO = FORMULARIOS.get(IDIOMA, FORMULARIOS["en"])


def plantilla(f=FORMULARIO):
    """La plantilla del Issue en YAML, escrita a mano para que se lea bien."""
    c = f["campos"]
    q = lambda s: json.dumps(s, ensure_ascii=False)  # noqa: E731
    estados = ", ".join(q(e) for e in [f["sin_estado"], *f["estados"]])
    notas = ", ".join(q(n) for n in [f["sin_nota"], *map(str, range(10, 0, -1))])
    return f"""# La escribe scripts/desde_issue.py --plantilla: no se toca a mano.
name: {q(f["nombre"])}
description: {q(f["descripcion"])}
title: {q(f["nombre"])}
labels: [{q(f["etiqueta"])}]
body:
  - type: input
    id: enlace
    attributes:
      label: {q(c["enlace"])}
      description: {q(f["enlace_ayuda"])}
      placeholder: https://letterboxd.com/film/parasite-2019/
    validations:
      required: true
  - type: dropdown
    id: nota
    attributes:
      label: {q(c["nota"])}
      options: [{notas}]
      default: 0
  - type: dropdown
    id: estado
    attributes:
      label: {q(c["estado"])}
      options: [{estados}]
      default: 0
  - type: checkboxes
    id: favorito
    attributes:
      label: {q(c["favorito"])}
      options:
        - label: {q(f["favorito_opcion"])}
  - type: input
    id: grupos
    attributes:
      label: {q(c["grupos"])}
      description: {q(f["grupos_ayuda"])}
  - type: input
    id: terminada
    attributes:
      label: {q(c["terminada"])}
      description: {q(f["terminada_ayuda"])}
  - type: textarea
    id: frase
    attributes:
      label: {q(c["frase"])}
      description: {q(f["frase_ayuda"])}
  - type: checkboxes
    id: oculta
    attributes:
      label: {q(c["oculta"])}
      options:
        - label: {q(f["oculta_opcion"])}
"""


def campos_del_formulario(cuerpo):
    """El cuerpo de un Issue de formulario -> {titulo de la pregunta: respuesta}.

    GitHub lo escribe como Markdown: cada pregunta es un `### Titulo` y debajo
    va la respuesta, o `_No response_` si se dejo en blanco.
    """
    campos = {}
    for bloque in re.split(r"^### ", cuerpo or "", flags=re.M)[1:]:
        titulo, _sep, respuesta = bloque.partition("\n")
        respuesta = respuesta.strip()
        campos[titulo.strip()] = "" if respuesta == SIN_RESPUESTA else respuesta
    return campos


def formulario_de(respuestas):
    """El formulario con el que se escribio el Issue, por sus preguntas.

    Se mira el de la vitrina primero, pero se aceptan los dos: una plantilla
    vieja abierta en el movil no tiene por que coincidir con la de hoy.
    """
    for f in (FORMULARIO, *FORMULARIOS.values()):
        if f["campos"]["enlace"] in respuestas:
            return f
    return FORMULARIO


def marcada(respuesta):
    return bool(re.search(r"^- \[[xX]\]", respuesta or "", flags=re.M))


def peticion(cuerpo):
    """Lo que pide el Issue, ya comprobado. Lanza ValueError si algo no vale."""
    respuestas = campos_del_formulario(cuerpo)
    f = formulario_de(respuestas)
    leer = lambda clave: respuestas.get(f["campos"][clave], "").strip()  # noqa: E731

    enlace = leer("enlace")
    if not re.fullmatch(r"https?://\S+", enlace):
        raise ValueError(_("el enlace tiene que ser una dirección web (https://...)"))

    nota = leer("nota")
    if nota in ("", f["sin_nota"]):
        nota = None
    elif not nota.isdigit() or not 1 <= int(nota) <= 10:
        raise ValueError(_("la nota tiene que ir del 1 al 10, no «{nota}»").format(nota=nota))

    estado = leer("estado").lower()
    if estado in ("", f["sin_estado"].lower()):
        estado = None
    elif f["estados"].get(estado) or estado_de(estado) in ESTADOS:
        estado = f["estados"].get(estado) or estado_de(estado)
    else:
        raise ValueError(_("el estado «{estado}» no es ninguno de {estados}").format(
            estado=estado, estados=", ".join(f["estados"])))

    # Los grupos son nombres escritos a mano: se rechaza lo que no pueda ser
    # un nombre de grupo o parezca una opcion de nueva.py.
    grupos = [g.strip() for g in leer("grupos").split(",") if g.strip()]
    for g in grupos:
        if g.startswith("-") or not re.fullmatch(r"[\w .'&()+-]{1,60}", g):
            raise ValueError(_("el grupo «{grupo}» lleva caracteres que no valen").format(grupo=g))

    terminada = leer("terminada")
    if terminada and not re.fullmatch(r"\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?", terminada):
        raise ValueError(_("la fecha «{fecha}» no es AAAA, AAAA-MM ni AAAA-MM-DD").format(fecha=terminada))

    return {"enlace": enlace, "rating": nota, "status": estado,
            "favorite": marcada(leer("favorito")), "hidden": marcada(leer("oculta")),
            "groups": grupos, "finished_on": terminada or None, "frase": leer("frase")}


def argumentos(pedido):
    """La lista de argumentos de nueva.py, sin pasar por ninguna shell."""
    args = [pedido["enlace"]]
    if pedido["rating"]:
        args += ["--nota", pedido["rating"]]
    if pedido["status"]:
        args += ["--estado", pedido["status"]]
    if pedido["favorite"]:
        args.append("--favorito")
    if pedido.get("hidden"):
        args.append("--oculta")
    for grupo in pedido.get("groups") or []:
        args += ["--grupo", grupo]
    if pedido.get("finished_on"):
        args += ["--terminada", pedido["finished_on"]]
    return args


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("evento", nargs="?", help="el JSON del evento de GitHub (GITHUB_EVENT_PATH)")
    p.add_argument("--resumen", help="donde escribir el comentario para el Issue")
    p.add_argument("--commit", help="donde escribir el mensaje del commit")
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    p.add_argument("--plantilla", action="store_true",
                   help="escribe la plantilla del Issue en el idioma de la vitrina")
    args = p.parse_args(argv)

    if args.plantilla:
        # Una sola plantilla, la del idioma de la vitrina: la otra se quita,
        # que si no salen las dos al abrir un Issue.
        for f in FORMULARIOS.values():
            (PLANTILLAS / f["fichero"]).unlink(missing_ok=True)
        PLANTILLAS.mkdir(parents=True, exist_ok=True)
        (PLANTILLAS / FORMULARIO["fichero"]).write_text(plantilla(), encoding="utf-8")
        print(PLANTILLAS / FORMULARIO["fichero"])
        return 0
    if not args.evento:
        p.error(_("falta el JSON del evento"))

    evento = json.loads(Path(args.evento).read_text(encoding="utf-8"))
    resumen = []

    def decir(texto):
        print(texto)
        resumen.append(texto)

    try:
        pedido = peticion(evento["issue"]["body"])
    except ValueError as e:
        decir(_("No he añadido nada: {porque}.").format(porque=e))
        escribir(args.resumen, resumen)
        return 1

    # nueva.py deja lo que ha hecho en un informe en JSON: asi no hace falta
    # leer sus mensajes, que salen en el idioma de la vitrina.
    with tempfile.TemporaryDirectory() as tmp:
        ruta_informe = Path(tmp) / "informe.json"
        orden = [sys.executable, str(AQUI / "nueva.py"), *argumentos(pedido),
                 "--informe", str(ruta_informe)]
        if args.dry_run:
            orden.append("--dry-run")
        salida = subprocess.run(orden, capture_output=True, text=True)
        print(salida.stdout, salida.stderr, sep="\n")
        informe = (json.loads(ruta_informe.read_text(encoding="utf-8"))
                   if ruta_informe.exists() else {})

    creada, ya = informe.get("creada"), informe.get("ya_estaba")
    if salida.returncode != 0 or not (creada or ya or args.dry_run):
        ultimas = "\n".join((salida.stdout + salida.stderr).strip().splitlines()[-6:])
        decir(_("No he podido añadirla. Lo último que dijo nueva.py:") + "\n\n```\n" + ultimas + "\n```")
        escribir(args.resumen, resumen)
        return 1

    if ya:
        decir(_("Ya estaba en la vitrina ({ruta}); no he tocado nada.").format(ruta=ya))
    elif creada:
        md = VAULT.parent / creada
        decir(_("Añadida: `{ruta}`.").format(ruta=creada))
        resumen.extend(f"- {d}" for d in informe.get("detalles", []))
        if pedido["frase"]:
            textos.escribir_lo_suyo(md, pedido["frase"])
            decir(_("La frase va en su cartela, «{titulo}».").format(titulo=idioma.texto("cartela")))
        escribir(args.commit, [FORMULARIO["commit"].format(titulo=md.stem), "",
                               FORMULARIO["commit_cuerpo"].format(
                                   numero=evento["issue"].get("number", "?"))])
    else:
        decir(_("Prueba sin escribir nada:") + "\n\n```\n" + salida.stdout.strip() + "\n```")
    escribir(args.resumen, resumen)
    return 0


def escribir(destino, lineas):
    if destino:
        Path(destino).write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
