"""Makes tiles.png, the lesson's picture of how `detector-artifacts` cuts a detector into traces.

    python tiles_figure.py            (writes tiles.png next to this file)

A schematic: the 256-row x 128-column detector of the lesson, its 16 x 16 tiles, the 7 rows summed
into one row's trace (--integrate 3), and the dispersion curve the row fits add up to (a made-up
smooth curve, not the lesson's answer).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

H, W, T = 256, 128, 16
BLUE, RED, ORANGE, GREY = "#9ec5e8", "#d1495b", "#f2a541", "0.35"

plt.rcParams.update({"font.size": 11})
fig = plt.figure(figsize=(8.4, 8.6))
gs = fig.add_gridspec(2, 2, width_ratios=[0.75, 1.25], height_ratios=[1.25, 0.85])
axs = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]

# 1. One frame: the tile grid.
ax = axs[0]
for x in range(0, W + 1, T):
    ax.plot([x, x], [0, H], color="0.75", lw=0.6)
for y in range(0, H + 1, T):
    ax.plot([0, W], [y, y], color="0.75", lw=0.6)
ax.add_patch(Rectangle((32, 112), T, T, color=ORANGE, zorder=3))
ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.set_aspect("equal")
ax.set_xlabel("column"); ax.set_ylabel("detector row")
ax.set_title("1. One detector frame\n(one of 97, one per delay):\n256 rows × 128 columns,\n128 tiles of 16 × 16 pixels",
             fontsize=10.5)

# 2. One tile: row r's trace sums 16 columns x 7 rows.
ax = axs[1]
x0, y0, r = 32, 112, 121
for x in range(x0, x0 + T + 1):
    ax.plot([x, x], [y0, y0 + T], color="0.85", lw=0.5)
for y in range(y0, y0 + T + 1):
    ax.plot([x0, x0 + T], [y, y], color="0.85", lw=0.5)
ax.add_patch(Rectangle((x0, r - 3), T, 7, color=BLUE, zorder=2))
ax.add_patch(Rectangle((x0, r), T, 1, color=RED, zorder=3))
ax.add_patch(Rectangle((x0, y0), T, T, fill=False, ec=ORANGE, lw=2.5, zorder=4))
ax.annotate("row r", (x0 + T, r + 0.5), (x0 + T + 2.2, r + 0.5), va="center", fontsize=10.5, color=RED,
            arrowprops=dict(arrowstyle="-", color=RED))
ax.annotate("rows r − 3 to r + 3\n(--integrate 3)", (x0 + T, r - 2.5), (x0 + T + 2.2, r - 5.5), va="center", fontsize=10.5,
            color="#3b78b5", arrowprops=dict(arrowstyle="-", color="#3b78b5"))
ax.add_artist(FancyArrowPatch((x0 - 2.2, r - 2), (x0 - 2.2, r + 3), arrowstyle="-|>", mutation_scale=12, color=GREY))
ax.text(x0 - 3.2, r + 0.5, "slides down\none row\nat a time", ha="right", va="center", fontsize=9.5, color=GREY)
ax.set_xlim(x0 - 8.5, x0 + T + 10.5); ax.set_ylim(y0 + T + 0.5, y0 - 0.5); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("2. The orange tile, enlarged. Row r's trace\nis the sum of all 16 columns × 7 rows (blue),\nat every delay. One fit per row per tile:\n128 tiles × 16 rows = 2,048 fits", fontsize=10.5)

# 3. The row fits add up to the dispersion curve.
ax = axs[2]
rows = np.arange(H)
curve = 0.4 + 0.5 * np.sin(np.pi * rows / 300) ** 2  # made up: smooth, as a dispersion curve is
ax.plot(rows, curve, ".", color="#2A78D6", ms=2.5)
ax.plot([r], [curve[r]], "o", color=RED, ms=6)
ax.annotate("row r's fitted frequency", (r, curve[r]), (15, 1.0), fontsize=10.5, color=RED,
            arrowprops=dict(arrowstyle="-", color=RED))
ax.set_xlim(0, H); ax.set_ylim(0.2, 1.1)
ax.set_xlabel("detector row"); ax.set_ylabel("strongest mode (THz)")
ax.set_title("3. Each row's fit gives a frequency. Plotted against the row, they make the\ndispersion curve (each value is also written to all 16 columns of its tile)", fontsize=10.5)

fig.text(0.995, 0.01, "schematic; the curve is made up, not the lesson's data", ha="right", fontsize=7, style="italic", color="0.4")
fig.tight_layout()
out = Path(__file__).with_name("tiles.png")
fig.savefig(out, dpi=130)
print("wrote", out)
