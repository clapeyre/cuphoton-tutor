# 4.4 · tutor notes

**Goal:** the learner designs and reads an injection-recovery test: detection
limit, flux bias, and whether error bars are honest. 4.5 and 4.6 reuse
the test.

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

- **Explaining the too-small error bars.** Walkthrough 5: the learner saw
  the variance map but "couldn't explain back the logical sequence". Don't
  lead with resampling vocabulary. Go one step per message, each checked
  against the pixels, and offer the figure early:
  1. Each pixel's variance in the map is right: on blank sky,
     pixel/√variance scatters by 0.9 (1.07 on the reference), close to 1.
  2. A flux is not one pixel: it's a weighted sum over the source's pixels
     (a 5×5 to 9×9 patch here).
  3. The error bar on a sum adds the pixels' variances. That is only right
     if each pixel's noise is independent of its neighbours'.
  4. Here it isn't. The survey resampled each exposure onto the sky grid,
     so each output pixel is a blend of a few input pixels, and neighbours
     share some of the same input noise. Measured on blank sky: correlation
     0.17 with the pixel to the side, 0.22 above and below, about 0 two
     pixels away.
  5. Shared noise doesn't average out in a sum. Blank-sky boxes scatter
     more than the map predicts: 1.08× (2×2), 1.29× (5×5), 1.60× (9×9),
     1.74× (11×11). That is the 1.2–1.5× (1.3–2 in some runs) seen in the
     injection pulls.
  The figure: `correlated_noise.py`, next to these notes. Copy it to
  `work/04/` and run it with the GPU environment's python, as
  `python correlated_noise.py data 4.4_correlated.png` from `work/04/`
  (only numpy, scipy and astropy; it prints the numbers above), then `show_figure`
  in the turn. Left panel: the correlation with each neighbour. Right panel:
  real/predicted scatter against box size, with 1 as the line for independent
  noise. Show the script on request.
- After the turn settles, point to the video that shows this in 1.5 minutes,
  with xRep resampling pure noise: it opens [5.3](#/5.3) ("Why the sum
  wobbles"). Not before: it gives the answer away.
- **What would have to be different** (if they ask, or as the last step
  once the cause is clear): (a) measure the factor on this data, as the box
  test or the injection pulls do, and scale the error bars by it (the common
  survey practice); (b) carry the correlation into the noise model, as a
  covariance or a per-scale correction, which a one-number-per-pixel map
  can't hold; (c) work on unresampled exposures, which needs alignment
  ([1.3](#/1.3)) back in the chain. It's not "smooth the variance map":
  the map's values are fine; what's missing is how pixels relate.
- Settle, then `reveal("4.4")`.
