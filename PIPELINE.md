# Pipeline

The stages each app goes through, in order. Deliberately not fleshed out yet — the detail
gets written from what actually happens during app_1, not predicted in advance.

## 1. Research

Find a real pain point (Reddit, forums, reviews, search) and scan competitors.

## 2. Positioning

Decide what we are building and why anyone would pick it, before any PRD exists.

A conversation loop, not a generated document. Claude proposes 2-3 candidate
positionings from the research, one paragraph each. The user reacts. Converge on one.

Every candidate must be writable as **"it's basically X, but Y"** — X a real shipping
product, Y one or two twists. A concept that cannot fit that sentence is too novel and
gets cut. The goal is something adjacent and sellable, not original.

Output is **one paragraph**, saved to the app repo. It names the user, the closest
existing product, and the wedge. It stays short on purpose: it is a constraint the PRD
must obey, and a long positioning statement constrains nothing.

## 3. Spec

Turn the problem into a tight PRD and a UI direction. The PRD must name what is *not*
being built. Reviewed as a clickable HTML artifact with comment threads, not as prose.

## 4. Contract freeze

Lock the API schema and shared types before any build work starts. This is what makes
stage 5 possible.

## 5. Build

Frontend and backend in parallel, each in its own git worktree, both coding against the
frozen contract from stage 4.

## 6. Ship

The full baseline from CLAUDE.md, then the showcase site.

## Open questions

- Waitlist as early validation (before stage 5) vs. showcase after ship — likely both,
  as two separate things.
- Which stages earn a skill, and which are one-offs. Decide after app_1.
