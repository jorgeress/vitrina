import {
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from "d3-force";

interface Nodo extends SimulationNodeDatum {
  id: string;
  titulo: string;
  tipo: string;
  favorito: boolean;
  portada: string | null;
  url: string;
  imagen?: HTMLImageElement;
  vecinos: Set<string>;
}

type Arista = SimulationLinkDatum<Nodo> & { peso: number; debil: boolean; source: Nodo; target: Nodo };

const radio = (n: Nodo) => (n.favorito ? 17 : 10);

export function iniciar() {
  const lienzo = document.getElementById("lienzo") as HTMLCanvasElement;
  const ctx = lienzo.getContext("2d")!;
  const datos = JSON.parse(document.getElementById("datos")!.textContent!);
  const estilo = getComputedStyle(document.documentElement);
  const color = (tipo: string) => estilo.getPropertyValue(`--${tipo}`).trim();
  const fondo = estilo.getPropertyValue("--fondo").trim();
  const tenue = estilo.getPropertyValue("--tenue").trim();
  const texto = estilo.getPropertyValue("--texto").trim();

  const nodos: Nodo[] = datos.nodos.map((n: Nodo) => ({ ...n, vecinos: new Set<string>() }));
  const porId = new Map(nodos.map((n) => [n.id, n]));
  const aristas = datos.aristas.map((a: { source: string; target: string; peso: number; debil: boolean }) => {
    porId.get(a.source)!.vecinos.add(a.target);
    porId.get(a.target)!.vecinos.add(a.source);
    return { ...a };
  }) as Arista[];

  // Las portadas se cargan poco a poco; hasta entonces el nodo es un punto
  // del color de su sección.
  for (const n of nodos) {
    if (!n.portada) continue;
    const img = new Image();
    img.src = n.portada;
    img.onload = () => {
      n.imagen = img;
      pintar();
    };
  }

  const visibles = new Set(nodos.map((n) => n.tipo));
  let vista = { x: 0, y: 0, k: 1 };
  let encima: Nodo | null = null;
  let foco: Nodo | null = porId.get(new URLSearchParams(location.search).get("foco") ?? "") ?? null;

  const simulacion = forceSimulation(nodos)
    .force(
      "aristas",
      forceLink<Nodo, Arista>(aristas)
        .id((n) => n.id)
        .distance((a) => (a.debil ? 70 : 46))
        .strength((a) => (a.debil ? 0.15 : Math.min(1, a.peso / 9))),
    )
    .force("carga", forceManyBody().strength(-70))
    .force("choque", forceCollide<Nodo>((n) => radio(n) + 3))
    .force("x", forceX().strength(0.035))
    .force("y", forceY().strength(0.035))
    .stop();
  // Se asienta antes de pintar nada: así se ve ya ordenado, sin la explosión
  // inicial, y se puede encuadrar desde el primer momento.
  simulacion.tick(300);
  simulacion.on("tick", pintar);

  function medir() {
    const r = lienzo.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    lienzo.width = r.width * dpr;
    lienzo.height = r.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    encuadrar();
    pintar();
  }

  // Que quepa todo, o si viene de una ficha, ella y sus vecinas de cerca.
  function encuadrar() {
    const { width, height } = lienzo.getBoundingClientRect();
    const grupo = foco ? [foco, ...[...foco.vecinos].map((id) => porId.get(id)!)] : nodos;
    const xs = grupo.map((n) => n.x!);
    const ys = grupo.map((n) => n.y!);
    const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    const margen = 60;
    const k = Math.min(2, (width - margen * 2) / (x1 - x0 || 1), (height - margen * 2) / (y1 - y0 || 1));
    vista = { k, x: width / 2 - ((x0 + x1) / 2) * k, y: height / 2 - ((y0 + y1) / 2) * k };
  }

  const resaltado = () => encima ?? foco;
  const apagado = (n: Nodo) => {
    if (!visibles.has(n.tipo)) return true;
    const r = resaltado();
    return r !== null && r !== n && !r.vecinos.has(n.id);
  };

  function pintar() {
    const { width, height } = lienzo.getBoundingClientRect();
    ctx.save();
    ctx.clearRect(0, 0, width, height);
    ctx.translate(vista.x, vista.y);
    ctx.scale(vista.k, vista.k);

    const r = resaltado();
    for (const a of aristas) {
      if (!visibles.has(a.source.tipo) || !visibles.has(a.target.tipo)) continue;
      const activa = r && (a.source === r || a.target === r);
      ctx.globalAlpha = r ? (activa ? 0.9 : 0.05) : 0.22;
      ctx.strokeStyle = activa ? color(r!.tipo) : tenue;
      ctx.lineWidth = (activa ? 2 : 1) / vista.k;
      ctx.setLineDash(a.debil ? [4 / vista.k, 4 / vista.k] : []);
      ctx.beginPath();
      ctx.moveTo(a.source.x!, a.source.y!);
      ctx.lineTo(a.target.x!, a.target.y!);
      ctx.stroke();
    }

    ctx.setLineDash([]);
    for (const n of nodos) {
      const rad = radio(n);
      ctx.globalAlpha = apagado(n) ? 0.12 : 1;
      ctx.save();
      ctx.beginPath();
      ctx.arc(n.x!, n.y!, rad, 0, Math.PI * 2);
      if (n.imagen) {
        ctx.clip();
        // Recorte centrado: las portadas son 2:3 y los discos cuadrados.
        const lado = Math.min(n.imagen.width, n.imagen.height);
        ctx.drawImage(
          n.imagen,
          (n.imagen.width - lado) / 2,
          (n.imagen.height - lado) / 2,
          lado,
          lado,
          n.x! - rad,
          n.y! - rad,
          rad * 2,
          rad * 2,
        );
      } else {
        ctx.fillStyle = color(n.tipo);
        ctx.fill();
      }
      ctx.restore();
      ctx.beginPath();
      ctx.arc(n.x!, n.y!, rad, 0, Math.PI * 2);
      ctx.strokeStyle = n === r ? texto : color(n.tipo);
      ctx.lineWidth = (n === r ? 3 : 2) / vista.k;
      ctx.stroke();
    }
    ctx.restore();
    ctx.globalAlpha = 1;

    // Con una obra resaltada, se nombran ella y sus vecinas.
    if (r && visibles.has(r.tipo)) {
      ctx.font = "600 12px Inter, system-ui, sans-serif";
      ctx.textAlign = "center";
      for (const n of [r, ...[...r.vecinos].map((id) => porId.get(id)!)]) {
        if (!visibles.has(n.tipo)) continue;
        const x = n.x! * vista.k + vista.x;
        const y = (n.y! + radio(n)) * vista.k + vista.y + 14;
        ctx.lineWidth = 4;
        ctx.strokeStyle = fondo;
        ctx.strokeText(n.titulo, x, y);
        ctx.fillStyle = n === r ? texto : tenue;
        ctx.fillText(n.titulo, x, y);
      }
    }
  }

  // Del punto de la pantalla al del grafo, y la obra que haya debajo.
  const aGrafo = (px: number, py: number) => ({ x: (px - vista.x) / vista.k, y: (py - vista.y) / vista.k });
  function nodoEn(px: number, py: number): Nodo | null {
    const p = aGrafo(px, py);
    let mejor: Nodo | null = null;
    let distancia = Infinity;
    for (const n of nodos) {
      if (!visibles.has(n.tipo)) continue;
      const d = Math.hypot(n.x! - p.x, n.y! - p.y);
      if (d < radio(n) + 4 && d < distancia) {
        mejor = n;
        distancia = d;
      }
    }
    return mejor;
  }

  let arrastre: { nodo: Nodo | null; x: number; y: number; movido: boolean } | null = null;

  lienzo.addEventListener("pointerdown", (e) => {
    lienzo.setPointerCapture(e.pointerId);
    lienzo.classList.add("agarrado");
    arrastre = { nodo: nodoEn(e.offsetX, e.offsetY), x: e.offsetX, y: e.offsetY, movido: false };
  });

  lienzo.addEventListener("pointermove", (e) => {
    if (arrastre) {
      const dx = e.offsetX - arrastre.x;
      const dy = e.offsetY - arrastre.y;
      if (Math.hypot(dx, dy) > 3) arrastre.movido = true;
      if (arrastre.nodo) {
        const p = aGrafo(e.offsetX, e.offsetY);
        arrastre.nodo.fx = p.x;
        arrastre.nodo.fy = p.y;
        simulacion.alphaTarget(0.2).restart();
      } else {
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

  lienzo.addEventListener("pointerup", () => {
    lienzo.classList.remove("agarrado");
    if (!arrastre) return;
    const { nodo, movido } = arrastre;
    arrastre = null;
    if (nodo) {
      nodo.fx = null;
      nodo.fy = null;
      simulacion.alphaTarget(0);
      // Un toque sin arrastrar: en el ratón abre la ficha; en el móvil, donde
      // no hay «pasar por encima», el primer toque resalta y el segundo abre.
      if (!movido) {
        if (foco === nodo || encima === nodo) location.href = nodo.url;
        else {
          foco = nodo;
          pintar();
        }
      }
    } else if (!movido) {
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

  for (const boton of document.querySelectorAll<HTMLButtonElement>("#leyenda button")) {
    boton.addEventListener("click", () => {
      const tipo = boton.dataset.tipo!;
      if (visibles.has(tipo)) visibles.delete(tipo);
      else visibles.add(tipo);
      boton.classList.toggle("activo", visibles.has(tipo));
      pintar();
    });
  }

  // Buscar una obra la enfoca: se resaltan ella y sus vecinas y se acerca.
  const buscar = document.getElementById("buscar") as HTMLInputElement;
  buscar.addEventListener("change", () => {
    const q = buscar.value.trim().toLowerCase();
    const hallada = nodos.find((n) => n.titulo.toLowerCase() === q) ?? nodos.find((n) => n.titulo.toLowerCase().includes(q));
    if (!q || !hallada) return;
    foco = hallada;
    visibles.add(hallada.tipo);
    document.querySelector(`#leyenda button[data-tipo="${hallada.tipo}"]`)?.classList.add("activo");
    encuadrar();
    pintar();
    history.replaceState(null, "", `?foco=${encodeURIComponent(hallada.id)}`);
  });

  window.addEventListener("resize", medir);
  medir();
}
