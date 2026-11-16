# 5.2 · tutor notes

**Goal:** the learner reads the catalog against their own 4.2/4.3 results:
rows aren't objects, flags name which quantity failed. Probes M-UQVALID.

## Slot `catalog` (on open)
- Needs 5.1's `run2` (PSF width set, shipped kernel settings). If it's
  missing, rerun it (see 5.1 notes) before anything else.
- Figure: `catalog_figure.py` next to these notes, run in place with the GPU
  environment's python from `work/05/`:
  `python <this dir>/catalog_figure.py run2/catalog.parquet <data>/target.fits 5.2_catalog.png`.
  Rows within 10 px share a label ("1, 9"). `show_figure(slot="catalog")`.
- Post the short table with it, in a code block: row, x, y, peak_abs_sigma,
  sign, psf_flux, psf_flux_err, uq_valid, quality_flags.

## Facts (run2, verified 16 Nov)

| row | x, y | peak_abs_sigma | sign | psf_flux ± err (err_fit) | uq_valid | flags | what |
|---|---|---|---|---|---|---|---|
| 0 | 402, 400 | 169.8 | + | 43,407 ± 329 (183) | False | 101 | SN 2011fe |
| 1 | 404, 640 | 110.4 | + | 1,524 ± 470 | True | 16 | star A (4.3) |
| 9 | 402, 645 | 8.1 | + | 1,527 ± 469 | True | 16 | star A again |
| 2 | 707, 456 | 94.5 | + | 6,105 ± 574 | True | 2 | bright star (not in 4.3's four) |
| 10 | 704, 462 | 8.0 | + | 6,105 ± 574 | True | 10 | same star |
| 3 | 45, 244 | 40.8 | + | 831 ± 178 | True | 2 | star B (4.3) |
| 6 | 49, 247 | 9.8 | − | −132 ± 134 | True | 26 | B, negative part |
| 11 | 50, 243 | 7.7 | + | 78 ± 125 | False | 27 | B again |
| 4, 5 | 273, 85 / 271, 82 | 19.8 / 19.1 | + | NaN | False | 15 | star D (4.3) |
| 8 | 276, 87 | 9.1 | − | NaN | False | 111 | D, negative part |
| 7 | 766, 453 | 9.8 | + | 710 ± 216 | True | 0 | weak residue on a star |

- Flag bits (`cuphoton.xfit.DipoleQualityFlag`): 1 UNCERTAINTY_INVALID,
  2 WIDTH_OUT_OF_RANGE, 4 LOBE_OUTSIDE_STAMP, 8 NO_LOBE_AT_CANDIDATE,
  16 LOBES_OVERLAP, 32 NEGATIVE_LOBE_UNSUPPORTED, 64 POSITIVE_LOBE_UNSUPPORTED.
  101 = 1+4+32+64.
- `peak_abs_sigma` is the peak |residual| over the robust sigma of the
  residual, not 4.2's z (residual over the propagated noise): 170 vs 62 for
  the same supernova. Different denominators; don't compare them as if equal.
- Same-place rows: the chain's detector finds each connected hotspot above 5
  (with `min_pixels` 3); a star's twisted residue has several, of both signs.
  Rows 1/9 and 2/10 even get the same psf_flux: it's measured at the fitted
  positive lobe, which lands on the same star.

## Your turn `same-answer`
- **Pass:** (a) the supernova is found (row 0), flux close to theirs
  (43,407 vs 43,867 ± 186 in 4.4; err 329 vs 186: that's 5.3's question, just
  note it); (b) the bogus residues of 4.3 are there (A, B, D), plus the star
  at (707, 456) and a weak one; (c) several rows per place, with the reason
  (split residues, both signs). If they count 12 "objects", point at the
  figure's shared labels.
- Show stamps only if asked: the chain writes no difference image
  (`transfers.intermediate_files: 0`); you'd have to rerun 4.2's chain for it.

## Your turn `trust-a-row` (checkpoint)
- SN row 0 details: `fit_model` "dipole", positive lobe on the source
  (source_x/y offsets 0.39, −0.12), negative lobe at (−328, −318) from the
  stamp centre: 457 px separation; `center_x_err` NaN; `psf_flux_err` 329
  defined; `uq_window_masked` False; flags 101.
- The `uq_valid` definition (catalog.py): true when *every* computed `<q>_err`
  of the row is defined; false when fewer than half of a window's pixels are
  usable, its correlation factor is undefined, or a total is non-finite. "The
  center requires both lobe windows to pass separately."
- **Pass:** yes, the flux and its error bar are usable; uq_valid is False
  because another quantity (the centre/separation of the dipole fit) has no
  error bar, and that's because a new point source isn't a dipole. Any
  equivalent reasoning from the columns they asked for.
- After settling, the other side (M-UQVALID): uq_valid True doesn't mean the
  bars are right. Verified example: with `uq.enabled=false`, every row is
  True, including row 8 of the final configuration's catalog, whose fit
  diverged (psf_flux −2.1 × 10²⁹). The bars are tested in 5.3.
- `reveal("5.2")`.
