import rss from "@astrojs/rss";
import type { APIContext } from "astro";
import { cartela, obras, porAlta, quienFirma, ruta, seccionDe, titulo } from "../lib/obras";

// Lo que va entrando en la vitrina, en la misma dirección que el RSS de
// Quartz (index.xml), para que quien ya lo siga no tenga que cambiar nada.
export async function GET(contexto: APIContext) {
  const recientes = (await obras()).sort(porAlta).slice(0, 40);
  return rss({
    title: "Vitrina",
    description: "Lo que va entrando en la vitrina: juegos, películas, series, libros y discos.",
    site: new URL(import.meta.env.BASE_URL, contexto.site),
    items: recientes.map((o) => {
      const quien = quienFirma(o);
      const sala = seccionDe(o.data.tipo).una;
      return {
        title: titulo(o),
        link: ruta(o),
        pubDate: o.data.alta ?? undefined,
        categories: [sala, ...(o.data.tags ?? [])],
        description: cartela(o) ?? [sala, o.data.year, quien].filter(Boolean).join(" · "),
      };
    }),
    customData: "<language>es</language>",
  });
}
