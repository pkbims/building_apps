#!/usr/bin/env python3
"""App Progress Visualizer — one page showing where every app in the series stands.

Everything is derived from disk on each load (scan.py); nothing is hand-maintained.
Opening a document generates a read-only copy of it beside the original, so a settled
review page can be read and shown without its own server running.
"""

import html
import importlib
import json
import os
import re
import socket
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

import scan as scanner
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app-maker", "scripts"))
import maker                              # the App Maker (2026-09-26): this server grew into it — D3
MAKER_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app-maker", "maker.html")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = scanner.ROOT
PORTFILE = os.path.join(HERE, ".port")
HIDDEN = os.path.join(HERE, "hidden.json")


def hidden_apps():
    """Which apps the board leaves out. A view preference owned by this tool — it is
    never written into an app, and it changes nothing that scan.py derives."""
    try:
        return list(json.load(open(HIDDEN)).get("apps", []))
    except (OSError, json.JSONDecodeError):
        return []


def set_hidden(app_id, hide):
    apps = [a for a in hidden_apps() if a != app_id]
    if hide:
        apps.append(app_id)
    try:
        json.dump({"apps": sorted(apps)}, open(HIDDEN, "w"), indent=2)
    except OSError:
        pass
    return apps

# Injected into a copied review page so it renders with its recorded answers and
# saves nothing. Overriding fetch beats rewriting the page's script: the pages were
# built from different template versions and only agree on talking to /api/state.
SHIM = """<script>
window.__STATE__ = %s;
window.mermaid = window.mermaid || {initialize:function(){}, run:function(){return Promise.resolve()}};
(function(){
  window.fetch = function(u){
    if (String(u).indexOf('/api/state') >= 0)
      return Promise.resolve({json:function(){return Promise.resolve(window.__STATE__)}});
    return Promise.resolve({json:function(){
      return Promise.resolve({ok:true, comments:(window.__STATE__.comments||[]), sent:0, addressed:0})}});
  };
  addEventListener('DOMContentLoaded', function(){
    var b = document.createElement('div');
    b.textContent = 'Read-only copy \\u2014 decisions shown as recorded. Nothing you click here is saved.';
    b.style.cssText = 'position:sticky;top:0;z-index:999;background:#7a5a1e;color:#fff;'
      + 'padding:7px 16px;font:600 12px/1.5 system-ui,sans-serif;letter-spacing:.02em';
    document.body.insertBefore(b, document.body.firstChild);
    var r = document.getElementById('round');
    if (r) r.textContent = 'Read-only copy';
    var s = document.getElementById('send');
    if (s) { s.disabled = true; s.textContent = 'Review closed'; s.style.opacity = .5; }
  });
})();
</script>"""


def free_port(start=7710):
    for p in range(start, start + 40):
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # a just-restarted port is free, not taken
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return start


def reading_copy(page_dir):
    """Write reading-copy.html beside an html-worker page (D16/D17) and return its path.
    Regenerated whenever state.json is newer than the copy."""
    src = os.path.join(page_dir, "index.html")
    state = os.path.join(page_dir, "state.json")
    out = os.path.join(page_dir, "reading-copy.html")
    if not os.path.exists(src):
        return None
    if (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src)
            and (not os.path.exists(state) or os.path.getmtime(out) >= os.path.getmtime(state))):
        return out
    try:
        doc = open(src, errors="ignore").read()
        st = json.load(open(state)) if os.path.exists(state) else {}
    except (OSError, json.JSONDecodeError):
        return None
    shim = SHIM % json.dumps(st)
    if "<head>" in doc:
        doc = doc.replace("<head>", "<head>\n" + shim, 1)
    else:
        doc = shim + doc
    try:
        open(out, "w").write(doc)
    except OSError:
        return None
    return out


MD_RULES = [
    (re.compile(r"^###### (.+)$", re.M), r"<h6>\1</h6>"),
    (re.compile(r"^##### (.+)$", re.M), r"<h5>\1</h5>"),
    (re.compile(r"^#### (.+)$", re.M), r"<h4>\1</h4>"),
    (re.compile(r"^### (.+)$", re.M), r"<h3>\1</h3>"),
    (re.compile(r"^## (.+)$", re.M), r"<h2>\1</h2>"),
    (re.compile(r"^# (.+)$", re.M), r"<h1>\1</h1>"),
    (re.compile(r"^> (.+)$", re.M), r"<blockquote>\1</blockquote>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<b>\1</b>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), r'<a href="\2">\1</a>'),
]


def render_markdown(path):
    """Enough markdown for reading a PRD or a research file in the panel."""
    try:
        txt = open(path, errors="ignore").read()
    except OSError:
        return "<p>Could not read this file.</p>"
    out, in_code, in_list, body = [], False, False, []
    for line in txt.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append("<pre>" if in_code else "</pre>")
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        esc = html.escape(line)
        for rx, sub in MD_RULES:
            esc = rx.sub(sub, esc)
        if re.match(r"^\s*[-*] ", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + re.sub(r"^\s*[-*] ", "", esc) + "</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("|"):
            cells = [c.strip() for c in esc.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            out.append("<tr>" + "".join("<td>%s</td>" % c for c in cells) + "</tr>")
            continue
        out.append("<p>%s</p>" % esc if esc.strip() else "")
    if in_list:
        out.append("</ul>")
    body = "\n".join(out)
    body = re.sub(r"(<tr>.*?</tr>\n?)+", lambda m: "<table>" + m.group(0) + "</table>", body, flags=re.S)
    return body


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _html(self, s, code=200):
        b = s.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        p = urlparse(self.path).path
        if p.startswith("/api/maker/"):
            importlib.reload(maker)
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                if p == "/api/maker/talk":
                    return self._json(maker.talk(body["app"], body["page"], body["text"]))
                if p == "/api/maker/start":
                    return self._json({"ok": True, "msg": maker.start_stage(body["app"], body["stage"])})
                if p == "/api/maker/new":
                    return self._json({"ok": True, "msg": maker.new_app(body.get("name", ""), body.get("problem", ""))})
            except Exception as e:
                return self._json({"error": str(e)[:300]}, 400)
            return self._json({"error": "unknown"}, 404)
        if urlparse(self.path).path != "/api/hidden":
            return self._json({"error": "unknown endpoint"}, 404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json({"error": "bad json"}, 400)
        if not body.get("id"):
            return self._json({"error": "no id"}, 400)
        return self._json({"hidden": set_hidden(body["id"], bool(body.get("hidden")))})

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)

        if u.path == "/api/maker":
            importlib.reload(scanner); importlib.reload(maker)
            try:
                return self._json(maker.state(scanner.scan(), hidden_apps()))
            except Exception as e:
                return self._json({"error": str(e), "apps": []}, 500)
        if u.path == "/api/maker/talk":
            importlib.reload(maker)
            return self._json(maker.talk_thread((q.get("app") or [""])[0], (q.get("page") or [""])[0]))
        if u.path == "/md":
            # a document as a readable page, for the App Maker's frame
            app = (q.get("app") or [""])[0]; rel = (q.get("path") or [""])[0]
            target = os.path.normpath(os.path.join(ROOT, app, rel))
            if not target.startswith(ROOT) or not os.path.isfile(target):
                return self._html("<p>Not found.</p>", 404)
            # themed by the App Maker (it posts its colours in); plain light/dark otherwise
            return self._html("<!doctype html><meta charset=utf-8><style>:root{--bg:#f4eee2;--panel:#fdf9f1;--ink:#2a2521;--line:#e3d9c7;--soft:#f5e4dc;--accent:#b0523a}"
                              "@media(prefers-color-scheme:dark){:root{--bg:#1b1916;--panel:#242019;--ink:#ede4d6;--line:#38322a;--soft:#3b2a24;--accent:#e28f72}}"
                              "body{font:15px/1.6 system-ui;max-width:860px;margin:0 auto;padding:24px 20px;background:var(--bg);color:var(--ink)}a{color:var(--accent)}"
                              "table{border-collapse:collapse}td,th{border:1px solid var(--line);padding:4px 8px}pre,code{background:var(--soft)}pre{padding:10px;overflow:auto}</style>"
                              "<script>addEventListener('message',e=>{const d=e.data;if(!d||d.type!=='am-theme')return;const R=document.documentElement;"
                              "for(const[k,v]of Object.entries(d.vars))R.style.setProperty(k,v);R.style.colorScheme=d.dark?'dark':'light'})</script>"
                              + render_markdown(target))
        if u.path == "/":
            return self._html(open(MAKER_HTML, encoding="utf-8").read())
        if u.path == "/progress":
            self.path = "/index.html"
            return super().do_GET()

        if u.path == "/api/scan":
            try:
                importlib.reload(scanner)            # pick up scan.py edits without a restart
                data = scanner.scan()
                data["hidden"] = hidden_apps()
                return self._json(data)
            except Exception as e:                      # a broken repo must not blank the page
                return self._json({"error": str(e), "apps": []}, 500)

        if u.path == "/api/doc":
            app = (q.get("app") or [""])[0]
            rel = (q.get("path") or [""])[0]
            target = os.path.normpath(os.path.join(ROOT, app, rel))
            if not target.startswith(ROOT) or not os.path.exists(target):
                return self._html("<p>Not found.</p>", 404)
            if os.path.isdir(target):
                copy = reading_copy(target)
                if copy:
                    return self._json({"kind": "page",
                                       "url": "/f/" + os.path.relpath(copy, ROOT)})
                listing = "".join("<li>%s</li>" % html.escape(f) for f in sorted(os.listdir(target)))
                return self._json({"kind": "inline", "html": "<ul>%s</ul>" % listing})
            if target.endswith(".html"):
                return self._json({"kind": "page", "no_shim": True,
                                   "url": "/f/" + os.path.relpath(target, ROOT)})
            if target.endswith((".md", ".txt")):
                return self._json({"kind": "inline", "html": render_markdown(target)})
            if target.endswith(".json"):
                try:
                    data = json.load(open(target))
                    paths = data.get("paths", {})
                    rows = "".join(
                        "<tr><td><code>%s</code></td><td>%s</td></tr>"
                        % (html.escape(p), ", ".join(m.upper() for m in sorted(v)))
                        for p, v in sorted(paths.items()))
                    return self._json({"kind": "inline",
                                       "html": "<p>%d routes, frozen.</p><table>%s</table>"
                                               % (len(paths), rows)})
                except (json.JSONDecodeError, OSError):
                    pass
            return self._json({"kind": "inline",
                               "html": "<pre>%s</pre>" % html.escape(open(target, errors="ignore").read()[:20000])})

        if u.path.startswith("/f/"):
            # Real path, not a query string: a copied page's own relative links to
            # vendor/ and images/ have to resolve next to it.
            from urllib.parse import unquote
            rel = unquote(u.path[3:])
            target = os.path.normpath(os.path.join(ROOT, rel))
            if not target.startswith(ROOT) or not os.path.isfile(target):
                return self._html("<p>Not found.</p>", 404)
            import mimetypes
            ctype = mimetypes.guess_type(target)[0] or "application/octet-stream"
            if ctype.startswith("text/"):
                ctype += "; charset=utf-8"
            b = open(target, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            return self.wfile.write(b)

        return super().do_GET()


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT") or free_port())
    try:
        open(PORTFILE, "w").write(str(PORT))
    except OSError:
        pass
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print("App Progress Visualizer on http://localhost:%d/" % PORT)
        httpd.serve_forever()
