# 5.4 · tutor notes

**Goal:** the learner turns this module's two silent problems (and Module
02's receipts) into per-image rules, and sees them run over every item of
the module's runs in an xLens dashboard. Module exit (O6, O3).

## Your turn `rules`
- **Pass:** at least two measurements and two rules, with at least one rule
  that would have caught a problem of 5.1 or 5.3 (PSF width missing / error
  terms excluded; kernel χ²/dof high or few fit pixels; fluxes NaN). Credit
  Module 02-style ones: reader and fallback reason, backend, candidate count,
  wall time. If they propose "flux bias" as a rule: it needs fakes in every
  image; good idea for a periodic check, not a per-image measurement.
- Build it with `watch_runs.py` next to these notes, run in place from
  `work/05/` with the GPU environment's python. Adapt its rules to theirs
  first (the `findings` block; thresholds are yours to argue), show them the
  changed lines:
  `python <this dir>/watch_runs.py xlens-state 5.4_dashboard.html run1 run2 inj/run-shipped inj/run-whole [run-final]`.
  It prints one line per sample (χ²/dof, finding codes) and the ingestion
  errors, and exports `work/05/5.4_dashboard.html`.
- Link the dashboard in your reply as
  `[the dashboard](/workspace/work/05/5.4_dashboard.html)`: it opens in a new
  tab, sandboxed. **Never** run `cuphoton xlens serve`: its default port is
  8765, this app's own port. Export only.
- Facts (verified with the module's runs, shipped rules in the script):
  every injection item under shipped kernel settings flags `kernel_fit_poor`
  (χ²/dof 15.6–15.8 on 4,743 px); the whole-image runs don't (1.29–1.31);
  run1 flags `no_psf_width` as well; every item flags `read_fallback` (info:
  xDR's native part isn't built here, 3.3); `uq_valid_low` (< 80%) fires on
  most whole-image items (~73% of rows valid) because new point sources are
  fitted as dipoles with an undefined centre (5.2): a rule that needs a
  better threshold or a narrower question (e.g. the psf_flux error only).
  Good to discuss: a noisy rule gets ignored.
- xLens traps (guide monitor.qmd): an analyser that raises becomes an
  ingestion error that keeps the exception class but not the message (debug
  by calling the analyser on one input directly); a file rewritten in place
  isn't re-read by a polling session; the page shows the last 256 samples.
- Settle when the dashboard is up and they've looked.

## Your turn `module-question` (module exit)
"Can you trust what a shipped pipeline writes on new data, and what does it
take to find out?" Not a checkpoint: settle on any honest answer with both
halves (not by default: it finished, but left out and biased things silently;
reading what it wrote and testing with known answers). One sentence connecting
to their 4.4 test at most. Then `reveal("5.4")`.
