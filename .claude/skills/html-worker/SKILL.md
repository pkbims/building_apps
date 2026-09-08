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

Work in a `<project>/<name>/` directory. Copy `server.py` from this skill beside the page.

```bash
mkdir -p <dir> && cp <skill>/server.py <dir>/
cd <dir> && python3 server.py    # run in background, port 7777, PORT= to change
```

**Run the server in a herdr pane, not as a background task**, if the user is inside herdr
(`$HERDR_ENV` is 1). Harness background tasks get killed under memory pressure and the
user's page dies with them:

```bash
herdr pane split --current --direction down --cwd <dir> --no-focus
herdr pane run <returned-pane-id> "python3 server.py"
```

To stop it, `lsof -ti tcp:7777 | xargs kill`. **`pkill` does not reliably kill it.**

Give the user the URL. Verify with `curl -s -o /dev/null -w '%{http_code}' http://localhost:7777/`.

## The page contract

Build the page from `page-template.html`. The JavaScript is already wired; only add
content. Three attributes do everything:

- `data-anchor="id" data-label="Short name"` on any block makes it commentable. Add
  `<button class="cbtn">comment</button>` as its first child.
- `data-radio="id"` around radio inputs records a single-choice decision.
- `data-check="id"` around checkboxes records a multi-choice decision.

Decisions save the instant they are clicked. Comments do not send until the user confirms.
That split is deliberate: decisions are state and must survive a refresh, comments are
messages the user should be able to draft, edit and delete first.

## The round loop

1. User clicks and comments. Nothing reaches you.
2. User presses **Confirm & send**. The server snapshots decisions into a round, marks
   comments sent, and writes `INBOX.md`.
3. You read `INBOX.md` — it holds the comments, what changed since the last round, what is
   still unanswered, and every decision as of now.
4. Address each comment. Revise the page. No server restart is needed for HTML changes.
5. Mark comments addressed so the next round does not repeat them:
   `curl -s -X POST localhost:7777/api/comment/addressed -d '{}'` — or if that endpoint is
   absent, set `addressed: true` **through the server**, never by editing the file.
6. Tell the user what changed and what is now open.

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
  value or it silently reads as unanswered.
- **State lives on disk, not in server memory.** Servers die. Nothing else should.
- **One page, not tabs.** Tabs fragment an argument and let people start in the middle.
  Use a sticky contents rail for navigation and `<details>` for reference material.
- **Comment anchors should be fine-grained.** A comment on a whole section is hard to act
  on; one on a specific decision is unambiguous.
- Verify structure after generating a large page: balanced `<div>` counts, matching
  section tags, and that every `data-radio` sits inside a block with a `data-anchor`.

## Exporting to Markdown

`export-md.py` converts the page into Markdown so there is one source, not two. Copy it
beside the page and run it; set `OUT` to name the output file.

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
