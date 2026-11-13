#!/usr/bin/env bash
# Usage: pipeline/make.sh <video-id>   Narrate, render and assemble one video into $VIDEOS_OUT.
# Run pipeline/data.sh first if the scene uses cuPhoton data that is not in $VIDEO_DATA yet.
set -euo pipefail
source "$(dirname "$0")/env.sh"
python "$MEDIA/pipeline/narrate.py" "$1"
"$MEDIA/pipeline/render.sh" "$1"
