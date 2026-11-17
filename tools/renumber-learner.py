"""One-off: move a learner folder from the old numbering to the one of 17 Nov evening.

    python tools/renumber-learner.py [LEARNER_DIR]     (default: learner/)

Before: xBeam was Module 07 (7.1-7.3, work/07/) and Where next Module 06 (6.1).
After: xBeam is Module 06 (6.1-6.3, work/06/), xRay 07, xImage 08, Where next 09 (9.1).
Rewrites the lesson keys and `current` in progress.json and page.json, every "work/07/" path in them,
and moves work/07 to work/06. Backs up both files first. Runs once: it leaves a marker file and refuses
to run again. Stop the server first, and start it after (a running server would write its old state back).
"""
import json
import re
import shutil
import sys
from pathlib import Path

d = Path(sys.argv[1] if len(sys.argv) > 1 else "learner")
marker = d / ".renumbered-2026-11-18"
if marker.exists():
    sys.exit(f"{d} was already renumbered ({marker}); nothing done")
if (d / "work/06").exists():
    sys.exit(f"{d}/work/06 already exists; nothing done")
MAP = {"6.1": "9.1", "7.1": "6.1", "7.2": "6.2", "7.3": "6.3"}

backup = d / "backup-before-renumber"
backup.mkdir(exist_ok=True)
for name in ("progress.json", "page.json"):
    p = d / name
    if not p.exists():
        continue
    shutil.copy2(p, backup / name)
    data = json.loads(p.read_text())
    if isinstance(data.get("lessons"), dict):
        data["lessons"] = {MAP.get(k, k): v for k, v in data["lessons"].items()}
    if data.get("current") in MAP:
        data["current"] = MAP[data["current"]]
    text = json.dumps(data, ensure_ascii=False, indent=1 if name == "page.json" else 2)
    text = text.replace("work/07/", "work/06/")
    text = re.sub(r'"work/07"', '"work/06"', text)
    p.write_text(text)
    print(f"{p}: lessons renumbered; current = {data.get('current')}; backup in {backup}")
if (d / "work/07").exists():
    (d / "work/07").rename(d / "work/06")
    print(f"moved {d}/work/07 to {d}/work/06")
marker.write_text("renumbered by tools/renumber-learner.py\n")
