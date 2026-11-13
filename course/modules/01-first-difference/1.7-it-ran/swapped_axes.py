"""Find and measure what changed between the sample reference and target.

Run from a directory containing sample/ (see tools/make_sample.py).
"""
import numpy as np
from astropy.wcs import WCS
from cuphoton.core.fits_io import read_fits_images
from cuphoton.xfit import fit_single_sources
from cuphoton.xpois import (
    GaussianBasisComponent,
    identify_residual_hotspots,
    solve_constant_kernel,
    standardize_constant_kernel_residual,
    window_stamps,
)
from cuphoton.xrep import BBox, ReprojectionSpec, make_wcs_pair_transform, reproject_masked_array

target_read = read_fits_images("sample/target.fits", [0])
reference_read = read_fits_images("sample/reference.fits", [0])
target = target_read.arrays[0].astype(np.float64)
reference = reference_read.arrays[0].astype(np.float64)
target_header = target_read.infos[0].header
reference_header = reference_read.infos[0].header

target_variance = np.clip(target, 0, None) / target_header["GAIN"]
reference_variance = np.clip(reference, 0, None) / reference_header["GAIN"]

mapping = make_wcs_pair_transform(WCS(target_header), WCS(reference_header))
spec = ReprojectionSpec(mapping=mapping, output_bbox=BBox(0, 0, target.shape[1], target.shape[0]))
aligned = reproject_masked_array(
    reference, reference_variance, np.zeros(reference.shape, dtype=bool), spec, backend="cpu"
)

basis = [GaussianBasisComponent(0.7, 4), GaussianBasisComponent(1.4, 2), GaussianBasisComponent(2.8, 2)]
fit = solve_constant_kernel(aligned.image, target, basis, kernel_shape=(19, 19),
                            variance=target_variance, background_degree=1, backend="cpu")
difference = fit.residual

noise = standardize_constant_kernel_residual(difference, kernel=fit.kernel, target_variance=target_variance,
                                             reference_variance=aligned.variance)
regions = identify_residual_hotspots(noise.standardized_residual, robust_sigma=1.0,
                                     threshold_sigma=5.0, max_regions=None)

positions = np.array([region["peak_yx"] for region in regions], dtype=float)
cutouts = window_stamps(difference, positions, 21)
cutout_variance = window_stamps(noise.marginal_residual_variance, positions, 21)
valid = np.isfinite(cutouts) & np.isfinite(cutout_variance) & (cutout_variance > 0)

start = np.zeros((len(positions), 2))
sources = fit_single_sources(cutouts, cutout_variance, start, target_header["PSFSIG"], mask=valid)
signed_flux = np.sign(sources.parameters[:, 0]) * sources.flux

print(f"{len(regions)} candidates")
for pos, flux, error in zip(positions, signed_flux, sources.flux_error):
    print(f"candidate at {pos}: flux {flux:.0f} +- {error:.0f} DN")
np.savez("swapped_axes_result.npz", cutouts=cutouts, positions=positions,
         flux=signed_flux, flux_error=sources.flux_error,
         converged=sources.converged, uncertainty_valid=sources.uncertainty_valid)
