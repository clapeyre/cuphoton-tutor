# v8 — Pump and probe

Opens Module 08 (top of 8.1). The picture the module needs before any code:
why a crystal "rings", how two pulses (pump, then probe) film something too
fast for a camera, how laser-on and laser-off frames become a trace, and
what xRay fits to it. Gives away no checkpoint: it never states an amplitude
or mentions the reference shift (8.1 `predict-fit`), never names a model
order (8.1 `order`), never shows a missing mode, a residual or a delay step
(8.2), and never shows a dead row or a status code (8.3). Data:
media/scenes/data_v8.py: the guide's sample pair, reduced and fitted by
xRay (NumPy), and a 64-row detector fitted row by row.

Subtitle: "x Ray" -> "xRay"

## s1 — A crystal rings
**Visual:** a bell struck, sound arcs. Then a crystal as a grid of atoms; a
red flash; the atoms sway back and forth together, faster than the bell.
A label: "terahertz: trillions of times a second".
**Narration:** Strike a bell, and it rings at its own notes. Strike a crystal
with a very short laser pulse, and its atoms ring too, swaying together at
their own frequencies. But they do it trillions of times a second. No camera
is that fast.

## s2 — Pump, then probe
**Visual:** a timeline: a red pulse "pump" at zero, a blue pulse "probe" a
gap later, the gap labelled "delay". The probe's X-rays scatter off the
crystal onto a detector; one frame lights up. The delay grows step by step,
and a stack of frames builds up, one per delay.
**Narration:** A beamline uses two pulses. The laser pulse, the pump, starts
the ringing. An X-ray pulse, the probe, arrives a set delay later, and the
X-rays it scatters onto a detector record where the atoms are at that
instant. Then it repeats, with the delay a little longer each time: one
detector frame per delay.

## s3 — Laser on, laser off
**Visual:** two stacks, "laser on" and "laser off". A region of the detector
highlighted; its brightness per delay plotted for both, the laser-off one
flat. Then the comparison, delay by delay, drawn as dots: a trace that rings
and dies away.
**Narration:** Frames taken without the laser show the crystal at rest. The
beam's own brightness wobbles from pulse to pulse, so each frame is divided
by a monitor of it first. Then compare laser on with laser off, delay by
delay, and what's left is what the laser changed: a trace that rings, and
dies away.

## s4 — What x Ray fits
**Visual:** the trace's dots; two damped cosines drawn below it, each in its
own colour, labelled with its frequency in THz; their sum drawn over the
dots. Then three words appear beside each mode: frequency, decay, strength.
**Narration:** x Ray fits the trace as a sum of damped oscillations, called
modes. Each mode has a frequency, a rate at which it dies away, and a
strength. Here there are two, and together they follow the trace.

## s5 — Every row, and this module
**Visual:** a detector; its rows light up one after another, and beside it
the fitted frequency for each row builds a curve. Then three cards: "One
trace", "A mode goes missing", "Every row on the GPU". Then one line: "a fit
always returns modes: are they all there?"
**Narration:** Each row of the detector sees the crystal from a slightly
different angle, and rings at its own frequency. On a GPU, x Ray fits every
row. In this module, you'll fit one trace whose answer you know, find out
how a mode can go missing, and fit a whole detector. A fit always returns
modes. The question is whether they're all there.
