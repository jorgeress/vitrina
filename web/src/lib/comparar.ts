// Comparar dos vitrinas a partir de sus vitrina.json, sin servidor: lo hace
// el navegador de quien mira. Va aparte de la página para poder probarlo.

export interface Pieza {
  titulo: string;
  tipo: string;
  year: number | null;
  autores: string[];
  nota: number | null;
  estado: string | null;
  favorito: boolean;
  tags: string[];
  ids: Record<string, string | number>;
  cartela: string | null;
  url: string;
  portada?: string | null;
}

export interface Vitrina {
  version: number;
  obras: Pieza[];
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
  return deIds.length > 0 ? deIds : [`${p.tipo}:${normal(p.titulo)}:${p.year ?? ""}`];
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
  for (const p of suya.obras) for (const c of claves(p)) indice.set(c, p);

  const comunes: Pareja[] = [];
  const emparejadas = new Set<Pieza>();
  const soloMias: Pieza[] = [];
  for (const p of mia.obras) {
    const otra = claves(p)
      .map((c) => indice.get(c))
      .find((o) => o && !emparejadas.has(o));
    if (otra) {
      comunes.push({ mia: p, suya: otra });
      emparejadas.add(otra);
    } else soloMias.push(p);
  }
  const soloSuyas = suya.obras.filter((p) => !emparejadas.has(p));
  const total = comunes.length + soloMias.length + soloSuyas.length;
  const aprecio = (p: Pieza) => (p.favorito ? 100 : 0) + (p.nota ?? 0);

  return {
    comunes,
    soloMias,
    soloSuyas,
    afinidad: total ? comunes.length / total : 0,
    favoritasDeLosDos: comunes.filter((c) => c.mia.favorito && c.suya.favorito),
    desacuerdos: comunes
      .filter((c) => c.mia.nota && c.suya.nota && Math.abs(c.mia.nota - c.suya.nota) >= 3)
      .sort((a, b) => Math.abs(b.mia.nota! - b.suya.nota!) - Math.abs(a.mia.nota! - a.suya.nota!)),
    recomendaciones: [...soloSuyas].sort((a, b) => aprecio(b) - aprecio(a)),
  };
}

/** De lo que pegue alguien (la portada de su vitrina, una ficha o el propio
 * json) a la dirección de su vitrina.json. */
export function direccionJSON(texto: string): string {
  let url = texto.trim();
  if (!/^https?:\/\//.test(url)) url = `https://${url}`;
  const u = new URL(url);
  if (u.pathname.endsWith(".json")) return u.href;
  // Una ficha cuelga de una sala: se sube hasta la raíz de la vitrina, que
  // es lo que va antes de /juegos/, /pelis/... o del final.
  const trozos = u.pathname.split("/").filter(Boolean);
  const sala = trozos.findIndex((t) => ["juegos", "pelis", "series", "libros", "musica", "autores", "tags"].includes(t));
  const raiz = sala === -1 ? trozos : trozos.slice(0, sala);
  return `${u.origin}/${raiz.map((t) => `${t}/`).join("")}vitrina.json`;
}
