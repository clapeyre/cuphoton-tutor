"""8.3: xImage on real frames: the Pan-STARRS1 nights of M101 from Module 04 (course/modules/04-your-own-data/
data, or DATA=...). The frames are already on one pixel grid (4.5). The answer to the fakes is in this file:
run it in place, don't copy it.

    python nights.py run OUT NAME [--nights refs|all] [--pedestal P] [--algo l2|rho] [--fakes F] [--device cpu|cuda]
                                  [--max-iter N] [--stop-tol T]
        build a bundle from a 160 x 160 cut around SN 2011fe's position, plant fake stars of flux F (default
        2000 counts, 0 for none) in every frame, reconstruct into OUT/runs/NAME, and report: the receipt's
        main lines; the fakes' measured flux against the planted one, in the scene and in the median of the
        frames; and the light at the supernova's position in each frame and in the scene
    python nights.py figure PNG RUN [RUN ...]
        the median of the frames and each run's scene, around the supernova's position

How the bundle is made (show it): each frame is scaled to one zero point (24.6, from FPA.ZP), its variance
by the square; mask 0 = good (no data and flagged pixels become bad, with a huge variance); one Gaussian
PSF per frame, 25 x 25, with the night's seeing (CHIP.SEEING, FWHM in pixels) as width; --pedestal adds P
counts to every frame (and is subtracted from the scene afterwards). Nights: refs = 2011-04-22 (two) and
2011-05-11, before the supernova; all = those and 2012-04-12, when it was bright.

The fakes (don't tell before the run): 24 point sources of flux F on a 27-pixel grid, at least 20 pixels
from the supernova, each blurred by that frame's own Gaussian PSF: the PSF model is exactly right for them.
"""
import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

DATA = Path(os.environ.get("DATA") or Path(__file__).resolve().parents[2] / "04-your-own-data/data")
NIGHTS = {"refs": ("reference", "reference-b", "reference-c"), "all": ("reference", "reference-b", "reference-c", "target")}
CY, CX, K, ZP = 400, 402, 25, 24.6
HALF = int(os.environ.get("HALF", 80))  # half the cut's side; HALF=300 for a 600 x 600 timing run
H = 2 * HALF


def checkout() -> Path:
    import cuphoton
    return Path(os.environ.get("CUPHOTON_REPO") or Path(cuphoton.__file__).resolve().parents[2])


def fake_positions():
    c = HALF
    return [(y, x) for y in range(26, H - 25, 27) for x in range(26, H - 25, 27) if abs(y - c) + abs(x - c) > 20]


def aperture(img, y, x, r=5, rin=8, rout=12):
    yy, xx = np.indices(img.shape)
    rr = np.hypot(yy - y, xx - x)
    return float((img[rr < r] - np.median(img[(rr >= rin) & (rr < rout)])).sum())


def build(names, pedestal, flux):
    from astropy.io import fits
    from scipy.signal import fftconvolve

    sl = (slice(CY - HALF, CY + HALF), slice(CX - HALF, CX + HALF))
    yy, xx = np.indices((K, K)) - K // 2
    imgs, vars_, masks, psfs = [], [], [], []
    for n in names:
        h = fits.getheader(DATA / f"{n}.fits")
        scale = 10 ** (0.4 * (ZP - h["FPA.ZP"]))
        im = fits.getdata(DATA / f"{n}.fits")[sl].astype(float) * scale
        va = fits.getdata(DATA / f"{n}.var.fits")[sl].astype(float) * scale**2
        good = (fits.getdata(DATA / f"{n}.mask.fits")[sl] == 0) & np.isfinite(im) & np.isfinite(va) & (va > 0)
        sigma = h["CHIP.SEEING"] / 2.3548
        psf = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
        psf /= psf.sum()
        if flux:
            pts = np.zeros((H, H))
            for y, x in fake_positions():
                pts[y, x] = flux
            im = im + fftconvolve(pts, psf, mode="same")
        imgs.append(np.where(good, im, 0.0) + pedestal)
        vars_.append(np.where(good, va, 1e10))
        masks.append(good)
        psfs.append(psf)
        print(f"  {n:12s} MJD {h.get('MJD-OBS', float('nan')):.2f}  seeing {h['CHIP.SEEING']:.2f} px (PSF sigma {sigma:.2f})  "
              f"scale {scale:.3f}  usable {good.mean():.0%}  sky sigma {np.sqrt(np.median(va[good])):.1f}")
    stack = lambda a: np.stack(a, -1)[None]
    return stack(imgs), stack(vars_), stack(masks), np.stack(psfs, -1)[:, :, None, :]


def run(a) -> None:
    import yaml
    from cuphoton.ximage import load_ximage_bundle, validate_bundle
    from cuphoton.ximage.workflows import run_reconstruction

    out = Path(a.out)
    names = NIGHTS[a.nights]
    print(f"{a.name}: nights {a.nights}, pedestal {a.pedestal:g}, algorithm {a.algo}, fakes {a.fakes:g}")
    images, variances, masks, psfs = build(names, a.pedestal, a.fakes)
    d = out / "bundles" / a.name
    d.mkdir(parents=True, exist_ok=True)
    for key, arr in (("images", images), ("variances", variances), ("masks", masks), ("psfs", psfs)):
        np.save(d / f"{key}.npy", arr)
    with load_ximage_bundle(d) as b:
        print("  validate_bundle issues:", validate_bundle(b))
    cfg = yaml.safe_load((checkout() / f"examples/ximage/reconstruct-{a.algo}.example.yaml").read_text())
    cfg["data"]["base"] = str(d)
    cfg["output"] = {"root_dir": str(out / "runs"), "name": a.name, "overwrite": True}
    cfg["roi"] = {"center": None, "height": H - K + 1, "width": H - K + 1}
    cfg["mask"] = {"mode": "provided"}
    if a.max_iter:
        cfg["max_iter"] = a.max_iter
    if a.stop_tol is not None:
        cfg["stop_tol"] = a.stop_tol
    (out / "runs").mkdir(parents=True, exist_ok=True)
    p = out / "runs" / f"{a.name}.yaml"
    p.write_text(yaml.safe_dump(cfg, sort_keys=False))
    t = time.perf_counter()
    r = run_reconstruction(p, device_override=a.device) if a.device else run_reconstruction(p)
    dt = time.perf_counter() - t
    s = r.summary
    tr = s["trace_summary"]
    print(f"  run {r.run_dir}: device {s['performance']['device']['device']}, {dt:.1f} s, iterations "
          f"{tr['iterations_count']}, loss {tr['loss_last']:.2f}")
    scene = np.load(s["saved"]["image"])[0, :, :, 0] - a.pedestal  # same 160 x 160 grid as the cut
    if a.fakes:
        pos = fake_positions()
        fs = np.array([aperture(scene, y, x) for y, x in pos]) / a.fakes
        med = np.median(images[0] - a.pedestal, axis=-1)
        fm = np.array([aperture(med, y, x, r=8, rin=12, rout=18) for y, x in pos]) / a.fakes
        print(f"  {len(pos)} fakes of {a.fakes:g}: measured/planted in the scene: median {np.median(fs):.3f}, scatter {fs.std():.3f}; "
              f"in the median of the frames: median {np.median(fm):.3f}, scatter {fm.std():.3f}")
    c = HALF
    print("  light at the supernova's position (5-pixel aperture): frames " +
          ", ".join(f"{n} {aperture(images[0, :, :, k] - a.pedestal, c, c):.0f}" for k, n in enumerate(names)) +
          f"; scene {aperture(scene, c, c):.0f}")


def figure(png, runs) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c, w = HALF, 40
    panels = [(np.load(Path(r) / "artifacts/image.npy")[0, :, :, 0], Path(r).name) for r in runs]
    frames = np.load(Path(runs[0]).parent.parent / "bundles" / Path(runs[0]).name / "images.npy")[0]
    allp = [(np.median(frames, axis=-1), "median of the frames")]
    if frames.shape[-1] == 4:
        allp.append((frames[..., 3], "the 2012-04-12 frame"))
    allp += panels
    fig, axes = plt.subplots(1, len(allp), figsize=(3.2 * len(allp), 3.4), squeeze=False)
    for ax, (p, title) in zip(axes[0], allp):
        cut = p[c - w:c + w, c - w:c + w]
        mid = np.median(cut)
        noise = 1.4826 * np.median(np.abs(cut - mid))
        lo, hi = mid - 2 * noise, cut.max()
        ax.imshow(np.arcsinh((np.clip(cut, lo, hi) - lo) / max(5 * noise, 1e-9)), origin="lower", cmap="gray")
        ax.set_title(title, fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.text(0.99, 0.01, "Pan-STARRS1 r band, M101; supernova position at the centre", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "run":
        ap = argparse.ArgumentParser()
        ap.add_argument("out"); ap.add_argument("name")
        ap.add_argument("--nights", default="refs", choices=NIGHTS)
        ap.add_argument("--pedestal", type=float, default=0.0)
        ap.add_argument("--algo", default="l2", choices=("l2", "rho"))
        ap.add_argument("--fakes", type=float, default=2000.0)
        ap.add_argument("--device", choices=("cpu", "cuda"))
        ap.add_argument("--max-iter", type=int)
        ap.add_argument("--stop-tol", type=float)
        run(ap.parse_args(sys.argv[2:]))
    elif len(sys.argv) >= 4 and sys.argv[1] == "figure":
        figure(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
