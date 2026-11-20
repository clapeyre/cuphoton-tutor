"""Data for v5 (why the sum wobbles): xRep resampling pure noise by half a pixel, and the PS1 target's
measured noise correlation (Module 04 data). Writes v5.npz to the output dir (argv[1], default .)."""
import sys
import warnings
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy import ndimage

from cuphoton.xrep import BBox, ReprojectionSpec, make_wcs_pair_transform, reproject_masked_array

warnings.simplefilter("ignore")
out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PS1 = Path(__file__).resolve().parents[2] / "course" / "modules" / "04-real-data" / "data"


def wcs(dx, dy, n):
    w = WCS(naxis=2)
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    w.wcs.crval = [210.8, 54.3]
    w.wcs.crpix = [n / 2 + dx, n / 2 + dy]
    w.wcs.cdelt = [-0.258 / 3600, 0.258 / 3600]
    return w


def resample(a):
    n = a.shape[0]
    spec = ReprojectionSpec(mapping=make_wcs_pair_transform(wcs(0, 0, n), wcs(0.5, 0.5, n)), output_bbox=BBox(0, 0, n, n))
    r = reproject_masked_array(a, np.ones_like(a), np.zeros(a.shape, bool), spec, backend="cpu")
    return r.image, r.variance


def corr(a, dy, dx):
    h, w = a.shape
    A = a[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)]
    B = a[max(-dy, 0):h + min(-dy, 0), max(-dx, 0):w + min(-dx, 0)]
    k = np.isfinite(A) & np.isfinite(B)
    A, B = A[k] - A[k].mean(), B[k] - B[k].mean()
    return float((A * B).mean() / np.sqrt((A * A).mean() * (B * B).mean()))


def box_ratio(img, var, n, good=None):
    good = np.isfinite(img) & np.isfinite(var) if good is None else good
    k = np.ones((n, n))
    s = ndimage.convolve(np.where(good, img, 0), k, mode="constant")
    v = ndimage.convolve(np.where(good, var, 0), k, mode="constant")
    full = ndimage.convolve(good.astype(float), k, mode="constant") == n * n
    idx = np.argwhere(full)
    idx = idx[(idx[:, 0] % n == 0) & (idx[:, 1] % n == 0)]
    return float(np.std(s[idx[:, 0], idx[:, 1]] / np.sqrt(v[idx[:, 0], idx[:, 1]])))


rng = np.random.default_rng(5)
N = 600
noise = rng.normal(0, 1, (N, N))
res, rvar = resample(noise)
c = slice(20, N - 20)
noise_c, res_c, rvar_c = noise[c, c], res[c, c], rvar[c, c]
# one input pixel's noise, spread by xRep over the output grid (the impulse response)
delta = np.zeros((40, 40)); delta[20, 20] = 1.0
imp, _ = resample(delta)
sizes = [1, 3, 5, 9]
d = dict(
    patch_in=noise_c[100:116, 100:116], patch_out=res_c[100:116, 100:116],
    impulse=imp[17:24, 17:24],
    iid_ratio=np.array([box_ratio(noise_c, np.ones_like(noise_c), n) for n in sizes]),
    res_ratio=np.array([box_ratio(res_c, rvar_c, n) for n in sizes]), sizes=np.array(sizes),
    res_pix=float(np.std(res_c / np.sqrt(rvar_c))), res_corr=np.array([corr(res_c, 0, 1), corr(res_c, 1, 0), corr(res_c, 0, 2)]),
    # 3x3 box sums for the flicker: 24 realisations from non-overlapping windows, in units of the predicted sigma
    iid_boxes=np.stack([noise_c[3 * i:3 * i + 3, 0:3] for i in range(40)]),
    res_boxes=np.stack([res_c[3 * i:3 * i + 3, 0:3] / np.sqrt(rvar_c[3 * i:3 * i + 3, 0:3]) for i in range(40)]),
)
# the survey's own images (target night, blank sky), as in 4.4
im = fits.getdata(PS1 / "target.fits").astype(float); var = fits.getdata(PS1 / "target.var.fits").astype(float)
mask = fits.getdata(PS1 / "target.mask.fits")
good = (mask == 0) & np.isfinite(im) & np.isfinite(var) & (var > 0)
z = np.where(good, im / np.sqrt(np.where(good, var, 1)), 0)
sky = good & ~ndimage.binary_dilation(np.abs(ndimage.gaussian_filter(z, 2)) > 0.6, iterations=6)
zs = np.where(sky, z, np.nan)
d["ps1_corr"] = np.array([[corr(zs, dy, dx) for dx in (-1, 0, 1)] for dy in (-1, 0, 1)])
d["ps1_sizes"] = np.array([1, 2, 3, 4, 5, 7, 9, 11])
d["ps1_ratio"] = np.array([box_ratio(im, var, n, sky) for n in d["ps1_sizes"]])
np.savez(out / "v5.npz", **d)
for k in ("iid_ratio", "res_ratio", "res_pix", "res_corr", "ps1_ratio"):
    print(k, np.round(d[k], 3))
print("impulse\n", np.round(d["impulse"], 2)); print("ps1_corr\n", np.round(d["ps1_corr"], 2))
