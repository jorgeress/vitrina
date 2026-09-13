import { h } from "preact"
import { transformLink } from "@quartz-community/utils/path"

/**
 * La cabecera de una ficha: la caratula y los datos de la obra.
 *
 * Es la mitad que faltaba del catalogo. La galeria ya enseñaba portada, autor y
 * año en cada tarjeta, pero al entrar en una ficha no quedaba nada de eso: solo
 * el titulo y el parrafo de "De que va". Los datos estaban en la cabecera del
 * Markdown y no se pintaban en ninguna parte, y los identificadores de la
 * fuente (`appid`, `letterboxd`, `mbid`, `wikipedia`) se guardaban desde el
 * primer dia sin que nadie pudiera pinchar en ellos.
 *
 * Esto los lee y no los guarda: la ficha sigue teniendo solo datos, y la
 * maquetacion sigue viviendo fuera de la nota, igual que un `.base`.
 */

// Lo que cambia de un tipo a otro: como se llama quien la firma y a donde se
// enlaza. El identificador nunca se adivina; si la ficha no lo tiene, no hay
// enlace y ya esta.
const TIPOS = {
  juego: {
    autor: "Estudio",
    enlace: (f) => f.appid && ["Ficha en Steam", `https://store.steampowered.com/app/${f.appid}/`],
  },
  peli: {
    autor: "Dirección",
    enlace: (f) =>
      f.letterboxd && ["Ficha en Letterboxd", `https://letterboxd.com/film/${f.letterboxd}/`],
  },
  libro: {
    autor: "Autor",
    // `coverid` identifica la portada, no la obra, asi que no sirve de enlace.
    // Los libros llevan ademas el nombre del articulo de Wikipedia, que si.
    enlace: (f) =>
      f.wikipedia && [
        "Artículo en Wikipedia",
        `https://es.wikipedia.org/wiki/${encodeURIComponent(String(f.wikipedia).replace(/ /g, "_"))}`,
      ],
  },
  album: {
    autor: "Artista",
    // `mbid` es el id del release-group, que es la pagina del disco.
    enlace: (f) =>
      f.mbid && ["Ficha en MusicBrainz", `https://musicbrainz.org/release-group/${f.mbid}`],
  },
}

const ESTADOS = {
  pendiente: "Pendiente",
  "en curso": "En curso",
  terminado: "Terminado",
  abandonado: "Abandonado",
}

const WIKILINK = /^\[\[([^\]|]+)(?:\|([^\]]+))?\]\]$/

/** ¿Hay algo? `nota: ` vacia llega como null, y `horas: 0` es un cero de verdad. */
const hay = (v) => v !== undefined && v !== null && v !== ""

/**
 * Las paginas de autor que hay, de nombre mas largo a mas corto.
 *
 * `autores.py` escribe una por cada firma con dos obras o mas, y el titulo de
 * la pagina es el nombre exacto: "FromSoftware, Inc.". De ahi sale el mapa.
 *
 * El orden importa y es la mitad del truco de `nombresEnTexto`: si algun dia
 * hay pagina de "FromSoftware" y de "FromSoftware, Inc.", la larga tiene que
 * probarse antes o la corta se lleva media firma por delante.
 */
export function paginasDeAutor(allFiles) {
  return allFiles
    .filter((file) => {
      const slug = String(file.slug ?? "")
      // El indice de la carpeta lo fabrica folder-page y se titula "Autores":
      // no es la firma de nadie.
      return slug.startsWith("autores/") && !slug.endsWith("/index")
    })
    .map((file) => [String(file.frontmatter?.title ?? ""), file.slug])
    .filter(([nombre]) => nombre !== "")
    .sort((a, b) => b[0].length - a[0].length)
}

/** Lo que separa una firma de la siguiente dentro del campo `autor`. */
const SEPARADOR = /[,;/&()]/

/**
 * El campo `autor` -> los trozos que lo forman, diciendo cuales tienen pagina.
 *
 * Devuelve una lista de `[texto, slug | null]` en el orden en que se leen, para
 * que quien la use pinte el enlace o lo apunte en el grafo.
 *
 * Va buscando nombres dentro del texto en vez de partirlo por comas, porque por
 * comas no se puede: la coma separa en "Mike Johnson, Tim Burton" y no separa
 * en "FromSoftware, Inc.". `autores.py` resuelve eso con una lista de sufijos
 * de empresa; aqui no hace falta ninguna heuristica, porque los nombres que
 * importan -- los que tienen pagina -- se conocen enteros y exactos.
 *
 * Asi "QLOC, FromSoftware, Inc." sale como "QLOC, " en texto y "FromSoftware,
 * Inc." enlazado, que es justo lo que se quiere de una ficha con dos autores.
 */
export function nombresEnTexto(valor, paginas) {
  const texto = String(valor).trim()
  const trozos = []
  let suelto = ""
  let i = 0

  // Un nombre solo cuenta si ocupa una firma entera: del principio del campo o
  // de detras de un separador, hasta el final o hasta el siguiente. El espacio
  // a secas no abre firma, o una pagina llamada "Burton" se llevaria el
  // apellido de "Tim Burton".
  const abre = (pos) => {
    const antes = texto.slice(0, pos).trimEnd()
    return antes === "" || SEPARADOR.test(antes[antes.length - 1])
  }
  const cierra = (pos) => {
    const despues = texto.slice(pos).trimStart()
    return despues === "" || SEPARADOR.test(despues[0])
  }

  while (i < texto.length) {
    const candidato = abre(i)
      ? paginas.find(([nombre]) => texto.startsWith(nombre, i) && cierra(i + nombre.length))
      : undefined
    if (candidato) {
      if (suelto) trozos.push([suelto, null])
      suelto = ""
      trozos.push([candidato[0], candidato[1]])
      i += candidato[0].length
    } else {
      suelto += texto[i]
      i += 1
    }
  }
  if (suelto) trozos.push([suelto, null])
  return trozos
}

/**
 * `autor` es siempre texto plano -- "Albert Camus", "QLOC, FromSoftware, Inc."
 * --, porque en la ficha es un dato y no maquetacion. El enlace a la pagina de
 * autor se pone aqui, al pintar, y solo para los nombres que tengan una.
 */
function autor(valor, slug, allSlugs, paginas) {
  return nombresEnTexto(valor, paginas).map(([trozo, destino]) =>
    destino
      ? h(
          "a",
          {
            href: transformLink(slug, destino, { strategy: "shortest", allSlugs }),
            class: "internal",
          },
          trozo,
        )
      : trozo,
  )
}

/** De "[[elden-ring.webp]]" al fichero, que vive siempre en assets/portadas/. */
function portada(valor, slug) {
  const m = String(valor).trim().match(WIKILINK)
  if (!m) return null
  const fichero = m[1].split("/").pop()
  // Relativo, no absoluto: el sitio cuelga de /vitrina/ en Pages y de la raiz
  // cuando se sirve en local, y asi vale igual en los dos.
  const subir = "../".repeat(slug.split("/").length - 1)
  return `${subir}assets/portadas/${fichero}`
}

/**
 * El grafo de la portada, entero y en grande.
 *
 * La vista pequeña de la barra lateral dibuja lo que hay a un salto de la
 * pagina, y en la portada eso son solo las cinco secciones: el arbol entero,
 * que es lo que tiene gracia enseñar en casa, habia que ir a buscarlo al boton
 * de pantalla completa. Aqui se pinta de entrada, y la vista pequeña se quita
 * de la barra para no dibujar dos veces lo mismo.
 *
 * No es un grafo nuevo: es el componente de Quartz, que su script busca por la
 * pagina entera y dibuja en cada `.graph-container` que encuentre con la
 * configuracion que lleve puesta. `depth: -1` es "todo", sin contar saltos.
 *
 * Va dentro de `Ficha` porque un plugin solo puede colocar un componente, y el
 * hueco que tiene Vitrina es ese: encima del texto. En una ficha lo ocupa la
 * caratula; en la portada, que no es una obra, no lo ocupaba nadie.
 */
// Las fuerzas estan para que el dibujo quepa en su caja, que con 290 nodos no
// es lo que sale de serie: los ajustes que trae Quartz reparten el grafo por
// donde pueda y la mitad acaba fuera del recuadro.
//
//   enableRadial  el que lo cambia todo: mete una fuerza que empuja cada nodo a
//                 una circunferencia de 0,8 del radio de la caja, asi que el
//                 dibujo sale redondo y acotado en vez de un manchon que crece
//                 hacia donde le dejan.
//   repelForce    mas flojo que el de serie: es lo que se empujan los nodos
//                 entre si, y con 290 a 0,5 el grafo se abria hasta reventar.
//   centerForce   mas fuerte por lo mismo, tirando todo hacia el medio.
//   linkDistance  mas corto: la distancia a la que se quieren los unidos.
//   scale         el zoom de entrada. Sube hasta que la circunferencia ocupa
//                 la caja, que si no se queda un circulito en medio.
//   fontSize      los rotulos, mas pequeños: son 290 y a 0,6 se pisan.
const GRAFO = {
  drag: true,
  zoom: true,
  depth: -1,
  scale: 1.15,
  repelForce: 0.35,
  centerForce: 0.4,
  linkDistance: 24,
  fontSize: 0.5,
  opacityScale: 1,
  showTags: true,
  removeTags: [],
  focusOnHover: true,
  enableRadial: true,
}

function grafoDeCasa() {
  return h(
    "div",
    { class: "grafo-casa" },
    h(
      "div",
      { class: "graph-outer" },
      h("div", { class: "graph-container", "data-cfg": JSON.stringify(GRAFO) }),
    ),
  )
}

const Ficha = () => {
  function Ficha({ fileData, allFiles }) {
    const f = fileData.frontmatter ?? {}
    const tipo = TIPOS[f.tipo]
    // La portada tampoco es una obra, pero su hueco no se queda vacio.
    if (fileData.slug === "index") return grafoDeCasa()
    // Los indices, los autores y los creditos no son obras: no llevan cabecera.
    if (!tipo) return null

    const slug = fileData.slug ?? ""
    const allSlugs = allFiles.map((file) => file.slug)

    // Solo lo que la ficha tiene. Una fila vacia no informa de nada, y casi la
    // mitad del catalogo sigue sin nota.
    const datos = []
    const dato = (clave, valor) => hay(valor) && datos.push([clave, valor])

    dato("Año", f.year)
    dato(tipo.autor, hay(f.autor) ? autor(f.autor, slug, allSlugs, paginasDeAutor(allFiles)) : null)
    dato("Nota", hay(f.nota) ? `${f.nota} / 10` : null)
    // Solo cuando dice algo. Casi todas las fichas ponen "terminado" --es lo que
    // escribe el importador de lo que ya has visto o leido-- asi que la fila
    // salia en todas repitiendo lo que se da por supuesto al tenerlo aqui. Lo
    // que informa es lo contrario: que este pendiente, a medias o abandonado.
    if (f.estado !== "terminado") dato("Estado", ESTADOS[f.estado])
    if (f.tipo === "juego") dato("Horas", hay(f.horas) ? `${f.horas} h` : null)

    const enlace = tipo.enlace(f) || null
    const img = hay(f.portada) ? portada(f.portada, slug) : null

    return h("div", { class: "ficha" }, [
      img &&
        h("img", {
          class: "ficha-portada",
          src: img,
          alt: `Carátula de ${fileData.frontmatter?.title ?? ""}`.trim(),
          loading: "lazy",
        }),
      h("div", { class: "ficha-datos" }, [
        f.favorito === true && h("p", { class: "ficha-favorito" }, "★ Favorito"),
        datos.length > 0 &&
          h(
            "dl",
            null,
            datos.map(([clave, valor]) =>
              h("div", { class: "ficha-dato" }, [h("dt", null, clave), h("dd", null, valor)]),
            ),
          ),
        enlace && h("p", { class: "ficha-enlace" }, h("a", { href: enlace[1] }, enlace[0])),
      ]),
    ])
  }

  // El sitio abre en oscuro salvo que ya hayas elegido claro.
  //
  // El boton de la barra guarda tu eleccion en `theme`; el script de Quartz, si
  // no hay ninguna, va a preguntarle al sistema, asi que a quien tenga el
  // portatil en claro le abria en claro. La coleccion esta pensada al reves:
  // es una vitrina a oscuras con las piezas iluminadas, y en claro las
  // caratulas pierden la mitad de la gracia. Asi que cuando no hay eleccion se
  // apunta la nuestra, y el boton sigue mandando en cuanto la toques.
  //
  // Esto va en `beforeDOMLoaded`, que se sirve en la cabecera y corre antes de
  // que se pinte nada: el atributo se corrige en el mismo tic aunque el script
  // del boton haya llegado antes, asi que no hay parpadeo.
  Ficha.beforeDOMLoaded = `
if (!localStorage.getItem("theme")) {
  localStorage.setItem("theme", "dark")
  document.documentElement.setAttribute("saved-theme", "dark")
}
`

  // El grafo, cuando la direccion lleva un simbolo o un acento.
  //
  // Al cargar una pagina de golpe, el grafo se pregunta cual es mirando
  // `location.pathname`, y el navegador lo entrega escapado: Dark Souls llega
  // como "juegos/dark-souls%E2%84%A2-remastered". Ese nombre no esta en el
  // indice, pero el grafo lo dibuja igual porque la pagina actual siempre entra
  // en el grafo, asi que salia un nodo suelto, sin etiquetas y rotulado con la
  // direccion en crudo en vez del titulo.
  //
  // Pasaba en diez paginas: los tres juegos con el simbolo de marca registrada,
  // "Idle Slayer" con su raya larga, "El Madrileño" con la eñe, y las cinco
  // etiquetas con tilde (accion, fantasia, ciencia-ficcion, filosofia,
  // animacion). Al llegar desde otra pagina del sitio no se veia, porque ahi el
  // nombre se lo pasa el navegador interno ya en claro.
  //
  // El nombre bueno lo lleva siempre el `<body>`, asi que en esas paginas se
  // vuelve a lanzar el aviso de "pagina nueva" con el que vale. Esto corre
  // detras del grafo, que se carga antes, y no se toca nada de Quartz.
  Ficha.afterDOMLoaded = `
if (decodeURI(location.pathname) !== location.pathname) {
  const avisar = () => {
    const slug = document.body?.dataset?.slug
    if (slug) document.dispatchEvent(new CustomEvent("nav", { detail: { url: slug } }))
  }
  // Al terminar de cargar, no antes: los scripts de la pagina se piden todos a
  // la vez y ninguno sabe cual llega primero, asi que el del grafo puede no
  // estar escuchando todavia. Cuando salta "load" ya se han ejecutado todos.
  if (document.readyState === "complete") avisar()
  else window.addEventListener("load", avisar, { once: true })
}
`

  Ficha.css = `
/* El grafo de la portada, en grande y con la vista pequeña de la barra fuera:
   dibujan lo mismo, y ahi al lado no cabe nada que se lea.

   La caja tira a cuadrada porque el radio del dibujo sale de su lado corto: en
   una tira ancha y baja, el grafo se queda en un circulito en medio. */
.grafo-casa .graph-outer {
  height: min(70vh, 520px);
  margin: 1.4rem 0 0;
}
body[data-slug="index"] .sidebar .graph {
  display: none;
}
.ficha {
  display: flex;
  gap: 1.2rem;
  align-items: flex-start;
  margin: 0.6rem 0 1.4rem;
}
.ficha-portada {
  flex: 0 0 auto;
  width: 185px;
  max-width: 40%;
  border-radius: 5px;
  border: 1px solid var(--lightgray);
}
.ficha-datos {
  flex: 1 1 auto;
  min-width: 0;
}
.ficha-datos > *:first-child { margin-top: 0; }
.ficha-datos > *:last-child { margin-bottom: 0; }
.ficha-favorito {
  margin: 0 0 0.5rem;
  color: var(--dorado);
  font-weight: 600;
  font-size: 0.9rem;
}
.ficha-datos dl {
  margin: 0;
  display: grid;
  /* Una columna para la etiqueta y otra para el dato: asi "Año" y "Estudio"
     quedan alineados aunque midan distinto. */
  grid-template-columns: auto 1fr;
  gap: 0.25rem 0.9rem;
  font-size: 0.95rem;
}
.ficha-dato { display: contents; }
.ficha-datos dt {
  color: var(--gray);
  white-space: nowrap;
}
.ficha-datos dd {
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}
.ficha-enlace {
  margin: 0.8rem 0 0;
  font-size: 0.9rem;
}
/* La caratula encima de los datos en cuanto no caben de lado: a 150px de
   imagen mas dos columnas de datos, en un movil se quedaba sin sitio. */
@media (max-width: 480px) {
  .ficha { flex-direction: column; gap: 0.9rem; }
  .ficha-portada { width: 130px; max-width: 100%; }
}
`

  return Ficha
}

export { Ficha }
