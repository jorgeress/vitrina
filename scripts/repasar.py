#!/usr/bin/env python3
"""Repasa las fichas a las que les falta lo tuyo: la nota y el estado.

Es lo unico que ninguna fuente sabe, y por eso es lo que mas falta: las
fichas entran de Steam o de Letterboxd con portada, año, autor y texto, y sin
lo que pensaste de ellas. Ponerlo en Obsidian es abrir cada nota, bajar al
panel de propiedades y escribir tres campos; aqui es una linea por ficha.

  scripts/repasar.py                  las que no tienen nota o estado
  scripts/repasar.py --seccion juegos solo esa carpeta
  scripts/repasar.py --todas          todas, para cambiar lo que ya tenian

Por cada ficha se contesta con lo que quieras poner, en cualquier orden:

  8                 la nota, del 1 al 10
  p  c  t  a        pendiente, en curso, terminado, abandonado
  f  / -f           favorita / ya no
  Enter             la deja como esta y pasa a la siguiente
  q                 para aqui; lo contestado ya esta guardado

  "9 f" es un 9 y favorita. Con nota y sin estado se entiende terminado,
  que es lo que suele querer decir haberle puesto nota; "9 a" la deja como
  abandonada.

Despues, si la ficha no tiene nada escrito por ti, pide la frase del porque:
lo que se lee arriba del todo al abrirla. Enter la salta.

Cada respuesta se escribe en el momento, asi que cortarlo a medias no pierde
nada. Al terminar pone al dia el bloque de cifras del README.
"""

import argparse
import sys

import estado
import textos
from vitrina import (ESTADOS, FRONT_RE, SECCIONES, VAULT, escribir_campos, frontmatter,
                     vacio, yaml_valor)

try:
    import readline  # noqa: F401  -- solo por poder corregir la linea con las flechas
except ImportError:
    pass

# Sale al empezar, y con ? en cualquier momento. Al principio y no solo con ?
# porque es un comando de cada tantas semanas, y para entonces los atajos ya no
# se recuerdan; pedir la ayuda es saber antes que hay que pedirla.
GUIA = """\
Cómo contestar, en una línea y en cualquier orden:

  NOTA       1 … 10      la nota
  ESTADO     p           pendiente
             c           en curso
             t           terminado
             a           abandonado
  FAVORITA   f  / -f     favorita / deja de serlo

  Enter      la deja como está y pasa a la siguiente
  ?          enseña otra vez esta guía
  q          para aquí; lo contestado ya está guardado

  Ejemplos:  9 f     → nota 9, favorita y terminado
             7 a     → nota 7 y abandonado
             c       → en curso, sin nota todavía
  Con nota y sin estado se entiende terminado, salvo que ya dijera en curso
  o abandonado.

  Después, si la ficha no tiene nada tuyo escrito, te pide por qué está en
  la vitrina: lo que te dejó, bueno o malo. Va arriba del todo en la ficha,
  en su cartela. Enter la salta.
"""

ATAJOS = {"p": "pendiente", "c": "en curso", "t": "terminado", "a": "abandonado",
          "curso": "en curso"}


def interpretar(respuesta):
    """Lo que dice una respuesta, como los campos que cambia.

    Lanza ValueError con el porque si hay algo que no se entiende: antes que
    escribir media respuesta, se vuelve a preguntar.
    """
    cambios = {}
    trozos = respuesta.lower().replace("en curso", "curso").split()
    for trozo in trozos:
        if trozo.isdigit():
            if not 1 <= int(trozo) <= 10:
                raise ValueError(f"la nota va del 1 al 10, no {trozo}")
            cambios["nota"] = int(trozo)
        elif trozo in ATAJOS or trozo in ESTADOS:
            cambios["estado"] = ATAJOS.get(trozo, trozo)
        elif trozo == "f":
            cambios["favorito"] = True
        elif trozo in ("-f", "nf"):
            cambios["favorito"] = False
        else:
            raise ValueError(f"no entiendo «{trozo}»")
    return cambios


def completar(campos, cambios):
    """Los cambios, con el estado que se sobreentiende al poner nota.

    Solo cuando la ficha no dice nada o dice pendiente: una nota a lo que
    tenias por ver quiere decir que ya lo has visto. Lo que ya estaba en curso
    o abandonado se queda asi, que ahi la nota no cambia nada.
    """
    cambios = dict(cambios)
    actual = campos.get("estado")
    if ("nota" in cambios and "estado" not in cambios
            and (vacio(actual) or actual == "pendiente")):
        cambios["estado"] = "terminado"
    return cambios


def tiene_lo_suyo(md):
    texto = md.read_text(encoding="utf-8")
    return bool(textos.lo_suyo(FRONT_RE.sub("", texto, count=1)))


def pedir_frase(md):
    """La frase del porque, si la ficha no tiene ya una. Devuelve si la ha puesto.

    Se pide aqui, justo despues de la nota, porque es cuando se tiene en la
    cabeza. Suelta en Obsidian, despues, no la escribe nadie: de 210 fichas
    habia 5 con algo tuyo, y 4 eran de prueba.
    """
    if tiene_lo_suyo(md):
        return False
    try:
        frase = input("  por qué está en la vitrina (Enter para saltar): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    if not frase:
        return False
    textos.escribir_lo_suyo(md, frase)
    print("  ✓ escrito")
    return True


def pendientes(carpetas, todas):
    for carpeta in carpetas:
        for md in sorted((VAULT / carpeta).glob("*.md")):
            if md.stem == "index":
                continue
            campos = frontmatter(md.read_text(encoding="utf-8"))
            if todas or vacio(campos.get("nota")) or vacio(campos.get("estado")):
                yield carpeta, md, campos


def describir(carpeta, md, campos):
    titulo = campos.get("title") or md.stem
    año = f" ({campos['year']})" if not vacio(campos.get("year")) else ""
    autor = f" — {campos['autor']}" if not vacio(campos.get("autor")) else ""
    nota = campos.get("nota") if not vacio(campos.get("nota")) else "—"
    est = campos.get("estado") if not vacio(campos.get("estado")) else "—"
    fav = "  ★" if campos.get("favorito") == "true" else ""
    return (f"{carpeta} · {titulo}{año}{autor}\n"
            f"      nota {nota} · {est}{fav}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seccion", choices=list(SECCIONES), help="solo una carpeta")
    p.add_argument("--todas", action="store_true",
                   help="tambien las que ya tienen nota y estado")
    args = p.parse_args()

    if not sys.stdin.isatty():
        print("Esto pregunta ficha a ficha, y hace falta una terminal para contestar.")
        return 1

    carpetas = [args.seccion] if args.seccion else list(SECCIONES)
    lista = list(pendientes(carpetas, args.todas))
    if not lista:
        print("No hay ninguna sin nota ni estado.")
        return 0
    print(GUIA)
    print(f"{len(lista)} fichas por repasar.\n")

    tocadas = frases = 0
    for i, (carpeta, md, campos) in enumerate(lista, 1):
        print(f"[{i}/{len(lista)}] {describir(carpeta, md, campos)}")
        while True:
            try:
                respuesta = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                respuesta = "q"
                print()
            if respuesta == "?":
                print(GUIA)
                continue
            if respuesta.lower() == "q" or not respuesta:
                break
            try:
                cambios = completar(campos, interpretar(respuesta))
            except ValueError as e:
                print(f"  {e}. Otra vez, o ? para la ayuda.")
                continue
            escribir_campos(md, cambios)
            tocadas += 1
            print("  ✓ " + ", ".join(f"{c}: {yaml_valor(v)}" for c, v in cambios.items()))
            frases += pedir_frase(md)
            break
        if respuesta.lower() == "q":
            break
        print()

    print(f"{tocadas} ficha(s) cambiadas, {frases} con frase nueva.")
    if tocadas and estado.actualizar_readme(callado=True):
        print("Puesto al día el bloque de cifras del README.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
