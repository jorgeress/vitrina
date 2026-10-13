# Vitrina

Mi colección de juegos, películas, series, libros y discos, con lo que pienso
de cada uno. Se escribe en Obsidian y se publica como web estática.

**→ [jorgeress.github.io/vitrina](https://jorgeress.github.io/vitrina/)**

*In English: [Vitrine](#in-english-vitrine).*

Cada obra es una ficha en Markdown. La web las lee tal cual y las enseña como
lo que son, piezas de una colección: cada sala con sus portadas y sus filtros,
lo mejor de lo mejor, la cartela de por qué está cada una y una constelación
que las une por lo que comparten. En Obsidian, las galerías y tablas de los
`.base` enseñan lo mismo con los mismos campos.

## Arrancarlo

Hace falta [Node 22.12 o superior](https://nodejs.org), Python 3 y, para editar
cómodamente, [Obsidian](https://obsidian.md).

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
- El buscador solo funciona sobre la web construida: `npm run build` y después
  `npm run preview`. Con `dev` todavía no hay índice.

En Obsidian, *Abrir carpeta como almacén* sobre **`content/`**, no sobre la raíz
del repo. La configuración ya viene hecha.

## Añadir una obra

Con el enlace de la obra, o buscándola por el título:

```bash
scripts/nueva.py https://store.steampowered.com/app/367520/Hollow_Knight/
scripts/nueva.py boxd.it/2bg8 --nota 9
scripts/nueva.py peli "parasite" --nota 10 --favorito
scripts/nueva.py serie "breaking bad"
scripts/nueva.py album "in rainbows" --estado "en curso"
scripts/nueva.py libro "dune"
```

Valen los enlaces de Steam, Letterboxd, TVmaze, MusicBrainz, Open Library y
Spotify, y también los de IMDb, TMDB, FilmAffinity, MyAnimeList, AniList,
Goodreads, Apple Music, Deezer, Discogs, IGDB, HowLongToBeat y Wikipedia, que
pasan por Wikidata (la lista con ejemplos, en
[`docs/scripts.md`](docs/scripts.md)). Si buscas por título, te enseña los
candidatos y eliges tú.
La ficha sale completa: portada, año, autor, géneros, el «De qué va» y el
identificador de la fuente. Lo único que no puede poner es lo tuyo.

### Desde el móvil, sin terminal

Abre un Issue con la plantilla **Nueva pieza** y pega el enlace; si quieres,
pon nota, estado, si es de lo mejor de lo mejor y por qué está en la vitrina.
Una Action crea la ficha igual que `nueva.py`, la guarda, publica la web y
cierra el Issue diciendo qué ha hecho. Solo corre con los Issues del dueño del
repo.

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
después de la nota.

### A mano

Una ficha es un `.md` en la carpeta de su sección. Solo `tipo` es obligatorio:

```markdown
---
tipo: juego          # juego, peli, serie, libro o album
year: 2024
autor: LocalThunk
nota: 9              # del 1 al 10
estado: terminado    # pendiente, en curso, terminado o abandonado
favorito: true
tags:
  - strategy         # en inglés y sin tildes
---

> [!vitrina] Por qué está en la vitrina
> Lo que te dejó.
```

La plantilla con todos los campos está en `content/_plantillas/Ficha.md`
(`Ctrl+P` → *Insertar plantilla* en Obsidian). Después, `scripts/al-dia.py` la
deja como si la hubiera creado `nueva.py`.

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

`al-dia.py` pasa, en orden, todo lo que los scripts saben rellenar: sección,
fecha de alta, la cartela de lo que hayas escrito suelto, portada, año, autor,
tags, texto, páginas de autor y las cifras del README. Solo toca lo que falta, así que se puede lanzar siempre que quieras;
con `--sin-red` hace solo lo que no pregunta a nadie.

Para ver los borradores en el sitio antes de publicarlos, `scripts/vistazo.py`
(<http://localhost:8081/vitrina/>). Qué trae cada fuente está en
[`docs/importar.md`](docs/importar.md).

## Cómo va la colección

`scripts/estado.py` dice qué hay y qué falta. Este bloque lo escribe
`estado.py --readme`, y `nueva.py`, `repasar.py` e `importar.py` lo actualizan
solos:

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
  nota        167   █████···················
  portada       1   ████████████████████████
  tags          4   ████████████████████████
  texto         2   ████████████████████████

FAVORITOS  ██······················  21 de 210
```

## La web

- **La entrada** lleva el rótulo y, debajo, la presentación, que es **el primer
  párrafo de `content/index.md`**: se cambia en Obsidian como cualquier nota.
  Después vienen las salas, **Lo mejor de lo mejor** (los `favorito: true`, de
  más nota a menos), las cartelas escritas, lo que está **en el almacén**
  (`estado: pendiente`) y lo **recién llegado**, por el campo `alta`, que lo
  pone `nueva.py` y `al-dia.py` a las escritas a mano.
- **Cada sala** tiene buscador, orden y filtros por estado, favoritos, cartela y
  tag, y se quedan en la dirección: `juegos/?tag=metroidvania` se puede enlazar.
  Lo `abandonado` sale como *Retirado de la vitrina*, apagado.
- **Cada ficha** enseña sus fuentes y las seis piezas que más se le parecen,
  con el motivo: el mismo autor, o los tags que comparten (cuanto más raro el
  tag, más pesa).
- **La constelación** une cada pieza con sus tres más parecidas y con las de su
  mismo autor. La que no comparte nada se une a las de su sala más cercanas en
  el tiempo, con línea discontinua: ninguna se queda suelta.
- **Las direcciones son las mismas que tenía la web cuando la hacía Quartz**
  (`juegos/golf-it!`, `autores/fromsoftware,-inc`, `tags/action`, `index.xml`),
  así que ningún enlace viejo se rompe. Las de autor salen del nombre de
  fichero que les da `autores.py`.
- **Se instala como app** en el móvil y abre sin conexión lo ya visitado.
- **`vitrina.json`** es la colección entera con los ids de cada fuente, para
  poder compararla con otra sin fiarse de los títulos.
- Si una ficha trae un campo mal (`nota: 11`, un estado mal escrito), la web no
  se construye y el error dice cuál: el esquema está en
  `web/src/content.config.ts`.

## Publicar

Cada push a `main` pasa las pruebas y construye y publica el sitio en GitHub
Pages.

Para montarlo en tu cuenta:

1. Haz un *fork*.
2. En `web/astro.config.mjs`, cambia `site` por `https://tuusuario.github.io`
   (y `base`, si el repo no se llama `vitrina`).
   Y en `web/src/repo.ts`, la dirección de tu repo, que es a donde lleva
   *Añadir una pieza*.
3. En *Settings → Pages*, pon *Source* en **GitHub Actions**.

## Reglas de la vault

- **La carpeta y el `tipo` van a juego.** Un `tipo: album` en `juegos/` sale en
  la galería de música.
- **Nombres de fichero y etiquetas, en ASCII**, porque de ellos salen las
  direcciones. Las etiquetas, en inglés. Si el título lleva tildes o símbolos,
  el de verdad va en `title`.
- **Las portadas son ficheros** de `content/assets/portadas/`, enlazados como
  `portada: "[[nombre.webp]]"`.
- **`autor` es texto plano**, aunque sean dos separados por coma. El enlace a su
  página lo pone la web.
- **`content/autores/` no se edita**: lo reescribe `autores.py`.
- **El manga es un libro y el anime una serie**, con la etiqueta `manga` o
  `anime`.

## Estructura

```
content/            la vault: lo único que se escribe a mano
  juegos/ pelis/ series/ libros/ musica/
  autores/          páginas de autor, generadas
  *.base            las galerías y tablas de cada sección
  assets/portadas/  carátulas
scripts/            altas, importación y mantenimiento (docs/scripts.md)
web/                la web, en Astro
  src/pages/        una página por tipo: entrada, sala, ficha, autor, tag...
  src/lib/          de dónde sale cada cosa: autores, parecidos, direcciones
  src/styles/       colores y letras
  src/scripts/      la constelación, lo único con JavaScript propio
  public/           iconos, manifest y service worker de la app
  test/             pruebas de src/lib, sin levantar nada
docs/               los scripts, las fuentes de importación y lo que queda
.github/            el despliegue y el Issue de «Nueva pieza»
```

Todos los scripts y sus opciones están en [`docs/scripts.md`](docs/scripts.md).

## Pruebas

```bash
python3 scripts/pruebas.py   # sin red
cd web
npm test                     # entre otras, que reparte los autores igual que autores.py
npm run check                # tipos, y con ellos el esquema de las fichas
```

## Por hacer

Lo que falta y lo que se puede añadir está en
[`docs/por-hacer.md`](docs/por-hacer.md). Lo primero:

- Crear la etiqueta `nueva-pieza` en el repo, o el Issue de *Nueva pieza* no
  llega a la Action.
- Escribir las cartelas de verdad: cuatro de las cinco son de prueba.
- Importar solo cada noche, con un PR de borradores para revisar.
- «Me llegó por», «Me llevó a» y épocas, para que la vitrina diga también de
  dónde viene cada cosa y cuándo.

## In English: Vitrine

**Vitrine** is the tool behind this site: a personal collection of games,
films, series, books and albums, written as Markdown notes in Obsidian and
published as a static website. *Vitrina* is my own collection, in Spanish;
the name of the tool in English is Vitrine, a glass display case.

Every work is a note with a few fields (`tipo`, `year`, `autor`, `nota` from
1 to 10, `estado`, `favorito`, `tags`) and, on top, a short label written by
the owner: *why it is in the display case*, the way a museum labels each
piece. The site turns them into rooms with covers and filters, a page for the
very best, author and tag pages, statistics, a constellation that links each
piece to the ones it has most in common with, and a page that compares two
collections by the ids of each source instead of by titles.

What it does:

- **Adds a work from a link** (Steam, Letterboxd, TVmaze, MusicBrainz, Open
  Library, Spotify, and through Wikidata IMDb, TMDB, Goodreads, MyAnimeList,
  Discogs and others) with cover, year, author, genres and synopsis. No source
  needs an API key, an account or payment.
- **Adds from a phone**, with no terminal: a GitHub Issue with the *Nueva
  pieza* form, or sharing a link to the installed web app on Android.
- **Imports** a Letterboxd diary or watchlist, a Steam library, ListenBrainz
  and a Spotify data export, as drafts to review.
- **Works offline** and installs as an app; publishes an RSS feed and a
  `vitrina.json` with the whole collection.

Running it needs Node 22.12+ and Python 3:

```bash
git clone https://github.com/jorgeress/vitrina.git
cd vitrina
pip install -r requirements.txt
cd web
npm ci --ignore-scripts --include=optional
npm run dev                    # http://localhost:4321/vitrina/
```

To make it your own: fork it, delete the notes in each section folder of
`content/` and their covers in `content/assets/portadas/`, rewrite
`content/index.md` (its first paragraph is the welcome text), set `site` and
`base` in
`web/astro.config.mjs` and your repo in `web/src/repo.ts`, and choose
*GitHub Actions* as the Pages source. The interface, the scripts and their
documentation are in Spanish for now; translating the interface is on the
list in [`docs/por-hacer.md`](docs/por-hacer.md).

Code under MIT; the texts in `content/` under CC BY-SA 4.0. Details in
`LICENSE.txt`.

## Licencia

El código es mío y va bajo MIT. Hasta octubre de 2026 la web la hacía un fork
de [Quartz](https://quartz.jzhao.xyz), de jackyzha0, también MIT; sigue en el
historial. Los textos de `content/` son míos, Copyright (c) 2026 Jorge García,
bajo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es). Las
carátulas son de sus autores y se usan en miniatura para identificar cada obra.
El detalle, en `LICENSE.txt`.
