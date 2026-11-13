# Renders manifest

Binaries (mp4/wav, audio/, manim/, data/) are not committed (.gitignore); only
timings.json is kept per video. Regenerate with (see media/README.md):

    pipeline/data.sh v0 v1 v2          # real data, cuPhoton env
    pipeline/make.sh <id>              # narrate + 720p30 render + mux -> media/videos/<id>.mp4, .srt

| id | status | length | notes |
| --- | --- | --- | --- |
| v1-why-not-subtract | draft rendered 720p30, cued on the word | 1:34.3 | real xRep/xPois data |
| v2-it-ran | draft rendered 720p30, cued on the word | 1:20.9 | real quickstart summary.json, xFit flags, xPois z |
| v0-intro, v3-kernel, v4-where-data-lives | script only | n/a | not narrated or rendered |
