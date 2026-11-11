// Farmhand service worker: lets the app open with no signal (cold start).
// Caches the app's own files only. Supabase API calls, uploaded photos, weather, Eircode lookups and map tiles always go to the network
// (offline, paddock outlines still show on a plain background).
const CACHE = 'farmapp-shell-v14';
const DATA = 'farmhand-crops-v1';      // crop library JSON (network first, so updates arrive)
const IMG = 'farmhand-cropimg-v1';     // crop thumbnails (~10 KB each, cache first, capped)
const IMG_MAX = 450;
const ASSETS = ['./', './index.html', './vendor/supabase.js', './vendor/leaflet.js', './vendor/leaflet.css', './vendor/leaflet-geoman.min.js', './vendor/leaflet-geoman.css', './vendor/polygon-clipping.min.js', './vendor/jszip.min.js', './vendor/fonts/nunito-latin-wght-normal.woff2', './vendor/fonts/nunito-latin-ext-wght-normal.woff2', './vendor/fonts/cinzel-latin-wght-normal.woff2', './brand/farmhand-original.jpg', './brand/logo-header.jpg', './brand/banner.jpg?v=8', './brand/banner-blur.jpg?v=8', './brand/hero-phone.jpg',
  './vendor/images/layers.png', './vendor/images/layers-2x.png', './vendor/images/marker-icon.png', './vendor/images/marker-icon-2x.png', './vendor/images/marker-shadow.png',
  './favicon.png', './favicon-32.png', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png', './crops/index.json'];
const KEEP = [CACHE, DATA, IMG];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => !KEEP.includes(k)).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
async function trim(name, max){ const c = await caches.open(name); const keys = await c.keys(); for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]); }
function networkFirst(req, cacheName){
  return fetch(req).then(res => { if (res.ok) { const copy = res.clone(); caches.open(cacheName).then(c => c.put(req, copy)); } return res; })
    .catch(() => caches.match(req, {ignoreSearch: true}).then(r => r || (req.mode === 'navigate' ? caches.match('./index.html') : Response.error())));
}
self.addEventListener('fetch', e => {
  const req = e.request; const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return; // never touch API / CDN / weather
  const p = url.pathname;
  if (/\/crops\/img\/[^/]+\.webp$/.test(p)) {   // thumbnails: cache first, keep at most IMG_MAX
    e.respondWith(caches.open(IMG).then(c => c.match(req).then(hit => hit || fetch(req).then(res => { if (res.ok) { c.put(req, res.clone()).then(() => trim(IMG, IMG_MAX)); } return res; }))));
    return;
  }
  if (/\/crops\/[^/]+\.json$/.test(p)) { e.respondWith(networkFirst(req, /index\.json$/.test(p) ? CACHE : DATA)); return; }
  e.respondWith(networkFirst(req, CACHE));   // app shell: network first so updates arrive
});
