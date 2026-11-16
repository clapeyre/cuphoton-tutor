---
id: "5.2"
title: Read the catalog
question: Does the shipped chain find what you found by hand, and what does each row really say?
terms: [catalog, quality flags]
---

The chain's answer is a [[catalog]]: one row per candidate, with about a
hundred columns. Position and how strongly it stands out (`x`, `y`,
`peak_abs_sigma`, `sign`), the fit and its [[quality flags]], a flux measured
with the PSF (`psf_flux`) with its error bar, and `uq_valid`, which says
whether every error bar in the row could be computed. You don't need them
all: ask the tutor for the columns you want.

:::slot catalog
title: The catalog on the sky
caption: The target night, with each catalog row marked and numbered. Dashed: the row's uq_valid is False.
:::

:::your-turn same-answer
title: The same answer?
prompt: In 4.2 and 4.3 you found one supernova and a few bogus residues on bright stars. Does the catalog agree? Where does it differ, and why?
:::

:::your-turn trust-a-row
title: The supernova's row
prompt: The supernova's row says uq_valid False. Can you use its flux and error bar? Ask for whatever columns you need to decide.
:::

:::closure
found: The chain finds the supernova, at 43,400 counts against your 43,900 ± 190 by hand, and the same bogus residues on bright stars as 4.3, plus one weaker one. But its 12 rows are only six places on the sky: a twisted residue on a star splits into several hotspots, positive and negative, each with its own row. And the supernova's uq_valid is False because the fit, built for a pair of lobes, sent its negative lobe 457 pixels away; the centre between the lobes has no error bar, but the flux and its error bar are fine.
matters: A catalog row is a measurement with conditions, not a verdict. Rows aren't objects, a flag tells you which quantity failed and not whether the row is useless, and the only way to know which is to read the flags against the question you're asking. That's the same habit as reading a receipt, one row at a time.
raises: The supernova's error bar is almost twice what the fit alone says. Where does the rest come from, and is it right?
:::
