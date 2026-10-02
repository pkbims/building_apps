import re, pathlib
T = pathlib.Path("../.claude/skills/html-worker/page-template.html").read_text()

CSS = """
  .flow{display:flex;flex-direction:column;align-items:center;margin:var(--s5) 0}
  .step{position:relative;width:100%;max-width:560px;background:var(--panel);border:1px solid var(--line);
    border-radius:var(--r2);padding:var(--s4) var(--s5);text-align:center}
  .step .who{display:inline-block;font-size:11px;font-weight:650;letter-spacing:.06em;text-transform:uppercase;
    padding:2px 8px;border-radius:99px;margin-bottom:6px;background:var(--bg);color:var(--muted)}
  .step .who.you{background:var(--soft);color:var(--accent)}
  .step .h{font-weight:650;font-size:16px}
  .step .d{color:var(--muted);font-size:14px;margin-top:4px}
  .step.start,.step.end{border:2px solid var(--accent)}
  .arrow{font-size:26px;line-height:1;color:var(--accent);margin:6px 0}
  .split{display:grid;gap:var(--s3);width:100%;max-width:560px}
  .split.two{grid-template-columns:1fr 1fr} .split.three{grid-template-columns:1fr 1fr 1fr}
  .split .step{max-width:none;padding:var(--s3)}
  .loop{margin-top:8px;font-size:14px;color:var(--accent);font-weight:600}
  .rules{display:grid;gap:var(--s3);margin-top:var(--s4)}
  @media (max-width:640px){.split.three{grid-template-columns:1fr}}
"""

def step(anchor, label, who, h, d="", cls=""):
    whocls = "who you" if who == "You" else "who"
    return f'''<div class="step {cls}" data-anchor="{anchor}" data-label="{label}">
  <button class="cbtn">comment</button>
  <span class="{whocls}">{who}</span><div class="h">{h}</div>{f'<div class="d">{d}</div>' if d else ''}
</div>'''

A = '<div class="arrow">↓</div>'

def flow(*parts):
    out = []
    for i, p in enumerate(parts):
        if i: out.append(A)
        out.append(p)
    return '<div class="flow">' + "\n".join(out) + "</div>"

def split(n, *steps):
    return f'<div class="split {n}">' + "\n".join(steps) + "</div>"

def section(sid, num, title, group, intro, body):
    return f'''<section id="s-{sid}" data-anchor="{sid}" data-label="{title}" data-group="{group}" data-title="{title}">
  <button class="cbtn">comment</button>
  <h2><span class="num">{num}</span>{title}</h2>
  <p>{intro}</p>
  {body}
</section>'''


EXTRA_CSS = """
  .one{font-size:18px;font-weight:600;margin:var(--s3) 0}
  .files{display:grid;gap:var(--s3);margin-top:var(--s4)}
  .file{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:var(--s3) var(--s4)}
  .file code{font-weight:650;color:var(--accent)}
  .file .d{color:var(--muted);font-size:14px;margin-top:2px}
  .say{background:var(--quote);border-radius:var(--r);padding:var(--s3) var(--s4);font-style:italic;margin:var(--s3) 0}
  h3{margin-top:var(--s6)}
"""

def files(prefix, items):
    return '<div class="files">' + "\n".join(
        f'<div class="file" data-anchor="{prefix}{i}" data-label="file {n}"><button class="cbtn">comment</button><code>{n}</code><div class="d">{d}</div></div>'
        for i, (n, d) in enumerate(items)) + "</div>"

def rules(prefix, items):
    return '<div class="rules">' + "\n".join(
        f'<div class="plain" data-anchor="{prefix}{i}" data-label="{t}"><button class="cbtn">comment</button><b>{t}.</b> {d}</div>'
        for i, (t, d) in enumerate(items)) + "</div>"

# ---------- 0. What is a skill ----------
what = flow(
    step("w1", "Skill · folder", "The skill", "A folder with a <code>SKILL.md</code> inside",
         "Plain-English instructions for one job, plus any helper scripts or templates.", "start"),
    step("w2", "Skill · trigger", "You", "Ask for that job in normal words",
         "Or type <code>/skill-name</code>. Claude matches your request to the skill’s description."),
    step("w3", "Skill · load", "Claude", "Loads the instructions and follows them",
         "Same steps, same rules, same quality every time — no re-explaining."),
    step("w4", "Skill · result", "Result", "A repeatable result", "Written once from real work, reused forever.", "end"),
)

# ---------- 1. research ----------
r_use = flow(
    step("ru1", "Research · input", "You say", "“Research &lt;niche&gt;: &lt;problem&gt;”",
         "e.g. “Research interior decor: people can’t picture a room before they buy”", "start"),
    step("ru2", "Research · dig", "Claude", "Looks at the market",
         "Why the problem exists → every app that solves it → how each works, what it earns, whether it went viral"),
    step("ru3", "Research · listen", "Claude", "Listens to real users",
         "Pulls hundreds of real reviews and finds complaints 3+ people share"),
    step("ru4", "Research · invent", "Claude", "Proposes 1–3 new ideas",
         "Each fixes a real complaint, with its USP, “why not just use ChatGPT?”, and a shareable feature"),
    step("ru5", "Research · decide", "You", "Pick on a review page",
         "Who it’s for · which idea · what we lead with · build it or not ($10k/month rule)"),
    step("ru6", "Research · output", "You get", "A decision you can defend",
         "A review page + <code>research/&lt;niche&gt;/&lt;niche&gt;.md</code> — every claim linked to a source", "end"),
)
r_files = files("rf", [
    ("SKILL.md", "The recipe: 9 steps, the rules, and the exact shape of the output file."),
    ("scripts/play_reviews.py", "Pulls the 300 most recent Google Play reviews per app, each with its own link. The reliable source."),
    ("scripts/appstore_reviews.py", "Pulls App Store reviews. Works for some apps, not others."),
    ("scripts/verify_quotes.py", "Checks every quote in the final file exists word-for-word in the pulled reviews. Catches invented quotes."),
])
r_rules = rules("rr", [
    ("No fake quotes", "Every quote is real text, copied exactly, with a link — and a script checks it."),
    ("This year only", "Old numbers and reviews are dropped. Missing evidence is written as “no 2026 source found”."),
    ("Money is never guessed", "TrustMRR → Sensor Tower → Google → labelled estimate → otherwise “no public number”."),
    ("You make the calls", "Claude recommends; you decide who, what, and whether to build at all."),
    ("Plain English", "Short sentences, no hype words like “massive” or “game changer”."),
])

# ---------- 2. html-worker ----------
h_use = flow(
    step("hu1", "html-worker · input", "Claude", "Has something long for you to review",
         "A spec, research, options, a design — too much for terminal text", "start"),
    step("hu2", "html-worker · page", "Claude", "Builds a local web page and gives you a link",
         "From a shared template, served on your Mac (first free port from 7777)"),
    step("hu3", "html-worker · react", "You", "Click and comment on the page",
         "Tick decisions (saved instantly) · comment on any exact block (queued until you send)"),
    step("hu4", "html-worker · send", "You", "Press “Confirm &amp; send”", "Your batch lands in a file Claude reads: <code>INBOX.md</code>"),
    split("three",
          step("hk1", "html-worker · change", "Change", "Claude edits the page", "Changed blocks get an orange tag"),
          step("hk2", "html-worker · question", "Question", "Answered in the terminal", "The page stays clean"),
          step("hk3", "html-worker · comment", "Comment", "Acknowledged", "No edit unless you ask")),
    step("hu5", "html-worker · output", "You get", "A reviewed document, round by round",
         "Plus a markdown copy exported straight from the page", "end"),
)
h_files = files("hf", [
    ("SKILL.md", "The recipe: how to set up, run rounds, and the rules learned the hard way."),
    ("page-template.html", "The page itself: layout, contents rail, comment buttons, decision boxes, light/dark theme. Claude only adds content."),
    ("server.py", "A tiny local server. Saves your answers to disk and writes INBOX.md when you send."),
    ("export-md.py", "Turns the page into a markdown file, so there’s one source and never two copies."),
    ("sync.py", "Updates older pages when the template improves, without touching their content or answers."),
    ("theme-lab/", "A preview page for trying colours and fonts before changing the template."),
])
h_rules = rules("hr", [
    ("Point, don’t describe", "Comment on the exact block you mean instead of explaining where it is."),
    ("Nothing is lost", "Answers are saved to disk the moment you click; servers can die, answers can’t."),
    ("You control sending", "Comments wait in a queue you can edit or delete before sending."),
    ("Any content", "It’s only the mechanics. Research, PRDs, designs — all use the same page."),
])

together = flow(
    step("t1", "Together · research", "research", "Decides <i>what</i> to show", "Evidence, ideas and decisions", "start"),
    step("t2", "Together · html-worker", "html-worker", "Decides <i>how</i> you review it", "A clickable page instead of terminal text"),
    step("t3", "Together · result", "Result", "You review research by clicking, not scrolling", "Then it moves on to stage 2, positioning.", "end"),
)

main = "\n".join([
    section("skill", 1, "First: what is a skill?", "Start", "A skill is a saved how-to that Claude follows whenever the job comes up.", what),
    section("research", 2, "research", "Skills",
            '<span class="one">Finds out if an app idea is worth building — before any code.</span>'
            '<br><b>Why it exists:</b> most app ideas die because someone already solves it, or nobody pays for it. This checks both with real evidence first.',
            '<div class="say">Say: “Research meal planning: people waste food they forgot they bought”</div>'
            '<h3>How it works</h3>' + r_use + '<h3>What’s inside the skill</h3>' + r_files + '<h3>What makes it trustworthy</h3>' + r_rules),
    section("htmlworker", 3, "html-worker", "Skills",
            '<span class="one">Turns anything long into a web page you review by clicking and commenting.</span>'
            '<br><b>Why it exists:</b> reading and replying to long answers in a terminal is slow. Pointing at the exact part you mean is faster.',
            '<div class="say">Say: “Show me this on a review page” — or other skills use it automatically</div>'
            '<h3>How it works</h3>' + h_use + '<h3>What’s inside the skill</h3>' + h_files + '<h3>Its rules</h3>' + h_rules),
    section("together", 4, "How they fit together", "Skills", "research is the content; html-worker is the screen you review it on.", together),
])

out = T.replace("TITLE HERE", "Your skills, explained")
out = re.sub(r"<main>.*?</main>", lambda m: "<main>\n" + main + "\n</main>", out, flags=re.S)
out = out.replace("</style>", CSS + EXTRA_CSS + "</style>", 1)
pathlib.Path("index.html").write_text(out)
print("ok", out.count("<div"), out.count("</div>"))
