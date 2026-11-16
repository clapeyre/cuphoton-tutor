"""Why the error bars are too small: each pixel's variance is right, but a sum of pixels isn't.

Run from the module's data/ directory (or pass it as the first argument). Writes
work/04/4.4_correlated.png relative to the current directory unless a second argument
names the output.

1. Blank sky only: masked pixels and anything near a source are left out.
2. One pixel at a time: the scatter of pixel/sqrt(variance) should be 1 if the map is right.
3. Neighbours: the correlation between a pixel's noise and its neighbour's.
4. Sums: add up N x N boxes of blank sky (a flux measurement is a weighted sum like this) and
   compare the real scatter of the sums with sqrt(sum of the variances), which assumes the
   pixels' noise is independent.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy import ndimage

data = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("work/04/4.4_correlated.png")

image = fits.getdata(data / "target.fits").astype(float)
variance = fits.getdata(data / "target.var.fits").astype(float)
mask = fits.getdata(data / "target.mask.fits")
good = (mask == 0) & np.isfinite(image) & np.isfinite(variance) & (variance > 0)
z = np.where(good, image / np.sqrt(np.where(good, variance, 1)), 0)
near_source = ndimage.binary_dilation(np.abs(ndimage.gaussian_filter(z, 2)) > 0.6, iterations=6)
sky = good & ~near_source
zs = np.where(sky, z, np.nan)


def corr(dy, dx):
    h, w = zs.shape
    a = zs[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)]
    b = zs[max(-dy, 0):h + min(-dy, 0), max(-dx, 0):w + min(-dx, 0)]
    k = np.isfinite(a) & np.isfinite(b)
    a, b = a[k] - a[k].mean(), b[k] - b[k].mean()
    return (a * b).mean() / np.sqrt((a * a).mean() * (b * b).mean())


lags = np.arange(-3, 4)
cmap = np.array([[corr(dy, dx) for dx in lags] for dy in lags])

sizes = [1, 2, 3, 4, 5, 7, 9, 11]
ratios = []
for n in sizes:
    k = np.ones((n, n))
    s = ndimage.convolve(np.where(sky, image, 0), k, mode="constant", origin=-(n // 2) if n % 2 == 0 else 0)
    v = ndimage.convolve(np.where(sky, variance, 0), k, mode="constant", origin=-(n // 2) if n % 2 == 0 else 0)
    full = ndimage.convolve(sky.astype(float), k, mode="constant", origin=-(n // 2) if n % 2 == 0 else 0) == n * n
    idx = np.argwhere(full)
    idx = idx[(idx[:, 0] % n == 0) & (idx[:, 1] % n == 0)]  # non-overlapping boxes
    ratios.append(np.std(s[idx[:, 0], idx[:, 1]] / np.sqrt(v[idx[:, 0], idx[:, 1]])))
    print(f"{n}x{n} boxes: {len(idx)} of them, real scatter / predicted = {ratios[-1]:.2f}")
print(f"neighbour correlation: right {corr(0, 1):.2f}, below {corr(1, 0):.2f}, diagonal {corr(1, 1):.2f}, two away {corr(0, 2):.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1, 1.3]})
shown = np.where((lags[:, None] == 0) & (lags[None, :] == 0), np.nan, cmap)
im = ax1.imshow(shown, cmap="gray_r", vmin=0, vmax=0.3, extent=[-3.5, 3.5, 3.5, -3.5])
for i, dy in enumerate(lags):
    for j, dx in enumerate(lags):
        txt = "1" if dy == dx == 0 else f"{cmap[i, j]:.2f}"
        ax1.text(dx, dy, txt, ha="center", va="center", fontsize=8,
                 color="white" if (dy or dx) and cmap[i, j] > 0.15 else "black")
ax1.set_xticks(lags); ax1.set_yticks(lags)
ax1.set_xlabel("pixels across"); ax1.set_ylabel("pixels down")
ax1.set_title("How much a pixel's noise is shared\nwith its neighbours (blank sky)")
fig.colorbar(im, ax=ax1, fraction=0.046, label="correlation")

ax2.plot(sizes, ratios, "o-", color="black", label="this image")
ax2.axhline(1, color="gray", ls="--", label="if the pixels' noise were independent")
ax2.set_xlabel("box size (pixels on a side)")
ax2.set_ylabel("real scatter of the sum / predicted")
ax2.set_title("Sum blank sky over a box:\nthe map's prediction falls short as the box grows")
ax2.set_ylim(0.6, max(ratios) + 0.2)
ax2.set_xticks(sizes)
ax2.legend(loc="upper left", fontsize=9, frameon=False)
fig.tight_layout()
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=130)
print(f"wrote {out}")
