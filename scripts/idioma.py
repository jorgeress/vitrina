"""El idioma de la vitrina, para lo que los scripts escriben o dicen.

Sale de `language` en vitrine.config.json. Manda en tres cosas:

  - En que idioma se piden los textos a las fuentes: la descripcion de Steam
    y el articulo de Wikipedia salen en el de la vitrina.
  - Lo que se escribe dentro de las fichas: el titulo de la cartela, el de la
    cita («De qué va» o «What it's about») y las paginas de autor.
  - Lo que dicen los scripts por pantalla, con `_()` (en vitrina.py, que es
    el que importan todos): el texto se escribe en castellano, como el resto
    del codigo, y su version en ingles esta en mensajes_en.py.

Las claves de las fichas no dependen del idioma: van siempre en ingles.
"""

from vitrina import IDIOMA, _  # noqa: F401  (_ se importa de aqui)

# Las fuentes que hablan varios idiomas, en el de la vitrina. Cualquier idioma
# sin entrada aqui cae en el ingles, que es el de la herramienta.
STEAM = {"es": "spanish", "en": "english"}.get(IDIOMA, "english")
WIKIPEDIA = IDIOMA if IDIOMA in ("es", "en") else "en"
LICENCIA_CC = f"https://creativecommons.org/licenses/by-sa/4.0/deed.{WIKIPEDIA}"

# El callout de la cartela: [!vitrina] en castellano, [!vitrine] en ingles.
# Se leen los dos en cualquier idioma; se escribe el de la vitrina.
CALLOUT = "vitrina" if IDIOMA == "es" else "vitrine"
CALLOUTS = ("vitrina", "vitrine")

TEXTOS = {
    "es": {
        "cartela": "Por qué está en la vitrina",
        "de_que_va": "De qué va",
        "en_ingles": "en inglés",
        "autores": "Autores",
        "lo_que_tengo": "Lo que tengo de {autor}",
        "la_escribe": "Esta página la escribe `scripts/autores.py`.",
    },
    "en": {
        "cartela": "Why it's on display",
        "de_que_va": "What it's about",
        "en_ingles": "in English",
        "autores": "Authors",
        "lo_que_tengo": "What I have by {autor}",
        "la_escribe": "This page is written by `scripts/autores.py`.",
    },
}


def texto(clave, **datos):
    """Un texto de los que van dentro de la vault, en el idioma de la vitrina."""
    return TEXTOS.get(IDIOMA, TEXTOS["en"])[clave].format(**datos)


def ayuda(doc, clave):
    """La ayuda de un script (`--help`): su docstring en castellano o, en una
    vitrina en ingles, el resumen en ingles del catalogo."""
    if IDIOMA == "es":
        return doc
    from mensajes_en import AYUDAS
    return AYUDAS.get(clave, doc)


def opciones(castellano, ingles):
    """Los dos nombres de una opcion, el del idioma de la vitrina delante:
    es el que enseña `--help` en la linea de uso. Valen los dos siempre."""
    return (castellano, ingles) if IDIOMA == "es" else (ingles, castellano)
