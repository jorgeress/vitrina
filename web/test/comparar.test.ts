import { test } from "node:test";
import assert from "node:assert/strict";
import { comparar, direccionJSON, type Pieza, type Vitrina } from "../src/lib/comparar.ts";

const pieza = (titulo: string, extra: Partial<Pieza> = {}): Pieza => ({
  titulo,
  tipo: "juego",
  year: 2020,
  autores: [],
  nota: null,
  estado: null,
  favorito: false,
  tags: [],
  ids: {},
  cartela: null,
  url: "",
  ...extra,
});
const vitrina = (...obras: Pieza[]): Vitrina => ({ version: 2, obras });

test("dos piezas son la misma si comparten un id, aunque el título cambie", () => {
  const r = comparar(
    vitrina(pieza("El viaje de Chihiro", { tipo: "peli", ids: { letterboxd: "spirited-away" } })),
    vitrina(pieza("Spirited Away", { tipo: "peli", ids: { letterboxd: "spirited-away" } })),
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
    pieza("A", { ids: { appid: 1 }, nota: 9, favorito: true }),
    pieza("B", { ids: { appid: 2 }, nota: 3 }),
    pieza("Solo mía", { ids: { appid: 3 } }),
  );
  const b = vitrina(
    pieza("A", { ids: { appid: 1 }, nota: 10, favorito: true }),
    pieza("B", { ids: { appid: 2 }, nota: 9 }),
    pieza("Suya normal", { ids: { appid: 4 }, nota: 6 }),
    pieza("Suya favorita", { ids: { appid: 5 }, favorito: true }),
  );
  const r = comparar(a, b);
  assert.equal(r.comunes.length, 2);
  assert.equal(r.afinidad, 2 / 5);
  assert.deepEqual(r.favoritasDeLosDos.map((c) => c.mia.titulo), ["A"]);
  assert.deepEqual(r.desacuerdos.map((c) => c.mia.titulo), ["B"]);
  assert.deepEqual(r.recomendaciones.map((p) => p.titulo), ["Suya favorita", "Suya normal"]);
});

test("cualquier enlace de una vitrina lleva a su vitrina.json", () => {
  assert.equal(direccionJSON("amiga.github.io/vitrina/"), "https://amiga.github.io/vitrina/vitrina.json");
  assert.equal(direccionJSON("https://amiga.github.io/vitrina/juegos/balatro/"), "https://amiga.github.io/vitrina/vitrina.json");
  assert.equal(direccionJSON("https://otra.es/vitrina.json"), "https://otra.es/vitrina.json");
  assert.equal(direccionJSON("https://otra.es"), "https://otra.es/vitrina.json");
});
