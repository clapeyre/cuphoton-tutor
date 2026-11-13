#!/usr/bin/env bash
# Recreate the media venv from scratch (user space, no sudo). ~6 GB with CUDA torch.
# Usage: MEDIA_VENV=/path/to/venv pipeline/setup.sh        (default: see env.sh)
# System needs: uv, ffmpeg/ffprobe, cairo + pango (for manim), Liberation Sans/Mono fonts.
# Exact versions of the env that rendered the current videos: pipeline/requirements.lock.txt
#   (uv pip install --python "$MEDIA_VENV/bin/python" -r pipeline/requirements.lock.txt  for a full replay).
set -euo pipefail
source "$(dirname "$0")/env.sh"
[ -e "$MEDIA_VENV" ] && { echo "$MEDIA_VENV exists; remove it or set MEDIA_VENV elsewhere" >&2; exit 1; }
uv venv --python 3.12 "$MEDIA_VENV"
uv pip install --python "$MEDIA_VENV/bin/python" \
  manim==0.22.1 kokoro==0.9.4 misaki==0.9.4 soundfile==0.14.0 matplotlib==3.11.2 astropy==8.0.2 \
  numpy==2.5.4 scipy==1.18.1 torch==2.15.0 \
  "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
# Fetch the Kokoro-82M weights into $HF_HOME once (kokoro would otherwise do it on first use).
mkdir -p "$HF_HOME"
CUDA_VISIBLE_DEVICES= "$MEDIA_VENV/bin/python" -c "from kokoro import KPipeline; KPipeline(lang_code='a')('Ready.', voice='af_heart').__next__(); print('kokoro ok')"
"$MEDIA_VENV/bin/manim" --version
