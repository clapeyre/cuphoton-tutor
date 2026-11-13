---
id: "0.1"
title: An image is an array of counts
question: What is a picture of the sky, as data?
terms: [pixel value, noise, exposure time, "@pixels-as-counts"]
---

:::video v0-what-changed
:::

The images in this course are raw counts: the number of photons each pixel
collected during the [[exposure time]], not a rate per second. A [[source]], a
star for instance, is a bump of high counts; the [[background]] is the light in
every pixel that no source accounts for.

Light arrives one photon at a time, so the counts wobble. The size of that
wobble, the [[noise]], grows as the square root of the counts.

Here is a toy sky: a flat background with a few sources on it, and that noise
added.

:::slot toy-sky
title: A toy sky
caption: One source is circled; its pixel values are shown beside it.
:::

:::your-turn twice-as-long
title: Twice as long
prompt: If the exposure time were twice as long, what would happen to the source's pixel values, and to the background's?
:::

:::closure
found: Pixel values count light. A longer exposure gives more counts everywhere, and the noise grows more slowly than the signal.
raises: We'll compare two images of the same sky. What can differ between them?
:::
