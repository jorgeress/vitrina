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
- `started_on`: cuándo lo empezaste o, un disco, cuándo lo oíste por primera
  vez. Igual que `finished_on`; lo pone `scripts/cuando.py` del primer logro de
  Steam o de la primera escucha.
- `times`: cuántas veces lo has terminado. Desde 2 sale en la ficha: «Vista 3
  veces», «Jugado 2 veces», «Leído 4 veces».
- `based_on`, `follows` y `soundtrack`: otras fichas de la vitrina, como
  enlace con su carpeta: `based_on: ["[[libros/Chainsaw Man]]"]`. En qué se
  basa, a cuál continúa y cuál es su banda sonora. Basta con ponerlo en una de
  las dos: la otra dice «Adaptada en», «Sigue en» o «Banda sonora de».
  `scripts/enlazar.py` pone los dos primeros cuando Wikidata los sabe.
- `added`: cuándo entró en la vitrina. Lo ponen los scripts.
- `hidden`: `true` para que no salga en la web, o una lista de lo que no
  quieres enseñar: `hidden: [rating, opinion]` quita la nota y la opinión. Ojo:
  el fichero sigue en el repo, que es público. Lo que no quieras que vea nadie
  va en la carpeta `privado/`, que git no sube.
- `draft`: true mientras es un borrador; lo importado entra así.
- El identificador de la fuente, que lo pone el script y no se toca: `appid`
  (Steam), `letterboxd`, `tvmaze`, `mbid` (MusicBrainz) o `coverid` (Open
  Library), y `wikipedia`, el título del artículo en la Wikipedia en
  castellano cuando Wikidata no lo sabe. Y `wikidata`, el elemento de la obra.

El cuerpo es para lo tuyo: por qué está en la vitrina, lo que te dejó. Es lo
único que ninguna fuente puede rellenar. Va arriba, como tu opinión:

> [!vitrina] Por qué está en la vitrina
> Lo que te dejó, en dos frases.

No hace falta escribir el marco: si escribes suelto encima de la cita,
`scripts/al-dia.py` lo mete en él sin cambiar ni una palabra.

Lo que destripe algo va en un spoiler, que sale plegado en la web y no entra
en el buscador:

> [!spoiler]- Spoilers
> Lo que pasa al final.

Esta carpeta no se publica: la web solo lee las carpetas de las salas.
