// Lo que hace que la vitrina se abra sin conexión, como una app.
//
// Las páginas van primero a la red, para que lo nuevo se vea en cuanto se
// publica, y si no hay red se sirven de la caché. Lo demás no cambia nunca o
// casi: lo de _astro/ lleva el hash en el nombre y las portadas solo cambian
// si se rehacen a mano, así que se sirve de la caché y se refresca por detrás.
const VERSION = "vitrina-1";
const BASE = new URL("./", self.location).pathname;
const INICIO = [BASE, `${BASE}offline/`, `${BASE}manifest.webmanifest`];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(INICIO)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((claves) => Promise.all(claves.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const peticion = e.request;
  const destino = new URL(peticion.url);
  if (peticion.method !== "GET" || destino.origin !== self.location.origin || !destino.pathname.startsWith(BASE)) return;

  if (peticion.mode === "navigate") {
    e.respondWith(
      fetch(peticion)
        .then((r) => guardar(peticion, r))
        .catch(async () => (await caches.match(peticion)) ?? (await caches.match(`${BASE}offline/`))),
    );
    return;
  }

  // Portadas, scripts, estilos y el índice del buscador.
  e.respondWith(
    caches.match(peticion).then((guardada) => {
      const deRed = fetch(peticion)
        .then((r) => guardar(peticion, r))
        .catch(() => guardada);
      return guardada ?? deRed;
    }),
  );
});

function guardar(peticion, respuesta) {
  if (respuesta.ok) {
    const copia = respuesta.clone();
    caches.open(VERSION).then((c) => c.put(peticion, copia));
  }
  return respuesta;
}
