# Why this way of learning

Evidence and the author's own words, collected for talks about this course
and for the course's framing (`ROADMAP.md`, step 3). Newest first. Add to it
whenever a walkthrough shows it.

## The message, in the author's words (walkthrough 5, 4.6, 17 Nov 2026)

> If I were to teach this course to astronomers, 20% of what I would be trying
> to convey is the fact that cuPhoton can do data processing fast. 80% of it
> would be a plea telling them: please stop opening your Python text editor
> when you're starting data processing and spending a week doing what you
> could do in 20 minutes having a chat with your agent.

> The fact that you have held my hand, trained the model, tested it, showed
> me the results on the test set, then changed the data, retrained the model
> to get better results. All of that in a single conversation without me ever
> seeing the code is absolutely amazing.

## What happened in that conversation (4.6)

One lesson, one conversation, no code written by the learner:

- labels designed by the learner (real = planted sources, bogus = sources on
  both nights), built into an xScan dataset from the real pair;
- validated and trained with the user guide's own commands, on the GPU, in
  seconds;
- a perfect test score (ROC AUC 1.000), then a stress test on kinds of bogus
  it had never seen: 40–98% of cosmic rays and trails called real;
- the training data changed, the model retrained and retested: 0 of 40 of
  each kind called real.

The learner's attention stayed on the science questions (what counts as
bogus, what a test score covers), not on file formats or training loops.

## Earlier signs

- Walkthrough 5, 4.5: stacking taught caution about one's own preconceptions
  ("more data is better") because the learner predicted, then measured.
- Walkthrough 5, 4.4: an injection test, designed in conversation, found the
  error bars 1.2–1.5× too small, a fact "nobody would have told you".
