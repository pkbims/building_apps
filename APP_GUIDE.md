# How to build one app, up to v1

The operating manual for `PIPELINE.md`: what must exist before you start, which skill runs
at each stage, exactly what you type, and how you know a stage is finished.

Stages 1–5 only. **Everything after v1 works differently** — see [After v1](#after-v1) at
the bottom.

`PIPELINE.md` says what each stage *is* and why. This says what you *do*. Where they
disagree, PIPELINE.md is the spec and this is the bug.

---

## Before anything: the three rules that do not bend

1. **Claude never moves you to the next stage.** Every transition is a file you have
   looked at plus a decision you have made.
2. **Each stage reads the previous stage's file, not the chat.** So a fresh or compacted
   session picks up exactly where the disk says you are.
3. **The baseline in `CLAUDE.md` is not negotiable** — real auth, real DB with migrations,
   Docker, CI/CD, tests gating the pipeline, rate limiting, health checks, error tracking,
   structured logging, metrics + dashboard, deliberate failure handling. Never accept the
   shortcut version, however small the app.

---

## Stage 1 — Research  ·  skill: `/research`

**Research comes first, before any app exists.** You only set an app up once research says
it is worth building. Most niches should die here, and a dead niche should cost a folder,
not a repo.

**Prerequisites:** the problem in one line; any hard limit (which phone, must it fit the
series stack). The skill asks if either is missing.

**You type:**

```
/research knowledge workers on iPhone who lose focus to social media
```

**What it does:** first works out why the problem exists (every cause sourced), then finds
every existing solution: how each one works step by step, its features, who it is for, what
it earns a month (sourced, a labelled estimate, or "no public number") and how it went
viral (sourced, or "no evidence"). It marks the **table stakes** — features every app has.
Then it pulls verbatim complaints from Google Play, the App Store and Trustpilot. Three or
more people saying the same thing is a pattern; one is a bad day. Last, 1–3 new ideas, each
fixing a named complaint.

**The rule that never bends:** never a quote it did not read this session. `verify_quotes.py`
checks every quote against the raw pulled JSON before the file is called done.

**Reddit is blocked.** If you want Reddit voices, paste the threads or links yourself.

**Produces:** everything in `building_apps/research/<niche>/` — there is no app repo yet —
`<niche>.md`, the pulled reviews, and an `html-worker` review page in `reviewer/`. You get a
URL, not a wall of terminal prose.

**Your gate, two decisions on the page:**

1. **Which option is strongest.** The file ends *"Strongest option: X. Why: one line."*
   and stops. You pick. Also pick the 2–3 quotes that will become the Anchored-to block.
2. **Build it or not.** The rule: **at least one app earns $10k+ a month** solving this
   problem — a sourced number or a labelled estimate. The page shows whether it is met.
   - **No** → move the folder to `archived_research/<niche>/` with a `README.md` saying why
     in a line or two (`toronto-student-rentals` is the precedent). Done; no repo was made.
   - **Yes** → set up the app, below.

---

## Stage 2 — Set up, then positioning  ·  skill: `positioning` (after set-up)

**Prerequisite:** research with a chosen strongest option and a **yes** to "build it".

### Set up the app

```bash
mkdir app_N && cd app_N && git init
mv ../research/<niche> research      # the research moves in with its review page
```

Write `app_N/CLAUDE.md` with what you know so far: the problem in one line, the platform
and hard limits, and `Stack: series default (see ../CLAUDE.md).` plus any deviation **with a
stated reason**. This file is loaded into every session for that app. The constraints come
after positioning, below, because they need the chosen wedge.

Commit: `Stage 1 research: <niche> — decided on <option>`.

### Positioning

**You type:**

```
Positioning for app_N, from the research.
```

**What it does:** runs the `positioning` skill — a review page (same layout as research: parts, progress card, a live preview of `positioning.md`). It proposes 2–3 candidates, one paragraph each, every one writable as
**"it's basically X, but Y"** where X is a real shipping product. A concept that cannot fit
that sentence is too novel and gets cut — you want adjacent and sellable, not original.

**Your gate:** you react until one paragraph survives.

**Produces:** `positioning.md` — the paragraph, naming the user, the closest existing
product and the wedge; then three one-liners the PRD drafts v1 from:

- **USP** — the one thing we do that X does not.
- **Viral feature** — modelled on what made competitors spread. Test: *describe the exact
  screenshot or 10-second video someone would post.*
- **What it does** — only for a new idea with no X close enough to copy: a short list.

Then an **Anchored to** block of 2–3 verbatim complaints with a link
to the research file.

> **Do not skip the Anchored-to block.** Stage 3 refuses to start without it. It is the
> evidence that lets the PRD argue rather than assert.

**Then finish `app_N/CLAUDE.md`** — the part set-up could not write yet:

- One paragraph: what the app is, in plain words (from the surviving positioning).
- **Decisions that constrain everything downstream** — the handful of things that must stay
  true. practice_3's list is the model: *never more than three options; recipes are curated, not
  generated; calories come from ingredients, never a photo; nothing useful behind a sign-up
  wall.* Each one names the research finding behind it.
- **Where things are** — a pointer per artefact, so a fresh session does not hunt.

It is the cheapest thing in the pipeline and the one that stops the most drift.

**Done when:** the app repo exists, `positioning.md` has its Anchored-to block and
`CLAUDE.md` names the constraints.

---

## Stage 3 — Spec  ·  skills: `/create-prd` + `html-worker`

**Prerequisite:** `positioning.md` **with** its Anchored-to block. Without evidence the
first part of the PRD cannot be written, and the skill will say so and stop.

**You type:**

```
/create-prd
```

then say **"HTML mode"**. A local server starts; you open the URL and work on one page.

**The order is fixed** (parts renamed on app_1, 2026-09-26): each part is confirmed before
the next opens, and the page ends on a hand-over button.

| Part | What it settles |
|---|---|
| 1 · The case | Summary · the problem with verbatim quotes · **R1, R2… design requirements, each with the evidence that forces it** · positioning · one audience · scope, including what you are *not* building |
| 2 · The experience (pick v1) | **v1 feature list** (table stakes + USP + viral feature; in v1 only if the promise breaks without it) · user flow · screens · one headline success metric · accepted risks |
| 3 · Can we build it? | TR1… · how it works · the riskiest bets, **tested before any design** |
| 4 · Prototype v1 | Tap through v1 on the phone, including the shareable moment |
| 5 · Design direction | The brief for Claude Design, and its handoff back (3.5) |
| 6 · Technical decisions | The choices behind the build: services, each workflow, **data (§15) and calls (§16)**, operations, build order, still open. Not the build itself |
| Hand-over | “PRD is ready — proceed to build” → PROGRESS.md updated, **code-orchestrator** (Opus, high) starts; its builders run Sonnet, high |

**§3 is the hinge.** Without numbered requirements tied to evidence, every later decision
is a preference.

**The prototype must show the viral feature's shareable moment**, and the spike list is
grouped by v1 feature, plus a shared group.

**Every technical decision is yours.** Database, hosting, auth, vendor, client framework,
queue, storage — each is a radio group with three plain lines per option (what it is /
what you get and what it costs / when you'd pick it). One may be marked *recommended*;
none is pre-selected.

**The prototype, between Part 2 and Part 3.** One `prototype.html` served from the same
directory, on your phone, with the decisions so far baked in. Reading a flow and feeling it
are different: practice_4 found *"if I have minutes, why am I seeing tasks?"* here, not in review.
Part 3 is written from what the prototype taught.

**How a round works:** you click, comment on specific blocks, press **Confirm & send**.
Claude reads `INBOX.md` and revises. Change requests revise the page; questions get answered
in the terminal so the page does not drift. Expect 3–6 rounds; practice_1 took 10 and practice_4 took 10.

**Your gate:** you say "done".

**Produces:** `PRD.md`, exported from the page with `export-md.py` — never hand-written, so
it records what you chose *and* what you rejected.

---

## Stage 3.5 — Design direction (the PRD's Part 5)  ·  skill: `create-ui-design-direction`

> Now a numbered stage in `PIPELINE.md`.

**Prerequisites:** all three, or it stops and says which is missing — `positioning.md` with
Anchored-to, the `spec/` page with §7 and §8 having survived a round, and `spec/prototype.html`.

**You type:**

```
Design brief for app_N.
```

**What it does:** pulls the generated blocks from the PRD page (not `PRD.md`, which may be
stale), asks the per-app design facts on an `html-worker` page — vibe, references,
navigation, real data, what is open for invention — and writes the brief.

**The principle:** *constrain the product, free the surface.* Flow, screen list, states and
contract strings are fixed; vibe and layout are a compass, not a cage. A brief that
specifies hex values instead of constraints kills the tool's best work — practice_1's mosaic
sign-in, the screen that landed best, was the tool's idea.

**Produces:** `design/BRIEF.md` plus the reference files it names.

**Your gate:** **you** paste the brief into Claude Design yourself and bring the handoff
back. The pipeline's output here is a prompt, not a design.

---

## Stage 4 — Contract freeze  ·  no skill (PIPELINE §4 is the spec)

**Prerequisite:** PRD §15 (data model) and §16 (API contract).

**You type:**

```
Freeze the contract from PRD §15-16.
```

Claude is now the **orchestrator**.

**What it does:** writes `backend/app/schemas.py` and the route *signatures* in
`backend/app/main.py` with empty bodies, then `backend/export_openapi.py` generates
`contract/openapi.json`. **The contract is code, not a document**, and the JSON is never
edited by hand.

Enforced three ways:

- **CI** — regenerate and `git diff --exit-code contract/openapi.json`. Drift fails the build.
- **Tooling** — ruff and mypy exclude the frozen files so a formatter cannot fork them.
- **Ownership** — workers may not edit them. The only way to change the contract is a
  numbered entry in `ORCH-QUESTIONS.md`.

**Your gate:** read the **endpoint list**, not the code. Does `POST /v1/rooms`,
`GET /v1/renders/{id}`… match the screens from stage 3? If yes, commit. From this moment
the contract is frozen.

**Done when:** `openapi.json` is committed, CI's contract check is green, and both worker
briefs point at it.

---

## Stage 5 — Build v1  ·  no skill yet (skill candidate)

The one stage where you run **three sessions, not one**.

**Prerequisites:** frozen contract; `PRD.md` §17 (operations) and §18 (build order).

### Set up (orchestrator session)

Claude writes `HANDOFF.md`, `backend/AGENT.md` and `<client>/AGENT.md`, then creates a
worktree per half on its own branch. In Herdr that is one tab each:

```
tab orchestrator   main checkout
tab backend        worktree on branch `backend`
tab ios            worktree on branch `ios`
```

### The three roles

**Orchestrator — writes no app code.** It writes the briefs, owns the contract's shape,
answers `ORCH-QUESTIONS.md`, merges at checkpoints, and **verifies what workers claim
rather than relaying it**. An orchestrator that also codes stops verifying, because it
trusts its own work.

**Two workers.** In each worktree, start a session and type:

```
Read AGENT.md and start.
```

Each reads its brief, the PRD and the contract, and builds **TDD-first** inside its own
folder. The backend worker builds the whole baseline as it goes — auth, migrations, Docker,
CI, metrics, error tracking, rate limiting, health — because it is in the brief, not an
afterthought.

### While they work

Almost nothing, and that is the point. You watch status summaries. When a worker hits a
contract problem it does not patch around it — it appends to `ORCH-QUESTIONS.md`:

```
Q3 — Unlock request needs a reason field
From: ios · Blocks: the request screen
```

The orchestrator pings you, you decide ("yes, optional string, max 200 chars"), the
orchestrator edits `schemas.py`, regenerates the contract, answers inline, both workers pull.

Some things only you can do — a physical device, an Apple ID re-auth, a store entitlement.
practice_4 stalled on exactly that. Those are yours, not the orchestrator's.

### Your gate

At each checkpoint the orchestrator merges a worker branch into `main` **after running the
tests and hitting the endpoint itself**.

**Done when:** both branches merged to `main`, the baseline items assigned to each half are
in, and **v1 is on TestFlight, talking to a real hosted backend** — a phone cannot reach
`localhost`. Hosting and signing are decided by the first app to get here, then become the
series default.

v1 is one app built at once. The PRD's v1 feature names are the sections of the build
order, so you can see which feature each checkpoint finished.

**That day is v1.** practice_1's was 2026-09-09: 40 commits, the whole backend baseline and the
iOS core, in one day.

---

## After v1

Stage 6 is **Features**, and it is a loop you re-enter rather than a step you pass through.
Same worktrees, same briefs, same checkpoint rule — but the unit is one named feature:

1. **Name it first.** The review page, the branch and the progress view all key off that name.
2. **Review it first, if it deserves a review.** A feature that changes what the user can
   ask for or see gets an `html-worker` page and rounds before any code. A catalogue growing
   18 → 62 does not; pretending otherwise is ceremony. Of practice_1's six features, four had a
   review page and two did not.
3. **Build it in the worktrees**, TDD-first.
4. **Merge on the same checkpoint rule** — the orchestrator verifies before merging.

**The contract stays frozen, and features are what test that.** Two of practice_1's six features
needed it changed — the options round, and shop-your-restyle — and both went through
`ORCH-QUESTIONS.md` rather than around it.

There is no "done" for this stage. A feature is done when it is merged and verified; the
stage is a list that grows.

---

## The whole thing, in one table

| Stage | Skill | You type | Lands on disk | Your gate |
|---|---|---|---|---|
| 1 Research | `/research` | `/research <who> who <problem>` | `research/<niche>/` (no repo yet) | strongest option picked; **build it?** no → `archived_research/` |
| 2 Set up + Positioning | — | "Positioning for app_N, from the research." | `app_N/` repo, research moved in, `positioning.md` + Anchored-to, constraints in `CLAUDE.md` | one paragraph survives |
| 3 Spec | `/create-prd` + `html-worker` | `/create-prd`, "HTML mode" | `spec/`, `prototype.html`, `PRD.md` | you say "done" |
| 3.5 Design direction | `create-ui-design-direction` | "Design brief for app_N." | `design/BRIEF.md` | you run Claude Design yourself |
| 4 Contract | — | "Freeze the contract from PRD §15-16." | `contract/openapi.json` | endpoint list matches the screens |
| 5 Build v1 | — (candidate) | "Read AGENT.md and start." ×2 | `main`, both halves merged | orchestrator verified, v1 on TestFlight |
| 6 Features | — | per feature | a feature per merge | repeats; never closes |
| 7 Ship | — (not yet written) | — | App Store release, showcase site | app is live on the App Store |

---

## Honest gaps, as of 2026-09-23

- **Stages 2, 4 and 5 have no skill.** They are procedure in prose, so a fresh session
  re-derives them from `PIPELINE.md` each time. Stage 5 is the strongest skill candidate.
- **Stage 7 (Ship) is defined but not written.** It means App Store review and release, then the showcase site; the first app to ship writes the detail. Hosting is decided earlier, by the first app to reach TestFlight in stage 5.
- **No app has reached stage 7.** practice_1 is the furthest along and is in stage 6.
