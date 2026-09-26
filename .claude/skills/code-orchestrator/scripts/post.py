#!/usr/bin/env python3
"""Post to the engineering center's feed — the orchestrator's only way to talk to the user.

    post.py <room> update "Contract frozen: 14 routes, CI green."
    post.py <room> ask apple "Do you have an Apple Developer team?" --why "Needed for sign-in and TestFlight." \
        --option yes "Yes" "Tell me the team name in a comment." \
        --option no "Not yet" "The worker builds sign-in anyway; it's tested once you have one." --rec yes
    post.py <room> resolve apple --note "Team: Bimal Saran"
    post.py <room> checkpoint "FindWhatsInTheRoom merged" --detail "12 tests, flow checked by hand" --verified
    post.py <room> todo oracle "Sign up for Oracle Cloud Always Free"      /  post.py <room> done oracle
    post.py <room> todo repo "Create the GitHub repo" --now                 # --now: the build is waiting on it
    post.py <room> plan backend "Skeleton" "The chain" "Baseline"      # a half's build steps, in order
    post.py <room> step backend 2 doing                                 # done | doing | todo (1-based)

A step is `done` only when the orchestrator has verified and merged it — the meter shows
merged work, not claims.

Writes <room>/feed.json atomically. Only this script writes feed.json; the page server owns
state.json and the ticker owns status.json, so nothing races.
"""
import argparse, json, os, tempfile
from datetime import datetime, timezone


def load(room):
    try:
        return json.load(open(os.path.join(room, "feed.json")))
    except (OSError, json.JSONDecodeError):
        return {"items": []}


def save(room, feed):
    fd, tmp = tempfile.mkstemp(dir=room, suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(feed, f, indent=1)
    os.replace(tmp, os.path.join(room, "feed.json"))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def find(feed, id):
    return next((i for i in feed["items"] if i.get("id") == id), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("room")
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("update"); u.add_argument("text")
    a = sub.add_parser("ask"); a.add_argument("id"); a.add_argument("text")
    a.add_argument("--why", default="")
    a.add_argument("--option", nargs=3, action="append", metavar=("VALUE", "LABEL", "DETAIL"), default=[])
    a.add_argument("--rec", default=None)
    r = sub.add_parser("resolve"); r.add_argument("id"); r.add_argument("--note", default="")
    c = sub.add_parser("checkpoint"); c.add_argument("text"); c.add_argument("--detail", default="")
    c.add_argument("--verified", action="store_true")
    t = sub.add_parser("todo"); t.add_argument("id"); t.add_argument("text")
    t.add_argument("--now", action="store_true", help="the build is waiting on it: shown under Needs you, not in the no-rush list")
    d = sub.add_parser("done"); d.add_argument("id")
    pl = sub.add_parser("plan"); pl.add_argument("half"); pl.add_argument("steps", nargs="+")
    st = sub.add_parser("step"); st.add_argument("half"); st.add_argument("n", type=int)
    st.add_argument("status", choices=["done", "doing", "todo"]); st.add_argument("--note", default="")
    x = ap.parse_args()

    feed = load(x.room)
    items = feed["items"]
    progress = feed.setdefault("progress", {})
    if x.cmd == "plan":                       # keeps the status of steps whose name is unchanged
        old = {st["name"]: st for st in progress.get(x.half, [])}
        progress[x.half] = [old.get(n, {"name": n, "status": "todo"}) for n in x.steps]
    elif x.cmd == "step":
        steps = progress.get(x.half) or []
        if not 1 <= x.n <= len(steps):
            raise SystemExit(f"{x.half} has {len(steps)} steps; plan them first")
        steps[x.n - 1].update({"status": x.status, "t": now(), **({"note": x.note} if x.note else {})})
    if x.cmd == "update":
        items.append({"id": "u%d" % len(items), "kind": "update", "t": now(), "text": x.text})
    elif x.cmd == "ask":
        if not x.id.replace("_", "").isalnum():
            raise SystemExit("ask id: letters, digits and _ only (it becomes a decision id)")
        if x.option and x.rec not in [o[0] for o in x.option]:
            raise SystemExit("an ask with options needs --rec naming one of them (series rule: every decision has a recommended option)")
        old = find(feed, x.id)
        if old:
            items.remove(old)
        items.append({"id": x.id, "kind": "ask", "t": now(), "text": x.text, "why": x.why,
                      "options": x.option, "rec": x.rec, "status": "open"})
    elif x.cmd == "resolve":
        it = find(feed, x.id)
        if not it:
            raise SystemExit("no such ask: " + x.id)
        it["status"] = "resolved"; it["resolved"] = now(); it["note"] = x.note
    elif x.cmd == "checkpoint":
        items.append({"id": "c%d" % len(items), "kind": "checkpoint", "t": now(), "text": x.text,
                      "detail": x.detail, "verified": x.verified})
    elif x.cmd == "todo":
        old = find(feed, x.id)
        if old:
            items.remove(old)
        items.append({"id": x.id, "kind": "todo", "t": now(), "text": x.text, "status": "open", "now": x.now})
    elif x.cmd == "done":
        it = find(feed, x.id)
        if not it:
            raise SystemExit("no such todo: " + x.id)
        it["status"] = "done"; it["resolved"] = now()
    save(x.room, feed)
    print("posted", x.cmd)


if __name__ == "__main__":
    main()
