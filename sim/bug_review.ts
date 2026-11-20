// Look for bugs in a sim run, one module at a time: the app, the course content, the tutor's handling of
// the page, and the environment the lessons run in. Not a tutoring grade (that's sim/grade.ts).
//   npx tsx sim/bug_review.ts runs/<id> [--grader aws/anthropic/bedrock-claude-opus-5-5] [--course <modules dir as of the run>]
// Writes runs/<id>/bugs.json and bugs.md (bugs-<grader>.* for any grader but the default).
import fs from "node:fs";
import path from "node:path";
import { chat, firstJson } from "./llm.ts";
import { brand, product } from "./course_names.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const run = path.resolve(process.argv[2]);
const gi = process.argv.indexOf("--grader");
const DEFAULT_GRADER = "aws/anthropic/bedrock-claude-opus-5-5";
const grader = gi > 0 ? process.argv[gi + 1] : DEFAULT_GRADER;
const ci = process.argv.indexOf("--course");
const suffix = grader === DEFAULT_GRADER ? "" : "-" + grader.split("/").pop();
const read = (f: string) => { try { return fs.readFileSync(f, "utf8"); } catch { return ""; } };
const cut = (s: string, n: number) => (s.length > n ? s.slice(0, n) + "\n…(cut)" : s);

const meta = JSON.parse(read(path.join(run, "meta.json")));
const modOf = (lessonId: string) => lessonId.split(".")[0].padStart(2, "0");

// Transcript, split at "Learner opens lesson X".
const byMod = new Map<string, string[]>();
let cur = "";
for (const block of read(path.join(run, "transcript.md")).split(/\n(?=## \[)/)) {
  const m = block.match(/^## \[\d+\] Learner opens lesson (\d+\.\d+)/) ?? (cur ? null : block.match(/lesson (\d+\.\d+)/));
  if (m) cur = modOf(m[1]);
  if (cur) (byMod.get(cur) ?? byMod.set(cur, []).get(cur)!).push(block);
}
// Tutor log, split at each prompt to the tutor by the lesson it names.
const tutorBy = new Map<string, string[]>();
let tcur = "";
for (const block of read(path.join(run, "tutor-log.md")).split(/\n\n(?=## → tutor)/)) {
  const m = block.match(/^## → tutor[^\n]*\n[^\n]*?(?:lesson |your-turn |margin, lesson )(\d+\.\d+)/);
  if (m) tcur = modOf(m[1]);
  if (tcur) (tutorBy.get(tcur) ?? tutorBy.set(tcur, []).get(tcur)!).push(block);
}
const signals = read(path.join(run, "signals.jsonl")).split("\n").filter(Boolean).map((l) => JSON.parse(l));

const prompt = (mod: string, dir: string) => {
  const lessons = fs.readdirSync(dir).filter((d) => /^\d+\.\d+-/.test(d)).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  const lessonText = lessons.map((d) => `<lesson dir="${d}">\n<lesson.md>\n${read(path.join(dir, d, "lesson.md"))}\n</lesson.md>\n<tutor.md>\n${read(path.join(dir, d, "tutor.md"))}\n</tutor.md>\n</lesson>`).join("\n");
  const sig = signals.filter((s) => (s.lesson && modOf(s.lesson) === mod) || (!s.lesson && s.kind !== "server_log"));
  return [
    `You are reviewing one module (${mod}) of a simulated run through an interactive course (${brand}). A simulated learner`,
    `used the real web app; an AI tutor (${meta.tutor_model ?? "unknown model"}) taught through page tools (ask, settle, reveal, show_figure) and ran real`,
    "code. Your job is to FIND BUGS, not to grade teaching. A bug is anything a course author should fix:",
    "- app: the page or server misbehaved (no reply, duplicated or misplaced messages, a slot never filled, the closing not shown,",
    "  status stuck, errors, very slow responses, a side question that went nowhere);",
    "- content: the lesson text, a figure spec, a video, or tutor.md is wrong, contradicts itself or the data, refers to something",
    "  that doesn't exist, asks a question the page can't support, or leaves the learner unable to answer;",
    "- tutor: the tutor broke a rule in its notes in a way the notes or SYSTEM.md should prevent (leaking an answer, settling",
    `  without the idea, wrong claims about ${product} or the physics, figures that don't match their caption);`,
    "- environment: code failed because of the machine (missing package, GPU, download, path, permissions, timing);",
    "- harness: the simulation itself caused it (the learner acted oddly); list these separately so they aren't mistaken for bugs.",
    "Be concrete: quote the step number or the tool call. Don't report style preferences. If the module ran cleanly, say so.",
    "",
    "<signals note=\"automatic checks: silent = the tutor posted nothing after the learner acted; slots_empty_on_leave and",
    "turns_open_on_leave = state when the learner moved on; admin_error = errors the server logged\">",
    cut(sig.map((s) => JSON.stringify(s)).join("\n"), 20000), "</signals>",
    "<lessons>", lessonText, "</lessons>",
    "<transcript note=\"what the learner saw and did\">", cut((byMod.get(mod) ?? []).join("\n"), 250000), "</transcript>",
    "<tutor-log note=\"the tutor's side: prompts it got, tool calls, results\">", cut((tutorBy.get(mod) ?? []).join("\n\n"), 250000), "</tutor-log>",
    'Return JSON only: {"bugs": [{"severity": "high|medium|low", "kind": "app|content|tutor|environment|harness", "lesson": "x.y",',
    '"what": "one sentence", "evidence": "step numbers / tool calls", "fix": "file and concrete change"}], "clean": true|false, "note": "one or two sentences"}',
  ].join("\n");
};

const out: any[] = [];
// The course as it was when the run started (the files may have been fixed since).
const modsDir = ci > 0 ? path.resolve(process.argv[ci + 1]) : path.join(ROOT, "course", "modules");
for (const d of fs.readdirSync(modsDir).sort()) {
  const mod = d.slice(0, 2);
  if (!byMod.has(mod)) continue;
  process.stdout.write(`module ${mod}… `);
  try {
    const r = firstJson(await chat(grader, [{ role: "user", content: prompt(mod, path.join(modsDir, d)) }], { maxTokens: 16000 }));
    out.push({ module: mod, ...r });
    console.log(`${r.bugs?.length ?? 0} found`);
  } catch (e: any) { console.log(`failed: ${e.message}`); out.push({ module: mod, error: e.message }); }
}
fs.writeFileSync(path.join(run, `bugs${suffix}.json`), JSON.stringify(out, null, 2));
const sev = { high: 0, medium: 1, low: 2 } as Record<string, number>;
const md = [`# Bugs: ${meta.run_id} (grader ${grader})`, "", `${meta.steps} steps, ${meta.lessons_visited}/${meta.lessons_total} lessons, ${meta.turns_settled}/${meta.turns_total} boxes settled, end: ${meta.end_reason}`, ""];
for (const m of out) {
  md.push(`## Module ${m.module}${m.clean ? " (clean)" : ""}`, "", m.note ?? m.error ?? "", "");
  for (const b of (m.bugs ?? []).sort((a: any, b: any) => (sev[a.severity] ?? 3) - (sev[b.severity] ?? 3)))
    md.push(`- **${b.severity} · ${b.kind} · ${b.lesson}**: ${b.what}  \n  _evidence:_ ${b.evidence}  \n  _fix:_ ${b.fix}`);
  md.push("");
}
fs.writeFileSync(path.join(run, `bugs${suffix}.md`), md.join("\n"));
