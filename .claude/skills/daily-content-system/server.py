#!/usr/bin/env python3
"""Daily content page: one page for the whole series, one day.json per series day.

    cd building_apps && python3 .claude/skills/daily-content-system/server.py

Serves page.html (the day) and review.html (one draft under review), and keeps every day
in content/day-NN/day.json. Every chunk goes prompt → draft → review → approved:

  recap    a time window of every agent's work, optionally narrowed by a focus prompt
  chunk    past work: a prompt, no window. An "outline" item proposes the chunks first;
           approving it creates one chunk item per outline entry
  intro    written from the day's approved chunks, played first
  outro    likewise, played last

Drafts are written, and revised from review comments, by Claude in the background
(`claude -p`, no saved session, so it never shows up in the next recap's digest).
Recaps and bookends get no tools; past-work outlines and chunks get read-only
Read/Grep/Glob so they can dig through old logs and the app's files.

Recap windows never overlap: each one starts exactly where the previous one ended.
"""
from __future__ import annotations

import difflib
import http.server
import json
import os
import re
import shutil
import socket
import socketserver
import subprocess
import sys
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hour  # noqa: E402

CONTENT = Path(os.environ.get("CONTENT", Path.cwd() / "content")).resolve()
ROOT = Path(os.environ.get("SERIES_ROOT", CONTENT.parent)).resolve()  # the series folder: app_N repos live here
PORT_FILE = CONTENT / ".port"
START_PORT = int(os.environ.get("PORT", "7790"))
PINNED = "PORT" in os.environ
MODEL = os.environ.get("RECAP_MODEL", "opus")  # the user chose Opus at high effort for script quality
EFFORT = os.environ.get("RECAP_EFFORT", "high")
RECAP_MINUTES = 60  # a split recap covers this much time each
TARGET_WORDS = 250  # ~2 minutes spoken: the user chose a fixed length (review D7)
LOCK = threading.Lock()  # every read-modify-write of a day.json goes through this
VIDEO_KINDS = ("intro", "recap", "chunk", "outro")  # "outline" is a planning item, never filmed


# ---- prompts ------------------------------------------------------------------------

DRAFT_SHAPE = """Return ONLY JSON, no prose, shaped exactly:
{"title":"<max 5 words>",
 "summary":"<5-8 sentences: what happened, as a story, so the creator understands it before filming>",
 "open":[{"what":"<thing to have open, max 6 words>","where":"<URL, file path, or command>"}],
 "lines":[{"act":"<what is on screen for this beat, max 10 words, e.g. 'localhost:7790, the + panel' or 'camera'>",
           "say":"<the exact words to say, 1-3 spoken sentences>"}]}"""

SCRIPT_RULES = f"""The script ("lines") is a proper script: the EXACT words the creator will say on camera,
cut into beats. They read it while clicking through their screen, so:
- 5-9 beats, {TARGET_WORDS - 30}-{TARGET_WORDS + 20} words in total (~2 minutes spoken). Count them: more
  than {TARGET_WORDS + 20} runs long on camera, so cut detail rather than squeeze it in.
- Each beat: one screen action ("act") and the words said while it is on screen ("say").
- Write it the way the creator actually talks. VOICE SAMPLE below is a transcript of them
  speaking: copy their rhythm, openers ("Hey folks", "so", "okay so"), sentence length and
  plainness. Spoken English, contractions, no written-essay phrasing, no hype, no emoji.
- Put transitions in the words ("Now let me show you...", "And this is where it got
  interesting...") so the creator never has to think how to move on.
- Say why, not just what: the decision and what it cost.
- Tell it for a VIEWER: what was built, what it does now, the decisions and results. Leave
  out tooling hiccups (a failed edit, a restart, a typecheck, a retry) unless they changed a
  decision. Say "Claude" or "my agent", never "agent 3".
- "act" is one concrete thing the creator can put on screen: a localhost URL, a file, the
  terminal running a command, or "camera". Never hedge ("or skip"), never describe an idea.
- Facts must come from the input. Never state a port, URL, file or number that isn't in it;
  a localhost URL must come from a "served page" line. When unsure, leave the detail out.
- Never invent work that is not in the input."""

OPEN_RULES = """"open": every distinct artifact the script shows, in order, each with an exact location from
the input. Prefer a "served page" localhost URL over the HTML file behind it. Never list a
file marked "(since deleted)". No duplicates. 0-6 items."""

RECAP_PROMPT = f"""You write a recap for a creator filming a ~2 minute screen recording about the work
they did in a time window, clicking through it while talking. The input is a digest of every
AI coding agent's activity in the window, plus an optional FOCUS.

{DRAFT_SHAPE}

If FOCUS is given, cover ONLY work that matches it and ignore the rest of the digest, even if
it's most of the hour. If nothing matches, say so plainly in 2 beats.

{SCRIPT_RULES}
- Beat 1 opens with the span, in the creator's words (e.g. "Hey folks, so this past hour I...").
  No day intro and no outro: those are separate recordings.
- The last beat says what's next.

{OPEN_RULES}

Summary: first person, concrete (pages, files, tools, numbers), including what didn't work."""

BOOKEND_PROMPT = """You write the {kind} for a creator's daily video, filmed face to camera at the end of the
day after all the chunks. The input is every approved chunk of the day.

""" + DRAFT_SHAPE.replace("{", "{{").replace("}", "}}") + """

{rules}

""" + SCRIPT_RULES.replace("{", "{{").replace("}", "}}") + """
- 3-6 beats, about 120-160 words: the {kind} is short. Most beats are "camera".
"open" is usually empty. If you list anything, copy its location exactly from a chunk's
"Shown" list; never build or guess a path."""

INTRO_RULES = """This is the INTRO, played first:
- Beat 1 is a hook: the most surprising or useful thing that happened today.
- Then which day of the challenge it is ("{day}"), and the challenge (10 apps in 30 days).
- Then what they worked on today, and what the viewer will see in this video, in order.
- End with a reason to keep watching."""

OUTRO_RULES = """This is the OUTRO, played last:
- The biggest lesson of the whole day, and why it matters to someone building their own apps.
- Where things stand now, honestly.
- Tomorrow: what comes next.
- A call to action: the free community, where the full process is shared every day.
- A short sign-off."""

OUTLINE_PROMPT = """You plan a set of short videos ("chunks") about work a creator finished in the past. They
film each chunk as a ~2 minute screen recording, clicking through the work while talking.

You have read-only tools (Read, Grep, Glob). Use them: the input gives a git history and an
index of past AI-agent sessions (with their log files under ~/.claude/projects). Grep the logs
and read the app's files to find what was actually built, when, why, and what it looks like now.

Return ONLY JSON, no prose, shaped exactly:
{"title":"<max 6 words, the series of chunks>",
 "summary":"<4-6 sentences: what you found, and how the chunks tell it>",
 "chunks":[{"title":"<max 6 words>","covers":"<2-3 sentences: what this chunk shows and why it matters>",
            "show":"<the pages, files or screens to click through>",
            "sources":"<where you found it: log files, commits, paths>"}]}

2-6 chunks, in the order a viewer should watch them. Each chunk is one recording. Only work
you actually found evidence for."""

CHUNK_PROMPT = f"""You write one chunk: a ~2 minute screen recording about past work, which the creator
clicks through while talking. The input is the chunk's plan (from an approved outline) and the
whole outline for context. You have read-only tools (Read, Grep, Glob): check the sources and
the files so the script is accurate and every location in "open" is real.

{DRAFT_SHAPE}

{SCRIPT_RULES}
- Beat 1 says what this chunk is about, in the creator's words. No day intro, no outro.

{OPEN_RULES}"""

REVISE_PROMPT = """You revise a draft the creator reviewed. The input is the current draft (JSON) and their
comments. Each comment has a kind:
- change: do what it asks, in the part it points at (a beat number, the summary, the open list,
  or a chunk number).
- question: answer it briefly and plainly. Do NOT change the draft because of a question.
- note: context to take on board; change the draft only if it clearly calls for it.
Keep everything that no comment touched exactly as it was.

You also get EARLIER ROUNDS (the creator's past comments and your past answers) so you don't
undo a change they already asked for or repeat an answer, and the SOURCE the draft was written
from (the agents' logs, or the day's chunks, or the outline plan). Check facts against the
SOURCE: when a comment asks for a fact, or when answering a question, use what the source
says, and say so if it isn't there. If you have read-only tools, you may also read files
to check. Never invent a fact to satisfy a comment.

Return ONLY JSON, no prose, shaped exactly:
{"draft": <the full revised draft, same shape as the input draft>,
 "answers": [{"id":"<comment id>","answer":"<your reply>"}],
 "changed": ["<what changed: 'beat 3', 'summary', 'open', 'chunk 2', ...>"]}
Every comment gets an entry in "answers" (for a change, say in a few words what you did)."""


# ---- storage ------------------------------------------------------------------------

def day_path(day: str) -> Path:
    if not re.fullmatch(r"day-\d{2,3}", day):
        raise ValueError(f"bad day id {day!r}")
    return CONTENT / day / "day.json"


def load(day: str) -> dict:
    return json.loads(day_path(day).read_text())


def save(day: str, data: dict) -> None:
    p = day_path(day)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(p)  # atomic, so a crash mid-write never leaves half a file


def days() -> list[str]:
    return sorted(p.parent.name for p in CONTENT.glob("day-*/day.json"))


def kind_of(r: dict) -> str:
    return r.get("kind", "recap")


def item(d: dict, n: int) -> dict:
    x = next((x for x in d["recaps"] if x["n"] == n), None)
    if x is None:  # a bare StopIteration used to reach the page as an empty error
        raise ValueError("that chunk no longer exists (it may have been deleted)")
    return x


def update_item(day: str, n: int, **fields) -> None:
    with LOCK:
        d = load(day)
        x = next((r for r in d["recaps"] if r["n"] == n), None)
        if x is None:  # deleted while Claude was writing it: drop the result
            return
        x.update(fields)
        save(day, d)


def file_for(d: dict, r: dict) -> str:
    """A new item's recording name. It's stored on the item and never recomputed, so deleting
    an earlier chunk can't make a later one point at someone else's video."""
    k = kind_of(r)
    if k in ("intro", "outro"):
        return f"{k}.mp4"
    prefix = "hour" if k == "recap" else "chunk"
    used = {x.get("file") for x in d["recaps"]}
    i = sum(1 for x in d["recaps"] if kind_of(x) == k and x is not r) + 1
    while f"{prefix}-{i:02d}.mp4" in used:
        i += 1
    return f"{prefix}-{i:02d}.mp4"


def video_of(day: str, d: dict, r: dict) -> Path | None:
    if kind_of(r) not in VIDEO_KINDS:
        return None
    return CONTENT / day / "hours" / (r.get("file") or file_for(d, r))


CHANNELS = ["instagram", "tiktok", "x", "youtube", "threads"]
LABELS = {"instagram": "Instagram", "tiktok": "TikTok", "x": "X", "youtube": "YouTube Shorts", "threads": "Threads"}
CHECKS = {"plan", "gear", "approved", "skool"} | {f"short_{c}" for c in CHANNELS}


def progress(day: str, d: dict) -> list[dict]:
    """The day's steps in order, each auto-detected from files where possible, else a tick.

    Everything is derived on read, never stored, so it can't drift from what's on disk."""
    ck, items = d.get("checks", {}), d.get("recaps", [])
    book = {kind_of(r): r for r in items if kind_of(r) in ("intro", "outro")}
    body = [r for r in items if kind_of(r) in ("recap", "chunk")]
    ok = sum(1 for r in body if r.get("status") == "approved")
    rec = sum(1 for r in body if r.get("recorded"))
    later = any(load(x)["date"] > d["date"] for x in days() if x != day)
    long_out = CONTENT / day / "out" / f"{day}-long.mp4"
    posted = [c for c in CHANNELS if ck.get(f"short_{c}")]
    step = lambda group, key, label, done, how, detail="", tick=None: {
        "group": group, "key": key, "label": label, "done": done, "how": how, "detail": detail, "tick": tick}

    def bookend(k):
        r = book.get(k)
        if not r:
            return f"Press + → {k.capitalize()}, after your last chunk"
        if r.get("recorded"):
            return "Recorded"
        return "Approved, not recorded yet" if r.get("status") == "approved" else "Draft: review and approve it"

    return [
        step("Morning", "day", "Create the day", bool(d.get("subtitle")), "auto",
             "" if d.get("subtitle") else "Add today's focus under the title"),
        step("Morning", "plan", "Plan the day", bool(ck.get("plan")), "tick",
             "Know what you're building today", tick="plan"),
        step("Morning", "gear", "Gear check", bool(ck.get("gear")), "tick",
             "iPhone, mic, light, Do Not Disturb, Screen Studio", tick="gear"),
        step("During the day", "recaps", "Recaps and chunks", bool(body) and rec == len(body), "auto",
             f"{len(body)} chunk{'s' if len(body) != 1 else ''} · {ok} approved · {rec} recorded" if body
             else "Press + after your first hour"),
        *[step("End of day", k, f"Record the {k}", bool(book.get(k, {}).get("recorded")), "auto", bookend(k))
          for k in ("intro", "outro")],
        step("End of day", "edit", "Edit the long video", long_out.exists(), "auto",
             "Rendered" if long_out.exists() else "Say “edit " + day + "”"),
        step("End of day", "approved", "Watch and approve", bool(ck.get("approved")), "tick", tick="approved"),
        step("End of day", "skool", "Post the long video to Skool", bool(ck.get("skool")), "tick", tick="skool"),
        step("End of day", "short", "Post the short", len(posted) == len(CHANNELS), "ticks",
             f"{len(posted)} of {len(CHANNELS)} channels",
             tick=[{"key": f"short_{c}", "label": LABELS[c], "done": c in posted} for c in CHANNELS]),
        step("Wrap-up", "tomorrow", "Set up tomorrow", later, "auto",
             "Tomorrow's page exists" if later else "Press “+ New day”"),
    ]


def live(where: str) -> bool | None:
    """Is a localhost page in a checklist still being served? None when it isn't a local URL."""
    m = re.search(r"localhost:(\d+)", where)
    return in_use(int(m.group(1))) if m else None


def normalise(d: dict) -> dict:
    # Before reviews existed a finished draft was "ready"; those were final, so they count as approved.
    for r in d.get("recaps", []):
        if r.get("status") == "ready":
            r["status"] = "approved"
    # Items from before file names were stored: pin the name they had by position, in order.
    for k in ("recap", "chunk"):
        for i, r in enumerate([x for x in d.get("recaps", []) if kind_of(x) == k], 1):
            r.setdefault("file", f"{'hour' if k == 'recap' else 'chunk'}-{i:02d}.mp4")
    for r in d.get("recaps", []):
        if kind_of(r) in ("intro", "outro"):
            r.setdefault("file", f"{kind_of(r)}.mp4")
    return d


def view(day: str) -> dict:
    d = normalise(load(day))
    for r in d.get("recaps", []):
        for o in r.get("open", []):
            o["live"] = live(o.get("where", ""))
        v = video_of(day, d, r)
        r["recorded"] = bool(v and v.exists())
        r["video"] = (str(v.relative_to(ROOT)) if v.is_relative_to(ROOT) else str(v)) if v else ""
        r["words"] = sum(len(l.get("say", "").split()) for l in r.get("lines", []))
    return {"days": days(), "day": d, "progress": progress(day, d), "now": now_iso()}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ---- context for the prompts ----------------------------------------------------------

def voice_sample(limit: int = 1800) -> str:
    """How the creator actually talks: their own recordings, transcribed by whisper."""
    parts = []
    for f in sorted(CONTENT.glob("day-*/hours/*.captions.json"))[:3]:
        try:
            parts.append("".join(c["text"] for c in json.loads(f.read_text()))[:limit // 2])
        except (OSError, ValueError, KeyError):
            continue
    return "\n...\n".join(parts)[:limit] or "(no recordings yet: write plainly and casually, first person)"


NAMES_FILE = CONTENT / "app-names.json"  # {"practice_1": ["DesignMyRoom", "decorMyRoom"]}: nicknames, editable


def app_folders() -> dict[str, set[str]]:
    """app_N → what the user might call it: the folder, the first heading of its CLAUDE.md or
    PRD.md (e.g. "Earn your scrolling"), and nicknames from content/app-names.json."""
    try:
        extra = json.loads(NAMES_FILE.read_text())
    except (OSError, ValueError):
        extra = {}
    out = {}
    for d in sorted([*ROOT.glob("app_*"), *ROOT.glob("practice_*")]):
        names = {d.name, d.name.replace("_", " ")} | set(extra.get(d.name, []))
        for f in ("CLAUDE.md", "PRD.md"):
            try:
                head = next(l for l in (d / f).read_text().splitlines() if l.startswith("#"))
            except (OSError, StopIteration):
                continue
            title = re.sub(r"^#+\s*((app|practice)_\d+\s*[—–-]\s*)?", "", head).strip(" \"'“”")
            if title:
                names.add(title)
        out[d.name] = {squash(n) for n in names if squash(n)}
    return out


def squash(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def focus_apps(focus: str) -> list[str]:
    """The apps a focus prompt names ("only the decorMyRoom work" → practice_1), used to pre-filter
    the digest. Matches whole names, also run together or split, and near-misses on long
    names (decorMyRoom vs DesignMyRoom), since the user speaks these prompts."""
    words = re.findall(r"[a-z0-9]+", focus.lower())
    # Every run of 1-4 consecutive words, squashed: "design my room" → "designmyroom".
    grams = {"".join(words[i:j]) for i in range(len(words)) for j in range(i + 1, min(i + 5, len(words) + 1))}
    hits = []
    for app, names in app_folders().items():
        for n in names:
            exact = n in grams
            near = len(n) >= 8 and any(len(g) >= 8 and difflib.SequenceMatcher(None, n, g).ratio() >= 0.8 for g in grams)
            if exact or near:
                hits.append(app)
                break
    return hits


def past_context(prompt: str) -> str:
    """Where to dig: recent git history of the apps the prompt names (or all), and an index of
    past agent sessions. The model greps the logs and reads the files itself."""
    apps = focus_apps(prompt) or [d.name for d in sorted([*ROOT.glob("app_*"), *ROOT.glob("practice_*")])]
    out = ["# Git history (last 90 days)"]
    for app in apps:
        log = subprocess.run(["git", "-C", str(ROOT / app), "log", "--since=90 days ago", "--date=short",
                              "--pretty=%h %ad %s", "-n", "150"], capture_output=True, text=True).stdout
        out.append(f"## {app}\n{log.strip() or '(no commits)'}")
    out.append("\n# Past agent sessions (log file · working folder · dates · first request)")
    rows = []
    for p in hour.PROJECTS.glob("*/*.jsonl"):
        cwd, first_ts, last_ts, asked = None, None, None, None
        try:
            for line in p.open(encoding="utf-8", errors="replace"):
                e = json.loads(line)
                t = e.get("timestamp")
                if t:
                    first_ts = first_ts or t
                    last_ts = t
                cwd = cwd or e.get("cwd")
                c = (e.get("message") or {}).get("content")
                if not asked and e.get("type") == "user" and isinstance(c, str) and not c.lstrip().startswith(hour.HARNESS):
                    asked = " ".join(c.split())[:160]
        except (OSError, ValueError):
            continue
        if cwd and any(a in cwd or a.replace("_", "-") in cwd for a in apps):
            rows.append((last_ts or "", f"- {p} · {cwd} · {(first_ts or '')[:10]}→{(last_ts or '')[:10]} · {asked or ''}"))
    out += [r for _, r in sorted(rows, reverse=True)[:80]]
    out.append(f"\n# App folders\n" + "\n".join(str(ROOT / a) for a in apps))
    return "\n".join(out)


def draft_text(r: dict) -> str:
    lines = "\n".join(f"  beat {i}: [{l.get('act', '')}] {l.get('say', '')}" for i, l in enumerate(r.get("lines", []), 1))
    opened = "\n".join(f"  - {o['what']}: {o['where']}" for o in r.get("open", []))
    return f"{r.get('summary', '')}\nScript:\n{lines}\nShown (exact locations):\n{opened or '  (none)'}"


def day_story(d: dict) -> str:
    """Every approved recap and chunk of the day, as the input for the intro and the outro."""
    out = [f"## {kind_of(r).capitalize()} · {r.get('title', '')}\n{draft_text(r)}" for r in d.get("recaps", [])
           if kind_of(r) in ("recap", "chunk") and r.get("status") in ("approved", "ready")]
    return "\n\n".join(out) or "(no approved chunks yet)"


# ---- claude -------------------------------------------------------------------------

READ_ONLY = ["--tools", "Read,Grep,Glob", "--allowedTools", "Read", "Grep", "Glob",
             "--disallowedTools", "Write", "Edit", "NotebookEdit", "Bash", "--add-dir", str(hour.PROJECTS)]


def ask_claude(system: str, user: str, dig: bool = False) -> dict:
    tools = READ_ONLY if dig else ["--tools", ""]
    out = subprocess.run(
        ["claude", "-p", "--no-session-persistence", *tools, "--model", MODEL, "--effort", EFFORT,
         "--output-format", "json", "--system-prompt", system],
        input=user, capture_output=True, text=True, timeout=900 if dig else 480,  # Opus at high effort is slower
        cwd=str(ROOT if dig else CONTENT),
    )
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout).strip()[:500] or f"claude exited {out.returncode}")
    text = json.loads(out.stdout).get("result", "")
    # Models sometimes wrap JSON in a fence or a sentence; take the outermost object.
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise RuntimeError(f"no JSON in reply: {text[:200]}")
    return json.loads(text[start:end + 1])


def clean_lines(lines: list) -> list:
    # The model sometimes echoes the field's label into the value ("SHOW: the page").
    return [{"act": re.sub(r"^(show\s*[:·—-]\s*)+", "", str(l.get("act", "")), flags=re.I).strip() or "camera",
             "say": str(l.get("say", "")).strip()} for l in lines if l.get("say")]


def draft_fields(got: dict) -> dict:
    return {"title": got.get("title", ""), "summary": got.get("summary", ""),
            "open": got.get("open", []), "lines": clean_lines(got.get("lines", []))}


def write_draft(day: str, n: int) -> None:
    """First draft of any item, in the background. Ends in status "draft" (or "error")."""
    with LOCK:
        d = load(day)
        r = dict(item(d, n))
    k = kind_of(r)
    try:
        head = f"DAY: {d.get('title')} — {d.get('subtitle', '')}\n\nVOICE SAMPLE:\n{voice_sample()}\n\n"
        if k == "recap":
            apps = focus_apps(r.get("focus", ""))
            dig = hour.digest(datetime.fromisoformat(r["from"]), datetime.fromisoformat(r["to"]), apps=apps)
            got = ask_claude(RECAP_PROMPT, head + f"FOCUS: {r.get('focus') or '(none: cover everything)'}\n\nDIGEST:\n{dig}")
            fields = draft_fields(got)
        elif k in ("intro", "outro"):
            dig = day_story(d)
            rules = (INTRO_RULES if k == "intro" else OUTRO_RULES).format(day=d.get("title", day))
            got = ask_claude(BOOKEND_PROMPT.format(kind=k, rules=rules), head + f"TODAY'S CHUNKS:\n{dig}")
            fields = draft_fields(got)
        elif k == "outline":
            dig = past_context(r["focus"])
            got = ask_claude(OUTLINE_PROMPT, f"REQUEST: {r['focus']}\n\n{dig}", dig=True)
            fields = {"title": got.get("title", ""), "summary": got.get("summary", ""), "chunks": got.get("chunks", [])}
        else:  # chunk, from an approved outline
            dig = f"THIS CHUNK:\n{json.dumps(r['plan'], ensure_ascii=False)}\n\nWHOLE OUTLINE:\n{r.get('outline_text', '')}"
            got = ask_claude(CHUNK_PROMPT, head + dig, dig=True)
            fields = draft_fields(got)
        update_item(day, n, **fields, digest=dig, status="draft", error="", round=1)
    except Exception as e:  # the tab shows the error and a retry button; nothing else breaks
        update_item(day, n, status="error", error=str(e)[:500])


def revise(day: str, n: int) -> None:
    """Send the queued review comments to Claude and apply the revision."""
    with LOCK:
        d = load(day)
        r = dict(item(d, n))
    sent = [c for c in r.get("comments", []) if c.get("status") == "sending"]
    if not any(x["n"] == n for x in load(day)["recaps"]):
        return
    k = kind_of(r)
    keys = ("title", "summary", "chunks") if k == "outline" else ("title", "summary", "open", "lines")
    current = {key: r.get(key) for key in keys}
    try:
        earlier = [{"round": c.get("round"), "kind": c["kind"], "target": c["target"], "text": c["text"],
                    "your answer": c.get("answer", "")} for c in r.get("comments", []) if c.get("status") == "sent"]
        got = ask_claude(REVISE_PROMPT, "CURRENT DRAFT:\n" + json.dumps(current, ensure_ascii=False, indent=1)
                         + "\n\nEARLIER ROUNDS:\n" + (json.dumps(earlier, ensure_ascii=False, indent=1) if earlier else "(none)")
                         + "\n\nSOURCE (what the draft was written from):\n" + (r.get("digest") or "(none)")[:40000]
                         + "\n\nVOICE SAMPLE (keep this voice):\n" + voice_sample(900)
                         + "\n\nCOMMENTS:\n" + json.dumps([{k2: c[k2] for k2 in ("id", "kind", "target", "text")} for c in sent],
                                                          ensure_ascii=False, indent=1),
                         # past-work drafts could read files when written, so they can when revised
                         dig=k in ("outline", "chunk"))
        draft = got.get("draft") or {}
        answers = {a.get("id"): a.get("answer", "") for a in got.get("answers", [])}
        with LOCK:
            d = load(day)
            x = next((r for r in d["recaps"] if r["n"] == n), None)
            if x is None:  # deleted mid-revision
                return
            for key in keys:
                if key in draft:
                    x[key] = clean_lines(draft[key]) if key == "lines" else draft[key]
            for c in x.get("comments", []):
                if c.get("status") == "sending":
                    c.update(status="sent", answer=answers.get(c["id"], ""), round=x.get("round", 1))
            x.update(status="draft", round=x.get("round", 1) + 1, changed=got.get("changed", []), error="")
            save(day, d)
    except Exception as e:
        with LOCK:
            d = load(day)
            x = next((r for r in d["recaps"] if r["n"] == n), None)
            if x is None:  # deleted mid-revision
                return
            for c in x.get("comments", []):
                if c.get("status") == "sending":
                    c["status"] = "queued"  # nothing lost: they can be sent again
            x.update(status="draft", error=f"revision failed: {str(e)[:400]}")
            save(day, d)


def next_n(items: list) -> int:
    return max((x["n"] for x in items), default=0) + 1


def blank(n: int, kind: str, **more) -> dict:
    return {"n": n, "kind": kind, "file": "", "title": "", "summary": "", "open": [], "lines": [], "digest": "",
            "status": "writing", "error": "", "comments": [], "round": 0, **more}


def spawn(fn, *args) -> None:
    threading.Thread(target=fn, args=args, daemon=True).start()


def add_recaps(day: str, until: str | None, split: bool, focus: str = "") -> list[int]:
    with LOCK:
        d = load(day)
        items = d.setdefault("recaps", [])
        recaps = [r for r in items if kind_of(r) == "recap"]
        start = datetime.fromisoformat(recaps[-1]["to"] if recaps else d["start"])
        end = datetime.fromisoformat(until) if until else datetime.now(timezone.utc).astimezone()
        if not recaps:
            # A day starts at midnight; the first recap starts when work actually began.
            began = hour.first_activity(start, end)
            if began:
                start = began.astimezone().replace(second=0, microsecond=0)
        if end <= start:
            raise ValueError("the end time must be after the last recap")
        windows, t = [], start
        step = timedelta(minutes=RECAP_MINUTES)
        while split and end - t > step * 1.25:  # a short tail joins the last window
            windows.append((t, t + step))
            t += step
        windows.append((t, end))
        made = []
        for a, b in windows:
            n = next_n(items)
            r = blank(n, "recap", focus=focus.strip(),
                      **{"from": a.isoformat(timespec="seconds"), "to": b.isoformat(timespec="seconds")})
            items.append(r)
            r["file"] = file_for(d, r)
            made.append(n)
        save(day, d)
    for n in made:
        spawn(write_draft, day, n)
    return made


def add_bookend(day: str, kind: str) -> int:
    """The intro or outro: one per day, rewritten in place if asked again."""
    with LOCK:
        d = load(day)
        items = d.setdefault("recaps", [])
        if not any(kind_of(r) in ("recap", "chunk") and r.get("status") == "approved" for r in items):
            raise ValueError(f"approve at least one chunk before the {kind}: it's written from them")
        r = next((x for x in items if kind_of(x) == kind), None)
        if r:
            r.update(status="writing", error="", comments=[], round=0, changed=[])
        else:
            r = blank(next_n(items), kind)
            items.append(r)
            r["file"] = file_for(d, r)
        save(day, d)
    spawn(write_draft, day, r["n"])
    return r["n"]


def add_outline(day: str, prompt: str) -> int:
    if not prompt.strip():
        raise ValueError("say what past work to make chunks about")
    with LOCK:
        d = load(day)
        items = d.setdefault("recaps", [])
        r = blank(next_n(items), "outline", focus=prompt.strip(), chunks=[])
        items.append(r)
        save(day, d)
    spawn(write_draft, day, r["n"])
    return r["n"]


def approve(day: str, n: int) -> list[int]:
    """Approve a draft. Approving an outline creates one chunk item per outline entry."""
    made = []
    with LOCK:
        d = load(day)
        r = item(d, n)
        if r.get("status") not in ("draft",):
            raise ValueError("only a finished draft can be approved")
        if any(c.get("status") in ("queued", "sending") for c in r.get("comments", [])):
            raise ValueError("send or delete your queued comments first")
        r["status"] = "approved"
        if kind_of(r) == "outline" and not r.get("made"):
            text = f"{r.get('title', '')}\n" + "\n".join(f"{i}. {c.get('title')}: {c.get('covers')}"
                                                         for i, c in enumerate(r.get("chunks", []), 1))
            for c in r.get("chunks", []):
                m = next_n(d["recaps"])
                x = blank(m, "chunk", plan=c, outline=n, outline_text=text, focus=r.get("focus", ""))
                d["recaps"].append(x)
                x["file"] = file_for(d, x)
                made.append(m)
            r["made"] = made
        save(day, d)
    for m in made:
        spawn(write_draft, day, m)
    return made


def midnight(d: str) -> str:
    return datetime.fromisoformat(d).astimezone().isoformat(timespec="seconds")


def new_day() -> str:
    existing = days()
    n = int(existing[-1].split("-")[1]) + 1 if existing else 1
    day = f"day-{n:02d}"
    today = date.today()
    # Pressed the evening before, a new day is tomorrow: the day after the last one, never in the past.
    last = date.fromisoformat(load(existing[-1])["date"]) if existing else None
    when = max(today, last + timedelta(days=1)) if last else today
    save(day, {"day": day, "date": when.isoformat(), "title": f"Day {n}", "subtitle": "",
               "start": midnight(when.isoformat()), "recaps": []})
    (CONTENT / day / "hours").mkdir(parents=True, exist_ok=True)
    return day


def delete_day(day: str) -> None:
    day_path(day)  # validates the id, so a crafted name can't point outside content/
    # Moved, not erased: the folder may hold recordings.
    trash = CONTENT / ".trash"
    trash.mkdir(exist_ok=True)
    shutil.move(str(CONTENT / day), str(trash / f"{day}-{datetime.now():%Y%m%d-%H%M%S}"))


# ---- http ---------------------------------------------------------------------------

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body: bytes, ctype: str, code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False).encode(), "application/json", code)

    def do_GET(self):
        path, _, query = self.path.partition("?")
        q = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
        if path in ("/", "/index.html"):
            return self._send((HERE / "page.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/review":
            return self._send((HERE / "review.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/api/state":
            ds = days()
            if not ds:
                return self._json({"days": [], "day": None, "now": now_iso()})
            return self._json(view(q.get("day") if q.get("day") in ds else ds[-1]))
        self.send_error(404)

    def do_POST(self):
        try:
            p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if self.path == "/api/new-day":
                return self._json(view(new_day()))
            day = p.get("day", "")
            if self.path == "/api/day-meta":
                with LOCK:
                    d = load(day)
                    for k in ("title", "subtitle"):
                        if k in p:
                            d[k] = p[k]
                    if "date" in p:
                        date.fromisoformat(p["date"])  # rejects anything that isn't a date
                        d["date"] = p["date"]
                        if not d.get("recaps"):  # once recaps exist, their times are fixed
                            d["start"] = midnight(p["date"])
                    save(day, d)
                return self._json({"ok": True})
            if self.path == "/api/check":
                if p.get("key") not in CHECKS:
                    raise ValueError(f"unknown check {p.get('key')!r}")
                with LOCK:
                    d = load(day)
                    d.setdefault("checks", {})[p["key"]] = bool(p.get("value"))
                    save(day, d)
                return self._json(view(day))
            if self.path == "/api/delete-day":
                with LOCK:
                    delete_day(day)
                ds = days()
                return self._json(view(ds[-1]) if ds else {"days": [], "day": None, "now": now_iso()})
            if self.path == "/api/recap":
                kind = p.get("kind", "recap")
                if kind in ("intro", "outro"):
                    add_bookend(day, kind)
                elif kind == "past":
                    add_outline(day, p.get("focus", ""))
                else:
                    add_recaps(day, p.get("until"), bool(p.get("split")), p.get("focus", ""))
                return self._json(view(day))
            if self.path == "/api/recap/retry":
                update_item(day, p["n"], status="writing", error="")
                spawn(write_draft, day, p["n"])
                return self._json(view(day))
            if self.path == "/api/recap/delete":
                with LOCK:
                    d = normalise(load(day))
                    r = item(d, p["n"])
                    v = video_of(day, d, r)
                    if v and v.exists():  # like Delete day: the recording is moved, never erased
                        trash = CONTENT / ".trash"
                        trash.mkdir(exist_ok=True)
                        shutil.move(str(v), str(trash / f"{day}-{v.stem}-{datetime.now():%Y%m%d-%H%M%S}{v.suffix}"))
                        for side in v.parent.glob(v.stem + ".captions.json"):
                            side.unlink()
                    d["recaps"] = [x for x in d["recaps"] if x["n"] != p["n"]]
                    save(day, d)
                return self._json(view(day))
            # ---- review ----
            if self.path == "/api/review/comment":  # add or delete a queued comment
                with LOCK:
                    d = load(day)
                    r = item(d, p["n"])
                    cs = r.setdefault("comments", [])
                    if p.get("delete"):
                        r["comments"] = [c for c in cs if not (c["id"] == p["delete"] and c.get("status") == "queued")]
                    else:
                        if p.get("kind") not in ("change", "question", "note") or not p.get("text", "").strip():
                            raise ValueError("a comment needs a kind and some text")
                        cs.append({"id": f"c{len(cs) + 1}-{datetime.now():%H%M%S}", "kind": p["kind"],
                                   "target": p.get("target", "general"), "label": p.get("label", ""),
                                   "text": p["text"].strip(), "status": "queued"})
                    save(day, d)
                return self._json(view(day))
            if self.path == "/api/review/send":
                with LOCK:
                    d = load(day)
                    r = item(d, p["n"])
                    queued = [c for c in r.get("comments", []) if c.get("status") == "queued"]
                    if not queued:
                        raise ValueError("no comments to send")
                    if r.get("status") != "draft":
                        raise ValueError("wait for the current draft to finish")
                    for c in queued:
                        c["status"] = "sending"
                    r.update(status="revising", error="")
                    save(day, d)
                spawn(revise, day, p["n"])
                return self._json(view(day))
            if self.path == "/api/review/approve":
                approve(day, p["n"])
                return self._json(view(day))
            if self.path == "/api/review/reopen":
                with LOCK:
                    d = load(day)
                    r = item(d, p["n"])
                    if kind_of(r) == "outline" and r.get("made"):
                        raise ValueError("its chunks already exist; review those instead")
                    r["status"] = "draft"
                    save(day, d)
                return self._json(view(day))
            return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": str(e)[:500]}, 400)


def in_use(port):
    # A connect probe catches listeners that SO_REUSEADDR would let us bind over on macOS.
    with socket.socket() as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def bind():
    host = os.environ.get("HOST", "127.0.0.1")
    for port in [START_PORT] if PINNED else range(START_PORT, START_PORT + 100):
        if in_use(port):
            continue
        try:
            return socketserver.ThreadingTCPServer((host, port), Handler), port
        except OSError:
            continue
    raise SystemExit(f"port {START_PORT} is in use" if PINNED else f"no free port from {START_PORT}")


if __name__ == "__main__":
    CONTENT.mkdir(parents=True, exist_ok=True)
    # Background work dies with the server: a draft left "writing" can be retried, and a
    # revision left "revising" falls back to its last draft with the comments re-queued.
    for dname in days():
        d = normalise(load(dname))
        for r in d.get("recaps", []):
            if r.get("status") == "writing":
                r.update({"status": "error", "error": "the server stopped while this was being written"})
            if r.get("status") == "revising":
                r["status"] = "draft"
                for c in r.get("comments", []):
                    if c.get("status") == "sending":
                        c["status"] = "queued"
        save(dname, d)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    httpd, port = bind()
    PORT_FILE.write_text(str(port))
    print(f"daily content page at http://localhost:{port}  (content: {CONTENT})")
    httpd.serve_forever()
