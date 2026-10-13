// Lo que no depende de Astro: cómo se forman las direcciones, cómo se reparte
// el campo `autor` y cómo se escriben las cosas. Va aparte para poder probarlo
// con `node --test` sin levantar nada (ver test/texto.test.ts).

/**
 * La dirección de una página, con la misma regla que usaba Quartz, que era la
 * web de antes. Así los enlaces que ya circulaban siguen llevando al mismo
 * sitio: «Golf It!.md» es `golf-it!`, y «Love, Death & Robots» es
 * `love,-death--and--robots`. Si se cambia, se rompen.
 */
export function slugQuartz(ruta: string): string {
  return ruta
    .split("/")
    .map((trozo) =>
      trozo
        .replace(/\s/g, "-")
        .replace(/&/g, "-and-")
        .replace(/%/g, "-percent")
        .replace(/\?/g, "")
        .replace(/#/g, "")
        .replace(/[<>:"|*]/g, "")
        .toLowerCase(),
    )
    .join("/")
    .replace(/\/$/, "");
}

// --- autores -----------------------------------------------------------------
// La misma regla que `separar()` de scripts/autores.py, y test/texto.test.ts
// comprueba que las dos dan lo mismo con todas las fichas. La coma separa
// personas («Mike Johnson, Tim Burton») salvo cuando lo que sigue es un sufijo
// de empresa («FromSoftware, Inc.») o un nombre conocido que la lleva dentro.

const SUFIJOS = ["inc", "ltd", "llc", "co", "corp", "gmbh", "s.a", "s.l", "b.v", "pty", "ab", "oy"];
const NOMBRES_CON_COMA = ["tyler, the creator"];

export function separarAutores(valor: string | null | undefined): string[] {
  const limpio = (valor ?? "").replace(/\[\[(?:[^\]|]*\|)?([^\]]*)\]\]/g, "$1").trim();
  const partes: string[] = [];
  for (const trozo of limpio.split(",").map((t) => t.trim())) {
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
export function enumerar(nombres: string[]): string {
  if (nombres.length <= 1) return nombres[0] ?? "";
  return `${nombres.slice(0, -1).join(", ")} y ${nombres.at(-1)}`;
}

// --- palabras ----------------------------------------------------------------

/** «1 disco», «90 discos». */
export function cantidad(n: number, una: string, varias: string): string {
  return `${n} ${n === 1 ? una : varias}`;
}

export function mayuscula(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** Los tags van en inglés y con guiones (`alternative-rock`); se leen mejor
 * como «Alternative rock». Las siglas conocidas se quedan en mayúsculas. */
const SIGLAS = new Set(["rpg", "mmo", "mmorpg", "fps", "edm", "idm", "uk", "us", "jrpg", "r&b"]);

export function nombreTag(tag: string): string {
  const palabras = tag.split("-").map((p) => (SIGLAS.has(p) ? p.toUpperCase() : p));
  return mayuscula(palabras.join(" "));
}

/**
 * Cómo se dice cada estado en la vitrina. Lo pendiente está «en el almacén»,
 * esperando su turno de salir; lo abandonado se «retira de la vitrina». Son
 * los rótulos de la lista de ideas del README.
 */
export const ESTADOS = {
  terminado: "Terminado",
  "en curso": "En curso",
  pendiente: "En el almacén",
  abandonado: "Retirado de la vitrina",
} as const;

export type Estado = keyof typeof ESTADOS;

// --- lo que él ha escrito ----------------------------------------------------

/** El texto de la cartela de una ficha, sin el marco ni el título. */
export function textoCartela(cuerpo: string | undefined): string | null {
  const lineas = (cuerpo ?? "").split("\n");
  const inicio = lineas.findIndex((l) => /^>\s*\[!vitrina\]/i.test(l));
  if (inicio === -1) return null;
  const parrafo: string[] = [];
  for (const l of lineas.slice(inicio + 1)) {
    if (!l.startsWith(">")) break;
    parrafo.push(l.replace(/^>\s?/, ""));
  }
  const texto = parrafo.join(" ").replace(/\s+/g, " ").trim();
  return texto || null;
}

/** El primer párrafo de una página de la vault, sin el frontmatter: lo que
 * se escribe en index.md es la presentación de la portada. */
export function primerParrafo(cuerpo: string | undefined): string | null {
  const bloques = (cuerpo ?? "").split(/\n\s*\n/).map((b) => b.trim());
  const parrafo = bloques.find((b) => b && !/^[-#>!*|[]/.test(b));
  return parrafo ? parrafo.replace(/\s+/g, " ") : null;
}

/** Recorta en la última palabra entera antes del límite. */
export function recortar(texto: string, limite: number): string {
  if (texto.length <= limite) return texto;
  return texto.slice(0, limite).replace(/\s+\S*$/, "").replace(/[\s.,;:]+$/, "") + "…";
}
