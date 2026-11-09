// Farm App weather proxy (Supabase Edge Function "weather").
// Why: Met Éireann's open-data API only works over plain http (its https address redirects to a host that fails TLS),
// so an https site can't call it from the browser (mixed content), and MET Norway (Yr) asks that
// browser apps go through a caching proxy that identifies itself with a User-Agent. This function fetches the point
// forecast for one location, normalises it to a small JSON, and caches it in public.weather_cache (shared by all users,
// keyed by source + location rounded to 0.01°), respecting upstream Expires / If-Modified-Since.
// Data licences: Met Éireann CC BY 4.0 (https://www.met.ie), MET Norway CC BY 4.0 / NLOD (https://api.met.no).
// Only signed-in Farm App users can call it (verify_jwt = true).
import { createClient } from "jsr:@supabase/supabase-js@2";

const UA = "FarmApp/3 (+https://github.com/jpfegan1/farm-app; Irish farm records app)";
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const json = (o: unknown, status = 200, extra: Record<string, string> = {}) =>
  new Response(JSON.stringify(o), { status, headers: { ...CORS, "Content-Type": "application/json", ...extra } });

type Pt = { t: string; temp?: number; wind?: number; gust?: number; dir?: number; rh?: number };
type Iv = { from: string; to: string; mm: number; prob?: number; sym?: string };

function pickNonOverlapping(iv: Iv[]): Iv[] { // prefer shortest intervals, never double count rain
  const s = iv.slice().sort((a, b) => a.from < b.from ? -1 : a.from > b.from ? 1 : (Date.parse(a.to) - Date.parse(b.to)));
  const out: Iv[] = []; let cursor = 0;
  for (const x of s) { const f = Date.parse(x.from); if (f >= cursor) { out.push(x); cursor = Date.parse(x.to); } }
  return out;
}
const attr = (tag: string, name: string) => { const m = tag.match(new RegExp(`\\b${name}="([^"]*)"`)); return m ? m[1] : undefined; };
const numA = (tag: string | undefined, name: string) => { if (!tag) return undefined; const v = attr(tag, name); return v == null || v === "" ? undefined : Number(v); };

function parseMetIe(xml: string) {
  const pts: Pt[] = [], iv: Iv[] = [];
  const re = /<time[^>]*from="([^"]+)"[^>]*to="([^"]+)"[^>]*>([\s\S]*?)<\/time>/g; let m;
  while ((m = re.exec(xml))) {
    const [, from, to, body] = m; const tag = (n: string) => (body.match(new RegExp(`<${n}\\b[^>]*>`)) || [])[0];
    if (from === to) {
      pts.push({ t: from, temp: numA(tag("temperature"), "value"), wind: numA(tag("windSpeed"), "mps"), gust: numA(tag("windGust"), "mps"), dir: numA(tag("windDirection"), "deg"), rh: numA(tag("humidity"), "value") });
    } else {
      const p = tag("precipitation"); if (p) iv.push({ from, to, mm: numA(p, "value") ?? 0, prob: numA(p, "probability"), sym: attr(tag("symbol") || "", "id") });
    }
  }
  return { pts, iv: pickNonOverlapping(iv) };
}
function parseMetNo(j: any) {
  const pts: Pt[] = [], iv: Iv[] = [];
  for (const ts of j?.properties?.timeseries || []) {
    const d = ts.data?.instant?.details || {};
    pts.push({ t: ts.time, temp: d.air_temperature, wind: d.wind_speed, gust: d.wind_speed_of_gust, dir: d.wind_from_direction, rh: d.relative_humidity });
    for (const [k, h] of [["next_1_hours", 1], ["next_6_hours", 6]] as const) {
      const n = ts.data?.[k]; if (n?.details?.precipitation_amount != null) {
        iv.push({ from: ts.time, to: new Date(Date.parse(ts.time) + h * 3600e3).toISOString().replace(".000", ""), mm: n.details.precipitation_amount, prob: n.details.probability_of_precipitation, sym: n.summary?.symbol_code });
      }
    }
  }
  return { pts, iv: pickNonOverlapping(iv) };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  const u = new URL(req.url); const src = u.searchParams.get("src") || "";
  const lat = Number(u.searchParams.get("lat")), lon = Number(u.searchParams.get("lon"));
  if (!["metie", "metno"].includes(src)) return json({ error: "src must be metie or metno" }, 400);
  if (!(lat > 49 && lat < 62 && lon > -15 && lon < 5)) return json({ error: "lat/lon outside Ireland / UK area" }, 400);
  const la = lat.toFixed(2), lo = lon.toFixed(2); const key = `${src}:${la},${lo}`;
  const { data: cached } = await db.from("weather_cache").select("*").eq("key", key).maybeSingle();
  if (cached && Date.parse(cached.expires_at) > Date.now()) return json({ ...JSON.parse(cached.body), cache: "hit", fetchedAt: cached.fetched_at }, 200, { "Cache-Control": "public, max-age=600" });
  // Met Éireann: documented open-data endpoint first, then the older ICHEC-hosted endpoint of the same service.
  const urls = src === "metie"
    ? [`http://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=${la};long=${lo}`, `https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat=${la};long=${lo}`]
    : [`https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=${la}&lon=${lo}`];
  const headers: Record<string, string> = { "User-Agent": UA };
  if (cached?.last_modified) headers["If-Modified-Since"] = cached.last_modified;
  let r: Response | undefined; const errs: string[] = [];
  for (const url of urls) {
    try { const x = await fetch(url, { headers, signal: AbortSignal.timeout(15000) }); if (x.ok || x.status === 304) { r = x; break; } errs.push(`${new URL(url).host}: HTTP ${x.status}`); await x.body?.cancel(); }
    catch (e) { errs.push(`${new URL(url).host}: ${String(e).slice(0, 160)}`); }
  }
  if (!r) { const e = errs.join(" | "); if (cached) return json({ ...JSON.parse(cached.body), cache: "stale", fetchedAt: cached.fetched_at, warning: String(e) }); return json({ error: "upstream unreachable: " + e }, 502); }
  const exp = Date.parse(r.headers.get("expires") || "") || 0;
  const expiresAt = new Date(Math.max(exp, Date.now() + (src === "metie" ? 60 : 30) * 60e3)).toISOString();
  if (r.status === 304 && cached) {
    await db.from("weather_cache").update({ expires_at: expiresAt }).eq("key", key);
    return json({ ...JSON.parse(cached.body), cache: "revalidated", fetchedAt: cached.fetched_at });
  }
  if (!r.ok) { if (cached) return json({ ...JSON.parse(cached.body), cache: "stale", fetchedAt: cached.fetched_at, warning: "upstream HTTP " + r.status }); return json({ error: "upstream HTTP " + r.status }, 502); }
  let out;
  try {
    if (src === "metie") out = { src, model: "Met Éireann (HARMONIE-AROME + ECMWF)", lat: +la, lon: +lo, ...parseMetIe(await r.text()) };
    else { const j = await r.json(); out = { src, model: "MET Norway (ECMWF-based, Yr)", lat: +la, lon: +lo, updatedAt: j?.properties?.meta?.updated_at, ...parseMetNo(j) }; }
  } catch (e) { return json({ error: "could not parse upstream: " + String(e) }, 502); }
  if (!out.pts.length) return json({ error: "upstream returned no forecast" }, 502);
  const fetchedAt = new Date().toISOString();
  await db.from("weather_cache").upsert({ key, body: JSON.stringify(out), content_type: "application/json", last_modified: r.headers.get("last-modified"), fetched_at: fetchedAt, expires_at: expiresAt });
  return json({ ...out, cache: "miss", fetchedAt }, 200, { "Cache-Control": "public, max-age=600" });
});
