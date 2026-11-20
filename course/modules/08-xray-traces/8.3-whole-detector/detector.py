"""8.3: a whole detector of laser-on/laser-off frames, fitted row by row with xRay on the GPU.
The answer is in this file: run it in place, don't copy it.

    python detector.py make DIR             write DIR/on.h5 and DIR/off.h5: 97 frames of a 256-row x 128-column
                                            detector, 0.1 ps apart (25 MB)
    python detector.py look RUN DIR PNG     read a detector-artifacts output folder RUN (made from DIR): the
                                            manifest's counts, fit_status, and per row the counts recorded,
                                            the strongest oscillating mode's frequency and
                                            amplitude
    python detector.py residuals RUN PNG    each fit's residual from RUN/fit_diagnostics.npz (needs
                                            --fit-diagnostics summary), against its detector row

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
    axs[1].set_ylabel("frequency (THz)"); axs[1].set_title("the dispersion curve: strongest mode per row", fontsize=9)
    axs[2].plot(rows[fitted], a1[fitted], ".", color="#2A78D6", ms=2.5)
    axs[2].set_ylabel("amplitude"); axs[2].set_title("its amplitude", fontsize=9)
    # Rows that weren't fitted are shaded and labelled, so a skipped band shows as one (its stored zeros aren't plotted).
    shade = {0: "#BBBBBB", 2: "#E8A33D", 3: "#D64545"}
    for code in (2, 3, 0):
        bad = np.flatnonzero(status[:, x] == code)
        if not bad.size:
            continue
        runs_ = np.split(bad, np.flatnonzero(np.diff(bad) > 1) + 1)
        span = ", ".join(f"{r[0]}" if r[0] == r[-1] else f"{r[0]}-{r[-1]}" for r in runs_[:4]) + (" ..." if len(runs_) > 4 else "")
        for ax in axs:
            for i, r in enumerate(runs_):
                ax.axvspan(r[0] - 0.5, r[-1] + 0.5, color=shade[code], alpha=0.35, lw=0,
                           label=f"{names[code]} (status {code}): rows {span}" if ax is axs[1] and i == 0 else None)
    axs[1].legend(frameon=False, fontsize=8)
    for ax in axs:
        ax.set_xlabel("detector row")
    fig.text(0.995, 0.01, f"synthetic data · {run.name} · column {x}", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)

def residuals(run: Path, png: str) -> None:
    d = np.load(run / "fit_diagnostics.npz")
    y, st = d["detector_y"], d["fit_status"]
    res, rel = d["residual_std"], d["relative_residual"]
    ok = st == 1
    print(f"fits: {len(y)}; residual std over fitted rows: median {np.median(res[ok]):.2e}, max {res[ok].max():.2e}")
    print(f"relative residual (residual std / trace std): median {np.median(rel[ok]):.2f}, max {rel[ok].max():.2f}")
    print("row  residual std (max over its 8 tiles)  relative residual")
    for r in range(114, 130):
        m = (y == r) & ok
        print(f"{r:3d}  {res[m].max() if m.any() else float('nan'):36.2e}  {rel[m].max() if m.any() else float('nan'):17.2f}")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2), sharex=True)
    axs[0].plot(y[ok], res[ok], ".", color="0.45", ms=2)
    axs[0].set_ylabel("residual std"); axs[0].set_title("what each fit left (one dot per fit)", fontsize=9)
    axs[1].plot(y[ok], rel[ok], ".", color="0.45", ms=2)
    axs[1].set_ylabel("residual std / trace std"); axs[1].set_title("the same, relative to the trace", fontsize=9)
    for ax in axs:
        ax.set_xlabel("detector row"); ax.set_ylim(bottom=0)
    fig.text(0.995, 0.01, f"synthetic data · {run.name} · fitted rows (status 1)", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "make":
        make(Path(sys.argv[2]))
    elif len(sys.argv) >= 5 and sys.argv[1] == "look":
        look(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) >= 4 and sys.argv[1] == "residuals":
        residuals(Path(sys.argv[2]), sys.argv[3])
    else:
        sys.exit(__doc__)
