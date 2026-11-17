"""6.2: read xBeam visibility runs (xbeam-v1 output folders) and show each baseline across the band.

    python visibilities.py <out.png> <run dir> [<run dir> ...]

For each run and baseline, averaged over the run's integrations: the weights, the correlation
amplitude per channel (|V| over the geometric mean of the two autocorrelations), the amplitude of
the band average (what an image made from the whole band would see), and the residual delay read
from the slope of the phase against frequency, as in 6.1. Figure: amplitude and phase across the
band (phase unwrapped, in turns: its slope is the residual delay), one column per run.
"""
import sys

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cuphoton.xbeam.adapters.radio.output import read_xbeam_v1

BW = 8e6
runs = sys.argv[2:]
fig, ax = plt.subplots(2, len(runs), figsize=(4.2 * len(runs), 5.2), squeeze=False, sharex=True)
turns = 1.0  # the phase axes share one scale, so a flat line looks flat
for col, run in enumerate(runs):
    recs = read_xbeam_v1(run)
    auto = {}
    for r in recs:
        if r.antenna_a == r.antenna_b:
            auto.setdefault(r.antenna_a, []).append(np.abs(r.spectrum))
    auto = {k: np.mean(v, 0) for k, v in auto.items()}
    print(f"{run}:")
    for pair in sorted({(r.antenna_a, r.antenna_b) for r in recs if r.antenna_a != r.antenna_b}):
        rs = [r for r in recs if (r.antenna_a, r.antenna_b) == pair]
        v = np.mean([r.spectrum for r in rs], 0)
        rho = v / np.sqrt(auto[pair[0]] * auto[pair[1]])
        freq = np.arange(len(v)) * BW / len(v)
        phase = np.unwrap(np.angle(rho))
        slope = np.polyfit(freq[1:], phase[1:], 1)[0] / (2 * np.pi)
        print(f"  {pair[0]}-{pair[1]}: {len(rs)} integrations, weights {min(r.weight for r in rs):.3f}-{max(r.weight for r in rs):.3f}, "
              f"amplitude per channel {np.median(np.abs(rho[1:])):.3f}, band-averaged {abs(rho[1:].mean()):.3f}, "
              f"residual delay {slope * 1e6:+.2f} us")
        ax[0, col].plot(freq / 1e6, np.abs(rho), lw=1, label=f"{pair[0]}–{pair[1]}")
        ax[1, col].plot(freq[1:] / 1e6, phase[1:] / (2 * np.pi), lw=1.2)
        turns = max(turns, np.abs(phase).max() / (2 * np.pi))
    ax[0, col].set_title(run, fontsize=10)
    ax[0, col].set_ylim(0, 0.25)
    ax[1, col].set_xlabel("frequency above 1.4 GHz (MHz)")
for a in ax[1]:
    a.set_ylim(-1.1 * turns, 1.1 * turns)
ax[0, 0].set_ylabel("correlation amplitude")
ax[1, 0].set_ylabel("phase, unwrapped (turns)")
ax[0, 0].legend(fontsize=8)
fig.text(0.99, 0.005, "Synthetic recordings made for this lesson", ha="right", fontsize=7, style="italic", color="0.4")
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=110)
print("wrote", sys.argv[1])
