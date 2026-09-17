---
name: research
description: Stage 1 of the app pipeline. The user gives a niche and a problem. This skill finds the solutions that already exist, checks what they target and how much money they make, finds what real users complain about, and then helps brainstorm new solutions nobody has built yet — before picking one to move forward with.
---

# Research

Simple version of the whole flow:

- **Problem** → **What already exists** → **The pattern (who, why, revenue)** →
  **What people complain about** → **New ideas nobody built yet** → **Pick one**

That's it. Everything below is just detail on how to do each part well.

## The one rule that never bends

**Never write a quote you did not read.** Every quote has to be real text a search or a
page gave you in this session. Copy it exactly. Add a link that works.

A quote in your own words is not a quote. A made-up complaint that sounds real is a lie —
if you can't check it's real, drop it. Ten real complaints beat fifty fake ones.

## Before you start

Make sure you know:

- The problem, in one line.
- Any hard limit — which phone, must it fit the series stack, anything else.

If either is missing, ask. If you already have both, just go.

---

## Step 1 — Write down the problem

One line. Plain words. This is the thing every solution below is trying to fix.

## Step 2 — Find the solutions that already exist

List **every** app or tool people use for this. Not just two or three — all of them you
can find.

Where to look:

- App Store and Google Play search for the topic.
- "Best [topic] apps" articles — good for finding names, not proof of anything.
- Forums and review sites, for names people actually use.

## Step 3 — Find the pattern across them

For each solution, write down:

- **How it actually works.** The steps a person goes through, in order — what they see,
  what they tap, what happens next. 3-6 steps is enough. Do this before anything else in
  this step. You cannot spot what's smart or what's broken about a solution, or think of a
  better one, if you don't know how it actually works. Get this from real reviews, the
  app's own screenshots or help pages, and what its users describe — not a guess.
- **Who it's for.** The exact kind of person it's built for.
- **Why that group.** What need it's chasing.
- **How much money it makes.** Only from a real source — a news article, a founder
  interview, Crunchbase, the company's own numbers. If there's no real source, write
  "no public number." Never guess a number.

Once you have this for every solution, look across all of them and ask:

- What do they all agree on?
- Who is nobody serving?
- Where do they all charge the same, or all avoid a certain type of user?

## Step 4 — Find what real users complain about

For each solution, go find real reviews — App Store, Google Play, Trustpilot. Pull the
complaints people actually wrote, word for word.

- If **3 or more different people** say the same thing, that's a real pattern.
- If only one person says it, that's just one bad day — don't count it.

For each solution, answer in one line: **is it actually helping people, or not really?**

Good places to find reviews fast:

- The Apple review feed:
  `https://itunes.apple.com/us/rss/customerreviews/id=<APP_ID>/page=<1-10>/sortBy=mostRecent/json`
  — up to 50 full reviews per page, up to 10 pages.
- Trustpilot, for anything with a company behind it.
- Reddit is blocked for us — if the user wants Reddit voices, they have to paste the
  links or text themselves.

Skip ads, "top 10" list pages, and anything that reads like a sales pitch, not a person.

## Step 5 — Brainstorm new solutions

Now that you know what exists and what's wrong with it, think of **1-3 new solutions**
nobody has built yet. Each one should fix a specific complaint from Step 4 — not a vague
new idea, a direct answer to something real people said.

For each new idea, check:

- **Can we actually build this?** Any phone or platform limit that would block it.
- **Could people find it?** How would someone even hear this exists.

If an idea fails both checks, cut it. A good idea that can't be built or found is not
useful yet.

## Step 6 — Decide

Lay out the choice plainly: the existing solutions, and the new ideas from Step 5. Say
which one looks strongest and why, in one line. Then stop — the user picks.

---

## Write the file

Save to `<app_repo>/research/<niche>.md`. Ask where if the app repo doesn't exist yet.
Use bullet points everywhere you can — short lines, not long paragraphs.

```markdown
# Research: <niche>

<date>

## The problem
- <one line>

## Solutions that already exist

### <Solution A name>
- What it does: <one line>
- How it works, step by step:
  1. <what the person sees/taps>
  2. <what happens next>
  3. <...>
- Who it's for, and why: <one line>
- Money: <number + source, or "no public number">
- What people complain about:
  - "<real quote>" — <link>
  - "<real quote>" — <link>
- Actually helping people? <yes / kind of / no — one line>

### <Solution B name>
(same shape)

## The pattern
- <what they all get right>
- <what they all get wrong>
- <who nobody is serving>

## New ideas nobody has built yet
- **Solution D** — <one line> — fixes: <which complaint from Step 4>
- **Solution E** — <one line> — fixes: <which complaint from Step 4>

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

## Decision
- Strongest option: <name it>
- Why: <one line>
```

## Not allowed in the file

- Hype words: "massive", "huge", "underserved", "exciting", "game changer".
- A made-up money number. See Step 3 — real source or "no public number".
- Long paragraphs where a bullet list would do.
- A summary section that just repeats what's already above.
- Any line that would still be true if you swapped in a different niche.
