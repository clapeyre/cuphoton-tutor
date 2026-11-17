# Roadmap

Work that must happen, in order, before the course is shown to anyone
outside the team (decided 17 Nov 2026). Parked ideas stay in `BACKLOG.md`.

## Coverage of the user guide

The guide (https://nvidia.github.io/cuPhoton/main/, `docs/guide/` at the
pinned commit) has 15 chapters. Where the course stands:

| Guide chapter | Course | Depth |
|---|---|---|
| 1–3 Install, first difference, concepts | 00, 01 (the guide's own sample pair) | taught |
| 4 Read FITS images | 3.3 | taught: a real GPU read, the default reader, the compression fallback |
| 5 Align, and stack | 1.3, 3.2, 3.4; stacking 4.5 | taught |
| 6 Subtract | 1.4, 4.2, 4.4 | taught |
| 7 Measure | 1.6, 5.2 | taught |
| 8 Classify (xScan) | 4.6 | taught: train, evaluate, score, test unseen bogus |
| 9 Transient chain | Module 05 | taught |
| 10 Uncertainty | 4.4, 5.3 | taught |
| 11 Reconstruct (xImage) | Module 08 (track) | taught: a known scene, faults validation misses, the M101 nights |
| 12 X-ray traces (xRay) | Module 07 (track) | taught: one trace, a lost mode and uneven steps, the detector on the GPU |
| 13 Correlate (xBeam) | Module 06 (track) | taught: time series, radio jobs, real data (GW150914) |
| 14 Scale out | 9.1 map | out of scope by decision (below) |
| 15 Monitor (xLens) | 5.4 | taught |

## 1. Module 04 changes (built and walked 17 Nov)

3.3 made honest (xDR built by `tools/setup-gpu-env.sh`; the compression
trap), 4.5 (a deeper reference: stacking), 4.6 (teach a classifier: xScan;
the module exit moved here from 4.4). Notes go in `docs/walkthrough-7.md`.

## 2. Component tracks (built 17 Nov; Module 06 walked)

The tracks follow the image modules in stride (walkthrough 8): Module 06
xBeam "Two receivers, one signal" (walked 17 Nov: "good"), Module 07 xRay
"Pump and probe", Module 08 xImage "Many frames, one scene", each with a
video. Each follows the course's pattern: a known answer first, the
receipt, the component's silent-error trap found by testing, then real or
realistic data.

## 3. Walk what's left

- Modules 07 and 08 (`docs/walkthrough-9.md`).
- 9.1 "Where next", now the course's last module: the full map and a
  conversation about the learner's own work. Walk it after 07 and 08.

## Decided out of scope

- **Scale-out (guide ch. 14).** Not taught (17 Nov). By the time a learner
  deploys to many GPUs they know the library well enough to work from the
  documentation with their agent, on their own cluster. 9.1's map points to
  the chapter; 3.4's timing habits carry over.
