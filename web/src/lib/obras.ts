import { getCollection, type CollectionEntry } from "astro:content";
import { CARPETAS, CARPETA_PRIVADA, IDIOMA, TIPOS, type Tipo } from "../config";
import { VISTAZO } from "../content.config";
import { t } from "../i18n";
import { CALLOUT_CARTELA, cantidad, enumerar, separarAutores, sinCartela, slugQuartz, textoCartela } from "./texto";

export * from "./texto";
export { VISTAZO };
export type { Tipo };

export type Obra = CollectionEntry<"obras">;

export const SECCIONES = TIPOS.map((tipo) => ({ tipo, slug: CARPETAS[tipo], ...t.salas[tipo] }));

export type Seccion = (typeof SECCIONES)[number];

export function seccionDe(tipo: string): Seccion {
  return SECCIONES.find((s) => s.tipo === tipo)!;
}

/** Ordenar textos como se ordenan en el idioma de la vitrina. */
export const comparaTexto = (a: string, b: string) => a.localeCompare(b, IDIOMA);

// --- qué se ve ---------------------------------------------------------------
// Hay tres maneras de que algo no salga en la web publicada, de menos a más:
//
//   draft: true     un borrador, aún sin revisar (lo que entra importado).
//   hidden: true    oculta: no sale en la web, pero el fichero está en el repo,
//                   que es público. Sirve para que no se vea, no para que sea
//                   secreto. Con una lista (`hidden: [rating, label]`) la
//                   ficha sale y lo que se oculta son esos campos.
//   carpeta privada la que dice `private` en vitrine.config.json, que git no
//                   sube: ni la web ni GitHub la ven nunca.
//
// En el vistazo (scripts/vistazo.py) sale todo, marcado.

export type Marca = "borrador" | "oculta" | "privada";

export function marcas(o: Obra): Marca[] {
  const lista: Marca[] = [];
  if (o.data.draft) lista.push("borrador");
  if (o.data.hidden === true) lista.push("oculta");
  if (esPrivada(o)) lista.push("privada");
  return lista;
}

export function esPrivada(o: Obra): boolean {
  return (o.filePath ?? "").includes(`/${CARPETA_PRIVADA}/`);
}

/** Lo que se queda fuera de una ficha pública con `hidden: [...]`. */
function sinLoOculto(o: Obra): Obra {
  const ocultos = Array.isArray(o.data.hidden) ? o.data.hidden : [];
  if (ocultos.length === 0 || VISTAZO) return o;
  const data = { ...o.data };
  if (ocultos.includes("rating")) data.rating = null;
  if (ocultos.includes("status")) data.status = null;
  if (ocultos.includes("favorite")) data.favorite = null;
  if (ocultos.includes("finished_on")) data.finished_on = null;
  if (ocultos.includes("groups")) data.groups = null;
  if (ocultos.includes("added")) data.added = null;
  if (!ocultos.includes("label")) return { ...o, data };
  // La cartela se quita del texto y del HTML ya hecho: no basta con no
  // pintarla, tiene que no estar en la página.
  const lineas = (o.body ?? "").split("\n");
  const inicio = lineas.findIndex((l) => CALLOUT_CARTELA.test(l));
  let fin = inicio;
  while (inicio !== -1 && fin < lineas.length && lineas[fin].startsWith(">")) fin++;
  const body = inicio === -1 ? o.body : [...lineas.slice(0, inicio), ...lineas.slice(fin)].join("\n");
  const rendered = o.rendered && { ...o.rendered, html: sinCartela(o.rendered.html) };
  return { ...o, data, body, rendered };
}

let cache: Promise<Obra[]> | null = null;

export function obras(): Promise<Obra[]> {
  cache ??= getCollection("obras").then((todas) =>
    todas.filter((o) => VISTAZO || marcas(o).length === 0).map(sinLoOculto),
  );
  return cache;
}

// --- direcciones ---------------------------------------------------------------

/** Enlaces con la base del sitio (/vitrina), que en local también se usa. */
export function url(ruta = ""): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${base}/${ruta.replace(/^\//, "")}`;
}

/** La dirección de una de las páginas fijas, en el idioma de la vitrina:
 * `ruta("autores")` es /autores/ en español y /authors/ en inglés. */
export const rutaFija = (pagina: keyof typeof t.rutas, resto = "") => url(`${t.rutas[pagina]}/${resto}`);

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
  const nombre = o.data.cover?.replace(/^\[\[|\]\]$/g, "").split("|")[0];
  return nombre ? url(`portadas/${nombre}`) : null;
}

/** La tarjeta para compartir la ficha, que hace la integración al construir. */
export const tarjeta = (o: Obra) => url(`tarjetas/${o.id.replace(/[^a-z0-9/-]+/gi, "_")}.png`);

export const autores = (o: Obra) => separarAutores(o.data.author);
export const quienFirma = (o: Obra) => enumerar(autores(o), t.y);
export const cartela = (o: Obra) => textoCartela(o.body);
export const piezas = (n: number) => cantidad(n, t.pieza, t.piezas);

let paginasAutor: Map<string, string> | null = null;

/** Nombre del autor → nombre de su página, tal como la escribió autores.py. */
export async function slugsAutores(): Promise<Map<string, string>> {
  paginasAutor ??= new Map((await getCollection("autores")).map((a) => [a.data.title, a.id]));
  return paginasAutor;
}

/** La dirección de la página de un autor: la de su fichero en la vault, que
 * es la que tenía con Quartz. Si autores.py aún no la ha escrito, la que
 * saldría de su nombre. */
export function slugAutor(autor: string, slugs: Map<string, string>): string {
  return slugs.get(autor) ?? slugQuartz(autor.replace(/\.+$/, ""));
}
export const rutaAutor = (autor: string, slugs: Map<string, string>) => rutaFija("autores", `${slugAutor(autor, slugs)}/`);
export const rutaTag = (tag: string) => rutaFija("tags", `${slugQuartz(tag)}/`);

/** Autores con dos obras o más: el mismo umbral que autores.py. */
export function autoresRepetidos(todas: Obra[]): Map<string, Obra[]> {
  const grupos = new Map<string, Obra[]>();
  for (const o of todas) for (const a of autores(o)) grupos.set(a, [...(grupos.get(a) ?? []), o]);
  return new Map([...grupos].filter(([, lista]) => lista.length >= 2));
}

/** Lo último que entró primero; a igual fecha (las importaciones entran
 * todas el mismo día), por título, para que el orden no baile entre builds. */
export function porAlta(a: Obra, b: Obra): number {
  return (b.data.added?.getTime() ?? 0) - (a.data.added?.getTime() ?? 0) || comparaTexto(titulo(a), titulo(b));
}

/** Lo mejor primero: favoritos, luego nota, luego lo último que entró. */
export function porAprecio(a: Obra, b: Obra): number {
  return (
    Number(Boolean(b.data.favorite)) - Number(Boolean(a.data.favorite)) ||
    (b.data.rating ?? 0) - (a.data.rating ?? 0) ||
    porAlta(a, b)
  );
}

// --- fechas ------------------------------------------------------------------------

/** «mayo de 2024» o «3 de mayo de 2024», con la precisión que tenga. */
export function fechaParcial(texto: string): string {
  const [y, m, d] = texto.split("-").map(Number);
  if (!m) return String(y);
  const fecha = new Date(Date.UTC(y, m - 1, d || 1));
  const opciones: Intl.DateTimeFormatOptions = { month: "long", year: "numeric", timeZone: "UTC" };
  if (d) opciones.day = "numeric";
  return fecha.toLocaleDateString(t.locale, opciones);
}

export const mesYAño = (fecha: Date) =>
  fecha.toLocaleDateString(t.locale, { month: "long", year: "numeric", timeZone: "UTC" });

export const añoTerminada = (o: Obra) => (o.data.finished_on ? Number(o.data.finished_on.slice(0, 4)) : null);
export const añoAlta = (o: Obra) => o.data.added?.getUTCFullYear() ?? null;

/** Los años del anuario: los que tienen algo terminado o algo que entró. */
export function años(todas: Obra[]): number[] {
  const hay = new Set<number>();
  for (const o of todas) for (const y of [añoTerminada(o), añoAlta(o)]) if (y) hay.add(y);
  return [...hay].sort((a, b) => b - a);
}

/** El año en que se abrió la vitrina: el de la primera alta. Ese año entra
 * de golpe todo lo que ya se tenía, y el anuario lo dice. */
export function añoDeApertura(todas: Obra[]): number | null {
  const altas = todas.map(añoAlta).filter((y): y is number => y !== null);
  return altas.length ? Math.min(...altas) : null;
}

// --- grupos --------------------------------------------------------------------------

export interface Grupo {
  slug: string;
  nombre: string;
  /** La nota del grupo, con su texto, si la tiene. */
  nota: CollectionEntry<"grupos"> | null;
  destacado: boolean;
  obras: Obra[];
}

let gruposCache: Promise<Grupo[]> | null = null;

/**
 * Los grupos: los que tienen nota en la carpeta de grupos y los que solo se
 * nombran en alguna ficha (`groups: [Anime]`), juntos por su dirección. Uno
 * con `hidden: true` en su nota no sale, y sus fichas tampoco dicen que
 * están en él.
 */
export function grupos(): Promise<Grupo[]> {
  gruposCache ??= (async () => {
    const notas = await getCollection("grupos");
    const porSlug = new Map<string, Grupo>();
    const ocultos = new Set<string>();
    for (const n of notas) {
      if (n.data.hidden && !VISTAZO) {
        ocultos.add(n.id);
        continue;
      }
      porSlug.set(n.id, {
        slug: n.id,
        nombre: n.data.title ?? n.filePath?.split("/").pop()?.replace(/\.md$/, "") ?? n.id,
        nota: n.body?.trim() ? n : null,
        destacado: Boolean(n.data.featured),
        obras: [],
      });
    }
    for (const o of await obras())
      for (const nombre of o.data.groups ?? []) {
        const slug = slugQuartz(nombre);
        if (ocultos.has(slug)) continue;
        if (!porSlug.has(slug)) porSlug.set(slug, { slug, nombre, nota: null, destacado: false, obras: [] });
        porSlug.get(slug)!.obras.push(o);
      }
    return [...porSlug.values()]
      .filter((g) => g.obras.length > 0)
      .map((g) => ({ ...g, obras: g.obras.sort(porAprecio) }))
      .sort((a, b) => Number(b.destacado) - Number(a.destacado) || b.obras.length - a.obras.length || comparaTexto(a.nombre, b.nombre));
  })();
  return gruposCache;
}

export const rutaGrupo = (g: Grupo) => rutaFija("grupos", `${g.slug}/`);

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
    lista.push({
      nombre: "Wikipedia",
      href: `https://${IDIOMA}.wikipedia.org/wiki/${encodeURIComponent(d.wikipedia.replace(/ /g, "_"))}`,
    });
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
    if (peso > 0 && a.data.type === b.data.type) peso += 0.5;
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
      .filter((b) => b.id !== a.id && b.data.type === a.data.type)
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
