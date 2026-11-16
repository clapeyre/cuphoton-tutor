# 1.4 · tutor notes

**Goal:** the learner predicts what matching leaves, sees the difference image,
names kernel mismatch, explains the NaN edge, and doesn't take chi2/dof as proof.

## Video `v3-kernel` (opens the lesson)
Blur adds in quadrature (1.16² + 1.38² = 1.80²), the real kernel between a
reference and a target star, the 27-weight basis, kernel sum 1.013 = flux
scale. It deliberately states no kernel size (`nan-edge`) and says nothing of
what a wrong kernel leaves (`perfect-kernel`): don't fill those in early.

## Your turn `perfect-kernel` (prediction)
- **Pass (prediction):** perfect kernel → only noise at an unchanged star;
  slightly off → a small ring or dipole-like leftover (they saw rings in 0.3).
  Accept any reasoned answer, then run.
- Run the guide's xPois block in `work/01/subtract.py` (basis
  `GaussianBasisComponent(0.7, 4), (1.4, 2), (2.8, 2)`, `kernel_shape=(19, 19)`,
  `variance=target_variance`, `background_degree=1`, `backend="cpu"`), using the
  aligned arrays from 1.3. Save `work/01/difference.npy` and `kernel.npy`.
- Figure `work/01/1.4_difference.png`: the difference in grey scale centred on
  zero (clip ±5× the robust noise, say so), injected positions **not** marked,
  and a small inset or second panel of the kernel. Don't explain the edge band
  in the caption. `show_figure(slot="difference")`.
- After they've looked, name it: what an imperfect match leaves at an
  unchanged source is **kernel mismatch**. In 0.3 nothing matched the blur, so
  the whole PSF difference remained; here the kernel removes most of it.
- Facts: kernel sum 1.013 (≈ flux scale), chi2/dof 1.29, NaN edge 9 px.
- Settle `perfect-kernel` once the run is shown and compared with their words.

## Your turn `nan-edge` (checkpoint, hold-back on "kernel")
- **Pass:** the kernel's footprint (19 × 19, so 9 px each side) can't be applied
  where it would reach past the image edge; the matched reference is undefined
  there. "Because the kernel is 19 wide" with the 9-px link is enough.
- The v1 video in 0.4 says the frame is "where the blur can't be matched". If
  they quote it, ask *why* it can't be matched there.
- Hints: (a) "What does the kernel need around each pixel to compute it?"
  (b) name "the kernel's footprint". A pass after (b) needs a variant: "what
  would a 31 × 31 kernel do to the frame?" (15 px).
- After the pass, ask separately: "chi2/dof came out at 1.29. Does that prove the
  subtraction is good?" (M-CHI2-VALIDATES). If yes, ask which variance it was
  computed with: only `target_variance` goes in, reference noise is left out,
  and the two real changes raise it too. Don't rescale variance here (1.6).
- Settle with their reason; then `reveal("1.4")`.
