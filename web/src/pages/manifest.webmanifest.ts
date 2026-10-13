import type { APIRoute } from "astro";
import { NOMBRE } from "../config";
import { t } from "../i18n";
import { SECCIONES } from "../lib/obras";

// El manifest de la app se escribe al construir, en el idioma de la vitrina y
// con sus direcciones. `share_target` es lo que hace que la web instalada
// salga en el menú Compartir de Android y lleve el enlace a la página de añadir.
export const GET: APIRoute = () => {
  const relativa = (ruta: string) => `./${ruta}/`;
  const manifest = {
    name: NOMBRE,
    short_name: NOMBRE,
    description: t.descripcion,
    lang: t.locale.slice(0, 2),
    start_url: "./",
    scope: "./",
    display: "standalone",
    background_color: "#0f0e10",
    theme_color: "#0f0e10",
    icons: [
      { src: "iconos/icono-192.png", sizes: "192x192", type: "image/png" },
      { src: "iconos/icono-512.png", sizes: "512x512", type: "image/png" },
      { src: "iconos/icono-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
    shortcuts: [
      { name: t.anadirTitulo, url: relativa(t.rutas.anadir) },
      ...SECCIONES.filter((s) => ["game", "film", "album"].includes(s.tipo)).map((s) => ({ name: s.nombre, url: relativa(s.slug) })),
      { name: t.constelacion, url: relativa(t.rutas.constelacion) },
    ],
    share_target: {
      action: relativa(t.rutas.anadir),
      method: "GET",
      params: { title: "title", text: "text", url: "url" },
    },
  };
  return new Response(JSON.stringify(manifest, null, 2), {
    headers: { "Content-Type": "application/manifest+json; charset=utf-8" },
  });
};
