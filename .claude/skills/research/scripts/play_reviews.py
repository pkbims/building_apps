#!/usr/bin/env python3
"""Pull recent Google Play reviews. Usage: play_reviews.py <country> name=package ... [--count N]"""
import json, os, sys
from google_play_scraper import app, reviews, Sort
args = [a for a in sys.argv[1:] if not a.startswith("--")]
count = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--count=")), 300))
country, pairs = args[0], [a.split("=", 1) for a in args[1:]]
os.makedirs("reviews", exist_ok=True)
path = "reviews/play.json"
out = json.load(open(path)) if os.path.exists(path) else {}
for name, pkg in pairs:
    try:
        meta = app(pkg, lang="en", country=country)
    except Exception as e:
        print(f"{name}: not found ({str(e)[:40]})"); continue
    r, _ = reviews(pkg, lang="en", country=country, sort=Sort.NEWEST, count=count)
    url = f"https://play.google.com/store/apps/details?id={pkg}&hl=en&gl={country.upper()}"
    out[name] = {"title": meta["title"], "installs": meta.get("installs"), "score": meta.get("score"),
                 "ratings": meta.get("ratings"), "url": url,
                 "reviews": [{"id": x["reviewId"], "rating": x["score"], "date": str(x["at"])[:10],
                              "author": x["userName"], "text": x["content"], "url": f"{url}&reviewId={x['reviewId']}"} for x in r]}
    low = sum(1 for x in r if x["score"] <= 2)
    print(f"{name:14} {meta['title'][:36]:36} {meta.get('installs')!s:>12} {round(meta.get('score') or 0, 2)} reviews={len(r)} low={low}")
    json.dump(out, open(path, "w"), indent=1)
