# 2.6 · tutor notes

**Goal:** the learner writes their own "after every run, check…" list, and
directs one complete small run in one instruction (module exit, O3).

## Your turn `after-every-run` (module exit)
- First their list, in their words. Compare with docs/troubleshooting.md ("A
  GPU run used CPU", "Results differ across devices", "A command rejected the
  input"). Expect at least: backend/device/dtype from the receipt against the
  request; exit status (and stderr, not just stdout: see 2.2); fit status or
  convergence counts; a plot; a new output directory per run. Discuss what's
  missing with one question each; don't dictate items.
- Then the single instruction. **Pass:** it names a component (e.g.
  `--component xpois`), the hardware on purpose, a new output directory, and
  the evidence expected back. The runner has no backend flag: `--profile auto`
  (prefer a GPU, fall back visibly) or `--profile cpu`, plus `--require-gpu`
  to fail without one. "GPU" or "cupy" maps to `--profile auto --require-gpu`;
  say so in one line when you run it, then report the backends the receipt
  shows. Run it exactly as instructed
  (`python <checkout>/examples/run_quickstarts.py --component <c> --profile <p> --output-dir work/02/<new>`)
  and report against *their* list, item by item, nothing more. If what they
  asked for can't run here (e.g. `--require-gpu`), let it fail and let them read
  the failure.
- Write their final list to `work/02/standing-instruction.md`, in their words,
  and say it's there. It's the standing instruction for Modules 03–04.
- Settle with the list as the summary, then `reveal("2.6")`.
