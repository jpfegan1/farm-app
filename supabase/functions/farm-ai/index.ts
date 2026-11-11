// Farmhand "Ask Farmhand" assistant (Supabase Edge Function "farm-ai").
// Signed-in users only (verify_jwt = true + getUser). The Groq API key is NOT in this code or the repo:
// it is stored encrypted in Supabase Vault (secret "groq_api_key", or env GROQ_API_KEY if set) and read with the service role.
// Per-user limit: DAILY_LIMIT messages per Irish calendar day (public.ai_usage via public.ai_bump).
// Request:  POST { messages: [{role:'user'|'assistant', content}], context: string, memory?: string[], summary?: string }
// Response: text/plain stream of the reply (or JSON {error, message} with 4xx/5xx).
// Memory:   POST { mode:'memory', messages, summary?, notes:[{id,text,locked}] } → JSON {title, summary, add[], update[{id,text}], remove[id]}
//           Background upkeep of the user's long-term "farm memory"; NOT counted against the daily question limit (own cap MEM_LIMIT).
import { createClient } from "jsr:@supabase/supabase-js@2";

const DAILY_LIMIT = 50, MEM_LIMIT = 150;
const PREFERRED = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "llama-3.3-70b-versatile", "openai/gpt-oss-20b", "llama-3.1-8b-instant"];
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Expose-Headers": "x-farmhand-model, x-farmhand-left",
};
const db = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const json = (o: unknown, status = 200) => new Response(JSON.stringify(o), { status, headers: { ...CORS, "Content-Type": "application/json" } });

let KEY: string | null = null, KEY_AT = 0, MODEL: string | null = null, MODEL_AT = 0;
async function groqKey() {
  if (KEY && Date.now() - KEY_AT < 10 * 60e3) return KEY;
  const env = Deno.env.get("GROQ_API_KEY");
  if (env) { KEY = env; KEY_AT = Date.now(); return KEY; }
  const { data, error } = await db.rpc("farm_ai_key");
  if (error) console.error("key lookup failed", error.message);
  KEY = (typeof data === "string" && data) ? data : null; KEY_AT = Date.now(); return KEY;
}
async function pickModel(key: string) { // choose the strongest available chat model from Groq's live list
  if (MODEL && Date.now() - MODEL_AT < 60 * 60e3) return MODEL;
  try {
    const r = await fetch("https://api.groq.com/openai/v1/models", { headers: { Authorization: `Bearer ${key}` }, signal: AbortSignal.timeout(8000) });
    if (r.ok) { const ids = new Set(((await r.json()).data || []).filter((m: any) => m.active !== false).map((m: any) => m.id)); MODEL = PREFERRED.find(m => ids.has(m)) || null; }
  } catch (e) { console.error("model list failed", String(e)); }
  MODEL = MODEL || PREFERRED[0]; MODEL_AT = Date.now(); return MODEL;
}

const SYSTEM = `You are Farmhand, a friendly, practical farm assistant built into an Irish farm records app.
- Answer questions about farming in Ireland (grassland, dairy, beef, sheep, pigs, poultry, tillage, horticulture, fruit and vegetable growing, soil, weather, compliance) and general questions too.
- Use the FARM CONTEXT below (the user's own records) when it is relevant, and say so ("Looking at your records…"). Never invent records that are not there; if something isn't recorded, say so.
- Respect the farm's approach: if it is ORGANIC, only suggest practices and inputs permitted under EU organic rules (Reg. 2018/848) and the farm's certifier, and mention organic withdrawal periods are doubled (min 48 h). If it is conventional or mixed, you may mention both.
- Use Irish context: Teagasc guidance, Met Éireann, Department of Agriculture (DAFM), Nitrates rules, Bord Bia, metric units, € and Irish seasons.
- Be concise and practical: short paragraphs or bullet lists, concrete numbers/timings where you can. Use simple Markdown (bold, bullet lists). Most users are on a phone: avoid wide tables (only use a table for a small comparison of at most 3 short columns).
- For animal health, medicines, safety, legal/compliance or big financial decisions, give general guidance and clearly advise checking with their vet, Teagasc adviser or the relevant authority.
- You have a long-term FARM MEMORY (notes from earlier conversations). Use it naturally when relevant ("Last time you mentioned…"); never claim to remember things that aren't in it.
- Today's date (Ireland): ${"{TODAY}"}.`;

const MEMSYS = `You maintain the long-term memory of "Farmhand", an Irish farm assistant app, for one farmer.
Given the farmer's EXISTING NOTES (each with an id) and the LATEST CONVERSATION, return ONLY a JSON object:
{"title": string, "summary": string, "add": string[], "update": [{"id": string, "text": string}], "remove": string[]}
- title: 2–6 word title for this conversation (e.g. "Winter wheat sowing").
- summary: what this whole conversation covered and concluded, max 90 words (used to continue it later).
- add: NEW durable notes worth remembering in future chats: the farmer's plans, decisions, preferences, problems, and key facts about their farm stated by the FARMER (e.g. "Planning to reseed Hill Paddock in spring", "Prefers organic slurry over CAN"). Max 25 words each, written in third person, include dates/months when given. Do NOT add generic advice, the assistant's suggestions the farmer didn't accept, greetings, or trivia. Usually 0–3 notes.
- update: rewrite an existing note when the conversation changes or refines it (keep its id). Never touch notes marked locked.
- remove: ids of notes that the farmer said are no longer true. Never remove locked notes.
- Never duplicate an existing note. If nothing new, use empty arrays.`;

const clip = (s: unknown, n: number) => String(s ?? "").slice(0, n);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "method", message: "Use POST." }, 405);
  const auth = req.headers.get("Authorization") || "";
  const { data: u, error: ue } = await db.auth.getUser(auth.replace(/^Bearer\s+/i, ""));
  if (ue || !u?.user) return json({ error: "auth", message: "Please sign in again to use the assistant." }, 401);
  let body: any; try { body = await req.json(); } catch { return json({ error: "bad_request", message: "Invalid request." }, 400); }
  const msgs = (Array.isArray(body?.messages) ? body.messages : [])
    .filter((m: any) => m && (m.role === "user" || m.role === "assistant") && String(m.content || "").trim())
    .slice(-12).map((m: any) => ({ role: m.role, content: clip(m.content, 4000) }));
  if (!msgs.length || (body?.mode !== "memory" && msgs[msgs.length - 1].role !== "user")) return json({ error: "bad_request", message: "Ask a question first." }, 400);
  const key = await groqKey();
  if (!key) return json({ error: "not_configured", message: "Assistant not set up yet — the Groq API key hasn't been added." }, 503);
  if (body?.mode === "memory") return memoryUpdate(u.user.id, key, body, msgs);
  const { data: n, error: be } = await db.rpc("ai_bump", { p_user: u.user.id, p_limit: DAILY_LIMIT });
  if (be) { console.error("ai_bump", be.message); return json({ error: "server", message: "The assistant is having trouble right now. Try again shortly." }, 500); }
  if (n === -1) return json({ error: "limit", message: `You've used all ${DAILY_LIMIT} assistant messages for today. The limit resets at midnight.` }, 429);
  const todayIE = new Intl.DateTimeFormat("en-IE", { timeZone: "Europe/Dublin", weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(new Date());
  const mem = (Array.isArray(body?.memory) ? body.memory : []).slice(0, 60).map((x: unknown) => "- " + clip(x, 240)).join("\n");
  const system = SYSTEM.replace("{TODAY}", todayIE) + "\n\nFARM MEMORY (notes kept from earlier conversations):\n" + (mem || "(nothing yet)")
    + (body?.summary ? "\n\nEARLIER IN THIS CONVERSATION (summary of messages no longer shown):\n" + clip(body.summary, 2000) : "")
    + "\n\nFARM CONTEXT (from the user's Farmhand records):\n" + (clip(body?.context, 8000) || "(none provided)");
  const model = await pickModel(key);
  const call = (m: string) => fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST", signal: AbortSignal.timeout(60000),
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: m, stream: true, temperature: 0.4, max_completion_tokens: 1500,
      ...(m.startsWith("openai/gpt-oss") ? { reasoning_effort: "low", include_reasoning: false } : {}),
      messages: [{ role: "system", content: system }, ...msgs] }),
  });
  let used = model, up = await call(model);
  if (!up.ok && up.status !== 429 && up.status !== 401) { // model problem → try the next preferred one
    const alt = PREFERRED.find(m => m !== model)!; console.error("groq", up.status, await up.text().catch(() => "")); used = alt; up = await call(alt);
  }
  if (!up.ok || !up.body) {
    const t = await up.text().catch(() => ""); console.error("groq fail", up.status, t.slice(0, 300));
    if (up.status === 401) { KEY = null; return json({ error: "not_configured", message: "Assistant not set up yet — the Groq API key was rejected." }, 503); }
    if (up.status === 429) return json({ error: "busy", message: "The assistant is busy right now (Groq rate limit). Try again in a minute." }, 503);
    return json({ error: "upstream", message: "The assistant couldn't answer just now. Try again shortly." }, 502);
  }
  const enc = new TextEncoder(), dec = new TextDecoder();
  const stream = new ReadableStream({
    async start(ctrl) {
      const rd = up.body!.getReader(); let buf = "", tokens = 0;
      try {
        for (;;) {
          const { done, value } = await rd.read(); if (done) break;
          buf += dec.decode(value, { stream: true }); let i;
          while ((i = buf.indexOf("\n")) >= 0) {
            const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
            if (!line.startsWith("data:")) continue; const d = line.slice(5).trim(); if (d === "[DONE]") continue;
            try { const j = JSON.parse(d); const c = j.choices?.[0]?.delta?.content; if (c) ctrl.enqueue(enc.encode(c)); const us = j.x_groq?.usage || j.usage; if (us?.total_tokens) tokens = us.total_tokens; } catch { /* partial */ }
          }
        }
      } catch (e) { ctrl.enqueue(enc.encode("\n\n_(The answer was cut short — please try again.)_")); console.error("stream", String(e)); }
      ctrl.close();
      if (tokens) await db.rpc("ai_add_tokens", { p_user: u.user.id, p_tokens: tokens });
    },
  });
  return new Response(stream, { headers: { ...CORS, "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-cache", "x-farmhand-model": used, "x-farmhand-left": String(DAILY_LIMIT - (n as number)) } });
});

async function memoryUpdate(user: string, key: string, body: any, msgs: { role: string; content: string }[]) {
  const { data: n, error } = await db.rpc("ai_bump_mem", { p_user: user, p_limit: MEM_LIMIT });
  if (error) { console.error("ai_bump_mem", error.message); return json({ error: "server", message: "Memory update failed." }, 500); }
  if (n === -1) return json({ error: "limit", message: "Memory updates paused for today." }, 429);
  const notes: { id: string; text: string; locked: boolean }[] = (Array.isArray(body?.notes) ? body.notes : []).slice(0, 80).map((x: any) => ({ id: clip(x?.id, 40), text: clip(x?.text, 240), locked: !!x?.locked }));
  const convo = msgs.map(m => `${m.role === "user" ? "FARMER" : "ASSISTANT"}: ${clip(m.content, 1500)}`).join("\n\n");
  const user_msg = `EXISTING NOTES:\n${notes.length ? notes.map(x => `[${x.id}]${x.locked ? " (locked)" : ""} ${x.text}`).join("\n") : "(none)"}\n\n${body?.summary ? "EARLIER SUMMARY OF THIS CONVERSATION:\n" + clip(body.summary, 2000) + "\n\n" : ""}LATEST CONVERSATION:\n${convo}`;
  const model = await pickModel(key);
  const r = await fetch("https://api.groq.com/openai/v1/chat/completions", { method: "POST", signal: AbortSignal.timeout(45000),
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model, temperature: 0.2, max_completion_tokens: 900, response_format: { type: "json_object" },
      ...(model.startsWith("openai/gpt-oss") ? { reasoning_effort: "low", include_reasoning: false } : {}),
      messages: [{ role: "system", content: MEMSYS }, { role: "user", content: user_msg }] }) });
  if (!r.ok) { console.error("memory groq", r.status, (await r.text().catch(() => "")).slice(0, 200)); return json({ error: "upstream", message: "Memory update failed." }, 502); }
  let out: any = {}; try { const j = await r.json(); out = JSON.parse(j.choices?.[0]?.message?.content || "{}"); } catch { return json({ error: "upstream", message: "Memory update failed." }, 502); }
  const ids = new Set(notes.filter(x => !x.locked).map(x => x.id));
  const str = (x: unknown, n: number) => typeof x === "string" ? x.trim().slice(0, n) : "";
  return json({ title: str(out.title, 60), summary: str(out.summary, 900),
    add: (Array.isArray(out.add) ? out.add : []).map((x: unknown) => str(x, 240)).filter(Boolean).slice(0, 5),
    update: (Array.isArray(out.update) ? out.update : []).filter((x: any) => x && ids.has(String(x.id)) && str(x.text, 240)).map((x: any) => ({ id: String(x.id), text: str(x.text, 240) })).slice(0, 10),
    remove: (Array.isArray(out.remove) ? out.remove : []).map(String).filter((x: string) => ids.has(x)).slice(0, 10) });
}
