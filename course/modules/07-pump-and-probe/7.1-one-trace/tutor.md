# 7.1 · tutor notes

**Goal:** the learner predicts what xRay's fit reports for a trace with
known modes, finds the amplitudes halved by the reference shift, and reads
the model-order sweep against the noise. Sets up M-ORDER-FINDS-ALL for 7.2.

Source: docs/guide/xray-traces.qmd ("Make a sample pair", "Extract a
trace", "Choose the model order", "Fit the trace with linear prediction"),
in the pinned checkout. `trace.py`, next to these notes, makes the guide's
sample pair and fits it. The learner may copy it to `work/07/` (nothing is
hidden in it); outputs go in `work/07/`. GPU environment (this lesson runs
on the CPU; xRay's trace steps need only NumPy and h5py). Module 07 is a
track: if this is the learner's first visit to `work/07/`, create it.

## Setup facts
- `cuphoton xray doctor` lists what xRay found (NumPy, h5py, CuPy; Bokeh
  missing, which only the interactive viewers need). Run it first and show
  it: the guide does, for new machines.
- The pair: `cropped-cube` layout. `imgs` (frame, y, x), `scan_var` (the
  delays), `i0` (the monitor xRay divides by), `i0_ipm3`, `bin_count`,
  `ROI` (required by the layout check). `probe_hdf5_pair` reports layout
  and normalization.
- `load_hdf5_pair_roi_trace(..., roi_x=0, roi_y=0, roi_width=16,
  roi_height=16)` drops the first frame, sums the ROI per frame, divides by
  `i0`, forms `(on + S) / (off + S) − 1` with S the mean laser-off sum.
  `model_order_sweep(delay, trace, range(1, 10))`, then
  `linear_prediction_numpy(delay, trace, order)`. Show these lines as an
  excerpt when you run.
- Frequencies come out as angular frequency (radians per ps); divide by 2π
  for THz (the script does).

## Your turn `predict-fit` (prediction)
- Collect the prediction for frequency, decay and amplitude. Most will say
  "the planted values" for all three. If they can't predict the amplitude,
  accept "I'd check how the trace is formed" and come back to it.
- Run from `work/07/`:
  `python <course>/modules/07-pump-and-probe/7.1-one-trace/trace.py make sample`
  then `... trace.py fit sample 7.1_fit.png`, and `show_figure(slot="fit")`.
- Facts (real run, under a second):
  ```
  on.h5: layout cropped-cube, normalized by i0
  trace: 96 samples, delay 0.0 to 9.5 ps, reference_shift=True
  model order sweep (RMS residual):  1: 1.00e-02  2: 1.00e-02  3: 1.75e-03  4: 1.91e-04  5-9: 1.91e-04
  chosen order: 4
    mode: 0.318 THz, decay 0.148 per ps, amplitude 0.0199
    mode: 0.717 THz, decay 0.079 per ps, amplitude 0.0099
  residual RMS 1.91e-04
  ```
  With `--no-shift`: amplitudes 0.0399 and 0.0198, residual floor 3.8e-4,
  same frequencies and decays.
- Planted: 2.0 rad/ps = 0.318 THz, 4.5 rad/ps = 0.716 THz.
- If their amplitude prediction was the planted 4% and 2%: let the run
  show 2% and 1%, and ask what in the trace's formula could halve a change
  (hint ladder: (a) "what does the trace divide by?" (b) the guide's
  sentence: "With this reference shift, the trace is about half the
  relative change"). Then run `--no-shift` to confirm. Why half:
  on ≈ off·(1 + c), S ≈ off, so (on + S)/(off + S) − 1 ≈ c/2.
- **Pass:** frequencies and decays as planted; amplitudes half, with the
  reason (the reference shift). Settle.

## Your turn `order` (checkpoint)
- **Pass:** (a) two oscillating modes need four components, two each (the
  guide); (b) order 3 can hold only one mode (its residual, 1.75e-3, is
  nine times the floor: the second mode is still in it); (c) above 4 the
  residual stays at 1.9e-4 because what's left is the noise, which no mode
  fits. Two of the three to start; ask about the third.
- If they ask where the noise comes from: Poisson counts, 50,000 per pixel
  per frame over 256 pixels, plus the monitor's 3% pulse-to-pulse wobble,
  which the `i0` division removes. If they ask how they'd know their own
  noise level: from the trace before time zero, or from two laser-off
  scans compared with each other.
- If they ask about the 1% constant: the fit carries a constant term
  besides the modes; in this run it isn't listed as a mode.
- Settle, then `reveal("7.1")`.
