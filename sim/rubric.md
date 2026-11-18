# Grading rubric for simulated sessions (the web app)

You get: the transcript (what the learner saw and did, in order, including the
tutor's tool calls), the persona with its hidden beliefs, the lessons the
session covered (lesson.md, which the learner sees, and tutor.md, the tutor's
private notes with the expected answers and hint ladders), the misconception
catalogue, the run's progress.json and feedback queue, and its metrics. You
don't know which model was the tutor; don't guess.

Score each 0–3 with one-line evidence (quote the step number). When a criterion
never came up in this session (e.g. a hidden belief whose lesson the learner
never reached), write "n/a" instead of a score and say why.

1. **Contract:** predictions before runs; one step at a time; short messages;
   no Your-turn answer leaked (in a box, in a figure caption, or in a side
   question's answer); hint ladder in tutor.md respected.
2. **Placement & pace:** matched this persona; sped up or slowed down at the
   right moments; didn't waste an expert's time; didn't lose a newcomer.
3. **Catalogued misconceptions:** each hidden catalogued belief that its lesson
   reached: surfaced? resolved by evidence rather than assertion?
4. **Novel misconceptions:** each hidden uncatalogued belief: surfaced?
   resolved? reported with file_feedback (check the queue)?
5. **Unstick:** when the learner was stuck or "ok"-ing, did the tutor notice,
   diagnose, and change representation?
6. **Visuals:** slots filled with the right figure, in time; captions honest
   and legible; figures used where they'd help and referred to correctly.
7. **Accuracy:** any claim about cuPhoton or the physics that the lesson,
   tutor notes or plain physics contradict? List them.
8. **Page mechanics:** replies landed in the right box; a box settled when, and
   only when, the learner had shown the idea (not on a guess, not long after);
   summaries in the learner's words; the closing revealed only after every box
   settled; side questions answered in the margin without answering an open
   box; no empty or "lost my train of thought" replies; tool errors recovered.
9. **Outcome:** at the end, could this learner explain what the lessons they
   finished set out to teach (judge from their own words)?

Also report:
- **Learner-sim fidelity (0–3):** did the simulated learner stay in character?
  Did it know things the persona couldn't? Low fidelity makes the run
  unreliable; say so.
- **Worst moment:** the single exchange a real learner would have minded most.
- **Top 3 fixes**, each tied to a file (tutor/SYSTEM.md, a skill, a lesson's
  tutor.md or lesson.md, the catalogue) with the concrete change, and whether
  it's a general tutoring fix or specific to this model.

Return JSON only:
{"scores": {"contract": 0-3|"n/a", "placement_pace": ..., "catalogued": ..., "novel": ...,
 "unstick": ..., "visuals": ..., "accuracy": ..., "page_mechanics": ..., "outcome": ...},
 "evidence": {"<criterion>": "one line, with step numbers", ...},
 "accuracy_issues": ["..."], "fidelity": 0-3, "fidelity_note": "...",
 "worst_moment": "...", "fixes": [{"file": "...", "change": "...", "scope": "general|model"}],
 "summary": "three sentences"}
