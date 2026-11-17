import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { Course, GlossaryEntry, Lesson, Pointer, ServerState, WorkFile } from "./types.ts";

export interface Ctx {
  course: Course;
  glossary: Map<string, GlossaryEntry>;
  state: ServerState;
  lesson: Lesson;
  send: (m: unknown) => void;
  /** Open the margin with a pointer ("About: …"), remembering where the learner was. */
  askAbout: (p: Pointer | null, opts?: { video?: HTMLVideoElement }) => void;
  def: TermDef | null;
  setDef: (d: TermDef | null) => void;
  /** This module's work folder (work/<module id>) and what's in it, for the Files panel and file links. */
  workDir: string;
  workFiles: WorkFile[];
  openFile: (path: string | null) => void;
}
/** An open definition: which term, where on the page, and the term's position (document coordinates). */
export interface TermDef { where: string; key: string; anchor: { x: number; y: number; top: number } }
export const C = createContext<Ctx>(null as any);
export const useCtx = () => useContext(C);

export const normKey = (s: string) =>
  s.trim().toLowerCase().replace(/\s*\(.*?\)\s*/g, " ").replace(/\s+/g, " ").trim();

export function lookup(glossary: Map<string, GlossaryEntry>, raw: string): GlossaryEntry | undefined {
  const k = raw.startsWith("@") ? raw.split("|")[0] : normKey(raw.split("|")[0]);
  return glossary.get(k) ?? glossary.get(k.replace(/s$/, ""));
}

/** A hold-back is active while the lesson it guards still has open turns. */
export function heldUntil(ctx: Pick<Ctx, "course" | "state">, e: GlossaryEntry): string | null {
  if (!e.holdUntil) return null;
  const outline = ctx.course.modules.flatMap((u) => u.lessons).find((l) => l.id === e.holdUntil);
  if (!outline) return null;
  const st = ctx.state.page.lessons[e.holdUntil];
  const settled = st ? Object.values(st.turns).filter((t) => t.status === "settled").length : 0;
  return settled >= outline.turns ? null : e.holdUntil;
}

/** A text box's unsent text, kept per box in this browser (survives switching lessons, tabs or reloading). */
export function useDraft(key: string): [string, (v: string) => void] {
  const k = `draft:${key}`;
  const [v, setV] = useState(() => { try { return localStorage.getItem(k) ?? ""; } catch { return ""; } });
  useEffect(() => { try { setV(localStorage.getItem(k) ?? ""); } catch { setV(""); } }, [k]);
  const set = useCallback((x: string) => {
    setV(x);
    try { if (x) localStorage.setItem(k, x); else localStorage.removeItem(k); } catch { /* storage unavailable: keep it in memory only */ }
  }, [k]);
  return [v, set];
}

export const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
