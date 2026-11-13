"""Check tool calling and image input per model on the NVIDIA inference endpoint."""
import base64, json, os, sys, time, urllib.request

BASE = "https://inference-api.nvidia.com/v1/chat/completions"
KEY = os.environ["INFERENCE_API_KEY"]
IMG = sys.argv[1]
MODELS = sys.argv[2:]

img_b64 = base64.b64encode(open(IMG, "rb").read()).decode()
IMG_PART = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
SETTLE = {"type": "function", "function": {"name": "settle", "description": "Mark a learner's question as settled and record a one-line summary.",
          "parameters": {"type": "object", "properties": {"turn_id": {"type": "string"}, "summary": {"type": "string"}}, "required": ["turn_id", "summary"]}}}
MARK = {"type": "function", "function": {"name": "mark_lobe", "description": "Report which side of the image holds the positive (red) lobe.",
        "parameters": {"type": "object", "properties": {"side": {"type": "string", "enum": ["left", "right"]}}, "required": ["side"]}}}


def call(model, messages, tools=None, stream=False):
    body = {"model": model, "messages": messages, "max_tokens": 4000, "stream": stream}
    if tools: body["tools"] = tools
    req = urllib.request.Request(BASE, data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read().decode()
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:300]}"}, time.time() - t
    except Exception as e:
        return {"error": str(e)[:300]}, time.time() - t
    if not stream:
        return json.loads(raw), time.time() - t
    # reassemble a streamed response
    content, calls = "", {}
    for line in raw.splitlines():
        if not line.startswith("data: ") or line.strip() == "data: [DONE]": continue
        ch = json.loads(line[6:])
        for c in ch.get("choices", []):
            d = c.get("delta", {})
            content += d.get("content") or ""
            for tc in d.get("tool_calls") or []:
                slot = calls.setdefault(tc.get("index", 0), {"name": "", "arguments": ""})
                f = tc.get("function", {})
                slot["name"] += f.get("name") or ""
                slot["arguments"] += f.get("arguments") or ""
    return {"stream": True, "content": content, "tool_calls": list(calls.values())}, time.time() - t


def summarize(resp):
    if "error" in resp: return resp["error"]
    if resp.get("stream"):
        return {"content": resp["content"][:200], "tool_calls": resp["tool_calls"]}
    m = resp["choices"][0]["message"]
    return {"content": (m.get("content") or "")[:300], "tool_calls": [tc["function"] for tc in m.get("tool_calls") or []],
            "finish": resp["choices"][0].get("finish_reason")}


TESTS = [
    ("tools", [{"role": "user", "content": "The learner just gave a complete answer to turn 0.2-2. Call settle with a one-line summary."}], [SETTLE], False),
    ("tools_stream", [{"role": "user", "content": "The learner just gave a complete answer to turn 0.2-2. Call settle with a one-line summary."}], [SETTLE], True),
    ("image", [{"role": "user", "content": [{"type": "text", "text": "This is a small difference-image cutout. In one sentence: describe the two lobes, and say which side (left or right) holds the positive, red lobe."}, IMG_PART]}], None, False),
    ("image_tool", [{"role": "user", "content": [{"type": "text", "text": "Look at this difference-image cutout and call mark_lobe with the side that holds the positive (red) lobe."}, IMG_PART]}], [MARK], False),
]

for model in MODELS:
    print(f"\n===== {model}")
    for name, msgs, tools, stream in TESTS:
        resp, dt = call(model, msgs, tools, stream)
        print(f"--- {name} ({dt:.1f}s)")
        print(json.dumps(summarize(resp), indent=1, ensure_ascii=False))
