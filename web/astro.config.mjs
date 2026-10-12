import { defineConfig } from "astro/config";
import { satteri } from "@astrojs/markdown-satteri";
import callouts from "satteri-callouts";

export default defineConfig({
  site: "https://jorgeress.github.io",
  base: "/vitrina",
  // Las portadas se quedan donde las deja portadas.py, dentro de la vault,
  // para que Obsidian las siga viendo. La web las sirve desde ahí mismo.
  publicDir: "../content/assets",
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
