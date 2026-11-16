---
id: "2.2"
title: Run it again
question: What happens if you run exactly the same command twice?
terms: [artifact]
---

Agents rerun things all the time: after a tweak, after an interruption, or
just to check. The quickstart runner has a rule about where its outputs go,
written in its documentation's "output contract": every run needs a new output
directory.

:::your-turn predict-rerun
title: Same command, again
prompt: Predict what happens if the tutor reruns the identical command, with the same output directory. Then ask it to.
:::

:::your-turn what-do-you-say
title: What do you tell your agent?
prompt: Your agent reports "run failed: output directory already exists, remove it first". What do you tell it, and why?
:::

:::closure
found: The runner refused to overwrite: exit status 1 and "output directory already exists; remove it first". That's by design: a run's artifacts are its evidence, and a new directory per run keeps every result. The right instruction is a new directory name, not deleting the old one, unless you've checked it holds nothing you need.
matters: "Remove it first" is exactly what an agent in a hurry will do, and it destroys the evidence of the earlier run. Even the failed rerun printed the earlier run's summary, status ok and all, on its standard output, with the error only on standard error: an agent that reads just the output would call it a success. Exit codes and error streams are part of the receipt too.
raises: So far we asked for the CPU by name. What does cuPhoton do when you let it choose?
:::
