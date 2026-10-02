"""Builds index.html — a picture of the App Maker idea (brainstorm, 2026-09-26). Nothing is built.
Run: python3 build.py   (the page server reads index.html from disk; no restart needed)."""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
T = open(os.path.join(HERE, "..", ".claude", "skills", "html-worker", "page-template.html")).read()
E = html.escape


def section(id, num, title, body, group="The idea"):
    return (f'<section id="s-{id}" data-anchor="{id}" data-label="{E(title)}" data-group="{group}" data-title="{E(title)}">'
            f'<button class="cbtn">comment</button><h2><span class="num">{num}</span>{E(title)}</h2>{body}</section>')


def decision(id, q, why, opts):
    """opts: (value, head, what, get, when, rec)"""
    o = "".join(
        f'<label class="opt"><input type="radio" name="{id}" value="{v}"><span><span class="oh">{E(h)}'
        f'{" <span class=rec>recommended</span>" if rec else ""}</span><span class="od"><b>What it is:</b> {E(w)}<br>'
        f'<b>What you get / what it costs:</b> {E(g)}<br><b>Pick it when:</b> {E(wh)}</span></span></label>'
        for v, h, w, g, wh, rec in opts)
    return (f'<div class="d open" data-anchor="{id}" data-label="{id.upper()} {E(q)}"><button class="cbtn">comment</button>'
            f'<div class="q">{id.upper()} — {E(q)}</div><div class="why">{E(why)}</div><div data-radio="{id}">{o}</div></div>')


CSS = """<style>
  .rec{font-size:10.5px;font-weight:800;color:var(--accent);text-transform:uppercase;letter-spacing:.05em;margin-left:6px}
  .layers{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:10px 0}
  @media(max-width:800px){.layers{grid-template-columns:1fr}}
  .layer{border:2px solid var(--line);border-radius:14px;padding:14px;background:var(--bg)}
  .layer h3{margin:0 0 4px;font-size:15px} .layer .port{font:600 11.5px ui-monospace,monospace;color:var(--muted)}
  .layer ul{margin:8px 0 0 16px;padding:0;font-size:13px} .layer li{margin:3px 0}
  .layer.mc{border-color:#8a8a8a} .layer.am{border-color:var(--accent)} .layer.ap{border-color:#3b82f6}
  .arrow{text-align:center;font-size:13px;color:var(--muted);margin:4px 0}
  .srvs{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:10px 0}
  @media(max-width:800px){.srvs{grid-template-columns:1fr}}
  .srvbox{border:1px solid var(--line);border-radius:12px;padding:12px;background:var(--bg);font-size:13px}
  .srvbox h4{margin:0 0 8px;font-size:14px}
  .srv{display:flex;justify-content:space-between;border:1px solid var(--line);border-radius:8px;padding:5px 9px;margin:4px 0;background:var(--panel)}
  .srv code{font-size:11.5px;color:var(--muted)}
  .srv.one{border:2px solid #3b82f6}
  /* mock-ups */
  .mock{border:2px solid #141414;border-radius:14px;overflow:hidden;margin:12px 0;background:var(--panel);font-size:13px}
  .mock .bar{display:flex;align-items:center;gap:10px;padding:8px 12px;background:#141414;color:#fff;font-size:12.5px}
  .mock .bar b{font-size:14px} .mock .bar .sp{flex:1}
  .mock .bar select{font:inherit;font-size:12px;border-radius:6px;padding:2px 6px}
  .notif{display:flex;gap:8px;flex-wrap:wrap;padding:8px 12px;background:color-mix(in srgb,#e0672c 12%,var(--panel));border-bottom:1px solid var(--line)}
  .nchip{border-radius:999px;padding:4px 10px;font-weight:700;font-size:12px;background:#e0672c;color:#fff;cursor:pointer}
  .nchip.term{background:#141414} .nchip.calm{background:var(--soft);color:var(--muted);font-weight:600}
  .mbody{display:flex;min-height:300px}
  .nav{width:210px;flex:none;border-right:1px solid var(--line);padding:10px 8px;background:var(--bg)}
  .nav .g{font:700 10.5px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:10px 6px 4px}
  .nav a{display:flex;align-items:center;gap:7px;padding:5px 8px;border-radius:7px;color:var(--ink);text-decoration:none;font-size:12.5px;cursor:pointer}
  .nav a:hover{background:var(--soft)} .nav a.on{background:var(--soft);font-weight:700}
  .nav a i{width:8px;height:8px;border-radius:50%;flex:none;background:var(--faint)}
  .nav a i.done{background:#22a55a} .nav a i.now{background:#3b82f6} .nav a i.wait{background:#e0672c}
  .nav a em{margin-left:auto;font-style:normal;background:#e0672c;color:#fff;border-radius:999px;font-size:10.5px;font-weight:800;padding:1px 6px}
  .main{flex:1;padding:14px 16px}
  .main .crumb{font-size:11.5px;color:var(--muted);margin-bottom:6px}
  .frame{border:1px dashed var(--line);border-radius:10px;padding:12px;background:var(--bg);min-height:180px}
  .ask{border-left:4px solid #e0672c;background:var(--panel);border-radius:8px;padding:10px 12px;margin-top:8px}
  .talk{display:flex;gap:6px;margin-top:10px} .talk input{flex:1;font:inherit;font-size:12.5px;padding:6px 9px;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--ink)}
  .talk button,.btnm{font:inherit;font-size:12px;font-weight:700;padding:6px 11px;border:0;border-radius:8px;background:var(--accent);color:#fff}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;padding:12px}
  .card{border:1px solid var(--line);border-radius:12px;padding:12px;background:var(--bg)}
  .card h4{margin:0;font-size:15px} .card .st{font-size:12px;color:var(--muted);margin:2px 0 8px}
  .segs{display:flex;gap:2px;margin:6px 0} .segs i{flex:1;height:7px;border-radius:2px;background:var(--soft)}
  .segs i.sd{background:#22a55a} .segs i.sn{background:#3b82f6}
  .card .need{font-size:12px;font-weight:700;color:#e0672c}
  .card.new{display:grid;place-items:center;border-style:dashed;color:var(--accent);font-weight:800;font-size:15px;min-height:110px}
  .flow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:10px 0;font-size:12.5px}
  .flow span{border:1px solid var(--line);border-radius:8px;padding:6px 9px;background:var(--bg)}
  .flow b{color:var(--muted)}
</style>"""

STAGES = [("Research", "done"), ("Positioning", "done"), ("PRD", None),
          ("3.1 The case", "done"), ("3.2 The experience", "done"), ("3.3 Can we build it?", "done"),
          ("3.4 Prototype v1", "done"), ("3.5 Design direction", "done"), ("3.6 Technical decisions", "done"),
          ("Build", None), ("Engineering center", "now"), ("Features", ""), ("Ship", "")]


def nav(active, badges, upto=None):
    """upto: the stage the app is on — stages before it are done, later ones not started."""
    out = ""
    names = [n for n, s in STAGES if s is not None]
    for name, st in STAGES:
        if st is not None and upto:
            i, j = names.index(name), names.index(upto)
            st = "done" if i < j else "now" if i == j else ""
        if st is None:
            out += f'<div class="g">{E(name)}</div>'
            continue
        b = badges.get(name)
        out += (f'<a class="{"on" if name == active else ""}"><i class="{"done" if st == "done" else "now" if st == "now" else "wait" if b else ""}"></i>'
                f'{E(name)}{f"<em>{b}</em>" if b else ""}</a>')
    return f'<div class="nav"><div class="g">app_1 · Homi</div>{out}<div class="g">Documents</div><a>PRD.md</a><a>Design handoff</a><a>Clickable app</a></div>'


H = []
H.append(section("idea", 1, "The idea in one picture",
 '<p class="plain"><b>One home page for making apps.</b> Every app gets <b>one server</b> that serves all of its pages — research, positioning, the PRD, the prototype, the engineering center. The <b>App Maker</b> is a separate home page that lists your apps, shows what needs you, and opens any stage. The <b>Monitoring center</b> stays on its own: it watches the machine, not the apps.</p>'
 '<div class="layers">'
 '<div class="layer mc"><h3>Monitoring center</h3><div class="port">stays as it is · :7700</div><ul><li>Every server on this Mac</li><li>Start, restart, stop</li><li>Later: CPU and memory</li></ul></div>'
 '<div class="layer am"><h3>App Maker</h3><div class="port">the home page · its own server</div><ul><li>Your apps, and where each stands</li><li>“Needs you” across all apps</li><li><b>New app</b> button</li><li>Replaces the progress visualizer</li></ul></div>'
 '<div class="layer ap"><h3>One server per app</h3><div class="port">app_1 · app_2 · …</div><ul><li>Serves every page of that app</li><li>One ticker: wakes the right Claude</li><li>Started when you open the app</li></ul></div>'
 '</div><p class="arrow">You live in the App Maker. It opens the app’s pages; the app’s server does the work. The monitoring center is for when something on the machine is wrong.</p>'))

H.append(section("servers", 2, "Fewer servers",
 '<p class="sub">What app_1 alone runs today, and what it would run.</p><div class="srvs">'
 '<div class="srvbox"><h4>Today — one server per page</h4>'
 '<div class="srv">research page <code>:7778</code></div><div class="srv">positioning page <code>:7779</code></div>'
 '<div class="srv">PRD page <code>:7780</code></div><div class="srv">design brief <code>:7781</code></div>'
 '<div class="srv">engineering center <code>:7782</code></div><div class="srv">clickable app <code>:7783</code></div>'
 '<div class="srv">progress visualizer <code>:7710</code></div><div class="srv">+ a ticker, + watchers inside Claude sessions</div></div>'
 '<div class="srvbox"><h4>The idea</h4>'
 '<div class="srv one">app_1 server — <code>/research · /positioning · /prd · /prototype · /design · /engineering</code></div>'
 '<div class="srv one">its one ticker (wakes the right Claude session)</div>'
 '<div class="srv">App Maker home <code>one port</code></div><div class="srv">Monitoring center <code>:7700</code></div>'
 '<p class="sub" style="margin-top:8px">Per app: 7 servers → 1. And the app’s server can stop when you haven’t opened it for a while.</p></div></div>'))

HOME = ('<div class="mock"><div class="bar"><b>App Maker</b><span class="sp"></span><span>Needs you: 3</span></div>'
        '<div class="notif"><span class="nchip">app_1 · Engineering center needs you (1)</span><span class="nchip">app_2 · Research needs you (2)</span><span class="nchip calm">practice_3 — nothing</span></div>'
        '<div class="cards">'
        '<div class="card"><h4>app_1 · Homi</h4><div class="st">Building v1 · 10h 10m</div><div class="segs">' + '<i class="sd"></i>' * 9 + '<i class="sn"></i><i></i><i></i></div><div class="need">1 question</div></div>'
        '<div class="card"><h4>app_2 · …</h4><div class="st">Research</div><div class="segs"><i class="sn"></i>' + '<i></i>' * 11 + '</div><div class="need">2 questions</div></div>'
        '<div class="card new">+ New app<br><span style="font-size:12px;font-weight:500;color:var(--muted)">the problem, in one line</span></div>'
        '</div></div>')
APP = ('<div class="mock"><div class="bar"><b>App Maker</b><span>›</span><select><option>app_1 · Homi</option><option>app_2</option></select><span class="sp"></span><span>⏱ 10h 10m</span></div>'
       '<div class="notif"><span class="nchip">Engineering center needs you (1)</span><span class="nchip term">Terminal: the ios tab is waiting for a permission — open it and approve</span></div>'
       '<div class="mbody">' + nav("Engineering center", {"Engineering center": 1}) +
       '<div class="main"><div class="crumb">app_1 › Build › Engineering center</div><div class="frame"><b>(the engineering center page, as it is today)</b>'
       '<div class="ask"><b>Where should errors from the server and the app go?</b><br><span style="color:var(--muted)">○ Sentry, free plan <span class="rec">recommended</span> · ○ Only our own logs</span></div>'
       '<div class="talk"><input placeholder="Talk to Claude about this stage…"><button>Send</button></div></div></div></div></div>')
RESEARCH = ('<div class="mock"><div class="bar"><b>App Maker</b><span>›</span><select><option>app_2</option></select><span class="sp"></span></div>'
            '<div class="notif"><span class="nchip">Research needs you (2)</span></div>'
            '<div class="mbody">' + nav("Research", {"Research": 2}, upto="Research").replace("app_1 · Homi", "app_2") +
            '<div class="main"><div class="crumb">app_2 › Research</div><div class="frame"><b>(the research page, as it is today)</b>'
            '<div class="ask"><b>Build it?</b> One app earns $10k+ a month (TrustMRR).<br><span style="color:var(--muted)">○ Yes, build it <span class="rec">recommended</span> · ○ No, archive it</span></div>'
            '<div class="ask"><b>Research asks:</b> which of these 3 quotes should anchor the positioning? (answer by comment)</div>'
            '<div class="talk"><input placeholder="Talk to Claude about this stage…"><button>Send</button></div>'
            '<p style="margin-top:10px"><span class="btnm">Research done → start positioning</span></p></div></div></div></div>')
H.append(section("mock-home", 3, "Mock-up: the App Maker home", '<p class="sub">Your apps as cards: the stage, a bar of all stages, and how many questions wait. One line across the top gathers every “needs you”.</p>' + HOME, "Mock-ups"))
H.append(section("mock-app", 4, "Mock-up: inside one app", '<p class="sub">The navbar on the left is every stage — the same list as the pipeline. Green done, blue now, orange needs you. The page on the right is the stage’s existing html-worker page, unchanged. A black chip means a Claude session needs you in the terminal, and says exactly where.</p>' + APP, "Mock-ups"))
H.append(section("mock-research", 5, "Mock-up: a stage asking you", '<p class="sub">The same loop as the engineering center, in research: questions with a recommended answer, a “talk to Claude” box for anything else, and a button to move on to the next stage.</p>' + RESEARCH, "Mock-ups"))

H.append(section("loop", 6, "How a question reaches you and comes back",
 '<div class="flow"><span>Claude (research session)</span><b>posts a question →</b><span>app_2’s server</span><b>→</b><span>App Maker: “Research needs you (2)” + a Mac notification</span></div>'
 '<div class="flow"><span>You answer on the page</span><b>→</b><span>app_2’s server saves it</span><b>→ the ticker sees it →</b><span>wakes the research session through herdr</span><b>→</b><span>its reply appears on the page</span></div>'
 '<p class="sub">The same way the engineering center already works. The difference: every stage uses it, so no stage needs you to type “sent” or open the terminal.</p>', "How it works"))

H.append(section("terminal", 7, "When you still need the terminal — and how you'd know",
 '<table class="t"><tr><th>Moment</th><th>How the App Maker tells you</th></tr>'
 '<tr><td>A Claude session waits for a permission, or its login expired</td><td>herdr shows it as waiting → a black chip: “Terminal: the <b>ios</b> tab needs you — approve a permission”</td></tr>'
 '<tr><td>Claude needs you to run a command (e.g. <code>gh auth login</code>)</td><td>An ask with the exact command and the tab</td></tr>'
 '<tr><td>First-time setup (herdr, Claude login, keys)</td><td>A checklist on the App Maker’s first launch</td></tr>'
 '<tr><td>Improving the App Maker itself</td><td>Not a notification — that’s you choosing to work on the tool</td></tr></table>', "How it works"))

H.append(section("decisions", 8, "Decisions",
 decision("d1", "How does one app's server serve all its pages?", "Today each page has its own server.", [
  ("paths", "One server, one path per page", "app_1’s server serves /research, /prd, /engineering… from the folders that exist today.", "One port per app; the pages don’t change; answers for all pages live in the app’s folder.", "always — the default.", True),
  ("proxy", "Keep a server per page, behind one front door", "The app server forwards each path to today’s page servers.", "No change to page servers; still many processes and memory.", "moving everything at once is too risky.", False)]) +
 decision("d2", "When does an app's server run?", "Your Mac was short on memory today.", [
  ("ondemand", "Started when you open the app; stops after an idle while", "The App Maker starts it; it stops itself after, say, an hour unused — unless a build is running.", "Only busy apps use memory; opening an old app takes a second or two.", "the default.", True),
  ("always", "Always on", "Every app’s server runs all the time.", "Instant; memory grows with every app.", "you only ever have one or two apps.", False)]) +
 decision("d3", "Where does the App Maker live?", "The progress visualizer already knows the stages and every document.", [
  ("evolve", "Grow the progress visualizer into the App Maker", "Same port (:7710), it gains the navbar, the notification line, and New app.", "Nothing to migrate; one less thing to run.", "the default.", True),
  ("new", "A new App Maker beside the visualizer", "A new server and port; the visualizer stays.", "A clean start; two overlapping pages.", "the visualizer should stay a read-only report.", False)]) +
 decision("d4", "How does a stage's page appear inside the App Maker?", "The pages are the work — they shouldn't be rebuilt.", [
  ("frame", "Inside the App Maker, next to the navbar", "The stage page shows in the right-hand area; the navbar and notifications stay visible.", "You never lose your place; pages unchanged.", "the default.", True),
  ("tab", "A new browser tab", "The navbar links open each page in its own tab.", "Simplest; you lose the navbar and notifications on that tab.", "you prefer many tabs.", False)]) +
 decision("d5", "How does free-form talk work?", "Some of the best turns were open conversation, like this brainstorm.", [
  ("perstage", "A “Talk to Claude” box on every stage", "Your message goes to that stage’s Claude session; its reply appears on the page.", "The terminal isn’t needed for thinking out loud.", "the default.", True),
  ("terminal", "Keep free-form talk in the terminal", "Pages for decisions, terminal for conversation.", "Nothing to build; you still switch windows.", "you like the terminal for thinking.", False)]) +
 decision("d6", "Who starts each stage's Claude session?", "Today you type the skill in the terminal.", [
  ("button", "A button: “Start research”, “Start positioning”, …", "The App Maker opens a herdr session for that stage and runs its skill.", "No commands to remember; a fresh session per stage.", "the default.", True),
  ("manual", "You start them in the terminal", "As today.", "Full control; the thing we're trying to remove.", "you want to watch every session start.", False)]), "Decisions"))

H.append(section("not", 9, "What this is not",
 '<ul><li><b>Not rebuilding the pages.</b> Research, positioning, the PRD and the engineering center stay html-worker pages.</li>'
 '<li><b>Not replacing the monitoring center.</b> It stays separate — the machine, not the apps.</li>'
 '<li><b>Not built now.</b> This page is only the picture. When we build it, the next app is the first one made entirely from the App Maker.</li></ul>', "Decisions"))

body = CSS + "\n".join(H)
a = T.index("<!--\n  CONTENT GOES HERE"); b = T.index("-->", a) + 3
page = T[:a] + body + T[b:]
page = page.replace("<title>TITLE HERE</title>", "<title>App Maker — the idea</title>", 1).replace("<h1>TITLE HERE</h1>", "<h1>App Maker — the idea</h1>", 1)
open(os.path.join(HERE, "index.html"), "w").write(page)
print("built", len(page))
