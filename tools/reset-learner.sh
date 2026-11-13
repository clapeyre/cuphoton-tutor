#!/bin/bash
# Start the learner fresh. The current learner/ (progress, conversations, page
# state, tutor sessions, workspace, feedback queue) is archived, never deleted:
# runs/learner-<timestamp>[-label]/. Restarts the dev server if it was running.
#   tools/reset-learner.sh [label]
set -euo pipefail
cd "$(dirname "$0")/.."
label=${1:+-$1}
was_running=0
if [ -f server.pid ] && kill -0 "$(cat server.pid)" 2>/dev/null; then was_running=1; kill "$(cat server.pid)"; sleep 1; fi
if [ -d learner ] && [ -n "$(ls -A learner)" ]; then
  dest="runs/learner-$(date +%m%d-%H%M%S)$label"
  mkdir -p runs
  mv learner "$dest"
  git rev-parse --short HEAD > "$dest/COMMIT" 2>/dev/null || true
  echo "archived learner/ to $dest"
fi
mkdir -p learner
[ "$was_running" = 1 ] && tools/serve.sh || true
