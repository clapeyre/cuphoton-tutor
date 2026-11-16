---
id: "1.7"
title: It ran, so it's right?
question: A script ran cleanly. How do you tell, from evidence alone, whether its result is right?
terms: [fit status]
---

A colleague asked their own agent to do what we just did on the same pair, in
one go. The agent wrote a script; it runs without an error or a warning and
prints its result. This is how you'll usually meet a pipeline's output: after
the fact, from someone (or something) else.

You have the same tools as before: you can ask the tutor for any evidence you
like, such as plots, cutouts, positions, fluxes, fit status or comparisons
with what was injected. You can't read the script until you've made up your
mind.

:::your-turn swapped
title: Is it right?
prompt: Ask the tutor to run your colleague's script. Is its result right? If not, give (a) the symptom you see in the evidence, (b) the cause, and (c) how you would have caught it before trusting the result.
:::

:::closure
found: The script ran cleanly, fit status looked healthy, and the answer was wrong. Hotspot peaks come back as (y, x), but the stamp cutter takes (x, y). Passing them unchanged cut the stamps at transposed positions, on empty sky, and the fit "succeeded" on noise. Only the evidence showed it: fluxes far from the injected ones, cutouts with nothing at their centre, fitted positions wandering off-centre.
matters: This is the job an agent can't do for you. Code that runs is not code that's right, and the failures that matter most, such as swapped axes, a wrong variance or a silent fallback, all run cleanly. Your defence is the habit from this module: know what each stage should produce, and look before you believe.
raises: Everything so far ran on a CPU. Before moving to the GPU: when a run finishes, how do you know what actually ran, and where?
:::
