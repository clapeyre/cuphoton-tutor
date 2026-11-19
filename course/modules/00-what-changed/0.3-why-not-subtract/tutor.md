# 0.3 · tutor notes

**Goal:** the learner builds the plan align → match PSF, background and
brightness → subtract → find → decide, tied to the observing conditions
from 0.2.

Use the pair from 0.2 (`work/00/night1.npy`, `night2.npy`). If they're missing,
remake them with `work/00/two_nights.py`.

## Your turn `predict-plain` (prediction, not a checkpoint)
- One part at a time: first the level of empty sky, then what appears around
  each star. Accept any reasoned prediction; settle when both parts are said.
- Then make the plain subtraction: `work/00/0.3_raw_difference.png`, colour
  bar, **no offset removed** (say so in the caption if you change it).
  `show_figure(slot="raw-difference")`. Compare with their prediction in one
  `ask` line only if the turn is still open; otherwise leave it to the page.
- When they describe a positive patch beside a negative one, name it: a
  **dipole**. Misalignment as its cause is fine to confirm once they see it;
  don't offer any other cause (held back to 0.4).

## Slot `aligned-difference`
- Fill it in the same reply that settles `predict-plain` (before `your-plan`
  is answered: the plan rests on it): align night 2 onto night 1's grid
  (undo the shift and rotation you applied, with `scipy.ndimage` or by
  resampling), subtract, letter each remaining spot A, B, C… Save
  `work/00/night2_aligned.npy` and `work/00/0.3_aligned_labeled.png`.
- The background difference remains everywhere, and blur residuals remain at
  unchanged stars: a dark core (night 2's peak is lower) inside a bright ring
  (its light is spread wider). Don't name the cause of the rings yet.
- Before lettering or discussing any spot, read `work/00/truth.json` (made in
  0.2) and map each letter to what it is: unchanged star, the brightened
  source, the new source. The brightened source isn't "unchanged". Don't
  endorse rules of thumb such as "a dipole is a matching error, a single
  bright spot is real": 0.4 exists to undo them.

## Your turn `your-plan` (checkpoint)
- Ask one part at a time: steps and order first, then what each removes, then
  what to do with what's left.
- **Pass:** align → match PSF and background (and brightness scale) → subtract
  → find the residuals → decide whether each is a real change. Wording doesn't
  matter, but each step must be tied to the observing condition it removes,
  using the terms alignment, PSF and background.
- Hint (a): point back to their sorted evidence from 0.2. Hint (b): name
  "matching the blur". A pass after hint (b) needs a variant first.
- Probe M-ALIGN-BLUR ("alignment also fixes the blur"): the lettered rings
  are the evidence against it; ask what could leave something at an unchanged
  star. Probe M-SUBTRACT.
- If they say matching the PSF removes the dipoles, don't agree, and don't
  put it in the summary: in one line, point at the aligned figure, where
  alignment removed the dipoles and the unchanged stars left rings, and ask
  which step removes the rings. (That names no cause beyond the figures.)
- After settling, `reveal("0.3")`. The v1 video in 0.4 replays this plan on
  the real sample pair.
