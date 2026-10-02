# Pipeline, as you'd actually live it

A walkthrough of `PIPELINE.md` using practice_2 (a social media blocker for knowledge workers
on iPhone; research already done) as the running example. Six stages, roughly six
sessions, one file lands per stage and becomes the next stage's input.

---

## Stage 1 — Research  *(skill: `/research`)*

**You type:** `/research knowledge workers on iPhone who lose focus to social media`

**What happens:** Claude asks for the two things it needs if missing (the problem in one
line, any hard limit like "iPhone only"), then searches — App Store, review feeds,
Trustpilot — and writes `practice_2/research/focus-social-media-blockers.md`. Every quote is
verbatim with a link. Money numbers have a source or say "no public number."

**The gate:** the file ends with *"Strongest option: X. Why: one line."* — and stops. You
pick. Claude does not pick for you.

**Already done for practice_2.** The file lists Opal, one sec, Freedom, and the "friend holds
the key" group, with real complaints (Opal's notification nagging, the update that broke
blocking).

---

## Stage 2 — Positioning  *(no skill; PIPELINE §2 is the spec)*

**You type:** *"Positioning for practice_2, from the research."*

**What happens:** Claude reads the research file and proposes 2-3 candidates, one
paragraph each, every one in the form *"it's basically X, but Y"*:

> A. Basically **Opal**, but it never nags — zero notifications, ever.
> B. Basically **Jolt**, but the key-holder is a scheduled rule, not a friend you have to bother.
> C. Basically **one sec**, but the pause gets longer each time you push through it.

**The gate:** you react — "B, but I don't like calling it a rule" — and go back and forth
until one paragraph survives. Claude saves `practice_2/positioning.md` with the paragraph plus
the **Anchored to** block: 2-3 quotes pulled from the research file. That block is what
unlocks stage 3.

---

## Stage 3 — Spec  *(skills: `/create-prd` + `html-worker`)*

**You type:** `/create-prd` — and say "HTML mode."

**What happens:** Claude first checks `positioning.md` has evidence behind it (the
Anchored-to block). If not, it refuses and says so. Then it starts a local server, you
open `localhost:7777`, and the PRD is one long clickable page in a fixed order:
**the case → the experience → the build**.

Every technical choice is a radio group with three plain lines per option (what it is /
what you get and what it costs / when you'd pick it). Nothing is pre-selected. You'll see:

> **Database** ○ Postgres ○ SQLite ○ Supabase — *recommended: Postgres, because the
> series stack already uses it*

You click through, leave comments on specific blocks ("this screen is wrong, the block
should show *who* holds the key"), and press **Confirm & send**. Claude reads `INBOX.md`,
revises the page, tells you what changed. Repeat for 3-6 rounds.

**The gate:** you say "done." Claude runs `export-md.py` → `practice_2/PRD.md`. The PRD is
*generated from the page*, never hand-written, so it records what you chose *and* what
you rejected.

---

## Stage 4 — Contract freeze  *(no skill; PIPELINE §4 is the spec)*

**You type:** *"Freeze the contract from PRD §15-16."*

**What happens:** Claude — now acting as **orchestrator** — writes
`backend/app/schemas.py` and the empty route signatures in `backend/app/main.py`,
straight from the PRD's data model and API sections. Runs `export_openapi.py` →
`contract/openapi.json`. Sets up the CI step that fails if the JSON ever drifts from the
code.

**The gate:** you read the endpoint list — not the code, the list. *"POST /blocks,
GET /blocks/{id}/status, POST /unlock-requests…"* Does it match the screens from
stage 3? If yes, commit. From this moment the contract is frozen and only changes
through `ORCH-QUESTIONS.md`.

---

## Stage 5 — Build  *(no skill yet; PIPELINE §5 is the spec — skill candidate for practice_3)*

The one stage where you run **three sessions, not one.**

**Session 1 — orchestrator (you're here).** Claude writes `HANDOFF.md`,
`backend/AGENT.md`, `ios/AGENT.md`, creates two worktrees on branches `backend` and
`ios`.

**Sessions 2 and 3 — workers.** In each worktree you start a fresh Claude session and
type: *"Read AGENT.md and start."* Each one reads its brief, the PRD, the contract, and
builds TDD-first inside its own folder. The backend one builds the whole baseline (auth,
migrations, Docker, CI, metrics, Sentry, rate limiting, health) as it goes — it's in its
brief, not an afterthought.

**What you do while they work:** almost nothing, and that's the point. You watch the
orchestrator's status summaries. When a worker hits a contract problem, it doesn't patch
around it — it appends to `ORCH-QUESTIONS.md`:

> **Q3 — Unlock request needs a reason field**
> From: ios · Blocks: the request screen

The orchestrator pings you. You decide ("yes, add it, optional string, max 200 chars").
The orchestrator edits `schemas.py`, regenerates the contract, answers inline. Both
workers pull.

**The gate:** at each checkpoint the orchestrator merges a worker branch into `main` —
after *verifying* the claim (runs the tests itself, hits the endpoint), not just relaying
"backend says done." Done when the client runs end-to-end against the real local backend.

---

## Stage 6 — Ship  *(undefined — hosting decision parked, see PIPELINE.md open questions)*

**When it's defined, it'll look like:** the orchestrator runs a deploy skill — build
image, push to registry, host pulls, health check gates, rollback if red — and you film
the "bad deploy" scenario on purpose. Then TestFlight/store review for iOS, or a static
build for web. Then the showcase site.

---

## The pattern underneath all six

| | You | Claude |
|---|---|---|
| **Inside a stage** | react, comment, choose from options | search, draft, build, verify — the agent-shaped part |
| **At a stage boundary** | decide: pick, converge, approve, "done" | stop and wait — the workflow-shaped part |
| **The artifact** | read it | write it, and only ever read it back from disk |

That's why it can be trusted: **Claude never moves you to the next stage.** Every
transition is a file you've looked at plus a decision you've made. And each stage only
takes the previous stage's file as input — not chat history — so a fresh session, or a
compacted one, picks up exactly where the disk says you are.

Two honest gaps as of 2026-09-17: stage 5 is procedure-in-prose, so a fresh session
re-derives it from `PIPELINE.md` until practice_3 turns it into a skill; and stage 6 doesn't
exist yet. Everything else is real and has been run at least once.
