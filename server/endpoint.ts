// The model the tutor talks to. Two sources, in order:
//  1. learner/endpoint.json, written by the first-run setup page (/setup). A fresh install (a Brev
//     launchable, a new lab machine) has nothing else, so the page asks: provider, URL, key, model.
//     The key stays in learner/, which is never committed.
//  2. tutor/pi-agent/models.json with TUTOR_PROVIDER / TUTOR_MODEL and the key from the environment
//     (.env): how the course was built, on the author's machine.
// pi reads a models.json; for (1) we write learner/.pi-models.json, the repo's file plus a "learner" provider.
import fs from "node:fs";
import path from "node:path";
import { config, learnerPath } from "./config.ts";

export type Api = "openai-completions" | "anthropic-messages";
export interface Endpoint {
  preset: string; // which choice on the setup page; informational
  api: Api;
  baseUrl: string;
  apiKey: string;
  model: string;
  contextWindow: number;
  maxTokens: number;
  images: boolean;
  compat?: Record<string, unknown>;
  prices?: { input: number; output: number; cacheRead: number; cacheWrite: number }; // USD per million tokens
}

// The choices the setup page offers. The course was built and tested with Claude Sonnet 5.5.
export const PRESETS = [
  { id: "anthropic", label: "Anthropic API", api: "anthropic-messages", baseUrl: "https://api.anthropic.com", model: "claude-sonnet-5-5", contextWindow: 200000, keyHint: "sk-ant-…", needsKey: true },
  { id: "nvidia-build", label: "NVIDIA API catalog (build.nvidia.com)", api: "openai-completions", baseUrl: "https://integrate.api.nvidia.com/v1", model: "", contextWindow: 128000, keyHint: "nvapi-…", needsKey: true },
  { id: "nvidia-inference", label: "NVIDIA inference hub (NVIDIA employees)", api: "openai-completions", baseUrl: "https://inference-api.nvidia.com/v1", model: "aws/anthropic/bedrock-claude-sonnet-5-5", contextWindow: 200000, keyHint: "", needsKey: true,
    compat: { supportsDeveloperRole: false, supportsStore: false, maxTokensField: "max_tokens", requiresNonNullAssistantContent: true } },
  { id: "openai-compatible", label: "Any OpenAI-compatible server (vLLM, NIM, Ollama, …)", api: "openai-completions", baseUrl: "http://localhost:8000/v1", model: "", contextWindow: 128000, keyHint: "often not needed for a local server", needsKey: false },
] as const;

const FILE = () => learnerPath("endpoint.json");
const REPO_MODELS = () => path.join(config.tutorDir, "pi-agent", "models.json");
const LEARNER_MODELS = () => learnerPath(".pi-models.json");

export function loadEndpoint(): Endpoint | null {
  try { return JSON.parse(fs.readFileSync(FILE(), "utf8")); } catch { return null; }
}

export function saveEndpoint(e: Endpoint) {
  fs.mkdirSync(path.dirname(FILE()), { recursive: true });
  fs.writeFileSync(FILE(), JSON.stringify(e, null, 1), { mode: 0o600 });
  fs.chmodSync(FILE(), 0o600);
}

function modelsJsonFor(e: Endpoint) {
  const repo = JSON.parse(fs.readFileSync(REPO_MODELS(), "utf8"));
  const p = e.prices ?? { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 };
  repo.providers = {
    ...repo.providers,
    learner: {
      name: "Set on the setup page", baseUrl: e.baseUrl, api: e.api, apiKey: e.apiKey || "none",
      ...(e.compat ? { compat: e.compat } : {}),
      models: [{ id: e.model, name: e.model, input: e.images ? ["text", "image"] : ["text"], contextWindow: e.contextWindow, maxTokens: e.maxTokens, cost: p }],
    },
  };
  return repo;
}

/** Point config at the setup page's endpoint, if there is one, and return the models.json pi should read. */
export function modelsPath(): string {
  const e = loadEndpoint();
  if (!e) return REPO_MODELS();
  fs.writeFileSync(LEARNER_MODELS(), JSON.stringify(modelsJsonFor(e), null, 1), { mode: 0o600 });
  config.provider = "learner";
  config.model = e.model;
  return LEARNER_MODELS();
}

/** The provider entry and model the tutor will use, with its key resolved ("$NAME" from the environment). */
export function current(): { api: Api; baseUrl: string; key: string; model: string; compat: any; cost: any; contextWindow?: number } | null {
  try {
    const models = JSON.parse(fs.readFileSync(modelsPath(), "utf8"));
    const prov = models.providers?.[config.provider];
    if (!prov) return null;
    const m = prov.models?.find((x: any) => x.id === config.model);
    const key = String(prov.apiKey ?? "").replace(/^\$\{?(\w+)\}?$/, (_: string, k: string) => process.env[k] ?? "");
    return { api: m?.api ?? prov.api, baseUrl: m?.baseUrl ?? prov.baseUrl, key, model: config.model, compat: { ...prov.compat, ...m?.compat }, cost: m?.cost, contextWindow: m?.contextWindow };
  } catch { return null; }
}

/** Is there a model to talk to? (A key, or a setup-page endpoint, which may be keyless for a local server.) */
export function isConfigured() {
  if (loadEndpoint()) return true;
  const c = current();
  return !!(c && c.key && c.key !== "none");
}

/** One tool call: proves the URL, key, model and tool use. Used by the setup page, the admin page and `npm run smoke`. */
export async function pingEndpoint(e?: { api: Api; baseUrl: string; key: string; model: string; compat?: any }): Promise<{ ok: boolean; seconds: number; detail: string }> {
  const t0 = Date.now();
  const target = e ?? current();
  const done = (ok: boolean, detail: string) => ({ ok, seconds: (Date.now() - t0) / 1000, detail });
  if (!target) return done(false, `no model configured (provider ${config.provider} not in models.json)`);
  const tool = { name: "ping", description: "ping", schema: { type: "object", properties: { n: { type: "integer" } }, required: ["n"] } };
  try {
    const base = target.baseUrl.replace(/\/$/, "");
    let res: Response, called = false, body: any;
    if (target.api === "anthropic-messages") {
      res = await fetch(`${base}/v1/messages`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-api-key": target.key, "anthropic-version": "2023-06-01" },
        body: JSON.stringify({ model: target.model, max_tokens: 500, messages: [{ role: "user", content: "Call the ping tool with n=7." }],
          tools: [{ name: tool.name, description: tool.description, input_schema: tool.schema }] }),
        signal: AbortSignal.timeout(60000),
      });
      body = await res.json().catch(() => ({}));
      called = (body.content ?? []).some((c: any) => c.type === "tool_use" && c.name === "ping");
    } else {
      const maxField = target.compat?.maxTokensField ?? "max_tokens";
      res = await fetch(`${base}/chat/completions`, {
        method: "POST",
        headers: { "content-type": "application/json", ...(target.key && target.key !== "none" ? { authorization: `Bearer ${target.key}` } : {}) },
        body: JSON.stringify({ model: target.model, [maxField]: 2000, messages: [{ role: "user", content: "Call the ping tool with n=7." }],
          tools: [{ type: "function", function: { name: tool.name, description: tool.description, parameters: tool.schema } }] }),
        signal: AbortSignal.timeout(60000),
      });
      body = await res.json().catch(() => ({}));
      called = body.choices?.[0]?.message?.tool_calls?.[0]?.function?.name === "ping";
    }
    const s = ((Date.now() - t0) / 1000).toFixed(1);
    if (called) return done(true, `${target.model} at ${base} · tool call in ${s} s`);
    if (!res.ok) return done(false, `HTTP ${res.status}: ${JSON.stringify(body).slice(0, 240)}`);
    return done(false, `the model answered but didn't call the tool; the tutor needs tool calls. ${JSON.stringify(body).slice(0, 200)}`);
  } catch (err: any) {
    return done(false, err?.cause?.code ? `${err.message} (${err.cause.code})` : err.message);
  }
}
