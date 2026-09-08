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
 * `autor` puede ser texto suelto ("Albert Camus") o un enlace a la pagina de
 * autor ("[[autores/Radiohead|Radiohead]]"), que es lo que hace `autores.py`
 * en cuanto dos obras comparten firma. Se pintan distinto: una es un nombre y
 * la otra se puede pinchar.
 */
function autor(valor, slug, allSlugs) {
  const texto = String(valor).trim()
  const m = texto.match(WIKILINK)
  if (!m) return texto
  const destino = m[1]
  const visible = m[2] ?? destino
  const href = transformLink(slug, destino, { strategy: "shortest", allSlugs })
  return h("a", { href, class: "internal" }, visible)
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
    dato(tipo.autor, hay(f.autor) ? autor(f.autor, slug, allSlugs) : null)
    dato("Nota", hay(f.nota) ? `${f.nota} / 10` : null)
    dato("Estado", ESTADOS[f.estado])
    if (f.tipo === "juego") dato("Horas", hay(f.horas) ? `${f.horas} h` : null)
    if (f.tipo === "album") dato("Canciones tuyas", f.favoritas)

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
