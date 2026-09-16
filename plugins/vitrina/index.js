import { nombresEnTexto, paginasDeAutor } from "./components.js"

/**
 * Lo que Vitrina necesita de Quartz y Quartz no trae.
 *
 * Son cuatro cosas sueltas que comparten fichero solo porque un plugin es la
 * unidad que Quartz sabe cargar, no porque tengan nada que ver:
 *
 *   - Aqui abajo, las seis paginas `.base` fuera del buscador.
 *   - Tambien aqui, la arista de cada ficha a la pagina de su autor.
 *   - Y la de Lo mejor de lo mejor a cada uno de sus favoritos.
 *   - En components.js, el componente `Ficha`, que pinta la cabecera de cada
 *     obra: la caratula, los datos y el enlace a la fuente.
 */

/**
 * De cada ficha a la pagina de su autor, para el grafo y los backlinks.
 *
 * El campo `autor` es texto plano: "QLOC, FromSoftware, Inc.". Eso lo hace un
 * dato y no maquetacion --que es el reparto de toda la vault-- y de paso evita
 * que la galeria se rompa, porque una tarjeta entera ya es un enlace y un
 * `[[...]]` dentro le metia un `<a>` dentro de otro: el navegador lo parte al
 * leerlo y la portada acababa en una celda y el titulo en otra.
 *
 * El precio de que sea texto es que el grafo dejaria de ver la relacion, y esa
 * si importa: es lo que junta los tres FromSoftware o los tres MCR. Asi que se
 * le devuelve aqui. El grafo del cliente monta las aristas con los `links` de
 * cada pagina y luego las recorre en los dos sentidos, asi que basta con
 * apuntar en la ficha la pagina de cada autor que tenga una.
 *
 * De regalo, la arista pasa a existir para las noventa fichas y no solo para
 * las doce que llevaban el `[[...]]` escrito, y una ficha con varios autores
 * enlaza a todos: hasta ahora "QLOC, FromSoftware, Inc." solo apuntaba a uno.
 */
function enlazarAutores(content) {
  const paginas = paginasDeAutor(content.map(([, vfile]) => vfile.data))
  if (paginas.length === 0) return

  for (const [, vfile] of content) {
    const autor = vfile.data?.frontmatter?.autor
    if (!autor) continue
    const destinos = nombresEnTexto(autor, paginas)
      .map(([, destino]) => destino)
      .filter((destino) => destino !== null)
    if (destinos.length === 0) continue
    vfile.data.links = [...new Set([...(vfile.data.links ?? []), ...destinos])]
  }
}

/**
 * De Lo mejor de lo mejor a cada favorito, por lo mismo.
 *
 * Esa pagina no enlaza a nada: lo que enseña es un `.base` filtrado por
 * `favorito == true`, y una galeria se pinta al emitir, cuando los enlaces ya
 * estan contados. Asi que su nodo colgaba de Vitrina y no llevaba a ninguna de
 * las veintiuna fichas que lista: pinchar en el no enseñaba nada.
 *
 * Se le apuntan aqui, y en este sentido a proposito: de la pagina a cada
 * favorito, como una pagina de autor a sus obras. Al reves, de la ficha a la
 * pagina como hace el campo `seccion`, el grafo saldria igual --el cliente
 * recorre las aristas en los dos sentidos-- pero los retroenlaces de Lo mejor
 * de lo mejor repetirian entera la galeria que ya esta debajo, que es justo lo
 * que se quito de las secciones. Asi cada favorito gana en cambio una linea que
 * dice que esta ahi, al lado de la de su autor.
 *
 * La pagina se busca por su direccion y no por su titulo, que ya se ha llamado
 * de dos maneras distintas y el fichero no se ha movido.
 */
function enlazarFavoritos(content) {
  const pagina = content.find(([, vfile]) => vfile.data?.slug === "favoritos")
  if (!pagina) return

  const favoritos = content
    .map(([, vfile]) => vfile.data)
    .filter((data) => data?.frontmatter?.favorito === true)
    .map((data) => data.slug)
    .filter((slug) => slug)
  if (favoritos.length === 0) return

  const data = pagina[1].data
  data.links = [...new Set([...(data.links ?? []), ...favoritos])]
}

/**
 * Las cinco paginas `.base` fuera del buscador.
 *
 * `includeEmptyFiles: true` esta puesto a proposito en content-index: una ficha
 * sin texto sigue teniendo titulo, y quien busca "Elden Ring" espera
 * encontrarla. El precio eran las paginas que bases-page emite por cada fichero
 * `.base`: entraban en el indice con el nombre del fichero y sin una linea
 * dentro, asi que buscar "juegos" devolvia dos veces «Juegos», y una de las dos
 * era una copia en blanco de la galeria que ya esta en /juegos/.
 *
 * content-index se salta lo que lleve `data.unlisted`, asi que basta con
 * marcarlas. Lo dificil es *donde*, y por eso esto es un pageType y no un
 * transformador, que era lo primero que parecia:
 *
 *   Un `.base` no es un fichero de entrada. Quartz parsea los .md de la vault
 *   y ninguno de los seis esta entre ellos; sus paginas las fabrica bases-page
 *   en `generate()`, ya emitiendo, y salen de ahi como *paginas virtuales*. Un
 *   `markdownPlugins` nunca las ve.
 *
 *   Tampoco vale un emisor propio: los emisores de la fase 2 arrancan todos a
 *   la vez con `Promise.all`, asi que llegar antes que content-index seria
 *   cuestion de suerte.
 *
 *   El despachador si ordena los pageType, y de mayor a menor `priority`. Con
 *   bases-page en 20 y esto en 1, cuando llega el turno de aqui sus paginas ya
 *   estan en `ctx.virtualPages`, todavia dentro de la fase 1 y mucho antes de
 *   que content-index lea nada.
 *
 * Asi que este pageType no aporta ninguna pagina -- `generate` devuelve la
 * lista vacia y `match` no reclama ninguna -- y lo unico que hace es tocar las
 * ajenas. La pagina se sigue emitiendo y el `![[Juegos.base]]` de cada seccion
 * se sigue pintando igual: lo unico que cambia es que dejan de salir al buscar.
 *
 * Ese mismo hueco -- fase 1, con todo parseado y antes de que emita nadie -- es
 * el que necesitan `enlazarAutores` y `enlazarFavoritos`, y por eso viajan de
 * gorra en este `generate` en vez de tener un pageType para ellas.
 */
const BasesFueraDelIndice = () => ({
  name: "VitrinaBasesFueraDelIndice",
  // Por debajo del 20 de bases-page: el despachador va de mayor a menor.
  priority: 1,
  match: () => false,
  generate({ content, ctx }) {
    for (const [, vfile] of ctx.virtualPages ?? []) {
      if (String(vfile.data?.slug ?? "").endsWith(".base")) {
        vfile.data.unlisted = true
      }
    }
    // Mismo sitio y mismo motivo que lo de arriba: hay que llegar antes que
    // content-index, que es quien vuelca los `links` al fichero que lee el
    // grafo, y esta fase 1 va entera por delante de los emisores.
    enlazarAutores(content)
    enlazarFavoritos(content)
    return []
  },
  // Nunca se usan, porque `match` no reclama ninguna pagina, pero el
  // despachador resuelve la maqueta de todos los pageType antes de mirar eso.
  layout: "content",
  body: () => () => null,
})

export default BasesFueraDelIndice
