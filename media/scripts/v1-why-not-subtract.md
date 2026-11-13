# v1 — Why you can't just subtract two pictures of the sky

Measured with Kokoro (af_heart): 1:33, not 2:15 (the ~235 words run ~150 wpm
with 0.6 s pads). Each segment = one narration clip + one scene beat. All
visuals are the course's synthetic pair and real cuPhoton CPU outputs (xRep,
xPois); nothing is a toy. Data: media/scenes/data_v1.py.

## s1 — The question (≈15 s)
**Visual:** reference image; slow crossfade to target. A soft circle appears
around the new source as the voice names it, then around the brightened star.
The list says what you see, not what caused it (same rule as v0 s2).
**Narration:** Every few nights, survey telescopes photograph the same patches
of sky. Almost nothing in those pictures changes. What we're after is the little
that does: here, a new point of light where there was none, and a star that got
brighter.

## s2 — Just subtract? (≈20 s)
**Visual (real pair, no alignment at all):** the target minus the middle 256x256 of the reference (the pair differs by ~4 px shift, 3° rotation, 0.26 vs 0.27 arcsec/px, 300 vs 256 px).
Every star becomes a bright lobe beside a dark one. Zoom on one pair.
**Narration:** So why not subtract last night's picture from tonight's? Here's
what that gives you. Every star leaves a bright half and a dark half. The
telescope pointed a few pixels differently, and turned a little, so nothing
lines up.

## s3 — Fix the geometry (≈25 s)
**Visual:** the reference's pixel grid drawn as a mesh, warping onto the target's
grid. Label "xRep". Then the real aligned reference beside the target, same shape.
Subtract: rings around every star.
**Narration:** First, fix the geometry. The file headers say where every pixel
points on the sky, so we can resample one image onto the other's grid. In
cuPhoton, that's xRep. Now subtract again. Better, but every star still leaves a
ring.

## s4 — The blur (≈30 s)
**Visual:** take one unchanged bright star (real 1D slice through the aligned reference and the target, each normalized to unit flux; the reference is the sharper one, PSF sigma 1.2 px vs 1.8 px); plot its profile on both nights as 1D curves, one
narrow, one wide. Their difference: a dip in the middle, a rise either side.
(Real fitted kernel: effective width 1.39 px, quadrature estimate 1.38 px:
reference sigma 1.2 px × 0.26/0.27 in target pixels.)
Then the narrow curve widens (convolution animation) until it matches the wide
one, and the difference flattens to zero.
**Narration:** The rings come from the air. On one night it blurred starlight
more than on the other. Subtract a narrow bump from a wide one and you get this
shape. To cancel it, blur the sharper image until it matches the other. xPois
fits that blur, called a kernel, together with the brightness scale and the sky
level.

## s5 — What's left (≈20 s)
**Visual:** the real standardized difference image from xPois: flat noise, a dark
frame at the edge, two spots. Circles appear on the two spots, labeled "brighter"
and "new".
**Narration:** Now the unchanged stars cancel into noise, and two things stand
out: a star that got three times brighter, and a source that wasn't there at all.
The empty frame around the edge is where the blur can't be matched: there's no
data beyond the border.

## s6 — The chain (≈20 s)
**Visual:** five boxes drawn left to right: Align (xRep) → Match & subtract (xPois)
→ Find (xPois) → Measure (xFit) → Decide (xScan). A small agent icon under the
first box; a person icon above, with a magnifying glass.
**Narration:** Align. Match and subtract. Find. Measure. Decide. That's the core of the
pipeline you'll direct in this course. Your agent will do the typing. Your job is
to know what each picture should look like, and to notice when it doesn't.
