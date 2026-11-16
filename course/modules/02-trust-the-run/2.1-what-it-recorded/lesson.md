---
id: "2.1"
title: What did the run record?
question: When a run finishes, what does it tell you about itself?
terms: [backend, device, receipt, artifact, profile]
---

:::video v2-it-ran
:::

cuPhoton ships a quickstart runner that exercises five components (xRep, xPois,
xFit, xScan and xRay, a detector-signal module we won't use) on small synthetic
inputs. It's the quickest way to check an installation, and a good first run to
read closely. We ask for the CPU explicitly: `--profile cpu`.

Every component has a [[backend]], the library doing its arithmetic, and runs
on a [[device]], the CPU or a GPU. Each run writes its outputs, the
[[artifact|artifacts]], into an output directory, together with a
[[receipt]]: a `summary.json` that records what was asked for and what
actually happened.

:::your-turn predict-record
title: Before you look
prompt: Ask the tutor to run the quickstarts on the CPU. Before you see anything it wrote, what do you think the run recorded about itself? Make a list.
:::

:::slot receipt
title: The receipt
caption: The main fields of the root summary.json, one row per component.
:::

:::your-turn where-xfit
title: Where did xFit run?
prompt: Where did xFit run, and how do you know?
:::

:::closure
found: The receipt records the request (profile cpu, no GPU required), the hardware (no usable GPU in this environment), and for each component the backend and device that actually ran, with the dtype. xFit ran with the numpy backend on the cpu device: you know because the receipt says so, not because nothing went wrong.
matters: Notice the names: the CPU backend is called numpy in xFit and cpu in xPois and xRep. Receipts are the one place where every such detail is written down, which is why the rest of this module is about reading them. A clean exit and a status of ok are the least informative fields in the file.
raises: What happens if you run exactly the same command again?
:::
