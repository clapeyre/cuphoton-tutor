# 0.2 · tutor notes

**Goal:** the learner tells real changes from observing-condition differences,
each with evidence they asked for or looked at.

## On open: fill the slot `two-nights`
One script, `work/00/two_nights.py`, seed 2, 96×96:
- Reference: 8 Gaussian sources (σ=1.6 px), background 100, Poisson noise.
- Target: the same sources shifted by (+3, −1) px and rotated by 2°, σ=2.4 px
  (wider PSF), background 160, one source three times brighter, one new source
  that isn't in the reference. Same exposure time.
- Save `work/00/night1.npy`, `work/00/night2.npy`, and side by side on one
  colour scale with colour bars `work/00/0.2_two_nights.png`;
  `show_figure(slot="two-nights")`.
- **Don't say what you changed** until the turn is settled, not in titles, file
  names or captions.

## Your turn `what-changed`
- When they ask for zooms, crops, profiles or pixel values, make them (annotated,
  colour bar, say any offset or stretch) and `show_figure(turn_id=...)` them into
  the conversation.
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
