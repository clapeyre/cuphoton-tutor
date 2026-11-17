# Misconception catalogue

The core asset of the course. Each entry: what the learner believes, what is
true, where the truth is documented, and a **probe**: a question or task that
surfaces the belief without naming it. Paths are relative to the cuPhoton checkout.

Status: seeded from the docs. Entries marked `source: field` come from real
learners; prefer them. Harvest more with `.claude/commands/harvest-misconceptions.md`.

## The problem itself

### M-SUBTRACT: "Align the images, subtract, done."
- **Truth:** Two exposures differ in blur, brightness scale and sky level as well
  as geometry. A plain subtraction leaves a ring or dipole at every star.
- **Docs:** docs/guide/first-difference.qmd, "Match the blur and subtract".
- **Probe:** Show two aligned images with different blur; ask them to sketch what
  the difference will look like around one star. Then show it.
- **Modules:** 00, 01

### M-ALIGN-BLUR: "Reprojection also matches the blur."
- **Truth:** xRep handles pixel-to-sky geometry only. Blur matching is xPois.
- **Docs:** README.md, xRep section.
- **Probe:** "After xRep, which differences between the two images remain?"
- **Modules:** 00, 01

### M-NEWSIGNAL: "Anything bright in the difference image is a new object."
- **Truth:** Brightening stars, moving sources and misalignment (dipoles) also
  leave residuals; that is why xFit measures shape and xScan scores real/bogus.
- **Docs:** docs/glossary.md (Dipole), README.md (xFit, xScan).
- **Probe:** Show a dipole cutout; ask what could have caused it.
- **Modules:** 00, 01
- field: 2026-11-10, "if you move something in one and not the other … you're
  going to have a spike where your star was moved" (it is a +/− pair, not one
  spike). He also asked whether the shift was a sensing error or a real change,
  which is the right question: both give the same dipole.

## Conventions

### M-AXIS: "Positions are (x, y) everywhere" (or "(y, x) everywhere").
- **Truth:** Arrays index `[y, x]`. Some calls take `(y, x)`, others `(x, y)`:
  `identify_residual_hotspots` returns `peak_yx`; `window_stamps` and xFit
  positions take `(x, y)`; xRep `BBox` is `min_x, min_y, width, height`.
- **Docs:** docs/guide/concepts.qmd, table "Axis order by call".
- **Probe:** Exercise 01/swapped_axes. Or: "The hotspot says (167, 80). Where do
  we cut the stamp?"
- **Modules:** 01

### M-MASK-POLARITY: "A mask is True where pixels are bad."
- **Truth:** Two kinds with opposite sense. Instrument masks are integer bit
  flags, nonzero = flagged. Fit masks are boolean, True = **use** the pixel.
  A learner who says "nonzero = bad" is right for instrument and xRep masks
  (aligned.mask); only the boolean fit mask flips. Confirm that half before probing.
- **Docs:** docs/guide/concepts.qmd, "Variance and masks".
- **Probe:** Hand them `aligned.mask` and ask for the mask to pass to xFit.
- **Modules:** 01, 04

### M-VARIANCE-COSMETIC: "Variance is optional bookkeeping."
- **Truth:** It sets the fit weights and the scale of every reported error. Too
  small a variance gives error bars that are too small; flux is unchanged.
- **Docs:** docs/guide/concepts.qmd; docs/uncertainty-quantification.md.
- **Probe:** "If we multiply the variance by 4, what happens to the flux and to its error?"
- **Modules:** 01, 04

## Trusting a run

### M-AUTO-GPU: "It ran, and I have a GPU, so it ran on the GPU."
- **Truth:** `auto` falls back to CPU whenever a GPU backend can't run, and the run
  still succeeds. The receipt / `summary.json` records what actually ran.
- **Docs:** docs/guide/concepts.qmd ("Backends", "Receipts"); docs/troubleshooting.md.
- **Probe:** After any run, ask "where did that execute?" before they look.
- **Modules:** 02, 03

### M-EXPLICIT-FALLBACK: "Naming a backend falls back like auto does."
- **Truth:** An explicit backend fails instead of falling back. `auto` never picks
  `cutile` or `native`.
- **Docs:** docs/guide/concepts.qmd, "Backends".
- **Probe:** Ask them to predict what `backend="cupy"` does on a CPU-only host.
- **Modules:** 02, 03

### M-BACKEND-NAMES: "`backend='cpu'` works in every module."
- **Truth:** The CPU path is `cpu` in xRep and xPois but `numpy` in xFit and xBeam.
- **Docs:** docs/guide/concepts.qmd, table "Backend names".
- **Modules:** 02

### M-HOST-DEVICE: "A GPU backend hands back GPU arrays."
- **Truth:** Host-result APIs (e.g. `reproject_masked_array`, `fit_dipoles`) return
  NumPy whatever ran. `*_device` functions keep results on the GPU; some calls
  follow their input type.
- **Docs:** docs/guide/concepts.qmd, "Dtype and device".
- **Probe:** "After the cupy reprojection, is `aligned.image` on the GPU?"
- **Modules:** 03

### M-FLOAT32: "Feed float32 and the GPU stages stay float32."
- **Truth:** xRep and xPois compute and return float64; xFit preserves
  float32/float64 input.
- **Docs:** docs/guide/concepts.qmd, "Dtype and device".
- **Probe:** "We pass float32 to xRep. What dtype comes back?" Then print
  `aligned.image.dtype`.
- **Modules:** 03

### M-READER-IS-BACKEND: "The FITS reader and the compute backend are one choice."
- **Truth:** Separate. A GPU fit can read through Astropy and transfer. `auto`
  reader falls back to Astropy for unsupported scaling or compression.
- **Docs:** docs/troubleshooting.md, "FITS reading used Astropy".
- **Modules:** 03

### M-XDR-INSTALLED: "The gpu extra gives me the GPU FITS reader."
- **Truth:** xDR's native extension needs a separate source build and isn't part of
  the quickstart.
- **Docs:** docs/components/xdr.md#install; docs/quickstarts.md.
- **Modules:** 03

### M-COMPRESSED-SAME: "A compressed FITS file is the same image, read the same way."
- **Truth:** Astropy's default compression (RICE_1) rounds floating-point
  pixels first, so the pixels change slightly, and xDR can't decode it, so
  `reader="auto"` quietly falls back to Astropy on the CPU. Lossless GZIP_1 or
  GZIP_2 with `quantize_level=0` keeps both.
- **Docs:** docs/guide/read-fits.qmd, "Write files xDR can decode".
- **Probe:** "Which reader would decode your survey's files, and how would you check before reading a pixel?"
- **Modules:** 03

### M-OUTDIR: "Rerunning fails, so something's broken."
- **Truth:** Runs require a fresh output directory by design, to preserve results.
- **Docs:** docs/troubleshooting.md, "A run directory already exists".
- **Modules:** 02

## Reading the numbers

### M-CHI2-VALIDATES: "chi2/dof near 1 means the subtraction is good."
- **Truth:** It uses only target variance and is raised by real changes and model
  mismatch; on its own it doesn't validate the subtraction.
- **Docs:** docs/guide/first-difference.qmd.
- **Modules:** 01

### M-Z-SIGNIFICANCE: "z > 5 means a 5-sigma detection with a known false-alarm rate."
- **Truth:** z is a noise diagnostic in approximate units; it omits resampling
  covariance and kernel uncertainty.
- **Docs:** docs/guide/first-difference.qmd, "Find the candidates".
- **Modules:** 01, 04

### M-FLUX-SIGN: "`sources.flux` tells me whether it got brighter or fainter."
- **Truth:** It's a nonnegative magnitude; the sign comes from the fitted amplitude.
- **Docs:** docs/guide/first-difference.qmd, "Measure the candidates".
- **Modules:** 01

### M-SPEEDUP: "The 14,900x figure is the pipeline speedup."
- **Truth:** It is image loading against a CPU baseline. Per-operation speedups
  aren't end-to-end.
- **Docs:** NVIDIA tech blog, "Faster Scientific Image Analysis with NVIDIA cuPhoton".
- **Modules:** 03

### M-SUCCESS-COMPLETE: "The pipeline reported success, so every column and term was computed."
- **Truth:** A shipped pipeline leaves out what it lacks inputs for and still
  succeeds: without a PSF width the transient chain writes NaN fluxes and a
  fit-only error budget, and says why only in `summary.json` (`uq.excluded`,
  `psf_sigma_source`).
- **Docs:** docs/guide/uncertainty.qmd ("A term without its inputs is left out");
  examples/transient-chain/README.md, "Catalog columns" (`psf_flux`).
- **Modules:** 05

### M-UQVALID: "`uq_valid` tells me whether a row's error bars are right."
- **Truth:** It says every computed error bar in the row is *defined* (enough
  usable pixels, a defined correlation factor). False often means one quantity,
  such as a dipole's centre, is undefined while the flux error is fine. True
  doesn't test the bars against anything; with `uq.enabled=false` it is
  always true.
- **Docs:** examples/transient-chain/transient_chain/catalog.py (`uq_valid`);
  docs/guide/transient-chain.qmd.
- **Modules:** 05

### M-BUDGET-BIAS: "The error budget covers every way a flux can be wrong."
- **Truth:** It adds up noise terms: how much the value would scatter. A bias,
  such as a poor kernel fit making every flux a few percent low, moves the
  values without widening the bars. Only a test with a known answer (an
  injection test) shows it.
- **Docs:** docs/guide/uncertainty.qmd (injection and repeat tests: "A bias that
  every exposure shares passes the test unseen").
- **Modules:** 05

### M-STACK-DEPTH: "Stacking N references makes the difference √N deeper."
- **Truth:** The difference's noise is the target's plus the reference's
  blurred by the matching kernel, which averages it down. When the target is
  the noisier image (a single night against a single night, as in 4.5, where
  the reference supplied 5% of the variance), a deeper reference gains almost
  nothing. Stacking can also add area and, with nights blurrier than the
  target, mismatch residues.
- **Docs:** docs/guide/align.qmd ("Stack several images on one grid").
- **Probe:** "Where does the noise in the difference come from, and how much of it is the reference's?"
- **Modules:** 04

### M-TEST-SCORE-COVERS: "A perfect test score means the classifier will sort my candidates."
- **Truth:** The test split holds the same kinds of candidates as training. A
  kind that was never in the training set (in 4.6: cosmic rays, satellite
  trails) gets an arbitrary score, often "real". Plant the kinds you worry
  about and score them.
- **Docs:** docs/guide/classify.qmd ("Evaluate on the test split", "What is survey-specific").
- **Probe:** "What kinds of candidates were in its test split, and what kinds will the next night have?"
- **Modules:** 04

### M-SCORE-PROBABILITY: "A score of 0.99 means 99% likely to be real."
- **Truth:** xScan's score is a sigmoid output, not calibrated. It ranks
  candidates like the training set's real class; how many of those that pass
  a threshold are real depends on how common real ones are on the night.
- **Docs:** docs/guide/classify.qmd (opening paragraphs).
- **Probe:** "If one candidate in a thousand is real, how many bogus ones pass a threshold that lets 1% of bogus through?"
- **Modules:** 04

### M-PEAK-IS-SIGNAL: "The correlation peaks at the delay."
- **Truth:** A correlation always has a highest point, signal or not, and
  xBeam reports products without judging them. A delay beyond the window's
  lags gives a noise peak; circular lag mode wraps a long delay to a wrong one
  that is consistent across results. A peak means something only against
  the peaks noise makes in the same analysis, and within the delays the
  geometry allows.
- **Docs:** docs/guide/correlate.qmd (Options, `lag_mode`; Troubleshooting,
  "The lag peak is at the wrong place").
- **Probe:** "Two results agree on a lag of −124. Does that make it right?"
- **Modules:** 07

### M-RAW-CORRELATES: "Correlate the recordings as they are."
- **Truth:** A correlation follows whatever is loudest in both recordings.
  In LIGO strain that's low-frequency noise, hundreds of times the wave, so
  raw strain put GW150914's delay at +9.5 ms (wrong, though physically
  possible). xBeam applies no taper, mean removal, normalization or
  whitening; choose the band and weight it by the noise yourself.
- **Docs:** docs/guide/correlate.qmd ("Products are raw sums ...").
- **Probe:** "What frequencies hold most of the power in each recording, and are they the ones the source is at?"
- **Modules:** 07

### M-WEIGHT-MEANS-RIGHT: "Weight 1.0 means the visibility is good."
- **Truth:** A radio job's weights record how much valid data went into
  each record. A wrong delay or clock leaves full weights and normal-looking
  amplitudes per channel, with the signal turned into a phase slope across
  the band that cancels in a band average (7.2: 0.176 → 0.001).
- **Docs:** docs/guide/correlate.qmd ("Correlate radio recordings");
  docs/xbeam/data-contract.md.
- **Probe:** "Every record has weight 1.0. What would a wrong clock look like in them?"
- **Modules:** 07

### M-DELAY-SIGN: "A station that hears it later gets a positive delay."
- **Truth:** Conventions differ, even within xBeam. In time-series
  correlation a positive lag means the second signal of the pair arrives
  later; in a radio job a station's delay says how much earlier it hears
  the wavefront than the reference (DiFX's convention), and clocks add to
  it. The user guide doesn't state the job's sign; a run with a known
  answer does.
- **Docs:** docs/guide/correlate.qmd ("Read the delay from the lag
  correlation"); src/cuphoton/xbeam/adapters/radio/compute_plan.py
  (`_delay_values`).
- **Probe:** "BB's clock is 1.75 µs late. What number goes into the job, and how will you know you had the sign right?"
- **Modules:** 07

## Working through an agent

### M-AGENT-SUCCESS: "The agent ran it without errors, so the result is right."
- **Truth:** Silent fallbacks, swapped axes and wrong variance all run cleanly.
  Evidence is in receipts, plots and comparison with what was injected; fit status can look healthy on a wrong cutout.
- **Probe:** Exercise 01/swapped_axes runs without an error.
- **Modules:** 01, 02

## From the field

<!-- Append harvested entries here, with `source: field (who/when)`. -->

### M-FIT-TWO-IMAGES: "xFit fits the reference and the new image separately."
- **Belief (learner's words):** "so then we do this fit for 2 different images
  (supposedly a reference one, and a new observation...?)"
- **Truth:** xFit fits stamps cut from **one** difference image; the comparison
  between the two images already happened in xPois. Both lobe centres are
  measured in that single array. Split mode adds positive and negative planes of
  the *same* candidate; it is not a second fit.
- **Docs:** docs/guide/measure.qmd (opening paragraph, "Make a difference image");
  docs/components/xfit.md (difference and split modes).
- **Probe:** "xFit returns two lobe centres, (x_pos, y_pos) and (x_neg, y_neg).
  Which image was each one measured in?"
- **Modules:** 00, 01
- source: field (Corentin, 2026-11-10)

### M-SIGMA-VARIANCE: "σx and σy are the Gaussian's two variances."
- **Belief (learner's words):** "a 2D Gaussian … characterized by its amplitude,
  2 variances, and its center's position"
- **Truth:** `sigma_x` and `sigma_y` are standard deviations: the lobe's widths in
  pixels along the ellipse's own axes, which `theta` rotates (swapping the widths
  and adding π/2 to `theta` gives the same ellipse). They are neither the
  per-pixel `variance` plane xFit takes as weights nor the 8×8 parameter
  covariance it returns. Four "spread" objects share similar names: these widths,
  the variance plane, the covariance/`standard_errors`, and `psf_sigma`.
- **Docs:** docs/guide/measure.qmd ("GaussianDipoleModel draws one elliptical
  Gaussian twice …"; `psf_sigma` "in pixels").
- **Probe:** "The fit returns sigma_x = 1.6. In what units? Would passing a
  different variance plane change it?"
- **Modules:** 01
- source: field (Corentin, 2026-11-10)

### M-PARAM-CORRELATION: "A negative amplitude–width correlation means brighter sources are narrower."
- **Belief (learner's words):** "'correlation … about −0.5' is equivalent to
  saying that brighter and narrower trade off? I don't see it"
- **Truth:** The off-diagonal terms of xFit's covariance describe how the fit's
  *estimation errors* move together, not anything about the sources. `amplitude`
  is a peak height, not a flux (flux = 2π|A|σxσy). Raising A and narrowing σ
  change the pixels in similar ways, so noise that pushes the fitted A up tends to
  push the fitted σ down. A and σ are therefore not independent measurements, and
  downstream uses (xScan features) should not treat them as if they were.
- **Docs:** docs/guide/measure.qmd (amplitude is "their peak height"; the flux
  formula; covariance "assuming independent pixels and the supplied variances").
  No doc explains how to read the off-diagonal terms.
- **Probe:** "The covariance between amplitude and sigma_x is negative. If noise
  made the fitted amplitude too high, what do you expect of the fitted sigma_x?"
- **Tutor hazard:** don't explain it as "brighter and narrower trade off"; that
  phrasing planted this belief in the field session.
- **Modules:** 04. Module 01's fit fixes the width (`psf_sigma`), so there is no
  amplitude–width correlation to probe there.
- source: field (Corentin, 2026-11-10)

### M-AUC-CERTAINTY: "ROC AUC rewards confident answers, and any value from 0 to 1 is possible."
- **Belief (learner's words):** "possible for the model to output the wrong
  answers with total certainty, and that's an AUC of 0? … 1 if they're all right
  and perfectly certain? … So anything between 0 and 1 is possible?"
- **Truth:** ROC AUC depends only on the *order* of the scores: the fraction of
  (real, bogus) pairs where the real one scores higher, ties counting half. The
  xScan quickstart scores every candidate between 0.532 and 0.534 and still
  reports AUC 1.0. With 2 real and 2 bogus validation samples there are only 4
  pairs, so AUC moves in steps of 0.25 (0.125 with ties). Confidence shows up in
  the loss instead: a validation loss of 0.695 ≈ ln 2 is what always answering
  50/50 gets.
- **Docs:** docs/guide/classify.qmd ("ROC AUC measures how often a random
  labeled-real candidate outranks a labeled-bogus one, counting ties as half").
- **Probe:** After the xScan quickstart: "Validation ROC AUC is 1.0 and
  validation loss is 0.695. Is this classifier any good?"
- **Modules:** 02
- source: field (Corentin, 2026-11-10)
