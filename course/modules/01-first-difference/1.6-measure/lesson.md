---
id: "1.6"
title: Measure (xFit)
question: How much did each candidate change, and with what error bar?
terms: [stamp, amplitude, fit status]
guide: [measure]
---

:::chain hi=xFit
caption: Measuring what's left.
:::

xFit measures each candidate by fitting a model to a small cutout around it,
a [[stamp]], taken from the difference image together with its variance. The
model is a single blurred point of light, with its width fixed to the target's
PSF width, which the header records (`PSFSIG`, in pixels). The fit returns an
[[amplitude]], the height of the model, whose sign says whether the source got
brighter or fainter; from it, a flux and its error bar; and a
[[fit status]] saying whether the fit converged and its error is usable.

:::your-turn cut-stamps
title: Cutting the stamps
prompt: How should we cut the stamps: from which image, centred where, and how big? Tell the tutor, then let it fit.
:::

:::slot fluxes
title: Measured fluxes
caption: Each stamp, its fit, and the measured flux against what was injected.
:::

:::your-turn test-prediction
title: Your prediction from 1.2
prompt: In 1.2 you predicted what multiplying the variance plane by 4 does to a flux and its error bar. Ask the tutor to rerun the measurement that way. Were you right, and why?
:::

:::closure
found: The brightened star measured +12,234 ± 114 DN against +12,120 injected, and the new source +4,140 ± 71 against 4,000, both within about two error bars. With the variance × 4, the fluxes didn't move at all, and both error bars doubled (227 and 141).
matters: You've now checked a result the right way: against a known answer, with an error bar, and with a test of how the error bar responds to its inputs. On real data there's no answer key, so the only protection is what you practised here: predict, run one stage, look, compare.
raises: That worked because you watched every stage. What if someone else's agent ran the whole thing and only showed you the result?
:::
