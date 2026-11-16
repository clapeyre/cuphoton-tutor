---
id: "4.3"
title: Real or bogus?
question: Which of the spots that passed the threshold are real changes in the sky?
terms: [real / bogus, candidate, kernel mismatch]
---

Every spot above the threshold is a [[candidate]]. On real data most
candidates are bogus: leftovers of an imperfect match, detector defects,
cosmic rays, satellites. Surveys rank them with trained classifiers (in
cuPhoton, xScan), but the classifier learned from people who looked. Here you
look.

:::slot candidates
title: The strongest candidates
caption: Each candidate in the reference, the target and the difference over its noise.
:::

:::your-turn sort-them
title: Sort them
prompt: For each candidate, real or bogus, and what's your evidence? Ask for anything that would help you decide.
:::

:::closure
found: One candidate is real: a round, positive source in the target with nothing at all in the reference, the shape of a point of light. It's SN 2011fe, a white dwarf that exploded in M101 in August 2011, seen here eight months later, still about magnitude 15. The others sit on bright stars that are in both nights, and leave twisted positive-and-negative residues: kernel mismatch, where the blur and position match wasn't perfect for those stars.
matters: The evidence that sorted them was the same each time: is there a source in the reference? Does the residue have the shape of a point of light? Is it positive, or a twisted pair? A classifier automates exactly these questions, and when you're checking its output, or your agent's, these are the questions to ask.
raises: You found one supernova. But what about the ones you didn't find? Without an answer key, how faint could a change be before this pipeline misses it?
:::
