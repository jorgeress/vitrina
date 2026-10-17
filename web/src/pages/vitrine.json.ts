import type { APIRoute } from "astro";
import { IDIOMA, NOMBRE } from "../config";
import { autores, opinion, obras, portada, ruta, titulo } from "../lib/obras";

// La colección entera en un fichero, con los ids de cada fuente. Es lo que
// permite comparar dos vitrinas cualesquiera (en qué coinciden, qué tiene una
// que la otra no) sin un servidor en medio y sin fiarse de los títulos. Las
// claves van en inglés, como en las fichas, para que dos vitrinas en idiomas
// distintos se entiendan.
export const GET: APIRoute = async ({ site }) => {
  const lista = (await obras()).map((o) => {
    const d = o.data;
    return {
      title: titulo(o),
      type: d.type,
      year: d.year ?? null,
      authors: autores(o),
      rating: d.rating ?? null,
      status: d.status ?? null,
      favorite: Boolean(d.favorite),
      added: d.added?.toISOString().slice(0, 10) ?? null,
      finished_on: d.finished_on ?? null,
      started_on: d.started_on ?? null,
      times: d.times ?? null,
      tags: d.tags ?? [],
      groups: d.groups ?? [],
      ids: Object.fromEntries(
        (["appid", "letterboxd", "tvmaze", "mbid", "wikipedia", "wikidata"] as const).filter((k) => d[k] != null).map((k) => [k, d[k]]),
      ),
      opinion: opinion(o),
      url: new URL(ruta(o), site).href,
      cover: portada(o) && new URL(portada(o)!, site).href,
    };
  });
  const vitrina = { format: "vitrine", version: 1, name: NOMBRE, language: IDIOMA, works: lista };
  return new Response(JSON.stringify(vitrina, null, 2), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
