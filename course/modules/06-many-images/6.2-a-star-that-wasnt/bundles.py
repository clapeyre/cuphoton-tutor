"""6.2: two more bundles of 6.1's field. Both pass validate_bundle. The answer is in this file: run it in
place, don't copy it.

    python bundles.py make DIR                 write DIR/bundle-1 and DIR/bundle-2 and validate them
    python bundles.py run BUNDLE RUNS NAME [l2|rho]
                                               reconstruct (the checkout's example configuration for that
                                               algorithm) into RUNS/NAME; print the receipt's main lines, the
                                               planted sources' fluxes, the brightest pixel away from them,
                                               and how well the scene, blurred by each frame's PSF, matches
                                               each frame (chi-squared per pixel, and the worst pixel)
    python bundles.py widths BUNDLE            per frame: the width of the brightest star measured in the frame,
                                               against the width of the PSF the bundle records for that frame
    python bundles.py figure PNG RUN [RUN ...] the reconstructed scenes side by side

What's wrong (don't tell before they've judged the runs):
  bundle-1  6.1's three frames, plus a cosmic ray: one pixel of frame 2 at (row 30, column 12) is 40 higher.
  bundle-2  6.1's frames, but frame 3's PSF is recorded as 0.6 pixels wide; the frame was blurred by 1.2.
"""
import sys
from pathlib import Path

import numpy as np

SOURCES = ((20, 22, 30.0), (35, 40, 50.0), (44, 18, 20.0))
SKY, BORDER, OFFSET = 0.1, 4, 8
y_, x_ = np.indices((9, 9)) - 4


def gauss(s):
    p = np.exp(-(x_**2 + y_**2) / (2 * s**2))
    return p / p.sum()


def checkout() -> Path:
    import os
    import cuphoton
    return Path(os.environ.get("CUPHOTON_REPO") or Path(cuphoton.__file__).resolve().parents[2])


def make(out: Path) -> None:
    from scipy.signal import convolve2d
    from cuphoton.ximage import load_ximage_bundle, validate_bundle

    scene = np.full((64, 64), SKY)
    for r, c, f in SOURCES:
        scene[r, c] = f
    for name, told, ray in (("bundle-1", (0.8, 1.0, 1.2), True), ("bundle-2", (0.8, 1.0, 0.6), False)):
        rng = np.random.default_rng(0)
        psfs = np.empty((9, 9, 1, 3))
        images = np.empty((1, 64, 64, 3))
        for k, (true, rec) in enumerate(zip((0.8, 1.0, 1.2), told)):
            psfs[:, :, 0, k] = gauss(rec)
            images[0, :, :, k] = convolve2d(scene, gauss(true), mode="same") + rng.normal(0, 0.01, scene.shape)
        if ray:
            images[0, 30, 12, 1] += 40.0
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        np.save(d / "images.npy", images)
        np.save(d / "variances.npy", np.full_like(images, 0.01**2))
        np.save(d / "psfs.npy", psfs)
        with load_ximage_bundle(d) as b:
            print(f"{d}: issues {validate_bundle(b)}")


def run(d: Path, runs: Path, name: str, algo: str) -> None:
    import yaml
    from scipy.signal import convolve2d
    from cuphoton.ximage.workflows import run_reconstruction

    config = yaml.safe_load((checkout() / f"examples/ximage/reconstruct-{algo}.example.yaml").read_text())
    config["data"]["base"] = str(d)
    config["output"] = {"root_dir": str(runs), "name": name, "overwrite": True}
    runs.mkdir(parents=True, exist_ok=True)
    cfg = runs / f"{name}.yaml"
    cfg.write_text(yaml.safe_dump(config, sort_keys=False))
    result = run_reconstruction(cfg)
    s = result.summary
    tr = s["trace_summary"]
    print(f"{name}: algorithm {s.get('algorithm', algo)}, device {s['performance']['device']['device']}, "
          f"iterations {tr['iterations_count']}, loss {tr['loss_last']:.2f}")
    img = np.load(s["saved"]["image"])[0, :, :, 0]
    o = OFFSET - BORDER
    away = np.zeros(img.shape, bool)
    away[BORDER:-BORDER, BORDER:-BORDER] = True  # inside the region, not its border
    for r, c, f in SOURCES:
        box = img[r - o - 4:r - o + 5, c - o - 4:c - o + 5]
        away[r - o - 5:r - o + 6, c - o - 5:c - o + 6] = False
        print(f"  source at ({r}, {c}): planted {f:.0f}, peak {img[r - o, c - o]:.1f}, flux {(box - SKY).sum():.1f}")
    ry, rx = np.unravel_index(np.argmax(np.where(away, img, -np.inf)), img.shape)
    print(f"  brightest pixel away from them: {img[ry, rx]:.1f} at ({ry + o}, {rx + o})")
    # forward model: the scene blurred by each frame's PSF, against that frame, inside the region
    images = np.load(d / "images.npy")[0]
    psfs = np.load(d / "psfs.npy")[:, :, 0, :]
    var = np.load(d / "variances.npy")[0]
    canvas = np.zeros((64, 64))
    canvas[o:o + img.shape[0], o:o + img.shape[1]] = img
    reg = slice(OFFSET, 64 - OFFSET)
    for k in range(images.shape[-1]):
        model = convolve2d(canvas, psfs[:, :, k], mode="same")
        chi = ((images[:, :, k] - model) ** 2 / var[:, :, k])[reg, reg]
        wy, wx = np.unravel_index(np.argmax(chi), chi.shape)
        print(f"  frame {k + 1}: chi-squared per pixel {chi.mean():.1f}, worst pixel {chi.max():.0f} at ({wy + OFFSET}, {wx + OFFSET})")


def sigma_of(a):
    a = np.clip(a - np.median(a), 0, None)
    yy, xx = np.indices(a.shape)
    t = a.sum()
    cy, cx = (a * yy).sum() / t, (a * xx).sum() / t
    return float(np.sqrt(((a * ((yy - cy) ** 2 + (xx - cx) ** 2)).sum() / t) / 2))


def widths(d: Path) -> None:
    images = np.load(d / "images.npy")[0]
    psfs = np.load(d / "psfs.npy")[:, :, 0, :]
    for k in range(images.shape[-1]):
        frame = images[:, :, k]
        r, c = np.unravel_index(np.argmax(frame[8:56, 8:56]), (48, 48))
        r, c = r + 8, c + 8
        print(f"frame {k + 1}: brightest star at ({r}, {c}), measured width {sigma_of(frame[r - 4:r + 5, c - 4:c + 5]):.2f} px; "
              f"recorded PSF width {sigma_of(psfs[:, :, k]):.2f} px")


def figure(png: str, runs: list) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    scenes = [(np.load(Path(r) / "artifacts/image.npy")[0, BORDER:-BORDER, BORDER:-BORDER, 0], Path(r).name) for r in runs]
    fig, axes = plt.subplots(1, len(scenes), figsize=(3.2 * len(scenes) + 1, 3.3), squeeze=False)
    norm = LogNorm(vmin=0.05, vmax=max(p.max() for p, _ in scenes))
    for ax, (p, title) in zip(axes[0], scenes):
        im = ax.imshow(np.clip(p, 0.05, None), origin="lower", cmap="magma", norm=norm)
        ax.set_title(title, fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=list(axes[0]), shrink=0.8, label="intensity (log)")
    fig.savefig(png, dpi=130, bbox_inches="tight")
    print("wrote", png)


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 3 and a[1] == "make":
        make(Path(a[2]))
    elif len(a) >= 5 and a[1] == "run":
        run(Path(a[2]), Path(a[3]), a[4], a[5] if len(a) > 5 else "l2")
    elif len(a) >= 3 and a[1] == "widths":
        widths(Path(a[2]))
    elif len(a) >= 4 and a[1] == "figure":
        figure(a[2], a[3:])
    else:
        sys.exit(__doc__)
