// One chat call to the inference endpoint (OpenAI-compatible), for the simulated learner and the grader.
// The tutor itself goes through pi, inside the server, like for a real learner.
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
for (const line of fs.existsSync(path.join(ROOT, ".env")) ? fs.readFileSync(path.join(ROOT, ".env"), "utf8").split("\n") : []) {
  const m = line.match(/^\s*([A-Za-z_]\w*)\s*=\s*(.*)\s*$/);
  if (m && process.env[m[1]] === undefined) process.env[m[1]] = m[2].replace(/^(['"])(.*)\1$/, "$2");
}
const BASE = process.env.SIM_BASE_URL ?? "https://inference-api.nvidia.com/v1";

export type Content = string | ({ type: "text"; text: string } | { type: "image_url"; image_url: { url: string } })[];
export interface Msg { role: "system" | "user" | "assistant"; content: Content }
export interface Usage { input: number; output: number; calls: number }

export function imagePart(file: string) {
  const ext = path.extname(file).slice(1).toLowerCase().replace("jpg", "jpeg");
  return { type: "image_url" as const, image_url: { url: `data:image/${ext};base64,${fs.readFileSync(file).toString("base64")}` } };
}

export async function chat(model: string, messages: Msg[], opts: { maxTokens?: number; usage?: Usage; temperature?: number } = {}): Promise<string> {
  let last = "";
  for (let attempt = 0; attempt < 6; attempt++) {
    try {
      const res = await fetch(`${BASE}/chat/completions`, {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${process.env.INFERENCE_API_KEY}` },
        body: JSON.stringify({ model, messages, max_tokens: opts.maxTokens ?? 2000, ...(opts.temperature != null ? { temperature: opts.temperature } : {}) }),
        signal: AbortSignal.timeout(300_000),
      });
      const body: any = await res.json().catch(() => ({}));
      if (res.ok && body.choices?.[0]?.message) {
        if (opts.usage) { opts.usage.input += body.usage?.prompt_tokens ?? 0; opts.usage.output += body.usage?.completion_tokens ?? 0; opts.usage.calls++; }
        return String(body.choices[0].message.content ?? "");
      }
      last = `HTTP ${res.status}: ${JSON.stringify(body).slice(0, 300)}`;
      if (res.status < 500 && res.status !== 429) break;
    } catch (e: any) { last = e.message; }
    await new Promise((r) => setTimeout(r, 15_000 * (attempt + 1)));
  }
  throw new Error(`${model}: ${last}`);
}

/** The first top-level JSON object in a reply (models sometimes wrap it in prose or a code fence). */
export function firstJson(s: string): any {
  const start = s.indexOf("{");
  if (start < 0) throw new Error("no JSON object");
  let depth = 0, inStr = false, esc = false;
  for (let i = start; i < s.length; i++) {
    const c = s[i];
    if (inStr) { if (esc) esc = false; else if (c === "\\") esc = true; else if (c === '"') inStr = false; continue; }
    if (c === '"') inStr = true;
    else if (c === "{") depth++;
    else if (c === "}" && --depth === 0) return JSON.parse(s.slice(start, i + 1));
  }
  throw new Error("unterminated JSON object");
}
