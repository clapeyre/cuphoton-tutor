// Live progress of running sims, redrawn every few seconds. Leave it open in a terminal pane:
//   npx tsx sim/watch.ts            (sims running now, plus those finished in the last 30 min)
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
  // Run ids start MMDD-HHMM (local time).
  const m = id.match(/^(\d\d)(\d\d)-(\d\d)(\d\d)/);
  if (!m) return Date.now();
  const d = new Date(); d.setMonth(+m[1] - 1, +m[2]); d.setHours(+m[3], +m[4], 0, 0);
  return d.getTime();
}

function render(): string {
  const now = Date.now();
  const lines: string[] = [`${c.bold}cuPhoton sims${c.off}  ${c.dim}${new Date().toLocaleTimeString()} · every ${EVERY_S}s · ctrl-c to quit${c.off}`, ""];
  const dirs = fs.existsSync(RUNS) ? fs.readdirSync(RUNS).filter((d) => /^\d{4}-\d{4}-/.test(d)).sort() : [];
  let shown = 0;
  for (const id of dirs) {
    const dir = path.join(RUNS, id);
    const tr = path.join(dir, "transcript.md");
    if (!fs.existsSync(tr)) continue;
    const meta = readJson(path.join(dir, "meta.json"));
    const lastWrite = fs.statSync(tr).mtimeMs;
    if (meta && now - fs.statSync(path.join(dir, "meta.json")).mtimeMs > 30 * 60e3) continue; // finished a while ago
    if (!meta && now - lastWrite > 2 * 3600e3) continue; // abandoned
    const head = fs.readFileSync(tr, "utf8").slice(0, 600);
    const mods = (head.match(/modules ([\d, ]+)/)?.[1] ?? "").split(",").map((s) => s.trim()).filter(Boolean);
    const lessons = mods.flatMap((m) => course.get(m) ?? []);
    const page = readJson(path.join(dir, "learner", "page.json")) ?? { lessons: {} };
    const done = lessons.filter((l) => page.lessons[l.id]?.revealed).length;
    const qTotal = lessons.reduce((a, l) => a + l.questions, 0);
    const qDone = lessons.reduce((a, l) => a + Object.values<any>(page.lessons[l.id]?.turns ?? {}).filter((t) => t.status === "settled").length, 0);
    const steps = (fs.readFileSync(tr, "utf8").match(/^## \[\d+\]/gm) ?? []).length;
    const t0 = started(id);
    const elapsed = ((meta ? fs.statSync(path.join(dir, "meta.json")).mtimeMs : now) - t0) / 1000;
    const frac = qTotal ? qDone / qTotal : lessons.length ? done / lessons.length : 0;
    const idle = (now - lastWrite) / 1000;
    const name = id.replace(/^\d{4}-\d{4}-/, "");
    const tutor = name.replace(/^(t1-thorough|s4-[a-z-]+?)-/, "");
    const cur = page.current ?? "—";
    let status: string;
    if (meta) status = `${c.green}done${c.off} (${meta.end_reason})`;
    else if (idle > 600) status = `${c.red}quiet ${mmss(idle)}${c.off}`;
    else if (idle > 180) status = `${c.yellow}quiet ${mmss(idle)}${c.off}`;
    else status = `${c.cyan}in ${cur}${c.off}`;
    const eta = !meta && frac > 0.05 ? `  ~${mmss(elapsed * (1 - frac) / frac)} left` : "";
    lines.push(`${c.bold}${tutor}${c.off}  ${c.dim}modules ${mods.join(",")} · ${id.slice(0, 9)}${c.off}`);
    lines.push(`  ${bar(frac, 32)} ${String(Math.round(frac * 100)).padStart(3)}%   lessons ${done}/${lessons.length} · questions ${qDone}/${qTotal}`);
    lines.push(`  ${status}  ${c.dim}· step ${steps} · ${mmss(elapsed)} elapsed${eta}${c.off}`);
    lines.push("");
    shown++;
  }
  if (!shown) lines.push(`${c.dim}No sim running (or finished in the last 30 min).${c.off}`);
  return lines.join("\n");
}

if (once) console.log(render());
else {
  const draw = () => process.stdout.write("\x1b[H\x1b[2J" + render() + "\n");
  draw();
  setInterval(draw, EVERY_S * 1000);
}
