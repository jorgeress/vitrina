import { test } from "node:test";
import assert from "node:assert/strict";
import { comparar, direccionesJSON, esVitrina, type Pieza, type Vitrina } from "../src/lib/comparar.ts";

const pieza = (title: string, extra: Partial<Pieza> = {}): Pieza => ({
  title,
  type: "game",
  year: 2020,
  authors: [],
  rating: null,
  status: null,
  favorite: false,
  tags: [],
  ids: {},
  opinion: null,
  url: "",
  ...extra,
});
const vitrina = (...works: Pieza[]): Vitrina => ({ format: "vitrine", version: 1, works });

test("dos piezas son la misma si comparten un id, aunque el título cambie", () => {
  const r = comparar(
    vitrina(pieza("El viaje de Chihiro", { type: "film", ids: { letterboxd: "spirited-away" } })),
    vitrina(pieza("Spirited Away", { type: "film", ids: { letterboxd: "spirited-away" } })),
  );
  assert.equal(r.comunes.length, 1);
  assert.equal(r.afinidad, 1);
});

test("sin ids se reconocen por tipo, título y año, sin tildes ni signos", () => {
  const r = comparar(vitrina(pieza("Pokémon: Rojo")), vitrina(pieza("pokemon rojo")));
  assert.equal(r.comunes.length, 1);
  const distintoAño = comparar(vitrina(pieza("Dune", { year: 1984 })), vitrina(pieza("Dune", { year: 2021 })));
  assert.equal(distintoAño.comunes.length, 0);
});

test("la afinidad, los desacuerdos y lo que recomendaría la otra", () => {
  const a = vitrina(
    pieza("A", { ids: { appid: 1 }, rating: 9, favorite: true }),
    pieza("B", { ids: { appid: 2 }, rating: 3 }),
    pieza("Solo mía", { ids: { appid: 3 } }),
  );
  const b = vitrina(
    pieza("A", { ids: { appid: 1 }, rating: 10, favorite: true }),
    pieza("B", { ids: { appid: 2 }, rating: 9 }),
    pieza("Suya normal", { ids: { appid: 4 }, rating: 6 }),
    pieza("Suya favorita", { ids: { appid: 5 }, favorite: true }),
  );
  const r = comparar(a, b);
  assert.equal(r.comunes.length, 2);
  assert.equal(r.afinidad, 2 / 5);
  assert.deepEqual(r.favoritasDeLosDos.map((c) => c.mia.title), ["A"]);
  assert.deepEqual(r.desacuerdos.map((c) => c.mia.title), ["B"]);
  assert.deepEqual(r.recomendaciones.map((p) => p.title), ["Suya favorita", "Suya normal"]);
});

test("de cualquier enlace de una vitrina se prueba subiendo hasta su vitrine.json", () => {
  assert.deepEqual(direccionesJSON("amiga.github.io/vitrina/"), [
    "https://amiga.github.io/vitrina/vitrine.json",
    "https://amiga.github.io/vitrine.json",
  ]);
  // Una ficha en inglés: las salas se llaman distinto y da igual.
  assert.deepEqual(direccionesJSON("https://friend.github.io/shelf/games/balatro/").slice(-2), [
    "https://friend.github.io/shelf/vitrine.json",
    "https://friend.github.io/vitrine.json",
  ]);
  assert.deepEqual(direccionesJSON("https://otra.es/vitrine.json"), ["https://otra.es/vitrine.json"]);
  assert.deepEqual(direccionesJSON("https://otra.es"), ["https://otra.es/vitrine.json"]);
});

test("un fichero que no es una vitrina no se compara", () => {
  assert.equal(esVitrina({ works: [] }), true);
  assert.equal(esVitrina({ obras: [] }), false);
  assert.equal(esVitrina(null), false);
});
