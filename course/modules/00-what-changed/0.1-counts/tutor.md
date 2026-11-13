# 0.1 · tutor notes

**Goal of the lesson:** the learner sees an image as an array of counts, with
noise that grows as the square root of the counts, and understands why that
makes long exposures worth having (signal-to-noise grows as √t).

## On open: fill the slot `toy-sky`
Make a toy sky in `work/00/` with NumPy and Matplotlib, in one script
(`work/00/toy_sky.py`, kept for the learner to read later):
- 64×64 pixels, flat background of 100 counts, four Gaussian sources (σ≈1.8 px)
  with peaks between 300 and 2000 counts, Poisson noise (`rng.poisson`), seed 1.
- Two panels: the image in grey scale (`cmap="gray"`, black = few counts) with
  a colour bar, one source circled; beside it the 5×5 pixel values around that
  source's centre, printed as a small table image.
- Save `work/00/0.1_toy_sky.png`, then `show_figure(slot="toy-sky")`.

## Your turn `twice-as-long`
The page now states both premises: counts are proportional to exposure time,
and the noise on N counts is about √N (Poisson). The turn is about *using*
them, not discovering them.
- **Pass:** source and background counts both roughly double; the noise grows
  by about √2, so less than the signal; so the source is easier to see.
  Accept this in any words ("the noise grows slower") — no need for the exact
  √2 if the direction and the reason are right.
- If they're unsure how the noise scales, point them back to the √N rule on the
  page in one sentence ("the page gives the rule: noise ≈ √counts. What are the
  counts now?"). **Don't** run a ladder of questions to extract it, and never
  make them derive Poisson statistics.
- Misconceptions to watch: thinking the background stays the same (it's light
  too, not a fixed floor); calling the background "the noise" (the background
  is a level of light; the noise is the wobble around it). If you see either,
  name the distinction in one line.
- Before settling, ask the *why* in one sentence: why does a longer exposure
  make the source easier to see?
- When you settle, add one or two sentences that link their answer to practice
  (long exposures, stacking, "four times the time for half the brightness").
  Then `reveal("0.1")`.
