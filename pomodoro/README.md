# Pomodoro widget

Local-only timer + todo list. No dependencies beyond Python 3.

Click **Pomodoro** in the Dock (`~/Applications/Pomodoro.app`, built with `osacompile`
around `open.sh`). It starts `server.py` if :7799 is quiet, then opens — or focuses — the
widget as a chromeless Chrome app window. From a terminal, `./open.sh [w h x y]` is the same.
`python3 server.py` alone serves it at http://localhost:7799 for a normal tab.

State lives in `state.json` next to the server; a running timer survives refresh and restart.

- Layout follows the window: **Split** (clock left, tasks right), collapses to a column
  under 380 px wide, and becomes a one-row **Strip** under 150 px tall (▾ opens the list).
- **Timer / Stopwatch** switch in the face. Timer runs Focus / Short / Long; click the
  digits to type a length (`45` or `45:30`) — remembered per mode. Stopwatch counts up and
  credits time to the selected task when paused or reset.
- Five looks (cube, mono, paper, lcd, glass) — footer button cycles them.
- Footer: today's tally opens a 7-day history; 🔔 toggles sound.
- Keys: Space start/pause · R reset · Esc close panels. Drag tasks to reorder.

`design-review/` is the html-worker page the layout decisions were made on.

Rebuilding the Dock app: `osacompile -o ~/Applications/Pomodoro.app -e 'do shell script "…/open.sh"'`,
then copy the icns to `Contents/Resources/applet.icns`, **delete `Resources/Assets.car` and
the `CFBundleIconName` key** (macOS prefers the asset catalog over the icns, so the custom
icon is ignored until both go), and `codesign --force --sign -` the bundle.

## Reminders

The **Reminders** tab beside Tasks. Type the thing and when: `Call mum 14:30`,
`standup 9am`, `+20 stretch`, `stretch in 20`. A bare past time rolls to the next
sensible one (9 → 9pm, else tomorrow). At the due minute the widget turns into a
full-bleed alert, chimes, and posts a system notification.

The alert offers **+1 hour** / **+2 hours** (keys `1` and `2`) beside **Got it** (Space or
Esc). Snoozing counts from the moment you press it, not the original due time, so a late
dismissal still buys a full hour; the reminder is reused, so the list keeps one row.

Notifications only fire while the page is open — which, in the Dock app window, it is.
Anything that came due while it was closed fires on next open, labelled "Was due …".
Reminders live in `state.json` with everything else.
