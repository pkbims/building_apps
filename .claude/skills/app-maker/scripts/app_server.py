#!/usr/bin/env python3
"""One server per app: serves every page of that app, and each page's html-worker API.

    app_server.py <app_dir>          # e.g. app_1, or research/<niche> before the app exists

App Maker decision D1 (2026-09-26): instead of one server per page, one server per app.
Every html-worker page folder under the app (a folder with index.html + state.json) is served
at its own path — /spec/, /engineering-center/, /research/reviewer/ — and gets its API at
<path>api/... The pages are unchanged: they call /api/..., so this server injects one line
into each page that points those calls at the page's own path.

Also: the page's conversation. A question, note or reply goes straight to that stage's Claude
session (named in <app>/.appmaker.json → "agents"), bundled if several arrive together; Send wakes it
for the round. Claude answers on the page with html-worker/reply.py. GET <page>api/agent says who
answers and whether they're busy.

Localhost only. Hidden files (.env, .git, …) are never served. Port: first free from 7801,
written to <app>/.appserver.port. Only this server writes a page's state.json while it runs.
"""
import http.server, json, os, socket, socketserver, subprocess, sys, threading, time
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse

APP = os.path.abspath(sys.argv[1])
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "html-worker"))
import server as hw          # html-worker's own load/save/write_inbox, pointed at one page at a time

LOCK = threading.Lock()
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", "DerivedData", ".build", "output-from-claude-design"}


def pages():
    """Every html-worker page under the app: {url path: folder}."""
    out = {}
    for d, subs, files in os.walk(APP):
        subs[:] = [s for s in subs if s not in SKIP and not s.startswith(".")]
        if "index.html" in files and "state.json" in files:
            rel = os.path.relpath(d, APP)
            out["/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/"] = d
    return out


def page_for(path):
    """The page a request belongs to: the longest page path that prefixes it."""
    best = None
    for p, d in pages().items():
        if path.startswith(p) and (best is None or len(p) > len(best[0])):
            best = (p, d)
    return best


def agents():
    try:
        return json.load(open(os.path.join(APP, ".appmaker.json"))).get("agents", {})
    except (OSError, ValueError):
        return {}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=APP, **kw)

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _hidden(self, path):
        return any(part.startswith(".") for part in unquote(path).split("/") if part)

    def do_HEAD(self):
        if self._hidden(urlparse(self.path).path):
            return self.send_error(404)
        return super().do_HEAD()

    def do_GET(self):
        u = urlparse(self.path)
        if self._hidden(u.path):
            return self.send_error(404)
        if u.path == "/api/pages":
            return self._json({"app": os.path.basename(APP), "pages": sorted(pages())})
        pg = page_for(u.path)
        if pg and u.path == pg[0] + "api/agent":
            return self._json(agent_status(pg))
        if pg and u.path == pg[0] + "api/state":
            with LOCK:
                self._point(pg[1])
                return self._json(hw.load())
        # a page's own html: inject the one line that sends its /api/ calls to its own path
        fs = self.translate_path(u.path)
        if os.path.isdir(fs):
            if not u.path.endswith("/"):
                self.send_response(301); self.send_header("Location", u.path + "/"); self.end_headers(); return
            fs = os.path.join(fs, "index.html")
        if pg and fs.endswith(".html") and os.path.isfile(fs):
            html = open(fs, encoding="utf-8").read()
            shim = ("<script>(()=>{const P=%s;const f=window.fetch.bind(window);"
                    "window.fetch=(u,o)=>f(typeof u==='string'&&u.startsWith('/api/')?P+u.slice(1):u,o);"
                    # the App Maker's theme, sent to the page inside its frame (colour tokens + light/dark)
                    "addEventListener('message',e=>{const d=e.data;if(!d||d.type!=='am-theme')return;"
                    "const R=document.documentElement;for(const[k,v]of Object.entries(d.vars))R.style.setProperty(k,v);"
                    "R.dataset.theme=d.dark?'dark':'light';R.style.colorScheme=d.dark?'dark':'light'})})()</script>"
                    % json.dumps(pg[0]))
            i = html.find("<head>")
            html = html[:i + 6] + shim + html[i + 6:] if i >= 0 else shim + html
            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def _point(self, d):
        hw.HERE, hw.STATE, hw.INBOX = d, os.path.join(d, "state.json"), os.path.join(d, "INBOX.md")

    def do_POST(self):
        u = urlparse(self.path)
        pg = page_for(u.path)
        if not pg or not u.path.startswith(pg[0] + "api/"):
            return self._json({"error": "unknown endpoint"}, 404)
        ep = "/api/" + u.path[len(pg[0] + "api/"):]
        try:
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except json.JSONDecodeError:
            return self._json({"error": "bad json"}, 400)
        with LOCK:
            self._point(pg[1])
            obj, event = hw.api(ep, payload)       # html-worker's own page actions — one implementation
            rnd = len(hw.load()["batches"])
        if event == "send":
            obj["woke"] = wake(pg, rnd)
        elif event == "message":
            PENDING[pg[0]] = (pg, time.time())      # bundled: see bundle_messages()
        return self._json(obj, 404 if obj.get("error") == "unknown endpoint" else 200)


def wake(pg, rnd):
    """The user pressed Send on a page → type a prompt into that stage's Claude session (herdr).
    Replaces the watcher each session used to run on INBOX.md, which the harness could reap."""
    agent = agents().get(pg[0].strip("/") or ".")
    if not agent:
        return None
    port = open(os.path.join(APP, ".appserver.port")).read().strip()
    post = os.path.join(ROOT, ".claude", "skills", "code-orchestrator", "scripts", "post.py")
    r = subprocess.run(["herdr", "agent", "prompt", agent,
                        f"The user sent round {rnd} on the {pg[0]} page of {os.path.basename(APP)}. Read {pg[1]}/INBOX.md and act on it: "
                        f"change requests → revise the page; questions and notes → answer on the page with "
                        f"python3 {post} {pg[1]} update \"...\" (never only in this terminal). Then mark the comments addressed: "
                        f"curl -s -X POST localhost:{port}{pg[0]}api/comment/addressed -d '{{}}'"],
                       capture_output=True, text=True, timeout=20)
    return agent if r.returncode == 0 else None


PENDING = {}                      # page path → (page, time of the last message)
BUNDLE_S = 8                      # messages sent within this many seconds go to Claude as one wake-up


def agent_status(pg):
    name = agents().get(pg[0].strip("/") or ".")
    if not name:
        return {"agent": None, "status": None}
    try:
        a = json.loads(subprocess.run(["herdr", "agent", "get", name], capture_output=True, text=True, timeout=5).stdout)
        return {"agent": name, "status": a["result"]["agent"].get("agent_status")}
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired):
        return {"agent": name, "status": "not running"}


def bundle_messages():
    """Questions, notes and replies go straight to Claude — but a burst becomes one wake-up (fewer turns)."""
    while True:
        time.sleep(2)
        for key, (pg, t) in list(PENDING.items()):
            if time.time() - t < BUNDLE_S:
                continue
            PENDING.pop(key, None)
            agent = agents().get(pg[0].strip("/") or ".")
            if not agent:
                continue            # no session for this page: INBOX.md (written by html-worker) is the fallback
            with LOCK:
                hw.HERE, hw.STATE, hw.INBOX = pg[1], os.path.join(pg[1], "state.json"), os.path.join(pg[1], "INBOX.md")
                st = hw.load()
            open_ = [c for c in st["comments"] if c.get("status") == "sent" and not c.get("addressed")]
            if not open_:
                continue
            lines = []
            for c in open_:
                convo = " | ".join(f"{'Claude' if m.get('from') == 'claude' else 'You'}: {m.get('text', '')}" for m in c.get("messages", []))
                lines.append(f"[id {c['id']} · {c.get('kind', 'change')} · on {c.get('anchorLabel') or c.get('anchor')}] {c.get('text', '')}"
                             + (f" — conversation so far: {convo}" if convo else ""))
            reply = os.path.join(ROOT, ".claude", "skills", "html-worker", "reply.py")
            subprocess.run(["herdr", "agent", "prompt", agent,
                            f"The user wrote on the {pg[0]} page of {os.path.basename(APP)} (answer each ON THE PAGE, short and plain: "
                            f"python3 {reply} {pg[1]} <id> \"answer\" — add --suggest if the answer implies changing the page; "
                            f"never edit the page for a question): " + "  ||  ".join(lines)],
                           capture_output=True, text=True, timeout=20)


def notify(title, text):
    esc = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(["osascript", "-e", f'display notification "{esc(text)}" with title "{esc(title)}" sound name "Glass"'],
                   capture_output=True, timeout=10)


def watch_questions():
    """Every page's feed.json (post.py's format): a new open question → one macOS notification.
    Seen ids are kept in <page>/.seen_asks so a restart doesn't repeat them. Pages that already had
    questions when the server started are marked seen once; a page made later notifies from its first."""
    for p, d in pages().items():
        sp = os.path.join(d, ".seen_asks")
        if not os.path.exists(sp):
            try:
                items = json.load(open(os.path.join(d, "feed.json"))).get("items", [])
            except (OSError, ValueError):
                items = []
            json.dump(sorted(i["id"] for i in items if i.get("kind") == "ask"), open(sp, "w"))
    while True:
        for p, d in pages().items():
            try:
                items = json.load(open(os.path.join(d, "feed.json"))).get("items", [])
            except (OSError, ValueError):
                continue
            sp = os.path.join(d, ".seen_asks")
            try:
                seen = set(json.load(open(sp)))
            except (OSError, ValueError):
                seen = set()                     # a page made after the server started: all its questions are new
            fresh = [i for i in items if i.get("kind") == "ask" and i.get("status") == "open" and i["id"] not in seen]
            for i in fresh:
                notify(f"{os.path.basename(APP)} · {p.strip('/') or 'app'} — needs you", i.get("text", "")[:180])
                seen.add(i["id"])
            if fresh:
                json.dump(sorted(seen), open(sp, "w"))
        time.sleep(10)


def free_port(start=7801):
    for p in range(start, start + 100):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise SystemExit("no free port")


if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    port = int(os.environ.get("PORT") or free_port())
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
    open(os.path.join(APP, ".appserver.port"), "w").write(str(port))
    threading.Thread(target=watch_questions, daemon=True).start()
    threading.Thread(target=bundle_messages, daemon=True).start()
    print(f"{os.path.basename(APP)} app server on http://localhost:{port}/  ({len(pages())} pages)")
    httpd.serve_forever()
