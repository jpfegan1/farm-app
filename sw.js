// Farm App service worker: lets the app open with no signal (cold start).
// Only caches the app's own files. Supabase API calls, photos, weather, Eircode lookups and map tiles always go to the network
// (offline, paddock outlines still show on a plain background).
const CACHE = 'farmapp-shell-v4';
const ASSETS = ['./', './index.html', './vendor/supabase.js', './vendor/leaflet.js', './vendor/leaflet.css', './vendor/leaflet-geoman.min.js', './vendor/leaflet-geoman.css', './vendor/jszip.min.js', './vendor/fonts/nunito-latin-wght-normal.woff2', './vendor/fonts/nunito-latin-ext-wght-normal.woff2',
  './vendor/images/layers.png', './vendor/images/layers-2x.png', './vendor/images/marker-icon.png', './vendor/images/marker-icon-2x.png', './vendor/images/marker-shadow.png',
  './favicon.svg', './manifest.webmanifest', './icon-192.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return; // never touch API / CDN / weather
  // network first (so updates arrive), fall back to cache when offline
  e.respondWith(fetch(req).then(res => { if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return res; })
    .catch(() => caches.match(req, {ignoreSearch: true}).then(r => r || (req.mode === 'navigate' ? caches.match('./index.html') : undefined))));
});
