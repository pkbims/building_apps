---
name: research
description: Stage 1 of the app pipeline. The user gives a niche and a problem. This skill works out why the problem exists, finds the solutions that already exist, how they work, what they earn and how they spread — using current-year evidence only — finds what real users complain about, proposes new ideas (each with its USP against the apps and free AI chatbots, and a viral feature), has the user decide who it is for and what to build, applies the build-it-or-not gate, and ends on a conclusion of what we are building — before any app repo exists.
---

# Research

Simple version of the whole flow:

- **Problem** → **Why the problem exists** → **Existing solutions** →
  **Patterns across them (how it works, features, who, money, how it went viral)** →
  **What people complain about** → **New ideas (each with its USP and viral feature)** →
  **Decide what we build (who → which idea → USP → viral → quotes)** → **Build it or not** →
  **Conclusion: what we are building**

That's it. Everything below is just detail on how to do each part well.

## The one rule that never bends

**Never write a quote you did not read.** Every quote has to be real text a search or a
page gave you in this session. Copy it exactly. Add a link that works.

A quote in your own words is not a quote. A made-up complaint that sounds real is a lie —
if you can't check it's real, drop it. Ten real complaints beat fifty fake ones.

WebFetch summaries paraphrase. Verify every quote against the raw pulled text — that is
what `scripts/verify_quotes.py` is for.

The same rule covers every other claim: why the problem exists, what an app earns, why an
app went viral. Each one has a source you read this session, or it is written as unknown.

## Current-year evidence only

Things move too fast for old evidence. **Every source must be dated in the current year** —
surveys, articles, revenue numbers, viral moments and reviews. Filter pulled reviews by
date before counting or quoting them; say how many of the 300 fall in the year.

- An older source is dropped, not kept "for context". If it was the only source for a
  claim, the claim becomes **"no <year> source found"** — say so plainly, don't soften it.
- A famous old number (a 2023 MRR, a 2023 viral TikTok) is the classic trap: it reads like
  proof and describes a market that no longer exists. Find this year's number or drop it.
- Pages read today without a date (store listings, pricing pages, help pages) count as
  current; write "read <date>" beside the link.
- A tool that only has older coverage is still listed so it isn't missed, marked "no
  <year> source", and not used as evidence.

## App Maker mode

When the session was started from the App Maker (its first prompt says "App Maker mode", or the
folder has a `.appmaker.json`), follow the `app-maker` skill's **Stage sessions** rules instead of
the page-server and terminal steps below: the page lives in the app folder and the app's one server
serves it — no page server of your own, no watcher; ask the user on the page with `post.py`; answer
questions in the page's conversation with `html-worker/reply.py <page_dir> <id> "…"` (they arrive by prompt, bundled); you are woken when the user presses Send.

## Before you start

Make sure you know:

- The problem, in one line.
- Any hard limit — which phone, must it fit the series stack, anything else.

If either is missing, ask. If you already have both, just go.

---

## Step 1 — Write down the problem

One line. Plain words. This is the thing every solution below is trying to fix.

## Step 2 — Why the problem exists

Before looking at any app: why do people have this problem at all? What in their habits,
their situation or their psychology keeps producing it? This is what the PRD's
requirements eventually rest on — complaints about other apps say what *they* get wrong,
not why the problem is there.

- 2-4 causes, one line each.
- **Every cause has a source**: a study, an article, or people saying it in their own words
  (a review, a forum post). A cause that only sounds true is cut.
- Write them as **hypotheses**. Step 5's complaints and Step 4's money either back each
  one up or don't; mark each cause *backed by* the complaint pattern or revenue that
  confirms it, or *not backed* — before the file is done.

## Step 3 — Existing solutions

List **every** app or tool people use for this. Not just two or three — all of them you
can find. Include free general-purpose AI (ChatGPT, Gemini, Claude) whenever reviewers
name it as what they'd use instead — it is the substitute every AI app now competes with.

Open the section with an overview table — kind of tool, the apps, this year's money — so
the reader sees the whole field before the per-app detail.

Where to look:

- App Store and Google Play search for the topic.
- "Best [topic] apps" articles — good for finding names, not proof of anything.
- Forums and review sites, for names people actually use.

## Step 4 — Patterns across the existing solutions

For each solution, write down:

- **How it actually works.** The steps a person goes through, in order — what they see,
  what they tap, what happens next. 3-6 steps is enough. Do this before anything else in
  this step. You cannot spot what's smart or what's broken about a solution, or think of a
  better one, if you don't know how it actually works. Get this from real reviews, the
  app's own screenshots or help pages, and what its users describe — not a guess.
- **Its features.** A short list of what it offers, from its store listing, screenshots
  and help pages. This is what the PRD later drafts v1 from, so name features the way a
  user would ("daily limit per app", not "usage enforcement engine").
- **Who it's for.** The exact kind of person it's built for.
- **Why that group.** What need it's chasing.
- **How much money it makes, per month.** Look in this order:
  1. **TrustMRR** (trustmrr.com) — revenue verified from the payment provider. Its search
     box isn't reachable by URL; guess slugs instead: `trustmrr.com/startup/<slug>.md`
     returns a markdown profile with last-30-day and 12-month verified revenue (fetch it
     from a trustmrr.com browser tab). A listing is a real source: write the number and
     link it.
  2. **Sensor Tower** — for mobile apps, `app.sensortower.com/overview/<App Store id>?country=US`
     carries this month's estimate in its meta description ("Last month's estimates were
     …k downloads and $…k revenue"), no login needed; read it from a browser tab. Find the
     id with the iTunes search API. Write it as an estimate with the month it covers.
  3. **Google search** — `"<app name>" MRR`, `"<app name>" revenue`, `"<founder>" MRR` —
     for a founder post or interview, a news article, Crunchbase or the company's own
     numbers. Write the number and link the page you read.
  4. An estimate, when a page you read gives one (an analyst or market-data figure quoted
     in an article). Write it as **"~$X/mo — estimate, <who estimated it>, <date>"**.
     Always labelled; never passed off as fact.
  5. None of these: **"no public number."**
  Never guess a number.
- **How it grew — did it go viral, and why.** Found by **Google search** —
  `"<app name>" viral`, `"<app name>" TikTok`, `"<app name>" went viral`,
  `"<founder>" how we grew` — and only from a page you read: a press piece, a founder
  saying what worked, a specific viral post or video (link it), or a chart-rank jump tied to
  a date. TikTok and X are not reachable directly, so a viral post counts when an article or
  a search result shows it. Name the thing that spread — a share card, a challenge, a result people posted.
  If there is no source, write **"no evidence of a viral moment"** — do not infer one from
  download numbers.

Once you have this for every solution, look across all of them and ask:

- What do they all agree on?
- **Which features does every app have?** Mark these as **table stakes** — a user will
  expect them from us too. Features only one or two apps have are differentiators.
- Who is nobody serving?
- Where do they all charge the same, or all avoid a certain type of user?
- What spread, for the ones that went viral — is there a pattern?

## Step 5 — Find what real users complain about

For each solution, go find real reviews — App Store, Google Play, Trustpilot. Pull the
complaints people actually wrote, word for word.

- If **3 or more different people** say the same thing, that's a real pattern.
- If only one person says it, that's just one bad day — don't count it.

For each solution, answer in one line: **is it actually helping people, or not really?**

How to pull reviews — use the scripts in `scripts/` (read `scripts/README.md` first):

- `play_reviews.py` first. Google Play is the reliable source: 300 recent reviews per
  app, each with its own link.
- `appstore_reviews.py` second. Works for some apps, not others; no per-review links, so
  link the app's reviews page.
- `verify_quotes.py` on the finished file before you call it done.
- Trustpilot, for anything with a company behind it.
- Reddit is blocked for us — if the user wants Reddit voices, they have to paste the
  links or text themselves.

Skip ads, "top 10" list pages, and anything that reads like a sales pitch, not a person.

## Step 6 — New ideas

Now that you know what exists and what's wrong with it, think of **1-3 new solutions**
nobody has built yet. Each one should fix a specific complaint from Step 5 — not a vague
new idea, a direct answer to something real people said.

Every idea card carries, in this order:

- **What it is** — in a few plain sentences, as the user would do it.
- **Its USP against the other apps** — a two-column table, "other apps / this idea". Every
  row answers a real complaint from Step 5; a USP no complaint asks for is cut.
- **Why not just use ChatGPT?** — what a person gets that pasting the same photo or
  question into a free chatbot doesn't give them. Check what chatbots can really do this
  year first (with sources); never claim "a chatbot can't" without one. Unchecked claims
  are written as "not tested yet".
- **How it could spread (viral feature)** — one feature built so that using the app makes
  something worth posting. Say plainly when it's a guess with no example to copy.
- **Complaints it answers**, **can we build it?**, **could people find it?**

If an idea fails both "build" and "find", cut it. End by saying which idea looks strongest.

**Don't set our pricing here.** Research records how the others charge and what users
say about it (Part 3); what *we* charge is decided later. Keep pricing out of the idea
cards, the USP options and the Conclusion.

## Step 7 — Decide what we build

Stop and let the user decide, **in this order** — people first, then the idea that fits them:

1. **Who is it for first** — 2-4 candidate groups, each with this year's evidence and
   whether anyone serves them today.
2. **Which idea** — the ideas from Step 6, alone or combined.
3. **What we lead with** — the USP points, as checkboxes.
4. **How it spreads** — the viral feature options.
5. **Which 2-3 complaints** become positioning's Anchored-to block.

Recommend an answer for each; the user picks.

## Step 8 — Build it or not

Research runs before any app exists, so this is where a niche dies cheaply. The series
rule: **build only if at least one app earns $10k+ a month solving this problem** — a real
number or a labelled estimate both count. Say plainly whether the rule is met and by which
app, then give your honest read in one line, including "not worth building" when the
evidence says so. The user decides.
**No** → move the folder to `archived_research/<niche>/` with a `README.md` saying why.
**Yes** → the app gets set up (stage 2) and the folder moves in — but only after the
user has closed the review page. **Never stop the review server yourself**; the user closes
servers from the monitoring center. Until they have, leave the folder where it is and say
so.

## Step 9 — Conclusion

The output of the research: **what we are building** — the idea, who it's for, its USP,
how it spreads, the complaints it answers, build yes/no — filled in from the user's
answers, plus the one biggest risk to test first. This is what stage 2 starts from.

---

## Write the file

Save to `building_apps/research/<niche>/<niche>.md`, with pulled reviews and the review
page beside it. **The review page is the one source**: build it first, then export this file
from it with the html-worker `export-md.py` (`OUT=../<niche>.md`), and re-export after every
round. Never hand-write the markdown alongside the page — two copies drift. The template
below shows what the export must end up covering. There is no app repo yet — it is only created after a **yes** in Step 8,
and this folder moves into it as `app_N/research/`. If research is re-run for an app that
already exists, write into `app_N/research/` instead.
Use bullet points everywhere you can — short lines, not long paragraphs. **Plain, simple
English** in the file and the page alike: short sentences, everyday words.

```markdown
# Research: <niche>

<date> · evidence window: <year> only

## The problem
- <one line>

## Why the problem exists
- <cause> — <source link> — backed by: <complaint pattern / revenue, or "not backed">
- <cause> — <source link> — backed by: <...>

## Existing solutions — what people use today

| Kind | Apps | Money, <year> |
|------|------|---------------|
| <kind> | <apps> | <$ + source / estimate / no <year> number> |

### <Solution A name>
- What it does: <one line>
- How it works, step by step:
  1. <what the person sees/taps>
  2. <what happens next>
  3. <...>
- Features: <feature>, <feature>, <feature>
- Who it's for, and why: <one line>
- Money: <$X/mo + source> | <~$X/mo — estimate, <tool>, <date>> | no public number
- How it grew: <what spread + source link> | no evidence of a viral moment
- What people complain about:
  - "<real quote>" — <link>
  - "<real quote>" — <link>
- Actually helping people? <yes / kind of / no — one line>

### <Solution B name>
(same shape)

## Patterns across the existing solutions
- <what they all get right>
- <what they all get wrong>
- <who nobody is serving>
- Table stakes (every app has these): <feature>, <feature>
- What went viral, across them: <one line, or "nothing did">

## New ideas nobody has built yet
- **Solution D** — <one line> — fixes: <which complaint from Step 5>
- **Solution E** — <one line> — fixes: <which complaint from Step 5>

## The simple picture

\`\`\`mermaid
flowchart TD
  P[The problem] --> A[Solution A]
  P --> B[Solution B]
  A --> AC[Biggest complaint about A]
  B --> BC[Biggest complaint about B]
  AC --> D[New idea: Solution D]
  BC --> D
  D --> DEC{Pick one}
  A --> DEC
  B --> DEC
\`\`\`

## Decide what we build
- Who it's for: <picked group> · Idea: <picked> · Lead with: <USP points> · Spreads by: <viral feature>
- Anchored to: "<quote>" — <link>; "<quote>" — <link>

## Build it or not
- $10k/month rule: <met by <app>, <number + source> | not met>
- Worth building? <yes / no — one line on why>

## Conclusion — what we are building
| What we build | <idea> |
| Who it's for | <group> |
| USP — why us | <points> |
| How it spreads | <viral feature> |
| Complaints we answer | <quotes> |
| Build it? | <yes / no> |
- Biggest risk to test first: <one line>
```

## Then show it as a review page

Don't present the result as terminal prose. Build the review page with the html-worker
skill and hand over the URL. The terminal reply is the URL plus the list of decisions on
the page, nothing more.

**The page reads as one argument, in seven parts:**

| Part | Answers | Decisions |
|---|---|---|
| 1 · The problem | what hurts, and why it keeps happening | — |
| 2 · What exists today | overview table, then one section per solution, chatbots last | — |
| 3 · What they all miss | the gaps, and what every app already has | — |
| 4 · New ideas | one card per idea: what it is, USP vs apps, why not ChatGPT, viral feature | — |
| 5 · Decide what we build | **D1 who** → **D2 which idea** → **D3 USP** → **D4 viral feature** → **D5 quotes** | D1–D5 |
| 6 · Build it or not | the $10k rule's result beside **D6 build?**, then **D7 Reddit** | D6–D7 |
| 7 · Conclusion | what we are building — filled in live from D1–D6 | — |

- **Plain, simple English** everywhere: short sentences, everyday words ("what every app
  already has", not "table stakes"). The reader should get each section in one read.
- Every part is a **visible heading on the page** (a `.part` divider: "Part N", title, the
  question it answers), and the left rail groups use the same words. A rail heading that
  doesn't appear on the page is a bug.
- Decisions are **numbered in reading order**.
- **"Your progress"** is its own card on the right, in its own column, **beside** the
  decisions and feedback queue (four columns: contents | page | progress | decisions +
  queue — never stacked): the seven parts, which is being read, which are read, and
  each part's decisions answered.
- The Conclusion updates live as decisions are clicked; rebuild the page before exporting
  so the markdown carries the current answers.

`research/interior-decor/reviewer/build.py` is the first page built this way — reuse its
`part_div`, the path CSS and the path script rather than rewriting them.

**Every option set on the page has one *recommended* option with a one-line reason** (html-worker
rule), never pre-selected.

## Not allowed in the file

- Hype words: "massive", "huge", "underserved", "exciting", "game changer".
- A made-up money number, or an estimate without "estimate" and its tool beside it.
- A cause, or a viral story, without a source.
- Any source, number or review dated before the current year (see "Current-year evidence only").
- Long paragraphs where a bullet list would do.
- Jargon where a plain word works ("what every app already has", not "table stakes").
- "A chatbot can't do X" without a current-year source — unchecked means "not tested yet".
- Our own pricing (decided after research).
- A summary section that just repeats what's already above.
- Any line that would still be true if you swapped in a different niche.
