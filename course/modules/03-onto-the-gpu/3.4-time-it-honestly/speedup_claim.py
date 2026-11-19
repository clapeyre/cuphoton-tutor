"""How much faster is xRep on the GPU? Reprojects a 2048 x 2048 image on the
CPU and on the GPU and reports the speedup."""
import time

import cupy as cp
import numpy as np
from cuphoton.xrep import BBox, ReprojectionSpec, reproject_array, reproject_array_device

N = 2048
image = np.random.default_rng(0).normal(100, 10, (N, N))
spec = ReprojectionSpec(mapping=lambda xy: xy + 0.37, output_bbox=BBox(0, 0, N, N))

start = time.perf_counter()
reproject_array(image, spec, backend="cpu")
cpu_seconds = time.perf_counter() - start

on_gpu = cp.asarray(image)
reproject_array_device(on_gpu, spec)  # warm-up
gpu_runs = []
for _ in range(10):
    start = time.perf_counter()
    reproject_array_device(on_gpu, spec)
    gpu_runs.append(time.perf_counter() - start)
gpu_seconds = float(np.median(gpu_runs))

print(f"CPU: {cpu_seconds:.3f} s")
print(f"GPU: {gpu_seconds * 1000:.2f} ms (median of 10, after warm-up)")
print(f"Speedup: {cpu_seconds / gpu_seconds:,.0f}x")
