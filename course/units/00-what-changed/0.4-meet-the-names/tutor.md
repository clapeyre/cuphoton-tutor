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
1. What could cause it?
2. What would you need to measure about it to tell those causes apart?
3. Which stage on the chain does that measuring?

- **Pass:** 1 and 2 unaided: misalignment or real motion, and the positions,
  brightness and widths of the two lobes **and** a comparison with the other,
  unchanged sources. Misalignment shifts them all the same way; real motion
  affects one source. Both give the same two-lobe shape
  (docs/guide/measure.qmd), so the lobes alone can't decide. 3 is read off the
  chain (xFit).
- If 2 needed a hint, set a variant before settling, e.g. "a single negative
  residual, with no positive lobe: what could cause it, and what would you
  measure?"
- Hold-back: the dipole's causes are this checkpoint. Don't state them anywhere
  (margin answers included) until the turn is settled.
- Before settling, ask them to say *why* in one sentence.
- After settling, `reveal("0.4")`.

## Unit exit
Before settling `two-lobes`, if the turn went well, ask the learner to say the
unit's question in their own words: "when so much else differs between two
nights, how do you find what really changed?" Put their answer, in their words,
in the settle summary.
