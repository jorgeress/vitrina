#!/usr/bin/env python3
"""Lo que une cada ficha con el mundo y con las demas, segun Wikidata.

Pone en la cabecera, solo donde este vacio:

  wikidata    el elemento de la obra (Q...), que es lo que permite lo demas
  based_on    las fichas de tu vitrina en las que se basa: el anime de
              Chainsaw Man, en el manga
  follows     a cual continua: Hollow Knight Silksong, a Hollow Knight

based_on y follows solo apuntan a lo que ya tienes, como enlace de Obsidian
("[[libros/Chainsaw Man]]"). La web pinta tambien el otro sentido ("Adaptada
en", "Continua en"), asi que basta con escribirlo en una de las dos.

Lo que escribas a mano no se toca nunca, y se puede poner lo mismo sin el
script, como una banda sonora con `soundtrack: ["[[musica/Disco]]"]`, que
Wikidata casi nunca sabe.

Antes ponia tambien el trailer de YouTube y el disco de Spotify para un
reproductor en la ficha. Se quito el 17 de octubre de 2026: incrustar otros
sitios cargaba la pagina con lo que no es de la vitrina. Esta entero en la
rama borrador/reproductor.

  scripts/enlazar.py                    todas las fichas
  scripts/enlazar.py content/pelis/Clue.md
  scripts/enlazar.py --dry-run          dice que pondria, sin tocar nada

Wikidata no pide clave.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

from idioma import ayuda
from vitrina import _, fichas, frontmatter, escribir_campos, pedir, vacio, IDIOMA, SECCIONES, VAULT

# Cada id de fuente que guarda una ficha, y la propiedad de Wikidata que lo
# lleva. Los libros no tienen: se encuentran por su articulo de Wikipedia.
PROPIEDADES = {"appid": "P1733", "letterboxd": "P6127", "tvmaze": "P8600", "mbid": "P436"}
SPARQL = "https://query.wikidata.org/sparql"
# Los discos que "continuan" a otro son la discografia del grupo: eso ya lo
# dice la pagina del autor. Aqui interesa lo que cruza o sigue una historia.
SIN_FOLLOWS = {"album"}


def consulta(sparql):
    datos = urllib.parse.urlencode({"query": sparql}).encode()
    r = pedir(SPARQL, datos=datos, headers={"Accept": "application/sparql-results+json",
                                             "Content-Type": "application/x-www-form-urlencoded"})
    return r["results"]["bindings"] if r else None


def elementos_por_id(lista):
    """(clave, valor del id) -> Q de la obra, en una sola consulta por fuente."""
    resultado = {}
    for clave, prop in PROPIEDADES.items():
        valores = sorted({str(c[clave]) for _md, c in lista if not vacio(c.get(clave))})
        if not valores:
            continue
        for i in range(0, len(valores), 200):
            trozo = " ".join(json.dumps(v) for v in valores[i:i + 200])
            filas = consulta(f"SELECT ?id ?item WHERE {{ VALUES ?id {{ {trozo} }} ?item wdt:{prop} ?id }}")
            for f in filas or []:
                # Si dos elementos dicen tener el mismo id (pasa con remasters),
                # se queda el primero: mejor uno que ninguno, y el campo se
                # puede corregir a mano.
                resultado.setdefault((clave, f["id"]["value"]), f["item"]["value"].rsplit("/", 1)[1])
    return resultado


def elementos_por_articulo(titulos):
    """Titulo de articulo de Wikipedia -> Q, de 50 en 50."""
    resultado = {}
    titulos = sorted(titulos)
    for i in range(0, len(titulos), 50):
        r = pedir("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({
            "action": "wbgetentities", "sites": f"{IDIOMA}wiki", "titles": "|".join(titulos[i:i + 50]),
            "props": "sitelinks", "sitefilter": f"{IDIOMA}wiki", "format": "json"}))
        for q, e in ((r or {}).get("entities") or {}).items():
            if q.startswith("Q"):
                resultado[e["sitelinks"][f"{IDIOMA}wiki"]["title"]] = q
    return resultado


def datos_de(qs):
    """Q -> {based_on, derivadas, follows, followed_by}, en una consulta."""
    datos = {q: {} for q in qs}
    qs = sorted(qs)
    for i in range(0, len(qs), 150):
        valores = " ".join(f"wd:{q}" for q in qs[i:i + 150])
        filas = consulta(f"""SELECT ?item ?p ?v WHERE {{
            VALUES ?item {{ {valores} }}
            VALUES (?p ?prop) {{ ("based_on" wdt:P144) ("derivadas" wdt:P4969) ("follows" wdt:P155) ("followed_by" wdt:P156) }}
            ?item ?prop ?v }}""")
        for f in filas or []:
            q = f["item"]["value"].rsplit("/", 1)[1]
            valor = f["v"]["value"].rsplit("/", 1)[-1]
            datos[q].setdefault(f["p"]["value"], [])
            if valor not in datos[q][f["p"]["value"]]:
                datos[q][f["p"]["value"]].append(valor)
    return datos


def enlace(md):
    """Como se escribe en la cabecera: un enlace de Obsidian con la carpeta,
    porque el manga y el anime de una misma obra se llaman igual."""
    return f"[[{md.parent.name}/{md.stem}]]"


def main(argv=None):
    p = argparse.ArgumentParser(description=ayuda(__doc__, "enlazar"), formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fichas", nargs="*", type=Path, help=_("las fichas que mirar; sin nada, todas"))
    p.add_argument("--dry-run", action="store_true", help=_("dice que pondria, sin tocar nada"))
    args = p.parse_args(argv)

    # Todas hacen falta siempre: una relacion solo se escribe si la otra obra
    # esta en la vitrina, aunque solo se este enlazando una.
    todas = [(md, frontmatter(md.read_text(encoding="utf-8")))
             for carpeta in SECCIONES for md in fichas(carpeta)]
    pedidas = {f.resolve() for f in args.fichas}
    objetivo = [(md, c) for md, c in todas if not pedidas or md.resolve() in pedidas]

    print(_("Preguntando a Wikidata por {n} fichas…").format(n=len(todas)))
    por_id = elementos_por_id([(md, c) for md, c in todas if vacio(c.get("wikidata"))])
    por_articulo = elementos_por_articulo({c["wikipedia"] for _md, c in todas
                                           if vacio(c.get("wikidata")) and not vacio(c.get("wikipedia"))})

    q_de = {}
    for md, c in todas:
        q = c.get("wikidata") if not vacio(c.get("wikidata")) else None
        for clave in PROPIEDADES:
            if not q and not vacio(c.get(clave)):
                q = por_id.get((clave, str(c[clave])))
        if not q and not vacio(c.get("wikipedia")):
            q = por_articulo.get(c["wikipedia"])
        if q:
            q_de[md] = q
    ficha_de = {}
    for md, q in q_de.items():
        ficha_de.setdefault(q, md)

    info = datos_de(set(q_de.values()))
    # Las relaciones se leen en los dos sentidos: que el anime diga «basado en
    # el manga» o que el manga diga «adaptado en el anime» es lo mismo.
    base_de, sigue_a = {}, {}
    for q, d in info.items():
        for otra in d.get("based_on", []):
            base_de.setdefault(q, set()).add(otra)
        for otra in d.get("derivadas", []):
            base_de.setdefault(otra, set()).add(q)
        for otra in d.get("follows", []):
            sigue_a.setdefault(q, set()).add(otra)
        for otra in d.get("followed_by", []):
            sigue_a.setdefault(otra, set()).add(q)

    cambiadas = 0
    for md, c in objetivo:
        q = q_de.get(md)
        tipo = c.get("type")
        if not q:
            continue
        d = info.get(q, {})
        nuevos = {}
        if q and vacio(c.get("wikidata")):
            nuevos["wikidata"] = q
        relacion = lambda qs: sorted(enlace(ficha_de[o]) for o in qs if o in ficha_de and ficha_de[o] != md)
        if vacio(c.get("based_on")) and relacion(base_de.get(q, ())):
            nuevos["based_on"] = relacion(base_de[q])
        if tipo not in SIN_FOLLOWS and vacio(c.get("follows")) and relacion(sigue_a.get(q, ())):
            nuevos["follows"] = relacion(sigue_a[q])
        if not nuevos:
            continue
        cambiadas += 1
        resumen = ", ".join(k if k == "wikidata" else f"{k}={v}" for k, v in nuevos.items())
        print(f"  ✓  {md.parent.name}/{md.stem}: {resumen}")
        if not args.dry_run:
            escribir_campos(md, nuevos)

    sin = [f"{md.parent.name}/{md.stem}" for md, _c in objetivo if md not in q_de]
    print("\n" + _("{n} fichas con algo nuevo; {m} sin elemento en Wikidata.").format(n=cambiadas, m=len(sin)))
    for s in sin:
        print(f"     {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
