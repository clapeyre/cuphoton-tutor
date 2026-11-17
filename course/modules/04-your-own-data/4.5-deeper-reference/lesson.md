---
id: "4.5"
title: A deeper reference?
question: Would stacking more nights into the reference let you see fainter changes?
terms: [stack, seeing]
---

Your reference is one 40-second exposure. Pan-STARRS1 looked at this patch of
M101 two more times before the explosion: again on 22 April 2011, a quarter
of an hour later, and on 11 May. They're in `data/` as `reference-b` and
`reference-c`, with their own variance and mask planes.

Combining several images into one is called a [[stack]]. In cuPhoton it's two
steps. xRep puts every image on one pixel grid (`reproject_stack`, or
`reproject_masked_array` to carry each image's variance and mask along). It
doesn't combine them: how to add up the pixels is your choice. This is the
"stack images" half of the guide's chapter on aligning.

:::your-turn recipe
title: Your recipe, and your prediction
prompt: How should the three nights be combined into one reference? Say what to do with a pixel that one night doesn't cover, and what the stack's variance is. Then predict what the stack buys you, using the 4.4 injection test as the measure. How much fainter will it reach?
:::

:::slot stack
title: Three nights and their stacks
caption: Top, the usable pixels of each night, with its seeing (the width of a star, as a FWHM in pixels), and how many nights cover each pixel. Bottom, z for the single reference and for each stack; circles mark hotspots outside the single night's usable area.
:::

:::your-turn what-it-bought
title: What it bought
prompt: Compare the single reference with the stacks, and the injection numbers. What did stacking buy on this pair, what did it cost, and why didn't it do what you predicted?
:::

:::closure
found: Almost no depth. With all three nights, the fakes of 1,000 counts had the same median flux error (81 counts) and the same number came back (30 of 75) as with one. The reason is where the difference's noise comes from. The matching kernel blurs the reference, which averages its noise down, so the reference supplied only 5% of the difference's variance. The target's own noise is the rest, and stacking references can't touch it. What the stack did buy is area. The nights' chip gaps differ, so 86% of the image became usable instead of 70%. But that new area is covered only by 11 May, the blurriest night (4.65 pixels, against the target's 3.59). All 11 hotspots found there are residues on stars, positive and negative: a reference blurrier than the target can't be matched by blurring it. Two shortcuts went wrong silently. A plain mean lost area (57%), because a pixel missing in any night was lost. Keeping the single night's variance threw the new area away and found fewer fakes.
matters: More data making a better reference is a prediction, and on this pair it was mostly wrong. Only the injection test said so: every stack ran without complaint. The same arithmetic says when stacking pays. Stacking N nights divides the reference's share of the noise by N. Here that share was 5%, so three nights could gain at most 2%. Where the reference supplies half the noise, as it does when it is no sharper than the target and about as deep, three nights cut the difference's noise by 18% and reach about 0.2 magnitudes fainter; ten nights, 26% and 0.3 magnitudes. That is why surveys build deep references from many nights. So measure the share before you stack. Then choose the nights by seeing, never blurrier than the target, put them on one grid and one flux scale, weight them, carry the variance, and check where the coverage changes, because a stack can have a different blur in each patch.
raises: The stack's new candidates were all bogus, and so were three of 4.3's four. Sorting them by eye works for a handful. Could something sort them for you?
:::
