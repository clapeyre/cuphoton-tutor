import { Fragment, type ReactNode } from "react";
import { heldUntil, lookup, useCtx } from "./ctx.tsx";

/** Inline markup: [[term]] or [[term|shown text]], **bold**, *italic*, `code`. */
export function Inline({ text, where }: { text: string; where: string }) {
  const ctx = useCtx();
  const out: ReactNode[] = [];
  const re = /\[\[(.+?)\]\]|\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`/g;
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
          <button key={n++} type="button" className="term" aria-expanded={open}
            onClick={() => ctx.setDef(open ? null : { where, key: e.key })}>{label}</button>,
        );
      } else out.push(label);
    } else if (m[2]) out.push(<strong key={n++}>{m[2]}</strong>);
    else if (m[3]) out.push(<em key={n++}>{m[3]}</em>);
    else if (m[4]) out.push(<code key={n++}>{m[4]}</code>);
    i = re.lastIndex;
  }
  if (i < text.length) out.push(text.slice(i));
  return <>{out.map((x, k) => <Fragment key={k}>{x}</Fragment>)}</>;
}

/** The short definition, opened beneath what was clicked. Depth layers never show here. */
export function Definition({ where }: { where: string }) {
  const ctx = useCtx();
  if (!ctx.def || ctx.def.where !== where) return null;
  const e = ctx.glossary.get(ctx.def.key);
  if (!e) return null;
  const held = heldUntil(ctx, e);
  return (
    <div className="def" role="region" aria-label={`Definition: ${e.label}`}>
      <span><strong>{e.label}.</strong> {e.definition}</span>
      {held && (
        <span className="held">
          {held === ctx.lesson.id ? "This lesson's Your turn asks about it; we come back to it once you've answered." : `We come back to this in lesson ${held}.`}
        </span>
      )}
      <div className="acts">
        {!held && (
          <button type="button" className="link" onClick={() => { ctx.askAbout({ kind: "term", label: e.label, key: e.key }); }}>
            Ask the tutor more
          </button>
        )}
        <button type="button" className="link quiet" onClick={() => ctx.setDef(null)}>Close</button>
      </div>
    </div>
  );
}
