#!/usr/bin/env python3
"""Instagram scheduler for @gentleskinapp (official Instagram API, Instagram Login).

Queue a post on your Mac, and GitHub Actions (.github/workflows/ig.yml, every 10 min)
publishes it when it is due.

    python3 ig/ig.py queue pov-carousel --at "2026-11-05 21:30" --caption-file cap.txt --images 01.png 02.png ...
    python3 ig/ig.py queue pov-reel --at "2026-11-05 21:30" --caption "..." --video pov-short.mp4 [--cover cover.png]
    python3 ig/ig.py queue pov-story --at now --story --images 01.png      (or --video)
    python3 ig/ig.py list                 # queued + recently posted
    python3 ig/ig.py unqueue <slug>       # drop a queued post
    python3 ig/ig.py me                   # check the token (needs IG_TOKEN)
    python3 ig/ig.py run                  # publish everything due (what the workflow runs)

Times without a zone are Buenos Aires time. `queue` commits and pushes on its own.

Where things live:
- ig/queue/<slug>.json      a queued post; ig/posted/<slug>.json once published (id + permalink)
- ig/media/<slug>/*.jpg     images (JPEG, Instagram's only image format), served from
                            gentleskin.app so Instagram can fetch them; deleted after posting
- videos: assets of the GitHub release `ig-media` (kept out of git history); the
  workflow downloads them and sends the bytes with Instagram's resumable upload
"""
import argparse, datetime as dt, json, os, shutil, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IG = os.path.join(ROOT, "ig")
QUEUE, POSTED, MEDIA = (os.path.join(IG, d) for d in ("queue", "posted", "media"))
SITE = "https://gentleskin.app"
REPO = "pivotrooky/gentleskin-site"
RELEASE = "ig-media"
API = "https://graph.instagram.com/v23.0"
BA = dt.timezone(dt.timedelta(hours=-3))


# ---------- Instagram API ----------

def token():
    t = os.environ.get("IG_TOKEN")
    if not t:
        sys.exit("IG_TOKEN is not set")
    return t


def api(method, path, **params):
    params["access_token"] = token()
    url = path if path.startswith("http") else f"{API}/{path}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path}: {e.code} {e.read().decode(errors='replace')}") from None


def wait_ready(container):
    for _ in range(60):  # up to ~10 min for a Reel to process
        s = api("GET", container, fields="status_code,status")
        if s.get("status_code") == "FINISHED":
            return
        if s.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {container}: {s}")
        time.sleep(10)
    raise RuntimeError(f"container {container} still not ready")


def image_container(uid, url, **extra):
    return api("POST", f"{uid}/media", image_url=url, **extra)["id"]


def video_container(uid, path, **extra):
    """Resumable upload: create the container, then POST the bytes to rupload."""
    c = api("POST", f"{uid}/media", upload_type="resumable", **extra)
    size = os.path.getsize(path)
    req = urllib.request.Request(c["uri"], data=open(path, "rb").read(), method="POST", headers={
        "Authorization": f"OAuth {token()}", "offset": "0", "file_size": str(size)})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"upload {path}: {e.code} {e.read().decode(errors='replace')}") from None
    return c["id"]


def publish(post):
    uid = api("GET", "me", fields="user_id")["user_id"]
    urls = [f"{SITE}/{p}" for p in post.get("images", [])]
    for u in urls + ([f"{SITE}/{post['cover']}"] if post.get("cover") else []):
        check_url(u)
    cap = {"caption": post["caption"]} if post.get("caption") else {}
    kind = post["type"]
    if kind == "carousel":
        kids = [image_container(uid, u, is_carousel_item="true") for u in urls]
        for k in kids:
            wait_ready(k)
        cid = api("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(kids), **cap)["id"]
    elif kind == "image":
        cid = image_container(uid, urls[0], **cap)
    elif kind == "reel":
        extra = {"media_type": "REELS", "share_to_feed": "true", **cap}
        if post.get("cover"):
            extra["cover_url"] = f"{SITE}/{post['cover']}"
        cid = video_container(uid, fetch_video(post["video"]), **extra)
    elif kind == "story":
        if post.get("video"):
            cid = video_container(uid, fetch_video(post["video"]), media_type="STORIES")
        else:
            cid = image_container(uid, urls[0], media_type="STORIES")
    else:
        raise RuntimeError(f"unknown type {kind}")
    wait_ready(cid)
    mid = api("POST", f"{uid}/media_publish", creation_id=cid)["id"]
    try:
        link = api("GET", mid, fields="permalink").get("permalink")
    except RuntimeError:
        link = None
    return mid, link


def check_url(u):
    """Pages deploys a minute or so after a push; don't hand Instagram a 404."""
    try:
        with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=30) as r:
            if r.status == 200:
                return
    except urllib.error.URLError:
        pass
    raise NotYet(f"{u} is not live yet")


class NotYet(Exception):
    pass


# ---------- git / release helpers ----------

def sh(*cmd, **kw):
    return subprocess.run(cmd, check=True, cwd=ROOT, text=True, **kw)


def fetch_video(name):
    d = os.path.join(ROOT, ".ig-tmp")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    if not os.path.exists(path):
        sh("gh", "release", "download", RELEASE, "-R", REPO, "-p", name, "-D", d, "--clobber")
    return path


def ensure_release():
    if subprocess.run(["gh", "release", "view", RELEASE, "-R", REPO], cwd=ROOT, capture_output=True).returncode:
        sh("gh", "release", "create", RELEASE, "-R", REPO, "--title", "Instagram queue media",
           "--notes", "Videos waiting to be posted by ig/ig.py. Removed after posting.", "--prerelease")


def commit_push(msg, *paths):
    sh("git", "add", "-A", *paths)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        return
    sh("git", "commit", "-q", "-m", msg)
    for _ in range(3):
        if subprocess.run(["git", "push", "-q"], cwd=ROOT).returncode == 0:
            return
        sh("git", "pull", "-q", "--rebase")
    raise RuntimeError("push failed")


# ---------- commands ----------

def parse_at(s):
    if s == "now":
        return dt.datetime.now(BA)
    t = dt.datetime.fromisoformat(s.replace(" ", "T"))
    return t if t.tzinfo else t.replace(tzinfo=BA)


def to_jpeg(src, dst):
    from PIL import Image
    im = Image.open(src)
    if im.mode != "RGB":
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.convert("RGBA").split()[3])
        im = bg
    im.save(dst, "JPEG", quality=92)


def cmd_queue(a):
    slug = a.slug
    qf = os.path.join(QUEUE, f"{slug}.json")
    if os.path.exists(qf) or os.path.exists(os.path.join(POSTED, f"{slug}.json")):
        sys.exit(f"{slug} already exists")
    caption = open(a.caption_file).read().strip() if a.caption_file else (a.caption or "")
    if len(caption) > 2200:
        sys.exit(f"caption is {len(caption)} chars; Instagram's limit is 2200")
    if a.story:
        kind = "story"
    elif a.video:
        kind = "reel"
    elif a.images and len(a.images) > 1:
        kind = "carousel"
    elif a.images:
        kind = "image"
    else:
        sys.exit("give --images or --video")
    if kind == "carousel" and len(a.images) > 10:
        sys.exit("a carousel holds at most 10 images")
    post = {"type": kind, "at": parse_at(a.at).isoformat(timespec="minutes"), "caption": caption}
    md = os.path.join(MEDIA, slug)
    imgs = list(a.images or []) + ([a.cover] if a.cover else [])
    if imgs:
        os.makedirs(md, exist_ok=True)
    rel = []
    for i, src in enumerate(a.images or [], 1):
        dst = os.path.join(md, f"{i:02d}.jpg")
        to_jpeg(src, dst)
        rel.append(os.path.relpath(dst, ROOT))
    if rel:
        post["images"] = rel
    if a.cover:
        dst = os.path.join(md, "cover.jpg")
        to_jpeg(a.cover, dst)
        post["cover"] = os.path.relpath(dst, ROOT)
    if a.video:
        ensure_release()
        name = f"{slug}.mp4"
        tmp = os.path.join(ROOT, ".ig-tmp")
        os.makedirs(tmp, exist_ok=True)
        shutil.copy(a.video, os.path.join(tmp, name))
        sh("gh", "release", "upload", RELEASE, "-R", REPO, os.path.join(tmp, name), "--clobber")
        post["video"] = name
    os.makedirs(QUEUE, exist_ok=True)
    json.dump(post, open(qf, "w"), indent=2, ensure_ascii=False)
    commit_push(f"IG queue: {slug} ({kind}) at {post['at']}", "ig")
    print(f"queued {slug}: {kind}, {post['at']}")


def load(d):
    if not os.path.isdir(d):
        return []
    return sorted(((f[:-5], json.load(open(os.path.join(d, f)))) for f in os.listdir(d) if f.endswith(".json")),
                  key=lambda x: x[1].get("at", ""))


def cmd_list(a):
    for slug, p in load(QUEUE):
        flag = f"  ERROR: {p['error']}" if p.get("error") else ""
        print(f"queued  {p['at']}  {p['type']:8} {slug}{flag}")
    for slug, p in load(POSTED)[-10:]:
        print(f"posted  {p.get('posted_at', p['at'])}  {p['type']:8} {slug}  {p.get('permalink') or ''}")


def cleanup(slug, post):
    shutil.rmtree(os.path.join(MEDIA, slug), ignore_errors=True)
    if post.get("video"):
        subprocess.run(["gh", "release", "delete-asset", RELEASE, post["video"], "-R", REPO, "-y"], cwd=ROOT)


def cmd_unqueue(a):
    qf = os.path.join(QUEUE, f"{a.slug}.json")
    post = json.load(open(qf))
    os.remove(qf)
    cleanup(a.slug, post)
    commit_push(f"IG unqueue: {a.slug}", "ig")
    print(f"removed {a.slug}")


def cmd_me(a):
    print(api("GET", "me", fields="user_id,username,account_type,media_count"))
    try:
        uid = api("GET", "me", fields="user_id")["user_id"]
        print(api("GET", f"{uid}/content_publishing_limit", fields="config,quota_usage"))
    except RuntimeError as e:
        print(e)


def cmd_run(a):
    now = dt.datetime.now(BA)
    failed = False
    for slug, post in load(QUEUE):
        if post.get("error") or parse_at(post["at"]) > now:
            continue
        qf = os.path.join(QUEUE, f"{slug}.json")
        try:
            mid, link = publish(post)
        except NotYet as e:
            print(f"{slug}: waiting, {e}")
            continue
        except Exception as e:  # mark it so it is never retried blindly; fix and clear "error" to retry
            post["error"] = str(e)[:500]
            json.dump(post, open(qf, "w"), indent=2, ensure_ascii=False)
            commit_push(f"IG failed: {slug}", "ig")
            print(f"{slug}: FAILED {e}")
            failed = True
            continue
        post.update(id=mid, permalink=link, posted_at=dt.datetime.now(BA).isoformat(timespec="minutes"))
        os.makedirs(POSTED, exist_ok=True)
        json.dump(post, open(os.path.join(POSTED, f"{slug}.json"), "w"), indent=2, ensure_ascii=False)
        os.remove(qf)
        cleanup(slug, post)
        commit_push(f"IG posted: {slug} {link or mid}", "ig")
        print(f"{slug}: posted {link or mid}")
    if failed:
        sys.exit(1)  # red run -> GitHub emails


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    q = s.add_parser("queue")
    q.add_argument("slug")
    q.add_argument("--at", required=True, help='"2026-11-05 21:30" (Buenos Aires) or "now"')
    q.add_argument("--caption")
    q.add_argument("--caption-file")
    q.add_argument("--images", nargs="+")
    q.add_argument("--video")
    q.add_argument("--cover", help="Reel cover image")
    q.add_argument("--story", action="store_true")
    s.add_parser("list")
    u = s.add_parser("unqueue")
    u.add_argument("slug")
    s.add_parser("me")
    s.add_parser("run")
    a = p.parse_args()
    {"queue": cmd_queue, "list": cmd_list, "unqueue": cmd_unqueue, "me": cmd_me, "run": cmd_run}[a.cmd](a)


if __name__ == "__main__":
    main()
