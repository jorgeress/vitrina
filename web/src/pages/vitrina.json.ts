import type { APIRoute } from "astro";
import { autores, cartela, obras, ruta, titulo } from "../lib/obras";

// La colección entera en un fichero, con los ids de cada fuente. Es lo que
// permitiría comparar dos vitrinas cualesquiera (en qué coinciden, qué tiene
// una que la otra no) sin un servidor en medio y sin fiarse de los títulos.
export const GET: APIRoute = async ({ site }) => {
  const lista = (await obras()).map((o) => {
    const d = o.data;
    return {
      titulo: titulo(o),
      tipo: d.tipo,
      year: d.year ?? null,
      autores: autores(o),
      nota: d.nota ?? null,
      estado: d.estado ?? null,
      favorito: Boolean(d.favorito),
      alta: d.alta?.toISOString().slice(0, 10) ?? null,
      tags: d.tags ?? [],
      ids: Object.fromEntries(
        (["appid", "letterboxd", "tvmaze", "mbid", "wikipedia"] as const)
          .filter((k) => d[k] != null)
          .map((k) => [k, d[k]]),
      ),
      cartela: cartela(o),
      url: new URL(ruta(o), site).href,
    };
  });
  return new Response(JSON.stringify({ version: 2, obras: lista }, null, 2), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
