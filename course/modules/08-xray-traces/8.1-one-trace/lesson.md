---
id: "8.1"
title: One trace
question: What does xRay's fit report for a trace whose modes you know, and why?
terms: [pump-probe, trace, damped mode, model order]
guide: [xray-traces]
---

:::video v8-pump-and-probe
:::

The video showed the whole path, from a laser pulse to a fitted trace. Here
it is in the user guide's terms.

The data comes as two HDF5 files, one laser-on and one laser-off, each a
stack of detector frames, one per delay, with the delays and an
incident-beam monitor (`i0`) beside them. The X-ray beam's intensity
wobbles from pulse to pulse, so xRay divides each frame by its monitor
reading before it compares anything.

Then it reduces the pair to a [[trace]]. For a region of the detector it
sums the counts of the laser-on frame and of the laser-off frame at each
delay, call them $\text{on}$ and $\text{off}$, and forms

$$\text{trace} = \frac{\text{on}}{\text{off}} - 1$$

Zero means the laser changed nothing; 0.04 means the laser-on signal is 4%
higher. By default xRay first adds a **reference shift** $S$ to the top and
the bottom of the ratio, where $S$ is the mean laser-off signal over all
delays:

$$\text{trace} = \frac{\text{on} + S}{\text{off} + S} - 1$$

The guide says, in one sentence, that this steadies the ratio.

The fit is **linear prediction**. It assumes the trace is a sum of
[[damped mode]]s, each with a frequency $f$, a decay rate $\gamma$, an
amplitude $A$ and a phase $\varphi$:

$$\text{trace}(t) \approx \sum_k A_k\, e^{-\gamma_k t} \cos(2\pi f_k t + \varphi_k)$$

It needs no starting guess: it turns the fit into linear algebra, which
works only when the delays are evenly spaced. The one choice you make is
the [[model order]], the number of components it keeps. Each oscillating
mode takes two, because a cosine is the sum of two complex exponentials,
$e^{(-\gamma + 2\pi i f)t}$ and $e^{(-\gamma - 2\pi i f)t}$. A sweep
fits several orders and picks the smallest one whose residual is within
1% of the best.

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
