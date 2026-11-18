// The tutor: one main pi session per learner, forks for margin threads.
// The tutor's context is loaded explicitly (SYSTEM.md + the course's skills);
// pi's discovery of AGENTS.md/CLAUDE.md, extensions and templates is off, so
// nothing from this repo's development setup reaches it.
import fs from "node:fs";
import path from "node:path";
import { Type } from "typebox";
import YAML from "yaml";
import {
  createAgentSession, createExtensionRuntime, defineTool, loadSkillsFromDir, ModelRuntime,
  SessionManager, SettingsManager, type AgentSession, type ResourceLoader, type ToolDefinition,
} from "@earendil-works/pi-coding-agent";
import { config, learnerPath } from "./config.ts";
import type { Course, Lesson } from "./content.ts";
import { modelsPath } from "./endpoint.ts";
import { Recorder } from "./recorder.ts";
import { QUEUE, Store, type FigureOnPage, type Pointer, type Thread } from "./state.ts";

// drafts: text the tutor is streaming right now, keyed "turn:<lesson>/<turn>" or "thread:<id>".
// turn: the Your turn ("lesson/turn") the main thread is answering right now, so the page can say it is still working there.
export type Activity = { main: string | null; turn: string | null; threads: Record<string, boolean>; drafts: Record<string, string> };

/** Text blocks of an assistant message so far (thinking and tool calls excluded). */
const textOf = (m: any) => (Array.isArray(m?.content) ? m.content : []).filter((c: any) => c.type === "text").map((c: any) => c.text).join("").trim();

const text = (t: string) => ({ content: [{ type: "text" as const, text: t }], details: {} });

export class Tutor {
  private runtime!: ModelRuntime;
  private model!: any;
  private main!: AgentSession;
  private chain: Promise<unknown> = Promise.resolve();
  private margins = new Map<string, AgentSession>();
  private pendingNotes: string[] = [];
  private spokeIn = new Set<string>(); // turn ids the tutor addressed during the current prompt
  private promptLesson: string | null = null; // the lesson the current main prompt is about
  private streamTurn: string | null = null; // the turn whose conversation the current main prompt's text goes to
  // The main thread belongs to one module (learner/thread.json). Opening a lesson of a later module
  // starts a new thread, seeded with the learner profile the old one wrote (see rotate()).
  private thread: { module: string; startedAt: number } | null = null;
  private rotating = false;
  recorder = new Recorder();
  activity: Activity = { main: null, turn: null, threads: {}, drafts: {} };
  onActivity: () => void = () => {};
  onNote: (n: { kind: string; summary: string }) => void = () => {};
  /** Events the session log doesn't keep (retries, compactions as they happen, margin calls), for the admin page. */
  onMetric: (m: Record<string, unknown>) => void = () => {};

  constructor(private course: Course, private store: Store, private lessonTurns: Map<string, string[]>) {}

  async init() {
    this.runtime = await ModelRuntime.create({
      authPath: path.join(config.learnerDir, ".pi-auth.json"),
      modelsPath: modelsPath(),
    });
    this.model = this.runtime.getModel(config.provider, config.model);
    if (!this.model) throw new Error(`model ${config.provider}/${config.model} not found (tutor/pi-agent/models.json, or learner/endpoint.json from /setup)`);
    const pyBin = config.pythonBin || path.join(config.cuphotonDir, ".venv", "bin");
    if (fs.existsSync(pyBin) && !process.env.PATH?.startsWith(pyBin)) process.env.PATH = `${pyBin}:${process.env.PATH}`;
    if (config.offline) process.env.PI_OFFLINE = "1";
    fs.mkdirSync(learnerPath("sessions", "main"), { recursive: true });
    this.main = await this.makeSession(SessionManager.continueRecent(config.learnerDir, learnerPath("sessions", "main")), "main");
    try { this.thread = JSON.parse(fs.readFileSync(learnerPath("thread.json"), "utf8")); } catch {}
    if (!this.thread) {
      // A thread from before threads were per module: it belongs to the module of the learner's last exchange
      // in a Your turn (not the current lesson: they may only be browsing).
      let lastAt = 0, lastLesson = this.store.page.current ?? "";
      for (const [id, l] of Object.entries(this.store.page.lessons))
        for (const t of Object.values(l.turns)) for (const msg of t.log) if (msg.at > lastAt) { lastAt = msg.at; lastLesson = id; }
      const m = this.moduleOf(lastLesson);
      if (m) this.saveThread({ module: m, startedAt: Date.now() });
    }
  }

  // ---------- one thread per module ----------

  private moduleOf(lessonId: string) { return this.course.modules.find((m) => m.lessons.some((l) => l.id === lessonId))?.id ?? null; }
  private moduleIndex(id: string) { return this.course.modules.findIndex((m) => m.id === id); }
  private saveThread(t: { module: string; startedAt: number }) {
    this.thread = t;
    fs.writeFileSync(learnerPath("thread.json"), JSON.stringify(t, null, 1));
  }
  private moduleDone(moduleId: string) {
    const m = this.course.modules.find((x) => x.id === moduleId);
    return !!m && m.lessons.every((l) => l.turnIds.every((t) => this.store.lesson(l.id).turns[t]?.status === "settled"));
  }

  /** Before a prompt about `lessonId`: a later module gets a new thread; an earlier one gets a pointer to its conversations. */
  private async ensureThread(lessonId: string) {
    const m = this.moduleOf(lessonId);
    if (!m || !this.thread || m === this.thread.module) return;
    if (this.moduleIndex(m) > this.moduleIndex(this.thread.module)) return this.rotate(m);
    this.pendingNotes.push(`[page] Lesson ${lessonId} is in Module ${m}, which an earlier thread of yours taught. Its conversations are in \`page.json\` (\`lessons["${lessonId}"].turns\`); read them if you need what was said.`);
  }

  private async rotate(next: string) {
    const prev = this.thread!.module;
    const prevTitle = this.course.modules.find((x) => x.id === prev)?.title ?? "";
    this.rotating = true;
    try {
      // 1. The old thread writes down what the next one should know about the learner.
      try {
        await this.main.prompt([
          `[page] The learner is moving on from Module ${prev} "${prevTitle}" to Module ${next}. Your next prompt starts a new thread`,
          `that won't see this conversation. Update the learner profile, \`${learnerPath("profile.md")}\`, as described`,
          'under "The learner profile" in your instructions: read it if it exists, then rewrite it whole with what this',
          "module showed, in under 700 words (cut what would change your teaching least). This conversation may use older",
          "lesson ids, from before the course was reordered: name every lesson by its id in the course outline of your",
          'instructions and its title, e.g. "8.3 Every row on the GPU". Use write. Don\'t use ask, settle or reveal, and say',
          "nothing on the page.",
        ].join("\n"));
      } catch (e: any) { console.error("[tutor] profile update failed:", e?.message ?? e); }
      // 2. A new thread, told who the learner is and where they are.
      this.main = await this.makeSession(SessionManager.create(config.learnerDir, learnerPath("sessions", "main")), "main");
      for (const st of Object.values(this.store.page.lessons)) st.briefed = false; // this thread hasn't read any lesson yet
      this.store.save(this.lessonTurns);
      this.saveThread({ module: next, startedAt: Date.now() });
      this.pendingNotes.unshift(this.threadSeed(next));
      this.onMetric({ kind: "thread", from: prev, to: next });
    } finally { this.rotating = false; }
  }

  /** The first thing a new thread reads: the profile, the learner's progress, and the course terms they've met. */
  private threadSeed(moduleId: string) {
    const mod = this.course.modules.find((x) => x.id === moduleId)!;
    let profile = "(none yet)";
    try { profile = fs.readFileSync(learnerPath("profile.md"), "utf8").trim() || profile; } catch {}
    const progress = this.course.modules.filter((m) => this.moduleIndex(m.id) < this.moduleIndex(moduleId)).map((m) => {
      const ls = m.lessons.map((l) => {
        const st = this.store.page.lessons[l.id];
        if (!st?.visited) return `${l.id} not visited`;
        const open = l.turnIds.filter((t) => st.turns[t]?.status !== "settled");
        return open.length ? `${l.id} visited, turns open: ${open.join(", ")}` : `${l.id} done`;
      });
      return `- Module ${m.id} "${m.title}": ${ls.join("; ")}`;
    }).join("\n");
    // Course terms introduced before this module (vocabulary.yaml's introduce_at), computed, not remembered.
    const firstLesson = mod.lessons[0]?.id;
    const cut = firstLesson ? this.course.order.indexOf(firstLesson) : this.course.order.length;
    let terms: string[] = [];
    try {
      const voc = YAML.parse(fs.readFileSync(path.join(config.courseDir, "vocabulary.yaml"), "utf8"));
      terms = (voc.terms ?? []).filter((t: any) => {
        const at = String(t.introduce_at ?? "").match(/\d+\.\d+/)?.[0];
        const i = at ? this.course.order.indexOf(at) : -1;
        return i >= 0 && i < cut;
      }).map((t: any) => String(t.term));
    } catch {}
    return [
      `[page] This is a new thread of yours, for Module ${mod.id} "${mod.title}". Earlier threads taught the modules before it;`,
      "what they left you is below. Earlier conversations are in `page.json` (`lessons[\"<id>\"].turns[\"<turn>\"].log`, and",
      "`threads` for margin trips): read one when a lesson builds on it, rather than guessing what was said.",
      "", "<learner-profile file=\"profile.md\">", profile, "</learner-profile>",
      "", "<progress>", progress || "(this is the first module)", "</progress>",
      "", "<terms-introduced>", terms.length ? terms.join("; ") : "(none yet)", "</terms-introduced>",
      "These course terms were introduced in earlier modules. The profile says which ones the learner owns and which aren't anchored yet.",
    ].join("\n");
  }

  // ---------- context ----------

  private systemPrompt(kind: "main" | "margin") {
    const base = fs.readFileSync(path.join(config.tutorDir, "SYSTEM.md"), "utf8");
    const outline = this.course.modules.map((u) =>
      `- Module ${u.id} · ${u.title}\n` + u.lessons.map((l) => `  - ${l.id} ${l.title} (turns: ${l.turnIds.join(", ") || "none"})`).join("\n")).join("\n");
    const env = [
      "## Environment",
      `- Learner workspace (your cwd): ${config.learnerDir}`,
      `- Course files (read-only): ${config.courseDir} — vocabulary.yaml, concepts.yaml, misconceptions.md, modules/*/<lesson>/lesson.md and tutor.md`,
      `- cuPhoton checkout, pinned at ${this.course.commit}: ${config.cuphotonDir}`,
      `- Python environments: \`python\` on your PATH is cuPhoton's CPU-only environment (no CuPy, CPU PyTorch), used for Modules 00–02.`,
      `  The GPU environment, with cuPhoton's gpu extra, is ${config.gpuPythonBin}: call ${path.join(config.gpuPythonBin, "python")} (and ${path.join(config.gpuPythonBin, "cuphoton")}) by full path for GPU work, from Module 03 on.`,
      "", "## The course", outline,
    ].join("\n");
    const margin = kind === "margin" ? "\n\n" + [
      "## You are in the margin",
      "This is a side conversation the learner opened from the margin (\"Ask about anything on this page\"),",
      "forked from your main thread. Answer in plain text: short, one idea, at most one question back.",
      "There are no page tools here. You may read files and run quick commands, but don't put anything on the page.",
      "\"About:\" says what \"this\" refers to; you still see the whole lesson.",
      "Never answer an open Your turn here, nor anything a hold-back guards: say we come back to it in that lesson, and",
      "offer something that helps them think instead. If they ask you to explain something a turn will test, give a",
      "question that narrows where to look (hint rung a), no more.",
    ].join("\n") : "";
    return `${base}\n\n${env}${margin}`;
  }

  private loader(kind: "main" | "margin"): ResourceLoader {
    const skills = loadSkillsFromDir({ dir: path.join(config.tutorDir, "skills"), source: "course" });
    const sys = this.systemPrompt(kind);
    return {
      getExtensions: () => ({ extensions: [], errors: [], runtime: createExtensionRuntime() }),
      getSkills: () => skills,
      getPrompts: () => ({ prompts: [], diagnostics: [] }),
      getThemes: () => ({ themes: [], diagnostics: [] }),
      getAgentsFiles: () => ({ agentsFiles: [] }),
      getSystemPrompt: () => sys,
      getSystemPromptSource: () => undefined,
      getAppendSystemPrompt: () => [],
      getAppendSystemPromptSources: () => [],
      extendResources: () => {},
      reload: async () => {},
    };
  }

  private async makeSession(sm: SessionManager, kind: "main" | "margin"): Promise<AgentSession> {
    const { session } = await createAgentSession({
      cwd: config.learnerDir,
      agentDir: path.join(config.tutorDir, "pi-agent"),
      modelRuntime: this.runtime,
      model: this.model,
      thinkingLevel: config.thinking,
      resourceLoader: this.loader(kind),
      tools: kind === "main" ? ["read", "bash", "edit", "write", "show_figure", "ask", "settle", "reveal", "file_feedback"] : ["read", "bash"],
      customTools: kind === "main" ? this.pageTools() : [],
      sessionManager: sm,
      settingsManager: SettingsManager.inMemory({ compaction: { enabled: true }, retry: { enabled: true, maxRetries: 4 } } as any),
    });
    if (kind === "main") {
      session.subscribe((ev: any) => {
        if (ev.type === "auto_retry_start") this.onMetric({ kind: "retry", attempt: ev.attempt, of: ev.maxAttempts, delayMs: ev.delayMs, error: String(ev.errorMessage ?? "").slice(0, 300) });
        else if (ev.type === "auto_retry_end") this.onMetric({ kind: "retry_end", ok: ev.success, attempt: ev.attempt, error: ev.finalError ? String(ev.finalError).slice(0, 300) : undefined });
        else if (ev.type === "compaction_start") this.onMetric({ kind: "compaction_start", reason: ev.reason });
        else if (ev.type === "compaction_end") this.onMetric({ kind: "compaction_end", reason: ev.reason, aborted: ev.aborted, error: ev.errorMessage });
        if (ev.type === "tool_execution_start") {
          this.recorder.start(ev.toolCallId, ev.toolName, ev.args);
          const label = ev.toolName === "bash" ? "Running" : ev.toolName === "show_figure" ? "Placing a figure" : ev.toolName === "read" ? "Reading" : "Working";
          // Preparing ahead, and the old thread writing the profile at a module change, are invisible to the
          // learner. (Rotation can run from prepareAhead before `background` is set; labelling it here left the
          // page saying "Working" after the module was done, since nothing cleared it.)
          if (!this.background && !this.rotating) this.setMain(label);
        } else if (ev.type === "tool_execution_end") {
          this.recorder.end(ev.toolCallId, ev.isError, ev.durationMs);
        } else if (this.streamTurn && ev.type === "message_update" && ev.assistantMessageEvent?.type === "text_delta") {
          // In a Your-turn conversation the tutor's text is its reply: stream it into the turn.
          this.activity.drafts[`turn:${this.streamTurn}`] = textOf(ev.message);
          this.onActivity();
        } else if (this.streamTurn && ev.type === "message_end" && ev.message?.role === "assistant") {
          const said = textOf(ev.message);
          delete this.activity.drafts[`turn:${this.streamTurn}`];
          if (said) {
            const [lid, tid] = this.streamTurn.split("/");
            this.store.turn(lid, tid).log.push({ who: "tutor", text: said, at: Date.now() });
            this.spokeIn.add(this.streamTurn);
            this.store.save(this.lessonTurns);
          } else this.onActivity();
        }
      });
    }
    return session;
  }

  // ---------- page tools ----------

  private pageTools(): ToolDefinition[] {
    const s = this.store;
    const resolveTurn = (raw: string) => {
      const id = raw.includes("/") ? raw : `${this.promptLesson ?? s.page.current}/${raw}`;
      const f = s.findTurn(id);
      if (!f) throw new Error(`unknown turn ${id}`);
      const lesson = this.course.lessons.get(f.lessonId);
      const tid = id.includes("/") ? id.split("/")[1] : id;
      if (!lesson?.turnIds.includes(tid)) throw new Error(`lesson ${f.lessonId} has no Your turn "${tid}". Its turns: ${lesson?.turnIds.join(", ")}`);
      return { ...f, tid, lesson };
    };
    return [
      defineTool({
        name: "show_figure", label: "Show figure", executionMode: "sequential",
        description: "Place an image from the learner workspace on the page: into a lesson slot (slot) or into a Your-turn conversation (turn_id, as lesson/turn). Its run record is attached automatically.",
        parameters: Type.Object({
          path: Type.String({ description: "Image path, relative to the learner workspace (e.g. work/00/0.1_toy_sky.png)" }),
          title: Type.Optional(Type.String({ description: "Short title. Defaults to the slot's authored title." })),
          caption: Type.Optional(Type.String({ description: "One line: what is shown, and anything the display does to the data." })),
          slot: Type.Optional(Type.String({ description: "Slot id in the current lesson, from its :::slot directive" })),
          turn_id: Type.Optional(Type.String({ description: "lesson/turn, to place it in that conversation" })),
        }),
        execute: async (_id, p) => {
          const abs = path.resolve(config.learnerDir, p.path);
          if (!abs.startsWith(config.learnerDir)) throw new Error(`not in the workspace: ${p.path}`);
          // A figure made by a bash call in the same batch may still be being written: give it a moment.
          for (let i = 0; i < 40 && !fs.existsSync(abs); i++) await new Promise((r) => setTimeout(r, 250));
          if (!fs.existsSync(abs)) throw new Error(`no such file in the workspace: ${p.path}`);
          if (!/\.(png|jpe?g|svg|gif|webp)$/i.test(abs)) throw new Error("show_figure takes an image (png, jpg, svg, gif, webp)");
          const rel = path.relative(config.learnerDir, abs);
          const fig: FigureOnPage = { id: `${rel}@${fs.statSync(abs).mtimeMs}`, src: `/workspace/${rel}?v=${Math.round(fs.statSync(abs).mtimeMs)}`, title: p.title ?? "", caption: p.caption ?? "", run: this.recorder.recordFor(rel) };
          if (p.turn_id) {
            const t = resolveTurn(p.turn_id);
            t.turn.log.push({ who: "tutor", text: "", figure: fig, at: Date.now() });
            this.spokeIn.add(`${t.lessonId}/${t.tid}`);
          } else {
            const lid = p.slot?.includes("/") ? p.slot.split("/")[0] : this.promptLesson ?? s.page.current;
            const slotId = p.slot?.includes("/") ? p.slot.split("/")[1] : p.slot;
            const lesson = lid ? this.course.lessons.get(lid) : undefined;
            const slot = slotId ?? lesson?.slotIds.find((x) => !s.lesson(lid!).slots[x]);
            if (!lesson || !slot || !lesson.slotIds.includes(slot)) throw new Error(`lesson ${lid} has no slot ${p.slot}; its slots: ${lesson?.slotIds.join(", ") || "none"}. Use turn_id to put it in a conversation.`);
            const part = lesson.parts.find((x) => x.kind === "slot" && x.id === slot) as any;
            fig.title ||= part?.title ?? "";
            fig.caption ||= part?.caption ?? "";
            s.lesson(lesson.id).slots[slot] = fig;
          }
          s.save(this.lessonTurns);
          return text(`Shown${fig.run ? ` with run record (${fig.run.by}, ${fig.run.device}, ${fig.run.seconds.toFixed(1)} s)` : " (no run record found: was it made by a bash run in this session?)"}.`);
        },
      }),
      defineTool({
        name: "ask", label: "Ask", executionMode: "sequential",
        description: "Post your line in a Your-turn conversation. One short message, at most one question.",
        parameters: Type.Object({
          turn_id: Type.String({ description: "lesson/turn, e.g. 0.2/what-changed" }),
          text: Type.String(),
          hint_rung: Type.Optional(Type.String({ description: "a, b, c or d when this line is a hint" })),
        }),
        execute: async (_id, p) => {
          const t = resolveTurn(p.turn_id);
          if (t.turn.status === "settled") throw new Error("that turn is settled");
          t.turn.log.push({ who: "tutor", text: p.text, at: Date.now() });
          if (p.hint_rung) t.turn.hints.push(p.hint_rung);
          this.spokeIn.add(`${t.lessonId}/${t.tid}`);
          s.save(this.lessonTurns);
          return text("Posted.");
        },
      }),
      defineTool({
        name: "settle", label: "Settle", executionMode: "sequential",
        description: "Mark a Your turn passed. The summary is one line, in the learner's words where possible; the turn folds to it with a check mark.",
        parameters: Type.Object({
          turn_id: Type.String(),
          summary: Type.String(),
          misconceptions: Type.Optional(Type.Array(Type.String(), { description: "M- ids observed in this turn (resolved or not)" })),
        }),
        execute: async (_id, p) => {
          const t = resolveTurn(p.turn_id);
          t.turn.status = "settled";
          t.turn.summary = p.summary;
          t.turn.misconceptions.push(...(p.misconceptions ?? []));
          this.spokeIn.add(`${t.lessonId}/${t.tid}`);
          s.save(this.lessonTurns);
          const left = t.lesson.turnIds.filter((x) => s.lesson(t.lessonId).turns[x]?.status !== "settled");
          return text(left.length
            ? `Settled. The page now opens the next turn, ${left[0]}, with its own question. Finish your reply about this one and stop: don't introduce or ask the next turn.`
            : `Settled. All turns in ${t.lessonId} are settled; reveal("${t.lessonId}") when ready.`);
        },
      }),
      defineTool({
        name: "reveal", label: "Reveal", executionMode: "sequential",
        description: "Show a lesson's closure (We found / Which raises). Only once all its Your turns are settled.",
        parameters: Type.Object({ lesson_id: Type.String() }),
        execute: async (_id, p) => {
          const lesson = this.course.lessons.get(p.lesson_id);
          if (!lesson) throw new Error(`no lesson ${p.lesson_id}`);
          const open = lesson.turnIds.filter((x) => s.lesson(lesson.id).turns[x]?.status !== "settled");
          if (open.length) throw new Error(`not yet: open turns ${open.join(", ")}`);
          s.lesson(lesson.id).revealed = true;
          s.save(this.lessonTurns);
          return text("Revealed.");
        },
      }),
      defineTool({
        name: "file_feedback", label: "File feedback", executionMode: "sequential",
        description: "Send a short structured note to the course authors (see the report-feedback skill). The learner sees every note.",
        parameters: Type.Object({
          kind: Type.Union(["novel_misconception", "stuck_unresolved", "content_error", "tutor_error", "env_failure", "frustration", "delight"].map((k) => Type.Literal(k))),
          summary: Type.String(),
          lesson: Type.Optional(Type.String()),
          learner_words: Type.Optional(Type.String()),
          tried: Type.Optional(Type.String()),
          resolved: Type.Optional(Type.String()),
          suggestion: Type.Optional(Type.String()),
        }),
        execute: async (_id, p) => {
          const ev = {
            ts: new Date().toISOString(), ...p, lesson: p.lesson ?? s.page.current,
            tutor_model: `${config.provider}/${config.model}`, course_commit: this.course.commit,
          };
          fs.appendFileSync(QUEUE(), JSON.stringify(ev) + "\n");
          if (p.kind === "novel_misconception") s.addObservation(p.summary);
          this.onNote({ kind: p.kind, summary: p.summary });
          if (s.page.feedbackConsent && config.feedbackUrl) {
            fetch(config.feedbackUrl, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(ev) }).catch(() => {});
          }
          return text(`Queued${s.page.feedbackConsent ? " and sent" : " (sent only if the learner agrees)"}. The learner sees it in the margin.`);
        },
      }),
    ] as ToolDefinition[];
  }

  // ---------- main thread ----------

  /** What the admin page shows about the live tutor. */
  status() {
    const m = this.main;
    let reserve = 16384;
    try { reserve = m.settingsManager.getCompactionReserveTokens(this.model); } catch {}
    return {
      provider: config.provider, model: config.model, thinking: config.thinking,
      contextWindow: this.model?.contextWindow ?? null, compactAt: (this.model?.contextWindow ?? 0) - reserve,
      usage: m?.getContextUsage() ?? null,
      busy: this.activity.main, preparing: this.background, queued: this.foreground,
      streaming: m?.isStreaming ?? false, compacting: m?.isCompacting ?? false, retrying: m?.isRetrying ?? false,
      margins: this.margins.size, thread: this.thread, sessionFile: m?.sessionManager.getSessionFile() ?? null,
    };
  }

  private setMain(label: string | null) { this.activity.main = label; this.onActivity(); }

  private foreground = 0; // learner-driven prompts queued or running
  private background: string | null = null; // lesson being prepared ahead, while it runs
  private interrupted: string | null = null; // a lesson whose preparation the learner just interrupted

  private enqueue(lessonId: string, label: string, msg: string, after?: (finalText: string) => void, streamTurn: string | null = null) {
    this.foreground++;
    // Anything the learner does comes first: interrupt a lesson being prepared ahead (it's retried later).
    if (this.background && !this.rotating) { this.interrupted = this.background; this.main.abort().catch(() => {}); }
    const run = async () => {
      if (!this.thread) { const m = this.moduleOf(lessonId); if (m) this.saveThread({ module: m, startedAt: Date.now() }); } // a new learner's first prompt
      if (!this.rotating && this.thread && this.moduleOf(lessonId) !== this.thread.module) { this.setMain("Starting the module"); await this.ensureThread(lessonId); }
      this.promptLesson = lessonId;
      this.streamTurn = streamTurn;
      this.activity.turn = streamTurn;
      this.setMain(label);
      this.spokeIn.clear();
      const notes = this.pendingNotes.splice(0);
      if (this.interrupted) {
        notes.push(`[page] Preparing lesson ${this.interrupted} was interrupted by the learner. Drop it for now (you'll be asked again later) and deal only with what follows.`);
        this.interrupted = null;
      }
      const full = (notes.length ? notes.join("\n") + "\n\n" : "") + msg;
      try {
        await this.main.prompt(full);
        after?.(this.main.getLastAssistantText() ?? "");
      } catch (e: any) {
        console.error("[tutor] main prompt failed:", e?.message ?? e);
        after?.("");
      } finally {
        this.streamTurn = null;
        this.activity.turn = null;
        this.activity.drafts = Object.fromEntries(Object.entries(this.activity.drafts).filter(([k]) => !k.startsWith("turn:")));
        this.foreground--;
        this.setMain(null);
        if (!this.foreground) this.prepareAhead();
      }
    };
    this.chain = this.chain.then(run, run);
    return this.chain;
  }

  /** Slots the tutor fills as soon as a lesson opens: those placed before its first Your turn. */
  private openingSlots(lesson: Lesson) {
    const firstTurn = lesson.parts.findIndex((p) => p.kind === "turn");
    return lesson.parts.filter((p, i) => p.kind === "slot" && (firstTurn < 0 || i < firstTurn)).map((p: any) => p.id as string);
  }

  private briefing(lesson: Lesson) {
    return ["<lesson.md>", lesson.source.trim(), "</lesson.md>", "", "<tutor.md>", lesson.tutorNotes.trim(), "</tutor.md>"].join("\n");
  }

  /** While the learner works, make the next lesson's opening figures so they're there when it opens.
   *  Runs only when nothing else is queued; any learner action interrupts it. */
  private prepareAhead() {
    const cur = this.store.page.current;
    const order = this.course.order;
    const next = cur ? this.course.lessons.get(order[order.indexOf(cur) + 1]) : undefined;
    if (!next) return;
    const st = this.store.lesson(next.id);
    const missing = this.openingSlots(next).filter((x) => !st.slots[x]);
    if (st.visited || !missing.length) return;
    // The next lesson opens a new module, so a new thread: start it only once this module is finished.
    const nextModule = this.moduleOf(next.id);
    if (this.thread && nextModule !== this.thread.module && !this.moduleDone(this.thread.module)) return;
    const run = async () => {
      if (this.foreground || st.visited) return;
      if (this.thread && nextModule && nextModule !== this.thread.module) await this.ensureThread(next.id);
      if (this.foreground) return;
      this.background = next.id;
      this.promptLesson = next.id;
      this.spokeIn.clear();
      const notes = this.pendingNotes.splice(0);
      const msg = [
        `[page] Prepare lesson ${next.id} "${next.title}" ahead: the learner is still on ${cur} and hasn't opened it.`,
        `Fill only these slots now: ${missing.join(", ")}. Don't use ask or settle, and say nothing; you'll be told when the learner opens it.`,
        st.briefed ? "(You read this lesson's text and notes earlier.)" : "\n" + this.briefing(next),
      ].join("\n");
      st.briefed = true;
      try {
        await this.main.prompt((notes.length ? notes.join("\n") + "\n\n" : "") + msg);
      } catch (e: any) {
        console.error("[tutor] preparing ahead failed:", e?.message ?? e);
      } finally {
        this.background = null;
        this.store.save(this.lessonTurns);
      }
    };
    this.chain = this.chain.then(run, run);
  }

  lessonOpened(lesson: Lesson) {
    const st = this.store.lesson(lesson.id);
    const first = !st.visited;
    st.visited = true;
    this.store.page.current = lesson.id;
    this.store.save(this.lessonTurns);
    const missing = lesson.slotIds.filter((x) => !st.slots[x]);
    // A lesson in a later module is answered by a new thread, which hasn't read any lesson yet: start it now,
    // even when the lesson has nothing to fill, so the learner's first message doesn't wait for it.
    const m = this.moduleOf(lesson.id);
    const later = !!(this.thread && m && m !== this.thread.module && this.moduleIndex(m) > this.moduleIndex(this.thread.module));
    if (later) st.briefed = false;
    if (!first && missing.length === 0 && !later) { if (!this.foreground) this.prepareAhead(); return; }
    const turnState = lesson.turnIds.map((t) => `${t}: ${st.turns[t]?.status ?? "open"}`).join("; ");
    const head = `[page] Learner opened lesson ${lesson.id} "${lesson.title}" (first visit). Turns: ${turnState || "none"}.\nSlots to fill when due: ${missing.join(", ") || "none"}.`;
    const msg = first
      ? st.briefed
        ? `${head}\nYou read this lesson's text and notes when preparing it ahead${missing.length ? "" : ", and its opening slots are filled"}.`
        : `${head}\n\n${this.briefing(lesson)}`
      : `[page] Learner is back on lesson ${lesson.id}. Turns: ${turnState}. Unfilled slots: ${missing.join(", ")}. Fill any that are due now; otherwise stop.${st.briefed ? "" : "\n\n" + this.briefing(lesson)}`;
    st.briefed = true;
    this.enqueue(lesson.id, "Preparing the lesson", msg);
  }

  learnerSays(lessonId: string, turnId: string, said: string) {
    const lesson = this.course.lessons.get(lessonId);
    if (!lesson) return;
    const t = this.store.turn(lessonId, turnId);
    if (t.status === "settled") return;
    const firstMsg = t.attempts === 0;
    t.attempts++;
    t.log.push({ who: "learner", text: said, at: Date.now() });
    this.store.save(this.lessonTurns);
    const part = lesson.parts.find((p) => p.kind === "turn" && p.id === turnId) as any;
    const asked = firstMsg ? `(The page asked: ${part?.lead ? part.lead.replace(/\[\[(.*?)\]\]/g, "$1") + " " : ""}${part?.prompt ?? ""})\n` : "";
    const key = `${lessonId}/${turnId}`;
    this.enqueue(lessonId, "Thinking", `[your-turn ${key}] ${asked}Learner: ${said}`, () => {
      // The tutor's text was streamed into the turn. If it said nothing at all, say so.
      if (!this.spokeIn.has(key)) {
        this.store.turn(lessonId, turnId).log.push({ who: "tutor", text: "Sorry, I lost my train of thought there. Could you say that again?", at: Date.now() });
        this.store.save(this.lessonTurns);
      }
    }, key);
  }

  note(msg: string) { this.pendingNotes.push(msg); }

  // ---------- margin threads ----------

  async marginAsk(thread: Thread, question: string) {
    let s = this.margins.get(thread.id);
    if (!s) {
      const header = this.main.sessionManager.getHeader();
      const entries = this.main.sessionManager.getBranch();
      const sm = SessionManager.inMemory(config.learnerDir, undefined, header ? [header, ...entries] as any : (entries as any));
      s = await this.makeSession(sm, "margin");
      s.subscribe((ev: any) => {
        const key = `thread:${thread.id}`;
        if (ev.type === "message_update" && ev.assistantMessageEvent?.type === "text_delta") {
          this.activity.drafts[key] = textOf(ev.message);
          this.onActivity();
        } else if (ev.type === "message_end" && ev.message?.role === "assistant") {
          const u = ev.message.usage;
          if (u) this.onMetric({ kind: "margin", thread: thread.id, lesson: thread.from, ctx: (u.input ?? 0) + (u.cacheRead ?? 0) + (u.cacheWrite ?? 0), input: u.input ?? 0, cacheRead: u.cacheRead ?? 0, cacheWrite: u.cacheWrite ?? 0, output: u.output ?? 0, out: u.output ?? 0, cost: u.cost?.total ?? 0, ms: ev.message.durationMs ?? null, stop: ev.message.stopReason, error: ev.message.errorMessage ? String(ev.message.errorMessage).slice(0, 300) : undefined });
          // Each finished message goes into the thread, so text written before a tool call isn't lost.
          const said = textOf(ev.message);
          delete this.activity.drafts[key];
          if (said) { thread.messages.push({ who: "tutor", text: said, at: Date.now() }); this.store.save(); }
          else this.onActivity();
        }
      });
      this.margins.set(thread.id, s);
    }
    const lesson = this.course.lessons.get(thread.from);
    const lst = this.store.lesson(thread.from);
    const open = lesson?.turnIds.filter((t) => lst.turns[t]?.status !== "settled") ?? [];
    const held = [...this.course.glossary.values()].filter((g) => g.holdUntil && this.lessonTurns.get(g.holdUntil)?.some((t) => this.store.lesson(g.holdUntil!).turns[t]?.status !== "settled"));
    const head = [
      `[margin, lesson ${thread.from}${lesson ? ` "${lesson.title}"` : ""}]`,
      thread.messages.length <= 1 && lesson ? `Lesson text:\n<lesson.md>\n${lesson.source.trim()}\n</lesson.md>` : "",
      open.length ? `Open Your turns here (don't answer them): ${open.join(", ")}.` : "",
      held.length ? `Held back until their lesson's turns settle: ${held.map((g) => `${g.label} (${g.holdUntil})`).join(", ")}.` : "",
      thread.about ? `About: ${thread.about.label}` : "",
    ].filter(Boolean).join("\n");
    const images = await this.pointerImages(thread.about, thread.messages.length <= 1);
    this.activity.threads[thread.id] = true; this.onActivity();
    try {
      const before = thread.messages.length;
      await s.prompt(`${head}\nLearner: ${question}`, images.length ? { images } : undefined);
      // The answer was posted message by message as it was written; return text only if nothing was.
      return thread.messages.length > before ? "" : s.getLastAssistantText()?.trim() || "…";
    } finally {
      delete this.activity.threads[thread.id];
      delete this.activity.drafts[`thread:${thread.id}`];
      this.onActivity();
    }
  }

  private async pointerImages(p: Pointer | undefined, first: boolean) {
    if (!p || !first) return [];
    let file: string | undefined;
    if (p.kind === "figure" && p.src) {
      const u = p.src.split("?")[0];
      if (u.startsWith("/workspace/")) file = path.join(config.learnerDir, u.slice("/workspace/".length));
      else if (u.startsWith("/course-files/")) file = path.join(config.courseDir, u.slice("/course-files/".length));
    } else if (p.kind === "video" && p.src && p.at != null) {
      file = await videoStill(p.src, p.at);
    }
    if (!file || !fs.existsSync(file)) return [];
    const ext = path.extname(file).slice(1).toLowerCase();
    if (!["png", "jpg", "jpeg", "gif", "webp"].includes(ext)) return [];
    return [{ type: "image" as const, data: fs.readFileSync(file).toString("base64"), mimeType: `image/${ext === "jpg" ? "jpeg" : ext}` }];
  }

  closeThread(thread: Thread) {
    const s = this.margins.get(thread.id);
    s?.dispose();
    this.margins.delete(thread.id);
    if (thread.messages.length) {
      const qa = thread.messages.map((m) => `${m.who === "learner" ? "Learner" : "You"}: ${m.text.slice(0, 400)}`).join("\n");
      this.note(`[page] A side trip from lesson ${thread.from}${thread.about ? ` (about: ${thread.about.label})` : ""} was closed. It went:\n${qa}`);
    }
  }
}

// A still from a video at a given second, for "Pause and ask" (the tutor is multimodal).
async function videoStill(src: string, at: number): Promise<string | undefined> {
  const m = src.match(/^\/media\/videos\/([\w.-]+\.mp4)/);
  if (!m) return;
  const out = learnerPath("work", "stills", `${m[1].replace(/\.mp4$/, "")}-${at.toFixed(1)}.png`);
  if (fs.existsSync(out)) return out;
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const { spawnSync } = await import("node:child_process");
  spawnSync("ffmpeg", ["-v", "error", "-ss", String(at), "-i", path.join(config.mediaDir, "videos", m[1]), "-frames:v", "1", "-vf", "scale=960:-1", out]);
  return fs.existsSync(out) ? out : undefined;
}
