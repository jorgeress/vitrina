// Todos los textos de la interfaz, en español y en inglés. La vitrina sale en
// el idioma de vitrine.config.json (`language`); el contenido —las fichas, las
// cartelas— va en el que las escriba cada uno.
//
// Para añadir un idioma basta con otro objeto con la misma forma que `es`: el
// tipo `Textos` obliga a que no falte nada.
import { IDIOMA, NOMBRE, type Tipo } from "./config";

type Estado = "pending" | "in-progress" | "finished" | "dropped";

interface Sala {
  /** «Películas», en la barra y en la cabecera. */
  nombre: string;
  /** «Pelis», en las pestañas del móvil, donde no cabe más. */
  corto: string;
  /** «película» / «películas», para contar. */
  una: string;
  varias: string;
}

const es = {
  locale: "es-ES",
  og: "es_ES",
  /** Las direcciones de las páginas que no son salas. Las de las salas son
   * las carpetas de la vault. */
  rutas: {
    autores: "autores",
    tags: "tags",
    favoritos: "favoritos",
    buscar: "buscar",
    cifras: "cifras",
    comparar: "comparar",
    anadir: "anadir",
    constelacion: "constelacion",
    creditos: "creditos",
    grupos: "grupos",
    anuario: "anuario",
    sorprendeme: "sorprendeme",
  },
  salas: {
    game: { nombre: "Juegos", corto: "Juegos", una: "juego", varias: "juegos" },
    film: { nombre: "Películas", corto: "Pelis", una: "película", varias: "películas" },
    series: { nombre: "Series", corto: "Series", una: "serie", varias: "series" },
    book: { nombre: "Libros", corto: "Libros", una: "libro", varias: "libros" },
    album: { nombre: "Música", corto: "Música", una: "disco", varias: "discos" },
  } satisfies Record<Tipo, Sala>,
  /** Lo pendiente está «en el almacén», esperando su turno de salir; lo
   * abandonado se «retira de la vitrina». */
  estados: {
    finished: "Terminado",
    "in-progress": "En curso",
    pending: "En el almacén",
    dropped: "Retirado de la vitrina",
  } satisfies Record<Estado, string>,
  y: "y",
  /** «3 de 46 juegos». */
  de: "de",
  pieza: "pieza",
  piezas: "piezas",
  sala: "sala",
  salasPalabra: "salas",

  // --- la casa ---------------------------------------------------------------
  descripcion: "Lo que juego, veo, leo y escucho, y por qué está cada cosa en la vitrina.",
  saltar: "Saltar al contenido",
  inicio: "Inicio",
  aInicio: `${NOMBRE}, inicio`,
  secciones: "Secciones",
  mas: "Más",
  constelacion: "Constelación",
  mapa: "Mapa",
  buscar: "Buscar",
  buscarAtajo: "Buscar (/)",
  tema: "Cambiar entre claro y oscuro",
  temaCorto: "Claro u oscuro",
  mejor: "Lo mejor de lo mejor",
  autores: "Autores",
  tags: "Tags",
  cifras: "Cifras",
  comparar: "Comparar",
  sorprendeme: "Sorpréndeme",
  creditos: "Créditos",
  grupos: "Grupos",
  anuario: "Anuario",
  rssTitulo: `${NOMBRE}: recién llegadas`,
  vistazo:
    "Esto es el vistazo, no la web publicada: salen también los borradores, lo oculto y lo privado, marcados. Nada de esto se publica hasta que le quites la marca.",

  // --- marcas en las tarjetas -----------------------------------------------
  borrador: "Borrador",
  oculta: "Oculta",
  privada: "Privada",
  conCartelaTitulo: "Tiene cartela: está escrito por qué está aquí",
  nota: (n: number) => `Nota: ${n} de 10`,
  portadaDe: (t: string) => `Portada de ${t}`,
  retirada: (t: string) => `${t} · Retirado de la vitrina`,

  // --- la entrada -------------------------------------------------------------
  enLoMejor: "en lo mejor de lo mejor",
  lasSalas: "Las salas",
  constelacionSub: "Todas, unidas por lo que comparten",
  mejorSub: "Lo que no puede faltar, sala por sala.",
  verTodo: "Verlo todo →",
  cartelasTitulo: "Por qué están en la vitrina",
  cartelasSub: "Lo que he escrito yo, no lo que dice la contraportada.",
  almacen: "En el almacén",
  almacenSub: "Lo que espera su turno de salir a la vitrina.",
  recientes: "Recién llegadas a la vitrina",
  recientesSub: "Lo último que ha entrado, de cualquier sala.",
  gruposSub: "Colecciones que cruzan las salas, hechas a mano.",

  // --- una sala ---------------------------------------------------------------
  enLaVitrina: (cuenta: string) => `${cuenta} en la vitrina, con lo que pienso de cada uno.`,
  buscarEnSala: "Buscar por título o autor…",
  buscarEnSalaEtiqueta: "Buscar en esta sala",
  ordenar: "Ordenar",
  ordenes: {
    alta: "Lo último que entró",
    aprecio: "Lo mejor primero",
    nota: "Mejor nota",
    year: "Más nuevas",
    antiguas: "Más antiguas",
    titulo: "Por título",
    decadas: "Por décadas",
  },
  estado: "Estado",
  todo: "Todo",
  conCartela: "Con cartela",
  todosLosTags: "Todos los tags →",
  nadaConFiltros: "No hay nada con esos filtros.",
  quitarFiltros: "Quitar los filtros",

  // --- una ficha --------------------------------------------------------------
  cartelaTitulo: "Por qué está en la vitrina",
  deQueVa: "De qué va",
  desde: (fecha: string) => `En la vitrina desde ${fecha}`,
  terminadaEn: (fecha: string) => `Terminado en ${fecha}`,
  compartir: "Compartir",
  copiado: "Enlace copiado",
  conectada: "Conectada con",
  conectadaSub: "Lo que tiene en común con otras piezas de la vitrina.",
  enConstelacion: "Verla en la constelación →",
  tambienDe: (a: string) => `También de ${a}`,
  masDe: (s: string) => `Más de ${s}`,
  anterior: "← Anterior",
  siguiente: "Siguiente →",
  resumenFicha: (titulo: string, sala: string) => `${titulo}, en la sala de ${sala.toLowerCase()} de la vitrina.`,
  enGrupos: "En los grupos",
  /** «Vista 3 veces», con el verbo de cada sala. */
  veces: (tipo: Tipo, n: number) =>
    `${{ game: "Jugado", film: "Vista", series: "Vista", book: "Leído", album: "Escuchado" }[tipo]} ${n} veces`,
  escuchar: "▶ Escuchar aquí",
  verTrailer: "▶ Ver el tráiler",
  cerrar: "Cerrar",
  /** Hasta que se pulsa, la página no le pide nada a Spotify ni a YouTube. */
  alPulsar: (donde: string) => `Se carga de ${donde} al pulsar; antes, la página no le pide nada.`,
  mismaHistoria: "De la misma historia",
  mismaHistoriaSub: "Adaptaciones, secuelas y bandas sonoras que también están en la vitrina.",
  relaciones: {
    basadaEn: "Basada en",
    adaptadaEn: "Adaptada en",
    sigueA: "Continúa a",
    continuaEn: "Sigue en",
    bandaSonora: "Su banda sonora",
    bandaSonoraDe: "Banda sonora de",
  },

  // --- décadas, en las salas ------------------------------------------------------
  /** «Años 90», «Años 2010», «Años 1840». */
  decada: (d: number) => `Años ${d >= 1900 && d < 2000 ? String(d).slice(2) : d}`,
  sinAño: "Sin año",

  // --- sorpréndeme ----------------------------------------------------------------
  sorprendemeDescripcion: "Una pieza al azar, de esta vitrina o de la de otra persona.",
  sorprendemeSub:
    "Una pieza al azar, de aquí o de la vitrina de otra persona, para cuando no sabes qué volver a ver, jugar, leer o escuchar.",
  deAqui: "De esta vitrina",
  deOtra: "De otra vitrina",
  cualquierSala: "Cualquier sala",
  soloAlmacen: "Solo lo que espera en el almacén",
  soloMejor: "Solo lo mejor de lo mejor",
  otraVez: "Otra",
  azar: {
    mirando: "Mirando su vitrina…",
    noEncuentro: "No encuentro una vitrina en {d}. Tiene que ser una web hecha con Vitrine, que publica su colección en vitrine.json.",
    nada: "No hay ninguna pieza con eso.",
    de: "De {nombre}",
    verFicha: "Ver su ficha →",
  },

  // --- lo mejor, autores, tags ---------------------------------------------------
  mejorDescripcion: "Lo que no puede faltar en la vitrina, sala por sala.",
  mejorCuenta: (cuenta: string) => `${cuenta} que no pueden faltar, sala por sala.`,
  enSuSala: "En su sala →",
  autoresSub: "Quien firma más de una pieza de la vitrina.",
  loQueTengoDe: (a: string) => `Lo que tengo de ${a} en la vitrina.`,
  enLaVitrinaDesde: (cuenta: string, desde: number, hasta: number) =>
    `${cuenta} en la vitrina${desde < hasta ? `, de ${desde} a ${hasta}` : ""}.`,
  tagsDescripcion: "Los géneros de la vitrina, de los que más se repiten a los que menos.",
  tagsSub: "Los géneros de todas las salas. Cuanto más grande, más piezas lo comparten.",
  conElTag: (cuenta: string, tag: string) => `${cuenta} de la vitrina con el tag ${tag}.`,
  enSalas: (piezas: string, salas: string) => `${piezas} en ${salas}.`,

  // --- grupos -------------------------------------------------------------------
  gruposDescripcion: "Las colecciones que cruzan las salas: las hago yo, no las fuentes.",
  gruposVacio:
    "Todavía no hay ninguno. Un grupo se crea con una nota en la carpeta de grupos de la vault, y una ficha entra en él con `groups: [Nombre]`.",
  grupoCuenta: (cuenta: string) => `${cuenta} en este grupo.`,

  // --- anuario -------------------------------------------------------------------
  anuarioDescripcion: "La vitrina año a año: lo que terminé y lo que entró cada año.",
  anuarioSub: "Lo que terminé y lo que entró en la vitrina, año a año.",
  anuarioVacio:
    "Todavía no hay ningún año. Sale en cuanto una ficha lleva `finished_on`, o entra algo nuevo en la vitrina.",
  añoTitulo: (y: number) => `${y} en la vitrina`,
  añoDescripcion: (y: number) => `Lo que terminé y lo que entró en la vitrina en ${y}.`,
  terminadas: "Lo que terminé",
  terminadasSub: (cuenta: string) => `${cuenta}, por la fecha de \`finished_on\`.`,
  entraron: "Lo que entró en la vitrina",
  entraronSub: (cuenta: string) => `${cuenta}, por la fecha de alta.`,
  apertura:
    "El año en que se abrió la vitrina: entró de golpe todo lo que ya tenía, así que esta lista es la colección de partida más que lo de ese año.",
  mejoresDelAño: "Lo mejor del año",
  resumenAño: (terminadas: number, entraron: number) =>
    [terminadas && `${terminadas} terminadas`, entraron && `${entraron} nuevas en la vitrina`].filter(Boolean).join(" · "),
  añoAnterior: "← Año anterior",
  añoSiguiente: "Año siguiente →",

  // --- cifras ---------------------------------------------------------------------
  cifrasDescripcion: "La vitrina en números: de qué épocas es, qué notas pongo y qué géneros se repiten.",
  cifrasTitulo: "La vitrina en cifras",
  deA: (a: number, b: number, salas: number) => `De ${a} a ${b}, en ${salas} salas.`,
  conNota: "con nota",
  autoresQueRepiten: "autores que repiten",
  epocas: "De qué época es cada sala",
  epocasSub: "Piezas por década del año de salida, todas con la misma escala.",
  antesDe: (y: number) => `La primera columna junta todo lo anterior a ${y}.`,
  porDecada: (s: string) => `${s} por década`,
  lasNotas: "Las notas",
  notasSub: (puntuadas: number, dieces: number) =>
    `${puntuadas} piezas puntuadas, y ${dieces} son un 10: la nota no separa mucho, por eso existe lo mejor de lo mejor.`,
  porNota: "Piezas por nota",
  quienSeRepite: "Quién se repite",
  quienSeRepiteSub: "Los autores con más piezas en la vitrina.",
  porAutor: "Piezas por autor",
  generos: "Los géneros que más se repiten",
  generosSub: "Contando todas las salas juntas.",
  porTag: "Piezas por tag",
  verTabla: "Ver como tabla",

  // --- buscar ---------------------------------------------------------------------
  buscarDescripcion: "Buscar en todas las salas de la vitrina.",
  buscarSub: "En todas las salas: títulos, autores, cartelas y de qué va cada pieza.",
  sinIndice:
    "El índice del buscador se crea al construir la web (npm run build), así que con npm run dev no hay nada que buscar todavía.",

  // --- comparar -------------------------------------------------------------------
  compararTitulo: "Comparar vitrinas",
  compararDescripcion: "Pon la dirección de otra vitrina y mira qué tenéis en común.",
  compararSub:
    "Pon la dirección de otra vitrina, o su fichero vitrine.json, y mira qué tenéis en común, dónde no estáis de acuerdo y qué hay allí que no está aquí.",
  direccionOtra: "Dirección de la otra vitrina",
  oFichero: "o un fichero",
  compararBoton: "Comparar",
  mejorDeLosDos: "Lo mejor de los dos",
  compartis: "Lo que compartís",
  desacuerdos: "Donde no estáis de acuerdo",
  desacuerdosSub: "Puntuadas en las dos vitrinas, con tres puntos o más de diferencia.",
  deAlli: "Lo de allí que no está aquí",
  deAlliSub: "Lo mejor de allí primero: por dónde empezar.",
  // Los del navegador van en un objeto aparte: se pasan a la página como JSON.
  cliente: {
    noEsDireccion: "Esa dirección no parece una dirección web.",
    mirando: "Mirando su vitrina…",
    noEncuentro: (d: string) =>
      `No encuentro una vitrina en ${d}. Tiene que ser una web hecha con Vitrine, que publica su colección en vitrine.json.`,
    noEsFichero: "Ese fichero no es el vitrine.json de ninguna vitrina.",
    unaPieza: "1 pieza",
    nPiezas: "{n} piezas",
    resumen:
      "{comunes} en común de {total} entre las dos vitrinas. Aquí hay {mias} que no {estanMias} allí, y allí {suyas} que no {estanSuyas} aquí.",
    esta: "está",
    estan: "están",
    enLasDos: "★ en las dos",
    aqui: "aquí",
    alli: "allí",
    deLoMejorDeAlli: "★ de lo mejor de allí",
    un: "un {n}",
  },

  // --- añadir -----------------------------------------------------------------------
  anadirTitulo: "Añadir una pieza",
  anadirDescripcion: "Añadir una obra a la vitrina desde su enlace.",
  anadirSub:
    "Pega el enlace de la obra y se abre el formulario del Issue con él ya puesto. Al enviarlo, la ficha se crea y se publica sola. Solo funciona con la cuenta dueña de la vitrina.",
  enlaceObra: "Enlace de la obra",
  seguirGitHub: "Seguir en GitHub →",
  anadirNota: `Con la web instalada como app en Android, ${NOMBRE} sale en el menú de Compartir: compartir un enlace desde Letterboxd, Steam o Spotify trae directamente aquí.`,
  plantillaIssue: "nueva-pieza.yml",

  // --- avisos ---------------------------------------------------------------------
  sinConexion: "Sin conexión",
  sinConexionTitulo: "Esta sala no la tengo guardada",
  sinConexionTexto: "Las páginas que ya has visitado se abren sin red; esta todavía no. Vuelve a probar cuando haya conexión.",
  irEntrada: "Ir a la entrada →",
  vacia: "Esta vitrina está vacía",
  vaciaTexto: "Lo que había aquí ha cambiado de sala, o el enlace no lleva a ninguna parte.",
  buscarlo: "Buscarlo",
  irEntradaCorto: "Ir a la entrada",

  // --- constelación -----------------------------------------------------------------
  constelacionDescripcion: "Las obras de la vitrina como un mapa: cada una unida a las que más se le parecen.",
  constelacionLienzo: "Grafo de las obras de la vitrina y lo que tienen en común",
  constelacionTexto: (n: number) =>
    `Cada punto es una de las ${n} obras, y cada línea une las que comparten autor o algo que las hace parecidas. Las discontinuas solo comparten sección y época, y los discos son cuadrados. Arrastra para moverte y usa la rueda para acercarte.`,
  buscarObra: "Buscar una obra…",

  // --- tarjeta para compartir ------------------------------------------------------
  tarjeta: {
    mejor: "★ Lo mejor de lo mejor",
    de10: "/10",
  },

  // --- RSS y manifest ------------------------------------------------------------------
  rssDescripcion: "Lo que va entrando en la vitrina: juegos, películas, series, libros y discos.",
};

export type Textos = typeof es;

const en: Textos = {
  locale: "en-GB",
  og: "en_GB",
  rutas: {
    autores: "authors",
    tags: "tags",
    favoritos: "best",
    buscar: "search",
    cifras: "stats",
    comparar: "compare",
    anadir: "add",
    constelacion: "constellation",
    creditos: "credits",
    grupos: "groups",
    anuario: "yearbook",
    sorprendeme: "surprise-me",
  },
  salas: {
    game: { nombre: "Games", corto: "Games", una: "game", varias: "games" },
    film: { nombre: "Films", corto: "Films", una: "film", varias: "films" },
    series: { nombre: "Series", corto: "Series", una: "series", varias: "series" },
    book: { nombre: "Books", corto: "Books", una: "book", varias: "books" },
    album: { nombre: "Music", corto: "Music", una: "album", varias: "albums" },
  },
  // Lo pendiente está «in storage», como lo que un museo no tiene expuesto;
  // lo abandonado, «off display».
  estados: {
    finished: "Finished",
    "in-progress": "In progress",
    pending: "In storage",
    dropped: "Off display",
  },
  y: "and",
  de: "of",
  pieza: "piece",
  piezas: "pieces",
  sala: "room",
  salasPalabra: "rooms",

  descripcion: "What I play, watch, read and listen to, and why each piece is on display.",
  saltar: "Skip to content",
  inicio: "Home",
  aInicio: `${NOMBRE}, home`,
  secciones: "Sections",
  mas: "More",
  constelacion: "Constellation",
  mapa: "Map",
  buscar: "Search",
  buscarAtajo: "Search (/)",
  tema: "Switch between light and dark",
  temaCorto: "Light or dark",
  mejor: "The best of the best",
  autores: "Authors",
  tags: "Tags",
  cifras: "Stats",
  comparar: "Compare",
  sorprendeme: "Surprise me",
  creditos: "Credits",
  grupos: "Groups",
  anuario: "Yearbook",
  rssTitulo: `${NOMBRE}: just arrived`,
  vistazo:
    "This is the preview, not the published site: drafts, hidden and private pieces show up too, marked. None of them is published until you remove the mark.",

  borrador: "Draft",
  oculta: "Hidden",
  privada: "Private",
  conCartelaTitulo: "Has a label: it says why it is here",
  nota: (n) => `Rating: ${n} out of 10`,
  portadaDe: (t) => `Cover of ${t}`,
  retirada: (t) => `${t} · Off display`,

  enLoMejor: "in the best of the best",
  lasSalas: "The rooms",
  constelacionSub: "All of them, joined by what they share",
  mejorSub: "What can't be missing, room by room.",
  verTodo: "See all →",
  cartelasTitulo: "Why they are on display",
  cartelasSub: "What I wrote, not what the back cover says.",
  almacen: "In storage",
  almacenSub: "Waiting for their turn on display.",
  recientes: "Just arrived",
  recientesSub: "The latest to come in, from any room.",
  gruposSub: "Hand-made collections that cross the rooms.",

  enLaVitrina: (cuenta) => `${cuenta} on display, with what I think of each.`,
  buscarEnSala: "Search by title or author…",
  buscarEnSalaEtiqueta: "Search this room",
  ordenar: "Sort",
  ordenes: {
    alta: "Latest in",
    aprecio: "Best first",
    nota: "Highest rated",
    year: "Newest",
    antiguas: "Oldest",
    titulo: "By title",
    decadas: "By decade",
  },
  estado: "Status",
  todo: "All",
  conCartela: "With a label",
  todosLosTags: "All tags →",
  nadaConFiltros: "Nothing matches those filters.",
  quitarFiltros: "Clear the filters",

  cartelaTitulo: "Why it's on display",
  deQueVa: "What it's about",
  desde: (fecha) => `On display since ${fecha}`,
  terminadaEn: (fecha) => `Finished in ${fecha}`,
  compartir: "Share",
  copiado: "Link copied",
  conectada: "Connected to",
  conectadaSub: "What it has in common with other pieces on display.",
  enConstelacion: "See it in the constellation →",
  tambienDe: (a) => `Also by ${a}`,
  masDe: (s) => `More ${s}`,
  anterior: "← Previous",
  siguiente: "Next →",
  resumenFicha: (titulo, sala) => `${titulo}, in the ${sala.toLowerCase()} room.`,
  enGrupos: "In the groups",
  veces: (tipo, n) => `${{ game: "Played", film: "Watched", series: "Watched", book: "Read", album: "Listened to" }[tipo]} ${n} times`,
  escuchar: "▶ Listen here",
  verTrailer: "▶ Watch the trailer",
  cerrar: "Close",
  alPulsar: (donde) => `Loads from ${donde} when pressed; until then, the page asks it for nothing.`,
  mismaHistoria: "Part of the same story",
  mismaHistoriaSub: "Adaptations, sequels and soundtracks that are on display too.",
  relaciones: {
    basadaEn: "Based on",
    adaptadaEn: "Adapted as",
    sigueA: "Follows",
    continuaEn: "Continues in",
    bandaSonora: "Its soundtrack",
    bandaSonoraDe: "Soundtrack of",
  },

  decada: (d) => `${d}s`,
  sinAño: "No year",

  sorprendemeDescripcion: "A random piece, from this display or someone else's.",
  sorprendemeSub: "A random piece, from here or from someone else's display, for when you don't know what to watch, play, read or listen to again.",
  deAqui: "From this display",
  deOtra: "From another display",
  cualquierSala: "Any room",
  soloAlmacen: "Only what's waiting in storage",
  soloMejor: "Only the best of the best",
  otraVez: "Another",
  azar: {
    mirando: "Looking at their display…",
    noEncuentro: "I can't find a display at {d}. It has to be a site made with Vitrine, which publishes its collection in vitrine.json.",
    nada: "There's no piece like that.",
    de: "From {nombre}",
    verFicha: "See its page →",
  },

  mejorDescripcion: "What can't be missing from the display, room by room.",
  mejorCuenta: (cuenta) => `${cuenta} that can't be missing, room by room.`,
  enSuSala: "In its room →",
  autoresSub: "Whoever signs more than one piece on display.",
  loQueTengoDe: (a) => `What I have by ${a} on display.`,
  enLaVitrinaDesde: (cuenta, desde, hasta) => `${cuenta} on display${desde < hasta ? `, from ${desde} to ${hasta}` : ""}.`,
  tagsDescripcion: "The genres on display, from the most to the least repeated.",
  tagsSub: "The genres of every room. The bigger, the more pieces share it.",
  conElTag: (cuenta, tag) => `${cuenta} on display tagged ${tag}.`,
  enSalas: (piezas, salas) => `${piezas} in ${salas}.`,

  gruposDescripcion: "Collections that cross the rooms: I make them, not the sources.",
  gruposVacio:
    "There are none yet. A group is a note in the groups folder of the vault, and a piece joins it with `groups: [Name]`.",
  grupoCuenta: (cuenta) => `${cuenta} in this group.`,

  anuarioDescripcion: "The display year by year: what I finished and what came in each year.",
  anuarioSub: "What I finished and what came in, year by year.",
  anuarioVacio: "There are no years yet. One appears as soon as a piece has `finished_on`, or something new comes in.",
  añoTitulo: (y) => `${y} on display`,
  añoDescripcion: (y) => `What I finished and what came in in ${y}.`,
  terminadas: "What I finished",
  terminadasSub: (cuenta) => `${cuenta}, by their \`finished_on\` date.`,
  entraron: "What came in",
  entraronSub: (cuenta) => `${cuenta}, by the date they were added.`,
  apertura:
    "The year the display opened: everything already owned came in at once, so this list is the starting collection more than that year's.",
  mejoresDelAño: "Best of the year",
  resumenAño: (terminadas, entraron) =>
    [terminadas && `${terminadas} finished`, entraron && `${entraron} new on display`].filter(Boolean).join(" · "),
  añoAnterior: "← Previous year",
  añoSiguiente: "Next year →",

  cifrasDescripcion: "The display in numbers: which eras, which ratings and which genres repeat.",
  cifrasTitulo: "The display in numbers",
  deA: (a, b, salas) => `From ${a} to ${b}, in ${salas} rooms.`,
  conNota: "rated",
  autoresQueRepiten: "authors who repeat",
  epocas: "Which era each room is from",
  epocasSub: "Pieces per decade of release, all on the same scale.",
  antesDe: (y) => `The first column groups everything before ${y}.`,
  porDecada: (s) => `${s} per decade`,
  lasNotas: "Ratings",
  notasSub: (puntuadas, dieces) =>
    `${puntuadas} rated pieces, and ${dieces} are a 10: ratings don't separate much, which is why the best of the best exists.`,
  porNota: "Pieces per rating",
  quienSeRepite: "Who repeats",
  quienSeRepiteSub: "The authors with the most pieces on display.",
  porAutor: "Pieces per author",
  generos: "The most repeated genres",
  generosSub: "Counting every room together.",
  porTag: "Pieces per tag",
  verTabla: "Show as a table",

  buscarDescripcion: "Search every room of the display.",
  buscarSub: "In every room: titles, authors, labels and what each piece is about.",
  sinIndice:
    "The search index is made when the site is built (npm run build), so with npm run dev there is nothing to search yet.",

  compararTitulo: "Compare displays",
  compararDescripcion: "Enter the address of another display and see what you have in common.",
  compararSub:
    "Enter the address of another display, or its vitrine.json file, and see what you share, where you disagree and what they have that isn't here.",
  direccionOtra: "Address of the other display",
  oFichero: "or a file",
  compararBoton: "Compare",
  mejorDeLosDos: "The best of both",
  compartis: "What you share",
  desacuerdos: "Where you disagree",
  desacuerdosSub: "Rated on both displays, three points or more apart.",
  deAlli: "What they have that isn't here",
  deAlliSub: "Their best first: where to start.",
  cliente: {
    noEsDireccion: "That doesn't look like a web address.",
    mirando: "Looking at their display…",
    noEncuentro: (d) => `There's no display at ${d}. It has to be a site made with Vitrine, which publishes its collection in vitrine.json.`,
    noEsFichero: "That file isn't the vitrine.json of any display.",
    unaPieza: "1 piece",
    nPiezas: "{n} pieces",
    resumen:
      "{comunes} in common out of {total} between both displays. There are {mias} here that {estanMias} not there, and {suyas} there that {estanSuyas} not here.",
    esta: "is",
    estan: "are",
    enLasDos: "★ on both",
    aqui: "here",
    alli: "there",
    deLoMejorDeAlli: "★ among their best",
    un: "a {n}",
  },

  anadirTitulo: "Add a piece",
  anadirDescripcion: "Add a work to the display from its link.",
  anadirSub:
    "Paste the link of the work and the Issue form opens with it already filled in. When you send it, the entry is created and published on its own. It only works for the account that owns the display.",
  enlaceObra: "Link to the work",
  seguirGitHub: "Continue on GitHub →",
  anadirNota: `With the site installed as an app on Android, ${NOMBRE} shows up in the Share menu: sharing a link from Letterboxd, Steam or Spotify brings you straight here.`,
  plantillaIssue: "new-piece.yml",

  sinConexion: "Offline",
  sinConexionTitulo: "This room isn't saved",
  sinConexionTexto: "Pages you've already visited open without a connection; this one doesn't yet. Try again when you're back online.",
  irEntrada: "Go to the entrance →",
  vacia: "This case is empty",
  vaciaTexto: "Whatever was here has moved rooms, or the link leads nowhere.",
  buscarlo: "Search for it",
  irEntradaCorto: "Go to the entrance",

  constelacionDescripcion: "The works on display as a map: each joined to the ones most like it.",
  constelacionLienzo: "Graph of the works on display and what they have in common",
  constelacionTexto: (n) =>
    `Each dot is one of the ${n} works, and each line joins those that share an author or something that makes them alike. Dashed lines only share a room and an era, and albums are squares. Drag to move and scroll to zoom.`,
  buscarObra: "Find a work…",

  tarjeta: {
    mejor: "★ The best of the best",
    de10: "/10",
  },

  rssDescripcion: "What comes into the display: games, films, series, books and albums.",
};

export const t: Textos = IDIOMA === "es" ? es : en;
export const DICCIONARIOS = { es, en };
export type { Estado };
