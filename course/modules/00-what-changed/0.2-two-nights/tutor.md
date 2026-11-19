# 0.2 · tutor notes

**Goal:** the learner tells real changes from observing-condition differences,
each with evidence they asked for or looked at.

## On open: fill the slot `two-nights`
One script, `work/00/two_nights.py`, seed 2, 96×96:
- Reference: 8 Gaussian sources (σ=1.6 px), background 100, Poisson noise.
- Target: the same sources shifted by (+3, −1) px and rotated by 2°, σ=2.4 px
  (wider PSF), background 160, one source three times brighter, one new source
  that isn't in the reference. Same exposure time.
- Give each source a **total flux** and draw it as a normalised Gaussian
  (amplitude = flux / (2πσ²)), so a source keeps its light when the PSF
  widens: on night 2 an unchanged source's peak is (1.6/2.4)² ≈ 0.44 of
  night 1's, spread wider. The brightened source has 3× the flux (its peak
  is about 1.3× night 1's). Don't scale peaks instead: that adds light.
- Save `work/00/night1.npy`, `work/00/night2.npy`, and side by side on one
  colour scale with colour bars `work/00/0.2_two_nights.png`;
  `show_figure(slot="two-nights")`. Also save `work/00/truth.json` (never
  shown): each source's position on each night, its flux, and which one
  brightened and which is new. Read it before saying which spot is which.
- **Don't say what you changed** until the turn is settled, not in titles, file
  names or captions.

## Your turn `what-changed`
- When they ask for zooms, crops, profiles or pixel values, make them (annotated,
  colour bar, say any offset or stretch) and `show_figure(turn_id=...)` them into
  the conversation. Crop only the sources they ask about; if their pick is an
  unchanged star, ask them to pick another to compare, rather than cropping
  the changed one for them (which source changed is theirs to find).
- **Pass:** pointing, PSF and background, each with a piece of evidence the
  learner names, and at least one real change. Being on the list in the lesson
  text isn't evidence. If they only see the new source, ask about one source in
  both images.
- When they describe a blurrier source, give the term: "what you called *more
  spread out* is a wider **PSF**; here it comes from **seeing**."
- Before settling, ask them to sort their evidence into the two kinds (real
  change / observing conditions), using the terms.
- After settling, you may say what you built (shift, rotation, blur, background,
  the brightened and the new source). Then `reveal("0.2")`.
- Misconceptions: M-NEWSIGNAL (anything bright is new) shows up as "the
  brighter background is a change in the sky".
