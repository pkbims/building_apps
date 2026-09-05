# building_apps — series doctrine

A series of small full-stack apps, built one at a time. Each is genuinely deployable and
able to carry ~10,000 real users, and each is the subject of a learning video. The
differentiator against AI-generated demo apps is that nothing here is faked.

## Non-negotiable baseline

Every app ships with all of these. Never propose the shortcut version — no in-memory
stores, no stubbed auth, no skipped CI — even when the app is small. Skipping any of them
defeats the point of the series.

- Real authentication (real sessions/tokens, not a hardcoded user)
- Real database, with migrations
- Docker containerization
- GitHub Actions CI/CD
- Tests that gate the pipeline before prod
- Rate limiting
- Health checks
- Error tracking
- Structured logging
- Metrics, plus a dashboard to view them
- Deliberate failure handling

Deploying locally first is acceptable.

## Architectural constraints

- Adding a feature must stay cheap.
- Restyling must stay cheap. UI changes must not require touching business logic.
- ~10k users is a modest load. The realism comes from the operational layer — what happens
  when the DB connection drops, when a deploy is bad, when someone hammers the login
  endpoint — not from scale. Don't reach for Kubernetes to look serious.

## Stack

Not yet decided. Settle the choices explicitly when app_1 starts — auth approach, database,
hosting — rather than defaulting to something silently. The intent is that the whole series
then reuses one stack and varies the domain, so viewers build muscle memory instead of
relearning the plumbing every episode.

## Layout

```
building_apps/
├── CLAUDE.md       this file — always-on series doctrine
├── PIPELINE.md     the stages, in order
├── PROGRESS.md     where each app stands
├── .claude/
│   ├── skills/     shared procedures, extracted from real work
│   └── agents/     reusable agent definitions
└── app_N/          each app is its own git repo
```

Each app is its own repo: its own CI, its own deploy, and viewers can clone one without
the rest. This parent repo tracks the pipeline itself, which is the most reusable thing
produced here. App directories are gitignored from this repo on purpose.

App-specific facts belong in that app's own CLAUDE.md, not this one. This file is loaded
into every session, so every line here costs context against the actual code — it holds
only what would otherwise be gotten wrong.

## Working agreement

- When we do something for the second or third time, stop and say so, and name it as a
  candidate for a skill, an agent, or a line in this file. Extract on the third
  occurrence, not the first — anything extracted earlier is a guess about the workflow.
- State the tradeoff behind each engineering choice in a sentence. This material gets
  narrated on camera, so an unexplained correct answer is only half useful.
- Progress lives in PROGRESS.md and in each app's own CLAUDE.md, never only in chat.
