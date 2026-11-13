import { createContext, useContext } from "react";
import type { Course, GlossaryEntry, Lesson, Pointer, ServerState } from "./types.ts";

export interface Ctx {
  course: Course;
  glossary: Map<string, GlossaryEntry>;
  state: ServerState;
  lesson: Lesson;
  send: (m: unknown) => void;
  /** Open the margin with a pointer ("About: …"), remembering where the learner was. */
  askAbout: (p: Pointer | null, opts?: { video?: HTMLVideoElement }) => void;
  def: { where: string; key: string } | null;
  setDef: (d: { where: string; key: string } | null) => void;
}
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
  const outline = ctx.course.units.flatMap((u) => u.lessons).find((l) => l.id === e.holdUntil);
  if (!outline) return null;
  const st = ctx.state.page.lessons[e.holdUntil];
  const settled = st ? Object.values(st.turns).filter((t) => t.status === "settled").length : 0;
  return settled >= outline.turns ? null : e.holdUntil;
}

export const fmtTime = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
