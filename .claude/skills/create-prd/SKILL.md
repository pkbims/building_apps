---
name: create-prd
description: Write a product requirements document that argues a case rather than listing features - problem and evidence, the requirements that evidence forces, then the experience, then the build. Use when the user has a chosen problem and needs it turned into a spec someone could build from. Works as terminal conversation or, with the html-worker skill, as a clickable review page; the structure is the same either way.
---

# Create a PRD

A PRD makes an argument: *this problem is real, therefore these requirements, therefore
this experience, therefore this system.* Sections exist to earn the next one.

Do not start until there is a chosen problem with evidence behind it. If there is only an
idea, say so and stop — the first part of this document cannot be invented.

In this series the inputs are `positioning.md` (the paragraph, the **USP**, the **viral
feature**, and for a new idea a **what it does** list, then the Anchored-to block) and the
research file (its **table stakes** — the features every competitor has). If the USP or
viral-feature line is missing, stop and say so: the v1 feature list is drafted from them.

## App Maker mode

When the session was started from the App Maker (its first prompt says "App Maker mode", or the
folder has a `.appmaker.json`), follow the `app-maker` skill's **Stage sessions** rules instead of
the page-server and terminal steps below: the page lives in the app folder and the app's one server
serves it — no page server of your own, no watcher; ask the user on the page with `post.py`; answer
Talk messages with `talk.py`; you are woken when the user presses Send.

## Order, and why it is fixed

Always **the case → the experience → the build**. The user settles why before how, and a
reader who stops after part one should still know whether the thing is worth making.

**The parts by name** (HTML mode; renamed 2026-09-26 so each name says what happens in it):
**The case → The experience (pick v1) → Can we build it? → Prototype v1 → Design direction →
Technical decisions → hand-over.** v1's features are chosen in *The experience*, so the
prototype is already v1's. *Technical decisions* is not the build: it is the choices behind
it — the building starts after the hand-over (stage 4 contract freeze, stage 5 build v1).

Never fragment this into tabs or separate files. One document, one thread of argument. Use
a contents rail for navigation and collapsible blocks for reference tables.

### Part 1 — The case

1. **Summary** — one paragraph. What it is, and the one thing it does that others don't.
2. **The problem** — with verbatim quotes and attribution. Never paraphrase evidence.
3. **Design requirements** — numbered **R1, R2…**, each with the evidence that forces it.
   *This section is the hinge of the whole document.* Without it, every later decision is
   a preference; with it, each one can be checked against something. Write it before any
   solution exists.
4. **Positioning** — the wedge, in one paragraph.
5. **Who it's for** — one audience. A PRD that serves everyone specifies nothing.
6. **Scope** — what it does, and an explicit list of what it does not. The exclusions
   matter more than the inclusions and are the section people skip.

### Part 2 — The experience (pick v1)

**Part 2 reads: §7 flow → §8 screens (sketches) → the v1 feature list → §9 → §10.** The
reader decides features far better after seeing the journey and the screens (app_1, round
5: the sketches exposed a conflict the feature cards never showed). So draw the flow and the
sketches for the **full set of candidate features**, greying out anything marked later, and
put the v1 feature list **after** them. The list is unnumbered on purpose: §7–§19 keep their
numbers, because existing PRDs and the other skills cite them (§8 screens, §16 contract).
Once decided, everything after it — prototype, spike, Part 3 — is organised around these
names.

Draft it from three sources, and say which each feature came from:

- **Table stakes** from the research — what every competitor has, so a user expects it.
  Or, for a new idea, the positioning's *what it does* list.
- **The USP** from positioning.
- **The viral feature** from positioning.

One card per feature: **name** (as a user would say it) → **the requirement it serves**
(R#) → **its screens** → **its endpoints** (a sketch until §16 is written) → **risk**
(*sure* / *unsure — spike it*, with one line on why).

The rule for what is v1: **a feature is in v1 only if the positioning's promise breaks
without it.** The viral feature is always v1 — a v1 nobody shares defeats the positioning.
There is no cap on the number; the rule is the cap. Everything that fails it is listed
underneath as **later** — named, so it is not lost, and picked up in stage 6. Each feature
is a checkbox the user moves between v1 and later; none is pre-decided.

7. **User flow** — end to end. A diagram earns its place here. **It must answer three
   moments, each as a decision, before Part 2 is confirmed:** *when sign-in happens* (before
   or after the first result, and what is shown before it), *what first run / onboarding looks
   like*, and *when we ask for money* (what is free, which actions hit the paywall — the price
   itself can wait). app_1 missed all three and had to add them after the prototype (round 11,
   2026-09-26); they change screens, the prototype and the design brief, so ask them early.
8. **Screens** — the actual interface. **Show every v1 screen as a simple phone sketch in
   the page itself, before Part 2 is confirmed** — the platform's plain look (on iOS: system
   font, grey grouped background, nav bar, inset lists, switches, a bottom sheet), grey
   boxes for photos, real labels and numbers. One sketch per screen, side by side. The user
   judges the features by seeing them, not by reading a list; the full clickable prototype
   still comes after Part 2 holds. Sketches often expose conflicts the text hides (app_1:
   the shared tour showed prices the unlock was meant to hide) — raise those as decisions.
   Layout choices are selectable decisions. `app_1/spec/sketches.py` is the first set —
   reuse its phone frame and iOS pieces.
9. **Success criteria** — one headline metric that measures the promise directly rather
   than a proxy for it. Say which percentile matters and why.
10. **Accepted risks** — see below.

### Between Part 2 and Part 3 — the prototype

Once the case and the experience have held through a review round, **build a clickable
prototype before writing a line of Part 3.** Reading a flow and feeling it are different;
the prototype is where the user finds the step that reads fine and plays wrong (practice_4:
"if I have minutes, why am I seeing tasks?"). Part 3 is then written from what the
prototype taught, not from what the flow diagram claimed.

What it is:

- One HTML file, `prototype.html`, served from the same html-worker directory as the PRD
  page, so it shares the server (`http://localhost:7777/prototype.html`). Start the server
  with `HOST=0.0.0.0` and give the user the Mac's LAN address too — the prototype is
  meant to be used on the phone. Publishing it as a private Artifact as well gives a link
  that works off the home network.
- Every screen from §8 and every path through §7, with the decisions recorded so far baked
  in — the prototype shows the product as decided, not a generic version of it.
- **The viral feature's shareable moment**: the screen or result someone would post, and
  the share action itself. Its worth can only be judged by feeling it, so it is never
  left for later.
- Styled to the platform's own conventions, not to the web: on iOS that is the system
  font, grouped background, inset lists, real switches, a tab bar, nav bars with a
  chevron. On a wide screen it sits inside a device frame; on the phone it is full-bleed.
  The user should be able to add it to the Home Screen and forget it is a page.
- Real sensors where a phone has them (motion, microphone, speech, share sheet), each with
  a visible "no sensor? simulate" fallback for the desktop. Time is compressed and the
  compression is printed on screen ("1 wallet minute = 2 seconds · nothing is real").
- State in browser storage so it survives relaunch, wrapped in try/catch, with a reset.

**Embed it in the PRD page** as its own part — *Prototype v1*, between the tests and the
technical decisions — in a phone-sized frame (an `<iframe>` of `prototype.html`), with the "what to notice"
list beside it, a link to open it full-screen on the phone, and a decision ("How does it
feel?"). Confirming that part is what unlocks the build. The user reviews the prototype
where they review everything else, and comments on it the same way.

What it is not: a backend, a build target, or a design system. It exists to be poked at
for an hour and then to inform §11–§18. Say in the terminal what to notice while using
it — the two or three places where the experience could still be wrong.

### After the prototype — the design brief

Once the prototype has been used and Part 2 still holds, run `create-ui-design-direction`
before writing Part 3. It produces `<app>/design/BRIEF.md`, the user runs Claude Design by
hand, and the handoff (`design/HANDOFF.md`, `design/tokens.json`, the canvas) comes back
before §14 is written — so §14 can name the token file and any bundled font as build
tasks instead of discovering them in stage 5, as practice_1 did.

### Before §12 — the spike, and what it does not test

§12 describes a mechanism. Some of it is documented behaviour; some of it is a bet on how
the platform or a vendor behaves under our exact use. **Do not write §12 as settled until
the bets have been run.** practice_1 wrote its mechanism first, spiked it after, and the spike
disproved it outright — the architecture was rewritten around the result.

**Explain the whole workflow first, then mark the bets inside it.** Open §12 with the
end-to-end job as numbered steps and a diagram, each step tagged *known to work* / *proven by
our spike* / *a bet — tested below* (bets visibly highlighted). Only then list the bets, each
titled with the step it tests ("Bet 1 · step 5 — …") and opening with "What we test:". A list
of bets without the workflow reads as noise — app_1's user could not tell what was being
tested or why (round 14, 2026-09-26).

So, between §11 and §12: list every belief the mechanism rests on, **grouped by v1
feature** — start from each feature marked *unsure — spike it* in the v1 list — plus one
**shared** group for bets that cut across features (a vendor's speed, a platform
permission every feature needs), so a shared bet is spiked once rather than per feature or
never. Then sort every belief into two tables the user reviews as a decision:

- **Spike** — bets that would *change the architecture* if they failed. Each row: the
  bet, why it is a bet (what is undocumented or unproven), the experiment, and what
  changes if it fails. These get a throwaway project (`<app>/spike/`) and a day.
- **Not spiked** — documented capabilities done daily by thousands of apps. Each row:
  the capability, the API, and one line on why it is not worth testing. Listed so
  nobody wonders; never tested. Accuracy tuning of a known API is a build task, not a
  bet. An accepted risk (§10) is not a bet either.

Testing the trivial wastes the day and hides the real risks in noise; skipping the real
risks produces practice_1's rewrite. The distinction is the point.

Results go back into the page as a table — experiment · result · what it changes — and
§12 onward is written from them.

**The build part opens with a "Ready for the build?" check.** A live checklist over the whole
page — every decision in the earlier parts answered, every part confirmed, every test done,
the prototype marked good, the design back and checked — each item ✓ or what's missing with a
link to it, and a **"Start the build part"** button enabled only when all are ✓. Pressing it
records `build_start = requested`, sends the round and shows the working bar; Claude then
writes the build part and sets it `done`. Test statuses live in `state.json`
(`test_<id>`), never only in the page, so the check can read them.

**One card per bet, in one place — nothing else on the PRD page.** Each card: the bet's name,
which workflow step it tests, a status, a one-line **verdict**, a one-line **what it changed**,
the decisions it settled (one line each, the full choice folded inside the card), and two
links — **Full report →** and **See the raw results →** (the folder of real output files).
Do not add a separate tracker, per-bet sections or a results table: app_1 grew all three on
top of each other and every verdict appeared four times (round 17, 2026-09-26).

**Every test gets its own report page** (`spec/bets/<bet>.html`, generated from the test's
own output files — never hand-written), linked from its tracker row and results row ("Open
the full report →"). Plain English, in this order: the verdict, what we tested and why, how
we ran it (step by step, with the code and output paths), what went in and what came out
(photos, videos, every item with price/store/link), the numbers, what to fix in the build,
what it changes in the plan. The PRD keeps a one-line summary per test; the detail lives in
the report. (app_1, 2026-09-26: the user couldn't read a whole test in a table cell.)

**The page tracks and starts the tests.** Put a **Test status** block at the top of the tests
part: one row per test with who runs it, a status (*ready to run → requested → running →
done*), the result once done, and what rides on it.

- **Tests Claude runs** (spikes) get a **"Run it now"** button. It records
  `test_<id> = requested`, sends the round and shows the "Claude is working" bar. When the
  inbox shows a requested test, set it to `running`, run it in `<app>/spike/`, then set
  `done` and write the result into the row and the results table — the bar flips when the
  page is rebuilt.
- **Tests the user runs** (anything needing their accounts or apps) show the steps and an
  **"I've run it"** button that opens a comment for the result; record it and mark `done`.
- Say what a spike needs from the user up front (e.g. "one photo of your room in
  `<app>/spike/input/`"), with a fallback if they don't provide it.

A test that was decided but never started is the gap this closes: the user should never have
to ask "when do we actually run this?" A bet that failed is struck through with what replaced
it, per the supersession rule below.

**The build part is organised by workflow, not by layer** (app_1, 2026-09-26). It opens with
**Overall decisions** — the choices every workflow shares (hosting, file storage, app framework,
how app and server talk, CI/CD, environments, which AI/search accounts; the series' fixed stack
stated, not asked). Then **one section per workflow**, named like `SignInWorkflow`,
`FindWhatsInTheRoomWorkflow`, covering *everything* the app does (not only what the bets tested),
each in the same shape: what it does (one line, as the user sees it) · how it works, step by
step, each step labelled App / Server / Worker / Service · what it stores · which calls it uses ·
when it fails and what the user sees · what we measure · what the bets found that applies ·
**the decisions it needs from the user**, each with a recommendation. After the workflows:
everything we store and every call (collected from the workflows), keeping it running, the build
order **by workflow**, riskiest first, and what's still open.

### Part 3 — Technical decisions

11. **Technical requirements** — numbered **TR1, TR2…**, derived from R1–Rn plus any
    project baseline. Requirements before solutions, again.
12. **Architecture** — how it works, and the mechanism the product depends on, in detail.
    Cover **every half of the system**, not just the server. See the symmetry rule below.
13. **Model or vendor choices** — with **rejected options and the reason for rejection**.
    Six months later this saves someone re-running every comparison.
14. **The client** — whatever the user actually touches: app, web front end, CLI. Name the
    framework, how the hardest screen is built, how the client is tested, how it is built
    and shipped, and which parts of the project baseline it carries. A platform is not a
    stack: "iOS", "web" or "mobile" answers *where*, not *in what*.
15. **Data model** — entities and fields.
16. **API contract** — every endpoint, body, response, error, auth, rate limit.
17. **Operations** — health, metrics, logging, failure handling, CI/CD, environments.
18. **Build order** — and put the part that could kill the project first, while stopping
    is still cheap. Sections are the **v1 feature names**, so each checkpoint in stage 5
    says which feature it finished. v1 is still one build toward one TestFlight release,
    not a series of releases.
19. **Open decisions** — everything unanswered, gathered.

**The PRD ends on a hand-over button** (HTML mode): "PRD is ready — proceed to build", enabled
only when every decision is answered; it records `prd_ready` and sends a round. On that
round, update `PROGRESS.md` (the app moves to 4. Contract freeze), write `<app>/HANDOFF.md`
(the orchestrator's brief), start the **code-orchestrator** session with
`.claude/scripts/start-agent.sh code-orchestrator <app> opus high "/code-orchestrator <app>"`,
set `prd_ready` to `done`, and stop. The `code-orchestrator` skill takes it from there: it
sets up the **engineering center** (the page the user watches from then on) and owns stages 4–5,
starting its workers on Sonnet at high effort.

## The disciplines that make it worth reading

**Plain words, for a reader who builds nothing themselves.** Write for someone who must
decide everything and implement none of it. Every technical term gets a short
plain-language gloss the first time it appears, inline — not in a glossary they have to
jump to. "Idempotency key" becomes "a unique ID the client sends so a retry doesn't
create two of something." Spell out each acronym once. No sentence should need a second
read. If a paragraph only makes sense to a reader who already knows the answer, rewrite
it. Simple wording is not the same as leaving things out — the document stays complete;
only the language gets easier.

**No codes in the prose the user reads.** Say "the result screen", not "S6"; "the room never
changes", not "R1"/"TR1". Codes can live in tables and ids, but never as the only name for a
thing — nobody remembers what S12 was (app_1, 2026-09-26).

**Show flows as simple top-down arrow diagrams**, one box per step, coloured by who does it
(App / Server / Worker / Service) — not numbered lists. Every workflow's "how it works" is a
diagram (`app_1/spec/part6.py` `flow()` is the model).

**Every technical decision is the user's to make, and every option is explained.** In
Part 3, nothing about the stack, database, hosting, auth, vendor, client framework, queue
or storage is chosen silently or by the author. Each one is a multiple-choice decision the
user answers — a radio group in HTML mode, a numbered choice in terminal mode. For each
option give three plain lines: **what it is**, **what you get and what it costs**, and
**when you'd pick it**. **You must mark one option *recommended* and give the reason in a sentence** (html-worker's
rule — every decision, every part of the PRD, not only Part 6). Never pre-select it and never
collapse the choice to a single "obvious" answer — the point is that the user makes the call
knowingly. If you are genuinely blocked and must pick something to keep drafting, record it
in §19 as a provisional pick to revisit, never as a settled default.

**Surface conflicts between decisions.** Individually sensible answers routinely combine
into an unsound whole — the widest promise plus the weakest input plus permission to ship
anyway. No single question catches this. Actively look for it after each round and raise it
as its own decision with a way out, not as a warning.

**Check both halves are specified to the same depth.** The server end attracts detail —
language, database, queue, storage, auth, deployment — while the client end often gets one
word and looks finished, because a platform name reads like a decision. Before calling a
PRD done, count the decisions on each side. If one has ten and the other has one, the
document is half written. The same trap applies to any second component: a worker, a CLI, a
scheduled job.

**Ask what the hardest screen or surface requires.** It usually drives the client stack
more than general preference does. Custom drawing, real-time interaction, camera work and
offline behaviour all rule frameworks in or out, and choosing on familiarity first means
discovering the constraint after the choice is expensive.

**Follow shipping requirements into every component.** A baseline demanding CI/CD, tests
and error tracking means something different for a mobile app than a container — signing,
store review, device testing — and that difference is where a plan quietly loses a
requirement it claimed to have.

**Record accepted risks properly.** State the failure concretely — inputs, then what the
user receives — name which requirement it breaks, say who accepted it and when, and give
the mitigation. A risk written down is doing its job; one omitted is a trap.

**Record superseded decisions.** When a later round overrides an earlier answer, mark the
old one struck through with what replaced it. A generator that ignores supersession
produces a document describing two different products.

**Generate the final file from the document itself**, not from a second narrative you
write alongside it. In HTML mode that means exporting the page (see `html-worker`'s
`export-md.py`); the decisions are injected from recorded state. A hand-written summary
that reads the same decisions will drift from the page within one round and will be a
fraction of its detail.

## Two modes

**Terminal** — work through the parts in order, in conversation. Produce `PRD.md` at the end.

**HTML — staged, one part at a time.** The page shows only the part under review; later
parts are visible as locked headings. Each part ends with a **"Confirm Part N — open Part
N+1"** button, enabled only when that part's decisions are answered. Pressing it records a
`gate` decision, sends the round (so Claude sees the answers and can revise the next part
before the user reads it), and unlocks the next part. A "reopen" link steps back. The order
is fixed: **the case → the experience (pick v1) → can we build it? → prototype v1 → design
direction → technical decisions**. *Can we build it?* holds the technical requirements (TR1…), how it
works (the whole workflow with the bets marked in it), and every bet with its test tracker
and results — the make-or-break check, run **before any design work**, because a failed bet
can change the screens, the positioning or kill the app cheaply. *Technical decisions* keeps only
the construction choices: tools and services (chosen from what the bets found), the app, data, API,
operations, build order. Decided on app_1 (2026-09-26) after the design was done while the
core mechanism was still untested — each its own part of the one page. Design direction is run by the
`create-ui-design-direction` skill *inside* this page (why, the answers in plain words, a
status tracker with a "Handoff is back" button), not on a separate page. Never show
the user a part whose earlier part isn't confirmed. `app_1/spec/build.py` is the first page
built this way — reuse its `gate()`, the lock CSS and the gate script. Same layout as the
research page: plain English, visible part headings, a progress column **beside** the
decisions and feedback queue (four columns, never stacked).

**HTML** — invoke `html-worker` for the mechanics. Same parts, same order, rendered as one
page with decisions as radio groups and every block commentable. Every decision's options
carry the three plain lines (what it is / what you get and what it costs / when you'd pick
it) right there in the page, so the user is never choosing between bare labels. Export
`PRD.md` from the page with `export-md.py`, and keep that exporter in the project so the
PRD can be rebuilt after any later change. The page is the document; the markdown is a
rendering of it.
