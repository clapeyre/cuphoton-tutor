"""Mark a transient-chain catalog's rows on the target image, numbered by row.

    python catalog_figure.py <catalog.parquet> <target.fits> <out.png>

Circles are rows with a positive sign, squares negative; a dashed marker is a row with
uq_valid False. Labels are the row numbers, so the table and the picture can be read together.
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import fits

cat, target, out = pd.read_parquet(sys.argv[1]), fits.getdata(sys.argv[2]).astype(float), sys.argv[3]
img = np.nan_to_num(target)
lo, hi = np.percentile(img, [30, 99.9])
fig, ax = plt.subplots(figsize=(7.5, 7.5))
ax.imshow(np.arcsinh(np.clip(img - lo, 0, None) / (0.01 * (hi - lo))), cmap="gray", origin="lower", vmin=0, vmax=np.arcsinh(100))
for i, r in cat.iterrows():
    style = dict(fill=False, lw=1.4, ls="-" if r.uq_valid else "--")
    if r.sign >= 0:
        ax.add_patch(plt.Circle((r.x, r.y), 14, ec="white", **style))
    else:
        ax.add_patch(plt.Rectangle((r.x - 12, r.y - 12), 24, 24, ec="white", **style))
# One label per place: rows within 10 px of each other share it ("1, 9").
groups = []
for i, r in cat.iterrows():
    for g in groups:
        if np.hypot(g["x"] - r.x, g["y"] - r.y) < 10:
            g["rows"].append(i)
            break
    else:
        groups.append({"x": r.x, "y": r.y, "rows": [i]})
for g in groups:
    ax.text(g["x"] + 16, g["y"] + 10, ", ".join(map(str, g["rows"])), color="white", fontsize=10, fontweight="bold",
            bbox=dict(facecolor="black", alpha=0.6, pad=1, lw=0))
ax.set_title("Target night with the catalog's rows (number = row; dashed = uq_valid False)")
ax.set_xlabel("x (pixels)"); ax.set_ylabel("y (pixels)")
fig.tight_layout(); fig.savefig(out, dpi=110)
print("wrote", out)
