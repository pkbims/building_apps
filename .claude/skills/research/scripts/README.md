# Research scripts

Three steps, run in order. Output lands in a `reviews/` folder next to wherever you run them.

```bash
python3 -m venv .venv && .venv/bin/pip install -q google-play-scraper
.venv/bin/python play_reviews.py  ca  supercook=com.supercook.app  cooklist=com.cooklist.android
python3 appstore_reviews.py       ca  supercook=1477747816         cooklist=1352600944
python3 verify_quotes.py          ../research/<niche>.md
```

- `play_reviews.py <country> name=package ...` — 300 most recent Google Play reviews per
  app, with installs/score, and a per-review link (`&reviewId=`). Use `search` in the
  script to find package IDs. This is the reliable source.
- `appstore_reviews.py <country> name=appId ...` — the 10 reviews embedded in the App
  Store page plus the RSS feed with retries (works for some apps, not others; also tries
  `us`). No per-review links exist on Apple; link the reviews page.
- `verify_quotes.py <file.md>` — every `"…" — [` quote in the file must exist verbatim in
  the pulled JSON. Run it before you call the file done. Whitespace differences are
  reported so you can decide.

Find App Store IDs: `curl 'https://itunes.apple.com/search?term=<name>&country=ca&entity=software&limit=3'`.
Trustpilot blocks curl (403); use the browser and read `__NEXT_DATA__`. Reddit is blocked
in the browser too.
