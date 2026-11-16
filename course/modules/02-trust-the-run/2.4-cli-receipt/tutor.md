# 2.4 · tutor notes

**Goal:** the learner reads a CLI receipt and separates the FITS reader from
the compute backend, each requested versus used. Introduces
M-READER-IS-BACKEND (used in Module 03).

If `work/01/sample/` is missing, make it with
`python <course dir>/modules/01-first-difference/make_sample.py <cuPhoton checkout> work/01`.

## Your turn `reader-and-backend`
- Run `cuphoton xrep reproject-image --input work/01/sample/target.fits --output-dir work/02/xrep-cli`
  (`cuphoton` is on the PATH). It writes
  `work/02/xrep-cli/reproject-image-<timestamp>/summary.json`.
- Show the receipt's relevant fields in a code block (not the whole file):
  `workflow`, `requested_backend`, `backend`, `device`, `dtype`, `fits_reader`,
  and `fits_reads[0]`: `reader`, `requested_reader`, `location`,
  `fallback_reason`, `hdus[0].shape`, `hdus[0].dtype`.
- Facts (real run, pinned commit): `requested_backend auto`, `backend cpu`,
  `device cpu`, `dtype float64`, `fits_reader auto`; `fits_reads[0]`:
  `reader astropy`, `requested_reader astropy`, `location host`,
  `fallback_reason null`, shape `[256, 256]`, dtype `<f4`.
- Note to discuss if they spot it: `fits_reader` says auto but
  `requested_reader` says astropy. CPU workflows turn auto into Astropy before
  reading, so the read receipt shows astropy as the request.
- **Pass:** for each of reader and backend, the request and what ran, read
  from the receipt, in any words. Then, if they want, try `--backend cupy` into a new directory:
  exit 1, `ERROR: No module named 'cupy'` (the CLI's message is shorter than
  the Python one).
- Settle, then `reveal("2.4")`.
