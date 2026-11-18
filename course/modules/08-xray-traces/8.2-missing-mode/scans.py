"""8.2: three scans of one crystal from "the beamline". Each is a laser-on/laser-off pair like 8.1's.
The answer is in this file: run it in place, don't copy it.

    python scans.py make DIR        write DIR/scan-a, DIR/scan-b, DIR/scan-c (on.h5 and off.h5 each)
    python scans.py fit PNG SCAN [SCAN ...]
                                    per scan: extract the 16 x 16 tile trace, sweep orders 1-12, fit at the
                                    chosen order, print the modes and the residual; draw one row per scan:
                                    trace and fit, the residual, and the residual's spectrum

The scans (don't tell the learner before they've judged the fits):
  scan-a  0.1 ps steps, 97 frames, like 8.1, but the crystal has three modes: 8.1's two and a third at
          2.0 THz, as strong as the second (change 0.02, decay 0.1 per ps).
  scan-b  the same crystal, uneven steps: 0.05 ps up to 2 ps, then 0.13 ps, to 9.3 ps (97 frames).
  scan-c  the same crystal, 0.05 ps steps over the same 9.6 ps (193 frames).
"""
import sys
from pathlib import Path

import numpy as np

MODES = ((0.04, 0.15, 2.0, 0.3), (0.02, 0.08, 4.5, -0.75), (0.02, 0.10, 2 * np.pi * 2.0, 0.0))  # change, decay /ps, rad/ps, phase


def delays(scan):
    if scan == "scan-a":
        return (np.arange(97) - 1) * 0.1
    if scan == "scan-b":
        return np.concatenate([[-0.05], np.arange(41) * 0.05, 2.0 + np.arange(1, 56) * 0.13])
    return (np.arange(193) - 1) * 0.05


def make(out: Path) -> None:
    import h5py

    rng = np.random.default_rng(11)
    for scan in ("scan-a", "scan-b", "scan-c"):
        delay = delays(scan)
        t = np.clip(delay, 0.0, None)
        change = 0.01 + sum(a * np.exp(-g * t) * np.cos(w * t + p) for a, g, w, p in MODES)
        d = out / scan
        d.mkdir(parents=True, exist_ok=True)
        for name, factor in (("on", 1.0 + change), ("off", np.ones(delay.size))):
            i0 = 1.0e4 * (1.0 + 0.03 * rng.standard_normal(delay.size))
            counts = 5.0e4 * (i0 / 1.0e4 * factor)[:, None, None] * np.ones((32, 32))
            with h5py.File(d / f"{name}.h5", "w") as h5:
                h5["imgs"] = rng.poisson(counts).astype(np.float32)
                h5["scan_var"] = delay
                h5["i0"] = i0
                h5["i0_ipm3"] = i0
                h5["bin_count"] = np.full(delay.size, 50)
                h5["ROI"] = np.array([0, 0, 32, 32])
        print(f"wrote {d}/on.h5 and off.h5: {delay.size} frames of 32 x 32, delays {delay[0]:.2f} to {delay[-1]:.2f} ps")


def fit(png: str, scans: list) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(scans), 3, figsize=(11, 3.2 * len(scans)), squeeze=False)
    for row, scan in zip(axes, scans):
        fit_one(Path(scan), *row)
    fig.text(0.995, 0.005, "synthetic data", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)


def fit_one(scan: Path, ax, axr, axf) -> None:
    from cuphoton.xray.hdf5 import load_hdf5_pair_roi_trace
    from cuphoton.xray.linear_prediction import linear_prediction_numpy, model_order_sweep

    tr = load_hdf5_pair_roi_trace(h5dir=str(scan), fon="on.h5", foff="off.h5", roi_x=0, roi_y=0, roi_width=16, roi_height=16)
    delay, trace = tr.delay, tr.ratio_minus_one
    print(f"{scan.name}: {delay.size} samples, delay {delay[0]:.2f} to {delay[-1]:.2f} ps")
    sweep = model_order_sweep(delay, trace, tuple(range(1, 13)))
    print("model order sweep (RMS residual):  " + "  ".join(f"{e.components}: {e.rms_residual:.1e}" for e in sweep.entries))
    print("chosen order:", sweep.best_components)
    f = linear_prediction_numpy(delay, trace, sweep.best_components)
    for w, g, a in zip(f.angular_frequency, f.decay, f.amplitude):
        print(f"  mode: {w / (2 * np.pi):.3f} THz, decay {g:.3f} per ps, amplitude {a:.4f}")
    n = len(f.reconstruction)
    resid = trace[:n] - f.reconstruction
    print(f"residual RMS {np.sqrt(np.mean(resid ** 2)):.1e}")
    ax.plot(delay, trace, ".", color="0.5", ms=3, label="trace")
    ax.plot(delay[:n], f.reconstruction, color="#2A78D6", lw=1.2, label=f"fit, order {sweep.best_components}")
    ax.set_xlabel("delay (ps)"); ax.set_ylabel("trace"); ax.legend(frameon=False, fontsize=8)
    ax.set_title(scan.name, fontsize=9)
    axr.plot(delay[:n], resid, ".", color="#B5402A", ms=3)
    axr.axhline(0, color="0.6", lw=0.8)
    axr.set_xlabel("delay (ps)"); axr.set_ylabel("trace − fit"); axr.set_title("residual", fontsize=9)
    step = np.median(np.diff(delay[:n]))
    spec = np.abs(np.fft.rfft(resid - resid.mean()))
    axf.plot(np.fft.rfftfreq(n, step), spec, color="#B5402A", lw=1.2)
    axf.set_xlabel(f"frequency (THz), if steps were even ({step:.2f} ps)"); axf.set_ylabel("|FFT| of residual")
    axf.set_title("residual spectrum", fontsize=9)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "make":
        make(Path(sys.argv[2]))
    elif len(sys.argv) >= 4 and sys.argv[1] == "fit":
        fit(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
