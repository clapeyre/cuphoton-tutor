---
id: "5.3"
title: The error budget
question: The chain quotes an error bar built from several terms. Is it right on this data, and is the value it's attached to?
terms: [error budget, pull]
---

:::video v5-why-the-sum-wobbles
:::

In [4.4](#/4.4) you found the error bars of your own chain too small, because
neighbouring pixels share noise after resampling. The transient chain has a
term for exactly that. Each flux's error bar is an [[error budget]]: the fit's
own error, plus a term for correlated noise (`corr`), one for the kernel fit's
own uncertainty (`kfit`), one for kernel mismatch on stars (`kmatch`) and one
for misalignment (`mis`), added in quadrature. Each term has its own column,
and `summary.json` says which terms ran and why any were left out.

:::your-turn budget
title: Where the rest comes from
prompt: The supernova's flux error is 183 from the fit alone and 329 in total. Ask for the terms. Where does the difference come from, and how does it compare with what you measured in 4.4?
:::

:::your-turn test-it
title: Test it
prompt: Test the chain's error bars the way you tested your own in 4.4. Say what you'd plant and what you'd measure, then ask the tutor to run it.
:::

:::slot injection
title: What came back
caption: Planted fakes measured by the chain: measured/planted flux per level, and the pulls against the chain's error bar and against the fit's alone.
:::

:::your-turn what-went-wrong
title: Right size, wrong place
prompt: Read the figure. Are the chain's error bars right? Are its fluxes? If something is off, find out why: ask for anything in the run's summary, change the configuration, and rerun.
:::

:::closure
found: The chain's correlated-noise term nearly doubles the fit's error bar on this pair (a factor of 1.8 for the supernova), measured from empty patches of this very image: the same correlation you found by hand in 4.4. Tested with 300 fakes, the bars were the right size, but every flux was 4 to 11% low. The run's summary held the clue: the kernel had been fitted on five small stamps, under 1% of the image, with a χ²/dof of 16. Fitted on the whole usable image (χ²/dof 1.3), the fluxes came back right and the pulls scattered by 0.8 to 0.9 around zero: honest, slightly cautious error bars.
matters: An error budget adds up the ways a value can scatter. It can't see a value that is wrong in the same direction every time, and no term would have widened to cover it. Only a test with known answers separates the two, which is why the injection test you designed in 4.4 isn't a one-off: it belongs in every new configuration, on every new kind of data.
raises: You found two silent problems by hand, on one image. How would you catch them on the thousandth?
:::
