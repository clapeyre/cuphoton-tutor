"""Move a learner folder to the course's current numbering, one migration at a time.

    python tools/renumber-learner.py [LEARNER_DIR]     (default: learner/)

Migrations, oldest first (each leaves a marker file and is skipped once applied):
  2026-11-18   xBeam 07 -> 06 (7.x -> 6.x), Where next 06 -> 09 (6.1 -> 9.1).
  2026-11-18b  xImage 08 -> 06, xBeam 06 -> 07, xRay 07 -> 08 (walkthrough 9: xImage follows the image modules).
Rewrites the lesson keys, `current`, margin threads' `from`, "work/NN/" paths and "#/X.Y" lesson links in
progress.json and page.json, and moves the work/NN folders. Backs up both files first. Stop the server
first, and start it after (a running server would write its old state back).
"""
import json
import re
import shutil
import sys
from pathlib import Path

MIGRATIONS = [
    ("2026-11-18", {"6.1": "9.1", "7.1": "6.1", "7.2": "6.2", "7.3": "6.3"}, {"07": "06"}),
    ("2026-11-18b", {**{f"6.{i}": f"7.{i}" for i in (1, 2, 3)}, **{f"7.{i}": f"8.{i}" for i in (1, 2, 3)},
                     **{f"8.{i}": f"6.{i}" for i in (1, 2, 3)}}, {"06": "07", "07": "08", "08": "06"}),
]

d = Path(sys.argv[1] if len(sys.argv) > 1 else "learner")


def migrate(name: str, lessons: dict, work: dict) -> None:
    backup = d / f"backup-before-renumber-{name}"
    backup.mkdir(exist_ok=True)
    path_rx = re.compile(r"work/(" + "|".join(work) + r")\b")
    link_rx = re.compile(r"#/(" + "|".join(re.escape(k) for k in lessons) + r")\b")
    for fname in ("progress.json", "page.json"):
        p = d / fname
        if not p.exists():
            continue
        shutil.copy2(p, backup / fname)
        data = json.loads(p.read_text())
        if isinstance(data.get("lessons"), dict):
            data["lessons"] = {lessons.get(k, k): v for k, v in data["lessons"].items()}
        if data.get("current") in lessons:
            data["current"] = lessons[data["current"]]
        for t in data.get("threads", []) or []:
            if t.get("from") in lessons:
                t["from"] = lessons[t["from"]]
        text = json.dumps(data, ensure_ascii=False, indent=1 if fname == "page.json" else 2)
        text = path_rx.sub(lambda m: "work/" + work[m.group(1)], text)  # one pass: a cycle maps cleanly
        text = link_rx.sub(lambda m: "#/" + lessons[m.group(1)], text)
        p.write_text(text)
        print(f"{p}: renumbered ({name}); current = {data.get('current')}; backup in {backup}")
    tmp = {k: d / f"work/.renumber-{k}" for k in work if (d / "work" / k).exists()}
    for k, t in tmp.items():
        (d / "work" / k).rename(t)
    for k, t in tmp.items():
        if (d / "work" / work[k]).exists():
            sys.exit(f"{d}/work/{work[k]} already exists; {t} left in place")
        t.rename(d / "work" / work[k])
        print(f"moved {d}/work/{k} to {d}/work/{work[k]}")
    (d / f".renumbered-{name}").write_text(f"renumbered by tools/renumber-learner.py ({name})\n")


done = 0
for name, lessons, work in MIGRATIONS:
    if (d / f".renumbered-{name}").exists():
        continue
    migrate(name, lessons, work)
    done += 1
print(f"{done} migration(s) applied" if done else f"{d} is already on the current numbering; nothing done")
