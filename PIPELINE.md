# Pipeline

The stages each app goes through, in order. Deliberately not fleshed out yet — the detail
gets written from what actually happens during practice_1, not predicted in advance.

**The whole path at a glance** (settled on app_1, 2026-09-26):

> Research → Positioning → **The case → The experience (pick v1) → Can we build it? →
> Prototype v1 → Design direction → Technical decisions** → Hand-over → Contract freeze →
> Build v1 → Features → Ship

The bold steps are the parts of the one PRD page — stage 3, split the same way: **3.1 The case · 3.2 The experience (pick v1) · 3.3 Can we build it? · 3.4 Prototype v1 · 3.5 Design direction · 3.6 Technical decisions**. Design direction is part of the PRD, not a stage beside it. v1's
features are picked in *The experience*, so the prototype is v1's. *Technical decisions*
is not the build — it is the choices behind it. The hand-over button starts the
code-orchestrator, and the building begins at the contract freeze.

## 1. Research

Find a real pain point (Reddit, forums, reviews, search) and scan competitors: why the
problem exists, how each competitor works, its features, what it earns, how it went viral,
and what its users complain about. Every claim has a source; the `research` skill carries
the detail.

Runs **before any app repo exists**, in `research/<niche>/`. It ends on a go/no-go: no →
`archived_research/<niche>/` with a line on why; yes → stage 2 sets the app up. The rule
for yes: **at least one app earns $10k+ a month solving this problem** — a sourced number or
a labelled estimate from a market-data tool. One app clearing it proves people pay; the
estimate is accepted because most apps never publish revenue, and labelling it keeps it
from being read as fact. Tradeoff:
research has no repo history of its own until it moves in, in exchange for a dead niche
costing a folder instead of an `app_N` number and a repo.

## 2. Positioning

Starts by setting the app up: `app_N/` as its own repo, the research folder moved in, a
first `CLAUDE.md` (problem, platform, stack). Its constraints are written after the
positioning below, because each one names a finding and needs the chosen wedge.

Decide what we are building and why anyone would pick it, before any PRD exists.

A review loop on an html-worker page (skill: `positioning`), not a generated document. Claude proposes 2-3 candidate
positionings from the research, one paragraph each. The user reacts. Converge on one.

Every candidate must be writable as **"it's basically X, but Y"** — X a real shipping
product, Y one or two twists. A concept that cannot fit that sentence is too novel and
gets cut. The goal is something adjacent and sellable, not original.

Output is **one paragraph**, saved as `<app>/positioning.md`. It names the user, the
closest existing product, and the wedge. It stays short on purpose: it is a constraint the
PRD must obey, and a long positioning statement constrains nothing.

Below the paragraph, three one-liners the PRD drafts v1 from:

- **USP** — the one thing we do that X does not.
- **Viral feature** — the share-worthy thing, modelled on what research found made
  competitors spread. It must pass one test: *describe the exact screenshot or 10-second
  video someone would post.* If you can't picture the post, it isn't share-worthy yet.
- **What it does** — only when the chosen option is a new idea with no X close enough to
  copy: a short list of what it offers, so the PRD has something to draft from.

Then an **"Anchored to"** block: 2-3 verbatim complaints from the research
file, with a link to it. Stage 3 refuses to start without evidence behind the chosen
problem; this block is what carries that evidence forward. Skip it and the PRD stalls.

## 3. Spec

Turn the problem into a tight PRD and a UI direction. The PRD must name what is *not*
being built. Reviewed as a clickable HTML artifact with comment threads, not as prose.

Written as one page in parts, in order — **The case → The experience (pick v1) → Can we
build it? → Prototype v1 → Design direction → Technical decisions** — each confirmed before
the next opens. The risky bets are tested (*Can we build it?*) before any design, and **a
clickable prototype of v1** is felt on the phone before the design and the technical
decisions. The prototype was settled in practice_4, the part order on app_1 (2026-09-26);
the `create-prd` skill carries the detail. Ends on the hand-over button.

**Then the design brief, before Part 3.** `create-ui-design-direction` generates
`<app>/design/BRIEF.md` — the prompt — and stops. The user runs Claude Design by hand
with the brief and the files it names attached (no repo connection), picks one of two
directions, and brings `HANDOFF.md`, `tokens.json` and the canvas back into `design/`.
Part 3 is written with that handoff on disk. Tradeoff: a manual step every app, in
exchange for a saved, reproducible brief — practice_1's only design run had none. Decided
2026-09-20 in `design-brief-review/REVIEW.md`.

## 3.5 Design direction (the PRD's Part 5)

Between Part 2 of the PRD and Part 3: the flow and screens have held through a round and a
prototype has been felt, but the system that serves them is not yet designed. Settled
2026-09-20; the `create-ui-design-direction` skill carries the detail.

**The output is a prompt, not a design.** Claude Code writes `<app>/design/BRIEF.md` plus
the reference files it names; **you** paste it into Claude Design yourself and bring the
handoff back. Tradeoff: a hand-carried prompt costs a manual step every app, and is
accepted because the alternative is what practice_1 did — no saved prompt at all, the tool
reading the repo and inventing the rest, which leaves nothing to reuse or correct.

Needs all three, or it stops and says which is missing: `positioning.md` with its
Anchored-to block, the `spec/` page with §7 and §8 having survived a review round, and
`spec/prototype.html`.

The per-app design facts — vibe, references, navigation, real data on disk, what is open
for invention — are asked on an `html-worker` page, never guessed.

**Constrain the product, free the surface.** Flow, screen list, states and contract strings
are fixed, because a wrong guess there costs a build round. Vibe and references are a
compass, not a cage: three words and a "not like". Motion, illustration and layout within a
screen are left open, and the brief says so. A brief that specifies answers (hex values,
font names) instead of constraints (at most three type roles, every value a named token)
kills the tool's best work — practice_1's mosaic sign-in, the screen that landed best, was the
tool's own idea.

Done when: `design/BRIEF.md` and its references exist, and you have the Claude Design
handoff back in `design/`.

## 4. Contract freeze

Lock the API before any build work starts. This is what makes stage 5 possible: two
workers can build in parallel only if neither can change the thing between them.

The contract is **code, not a document**. The orchestrator writes `backend/app/schemas.py`
and the route *signatures* in `backend/app/main.py` (bodies left empty), straight from
PRD §15-16. `backend/export_openapi.py` generates `contract/openapi.json` from them; the
JSON is never edited by hand. Tradeoff: the backend framework becomes the schema language,
which ties the contract to FastAPI/Pydantic pins — accepted, because a hand-written spec
drifts from the code within a week and a generated one cannot.

Enforced three ways:

- **CI**: regenerate and `git diff --exit-code contract/openapi.json`. Drift fails the build.
- **Tooling**: ruff and mypy exclude the frozen files, so a formatter cannot fork them.
- **Ownership**: workers may not edit the frozen files. The only way to change the contract
  is a numbered entry in `ORCH-QUESTIONS.md`; the orchestrator decides, regenerates, and
  records the answer inline.

Done when: `openapi.json` is committed, CI's contract check is green, and both worker
briefs (stage 5) point at it.

## 5. Build v1

Client and backend in parallel, each in its own git worktree, both coding against the
frozen contract from stage 4. One orchestrator session, two worker sessions.

**The orchestrator writes no app code.** It writes the briefs, owns the contract's shape,
answers `ORCH-QUESTIONS.md`, merges each worker's branch into `main` at checkpoints, and
verifies what workers claim rather than relaying it. Tradeoff: an orchestrator that also
codes stops verifying — it trusts its own work — so the role is kept pure on purpose.

**Who runs it, and on which model** (user, 2026-09-26): the PRD page ends on a "PRD is ready —
proceed to build" button. Pressing it updates `PROGRESS.md`, and the session that wrote the
PRD starts a new Claude session named **`code-orchestrator`** in its own herdr tab and stops
there — the orchestrator owns stages 4 and 5. The orchestrator runs **Opus at high effort**;
coding workers (`backend`, `ios`) run **Sonnet at high effort**. Start any of them with
`.claude/scripts/start-agent.sh <name> <cwd> <model> <effort> "<prompt>"`.

**The orchestrator is a skill, and the user watches one page** (2026-09-26): the hand-over
starts it with `/code-orchestrator <app>`. It sets up `<app>/build-room/`, an html-worker page
with *Needs you* (questions, each with a recommended option, and the user's to-dos), *Now*
(each agent's state, each branch's last commit), *Updates* and *Checkpoints*. A ticker
script — no model — refreshes the status every 5 minutes, sends a macOS notification the
moment a question appears, and wakes the orchestrator through herdr the moment the user
presses *Send to the orchestrator*. Tradeoff: a heartbeat from a script costs nothing and
can't be reaped; only real events cost model time. Tradeoff: the
judgement-heavy role (contract shape, verifying claims) gets the strongest model; the
volume of code goes to the faster, cheaper one.

Files that make it work (all shipped in practice_1):

- `HANDOFF.md` — orchestrator context for a fresh session: roster, what is in flight,
  gotchas. Rewritten as things change; this is what lets the role survive a context reset.
- `<half>/AGENT.md` — one brief per worker. Read order, what it owns, what it must not
  touch, the one rule (never edit the contract; ask in `ORCH-QUESTIONS.md` instead), TDD
  mandatory, commit discipline.
- `ORCH-QUESTIONS.md` — append-only numbered questions from workers, answered inline by
  the orchestrator. A worker that hits a contract problem appends and keeps working on
  something else; it never blocks and never patches around it.
- Worktrees: `backend` and the client each on their own branch. Design/research agents
  that write no code share the orchestrator's checkout — check `git branch
  --show-current` before every commit there.

v1 is **one app, built at once**: one design brief, one frozen contract, one build order.
The PRD's v1 feature names become the sections of that build order, so progress has a
unit without splitting v1.

Done when: both branches merged to `main`, the baseline items assigned to each half (PRD
§17) are in, and **v1 is on TestFlight, talking to a real hosted backend** (a phone
cannot reach `localhost`). Hosting and signing are not settled yet: the first app to reach
this point decides them, and the choice becomes the series default in `CLAUDE.md`.
Tradeoff: v1 costs a deploy and a signing setup, in exchange for v1 meaning a build a
real person can install rather than one that only runs on this Mac.

**v1 ends here, and it ends on a day you can name.** practice_1's v1 was 40 commits in one
day (2026-09-09): the whole backend baseline and the iOS core, straight down PRD §18.
Everything after it is stage 6.

## 6. Features

The stage you re-enter. v1 is the app existing; this is the app getting better, and it
never finishes — so it is a loop, not a step you pass through.

Each feature is the pipeline in miniature, and the unit is one named feature, not a
sprint:

1. **Name it.** A feature has a name before it has commits, because that name is what the
   review page, the branch and the progress view all key off.
2. **Review it first, if it deserves a review.** Most do: a feature that changes what the
   user can ask for, or what they see, gets an `html-worker` page and rounds before any
   code. Some do not — a catalogue growing from 18 entries to 62 needs no review, and
   pretending otherwise is ceremony.
3. **Build it in the worktrees**, same two workers, same briefs, same TDD.
4. **Merge on the same checkpoint rule**: the orchestrator verifies before it merges.

**The contract is still frozen, and features are what test that.** Two of practice_1's six
features needed it changed — the options round and shop-your-restyle — and both went
through `ORCH-QUESTIONS.md` rather than round the side. A feature that edits the frozen
files directly has broken the one rule the parallel build depends on.

Done when: nothing. The stage stays open. A feature is done when it is merged and
verified; the stage is a list that grows.

Tradeoff: keeping Ship at 7 means the pipeline still reads as a line, at the cost of
pretending features stop when you ship. They do not — after shipping you come back here.
This is the one stage that repeats, and it is worth one irregular arrow on the diagram to
avoid inventing a second, parallel pipeline for work that uses exactly the same machinery.

## 7. Ship

v1 already reached TestFlight in stage 5, so Ship is the public release: **App Store
review and release**, then **the showcase site**. The full baseline from CLAUDE.md must
hold in the release build. Settled 2026-09-24; the detail gets written from the first
app that ships, not predicted.

## Open questions

- Waitlist as early validation (before stage 5) vs. showcase after ship — likely both,
  as two separate things.
- ~~Client CI.~~ Settled in practice_4 (PRD D17): the iOS client has CI — GitHub Actions on a
  macOS runner, build + core-package unit tests on every PR, UI tests nightly; device-only
  paths (Screen Time, Health, camera) are a written checklist run by hand before TestFlight.
  practice_1 shipped without it as an accepted risk (PRD F3); that was the exception, not the rule.
- Which stages earn a skill, and which are one-offs. Decide after practice_1.
  - Candidate noted mid-practice_1: the stage-5 orchestration pattern itself — two worker
    agents in git worktrees, `ORCH-QUESTIONS.md` for contract questions, an orchestrator
    giving periodic status summaries and pinging on new questions. Used once so far
    (practice_1). Revisit as a skill/`.claude/agents/` entry once a second app reuses it.
