#!/usr/bin/env python3
"""Record what trying the app cost — the engineering center's Expenses → Tests.

    expense.py <room> test "One real room on the live server" --openai 0.18 --searchapi 0.015 --calls 4 --searches 6
    expense.py <room> list

Writes <room>/expenses.json (tests only). Monthly bills are set by the user on the page.
Record real figures only: from the backend's own cost log, a provider's usage page, or a run you measured.
"""
import argparse, json, os, tempfile
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("room")
sub = ap.add_subparsers(dest="cmd", required=True)
t = sub.add_parser("test"); t.add_argument("what")
for k in ("openai", "searchapi"):
    t.add_argument("--" + k, type=float, default=0.0)
t.add_argument("--calls", type=int, default=0); t.add_argument("--searches", type=int, default=0)
t.add_argument("--when", default=None, help="ISO time of the run (default: now)")
t.add_argument("--source", default="measured")
sub.add_parser("list")
x = ap.parse_args()
path = os.path.join(x.room, "expenses.json")
try:
    data = json.load(open(path))
except (OSError, ValueError):
    data = {"tests": []}
if x.cmd == "test":
    data["tests"].append({"t": x.when or datetime.now(timezone.utc).isoformat(timespec="seconds"), "what": x.what,
                          "openai": round(x.openai, 4), "searchapi": round(x.searchapi, 4),
                          "calls": x.calls, "searches": x.searches, "source": x.source})
    fd, tmp = tempfile.mkstemp(dir=x.room, suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)
    print("recorded")
else:
    tot = sum(r["openai"] + r["searchapi"] for r in data["tests"])
    print(f"{len(data['tests'])} runs, ${tot:.2f}")
