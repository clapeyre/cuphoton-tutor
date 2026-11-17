"""6.1: two signals with a known delay, correlated with xBeam on the GPU.

    python delays.py known <out.png>
        The guide's sample pair (8,192 samples at 1,024 Hz; b is a copy of a, 7 samples late, plus noise
        of half a's size), and the same with a delay of 7.4 samples. Prints, per pair, the lag of the
        correlation peak and the delay read from the phase slope of the averaged cross-spectrum, and
        the pair swapped. Figure: lag correlation and unwrapped phase, as in the guide.
    python delays.py hidden
        Two pairs with delays the learner isn't told, each correlated with 1,024-sample windows in
        linear and circular lag mode, two windows per result. Prints each result's peak lag and how
        far the peak stands above the median |correlation| (peak/median).

Run it from the course folder (the hidden delays are in this file). GPU environment.
"""
import sys

import cupy as cp
import numpy as np
from cuphoton.xbeam import ArraySource, CorrelationSpec, correlate_series

FS, N = 1024.0, 8192


def pair(delay, seed=2026):
    """a, and b = a delayed by `delay` samples (a true shift, not a wrap) plus noise of half a's size."""
    rng = np.random.default_rng(seed)
    x = rng.normal(size=N + 4096)
    f = np.fft.rfftfreq(x.size)
    shifted = np.fft.irfft(np.fft.rfft(x) * np.exp(-2j * np.pi * f * delay), x.size)
    a, b = x[2048:2048 + N], shifted[2048:2048 + N] + 0.5 * rng.normal(size=N)
    return a.astype(np.float32), b.astype(np.float32)


def correlate(a, b, window, per_result, mode="linear", pairs=(("a", "b"),)):
    source = ArraySource({"a": cp.asarray(a), "b": cp.asarray(b)}, sample_rate_hz=FS)
    spec = CorrelationSpec(pairs=pairs, window_samples=window, windows_per_result=per_result, output="both",
                           lag_mode=mode, backend="cupy")
    return list(correlate_series(source, spec))


def readings(results):
    r = results[0]
    peak = int(r.lag_samples[np.argmax(np.abs(r.lag[0]))])
    spectrum = np.mean([x.spectrum[0] for x in results], axis=0)
    freq = r.frequencies_hz
    pos = freq > 0
    phase = np.unwrap(np.angle(spectrum[pos]))
    slope = np.polyfit(freq[pos], phase, 1)[0] / (2 * np.pi) * FS
    return peak, slope, freq[pos], phase


step = sys.argv[1]
if step == "known":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(7.5, 5))
    for row, d in enumerate([7, 7.4]):
        res = correlate(*pair(d), 1024, 4)
        peak, slope, freq, phase = readings(res)
        swapped = readings(correlate(*pair(d), 1024, 4, pairs=(("b", "a"),)))
        print(f"b {d} samples late: {len(res)} results; lag peak {peak:+d}, phase slope {slope:+.2f} samples; "
              f"pair (b, a): lag peak {swapped[0]:+d}, phase slope {swapped[1]:+.2f}")
        r = res[0]
        near = np.abs(r.lag_samples) <= 20
        ax[row, 0].bar(r.lag_samples[near], r.lag[0, near].real, width=0.8, color="#2A78D6")
        ax[row, 0].set_ylabel(f"delay {d}: correlation")
        ax[row, 1].plot(freq, phase / (2 * np.pi), color="#2A78D6", lw=0.8)
        ax[row, 1].plot(freq, np.polyval(np.polyfit(freq, phase, 1), freq) / (2 * np.pi), "--", color="#EB6834")
        ax[row, 1].set_ylabel("phase (turns)")
    ax[1, 0].set_xlabel("lag (samples)")
    ax[1, 1].set_xlabel("frequency (Hz)")
    fig.text(0.99, 0.005, "Synthetic signals, made like the guide's sample pair", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(sys.argv[2], dpi=110)
    print("wrote", sys.argv[2])
elif step == "hidden":
    for name, d in [("pair 1", 900), ("pair 2", 1500)]:
        for mode in ["linear", "circular"]:
            out = []
            for r in correlate(*pair(d), 1024, 2, mode):
                m = np.abs(r.lag[0])
                out.append(f"peak at lag {int(r.lag_samples[np.argmax(m)]):+5d} (peak/median {m.max() / np.median(m):5.1f})")
            print(f"{name}, {mode:8s}: " + ";  ".join(out))
    ref = [np.abs(r.lag[0]).max() / np.median(np.abs(r.lag[0])) for m in ["linear", "circular"] for r in correlate(*pair(7), 1024, 2, m)]
    print(f"For comparison, the 7-sample pair in the same setup: peak/median {min(ref):.0f} to {max(ref):.0f}.")
