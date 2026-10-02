# Design brief review — how we brief Claude Design

Generated 2026-09-20 from `design-brief-review/index.html` and `design-brief-review/state.json`.
2 review rounds · 7 decisions recorded · 7 decision points in the document.

> Generated file — do not edit by hand. Change the page or the decisions and re-run
> `OUT=<file> TITLE="<title>" python3 design-brief-review/export-md.py`.

---

# Start here

## What this page is

*A review of how we hand our UI work to claude.ai's Design tool (Claude Design), built from what is actually on disk in `app_1/` and `app_4/`, not from memory.*

Three questions, in three parts, then a proposal. Part 1 reconstructs what Claude Design effectively received. Part 2 walks a product designer's checklist against that and marks each item provided, partly or missing, with the file that proves it. Part 3 proposes a brief template we would reuse for every app, and every place I had to choose between options is a decision for you.

> **The headline finding:** Claude Design has been used exactly once in the series (app_1, 2026-09-08), and **no literal prompt was saved**. The "brief" was the GitHub repo itself: Claude Design was connected to `pkbims/test_app_1` and read `PRD.md`, `positioning.md` and `research/` on its own. Everything it did not find there, it invented — and told us so in its own output header.

app_4 has not been through Claude Design at all. Its clickable prototype was built by Claude Code inside the `create-prd` skill, which is a different tool doing a different job. Part 1 covers both, because app_4 is the app that would go through Claude Design next and its artifacts are what a brief would be built from.

---

# Part 1 · What we provide today

## The one time it happened — app_1, 2026-09-08

*Reconstructed from git timestamps, Claude Design's own sync note, and the output file.*

> [!WARNING]
> **What that timeline says.** Claude Design got the richest possible *product* input — a 722-line PRD with numbered, evidenced decisions — and zero *design* input. It produced a good screen set and its own aesthetic, and two days later we did a second visual pass in a different tool to get the aesthetic we actually wanted, plus the token-level spec the build needed. The brief was missing exactly the things the second pass supplied.

## What was effectively provided

*There is no prompt to quote. What follows is what existed in the repo at 17:06 on 2026-09-08 and what Claude Design's own screen map says it used.*

| Artifact on disk at that moment | What it gave the designer | Proof it was used |
| --- | --- | --- |
| `positioning.md` | The one-paragraph wedge ("basically DecorAI, but it never invents architecture"), the user in one line, two verbatim complaints. | Screen map row "Copy + tone: positioning.md, research/home-decorating.md". The sign-in headline it wrote — "Restyle your room, not somebody else's." — is the positioning restated. |
| `PRD.md` §5 Who it's for, §6 Scope | "Someone who has just moved in… furniture that does not suit the new place." Seven explicit exclusions. | No shopping, AR or sharing appears in any screen. |
| `PRD.md` §7 Flow, §8 Screens | A mermaid flow with a decision branch (confident / low confidence), and eight named screens each with 3–5 bullets of intent and the decision IDs they serve. | Screen map maps every built screen to "PRD.md §8 <name>" plus the decision IDs (D13, U2, T12, F2…). |
| `PRD.md` decision records (D1–D14, U1–U4, F1–F5, C1–C4, T1–T14) | Which choices were settled and which were still open — the PRD marks the chosen option with **→**. | The export header lists "TAKEN AS SETTLED: geometry-only lock (D10b), one photo (U1 silent), account first via Apple (D13)…" and builds U2/F2/U3/U4 as switches because they had no arrow yet. |
| `PRD.md` §9 Success criteria | Fidelity (preservation rate) is the headline metric and must be shown, not hidden. | Compare screen shows "94% STRUCTURE KEPT" as the largest element. |
| `PRD.md` §13 The iOS app | Platform (iOS), stack (Swift + SwiftUI, F1), and "the outline screen is the hard one — it is real drawing work." | Built in an iOS 26 device frame (`ios-frame.jsx`), Sign in with Apple, system font for tappable things. |
| `PRD.md` §16 "Every error" | Eight error codes, each with the exact sentence the user sees. | Six edge states built; screen map row "Error / edge states: PRD.md §16". |
| `spec/index.html` wireframes | Low-fi phone mockups drawn in HTML inside the PRD page (the `SCREENS` array, ~264 px phones with placeholder slots). | Claude Design says "the repo contains no app UI" — it either did not open the spec page's JavaScript or did not count it. Effectively **not** used. |
| `research/home-decorating.md` | 63 verbatim complaints from 45 people. | Used for copy tone (per screen map). The "We never move your walls" trust line is a direct answer to the complaints. |

And the things that were *on the machine* but not in the repo, so not seen: the real test photo `inputs/room.jpg` (added in the spike a day later), the six style sample photos (added 2026-09-10 to `options_review/images/`), and the series constraints in the parent `CLAUDE.md` ("restyling must stay cheap", "UI changes must not touch business logic") — which live one directory up, outside the app's repo.

## What Claude Design told us it invented

*The export's own header — the best evidence of the gaps, because the tool wrote it.*

> **THE AESTHETIC I PICKED** — "Editorial and quiet: warm paper, one ink, Instrument Serif for the sentences that carry the promise, system sans for anything you tap, monospace for anything the machine is asserting. Colour appears only in the overlays — so colour *means* 'protected'."

> **THE ALTERNATIVE, IF YOU WANT IT** — "A surveyor's aesthetic — mono-first, measurements visible, outlines drawn like a survey rather than a design app… Say the word and I'll build it beside this."

> **PLACEHOLDERS** — "No photography yet, so every room is a labelled plate with the detected geometry drawn on it at true position. Drop real photos in and the overlays sit on top unchanged."

Three admissions: it chose the brand direction itself, it offered an alternative because nothing told it which way to go, and it had no real imagery for a product whose entire promise is about a photograph. It also added a screen the PRD did not list — a "Rooms" list with "0 FREE ROOMS LEFT" — because a flow needs somewhere to land, and nobody had said what Home was. Two days later the v2 pass made Home the flagship screen.

Its aesthetic was *not* carried into the build. v2 chose Fraunces over Instrument Serif and a clay accent over "one ink"; only the headline "It's still your room." survived, borrowed back into v2's sign-in screen (v2 `HANDOFF.md` §2 says so explicitly).

## app_4 — what a brief today would be built from

*Not yet through Claude Design. PRD closed 2026-09-20 after ten review rounds and seventeen decisions (per `PROGRESS.md`); the app is at stage 4, contract freeze. A design run for app_4 would therefore happen the way app_1's did — after the full PRD — whatever D2 below settles for the apps that follow.*

- **`positioning.md`** (2026-09-19) — the wedge, three anchored quotes, and a "Left out on purpose" block. Stronger than app_1's because it names what the paragraph does *not* promise.
- **`spec/index.html` §8** — eleven screens in a table with three columns: *Screen · What's on it · Requirement it serves*. Names the hardest screen (the empty-wallet menu) and says why it shapes the client stack. Three layout decisions (D7, D8, D9) each with three plain-language options.
- **`spec/index.html` §14** — the client in detail: SwiftUI iOS 17+, a tab bar (Wallet · Earn · Receipt · Settings), three extensions, "the hardest screen is M3, copy the move… 30 fps, without dropping the counter."
- **`spec/prototype.html`** (45 KB) — built by Claude Code per the `create-prd` prototype step. It has what app_1's brief lacked: a **token set** (`--bg --card --ink --muted --tint --warn --bad --good`), a **dark theme** via `prefers-color-scheme`, iOS conventions (grouped background, inset lists, real switches, 44 pt rows), an installable Home Screen icon, compressed time printed on screen.

> **So app_4 is already ahead of app_1 on three checklist items** (screen inventory with the requirement each serves, tokens, dark mode) — but by accident of the prototype step, not because a brief asked for them. Nothing yet says what app_4 should *look like*, what tone its copy has, or what the designer is allowed to change.

---

# Part 2 · What we are not providing

## A designer's checklist against the app_1 brief

*Each item is what a product designer would expect in the brief. Status is for app_1 on 2026-09-08 — the only real data point — with a note where app_4 would differ today. Every item is its own comment anchor.*

### Screen inventory partly

PRD §8 lists eight screens with intent bullets. But the list is the *flow*, not the app: there is no Home, no room list, no room detail, no settings, no sign-out. Claude Design invented a "Rooms" screen; the build added Home and Room detail; v2 made Home the flagship. Three screens the product shipped with were never in the brief.

### Every state per screen — empty, loading, error, success partly

Error is the strong one: PRD §16 gives eight error codes with the exact user-facing sentence, and Claude Design built six edge states from it. Loading exists once (the Rendering screen, because it is a product moment). Empty and success are absent: no empty Home, no "first render done" state, no "credits used up" state on Home. The v2 pass had to write the empty-state copy itself ("No rooms yet…").

### User and job-to-be-done provided

The best-covered item. Positioning names the user in a sentence; PRD §5 gives one audience and says why it matters ("sets what 'keep my furniture' means"); §2 carries verbatim complaints so the designer hears the user's own words.

### Brand direction and references missing

Nothing. No adjectives, no reference apps, no "like X, not like Y", no images. Claude Design's header says "THE AESTHETIC I PICKED" and offers a second one unprompted. The direction we actually wanted only surfaced through review reactions in v2 ("Make this more interesting", "Very Cool" on the mosaic) and a side-by-side of two accents — that is brand direction discovered by iteration, which costs a round each time.

### Tone of copy partly

Tone is inferable — the PRD is written in plain, short, slightly wry sentences and the positioning has a voice — and Claude Design inferred it well ("One free room, three restyles, no card." / "We never move your walls."). But nothing states it, so it is not checkable, and the two copy changes in v2 ("My Latest Decors", "Decorate a New Room") were the user's taste arriving as comments, not a rule the designer could have applied.

### Platform and device provided

iOS, Swift + SwiftUI (F1), and which screen is hard and why (§13). Claude Design used an iOS 26 frame and platform controls. The one hole is device range: nothing says iPhone-only vs iPad, or the smallest screen we care about. The series CLAUDE.md settles the two client types (iOS or web) but that file is outside the app repo.

### Design tokens, and the series rule that restyling must stay cheap missing

The series constraint — "Restyling must stay cheap. UI changes must not require touching business logic" — is in the parent `CLAUDE.md`, which is not in the app repo and was never passed to the designer. The Claude Design export is styled with inline hex values on every element. Tokens first appear in v2's `HANDOFF.md` §1 (14 colours, three type roles, a spacing scale, radii, two shadow tiers), and the build turned that into `DesignTokens.swift` and 14 named colour sets. That is exactly what the brief should have asked for in the first place, and now there is a precedent to hand over as the required output shape.

### Navigation model partly

app_1's PRD gave a linear flow with one branch and the loop style → render → compare. It did not say whether the app has tabs, a stack, a modal flow, or where you land after "Save". Claude Design had to guess ("Rooms" list). app_4 is explicit: "Tab bar: Wallet · Earn · Receipt · Settings (as the prototype)" — but that sentence lives in §14 The iOS app, a build section, not in the experience part a designer reads.

### Which data is real and which is placeholder missing

For a product about photographs, the designer had no photograph. "No photography yet, so every room is a labelled plate." A real room photo existed on the machine (`inputs/room.jpg`, the spike input) and six style samples existed two days later; neither was in the brief. Nothing said which numbers are real (fidelity 94%, credits "2 left", "usually under a minute") or which strings come from the API verbatim (the §16 error messages are contract strings the client must show as-is — the designer should be told they cannot rewrite them).

### Accessibility missing

Not one mention anywhere — not in either PRD, not in the v2 handoff, not in the worker briefs. No Dynamic Type, no VoiceOver, no contrast target, no minimum tap size. The confirm screen in app_1 (tap letters on a photo) and the shield screen in app_4 (Apple's, our words) are both places this would bite. The one accidental win: app_4's prototype uses 44 pt rows and `focus-visible` outlines.

### Dark mode partly

Never asked for in a brief. app_1 v2 explicitly ruled it out ("out of scope for this pass… a deliberate single warm-light system") and the app ships light-only. app_4's prototype has a full dark theme because the html-worker template does. So the series has no position: one app says no, one app's prototype says yes, and no brief has ever said either.

### What is fixed and what is open for the designer partly

The PRD's decision records did this job well by accident: a **→** marks the chosen option, and Claude Design correctly read U2/F2/U3/U4 as open and built them as switches. What was never said: the *flow* is fixed and the *look* is entirely open; copy is open except contract strings; the designer may not add a screen without flagging it (it added "Rooms" silently). The v2 handoff shows the right shape — "This covers restyling only. No flow, endpoint, or state-machine logic changes" — but that was written *after* the design, as a constraint on the build.

### The output format we need back missing

Nothing was asked for, so we got Claude Design's default: a `.dc.html` canvas, a `.jsx` frame, and a sync note. The iOS worker was told to "open it in a browser". Two days later the build needed something else — a per-screen table of exact values against named source files — and got it from v2's `HANDOFF.md`, which is the de facto handoff format the series has actually built from. A brief should ask for that shape on the way out: tokens as a table, per-screen changes against the screen inventory, states enumerated, and "hold off on" items listed.

### The hardest screen, and the number the product is staking itself on provided

Two things the PRD does that most briefs do not: it names the hardest screen and why ("the outline screen is the hard one — it is real drawing work" / app_4: "M3, copy the move… 30 fps"), and it names the headline metric and says it must be visible (fidelity, 5th percentile). Claude Design made 94% the largest thing on the Compare screen. Keep both in the template.

### Scorecard — the checklist in one table

| Item | app_1 brief (2026-09-08) | app_4 artifacts today |
| --- | --- | --- |
| Screen inventory | partly 8 flow screens, no Home/list/detail | partly 11 screens + tab bar, no Settings |
| States per screen | partly errors yes, empty/success no | missing no state column |
| User and JTBD | provided | provided |
| Brand direction and references | missing | missing |
| Tone of copy | partly inferable, unstated | partly |
| Platform and device | provided (device range no) | provided |
| Tokens and restyle-cheap rule | missing | partly prototype has tokens, rule unstated |
| Navigation model | partly | provided (in §14, not §8) |
| Real vs placeholder data | missing | missing |
| Accessibility | missing | missing |
| Dark mode | missing (later ruled out) | partly prototype has it, nobody decided |
| Fixed vs open | partly via decision arrows | partly |
| Output format back | missing | missing |
| Hardest screen + headline metric | provided | provided |

---

# Part 3 · What we should provide

## What we should provide — the principle

The PRD already carries the product half of a design brief better than most design briefs do. What it lacks is the design half, and the design half is short: a direction, a token contract, a state grid, and the shape of the answer. So the proposal is **not** a new document to maintain. It is a one-page `DESIGN_BRIEF.md` generated from the PRD page's export plus a small block of design-only facts we write once per app — and the series rules that never change live in the template, not in each app.

> **Tradeoff, in a sentence:** a brief that repeats the PRD drifts from it within one round (the same reason `PRD.md` is generated, not written). A brief that only *points* at the PRD leaves the designer to find §5, §8, §9, §13 and §16 on their own — which is what happened, and it mostly worked. The middle: the brief quotes the PRD's screen table and error table by generation, and adds only what the PRD does not hold.

## Decisions — where I had to choose

*Each of these changes the template in §8. Nothing is pre-selected; the recommended option is first and says why.*

**D1 — Where does the brief live, and how does Claude Design get it?**

*Claude Design read the repo by GitHub connection last time. Whatever we write has to be where it will look.*

**→** **A file in the app repo, <app>/design/BRIEF.md, committed before the run (recommended)** — What it is: one Markdown file next to the PRD, generated + hand-written block. What you get / costs: Claude Design's GitHub sync finds it; it survives context resets; it is what the iOS worker reads later too. Costs one more generated file to keep in step. When you'd pick it: you want the designer and the builder to read the same thing — which is the series' whole method.
  · A prompt pasted into Claude Design each time, from the template — What it is: fill the §8 template, paste it. What you get / costs: fastest; nothing new in the repo. Costs: the exact brief is lost unless someone saves it — which is precisely the gap this page found. When you'd pick it: you treat the design run as disposable.
  · Both — file in the repo, and the paste is one line pointing at it — What it is: the file is the brief; the pasted prompt says "read design/BRIEF.md first, then the PRD". What you get / costs: the file is durable and the run is reproducible. Costs: two steps. When you'd pick it: you are not sure the GitHub sync reads a new file without being told.

**D2 — When in the pipeline does Claude Design run, and who runs it?**

*app_1 ran it after the whole PRD was done. app_4's create-prd now builds a prototype between Part 2 and Part 3.*

**→** **After Part 2 holds, as the visual layer on top of the Part-2 prototype (recommended)** — What it is: Claude Code's prototype settles the flow and states; Claude Design then gets the brief + prototype and does look, tokens and copy. What you get / costs: the designer works on a flow that has already been felt on a phone, so fewer "this step plays wrong" rounds. Costs: two artifacts (prototype, design) that must agree; a flow change after the design run costs a redesign. When you'd pick it: the prototype step in create-prd is staying.
  · After the full PRD, before contract freeze — what app_1 did — What it is: the designer sees the finished document including the client stack. What you get / costs: maximal context; the build brief can point at the design from day one. Costs: Part 3 is written from a flow diagram, not a felt flow — the thing the prototype step was added to fix. When you'd pick it: you drop the prototype step.
  · Instead of the Part-2 prototype — Claude Design's clickable output is the prototype — What it is: one tool, one artifact. What you get / costs: no duplication. Costs: the .dc.html is a canvas in a device frame, not a phone-installable page with sensors and compressed time — the things create-prd asks the prototype for. When you'd pick it: the prototype's sensor/time features turn out not to matter for the next app.

**D3 — Who sets the visual direction?**

*app_1's direction was picked by the tool, then overridden two days later by a side-by-side (moss vs clay) and a comment ("make this more interesting"). Neither is a brief.*

**→** **We write three adjectives + two reference apps + one "not like"; the designer builds two directions side by side; we pick one in round 1 (recommended)** — What it is: a short direction block in the brief, and a required A/B as the first deliverable. What you get / costs: the choice the v2 round made by accident (clay vs moss) becomes the designed first step; cheap to write, one round to settle. Costs: one extra round before screens. When you'd pick it: you want on-camera a moment where the look is chosen for a stated reason.
  · We dictate the palette and type up front, from a series house style — What it is: one token set for the whole series, per-app accent only. What you get / costs: every app looks like it is from the same studio; zero direction rounds. Costs: the apps stop being distinguishable; a house style has to be designed first. When you'd pick it: the series brand matters more than each app's.
  · Platform default — Apple HIG look, system font, one accent colour, nothing else — What it is: what app_4's prototype already is. What you get / costs: fastest, most accessible by default, restyling is trivially cheap. Costs: looks like a demo app — the thing the series exists to not be. When you'd pick it: an app whose value is entirely in the mechanism, not the surface.

**D4 — What do we ask for back?**

*The build read a handoff table (v2 HANDOFF.md), not the canvas. Whatever we ask for should be the thing a worker brief can point at.*

**→** **Canvas + HANDOFF.md in the v2 shape + a tokens.json (recommended)** — What it is: the clickable .dc.html as the picture; a Markdown handoff with §1 visual system, §2 per-screen changes, §3 states grid, §4 hold-off list; tokens as one machine-readable file. What you get / costs: the worker brief points at two files and the build converts tokens by script (DesignTokens.swift or tokens.css). Costs: the designer must write the table, which it will only do if asked. When you'd pick it: you have already built from this shape twice (v2, options round).
  · Canvas only — the worker reads the design by opening it — What it is: what app_1 did. What you get / costs: nothing to ask for. Costs: exact values must be read off the page by the worker; the v2 round shows that is not enough. When you'd pick it: never, given the evidence — listed so the rejection is on record.
  · Code — SwiftUI views or a CSS file, straight from the design tool — What it is: ask Claude Design for implementation. What you get / costs: no translation step. Costs: it cuts across the stage-5 worker's ownership of ios/, and the restyle-cheap rule needs the views to be dumb layers over a state machine the designer knows nothing about. When you'd pick it: a web app where the design tool's HTML is the deliverable — decide again when the first web app arrives.

**D5 — Is dark mode a series rule?**

*app_1 said no (deliberately). app_4's prototype has it (accidentally). The template needs one line either way.*

  · Required from the first brief — every token has a light and a dark value (recommended) — What it is: the tokens file carries two columns; the designer shows every screen in both. What you get / costs: iOS users who run dark get a real app, not a white flash; it forces the token discipline that makes restyling cheap. Costs: roughly a third more design work on the first pass; photo-heavy screens need scrim rules twice. When you'd pick it: the baseline says "nothing here is faked".
  · Per app — the brief states yes/no and the PRD records why — What it is: a line in the brief. What you get / costs: app_1's "deliberate single warm-light system" stays legitimate. Costs: a decision to make every time, and a token set that may not be two-column when a later app needs it. When you'd pick it: some apps are genuinely one-mood (a photo product may be).
**→** **Light only for v1 of every app, dark as a documented v2 item** — What it is: what app_1 did, made the rule. What you get / costs: fastest first pass. Costs: an item the series always promises and never ships — the demo-app smell. When you'd pick it: throughput over completeness.

**D6 — What is the accessibility floor in every brief?**

*Currently nothing, anywhere. The template needs a floor or it will stay nothing.*

  · A fixed floor in the template: 4.5:1 text contrast, 44 pt tap targets, Dynamic Type up to the accessibility sizes on every list screen, VoiceOver labels on every control (recommended) — What it is: four lines that never change. What you get / costs: checkable; the designer designs to it; the worker tests to it. Costs: Fraunces-at-34pt-on-a-photo kind of choices get harder. When you'd pick it: it costs almost nothing to state and everything to retrofit.
  · Mention it, no numbers — "follow Apple's accessibility guidance" — What it is: one sentence. What you get / costs: something rather than nothing. Costs: unverifiable, so it will be skipped the way "error tracking" is skipped when it is not a line item. When you'd pick it: you trust the tool's defaults.
**→** **Leave it out of the brief; handle it in the build stage** — What it is: status quo. What you get / costs: no design constraint. Costs: layouts that cannot grow with Dynamic Type get discovered after they are built. When you'd pick it: never recommended — on record as the current state.

**D7 — Does Claude Design get the repo, or only the brief?**

*Last time it got the whole repo and found what it needed. But the repo also contained a 1,196-line spec page it did not read and, from stage 5 on, will contain the code.*

  · The repo, with the brief telling it the read order (recommended) — What it is: GitHub connection as before; BRIEF.md §0 says "read this, then PRD §5, §7, §8, §9, §13, §16, then prototype.html; ignore spec/ tooling and backend/". What you get / costs: it can quote the PRD directly; the read order stops it re-deriving the product. Costs: on a re-run after build starts it will see Swift files and may design to what exists. When you'd pick it: you re-run the design tool before the build, not during.
**→** **Only the brief and the files it names, uploaded — no repo connection** — What it is: paste/upload BRIEF.md, PRD.md, photos. What you get / costs: exactly controlled input; reproducible. Costs: manual; the sync note that served as our only record last time goes away. When you'd pick it: mid-build restyles where the code must not steer the design.

## The brief template — `<app>/design/BRIEF.md`

*Updated to the decisions recorded in round 2: the file lives in the repo (D1), Claude Code generates it after Part 2 and **you paste it into Claude Design yourself** (D2); two directions first (D3); handoff + tokens back (D4); light only for v1 (D5); accessibility handled at build, not in the brief (D6); the brief plus the files it names, no repo connection (D7). Blocks marked *generated* come from the PRD page's export; *written* blocks are the per-app design facts added once; the rest is the series template.*

```
# Design brief — {{app}}                                  ← written

## 0. How this brief is used                              ← D2 · D7
Generated by Claude Code after Part 2 of the PRD holds. Pasted
into Claude Design by hand, with these files attached — no repo
connection: PRD.md · spec/prototype.html · design/references/*.
Read in that order. Everything you need is in what is attached;
if something is missing, ask rather than infer it.

## 1. What this is, and for whom                          ← generated
{{positioning paragraph}}
{{PRD §5, verbatim}}
Two things people said, in their words:
{{two anchored quotes from positioning.md}}

## 2. Platform and device                                 ← written
iOS · iPhone only · smallest supported: iPhone SE (3rd gen) width
· iOS {{n}}+ · SwiftUI. (Web apps: browsers, breakpoints, and
whether the design tool's HTML is the deliverable — decide in the
first web app.)

## 3. Navigation model                                    ← written
{{one sentence: tab bar with N tabs named … / single stack /
modal flow from a home screen}} Where "done" lands: {{screen}}.

## 4. Screen inventory, with every state                  ← generated + written
| # | Screen | What's on it | Serves | Empty | Loading | Error | Success |
Every row from PRD §8, plus the screens the flow needs but the
PRD does not list: Home, Settings, sign-out, account/credits.
Each state cell: "—" if that state cannot happen, otherwise the
copy or a pointer to §16. No cell is left blank.
The hardest screen is {{name}}: {{PRD's sentence on why}}.

## 5. Copy                                                ← written
Voice: {{three adjectives}}. Sentences short; second person; no
exclamation marks; say what we do, not what we are.
Fixed strings — show verbatim, do not rewrite:
{{PRD §16 "What the user sees" column, generated}}
Open copy: everything else. Propose; we approve per screen.

## 6. Data: real vs placeholder                           ← written
Real, use these: {{design/references/room.jpg …}} — a real
{{thing}} from a real phone. Numbers on screen are the product's
real range: {{e.g. fidelity 0.85–0.99, credits 0–3}}.
Placeholder is not acceptable for {{the artifact the promise is
about}}. Placeholder is fine for {{avatars, dates}}.

## 7. Visual direction                                    ← written · D3
Three words: {{editorial · warm · quiet}}.
Like: {{two shipping apps, one screen each in references/}}.
Not like: {{one app, and the one thing about it we reject}}.
First deliverable: two directions, side by side, on the two
screens that matter most ({{hardest screen}}, {{home}}). We pick
one before any other screen is built.

## 8. Tokens — the contract with the build                ← series rule
Every colour, type role, spacing step, radius and shadow is a
named token. No literal values in screens. Deliver tokens as
tokens.json. Light appearance only for v1; dark mode is a
documented v2 item, so keep every colour a token now so the
second column can be added without touching a screen.   ← D5
The build converts this file by script (app_1 precedent:
ui_design_v2/HANDOFF.md §1 → DesignTokens.swift). Changing the
look later must be a change to this file, never to a view, and
never to business logic (series CLAUDE.md).
Type: at most three roles (display / UI / meta). A bundled font
is a real build task — name the exact weights.

## 9. Accessibility                                        ← D6
Not part of this brief; handled in the build stage. Do not
design to a floor we have not set.

## 10. What is fixed, what is open                        ← generated + series rule
Fixed: the flow (§7), the screen list (§4), the decisions marked
→ in the PRD ({{list of IDs}}), the contract strings (§5).
Open: everything visual, all unfixed copy, layout within a screen.
Still undecided in the PRD — build as switches and compare:
{{decision IDs with no → yet}}
Adding a screen, a step, or a permission ask is a change request
to us, not a design choice — flag it, do not build it silently.

## 11. What we need back                                  ← series rule · D4
1. The clickable canvas, in the device frame, every screen in
   every state from §4, both themes.
2. HANDOFF.md in this shape (app_1 precedent, ui_design_v2/):
   §1 visual system as tables · §2 per-screen changes against
   §4's numbering · §3 the states grid, filled · §4 hold-off /
   sequence-carefully list · §5 rejected alternatives, one line
   each, so they are not re-proposed.
3. tokens.json.
4. references/ back with any new imagery, named.
All of it goes into <app>/design/. The build stage's worker
brief points at 2 and 3 and opens 1.
```

Length target: under 200 lines with the generated blocks in. If it is longer, the PRD is being repeated.

## Where this lands in the pipeline files

- **`PIPELINE.md` §3 Spec** — one paragraph: after Part 2 holds and the prototype exists, Claude Code generates `design/BRIEF.md` and stops. **You** take the brief and the attached files into Claude Design, pick one of two directions, run the screens, and put the handoff and `tokens.json` into `design/`. Part 3 is then written with the handoff on disk, so §14 (the client) can name the token file and any bundled font as build tasks.
- **`.claude/skills/create-prd/SKILL.md`** — a new step between the prototype and Part 3: "the design brief", with the template above and the generated-vs-written split. The exporter gains a `--brief` mode that emits §1, §4, §5-fixed and §10 from the page. The step ends with the file, not with a design — the design tool is run by hand.
- **`CLAUDE.md`** — one line only, because the file is loaded every session: the token contract rule (§8). Accessibility stays out of doctrine per D6.
- **`PROGRESS.md`** — app_4 has passed the point where D2's recommended slot sits (its PRD closed 2026-09-20), so it would run the brief post-PRD like app_1; app_3 (PRD not started) is the first app that can run it in the recommended slot. Note each run so the third occurrence is when the brief step becomes a skill of its own, per the working agreement.

> **Second-occurrence notice, per the working agreement:** the v2 `HANDOFF.md` shape (visual system → per-screen → hold-off) has now been used twice in app_1 (`ui_design_v2/` on 09-10, `options_review/` on 09-11). This page proposes it as the required output format, which would be the third use. That is the moment to extract it — into the template above, not a separate skill.

---

# Reference

## Evidence index

### Every file cited on this page, and what it proves

| File | Proves |
| --- | --- |
| `app_1/ui_ux/DesignMyRoom iOS screens/github.md` | The Claude Design run happened, when, against which repo, and what it read. The only record of the "brief". |
| `app_1/ui_ux/DesignMyRoom iOS screens/DesignMyRoom.dc.html` | The output; header admits chosen aesthetic, offered alternative, placeholder imagery; lists open decisions U2/F2/U3/U4. |
| `app_1` git log, commit `97db015` | What existed on 2026-09-08 16:53: research, positioning, spec page, PRD.md (722 lines, 35 decisions, 9 rounds). |
| `app_1/PRD.md` §5, §7, §8, §9, §13, §16 | The product half of the brief — user, flow, eight screens, metric, client stack, error copy. |
| `app_1/spec/index.html``SCREENS` array | Low-fi wireframes existed inside the spec page and were not counted as "app UI" by the tool. |
| `app_1/ios/AGENT.md` lines 16–18, 117, "Architecture the app must keep cheap" | How the design reached the build worker; contract strings shown verbatim; restyle-cheap rule restated for the builder but never for the designer. |
| `app_1/ui_design_v2/HANDOFF.md`, `state.json`, `INBOX.md` | The second visual pass: tokens, type, spacing, per-screen changes, dark mode ruled out, brand direction settled by side-by-side and comments. |
| `app_1/ios/DesignMyRoomApp/Sources/Shared/DesignTokens.swift` + 14 `.colorset`s | The token handoff was consumed by the build exactly as written — the shape works. |
| `app_1/options_review/HANDOFF.md` | Second use of the handoff shape (2026-09-11). |
| `app_1/inputs/room.jpg`, `options_review/images/` | Real imagery existed and was not in the brief. |
| `app_4/positioning.md` | Stronger positioning shape ("Left out on purpose"). |
| `app_4/spec/index.html` §8, §14 | Eleven-screen table with requirement column; tab bar and hardest screen named in the build section. |
| `app_4/spec/prototype.html` | Tokens and dark mode exist by way of the html-worker template; iOS conventions per `create-prd`. |
| `CLAUDE.md` (series), `PIPELINE.md` §3, `.claude/skills/create-prd/SKILL.md` | The restyle-cheap constraint; the prototype step; no design-brief step anywhere. |

