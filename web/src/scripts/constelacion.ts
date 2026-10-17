import {
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  type Simulation,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from "d3-force";

/**
 * La constelación en tres niveles, de lo general a lo concreto:
 *
 *   salas    una burbuja por sala, unidas por las obras que se parecen de
 *            una sala a otra (un anime y su manga, un juego y su banda sonora)
 *   géneros  los tags que más se repiten, unidos cuando comparten obras
 *   obras    cada obra, unida a las que más se le parecen
 *
 * Pulsar una burbuja baja un nivel quedándose con ella (la sala, luego el
 * género) y «Subir» vuelve. Los dos niveles de arriba no vienen hechos del
 * servidor: se cuentan aquí con las obras y sus aristas, que ya están en la
 * página, así que no pesan nada más.
 */

type Nivel = "salas" | "generos" | "obras";

interface Punto extends SimulationNodeDatum {
  id: string;
  titulo: string;
  /** La sala que le da el color. En un género, la que más obras pone. */
  tipo: string;
  vecinos: Set<string>;
}

interface Obra extends Punto {
  favorito: boolean;
  portada: string | null;
  url: string;
  tags: string[];
  imagen?: HTMLImageElement;
}

interface Burbuja extends Punto {
  n: number;
}

type Arista<N extends Punto> = SimulationLinkDatum<N> & {
  peso: number;
  debil: boolean;
  /** based_on, follows o soundtrack: la arista lleva flecha. */
  relacion?: string;
  source: N;
  target: N;
};

interface Escena<N extends Punto> {
  nivel: Nivel;
  nodos: N[];
  aristas: Arista<N>[];
  porId: Map<string, N>;
  simulacion: Simulation<N, Arista<N>>;
  radio: (n: N) => number;
  /** El mayor peso de arista, para el grosor de las líneas entre burbujas. */
  maximo: number;
}

const radioObra = (n: Obra) => (n.favorito ? 17 : 10);

export function iniciar() {
  const lienzo = document.getElementById("lienzo") as HTMLCanvasElement;
  const ctx = lienzo.getContext("2d")!;
  const datos = JSON.parse(document.getElementById("datos")!.textContent!);
  const textos = datos.textos as Record<string, string> & { niveles: Record<Nivel, string>; todas: string };
  const nombreSala = new Map<string, string>(datos.salas.map((s: { tipo: string; nombre: string }) => [s.tipo, s.nombre]));
  const nombreTag = (tag: string) => (datos.nombresTag[tag] as string | undefined) ?? tag;

  // Los colores salen de las variables de global.css, y se releen al cambiar
  // de tema: el lienzo no se entera solo, como sí hace el CSS.
  const colores: Record<string, string> = {};
  const color = (tipo: string) => colores[tipo];
  function leerColores() {
    const estilo = getComputedStyle(document.documentElement);
    for (const v of ["game", "film", "series", "book", "album", "fondo", "tenue", "texto", "caja"])
      colores[v] = estilo.getPropertyValue(`--${v}`).trim();
  }
  leerColores();
  window.addEventListener("tema", () => {
    leerColores();
    pintar();
  });

  // --- las escenas ------------------------------------------------------------

  function montar<N extends Punto>(
    nivel: Nivel,
    nodos: N[],
    crudas: { source: string; target: string; peso: number; debil: boolean; relacion?: string }[],
    radio: (n: N) => number,
    fuerzas: { distancia: (a: Arista<N>) => number; carga: number; fuerza: (a: Arista<N>) => number },
  ): Escena<N> {
    const porId = new Map(nodos.map((n) => [n.id, n]));
    for (const n of nodos) n.vecinos = new Set();
    const aristas = crudas
      .filter((a) => porId.has(a.source) && porId.has(a.target))
      .map((a) => {
        porId.get(a.source)!.vecinos.add(a.target);
        porId.get(a.target)!.vecinos.add(a.source);
        return { ...a };
      }) as unknown as Arista<N>[];
    const maximo = Math.max(1, ...crudas.map((a) => a.peso));
    const simulacion = forceSimulation<N, Arista<N>>(nodos)
      .force(
        "aristas",
        forceLink<N, Arista<N>>(aristas)
          .id((n) => n.id)
          .distance(fuerzas.distancia)
          .strength(fuerzas.fuerza),
      )
      .force("carga", forceManyBody<N>().strength(fuerzas.carga))
      .force("choque", forceCollide<N>((n) => radio(n) + (nivel === "obras" ? 3 : 8)))
      // Las salas tiran más hacia el centro: una sala sin nada en común con
      // las demás (la música, casi siempre) se iría flotando lejos.
      .force("x", forceX<N>().strength({ obras: 0.035, generos: 0.06, salas: 0.25 }[nivel]))
      .force("y", forceY<N>().strength({ obras: 0.035, generos: 0.06, salas: 0.25 }[nivel]))
      .stop();
    // Se asienta antes de pintar nada: así se ve ya ordenado, sin la
    // explosión inicial, y se puede encuadrar desde el primer momento.
    simulacion.tick(300);
    simulacion.on("tick", pintar);
    return { nivel, nodos, aristas, porId, simulacion, radio, maximo };
  }

  const obras: Obra[] = datos.nodos.map((n: Obra) => ({ ...n }));
  const obraPorId = new Map(obras.map((n) => [n.id, n]));
  const escenaObras = montar<Obra>("obras", obras, datos.aristas, radioObra, {
    distancia: (a) => (a.relacion ? 40 : a.debil ? 70 : 46),
    fuerza: (a) => (a.relacion ? 1 : a.debil ? 0.15 : Math.min(1, a.peso / 9)),
    carga: -70,
  });

  // Las portadas se cargan poco a poco; hasta entonces la obra es un punto
  // del color de su sala.
  for (const n of obras) {
    if (!n.portada) continue;
    const img = new Image();
    img.src = n.portada;
    img.onload = () => {
      n.imagen = img;
      if (escena.nivel === "obras") pintar();
    };
  }

  /** Las salas: tantas obras como tienen, y unidas por cada arista entre
   * obras que cruza de una a otra. Lo de la misma historia cuenta triple. */
  function escenaSalas(): Escena<Burbuja> {
    const cuantas = new Map<string, number>();
    for (const o of obras) cuantas.set(o.tipo, (cuantas.get(o.tipo) ?? 0) + 1);
    const nodos: Burbuja[] = [...cuantas].map(([tipo, n]) => ({
      id: tipo,
      tipo,
      n,
      titulo: nombreSala.get(tipo) ?? tipo,
      vecinos: new Set(),
    }));
    const pesos = new Map<string, number>();
    for (const a of escenaObras.aristas) {
      if (a.debil || a.source.tipo === a.target.tipo) continue;
      const clave = [a.source.tipo, a.target.tipo].sort().join("|");
      pesos.set(clave, (pesos.get(clave) ?? 0) + (a.relacion ? 3 : 1));
    }
    const crudas = [...pesos].map(([clave, peso]) => {
      const [source, target] = clave.split("|");
      return { source, target, peso, debil: false };
    });
    const radio = (n: Burbuja) => 22 + 3.4 * Math.sqrt(n.n);
    return montar("salas", nodos, crudas, radio, {
      distancia: (a) => radio(a.source) + radio(a.target) + 50,
      fuerza: () => 0.2,
      carga: -900,
    });
  }

  /** Los géneros de una sala o de todas: los tags con más obras, unidos por
   * las obras que comparten. Cada uno se queda con sus cuatro uniones más
   * fuertes, como las obras con sus tres: con todas, una bola sin forma. */
  function escenaGeneros(sala: string | null): Escena<Burbuja> {
    const dentro = obras.filter((o) => !sala || o.tipo === sala);
    const porTag = new Map<string, Obra[]>();
    for (const o of dentro) for (const tag of o.tags) porTag.set(tag, [...(porTag.get(tag) ?? []), o]);
    const minimo = sala ? 2 : 3;
    const elegidos = [...porTag]
      .filter(([, lista]) => lista.length >= minimo)
      .sort((a, b) => b[1].length - a[1].length)
      .slice(0, 45);
    const nodos: Burbuja[] = elegidos.map(([tag, lista]) => {
      const porSala = new Map<string, number>();
      for (const o of lista) porSala.set(o.tipo, (porSala.get(o.tipo) ?? 0) + 1);
      const tipo = [...porSala].sort((a, b) => b[1] - a[1])[0][0];
      return { id: tag, titulo: nombreTag(tag), tipo, n: lista.length, vecinos: new Set() };
    });
    const elegido = new Set(elegidos.map(([tag]) => tag));
    const juntas = new Map<string, number>();
    for (const o of dentro) {
      const suyos = o.tags.filter((tag) => elegido.has(tag)).sort();
      for (let i = 0; i < suyos.length; i++)
        for (let j = i + 1; j < suyos.length; j++) {
          const clave = `${suyos[i]}|${suyos[j]}`;
          juntas.set(clave, (juntas.get(clave) ?? 0) + 1);
        }
    }
    const cuantas = new Map(elegidos.map(([tag, lista]) => [tag, lista.length]));
    // Coseno: compartir 5 obras pesa más entre dos géneros pequeños que entre
    // «action» y «adventure», que salen juntos en media vitrina.
    const candidatas = [...juntas]
      .map(([clave, compartidas]) => {
        const [a, b] = clave.split("|");
        return { source: a, target: b, compartidas, peso: compartidas / Math.sqrt(cuantas.get(a)! * cuantas.get(b)!) };
      })
      .filter((a) => a.compartidas >= (sala ? 1 : 2));
    const quedan = new Set<(typeof candidatas)[number]>();
    for (const n of nodos)
      candidatas
        .filter((a) => a.source === n.id || a.target === n.id)
        .sort((x, y) => y.peso - x.peso)
        .slice(0, 4)
        .forEach((a) => quedan.add(a));
    const radio = (n: Burbuja) => 7 + 2.8 * Math.sqrt(n.n);
    return montar(
      "generos",
      nodos,
      [...quedan].map((a) => ({ ...a, debil: false })),
      radio,
      {
        distancia: (a) => radio(a.source) + radio(a.target) + 30,
        fuerza: (a) => 0.15 + a.peso * 0.6,
        carga: -160,
      },
    );
  }

  let salas: Escena<Burbuja> | null = null;
  const generos = new Map<string, Escena<Burbuja>>();
  type Cualquiera = Escena<Obra> | Escena<Burbuja>;

  // --- el estado: en qué nivel, con qué sala y qué género -----------------------

  const parametros = new URLSearchParams(location.search);
  let foco: Obra | null = obraPorId.get(parametros.get("foco") ?? "") ?? null;
  let sala: string | null = parametros.get("sala");
  // Un género que no tiene ninguna obra (una dirección escrita a mano, o un
  // tag que ya no está) se ignora: si no, se apagaría todo.
  const tagValido = (x: string | null) => (x && obras.some((o) => o.tags.includes(x)) ? x : null);
  let tag: string | null = tagValido(parametros.get("tag"));
  let nivel: Nivel = (parametros.get("nivel") as Nivel) ?? (foco ? "obras" : "salas");
  if (!["salas", "generos", "obras"].includes(nivel)) nivel = "salas";
  const visibles = new Set(obras.map((n) => n.tipo));
  let escena: Cualquiera = escenaObras;
  let encima: Punto | null = null;
  let vista = { x: 0, y: 0, k: 1 };
  // Cuándo empezó el nivel que se ve: los primeros 300 ms entra fundiéndose.
  let aparicion = 0;

  function escenaDe(n: Nivel): Cualquiera {
    if (n === "obras") return escenaObras;
    if (n === "salas") return (salas ??= escenaSalas());
    const clave = sala ?? "";
    if (!generos.has(clave)) generos.set(clave, escenaGeneros(sala));
    return generos.get(clave)!;
  }

  /** Cambia de nivel, de sala o de género. `apilar` deja la vuelta atrás del
   * navegador subiendo de nivel, como un enlace. */
  function ir(nuevo: { nivel: Nivel; sala?: string | null; tag?: string | null; foco?: Obra | null }, apilar = true) {
    nivel = nuevo.nivel;
    sala = nuevo.sala === undefined ? sala : nuevo.sala;
    tag = nuevo.tag === undefined ? tag : tagValido(nuevo.tag);
    foco = nuevo.foco === undefined ? foco : nuevo.foco;
    if (nivel !== "obras") foco = null;
    if (nivel === "salas") sala = tag = null;
    if (nivel === "generos") tag = null;
    // Bajando de una sala, las obras se quedan con esa sala y nada más.
    visibles.clear();
    for (const n of obras) if (!sala || n.tipo === sala) visibles.add(n.tipo);
    if (foco) visibles.add(foco.tipo);
    escena = escenaDe(nivel);
    encima = null;
    const q = new URLSearchParams();
    if (nivel !== "salas") q.set("nivel", nivel);
    if (sala) q.set("sala", sala);
    if (tag) q.set("tag", tag);
    if (foco) q.set("foco", foco.id);
    const url = q.toString() ? `?${q}` : location.pathname;
    if (apilar) history.pushState(null, "", url);
    else history.replaceState(null, "", url);
    rotular();
    encuadrar();
    aparicion = performance.now();
    requestAnimationFrame(animar);
  }

  window.addEventListener("popstate", () => {
    const p = new URLSearchParams(location.search);
    const f = obraPorId.get(p.get("foco") ?? "") ?? null;
    ir({ nivel: (p.get("nivel") as Nivel) ?? (f ? "obras" : "salas"), sala: p.get("sala"), tag: p.get("tag"), foco: f }, false);
  });

  function animar() {
    pintar();
    if (performance.now() - aparicion < 300) requestAnimationFrame(animar);
  }

  // --- el panel -----------------------------------------------------------------

  const botonesNivel = document.querySelectorAll<HTMLButtonElement>(".niveles button");
  const subir = document.getElementById("subir") as HTMLButtonElement;
  const camino = document.getElementById("camino")!;
  const textoNivel = document.getElementById("texto-nivel")!;
  const leyenda = document.getElementById("leyenda")!;
  const notaFlechas = document.getElementById("nota-flechas");

  function rotular() {
    for (const b of botonesNivel) b.setAttribute("aria-pressed", String(b.dataset.nivel === nivel));
    // El camino dice desde dónde se ha bajado: «Juegos › Roguelike».
    const partes = [sala && nombreSala.get(sala), nivel === "obras" && tag && nombreTag(tag)].filter(Boolean);
    camino.textContent = nivel === "salas" ? "" : partes.length ? partes.join(" › ") : textos.todas;
    subir.hidden = nivel === "salas";
    textoNivel.textContent = textos[nivel];
    leyenda.hidden = nivel !== "obras";
    if (notaFlechas) notaFlechas.hidden = nivel !== "obras";
    for (const b of leyenda.querySelectorAll<HTMLButtonElement>("button")) b.classList.toggle("activo", visibles.has(b.dataset.tipo!));
  }

  for (const b of botonesNivel) b.addEventListener("click", () => ir({ nivel: b.dataset.nivel as Nivel, tag: null, foco: null }));
  subir.addEventListener("click", () => ir({ nivel: nivel === "obras" ? "generos" : "salas" }));

  // --- encuadre y dibujo ----------------------------------------------------------

  const enGrupo = (n: Obra) => !tag || n.tags.includes(tag);
  const visible = (n: Punto) => escena.nivel !== "obras" || visibles.has(n.tipo);

  // Que quepa todo; si viene de una ficha, ella y sus vecinas; si se ha bajado
  // a un género, sus obras.
  function encuadrar() {
    const { width, height } = lienzo.getBoundingClientRect();
    let grupo: Punto[] = escena.nodos.filter(visible);
    if (escena.nivel === "obras" && foco) grupo = [foco, ...[...foco.vecinos].map((id) => obraPorId.get(id)!)];
    else if (escena.nivel === "obras" && tag) grupo = obras.filter((n) => visibles.has(n.tipo) && enGrupo(n));
    if (!grupo.length) grupo = escena.nodos;
    const r = (n: Punto) => (escena.radio as (n: Punto) => number)(n);
    const x0 = Math.min(...grupo.map((n) => n.x! - r(n)));
    const x1 = Math.max(...grupo.map((n) => n.x! + r(n)));
    const y0 = Math.min(...grupo.map((n) => n.y! - r(n)));
    const y1 = Math.max(...grupo.map((n) => n.y! + r(n) + (escena.nivel === "obras" ? 0 : 18)));
    // El hueco libre es lo que no tapa el panel: a su derecha en pantalla
    // ancha, debajo en el móvil, donde ocupa todo el ancho.
    const panel = document.querySelector(".panel")?.getBoundingClientRect();
    const caja = lienzo.getBoundingClientRect();
    let izquierda = 0;
    let arriba = 0;
    if (panel && !foco) {
      if (width > 760) izquierda = panel.right - caja.left;
      else arriba = panel.bottom - caja.top;
    }
    const margen = 36;
    const ancho = width - izquierda - margen * 2;
    const alto = height - arriba - margen * 2;
    const k = Math.min(escena.nivel === "obras" ? 2 : 2.4, ancho / (x1 - x0 || 1), alto / (y1 - y0 || 1));
    vista = {
      k,
      x: izquierda + margen + ancho / 2 - ((x0 + x1) / 2) * k,
      y: arriba + margen + alto / 2 - ((y0 + y1) / 2) * k,
    };
  }

  function medir() {
    const r = lienzo.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    lienzo.width = r.width * dpr;
    lienzo.height = r.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    encuadrar();
    pintar();
  }

  const resaltado = () => encima ?? (escena.nivel === "obras" ? foco : null);
  const apagado = (n: Punto) => {
    if (!visible(n)) return true;
    if (escena.nivel === "obras" && !enGrupo(n as Obra)) return true;
    const r = resaltado();
    return r !== null && r !== n && !r.vecinos.has(n.id);
  };

  function pintar() {
    const { width, height } = lienzo.getBoundingClientRect();
    const entrada = Math.min(1, (performance.now() - aparicion) / 300);
    ctx.save();
    ctx.clearRect(0, 0, width, height);
    // Al cambiar de nivel, entra fundiéndose y acercándose un poco: se nota
    // que se ha bajado (o subido) en vez de un salto en seco.
    const k = vista.k * (0.94 + 0.06 * entrada);
    const cx = width / 2;
    const cy = height / 2;
    ctx.translate(cx + (vista.x - cx) * (k / vista.k), cy + (vista.y - cy) * (k / vista.k));
    ctx.scale(k, k);
    ctx.globalAlpha = entrada;
    if (escena.nivel === "obras") pintarObras(entrada);
    else pintarBurbujas(escena as Escena<Burbuja>, entrada);
    ctx.restore();
    ctx.globalAlpha = 1;
    if (escena.nivel === "obras") rotulosObras();
  }

  function pintarObras(entrada: number) {
    const r = resaltado();
    for (const a of escenaObras.aristas) {
      if (!visibles.has(a.source.tipo) || !visibles.has(a.target.tipo) || a.relacion) continue;
      const activa = r && (a.source === r || a.target === r);
      const fuera = tag && !(enGrupo(a.source) && enGrupo(a.target));
      ctx.globalAlpha = entrada * (r ? (activa ? 0.9 : 0.05) : fuera ? 0.04 : 0.22);
      ctx.strokeStyle = activa ? color(r!.tipo) : colores.tenue;
      ctx.lineWidth = (activa ? 2 : 1) / vista.k;
      ctx.setLineDash(a.debil ? [4 / vista.k, 4 / vista.k] : []);
      ctx.beginPath();
      ctx.moveTo(a.source.x!, a.source.y!);
      ctx.lineTo(a.target.x!, a.target.y!);
      ctx.stroke();
    }
    ctx.setLineDash([]);
    // Lo de la misma historia, encima y con flecha: son pocas y dicen más que
    // cualquier parecido.
    for (const a of escenaObras.aristas) {
      if (!a.relacion || !visibles.has(a.source.tipo) || !visibles.has(a.target.tipo)) continue;
      const activa = !r || a.source === r || a.target === r;
      ctx.globalAlpha = entrada * (activa ? 0.95 : 0.15);
      flecha(a.source, a.target, color(a.source.tipo));
    }

    for (const n of obras) {
      const rad = radioObra(n);
      ctx.globalAlpha = entrada * (apagado(n) ? 0.12 : 1);
      ctx.save();
      forma(n, rad);
      if (n.imagen) {
        ctx.clip();
        // Recorte centrado: las portadas son 2:3 y los discos cuadrados.
        const lado = Math.min(n.imagen.width, n.imagen.height);
        ctx.drawImage(n.imagen, (n.imagen.width - lado) / 2, (n.imagen.height - lado) / 2, lado, lado, n.x! - rad, n.y! - rad, rad * 2, rad * 2);
      } else {
        ctx.fillStyle = color(n.tipo);
        ctx.fill();
      }
      ctx.restore();
      forma(n, rad);
      ctx.strokeStyle = n === r ? colores.texto : color(n.tipo);
      ctx.lineWidth = (n === r ? 3 : 2) / vista.k;
      ctx.stroke();
    }
  }

  function flecha(desde: Punto, hacia: Punto, tono: string) {
    const ang = Math.atan2(hacia.y! - desde.y!, hacia.x! - desde.x!);
    // La punta va a mitad de camino y no en el borde de la obra: ahí la
    // tapaban la portada o su nombre, que se escribe justo debajo.
    const px = (desde.x! + hacia.x!) / 2 + Math.cos(ang) * 5;
    const py = (desde.y! + hacia.y!) / 2 + Math.sin(ang) * 5;
    const largo = 11 / Math.min(vista.k, 1.5);
    ctx.strokeStyle = ctx.fillStyle = tono;
    ctx.lineWidth = 2.2 / vista.k;
    ctx.beginPath();
    ctx.moveTo(desde.x!, desde.y!);
    ctx.lineTo(hacia.x!, hacia.y!);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.lineTo(px - largo * Math.cos(ang - 0.5), py - largo * Math.sin(ang - 0.5));
    ctx.lineTo(px - largo * Math.cos(ang + 0.5), py - largo * Math.sin(ang + 0.5));
    ctx.closePath();
    ctx.fill();
  }

  // Los nombres van fuera de la transformación, para que se lean siempre al
  // mismo tamaño: con una obra resaltada, ella y sus vecinas; con un género,
  // sus obras si no son demasiadas.
  function rotulosObras() {
    const r = resaltado();
    let nombrar: Obra[] = [];
    if (r) nombrar = [r as Obra, ...[...r.vecinos].map((id) => obraPorId.get(id)!)];
    else if (tag) nombrar = obras.filter((n) => enGrupo(n) && visibles.has(n.tipo));
    if (nombrar.length > 30) nombrar = r ? nombrar : [];
    ctx.font = "600 13px 'Source Sans 3', system-ui, sans-serif";
    ctx.textAlign = "center";
    for (const n of nombrar) {
      if (!visibles.has(n.tipo)) continue;
      const x = n.x! * vista.k + vista.x;
      const y = (n.y! + radioObra(n)) * vista.k + vista.y + 14;
      ctx.lineWidth = 4;
      ctx.strokeStyle = colores.fondo;
      ctx.strokeText(n.titulo, x, y);
      ctx.fillStyle = n === r ? colores.texto : colores.tenue;
      ctx.fillText(n.titulo, x, y);
    }
  }

  function pintarBurbujas(e: Escena<Burbuja>, entrada: number) {
    const r = resaltado();
    for (const a of e.aristas) {
      const activa = r && (a.source === r || a.target === r);
      ctx.globalAlpha = entrada * (r ? (activa ? 0.8 : 0.06) : 0.28);
      ctx.strokeStyle = activa ? color(r!.tipo) : colores.tenue;
      ctx.lineWidth = (1 + (e.nivel === "salas" ? 9 : 4) * (a.peso / e.maximo)) / vista.k;
      ctx.beginPath();
      ctx.moveTo(a.source.x!, a.source.y!);
      ctx.lineTo(a.target.x!, a.target.y!);
      ctx.stroke();
    }
    for (const n of e.nodos) {
      const rad = e.radio(n);
      const alfa = entrada * (apagado(n) ? 0.2 : 1);
      ctx.beginPath();
      ctx.arc(n.x!, n.y!, rad, 0, Math.PI * 2);
      // Relleno suave del color de la sala sobre el de las cajas, y borde
      // entero: el nombre va encima y tiene que leerse en los dos temas. En
      // dos capas y no con color-mix(), que el lienzo no entiende en todos.
      ctx.globalAlpha = alfa;
      ctx.fillStyle = colores.caja;
      ctx.fill();
      ctx.globalAlpha = alfa * (n === r ? 0.45 : 0.28);
      ctx.fillStyle = color(n.tipo);
      ctx.fill();
      ctx.globalAlpha = alfa;
      ctx.strokeStyle = color(n.tipo);
      ctx.lineWidth = (n === r ? 3 : 2) / vista.k;
      ctx.stroke();

      ctx.fillStyle = colores.texto;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      const grande = e.nivel === "salas";
      ctx.font = `600 ${(grande ? 15 : 12.5) / vista.k}px 'Source Sans 3', system-ui, sans-serif`;
      // Dentro si cabe el nombre entero; si no, debajo. Encogerlo hasta que
      // quepa dejaba «Alternative rock» ilegible.
      const cabe = ctx.measureText(n.titulo).width <= rad * 1.75 && rad * vista.k > 20;
      if (cabe) {
        ctx.fillText(n.titulo, n.x!, n.y! - (grande ? 8 : 6) / vista.k);
        ctx.font = `${(grande ? 13 : 11) / vista.k}px 'Source Sans 3', system-ui, sans-serif`;
        ctx.fillStyle = colores.tenue;
        ctx.fillText(String(n.n), n.x!, n.y! + (grande ? 10 : 8) / vista.k);
      } else {
        // Burbuja pequeña: el nombre debajo, con un filo del fondo para que se
        // lea sobre las líneas.
        const y = n.y! + rad + 10 / vista.k;
        ctx.lineWidth = 3.5 / vista.k;
        ctx.strokeStyle = colores.fondo;
        ctx.strokeText(n.titulo, n.x!, y);
        ctx.fillText(n.titulo, n.x!, y);
      }
      ctx.textBaseline = "alphabetic";
    }
  }

  // Los discos, cuadrados como sus portadas; lo demás, redondo. Así la sala
  // no depende solo del color, que entre cinco no siempre se distingue.
  function forma(n: Obra, rad: number) {
    ctx.beginPath();
    if (n.tipo === "album") ctx.roundRect(n.x! - rad * 0.9, n.y! - rad * 0.9, rad * 1.8, rad * 1.8, rad * 0.25);
    else ctx.arc(n.x!, n.y!, rad, 0, Math.PI * 2);
  }

  // --- el ratón y los dedos -------------------------------------------------------

  // Del punto de la pantalla al del grafo, y lo que haya debajo.
  const aGrafo = (px: number, py: number) => ({ x: (px - vista.x) / vista.k, y: (py - vista.y) / vista.k });
  function nodoEn(px: number, py: number): Punto | null {
    const p = aGrafo(px, py);
    let mejor: Punto | null = null;
    let distancia = Infinity;
    for (const n of escena.nodos as Punto[]) {
      if (!visible(n)) continue;
      const d = Math.hypot(n.x! - p.x, n.y! - p.y);
      if (d < (escena.radio as (n: Punto) => number)(n) + 4 && d < distancia) {
        mejor = n;
        distancia = d;
      }
    }
    return mejor;
  }

  /** Pulsar una burbuja baja un nivel quedándose con ella. */
  function bajar(n: Punto) {
    if (escena.nivel === "salas") ir({ nivel: "generos", sala: n.id });
    else if (escena.nivel === "generos") ir({ nivel: "obras", tag: n.id, foco: null });
  }

  let arrastre: { nodo: Punto | null; x: number; y: number; movido: boolean } | null = null;

  // Con dos dedos se acerca y se aleja, como un mapa: en el móvil no hay
  // rueda. Se guarda dónde está cada dedo y, mientras haya dos, la distancia
  // entre ellos manda sobre el zoom y su punto medio, sobre el centro.
  const dedos = new Map<number, { x: number; y: number }>();
  let pellizco: { distancia: number; k: number } | null = null;
  const separacion = () => {
    const [a, b] = [...dedos.values()];
    return { d: Math.hypot(a.x - b.x, a.y - b.y), mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 };
  };

  lienzo.addEventListener("pointerdown", (e) => {
    dedos.set(e.pointerId, { x: e.offsetX, y: e.offsetY });
    if (dedos.size === 2) {
      pellizco = { distancia: separacion().d, k: vista.k };
      arrastre = null;
      return;
    }
    lienzo.setPointerCapture(e.pointerId);
    lienzo.classList.add("agarrado");
    arrastre = { nodo: nodoEn(e.offsetX, e.offsetY), x: e.offsetX, y: e.offsetY, movido: false };
  });

  lienzo.addEventListener("pointermove", (e) => {
    if (dedos.has(e.pointerId)) dedos.set(e.pointerId, { x: e.offsetX, y: e.offsetY });
    if (pellizco && dedos.size === 2) {
      const { d, mx, my } = separacion();
      const k = Math.min(4, Math.max(0.25, (pellizco.k * d) / pellizco.distancia));
      vista.x = mx - ((mx - vista.x) * k) / vista.k;
      vista.y = my - ((my - vista.y) * k) / vista.k;
      vista.k = k;
      pintar();
      return;
    }
    if (arrastre) {
      const dx = e.offsetX - arrastre.x;
      const dy = e.offsetY - arrastre.y;
      if (Math.hypot(dx, dy) > 3) arrastre.movido = true;
      if (arrastre.nodo && arrastre.movido) {
        const p = aGrafo(e.offsetX, e.offsetY);
        arrastre.nodo.fx = p.x;
        arrastre.nodo.fy = p.y;
        (escena.simulacion as unknown as Simulation<Punto, undefined>).alphaTarget(0.2).restart();
      } else if (!arrastre.nodo) {
        vista.x += dx;
        vista.y += dy;
        arrastre.x = e.offsetX;
        arrastre.y = e.offsetY;
        pintar();
      }
      return;
    }
    const n = nodoEn(e.offsetX, e.offsetY);
    if (n !== encima) {
      encima = n;
      lienzo.style.cursor = n ? "pointer" : "";
      pintar();
    }
  });

  const soltar = (e: PointerEvent) => {
    dedos.delete(e.pointerId);
    if (dedos.size < 2) pellizco = null;
  };
  lienzo.addEventListener("pointercancel", (e) => {
    soltar(e);
    arrastre = null;
  });
  lienzo.addEventListener("pointerup", (e) => {
    const eraPellizco = pellizco !== null;
    soltar(e);
    if (eraPellizco) return;
    lienzo.classList.remove("agarrado");
    if (!arrastre) return;
    const { nodo, movido } = arrastre;
    arrastre = null;
    if (nodo) {
      nodo.fx = null;
      nodo.fy = null;
      (escena.simulacion as unknown as Simulation<Punto, undefined>).alphaTarget(0);
      if (movido) return;
      if (escena.nivel !== "obras") return bajar(nodo);
      // Una obra: en el ratón, un clic abre la ficha; en el móvil, donde no
      // hay «pasar por encima», el primer toque resalta y el segundo abre.
      const obra = nodo as Obra;
      if (foco === obra || encima === obra) location.href = obra.url;
      else {
        foco = obra;
        pintar();
      }
    } else if (!movido && foco) {
      foco = null;
      pintar();
    }
  });

  lienzo.addEventListener("pointerleave", () => {
    encima = null;
    pintar();
  });

  lienzo.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const k = Math.min(4, Math.max(0.25, vista.k * Math.exp(-e.deltaY * 0.0015)));
      vista.x = e.offsetX - ((e.offsetX - vista.x) * k) / vista.k;
      vista.y = e.offsetY - ((e.offsetY - vista.y) * k) / vista.k;
      vista.k = k;
      pintar();
    },
    { passive: false },
  );

  for (const boton of leyenda.querySelectorAll<HTMLButtonElement>("button")) {
    boton.addEventListener("click", () => {
      const tipo = boton.dataset.tipo!;
      if (visibles.has(tipo)) visibles.delete(tipo);
      else visibles.add(tipo);
      boton.classList.toggle("activo", visibles.has(tipo));
      pintar();
    });
  }

  // Buscar una obra la enfoca, desde cualquier nivel: se baja a las obras y
  // se resaltan ella y sus vecinas.
  const buscar = document.getElementById("buscar") as HTMLInputElement;
  buscar.addEventListener("change", () => {
    const q = buscar.value.trim().toLowerCase();
    const hallada = obras.find((n) => n.titulo.toLowerCase() === q) ?? obras.find((n) => n.titulo.toLowerCase().includes(q));
    if (!q || !hallada) return;
    ir({ nivel: "obras", sala: null, tag: null, foco: hallada });
  });

  window.addEventListener("resize", medir);
  ir({ nivel, sala, tag, foco }, false);
  medir();
}
