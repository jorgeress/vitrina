# Vitrina

Mi colección de juegos, películas, series, libros y discos, con lo que pienso
de cada uno. Se escribe en Obsidian y se publica como web estática.

**→ [jorgeress.github.io/vitrina](https://jorgeress.github.io/vitrina/)**

*In English: [README.en.md](README.en.md). La herramienta se llama
**Vitrine** y sirve de plantilla para hacerse una vitrina propia, en castellano
o en inglés.*

Cada obra es una ficha en Markdown. La web las lee tal cual y las enseña como
lo que son, piezas de una colección: cada sala con sus portadas y sus filtros,
lo mejor de lo mejor, la cartela de por qué está cada una, los grupos que hago
yo, un anuario y una constelación que las une por lo que comparten. En
Obsidian, las galerías y tablas de los `.base` enseñan lo mismo con los mismos
campos.

## Arrancarlo

Hace falta [Node 22.12 o superior](https://nodejs.org), Python 3 y, para
editar cómodamente, [Obsidian](https://obsidian.md).

```bash
git clone https://github.com/jorgeress/vitrina.git
cd vitrina
pip install -r requirements.txt
cd web
npm ci --ignore-scripts --include=optional
npm run dev                    # http://localhost:4321/vitrina/
```

- La web está en `web/`, hecha con [Astro](https://astro.build), y lee las
  fichas de `content/` sin tocarlas: lo que guardas en Obsidian sale en
  `npm run dev` al momento.
- Sin `--ignore-scripts`, `sharp` intenta compilarse y la instalación falla.
- El buscador y las tarjetas para compartir se hacen al construir: `npm run
  build` y después `npm run preview`.

En Obsidian, *Abrir carpeta como almacén* sobre **`content/`**, no sobre la raíz
del repo. La configuración ya viene hecha.

## Una sola configuración: `vitrine.config.json`

Todo lo que cambia de una vitrina a otra está en un fichero, en la raíz, que
leen la web y los scripts:

```json
{
  "name": "Vitrina",
  "owner": "Jorge García",
  "language": "es",
  "site": "https://jorgeress.github.io",
  "base": "/vitrina",
  "repo": "https://github.com/jorgeress/vitrina",
  "folders": { "game": "juegos", "film": "pelis", "series": "series", "book": "libros",
               "album": "musica", "author": "autores", "private": "privado", "group": "grupos" }
}
```

- **`language`**: `es` o `en`. Cambia la interfaz entera, las direcciones de las
  páginas (`/autores/` o `/authors/`), lo que dicen los scripts y en qué idioma
  se piden los textos a Steam y a Wikipedia.
- **`folders`**: cómo se llama cada carpeta de la vault, que es también la
  dirección de cada sala.

### Hacerse una vitrina propia

Con el botón *Use this template* de GitHub (si el repo está marcado como
plantilla), o con un fork:

```bash
scripts/empezar.py --idioma en --nombre "Shelf" --dueno "Alex" \
    --repo https://github.com/alex/shelf --vaciar --si
```

Escribe la configuración (la dirección sale del repo), quita mi colección y
deja las salas, las vistas de Obsidian, la entrada, las plantillas y el
formulario del Issue en el idioma elegido. Después, en *Settings → Pages*,
*Source* en **GitHub Actions**, y crear la etiqueta del Issue (`gh label create
new-piece`, o `nueva-pieza` en castellano).

## Añadir una obra

Con el enlace de la obra, o buscándola por el título:

```bash
scripts/nueva.py https://store.steampowered.com/app/367520/Hollow_Knight/
scripts/nueva.py boxd.it/2bg8 --nota 9
scripts/nueva.py peli "parasite" --nota 10 --favorito
scripts/nueva.py serie "death note" --grupo "Anime y manga" --terminada 2021-03
scripts/nueva.py album "in rainbows" --estado "en curso"
scripts/nueva.py libro "dune" --oculta
```

Valen los enlaces de Steam, Letterboxd, TVmaze, MusicBrainz, Open Library y
Spotify, y también los de IMDb, TMDB, FilmAffinity, MyAnimeList, AniList,
Goodreads, Apple Music, Deezer, Discogs, IGDB, HowLongToBeat y Wikipedia, que
pasan por Wikidata (la lista con ejemplos, en
[`docs/scripts.md`](docs/scripts.md)). Si buscas por título, te enseña los
candidatos y eliges tú. Las órdenes valen en castellano y en inglés: `peli` o
`film`, `--nota` o `--rating`, `--estado terminado` o `--status finished`.

La ficha sale completa: portada, año, autor, géneros, el «De qué va» y el
identificador de la fuente. Lo único que no puede poner es lo tuyo.

### Desde el móvil, sin terminal

Abre un Issue con la plantilla **Nueva pieza** y pega el enlace; si quieres,
pon nota, estado, grupos, cuándo la terminaste, si es de lo mejor de lo mejor,
si va oculta y por qué está en la vitrina. Una Action crea la ficha igual que
`nueva.py`, la guarda, publica la web y cierra el Issue diciendo qué ha hecho.
Solo corre con los Issues del dueño del repo, y solo si existe la etiqueta
`nueva-pieza`.

Con la web instalada como app, en Android sale **Vitrina** en el menú de
Compartir: compartir un enlace desde Letterboxd, Steam o Spotify abre el
formulario con el enlace ya puesto. También está en `/anadir/`.

### Lo tuyo: por qué está en la vitrina

Lo que escribes tú va arriba del todo, en su propia cartela, **«Por qué está en
la vitrina»**, como la que lleva al lado cada pieza de un museo. Debajo queda la
cita de la fuente, así que se ve de un vistazo qué es tuyo y qué no, en Obsidian
y en la web:

```markdown
> [!vitrina] Por qué está en la vitrina
> Me reí con esta desde los catorce y no he parado.

> [!quote] De qué va
> Zoolander es una comedia…
```

No hace falta escribir el marco: escribe suelto encima de la cita y
`scripts/al-dia.py` lo enmarca, o contéstalo en `repasar.py`, que lo pide
después de la nota. En una vitrina en inglés el callout es `[!vitrine]`; valen
los dos.

### A mano

Una ficha es un `.md` en la carpeta de su sala. Solo `type` es obligatorio. Las
claves van en inglés también en una vitrina en castellano, para que dos
vitrinas en idiomas distintos se puedan comparar:

```markdown
---
type: game           # game, film, series, book o album
year: 2024
author: LocalThunk
rating: 9            # del 1 al 10
status: finished     # pending, in-progress, finished o dropped
favorite: true
tags:
  - strategy         # en inglés y sin tildes
groups:
  - Roguelikes       # los grupos que haces tú
finished_on: 2024-05 # AAAA, AAAA-MM o AAAA-MM-DD: el anuario
---

> [!vitrina] Por qué está en la vitrina
> Lo que te dejó.
```

La plantilla con todos los campos está en `content/_plantillas/Ficha.md`
(`Ctrl+P` → *Insertar plantilla* en Obsidian). Después, `scripts/al-dia.py` la
deja como si la hubiera creado `nueva.py`.

## Lo que se ve y lo que no

Tres niveles, de menos a más:

| | Cómo | ¿En la web? | ¿En GitHub? |
|---|---|---|---|
| **Borrador** | `draft: true` | no | sí |
| **Oculta** | `hidden: true` | no | **sí** |
| **Campos ocultos** | `hidden: [rating, label]` | la ficha sí, esos campos no | sí |
| **Privada** | en la carpeta `content/privado/` | no | no |

- `hidden` con una lista quita esos campos de la página, del `vitrine.json`, de
  la tarjeta para compartir y del anuario. `label` es la cartela. Valen
  `rating`, `status`, `favorite`, `label`, `finished_on`, `groups` y `added`.
- **Oculto no es secreto**: el repo es público y el fichero se lee en GitHub.
  Lo que no quieras que vea nadie va en `content/privado/`, que git no sube.
  Dentro lleva las mismas carpetas (`privado/juegos/…`) y sus propias
  portadas. `nueva.py --privada` la crea ahí directamente.
- `scripts/vistazo.py` construye la web con todo dentro, marcado, en
  <http://localhost:8081/vitrina/>: es la única forma de ver lo privado, y solo
  en tu ordenador.

## Grupos

Colecciones que haces tú y que cruzan las salas: «Anime y manga», «Lo que me
recomendó Pablo», «Verano de 2024». Un tag lo pone la fuente; un grupo, tú.

- En la ficha: `groups: [Anime y manga]` (o `nueva.py --grupo`).
- Si quieres un texto o sacarlo en la entrada, una nota en `content/grupos/`
  con su título (plantilla en `_plantillas/Grupo.md`): `featured: true` lo pone
  debajo de las salas, `hidden: true` lo quita de la web.
- Cada grupo tiene su página en `/grupos/`.

## Ponerle nota a lo que ya tienes

```bash
scripts/repasar.py
```

Al empezar enseña una guía con los atajos (y `?` la repite). Luego va una a una
por las fichas sin nota o sin estado, y contestas en una línea:
`9 f` es un 9 y favorita, `t` es terminado, `p` pendiente, Enter la salta y `q`
para. Si la ficha no tiene nada tuyo escrito, después te pide por qué está en
la vitrina, y lo guarda en su cartela. Guarda cada respuesta al momento.

## Traer tu colección de otros sitios

```bash
scripts/importar.py letterboxd-rss TU_USUARIO
scripts/importar.py letterboxd-watchlist TU_USUARIO
scripts/importar.py steam ~/Descargas/juegos.html
scripts/importar.py listenbrainz TU_USUARIO
scripts/importar.py spotify-export ~/Descargas/spotify.zip
```

Lo importado entra **en borrador**: se ve en Obsidian pero no en la web hasta
que le quitas la línea `draft: true`. Después, para completarlo:

```bash
scripts/al-dia.py
```

`al-dia.py` pasa, en orden, todo lo que los scripts saben rellenar: sala,
fecha de alta, la cartela de lo que hayas escrito suelto, portada, año, autor,
tags, texto, páginas de autor y las cifras del README. Solo toca lo que falta,
así que se puede lanzar siempre que quieras; con `--sin-red` hace solo lo que
no pregunta a nadie. Qué trae cada fuente está en
[`docs/importar.md`](docs/importar.md).

## Cómo va la colección

`scripts/estado.py` dice qué hay y qué falta. Este bloque lo escribe
`estado.py --readme`, y `nueva.py`, `repasar.py` e `importar.py` lo actualizan
solos. Cuenta solo lo que sale en la web:

```
FICHAS
              total  borrador  publicadas  con texto
  juegos         46         0          46         45
  pelis          37         0          37         37
  series         26         0          26         26
  libros         11         0          11         10
  musica         90         0          90         90
             —————— ————————— ——————————— ——————————
  total         210         0         210        208

SIN RELLENAR
  rating      167   █████···················
  cover         1   ████████████████████████
  tags          4   ████████████████████████
  texto         2   ████████████████████████

FAVORITOS  ██······················  21 de 210
```

## La web

- **La entrada** lleva el rótulo y, debajo, la presentación, que es **el primer
  párrafo de `content/index.md`**: se cambia en Obsidian como cualquier nota.
  Después vienen las salas, los grupos destacados, **Lo mejor de lo mejor**
  (los `favorite: true`, de más nota a menos), las cartelas escritas, lo que
  está **en el almacén** (`status: pending`) y lo **recién llegado**.
- **Cada sala** tiene buscador, orden y filtros por estado, favoritos, cartela y
  tag, y se quedan en la dirección: `juegos/?tag=metroidvania` se puede enlazar.
  Lo `dropped` sale como *Retirado de la vitrina*, apagado.
- **Cada ficha** enseña sus fuentes, sus grupos, cuándo la terminaste y las seis
  piezas que más se le parecen, con el motivo: el mismo autor, o los tags que
  comparten (cuanto más raro el tag, más pesa).
- **El anuario** (`/anuario/2024/`) junta lo que terminaste cada año
  (`finished_on`) y lo que entró en la vitrina (`added`), con lo mejor del año
  y sus cartelas. El año en que se abrió la vitrina lo dice: ese año entró todo
  de golpe.
- **La constelación** une cada pieza con sus tres más parecidas y con las de su
  mismo autor. La que no comparte nada se une a las de su sala más cercanas en
  el tiempo, con línea discontinua: ninguna se queda suelta.
- **Cada ficha tiene su tarjeta para compartir**: al pegar su enlace en un chat
  sale una imagen con la portada, el título, la nota, la estrella y el
  principio de la cartela, con las letras de la casa. Se pintan al construir.
- **Comparar** (`/comparar/`) cruza esta vitrina con otra, por su dirección o
  con su fichero `vitrine.json`: lo que tenéis en común, dónde no estáis de
  acuerdo y qué hay allí que no está aquí. Se compara por los ids de cada
  fuente, no por los títulos.
- **Las direcciones son las mismas que tenía la web cuando la hacía Quartz**
  (`juegos/golf-it!`, `autores/fromsoftware,-inc`, `tags/action`, `index.xml`),
  así que ningún enlace viejo se rompe.
- **Se instala como app** en el móvil y abre sin conexión lo ya visitado.
- Si una ficha trae un campo mal (`rating: 11`, un estado mal escrito), la web
  no se construye y el error dice cuál: el esquema está en
  `web/src/content.config.ts`.

## Publicar

Cada push a `main` pasa las pruebas y construye y publica el sitio en GitHub
Pages. La primera vez, en *Settings → Pages*, *Source* en **GitHub Actions**.

## Reglas de la vault

- **La carpeta y el `type` van a juego.** Un `type: album` en `juegos/` sale en
  la galería de música.
- **Nombres de fichero y etiquetas, en ASCII**, porque de ellos salen las
  direcciones. Las etiquetas, en inglés. Si el título lleva tildes o símbolos,
  el de verdad va en `title`.
- **Las portadas son ficheros** de `content/assets/portadas/`, enlazados como
  `cover: "[[nombre.webp]]"`.
- **`author` es texto plano**, aunque sean dos separados por coma. El enlace a
  su página lo pone la web.
- **`content/autores/` no se edita**: lo reescribe `autores.py`.
- **El manga es un libro y el anime una serie**, con la etiqueta `manga` o
  `anime`; el grupo *Anime y manga* los junta.

## Estructura

```
vitrine.config.json  nombre, idioma, dirección y carpetas
content/             la vault: lo único que se escribe a mano
  juegos/ pelis/ series/ libros/ musica/
  grupos/            las notas de los grupos
  autores/           páginas de autor, generadas
  privado/           lo privado, que git no sube
  *.base             las galerías y tablas de cada sala
  assets/portadas/   carátulas
scripts/             altas, importación y mantenimiento (docs/scripts.md)
  idioma.py          el idioma de la vitrina para los scripts
  mensajes_en.py     lo que dicen los scripts, en inglés
web/                 la web, en Astro
  src/i18n.ts        todos los textos de la web, en castellano y en inglés
  src/pages/         una página por tipo; las de [nombre] van en su idioma
  src/lib/           de dónde sale cada cosa: visibilidad, grupos, parecidos
  src/integraciones/ portadas, buscador y tarjetas para compartir
  fuentes/           las letras de la casa, para las tarjetas
  test/              pruebas de src/lib, sin levantar nada
docs/                los scripts, las fuentes de importación y lo que queda
.github/             el despliegue y el Issue de «Nueva pieza»
```

## Pruebas

```bash
python3 scripts/pruebas.py   # sin red; también que no falte ninguna traducción
cd web
npm test                     # entre otras, que reparte los autores igual que autores.py
npm run check                # tipos, y con ellos el esquema de las fichas
```

## Por hacer

Lo que falta y lo que se puede añadir está en
[`docs/por-hacer.md`](docs/por-hacer.md).

## Licencia

El código es mío y va bajo MIT. Hasta octubre de 2026 la web la hacía un fork
de [Quartz](https://quartz.jzhao.xyz), de jackyzha0, también MIT; sigue en el
historial. Los textos de `content/` son míos, Copyright (c) 2026 Jorge García,
bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es).
Las carátulas son de sus autores y se usan en miniatura para identificar cada
obra. Las fuentes de `web/fuentes/` son de sus autores, bajo la SIL Open Font
License. El detalle, en `LICENSE.txt`.
