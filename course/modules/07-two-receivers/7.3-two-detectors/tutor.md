# 7.3 · tutor notes

**Goal:** on real data, the learner finds that raw strain gives a plausible
wrong delay, fixes it by whitening, and judges the peak against a
background from the same data. The module exit (O7: what they'd check
first on their own recordings). Probes M-RAW-CORRELATES, M-PEAK-IS-SIGNAL.

Source: docs/guide/correlate.qmd (ArraySource; "Products are raw sums ...
no taper, mean removal or normalization. Add the pair ("a", "a") for an
autocorrelation to normalize by"). Data: `data/` in this module's course
folder, the two 32 s GWOSC files (4,096 Hz, GPS 1126259446 + 32 s, event at
GPS 1126259462.4, 16.4 s in). `gw_delay.py`, next to these notes: run it
in place, `python <course>/modules/07-two-receivers/7.3-two-detectors/gw_delay.py ...`,
from `work/07/` (outputs land there; it finds the course's `data/` itself).
Nothing is hidden in it: if they want to read or change it, copy it to
`work/07/` and run the copy with `DATA=<course>/modules/07-two-receivers/data`. GPU environment. Read
the files with h5py: `strain/Strain`, `Xspacing` 1/4096 s (no xDR here: not
FITS).

Physics facts (LIGO, PRL 116, 061102, 2016): GW150914 arrived at L1 first,
6.9 (+0.5/−0.4) ms before H1; sites 3,002 km apart (10.0 ms light time);
the detectors' arms are oriented so that the wave's strain appears with
opposite sign; distance about 410 Mpc (1.3 billion light years); false-alarm
rate below 1 per 203,000 years, from matched filtering and 16 days of
time-shifted background. The data are LIGO's, released by GWOSC under
CC BY 4.0: credit "LIGO Scientific Collaboration and Virgo Collaboration,
via GWOSC (gwosc.org)".

## Your turn `plan` (prediction)
- Collect the plan. Look for: the ±10 ms limit (from 3,002 km, if they
  ask: give it; it's in the lesson text), a peak somewhere inside it, and
  any idea of sign or of preprocessing. Don't suggest whitening yet.
- Run raw first, as asked: `python <gw_delay.py> correlate raw`, then the
  figure: `python <gw_delay.py> look 7.3_look.png`, `show_figure(slot="look")`.
  ```
  raw: peak over all lags at +39 samples (+9.52 ms); within ±10 ms at +39 samples (+9.52 ms), correlation negative
  ```
  Show the xBeam lines as an excerpt (ArraySource of CuPy float64 vectors,
  pair (H1, L1), window 1,024 = a quarter second, linear lags, cupy).
- Let them judge it from the figure: the raw strain is a slow wobble
  (hundreds of times the wave; the wave isn't visible in it), the noise
  spectrum is huge below 30 Hz and has narrow lines; the wave is in the grey
  band. Ask what the correlation is following. If they propose filtering,
  ask which band and why; whitening is the name (each frequency divided by
  that detector's own noise level, measured over the 32 s by Welch's
  method, then 35–350 Hz kept).
- Then `python <gw_delay.py> correlate whitened`:
  ```
  whitened: peak over all lags at -30 samples (-7.32 ms); within ±10 ms at -30 samples (-7.32 ms), correlation negative
  ```
  Pair (H1, L1): negative lag = L1 earlier. The sign of the correlation:
  arm orientation. One sample is 0.24 ms; LIGO's 6.9 ms is within two
  samples. A phase-slope reading (7.1) is possible over 35–350 Hz but noisy
  for a 0.2 s chirp; not needed.
- If they cast to float32: raw strain (~1e-19..1e-21) squared underflows
  float32 (smallest normal 1.2e-38), so autocorrelations come out 0 and a
  normalized correlation divides by zero. Keep float64 (the script does);
  whitened data is of order 1 and fine either way.
- **Pass:** they say why the raw result is wrong though inside the allowed
  range (it follows the loud low-frequency noise; a different quarter
  second moves it: +0.5 ms on the grid in the next turn), and read the
  whitened one: L1 first by about 7 ms, opposite sign. Settle.

## Your turn `is-it-real` (checkpoint)
- Collect their idea. Good answers: compare with the same correlation where
  there's no event (other stretches of the 32 s), normalized so values are
  comparable; count how many are as loud. Time-shifting one detector
  (LIGO's method) is also right; the script does off-source stretches.
- Run `python <gw_delay.py> background whitened 7.3_background.png`, then
  `show_figure(slot="background")`; and `background raw` (text is enough).
  ```
  whitened: event's quarter second: peak at -30 samples (-7.32 ms), rho -0.66. Background: 112 quarter seconds, median |rho| 0.18, loudest 0.58; 0 as loud as the event or louder.
  raw: event's quarter second: peak at +2 samples (+0.49 ms), rho -0.30. Background: 112 quarter seconds, median |rho| 0.19, loudest 0.60; 23 as loud as the event or louder.
  ```
  Normalization: each quarter second's cross-correlation divided by
  √(R_H1H1(0)·R_L1L1(0)), from the autocorrelation pairs the guide
  suggests. Background: quarter seconds more than 2 s from the event (the
  grid of 128 quarter seconds, minus those near the event).
- What it can claim: louder than every one of 112, so a chance below about
  1 in 100 for this analysis. Not more: the loudest background at 0.58 is
  close. LIGO's 5.1σ came from matched filtering and far more background.
- **Pass:** (a) a background from the same analysis on stretches without
  the event; (b) the event beats all of it whitened, not raw; (c) the limit
  of what 32 s can say. Two of three to start.
- Module exit (one question at most, then settle): "Your own recordings:
  what would you check first?" Look for: the largest delay the geometry
  allows and windows longer than it (7.1), the conventions' signs checked
  against a run with a known answer (7.2), the noise spectrum and whitening
  (7.3), a background from the same data (7.3), and the receipt
  (`ingest-manifest.json` for radio jobs). Settle, then `reveal("7.3")`.
