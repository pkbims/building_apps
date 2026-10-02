#!/usr/bin/env python3
"""Tiny localhost server for the pomodoro widget. No dependencies.

Serves index.html and persists widget state to state.json so a refresh, a
closed tab, or a restart never loses the task list or a running timer.
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state.json")
PORT = int(os.environ.get("PORT", 7799))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # keep the pane quiet
        pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    STATIC = {
        "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
        "/icon.svg": ("icon.svg", "image/svg+xml"),
    }

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/api/state"):
            try:
                with open(STATE, "rb") as f:
                    return self._send(200, f.read())
            except FileNotFoundError:
                return self._send(200, b"null")
        name, ctype = self.STATIC.get(path, ("index.html", "text/html; charset=utf-8"))
        with open(os.path.join(HERE, name), "rb") as f:
            self._send(200, f.read(), ctype)

    def do_PUT(self):
        if not self.path.startswith("/api/state"):
            return self._send(404, b"{}")
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        json.loads(body)  # reject garbage before it hits disk
        tmp = STATE + ".tmp"
        with open(tmp, "wb") as f:
            f.write(body)
        os.replace(tmp, STATE)  # atomic: never a half-written file
        self._send(200, b"{}")


if __name__ == "__main__":
    print(f"pomodoro at http://localhost:{PORT}/", flush=True)
    try:
        HTTPServer(("127.0.0.1", PORT), H).serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
