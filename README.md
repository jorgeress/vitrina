# Vitrina

Mi colección de juegos, películas, series, libros y discos, con lo que pienso
de cada uno. Se escribe en Obsidian y se publica como web estática.

**→ [jorgeress.github.io/vitrina](https://jorgeress.github.io/vitrina/)**

Cada obra es una ficha en Markdown. Las galerías, las tablas y las listas de
pendientes se generan solas a partir de los campos de la ficha, y se ven igual
en Obsidian que en la web.

## Arrancarlo

Hace falta [Node 22 o superior](https://nodejs.org), Python 3 y, para editar
cómodamente, [Obsidian](https://obsidian.md).

```bash
git clone https://github.com/jorgeress/vitrina.git
cd vitrina
npm ci --ignore-scripts --include=optional
npm run install-plugins
pip install -r requirements.txt
npx quartz build --serve       # http://localhost:8080
```

- Sin `--ignore-scripts`, `sharp` intenta compilarse y la instalación falla.
- Si el sitio construye pero las galerías salen vacías, falta `install-plugins`.

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

Valen los enlaces de Steam, Letterboxd, TVmaze, MusicBrainz, Open Library y los
discos de Spotify. Si buscas por título, te enseña los candidatos y eliges tú.
La ficha sale completa: portada, año, autor, géneros y el identificador de la
fuente.

Después escribe en la ficha, encima de la cita de «De qué va», por qué te
gustó. Es lo único que ningún script sabe poner.

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

Por qué me gustó.
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
para. Si la ficha no tiene nada tuyo escrito, después te pide la frase de por
qué, que va arriba del todo en la ficha. Guarda cada respuesta al momento.

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
fecha de alta, portada, año, autor, tags, texto, páginas de autor y las cifras
del README. Solo toca lo que falta, así que se puede lanzar siempre que quieras;
con `--sin-red` hace solo lo que no pregunta a nadie.

Para ver los borradores en el sitio antes de publicarlos, `scripts/vistazo.py`
(<http://localhost:8081>). Qué trae cada fuente está en
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
  tags          7   ███████████████████████·
  texto         2   ████████████████████████

FAVORITOS  ██······················  21 de 210
```

## La portada

Enseña las secciones y las **últimas 12 fichas añadidas**, ordenadas por el
campo `alta`, que llevan todas. Lo pone `nueva.py` al crear la ficha, y
`al-dia.py` a las escritas a mano. Abajo está el enlace al RSS del sitio.

## Publicar

Cada push a `main` pasa las pruebas y construye y publica el sitio en GitHub
Pages.

Para montarlo en tu cuenta:

1. Haz un *fork*.
2. En `quartz.config.yaml`, cambia `baseUrl` por `tuusuario.github.io/vitrina`.
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
plugins/vitrina/    la cabecera de cada ficha y el grafo de la portada
quartz.config.yaml  colores, tipografías y plugins del sitio
quartz/             el generador, un fork de Quartz
```

Todos los scripts y sus opciones están en [`docs/scripts.md`](docs/scripts.md).

## Pruebas

```bash
python3 scripts/pruebas.py   # sin red
npm run check                # tipos y formato
```

## Por hacer

- **Importar solo cada noche.** Una Action programada que pase
  `importar.py letterboxd-rss` y `listenbrainz` y después `al-dia.py`, y abra
  un PR con los borradores nuevos para revisarlos.

## Licencia

El generador es [Quartz](https://quartz.jzhao.xyz), de jackyzha0, bajo MIT, y
mis cambios también. Los textos de `content/` son míos, Copyright (c) 2026
Jorge García, bajo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es). Las
carátulas son de sus autores y se usan en miniatura para identificar cada obra.
El detalle, en `LICENSE.txt`.
