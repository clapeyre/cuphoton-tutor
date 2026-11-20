// Run recorder: watches the tutor's tool calls and keeps a record of every run,
// so anything the tutor puts on the page carries "Made by … · CPU · 0.4 s · Run record".
// The record is built from what actually happened (commands, files written,
// receipts), never from what the tutor says about it.
import fs from "node:fs";
import path from "node:path";
import { config } from "./config.ts";
import type { RunRules } from "./content.ts";

export interface RunRecord {
  id: string;
  by: string; // the course's stages (cuPhoton: xRep, xPois, …), or NumPy / Python / shell
  device: "CPU" | "GPU" | "CPU + GPU";
  seconds: number;
  at: number;
  commands: string[];
  files: string[]; // written, relative to the learner dir
  code?: { path: string; text: string }[];
  receipt?: Record<string, unknown>; // a receipt's fields (course.yaml runs.receipts), when the run wrote one
  ok: boolean;
  tool: string;
  /** Earlier runs whose output this one read (a plotting script drawing a GPU run's results). */
  inputs?: Omit<RunRecord, "inputs">[];
}

// A stage named only to say it didn't run (xrep='skipped', "xRep: skipped", "xRep was skipped") isn't one the run used.
const NOT_RUN = String.raw`(?!["']?\s*[=:]\s*["']?(skip|none|off|false|no\b|not)|\s+(was\s+|is\s+)?(skipped|not run|off)\b)`;
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
  private stages: string[];
  constructor(private rules: RunRules) { this.stages = rules.stages; }
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
        // Follow any `cd` before it (cd work/04 && $PY stack_compare.py).
        let cwd = config.learnerDir;
        for (const c of cmd.slice(0, m.index).matchAll(/(?:^|[;\n&|(]\s*)cd\s+([^\s;&|)]+)/g)) cwd = path.resolve(cwd, c[1].replace(/^["']|["']$/g, ""));
        const sp = path.resolve(cwd, m[1]);
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
    const components = new Set<string>(); // what a quickstart summary says actually ran
    const devices = new Set<"CPU" | "GPU">(); // every receipt's device, for a run that did both
    // A run's receipt (cuPhoton: a summary.json from the chain or a quickstart, a manifest.json from the xRay detector track).
    for (const f of files.filter((f) => this.rules.receipts.some((r) => f.endsWith(r)))) {
      try {
        const j = JSON.parse(fs.readFileSync(path.join(config.learnerDir, f), "utf8"));
        if (Array.isArray(j.components)) for (const c of j.components) components.add(String(c).toLowerCase());
        receipt = Object.fromEntries(this.rules.receiptFields.filter((k) => k in j).map((k) => [k, j[k]]));
        // Some workflows keep the device deeper (xImage: performance.device.device = "cuda").
        if (receipt.device == null) { const d = deepDevice(j); if (d) receipt.device = d; }
        if (receipt.device != null) devices.add(isGpu(receipt.device) ? "GPU" : "CPU");
      } catch {}
    }
    // Every stage the run used, in pipeline order ("xRep + xPois"). A receipt that lists its components
    // decides; otherwise the code does (cuPhoton's run_quickstarts.py names all of them, so it can't).
    const pkg = this.rules.package;
    const stages = components.size ? this.stages.filter((s) => components.has(s.toLowerCase()))
      : this.stages.filter((s) => new RegExp(`(\\b${s}\\b${pkg ? `|${pkg}\\.${s.toLowerCase()}` : ""}|\\b${s.toLowerCase()}\\b)${NOT_RUN}`).test(all));
    const core = this.rules.core;
    const stage = stages.length ? stages.join(" + ") : core && new RegExp(core.pattern).test(all) ? core.label : undefined;
    const by = stage ?? (/\bnumpy\b|\bnp\./.test(all) ? "NumPy" : /python/.test(all) ? "Python" : "shell");
    // The receipt's device decides when it has one (torch and native backends also run on the CPU).
    // A summary with neither (a chain script's own summary) leaves it to the code.
    const gpu = receipt?.device != null ? isGpu(receipt.device)
      : receipt?.backend != null ? !!this.rules.gpuBackend && new RegExp(this.rules.gpuBackend, "i").test(String(receipt.backend))
      : !!this.rules.gpuCode && new RegExp(this.rules.gpuCode).test(all);
    this.runs.push({
      id: `r${++this.n}-${Date.now().toString(36)}`, by, device: devices.size > 1 ? "CPU + GPU" : gpu ? "GPU" : "CPU", seconds, at: Date.now(),
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
    // Returns what the script named (the matched path tail, or the folder), or null.
    const mentions = (f: string): string | null => {
      const parts = f.split("/");
      for (let k = 0; k <= parts.length - 2; k++) { const tail = parts.slice(k).join("/"); if (text.includes(tail)) return tail; }
      const dir = path.dirname(f);
      // A bare name ("chain_gpu.json") only counts next to the figure or in a folder the command cd's into.
      if ((dir === own || text.includes(`cd ${dir}`)) && new RegExp(`["'/\\s]${parts.at(-1)!.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["'\\s)]`).test(text)) return f;
      if (dir === "." || !dir.includes("/") || own === dir || own.startsWith(dir + "/")) return null;
      // A path built from pieces under the figure's folder: root / 'chain-01' / m / 'summary.json' for m in ('cpu', 'gpu').
      // Every part of its path below that folder appears as a quoted string in the script.
      if (f.startsWith(own + "/")) {
        const parts2 = f.slice(own.length + 1).split("/");
        const quoted = (x: string) => new RegExp(`["']${x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["']`).test(text);
        if (parts2.length > 1 && parts2.every(quoted)) return f;
      }
      // A folder named from inside the folder the command cd's into: cd work/08 && … look run2 …
      for (const c of text.matchAll(/(?:^|[;\n&|(]\s*)cd\s+([^\s;&|)]+)/g)) {
        const base = path.relative(config.learnerDir, path.resolve(config.learnerDir, c[1].replace(/^["']|["']$/g, "")));
        if (!dir.startsWith(base + "/")) continue;
        const sub = dir.slice(base.length + 1).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        if (new RegExp(`(^|[\\s"'=])${sub}/?(["'\\s)]|$)`, "m").test(text)) return dir;
      }
      return new RegExp(`${dir.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}/?["'\\s)]`).test(text) ? dir : null;
    };
    const inputs: RunRecord[] = [];
    const seen = new Set<string>();
    // What the script named belongs to the latest run that wrote it: "runs/reproject/artifacts/mask.npy"
    // matches every quickstart's output folder, but the script read the newest one.
    const claimed = new Set<string>();
    for (let j = i - 1; j >= 0 && j >= i - 200; j--) {
      const x = this.runs[j];
      if (!x.ok || x.tool !== "bash") continue;
      const named = x.files.filter((f) => f !== rel && !seen.has(f) && !/\.(png|jpe?g|svg|log|err|out)$/.test(f))
        .map(mentions).filter((m): m is string => m != null);
      const fresh = named.filter((m) => !claimed.has(m));
      named.forEach((m) => claimed.add(m));
      if (!fresh.length) continue;
      x.files.forEach((f) => seen.add(f));
      inputs.push(x);
    }
    if (!inputs.length) return r;
    const all = [...inputs.reverse(), r];
    const stages = this.stages.filter((s) => all.some((x) => x.by.split(" + ").includes(s)));
    return {
      ...r,
      by: stages.length ? stages.join(" + ") : inputs.find((x) => x.by !== "shell")?.by ?? r.by,
      device: foldDevice(all),
      seconds: all.reduce((t, x) => t + x.seconds, 0),
      receipt: r.receipt ?? inputs.findLast((x) => x.receipt)?.receipt,
      inputs: inputs.map(({ inputs: _, ...x }) => x),
    };
  }
}

/** The device of a figure's runs taken together. */
function foldDevice(all: RunRecord[]): RunRecord["device"] {
  // Runs with a receipt decide; without any, a GPU run among the inputs makes it GPU (as before).
  const withReceipt = all.filter((x) => x.receipt?.device != null || x.receipt?.backend != null);
  if (!withReceipt.length) return all.some((x) => x.device !== "CPU") ? "GPU" : "CPU";
  const runs = withReceipt;
  const gpu = runs.some((x) => x.device !== "CPU"), cpu = runs.some((x) => x.device !== "GPU");
  return gpu && cpu ? "CPU + GPU" : gpu ? "GPU" : "CPU";
}

/** The first string `device` anywhere in a summary (nested receipts), or undefined. */
/** A receipt's device names a GPU: "cuda:0", "gpu", or the card itself ("NVIDIA GeForce RTX 4070 Ti SUPER", "NVIDIA H100"):
 *  learners' own summaries often record torch.cuda.get_device_name(). */
export function isGpu(device: unknown): boolean {
  return /cuda|gpu|nvidia|geforce|\brtx\b|tesla|quadro|\b[abhlt]\d{2,3}\b|gh200|gb200|dgx/i.test(String(device));
}
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
