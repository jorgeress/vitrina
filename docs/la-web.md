# La web por dentro

Lo que hace cada página, las reglas de la vault y dónde está cada cosa. Para
copiarla, arrancarla y usarla basta el [README](../README.md).

## Lo que enseña

- **La entrada** lleva el rótulo y, debajo, la presentación, que es **el primer
  párrafo de `content/index.md`**: se cambia en Obsidian como cualquier nota.
  Después vienen las salas, los grupos destacados, **Lo mejor de lo mejor**
  (los `favorite: true`, de más nota a menos), las opiniones escritas, lo que
  está **en el almacén** (`status: pending`) y lo **recién llegado**.
- **Cada sala** tiene buscador, orden y filtros por estado, favoritos, opinión y
  tag, y se quedan en la dirección: `juegos/?tag=metroidvania` se puede enlazar.
  Lo `dropped` sale como *Retirado de la vitrina*, apagado. Ordenada **por
  décadas** (`pelis/?orden=decadas`), la sala se parte en «Años 90», «Años
  2000»…, con una línea del tiempo arriba que lleva a cada una.
- **Cada ficha** enseña sus fuentes, sus grupos, cuándo la terminaste, cuántas
  veces (`times`) y las seis piezas que más se le parecen, con el motivo: el
  mismo autor, o los tags que comparten (cuanto más raro el tag, más pesa).
  Debajo, lo que es **de la misma historia**: adaptaciones, secuelas y bandas
  sonoras, en los dos sentidos.
- **El color de la portada** tiñe la luz de su ficha y el filo de la opinión.
  Se calcula al construir: el tono que más pesa contando cuánto ocupa y cuánto
  color tiene. Una portada en blanco y negro deja la ficha sin tinte.
- **Sorpréndeme** (`/sorprendeme/`, el dado de la barra) saca una pieza al azar
  de esta vitrina o de la de otra persona, por sala, de lo que espera en el
  almacén o de lo mejor de lo mejor. Las vitrinas de tus amigos se pueden dejar
  a mano en `vitrine.config.json`:
  `"friends": [{ "name": "Ana", "url": "https://ana.github.io/vitrina/" }]`.
- **El anuario** (`/anuario/2024/`) junta lo que terminaste cada año
  (`finished_on`), lo que empezaste (`started_on`) y lo que entró en la vitrina
  (`added`), con lo mejor del año
  y sus opiniones. El año en que se abrió la vitrina lo dice: ese año entró todo
  de golpe.
- **La constelación** tiene tres niveles: las **salas**, unidas por lo que se
  parece de una a otra; los **géneros**, unidos cuando comparten obras; y las
  **obras**, cada una con sus tres más parecidas y las de su mismo autor. Se
  baja pulsando una burbuja (una sala, luego un género) y se sube con el botón.
  Lo que es de la misma historia (`based_on`, `follows`, `soundtrack`) va con
  flecha.
- **Cada ficha tiene su tarjeta para compartir**: al pegar su enlace en un chat
  sale una imagen con la portada, el título, la nota, la estrella y el
  principio de la opinión, con las letras de la casa. Se pintan al construir.
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
vitrine.local.json   tus cuentas para cuando.py; git no lo sube
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
.github/             el despliegue y los Issues de «Nueva pieza» y «Editar pieza»
```

## Pruebas

```bash
python3 scripts/pruebas.py   # sin red; también que no falte ninguna traducción
cd web
npm test                     # entre otras, que reparte los autores igual que autores.py
npm run check                # tipos, y con ellos el esquema de las fichas
```
