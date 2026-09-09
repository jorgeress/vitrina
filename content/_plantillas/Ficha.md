---
tipo: 
estado: pendiente
---

Plantilla mínima: de todo lo que puede llevar una ficha, `tipo` es lo único que
hace falta de verdad, porque es lo que decide en qué galería sale. El resto se
añade cuando se sepa, y los scripts saben crear una clave que no existía.

Campos:

- `tipo`: juego, peli, libro o album. Debe coincidir con la carpeta.
- `estado`: pendiente, en curso, terminado, abandonado. Es lo que reparte
  películas, libros y discos en sus dos últimas pestañas: lo terminado en una,
  y lo pendiente y lo empezado en la otra, que es la lista de lo que queda; una
  ficha sin él sale en la galería y en ninguna de las dos. Los juegos no lo
  llevan y no les hace falta: allí las dos pestañas se reparten por las `horas`,
  porque de un juego ninguna fuente sabe si lo terminaste y los 44 acabaron
  diciendo lo mismo. Por eso es el único campo que no deja hueco vacío: si no
  lo sabes, la clave no va.
- `year`: año de la obra, no el de la edición que tengas.
- `autor`: estudio, dirección, autor o artista según el caso.
- `nota`: del 1 al 10, en número. Es opcional: ordena las galerías, y una ficha
  sin nota sale igual, al final.
- `favorito`: true o false. Alimenta *Favoritos* y la vista «Solo favoritos» de
  cada sección.
- `favoritas`: solo en discos. Cuántas canciones tuyas hay en él. Sale en la
  ficha como «Canciones tuyas»; los nombres van en el cuerpo.
- `portada`: enlace a una imagen de `assets/portadas/`, entre corchetes.
- `tags`: géneros o etiquetas libres, en minúscula y sin espacios. Los mangas
  van aquí, con la etiqueta `manga`, y no en una sección aparte. Los rellena
  `datos.py` salvo en libros: juegos y películas en castellano, discos en
  inglés, que es como los da MusicBrainz.
- El identificador de la fuente, que lo pone el script y no se toca: `appid`
  (Steam), `letterboxd`, `mbid` (MusicBrainz) o `coverid` (Open Library). La
  ficha los usa para enlazar a la fuente al pie de sus datos.
- `wikipedia`: solo en libros, el nombre de su artículo en la Wikipedia en
  español. `coverid` identifica la portada y no la obra, así que es lo único
  con lo que un libro puede enlazar a algún sitio.

El cuerpo de la ficha es para lo tuyo: por qué te gustó, o qué canciones son
las que te sabes. Es lo único que ninguna fuente puede rellenar, y lo único que
el buscador de la web indexa por dentro.

Esta carpeta no se publica: está en `ignorePatterns` de la configuración de Quartz.
