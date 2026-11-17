---
id: "1.1"
title: The sample pair
question: What will we test the pipeline on, and how will we know its answer is right?
terms: [FITS file, injected source, flux]
guide: [first-difference]
---

To trust a pipeline, first run it on data where you already know the answer.
Our pair comes from cuPhoton's own tutorial: two synthetic pictures of the same
patch of sky, a sharper **reference** and a blurrier **target** taken with a
slightly different camera, pointing and sky. Two changes were put into the
target on purpose: they are [[injected source|injected]], so we know exactly
where they are and how much light each one adds, its [[flux]]. We'll keep that
answer key closed until the pipeline has given its own answer.

Each image is stored as a [[FITS file]], the standard file format of astronomy:
a **header** of named metadata (where the telescope pointed, the pixel scale,
the detector's settings) followed by the pixel values themselves.

:::slot pair
title: The sample pair
caption: Reference (left) and target (right), as read from their FITS files.
:::

:::your-turn two-shapes
title: Two shapes
lead: Reading the files gives the reference as 300 × 300 pixels and the target as 256 × 256.
prompt: Why can two pictures of the same sky have different shapes? What does that mean for subtracting one from the other?
:::

:::closure
found: The two images come from different pixel grids: different detectors, pixel sizes, pointing and rotation. Pixel (100, 100) in one isn't the same patch of sky as pixel (100, 100) in the other, so nothing can be subtracted until one image is put on the other's grid.
matters: In Module 00 alignment fixed a small shift. On real data the grids can differ in every way at once, and only the header tells you how. That is why the pipeline reads headers as carefully as pixels.
raises: Before aligning, there's something cuPhoton needs that the pictures don't show: how noisy each pixel is.
:::
