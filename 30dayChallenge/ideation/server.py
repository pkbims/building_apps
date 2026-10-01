#!/usr/bin/env python3
"""Ideation's own server. Separate from the App Maker (user, 2026-10-01: "completely separate").

    python3 server.py            # from this folder; PORT=7802 pins the port

Serves the shell (index.html + nav.json) and every html-worker page under this folder
(plan/, sources/, runs/run-NN/, selected/) at its own path, with that page's API at
<path>api/... Pages are unchanged html-worker pages: they call /api/..., so one injected line
points those calls at the page's own path.

Send on a page wakes the Claude session in ideation.json → "agent" (a herdr pane id); questions
and replies are bundled into one wake-up. Discard moves that page's folder to the Trash and drops
it from nav.json. Localhost only; hidden files are never served.
"""
import http.server, json, os, shutil, socket, socketserver, subprocess, threading, time
from datetime import datetime
from urllib.parse import unquote, urlparse
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.expanduser("~/Documents/building_apps/.claude/skills/html-worker")   # review-page mechanics
sys.path.insert(0, HW)
import server as hw          # html-worker's load/save/api, pointed at one page at a time

LOCK = threading.Lock()
PENDING = {}                 # page path → (page, time of last message)
BUNDLE_S = 8
PORT = None


def pages():
    """Every review page under this folder: {url path: folder}."""
    out = {}
    for d, subs, files in os.walk(HERE):
        subs[:] = [s for s in subs if not s.startswith(".") and s != "__pycache__"]
        if d != HERE and "index.html" in files and "state.json" in files:
            out["/" + os.path.relpath(d, HERE).replace(os.sep, "/") + "/"] = d
    return out


def page_for(path):
    best = None
    for p, d in pages().items():
        if path.startswith(p) and (best is None or len(p) > len(best[0])):
            best = (p, d)
    return best


def agent():
    try:
        return json.load(open(os.path.join(HERE, "ideation.json"))).get("agent")
    except (OSError, ValueError):
        return None


def point(d):
    hw.HERE, hw.STATE, hw.INBOX = d, os.path.join(d, "state.json"), os.path.join(d, "INBOX.md")


def wake(text):
    a = agent()
    if not a:
        return False
    try:
        return subprocess.run(["herdr", "agent", "prompt", a, text], capture_output=True,
                              text=True, timeout=20).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def addressed(pg):
    return f"curl -s -X POST localhost:{PORT}{pg[0]}api/comment/addressed -d '{{}}'"


def bundle_messages():
    while True:
        time.sleep(2)
        for key, (pg, t) in list(PENDING.items()):
            if time.time() - t < BUNDLE_S:
                continue
            PENDING.pop(key, None)
            wake(f"The user wrote on the Ideation page {pg[0]} ({pg[1]}). Read {pg[1]}/INBOX.md and answer each "
                 f"open question ON THE PAGE with reply.py, as it says. Then: {addressed(pg)}")


def discard(pg):
    """Discard on a page: move its folder to the Trash, drop it from nav.json, tell Claude."""
    time.sleep(0.5)
    dest = os.path.join(os.path.expanduser("~/.Trash"),
                        f"ideation-{pg[0].strip('/').replace('/', '-')}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    with LOCK:
        shutil.move(pg[1], dest)
        try:
            nav = json.load(open(os.path.join(HERE, "nav.json")))
            for g in nav.get("groups", []):
                g["items"] = [i for i in g.get("items", []) if "/" + i.get("path", "").strip("/") + "/" != pg[0]]
            json.dump(nav, open(os.path.join(HERE, "nav.json"), "w"), indent=2)
        except (OSError, ValueError):
            pass
    wake(f"The user discarded the Ideation page {pg[0]}. It was moved to {dest} and removed from the navbar. "
         f"Acknowledge in one line; don't recreate it unless asked.")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

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
        return any(p.startswith(".") for p in unquote(path).split("/") if p) or path.endswith((".py", ".md", ".json")) \
            and not path.endswith("/nav.json")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_HEAD(self):
        if self._hidden(urlparse(self.path).path):
            return self.send_error(404)
        return super().do_HEAD()

    def do_GET(self):
        u = urlparse(self.path)
        if self._hidden(u.path):
            return self.send_error(404)
        pg = page_for(u.path)
        if pg and u.path == pg[0] + "api/agent":
            a = agent()
            if not a:
                return self._json({"agent": None, "status": None})
            try:
                r = json.loads(subprocess.run(["herdr", "agent", "get", a], capture_output=True,
                                              text=True, timeout=5).stdout)["result"]["agent"]
                return self._json({"agent": r.get("agent", a), "status": r.get("agent_status")})
            except (ValueError, KeyError, OSError, subprocess.TimeoutExpired):
                return self._json({"agent": a, "status": "not running"})
        if pg and u.path == pg[0] + "api/state":
            with LOCK:
                point(pg[1])
                return self._json(hw.load())
        fs = self.translate_path(u.path)
        if os.path.isdir(fs):
            if not u.path.endswith("/"):
                self.send_response(301); self.send_header("Location", u.path + "/"); self.end_headers(); return
            fs = os.path.join(fs, "index.html")
        if pg and fs.endswith(".html") and os.path.isfile(fs):
            html = open(fs, encoding="utf-8").read()
            shim = ("<script>(()=>{const P=%s;const f=window.fetch.bind(window);"
                    "window.fetch=(u,o)=>f(typeof u==='string'&&u.startsWith('/api/')?P+u.slice(1):u,o)})()</script>"
                    % json.dumps(pg[0]))
            i = html.find("<head>")
            html = html[:i + 6] + shim + html[i + 6:] if i >= 0 else shim + html
            body = html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

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
        if ep == "/api/discard":
            threading.Thread(target=discard, args=(pg,), daemon=True).start()
            return self._json({"ok": True})
        with LOCK:
            point(pg[1])
            obj, event = hw.api(ep, payload)
            rnd = len(hw.load()["batches"])
        if event == "send":
            obj["woke"] = wake(f"The user sent round {rnd} on the Ideation page {pg[0]} ({pg[1]}). Read {pg[1]}/INBOX.md "
                               f"and act on it: change requests → revise the page; open questions and notes → answer on "
                               f"the page with reply.py. Then: {addressed(pg)}")
        elif event == "message":
            PENDING[pg[0]] = (pg, time.time())
        return self._json(obj, 404 if obj.get("error") == "unknown endpoint" else 200)


def free_port(start=7802):
    for p in range(start, start + 100):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise SystemExit("no free port")


if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    PORT = int(os.environ.get("PORT") or free_port())
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    open(os.path.join(HERE, ".port"), "w").write(str(PORT))
    open(os.path.join(HERE, ".pages.port"), "w").write(str(PORT))   # how html-worker's reply.py finds us
    threading.Thread(target=bundle_messages, daemon=True).start()
    print(f"Ideation on http://localhost:{PORT}/  ({len(pages())} pages)")
    httpd.serve_forever()
