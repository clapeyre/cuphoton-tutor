# Expansion plan: what the course leaves out of cuPhoton

Written 16 Nov 2026 from a coverage review: the course (Modules 00–04) against
the public cuPhoton docs, the user guide and the two NVIDIA blog posts (sources
at the end). The question asked: a research lab goes through this course, then
decides how cuPhoton could serve its own work. What would it miss?

This file holds the **low-hanging fruit**: additions that build on what is
already written and fit the course's thread. Larger additions (other
components, multi-GPU) are parked in `BACKLOG.md` under "Coverage".

## Where the course stands

The course goes deeper than the docs on the optical chain (xRep, xPois, xFit),
on trusting a run (receipts, `auto` vs named, host vs device, honest timing)
and, since Module 04, on real data (noise model, masks, real/bogus by eye,
injection tests). The verification habits and the misconceptions are its edge;
the docs don't teach them.

What it leaves out, by how likely a lab is to miss it:

| Capability | In the course | Who needs it | Miss it? |
|---|---|---|---|
| Shipped end-to-end chain (`examples/transient-chain`: survey adapters, config, Parquet catalog, local/Dragon/MPI executors) | absent | any survey or time-domain group | very likely; it is the documented "run it on my images" path |
| Error budget of the catalog (`corr`, `kfit`, `kmatch`, `mis`, `uq_valid`) | 4.4 finds the correlated-noise factor by hand; the budget itself is absent | anyone quoting fluxes or positions | likely |
| xScan in practice (training, `review-queue`, `review-bokeh`, xFit fusion) | named; 4.3 sorts by eye | survey and alert groups | likely |
| Scale-out (MPI, Dragon, `DeviceWorkerContext` persistent pipeline) | absent | HPC centres, LSST-scale work | very likely; headline of both blog posts |
| xDR at full strength (native build, GDS, nvCOMP) | 3.3 teaches the fallback | I/O-bound groups | likely |
| Inputs beyond FITS (HDF5 through xImage/xRay/xBeam, VDIF through xBeam; the xDR Legate HDF5 loader was removed) | absent | X-ray, radio, simulation labs | very likely |
| xRay (X-ray detector traces) | "a module we won't use" (2.1) | synchrotron, XFEL | near-certain |
| xBeam (signal correlation, VLBI correlator) | absent | radio, signal processing | near-certain |
| xImage (multi-frame reconstruction, PSF calibration) | absent | imaging groups | near-certain |
| xLens (run monitoring, dashboards, optional LLM questions) | absent | anyone running long batches | near-certain |

Two structural causes:

- ~~**Version drift.**~~ *Corrected 16 Nov:* our pin `ff4d260` already has
  every component, `examples/transient-chain` with the error budget, xLens and
  the whole 15-chapter guide (`docs/guide/*.qmd`). `c04d1a5` is only 7 commits
  later (gzip selection, xLens NOOA investigations, wheel licensing, guide
  publishing). The gap is in the course, not the pin.
- **Framing.** Module 00's intro says the course teaches cuPhoton "in
  particular for one job". Correct, but a materials or X-ray lab stops reading
  there. NVIDIA's own positioning is broader ("make multidimensional data AI
  ready", optical, X-ray and radio).

## The plan, in order

### 0. Re-pin cuPhoton (no longer a prerequisite)

*16 Nov: everything below exists at `ff4d260`, and the chain runs on it (see
item 2). Re-pinning to `c04d1a5` gains 7 small commits; do it with the next
full rerun of the modules, not before. Note the release tags (`v0.2.0`,
`v0.2.1`) sit on a release branch, not on main: decide then whether the course
pins main or the release a lab would install.*

Originally:

- Bump `course.yaml`'s commit, rebuild both environments, rerun every lesson's
  runs and update the tutor notes' "Facts (real run…)" blocks.
- Expect Module 02 to move most (see the backlog item "Module 02 is tied to
  today's CLI behaviour"); 2.2's stale-summary bug may be fixed upstream.
- Check the 2.3 bonus fact: the architecture doc now lists the xPois `auto`
  order as CuPy then CPU, while the October blog says CuPy, Numba-CUDA, CPU.

**Done when** Modules 01–04 run clean on the new pin and the notes match.

### 1. A map, and one sentence of framing *(done 16 Nov: Module 06, 6.1)*

*Built as a one-lesson **Module 06 "Where next"**, so it closes the course
after Module 05. Module 00's intro has the framing paragraph. The tutor notes
carry a brief per component (input, first command, needs, silent-error trap,
evidence), each cited to the guide; two facts the plan had wrong: xDR's Legate
HDF5 loader was removed (use h5py), and VDIF is read by xBeam only.*

Cheapest fix for the "near-certain" rows: a short closing lesson, **4.5 Where
next** (or a one-lesson Module 05 if 4.x should stay about the M101 pair).

- Prose: the guide's "Find your task" table, one line per module, in the
  course's voice. Name the inputs each takes (FITS, HDF5, VDIF, delay-indexed
  detector frames, sampled signals) so a non-optical lab sees itself.
- `:::your-turn your-data`: "What does your lab's data look like, and which of
  these would you start from? What would you check first?" The tutor maps the
  answer to a component and a guide chapter, and reuses the course's habits
  (receipts, noise model, injection test) on that component's terms.
- Module 00 intro: keep "one job", add one sentence that the same library
  covers X-ray traces, radio correlation, reconstruction and monitoring, and
  that the last lesson maps them.
- `tutor.md`: a short per-component brief (inputs, first command, the one
  silent-error trap of each) drawn from the guide, so the tutor can answer
  without reading the whole checkout mid-conversation.

No GPU runs needed; text and tutor notes only.

### 2. Module 05: the shipped chain on the M101 pair

Module 04 ran the chain by hand and found, by injection, that error bars were
1.2–1.5× too small because of correlated noise. The shipped chain has a term
for exactly that (`corr`). So Module 05 picks up where 4.4's closure leaves
off: "Now let cuPhoton's own pipeline do it, and see whether its error budget
agrees with your test."

Draft lessons:

- **5.1 From your instruction to a configuration.** Turn the 4.2 instruction
  into `config-generic.yaml` + `selections.json` for the PS1 pair:
  `variance_kind` (the PS1 `.wt` is a variance), `mask_policy` (PS1 bits:
  `strict` or `{bits: N}`, matching what 4.1 settled), `on_target_grid: true`
  (both nights are already on the sky grid). Your-turn: predict which
  settings matter for this data before reading the shipped defaults.
- **5.2 Read the catalog.** `catalog.parquet` and per-item `summary.json`:
  `candidate_id`, `sign`, `fit_model`, `quality_flags`, read receipts,
  `timings_sec`, `transfers`. Your-turn: does the chain find SN 2011fe and the
  same bogus spots as 4.2–4.3? Where does it disagree, and why?
- **5.3 The error budget.** `psf_flux_err` vs `psf_flux_err_fit` and the four
  terms; `uq_valid`. Your-turn: compare the chain's `corr` inflation with the
  factor the 4.4 injection test measured. Then rerun with `uq.enabled=false`
  and say what a reader of the catalog would lose. Misconception candidate:
  "`uq_valid` true means the error bars are right."
- **5.4 Scoring (optional).** `--checkpoint-dir` adds xScan scores. Only if a
  checkpoint whose `image_size` matches the stamps can be shipped or trained
  in reasonable time; otherwise show `review-queue` / `review-bokeh` on the
  4.3 cutouts and keep "the classifier automates your 4.3 questions" as the
  point.
- **5.5 Watch the run (xLens).** Turn each item's `summary.json` into an
  xLens `Sample` (measurements: candidates, timings, fallback reasons;
  findings: a fallback, a `uq_valid` rate below a threshold), export the
  dashboard. It is Module 02's idea, evidence about every run, at batch scale.
  Placed here rather than in Module 02 because it needs a multi-item run to
  mean anything. Needs no GPU.

Open questions, answered 16 Nov (facts and scripts in
`course/modules/05-the-shipped-chain/dev/`):

- **Does the chain run on the PS1 pair?** Yes, first try, 12 candidates, SN
  2011fe at (402, 400) with psf_flux 43,407 (4.4 by hand: 43,867). But two
  silent problems, which become the module's spine:
  - With `on_target_grid: true` the refine stage skips itself, so no PSF width
    is measured: `psf_flux` is NaN and every budget term is excluded ("no PSF
    width"), and the run says success. Fix: `xfit.psf_sigma_px`.
  - The default `auto_stamp_mask: true` fits the kernel on 5 stamps: chi2/dof
    ≈ 15 on this galaxy field, and injected fluxes come back 4–9% low. Only an
    injection test (or reading chi2/dof) shows it. With `false`: chi2/dof 1.55,
    fluxes unbiased.
- **xScan checkpoint?** None ships in the repo; training needs labelled survey
  data. 5.4 takes the fallback (review tools on the 4.3 cutouts), or drops.
- **Does `corr` apply?** Yes: measured factor used (`uq_corr_measured`), 2 of
  12 rows undefined. The measured variance factor (3.2–4.3) is about twice
  the closed form (1.5–1.7). With a sane kernel, the chain's total error bars
  give pull MADs of 0.8–1.3 on 300 fakes: honest in the core, with heavy
  tails still unexplained. That's 5.3's comparison with 4.4.

Revised 5.1: the configuration *and* its two traps (PSF width, kernel stamps),
found the course's way: read `summary.json` (`uq.excluded`, chi2/dof), then
inject.

New objective to add in `course.yaml`: "O6: Run a shipped pipeline on new
data, read its catalog and error budget, and check them against your own
test."

**Done when** 5.1–5.3 and 5.5 run on the GPU box, with tutor notes and run
facts, and one simulated learner gets through them.

## Sources

- cuPhoton README and docs on `main`: https://github.com/NVIDIA/cuPhoton
  (`docs/README.md`, `docs/architecture.md`, `docs/quickstarts.md`)
- User guide, 0.3.0.dev98 (`c04d1a5`): https://nvidia.github.io/cuPhoton/main/
  (chapters 9 "Run the transient chain" and 15 "Monitor runs" read in full)
- Blog, 7 Oct 2026: https://developer.nvidia.com/blog/faster-scientific-image-analysis-with-nvidia-cuphoton/
- Blog, 13 Nov 2026: https://developer.nvidia.com/blog/run-gpu-powered-black-hole-interferometry-with-nvidia-cuphoton/
- Product page: https://www.nvidia.com/en-us/high-performance-computing/ai-for-science/cuphoton/
