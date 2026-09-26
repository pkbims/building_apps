#!/usr/bin/env python3
"""Set up (or refresh) an app's build room and start its server and ticker.

    setup.py <app_dir> [--orchestrator code-orchestrator] [--workers backend,ios] [--interval 300]

<app>/build-room/ is an html-worker page: index.html (template + room-body.html), the
html-worker server.py, feed.json (written by post.py), status.json (written by ticker.py).
Idempotent: re-running rebuilds index.html and starts only what isn't running.
Prints the URL.
"""
import argparse, json, os, shutil, socket, subprocess, time

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(SKILL, "..", "..", ".."))
HW = os.path.join(ROOT, ".claude", "skills", "html-worker")
PANE = os.path.join(ROOT, ".claude", "scripts", "server-pane.sh")


def listening(port):
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def alive(pidfile):
    try:
        os.kill(int(open(pidfile).read().strip()), 0)
        return True
    except (OSError, ValueError):
        return False


def run_in_pane(cwd, cmd):
    if os.environ.get("HERDR_ENV") == "1" and os.path.exists(PANE):
        subprocess.run([PANE, cwd, cmd], check=True, capture_output=True, text=True)
    else:
        subprocess.Popen(cmd, shell=True, cwd=cwd, start_new_session=True,
                         stdout=open(os.path.join(cwd, "room.log"), "a"), stderr=subprocess.STDOUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("app")
    ap.add_argument("--orchestrator", default="code-orchestrator")
    ap.add_argument("--workers", default="backend,ios")
    ap.add_argument("--interval", type=int, default=300)
    x = ap.parse_args()
    app = os.path.abspath(x.app)
    name = os.path.basename(app)
    room = os.path.join(app, "build-room")
    os.makedirs(room, exist_ok=True)

    shutil.copy(os.path.join(HW, "server.py"), os.path.join(room, "server.py"))
    t = open(os.path.join(HW, "page-template.html")).read()
    body = open(os.path.join(SKILL, "room-body.html")).read()
    a = t.index("<!--\n  CONTENT GOES HERE")
    b = t.index("-->", a) + 3
    page = t[:a] + body + t[b:]
    page = page.replace("<title>TITLE HERE</title>", f"<title>Build room — {name}</title>", 1)
    page = page.replace("<h1>TITLE HERE</h1>", f"<h1>Build room — {name}</h1>", 1)
    page = page.replace("Confirm &amp; send", "Send to the orchestrator", 1)
    page = page.replace("`Confirm & send round ${ROUND}`", "`Send to the orchestrator`", 1)
    open(os.path.join(room, "index.html"), "w").write(page)
    for f, init in (("feed.json", {"items": []}), ("status.json", {})):
        p = os.path.join(room, f)
        if not os.path.exists(p):
            json.dump(init, open(p, "w"))

    port_file = os.path.join(room, ".port")
    up = os.path.exists(port_file) and listening(int(open(port_file).read().strip() or 0))
    if not up:
        if os.path.exists(port_file):
            os.remove(port_file)
        run_in_pane(room, "python3 server.py")
        for _ in range(50):
            if os.path.exists(port_file) and listening(int(open(port_file).read().strip() or 0)):
                break
            time.sleep(0.2)
    if not alive(os.path.join(room, ".ticker.pid")):
        run_in_pane(room, f"python3 {os.path.join(SKILL, 'scripts', 'ticker.py')} {room} --app {app} "
                          f"--orchestrator {x.orchestrator} --workers {x.workers} --interval {x.interval}")
    port = open(port_file).read().strip() if os.path.exists(port_file) else "?"
    print(f"http://localhost:{port}/")


if __name__ == "__main__":
    main()
