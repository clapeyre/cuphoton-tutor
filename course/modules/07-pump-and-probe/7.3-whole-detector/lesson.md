---
id: "7.3"
title: Every row on the GPU
question: A fit of every detector row says 2,048 fits and no failures. Is every fitted row a measurement?
terms: [dispersion]
guide: [xray-traces]
---

Each row of the detector catches X-rays scattered at a slightly different
angle, so each row watches a different wave of motion through the crystal.
Their frequencies differ: a crystal's ringing frequency changes with the
wave's length, and plotted across the detector it traces the crystal's
[[dispersion]] curve. That curve is what a beamline scientist is after,
so xRay fits every row.

`cuphoton xray detector-artifacts` does it on the GPU, in tiles of 16 × 16
pixels. For each detector row of each tile it sums the tile's columns and
the rows within 3 pixels (`--integrate`), smooths the trace along the delay,
fits it, and writes the result to every column of the tile. It writes
arrays per pixel (each mode's frequency and amplitude) and two records of
the run: `manifest.json` (inputs, settings, counts of fits and failures)
and `fit_status.npy`, one code per pixel: 0 not processed, 1 fitted,
2 skipped, 3 failed. `detector-mask` plans the run on the CPU first.

:::your-turn first-look
title: Before it runs
prompt: The tutor will fit every row of a 256-row × 128-column detector on the GPU, at order 4: 2,048 fits. Before it runs, what will you look at to decide whether the run is good?
:::

:::slot rows
title: Every row
caption: Per detector row, from left: the laser-off counts it recorded, the fitted frequency of its strongest oscillating mode (blue; the planted curve dashed), and that mode's amplitude.
:::

:::your-turn every-row
title: Is every fitted row a measurement?
prompt: The manifest says 2,048 fits and 0 failures, and every pixel has status 1, fitted. Look at the three panels together. Is every fitted row a measurement? What would you change, and what do you expect after the rerun?
:::

:::slot fixed
title: After the change
caption: The same three panels from the rerun.
:::

:::closure
found: The fit followed the planted dispersion curve, to 0.002 THz on the median row. Rows 120 to 123 recorded nothing, 0 counts in every frame, and still came back fitted, with frequencies of 0.996 to 1.003 THz: the neighbours' values, summed in by the 3-row integration. The manifest counted them as fits and none as failures. With `--exclude-y 120:124` they became status 2, skipped, and the manifest counted 32 skipped fits. The rows within 3 of the dead band still sum its zeros: their frequencies stayed right, but their amplitudes stayed low, down to 55% of the rest.
matters: A status code says what the code did with a row, not what the row recorded. Integration and smoothing make every row's trace partly its neighbours', so a fitted value can come from somewhere else. Check what each row recorded before trusting its fit, exclude the dead rows, and treat amplitudes near an exclusion with care. And set the order yourself: at the default, 30, rows came back with up to 6 modes, where order 4 gave one mode and the constant.
raises: xRay follows one signal through time at every row. What if instead you have many pictures of one scene, each blurred differently, and want the sharpest scene they agree on?
:::
