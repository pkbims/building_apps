# Progress

| App | Problem | Stage | Status | Video |
|-----|---------|-------|--------|-------|
| practice_1 | Restyle a room photo without inventing architecture | 6. Features | v1 complete 2026-09-09 (40 commits, both halves). Six features since: redesign v2, styles 6→18, room history, the options round, shop your restyle, styles 18→62. Two reopened the contract via ORCH-QUESTIONS. | — |
| practice_2 | Cut social media use, regain focus (iPhone) | 1. Research | Research written, reviewed via html-worker. Stage 2 not started. | — |
| practice_3 | Have food, can't decide what to cook — three dinners (one per cuisine) from what's in the fridge, under today's calories; cooking it is the log (iPhone) | 3. Spec | Research + positioning closed 2026-09-19 on one html-worker page, 3 rounds. `positioning.md` written with Anchored-to and v1 scope (fridge/receipt photo in; more cuisines, expiry wait). PRD not started. | — |
| practice_4 | Earn your scrolling — real-life actions buy TikTok/Instagram minutes (iPhone) | 5. Build v1 | Contract frozen 2026-09-20 (11 routes, 29 schemas, CI check). Worker briefs + HANDOFF written. Design brief written 2026-09-20 (`design/BRIEF.md`, first run of `create-ui-design-direction`); awaiting Claude Design handoff into `design/`. Next: iOS §18 step 1 (mechanism on device, entitlement request), backend skeleton — in parallel. | — |
| app_1 | Fill or restyle my room — basically Home AI, but your room stays your room and everything in it is real (iOS) | 4. Contract freeze | PRD done 2026-09-26 (23 review rounds, D1–D52 answered; `PRD.md`). Bets: chatbot, depth room tour, plan → find → draw; round 19–21 tests: draw prompt keeps products but can shift the camera (accepted, R1 reworded to "recognisable"), empty room + repaint works with descriptive searches. Design back (Sticker book, `design/HANDOFF.md`). v1: no purchases, everything free (accepted cost risk). Handed to **code-orchestrator** (Opus high; workers Sonnet high) — brief `app_1/HANDOFF.md`. Next: contract freeze, then build down PRD §18. | — |

practice_1–4 were built before the series started (renamed from app_1–4 on 2026-09-24). They stay as reference and precedent; app_1 is the first series app.

Stages: 1 Research · 2 Positioning · 3 Spec · 3½ Design direction · 4 Contract freeze · 5 Build v1 · 6 Features (repeats) · 7 Ship — see `PIPELINE.md`

## Content pipeline

2026-09-22 — pipeline settled on one html-worker page (`content-pipeline/`, 5 rounds): a 1–2 min Screen Studio recap every hour, joined into the long video by Remotion. Practice days Tue 22 – Thu 24 Sep; series Day 1 is Fri 25 Sep.
Two skills built the same day: `daily-content-system` (recap tabs; + reads every agent's log since the last recap and writes the script, verified end to end) and `daily-tasks` (spoken plan → task cards). Recap format settled via a mockup (`daily-content-mock/`, 3 rounds). Not built yet: the Remotion composition that joins recaps, adds captions and title cards (`video/day.ts` computes the cuts only).
2026-09-23 — content system v2 (reviewed on `content-system-v2-review/`): scripts are the exact words in the user's voice; every draft goes through a review window (comment → automatic revision → approve); recaps take an optional focus prompt ("only DesignMyRoom"); + → Past work digs through old logs, git and app files (read-only) and proposes an outline whose approval creates the chunks. Verified end to end on day-02: focused recap, a revision round, a real 5-chunk DesignMyRoom outline, and a chunk draft.

## Pipeline changes

2026-09-24 — reviewed on `pipeline-guide/` plus a terminal brainstorm. Research now runs before any app repo exists (`research/<niche>/`) and ends on a build-it gate: at least one app at $10k+/month, labelled estimates accepted; no → `archived_research/`. Research adds why-the-problem-exists, competitor features (table stakes) and how each went viral, all sourced. Positioning adds USP, viral feature (the "describe the post" test) and, for new ideas, a what-it-does list. create-prd opens Part 2 with a v1 feature list (in v1 only if the promise breaks without it; viral feature always in), the prototype must show the shareable moment, spikes are grouped by feature. v1 now ends on TestFlight with a hosted backend; hosting and signing are decided by the first app to get there. Then settled: MRR comes from TrustMRR and Google search; viral evidence from Google search; stage 7 Ship = App Store review and release, then the showcase site.
