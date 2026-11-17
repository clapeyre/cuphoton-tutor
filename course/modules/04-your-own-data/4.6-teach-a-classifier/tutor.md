# 4.6 · tutor notes

**Goal:** the learner designs a training set from this pair, trains xScan on
the GPU, reads a perfect test score, then finds and fixes what it has never
seen. Module 04's exit (O5). Probes M-TEST-SCORE-COVERS and M-SCORE-PROBABILITY.

Source: docs/guide/classify.qmd (the dataset files, the label guard, the CLI,
the tiny model config, "What is survey-specific"), the pinned checkout.
Everything runs with the GPU environment from `work/04/`, with
`classify.py` next to these notes copied there (env `DATA` if the data isn't
in `work/04/data`). Its docstring describes every choice.

## Your turn `labels` (design)
- Collect their design. Look for: real = sources they plant (the 4.4 recipe:
  the target's PSF, a range of fluxes, on usable pixels); bogus = things
  that are in both nights and leave residues (stars, knots of the galaxy),
  or other junk they can name. Not the supernova or 4.3's four: those are
  what it will be tested on. If they propose labelling the real hotspots by
  eye, say why that's too few here (one real among 19) and ask what else
  they could use. One question at a time; don't hand them the design.
- If they ask for cosmic rays or trails in the bogus class now, take it
  (`--with-rays-and-trails`) and adapt the `never-seen` turn: ask what else is
  missing (variable stars; asteroids; other surveys' bogus). Facts for that
  case are under "Retrained" below.
- Run, showing commands and outputs in code blocks:
  ```
  python classify.py build ps1
  cuphoton xscan data-validate --dataset-dir ps1
  cuphoton xscan data-check-training-labels --dataset-dir ps1 --require-ok
  cuphoton xscan train-inada-triplet --config ps1/train.yaml > ps1-train.json
  cuphoton xscan evaluate-real-bogus --run-dir runs/ps1 --dataset-dir ps1 > ps1-eval.json
  python classify.py score ps1 runs/ps1 4.6_scores.png
  ```
  The dataset: 568 candidates (480 fakes, flux 800–8,000 counts; 88 stars and
  knots), each as 4 rotations that share a `split_group`, so 2,272 cutouts of
  21 × 21; split 60/20/20 by group. `label_source` is `injection` or `star on
  both nights`; the label guard passes. The model is the guide's tiny one
  (two stages, 16 wide), 10 epochs with early stopping on validation loss,
  on CUDA, a few seconds.
- Point out, when they come up: the label guard checks that copies of one
  candidate never straddle splits (why the rotations share a group); and
  that each cutout is in units of its own noise, so the checkpoint only
  fits cutouts prepared the same way (the guide's "What is
  survey-specific").
- `show_figure(slot="scores")`. Facts (training isn't bit-reproducible on a
  GPU; these held over 3 dataset seeds): test ROC AUC 1.000, PR AUC 1.000,
  0–1 errors at threshold 0.5; A 0.00, B 0.00, C (the supernova) 1.00,
  D 0.00; of the 19 hotspots of 4.2, only the supernova above 0.5. The
  supernova (43,000 counts) is brighter than any fake; it still scores 1.00.
- Settle on the run.

## Your turn `never-seen` (prediction, then checkpoint)
- Collect their list and prediction first. 4.3's intro named cosmic rays and
  satellites; if they don't think of them, ask what 4.3 said bogus
  candidates are made of.
- Then run `python classify.py stress ps1 runs/ps1 4.6_stress.png` and
  `show_figure(slot="stress")`, output in a code block. Facts (40 each, on
  empty sky, not seen in training; ranges over 3 dataset seeds):
  one-pixel cosmic rays called real 17–25/40 (median score 0.4–0.6),
  two-pixel 26–34/40, trail segments 34–39/40. New light of 1,500 counts
  on top of a fainter source that is in the reference (a supernova in a
  knot of its galaxy): 60/60 real, same as on empty sky. So it did not
  learn "anything in the reference is bogus".
- **Pass:** (a) it fails on kinds of bogus that weren't in training; (b) the
  perfect test score couldn't show that, because the test split holds the
  same kinds as training; (c) the fix: put those kinds in the bogus class
  and test again on fresh ones. Then run it:
  ```
  python classify.py build ps1-rays-trails --with-rays-and-trails
  cuphoton xscan data-check-training-labels --dataset-dir ps1-rays-trails --require-ok
  cuphoton xscan train-inada-triplet --config ps1-rays-trails/train.yaml > ps1-rays-trails-train.json
  python classify.py stress ps1-rays-trails runs/ps1-rays-trails 4.6_stress_after.png
  ```
  **Retrained** facts: 808 candidates (adds 80 each of one-pixel rays,
  two-pixel rays, trails, seed 21; the stress test uses seed 3); test ROC
  AUC 1.000; 0/40 of each kind called real; still 60/60 for new light on a
  source or on sky; A–D unchanged.
- On the score as a probability (if they read 0.99 as "99% sure"): the
  guide says it isn't calibrated. The training set is 85% real; a real night
  is mostly bogus; the score ranks, it doesn't give odds. A threshold is
  chosen on validation data for the miss and false-alarm rates you accept.
- What the synthetic cosmic rays and trails can't cover: real cosmic rays and trails
  have shapes these don't (ours are one width, one brightness profile);
  surveys label real ones by hand, which is what xScan's review queue
  (`cuphoton xscan review-queue`) is for. Mention, don't run.
- Settle.

## Your turn `next-night` (module exit)
- Their instruction for an agent processing the next night of this survey.
  Look for: data checks (grid/WCS, sky-subtracted or not, units, header
  values not trusted blindly, e.g. the zero point), the noise model (survey
  variance map, masked variances excluded, not set to 0), masks (which
  bits), the reference (which nights, if stacked: chosen by seeing, variance
  carried), the run (whole chain, GPU, receipts), the evidence back
  (overview figure, candidate stamps, z, fluxes with errors, the receipt),
  an injection test with the pull-scatter check and the error-bar correction
  it implies, and the sorting: which classifier, trained on what, checked
  against which kinds of bogus.
- One question at most for a missing piece that matters; don't make them
  polish wording. Then compare with their 2.6 list in one or two sentences:
  what real data added. Settle, then `reveal("4.6")`.
