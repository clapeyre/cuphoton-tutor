"""4.1: does each night's variance map match the scatter of empty sky?

    python noise_check.py [data dir] [corner size]

Empty sky, defined once so every run gets the same numbers: the four corners (150 x 150 px by default),
pixels the survey marks usable (none of MASK.VALUE's bits, finite, variance > 0), minus anything
brighter than 3 sigma above the corner's median, grown by 5 px so the faint wings of stars go too.
Each corner's own sky level is removed first (the corners sit up to ~15 counts apart, and pooling them
would count that as noise). The scatter is a 3-sigma-clipped variance, not the MAD: the survey stores pixel values in steps of about 0.8
counts, so the MAD jumps between a few values and small changes in the selection flip it. The map's value is
its median over the same pixels.
"""
import sys
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from scipy import ndimage as ndi

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 150
BAD = 8575  # MASK.VALUE in the headers: the bits the survey says to reject


def corners(a):
    return [a[:N, :N], a[:N, -N:], a[-N:, :N], a[-N:, -N:]]


for name in ("reference", "target"):
    im = fits.getdata(D / f"{name}.fits").astype(float)
    va = fits.getdata(D / f"{name}.var.fits").astype(float)
    mk = fits.getdata(D / f"{name}.mask.fits").astype(int)
    scat, mapv, used = [], [], 0
    for c, v, m in zip(corners(im), corners(va), corners(mk)):
        ok = np.isfinite(c) & np.isfinite(v) & (v > 0) & ((m & BAD) == 0)
        if ok.sum() < 100:
            continue
        med = np.median(c[ok])
        sig = 1.4826 * np.median(np.abs(c[ok] - med))
        src = ndi.binary_dilation(ok & (c > med + 3 * sig), iterations=5)
        sky = ok & ~src
        x = c[sky] - sigma_clipped_stats(c[sky], sigma=3)[0]  # this corner's own sky level removed
        scat.append(x)
        mapv.append(v[sky])
        used += sky.sum()
    var = lambda a: sigma_clipped_stats(a, sigma=3, maxiters=10)[2] ** 2
    x = np.concatenate(scat)
    m = np.median(np.concatenate(mapv))
    per = ", ".join(f"{var(s):.0f}" for s in scat if s.size > 100)
    print(f"{name:9s} empty-sky pixels {used:6d}  scatter (clipped variance) {var(x):5.0f}  map median {m:5.0f}  "
          f"map/scatter {m / var(x):.2f}   per corner: {per}")
