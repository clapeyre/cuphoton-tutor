# v5 — Why the sum wobbles

Placed at the start of 5.3 (after 4.4 has settled, so it gives away no
checkpoint: 4.4's `what-it-proves` asks for the reason). Data:
media/scenes/data_v5.py — xRep (CPU) shifting pure noise by half a pixel, and the
PS1 target's blank-sky correlation and box sums (Module 04 data). Answers the
walkthrough-5 note "I couldn't explain it back".

Subtitle: "four point four" -> "4.4"

## s1 — The puzzle
**Visual:** two cards. Left: "one pixel: scatter / map = 0.9 to 1.07, the map is
right". Right: "a flux: error bars 1.2 to 1.5 times too small". A question mark
between them.
**Narration:** In lesson four point four, the fake stars told you the error bars
were too small. Yet one pixel at a time, the survey's variance map was right.
How can every pixel be right, and their sum be wrong?

## s2 — Adding up independent noise
**Visual:** a three by three grid of pixels whose noise values flicker through
several draws; beside it, the sum of the nine, and a running tally of how far it
strays. Label: each pixel plus or minus 1, the sum plus or minus 3, the square
root of 9.
**Narration:** Start with nine pixels, each with noise of one unit, independent
of each other. A flux measurement adds them up. Their wobbles partly cancel, so
the sum wobbles by three units: the square root of nine, not nine. That's the
rule an error bar uses. Add the variances, then take the square root.

## s3 — What resampling does
**Visual:** a patch of pure noise, then the same patch after xRep shifts it by
half a pixel: visibly smoother. Then one input pixel lights up, and the four
output pixels it feeds light up with their weights, 0.37 each. Then two
neighbouring output pixels are outlined: they share two input pixels.
**Narration:** Now resample, the way a survey puts every exposure onto its sky
grid. Here xRep shifts pure noise by half a pixel. Each output pixel is a
weighted blend of a few input pixels. So one input pixel's noise lands in
several output pixels, and two neighbours share part of the same noise.

## s4 — Shared noise doesn't cancel
**Visual:** two three by three grids side by side, independent and resampled,
flickering through draws. Under each: per-pixel scatter, 1.00 for both. Then the
sums: 1.00 times the prediction for the independent grid, 1.22 for the
resampled one.
**Narration:** xRep carries the variance along, and pixel by pixel it is exactly
right. But when you add up neighbours, the shared parts don't cancel. They move
together. So the sum wobbles more than the variances add up to: here,
twenty-two percent more, with nothing wrong in any single pixel.

## s5 — On the survey's images
**Visual:** the PS1 target's neighbour correlations (0.17 across, 0.22 up and
down) in a three by three grid; then real scatter of a box sum over predicted,
against box size: 0.9 at one pixel rising to 1.7 at eleven, with the line at 1.
**Narration:** The survey's images show the same thing. Each pixel shares about
a fifth of its noise with the next one, and the bigger the patch you add up, the
further the map falls short. A map with one number per pixel can't record how
pixels move together. So you measure the factor on the image itself, and widen
the error bars by it.
