---
name: app-maker
description: The App Maker — the home page for making apps (localhost:7710, grown from the progress visualizer). Lists every app, shows what needs the user across all apps, opens any stage's page inside it with a left navbar of stages, a Talk-to-Claude box per stage, Start buttons for stages and "New app" to start research. Each app has ONE server (app_server.py) for all its pages. Use when the user asks for the App Maker, wants to start a new app, open a stage, or asks why a page or app server isn't running.
---

# App Maker

Decided on the `app-maker-vision/` page (round 1, 2026-09-26). The user lives in one page;
the terminal is for first-time setup, emergencies, and improving the App Maker itself.

| Piece | Where | What it does |
|---|---|---|
| **App Maker** | `localhost:7710` — the progress visualizer's server, grown (D3). `/` is the App Maker, `/progress` the old board | Your apps as cards; one "needs you" line across all apps; inside an app, a navbar of every stage, the stage's page on the right, a Talk box under it; documents |
| **One server per app** | `scripts/app_server.py <app>`, port in `<app>/.appserver.port` (first free from 7801) | Serves every html-worker page of the app at its own path (`/spec/`, `/engineering-center/`, `/research/reviewer/`) with its API at `<path>api/…`. Always on (D2): the App Maker starts it if it isn't running |
| **Monitoring center** | `localhost:7700`, separate | The machine: every server, start / restart / stop |

## How the pieces talk

- **Pages are unchanged.** They call `/api/…`; the app server injects one line into each page
  that points those calls at the page's own path. So a page works on its own server *or*
  under the app server with no edit. While the app server runs, it is the only writer of a
  page's `state.json` — close the page's own server (from the monitoring center).
- **Needs you** is read from each page's `feed.json` — the shared format written by
  `code-orchestrator/scripts/post.py` (open asks, and to-dos marked `--now`). A stage that
  wants to ask the user uses the same `post.py` against its own page folder. Herdr's
  `blocked` state (an approval or question in a terminal) shows as a black "Terminal" chip.
- **Talk box** (D5): the App Maker → the app server's `<page>api/talk` → the message is saved
  in the page's `talk.json` and typed into the stage's Claude session through herdr. The
  session replies with `python3 .claude/skills/app-maker/scripts/talk.py <page_dir> "reply"`.
  Which session answers which page: `<app>/.appmaker.json → "agents": {"<page path>": "<herdr name>"}`.
- **Start buttons** (D6): `maker.START` maps a stage to its skill; pressing Start opens a herdr
  tab (`start-agent.sh`) and records the session in `.appmaker.json`. **New app** creates
  `research/<slug>/` with its `.appmaker.json` and starts `/research` — research runs before
  any `app_N` exists (PIPELINE stage 1); the niche shows as a card from then on.

## Overall progress, the Guide, and one workspace per app

- `#/<app>` opens **Overall progress**: every pipeline stage with its status, its checks and its
  documents — read from `scan.py`, so it replaces the separate progress board (still at `/progress`,
  no longer linked). Each row's **Open** jumps to that stage in the navbar.
- **Guide** in the top bar: how an app gets made with the App Maker, stage by stage — the skill
  behind each, and the page where the user answers. Written in `maker.html` (`GUIDE`).
- **New app creates a herdr workspace first** (“<Name> app”, like “decorate interior app”) and starts
  research in its first tab. The workspace id is saved in `.appmaker.json → "workspace"`; every later
  Start button opens its tab there, and the app's server goes in that workspace's `servers-tab`
  (`WS=` for `start-agent.sh` / `server-pane.sh`).

## Themes

The **🎨 Theme** menu: a mode (Auto · Light · Dark) × a palette (Clay · Homi · Ocean · Forest ·
Mono), remembered in the browser. The App Maker applies it to itself and posts it into the page
in its frame (the app server injects a small listener into every page; `/md` documents have
one too), so every stage and document follows the same look. `?pal=homi&mode=dark` in the URL
sets it too. A palette is only colour tokens (`--bg --panel --ink --muted --faint --line
--accent --soft`) — the same names the html-worker template uses; add one in `maker.html`.

## The stages in the navbar

`maker.STAGES` — Research · Positioning · The case · The experience (pick v1) · Can we build
it? · Prototype v1 · Design direction · Technical decisions (the six PRD parts open the PRD
page at their section) · Engineering center · Features · Ship. Status comes from the
progress visualizer's `scan.py` (one source), so the navbar and the board always agree.

## Rules

- A new page inside an app needs no server of its own: put it in the app folder with
  `index.html` + `state.json` and the app server serves it on the next request.
- Never serve hidden files; the app server binds to localhost only.
- Restarting the App Maker or an app server to pick up code is fine; closing one for good is
  the user's call (monitoring center).
