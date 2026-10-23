#!/usr/bin/env python3
"""Static site builder for Divya Luxury Foods.

Usage:  python3 tools/build.py            -> builds ./dist
Edit business info in data/site.json, product range in data/products.json,
and page copy in content/pages/*.html. No dependencies beyond Python 3.8+.
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
BASE = SITE["site_url"].rstrip("/")
TODAY = date.today().isoformat()
ASSET_V = TODAY.replace("-", "")

NAV = [
    ("Products", "/products/", [
        ("Premium Seafood", "/seafood/"),
        ("Japanese & Asian Foods", "/japanese-asian-foods/"),
        ("Imported Cheese", "/imported-cheese/"),
        ("Chicken, Lamb & Poultry", "/chicken-lamb/"),
    ]),
    ("Hotels & Restaurants", "/hotels-restaurants-catering/", None),
    ("Wholesale", "/wholesale-supply/", None),
    ("About", "/about/", None),
    ("Contact", "/contact/", None),
]

e = html.escape


def wa_link(text):
    from urllib.parse import quote
    return f"https://wa.me/{SITE['whatsapp']}?text={quote(text)}"


def icon(name, size=20):
    paths = {
        "wa": '<path d="M20.5 3.5A11.8 11.8 0 0 0 1.9 17.7L.3 23.7l6.2-1.6A11.8 11.8 0 0 0 20.5 3.5ZM12 21.6c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4a9.8 9.8 0 1 1 8.3 4.6Zm5.4-7.3c-.3-.2-1.8-.9-2-1-.3-.1-.5-.2-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1a8 8 0 0 1-2.4-1.5 9 9 0 0 1-1.6-2c-.2-.3 0-.5.1-.6l.4-.5.3-.5v-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6a1.1 1.1 0 0 0-.8.4 3.4 3.4 0 0 0-1 2.5 6 6 0 0 0 1.2 3.1c.2.2 2 3.1 4.9 4.3 2.4 1 2.9.8 3.4.7.6 0 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4l-.3-.3Z" fill="currentColor"/>',
        "phone": '<path d="M6.6 10.8a15.5 15.5 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.2 11.4 11.4 0 0 0 3.6.6 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.2.2 2.5.6 3.6a1 1 0 0 1-.3 1l-2.2 2.2Z" fill="currentColor"/>',
        "mail": '<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm9 7.2L4.3 7H4v.3l8 5.4 8-5.4V7h-.3L12 12.2Z" fill="currentColor"/>',
        "pin": '<path d="M12 2a7 7 0 0 1 7 7c0 5.2-7 13-7 13S5 14.2 5 9a7 7 0 0 1 7-7Zm0 4.5A2.5 2.5 0 1 0 12 11.5 2.5 2.5 0 0 0 12 6.5Z" fill="currentColor"/>',
        "arrow": '<path d="M5 12h13m-5-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
        "snow": '<path d="M12 2v20M4.9 6l14.2 12M4.9 18 19.1 6M9 3.5l3 2.5 3-2.5M9 20.5l3-2.5 3 2.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
        "check": '<path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
        "split": '<path d="M12 3v18M4 7h5M4 12h5M4 17h5M15 7h5M15 12h5M15 17h5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
        "truck": '<path d="M2 6h11v9H2zM13 9h4l4 4v2h-8zM6 18.5a1.5 1.5 0 1 0 0-.01M17 18.5a1.5 1.5 0 1 0 0-.01" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
        "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2M4 14h3v6H5a1 1 0 0 1-1-1v-5Zm16 0h-3v6h2a1 1 0 0 0 1-1v-5Z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>',
        "globe": '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z" fill="none" stroke="currentColor" stroke-width="1.6"/>',
        "ig": '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/>',
        "in": '<path d="M4 9h3.5v11H4zM5.8 3.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4ZM10 9h3.3v1.6c.5-.9 1.7-1.9 3.5-1.9 3.6 0 4.2 2.4 4.2 5.5V20h-3.5v-5.1c0-1.3 0-2.9-1.8-2.9s-2.1 1.4-2.1 2.8V20H10z" fill="currentColor"/>',
        "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v8h4v-8h3l1-4h-4V8.6c0-.3.3-.6.6-.6Z" fill="currentColor"/>',
    }
    return f'<svg class="i" width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{paths[name]}</svg>'


def img(slug, alt, sizes="(max-width: 640px) 50vw, 300px", eager=False, cls=""):
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img class="{cls}" src="/assets/img/products/{slug}-480.webp" '
            f'srcset="/assets/img/products/{slug}-480.webp 480w, /assets/img/products/{slug}-900.webp 900w" '
            f'sizes="{sizes}" width="480" height="480" alt="{e(alt)}" {load}>')


# ---------- components ----------

def products_block(slug):
    cat = next(c for c in CATALOG["categories"] if c["slug"] == slug)
    out = []
    for g in cat["groups"]:
        featured = [i for i in g["items"] if isinstance(i, dict)]
        plain = [i for i in g["items"] if isinstance(i, str)]
        out.append(f'<section class="range-group"><h2 class="h3">{e(g["name"])}</h2>')
        if featured:
            out.append('<ul class="pgrid" role="list">')
            for it in featured:
                msg = f"Hello Divya Luxury Foods, I'd like a quote for: {it['name']}."
                out.append(
                    f'<li class="pcard">{img(it["img"], it["name"] + " — product photo from Divya Luxury Foods")}'
                    f'<div class="pcard-b"><h3>{e(it["name"])}</h3>'
                    f'<a class="pcard-cta" href="{e(wa_link(msg))}" target="_blank" rel="noopener" '
                    f'aria-label="Ask for a quote for {e(it["name"])} on WhatsApp">Get quote {icon("arrow",16)}</a></div></li>')
            out.append('</ul>')
        if plain:
            out.append('<ul class="chips" role="list">' + "".join(f"<li>{e(p)}</li>" for p in plain) + "</ul>")
        out.append('</section>')
    out.append('<p class="note">The range above is indicative. Brands, pack sizes, origin and availability change with each shipment — '
               '<a href="/enquiry/?type=catalogue">request the current catalogue</a> or ask our team for today\'s availability.</p>')
    return "\n".join(out)


def category_cards():
    meta = {
        "seafood": ("seafood/lobster-tail", "Premium Seafood", "/seafood/"),
        "japanese-asian-foods": ("japanese-asian/sushi-rice", "Japanese & Asian Foods", "/japanese-asian-foods/"),
        "imported-cheese": (None, "Imported Cheese", "/imported-cheese/"),
        "chicken-lamb": (None, "Chicken, Lamb & Poultry", "/chicken-lamb/"),
    }
    out = ['<ul class="cats" role="list">']
    for c in CATALOG["categories"]:
        pic, title, href = meta[c["slug"]]
        visual = img(pic, title, sizes="(max-width: 640px) 100vw, 25vw") if pic else f'<div class="cat-ph cat-ph-{c["slug"]}" aria-hidden="true"><span>{ {"imported-cheese":"Cheese","chicken-lamb":"Lamb &amp; Poultry"}.get(c["slug"], e(title)) }</span></div>'
        out.append(f'<li class="cat"><a href="{href}">{visual}<div class="cat-b"><h3>{e(title)}</h3><p>{e(c["short"])}</p><span class="more">Explore range {icon("arrow",16)}</span></div></a></li>')
    out.append("</ul>")
    return "\n".join(out)


def stock_fig(path, alt, caption="Illustrative photo", cls="photo"):
    """A licensed stock photo (see IMAGE-CREDITS.md / manifest.json), always captioned as illustrative."""
    return (f'<figure class="{cls}"><img src="/assets/img/stock/{path}-900.webp" srcset="/assets/img/stock/{path}-900.webp 900w, /assets/img/stock/{path}-1600.webp 1600w" '
            f'sizes="(max-width: 860px) 100vw, 560px" width="900" height="600" loading="lazy" decoding="async" alt="{e(alt)}"><figcaption>{e(caption)}</figcaption></figure>')


def mosaic():
    picks = [("seafood/lobster-tail", "Frozen lobster tails measured against a steel rule"), ("seafood/tuna-yellowfin-saku", "Yellowfin tuna saku block"),
             ("seafood/chilean-sea-bass", "Chilean sea bass fillet"), ("seafood/mud-crabs", "Tied mud crabs"),
             ("seafood/squid-tube", "Packed IQF squid tubes"), ("japanese-asian/sushi-rice", "Kokuho premium rice pack")]
    cells = "".join(f'<figure class="m m{i}">{img(s, a, sizes="(max-width:900px) 33vw, 220px", eager=i < 2)}</figure>' for i, (s, a) in enumerate(picks))
    return f'<div class="mosaic">{cells}</div>'


def contact_block():
    a = SITE["address"]
    phones = "".join(f'<li>{icon("phone")}<span><small>{e(p["label"])}</small><a href="tel:{p["tel"]}">{e(p["display"])}</a></span></li>' for p in SITE["phones"])
    hours = f'<li>{icon("headset")}<span><small>Hours</small>{e(SITE["hours"])}</span></li>' if SITE["hours"] else ""
    return f'''<ul class="contact-list" role="list">
{phones}
<li>{icon("wa")}<span><small>WhatsApp</small><a href="{e(wa_link("Hello Divya Luxury Foods, I have a business enquiry."))}" target="_blank" rel="noopener">Chat on WhatsApp</a></span></li>
<li>{icon("mail")}<span><small>Email</small><a href="mailto:{SITE["email"]}">{e(SITE["email"])}</a></span></li>
<li>{icon("pin")}<span><small>Office</small><a href="{e(SITE["maps_url"])}" target="_blank" rel="noopener">{e(a["street"])}, {e(a["locality"])} {e(a["postal"])}</a></span></li>
{hours}
</ul>'''


def enquiry_form():
    server = SITE["form_endpoint"].get("server_form", False)
    cats = "".join(f'<label class="cb"><input type="checkbox" name="interest" value="{e(v)}"> {e(v)}</label>' for v in
                   ["Seafood", "Japanese & Asian foods", "Imported cheese", "Chicken & lamb", "Other"])
    return f'''<form class="enq" id="enquiry" novalidate data-wa="{SITE["whatsapp"]}" data-email="{SITE["email"]}" data-server="{"1" if server else "0"}">
  <fieldset class="seg"><legend>I would like to</legend>
    <label><input type="radio" name="type" value="quote" checked> Request a quote</label>
    <label><input type="radio" name="type" value="catalogue"> Request the catalogue</label>
    <label><input type="radio" name="type" value="general"> General / partnership enquiry</label>
  </fieldset>
  <div class="row2">
    <div class="f"><label for="f-name">Your name *</label><input id="f-name" name="name" autocomplete="name" required maxlength="80"></div>
    <div class="f"><label for="f-company">Business name *</label><input id="f-company" name="company" autocomplete="organization" required maxlength="120"></div>
  </div>
  <div class="row2">
    <div class="f"><label for="f-phone">Phone / WhatsApp *</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required inputmode="tel" maxlength="20" placeholder="+91"></div>
    <div class="f"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" maxlength="120"></div>
  </div>
  <div class="row2">
    <div class="f"><label for="f-btype">Business type</label><select id="f-btype" name="btype"><option value="">Select…</option><option>Hotel / resort</option><option>Restaurant / café / cloud kitchen</option><option>Caterer / banquet</option><option>Retailer / gourmet store</option><option>Distributor / importer</option><option>Private property / institution</option><option>Other</option></select></div>
    <div class="f"><label for="f-city">City / country *</label><input id="f-city" name="city" autocomplete="address-level2" required maxlength="80"></div>
  </div>
  <fieldset class="f"><legend>Products of interest</legend><div class="cbs">{cats}</div></fieldset>
  <div class="f"><label for="f-msg">Requirements</label><textarea id="f-msg" name="message" rows="4" maxlength="1500" placeholder="Products, approximate monthly quantity, delivery location…"></textarea></div>
  <input type="text" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <p class="consent">We use these details only to respond to your enquiry. See our <a href="/privacy-policy/">privacy policy</a>.</p>
  <div class="actions">
    {'<button type="submit" class="btn btn-gold" data-via="server">Submit enquiry</button>' if server else ''}
    <button type="submit" class="btn {"btn-line" if server else "btn-gold"}" data-via="wa">{icon("wa")} Send via WhatsApp</button>
    <button type="submit" class="btn btn-line" data-via="email">{icon("mail")} Send via email</button>
  </div>
  <p class="form-status" role="status" aria-live="polite"></p>
</form>'''


def cta_band(title="Planning your next menu or monthly purchase?", text="Share your requirements and our team will respond with availability and a quotation."):
    return f'''<section class="band"><div class="wrap band-in"><div><h2>{e(title)}</h2><p>{e(text)}</p></div>
<div class="band-act"><a class="btn btn-gold" href="/enquiry/?type=quote">Request a quote</a>
<a class="btn btn-ghost" href="{e(wa_link("Hello Divya Luxury Foods, I have a business enquiry."))}" target="_blank" rel="noopener">{icon("wa")} WhatsApp us</a></div></div></section>'''


def why_block():
    items = [
        ("snow", "Own cold storage", "Products are held in our own cold storage facilities with maintained temperatures before dispatch."),
        ("check", "Expiry checked at dispatch", "Every order is checked for shelf life before it leaves us, so expired stock never reaches your kitchen."),
        ("split", "Veg & non-veg kept separate", "Vegetarian and non-vegetarian products are stored and handled separately."),
        ("truck", "Delhi NCR base, pan-India supply", "Serving kitchens across Delhi NCR, with supply to customers across India."),
        ("headset", "Dedicated customer care", "A responsive team for orders, availability questions and after-sales support."),
        ("globe", "One supplier, many categories", "Seafood, Japanese & Asian pantry, cheese, chicken and lamb from a single point of contact."),
    ]
    lis = "".join(f'<li>{icon(i,28)}<h3>{e(t)}</h3><p>{e(d)}</p></li>' for i, t, d in items)
    return f'<ul class="why" role="list">{lis}</ul>'


def credentials():
    items = []
    if SITE.get("fssai"): items.append(("FSSAI Central Licence", SITE["fssai"], "Importer · Wholesaler · Distributor · Exporter"))
    if SITE.get("gstin"): items.append(("GSTIN", SITE["gstin"], "GST registered company"))
    if SITE.get("iec"): items.append(("Import Export Code (IEC)", SITE["iec"], "Registered with DGFT"))
    lis = "".join(f'<li><small>{e(a)}</small><strong>{e(b)}</strong><span>{e(c)}</span></li>' for a, b, c in items)
    return f'<ul class="creds" role="list">{lis}</ul>'


def service_area():
    sa = SITE.get("service_area", {})
    cities = sa.get("primary", [])
    if not cities:
        return ""
    return (f'<p class="area"><strong>Delhi NCR:</strong> {e(", ".join(cities))}. '
            f'<strong>Pan-India:</strong> supply to customers across India — delivery method and timelines confirmed with each quotation.</p>')


COMPONENTS = {
    "{{service_area}}": service_area,
    "{{credentials}}": credentials,
    "{{category_cards}}": category_cards,
    "{{mosaic}}": mosaic,
    "{{contact_block}}": contact_block,
    "{{enquiry_form}}": enquiry_form,
    "{{cta_band}}": cta_band,
    "{{why}}": why_block,
}


# ---------- layout ----------

def header(path):
    def active(href):
        return ' aria-current="page"' if path == href else ""
    items = []
    for label, href, sub in NAV:
        if sub:
            subl = "".join(f'<li><a href="{h}"{active(h)}>{e(l)}</a></li>' for l, h in sub)
            items.append(f'<li class="has-sub"><a href="{href}"{active(href)}>{e(label)}</a><ul class="sub">{subl}</ul></li>')
        else:
            items.append(f'<li><a href="{href}"{active(href)}>{e(label)}</a></li>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="hdr"><div class="wrap hdr-in">
<a class="brand" href="/" aria-label="{e(SITE["brand"])} — home"><span class="brand-mark">DIVYA</span><span class="brand-sub">LUXURY FOODS</span></a>
<button class="nav-btn" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span><span class="sr">Menu</span></button>
<nav id="nav" aria-label="Main"><ul class="nav">{"".join(items)}</ul>
<a class="btn btn-gold btn-sm nav-cta" href="/enquiry/?type=quote">Get a quote</a></nav>
</div></header>'''


def footer():
    a = SITE["address"]
    soc = []
    for k, ic, lbl in (("instagram", "ig", "Instagram"), ("linkedin", "in", "LinkedIn"), ("facebook", "fb", "Facebook")):
        if SITE["social"].get(k):
            soc.append(f'<a href="{e(SITE["social"][k])}" target="_blank" rel="noopener" aria-label="{lbl}">{icon(ic)}</a>')
    regs = " · ".join(x for x in [f"FSSAI Lic. No. {SITE['fssai']}" if SITE["fssai"] else "", f"GSTIN {SITE['gstin']}" if SITE["gstin"] else "", f"IEC {SITE['iec']}" if SITE.get("iec") else ""] if x)
    phones = "<br>".join(f'<a href="tel:{p["tel"]}">{e(p["display"])}</a>' for p in SITE["phones"])
    return f'''<footer class="ftr"><div class="wrap ftr-grid">
<div><p class="brand brand-f"><span class="brand-mark">DIVYA</span><span class="brand-sub">LUXURY FOODS</span></p>
<p class="muted">{e(SITE["tagline"])}. Supplying hotels, restaurants, caterers and food businesses from New Delhi.</p>
<div class="soc">{"".join(soc)}</div></div>
<div><h2 class="fh">Products</h2><ul role="list"><li><a href="/seafood/">Premium Seafood</a></li><li><a href="/japanese-asian-foods/">Japanese & Asian Foods</a></li><li><a href="/imported-cheese/">Imported Cheese</a></li><li><a href="/chicken-lamb/">Chicken, Lamb & Poultry</a></li><li><a href="/enquiry/?type=catalogue">Request catalogue</a></li></ul></div>
<div><h2 class="fh">Company</h2><ul role="list"><li><a href="/about/">About us</a></li><li><a href="/hotels-restaurants-catering/">Hotels, restaurants & catering</a></li><li><a href="/wholesale-supply/">B2B wholesale supply</a></li><li><a href="/international-enquiries/">International enquiries</a></li><li><a href="/guides/choosing-a-frozen-seafood-supplier/">Buyer guide</a></li></ul></div>
<div><h2 class="fh">Contact</h2><p class="muted">{e(a["street"])},<br>{e(a["locality"])} {e(a["postal"])}, {e(a["country_name"])}</p><p>{phones}<br><a href="mailto:{SITE["email"]}">{e(SITE["email"])}</a></p></div>
</div>
<div class="wrap ftr-base"><p>© {date.today().year} {e(SITE["legal_name"])} All rights reserved.{("<br>" + e(regs)) if regs else ""}</p>
<p><a href="/privacy-policy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/delivery-cancellation-refund-policy/">Delivery, cancellation & refunds</a></p></div></footer>
<a class="wa-float" href="{e(wa_link("Hello Divya Luxury Foods, I have a business enquiry."))}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{icon("wa",28)}</a>'''


def org_schema():
    a = SITE["address"]
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": BASE + "/#organization",
        "name": SITE["legal_name"],
        "alternateName": [SITE["brand"], "Divya Foods"],
        "url": BASE + "/",
        "logo": BASE + "/assets/img/logo-mark.png",
        "description": SITE["description"],
        "email": SITE["email"],
        "telephone": SITE["phones"][0]["tel"],
        "address": {"@type": "PostalAddress", "streetAddress": a["street"], "addressLocality": a["locality"],
                    "addressRegion": a["region"], "postalCode": a["postal"], "addressCountry": a["country"]},
        "areaServed": [{"@type": "City", "name": c} for c in SITE.get("service_area", {}).get("primary", [])] + [{"@type": "Country", "name": "India"}],
        "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "telephone": p["tel"],
                          "email": SITE["email"], "areaServed": "IN", "availableLanguage": ["en", "hi"]} for p in SITE["phones"]],
        "sameAs": [v for v in SITE["social"].values() if v],
    }
    if SITE.get("gstin"):
        org["taxID"] = SITE["gstin"]
    if SITE.get("fssai"):
        org["identifier"] = [{"@type": "PropertyValue", "propertyID": "FSSAI Licence", "value": SITE["fssai"]}]
    web = {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/",
           "name": SITE["brand"], "publisher": {"@id": BASE + "/#organization"}, "inLanguage": "en-IN"}
    return [org, web]


def breadcrumb_schema(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + h} for i, (n, h) in enumerate(crumbs)]}


def breadcrumbs_html(crumbs):
    if len(crumbs) < 2:
        return ""
    parts = [f'<li><a href="{h}">{e(n)}</a></li>' for n, h in crumbs[:-1]] + [f'<li aria-current="page">{e(crumbs[-1][0])}</li>']
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'


def page(meta, body, path):
    url = BASE + path
    title = meta["title"]
    desc = meta["description"]
    crumbs = [("Home", "/")] + [tuple(c) for c in meta.get("crumbs", [])]
    schemas = list(meta.get("schema", []))
    if path == "/":
        schemas = org_schema() + schemas
    elif len(crumbs) > 1:
        schemas.append(breadcrumb_schema(crumbs))
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    robots = meta.get("robots", "index,follow,max-image-preview:large")
    ogimg = BASE + "/assets/img/og-default.jpg"
    verif = ""
    if SITE.get("google_site_verification"):
        verif += f'<meta name="google-site-verification" content="{e(SITE["google_site_verification"])}">'
    if SITE.get("bing_site_verification"):
        verif += f'<meta name="msvalidate.01" content="{e(SITE["bing_site_verification"])}">'
    canonical = "" if meta.get("noindex") else f'<link rel="canonical" href="{url}">'
    return f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
{canonical}
<meta name="theme-color" content="#0B1D2A">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE["brand"])}">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ogimg}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{verif}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/cormorant-garamond-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
{ld}
</head>
<body class="{meta.get("body_class","")}">
{header(path)}
{breadcrumbs_html(crumbs) if path != "/" and meta.get("show_crumbs", True) else ""}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
</body>
</html>'''


META_RE = re.compile(r"^<!--meta\s*(\{.*?\})\s*-->\s*", re.S)


def render_body(src, meta):
    for k, fn in COMPONENTS.items():
        if k in src:
            src = src.replace(k, fn())
    src = re.sub(r"\{\{products:([a-z-]+)\}\}", lambda m: products_block(m.group(1)), src)
    note = " If you use the \"Submit enquiry\" button, your details are sent securely from our website to our sales inbox through our email delivery provider (Resend); they are not stored on the website." if SITE["form_endpoint"].get("server_form") else ""
    src = src.replace("{{form_note}}", note)
    src = src.replace("{{email}}", e(SITE["email"])).replace("{{legal_name}}", e(SITE["legal_name"]))
    src = src.replace("{{brand}}", e(SITE["brand"])).replace("{{updated}}", meta.get("updated", TODAY))
    src = src.replace("{{address}}", e(f'{SITE["address"]["street"]}, {SITE["address"]["locality"]} {SITE["address"]["postal"]}, India'))
    src = re.sub(r"\{\{stock:([a-z0-9/-]+)\|(.+?)\}\}", lambda m: stock_fig(m.group(1), m.group(2)), src)
    src = re.sub(r"\{\{wa:(.+?)\}\}", lambda m: e(wa_link(m.group(1))), src)
    src = re.sub(r"\{\{icon:([a-z]+)\}\}", lambda m: icon(m.group(1)), src)
    left = re.findall(r"\{\{[^}]+\}\}", src)
    if left:
        raise SystemExit(f"Unresolved placeholders: {left}")
    return src


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "src", DIST)
    urls = []
    for f in sorted((ROOT / "content/pages").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = META_RE.match(raw)
        if not m:
            raise SystemExit(f"{f.name}: missing <!--meta {{...}} --> header")
        meta = json.loads(m.group(1))
        body = render_body(raw[m.end():], meta)
        path = meta["path"]
        out = DIST / ("404.html" if path == "/404" else (path.strip("/") + "/index.html" if path != "/" else "index.html"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(meta, body, path if path != "/404" else "/404"), encoding="utf-8")
        if not meta.get("noindex") and path != "/404":
            urls.append((path, meta.get("priority", "0.7")))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, pr in sorted(urls, key=lambda x: (x[0] != "/", x[0])):
        sm.append(f"  <url><loc>{BASE}{p}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(urls)} indexable pages + 404 into {DIST}")


if __name__ == "__main__":
    main()
