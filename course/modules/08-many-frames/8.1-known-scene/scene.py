"""8.1: the user guide's xImage example. Three blurred, noisy frames of three point sources, one PSF per
frame; reconstruct one scene from them and check it against the scene that made them.

    python scene.py make DIR                     write the bundle (DIR/images.npy, variances.npy, psfs.npy)
                                                 and print validate_bundle's issues and the arrays' shapes
    python scene.py run DIR RUNS NAME [MAX_ITER] reconstruct (L2, the checkout's example configuration, the
                                                 GPU when PyTorch sees one) into RUNS/NAME; print the receipt's
                                                 main lines, each source's flux against the planted one, and
                                                 the evaluation against the median of the frames
    python scene.py figure DIR RUN PNG           one frame, the median of the frames, and the reconstruction

Planted: sky 0.1 everywhere; sources of 30, 50 and 20 at (row, column) (20, 22), (35, 40), (44, 18);
Gaussian PSFs 0.8, 1.0 and 1.2 pixels wide; noise 0.01 per pixel. As in the guide.
"""
import sys
from pathlib import Path

import numpy as np

SOURCES = ((20, 22, 30.0), (35, 40, 50.0), (44, 18, 20.0))
SKY, BORDER, OFFSET = 0.1, 4, 8  # the example reconstructs the central 48 x 48 (rows 8-55) plus a 4-pixel border


def checkout() -> Path:
    import os
    import cuphoton
    return Path(os.environ.get("CUPHOTON_REPO") or Path(cuphoton.__file__).resolve().parents[2])


def make(d: Path) -> None:
    from scipy.signal import convolve2d
    from cuphoton.ximage import load_ximage_bundle, summarize_bundle, validate_bundle

    scene = np.full((64, 64), SKY)
    for r, c, f in SOURCES:
        scene[r, c] = f
    y, x = np.indices((9, 9)) - 4
    rng = np.random.default_rng(0)
    psfs = np.empty((9, 9, 1, 3))
    images = np.empty((1, 64, 64, 3))
    for k, sigma in enumerate((0.8, 1.0, 1.2)):
        psf = np.exp(-(x**2 + y**2) / (2 * sigma**2))
        psfs[:, :, 0, k] = psf / psf.sum()
        images[0, :, :, k] = convolve2d(scene, psfs[:, :, 0, k], mode="same") + rng.normal(0, 0.01, scene.shape)
    d.mkdir(parents=True, exist_ok=True)
    np.save(d / "images.npy", images)
    np.save(d / "variances.npy", np.full_like(images, 0.01**2))
    np.save(d / "psfs.npy", psfs)
    with load_ximage_bundle(d) as bundle:
        print("issues:", validate_bundle(bundle))
        for key, info in summarize_bundle(bundle).items():
            print(f"{key:9s} {info['shape']} {info['axes']}")


def run(d: Path, runs: Path, name: str, max_iter: int | None) -> None:
    import yaml
    from cuphoton.ximage.evaluation import evaluate_reconstruction_run
    from cuphoton.ximage.workflows import run_reconstruction

    config = yaml.safe_load((checkout() / "examples/ximage/reconstruct-l2.example.yaml").read_text())
    config["data"]["base"] = str(d)
    config["output"] = {"root_dir": str(runs), "name": name, "overwrite": True}
    if max_iter:
        config["max_iter"] = max_iter
    cfg = runs / f"{name}.yaml"
    runs.mkdir(parents=True, exist_ok=True)
    cfg.write_text(yaml.safe_dump(config, sort_keys=False))
    result = run_reconstruction(cfg)
    s = result.summary
    tr = s["trace_summary"]
    print(f"run {result.run_dir}")
    print(f"backend {s['backend']}, device {s['performance']['device']['device']} "
          f"({s['performance']['device'].get('device_name', '')}), dtype {s['dtype']}, saved image {s['image_shape']}")
    print(f"iterations {tr['iterations_count']} (max_iter {config['max_iter']}), loss {tr['loss_last']:.2f}, "
          f"u_score {tr['u_score_last']:.1e} (stop_tol {config['stop_tol']:g})")
    img = np.load(s["saved"]["image"])[0, :, :, 0]
    o = OFFSET - BORDER
    for r, c, f in SOURCES:
        box = img[r - o - 4:r - o + 5, c - o - 4:c - o + 5]
        print(f"source at ({r}, {c}): planted {f:.0f}, peak pixel {img[r - o, c - o]:.1f}, "
              f"flux in 9 x 9 box minus sky {(box - SKY).sum():.1f}")
    ev = evaluate_reconstruction_run(result.run_dir, metrics_backend="auto")
    for key in ("restoration", "synthetic_coadd"):
        print(key, {k: round(v, 3) for k, v in ev[key].items() if isinstance(v, float)})


def figure(d: Path, run: Path, png: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    images = np.load(d / "images.npy")
    scene = np.load(run / "artifacts/image.npy")[0, BORDER:-BORDER, BORDER:-BORDER, 0]
    sl = slice(OFFSET, 64 - OFFSET)
    panels = [(images[0, sl, sl, 2], "one frame (PSF 1.2 px)"), (np.median(images[0, sl, sl], axis=-1), "median of the 3 frames"),
              (scene, f"xImage ({run.name})")]
    fig, axes = plt.subplots(1, 3, figsize=(9, 3.3))
    norm = LogNorm(vmin=0.05, vmax=max(p.max() for p, _ in panels))
    for ax, (p, title) in zip(axes, panels):
        im = ax.imshow(np.clip(p, 0.05, None), origin="lower", cmap="magma", norm=norm)
        ax.set_title(title, fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=axes, shrink=0.8, label="intensity (log)")
    fig.text(0.99, 0.1, "synthetic data (the user guide's example)", ha="right", fontsize=7, style="italic", color="0.4")
    fig.savefig(png, dpi=130, bbox_inches="tight")
    print("wrote", png)


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 3 and a[1] == "make":
        make(Path(a[2]))
    elif len(a) >= 5 and a[1] == "run":
        run(Path(a[2]), Path(a[3]), a[4], int(a[5]) if len(a) > 5 else None)
    elif len(a) >= 5 and a[1] == "figure":
        figure(Path(a[2]), Path(a[3]), a[4])
    else:
        sys.exit(__doc__)
