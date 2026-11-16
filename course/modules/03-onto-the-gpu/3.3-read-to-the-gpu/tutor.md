# 3.3 · tutor notes

**Goal:** the learner predicts and reads three FITS read receipts, and sees
that `auto` falls back for the reader exactly as for backends.
Probes M-READER-IS-BACKEND, M-XDR-INSTALLED.

Source: docs/guide/read-fits.qmd ("Choose a reader"), docs/troubleshooting.md
("FITS reading used Astropy or could not load xDR"). Use the GPU environment,
on `work/01/sample/target.fits` (make it with the Module 01 `make_sample.py`
if missing).

## Your turn `three-reads` (prediction, then reading)
- Collect the three predictions, then run `work/03/reads.py`, printing for each
  the array module (`cuphoton.core.arrays.array_module`) and
  `metadata()`'s `reader`, `requested_reader`, `location`, `fallback_reason`,
  or the error. Show the output in a code block.
- Facts (real run, pinned commit, GPU environment):
  ```
  device=True, reader='auto' -> cupy  reader astropy, requested auto, location device,
      fallback_reason 'xDR GPU dependencies or a CUDA device are unavailable'
  device=True, reader='xdr'  -> ValueError: Cannot use xDR: xDR GPU dependencies or a CUDA device are unavailable
  device=False (reader astropy, the default) -> numpy  reader astropy, location host, no fallback
  ```
  Note the default `reader` is `astropy`, not `auto`.
- Compare with their predictions in your reply. If they ask why xDR is
  missing: source and editable installs don't compile it, even with the `io`
  or `gpu` extra (docs/troubleshooting.md; docs/components/xdr.md, "Install").
  Building it is out of scope here; say so.
- **Pass:** for the auto read, they say from the receipt that Astropy read it
  and it was then put on the device, and that the receipt says why; and they link
  it to the Module 02 rule (auto falls back quietly, a named reader fails).
- Settle, then `reveal("3.3")`.
