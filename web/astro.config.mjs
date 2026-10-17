import { readFileSync } from "node:fs";
import { defineConfig } from "astro/config";
import { satteri } from "@astrojs/markdown-satteri";
import callouts from "satteri-callouts";
import vitrina from "./src/integraciones/vitrina.mjs";

// La dirección, el idioma y las carpetas de la vitrina, del mismo fichero que
// leen los scripts.
const ajustes = JSON.parse(readFileSync(new URL("../vitrine.config.json", import.meta.url), "utf-8"));
const vistazo = process.env.VITRINE_PREVIEW === "1";

// El título de la cartela cuando la ficha no lo escribe. Las dos formas del
// callout valen en cualquier idioma: [!vitrina] y [!vitrine].
const cartela = ajustes.language === "es" ? "Por qué está en la vitrina" : "Why it's on display";

export default defineConfig({
  site: ajustes.site,
  base: ajustes.base,
  // web/public lleva los iconos y el service worker. Las portadas no: se
  // quedan donde las deja portadas.py, dentro de la vault, para que Obsidian
  // las siga viendo, y las sirve la integración `vitrina`.
  integrations: [vitrina({ privada: ajustes.folders?.private ?? "private", vistazo })],
  markdown: {
    // Los callouts de Obsidian: la cartela y la cita de la fuente (`[!quote]`)
    // se ven en la web igual que en la vault.
    processor: satteri({
      hastPlugins: [
        callouts({
          showIndicator: false,
          // `> [!spoiler]-` sale plegado, como en Obsidian, y fuera del
          // buscador: si no, el extracto de un resultado podría destriparlo.
          callouts: { vitrina: { title: cartela }, vitrine: { title: cartela }, spoiler: { title: "Spoilers" } },
          props: { containerProps: (_nodo, tipo) => (tipo === "spoiler" ? { "data-pagefind-ignore": "all" } : null) },
        }),
      ],
    }),
  },
});
