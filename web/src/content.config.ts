import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";
import { CARPETAS, CARPETA_AUTORES, CARPETA_GRUPOS, CARPETA_PRIVADA, TIPOS } from "./config";
import { slugQuartz } from "./lib/texto";

/**
 * Con VITRINE_PREVIEW=1 (lo pone scripts/vistazo.py) entran también los
 * borradores, lo oculto y la carpeta privada, marcados, para ver la vitrina
 * entera en tu ordenador. Sin eso, la web publicada no los lee siquiera.
 */
export const VISTAZO = globalThis.process?.env?.VITRINE_PREVIEW === "1";

const salas = `{${TIPOS.map((t) => CARPETAS[t]).join(",")}}`;
const privada = (patron: string) => (VISTAZO ? [`${CARPETA_PRIVADA}/${patron}`] : []);

/** El id quita la carpeta privada de delante: lo privado tiene la misma
 * dirección que tendría si fuera público, así que hacerlo público no cambia
 * ningún enlace. */
const id = (entrada: string, quitar: string | RegExp = "") =>
  slugQuartz(entrada.replace(new RegExp(`^${CARPETA_PRIVADA}/`), "").replace(quitar, "").replace(/\.md$/, ""));

/** Lo que se puede ocultar de una ficha pública, campo a campo. `label` es la
 * cartela, «Por qué está en la vitrina». */
export const OCULTABLES = ["rating", "status", "favorite", "label", "finished_on", "groups", "added"] as const;

/**
 * Cuándo lo terminaste: un año, un año y un mes, o el día. YAML lee `2024`
 * como número y `2024-05-03` como fecha; aquí todo acaba en texto
 * («2024-05»), con la precisión que se haya escrito y ni una más.
 */
const fechaParcial = z
  .union([z.date(), z.number().int(), z.string()])
  .transform((v, ctx) => {
    const texto = v instanceof Date ? v.toISOString().slice(0, 10) : String(v).trim();
    if (!/^\d{4}(-(0[1-9]|1[0-2])(-(0[1-9]|[12]\d|3[01]))?)?$/.test(texto)) {
      ctx.addIssue({ code: "custom", message: `finished_on: «${texto}» no es AAAA, AAAA-MM ni AAAA-MM-DD` });
      return z.NEVER;
    }
    return texto;
  });

// Las mismas fichas que edita Obsidian y rellenan los scripts. El esquema es
// el contrato: si una ficha trae `rating: 11` o un estado mal escrito, la web
// no se construye y el error dice cuál es, en vez de publicarla rara.
const obras = defineCollection({
  loader: glob({
    pattern: [`${salas}/*.md`, ...privada(`${salas}/*.md`), "!**/index.md"],
    base: "../content",
    // La misma dirección que en Quartz, para que no se rompa ningún enlace.
    generateId: ({ entry }) => id(entry),
  }),
  schema: z.object({
    type: z.enum(TIPOS as [string, ...string[]]),
    title: z.string().optional(),
    year: z.number().int().nullish(),
    // Un autor que es solo un número (un grupo como «2814») llega como number.
    author: z.union([z.string(), z.number()]).transform(String).nullish(),
    rating: z.number().int().min(1).max(10).nullish(),
    status: z.enum(["pending", "in-progress", "finished", "dropped"]).nullish(),
    favorite: z.boolean().nullish(),
    cover: z.string().nullish(),
    tags: z.array(z.string()).nullish(),
    added: z.coerce.date().nullish(),
    finished_on: fechaParcial.nullish(),
    groups: z.array(z.union([z.string(), z.number()]).transform(String)).nullish(),
    hidden: z.union([z.boolean(), z.array(z.enum(OCULTABLES))]).nullish(),
    draft: z.boolean().optional(),
    favorite_tracks: z.number().int().nullish(),
    // Los ids de cada fuente: con ellos dos vitrinas pueden compararse sin
    // fiarse del título.
    appid: z.number().nullish(),
    letterboxd: z.string().nullish(),
    tvmaze: z.number().nullish(),
    mbid: z.string().nullish(),
    wikipedia: z.string().nullish(),
  }),
});

// Los grupos que haces tú: una nota por grupo con su título y, si quieres,
// un texto. Las fichas entran con `groups: [Anime]`. Un grupo que se nombra
// en una ficha y no tiene nota sale igual, con su nombre y sin texto.
const grupos = defineCollection({
  loader: glob({
    pattern: [`${CARPETA_GRUPOS}/*.md`, ...privada(`${CARPETA_GRUPOS}/*.md`)],
    base: "../content",
    generateId: ({ entry }) => id(entry, new RegExp(`^${CARPETA_GRUPOS}/`)),
  }),
  schema: z.object({
    title: z.string().optional(),
    /** Sale en la entrada, debajo de las salas. */
    featured: z.boolean().optional(),
    hidden: z.boolean().optional(),
  }),
});

// Las páginas sueltas de la vault que también salen en la web: los créditos y
// la portada, de la que se toma la presentación que escribe el dueño.
const paginas = defineCollection({
  loader: glob({ pattern: ["creditos.md", "credits.md", "index.md"], base: "../content" }),
  schema: z.object({ title: z.string() }),
});

// Las páginas de autor que escribe scripts/autores.py. De ellas solo se toma
// cómo se llama cada fichero, que es lo que da la dirección: autores.py lo
// pasa a ASCII y le quita el punto final («FromSoftware, Inc.» queda en
// `fromsoftware,-inc`), y así la web no tiene que copiar esa regla.
const autores = defineCollection({
  loader: glob({
    pattern: [`${CARPETA_AUTORES}/*.md`, `!${CARPETA_AUTORES}/index.md`],
    base: "../content",
    generateId: ({ entry }) => slugQuartz(entry.replace(new RegExp(`^${CARPETA_AUTORES}/`), "").replace(/\.md$/, "")),
  }),
  schema: z.object({ title: z.string() }),
});

export const collections = { obras, grupos, paginas, autores };
