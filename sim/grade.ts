// Grade a sim run with sim/rubric.md. The grader doesn't see which model tutored.
//   npx tsx sim/grade.ts runs/<id> [--grader aws/anthropic/bedrock-claude-opus-5-5]
import fs from "node:fs";
import path from "node:path";
import { product } from "./course_names.ts";
import { chat, firstJson } from "./llm.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const run = path.resolve(process.argv[2]);
const gi = process.argv.indexOf("--grader");
const grader = gi > 0 ? process.argv[gi + 1] : "aws/anthropic/bedrock-claude-opus-5-5";
const read = (f: string, max = 400_000) => { try { const s = fs.readFileSync(f, "utf8"); return s.length > max ? s.slice(0, max) + "\n…(cut)" : s; } catch { return "(none)"; } };

const meta = JSON.parse(fs.readFileSync(path.join(run, "meta.json"), "utf8"));
const page = JSON.parse(read(path.join(run, "learner", "page.json")));
// Lessons the learner opened: their text and the tutor's notes.
const lessonDirs: string[] = [];
for (const m of fs.readdirSync(path.join(ROOT, "course", "modules"))) {
  const md = path.join(ROOT, "course", "modules", m);
  if (!fs.statSync(md).isDirectory()) continue;
  for (const l of fs.readdirSync(md)) {
    const id = l.match(/^(\d+\.\d+)-/)?.[1];
    if (id && page.lessons?.[id]?.visited) lessonDirs.push(path.join(md, l));
  }
}
const lessonsText = lessonDirs.map((d) => `<lesson dir="${path.basename(d)}">\n<lesson.md>\n${read(path.join(d, "lesson.md"))}\n</lesson.md>\n<tutor.md>\n${read(path.join(d, "tutor.md"))}\n</tutor.md>\n</lesson>`).join("\n\n");
const blind = (s: string) => s.replaceAll(meta.tutor_model, "<tutor model>").replace(/(aws|azure|nvidia)\/[\w./-]*(sonnet|nemotron|opus|haiku|gemini|gpt)[\w.-]*/gi, "<model>");
const { tutor_model, run_id, ...metaBlind } = meta;

const prompt = [
  read(path.join(ROOT, "sim", "rubric.md")).replaceAll("{{product}}", product),
  "<persona>", read(path.join(ROOT, "sim", "personas", meta.persona)), "</persona>",
  "<misconception-catalogue>", read(path.join(ROOT, "course", "misconceptions.md")), "</misconception-catalogue>",
  "<lessons-covered>", lessonsText, "</lessons-covered>",
  "<transcript note=\"what the learner saw and did; step numbers in [brackets]\">", blind(read(path.join(run, "transcript.md"))), "</transcript>",
  "<tutor-log note=\"the tutor's side: what the page told it, its tool calls (ask/settle/reveal/show_figure post to the page; bash runs code), and results; long items cut\">",
  blind(read(path.join(run, "tutor-log.md"), 250_000)), "</tutor-log>",
  "<progress.json>", read(path.join(run, "learner", "progress.json")), "</progress.json>",
  "<feedback-queue>", read(path.join(run, "learner", "feedback-queue.jsonl")), "</feedback-queue>",
  "<metrics>", JSON.stringify(metaBlind, null, 1), "</metrics>",
  "Grade this session now. Return the JSON object only.",
].join("\n\n");

const reply = await chat(grader, [{ role: "user", content: prompt }], { maxTokens: 6000 });
const g = firstJson(reply);
fs.writeFileSync(path.join(run, "grade.json"), JSON.stringify({ grader, ...g }, null, 2));
const num = Object.values<any>(g.scores).filter((v) => typeof v === "number");
const md = [
  `# Grade: ${meta.run_id}`, "",
  `Total ${num.reduce((a, b) => a + b, 0)} / ${num.length * 3} over ${num.length} scored criteria · fidelity ${g.fidelity}/3 · grader ${grader}`, "",
  "| criterion | score | evidence |", "|---|---|---|",
  ...Object.entries<any>(g.scores).map(([k, v]) => `| ${k} | ${v} | ${String(g.evidence?.[k] ?? "").replace(/\|/g, "/").replace(/\n/g, " ")} |`), "",
  `**Fidelity:** ${g.fidelity_note ?? ""}`, "",
  `**Worst moment:** ${g.worst_moment ?? ""}`, "",
  `**Accuracy issues:** ${(g.accuracy_issues ?? []).join("; ") || "none"}`, "",
  "**Fixes:**", ...(g.fixes ?? []).map((f: any) => `- ${f.file} (${f.scope}): ${f.change}`), "",
  `**Summary:** ${g.summary ?? ""}`,
].join("\n");
fs.writeFileSync(path.join(run, "grade.md"), md);
console.log(md.split("\n").slice(0, 3).join(" "));
