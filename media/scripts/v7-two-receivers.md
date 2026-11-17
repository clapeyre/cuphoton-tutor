# v7 — Two receivers, one signal

Opens Module 06 (top of 6.1). The picture the module needs before any code:
one wave reaching two receivers at different times, what a radio telescope
records, and how sliding one recording past the other finds the delay.
Written after walkthrough 8 ("I'm clinging on for dear life"). Gives away no
checkpoint: it never states a sign convention (6.1), never shows a delay
beyond the window or a wrapped lag (6.1 `hidden`), never shows a wrong delay
model or a phase slope (6.2), and never mentions whitening or a background
(6.3). Data: media/scenes/data_v7.py: two synthetic recordings sharing a
faint signal 23 samples apart, correlated with xBeam (NumPy backend).

Subtitle: "x beam" -> "xBeam"

## s1 — One wave, two receivers
**Visual:** a source far away at the top; two radio dishes on the ground, apart.
Straight wavefronts travel down at a slant; one touches the left dish, then,
later, the right one. The extra distance the wave travels to the second dish is
highlighted and labelled "delay".
**Narration:** Far away, a source sends out waves: radio waves, from a galaxy
or a black hole. Two radio telescopes on the ground both receive them. But the
source isn't straight overhead, so each wavefront reaches one dish first, and
the other a moment later. That moment is the delay. It depends on where the
source is in the sky, and it changes slowly as the Earth turns.

## s2 — What a dish records
**Visual:** under each dish, a recording scrolls in: a jagged trace of numbers.
A faint shared pattern is drawn in colour inside each, then the colour fades:
by eye, the two traces look unrelated.
**Narration:** A radio telescope doesn't take a picture. It records the voltage
from its receiver, millions of times a second. Most of that voltage is the
receiver's own noise. The source is a faint pattern hidden in both recordings,
the same pattern in each, shifted by the delay. By eye, you can't see it.

## s3 — Slide, multiply, add
**Visual:** recording A fixed; recording B above it, sliding sideways step by
step. At each shift the sample-by-sample products flash, their sum moves a dot,
and the dots trace a curve against the shift. The curve is flat and noisy, then
jumps where the shared pattern lines up, and falls back.
**Narration:** To find it, slide one recording past the other. At each shift,
multiply them sample by sample, and add up the products. Mostly, the products
are as often negative as positive, and the sum stays small. When the hidden
patterns line up, the products turn mostly positive, and the sum jumps. That
curve is the cross-correlation. Its peak sits at the delay. x beam computes it
this way, through Fourier transforms, on the GPU.

## s4 — Why line them up
**Visual:** the Earth with dishes on several continents; lines join pairs of
them; a label "baseline". Then an image of a ring, labelled "detail as fine as
one dish this wide".
**Narration:** Radio astronomers correlate recordings from dishes thousands of
kilometres apart. Lined up by their delays, each pair of dishes, a baseline,
sees detail as fine as a single dish as wide as the distance between them.
That's how the Event Horizon Telescope made its images of black holes.

## s5 — This module
**Visual:** three cards appear in turn: "A known delay", "Three radio
stations", "Two gravitational-wave detectors". Then one line: "every run gives
a number: when do you believe it?"
**Narration:** The same idea works for any two receivers that hear one source:
two microphones, or the two detectors that heard the first gravitational wave.
In this module, you'll find a delay you know, correlate three radio stations,
and measure that wave's delay yourself. Each time, the correlation hands you a
number. The question is when to believe it.
