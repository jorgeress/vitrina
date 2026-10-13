---
type:
status: pending
---

Plantilla mínima: de todo lo que puede llevar una ficha, `type` es lo único
que hace falta de verdad, porque es lo que decide en qué sala sale. El resto se
añade cuando se sepa, y los scripts saben crear una clave que no existía.

Las claves van en inglés, también en una vitrina en castellano: así dos
vitrinas en idiomas distintos se pueden comparar, y las vistas de Obsidian
valen para las dos.

Campos:

- `type`: game, film, series, book o album. Debe coincidir con la carpeta.
- `status`: pending (en el almacén), in-progress, finished o dropped (retirado
  de la vitrina). Si no lo sabes, la clave no va.
- `year`: año de la obra, no el de la edición que tengas.
- `author`: estudio, dirección, autor o artista según el caso. Texto plano,
  aunque sean varios separados por comas.
- `rating`: del 1 al 10, en número. Opcional: ordena las galerías.
- `favorite`: true o false. Alimenta «Lo mejor de lo mejor».
- `cover`: enlace a una imagen de `assets/portadas/`, entre corchetes.
- `tags`: géneros, en inglés, en minúscula y sin tildes. Los rellena
  `datos.py`. El manga es un libro y el anime una serie, con su etiqueta.
- `groups`: los grupos que haces tú, en lista: `groups: [Anime y manga]`. Un
  grupo puede tener su nota en la carpeta `grupos/`, con un texto; si no la
  tiene, sale igual.
- `finished_on`: cuándo lo terminaste, `2024`, `2024-05` o `2024-05-03`, con
  la precisión que sepas. Es lo que lo pone en el anuario.
- `added`: cuándo entró en la vitrina. Lo ponen los scripts.
- `hidden`: `true` para que no salga en la web, o una lista de lo que no
  quieres enseñar: `hidden: [rating, label]` quita la nota y la cartela. Ojo:
  el fichero sigue en el repo, que es público. Lo que no quieras que vea nadie
  va en la carpeta `privado/`, que git no sube.
- `draft`: true mientras es un borrador; lo importado entra así.
- El identificador de la fuente, que lo pone el script y no se toca: `appid`
  (Steam), `letterboxd`, `tvmaze`, `mbid` (MusicBrainz) o `coverid` (Open
  Library), y `wikipedia`, el título del artículo en la Wikipedia en
  castellano cuando Wikidata no lo sabe.

El cuerpo es para lo tuyo: por qué está en la vitrina, lo que te dejó. Es lo
único que ninguna fuente puede rellenar. Va arriba, en su cartela:

> [!vitrina] Por qué está en la vitrina
> Lo que te dejó, en dos frases.

No hace falta escribir el marco: si escribes suelto encima de la cita,
`scripts/al-dia.py` lo mete en él sin cambiar ni una palabra.

Esta carpeta no se publica: la web solo lee las carpetas de las salas.
