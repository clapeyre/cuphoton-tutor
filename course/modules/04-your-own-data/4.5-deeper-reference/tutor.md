# 4.5 · tutor notes

**Goal:** the learner predicts what a deeper reference buys, then measures it
with the 4.4 injection test and finds the prediction mostly wrong: no depth,
some area, and the new area brings bogus. Probes M-STACK-DEPTH and, again,
M-VARIANCE-COSMETIC.

Source: docs/guide/align.qmd ("Stack several images on one grid"), the
pinned checkout. Data: `work/04/data/reference-b*.fits`, `reference-c*.fits`
(the course's `data/`, copied with the rest in 4.1; copy them if missing).

## The nights (facts)
| file | date | seeing (FWHM, px) | usable alone |
|---|---|---|---|
| reference | 2011-04-22 10:33 | 3.43 | 77% |
| reference-b | 2011-04-22 10:48 | 3.84 | 77% |
| reference-c | 2011-05-11 | 4.65 | 82% |
| target | 2012-04-12 | 3.59 | |

Seeing is in the headers as `CHIP.SEEING`. The two 22 April frames have the
same chip gaps (same pointing); 11 May's gaps run differently. PS1 lists two
more warps that night; they hold no data at this position. All four images
are on the same PS1 sky-cell grid, so xRep's resampling here is an identity:
`max |resampled − original|` is below 3e-6. Say so if they ask what xRep
did; on their own survey, nights won't share a grid.

## Your turn `recipe` (prediction)
- Collect their recipe and prediction. Don't correct either. If the recipe
  leaves out what happens where a night has no data, or the variance, ask
  that one thing.
- Typical prediction: √3 less reference noise, so fakes about 1.3–1.7×
  fainter come back. Write their number down; it's the checkpoint's anchor.
- Run `stack_compare.py`, next to these notes. Copy it to `work/04/` and run
  `python stack_compare.py 4.5_stack.png single weighted mean samevar`
  from `work/04/` with the GPU environment (13 s; env `DATA` if the data
  isn't in `work/04/data`). Always all four: the closing quotes the plain
  mean and samevar rows. This script builds its own chain, so its `single`
  row won't match the learner's 4.2 counts exactly (10–19 hotspots,
  depending on mask and basis choices); if they compare, say so and compare
  references within this one table. Include their recipe if it matches a config:
  weighted = inverse-variance weighted mean over each pixel's usable
  nights, variance 1/Σ(1/var); mean = plain mean (a pixel missing in any
  night is lost); samevar = weighted but keeping the single night's variance
  map; two = only the 22 April pair. Something else: write it, using the
  script's `combine` as the base, and show the code.
- `show_figure(slot="stack")`, with the printed table in a code block.
- Facts (3 seeds × 25 fakes per level, same positions for every reference):

  | reference | usable | kernel sum | χ²/dof | hotspots | ref's share of diff variance | found at 1,000 | median err at 1,000 |
  |---|---|---|---|---|---|---|---|
  | single | 70% | 0.972 | 1.13 | 14 | 0.05 | 30/75 | 81 |
  | weighted (3) | 86% | 0.877 | 1.22 | 23 | 0.03 | 30/75 | 81 |
  | mean (3) | 57% | 0.962 | 1.11 | 9 | 0.03 | 24/75 | 82 |
  | samevar | 74% | 0.876 | 1.23 | 11 | 0.10 | 22/75 | 83 |

  At 2,000 counts: 75/75 for all but mean (58/75: fakes in the lost area).
  At 700: 2–3/75 for all. Weighted: 11 hotspots outside the single
  night's area, at four places, (390, 566), (397, 140), (90, 697),
  (124, 223), each covered only by reference-c; positive and negative
  residues on stars.
- Settle on the run.

## Your turn `what-it-bought` (checkpoint)
- **Pass:** (a) depth: essentially none, against their prediction; (b) why:
  the reference is a small part of the difference's noise (5%) because the
  kernel blurs it; the target's noise dominates; (c) what it bought: area,
  70% → 86%, because the gaps differ; (d) what it cost: the new area is
  covered only by the blurriest night, worse than the target, and its
  hotspots are mismatch residues. Two of the four with a reason is enough to
  start; ask about the rest one at a time.
- **Explaining (b)** if stuck, one step per message: the difference is
  target − kernel ⊛ reference. Its variance is the target's variance plus the
  reference's variance blurred by the kernel squared. The kernel spreads each
  reference pixel over many, and spread noise averages down: the sum of the
  kernel's squared values is 0.06, so the reference's variance (152 per
  pixel) arrives as about 9.5, against the target's 171. Cutting 152 to 49
  (the stack) cuts 9.5 to about 5: 2.5% of the total.
- **When stacking the reference helps** (walkthrough 5, second pass: the
  learner found the lesson enlightening but unsatisfying, "something we spend
  a long time showing doesn't work". Close on this rule, with numbers, so the
  takeaway is when to stack, not that stacking failed). Stacking N nights
  divides the reference's variance, so its share s of the difference's
  variance becomes s/N: the noise scales by √(1 − s + s/N). Here s = 0.05:
  three exposures gain at most 1.7%. With s = 0.5 (a reference no sharper than
  the target and about as deep): three exposures, 18% less noise, about 0.22
  mag deeper; ten, 26% and 0.32 mag. The share is the number to measure
  first; the script prints it. Also: xRep did its part right (identity on
  this grid, variance and mask carried); what failed was the prediction.
  Otherwise: when it is the noisier image (a
  short reference, a deep or stacked target); when the reference night was
  poor; or for area. And the recipe: select nights by seeing (never blurrier
  than the target), scale to one flux scale (the zero points differ by up to
  0.1 mag here: `FPA.ZP` 24.56, 24.60, 24.66), weight by inverse variance,
  carry the variance, and check the PSF wherever coverage changes. Surveys
  often blur every night to a common PSF before stacking.
- If the learner chose the plain mean or kept the single variance: those were
  silent. Ask what the run would have said (nothing; it ran) and what showed
  it (the usable fraction and the injection test). Links to 4.1's
  M-VARIANCE-COSMETIC: the variance map is part of the data.
- Settle, then `reveal("4.5")`.
