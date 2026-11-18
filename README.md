# cuPhoton Learn

An interactive textbook for cuPhoton. Lessons read like a book; an LLM tutor
(pi SDK, any OpenAI- or Anthropic-style endpoint) runs real work in the
learner's workspace behind the page and talks to the learner in "Your turn"
blocks and in the margin. One server per learner, on the GPU machine. See
`PLAN.md` for the design and milestones, and `docs/M0-harness-spike.md` for M0.

## Run it

```bash
npm ci
npm run build          # the page, into web/dist
npm run smoke          # GPU, endpoint, course, Python env
npm start              # http://127.0.0.1:8765
```

From a laptop: `ssh -L 8765:127.0.0.1:8765 <gpu-machine>`, then open
http://localhost:8765.

While editing, run `npm run dev` instead of `npm start`: same address, the
server restarts when `server/`, `course/` or the tutor's prompt and skills
change, and the page is rebuilt on every save (reload the browser). A
restart cuts off a tutor turn in progress; the conversation survives. For
hot reload of the page, `npm run dev:server` with `npm run dev:web` (Vite on
:5173, proxied to the server).

## The model

On first start with no model configured, the page opens a setup form
(`/setup`): pick a provider (Anthropic API, NVIDIA API catalog, the NVIDIA
inference hub, or any OpenAI-compatible server such as vLLM or NIM), paste a
key, name the model. It makes one tool call to test it, then saves it to
`learner/endpoint.json` (readable by you only; `learner/` is never
committed) and starts the tutor. `/setup` changes it later (restart to
apply); the admin page links to it. Without that file, the server uses
`TUTOR_PROVIDER`/`TUTOR_MODEL` from `tutor/pi-agent/models.json` and the key
from the environment, as below.

## Who can use it

The tutor runs shell commands on this machine, so the course belongs to the
first browser that opens it: the server makes a random token
(`learner/access.json`) and sets it as a cookie; every page, API call and
the WebSocket need it, and requests from other sites are refused. To open
the course in another browser, use the access link in
`learner/access-link.txt` (also printed in the server log, and copyable from
the admin page). To hand the course to a new browser, delete
`learner/access.json` and restart. `ACCESS=open` turns the check off, for a
machine only you can reach.

## Configuration (environment or `.env`)

| variable | default | |
|---|---|---|
| `INFERENCE_API_KEY` | | key for the provider in `tutor/pi-agent/models.json` |
| `TUTOR_PROVIDER`, `TUTOR_MODEL` | `nvidia`, `aws/anthropic/bedrock-claude-sonnet-5-5` | any model listed in models.json |
| `TUTOR_THINKING` | `off` | pi thinking level |
| `CUPHOTON_DIR` | `~/cuphoton-overnight/cuPhoton` | pinned checkout (commit in `course/course.yaml`) |
| `LEARNER_PYTHON_BIN` | `$CUPHOTON_DIR/.venv/bin` | Python with NumPy, SciPy, Matplotlib, cuPhoton |
| `LEARNER_DIR` | `learner/` | progress, conversations, workspace, tutor sessions |
| `CUPHOTON_LEARN_FEEDBACK_URL` | | where consented feedback notes are POSTed |
| `PORT`, `HOST` | `8765`, `127.0.0.1` | |
| `PI_OFFLINE` | `1` | no pi network activity besides the endpoint |
| `ACCESS` | | `open`: no access check (see "Who can use it") |
| `PING_EVERY_MIN` | `10` | background endpoint ping for the admin page; `0` turns it off |

`/admin` (the "Admin" link in the course header) shows how the tutor is
doing: context size and compactions, response times, errors and retries,
spend, GPU memory and disk, and the endpoint's response to a small ping
every 10 minutes (shared endpoints get busy at times). It reads `learner/sessions/` and
`learner/metrics.jsonl`.

To use another endpoint or self-hosted model, add a provider to
`tutor/pi-agent/models.json` and set `TUTOR_PROVIDER`/`TUTOR_MODEL`.

## Layout

- `course/` — learner-facing `lesson.md` + tutor-only `tutor.md` per lesson,
  plus vocabulary, concepts and misconceptions.
- `tutor/` — the tutor's system prompt (`SYSTEM.md`) and skills. This is
  the only context the tutor gets.
- `server/` — content parser, pi sessions and page tools, run recorder, state.
- `web/` — the page (React).
- `media/` — videos with `.srt` subtitles, listed in `media/videos.yaml`; the pipeline that makes them (scripts, scenes, narration) is in `media/pipeline`, see `media/README.md`.
- `sim/` — the M0 simulated-learner harness.

## Lesson format

Prose, with `[[term]]` look-ups from `course/vocabulary.yaml` (`[[@concept-id]]`
for concepts), and these directives:

```
:::video v1-why-not-subtract        :::slot two-nights        :::your-turn what-changed
:::                                 title: The two nights     title: What changed?
                                    caption: …                prompt: …
:::figure dipole.png                :::                       image: dipole.png
title: …                                                      lead: Here is a [[dipole]]…
caption: …                          :::chain hi=xRep          :::
:::                                 caption: …
                                    :::                       :::closure
                                                              found: …
:::ref                                                        raises: …
text: …  label: …  video: v1-…                                :::
:::
```

Slots are filled at run time by the tutor's `show_figure`. Everything the tutor
puts on the page carries a run record built from what actually ran.
