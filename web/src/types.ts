export type Part =
  | { kind: "prose"; text: string }
  | { kind: "code"; text: string; lang?: string }
  | { kind: "video"; id: string; title: string; duration: string; chapters: [number, string][]; src: string }
  | { kind: "figure"; title: string; caption: string; src: string; alt: string }
  | { kind: "slot"; id: string; title: string; caption: string }
  | { kind: "chain"; hi?: string; caption: string }
  | { kind: "turn"; id: string; title: string; prompt?: string; lead?: string; image?: string; imageCaption?: string }
  | { kind: "ref"; text: string; label: string; video?: string; videoTitle?: string };

export interface Lesson {
  id: string; module: string; slug: string; title: string; question: string; terms: string[];
  parts: Part[]; closure: { found: string; matters?: string; raises: string } | null; intro?: string[]; turnIds: string[]; slotIds: string[];
}
export interface GlossaryEntry { key: string; label: string; definition: string; holdUntil?: string; concept?: boolean; link?: { url: string; label: string } }
export interface Course {
  title: string;
  modules: { id: string; title: string; lessons: { id: string; title: string; turns: number }[] }[];
  chain: { id: string; does: string; definition: string }[];
  glossary: GlossaryEntry[];
  order: string[];
}
export interface RunRecord {
  id: string; by: string; device: "CPU" | "GPU"; seconds: number; at: number; commands: string[]; files: string[];
  code?: { path: string; text: string }[]; receipt?: Record<string, unknown>; ok: boolean;
}
export interface FigureOnPage { id: string; src: string; title: string; caption: string; run?: RunRecord }
export interface TurnMsg { who: "tutor" | "learner"; text: string; figure?: FigureOnPage; at: number }
export interface TurnState { status: "open" | "settled"; summary?: string; log: TurnMsg[] }
export interface LessonState { visited: boolean; turns: Record<string, TurnState>; slots: Record<string, FigureOnPage>; revealed: boolean }
export interface Pointer { kind: "text" | "figure" | "video" | "term" | "turn"; label: string; src?: string; at?: number; key?: string }
export interface Thread { id: string; from: string; about?: Pointer; title: string; messages: { who: "tutor" | "learner"; text: string }[]; open: boolean }
export interface PageState { current: string | null; lessons: Record<string, LessonState>; threads: Thread[]; feedbackConsent: boolean | null }
export interface ServerState {
  page: PageState;
  boxes: Record<string, "empty" | "half" | "full">;
  activity: { main: string | null; turn: string | null; threads: Record<string, boolean>; drafts: Record<string, string> };
  notes: { ts: string; kind: string; summary: string }[];
}

/** A file in the learner's work folder (the Files panel). */
export interface WorkFile { path: string; size: number; kind: "text" | "image" | "html" | "other" }
