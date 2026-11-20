// Who may use this course. The tutor runs shell commands on this machine, so reaching the page means
// reaching a shell: on a shared link (a Brev launchable, a forwarded port) that must be the learner only.
//
// The first browser to open a page claims the course: the server makes a random token (learner/access.json),
// sets it as a cookie, and from then on every request and the WebSocket need it. Another browser gets a page
// saying how to get in: the access link in learner/access-link.txt (also in the server log, and on the admin
// page of a browser that's already in). ACCESS=open turns the check off (a machine only you can reach).
import crypto from "node:crypto";
import fs from "node:fs";
import type http from "node:http";
import { config, learnerPath } from "./config.ts";

const FILE = () => learnerPath("access.json");
const LINK = () => learnerPath("access-link.txt");
const COOKIE = () => `cpl_access_${config.port}`; // per port: two servers on one host don't share it
const open = () => process.env.ACCESS === "open";

let token: string | null = null;
function load() {
  if (token) return token;
  try { token = JSON.parse(fs.readFileSync(FILE(), "utf8")).token ?? null; } catch {}
  return token;
}

function claim(): string {
  token = crypto.randomBytes(24).toString("base64url");
  fs.writeFileSync(FILE(), JSON.stringify({ token, claimedAt: new Date().toISOString() }), { mode: 0o600 });
  return token;
}

const same = (a: string, b: string) => a.length === b.length && crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));

function cookieToken(req: http.IncomingMessage) {
  const m = (req.headers.cookie ?? "").split(/;\s*/).find((c) => c.startsWith(COOKIE() + "="));
  return m ? decodeURIComponent(m.slice(COOKIE().length + 1)) : "";
}

function origin(req: http.IncomingMessage) {
  const host = String(req.headers["x-forwarded-host"] ?? req.headers.host ?? `${config.host}:${config.port}`).split(",")[0].trim();
  const proto = String(req.headers["x-forwarded-proto"] ?? "").split(",")[0].trim() || "http";
  return `${proto}://${host}`;
}

/** The link that lets another browser in. */
export function accessLink(req?: http.IncomingMessage) {
  const t = load();
  return t ? `${req ? origin(req) : `http://${config.host}:${config.port}`}/?access=${t}` : null;
}

function writeLink(req: http.IncomingMessage) {
  const link = accessLink(req)!;
  fs.writeFileSync(LINK(), `Open this link in a browser to use this course there (keep it private: it gives access to the tutor and this machine):\n${link}\n`, { mode: 0o600 });
  console.log(`[access] course claimed by the first browser; to open it elsewhere: ${link}  (also in ${LINK()})`);
}

function setCookie(res: http.ServerResponse, t: string, req: http.IncomingMessage) {
  const secure = origin(req).startsWith("https:") ? "; Secure" : "";
  res.setHeader("set-cookie", `${COOKIE()}=${encodeURIComponent(t)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000${secure}`);
}

const PAGES = new Set(["/", "/index.html", "/setup", "/admin"]);

/** Gate one HTTP request. Returns true if it may go on; otherwise it has already answered. */
export function allow(req: http.IncomingMessage, res: http.ServerResponse): boolean {
  if (open()) return true;
  const url = new URL(req.url ?? "/", "http://x");
  const t = load();
  const given = url.searchParams.get("access");
  // The access link: set the cookie and go to the page without the token in the address bar.
  if (given && t && same(given, t)) {
    setCookie(res, t, req);
    url.searchParams.delete("access");
    res.writeHead(302, { location: url.pathname + (url.search || "") }).end();
    return false;
  }
  if (t && same(cookieToken(req), t)) {
    // A state-changing request must come from this course's own pages.
    if (req.method !== "GET" && req.method !== "HEAD" && req.headers.origin && req.headers.origin !== origin(req)) {
      res.writeHead(403, { "content-type": "text/plain" }).end("cross-site request refused");
      return false;
    }
    return true;
  }
  // Nobody has claimed it yet: the first browser to open a page does.
  if (!t && req.method === "GET" && PAGES.has(url.pathname)) {
    setCookie(res, claim(), req);
    writeLink(req);
    return true;
  }
  if (PAGES.has(url.pathname) || (req.headers.accept ?? "").includes("text/html")) {
    res.writeHead(401, { "content-type": "text/html; charset=utf-8" }).end(LOCKED());
  } else {
    res.writeHead(401, { "content-type": "application/json" }).end(JSON.stringify({ error: "this course belongs to another browser; open its access link" }));
  }
  return false;
}

/** Gate the WebSocket: the cookie, and an Origin that is this server. */
export function allowSocket(req: http.IncomingMessage): boolean {
  if (open()) return true;
  const t = load();
  if (!t || !same(cookieToken(req), t)) return false;
  return !req.headers.origin || req.headers.origin === origin(req);
}

/** What the lock page calls the course (course.yaml `brand`); index.ts sets it at startup. */
let brand = "This course";
export function setBrand(b: string) { brand = b; }
const LOCKED = () => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${brand} · In use</title>
<style>body{margin:0;background:#141414;color:#ececec;font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:600px;margin:0 auto;padding:48px 16px}h1{font-size:22px;font-weight:600}code{font:13px ui-monospace,Menlo,monospace;background:#0d0d0d;padding:2px 6px;border-radius:4px}p{color:#a3a3a3}</style></head>
<body><main><h1>This course is open in another browser</h1>
<p>${brand} belongs to the first browser that opened it, because its tutor can run commands on this machine.</p>
<p>If it's yours, open its access link. On the machine, it is in <code>learner/access-link.txt</code>, and in the server's log. In the browser that's already in, it's on the admin page.</p>
<p>To start over with this browser as the owner, delete <code>learner/access.json</code> on the machine and restart the server.</p></main></body></html>`;
