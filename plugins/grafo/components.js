import { Graph } from "@quartz-community/graph"

/**
 * El grafo de siempre, pero sabiendo en que pagina esta.
 *
 * El grafo dibuja a un salto de donde estas, asi que lo primero que hace es
 * preguntar en que pagina es eso. Y lo pregunta al sitio equivocado: a la
 * direccion del navegador. De ahi saca "juegos" para /juegos/, mientras que las
 * fichas cuelgan del nodo "juegos/", que es como queda "juegos/index" al
 * simplificarlo: se le cae el nombre y se queda la barra. Como no encuentra ese
 * nodo se inventa uno vacio en el momento, y la seccion dibujaba un punto
 * suelto, sin una sola arista, en la unica pagina donde el grafo tenia algo que
 * contar: sus cuarenta y cinco juegos colgando.
 *
 * Lo mismo rompia las direcciones con tilde o con simbolo, porque del navegador
 * vienen escapadas ("%C3%B1") y el nodo no lo esta.
 *
 * La respuesta buena la trae cada pagina en el `data-slug` del `body`, que es
 * justo lo que lee el Quartz de serie, sin escapar y con el "index" dentro. El
 * plugin lo tiene a mano y no lo usa, asi que se le cambia esa linea al guion
 * que manda al navegador. Es de una pieza y minificado, de modo que lo que se
 * sustituye es el texto tal cual sale del paquete: si un dia deja de estar --
 * porque lo arreglen de verdad, que es donde toca-- esto no se queda arreglando
 * a medias en silencio, sino que revienta el build y se lee aqui por que.
 */
const VIEJO = "function u(){var a=we(),o=Nu();"
const NUEVO =
  "function u(){var vslug=document.body?.dataset?.slug;if(vslug)return vslug;var a=we(),o=Nu();"

export const Grafo = (opts) => {
  const componente = Graph(opts)
  const guion = componente.afterDOMLoaded ?? ""

  if (!guion.includes(VIEJO)) {
    throw new Error(
      "plugins/grafo: el guion de @quartz-community/graph ya no pregunta la pagina a la " +
        "direccion del navegador. Comprueba si lee el data-slug del body por su cuenta: si es " +
        "que si, este envoltorio sobra y la configuracion puede volver al plugin de serie.",
    )
  }

  componente.afterDOMLoaded = guion.replace(VIEJO, NUEVO)
  return componente
}
