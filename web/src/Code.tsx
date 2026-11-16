import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import python from "highlight.js/lib/languages/python";
import { useMemo } from "react";

hljs.registerLanguage("python", python);
hljs.registerLanguage("bash", bash);

/** A code block with syntax highlighting. Language from a hint (file name or fence tag), else guessed. */
export function Code({ text, lang, className }: { text: string; lang?: string; className?: string }) {
  const html = useMemo(() => {
    const l = lang && /\.py$|^py(thon)?$/.test(lang) ? "python" : lang && /\.sh$|^(ba)?sh|shell|console$/.test(lang) ? "bash" : undefined;
    try {
      return l ? hljs.highlight(text, { language: l }).value : hljs.highlightAuto(text, ["python", "bash"]).value;
    } catch { return null; }
  }, [text, lang]);
  return html != null
    ? <pre className={`hl ${className ?? ""}`} dangerouslySetInnerHTML={{ __html: html }} />
    : <pre className={`hl ${className ?? ""}`}>{text}</pre>;
}
