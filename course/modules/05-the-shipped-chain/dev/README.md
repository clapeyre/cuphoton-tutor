# Module 05 author notes: the shipped transient chain on the PS1 pair

The scripts now live next to the lessons that use them (5.1 config, 5.2 catalog figure,
5.3 injection and figure, 5.4 xLens watch). Runs from 16 Nov 2026,
cuPhoton `ff4d260`, `.envs/cuphoton-chain` (gpu + catalog extras + `examples/transient-chain`),
one local GPU.

- `config-ps1.yaml`: `config-generic.yaml` with the generic adapter pointed at the
  PS1 files: `variance_kind: variance` for both, the template's mask and variance,
  `on_target_grid: true`, `mask_policy: {bits: 8575}` (4.1's MASK.VALUE).
- `inject_chain.py`: 4 seeds × 75 fakes (25 each at 8000/4000/2000 counts, Gaussian
  σ = 1.57 px, on quiet usable pixels ≥ 28 px apart and ≥ 40 px from the SN),
  written as new target images + variance, with `inj/selections.json`. Run from a
  scratch dir containing `inj/`.
- `pulls.py <out dirs>`: kernel-fit diagnostics and, per flux level, the ratio
  measured/planted and the pull scatter against `psf_flux_err_fit` and `psf_flux_err`.

Run: `launch.py --executor local --selections ... --config config-ps1.yaml
--set xfit.psf_sigma_px=1.57 [--set subtract.auto_stamp_mask=false] --output-dir out`.

## Facts

| run | chi2/dof | kernel sum | fit px | flux ratio 2000/4000/8000 | pull MAD vs fit err | vs total err | total/fit |
|---|---|---|---|---|---|---|---|
| shipped defaults (no psf width) | 14.7 | 0.976 | 4,743 | psf_flux NaN; budget = fit only, "no PSF width" | | | |
| defaults + psf 1.57 | 15.8 | 0.976 | 4,743 | 0.91 / 0.94 / 0.97 | 2.3 / 1.4 / 2.0 | 1.23 / 0.78 / 1.06 | 1.8–1.9 |
| + Module 04 kernel (19², 0.7/1.4/2.8, bg 1) | 14.9 | 1.01 | 4,681 | 0.88 / 0.89 / 0.93 | | 0.4–0.9 | 8.9 (corr factor 85) |
| psf 1.57, `auto_stamp_mask: false` | 1.55 | 0.938 | 404,012 | 1.01 / 1.00 / 1.00 | 2.0 / 1.4 / 1.8 | 1.06 / 0.77 / 0.95 | 1.95 |
| same + Module 04 kernel | 1.55 | 0.964 | 387,853 | 1.01 / 1.00 / 1.00 | 2.1 / 1.6 / 1.6 | 1.33 / 1.04 / 1.03 | 1.57 |

- Real run (no fakes), defaults + psf 1.57: 12 candidates. SN 2011fe at (402, 400),
  z 170, psf_flux 43,407 (4.4 by hand: 43,867 ± 186), err_fit 183, err 329
  (corr 274, kfit 12). `uq_valid` False with flags 101 (both lobes unsupported,
  a lobe outside the stamp): the dipole put its negative lobe 457 px away, so the
  centre error is undefined, while the flux error is fine. Two pairs of rows are
  the same star found twice ((404,640)/(402,645), (707,456)/(704,462)).
- Psf width sensitivity (defaults, seed 0): σ 1.45 → ratio 0.86–0.90; 1.57 → 0.91–0.96;
  1.70 → 0.96–1.01. A bad kernel widens the difference's effective PSF.
- Measured correlation factor (variance, psf_flux) 3.2–4.3 with auto stamps, 3.7 with
  the whole image; the closed form says 1.54–1.66. `undefined_factor` 2 of 12.
- Heavy tails in the first injection runs (std 3–10 against MAD ~1) were the design:
  fakes ~28 px apart, so a 51-px stamp often held two and the fit measured the
  neighbour. With SPACING=60 (10 seeds × 30 fakes) they're gone; ~5 of 300 outliers
  remain, fakes next to a bright star's residue (blending). The 5.3 tutor notes hold
  the final table.
- Warm time per 800×800 item: 3–7 s, most of it `uq` and `xfit`; the first item
  of a run pays ~30 s of start-up.
- No xScan checkpoint ships in the repo; the plan's scoring lesson was dropped (5.4 is xLens).
