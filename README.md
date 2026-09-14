# Vitrina

Mi colección personal de juegos, películas, libros y discos, escrita en Obsidian
y publicada como web estática.

La idea era simple: llevaba años recomendando las mismas cosas por WhatsApp y
olvidándome de por qué me habían gustado. Quería un sitio donde apuntarlo una
vez, que se viera bien y que pudiera enlazar desde cualquier parte.

## Cómo funciona

Cada ficha es un fichero Markdown con unas pocas propiedades en la cabecera:

```yaml
---
tipo: juego                        # juego, peli, libro o album
seccion: "[[juegos/index|Juegos]]" # de qué sección cuelga; lo ponen los scripts
year: 2019
autor: ZA/UM                       # estudio, dirección, autor o artista
nota: 10                           # del 1 al 10
estado: terminado                  # pendiente, en curso, terminado, abandonado
favorito: true
portada: "[[disco-elysium.webp]]"  # fichero de assets/portadas/
tags:
  - rpg                            # siempre en inglés y sin tildes
---
```

Las galerías no están escritas a mano. Son *Bases* de Obsidian (`.base`), que
filtran y ordenan por esas propiedades, así que se actualizan solas en cuanto
añado una ficha. Cada sección tiene cuatro vistas: galería, tabla, favoritos y
lo que queda, que es su watchlist. La última sale del campo `estado`, salvo en
juegos: ahí Steam sabe cuántas horas les has echado y no si los terminaste, así
que el reparto va por las horas y la pestaña es *Por jugar*.

Lo que se ve en la web es exactamente lo mismo que veo en Obsidian, sin plugins
de terceros ni un segundo formato que mantener.

## Por qué está partido en tres

Al abrir la carpeta se ven tres cosas que parecen lo mismo y no lo son. El
reparto es siempre igual: **una fuente, unas vistas y un resultado**.

**`content/` es la vault: la fuente.** Markdown plano y unos cuantos campos en
la cabecera. Es lo único que se escribe a mano y lo único que importa de
verdad: si mañana desaparecieran Obsidian y Quartz, la colección seguiría
entera y legible en cualquier editor de texto. Por eso la nota no guarda ni
maquetación ni orden ni el HTML de una tarjeta, solo los datos.

**Los `.base` son las vistas.** Un `.base` no contiene fichas: contiene la
*pregunta* («dame todo lo que tenga `tipo: juego`, ordenado por nota, en
tarjetas de 220 px»). Están sueltos y no dentro de las notas justamente para que
se puedan cambiar sin tocar ni una ficha: cambiar el criterio de *Favoritos*, o
el orden de una galería, es editar un fichero, no ciento veintisiete. Y como es
un formato nativo de Obsidian, la misma vista se pinta igual en el editor y en
la web.

**`public/` es el resultado.** Lo escupe Quartz al construir y está en el
`.gitignore` a propósito: es material derivado, se regenera entero en cada
`build` y versionarlo solo serviría para llenar el historial de HTML. Se borra
sin miedo. En GitHub lo reconstruye la Action en cada push y lo sube a Pages; la
carpeta local es solo para verlo antes de publicar.

**`plugins/vitrina/` es lo que Quartz no trae**, y todo por lo mismo: para que
la maquetación siga fuera de las notas. Son tres cosas:

- La **cabecera de cada ficha**, que pinta la carátula, los datos y el enlace a
  la fuente leyendo el `tipo`, la `nota`, el `appid`… de la nota, sin escribir
  nada en ella. Y los enlaces que no están escritos en ninguna nota: de cada
  ficha a su autor, y de *Lo mejor de lo mejor* a cada uno de sus favoritos.
- El **grafo de la portada**, grande y entero, en vez de la vista pequeña de la
  barra. Y que el sitio abra en oscuro si no has elegido otra cosa.
- Sacar del buscador las cinco páginas sueltas que Quartz emite por cada
  `.base`, que eran una copia en blanco de la galería que ya está en el índice
  de su sección.

**`plugins/grafo/` es el grafo de Quartz con una línea cambiada**, la que decide
en qué página cree que está: sin ella, una sección dibujaba un punto suelto en
vez de su rama. Es un envoltorio de veinte líneas y el porqué está escrito
dentro; si algún día el plugin lo arregla por su cuenta, el `build` avisa y se
vuelve al de serie.

La otra carpeta grande, `quartz/`, es el generador: no es contenido, es el
programa. Este repo es un *fork* de Quartz con la vault dentro, que es como se
usa Quartz normalmente.

### Por qué Quartz y no otra cosa

- Entiende los enlaces `[[wiki]]`, los *callouts* y los `![[embeds]]` de
  Obsidian tal cual. Con Hugo o Jekyll habría que reescribir cada nota o meter
  un preprocesador.
- Es de los pocos generadores que renderizan los `.base`. Esto es lo que evita
  mantener las galerías dos veces.
- Sale un sitio estático: se publica gratis en GitHub Pages, no hay servidor ni
  base de datos que se caiga, y se puede llevar a cualquier otro alojamiento
  copiando `public/`.
- Trae ya hechos el buscador, el modo oscuro, el grafo, los *backlinks* y las
  previsualizaciones al pasar el ratón.

## Estructura

```
content/            la vault de Obsidian: lo único que se escribe a mano
  index.md          portada
  juegos/  pelis/  libros/  musica/
  autores/          derivadas: las escribe autores.py, no se tocan a mano
  *.base            las vistas de cada sección
  _plantillas/      plantilla de ficha (no se publica)
  assets/portadas/  imágenes
docs/
  importar.md       qué se puede sacar de cada fuente, y el flujo completo
scripts/
  nueva.py          busca una obra suelta y deja la ficha entera
  importar.py       vuelca de golpe Letterboxd, Steam, Spotify y ListenBrainz
  vitrina.py        lo que comparten todos los scripts
  portadas.py       baja las carátulas y rellena el campo `portada`
  datos.py          rellena año, autor y tags: Steam, Letterboxd, MusicBrainz
  textos.py         escribe el cuerpo: de qué va cada obra, y las canciones
  autores.py        conecta lo que comparte estudio, dirección o artista
  secciones.py      cuelga cada ficha de su sección: el campo `seccion`
  vistazo.py        levanta el sitio con los borradores dentro
  estado.py         qué hay, qué falta y qué se publica
  pruebas.py        las pruebas de todo lo anterior, sin red
requirements.txt    Pillow, lo único que los scripts piden fuera de la estándar
plugins/vitrina/    la cabecera de las fichas, el grafo de la portada y el tema
plugins/grafo/      el grafo de Quartz, sabiendo en qué página está
quartz.config.yaml  configuración del sitio: colores, tipografías y plugins
quartz/             el generador (fork de Quartz). De aquí solo se toca
                    styles/custom.scss, que son los retoques de estilo propios
public/             lo que genera el build; no se versiona
```

## Montarlo en otro ordenador

Hace falta [Node 22 o superior](https://nodejs.org), git y, para editar
cómodamente, [Obsidian](https://obsidian.md). Nada más: ni Docker, ni Ruby, ni
claves de API para arrancar.

```bash
git clone https://github.com/jorgeress/vitrina.git
cd vitrina
npm ci --ignore-scripts --include=optional
npm run install-plugins
npx quartz build --serve
```

Y ya está en <http://localhost:8080>, recargándose solo al guardar una nota.

Los dos detalles que no son evidentes:

- **`--ignore-scripts` no es opcional.** Sin él, `sharp` intenta compilarse
  desde el código fuente en vez de usar los binarios precompilados que ya vienen
  en las dependencias, y la instalación falla.
- **`install-plugins` va aparte de `npm ci`.** Los plugins de Quartz se leen de
  `quartz.config.yaml`, no del `package.json`, así que se instalan en un segundo
  paso. Si el sitio construye pero las galerías salen vacías o no aparece el
  grafo, es que falta este comando.

Para editar las notas: en Obsidian, `Abrir carpeta como almacén` apuntando a
`content/` (a `content/`, no a la raíz del repo). La configuración de la vault
viene versionada, así que las Bases funcionan desde el primer arranque.

### Publicarlo bajo tu propia cuenta

1. Haz un *fork* del repo, o clónalo y súbelo al tuyo.
2. En `quartz.config.yaml`, cambia `baseUrl` por `tuusuario.github.io/vitrina`.
3. En `Settings → Pages` del repo, pon *Source* en **GitHub Actions**.
4. Empuja a `main`. El workflow de `.github/workflows/deploy.yaml` revisa tipos
   y formato, pasa las pruebas de los scripts, construye y despliega solo.

El workflow se salta el despliegue mientras el repositorio sea privado, porque
Pages no está disponible en repos privados con el plan gratuito. En cuanto lo
pases a público se activa solo, sin tocar nada.

## Añadir una obra

Lo que se hace siempre es añadir la película de anoche, el disco de esta semana,
el juego que acabas de empezar. Eso es `scripts/nueva.py`, y funciona igual para
los cuatro tipos:

```bash
scripts/nueva.py juego "hollow knight"
scripts/nueva.py peli "parasite" --nota 10 --favorito
scripts/nueva.py album "in rainbows" --estado "en curso"
scripts/nueva.py libro "dune" --nota 9 --estado terminado
scripts/nueva.py libro "sapiens" --elegir 2     # sin preguntar
scripts/nueva.py peli "harakiri" --dry-run      # dice qué crearía
```

Enseña los candidatos, eliges tú, y guarda **el identificador** de lo que
elijas en vez del nombre. Cada tipo pregunta a la fuente que mejor lo conoce, y
ninguna pide clave:

| Tipo | Fuente | Guarda | Y trae |
| --- | --- | --- | --- |
| `juego` | Steam | `appid` | año, estudio y géneros |
| `peli` | Wikidata | `letterboxd` | año y dirección |
| `album` | MusicBrainz | `mbid` | año y artista |
| `libro` | Open Library | `coverid` | año y autor |

Con la obra elegida baja la portada en la misma pasada, así que la ficha sale
completa y no hay que pasar después ni `portadas.py` ni `datos.py`. Lo que la
fuente no puede saber es lo tuyo, y va en las opciones: `--nota`, `--estado`,
`--favorito`.

**Elegir a mano es el punto, no un trámite.** Open Library devuelve la edición
inglesa aunque busques en español, en Steam «Portal» saca antes el 2 que el 1 y
hay tres películas llamadas *Parasite*. Quedarse con el primero a ciegas es
exactamente lo que hace que una ficha acabe con los datos de otra obra. Con el
identificador guardado, la portada y los datos salen exactos y se pueden rehacer
siempre igual.

A mano también se puede, con la plantilla de `_plantillas/Ficha.md` (`Ctrl+P` →
*Insertar plantilla*) en la carpeta de su sección. En cuanto tenga `tipo`
aparece sola en la galería y en la tabla, y si lleva `favorito: true`, también
en *Lo mejor de lo mejor*. No hay que tocar ningún índice.

Los cómics y la novela gráfica entran como `tipo: libro`, que Open Library los
cataloga, **y el manga también**: se queda en libros con la etiqueta `manga` en
`tags` y no tiene sección propia. Un `.base` filtra por etiqueta igual de bien
que por carpeta, así que separarlos sería duplicar una sección entera para no
ganar nada.

## Traer lo que ya tienes en otros sitios

`scripts/importar.py` crea fichas a partir de Letterboxd, Steam y Spotify. No
pisa nunca una ficha que ya exista, así que se puede repetir cuando quieras para
recoger solo lo nuevo, y avisa cuando algo se parece a lo que ya tienes (el
*Witcher 3* de Steam se llama *The Witcher 3: Wild Hunt*, y esa la unes tú).

```bash
scripts/importar.py letterboxd-rss TU_USUARIO        # lo visto, sin cuenta de pago
scripts/importar.py letterboxd-watchlist TU_USUARIO  # lo que tienes por ver
scripts/importar.py letterboxd ~/Descargas/letterboxd-export.zip  # con Pro
scripts/importar.py steam ~/Descargas/juegos.html    # tu página de juegos
scripts/importar.py listenbrainz TU_USUARIO          # discos más escuchados
scripts/importar.py spotify-export ~/Descargas/spotify.zip
scripts/importar.py spotify-export ~/Descargas/spotify.zip --canciones
scripts/importar.py --dry-run letterboxd ...         # dice qué haría
```

**Todo entra en borrador**, con `draft: true` y el cuerpo en blanco. Quartz no
publica lo que lleva `draft`, así que la web sigue enseñando solo lo que hayas
ascendido a mano, mientras que en Obsidian se ven todas. Para ascender una ficha
se le quita la línea `draft` y se le pone nota y las dos frases del porqué, que
es lo único que estas fuentes no saben. Si prefieres que entren publicadas,
`--sin-borrador`.

Por defecto va en **modo rápido**: solo entra lo que da alguna señal de haberte
importado, 8 horas jugadas en Steam y 4 estrellas en Letterboxd. Lo que se queda
fuera se cuenta por pantalla, no desaparece en silencio, y con `--completo` entra
todo. Los umbrales se mueven con `--min-horas` y `--min-nota`. La watchlist es la
excepción y no pasa por la criba: ahí no hay señal que valga, porque nada de lo
que hay dentro lo has visto, y la lista entera es la señal. Entra como
`estado: pendiente`, que es lo que llena la pestaña *Por ver*.

| Fuente | Cómo | Qué trae |
| --- | --- | --- |
| Letterboxd | El RSS del perfil, o el export si tienes Pro | Título, año y **tu puntuación**, que pasa de estrellas a la escala de 1 a 10. La *watchlist* entra como `pendiente`. |
| Steam | Guardar `steamcommunity.com/my/games?tab=all` con `Ctrl+S`, o el export de datos | Título y horas jugadas, en el campo `horas`. |
| ListenBrainz | Tu nombre de usuario | Los discos más escuchados, con artista y el *mbid* de MusicBrainz. |
| Spotify | El zip del export | Lo mismo, desde tu historial. Con `--completo`, los álbumes guardados; con `--canciones`, tus me gusta plegados en los discos que los llevan. |

Después de importar quedan dos pasos, los dos de una pasada y sin clave:
`scripts/portadas.py` le pone carátula a todo lo nuevo, y `scripts/datos.py`
rellena lo que la fuente no supo decir.

**Nada de esto pide pagar, ni registrar una aplicación, ni una clave de API.**
Fue una decisión, no una casualidad: el export CSV de Letterboxd está detrás de
su cuenta Pro y la API de Spotify pide Premium desde febrero de 2026, así que
las dos se cambiaron por vías abiertas. Lo que da y lo que no da cada fuente está
en [`docs/importar.md`](docs/importar.md).

## Portadas

Las carátulas se guardan **como fichero, dentro de la vault**, en
`content/assets/portadas/`, y la ficha las referencia con un enlace de Obsidian:

```yaml
portada: "[[disco-elysium.webp]]"
```

Enlazar a la imagen de un servidor ajeno es más cómodo el primer día y peor
todos los demás: las URLs se pudren, muchos CDN bloquean el *hotlinking* y en
Obsidian, sin conexión, no se ve nada. Con el fichero dentro, la vault es
autocontenida. El formato es **WebP a 400 px de ancho**, entre 20 y 80 KB por
carátula: las tarjetas miden 220 px, así que 400 cubre pantallas 2x y de ahí
para arriba solo se malgasta ancho de banda.

El enlace va entre corchetes y no como ruta suelta a posta: así Obsidian lo
reconoce como enlace de verdad y lo renombra solo si mueves la imagen, y Quartz
lo resuelve desde cualquier página. Una ruta en texto plano se rompe en las
subcarpetas.

```bash
scripts/portadas.py                 # rellena las fichas que no tienen portada
scripts/portadas.py --seccion pelis # solo esa carpeta
scripts/portadas.py --force         # rehace también las que ya la tienen
scripts/portadas.py --dry-run       # dice qué haría, sin tocar nada
```

Cada sección tira de la fuente que mejor la conoce, y **ninguna pide clave**:

| Sección | Fuente |
| --- | --- |
| Juegos | Steam |
| Libros | Open Library (exacta, si la ficha trae `coverid`) |
| Música | MusicBrainz + Cover Art Archive |
| Películas | Letterboxd, identificada por Wikidata (Wikipedia de reserva) |

Las películas son el caso raro y conviene saberlo: no hay catálogo abierto de
carteles, así que el cartel sale de Letterboxd, pero **el identificador lo dice
Wikidata** (la propiedad `P6127`), porque la dirección de una película no se
deduce del título: `/film/parasite/` es la de Charles Band de 1982. Con ese id se
apunta en la ficha (`letterboxd: little-women-2019`) y ya no se vuelve a buscar.
Wikipedia queda de reserva para lo que Wikidata todavía no sepa identificar, que
en la práctica son los estrenos futuros, y de allí el póster llega a 220 px.

Si una ficha no se encuentra, lo más rápido es dejar la imagen a mano en
`assets/portadas/` y escribir el enlace en la cabecera. Y si una se queda sin
portada tampoco pasa nada: la tarjeta se pinta con un degradado y la rejilla no
se descuadra.

## Lo que la fuente no sabe

Lo importado entra con `year`, `autor` y `tags` en blanco: sin año la galería no
se ordena por fecha, y sin tags la página de etiquetas y el grafo se quedan
vacíos. Eso lo cierra `scripts/datos.py`, que sabe dónde está cada cosa:

| Sección | Fuente | Qué rellena |
| --- | --- | --- |
| Juegos | Ficha de la tienda de Steam | `year`, `autor` (el estudio) y `tags` |
| Películas | Ficha de Letterboxd | `autor`, o sea la dirección, y `tags` |
| Música | MusicBrainz | `tags`, tal como los da |
| Libros | Open Library | `tags`, los que reconozca una lista blanca de géneros |

```bash
scripts/datos.py                    # rellena solo lo que esté vacío
scripts/datos.py --force            # reescribe también lo que ya tenga valor
scripts/datos.py --seccion juegos   # solo esa carpeta
scripts/datos.py --dry-run          # dice qué pondría, sin tocar nada
scripts/datos.py content/juegos/Hollow\ Knight.md   # una ficha suelta
```

**La regla es no adivinar.** Todo va por el identificador que ya está en la
ficha, no por el título: buscar «PEAK» o «skate.» por nombre en Steam no
encuentra nada, y por `appid` sale siempre. Antes que rellenar una ficha con los
datos de otra obra, se queda vacía y lo dice. Y no pisa nada de lo que hayas
escrito tú: solo toca los campos vacíos, salvo con `--force`, y deja el resto de
la cabecera igual y en el mismo orden.

Los libros dan menos que el resto, y no es un fallo. Lo que Open Library llama
`subject` es la catalogación de una biblioteca: `L'étranger` trae sesenta, y ahí
dentro están revueltos el género («Philosophical Novels»), el tema («Murder») y
hasta el formato («Large type books»). Así que en vez de coger los primeros se
mira cuáles están en una lista blanca corta, `GENEROS_OPENLIBRARY`, y lo que no
esté no se escribe. La tabla es corta a propósito: cada vez que se le mete un
género blando («classics», «adventure stories») empieza a acertar en los libros
de género y a fallar en los demás. Si añades uno, las pruebas de
`GenerosDeLibro` son el sitio donde comprobarlo.

## Las etiquetas van en inglés, y todo en ASCII

De cada etiqueta sale una página, y de cada página una dirección. **Una tilde ahí
viaja escapada**: `tags/acción` se lee bien en la barra del navegador, pero por
dentro es `tags/acci%C3%B3n`, y eso es lo que se copia y se comparte. Pasaba con
`acción`, `fantasía`, `ciencia-ficción`, `animación` y `filosofía`, que venían de
traducir al castellano los géneros de Steam y de Letterboxd, y lo mismo con los
tres juegos del símbolo ™ y con *El madrileño*.

Así que **los tags van en inglés en las cuatro secciones**, que es como los dan
las cuatro fuentes: a Steam se le pide la ficha con `l=english` y las otras tres
no saben decirlos de otra manera. De propina sale lo que la traducción buscaba:
con una sola lengua, el `action` de un juego y el de una película son la misma
etiqueta sin que nadie traduzca nada.

**La regla, para lo que venga:** de un nombre de fichero y de una etiqueta sale
una dirección, así que las dos se quedan en ASCII. Lo garantizan
`nombre_de_fichero()` y `etiqueta()`, y lo vigilan dos pruebas que recorren la
vault entera. El título de verdad no se pierde: cuando el nombre del fichero no
puede ser igual que él, se apunta aparte en `title`, que es lo que pinta la web.
Por eso la ficha se llama `DARK SOULS REMASTERED.md` y la página sigue diciendo
*DARK SOULS™ REMASTERED*.

## De qué va cada cosa

Las fichas entraban con la cabecera completa y el cuerpo en blanco. El buscador
las encontraba por el título, pero abrir una era abrir nada. `scripts/textos.py`
lo cierra, sacando el texto de la misma fuente que ya identifica la ficha:

| Sección | Fuente | Qué escribe |
| --- | --- | --- |
| Juegos | Steam, por `appid` | la descripción corta de la tienda, en español |
| Películas | Wikipedia en español, por el `letterboxd` que resuelve Wikidata | el primer párrafo del artículo |
| Películas sin artículo | TMDB, por la ficha de Letterboxd | su sinopsis, en inglés |
| Música | MusicBrainz, por `mbid` | la lista de canciones del disco |
| Libros | ninguna todavía | hace falta un campo `wikipedia` en la ficha |

```bash
scripts/textos.py                    # solo las fichas que estén en blanco
scripts/textos.py --force            # reescribe también las que ya tengan texto
scripts/textos.py --seccion pelis    # solo esa carpeta
scripts/textos.py --dry-run          # dice qué haría, sin pedir ni tocar nada
```

**Lo tuyo va arriba y lo generado debajo**, en las cuatro secciones. No hay que
marcarlo con nada: escribes en el cuerpo, encima de la cita o de la lista de
canciones, y ya está.

```markdown
---
tipo: peli
---

Me reí con esta desde los catorce y no he parado.

> [!quote] De qué va
> Zoolander es una comedia cinematográfica estadounidense de 2001…
>
> → Wikipedia · CC BY-SA 4.0
```

`textos.py` **sólo pisa lo que ha escrito él**: el bloque de la cita, y la lista
de canciones de un disco desde su encabezado. Todo lo demás se conserva tal cual,
incluso con `--force`. La sinopsis se puede volver a bajar mil veces; tu párrafo
no, así que es lo único que el script no toca. Y el orden también es a propósito:
quien entra en una ficha lee primero por qué te gustó, que es para lo que existe
el sitio, y luego la referencia.

### Lo que no es tuyo va citado

- **Steam no da ninguna licencia.** Su descripción es texto suyo con todos los
  derechos, así que va como cita breve, marcada como tal y con enlace a su ficha
  de la tienda. La cita no es cortesía: es lo que la ampara.
- **Wikipedia es CC BY-SA 4.0**, que sí da permiso a cambio de nombrar a los
  autores, enlazar la fuente y decir la licencia. Se cumplen las tres con el
  enlace al artículo, cuyo historial es la lista de autores, y el nombre de la
  licencia enlazado.
- **MusicBrainz no pide nada.** Sus datos base son CC0, y una lista de títulos
  son datos, no prosa: no hay redacción de nadie que citar.

Lo que **no** se hace es parafrasear: reescribir un párrafo ajeno cambiando
cuatro palabras sigue siendo derivado de su texto, pero ya no parece una cita,
así que pierde también el amparo. Por eso el texto de fuera va en un *callout*
aparte y no suelto en el cuerpo.

En los discos, la lista lleva una estrella en tus favoritas y esa parte se lee
del fichero antes de reescribirla, porque es lo único de la ficha que no se puede
volver a buscar en ningún sitio. Los favoritos son **de disco entero**, con el
campo `favorito` como en las otras tres secciones; `favoritas` es solo cuántas
canciones tuyas hay en él, y los nombres viven en el cuerpo, que es donde los
encuentra el buscador de la web.

## De Vitrina cuelga todo

Una colección es, de partida, una nube de puntos sueltos. Una ficha no cita a
ninguna otra, y la galería de su sección tampoco la cita a ella, porque el
`![[Juegos.base]]` de `/juegos/` no es una lista de enlaces sino una pregunta que
se resuelve al pintar. Así que el grafo salía partido en dos: Vitrina con sus
secciones por un lado y las 127 fichas por otro, colgando sólo de sus etiquetas.

La arista que faltaba va escrita en la cabecera de cada ficha:

```yaml
seccion: "[[juegos/index|Juegos]]"
```

*Hollow Knight* cuelga de **Juegos**, Juegos cuelga de **Vitrina**, y las páginas
de autor cuelgan de **Autores** por el mismo campo. Un árbol, y el mismo en
Obsidian y en la web.

Va en la cabecera y no en el cuerpo porque dice de qué sección es la ficha, que
es un dato como el año o la nota, y no maquetación. Y va escrito en la nota, y no
puesto al construir como el enlace del autor, porque el grafo de Obsidian sólo
dibuja los `[[...]]` que están en la vault: un enlace que ponga el sitio al
generarse se ve en la web y allí no.

Nadie lo escribe a mano: lo ponen `nueva.py` e `importar.py` al crear la ficha,
porque lo dice la carpeta en la que cae. `scripts/secciones.py` es para las que
ya estaban, para una escrita a mano y para una que cambie de sección:

```bash
scripts/secciones.py            # escribe el campo en las que falte o esté mal
scripts/secciones.py --dry-run  # dice qué haría, sin tocar nada
scripts/secciones.py --deshacer # quita el campo de todas las fichas
```

Eso es el tronco, y un tronco solo no junta una peli con un juego. Lo que cruza
la colección son los otros dos hilos: las etiquetas y las páginas de autor.

## Lo que comparte estudio, dirección o artista

Obsidian agrupa por **enlaces**, no por campos: dos juegos con `autor:
FromSoftware` escrito exactamente igual no están conectados de ninguna manera.
`scripts/autores.py` escribe la página de cada autor con lo suyo listado, y el
sitio se encarga del enlace de vuelta:

```bash
scripts/autores.py             # escribe las páginas de autor
scripts/autores.py --minimo 1  # una página por autor, tenga una obra o veinte
scripts/autores.py --deshacer  # borra las páginas de autor
scripts/autores.py --dry-run   # dice qué haría, sin tocar nada
```

**El campo `autor` nunca lleva el enlace dentro**, ni siquiera cuando son dos:
es un dato, igual que el año o la nota. Quien pone el enlace es
`plugins/vitrina`, al pintar, buscando dentro del texto los nombres que tengan
página, y el mismo plugin las apunta en los `links` de la ficha para que el grafo
dibuje la arista. Así una ficha con varios autores los enlaza a todos, las
tarjetas de la galería no se rompen con un enlace dentro de otro, y `datos.py` y
`autores.py` no se pisan.

La coma del campo significa dos cosas a la vez, y ésa es la trampa:
`"Mike Johnson, Tim Burton"` son dos directores y `"FromSoftware, Inc."` es un
solo estudio. Lo que decide es si el trozo siguiente es un sufijo de empresa
(`Inc.`, `Ltd.`, `S.L.`…), y tiene prueba, por si algún día alguien lo
«simplifica»: partiendo por comas a secas, «Inc.» salía como el estudio con más
juegos de la colección.

**Sólo tiene página quien tenga dos obras o más.** De los 119 autores de esta
colección, repiten 13. Darle página a los otros 106 sería crear 106 callejones
sin salida. Al crecer la colección basta con volver a pasarlo: el que llegue a
dos la estrena solo. Las páginas de `content/autores/` son derivadas y se
reescriben enteras en cada pasada, así que no se editan a mano; el campo `autor`
sí es tuyo, y el script nunca cambia el nombre.

## Cómo se ve

El aspecto vive en dos sitios, y ninguno es una nota:

- **`quartz.config.yaml`**, en `theme`: los nueve colores de cada modo y las tres
  tipografías, que salen de Google Fonts. La paleta es una vitrina a oscuras con
  las piezas iluminadas (fondo casi negro con un punto cálido, texto hueso,
  enlaces en gris azulado frío) y los titulares van en **Cinzel**, la capital
  romana con la que se rotula una sala de museo. El claro va a juego, en papel.
- **`quartz/styles/custom.scss`**, para lo que no es un color: el rótulo
  «VITRINA» en capitales espaciadas, la portada con las secciones como renglones
  de un índice, y el dorado.

Tres cosas que conviene saber porque no se deducen del fichero:

- **El sitio abre en oscuro** salvo que hayas elegido claro con el botón. El
  script de Quartz le pregunta al sistema; esto se adelanta y apunta el oscuro
  cuando no hay ninguna elección guardada.
- **El dorado es de una sola página.** *Lo mejor de lo mejor* es la única que no
  es ni una sección ni una obra, así que va en dorado con su estrella, allá
  donde se la enlace, y las tarjetas de su galería llevan el mismo color. Por eso
  los enlaces normales son grises y no dorados: si todo fuera dorado, no se
  distinguiría.
- **La portada pinta el grafo entero**, grande y debajo del título, en vez de la
  vista pequeña de la barra. En las demás páginas sigue en la barra, al lado, y
  cada una dibuja lo suyo: una etiqueta, todo lo que la lleva cruzando secciones;
  una sección, su rama entera; *Lo mejor de lo mejor*, sus favoritos.

## Qué falta por rellenar

Las galerías enseñan lo que hay. Para saber por dónde seguir hace falta lo
contrario, que es lo que **no** hay:

```bash
scripts/estado.py                  # el resumen
scripts/estado.py --seccion pelis  # solo esa carpeta
scripts/estado.py --detalle        # además, qué ficha le falta cada cosa
```

```
FICHAS
              total  borrador  publicadas  con texto
  juegos         44         0          44         44
  pelis          37         0          37         37
  libros          9         0           9          8
  musica         37         0          37         37
             —————— ————————— ——————————— ——————————
  total         127         0         127        126

SIN RELLENAR
  nota         84   ████████················
  texto         1   ████████████████████████

FAVORITOS  ████····················  21 de 127
```

Avisa además de dos cosas que no se ven de otra manera: fichas que apuntan a una
imagen que ya no está, e imágenes en `assets/portadas/` que ya no usa ninguna
ficha. No consulta nada por red ni escribe nada, así que se puede lanzar cuando
sea.

## Verlo antes de ascender

Decidir qué asciendes mirando la web publicada no se puede, porque ahí todavía
no está: es justo lo que aún no has ascendido.

```bash
scripts/vistazo.py               # el sitio completo, borradores incluidos
scripts/vistazo.py --puerto 9000
scripts/vistazo.py --solo-build  # construye y no levanta nada
scripts/vistazo.py --tema rose-pine   # con ese tema de Obsidian, para verlo
```

Sale en <http://localhost:8081>, con las fichas en borrador dentro y un aviso en
la portada para que no lo confundas con el sitio de verdad, que sigue en el 8080.
No toca la vault: copia el contenido **fuera del repositorio**, le quita la línea
`draft` a la copia y construye desde ahí, así que ni cortándolo a mitad puede
acabar publicando un borrador. Es una foto fija: si tocas una ficha, vuelve a
lanzarlo.

## Las pruebas

```bash
python3 scripts/pruebas.py   # 64, sin salir a la red
npm run check                # tipos del plugin y formato del código
```

No cubren todo a propósito. Cubren dos cosas: las funciones que deciden si una
ficha se rellena o se queda vacía, que es donde un fallo es silencioso, y los
casos concretos que ya mordieron una vez, cada uno con su historia escrita al
lado. Además recorren la vault entera para que no se separe de lo que los
scripts esperan de ella: que ninguna ficha se invente un estado, que cada una
cuelgue de su sección, y que ni un nombre de fichero ni una etiqueta se salgan
del ASCII. El CI pasa las dos cosas en cada push, antes de construir.

## Licencia y créditos

El generador es [Quartz](https://quartz.jzhao.xyz), de jackyzha0, bajo licencia
MIT. Mis cambios sobre él van igual, bajo MIT.

Los textos de `content/` son míos, Copyright (c) 2026 Jorge García, bajo
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es):
cópialos y adáptalos citando de dónde salen y manteniendo la misma licencia.

El reparto completo está en `LICENSE.txt`.

Las carátulas son de sus respectivos autores y se usan en miniatura para
identificar cada obra. Vienen de [Open Library](https://openlibrary.org),
[Cover Art Archive](https://coverartarchive.org),
[Letterboxd](https://letterboxd.com), [Wikipedia](https://en.wikipedia.org) y
Steam.
