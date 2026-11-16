# 4.3 · tutor notes

**Goal:** the learner sorts real from bogus by looking: presence in the
reference, shape, sign. Names SN 2011fe after the sort.

## Slot `candidates` (on open, if the 4.2 run exists; else after redoing it)
- Figure `work/04/4.3_candidates.png`: a grid, one row per candidate, columns
  reference / target / z (±8), 31×31 px cutouts, grey scale, each row lettered
  A to D from top to bottom. The four strongest from the verified run, in this
  order, so the real one isn't simply first: A (403, 640), B (46, 246),
  C the supernova (402, 400), D (274, 84). `show_figure(slot="candidates")`.

## Your turn `sort-them` (checkpoint)
- Facts: C (the supernova): nothing in the reference (peak 47, noise), round
  source in the target (peak 2450), clean round positive blob in z (z ≈ 62).
  A, B, D: bright stars present on both nights (target peaks 5342, 3423, 1894;
  reference 5972, 4333, 2361); z shows a twisted positive/negative residue,
  typical of kernel mismatch (the PSF shape varies across the detector, and
  one constant kernel for the whole image can't fit every star). A touches a
  chip gap. B carries the SUSPECT bit (128) in the target mask, which isn't in
  the survey's "don't use" set.
- **Pass:** C real, A/B/D bogus, each with evidence from the cutouts (source in
  both nights or not; shape; sign). If they call any of A/B/D a variable star,
  ask what a star that really brightened or faded would leave (a residue with
  the star's own shape, one sign, not a twisted pair).
- After settling: name it. SN 2011fe, type Ia, in M101, discovered 2011 Aug 24
  (Nugent et al. 2011), the nearest type Ia in decades; the target night is
  233 days after the explosion. Optional depth if they ask how bright: fit
  ≈ 43,900 ± 190 counts; calibrated against ~20 PS1 catalogue stars in the same
  image (zero point 26.9 ± 0.2), that's r ≈ 15.3. The header's FPA.ZP does
  **not** apply directly to these warps (it gives 17.0: off by 1.7 mag); a good
  "check the header against the data" story if they're interested.
- `reveal("4.3")`.
