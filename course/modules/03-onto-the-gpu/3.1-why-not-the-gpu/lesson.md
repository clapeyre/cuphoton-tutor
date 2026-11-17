---
id: "3.1"
title: Why not the GPU?
question: This machine has a GPU. Why did every run so far use the CPU?
terms: [fallback]
guide: [concepts]
---

:::video v4-where-data-lives
:::

In Module 02 every receipt said `gpu_available: false`, and `auto` ran
everything on the CPU. Yet this machine has an NVIDIA GPU.

A GPU run needs two things: the hardware, with its driver, and Python
libraries built to use it. In cuPhoton those come with its `gpu` extra: CuPy
(NumPy-like arrays on the GPU) and a CUDA build of PyTorch. The course provides
two environments. The one you've used so far is cuPhoton's plain installation;
the second has the `gpu` extra.

:::your-turn what-was-missing
title: Hardware or software?
prompt: Ask the tutor for whatever evidence you need: what the machine reports about its GPU, and what each environment can use. What was missing, and how will you know the next run really uses the GPU?
:::

:::closure
found: The hardware was there all along: nvidia-smi sees the GPU and its driver. What was missing was software: the default environment has no CuPy and a CPU-only PyTorch, so nothing in it could reach the GPU, and auto fell back. In the GPU environment, the quickstarts with --require-gpu put every component on cuda, and the receipt says so.
matters: "Is there a GPU?" has two answers, one for the machine and one for the Python environment, and only the second matters to your code. Compute centres often have GPU nodes with CPU-only software stacks, or the reverse. Asking for --require-gpu turns that mismatch from a slow run into an error.
raises: Now the Module 01 chain. What changes when it runs on the GPU, and where do its results end up?
:::
