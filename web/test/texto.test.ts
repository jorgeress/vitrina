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
  sinCartela,
  slugQuartz,
  textoCartela,
} from "../src/lib/texto.ts";

const RAIZ = join(import.meta.dirname, "..", "..");
const VAULT = join(RAIZ, "content");
// Las carpetas de las salas, de la misma configuración que leen la web y los scripts.
const CARPETAS = JSON.parse(readFileSync(join(RAIZ, "vitrine.config.json"), "utf8")).folders;
const SECCIONES = ["game", "film", "series", "book", "album"].map((t) => CARPETAS[t]);

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
      const autor = texto.match(/^author:[ \t]*(.*)$/m)?.[1]?.trim().replace(/^"(.*)"$/, "$1");
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

test("«y» o «and», según el idioma", () => {
  assert.equal(enumerar(["A", "B", "C"]), "A, B y C");
  assert.equal(enumerar(["A", "B"], "and"), "A and B");
});

test("una cartela oculta no queda en la página, y lo demás sí", () => {
  const html =
    '<div class="callout" data-callout="vitrina" data-collapsible="false"><div class="callout-title"><div class="callout-title-text">Por qué</div></div>' +
    '<div class="callout-content"><p>Lo mío.</p></div></div>\n<div class="callout" data-callout="quote"><p>De qué va</p></div>';
  const limpio = sinCartela(html);
  assert.ok(!limpio.includes("Lo mío"));
  assert.ok(limpio.includes("De qué va"));
  assert.equal(sinCartela("<p>sin cartela</p>"), "<p>sin cartela</p>");
  // En una vitrina en inglés el callout es [!vitrine], y vale igual.
  assert.ok(!sinCartela('<div class="callout" data-callout="vitrine"><div><p>Mine.</p></div></div>').includes("Mine"));
  assert.equal(textoCartela("> [!vitrine] Why it's on display\n> Mine."), "Mine.");
});
