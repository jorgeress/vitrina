import { getCollection, type CollectionEntry } from "astro:content";
import { enumerar, separarAutores, slugQuartz, textoCartela } from "./texto";

export * from "./texto";

export type Obra = CollectionEntry<"obras">;
export type Tipo = Obra["data"]["tipo"];

export const SECCIONES = [
  { tipo: "juego", slug: "juegos", nombre: "Juegos", corto: "Juegos", una: "juego", varias: "juegos" },
  { tipo: "peli", slug: "pelis", nombre: "Películas", corto: "Pelis", una: "película", varias: "películas" },
  { tipo: "serie", slug: "series", nombre: "Series", corto: "Series", una: "serie", varias: "series" },
  { tipo: "libro", slug: "libros", nombre: "Libros", corto: "Libros", una: "libro", varias: "libros" },
  { tipo: "album", slug: "musica", nombre: "Música", corto: "Música", una: "disco", varias: "discos" },
] as const;

export type Seccion = (typeof SECCIONES)[number];

/** El color de cada sección es una variable de global.css, con su versión
 * para el tema oscuro. */
export const colorDe = (tipo: Tipo) => `var(--${tipo})`;

export function seccionDe(tipo: Tipo): Seccion {
  return SECCIONES.find((s) => s.tipo === tipo)!;
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

/** El id es `juegos/golf-it!`: sección y nombre de la página, como en Quartz. */
export function ruta(o: Obra): string {
  return url(`${o.id}/`);
}

export function slugObra(o: Obra): string {
  return o.id.split("/").pop()!;
}

/** Un nombre de transición por obra, para que la portada «vuele» de la
 * rejilla a la ficha. Tiene que ser un identificador CSS válido. */
export function transicion(o: Obra): string {
  let h = 0;
  for (const c of o.id) h = (Math.imul(31, h) + c.charCodeAt(0)) | 0;
  return `obra-${(h >>> 0).toString(36)}`;
}

export function portada(o: Obra): string | null {
  const nombre = o.data.portada?.replace(/^\[\[|\]\]$/g, "").split("|")[0];
  return nombre ? url(`portadas/${nombre}`) : null;
}

export const autores = (o: Obra) => separarAutores(o.data.autor);
export const quienFirma = (o: Obra) => enumerar(autores(o));
export const cartela = (o: Obra) => textoCartela(o.body);

let paginasAutor: Map<string, string> | null = null;

/** Nombre del autor → nombre de su página, tal como la escribió autores.py. */
export async function slugsAutores(): Promise<Map<string, string>> {
  paginasAutor ??= new Map((await getCollection("autores")).map((a) => [a.data.title, a.id]));
  return paginasAutor;
}

/** La dirección de la página de un autor: la de su fichero en la vault, que
 * es la que tiene en Quartz. Si autores.py aún no la ha escrito, la que
 * saldría de su nombre. */
export function slugAutor(autor: string, slugs: Map<string, string>): string {
  return slugs.get(autor) ?? slugQuartz(autor.replace(/\.+$/, ""));
}
export const rutaAutor = (autor: string, slugs: Map<string, string>) => url(`autores/${slugAutor(autor, slugs)}/`);
export const rutaTag = (tag: string) => url(`tags/${slugQuartz(tag)}/`);

/** Autores con dos obras o más: el mismo umbral que autores.py. */
export function autoresRepetidos(todas: Obra[]): Map<string, Obra[]> {
  const grupos = new Map<string, Obra[]>();
  for (const o of todas) for (const a of autores(o)) grupos.set(a, [...(grupos.get(a) ?? []), o]);
  return new Map([...grupos].filter(([, lista]) => lista.length >= 2));
}

/** Lo último que entró primero; a igual fecha (las importaciones entran
 * todas el mismo día), por título, para que el orden no baile entre builds. */
export function porAlta(a: Obra, b: Obra): number {
  return (b.data.alta?.getTime() ?? 0) - (a.data.alta?.getTime() ?? 0) || titulo(a).localeCompare(titulo(b), "es");
}

/** Lo mejor primero: favoritos, luego nota, luego lo último que entró. */
export function porAprecio(a: Obra, b: Obra): number {
  return (
    Number(Boolean(b.data.favorito)) - Number(Boolean(a.data.favorito)) ||
    (b.data.nota ?? 0) - (a.data.nota ?? 0) ||
    porAlta(a, b)
  );
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
  // La cita de la fuente ya acaba en «→ Steam»: ese no se repite.
  return lista.filter((f) => !(o.body ?? "").includes(new URL(f.href).hostname));
}

// --- parecidos ---------------------------------------------------------------

export interface Vecina {
  obra: Obra;
  peso: number;
  /** Unida solo por sección y época, a falta de algo mejor: se pinta aparte. */
  debil: boolean;
  /** Lo que comparten, para decirlo: «FromSoftware», «metroidvania». */
  motivos: string[];
}

/**
 * Cuánto se parecen dos obras, y por qué. Compartir autor pesa mucho; cada
 * tag compartido pesa más cuanto más raro es: que dos juegos sean «indie» dice
 * poco, que los dos sean «metroidvania» dice bastante.
 */
function medidor(todas: Obra[]) {
  const frecuencia = new Map<string, number>();
  for (const o of todas) for (const t of o.data.tags ?? []) frecuencia.set(t, (frecuencia.get(t) ?? 0) + 1);
  const rareza = (t: string) => Math.log(todas.length / (frecuencia.get(t) ?? 1));
  const autoresDe = new Map(todas.map((o) => [o.id, autores(o)]));

  return (a: Obra, b: Obra): { peso: number; motivos: string[] } => {
    if (a.id === b.id) return { peso: 0, motivos: [] };
    let peso = 0;
    const motivos: string[] = [];
    const deB = new Set(autoresDe.get(b.id));
    for (const autor of autoresDe.get(a.id)!)
      if (deB.has(autor)) {
        peso += 6;
        motivos.push(autor);
      }
    const tagsB = new Set(b.data.tags ?? []);
    const comunes = (a.data.tags ?? []).filter((t) => tagsB.has(t)).sort((x, y) => rareza(y) - rareza(x));
    for (const t of comunes) peso += rareza(t);
    motivos.push(...comunes.slice(0, 2));
    if (peso > 0 && a.data.tipo === b.data.tipo) peso += 0.5;
    return { peso, motivos };
  };
}

/** Lo mínimo para llamar «parecidas» a dos obras: un tag no del todo común o
 * el mismo autor. Un tag que lleva media colección («rock», «indie») no basta. */
const UMBRAL = 1.6;

const calculados = new Map<string, Map<string, Vecina[]>>();

/**
 * Las vecinas de cada obra. Primero las que se parecen de verdad; a la que no
 * se parece a nada —un disco sin tags ni autor repetido— se le buscan las de
 * su misma sección más cercanas en el tiempo, marcadas como débiles, para que
 * en la constelación no se quede flotando sola.
 */
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
      .map((b) => ({ obra: b, ...parecido(a, b), debil: false }))
      .filter((v) => v.peso >= UMBRAL)
      .sort((x, y) => y.peso - x.peso || cerca(x.obra) - cerca(y.obra));
    if (fuertes.length > 0) {
      mapa.set(a.id, fuertes.slice(0, cuantas));
      continue;
    }
    const cercanas = todas
      .filter((b) => b.id !== a.id && b.data.tipo === a.data.tipo)
      .sort((x, y) => cerca(x) - cerca(y))
      .slice(0, 2)
      .map((b) => ({ obra: b, peso: 1, debil: true, motivos: [] }));
    mapa.set(a.id, cercanas);
  }
  calculados.set(clave, mapa);
  return mapa;
}

export function relacionadas(o: Obra, todas: Obra[], cuantas = 6): Vecina[] {
  return (vecindario(todas, cuantas).get(o.id) ?? []).filter((v) => !v.debil);
}
