#!/usr/bin/env python3
"""Tells IndexNow (Bing, Yandex, Seznam, Naver...) which pages a deploy changed.

    python3 .github/indexnow.py <old-sha> <new-sha>   # pages changed between two commits
    python3 .github/indexnow.py                        # every page in sitemap.xml

A changed `<dir>/index.html` is the page https://gentleskin.app/<dir>/. Only URLs
listed in sitemap.xml are sent (so /go/, /ig/ and drafts never are). If the diff
can't be read, it falls back to the whole sitemap.
"""
import glob, json, os, re, subprocess, sys, urllib.request

HOST = "gentleskin.app"
SITE = f"https://{HOST}/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_FILE = [f for f in glob.glob(os.path.join(ROOT, "*.txt"))
            if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(f))][0]
KEY = open(KEY_FILE).read().strip()

sitemap = re.findall(r"<loc>(.*?)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())
urls = sitemap
if len(sys.argv) == 3:
    try:
        changed = subprocess.run(["git", "diff", "--name-only", sys.argv[1], sys.argv[2]], cwd=ROOT,
                                 check=True, capture_output=True, text=True).stdout.split()
        pages = {SITE + f[: -len("index.html")] for f in changed if f == "index.html" or f.endswith("/index.html")}
        urls = [u for u in sitemap if u in pages]
    except subprocess.CalledProcessError as e:
        print("diff failed, sending the whole sitemap:", e.stderr.strip())

if not urls:
    print("No changed pages to submit.")
    sys.exit(0)

print("Submitting", len(urls), "URLs:", *urls, sep="\n  ")
body = json.dumps({"host": HOST, "key": KEY, "keyLocation": SITE + os.path.basename(KEY_FILE), "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, r.read().decode()[:300])
except urllib.error.HTTPError as e:
    print("IndexNow:", e.code, e.read().decode()[:300])
    sys.exit(1)
