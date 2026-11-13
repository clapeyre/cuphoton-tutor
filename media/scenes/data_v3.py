"""Real kernel numbers for v3 (needs sample/ in cwd). Saves v3.npz: kernel, the basis images, fitted weights."""
import sys
import numpy as np
exec(open(__file__.replace("data_v3", "data_v1")).read().split("good = [")[0])  # reuse alignment from data_v1
from cuphoton.xpois import GaussianBasisComponent, solve_constant_kernel
basis = [GaussianBasisComponent(0.7, 4), GaussianBasisComponent(1.4, 2), GaussianBasisComponent(2.8, 2)]
fit = solve_constant_kernel(aligned, target, basis, kernel_shape=(19, 19), variance=tv, background_degree=1, backend="cpu")
k = fit.kernel
yy, xx = np.mgrid[-9:10, -9:10]
sig = np.sqrt((k * (xx**2 + yy**2)).sum() / k.sum() / 2)
print("kernel sum", k.sum(), "effective sigma [px]", sig)
bk = np.asarray(fit.basis_kernels)
c = np.asarray(fit.kernel_coefficients)
np.savez(f"{out}/v3.npz", kernel=k, basis_kernels=bk, coeffs=c)
