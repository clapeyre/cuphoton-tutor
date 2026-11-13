# v0 — What changed in the sky?

Opens module 00, before step 0.1. The video has two parts, and the narration
says out loud when it moves from one to the other:
- **The problem, in general (s1–s5):** what astronomers look for, what a picture
  of the sky is, and why two pictures differ.
- **This module (s6):** where the learner starts, what they'll do, where they
  finish, and what's not included.

It states the physical premises the learner can't discover from pixels and
introduces the first target terms (course/vocabulary.yaml).

Must not give away:
- **Checkpoint 0.2:** it names what *can* differ between two nights, but never
  which of them happened in the course's pair.
- **Checkpoint 0.3:** no subtraction is shown, and it doesn't say how to remove
  each difference or in what order.

Target length about 2:15 at about 150 wpm. Line art for the garden and the
schematics. Sky images: s2 and s5 use one made-up star field; s3 zooms into
the course's reference image.

## s1 — A camera in the garden (≈20 s)
**Visual:** line-art garden at night, a camera on a tripod pointing up. A frame
is captured; the frame slides to the right and becomes a thumbnail labelled
"night 1". The camera captures again, "night 2", then "night 3".
**Narration:** Imagine you put a camera on a tripod in your garden and point it
at one patch of sky. Every clear night, you take a picture of that same patch.
After a week, you have a stack of pictures of the same stars.

## s2 — What we're looking for (≈25 s)
**Visual:** a flipbook of one star field. Every frame has the same stars in the
same places, with only tiny frame-to-frame jitter and noise. On one frame a new
point appears and gets a soft circle; on another, one star brightens and gets a
circle. Title on screen: "real changes in the sky".
**Narration:** Flip through them, and almost nothing changes. But now and then,
something in the sky really does change: a star gets brighter or fainter, a new
point of light appears where there was nothing, or something moves. A flare, an
exploding star, an asteroid. These real changes in the sky are what astronomers
are looking for. That's why survey telescopes photograph large parts of the sky
every few nights.

## s3 — What a picture is (≈25 s)
**Visual:** zoom from the reference image into one star until the pixel grid
appears, with numbers in the cells. Labels fade in one at a time, each with an
arrow: "pixel value (counts)" on a cell, "source" on the bump, "background" on
the flat area around it, "noise" on two neighbouring background cells with
different numbers.
**Narration:** To a computer, each picture is a grid of numbers. Each pixel value
counts the light that landed on that pixel during the exposure time. A star is a
source: a bump in those counts. Around it, every pixel still collects some light
from the sky itself: that's the background. Even two pixels of plain sky don't
read exactly the same number, because light arrives as random photons. That's
noise.

## s4 — Observing conditions (≈40 s)
**Visual:** title "observing conditions" at the top, subtitle "how each picture
was taken". Four small panels appear one by one, each a schematic, not the
course pair:
1. "pointing": a frame outline nudged and slightly turned;
2. "background": a sky gradient from dark to hazy, with a moon icon;
3. "exposure time": a stopwatch, 30 s vs 60 s;
4. "seeing": wavy air layers above the telescope, and one point of light drawn
   sharp, then spread wider.

Then a caption under panel 4: "PSF, point-spread function: the shape one point
of light takes in the image". Last, the s2 title "real changes in the sky"
returns on the left and "observing conditions" moves to the right, with a
vertical line between them.
**Narration:** But your pictures also differ for a second reason: they weren't
all taken the same way. In this course, we call that the observing conditions:
not just the sky and the air, but also where the camera points and how long it
collects light. The camera may point a little
differently. The moon or a thin haze can make the background brighter. You might
change the exposure time. And starlight crosses kilometres of moving air, which
spreads each star's light over more pixels. Astronomers call this seeing, and it
changes from night to night. The shape that one point of light takes in the
image, set by the telescope and the seeing, is called the point-spread
function, or P S F. So two pictures can differ
because the sky really changed, or because the observing conditions did.

## s5 — Two names (≈10 s)
**Visual:** two frames side by side, from the s2 flipbook's star field (not the
course pair, so nothing primes checkpoint 0.2), labelled "reference
image" (left) and "target image" (right), with "usually earlier, compared
against" and "new, searched for changes" underneath.
**Narration:** The picture you compare against is the reference image. It's
usually the earlier one. The new picture, where you look for changes, is the
target image.

## s6 — In this module (≈35 s)
**Visual:** a card titled "Module 00: What changed in the sky?". Three rows
appear one by one, in step with the narration:
- **Start:** "what a picture is made of";
- **Do:** "find how two pictures differ" → "plan how to keep only the real
  changes";
- **Finish:** "meet the cuPhoton stages that carry out your plan".

A smaller line underneath: "made-up images · you won't write code · no
telescope data yet". In the corner, a person icon labelled "you think" and a terminal
icon labelled "your tutor types".
**Narration:** Now, here's what you'll do in this first module. You'll work with two
small, made-up pictures of the same sky, one reference and one target. You'll
start by looking at what a picture is made of. Then you'll find every way the
two pictures differ, and work out a plan to keep only the real changes in the
sky. You'll finish by meeting the cuPhoton stages that carry out your plan.
You won't write any code, and there's no real telescope data yet. Your tutor
is an AI agent: it does the typing, and you do the thinking.
