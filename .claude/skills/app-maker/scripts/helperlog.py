"""The helpers' log: every time a helper script nudged Claude or did something on its own.

Two helpers write here — the engineering center's ticker (code-orchestrator/scripts/ticker.py)
and the app's server (app_server.py). One line of JSON per action in <app>/helpers-log.jsonl:

    {"t": iso, "by": "ticker"|"app server", "kind": "wake"|"update"|"handover"|"notify"|"problem",
     "text": "a plain sentence", "ok": true, "detail": "exactly what was sent"}

The engineering center's Ticker section reads it. Kept to the last 2,000 lines.
"""
import json, os
from datetime import datetime, timezone

KEEP = 2000


def log(app, by, kind, text, ok=True, detail=""):
    path = os.path.join(app, "helpers-log.jsonl")
    line = json.dumps({"t": datetime.now(timezone.utc).isoformat(timespec="seconds"), "by": by, "kind": kind,
                       "text": text, "ok": ok, "detail": detail[:2000]})
    try:
        with open(path, "a") as f:
            f.write(line + "\n")
        if os.path.getsize(path) > 1_500_000:          # trim: keep the newest lines
            lines = open(path).read().splitlines()[-KEEP:]
            open(path, "w").write("\n".join(lines) + "\n")
    except OSError:
        pass
