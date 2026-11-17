"""4.6: teach xScan a real/bogus classifier from this pair alone, score the candidates, and test it on
kinds of bogus it has never seen.  GPU environment; run each step from the same working directory.

    python classify.py build <dataset dir> [--with-rays-and-trails]
        Real (label 1): 480 point sources planted in the target (the 4.4 recipe; flux 800 to 8,000
        counts, log-uniform; 8 realisations of 60). Bogus (label 0): the 88 sources of the reference
        brighter than 20 counts after a 1.5 px smoothing (stars and knots of M101, on both nights),
        away from the supernova and 4.3's candidates. With --with-rays-and-trails, also 80 each of one-pixel
        and two-pixel cosmic rays and 31-px satellite-trail segments added to the target (seed 21).
        Every cutout is a 21 x 21 triplet (target, reference, difference), each channel in units of its
        own noise, and appears in 4 rotations that share one split_group. Split 60/20/20 by group.
        Then write the xScan dataset files and the training YAML (the guide's tiny model, 10 epochs).
    cuphoton xscan data-validate / data-check-training-labels / train-inada-triplet / evaluate-real-bogus
        (the guide's commands; train with --config <dataset dir>/train.yaml)
    python classify.py score <dataset dir> <run dir> <out.png>
        p(real) of 4.3's candidates A-D and of every 4.2 hotspot; the figure shows A-D.
    python classify.py stress <dataset dir> <run dir> <out.png>
        40 each of one-pixel and two-pixel cosmic rays and trail segments, on empty sky, seed 3 (not
        the training seed), and 60 sources of 1,500 counts planted on top of fainter sources that
        are in the reference (a supernova in a knot of its galaxy), and on empty sky.
Env: DATA (default ./data if it holds target.fits, else the course's data/), SEED (dataset seed, default 5).
"""
import json
import os
import pathlib
import sys
import warnings

warnings.simplefilter("ignore")
import cupy as cp
import numpy as np
from astropy.io import fits
from scipy.ndimage import binary_erosion, gaussian_filter, maximum_filter
from cuphoton.xpois import (GaussianBasisComponent, identify_residual_hotspots, solve_constant_kernel,
                            standardize_constant_kernel_residual)

D = os.environ.get("DATA") or ("data" if os.path.exists("data/target.fits") else str(pathlib.Path(__file__).resolve().parents[1] / "data"))
BAD, SIG, S = 8575, 1.57, 21
H = S // 2
L = lambda n, s="": fits.getdata(f"{D}/{n}{s}.fits").astype(np.float64)
to = lambda x: cp.asnumpy(x) if not isinstance(x, np.ndarray) else x
ref, tgt, rv, tv = L("reference"), L("target"), L("reference", ".var"), L("target", ".var")
rm, tm = fits.getdata(f"{D}/reference.mask.fits"), fits.getdata(f"{D}/target.mask.fits")
GAIN = fits.getheader(f"{D}/target.fits")["CELL.GAIN"]
use = np.isfinite(ref) & np.isfinite(tgt) & np.isfinite(rv) & np.isfinite(tv) & ((rm & BAD) == 0) \
    & ((tm & BAD) == 0) & (rv > 0) & (tv > 0)
basis = [GaussianBasisComponent(0.7, 4), GaussianBasisComponent(1.4, 2), GaussianBasisComponent(2.8, 2)]
CANDS = {"A": (640, 403), "B": (246, 46), "C": (400, 402), "D": (84, 274)}  # 4.3's four, (y, x)
YY, XX = np.mgrid[:800, :800]


def chain(t_img, t_var):
    """The 4.2 chain: match, subtract, standardize. Returns difference, z, and the difference's variance."""
    fit = solve_constant_kernel(np.where(use, ref, 0.0), np.where(use, t_img, 0.0), basis, kernel_shape=(19, 19),
                                variance=np.where(use, t_var, 1e12), fit_mask=use, background_degree=1, backend="cupy")
    diff = to(fit.residual).copy()
    diff[~use] = np.nan
    noise = standardize_constant_kernel_residual(diff, kernel=to(fit.kernel), target_variance=np.where(use, t_var, np.nan),
                                                 reference_variance=np.where(use, rv, np.nan))
    return diff, np.asarray(noise.standardized_residual), np.asarray(noise.marginal_residual_variance)


def triplet(t_img, t_var, diff, mv, y, x):
    """Target, reference, difference around (y, x), each in units of its own noise."""
    sl = (slice(y - H, y + H + 1), slice(x - H, x + H + 1))
    planes = (t_img[sl] / np.sqrt(np.nanmedian(t_var[sl])), ref[sl] / np.sqrt(np.nanmedian(rv[sl])), diff[sl] / np.sqrt(mv[sl]))
    return np.stack([np.nan_to_num(a) for a in planes]).astype(np.float32)


def plant(points, flux, dx=0):
    fake = np.zeros((800, 800))
    for y, x in points:
        x = x + dx
        sl = (slice(int(y) - 12, int(y) + 13), slice(int(x) - 12, int(x) + 13))
        fake[sl] += flux(y, x) / (2 * np.pi * SIG ** 2) * np.exp(-((YY[sl] - y) ** 2 + (XX[sl] - x) ** 2) / (2 * SIG ** 2))
    return fake


def spread(rng, allowed, n, avoid=(), gap=30):
    cand, pts = np.argwhere(allowed), []
    while len(pts) < n:
        y, x = cand[rng.integers(len(cand))]
        if all((y - p[0]) ** 2 + (x - p[1]) ** 2 > gap ** 2 for p in list(avoid) + pts):
            pts.append((int(y), int(x)))
    return pts


def rays_and_trails(rng, pts, kind):
    art = np.zeros((800, 800))
    for y, x in pts:
        a, th = rng.uniform(300, 2000), rng.uniform(0, np.pi)
        if kind == "trail":
            for t in np.linspace(-15, 15, 121):
                art[int(round(y + np.sin(th) * t)), int(round(x + np.cos(th) * t))] = 80
        else:
            art[y, x] += a
            if kind == "ray2":
                art[y, x + 1] += .6 * a
    return art


diff0, z0, mv0 = chain(tgt, tv)
good = binary_erosion(np.isfinite(z0), iterations=H + 2)
good[:H + 2] = good[-H - 2:] = False
good[:, :H + 2] = good[:, -H - 2:] = False
yy, xx = np.ogrid[:800, :800]
keep_out = ((yy - 400) ** 2 + (xx - 402) ** 2) < 40 ** 2
for y, x in CANDS.values():
    keep_out |= ((yy - y) ** 2 + (xx - x) ** 2) < 15 ** 2
sm = gaussian_filter(np.nan_to_num(ref), 1.5)
local_max = (sm == maximum_filter(sm, 9)) & good & ~keep_out
empty = good & ~keep_out & (sm < 4)
step = sys.argv[1]


def load_model(run):
    import torch
    from cuphoton.xscan.training import load_model_from_checkpoint
    model, _, _ = load_model_from_checkpoint(pathlib.Path(run), device=torch.device("cuda"))

    def score(trips):
        with torch.no_grad():
            return torch.sigmoid(model(torch.from_numpy(np.stack(trips)).cuda())).cpu().numpy()
    return score


if step == "build":
    out = pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(int(os.environ.get("SEED", 5)))
    X, lab, meta = [], [], []
    for y, x in np.argwhere(local_max & (sm > 20)):
        X.append(triplet(tgt, tv, diff0, mv0, y, x)); lab.append(0); meta.append(("star", "star on both nights", y, x))
    for _ in range(8):
        pts = spread(rng, good & ~keep_out, 60)
        pts = [(y + rng.uniform(-.5, .5), x + rng.uniform(-.5, .5)) for y, x in pts]
        fl = {p: float(np.exp(rng.uniform(np.log(800), np.log(8000)))) for p in pts}
        fake = plant(pts, lambda y, x: fl[(y, x)])
        t_img, t_var = tgt + fake + rng.normal(size=fake.shape) * np.sqrt(fake / GAIN), tv + fake / GAIN
        diff, _, mv = chain(t_img, t_var)
        for y, x in pts:
            X.append(triplet(t_img, t_var, diff, mv, int(round(y)), int(round(x)))); lab.append(1)
            meta.append(("fake", "injection", y, x))
    if "--with-rays-and-trails" in sys.argv:
        rng4 = np.random.default_rng(21)
        for kind in ("ray1", "ray2", "trail"):
            pts = spread(rng4, empty, 80)
            t_img = tgt + rays_and_trails(rng4, pts, kind)
            diff, _, mv = chain(t_img, tv)
            for y, x in pts:
                X.append(triplet(t_img, tv, diff, mv, y, x)); lab.append(0); meta.append((kind, "synthetic cosmic ray or trail", y, x))
    lab = np.array(lab)
    split = np.zeros(len(lab), int)
    for c in (0, 1):
        g = rng.permutation(np.flatnonzero(lab == c)); n = len(g)
        split[g[int(.6 * n):int(.8 * n)]] = 1
        split[g[int(.8 * n):]] = 2
    R = 4  # rotations; the copies of one candidate share its group, so they never straddle splits
    arr = np.array([np.rot90(t, k, axes=(1, 2)) for t in X for k in range(R)])
    for k, name in enumerate(["search", "template", "difference"]):
        np.save(out / f"{name}.npy", np.ascontiguousarray(arr[:, k]))
    np.save(out / "labels.npy", np.repeat(lab, R)); np.save(out / "split.npy", np.repeat(split, R))
    rows = [dict(candidate_id=f"{m[0]}-{i}-r{k}", split_group=f"{m[0]}-{i}", split=("train", "val", "test")[split[i]],
                 label=int(lab[i]), label_source=m[1], exposure_id=0, ccd_id=0, band="r", x=float(m[3]), y=float(m[2]))
            for i, m in enumerate(meta) for k in range(R)]
    (out / "metadata.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    (out / "train.yaml").write_text(f"""dataset_dir: {out.resolve()}
output_root: {(out.parent / 'runs').resolve()}
run_name: {out.name}
epochs: 10
batch_size: 32
early_stopping_metric: val_loss   # keep the epoch with the lowest validation loss
device: auto
model:                            # the guide's tiny network: trains in seconds
  image_size: {S}
  depths: [1, 1]
  num_heads: [1, 1]
  embed_dims: [16, 16]
  decoder_embedding_dim: 16
""")
    kinds = {}
    for m in meta:
        kinds[m[0]] = kinds.get(m[0], 0) + 1
    print(f"wrote {out}: {len(rows)} cutouts ({len(meta)} candidates x {R} rotations): {kinds}")
    print(f"training config: {out}/train.yaml (runs go to {(out.parent / 'runs').resolve()}/{out.name})")

elif step == "score":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    score = load_model(sys.argv[3])
    p = {k: float(score([triplet(tgt, tv, diff0, mv0, *v)])[0]) for k, v in CANDS.items()}
    print("4.3's candidates, p(real):", "  ".join(f"{k} {v:.3f}" for k, v in p.items()))
    regs = identify_residual_hotspots(z0, robust_sigma=1.0, threshold_sigma=5.0, max_regions=None)
    print(f"every 4.2 hotspot ({len(regs)}): x, y, z, p(real)")
    for r in sorted(regs, key=lambda r: -z0[int(r["peak_yx"][0]), int(r["peak_yx"][1])]):
        y, x = map(int, r["peak_yx"])
        print(f"   {x:4d} {y:4d} {z0[y, x]:6.1f}  {score([triplet(tgt, tv, diff0, mv0, y, x)])[0]:.3f}")
    fig, ax = plt.subplots(3, 4, figsize=(7.5, 6))
    for col, (k, (y, x)) in enumerate(CANDS.items()):
        t = triplet(tgt, tv, diff0, mv0, y, x)
        for row in range(3):
            ax[row, col].imshow(t[row], origin="lower", cmap="gray" if row < 2 else "RdBu_r",
                                vmin=(-3 if row < 2 else -8), vmax=(max(30, t[0].max()) if row < 2 else 8))
            ax[row, col].set_xticks([]); ax[row, col].set_yticks([])
        ax[0, col].set_title(f"{k}   p(real) {p[k]:.2f}", fontsize=9)
    for row, name in enumerate(["target", "reference", "difference"]):
        ax[row, 0].set_ylabel(name, fontsize=9)
    fig.tight_layout(); fig.savefig(sys.argv[4], dpi=110); print("wrote", sys.argv[4])

elif step == "stress":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    score = load_model(sys.argv[3])
    rng = np.random.default_rng(3)
    show = []
    for kind, name in (("ray1", "cosmic ray, 1 px"), ("ray2", "cosmic ray, 2 px"), ("trail", "satellite trail")):
        pts = spread(rng, empty, 40)
        t_img = tgt + rays_and_trails(rng, pts, kind)
        diff, z, mv = chain(t_img, tv)
        trips = [triplet(t_img, tv, diff, mv, y, x) for y, x in pts]
        pr = score(trips)
        print(f"{name:18s} median z {np.median([z[y, x] for y, x in pts]):5.0f}   p(real) median {np.median(pr):.3f}   "
              f"called real (p > 0.5): {(pr > .5).sum()}/{len(pr)}")
        show += [(name, trips[i], pr[i]) for i in np.argsort(-pr)[:2]]
    rng2 = np.random.default_rng(7)
    srcs = [tuple(v) for v in np.argwhere(local_max & (sm > 10) & (sm <= 20))[rng2.permutation(int((local_max & (sm > 10) & (sm <= 20)).sum()))]]
    on = []
    for y, x in srcs:
        if all((y - p[0]) ** 2 + (x - p[1]) ** 2 > 30 ** 2 for p in on):
            on.append((int(y), int(x)))
        if len(on) == 60:
            break
    off = spread(rng2, empty, 60, avoid=on)
    for name, pts in (("new light on a source", on), ("new light on empty sky", off)):
        fake = plant(pts, lambda y, x: 1500.0)
        t_img, t_var = tgt + fake + rng2.normal(size=fake.shape) * np.sqrt(fake / GAIN), tv + fake / GAIN
        diff, z, mv = chain(t_img, t_var)
        pr = score([triplet(t_img, t_var, diff, mv, y, x) for y, x in pts])
        print(f"{name:22s} (1,500 counts) median z {np.median([z[y, x] for y, x in pts]):4.1f}   "
              f"called real: {(pr > .5).sum()}/{len(pr)}")
    fig, ax = plt.subplots(3, len(show), figsize=(1.5 * len(show), 4.8))
    for col, (name, t, pr) in enumerate(show):
        for row in range(3):
            ax[row, col].imshow(t[row], origin="lower", cmap="gray" if row < 2 else "RdBu_r",
                                vmin=(-3 if row < 2 else -8), vmax=(30 if row < 2 else 8))
            ax[row, col].set_xticks([]); ax[row, col].set_yticks([])
        ax[0, col].set_title(f"{name}\np(real) {pr:.2f}", fontsize=7)
    for row, name in enumerate(["target", "reference", "difference"]):
        ax[row, 0].set_ylabel(name, fontsize=8)
    fig.text(.99, .005, "Synthetic cosmic rays and trails added to the Pan-STARRS1 target.", ha="right", fontsize=6, color="0.4")
    fig.tight_layout(); fig.savefig(sys.argv[4], dpi=110); print("wrote", sys.argv[4])
