// cuPhoton Learn server: one learner, on the GPU machine, reached over an SSH tunnel.
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { WebSocketServer, type WebSocket } from "ws";
import { config } from "./config.ts";
import { courseOutline, loadCourse, publicLesson } from "./content.ts";
import { QUEUE, Store, type Pointer, type Thread } from "./state.ts";
import { Tutor } from "./tutor.ts";

const course = loadCourse();
const lessonTurns = new Map([...course.lessons].map(([id, l]) => [id, l.turnIds]));
const store = new Store();
const tutor = new Tutor(course, store, lessonTurns);

const MIME: Record<string, string> = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
  ".mp4": "video/mp4", ".vtt": "text/vtt", ".srt": "text/plain; charset=utf-8", ".woff2": "font/woff2", ".ico": "image/x-icon",
};

function sendFile(req: http.IncomingMessage, res: http.ServerResponse, file: string) {
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
  res.writeHead(200, { "content-type": type, "content-length": st.size, "accept-ranges": "bytes", "cache-control": "no-cache" });
  fs.createReadStream(file).pipe(res);
}

// Serve only files inside `base`, and only with an allowed extension.
function under(base: string, rel: string, allow: RegExp) {
  const p = path.resolve(base, decodeURIComponent(rel));
  return p.startsWith(base + path.sep) && allow.test(p) ? p : null;
}
const IMG = /\.(png|jpe?g|gif|svg|webp)$/i;

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
    return json({ title: course.title, units: courseOutline(course), chain: course.chain, glossary: [...course.glossary.values()], order: course.order, videos: course.videos });
  }
  if (p.startsWith("/api/lesson/")) {
    const l = course.lessons.get(decodeURIComponent(p.slice("/api/lesson/".length)));
    return l ? json(publicLesson(l)) : json({ error: "no such lesson" }, 404);
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
    const f = under(path.join(config.courseDir, "units"), p.slice("/course-files/units/".length), IMG);
    return f ? sendFile(req, res, f) : json({ error: "not found" }, 404);
  }
  if (p.startsWith("/workspace/")) {
    const f = under(path.join(config.learnerDir, "work"), p.slice("/workspace/work/".length), IMG);
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
    t.messages.push({ who: "tutor", text: a, at: Date.now() });
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
