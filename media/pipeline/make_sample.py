"""Write sample/reference.fits and sample/target.fits using the cuPhoton guide's
own generator (docs/guide/_sample-pair.qmd), so the course never drifts from it.

Usage: uv run --project <cuPhoton checkout> python tools/make_sample.py [CHECKOUT] [OUTDIR]
"""
import os
import re
import sys
from pathlib import Path

checkout = Path(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CUPHOTON_DIR", "../cuPhoton"))
outdir = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
source = (checkout / "docs/guide/_sample-pair.qmd").read_text()
block = re.search(r"```\{python\}\n(.*?)```", source, re.S)
if block is None:
    sys.exit(f"No python block found in {checkout}/docs/guide/_sample-pair.qmd")
code = "\n".join(line for line in block.group(1).splitlines() if not line.startswith("#|"))

outdir.mkdir(parents=True, exist_ok=True)
os.chdir(outdir)
exec(compile(code, "_sample-pair.qmd", "exec"), {"__name__": "__main__"})
print(f"wrote {outdir.resolve()}/sample/reference.fits and target.fits")
