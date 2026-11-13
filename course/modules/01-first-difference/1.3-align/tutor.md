# 1.3 · tutor notes

**Goal:** the learner predicts and then sees xRep put the reference on the
target's grid, with variance and mask carried along.

## Your turn `which-grid` (prediction)
- Ask for both predictions, one at a time if needed. Accept any reasoned answer;
  this is a prediction, not a checkpoint.
- When they tell you to run it (or say "go"), run the guide's xRep block in
  `work/01/align.py` (`make_wcs_pair_transform`, `ReprojectionSpec` with
  `BBox(0, 0, target.shape[1], target.shape[0])`, `reproject_masked_array(...,
  backend="cpu")`). Save `work/01/aligned_reference.npy` and
  `aligned_variance.npy` for the next lessons.
- Figure `work/01/1.3_aligned.png`: aligned reference beside the target, grey
  scale, same stretch, a small circle on the same bright star in both.
  `show_figure(slot="aligned")`. Then compare with their prediction in your
  reply.
- Facts from the real run (pinned commit): result shape (256, 256),
  interpolation `lanczos3`, mask sum 0 (nothing uncovered).
- If they predicted the target moves: ask why cuPhoton might prefer to move the
  reference. Hint: it's the image that gets blurred in the next step (and it's
  the sharper one). Probe M-ALIGN-BLUR if they expect the stars to match now.
- **Settle** once the run is shown and they've said what it did and why the
  reference moved, in their words. Then `reveal("1.3")`.
