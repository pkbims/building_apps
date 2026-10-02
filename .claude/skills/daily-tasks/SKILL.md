---
name: daily-tasks
description: The user's daily to-do page — they speak or type their plan for the day, Claude turns it into a few task cards with small tickable steps, one list per calendar date. Use when the user says today's tasks, task list, to-do, "plan my day", "what am I doing today", or wants to add, tick or see tasks — even if they don't name the skill. Separate from daily-content-system (filming); neither reads the other.
---

# Daily tasks

A to-do list the user keeps open all day. They dictate the plan (Fn twice in any text
box), press **Make my task list**, and get 2–5 task cards, each with 2–4 steps, a progress
bar and a count. Later in the day, **+ Add task** takes one dictated task and adds it as
one new card with its own steps. Ticking, adding steps by hand and removing steps and
tasks happen on the page and don't involve Claude. So does editing: click any goal, task title, "why" line or step to edit it in place (Enter or
clicking away saves, Esc cancels). So does dragging: the ⠿ grip (shown on
hover) moves a card among cards, or a step within its card or into another card. It uses the
browser's built-in drag and drop, not a library, so the page stays dependency-free and works
offline; the cost is no touch support, which is fine for a desktop page.

Each card also has a **→** button (next to ×, shown on hover) that moves it to another
day: one click for the days either side and for today, or any date in the date box.
The card keeps its steps and its ticks. `POST /api/move {date, to, index}` does it, writing
the destination first and the source second, so a crash mid-move leaves a duplicate to
delete rather than a lost card. A day with no file yet is created and joins the switcher.

Kept separate from `daily-content-system` on purpose: the to-do list covers the whole
day, filming or not, and is organised by calendar date; content is organised by series
day. Neither skill reads the other's files — the user rejected the recap reading this
list as too much coupling (2026-09-22).

## Files

- `server.py` serves the page, stores lists, calls `claude -p` for generation.
- `page.html` has the date switcher, the speak box and the task cards.
- Data: `tasks/YYYY-MM-DD.json` at the series root.

## Start it

```bash
cd building_apps && python3 .claude/skills/daily-tasks/server.py
```

In herdr, start it with `.claude/scripts/server-pane.sh "$PWD" "python3 .claude/skills/daily-tasks/server.py"` (the `servers-tab` tab). It takes the first free port from 7800 and writes it
to `tasks/.port`. Check the title is `Daily Tasks` before giving the URL:
`curl -s localhost:$(cat tasks/.port)/ | grep -o '<title>[^<]*'`.

## Today's goals

A 🎯 card above the tasks: a few tickable lines the user types by hand, stored as `goals`
in the same day file via `POST /api/goals`. Goals are **always hand-typed** — the user asked
for that explicitly (2026-09-23). Never generate them, never send them to Claude, and don't
fill them in from chat unless the user dictates the exact words.

## How generation works

`POST /api/generate {date, text}` sends the spoken plan plus the existing list to
`claude -p` (`--tools ""`, `--no-session-persistence`, model from `TASKS_MODEL`, default
sonnet) with the rules in `PROMPT`. A step whose text comes back unchanged stays ticked,
so saying more later adds to the list without losing progress. Takes ~5–10 s; the button
shows "Writing your tasks…".

`POST /api/add {date, text}` is for one new task: `ADD_PROMPT` turns just that text into
one card, which is appended. The existing list is never sent to Claude, so a later
addition can't reword a card or untick a step. The tradeoff: it won't notice the new
item belongs inside an existing card. The user chose a separate card they can delete
over a quiet rewrite they might not notice (2026-09-22).

If the user gives their plan in chat instead, call `/api/generate` (a whole plan) or `/api/add` (one
task) rather than writing
the JSON yourself, so the format stays the same.

## Format

Each task: one emoji, a title of up to 6 words, a "why" of up to 8 words, and steps of up
to 7 words each. The user asked for parent tasks with sub-steps that are visual and easy
to take in at a glance, and said they were "going too much in depth". Keep lists short;
merge small items rather than adding cards.

## Rules

- Only the server writes the list files, under a lock, atomically.
- The date switcher always includes today, even before today's file exists.
- After editing `page.html`, check the script before telling the user it works: one syntax error
  leaves the page stuck on "Loading…". `bun build` on the extracted `<script>` catches it;
  loading the page in a browser catches runtime errors too.
