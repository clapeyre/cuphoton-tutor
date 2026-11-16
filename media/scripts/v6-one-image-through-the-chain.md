# v6 — One image through the shipped chain

Opens Module 05 (top of 5.1). A hook: what the transient chain is, what flows
through it on the GPU, what it leaves behind. Gives away no checkpoint: it never
mentions the PSF width, the kernel stamps or bias, and doesn't say what to read
in the summary. Data: media/scenes/data_v6.py runs the chain on the Module 04
pair with Module 05's final configuration (real timings, transfers, catalog row,
summary).

Subtitle: "Module zero four" -> "Module 04"
Subtitle: "x pois" -> "xPois"
Subtitle: "x fit" -> "xFit"
Subtitle: "x rep" -> "xRep"

## s1 — By hand, then by the thousand
**Visual:** the chain as boxes (xRep, xPois, detect, xFit), each lit in turn as
"one call"; then the one image pair multiplies into a stack of hundreds.
**Narration:** In Module zero four, you ran the chain one call at a time, on one
pair of images. A survey has thousands of pairs every night. So cuPhoton also
ships the chain as one pipeline: the transient chain.

## s2 — One image through it
**Visual:** the target night enters a box labelled GPU. Stage labels light up in
order, each with its real time: read, template, refine, mask, x pois, detect,
stamps, x fit, error budget. At the end, an arrow out of the box: "one download,
5.7 kB", and "intermediate files: 0".
**Narration:** One worker per GPU takes each image from its files to a table of
candidates. It reads the planes, puts the reference on the target's grid, matches
and subtracts, finds the hotspots, cuts stamps, fits them, and builds an error
bar for each. The images stay on the GPU the whole way. What comes back is one
small download.

## s3 — What comes back
**Visual:** the supernova's catalog row: position, flux 43,657, error bar 345,
then its terms appearing in their own columns: fit 183, corr 292, kfit 1. Then
the item's summary: the GPU's name, the reader requested and the reader that
ran, the error terms used, each stage's time.
**Narration:** Two things come back. A catalog, with one row per candidate: a
position, a flux, and an error bar built from several terms, each in its own
column. And a summary for every image: which GPU, which reader actually ran,
which error terms went in, and how long each stage took.

## s4 — Driven by a configuration
**Visual:** a configuration file builds up: the survey block (where each plane
is, variance kind, grid, mask bits), then one block per stage. A tag on it:
"shipped values: chosen for another survey".
**Narration:** Everything it does is set in one configuration file. First, where
each plane of your data is and what its numbers mean. Then every stage's
settings. It ships with values chosen for another survey's data. Yours is
different.

## s5 — The question
**Visual:** the module question, on its own.
**Narration:** So, the question of this module. When the shipped pipeline says
it's done, can you trust what it wrote, on your data? You already have every
habit you need to find out.
