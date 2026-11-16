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
- **Cold GPU start isn't reproducible here:** the first GPU quickstart took
  28 s (CuPy compiling kernels), later runs 3 s, because the compiled code is
  cached in `~/.cupy/kernel_cache`. 3.4 can only quote it.

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
