// Drive the page over its WebSocket, for tests: tsx tools/ws-drive.ts '<json msg>' ... [--wait-idle]
import WebSocket from "ws";
const port = process.env.PORT ?? "8765";
// The server lets in only the browser that claimed the course (server/access.ts): send its cookie.
import fs from "node:fs";
let token = "";
try { token = JSON.parse(fs.readFileSync(`${process.env.LEARNER_DIR ?? "learner"}/access.json`, "utf8")).token; } catch {}
const ws = new WebSocket(`ws://127.0.0.1:${port}/ws`, { headers: token ? { cookie: `cpl_access_${port}=${token}` } : {} });
const msgs = process.argv.slice(2).filter((a) => !a.startsWith("--"));
let last: any = null, sent = false, busySeen = false;
ws.on("message", (raw) => {
  last = JSON.parse(String(raw));
  const busy = last.activity.main || Object.keys(last.activity.threads).length;
  if (busy) busySeen = true;
  if (!sent) { sent = true; for (const m of msgs) ws.send(m); return; }
  if (busySeen && !busy) setTimeout(() => { if (!(last.activity.main || Object.keys(last.activity.threads).length)) { console.log(JSON.stringify(last, null, 1)); process.exit(0); } }, 1500);
});
setTimeout(() => { console.log("TIMEOUT", JSON.stringify(last?.activity)); process.exit(1); }, Number(process.env.WAIT ?? 300000));
