#!/bin/sh
# One-click launcher: start the server if nothing is on :7799, then open (or focus)
# the widget as a chromeless Chrome app window.
# Args: width height x y — defaults put it bottom-left.
cd "$(dirname "$0")"
W=${1:-440} H=${2:-260} X=${3:-0} Y=${4:-680}

if ! nc -z localhost 7799 2>/dev/null; then
  nohup python3 server.py >> server.log 2>&1 &
  for i in 1 2 3 4 5 6 7 8 9 10; do nc -z localhost 7799 2>/dev/null && break; sleep 0.2; done
fi

# already open? bring it forward instead of opening a second one
if osascript -e 'tell application "Google Chrome"
  repeat with w in windows
    if title of w ends with "Pomodoro" then
      set index of w to 1
      activate
      return "focused"
    end if
  end repeat
  return "none"
end tell' 2>/dev/null | grep -q focused; then exit 0; fi

open -na "Google Chrome" --args --app=http://localhost:7799/ --window-size=$W,$H --window-position=$X,$Y
