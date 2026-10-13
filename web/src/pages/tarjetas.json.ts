import type { APIRoute } from "astro";
import { NOMBRE } from "../config";
import { t } from "../i18n";
import { cartela, obras, quienFirma, seccionDe, tarjeta, titulo, url } from "../lib/obras";

// Lo que necesita la integración para pintar la tarjeta de cada ficha: la
// imagen que sale al pegar el enlace en un chat o una red. No se publica: la
// integración lo lee al acabar el build, hace las imágenes y lo borra.
export const GET: APIRoute = async ({ site }) => {
  const lista = (await obras()).map((o) => {
    const d = o.data;
    return {
      id: o.id,
      // La dirección de la imagen, sin la base: es donde se escribe en dist.
      salida: tarjeta(o).slice(url().length),
      titulo: titulo(o),
      // El nombre del fichero siempre está en ASCII: sirve de título si el de
      // verdad no se puede pintar (un disco japonés sin la fuente a mano).
      alternativo: (o.filePath ?? o.id).split("/").pop()!.replace(/\.md$/, ""),
      autor: quienFirma(o),
      year: d.year ?? null,
      tipo: d.type,
      sala: seccionDe(d.type).nombre,
      nota: d.rating ?? null,
      favorito: Boolean(d.favorite),
      cartela: cartela(o),
      portada: d.cover?.replace(/^\[\[|\]\]$/g, "").split("|")[0] ?? null,
    };
  });
  const textos = { nombre: NOMBRE, mejor: t.tarjeta.mejor, de10: t.tarjeta.de10, sitio: new URL(url(), site).host + url() };
  return new Response(JSON.stringify({ textos, tarjetas: lista }), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
