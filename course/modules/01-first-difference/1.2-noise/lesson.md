---
id: "1.2"
title: How noisy is each pixel?
question: How noisy is each pixel, and how do we tell cuPhoton?
terms: [gain, variance plane, error bar]
guide: [concepts]
---

In 0.1 the noise on a pixel that expects N counts was about √N, so its
[variance](https://en.wikipedia.org/wiki/Variance), the square of the noise, is
about N. Real files store *data numbers* (DN) rather than photons; the
detector's [[gain]] $g$, recorded in the header, says how many electrons make
one DN. Converting back and forth, the variance of a pixel in DN² is its value
divided by the gain:

$$\sigma^2_{\mathrm{DN}} = \frac{\text{value}}{g}.$$ (A full noise model adds the detector's read noise; for
this bright synthetic sky we can leave it out.)

cuPhoton never guesses the noise: every call takes it explicitly, as a
[[variance plane]]. That is an image with the same shape as the data, holding
one number per pixel: how much that pixel's value would wobble if the same
exposure were repeated many times. It is not the spread of the image's values;
a star and the empty sky beside it have very different variances.

The variance plane does two jobs. It sets how much each pixel counts in every
fit (noisy pixels count less), and it is where every [[error bar]] at the end
comes from.

:::slot variance
title: An image and its variance plane
caption: The target, and its variance plane computed as value / gain.
:::

:::your-turn times-four
title: Variance × 4
prompt: Suppose we multiplied the whole variance plane by 4, claiming every pixel is noisier than it really is. When we measure a source's flux at the end, what happens to the flux, and what happens to its error bar? We'll test your answer in 1.6.
:::

:::closure
found: The noise goes into cuPhoton as a variance plane: one number per pixel, built from a noise model (value / gain here), not from the spread of the image's values. You've made a prediction about scaling it; 1.6 runs the test.
matters: Every weight in every fit and every error bar at the end come from this plane. A pipeline can run perfectly on a wrong variance plane, and nothing will warn you, which is why we choose it on purpose rather than accept a default.
raises: Now both images carry their noise. Next, putting them on one grid.
:::
