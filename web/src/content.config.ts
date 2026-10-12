import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";
import { slugQuartz } from "./lib/texto";

// Las mismas fichas que edita Obsidian y rellenan los scripts. El esquema es
// el contrato: si una ficha trae `nota: 11` o un estado mal escrito, la web
// no se construye y el error dice cuál es, en vez de publicarla rara.
const obras = defineCollection({
  loader: glob({
    pattern: ["{juegos,pelis,series,libros,musica}/*.md", "!**/index.md"],
    base: "../content",
    // La misma dirección que en Quartz, para que no se rompa ningún enlace.
    generateId: ({ entry }) => slugQuartz(entry.replace(/\.md$/, "")),
  }),
  schema: z.object({
    tipo: z.enum(["juego", "peli", "serie", "libro", "album"]),
    title: z.string().optional(),
    year: z.number().int().nullish(),
    // Un autor que es solo un número (un grupo como «2814») llega como number.
    autor: z.union([z.string(), z.number()]).transform(String).nullish(),
    nota: z.number().int().min(1).max(10).nullish(),
    estado: z.enum(["pendiente", "en curso", "terminado", "abandonado"]).nullish(),
    favorito: z.boolean().nullish(),
    portada: z.string().nullish(),
    tags: z.array(z.string()).nullish(),
    alta: z.coerce.date().nullish(),
    draft: z.boolean().optional(),
    // Los ids de cada fuente: con ellos dos vitrinas pueden compararse sin
    // fiarse del título.
    appid: z.number().nullish(),
    letterboxd: z.string().nullish(),
    tvmaze: z.number().nullish(),
    mbid: z.string().nullish(),
    wikipedia: z.string().nullish(),
  }),
});

// Las páginas sueltas de la vault que también salen en la web: los créditos y
// la portada, de la que se toma la presentación que él escribe.
const paginas = defineCollection({
  loader: glob({ pattern: ["creditos.md", "index.md"], base: "../content" }),
  schema: z.object({ title: z.string() }),
});

// Las páginas de autor que escribe scripts/autores.py. De ellas solo se toma
// cómo se llama cada fichero, que es lo que da la dirección: autores.py lo
// pasa a ASCII y le quita el punto final («FromSoftware, Inc.» queda en
// `fromsoftware,-inc`), y así la web no tiene que copiar esa regla.
const autores = defineCollection({
  loader: glob({
    pattern: ["autores/*.md", "!autores/index.md"],
    base: "../content",
    generateId: ({ entry }) => slugQuartz(entry.replace(/^autores\//, "").replace(/\.md$/, "")),
  }),
  schema: z.object({ title: z.string() }),
});

export const collections = { obras, paginas, autores };
