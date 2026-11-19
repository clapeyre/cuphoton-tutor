---
id: "0.3"
title: Why not just subtract?
question: If we subtract the reference from the target, pixel by pixel, do only the real changes remain?
terms: [difference image, alignment, residual, "@imaging-difference"]
---

"Subtract" means target minus reference at each pixel. Positive means brighter
in the target.

:::your-turn predict-plain
title: Before we subtract
prompt: What level will the empty parts of the sky sit at, and what will you see around each star?
:::

:::slot raw-difference
title: Plain subtraction
caption: Target minus reference, nothing fixed.
:::

Now we fix only the pointing. [[Alignment]] puts both images on the same pixel
grid, so the same star sits on the same pixel.

:::slot aligned-difference
title: Aligned, then subtracted
caption: Each spot is lettered.
:::

:::your-turn your-plan
title: Your plan
prompt: Our goal is a difference image where only the real changes remain. Which steps would you apply before subtracting, in what order, and what does each remove? And what would you do with what's left?
:::

:::closure
found: Plain subtraction leaves the night's differences everywhere: a raised floor, and positive and negative lobes around every star. Each observing-condition difference needs its own fix before subtracting: align, then match the background and the blur. Even then, what survives is a real change, a mistake in the matching, or noise, and its shape and size are your first clues to which.
matters: Your plan is the standard recipe of difference imaging, the one sky surveys run on every image. Its weak point is the one you found: a slightly wrong match leaves residuals that look like signal. Much of the judgment this course asks of you is about telling those two apart.
raises: cuPhoton has a stage for each step of this plan. Which is which?
:::
