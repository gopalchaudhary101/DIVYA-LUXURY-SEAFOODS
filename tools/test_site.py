"""Automated checks: every page loads, internal links resolve, no console errors,
metadata present and unique, JSON-LD parses, images have alt, no horizontal scroll at 375px."""
import json, re, sys
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765"
SHOTS = sys.argv[2] if len(sys.argv) > 2 else None
pages = [l.split("<loc>")[1].split("</loc>")[0] for l in open("dist/sitemap.xml") if "<loc>" in l]
paths = [urlparse(u).path for u in pages]
results, titles, descs, links = [], {}, {}, set()
fail = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for vp, label in (({"width": 1366, "height": 860}, "desktop"), ({"width": 375, "height": 760}, "mobile")):
        ctx = b.new_context(viewport=vp)
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        bad_req = []
        pg.on("response", lambda r: bad_req.append((r.status, r.url)) if r.status >= 400 and urlparse(r.url).hostname in ("localhost",) else None)
        for path in paths:
            errs.clear(); bad_req.clear()
            r = pg.goto(BASE + path, wait_until="networkidle")
            st = r.status if r else 0
            info = pg.evaluate("""() => ({
              title: document.title, desc: (document.querySelector('meta[name=description]')||{}).content||'',
              canon: (document.querySelector('link[rel=canonical]')||{}).href||'',
              h1: document.querySelectorAll('h1').length,
              noalt: [...document.images].filter(i => !i.hasAttribute('alt')).map(i=>i.src),
              broken: [...document.images].filter(i => i.complete && i.naturalWidth===0).map(i=>i.src),
              ld: [...document.querySelectorAll('script[type="application/ld+json"]')].map(s=>s.textContent),
              hscroll: document.documentElement.scrollWidth > window.innerWidth + 1,
              links: [...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))
            })""")
            for s in info["ld"]:
                try: json.loads(s)
                except Exception as ex: errs.append("JSON-LD parse: " + str(ex))
            for h in info["links"]:
                if h.startswith("/"): links.add(h.split("#")[0])
            problems = []
            if st != 200: problems.append(f"status {st}")
            if info["h1"] != 1: problems.append(f"h1 count {info['h1']}")
            if not info["desc"]: problems.append("no description")
            if not info["canon"]: problems.append("no canonical")
            if info["noalt"]: problems.append(f"img without alt {info['noalt']}")
            if info["broken"]: problems.append(f"broken img {info['broken']}")
            if info["hscroll"]: problems.append("horizontal scroll")
            if errs: problems.append(f"console {errs}")
            if bad_req: problems.append(f"4xx/5xx {bad_req}")
            if label == "desktop":
                titles.setdefault(info["title"], []).append(path); descs.setdefault(info["desc"], []).append(path)
                if not (30 <= len(info["title"]) <= 70): problems.append(f"title len {len(info['title'])}")
                if not (70 <= len(info["desc"]) <= 165): problems.append(f"desc len {len(info['desc'])}")
            if SHOTS and path in ("/", "/seafood/", "/enquiry/", "/hotels-restaurants-catering/", "/about/"):
                pg.screenshot(path=f"{SHOTS}/{label}{path.strip('/').replace('/','_') or '_home'}.png", full_page=True)
            print(("FAIL " if problems else "ok   ") + f"[{label}] {path} {problems if problems else ''}")
            fail += bool(problems)
        ctx.close()
    # internal links
    ctx = b.new_context(); pg = ctx.new_page()
    for h in sorted(links):
        r = pg.request.get(BASE + h)
        if r.status != 200:
            print(f"FAIL link {h} -> {r.status}"); fail += 1
    print(f"checked {len(links)} unique internal links")
    for k, v in titles.items():
        if len(v) > 1: print("FAIL duplicate title", v); fail += 1
    for k, v in descs.items():
        if len(v) > 1: print("FAIL duplicate description", v); fail += 1
    r = pg.request.get(BASE + "/does-not-exist/"); print("404 page status (python server serves its own 404):", r.status)
    b.close()
print("TOTAL FAILURES:", fail)
