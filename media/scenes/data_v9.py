"""Data for v9 (many frames, one scene): a bundle like the user guide's, but not its scene (8.1 asks the
learner to predict that one): three frames of a close pair of sources and a third, each frame with its own
Gaussian PSF (1.2, 1.6, 2.0 px, wide enough to blend the pair), reconstructed with the checkout's L2 example stopped after 1, 3, 10, 30 and 75
steps, and the loss per step. Writes v9.npz to the output dir (argv[1], default .)."""
import sys
import tempfile
from pathlib import Path

import numpy as np
import yaml
from scipy.signal import convolve2d

import cuphoton
from cuphoton.ximage.workflows import run_reconstruction

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
repo = Path(cuphoton.__file__).resolve().parents[2]
tmp = Path(tempfile.mkdtemp())
scene = np.full((64, 64), 0.1)
scene[30, 29], scene[31, 33], scene[44, 18] = 40.0, 25.0, 20.0
y, x = np.indices((9, 9)) - 4
rng = np.random.default_rng(0)
psfs = np.empty((9, 9, 1, 3)); images = np.empty((1, 64, 64, 3))
for k, sigma in enumerate((1.2, 1.6, 2.0)):
    psf = np.exp(-(x**2 + y**2) / (2 * sigma**2)); psfs[:, :, 0, k] = psf / psf.sum()
    images[0, :, :, k] = convolve2d(scene, psfs[:, :, 0, k], mode="same") + rng.normal(0, 0.01, scene.shape)
b = tmp / "bundle"; b.mkdir()
np.save(b / "images.npy", images); np.save(b / "variances.npy", np.full_like(images, 0.01**2)); np.save(b / "psfs.npy", psfs)
base = yaml.safe_load((repo / "examples/ximage/reconstruct-l2.example.yaml").read_text())
snaps, steps = [], (1, 3, 10, 30, 75)
for n in steps:
    c = dict(base); c["data"] = {"base": str(b)}; c["max_iter"] = n; c["device"] = "cpu"
    c["output"] = {"root_dir": str(tmp / "runs"), "name": f"it{n}", "overwrite": True}
    p = tmp / f"it{n}.yaml"; p.write_text(yaml.safe_dump(c, sort_keys=False))
    r = run_reconstruction(p)
    snaps.append(np.load(r.summary["saved"]["image"])[0, 4:-4, 4:-4, 0])
    loss = np.load(r.run_dir / "trace/loss.npy")
    print(n, "steps: loss", round(float(loss[-1]), 2), "peak", round(float(snaps[-1].max()), 1))
sl = slice(8, 56)
np.savez(out / "v9.npz", frames=images[0, sl, sl, :], median=np.median(images[0, sl, sl, :], axis=-1),
         psfs=psfs[:, :, 0, :], snaps=np.array(snaps), steps=np.array(steps), loss=loss, truth=scene[sl, sl])
print("wrote", out / "v9.npz")
