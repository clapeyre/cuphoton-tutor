---
id: "3.2"
title: Move the chain to the GPU
question: What changes when the Module 01 chain runs on the GPU, and where does each result end up?
terms: [host memory, device memory]
guide: [concepts]
---

A GPU has its own memory, separate from the computer's main memory. In GPU
programming the computer is the **host** and the GPU is the **device**: data
has to be copied from [[host memory]] to [[device memory]] before the GPU can
work on it, and back again before ordinary code can use the result. NumPy
arrays live on the host; CuPy arrays, which look and behave almost the same,
live on the device.

Moving the chain to the GPU means asking each stage for the `cupy` backend.
How each stage hands its result back is a design choice that cuPhoton makes
stage by stage.

:::your-turn predict-move
title: Before it runs
prompt: Tell the tutor to run the Module 01 chain (align, match and subtract, measure) on the GPU. Before it runs, predict: will the fluxes change? And after each stage, will the result be a NumPy array on the host or a CuPy array on the device?
:::

:::slot gpu-chain
title: The chain on the GPU
caption: Each stage: the backend that ran, the type of its result, and its time, beside the CPU run.
:::

:::your-turn where-it-lives
title: Where does it live?
prompt: After the GPU run, where do the aligned image, the difference image and the fluxes live? What would that mean if the next step were another GPU stage?
:::

:::closure
found: The fluxes didn't change: +12,234 ± 114 and +4,140 ± 71 DN, matching the CPU to about a billionth. xRep and xPois ran on the GPU but handed their results back as NumPy arrays on the host; xFit, given CuPy stamps, returned CuPy arrays on the device. xRep's result says the cupy backend ran. xPois hands back NumPy on either path, so for it the evidence is that the named cupy backend ran without error: a GPU-only backend fails loudly when it can't run (2.3).
matters: A stage that copies its result back to the host is convenient, but a chain of such stages copies the image across and back at every step, and for big images the copies can cost more than the arithmetic. cuPhoton offers `_device` versions that keep results on the GPU for exactly that reason. Knowing where each result lives tells you where the time goes.
raises: The files themselves still go through the CPU first. Can we read an image straight onto the GPU?
:::
