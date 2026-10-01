# 30-Day Challenge: AI Maxxing

A snapshot of the planning work for **AI Maxxing**: a public series of 30 builds in 30 days, each a useful, surprising thing built with Claude. Copied from `~/Documents/30dayChallenge` on 2026-10-01 so other Claude sessions (e.g. the Claude app) can pick up the work.

**Start with [`CONTEXT.md`](CONTEXT.md).** It has every decision made so far, with the reasons.

## Where things stand (2026-10-01)

| Area | Status |
|---|---|
| Goal and strategy | Final. See `goal/` |
| Content pipeline (idea → build → post) | Final. See `pipeline/` |
| Ideation method | **Product-first**: find tools already built for an audience, judge them with rubric v3, add a twist. See `ideation/plan/` |
| Run 3 (problem-first, small business owners) | 10 idea cards, Keep/Kill **not yet decided** |
| Run 4 (product-first: couples' money, stock investors, crypto) | 48 tools analysed → 10 idea cards, plus 4 of his own ideas judged. 2 kept so far |
| **Selected Ideas** (the build list) | **Which Card For This Bill?** and **Points Goal Planner** |
| Posting start | Suggested Mon 2026-10-05, after a 2-day build sprint |

## The rubric (v3)

**Gates (yes/no, one "no" and it's out):**
- **One day:** the core works in 2–3 hours.
- **Takeable:** a stranger can use it on their own device in under a minute.
- **Beyond ChatGPT:** it does something a chat window can't. It lives where the problem is, runs by itself, connects to real things and acts, handles video, sites or files, or remembers over time.

**Scores (1–3 each, with a reason, out of 12):** Relatable · Value (must be medium or high) · Shareable · Visual.

## Folder map

```
30dayChallenge/
├── CONTEXT.md            every decision so far: strategy, rubric, sources, runs (start here)
├── goal/                 the goal: AI Maxxing, why, benefits, $10k/month in 90 days (final)
├── pipeline/             idea bank → pick → plan → build → ship → record → post → learn (final)
├── ideas/                early "idea engine" page (superseded by ideation/, kept for history)
└── ideation/             the ideation workspace (App-Maker-like, but fully separate)
    ├── index.html        shell: left navbar (from nav.json), chosen page on the right
    ├── nav.json          the navbar: Ideation · Runs · Bank
    ├── server.py         Ideation's own server (serves all pages, wakes Claude on Send)
    ├── plan/             how ideation works (product-first), the rubric
    ├── sources/          every source tested, what works, how each is used
    ├── runs/run-03/      problem-first run: 106 signals (signals-*.md) → 10 cards
    ├── runs/run-04/      product-first run: tools-A/B/C.md (~130 entries) → 48 tools → 10 cards, plus "Your ideas"
    └── selected/         Selected Ideas: the kept ideas, ready to build
```

## How to read the pages

Each folder with an `index.html` is an **html-worker review page** (the skill is at `.claude/skills/html-worker/` in this repo):

- **`index.html`**: the page. Content sits inside `<main>`, and the rest is the html-worker template.
- **`state.json`**: what he decided and said on that page. `decisions` holds his picks (e.g. `k1: "keep"` on an idea card), `comments` holds his comments with Claude's replies, and `batches` holds each round he sent.
- **`INBOX.md`**: the last round he sent, in readable form.
- **`*.md` research files**: the raw signals and tool lists behind each run, with links and numbers.

**Reading is enough** to understand everything, so no server is needed. To click through the pages locally:

```bash
cd 30dayChallenge/ideation && PORT=7802 python3 server.py   # then open http://localhost:7802/
```

(`goal/` and `pipeline/` are single pages; copy `.claude/skills/html-worker/server.py` beside one and run it.)

## Working agreements learned along the way

- Every idea card has a **"How it works"** line (the user's main workflow in 1–2 lines), and is honest about limits.
- Each run starts with a **brief** that holds all its inputs, and runs only after he confirms it.
- He prefers **short, plain lines** over long paragraphs, and diagrams over walls of text.
- Ideation stays **completely separate from the App Maker**.
