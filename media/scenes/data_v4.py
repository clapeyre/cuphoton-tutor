"""Data for v4 (where your data lives): real copy and compute times on this machine's GPU for a
2048 x 2048 float64 image (the 3.4 image): host -> device, xRep on the device, device -> host.
Synchronized, warm, median of 20. Needs the GPU environment (.envs/cuphoton-gpu). Writes v4.json."""
import json
import sys
import time
from pathlib import Path

import cupy as cp
import numpy as np
from cuphoton.xrep import BBox, ReprojectionSpec, reproject_array_device

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
N = 2048
image = np.random.default_rng(1).normal(100, 10, (N, N))
spec = ReprojectionSpec(mapping=lambda xy: xy + 0.37, output_bbox=BBox(0, 0, N, N))
sync = cp.cuda.Device().synchronize


def timed(f, n=20):
    f(); sync()
    ts = []
    for _ in range(n):
        t0 = time.perf_counter(); f(); sync(); ts.append(time.perf_counter() - t0)
    return float(np.median(ts))


on_gpu = cp.asarray(image)
res = reproject_array_device(on_gpu, spec).image  # a DeviceReprojectionResult; .image is the CuPy array
d = {"N": N, "mbytes": image.nbytes / 1e6, "gpu": cp.cuda.runtime.getDeviceProperties(0)["name"].decode(),
     "up_s": timed(lambda: cp.asarray(image)), "xrep_s": timed(lambda: reproject_array_device(on_gpu, spec)),
     "down_s": timed(lambda: cp.asnumpy(res))}
(out / "v4.json").write_text(json.dumps(d, indent=1))
print(d)
