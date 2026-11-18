---
id: "2.5"
title: Which run didn't run where we meant?
question: From receipts alone, can you tell which run quietly fell back?
terms: [fallback, profile]
guide: [concepts]
---

Three runs of the same quickstarts, by three different people. One was a
deliberate CPU baseline. The other two were meant for the GPU. One of those
two didn't use it, and nobody got an error: all three exited cleanly with
status ok, and their results agree.

You get the three receipts, named `run-1`, `run-2` and `run-3`, and nothing
else. You can ask the tutor for any field or comparison you like.

:::your-turn which-run
title: Which one?
prompt: Ask the tutor for the receipts. Which run was meant for the GPU and didn't use it? Give (a) which run, (b) what in the receipts shows it, and (c) what request would have turned this silent fallback into an error.
:::

:::closure
found: The silent one asked for the best available hardware (profile auto), didn't require a GPU, found none usable (gpu_available false), and ran every component on the cpu device, with status ok. The CPU baseline looks almost identical, except that it asked for the CPU on purpose (profile cpu). The GPU run put every component on a cuda device, each with its own GPU backend (cupy for most, torch for xScan). The numbers in all three agree, so they can't tell you anything; only the receipt's request and devices can. Adding --require-gpu would have made the fallback an error.
matters: The difference between the two CPU runs wasn't in what happened but in what was asked for. A receipt is only meaningful against your intent, so the instruction you give an agent has to carry that intent: "on the GPU, and fail if you can't".
raises: Last step: write the instruction you'll give every agent that runs cuPhoton for you.
:::
