# 2.2 · tutor notes

**Goal:** the learner predicts and sees the runner refuse to reuse an output
directory, and says the right instruction (new directory; never delete results
unchecked). Probes M-OUTDIR and M-AGENT-SUCCESS.

## Your turn `predict-rerun` (prediction)
- Accept any prediction. When they ask, rerun the identical 2.1 command
  (same `--output-dir work/02/qs-cpu`), capturing stdout, stderr and the exit
  status separately, e.g. `> rerun.out 2> rerun.err; echo $?`.
- Facts (real run, pinned commit): exit status **1**; stderr is one line,
  `quickstart failed: FileExistsError: output directory already exists; remove it first: <path>`;
  **stdout prints the earlier run's summary.json in full, ending in
  `"status": "ok"`** (`run_quickstarts.py` `main()` prints any existing
  summary.json on failure). Nothing in the directory changed.
- Show them all three: in your reply, put the exit status and stderr line in a
  code block, and say that stdout printed a summary; let them ask to see it.
  Ask what an agent that only read stdout would have reported.
- Settle on the comparison with their prediction.

## Your turn `what-do-you-say` (checkpoint)
- **Pass:** choose a new output directory (name or root); don't delete the old
  one without checking it holds only generated artifacts that aren't needed.
  Ground in docs/quickstarts.md ("Output contract") and docs/troubleshooting.md
  ("A run directory already exists").
- If they say "delete it", ask what was in it and whether anything else might
  need it.
- If they bring up the stale "status ok" on stdout, good: it's real cuPhoton
  behaviour, known to the course authors, so there's no need to file it.
- Settle, then `reveal("2.2")`.
