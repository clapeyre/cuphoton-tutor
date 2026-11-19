# 6.3 · tutor notes

**Goal:** the learner builds (with you) an xImage bundle from real frames,
calibrates the scene's fluxes with fakes and finds them off by 10% against
the median with a third of the scatter, then sees what a reconstruction
does to the supernova, a source that changed. Probes M-ONE-SCENE and,
again, M-SHARP-MEANS-RIGHT.

Source: docs/guide/reconstruct.qmd ("Read the run directory": "The run
returns no output variance and no effective PSF for the scene"; the
opening: "one nonnegative scene"), docs/components/ximage.md; Module 04's
data (`course/modules/04-your-own-data/data/`, its README for credit).
`nights.py`, next to these notes. **Run it in place, from the course
folder, with outputs in `work/06/`; don't copy it: the fakes' answer is
in it.** It finds Module 04's data itself (or `DATA=...`).

## How the bundle is made (show the `build` function when they ask, and
## go through these as decisions, not as givens)
- Cut: 160 × 160 around SN 2011fe (row 400, column 402 of the 800 × 800
  frames); the region reconstructed is the central 136 × 136 (a 25 × 25
  PSF needs 12 real pixels beyond each edge under `VALID`).
- Zero points: each frame × 10^(0.4 (24.6 − FPA.ZP)), variance × its
  square: scales 1.035, 0.998, 0.944, 1.000.
- Masks: PS1 mask 0 = good (Module 04's README); bad pixels also get value
  0 and variance 1e10. The 2012 frame is 75% usable here (a chip gap
  crosses the cut); the 2011 ones 97–98%.
- PSFs: a 25 × 25 Gaussian per night with σ = CHIP.SEEING / 2.355 (1.46,
  1.63, 1.97, 1.52 px). Real PS1 PSFs have wings a Gaussian lacks; the
  fakes are planted with the same Gaussians, so the fake test checks
  xImage, not the PSF model. Say so if they ask how far the test reaches.
- Configuration: the checkout's L2 (or rho) example, region as above,
  `mask.mode: provided`.

## Your turn `fakes` (prediction)
- Before running, go through the build decisions above (zero-point
  scales, mask rule, PSF σ from seeing) in one short message with the
  numbers, and ask them to check one against the headers or the data. If the
  lesson's request to check them comes up, this is it; don't skip it to run.
- Collect the prediction (how close to 2,000 in each, which scatters
  less). Most expect the scene to be both closer and tighter.
- Run from `work/06/`:
  ```
  python <course>/modules/06-many-images/6.3-four-nights/nights.py run m101 refs
  python <course>/.../nights.py figure 6.3_fakes.png m101/runs/refs
  ```
  `show_figure(slot="fakes")`. Facts (real run, GPU, about 1 s):
  ```
  reference    MJD 55673.44  seeing 3.43 px (PSF sigma 1.46)  scale 1.035  usable 97%  sky sigma 12.8
  reference-b  MJD 55673.45  seeing 3.84 px (PSF sigma 1.63)  scale 0.998  usable 97%  sky sigma 12.1
  reference-c  MJD 55692.33  seeing 4.65 px (PSF sigma 1.97)  scale 0.944  usable 98%  sky sigma 10.9
  validate_bundle issues: []
  device cuda, iterations 47, loss 1.43
  24 fakes of 2000: measured/planted in the scene: median 1.151, scatter 0.050;
                    in the median of the frames: median 1.051, scatter 0.164
  ```
  Measured with apertures and a local sky ring (5 px in the scene, 8 px in
  the median, which is blurrier). The run converged (47 iterations, under
  the 75 cap).
- Then the second half of the prompt: before measuring anything real,
  calibrate the scene with fakes at the same settings and divide by the
  ratio; the guide says the run gives no variance and no PSF for the
  scene, so its error bars come from the fakes' scatter too.
- **Pass:** they read the 10% offset against the median and the scatter
  three times smaller, and say they'd calibrate with fakes before using a
  flux. Settle.
- Deeper facts, only if asked (17 Nov runs; they are messy, say so):
  - The ratio depends on settings. Forced to 300 iterations (`--max-iter
    300 --stop-tol 1e-12`): 1.084, scatter 0.055. Measured as the
    difference between runs with and without the fakes (no sky ring), in
    3/5/8-pixel apertures: 1.094/1.048/1.024; the median of the frames
    the same way: 0.995. So part of the 5% the median shows is the sky
    ring in a galaxy, and the scene's light around a source is
    redistributed (the rings of 6.1).
  - These frames are sky-subtracted: their sky is near 0, with negative
    noise, and the scene is nonnegative. Adding a constant (a pedestal,
    `--pedestal 300`) changed the ratio to 1.056 at the default stop, but
    to 0.852 at 300 iterations, and it makes the run stop early (the
    update score is relative). We did not find a setting that is right
    without calibration; don't recommend one.
  - Speed: this cut takes about a second on either device. A 600 × 600
    cut of the same three nights (`HALF=300 ... --pedestal 300`): GPU
    3.2 s, CPU 16.1 s (28 threads), same 26 iterations and loss. xImage's
    `benchmark-devices` command times whole workflows the same way.

## Your turn `supernova` (prediction)
- Collect the prediction for each scene. Common: L2 shows it at a quarter
  of its brightness (one night in four); rho removes it.
- Run:
  ```
  python <course>/.../nights.py run m101 all --nights all --fakes 0
  python <course>/.../nights.py run m101 all-rho --nights all --fakes 0 --algo rho
  python <course>/.../nights.py figure 6.3_supernova.png m101/runs/all m101/runs/all-rho
  ```
  `show_figure(slot="supernova")`. Facts:
  ```
  light at the supernova's position (5-pixel aperture): frames reference -20, reference-b 243, reference-c 38, target 46414
  all (L2):   iterations 75, loss 2.14, scene 3615
  all-rho:    iterations 46, loss 0.62, scene 416
  refs only (pre-supernova, 6.3's first run): loss 1.43, scene 292
  ```
  L2 forced to 236 iterations: 3,659; the smudge doesn't grow towards a
  quarter. It's 8% of the 2012 aperture, not 25%. We haven't pinned down
  why (the fit is nonnegative, variance-weighted and blurred differently
  per night); say so rather than offering a mechanism.
- The scenes' texture ("worms" in the galaxy's light): a nonnegative scene
  fitted to noisy, sky-subtracted frames sharpens the noise too. It's
  what the evaluation's `sky_sigma` would report as a larger scatter than
  the median's.
- **Pass:** they say neither scene is right about the supernova, why (one
  scene for all frames: something that changed is either averaged into a
  ghost or rejected as an outlier), and that change is the difference
  chain's job (Modules 01–05), while xImage is for what stays put. The
  loss rose (1.43 → 2.14) but no warning came.
- Settle, then `reveal("6.3")`. This is the last track; the course's map
  (9.1) comes next.
