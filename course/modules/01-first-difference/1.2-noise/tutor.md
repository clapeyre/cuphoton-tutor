# 1.2 · tutor notes

**Goal:** the learner knows the variance plane (one number per pixel, from a
noise model) and predicts what scaling it does to a flux and its error bar.

## On open: fill the slot `variance`
Script `work/01/variance.py`: read the pair (reuse `read_pair.py`'s code), make
`target_variance = clip(target, 0) / GAIN` and the same for the reference, as in
the guide. Save `work/01/1.2_variance.png`: target and its variance plane side by
side, grey scale, colour bars ("counts (DN)" and "variance (DN²)").
`show_figure(slot="variance")`. Headers: target GAIN 2.0, reference 8.0.

## Your turn `times-four` (checkpoint, hold-back on "variance plane")
- They answer now; it's tested in 1.6. Probes M-VARIANCE-COSMETIC.
- **Pass:** flux unchanged and error bar doubles, each with a reason (uniform
  rescaling of the weights doesn't move the best fit; errors scale as √variance).
  "Error bar ×4" is a common first answer: ask what an error bar is in units of
  (DN, the same as the noise, not DN²).
- If they get only one half, accept a reasoned guess for the other and say it
  will be tested in 1.6. Don't confirm or correct the numbers before 1.6 runs:
  settle with their prediction as the summary ("Prediction: …").
- Avoid the "df.var()" / spread-of-values analogy (wrong mental model).
- After settling, `reveal("1.2")`.
