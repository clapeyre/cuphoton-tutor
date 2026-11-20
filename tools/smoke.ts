// Smoke test for a compute-centre install: proves GPU, endpoint and course load.
//   npm run smoke            (exit code 0 = all good)
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { config } from "../server/config.ts";
import { loadCourse, normKey, type Course } from "../server/content.ts";
import { isConfigured, pingEndpoint } from "../server/endpoint.ts";

let failed = 0;
const ok = (name: string, detail = "") => console.log(`  ok    ${name}${detail ? "  " + detail : ""}`);
const bad = (name: string, detail: string) => { failed++; console.log(`  FAIL  ${name}  ${detail}`); };
const warn = (name: string, detail: string) => console.log(`  warn  ${name}  ${detail}`);

let course: Course;
try { course = loadCourse(); } catch (e: any) { console.log(`  FAIL  course  ${e.message}`); process.exit(1); }
console.log(`${course.brand} smoke test`);

// 1. Course: every lesson parses; every video, figure and turn image exists.
try {
  const c = course;
  let missing = 0;
  for (const l of c.lessons.values()) {
    for (const p of l.parts) {
      const srcs = p.kind === "figure" ? [p.src] : p.kind === "turn" && p.image ? [p.image] : [];
      for (const s of srcs) if (!fs.existsSync(path.join(config.courseDir, s.replace(/^\/course-files\//, "")))) { missing++; bad("course file", `${l.id}: ${s}`); }
    }
    if (!l.tutorNotes) bad("tutor notes", `${l.id} has no tutor.md`);
    // Every [[term]] and key term must have a definition, or it renders as plain text.
    const refs = [...l.source.matchAll(/\[\[(.+?)\]\]/g)].map((m) => m[1]).concat(l.terms).map((r) => r.split("|")[0]);
    for (const r of refs) {
      const k = r.startsWith("@") ? r : normKey(r);
      if (!c.glossary.has(k) && !c.glossary.has(k.replace(/s$/, ""))) bad("term", `${l.id}: [[${r}]] has no definition`);
    }
  }
  if (c.lessons.size === 0) bad("course", "no lessons found");
  else if (!missing) ok("course", `${c.modules.length} module(s), ${c.lessons.size} lessons, ${c.glossary.size} glossary entries`);
} catch (e: any) { bad("course", e.message); }

// 2. The product checkout, at the commit the course is pinned to.
if (!fs.existsSync(config.productDir)) bad(`${course.product || "product"} checkout`, config.productDir);
else {
  const head = spawnSync("git", ["-C", config.productDir, "rev-parse", "HEAD"], { encoding: "utf8" }).stdout.trim();
  const want = course.commit;
  head === want ? ok(`${course.product} checkout`, `pinned ${head.slice(0, 12)}`) : bad(`${course.product} checkout`, `at ${head.slice(0, 12)}, course wants ${want.slice(0, 12)}`);
}

// 3. GPU, then the course's own checks of its environments (course/smoke.ts, if it has one).
const smi = spawnSync("nvidia-smi", ["--query-gpu=name,memory.total", "--format=csv,noheader"], { encoding: "utf8" });
smi.status === 0 ? ok("gpu", smi.stdout.trim()) : bad("gpu", "nvidia-smi failed");
const courseChecks = path.join(config.courseDir, "smoke.ts");
if (fs.existsSync(courseChecks)) {
  const { default: checks } = await import(pathToFileURL(courseChecks).href);
  await checks({ ok, bad, warn, config, course });
}

// 4. Endpoint: the configured model answers a tool call.
if (isConfigured()) {
  const ping = await pingEndpoint();
  ping.ok ? ok("endpoint", ping.detail) : bad("endpoint", ping.detail);
} else ok("endpoint", "none set yet: the page asks for one on first visit (/setup)");

// 5. Learner dir is writable.
try { fs.mkdirSync(path.join(config.learnerDir, "work"), { recursive: true }); fs.accessSync(config.learnerDir, fs.constants.W_OK); ok("learner dir", config.learnerDir); }
catch (e: any) { bad("learner dir", e.message); }

console.log(failed ? `${failed} check(s) failed` : "all checks passed");
process.exit(failed ? 1 : 0);
