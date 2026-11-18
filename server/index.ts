// cuPhoton Learn server: one learner, on the GPU machine, reached over an SSH tunnel.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { WebSocketServer, type WebSocket } from "ws";
import { config } from "./config.ts";
import { courseOutline, loadCourse, publicLesson } from "./content.ts";
import { QUEUE, Store, type Pointer, type Thread } from "./state.ts";
import { Tutor } from "./tutor.ts";
import { Admin } from "./admin.ts";
import { pingEndpoint } from "./endpoint.ts";

const course = loadCourse();
const lessonTurns = new Map([...course.lessons].map(([id, l]) => [id, l.turnIds]));
const store = new Store();
const tutor = new Tutor(course, store, lessonTurns);
const admin = new Admin(tutor);
tutor.onMetric = (m) => admin.record(m);

const MIME: Record<string, string> = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
  ".mp4": "video/mp4", ".vtt": "text/vtt", ".srt": "text/plain; charset=utf-8", ".woff2": "font/woff2", ".ico": "image/x-icon",
};

function sendFile(req: http.IncomingMessage, res: http.ServerResponse, file: string, extra: http.OutgoingHttpHeaders = {}) {
  let st: fs.Stats;
  try { st = fs.statSync(file); if (!st.isFile()) throw 0; } catch { res.writeHead(404).end(); return; }
  const type = MIME[path.extname(file).toLowerCase()] ?? "application/octet-stream";
  const range = req.headers.range?.match(/bytes=(\d*)-(\d*)/);
  if (range && type === "video/mp4") { // videos need range requests to seek
    const start = range[1] ? Number(range[1]) : 0;
    const end = range[2] ? Number(range[2]) : st.size - 1;
    res.writeHead(206, { "content-type": type, "content-range": `bytes ${start}-${end}/${st.size}`, "accept-ranges": "bytes", "content-length": end - start + 1 });
    fs.createReadStream(file, { start, end }).pipe(res);
    return;
  }
  res.writeHead(200, { "content-type": type, "content-length": st.size, "accept-ranges": "bytes", "cache-control": "no-cache", ...extra });
  fs.createReadStream(file).pipe(res);
}

// Serve only files inside `base`, and only with an allowed extension.
function under(base: string, rel: string, allow: RegExp) {
  const p = path.resolve(base, decodeURIComponent(rel));
  return p.startsWith(base + path.sep) && allow.test(p) ? p : null;
}
const IMG = /\.(png|jpe?g|gif|svg|webp)$/i;

// The Files panel: read-only views of the learner's work folder. Nothing here writes; paths are
// relative to work/ and can't leave it.
const WORK = () => path.join(config.learnerDir, "work");
const TEXT = /\.(py|ya?ml|json|jsonl|txt|md|log|csv|tsv|sh|toml|cfg|ini|out|err)$/i;
const SKIP_DIR = /^(__pycache__|\.git|node_modules|\.ipynb_checkpoints)$/;
function fileKind(name: string) {
  return TEXT.test(name) ? "text" : IMG.test(name) ? "image" : /\.html$/i.test(name) ? "html" : "other";
}
function listWork(dir: string) {
  const root = dir ? under(WORK(), dir, /./) : null;
  if (!root || !fs.existsSync(root) || !fs.statSync(root).isDirectory()) return { dir, files: [] };
  const files: { path: string; size: number; kind: string }[] = [];
  const walk = (d: string, depth: number) => {
    let ents: fs.Dirent[];
    try { ents = fs.readdirSync(d, { withFileTypes: true }); } catch { return; }
    ents.sort((a, b) => Number(b.isFile()) - Number(a.isFile()) || a.name.localeCompare(b.name));
    for (const e of ents) {
      if (files.length >= 800) return;
      const full = path.join(d, e.name);
      if (e.isDirectory()) { if (depth < 5 && !SKIP_DIR.test(e.name)) walk(full, depth + 1); }
      else if (e.isFile()) files.push({ path: path.relative(root, full), size: fs.statSync(full).size, kind: fileKind(e.name) });
    }
  };
  walk(root, 0);
  return { dir, files };
}
const MAX_TEXT = 512 * 1024;
function readWork(rel: string) {
  const f = under(WORK(), rel, TEXT);
  if (!f || !fs.existsSync(f) || !fs.statSync(f).isFile() || !fs.realpathSync(f).startsWith(fs.realpathSync(WORK()) + path.sep))
    return { error: "not a text file in your work folder" };
  const size = fs.statSync(f).size;
  const fd = fs.openSync(f, "r");
  const buf = Buffer.alloc(Math.min(size, MAX_TEXT));
  fs.readSync(fd, buf, 0, buf.length, 0);
  fs.closeSync(fd);
  return { path: rel, size, truncated: size > MAX_TEXT, text: buf.toString("utf8") };
}

function notes() {
  if (!fs.existsSync(QUEUE())) return [];
  return fs.readFileSync(QUEUE(), "utf8").split("\n").filter(Boolean).map((l) => {
    try { const j = JSON.parse(l); return { ts: j.ts, kind: j.kind, summary: j.summary }; } catch { return null; }
  }).filter(Boolean);
}

function snapshot() {
  const boxes = Object.fromEntries([...course.lessons.values()].map((l) => [l.id, store.boxState(l.id, l.turnIds)]));
  return { type: "state", page: store.page, boxes, activity: tutor.activity, notes: notes() };
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url ?? "/", "http://x");
  const p = url.pathname;
  const json = (o: unknown, code = 200) => { res.writeHead(code, { "content-type": "application/json" }).end(JSON.stringify(o)); };
  if (p === "/api/course") {
    return json({ title: course.title, guideUrl: course.guideUrl, modules: courseOutline(course), chain: course.chain, glossary: [...course.glossary.values()], order: course.order, videos: course.videos });
  }
  if (p.startsWith("/api/lesson/")) {
    const l = course.lessons.get(decodeURIComponent(p.slice("/api/lesson/".length)));
    return l ? json(publicLesson(l)) : json({ error: "no such lesson" }, 404);
  }
  // The learner's files, read-only: a module's work folder listed, and one text file's contents.
  if (p === "/api/files" || p === "/api/file") {
    try {
      if (p === "/api/files") return json(listWork(url.searchParams.get("dir") ?? ""));
      const r = readWork(url.searchParams.get("path") ?? "");
      return "error" in r ? json(r, 404) : json(r);
    } catch { return json({ error: "can't read that" }, 400); }
  }
  // The admin page: how the tutor is doing (context, waits, errors, spend, the machine). Read-only,
  // except "ping", which spends one small model call.
  if (p === "/admin") return sendFile(req, res, path.join(import.meta.dirname, "admin.html"));
  if (p === "/api/admin") { admin.report().then(json, (e) => json({ error: String(e?.message ?? e) }, 500)); return; }
  if (p === "/api/admin/ping" && req.method === "POST") {
    pingEndpoint().then((r) => { admin.record({ kind: "ping", ok: r.ok, seconds: r.seconds, detail: r.detail }); json(r); });
    return;
  }
  if (p === "/api/health") return json({ ok: true, model: `${config.provider}/${config.model}`, lessons: course.order.length });
  if (p.startsWith("/media/") && p.endsWith(".vtt")) { // subtitles: the .srt next to the video, as WebVTT
    const f = under(config.mediaDir, p.slice(7).replace(/\.vtt$/, ".srt"), /\.srt$/);
    if (!f || !fs.existsSync(f)) return json({ error: "not found" }, 404);
    const vtt = "WEBVTT\n\n" + fs.readFileSync(f, "utf8").replace(/(\d\d:\d\d:\d\d),(\d\d\d)/g, "$1.$2");
    res.writeHead(200, { "content-type": "text/vtt" }).end(vtt);
    return;
  }
  if (p.startsWith("/media/")) {
    const f = under(config.mediaDir, p.slice(7), /\.(mp4|srt|vtt|png|jpe?g)$/i);
    return f ? sendFile(req, res, f) : json({ error: "not found" }, 404);
  }
  if (p.startsWith("/course-files/")) {
    const f = under(path.join(config.courseDir, "modules"), p.slice("/course-files/modules/".length), IMG);
    return f ? sendFile(req, res, f) : json({ error: "not found" }, 404);
  }
  if (p.startsWith("/workspace/")) {
    const rel = p.slice("/workspace/work/".length);
    // Exported reports (e.g. an xLens dashboard) open in their own tab, sandboxed: an opaque origin with
    // no access to this app, and no network.
    if (/\.html$/i.test(rel)) {
      const f = under(path.join(config.learnerDir, "work"), rel, /\.html$/i);
      return f ? sendFile(req, res, f, { "content-security-policy": "sandbox allow-scripts; connect-src 'none'" }) : json({ error: "not found" }, 404);
    }
    const f = under(path.join(config.learnerDir, "work"), rel, IMG);
    return f ? sendFile(req, res, f) : json({ error: "not found" }, 404);
  }
  // the built page
  const f = under(config.webDist, p === "/" ? "index.html" : p.slice(1), /./) ?? path.join(config.webDist, "index.html");
  if (!fs.existsSync(f)) return sendFile(req, res, path.join(config.webDist, "index.html"));
  sendFile(req, res, f);
});

const wss = new WebSocketServer({ server, path: "/ws" });
const clients = new Set<WebSocket>();
let pending: NodeJS.Timeout | null = null;
const broadcast = () => {
  if (pending) return;
  pending = setTimeout(() => {
    pending = null;
    const msg = JSON.stringify(snapshot());
    for (const c of clients) c.send(msg);
  }, 30);
};
store.onChange(broadcast);
tutor.onActivity = broadcast;
tutor.onNote = broadcast;

const newId = () => Math.random().toString(36).slice(2, 10);

wss.on("connection", (ws) => {
  clients.add(ws);
  ws.send(JSON.stringify(snapshot()));
  ws.on("close", () => clients.delete(ws));
  ws.on("message", async (raw) => {
    let m: any;
    try { m = JSON.parse(String(raw)); } catch { return; }
    try {
      switch (m.type) {
        case "open": {
          const l = course.lessons.get(m.lesson);
          if (l) tutor.lessonOpened(l);
          break;
        }
        case "say":
          if (typeof m.text === "string" && m.text.trim()) tutor.learnerSays(m.lesson, m.turn, m.text.trim());
          break;
        case "thread.new": {
          const about: Pointer | undefined = m.about ?? undefined;
          const t: Thread = { id: newId(), from: m.from, about, title: (m.question as string).slice(0, 80), messages: [], open: true };
          store.page.threads.forEach((x) => (x.open = false));
          store.page.threads.push(t);
          await askThread(t, m.question);
          break;
        }
        case "thread.ask": {
          const t = store.page.threads.find((x) => x.id === m.id);
          if (t) { t.open = true; await askThread(t, m.question); }
          break;
        }
        case "thread.open": {
          store.page.threads.forEach((x) => (x.open = x.id === m.id));
          store.save();
          break;
        }
        case "thread.close": {
          const t = store.page.threads.find((x) => x.id === m.id);
          if (t) { t.open = false; tutor.closeThread(t); store.save(); }
          break;
        }
        case "consent":
          store.page.feedbackConsent = !!m.value;
          store.save(lessonTurns);
          break;
      }
    } catch (e: any) {
      console.error("[ws]", e?.message ?? e);
    }
  });
});

async function askThread(t: Thread, q: string) {
  if (!q?.trim()) return;
  t.messages.push({ who: "learner", text: q.trim(), at: Date.now() });
  store.save();
  try {
    const a = await tutor.marginAsk(t, q.trim());
    if (a) t.messages.push({ who: "tutor", text: a, at: Date.now() });
  } catch (e: any) {
    console.error("[margin]", e?.message ?? e);
    t.messages.push({ who: "tutor", text: "I couldn't reach the model just now. Ask again in a moment.", at: Date.now() });
  }
  store.save();
}

await tutor.init();
server.listen(config.port, config.host, () => {
  console.log(`cuPhoton Learn on http://${config.host}:${config.port}  (tutor ${config.provider}/${config.model}; ${course.order.length} lessons)`);
});
