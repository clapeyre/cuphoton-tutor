# 7.2 · tutor notes

**Goal:** the learner runs the radio path on the GPU (inspect, sidecar,
correlate), predicts and reads visibilities, finds the station with the bad
clock from which baselines slope, fixes it with the job's sign convention,
and checks the fix by rerunning. Probes M-WEIGHT-MEANS-RIGHT and
M-DELAY-SIGN.

Source: docs/guide/correlate.qmd ("Correlate radio recordings"),
docs/xbeam/README.md, data-contract.md, sidecars.md; the developer blog (13
Nov 2026, "Run GPU-powered black hole interferometry with NVIDIA cuPhoton")
for context. Two scripts next to these notes. **Run both in place, from the
course folder, with outputs in `work/07/`; don't copy `make_recordings.py`:
the answer is in it.** `visibilities.py` may be copied if they ask for it.

## Setup (when you prepare the lesson)
From `work/07/`, GPU environment:
```
python <course>/modules/07-time-series/7.2-radio-recordings/make_recordings.py radio
```
Writes `radio/AA.vdif`, `BB.vdif`, `CC.vdif` (4 MB each: 1 s, 16 MHz real
sampling, 2 bits, one 8 MHz band at 1.4 GHz, 500 frames of 8,032 bytes) and
`radio/job.json`. Run every xBeam command **from `radio/`**: the job's
`source_files` resolve against the working directory, not the job file.
The learner can read `job.json` in Files; point to `stations[].clock` and
`scans[0].station_models[].delay_coefficients_s`.

The truth (don't tell): the wavefront reaches CC 0.9 µs before AA and BB
2.3 µs after AA; the job has these right (BB `delay_coefficients_s`
[-2.3e-06], CC [9e-07]). BB's clock also stamps its samples 1.75 µs late;
the job's clocks are all 0. 20% of each recording is the shared sky.

## Your turn `first-fringes` (prediction)
- Collect the prediction for amplitude and phase. Expected reasoning:
  amplitude is the shared fraction (the same on every baseline, here, since
  every station sees the same sky), phase flat at 0 once the delays are
  right (7.1: a leftover delay would be a slope). If they have no basis for
  the amplitude, accept "some fraction, the same everywhere".
- Run, showing commands and outputs in code blocks (excerpts):
  ```
  cuphoton xbeam inspect-vdif AA.vdif --json        # headers only: station_codes ["AA"], 500 frames of 32,000 samples, 2 bits, real, invalid_sample_count 0, sampled_monotonic true
  cuphoton xbeam build-vdif-sidecar AA.vdif BB.vdif CC.vdif --index-dir sidecars --backend posix
  cuphoton xbeam correlate job.json --output run1 --backend cupy --index-dir sidecars
  python <course>/.../visibilities.py ../8.2_fringes.png run1
  ```
  `--backend posix` for the sidecars: GPUDirect Storage isn't available on
  this machine (3.3: no nvidia-fs); the default is `cufile`. Correlate
  takes about half a second. `run1/` holds `metadata.jsonl` (one line per
  record: antennas, time, weight, u/v/w), `spectra.c64` and
  `ingest-manifest.json`, the receipt: `backend: cupy`, `profile:
  analytic-v1`, the job's fingerprint, `effective_io_mode:
  binary-sidecar-mapped`. Show a few manifest lines.
- `show_figure(slot="fringes")`. Facts (real run):
  ```
  AA-BB: 5 integrations, weights 1.000, amplitude per channel 0.158, band-averaged 0.001, residual delay +1.75 us
  AA-CC: 5 integrations, weights 1.000, amplitude per channel 0.176, band-averaged 0.176, residual delay +0.00 us
  BB-CC: 5 integrations, weights 1.000, amplitude per channel 0.157, band-averaged 0.001, residual delay -1.75 us
  ```
  0.176 is the expected value: 20% shared power × 0.88, the efficiency of
  two-bit sampling with optimal thresholds.
- Compare with their prediction; let the mismatch stand for the next turn.
  Settle.

## Your turn `fix-it` (checkpoint)
- **Pass:** (a) BB: it's in both sloping baselines and not in the flat one
  (if they say "AA–BB and BB–CC are bad", ask what those have in common);
  (b) 1.75 µs, from the phase slope (7.1), or from 14 turns across 8 MHz;
  (c) a change to BB's clock (or its delay model) in the job, with a sign
  they've reasoned about, and a prediction of the rerun (all three flat).
- The sign: the job's delays say how much **earlier** the station hears the
  wavefront than the reference (DiFX's convention; measured here: BB, which
  hears it 2.3 µs late, needs -2.3e-06). xBeam adds the clock polynomial to
  the delay model (`compute_plan.py`, `_delay_values`). The user guide
  doesn't state the sign; that's why a rerun is the check. If they ask for
  +1.75e-6, run it: don't warn first. If they ask for -1.75e-6, run it, then
  ask what +1.75e-6 would have done, and show that run too.
- Make the change in a copy, `job-fixed.json` (show the diff), and run:
  ```
  cuphoton xbeam correlate job-fixed.json --output run2 --backend cupy --index-dir sidecars
  python <course>/.../visibilities.py ../8.2_fixed.png run1 run2
  ```
  `show_figure(slot="fixed")`. Facts:
  ```
  clock -1.75e-6: all three baselines amplitude 0.176-0.177, band-averaged 0.176-0.177, residual delay +0.00 us
  clock +1.75e-6: AA-BB +3.50 us and BB-CC -3.50 us, amplitude per channel 0.138, band-averaged 0.001; AA-CC unchanged
  ```
  Every run: weights 1.000, nothing on stderr.
- Why the per-channel amplitude drops a little: a delay error shifts the two
  stations' samples within each 256-sample transform; 1.75 µs is 28 samples,
  so about 11% of each transform doesn't overlap (0.176 → 0.158). Why the
  band average collapses: 14 turns of phase across the band sum to nearly
  nothing.
- Speed, if asked (3.4's habits: second run, whole command): three 8-second
  stations (`make_recordings.py big --seconds 8`, 32 MB each): GPU 0.68 s,
  CPU (`--backend numpy`, with `--max-read-bytes 4294967296`, since it
  decodes 1.9 GB on the host and refuses above its 1 GiB default) 16.3 s.
  One RTX 4070 Ti SUPER, 28 CPU threads. The blog's figure (10 TB in 70 s
  on 64 GPUs, 460× an x86 CPU baseline) is NVIDIA's own measurement on a
  Vera Rubin NVL72 with GPUDirect Storage; quote it as such.
- Real arrays: delays come from a geometric model computed for the
  stations' positions and the source (the job carries the polynomials);
  clocks are found the way the learner just did, by fringe-fitting a strong
  source. The Event Horizon Telescope correlates 2-bit recordings at up to
  64 Gbps per station (blog).
- Settle, then `reveal("7.2")`.
