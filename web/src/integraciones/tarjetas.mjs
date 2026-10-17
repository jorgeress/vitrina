// Las tarjetas para compartir: una imagen de 1200×630 por ficha, la que sale
// al pegar su enlace en un chat o una red social. Sin ella sale la carátula
// suelta, que no dice de dónde viene ni lo que piensa el dueño.
//
// Se pintan con sharp, que ya trae Astro, y las fuentes de la casa que van en
// web/fuentes: así no hace falta navegador ni ningún paquete más. Cada tarjeta
// se guarda en una caché por su contenido, y entre builds solo se rehace la
// que ha cambiado.
import { createHash } from "node:crypto";
import { copyFile, mkdir, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const FUENTES = fileURLToPath(new URL("../../fuentes/", import.meta.url));
const CACHE = fileURLToPath(new URL("../../node_modules/.cache/tarjetas/", import.meta.url));
// Sube cuando cambie el dibujo, para que la caché no sirva las viejas.
const VERSION = "1";

const ANCHO = 1200;
const ALTO = 630;
const MARGEN = 60;

// Los colores del tema oscuro de global.css: la tarjeta es una pieza
// iluminada en su vitrina, como la ficha en oscuro.
const FONDO = "#0f0e10";
const TEXTO = "#ece7dd";
const TENUE = "#a39d93";
const DORADO = "#e0c063";

const escapar = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/** Un bloque de texto ya pintado, con su alto, para apilarlo debajo del anterior. */
async function texto(markup, { fuente, fichero, ancho, alineacion = "left" }) {
  const imagen = sharp({
    text: { text: markup, font: fuente, fontfile: fichero, width: ancho, wrap: "word", rgba: true, dpi: 72, align: alineacion },
  });
  const buffer = await imagen.png().toBuffer();
  const { width, height } = await sharp(buffer).metadata();
  return { buffer, ancho: width, alto: height };
}

/** Un rectángulo de esquinas redondeadas, para recortar la portada. */
const redondeo = (w, h, r) =>
  Buffer.from(`<svg width="${w}" height="${h}"><rect width="${w}" height="${h}" rx="${r}" ry="${r}"/></svg>`);

/** ¿Hay algo en el título que no esté en el alfabeto latino? */
const noLatino = (s) => /[^\u0000-ɏḀ-ỿ -⁯←-⇿☀-⛿]/.test(s);

/**
 * La fuente para un título en japonés, chino o coreano: Noto Sans JP, de
 * Google Fonts, pedida solo con las letras de ese título (`text=`), que son
 * unos pocos KB. Sin clave ni cuenta. Si no hay red, null, y la tarjeta usa
 * el nombre del fichero, que siempre está en ASCII.
 */
async function fuenteCJK(titulo, logger) {
  const clave = createHash("sha1").update(titulo).digest("hex").slice(0, 16);
  const destino = join(CACHE, `cjk-${clave}.ttf`);
  try {
    await stat(destino);
    return destino;
  } catch {}
  try {
    const css = await (
      await fetch(`https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@600&text=${encodeURIComponent(titulo)}`)
    ).text();
    const enlace = css.match(/src:\s*url\(([^)]+)\)/)?.[1];
    if (!enlace) return null;
    const fuente = Buffer.from(await (await fetch(enlace)).arrayBuffer());
    await mkdir(CACHE, { recursive: true });
    await writeFile(destino, fuente);
    return destino;
  } catch {
    logger.warn(`tarjetas: sin fuente para «${titulo}», va con el nombre del fichero`);
    return null;
  }
}

async function pintar(t, textos, portadas, colores, logger) {
  const color = colores[t.tipo] ?? TENUE;
  const capas = [];

  // La portada, si la hay: a la izquierda y, desenfocada, de fondo, como en la
  // cabecera de la ficha.
  let fichero = null;
  for (const dir of portadas) {
    if (!t.portada) break;
    try {
      await stat(join(dir, t.portada));
      fichero = join(dir, t.portada);
      break;
    } catch {}
  }
  const altoPortada = ALTO - MARGEN * 2;
  let derecha = MARGEN;
  const fondo = sharp({ create: { width: ANCHO, height: ALTO, channels: 4, background: FONDO } });
  if (fichero) {
    const desenfocada = await sharp(fichero)
      .resize(ANCHO, ALTO, { fit: "cover" })
      .blur(40)
      .modulate({ brightness: 0.45, saturation: 1.2 })
      .png()
      .toBuffer();
    capas.push({ input: desenfocada, left: 0, top: 0 });
    capas.push({
      input: Buffer.from(`<svg width="${ANCHO}" height="${ALTO}"><rect width="100%" height="100%" fill="${FONDO}" fill-opacity="0.55"/></svg>`),
      left: 0,
      top: 0,
    });
    const anchoPortada = t.tipo === "album" ? altoPortada : Math.round((altoPortada * 2) / 3);
    const portada = await sharp(fichero)
      .resize(anchoPortada, altoPortada, { fit: "cover" })
      .composite([{ input: redondeo(anchoPortada, altoPortada, 10), blend: "dest-in" }])
      .png()
      .toBuffer();
    capas.push({ input: portada, left: MARGEN, top: MARGEN });
    derecha = MARGEN + anchoPortada + 56;
  } else {
    // Sin portada, el color de la sala de fondo, muy bajo.
    capas.push({
      input: Buffer.from(
        `<svg width="${ANCHO}" height="${ALTO}"><defs><radialGradient id="g" cx="0.15" cy="0.2" r="0.9"><stop offset="0" stop-color="${color}" stop-opacity="0.45"/><stop offset="1" stop-color="${FONDO}" stop-opacity="0"/></radialGradient></defs><rect width="100%" height="100%" fill="url(#g)"/></svg>`,
      ),
      left: 0,
      top: 0,
    });
  }

  const ancho = ANCHO - derecha - MARGEN;
  const cinzel = join(FUENTES, "Cinzel.ttf");
  const sans = join(FUENTES, "SourceSans3.ttf");
  const cursiva = join(FUENTES, "SourceSans3-Italic.ttf");
  let y = MARGEN + 6;

  // La sala, en capitales espaciadas y con su punto de color.
  const sala = await texto(
    `<span foreground="${color}">●</span>  <span foreground="${TENUE}" letter_spacing="4000">${escapar(t.sala.toUpperCase())}</span>`,
    { fuente: "Cinzel SemiBold 22", fichero: cinzel, ancho },
  );
  capas.push({ input: sala.buffer, left: derecha, top: y });
  y += sala.alto + 22;

  // El título. Más pequeño cuanto más largo, para que no pase de tres líneas.
  let titulo = t.titulo;
  let fuenteTitulo = cinzel;
  let familia = "Cinzel SemiBold";
  if (noLatino(titulo)) {
    const cjk = await fuenteCJK(titulo, logger);
    if (cjk) {
      fuenteTitulo = cjk;
      familia = "Noto Sans JP SemiBold";
    } else titulo = t.alternativo;
  }
  const cuerpo = titulo.length > 60 ? 40 : titulo.length > 32 ? 50 : 62;
  const rotulo = await texto(`<span foreground="${TEXTO}">${escapar(titulo)}</span>`, {
    fuente: `${familia} ${cuerpo}`,
    fichero: fuenteTitulo,
    ancho,
  });
  capas.push({ input: rotulo.buffer, left: derecha, top: y });
  y += rotulo.alto + 18;

  const quien = [t.autor, t.year].filter(Boolean).join(" · ");
  if (quien) {
    const linea = await texto(`<span foreground="${TENUE}">${escapar(quien)}</span>`, {
      fuente: "Source Sans 3 30",
      fichero: sans,
      ancho,
    });
    capas.push({ input: linea.buffer, left: derecha, top: y });
    y += linea.alto + 22;
  }

  // La nota y, si lo es, lo mejor de lo mejor: el único dorado de la casa.
  const sellos = [
    t.nota && `<span foreground="${TEXTO}" weight="bold">${t.nota}</span><span foreground="${TENUE}">${escapar(textos.de10)}</span>`,
    t.favorito && `<span foreground="${DORADO}" weight="bold">${escapar(textos.mejor)}</span>`,
  ].filter(Boolean);
  if (sellos.length) {
    const linea = await texto(sellos.join(`<span foreground="${TENUE}">   ·   </span>`), {
      fuente: "Source Sans 3 32",
      fichero: sans,
      ancho,
    });
    capas.push({ input: linea.buffer, left: derecha, top: y });
    y += linea.alto + 26;
  }

  // La opinión, si cabe: lo que dice el dueño, recortado a lo que entre.
  const pie = ALTO - MARGEN - 30;
  if (t.opinion && pie - y > 70) {
    const lineas = Math.floor((pie - y - 20) / 36);
    const limite = Math.max(60, lineas * 46);
    const frase =
      t.opinion.length > limite ? `${t.opinion.slice(0, limite).replace(/\s+\S*$/, "").replace(/[\s.,;:]+$/, "")}…` : t.opinion;
    const cita = await texto(`<span foreground="${TEXTO}">“${escapar(frase)}”</span>`, {
      fuente: "Source Sans 3 Italic 28",
      fichero: cursiva,
      ancho,
    });
    // Si aun así no cabe, se recorta por abajo antes que pisar el pie.
    const alto = Math.min(cita.alto, pie - y - 10);
    const recortada = alto < cita.alto ? await sharp(cita.buffer).extract({ left: 0, top: 0, width: cita.ancho, height: alto }).toBuffer() : cita.buffer;
    capas.push({ input: recortada, left: derecha, top: y });
  }

  // El rótulo de la casa, abajo a la derecha: de qué vitrina es y dónde está.
  // Son dos fuentes, así que dos textos, uno detrás del otro.
  const direccion = await texto(`<span foreground="${TENUE}">${escapar(textos.sitio)}</span>`, {
    fuente: "Source Sans 3 22",
    fichero: sans,
    ancho: 600,
  });
  const marca = await texto(
    `<span foreground="${TEXTO}" letter_spacing="6000">${escapar(textos.nombre.toUpperCase())}</span>`,
    { fuente: "Cinzel SemiBold 24", fichero: cinzel, ancho: 600 },
  );
  const base = ALTO - MARGEN + 8;
  capas.push({ input: direccion.buffer, left: ANCHO - MARGEN - direccion.ancho, top: base - direccion.alto });
  capas.push({ input: marca.buffer, left: ANCHO - MARGEN - direccion.ancho - 18 - marca.ancho, top: base - marca.alto - 1 });

  return fondo.composite(capas).png({ compressionLevel: 9, palette: false }).toBuffer();
}

/** Lee los colores de cada sala del tema oscuro de global.css. */
async function coloresOscuros(css) {
  const bloque = css.match(/:root\[data-tema="oscuro"\]\s*\{([^}]*)\}/)?.[1] ?? "";
  return Object.fromEntries([...bloque.matchAll(/--([a-z]+):\s*(#[0-9a-f]{6})/gi)].map((m) => [m[1], m[2]]));
}

export async function hacerTarjetas({ salida, datos, portadas, css, logger }) {
  const colores = await coloresOscuros(css);
  await mkdir(CACHE, { recursive: true });
  let hechas = 0;
  let deCache = 0;
  for (const t of datos.tarjetas) {
    const destino = join(salida, t.salida);
    await mkdir(dirname(destino), { recursive: true });
    let huella = createHash("sha1").update(VERSION + JSON.stringify(t) + JSON.stringify(datos.textos));
    for (const dir of portadas)
      try {
        huella = huella.update(String((await stat(join(dir, t.portada ?? ""))).mtimeMs));
      } catch {}
    const enCache = join(CACHE, `${huella.digest("hex")}.png`);
    try {
      await copyFile(enCache, destino);
      deCache++;
      continue;
    } catch {}
    const png = await pintar(t, datos.textos, portadas, colores, logger);
    await writeFile(destino, png);
    await writeFile(enCache, png);
    hechas++;
  }
  logger.info(`tarjetas: ${hechas} hechas, ${deCache} de la caché`);
}

