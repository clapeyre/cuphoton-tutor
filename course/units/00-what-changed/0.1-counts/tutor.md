# 0.1 · tutor notes

**Goal of the lesson:** the learner sees an image as an array of counts, with
noise that grows as the square root of the counts.

## On open: fill the slot `toy-sky`
Make a toy sky in `work/00/` with NumPy and Matplotlib, in one script
(`work/00/toy_sky.py`, kept for the learner to read later):
- 64×64 pixels, flat background of 100 counts, four Gaussian sources (σ≈1.8 px)
  with peaks between 300 and 2000 counts, Poisson noise (`rng.poisson`), seed 1.
- Two panels: the image with a colour bar, one source circled; beside it the
  5×5 pixel values around that source's centre, printed as a small table image.
- Save `work/00/0.1_toy_sky.png`, then `show_figure(slot="toy-sky")`.

## Your turn `twice-as-long`
- Premises to state if asked (never make them guess): raw counts, Poisson noise,
  nothing else changes between the two exposures.
- **Pass:** source and background both roughly double. If they also volunteer
  the noise: it grows by about √2, more slowly than the signal.
- If they only answer for the source, ask about the background, one question.
- Optional follow-up once they pass, with the noise model stated: "and the
  noise?" Settle on their words.
- Misconception to watch: thinking the background stays the same (it's light
  too, not a fixed floor). Not catalogued; file it if you see it.
- Settle with a one-line summary in their words; then `reveal("0.1")`.
