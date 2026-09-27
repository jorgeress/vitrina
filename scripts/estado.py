#!/usr/bin/env python3
"""Cómo va Vitrina: qué hay, qué falta y qué se publica.

Las galerias enseñan lo que hay. Esto enseña lo que **no** hay, que es lo que
hace falta para saber por donde seguir: cuantas fichas siguen en borrador, a
cuales les falta la nota o el texto, y cuantas verian de verdad los visitantes.

No consulta nada por red ni escribe nada: solo lee la vault. Se puede lanzar
tantas veces como quieras.

Uso:
  scripts/estado.py                  el resumen
  scripts/estado.py --seccion pelis  solo esa carpeta
  scripts/estado.py --detalle        ademas, que ficha le falta cada cosa
  scripts/estado.py --readme         reescribe el bloque de cifras del README
  scripts/estado.py --comprobar      avisa de lo que se ha quedado atras

El README enseña un trozo de este resumen como ejemplo. Escrito a mano se queda
viejo a la semana siguiente -- paso, y acabo diciendo 155 fichas cuando ya habia
210 --, asi que no se escribe a mano: `--readme` lo vuelve a sacar de la vault y
lo mete en su sitio. Las cifras que no pueden salir de aqui, como las de los
comentarios de los `.base`, sencillamente no se ponen.
"""

import argparse
import contextlib
import io
import os
import re
import sys
from collections import Counter, defaultdict

from vitrina import (ESTADOS, FRONT_RE, PORTADAS, RAIZ, SECCIONES, VAULT,
                     frontmatter, vacio)

# Los que hacen falta para que una ficha este completa de verdad.
CAMPOS = ("year", "autor", "nota", "portada", "tags")

# Las secciones que reparten sus dos ultimas vistas por `estado`, que desde que
# los juegos dejaron de guardar las horas son las cinco. Antes juegos no estaba:
# alli el reparto salia de las horas, y una ficha suya sin estado no le faltaba
# nada. Ahora si: un juego sin estado no sale en ninguna de las dos.
POR_ESTADO = ("juegos", "pelis", "series", "libros", "musica")

# En assets/portadas/ vive tambien el .gitkeep, que no es una caratula huerfana.
IMAGENES = {".webp", ".jpg", ".jpeg", ".png", ".gif", ".avif"}

def leer(carpeta):
    """Cada ficha de la carpeta: sus campos, si es borrador y si tiene texto."""
    for md in sorted((VAULT / carpeta).glob("*.md")):
        if md.stem == "index":
            continue
        texto = md.read_text(encoding="utf-8")
        m = FRONT_RE.match(texto)
        if not m:
            continue
        yield md, frontmatter(texto), texto[m.end():].strip()


def barra(hechas, total, ancho=24):
    if not total:
        return " " * ancho
    llenas = round(ancho * hechas / total)
    return "█" * llenas + "·" * (ancho - llenas)


# El bloque del README es este resumen recortado: las tres cosas que se leen de
# un vistazo. El reparto por estados y el recuento de notas se quedan fuera
# porque ahi ocupan media pantalla y no es lo que el README esta contando.
PARTES_README = ("FICHAS", "SIN RELLENAR", "FAVORITOS")

# El bloque de cifras del README, que es el unico cercado que empieza por FICHAS.
BLOQUE_RE = re.compile(r"(?<=```\n)FICHAS\n.*?(?=\n```)", re.S)


def bloque_readme(salida):
    """El resumen recortado a lo que el README enseña.

    De FAVORITOS solo la primera linea: el reparto por secciones que viene
    debajo es para trabajar, no para ilustrar.
    """
    bloques = {t.split("\n")[0].split("  ")[0]: t
               for t in salida.strip().split("\n\n")}
    partes = [bloques.get(nombre, "") for nombre in PARTES_README]
    if partes[-1]:
        partes[-1] = partes[-1].split("\n")[0]
    return "\n\n".join(p for p in partes if p)


def escribir_readme(salida):
    """Mete el bloque en el README. Devuelve si ha cambiado algo."""
    readme = RAIZ / "README.md"
    texto = readme.read_text(encoding="utf-8")
    if not BLOQUE_RE.search(texto):
        print("No encuentro el bloque de cifras en el README: tiene que ser un\n"
              "cercado que empiece por una linea «FICHAS».")
        return None
    nuevo = BLOQUE_RE.sub(lambda _: bloque_readme(salida), texto, count=1)
    if nuevo == texto:
        print("El README ya estaba al dia.")
        return False
    readme.write_text(nuevo, encoding="utf-8")
    print(f"Actualizado el bloque de cifras de {readme.name}.")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seccion", choices=list(SECCIONES), help="solo una carpeta")
    p.add_argument("--detalle", action="store_true",
                   help="lista las fichas a las que les falta algo")
    p.add_argument("--readme", action="store_true",
                   help="reescribe el bloque de cifras del README")
    p.add_argument("--comprobar", action="store_true",
                   help="avisa de lo que se ha quedado atras, sin tocar nada")
    args = p.parse_args()

    if args.readme:
        return 0 if actualizar_readme() is not None else 1
    if args.comprobar:
        return comprobar()
    return resumen(args)


def resumen_entero():
    """El resumen de la vault entera y sin detalle, como texto.

    Es lo que enseña el README: el resumen, no la lista de lo que le falta a
    cada ficha.
    """
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        resumen(argparse.Namespace(seccion=None, detalle=None))
    return salida.getvalue()


def actualizar_readme(callado=False):
    """Vuelve a sacar el bloque de cifras y lo mete en el README.

    Lo llaman tambien nueva.py, repasar.py e importar.py al terminar, que son
    los que cambian las cifras: asi el bloque no depende de que alguien se
    acuerde de pasar esto, que es justo lo que lo dejaba viejo.
    """
    if not callado:
        return escribir_readme(resumen_entero())
    with contextlib.redirect_stdout(io.StringIO()):
        return escribir_readme(resumen_entero())


def comprobar():
    """Lo que se ha quedado atras y no rompe nada, dicho como aviso.

    Es el paso del CI que va antes de construir. Lo que rompe el sitio --un
    estado inventado, una portada que no esta, una ficha sin seccion-- ya lo
    paran las pruebas. Esto es lo otro: lo que el build publica igual y nadie
    nota, como el README contando fichas de hace un mes. No falla, porque
    parar el despliegue por una cifra vieja seria castigar a la web por algo
    que solo se ve en GitHub; en la Action sale como aviso amarillo en el
    resumen del run.
    """
    en_action = bool(os.environ.get("GITHUB_ACTIONS"))
    avisos = []
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    actual = BLOQUE_RE.search(texto)
    if actual and actual.group(0) != bloque_readme(resumen_entero()):
        avisos.append("El bloque de cifras del README no dice lo que hay en la "
                      "vault. Pasa scripts/estado.py --readme")
    usadas = {re.sub(r"^\[\[|\]\]$", "", campos.get("portada") or "")
              for carpeta in SECCIONES for _, campos, _ in leer(carpeta)}
    sueltas = sorted(p.name for p in PORTADAS.glob("*")
                     if p.is_file() and p.suffix.lower() in IMAGENES
                     and p.name not in usadas)
    if sueltas:
        avisos.append(f"{len(sueltas)} portada(s) que ya no usa ninguna ficha: "
                      + ", ".join(sueltas[:5]) + (" …" if len(sueltas) > 5 else ""))
    sin_alta = [f"{carpeta}/{md.stem}" for carpeta in SECCIONES
                for md, campos, _ in leer(carpeta) if vacio(campos.get("alta"))]
    if sin_alta:
        # Solo las deja fuera de "Recien llegadas", que no es para parar nada.
        avisos.append(f"{len(sin_alta)} ficha(s) sin fecha de alta, que no saldran "
                      "en Recien llegadas: " + ", ".join(sin_alta[:5])
                      + (" …" if len(sin_alta) > 5 else "")
                      + ". Pasa scripts/fechas.py")
    for aviso in avisos:
        print(f"::warning::{aviso}" if en_action else f"  ! {aviso}")
    if not avisos and not en_action:
        print("Nada atrasado.")
    return 0


def resumen(args):

    carpetas = [args.seccion] if args.seccion else list(SECCIONES)
    total = Counter()
    borrador = Counter()
    con_texto = Counter()
    faltan = defaultdict(list)
    notas = Counter()
    estados = defaultdict(Counter)
    inventados = []
    favoritos = Counter()
    portadas_usadas = set()
    rotas = []

    for carpeta in carpetas:
        for md, campos, cuerpo in leer(carpeta):
            total[carpeta] += 1
            if campos.get("draft") == "true":
                borrador[carpeta] += 1
            if cuerpo:
                con_texto[carpeta] += 1
            else:
                faltan["texto"].append(f"{carpeta}/{md.stem}")
            for campo in CAMPOS:
                if vacio(campos.get(campo)):
                    faltan[campo].append(f"{carpeta}/{md.stem}")
            if campos.get("nota"):
                notas[int(campos["nota"])] += 1
            estado = campos.get("estado")
            if vacio(estado):
                estados[carpeta]["sin poner"] += 1
            elif estado in ESTADOS:
                estados[carpeta][estado] += 1
            else:
                inventados.append(f"{carpeta}/{md.stem} -> {estado}")
            if campos.get("favorito") == "true":
                favoritos[carpeta] += 1
            apuntada = re.sub(r"^\[\[|\]\]$", "", campos.get("portada") or "")
            if apuntada:
                portadas_usadas.add(apuntada)
                if not (PORTADAS / apuntada).exists():
                    rotas.append(f"{carpeta}/{md.stem} -> {apuntada}")

    hay = sum(total.values())
    if not hay:
        print("No hay ninguna ficha todavía.")
        return 0
    publicadas = hay - sum(borrador.values())

    print("FICHAS")
    print(f"  {'':10} {'total':>6} {'borrador':>9} {'publicadas':>11} {'con texto':>10}")
    for carpeta in carpetas:
        print(f"  {carpeta:10} {total[carpeta]:>6} {borrador[carpeta]:>9} "
              f"{total[carpeta] - borrador[carpeta]:>11} {con_texto[carpeta]:>10}")
    print(f"  {'':10} {'—' * 6:>6} {'—' * 9:>9} {'—' * 11:>11} {'—' * 10:>10}")
    print(f"  {'total':10} {hay:>6} {sum(borrador.values()):>9} "
          f"{publicadas:>11} {sum(con_texto.values()):>10}")

    print(f"\nEN LA WEB  {barra(publicadas, hay)}  {publicadas} de {hay}")
    if not publicadas:
        print("  Ninguna. Quartz se salta lo que lleva `draft: true`; en Obsidian se")
        print("  ven todas. Para ascender una, quítale esa línea.")

    print("\nSIN RELLENAR")
    for campo in CAMPOS + ("texto",):
        cuantas = len(faltan[campo])
        if cuantas:
            print(f"  {campo:10} {cuantas:>4}   {barra(hay - cuantas, hay)}")
            if args.detalle:
                for ficha in faltan[campo]:
                    print(f"             · {ficha}")
    if not any(faltan.values()):
        print("  Nada. Están todas completas.")

    if notas:
        print("\nNOTAS      " + "  ".join(f"{n}:{c}" for n, c in
                                          sorted(notas.items(), reverse=True)))

    # De aqui salen las dos ultimas vistas de pelis, libros y musica: lo
    # terminado en una y lo que queda -- "pendiente" y "en curso" -- en la otra.
    # Lo que no cae en ninguna de las dos solo se ve en la galeria, y eso no se
    # nota mirandola.
    print("\nESTADOS")
    columnas = ESTADOS + ["sin poner"]
    print("  " + " " * 10 + "".join(f"{c:>11}" for c in columnas))
    for carpeta in carpetas:
        print(f"  {carpeta:10}" + "".join(f"{estados[carpeta][c]:>11}"
                                          for c in columnas))
    sin_poner = sum(estados[c]["sin poner"] for c in carpetas
                    if c in POR_ESTADO)
    if sin_poner:
        print(f"  {sin_poner} ficha(s) sin estado: no salen ni en la vista de lo")
        print("  terminado ni en la lista de lo que queda.")
    if inventados:
        print(f"  {len(inventados)} ficha(s) con un estado que no existe, que es")
        print("  la otra manera de no salir en ninguna de las dos:")
        for i in inventados:
            print(f"    ✗ {i}")

    # Favoritos.base junta las cinco secciones y cada .base tiene ademas su
    # vista "Favoritos". Si aqui sale 0, esas paginas salen vacias.
    print(f"\nFAVORITOS  {barra(sum(favoritos.values()), hay)}  "
          f"{sum(favoritos.values())} de {hay}")
    for carpeta in carpetas:
        print(f"  {carpeta:10} {favoritos[carpeta]:>4}")
    if not sum(favoritos.values()):
        print("  Ninguna. Favoritos.base y las vistas «Solo favoritos» salen vacías")
        print("  hasta que alguna ficha lleve `favorito: true`.")

    # Solo con la vault entera tiene sentido: con --seccion sobran las de las otras.
    if not args.seccion:
        sueltas = sorted(p.name for p in PORTADAS.glob("*")
                         if p.is_file() and p.suffix.lower() in IMAGENES
                         and p.name not in portadas_usadas)
        if sueltas or rotas:
            print("\nPORTADAS")
            if rotas:
                print(f"  {len(rotas)} ficha(s) apuntan a una imagen que no está:")
                for r in rotas:
                    print(f"    ✗ {r}")
            if sueltas:
                print(f"  {len(sueltas)} imagen(es) que ya no usa ninguna ficha:")
                for s in sueltas if args.detalle else sueltas[:5]:
                    print(f"    · {s}")
                if not args.detalle and len(sueltas) > 5:
                    print(f"    … y {len(sueltas) - 5} más (--detalle las lista)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
