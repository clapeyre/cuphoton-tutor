# 1.5 · tutor notes

**Goal:** the learner predicts the hotspots, sees exactly the two injected
changes, and doesn't read z > 5 as a calibrated probability.

## Your turn `how-many` (prediction)
- Accept any reasoned prediction. If they remember 1.1 ("two changes were put
  in"), good: ask what else could pass (kernel mismatch at bright stars, the
  edge).
- On "run it": `work/01/hotspots.py`: `standardize_constant_kernel_residual`
  (target and aligned reference variance, the fitted kernel), then
  `identify_residual_hotspots(z, robust_sigma=1.0, threshold_sigma=5.0,
  max_regions=None)`. Save `work/01/z.npy` and the regions (e.g. JSON) for 1.6.
- Figure `work/01/1.5_hotspots.png`: z in grey scale centred on zero, ±6,
  each hotspot circled and lettered A, B. **Never print `peak_yx`, coordinates
  or "(y, x)" labels** anywhere (hold-back for 1.7, the axis-order bug).
  That includes the code: run records show the scripts behind a figure and
  the earlier runs it drew on. Do the lookup in `work/01/hotspots.py`
  (writing plain positions to a file) and make its first line
  `# hold-back: 1.7 axis order`; the run record then names the file without
  showing its code. Keep the figure script itself free of axis-order names.
  Same in 1.6.
  `show_figure(slot="hotspots")`.
- Now open the answer key: a star was made 3× brighter (difference flux
  +12,120 DN) and a new source of 4,000 DN was added. Ask them which letter is
  which (the brighter one has the higher z: A z≈27, 50 px; B z≈15, 30 px).
- Settle when they've compared prediction and result.

## Your turn `what-five-means`
- Probes M-Z-SIGNIFICANCE. **Pass:** no, or "not exactly", with a reason: z is
  approximate (it leaves out the correlations resampling adds and the
  uncertainty of the fitted kernel and background), so the Gaussian tail
  probability doesn't apply as such. Also fine: "in a million-pixel image,
  one-in-a-million happens".
- Ground it in the guide: "a noise diagnostic rather than calibrated detection
  significance". Then `reveal("1.5")`.
