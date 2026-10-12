// Lo que la web necesita fuera de las páginas: las portadas, que viven en la
// vault y no en web/public, y el índice del buscador, que se hace con la web
// ya construida.
import { cp, readdir, readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join, normalize } from "node:path";

const PORTADAS = fileURLToPath(new URL("../../../content/assets/portadas/", import.meta.url));

export default function vitrina() {
  let base = "/";
  return {
    name: "vitrina",
    hooks: {
      "astro:config:setup": ({ config }) => {
        base = config.base.replace(/\/?$/, "/");
      },
      // En `astro dev` las portadas se sirven directamente desde la vault.
      "astro:server:setup": ({ server }) => {
        // Vite le quita la base a la dirección antes de pasarla, así que llega
        // `/portadas/x.webp` y no `/vitrina/portadas/x.webp`; se aceptan las dos.
        server.middlewares.use(servirPortadas([`${base}portadas/`, "/portadas/"]));
      },
      // Las portadas se copian tal cual: portadas.py ya las deja en webp y a
      // 400 px, que es lo que se pinta.
      "astro:build:done": async ({ dir, logger }) => {
        const salida = fileURLToPath(dir);
        await cp(PORTADAS, join(salida, "portadas"), { recursive: true });

        // El buscador es Pagefind: lee el HTML construido y deja un índice
        // estático partido en trozos, así que busca sin servidor y sin clave.
        // Solo indexa lo que lleva data-pagefind-body, que son las fichas.
        const pagefind = await import("pagefind");
        const { index } = await pagefind.createIndex();
        await index.addDirectory({ path: salida });
        await index.writeFiles({ outputPath: join(salida, "pagefind") });
        await pagefind.close();
        // Un fragmento por página que entra en el índice.
        const fichas = (await readdir(join(salida, "pagefind", "fragment"))).length;
        logger.info(`buscador: ${fichas} fichas en el índice`);
      },
    },
  };
}

/** Un middleware que contesta las direcciones de portadas con el fichero de
 * la vault, y deja pasar todo lo demás. */
function servirPortadas(prefijos) {
  return async (req, res, next) => {
    const prefijo = prefijos.find((p) => req.url?.startsWith(p));
    if (!prefijo) return next();
    const nombre = decodeURIComponent(req.url.slice(prefijo.length).split("?")[0]);
    const fichero = normalize(join(PORTADAS, nombre));
    if (!fichero.startsWith(PORTADAS)) return next();
    try {
      await stat(fichero);
      res.setHeader("Content-Type", "image/webp");
      res.end(await readFile(fichero));
    } catch {
      next();
    }
  };
}
