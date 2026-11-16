# Backlog

Parked requests, ideas and concerns: things we agreed matter but aren't doing
now. Newest at the top of each section. When an item is done, delete it here
and mention it in the commit. Walkthrough notes stay in `docs/walkthrough-*.md`;
anything parked from them is copied here with a pointer back.

## Course content

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
- **Videos v3 (kernel) and v4 (host/device memory)** have scripts but no
  scenes; v4 belongs in Module 03.

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
planned in `docs/EXPANSION-PLAN.md`. These are the larger pieces, parked:

- **Component tracks for non-optical labs.** xRay (X-ray detector traces,
  guide ch. 12), xBeam (signal correlation and the VLBI correlator, ch. 13 and
  the 13 Nov blog post), xImage (multi-frame reconstruction, ch. 11). Each
  would be a short optional module: one synthetic run, its receipt, its one
  silent-error trap, then "your data". Until then the map lesson (plan item 1)
  is the only mention.
- **Scale-out.** MPI and Dragon executors, Slurm/SSH launches, the persistent
  `DeviceWorkerContext` pipeline (guide ch. 14, `docs/distributed-execution.md`).
  It's the headline of both blog posts and what HPC centres will ask about
  first. Needs a multi-GPU node to teach honestly; the 3.4 timing lessons
  carry over (per-stage vs end-to-end, synchronize, warm-up rounds).
- **Inputs beyond FITS.** HDF5 via Legate (`hdf5` extra, not on Python 3.14),
  VDIF for xBeam. Nothing in the course shows them, so non-FITS labs may assume
  cuPhoton is FITS-only. Could ride on the component tracks.
- **Re-check coverage at every re-pin.** The guide grew from 4 to 15 chapters
  between our pin and 0.3.0.dev; diff its "Find your task" table against the
  course whenever `course.yaml`'s commit moves.

## App

- **Prepare-ahead looks one lesson ahead only.** Jumping ahead still waits.
- **"Ask about" for prose:** selecting text to ask was removed (walkthrough 2,
  1.7: it stole the cursor). A deliberate affordance on paragraphs could come
  back later.
- **Tutor latency:** about 2 s before the first word, even though thinking is
  already off (`TUTOR_THINKING=off`): it's the endpoint's time to first token on
  a long, mostly cached context. Worth measuring per model in the comparison.
- **Building xDR** (cuPhoton's GPU FITS decoder) isn't part of the GPU
  environment; 3.3 teaches the fallback instead. A later lesson could build it.
  The coverage review rates this "likely missed": the blog's first next step
  is building xDR, and GDS/nvCOMP is where the 14,900x I/O figure comes from.
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
