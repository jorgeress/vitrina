# Los scripts, uno a uno

Todos leen y escriben en `content/`, ninguno pide clave de API y todos aceptan
`--dry-run` para ver qué harían sin tocar nada, salvo `repasar.py`, que pregunta
antes de escribir. Se pueden repetir cuantas veces quieras: solo rellenan lo
que falta.

| Script | Para qué |
| --- | --- |
| `nueva.py` | Da de alta una obra, buscándola o desde su enlace |
| `repasar.py` | Pone nota, estado y favorito ficha a ficha |
| `importar.py` | Vuelca Letterboxd, Steam, ListenBrainz o Spotify |
| `portadas.py` | Baja las carátulas que falten |
| `datos.py` | Rellena año, autor y tags |
| `textos.py` | Escribe el «De qué va» y las canciones de cada disco |
| `autores.py` | Escribe las páginas de autor |
| `secciones.py` | Cuelga cada ficha de su sección (campo `seccion`) |
| `fechas.py` | Apunta la fecha de alta (campo `alta`) de las que no la tienen |
| `estado.py` | Qué hay y qué falta; actualiza las cifras del README |
| `vistazo.py` | Levanta el sitio con los borradores dentro |
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
el enlace ya dice cuál es. Guarda el identificador de la obra, baja la portada y
pone al día las páginas de autor y las cifras del README.

| Tipo | Fuente | Guarda | Enlaces que entiende |
| --- | --- | --- | --- |
| `juego` | Steam | `appid` | `store.steampowered.com/app/…` |
| `peli` | Wikidata + Letterboxd | `letterboxd` | `letterboxd.com/film/…`, `boxd.it/…` |
| `serie` | TVmaze | `tvmaze` | `tvmaze.com/shows/…` |
| `album` | MusicBrainz | `mbid` | `musicbrainz.org/release-group/…`, `/release/…`, `open.spotify.com/album/…` |
| `libro` | Open Library | `coverid` | `openlibrary.org/works/…`, `/books/…` |

Un disco de Spotify solo se encuentra si alguien lo ha enlazado en MusicBrainz;
si no, búscalo por título.

Opciones: `--nota 1-10`, `--estado`, `--favorito`, `--borrador`, `--elegir N`
y `--fichero NOMBRE`. Esta última hace falta cuando el título no tiene letras
latinas (`悪の華`) y la fuente no sabe cómo se llama en latino.

## repasar.py

```bash
scripts/repasar.py                   # las fichas sin nota o sin estado
scripts/repasar.py --seccion series  # solo esa carpeta
scripts/repasar.py --todas           # también las que ya tienen las dos
```

Por cada ficha contestas en una línea, en cualquier orden:

| Escribes | Pone |
| --- | --- |
| `8` | `nota: 8` |
| `p` `c` `t` `a` | pendiente, en curso, terminado, abandonado |
| `f` / `-f` | favorita / ya no |
| Enter | nada; pasa a la siguiente |
| `q` | para; lo contestado ya está guardado |

Con nota y sin estado se entiende `terminado`, salvo que la ficha ya dijera
`en curso` o `abandonado`.

## importar.py

```bash
scripts/importar.py letterboxd-rss TU_USUARIO
scripts/importar.py letterboxd-watchlist TU_USUARIO
scripts/importar.py letterboxd ~/Descargas/letterboxd-export.zip
scripts/importar.py steam ~/Descargas/juegos.html
scripts/importar.py listenbrainz TU_USUARIO
scripts/importar.py spotify-export ~/Descargas/spotify.zip [--canciones]
```

Todo entra en borrador (`draft: true`) salvo con `--sin-borrador`, y nunca
pisa una ficha que ya exista. Por defecto solo entra lo que tiene señal de
haberte importado: 8 horas en Steam, 4 estrellas en Letterboxd. Los umbrales se
cambian con `--min-horas` y `--min-nota`, y `--completo` los quita. Qué da cada
fuente, en [`importar.md`](importar.md).

## portadas.py, datos.py y textos.py

Los tres van por el identificador de la ficha y solo tocan lo que está vacío,
salvo con `--force`. Aceptan `--seccion CARPETA`.

| Sección | Portada | Año, autor y tags | Texto |
| --- | --- | --- | --- |
| Juegos | Steam | Steam | Steam, en español |
| Películas | Letterboxd | Letterboxd | Wikipedia en español; si no hay, TMDB |
| Series | TVmaze | TVmaze | Wikipedia en español; si no hay, TVmaze |
| Música | Cover Art Archive | MusicBrainz (tags) | Lista de canciones |
| Libros | Open Library | Open Library (tags) | Wikipedia, si la ficha lleva `wikipedia` |

`textos.py` solo reescribe lo que escribió él: la cita de «De qué va» y la
lista de canciones. Lo que escribas encima se queda.

## autores.py y secciones.py

El campo `seccion` lo escriben `nueva.py` e `importar.py` al crear la ficha, y
`nueva.py` pasa `autores.py` al terminar. A mano hacen falta después de
escribir o mover fichas fuera de los scripts, y `autores.py` también después de
`datos.py`, que es quien rellena el autor de lo importado. Da página a quien
tenga dos obras o más (`--minimo N` lo cambia). Las páginas de `content/autores/` se
reescriben enteras en cada pasada: no se editan a mano.

## estado.py

```bash
scripts/estado.py              # el resumen
scripts/estado.py --detalle    # qué le falta a cada ficha
scripts/estado.py --readme     # reescribe el bloque de cifras del README
scripts/estado.py --comprobar  # avisa de lo que se ha quedado atrás
```

`--comprobar` es el paso del CI que va antes de construir. Avisa si las cifras
del README ya no son las de la vault, si hay portadas que no usa ninguna ficha
o fichas sin fecha de alta. No para el despliegue.

## vistazo.py

```bash
scripts/vistazo.py               # http://localhost:8081, borradores incluidos
scripts/vistazo.py --solo-build
```

Construye una copia de la vault fuera del repo con los borradores
publicados. No toca `content/`.
