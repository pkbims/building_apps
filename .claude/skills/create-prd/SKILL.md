---
name: create-prd
description: Write a product requirements document that argues a case rather than listing features - problem and evidence, the requirements that evidence forces, then the experience, then the build. Use when the user has a chosen problem and needs it turned into a spec someone could build from. Works as terminal conversation or, with the html-worker skill, as a clickable review page; the structure is the same either way.
---

# Create a PRD

A PRD makes an argument: *this problem is real, therefore these requirements, therefore
this experience, therefore this system.* Sections exist to earn the next one.

Do not start until there is a chosen problem with evidence behind it. If there is only an
idea, say so and stop — the first part of this document cannot be invented.

## Order, and why it is fixed

Always **the case → the experience → the build**. The user settles why before how, and a
reader who stops after part one should still know whether the thing is worth making.

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

### Part 2 — The experience

7. **User flow** — end to end. A diagram earns its place here.
8. **Screens** — the actual interface. In HTML mode, make it clickable and let layout
   choices be selectable decisions.
9. **Success criteria** — one headline metric that measures the promise directly rather
   than a proxy for it. Say which percentile matters and why.
10. **Accepted risks** — see below.

### Part 3 — The build

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
    is still cheap.
19. **Open decisions** — everything unanswered, gathered.

## The disciplines that make it worth reading

**Plain words, for a reader who builds nothing themselves.** Write for someone who must
decide everything and implement none of it. Every technical term gets a short
plain-language gloss the first time it appears, inline — not in a glossary they have to
jump to. "Idempotency key" becomes "a unique ID the client sends so a retry doesn't
create two of something." Spell out each acronym once. No sentence should need a second
read. If a paragraph only makes sense to a reader who already knows the answer, rewrite
it. Simple wording is not the same as leaving things out — the document stays complete;
only the language gets easier.

**Every technical decision is the user's to make, and every option is explained.** In
Part 3, nothing about the stack, database, hosting, auth, vendor, client framework, queue
or storage is chosen silently or by the author. Each one is a multiple-choice decision the
user answers — a radio group in HTML mode, a numbered choice in terminal mode. For each
option give three plain lines: **what it is**, **what you get and what it costs**, and
**when you'd pick it**. You may mark one option *recommended* and give the reason in a
sentence, but never pre-select it and never collapse the choice to a single "obvious"
answer — the point is that the user makes the call knowingly. If you are genuinely blocked
and must pick something to keep drafting, record it in §19 as a provisional pick to
revisit, never as a settled default.

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

**HTML** — invoke `html-worker` for the mechanics. Same parts, same order, rendered as one
page with decisions as radio groups and every block commentable. Every decision's options
carry the three plain lines (what it is / what you get and what it costs / when you'd pick
it) right there in the page, so the user is never choosing between bare labels. Export
`PRD.md` from the page with `export-md.py`, and keep that exporter in the project so the
PRD can be rebuilt after any later change. The page is the document; the markdown is a
rendering of it.
