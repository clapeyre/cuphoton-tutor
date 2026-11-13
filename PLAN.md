# cuPhoton Learn: implementation plan

A web app that teaches cuPhoton as an interactive textbook: lessons read like a
book, an LLM tutor runs real cuPhoton work on a GPU behind the page, and the
learner talks to the tutor in "Your turn" blocks and in the margin.

The design reference is `design/mockup.dc.html` (the Claude Design canvas
"cuPhoton Learn mockup"; the file is its source, it only renders in the design
tool).

**This repo starts fresh.** The earlier course work lives in `cuphoton-learn`
(dl-machine, `~/cuphoton-overnight/cuphoton-learn`, branch `overnight`). Read it
as reference so nothing is relearned the hard way, but don't copy it in.
Worth reading there: `AGENTS.md` (the tutor contract), `.claude/skills/*`,
`course/concepts.yaml`, `course/vocabulary.yaml`, `course/misconceptions.md`,
`course/modules/*/module.md`, `media/VIDEOS.md` and `media/pipeline/`,
`learner/feedback-queue.jsonl` (field feedback), and next to it
`overnight/MORNING.md` and `overnight/reports/review-module00.md`. cuPhoton is
pinned at `ff4d26018eb4a5fed391d196ebe424736c6498e5`.

## Constraints that shape everything

- **Runs at the learner's compute centre.** On-premises, on a machine with a GPU,
  possibly with no outside network. Learners reach the page through a browser,
  usually over an SSH tunnel.
- **One server, one learner.** Everything runs locally on the learner's GPU
  machine; the only remote dependency is the tutor's inference endpoint. No
  multi-tenancy, no scheduling. Scaling to many learners means many instances,
  later, if ever.
- **Any model behind an inference endpoint.** No dependency on one vendor.
  Development uses Claude Sonnet 5.5 through the NVIDIA endpoint (`NVIDIA_API_KEY`
  in `.env`), to keep the model constant while the harness changes.
- **Code stays backstage.** The page shows concepts, figures and run records.
  Code is reachable from a run record, never the main surface.

## Decisions taken in the mockup

- **Names:** course → units → lessons (Unit 00, Lesson 0.4).
- **Progress:** one language only, Khan-style boxes per lesson, grouped by unit
  (empty / half / full). Same boxes in the top strip and the left map. No attempt
  counts shown to the learner (they stay in `progress.json` for authors).
- **The page is a textbook.** Prose, captioned figures, videos. No part labels,
  no boxes, no text that explains the UI. Only "Your turn" is set apart.
- **Your turn:** a conversation of any length. Once settled it folds to a
  one-line summary with a ✓ and "Show the conversation (n turns)".
- **Look-ups are inline.** A key term, a diagram box: its short definition opens
  beneath it. The depth layers in `concepts.yaml` (Picture / Use / How / Edge)
  are for the tutor, never shown as UI.
- **The margin is for conversations only.** "Ask about anything on this page",
  with an optional pointer ("About: …") set by selecting text, "Ask about this"
  on a figure, "Pause and ask" on a video, or "Ask the tutor more" under a
  definition. The tutor sees the whole lesson either way; the pointer only says
  what "this" means. Closing returns the learner to where they were (and resumes
  the video at that second).
- **Run records, not narration.** Anything the agent produced carries a caption
  line, "Made by xRep · CPU · 0.4 s · Run record". Authored text never says
  "the agent will now…".
- **Hold-back rules survive in the UI.** A definition or concept that would
  answer an open "Your turn" shows "We come back to this in lesson X".
- **Earlier material is referenced, not repeated** (e.g. a recap video opens in
  the margin).

## Architecture

```
browser (lesson page + margin; React + KUI)
   │  HTTP + WebSocket (via SSH tunnel)
server (Node/TypeScript, on the GPU machine, one learner)
   ├─ content: parses units/lessons into pages
   ├─ tutor: pi SDK sessions (one main thread, forks for margin threads)
   │     ├─ built-in tools: read, bash, edit, write (run cuPhoton in the learner workspace)
   │     ├─ page tools (pi extension): the contract below
   │     └─ skills: cuphoton, adapt-pace, unstick, report-feedback
   ├─ run recorder: wraps tool calls, writes run records for every produced artifact
   └─ state: learner/progress.json, conversations, feedback queue
inference endpoint (configurable; NVIDIA endpoint for dev)
```

**Harness: pi** (`@mariozechner/pi-coding-agent`, SDK mode). Why: small system
prompt we own (`SYSTEM.md`), any provider through `models.json` (OpenAI- or
Anthropic-style APIs), Agent Skills format, extensions for custom tools, session
trees with fork (margin threads), `PI_OFFLINE=1` for air-gapped sites.
Fallback if the spike fails: Claude Agent SDK, accepting the Claude-only limit
for now.

**Context isolation.** pi loads `AGENTS.md`/`CLAUDE.md` from the cwd *and every
parent*. The repo's development instructions (for Claude Code) must not reach
the tutor. Load the tutor's context explicitly (SDK resource loader, or
`--no-context-files` plus explicit files) and point skills at the course's own
skill folder.

### The page ↔ tutor contract (page tools)

The tutor never writes HTML. It drives the page through a few tools:

| tool | does |
|---|---|
| `show_figure(path, title, caption)` | places an artifact from the learner workspace into the current lesson; the run recorder attaches its record |
| `ask(turn_id, text)` | posts the tutor's line in a Your-turn conversation |
| `settle(turn_id, summary)` | marks the turn settled, writes the one-line summary, updates progress |
| `reveal(lesson_id)` | shows the lesson's closure ("We found / Which raises") once its turns are settled |
| `file_feedback(kind, …)` | the existing report-feedback path |

Margin threads use the same session (forked at the current point) and reply as
plain assistant text. Lesson text, figures authored in the course, videos and
definitions are rendered from content, not by the tutor.

**Frontend: KUI** (`@kui/foundations-react`, dark theme), as in the mockup. Fine
for now: nothing ships outside NVIDIA without approval, and it will likely be
rebuilt before it does.

### Content format

New content, written in this repo. Split what the learner sees from what the
tutor is told. In `cuphoton-learn`, `module.md` mixes both, which is how "What
was injected stays hidden for now" leaked onto the page.

```
course/
  course.yaml, concepts.yaml, vocabulary.yaml, misconceptions.md   (as today)
  units/00-what-changed/
    unit.yaml                     title, objectives, needs
    0.4-meet-the-names/
      lesson.md                   learner-facing: prose + directives
      tutor.md                    tutor-only: probes, pass criteria, hold-backs
media/                            videos, stills, srt
```

`lesson.md` uses a few directives (MyST-style), e.g. `:::video v1-why-not-subtract`,
`:::figure path caption`, `:::chain hi=xRep`, `:::your-turn id prompt`,
`:::slot` (filled by `show_figure` at run time). Key terms come from
`vocabulary.yaml` (`introduce_at`), hold-backs from `hold_back`.

## Milestones

**M0 · Harness spike (no UI).** pi CLI on dl-machine, Sonnet 5.5 via the NVIDIA
endpoint (custom provider in `models.json`), pointed at `cuphoton-learn` in
place (its `AGENTS.md` and four skills, read from there, nothing else loaded).
This is the one place the old repo is used directly: it isolates the harness as
the only variable. Replay the overnight personas on Unit 00 with the
existing sim harness. Pass if it scores within noise of the Claude Code runs,
holds back checkpoint answers, and files feedback. Record what had to change.

**M1 · One lesson end to end.** Server + page for Lesson 0.2 only: prose, figure,
one Your turn wired to the tutor, the margin with pointer and return-to-place,
run records on figures the tutor produces.

**M2 · Content format.** Write Unit 00 fresh as `lesson.md` + `tutor.md`, using
the old `module.md` as source material; render it
with the inline definitions, chain diagram and videos; progress boxes driven by
`progress.json`.

**M3 · Full Your-turn lifecycle.** Settle, fold, unroll; closure reveal; hold-back
rules in definitions; feedback queue.

**M4 · Units 01–02 on the GPU.** Real cuPhoton runs through the tutor, run
records from receipts (`summary.json`), slots filled at run time.

**M5 · Packaging for compute centres.** One instance per learner: one container
(or uv + npm lockfiles), offline mode, endpoint and model as config, a smoke test
that proves GPU, endpoint and course load.

**Then:** swap models (other vendors, self-hosted) against the M0 sims.

## Open questions

None blocking M0.

## Inference endpoint (dev)

- **API:** OpenAI-compatible chat completions. Base URL
  `https://inference-api.nvidia.com/v1`, key in `.env` as `INFERENCE_API_KEY`.
- **Model:** `aws/anthropic/bedrock-claude-sonnet-5-5`.
- **pi setup:** a custom provider in `models.json` with the OpenAI completions
  API, that base URL and that model id.
- **Checked on 13 Nov (curl):** function calling works, non-streaming and
  streaming (tool-call arguments arrive as deltas, `finish_reason: tool_calls`).
  Usage reports cache fields (`cache_read_input_tokens`, `cached_tokens`), all 0
  on these single calls. Whether prompt caching kicks in over this API on long
  sessions is untested; check it in M0, as it drives cost and latency.
- **Other models on the same endpoint** (258 listed by `/v1/models`). The tutor
  must be **multimodal**: it looks at the figures it makes, the learner's
  selections on them, and video stills. That rules out text-only models.

## Model comparison (after the setup is solid, not before)

Only once M0–M3 are satisfactory on Sonnet 5.5: change the model, nothing else,
and rerun the same sims.

Tutoring is nuanced, live interaction with a person, so the model can't sit far
below Sonnet on general intelligence. Two questions, two sets of candidates:

- **Vendor independence** (does the setup work beyond Claude?): models close to
  Sonnet on the Artificial Analysis index and comparable in price on the
  internal endpoint. **Gemini 4 Argon** (`gcp/google/gemini-4-argon`) and
  **GPT 6.1 Sol** (`openai/openai/gpt-6.1-sol`, also under `azure/openai/`).
  Run these first.
- **Self-hosting** (can it run fully on-premises?): **Nemotron 3.5 Super VL**
  (`nvidia/nvidia/nemotron-3.5-super-vl`). Self-hostable and NVIDIA's own, so a
  pass makes the on-premises story real, but it ranks well below Sonnet, so
  expect gaps; the point is to find where it falls short (holding back answers,
  judging learner replies, reading figures, tool use). Smaller multimodal options
  (`nemotron-3-nano-omni-30b-a3b-reasoning`, `nemotron-nano-12b-v2-vl`) only if
  Super VL comes close.
- **Endpoint check, 13 Nov** (`tools/endpoint_check.py <png> <model>...`, using
  the 0.4 dipole figure; correct answer: red lobe on the right):

  | | tool call | tool call, streamed | image → text | image → tool call |
  |---|---|---|---|---|
  | Sonnet 5.5 (`aws/anthropic/bedrock-claude-sonnet-5-5`) | ✓ | ✓ | ✓ right, with lobe positions and amplitudes | ✓ right |
  | Nemotron 3.5 Super VL (`nvidia/nvidia/nemotron-3.5-super-vl`) | ✓ | ✓ | ✓ right | ✓ right |
  | Nemotron 3.5 Super VL preview | ✗ once: asked for the summary instead of writing one | ✓ | ✓ right | ✓ right |
  | Gemini 4 Argon (`gcp/google/gemini-4-argon`) | ✓ | ✓ | ✓ right, with the lobes' row | ✓ right |
  | GPT 6.1 Sol (`openai/openai/gpt-6.1-sol`) | ✓ | ✓ | ✓ right | ✓ right |

  Latency per call here: Sonnet 2–3 s, GPT 6.1 Sol 3–4 s, Gemini 4 Argon 5–8 s,
  Nemotron 1.5–6 s (one call each, so only indicative).

  Notes for the Nemotron runs:
  - It is a reasoning model: 135–410 reasoning tokens per call here, counted in
    `max_tokens`. At 400 the preview returned nothing (`finish: length`); give
    it several thousand.
  - It answers tool calls with a stray `"\n\n"` text content; the harness should
    ignore whitespace-only content.
  - The shared endpoint returned 429 "model capacity reached" on the first try;
    retrying after 20 s worked. Plan for retries in sim runs.
  - Sonnet's description was richer (positions, amplitudes); Nemotron's was
    correct but bare. One image says nothing about tutoring quality: that is
    what the sims are for.

## Settled

The repo starts fresh (cuphoton-learn is reference only); KUI for the
frontend; one server per learner.
