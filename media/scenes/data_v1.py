"""Real cuPhoton CPU outputs on the sample pair for v1. Run from a dir containing sample/:
  uv run --no-sync --project <cuPhoton> python data_v1.py <outdir>
Saves <outdir>/v1.npz (same numbers as docs/guide/first-difference.qmd)."""
import sys
import numpy as np
from astropy.wcs import WCS
from cuphoton.core.fits_io import read_fits_images
from cuphoton.xrep import BBox, ReprojectionSpec, make_wcs_pair_transform, reproject_masked_array
from cuphoton.xpois import (GaussianBasisComponent, solve_constant_kernel, identify_residual_hotspots,
                            standardize_constant_kernel_residual)

out = sys.argv[1] if len(sys.argv) > 1 else "."
tr = read_fits_images("sample/target.fits", [0]); rr = read_fits_images("sample/reference.fits", [0])
target = tr.arrays[0].astype(float); reference = rr.arrays[0].astype(float)
th, rh = tr.infos[0].header, rr.infos[0].header
tv = np.clip(target, 0, None) / th["GAIN"]; rv = np.clip(reference, 0, None) / rh["GAIN"]
mapping = make_wcs_pair_transform(WCS(th), WCS(rh))
spec = ReprojectionSpec(mapping=mapping, output_bbox=BBox(0, 0, target.shape[1], target.shape[0]))
al = reproject_masked_array(reference, rv, np.zeros(reference.shape, bool), spec, backend="cpu")
aligned, av = al.image, al.variance

def match(basis):
    fit = solve_constant_kernel(aligned, target, basis, kernel_shape=(19, 19), variance=tv,
                                background_degree=1, backend="cpu")
    noise = standardize_constant_kernel_residual(fit.residual, kernel=fit.kernel, target_variance=tv, reference_variance=av)
    return fit, noise.standardized_residual, noise.marginal_residual_variance

good = [GaussianBasisComponent(0.7, 4), GaussianBasisComponent(1.4, 2), GaussianBasisComponent(2.8, 2)]
fit, z, marg = match(good)
narrow = [GaussianBasisComponent(0.5, 2)]            # too narrow to widen 1.2 px -> 1.8 px
fit_bad, z_bad, _ = match(narrow)
regions = identify_residual_hotspots(z, robust_sigma=1.0, threshold_sigma=5.0, max_regions=None)
peaks = np.array([r["peak_yx"] for r in regions])

# naive subtraction: target minus the middle of the reference, no alignment at all
off = (reference.shape[0] - target.shape[0]) // 2
naive = target - reference[off:off + 256, off:off + 256]
# aligned but not blur-matched (sky level matched by medians only)
aligned_only = target - aligned * (np.nanmedian(target) / np.nanmedian(aligned))

# an unchanged bright star for the 1D blur story: brightest aligned local max away from edges/hotspots
a = np.where(np.isfinite(aligned), aligned, 0); best = None
for y in range(20, 236):
    for x in range(20, 236):
        v = a[y, x]
        if (best is None or v > best[0]) and v == a[y-2:y+3, x-2:x+3].max() \
                and all(np.hypot(y-p[0], x-p[1]) > 12 for p in peaks):
            best = (v, y, x)
_, sy, sx = best
sl = slice(sx - 12, sx + 13)
prof_ref = aligned[sy, sl] - np.median(aligned); prof_tgt = target[sy, sl] - np.median(target)
np.savez(f"{out}/v1.npz", target=target, reference=reference, aligned=aligned, naive=naive,
         aligned_only=aligned_only, difference=fit.residual, z=z, marg_var=marg, z_bad=z_bad, kernel=fit.kernel,
         kernel_bad=fit_bad.kernel, peaks=peaks, star=np.array([sy, sx]), prof_ref=prof_ref, prof_tgt=prof_tgt,
         psfsig=np.array([rh["PSFSIG"], th["PSFSIG"]]))
print("kernel sum", fit.kernel.sum(), "bad kernel sum", fit_bad.kernel.sum(), "star", sy, sx, "peaks", peaks.tolist())
print("z std", np.nanstd(z), "z_bad std", np.nanstd(z_bad), "chi2/dof", fit.chi2/fit.dof, fit_bad.chi2/fit_bad.dof)
print("profile peaks", prof_ref.max(), prof_tgt.max())
