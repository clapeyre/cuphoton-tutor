# Sim 1 · Sonnet 5.5 vs Nemotron 3.5 Super VL as the tutor (18 Nov)

**Verdict: Nemotron is not ready to tutor this course.** It scores 38% of the
rubric against Sonnet's 62–68%, in both rounds. The gap is in what matters most:
it tells learners the answer, settles boxes before they reply, gets the lesson's
own data wrong, and once looped on one question 133 times. It is fast and its
tool calls mostly work. Sonnet's runs also exposed course and app fixes.

## Setup

- Harness: `sim/app_sim.ts` (new). Each run starts its own server (own port and
  learner folder) with the tutor model under test. A persona played by Haiku 5.5
  reads the page and acts through the browser's WebSocket messages: open a
  lesson, answer in a Your-turn box, ask a side question, move on, stop. It sees
  the figures the tutor places (as images) and the videos' transcripts.
- Scope: Modules 00–01 (11 lessons, 16 Your turns), the four overnight personas
  (`sim/personas/`), whose hidden beliefs mostly live there.
- Grading: `sim/grade.ts`, Opus 5.5, blind to the model, with `sim/rubric.md`
  (the overnight rubric plus **page mechanics**). It reads the transcript, the
  tutor's own log, the lessons and tutor notes, progress.json and feedback.
- All models through `inference-api.nvidia.com`. Nemotron's context set to 200k,
  like Sonnet's, so only the model differs.

## Results

Round 1 (`runs/1118-161*`) was hit by an app bug (below): five of eight runs
stalled 15 minutes at the Module 00 → 01 boundary and the learners left. Round 2
(`runs/1118-16[34]*`) is after the fix. Scores are 0–3 per criterion; "n/a"
where the session never reached what the criterion tests.

| persona | Sonnet r1 | Sonnet r2 | Nemotron r1 | Nemotron r2 |
|---|---|---|---|---|
| p1 newcomer | 15/24 | 19/27 | 9/24 | 9/27 |
| p2 astronomer | 12/18 | 14/21 | 8/21 | 8/27 |
| p3 CUDA dev | 15/24 | 16/21 | 10/21 | 11/21 |
| p4 expert | 12/21 | 10/18 | 5/18 | 8/21 |
| **share of points** | **62%** | **68%** | **38%** | **38%** |

Round 2, by criterion (Sonnet / Nemotron, summed over the runs that scored it):
contract 7/12 vs 4/12, accuracy 8/12 vs 3/12, page mechanics 6/12 vs 4/12,
visuals 10/12 vs 5/12, outcome 10/12 vs 7/12, placement and pace 8/12 vs 6/12.

Runs are small (one per persona and model per round, ±2 noise per run in
earlier rounds), but the gap is consistent: Nemotron is lower in all eight
pairings.

## What Nemotron gets wrong

- **Gives the answer.** It measures and states what the learner was asked to
  find (background levels in 0.2, the sky offset in 0.3), and corrects
  predictions in words rather than letting the figure do it.
- **Settles too early.** It asks "in one sentence, why…?" and calls settle in
  the same reply, with a summary in words the learner never used. More boxes
  closed (13–14 of 16 in two runs), less learned.
- **Misreads its own data.** It called the brightened star an unchanged one, read
  a learner's (x, y) as (y, x) and told an astronomer her correct new source was
  an existing star, and said the shift was down when it was up. It called a
  wider-PSF ring a "dipole".
- **Loops.** Round 1, p4: the same `ask` posted ~133 times into one box over
  225 s; the learner quit. Round 2, p4: one question posted three times.
- **Tool slips:** `edit` and `show_figure` calls with missing arguments
  (recovered); 2–8 tool errors per run against Sonnet's 0–2.
- Speed is fine: median wait 7–10 s, the same as Sonnet.

## What the runs found for the course itself (Sonnet runs too)

- **App bug, fixed (53f2e44):** after a module's last box, the page stayed on
  "Working" until the learner did something else. Rotating to the next module's
  thread ran from preparing-ahead before it was marked as background.
- **"Lost my train of thought" under endpoint load.** pi retries 429s for ~30 s
  (2+4+8+16) and then gives up; a learner saw the fallback in four Sonnet runs
  (and, by chance, no Nemotron run) and had to retype. 429s came even with starts staggered. Worth a longer retry
  (pi's retry settings in `server/tutor.ts`) and a gentler fallback message.
- **Duplicated replies** (Sonnet): after settle/reveal the final text repeats
  what the turn already said. SYSTEM.md should say the reply is posted once.
- **0.3/0.4 content** (both models): the tutor endorsed "a dipole means a
  matching error; a single bright spot is real", which 0.4 exists to undo; and
  labelled the brightened star among "unchanged" spots. tutor.md for 0.3 should
  carry a ground-truth table of the planted changes and their positions.
- **Placement:** the expert (p4) was never offered a faster path through
  Module 00 and left without reaching the SDK, with either model.
- **Catalogue:** graders proposed new entries for beliefs the personas voiced
  (warp direction, NaN borders, float32 everywhere); none was filed with
  file_feedback.

## Limits

- The learner sim is more articulate than p1 and never steers toward
  performance as p3 should (fidelity 1–2 of 3). The p3 numbers are weakest.
- Modules 00–01 only. The page tools and figure work are the same later on, but
  GPU modules and the tracks weren't tested.
- One run per cell. Rerun with `sim/run_matrix.sh "00,01" <model>...` and
  `npx tsx sim/summarize.ts runs/<id>...`.
