// Lo que la web necesita fuera de las páginas: las portadas, que viven en la
// vault y no en web/public; el índice del buscador, que se hace con la web ya
// construida; y las tarjetas para compartir, que se pintan con ella.
import { cp, readFile, readdir, rm, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join, normalize } from "node:path";
import { hacerTarjetas } from "./tarjetas.mjs";

const CONTENT = fileURLToPath(new URL("../../../content/", import.meta.url));
const PORTADAS = join(CONTENT, "assets", "portadas");
const CSS = fileURLToPath(new URL("../styles/global.css", import.meta.url));

/**
 * @param {{ privada: string, vistazo: boolean }} opciones La carpeta privada de
 * vitrine.config.json y si es el vistazo: solo entonces se sirven y se copian
 * sus portadas, que no salen nunca en la web publicada.
 */
export default function vitrina({ privada, vistazo }) {
  const portadas = vistazo ? [PORTADAS, join(CONTENT, privada, "portadas")] : [PORTADAS];
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
        server.middlewares.use(servirPortadas([`${base}portadas/`, "/portadas/"], portadas));
      },
      // Las portadas se copian tal cual: portadas.py ya las deja en webp y a
      // 400 px, que es lo que se pinta.
      "astro:build:done": async ({ dir, logger }) => {
        const salida = fileURLToPath(dir);
        for (const origen of portadas)
          try {
            await cp(origen, join(salida, "portadas"), { recursive: true });
          } catch {}

        // Las tarjetas: los datos los deja la propia web en tarjetas.json, que
        // no se publica.
        const datos = join(salida, "tarjetas.json");
        await hacerTarjetas({
          salida,
          datos: JSON.parse(await readFile(datos, "utf-8")),
          portadas,
          css: await readFile(CSS, "utf-8"),
          logger,
        });
        await rm(datos);

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
function servirPortadas(prefijos, carpetas) {
  return async (req, res, next) => {
    const prefijo = prefijos.find((p) => req.url?.startsWith(p));
    if (!prefijo) return next();
    const nombre = decodeURIComponent(req.url.slice(prefijo.length).split("?")[0]);
    for (const carpeta of carpetas) {
      const fichero = normalize(join(carpeta, nombre));
      if (!fichero.startsWith(carpeta)) continue;
      try {
        await stat(fichero);
        res.setHeader("Content-Type", "image/webp");
        res.end(await readFile(fichero));
        return;
      } catch {}
    }
    next();
  };
}
