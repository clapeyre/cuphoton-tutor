---
id: "6.1"
title: A map of cuPhoton
question: Which part of cuPhoton takes your data, and what would you check first?
terms: []
---

Each part of cuPhoton takes a particular kind of data. The guide's chapters
start from the task, so find the line that sounds like your work, and look at
what it takes in. The guide is at
[nvidia.github.io/cuPhoton](https://nvidia.github.io/cuPhoton/main/); every
chapter also lives in the checkout under `docs/guide/`.

**The chain you've used.** Read FITS images, on the CPU or straight to GPU
memory (Core, xDR: 2-D FITS images; chapter "Read FITS"). Align one image to
another's grid (xRep). Match blur and subtract (xPois). Measure many cutouts
at once (xFit). Score candidates as real or bogus with a neural network you
train on your own labelled cutouts (xScan: cutout triplets; chapter
"Classify").

**The chain, shipped.** The same stages as one pipeline that runs on a
survey's images and writes a catalogue with an error budget for every flux
and position (the transient chain: FITS pairs with WCS and variance planes;
chapters "Run the transient chain" and "Uncertainty").

**Beyond the sky.**

**xImage** builds one sharp image from many frames of the same scene, each
with its own blur and noise: microscopy, adaptive optics, lucky imaging.
It takes frame stacks with a variance and a PSF per frame (chapter
"Reconstruct").

**xRay** turns pump-probe X-ray detector frames, laser on and laser off,
into a trace over delay, and fits it as damped oscillations (synchrotron
and XFEL beamlines; HDF5 frame stacks; chapter "X-ray traces").

**xBeam** measures what two recordings of one source share, and at what
delay, frequency by frequency: two microphones, two radio telescopes, a
VLBI correlator. It takes sampled signals, from arrays, HDF5 or VDIF
recordings (chapter "Correlate").

**Around any of them.**

**Scale-out** spreads whole work items over many GPUs and nodes, under MPI
or Dragon (chapter "Scale").

**xLens** records what your own code measured in every run and shows it in
a dashboard: Module 02's receipts, at batch scale. It needs no GPU (chapter
"Monitor").

:::your-turn your-data
title: Your data
prompt: What does your lab's data look like (what instrument, what shape and format, how much of it), and what do you want out of it? Which part of cuPhoton would you start from, and what would you check on its first run? Ask the tutor anything about any part.
:::

:::closure
found: Each part of cuPhoton takes a particular kind of data, and its guide chapter starts from a task, not from the library. Whatever the part, the first run should leave evidence you can check: a receipt naming what actually ran and where, a summary of what was measured, and an error bar you have tested with something whose answer you know.
matters: The library will keep growing; these habits don't depend on its version. Know what a step should give back before it runs, read the receipt rather than the absence of errors, check the noise model against the data, and plant something you can find.
raises: What would you ask an agent to show you before you trust its first run on your data?
:::
