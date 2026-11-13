# 1.1 · tutor notes

**Goal:** the learner knows what we test on (a synthetic pair with injected,
known changes, in FITS files) and why the two images can't be subtracted yet.

Module source: `docs/guide/first-difference.qmd` and `_sample-pair.qmd` in the
pinned checkout. Follow their code and numbers. Work in `work/01/`.

## On open: fill the slot `pair`
1. Make the pair with the course's copy of the guide's generator:
   `python <course dir>/modules/01-first-difference/make_sample.py <cuPhoton checkout> work/01`
   (writes `work/01/sample/reference.fits` and `target.fits`).
2. One script `work/01/read_pair.py`: read both with
   `cuphoton.core.fits_io.read_fits_images` as in the guide, then save
   `work/01/1.1_pair.png`: two panels, reference and target, each in grey scale
   with its own colour bar, display stretch 1st–99.5th percentile (say so in
   the caption), titles "Reference (300×300)" and "Target (256×256)".
3. `show_figure(slot="pair")`.

Don't say what was injected (a star made 3× brighter, flux change +12,120 DN;
a new source of 4,000 DN). That is opened in 1.5.

## Your turn `two-shapes`
- **Pass:** different pixel grids (detector size, pixel scale, pointing,
  rotation; any two of these), so the same pixel index isn't the same sky; one
  image must be put onto the other's grid first. Accept "align them, like in
  0.3" if they add *why* a plain shift may not be enough.
- If they ask, the headers say: reference 0.26″/px, target 0.27″/px and rotated
  3°, different gain, different PSF width. Give these as facts when asked.
- When you settle, link it to practice in a sentence (surveys combine images
  from different nights, cameras and telescopes). Then `reveal("1.1")`.
