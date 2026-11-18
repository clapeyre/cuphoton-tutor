# v9 — Many frames, one scene

Opens Module 06 (top of 6.1). The picture the module needs: why stacking
keeps the blur, and how xImage works backwards from a guessed scene, blurred
by each frame's PSF and compared with that frame, step by step. Gives away
no checkpoint: it uses its own scene, not the guide's (6.1 asks for a
prediction of that one), shows no brightness numbers, never mentions the
evaluation's scores or the receipt's stop condition (6.1 `how-know`), never
shows a bad pixel, a wrong PSF or a robust loss (6.2), and never a
changing source (6.3). Data: media/scenes/data_v9.py: three frames of a
close pair and a third source, reconstructed by xImage (L2, CPU) after 1,
3, 10, 30 and 75 steps.

Subtitle: "x Image" -> "xImage"

## s1 — Many frames
**Visual:** three frames of the same small field appear side by side, each
blurred differently; under each, its PSF as a small blob of a different
width.
**Narration:** Take several pictures of the same scene, and each comes out a
little different. The blur changes from one to the next, from the air, the
focus, or a shaking mount, and so does the noise. Each frame has its own
blur, its point spread function.

## s2 — Stacking keeps the blur
**Visual:** the three frames slide together into one: their median. A close
pair of sources stays one blob. Label: "less noise, same blur".
**Narration:** Stacking them, taking the median pixel by pixel, beats down
the noise. But it keeps the blur. Two sources close together still look
like one.

## s3 — Working backwards
**Visual:** a loop: "scene guess" → blurred by frame 1's PSF → compared with
frame 1, the difference shown; the same for frames 2 and 3; an arrow back to
the scene, which updates. The scene panel steps through the real snapshots
(1, 3, 10, 30, 75 steps); beside it the loss falls.
**Narration:** x Image works backwards. It starts from a guess of the scene,
blurs the guess with each frame's own blur, and compares the result with
that frame. Where they disagree, it adjusts the scene, and tries again. Step
by step, the blurred scene matches every frame more closely, and the
mismatch, the loss, falls toward the noise.

## s4 — One scene
**Visual:** the median and the final scene side by side; the pair, one blob
in the median, two points in the scene. Then a small receipt card:
"device, steps, loss".
**Narration:** What comes back is one sharp scene that all the frames agree
on. The pair that the stack blurred together is two sources again. With it
comes a receipt: what ran, where, for how many steps, and how well it
matched.

## s5 — This module
**Visual:** three cards: "A known scene", "A star that wasn't there", "Four
nights of M101". Then one line: "a sharp picture: is it a true one?"
**Narration:** In this module, you'll reconstruct a scene you know, look for
what went wrong in two bundles that both look fine, and reconstruct the
nights of M101 from earlier in the course. A sharper picture is easy to
make. The question is whether it's true.
