---
id: "5.1"
title: From instruction to configuration
question: What does the shipped pipeline need to know about this data, and how do you know it used it?
terms: [configuration]
---

:::video v6-one-image-through-the-chain
:::

In [4.2](#/4.2) you gave the run as one instruction to an agent. The transient
chain takes the same decisions as a [[configuration]]: a YAML file with one
block per stage, and a `survey` block that says where each plane of the data
is and what its numbers mean. It ships with a configuration for a different
survey, with a different file layout, and checks every key when it loads it.

The tutor can show you the shipped configuration's `survey` block, or any
other block. What you decided about this data in [4.1](#/4.1) is what goes
into it.

:::your-turn settings
title: What has to change?
prompt: Ask to see the shipped configuration's survey block. Which settings must change for the M101 pair, and why? Then ask the tutor to write the configuration and run the chain on the GPU.
:::

:::your-turn success
title: It says success
prompt: The run finished with "success" and 12 candidates. Is it done? Ask for anything the run left behind, and say what you'd check before using its catalog.
:::

:::closure
found: Four settings carried what 4.1 established: the survey's planes are variances (not inverse variances), the reference has its own variance and mask, both nights are already on one grid, and the survey's "don't use" bits are 8575. The run then succeeded, and its catalog had no fluxes: with the reference already on the target's grid, the chain skips the step that matches stars, so it never measured the PSF width that its flux measurement and most of its error budget need. Only `summary.json` said so, in `psf_sigma_source: null` and `uq.excluded`. Giving the width (1.57 pixels, from the header, as in 4.4) fixed it.
matters: A pipeline's "success" means it finished, not that it computed everything. What it had to leave out is written down, in the summary, for the reader who looks. The instruction you'd give an agent becomes a configuration you can check, but its defaults still answer questions you didn't ask.
raises: The catalog now has fluxes. What's in it, and how does it compare with what you found by hand?
:::
