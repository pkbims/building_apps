#!/usr/bin/env python3
"""What happened in a time window, across every Claude Code agent and repo.

    python3 hour.py                    # last 60 minutes
    python3 hour.py 90                 # last 90 minutes
    python3 hour.py 14:30 16:15        # today, 14:30 to 16:15 (local time)

Reads the session logs every Claude Code agent writes to ~/.claude/projects/ (one
.jsonl per session, every line timestamped), plus git commits in the repos those
agents worked in. Produces a digest: per agent, what you asked, what it said back,
which files it wrote, and what it committed. The recap is written from that.

The logs are local files, so this sees every agent regardless of which terminal,
herdr pane or worktree it runs in. It does not see work done outside Claude Code
(e.g. tapping through the app on a phone); git commits cover some of that.

Filtering is by each line's own timestamp, not the file's modified time — resuming
an old session touches its file without adding work to the window.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
HARNESS = ("<command-", "<local-command", "<system-reminder", "<task-notification", "<user-prompt")
CLIP = 400  # characters kept per message; the digest is for summarising, not reading


def clip(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= CLIP else text[:CLIP] + " …"


def when(entry: dict):
    ts = entry.get("timestamp")
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def read_session(path: Path, since: datetime, until: datetime) -> dict | None:
    asked, said, files, urls, cwd = [], [], set(), set(), None
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = when(e)
        if t is None or t < since or t > until or e.get("isSidechain"):
            continue
        cwd = e.get("cwd") or cwd
        content = (e.get("message") or {}).get("content")
        if e.get("type") == "system" and e.get("subtype") == "away_summary" and e.get("content"):
            # Claude Code's own one-paragraph "where this agent is" note — the best single line.
            said.append("(agent summary) " + clip(e["content"]))
        elif e.get("type") == "user" and isinstance(content, str) and not e.get("isMeta"):
            # Drop harness-injected lines (command output, reminders, task events); keep what
            # a person typed, including text they pasted in (unwrapped from its tags).
            if not content.lstrip().startswith(HARNESS):
                asked.append(clip(re.sub(r"</?pasted_content[^>]*>", " ", content)))
        elif e.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if b.get("type") == "text" and b.get("text", "").strip():
                    said.append(clip(b["text"]))
                    # Pages the agent served, from its full text (clip() would cut most of them off).
                    urls.update(re.findall(r"https?://localhost:\d+/?[\w./-]*", b["text"]))
                elif b.get("type") == "tool_use" and b.get("name") in WRITE_TOOLS:
                    fp = (b.get("input") or {}).get("file_path")
                    if fp:
                        files.add(fp)
    if not (asked or said or files):
        return None
    urls = {u.rstrip("/.") for u in urls}
    # The last replies are usually the agent's own account of where it got to.
    return {"cwd": cwd, "asked": asked, "said": said[-3:], "files": sorted(files), "urls": sorted(urls)}


def first_activity(since: datetime, until: datetime) -> datetime | None:
    """When work actually began in the window: the earliest user or agent line in any log."""
    best = None
    for p in PROJECTS.glob("*/*.jsonl"):
        if p.stat().st_mtime < since.timestamp():
            continue
        for line in p.open(encoding="utf-8", errors="replace"):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") not in ("user", "assistant") or e.get("isSidechain"):
                continue
            t = when(e)
            if t and since <= t <= until and (best is None or t < best):
                best = t
    return best


def commits(repo: str, since: datetime, until: datetime) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", repo, "log", f"--since={since.isoformat()}", f"--until={until.isoformat()}", "--pretty=%h %s"],
            capture_output=True, text=True, timeout=10,
        )
        return out.stdout.split("\n")[:-1] if out.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired):
        return []


def in_apps(cwd: str | None, apps: list[str]) -> bool:
    """Does an agent's folder belong to one of these apps? Covers the app folder itself and
    herdr worktrees, which are named like app-1-backend. practice_N was app_N until 2026-09-24,
    so its older logs and its herdr worktrees still carry the app_N name."""
    apps = apps + [re.sub(r"^practice_", "app_", a) for a in apps if a.startswith("practice_")]
    return bool(cwd) and any(re.search(rf"(^|[/_-]){re.escape(a)}([/_-]|$)", cwd) or
                             re.search(rf"(^|[/_-]){re.escape(a.replace('_', '-'))}([/_-]|$)", cwd) for a in apps)


def digest(since: datetime, until: datetime, apps: list[str] | None = None) -> str:
    # A file last written before the window can't hold lines inside it.
    recent = [p for p in PROJECTS.glob("*/*.jsonl") if p.stat().st_mtime >= since.timestamp()]
    sessions = [s for s in (read_session(p, since, until) for p in recent) if s]
    total = len(sessions)
    if apps:  # a focus prompt named apps: drop agents that worked elsewhere before Claude sees them
        sessions = [s for s in sessions if in_apps(s["cwd"], apps)]
    fmt = lambda d: d.astimezone().strftime("%H:%M")
    kept = f" (focus: kept {len(sessions)} of {total}, working in {', '.join(apps)})" if apps else ""
    out = [f"# {fmt(since)}–{fmt(until)} — {len(sessions)} agent sessions{kept}", ""]
    repos = set()
    for i, s in enumerate(sorted(sessions, key=lambda s: s["cwd"] or ""), 1):
        out.append(f"## Agent {i} — {s['cwd']}")
        repos.add(s["cwd"])
        out += [f"- asked: {a}" for a in s["asked"]]
        # A file written then deleted in the same window can't be shown on camera.
        out += [f"- wrote: {f}" + ("" if Path(f).exists() else " (since deleted)") for f in s["files"]]
        out += [f"- served page: {u}" for u in s["urls"]]
        out += [f"- said: {r}" for r in s["said"]]
        out.append("")
    out.append("## Commits")
    for repo in sorted(r for r in repos if r):
        out += [f"- {Path(repo).name}: {c}" for c in commits(repo, since, until)]
    return "\n".join(out)


def _today_at(hhmm: str) -> datetime:
    h, m = map(int, hhmm.split(":"))
    return datetime.now().astimezone().replace(hour=h, minute=m, second=0, microsecond=0)


if __name__ == "__main__":
    args = sys.argv[1:]
    now = datetime.now(timezone.utc)
    if len(args) == 2:
        print(digest(_today_at(args[0]), _today_at(args[1])))
    else:
        print(digest(now - timedelta(minutes=int(args[0]) if args else 60), now))
