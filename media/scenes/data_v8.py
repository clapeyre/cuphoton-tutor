"""Data for v8 (pump and probe): the user guide's xRay sample pair reduced to a trace and fitted by linear
prediction (each mode's own curve too), and a small detector whose rows ring at different frequencies,
fitted row by row on the CPU. Writes v8.npz to the output dir (argv[1], default .)."""
import sys
import tempfile
from pathlib import Path

import h5py
import numpy as np

from cuphoton.xray.hdf5 import load_hdf5_pair_roi_trace
from cuphoton.xray.linear_prediction import linear_prediction_numpy, model_order_sweep

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
tmp = Path(tempfile.mkdtemp())

# the guide's sample pair (docs/guide/xray-traces.qmd, "Make a sample pair")
rng = np.random.default_rng(5)
frames, height, width = 97, 32, 32
delay = (np.arange(frames) - 1) * 0.1
t = np.clip(delay, 0.0, None)
change = (0.04 * np.exp(-0.15 * t) * np.cos(2.0 * t + 0.3) + 0.02 * np.exp(-0.08 * t) * np.cos(4.5 * t - 0.75) + 0.01)
on_sum, off_sum = [], []
for name, factor in (("on", 1.0 + change), ("off", np.ones(frames))):
    i0 = 1.0e4 * (1.0 + 0.03 * rng.standard_normal(frames))
    counts = 5.0e4 * (i0 / 1.0e4 * factor)[:, None, None] * np.ones((height, width))
    with h5py.File(tmp / f"{name}.h5", "w") as h5:
        h5["imgs"] = rng.poisson(counts).astype(np.float32)
        h5["scan_var"] = delay
        h5["i0"] = i0
        h5["i0_ipm3"] = i0
        h5["bin_count"] = np.full(frames, 50)
        h5["ROI"] = np.array([0, 0, width, height])
        (on_sum if name == "on" else off_sum).append(np.asarray(h5["imgs"][1:, :16, :16]).sum(axis=(1, 2)) / i0[1:])
tr = load_hdf5_pair_roi_trace(h5dir=str(tmp), fon="on.h5", foff="off.h5", roi_x=0, roi_y=0, roi_width=16, roi_height=16)
d, y = tr.delay, tr.ratio_minus_one
sweep = model_order_sweep(d, y, tuple(range(1, 10)))
fit = linear_prediction_numpy(d, y, sweep.best_components)
order = np.argsort(fit.angular_frequency)
modes = np.array([a * np.exp(-g * fit.time) * np.cos(w * fit.time + p) for w, g, a, p in
                  zip(fit.angular_frequency[order], fit.decay[order], fit.amplitude[order], fit.phase[order])])
print("order", sweep.best_components, "modes (THz):", np.round(fit.angular_frequency[order] / 2 / np.pi, 3))

# a small detector: 64 rows, each ringing at its own frequency (a dispersion curve), fitted per row
rows = 64
f_row = 0.25 + 0.75 * np.sin(np.pi * np.arange(rows) / (rows - 1))
dd = np.arange(96) * 0.1
fitted = []
for f in f_row:
    yy = 0.015 * np.exp(-0.12 * dd) * np.cos(2 * np.pi * f * dd + 0.2) + 0.004 + rng.normal(0, 2e-4, dd.size)
    r = linear_prediction_numpy(dd, yy, 3)
    f_hz = np.abs(r.angular_frequency) / 2 / np.pi
    amp = np.where(f_hz > 0.05, np.abs(r.amplitude), 0)
    fitted.append(float(f_hz[np.argmax(amp)]) if amp.size else np.nan)
np.savez(out / "v8.npz", delay=d, trace=y, fit_time=fit.time + d[0], recon=fit.reconstruction, modes=modes,
         thz=fit.angular_frequency[order] / 2 / np.pi, on=on_sum[0], off=off_sum[0],
         f_row=f_row, f_fit=np.array(fitted))
print("detector rows: median |fit - planted|", np.median(np.abs(np.array(fitted) - f_row)).round(4), "THz")
print("wrote", out / "v8.npz")
