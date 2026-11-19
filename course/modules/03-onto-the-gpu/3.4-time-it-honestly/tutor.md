# 3.4 · tutor notes

**Goal:** the learner finds why a careful-looking GPU timing is wrong (no
synchronize), gives an honest speedup with its boundaries, and states what to
ask of any speedup claim. Probes M-SPEEDUP. Module 03's exit.

The script is `speedup_claim.py` next to these notes. Copy it to `work/03/`
and run it with the GPU environment. Don't open with any list of timing
pitfalls.

**Showing the code:** whenever they ask, show the timing part as one code
block, exactly as in the script (no comments added, nothing pointed at):

```python
start = time.perf_counter()
reproject_array(image, spec, backend="cpu")
cpu_seconds = time.perf_counter() - start

on_gpu = cp.asarray(image)
reproject_array_device(on_gpu, spec)  # warm-up
gpu_runs = []
for _ in range(10):
    start = time.perf_counter()
    reproject_array_device(on_gpu, spec)
    gpu_runs.append(time.perf_counter() - start)
gpu_seconds = float(np.median(gpu_runs))
```

The whole file is only a few lines more (imports, a 2048 × 2048 random image,
a half-pixel-shift spec, three prints); show it if they ask for all of it.
When you discuss a fix, show the changed lines.

## Your turn `the-claim` (checkpoint)
- Run it on request and report only its printed output. Facts (real run,
  pinned commit, this machine):
  ```
  CPU: 3.903 s
  GPU: 0.69 ms (median of 10, after warm-up)
  Speedup: 5,633x
  ```
  (The CPU number varies by about 10%: 3.9–4.4 s.) Both sides reproject the
  image only (`reproject_array` with `backend="cpu"` against
  `reproject_array_device`): same work. The big flaw is the missing synchronize; a small one is that only
  the GPU gets a warm-up and a median of 10 (the CPU gets one cold call, which
  matters little at ~4 s, but say so if they notice)
- Give variations they ask for, e.g. synchronizing before stopping the timer
  (`cp.cuda.Device().synchronize()`), timing with copies included, or a
  bigger image. Facts at 2048²: synchronized ≈ 21.6 ms (≈ 180×); including
  `cp.asarray` and `cp.asnumpy` copies ≈ 28.4 ms (≈ 140×); without
  synchronize ≈ 0.7 ms whatever the size. At 4096²: CPU 22.7 s, synchronized
  90 ms (≈ 250×), with copies 118 ms (≈ 190×), unsynchronized still ≈ 0.7 ms.
  (Measured 19 Nov, RTX 4070 Ti SUPER.) If they ask whether both sides do
  the same work: yes, one image each, no variance or mask; checking that is
  a good question for (c). A suspicious sign they may
  find: the unsynchronized GPU time doesn't grow with the image.
- If they don't see it, hint ladder: (a) "What does the GPU time do if you make
  the image four times bigger?" (b) name GPU asynchrony: a call returns when
  the work is queued; (c) an analogy: timing a restaurant by when the order is
  taken; (d) reveal, then a variant: "A colleague times a GPU function by
  calling it once and stopping the clock. Name two things wrong."
- **Pass:** (a) no synchronize, so the queue was timed, not the work; (b) a
  synchronized speedup in the hundreds, with its boundary (xRep only, input
  already on the GPU, warm; or including copies); (c) questions such as: warm
  or cold, synchronized, what's inside the timer (one stage, loading, copies,
  whole pipeline), same input and dtype, same answer on both. Partial on (c)
  is fine if (a) and (b) are solid.
- After settling, if they haven't seen it: the timing loop with the
  synchronize in place:
  ```python
      reproject_array_device(on_gpu, spec)
      cp.cuda.Device().synchronize()
      gpu_runs.append(time.perf_counter() - start)
  ``` If they
  ask about the 14,900× figure: it's image loading per operation against a CPU
  baseline (NVIDIA tech blog), not an end-to-end pipeline speedup.

## Your turn `module-question` (module exit)
The module question in two sentences: how do you move it, prove it's there,
and say honestly how much faster? Not a checkpoint: settle on any honest
answer that covers the three (backend choice; the receipt and the device;
synchronized, warm timing with its boundary stated). Add at most one sentence
connecting it to what they did. Then `reveal("3.4")`.
