# Farmhand

Farm records web app for an Irish dairy/beef farm: paddock map, herd, milk, breeding & calving, grass planner, photos, tasks and compliance record-keeping (a record-keeping aid, not an official register).

* Static single-page app (`index.html`), hosted on GitHub Pages.
* Accounts and data: Supabase (email + password auth, Postgres with row-level security so each user only sees their own rows, private Storage bucket `photos` with one folder per user).
* Works with poor signal: per-user local cache + queued writes that sync when back online; `sw.js` caches the app shell for offline start.
* The key in `index.html` is Supabase's *publishable* key, which is designed to be public; data access is enforced by RLS policies.

## Map (v3)

* Real satellite map (Esri World Imagery, with Esri road/place labels) or street map (OpenStreetMap), drawn with Leaflet + Leaflet-Geoman, bundled in `vendor/` (no CDN).
* Draw fields by tapping corners (live area in ha and acres), edit corners, and import KML/KMZ from Google Earth (placemark names become paddock names). Paddocks can also be exported as KML.
* Farm location from an Eircode: an exact match in OpenStreetMap (Nominatim) where the Eircode is mapped, otherwise the routing-key area (approximate). After that, drop a pin, use GPS, or paste coordinates or a Google Maps link. There is no free official Eircode API that an app may use; the app links to Eircode Finder for checking a code by hand.
* Paddock geometry: `geo: [[lat,lng],...]`. Paddocks from v2 that only have sketch `points` still work and can be shown on the "Old sketch map".

## Weather (v3.1)

* Forecast is always for the saved farm location (map pin, GPS, Eircode or typed coordinates). If none is set, the app asks for one and doesn't fetch any weather.
* Sources: Met Éireann and Yr / MET Norway go through the Supabase Edge Function `weather` (`supabase/functions/weather`). It caches results in `public.weather_cache`, shared between users and keyed by location rounded to 0.01°. ECMWF, UK Met Office, DWD ICON and NOAA GFS come from Open-Meteo directly in the browser. Met Éireann warnings come from met.ie open data.
* The Weather page shows the sources side by side (rain, temperature, wind) plus an average. Grass growth uses Met Éireann by default, with soil temperature from Open-Meteo.
* The last download is cached on the device for offline use.
