// Run recorder: watches the tutor's tool calls and keeps a record of every run,
// so anything the tutor puts on the page carries "Made by … · CPU · 0.4 s · Run record".
// The record is built from what actually happened (commands, files written,
// receipts), never from what the tutor says about it.
import fs from "node:fs";
import path from "node:path";
import { config } from "./config.ts";

export interface RunRecord {
  id: string;
  by: string; // xRep, xPois, …, or NumPy / Python / shell
  device: "CPU" | "GPU";
  seconds: number;
  at: number;
  commands: string[];
  files: string[]; // written, relative to the learner dir
  code?: { path: string; text: string }[];
  receipt?: Record<string, unknown>; // summary.json fields, when a cuPhoton CLI run wrote one
  ok: boolean;
  tool: string;
  /** Earlier runs whose output this one read (a plotting script drawing a GPU run's results). */
  inputs?: Omit<RunRecord, "inputs">[];
}

const STAGES = ["xRep", "xPois", "xFit", "xScan", "xDR", "xImage"];
const SKIP = /(^|\/)(\.venv|node_modules|__pycache__|sessions)(\/|$)/;

function snapshot(dir: string, out = new Map<string, number>(), base = dir): Map<string, number> {
  let entries: fs.Dirent[] = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    const p = path.join(dir, e.name);
    const rel = path.relative(base, p);
    if (SKIP.test(rel)) continue;
    if (e.isDirectory()) snapshot(p, out, base);
    else if (e.isFile()) { try { out.set(rel, fs.statSync(p).mtimeMs); } catch {} }
  }
  return out;
}

function readSmall(p: string, max = 20000): string | null {
  try {
    const st = fs.statSync(p);
    if (st.size > max) return fs.readFileSync(p, "utf8").slice(0, max) + "\n… (truncated)";
    return fs.readFileSync(p, "utf8");
  } catch { return null; }
}

export class Recorder {
  runs: RunRecord[] = [];
  private pending = new Map<string, { t0: number; before: Map<string, number>; command: string; tool: string; path?: string }>();
  private n = 0;

  start(toolCallId: string, toolName: string, args: any) {
    if (toolName !== "bash" && toolName !== "write" && toolName !== "edit") return;
    this.pending.set(toolCallId, {
      t0: Date.now(),
      before: toolName === "bash" ? snapshot(config.learnerDir) : new Map(),
      command: toolName === "bash" ? String(args?.command ?? "") : `${toolName} ${args?.path ?? args?.file_path ?? ""}`,
      tool: toolName,
      path: args?.path ?? args?.file_path,
    });
  }

  end(toolCallId: string, isError: boolean, durationMs?: number) {
    const p = this.pending.get(toolCallId);
    if (!p) return;
    this.pending.delete(toolCallId);
    let files: string[] = [];
    if (p.tool === "bash") {
      const after = snapshot(config.learnerDir);
      for (const [f, m] of after) if (p.before.get(f) !== m) files.push(f);
    } else if (p.path) {
      files = [path.relative(config.learnerDir, path.resolve(config.learnerDir, p.path))];
    }
    const seconds = (durationMs ?? Date.now() - p.t0) / 1000;
    const code: RunRecord["code"] = [];
    if (p.tool === "bash") {
      for (const m of p.command.matchAll(/(?:python3?|uv run[^|;&]*?python)\s+(?:-\S+\s+)*([\w./-]+\.py)/g)) {
        const sp = path.resolve(config.learnerDir, m[1]);
        const text = readSmall(sp);
        if (text != null) code.push({ path: path.relative(config.learnerDir, sp), text });
      }
      const heredoc = p.command.match(/<<\s*['"]?(\w+)['"]?\n([\s\S]*?)\n\1/);
      if (heredoc) code.push({ path: "(inline)", text: heredoc[2] });
    }
    const all = p.command + "\n" + code.map((c) => c.text).join("\n");
    let receipt: Record<string, unknown> | undefined;
    for (const f of files.filter((f) => f.endsWith("summary.json"))) {
      try {
        const j = JSON.parse(fs.readFileSync(path.join(config.learnerDir, f), "utf8"));
        receipt = Object.fromEntries(["workflow", "requested_backend", "backend", "device", "dtype", "fits_reader"].filter((k) => k in j).map((k) => [k, j[k]]));
      } catch {}
    }
    // Every cuPhoton stage the run used, in pipeline order ("xRep + xPois").
    const stages = STAGES.filter((s) => new RegExp(`\\b${s}\\b|cuphoton\\.${s.toLowerCase()}|\\b${s.toLowerCase()}\\b`).test(all));
    const stage = stages.length ? stages.join(" + ") : /cuphoton\.core|fits_io/.test(all) ? "cuPhoton Core" : undefined;
    const by = stage ?? (/\bnumpy\b|\bnp\./.test(all) ? "NumPy" : /python/.test(all) ? "Python" : "shell");
    const gpu = receipt
      ? /cuda|gpu/i.test(String(receipt.device ?? "")) || /cupy|torch|cutile|native/i.test(String(receipt.backend ?? ""))
      : /--require-gpu|backend\s*=\s*["'](cupy|torch|cutile)["']|\bcupy\b/.test(all);
    this.runs.push({
      id: `r${++this.n}-${Date.now().toString(36)}`, by, device: gpu ? "GPU" : "CPU", seconds, at: Date.now(),
      commands: [p.command.slice(0, 4000)], files, code: code.length ? code : undefined, receipt, ok: !isError, tool: p.tool,
    });
    if (this.runs.length > 500) this.runs.splice(0, this.runs.length - 500);
  }

  /** The most recent run that wrote this file, with the runs that wrote its inputs folded in: a figure drawn
   *  by a 0.4 s plotting script from a GPU run's summary.json is labelled with that GPU run. */
  recordFor(file: string): RunRecord | undefined {
    const rel = path.relative(config.learnerDir, path.resolve(config.learnerDir, file));
    const i = this.runs.findLastIndex((x) => x.files.includes(rel) && x.tool === "bash");
    if (i < 0) return undefined;
    const r = this.runs[i];
    const text = r.commands.join("\n") + "\n" + (r.code ?? []).map((c) => c.text).join("\n");
    const own = path.dirname(rel);
    // The script names the file (or its path from a subfolder: cd work/03 && … "qs-gpu/summary.json"), or names
    // the run's output folder as a whole (--output-dir work/03/qs-gpu). Its own output folder doesn't count.
    const mentions = (f: string) => {
      const parts = f.split("/");
      for (let k = 0; k <= parts.length - 2; k++) if (text.includes(parts.slice(k).join("/"))) return true;
      const dir = path.dirname(f);
      // A bare name ("chain_gpu.json") only counts next to the figure or in a folder the command cd's into.
      if ((dir === own || text.includes(`cd ${dir}`)) && new RegExp(`["'/\\s]${parts.at(-1)!.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["'\\s)]`).test(text)) return true;
      if (dir === "." || !dir.includes("/") || own === dir || own.startsWith(dir + "/")) return false;
      return new RegExp(`${dir.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}/?["'\\s)]`).test(text);
    };
    const inputs: RunRecord[] = [];
    const seen = new Set<string>();
    for (let j = i - 1; j >= 0 && j >= i - 200; j--) {
      const x = this.runs[j];
      if (!x.ok || x.tool !== "bash") continue;
      const read = x.files.filter((f) => f !== rel && !seen.has(f) && !/\.(png|jpe?g|svg|log|err|out)$/.test(f) && mentions(f));
      if (!read.length) continue;
      x.files.forEach((f) => seen.add(f));
      inputs.push(x);
    }
    if (!inputs.length) return r;
    const all = [...inputs.reverse(), r];
    const stages = STAGES.filter((s) => all.some((x) => x.by.split(" + ").includes(s)));
    return {
      ...r,
      by: stages.length ? stages.join(" + ") : inputs.find((x) => x.by !== "shell")?.by ?? r.by,
      device: all.some((x) => x.device === "GPU") ? "GPU" : "CPU",
      seconds: all.reduce((t, x) => t + x.seconds, 0),
      receipt: r.receipt ?? inputs.findLast((x) => x.receipt)?.receipt,
      inputs: inputs.map(({ inputs: _, ...x }) => x),
    };
  }
}
