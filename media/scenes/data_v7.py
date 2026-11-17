"""Data for v7 (two receivers, one signal): two synthetic recordings that share a faint signal, B
hearing it 23 samples after A, and their cross-correlation from xBeam (NumPy backend). Writes v7.npz
to the output dir (argv[1], default .)."""
import sys
from pathlib import Path

import numpy as np

from cuphoton.xbeam import ArraySource, CorrelationSpec, correlate_series

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
N, DELAY, SHARED = 4096, 23, 0.35   # samples; B's delay; fraction of each recording that is the source
rng = np.random.default_rng(13)
src = rng.normal(size=N + DELAY)
a = np.sqrt(SHARED) * src[DELAY:] + np.sqrt(1 - SHARED) * rng.normal(size=N)
b = np.sqrt(SHARED) * src[:N] + np.sqrt(1 - SHARED) * rng.normal(size=N)   # b[n] = source at a's n - DELAY
spec = CorrelationSpec(pairs=(("a", "b"), ("a", "a"), ("b", "b")), window_samples=1024, windows_per_result=4,
                       output="lag", backend="numpy")
r = next(correlate_series(ArraySource({"a": a, "b": b}, sample_rate_hz=1.0), spec))
zero = r.lag_samples == 0
rho = r.lag[0].real / np.sqrt(r.lag[1][zero].real * r.lag[2][zero].real)
near = np.abs(r.lag_samples) <= 60
peak = int(r.lag_samples[np.argmax(rho)])
print(f"xBeam: peak at lag {peak} (planted {DELAY}), normalized {rho.max():.2f}; off-peak |rho| median "
      f"{np.median(np.abs(rho[near & (r.lag_samples != peak)])):.3f}")
np.savez(out / "v7.npz", a=a.astype(np.float32), b=b.astype(np.float32), shared=src.astype(np.float32),
         lags=r.lag_samples[near], rho=rho[near], delay=DELAY, peak=peak)
print("wrote", out / "v7.npz")
