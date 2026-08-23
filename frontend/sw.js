/* PestWatch service worker — offline app shell + installability. */
const CACHE = "pestwatch-v6";
const SHELL = [
  "/", "/index.html",
  "/app.js?v=6", "/i18n.js?v=6", "/styles.css?v=6",
  "/icon-192.png", "/icon-512.png", "/manifest.json",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.allSettled(SHELL.map((u) => c.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);

  // Never cache API calls or non-GET — always hit the network.
  if (req.method !== "GET" || url.pathname.startsWith("/api/")) return;

  // App shell / assets: network-first (fresh when online), fall back to cache offline.
  e.respondWith(
    fetch(req)
      .then((resp) => {
        if (resp && resp.ok && url.origin === self.location.origin) {
          const copy = resp.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return resp;
      })
      .catch(() =>
        caches.match(req).then((r) => r || caches.match("/"))
      )
  );
});
