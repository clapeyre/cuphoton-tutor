# 4.4 · tutor notes

**Goal:** the learner designs and reads an injection-recovery test: detection
limit, flux bias, and whether error bars are honest. Module 04's exit (O5).

## Your turn `design`
- Collect their design: what (point sources with the PSF), flux levels (a
  range spanning detected to undetected), how many per level, where (good
  pixels, on sky and on the galaxy, away from the supernova and from each
  other), what to measure (recovered fraction, measured vs planted flux,
  scatter vs error bars). Discuss what's missing with one question each;
  don't hand them a design.
- Run their design if reasonable. Reference (verified): Gaussian PSF
  σ = 1.57 px (target seeing), 20 sources each at 4000, 2000, 1000, 500, 250
  counts, uniformly placed on usable pixels, ≥ 30 px apart and ≥ 40 px from the
  supernova; add Poisson noise of the fakes (flux/gain) to the image and their
  variance to the variance map; rerun the identical chain; a fake counts as
  found if a hotspot (threshold 5) lies within 3 px; measure all fakes at
  their planted positions with `fit_single_sources`.
- Figure `work/04/4.4_recovery.png`: left, recovered fraction vs planted flux
  (with the magnitude on a second axis using zero point 26.9); right,
  measured/planted flux ratio and the scatter of (measured − planted)/error per
  level. `show_figure(slot="recovery")`.
- Facts (seed 11, this pair, GPU):

  | planted (counts) | ≈ r mag | found | measured/planted | pull scatter |
  |---|---|---|---|---|
  | 4000 | 17.9 | 20/20 | 0.993 | 1.39 |
  | 2000 | 18.6 | 20/20 | 1.010 | 1.16 |
  | 1000 | 19.4 | 6/20 | 0.930 | 1.49 |
  | 500 | 20.2 | 0/20 | 1.115 | 1.76 |
  | 250 | 20.9 | 0/20 | (unreliable) | – |

  Pull scatter should be ≈ 1 if error bars are honest. A different seed moves
  these by a few counts, not the conclusions.
- Settle on the run.

## Your turn `what-it-proves` (checkpoint)
- **Pass:** (a) a detection limit: complete to ~2000 counts (r ≈ 18.6), about
  half-ish near 1000, blind below 500, at threshold 5; (b) bright fluxes are
  unbiased; (c) error bars are too small by ~1.2–1.5×, with any plausible
  reason (correlated noise from resampling is the main one; kernel and PSF
  approximations too); and (d) one limit of the test: it only checks sources
  like the ones planted (point sources, these positions, this pair), not other
  kinds of change or other nights.
- Module exit, after settling: ask them to write the instruction they'd give an
  agent for the next night of this survey, in a few lines (data checks, noise
  model, masks, run, evidence, an injection test with the error-bar check).
  Compare with their 2.6 list in one or two sentences. Then `reveal("4.4")`.
