---
id: "0.1"
title: An image is an array of counts
question: What is a picture of the sky, as data?
terms: [pixel value, noise, exposure time, "@pixels-as-counts"]
---

:::video v0-what-changed
:::

Everything that follows starts from one fact: a picture of the sky is a grid of
numbers. Each pixel counts the photons that landed on it during the
[[exposure time]]. These are raw counts, not a rate per second. A [[source]],
a star for instance, is a bump of high counts. The [[background]] is the faint
light that reaches every pixel even where there's no source: sky glow,
moonlight, scattered light. Background is light too, and it is counted the
same way.

Light arrives one photon at a time, at random moments, so even a perfectly
steady source never gives the same count twice: the counts wobble around their
average. Counting random arrivals follows a
[Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution), and
its key property is all you need here: if a pixel expects $N$ counts, the
wobble, the [[noise]], is about

$$\sigma \approx \sqrt{N}.$$

A background of 100 counts wobbles by about ±10; a star peak of 10,000 counts by
about ±100. Astronomers call this
[shot noise](https://en.wikipedia.org/wiki/Shot_noise).

Here is a toy sky: a flat background with a few sources on it, and that noise
added.

:::slot toy-sky
title: A toy sky
caption: One source is circled; its pixel values are shown beside it.
:::

:::your-turn twice-as-long
title: Twice as long
lead: Astronomers fight for exposure time. They book telescopes by the night and stack images taken over weeks. Let's see why, using only the two facts above.
prompt: If the exposure time were twice as long, what would happen to the source's counts, to the background's, and to the noise? Would the source be easier or harder to see?
:::

:::closure
found: Doubling the exposure doubles every count, source and background alike, but the noise grows only by √2 ≈ 1.4. The signal grows faster than its noise, so the ratio between them, the [signal-to-noise ratio](https://en.wikipedia.org/wiki/Signal-to-noise_ratio_(imaging)), improves as the square root of the exposure time: $S/N \propto \sqrt{t}$.
matters: This is the reason astronomers chase exposure time, and the price is steep. To see a source half as bright with the same confidence, you need four times the exposure. It's why telescopes take long exposures, why surveys stack many nights, and why faint changes in the sky are hard to catch at all. Noise also sets the bar for the rest of this course. Whenever we later ask whether a leftover bump in an image is real, we'll be comparing it with this √N wobble.
raises: Here we changed one thing on purpose. Next come two pictures of the same sky, taken on different nights. What can differ between them?
:::
