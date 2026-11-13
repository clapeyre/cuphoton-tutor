// Everything the server remembers about the one learner, in learner/.
// progress.json is the author-facing record (attempts and hints live there,
// never in the UI); page.json holds what the page shows.
import fs from "node:fs";
import path from "node:path";
import { config, learnerPath } from "./config.ts";
import type { RunRecord } from "./recorder.ts";

export interface TurnMsg { who: "tutor" | "learner"; text: string; figure?: FigureOnPage; at: number }
export interface FigureOnPage { id: string; src: string; title: string; caption: string; run?: RunRecord }
export interface TurnState {
  status: "open" | "settled";
  summary?: string;
  log: TurnMsg[];
  attempts: number; // learner messages
  hints: string[]; // rungs used
  misconceptions: string[];
}
export interface LessonState { visited: boolean; briefed?: boolean; /* the tutor has read lesson.md and tutor.md */ turns: Record<string, TurnState>; slots: Record<string, FigureOnPage>; revealed: boolean }
export interface Thread {
  id: string;
  from: string; // lesson id
  about?: Pointer;
  title: string;
  messages: { who: "tutor" | "learner"; text: string; at: number }[];
  open: boolean;
}
export interface Pointer { kind: "text" | "figure" | "video" | "term" | "turn"; label: string; src?: string; at?: number; key?: string }

export interface PageState {
  current: string | null;
  lessons: Record<string, LessonState>;
  threads: Thread[];
  feedbackConsent: boolean | null;
}

export interface Progress {
  learner: { levels: Record<string, string> };
  current: string | null;
  lessons: Record<string, { status: "empty" | "half" | "full"; turns: Record<string, { status: string; attempts: number; hints: string[]; misconceptions: string[]; summary?: string }> }>;
  misconceptions: { observed: string[] };
  new_observations: string[];
  feedback_consent: boolean | null;
  session_notes: string[];
}

const PAGE = () => learnerPath("page.json");
const PROGRESS = () => learnerPath("progress.json");
export const QUEUE = () => learnerPath("feedback-queue.jsonl");

export class Store {
  page: PageState;
  private listeners = new Set<() => void>();

  constructor() {
    fs.mkdirSync(config.learnerDir, { recursive: true });
    fs.mkdirSync(learnerPath("work"), { recursive: true });
    this.page = fs.existsSync(PAGE())
      ? JSON.parse(fs.readFileSync(PAGE(), "utf8"))
      : { current: null, lessons: {}, threads: [], feedbackConsent: null };
  }

  onChange(f: () => void) { this.listeners.add(f); return () => this.listeners.delete(f); }

  lesson(id: string): LessonState {
    return (this.page.lessons[id] ??= { visited: false, turns: {}, slots: {}, revealed: false });
  }
  turn(lessonId: string, turnId: string): TurnState {
    return (this.lesson(lessonId).turns[turnId] ??= { status: "open", log: [], attempts: 0, hints: [], misconceptions: [] });
  }
  findTurn(turnId: string): { lessonId: string; turn: TurnState } | null {
    // turn ids are "lesson/turn" from the tutor, or bare when unique in the current lesson
    const [a, b] = turnId.includes("/") ? turnId.split("/", 2) : [this.page.current ?? "", turnId];
    if (!a || !b) return null;
    return { lessonId: a, turn: this.turn(a, b) };
  }

  boxState(id: string, turnIds: string[]): "empty" | "half" | "full" {
    const l = this.page.lessons[id];
    if (!l?.visited) return "empty";
    const settled = turnIds.filter((t) => l.turns[t]?.status === "settled").length;
    if (l.revealed || (turnIds.length > 0 && settled === turnIds.length) || turnIds.length === 0) return "full";
    return "half";
  }

  save(lessonTurns?: Map<string, string[]>) {
    fs.writeFileSync(PAGE(), JSON.stringify(this.page, null, 1));
    if (lessonTurns) this.writeProgress(lessonTurns);
    for (const f of this.listeners) f();
  }

  private writeProgress(lessonTurns: Map<string, string[]>) {
    const old: Partial<Progress> = fs.existsSync(PROGRESS()) ? JSON.parse(fs.readFileSync(PROGRESS(), "utf8")) : {};
    const lessons: Progress["lessons"] = {};
    const observed = new Set(old.misconceptions?.observed ?? []);
    for (const [id, turnIds] of lessonTurns) {
      const l = this.page.lessons[id];
      if (!l) continue;
      lessons[id] = { status: this.boxState(id, turnIds), turns: {} };
      for (const [tid, t] of Object.entries(l.turns)) {
        lessons[id].turns[tid] = { status: t.status, attempts: t.attempts, hints: t.hints, misconceptions: t.misconceptions, summary: t.summary };
        t.misconceptions.filter((m) => /^M-/.test(m)).forEach((m) => observed.add(m));
      }
    }
    const p: Progress = {
      learner: old.learner ?? { levels: {} },
      current: this.page.current,
      lessons,
      misconceptions: { observed: [...observed] },
      new_observations: old.new_observations ?? [],
      feedback_consent: this.page.feedbackConsent,
      session_notes: old.session_notes ?? [],
    };
    fs.writeFileSync(PROGRESS(), JSON.stringify(p, null, 2));
  }

  addObservation(text: string) {
    const p: Progress = JSON.parse(fs.existsSync(PROGRESS()) ? fs.readFileSync(PROGRESS(), "utf8") : "{}");
    p.new_observations = [...(p.new_observations ?? []), text];
    fs.writeFileSync(PROGRESS(), JSON.stringify(p, null, 2));
  }
}

export function ensureDir(p: string) { fs.mkdirSync(path.dirname(p), { recursive: true }); }
