// Admin page data: how the tutor is doing. Read from the main session log (pi writes every
// model call there, with usage and timing), plus a small log of what the session file doesn't
// keep (learner/metrics.jsonl: retries, compactions as they happen, margin calls), plus the
// live tutor and the machine. Nothing here changes the learner's state.
import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { config, learnerPath } from "./config.ts";
import type { Tutor } from "./tutor.ts";

type Call = { t: number; ctx: number; cached: number; out: number; cost: number; ms: number | null; stop: string; error?: string; lesson: string | null; kind: string };
type Prompt = {
  t: number; kind: string; lesson: string | null; label: string;
  firstMs: number | null; totalMs: number | null; calls: number; tools: number; toolMs: number; toolErrors: number;
  ctx: number; cost: number; error?: string;
};
type ToolStat = { n: number; errors: number; ms: number[] };

// Lesson ids were renumbered twice on 17-18 Nov 2026 (tools/renumber-learner.py, which leaves a marker
// file per migration): log lines older than a marker use the ids from before it. Map them, so per-lesson
// figures add up under today's names.
const MIGRATIONS: { marker: string; map: Record<string, string> }[] = [
  { marker: ".renumbered-2026-11-18", map: { "6.1": "9.1", "7.1": "6.1", "7.2": "6.2", "7.3": "6.3" } },
  { marker: ".renumbered-2026-11-18b", map: Object.fromEntries([1, 2, 3].flatMap((i) => [[`6.${i}`, `7.${i}`], [`7.${i}`, `8.${i}`], [`8.${i}`, `6.${i}`]])) },
];
type Applied = { at: number; map: Record<string, string> }[];
function migrationsApplied(): Applied {
  return MIGRATIONS.flatMap((m) => { try { return [{ at: fs.statSync(learnerPath(m.marker)).mtimeMs, map: m.map }]; } catch { return []; } });
}
const renumber = (id: string, t: number, applied: Applied) => applied.reduce((x, m) => (t < m.at ? m.map[x] ?? x : x), id);

/** Which kind of prompt a user message is, from the markers the server writes (tutor.ts). */
function classify(text: string): { kind: string; lesson: string | null; label: string } {
  let m: RegExpMatchArray | null;
  if ((m = text.match(/\[your-turn (\d+\.\d+)\/([\w-]+)\]/))) {
    const said = text.slice(m.index! + m[0].length).match(/Learner:\s*([^\n]*)/);
    return { kind: "reply", lesson: m[1], label: `${m[2]}: ${said ? said[1] : text.slice(m.index! + m[0].length).trim().split("\n")[0]}` };
  }
  if ((m = text.match(/\[page\] Prepare lesson (\d+\.\d+)/))) return { kind: "prepare", lesson: m[1], label: "prepare ahead" };
  if ((m = text.match(/\[page\] Learner opened lesson (\d+\.\d+)/))) return { kind: "open", lesson: m[1], label: "opened (first visit)" };
  if ((m = text.match(/\[page\] Learner is back on lesson (\d+\.\d+)/))) return { kind: "return", lesson: m[1], label: "came back" };
  if ((m = text.match(/\[page\] A side trip from lesson (\d+\.\d+)/))) return { kind: "note", lesson: m[1], label: "margin thread closed" };
  return { kind: "other", lesson: null, label: text.split("\n")[0] };
}

const PAGE_TOOLS = new Set(["show_figure", "ask", "settle", "reveal"]);
const textOf = (c: any) => typeof c === "string" ? c : Array.isArray(c) ? c.filter((x: any) => x.type === "text").map((x: any) => x.text).join("\n") : "";

/** Incremental reader of one session file: only new bytes are parsed on each refresh. */
class SessionLog {
  offset = 0;
  rest = "";
  calls: Call[] = [];
  prompts: Prompt[] = [];
  compactions: { t: number; before: number; summaryChars: number; cost: number }[] = [];
  tools = new Map<string, ToolStat>();
  errors: { t: number; where: string; message: string }[] = [];
  private cur: Prompt | null = null;
  private pendingTool = new Map<string, number>(); // toolCallId -> time the call was requested
  constructor(public file: string, private applied: Applied) {}

  refresh() {
    let size: number;
    try { size = fs.statSync(this.file).size; } catch { return; }
    if (size < this.offset) { Object.assign(this, new SessionLog(this.file, this.applied)); }
    if (size === this.offset) return;
    const fd = fs.openSync(this.file, "r");
    const buf = Buffer.alloc(size - this.offset);
    fs.readSync(fd, buf, 0, buf.length, this.offset);
    fs.closeSync(fd);
    this.offset = size;
    const lines = (this.rest + buf.toString("utf8")).split("\n");
    this.rest = lines.pop() ?? "";
    for (const l of lines) { if (l.trim()) try { this.entry(JSON.parse(l)); } catch {} }
  }

  private lessonId(id: string | null, t: number) { return id ? renumber(id, t, this.applied) : id; }

  private entry(e: any) {
    const t = Date.parse(e.timestamp);
    if (e.type === "compaction") {
      this.compactions.push({ t, before: Number(e.tokensBefore) || 0, summaryChars: String(e.summary ?? "").length, cost: e.usage?.cost?.total ?? 0 });
      return;
    }
    if (e.type !== "message") return;
    const m = e.message ?? {};
    if (m.role === "user") {
      const c = classify(textOf(m.content));
      this.cur = { t, kind: c.kind, lesson: this.lessonId(c.lesson, t), label: c.label.slice(0, 140), firstMs: null, totalMs: null, calls: 0, tools: 0, toolMs: 0, toolErrors: 0, ctx: 0, cost: 0 };
      this.prompts.push(this.cur);
    } else if (m.role === "assistant") {
      const u = m.usage ?? {};
      const p = this.cur;
      const call: Call = {
        t, ctx: (u.input ?? 0) + (u.cacheRead ?? 0) + (u.cacheWrite ?? 0), cached: u.cacheRead ?? 0, out: u.output ?? 0, cost: u.cost?.total ?? 0,
        ms: m.durationMs ?? null, stop: m.stopReason ?? "", lesson: p?.lesson ?? null, kind: p?.kind ?? "other",
      };
      if (m.errorMessage) { call.error = String(m.errorMessage).slice(0, 300); this.errors.push({ t, where: "model call", message: call.error }); }
      this.calls.push(call);
      for (const c of Array.isArray(m.content) ? m.content : []) if (c.type === "toolCall" && c.id) this.pendingTool.set(c.id, t);
      if (p) {
        p.calls++;
        if (call.ctx) p.ctx = call.ctx;
        p.cost += call.cost;
        // The first thing the learner sees: text, or a page tool (a figure, a question, a settled turn).
        const visible = (Array.isArray(m.content) ? m.content : []).some((c: any) => (c.type === "text" && c.text?.trim()) || (c.type === "toolCall" && PAGE_TOOLS.has(c.name)));
        if (p.firstMs === null && visible) p.firstMs = t - p.t;
        p.totalMs = t - p.t;
        if (call.error) p.error = call.error;
        else if (m.stopReason !== "error") delete p.error; // a retry that went through
      }
    } else if (m.role === "toolResult") {
      const name = m.toolName ?? "?";
      const st = this.tools.get(name) ?? { n: 0, errors: 0, ms: [] };
      const ms = Number(m.durationMs ?? (this.pendingTool.has(m.toolCallId) ? t - this.pendingTool.get(m.toolCallId)! : 0));
      const isErr = m.isError === true;
      st.n++; st.ms.push(ms); if (isErr) st.errors++;
      this.tools.set(name, st);
      this.pendingTool.delete(m.toolCallId);
      if (isErr) this.errors.push({ t, where: `tool ${name}`, message: textOf(m.content).slice(0, 300) });
      if (this.cur) { this.cur.tools++; this.cur.toolMs += ms; if (isErr) this.cur.toolErrors++; }
    }
  }
}

const quantile = (xs: number[], q: number) => {
  if (!xs.length) return null;
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.floor(q * s.length))];
};

function run(cmd: string, args: string[]): Promise<string | null> {
  return new Promise((res) => execFile(cmd, args, { timeout: 5000 }, (err, out) => res(err ? null : String(out))));
}

function dirSize(dir: string): number {
  let total = 0;
  const walk = (d: string) => {
    let ents: fs.Dirent[];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of ents) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.isFile()) { try { total += fs.statSync(p).size; } catch {} }
    }
  };
  walk(dir);
  return total;
}

export class Admin {
  private logs = new Map<string, SessionLog>();
  private started = Date.now();
  private machineCache: { at: number; value: any } | null = null;
  private workSize: { at: number; bytes: number } | null = null;
  private metricsFile = learnerPath("metrics.jsonl");

  constructor(private tutor: Tutor) {}

  /** Append one event the session log doesn't keep. */
  record(m: Record<string, unknown>) {
    try { fs.appendFileSync(this.metricsFile, JSON.stringify({ t: Date.now(), ...m }) + "\n"); } catch {}
  }

  private metrics(): any[] {
    if (!fs.existsSync(this.metricsFile)) return [];
    return fs.readFileSync(this.metricsFile, "utf8").split("\n").filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  }

  private sessionLogs(): SessionLog[] {
    const dir = learnerPath("sessions", "main");
    const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => f.endsWith(".jsonl")).sort() : [];
    const applied = migrationsApplied();
    return files.map((f) => {
      const p = path.join(dir, f);
      let l = this.logs.get(p);
      if (!l) { l = new SessionLog(p, applied); this.logs.set(p, l); }
      l.refresh();
      return l;
    });
  }

  private async machine() {
    if (this.machineCache && Date.now() - this.machineCache.at < 5000) return this.machineCache.value;
    const smi = await run("nvidia-smi", ["--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"]);
    const gpus = (smi ?? "").trim().split("\n").filter(Boolean).map((l) => {
      const [name, used, total, util] = l.split(",").map((x) => x.trim());
      return { name, memUsedMiB: Number(used), memTotalMiB: Number(total), utilPct: Number(util) };
    });
    let disk: { freeBytes: number; totalBytes: number } | null = null;
    try { const s = fs.statfsSync(config.learnerDir); disk = { freeBytes: s.bavail * s.bsize, totalBytes: s.blocks * s.bsize }; } catch {}
    if (!this.workSize || Date.now() - this.workSize.at > 60000) this.workSize = { at: Date.now(), bytes: dirSize(learnerPath("work")) };
    const value = { gpus, gpuError: smi === null ? "nvidia-smi failed" : null, disk, workBytes: this.workSize.bytes, rssBytes: process.memoryUsage().rss };
    this.machineCache = { at: Date.now(), value };
    return value;
  }

  async report() {
    const logs = this.sessionLogs();
    const calls = logs.flatMap((l) => l.calls);
    const prompts = logs.flatMap((l) => l.prompts);
    const compactions = logs.flatMap((l) => l.compactions);
    const errors = logs.flatMap((l) => l.errors);
    const tools = new Map<string, ToolStat>();
    for (const l of logs) for (const [k, v] of l.tools) {
      const st = tools.get(k) ?? { n: 0, errors: 0, ms: [] };
      st.n += v.n; st.errors += v.errors; st.ms.push(...v.ms);
      tools.set(k, st);
    }
    const metrics = this.metrics();
    const margin = metrics.filter((m) => m.kind === "margin");
    for (const m of metrics) if ((m.kind === "retry" || m.kind === "compaction_end") && m.error) errors.push({ t: m.t, where: m.kind === "retry" ? `retry ${m.attempt}/${m.of}` : "compaction", message: m.error });
    for (const m of margin) if (m.error) errors.push({ t: m.t, where: "margin call", message: m.error });
    errors.sort((a, b) => a.t - b.t);

    // What the learner waits for: anything they did (a reply, opening or returning to a lesson).
    const learnerKinds = new Set(["reply", "open", "return"]);
    const waited = prompts.filter((p) => learnerKinds.has(p.kind) && p.firstMs !== null);
    const recentWait = waited.slice(-50);
    const day = 24 * 3600 * 1000;
    const now = Date.now();
    const sum = (xs: number[]) => xs.reduce((a, b) => a + b, 0);
    const todayStart = new Date(); todayStart.setHours(0, 0, 0, 0);

    const lessons = new Map<string, { prompts: number; calls: number; cost: number; waits: number[]; tools: number; maxCtx: number }>();
    for (const p of prompts) {
      if (!p.lesson) continue;
      const s = lessons.get(p.lesson) ?? { prompts: 0, calls: 0, cost: 0, waits: [], tools: 0, maxCtx: 0 };
      s.prompts++; s.calls += p.calls; s.cost += p.cost; s.tools += p.tools; s.maxCtx = Math.max(s.maxCtx, p.ctx);
      if (learnerKinds.has(p.kind) && p.firstMs !== null) s.waits.push(p.firstMs);
      lessons.set(p.lesson, s);
    }
    for (const m of margin) {
      const s = lessons.get(m.lesson) ?? { prompts: 0, calls: 0, cost: 0, waits: [], tools: 0, maxCtx: 0 };
      s.calls++; s.cost += m.cost ?? 0;
      lessons.set(m.lesson, s);
    }

    const cached = calls.slice(-50);
    return {
      now, startedAt: this.started,
      tutor: this.tutor.status(),
      totals: {
        calls: calls.length, prompts: prompts.length,
        cost: sum(calls.map((c) => c.cost)) + sum(compactions.map((c) => c.cost)) + sum(margin.map((m) => m.cost ?? 0)),
        costToday: sum(calls.filter((c) => c.t >= todayStart.getTime()).map((c) => c.cost)) + sum(margin.filter((m) => m.t >= todayStart.getTime()).map((m) => m.cost ?? 0)),
        marginCalls: margin.length, marginCost: sum(margin.map((m) => m.cost ?? 0)),
        firstCall: calls[0]?.t ?? null,
        errors24h: errors.filter((e) => now - e.t < day).length,
        // Share of the prompt read from the provider's cache, last 50 calls: low means every call pays full price.
        cacheShare: (() => { const xs = cached.filter((c) => c.ctx); return xs.length ? sum(xs.map((c) => c.cached)) / sum(xs.map((c) => c.ctx)) : null; })(),
      },
      wait: {
        n: recentWait.length,
        firstP50: quantile(recentWait.map((p) => p.firstMs!), 0.5), firstP90: quantile(recentWait.map((p) => p.firstMs!), 0.9),
        totalP50: quantile(recentWait.map((p) => p.totalMs!), 0.5), totalP90: quantile(recentWait.map((p) => p.totalMs!), 0.9),
      },
      // Context size at every model call, for the chart (main thread only).
      context: calls.filter((c) => c.ctx > 0).map((c) => [c.t, c.ctx, c.lesson]),
      compactions,
      prompts: prompts.slice(-200).reverse(),
      lessons: [...lessons].map(([id, s]) => ({ id, prompts: s.prompts, calls: s.calls, cost: s.cost, tools: s.tools, maxCtx: s.maxCtx, waitP50: quantile(s.waits, 0.5), waitMax: s.waits.length ? Math.max(...s.waits) : null }))
        .sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true })),
      tools: [...tools].map(([name, s]) => ({ name, n: s.n, errors: s.errors, msP50: quantile(s.ms, 0.5), msP90: quantile(s.ms, 0.9), msMax: s.ms.length ? Math.max(...s.ms) : null, msTotal: sum(s.ms) }))
        .sort((a, b) => b.msTotal - a.msTotal),
      errors: errors.slice(-100).reverse(),
      retries: metrics.filter((m) => m.kind === "retry").slice(-50).reverse(),
      margin: margin.slice(-50).reverse(),
      // One thread per module: when each started, and the profile the threads hand on.
      threads: metrics.filter((m) => m.kind === "thread").map((m) => ({ t: m.t, from: m.from, to: m.to })),
      profile: (() => { try { const p = learnerPath("profile.md"); return { text: fs.readFileSync(p, "utf8"), at: fs.statSync(p).mtimeMs }; } catch { return null; } })(),
      machine: await this.machine(),
    };
  }
}
