# Walkthrough 9 · Modules 07 (xRay) and 08 (xImage), then 9.1

Rough notes are fine. Put the lesson number first, and the time if you can.

What's new (17 Nov): the tracks now follow Module 05 in stride, and "Where
next" closes the course as 9.1. Restart the server first (the course
changed, and your progress was renumbered: xBeam is now 6.1–6.3, in
`learner/work/06/`). Module 07 "Pump and probe" opens with a video, fits
one pump-probe trace with known modes, loses a mode without a warning, and
fits a whole detector on the GPU. Module 08 "Many frames, one scene" opens
with a video, reconstructs a known scene, finds what's wrong in two bundles
that both validate, and reconstructs the M101 nights from Module 04,
supernova included. Work lands in `learner/work/07/` and `work/08/`.

This is kind of a general question, but now that I look at the growing list on the side (in the navigation pane of modules from 00 to 09), it kind of feels very much AI-generated. It's a little too punchy, like trying to be witty in the way that things are written, as opposed to trying to be purely legible and transparent.

In reality, we have a number of modules at the beginning that are on astrophotography, and then we move to other things. Pump and probe is a cute term, but come on, this is X-ray. I don't know, actually, what the more legible term would be: X-ray something, maybe synchrotron data processing or something directly with X-ray data, or crystallography. Pump and probe is just too opaque. It's cute, but it's opaque, and I think this is true of all these names for all the modules. We should try to make them very explicit and legible. 
## 7.1
I wonder whether the trace should be expressed in the text as math text instead of as code. It might be more legible.  I also don't really understand the text. It's saying it adds the mean laser-off level to both sides, but both sides of what? This is a ratio. Does that mean top and bottom?  also, I don't think S has been defined, and so I'm not quite sure how to interpret the terms of the equation. Actually, I don't really know what I'm looking at 

 okay, I asked about S, and it came up later, so that was explained pretty well. However, here I asked another question in the second block of conversation, and I got a great answer between dollar signs, which is unreadable without the MathJax rendering, unfortunately. I guess the rendering inside the tutor's response isn't fixed. 


## 7.2
 I felt like I spent a lot of time fishing for the constraints around this linear fit thing because I don't really know how it works. I did sort of get an explanation at some point, but it felt like I could have been given a little more information upfront about the type of fit we're doing.  this is a delicate balance because we don't want to overload the text, especially since some people already know this, so it's also good to go through asking on my part.
## 7.3
I'm reading and reading and reading the text, including the side trip I'm having on the side. I cannot, for the life of me, visualize what the hell it is we're talking about in terms of these tiles that we're cutting out of the detector. Could you please add a figure so that it's more obvious for the students? 
 oh, and now I've actually run through the course and seen how crucial it is to understand this averaging of rows together to even answer the course's question. We definitely need to have an explanation. The one the agent gave me when I asked is actually pretty good, so I guess you could imagine pushing that back just to having the student ask. But it still is a little weird to underspecify the problem so much. I think a visual explanation planted from the beginning would help. 
  wow, the turn-by-turn was very confusing in this one.
## 8.1
okay, right off the bat, I'm very surprised to find this here. I'm trying to grasp the context because it's saying, "Take many pictures of the same thing," but what's the thing? In this course, we've just been talking about X-ray crystallography, and now it seems we're talking about astrophotography again. If so, it's quite surprising to have this here and not group it closer to the modules that were about astrophysical photos.  maybe this would be breaking with the order of the cuPhoton user guide, but we are crafting a slightly different path here, so I think I would be okay with it. 
## 8.2

## 8.3
I'm reinforcing my previous comment: we're directly continuing the work from module 4. Couldn't module 8 be module 5? Would that break some other continuity? Maybe not 5 but 6 or 7 i guess.
## 9.1

## Overall

## What changed in response (18 Nov)

Lesson numbers below are the new ones; the notes above use the old ones
(xRay was 07, xImage 08).

**Order.** xImage moved up to Module 06, right after the image modules: it
ends on the M101 nights of Module 04, so it now follows them instead of
arriving after the X-ray module. Then xBeam (07), xRay (08), and the map
(09). The transitions were rewritten: 5.4 leads into many images of one
scene, 6.3 into the other kinds of data, 8.3 into the map. Your progress
and work folders were moved with `tools/renumber-learner.py` (backup in
`learner/backup-before-renumber-2026-11-18b/`).

**Titles.** Every module now says what it is about: 00 "Difference imaging:
the idea", 01 "A first difference with cuPhoton", 02 "Reading what a run
recorded", 03 "Running on the GPU", 04 "Real data: M101 from Pan-STARRS",
05 "The transient chain pipeline", 06 "Combining many images (xImage)",
07 "Correlating two receivers (xBeam)", 08 "Time-resolved X-ray traces
(xRay)", 09 "Your work and the rest of cuPhoton". Lesson titles are
unchanged. The v0 video's title card, and the end cards of v7–v9, were
re-rendered.

**Maths in the tutor's replies.** Display maths written over several lines
(`$$` on its own line, the equation, `$$`) now renders; before, only
one-line `$$…$$` did.

**8.1 (was 7.1).** The trace is now written as maths, plain and with the
reference shift, with $S$ defined (the mean laser-off signal over all
delays) and "top and bottom" of the ratio instead of "both sides". The fit
paragraph shows the model, a sum of damped cosines, and why each mode
takes two components.

**8.2 (was 7.2).** A paragraph up front on how linear prediction finds the
modes (a recurrence between samples at even steps, least squares, the
roots of a polynomial), so the constraints don't have to be fished for.

**8.3 (was 7.3).** A figure, `tiles.png`, shows how the detector becomes
2,048 fits: the 16 × 16 tiles, the 7-row block summed for one row's trace
(`--integrate 3`) sliding down a row at a time, and the dispersion curve
the row fits make. The text explains the same before the first turn, and
names the goal: each point on the dispersion curve should be something its
row measured. Both prompts now ask about that curve. The tutor notes say
why the walk was confusing and what to do instead (one question at a time,
always tied to the curve; ask "what would you change" only once the goal is
clear; use the script's figures). `detector.py residuals` draws the
per-fit residuals, the plot the tutor got wrong by hand; it also shows
that the residual does not catch dead rows, which the notes now say.

**6.1 (was 8.1).** Now it follows Module 05, it opens by tying back to the
two nights of M101.
