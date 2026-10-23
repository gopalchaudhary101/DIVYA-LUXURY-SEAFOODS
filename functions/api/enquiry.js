/**
 * POST /api/enquiry — server-side enquiry handler (Cloudflare Pages Function).
 *
 * Validates input, applies spam checks, and emails the enquiry to the sales inbox
 * through Resend (https://resend.com). Nothing is stored.
 *
 * Required environment variables (set in Cloudflare Pages → Settings → Variables and Secrets,
 * as *encrypted* secrets — never commit them):
 *   RESEND_API_KEY   – Resend API key
 *   NOTIFY_EMAIL     – inbox that receives enquiries (e.g. divyaluxuryfoods@gmail.com)
 * Optional:
 *   FROM_EMAIL       – verified sender; defaults to Resend's onboarding sender
 *   ALLOWED_ORIGINS  – comma-separated extra origins allowed to post (the site's own origin is always allowed)
 *
 * Until RESEND_API_KEY and NOTIFY_EMAIL are set, the endpoint answers 503 "not_configured"
 * and the website keeps using WhatsApp / email links instead (the online-submit button stays hidden).
 */

const MAX_BODY = 10 * 1024;
const TYPES = new Set(["quote", "catalogue", "general"]);
const INTERESTS = new Set(["Seafood", "Japanese & Asian foods", "Imported cheese", "Chicken & lamb", "Other"]);
const BTYPES = new Set(["", "Hotel / resort", "Restaurant / café / cloud kitchen", "Caterer / banquet", "Retailer / gourmet store",
  "Distributor / importer", "Private property / institution", "Other"]);
const RATE_LIMIT = 5;            // submissions
const RATE_WINDOW_S = 600;       // per 10 minutes per IP (best effort, per data centre)
const MIN_FILL_MS = 3000;        // humans take longer than 3 s to fill the form

const json = (status, data, extra = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra },
  });

const clean = (v, max) => (typeof v === "string" ? v.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim().slice(0, max) : "");
const esc = (s) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function validate(raw) {
  const errors = {};
  const d = {
    type: clean(raw.type, 20),
    name: clean(raw.name, 80),
    company: clean(raw.company, 120),
    phone: clean(raw.phone, 20),
    email: clean(raw.email, 120),
    btype: clean(raw.btype, 60),
    city: clean(raw.city, 80),
    message: clean(raw.message, 1500),
    interests: Array.isArray(raw.interests) ? raw.interests.filter((x) => typeof x === "string" && INTERESTS.has(x)).slice(0, 5) : [],
  };
  if (!TYPES.has(d.type)) errors.type = "Choose an enquiry type.";
  if (d.name.length < 2) errors.name = "Please enter your name.";
  if (d.company.length < 2) errors.company = "Please enter your business name.";
  if (d.city.length < 2) errors.city = "Please enter your city or country.";
  const digits = d.phone.replace(/\D/g, "");
  if (!/^[+\d][\d\s()-]*$/.test(d.phone) || digits.length < 8 || digits.length > 15) errors.phone = "Please enter a valid phone number.";
  if (d.email && !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]{2,}$/.test(d.email)) errors.email = "Please enter a valid email address.";
  if (!BTYPES.has(d.btype)) errors.btype = "Choose a business type from the list.";
  return { data: d, errors };
}

async function rateLimited(request) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const cache = caches.default;
  const key = new Request(`https://rate-limit.internal/enquiry/${encodeURIComponent(ip)}`);
  const hit = await cache.match(key);
  const count = hit ? Number(await hit.text()) || 0 : 0;
  if (count >= RATE_LIMIT) return true;
  await cache.put(key, new Response(String(count + 1), { headers: { "cache-control": `max-age=${RATE_WINDOW_S}` } }));
  return false;
}

export async function onRequestPost({ request, env }) {
  // Same-origin check (blocks cross-site form posts)
  const origin = request.headers.get("origin") || "";
  const self = new URL(request.url).origin;
  const allowed = new Set([self, ...(env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean)]);
  if (!allowed.has(origin)) return json(403, { ok: false, error: "forbidden_origin" });

  if (!(request.headers.get("content-type") || "").includes("application/json")) return json(415, { ok: false, error: "unsupported_type" });
  const len = Number(request.headers.get("content-length") || 0);
  if (len > MAX_BODY) return json(413, { ok: false, error: "too_large" });

  let raw;
  try {
    const text = await request.text();
    if (text.length > MAX_BODY) return json(413, { ok: false, error: "too_large" });
    raw = JSON.parse(text);
  } catch {
    return json(400, { ok: false, error: "invalid_json" });
  }
  if (!raw || typeof raw !== "object") return json(400, { ok: false, error: "invalid_json" });

  // Spam traps: hidden field must be empty, form must not be submitted instantly
  if (raw.botcheck) return json(400, { ok: false, error: "rejected" });
  const elapsed = Number(raw.elapsed_ms);
  if (!Number.isFinite(elapsed) || elapsed < MIN_FILL_MS) return json(400, { ok: false, error: "rejected" });

  const { data, errors } = validate(raw);
  if (Object.keys(errors).length) return json(422, { ok: false, error: "validation", fields: errors });

  if (!env.RESEND_API_KEY || !env.NOTIFY_EMAIL) return json(503, { ok: false, error: "not_configured" });

  if (await rateLimited(request)) return json(429, { ok: false, error: "rate_limited" }, { "retry-after": String(RATE_WINDOW_S) });

  const label = { quote: "Quote request", catalogue: "Catalogue request", general: "Business enquiry" }[data.type];
  const rows = [
    ["Name", data.name], ["Business", data.company], ["Business type", data.btype], ["Location", data.city],
    ["Phone", data.phone], ["Email", data.email], ["Interested in", data.interests.join(", ")], ["Requirements", data.message],
  ].filter(([, v]) => v);
  const text = `${label} — via website\n\n` + rows.map(([k, v]) => `${k}: ${v}`).join("\n");
  const html = `<h2>${esc(label)} — via website</h2><table cellpadding="6">` +
    rows.map(([k, v]) => `<tr><th align="left" valign="top">${esc(k)}</th><td>${esc(v).replace(/\n/g, "<br>")}</td></tr>`).join("") + "</table>";

  let res;
  try {
    res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, "content-type": "application/json" },
      body: JSON.stringify({
        from: env.FROM_EMAIL || "Divya Luxury Foods Website <onboarding@resend.dev>",
        to: [env.NOTIFY_EMAIL],
        reply_to: data.email || undefined,
        subject: `${label} — ${data.company}`,
        text,
        html,
      }),
    });
  } catch {
    return json(502, { ok: false, error: "delivery_failed" });
  }
  if (!res.ok) return json(502, { ok: false, error: "delivery_failed" });
  return json(200, { ok: true });
}

// Any other method (GET, PUT, …) — onRequestPost above takes precedence for POST.
export const onRequest = () => json(405, { ok: false, error: "method_not_allowed" }, { allow: "POST" });
