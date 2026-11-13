# Video pipeline

All local, all open source. Draft quality first (720p, generic voice).

1. **Narration per segment.** Split the script's `**Narration:**` blocks into
   segments. Synthesize each with Kokoro (`pip install kokoro soundfile`, needs
   `espeak-ng`; Apache-2.0; small enough for CPU, fast on any GPU), one generic
   voice for all videos. Save `media/renders/<id>/audio/sNN.wav` and write
   `timings.json` with each segment's duration.
2. **Scenes.** Manim Community Edition, one scene class per video in
   `media/scenes/<id>.py`, one `construct` section per segment. Each section uses
   `Timed.seg(self, T, "sN")`, which reads the segment's duration and word
   timestamps from `timings.json`. `t.at("phrase")` waits until the voice starts
   that phrase, so each element appears as it is named (VIDEOS.md, "Reveal on the
   word"). Timed measures Manim's real clock and rounds waits to whole frames, so
   segments don't drift from the narration. For a human voiceover, produce the
   `words` list by forced alignment of the recording (e.g. a Whisper model with
   word timestamps) and keep the same timings.json format. Real data comes
   from cuPhoton CPU runs on the sample pair, saved as `.npz` by a small
   `media/scenes/data_<id>.py` script, so the video and the course use the same
   numbers.
3. **Assemble.** ffmpeg: concatenate segment audio, mux with the render, burn no
   subtitles; write `<id>.srt` from the segment texts and timings.
4. **Check.** Watch every draft at 2× for sync, legibility on a laptop screen,
   and anything that contradicts the docs.

Voice cloning: if wanted later, record 30 s of clean speech; an open
zero-shot cloning model (e.g. Chatterbox) can then replace step 1. Keep the
generic voice as the default until the scripts settle, so re-recording costs nothing.
Music: none in drafts.

## Setup used for the drafts (user space, no sudo)

    pipeline/setup.sh                      # venv at $MEDIA_VENV (uv, python 3.12, pinned manim/kokoro)
    pipeline/data.sh v1                    # data_v1.py in the cuPhoton env ($CUPHOTON_DIR) -> $VIDEO_DATA
    pipeline/make.sh v1-why-not-subtract   # narrate.py + render.sh -> media/videos/
    # paths and quality: pipeline/env.sh; usage: media/README.md

Scene fonts: Liberation Sans/Mono (DejaVu not installed here). Manim -qm is 720p30.
`pipeline/narrate.py` pads each segment by 0.6 s; scenes consume it via `Timed.rest()`.
