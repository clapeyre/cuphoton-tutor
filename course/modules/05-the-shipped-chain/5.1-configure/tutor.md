# 5.1 · tutor notes

**Goal:** the learner turns their 4.1/4.2 decisions into the chain's
configuration, then refuses "success" as proof and finds the missing PSF width
in `summary.json`. Probes M-SUCCESS-COMPLETE, M-AGENT-SUCCESS.

## Video `v6-one-image-through-the-chain` (opens the module)
What the chain is, its stages on the GPU with real timings from the final
configuration, the catalog row and summary it leaves, the configuration that
drives it. It names no trap: don't add one when discussing it.

## Setup (once, in the first turn)
- Working dir `work/05/`. Data: the module 04 files in
  `course/modules/04-your-own-data/data/` (absolute paths: the selections file
  needs them). Python: the GPU environment (it has the `catalog` extra and the
  `transient-chain` example installed). Launcher:
  `<checkout>/examples/transient-chain/launch.py`.
- Selections file `work/05/selections.json`, one entry, keys used by the
  generic adapter: `expnum` "m101-2012", `ccdnum` "skycell2381.053", `band`
  "r", `image`, `mask`, `variance` (target files), `template`,
  `template_mask`, `template_variance` (reference files).
- Start the configuration from `<checkout>/examples/transient-chain/config-generic.yaml`,
  copied to `work/05/config.yaml`. Reference answer (verified):
  `config-ps1.yaml` next to these notes.

## Your turn `settings`
- Show the `survey:` block of `config-generic.yaml` when asked (as written,
  comments included). It describes a DECam-style layout.
- **Pass:** at least three of the four, each with its reason from 4.1:
  1. `variance_kind: variance` for the target (shipped: `inverse_variance`;
     the PS1 `.var.fits` is a variance in counts², checked in 4.1);
  2. the template's variance (and mask) planes: `template_variance`,
     `template_mask` path keys. Without a reference variance the `corr` error
     term is left out (guide: "A term without its inputs is left out");
  3. `on_target_grid: true`: both nights are on one sky grid (identical WCS,
     4.1), so no reprojection;
  4. `mask_policy: {bits: 8575}` (MASK.VALUE, 4.1). `strict` would also
     drop SUSPECT (128) etc.; acceptable if they argue it, note the cost.
  Also `extra_keys: []` (the shipped `[field]` key isn't in our selections) and
  the identity keys; set these yourself, don't make them a question.
- Don't raise the PSF width or kernel settings here: they're the next turn
  and 5.3.
- Write the config, show the diff against the shipped file, run:
  `python launch.py --executor local --selections selections.json --config config.yaml --output-dir run1`
  from `work/05/`. Settle on the run (~45 s cold: startup and compilation).
  Facts: `success 12`, `catalog: run1/catalog.parquet`.

## Your turn `success` (checkpoint)
- What the run left (all verified): `run1/summary.json` (merged) and
  `run1/items/skycell2381.053-vm101-2012/{catalog.parquet,summary.json}`,
  `run1/records/`, `run1/workers/`. Show excerpts on request, not whole files.
- The facts in the item summary:
  - `psf_sigma_px: null`, `psf_sigma_source: null`;
  - `uq.terms: ["fit"]`; `uq.excluded`: corr, kfit, kmatch all "no PSF
    width"; mis "no misalignment model";
  - every `psf_flux`, `psf_flux_err` is NaN (catalog);
  - `diagnostics.read.receipts`: reader `xdr`, requested `auto`, no
    fallback: the planes were decoded on the GPU (3.3). If xDR isn't built
    at this centre (3.3's check), it says reader `astropy` with fallback
    "xDR GPU dependencies or a CUDA device are unavailable": not the
    problem, but a good catch. The read stage took 0.37 s with xDR against
    0.12 s with Astropy before it was built: one cold run on one small
    image, where setup dominates (3.4's warm-up lesson), not a verdict.
  - `timings_sec`: refine 0.0 s, the hint that the star step didn't run.
- Why: with `on_target_grid: true` the template provider isn't refinable, so
  the refine stage skips itself; it's the stage that matches stars and
  measures their width (README "Other surveys": "returns refinable = False and
  the refine stage skips itself"; "When `xfit.psf_sigma_px` is null that width
  is the one the uncertainty stage uses... null when neither was available and
  the psf_flux columns are NaN").
- **Pass:** they look past "success" at what was written (any of: NaN fluxes,
  `uq.excluded`, `psf_sigma_source` null) and name the missing piece (a PSF
  width) or the fix. Hint ladder: (a) "What would you want to read in the
  catalog for the supernova?" (b) "Ask for the supernova's row." (c) show
  `uq.excluded`.
- Fix: `--set xfit.psf_sigma_px=1.57` (target `CHIP.SEEING` 3.59″ × 0.258/0.25
  ″/px ÷ 2.3548; the same width 4.4 used). Rerun to `run2`. Facts: success,
  12 candidates, `uq.terms: ["fit", "corr", "kfit"]`, `uq.excluded`: kmatch
  "fewer than 5 matched stars" (same root cause: no matched stars), mis "no
  misalignment model" (fine: one grid). Settle, then `reveal("5.1")`.
