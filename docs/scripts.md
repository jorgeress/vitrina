# Los scripts, uno a uno

Todos leen y escriben en `content/`, ninguno pide clave de API y todos aceptan
`--dry-run` para ver qué harían sin tocar nada, salvo `repasar.py`, que pregunta
antes de escribir. Se pueden repetir cuantas veces quieras: solo rellenan lo
que falta.

Hablan el idioma de la vitrina (`language` en `vitrine.config.json`): sus
mensajes, su `--help` y lo que escriben dentro de las fichas. Las órdenes y las
opciones valen en los dos idiomas: `peli` o `film`, `--nota` o `--rating`,
`--estado terminado` o `--status finished`, `--seccion` o `--section`. Los
mensajes van en castellano en el código, dentro de `_()`, y su versión en
inglés en `mensajes_en.py`; `pruebas.py` falla si alguno no la tiene.

| Script | Para qué |
| --- | --- |
| `nueva.py` | Da de alta una obra, buscándola o desde su enlace |
| `desde_issue.py` | Lo mismo desde un Issue de GitHub, para añadir o editar desde el móvil |
| `repasar.py` | Pone nota, estado, favorito y tu frase, ficha a ficha |
| `importar.py` | Vuelca Letterboxd, Steam, ListenBrainz o Spotify |
| `al-dia.py` | Pasa todos los de abajo en orden, hasta `autores.py` |
| `portadas.py` | Baja las carátulas que falten |
| `datos.py` | Rellena año, autor y tags |
| `textos.py` | Escribe el «De qué va» y las canciones de cada disco |
| `enlazar.py` | Une cada ficha con Wikidata: de qué otra viene |
| `cuando.py` | Cuándo terminaste o empezaste cada cosa, de Letterboxd, Steam, Goodreads, ListenBrainz o Spotify |
| `autores.py` | Escribe las páginas de autor |
| `secciones.py` | Cuelga cada ficha de su sala (campo `section`) |
| `fechas.py` | Apunta la fecha de alta (campo `added`) de las que no la tienen |
| `enmarcar.py` | Convierte en opinión lo que hayas escrito suelto |
| `estado.py` | Qué hay y qué falta |
| `vistazo.py` | Levanta el sitio con los borradores, lo oculto y lo privado dentro |
| `empezar.py` | Deja una vitrina nueva, vacía, en castellano o en inglés |
| `plantillas.py` | Escribe las plantillas de ficha y de grupo de Obsidian |
| `pruebas.py` | Las pruebas, sin red |

## nueva.py

```bash
scripts/nueva.py juego "hollow knight"
scripts/nueva.py peli "parasite" --nota 10 --favorito
scripts/nueva.py album "in rainbows" --estado "en curso"
scripts/nueva.py libro "sapiens" --elegir 2      # sin preguntar
scripts/nueva.py https://store.steampowered.com/app/367520/
scripts/nueva.py boxd.it/2bg8                    # el enlace corto de Letterboxd
```

Con un título enseña candidatos y eliges tú. Con un enlace no pregunta, porque
el enlace ya dice cuál es. Guarda el identificador de la obra y la fecha de
alta, baja la portada, escribe el «De qué va» y pone al día las páginas de
autor.

| Tipo | Fuente | Guarda | Enlaces que entiende |
| --- | --- | --- | --- |
| `juego` / `game` | Steam | `appid` | `store.steampowered.com/app/…` |
| `peli` / `film` | Wikidata + Letterboxd | `letterboxd` | `letterboxd.com/film/…`, `boxd.it/…` |
| `serie` / `series` | TVmaze | `tvmaze` | `tvmaze.com/shows/…` |
| `album` / `disco` | MusicBrainz | `mbid` | `musicbrainz.org/release-group/…`, `/release/…`, `open.spotify.com/album/…` |
| `libro` / `book` | Open Library | `coverid` | `openlibrary.org/works/…`, `/books/…` |

Un disco de Spotify solo se encuentra si alguien lo ha enlazado en MusicBrainz;
si no, búscalo por título.

Los enlaces de otros sitios pasan por Wikidata, que guarda sus ids junto a los
de las cinco fuentes de arriba. Si Wikidata no tiene la obra enlazada, lo dice
y hay que buscarla por título.

| Sitio | Enlaces | Suele dar |
| --- | --- | --- |
| IMDb | `imdb.com/title/tt…` | película o serie |
| TMDB | `themoviedb.org/movie/…`, `/tv/…` | película, serie |
| FilmAffinity | `filmaffinity.com/es/film….html` | película |
| MyAnimeList, AniList | `/anime/…`, `/manga/…` | serie; el manga casi nunca |
| Goodreads | `goodreads.com/book/show/…`, `/work/…` | libro |
| Apple Music, Deezer, Discogs | `/album/…`, `discogs.com/master/…` | disco |
| IGDB, HowLongToBeat | `igdb.com/games/…`, `howlongtobeat.com/game/…` | juego (si está en Steam) |
| Wikipedia, Wikidata | cualquier artículo, en cualquier idioma | cualquiera |

Si la obra tiene ids de dos fuentes (el anime de *Death Note* tiene serie y
película), gana la serie; para elegir, pon el tipo delante:
`scripts/nueva.py peli https://myanimelist.net/anime/1535`.

Opciones:

| Opción | Qué hace |
| --- | --- |
| `--nota 1-10` | la nota (`rating`) |
| `--estado` | pending, in-progress, finished, dropped (o en castellano). Sin él, lo que lleva nota o fecha entra terminado y lo demás pendiente |
| `--favorito` | de lo mejor de lo mejor |
| `--grupo NOMBRE` | la mete en ese grupo; se puede repetir |
| `--terminada 2024-05` | cuándo la terminaste (`finished_on`): el anuario |
| `--veces 3` | cuántas veces la has terminado (`times`) |
| `--borrador` | entra con `draft: true` |
| `--oculta` | entra con `hidden: true`: no sale en la web, pero está en el repo |
| `--privada` | va a la carpeta privada, que git no sube |
| `--elegir N` | sin preguntar, el resultado N |
| `--fichero NOMBRE` | el nombre del fichero cuando el título no tiene letras latinas (`悪の華`) y la fuente no sabe cómo se llama en latino |

## desde_issue.py

Es lo que usa la Action `nueva-pieza.yml`, no hace falta lanzarlo a mano.
Para añadir sin terminal se abre un Issue con la plantilla **Nueva pieza**: el
enlace (vale cualquiera de los que acepta `nueva.py`), y si quieres la nota,
el estado, los grupos, cuándo la terminaste, si es de lo mejor de lo mejor, si
va oculta y por qué está en la vitrina. La Action crea la ficha con todo, la
guarda en `main` con un commit que redacta este script, publica la web y
contesta en el Issue con lo que ha hecho antes de cerrarlo.

El formulario está definido aquí, en los dos idiomas, y la plantilla del Issue
sale de él: `scripts/desde_issue.py --plantilla` la reescribe en el idioma de
la vitrina (`nueva-pieza.yml` o `new-piece.yml`). Una prueba avisa si la del
repo no es la que toca. Lo que ha hecho `nueva.py` lo lee de un informe en
JSON, no de sus mensajes.

Solo corre con los Issues del dueño del repo y con la etiqueta de la plantilla
(`nueva-pieza` o `new-piece`, que hay que crear una vez): en uno público
cualquiera puede abrir uno, y esto escribe en `main`. Lo que llega del formulario se valida
campo a campo y nunca se pega en una orden.

La otra plantilla, **Editar pieza** (`editar-pieza.yml`, con la etiqueta
`editar-pieza`), cambia una ficha que ya está: nota, estado, fecha de terminada
y opinión. No se rellena a mano: la abre el botón **✎ Editar** de cada ficha
(sale en el navegador donde lo hayas pedido en `/anadir/`), con la ruta de la
ficha y lo que ya tiene. Lo que llega en «Sin cambios» o en blanco no se toca;
la opinión se cambia sin tocar el resto del texto (spoilers, la cita). La ruta
tiene que ser una ficha que exista dentro de una sala; cualquier otra cosa es
un error, no un fichero nuevo.

Desde el móvil es aún más corto: con la web instalada como app, en Android
sale en el menú de **Compartir**. Compartir un enlace de Letterboxd, Steam o
Spotify a *Vitrina* abre el formulario con el enlace ya puesto.

```bash
scripts/desde_issue.py evento.json --dry-run   # lo que haría con ese Issue
```

## repasar.py

```bash
scripts/repasar.py                   # las fichas sin nota o sin estado
scripts/repasar.py --seccion series  # solo esa carpeta
scripts/repasar.py --todas           # también las que ya tienen las dos
```

Por cada ficha contestas en una línea, en cualquier orden:

| Escribes | Pone |
| --- | --- |
| `8` | `rating: 8` |
| `p` `c` `t` `a` | pending, in-progress, finished, dropped (también escritos enteros, en los dos idiomas) |
| `f` / `-f` | favorita / ya no |
| Enter | nada; pasa a la siguiente |
| `q` | para; lo contestado ya está guardado |

Con nota y sin estado se entiende `finished`, salvo que la ficha ya dijera
`in-progress` o `dropped`. Después, si la ficha no tiene nada tuyo escrito,
pide por qué está en la vitrina y lo pone arriba del todo, como su opinión
(`> [!vitrina] Por qué está en la vitrina`), encima de la cita. Enter la salta.

## al-dia.py

```bash
scripts/al-dia.py                   # todo
scripts/al-dia.py --seccion libros  # solo esa carpeta, en lo que va por carpeta
scripts/al-dia.py --sin-red         # solo secciones, fechas, opiniones y autores
scripts/al-dia.py --dry-run
```

Pasa `secciones`, `fechas`, `enmarcar`, `portadas`, `datos`, `textos`,
`enlazar`, `cuando` y `autores`, en ese orden. Si un paso falla sigue con los demás y
lo dice al terminar.

## importar.py

```bash
scripts/importar.py letterboxd-rss TU_USUARIO
scripts/importar.py letterboxd-watchlist TU_USUARIO
scripts/importar.py letterboxd ~/Descargas/letterboxd-export.zip
scripts/importar.py steam ~/Descargas/juegos.html
scripts/importar.py listenbrainz TU_USUARIO
scripts/importar.py spotify-export ~/Descargas/spotify.zip [--canciones]
```

Todo entra en borrador (`draft: true`) salvo con `--sin-borrador`, en la
carpeta de su sala según la configuración, y nunca
pisa una ficha que ya exista. Por defecto solo entra lo que tiene señal de
haberte importado: 8 horas en Steam, 4 estrellas en Letterboxd. Los umbrales se
cambian con `--min-horas` y `--min-nota`, y `--completo` los quita. Qué da cada
fuente, en [`importar.md`](importar.md).

## portadas.py, datos.py y textos.py

Los tres van por el identificador de la ficha y solo tocan lo que está vacío,
salvo con `--force`. Aceptan `--seccion CARPETA`.

| Sección | Portada | Año, autor y tags | Texto |
| --- | --- | --- | --- |
| Juegos | Steam | Steam | Steam, en el idioma de la vitrina |
| Películas | Letterboxd | Letterboxd | su Wikipedia; si no hay, TMDB (en inglés) |
| Series | TVmaze | TVmaze | su Wikipedia; si no hay, TVmaze (en inglés) |
| Música | Cover Art Archive | MusicBrainz (tags) | Lista de canciones |
| Libros | Open Library | Open Library (tags) | su Wikipedia, vía Wikidata |

«Su Wikipedia» es la del idioma de la vitrina: la española en una vitrina en
castellano, la inglesa en una en inglés. Lo que solo existe en inglés lleva el
aviso en el crédito si la vitrina no lo está.

`textos.py` solo reescribe lo que escribió él: la cita de «De qué va» y la
lista de canciones. Lo que escribas encima se queda.

En los libros, el artículo sale de la obra de Open Library a la que pertenece
el `coverid`, y se apunta en el campo `wikipedia`. Si Wikidata no tiene la obra
enlazada, pon ese campo a mano con el nombre del artículo.

## cuando.py

```bash
scripts/cuando.py                          # las cuentas de "accounts"
scripts/cuando.py letterboxd TU_USUARIO     # el RSS: las últimas ~50 películas
scripts/cuando.py letterboxd ~/Descargas/letterboxd.zip   # el export, entero
scripts/cuando.py steam 7656119XXXXXXXXXX
scripts/cuando.py goodreads 12345678
scripts/cuando.py listenbrainz TU_USUARIO
scripts/cuando.py spotify ~/Descargas/my_spotify_data.zip
scripts/cuando.py --dry-run
```

Solo escribe donde el campo está vacío:

| Sala | Campo | De dónde |
| --- | --- | --- |
| Películas | `finished_on` (el día) | diario de Letterboxd, por el slug de la ficha; con el export, también `times` |
| Libros | `finished_on` (el día) | estantería «read» de Goodreads, por título y autor a la vez |
| Juegos | `started_on` (el mes) | el primer logro en Steam, por el `appid` |
| Discos | `started_on` (el día) | la primera escucha en ListenBrainz o en el historial ampliado de Spotify |

Lo que no se sabe seguro se deja vacío: una película cuya primera entrada en el
diario ya es un revisionado, un juego con algún logro sin fecha (Steam pone
1970), un disco cuya primera escucha cae en el primer mes del registro. Steam
pide el perfil y los detalles de juegos públicos; Goodreads, la estantería
pública. Las series no tienen de dónde: TVmaze y Trakt piden cuenta o clave.

## enlazar.py

```bash
scripts/enlazar.py                         # todas
scripts/enlazar.py "content/pelis/Clue.md"
scripts/enlazar.py --dry-run
```

Busca el elemento de Wikidata de cada ficha por el id que ya tiene (`appid`,
`letterboxd`, `tvmaze`, `mbid`; los libros, por su `wikipedia`) y rellena, solo
donde esté vacío:

| Campo | De dónde | Para qué |
| --- | --- | --- |
| `wikidata` | el elemento (`Q…`) | lo demás |
| `based_on` | Wikidata (P144 y P4969, en los dos sentidos) | «Basada en» / «Adaptada en» |
| `follows` | Wikidata (P155 y P156) | «Continúa a» / «Sigue en» |

Las relaciones solo se escriben si la otra obra también está en la vitrina, y
los discos no llevan `follows` (la discografía ya la cuenta la página del
autor). `soundtrack` no lo sabe casi nunca: va a mano. `nueva.py` lo pasa solo para cada ficha nueva.

## autores.py, secciones.py y fechas.py

Los campos `section` y `added` los escriben `nueva.py` e `importar.py` al crear
la ficha, y `nueva.py` pasa `autores.py` al terminar. Para lo escrito o movido a
mano, `al-dia.py` los pasa los tres. `autores.py` da página a quien tenga dos
obras o más (`--minimo N` lo cambia). `fechas.py` saca la fecha del commit en
que entró cada ficha, y nunca cambia una que ya esté puesta. Las páginas de la
carpeta de autores se reescriben enteras en cada pasada: no se editan a mano.
Solo cuentan las fichas públicas: una página de autor está en el repo, y no
puede nombrar lo privado.

## estado.py

```bash
scripts/estado.py              # el resumen
scripts/estado.py --detalle    # qué le falta a cada ficha
scripts/estado.py --comprobar  # avisa de lo que se ha quedado atrás
```

`--comprobar` es el paso del CI que va antes de construir. Avisa si hay
portadas que no usa ninguna ficha o fichas sin fecha de alta. No para el
despliegue. Las cifras cuentan solo lo que sale en la web: ni lo oculto ni lo
privado.

## vistazo.py

```bash
scripts/vistazo.py               # http://localhost:8081/vitrina/, con todo dentro
scripts/vistazo.py --solo-build  # lo construye en web/vistazo/
```

Construye la web con los borradores, lo oculto (`hidden`) y la carpeta privada
dentro, marcados, para ver cómo queda una sala antes de publicar lo importado,
y la sirve en el 8081. Es la única forma de ver lo privado en la web, y solo en
tu ordenador. No copia ni toca la vault. Es una foto fija: si cambias algo,
vuelve a lanzarlo.

## empezar.py y plantillas.py

```bash
scripts/empezar.py --idioma en --nombre "Shelf" --dueno "Alex" \
    --repo https://github.com/alex/shelf --vaciar        # dice qué borraría
scripts/empezar.py ... --vaciar --si                     # lo hace
scripts/empezar.py --idioma es --solo-vistas             # rehace solo las vistas
scripts/plantillas.py                                    # las plantillas de Obsidian
```

`empezar.py` es para quien usa este repo como plantilla: escribe
`vitrine.config.json` (la dirección sale del repo), las carpetas de las salas
con el nombre en su idioma, sus vistas de Obsidian (`.base`), la entrada, los
créditos, las plantillas y la del Issue. Con `--vaciar --si` quita la colección
anterior: fichas, autores, grupos y portadas. Las vistas que genera son las
mismas que las de esta vitrina, sin los comentarios.
