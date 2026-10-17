// Comparar dos vitrinas a partir de sus vitrine.json, sin servidor: lo hace
// el navegador de quien mira. Va aparte de la página para poder probarlo.
//
// Las claves del fichero van en inglés, como las de las fichas, para que dos
// vitrinas en idiomas distintos se puedan comparar igual.

export interface Pieza {
  title: string;
  type: string;
  year: number | null;
  authors: string[];
  rating: number | null;
  status: string | null;
  favorite: boolean;
  tags: string[];
  ids: Record<string, string | number>;
  opinion: string | null;
  /** El nombre de antes de `opinion`, en las vitrinas que aún no se han rehecho. */
  label?: string | null;
  url: string;
  cover?: string | null;
}

export interface Vitrina {
  format?: string;
  version: number;
  works: Pieza[];
}

/** Si lo que se ha leído tiene pinta de vitrine.json. */
export function esVitrina(datos: unknown): datos is Vitrina {
  return Array.isArray((datos as Vitrina | null)?.works);
}

/** Lo que se compara de un título: sin tildes, mayúsculas ni signos. */
export function normal(texto: string): string {
  return texto
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

/**
 * Las claves por las que se reconoce una pieza. Primero los ids de sus
 * fuentes, que no dejan dudas; si no tiene ninguno, tipo, título y año. Dos
 * piezas son la misma si comparten una clave cualquiera.
 */
export function claves(p: Pieza): string[] {
  const deIds = Object.entries(p.ids ?? {}).map(([fuente, id]) => `${fuente}:${String(id).toLowerCase()}`);
  return deIds.length > 0 ? deIds : [`${p.type}:${normal(p.title)}:${p.year ?? ""}`];
}

export interface Pareja {
  mia: Pieza;
  suya: Pieza;
}

export interface Comparacion {
  comunes: Pareja[];
  soloMias: Pieza[];
  soloSuyas: Pieza[];
  /** Comunes entre todas las distintas, de 0 a 1. */
  afinidad: number;
  /** Las que los dos tienen en lo mejor de lo mejor. */
  favoritasDeLosDos: Pareja[];
  /** Las que los dos han puntuado y con tres puntos o más de diferencia. */
  desacuerdos: Pareja[];
  /** Lo suyo que yo no tengo, lo que más le gusta primero. */
  recomendaciones: Pieza[];
}

export function comparar(mia: Vitrina, suya: Vitrina): Comparacion {
  const indice = new Map<string, Pieza>();
  for (const p of suya.works) for (const c of claves(p)) indice.set(c, p);

  const comunes: Pareja[] = [];
  const emparejadas = new Set<Pieza>();
  const soloMias: Pieza[] = [];
  for (const p of mia.works) {
    const otra = claves(p)
      .map((c) => indice.get(c))
      .find((o) => o && !emparejadas.has(o));
    if (otra) {
      comunes.push({ mia: p, suya: otra });
      emparejadas.add(otra);
    } else soloMias.push(p);
  }
  const soloSuyas = suya.works.filter((p) => !emparejadas.has(p));
  const total = comunes.length + soloMias.length + soloSuyas.length;
  const aprecio = (p: Pieza) => (p.favorite ? 100 : 0) + (p.rating ?? 0);

  return {
    comunes,
    soloMias,
    soloSuyas,
    afinidad: total ? comunes.length / total : 0,
    favoritasDeLosDos: comunes.filter((c) => c.mia.favorite && c.suya.favorite),
    desacuerdos: comunes
      .filter((c) => c.mia.rating && c.suya.rating && Math.abs(c.mia.rating - c.suya.rating) >= 3)
      .sort((a, b) => Math.abs(b.mia.rating! - b.suya.rating!) - Math.abs(a.mia.rating! - a.suya.rating!)),
    recomendaciones: [...soloSuyas].sort((a, b) => aprecio(b) - aprecio(a)),
  };
}

/**
 * Dónde puede estar el vitrine.json de lo que pegue alguien: la portada de
 * su vitrina, una ficha, una sala o el propio fichero. No se sabe cómo se
 * llaman sus salas —van en su idioma—, así que se prueba subiendo carpeta a
 * carpeta, de la más honda a la raíz.
 */
export function direccionesJSON(texto: string): string[] {
  let url = texto.trim();
  if (!/^https?:\/\//.test(url)) url = `https://${url}`;
  const u = new URL(url);
  if (u.pathname.endsWith(".json")) return [u.href];
  const trozos = u.pathname.split("/").filter(Boolean);
  const candidatas: string[] = [];
  for (let n = trozos.length; n >= 0; n--)
    candidatas.push(`${u.origin}/${trozos.slice(0, n).map((t) => `${t}/`).join("")}vitrine.json`);
  return candidatas;
}
