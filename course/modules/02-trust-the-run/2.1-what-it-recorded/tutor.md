# 2.1 · tutor notes

**Goal:** the learner predicts, then reads, what a run records about itself,
and answers "where did it run" from the receipt, not from "no error".

Work in `work/02/`. Run cuPhoton's own runner, from the checkout:
`python <cuPhoton checkout>/examples/run_quickstarts.py --profile cpu --output-dir work/02/qs-cpu`
(about 3 s, mostly start-up). Use a plain directory name for this first run:
2.2 is about what happens when you reuse it, so don't add suffixes "to be safe".

## Your turn `predict-record` (prediction)
- Collect their list before showing anything. Accept any list; ask "anything
  else?" once at most.
- Then run it, and fill the slot: `work/02/receipt_table.py` reads
  `work/02/qs-cpu/summary.json` and renders `work/02/2.1_receipt.png`, a clean
  table image: top lines `profile`, `require_gpu`, `status`,
  `hardware.gpu_available`; then one row per component with
  `requested_backend` (blank if not recorded), `backend`, `device`, `dtype`.
  `show_figure(slot="receipt")`.
- In your reply, tick their list off against the file (docs/quickstarts.md,
  "Output contract": profile, resolved backend/device/dtype per component,
  hardware, seeds and shapes, artifact paths). Settle on the comparison.

Facts (real run, pinned commit, this environment):

| component | requested_backend | backend | device | dtype |
|---|---|---|---|---|
| xfit | numpy | numpy | cpu | float64 |
| xpois | cpu | cpu | cpu | float64 |
| xrep | – | cpu | cpu | float64 |
| xray | – | cpu | cpu | float64 |
| xscan | – | torch | cpu | float32 |

`profile cpu`, `require_gpu false`, `status ok`, `seed 20260701`,
`hardware.gpu_available false` (CuPy is not installed in this environment, and
PyTorch is a CPU build, even though the machine has a GPU: `nvidia-smi` sees
it). Backend and device live inside each `results.<component>`, not at the top.
xFit metrics: 3 candidates, 3 converged.

## Your turn `where-xfit` (checkpoint)
- Probes M-AGENT-SUCCESS. **Pass:** the answer comes from what the receipt
  records ("the receipt says xFit ran on the CPU"), not from "it didn't error"
  or "we asked for CPU". Any wording; don't ask for field names.
- If they answer "on the CPU because we asked", ask how they'd know if the
  request had been ignored.
- Optional, if they look at xScan: "Validation ROC AUC is 1.0. Is this
  classifier any good?" One epoch on 8 samples; AUC on so few is meaningless
  (M-AUC-CERTAINTY). "It ran" isn't "it works" for metrics either.
- Settle, then `reveal("2.1")`.
