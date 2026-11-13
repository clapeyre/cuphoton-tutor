import { useEffect, useRef, useState } from "react";
import { useCtx } from "./ctx.tsx";
import type { Pointer } from "./types.ts";

/** The margin is for conversations only: one ask box, side trips, and notes to the authors. */
export function Margin({ pointer, setPointer, onClose }: {
  pointer: Pointer | null; setPointer: (p: Pointer | null) => void; onClose: () => void;
}) {
  const ctx = useCtx();
  const { page, activity, notes } = ctx.state;
  const open = page.threads.find((t) => t.open);
  const [draft, setDraft] = useState("");
  const [tripDraft, setTripDraft] = useState("");
  const askRef = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { if (pointer && !open) askRef.current?.focus(); }, [pointer, open]);

  const ask = () => {
    const q = draft.trim();
    if (!q) return;
    ctx.send({ type: "thread.new", from: ctx.lesson.id, about: pointer, question: q });
    setDraft("");
    setPointer(null);
  };

  if (open) {
    const busy = !!activity.threads[open.id];
    const sendTrip = () => {
      const q = tripDraft.trim();
      if (!q) return;
      ctx.send({ type: "thread.ask", id: open.id, question: q });
      setTripDraft("");
    };
    return (
      <div className="card trip" role="dialog" aria-label="Side trip">
        <div className="note">Side trip from lesson {open.from}</div>
        <div style={{ fontSize: 18, fontWeight: 600 }}>{open.title}</div>
        {open.about && <div className="about"><span><span className="k">About: </span>{open.about.label}</span></div>}
        {open.about?.kind === "video" && open.about.src && open.about.at === 0 && (
          <video controls preload="metadata" src={open.about.src} />
        )}
        {open.messages.map((m, i) => (
          <div key={i} className={`msg ${m.who}`}><span className="who">{m.who === "tutor" ? "Tutor" : "You"}</span>{m.text}</div>
        ))}
        {busy && <span className="typing">The tutor is answering</span>}
        <label htmlFor="trip-in" className="note">Ask a follow-up</label>
        <textarea id="trip-in" className="input" rows={2} value={tripDraft} onChange={(e) => setTripDraft(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) sendTrip(); }} />
        <div className="btn-row">
          <button type="button" className="btn secondary small" onClick={sendTrip} disabled={!tripDraft.trim() || busy}>Ask</button>
          <button type="button" className="btn primary small" onClick={() => { ctx.send({ type: "thread.close", id: open.id }); onClose(); }}>Back to the lesson</button>
        </div>
      </div>
    );
  }

  const trips = page.threads.filter((t) => t.messages.length);
  return (
    <div className="margin-stack">
      <div className="card">
        <label htmlFor="page-ask" style={{ fontWeight: 600 }}>Ask about anything on this page</label>
        {pointer && (
          <div className="about">
            <span><span className="k">About: </span>{pointer.label}</span>
            <button type="button" className="link" onClick={() => setPointer(null)} aria-label="Clear what this question is about">Clear</button>
          </div>
        )}
        <textarea ref={askRef} id="page-ask" className="input" rows={3} value={draft} onChange={(e) => setDraft(e.target.value)}
          placeholder="e.g. Why does the second night look blurrier?"
          onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) ask(); }} />
        <div><button type="button" className="btn secondary small" onClick={ask} disabled={!draft.trim()}>Ask</button></div>
      </div>
      {trips.length > 0 && (
        <>
          <div className="small-caps">Your side trips</div>
          {[...trips].reverse().map((t) => (
            <button key={t.id} type="button" className="tripbtn" onClick={() => ctx.send({ type: "thread.open", id: t.id })}>
              <span className="note">From lesson {t.from}{t.about ? ` · ${t.about.label}` : ""}</span>
              <span style={{ fontWeight: 600 }}>{t.title}</span>
            </button>
          ))}
        </>
      )}
      {notes.length > 0 && (
        <div className="card">
          <div className="small-caps">Notes for the course authors</div>
          {notes.slice(-5).map((n, i) => <div key={i} className="note">• {n.summary}</div>)}
          {page.feedbackConsent === null ? (
            <>
              <span className="note">May the tutor send notes like these, anonymously, to the people who write this course?</span>
              <div className="btn-row">
                <button type="button" className="btn secondary small" onClick={() => ctx.send({ type: "consent", value: true })}>Yes, send them</button>
                <button type="button" className="btn tertiary small" onClick={() => ctx.send({ type: "consent", value: false })}>Keep them here</button>
              </div>
            </>
          ) : (
            <button type="button" className="link quiet" style={{ alignSelf: "flex-start" }} onClick={() => ctx.send({ type: "consent", value: !page.feedbackConsent })}>
              {page.feedbackConsent ? "Sent to the authors. Stop sending" : "Kept on this machine. Send them"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
