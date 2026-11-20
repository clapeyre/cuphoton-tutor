# 0.4 · tutor notes

**Goal:** the learner maps their plan onto xRep, xPois, xFit, xScan, and can
reason about a dipole from evidence.

The chain on the page: xRep aligns (cuPhoton calls it reprojection); xPois
matches PSF, brightness and background, subtracts, and flags what's left
worth measuring, the **candidates**; xFit measures each candidate; xScan
scores each as **real or bogus**. Ground this in the "Choose a workflow" table
of the cuPhoton README if asked.

## Your turn `two-lobes` (checkpoint)
The figure is an example made for this question, not from our pair. Ask one
question at a time:
1. Misalignment is a given (the video says so, and 0.3's aligned difference
   showed alignment removing them): what else could make one?
2. What would you need to measure about it to tell those causes apart?
3. Which stage on the chain does that measuring?

- **Pass:** 1 and 2 unaided: a second story (real motion; or a source that
  faded next to one that brightened), and a comparison with the other,
  unchanged sources, using some measurement of the lobes (offset, direction,
  size or flux: any one is enough, don't drill for a full list).
  Misalignment moves every source by one geometric rule (the same offset for a
  pure shift; with a rotation, an offset that changes smoothly across the
  image); real motion affects one source.
  Both give the same two-lobe shape (docs/guide/measure.qmd), so the lobes
  alone can't decide. 3 is read off the chain (xFit). An answer that already
  has 1 and 2 passes: go to 3, don't ask for more detail first.
- A small rotation is misalignment too (one geometric story, which xRep
  fixes), not a second story: say so in a line and ask again for one that
  isn't geometry.
- If 2 needed a hint, set a variant before settling (a leading prompt counts
  as a hint: "anything else in it?", "suppose every other star is clean"), e.g. "a single negative
  residual, with no positive lobe: what could cause it, and what would you
  measure?"
- Hold-back: the second story (real motion) and the comparison with the
  unchanged sources are this checkpoint. Don't state either anywhere (margin
  answers included) until the turn is settled. Misalignment you can name.
- Before settling, ask them to say *why* in one sentence.
- After settling, `reveal("0.4")`.

## Module exit
Before settling `two-lobes`, if the turn went well, ask the learner to say the
module's question in their own words: "when so much else differs between two
nights, how do you find what really changed?" Put their answer, in their words,
in the settle summary.
