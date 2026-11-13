"""Step 1+3 of the pipeline: narration -> audio/sNN.wav, timings.json, <id>.srt.

Usage: python pipeline/narrate.py <video-id> [--voice af_heart]
Reads media/scripts/<id>-*.md (or <id>.md). Output goes to $MEDIA_RENDERS/<id>/
(default media/renders/<id>/); see pipeline/env.sh.
timings.json holds, per segment, its duration and each word's start/end in
seconds, so scenes can reveal an element when the voice starts naming it
(common.Timed.at). For a human voiceover, produce the same words list by forced
alignment of the recording.
Each segment's duration = speech + PAD seconds (so scenes breathe).
"""
import json, os, re, sys, glob
from pathlib import Path
import numpy as np, soundfile as sf

PAD = 0.6
SR = 24000
root = Path(__file__).resolve().parents[1]
vid = sys.argv[1]
voice = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "af_heart"
src = next(iter(sorted(glob.glob(str(root / "scripts" / f"{vid}*.md")))))
text = Path(src).read_text()

segs = []
for m in re.finditer(r"^## (s\d+) — (.*?)\n(.*?)(?=^## |\Z)", text, re.S | re.M):
    sid, title, body = m.groups()
    n = re.search(r"\*\*Narration:\*\*\s*(.*)", body, re.S)
    if n:
        segs.append((sid, re.sub(r"\s+", " ", n.group(1)).strip()))

out = Path(os.environ.get("MEDIA_RENDERS", root / "renders")) / vid
(out / "audio").mkdir(parents=True, exist_ok=True)
from kokoro import KPipeline
pipe = KPipeline(lang_code="a")
timings = {}
for sid, narr in segs:
    chunks, words, off = [], [], 0.0
    for r in pipe(narr, voice=voice, speed=1.0):
        a = r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
        for tk in (r.tokens or []):
            if tk.start_ts is not None and tk.text.strip():
                words.append({"w": tk.text, "start": round(off + tk.start_ts, 3),
                              "end": round(off + (tk.end_ts or tk.start_ts), 3)})
        chunks.append(a); off += len(a) / SR
    audio = np.concatenate(chunks + [np.zeros(int(PAD * SR), dtype=np.float32)])
    sf.write(out / "audio" / f"{sid}.wav", audio, SR)
    timings[sid] = {"duration": len(audio) / SR, "text": narr, "words": words}
    print(sid, round(len(audio) / SR, 2), "s,", len(words), "timed tokens")
(out / "timings.json").write_text(json.dumps(timings, indent=2))

def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")
t0, lines = 0.0, []
for sid, v in timings.items():
    # one cue per sentence, timed from the word timestamps
    sent, start = [], None
    ws = v["words"]
    for i, w in enumerate(ws):
        if start is None:
            start = w["start"]
        sent.append(w["w"])
        if w["w"] in ".?!" or i == len(ws) - 1:
            end = ws[i + 1]["start"] if i + 1 < len(ws) else v["duration"] - PAD
            text_ = re.sub(r"\s+([.,;:?!])", r"\1", " ".join(sent))
            lines.append(f"{len(lines)+1}\n{ts(t0+start)} --> {ts(t0+end)}\n{text_}\n")
            sent, start = [], None
    t0 += v["duration"]
(out / f"{vid}.srt").write_text("\n".join(lines))
print("total", round(t0, 1), "s")
