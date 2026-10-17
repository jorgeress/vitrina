// Lo que cambia de una vitrina a otra vive en vitrine.config.json, en la raíz
// del repo, y lo leen también los scripts y astro.config.mjs. Hacerse una
// vitrina propia es cambiar ese fichero; aquí solo se lee y se le dan tipos.
import ajustes from "../../vitrine.config.json";

export type Idioma = "es" | "en";
export type Tipo = "game" | "film" | "series" | "book" | "album";

export const TIPOS: readonly Tipo[] = ["game", "film", "series", "book", "album"];

interface Ajustes {
  name: string;
  owner: string;
  language: string;
  site: string;
  base: string;
  repo: string;
  folders: Record<Tipo | "author" | "private" | "group", string | undefined>;
  /** Otras vitrinas a mano en «Sorpréndeme»: `[{ "name": "Ana", "url": "…" }]`. */
  friends?: { name: string; url: string }[];
}

const a = ajustes as unknown as Ajustes;

export const NOMBRE = a.name;
export const DUENO = a.owner;
/** Cualquier idioma que no sea el español cae en el inglés, que es el de la
 * herramienta. */
export const IDIOMA: Idioma = a.language === "es" ? "es" : "en";
export const REPO = a.repo;
export const AMIGOS = a.friends ?? [];

/** La carpeta de la vault de cada sección, que es también su dirección. */
export const CARPETAS: Record<Tipo, string> = Object.fromEntries(
  TIPOS.map((t) => [t, a.folders[t] ?? t]),
) as Record<Tipo, string>;
export const CARPETA_AUTORES = a.folders.author ?? "authors";
export const CARPETA_PRIVADA = a.folders.private ?? "private";
export const CARPETA_GRUPOS = a.folders.group ?? (IDIOMA === "es" ? "grupos" : "groups");
