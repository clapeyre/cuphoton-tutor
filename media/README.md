# Course videos

The app serves `videos/<id>.mp4` and `videos/<id>.srt`, listed in `videos.yaml`.
Everything here regenerates them: `scripts/` (narration + visual notes),
`scenes/` (Manim, one class per video), `pipeline/` (tools). Rules for content
are in `VIDEOS.md`; design notes in `pipeline/README.md`.

## Setup (once)

    media/pipeline/setup.sh        # uv venv, python 3.12, manim + kokoro, Kokoro weights

System needs: `uv`, `ffmpeg`, cairo/pango, Liberation fonts. Locations come from
`pipeline/env.sh` and can be overridden: `MEDIA_VENV` (default
`~/cuphoton-overnight/tools-media/venv`), `HF_HOME` (`.../tools-media/hf`),
`CUPHOTON_DIR` (`~/cuphoton-overnight/cuPhoton`, has its own `.venv`; data was
made at ff4d26018eb4). Intermediates go to `MEDIA_RENDERS` (`media/renders/`,
gitignored except `timings.json`), scene data to `VIDEO_DATA`
(`media/renders/data/`), finals to `VIDEOS_OUT` (`media/videos/`).
`QUALITY=l` renders 480p15 for quick checks; default `m` is 720p30.

## One video, end to end

    media/pipeline/data.sh v1                    # cuPhoton env: sample pair, quickstart, data_v1.py -> v1.npz
    media/pipeline/make.sh v1-why-not-subtract   # narrate + render + assemble -> media/videos/

`make.sh` is `narrate.py <id>` then `render.sh <id>`; run them alone when only
one side changed. To write somewhere else, e.g. a trial render:
`VIDEOS_OUT=/tmp/try MEDIA_RENDERS=/tmp/try/r media/pipeline/make.sh <id>`.

- **Edit the words:** change the `**Narration:**` block of a segment in
  `scripts/<id>.md`, then `make.sh <id>`. New wording moves the word timestamps;
  check the log for `WARNING: cue ...` (a `t.at("phrase")` no longer in the
  text raises `KeyError`) and fix the phrase in the scene.
- **Edit the picture only:** change `scenes/<id>.py`, then `render.sh <id>`
  (reuses the existing audio and `timings.json`).
- **Data changed (new cuPhoton, new sample):** delete `renders/data/` (or the
  stale `vN.npz`) and rerun `data.sh`. v2 needs v1 data: `data.sh v1 v2`.

## Adding vN

1. `scripts/vN-slug.md`: segments as `## sK — Title`, each with `**Visual:**`
   and `**Narration:**`. Add a row to `VIDEOS.md`.
2. If the video shows real outputs: `scenes/data_vN.py` that runs from
   `$VIDEO_DATA` (cwd has `sample/`), takes the output dir as argv[1], and writes
   `vN.npz`. It runs in the cuPhoton env through `data.sh vN`.
3. `scenes/vN_slug.py` with `class VN(Scene)`, `from common import *`, one
   `self.next_section("sK"); t = Timed.seg(self, T, "sK")` per segment, reveals
   with `t.at("phrase")`, ending in `t.rest()`. Load data with `np.load(DATA / "vN.npz")`.
4. `data.sh vN` (if any), then `make.sh vN-slug`. Watch it, then add the entry
   (title, duration, chapters in seconds) to `videos.yaml`.
