---
id: "1.5"
title: Find the candidates
question: Which leftovers stand out from the noise?
terms: [standardized residual, threshold, hotspot]
---

:::chain hi=xPois
caption: xPois also flags what's left worth measuring.
:::

A leftover of 50 counts means little on a bright star and a lot on empty sky.
So xPois divides the difference image, pixel by pixel, by the noise it
predicts there (from both variance planes and the kernel). The result is the
[[standardized residual]], written z: the difference measured in units of its
own noise. Pure noise gives z mostly between −3 and 3.

Pixels above a [[threshold]], 5 in cuPhoton's tutorial, are grouped into
[[hotspot|hotspots]]: connected regions, each a candidate change.

:::your-turn how-many
title: How many, and where?
prompt: From everything you've seen of this pair, how many hotspots do you expect above z = 5, and what do you expect them to be? Then ask the tutor to run it.
:::

:::slot hotspots
title: Hotspots
caption: The standardized residual z, with each hotspot lettered.
:::

:::your-turn what-five-means
title: What 5 means
prompt: A hotspot passed z > 5. Does that mean there's less than a one-in-a-million chance it's just noise?
:::

:::closure
found: Two hotspots passed the threshold, exactly where the two changes were injected: the star that got brighter and the new source. Nothing else in the field rose above 5. The threshold is in z's approximate noise units; it doesn't by itself give a false-alarm probability, because z leaves out the noise that resampling and the fitted kernel add.
matters: Thresholds decide what anyone ever looks at. Too low, and you drown in noise and kernel mismatch; too high, and faint real changes are never seen. Surveys tune this one number very carefully, and they always check it against injected sources, just as we can here.
raises: We know where the changes are. How much did each one change, and how sure are we?
:::
