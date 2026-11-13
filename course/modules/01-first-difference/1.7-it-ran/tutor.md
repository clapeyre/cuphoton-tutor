# 1.7 · tutor notes

**Goal:** the learner catches a silent bug from evidence alone: swapped axes in
`swapped_axes.py` (next to these notes; copy it to `work/01/` and run it from
`work/01/`, where `sample/` is). Never show the learner the script, its
comments or this file before the turn is settled.

## Your turn `swapped` (checkpoint, the module's last)
- Run it and report **only its printed output**. This overrides the cuphoton
  skill's "After running" list. Don't offer a list of possible checks.
- Give comparisons (cutout plots, fluxes against the injected values, fitted
  positions against stamp centres, z at the stamp centre) only when asked. If
  they ask for fit status, show it: it looks healthy, which is part of the
  lesson.
- **Pass:** all three of (a) a symptom from the evidence (stamps, fluxes or
  positions; fit status doesn't reveal it), (b) the cause (stamps cut at
  transposed / swapped coordinates), (c) how they'd have caught it (plot the
  cutouts, check the peak is centred, check fitted positions, compare with the
  hotspot's own peak or the injection). "Check `converged`" alone is partial.
- Hint ladder, never pointing at the line: (a) "What would you expect at the
  centre of each cutout?" (b) the axis-order table in docs/guide/concepts.qmd;
  (c) an unrelated (y, x)/(x, y) mix-up, e.g. indexing a NumPy image with an
  Astropy pixel position; (d) reveal, then a variant: they say how to cut a
  stamp at an Astropy (x, y) = (40, 25) position from a NumPy image.

## Instructor facts (real run, pinned commit, CPU)
- Bug: hotspot peaks are `(y, x)`; the script passes them to `window_stamps`
  unchanged, which takes `(x, y)`. Stamps are cut at the transposed position.
- Prints "2 candidates", fluxes −133 ± 52 DN at [21, 72] and +89 ± 50 at
  [167, 80]. Correct: +12,234 ± 114 and +4,140 ± 71 (1.6).
- `converged` and `uncertainty_valid` True for both; stamp fit chi2/dof 1.11
  and 1.02. The transposed centres are blank sky (z −0.65, +0.05); the cutouts
  are pure noise (std ≈ 8 DN, max +21 / min −25, against true peaks 605 and
  190). Fitted position wanders +5.4 px in y for the first. The hotspots had
  z 27 and 15, but the fitted fluxes are only ~2.5 and ~1.8 σ.
- After the pass, show the script and the line, and add the rule in words:
  arrays index `[y, x]`, and each call says which order it takes.

## Module exit
After settling, ask once (a new line in your reply, not a new turn) for the
module question in two sentences: "Does cuPhoton find the two changes, and how
would you know its answer is right?" Then `reveal("1.7")`.
