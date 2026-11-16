---
id: "1.4"
title: Match and subtract (xPois)
question: How do we make the reference look like the target, so that subtracting leaves only the real changes?
terms: [kernel, kernel mismatch, chi2/dof]
---

:::video v3-kernel
:::

:::chain hi=xPois
caption: The heart of the pipeline.
:::

The target is blurrier than the reference. xPois finds a [[kernel]]: a small
array of weights (19 × 19 pixels here) that, slid across the reference, blurs
it until its stars look like the target's. It fits the kernel together with a
smooth background level, then subtracts the matched reference from the target.
"Kernel" here means this blurring stencil; Module 03 meets the GPU meaning of
the word.

:::your-turn perfect-kernel
title: Before we subtract
prompt: If the kernel were perfect, what would the subtraction leave at a star that didn't change? And if the kernel were slightly off?
:::

:::slot difference
title: The difference image
caption: Target minus the matched reference, with the fitted kernel.
:::

:::your-turn nan-edge
title: The empty frame
lead: The difference image has a frame around its edge, 9 pixels wide, where every value is NaN (no number at all).
prompt: Why is that frame there?
:::

:::closure
found: The unchanged stars have mostly cancelled into noise; what a slightly imperfect match still leaves at them is kernel mismatch. The empty frame is the kernel's reach: a 19 × 19 kernel needs 9 pixels on every side, so near the edge there's nothing to blur with. The fit's chi2/dof came out at 1.29: the residuals are about noise-sized, which is necessary, not proof.
matters: This is the step that makes difference imaging work at all, and the one most likely to go subtly wrong. A good-looking number like chi2/dof ≈ 1 tells you the leftovers are noise-sized on average, not that every star cancelled, and not that the noise model is right.
raises: The changes should now stand out from the noise. Which of the leftovers do?
:::
