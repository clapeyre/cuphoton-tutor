---
id: "1.3"
title: Align (xRep)
question: How do we put both images on one grid, and which image moves?
terms: [WCS, reprojection, mask]
guide: [align]
---

:::chain hi=xRep
caption: The first stage of the plan from Module 00.
:::

Each FITS header holds a [[WCS]], a world coordinate system: the formula that
turns a pixel position into a position on the sky. With the two WCS headers,
xRep can work out, for every pixel of one grid, where it falls on the other,
and resample one image onto the other's grid. That is [[reprojection]].

xRep moves the variance plane along with the image, and a [[mask]] that flags
pixels with no valid data, for example parts of one grid that the other image
never covered. It changes the geometry only: it doesn't touch the blur.

:::your-turn which-grid
title: Which one moves?
prompt: Before we run it, predict two things. Which image will cuPhoton move onto the other's grid, and why that one? What shape will the result have? Then tell the tutor to run it.
:::

:::slot aligned
title: Aligned
caption: The reference after xRep, beside the target.
:::

:::closure
found: xRep moved the reference onto the target's grid, so the result has the target's shape, 256 × 256, and the same star now sits on the same pixel in both. The reference covers the whole target, so the mask flags nothing here.
matters: The image that moves is the one that will be blurred next. Resampling and blurring both soften an image, so you do both to the sharper one and leave the target, where you want to find changes, untouched. Choosing which image moves is a real decision on every survey.
raises: The stars line up, but they're still sharper in the reference. Next comes matching the blur and subtracting.
:::
