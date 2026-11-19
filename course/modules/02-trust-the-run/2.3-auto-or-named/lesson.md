---
id: "2.3"
title: Let it choose, or name it?
question: What does cuPhoton do when you let it pick the backend, and when you name one it can't use?
terms: [auto, fallback]
guide: [concepts]
---

Most cuPhoton calls take a `backend` argument. Its default is [[auto]]: try the
GPU backends in a fixed order, take the first one that is installed and can
reach a GPU, and end on the CPU. A backend you name yourself is different: if
it can't run, the call fails instead of [[fallback|falling back]].

The names, from cuPhoton's concepts guide:
`cpu` (called `numpy` in xFit) runs on the CPU with NumPy; `cupy` needs an
NVIDIA GPU and the CuPy library; `torch` (xRep only) runs PyTorch, on a GPU or
on the CPU. `auto` never picks the specialised `cutile` and `native` GPU
backends: those you request by name.

This machine has a GPU, but the cuPhoton environment the tutor runs in has no
CuPy and a CPU-only build of PyTorch, the way many laptops and fresh installs
are set up.

:::your-turn four-backends
title: Four requests
prompt: The tutor will call xRep on a small image four times, with backend set to auto, cpu, torch and cupy. For each, predict what happens: which backend actually runs, or does it fail? Then ask it to run them.
:::

:::your-turn laptop
title: On a laptop
prompt: On a laptop with no usable GPU, you ask your agent to run a stage with the cupy backend, and then with auto. What does each do, and how would you find out which one ran where?
:::

:::closure
found: auto ran on the CPU and reported success; cpu ran on the CPU; torch ran too, on the CPU; cupy failed at once, naming the package to install. Naming a backend isn't naming a device: torch ran on the CPU without a word. Only a GPU-only backend like cupy fails loudly when there's no GPU, and auto never fails for want of one. The result names the backend, not the device, so where it ran comes from a receipt's device field or from what the environment can reach (2.1's hardware record).
matters: auto is the right default for code that must run anywhere, and the wrong one for anything where the GPU matters: a timing, a GPU-correctness check, a production job you sized for a GPU. Then you name a GPU-only backend, or make the run demand a GPU, so a missing GPU becomes an error you see instead of a slowdown you don't.
raises: The command line has its own receipts. Which choices does one record?
:::
