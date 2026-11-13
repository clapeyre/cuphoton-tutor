---
name: unstick
description: Playbook for when a learner is stuck, confused, wrong twice in a row, or quietly disengaging in this course. Use it whenever a learner's prediction misses, they answer "ok"/"sure"/"I guess" without substance, they ask for the answer, they repeat a wrong idea after a correction, their replies get shorter, or they say they're lost, even if they don't ask for help.
---

# Unstick

Being stuck is information. Before explaining anything, find out *which kind*
of stuck it is; the fix is different for each.

## 1. Notice

Signals, strongest first: the learner says they're lost; a second wrong
prediction on the same idea; a correct answer with a wrong reason; "ok" with no
content after an explanation; asking for the answer before trying; shorter and
shorter replies; questions that reveal a missing term ("what's a kernel?").

## 2. Diagnose with one question

Ask one short question that tells the kinds apart. Don't explain yet.

| Kind | What it sounds like | Diagnostic question |
| --- | --- | --- |
| Missing prerequisite | Doesn't know a term or idea the step assumes | "What does *kernel* mean to you here?" |
| Misconception | Confident and wrong; consistent reasoning from a false belief | "Walk me through why you expected that." |
| Overload | Knew it a step ago, now lost; too many new things at once | "Which part was still clear?" |
| Representation | Gets the words, not the picture (or vice versa) | "Can you sketch what you think the image looks like?" |
| Environment | Error messages, nothing renders, can't see the output | "What's on your screen right now?" |
| Motivation | Doesn't see why this matters to them | "What would you use this for?" |

Check `course/misconceptions.md` (absolute path in your system prompt) for a matching entry and its probe. If none
matches, it's a candidate for the `report-feedback` skill.

## 3. Move

Pick the smallest move that fits the kind. One move, then check.

- **Rewind one layer.** Use `course/concepts.yaml`: drop to the concept's
  prerequisite or to a lower layer (L1 → L0). Say you're doing it: "Let's step
  back to what the blur is doing, then come back."
- **Change representation.** If words failed, show it: plot the actual array,
  a single row's profile, a before/after pair, a cutout. Prefer the learner's
  real data over a schematic. If a picture failed, use numbers: print a 5×5
  patch. If both failed, use an analogy from their own field (ask at intake).
- **Shrink the step.** Split the stage into its smallest parts. Ask for a
  prediction on just the first.
- **Contrast case.** Show the version where the idea fails (plain subtraction
  next to matched subtraction). Differences teach better than examples.
- **Let them run into it.** For misconceptions: set up a quick experiment
  where their belief predicts something visible, run it, compare. Don't
  correct a misconception by assertion.
- **Make a visual explainer** when the idea has structure (a data flow, a
  coordinate convention, host vs device memory). One idea per figure, labeled
  with the learner's words where possible. Save it under `work/` and `show_figure` it so they
  can come back to it.
- **Fix the environment** directly when that's the problem; it isn't a learning
  objective.

## 4. Check, then climb back

Ask a *different* question that needs the same idea (transfer, not repetition).
If they pass, return to where you were and say so. If they fail again, try a
different move from step 3, not a longer version of the same one.

After three moves without progress: say so honestly, offer to mark the step
and move on, and use `report-feedback` (kind `stuck_unresolved`).

## 5. Record

Mention in your next `settle` summary or `file_feedback` what worked (concept, kind of stuck, moves
tried, what worked). What worked is the most valuable field.
