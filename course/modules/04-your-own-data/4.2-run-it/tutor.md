# 4.2 · tutor notes

**Goal:** the learner directs the whole chain on real data in one instruction,
then reads the result. Probes M-AGENT-SUCCESS (the evidence they ask for).

## Your turn `direct-run`
- Run exactly what they instruct, with the GPU environment, into
  `work/04/run-<n>/`. If the instruction leaves out something that matters
  (masks, variance, backend), ask about that one thing before running.
- Reference implementation (verified): fit mask = finite in all four arrays and
  `(mask & 8575) == 0` in both nights and variance > 0; set masked pixels to 0
  in the inputs (NaNs would spread through the convolution); xPois
  `solve_constant_kernel(ref, target, basis, kernel_shape=(19,19),
  variance=target_var (huge where masked), fit_mask=use, background_degree=1,
  backend="cupy")` with the guide's basis (0.7/4, 1.4/2, 2.8/2); difference
  NaN where not used; `standardize_constant_kernel_residual` with both
  variance maps **set to NaN where not used** (not 0, not huge): then every
  pixel whose 19×19 kernel footprint touches a masked pixel drops out, the same
  reason as 1.4's NaN frame. With 0 instead, the noise along every mask edge is
  underestimated and the run finds about 37 hotspots instead of 19, the extra
  ones single pixels along chip gaps (verified both ways). If the learner asks
  why the count changed, that's a good discussion: it links back to 1.4.
  Hotspots at threshold 5. No xRep (identity), or run it if
  they ask.
- Report back against *their* evidence list (and their 2.6 list), nothing more.
  Facts: kernel sum 1.022, chi2/dof 1.26, 19 hotspots above 5 (10 above 10),
  run on the GPU (cupy, cuda).
- Figure `work/04/4.2_overview.png`: reference, target and z (±6), grey scale,
  side by side. Excluded pixels (chip gaps, masks) in one distinct colour
  (`cmap.set_bad`, e.g. blue), said in the caption: never white or black,
  which on a grey z map read as "brighter" or "fainter". Stretch the sky
  panels so the galaxy's arms show (e.g. 1st–99.5th percentile, or an
  asinh stretch). `show_figure(slot="overview")`. Don't mark or name the
  supernova. Use the same colours in 4.3's figure.
- Settle `direct-run` in the same reply as the report and the figure, before
  anything about what came out: the page then opens `what-came-out` with its
  own question. Don't ask that question yourself.

## Your turn `what-came-out`
- **Pass:** the galaxy cancelled (flat noise where the arms were), and one
  bright new source stands out; mention of other weaker spots is a bonus.
- If they ask for coordinates: the strong source is at the image centre
  (x 402, y 400), RA 210.7742°, Dec +54.2737°. If they look it up or know it:
  SN 2011fe, a type Ia supernova discovered on 2011 August 24, the nearest in
  decades. If they don't, say it after settling.
- Settle, then `reveal("4.2")`.
