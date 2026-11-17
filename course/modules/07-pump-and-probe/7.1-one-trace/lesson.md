---
id: "7.1"
title: One trace
question: What does xRay's fit report for a trace whose modes you know, and why?
terms: [pump-probe, trace, damped mode, model order]
guide: [xray-traces]
---

The data comes as two HDF5 files, one laser-on and one laser-off, each a
stack of detector frames, one per delay, with the delays and an
incident-beam monitor (`i0`) beside them. The X-ray beam's intensity
wobbles from pulse to pulse, so xRay divides each frame by its monitor
reading before it compares anything.

Then it reduces the pair to a [[trace]]: for a region of the detector, the
laser-on signal over the laser-off one, minus one, at each delay. Zero
means the laser changed nothing. By default it adds the mean laser-off
level to both sides first, `(on + S) / (off + S) − 1`, which steadies the
ratio.

The fit is **linear prediction**. It assumes the trace is a sum of
[[damped mode]]s plus a constant, needs no starting guess, and turns the
fit into linear algebra. The one choice you make is the [[model order]],
the number of components it keeps: each oscillating mode takes two. A
sweep fits several orders and picks the smallest one whose residual is
within 1% of the best.

You'll use the user guide's own sample pair: 97 frames of a 32 × 32
detector, 0.1 picoseconds apart.

:::your-turn predict-fit
title: What will the fit report?
prompt: In the sample pair, the laser-on frames change by 4% at 0.32 THz, dying away at 0.15 per picosecond, and by 2% at 0.72 THz, dying at 0.08 per picosecond, plus a constant 1%. The tutor will extract one 16 × 16 tile's trace and fit it. Predict what the fit reports for each mode, its frequency, decay and amplitude. If you can't tell for one of them, say what you'd check.
:::

:::slot fit
title: The trace and its fit
caption: Left, the tile's trace (grey) and the fit at the order the sweep chose (blue); middle, what the fit leaves (the trace minus the fit); right, the fit's modes as a spectrum.
:::

:::your-turn order
title: Why that order?
prompt: The sweep tried orders 1 to 9. Why did it choose 4? What would order 3 have missed, and why don't the orders above 4 leave a smaller residual?
:::

:::closure
found: The fit returned both modes, at 0.318 and 0.717 THz, decaying at 0.148 and 0.079 per picosecond: the planted values. The amplitudes came back as 0.0199 and 0.0099, half the 4% and 2% planted, because of the reference shift: adding the laser-off level to both sides of the ratio halves a small change. With `reference_shift=False` they were 0.0399 and 0.0198. The sweep's residual fell from 1.0e-2 at order 2 to 1.75e-3 at order 3, which holds only one mode, and to 1.91e-4 at order 4, two modes, then stayed there: 1.9e-4 is the counting noise, and no mode is left to take.
matters: The fit reports what the trace holds, and the trace is a choice: the reference shift halves every amplitude, and the guide says so in one sentence. Frequencies and decays don't depend on it; amplitudes do, so compare them only between traces made the same way. The residual is the check on the order: when adding components stops lowering it, what's left should be noise, and you know what your noise should be.
raises: Here you knew how many modes there were. A real crystal doesn't say. Does the sweep find every mode that's there?
:::
