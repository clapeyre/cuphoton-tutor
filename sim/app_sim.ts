// A simulated learner takes the course in the real app: its own server (own port, own learner folder), the
// tutor model under test inside it, and a persona played by another model that reads the page and acts on it
// the way the browser does (open a lesson, answer in a Your-turn box, ask a side question, move on, stop).
//
//   npx tsx sim/app_sim.ts --persona sim/personas/p1-newcomer.md --tutor nvidia/nvidia/nemotron-3.5-super-vl \
//       --modules 00,01 --port 8811
//
// Writes runs/<id>/: transcript.md (what the learner saw and did), tutor-log.md (the tutor's side: prompts,
// tool calls, results), meta.json, admin.json (the admin page's report: waits, errors, tokens), learner/.
// Grade with sim/grade.ts.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";
import { chat, firstJson, imagePart, type Msg, type Usage } from "./llm.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const arg = (k: string, d?: string) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : d; };
const personaFile = path.resolve(arg("persona")!);
const tutorModel = arg("tutor", "aws/anthropic/bedrock-claude-sonnet-5-5")!;
const learnerModel = arg("learner", "aws/anthropic/bedrock-claude-haiku-5-5")!;
const modules = arg("modules", "00,01")!.split(",");
const port = Number(arg("port", "8811"));
const maxSteps = Number(arg("max-steps", "45"));
const actionTimeout = Number(arg("action-timeout-min", "15")) * 60_000;
const tag = arg("tag", "");
const historyLimit = Number(arg("history", "80"));

const persona = fs.readFileSync(personaFile, "utf8");
const rules = fs.readFileSync(path.join(ROOT, "sim", "learner_rules.md"), "utf8");
const shortModel = tutorModel.split("/").pop()!.replace(/^bedrock-claude-/, "");
const stamp = new Date().toISOString().slice(5, 16).replace(/[-:T]/g, "").replace(/^(\d{4})/, "$1-");
const runId = `${stamp}-${path.basename(personaFile, ".md")}-${shortModel}${tag ? "-" + tag : ""}`;
const run = path.join(ROOT, "runs", runId);
const learnerDir = path.join(run, "learner");
fs.mkdirSync(learnerDir, { recursive: true });
const out = fs.createWriteStream(path.join(run, "transcript.md"));
const log = (s: string) => out.write(s + "\n\n");
const say = (s: string) => console.log(`[${runId}] ${s}`);

// ---------- the server ----------
const server = spawn(path.join(ROOT, "node_modules", ".bin", "tsx"), ["server/index.ts"], {
  cwd: ROOT, stdio: ["ignore", fs.openSync(path.join(run, "server.log"), "a"), fs.openSync(path.join(run, "server.log"), "a")],
  env: { ...process.env, PORT: String(port), LEARNER_DIR: learnerDir, ACCESS: "open", PING_EVERY_MIN: "0", TUTOR_PROVIDER: "nvidia", TUTOR_MODEL: tutorModel },
});
const stopServer = () => { try { server.kill("SIGTERM"); } catch {} };
process.on("exit", stopServer);
process.on("SIGINT", () => { stopServer(); process.exit(130); });
const base = `http://127.0.0.1:${port}`;
for (let i = 0; ; i++) {
  try { if ((await fetch(`${base}/api/course`)).ok) break; } catch {}
  if (i > 120 || server.exitCode !== null) throw new Error(`server didn't start (see ${run}/server.log)`);
  await new Promise((r) => setTimeout(r, 500));
}
const course: any = await (await fetch(`${base}/api/course`)).json();
const lessonIds: string[] = course.modules.filter((m: any) => modules.includes(m.id)).flatMap((m: any) => m.lessons.map((l: any) => l.id));
const lessons = new Map<string, any>();
for (const id of lessonIds) lessons.set(id, await (await fetch(`${base}/api/lesson/${encodeURIComponent(id)}`)).json());

// ---------- the page, over the WebSocket the browser uses ----------
let state: any = null;
const ws = new WebSocket(`ws://127.0.0.1:${port}/ws`);
ws.on("message", (raw) => { const m = JSON.parse(String(raw)); if (m.type === "state") state = m; });
await new Promise<void>((res, rej) => { ws.on("open", () => res()); ws.on("error", rej); });
while (!state) await new Promise((r) => setTimeout(r, 100));
const send = (m: unknown) => ws.send(JSON.stringify(m));
const busy = () => !!(state.activity.main || Object.keys(state.activity.threads).length);

/** After a learner action: wait for the tutor to start (if it does) and then to be idle for 3 s. */
async function settle(): Promise<number> {
  const t0 = Date.now();
  while (!busy() && Date.now() - t0 < 6000) await new Promise((r) => setTimeout(r, 200));
  let idleSince = busy() ? 0 : Date.now();
  while (Date.now() - t0 < actionTimeout) {
    await new Promise((r) => setTimeout(r, 300));
    if (busy()) idleSince = 0; else if (!idleSince) idleSince = Date.now(); else if (Date.now() - idleSince > 3000) break;
  }
  return (Date.now() - t0) / 1000;
}

// ---------- what the learner sees ----------
const strip = (s: string) => s.replace(/\[\[([^\]|]*)\|?([^\]]*)\]\]/g, (_m, t, shown) => shown || t.replace(/^@/, ""));
function srt(src: string) {
  const f = path.join(ROOT, "media", "videos", path.basename(src).replace(/\.mp4$/, ".srt"));
  if (!fs.existsSync(f)) return "";
  return fs.readFileSync(f, "utf8").split(/\r?\n/).filter((l) => l.trim() && !/^\d+$/.test(l.trim()) && !/-->/.test(l)).join(" ");
}
function fileFor(src: string): string | null {
  const u = src.split("?")[0];
  if (u.startsWith("/workspace/")) return path.join(learnerDir, decodeURIComponent(u.slice("/workspace/".length)));
  if (u.startsWith("/course-files/")) return path.join(ROOT, "course", decodeURIComponent(u.slice("/course-files/".length)));
  if (u.startsWith("/media/")) return path.join(ROOT, "media", decodeURIComponent(u.slice("/media/".length)));
  return null;
}
type Seen = { turnLog: Record<string, number>; status: Record<string, string>; slots: Record<string, string>; revealed: boolean; thread: Record<string, number> };
const seen = new Map<string, Seen>();
const images: string[] = []; // files to attach to the next learner message

function figureLine(f: any, made: boolean) {
  const file = fileFor(f.src);
  if (file && fs.existsSync(file) && /\.(png|jpe?g|gif|webp)$/i.test(file)) images.push(file);
  return `[Figure${made ? ", made by the tutor" : ""}: ${f.title ?? ""}${f.caption ? ` (caption: ${strip(f.caption)})` : ""}${file && images.at(-1) === file ? " (image attached)" : ""}]`;
}

function lessonPage(l: any): string {
  const st = state.page.lessons[l.id] ?? { turns: {}, slots: {}, revealed: false };
  const out: string[] = [`# Lesson ${l.id}: ${l.title}`, `Question: ${strip(l.question ?? "")}`];
  if (l.intro?.length) out.push(...l.intro.map(strip));
  for (const p of l.parts) {
    if (p.kind === "prose") out.push(strip(p.text));
    else if (p.kind === "code") out.push("```\n" + p.text + "\n```");
    else if (p.kind === "video") out.push(`[Video: "${p.title}" (${p.duration}). What it says: ${srt(p.src) || "(no transcript)"}]`);
    else if (p.kind === "figure") out.push(figureLine(p, false));
    else if (p.kind === "slot") out.push(st.slots[p.id] ? figureLine(st.slots[p.id], true) : `[A figure will appear here: ${p.title}]`);
    else if (p.kind === "chain") out.push(`[Diagram of the chain of stages: ${course.chain.map((c: any) => c.id === p.hi ? `**${c.id}** (${c.does})` : `${c.id} (${c.does})`).join(" → ")}. ${strip(p.caption ?? "")}]`);
    else if (p.kind === "ref") out.push(`[Reference: ${p.label}: ${strip(p.text ?? "")}]`);
    else if (p.kind === "turn") {
      const t = st.turns[p.id];
      // As on the page: a turn waits, prompt hidden, while an earlier one in the lesson is open.
      const before = l.parts.filter((q: any) => q.kind === "turn").map((q: any) => q.id);
      if (t?.status !== "settled" && before.slice(0, before.indexOf(p.id)).some((id: string) => st.turns[id]?.status !== "settled")) {
        out.push(`## Your turn (turn id "${p.id}"): ${p.title}\n(Opens once you've finished the one above)`);
        continue;
      }
      out.push(`## Your turn (turn id "${p.id}"): ${p.title}\n${p.lead ? strip(p.lead) + " " : ""}${strip(p.prompt ?? "")}` +
        (p.image ? `\n${figureLine({ src: p.image, title: "", caption: p.imageCaption }, false)}` : "") +
        (t?.log?.length ? "\n" + t.log.map((m: any) => `> ${m.who === "tutor" ? "Tutor" : "You"}: ${m.text}${m.figure ? "\n> " + figureLine(m.figure, true) : ""}`).join("\n") : "") +
        (t?.status === "settled" ? `\n✓ Closed: ${t.summary ?? ""}` : "\n(open)"));
    }
  }
  if (st.revealed && l.closure) out.push(`## We found\n${strip(l.closure.found)}${st.yourRun ? `\nIn your run: ${st.yourRun}` : ""}${l.closure.matters ? "\n" + strip(l.closure.matters) : ""}\n## Which raises\n${strip(l.closure.raises)}`);
  return out.join("\n\n");
}

/** What changed on the current lesson since the learner last looked. */
function changes(l: any): string {
  const st = state.page.lessons[l.id] ?? { turns: {}, slots: {}, revealed: false };
  const s = seen.get(l.id)!;
  const out: string[] = [];
  for (const p of l.parts) {
    if (p.kind === "slot" && st.slots[p.id] && s.slots[p.id] !== st.slots[p.id].src) { s.slots[p.id] = st.slots[p.id].src; out.push(`A figure appeared in the lesson: ${figureLine(st.slots[p.id], true)}`); }
    if (p.kind !== "turn") continue;
    const t = st.turns[p.id];
    if (!t) continue;
    const n = s.turnLog[p.id] ?? 0;
    for (const m of t.log.slice(n)) if (m.who === "tutor") out.push(`In Your turn "${p.id}", the tutor: ${m.text}${m.figure ? "\n" + figureLine(m.figure, true) : ""}`);
    s.turnLog[p.id] = t.log.length;
    if (t.status !== s.status[p.id] && t.status === "settled") out.push(`Your turn "${p.id}" closed with a check mark: ${t.summary ?? ""}`);
    s.status[p.id] = t.status;
  }
  for (const th of state.page.threads.filter((x: any) => x.from === l.id)) {
    const n = s.thread[th.id] ?? 0;
    for (const m of th.messages.slice(n)) if (m.who === "tutor") out.push(`In the margin, the tutor answers your side question: ${m.text}`);
    s.thread[th.id] = th.messages.length;
  }
  if (st.revealed && !s.revealed && l.closure) { s.revealed = true; out.push(`The lesson's closing appeared.\nWe found: ${strip(l.closure.found)}${st.yourRun ? `\nIn your run: ${st.yourRun}` : ""}${l.closure.matters ? `\nWhy it matters: ${strip(l.closure.matters)}` : ""}\nWhich raises: ${strip(l.closure.raises)}`); }
  return out.join("\n\n");
}
function markAllSeen(l: any) {
  const st = state.page.lessons[l.id] ?? { turns: {}, slots: {}, revealed: false };
  const s: Seen = { turnLog: {}, status: {}, slots: {}, revealed: !!st.revealed, thread: {} };
  for (const [id, t] of Object.entries<any>(st.turns)) { s.turnLog[id] = t.log.length; s.status[id] = t.status; }
  for (const [id, f] of Object.entries<any>(st.slots)) s.slots[id] = f.src;
  for (const th of state.page.threads) s.thread[th.id] = th.messages.length;
  seen.set(l.id, s);
}

// ---------- bug signals: things that look wrong whatever the tutoring quality ----------
const signalsFile = fs.createWriteStream(path.join(run, "signals.jsonl"));
const signal = (kind: string, detail: unknown) => { signalsFile.write(JSON.stringify({ t: Date.now(), step: steps, lesson: current, kind, detail }) + "\n"); };
function leaving(id: string) {
  const l = lessons.get(id), st = state.page.lessons[id] ?? { turns: {}, slots: {} };
  const empty = l.parts.filter((p: any) => p.kind === "slot" && !st.slots[p.id]).map((p: any) => p.id);
  const open = l.parts.filter((p: any) => p.kind === "turn" && st.turns[p.id]?.status !== "settled").map((p: any) => p.id);
  if (empty.length) signal("slots_empty_on_leave", empty);
  if (open.length) signal("turns_open_on_leave", open);
  if (l.closure && !st.revealed && !open.length) signal("closure_not_revealed", "every box settled but the closing never showed");
}
function checkTurns(id: string) {
  const st = state.page.lessons[id];
  for (const [tid, t] of Object.entries<any>(st?.turns ?? {})) {
    const tutorTexts = t.log.filter((m: any) => m.who === "tutor").map((m: any) => m.text.trim());
    const dup = tutorTexts.find((x: string, i: number) => x && tutorTexts.indexOf(x) !== i);
    if (dup) signal("duplicate_tutor_message", { turn: tid, text: dup.slice(0, 200) });
  }
}

// ---------- the session ----------
const usage: Usage = { input: 0, output: 0, calls: 0 };
// A subset of modules jumps (1.7 to 4.1): say so, or the learner works the skipped modules in the margin.
const skipped = course.modules.map((m: any) => m.id).filter((id: string) => !modules.includes(id));
const scope = skipped.length ? `\n\n# This session\n\nIt covers modules ${modules.join(", ")} only. Modules ${skipped.join(", ")} are skipped on purpose: when Next jumps past them, carry on; don't ask to do them.` : "";
const history: Msg[] = [{ role: "system", content: `${rules}\n\n# Your persona\n\n${persona}${scope}` }];
let clockS = 0; // simulated minutes: the tutor's real response time plus reading and typing time per step
const waits: number[] = [];
let steps = 0, endReason = "max_steps", current = lessonIds[0], openThread: string | null = null;
const t0 = Date.now();
log(`# ${runId}\n\npersona: ${path.basename(personaFile)} · modules ${modules.join(", ")} · learner: ${learnerModel}`);

function open(id: string) {
  current = id;
  send({ type: "open", lesson: id });
}
async function learnerTurn(text: string) {
  const parts: any[] = [{ type: "text", text }];
  for (const f of images.splice(0)) parts.push(imagePart(f));
  history.push({ role: "user", content: parts.length > 1 ? parts : text });
  // keep images only in the latest message: older screenshots are history the learner has already seen
  // A whole-course run is hundreds of steps: keep the persona and the most recent exchanges.
  if (history.length > historyLimit) { let cut = history.length - historyLimit; while (history[cut]?.role !== "user") cut++; history.splice(1, cut - 1, { role: "user", content: "(Earlier lessons: done; you remember them in outline.)" }, { role: "assistant", content: '{"action":"next"}' }); }
  for (const m of history.slice(1, -1)) if (Array.isArray(m.content)) m.content = m.content.filter((p) => p.type === "text").map((p: any) => p.text).join("\n");
  for (let i = 0; i < 3; i++) {
    const reply = await chat(learnerModel, history, { usage, maxTokens: 800 });
    try {
      const a = firstJson(reply);
      if (!["say", "side", "next", "end"].includes(a.action)) throw new Error("unknown action");
      history.push({ role: "assistant", content: JSON.stringify(a) });
      return a;
    } catch (e: any) {
      history.push({ role: "assistant", content: reply }, { role: "user", content: `That wasn't one JSON action (${e.message}). Reply with exactly one JSON object.` });
    }
  }
  throw new Error("learner gave no valid action");
}

try {
  open(current);
  waits.push(await settle());
  markAllSeen({ id: current });
  let view = lessonPage(lessons.get(current));
  log(`## [0] Learner opens lesson ${current}\n\n<details><summary>page as shown</summary>\n\n${view}\n\n</details>`);
  while (steps < maxSteps) {
    steps++;
    clockS += waits.at(-1)! + 90;
    const l = lessons.get(current);
    const ts = state.page.lessons[current]?.turns ?? {};
    let first = true; // the first unsettled turn is open; later ones wait, as on the page
    const turns = l.parts.filter((p: any) => p.kind === "turn").map((p: any) => {
      if (ts[p.id]?.status === "settled") return `${p.id} (closed)`;
      const w = first ? "open" : "waits for the one above"; first = false; return `${p.id} (${w})`;
    });
    const msg = `${view}\n\n[Lesson ${current}. Your turns here: ${turns.join(", ") || "none"}.${lessonIds.indexOf(current) === lessonIds.length - 1 ? " This is the last lesson of the session." : ""}]\n[Session clock: ${Math.round(clockS / 60)} min elapsed]`;
    const a = await learnerTurn(msg);
    if (a.action !== "side" && openThread) { send({ type: "thread.close", id: openThread }); openThread = null; }
    if (a.action === "end") { log(`## [${steps}] Learner ends\n\n${a.text ?? ""}`); endReason = "learner_ended"; break; }
    if (a.action === "next") {
      leaving(current); checkTurns(current);
      const i = lessonIds.indexOf(current);
      if (i === lessonIds.length - 1) { log(`## [${steps}] Learner moves on past the last lesson`); endReason = "finished"; break; }
      open(lessonIds[i + 1]);
      waits.push(await settle());
      markAllSeen({ id: current });
      view = lessonPage(lessons.get(current));
      log(`## [${steps}] Learner opens lesson ${current} (${waits.at(-1)!.toFixed(0)} s)\n\n<details><summary>page as shown</summary>\n\n${view}\n\n</details>`);
      continue;
    }
    if (a.action === "say") {
      const st = state.page.lessons[current]?.turns[a.turn];
      if (!l.parts.some((p: any) => p.kind === "turn" && p.id === a.turn) || st?.status === "settled") {
        view = `(Nothing happened: there's no open Your-turn box "${a.turn}" in this lesson.)`;
        signal("learner_bad_box", a.turn);
        log(`## [${steps}] Learner tries to answer in "${a.turn}" (no such open box)\n\n${a.text}`);
        waits.push(0);
        continue;
      }
      send({ type: "say", lesson: current, turn: a.turn, text: String(a.text ?? "") });
      log(`## [${steps}] Learner, in Your turn "${a.turn}"\n\n${a.text}`);
    } else {
      const th = openThread ? state.page.threads.find((x: any) => x.id === openThread) : null;
      if (th) send({ type: "thread.ask", id: th.id, question: a.text });
      else {
        const before = new Set(state.page.threads.map((x: any) => x.id));
        send({ type: "thread.new", from: current, question: a.text });
        for (let i = 0; i < 50 && !openThread; i++) { await new Promise((r) => setTimeout(r, 100)); openThread = state.page.threads.find((x: any) => !before.has(x.id))?.id ?? null; }
      }
      log(`## [${steps}] Learner, side question\n\n${a.text}`);
    }
    waits.push(await settle());
    view = changes(l) || "(Nothing new on the page.)";
    const w = waits.at(-1)!;
    if (view === "(Nothing new on the page.)") signal("silent", { action: a.action, turn: a.turn, wait_s: w });
    if (/lost my train of thought|couldn't reach the model/.test(view)) signal("fallback_reply", view.slice(0, 200));
    if (w * 1000 >= actionTimeout) signal("timeout", { wait_s: w });
    else if (w > 120) signal("slow", { wait_s: Math.round(w) });
    log(`### Tutor (${waits.at(-1)!.toFixed(0)} s)\n\n${view}`);
    if (waits.at(-1)! * 1000 >= actionTimeout) log("_(the tutor was still working when the action timed out)_");
  }
} catch (e: any) {
  endReason = `error: ${e.message}`;
  say(endReason);
}

// ---------- results ----------
if (endReason !== "learner_ended" && endReason !== "finished") { leaving(current); checkTurns(current); }
const admin: any = await (await fetch(`${base}/api/admin`)).json().catch(() => ({}));
for (const line of fs.readFileSync(path.join(run, "server.log"), "utf8").split("\n"))
  if (/\[(tutor|ws|margin|content)\]|Error|failed|Traceback|warn/i.test(line)) signal("server_log", line.slice(0, 300));
for (const e of admin.errors ?? []) if (!/Request (was )?aborted/.test(e.message)) signalsFile.write(JSON.stringify({ t: e.t, kind: "admin_error", detail: `${e.where}: ${String(e.message).slice(0, 300)}` }) + "\n");
signalsFile.end();
fs.writeFileSync(path.join(run, "admin.json"), JSON.stringify(admin, null, 1));
ws.close();
stopServer();
out.end();

// The tutor's side, from pi's session logs: what it was told, what it ran, what came back.
const tl: string[] = [];
const sessDir = path.join(learnerDir, "sessions", "main");
for (const f of fs.existsSync(sessDir) ? fs.readdirSync(sessDir).filter((x) => x.endsWith(".jsonl")).sort() : []) {
  tl.push(`# session ${f}`);
  for (const line of fs.readFileSync(path.join(sessDir, f), "utf8").split("\n")) {
    let e: any; try { e = JSON.parse(line); } catch { continue; }
    if (e.type !== "message") continue;
    const m = e.message, c = Array.isArray(m.content) ? m.content : [];
    const ts = String(e.timestamp ?? "").slice(11, 19);
    if (m.role === "user") tl.push(`## → tutor [${ts}]\n${c.filter((b: any) => b.type === "text").map((b: any) => b.text.replace(/<lesson\.md>[\s\S]*?<\/tutor\.md>/, "(lesson.md and tutor.md)")).join("\n").slice(0, 3000)}`);
    if (m.role === "assistant" && m.stopReason === "aborted") { tl.push("(call cancelled: the learner acted while the tutor was preparing a lesson ahead; this is on purpose, not an error)"); continue; }
    if (m.role === "assistant") for (const b of c) {
      if (b.type === "text" && b.text.trim()) tl.push(`tutor says (not on the page unless in a tool): ${b.text.trim().slice(0, 1500)}`);
      if (b.type === "toolCall") tl.push(`tool ${b.name}: ${JSON.stringify(b.arguments).slice(0, 1500)}`);
      if (m.stopReason === "error") tl.push(`ERROR: ${m.errorMessage}`);
    }
    if (m.role === "toolResult") tl.push(`  ↳ ${m.isError ? "ERROR " : ""}${c.filter((b: any) => b.type === "text").map((b: any) => b.text).join(" ").slice(0, 600)}`);
  }
}
fs.writeFileSync(path.join(run, "tutor-log.md"), tl.join("\n\n"));

const page = JSON.parse(fs.readFileSync(path.join(learnerDir, "page.json"), "utf8"));
const turnsIn = lessonIds.flatMap((id) => lessons.get(id).parts.filter((p: any) => p.kind === "turn").map((p: any) => ({ id, turn: p.id })));
const settled = turnsIn.filter((t) => page.lessons[t.id]?.turns[t.turn]?.status === "settled").length;
const lost = Object.values<any>(page.lessons).flatMap((l: any) => Object.values<any>(l.turns)).flatMap((t: any) => t.log).filter((m: any) => /lost my train of thought/.test(m.text)).length;
const sorted = waits.filter((w) => w > 0).sort((a, b) => a - b);
const meta = {
  run_id: runId, persona: path.basename(personaFile), tutor_model: tutorModel, learner_model: learnerModel, modules,
  end_reason: endReason, steps, wall_s: Math.round((Date.now() - t0) / 1000), sim_minutes: Math.round(clockS / 60),
  lessons_visited: lessonIds.filter((id) => page.lessons[id]?.visited).length, lessons_total: lessonIds.length,
  turns_settled: settled, turns_total: turnsIn.length,
  lessons_revealed: lessonIds.filter((id) => page.lessons[id]?.revealed).length,
  lost_train_fallbacks: lost,
  wait_s: { median: sorted[Math.floor(sorted.length / 2)] ?? null, p90: sorted[Math.floor(sorted.length * 0.9)] ?? null, max: sorted.at(-1) ?? null },
  tutor: { calls: admin.totals?.calls, cost_usd_est: admin.totals?.cost,
    // "Request was aborted": preparing the next lesson ahead, cancelled on purpose when the learner acts
    errors: admin.errors?.filter((e: any) => !/Request (was )?aborted/.test(e.message)).length, retries: admin.retries?.length, compactions: admin.compactions?.length,
    tool_calls: admin.tools?.reduce((a: number, t: any) => a + t.n, 0), tool_errors: admin.tools?.reduce((a: number, t: any) => a + t.errors, 0),
    peak_context: Math.max(0, ...(admin.context ?? []).map((c: any) => c[1])) },
  learner_usage: usage,
  feedback_notes: fs.existsSync(path.join(learnerDir, "feedback-queue.jsonl")) ? fs.readFileSync(path.join(learnerDir, "feedback-queue.jsonl"), "utf8").split("\n").filter(Boolean).length : 0,
};
fs.writeFileSync(path.join(run, "meta.json"), JSON.stringify(meta, null, 2));
say(JSON.stringify(meta));
process.exit(0);
