---
id: "4.4"
title: No answer key
question: Without an answer key, how faint a change can this pipeline find, and can you trust its error bars?
terms: [injected source]
guide: [uncertainty]
---

On the synthetic pair you checked every answer against what was put in. On
real data nothing tells you what you missed, or whether a flux of 1,000 ± 80
is really that good. Surveys answer both questions the same way: they make
their own answer key, by planting fake sources of known brightness in the real
images, running the unchanged pipeline, and counting what comes back. This is
an **injection test**: the [[injected source|injected sources]] see the real
noise, the real galaxy and the real masks.

:::your-turn design
title: Design the test
prompt: Design an injection test for this pair: what would you plant, how bright, how many and where, and what would you measure? Then ask the tutor to run it.
:::

:::slot recovery
title: What came back
caption: Fraction of fake sources found, and measured against planted flux, at each brightness.
:::

:::your-turn what-it-proves
title: What it tells you
prompt: What does the test tell you about this pipeline on this data, and what doesn't it tell you?
:::

:::closure
found: In our reference run, fakes planted with the same round blur the fitter assumes came back at 2,000 counts and brighter (about magnitude 18.6), with fluxes within 1% of what was planted. At 1,000 counts only some did (a third to a half, depending on where the fakes landed); at 500, almost none. Your design will move these numbers. Fakes shaped like the image's real stars, rather than like the fitter's model, come back low: that measures the fitter's blur model, a separate error from the noise. And the measured fluxes scattered about 1.2 to 1.5 times more than their error bars said. The variance map is right pixel by pixel, but a flux adds up many pixels, and adding variances assumes each pixel's noise is independent. Here it isn't: the survey resampled its images onto the sky grid, so neighbouring pixels share part of their noise, and shared noise doesn't average out in a sum. A one-number-per-pixel map can't record that, so the fix for the scatter is to measure the factor, as this test did, and widen the error bars by it. A flux bias needs a different fix: a better model of the blur. (The video that opens [5.3](#/5.3) shows it happening, in a minute and a half.)
matters: Facts nobody would have told you, and that no single run could show: where this configuration goes blind on this data, and that its error bars are too optimistic. They have different causes. The too-small error bars come from the data: the survey's resampling shared noise between pixels. A flux bias on star-shaped fakes comes from the fitter's blur model, a setting you can change. And a blind band around unused pixels, if your test found one, comes from the rule that a difference pixel needs its whole kernel footprint. None of them shows up as an error in a single run. Whatever your instrument, an injection test is how you turn "it found something" into a statement you can defend, with a limit and an honest uncertainty.
raises: Fakes fainter than about 1,000 counts didn't come back. Your reference is a single night, and the survey took others. Would stacking them let you see fainter?
:::
