import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  enumerar,
  nombreTag,
  primerParrafo,
  recortar,
  separarAutores,
  slugQuartz,
  textoCartela,
} from "../src/lib/texto.ts";

const VAULT = join(import.meta.dirname, "..", "..", "content");
const SECCIONES = ["juegos", "pelis", "series", "libros", "musica"];

test("las direcciones son las mismas que en Quartz", () => {
  // Sacadas de la web de Quartz tal cual: si cambian, se rompen enlaces.
  const casos: [string, string][] = [
    ["juegos/(the) Gnorp Apologue", "juegos/(the)-gnorp-apologue"],
    ["juegos/Golf It!", "juegos/golf-it!"],
    ["series/Love, Death & Robots", "series/love,-death--and--robots"],
    ["pelis/Howl's Moving Castle", "pelis/howl's-moving-castle"],
    ["musica/A.D.R.O.M.I.C.F.M.S. 2", "musica/a.d.r.o.m.i.c.f.m.s.-2"],
    ["pelis/Kill Bill Vol. 1", "pelis/kill-bill-vol.-1"],
  ];
  for (const [fichero, url] of casos) assert.equal(slugQuartz(fichero), url);
});

test("los autores se reparten como en autores.py, con todas las fichas", () => {
  const valores: string[] = [];
  for (const seccion of SECCIONES)
    for (const f of readdirSync(join(VAULT, seccion))) {
      if (!f.endsWith(".md") || f === "index.md") continue;
      const texto = readFileSync(join(VAULT, seccion, f), "utf8");
      const autor = texto.match(/^autor:[ \t]*(.*)$/m)?.[1]?.trim().replace(/^"(.*)"$/, "$1");
      if (autor) valores.push(autor);
    }
  assert.ok(valores.length > 100, "no ha encontrado las fichas");

  const python = execFileSync(
    "python3",
    [
      "-c",
      "import json,sys; sys.path.insert(0, sys.argv[1]); from autores import separar; " +
        "print(json.dumps([separar(v) for v in json.load(sys.stdin)]))",
      join(import.meta.dirname, "..", "..", "scripts"),
    ],
    { input: JSON.stringify(valores), encoding: "utf8" },
  );
  const esperados: string[][] = JSON.parse(python);
  valores.forEach((v, i) => assert.deepEqual(separarAutores(v), esperados[i], v));
});

test("casos de autores que tienen trampa", () => {
  assert.deepEqual(separarAutores("QLOC, FromSoftware, Inc."), ["QLOC", "FromSoftware, Inc."]);
  assert.deepEqual(separarAutores("Tyler, The Creator"), ["Tyler, The Creator"]);
  assert.deepEqual(separarAutores("Yung Beef, Steve Lean"), ["Yung Beef", "Steve Lean"]);
  assert.deepEqual(separarAutores(""), []);
  assert.equal(enumerar(["A", "B", "C"]), "A, B y C");
});

test("los tags se leen como palabras", () => {
  assert.equal(nombreTag("alternative-rock"), "Alternative rock");
  assert.equal(nombreTag("rpg"), "RPG");
  assert.equal(nombreTag("r&b"), "R&B");
});

test("la cartela sale entera y sin el marco", () => {
  const cuerpo = "> [!vitrina] Por qué está en la vitrina\n> Una línea\n> y otra.\n\n> [!quote] De qué va\n> Otra cosa";
  assert.equal(textoCartela(cuerpo), "Una línea y otra.");
  assert.equal(textoCartela("> [!quote] De qué va\n> Nada mío"), null);
});

test("la presentación de la portada es el primer párrafo de index.md", () => {
  const cuerpo = "\nMi colección personal de lo que juego,\nveo y escucho.\n\n- [[juegos/index|Juegos]]\n";
  assert.equal(primerParrafo(cuerpo), "Mi colección personal de lo que juego, veo y escucho.");
  assert.equal(recortar("uno dos tres cuatro", 9), "uno dos…");
  // Sin «arriba.…»: el punto se va antes de los puntos suspensivos.
  assert.equal(recortar("escribirlo aquí arriba. Bórralo luego", 25), "escribirlo aquí arriba…");
});
