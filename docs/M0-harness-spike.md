# M0 · Harness spike: pi in place of Claude Code (13 Nov)

**Verdict: pass, with the same weak spot as before.** pi 1.5.2 with Sonnet 5.5 through
the NVIDIA endpoint tutors the old course about as well as Claude Code did. It costs
about a sixth as much per session, and sessions run to their natural end.

## Setup

- Harness: `sim/simulate_pi.py`, a copy of `overnight/sim/simulate.py` in which
  only the tutor call changed. It runs `pi -p --mode json` with a persistent
  session, `-nc -ns -ne -np --no-mcp`, `--append-system-prompt AGENTS.md` and
  `--skill` for each of the four skills, all read from the course copy in place.
- Learner: unchanged (`claude -p`, haiku, same rules, same personas).
- Model: `nvidia/aws/anthropic/bedrock-claude-sonnet-5-5`, configured in
  `tutor/pi-agent/models.json` with the OpenAI completions API.
- Grading: same rubric, an Opus grader per run, with no baseline scores shown.
- Runs: `runs/1113-113428-*` (gitignored). Each has `grade.md`.

## Scores (/24)

| persona | Claude Code CLI (10 Nov) | pi (13 Nov) | pi fidelity |
|---|---|---|---|
| p1 newcomer | 17 | 17 | 1 |
| p2 astronomer | 16 | 13 | 2 |
| p3 CUDA dev | 13 | 11 | 1 |
| p4 expert | 14 | 15 | 3 |
| **total** | **60** | **56** | |

The overnight report put noise at ±2 per run, so three of the four runs are
within noise. p2 is 3 lower: the tutor leaked the 1.4 edge-band answer (it
caught this itself and filed it), and it confirmed which image xRep moves before
asking for the prediction. Fidelity was 1/3 in two runs (the learners were too
expert), so this comparison is indicative, as in every earlier round.

## The three checks M0 asked for

- **Within noise of the Claude Code runs:** yes, apart from p2 (−3).
- **Holds back checkpoint answers:** mostly. There were no outright leaks in
  p1, p3 or p4. There were partial leaks in p1 (0.2), p2 (1.4) and p3 (a
  0.4 hint that named a cause). In two of them the tutor caught the leak,
  filed a `tutor_error` and set a variant.
- **Files feedback:** yes. 6 events across the runs: `tutor_error` ×4 and
  `content_error` ×2 (p4 filed none). **No run filed a `novel_misconception`**,
  even when a planted uncatalogued belief came up and was resolved with
  evidence (p2 warp direction, p3 noise scaling, p4 NaN edge). This is the
  same failure the Claude Code runs had, so it isn't the harness. In the new
  app, filing is a page tool and the lesson notes name the beliefs to watch;
  in the first live test of the app, the tutor filed the 0.1 "background is a
  fixed floor" belief in the same turn.

## Cost, latency, caching

| | Claude Code CLI | pi |
|---|---|---|
| cost per session (Sonnet list price) | $4.6–8.8, three runs hit the $8 cap | **$0.80–1.68**, none capped |
| end of session | cost cap ×3, learner quit ×1 | learner ended ×4 |
| learner turns reached | ~20 | 14–24 |

- **Prompt caching works over the endpoint's OpenAI-style API.** Of all input
  tokens, 97% were cache reads: for p1, 1.95 M read, 53 k written, 188
  uncached.
- The smaller system prompt matters too: pi's preamble plus AGENTS.md, against
  Claude Code's.
- Wall time per run was similar (4–9 min).

## What had to change

- **The package moved:** `@mariozechner/pi-coding-agent` stops at 0.73. pi
  1.5.2 is `@earendil-works/pi-coding-agent`.
- **`pi -p` waits on stdin:** run it with stdin closed (`</dev/null`).
- **models.json compat for the endpoint:**
  - `supportsDeveloperRole: false`;
  - `supportsStore: false`;
  - `maxTokensField: max_tokens`;
  - `requiresNonNullAssistantContent: true`.

  These are set defensively; none was tested on its own.
- **Context isolation:** `-nc` (no AGENTS.md/CLAUDE.md discovery) plus explicit
  `--skill` paths is enough for the CLI. In the app, the SDK takes a custom
  `ResourceLoader` that returns `tutor/SYSTEM.md` and `tutor/skills/` and
  nothing else.
- **Nothing in the course had to change** for pi.

## Not tested yet

- Other models on the same sims (planned after M3).
- Nemotron's stray `"\n\n"` content. The app ignores empty text, but this
  hasn't been checked against that model.
