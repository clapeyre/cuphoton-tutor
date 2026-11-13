# v2 — It ran. Is it right?

Measured 1:21 with Kokoro (was 2:00 target; with the added s4 sentence). Must not
hint at exercise 1.7 (axis order). Uses a backend fallback and a failed blur match
as its two examples. Data: media/scenes/data_v1.py, data_v2.py, and the real
`examples/run_quickstarts.py --profile auto` summary.json on a CPU host.

## s1 — The green checkmark (≈15 s)
**Visual:** terminal; a run finishes, "done" in green. A big checkmark appears,
then a question mark replaces it.
**Narration:** Your agent ran the pipeline. No errors, a tidy summary, a green
light. It's tempting to stop there. But "it ran" and "it's right" are different
claims, and the gap between them is where most mistakes hide.

## s2 — Where did it run? (≈30 s)
**Visual:** the request "run this on the GPU". Then the real `summary.json` from a
`--profile auto` quickstart on a CPU host; highlight `hardware.gpu_available: false` and each component's
`backend`/`device` (xrep/xpois cpu, xscan torch on cpu; the quickstart requests numpy for xFit). xfit and xpois also record requested_backend. Side note: "auto → tries GPU, falls back".
**Narration:** First question: where did it actually run? cuPhoton's default
backend, auto, tries the GPU and quietly falls back to the CPU if it can't use
it. The run still succeeds. The only trace is in the record it leaves behind, the
receipt. So ask your agent for it, every time.

## s3 — Does the picture look right? (≈30 s)
**Visual:** two difference images side by side: one clean (flat noise, two spots),
one where the kernel was too narrow (rings at every star). Both runs printed
"done".
**Narration:** Second question: does the output look like what it should? Both of
these runs finished without complaint. Only one of them matched the blur. You
can't tell from a log line. You can tell in half a second from the picture, if
you know what the picture should look like.

## s4 — Did the numbers converge? (≈20 s)
**Visual:** the real xFit table for the two candidates from a solver stopped after
3 evaluations: flux still 12234 and 4140 DN, but `converged` False,
`uncertainty_valid` False and the error bar `nan` (both rows, not one).
**Narration:** Third question: did the measurements actually converge? Fits
report whether they did, and whether their error bars can be trusted. A number
without that flag is just a number. But the flag is a minimum, not a proof: a fit
can converge and still be wrong, so check the value against the picture too.

## s5 — The habit (≈20 s)
**Visual:** a three-line checklist card: Where did it run? Does it look right? Did
it converge? Then the card becomes a sentence typed into an agent prompt.
**Narration:** Three questions, after every run. Better still, make them part of
what you ask for in the first place: "run it, and show me where it ran, the
difference image, and the fit status." That's what directing an agent well looks
like.
