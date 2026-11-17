---
id: "4.6"
title: Teach a classifier
question: Can a classifier you train sort the candidates for you, and how would you know what it gets wrong?
terms: [real / bogus, classifier score, training set]
---

In 4.3 you sorted four candidates by looking: is there a source in the
reference, does the residue have the shape of a point of light, is it
positive or a twisted pair? A survey night has thousands of candidates, so
surveys train a classifier to ask those questions for them.

cuPhoton's classifier is xScan: a small neural network (the transformer of
Inada et al. 2026) that reads three cutouts around each candidate, the target,
the reference and the difference, and returns a [[classifier score]] between
0 and 1. No trained model ships for Pan-STARRS1, so you'll train one. That
needs labelled examples, the [[training set]], and you have no labelled
history for this survey. What you do have is 4.4's trick: anything you plant
yourself is real by construction.

:::your-turn labels
title: Where the labels come from
prompt: From this pair alone, what would you use as examples of real and of bogus candidates to train it on? Then ask the tutor to build the dataset, check it, and train.
:::

:::slot scores
title: Its verdict on 4.3's candidates
caption: The four candidates of 4.3, as the classifier sees them (each cutout in units of its own noise), with its score.
:::

:::your-turn never-seen
title: What has it never seen?
prompt: Its score on its own test cutouts is perfect, and it agrees with you on A to D. Before you let it sort the next night, what kinds of candidates were not in its training set? Predict how it would score one, then ask the tutor to test it.
:::

:::slot stress
title: Bogus it was never shown
caption: Cosmic rays and satellite trails added to the target, and the classifier's score for each.
:::

:::your-turn next-night
title: Brief the next night
prompt: Write the instruction you'd give an agent before it processes the next night of this survey, in a few lines: what it checks about the data, the noise model and masks, the run itself, the evidence it brings back, an injection test with the error-bar check, and how it sorts the candidates.
:::

:::closure
found: Trained on 480 planted point sources (real) and 88 stars and knots of M101 that are on both nights (bogus), the classifier scored its own test cutouts perfectly and agreed with you on A to D. Then it called about half of single-pixel cosmic rays real, most two-pixel ones, and nearly every satellite trail. None of those were in its training set, and the test cutouts came from the same two kinds as the training ones, so the perfect score said nothing about them. Adding synthetic cosmic rays and trails to the bogus class and retraining fixed it: none of either was called real, and it still found the supernova and every fake.
matters: A classifier learns what was in its training set, and its test score only covers the same kinds of candidates. It can't tell you about kinds it never saw; you have to ask, then test. The score isn't a probability either. 0.99 here means "looks like my planted sources", not "99% likely to be a supernova". On a real night, where bogus outnumber real by far, even a good classifier passes some bogus. So check it the way you checked the pipeline: plant what you're worried about and see what comes back.
raises: You've built the whole chain by hand and tested every part on real data. cuPhoton also ships it as one pipeline. When it says it's done, can you trust what it wrote?
:::
