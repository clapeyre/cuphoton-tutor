---
id: "4.4"
title: No answer key
question: Without an answer key, how faint a change can this pipeline find, and can you trust its error bars?
terms: [injected source]
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
found: Fake stars of 2,000 counts and brighter (about magnitude 18.6) all came back, with fluxes within 1% of what was planted. At 1,000 counts only about a third did; at 500, none. And the measured fluxes scattered about 1.2 to 1.5 times more than their error bars said: the survey resampled its images onto the sky grid, which makes neighbouring pixels' noise correlated, and the variance map doesn't record that.
matters: Two facts nobody would have told you, and that no single run could show: where this pipeline goes blind, and that its error bars are too optimistic on this data. Neither is a bug in cuPhoton; both are properties of the data, found by testing it. Whatever your instrument, an injection test is how you turn "it found something" into a statement you can defend, with a limit and an honest uncertainty.
raises: You've now run the whole chain on real data, adapted it, and tested it. What would you tell an agent before it processes the next night?
:::
