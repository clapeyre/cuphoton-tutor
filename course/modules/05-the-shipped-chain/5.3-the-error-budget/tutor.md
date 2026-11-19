# 5.3 · tutor notes

**Goal:** the learner reads the error budget, tests it with an injection
test, and finds that the bars are right while the values are biased, because
of the shipped kernel-fit settings. Probes M-BUDGET-BIAS (and M-UQVALID from
5.2). Exit of the module's science (O6).

## Video `v5-why-the-sum-wobbles` (opens the lesson)
Recaps 4.4's cause with xRep on pure noise: per-pixel scatter 1.00, neighbour
correlation 0.25, 3×3 sums 1.22× the prediction; on the PS1 target, box sums
0.9 → 1.7× from 1 to 11 px. It ends on "measure the factor on the image": that
is the `corr` term, which the `budget` turn is about.

## Your turn `budget`
- SN row (5.1's `run2`): `psf_flux_err_fit` 183.2, `_corr` 273.6, `_kfit`
  11.9, `_kmatch` 0, `_mis` 0, total 329.5 = √(183² + 274² + 12²).
  `summary.json` `uq.correlation`: `closed_form.psf_flux` 1.65, `measured`
  3.23 (± 0.27), `source: measured`, `positions_used` 776 of 1000 requested,
  `window_px` 17. The factor is on the *variance*: √3.23 = 1.80 on the error
  bar, so corr = 183 × √(3.23 − 1) = 274.
- How it's measured (README "How the error bar is built", guide
  uncertainty.qmd): the chain applies the flux's own PSF weights at ~1000
  empty positions of the difference and compares the scatter with what the
  per-pixel variance predicts: the box test of 4.4 done with the real
  weights. It uses the measured factor where it exceeds the closed form (from
  the resampling/convolution weights) by over two standard errors.
- Compare with 4.4: pull scatter of their own chain 1.2–1.5; box sums 1.29×
  (5×5), 1.60× (9×9). The chain's 1.8 on the error bar is in that range for a
  PSF-weighted sum over a 17-px window.
- kmatch, mis are 0 because left out (`uq.excluded`): kmatch "fewer than 5
  matched stars" (no star matching on a pre-gridded pair, 5.1), mis "no
  misalignment model". Guide: "A term without its inputs is left out; that
  does not establish that its physical contribution is zero."
- **Pass:** corr is most of it, it's the correlated noise of 4.4, measured on
  this image; bonus for noticing the left-out terms aren't proven zero.

## Your turn `test-it`
- **Pass (design):** fakes in the target only, the target's PSF, a few flux
  levels, many per level, away from stars, masks, the SN and each other;
  measure found fraction, measured/planted, and pulls against
  `psf_flux_err`. If spacing isn't raised: ask how far apart, given the chain
  cuts 51-px stamps (verified: with fakes ~28 px apart, 16 of 300 came back
  more than 4 bars off, most of them measured on a neighbouring fake). Don't block on details.
- Run (verified): from `work/05/`,
  `NSEED=10 NPER=10 SPACING=60 python <this dir>/inject_chain.py` (writes
  `inj/`: 10 target images × 30 fakes, 10 each at 8000/4000/2000 counts,
  σ 1.57 px, ≥ 60 px apart, quiet usable pixels, ≥ 40 px from the SN; fake
  shot noise added to image and variance; `inj/selections.json`,
  `inj/truth.json`). Then the launcher with the same `config.yaml` and
  `--set xfit.psf_sigma_px=1.57`, `--selections inj/selections.json
  --output-dir inj/run-shipped` (~1 min). Then
  `python <this dir>/injection_figure.py inj 5.3_injection.png "inj/run-shipped=Shipped kernel settings"`;
  `show_figure(slot="injection")`, with the printed table in a code block.
- Settle on the run.

## Your turn `what-went-wrong` (checkpoint)
- Facts, shipped kernel settings (10 seeds, 300 fakes, all found):

  | planted | measured/planted | pull mean | pull scatter (robust) | fit-only scatter | quoted/fit |
  |---|---|---|---|---|---|
  | 2000 | 0.89 | −1.22 | 0.67 | 1.27 | 1.99 |
  | 4000 | 0.94 | −1.26 | 0.90 | 1.90 | 1.99 |
  | 8000 | 0.96 | −1.20 | 0.83 | 1.66 | 1.99 |

  The bars are the right size (scatter ≲ 1); the values sit ~1.2 bars low:
  a bias. In counts that is a few hundred at every level (about 220, 240 and
  320), so the fraction shrinks as the fakes get brighter (11%, 6%, 4%): not
  "the same fraction". Describe it as the data show it; don't explain
  the count-versus-fraction shape beyond what the notes verify. The fit's own error alone would be too small by 1.3–1.9 (4.4 again).
- Where the clue is: each item's `summary.json` `diagnostics.xpois`:
  `chi2` / `dof` ≈ 15.8, `fit_pixel_count` 4,743 (of 640,000; <1%),
  `kernel_sum` 0.97. The shipped `subtract.auto_stamp_mask: true` fits the
  kernel on `auto_stamp_count: 5` stamps of 31 × 31 around the brightest
  compact peaks: on this galaxy field, a poor kernel. A poor kernel leaves
  the difference's PSF wider than the target's, so a fixed-width PSF flux
  loses light (verified on one seed: given σ 1.70 instead of 1.57, the bias
  vanishes for bright fakes).
- Hint ladder: (a) "The error bars look right. What would make every value
  come out low, by a few hundred counts at every brightness?" (b) "Which stage decides how well the
  reference is matched? Ask for its numbers in the summary." (c) show
  `diagnostics.xpois` and the `subtract:` block.
- Fix: `--set subtract.auto_stamp_mask=false` (fit the kernel on all usable
  pixels, as their 4.2 chain did). Rerun the injection to `inj/run-whole`,
  figure with both runs:
  `python <this dir>/injection_figure.py inj 5.3_injection_both.png "inj/run-shipped=Shipped kernel settings" "inj/run-whole=Kernel fitted on the whole image"`;
  `show_figure` in the turn. Facts: χ²/dof 1.30, fit pixels 404,012;
  measured/planted 0.99 / 1.00 / 1.00; pull mean −0.01 / +0.09 / −0.40,
  scatter 0.77 / 0.94 / 0.86; fit-only 1.57 / 1.79 / 1.60. A few outliers
  (|pull| > 4, about 5 of 300) are fakes planted next to a bright star's
  residue: blending, not the budget.
  (Adding 4.2's kernel basis, 19 × 19 and widths 0.7/1.4/2.8, without this
  fix does *not* help: χ²/dof stays ~15 and the corr factor goes to 85.)
- **Pass:** (a) bars right-sized, values biased low, said in their words;
  (b) the bias traced to the kernel fit (χ²/dof, few pixels, or the
  auto-stamp setting), or a well-argued test that isolates it; (c) a rerun
  shows it gone. If they ask whether the error budget should have caught it:
  that's the point; it can't (M-BUDGET-BIAS).
- Final configuration on the real pair (`--set subtract.auto_stamp_mask=false`,
  PSF 1.57): χ²/dof 1.13, 9 candidates; SN 43,657 ± 345 (fit 183). Mention if
  they ask what changed for the supernova: almost nothing, it's bright; the
  bias mattered most for faint sources (−11% at 2000 counts).
- `reveal("5.3")`.

## Closing
The closing quotes our reference run: Gaussian fakes of σ 1.57 px from
`inject_chain.py`, the shipped kernel and the whole-image rerun
(`subtract.auto_stamp_mask=false`). A learner-designed variant (empirical
PSF, other spacing) is welcome, but run the course's test and the rerun too
before settling `what-went-wrong`, so the closing's numbers exist in this
run. Before `reveal`, compare with the learner's own numbers; where theirs
differ, pass `your_run`: their numbers and what that changes.
