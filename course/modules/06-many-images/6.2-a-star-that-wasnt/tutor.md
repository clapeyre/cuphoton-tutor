# 6.2 · tutor notes

**Goal:** the learner judges two reconstructions that passed validation,
uses the loss as the alarm, traces each fault to its frame (a cosmic ray,
a wrong PSF), fixes them (robust loss or a mask; the right PSF) and checks
the reruns. Probes M-VALID-MEANS-USABLE.

Source: docs/guide/reconstruct.qmd ("Save and validate a bundle": "An empty
list does not check every pixel value"; Options: `algorithm`, `rho_loss`,
`delta_rho_start`; "Run the reconstruction": the loss). `bundles.py`, next
to these notes. **Run it in place, from the course folder, with outputs in
`work/06/`; don't copy it: the answer is in it.**

## Setup (when you prepare the lesson)
From `work/06/`: `python <course>/modules/06-many-images/6.2-a-star-that-wasnt/bundles.py make b2`
writes `b2/bundle-1` and `b2/bundle-2` (issues `[]` for both).

The truth (don't tell): bundle-1 is 6.1's frames plus a cosmic ray, pixel
(row 30, column 12) of frame 2 raised by 40. bundle-2 is 6.1's frames with
frame 3's PSF recorded as 0.6 pixels wide; the frame was blurred by 1.2.

## Your turn `two-bundles` (prediction, then run)
- Collect what they'd look at first (receipt, loss, the picture against
  6.1's). Then run:
  ```
  python <course>/.../bundles.py run b2/bundle-1 runs bundle-1
  python <course>/.../bundles.py run b2/bundle-2 runs bundle-2
  python <course>/.../bundles.py figure 6.2_scenes.png runs/bundle-1 runs/bundle-2
  ```
  `show_figure(slot="two-scenes")`. Facts (real runs, GPU, about a second each):
  ```
  bundle-1: algorithm l2, device cuda, iterations 75, loss 2083.49
    sources: peaks 25.5, 43.0, 16.7; fluxes 30.5, 50.6, 20.4
    brightest pixel away from them: 25.6 at (30, 12)
    frame 1: chi-squared per pixel 341.6 · frame 2: 5770.1, worst pixel at (30, 12) · frame 3: 138.7
  bundle-2: algorithm l2, device cuda, iterations 75, loss 172.55
    sources: peaks 8.5, 14.2, 5.7; fluxes 30.0, 50.1, 20.0
    brightest pixel away from them: 0.2
    frame 1: chi-squared per pixel 254.9 · frame 2: 78.6 · frame 3: 184.2
  ```
  (6.1's clean bundle, the same check: 5.9, 1.8, 1.2.)
- Neither run failed or warned. Settle on their judgment: most distrust
  bundle-1 (an extra source) and miss that bundle-2 is wrong too until
  they see its loss or its blurrier peaks.

## Your turn `what-wrong` (checkpoint)
- Help them look; show code and output for each look:
  - The frames at (30, 12): frame 2 is about 40 above the sky there; frames
    1 and 3 have sky.
  - `bundles.py widths b2/bundle-1`: frame 2's "brightest star" is at
    (30, 12), measured width 0.24 px against a recorded PSF of 0.98: a
    single hot pixel. `bundles.py widths b2/bundle-2`: frame 3's stars
    measure 1.13 px, its recorded PSF 0.59 px; frames 1 and 2 match (0.80,
    0.98). (Widths are second moments on the 9 × 9 cutout; a 1.2-pixel
    Gaussian truncated at 9 × 9 measures 1.13.)
  - Per-frame chi-squared: for bundle-1 it singles out frame 2; for
    bundle-2 it doesn't single out frame 3 (frame 1 is worst), because a
    wrong PSF misshapes the whole scene. That's why the widths check
    matters.
- **Pass:** (a) bundle-1: a cosmic ray in frame 2, from the frames or the
  width; (b) bundle-2: frame 3's PSF is too narrow, from the widths; (c)
  fixes: for bundle-1 the robust reconstruction (`rho`) or a mask on that
  pixel; for bundle-2 the right PSF for frame 3; with a prediction for
  each. Two of three to start; ask about the third.
- Run the fixes:
  ```
  python <course>/.../bundles.py run b2/bundle-1 runs bundle-1-rho rho
  # bundle-2: copy it to b2/bundle-2-fixed, replace frame 3's PSF with a 1.2-pixel Gaussian (show the code)
  python <course>/.../bundles.py run b2/bundle-2-fixed runs bundle-2-fixed
  python <course>/.../bundles.py figure 6.2_fixed.png runs/bundle-1-rho runs/bundle-2-fixed
  ```
  `show_figure(slot="fixed")`. Facts:
  ```
  bundle-1-rho: algorithm rho, iterations 75, loss 1.33; peaks 20.1, 32.0, 13.3; fluxes 30.6, 51.2, 20.5;
                brightest pixel away from them 0.2
  bundle-2-fixed: loss 2.97; peaks 25.5, 43.0, 16.7; fluxes 30.6, 50.6, 20.4 (6.1's run exactly)
  ```
  The robust run's peaks are lower than L2's: it's a different fit and
  isn't converged either; the totals are what to compare. If they choose
  a mask instead: write `masks.npy` (True = good) with that one pixel
  False, set `mask.mode: provided`, and run L2; say you haven't a
  measured result for it in these notes and report what comes back.
- Settle, then `reveal("6.2")`.
