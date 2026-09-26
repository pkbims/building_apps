#!/usr/bin/env python3
"""Derive every app's progress from what is on disk. Nothing here is hand-maintained:
files present, state.json round/decision counts, and git history are the only sources.

The model it produces is the one settled on the app-maker-review page (D1-D18):
thirteen stages (the spec split into its six PRD parts, 3.1–3.6), v1 as a closed milestone, features as a repeating stage below it,
side work nested under the stage it happened during.
"""

import json
import os
import re
import subprocess
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

STAGES = [
    (1,    "Research",         "Why the problem exists, who solves it, what they earn — build it or not"),
    (2,    "Set up + Positioning", "The repo, then one paragraph, a USP and a viral feature"),
    ("3.1", "The case",         "Why it's worth building, and the rules the app must follow"),
    ("3.2", "The experience (pick v1)", "v1's features, the flow, the screens"),
    ("3.3", "Can we build it?", "How it works — the riskiest bets tested before any design"),
    ("3.4", "Prototype v1",     "Tap through v1 on the phone, including the shareable moment"),
    ("3.5", "Design direction", "A prompt for Claude Design, and the design brought back"),
    ("3.6", "Technical decisions", "The choices behind the build — ends on the hand-over"),
    (4,    "Contract freeze",  "Lock the API so two workers can build at once"),
    (5,    "Build v1",         "Three sessions; ends when v1 is on TestFlight"),
    (6,    "Features",         "The stage you re-enter"),
    (7,    "Ship",             "App Store release, then the showcase site"),
]

MERGE = re.compile(r"^Merge\s+(\w[\w-]*)\s+into\s+main\s+[—-]\s+(.+)$")
BACKMERGE = re.compile(r"^Merge\s+branch\s+'main'")


def sh(args, cwd):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=15)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def app_dirs():
    out = []
    for n in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, n)
        if re.fullmatch(r"app_\d+", n) and os.path.isdir(p):
            out.append((n, p))
    return out


def review_pages(app):
    """Every html-worker page under an app: index.html + state.json side by side."""
    pages = []
    for cur, dirs, files in os.walk(app):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "vendor", ".venv")]
        if "index.html" in files and "state.json" in files:
            try:
                st = json.load(open(os.path.join(cur, "state.json")))
            except (json.JSONDecodeError, OSError):
                continue
            rel = os.path.relpath(cur, app)
            title = page_title(os.path.join(cur, "index.html"))
            batches = st.get("batches", [])
            pages.append({
                "id": rel.replace("/", "__"), "dir": rel, "title": title or rel,
                "kind": "html-worker",
                "rounds": len(batches), "decisions": len(st.get("decisions", {})),
                "comments": len(st.get("comments", [])),
                "completed": bool(st.get("completed")),
                "first": batches[0]["ts"][:10] if batches else None,
                "last": batches[-1]["ts"][:10] if batches else None,
                "mtime": datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(cur, "index.html"))).strftime("%Y-%m-%d"),
            })
    return sorted(pages, key=lambda p: p["last"] or p["mtime"])


def page_title(path):
    try:
        m = re.search(r"<title>([^<]*)</title>", open(path, errors="ignore").read(4000))
        return m.group(1).strip() if m else ""
    except OSError:
        return ""


def standalone_html(app, pages):
    """HTML documents that are not html-worker pages: a teardown written as a page, a
    prototype, a mockup, the variant sheets beside a review. They carry no state.json,
    so the page scan misses them — but they were built to be read, and they open fine."""
    page_index = {os.path.join(p["dir"], "index.html") for p in pages}
    out = []
    for cur, dirs, files in os.walk(app):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "vendor", ".venv")]
        for f in sorted(files):
            if not f.endswith(".html") or f == "reading-copy.html":
                continue
            rel = os.path.relpath(os.path.join(cur, f), app)
            if rel in page_index:
                continue
            out.append({"path": rel, "dir": os.path.relpath(cur, app),
                        "title": page_title(os.path.join(cur, f)) or f})
    return out


def git_history(app):
    """Commits oldest-first, plus the feature merges into main."""
    raw = sh(["git", "log", "--format=%H|%ad|%s", "--date=short", "--reverse"], app)
    commits = []
    for line in raw.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            commits.append({"sha": parts[0][:8], "date": parts[1], "subject": parts[2]})
    return commits


def norm_feature(name):
    """Two merges of the same feature (backend side, iOS side) collapse to one name."""
    n = name.strip().lower()
    n = re.sub(r"\s*\((?:[^)]*)\)\s*$", "", n)
    n = re.sub(r",?\s*(ios|backend|client|web)\s+side\s*$", "", n)
    n = re.sub(r"^the\s+", "", n)
    n = re.sub(r"[—-]\s*", " ", n)
    return re.sub(r"\s+", " ", n).strip(" .,")


def v1_boundary(commits, app):
    """The day v1 ended. A `v1` git tag is authoritative; otherwise the busiest
    build day is used and the page says it was inferred.

    An app only has a v1 once there is build evidence — worker briefs or a frozen
    contract — and at least one worker branch merged into main. Without that, the
    busiest day is just the day you wrote the research."""
    if not (has(app, "backend/AGENT.md") or has(app, "contract/openapi.json")):
        return None, None
    if not any(MERGE.match(c["subject"]) for c in commits):
        return None, None
    tag = sh(["git", "log", "-1", "--format=%ad", "--date=short", "v1"], app).strip()
    if tag:
        return tag, "tag"
    if not commits:
        return None, None
    counts = {}
    for c in commits:
        counts[c["date"]] = counts.get(c["date"], 0) + 1
    busiest = max(counts, key=lambda d: (counts[d], d))
    return busiest, "inferred"


STOP = {"the", "a", "an", "in", "to", "into", "and", "of", "for", "on", "with", "fix",
        "fixes", "main", "side", "new", "up", "it", "is", "all", "from", "plus"}


def tokens(name):
    return {t for t in re.findall(r"[a-z0-9]+", name) if t not in STOP}


def overlap(ta, tb):
    """Shared significant words, counting shop/shopping and design/redesign as shared."""
    n = 0
    for x in ta:
        for y in tb:
            if x == y or (len(x) >= 4 and len(y) >= 4 and (x.startswith(y) or y.startswith(x) or x in y or y in x)):
                n += 1
                break
    return n


def same_feature(a, b):
    """Two merge names describe one feature if their significant words mostly overlap."""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / min(len(ta), len(tb)) >= 0.5


def features_of(commits, v1_end):
    """Derived from merge commits into main after v1 (D14)."""
    feats, order = {}, []
    for c in commits:
        if BACKMERGE.match(c["subject"]):
            continue
        m = MERGE.match(c["subject"])
        if not m:
            continue
        if v1_end and c["date"] <= v1_end:
            continue
        key = norm_feature(m.group(2))
        if not key:
            continue
        for k in order:
            if k != key and same_feature(key, k):
                key = k
                break
        if key not in feats:
            feats[key] = {"name": m.group(2).strip(), "key": key, "halves": set(),
                          "first": c["date"], "last": c["date"], "merges": 0, "docs": []}
            order.append(key)
        f = feats[key]
        f["halves"].add(m.group(1))
        f["last"] = c["date"]
        f["merges"] += 1
    out = []
    for i, k in enumerate(order, 1):
        f = feats[k]
        f["halves"] = sorted(f["halves"])
        f["id"] = "F%d" % i
        out.append(f)
    return out


def date_gap(page, start, end):
    """Days between a review page's activity and a feature's merge window.
    0 means it happened during the feature; None means one of the dates is missing."""
    d = page["last"] or page["mtime"]
    if not (d and start):
        return None
    try:
        dd = datetime.strptime(d, "%Y-%m-%d")
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end or start, "%Y-%m-%d")
    except ValueError:
        return None
    if s <= dd <= e:
        return 0
    return min(abs((dd - s).days), abs((dd - e).days))


def has(app, *rel):
    return any(os.path.exists(os.path.join(app, r)) for r in rel)


def contains(app, rel, needle):
    try:
        return needle.lower() in open(os.path.join(app, rel), errors="ignore").read().lower()
    except OSError:
        return False


def glob_md(app, sub):
    d = os.path.join(app, sub)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".md"))


def doc(path, kind, title=None):
    return {"id": path.replace("/", "__"), "path": path, "kind": kind,
            "title": title or os.path.basename(path)}


def orch_questions(app):
    p = os.path.join(app, "ORCH-QUESTIONS.md")
    if not os.path.exists(p):
        return None
    txt = open(p, errors="ignore").read()
    total = len(re.findall(r"^#+\s*Q\d+", txt, re.M))
    answered = len(re.findall(r"^\*{0,2}Answer", txt, re.M)) or len(re.findall(r"Answer:", txt))
    return {"total": total, "answered": min(answered, total)}


def build_app(name, app):
    pages = review_pages(app)
    extras = standalone_html(app, pages)
    taken = set()

    # An HTML file living inside a review page's folder belongs to that review — the
    # variant sheets and prototypes beside options_review are part of it, not loose
    # documents. They hang off the page instead of cluttering the stage.
    for e in extras:
        owner = None
        for p in pages:
            if e["dir"] == p["dir"] or e["dir"].startswith(p["dir"] + "/"):
                if owner is None or len(p["dir"]) > len(owner["dir"]):
                    owner = p
        if owner is not None:
            owner.setdefault("extras", []).append({"path": e["path"], "title": e["title"]})
            taken.add(e["path"])

    def extras_under(*prefixes):
        """Standalone HTML whose folder sits under one of these paths."""
        got = []
        for e in extras:
            if e["path"] in taken:
                continue
            d = e["dir"] if e["dir"] != "." else ""
            if any(d == p or d.startswith(p + "/") or (p == "" and d == "") for p in prefixes):
                taken.add(e["path"])
                got.append(doc(e["path"], "html", e["title"]))
        return got

    commits = git_history(app)
    v1_end, v1_src = v1_boundary(commits, app)
    feats = features_of(commits, v1_end)
    used = set()

    # Attach a review page to a feature by NAME, with date as the tiebreak. Several
    # features merge on the same day, so dates alone give the first one everything;
    # `ui_design_v2` belongs to "visual redesign v2" because the words match.
    for p in pages:
        cands = []
        ptok = tokens(p["dir"].replace("_", " ").replace("/", " ").lower()) | tokens(p["title"].lower())
        for f in feats:
            score = overlap(ptok, tokens(f["key"]))
            if not score:
                continue
            gap = date_gap(p, f["first"], f["last"])
            if gap is None or gap > 3:
                continue
            cands.append((-score, gap, f))
        if cands:
            cands.sort(key=lambda c: (c[0], c[1]))
            f = cands[0][2]
            f["docs"].append(p["id"])
            used.add(p["id"])

    research_md = glob_md(app, "research")
    ci = os.path.join(app, ".github", "workflows")
    ci_files = sorted(os.listdir(ci)) if os.path.isdir(ci) else []
    oq = orch_questions(app)
    v1_commits = len([c for c in commits if v1_end and c["date"] <= v1_end])

    def page_by_dir(prefix):
        return [p for p in pages if p["dir"].startswith(prefix)]

    stages = []

    # 1 Research
    d = [doc("research/" + f, "markdown") for f in research_md]
    d += [doc(p["dir"], "html-worker", p["title"]) for p in page_by_dir("research")]
    d += extras_under("research")
    for p in page_by_dir("research"):
        used.add(p["id"])
    stages.append({"n": 1, "docs": d, "gates": [
        ["research file written", bool(research_md), research_md[0] if research_md else ""],
        ["reviewed on a page", bool(page_by_dir("research")), ""],
        ["build-it decision recorded",
         any(contains(app, "research/" + f, "worth building") for f in research_md), ""]]})

    # 2 Set up + Positioning — the positioning skill's review page lives in positioning/,
    # so work in progress shows before positioning.md is saved.
    pos_pages = page_by_dir("positioning")
    for p in pos_pages:
        used.add(p["id"])
    d = [doc(p["dir"], "html-worker", p["title"]) for p in pos_pages]
    if has(app, "positioning.md"):
        d.append(doc("positioning.md", "markdown"))
    d += extras_under("positioning")
    pos_rounds = max([p["rounds"] for p in pos_pages], default=0)
    stages.append({"n": 2, "docs": d, "gates": [
        ["repo set up (CLAUDE.md, research moved in)",
         has(app, "CLAUDE.md") and os.path.isdir(os.path.join(app, "research")), ""],
        ["reviewed on a page", pos_rounds > 0, "%d rounds" % pos_rounds if pos_rounds else ""],
        ["positioning.md exists", has(app, "positioning.md"), ""],
        ["USP and viral feature named",
         contains(app, "positioning.md", "usp") and contains(app, "positioning.md", "viral"), ""],
        ["Anchored-to block present", contains(app, "positioning.md", "anchored"), ""]]})

    # 3 Spec — one stage per part of the PRD page (renamed 2026-09-26): 3.1 … 3.6.
    # Design direction is the PRD's Part 5, so it is 3.5 here, not a stage beside the spec.
    spec_pages = [p for p in pages if p["dir"] == "spec" or p["dir"].startswith("spec/")]
    dpages = [p for p in pages if p["dir"].startswith("design")]
    for p in spec_pages + dpages:
        used.add(p["id"])
    rounds = max([p["rounds"] for p in spec_pages], default=0)
    dec = {}
    try:
        dec = json.load(open(os.path.join(app, "spec", "state.json"))).get("decisions", {})
    except (OSError, json.JSONDecodeError):
        pass
    g = int(dec.get("gate") or 0) if "gate" in dec else None   # None: an older, unstaged PRD page
    handed = dec.get("prd_ready") == "done"
    brief = has(app, "design/BRIEF.md")
    handoff_in = os.path.isdir(os.path.join(app, "design")) and any(
        f not in ("BRIEF.md", "brief", "references") for f in os.listdir(os.path.join(app, "design")))
    staged = g is not None

    d = [doc(p["dir"], "html-worker", p["title"]) for p in spec_pages] + extras_under("spec")
    stages.append({"n": "3.1", "docs": d, "gates": [
        ["review rounds held", rounds > 0, "%d rounds" % rounds if rounds else ""],
        ["The case confirmed" if staged else "PRD page exists", g >= 1 if staged else bool(spec_pages), ""]]})
    stages.append({"n": "3.2", "docs": [], "gates": [
        ["v1 feature list decided", (g >= 2) if staged else contains(app, "PRD.md", "v1 feature"), ""]]})
    stages.append({"n": "3.3", "docs": [doc("spike", "code")] if has(app, "spike") else [], "gates": [
        ["bets tested (spike)", (g >= 3) if staged else has(app, "spike"), ""]]})
    stages.append({"n": "3.4", "docs": [doc("spec/prototype.html", "prototype")] if has(app, "spec/prototype.html") else [], "gates": [
        ["clickable prototype built", has(app, "spec/prototype.html"), ""]]
        + ([["Prototype v1 confirmed", g >= 4, ""]] if staged else [])})
    d = [doc(p["dir"], "html-worker", p["title"]) for p in dpages]
    if brief:
        d.append(doc("design/BRIEF.md", "markdown"))
    d += extras_under("design")
    stages.append({"n": "3.5", "docs": d, "gates": [
        ["design brief written", brief, ""],
        ["Claude Design handoff received", handoff_in, ""]]
        + ([["Design direction confirmed", g >= 5, ""]] if staged else [])})
    stages.append({"n": "3.6", "docs": [doc("PRD.md", "markdown")] if has(app, "PRD.md") else [], "gates": [
        ["PRD exported from the page", has(app, "PRD.md"), ""]]
        + ([["Hand-over to code-orchestrator", handed, ""]] if staged else [])})

    # 4 Contract
    d = [doc("contract/openapi.json", "generated")] if has(app, "contract/openapi.json") else []
    routes = 0
    if has(app, "contract/openapi.json"):
        try:
            routes = len(json.load(open(os.path.join(app, "contract/openapi.json"))).get("paths", {}))
        except (json.JSONDecodeError, OSError):
            pass
    stages.append({"n": 4, "docs": d, "gates": [
        ["openapi.json committed", has(app, "contract/openapi.json"), "%d routes" % routes if routes else ""],
        ["CI contract check", bool(ci_files), ", ".join(ci_files)],
        ["both worker briefs point at it", has(app, "backend/AGENT.md"), ""]]})

    # 5 Build v1
    d = [doc(f, "markdown") for f in ("HANDOFF.md", "ORCH-QUESTIONS.md") if has(app, f)]
    merged = [c for c in commits if MERGE.match(c["subject"])]
    stages.append({"n": 5, "docs": d, "v1": bool(v1_end and v1_commits > 3), "gates": [
        ["worker briefs written", has(app, "backend/AGENT.md"), ""],
        ["both halves merged to main", len({MERGE.match(c["subject"]).group(1) for c in merged}) > 1
         if merged else False, ""],
        ["v1 build order complete", bool(v1_end and v1_commits > 3),
         "%d commits" % v1_commits if v1_commits else ""],
        # Tag `v1` on the commit whose build went to TestFlight — the only on-disk trace.
        ["v1 on TestFlight (tag v1)", bool(sh(["git", "tag", "-l", "v1"], app).strip()), ""]]})

    # 6 Features
    leftover = [p for p in pages if p["id"] not in used]
    rest = [doc(e["path"], "html", e["title"]) for e in extras if e["path"] not in taken]
    stages.append({"n": 6, "repeats": True, "features": True,
                   "docs": [doc(p["dir"], "html-worker", p["title"]) for p in leftover] + rest,
                   "gates": [
        ["features merged and verified", bool(feats), "%d so far" % len(feats) if feats else ""],
        ["contract questions answered",
         bool(oq and oq["answered"] >= oq["total"] and oq["total"]),
         "%d of %d" % (oq["answered"], oq["total"]) if oq else ""]]})

    # 7 Ship
    stages.append({"n": 7, "docs": [], "gates": [
        ["live on the App Store (tag release)", bool(sh(["git", "tag", "-l", "release"], app).strip()), ""],
        ["showcase site", False, ""]]})

    # state per stage: done / now / skip / todo
    last_touched = -1
    for i, s in enumerate(stages):
        s["met"] = sum(1 for g in s["gates"] if g[1])
        if s["met"]:
            last_touched = i
    # a finished stage hands "now" to the next one (app_1: PRD handed over → contract freeze)
    if 0 <= last_touched < len(stages) - 1 and stages[last_touched]["met"] == len(stages[last_touched]["gates"]):
        last_touched += 1
    for i, s in enumerate(stages):
        if i < last_touched:
            s["state"] = "done" if s["met"] == len(s["gates"]) else ("skip" if s["met"] == 0 else "done")
        elif i == last_touched:
            s["state"] = "now"
        else:
            s["state"] = "todo"

    pagemap = {p["id"]: p for p in pages}
    return {
        "id": name,
        "stage": stages[last_touched]["n"] if last_touched >= 0 else 1,
        "stage_name": dict((str(s[0]), s[1]) for s in STAGES).get(
            str(stages[last_touched]["n"]) if last_touched >= 0 else "1", ""),
        "commits": len(commits),
        "pages": len(pages),
        "decisions": sum(p["decisions"] for p in pages),
        "rounds": sum(p["rounds"] for p in pages),
        "stages": stages,
        "v1": {"end": v1_end, "source": v1_src, "commits": v1_commits} if v1_end else None,
        "features": [{k: v for k, v in f.items()} for f in feats],
        "pagemap": pagemap,
        "orch": oq,
        "commitlog": commits,
    }


def scan():
    apps = [build_app(n, p) for n, p in app_dirs()]
    return {"root": ROOT, "stages": [{"n": s[0], "name": s[1], "why": s[2]} for s in STAGES],
            "apps": apps, "scanned": datetime.now().strftime("%Y-%m-%d %H:%M")}


if __name__ == "__main__":
    print(json.dumps(scan(), indent=2, default=str)[:4000])
