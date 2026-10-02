---
name: daily-content-system
description: The series' filming loop — a local page where "+" turns work into ~2 minute recording scripts (exact words, in the user's voice) that are reviewed and approved in a comment window before filming. Chunks come from a time window of every agent's work (optionally narrowed by a focus prompt like "only the DesignMyRoom work") or from a past-work prompt that digs through old logs and git; recordings are joined in Remotion. Use when the user says recap, "+", chunk, past work, script, draft, review the draft, content day, open the content page, new content day, "what did I do in the last hour", or edit day-NN — even if they don't name the skill.
---

# Daily content system

The user builds 10 apps in 30 days and films it. Work becomes **chunks**: ~2 minute
Screen Studio takes clicking through something while reading a script. The day's chunks
become the long video (Skool); the short (5 channels) is cut from the same day.

Every chunk goes **prompt → draft → review → approved → recorded**. Kinds:

| Kind | Made from | Tab |
|---|---|---|
| recap | a time window of every agent's work, plus an optional **focus** prompt | ⏱️ N · 14:30–16:15 |
| outline | a **past-work** prompt, no window: proposes 2–6 chunks; approving it creates them | 🗂️ Outline |
| chunk | one entry of an approved outline | 📦 N |
| intro / outro | the day's approved chunks, filmed face to camera at the end of the day | 🎬 Intro / 🏁 Outro |

Why this shape (review, 2026-09-23): bullet scripts gave no direction on camera, so scripts
are the exact words; the user wants to shape each draft before filming; and a video is
often about one app, or about old work, not "everything in the last hour". Talking over
silent clips was tried on practice day 1 and felt unnatural — don't propose it again. The
to-do list is a separate skill, `daily-tasks`; nothing here reads it.

## Files

| File | Job |
|---|---|
| `server.py` | Pages, storage, background drafting and revising, all prompts |
| `page.html` | The day: switcher, chunk tabs, + panel, progress rail |
| `review.html` | One draft under review: comment on any part, send, approve |
| `hour.py` | Digest of every agent's activity in a time window (also a CLI) |

Data: `content/day-NN/day.json` (the day; its items are in `recaps` for history's sake),
recordings in `content/day-NN/hours/` as `hour-NN.mp4`, `chunk-NN.mp4`, `intro.mp4` and
`outro.mp4`. Each item's name is fixed when it's made and shown on its tab. `content/app-names.json` holds app nicknames. Videos are
gitignored.

## Start it

Inside herdr, `.claude/scripts/server-pane.sh "$PWD" "python3 .claude/skills/daily-content-system/server.py"`
from `building_apps`: it goes in `servers-tab`, never as a split of the user's pane. It takes
the first free port from 7790 (`content/.port`). Check the title is `Daily Content` before
giving the URL. Restart after editing `server.py`; `page.html` / `review.html` changes need
only a refresh. The monitoring center (7700) can stop and start it.

## The loop

1. **New day** — "+ New day" takes the day after the previous one (the user often sets up
   tomorrow the evening before); click the date to change it. The day is in the URL
   (`#day-02`). "Delete day" moves the folder to `content/.trash/`.
2. **+ → ⏱️ Recap** — the window starts where the last recap ended (**never overlapping**);
   the user picks the end. Over 75 min it offers hourly splits. The optional **"What should
   this cover?"** box narrows it: if it names an app, agents working elsewhere are dropped
   from the digest (`focus_apps()` → `hour.digest(apps=…)`, header says "focus: kept N of M");
   the prompt also tells Claude to cover only matching work.
3. **+ → 📦 Past work** — a prompt. The outline is written with read-only tools (below), in
   ~1 min. Review it like any draft; **approving it creates one chunk per entry**, each
   drafted in the background (~35 s each, in parallel). An outline can't be reopened once
   its chunks exist.
4. **Review** — each draft's tab has **✏️ Review draft**, which opens `review.html` in its own
   window (the user chose a button, not a pop-up). Comment on the summary, the open list,
   any beat, any outline chunk, or in general, as **Change this / Ask a question / Comment**.
   **Send comments** → Claude revises in ~30 s: only the parts commented on change, and those
   are marked "changed". Questions get an answer in "Earlier rounds" and don't change the
   draft. **Approve** is disabled while comments are queued. Approved tabs show ✅ and can be
   reopened.
5. **Record** — Screen Studio, camera + mic, saved to the path on the tab; the dot turns green.
6. **Intro / outro** — once at least one chunk is approved; written from approved chunks.
7. **End of day** — `cd video && bun day.ts day-NN` then preview the `day` composition in
   Remotion Studio (`localhost:3000/day`); the user renders it. Video order = tab order:
   intro, recaps and chunks as made, outro; recordings not made yet are left out and listed.
   Each recap/chunk gets a 2 s "Hour N · title" card; pauses over 0.5 s at -30 dB are
   shortened to 0.25 s; captions, day badge, soft music (5% under voice, 18% on cards).
   - Pauses come from ffmpeg `silencedetect`, not whisper (its word offsets absorb pauses).
     Captions use whisper's DTW `timestampMs`. Whisper drops "um"/"uh".
   - Studio's timeline ignores automated clicks: check frames with `bunx remotion still`.

If the user says "recap" in chat, `POST /api/recap {"day","kind":"recap","until":null,"split":false,"focus":""}`
(or `"kind":"past","focus":"<prompt>"`) and point them to the tab's Review button.

## The script

Each draft has **📖 What happened** (a story to read first), **🧰 Open these first** (exact
locations; localhost URLs are live-checked and flagged "not running"), and **🎬 Script**:
5–9 beats of `SHOW · <what's on screen>` + **the exact words**, 220–270 words (~2 min), shown
with a word count and time. Rules live in `SCRIPT_RULES` / `DRAFT_SHAPE`:

- **In the user's voice**: `voice_sample()` feeds their own whisper transcripts
  (`content/day-*/hours/*.captions.json`) into every draft and revision.
- **For a viewer**: no tooling hiccups (failed edits, restarts, typechecks); "Claude", never
  "agent 3"; transitions written in.
- **Facts only from the input**: first drafts stated wrong ports and invented a "scrapped"
  folder until this rule and the served-page rule were added. Review catches the rest.
- `clean_lines()` strips an echoed "SHOW:" label from cues (the model did it every beat).

## Past-work digging

`past_context()` pre-collects git history (90 days) of the apps the prompt names (or all)
and an index of past agent sessions (log file, folder, dates, first request). Claude then
gets **Read, Grep, Glob only**, with `--add-dir ~/.claude/projects`; Bash, Write and Edit are
disallowed. A git Bash allowlist was tried first and denied every call; pre-collecting is
simpler and can't run anything.

App names: `app_folders()` reads each app's `CLAUDE.md` / `PRD.md` heading plus
`content/app-names.json` (practice_1 is **DesignMyRoom**, which the user also calls
"decorMyRoom"), and near-misses on long names match too. Add a nickname there when a
focus prompt misses.

## Who does the writing

No tab or pane: every draft, revision and outline is a **one-off background `claude -p`**
started by the server (in servers-tab), on **Opus at high effort** (`RECAP_MODEL`,
`RECAP_EFFORT`), chosen by the user for script quality. `--no-session-persistence`, so
it's never an "agent" in the next digest. Each call knows only what it's given:

- **Draft:** the format rules, the day's title and focus, a ~1,800-character voice sample,
  plus the digest (recap), the approved chunks (intro/outro), or the git and session index
  (outline). Read-only tools only for past work.
- **Revision:** the current draft, **every earlier round's comments and answers** (so it
  doesn't undo past changes), the **source the draft was written from** (the stored
  `digest`, up to 40k characters) to check facts against, a voice sample, and this round's
  comments. Outline and chunk revisions also get read-only tools. In testing, it answered
  "which files were written?" from the source and flagged a closing line the log didn't support.

It never sees this conversation, `CLAUDE.md` or memory. Rounds took ~12 s on Opus.

## How recaps know what happened

`hour.py` reads every Claude Code session log (`~/.claude/projects/*/*.jsonl`) inside the
window: what the user asked (including pasted text), files written (marked "since deleted"
when gone), pages served, the agent's `away_summary`, last replies, and git commits.
Filter by each line's timestamp, never file mtime (resumed sessions bump mtimes). Every
`claude -p` runs with `--no-session-persistence`, so drafting never shows up as an agent in
the next digest.

## Progress rail

Derived on every read by `progress()`. "Recaps and chunks" counts chunks, how many are
approved and how many recorded, and is done when all are recorded. Intro/outro show
"Draft: review and approve it" / "Approved, not recorded yet" / "Recorded". Other steps
are unchanged (ticks in `checks`). Making the short is not a step until the user decides how.

## Rules

- **Only the server writes `day.json`** (a lock, atomic writes). Use the API.
- On restart, a draft left `writing` becomes `error` (Try again); one left `revising` goes
  back to `draft` with its comments re-queued, so nothing is lost.
- Old items with status `ready` count as `approved` (`normalise()`).
- **Delete** (🗑 Delete recap / chunk / outline / intro, top right of every tab) confirms inline
  like Delete day. A recording, if any, is moved to `content/.trash/` (never erased) and
  its captions file dropped. Deleting an outline leaves its chunks.
- **Recording names are pinned per item** (`file`, set by `file_for()` when the item is
  made). They used to be computed by position, so deleting recap 1 would have pointed
  recap 2 at `hour-01.mp4`. `normalise()` pins names on older items, and `day.ts` uses
  `file` too.
- Background drafting and revising check the item still exists before saving, so deleting
  mid-write just drops the result.
- The page never redraws while the + panel is open or a box is being typed in.
- After editing `page.html` or `review.html`, `bun build` the extracted `<script>` and load
  it in a browser before saying it works; one syntax error leaves it on "Loading…".
