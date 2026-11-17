# 3.3 · tutor notes

**Goal:** the learner predicts and reads FITS read receipts: a real GPU read,
the default reader, and a quiet fallback caused by the file's format. Sees
that `auto` falls back for the reader exactly as for backends.
Probes M-READER-IS-BACKEND, M-XDR-INSTALLED, M-COMPRESSED-SAME.

Source: docs/guide/read-fits.qmd ("Choose a reader", "Write files xDR can
decode"), docs/troubleshooting.md ("FITS reading used Astropy or could not
load xDR"). Use the GPU environment, on `work/01/sample/target.fits` (make it
with the Module 01 `make_sample.py` if missing). `reads.py`, next to these
notes, does both turns: copy it to `work/03/` and run
`python reads.py ../01/sample/target.fits` from there; it writes the two
compressed copies next to the sample. Show its output in code blocks.

**First, check xDR is built here:** `python -c "from cuphoton.xdr.nvcomp_batch
import cpp_helper_available; print(cpp_helper_available())"`. The course's
`tools/setup-gpu-env.sh` builds it, but the build needs CUDA and cuFile headers
and a thread-safe CFITSIO, and a compute centre may lack them. If it prints
False, use the facts under "Without xDR" and say why it's missing.

## Your turn `three-reads` (prediction, then reading)
- Collect the three predictions, then run the first part of `reads.py`.
- Facts (real run, pinned commit, GPU environment with xDR built):
  ```
  device=True,  reader='auto' -> cupy   reader xdr, requested auto, location device, fallback_reason None
  device=True,  reader='xdr'  -> cupy   reader xdr, requested xdr, location device, fallback_reason None
  device=False (default)      -> numpy  reader astropy, requested astropy, location host, fallback_reason None
  ```
  The trap is the third: the default `reader` is `astropy`, not `auto`.
- Compare with their predictions in your reply.
- **Pass:** they read the reader and location from each receipt, and say why
  the third used Astropy (the default reader).
- Settle.

## Your turn `compressed` (prediction, then reading)
- Collect the two predictions, then run the second part.
- Facts (the sample target: 267,840 bytes, sky noise 8.2 counts):
  ```
  astropy default: 77,760 bytes, RICE_1; xdr_unsupported_reason 'compression RICE_1 requires Astropy'
    auto -> cupy  reader astropy, requested auto, location device, fallback_reason 'compression RICE_1 requires Astropy'
    xdr  -> ValueError: Cannot use xDR: compression RICE_1 requires Astropy
    pixels: not identical, max |change| 0.315, rms 0.141
  GZIP_2, quantize_level=0: 241,920 bytes, GZIP_2
    auto, xdr -> cupy  reader xdr, location device, no fallback; pixels identical
  ```
- Why: Astropy's `CompImageHDU` defaults to RICE_1 and quantizes floats
  before compressing (lossy, about 1/60 of the noise here). xDR decodes only
  uncompressed or GZIP_1/GZIP_2 tile-compressed images, and rejects every
  quantized image (the guide's "Write files xDR can decode": also no
  `BSCALE`/`BZERO`/`BLANK`, no `.fits.gz`). `inspect_fits_images` reports
  `xdr_unsupported_reason` per HDU without decoding.
- Real surveys: many archives store fpack'ed RICE_1 images. Pan-STARRS1's
  full warps are RICE_1-compressed 16-bit integers with BSCALE/BZERO scaling
  (checked on Module 04's reference night in the archive), so xDR would
  reject them twice over; Module 04's cutouts come uncompressed from the
  cutout service. Every such file falls back.
- **Pass:** they notice from the receipt that `auto` quietly used Astropy for
  the default-compressed copy and that a named `xdr` would have failed loudly,
  and they link it to the Module 02 rule (auto falls back quietly, a named
  choice fails). Noticing that the pixels changed is a bonus; if they don't,
  ask whether the default copy holds the same image.
- If they ask about GPUDirect Storage (the blog's I/O figures): the receipt
  doesn't record it (guide). xDR's cuFile writes `cufile.log` into the working
  directory; here it says `failed to open /proc/driver/nvidia-fs/devcount`:
  no GDS driver, so files are read the ordinary way (KvikIO's compatibility
  mode) and decoded on the GPU. GDS needs a supported driver, filesystem and
  storage (docs/components/xdr.md, "Install").
- Settle, then `reveal("3.3")`.

## Without xDR (only if `cpp_helper_available()` is False)
- Every read falls back: auto -> reader astropy, location device,
  fallback_reason 'xDR GPU dependencies or a CUDA device are unavailable';
  xdr -> ValueError with that reason; the compressed copies give the same
  reason, so the format trap can't be seen. Teach the first turn on the
  fallback (the receipt says why), skip `compressed`'s run, and tell them
  what it would show (the facts above). The fix is building the extension:
  `bash src/cuphoton/xdr/src/build.sh` in the checkout, with
  `PYTHON=<GPU env python>` (docs/components/xdr.md, "Install").
