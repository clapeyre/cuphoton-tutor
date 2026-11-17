---
id: "7.3"
title: Two detectors, one wave
question: Did the gravitational wave reach the two LIGO detectors at different times, and how sure can you be from the data alone?
terms: [strain, whitening, "background estimate|background"]
guide: [correlate]
---

On 14 September 2015 the two LIGO detectors, at Hanford in Washington and
Livingston in Louisiana, recorded the first gravitational wave ever
detected, GW150914: two black holes merging 1.3 billion light years away.
Each detector measures [[strain]], the tiny relative stretching of its 4 km
arms, 4,096 times a second. The sites are 3,002 km apart, so a wave
travelling at the speed of light reaches one at most 10 ms before the other.

The `data/` folder holds the public recordings around the event: 32 seconds
from each detector, as released by the Gravitational Wave Open Science
Center. They're two uniformly sampled signals on one time grid: exactly
what xBeam's time-series correlation takes.

:::your-turn plan
title: Which detector heard it first?
prompt: Plan the measurement. What range of delays is possible, and what would you expect the correlation around the event to look like? Then ask the tutor to correlate Hanford with Livingston over the quarter second around the event, and to show you what the recordings look like.
:::

:::slot look
title: The recordings
caption: Left, the strain around the event in Hanford (H1) and Livingston (L1); middle, the same after whitening, 35–350 Hz; right, how loud each detector's noise is at each frequency, with the wave's band in grey.
:::

:::your-turn is-it-real
title: Is the peak real?
prompt: In 7.1 every correlation had a peak, signal or not. How would you show, from these 32 seconds alone, that this one isn't noise? Then ask the tutor to do it.
:::

:::slot background
title: The event against the background
caption: Left, the correlation in the quarter second around the event, against lag, with the physically possible ±10 ms in grey; right, the strongest peak within ±10 ms in each of the other quarter seconds, and the event's in orange.
:::

:::closure
found: Correlated as recorded, the strain put the peak at +9.5 ms: Livingston hearing it later, inside the allowed 10 ms, and wrong. The recordings are dominated by noise below 30 Hz, hundreds of times larger than the wave, and the correlation follows that noise; the quarter second starting a tenth of a second later gave +0.5 ms instead. [[Whitening]] each detector by its own noise, and keeping 35–350 Hz where the wave is, put the peak at −7.3 ms: Livingston first, by about 7 ms, and with a negative correlation, because the two detectors' arms point differently and see the wave's stretch with opposite signs. LIGO's own analysis found 6.9 ms. Against the [[background estimate|background]] of 112 other quarter seconds, the event's correlation, 0.66, was louder than all of them; the loudest noise reached 0.58. In raw strain, 23 of the 112 beat the event's quarter second.
matters: The correlator did the same job every time; what changed the answer was what you fed it and what you compared it with. Raw data correlates on whatever is loudest, which is rarely what you're after, and xBeam doesn't whiten, taper or normalize for you. A peak means something only against the peaks noise makes in the same analysis, and 32 seconds of background can say "louder than anything in this stretch", roughly 1 in 100, not more. LIGO's detection claim rested on matched filtering against predicted waveforms and on weeks of shifted-time background, which put false alarms that loud at fewer than one in 203,000 years.
raises: You've now correlated synthetic signals, radio recordings and a real gravitational wave. What would correlating your own recordings take, and what would you check first?
:::
