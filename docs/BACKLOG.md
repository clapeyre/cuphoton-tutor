# Backlog

Parked requests, ideas and concerns: things we agreed matter but aren't doing
now. Newest at the top of each section. When an item is done, delete it here
and mention it in the commit. Walkthrough notes stay in `docs/walkthrough-*.md`;
anything parked from them is copied here with a pointer back.

## Course content

- **Predictions that hinge on trivia** (walkthrough 4, 3.3, second pass).
  Some Your-turn predictions can't be reasoned out (a library default, a
  format's rules). The tutor now treats "I can't tell, I'd check X" as a
  good answer, and 3.3's prompt says so. Not done: go through every
  prediction prompt and either give the fact it hinges on in the lesson
  text, or turn it into "what would you check?".
- **Module 02 is tied to today's CLI behaviour** (walkthrough 3, "Overall").
  Several lessons rest on details that could change in any cuPhoton release:
  the runner refusing an existing directory, the stale summary on stdout, the
  exact receipt fields, error messages. Worth it for now (learners do trip on
  these basics), but long term:
  - teach the durable idea (receipts, auto vs named, intent) and treat the
    specific fields as examples, so a change means editing facts, not lessons;
  - make every tutor-notes "Facts (real run…)" block re-checkable by a script,
    run whenever `course.yaml`'s pinned commit is bumped.
- **Learner preferences that apply course-wide** (walkthrough 1/2 discussion):
  e.g. "I'm colour-blind" or "less maths, please". The tutor honours this in
  conversation today, but there is no persisted preferences store that every
  later figure and lesson reads. Would make prepare-ahead regenerate on change.
- **Module 04 data source:** IRSA's ZTF image services were down on 16 Nov
  2026 (HTTP 502 from IRSA), so the module uses Pan-STARRS1 instead. Its
  nights are pre-aligned to a sky grid, so xRep has nothing to do there. A
  ZTF pair (different pixel grids, a reference coadd) would exercise
  alignment on real data too; worth revisiting when IRSA is reachable.
- **Module 04 at compute centres:** learners' own instruments differ; the
  lessons ask the right questions, but a "bring your own pair" path (the tutor
  adapting the notes to unknown headers) is untested.

## Coverage (cuPhoton beyond the optical chain)

From the 16 Nov coverage review. The low-hanging fruit (re-pin, a map
lesson, Module 05 on the shipped transient chain, error budget and xLens) is
planned in `docs/EXPANSION-PLAN.md`; coverage status is in `docs/ROADMAP.md`.

- **Component tracks and scale-out** moved to `docs/ROADMAP.md` (17 Nov):
  the tracks are required before the course is shown; scale-out is out of
  scope by decision.
- **Inputs beyond FITS.** cuPhoton no longer reads HDF5 itself (the Legate
  loader was removed; the docs say use h5py), and VDIF belongs to xBeam.
  Non-FITS labs may assume cuPhoton is FITS-only; the xBeam track will show
  VDIF.
- **Re-check coverage at every re-pin.** The guide grew from 4 to 15 chapters
  between our pin and 0.3.0.dev; diff its "Find your task" table against the
  course whenever `course.yaml`'s commit moves.

## Coherence with the user guide

- **Drift towards the guide** (https://nvidia.github.io/cuPhoton/main/, built
  from `docs/guide/` in the checkout). Asked 16 Nov 2026: not a copy, but lean
  towards it wherever a choice is open, so a learner who opens the guide after
  the course finds the same shape. Concretely, when the occasion comes up:
  - **Structure:** its chapters are task-first (read FITS, align, subtract,
    measure, classify, the transient chain, uncertainty, then the other
    components). Lessons could name and link "their" chapter (Module 06 already
    does); module order already roughly follows it.
  - **Data:** the guide's examples use its synthetic sample pair
    (`docs/guide/_sample-pair.qmd`), which Module 01 already uses via
    `make_sample.py`; check they stay the same pair at every re-pin. Prefer the
    guide's examples and parameters over invented ones for new exercises.
  - **Words:** use the guide's terms where ours differ (vocabulary.yaml cites
    sources; add the guide chapter where it has the term).
  - Check at every re-pin, with the coverage diff above.

## App

- **Editing files in the Files panel** (walkthrough 6, 5.1). The panel is
  read-only by decision: changes go through the tutor. Editing in the
  browser would race the tutor's own writes and needs save/conflict
  handling. Revisit only if learners keep wanting to tweak a configuration
  by hand.
- **More in the Files panel** (walkthrough 6, 5.1). It shows text files and
  figures in `work/<module>/`. Not yet: the course data and the pinned
  checkout's shipped files (e.g. `config-generic.yaml` before it's copied),
  a FITS header view (Module 04 reads headers a lot), and a first-rows view
  of Parquet catalogs (5.2). The list doesn't refresh while the tutor works,
  only when it goes idle, or on Refresh.
- **Prepare-ahead looks one lesson ahead only.** Jumping ahead still waits.
- **"Ask about" for prose:** selecting text to ask was removed (walkthrough 2,
  1.7: it stole the cursor). A deliberate affordance on paragraphs could come
  back later.
- **Tutor latency:** about 2 s before the first word, even though thinking is
  already off (`TUTOR_THINKING=off`): it's the endpoint's time to first token on
  a long, mostly cached context. Worth measuring per model in the comparison.
- **Cold GPU start isn't reproducible here:** the first GPU quickstart took
  28 s (CuPy compiling kernels), later runs 3 s, because the compiled code is
  cached in `~/.cupy/kernel_cache`. 3.4 can only quote it.

## Repository

- **Videos and GitLab's 5 MiB per-file limit.** The pipeline re-encodes to
  stay under it (render.sh warns above 4.5 MiB); v0 was re-encoded and the
  unpushed history rewritten on 16 Nov 2026. If videos outgrow that (longer
  or higher resolution), move `media/videos/*.mp4` to Git LFS, which needs
  `git-lfs` installed wherever the repo is cloned.

## Upstream (cuPhoton)

- **xRay: the detector command is slower than a NumPy loop here** (found
  building 7.3). `detector-artifacts` took 13–17 s for 2,048 row fits
  (256 × 128 detector, 97 frames) and 102 s for 16,384 (512 × 512) on an
  RTX 4070 Ti SUPER, about 6 ms per row; `linear_prediction_numpy` takes
  about 1 ms per 95-sample trace on the CPU. The guide makes no speed
  claim, and the course makes none. Worth profiling (HDF5 read? per-tile
  Python?) and reporting.
- **xRay: excluded rows still feed their neighbours.** With `--exclude-y`
  the dead rows are skipped, but rows within `--integrate` of them still sum
  their zeros (amplitudes 55–87% of typical in 7.3). Without it, dead rows
  come back status 1 with their neighbours' frequency. Neither is in the
  guide.
- **xImage: photometry on the scene depends on when it stopped.** On the
  M101 nights (8.3), fakes measured 1.15× planted at the default stop, 1.08×
  at 300 steps; with a constant pedestal added to the sky-subtracted frames,
  1.06× and 0.85×. The guide says the run returns no variance or effective
  PSF; a note on calibrating fluxes (and on sky-subtracted inputs to a
  nonnegative scene) would help.

- **xBeam: the radio job's delay sign isn't documented** (found building
  7.2). A station's `delay_coefficients_s` is how much earlier it hears the
  wavefront than the reference (DiFX's convention, measured with a known
  delay); the guide and data contract don't say, and the time-series path
  uses the opposite-feeling "positive lag = second signal later". A sign
  error doubles the residual delay without any warning.
- **xBeam: a radio job's `source_files` resolve against the working
  directory**, not the job file's folder (`correlate-series` JSON paths are
  relative to the JSON file, guide). Running from elsewhere fails with
  FileNotFoundError.
- **xBeam sample data.** The 13 Nov blog says a sample recording and job are
  in the repository; neither the pinned commit nor `main` (db23dd9, 17 Nov)
  has one. 7.2 makes its own (`make_recordings.py`).

- **`examples/run_quickstarts.py` prints a stale summary on failure.** When the
  output directory exists, it exits 1 with the error on stderr, but prints the
  *earlier* run's summary.json (`"status": "ok"`) on stdout. An agent reading
  stdout reports success. `docs/quickstarts.md` says "the same summary is
  printed to standard output", which reads as the current run's. Found
  16 Nov 2026 on ff4d260; used as a teaching point in 2.2. Not reported yet.

## Plan milestones not started

- Rerun the M0 simulated learners against the app (not the old CLI course).
- M5: packaging for compute centres (container or lockfiles, offline mode).
- Model comparison (Gemini 4 Argon, GPT 6.1 Sol, Nemotron 3.5 Super VL) on
  the same sims, once the setup is stable.
