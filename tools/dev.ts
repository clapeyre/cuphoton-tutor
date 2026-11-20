// npm run dev: the server at the usual address, restarted when its code, the course or the tutor's
// prompt changes, and the page rebuilt into web/dist on every save (reload the browser to see it).
// A restart cuts off a tutor turn in progress; the conversation itself survives (it's in learner/).
import { spawn, type ChildProcess } from "node:child_process";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const bin = (name: string) => path.join(root, "node_modules", ".bin", name);

const children: ChildProcess[] = [
  spawn(bin("vite"), ["build", "web", "--watch"], { cwd: root, stdio: "inherit" }),
  spawn(bin("tsx"), [
    "watch", "--clear-screen=false",
    "--include", "course/**", "--include", "tutor/SYSTEM.md", "--include", "tutor/COURSE.md", "--include", "tutor/skills/**",
    "server/index.ts",
  ], { cwd: root, stdio: "inherit" }),
];

let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const c of children) if (c.exitCode === null) c.kill("SIGTERM");
  setTimeout(() => process.exit(code), 500);
}
for (const c of children) c.on("exit", (code) => stop(code ?? 1));
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
