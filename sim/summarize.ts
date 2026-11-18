// One table over sim runs: scores, coverage, waits, tutor errors.  npx tsx sim/summarize.ts runs/<id> ...
import fs from "node:fs";
import path from "node:path";

const crit = ["contract", "placement_pace", "catalogued", "novel", "unstick", "visuals", "accuracy", "page_mechanics", "outcome"];
const short = ["contr", "pace", "catal", "novel", "unstk", "vis", "accur", "mech", "outc"];
const rows: string[] = [];
rows.push(`| run | ${short.join(" | ")} | total | fid | turns settled | lessons | steps | end | wait p50/p90 s | tool err | errors |`);
rows.push(`|---|${crit.map(() => "---").join("|")}|---|---|---|---|---|---|---|---|---|`);
const byModel = new Map<string, { sum: number; max: number; n: number }>();
for (const dir of process.argv.slice(2)) {
  const m = JSON.parse(fs.readFileSync(path.join(dir, "meta.json"), "utf8"));
  let g: any = null; try { g = JSON.parse(fs.readFileSync(path.join(dir, "grade.json"), "utf8")); } catch {}
  const sc = crit.map((c) => g?.scores?.[c] ?? "?");
  const nums = sc.filter((v) => typeof v === "number") as number[];
  const tot = nums.reduce((a, b) => a + b, 0);
  const model = m.tutor_model.split("/").pop();
  const agg = byModel.get(model) ?? { sum: 0, max: 0, n: 0 };
  agg.sum += tot; agg.max += nums.length * 3; agg.n++; byModel.set(model, agg);
  rows.push(`| ${m.persona.replace(".md", "")} · ${model.replace("bedrock-claude-", "")} | ${sc.join(" | ")} | ${tot}/${nums.length * 3} | ${g?.fidelity ?? "?"} | ${m.turns_settled}/${m.turns_total} | ${m.lessons_visited}/${m.lessons_total} | ${m.steps} | ${m.end_reason} | ${m.wait_s.median?.toFixed(0)}/${m.wait_s.p90?.toFixed(0)} | ${m.tutor.tool_errors} | ${m.tutor.errors} |`);
}
console.log(rows.join("\n"));
console.log();
for (const [model, a] of byModel) console.log(`${model}: ${a.sum}/${a.max} (${((100 * a.sum) / a.max).toFixed(0)}%) over ${a.n} runs`);
