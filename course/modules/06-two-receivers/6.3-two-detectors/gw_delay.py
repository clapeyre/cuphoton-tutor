"""6.3: GW150914 in the two LIGO detectors. When did the wave reach each, and is the peak real?

    python gw_delay.py look <out.png>
        The strain around the event in Hanford (H1) and Livingston (L1), and what frequencies it holds.
    python gw_delay.py correlate raw|whitened
        Correlate H1 with L1 (pair (H1, L1): a positive lag means L1 heard it later) over the quarter
        second centred on the event, with xBeam on the GPU. Prints the peak over all lags and within
        the light-travel time between the sites (10 ms), and the normalized correlation there.
    python gw_delay.py background raw|whitened <out.png>
        The same correlation in every quarter second of the 32 s, normalized by the two
        autocorrelations; the strongest peak within 10 ms in each. Compares the event's quarter second
        with all those more than 2 s away from it (the background). Figure: the event's correlation
        against lag, and the background's peaks.

"whitened": each detector's strain divided, frequency by frequency, by its own noise level (measured
over the 32 s), keeping 35-350 Hz. Env DATA: folder with the two GWOSC files (default ./data if it
holds them, else the course's data/ next to this lesson). GPU environment.
"""
import os
import pathlib
import sys

import cupy as cp
import h5py
import numpy as np
from scipy.signal import welch
from cuphoton.xbeam import ArraySource, CorrelationSpec, correlate_series

here = pathlib.Path(__file__).resolve().parent
D = pathlib.Path(os.environ.get("DATA") or ("data" if pathlib.Path("data/H-H1_LOSC_4_V2-1126259446-32.hdf5").exists() else here.parent / "data"))
FS, GPS0, EVENT_GPS = 4096, 1126259446, 1126259462.4
EV = int((EVENT_GPS - GPS0) * FS)          # sample of the event (16.4 s into the files)
W, MAXLAG = 1024, 41                        # a quarter second; 10 ms = 41 samples
strain = {d: h5py.File(D / f"{d[0]}-{d}_LOSC_4_V2-1126259446-32.hdf5")["strain/Strain"][:] for d in ("H1", "L1")}


def whiten(x, lo=35, hi=350):
    f, psd = welch(x, FS, nperseg=4 * FS)
    X = np.fft.rfft(x * np.hanning(x.size))
    ff = np.fft.rfftfreq(x.size, 1 / FS)
    Xw = X / np.sqrt(np.interp(ff, f, psd))
    Xw[(ff < lo) | (ff > hi)] = 0
    return np.fft.irfft(Xw, x.size)


def series(kind):
    return {d: (whiten(x) if kind == "whitened" else x) for d, x in strain.items()}   # float64 throughout


def correlate(s, start=None, normalize=False):
    sl = slice(start, start + W) if start is not None else slice(None)
    src = ArraySource({d: cp.asarray(x[sl]) for d, x in s.items()}, sample_rate_hz=FS)
    pairs = (("H1", "L1"), ("H1", "H1"), ("L1", "L1")) if normalize else (("H1", "L1"),)
    for r in correlate_series(src, CorrelationSpec(pairs=pairs, window_samples=W, windows_per_result=1,
                                                   output="lag", backend="cupy")):
        lag = r.lag[0].real
        if normalize:
            zero = r.lag_samples == 0
            lag = lag / np.sqrt(r.lag[1][zero].real * r.lag[2][zero].real)
        yield r.sample_start, r.lag_samples, lag


def peak(lags, c, maxlag=None):
    sel = np.ones(lags.size, bool) if maxlag is None else np.abs(lags) <= maxlag
    i = np.argmax(np.abs(c[sel]))
    return int(lags[sel][i]), float(c[sel][i])


step = sys.argv[1]
if step == "look":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
    t = (np.arange(-FS // 4, FS // 8) + EV)
    for d, c in (("H1", "#2A78D6"), ("L1", "#EB6834")):
        x = strain[d]
        ax[0].plot((t - EV) / FS, x[t] * 1e19, color=c, lw=0.8, label=d)
        ax[1].plot((t - EV) / FS, whiten(x)[t], color=c, lw=0.8, label=d)
        f, psd = welch(x, FS, nperseg=4 * FS)
        ax[2].loglog(f[1:], np.sqrt(psd[1:]), color=c, lw=0.8, label=d)
    ax[0].set_ylabel("strain (×10⁻¹⁹)")
    ax[0].set_xlabel("seconds from the event")
    ax[1].set_ylabel("whitened, 35–350 Hz")
    ax[1].set_xlabel("seconds from the event")
    ax[2].axvspan(35, 350, color="0.85")
    ax[2].set_xlabel("frequency (Hz)")
    ax[2].set_ylabel("noise level (strain/√Hz)")
    ax[2].set_title("grey: the band the wave is in", fontsize=9)
    ax[0].legend(fontsize=8)
    fig.text(0.99, 0.005, "LIGO strain data for GW150914, from GWOSC (gwosc.org)", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(sys.argv[2], dpi=110)
    print("wrote", sys.argv[2])
elif step == "correlate":
    kind = sys.argv[2]
    _, lags, c = next(correlate(series(kind), EV - W // 2))
    k, _ = peak(lags, c)
    k10, v10 = peak(lags, c, MAXLAG)
    print(f"{kind}: peak over all lags at {k:+d} samples ({1e3 * k / FS:+.2f} ms); "
          f"within ±10 ms at {k10:+d} samples ({1e3 * k10 / FS:+.2f} ms), correlation {'positive' if v10 > 0 else 'negative'}")
elif step == "background":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    kind = sys.argv[2]
    s = series(kind)
    found = [(st, *peak(l, c, MAXLAG)) for st, l, c in correlate(s, normalize=True)]
    on = next(f for f in found if f[0] <= EV < f[0] + W)
    off = np.array([abs(f[2]) for f in found if abs(f[0] + W / 2 - EV) > 2 * FS])
    louder = int((off >= abs(on[2])).sum())
    print(f"{kind}: event's quarter second: peak at {on[1]:+d} samples ({1e3 * on[1] / FS:+.2f} ms), rho {on[2]:+.2f}. "
          f"Background: {off.size} quarter seconds, median |rho| {np.median(off):.2f}, loudest {off.max():.2f}; "
          f"{louder} as loud as the event or louder.")
    _, lags, c = next(correlate(s, EV - W // 2, normalize=True))
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    near = np.abs(lags) <= 3 * MAXLAG
    ax[0].plot(1e3 * lags[near] / FS, c[near], color="#2A78D6", lw=1)
    ax[0].axvspan(-10, 10, color="0.9")
    ax[0].set_xlabel("lag of L1 behind H1 (ms); grey: ±10 ms")
    ax[0].set_ylabel("normalized correlation")
    ax[0].set_title(f"{kind}: the quarter second around the event", fontsize=9)
    ax[1].hist(off, bins=20, color="0.6")
    ax[1].axvline(abs(on[2]), color="#EB6834", lw=2)
    ax[1].set_xlabel("strongest |correlation| within ±10 ms")
    ax[1].set_ylabel("quarter seconds")
    ax[1].set_title(f"background ({off.size}), and the event (orange)", fontsize=9)
    fig.text(0.99, 0.005, "LIGO strain data for GW150914, from GWOSC (gwosc.org)", ha="right", fontsize=7, style="italic", color="0.4")
    fig.tight_layout()
    fig.savefig(sys.argv[3], dpi=110)
    print("wrote", sys.argv[3])
