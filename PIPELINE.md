# Pipeline

The stages each app goes through, in order. Deliberately not fleshed out yet — the detail
gets written from what actually happens during app_1, not predicted in advance.

## 1. Research

Find a real pain point (Reddit, forums, reviews, search) and scan competitors.

## 2. Spec

Turn the problem into a tight PRD and a UI direction. The PRD must name what is *not*
being built. Reviewed as a clickable HTML artifact with comment threads, not as prose.

## 3. Contract freeze

Lock the API schema and shared types before any build work starts. This is what makes
stage 4 possible.

## 4. Build

Frontend and backend in parallel, each in its own git worktree, both coding against the
frozen contract from stage 3.

## 5. Ship

The full baseline from CLAUDE.md, then the showcase site.

## Open questions

- Waitlist as early validation (before stage 4) vs. showcase after ship — likely both,
  as two separate things.
- Which stages earn a skill, and which are one-offs. Decide after app_1.
