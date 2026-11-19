# 3.1 · tutor notes

**Goal:** the learner separates "the machine has a GPU" from "this Python
environment can use it", fixes it by switching to the GPU environment, and
proves the switch with a receipt (`--require-gpu`). Probes M-AUTO-GPU.

Two environments (paths in your system prompt): `python` on the PATH is the
CPU-only one; the GPU one is called by full path. Use the GPU one from here on
for anything meant for the GPU, and say which one you're using.

## Video `v4-where-data-lives` (opens the module)
Host and device memory, real copy and xRep times for a 2048² image on this GPU
(up 2.6 ms, xRep 21.6 ms, back 4.0 ms; CPU xRep 8.8 s), crossing once vs at
every stage. It deliberately doesn't say which calls return NumPy or CuPy (3.2's
prediction) or mention queuing (3.4): don't fill those in when discussing it.

## Your turn `what-was-missing`
- Hand over the evidence they ask for, nothing more. Likely requests:
  - `nvidia-smi`: an NVIDIA GeForce RTX 4070 Ti SUPER, 16 GB, driver 615.78.
  - The default environment: `python -c "import cupy"` fails (no module);
    `torch.__version__` is `2.15.0+cpu`, `torch.cuda.is_available()` False.
  - The GPU environment: CuPy 14.1.1, PyTorch `2.13.0+cu130` with CUDA
    available, cuPhoton the same pinned version.
- When they ask to run on the GPU, run the quickstarts with the GPU
  environment and `--require-gpu`, into a new directory:
  `<gpu python> <checkout>/examples/run_quickstarts.py --require-gpu --output-dir work/03/qs-gpu`.
  Show the receipt as in 2.1 (a table figure, `work/03/3.1_receipt.png`, posted
  with `show_figure(turn_id=...)`): profile auto, require_gpu true,
  gpu_available true; xfit cupy/cuda:0, xpois cupy/cuda, xrep cupy/cuda,
  xray gpu/cuda, xscan torch/cuda; 3/3 converged (`results.xfit.metrics.converged_count`).
- Timing facts if asked: on this machine about 3 s warm. On a fresh machine the
  very first GPU run took 28 s, mostly compiling GPU code that CuPy then caches
  (`~/.cupy/kernel_cache`); 3.4 comes back to this. Don't open the timing topic
  yourself.
- **Pass:** (a) hardware present, software missing (no CuPy / CPU PyTorch in
  the default environment); (b) they looked at the new receipt and it shows the
  GPU was used, in a reply of theirs after you show it (don't show, settle
  and reveal in one go). Settle as soon as both are there: no extra "say it in one
  sentence", no field names. Mention `--require-gpu` as the guard yourself if
  they didn't.
- Settle, then `reveal("3.1")`.
