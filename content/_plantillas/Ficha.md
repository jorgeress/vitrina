---
tipo: 
estado: pendiente
---

Plantilla mínima: de todo lo que puede llevar una ficha, `tipo` es lo único que
hace falta de verdad, porque es lo que decide en qué galería sale. El resto se
añade cuando se sepa, y los scripts saben crear una clave que no existía.

Campos:

- `tipo`: juego, peli, serie, libro o album. Debe coincidir con la carpeta.
- `seccion`: el enlace a la galería de su sección, `"[[juegos/index|Juegos]]"`.
  Es lo que cuelga la ficha de su sección en el grafo, y de ahí de Vitrina.
  No se escribe a mano: lo ponen los scripts al crear la ficha, y
  `scripts/secciones.py` repara el de las que falten o cambien de carpeta.
- `estado`: pendiente, en curso, terminado, abandonado. Es lo que reparte las
  cinco secciones en sus dos últimas pestañas: lo terminado en una, y lo
  pendiente y lo empezado en la otra, que es la lista de lo que queda; una ficha
  sin él sale en la galería y en ninguna de las dos. En series es donde más
  dice, que una serie larga se pasa años en «en curso». En juegos lo pones tú
  entero: Steam sabe cuántas horas le has echado a uno, no si lo terminaste, así
  que de un volcado solo sale `pendiente` para lo que no has abierto nunca. Es
  el único campo que no deja hueco vacío: si no lo sabes, la clave no va.
- `year`: año de la obra, no el de la edición que tengas.
- `autor`: estudio, dirección, autor o artista según el caso.
- `nota`: del 1 al 10, en número. Es opcional: ordena las galerías, y una ficha
  sin nota sale igual, al final.
- `favorito`: true o false. Alimenta *Lo mejor de lo mejor* y la pestaña
  «Favoritos» de
  cada sección.
- `favoritas`: solo en discos. Cuántas canciones tuyas hay en él. Sale en la
  ficha como «Canciones tuyas»; los nombres van en el cuerpo.
- `portada`: enlace a una imagen de `assets/portadas/`, entre corchetes.
- `tags`: géneros o etiquetas libres, **en inglés**, en minúscula, sin espacios
  y sin tildes ni símbolos. Los rellena `datos.py` con lo que digan Steam,
  Letterboxd, MusicBrainz y Open Library, que ya los dan así. En inglés porque
  de cada etiqueta sale una página: con tilde, su dirección viaja escapada
  (`tags/acci%C3%B3n`) y el grafo deja de encontrarla; y porque una sola lengua
  junta las cinco secciones en la misma etiqueta. Los mangas van en libros, con
  la etiqueta `manga`, y el anime en series, con la etiqueta `anime`: ninguno de
  los dos tiene sección aparte.
- El identificador de la fuente, que lo pone el script y no se toca: `appid`
  (Steam), `letterboxd`, `tvmaze`, `mbid` (MusicBrainz) o `coverid` (Open
  Library). La ficha los usa para enlazar a la fuente al pie de sus datos.
- `wikipedia`: en libros y en series, el nombre de su artículo en la Wikipedia
  en español. En un libro es lo único con lo que puede enlazar a algún sitio,
  porque `coverid` identifica la portada y no la obra. En una serie es opcional:
  solo hace falta cuando Wikidata no enlaza su `tvmaze` con ningún artículo, que
  es lo que pasa con casi todo el anime.

El cuerpo de la ficha es para lo tuyo: por qué está en la vitrina, lo que te
dejó, o qué canciones son las que te sabes. Es lo único que ninguna fuente
puede rellenar. Va arriba, en su cartela, encima de la cita de «De qué va»:

> [!vitrina] Por qué está en la vitrina
> Lo que te dejó, en dos frases.

No hace falta escribir el marco: si escribes suelto encima de la cita,
`scripts/al-dia.py` lo mete en él sin cambiar ni una palabra.

Esta carpeta no se publica: está en `ignorePatterns` de la configuración de Quartz.
