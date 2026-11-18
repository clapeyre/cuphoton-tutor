---
id: "6.1"
title: A known scene
question: What does xImage give back for a scene you know, and what tells you it's right?
terms: [bundle, reconstruction, loss]
guide: [reconstruct]
---

:::video v9-many-frames
:::

xImage reads a [[bundle]]: a folder (or an HDF5 file or Zarr store) of
named arrays. Three are required: the `images`, one per frame, all on one
pixel grid; their `variances`, pixel by pixel; and one `psfs` per frame.
`validate_bundle` checks the arrays' shapes and types before anything runs.

The [[reconstruction]] is set by a YAML file; the checkout's
`examples/ximage/` has annotated ones. It starts from the median of the
frames and improves the scene step by step. It stops after `max_iter`
steps, or earlier once a step changes the scene by less than `stop_tol`.
Its [[loss]] is how far the blurred scene is from the frames, in units of
their noise: around 1 when the scene explains the frames down to the
noise.

You'll use the guide's own example: three 64 × 64 frames of three point
sources with brightnesses 30, 50 and 20 on a faint sky, each frame blurred
by its own Gaussian PSF, 0.8, 1.0 and 1.2 pixels wide.

:::your-turn predict-scene
title: What comes back?
prompt: The tutor will validate the bundle and reconstruct it on the GPU with the guide's L2 configuration. Predict what the scene will look like next to the frames, and what the three sources' brightness will be, against the 30, 50 and 20 planted.
:::

:::slot scene
title: Frames and scene
caption: The central 48 × 48 pixels on one logarithmic scale: one frame, the median of the three, and xImage's scene.
:::

:::your-turn how-know
title: How do you know?
prompt: xImage's evaluation compares the scene with the median of the frames: a similarity score (SSIM) of 0.96, and a sharpness 3.6 times the median's. Does that show the reconstruction is right? What in this run does, and what in the receipt would you check before trusting it?
:::

:::closure
found: The sources came back sharp, a few pixels across, inside dark rings where the scene fell below the sky, and their light added up to 30.6, 50.6 and 20.4 against the 30, 50 and 20 planted. Their peak pixels read 25.5, 43.0 and 16.7, not the planted values: the scene gathers each source into a single pixel slowly, so the totals come right long before the peaks do. And the run hadn't finished: the receipt said 75 iterations of 75, with the last step's change, 7.9e-6, still above the 1e-6 stop. Allowed 500 steps, it stops by itself at 133, with the same totals, peaks a little higher (27.1, 45.6 and 17.8) but still short, and a loss of 1.54 instead of 2.97. The evaluation's similarity and sharpness compare the scene with the median of the same frames, which carries the same noise: they can't say the scene is right.
matters: A sharper image isn't a truer one; a known scene is what tells you. Before trusting a run, read its receipt: the device it ran on, whether it stopped by converging or by hitting the cap, and the loss, which should sit near 1 when the scene explains the frames.
raises: Validation passed and the receipt looked reasonable here. Would they catch a bundle where one frame or one PSF is wrong?
:::
