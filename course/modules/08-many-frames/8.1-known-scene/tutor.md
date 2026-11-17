# 8.1 · tutor notes

**Goal:** the learner predicts and reads an xImage reconstruction of a
known scene, checks it against the planted fluxes rather than against the
evaluation's similarity scores, and reads the receipt: device, whether the
run converged or hit its cap, the loss. Probes M-SHARP-MEANS-RIGHT.

Source: docs/guide/reconstruct.qmd (the whole page; "Evaluate the run":
"Similarity or sharpness alone therefore does not show that a
reconstruction is accurate"). `scene.py`, next to these notes, makes the
guide's bundle, runs it and draws it. Nothing is hidden in it: the learner
may copy it to `work/08/`. Outputs in `work/08/`. GPU environment (it
needs the `ximage` extra: PyTorch, pydantic, Zarr; `tools/setup-gpu-env.sh`
installs it). Module 08 is a track: if this is the learner's first visit
to `work/08/`, create it.

## Setup facts
- The bundle: `images` (batch, y, x, frame) = (1, 64, 64, 3), `variances`
  same shape (0.01² everywhere), `psfs` (psf_y, psf_x, channel, frame) =
  (9, 9, 1, 3). The frame index is the last axis.
- The configuration is the checkout's `examples/ximage/reconstruct-l2.example.yaml`
  with `data.base` and `output` changed (scene.py writes it next to the
  run as `<name>.yaml`; show it in Files). It reconstructs the central
  48 × 48 pixels; with `VALID` padding the frames must hold 4 real pixels
  beyond each edge. The saved image is 56 × 56: the region plus a 4-pixel
  border to crop.
- `run_reconstruction(Path(...))` returns `result.run_dir` and
  `result.summary`, which is also saved as `summary.json`, the receipt
  (backend, device, dtype, version, input, region, saved paths,
  `trace_summary`, timings). Show these lines as an excerpt when you run.

## Your turn `predict-scene` (prediction)
- Collect the prediction: look (sharper than the frames? points?) and
  brightness. Most say "single bright pixels of 30, 50, 20". Accept "I
  can't tell how sharp it gets" with what they'd check.
- Run from `work/08/`:
  ```
  python <course>/modules/08-many-frames/8.1-known-scene/scene.py make bundle
  python <course>/.../scene.py run bundle runs l2
  python <course>/.../scene.py figure bundle runs/l2 8.1_scene.png
  ```
  `show_figure(slot="scene")`. Facts (real run, GPU, about 1 s):
  ```
  issues: []
  backend torch, device cuda (NVIDIA GeForce RTX 4070 Ti SUPER), dtype float64, saved image [1, 56, 56, 1]
  iterations 75 (max_iter 75), loss 2.97, u_score 7.9e-06 (stop_tol 1e-06)
  source at (20, 22): planted 30, peak pixel 25.5, flux in 9 x 9 box minus sky 30.6
  source at (35, 40): planted 50, peak pixel 43.0, flux in 9 x 9 box minus sky 50.6
  source at (44, 18): planted 20, peak pixel 16.7, flux in 9 x 9 box minus sky 20.4
  restoration {'sharpness_sf': 3.75, 'sky_sigma': 0.024, ...}
  synthetic_coadd {'sharpness_sf': 1.048, 'sky_sigma': 0.007, ..., 'psnr_vs_restoration': 33.457, 'ssim_vs_restoration': 0.956}
  ```
- The dark rings: the scene is nonnegative and drops below the sky (0.1)
  around each source; the guide's figure caption describes the same.
- Compare with the prediction; settle on what they see.

## Your turn `how-know` (checkpoint)
- **Pass:** (a) no: the evaluation compares with the median of the same
  frames, which shares their noise (guide), so similarity and sharpness
  don't establish accuracy; (b) the known scene does: each source's total
  light matches the planted value within 2%; (c) the receipt: it ran on
  cuda, and it stopped at the cap (75 of 75, `u_score` 7.9e-6 above
  `stop_tol` 1e-6), so it hadn't converged; the loss, 2.97, is the
  measure of fit. Two of three to start; ask about the third.
- If they ask to run longer: `scene.py run bundle runs l2-long 500`.
  Facts: stopped by itself at 133 iterations, loss 1.54, `u_score` 1.0e-6;
  peaks 27.1, 45.6, 17.8; totals 30.4, 50.7, 20.3. A tenth of a second.
- Why peaks aren't 30/50/20 even then: the scene approaches single pixels
  slowly; the totals are right well before the peaks are. Why the loss
  isn't 1 even converged: don't speculate past "the scene isn't a perfect
  fit yet"; the guide doesn't give an expected value.
- Settle, then `reveal("8.1")`.

## Video `v9-many-frames` (opens the module)
Three frames with their own PSFs, the median (less noise, same blur), and
xImage working backwards: a guess blurred by each frame's PSF and compared
with that frame, adjusted step by step while the loss falls (real snapshots
after 1, 3, 10, 30, 75 steps). It uses its own scene (a close pair and a
third source), not 8.1's, and shows no numbers: `predict-scene` still
stands. It does show the dark rings around sharpened sources; if a learner
predicts them from the video, credit it.
