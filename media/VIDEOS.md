# Videos

Short explainers (1–3 min) that carry the L0 "picture" layer better than text.
The tutor offers them at the steps listed; they never replace a checkpoint.

Rules: one idea per video; real cuPhoton outputs on the synthetic pair wherever
possible, not schematic art; no video gives away a checkpoint or exercise
(in particular, nothing about axis order before exercise 1.7).

**Reveal on the word.** Each on-screen element appears as the voice starts
naming or describing it, not at the end of the sentence. A viewer who reads and
one who listens then get the same information in the same moment. Cue reveals
with `Timed.at("phrase")` (media/scenes/common.py), which uses the word
timestamps narrate.py writes to timings.json. Don't place them by estimated
seconds. Accumulate rather than replace when the narration lists items quickly.

| id | title | length | used at | layer | status |
| --- | --- | --- | --- | --- | --- |
| v0-what-changed | What changed in the sky? | 2:28 | start of module 00, before 0.1 | L0 + vocabulary | draft rendered |
| v1-why-not-subtract | Why you can't just subtract two pictures of the sky | 1:34 | after checkpoint 0.3; after checkpoint 1.4 | L0 | draft rendered, cued on the word |
| v2-it-ran | It ran. Is it right? | 1:21 | after 2.3 | L0/L1 | draft rendered, cued on the word |
| v3-kernel | What the matching kernel does | 2:00 | 01 step 1.4 (optional detour) | L2 | script (unrendered) |
| v4-where-data-lives | Where your data lives: host and device | 2:00 | after 3.1 | L0/L1 | script (unrendered) |
| v6-one-image-through-the-chain | One image through the shipped chain | 1:19 | start of 5.1 (opens Module 05) | L0/L1 | rendered, cued on the word; real chain run |
| v5-why-the-sum-wobbles | Why the sum wobbles | 1:31 | start of 5.3 (after 4.4) | L1 | rendered, cued on the word; xRep data |

## Outlines

**v0-what-changed.** Script: scripts/v0-what-changed.md. A camera in the garden,
the same patch of sky night after night. Why look: the few things that change.
What a picture is (pixel value, source, background, noise). What differs between
nights anyway (pointing, background, exposure time, seeing and PSF), stated as
premises. Reference vs target image. It ends on the module's question and on
"your agent types, you think". It replaces the old v0-intro outline. It never
shows a subtraction and never says which differences the course pair has
(checkpoints 0.2 and 0.3).

**v3-kernel.** 1D first: a narrow Gaussian convolved with a small Gaussian becomes
the wide one (widths add in quadrature). Then 2D with the basis: three Gaussians
of different widths, weights fitted, summing to the kernel xPois actually found
on the sample pair. End on the kernel sum ≈ 1 and what it means (flux scale).
Mention the target-sharper case in one line.

**v4-where-data-lives.** Two boxes, CPU memory and GPU memory, a slow bridge
between. Animate an image crossing once vs. every stage. Then the three cases in
cuPhoton: host-result APIs (NumPy back), `*_device` functions (stays on GPU),
calls that follow their input type. End: "Ask your agent where each result lives."

## Production

See `pipeline/README.md`. Narration is synthesized per segment first; each
segment's measured duration drives the animation timing, so picture and voice
stay in sync without manual editing.
