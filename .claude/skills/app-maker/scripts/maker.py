"""The App Maker's logic — imported by the App Maker server (the progress visualizer, grown, :7710).

Decisions (app-maker-vision/, round 1, 2026-09-26): D1 one server per app (app_server.py),
D2 always on, D3 the visualizer grows into the App Maker, D4 stage pages show inside it,
D5 a Talk box per stage, D6 Start buttons for each stage.

Everything is read from disk and herdr each time; nothing here is a second source of truth.
"""
import json, os, re, socket, subprocess, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
APP_SERVER = os.path.join(HERE, "app_server.py")
PANE = os.path.join(ROOT, ".claude", "scripts", "server-pane.sh")
START_AGENT = os.path.join(ROOT, ".claude", "scripts", "start-agent.sh")

# The navbar: every stage, the page that holds it, and the pipeline stage(s) whose state it shows.
STAGES = [
    ("research",    "Research",                  "research/reviewer",    "",               ["1"],  "Research"),
    ("positioning", "Positioning",               "positioning/reviewer", "",               ["2"],  "Research"),
    ("case",        "The case",                  "spec",                 "#s-summary",     ["3.1"], "PRD"),
    ("experience",  "The experience (pick v1)",  "spec",                 "#s-flow",        ["3.2"], "PRD"),
    ("canbuild",    "Can we build it?",          "spec",                 "#s-tr",          ["3.3"], "PRD"),
    ("prototype",   "Prototype v1",              "spec",                 "#s-proto",       ["3.4"], "PRD"),
    ("design",      "Design direction",          "spec",                 "#s-design_why",  ["3.5"], "PRD"),
    ("technical",   "Technical decisions",       "spec",                 "#s-overall",     ["3.6"], "PRD"),
    ("engineering", "Engineering center",        "engineering-center",   "",               ["4", "5"], "Build"),
    ("features",    "Features",                  "",                     "",               ["6"],  "After v1"),
    ("ship",        "Ship",                      "",                     "",               ["7"],  "After v1"),
]
# What pressing Start on a stage runs, in a new herdr tab in the app's workspace (model, effort, first prompt).
MODE = (" — App Maker mode (see the app-maker skill, 'Stage sessions'): your page lives in the app folder and the "
        "app's server serves it (don't start a page server); ask the user on the page with post.py, answer Talk "
        "messages with talk.py, and wait to be woken when they press Send (no watcher).")
START = {
    "positioning": ("opus", "high", "/positioning {app}" + MODE),
    "case":        ("opus", "high", "/create-prd {app} — HTML mode" + MODE),
    "design":      ("opus", "high", "/create-ui-design-direction {app}" + MODE),
    "engineering": ("opus", "high", "/code-orchestrator {app}"),
}
# Test mode: the plumbing is real (workspace, sessions, servers, questions, Send, Talk); the work is a
# few-line fake on the cheapest model, so a full run costs almost nothing.
POST = os.path.join(ROOT, ".claude", "skills", "code-orchestrator", "scripts", "post.py")
TALK = os.path.join(HERE, "talk.py")
CLI = os.path.join(HERE, "maker_cli.py")
TEMPLATE = os.path.join(ROOT, ".claude", "skills", "html-worker", "page-template.html")
MOCK_RULES = ("TEST MODE — a plumbing test of the App Maker. Do NOT run any skill, search the web, or write real "
              "content; keep every step to a few lines and every reply to one line. Make a tiny page: copy "
              f"{TEMPLATE} to <page>/index.html, set its <title> and <h1>, and put in ONE decision block (data-radio, two "
              "options) inside a data-anchor section; create <page>/state.json containing {{}}. Then post one question: "
              f"python3 {POST} <page> ask <id> \"<question>\" --option yes Yes \"mock\" --option no No \"mock\" --rec yes. "
              "Then stop. When you are woken with a round or a Talk message: post one update line with "
              f"python3 {POST} <page> update \"...\", resolve the ask (python3 {POST} <page> resolve <id>), mark comments "
              f"addressed as the prompt says, and answer any Talk message with python3 {TALK} <page> \"...\".")
MOCK = {
    "research":    "{rules} Stage: RESEARCH for '{name}'. <page> = {dir}/reviewer. Question id: build_it — 'Build {name}? (mock)'.",
    "positioning": "{rules} Stage: POSITIONING. First turn the research into an app: python3 " + CLI + " promote {app} {test_app} "
                   "— from then on the app folder is {root}/{test_app}. <page> = {root}/{test_app}/positioning/reviewer. "
                   "Question id: angle — 'Which angle? (mock)'.",
    "case":        "{rules} Stage: PRD. <page> = {dir}/spec. Question id: prd_ok — 'Is the case right? (mock)'.",
    "design":      "{rules} Stage: DESIGN DIRECTION. <page> = {dir}/design/brief. Question id: vibe — 'Pick a vibe (mock)'.",
    "engineering": "{rules} Stage: ENGINEERING CENTER — do not start workers or write code. <page> = {dir}/engineering-center. "
                   "Question id: go — 'Start the build? (mock)'.",
}
DOCS = [("PRD", "PRD.md"), ("Positioning", "positioning.md"), ("Design brief", "design/BRIEF.md"),
        ("Design handoff", "design/HANDOFF.md"), ("Clickable app", "design/clickable/app.dc.html"),
        ("Progress notes", "CLAUDE.md")]


def _open(port):
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def cfg(app_dir):
    try:
        return json.load(open(os.path.join(app_dir, ".appmaker.json")))
    except (OSError, ValueError):
        return {}


def save_cfg(app_dir, c):
    json.dump(c, open(os.path.join(app_dir, ".appmaker.json"), "w"), indent=1)


def app_server(app_dir, start=True):
    """The app's server port — started if it isn't running (D2: always on)."""
    pf = os.path.join(app_dir, ".appserver.port")
    try:
        port = int(open(pf).read().strip())
        if _open(port):
            return port
    except (OSError, ValueError):
        pass
    if not start:
        return None
    if os.path.exists(pf):
        os.remove(pf)
    cmd = f"python3 {APP_SERVER} {app_dir}"
    if os.environ.get("HERDR_ENV") == "1" and os.path.exists(PANE):
        env = dict(os.environ, **({"WS": cfg(app_dir)["workspace"]} if cfg(app_dir).get("workspace") else {}))
        subprocess.run([PANE, app_dir, cmd], capture_output=True, text=True, timeout=20, env=env)
    else:
        subprocess.Popen(cmd, shell=True, cwd=app_dir, start_new_session=True,
                         stdout=open(os.path.join(app_dir, ".appserver.log"), "a"), stderr=subprocess.STDOUT)
    for _ in range(30):
        try:
            port = int(open(pf).read().strip())
            if _open(port):
                return port
        except (OSError, ValueError):
            pass
        time.sleep(0.2)
    return None


def herdr_agents():
    try:
        out = subprocess.run(["herdr", "agent", "list"], capture_output=True, text=True, timeout=10).stdout
        return {a["name"]: a for a in json.loads(out)["result"]["agents"] if a.get("name")}
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        return {}


def _json(path, default):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def needs(app_dir, page):
    """Open questions on a page (the shared feed format: feed.json via post.py)."""
    if not page:
        return []
    items = _json(os.path.join(app_dir, page, "feed.json"), {}).get("items", [])
    return [i for i in items if (i.get("kind") == "ask" and i.get("status") == "open")
            or (i.get("kind") == "todo" and i.get("now") and i.get("status") != "done")]


def app_dirs(scan):
    """Series apps from the scan, plus research niches started from the App Maker (before app_N exists)."""
    out = [(a["id"], os.path.join(ROOT, a["id"]), a) for a in scan.get("apps", [])]
    rdir = os.path.join(ROOT, "research")
    for n in sorted(os.listdir(rdir)) if os.path.isdir(rdir) else []:
        d = os.path.join(rdir, n)
        c = cfg(d)
        if c and not c.get("moved_to"):
            out.append(("research/" + n, d, None))
    return out


def state(scan, hidden=()):
    ag = herdr_agents()
    apps = []
    for id_, d, a in app_dirs(scan):
        if id_ in hidden:
            continue
        c = cfg(d)
        research_only = a is None
        pstate = {str(s["n"]): s.get("state") for s in (a or {}).get("stages", [])}
        stages, total = [], 0
        for key, label, page, hash_, ns, group in STAGES:
            if research_only:
                page = page if key == "research" else ""
                if key == "research" and page and not os.path.isdir(os.path.join(d, page)):
                    page = "reviewer" if os.path.isdir(os.path.join(d, "reviewer")) else ""
            exists = bool(page) and os.path.isfile(os.path.join(d, page, "index.html"))
            sts = [pstate.get(n) for n in ns]
            status = ("now" if "now" in sts else "done" if sts and all(s in ("done", "skip") for s in sts) else
                      "now" if research_only and key == "research" else "")
            n = needs(d, page) if exists else []
            total += len(n)
            akey = page or ("reviewer" if research_only and key == "research" else "")
            agent = c.get("agents", {}).get(akey) if akey else None
            stages.append({"key": key, "label": label, "group": group, "page": page if exists else "",
                           "hash": hash_, "status": status, "needs": len(n),
                           "needs_text": [x.get("text", "") for x in n][:5],
                           "agent": agent, "agent_status": (ag.get(agent) or {}).get("agent_status") if agent else None,
                           "can_start": key in START and not agent})
        terminal = [{"agent": n, "tab": (ag.get(n) or {}).get("tab_id")} for n in set(c.get("agents", {}).values())
                    if (ag.get(n) or {}).get("agent_status") == "blocked"]
        docs = [{"label": l, "path": p} for l, p in DOCS if os.path.exists(os.path.join(d, p))]
        started = None
        es = _json(os.path.join(d, "engineering-center", "status.json"), {})
        started = es.get("build_started")
        names = {str(x["n"]): (x.get("name", ""), x.get("why", "")) for x in scan.get("stages", [])}
        pipeline = [{"n": s["n"], "name": names.get(str(s["n"]), ("", ""))[0], "why": names.get(str(s["n"]), ("", ""))[1],
                     "state": s.get("state"),
                     "gates": s.get("gates", []), "docs": [x.get("path") for x in s.get("docs", [])]}
                    for s in (a or {}).get("stages", [])]
        apps.append({"id": id_, "name": c.get("name") or id_, "problem": c.get("problem", ""),
                     "workspace": c.get("workspace"), "pipeline": pipeline,
                     "stage_name": (a or {}).get("stage_name") or "Research", "stages": stages,
                     "needs": total + len(terminal), "terminal": terminal, "docs": docs,
                     "port": app_server(d, start=True), "build_started": started})
    return {"apps": apps, "agents": {k: v.get("agent_status") for k, v in ag.items()}}


def talk_thread(app_id, page):
    d = os.path.join(ROOT, app_id)
    return _json(os.path.join(d, page, "talk.json"), {"messages": []})


def talk(app_id, page, text):
    d = os.path.join(ROOT, app_id)
    port = app_server(d)
    req = urllib.request.Request(f"http://127.0.0.1:{port}/{page}/api/talk", data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def start_stage(app_id, stage, mock=None):
    """D6: a Start button — opens that stage's Claude session in a new tab in the app's workspace, and records it.
    Test mode (the app's .appmaker.json has "mock": true, or mock=True) runs a few-line fake on Haiku."""
    d = os.path.join(ROOT, app_id)
    c = cfg(d)
    mock = c.get("mock") if mock is None else mock
    if stage not in (MOCK if mock else START):
        raise ValueError("this stage has no Start button")
    name = f"{os.path.basename(app_id)}-{stage}"
    if mock:
        model, effort = "haiku", "low"
        prompt = MOCK[stage].format(rules=MOCK_RULES, name=c.get("name", app_id), dir=d, app=app_id, root=ROOT,
                                    test_app=c.get("test_app", "app_99"))
    else:
        model, effort, prompt = START[stage]
        prompt = prompt.format(app=app_id)
    env = dict(os.environ, **({"WS": c["workspace"]} if c.get("workspace") else {}))
    r = subprocess.run([START_AGENT, name, d, model, effort, prompt], capture_output=True, text=True, timeout=90, env=env)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "could not start the session")
    page = next(p for k, _, p, *_ in STAGES if k == stage)
    c = cfg(d); c.setdefault("agents", {})[page] = name; save_cfg(d, c)
    return f"started {name} in the app's workspace ({model}, {effort} effort{', test mode' if mock else ''})"


def promote(src_id, app_id):
    """Research becomes an app: research/<slug>/ moves into <app_id>/research/, and its App Maker settings
    (workspace, sessions) come with it, so the card switches over instead of showing twice."""
    import shutil, signal
    src, dst = os.path.join(ROOT, src_id), os.path.join(ROOT, app_id)
    c = cfg(src)
    old = None
    try:
        old = int(open(os.path.join(src, ".appserver.port")).read().strip())
    except (OSError, ValueError):
        pass
    os.makedirs(dst, exist_ok=True)
    if os.path.exists(os.path.join(dst, "research")):
        raise ValueError(f"{app_id}/research already exists")
    shutil.move(src, os.path.join(dst, "research"))
    moved = os.path.join(dst, "research")
    for f in (".appmaker.json", ".appserver.port"):
        if os.path.exists(os.path.join(moved, f)):
            os.remove(os.path.join(moved, f))
    agents = {("research/" + k if not k.startswith(("research/", "positioning/", "spec", "design/", "engineering")) else k): v
              for k, v in c.get("agents", {}).items()}
    c.update(agents=agents, promoted_from=src_id)
    save_cfg(dst, c)
    if old:   # the research folder's server is serving a folder that moved — replace it with the app's
        out = subprocess.run(["lsof", "-ti", f"tcp:{old}", "-sTCP:LISTEN"], capture_output=True, text=True).stdout.split()
        for pid in out:
            try:
                os.kill(int(pid), signal.SIGTERM)
            except (OSError, ValueError):
                pass
    port = app_server(dst)
    return f"{src_id} is now {app_id} (server on {port})"


def new_app(name, problem, mock=False):
    """New app: its own herdr workspace (like "decorate interior app"), then research in its first tab.
    Research runs before any app_N folder exists (PIPELINE stage 1)."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug or not problem.strip():
        raise ValueError("give it a name and the problem in one line")
    d = os.path.join(ROOT, "research", slug)
    if os.path.exists(os.path.join(d, ".appmaker.json")):
        raise ValueError(f"research/{slug} already exists")
    os.makedirs(d, exist_ok=True)
    out = subprocess.run(["herdr", "workspace", "create", "--label", f"{name} app", "--cwd", ROOT, "--no-focus"],
                         capture_output=True, text=True, timeout=20)
    try:
        res = json.loads(out.stdout)["result"]
        ws, pane = res["workspace"]["workspace_id"], res["root_pane"]["pane_id"]
    except (ValueError, KeyError):
        raise RuntimeError(out.stderr.strip() or "could not create the herdr workspace")
    agent = f"{slug}-research"
    save_cfg(d, {"name": name, "problem": problem, "workspace": ws, "agents": {"reviewer": agent},
                 **({"mock": True, "test_app": "app_99"} if mock else {})})
    if mock:
        model, effort = "haiku", "low"
        prompt = MOCK["research"].format(rules=MOCK_RULES, name=name, dir=d, app=f"research/{slug}", root=ROOT, test_app="app_99")
    else:
        model, effort = "opus", "high"
        prompt = (f"/research {problem} — niche folder: research/{slug}/, review page in research/{slug}/reviewer/" + MODE)
    r = subprocess.run([START_AGENT, agent, ROOT, model, effort, prompt],
                       capture_output=True, text=True, timeout=90, env=dict(os.environ, WS=ws, PANE=pane))
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "could not start the research session")
    app_server(d)
    return f"{name}: workspace “{name} app” created in herdr, research started in its first tab"
