---
name: html-worker
description: Work with the user through an interactive HTML page served locally, where they click through content, answer decisions, and leave comments anchored to specific blocks that arrive in batches. Use when the user wants to review, shape, or decide on something visually rather than in terminal prose - specs, plans, designs, options, anything long enough that pointing at a part of it beats describing it. Not tied to any document type.
---

# HTML worker

A review loop where the user reacts to a page instead of to paragraphs. They click,
comment on specific blocks, queue those comments, and send them in batches. You read the
batch and revise the page.

This skill owns the mechanics only. What goes *in* the page is not its concern.

## When this beats plain conversation

Use it when the user must react to many things and pointing is easier than describing —
long documents, sets of options, layouts, flows. Do not use it for a single question or a
short answer; a page is heavier than a sentence and should earn its weight.

## Setup

**Inside an app, don't start a server.** A page in an app folder (`app_N/…` or a
`research/<niche>/` started from the App Maker) is served by that app's one server — see the
`app-maker` skill; it appears in the App Maker's navbar on the next load. The steps below are
for a page that lives outside any app (a review of the pipeline itself, say).

Work in a `<project>/<name>/` directory. Copy `server.py` from this skill beside the page.

```bash
mkdir -p <dir> && cp <skill>/server.py <dir>/
cd <dir> && python3 server.py    # first free port from 7777 up
```

**Never assume the port.** Other pages are often already running, so the server takes
the first free port from 7777 upward and writes it to `<dir>/.port`. Read that file after
starting, and use that port for the URL, the `curl` checks and the stop command.
`PORT=N` pins a port and fails if it is taken.

It binds to localhost. `HOST=0.0.0.0 python3 server.py` opens it to the local network so
the user can open the page — or a `prototype.html` beside it — on their phone at
`http://<mac-ip>:<port>/` (`ipconfig getifaddr en0` gives the address).

**Run the server in the herdr `servers-tab`, not as a background task and not as a split of
the user's pane**, if the user is inside herdr (`$HERDR_ENV` is 1). Harness background tasks
get killed under memory pressure, and the user wants their session pane kept at full size:

```bash
.claude/scripts/server-pane.sh <dir> "python3 server.py"   # prints the pane id
```

To stop it, `lsof -ti tcp:$(cat <dir>/.port) | xargs kill`. **`pkill` does not reliably kill it.**

Give the user the URL only after checking it serves *this* page — match the `<title>`, e.g.
`curl -s localhost:$(cat <dir>/.port)/ | grep -o '<title>[^<]*'`. A bare 200 can come from
another page's server on the port you guessed, and the server crashing on bind looks the same.

## The page contract

Build the page from `page-template.html`. The JavaScript is already wired; only add
content. Three attributes do everything:

- `data-anchor="id" data-label="Short name"` on any block makes it commentable. Add
  `<button class="cbtn">comment</button>` as its first child.
- `data-radio="id"` around radio inputs records a single-choice decision.
- `data-check="id"` around checkboxes records a multi-choice decision.
  **Every input needs `name="id"` matching its group** — radios and checkboxes alike. A
  checkbox without it saves under an empty key and its group reads as unanswered.

**Every decision carries Claude's recommendation.** Exactly one option is marked
*recommended* (a small tag on the option) with a one-line reason in its description — for
checkbox groups, say which boxes you'd tick and why in the decision's "why" line. Never
pre-select it: the user still clicks. A decision with no recommendation is a bug — it hands
the user bare labels. The only exception is a question about the user's own taste or facts
Claude cannot know (e.g. "which room is yours"); then say so in the "why" line.

Decisions save the instant they are clicked. Comments do not send until the user confirms.
That split is deliberate: decisions are state and must survive a refresh, comments are
messages the user should be able to draft, edit and delete first.

## The round loop

1. User clicks and comments. Nothing reaches you.
2. User presses **Confirm & send**. The server snapshots decisions into a round, marks
   comments sent, and writes `INBOX.md`.
3. You read `INBOX.md` — it holds the comments, what changed since the last round, what is
   still unanswered, and every decision as of now.
4. `INBOX.md` sorts comments into three kinds — the user picks the kind on the comment
   popup — and they are handled differently:
   - **Change request** — revise the page. The page is the spec; the revision is the
     answer.
   - **Question** — answer it **in the terminal, not on the page.** Answering on the page
     bloats the spec with explanation and drifts it toward whatever the question hinted
     at, costing a round either way. If the answer changes a decision, the user turns
     that into a change request next round, deliberately.
   - **Comment** — context, a reaction, a preference, something the user wants you to
     know. Take it on board and **acknowledge it in the terminal** in a line, saying
     what you took from it. Don't revise the page for it; if it clearly implies a change,
     say so and let the user confirm. Keeps the user free to think out loud without
     every remark becoming an edit.
   No server restart is needed for HTML changes.
5. Mark comments addressed so the next round does not repeat them:
   `curl -s -X POST localhost:$(cat <dir>/.port)/api/comment/addressed -d '{}'` — or if that endpoint is
   absent, set `addressed: true` **through the server**, never by editing the file.
6. Tell the user what changed and what is now open.

## The "Claude is working" bar

After the user sends a round, the page shows a strip under the header: **"Claude is working on
round N…"** with a spinner. It turns into **"Round N revision is ready — Reload"** when either
the page file changes (you rebuilt it) or every comment from that round is marked addressed.
After four minutes with neither, it says to type "sent" in the terminal. It survives a
reload, and a page that sends by its own button (e.g. a stage gate) calls
`window.markWorking(round)` so the bar shows there too.

**Your side of it:** end every round by rebuilding the page *or* marking the comments
addressed — ideally both. A round with only decisions and no revision needed still needs one
of them (`touch index.html` is enough), or the user watches a spinner that never stops.

## Waking up

A local page cannot wake your session. A background watcher can, by blocking on the file
and exiting when it changes, which re-invokes you:

```bash
INBOX=<dir>/INBOX.md
start=$(stat -f %m "$INBOX" 2>/dev/null || echo 0)
while :; do
  cur=$(stat -f %m "$INBOX" 2>/dev/null || echo 0)
  [ "$cur" != "$start" ] && { echo "new round sent"; break; }
  sleep 15
done
```

**Tell the user this is unreliable.** It only works as a harness background task, and those
get reaped. Say plainly: if they confirm and hear nothing within a minute, they should say
"sent". Do not promise the automatic path works.

Restart it after each round. It fires once and exits.

## Rules learned the hard way

- **Only the server writes `state.json`.** Editing it from a script while the server runs
  loses answers to a read-modify-write race. Use `POST /api/decision` instead.
- **Never orphan an answer.** If you replace a decision's options, migrate the existing
  value or it silently reads as unanswered. Retire a dropped id with
  `POST /api/decision {"id": ..., "value": null}`.
- **State lives on disk, not in server memory.** Servers die. Nothing else should.
- **One page, not tabs.** Tabs fragment an argument and let people start in the middle.
  Use a sticky contents rail for navigation and `<details>` for reference material.
- **Comment anchors should be fine-grained.** A comment on a whole section is hard to act
  on; one on a specific decision is unambiguous.
- Verify structure after generating a large page: balanced `<div>` counts, matching
  section tags, and that every `data-radio` sits inside a block with a `data-anchor`.

## Updating existing pages after a skill change

Pages are copies of the template beside copies of `server.py`, so a change to the skill
does not reach page directories that already exist. `sync.py <page-dir> ...` brings a
directory up to date: the page's `<style>`, font `<link>`, theme script, comment popup
and page `<script>` are swapped for the template's, and `server.py` / `export-md.py`
are replaced. `<main>` content, anchors and `state.json` are untouched. Refresh the
browser; restart the server (it loads `server.py` once) — in its herdr pane if that is
where it runs. `theme-lab/index.html` is a preview page for trying palettes, fonts and
sizes against real template markup before changing the template.

## Marking what changed

Reviewers lose track of what moved between rounds. When you revise a block, add
`data-changed="N"` to it, N being the round the revision answers. The left rail then opens
with "Changed in round N" — every block from the latest round, clickable, flashed on
arrival — and each such block carries an orange edge and tag. Blocks marked with earlier
rounds keep their tag but drop out of the rail. Put the attribute on the smallest block
that changed, not the whole section, and give it a `data-label` that says what changed
("R8 rewritten", "task catalogue — new").

## Exporting to Markdown

`export-md.py` converts the page into Markdown so there is one source, not two. Copy it
beside the page and run it; set `OUT` (path relative to the page dir's parent) and `TITLE`.
Links survive as Markdown links, so quoted evidence stays traceable; comment buttons and
section numbers are dropped.

It handles sections and headings, paragraphs, lists, blockquotes, `table.t`, `pre.code`,
`<details>`, `.plain` as a quote and `.risk` as a `> [!WARNING]` callout. Mermaid blocks
become ```` ```mermaid ```` fences, which GitHub renders — keep `<br/>` inside node labels
intact rather than converting it to a newline, or the diagram breaks.

Decision blocks render with the recorded answer marked **→** and the rejected options
listed beneath, so the exported document shows what was chosen *and* what was turned down.

**Never hand-write a second narrative alongside the page.** Doing that produces two
documents that drift, and the markdown ends up a thin summary of the real thing. If part
of the page is generated by JavaScript — mockups built from an array, for example — the
exporter must pull that content out of the script too, or those sections come out empty.
