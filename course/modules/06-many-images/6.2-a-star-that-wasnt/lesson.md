---
id: "6.2"
title: A star that wasn't there
question: Two bundles pass validation. Which reconstruction would you trust, and how do you find what's wrong in the other?
terms: [cosmic ray, robust loss]
guide: [reconstruct]
---

`validate_bundle` checks shapes, types, the PSFs' sizes and the masks'
dtype. The guide is plain about its limit: "An empty list does not check
every pixel value". A frame can hold a pixel that isn't sky, and a PSF can
be the wrong one for its frame, and validation will pass both.

The L2 reconstruction weighs every pixel of every frame by its variance
and fits them all. Its alternative, `rho`, uses a [[robust loss]] (Huber):
quadratic for small misfits, as L2 is, but linear past a threshold, so a
few large misfits pull less on the scene.

:::your-turn two-bundles
title: Two bundles
prompt: Two more bundles of 6.1's field arrived, bundle-1 and bundle-2. Both pass `validate_bundle` with no issues. The tutor will reconstruct each with 6.1's L2 configuration. Which would you trust, and why? Say what you'd look at first.
:::

:::slot two-scenes
title: Two reconstructions
caption: The two scenes, the central 48 × 48 pixels, on one logarithmic scale.
:::

:::your-turn what-wrong
title: What's wrong, and where?
prompt: Find what's wrong in each bundle, and in which frame, from the bundles and the runs. You can ask the tutor to look at anything: the frames, the PSFs, the receipts. Then say what you'd change, predict the result, and ask for the rerun.
:::

:::slot fixed
title: After the changes
caption: Each bundle's scene after its fix.
:::

:::closure
found: Bundle-1's scene had a fourth source at (30, 12), as bright at its peak (25.6) as the real source of 30. It was a [[cosmic ray]]: one pixel of frame 2, 40 above the sky, and nothing in frames 1 and 3. Measured as a star, it was 0.24 pixels wide, narrower than any frame's PSF allows. The loss was 2,083, against 2.97 in 6.1. Bundle-2's sources were blurrier, with peaks of 8.5, 14.2 and 5.7 though their totals were right, and its loss was 173: frame 3's PSF was recorded 0.59 pixels wide while its stars measured 1.13. Either fix removes the cosmic ray: masking that one pixel, or the robust reconstruction, which in our run left nothing brighter than 0.2 away from the sources (loss 1.33) and kept their totals within 3%. Recording frame 3's PSF correctly brought bundle-2 back to 6.1's scene and loss.
matters: Validation checks the bundle's form, not its content. The loss is the run's own alarm: hundreds or thousands of times the noise means the scene can't explain the frames, and the run reports it without failing. To find the cause, go back to the frames: a source in one frame only isn't a source, and a PSF should match the stars in its frame. L2 trusts every pixel; a robust loss limits what a few bad ones can do.
raises: Here the frames were synthetic and the faults planted. On real frames of a real galaxy, what can you check, and what happens to something that changed between the nights?
:::
