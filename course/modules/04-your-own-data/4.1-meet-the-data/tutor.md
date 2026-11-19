# 4.1 · tutor notes

**Goal:** the learner finds what was already done to real survey data and
adapts: no alignment needed, sky-subtracted images, the survey's variance map
(checked against the data), mask bits from the header. Probes
M-VARIANCE-COSMETIC, M-MASK-POLARITY.

Data: `<course dir>/modules/04-your-own-data/data/` (see its README.md): for
`reference` and `target`: `.fits` (image, counts), `.var.fits` (variance,
counts²), `.mask.fits` (integer bits, 0 = good). Copy it to `work/04/data/`.
Use the GPU environment for cuPhoton from here on.

## Your turn `what-differs`
- Hand over what they ask for; don't list the differences for them. Facts
  (verified on these files):
  - Same grid: both are PS1 "warps" of sky cell 2381.053 at 0.25″/px, 800×800;
    the WCS headers are identical. xRep's `make_wcs_pair_transform` moves
    points by 3e-10 px: alignment is the identity. (If they ask to run xRep
    anyway, fine: it changes nothing.)
  - Sky-subtracted: empty sky has a median of about +1 count (reference 1.1,
    target 1.3). The sky level isn't in the image, but its noise is.
  - Chip gaps: the camera's gaps between detectors leave blank strips (NaN,
    mask bit 8 BLANK). Usable pixels in both: 72.7%.
  - Masks: bits are named in the mask header (MSKNAMxx/MSKVALxx: DETECTOR 1,
    FLAT 2, DARK 4, BLANK 8, CTE 16, SAT 32, LOW 64, SUSPECT 128, CR 256, SPIKE
    512, GHOST 1024, STREAK 2048, STARCORE 4096, CONV.BAD 8192, CONV.POOR
    16384), and `MSKVAL16 = 8575` ("MASK.VALUE") is the survey's own set of
    bits meaning "don't use". Nonzero is flagged; a fit mask for cuPhoton is
    the opposite (True = use): M-MASK-POLARITY.
  - Headers: EXPTIME 40 s both; CELL.GAIN 0.99 (ref) and 1.16 (target);
    CELL.READNOISE 5.6 and 6.6 e-; CHIP.SEEING 3.43 and 3.59 (FWHM in detector
    pixels of 0.258″), i.e. σ ≈ 1.52 and 1.57 warp pixels: similar seeing.
  - The supernova: don't mention it. Let them see the images if they ask
    (grey scale, same stretch, chip gaps visible).
- **Pass:** at least: (a) same grid, so alignment can be skipped or checked;
  (b) sky-subtracted; (c) masks with named bits, to combine from both nights;
  (d) a variance map is provided. In any words.
- Settle, then the next turn opens.

## Your turn `noise-model` (checkpoint)
- **Pass:** value/gain gives about 1 count² on empty sky (the sky was
  subtracted, so its noise is lost from the recipe) versus a real scatter of
  about 175 count²; so use the survey's variance map; and check it against the
  data (e.g. the scatter of empty-sky pixels).
- Run the check they propose, on empty sky (the corners, sources masked):
  over the whole frame the galaxy's structure inflates the scatter (ref 213).
  Facts: robust variance of empty sky (MAD²) 179 (ref) and 174 (target); the
  variance map's median there 151 and 173. The target agrees; the reference's
  map runs about 15% low. Say both.
- If they say "variance doesn't matter much" (M-VARIANCE-COSMETIC): remind them
  of 1.6 (error bars scale with it) in one sentence.
- Settle, then `reveal("4.1")`.
