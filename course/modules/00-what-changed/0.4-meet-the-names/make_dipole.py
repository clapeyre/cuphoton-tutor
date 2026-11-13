# Regenerates dipole.png, the authored figure for the 0.4 Your turn.
#   ~/cuphoton-overnight/cuPhoton/.venv/bin/python make_dipole.py
# Difference images use a grey scale centred on zero: mid-grey = no change,
# white = brighter in the target, black = brighter in the reference.
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(4)
n = 41
yy, xx = np.mgrid[:n, :n]
g = lambda x0, y0: 1500 * np.exp(-((xx - x0) ** 2 + (yy - y0) ** 2) / (2 * 2.0 ** 2))
diff = g(21.2, 20) - g(18.8, 20) + rng.normal(0, 20, (n, n))
lim = np.abs(diff).max()
fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=100)
im = ax.imshow(diff, cmap="gray", vmin=-lim, vmax=lim, origin="lower")
ax.set_xticks([]); ax.set_yticks([])
fig.colorbar(im, ax=ax, label="difference (counts)")
fig.tight_layout()
fig.savefig("dipole.png")
