# 7.2 · tutor notes

**Goal:** the learner predicts that the sweep finds every mode, sees a
2 THz mode vanish without a warning, names the residual against the noise
as the check, and judges two more scans, one of them broken by uneven
delay steps. Probes M-ORDER-FINDS-ALL and M-EVEN-STEPS.

Source: docs/guide/xray-traces.qmd ("Choose the model order": "It assumes
finite samples at uniformly increasing delays; check that condition";
Troubleshooting: "A fast mode is missing from the fit"),
docs/xray/LINEAR-PREDICTION-VALIDATION.md. `scans.py`, next to these notes,
writes the three scans and fits them. **Run it in place, from the course
folder, with outputs in `work/07/`; don't copy it: the answer is in it.**

## Setup (when you prepare the lesson)
From `work/07/`: `python <course>/modules/07-pump-and-probe/7.2-missing-mode/scans.py make scans`
writes `scans/scan-a`, `scan-b`, `scan-c`, each an `on.h5`/`off.h5` pair
like 7.1's (32 × 32, Poisson counts, `i0` wobble).

The truth (don't tell): every scan is the same crystal, 7.1's two modes
plus a third at 2.0 THz, change 0.02 (as strong as the second), decay
0.1 per ps. scan-a: 0.1 ps steps, 97 frames. scan-b: 0.05 ps steps to
2 ps, then 0.13 ps, to 9.15 ps (97 frames). scan-c: 0.05 ps steps to
9.55 ps (193 frames).

## Your turn `third-mode` (prediction)
- Collect the prediction: most say three modes at order 6 or 7. Accept it.
- Run `... scans.py fit 7.2_scan-a.png scans/scan-a`, then
  `show_figure(slot="scan-a")`. Facts (real run):
  ```
  scan-a: 96 samples, delay 0.00 to 9.50 ps
  model order sweep (RMS residual):  1: 1.1e-02  2: 1.1e-02  3: 5.1e-03  4: 4.8e-03  5: 4.8e-03  6: 4.8e-03  7-12: 4.7e-03
  chosen order: 5
    mode: 0.319 THz, decay 0.152 per ps, amplitude 0.0207
    mode: 0.706 THz, decay 0.079 per ps, amplitude 0.0098
    mode: 0.000 THz, decay 0.005 per ps, amplitude 0.0114
  residual RMS 4.8e-03
  ```
  The 0.000 THz entry is the constant step, fitted as a mode that doesn't
  oscillate.
- Noise-free, the same thing happens: a clean trace with these three modes
  at 0.1 ps steps loses the 2 THz mode at every order from 4 to 30
  (residual 4.8e-3 at all of them; checked 17 Nov). It's the guide's
  troubleshooting case, not noise. At 0.05 ps steps, order 8 recovers it
  exactly. 2.0 THz is 0.4 of the Nyquist frequency at 0.1 ps (5 THz):
  well inside what the scan can represent. Why linear prediction drops
  it: it keeps only part of the polynomial's roots, prioritizing large
  real parts, then filters by decay (guide). Don't go deeper unless asked.
- Let the mismatch stand. Ask what in the output, other than knowing the
  answer, looks wrong; settle on their reading.

## Your turn `two-more` (checkpoint)
- First, their answer for scan a: the residual, 4.8e-3, is 25 times 7.1's
  noise floor (same counts, same tile, same steps, so the same noise is
  expected), it has structure (stripes: a 2 THz wave sampled every 0.1 ps
  repeats every 5 samples), and its spectrum peaks at 2.0 THz.
- If they ask about the scans before fitting (step size, number of frames,
  delays), answer from the files: `h5py`, `np.diff(f["scan_var"][:])`.
  scan-b: steps 0.05 ps up to 2.0 ps, then 0.13 ps. scan-c: 0.05 ps
  throughout, 193 frames. Show the code and the output. Credit asking.
- Run `... scans.py fit 7.2_scans.png scans/scan-b scans/scan-c`,
  `show_figure(slot="scans")`. Facts:
  ```
  scan-b: 96 samples, delay 0.00 to 9.15 ps
  model order sweep (RMS residual):  1: 1.1e-02  2: 9.9e-03  3: 1.0e-02  4: 8.2e-03  5: 7.0e-03  6: 8.0e-03 ... 12: 7.6e-03
  chosen order: 5
    mode: 0.454 THz, decay 0.175 per ps, amplitude 0.0138
    mode: 2.056 THz, decay 0.075 per ps, amplitude 0.0078
    mode: 0.890 THz, decay 0.020 per ps, amplitude 0.0088
  residual RMS 7.0e-03
  scan-c: 192 samples, delay 0.00 to 9.55 ps
  model order sweep (RMS residual):  ... 5: 4.8e-03  6: 1.1e-03  7: 1.9e-04  8-12: 1.9e-04
  chosen order: 7
    mode: 0.318 THz, decay 0.148 per ps, amplitude 0.0199
    mode: 2.000 THz, decay 0.104 per ps, amplitude 0.0102
    mode: 0.716 THz, decay 0.080 per ps, amplitude 0.0100
    mode: 0.000 THz, decay 0.000 per ps, amplitude 0.0104
  residual RMS 1.9e-04
  ```
  scan-b's residual spectrum is meaningless (it assumes even steps; the
  axis label says so). scan-b's sweep isn't even monotonic (order 3 worse
  than 2, 6 worse than 5).
- **Pass:** (a) scan a's warning sign: residual far above the noise, with
  structure; (b) trust scan c: residual at the noise floor and three
  modes, two matching scan a's; (c) don't trust scan b: residual high,
  modes disagree with both other scans, and the reason, uneven delay steps,
  once they've asked or been shown the delays. Two of the three to start;
  ask about the third.
- If they trust scan b because it found a mode near 2 THz: ask whether its
  other two modes agree with scans a and c.
- Fixes for an uneven scan, if asked: fit only an evenly stepped stretch
  (here 0 to 2 ps is too short; the fit needs 16 samples and a mode's
  period), or measure with even steps. Don't interpolate onto an even grid
  without testing that with planted modes first.
- `cuphoton xray lpv` (linear-prediction-validate) checks the fit against
  synthetic modes and the Cramér–Rao bound, but only for its built-in
  fixture (two modes, 96 samples): it doesn't take your step size or
  frequencies. Planting your own modes at your cadence, as scans.py does,
  is the check the guide's troubleshooting means.
- Settle, then `reveal("7.2")`.
