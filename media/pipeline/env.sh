# Sourced by the pipeline scripts (or by you: `source media/pipeline/env.sh`).
# Every variable can be overridden from the environment.
MEDIA=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd); export MEDIA
export MEDIA_VENV=${MEDIA_VENV:-$HOME/cuphoton-overnight/tools-media/venv}  # manim + kokoro (pipeline/setup.sh)
export HF_HOME=${HF_HOME:-$HOME/cuphoton-overnight/tools-media/hf}           # Kokoro-82M weights
export CUPHOTON_DIR=${CUPHOTON_DIR:-$HOME/cuphoton-overnight/cuPhoton}       # checkout with its own .venv
export MEDIA_RENDERS=${MEDIA_RENDERS:-$MEDIA/renders}  # per-video intermediates: audio/, manim/, timings.json
export VIDEO_DATA=${VIDEO_DATA:-$MEDIA_RENDERS/data}   # sample pair, quickstart run, vN.npz/json
export VIDEOS_OUT=${VIDEOS_OUT:-$MEDIA/videos}         # final <id>.mp4 + <id>.srt, served by the app
export QUALITY=${QUALITY:-m}                           # manim -q: l=480p15, m=720p30 (drafts), h=1080p60
case ":$PATH:" in *":$MEDIA_VENV/bin:"*) ;; *) export PATH=$MEDIA_VENV/bin:$PATH ;; esac
