# 2.3 · tutor notes

**Goal:** the learner predicts and sees auto versus named backends on a host
without a usable GPU, and states the rule. Probes M-AUTO-GPU,
M-EXPLICIT-FALLBACK, M-BACKEND-NAMES.

## Your turn `four-backends` (prediction)
- Ask for all four predictions; write them back in one line before running.
- Run the loop from docs/guide/concepts.qmd ("Backends") as
  `work/02/backends.py` (64×64 random image, half-pixel shift,
  `reproject_masked_array(..., backend=b)`, print `result.backend` or the error).
- Facts (real run, pinned commit, this environment):
  ```
  backend='auto': ran cpu
  backend='cpu': ran cpu
  backend='torch': ran torch
  backend='cupy': Requested backend is unavailable: cupy. Run 'uv sync --extra gpu' for development or install 'cuphoton[gpu]'.
  ```
- Show the output in a code block and compare with their predictions. If they
  expected torch to fail ("no GPU"), point out it runs on the CPU too. If they
  ask why the GPU wasn't used: `nvidia-smi` sees it, but the environment has
  no CuPy and a CPU-only PyTorch (`hardware` in 2.1's receipt). Show
  `nvidia-smi` if they ask.
- Settle on the comparison.

## Your turn `laptop` (checkpoint)
- **Pass:** cupy fails loudly (an error naming the missing package); auto
  succeeds on the CPU, and only the receipt tells you so.
  Bonus, not required: auto never picks `cutile` or `native`; the CPU backend
  is `numpy` in xFit and xBeam and `cpu` in xRep and xPois.
- If they say auto "warns": it doesn't; ask where they'd look.
- Settle, then `reveal("2.3")`.
