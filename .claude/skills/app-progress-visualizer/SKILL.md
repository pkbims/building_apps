---
name: app-progress-visualizer
description: One local page showing where every app in the series stands — the seven pipeline stages, which gates each app has met, v1 as a closed milestone, the features merged since, and every html-worker review page and document hanging off the stage it belongs to. Everything is derived from disk on each load; nothing is hand-maintained. Use when the user asks where an app is, what stage something reached, what has been built since v1, wants to see or show a past review page or PRD, or mentions the app progress visualizer, the app maker, or the progress dashboard — even if they don't name the skill.
---

# App Progress Visualizer

One address for "where is everything": **the port in `.port`** (first free from 7710).
Built 2026-09-23 from the `app-maker-review` page (18 decisions, 2 rounds); D-numbers below
refer to those.

## Start it

```bash
cd building_apps && .claude/scripts/server-pane.sh \
  "$PWD/.claude/skills/app-progress-visualizer" "python3 server.py"
```

It goes in the herdr `servers-tab` like every other server, never as a split of the user's
pane, and it is listed in the monitoring center at :7700. Check the title is
`App Progress Visualizer` before giving the URL.

## What it shows

Four views, one page.

- **Board** — every `app_N` as a row, the seven stages as columns. Click any cell.
- **App** — the stage rail: each stage's gates ticked from what is on disk, the documents
  it produced, **v1 as a closed milestone**, and the features merged since (D13). Side
  work — a review page that belongs to no feature — sits under the stage it happened
  during (D2).
- **Guide** — the short form of `APP_GUIDE.md`: prerequisites, skill, prompt, gate.

A fourth view, **Journal** (every review round and merge for one app, in order), is built
but hidden — `SHOW_JOURNAL` at the top of `index.html`'s script turns it back on.

Dates are hidden too; `SHOW_DATES` in the same place turns them all back on.

## How it looks

The numbers on the page are drawn, not just listed, and every drawn thing counts the same
gates the rail ticks — so a ring can never disagree with the list beneath it.

- **A ring per view**: gates met over gates that exist. The board's ring sums every visible
  app; the app view's is that app alone.
- **Gate micro-bars** on every board cell — one segment per gate, filled when met. A cell
  therefore says *how far in* a stage is, not just done/not done.
- **Commits per day** as a bar strip, straight from the commit log.
- **"Waiting on"** under the board: the unmet gates of each app's current stage, which is
  the one thing the board could not say before. Clicking a card jumps to that stage.
- Green (`--done`) means met, terracotta (`--accent`) means here now. The two used to be
  the same colour, which made a finished stage and the live one look alike.
- `--onacc` is the text colour on an accent background: white in light mode, dark ink in
  dark mode, where the accent is a light salmon that white text disappears into.

## Where the facts come from

**Nothing is hand-maintained (D5).** `scan.py` reads, on every page load:

- **Files present** — `positioning.md`, `PRD.md`, `spec/prototype.html`,
  `design/BRIEF.md`, `contract/openapi.json`, `backend/AGENT.md`, `.github/workflows/`.
  These are the stage gates (D3), so a gate can only claim what a file proves.
- **Lines in those files** — the research file's "Worth building?" line (the build-it
  gate), `positioning.md` naming a USP and a viral feature, `PRD.md` holding a v1 feature
  list. Added 2026-09-24 with the pipeline change; apps from before it show them unmet,
  which is true.
- **Review pages by folder** — `research/` → stage 1, `positioning/` → stage 2 (the
  positioning skill's page), `spec/` → 3, `design/` → 3½. A page with at least one sent
  round counts as "reviewed on a page", so a stage shows as in progress before its output
  file is saved. Stage 2 also checks set-up: `CLAUDE.md` plus a `research/` folder.
- **Git tags** — `v1` on the commit whose build went to TestFlight (stage 5's last gate,
  and the authoritative v1 boundary), `release` on the one that went live on the App Store
  (stage 7). A tag is the only on-disk trace of either event, so tag it when it happens.
- **`state.json`** beside every `index.html` — rounds, decisions, comments. That is where
  review pages are discovered; no registry.
- **git** — commits, and merges into `main` matching `Merge <half> into main — <name>`.

`PROGRESS.md` stays the file a fresh agent session reads (D9); this is the view of the
same truth, not a replacement.

### The two derivations that can be wrong

**The v1 boundary.** A `v1` git tag is authoritative. Without one it is inferred from the
busiest build day, and the page says so. practice_1's inferred boundary is a day early, which
turns three baseline-completion merges into features — `git tag v1 <sha>` in that repo
fixes it exactly.

**Feature grouping.** Features come from merge messages (D14), grouped when their
significant words overlap, so "the options round" merged from both halves is one feature.
Vague merge messages group badly. A review page is attached to a feature by **name**, with
date as the tiebreak — several features merge on the same day, so dates alone give the
first one everything.

## Opening a document

Clicking any document opens it read-only (D7). Markdown and `openapi.json` render in the
panel; an html-worker page gets a **read-only copy generated beside it** as
`reading-copy.html` (D16, D17), regenerated whenever `state.json` is newer.

The copy works by injecting a shim in `<head>` that answers `/api/state` from baked-in
state and swallows writes — **not** by rewriting the page's script. The pages were built
from different template versions and only agree on talking to `/api/state`; rewriting
their scripts breaks the older ones. Copies are served from a real path (`/f/<path>`) so
their own relative links to `vendor/` and `images/` still resolve.

Copies are generated when a document is opened. **When html-worker gains a "Review
complete" button** (D18, not built yet — it writes `completed` into `state.json`, which
`scan.py` already reads), generation should move to that event.

## Hiding an app

Hover an app's name on the board and click **hide**: it leaves the board and the top bar.
A **Hidden (n)** button then appears in the header — it reveals the hidden rows dimmed,
each with a **show** button, so nothing is ever lost.

The list lives in `hidden.json` beside this skill, never in the app itself. It is a view
preference, not a fact about the app, which is why it sits outside everything `scan.py`
derives: the scan still reports every app, and the page filters. Delete `hidden.json` to
show everything again.

## Rules

- **Derived, not declared.** If something cannot be read off disk, it does not go on the
  page. Do not add a hand-written status field.
- **A new app needs no registration** — a directory matching `app_N` appears on its own,
  and so does a new review page.
- **Never write into an app from here** except `reading-copy.html`.
- A stage with no gates met that sits before a later stage with gates met is shown as
  **not run**, not as pending — that is how practice_1 correctly shows 3½ as skipped.
