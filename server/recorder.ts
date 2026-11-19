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

const STAGES = ["xDR", "xRep", "xPois", "xFit", "xScan", "xLens", "xImage", "xBeam", "xRay"];
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

/** A script whose first line is `# hold-back: <why>` answers a later lesson's question:
 *  the run record names it but doesn't show its code (the stage and device still come from it). */
export const HOLD_MARK = /^#\s*hold-back\b/i;
function heldBack(text: string): string {
  return HOLD_MARK.test(text) ? "(code held back for a later lesson; it's in the Files panel)" : text;
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
    const raw: string[] = []; // full texts, for the stage and device even when the code is held back
    let shown = p.command;
    if (p.tool === "bash") {
      // Expand simple shell variables (G=/path/script.py; $PY $G …) so the script is found and read.
      const vars = new Map<string, string>();
      for (const m of p.command.matchAll(/(?:^|[;\n&]\s*)(\w+)=([^\s;&|]+)/g)) vars.set(m[1], m[2].replace(/^["']|["']$/g, ""));
      const cmd = p.command.replace(/\$\{?(\w+)\}?/g, (m, v) => vars.get(v) ?? m);
      for (const m of cmd.matchAll(/(?:python3?|uv run[^|;&]*?python)\s+(?:-\S+\s+)*([\w./-]+\.py)/g)) {
        const sp = path.resolve(config.learnerDir, m[1]);
        const text = readSmall(sp);
        if (text != null) { raw.push(text); code.push({ path: path.relative(config.learnerDir, sp), text: heldBack(text) }); }
      }
      const heredoc = cmd.match(/<<\s*['"]?(\w+)['"]?\n([\s\S]*?)\n\1/);
      if (heredoc) {
        raw.push(heredoc[2]);
        code.push({ path: "(inline)", text: heldBack(heredoc[2]) });
        if (HOLD_MARK.test(heredoc[2])) shown = shown.replace(heredoc[2], heldBack(heredoc[2]));
      }
    }
    const all = p.command + "\n" + raw.join("\n");
    let receipt: Record<string, unknown> | undefined;
    for (const f of files.filter((f) => f.endsWith("summary.json"))) {
      try {
        const j = JSON.parse(fs.readFileSync(path.join(config.learnerDir, f), "utf8"));
        receipt = Object.fromEntries(["workflow", "requested_backend", "backend", "device", "dtype", "fits_reader"].filter((k) => k in j).map((k) => [k, j[k]]));
        // Some workflows keep the device deeper (xImage: performance.device.device = "cuda").
        if (receipt.device == null) { const d = deepDevice(j); if (d) receipt.device = d; }
      } catch {}
    }
    // Every cuPhoton stage the run used, in pipeline order ("xRep + xPois").
    const stages = STAGES.filter((s) => new RegExp(`\\b${s}\\b|cuphoton\\.${s.toLowerCase()}|\\b${s.toLowerCase()}\\b`).test(all));
    const stage = stages.length ? stages.join(" + ") : /cuphoton\.core|fits_io/.test(all) ? "cuPhoton Core" : undefined;
    const by = stage ?? (/\bnumpy\b|\bnp\./.test(all) ? "NumPy" : /python/.test(all) ? "Python" : "shell");
    // The receipt's device decides when it has one (torch and native backends also run on the CPU).
    // A summary with neither (a chain script's own summary) leaves it to the code.
    const gpu = receipt?.device != null ? /cuda|gpu/i.test(String(receipt.device))
      : receipt?.backend != null ? /cupy|cutile/i.test(String(receipt.backend))
      : /--require-gpu|backend\s*=\s*["'](cupy|torch|cutile)["']|\bcupy\b/.test(all);
    this.runs.push({
      id: `r${++this.n}-${Date.now().toString(36)}`, by, device: gpu ? "GPU" : "CPU", seconds, at: Date.now(),
      commands: [shown.slice(0, 4000)], files, code: code.length ? code : undefined, receipt, ok: !isError, tool: p.tool,
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

/** The first string `device` anywhere in a summary (nested receipts), or undefined. */
function deepDevice(o: unknown, depth = 0): string | undefined {
  if (depth > 4 || o == null || typeof o !== "object") return undefined;
  for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
    if (k === "device" && typeof v === "string") return v;
  }
  for (const v of Object.values(o as Record<string, unknown>)) {
    const d = deepDevice(v, depth + 1);
    if (d) return d;
  }
  return undefined;
}
