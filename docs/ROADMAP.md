# Roadmap

Work that must happen, in order, before the course is shown to anyone
outside the team (decided 17 Nov 2026). Parked ideas stay in `BACKLOG.md`.

## Coverage of the user guide

The guide (https://nvidia.github.io/cuPhoton/main/, `docs/guide/` at the
pinned commit) has 15 chapters. Where the course stands:

| Guide chapter | Course | Depth |
|---|---|---|
| 1–3 Install, first difference, concepts | 00, 01 (the guide's own sample pair) | taught |
| 4 Read FITS images | 3.3 | taught: a real GPU read, the default reader, the compression fallback |
| 5 Align, and stack | 1.3, 3.2, 3.4; stacking 4.5 | taught |
| 6 Subtract | 1.4, 4.2, 4.4 | taught |
| 7 Measure | 1.6, 5.2 | taught |
| 8 Classify (xScan) | 4.6 | taught: train, evaluate, score, test unseen bogus |
| 9 Transient chain | Module 05 | taught |
| 10 Uncertainty | 4.4, 5.3 | taught |
| 11 Reconstruct (xImage) | Module 06 (track) | taught: a known scene, faults validation misses, the M101 nights |
| 12 X-ray traces (xRay) | Module 08 (track) | taught: one trace, a lost mode and uneven steps, the detector on the GPU |
| 13 Correlate (xBeam) | Module 07 (track) | taught: time series, radio jobs, real data (GW150914) |
| 14 Scale out | 9.1 map | out of scope by decision (below) |
| 15 Monitor (xLens) | 5.4 | taught |

## 1. Module 04 changes (built and walked 17 Nov)

3.3 made honest (xDR built by `tools/setup-gpu-env.sh`; the compression
trap), 4.5 (a deeper reference: stacking), 4.6 (teach a classifier: xScan;
the module exit moved here from 4.4). Notes go in `docs/walkthrough-7.md`.

## 2. Component tracks (built 17 Nov; walked 17–18 Nov)

After the image modules (walkthroughs 8 and 9): Module 06 xImage
"Combining many images" (it ends on the M101 nights of Module 04, so it
follows the image modules), Module 07 xBeam "Correlating two receivers"
(walked 17 Nov: "good"), Module 08 xRay "Time-resolved X-ray traces"
(walked 18 Nov; 8.3 reworked), each with a video. Each follows the
course's pattern: a known answer first, the receipt, the component's
silent-error trap found by testing, then real or realistic data. Module
titles say what the module is about (walkthrough 9).

## 3. Walk what's left

- 9.1, the course's last module: the full map and a conversation about the
  learner's own work.
- A second look at 8.3 after its rework (the tiles figure, the turns on the
  dispersion curve), and at 8.1's maths.

## 4. Tutor observability (admin page built 18 Nov)

The tutor's context fills up: in the first five days of the author's own
run it reached pi's compaction threshold (184k of a 200k window) twice
(16 Nov, 18 Nov), about every day and a half. The progress survives,
because it lives on the page, but the tutor loses the detail of how the
learner answered earlier, which is what it adapts to.

Built: `/admin` (the "Admin" link in the course header). It shows the
context at every model call with the compactions marked, how long the
learner waits for a first response and for the whole turn, errors and
retries (the 429s pi retried silently), per-lesson and per-tool figures,
spend and cache share, margin threads, GPU memory and disk, and a "Ping
the model" button. It reads pi's session log; what the log doesn't keep
(retries as they happen, compactions, margin calls, pings) goes to
`learner/metrics.jsonl`.

**One tutor thread per module (built 18 Nov).** Opening a lesson of a later
module starts a new main thread (`learner/thread.json` says which module the
current one belongs to). First the old thread rewrites `learner/profile.md`
(`tutor/SYSTEM.md`, "The learner profile": their work, how they learn, wrong
turns, terms they own / not anchored / explained off-list, open threads).
The new thread starts from that profile, the learner's progress, and the
course terms introduced so far, computed from `vocabulary.yaml`'s
`introduce_at` rather than remembered. Earlier conversations stay readable
in `page.json`. Going back to an earlier module stays in the current thread,
with a pointer to that lesson's conversations. Pi's compaction stays on as
a safety net. Tested on a copy of the author's run: the switch to 9.1 took
the context from 134k to 22k. A module that outgrows the window should be
split, not compacted (author, 18 Nov).

Still to do:
- Watch the first real switch (the author's 9.1) on the admin page: the
  profile, and whether the new thread re-anchors the terms it lists as
  not anchored.

## 5. Public launch: a Brev launchable

Public repo prepared: `git@github.com:clapeyre/cuphoton-tutor.git` (not
pushed yet). cuPhoton itself is public (`github.com/NVIDIA/cuPhoton`) and
Module 04 downloads its PS1 data from the public archive, so nothing
internal is needed besides the model endpoint. Licensing goes through the
SA process, not here. To do, most important first:

1. **First-run setup page for the model.** `tutor/pi-agent/models.json`
   points at `inference-api.nvidia.com`, which is NVIDIA-internal. On
   first open the page asks for the provider (build.nvidia.com, any
   OpenAI-compatible URL such as a local vLLM or NIM, or Anthropic), the
   key and the model, runs the endpoint ping (`server/endpoint.ts`), and
   saves to `learner/`, never to the repo. It warns that the course was
   tuned on Sonnet 5.5 (weaker models mostly fail at the page tools: ask,
   settle, reveal) and that a local model shares the GPU the lessons use.
2. **Access control.** The tutor runs shell commands and the page has no
   login; today it is bound to 127.0.0.1 behind an SSH tunnel. A public
   link would be a shell on the instance. Use Brev's access-controlled
   links (check what they offer) or a token the setup step generates; the
   admin page sits behind the same gate.
3. **Packaging.** The GPU environment is 11 GB, plus the CPU `.venv` and
   the native xDR build: a setup script from scratch is probably 15–30
   minutes per launch (not timed). Prefer a prebuilt container image.
   Either way: a neutral `CUPHOTON_DIR` default (today it's the author's
   path), clone cuPhoton at the pinned commit, `npm ci && npm run build`,
   then `npm run smoke` as the "ready" check.
4. **Pick and test the GPU.** The course has only ever run on one machine
   (RTX 4070 Ti SUPER, 16 GB). Run every module once on a fresh instance
   of the smallest GPU that should pass (4.6 trains with PyTorch; 6.3,
   8.3 use the GPU) and write the result in the README.

One instance per learner fits the app: progress is one `learner/` folder.

## Decided out of scope

- **Scale-out (guide ch. 14).** Not taught (17 Nov). By the time a learner
  deploys to many GPUs they know the library well enough to work from the
  documentation with their agent, on their own cluster. 9.1's map points to
  the chapter; 3.4's timing habits carry over.
