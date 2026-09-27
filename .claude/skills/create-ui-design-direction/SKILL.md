---
name: create-ui-design-direction
description: Stage 3½ of the app pipeline — after Part 2 of the PRD (flow, screens, prototype) holds and before Part 3 is written. Produces `<app>/design/BRIEF.md`, the prompt the user pastes into claude.ai's Design tool (Claude Design) by hand, plus the reference files it names. Asks for the per-app design facts (vibe, references, navigation, real data, what is open for invention) through an html-worker page, never by guessing. Use whenever the user says design brief, design direction, UI direction, "brief Claude Design", "what do I give the design tool", or wants screens designed for an app in this series — even if they just say "let's do the UI now".
---

# Create a UI design direction

The pipeline's output here is a **prompt, not a design**. Claude Code writes the brief;
the user runs Claude Design themselves and brings the handoff back. Settled on
2026-09-20 in `design-brief-review/REVIEW.md` (seven decisions, D1–D7) after finding that
practice_1's only design run had no saved prompt at all — the tool read the repo and invented
the rest, and told us so ("THE AESTHETIC I PICKED", "PLACEHOLDERS: no photography yet").

The whole flow:

- **Check Part 2 holds** → **pull the generated blocks from the PRD page** →
  **ask the written blocks on an html-worker page** → **rounds until "done"** →
  **build `design/BRIEF.md` + `design/references/`** → **stop and hand over** →
  *(later)* **receive the handoff, check its shape, Part 3 continues**

## The principle behind every question

**Constrain the product, free the surface.** Flow, screen list, states, contract strings
and the token *discipline* are fixed — a wrong guess there costs a build round. Vibe,
references and voice are a compass, not a cage — three words and a "not like". Motion,
illustration, the one moment that deserves animation, layout within a screen are left
open and the brief *says* they are open. What kills the tool's best work is a brief that
specifies answers (hex values, font names) instead of constraints (at most three type
roles, every value a named token). practice_1's mosaic sign-in — the screen that got "Very
Cool" — was the tool's idea, not ours.

## App Maker mode

When the session was started from the App Maker (its first prompt says "App Maker mode", or the
folder has a `.appmaker.json`), follow the `app-maker` skill's **Stage sessions** rules instead of
the page-server and terminal steps below: the page lives in the app folder and the app's one server
serves it — no page server of your own, no watcher; ask the user on the page with `post.py`; answer
questions in the page's conversation with `html-worker/reply.py <page_dir> <id> "…"` (they arrive by prompt, bundled); you are woken when the user presses Send.

## Before you start

All three must exist, or stop and say which is missing. The first part of this brief is
generated from them and cannot be invented.

- `<app>/positioning.md` with an **Anchored to** block.
- `<app>/spec/index.html` + `state.json` — the PRD page — with §7 (flow) and §8 (screens)
  written and having survived at least one review round.
- `<app>/spec/prototype.html` — the `create-prd` prototype. If it is missing, the
  prototype step comes first; this brief is the visual layer *on top of* a felt flow (D2).

If Part 3 already exists (practice_1, practice_4), the brief still works — §16's error table becomes
the fixed-strings block instead of a placeholder. Say which case you are in.

## Step 1 — Pull the generated blocks

Read the PRD page and `state.json`, not `PRD.md` (the page is the source; the markdown
may be stale). Extract, verbatim where possible:

| Brief section | Source |
|---|---|
| §1 What this is, for whom | `positioning.md` paragraph; PRD §5; two Anchored-to quotes |
| §4 Screen inventory | PRD §8 — every screen, what's on it, the requirement it serves |
| §4 hardest screen | PRD §13/§14 sentence naming it and why; else the §8 note |
| §5 fixed strings | PRD §16 "What the user sees" column if Part 3 exists; else *"contract strings arrive in Part 3 — propose error copy, we adopt or replace"* |
| §10 fixed vs open | `state.json`: decision ids with a value are fixed, ids in `groups` without a value are open → "build as switches and compare" |

Then list the screens the flow **needs but §8 does not name** — Home / list, Settings,
account or credits, sign-out, "done" landing. practice_1's PRD had eight screens; the shipped
app needed three more and the tool invented one silently. Those candidates become a
question in step 2, not an assumption.

Also scan the app directory for **real data** a designer could use: photos in `inputs/`,
sample images, anything the spike produced. practice_1 had a real room photo on disk while the
tool worked from "labelled plates". Every candidate file becomes a checkbox.

## Where it lives: inside the PRD page, as a step

Design direction is **a part of the PRD page** (after *Try the prototype*, before *The
build*), not a separate page — so anyone reading the PRD sees why we do it and where it
stands. Everything on it is in **plain, simple words** (the brief itself can stay precise;
the page that explains it must not read like a designer's spec). The part has:

1. **Why this step** — the prototype shows what it does, this decides how it looks; a brief,
   not a design, because the designer works best with room to move; before the build,
   because the build needs the look as a token file; two looks first, because comparing is
   easier than judging one.
2. **The questions** below, each option one short plain line (what you'd get), recommended
   one marked, nothing pre-selected. After they're answered, this becomes **"What we told
   the designer"** — a short table of the answers.
3. **Where the design is** — a status tracker: brief written (Claude) → Claude Design running
   (user) → design back (user, a **"Handoff is back"** button) → design checked (Claude).
   Plus the upload folder (`design/make_bundle.sh` → `design/for-claude-design/` + zip) and
   the paste-this-first steps.

app_1 (2026-09-25) ran it on a separate page first; the user asked for it to move into the
PRD in plain words. `app_1/spec/build.py` Part 5 is the model.

**Every option set on the page has one *recommended* option with a one-line reason** (html-worker
rule), never pre-selected.

## Step 2 — Ask the written blocks

Invoke `html-worker`. Directory `<app>/design/brief/`; pick a free port (7777–7779 are
often taken — check with `lsof -ti tcp:<port>`). Run the server in a herdr pane if
`$HERDR_ENV` is 1.

One page, in brief order. Each written block is a decision with options **derived from
the app's own files** — vibe triads from the positioning's adjectives and the research's
complaints, reference apps from the competitors the research names, navigation options
from what the prototype actually does. Never bare labels: each option carries what it is,
what it costs, when you'd pick it, same as `create-prd`. Free-text answers ("Fraunces",
"like Things 3 but warmer") arrive as *change* comments on the block; fold them in as a
new option and pre-select nothing.

The question catalogue with derivation rules is in `references/questions.md`. Read it
before building the page. The short list:

1. Navigation model, and where "done" lands.
2. Device range.
3. Screens to add to the inventory (the candidates from step 1).
4. Vibe — three words; three candidate triads.
5. Like / not like — reference apps, one screen each.
6. Copy voice.
7. Real data — which files on disk go into `references/`; which numbers are real.
8. The two screens for the side-by-side directions (default: hardest + home).
9. **Open for invention** — motion, the one moment, illustration or mascot, sound and
   haptics, app icon, onboarding depth. Checkboxes. What is checked goes into the brief
   as "surprise us on"; what is not checked is not mentioned at all.

Series rules are stated on the page as fixed, not asked: light only for v1 (D5),
accessibility handled at build (D6), tokens as the build contract, two directions before
any other screen (D3), the handoff shape back (D4). Show them so the user can object with
a comment; do not turn them into radios.

Rounds work as html-worker says: revise on change requests, answer questions in the
terminal, mark addressed, re-arm the watcher. Done when the user says "done".

## Step 3 — Build the brief

Fill `assets/BRIEF-template.md`. Generated blocks from step 1, written blocks from the
recorded decisions, series rules untouched. Then run the checker — it fails on any
`{{placeholder}}` left, any §4 row with an empty state cell, any file named in §6 that
does not exist under `design/references/`, and a brief over 200 lines (longer means the
PRD is being repeated instead of pointed at):

```bash
python3 <skill>/scripts/check_brief.py <app>/design/BRIEF.md
```

Copy the chosen real files into `<app>/design/references/`, named for what they are
(`room-real-iphone.jpg`, `like-things3-today.png`). Commit `design/`.

## Step 4 — Stop and hand over

Say, in the terminal, exactly this and no more:

- Open Claude Design, new project, **no repo connection** (D7).
- Attach: `design/BRIEF.md`, `PRD.md`, `spec/prototype.html`, `design/references/*`.
- Paste the contents of `BRIEF.md` as the first message.
- Expect two directions on the two named screens first; pick one there, then screens.
- Bring back into `design/`: `HANDOFF.md`, `tokens.json`, `canvas.dc.html` (or whatever
  the export is called — rename it).

Update `PROGRESS.md` for the app: "Design brief written <date>; awaiting Claude Design
handoff." Then stop. Do not run the design tool, do not open a browser at it, do not
draft screens yourself — the user asked for the checklist, not the design.

## The return path

When the user says the handoff is back, check its shape before Part 3 continues:

- `design/HANDOFF.md` has the five sections the brief asked for — §1 visual system as
  tables, §2 per-screen changes against §4's numbering, §3 the states grid filled, §4
  hold-off list, §5 rejected alternatives. Missing sections are a question back to the
  tool, not something to fill in yourself.
- `design/tokens.json` parses, every colour is named, no screen in the handoff cites a
  literal value that is not in it.
- Every screen in the brief's §4 appears in §2; every added screen the tool introduced
  is flagged as a change request, not silently present.

- If the handoff proposes an **app name** (or the user picks one), search the App Store
  (`itunes.apple.com/search?term=<name>&entity=software`) and flag any same-category app or
  ® holder with that name before recording it — as *provisional* until a trademark search.
  (app_1: "Homi" was taken in the same category and as a registered mark aimed at renters.)

Then `create-prd` Part 3 is written with the handoff on disk: §14 names `tokens.json` and
any bundled font as build tasks, and the stage-5 client worker brief points at
`design/HANDOFF.md` and `design/tokens.json` and opens the canvas.

## Tradeoffs, for the camera

- **Prompt, not design.** The tool does its best work with room to move; the pipeline's
  job is to make the room well-shaped. Costs a manual step every app.
- **No repo connection.** Reproducible input, and the code never steers the design. Costs
  attaching four files by hand and losing the tool's sync note as a record — which is why
  `BRIEF.md` is committed *before* the run.
- **Light only, no accessibility floor.** Chosen for throughput on 2026-09-20 with the
  cost named: an item the series promises and does not ship, and layouts that may not
  grow with Dynamic Type. Revisit as D5/D6 when an app makes it hurt.
