# Design brief — {{app_name}}

Written {{date}} by the `create-ui-design-direction` step, from the PRD page and its
recorded decisions. Sections marked *generated* were pulled from the PRD; sections marked
*written* were decided on the brief-review page; the rest are series rules.

## 0. How this brief is used

Generated after Part 2 of the PRD held. Pasted into Claude Design by hand, with these
files attached — no repo connection: `PRD.md` · `spec/prototype.html` ·
`design/references/*`. Read them in that order. Everything you need is attached; if
something is missing, ask rather than infer it.

## 1. What this is, and for whom  *(generated)*

{{positioning_paragraph}}

{{prd_s5_who_verbatim}}

Two things people said, in their words:

> {{quote_1}}

> {{quote_2}}

## 2. Platform and device  *(written)*

{{platform_line}}
<!-- e.g. iOS · iPhone only · smallest supported: iPhone SE (3rd gen) width · iOS 17+ · SwiftUI.
     Web apps: browsers, breakpoints, and whether the design tool's HTML is the deliverable —
     decide in the first web app. -->

## 3. Navigation model  *(written)*

{{navigation_sentence}} Where "done" lands: {{done_lands_on}}.

## 4. Screen inventory, with every state  *(generated + written)*

Every state cell is filled: "—" means that state cannot happen on this screen; otherwise
the copy, or a pointer to §5. No cell is blank.

| # | Screen | What's on it | Serves | Empty | Loading | Error | Success |
|---|---|---|---|---|---|---|---|
{{screen_rows}}

Screens the flow needs that the PRD did not list, added here: {{added_screens}}.

**The hardest screen is {{hardest_screen}}:** {{hardest_screen_why}}

## 5. Copy  *(written + generated)*

Voice: {{voice_three_words}}. Sentences short; second person; no exclamation marks; say
what we do, not what we are.

Fixed strings — show verbatim, do not rewrite:

{{fixed_strings}}
<!-- PRD §16 "What the user sees" column, or:
     "Contract strings arrive in Part 3. Propose error copy for every error state in §4;
      we adopt or replace it, but it is not fixed yet." -->

Open copy: everything else. Propose; we approve per screen.

## 6. Data: real vs placeholder  *(written)*

Real, use these — attached in `references/`:

{{real_files}}
<!-- one line each: filename — what it is, where it came from (a real phone, the spike) -->

Numbers on screen use the product's real range: {{real_number_ranges}}.

Placeholder is **not** acceptable for {{no_placeholder_for}} — it is what the promise is
about. Placeholder is fine for {{placeholder_ok_for}}.

## 7. Visual direction  *(written)*

Three words: **{{vibe_three_words}}**.

Like: {{like_apps}} — one screen each in `references/`.
Not like: {{not_like_app}} — {{not_like_reason}}.

**First deliverable: two directions, side by side, on {{ab_screen_1}} and
{{ab_screen_2}}.** We pick one before any other screen is built.

{{surprise_us_block}}
<!-- Only if the "open for invention" decision has items checked:
     "Surprise us on: motion between screens · the one moment that deserves animation
      ({{moment}}) · illustration or a character · sound and haptics · the app icon ·
      how deep onboarding goes." List only what was checked. Omit the block entirely
      if nothing was. -->

## 8. Tokens — the contract with the build  *(series rule)*

Every colour, type role, spacing step, radius and shadow is a named token. No literal
values in screens. Deliver tokens as `tokens.json`. Light appearance only for v1; dark
mode is a documented v2 item, so keep every colour a token now so the second column can
be added later without touching a screen.

The build converts this file by script (practice_1 precedent: `ui_design_v2/HANDOFF.md` §1 →
`DesignTokens.swift`). Changing the look later must be a change to this file, never to a
view, and never to business logic.

Type: at most three roles (display / UI / meta). A bundled font is a real build task —
name the exact weights you use.

## 9. Accessibility  *(series rule)*

Not part of this brief; handled in the build stage. Do not design to a floor we have not
set.

## 10. What is fixed, what is open  *(generated + series rule)*

Fixed: the flow (PRD §7), the screen list (§4 above), the decisions already made in the
PRD ({{fixed_decision_ids}}), the contract strings (§5).

Open: everything visual, all unfixed copy, layout within a screen, and the items in §7's
"surprise us" list.

Still undecided in the PRD — build each as a switch and compare, do not pick:
{{open_decision_ids}}

Adding a screen, a step, or a permission ask is a change request to us, not a design
choice — flag it, do not build it silently.

## 11. What we need back  *(series rule)*

1. The clickable canvas, in the device frame, every screen in every state from §4.
2. `HANDOFF.md` in this shape (practice_1 precedent, `ui_design_v2/HANDOFF.md`):
   - §1 visual system as tables — colour, type, spacing, radii, elevation, imagery rules
   - §2 per-screen changes, numbered as §4 above
   - §3 the states grid from §4, filled with what you built
   - §4 hold off on / sequence carefully
   - §5 rejected alternatives, one line each, so they are not re-proposed
3. `tokens.json`.
4. `references/` back with any new imagery, named.

All of it goes into `<app>/design/`. The build stage's worker brief points at 2 and 3 and
opens 1.
