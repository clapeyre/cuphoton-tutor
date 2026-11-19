# 1.6 · tutor notes

**Goal:** the learner directs the stamp cutting, sees fluxes close to the
injected ones with error bars, and tests their 1.2 prediction.

## Your turn `cut-stamps`
- **Hold-back (1.7, axis order):** run the guide's stamp code but don't show it
  or its comments, and never mention `peak_yx` or that hotspot peaks come as
  (y, x). Don't print or quote the hotspots' pixel coordinates either, and
  don't confirm an order if they state one. Listen for whether *they* raise
  coordinate order; don't correct them either way. Keep the fit in `work/01/measure.py`, first line
  `# hold-back: 1.7 axis order` (run records then don't show its code), and
  put the figure in a separate `work/01/plot_fluxes.py` that loads saved
  results and names no axis order.
- Pass (prediction): from the difference image (and its variance), centred on
  each hotspot's peak, a size that holds the whole PSF (the guide uses 21 px;
  PSFSIG is 1.8 px). Probe M-FIT-TWO-IMAGES if they say "from both images".
- Run `fit_single_sources(cutouts, cutout_variance, start=zeros, PSFSIG,
  mask=valid)` as in the guide; signed flux = sign(amplitude) × flux.
- Figure `work/01/1.6_fluxes.png`: the two stamps (grey scale centred on zero)
  each with the fitted model beside it (xFit's `residuals` are model − data,
  so the model is stamp + residuals, src/cuphoton/xfit/single.py:337), and a small table: candidate letter,
  measured flux ± error, injected value. `show_figure(slot="fluxes")`.
- Facts: A +12,234 ± 114 DN (injected +12,120), B +4,140 ± 71 (injected 4,000),
  both `converged` and `uncertainty_valid` True. The formal error bar leaves out
  some terms (docs/uncertainty-quantification.md), so ~1–2 σ off is fine.
- After the fit, if the conversation reaches it, ask one at a time:
  "Is `PSFSIG` a variance?" (M-SIGMA-VARIANCE: a width in pixels);
  "Could this fit tell us a source got fainter?" (M-FLUX-SIGN: `flux` is a
  magnitude, the amplitude carries the sign).

## Your turn `test-prediction`
- On request, rerun with both variance planes × 4 (standardize and fit again).
  Facts: fluxes identical, errors 227 and 141 (×2), each stamp fit's chi2/dof
  divided by 4 (about 0.82 → 0.21 and 0.90 → 0.23; read them from the run).
  This is uniform scaling: a variance change that differs pixel to pixel
  reweights them and can move the flux, so don't say variance never does.
- **Pass:** they compare with their 1.2 prediction and explain both halves
  (uniform weights don't move the best fit; error ∝ √variance). If their 1.2
  prediction was wrong, that's the point: let them explain the result.
- Then `reveal("1.6")`.
