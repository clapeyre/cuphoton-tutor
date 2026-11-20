// Live progress of running sims, redrawn every few seconds. Leave it open in a terminal pane:
//   npm run sims                    (sims running now, and those finished today)
//   npx tsx sim/watch.ts --once     (print once and exit)
// Reads only files the sims write: runs/<id>/transcript.md, learner/page.json and, once done, meta.json.
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const RUNS = path.join(ROOT, "runs");
const MODS = path.join(ROOT, "course", "modules");
const once = process.argv.includes("--once");
const EVERY_S = 5;

// Lessons and their Your-turn questions, per module, from the course folder.
type Lesson = { id: string; questions: number };
const course = new Map<string, Lesson[]>();
for (const m of fs.readdirSync(MODS).filter((d) => /^\d\d-/.test(d)).sort()) {
  const lessons = fs.readdirSync(path.join(MODS, m)).filter((d) => /^\d+\.\d+-/.test(d)).sort((a, b) => parseFloat(a) - parseFloat(b))
    .map((d) => {
      const f = path.join(MODS, m, d, "lesson.md");
      const q = fs.existsSync(f) ? (fs.readFileSync(f, "utf8").match(/^:::your-turn\b/gm) ?? []).length : 0;
      return { id: d.split("-")[0], questions: q };
    });
  course.set(m.slice(0, 2), lessons);
}

const readJson = (f: string) => { try { return JSON.parse(fs.readFileSync(f, "utf8")); } catch { return null; } };
const mmss = (s: number) => s >= 3600 ? `${Math.floor(s / 3600)}h${String(Math.floor((s % 3600) / 60)).padStart(2, "0")}` : `${Math.floor(s / 60)}m${String(Math.floor(s % 60)).padStart(2, "0")}`;
const bar = (f: number, w: number) => { const n = Math.round(Math.max(0, Math.min(1, f)) * w); return "█".repeat(n) + "░".repeat(w - n); };
const c = { dim: "\x1b[2m", bold: "\x1b[1m", green: "\x1b[32m", yellow: "\x1b[33m", red: "\x1b[31m", cyan: "\x1b[36m", off: "\x1b[0m" };

function started(id: string): number {
  // Run ids start MMDD-HHMM in UTC (app_sim stamps them with toISOString).
  const m = id.match(/^(\d\d)(\d\d)-(\d\d)(\d\d)/);
  if (!m) return Date.now();
  return Date.UTC(new Date().getUTCFullYear(), +m[1] - 1, +m[2], +m[3], +m[4]);
}

type Info = { id: string; tutor: string; mods: string[]; done: number; lessons: number; qDone: number; qTotal: number; steps: number; elapsed: number; idle: number; cur: string; meta: any; metaAt: number };

function info(id: string, now: number): Info | null {
  const dir = path.join(RUNS, id);
  const tr = path.join(dir, "transcript.md");
  if (!fs.existsSync(tr)) return null;
  const meta = readJson(path.join(dir, "meta.json"));
  const metaAt = meta ? fs.statSync(path.join(dir, "meta.json")).mtimeMs : 0;
  const lastWrite = fs.statSync(tr).mtimeMs;
  const text = fs.readFileSync(tr, "utf8");
  const mods = (text.slice(0, 600).match(/modules ([\d, ]+)/)?.[1] ?? "").split(",").map((s) => s.trim()).filter(Boolean);
  const lessons = mods.flatMap((m) => course.get(m) ?? []);
  const page = readJson(path.join(dir, "learner", "page.json")) ?? { lessons: {} };
  return {
    id, meta, metaAt, mods, cur: page.current ?? "—",
    tutor: id.replace(/^\d{4}-\d{4}-/, "").replace(/^(t1-thorough|s4-[a-z-]+?)-/, ""),
    done: lessons.filter((l) => page.lessons[l.id]?.revealed).length, lessons: lessons.length,
    qTotal: lessons.reduce((a, l) => a + l.questions, 0),
    qDone: lessons.reduce((a, l) => a + Object.values<any>(page.lessons[l.id]?.turns ?? {}).filter((t) => t.status === "settled").length, 0),
    steps: (text.match(/^## \[\d+\]/gm) ?? []).length,
    elapsed: ((meta ? metaAt : now) - started(id)) / 1000, idle: (now - lastWrite) / 1000,
  };
}

/** Why a finished run didn't complete everything, from its results. */
function why(r: Info): string {
  const e = String(r.meta?.end_reason ?? "");
  if (e === "stopped_by_operator") return "stopped by the operator";
  if (e.startsWith("error")) {
    const http = e.match(/HTTP (\d{3})/)?.[1];
    return http ? `sim error: the learner model's API refused a request (HTTP ${http})` : "sim error: " + e.replace(/^error:\s*/, "").slice(0, 50);
  }
  if (e === "max_steps") return "ran out of steps";
  if (r.qDone === r.qTotal) return "every question answered, a closing never shown";
  return e.replace(/_/g, " ");
}

const hhmm = (t: number) => new Date(t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

/** The --tag of every app_sim process alive on this machine (a run id ends with "-<tag>"). */
function liveTags(): Set<string> {
  const tags = new Set<string>();
  for (const pid of fs.readdirSync("/proc").filter((d) => /^\d+$/.test(d))) {
    try {
      const argv = fs.readFileSync(`/proc/${pid}/cmdline`, "utf8").split("\0");
      if (!argv.some((a) => a.endsWith("app_sim.ts"))) continue;
      const i = argv.indexOf("--tag");
      if (i >= 0 && argv[i + 1]) tags.add(argv[i + 1]);
    } catch {}
  }
  return tags;
}

function render(): string {
  const now = Date.now();
  const today = new Date().toDateString();
  const lines: string[] = [`${c.bold}cuPhoton sims${c.off}  ${c.dim}${new Date().toLocaleTimeString()} · every ${EVERY_S}s · ctrl-c to quit${c.off}`, ""];
  const ids = fs.existsSync(RUNS) ? fs.readdirSync(RUNS).filter((d) => /^\d{4}-\d{4}-/.test(d)).sort() : [];
  const all = ids.map((id) => info(id, now)).filter((x): x is Info => !!x);
  // A run without results is running only if its sim process is alive; otherwise it was stopped (killed) without results.
  const alive = liveTags();
  const isAlive = (r: Info) => [...alive].some((t) => r.id.endsWith("-" + t));
  const running = all.filter((r) => !r.meta && isAlive(r));
  const stopped = all.filter((r) => !r.meta && !isAlive(r) && new Date(now - r.idle * 1000).toDateString() === today);
  const finished = all.filter((r) => r.meta && new Date(r.metaAt).toDateString() === today).sort((a, b) => b.metaAt - a.metaAt);

  lines.push(`${c.bold}Running${c.off}`, "");
  for (const r of running) {
    const frac = r.qTotal ? r.qDone / r.qTotal : r.lessons ? r.done / r.lessons : 0;
    const status = r.idle > 600 ? `${c.red}quiet ${mmss(r.idle)}${c.off}` : r.idle > 180 ? `${c.yellow}quiet ${mmss(r.idle)}${c.off}` : `${c.cyan}in ${r.cur}${c.off}`;
    const eta = frac > 0.05 ? `  ~${mmss(r.elapsed * (1 - frac) / frac)} left` : "";
    lines.push(`${c.bold}${r.tutor}${c.off}  ${c.dim}modules ${r.mods.join(",")} · started ${hhmm(started(r.id))}${c.off}`);
    lines.push(`  ${bar(frac, 32)} ${String(Math.round(frac * 100)).padStart(3)}%   lessons ${r.done}/${r.lessons} · questions ${r.qDone}/${r.qTotal}`);
    lines.push(`  ${status}  ${c.dim}· step ${r.steps} · ${mmss(r.elapsed)} elapsed${eta}${c.off}`, "");
  }
  if (!running.length) lines.push(`${c.dim}  No sim running.${c.off}`, "");

  lines.push(`${c.bold}Finished today${c.off}`);
  for (const r of finished) {
    const dir = path.join(RUNS, r.id);
    const rev = [fs.existsSync(path.join(dir, "bugs.json")) && "Opus", fs.existsSync(path.join(dir, "bugs-gpt-6.2-astra.json")) && "Astra"].filter(Boolean);
    const complete = r.done === r.lessons && r.qDone === r.qTotal;
    const at = new Date(r.metaAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    lines.push(`  ${c.dim}${at}${c.off}  ${complete ? c.green + "✓" : c.yellow + "…"}${c.off} ${r.tutor.padEnd(34)} ${c.dim}${r.mods.join(",").padEnd(15)}${c.off}` +
      ` lessons ${r.done}/${r.lessons} · questions ${r.qDone}/${r.qTotal} · ${mmss(r.elapsed)}` +
      (complete ? "" : ` · ${c.yellow}${why(r)}${c.off}`) +
      ` · ${rev.length ? `${c.green}reviewed: ${rev.join(" + ")}${c.off}` : `${c.yellow}not reviewed yet${c.off}`}`);
  }
  for (const r of stopped)
    lines.push(`  ${c.dim}${hhmm(now - r.idle * 1000)}${c.off}  ${c.red}✗${c.off} ${r.tutor.padEnd(34)} ${c.dim}${r.mods.join(",").padEnd(15)}${c.off}` +
      ` lessons ${r.done}/${r.lessons} · questions ${r.qDone}/${r.qTotal} · ${c.red}stopped without results${c.off}`);
  if (!finished.length && !stopped.length) lines.push(`${c.dim}  None yet.${c.off}`);
  return lines.join("\n");
}

if (once) console.log(render());
else {
  const draw = () => process.stdout.write("\x1b[H\x1b[2J" + render() + "\n");
  draw();
  setInterval(draw, EVERY_S * 1000);
}
