# The question catalogue

What goes on the brief-review page, in order, and how each block's options are derived
from the app's own files. Derive, don't invent: an option the user has never seen a reason
for is a bare label, and bare labels get picked at random.

Every block: a `.d` decision with `data-anchor`, a `data-radio` (one answer) or
`data-check` (several), and options carrying **what it is / what you get and what it
costs / when you'd pick it**. Recommended option first, marked, never pre-selected. Every
block commentable so free text can arrive as a change request.

Above the questions, one short section titled **"Fixed by the series — say so if you
object"** listing D3 (two directions first), D4 (handoff + tokens back), D5 (light only),
D6 (no accessibility floor), D7 (no repo connection). Plain text, commentable, no radios.

---

## Q1 · Navigation model  `nav` · radio

Derive from `spec/prototype.html`: does it have a tab bar (how many tabs, named), a single
push stack, or a modal flow from a home screen? Offer the prototype's actual structure
first, then the one or two plausible alternatives.

Second radio in the same block, `done-lands`: after the main loop completes, where does
the user land? Options are the screens from PRD §8 that could plausibly be a home.

## Q2 · Device range  `device` · radio

iOS: iPhone only / iPhone + iPad / iPhone with the smallest supported width named.
Cost line for each: iPad doubles layout work; naming the SE width makes the designer
test the narrow case. Web (when the first web app arrives): breakpoints and browsers.

## Q3 · Screens to add  `add-screens` · check

The candidates from step 1 — screens the flow needs that §8 does not name. Typical:
Home / list of things, Settings, account or credits, sign-out, the "done" landing, a
paywall if §6 mentions a paid tier. Each checkbox says which PRD line implies it. Checked
ones go into the brief's §4 with their states.

## Q4 · Vibe — three words  `vibe` · radio

Three candidate triads. Derive: one from the positioning's own adjectives, one from what
the research's complaints are *against* (if users hate "cluttered" and "salesy", a triad
that answers it), one deliberately different in register (if the first two are calm,
make the third bold). Each option's cost line says what the triad rules out.

Free text ("warm, editorial, a little wry") arrives as a change comment — add it as a
fourth option next round, unselected.

## Q5 · Like / not like  `like` · check, `not-like` · radio

Like: the competitors the research names, plus one or two well-known apps outside the
category whose *surface* fits the vibe. Cost line: what copying it would drag in.
Not like: one app, and the one thing about it we reject. This is the most useful line in
the brief — a designer can do more with one "not like" than three "likes".

Each checked "like" needs one screenshot in `references/`. Ask for it in the terminal
after "done"; do not block the page on it.

## Q6 · Copy voice  `voice` · radio

Three triads again, derived from how the PRD itself is written (the PRD's own sentences
are the closest thing to a voice sample we have) and from the positioning. Distinct from
Q4: vibe is how it looks, voice is how it talks. They can differ ("looks calm, talks
blunt").

## Q7 · Real data  `real-files` · check, `real-numbers` · comment-only

Every candidate file found in step 1, one checkbox each, with its path and what it is.
Checked files are copied into `design/references/` with descriptive names.

Below it, a plain block listing the numbers the product shows (from §8 and §9 — a
score, a count, a balance, a duration) with the real range you can derive from the spike
or the PRD. Commentable; corrections arrive as change requests.

## Q8 · The side-by-side screens  `ab-screens` · check (exactly two)

Default: the hardest screen (from §13/§14) and the home. Options are every screen in §4.
The why line: these two carry the vibe or nothing does — the hardest because it is the
product, the home because it is opened most.

## Q9 · Open for invention  `surprise` · check

The list from the 2026-09-20 review round-1 answer:

- Motion between screens
- The one moment that deserves animation — and which (a sub-radio `moment` over §4's
  screens, shown only if this is checked)
- Illustration, or a character / mascot
- Sound and haptics
- The app icon, name treatment, splash
- How deep onboarding goes

What is checked goes into the brief's §7 as "Surprise us on:". What is unchecked is not
mentioned — silence leaves it open by default without inviting a mascot nobody wants.

---

## What is deliberately *not* asked

- Palette, font names, radii, shadows — those are the designer's answers. Asking them
  turns the brief into the design.
- Dark mode, accessibility floor — series rules (D5, D6). Stated, not asked. If the user
  objects in a comment, that is a change to the series decision, made in
  `design-brief-review/`, not per app.
- Whether to run Claude Design at all — that is D2, settled: the user runs it by hand.
