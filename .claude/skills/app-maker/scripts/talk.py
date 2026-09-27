#!/usr/bin/env python3
"""Reply in a page's "Talk to Claude" box.

    talk.py <page_dir> "your reply"

Appends to <page_dir>/talk.json, which the App Maker shows under that stage. Written by the
app server (the user's messages) and by this script (the replies) — both append whole lines,
never edit.
"""
import json, os, sys, tempfile
from datetime import datetime, timezone

d, text = sys.argv[1], " ".join(sys.argv[2:]).strip()
if not text:
    raise SystemExit("usage: talk.py <page_dir> \"reply\"")
path = os.path.join(d, "talk.json")
try:
    talk = json.load(open(path))
except (OSError, ValueError):
    talk = {"messages": []}
talk["messages"].append({"from": "claude", "t": datetime.now(timezone.utc).isoformat(timespec="seconds"), "text": text})
fd, tmp = tempfile.mkstemp(dir=d, suffix=".json")
with os.fdopen(fd, "w") as f:
    json.dump(talk, f, indent=1)
os.replace(tmp, path)
print("replied")
