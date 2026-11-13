---
name: cuphoton
description: Operate NVIDIA cuPhoton, the GPU-accelerated toolkit for astronomical imaging (FITS reading, reprojection, difference imaging, source and dipole fitting, real/bogus scoring), X-ray detector traces and signal correlation. Use this whenever the user wants to run, write, adapt, debug or explain cuPhoton code or commands, or mentions xDR/xDataReader, xRep, xPois, xFit, xScan, xImage, xRay, xBeam, xLens, FITS-to-GPU loading, image subtraction, transient or candidate detection with cuPhoton, even if they don't name cuPhoton.
---

# cuPhoton

Working layer: how to *use* cuPhoton correctly. Paths below are relative to the
cuPhoton checkout (its absolute path is in your system prompt). Draft for upstreaming into
NVIDIA/cuPhoton. Contains no teaching behavior.

## Ground truth

cuPhoton is 0.1.x and changes quickly. Read the checkout, not your memory:

- Choosing a component: README.md, table "Choose a workflow".
- Shared conventions: docs/guide/concepts.qmd. **Read it before writing any
  multi-component code.**
- Task guides: docs/guide/*.qmd (read-fits, align, subtract, measure, classify,
  transient-chain, scale, uncertainty, …).
- Data contracts: docs/data-artifacts.md. CLI: docs/cli.md.
- When stuck: docs/troubleshooting.md.

## Before running anything

```bash
uv run --no-sync python -c "import cuphoton, sys; print(sys.executable, cuphoton.__version__)"
nvidia-smi   # only if GPU work is intended
```
Linux only, CPython 3.12–3.14, environments via `uv sync --locked` with extras
(`gpu`, `ximage`, `catalog`, `viz`, …). xDR's native FITS extension is a separate
build: docs/components/xdr.md#install.

## Conventions that cause silent errors

1. **Axis order differs by call.** Arrays are `[y, x]`. `identify_residual_hotspots`
   returns `peak_yx`; `window_stamps`, xFit positions and Astropy WCS use `(x, y)`;
   xRep `BBox` is `min_x, min_y, width, height`. Check the table in concepts.qmd
   for every position you pass.
2. **`auto` falls back to CPU silently.** Explicit backends fail instead. `auto`
   never picks `cutile` or `native`. The CPU name is `cpu` in xRep/xPois and
   `numpy` in xFit/xBeam.
3. **Host vs device.** Host-result APIs return NumPy even after a GPU backend ran;
   `*_device` functions keep CuPy results on the GPU.
4. **Two mask polarities.** Instrument masks: integer bits, nonzero = flagged.
   Fit masks: boolean, True = use.
5. **Variance is load-bearing.** It sets weights and error scale. Build it from
   the instrument's noise model, not as a placeholder.
6. **FITS reader ≠ compute backend.** Separate choices; check the read receipt.
7. **Fresh output directory** per run; reuse is refused by design.
8. **Dtype.** xRep and xPois compute and return float64 whatever you pass; xFit's
   fit_dipoles/fit_single_sources preserve float32 or float64. Check concepts.qmd
   "Dtype and device" before any precision claim.

## After running: report evidence, not success

For every run, tell the user:
- the backend and device that actually ran (receipt or `summary.json`), and any
  fallback reason;
- for fits, `converged` and `uncertainty_valid` counts (necessary, not sufficient), and each fitted position's offset from its cutout center;
- a plot whenever the result is an image or cutout;
- for synthetic data, how results compare with what was injected.

While a checkpoint or exercise is open, report only what the learner asks for:
the evidence list above can hand over the answer (Your turn rule 3).

Don't describe a run as correct because it raised no error. Silent fallbacks,
swapped axes and wrong variances all run cleanly.

## Performance claims

Synchronize the device before timing. Separate load from compute. Published
figures (e.g. the 14,900x image-loading result) are per-operation against a CPU
baseline, not end-to-end pipeline speedups.
