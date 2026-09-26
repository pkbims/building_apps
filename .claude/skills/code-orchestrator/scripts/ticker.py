#!/usr/bin/env python3
"""The engineering center's heartbeat. No model, no tokens — a plain loop, run in the herdr servers-tab.

    ticker.py <room> --app <app_dir> [--orchestrator code-orchestrator] [--workers backend,ios] [--interval 300]

Every 10 s:
  - the user sent a round on the page (INBOX.md changed) → type a prompt into the orchestrator's
    herdr pane, so it wakes up and reads it. More reliable than a watcher inside a Claude session,
    which the harness can reap.
  - a new question appeared in feed.json → a macOS notification, so the user hears about it even
    with the page closed.
Every 30 s:
  - a worker posted a new open checkpoint or question in any worktree's ORCH-QUESTIONS.md, or a
    worker went from working to idle/done → type a prompt into the orchestrator's pane. Workers
    stop at each checkpoint and wait, so a missed one means idle workers (happened 2026-09-26).
Every --interval seconds (default 5 min):
  - a status snapshot → status.json: each agent's state, each branch's latest commit, commits since
    the last check, open ORCH-QUESTIONS, and a one-line heartbeat the page shows in its feed.
"""
import argparse, json, os, re, subprocess, tempfile, time
from datetime import datetime, timezone


def sh(args, cwd=None):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def write_json(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def agents():
    try:
        return {a["name"]: a.get("agent_status", "?")
                for a in json.loads(sh(["herdr", "agent", "list"]))["result"]["agents"] if a.get("name")}
    except (ValueError, KeyError, TypeError):
        return {}


def branches(app):
    out = sh(["git", "for-each-ref", "--sort=-committerdate", "refs/heads",
              "--format=%(refname:short)|%(committerdate:iso-strict)|%(subject)"], cwd=app)
    return [dict(zip(("branch", "when", "subject"), l.split("|", 2))) for l in out.splitlines() if l.count("|") >= 2]


def commits_since(app, since_iso):
    out = sh(["git", "log", "--all", "--since=" + since_iso, "--format=%D|%s"], cwd=app)
    return len([l for l in out.splitlines() if l.strip()])


def open_entries(app):
    # Workers append in their own worktree, so a question is on `main` only after a merge:
    # read every worktree's copy. Only real entries count — "## Q<number>" (the format
    # example is "## Q<n>", so its "Status: open" is ignored) wherever a worker put them —
    # and an entry answered in any copy is closed.
    status = {}
    for line in sh(["git", "worktree", "list", "--porcelain"], cwd=app).splitlines():
        if not line.startswith("worktree "):
            continue
        try:
            text = open(os.path.join(line[9:], "ORCH-QUESTIONS.md")).read()
        except OSError:
            continue
        for title, body in re.findall(r"^## (Q\d+[^\n]*)\n(.*?)(?=^## |\Z)", text, re.M | re.S):
            is_open = bool(re.search(r"\*\*Status:\*\*\s*(open|checkpoint)\b", body))
            status[title.strip()] = status.get(title.strip(), True) and is_open
    return {t for t, is_open in status.items() if is_open}


def open_questions(app):
    return len(open_entries(app))


def commits(app, n=60):
    """Recent commits in three lanes by the files they touch: backend/, ios/, everything else
    (the orchestrator: contract, CI, docs). Each with its plain explanation — the first sentence
    of the commit body, which the worker briefs ask to be plain English."""
    out = sh(["git", "log", "--all", "--no-merges", "-n", str(n), "--name-only",
              "--format=%x1e%h%x1f%cI%x1f%s%x1f%b%x1d"], cwd=app)
    lanes = {"backend": [], "ios": [], "orchestrator": []}
    for rec in out.split("\x1e")[1:]:
        meta, _, names = rec.partition("\x1d")
        parts = meta.split("\x1f", 3)
        if len(parts) < 4:
            continue
        h, when, subj, body = parts
        paths = [p.strip() for p in names.splitlines() if p.strip()]
        by_orch = "Claude Opus" in body        # the orchestrator runs Opus, the workers Sonnet
        body = " ".join(l for l in body.splitlines() if not l.startswith("Co-Authored-By"))
        body = " ".join(body.split())
        m = re.match(r"(.{20,240}?[.!?])(\s|$)", body)
        why = m.group(1) if m else body[:240]
        nb = sum(p.startswith("backend/") for p in paths)
        ni = sum(p.startswith("ios/") for p in paths)
        low = subj.lower()
        lane = "orchestrator" if by_orch else "backend" if nb > ni else "ios" if ni > nb else \
            ("ios" if low.startswith("ios") else "backend" if low.startswith("backend") else "orchestrator")
        subj = re.sub(r"^(ios|backend)\s*:\s*", "", subj, flags=re.I)
        lanes[lane].append({"hash": h, "when": when, "title": subj, "why": why, "files": len(paths)})
    return {k: v[:15] for k, v in lanes.items()}


def context_use(name):
    """A worker's context use in percent, read off its Claude status line ("ctx 53%/530k")."""
    raw = sh(["herdr", "agent", "read", name])
    try:                                    # plain text today; JSON if herdr ever wraps it
        text = json.loads(raw)["result"].get("text", raw)
    except (ValueError, KeyError, TypeError, AttributeError):
        text = raw
    found = re.findall(r"ctx (\d+)%/", text)
    return int(found[-1]) if found else None


def notify(title, text):
    esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
    sh(["osascript", "-e", f'display notification "{esc(text)}" with title "{esc(title)}" sound name "Glass"'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("room")
    ap.add_argument("--app", required=True)
    ap.add_argument("--orchestrator", default="code-orchestrator")
    ap.add_argument("--workers", default="backend,ios")
    ap.add_argument("--interval", type=int, default=300)
    x = ap.parse_args()
    room, app = os.path.abspath(x.room), os.path.abspath(x.app)
    name = os.path.basename(app)
    open(os.path.join(room, ".ticker.pid"), "w").write(str(os.getpid()))
    inbox = os.path.join(room, "INBOX.md")
    status_path = os.path.join(room, "status.json")
    try:
        status = json.load(open(status_path))
    except (OSError, ValueError):
        status = {}
    heartbeats = status.get("heartbeats", [])
    last_inbox = os.path.getmtime(inbox) if os.path.exists(inbox) else 0
    seen_asks = set(status.get("seen_asks", []))
    last_commits = 0.0
    try:
        last_ask = json.load(open(os.path.join(room, "state.json"))).get("decisions", {}).get("update_request")
    except (OSError, ValueError):
        last_ask = None
    seen_entries = set(status.get("seen_entries", []))
    last_states = {}
    workers = [w for w in x.workers.split(",") if w]
    ctx_alerted = status.get("ctx_alerted", {})     # worker -> highest threshold already reported
    last_beat, last_iso = 0.0, datetime.now(timezone.utc).isoformat(timespec="seconds")

    while True:
        # 0. the user pressed "Get me an update" → ask the orchestrator for one, and refresh the status now
        try:
            ask = json.load(open(os.path.join(room, "state.json"))).get("decisions", {}).get("update_request")
        except (OSError, ValueError):
            ask = last_ask
        if ask and ask != last_ask:
            last_ask = ask
            last_beat = 0.0                      # the next block refreshes status.json straight away
            if x.orchestrator in agents():
                post = os.path.join(os.path.dirname(os.path.abspath(__file__)), "post.py")
                sh(["herdr", "agent", "prompt", x.orchestrator,
                    f"The user pressed 'Get me an update' in the engineering center. Post one update now with "
                    f"python3 {post} {room} update \"...\" — plain English, at most 4 short lines: what's done since "
                    f"your last update, what backend and ios are each on, what's next, and anything blocked or "
                    f"waiting on the user (say 'nothing' if nothing). Check git and the workers before you write it."])
                status["update_forwarded"] = ask
            else:
                status["update_forwarded"] = "no orchestrator running"
        # 1. a round was sent → wake the orchestrator
        m = os.path.getmtime(inbox) if os.path.exists(inbox) else 0
        if m != last_inbox:
            last_inbox = m
            if x.orchestrator in agents():
                sh(["herdr", "agent", "prompt", x.orchestrator,
                    f"The user sent a round on the engineering center. Read {room}/INBOX.md and act on it: answer "
                    f"questions with post.py update, resolve answered asks with post.py resolve, then mark the "
                    f"comments addressed (curl -s -X POST localhost:$(cat {room}/.port)/api/comment/addressed -d '{{}}')."])
                status["last_forwarded"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

        # 2. a new question for the user → notify
        try:
            feed = json.load(open(os.path.join(room, "feed.json")))["items"]
        except (OSError, ValueError, KeyError):
            feed = []
        for it in feed:
            if it.get("kind") == "ask" and it.get("status") == "open" and it["id"] not in seen_asks:
                seen_asks.add(it["id"])
                notify(f"{name} engineering center — needs you", it.get("text", "")[:180])

        # 3. the heartbeat
        if time.time() - last_beat >= x.interval:
            ag = agents()
            watch = [x.orchestrator] + [w for w in x.workers.split(",") if w]
            now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
            n = commits_since(app, last_iso) if last_beat else 0
            oq = open_questions(app)
            parts = [f"{w} {ag.get(w, 'not running')}" for w in watch]
            line = " · ".join(parts) + f" · {n} new commit{'s' if n != 1 else ''}" + \
                   (f" · {oq} open question{'s' if oq != 1 else ''} from workers" if oq else "")
            if last_beat:
                heartbeats.append({"t": now_iso, "text": line})
                heartbeats = heartbeats[-60:]
            # context use: wake the orchestrator once per threshold, so it can restart a worker
            # with a fresh session at its next checkpoint (60%) or right away (80%)
            ctx = {w: context_use(w) for w in watch if w in ag}   # shown on the page for everyone
            for w, pct in ((w, ctx.get(w)) for w in workers):  # alerts: workers only
                hit = max([t for t in (60, 80) if pct is not None and pct >= t], default=0)
                if hit > ctx_alerted.get(w, 0) and x.orchestrator in ag:
                    ctx_alerted[w] = hit
                    sh(["herdr", "agent", "prompt", x.orchestrator,
                        f"Worker event: {w}'s context is at {pct}%. "
                        + ("Restart it with a fresh session at its next checkpoint."
                           if hit == 60 else "Restart it now: have it commit and update its notes file first.")])
                elif pct is not None and pct < 40:
                    ctx_alerted.pop(w, None)                # a fresh session: re-arm the alerts
            status["context"] = ctx
            status["ctx_alerted"] = ctx_alerted
            status.update({"t": now_iso, "interval": x.interval, "agents": {w: ag.get(w, "not running") for w in watch},
                           "branches": branches(app)[:8], "open_questions": oq, "heartbeats": heartbeats})
            last_beat, last_iso = time.time(), now_iso
        if time.time() - last_commits >= 30:          # commits are cheap to read: every 30 s
            status["commits"] = commits(app)
            last_commits = time.time()
            # 4. worker events → wake the orchestrator
            wake = []
            for title in sorted(open_entries(app) - seen_entries):
                seen_entries.add(title)
                wake.append(f"a worker posted in ORCH-QUESTIONS.md: \"{title}\"")
            ag = agents()
            for w in workers:
                st = ag.get(w)
                if last_states.get(w) == "working" and st in ("idle", "done"):
                    # a worker that ended its turn to wait on its own background job ("1 monitor
                    # still running") will be woken by that job — not a stop worth waking for
                    waiting = re.search(r"(shell|monitor)s? still running", sh(["herdr", "agent", "read", w])[-2000:])
                    if not waiting:
                        wake.append(f"{w} stopped working (now {st}) — at a checkpoint, finished, or blocked")
                if st:
                    last_states[w] = st
            if wake and x.orchestrator in ag:
                sh(["herdr", "agent", "prompt", x.orchestrator,
                    "Worker event: " + "; ".join(wake) + ". Read the worker's ORCH-QUESTIONS.md in its "
                    "worktree and its pane (herdr agent read <name>); a checkpoint means verify, then "
                    "merge and post it — the worker waits until you answer."])
        status["seen_asks"] = sorted(seen_asks)
        status["seen_entries"] = sorted(seen_entries)
        status["alive"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        write_json(status_path, status)
        time.sleep(10)


if __name__ == "__main__":
    main()
