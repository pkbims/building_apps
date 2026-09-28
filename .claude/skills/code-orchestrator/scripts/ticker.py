#!/usr/bin/env python3
"""The engineering center's heartbeat. No model, no tokens — a plain loop, run in the herdr servers-tab.

    ticker.py <room> --app <app_dir> [--orchestrator code-orchestrator] [--workers backend,ios] [--interval 300]

Every 10 s: "Get me an update" pressed → prompt the orchestrator. (A sent round and a new question
are handled by the app's server — app-maker/scripts/app_server.py — for every page of the app.)
Every 30 s:
  - a worker posted a new open checkpoint or question in any worktree's ORCH-QUESTIONS.md, or a
    worker went from working to idle/done → type a prompt into the orchestrator's pane. Workers
    stop at each checkpoint and wait, so a missed one means idle workers (happened 2026-09-26).
Every --interval seconds (default 5 min):
  - a status snapshot → status.json: each agent's state, each branch's latest commit, commits since
    the last check, open ORCH-QUESTIONS, a one-line heartbeat the page shows in its feed, and each
    agent's tokens and busy time since the hand-over (usage.py, read off the transcripts).
"""
import argparse, json, os, re, subprocess, tempfile, time
from datetime import datetime, timezone
from usage import usage
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app-maker", "scripts"))
from helperlog import log as _hlog          # the helpers' log, shown in the engineering center's Ticker section

APP_DIR = None                               # set in main(); the log lives in the app folder
PROBLEMS = []                                # herdr/git calls that failed or timed out this pass


def hlog(kind, text, ok=True, detail=""):
    if APP_DIR:
        _hlog(APP_DIR, "ticker", kind, text, ok, detail)


def job(status, key, result, ok=True):
    """Record a job's last run and how it went — the Ticker section's "Its jobs" table."""
    status.setdefault("jobs", {})[key] = {"last": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                          "result": result, "ok": ok}


def sh(args, cwd=None):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        PROBLEMS.append(f"{' '.join(args[:4])} — {'timed out' if isinstance(e, subprocess.TimeoutExpired) else 'failed'}")
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


def activity(name):
    """What an agent is doing right now, read off its pane (no model): its latest '⏺' line —
    the sentence it last said about its own work — and whether it has ended its turn only to
    wait on its own background job (a test run or build: "1 shell still running")."""
    raw = sh(["herdr", "agent", "read", name])
    try:
        raw = json.loads(raw)["result"].get("text", raw)
    except (ValueError, KeyError, TypeError, AttributeError):
        pass
    said = [l.strip()[1:].strip() for l in raw.splitlines() if l.strip().startswith("⏺")]
    # keep sentences, drop raw tool calls ("Update(app/main.py)", "Bash(...)") and timings
    said = [re.sub(r"\s·\s\d+[smh]$", "", t) for t in said if not re.match(r"^[A-Z][A-Za-z]*\(", t)]
    text = re.sub(r"\s+", " ", said[-1]) if said else ""
    if len(text) > 170:
        text = text[:167].rsplit(" ", 1)[0] + "…"
    waiting = bool(re.search(r"(shell|monitor)s? still running", raw[-2000:]))
    return {"text": text, "waiting": waiting}


def context_use(name):
    """A worker's context use in percent, read off its Claude status line ("ctx 53%/530k")."""
    raw = sh(["herdr", "agent", "read", name])
    try:                                    # plain text today; JSON if herdr ever wraps it
        text = json.loads(raw)["result"].get("text", raw)
    except (ValueError, KeyError, TypeError, AttributeError):
        text = raw
    found = re.findall(r"ctx (\d+)%/", text)
    return int(found[-1]) if found else None


PRICES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json")))


def usd(r):
    """What an agent's tokens would cost at API prices (prices.json). Cache writes are 1-hour ones."""
    p = PRICES.get((r.get("models") or ["claude-sonnet-5"])[0], PRICES["claude-sonnet-5"])
    return round((r.get("input_tokens", 0) * p["input"] + r.get("output_tokens", 0) * p["output"]
                  + r.get("cache_creation_input_tokens", 0) * p["cache_write_1h"]
                  + r.get("cache_read_input_tokens", 0) * p["cache_read"]) / 1e6, 2)


def plan_usage(names):
    """The user's Claude plan limits, read off a Claude status line: "5h 31%↻19m  wk 5%↻151h18m"."""
    for n in names:
        raw = sh(["herdr", "agent", "read", n])
        try:
            raw = json.loads(raw)["result"].get("text", raw)
        except (ValueError, KeyError, TypeError, AttributeError):
            pass
        m = re.findall(r"5h (\d+)%\S*?(\d+h\d+m|\d+h|\d+m)\s+wk (\d+)%\S*?(\d+h\d+m|\d+h|\d+m)", raw)
        if m:
            f, fr, w, wr = m[-1]
            return {"five_h": int(f), "five_h_reset": fr, "week": int(w), "week_reset": wr,
                    "t": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return None


def build_started(app, room):
    """When the build began: the PRD page's hand-over round (the first round that carries prd_ready).
    Falls back to the engineering center's first post."""
    try:
        for b in json.load(open(os.path.join(app, "spec", "state.json"))).get("batches", []):
            if (b.get("decisions") or {}).get("prd_ready"):
                return b["ts"]
    except (OSError, ValueError, KeyError):
        pass
    try:
        items = json.load(open(os.path.join(room, "feed.json")))["items"]
        return min(i["t"] for i in items) if items else None
    except (OSError, ValueError, KeyError):
        return None


def notify(title, text):
    try:
        from helperlog import muted
        if muted():
            return
    except ImportError:
        pass
    esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
    sh(["osascript", "-e", f'display notification "{esc(text)}" with title "{esc(title)}" sound name "Glass"'])


SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)))
RESTART = os.path.abspath(os.path.join(SCRIPTS, "..", "..", "..", "scripts", "restart-agent.sh"))


def _cwd(name):
    try:
        r = json.loads(sh(["herdr", "agent", "get", name]))["result"]
        return r.get("agent", r).get("cwd", "")
    except (ValueError, KeyError, TypeError):
        return ""


def handovers(x, room, app, workers, status, ag):
    """The context manager (user, 2026-09-27). Sessions are treated like servers: at
    --handover-at the ticker asks an agent to drain (finish, save, write notes, touch a marker,
    stop); once it's ready, idle and — for a worker — clean, it restarts it under the same herdr
    name with a resume prompt, confirms the new session is up, and says so on the page. One
    restart at a time; wake-ups for the orchestrator are held while it restarts. Touching
    <room>/.handover/<name>.request forces a handover (tests, or the user's call)."""
    hdir = os.path.join(room, ".handover")
    os.makedirs(hdir, exist_ok=True)
    ho = status.setdefault("handover", {})
    now = datetime.now(timezone.utc)
    iso = now.isoformat(timespec="seconds")
    post = os.path.join(SCRIPTS, "post.py")
    skill = os.path.dirname(SCRIPTS)
    for w in [x.orchestrator] + workers:
        if w not in ag:
            continue
        orch = w == x.orchestrator
        pct = context_use(w)
        st = ag.get(w)
        marker = os.path.join(hdir, f"{w}.ready")
        request = os.path.join(hdir, f"{w}.request")
        h = ho.get(w)
        notes = "HANDOFF.md" if orch else f"{w}/WORKER-NOTES.md"
        if not h:
            forced = os.path.exists(request)
            if forced or (pct is not None and pct >= x.handover_at):
                if os.path.exists(request):
                    os.remove(request)
                why = "a handover was requested" if forced else f"your context is at {pct}%"
                sh(["herdr", "agent", "prompt", w,
                    f"From the ticker (context manager): {why}. Graceful handover — "
                    + ("finish what you're doing (don't leave a verification or background check running), "
                       "update HANDOFF.md 'Where things stand' with exactly what's in flight (pending checkpoints, "
                       "what each worker is on), commit and push, "
                       if orch else
                       f"finish the smallest safe unit, commit everything, update {notes} with exactly where you "
                       "are and what's next, make sure 'git status' is clean, ")
                    + f"then run: touch {marker} — and stop. The ticker restarts you under the same name with a "
                    + "fresh session that reads your notes" + ("; wake-ups are held until you're back." if orch else ".")])
                ho[w] = {"phase": "asked", "since": iso, "pct": pct}
                hlog("handover", f"Asked {w} to save its work and get a fresh start — "
                     + ("you requested it" if forced else f"its memory was {pct}% full") + ".")
            continue
        if h["phase"] in ("asked", "nudged"):
            if h["phase"] == "asked" and pct is not None and pct >= x.nudge_at:
                sh(["herdr", "agent", "prompt", w, f"Reminder from the ticker: context {pct}% — please hand over "
                    f"at your next safe point (commit, notes, then touch {marker} and stop)."])
                h["phase"] = "nudged"
                hlog("handover", f"Reminded {w} to hand over — its memory is at {pct}%.")
            busy = any(k != w and v.get("phase") == "restarting" for k, v in ho.items())
            clean = orch or not sh(["git", "-C", _cwd(w), "status", "--porcelain"]).strip()
            if os.path.exists(marker) and st in ("idle", "done") and clean and not busy:
                if orch:          # leave the new session a snapshot of the whole build
                    snap = {"t": iso, "agents": dict(ag), "context": status.get("context", {}),
                            "activity": status.get("activity", {}), "open_entries": sorted(open_entries(app)),
                            "branches": branches(app)[:8]}
                    for v in workers:
                        snap.setdefault("ahead_of_main", {})[v] = sh(["git", "-C", app, "rev-list", "--count",
                                                                      f"main..{v}"]).strip()
                    write_json(os.path.join(hdir, "snapshot.json"), snap)
                h.update({"phase": "restarting", "restarted_at": iso})
                write_json(os.path.join(room, "status.json"), status)
                resume = (
                    f"You are {w} for {os.path.basename(app)}, restarted by the ticker at a clean point (a context "
                    f"handover) — nothing is wrong. Read, in order: {skill}/SKILL.md, {app}/HANDOFF.md, "
                    f"{hdir}/snapshot.json. Then check each worker ({', '.join(workers)}): its status (herdr agent get), "
                    f"`git log main..<branch>`, any 'Status: checkpoint' entry in its worktree's ORCH-QUESTIONS.md, and "
                    f"its WORKER-NOTES.md. Verify and merge pending checkpoints, answer open questions, and give any "
                    f"idle worker its next step. Held wake-ups (if any) follow."
                    if orch else
                    f"You are the {w} worker for {os.path.basename(app)}, restarted by the ticker at a clean point (a "
                    f"context handover) — nothing is wrong. Read, in order: {w}/AGENT.md, {notes}, your entries in "
                    f"ORCH-QUESTIONS.md, then git log --oneline -30. Merge main first. Carry on from your notes' 'next'.")
                env = dict(os.environ, HERDR_ENV="1", **({"SKIP_GIT_CHECK": "1"} if orch else {}))
                model = x.orch_model if orch else x.worker_model
                try:
                    r = subprocess.run([RESTART, w, model, x.effort, resume], env=env, capture_output=True,
                                       text=True, timeout=120)
                    if r.returncode == 0:
                        hlog("handover", f"{w} saved its notes — restarted it with a fresh session.", detail=resume)
                    else:
                        # The script refuses to start over a live session (e.g. /exit answered a late background
                        # notification instead of exiting). Never log that as a restart (it was, twice: 2026-09-27/28).
                        h["error"] = (r.stderr or r.stdout or f"exit {r.returncode}").strip()[-200:]
                        hlog("problem", f"Couldn't restart {w}: {h['error']}", ok=False)
                        if not orch:
                            sh(["herdr", "agent", "prompt", x.orchestrator,
                                f"The ticker couldn't restart {w} for its handover: {h['error']}. Its old session may "
                                f"still be open — check with `herdr agent read {w}`, close it, then restart it."])
                except (OSError, subprocess.TimeoutExpired) as e:
                    h["error"] = repr(e)[:200]
                    hlog("problem", f"Couldn't restart {w}: {h['error']}", ok=False)
            continue
        if h["phase"] == "restarting":
            age = (now - datetime.fromisoformat(h["restarted_at"])).total_seconds()
            if pct is not None and pct < 30 and age > 20:          # the fresh session is up
                for f in (marker, request):
                    if os.path.exists(f):
                        os.remove(f)
                ho.pop(w, None)
                hlog("handover", f"{w} is back — memory down from {h.get('pct')}% to {pct}%.")
                held = status.pop("held_wakeups", []) if orch else []
                if held:
                    sh(["herdr", "agent", "prompt", w, "Held while you restarted — " + " || ".join(held)])
                sh(["python3", post, room, "update",
                    f"{'The orchestrator' if orch else 'The ' + ('iPhone app' if w == 'ios' else w) + ' worker'} got a "
                    f"fresh session (context was {h.get('pct')}%) — it saved its work and notes first, and picked up "
                    f"where it left off."])
            elif age > 300:
                h["error"] = "the new session didn't come up within 5 minutes — check the pane"
                hlog("problem", f"{w}'s fresh session didn't start within 5 minutes — check its tab.", ok=False)
                status.setdefault("handover_errors", []).append({"t": iso, "agent": w})
                ho.pop(w, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("room")
    ap.add_argument("--app", required=True)
    ap.add_argument("--orchestrator", default="code-orchestrator")
    ap.add_argument("--workers", default="backend,ios")
    ap.add_argument("--interval", type=int, default=300)
    # context manager (user, 2026-09-27): sessions are treated like servers — graceful drain at
    # --handover-at, a firmer nudge at --nudge-at, restart under the same herdr name
    ap.add_argument("--handover-at", type=int, default=70)
    ap.add_argument("--nudge-at", type=int, default=85)
    ap.add_argument("--orch-model", default="opus")
    ap.add_argument("--worker-model", default="sonnet")
    ap.add_argument("--effort", default="high")
    x = ap.parse_args()
    room, app = os.path.abspath(x.room), os.path.abspath(x.app)
    name = os.path.basename(app)
    global APP_DIR
    APP_DIR = app
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
    status["ticker_started"] = last_iso
    hlog("start", "The ticker started.")

    def wake(msg):
        """Type a prompt into the orchestrator's pane — or hold it while the orchestrator is
        being restarted, so nothing typed into a half-started session is lost."""
        if status.get("handover", {}).get(x.orchestrator, {}).get("phase") == "restarting":
            status.setdefault("held_wakeups", []).append(msg)
            hlog("wake", "Held a wake-up for the orchestrator until it's back from its fresh start.", detail=msg)
        else:
            sh(["herdr", "agent", "prompt", x.orchestrator, msg])

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
                wake(
                    f"The user pressed 'Get me an update' in the engineering center. Post one update now with "
                    f"python3 {post} {room} update \"...\" — plain English, at most 4 short lines: what's done since "
                    f"your last update, what backend and ios are each on, what's next, and anything blocked or "
                    f"waiting on the user (say 'nothing' if nothing). Check git and the workers before you write it.")
                status["update_forwarded"] = ask
                hlog("update", f"You pressed Get me an update → asked {x.orchestrator}.")
                job(status, "update", f"asked {x.orchestrator}")
            else:
                status["update_forwarded"] = "no orchestrator running"
                hlog("problem", "You pressed Get me an update, but the orchestrator isn't running.", ok=False)
                job(status, "update", "the orchestrator isn't running", False)
        # (Sends and new-question notifications are handled by the app's server for every page —
        #  App Maker, 2026-09-26. The ticker keeps the heartbeat, commits, runtime and update requests.)
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
            # context use, shown on the page for everyone (handovers are managed every 30 s below)
            status["context"] = {w: context_use(w) for w in watch if w in ag}
            try:
                status["usage"] = {"t": now_iso, "agents": usage(watch, status.get("build_started"))}
                for r in status["usage"]["agents"].values():
                    r["usd"] = usd(r)
                job(status, "usage", f"read {len(status['usage']['agents'])} sessions")
            except Exception as e:                    # a bad transcript line must not stop the heartbeat
                status["usage_error"] = repr(e)[:200]
                job(status, "usage", "couldn't read a transcript", False)
                hlog("problem", f"Couldn't count tokens: {repr(e)[:160]}", ok=False)
            status.update({"t": now_iso, "interval": x.interval, "agents": {w: ag.get(w, "not running") for w in watch},
                           "branches": branches(app)[:8], "open_questions": oq, "heartbeats": heartbeats})
            last_beat, last_iso = time.time(), now_iso
            status["checks"] = status.get("checks", 0) + 1
            pl = plan_usage([x.orchestrator] + workers)
            if pl:
                status["plan"] = pl
            job(status, "snapshot", "saved")
        if time.time() - last_commits >= 30:          # commits are cheap to read: every 30 s
            before = {h["hash"] for lane in (status.get("commits") or {}).values() for h in lane}
            status["commits"] = commits(app)
            last_commits = time.time()
            new = [h for lane in status["commits"].values() for h in lane if h["hash"] not in before]
            job(status, "commits", f"{len(new)} new commit{'s' if len(new) != 1 else ''}" if before else "read")
            # what each agent is doing right now, for the page (no model, no tokens)
            status["activity"] = {w: activity(w) for w in [x.orchestrator] + workers if w in agents()}
            handovers(x, room, app, workers, status, agents())
            cx = {w: context_use(w) for w in [x.orchestrator] + workers if w in agents()}
            hot = [f"{w} at {p}%" for w, p in cx.items() if p is not None and p >= x.handover_at - 10]
            job(status, "memory", ("; ".join(hot) + " — fresh start soon") if hot else
                " · ".join(f"{w} {p}%" for w, p in cx.items() if p is not None) or "no readings", not hot)
            # 4. worker events → wake the orchestrator
            events = []
            for title in sorted(open_entries(app) - seen_entries):
                seen_entries.add(title)
                events.append(f"a worker posted in ORCH-QUESTIONS.md: \"{title}\"")
            ag = agents()
            for w in workers:
                st = ag.get(w)
                if last_states.get(w) == "working" and st in ("idle", "done"):
                    # a worker that ended its turn to wait on its own background job ("1 monitor
                    # still running") will be woken by that job — not a stop worth waking for
                    waiting = re.search(r"(shell|monitor)s? still running", sh(["herdr", "agent", "read", w])[-2000:])
                    if not waiting:
                        events.append(f"{w} stopped working (now {st}) — at a checkpoint, finished, or blocked")
                if st:
                    last_states[w] = st
            job(status, "watch", f"{len(events)} event{'s' if len(events) != 1 else ''}" if events else "nothing new")
            for e in events:
                hlog("wake", f"Woke {x.orchestrator} — {e}.")
            if events and x.orchestrator in ag:
                wake(
                    "Worker event: " + "; ".join(events) + ". Read the worker's ORCH-QUESTIONS.md in its "
                    "worktree and its pane (herdr agent read <name>); a checkpoint means verify, then "
                    "merge and post it — the worker waits until you answer.")
        if not status.get("build_started"):
            status["build_started"] = build_started(app, room)
        status["seen_asks"] = sorted(seen_asks)
        status["seen_entries"] = sorted(seen_entries)
        for p in sorted(set(PROBLEMS)):
            hlog("problem", f"A check didn't answer in time ({p}) — it'll try again on the next pass.", ok=False)
        PROBLEMS.clear()
        status["alive"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        write_json(status_path, status)
        time.sleep(10)


if __name__ == "__main__":
    main()
