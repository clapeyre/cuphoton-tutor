# 3.2 · tutor notes

**Goal:** the learner directs the chain onto the GPU, sees the same answers,
and learns where each stage's result lives. Probes M-HOST-DEVICE.

Source: docs/guide/first-difference.qmd, "Run it on a GPU", and
docs/guide/concepts.qmd, "Dtype and device". Use the GPU environment.

## Your turn `predict-move` (prediction)
- Accept any reasoned predictions (fluxes; NumPy or CuPy per stage).
- Run `work/03/chain_gpu.py` with the GPU environment: the Module 01 chain
  (the guide's code, as in `work/01/`) once with `backend="cpu"` and once with
  `backend="cupy"` for xRep and xPois, and xFit given CuPy arrays
  (`cp.asarray(...)` on cutouts, variance, start, mask). Run each twice and
  report the second (warm) run; synchronize the GPU before stopping each timer.
  Record the result type of each stage (`type(x).__module__`).
- Figure `work/03/3.2_chain.png`: a table, one row per stage: backend that ran
  (read from the run, never typed in: xRep's result carries `.backend`; xFit's
  CuPy result shows it ran on the device; xPois returns NumPy on both paths, so
  write "cupy (named; ran without error)" for it, and say why if asked), result type (NumPy/host or CuPy/device), CPU time, GPU time; and the two
  fluxes ± error from each run. `show_figure(slot="gpu-chain")`.
- Facts (real run, pinned commit, this machine, warm):

  | stage | GPU result type | CPU time | GPU time |
  |---|---|---|---|
  | xRep `reproject_masked_array` | NumPy (host) | 92 ms | 7.8 ms |
  | xPois `solve_constant_kernel` | NumPy (host) | 22 ms | 5.6 ms |
  | xFit `fit_single_sources` | CuPy (device) | 1.8 ms | 15 ms |

  Fluxes 12234 ± 114 and 4140 ± 71 on both; residuals agree to 2e-9. xFit is
  slower on the GPU here: two 21×21 stamps are far too little work. Don't make
  timing the topic; if they ask, say 3.4 is about it.
- Settle `predict-move` on the comparison with their prediction.
- If they want float32 (M-FLOAT32), don't endorse or refuse it: ask what dtype
  they expect back from xRep and xPois when fed float32, then run it and print
  each stage's result dtype. xRep and xPois compute and return float64; xFit
  keeps its input's dtype (docs/guide/concepts.qmd, "Dtype and device"). Whether
  float32 is accurate enough is then a measurement: compare fluxes with the
  float64 run against their error bars.

## Your turn `where-it-lives` (checkpoint)
- **Pass:** aligned image and difference on the host (NumPy), fluxes on the
  device (CuPy); and for a following GPU stage, the host results would be
  copied back to the device (cost), which is what the `_device` functions
  avoid (`reproject_array_device`, `solve_constant_kernel_device`,
  `fit_dipoles_device`).
- If they say "it ran on the GPU so it's on the GPU" (M-HOST-DEVICE): ask what
  type the aligned image is, and let them see `type(...)`.
- Settle, then `reveal("3.2")`.
