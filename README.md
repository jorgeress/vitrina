# Vitrina

Una colección de juegos, películas, series, libros y discos, con lo que pienso
de cada uno. Se escribe en Obsidian y se publica como web estática.

**→ [jorgeress.github.io/vitrina](https://jorgeress.github.io/vitrina/)**

*In English: [README.en.md](README.en.md). Sirve de plantilla para hacerte la
tuya, en castellano o en inglés.*

Cada obra es una ficha en Markdown. La web enseña cada sala con sus portadas y
filtros, la ficha de cada obra con tu opinión, lo mejor de lo mejor, tus grupos,
un anuario y una constelación que las une por lo que comparten. Ninguna fuente
pide clave, cuenta ni pago.

## Hacerte la tuya

1. Haz un fork (o *Use this template*) y clónalo.
2. Déjala vacía y en tu idioma:

   ```bash
   pip install -r requirements.txt
   scripts/empezar.py --idioma es --nombre "Vitrina" --dueno "Tu nombre" \
       --repo https://github.com/tu-usuario/vitrina --vaciar --si
   ```

3. En GitHub, *Settings → Pages → Source*: **GitHub Actions**.
4. Crea las etiquetas de los Issues, para añadir y editar desde el móvil:

   ```bash
   gh label create nueva-pieza && gh label create editar-pieza
   ```

   (en una vitrina en inglés, `new-piece` y `edit-piece`).
5. Cambia el primer párrafo de `content/index.md`: es la presentación de la web.

Cada push a `main` pasa las pruebas y publica la web.

## Arrancarla

Hace falta [Node 22.12 o superior](https://nodejs.org), Python 3 y, para
escribir las fichas, [Obsidian](https://obsidian.md).

```bash
pip install -r requirements.txt
cd web
npm ci --ignore-scripts --include=optional
npm run dev                    # http://localhost:4321/vitrina/
```

- Lo que guardas en Obsidian sale en `npm run dev` al momento.
- Sin `--ignore-scripts`, `sharp` intenta compilarse y la instalación falla.
- El buscador y las tarjetas para compartir solo se hacen al construir:
  `npm run build` y después `npm run preview`.

En Obsidian, *Abrir carpeta como almacén* sobre **`content/`**, no sobre la raíz
del repo.

### La configuración

`vitrine.config.json`, en la raíz, lo leen la web y los scripts:

```json
{
  "name": "Vitrina",
  "owner": "Tu nombre",
  "language": "es",
  "site": "https://tu-usuario.github.io",
  "base": "/vitrina",
  "repo": "https://github.com/tu-usuario/vitrina",
  "folders": { "game": "juegos", "film": "pelis", "series": "series", "book": "libros",
               "album": "musica", "author": "autores", "private": "privado", "group": "grupos" }
}
```

`language` (`es` o `en`) cambia la interfaz, las direcciones y lo que dicen los
scripts. `folders` es el nombre de cada carpeta de la vault y la dirección de
cada sala. Lo escribe `empezar.py`.

Tus cuentas, para sacar las fechas (ver [Cuándo lo terminaste](#cuándo-lo-terminaste)),
van aparte en `vitrine.local.json`, que git no sube:

```json
{ "accounts": { "letterboxd": "usuario", "steam": "7656119…", "goodreads": "", "listenbrainz": "" } }
```

## Usarla

### Añadir una obra

Con su enlace o buscándola por el título:

```bash
scripts/nueva.py https://store.steampowered.com/app/367520/Hollow_Knight/
scripts/nueva.py peli "parasite" --nota 10 --favorito
scripts/nueva.py serie "death note" --grupo "Anime y manga" --terminada 2021-03
scripts/nueva.py album "in rainbows" --estado "en curso"
scripts/nueva.py libro "dune" --oculta
```

Valen los enlaces de Steam, Letterboxd, TVmaze, MusicBrainz, Open Library,
Spotify, IMDb, TMDB, FilmAffinity, MyAnimeList, AniList, Goodreads, Discogs,
Wikipedia y más. La ficha sale con portada, año, autor, géneros y el «De qué
va». Las órdenes valen en castellano y en inglés (`peli` o `film`, `--nota` o
`--rating`). Todas las opciones, en [`docs/scripts.md`](docs/scripts.md).

### Desde el móvil

Abre un Issue con la plantilla **Nueva pieza** y pega el enlace; si quieres,
pon nota, estado, grupos, fecha y tu opinión. Una Action crea la ficha, publica
la web y cierra el Issue. Solo atiende los Issues del dueño del repo.

Con la web instalada como app, en Android sale en el menú de **Compartir**:
compartir un enlace desde Letterboxd, Steam o Spotify abre el formulario con el
enlace puesto. También está en `/anadir/`.

### Editar desde la web

En `/anadir/`, marca «Enseñar el botón Editar». Desde entonces, en ese
navegador, cada ficha lleva un **✎ Editar** que abre el Issue **Editar pieza**
con la nota, el estado, la fecha y la opinión que ya tiene. Cambias lo que
quieras, lo mandas, y en un par de minutos está publicado.

### Tu opinión

Lo que escribes tú va arriba de la ficha, en su recuadro, y debajo la cita de
la fuente:

```markdown
> [!vitrina] Por qué está en la vitrina
> Me reí con esta desde los catorce y no he parado.
```

No hace falta escribir el marco: escribe suelto encima de la cita y
`scripts/al-dia.py` lo enmarca.

### Una ficha a mano

Un `.md` en la carpeta de su sala. Solo `type` es obligatorio, y las claves van
en inglés:

```markdown
---
type: game           # game, film, series, book o album
year: 2024
author: LocalThunk
rating: 9            # del 1 al 10
status: finished     # pending, in-progress, finished o dropped
favorite: true
tags:
  - strategy
groups:
  - Roguelikes       # los grupos que haces tú
finished_on: 2024-05 # AAAA, AAAA-MM o AAAA-MM-DD: el anuario
started_on: 2024-02  # cuándo lo empezaste
times: 2             # cuántas veces lo has terminado
follows:             # a cuál continúa; también based_on y soundtrack
  - "[[juegos/Slay the Spire]]"
---
```

Después pasa `scripts/al-dia.py`, que pone portada, datos y texto. La plantilla
con todos los campos explicados está en `content/_plantillas/Ficha.md`.

### Ponerle nota a lo que ya tienes

```bash
scripts/repasar.py
```

Va una a una por las fichas sin nota o sin estado y contestas en una línea:
`9 f` es un 9 y favorita, `t` terminado, `p` pendiente, Enter la salta, `q`
para. Después te pide tu opinión.

### Traer tu colección

```bash
scripts/importar.py letterboxd-rss TU_USUARIO
scripts/importar.py steam ~/Descargas/juegos.html
scripts/importar.py listenbrainz TU_USUARIO
scripts/importar.py spotify-export ~/Descargas/spotify.zip
scripts/al-dia.py
```

Lo importado entra en borrador (`draft: true`): se ve en Obsidian pero no en la
web hasta que quitas esa línea. `al-dia.py` rellena lo que falte; con
`--sin-red`, solo lo que no pregunta a nadie. Qué trae cada fuente, en
[`docs/importar.md`](docs/importar.md).

### Cuándo lo terminaste

```bash
scripts/cuando.py                       # las cuentas de vitrine.local.json
scripts/cuando.py letterboxd TU_USUARIO
```

Pone las fechas donde falten: las películas, del diario de Letterboxd; los
libros, de Goodreads; los juegos, del primer logro de Steam; los discos, de la
primera escucha en ListenBrainz o en el historial de Spotify. Lo que no se sabe
seguro se queda vacío. También lo pasa `al-dia.py`.

### Grupos

Colecciones que cruzan las salas («Anime y manga», «Lo que me recomendó
Pablo»): `groups: [Anime y manga]` en la ficha. Una nota con su nombre en
`content/grupos/` les da texto, y `featured: true` los saca en la entrada.

### Lo que se ve y lo que no

| | Cómo | ¿En la web? | ¿En GitHub? |
|---|---|---|---|
| **Borrador** | `draft: true` | no | sí |
| **Oculta** | `hidden: true` | no | **sí** |
| **Campos ocultos** | `hidden: [rating, opinion]` | la ficha sí, esos campos no | sí |
| **Privada** | en `content/privado/` | no | no |

Oculto no es secreto: el repo es público. Lo que no deba ver nadie va en
`content/privado/`, que git no sube. `scripts/vistazo.py` enseña la web con
todo dentro, solo en tu ordenador.

## Más

- [`docs/scripts.md`](docs/scripts.md): todos los scripts y sus opciones.
- [`docs/importar.md`](docs/importar.md): qué trae cada fuente.
- [`docs/la-web.md`](docs/la-web.md): lo que enseña cada página, las reglas de
  la vault, la estructura y las pruebas.
- [`docs/por-hacer.md`](docs/por-hacer.md): lo que queda.

## Licencia

El código va bajo MIT. Hasta octubre de 2026 la web la hacía un fork de
[Quartz](https://quartz.jzhao.xyz), de jackyzha0, también MIT; sigue en el
historial. Los textos de `content/` son míos, Copyright (c) 2026 Jorge García,
bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es).
Las carátulas son de sus autores y se usan en miniatura para identificar cada
obra. Las fuentes de `web/fuentes/` son de sus autores, bajo la SIL Open Font
License. El detalle, en `LICENSE.txt`.
