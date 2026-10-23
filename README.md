# Divya Luxury Foods — company website

Static, fast, SEO-ready B2B website for **Divya Luxury Foods Pvt. Ltd.** No framework, no database, no secrets.
Hosted free on **Cloudflare Pages** (commercial use allowed on the free plan).

## Structure

```
data/site.json        ← business details: phones, WhatsApp, email, address, GSTIN, FSSAI, IEC, social links, site URL
data/products.json    ← product range shown on category pages (no prices)
content/pages/*.html  ← page copy (each file starts with a <!--meta {...} --> block: path, title, description)
src/                  ← CSS, JS, fonts, images, favicon, _headers (security), _redirects
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

Adding a product photo: put a square photo in `src/assets/img/products/` as `<slug>-480.webp` and `<slug>-900.webp`, then reference `{"name": "...", "img": "<slug>"}` in `products.json`. Only use your own photos or properly licensed images.

## Cloudflare Pages settings

- Framework preset: **None**
- Build command: *(leave empty)*
- Build output directory: **dist**
- Production branch: **main**

If the final URL is not `https://divyaluxuryfoods.pages.dev`, change `site_url` in `data/site.json`, rebuild and push (canonical URLs and the sitemap depend on it). When a custom domain is bought later, change `site_url` again and add the domain in Cloudflare Pages → Custom domains.

## Enquiry form

The form validates input, then opens WhatsApp (to the number in `site.json`) or the visitor's email app with the enquiry pre-filled — no data is stored on any server, no keys needed.
Optional: add a free Web3Forms access key in `site.json → form_endpoint.web3forms_access_key` to also receive a copy in the inbox.

## Search Console / Bing verification

Paste the verification code in `site.json → google_site_verification` / `bing_site_verification`, rebuild and push.
