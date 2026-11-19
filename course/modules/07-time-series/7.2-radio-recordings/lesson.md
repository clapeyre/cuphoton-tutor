---
id: "7.2"
title: Three radio stations
question: What does a correlator need to know besides the recordings, and what happens when part of it is wrong?
terms: [VDIF, delay model, visibility, baseline]
guide: [correlate]
---

A radio telescope records the voltage from its receiver, millions of times a
second, often with just two bits per sample. The recordings are written as
[[VDIF]] files: frames of packed samples, each behind a header that stamps
its time and its station. A recording alone doesn't say when the wavefront
from the source reached that dish. That's in the job, the correlator's
instructions: the stations and their clocks, the frequency band, which
pairs to correlate, and for each station a [[delay model]], the time the
wavefront arrives there, which changes as the Earth turns.

xBeam lines the recordings up with the delay model, transforms them into
frequency channels, and multiplies each pair of stations, a [[baseline]].
What it writes, per baseline, channel and stretch of time, is a
[[visibility]]: a complex number whose amplitude says how much the two
recordings share, and whose phase says how well they were lined up.

On the command line it takes three steps: `cuphoton xbeam inspect-vdif`
reads a recording's headers, `build-vdif-sidecar` indexes its frames once,
and `correlate` runs the job.

:::your-turn first-fringes
title: Predict the visibilities
prompt: Three stations, AA, BB and CC, recorded the same patch of sky for one second, and the tutor has their recordings and a job for them. Assume the job is right. What should each baseline's visibility look like across the band: its amplitude, and its phase? Then ask the tutor to inspect the recordings, correlate them on the GPU and show you the visibilities.
:::

:::slot fringes
title: The visibilities
caption: Each baseline across the 8 MHz band, averaged over the second. Top, the correlation amplitude; bottom, the phase, unwrapped, in turns.
:::

:::your-turn fix-it
title: Which station?
prompt: Two of the baselines don't look like your prediction. Which station is at fault, by how much, and what would you change in the job? Predict what the rerun will show, then ask the tutor to make the change and run it again.
:::

:::slot fixed
title: After the change
caption: The same three baselines with the corrected job.
:::

:::closure
found: AA–CC came out as predicted: flat phase, amplitude 0.18. AA–BB and BB–CC had phases that climbed and fell by 14 turns across the band, a slope of 1.75 microseconds, opposite in sign because BB is the second station in one pair and the first in the other. The station they share was the problem: BB's clock stamped its samples 1.75 µs late, and the job didn't know. Per channel, the amplitude dropped only slightly, from 0.18 to 0.16; averaged over the band it fell to 0.001, because the phases cancel. Every record had weight 1.0 and the run reported nothing wrong. The fix went into BB's clock or its delay model, with the job's sign: its delays say how much earlier a station hears the wavefront, so BB needed 1.75 µs more negative (clock −1.75 µs, or delay −2.3 → −4.05 µs). With the other sign, it doubles the slope to 3.5 µs, again without a word.
matters: A correlator computes exactly what the job tells it. Its weights describe data coverage, not whether the model was right, so a wrong delay comes out as good-looking records with the signal spread into a phase slope, and a band-averaged image of nothing. Correlating real arrays is mostly this: run, look at every baseline's phase, find the station whose baselines all slope, and fix its clock. The slope is the 7.1 reading again, and the sign of every convention needs checking against a run. On an RTX 4070 Ti SUPER, the GPU correlated three 8-second stations in 0.7 s; the CPU path took 16 s.
raises: Synthetic recordings had a known answer. On real data with a weak signal and loud noise, how do you find the delay, and how do you know it's not a fluke?
:::
