import { Fragment, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Code } from "./Code.tsx";
import { heldUntil, lookup, useCtx } from "./ctx.tsx";

/** Inline markup: [[term]] or [[term|shown text]], [text](https://…), **bold**, *italic*, `code`. */
export function Inline({ text, where }: { text: string; where: string }) {
  const ctx = useCtx();
  const out: ReactNode[] = [];
  const re = /\[\[(.+?)\]\]|\[([^\]]+)\]\((https?:\/\/(?:[^()\s]|\([^()\s]*\))+)\)|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`/g;
  let i = 0, m: RegExpExecArray | null, n = 0;
  while ((m = re.exec(text))) {
    if (m.index > i) out.push(text.slice(i, m.index));
    if (m[1]) {
      const [raw, shown] = m[1].split("|");
      const e = lookup(ctx.glossary, raw);
      const label = shown ?? (raw.startsWith("@") ? e?.label ?? raw : raw);
      if (e) {
        const open = ctx.def?.where === where && ctx.def.key === e.key;
        out.push(
          <button key={n++} type="button" className="term" aria-expanded={open} aria-haspopup="dialog"
            onClick={(ev) => {
              const r = (ev.currentTarget as HTMLElement).getBoundingClientRect();
              ctx.setDef(open ? null : { where, key: e.key, anchor: { x: r.left + window.scrollX, y: r.bottom + window.scrollY, top: r.top + window.scrollY } });
            }}>{label}</button>,
        );
      } else out.push(label);
    } else if (m[2]) out.push(<a key={n++} href={m[3]} target="_blank" rel="noopener noreferrer" className="ext">{m[2]}</a>);
    else if (m[4]) out.push(<strong key={n++}>{m[4]}</strong>);
    else if (m[5]) out.push(<em key={n++}>{m[5]}</em>);
    else if (m[6]) out.push(<code key={n++}>{m[6]}</code>);
    i = re.lastIndex;
  }
  if (i < text.length) out.push(text.slice(i));
  return <>{out.map((x, k) => <Fragment key={k}>{x}</Fragment>)}</>;
}

/** The short definition, floating under the term that was clicked. One at a time; Esc or a click outside closes it. */
export function TermPopover() {
  const ctx = useCtx();
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null);
  const d = ctx.def;
  useLayoutEffect(() => {
    if (!d || !ref.current) return setPos(null);
    const w = ref.current.offsetWidth, h = ref.current.offsetHeight;
    const left = Math.max(16, Math.min(d.anchor.x, window.scrollX + document.documentElement.clientWidth - w - 16));
    // Below the term, unless that runs off the bottom of the window and there's room above.
    const below = d.anchor.y + 6;
    const top = below + h > window.scrollY + window.innerHeight && d.anchor.top - h - 6 > window.scrollY ? d.anchor.top - h - 6 : below;
    setPos({ left, top });
  }, [d]);
  useEffect(() => {
    if (!d) return;
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") ctx.setDef(null); };
    const click = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      if (ref.current?.contains(t) || t.closest(".term")) return;
      ctx.setDef(null);
    };
    window.addEventListener("keydown", key);
    window.addEventListener("mousedown", click);
    return () => { window.removeEventListener("keydown", key); window.removeEventListener("mousedown", click); };
  }, [d, ctx]);
  if (!d) return null;
  const e = ctx.glossary.get(d.key);
  if (!e) return null;
  const held = heldUntil(ctx, e);
  return createPortal(
    <div ref={ref} className="def pop" role="dialog" aria-label={`Definition: ${e.label}`}
      style={{ left: pos?.left ?? d.anchor.x, top: pos?.top ?? d.anchor.y, visibility: pos ? "visible" : "hidden" }}>
      <span><strong>{e.label}.</strong> {e.definition}</span>
      {e.link && (
        <a className="ext" href={e.link.url} target="_blank" rel="noopener noreferrer">{e.link.label}</a>
      )}
      {held && (
        <span className="held">
          {held === ctx.lesson.id ? "This lesson's Your turn asks about it; we come back to it once you've answered." : `We come back to this in lesson ${held}.`}
        </span>
      )}
      <div className="acts">
        {!held && (
          <button type="button" className="link" onClick={() => { ctx.setDef(null); ctx.askAbout({ kind: "term", label: e.label, key: e.key }); }}>
            Ask the tutor more
          </button>
        )}
        <button type="button" className="link quiet" onClick={() => ctx.setDef(null)}>Close</button>
      </div>
    </div>,
    document.body,
  );
}

/** A tutor message: paragraphs with inline markup, and ``` code blocks. */
export function MessageText({ text, where }: { text: string; where: string }) {
  // Split on ``` fences. Odd blocks are code; code block i was opened by fence i-1, whose tag is langs[i - 1].
  const blocks: string[] = [], langs: string[] = [];
  text.split(/```([\w-]*)\n?/).forEach((b, i) => (i % 2 === 1 ? langs.push(b) : blocks.push(b)));
  const seq: { code: boolean; text: string; lang?: string }[] = blocks.map((b, i) => ({ code: i % 2 === 1, text: b, lang: langs[i - 1] }));
  return (
    <>
      {seq.map((b, i) => b.code
        ? <Code key={i} text={b.text.replace(/\n$/, "")} lang={b.lang || undefined} className="msg-code" />
        : b.text.split(/\n\s*\n/).filter((p) => p.trim()).map((p, j) => (
            <p key={`${i}-${j}`} className="msg-p"><Inline text={p.trim()} where={`${where}-${i}-${j}`} /></p>
          )))}
    </>
  );
}

/** Types `text` out at a steady pace (catching up with streamed chunks), then shows it whole.
 *  Keep the same React key from the streaming draft to the final message so typing continues. */
export function Typed({ text, where, animate }: { text: string; where: string; animate: boolean }) {
  const [n, setN] = useState(animate ? 0 : text.length);
  const target = useRef(text.length);
  target.current = text.length;
  useEffect(() => {
    if (n >= text.length) return;
    let raf = 0, last = performance.now(), pos = n;
    const step = (t: number) => {
      const dt = Math.min(100, t - last); last = t;
      const remaining = target.current - pos;
      // ~90 chars/s at rest, faster when far behind, so it never lags a chunk by much.
      pos = Math.min(target.current, pos + Math.max(0.09 * dt, remaining * dt / 600));
      setN(Math.floor(pos));
      if (pos < target.current) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [text]); // eslint-disable-line react-hooks/exhaustive-deps
  return <MessageText text={text.slice(0, n)} where={where} />;
}
