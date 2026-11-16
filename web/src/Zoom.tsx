import { useEffect, useRef, useState, type ImgHTMLAttributes } from "react";
import { createPortal } from "react-dom";

/** An image that opens full screen on click. In the viewer: click or +/− to zoom, drag or scroll to
 *  move around, Esc or the backdrop to close. */
export function ZoomImg(props: ImgHTMLAttributes<HTMLImageElement> & { caption?: string }) {
  const { caption, ...img } = props;
  const [open, setOpen] = useState(false);
  return (
    <>
      <img {...img} className={`${img.className ?? ""} zoomable`} tabIndex={0} role="button"
        aria-label={`${img.alt ?? "Image"}: open full screen`}
        onClick={() => setOpen(true)}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setOpen(true); } }} />
      {open && <Viewer src={img.src!} alt={img.alt ?? ""} caption={caption} onClose={() => setOpen(false)} />}
    </>
  );
}

const STEPS = [1, 1.5, 2, 3, 4];

function Viewer({ src, alt, caption, onClose }: { src: string; alt: string; caption?: string; onClose: () => void }) {
  const [step, setStep] = useState(0);
  const [fitW, setFitW] = useState<number | null>(null); // width that fills the screen at 100%
  const box = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; sl: number; st: number; moved: boolean } | null>(null);
  const zoom = STEPS[step];

  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      else if (e.key === "+" || e.key === "=") setStep((s) => Math.min(s + 1, STEPS.length - 1));
      else if (e.key === "-") setStep((s) => Math.max(s - 1, 0));
    };
    window.addEventListener("keydown", k);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { window.removeEventListener("keydown", k); document.body.style.overflow = prev; };
  }, [onClose]);

  // Zooming keeps the point you clicked under the pointer.
  const zoomAt = (next: number, cx?: number, cy?: number) => {
    const el = box.current;
    if (!el) return setStep(next);
    const r = el.getBoundingClientRect();
    const px = (cx ?? r.left + r.width / 2) - r.left, py = (cy ?? r.top + r.height / 2) - r.top;
    const fx = (el.scrollLeft + px) / el.scrollWidth, fy = (el.scrollTop + py) / el.scrollHeight;
    setStep(next);
    requestAnimationFrame(() => { el.scrollLeft = fx * el.scrollWidth - px; el.scrollTop = fy * el.scrollHeight - py; });
  };

  return createPortal(
    <div className="viewer" role="dialog" aria-modal="true" aria-label={alt || "Image viewer"}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="viewer-bar">
        <span className="viewer-cap">{caption || alt}</span>
        <button type="button" className="btn" onClick={() => zoomAt(Math.max(step - 1, 0))} disabled={step === 0} aria-label="Zoom out">−</button>
        <span className="viewer-z">{Math.round(zoom * 100)}%</span>
        <button type="button" className="btn" onClick={() => zoomAt(Math.min(step + 1, STEPS.length - 1))} disabled={step === STEPS.length - 1} aria-label="Zoom in">+</button>
        <button type="button" className="btn" onClick={onClose} aria-label="Close">Close</button>
      </div>
      <div ref={box} className={`viewer-box ${zoom > 1 ? "zoomed" : ""}`}
        onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
        onPointerDown={(e) => { const el = box.current!; drag.current = { x: e.clientX, y: e.clientY, sl: el.scrollLeft, st: el.scrollTop, moved: false }; }}
        onPointerMove={(e) => {
          const d = drag.current; if (!d || zoom === 1) return;
          if (Math.abs(e.clientX - d.x) + Math.abs(e.clientY - d.y) > 4) d.moved = true;
          box.current!.scrollLeft = d.sl - (e.clientX - d.x); box.current!.scrollTop = d.st - (e.clientY - d.y);
        }}
        onPointerUp={() => { setTimeout(() => { drag.current = null; }, 0); }}>
        <img src={src} alt={alt} draggable={false}
          onLoad={(e) => {
            const im = e.currentTarget, el = box.current!;
            const fit = Math.min((el.clientWidth - 16) / im.naturalWidth, (el.clientHeight - 16) / im.naturalHeight);
            setFitW(Math.round(im.naturalWidth * fit));
          }}
          style={fitW ? { width: fitW * zoom, maxWidth: "none", maxHeight: "none" } : undefined}
          onClick={(e) => {
            if (drag.current?.moved) return;
            zoomAt(step === STEPS.length - 1 ? 0 : Math.min(step + 2, STEPS.length - 1), e.clientX, e.clientY);
          }} />
      </div>
    </div>,
    document.body,
  );
}
