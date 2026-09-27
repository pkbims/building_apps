#!/usr/bin/env bash
# Restart a named worker's Claude session in its own herdr pane, with a fresh context.
#
#   .claude/scripts/restart-agent.sh <name> <model> <effort> "<first prompt>"
#
# For long builds: a worker past ~60% context is restarted at its next checkpoint (the
# ticker says when). Before calling this, the worker must have committed everything and
# updated its notes file (<half>/WORKER-NOTES.md) — the new session starts from its brief,
# those notes, ORCH-QUESTIONS.md and its own git log, not from the old conversation.
# The pane, worktree and branch stay the same. Prints the pane id.
set -euo pipefail
[ "${HERDR_ENV:-}" = 1 ] || { echo "not inside herdr" >&2; exit 1; }
name=$1 model=$2 effort=$3 prompt=$4

info=$(herdr agent get "$name") || { echo "no agent named $name" >&2; exit 1; }
pane=$(printf '%s' "$info" | python3 -c "import json,sys;r=json.load(sys.stdin)['result'];print(r.get('agent',r)['pane_id'])")
cwd=$(printf '%s' "$info" | python3 -c "import json,sys;r=json.load(sys.stdin)['result'];print(r.get('agent',r).get('cwd',''))")
# Workers must be clean. The orchestrator's checkout also holds other sessions' uncommitted
# files (e.g. the PRD page's spec/), so its restart passes SKIP_GIT_CHECK=1.
if [ "${SKIP_GIT_CHECK:-}" != 1 ]; then
  [ -z "$(git -C "$cwd" status --porcelain 2>/dev/null)" ] || { echo "$name has uncommitted work in $cwd — commit first" >&2; exit 1; }
fi

still_claude() {
  st=$(herdr agent get "$name" 2>/dev/null | python3 -c "import json,sys;r=json.load(sys.stdin)['result'];print(r.get('agent',r).get('agent',''))" 2>/dev/null || true)
  [ "$st" = claude ]
}
wait_gone() { for _ in $(seq 1 "$1"); do still_claude || return 0; sleep 1; done; ! still_claude; }

herdr agent prompt "$name" "/exit" >/dev/null
# /exit can stop at "You have 1 unsent feedback draft — Enter to review & send · Esc to discard
# and exit" (backend handover, 2026-09-27). Esc is the no-send answer. Never start over a live
# session: the start command would be typed into it.
if ! wait_gone 30; then
  herdr pane send-keys "$pane" esc >/dev/null
  wait_gone 15 || { echo "$name did not exit after /exit and Esc — check pane $pane" >&2; exit 1; }
fi
herdr agent start "$name" --kind claude --pane "$pane" -- --model "$model" --effort "$effort" --name "$name" >/dev/null
herdr agent prompt "$name" "$prompt" >/dev/null
echo "$pane"
