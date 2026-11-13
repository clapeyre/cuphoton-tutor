# v4 — Where your data lives: host and device

Draft script, not yet narrated or rendered. Target about 1:45. Plays at 03 start.
No checkpoint or exercise content. Schematic animation throughout (two boxes and a
bridge), so no data script is needed except one timing card. If a timing card is
wanted, take its numbers from overnight/reports/gpu.md (real GPU runs), never from
memory; otherwise omit numbers and say "slow" and "fast".

Facts checked against docs/guide/concepts.qmd (pinned checkout): NumPy results
live in host memory even when a GPU backend ran (example: `fit_dipoles(...,
backend="cupy")`). `*_device` functions keep CuPy results on the GPU:
`reproject_array_device` (xRep), `solve_constant_kernel_device` (xPois),
`fit_dipoles_device` (xFit); the xPois and xFit device versions copy NumPy inputs
up for you, CuPy inputs must already be on the active GPU. xFit's fit_single_sources returns CuPy for CuPy input (follow-the-input); fit_dipoles returns NumPy. The FITS reader returns
CuPy with `device=True`. The final cut names these three functions on the s3 cards.

## s1 — Two memories (≈20 s)
**Visual:** two boxes, "CPU memory" (host) and "GPU memory" (device), with a narrow
bridge labeled "copy". A small image tile sits in the CPU box.
**Narration:** Your computer has two kinds of memory. The processor has one, the
GPU has another, and a narrow bridge joins them. Anything the GPU works on has to
cross that bridge first, and the result has to cross back before you can use it
anywhere else.

## s2 — The expensive way (≈25 s)
**Visual:** an image tile crossing to the GPU, a stage runs, tile crosses back, next
stage, crosses again; the bridge glows red each time and a cost bar grows.
Then the cheap way: it crosses once, three stages run on the GPU, it crosses back
once; the bar stays short.
**Narration:** The bridge is slow compared with the GPU itself. If every stage sends
the image back to the CPU and then up again, you spend most of the time on the
bridge. If the image crosses once, stays on the GPU through all the stages, and
comes back at the end, the GPU can do what it's good at.

## s3 — Three cases (≈40 s)
**Visual:** three cards. Card A: "host-result APIs": arrow from GPU box back to CPU
box, result is a NumPy array. Card B: "*_device functions": the result stays in
the GPU box. Card C: "follows its input": a CPU tile in gives a CPU tile out, a GPU
tile in gives a GPU tile out.
**Narration:** In cuPhoton you meet three cases. Some calls hand you a NumPy array:
the work may have happened on the GPU, but the result comes home. Functions with
device in their name keep the result on the GPU, ready for the next stage. And some
calls follow their input: give them host memory and you get host memory, give them
device memory and you get device memory.

## s4 — Why it matters to you (≈20 s)
**Visual:** a pipeline of five stages with bridge icons between; the agent's code
appears as a faint overlay; one stage is highlighted where a copy occurs.
**Narration:** You won't write the transfers yourself. But a working pipeline can
still be a slow one, and the cause is often a copy nobody meant to make. The code
runs and the picture is right; only the clock tells you.

## s5 — Ask (≈10 s)
**Visual:** prompt card: "Where does each result live?"
**Narration:** Ask your agent where each result lives.
