---
name: adapt-pace
description: Choose how deep and how fast to go for this learner, using the layered concept graph in course/concepts.yaml. Use when a lesson opens, whenever a learner breezes through a Your turn, seems bored, asks to skip, or slows down, so the course runs at a different speed for a beginner and for someone who already knows most of it.
---

# Adapt pace

Each concept in `course/concepts.yaml` has prerequisites and four layers. The
layers are for you; the page never shows them.

- **L0 picture:** intuition, a visual, no math, no code.
- **L1 use:** what to ask the agent for and what to check. The target for everyone.
- **L2 how:** the mechanism: equations, algorithm, parameters.
- **L3 edge:** limits, failure modes, source pointers.

## Level is per domain

Concepts are tagged `imaging`, `gpu` or `workflow`. An astronomer may be L2 on
imaging and L0 on gpu; a CUDA developer the reverse. Judge each domain from
the learner's answers, not from self-report.

## In a Your turn

- **Speed up** after a first-try pass with a reason: settle, don't add probes.
  Two such passes in a row: keep your lines shorter and skip L0 pictures.
- **Slow down** on the unstick signals. Drop one layer, not to the bottom.
- **Always reach L1** for each concept on the lesson's path, at any speed.
- **Offer L2/L3 as one optional sentence**, never forced: "There's a neat reason
  the edge band is exactly half the kernel width; ask in the margin if you want it."

Pass the level you judged into `settle(..., misconceptions)` notes only when it
changed; the server keeps the record.
