#!/usr/bin/env python3
"""Conecta las fichas que comparten estudio, direccion o artista.

Obsidian agrupa por enlaces, no por campos: dos juegos con `autor: FromSoftware`
escrito igual no estan conectados de ninguna manera. La pagina de autor si los
conecta: lista lo suyo, el grafo dibuja el haz y desde una ficha se llega a las
hermanas por los backlinks.

Lo que este script escribe son **las paginas**, no los enlaces. El campo `autor`
de la ficha se queda siempre en texto plano -- "QLOC, FromSoftware, Inc." --
porque es un dato, no maquetacion, y porque es lo que escriben tambien
`datos.py`, `nueva.py` e `importar.py`; antes esto le ponia un `[[...]]`
alrededor y los tres se pisaban en cada pasada.

El enlace lo pone la web al pintar, en `plugins/vitrina`: la cabecera de la
ficha busca dentro del texto los nombres que tengan pagina y los enlaza, y el
mismo plugin apunta esas paginas en los `links` de la ficha para que el grafo
las una. Asi una ficha con varios autores enlaza a todos los que tengan pagina
sin partir el campo por comas, que no se puede hacer a ojo: la coma separa
"Mike Johnson, Tim Burton" y no separa "FromSoftware, Inc.".

**Solo tiene pagina quien tenga dos obras o mas** (`--minimo`). Con una sola, la
pagina no agrupa nada, y son 92 autores para 90 fichas: el sitio doblaria de
tamaño en paginas muertas. Al crecer la coleccion basta con volver a pasarlo y
el que llegue a dos la estrena.

Las paginas de `content/autores/` las escribe esto entero en cada pasada, asi
que no se editan a mano.

Uso:
  scripts/autores.py             escribe las paginas de autor
  scripts/autores.py --minimo 1  una pagina por autor, tenga una obra o veinte
  scripts/autores.py --deshacer  borra las paginas de autor
  scripts/autores.py --dry-run   dice que haria, sin tocar nada
"""

import argparse
import re
import shutil
import sys
from collections import defaultdict

from vitrina import (SECCIONES, VAULT, escribir_campos, frontmatter,
                     nombre_de_fichero)

AUTORES = VAULT / "autores"

# El indice de la carpeta. Sin el, quien la fabrica es el plugin folder-page de
# Quartz, que la titula con el nombre crudo del directorio: en el arbol lateral
# salia "autores" en minuscula, entre secciones que van en mayuscula. Y de paso
# la carpeta deja de ser una lista sin explicar.
#
# Va aqui y no a mano porque main() borra la carpeta entera en cada pasada.
INDICE = """---
title: Autores
---

Quien se repite en la colección. Hay página de cada estudio, dirección, autoría
o artista con **dos obras o más**: con una sola no agruparía nada, y serían más
de cien páginas para no juntar a nadie.

No se escriben a mano. Las hace `scripts/autores.py` leyendo el campo `autor`
de las fichas, y se rehacen enteras en cada pasada.
"""

# Un `autor` enlazado de cuando el enlace vivia en el campo: "[[autores/X|X]]".
# Se sigue leyendo para poder recuperar el nombre de las fichas que aun lo
# lleven, y para que volver a pasar el script sobre una vault vieja la limpie.
ENLACE_RE = re.compile(r"\[\[autores/[^|\]]+\|([^\]]+)\]\]")

# Trozos que son el final de un nombre de empresa y no un autor aparte: sin
# esto, "FromSoftware, Inc." se parte en dos y "Inc." acaba siendo el estudio
# con mas juegos de la coleccion.
SUFIJOS = ("inc.", "inc", "ltd.", "ltd", "llc", "co.", "corp.", "gmbh",
           "s.a.", "s.l.", "b.v.", "pty", "ab", "oy")

# Nombres que llevan una coma dentro y son uno solo. Con los estudios basta la
# lista de arriba, porque lo que va detras de la coma es siempre un sufijo de
# empresa; con las personas y los grupos no hay regla que valga -- "The Creator"
# no es "Inc." --, asi que se nombran. Sin esto, "Tyler, The Creator" entraba
# como dos autores y se llevaba dos paginas, una titulada "Tyler" y otra "The
# Creator", con un disco cada una.
#
# La lista crece cuando aparezca el siguiente: "Earth, Wind & Fire" o
# "Crosby, Stills & Nash" harian lo mismo.
NOMBRES_CON_COMA = ("tyler, the creator",)


def separar(valor):
    """El campo `autor` -> la lista de personas o estudios que nombra.

    La coma no basta como separador porque significa las dos cosas:
    "Mike Johnson, Tim Burton" son dos directores y "FromSoftware, Inc." es un
    solo estudio. Lo que decide es si el trozo de despues es un sufijo de
    empresa, en cuyo caso se vuelve a pegar al anterior, o si los dos juntos
    forman un nombre de los que se sabe que llevan coma.
    """
    valor = ENLACE_RE.sub(r"\1", valor or "").strip()
    if not valor:
        return []
    partes = []
    for trozo in [t.strip() for t in valor.split(",")]:
        if not trozo:
            continue
        junto = f"{partes[-1]}, {trozo}".lower() if partes else ""
        if junto in NOMBRES_CON_COMA:
            partes[-1] += ", " + trozo
        elif partes and trozo.lower().rstrip(".") in [s.rstrip(".") for s in SUFIJOS]:
            partes[-1] += ", " + trozo
        else:
            partes.append(trozo)
    return partes


def fichas():
    for carpeta, tipo in SECCIONES.items():
        for md in sorted((VAULT / carpeta).glob("*.md")):
            if md.stem == "index":
                continue
            campos = frontmatter(md.read_text(encoding="utf-8"))
            yield md, carpeta, tipo, campos


def obras_por_autor():
    mapa = defaultdict(list)
    for md, carpeta, _, campos in fichas():
        for autor in separar(campos.get("autor")):
            mapa[autor].append((carpeta, md.stem, campos.get("year") or ""))
    return mapa


def pagina(autor, obras):
    # `seccion` cuelga la pagina de Autores, igual que una ficha cuelga de la
    # suya. El titulo no se lee del index.md de la carpeta, que main() borra
    # entera antes de rehacerla y para entonces ya no esta: aqui se sabe, es el
    # de INDICE.
    lineas = [f'---\ntitle: "{autor}"\ntipo: autor\n'
              f'seccion: "[[autores/index|Autores]]"\n---\n',
              # Sin el punto si el nombre ya acaba en uno: "FromSoftware, Inc.."
              f"Lo que tengo de {autor}{'' if autor.endswith('.') else '.'}\n"]
    for carpeta, nombre, year in sorted(obras, key=lambda o: (o[0], o[1])):
        año = f" ({year})" if year else ""
        lineas.append(f"- [[{carpeta}/{nombre}|{nombre}]]{año}")
    lineas.append("\nEsta página la escribe `scripts/autores.py`.\n")
    return "\n".join(lineas)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--minimo", type=int, default=2,
                   help="obras que hacen falta para tener pagina (por defecto 2)")
    p.add_argument("--deshacer", action="store_true",
                   help="borra las paginas de autor")
    p.add_argument("--dry-run", action="store_true", help="no escribe nada")
    args = p.parse_args()

    mapa = obras_por_autor()
    enlazables = ({} if args.deshacer
                  else {a: o for a, o in mapa.items() if len(o) >= args.minimo})

    # Las fichas: solo se les quita el `[[...]]` que dejaron las pasadas de
    # antes, cuando el enlace vivia en el campo. El nombre nunca se cambia.
    tocadas = 0
    for md, _, _, campos in fichas():
        partes = separar(campos.get("autor"))
        if not partes:
            continue
        nuevo = ", ".join(partes)
        if nuevo == (campos.get("autor") or ""):
            continue
        tocadas += 1
        if args.dry_run:
            print(f"  ·  {md.parent.name}/{md.stem}: {campos.get('autor')} -> {nuevo}")
        else:
            escribir_campos(md, {"autor": nuevo})

    if args.dry_run:
        print(f"\n  ·  {tocadas} fichas, {len(enlazables)} paginas de autor")
        return 0

    # Las paginas se reescriben enteras: son derivadas, no fuente.
    if AUTORES.exists():
        shutil.rmtree(AUTORES)
    if enlazables:
        AUTORES.mkdir(parents=True)
        (AUTORES / "index.md").write_text(INDICE, encoding="utf-8")
        for autor, obras in enlazables.items():
            destino = AUTORES / f"{nombre_de_fichero(autor)}.md"
            destino.write_text(pagina(autor, obras), encoding="utf-8")

    print(f"{len(enlazables)} páginas de autor"
          + (f", {tocadas} fichas limpiadas de enlaces viejos." if tocadas else "."))
    if not args.deshacer:
        sueltos = len(mapa) - len(enlazables)
        print(f"{sueltos} autores con menos de {args.minimo} obras se quedan "
              f"en texto, sin página.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
