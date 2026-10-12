import { getCollection, type CollectionEntry } from "astro:content";

export type Obra = CollectionEntry<"obras">;
export type Tipo = Obra["data"]["tipo"];

export const SECCIONES = [
  { tipo: "juego", slug: "juegos", nombre: "Juegos", corto: "Juegos", una: "juego", varias: "juegos", color: "var(--juego)" },
  { tipo: "peli", slug: "pelis", nombre: "Películas", corto: "Pelis", una: "película", varias: "películas", color: "var(--peli)" },
  { tipo: "serie", slug: "series", nombre: "Series", corto: "Series", una: "serie", varias: "series", color: "var(--serie)" },
  { tipo: "libro", slug: "libros", nombre: "Libros", corto: "Libros", una: "libro", varias: "libros", color: "var(--libro)" },
  { tipo: "album", slug: "musica", nombre: "Música", corto: "Música", una: "disco", varias: "discos", color: "var(--album)" },
] as const;

export type Seccion = (typeof SECCIONES)[number];

export function seccionDe(tipo: Tipo): Seccion {
  return SECCIONES.find((s) => s.tipo === tipo)!;
}

/** «1 disco», «90 discos». */
export function cantidad(n: number, una: string, varias: string): string {
  return `${n} ${n === 1 ? una : varias}`;
}

/** Todas las obras publicadas, las de borrador fuera, igual que en Quartz. */
export async function obras(): Promise<Obra[]> {
  return getCollection("obras", (o) => !o.data.draft);
}

/** Enlaces con la base del sitio (/vitrina), que en local también se usa. */
export function url(ruta = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${base}/${ruta.replace(/^\//, "")}`;
}

export function titulo(o: Obra): string {
  if (o.data.title) return o.data.title;
  const fichero = o.filePath?.split("/").pop() ?? o.id;
  return fichero.replace(/\.md$/, "");
}

/** El id de Astro es `juegos/hollow-knight`: sección y nombre de la página. */
export function ruta(o: Obra): string {
  return url(`${o.id}/`);
}

export function slugObra(o: Obra): string {
  return o.id.split("/").pop()!;
}

export function portada(o: Obra): string | null {
  const nombre = o.data.portada?.replace(/^\[\[|\]\]$/g, "").split("|")[0];
  return nombre ? url(`portadas/${nombre}`) : null;
}

/** Los tags van en inglés y con guiones (`alternative-rock`); se leen mejor
 * como «Alternative rock». */
export function nombreTag(tag: string): string {
  const texto = tag.replace(/-/g, " ");
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

export function mayuscula(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

// --- autores -----------------------------------------------------------------
// La misma regla que `separar()` de scripts/autores.py, para que las páginas de
// autor de la web y las de la vault sean las mismas. La coma separa personas
// («Mike Johnson, Tim Burton») salvo cuando lo que sigue es un sufijo de
// empresa («FromSoftware, Inc.») o un nombre conocido que la lleva dentro.

const SUFIJOS = ["inc", "ltd", "llc", "co", "corp", "gmbh", "s.a", "s.l", "b.v", "pty", "ab", "oy"];
const NOMBRES_CON_COMA = ["tyler, the creator"];

export function autores(o: Obra): string[] {
  const valor = (o.data.autor ?? "").replace(/\[\[(?:[^\]|]*\|)?([^\]]*)\]\]/g, "$1").trim();
  const partes: string[] = [];
  for (const trozo of valor.split(",").map((t) => t.trim())) {
    if (!trozo) continue;
    const ultimo = partes.at(-1);
    const junto = ultimo ? `${ultimo}, ${trozo}`.toLowerCase() : "";
    if (ultimo && (NOMBRES_CON_COMA.includes(junto) || SUFIJOS.includes(trozo.toLowerCase().replace(/\.$/, ""))))
      partes[partes.length - 1] = `${ultimo}, ${trozo}`;
    else partes.push(trozo);
  }
  return partes;
}

/** «A», «A y B», «A, B y C». */
export function listaAutores(nombres: string[]): string {
  if (nombres.length <= 1) return nombres[0] ?? "";
  return `${nombres.slice(0, -1).join(", ")} y ${nombres.at(-1)}`;
}

export function slugAutor(autor: string): string {
  return autor
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

/** Autores con dos obras o más: el mismo umbral que autores.py. */
export function autoresRepetidos(todas: Obra[]): Map<string, Obra[]> {
  const grupos = new Map<string, Obra[]>();
  for (const o of todas) for (const a of autores(o)) grupos.set(a, [...(grupos.get(a) ?? []), o]);
  return new Map([...grupos].filter(([, lista]) => lista.length >= 2));
}

// --- lo que él ha escrito ----------------------------------------------------

/** El texto de la cartela, sin el marco ni el título. */
export function cartela(o: Obra): string | null {
  const lineas = (o.body ?? "").split("\n");
  const inicio = lineas.findIndex((l) => /^>\s*\[!vitrina\]/i.test(l));
  if (inicio === -1) return null;
  const cuerpo: string[] = [];
  for (const l of lineas.slice(inicio + 1)) {
    if (!l.startsWith(">")) break;
    cuerpo.push(l.replace(/^>\s?/, ""));
  }
  const texto = cuerpo.join(" ").replace(/\s+/g, " ").trim();
  return texto || null;
}

/** Lo último que entró primero; a igual fecha (las importaciones entran
 * todas el mismo día), por título, para que el orden no baile entre builds. */
export function porAlta(a: Obra, b: Obra): number {
  return (b.data.alta?.getTime() ?? 0) - (a.data.alta?.getTime() ?? 0) || titulo(a).localeCompare(titulo(b), "es");
}

// --- fuentes -----------------------------------------------------------------

/** Dónde está cada obra en su fuente, a partir del id que guarda la ficha. */
export function fuentes(o: Obra): { nombre: string; href: string }[] {
  const d = o.data;
  const lista: { nombre: string; href: string }[] = [];
  if (d.appid) lista.push({ nombre: "Steam", href: `https://store.steampowered.com/app/${d.appid}/` });
  if (d.letterboxd) lista.push({ nombre: "Letterboxd", href: `https://letterboxd.com/film/${d.letterboxd}/` });
  if (d.tvmaze) lista.push({ nombre: "TVmaze", href: `https://www.tvmaze.com/shows/${d.tvmaze}` });
  if (d.mbid) lista.push({ nombre: "MusicBrainz", href: `https://musicbrainz.org/release-group/${d.mbid}` });
  if (d.wikipedia)
    lista.push({ nombre: "Wikipedia", href: `https://es.wikipedia.org/wiki/${encodeURIComponent(d.wikipedia.replace(/ /g, "_"))}` });
  return lista;
}

// --- parecidos ---------------------------------------------------------------

export interface Vecina {
  obra: Obra;
  peso: number;
  /** Unida solo por sección y época, a falta de algo mejor: se pinta aparte. */
  debil: boolean;
}

/**
 * Cuánto se parecen dos obras. Compartir autor pesa mucho; cada tag
 * compartido pesa más cuanto más raro es: que dos juegos sean «indie» dice
 * poco, que los dos sean «metroidvania» dice bastante.
 */
function medidor(todas: Obra[]) {
  const frecuencia = new Map<string, number>();
  for (const o of todas) for (const t of o.data.tags ?? []) frecuencia.set(t, (frecuencia.get(t) ?? 0) + 1);
  const peso = (t: string) => Math.log(todas.length / (frecuencia.get(t) ?? 1));
  const autoresDe = new Map(todas.map((o) => [o.id, new Set(autores(o))]));

  return (a: Obra, b: Obra): number => {
    if (a.id === b.id) return 0;
    let total = 0;
    const deB = autoresDe.get(b.id)!;
    for (const autor of autoresDe.get(a.id)!) if (deB.has(autor)) total += 6;
    const tagsB = new Set(b.data.tags ?? []);
    for (const t of a.data.tags ?? []) if (tagsB.has(t)) total += peso(t);
    if (total > 0 && a.data.tipo === b.data.tipo) total += 0.5;
    return total;
  };
}

/** Lo mínimo para llamar «parecidas» a dos obras: un tag no del todo común o
 * el mismo autor. Un tag que lleva media colección («rock», «indie») no basta. */
const UMBRAL = 1.6;

/**
 * Las vecinas de cada obra. Primero las que se parecen de verdad; a la que no
 * se parece a nada —un disco sin tags ni autor repetido— se le buscan las de
 * su misma sección más cercanas en el tiempo, marcadas como débiles, para que
 * en la constelación no se quede flotando sola.
 */
const calculados = new Map<string, Map<string, Vecina[]>>();

export function vecindario(todas: Obra[], cuantas: number): Map<string, Vecina[]> {
  // Cada ficha pide las suyas y el cálculo es el mismo para todas: se hace una
  // vez por build y no 210.
  const clave = `${cuantas}:${todas.map((o) => o.id).join(",")}`;
  if (calculados.has(clave)) return calculados.get(clave)!;
  const parecido = medidor(todas);
  const mapa = new Map<string, Vecina[]>();
  for (const a of todas) {
    // A igual parecido, primero la más cercana en el tiempo: si no, los
    // empates salían en orden alfabético, que no dice nada.
    const cerca = (b: Obra) => Math.abs((b.data.year ?? 0) - (a.data.year ?? 0));
    const fuertes = todas
      .map((b) => ({ obra: b, peso: parecido(a, b), debil: false }))
      .filter((v) => v.peso >= UMBRAL)
      .sort((x, y) => y.peso - x.peso || cerca(x.obra) - cerca(y.obra));
    if (fuertes.length > 0) {
      mapa.set(a.id, fuertes.slice(0, cuantas));
      continue;
    }
    const cercanas = todas
      .filter((b) => b.id !== a.id && b.data.tipo === a.data.tipo)
      .map((b) => ({ obra: b, peso: 1, debil: true, dist: Math.abs((b.data.year ?? 0) - (a.data.year ?? 0)) }))
      .sort((x, y) => x.dist - y.dist)
      .slice(0, 2)
      .map(({ dist: _, ...v }) => v);
    mapa.set(a.id, cercanas);
  }
  calculados.set(clave, mapa);
  return mapa;
}

export function relacionadas(o: Obra, todas: Obra[], cuantas = 6): Obra[] {
  return (vecindario(todas, cuantas).get(o.id) ?? []).filter((v) => !v.debil).map((v) => v.obra);
}
