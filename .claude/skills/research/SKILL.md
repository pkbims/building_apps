---
name: research
description: Find real, evidenced problems in a niche by mining verbatim complaints from Reddit and Google, then map the 2-3 real competitors and what people dislike about them. Returns 2-3 candidate problems to choose from. Use at stage 1 of the app pipeline, when the user names a niche to research.
---

# Research

Find problems worth building for. The output is evidence, not opinion.

Input is one niche. If the user has not named one, ask for it and stop. Do not pick a
niche yourself.

## The rule that matters most

**Never write a quote you did not read.** Every quoted complaint must be text actually
returned by a search or fetch in this session, copied verbatim, with a working link.

A paraphrase is not a quote. A plausible-sounding complaint you composed is a fabrication,
and it poisons the entire pipeline downstream — the app gets built for a problem nobody
reported. If you cannot verify it, drop it. Fewer real complaints always beats more
invented ones.

## Phase 1 — Mine complaints

Target: **50 verbatim complaints.**

Reddit is unreachable — blocked at the crawler level by direct fetch, its JSON endpoint,
the search domain filter, and third-party mirrors. Do not spend turns retrying it. If the
user wants Reddit voices, they must supply thread URLs or text themselves.

Sources that work, in order of yield:

1. **App Store / Google Play reviews** of competing apps — highest yield, many verbatim
   complaints per page, and they double as Phase 3 evidence about the competitors.
2. **Trustpilot and BBB complaints** for service businesses — long, dated, attributed.
3. **Niche forums** (Houzz for home, and the equivalent for other niches) — the genuine
   community, but replies lazy-load, so expect only 1-2 usable quotes per thread fetch.

Quora is 403. General web search returns SEO filler and affiliate content, not people —
treat a search result as a way to find forum threads, not as evidence itself.

Search for the language people use when they are annoyed, not for the category name:

- `site:reddit.com "<niche>" "I hate"`
- `site:reddit.com "<niche>" "why is there no"`
- `site:reddit.com "<niche>" "anyone else"`
- `site:reddit.com "<niche>" "workaround"`
- `site:reddit.com "<niche>" "gave up on"`
- `site:reddit.com "<niche>" "wish there was"`
- `"<niche>" "waste of time"` / `"so frustrating"` / `"still doing this manually"`

Vary the niche wording — insiders rarely use the outsider term for their own field.

Record each complaint as: verbatim text, source (subreddit or site), URL, and date if
visible. Keep the person's own words including their typos. Do not clean them up.

Skip: marketing copy, SEO listicles, AI-generated blog filler, and anything that reads
like a pitch rather than a person complaining.

**If 50 real complaints cannot be found, stop and say so.** That is a finding, not a
failure — a niche without 50 traceable complaints probably lacks enough pain to build on.
Report how many were found and let the user decide whether to continue or change niche.

## Phase 2 — Cluster into problems

Group the complaints by the underlying problem, not by wording.

A cluster qualifies as a candidate problem only if **at least 5 independent people**
reported it. One loud thread is an anecdote. Discard clusters below the threshold rather
than promoting them to reach a target count.

Select the 2-3 strongest clusters. Strength means: reported often, reported specifically,
and reported by people who appear to have tried to solve it already.

## Phase 3 — Competitors

For each candidate problem, find **2-3 real competitors** — no more. Then search for
complaints about those competitors the same way as Phase 1:

- `site:reddit.com "<competitor>" "alternative"`
- `site:reddit.com "<competitor>" "cancelled"` / `"switched from"` / `"too expensive"`

What people dislike about the incumbent is usually the actual opening. Quote it verbatim,
same rules as Phase 1.

If a problem has no competitors at all, say so plainly and treat it with suspicion — an
empty market more often means no willingness to pay than an untapped opportunity.

## Phase 4 — Write the file

Save to `<app_repo>/research/<niche>.md`. Ask where if the app repo does not exist yet.

Use exactly this shape:

```markdown
# Research: <niche>

<date> · <N> complaints reviewed · <N> qualified

## Problem 1 — <one concrete sentence>

<N> of <N> complaints. <One sentence on who reports it and how consistently.>

**Evidence**

> "<verbatim>"
> — r/<subreddit>, <url>

> "<verbatim>"
> — r/<subreddit>, <url>

**Competitors**

- **<Name>** — <what it does, one line>
  > "<verbatim complaint about it>"
  > — <url>

## Problem 2 — ...
```

Then present the 2-3 problems to the user and stop. The user chooses. Do not recommend
one unless asked, and do not begin specifying or building.

## Banned in the output

The output is evidence and nothing else. Do not write:

- Adjectives selling the opportunity: "massive", "huge", "underserved", "exciting"
- Market-size estimates, TAM figures, or revenue projections — all of it would be invented
- Executive summaries, "key takeaways", or a conclusion restating the sections above
- Feature ideas or proposed solutions — that is the next stage, not this one
- Any sentence that would survive unchanged if the niche were swapped for another one

If a line is not a problem statement, a verbatim quote with a link, or a competitor fact,
delete it.
