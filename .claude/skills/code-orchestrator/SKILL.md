---
name: code-orchestrator
description: Run an app's build after its PRD is handed over — stage 4 (contract freeze) and stage 5 (build v1) — as the orchestrator that writes no app code, starts and checks two coding workers, and talks to the user only through an "engineering center" page (html-worker UI) with a 5-minute status check, instant questions and notifications. Use when the PRD page's hand-over button is pressed, when the user says "start the build", "code-orchestrator", "run the orchestrator for app_N", or asks to set up the engineering center.
---

# Code orchestrator

Invoked as `/code-orchestrator <app>` — normally typed for you by the PRD page's hand-over
button (`create-prd`), in a session started on **Opus at high effort**. From then on the user
**only looks at the engineering center**: every update, question and checkpoint goes there, never
only in this terminal. Extracted 2026-09-26 on the third orchestrator run (practice_1,
practice_4, app_1).

The whole flow:

- **Check the hand-over** → **set up the engineering center** → **write HANDOFF.md** →
  **stage 4: freeze the contract** → **brief and start the workers** →
  **stage 5: the loop — verify, merge, post** → **v1 on TestFlight**

## Before you start

All of these must exist, or post nothing and tell the user in the terminal which is missing:

- `<app>/PRD.md` exported, and `<app>/spec/state.json` with `prd_ready` set (the hand-over).
- `<app>/design/HANDOFF.md` and `design/tokens.json` (the design came back).
- `<app>/CLAUDE.md`, `../PIPELINE.md` stages 4–5, `../CLAUDE.md` (the series baseline).

## Step 1 — Set up the engineering center

```bash
python3 .claude/skills/code-orchestrator/scripts/setup.py <app>
```

It builds `<app>/engineering-center/` (html-worker template + `room-body.html`), starts the page
server and the **ticker** in the herdr `servers-tab`, and prints the URL. Re-run it any time
— it only starts what isn't running and rebuilds the page. Then post the first update and
give the user the URL in the terminal, once:

```bash
POST=.claude/skills/code-orchestrator/scripts/post.py; ROOM=<app>/engineering-center   # two variables: zsh does not split one
python3 $POST $ROOM update "Engineering center is live. I'm reading the PRD and the design; next I freeze the contract."
```

What the engineering center is made of, and who writes what — nothing races:

| File | Written by | Shows |
|---|---|---|
| `feed.json` | you, via `post.py` only | updates, questions (asks), checkpoints, the user's to-dos |
| `status.json` | the ticker (status every 5 min, commits every 30 s) | each agent's state, the heartbeat line, open ORCH-QUESTIONS, and recent commits in three lanes — backend, iOS, orchestrator (by the model that wrote them and the files they touch) |
| `state.json` | the page server | the user's answers and comments (html-worker rules) |

**The ticker** (`scripts/ticker.py`, no model, no tokens): every 5 minutes a status line;
the moment a new ask appears, a macOS notification; the moment the user presses **Send to the
orchestrator**, it types a prompt into your herdr pane telling you to read
`engineering-center/INBOX.md`. You never run a watcher of your own. If the page's dot turns red
("the 5-minute check is not running"), re-run `setup.py`.

**Claude usage and Expenses** (2026-09-27). *Claude usage*: the user's plan limits (5-hour and weekly %, read
off a Claude status line) and, per Claude, busy time, tokens, written, and cost at API prices
(`scripts/prices.json`, dated, from claude.com/pricing). *Expenses*: monthly bills the user sets on the page,
and tests — **record every real run that calls OpenAI or SearchApi**:
`python3 scripts/expense.py <room> test "<what>" --openai $ --searchapi $ --calls n --searches n --source "<where from>"`
(real figures; say "estimate" if not). Keep the page's notes to one short line.

**The Ticker section** (2026-09-27) is the ticker's dashboard, on the engineering center: is it alive,
today's counts (wake-ups by reason, fresh starts, status checks, problems), its jobs with their last run
and result (folded behind "Show its jobs"), and a timeline of **every time a helper nudged Claude** —
the ticker's wake-ups, handover steps, update requests and problems, plus the app server's Send wake-ups,
message wake-ups and notifications — each with exactly what was sent. The log is
`<app>/helpers-log.jsonl` (`app-maker/scripts/helperlog.py`, last 2,000 lines); the job status is
`status.json → jobs`. When you change what the ticker does, log it with `hlog(...)` and record the job
with `job(...)`, or it disappears from the dashboard.

## Step 2 — HANDOFF.md

Write `<app>/HANDOFF.md`: your role, the reading order, every settled decision from the PRD
that must not be reopened, the roster, what is in flight, gotchas. Rewrite it as things
change — it is what lets the role survive a context reset. app_1's is the model.

## Step 3 — Stage 4, the contract freeze

Exactly as `PIPELINE.md` stage 4 says, copying practice_1's pattern rather than reinventing:
`backend/app/schemas.py` + route signatures in `backend/app/main.py` from the PRD's data and
calls sections, `contract/openapi.json` generated (never hand-edited), a CI
regenerate-and-diff check, ruff/mypy excluding the frozen files, `ORCH-QUESTIONS.md`
created. Done when `openapi.json` is committed and CI is green on GitHub.

Things only the user can do (a GitHub repo, an Apple Developer team, a hosting account)
become **to-dos plus an ask**, posted the moment you know you'll need them — not when you're
already blocked:

```bash
python3 $POST $ROOM todo github "Create an empty private GitHub repo for app_1 and paste its URL"
python3 $POST $ROOM ask github_repo "Where should app_1's code live on GitHub?" \
  --why "CI must pass on GitHub before the contract counts as frozen." \
  --option paste "I'll paste a repo URL" "Create an empty private repo, then comment the URL on this question." \
  --option gh "Install gh and let you create it" "brew install gh, then gh auth login." --rec paste
```

## Step 4 — Brief and start the workers

One brief per worker, `<half>/AGENT.md`: read order, what it owns, what it must not touch,
**the one rule** (never edit the contract; append to `ORCH-QUESTIONS.md` and keep working),
TDD, commit discipline — **every commit body opens with one plain-English sentence saying
what changed for the app** (the engineering center shows that sentence under the title; the technical
detail follows) — the build order it works down. Each in its own git worktree and
branch, outside the app folder (app_1's layout):
`git -C <app> worktree add ~/.herdr/worktrees/series_<app>/backend -b backend` (same for `ios`).
Start them — **workers run Sonnet at high effort**:

```bash
W=~/.herdr/worktrees/series_<app>
.claude/scripts/start-agent.sh backend $W/backend sonnet high "Read AGENT.md and start."
.claude/scripts/start-agent.sh ios     $W/ios     sonnet high "Read AGENT.md and start."
```

Post an update naming both, and what each builds first (the riskiest chain first — the
PRD's build order).

## Step 5 — The loop

You are woken by the ticker — when the user sends a round, and (every 30 s) when a worker posts
a new open question or checkpoint in any worktree's `ORCH-QUESTIONS.md`, or goes from working to
idle/done. Workers post a checkpoint and **carry on**; you verify in parallel and tell them if
something must be fixed first — a checkpoint that waits on you leaves a worker idle. Each time:

1. **A round from the user** — read `engineering-center/INBOX.md`. Answered asks: act, then
   `post.py $ROOM resolve <id> --note "<what you did>"`. Comments: change requests → do them;
   questions → answer with `post.py update`; notes → acknowledge with `post.py update`.
   Then mark comments addressed:
   `curl -s -X POST localhost:$(cat <app>/.appserver.port)/engineering-center/api/comment/addressed -d '{}'`,
   and **always** `touch <app>/engineering-center/index.html` — the page's "Claude is working" bar
   clears only when that round's comments are addressed *or* the page file changes, so a
   round with no comments (decisions only) otherwise shows "Still waiting" forever. Re-read
   `INBOX.md` just before marking: a new round can land while you work.
2. **A worker question** (`ORCH-QUESTIONS.md`) — answer inline. If it is really the user's
   call (a product choice, money, an account), turn it into an ask; never guess on their
   behalf.
3. **A checkpoint** — run the worker's tests yourself, start the stack, check the flow it
   claims. Only then merge into `main` and post it:
   `post.py $ROOM checkpoint "<feature> merged" --detail "<tests run, what you checked>" --verified`.
   A claim you could not verify is posted without `--verified`, with why.
   Then move the Progress meter: `post.py $ROOM step <half> <k> done --note "checked and merged <date>"`
   and `post.py $ROOM step <half> <k+1> doing`. Set each half's steps once, from the build
   order, with `post.py $ROOM plan <half> "<step>" …` (plain words — the user reads them).
4. **Context fills — the ticker handles it (context manager, 2026-09-27).** Sessions are treated
   like servers. At 70% the ticker asks the agent (worker or orchestrator) to drain: finish,
   commit, update its notes (`WORKER-NOTES.md` / `HANDOFF.md`), `touch <room>/.handover/<name>.ready`,
   stop. When it's ready, idle and (for a worker) clean, the ticker restarts it under the same
   herdr name with a resume prompt, confirms it's up, and posts one line. Nudge at 85%. One
   restart at a time; wake-ups for the orchestrator are held while it restarts; a snapshot of
   the build is left in `.handover/snapshot.json`. Force one with `touch .handover/<name>.request`.
   When the ticker asks you to hand over, do it at your next clean point.
5. **Every real paid test run → Expenses** (user, 2026-09-27). One line per run that called OpenAI or
   SearchApi: `python3 .claude/skills/code-orchestrator/scripts/expense.py <app>/engineering-center test "<what>"
   --openai <$> --searchapi <$> --calls <n> --searches <n> --when <iso> --source "<where the figure comes from>"`.
   Real figures only (the backend's cost log, a provider's usage page, a run you measured); anything priced from
   call counts says "estimate" in `--source`. Monthly bills are the user's, set on the page.
6. **Stage changes** — update `PROGRESS.md` and the app's `CLAUDE.md`; post an update.

**"Get me an update"** — a button on the page. The ticker sees it within ~10 s and prompts you:
post **one** update, at most 4 short lines — done since your last update, what backend and ios are
each on, what's next, anything waiting on the user. Check git and the workers first; don't guess.

**What to post, and when** — the user reads only the engineering center:

- An **update** at every real step — **one or two short sentences**; the page shows only the
  latest 5, and only the first sentence until the user opens it: stage started or finished, a worker started, a merge, CI
  red or green, a decision you made and its tradeoff in one sentence. Not "still working" —
  the ticker covers that every 5 minutes.
- An **ask** the moment something needs the user. Options carry the three plain lines' worth
  of detail and **exactly one `--rec`** (series rule). An ask with no options is answered by
  comment. Never ask only in the terminal.
- **Whenever you need the user, or have just unblocked them, it goes in Needs you** (user, 2026-09-27):
  an ask (it notifies) or a `--now` to-do — "the fix is merged, press ⌘R now", a to-do that just became
  actionable, a decision. An update alone never counts: updates don't notify.
- **Anything that needs the terminal is an ask, never an update** — only asks notify. Some
  answers only count typed in the terminal (Claude Code's safety check won't take an
  irreversible action — a history rewrite, a force-push — on the strength of a page file).
  Post an ask titled "Go to the terminal: …" saying what to type there.
- A **checkpoint** for every merge into `main`.
- A **to-do** for anything only the user can do, marked `done` when it is. Add `--now` only when
  the build is waiting on it — those show under *Needs you*; the rest sit in *Your to-do list — no
  rush* at the bottom of the page.

Plain English, short, no codes the user must remember; state the tradeoff behind each
engineering choice in a sentence (this is narrated on camera).

## Rules

- **You write no app code.** You write the contract, the briefs, answers, merges and posts.
  An orchestrator that codes stops verifying.
- The contract changes only through `ORCH-QUESTIONS.md`, answered by you, regenerated, and
  posted as an update.
- Never print or commit keys. Never stop a page server for good — the user closes servers;
  restarting one to pick up code is fine.
- Stage 5 is done when both branches are merged, the baseline items are in, and **v1 is on
  TestFlight, talking to a hosted backend**. Tag `v1`, post it, update `PROGRESS.md`.
