---
id: "8.2"
title: A mode goes missing
question: When the sweep and the fit say nothing is wrong, how would you know a mode is missing?
terms: [fit residual]
guide: [xray-traces]
---

How linear prediction finds the modes: with delays at even steps
$\Delta t$, a sum of $p$ damped exponentials obeys a fixed rule, each sample
being the same linear combination of the $p$ samples before it. The fit
solves for those $p$ coefficients by least squares, then finds the roots
of the polynomial they define; each root gives one exponential's
frequency and decay. A last least-squares solve gives the amplitudes.
Everything rests on the steps being even, and on which roots it keeps.

A crystal doesn't say how many modes it has. The sweep chooses an order
from the residual alone, and the fit returns whatever modes it finds: no
warning comes from either when something is left out. The guide's
troubleshooting warns about one case: linear prediction keeps only some of
the polynomial's roots, and "this can discard high-frequency modes even
without noise".

What's left after the fit, the [[fit residual]], is the one place a
missing mode can show. In 8.1 it was pure noise, 1.9e-4.

:::your-turn third-mode
title: Three modes
prompt: This crystal rings in three modes: 8.1's two, and a third at 2.0 THz, as strong as the second. The scan is like 8.1's, with 0.1 ps steps over 9.5 ps. The tutor will sweep and fit it the same way. Predict what comes back: how many modes, and at what order?
:::

:::slot scan-a
title: Scan a
caption: Left, the trace and the fit at the chosen order; middle, the fit residual; right, the residual's spectrum.
:::

:::your-turn two-more
title: Two more scans
prompt: Say you hadn't been told about the third mode. What in that output would have told you something was missing? The beamline sent two more scans of the same crystal, b and c, both about 9.5 ps long. Ask the tutor to fit them the same way. Which fit would you trust, and why? If you'd want to know something about a scan before trusting it, ask.
:::

:::slot scans
title: Scans b and c
caption: The same three panels for each scan; the spectra assume the delays are evenly spaced.
:::

:::closure
found: Scan a came back with two modes, 0.319 and 0.706 THz, and a zero-frequency term; the 2.0 THz mode was gone, at every order the sweep tried, with no warning. What gave it away was the residual: 4.8e-3, 25 times the noise of 8.1, with stripes in it and a spectrum peaked at 2.0 THz. Scan c, with 0.05 ps steps over the same span, found all three modes, at 0.318, 2.000 and 0.716 THz, and its residual was back at the noise, 1.9e-4. Scan b fitted 0.454, 2.056 and 0.890 THz, all wrong, with a residual of 7.0e-3: its delays ran in 0.05 ps steps to 2 ps and 0.13 ps steps after, and linear prediction assumes even steps. It said nothing about that either.
matters: A fit's output is a list of modes, and a missing one leaves no gap in the list. The check is the residual against the noise you expect: if it's well above it, something in the trace isn't in the model. The guide's advice works: plant modes at your scan's step size and see which come back, before you trust the scan. And check the delays before any fit: linear prediction assumes they're evenly spaced, and it won't tell you when they aren't.
raises: One trace at a time is slow going. A detector has hundreds of rows, each a trace. What does a fit of every row tell you, and how do you check thousands of fits?
:::
