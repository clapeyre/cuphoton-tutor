---
id: "4.2"
title: Run it
question: Run the chain on the real pair. What comes out?
terms: [difference image, hotspot]
---

You've decided how to handle the grid, the noise and the masks. Now direct
the run: the whole chain, on the GPU, in one instruction, the way you would
hand it to an agent. Your standing instruction from 2.6 applies.

:::your-turn direct-run
title: Your instruction
prompt: Give the tutor one instruction for the whole run: what to use for the variance and the masks, which stages to run (or skip), the backend, where the results go, and the evidence you want back.
:::

:::slot overview
title: The two nights and their difference
caption: Reference, target, and the difference divided by its noise.
:::

:::your-turn what-came-out
title: What came out?
prompt: Look at the difference. What happened to the galaxy, and what stands out?
:::

:::closure
found: The galaxy's spiral arms, bright in both nights, cancelled into flat noise: the kernel matched the blur and the brightness, and the masks kept the chip gaps and bad pixels out of the fit. One source stands far above everything else: a bright, round, new point of light in the target, at about 62 times its noise. A handful of weaker spots sit on bright stars that are present on both nights.
matters: This is the moment the pipeline exists for: the night's differences, a whole galaxy's worth, cancel, and what changed in the sky stands out. Getting there took only small adaptations, but each was a decision about this data that a default would have got wrong.
raises: One clear new source, and a handful of other spots. Which are real?
:::
