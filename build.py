#!/usr/bin/env python3
"""Builds the Gentleskin site: content/*.html -> pages with the shared shell.

    python3 build.py

Each content file starts with a header block, then the body HTML:

    title: How to stop picking your skin
    description: One sentence for search results.
    path: guides/how-to-stop-picking-skin/   (index.html is written there)
    ---
    <h1>...</h1>
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://gentleskin.app"
APP_ID = "6789245158"
UPDATED = "2026-10-19"


def store(ct):
    # App Store link with a campaign token, so App Store Connect shows where installs came from.
    return f"https://apps.apple.com/app/apple-store/id{APP_ID}?pt=668857691&ct={ct}&mt=8"


def shell(title, description, path, body, depth, kind):
    up = "../" * depth
    url = SITE + "/" + path
    ld = [{
        "@context": "https://schema.org", "@type": "MobileApplication",
        "name": "Gentleskin: Skin Picking", "operatingSystem": "iOS",
        "applicationCategory": "HealthApplication",
        "url": SITE + "/", "installUrl": store("web"),
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD",
                   "description": "7-day free trial, then a yearly or monthly membership"},
    }]
    if kind == "article":
        ld.append({
            "@context": "https://schema.org", "@type": "Article", "headline": title,
            "description": description, "dateModified": UPDATED, "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": "Gentleskin"},
        })
    faq = re.findall(r"<details><summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": re.sub("<.*?>", "", q),
             "acceptedAnswer": {"@type": "Answer", "text": re.sub("<.*?>", "", a).strip()}}
            for q, a in faq]})
    body = body.replace("{{store}}", store("web" if kind == "home" else "web_guide")).replace("{{up}}", up)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{url}">
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="{SITE}/img/header.jpg">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF1F3">
<link rel="icon" href="{up}img/favicon.png">
<link rel="apple-touch-icon" href="{up}img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Albert+Sans:wght@400;600&family=Castoro:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}style.css">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0])}</script>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="{up or './'}"><img src="{up}img/icon.png" alt="">Gentleskin</a>
  <nav><a href="{up}guides/">Guides</a><a href="{store('web_nav')}">Get the app</a></nav>
</div></header>
{body}
<footer><div class="wrap">
  <span>Gentleskin is a self-tracking tool, not a medical device. It doesn't diagnose or treat any condition.</span>
  <span><a href="https://pivotrooky.github.io/privacy-policies/gentleskin/">Privacy</a> · <a href="https://pivotrooky.github.io/privacy-policies/gentleskin/support/">Support</a></span>
</div></footer>
</body>
</html>
"""


def main():
    pages = []
    for name in sorted(os.listdir(os.path.join(ROOT, "content"))):
        if not name.endswith(".html"):
            continue
        raw = open(os.path.join(ROOT, "content", name)).read()
        head, body = raw.split("\n---\n", 1)
        meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
        path = meta["path"].strip("/")
        path = path + "/" if path else ""
        kind = "home" if not path else ("article" if path.startswith("guides/") and path != "guides/" else "list")
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        page = shell(meta["title"], meta["description"], path, body, path.count("/"), kind)
        open(os.path.join(out_dir, "index.html"), "w").write(page)
        pages.append((path, meta))
        print("wrote", path or "/")

    urls = "".join(f"  <url><loc>{SITE}/{p}</loc><lastmod>{UPDATED}</lastmod></url>\n" for p, _ in pages)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    # llms.txt: a plain map of the site for AI assistants that read it.
    lines = ["# Gentleskin", "",
             "> A gentle iPhone app for tracking skin picking (dermatillomania, excoriation disorder) "
             "and other body-focused repetitive behaviors (BFRBs). Log a pick in two taps, see patterns, "
             "ride out urges, and make a PDF report for a therapist. No streaks.", "",
             f"- App Store: https://apps.apple.com/app/id{APP_ID}",
             "- Price: 7-day free trial, then $29.99/year or $5.99/month (US; varies by region)", "",
             "## Guides", ""]
    lines += [f"- [{m['title']}]({SITE}/{p}): {m['description']}" for p, m in pages if p.startswith("guides/") and p != "guides/"]
    open(os.path.join(ROOT, "llms.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
