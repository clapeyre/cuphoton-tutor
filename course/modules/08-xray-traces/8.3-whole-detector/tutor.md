# 8.3 · tutor notes

**Goal:** the learner runs xRay's detector-wide fit on the GPU, says what
they'd check before it runs, reads the manifest and `fit_status`, and finds
that dead rows came back "fitted" with their neighbours' frequency. Fixes
it with `--exclude-y` and checks the rerun. Probes M-STATUS-MEANS-DATA.

Source: docs/guide/xray-traces.qmd ("Fit every detector row", "Read the
outputs", Options; "These steps change the trace's support and amplitude").
`detector.py`, next to these notes, writes the detector and reads the run.
**Run it in place, from the course folder, with outputs in `work/08/`;
don't copy it: the answer is in it.** GPU environment (the default
detector backend needs CuPy and a GPU).

## Keep it on the dispersion curve
The first walk of this lesson lost the learner: they had to ask what the
tiles were, a home-made residual plot came back with a wrong axis, and
"what would you change?" came before they knew the goal ("What curve?").
So:
- The page now explains the tiles and has a figure of them (`tiles.png`,
  made by `tiles_figure.py`). Point to it; don't redraw it.
- Name the goal in every question: **the dispersion curve**, the middle
  panel of the rows figure, one point per row. The question is whether
  each point is something its row measured.
- One question per message. Ask "what would you change?" only after they
  have said that some points weren't measured, and say what the change is
  for: a curve that shows which points were measured.
- Use the script's figures (`look`, `residuals`); don't write plotting code
  here unless the learner asks for something they don't cover.
- If they ask for the residuals (a good habit from 8.2): `python
  <course>/.../detector.py residuals run1 8.3_residuals.png`. Facts: median
  residual std 7.2e-3, max 1.1e-2; around the dead rows it is *lower*
  (5.4–5.6e-3), and the relative residual a little higher (0.27 against a
  median of 0.16), because the borrowed trace is smaller. The residual
  doesn't catch this fault: the borrowed traces fit fine. Only what the
  rows recorded does. Say so; it's the contrast with 8.2.

## Setup (when you prepare the lesson)
From `work/08/`: `python <course>/modules/08-xray-traces/8.3-whole-detector/detector.py make detector`
writes `detector/on.h5` and `off.h5` (25 MB; 97 frames of 256 rows × 128
columns, 0.1 ps steps, about 2,000 counts per pixel).

The truth (don't tell): one mode whose frequency follows the row,
0.25 THz at the edges rising to 1.0 THz at row 128 (`0.25 + 0.75 sin(π y
/ 255)`), change 0.03, decay 0.12 per ps, plus a 0.8% step. Rows 120–123
are dead: 0 counts in every frame, laser on and off.

## Your turn `first-look` (prediction)
- Collect their list. Good answers: the manifest (backend, device, fits,
  failures, the order used), `fit_status`, a picture of the fitted
  frequencies across the detector, whether the curve is smooth, the raw
  counts. Don't add to it yet.
- Run, showing commands and outputs (excerpts):
  ```
  cuphoton xray detector-mask --roi-lower 0 0 --roi-dim 128 256
  cuphoton xray detector-artifacts --h5dir detector --fon on.h5 --foff off.h5 --output-dir run1 \
    --roi-lower 0 0 --roi-dim 128 256 --zero-offset-index 0 --components 4 \
    --fit-diagnostics summary --artifact-layout tile-rows
  python <course>/.../detector.py look run1 detector 8.3_rows.png
  ```
  `--roi-dim` is width then height (x, y). `--components 4`: one mode,
  set by the lesson (no sweep runs on this detector; 8.2's sweep is on its
  own scans), and the guide says to set the order a sweep chose; the default is 30
  (see below). `detector-mask`: 128 tiles, 2,048 row fits, 0 skipped.
- `show_figure(slot="rows")`. Facts (real run, RTX 4070 Ti SUPER):
  ```
  manifest: backend cupy, device cuda, components 4, exclude_y , raw_fits 2048, failures 0, skipped_fits 0, elapsed_s 15.7
  fit_status: fitted 32768
  strongest oscillating mode vs the planted frequency, fitted rows: median |error| 0.002 THz
  row  laser-off counts  status  frequency (THz)  amplitude
  116              2007   fitted            0.993     0.1064
  117              2007   fitted            0.994     0.0910
  118              2007   fitted            0.994     0.0760
  119              2006   fitted            0.994     0.0620
  120                 0   fitted            0.996     0.0458
  121                 0   fitted            0.999     0.0474
  122                 0   fitted            1.003     0.0427
  123                 0   fitted            1.003     0.0440
  124              2007   fitted            1.003     0.0579
  125              2008   fitted            1.004     0.0706
  126              2007   fitted            1.002     0.0861
  ```
  Typical amplitude 0.10–0.11. The detector's amplitudes aren't on 8.1's
  scale: integration and smoothing change the trace's amplitude (guide).
  The edge rows dip too (row 0 0.062, 1 0.074, 254 0.083, 255 0.062): the
  ±3-row sum runs off the detector, so row 0 sums 4 rows instead of 7, the
  same effect as next to the dead band. Frequencies there are right. If the
  learner points it out, they're right: credit it and link it to the band.
- Show a few manifest lines (`backend`, `device`, `components`,
  `fit_status_codes`, `failures`). Settle `first-look` on what they see
  first, in that reply, and stop: the page then opens `every-row` with its
  own question. Don't ask whether every point was measured yourself. Name
  only panels the figure has (counts, frequency, amplitude); the status map
  is in the manifest, not on the page.

## Your turn `every-row` (checkpoint)
- **Pass:** (a) rows 120–123 recorded nothing (left panel) yet have status
  1 and a frequency: not measurements; (b) why: each row's trace sums the
  rows within 3 pixels (`--integrate 3`), so the dead rows borrowed their
  neighbours' signal, and their neighbours' amplitudes dropped because the
  sum includes zeros; (c) the change: `--exclude-y 120:124`, with a
  prediction (status 2 for those rows, skipped fits counted). Two of three
  to start; ask about the third.
- If they don't see it: hint ladder (a) "compare the left panel with the
  middle one"; (b) "what did rows 120–123 record, and what did the fit say
  for them?"
- Run, with `detector-mask ... --exclude-y 120:124` first (8 tiles
  partially excluded, 2,016 active row fits, 32 skipped), then:
  ```
  cuphoton xray detector-artifacts ... --output-dir run2 ... --exclude-y 120:124
  python <course>/.../detector.py look run2 detector 8.3_fixed.png
  ```
  `show_figure(slot="fixed")`. Facts:
  ```
  manifest: ... exclude_y 120:124, raw_fits 2016, failures 0, skipped_fits 32
  fit_status: fitted 32256, skipped 512
  rows 120-123: skipped, frequency 0, amplitude 0
  rows 117-119 and 124-126: unchanged (amplitudes 0.091, 0.076, 0.062, 0.058, 0.071, 0.086)
  ```
  Excluding the rows skips their fits, but rows within 3 of them still
  integrate the zeros: frequencies fine, amplitudes 55–87% of typical. If
  amplitudes matter, treat those rows as suspect too, or exclude them.
- The default order: with no `--components` (30) the same run gives
  "modes per row: 1: 75 rows, 2: 89, 3: 69, 4: 14, 5: 8, 6: 1" against
  "1: 149, 2: 107" at order 4 (counting the constant step as an entry).
  The strongest mode's frequency is unchanged (median error 0.002 THz);
  the extra entries are small fits to noise. Mention it if they didn't set
  the order themselves or ask about the default.
- Speed, if asked (3.4's habits: whole command, said plainly): quote the
  manifest's `elapsed_s` from the learner's own run, not the numbers here,
  which are from the course author's RTX 4070 Ti SUPER (a Tesla T4 takes
  37–61 s for the same run). There, 2,048 row
  fits took 13–17 s per run (several runs; each command is a fresh process
  and reads both files). A 512 × 512 detector, 16,384 row fits, took
  102 s. For comparison, `linear_prediction_numpy` on one 95-sample trace
  takes about 1 ms on this CPU, so 2,048 single-trace fits take about 2 s,
  without the integration and smoothing. On this machine and at these
  sizes, the detector command is not faster than a NumPy loop; what it
  gives is the whole workflow in one command, with a manifest, per-pixel
  status, diagnostics, and the path to many GPUs
  (`detector-artifact-distributed`). The guide makes no speed claim. Don't
  make one either.
- Settle, then `reveal("8.3")`.
