---
name: report-feedback
description: Send structured feedback upstream to the course authors when something in this course didn't go as designed. Use it whenever a learner shows a misconception that isn't in course/misconceptions.md (including a field meaning of a course term that differs from ours), stays stuck after the unstick playbook, hits wrong or confusing course content or cuPhoton docs, hits an environment failure, gets frustrated, or when you notice you made an error, even if the learner doesn't ask you to report anything.
---

# Report feedback

The course improves only from what goes wrong in real sessions. Notice it and
send a short, structured note with the `file_feedback` tool, in the same turn,
while the details are fresh; then go back to teaching.

| kind | when |
| --- | --- |
| `novel_misconception` | A wrong belief not in `course/misconceptions.md`, including a term their field uses differently. File it in the same turn you first respond to it. |
| `stuck_unresolved` | Three unstick moves without progress |
| `content_error` | Lesson text, figure, exercise or cuPhoton doc is wrong, unclear or out of date |
| `tutor_error` | You stated something false, leaked an answer, or broke the contract ("I was wrong", "one correction") |
| `env_failure` | Install or run failure not covered by docs/troubleshooting.md |
| `frustration` | The learner is annoyed, bored, or about to quit |
| `delight` | Something worked unusually well (worth keeping) |

Don't report routine, catalogued misconceptions that the lesson handled. Do
report when a catalogued probe *failed* to surface or fix one (`content_error`).

Keep it short and specific: no personal data, no paths from the learner's home
directory, learner quotes only if under 30 words. Fields: `kind`, `summary`,
`lesson`, `learner_words`, `tried`, `resolved` (yes/no/partly), `suggestion`.

The server shows the learner every note and sends it only if they consented;
otherwise it stays queued locally. Never block the lesson on it.
