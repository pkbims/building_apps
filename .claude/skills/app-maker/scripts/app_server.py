#!/usr/bin/env python3
"""One server per app: serves every page of that app, and each page's html-worker API.

    app_server.py <app_dir>          # e.g. app_1, or research/<niche> before the app exists

App Maker decision D1 (2026-09-26): instead of one server per page, one server per app.
Every html-worker page folder under the app (a folder with index.html + state.json) is served
at its own path — /spec/, /engineering-center/, /research/reviewer/ — and gets its API at
<path>api/... The pages are unchanged: they call /api/..., so this server injects one line
into each page that points those calls at the page's own path.

Also: POST <page>/api/talk — the "Talk to Claude" box. The message is saved in the page's
talk.json and typed into that stage's Claude session through herdr (the session is named in
<app>/.appmaker.json → "agents"); it replies with scripts/talk.py.

Localhost only. Hidden files (.env, .git, …) are never served. Port: first free from 7801,
written to <app>/.appserver.port. Only this server writes a page's state.json while it runs.
"""
import http.server, json, os, socket, socketserver, subprocess, sys, threading
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
                    "window.fetch=(u,o)=>f(typeof u==='string'&&u.startsWith('/api/')?P+u.slice(1):u,o)})()</script>"
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
        if ep == "/api/talk":
            return self._json(self._talk(pg, payload))
        with LOCK:
            self._point(pg[1])
            st = hw.load()
            if ep == "/api/groups":
                st["groups"] = payload.get("groups", []); hw.save(st); return self._json({"ok": True})
            if ep == "/api/decision":
                if payload.get("value") is None:
                    st["decisions"].pop(payload["id"], None)
                else:
                    st["decisions"][payload["id"]] = payload["value"]
                hw.save(st); return self._json({"ok": True})
            if ep == "/api/comment":
                payload.update(status="queued", ts=now()); st["comments"].append(payload)
                hw.save(st); return self._json({"ok": True, "comments": st["comments"]})
            if ep == "/api/comment/delete":
                st["comments"] = [c for c in st["comments"] if c.get("id") != payload.get("id")]
                hw.save(st); return self._json({"ok": True, "comments": st["comments"]})
            if ep == "/api/comment/addressed":
                n = 0
                for c in st["comments"]:
                    if c.get("status") == "sent" and not c.get("addressed"):
                        c["addressed"] = True; n += 1
                hw.save(st); return self._json({"ok": True, "addressed": n})
            if ep == "/api/send":
                ids = []
                for c in st["comments"]:
                    if c.get("status") == "queued":
                        c["status"] = "sent"; ids.append(c.get("id"))
                st["batches"].append({"round": len(st["batches"]) + 1, "ts": now(), "commentIds": ids,
                                      "decisions": dict(st["decisions"])})
                hw.save(st); hw.write_inbox(st)
                return self._json({"ok": True, "sent": len(ids)})
        return self._json({"error": "unknown endpoint"}, 404)

    def _talk(self, pg, payload):
        """A message from the page's "Talk to Claude" box → talk.json + the stage's Claude session."""
        text = (payload.get("text") or "").strip()
        if not text:
            return {"error": "empty"}
        path = os.path.join(pg[1], "talk.json")
        with LOCK:
            try:
                talk = json.load(open(path))
            except (OSError, ValueError):
                talk = {"messages": []}
            talk["messages"].append({"from": "you", "t": now(), "text": text})
            json.dump(talk, open(path, "w"), indent=1)
        agent = agents().get(pg[0].strip("/") or ".")
        if not agent:
            return {"ok": True, "delivered": False, "why": "no Claude session for this stage — start one from the App Maker"}
        reply = os.path.join(ROOT, ".claude", "skills", "app-maker", "scripts", "talk.py")
        r = subprocess.run(["herdr", "agent", "prompt", agent,
                            f"The user wrote in the Talk box on the {pg[0]} page of {os.path.basename(APP)}: \"{text}\" — "
                            f"answer them there (not only in this terminal): python3 {reply} {pg[1]} \"<your reply>\". "
                            f"Plain English, short. If it asks for a change, do it, then reply what you did."],
                           capture_output=True, text=True, timeout=20)
        return {"ok": True, "delivered": r.returncode == 0, "agent": agent}


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
    print(f"{os.path.basename(APP)} app server on http://localhost:{port}/  ({len(pages())} pages)")
    httpd.serve_forever()
