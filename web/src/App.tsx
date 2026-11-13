import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { C, lookup, type Ctx } from "./ctx.tsx";
import { Margin } from "./Margin.tsx";
import { Definition, Inline } from "./Prose.tsx";
import { PartView } from "./Parts.tsx";
import type { Course, Lesson, Pointer, ServerState } from "./types.ts";

function useServer() {
  const [state, setState] = useState<ServerState | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const queue = useRef<string[]>([]);
  useEffect(() => {
    let stop = false, retry: number | undefined;
    const connect = () => {
      const s = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
      ws.current = s;
      s.onopen = () => { for (const m of queue.current.splice(0)) s.send(m); };
      s.onmessage = (e) => setState(JSON.parse(e.data));
      s.onclose = () => { if (!stop) retry = window.setTimeout(connect, 1500); };
    };
    connect();
    return () => { stop = true; clearTimeout(retry); ws.current?.close(); };
  }, []);
  const send = useCallback((m: unknown) => {
    const s = JSON.stringify(m);
    if (ws.current?.readyState === WebSocket.OPEN) ws.current.send(s);
    else queue.current.push(s);
  }, []);
  return { state, send };
}

const hashLesson = () => decodeURIComponent(location.hash.replace(/^#\/?/, "")) || null;

export function App() {
  const { state, send } = useServer();
  const [course, setCourse] = useState<Course | null>(null);
  const [lessons, setLessons] = useState<Record<string, Lesson>>({});
  const [lessonId, setLessonId] = useState<string | null>(hashLesson());
  const [def, setDef] = useState<{ where: string; key: string } | null>(null);
  const [pointer, setPointer] = useState<Pointer | null>(null);
  const place = useRef<{ y: number; video?: HTMLVideoElement; t?: number; playing?: boolean } | null>(null);
  const [openUnits, setOpenUnits] = useState<Record<string, boolean>>({});

  useEffect(() => { fetch("/api/course").then((r) => r.json()).then(setCourse); }, []);
  useEffect(() => {
    const f = () => setLessonId(hashLesson());
    window.addEventListener("hashchange", f);
    return () => window.removeEventListener("hashchange", f);
  }, []);
  // Default lesson: where the learner was, else the first.
  useEffect(() => {
    if (!lessonId && course && state) location.hash = `#/${state.page.current ?? course.order[0]}`;
  }, [lessonId, course, state]);
  useEffect(() => {
    if (!lessonId) return;
    setDef(null);
    setPointer(null);
    window.scrollTo(0, 0);
    send({ type: "open", lesson: lessonId });
    if (!lessons[lessonId]) fetch(`/api/lesson/${encodeURIComponent(lessonId)}`).then((r) => r.ok ? r.json() : null).then((l) => l && setLessons((x) => ({ ...x, [l.id]: l })));
  }, [lessonId]); // eslint-disable-line react-hooks/exhaustive-deps

  const glossary = useMemo(() => new Map((course?.glossary ?? []).map((g) => [g.key, g])), [course]);
  const lesson = lessonId ? lessons[lessonId] : undefined;

  // Selecting text in the lesson sets the margin's pointer.
  const onMouseUp = () => {
    const sel = window.getSelection()?.toString().trim();
    if (sel && sel.length > 2 && sel.length < 400) setPointer({ kind: "text", label: `“${sel.length > 90 ? sel.slice(0, 90) + "…" : sel}”` });
  };

  const askAbout = useCallback((p: Pointer | null, opts?: { video?: HTMLVideoElement }) => {
    const v = opts?.video;
    place.current = { y: window.scrollY, video: v, t: v?.currentTime, playing: v ? !v.paused : false };
    v?.pause();
    setPointer(p);
    // Close any open side trip so the ask box shows with the new pointer.
    const open = state?.page.threads.find((t) => t.open);
    if (open) send({ type: "thread.close", id: open.id });
    if (window.innerWidth < 900) document.getElementById("page-ask")?.scrollIntoView({ behavior: "smooth" });
  }, [state, send]);

  // Closing a side trip returns the learner to where they were, and resumes the video at that second.
  const returnToPlace = () => {
    const p = place.current;
    place.current = null;
    if (!p) return;
    window.scrollTo({ top: p.y, behavior: "smooth" });
    if (p.video && p.t != null) { p.video.currentTime = p.t; if (p.playing || true) p.video.play().catch(() => {}); }
  };

  if (!course || !state) return <div style={{ padding: 32 }} className="note">Loading…</div>;

  const allLessons = course.units.flatMap((u) => u.lessons.map((l) => ({ ...l, unit: u })));
  const idx = allLessons.findIndex((l) => l.id === lessonId);
  const prev = idx > 0 ? allLessons[idx - 1] : null;
  const next = idx >= 0 && idx < allLessons.length - 1 ? allLessons[idx + 1] : null;
  const unit = course.units.find((u) => u.lessons.some((l) => l.id === lessonId));
  const go = (id: string) => { location.hash = `#/${id}`; };
  const box = (id: string) => state.boxes[id] ?? "empty";

  const ctx: Ctx | null = lesson ? { course, glossary, state, lesson, send, askAbout, def, setDef } : null;
  const lst = lesson ? state.page.lessons[lesson.id] : undefined;

  return (
    <>
      <header className="top">
        <div className="brand"><span className="logo" aria-hidden="true" /><span>cuPhoton Learn</span></div>
        <nav className="strip" aria-label="Course progress">
          {course.units.map((u) => (
            <div key={u.id} className="strip-group">
              <span className={`strip-label ${u.id === unit?.id ? "cur" : ""}`}>{u.id}</span>
              <div className="boxes">
                {u.lessons.map((l) => (
                  <button key={l.id} type="button" className={`sq ${box(l.id)} ${l.id === lessonId ? "cur" : ""}`}
                    title={`${l.id} ${l.title}`} aria-label={`Lesson ${l.id}: ${l.title}`} onClick={() => go(l.id)} />
                ))}
              </div>
            </div>
          ))}
        </nav>
      </header>
      <div className="cols">
        <nav className="map" aria-label="Course map">
          {course.units.map((u) => {
            const open = openUnits[u.id] ?? u.id === unit?.id;
            return (
              <div key={u.id} style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <button type="button" className="row unit-head" aria-expanded={open} onClick={() => setOpenUnits({ ...openUnits, [u.id]: !open })}>
                  {u.id} · {u.title}
                </button>
                {open && u.lessons.map((l) => (
                  <button key={l.id} type="button" className={`row ${l.id === lessonId ? "cur" : ""}`} onClick={() => go(l.id)} style={{ paddingLeft: 4 }}>
                    <span className={`sq ${box(l.id)}`} aria-hidden="true" style={{ flex: "none", cursor: "inherit" }} />
                    <span style={{ fontSize: 14 }}>{l.id} {l.title}</span>
                  </button>
                ))}
              </div>
            );
          })}
        </nav>

        {ctx && lesson ? (
          <C.Provider value={ctx}>
            <main className="lesson" onMouseUp={onMouseUp}>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div className="crumb">Unit {unit?.id} · {unit?.title} · Lesson {lesson.id}</div>
                <h1>{lesson.title}</h1>
                <p className="question">{lesson.question}</p>
                {lesson.terms.length > 0 && (
                  <div className="keyterms">
                    <span className="note">Key terms</span>
                    <Inline where="terms" text={lesson.terms.map((t) => `[[${t}${t.startsWith("@") && !t.includes("|") ? "|" + (lookup(glossary, t)?.label ?? t) : ""}]]`).join("  ")} />
                  </div>
                )}
                <Definition where="terms" />
              </div>
              {lesson.parts.map((p, i) => <PartView key={i} part={p} idx={i} />)}
              <div className="closure">
                {lst?.revealed && lesson.closure && (
                  <>
                    <p><strong>We found:</strong> {lesson.closure.found}</p>
                    <p className="note" style={{ fontSize: 16 }}><strong style={{ color: "var(--text-color-primary)" }}>Which raises:</strong> {lesson.closure.raises}</p>
                  </>
                )}
                <div className="nav">
                  {prev ? <button type="button" className="btn tertiary" onClick={() => go(prev.id)}>← {prev.id} {prev.title}</button> : <span />}
                  {next && <button type="button" className="btn secondary" onClick={() => go(next.id)}>{next.id} {next.title} →</button>}
                </div>
              </div>
            </main>
            <aside className="margin" aria-label="Ask and side trips">
              <Margin pointer={pointer} setPointer={setPointer} onClose={returnToPlace} />
            </aside>
          </C.Provider>
        ) : (
          <main className="lesson"><p className="note">{lessonId && course.order.includes(lessonId) ? "Loading the lesson…" : "This lesson isn't written yet."}</p></main>
        )}
      </div>
    </>
  );
}
