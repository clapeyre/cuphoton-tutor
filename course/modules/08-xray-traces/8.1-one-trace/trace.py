"""8.1: one laser-on/laser-off pair, reduced to a trace and fitted with xRay's linear prediction.

    python trace.py make DIR            write the user guide's sample pair: DIR/on.h5, DIR/off.h5
    python trace.py fit DIR PNG [--no-shift]
                                        probe the pair, extract one 16 x 16 tile's trace, sweep the model
                                        order, fit, print each mode, and draw trace, fit, residual, spectrum

The pair is the guide's ("Analyze X-ray detector traces"): 97 delay frames of a 32 x 32 detector, 0.1 ps
apart; the laser-on frames change by two damped oscillations and a constant, on top of Poisson counts.
CPU only (NumPy, h5py); the GPU comes in 8.3.
"""
import sys
from pathlib import Path

import numpy as np


def make(out: Path) -> None:
    import h5py

    rng = np.random.default_rng(5)
    frames, height, width = 97, 32, 32
    delay = (np.arange(frames) - 1) * 0.1  # ps; xRay drops frame 0 by default
    t = np.clip(delay, 0.0, None)
    change = (0.04 * np.exp(-0.15 * t) * np.cos(2.0 * t + 0.3)
              + 0.02 * np.exp(-0.08 * t) * np.cos(4.5 * t - 0.75) + 0.01)
    out.mkdir(parents=True, exist_ok=True)
    for name, factor in (("on", 1.0 + change), ("off", np.ones(frames))):
        i0 = 1.0e4 * (1.0 + 0.03 * rng.standard_normal(frames))  # incident-beam monitor
        counts = 5.0e4 * (i0 / 1.0e4 * factor)[:, None, None] * np.ones((height, width))
        with h5py.File(out / f"{name}.h5", "w") as h5:
            h5["imgs"] = rng.poisson(counts).astype(np.float32)
            h5["scan_var"] = delay
            h5["i0"] = i0
            h5["i0_ipm3"] = i0
            h5["bin_count"] = np.full(frames, 50)
            h5["ROI"] = np.array([0, 0, width, height])
    print(f"wrote {out}/on.h5 and {out}/off.h5: {frames} frames of {height} x {width}, delays "
          f"{delay[0]:.1f} to {delay[-1]:.1f} ps")


def fit(pair: Path, png: str, shift: bool) -> None:
    from cuphoton.xray.hdf5 import load_hdf5_pair_roi_trace, probe_hdf5_pair
    from cuphoton.xray.linear_prediction import linear_prediction_numpy, model_order_sweep

    probe = probe_hdf5_pair(h5dir=str(pair), fon="on.h5", foff="off.h5")
    for side in (probe.on, probe.off):
        print(f"{side.path.name}: layout {side.schema}, normalized by {side.load_plan.ipm_pair.normalization}")
    tr = load_hdf5_pair_roi_trace(h5dir=str(pair), fon="on.h5", foff="off.h5", roi_x=0, roi_y=0,
                                  roi_width=16, roi_height=16, reference_shift=shift)
    delay, trace = tr.delay, tr.ratio_minus_one
    print(f"trace: {delay.size} samples, delay {delay[0]:.1f} to {delay[-1]:.1f} ps, "
          f"reference_shift={shift}")
    sweep = model_order_sweep(delay, trace, tuple(range(1, 10)))
    print("model order sweep (RMS residual):  " + "  ".join(f"{e.components}: {e.rms_residual:.2e}" for e in sweep.entries))
    print("chosen order:", sweep.best_components)
    f = linear_prediction_numpy(delay, trace, sweep.best_components)
    for w, g, a in zip(f.angular_frequency, f.decay, f.amplitude):
        print(f"  mode: {w / (2 * np.pi):.3f} THz, decay {g:.3f} per ps, amplitude {a:.4f}")
    t = f.time + delay[0]
    model = np.interp(delay, t, f.reconstruction)
    resid = trace - model
    print(f"residual RMS {np.sqrt(np.mean(resid[:len(t)] ** 2)):.2e}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax, axr, axf) = plt.subplots(1, 3, figsize=(11, 3.2))
    ax.plot(delay, trace, ".", color="0.5", ms=3, label="trace")
    ax.plot(t, f.reconstruction, color="#2A78D6", lw=1.2, label=f"fit, order {sweep.best_components}")
    ax.set_xlabel("delay (ps)"); ax.set_ylabel("trace"); ax.legend(frameon=False, fontsize=8)
    axr.plot(t, resid[:len(t)], ".", color="#B5402A", ms=3)
    axr.axhline(0, color="0.6", lw=0.8)
    axr.set_xlabel("delay (ps)"); axr.set_ylabel("trace − fit"); axr.set_title("residual", fontsize=9)
    axf.plot(f.frequency, f.spectrum_total, color="#2A78D6", lw=1.2)
    axf.set_xlabel("frequency (THz)"); axf.set_ylabel("modal spectrum")
    fig.text(0.995, 0.01, "synthetic data (the user guide's sample pair)", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(png, dpi=130)
    print("wrote", png)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "make":
        make(Path(sys.argv[2]))
    elif len(sys.argv) >= 4 and sys.argv[1] == "fit":
        fit(Path(sys.argv[2]), sys.argv[3], shift="--no-shift" not in sys.argv)
    else:
        sys.exit(__doc__)
