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

const Ficha = () => {
  function Ficha({ fileData, allFiles }) {
    const f = fileData.frontmatter ?? {}
    const tipo = TIPOS[f.tipo]
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

  Ficha.css = `
.ficha {
  display: flex;
  gap: 1.2rem;
  align-items: flex-start;
  margin: 0.6rem 0 1.4rem;
}
.ficha-portada {
  flex: 0 0 auto;
  width: 150px;
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
  color: var(--tertiary);
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
