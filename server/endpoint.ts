// One tool call against the configured model: proves the endpoint, key and tool use work.
// Used by `npm run smoke` and the admin page's "Ping the model" button.
import fs from "node:fs";
import path from "node:path";
import { config } from "./config.ts";

export async function pingEndpoint(): Promise<{ ok: boolean; seconds: number; detail: string }> {
  const t0 = Date.now();
  try {
    const models = JSON.parse(fs.readFileSync(path.join(config.tutorDir, "pi-agent", "models.json"), "utf8"));
    const prov = models.providers?.[config.provider];
    if (!prov) throw new Error(`provider ${config.provider} not in models.json`);
    const key = String(prov.apiKey ?? "").replace(/^\$\{?(\w+)\}?$/, (_: string, k: string) => process.env[k] ?? "");
    const res = await fetch(`${prov.baseUrl}/chat/completions`, {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${key}` },
      body: JSON.stringify({
        model: config.model, max_tokens: 2000,
        messages: [{ role: "user", content: "Call the ping tool with n=7." }],
        tools: [{ type: "function", function: { name: "ping", description: "ping", parameters: { type: "object", properties: { n: { type: "integer" } }, required: ["n"] } } }],
      }),
      signal: AbortSignal.timeout(60000),
    });
    const j: any = await res.json();
    const call = j.choices?.[0]?.message?.tool_calls?.[0];
    const seconds = (Date.now() - t0) / 1000;
    return call?.function?.name === "ping"
      ? { ok: true, seconds, detail: `${config.provider}/${config.model} · tool call in ${seconds.toFixed(1)} s` }
      : { ok: false, seconds, detail: `HTTP ${res.status}: ${JSON.stringify(j).slice(0, 200)}` };
  } catch (e: any) {
    return { ok: false, seconds: (Date.now() - t0) / 1000, detail: e.message };
  }
}
