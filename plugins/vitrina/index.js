/**
 * Lo que Vitrina necesita de Quartz y Quartz no trae.
 *
 * Son dos cosas sueltas que comparten fichero solo porque un plugin es la
 * unidad que Quartz sabe cargar, no porque tengan nada que ver:
 *
 *   - Aqui abajo, las cinco paginas `.base` fuera del buscador.
 *   - En components.js, el componente `Ficha`, que pinta la cabecera de cada
 *     obra: la caratula, los datos y el enlace a la fuente.
 */

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
 *   Un `.base` no es un fichero de entrada. Quartz parsea 102 ficheros y
 *   ninguno de los cinco esta entre ellos; sus paginas las fabrica bases-page
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
 * lista vacia y `match` no reclama ninguna -- y lo unico que hace es marcar las
 * ajenas. La pagina se sigue emitiendo y el `![[Juegos.base]]` de cada seccion
 * se sigue pintando igual: lo unico que cambia es que dejan de salir al buscar.
 */
const BasesFueraDelIndice = () => ({
  name: "VitrinaBasesFueraDelIndice",
  // Por debajo del 20 de bases-page: el despachador va de mayor a menor.
  priority: 1,
  match: () => false,
  generate({ ctx }) {
    for (const [, vfile] of ctx.virtualPages ?? []) {
      if (String(vfile.data?.slug ?? "").endsWith(".base")) {
        vfile.data.unlisted = true
      }
    }
    return []
  },
  // Nunca se usan, porque `match` no reclama ninguna pagina, pero el
  // despachador resuelve la maqueta de todos los pageType antes de mirar eso.
  layout: "content",
  body: () => () => null,
})

export default BasesFueraDelIndice
