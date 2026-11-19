---
id: "7.1"
title: A known delay
question: How do you read a delay from two recordings, and when does the reading lie?
terms: [cross-correlation, lag, cross-spectrum]
guide: [correlate]
---

:::video v7-two-receivers
:::

The video found the delay by sliding one recording past the other. xBeam
gets the same sums faster, through Fourier transforms: it cuts both
recordings into windows, turns each window into its frequencies, multiplies
one by the complex conjugate of the other, frequency by frequency, and averages over the windows. That product
is the [[cross-spectrum]]. Turned back into a function of the shift, it's the
[[cross-correlation]] from the video, one value per [[lag]], the shift in
samples.

You'll start where the user guide starts: two made-up signals, one a copy of
the other that arrives a few samples later, plus noise of its own.

In Python it takes a source and a spec: `ArraySource` holds the signals on
one sample grid, and `CorrelationSpec` names the pairs, the window length,
how many windows to average, and the backend (`cupy` for the GPU).

:::your-turn known-delay
title: Where is the peak?
prompt: Signal b is a copy of a that arrives 7 samples later, plus noise. The tutor will correlate the pair (a, b) on the GPU. Predict where the cross-correlation peaks, and its sign. Then ask what happens with a delay of 7.4 samples, which falls between two samples.
:::

:::slot delay
title: Two ways to read a delay
caption: Left, the cross-correlation near zero lag; right, the phase of the averaged cross-spectrum against frequency (blue) and a straight-line fit (dashed). Top, a delay of 7 samples; bottom, 7.4.
:::

:::your-turn hidden
title: Delays you aren't told
prompt: The tutor has two more pairs whose delays you aren't told, up to a couple of thousand samples. It will correlate each with 1,024-sample windows, in both of xBeam's lag modes, linear and circular, and show you each result's peak. Which readings would you trust, and why? If you can't tell yet, say what you'd look at.
:::

:::closure
found: The peak sat at lag +7: positive, because in the pair (a, b) the second signal arrives later; swapped to (b, a), it was −7. At 7.4 samples the peak still said 7, a whole number of samples, spread over lags 7 and 8, while the slope of the cross-spectrum's phase read 7.39: across the band the phase gains half a turn for every sample of delay, fractions included (3.5 turns for 7 samples). The hidden pairs were 900 and 1,500 samples apart. With 1,024-sample windows, linear mode found 900 every time, its peak 12 times the typical value, against 56 to 97 for the 7-sample pair: fewer samples overlap at a long lag. At 1,500 it couldn't: each result peaked somewhere else, only 7 to 11 times the typical value. Circular mode wraps lags around the window, so 900 came out as −124 in every result: wrong, and consistent.
matters: A correlation always has a highest point; xBeam reports it without judging it. No error came from any of these runs. What tells a delay from noise is outside the number: the peak's height against the rest, whether separate results agree, and whether the delay is one the geometry allows. Agreement alone isn't enough, since a wrapped lag agrees with itself. Choose windows longer than the largest delay you could meet, in linear mode, before you look.
raises: Radio telescopes record voltages, not neat arrays, and the delay changes as the Earth turns. What does correlating real radio recordings look like?
:::
