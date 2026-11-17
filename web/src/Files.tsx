import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Code } from "./Code.tsx";
import type { WorkFile } from "./types.ts";

/** The files the learner and the tutor wrote in one module's work folder. Read-only: changes go through
 *  the tutor. Floats over the page, so the lesson and its conversations stay usable underneath. */
export function FilesPanel({ dirs, dir, setDir, files, path, setPath, onClose, refresh }: {
  dirs: string[]; dir: string; setDir: (d: string) => void; files: WorkFile[];
  path: string | null; setPath: (p: string | null) => void; onClose: () => void; refresh: () => void;
}) {
  const [doc, setDoc] = useState<{ path: string; text?: string; size?: number; truncated?: boolean; error?: string } | null>(null);
  const [filter, setFilter] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const file = files.find((f) => f.path === path);

  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [onClose]);
  useEffect(() => { ref.current?.focus(); }, []);

  useEffect(() => {
    if (!path || !file || file.kind !== "text") return setDoc(null);
    let stop = false;
    setDoc({ path });
    fetch(`/api/file?path=${encodeURIComponent(`${dir}/${path}`)}`).then((r) => r.json())
      .then((j) => { if (!stop) setDoc({ path, ...j }); })
      .catch(() => { if (!stop) setDoc({ path, error: "couldn't load it" }); });
    return () => { stop = true; };
  }, [dir, path, file?.size]); // eslint-disable-line react-hooks/exhaustive-deps

  const shown = useMemo(() => {
    const q = filter.trim().toLowerCase();
    return q ? files.filter((f) => f.path.toLowerCase().includes(q)) : files;
  }, [files, filter]);

  const src = `/workspace/work/${dir}/${path ?? ""}`;
  return createPortal(
    <div ref={ref} tabIndex={-1} className="files" role="dialog" aria-label={`Your files in work/${dir}`}>
      <div className="files-bar">
        <span className="small-caps">Your files</span>
        <label className="note" htmlFor="files-dir">work/</label>
        <select id="files-dir" value={dir} onChange={(e) => { setDir(e.target.value); setPath(null); }}>
          {dirs.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
        <span className="note files-ro">Read-only. To change a file, ask the tutor.</span>
        <button type="button" className="btn tertiary small" onClick={refresh}>Refresh</button>
        <button type="button" className="btn tertiary small" onClick={onClose}>Close</button>
      </div>
      <div className="files-main">
        <nav className="files-list" aria-label="Files">
          <input className="input files-filter" placeholder="Filter" value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filter files" />
          {shown.length === 0 && <span className="note">{files.length ? "No match." : "Nothing here yet."}</span>}
          {shown.map((f) => (
            <button key={f.path} type="button" className={`files-item ${f.path === path ? "cur" : ""} ${f.kind}`}
              onClick={() => setPath(f.path)} title={`${f.path} · ${fmtSize(f.size)}`}>
              {f.path.includes("/") && <span className="files-dirpart">{f.path.slice(0, f.path.lastIndexOf("/") + 1)}</span>}
              <span>{f.path.slice(f.path.lastIndexOf("/") + 1)}</span>
            </button>
          ))}
        </nav>
        <div className="files-view">
          {!path && <p className="note">Pick a file on the left. Code, configurations, logs and summaries open here; figures open full size.</p>}
          {path && file && (
            <div className="files-head">
              <code>work/{dir}/{path}</code> <span className="note">{fmtSize(file.size)}</span>
              {file.kind === "html" && <a className="ext" href={src} target="_blank" rel="noopener noreferrer">Open in a new tab</a>}
            </div>
          )}
          {path && !file && <p className="note">No file <code>{path}</code> in work/{dir}.</p>}
          {file?.kind === "image" && <img className="files-img" src={`${src}?v=${file.size}`} alt={path ?? ""} />}
          {file?.kind === "other" && <p className="note">This file isn't text (a table, an image cube or a binary), so it can't be shown here. Ask the tutor what's in it.</p>}
          {file?.kind === "html" && <p className="note">An exported report: it opens in its own tab.</p>}
          {file?.kind === "text" && doc?.error && <p className="note">{doc.error}</p>}
          {file?.kind === "text" && doc?.text != null && <FileText path={doc.path} text={doc.text} truncated={!!doc.truncated} />}
        </div>
      </div>
    </div>,
    document.body,
  );
}

function FileText({ path, text, truncated }: { path: string; text: string; truncated: boolean }) {
  const lines = text.endsWith("\n") ? text.slice(0, -1) : text;
  const n = lines.split("\n").length;
  const highlight = text.length < 200_000 && /\.(py|ya?ml|json|sh)$/i.test(path);
  return (
    <>
      <div className="files-text">
        <pre className="files-gutter" aria-hidden="true">{Array.from({ length: n }, (_, i) => i + 1).join("\n")}</pre>
        {highlight ? <Code text={lines} lang={path} className="files-code" /> : <pre className="hl files-code">{lines}</pre>}
      </div>
      {truncated && <p className="note">Only the first 512 KB are shown.</p>}
    </>
  );
}

const fmtSize = (b: number) => b < 1024 ? `${b} B` : b < 1024 ** 2 ? `${(b / 1024).toFixed(1)} KB` : `${(b / 1024 ** 2).toFixed(1)} MB`;

/** A file name the tutor wrote (`config.yaml`, `run1/summary.json`, `work/05/config.yaml`) resolved
 *  against the module's work folder, or null when there's no such file. */
export function resolveWorkPath(files: WorkFile[], dir: string, raw: string): string | null {
  let s = raw.trim().replace(/^\.\//, "");
  if (!/^[\w./-]+$/.test(s) || !/\.\w+$/.test(s)) return null;
  s = s.replace(new RegExp(`^(learner/)?work/${dir}/`), "");
  if (files.some((f) => f.path === s)) return s;
  if (!s.includes("/")) {
    const m = files.filter((f) => f.path.endsWith("/" + s) || f.path === s);
    if (m.length === 1) return m[0].path;
  }
  return null;
}
