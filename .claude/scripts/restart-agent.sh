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

herdr agent prompt "$name" "/exit" >/dev/null
for _ in $(seq 1 30); do                       # wait until Claude has left the pane
  st=$(herdr agent get "$name" 2>/dev/null | python3 -c "import json,sys;r=json.load(sys.stdin)['result'];print(r.get('agent',r).get('agent',''))" 2>/dev/null || true)
  [ "$st" = claude ] || break
  sleep 1
done
herdr agent start "$name" --kind claude --pane "$pane" -- --model "$model" --effort "$effort" --name "$name" >/dev/null
herdr agent prompt "$name" "$prompt" >/dev/null
echo "$pane"
