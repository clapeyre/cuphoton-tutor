---
id: "8.3"
title: Four nights of M101
question: On real frames, how far can you trust the scene's fluxes, and what happens to something that changed?
terms: []
guide: [reconstruct, align]
---

The Pan-STARRS1 nights of M101 from Module 04 are already on one pixel
grid, with variance planes and masks. To make a bundle from them the tutor
has to decide a few things, and you should check each: every night scaled
to the same zero point, so a star has the same counts on each; the masks
turned into xImage's form (True for a good pixel); and one PSF per night,
here a Gaussian as wide as that night's seeing, from the header.

xImage returns the scene, but no variance for it and no PSF for it (the
guide says so). To know what a brightness in the scene means, you measure
it, with fakes, as in 4.4.

:::your-turn fakes
title: Fakes in the scene
prompt: The tutor will plant 24 fake stars of 2,000 counts in each of the three 2011 nights, each blurred by that night's PSF, then reconstruct a 160 × 160 cut around the supernova's position. It will measure the fakes in the scene and in the median of the frames, the same way. Predict how close each will come to 2,000, and which will scatter less. Then ask what you'd do before measuring anything real in the scene.
:::

:::slot fakes
title: Median and scene
caption: The central 80 × 80 pixels of the cut: the median of the three nights and xImage's scene, fakes included.
:::

:::your-turn supernova
title: Add the supernova's night
prompt: Now the tutor will add 2012-04-12, when SN 2011fe was bright at the centre of the cut, and reconstruct the four nights without fakes, once with L2 and once with the robust loss. Predict what each scene shows at the supernova's position.
:::

:::slot supernova
title: The supernova's position
caption: The median of the four nights, the 2012-04-12 frame alone, and the two scenes, each on its own stretch.
:::

:::closure
found: In the scene the fakes came back at 1.15 times their planted flux, scattered by 0.05; in the median of the frames, measured the same way, at 1.05, scattered by 0.16. The scene's sharpness bought a third of the scatter, but its flux scale was off by 10% against the median's, without any warning. On the 2012 night the supernova put 46,000 counts in the aperture; before it, the three nights had a few hundred at most. The L2 scene put 3,600 there, a faint smudge that was neither the supernova nor its absence, and the robust scene 400, about what was there before. The loss rose from 1.43 to 2.14, and nothing else said anything.
matters: A reconstruction is a measurement, so calibrate it: plant what you'll measure, at your settings, and use the ratio. And xImage assumes one scene that doesn't change. Something that changed between the frames is either smeared into a faint ghost or removed as an outlier, depending on the loss. To find what changed, use the chain from Modules 01 to 05; use xImage for what stays put.
raises: You've now run four kinds of cuPhoton data: images over two nights, two receivers, pump-probe traces, many frames of one scene. What does your own data look like, and where would you start?
:::
