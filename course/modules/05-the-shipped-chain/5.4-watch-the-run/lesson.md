---
id: "5.4"
title: Watch the run
question: How would you catch, on every image of a long run, the problems you found by hand on one?
terms: []
guide: [monitor]
---

A survey runs this chain on thousands of images a night, and nobody reads
every `summary.json`. Module 02's habit, evidence about every run, has to
scale. cuPhoton's **xLens** records what your own code measured for each
image as a *sample*: named measurements with units, plus *findings*, the
results of rules you write ("the kernel fit is poor"). It keeps every sample
and exports a dashboard as one HTML file. It needs no GPU.

You've run the chain on 22 images in this module: the real pair a few times,
and two injection tests of ten images each.

:::your-turn rules
title: What to record, what to flag
prompt: For every image the chain processes, what would you record, and which rules would raise a flag? Think of what went wrong in 5.1 and 5.3, and of Module 02. Then ask the tutor to build the watch over this module's runs and show you the dashboard.
:::

:::your-turn module-question
title: The module in two sentences
prompt: Can you trust what a shipped pipeline writes on new data, and what does it take to find out? Two sentences, in your own words.
:::

:::closure
found: A few numbers from each image's summary would have caught both silent problems of this module on every image of a long run: the PSF width's source and the error terms left out, the kernel fit's χ²/dof and how many pixels it used. Rules on them turn into flags on a dashboard, next to the read receipts and the candidate counts. Writing them took one small function.
matters: The habits of this course were all done by hand, once. A pipeline runs them thousands of times. What scales is to write each check you did by hand as a rule that runs on every image, and to read the flags before the catalog. A rule only exists, though, once someone has found the problem by looking.
raises: Your data may not be two nights of M101. cuPhoton has parts for other kinds of signal; the next three modules take one each, starting with two receivers that hear the same source.
:::
