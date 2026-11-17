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
| 11 Reconstruct (xImage) | 6.1 map | **next: component track** |
| 12 X-ray traces (xRay) | 6.1 map | **next: component track** |
| 13 Correlate (xBeam) | 6.1 map | **next: component track, first** |
| 14 Scale out | 6.1 map | out of scope by decision (below) |
| 15 Monitor (xLens) | 5.4 | taught |

## 1. Module 04 changes (built and walked 17 Nov)

3.3 made honest (xDR built by `tools/setup-gpu-env.sh`; the compression
trap), 4.5 (a deeper reference: stacking), 4.6 (teach a classifier: xScan;
the module exit moved here from 4.4). Notes go in `docs/walkthrough-7.md`.

## 2. Component tracks (required before showing the course)

6.1 ("Where next") hasn't been walked yet: it's open-ended and will read
better once the tracks exist, so walk it after them.

One optional module per component, in this order:

1. **xBeam** (guide ch. 13: correlate two sampled signals, radio recordings,
   the VLBI correlator). First because the developer blog (13 Nov) featured
   it, and the course doesn't touch it.
2. **xRay** (ch. 12: time-resolved X-ray detector traces).
3. **xImage** (ch. 11: one sharp image from many frames).

Each follows the course's pattern: a short synthetic run with a known answer
(for xBeam, a known delay), its receipt, the component's own silent-error
trap found by testing, then "your data", and a "Where next" link from 6.1.
Prefer the guide's own examples and data. Video only if a mechanism needs
motion (`media/VIDEOS.md`).

## Decided out of scope

- **Scale-out (guide ch. 14).** Not taught (17 Nov). By the time a learner
  deploys to many GPUs they know the library well enough to work from the
  documentation with their agent, on their own cluster. 6.1's map points to
  the chapter; 3.4's timing habits carry over.
