import type { APIContext } from "astro";
import {
  SECCIONES,
  autoresRepetidos,
  años,
  grupos,
  obras,
  ruta,
  rutaAutor,
  rutaFija,
  rutaGrupo,
  rutaTag,
  slugsAutores,
  url,
} from "../lib/obras";

// En la misma dirección que el de Quartz, /sitemap.xml, que es donde ya lo
// buscan los buscadores. Cada ficha lleva de fecha su alta en la vitrina.
export async function GET({ site }: APIContext) {
  const todas = await obras();
  const slugs = await slugsAutores();
  const absoluta = (ruta: string) => new URL(ruta, site).href;
  const fecha = (d?: Date | null) => (d ? `<lastmod>${d.toISOString().slice(0, 10)}</lastmod>` : "");

  const fijas = [
    url(),
    ...(["favoritos", "grupos", "anuario", "constelacion", "autores", "tags", "cifras", "buscar", "creditos"] as const).map(
      (p) => rutaFija(p),
    ),
  ];
  const salas = SECCIONES.map((s) => url(`${s.slug}/`));
  const autores = [...autoresRepetidos(todas).keys()].map((a) => rutaAutor(a, slugs));
  const tags = [...new Set(todas.flatMap((o) => o.data.tags ?? []))].map(rutaTag);
  const deGrupos = (await grupos()).map(rutaGrupo);
  const deAños = años(todas).map((y) => rutaFija("anuario", `${y}/`));

  const entradas = [
    ...[...fijas, ...salas, ...autores, ...tags, ...deGrupos, ...deAños].map((r) => `<url><loc>${absoluta(r)}</loc></url>`),
    ...todas.map((o) => `<url><loc>${absoluta(ruta(o))}</loc>${fecha(o.data.added)}</url>`),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${entradas.join("\n")}\n</urlset>\n`;
  return new Response(xml, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
}
