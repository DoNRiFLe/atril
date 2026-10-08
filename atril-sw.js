// Service worker del Atril: deja la app funcionando sin internet.
// Subí el numero de version cuando cambie letras.html para forzar la
// actualizacion en las tablets que ya la tengan instalada.
const CACHE = 'atril-v9';
const ARCHIVOS = [
  './',
  'index.html',
  'atril.webmanifest',
  'atril-192.png',
  'atril-512.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(ARCHIVOS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // lo de Google (login de Drive) nunca se cachea: tiene que ir a la red
  if (url.origin !== self.location.origin) return;

  // red primero y cache como respaldo: asi al volver la conexion
  // la tablet toma la version nueva sola
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res && res.ok) {
          const copia = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copia));
        }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match('index.html')))
  );
});
