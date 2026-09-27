---
name: positioning
description: Stage 2 of the app pipeline, right after research says "build it". Turns the research Conclusion into one short positioning — "it's basically X, but Y" — plus the USP, the viral feature (described as the exact post someone would share), the platform and the Anchored-to quotes, reviewed on an html-worker page in plain English, and saved as <app>/positioning.md. Use when the user says positioning, "position app_N", "it's basically X but Y", or asks what comes after research — even if they don't name the skill.
---

# Positioning

Simple version:

- **Why this step matters** → **What research decided** → **2-3 candidates, each "it's basically X, but Y"** →
  **you pick one** → **sharpen it: USP, viral feature, platform, quotes** →
  **the result: positioning.md**

The output is short on purpose. It is a rule the PRD must obey, and a long positioning
statement rules out nothing.


## App Maker mode

When the session was started from the App Maker (its first prompt says "App Maker mode", or the
folder has a `.appmaker.json`), follow the `app-maker` skill's **Stage sessions** rules instead of
the page-server and terminal steps below: the page lives in the app folder and the app's one server
serves it — no page server of your own, no watcher; ask the user on the page with `post.py`; answer
Talk messages with `talk.py`; you are woken when the user presses Send. **Setting the app up:** don't move the research folder by hand — run `python3 .claude/skills/app-maker/scripts/maker_cli.py promote research/<slug> app_N`, which moves it into `app_N/research/` and carries the workspace and sessions with it.

## Before you start

- The app repo exists and its research has a **Conclusion** (idea, who it's for, USP points,
  viral feature, complaints, build = yes). Read `<app>/research/<niche>.md`, and the
  research page's `state.json` for the exact answers.
- If the Conclusion is missing or says "not decided", stop and send the user back to the
  research page. Positioning doesn't re-decide research.

## Step 1 — Say why this step matters

Open with a short, plain paragraph (or 3-4 bullets) on why positioning comes after
research, written for this app — not generic. Cover:

- Research found *what* to build; positioning decides how people *understand* it — in one
  sentence, by comparing it to something they already know. Source it (e.g. Moreau, Markman
  & Lehmann 2001, "What Is It?", Journal of Consumer Research) and don't overstate it —
  comparison helps a lot; it isn't the *only* way people understand things.
- Choosing X picks who we're compared against, and so which complaints we must beat first.
- The **"but Y"** becomes the words everywhere (first screen, video hook, the post). The
  **"X" stays mostly internal**: App Store name, subtitle and keywords must not name other
  apps (Apple guideline 2.3.7); ads and videos may name a competitor in the US if truthful
  and not misleading (FTC comparative-advertising policy).
- It's the rule for Stage 3: every feature must support the "but Y"; anything else is cut.

Use this app's real names in the examples ("basically Home AI, but…"), so it reads as
this app's reason, not a lecture.

Then a short block, **"What it gives you, the app creator"** — the user has to explain this
step to others, so give them the words:

- One sentence, in bold: *one sentence to check every later choice against — which feature
  to build, what to cut, what to show first, what to say in the video — so the app stays one
  sharp thing instead of slowly becoming another <X>.*
- The app's (recommended) positioning sentence, then a **yes/no table of 4-5 real choices**
  it settles for this app: a tempting feature it rules out, a shortcut it forbids, what the
  first screen shows, the video's first line.
- A line they can say to others: *"Without this sentence, every idea sounds reasonable and
  we slowly rebuild what already exists. With it, we can say no fast — and every no keeps
  the app different."*

## Step 1b — Recap what research decided

Four or five lines, taken from the research Conclusion, in its words: the idea, who it's
for, the USP points, the viral feature, the biggest risk. No new claims here.

## Step 2 — Write 2-3 candidates

Each one must fit **"it's basically X, but Y"**:

- **X is a real app people use today**, named in the research, with its 2026 money or
  usage from the research beside it. No X → cut the candidate; it's too new to sell.
- **Y is one or two twists**, each answering a complaint from the research. A twist no
  complaint asks for is cut.
- One paragraph: who it's for, what they do, what they get. Plain words.
- Under it: **closest app**, **the twist**, **evidence** (which research complaints back it),
  **risk** (what could go wrong with this framing).

Candidates should differ in **which X** they compare to — that is the real choice. Say
which one you'd pick and why, in one line.

## Step 3 — Sharpen the chosen one

After the pick, give options (with your recommendation) for:

- **USP** — one sentence: the one thing we do that X doesn't.
- **Viral feature** — must pass the post test: *describe the exact screenshot or 10-second
  video someone would post*, shot by shot, with the caption. If you can't picture the post,
  it isn't ready. Start from the research's viral feature pick.
  If the post depends on something not yet proven buildable (e.g. a smooth tour made from a
  photo), save it as a **leaning** — "final pick after the Stage 3 spike" — and name what the
  spike must show.
- **What it does** — only when no X is close enough to copy: a short list.
- **Platform** — iOS or web, with the reason taken from how the idea works (camera,
  sensors, where users are). The series allows either; the choice goes into CLAUDE.md.
- **Anchored to** — 2-3 verbatim complaints, pre-ticked from the research pick. Link each to
  its review. Stage 3 won't start without this block.

No pricing here — pricing is decided later.

## Step 4 — The result

`positioning.md` in this shape:

```markdown
# Positioning — <app> "<working name>"

<date> · decided on the positioning review page, <N> rounds.

**It's basically <X>, but <Y>.** <one paragraph: who, what they do, what they get, the twist>

- **USP:** <one sentence>
- **Viral feature:** <the exact post, shot by shot, with caption>
- **Platform:** <iOS / web> — <reason>
- **What it does:** <only for a new idea>

## Anchored to

Verbatim complaints from `research/<niche>.md`:

- "<quote>" — <app>, [<store>, <month year>](<link>)

Not this: <the closest apps we are deliberately not, one clause each>
```

Then finish `<app>/CLAUDE.md`: a one-paragraph description from the positioning, the
**decisions that constrain everything downstream** (each naming the research finding
behind it), the platform with its reason, and where things are. Update PROGRESS.md
(stage 3 next) and commit in the app repo: `Stage 2 positioning: basically <X>, but <Y>`.

## The review page

Build it with the html-worker skill in `<app>/positioning/reviewer/`, and hand over the
URL. Terminal replies stay short: what changed, what's still open.

**Five parts, each a visible heading, the same words in the left rail:**

| Part | Answers | Decisions |
|---|---|---|
| 1 · Why this step, and where we start | why positioning matters (for this app), then the recap | — |
| 2 · The candidates | 2-3 "basically X, but Y" cards, my pick | **D1 which one** |
| 3 · Sharpen it | USP, viral feature (the exact post), platform | **D2 USP · D3 viral · D4 platform** |
| 4 · The evidence | Anchored-to quotes, pre-ticked from research | **D5 quotes** |
| 5 · Result | `positioning.md` as it will be saved — updates live from D1-D5 | — |

- **Plain, simple English**, like the research page: short sentences, everyday words.
- **"Your progress"** is its own column on the right, **beside** the decisions and the
  feedback queue (four columns: contents | page | progress | decisions + queue — never
  stacked).
- Decisions are numbered in reading order; options and the Result read from one table of
  labels so they always match.
- Reuse the part dividers, progress card and live-result code from
  `app_1/research/reviewer/build.py` rather than rewriting them.
- Write `positioning.md` from the page's answers once D1-D5 are decided and the user says
  so. The page is the source; don't hand-write a second version.
- **Never stop the review server** — the user closes it from the monitoring center.

**Every option set on the page has one *recommended* option with a one-line reason** (html-worker
rule), never pre-selected.

## Not allowed

- An X that isn't a real app from the research.
- A twist, USP or viral feature with no research complaint or finding behind it.
- A viral feature you can't describe as an exact post.
- "A chatbot can't do X" without a current-year source.
- Our pricing.
- A claim about how people think or what's legal, without a source.
- More than one paragraph of positioning.
- Jargon where a plain word works.
