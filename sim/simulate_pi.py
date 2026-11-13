#!/usr/bin/env python3
"""M0 harness spike: replay a simulated learner against the cuphoton-learn tutor,
with the tutor running under pi instead of Claude Code. Everything else is the
same as cuphoton-learn's overnight/sim/simulate.py: same course copy, same
learner (headless Claude Code, haiku), same screen/clock notes, same outputs.

  set -a; . .env; set +a
  python sim/simulate_pi.py --persona ~/cuphoton-overnight/overnight/sim/personas/p1-newcomer.md

The tutor gets AGENTS.md (appended to pi's system prompt) and the course's four
skills, read from the course copy; no other context file, skill, extension or
prompt template is loaded (`-nc -ns -ne -np`), so nothing from this repo or its
parents reaches it.

Writes runs/<run_id>/{transcript.md, meta.json, tutor-session/} plus the course
copy with learner/progress.json and the feedback queue.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import time
import uuid

REPO = pathlib.Path(__file__).resolve().parent.parent
OLD = pathlib.Path.home() / "cuphoton-overnight"
OLD_SIM = OLD / "overnight" / "sim"
IMG = re.compile(r"\.(png|svg|jpe?g|gif|html)$", re.I)
SKILLS = ["adapt-pace", "cuphoton", "report-feedback", "unstick"]

p = argparse.ArgumentParser()
p.add_argument("--persona", required=True)
p.add_argument("--tutor-model", default="nvidia/sonnet-5.5", help="pi model pattern")
p.add_argument("--thinking", default=None, help="pi thinking level for the tutor")
p.add_argument("--learner-model", default="haiku", help="claude CLI model for the learner")
p.add_argument("--course", default=str(OLD / "cuphoton-learn"))
p.add_argument("--cuphoton", default=str(OLD / "cuPhoton"))
p.add_argument("--runs-dir", default=str(REPO / "runs"))
p.add_argument("--max-turns", type=int, default=40)
p.add_argument("--max-cost", type=float, default=8.0, help="USD, both sides combined (tutor at list price)")
p.add_argument("--call-timeout", type=int, default=900)
p.add_argument("--retries", type=int, default=3, help="per tutor call, for 429/5xx")
p.add_argument("--tag", default="pi")
args = p.parse_args()

persona_path = pathlib.Path(args.persona).expanduser().resolve()
persona = persona_path.read_text()
rules = (OLD_SIM / "learner_rules.md").read_text()
stamp = dt.datetime.now().strftime("%m%d-%H%M%S")
short_model = args.tutor_model.split("/")[-1]
run_id = f"{stamp}-{persona_path.stem}-{short_model}{('-' + args.tag) if args.tag else ''}"
run = pathlib.Path(args.runs_dir) / run_id
course = run / "cuphoton-learn"
screen = run / "screen"
sessions = run / "tutor-session"
screen.mkdir(parents=True)
sessions.mkdir()
shutil.copytree(args.course, course, ignore=shutil.ignore_patterns(
    ".git", "progress.json", "work", "renders", "feedback-*.jsonl", "__pycache__"))
(run / "cuPhoton").symlink_to(pathlib.Path(args.cuphoton).resolve())

env = dict(os.environ, CUPHOTON_LEARN_RUN_ID=run_id, CUPHOTON_LEARN_MODEL=args.tutor_model,
           PI_CODING_AGENT_DIR=str(REPO / "tutor" / "pi-agent"), PI_OFFLINE="1",
           PI_SKIP_VERSION_CHECK="1", PI_TELEMETRY="0")
cost = 0.0
usage_total = {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "calls": 0}
tool_calls = []
log = []
tutor_session_id = str(uuid.uuid4())
PI = str(REPO / "node_modules" / ".bin" / "pi")


def pi_tutor(msg):
    """One tutor turn under pi. Returns every assistant text block of the turn
    joined (what the learner would see), the turn's cost and its wall time."""
    cmd = [PI, "--model", args.tutor_model, "--mode", "json", "-p",
           "-nc", "-ns", "-ne", "-np", "--no-mcp", "--no-themes",
           "--append-system-prompt", str(course / "AGENTS.md"),
           "--session-dir", str(sessions), "--session-id", tutor_session_id]
    for s in SKILLS:
        cmd += ["--skill", str(course / ".claude" / "skills" / s)]
    if args.thinking:
        cmd += ["--thinking", args.thinking]
    cmd += ["--", msg]
    t0 = time.time()
    for attempt in range(args.retries + 1):
        out = subprocess.run(cmd, cwd=course, env=env, capture_output=True, text=True,
                             timeout=args.call_timeout, stdin=subprocess.DEVNULL)
        texts, c, err = [], 0.0, None
        for line in out.stdout.splitlines():
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("type") == "message_end" and ev["message"].get("role") == "assistant":
                m = ev["message"]
                texts += [b["text"].strip() for b in m.get("content", [])
                          if b.get("type") == "text" and b.get("text", "").strip()]
                for b in m.get("content", []):
                    if b.get("type") == "toolCall":
                        tool_calls.append({"name": b.get("name"), "args": str(b.get("arguments"))[:300]})
                u = m.get("usage") or {}
                c += float((u.get("cost") or {}).get("total") or 0)
                for k in ("input", "output", "cacheRead", "cacheWrite"):
                    usage_total[k] += int(u.get(k) or 0)
                usage_total["calls"] += 1
                if m.get("stopReason") == "error":
                    err = m.get("errorMessage") or "error"
        if out.returncode == 0 and texts and not err:
            return "\n\n".join(texts), c, time.time() - t0
        if attempt < args.retries:
            time.sleep(20 * (attempt + 1))
            # resume the same session: the failed turn's user message is already in it
            msg = "(continue)" if texts or err else msg
            cmd[-1] = msg
            continue
        raise RuntimeError(f"pi exited {out.returncode}: {err or out.stderr[-2000:]}")


def claude_learner(msg, session):
    extra = ["--allowedTools", "Read",
             "--append-system-prompt", rules + "\n\n# Your persona\n\n" + persona,
             "--disallowedTools", "Bash,Edit,Write,MultiEdit,NotebookEdit,WebFetch,WebSearch,Task"]
    cmd = ["claude", "-p", msg, "--model", args.learner_model, "--output-format", "stream-json",
           "--verbose", "--strict-mcp-config", *extra]
    if session:
        cmd += ["--resume", session]
    t0 = time.time()
    out = subprocess.run(cmd, cwd=screen, env=env, capture_output=True, text=True,
                         timeout=args.call_timeout, stdin=subprocess.DEVNULL)
    if out.returncode != 0:
        raise RuntimeError(f"claude exited {out.returncode}: {out.stderr[-2000:]}")
    result = {}
    for line in out.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "result":
            result = ev
    return result.get("result", ""), result.get("session_id"), float(result.get("total_cost_usd") or 0), time.time() - t0


seen = {}


def new_visuals():
    """Copy images the tutor created or changed into the learner's screen dir."""
    shown = []
    for f in course.rglob("*"):
        if f.is_file() and IMG.search(f.name) and "media" not in f.parts and ".claude" not in f.parts:
            m = f.stat().st_mtime
            if seen.get(f) != m:
                seen[f] = m
                dest = screen / f.name
                shutil.copy2(f, dest)
                shown.append(str(dest))
    return shown


new_visuals()  # baseline: course-shipped images are not the tutor's

end_reason = "max_turns"
learner_sid = None
learner_cost = 0.0
t_start = time.time()
try:
    tutor_msg, c, secs = pi_tutor("Begin")
    cost += c
    log.append(("tutor", tutor_msg, secs))
    for turn in range(args.max_turns):
        shown = new_visuals()
        screen_note = ("\n\n[On your screen now: " + ", ".join(shown) + " (open with Read if you look at them)]") if shown else ""
        minutes = sum(x[2] for x in log if x[0] == "tutor") / 60 + 2 * sum(1 for x in log if x[0] == "learner")
        clock_note = f"\n\n[Session clock: {minutes:.0f} min elapsed]"
        learner_msg, learner_sid, c, secs = claude_learner(
            f"The tutor says:\n\n{tutor_msg}{screen_note}{clock_note}", learner_sid)
        cost += c
        learner_cost += c
        ended = "[END]" in learner_msg
        learner_msg = learner_msg.replace("[END]", "").strip()
        log.append(("learner", learner_msg, secs))
        if ended:
            end_reason = "learner_ended"
            break
        if cost > args.max_cost:
            end_reason = "max_cost"
            break
        tutor_msg, c, secs = pi_tutor(learner_msg)
        cost += c
        log.append(("tutor", tutor_msg, secs))
        if cost > args.max_cost:
            end_reason = "max_cost"
            break
except Exception as e:  # keep whatever transcript we have
    end_reason = f"error: {e}"

with (run / "transcript.md").open("w") as f:
    f.write(f"# {run_id}\n\npersona: {persona_path.name} · tutor: {args.tutor_model} (pi) · learner: {args.learner_model}\n\n")
    for i, (who, text, secs) in enumerate(log):
        f.write(f"## [{i}] {who.upper()}  ({secs:.0f}s)\n\n{text}\n\n")
(run / "tool-calls.jsonl").write_text("".join(json.dumps(t) + "\n" for t in tool_calls))
meta = {"run_id": run_id, "persona": persona_path.name, "tutor_model": args.tutor_model,
        "learner_model": args.learner_model, "harness": "pi", "messages": len(log), "end_reason": end_reason,
        "cost_usd": round(cost, 3), "tutor_cost_usd_list_price": round(cost - learner_cost, 3),
        "learner_cost_usd": round(learner_cost, 3), "tutor_usage": usage_total,
        "tutor_tool_calls": len(tool_calls), "wall_s": round(time.time() - t_start),
        "tutor_session": tutor_session_id, "learner_session": learner_sid}
(run / "meta.json").write_text(json.dumps(meta, indent=2))
print(json.dumps(meta))
