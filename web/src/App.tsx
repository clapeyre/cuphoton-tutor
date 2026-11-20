import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { C, lookup, type Ctx, type TermDef } from "./ctx.tsx";
import { FilesPanel } from "./Files.tsx";
import { Margin } from "./Margin.tsx";
import { Inline, TermPopover } from "./Prose.tsx";
import { PartView } from "./Parts.tsx";
import type { Course, Lesson, Pointer, ServerState, WorkFile } from "./types.ts";

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
  const [def, setDef] = useState<TermDef | null>(null);
  const [pointer, setPointer] = useState<Pointer | null>(null);
  const place = useRef<{ y: number; video?: HTMLVideoElement; t?: number; playing?: boolean } | null>(null);
  const [openModules, setOpenModules] = useState<Record<string, boolean>>({});
  // The Files panel: which work folder, which file, and whether it's open.
  const [filesOpen, setFilesOpen] = useState(false);
  const [filesDir, setFilesDir] = useState<string | null>(null);
  const [filesPath, setFilesPath] = useState<string | null>(null);
  const [workFiles, setWorkFiles] = useState<Record<string, WorkFile[]>>({});

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

  // This lesson's module, and the files in its work folder: fetched on arrival, again whenever the tutor
  // goes idle (it may have written something), and when the panel's folder changes.
  const moduleId = course?.modules.find((u) => u.lessons.some((l) => l.id === lessonId))?.id ?? null;
  const busy = !!state?.activity.main;
  const loadFiles = useCallback((dir: string) => {
    fetch(`/api/files?dir=${encodeURIComponent(dir)}`).then((r) => r.json()).then((j) => setWorkFiles((x) => ({ ...x, [dir]: j.files ?? [] }))).catch(() => {});
  }, []);
  useEffect(() => { if (moduleId && !busy) loadFiles(moduleId); }, [moduleId, busy, loadFiles]);
  useEffect(() => { if (filesOpen && filesDir && filesDir !== moduleId) loadFiles(filesDir); }, [filesOpen, filesDir, moduleId, loadFiles]);
  const openFile = useCallback((p: string | null) => { setFilesDir(moduleId); setFilesPath(p); setFilesOpen(true); }, [moduleId]);

  const glossary = useMemo(() => new Map((course?.glossary ?? []).map((g) => [g.key, g])), [course]);
  const lesson = lessonId ? lessons[lessonId] : undefined;

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

  const allLessons = course.modules.flatMap((u) => u.lessons.map((l) => ({ ...l, module: u })));
  const idx = allLessons.findIndex((l) => l.id === lessonId);
  const prev = idx > 0 ? allLessons[idx - 1] : null;
  const next = idx >= 0 && idx < allLessons.length - 1 ? allLessons[idx + 1] : null;
  const module = course.modules.find((u) => u.lessons.some((l) => l.id === lessonId));
  const go = (id: string) => { location.hash = `#/${id}`; };
  const box = (id: string) => state.boxes[id] ?? "empty";

  const workDir = moduleId ?? "";
  const ctx: Ctx | null = lesson ? { course, glossary, state, lesson, send, askAbout, def, setDef, workDir, workFiles: workFiles[workDir] ?? [], openFile } : null;
  const dirs = course.modules.map((u) => u.id);
  const panelDir = filesDir ?? workDir;
  const lst = lesson ? state.page.lessons[lesson.id] : undefined;

  return (
    <>
      <header className="top">
        <div className="brand"><span className="logo" aria-hidden="true" /><span>{course.brand}</span></div>
        <nav className="strip" aria-label="Course progress">
          {course.modules.map((u) => (
            <div key={u.id} className="strip-group">
              <span className={`strip-label ${u.id === module?.id ? "cur" : ""}`}>{u.id}</span>
              <div className="boxes">
                {u.lessons.map((l) => (
                  <button key={l.id} type="button" className={`sq ${box(l.id)} ${l.id === lessonId ? "cur" : ""}`}
                    title={`${l.id} ${l.title}`} aria-label={`Lesson ${l.id}: ${l.title}`} onClick={() => go(l.id)} />
                ))}
              </div>
            </div>
          ))}
        </nav>
        {course.guideUrl && <a className="ext guide-link" href={course.guideUrl} target="_blank" rel="noopener noreferrer">{course.product} user guide</a>}
        <button type="button" className="btn tertiary small files-btn" aria-expanded={filesOpen}
          onClick={() => filesOpen ? setFilesOpen(false) : openFile(filesDir === moduleId ? filesPath : null)}>
          Files
        </button>
        <a className="btn tertiary small admin-link" href="/admin" target="_blank" rel="noopener" title="How the tutor is doing: context, response times, errors, spend">Admin</a>
      </header>
      {filesOpen && panelDir && (
        <FilesPanel dirs={dirs} dir={panelDir} setDir={setFilesDir} files={workFiles[panelDir] ?? []}
          path={filesPath} setPath={setFilesPath} onClose={() => setFilesOpen(false)} refresh={() => loadFiles(panelDir)} />
      )}
      <div className="cols">
        <nav className="map" aria-label="Course map">
          {course.modules.map((u) => {
            const open = openModules[u.id] ?? u.id === module?.id;
            return (
              <div key={u.id} style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                <button type="button" className="row module-head" aria-expanded={open} onClick={() => setOpenModules({ ...openModules, [u.id]: !open })}>
                  {u.id} · {u.title}
                </button>
                {open && u.lessons.map((l) => (
                  <button key={l.id} type="button" className={`row ${l.id === lessonId ? "cur" : ""}`} onClick={() => go(l.id)} style={{ paddingLeft: 4 }}>
                    <span className={`sq ${box(l.id)} ${l.id === lessonId ? "cur" : ""}`} aria-hidden="true" style={{ flex: "none", cursor: "inherit" }} />
                    <span style={{ fontSize: 14 }}>{l.id} {l.title}</span>
                  </button>
                ))}
              </div>
            );
          })}
        </nav>

        {ctx && lesson ? (
          <C.Provider value={ctx}>
            <main className="lesson">
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div className="crumb">Module {module?.id} · {module?.title} · Lesson {lesson.id}</div>
                <h1>{lesson.title}</h1>
                <p className="question">{lesson.question}</p>
                {lesson.terms.length > 0 && (
                  <div className="keyterms">
                    <span className="note">Key terms</span>
                    <Inline where="terms" text={lesson.terms.map((t) => `[[${t}${t.startsWith("@") && !t.includes("|") ? "|" + (lookup(glossary, t)?.label ?? t) : ""}]]`).join("  ")} />
                  </div>
                )}
                {!!lesson.guide?.length && (
                  <div className="keyterms">
                    <span className="note">In the user guide</span>
                    {lesson.guide.map((g) => <a key={g.url} className="ext" href={g.url} target="_blank" rel="noopener noreferrer">{g.title}</a>)}
                  </div>
                )}
              </div>
              {lesson.intro && (
                <section className="intro" aria-label={`About Module ${module?.id}`}>
                  <div className="small-caps">Module {module?.id} · {module?.title}</div>
                  {lesson.intro.map((t, i) => <p key={i}><Inline text={t} where={`intro${i}`} /></p>)}
                </section>
              )}
              {lesson.parts.map((p, i) => <PartView key={i} part={p} idx={i} />)}
              <div className="closure">
                {lst?.revealed && lesson.closure && (
                  <>
                    <div className="small-caps">What we found</div>
                    <p><Inline text={lesson.closure.found} where="found" /></p>
                    {lst.yourRun && (
                      <div className="your-run">
                        <span className="note">In your run</span>
                        <p>{lst.yourRun}</p>
                      </div>
                    )}
                    {lesson.turnIds.some((t) => lst.turns[t]?.summary) && (
                      <div className="yours">
                        <span className="note">Your answers, in short</span>
                        {lesson.turnIds.map((t) => lst.turns[t]?.summary && <span key={t}>“{lst.turns[t].summary}”</span>)}
                      </div>
                    )}
                    {lesson.closure.matters && (
                      <>
                        <div className="small-caps">Why it matters</div>
                        <p><Inline text={lesson.closure.matters} where="matters" /></p>
                      </>
                    )}
                    <p className="raises"><strong>Which raises:</strong> <Inline text={lesson.closure.raises} where="raises" /></p>
                  </>
                )}
                <div className="nav">
                  {prev ? <button type="button" className="btn tertiary" onClick={() => go(prev.id)}>← {prev.id} {prev.title}</button> : <span />}
                  {next && <button type="button" className="btn secondary" onClick={() => go(next.id)}>{next.id} {next.title} →</button>}
                </div>
              </div>
            </main>
            <TermPopover />
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
