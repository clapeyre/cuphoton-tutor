// Smoke test for a compute-centre install: proves GPU, endpoint and course load.
//   npm run smoke            (exit code 0 = all good)
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { config } from "../server/config.ts";
import { loadCourse, normKey } from "../server/content.ts";

let failed = 0;
const ok = (name: string, detail = "") => console.log(`  ok    ${name}${detail ? "  " + detail : ""}`);
const bad = (name: string, detail: string) => { failed++; console.log(`  FAIL  ${name}  ${detail}`); };

console.log("cuPhoton Learn smoke test");

// 1. Course: every lesson parses; every video, figure and turn image exists.
try {
  const c = loadCourse();
  let missing = 0;
  for (const l of c.lessons.values()) {
    for (const p of l.parts) {
      const srcs = p.kind === "figure" ? [p.src] : p.kind === "turn" && p.image ? [p.image] : [];
      for (const s of srcs) if (!fs.existsSync(path.join(config.courseDir, s.replace(/^\/course-files\//, "")))) { missing++; bad("course file", `${l.id}: ${s}`); }
    }
    if (!l.tutorNotes) bad("tutor notes", `${l.id} has no tutor.md`);
    // Every [[term]] and key term must have a definition, or it renders as plain text.
    const refs = [...l.source.matchAll(/\[\[(.+?)\]\]/g)].map((m) => m[1].split("|")[0]).concat(l.terms);
    for (const r of refs) {
      const k = r.startsWith("@") ? r : normKey(r);
      if (!c.glossary.has(k) && !c.glossary.has(k.replace(/s$/, ""))) bad("term", `${l.id}: [[${r}]] has no definition`);
    }
  }
  if (c.lessons.size === 0) bad("course", "no lessons found");
  else if (!missing) ok("course", `${c.modules.length} module(s), ${c.lessons.size} lessons, ${c.glossary.size} glossary entries`);
} catch (e: any) { bad("course", e.message); }

// 2. Learner Python: NumPy, Matplotlib, cuPhoton.
const pyBin = config.pythonBin || path.join(config.cuphotonDir, ".venv", "bin");
const py = path.join(pyBin, "python");
const r = spawnSync(py, ["-c", "import numpy, matplotlib, scipy, cuphoton; print(cuphoton.__version__)"], { encoding: "utf8" });
r.status === 0 ? ok("python", `${py} · cuphoton ${r.stdout.trim()}`) : bad("python", (r.stderr || r.error?.message || "").trim().split("\n").pop() ?? "");
if (!fs.existsSync(config.cuphotonDir)) bad("cuphoton checkout", config.cuphotonDir);
else {
  const head = spawnSync("git", ["-C", config.cuphotonDir, "rev-parse", "HEAD"], { encoding: "utf8" }).stdout.trim();
  const want = loadCourse().commit;
  head === want ? ok("cuphoton checkout", `pinned ${head.slice(0, 12)}`) : bad("cuphoton checkout", `at ${head.slice(0, 12)}, course wants ${want.slice(0, 12)}`);
}

// 3. GPU: nvidia-smi, and CuPy can allocate and synchronize (GPU lessons need it; Module 00 doesn't).
const smi = spawnSync("nvidia-smi", ["--query-gpu=name,memory.total", "--format=csv,noheader"], { encoding: "utf8" });
smi.status === 0 ? ok("gpu", smi.stdout.trim()) : bad("gpu", "nvidia-smi failed");
// Modules 00–02 expect the default environment to have no usable GPU; Module 03 on uses the GPU environment.
const cupyCpuEnv = spawnSync(py, ["-c", "import cupy"], { encoding: "utf8" });
cupyCpuEnv.status === 0 ? console.log(`  warn  default env  ${py} has CuPy: Module 02's fallback lessons assume it doesn't`) : ok("default env", "CPU only, as Modules 00–02 expect");
const gpy = path.join(config.gpuPythonBin, "python");
const cupy = spawnSync(gpy, ["-c", "import cupy as cp, cuphoton; a=cp.arange(10); cp.cuda.Device().synchronize(); print(int(a.sum()))"], { encoding: "utf8" });
cupy.status === 0 && cupy.stdout.trim().endsWith("45") ? ok("gpu env", `${gpy} · CuPy runs on the GPU`) : bad("gpu env", `not usable (${gpy}); run tools/setup-gpu-env.sh. Needed from Module 03.`);

// 4. Endpoint: the configured model answers a tool call.
try {
  const models = JSON.parse(fs.readFileSync(path.join(config.tutorDir, "pi-agent", "models.json"), "utf8"));
  const prov = models.providers?.[config.provider];
  if (!prov) throw new Error(`provider ${config.provider} not in models.json`);
  const key = String(prov.apiKey ?? "").replace(/^\$\{?(\w+)\}?$/, (_: string, k: string) => process.env[k] ?? "");
  const t0 = Date.now();
  const res = await fetch(`${prov.baseUrl}/chat/completions`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${key}` },
    body: JSON.stringify({
      model: config.model, max_tokens: 2000,
      messages: [{ role: "user", content: "Call the ping tool with n=7." }],
      tools: [{ type: "function", function: { name: "ping", description: "ping", parameters: { type: "object", properties: { n: { type: "integer" } }, required: ["n"] } } }],
    }),
    signal: AbortSignal.timeout(60000),
  });
  const j: any = await res.json();
  const call = j.choices?.[0]?.message?.tool_calls?.[0];
  call?.function?.name === "ping" ? ok("endpoint", `${config.provider}/${config.model} · tool call in ${((Date.now() - t0) / 1000).toFixed(1)} s`) : bad("endpoint", `HTTP ${res.status}: ${JSON.stringify(j).slice(0, 200)}`);
} catch (e: any) { bad("endpoint", e.message); }

// 5. Learner dir is writable.
try { fs.mkdirSync(path.join(config.learnerDir, "work"), { recursive: true }); fs.accessSync(config.learnerDir, fs.constants.W_OK); ok("learner dir", config.learnerDir); }
catch (e: any) { bad("learner dir", e.message); }

console.log(failed ? `${failed} check(s) failed` : "all checks passed");
process.exit(failed ? 1 : 0);
