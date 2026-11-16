---
id: "3.4"
title: Time it honestly
question: How much faster is the GPU, really, and what exactly did you measure?
terms: [synchronize, warm-up, speedup]
---

Speedups are the most quoted numbers about GPUs and the easiest to get wrong.
A GPU [[speedup]] only means something if both timings measure the same work,
from the same starting point to the same end, and if the work had actually
finished when the clock stopped.

A colleague wrote a short script to answer "how much faster is xRep on the
GPU?" for a 2048 × 2048 image. It looks careful: it does a [[warm-up]] call
first, then times ten runs and takes the median. It reports a speedup of
more than ten thousand. You can ask to see the script: the tutor will show
you the part that does the timing.

:::your-turn the-claim
title: Ten thousand times?
prompt: Ask the tutor to run the colleague's script. Do you believe the number? Ask for any evidence or variation you like. Then say (a) what's wrong, if anything, (b) a speedup you'd stand behind and what it measures, and (c) what you'd ask any agent that reports a GPU speedup.
:::

:::your-turn module-question
title: The module in two sentences
prompt: How do you move the pipeline onto the GPU, prove that's where it ran, and say honestly how much faster it is? Two sentences, in your own words.
:::

:::closure
found: The script never waited for the GPU. A GPU call returns as soon as its work is queued, so the stopwatch timed the queuing: under a millisecond. Synchronizing before stopping the clock gives about 22 ms, a speedup of about 400 for the reprojection alone, or about 300 counting the copies to and from the GPU. The warm-up and the median were right; the missing synchronize made the number thirty times too good.
matters: Every speedup is a ratio of two boundaries, and both must be stated: one stage or the whole pipeline, with or without loading and copying, warm or cold, how big the input. cuPhoton's often-quoted 14,900× is for image loading, one operation, not the pipeline. And small inputs can be slower on a GPU: in 3.2, xFit took longer there than on the CPU. Ask for the boundaries before you repeat the number.
raises: The last module takes the pipeline to real telescope data, where the noise model has to fit the data too.
:::
