#!/usr/bin/env bash
# Usage: pipeline/data.sh [vN ...]   (default: v0 v1 v2)
# Real cuPhoton CPU outputs for the scenes, written to $VIDEO_DATA. Runs in the cuPhoton
# checkout's own env ($CUPHOTON_DIR/.venv, via uv), not in $MEDIA_VENV.
# Also creates, once: sample/ (the guide's synthetic pair) and quickstart_auto/ (summary.json for v2).
set -euo pipefail
source "$(dirname "$0")/env.sh"
export CUDA_VISIBLE_DEVICES=  # the videos show CPU runs (v2 shows gpu_available: false)
mkdir -p "$VIDEO_DATA"; cd "$VIDEO_DATA"
run() { uv run --no-sync --project "$CUPHOTON_DIR" python "$@"; }
echo "cuPhoton $(git -C "$CUPHOTON_DIR" rev-parse --short HEAD) -> $VIDEO_DATA"
[ -f sample/reference.fits ] || run "$MEDIA/pipeline/make_sample.py" "$CUPHOTON_DIR" .
[ -f quickstart_auto/summary.json ] || run "$CUPHOTON_DIR/examples/run_quickstarts.py" --profile auto --output-dir quickstart_auto
for v in ${@:-v0 v1 v2}; do
  case $v in
    v0) run "$MEDIA/scenes/data_v0.py" sample . ;;
    *)  run "$MEDIA/scenes/data_$v.py" . ;;   # data_vN.py reads sample/ from the cwd
  esac
done
