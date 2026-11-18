# Sim 2 · the whole course, Sonnet 5.5 (18 Nov)

One simulated learner (`sim/personas/t1-thorough.md`: careful, no time limit,
answers every box, says when the page looks broken) through all 41 lessons on a
fresh learner folder, Sonnet 5.5 tutoring. Run `runs/1118-1728-t1-thorough-sonnet-5-5-full`
(bugs.md there). Opus reviewed each module for bugs (`sim/bug_review.ts`); every
item below was checked by hand against the code, the course files or the logs.

**The app held up.** 203 steps in 74 minutes: 41/41 lessons, 72/72 boxes
settled, every closing shown, no stalls, no lost replies, median wait 13 s
(longest 140 s, 4.2's first real-data run). Peak context 109k; no compaction
(one thread per module). Tutor spend about $3.30.

## App bugs

1. **Run records describe the wrong run.** `recordFor` (server/recorder.ts)
   returns the bash call that wrote the PNG. When that call only plots another
   run's output, the figure is labelled with the plotting script: 3.1's GPU
   receipt figure says "CPU, 0.4 s"; 5.3's injection figures say CPU after a GPU
   chain; 3.2's table says 0.4 s. Its own comment says inputs are "folded in";
   they aren't. This is the module about trusting run records.
2. **Replies posted twice** after settle/reveal (1.1, 1.3, 1.5, and Sim 1).
3. **The tutor reads a figure before it exists.** It sends `read` in the same
   batch as the bash that writes the PNG; the read fails (ENOENT) and it then
   discusses a figure it never saw (0.2, 6.2, 8.2). pi runs built-in tools in
   parallel; `read` after `bash` should be sequential, or SYSTEM.md should say so.

## Course bugs, fixed in this commit

- 7.3: `gw_delay.py background raw` crashed without a figure path, which is how
  tutor.md runs it.
- 5.3: `inject_chain.py` didn't create `inj/`; the documented command failed
  on a fresh folder.
- 7.1–7.3 tutor.md named figures `8.x_…` (from before the renumbering).

## Course bugs, to decide

- **0.2 toy sky:** the spec changes σ but not the peak, so night-2 stars carry
  2.25× the light and "three times brighter" is 6.75× in flux. The tutor then
  said stars got "lower" while printing equal peaks. Make sources flux-normalised.
- **2.6 prompt** asks for "the backend you want"; the quickstart runner takes
  `--profile`/`--require-gpu`, not a backend.
- **Closings that state results the learner may not have seen:** 2.4 (an
  optional run), 4.4 ("about a third"; this run 40%), 4.5 (two of four configs
  run), 4.6 ("perfect"; this run had 1 false positive, and 2 missed fakes after
  retraining), 6.2 (the robust fix; the learner masked instead, which the notes
  allow), 7.2 (a GPU timing run only "if asked"), 2.5 ("cupy and cuda
  throughout"; xray says gpu, xscan torch). Either make those runs mandatory or
  word the closing for any outcome.
- **5.1:** tutor.md gives `selections.json`'s keys but not its top-level shape;
  the tutor's first file was rejected by `launch.py`.
- **5.2:** the supernova flux is quoted three ways (closing 43,900 ± 190,
  tutor.md 43,867 ± 186, tutor 43,852 ± 186).
- **6.1 closing** blames the 75-step cap for low peaks; its next sentence and
  tutor.md show they stay low after convergence.
- **5.4 tutor.md** lacks the fact that run2 has 3/12 NaN fluxes; the tutor
  called the NaN rule a bug and sent the learner hunting.
- **Held-back answers leaked** where the notes say not to (0.3 dipole causes,
  1.2 confirming the ×4 prediction, 1.5 `peak_yx` in a shown script, 1.7 the
  transposition as a "question"). Recurring enough for SYSTEM.md, not only the
  lessons.

## Harness notes

The reviewer's "aliased terms render wrong" finding was the harness's text
rendering, not the page (fixed). The learner twice answered a closing's
"Which raises" question into a box that doesn't exist; real learners might
try that too.
