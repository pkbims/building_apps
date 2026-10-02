#!/usr/bin/env python3
"""Daily task list: say what you're doing today, get task cards, tick them off.

    cd building_apps && python3 .claude/skills/daily-tasks/server.py

One file per calendar date in tasks/YYYY-MM-DD.json. "Make my task list" sends what you
said to Claude with `claude -p` (no tools, no saved session) and gets back 2-5 tasks
with 2-4 steps each. Ticking, adding and removing are plain saves; Claude isn't involved.
"""
from __future__ import annotations

import http.server
import json
import os
import re
import socket
import socketserver
import subprocess
import threading
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = Path(os.environ.get("TASKS", Path.cwd() / "tasks")).resolve()
PORT_FILE = TASKS / ".port"
START_PORT = int(os.environ.get("PORT", "7800"))
PINNED = "PORT" in os.environ
MODEL = os.environ.get("TASKS_MODEL", "sonnet")
LOCK = threading.Lock()

PROMPT = """You turn a spoken plan for a workday into task cards.
Return ONLY JSON, no prose, shaped exactly:
{"tasks":[{"icon":"<one emoji>","title":"<max 6 words>","why":"<max 8 words, what it's for>","steps":["<max 7 words>", ...]}]}
Rules: 2-5 tasks, each with 2-4 steps. Plain words, no jargon. Keep the speaker's order.
Merge small things into one task rather than making many tiny ones.
If an existing list is given and the speaker is adding to it, keep the existing tasks and
repeat done steps' text exactly so they stay ticked."""

ADD_PROMPT = """You turn one spoken task into a single task card.
Return ONLY JSON, no prose, shaped exactly:
{"icon":"<one emoji>","title":"<max 6 words>","why":"<max 8 words, what it's for>","steps":["<max 7 words>", ...]}
Rules: exactly one task, 2-4 steps. Plain words, no jargon. Even if the speaker mentions
several things, keep them as steps of this one task."""


def path(d: str) -> Path:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        raise ValueError(f"bad date {d!r}")
    return TASKS / f"{d}.json"


def load(d: str) -> dict:
    p = path(d)
    return json.loads(p.read_text()) if p.exists() else {"date": d, "tasks": []}


def save(d: str, data: dict) -> None:
    p = path(d)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(p)  # atomic, so a crash mid-write never leaves half a file


def dates() -> list[str]:
    ds = {p.stem for p in TASKS.glob("????-??-??.json")} | {date.today().isoformat()}
    return sorted(ds)


def view(d: str) -> dict:
    return {"dates": dates(), "today": date.today().isoformat(), "list": load(d)}


def ask(prompt: str, text: str) -> dict:
    out = subprocess.run(
        ["claude", "-p", "--no-session-persistence", "--tools", "", "--model", MODEL,
         "--output-format", "json", "--system-prompt", prompt],
        input=text, capture_output=True, text=True, timeout=180, cwd=str(TASKS),
    )
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout).strip()[:400] or "claude failed")
    reply = json.loads(out.stdout).get("result", "")
    return json.loads(reply[reply.find("{"):reply.rfind("}") + 1])  # tolerate a fence around the JSON


def card(t: dict, done: set[str] = frozenset()) -> dict:
    return {"icon": t.get("icon", "•"), "title": t.get("title", ""), "why": t.get("why", ""),
            "steps": [{"text": s, "done": s in done} for s in t.get("steps", [])]}


def generate(d: str, spoken: str) -> dict:
    cur = load(d)
    got = ask(PROMPT, f"Spoken plan:\n{spoken}\n\nExisting list (may be empty):\n{json.dumps(cur['tasks'], ensure_ascii=False)}")
    done = {s["text"] for t in cur["tasks"] for s in t["steps"] if s.get("done")}
    tasks = [card(t, done) for t in got.get("tasks", [])]
    with LOCK:
        cur = load(d)
        cur["tasks"], cur["spoken"] = tasks, spoken
        save(d, cur)
    return view(d)


def add(d: str, spoken: str) -> dict:
    """One spoken task becomes one new card. The existing list is never sent to Claude,
    so nothing already there can be reworded or lose its ticks."""
    if not spoken.strip():
        raise ValueError("say the task first")
    new = card(ask(ADD_PROMPT, f"Spoken task:\n{spoken}"))
    with LOCK:
        cur = load(d)  # re-read: ticks made while Claude was writing must survive
        cur["tasks"].append(new)
        save(d, cur)
    return view(d)


def move(src: str, dst: str, index: int) -> dict:
    """Move one card to another day, keeping its steps and ticks exactly as they are.
    Both files are written under the one lock, so a move can't race a tick on either day."""
    if src == dst:
        raise ValueError("that card is already on that day")
    path(src), path(dst)  # validates both dates before anything is written
    with LOCK:
        a = load(src)
        if not 0 <= index < len(a["tasks"]):
            raise ValueError("that card isn't there any more — reload the page")
        card_ = a["tasks"].pop(index)
        b = load(dst)
        b["tasks"].append(card_)
        save(dst, b)
        save(src, a)   # the source is written last: a crash mid-move duplicates a card
                       # rather than losing one, and a duplicate is easy to delete.
    return view(src)


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
        if self.path in ("/", "/index.html"):
            return self._send((HERE / "page.html").read_bytes(), "text/html; charset=utf-8")
        if self.path.startswith("/api/state"):
            m = re.search(r"date=(\d{4}-\d{2}-\d{2})", self.path)
            return self._json(view(m.group(1) if m else date.today().isoformat()))
        self.send_error(404)

    def do_POST(self):
        try:
            p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            d = p.get("date", date.today().isoformat())
            if self.path == "/api/tasks":
                with LOCK:
                    cur = load(d)
                    cur["tasks"] = p["tasks"]
                    save(d, cur)
                return self._json({"ok": True})
            if self.path == "/api/goals":  # hand-typed only; never sent to Claude
                with LOCK:
                    cur = load(d)
                    cur["goals"] = p["goals"]
                    save(d, cur)
                return self._json({"ok": True})
            if self.path == "/api/generate":
                return self._json(generate(d, p.get("text", "")))
            if self.path == "/api/add":
                return self._json(add(d, p.get("text", "")))
            if self.path == "/api/move":
                return self._json(move(d, p["to"], int(p["index"])))
            return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": str(e)[:400]}, 400)


def in_use(port):
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
    TASKS.mkdir(parents=True, exist_ok=True)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    httpd, port = bind()
    PORT_FILE.write_text(str(port))
    print(f"daily tasks at http://localhost:{port}  (tasks: {TASKS})")
    httpd.serve_forever()
