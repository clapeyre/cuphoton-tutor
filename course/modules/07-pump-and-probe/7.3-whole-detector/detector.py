"""7.3: a whole detector of laser-on/laser-off frames, fitted row by row with xRay on the GPU.
The answer is in this file: run it in place, don't copy it.

    python detector.py make DIR             write DIR/on.h5 and DIR/off.h5: 97 frames of a 256-row x 128-column
                                            detector, 0.1 ps apart (25 MB)
    python detector.py look RUN DIR PNG     read a detector-artifacts output folder RUN (made from DIR): the
                                            manifest's counts, fit_status, and per row the counts recorded,
                                            the strongest oscillating mode's frequency and
                                            amplitude

The crystal (don't tell before they've looked): one mode whose frequency depends on the detector row,
0.25 THz at the edges rising to 1.0 THz mid-detector (each row sees a different momentum: a dispersion
curve), change 0.03, decay 0.12 per ps, plus a 0.8% step. Rows 120-123 are dead: they record 0 counts in
every frame, laser on and off.
"""
import json
import sys
from pathlib import Path

import numpy as np

H, W, F = 256, 128, 97
DEAD = (120, 124)


def truth():
    return 0.25 + 0.75 * np.sin(np.pi * np.arange(H) / (H - 1))


def make(out: Path) -> None:
    import h5py

    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    delay = (np.arange(F) - 1) * 0.1
    t = np.clip(delay, 0, None)[:, None]
    change = 0.03 * np.exp(-0.12 * t) * np.cos(2 * np.pi * truth()[None, :] * t + 0.2) + 0.008  # (frame, row)
    for name, fac in (("on", 1 + change), ("off", np.ones((F, H)))):
        i0 = 1e4 * (1 + 0.03 * rng.standard_normal(F))
        img = rng.poisson(2e3 * (i0 / 1e4)[:, None, None] * fac[:, :, None] * np.ones((1, 1, W))).astype(np.float32)
        img[:, DEAD[0]:DEAD[1], :] = 0
        with h5py.File(out / f"{name}.h5", "w") as h:
            h["imgs"] = img
            h["scan_var"] = delay
            h["i0"] = i0
            h["i0_ipm3"] = i0
            h["bin_count"] = np.full(F, 50)
            h["ROI"] = np.array([0, 0, W, H])
    print(f"wrote {out}/on.h5 and off.h5: {F} frames of {H} rows x {W} columns, delays {delay[0]:.1f} to {delay[-1]:.1f} ps")


def look(run: Path, data: Path, png: str) -> None:
    import h5py
    from cuphoton.xray.detector_storage import load_detector_array

    m = json.loads((run / "manifest.json").read_text())
    print("manifest:", ", ".join(f"{k} {m.get(k)}" for k in ("backend", "device", "components", "exclude_y", "raw_fits",
                                                             "failures", "skipped_fits", "elapsed_s")))
    status = np.load(run / "fit_status.npy")
    names = {0: "not processed", 1: "fitted", 2: "skipped", 3: "failed"}
    print("fit_status:", ", ".join(f"{names[int(k)]} {n}" for k, n in zip(*np.unique(status, return_counts=True))))
    x = 8  # one column; every column of a tile row holds the same fit
    freq = load_detector_array(str(run / "freq_all.npy"))[:, x, :]
    amp = load_detector_array(str(run / "amp_all.npy"))[:, x, :]
    nmodes = (amp > 0).sum(1)
    print("modes per row:", ", ".join(f"{k}: {n} rows" for k, n in zip(*np.unique(nmodes, return_counts=True))))
    best = np.argmax(np.where(freq > 0.05, amp, 0), axis=1)  # leave out the 0 THz entry: the constant step
    f1 = freq[np.arange(H), best]
    a1 = amp[np.arange(H), best]
    with h5py.File(data / "off.h5") as h:
        counts = np.asarray(h["imgs"][:, :, :]).mean(axis=(0, 2))
    ok = status[:, x] == 1
    print(f"strongest oscillating mode vs the planted frequency, fitted rows: median |error| {np.median(np.abs(f1 - truth())[ok]):.3f} THz")
    print("row  laser-off counts  status  frequency (THz)  amplitude")
    for y in list(range(114, 130)):
        print(f"{y:3d}  {counts[y]:16.0f}  {names[int(status[y, x])]:>7s}  {f1[y]:15.3f}  {a1[y]:9.4f}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = np.arange(H)
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4), sharex=True)
    axs[0].plot(rows, counts, color="0.3", lw=1)
    axs[0].set_ylabel("laser-off counts per pixel"); axs[0].set_title("what each row recorded", fontsize=9)
    fitted = status[:, x] == 1
    axs[1].plot(rows, truth(), "--", color="0.6", lw=1, label="planted")
    axs[1].plot(rows[fitted], f1[fitted], ".", color="#2A78D6", ms=2.5, label="fitted (status 1)")
    axs[1].set_ylabel("frequency (THz)"); axs[1].set_title("strongest oscillating mode", fontsize=9); axs[1].legend(frameon=False, fontsize=8)
    axs[2].plot(rows[fitted], a1[fitted], ".", color="#2A78D6", ms=2.5)
    axs[2].set_ylabel("amplitude"); axs[2].set_title("its amplitude", fontsize=9)
    for ax in axs:
        ax.set_xlabel("detector row")
    fig.text(0.995, 0.01, f"synthetic data · {run.name} · column {x}", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "make":
        make(Path(sys.argv[2]))
    elif len(sys.argv) >= 5 and sys.argv[1] == "look":
        look(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
    else:
        sys.exit(__doc__)
