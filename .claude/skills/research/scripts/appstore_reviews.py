#!/usr/bin/env python3
"""Pull App Store reviews: page-embedded JSON (10) + RSS feed where it works. Usage: appstore_reviews.py <country> name=appId ..."""
import html, json, os, re, sys, time, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
country, pairs = sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]]
os.makedirs("reviews", exist_ok=True)
path = "reviews/appstore.json"
out = json.load(open(path)) if os.path.exists(path) else {}
def walk(o, acc):
    if isinstance(o, dict):
        if o.get("$kind") == "Review" and "contents" in o: acc[o["id"]] = o
        for v in o.values(): walk(v, acc)
    elif isinstance(o, list):
        for v in o: walk(v, acc)
def rss(aid, cc, sb):
    for attempt in range(3):
        try:
            req = urllib.request.Request(f"https://itunes.apple.com/{cc}/rss/customerreviews/id={aid}/page=1/sortBy={sb}/json", headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r: e = json.load(r).get("feed", {}).get("entry")
            if e: return e if isinstance(e, list) else [e]
        except Exception: pass
        time.sleep(2 + 2 * attempt)
    return []
for name, aid in pairs:
    acc = {}
    for cc in dict.fromkeys([country, "us"]):
        try:
            req = urllib.request.Request(f"https://apps.apple.com/{cc}/app/id{aid}?see-all=reviews", headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r: s = r.read().decode("utf-8", "ignore")
            m = re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>', s, re.S)
            if m: walk(json.loads(html.unescape(m.group(1))), acc)
        except Exception as e:
            print(f"{name} {cc}: page error {str(e)[:40]}")
        time.sleep(1)
    page_url = f"https://apps.apple.com/{country}/app/id{aid}?see-all=reviews"
    revs = [{"id": r["id"], "rating": r["rating"], "title": r["title"], "text": r["contents"], "date": r["date"][:10],
             "author": r["reviewerName"], "url": page_url} for r in acc.values()]
    seen = {r["id"] for r in revs}
    for cc in dict.fromkeys([country, "us"]):
        for sb in ("mostRecent", "mostHelpful"):
            for e in rss(aid, cc, sb):
                if "im:rating" not in e or e["id"]["label"] in seen: continue
                seen.add(e["id"]["label"])
                revs.append({"id": e["id"]["label"], "rating": int(e["im:rating"]["label"]), "title": e["title"]["label"],
                             "text": e["content"]["label"], "date": e.get("updated", {}).get("label", "")[:10],
                             "author": e["author"]["name"]["label"], "url": f"https://apps.apple.com/{cc}/app/id{aid}?see-all=reviews"})
            time.sleep(0.5)
    out[name] = {"url": page_url, "reviews": revs}
    print(f"{name:14} reviews={len(revs)} low={sum(1 for r in revs if r['rating'] <= 2)}")
    json.dump(out, open(path, "w"), indent=1)
