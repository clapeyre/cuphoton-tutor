---
id: "2.6"
title: Your standing instruction
question: What should every agent that runs cuPhoton for you check, every time?
terms: []
guide: [concepts]
---

An agent will do what you ask, report "done", and move on. In this module and
the last, the runs that went wrong all said "done": swapped axes with healthy
fit status, a CPU run that was meant for the GPU, a rerun that printed
"status: ok" while failing.

So you need an instruction you give once and every agent follows on every run:
a short list that starts "After every run, check…". It's the most useful thing
you'll take from this course into real work.

:::your-turn after-every-run
title: After every run, check…
prompt: Write your standing instruction, in your own words: what must the agent check, and report back to you, after every cuPhoton run? Then, to try it, direct one small run in a single instruction: name the component, the hardware you want (and whether to fail without it), the output directory, and the evidence you expect back.
:::

:::closure
found: cuPhoton's troubleshooting guide checks where the run happened (backend, device and dtype from the receipt, against what you asked for), whether it worked (exit status, fit status or convergence counts), whether it's right (a plot, and a comparison with what you expected), and where the evidence lives (a new output directory per run).
matters: This is the job that's left to you when an agent does the typing: deciding what counts as evidence, and asking for it every time. The next modules move the work onto the GPU, where every item on your list gets used.
raises: Module 03 moves the pipeline onto the GPU. How do you get it there, and prove it's there?
:::
