#!/usr/bin/env python3
"""The build room's heartbeat. No model, no tokens — a plain loop, run in the herdr servers-tab.

    ticker.py <room> --app <app_dir> [--orchestrator code-orchestrator] [--workers backend,ios] [--interval 300]

Every 10 s:
  - the user sent a round on the page (INBOX.md changed) → type a prompt into the orchestrator's
    herdr pane, so it wakes up and reads it. More reliable than a watcher inside a Claude session,
    which the harness can reap.
  - a new question appeared in feed.json → a macOS notification, so the user hears about it even
    with the page closed.
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


def open_questions(app):
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
            is_open = bool(re.search(r"\*\*Status:\*\*\s*open\b", body))
            status[title.strip()] = status.get(title.strip(), True) and is_open
    return sum(status.values())


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
    last_beat, last_iso = 0.0, datetime.now(timezone.utc).isoformat(timespec="seconds")

    while True:
        # 1. a round was sent → wake the orchestrator
        m = os.path.getmtime(inbox) if os.path.exists(inbox) else 0
        if m != last_inbox:
            last_inbox = m
            if x.orchestrator in agents():
                sh(["herdr", "agent", "prompt", x.orchestrator,
                    f"The user sent a round on the build room. Read {room}/INBOX.md and act on it: answer "
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
                notify(f"{name} build room — needs you", it.get("text", "")[:180])

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
            status.update({"t": now_iso, "interval": x.interval, "agents": {w: ag.get(w, "not running") for w in watch},
                           "branches": branches(app)[:8], "open_questions": oq, "heartbeats": heartbeats})
            last_beat, last_iso = time.time(), now_iso
        status["seen_asks"] = sorted(seen_asks)
        status["alive"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        write_json(status_path, status)
        time.sleep(10)


if __name__ == "__main__":
    main()
