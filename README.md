# Divya Luxury Foods — company website

Static, fast, SEO-ready B2B website for **Divya Luxury Foods Pvt. Ltd.** No framework, no database, no secrets.
Hosted free on **Cloudflare Pages** (commercial use allowed on the free plan).

## Structure

```
data/site.json        ← business details: phones, WhatsApp, email, address, GSTIN, FSSAI, IEC, social links, site URL
data/products.json    ← product range shown on category pages (no prices)
content/pages/*.html  ← page copy (each file starts with a <!--meta {...} --> block: path, title, description)
src/                  ← CSS, JS, fonts, images, favicon, _headers (security), _redirects
src/assets/img/       ← products/<category>/ (own photos), stock/<category>/ (licensed), manifest.json (every published image)
functions/api/        ← optional server-side enquiry endpoint (Cloudflare Pages Function)
tools/build.py        ← builds everything into dist/ (+ sitemap.xml, robots.txt)
tools/test_site.py    ← automated checks (links, metadata, JSON-LD, mobile overflow, console errors)
dist/                 ← the built site that Cloudflare publishes (committed)
IMAGE-CREDITS.md      ← source/licence of every image
```

## Updating the site

1. Edit `data/site.json`, `data/products.json` or a file in `content/pages/`.
2. Rebuild: `python3 tools/build.py`
3. Optional check: `cd dist && python3 -m http.server 8765` then in another terminal `pip install playwright && playwright install chromium && python3 tools/test_site.py`
4. Commit and push to `main` — Cloudflare Pages redeploys automatically in ~1 minute.

Adding a product photo: put a square photo in `src/assets/img/products/<category>/` as `<slug>-480.webp` and `<slug>-900.webp`, reference `{"name": "...", "img": "<category>/<slug>"}` in `products.json`, and add it to `src/assets/img/manifest.json`. Only use your own photos or properly licensed images.

## Cloudflare Pages settings

- Framework preset: **None**
- Build command: *(leave empty)*
- Build output directory: **dist**
- Production branch: **main**

If the final URL is not `https://divyaluxuryfoods.pages.dev`, change `site_url` in `data/site.json`, rebuild and push (canonical URLs and the sitemap depend on it). When a custom domain is bought later, change `site_url` again and add the domain in Cloudflare Pages → Custom domains.

## Enquiry form

Works today with no keys: the form validates input, then opens WhatsApp (number in `site.json`) or the visitor's email app with the enquiry pre-filled. Nothing is stored.

Optional server-side submission (`functions/api/enquiry.js`, a Cloudflare Pages Function): server-side validation, honeypot + time trap,
same-origin check, 10 KB body limit, best-effort rate limit (5 per IP per 10 min), and delivery to the sales inbox via Resend.
It answers `503 not_configured` until these encrypted secrets are added in Cloudflare Pages → Settings → Variables and Secrets:
`RESEND_API_KEY`, `NOTIFY_EMAIL` (optional `FROM_EMAIL`). After a live test enquiry arrives, set
`form_endpoint.server_form` to `true` in `site.json`, rebuild and push — only then does the "Submit enquiry" button appear.

Local test: `npx wrangler pages dev dist --binding RESEND_API_KEY=... NOTIFY_EMAIL=...` (run from the repo root so `functions/` is picked up).

## Search Console / Bing verification

Paste the verification code in `site.json → google_site_verification` / `bing_site_verification`, rebuild and push.
