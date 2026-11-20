// Parses course/ into pages. Learner-facing text comes from lesson.md only;
// tutor.md is read here but only ever sent to the tutor, never to the browser.
import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";
import { config } from "./config.ts";

export type Part =
  | { kind: "prose"; text: string }
  | { kind: "code"; text: string; lang?: string }
  | { kind: "video"; id: string; title: string; duration: string; chapters: [number, string][]; src: string }
  | { kind: "figure"; title: string; caption: string; src: string; alt: string }
  | { kind: "slot"; id: string; title: string; caption: string }
  | { kind: "chain"; hi?: string; caption: string }
  | { kind: "turn"; id: string; title: string; prompt?: string; lead?: string; image?: string; imageCaption?: string }
  | { kind: "ref"; text: string; label: string; video?: string; videoTitle?: string };

export interface Lesson {
  id: string;
  module: string;
  slug: string;
  dir: string;
  title: string;
  question: string;
  terms: string[];
  guide: { title: string; url: string }[]; // the user guide's pages this lesson draws on
  parts: Part[];
  closure: { found: string; matters?: string; raises: string } | null;
  intro?: string[]; // the module introduction, on the module's first lesson only
  turnIds: string[];
  slotIds: string[];
  source: string; // lesson.md, for the tutor
  tutorNotes: string; // tutor.md, for the tutor only
}

export interface Module {
  id: string;
  dir: string;
  title: string;
  question: string;
  misconceptions: string[];
  lessons: Lesson[];
}

export interface GlossaryEntry {
  key: string; // normalized look-up key
  label: string;
  definition: string;
  holdUntil?: string; // lesson id whose turns must settle before "ask more" opens
  concept?: boolean;
  link?: { label: string; url: string }; // read_more in vocabulary.yaml
}

/** How the run recorder names what made a figure and where it ran: course.yaml `runs`. */
export interface RunRules {
  stages: string[];
  package?: string;
  core?: { label: string; pattern: string };
  receipts: string[];
  receiptFields: string[];
  gpuBackend?: string;
  gpuCode?: string;
}

export interface Course {
  title: string;
  brand: string; // what the page calls the course ("cuPhoton Learn")
  reportName: string; // the admin page's report archive: <reportName>-<date>-<commit>
  product: string; // the software it teaches ("cuPhoton")
  commit: string;
  guideUrl: string;
  runs: RunRules;
  modules: Module[];
  lessons: Map<string, Lesson>;
  order: string[]; // lesson ids in reading order
  glossary: Map<string, GlossaryEntry>;
  chain: { id: string; does: string; definition: string }[];
  videos: Record<string, { title: string; duration: string; chapters: [number, string][] }>;
}

export const normKey = (s: string) =>
  s.trim().toLowerCase().replace(/\s*\(.*?\)\s*/g, " ").replace(/\s+/g, " ").trim();

function frontmatter(src: string): { meta: Record<string, any>; body: string } {
  const m = src.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return { meta: {}, body: src };
  return { meta: YAML.parse(m[1]) ?? {}, body: src.slice(m[0].length) };
}

// Directive options: "key: value" lines, split on the first colon, so authors
// never need YAML quoting. Indented lines continue the previous value.
function keyValues(lines: string[]): Record<string, string> {
  const out: Record<string, string> = {};
  let last: string | null = null;
  for (const l of lines) {
    const m = l.match(/^([a-z][\w-]*):\s*(.*)$/i);
    if (m) { last = m[1]; out[last] = m[2].trim(); }
    else if (last && l.trim()) out[last] += " " + l.trim();
  }
  return out;
}

// :::name arg\nkey: value\n...\n:::
function parseBody(body: string, lessonDir: string, videos: Course["videos"], lessonId: string): {
  parts: Part[];
  closure: Lesson["closure"];
} {
  const parts: Part[] = [];
  let closure: Lesson["closure"] = null;
  const lines = body.split("\n");
  let para: string[] = [];
  const flush = () => {
    const t = para.join(" ").replace(/\s+/g, " ").trim();
    if (t) parts.push({ kind: "prose", text: t });
    para = [];
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // ``` fenced code block, shown as highlighted code (e.g. a command the learner will ask for)
    const fence = line.match(/^```\s*([\w-]*)\s*$/);
    if (fence) {
      flush();
      const code: string[] = [];
      while (++i < lines.length && !/^```\s*$/.test(lines[i])) code.push(lines[i]);
      parts.push({ kind: "code", lang: fence[1] || undefined, text: code.join("\n") });
      continue;
    }
    const d = line.match(/^:::([a-z-]+)\s*(.*)$/);
    if (!d) {
      if (line.trim() === "") flush();
      else para.push(line);
      continue;
    }
    flush();
    const [, name, argStr] = d;
    const block: string[] = [];
    while (++i < lines.length && lines[i].trim() !== ":::") block.push(lines[i]);
    const opts = keyValues(block);
    const arg = argStr.trim();
    const kv = Object.fromEntries(
      arg.split(/\s+/).filter((a) => a.includes("=")).map((a) => a.split("=", 2) as [string, string]),
    );
    const rel = (p: string) => `/course-files/${path.relative(config.courseDir, path.join(lessonDir, p))}`;
    switch (name) {
      case "video": {
        const v = videos[arg];
        if (!v || !fs.existsSync(path.join(config.mediaDir, "videos", `${arg}.mp4`))) {
          console.warn(`[content] ${lessonId}: video ${arg} not found, skipped`);
          break;
        }
        parts.push({ kind: "video", id: arg, title: opts.title ?? v.title, duration: v.duration, chapters: v.chapters ?? [], src: `/media/videos/${arg}.mp4` });
        break;
      }
      case "figure":
        parts.push({ kind: "figure", title: opts.title ?? "", caption: opts.caption ?? "", alt: opts.alt ?? opts.title ?? "", src: rel(arg) });
        break;
      case "slot":
        parts.push({ kind: "slot", id: arg, title: opts.title ?? "", caption: opts.caption ?? "" });
        break;
      case "chain":
        parts.push({ kind: "chain", hi: kv.hi, caption: opts.caption ?? "" });
        break;
      case "your-turn":
        parts.push({
          kind: "turn", id: arg, title: opts.title ?? "", prompt: opts.prompt, lead: opts.lead,
          image: opts.image ? rel(opts.image) : undefined, imageCaption: opts["image-caption"],
        });
        break;
      case "ref":
        parts.push({ kind: "ref", text: opts.text ?? "", label: opts.label ?? "", video: opts.video ? `/media/videos/${opts.video}.mp4` : undefined, videoTitle: opts.video ? videos[opts.video]?.title : undefined });
        break;
      case "closure":
        closure = { found: opts.found ?? "", matters: opts.matters, raises: opts.raises ?? "" };
        break;
      default:
        console.warn(`[content] ${lessonId}: unknown directive :::${name}`);
    }
  }
  flush();
  return { parts, closure };
}

// A guide page by its file name (read-fits): its title from the pinned checkout's guide sources, and its URL.
function guidePage(product: any, name: string) {
  const base = product?.guide ?? "";
  const f = path.join(config.productDir, product?.guide_dir ?? "docs/guide", `${name}${product?.guide_ext ?? ".qmd"}`);
  const t = fs.existsSync(f) ? fs.readFileSync(f, "utf8").match(/^# (.+?)(?:\s*\{[^}]*\})?\s*$/m)?.[1] : undefined;
  return { title: t ?? name, url: `${base}${name}.html` };
}

export function loadCourse(): Course {
  const cy = YAML.parse(fs.readFileSync(path.join(config.courseDir, "course.yaml"), "utf8"));
  const product = cy.product ?? cy.cuphoton ?? {}; // `cuphoton:` was this block's name before 20 Nov 2026
  const videosFile = path.join(config.mediaDir, "videos.yaml");
  const videos = fs.existsSync(videosFile) ? YAML.parse(fs.readFileSync(videosFile, "utf8")) ?? {} : {};
  const modules: Module[] = [];
  const lessons = new Map<string, Lesson>();
  const order: string[] = [];
  for (const udir of cy.modules as string[]) {
    const ud = path.join(config.courseDir, "modules", udir);
    if (!fs.existsSync(path.join(ud, "module.yaml"))) continue; // listed but not written yet
    const uy = YAML.parse(fs.readFileSync(path.join(ud, "module.yaml"), "utf8"));
    const module: Module = { id: String(uy.id), dir: udir, title: uy.title, question: uy.question ?? "", misconceptions: uy.misconceptions ?? [], lessons: [] };
    const ldirs = fs.readdirSync(ud).filter((d) => fs.existsSync(path.join(ud, d, "lesson.md"))).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
    for (const ld of ldirs) {
      const dir = path.join(ud, ld);
      const source = fs.readFileSync(path.join(dir, "lesson.md"), "utf8");
      const { meta, body } = frontmatter(source);
      const id = String(meta.id ?? ld.split("-")[0]);
      const { parts, closure } = parseBody(body, dir, videos, id);
      const notesFile = path.join(dir, "tutor.md");
      const lesson: Lesson = {
        id, module: module.id, slug: ld, dir, title: meta.title ?? ld, question: meta.question ?? "",
        terms: (meta.terms ?? []).map(String), guide: (meta.guide ?? []).map((g: string) => guidePage(product, String(g))), parts, closure,
        turnIds: parts.flatMap((p) => (p.kind === "turn" ? [p.id] : [])),
        slotIds: parts.flatMap((p) => (p.kind === "slot" ? [p.id] : [])),
        source, tutorNotes: fs.existsSync(notesFile) ? fs.readFileSync(notesFile, "utf8") : "",
      };
      // A module's intro (module.yaml `intro`, paragraphs separated by blank lines) opens its first lesson.
      if (!module.lessons.length && uy.intro) lesson.intro = String(uy.intro).split(/\n\s*\n/).map((p) => p.replace(/\s+/g, " ").trim()).filter(Boolean);
      module.lessons.push(lesson);
      lessons.set(id, lesson);
      order.push(id);
    }
    modules.push(module);
  }
  const r = cy.runs ?? {};
  const runs: RunRules = {
    stages: (r.stages ?? []).map(String), package: r.package, core: r.core,
    receipts: r.receipts ?? ["summary.json"], receiptFields: r.receipt_fields ?? ["backend", "device"],
    gpuBackend: r.gpu_backend, gpuCode: r.gpu_code,
  };
  const name = String(product.name ?? "");
  return { title: cy.title, brand: String(cy.brand ?? cy.title), reportName: String(cy.report_name ?? `${cy.id ?? "course"}-report`), product: name, commit: product.commit ?? "", guideUrl: product.guide ?? "", runs, modules, lessons, order, glossary: loadGlossary(), chain: cy.chain ?? [], videos };
}

// read_more: "Label | https://…" — one outside page that explains the idea in more depth.
function readMore(v: unknown): { label: string; url: string } | undefined {
  const m = typeof v === "string" ? v.match(/^(.*?)\s*\|\s*(https?:\/\/\S+)$/) : null;
  return m ? { label: m[1], url: m[2] } : undefined;
}

function loadGlossary(): Map<string, GlossaryEntry> {
  const g = new Map<string, GlossaryEntry>();
  const voc = YAML.parse(fs.readFileSync(path.join(config.courseDir, "vocabulary.yaml"), "utf8"));
  for (const t of voc.terms ?? []) {
    const hold = typeof t.hold_back === "string" ? t.hold_back.match(/checkpoint (\d+\.\d+)/i)?.[1] ?? t.hold_back.match(/(\d+\.\d+)/)?.[1] : undefined;
    const names = String(t.term).split(/,(?![^(]*\))/).map((s) => s.trim());
    const label = String(t.term).replace(/\s*\(.*?\)\s*$/, "");
    for (const n of names) {
      const e: GlossaryEntry = { key: normKey(n), label: names.length > 1 ? n : label, definition: t.definition, holdUntil: hold, link: readMore(t.read_more) };
      g.set(e.key, e);
      // "PSF (point-spread function)" is also reachable as "point-spread function"
      const paren = String(n).match(/\((.*?)\)/)?.[1];
      if (paren && !/^(counts|in the sky|matching kernel|sample)$/i.test(paren)) g.set(normKey(paren), { ...e, key: normKey(paren) });
    }
  }
  const con = YAML.parse(fs.readFileSync(path.join(config.courseDir, "concepts.yaml"), "utf8"));
  for (const c of con.concepts ?? []) {
    const label = String(c.id).replace(/-/g, " ").replace(/^./, (s: string) => s.toUpperCase());
    // Only the L0 picture is ever shown; deeper layers are for the tutor.
    g.set("@" + c.id, { key: "@" + c.id, label, definition: String(c.layers?.L0 ?? "").trim(), concept: true });
  }
  return g;
}

// What the browser gets: no tutor notes, no lesson source.
export function publicLesson(l: Lesson) {
  const { source, tutorNotes, dir, ...rest } = l;
  return rest;
}

export function courseOutline(c: Course) {
  return c.modules.map((u) => ({ id: u.id, title: u.title, lessons: u.lessons.map((l) => ({ id: l.id, title: l.title, turns: l.turnIds.length })) }));
}
