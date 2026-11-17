---
id: "9.1"
title: A map of cuPhoton
question: Which part of cuPhoton takes your data, and what would you check on its first run?
terms: []
guide: [index]
---

Each part of cuPhoton takes a particular kind of data, and each chapter of
the user guide starts from a task. The guide is at
[nvidia.github.io/cuPhoton](https://nvidia.github.io/cuPhoton/main/); every
chapter also lives in the checkout under `docs/guide/`.

**What you've run.**

**Images over time** (Modules 01–05). Read FITS images on the CPU or
straight to GPU memory (Core, xDR); align one to another's grid (xRep);
match blur and subtract (xPois); measure what's left (xFit); score
candidates as real or bogus with a network trained on your own cutouts
(xScan). The **transient chain** ships all of it as one pipeline, with an
error budget for every flux, and **xLens** watches its runs. Chapters
"Read FITS images" to "Monitor".

**Two receivers** (Module 06, **xBeam**). What two recordings of one
source share, and at what delay: arrays, HDF5 or VDIF radio recordings.
Chapter "Correlate".

**Pump and probe** (Module 07, **xRay**). Laser-on and laser-off X-ray
detector frames, reduced to traces and fitted as damped oscillations, row
by row on the GPU. Chapter "X-ray traces".

**Many frames, one scene** (Module 08, **xImage**). One sharp scene from
frames with their own PSF and noise: telescopes, microscopes, adaptive
optics. Chapter "Reconstruct".

**What you haven't.** **Scale-out** spreads whole work items over many GPUs
and nodes, under MPI or Dragon: image pairs, cutouts, detector tiles
(chapter "Scale"). By the time you need it, you'll know which work items
are yours; the habits of 3.4 (time the whole job, second run, say what
was timed) carry over.

:::your-turn your-data
title: Your work
prompt: Tell the tutor about your work: what you measure, with what instrument, what the data looks like (shape, format, how much of it), and what you want out of it. Which part of cuPhoton would you start from, or does none fit? What would you check on its first run? Ask anything about any part.
:::

:::closure
found: Each part of cuPhoton takes a particular kind of data, and its guide chapter starts from a task, not from the library. Whatever the part, the first run should leave evidence you can check: a receipt naming what ran and where, a summary of what was measured, and an error bar you've tested with something whose answer you know. In every module, the run that looked fine and wasn't said nothing about it: a kernel that didn't fit, a delay that wrapped, rows that recorded nothing, a star that wasn't there.
matters: The library will keep growing; these habits don't depend on its version. Know what a step should give back before it runs, read the receipt rather than the absence of errors, check the noise model against the data, and plant something you can find.
raises: What would you ask an agent to show you before you trust its first run on your data?
:::
