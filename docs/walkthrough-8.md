# Walkthrough 8 · Module 07, the xBeam track

Rough notes are fine. Put the lesson number first, and the time if you can.

What's new: Module 07, "Two receivers, one signal", after 6.1. Restart the
server first. 7.1 measures a known delay and then two hidden ones; 7.2
correlates three synthetic radio stations (VDIF recordings, a job, the
command line on the GPU) with one clock wrong; 7.3 finds GW150914's delay
between the two LIGO detectors from the public data. Everything lands in
`learner/work/07/`, which you can browse with Files.

## 7.1

## 7.2

## 7.3

## Overall

(Author, 17 Nov, in conversation) Went through the module and liked it; no
real comments, a good intro. Asked for the xRay and xImage tracks, and for
"Where next" to come at the end: the tracks should follow the image modules
in stride, and the closing module should give the full map of cuPhoton and
open a discussion of the learner's own work.

## What changed in response

- **Order.** The tracks follow Module 05 directly: xBeam is now Module 06
  (6.1–6.3, `work/06/`), xRay Module 07, xImage Module 08, and "Where next"
  closes the course as Module 09 (9.1). 5.4 leads into the tracks, each
  track's last lesson into the next, and 8.3 into 9.1.
  `tools/renumber-learner.py` moved your progress and `work/07/` to the new
  numbers (backup in `learner/backup-before-renumber/`).
- **9.1** is now "what you've run" (all four kinds of data, with their
  modules and chapters) plus "what you haven't" (scale-out), then an open
  conversation about your own work: what you measure, which part fits, how
  parts connect, what you'd check on a first run.
- **Module 07, Pump and probe (xRay)** and **Module 08, Many frames, one
  scene (xImage)**, three lessons each, each opened by a video (v8, v9).
  Notes go in `docs/walkthrough-9.md`.
