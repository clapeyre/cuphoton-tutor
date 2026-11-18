// What the tutor is doing, step by step, for the page to show during a long request.
/** One thing the tutor did in the learner's current request, for the page to show while it waits. */
export type Step = { id: string; what: string; detail: string; at: number; ms?: number; error?: boolean };

/** A tool call as the learner would describe it: the command that matters, the file looked at (null: not worth showing). */
export function describeStep(tool: string, args: any): { what: string; detail: string } | null {
  if (tool === "bash") {
    const cmd = String(args?.command ?? "");
    // Skip the plumbing (cd, export, mkdir...) and heredoc bodies; keep the first command that does the work.
    const lines: string[] = [];
    let heredoc: string | null = null;
    for (const line of cmd.split("\n")) {
      if (heredoc) { if (line.trim() === heredoc) heredoc = null; continue; }
      const h = line.match(/<<-?\s*['"]?(\w+)['"]?/);
      if (h) heredoc = h[1];
      lines.push(line);
    }
    const parts = lines.join(" ; ").replace(/\$\([^()]*\)/g, "…").split(/\s*(?:&&|;|\|\||\(|\))\s*/).map((x) => x.trim()).filter(Boolean)
      .filter((x) => !/^(?:(?:cd|export|mkdir|set|source|echo|cp|ls|true|EOF)\b|\.\s|cat\s*>|[A-Za-z_]+=)/.test(x));
    const main = (parts[0] ?? cmd.split("\n")[0]).replace(/\s*\|\s*(tail|head)\b.*$/, "").replace(/\s*[12]?>\s*\S+/g, "").replace(/\/home\/[^ ]*\/(learner\/)?/g, "");
    const detail = main.length > 100 ? main.slice(0, 99) + "…" : main;
    return { what: /\btrain-|\btrain\s|\.fit\(/.test(main) ? "Training" : "Running", detail: detail + (parts.length > 1 ? " …" : "") };
  }
  const file = String(args?.path ?? "").split("/").pop() ?? "";
  if (tool === "read") return { what: /\.(png|jpe?g)$/i.test(file) ? "Looking at" : "Reading", detail: file };
  if (tool === "write" || tool === "edit") return { what: "Writing", detail: file };
  if (tool === "show_figure") return { what: "Placing a figure", detail: file };
  return null; // the page tools (settle a turn, note a margin) are quick and show up on the page themselves
}
