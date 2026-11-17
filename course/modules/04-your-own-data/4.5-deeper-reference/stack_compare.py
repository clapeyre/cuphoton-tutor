"""4.5: stack the three pre-explosion nights into one reference with xRep, and compare references
with the 4.2 chain and the 4.4 injection test.

    python stack_compare.py <out.png> [config ...]      (GPU environment; any working directory)

Configs (default: single weighted mean): single = the 4.2 reference alone; weighted = all three
nights, inverse-variance weighted over each pixel's usable nights, variance 1/sum(1/var); mean =
plain mean, a pixel missing in any night is lost; samevar = weighted, but keeping the single
night's variance map; two = the two nights of 22 April, weighted.
Env: DATA (default ./data if it holds target.fits, else the course's data/), SEEDS (injection seeds, default "11 12 13"; 100 fakes each).

Prints, per reference: usable fraction, kernel sum, chi2/dof, hotspots (threshold 5), the share of
the difference's variance that comes from the reference, and per planted flux the fakes found and
their median error. Then, for each stack, the hotspots that fall outside the single reference's
usable area, with the nights that cover them. The figure: top, each night's usable pixels with
its seeing; bottom, z of the single reference and of each stack, new-area hotspots circled.
"""
import os
import pathlib
import sys
import warnings

warnings.simplefilter("ignore")
import cupy as cp
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from scipy.ndimage import binary_erosion
from scipy.signal import fftconvolve
from cuphoton.xfit import fit_single_sources
from cuphoton.xpois import (GaussianBasisComponent, identify_residual_hotspots, solve_constant_kernel,
                            standardize_constant_kernel_residual, window_stamps)
from cuphoton.xrep import BBox, Grid, build_stack_spec_from_fits, reproject_masked_array

D = os.environ.get("DATA") or ("data" if os.path.exists("data/target.fits") else str(pathlib.Path(__file__).resolve().parents[1] / "data"))
OUT = sys.argv[1]
CONFIGS = sys.argv[2:] or ["single", "weighted", "mean"]
SEEDS = [int(s) for s in os.environ.get("SEEDS", "11 12 13").split()]
BAD, SIG = 8575, 1.57
L = lambda n, s="": fits.getdata(f"{D}/{n}{s}.fits").astype(np.float64)
to = lambda x: cp.asnumpy(x) if not isinstance(x, np.ndarray) else x
tgt, tv, tm = L("target"), L("target", ".var"), fits.getdata(f"{D}/target.mask.fits")
th = fits.getheader(f"{D}/target.fits")
GAIN = th["CELL.GAIN"]
basis = [GaussianBasisComponent(0.7, 4), GaussianBasisComponent(1.4, 2), GaussianBasisComponent(2.8, 2)]
NAMES = ["reference", "reference-b", "reference-c"]
SEEING = {n: fits.getheader(f"{D}/{n}.fits")["CHIP.SEEING"] for n in NAMES + ["target"]}

# xRep: every night onto the target's grid, with its variance and mask (reproject_stack alone gives no variance)
_, spec = build_stack_spec_from_fits([f"{D}/{n}.fits" for n in NAMES], grid=Grid.from_wcs(WCS(th)),
                                     output_bbox=BBox(0, 0, *tgt.shape[::-1]), fits_reader="auto", device=True)
members = {}
print("xRep onto the target's grid (seeing: FWHM in detector px; target", f"{SEEING['target']:.2f})")
for k, n in enumerate(NAMES):
    img, var, msk = L(n), L(n, ".var"), fits.getdata(f"{D}/{n}.mask.fits").astype(np.int32)
    bad = ~np.isfinite(img) | ~np.isfinite(var) | ((msk & BAD) != 0) | (var <= 0)
    r = reproject_masked_array(np.where(bad, 0, img), np.where(bad, 0, var), np.where(bad, msk | 8, msk),
                               spec.members[k], backend="cupy")
    o_img, o_var, o_msk = to(r.image), to(r.variance), to(r.mask)
    good = ((o_msk & (BAD | 1)) == 0) & np.isfinite(o_img) & np.isfinite(o_var) & (o_var > 0)
    moved = float(np.max(np.abs(o_img - img)[good & ~bad]))
    members[n] = (o_img, o_var, good)
    print(f"  {n:12s} seeing {SEEING[n]:.2f}  usable {good.mean():.3f}  max |resampled - original| {moved:.1e}")


def combine(names, mode="weighted"):
    imgs = np.stack([members[n][0] for n in names])
    vars_ = np.stack([members[n][1] for n in names])
    goods = np.stack([members[n][2] for n in names])
    if mode == "mean":
        ok = goods.all(0)
        return np.where(ok, imgs.mean(0), np.nan), np.where(ok, vars_.sum(0) / len(names) ** 2, np.nan), ok
    w = np.where(goods, 1 / np.where(goods, vars_, 1), 0)
    sw = w.sum(0)
    ok = sw > 0
    s = np.where(ok, (w * np.where(goods, imgs, 0)).sum(0) / np.where(ok, sw, 1), np.nan)
    return s, np.where(ok, 1 / np.where(ok, sw, 1), np.nan), ok


def chain(ref, rv, refok, t_img, t_var):
    use = refok & np.isfinite(ref) & np.isfinite(rv) & (rv > 0) & np.isfinite(t_img) & np.isfinite(t_var) \
        & ((tm & BAD) == 0) & (t_var > 0)
    fit = solve_constant_kernel(np.where(use, ref, 0.0), np.where(use, t_img, 0.0), basis, kernel_shape=(19, 19),
                                variance=np.where(use, t_var, 1e12), fit_mask=use, background_degree=1, backend="cupy")
    diff, kern = to(fit.residual).copy(), to(fit.kernel)
    diff[~use] = np.nan
    noise = standardize_constant_kernel_residual(diff, kernel=kern, target_variance=np.where(use, t_var, np.nan),
                                                 reference_variance=np.where(use, rv, np.nan))
    z = np.asarray(noise.standardized_residual)
    regs = identify_residual_hotspots(z, robust_sigma=1.0, threshold_sigma=5.0, max_regions=None)
    return dict(diff=diff, z=z, mv=np.asarray(noise.marginal_residual_variance), regs=regs, use=use, kern=kern,
                ksum=float(kern.sum()), chi2=float(fit.chi2 / fit.dof))


single = members["reference"]
REFS = {"single": single,
        "weighted": combine(NAMES),
        "mean": combine(NAMES, "mean"),
        "samevar": (combine(NAMES)[0], single[1], combine(NAMES)[2]),
        "two": combine(NAMES[:2])}
base = chain(*single, tgt, tv)
YY, XX = np.mgrid[:800, :800]
yy, xx = np.ogrid[:800, :800]
allowed = binary_erosion(np.isfinite(base["z"]), iterations=12)  # same fake positions for every reference
allowed[:20] = allowed[-20:] = False
allowed[:, :20] = allowed[:, -20:] = False
for q in base["regs"]:
    py, px = q["peak_yx"]
    allowed &= ((yy - py) ** 2 + (xx - px) ** 2) > 25 ** 2
allowed &= ((yy - 400) ** 2 + (xx - 402) ** 2) > 40 ** 2
LEVELS = (2000, 1400, 1000, 700)


def inject(refs, seed, n=25):
    rng = np.random.default_rng(seed)
    cand, placed = np.argwhere(allowed), []
    for f in LEVELS:
        k = 0
        while k < n:
            y, x = cand[rng.integers(len(cand))] + rng.uniform(-.5, .5, 2)
            if all((y - p[1]) ** 2 + (x - p[2]) ** 2 > 30 ** 2 for p in placed):
                placed.append((f, y, x))
                k += 1
    fake = np.zeros((800, 800))
    for f, y, x in placed:
        sl = (slice(int(y) - 12, int(y) + 13), slice(int(x) - 12, int(x) + 13))
        fake[sl] += f / (2 * np.pi * SIG ** 2) * np.exp(-((YY[sl] - y) ** 2 + (XX[sl] - x) ** 2) / (2 * SIG ** 2))
    t_img = tgt + fake + rng.normal(size=fake.shape) * np.sqrt(fake / GAIN)
    r = chain(*refs, t_img, tv + fake / GAIN)
    peaks = np.array([q["peak_yx"] for q in r["regs"]], float)
    lv = np.array([p[0] for p in placed])
    found = np.array([np.hypot(peaks[:, 0] - y, peaks[:, 1] - x).min() < 3 for f, y, x in placed])
    ctr = np.rint([[x, y] for f, y, x in placed]).astype(float)
    cut, cv = window_stamps(r["diff"], ctr, 21), window_stamps(r["mv"], ctr, 21)
    valid = np.isfinite(cut) & np.isfinite(cv) & (cv > 0)
    src = fit_single_sources(cp.asarray(np.nan_to_num(cut)), cp.asarray(np.where(valid, cv, 1.0)),
                             cp.asarray(np.zeros((len(ctr), 2))), SIG, mask=cp.asarray(valid))
    err = np.where(valid.any((1, 2)), to(src.flux_error), np.nan)
    return lv, found, err


runs = {}
print(f"\ninjection: {len(SEEDS)} seed(s) x {len(LEVELS)} levels x 25 fakes, the same positions for every reference")
for c in CONFIGS:
    b = chain(*REFS[c], tgt, tv)
    blank = binary_erosion(b["use"], iterations=12)
    rvc = fftconvolve(np.where(b["use"], REFS[c][1], 0), b["kern"] ** 2, mode="same")
    share = float(np.median((rvc / (rvc + tv))[blank]))
    res = [inject(REFS[c], s) for s in SEEDS]
    lv = np.concatenate([q[0] for q in res]); fd = np.concatenate([q[1] for q in res]); er = np.concatenate([q[2] for q in res])
    runs[c] = b
    print(f"\n{c}: usable {b['use'].mean():.3f}  kernel sum {b['ksum']:.3f}  chi2/dof {b['chi2']:.2f}  "
          f"hotspots {len(b['regs'])}  reference's share of the difference variance {share:.2f}")
    for f in LEVELS:
        m = lv == f
        print(f"   {f:5d} counts: found {fd[m].sum():3d}/{m.sum()}  median error {np.nanmedian(er[m]):.0f}")

new = {}
for c in CONFIGS:
    if c == "single":
        continue
    new[c] = [q for q in runs[c]["regs"] if not base["use"][int(q["peak_yx"][0]), int(q["peak_yx"][1])]]
    if new[c]:
        print(f"\n{c}: {len(new[c])} hotspots outside the single reference's usable area")
    for q in new[c]:
        y, x = map(int, q["peak_yx"])
        who = [n for n in NAMES if members[n][2][y, x]]
        print(f"   x {x} y {y}  z {runs[c]['z'][y, x]:6.1f}  covered by {', '.join(who)}")

fig, ax = plt.subplots(2, 4, figsize=(13, 6.8))
for a, n in zip(ax[0], NAMES):
    a.imshow(members[n][2], origin="lower", cmap="gray", vmin=0, vmax=1)
    a.set_title(f"{n}: usable {members[n][2].mean():.0%}\nseeing {SEEING[n]:.2f} px", fontsize=9)
cnt = sum(members[n][2].astype(int) for n in NAMES)
im = ax[0, 3].imshow(cnt, origin="lower", cmap="viridis", vmin=0, vmax=3)
ax[0, 3].set_title(f"nights per pixel\n(target seeing {SEEING['target']:.2f} px)", fontsize=9)
fig.colorbar(im, ax=ax[0, 3], ticks=[0, 1, 2, 3], fraction=.046)
show = [c for c in CONFIGS][:4]
for a, c in zip(ax[1], show):
    a.imshow(runs[c]["z"], origin="lower", cmap="gray", vmin=-6, vmax=6)
    a.set_title(f"z, {c}: usable {runs[c]['use'].mean():.0%}, {len(runs[c]['regs'])} hotspots", fontsize=9)
    for q in new.get(c, []):
        a.add_patch(plt.Circle(q["peak_yx"][::-1], 14, fill=False, color="#ffb000", lw=1.2))
for a in ax[1, len(show):]:
    a.axis("off")
for a in ax.flat:
    a.set_xticks([]); a.set_yticks([])
fig.text(.99, .005, "Pan-STARRS1 DR2, M101, r band. Circles: hotspots outside the single night's usable area.",
         ha="right", fontsize=7, color="0.4")
fig.tight_layout()
fig.savefig(OUT, dpi=110)
print("\nwrote", OUT)
