// Runtime configuration. Everything a compute centre may need to change is an
// environment variable (or a line in .env); nothing else is read at startup.
import fs from "node:fs";
import path from "node:path";

export const ROOT = path.resolve(import.meta.dirname, "..");

function loadDotEnv(file: string) {
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/);
    if (!m || process.env[m[1]] !== undefined) continue;
    process.env[m[1]] = m[2].replace(/^(['"])(.*)\1$/, "$2");
  }
}
loadDotEnv(path.join(ROOT, ".env"));

const env = (k: string, d: string) => process.env[k] ?? d;
const abs = (p: string) => path.resolve(ROOT, p);

export const config = {
  port: Number(env("PORT", "8765")),
  host: env("HOST", "127.0.0.1"), // reached over an SSH tunnel; don't bind publicly
  courseDir: abs(env("COURSE_DIR", "course")),
  mediaDir: abs(env("MEDIA_DIR", "media")),
  tutorDir: abs(env("TUTOR_DIR", "tutor")),
  learnerDir: abs(env("LEARNER_DIR", "learner")),
  webDist: abs(env("WEB_DIST", "web/dist")),
  cuphotonDir: abs(env("CUPHOTON_DIR", path.join(process.env.HOME ?? "", "cuphoton-overnight/cuPhoton"))),
  // Python for the learner workspace: NumPy, SciPy, Matplotlib and cuPhoton.
  pythonBin: env("LEARNER_PYTHON_BIN", ""), // a venv's bin/ dir; default: <cuphotonDir>/.venv/bin
  // The same with cuPhoton's gpu extra (CuPy, CUDA PyTorch), for Module 03 on. Modules 00–02 rely on the
  // default environment having no usable GPU (Module 02 teaches the silent fallback). tools/setup-gpu-env.sh makes it.
  gpuPythonBin: abs(env("LEARNER_GPU_PYTHON_BIN", ".envs/cuphoton-gpu/bin")),
  // Inference: any OpenAI- or Anthropic-style endpoint. Provider + model are
  // looked up in tutor/pi-agent/models.json (add a provider there for a new site).
  provider: env("TUTOR_PROVIDER", "nvidia"),
  model: env("TUTOR_MODEL", "aws/anthropic/bedrock-claude-sonnet-5-5"),
  thinking: env("TUTOR_THINKING", "off") as "off" | "minimal" | "low" | "medium" | "high",
  feedbackUrl: env("CUPHOTON_LEARN_FEEDBACK_URL", ""),
  offline: env("PI_OFFLINE", "1") === "1",
};

export function learnerPath(...p: string[]) {
  return path.join(config.learnerDir, ...p);
}
