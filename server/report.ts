// The report archive (admin page, "Download report"): what the course authors need to understand a
// session, in one file the learner can email or attach to an issue. It holds the learner's conversations
// with the tutor, their progress, the tutor's feedback notes and the server's metrics and log, stamped with
// the app's commit. It leaves out the model key (endpoint.json), the access token and link, and the
// workspace's files (only their names and sizes); any key or token that shows up in a log is replaced.
import { execFile } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { config, learnerPath, ROOT } from "./config.ts";
import { current } from "./endpoint.ts";
import { app } from "./version.ts";

const FILES = ["progress.json", "page.json", "thread.json", "profile.md", "feedback-queue.jsonl", "metrics.jsonl"];
const DIRS = ["sessions"];
const LOG_LINES = 2000;

function secrets(): string[] {
  const s = [current()?.key, process.env.INFERENCE_API_KEY];
  try { s.push(JSON.parse(fs.readFileSync(learnerPath("access.json"), "utf8")).token); } catch {}
  return s.filter((x): x is string => typeof x === "string" && x.length >= 8);
}

function scrubber() {
  const hidden = secrets();
  const home = os.homedir();
  return (text: string) => {
    for (const k of hidden) text = text.split(k).join("[removed]");
    return home.length > 1 ? text.split(home).join("~") : text;
  };
}

function walk(dir: string, rel = ""): string[] {
  let out: string[] = [];
  for (const e of fs.readdirSync(path.join(dir, rel), { withFileTypes: true })) {
    const r = path.join(rel, e.name);
    if (e.isDirectory()) out = out.concat(walk(dir, r));
    else if (e.isFile()) out.push(r);
  }
  return out;
}

/** Writes the archive to a temporary folder; returns its path and a file name. Call cleanup() when sent. */
export async function buildReport(prefix: string, about: Record<string, unknown>): Promise<{ file: string; name: string; cleanup: () => void }> {
  const scrub = scrubber();
  const stamp = new Date().toISOString().slice(0, 16).replace(/[-:T]/g, "");
  const name = `${prefix}-${stamp}-${app.commit}`;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), `${prefix}-`));
  const out = path.join(tmp, name);
  fs.mkdirSync(out);
  const put = (rel: string, text: string) => {
    fs.mkdirSync(path.dirname(path.join(out, rel)), { recursive: true });
    fs.writeFileSync(path.join(out, rel), scrub(text));
  };

  for (const f of FILES) {
    try { put(f, fs.readFileSync(learnerPath(f), "utf8")); } catch {}
  }
  for (const d of DIRS) {
    const base = learnerPath(d);
    if (!fs.existsSync(base)) continue;
    for (const r of walk(base)) put(path.join(d, r), fs.readFileSync(path.join(base, r), "utf8"));
  }
  try {
    const log = fs.readFileSync(path.join(ROOT, "server.log"), "utf8").split("\n");
    put("server.log", log.slice(-LOG_LINES).join("\n"));
  } catch {}
  const work = learnerPath("work");
  if (fs.existsSync(work)) {
    put("work-files.txt", walk(work).map((r) => `${fs.statSync(path.join(work, r)).size}\t${r}`).join("\n") + "\n");
  }
  put("about.json", JSON.stringify({
    created: new Date().toISOString(),
    app: { commit: app.commit, dirty: app.dirty, date: app.date },
    model: `${config.provider}/${config.model}`,
    ...about,
    contents: "conversations with the tutor (sessions/), progress, the tutor's feedback notes, metrics, the server log; "
      + "no model key, no access token, no workspace files (work-files.txt lists them)",
  }, null, 2) + "\n");

  const file = path.join(tmp, name + ".tar.gz");
  await new Promise<void>((resolve, reject) =>
    execFile("tar", ["-czf", file, "-C", tmp, name], (e) => (e ? reject(e) : resolve())));
  return { file, name: name + ".tar.gz", cleanup: () => fs.rmSync(tmp, { recursive: true, force: true }) };
}
