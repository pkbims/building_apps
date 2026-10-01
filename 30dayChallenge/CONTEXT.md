# Context: every decision so far

Written by Claude Code while working with Bimal (2026-09-30 → 2026-10-01). "He" is Bimal. Paths like `ideation/...` are relative to this folder. This is the source of truth for why things are the way they are. Treat decided items as locked unless he reopens them.

## Plan from here
1. Keep/Kill the remaining cards in Run 3 and Run 4. Kept ideas go to `ideation/selected/`.
2. One-time setup from `pipeline/`: domain, Instagram keyword auto-DM, email sign-up, guide and video templates, default stack.
3. A 2-day build sprint (5 builds), then start posting (suggested Mon 2026-10-05) and keep a 3–5 build buffer.
4. Turn the ideation process into an `idea-bank` skill and run it weekly.
5. Day 31: start selling (around Nov 4).

## Decisions and notes
Decided by 2026-09-30. Public series **AI Maxxing** (renamed from "Claude-Maxxing" on 2026-09-30): 30 days, 30 builds, one useful and surprising thing built with Claude each day (web apps, tools, skills, workflows, automations, agents, extensions, experiments — not full startups). Viewers comment a keyword to get the live tool plus a build guide. Real MRR apps (building_apps/) stay private until launch.

- Builds stay free. Selling starts on Day 31 (decided 2026-09-30, replacing the earlier $0-for-90-days rule): something paid is always on offer after Day 30.
- Progression: show → teach → sell. Later money comes from his own apps, sponsorships, affiliates, templates and products. His target is $10k/month **within 90 days** (set 2026-09-30).
- Idea rubric v3 (2026-09-30): gates One day, Takeable ("on their own device, working in under a minute") and Beyond ChatGPT (must do something a chat window can't: live where the problem is, run by itself, connect to real things and act, handle video/sites/files, or remember over time). He rejected ideas that are "a prompt with a nice screen". Scores 1–3, each with a reason: Relatable, Value (what exactly it gives; must be medium or high), Shareable, Visual. He removed Surprising, "AI is the magic" and Safe.
- Operations: build about 5 builds in the first 2 days, keep a 3–5 day buffer, start posting on a Thursday, and never build and post on the same day.
- Rejected: building startups in public (can't ship many, exposes ideas, public abandonment looks shallow) and generic "Claude tips" content (nothing concrete to show).

- Pipeline (html-worker page at 30dayChallenge/pipeline/, 2026-09-30): Idea bank (weekly; the rubric gates entry) → Pick → Plan (hook + curiosity loop + per-build AI cost) → Build (no recording during the build) → Ship (live link + guide) → Record (after the build; a create-content skill comes later) → Post on IG, TikTok and YT Shorts, with IG leading for keyword DMs → Learn at 48h. Decided: face for the hook and CTA with screen for the rest (flexible per video), tool free and guide behind an email, one default stack, weekly idea bank.


**Why:** he enjoys building, so the content should require building rather than commentary.
**How to apply:** treat the strategy as locked; don't re-litigate it. Work lives in ~/Documents/30dayChallenge (goal page at goal/index.html, an html-worker page).

- Idea sources, tested 2026-10-01. The canonical list is 30dayChallenge/sources/ (an html-worker page).
  - Working: TrustMRR (verified revenue, free), IdeaIndex (free case studies), There's An AI For That and Toolify (traffic and growth, both through Chrome), Future Tools (last 48h), YC directory (Chrome), Launch HN and Show HN (Algolia API), Hugging Face trending, Reddit and Threads (Google in Chrome), TikTok (Chrome), IdeaBrowser (his free login: all 1,923 ideas, reports with search demand, and the Trends Library; only playbooks are locked).
  - Partly: FoundersDB ($19 lifetime), Starter Story, Acquire.com, Exploding Topics, Google Trends (for checking one idea only).
  - Useless: BigIdeasDB on his free login (everything locked; Pro $349), Indie Hackers revenue (fake numbers), Chrome Web Store (can't be automated), App Store charts (only giants), a16z top 100 (stale).
- Ideation workspace (2026-10-01): an App-Maker-LIKE shell at 30dayChallenge/ideation/. It must stay COMPLETELY SEPARATE from the App Maker (his words, 2026-10-01), so it runs on its own ideation/server.py (PORT=7802). The only shared code is the html-worker skill's page mechanics.
  - Left navbar from nav.json: Ideation (Plan, Sources), Runs (Run 3 …), Bank (Selected Ideas). The chosen page opens on the right, each with its own Chat center.
  - New run = a new runs/run-NN/ page plus a nav.json entry.
  - Each run starts with a brief holding ALL its inputs (audiences with niche sub-groups, never pre-picked; themes; build types; count; remix; research style) and runs only after he confirms in it.
  - Runs skip anything already in Selected Ideas, and kept ideas move there.
  - His inputs: build range web, extension, skill, automation, browser agent; startup-remix format NO; parallel research helpers YES; $0 tool budget; 10 ideas per run.
  - He removed the taste, audience-knowledge and off-limits asks.
- Run 3 results (2026-10-01), at ideation/runs/run-03/. 106 signals, 22 ideas, 10 passed.
  - The 10: ClassPass Converter, Gallery Countdown, Last-Minute Slot Filler (11 each); Gym Secret Shopper, Showing Gatekeeper, Deal Timeline, Past Client Radar, Empty Class Filler, Search My Shoot (10 each); Revision Gate (9).
  - Killed for crowding: AI receptionists, listing generators, AI-visibility checkers, scribes.
  - Keep/Kill radios are k1–k10. On Send, kept ideas get copied into selected/ and the nav badge is updated.
- PRODUCT-FIRST ideation, adopted 2026-10-01 (Plan P1). He found problem-first slow and unscalable.
  - Each run finds tools already built for the audience, then judges them with rubric v3. 40 tools are analysed per run (P2), 10 become cards, and each card gets his twist (1–2 changes).
  - There is no separate "do people want it?" check; the tool's own proof covers that.
  - Helper A reads sites directly: TrustMRR, Product Hunt, Show HN.
  - Helper B uses Chrome: There's An AI For That, Toolify, YC, IdeaBrowser.
  - Helper C uses Chrome: Reddit "I built" posts via Google, TikTok, Instagram, Threads, X.
  - B and C run one after the other (one Chrome).
  - Run 4 page: ideation/runs/run-04 (product-first brief).
- Run 4 (first product-first run, 2026-10-01), at ideation/runs/run-04.
  - Audience: couples managing money together, stock investors, crypto holders and traders.
  - 3 helpers produced ~130 tool entries, merged into a 48-row tools table.
  - The 10 ideas: Trade Journal Coach (12), Fee X-Ray (12, only just passes Beyond ChatGPT), Couples Money Pot (11), Chart Second Opinion (11), Market-Mover Alerts (11), Whale Watch (10), Crypto Dead Man's Switch (10), Filing Radar (9), Earnings Recap (9), Dividend Paycheck (9).
  - Lessons: Reddit snippets often hide product names, and TrustMRR's `/startup/<slug>.md` gives clean verified revenue.
- Every run page gets a "Your ideas for this audience" box (added on Run 4, 2026-10-01).
  - The textarea posts a note (anchor `yourideas`, kind `note`, now:true), which wakes me.
  - For each idea: find existing tools like it as proof, suggest his twist, judge with rubric v3, and add a card with a Keep/Kill radio in that section.
- Every idea card must include a "How it works" line: the user's main workflow in 1–2 lines. He asked for this on Run 4 (2026-10-01). Be honest about limits, e.g. congressional trades can't be copied in real time because disclosure takes up to 45 days.
