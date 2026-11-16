import { useRef, useState } from "react";
import { fmtTime, useCtx, useDraft } from "./ctx.tsx";
import { Code } from "./Code.tsx";
import { Inline, Typed } from "./Prose.tsx";
import { ZoomImg } from "./Zoom.tsx";
import type { FigureOnPage, Part, RunRecord } from "./types.ts";

export function PartView({ part, idx }: { part: Part; idx: number }) {
  switch (part.kind) {
    case "prose":
      return (
        <div className="prose">
          <p><Inline text={part.text} where={`p${idx}`} /></p>
        </div>
      );
    case "code": return <Code text={part.text} lang={part.lang} className="lesson-code" />;
    case "video": return <Video part={part} />;
    case "figure": return <AuthoredFigure part={part} />;
    case "slot": return <Slot part={part} />;
    case "chain": return <Chain part={part} idx={idx} />;
    case "turn": return <Turn part={part} />;
    case "ref": return <Ref part={part} />;
  }
}

function Video({ part }: { part: Extract<Part, { kind: "video" }> }) {
  const ctx = useCtx();
  const ref = useRef<HTMLVideoElement>(null);
  return (
    <figure>
      <video ref={ref} id={`video-${part.id}`} controls preload="metadata" src={part.src}>
        <track kind="subtitles" srcLang="en" label="English" src={part.src.replace(/\.mp4$/, ".vtt")} />
      </video>
      <figcaption>
        <span className="capline">
          <span><strong>{part.title}</strong> · {part.duration}</span>
          {part.chapters.length > 1 && part.chapters.map(([t, label]) => (
            <button key={t} type="button" className="link quiet" onClick={() => { const v = ref.current!; v.currentTime = t; v.play(); }}>
              {fmtTime(t)} {label}
            </button>
          ))}
          <button type="button" className="link" onClick={() => {
            const v = ref.current!;
            const at = v.currentTime;
            ctx.askAbout({ kind: "video", label: `${part.title}, at ${fmtTime(at)}`, src: part.src, at }, { video: v });
          }}>Pause and ask</button>
        </span>
      </figcaption>
    </figure>
  );
}

function AuthoredFigure({ part }: { part: Extract<Part, { kind: "figure" }> }) {
  const ctx = useCtx();
  return (
    <figure>
      <ZoomImg className="plot" src={part.src} alt={part.alt} caption={part.title} />
      <figcaption>
        <span><strong>{part.title}.</strong> {part.caption}</span>
        <span className="capline">
          <button type="button" className="link" onClick={() => ctx.askAbout({ kind: "figure", label: part.title, src: part.src })}>Ask about this</button>
        </span>
      </figcaption>
    </figure>
  );
}

export function runLine(r: RunRecord) {
  const s = r.seconds < 10 ? r.seconds.toFixed(1) : Math.round(r.seconds).toString();
  return `Made by ${r.by} · ${r.device} · ${s} s`;
}

export function ProducedFigure({ fig, compact }: { fig: FigureOnPage; compact?: boolean }) {
  const ctx = useCtx();
  const [open, setOpen] = useState(false);
  const r = fig.run;
  return (
    <figure>
      <ZoomImg className="plot" src={fig.src} alt={fig.title || fig.caption} caption={fig.title ? `${fig.title}. ${fig.caption ?? ""}` : fig.caption}
        style={compact ? { maxWidth: "100%" } : undefined} />
      <figcaption>
        {(fig.title || fig.caption) && <span>{fig.title && <strong>{fig.title}. </strong>}{fig.caption}</span>}
        <span className="capline">
          {r && <span>{runLine(r)}</span>}
          {r && <button type="button" className="link" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? "Hide the run record" : "Run record"}</button>}
          <button type="button" className="link" onClick={() => ctx.askAbout({ kind: "figure", label: fig.title || fig.caption.slice(0, 60) || "this figure", src: fig.src })}>Ask about this</button>
        </span>
      </figcaption>
      {open && r && <RunRecordView r={r} />}
    </figure>
  );
}

function RunRecordView({ r }: { r: RunRecord }) {
  const [code, setCode] = useState(false);
  return (
    <div className="run">
      <div className="h">{new Date(r.at).toLocaleString()} · {r.ok ? "finished" : "failed"} · {r.seconds.toFixed(2)} s on the {r.device}</div>
      {r.receipt && <pre>{Object.entries(r.receipt).map(([k, v]) => `${k}: ${String(v)}`).join("\n")}</pre>}
      <div>
        <div className="h">Files written</div>
        <pre>{r.files.join("\n") || "(none)"}</pre>
      </div>
      {r.code?.length ? (
        <div>
          <button type="button" className="link" onClick={() => setCode(!code)}>{code ? "Hide the code" : `Show the code (${r.code.map((c) => c.path).join(", ")})`}</button>
          {code && r.code.map((c) => (
            <div key={c.path} style={{ marginTop: 8 }}>
              <div className="h">{c.path}</div>
              <Code text={c.text} lang={c.path} />
            </div>
          ))}
        </div>
      ) : (
        <div><div className="h">Command</div><Code text={r.commands.join("\n")} lang="bash" /></div>
      )}
    </div>
  );
}

function Slot({ part }: { part: Extract<Part, { kind: "slot" }> }) {
  const ctx = useCtx();
  const fig = ctx.state.page.lessons[ctx.lesson.id]?.slots[part.id];
  if (fig) return <ProducedFigure fig={{ ...fig, title: fig.title || part.title, caption: fig.caption || part.caption }} />;
  if (ctx.state.activity.main && ctx.state.page.current === ctx.lesson.id) {
    return (
      <figure>
        <div className="placeholder" aria-live="polite">{part.title} <span className="typing" /></div>
      </figure>
    );
  }
  return null;
}

function Chain({ part, idx }: { part: Extract<Part, { kind: "chain" }>; idx: number }) {
  const ctx = useCtx();
  const where = `chain${idx}`;
  const [open, setOpen] = useState<string | null>(null);
  const stage = ctx.course.chain.find((s) => s.id === open);
  return (
    <figure>
      <div className="chain">
        {ctx.course.chain.map((s) => (
          <button key={s.id} type="button" aria-expanded={open === s.id}
            className={`stage ${part.hi === s.id ? "hi" : part.hi ? "dim" : ""}`}
            onClick={() => setOpen(open === s.id ? null : s.id)}>
            <span className="id">{s.id}</span>
            <span className="does">{s.does}</span>
          </button>
        ))}
      </div>
      {stage && (
        <div className="def">
          <span><strong>{stage.id}.</strong> {stage.definition}</span>
          <div className="acts">
            <button type="button" className="link" onClick={() => ctx.askAbout({ kind: "term", label: `${stage.id} (the chain)`, key: stage.id })}>Ask the tutor more</button>
            <button type="button" className="link quiet" onClick={() => setOpen(null)}>Close</button>
          </div>
        </div>
      )}
      <figcaption><span><strong>{part.hi ? "Where we are in the chain" : "The whole chain"}.</strong> {part.caption}</span></figcaption>
    </figure>
  );
}

function Turn({ part }: { part: Extract<Part, { kind: "turn" }> }) {
  const ctx = useCtx();
  const st = ctx.state.page.lessons[ctx.lesson.id]?.turns[part.id];
  const settled = st?.status === "settled";
  const [unrolled, setUnrolled] = useState(false);
  const [draft, setDraft] = useDraft(`turn:${ctx.lesson.id}/${part.id}`);
  const log = st?.log ?? [];
  // Turns open one at a time: this one waits while an earlier turn in the lesson is still open.
  const lst = ctx.state.page.lessons[ctx.lesson.id];
  const before = ctx.lesson.turnIds.slice(0, ctx.lesson.turnIds.indexOf(part.id));
  const locked = !settled && before.some((t) => lst?.turns[t]?.status !== "settled");
  const seenAtMount = useRef(log.length); // messages already there when the page opened don't type out
  const lastLearner = [...log].reverse().findIndex((m) => m.who === "learner");
  const streaming = ctx.state.activity.drafts?.[`turn:${ctx.lesson.id}/${part.id}`];
  // The tutor is still on this turn (between messages, running code, making a figure): say so until it's done.
  const working = ctx.state.activity.turn === `${ctx.lesson.id}/${part.id}` && !streaming;
  const doing = { Running: "running code", "Placing a figure": "placing a figure", Reading: "reading" }[ctx.state.activity.main ?? ""] ?? "thinking";
  const exchanges = log.filter((m) => m.text).length;
  const send = () => {
    const t = draft.trim();
    if (!t) return;
    ctx.send({ type: "say", lesson: ctx.lesson.id, turn: part.id, text: t });
    setDraft("");
  };
  // Stay open while the tutor is still writing here, even if it has just settled the turn.
  const showBody = (!settled && !locked) || unrolled || working || !!streaming;
  const where = `turn:${part.id}`;
  return (
    <section className={`turn ${settled ? "settled" : ""} ${locked ? "locked" : ""}`} aria-label={`Your turn: ${part.title}`} id={`turn-${part.id}`}>
      <div className="turn-head">
        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
          <span className="label">Your turn</span>
          <span style={{ fontWeight: 600 }}>{part.title}</span>
        </div>
        {locked && <span className="note">Opens once you've finished the one above</span>}
        {settled && !working && !streaming && (
          <button type="button" className="link" aria-expanded={unrolled} onClick={() => setUnrolled(!unrolled)}>
            {unrolled ? "Hide the conversation" : `Show the conversation (${exchanges} turns)`}
          </button>
        )}
      </div>
      {showBody && (
        <div className="turn-body">
          {part.image && (
            <figure>
              <ZoomImg src={part.image} alt={part.imageCaption ?? part.title} caption={part.imageCaption} />
              {part.imageCaption && <figcaption>{part.imageCaption}</figcaption>}
            </figure>
          )}
          <div className="turn-col">
            {part.lead && <p style={{ margin: 0 }}><Inline text={part.lead} where={where} /></p>}
            {part.prompt && <p style={{ margin: 0 }}><Inline text={part.prompt} where={where} /></p>}
            {/* The streaming draft takes the next log index, so its typing carries on into the final message. */}
            {[...log, ...(streaming ? [{ who: "tutor" as const, text: streaming, at: 0 }] : [])].map((m, i) => "figure" in m && m.figure ? (
              <div key={i} className="msg figure"><ProducedFigure fig={m.figure} compact /></div>
            ) : (
              <div key={i} className={`msg ${m.who}`} aria-live={m.who === "tutor" ? "polite" : undefined}>
                <span className="who">{m.who === "tutor" ? "Tutor" : "You"}</span>
                {m.who === "tutor" ? <Typed text={m.text} where={`${where}-m${i}`} animate={i >= seenAtMount.current} /> : m.text}
              </div>
            ))}
            {working && <span className="typing" aria-live="polite">The tutor is {doing}</span>}
            {!settled && (
              <>
                <label htmlFor={`in-${part.id}`} className="note">{lastLearner < 0 ? "Your answer" : "Your reply"}</label>
                <textarea id={`in-${part.id}`} className="input" rows={3} value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) send(); }} />
                <div className="btn-row">
                  <button type="button" className="btn primary" onClick={send} disabled={!draft.trim()}>Send</button>
                  <span className="note">Ctrl+Enter sends</span>
                </div>
              </>
            )}
          </div>
        </div>
      )}
      {settled && !working && !streaming && (
        <div className="check"><span className="tick" aria-hidden="true">✓</span><span>{st?.summary}</span></div>
      )}
    </section>
  );
}

function Ref({ part }: { part: Extract<Part, { kind: "ref" }> }) {
  const ctx = useCtx();
  return (
    <p style={{ margin: 0 }}>
      {part.text}{" "}
      <button type="button" className="link" style={{ fontSize: 16 }}
        onClick={() => ctx.askAbout({ kind: "video", label: part.videoTitle ?? part.label, src: part.video, at: 0 })}>
        {part.label}
      </button>
    </p>
  );
}
