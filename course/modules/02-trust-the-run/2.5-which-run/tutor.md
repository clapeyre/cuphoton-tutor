# 2.5 · tutor notes

**Goal:** the learner identifies a silent GPU→CPU fallback from receipts alone,
says what in the receipts shows it, and names `--require-gpu`.

## On open: nothing visible
Don't put anything on the page. Prepare the three receipts quietly in
`work/02/which-run/`, so they're ready when asked:
- **A, the GPU run:** `gpu-require-gpu-summary.json` next to these notes. A
  real `--require-gpu` run on a GPU machine (RTX 4070 Ti SUPER, CUDA 13):
  `profile auto`, `require_gpu true`, xfit cupy/cuda:0, xpois cupy/cuda,
  xrep cupy/cuda, xray gpu/cuda, xscan torch/cuda, `gpu_available true`.
- **B, the silent fallback:** made live in this environment, into a new
  directory: `python <checkout>/examples/run_quickstarts.py --output-dir work/02/qs-auto`
  (default profile auto). Exit 0, status ok, `profile auto`, `require_gpu false`,
  `gpu_available false`, numpy/cpu throughout (xscan torch/cpu).
- **C, the decoy:** the `--profile cpu` run from 2.1 (`work/02/qs-cpu/summary.json`).
  Identical to B except `profile`.
Copy them as `run-1.json`, `run-2.json`, `run-3.json` in a shuffled order and
write the mapping to `work/02/which-run/.key` (never show it, never name the
files after their origin).

## Your turn `which-run` (checkpoint)
- Hand over what they ask for: a whole receipt in a code block, chosen fields
  side by side, or a comparison table figure. Don't offer a list of fields to
  look at. Don't point at the deciding field.
- **Pass:** all three: (a) B's label; (b) the evidence, in any words: it ran
  on the CPU, found no usable GPU, and had asked for the best available
  (auto) rather than the CPU; (c) requiring the GPU (`--require-gpu`, or
  "make it fail if there's no GPU"). Don't ask for field names. "Ask for
  backend=cupy" isn't (c) here: the quickstart runner has no backend flag
  (2.6). Ask how they'd make a profile-auto run fail when there's no GPU,
  and settle only when they say it, not after you name `--require-gpu`.
- Common wrong answers: A ("its status looks the same": check devices);
  C (right symptom, but it asked for the CPU); "compare the metrics" (they
  match to ~1e-9 across devices: `max_absolute_parameter_error` 4.4959e-10 in
  every run).
- Hint ladder: (a) "Which fields say where each component executed?" (b) "Do
  any two receipts differ in `hardware`?" (c) "Which one *asked* for the GPU
  and didn't get it, and which never asked?" (d) reveal, then a variant: "A
  fourth receipt says `profile auto`, `require_gpu true`, status failed. What
  happened?" (it demanded a GPU, found none, and stopped:
  `RuntimeError: xfit has no usable CUDA backend`, verified here).
- Settle, then `reveal("2.5")`.
