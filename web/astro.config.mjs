import { defineConfig } from "astro/config";
import { satteri } from "@astrojs/markdown-satteri";
import sitemap from "@astrojs/sitemap";
import callouts from "satteri-callouts";
import vitrina from "./src/integraciones/vitrina.mjs";

export default defineConfig({
  site: "https://jorgeress.github.io",
  base: "/vitrina",
  // web/public lleva los iconos, el manifest y el service worker. Las
  // portadas no: se quedan donde las deja portadas.py, dentro de la vault,
  // para que Obsidian las siga viendo, y las sirve la integración `vitrina`.
  integrations: [vitrina(), sitemap({ filter: (pagina) => !pagina.includes("/offline/") })],
  markdown: {
    // Los callouts de Obsidian: la cartela (`[!vitrina]`) y la cita de la
    // fuente (`[!quote]`) se ven en la web igual que en la vault.
    processor: satteri({
      hastPlugins: [
        callouts({
          showIndicator: false,
          callouts: { vitrina: { title: "Por qué está en la vitrina" } },
        }),
      ],
    }),
  },
});
