# 7.1 · tutor notes

**Goal:** the learner predicts and reads a delay two ways (lag peak, phase
slope), then meets readings that are wrong without an error, and names
what tells them apart. Probes M-PEAK-IS-SIGNAL.

Source: docs/guide/correlate.qmd (the sample pair, "Read the delay from the
lag correlation", "... from the cross-spectrum", Options, Troubleshooting:
"The lag peak is at the wrong place. The delay can exceed the window"),
docs/xbeam/time-series.md. `delays.py`, next to these notes, does both turns.
**Run it in place, from the course folder, with outputs in `work/07/`; don't
copy it:** the hidden delays are in the file, and the learner's Files panel
shows `work/07/`. GPU environment. Module 07 is a track: if this is the
learner's first visit to `work/07/`, create it.

## Video `v7-two-receivers` (opens the module)
One wave reaching two dishes at different times, what a dish records (noise
with a faint shared pattern), sliding one recording past the other until
the products line up and the sum peaks (real xBeam curve), why baselines
matter (the EHT), and the module's three lessons. Added after walkthrough 8:
the author, new to radio astronomy, found the module hard to picture. If a
learner seems lost on what's being measured, offer it, and use its words:
two receivers, one source, a delay. It shows a peak right of zero but never
says what a positive lag means in xBeam: the `known-delay` turn's sign
question still stands.

## Setup facts
- xBeam takes NumPy or CuPy vectors in `ArraySource({"a": a, "b": b},
  sample_rate_hz=...)`; `CorrelationSpec(pairs=(("a", "b"),),
  window_samples=1024, windows_per_result=4, output="both",
  backend="cupy")`; `correlate_series(source, spec)` yields results. On the
  GPU the results come back as host NumPy arrays (guide, "On a GPU"; add
  `result_location="device"` to keep them on the GPU). Show these lines as
  an excerpt when you run; the learner hasn't seen xBeam code before.
- Products are raw sums: no taper, mean removal or normalization (guide).
- Convention (guide): R(k) = Σ a[n]·conj(b[n+k]); a positive lag means the
  second signal of the pair arrives later.

## Your turn `known-delay` (prediction)
- Collect the prediction (where, and which sign). Most will say 7; the sign
  is the real question. If they can't predict the sign, accept "I'd check
  the guide's convention" and give it after the run.
- Run `python <course>/modules/07-two-receivers/7.1-a-known-delay/delays.py known 7.1_delay.png`
  from `work/07/`, then `show_figure(slot="delay")`.
- Facts (real run, GPU; signals made like the guide's: 8,192 samples at
  1,024 Hz, noise of half the signal's size; 2 results of 4 windows):
  ```
  b 7 samples late: lag peak +7, phase slope +6.99 samples; pair (b, a): lag peak -7, phase slope -6.99
  b 7.4 samples late: lag peak +7, phase slope +7.39 samples; pair (b, a): lag peak -7, phase slope -7.39
  ```
  Under a second, warm. Across 0–512 Hz the phase rises 3.5 turns for 7
  samples (half a turn per sample: phase 2πfτ, up to f = fs/2).
- Why the phase slope sees fractions: the peak can only sit on whole lags;
  at 7.4 it spreads over 7 and 8 with ringing around them (the figure). The
  phase is continuous in τ.
- **Pass:** they read +7 and why it's positive (second signal later), and
  say which reading gives the fraction (the phase slope) and why. Settle.

## Your turn `hidden` (prediction, then checkpoint)
- Collect what they'd trust. Don't reveal the delays (900 and 1,500) until
  they've judged the output.
- Run `python <course>/.../delays.py hidden` from `work/07/` and show the
  output whole:
  ```
  pair 1, linear  : +900 (11.5); +900 (12.1); +900 (13.5); +900 (11.5)
  pair 1, circular: -124 (6.4); -124 (8.1); -124 (7.9); -124 (6.5)
  pair 2, linear  : +178 (7.4); +195 (7.2); -111 (7.9); -5 (11.2)
  pair 2, circular: -383 (4.9); +384 (4.5); -65 (5.2); -5 (6.9)
  For comparison, the 7-sample pair in the same setup: peak/median 56 to 97.
  ```
  (numbers in brackets: peak/median |correlation|; 4 results of 2 windows.)
- What's happening: linear mode zero-pads, so its lags run to ±1,023; at
  900 only 124 of 1,024 samples overlap in each window, hence the weak but
  correct peak. 1,500 is beyond any lag the window has: every peak is
  noise. Circular mode wraps: a lag of 900 in a 1,024-sample circle is
  −124. Guide, Options (`lag_mode`) and Troubleshooting.
- **Pass:** (a) pair 2 is noise: results disagree and peaks are low; (b)
  pair 1 linear is believable (agrees, well above typical) and circular is
  wrong though consistent, because circular mode wraps; (c) the fix: a
  window longer than the largest delay possible, in linear mode, and a
  check of the peak against the rest and against what the geometry allows.
  Two of the three to start; ask about the third.
- If they trust pair 1 circular because it agrees with itself: ask what a
  lag of 900 looks like on a circle of 1,024 (hint ladder (a) → (b): the
  guide's `lag_mode` row).
- If asked "how high is high enough?": not settled here; 7.3 measures it
  against a background. Settle, then `reveal("7.1")`.
