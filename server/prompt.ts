// The tutor's system prompt: the engine's tutor/SYSTEM.md (the same for every course) with each {{name}}
// filled from the course's tutor/COURSE.md (`<!-- block: name -->` up to the next marker) or from the
// variables below. A placeholder with no block and no variable is an error, so a course can't ship a
// prompt with a hole in it.
import fs from "node:fs";
import path from "node:path";

export type PromptVars = Record<string, string>;

/** COURSE.md's blocks, by name. Text before the first marker is a note for authors and isn't sent. */
export function courseBlocks(file: string): Map<string, string> {
  const blocks = new Map<string, string>();
  if (!fs.existsSync(file)) return blocks;
  const parts = fs.readFileSync(file, "utf8").split(/^<!-- block: ([\w-]+) -->\n/m);
  for (let i = 1; i < parts.length; i += 2) blocks.set(parts[i], parts[i + 1].replace(/\n+$/, ""));
  return blocks;
}

export function fill(text: string, blocks: Map<string, string>, vars: PromptVars, where: string): string {
  // Blocks first (they may use variables), then variables.
  const withBlocks = text.replace(/\{\{([\w-]+)\}\}/g, (m, k) => blocks.get(k) ?? m);
  return withBlocks.replace(/\{\{([\w-]+)\}\}/g, (_, k) => {
    if (k in vars) return vars[k];
    throw new Error(`${where}: {{${k}}} has no block in COURSE.md and no variable`);
  });
}

/** The engine's prompt with the course's blocks in place, and the course's environment lines. */
export function tutorPrompt(tutorDir: string, vars: PromptVars) {
  const blocks = courseBlocks(path.join(tutorDir, "COURSE.md"));
  const system = fill(fs.readFileSync(path.join(tutorDir, "SYSTEM.md"), "utf8"), blocks, vars, "SYSTEM.md");
  const environment = blocks.has("environment") ? fill(blocks.get("environment")!, blocks, vars, "COURSE.md environment") : "";
  return { system, environment };
}
