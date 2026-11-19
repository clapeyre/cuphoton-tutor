# 9.1 · tutor notes

**Goal:** a conversation about the learner's own work, mapped onto cuPhoton:
which part takes their data (or none), where its guide chapter starts, how
it would fit in their workflow, and the first evidence they'd check on its
first run. Course exit (O7). It closes the course: by now they've run the
image chain (01–05) and the three tracks (06 xImage, 07 xBeam, 08 xRay);
check `progress` for any they skipped, and if one fits their work, send
them there ([6.1](#/6.1), [7.1](#/7.1), [8.1](#/8.1)). No runs in this
lesson: answer from the briefs below, and read the cited file in the
pinned checkout only when a question goes beyond them.

## Your turn `your-data` (course exit)
- Open it as a conversation, not a quiz. First understand their work:
  what they measure, the instrument, array shape and format, volume, what
  they want out of it, and what they do with it today. One question at a
  time if it's vague. If they'd rather not describe a real lab, let them
  pick a plausible one.
- Map it to a component (or to "none fits": say so plainly; cuPhoton is
  not a general array library). Often more than one part fits a workflow
  (frames reconstructed with xImage, then compared over time with the
  chain; two detectors' traces correlated with xBeam): say how they'd
  connect. Name the guide chapter and the first command from the brief,
  verbatim. If they ran that part's track, tie it to what they found
  there, in their words if you have them.
- Ask what they'd check on its first run. Steer with the course's habits, on
  that component's terms: the receipt or summary that says what ran (Module
  02; always ask for this one if they don't name it, above all when their
  goal is speed: a silent CPU fallback makes a speed claim wrong), what the step should give back (O2), the noise model (4.1), and a test
  with a known answer (4.4's injection test; for xBeam a known delay (7.1),
  for xRay planted modes at their own step size (8.2), for xImage planted
  fakes at their settings (6.3)). Give them the component's silent-error
  trap from its brief once they've named their checks, as the thing to add.
- Then the wider question, if they want it: what would they still need
  that cuPhoton doesn't do, and what would they ask an agent to show them
  before trusting its first run on their data.
- **Pass:** a component (or "none") with a reason tied to their data's shape,
  and at least two concrete first-run checks, one of which is evidence the run
  leaves behind. Settle with their plan in their words, then `reveal("9.1")`.
- Don't oversell: if something is CPU-only, needs a native build, or isn't
  shipped (no xScan checkpoint ships; HDF5 via Legate was removed), say so.
  Don't claim speedups the tracks didn't measure: on this machine xImage
  was 5× faster on the GPU at 600 × 600 × 3 frames, and xRay's detector fit
  was not faster than a NumPy loop at 2,048 rows (8.3's notes).

## Component briefs (pinned checkout ff4d260)

Paths are relative to the cuPhoton checkout; `G/` = `docs/guide/`. Every API
and command was checked against `src/cuphoton/` on 16 Nov 2026.

### Corrections worth knowing

- **No HDF5 via Legate.** `CHANGELOG.md:73-76`: "xDR's Legate-backed HDF5 loader has been removed. Use `h5py` for local HDF5 reads…". `docs/components/xdr.md:229-238`: `cuphoton.xdr.load_hdf5` and the `hdf5` extra are gone. "Legate" now survives only as the name of an xRay HDF5 layout, `legate-cube` (`docs/xray/README.md:160`, `src/cuphoton/xray/hdf5.py:161`).
- **VDIF is xBeam's format, not xDR/Core's.** There is no VDIF code in `src/cuphoton/xdr` or `src/cuphoton/core`. It lives in `src/cuphoton/xbeam/adapters/vdif/` and is covered in `G/correlate.qmd` (see xBeam below).
- **xDR stub:** `xdr.open_gpu` is exported, but it only raises `NotImplementedError` (`src/cuphoton/xdr/convenience.py:15-27`; also stated in `docs/components/xdr.md:226-227`).
- Only `examples/benchmarks/README.md` and `examples/transient-chain/README.md` exist. There is no `examples/xray/`.

---

### xRep: align (`G/align.qmd`)
- **For:** puts one image on another image's pixel grid using the WCS in both headers, resampling the image, its variance and its bad-pixel mask together. Also stacks several exposures on one shared grid, without combining them (`:3`, `:155`).
- **Input:** two-dimensional FITS images with a celestial WCS (`:8`). From Python: NumPy image, variance (nonnegative, NaN or +inf for no data) and an integer or boolean mask, plus a `ReprojectionSpec(mapping=..., output_bbox=BBox(...))`. Positions are (x, y) while arrays index (y, x) (`:63`, `:67`, `:210`).
- **First run:** `cuphoton xrep reproject-stack --inputs sample/reference.fits --target-wcs sample/target.fits --backend cpu --mapping-grid-step 1 --output-dir runs/align` (`:241-242`). From Python: `make_wcs_pair_transform(target_wcs, reference_wcs)` (`:59`), then `reproject_masked_array(reference, reference_variance, mask, spec, backend="cpu")` (`:86`).
- **Needs:** the CPU profile. The `gpu` profile adds `backend="cupy"`; `native` needs the native extension (`:7`, `:214`). Without `backend`, it takes the first available of `cupy`, CUDA `torch` and `cpu` (`:210`).
- **Silent trap:** "The commands do not resample variance", and `reproject-stack` "marks only the geometric footprint"; use `reproject_masked_array` for both (`:259`). "xRep does not skip NaN source pixels. Each NaN turns every output pixel that reads it into NaN" (`:264`). Resampling correlates neighbouring pixels' noise and "xRep does not return that correlation" (`:91`). `area_scaling=True` by default: set it `False` for surface-brightness units (`:151`).
- **Evidence:** the result's `backend`, `interpolation` and `metadata` (variance recorded as diagonal); mask bit 1 marks pixels outside the source, with NaN image and variance (`:87-95`). The command's run directory holds `summary.json` (`requested_backend`, `backend`, `device`, `fits_reads`, `interpolation`, `stack_shape`, `saved`) and `artifacts/reprojected_stack.npy` (`:245`; `src/cuphoton/xrep/workflows.py:932-982`).
- **Track:** Module 01, "A first difference with cuPhoton": xRep moved the
  reference onto the target's grid, and the learner predicted which image
  moves and why (the sharper one, which gets blurred next). Link [1.3](#/1.3).

### xPois: subtract (`G/subtract.qmd`)
- **For:** fits a convolution kernel that blurs the reference until it matches the target, plus a smooth background, subtracts, predicts the noise of every difference pixel and finds the candidates (`:3`).
- **Input:** a reference and a target of the same shape on one pixel grid, each with a variance plane; variance must be strictly positive, with NaN marking pixels to leave out (`:5`, `:424`, `:430`). A kernel basis of `GaussianBasisComponent(sigma, degree)` and an odd `kernel_shape` (`:42`, `:56`). The command reads FITS or NPY (`:322`).
- **First run:** `solve_constant_kernel(aligned.image, target, basis, kernel_shape=(19, 19), variance=target_variance, background_degree=1, backend="cpu")` (`:65-66`). CLI: `cuphoton xpois subtract --reference sample/reference_aligned.npy --target sample/target.fits --variance sample/target_variance.npy --fit-mask sample/fit_mask.npy --kernel-height 19 --kernel-width 19 --basis-sigmas 0.7,1.4,2.8 --basis-degrees 4,2,2 --background-degree 1 --backend cpu --no-review --output-dir runs --name sample`, then `cuphoton xpois evaluate-subtraction --run-dir runs/sample` (`:333-337`).
- **Needs:** the CPU profile. `gpu` for `cupy`; `cutile` is experimental and needs its extra; `native` needs the native extension (`:5`, `:302-304`).
- **Silent trap:** "A GPU fit reports `backend` `cpu`": `auto` falls back without error, so check `fit.backend` (`:452`). Bad pixels left in "pull the kernel, and stars across the image become candidates"; set them to NaN or pass `--mask-policy` (`:215`, `:375`). The noise prediction ignores correlation: on a resampled reference "the diagonal prediction is approximate" (`:109`). `solve_spatial_als` "returns `converged=False` without an error. Check it." (`:251`). `identify_residual_hotspots` keeps only 8 regions unless `max_regions=None` (`:289`). Not in the guide, from the code: `cuphoton xpois subtract` takes only the target's `--variance` (no reference variance) and saves kernel, matched image, residual, fit mask and background, but no noise prediction or standardized residual (`src/cuphoton/xpois/commands.py`), so a z-map needs the Python API (`standardize_constant_kernel_residual`, as in 1.4).
- **Evidence:** `fit.backend`, `chi2`/`dof` and `fit_pixel_count`; the kernel sum is the reference-to-target flux ratio (`:68-73`). The robust spread of the standardized residual should sit near one (`:98-102`). The command's `runs/<name>/summary.json` holds `requested_backend`, `backend`, `device`, `fits_reads`, `kernel_sum`, `chi2`, `dof`, `fit_pixel_count` and, with masks, `input_mask`; `evaluate-subtraction` prints `robust_sigma` and `pixels_gt_5sigma` (`:340`, `:365`, `:392-406`; `src/cuphoton/xpois/workflows.py:924-955`, `:1520-1540`).
- **Track:** Module 01, "A first difference with cuPhoton": the 19 × 19
  kernel, the NaN edge frame it leaves, chi2/dof 1.29 as necessary but not
  proof ([1.4](#/1.4)), then the candidates from the standardized residual
  ([1.5](#/1.5)). Link [1.4](#/1.4).

### xFit: measure (`G/measure.qmd`)
- **For:** measures each candidate on a difference image: one fitted source (new, brightened or faded), a forced PSF flux at a known position, or a dipole (two opposite lobes, from a moved source or a misaligned star) (`:3`, `:68-75`). `fit_single_sources` with `psf_sigma` fits a round lobe of that width (amplitude, x, y); without it the lobe is an elliptical Gaussian with free widths and orientation (`:81`; `src/cuphoton/xfit/single.py:106-119`). The model has no constant background term: a stamp sitting on a pedestal needs it subtracted first.
- **Input:** cutouts as NumPy (or CuPy) arrays `(batch, y, x)` cut from the difference image, with a per-pixel variance of the same shape, finite and strictly positive on the pixels the `mask` includes (`:52`, `:256`; `src/cuphoton/xfit/io.py:250-255`). Positions are (x, y) from the cutout centre (`:64`). `fit_single_sources` and `forced_psf_photometry` take the variance as a required argument; `fit_dipoles` takes it as optional, scaling the covariance by the reduced chi-square without it (`:257`). The command reads an NPZ with `candidate_id` and `images`, optionally `initial`, `mask`, `variance` and `stamp_basis` (`:301`).
- **First run:** `fit_single_sources(cutouts, cutout_variance, start, psf_sigma, mask=usable, sign=1)` (`:88`). CLI: `cuphoton xfit data-validate --input sample/cutouts.npz --model gaussian --mode difference`, then `cuphoton xfit fit-dipoles --input sample/cutouts.npz --model gaussian --backend numpy --output-dir runs/dipoles` (`:311-312`).
- **Needs:** the CPU profile. `gpu` for `cupy`; `cutile` and `native` fit Gaussian models only (`:5`, `:284`). The command line fits dipoles only (`:344`).
- **Silent trap:** "A converged fit can still be wrong" (`:175`). The covariance "does not account for a wrong PSF or pixel correlations" (`:95`). `fit_single_sources`' `flux` is "the nonnegative lobe-flux magnitude"; the sign is in `parameters[:, 0]` (`:95`). Forced `flux_error` "leaves out the uncertainty of a position fitted on the same image" (`:109`).
- **Evidence:** `converged`, `uncertainty_valid` and `uncertainty_reason`, plus `status`, `reduced_chi_square`, `backend`, `device`, `dtype` and `solver_version` on a dipole result (`:144-155`); `dipole_quality_flags` bits (`:188-196`). The command writes `summary.json` (`requested_backend`, `backend`, `device`, `solver_version`, `inputs.variance_present`, and `metrics`: `converged_count`, `uncertainty_valid_count`, `median_reduced_chi_square`, `status_counts`), `fits.parquet` and `fit-arrays.npz` (`:315`, `:335`; `src/cuphoton/xfit/io.py:560-612`).
- **Track:** Module 01, "A first difference with cuPhoton": `fit_single_sources`
  with the width fixed to `PSFSIG`; both injected fluxes came back within
  about two error bars, and variance × 4 left the fluxes alone and doubled
  the error bars. Link [1.6](#/1.6).

---

### xImage: reconstruct (`G/reconstruct.qmd`)
- **For:** builds one sharp image from many already-aligned frames, each with its own blur (PSF) and noise.
- **Input:** a bundle (NPY directory, HDF5 file or Zarr store) holding `images` `(batch, y, x, frame)`, `variances` (same shape, finite and positive) and `psfs` `(psf_y, psf_x, channel, frame)`, which must be square, odd-sized and one channel. Optional: `masks` (bool, `True` = good pixel) and `exp_times`. Settings come from a strictly validated YAML file (`:41-47`, `:67`, `:71`).
- **First run:** `uv run --no-sync cuphoton ximage data-validate --base data` (`:241`). From Python: `validate_bundle(bundle)` (`:62`).
- **Needs:** the `ximage` extra (PyTorch, Photutils, Zarr). Runs on CPU or CUDA (`device: auto`). Needs the checkout for the example configs. Frames must already share one pixel grid (`:7-9`).
- **Silent trap:** "An empty list does not check every pixel value" (`:49`). Also, the evaluation compares against a median coadd made from the same frames, so "Similarity or sharpness alone therefore does not show that a reconstruction is accurate" (`:138`). The output image keeps a PSF border that you must crop, and it is in exposure-time-normalised units (`:122`).
- **Evidence:** a run directory holding `config.yaml` (resolved), `summary.json` (backend, device, dtype, version, input store, region, saved paths, `trace_summary`, timings), `artifacts/image.npy` and `trace/`. `evaluate-reconstruction` also writes `evaluation/evaluation_summary.json` (`:117-120`, `:247`).
- **Track:** Module 06, "Combining many images (xImage)" (a known scene; a cosmic
  ray and a wrong PSF that pass validation; the M101 nights, fakes and the
  supernova). Link [6.1](#/6.1).

### xRay: X-ray detector traces (`G/xray-traces.qmd`)
- **For:** pump-probe experiments. It turns laser-on and laser-off detector frame stacks into a trace over delay, then fits that trace as a sum of damped oscillations, optionally for every detector row.
- **Input:** a laser-on and laser-off pair of HDF5 files in one layout. `cropped-cube` holds `imgs` `(frame, y, x)`, `scan_var`, `i0`, `i0_ipm3`, `bin_count` (each `(frame,)`) and `ROI`. `legate-cube` holds `jungfrau1M_data` etc. Both files need the same frame shape and the same delays (`:38-49`; `docs/xray/README.md:157-161`).
- **First run:** `cuphoton xray doctor` (`:21`). Then `probe_hdf5_pair(...)` or `cuphoton xray data-probe` (`:86`, `:321`).
- **Needs:** the CPU profile (NumPy, h5py) for trace fitting. The default `detector-artifacts` backend needs the `gpu` profile, CuPy and a GPU. The structured backends need the native extension (`CUPHOTON_XRAY_BUILD_EXT=1`, Linux, C++17). `phonon-viz` needs `viz` (`:7-8`, `:325-330`).
- **Silent trap:** "A fast mode is missing from the fit… This can discard high-frequency modes even without noise" (`:329`). Also, `--components` defaults to 30, not the order the sweep chose (`:210`). Detector fits smooth and integrate, so they "differ from a fit of the tile trace" (`:190`). The fit assumes uniformly increasing delays: "check that condition" (`:111`).
- **Evidence:** `manifest.json` (inputs, ROI, settings, fit and failure counts), `fit_status.npy` (0 not processed, 1 fitted, 2 skipped, 3 failed) and `fit_diagnostics.npz` (`:218-224`). `extract-trace` writes an NPZ with a `summary` entry (`:304`).
- **Track:** Module 08, "Time-resolved X-ray traces (xRay)" (one trace with known modes; a
  mode lost at 0.1 ps steps and a scan with uneven steps; a whole detector
  where dead rows came back "fitted"). Link [8.1](#/8.1).

### xBeam: correlate (`G/correlate.qmd`)
- **For:** measures how much two recordings of one source share, and at what delay, frequency by frequency (cross-spectra and lag correlations). Examples: two microphones, two radio telescopes.
- **Input:** uniformly sampled signals on one time grid. Use NumPy/CuPy vectors via `ArraySource`, or 1-D HDF5 datasets with scalar `sample_rate_hz` and `origin_seconds` attributes via `Hdf5Source` (`:9`, `:36-42`, `:123`). Radio path: a JSON job or DiFX `.input` file, plus file-backed, two-bit, non-legacy VDIF recordings with oversampling and decimation factors of one (`:251-254`).
- **First run:** `correlate_series(source, spec)` (`:52`). CLI: `cuphoton xbeam correlate-series series.json --output results.h5 --backend numpy` (`:224`). Radio: `cuphoton xbeam inspect-vdif AA.vdif --json` (`:260`).
- **Needs:** no extra on CPU. The GPU path needs `gpu` (or `io`) plus a GPU. `io_backend="cufile"` needs working GPUDirect Storage. `build-vdif-sidecar` defaults to `cufile`, so pass `--backend posix` without GDS (`:7-8`, `:199`, `:269`).
- **Silent trap:** "The lag peak is at the wrong place. The delay can exceed the window" (`:289`). Products are raw: "xBeam applies no taper, mean removal or normalization" (`:68`). "Do not average shard outputs" (`:161`).
- **Track:** Module 07, "Correlating two receivers (xBeam)", teaches xBeam end to
  end (a known delay, three radio stations with a wrong clock, GW150914 in
  the two LIGO detectors). If xBeam fits their data, link [7.1](#/7.1).
- **Evidence:** in `results.h5`, the attributes `schema` and `complete` (false after an interrupted write) and `/results/<result_index>` (`:238-247`). Per result: `lag_valid_samples`, `contributing_windows` and `valid` (`:64-65`). Radio output: `metadata.jsonl`, `spectra.c64` and `ingest-manifest.json` (`:271`).

### Core executors / scale-out (`G/scale.qmd`)
- **For:** spreads a batch of whole work items (image pairs, chunks of cutouts) over GPU workers on one or many nodes.
- **Input:** the commands' own inputs. For example, `xfit fit-dipoles` takes an NPZ with `candidate_id`, `images` and `variance`. `xscan run-pipeline` takes a JSON manifest (`schema`, `configuration`, `items`) whose image descriptors carry path, SHA-256, shape and dtype (`:58`, `:90`, `:105`).
- **First run:** `cuphoton xfit fit-dipoles --input runs/scale/stamps.npz --model gaussian --backend numpy --output-dir runs/scale/xfit-local` (`:66-67`). It uses the `local` executor.
- **Needs:** for GPU runs, Linux with CUDA 13-compatible drivers and the `gpu` extra. Add either `mpi` with the site's Open MPI or `dragon` (Python 3.12/3.13). Every node must see the same absolute paths (`:8`).
- **Silent trap:** "Dragon's SSH launcher does not forward `CUDA_VISIBLE_DEVICES`. A mask in your shell does not limit the GPUs it finds on remote hosts" (`:204`). "A successful summary does not prove that MPI finalized or Dragon stopped" (`:266`). An unbalanced shard count makes a round wait for the slowest worker (`:36`, `:130`).
- **Evidence:** `<output-dir>/<name>/summary.json` holds `status` (written only after every record matched its files), `batch_wall_sec`, `finalization_sec`, `benchmark.rounds`, and `placements` (Dragon) or `world_size` (MPI). Each `workers/worker-*.json` carries `provenance.hostname`, `gpu.uuid`, `success_count` and `failed_count` (`:242-277`).

### xLens: monitor (`G/monitor.qmd`)
- **For:** records the values your own code measured during a run (one sample per image, candidate or window) and shows them in a dashboard or a single HTML file.
- **Input:** no fixed file format. You write an analyser that returns a `Sample` of `Measurement` (scalar + unit), `Finding` and `Artifact` (relative path + SHA-256). Limits: 64 KiB per sample, 128 measurements, 10,000 samples per run (`:41-69`, `:241`).
- **First run:** `cuphoton xlens quickstart --output-dir xlens-demo` (`:246`). Then `Monitor(...)` and `monitor.replay(...)` (`:78-79`).
- **Needs:** any profile, no GPU, no outside service. Language-model questions need the `xlens-inference` extra (`:3`, `:5`, `:272`). The server has no TLS and no authentication (`:255`).
- **Silent trap:** "This poller processes each filename once." A file rewritten in place is never re-read, so use a new revision instead (`:193`). A corrupt input becomes an ingestion error, not a sample, and the error record omits the message (`:86`). The page shows only the last 256 samples (`:222`).
- **Evidence:** `state.json` in the state directory (all samples, revision `history`, and `errors` keeping the latest 100), the `/health` and `/api/state` routes, and the exported `report.html` (`:73`, `:165-172`, `:241`).

### xScan: classify (`G/classify.qmd`)
- **For:** a neural network that scores each candidate cutout as a real change or an artefact (cosmic ray, badly subtracted star), with a human-review loop for labels.
- **Input:** a dataset directory: `search.npy`, `template.npy` and `difference.npy` (each `(candidate, y, x)`), `labels.npy` (1 real, 0 bogus), `split.npy` (0/1/2) and `metadata.jsonl`. `metadata.jsonl` needs `exposure_id`, `ccd_id`, `band`, `x`, `y`, `label_source` and `split_group`. In memory, the triplet model takes float32 `(candidate, channel, y, x)` (`:52-59`, `:79`, `:221`).
- **First run:** `cuphoton xscan data-validate --dataset-dir sample/cutouts` (`:99`), then `data-check-training-labels … --require-ok` (`:100`).
- **Needs:** the `torch` extra (CPU) or `gpu`. The review viewers need `viz`. `predict_fits` needs CuPy, an explicit CUDA device and odd stamp sides (`:9`, `:387`).
- **Silent trap:** `probability` "Training does not calibrate it into an observed probability… Check calibration… before interpreting a score such as 0.9 as a 90% chance of being real" (`:5`). "A checkpoint is valid only for cutouts prepared like its training set." Training and prediction do not align or rescale (`:46`, `:406`).
- **Evidence:** the run directory holds `checkpoint.pt`, `config.yaml`, `history.json` and `summary.json` (`device`, `early_stopping.best_epoch`, `best_metric`) (`:150-154`). Also `evaluation/test/` (metrics, `threshold_diagnostics`, `summary.md`), `inference/test/probabilities.npy`, and the review `queue.jsonl` and `annotations.jsonl` (`:165`, `:190`, `:196`, `:329`).

### Transient chain (`G/transient-chain.qmd`; `examples/transient-chain/`)
- **For:** the shipped end-to-end pipeline, from a target and reference FITS image to a catalogue of changed sources with positions, fluxes, error bars and an optional real/bogus score.
- **Input:** a target and a reference as FITS with WCS headers, plus a variance plane each (needed for most of the error budget). A `selections.json` with one entry per target (identity keys plus path keys, absolute paths). A YAML config started from `config-generic.yaml` (`:21`, `:85`, `:155`).
- **First run:** `uv pip install -e examples/transient-chain` (`:50`). Then the CPU check `prepare_workload(Path("sample/selections.json"), Path("sample/chain.yaml"), None)` (`:174`). On the GPU: `python examples/transient-chain/launch.py --executor local --config sample/chain.yaml --selections sample/selections.json --output-dir out` (`:224-225`).
- **Needs:** an NVIDIA GPU on Linux with the `gpu` and `catalog` extras, plus `dragon` or `mpi` for those executors. Optional: an xScan checkpoint. Reinstall the example after every `uv sync` (`:20-22`, `:47`).
- **Silent trap:** replacing the whole `params` block "drops the shipped `identity`, `extra_keys` and `variance_kind`" (`:97`). Without a reference variance plane, the chain "leaves out the `corr` error term" (`:197`). With `uq.enabled=false`, "`uq_valid` is always true" (`:330`). `ra`/`dec` come from the hotspot centroid, not the fitted source position (`:270`).
- **Evidence:** `out/items/<item>/summary.json` holds `candidates`, `psf_sigma_source`, `uq_terms`, `uq.excluded`, `diagnostics.read.receipts`, `timings_sec` and `transfers`. The run also writes per-item and merged `catalog.parquet` (with `quality_flags` and `uq_valid`). Cross-checks: `compare_catalogs.py` and `repeat_catalogs.py` (`:251`, `:296-306`, `:384-388`).

- **Seen on the course's own PS1 pair** (16 Nov, GPU, `config-generic.yaml`
  with `on_target_grid: true`): with the template already on the target grid
  the refine stage skips itself, so no PSF width is measured: `psf_flux` is NaN
  and `uq.excluded` reads "no PSF width" for every term, while the run reports
  success. Set `xfit.psf_sigma_px`. And the default `auto_stamp_mask: true`
  fits the kernel on 5 stamps; on this galaxy field chi2/dof was about 15 and
  injected fluxes came back 4–9% low; `auto_stamp_mask: false` gave 1.55 and
  unbiased fluxes. Module 05 teaches both; the learner has been through them.

### Uncertainty (`G/uncertainty.qmd`)
- **For:** follows per-pixel noise through align → subtract → measure, corrects error bars for noise made correlated by resampling and convolution, and checks the bars with injected sources or repeat exposures.
- **Input:** a target and a reference with per-pixel variance planes (squared image units), or a finished transient-chain run (`:8`, `:27`).
- **First run:** `empirical_correlation_factor(difference, difference_variance, weights, empty)` (`:108`). On a finished chain run: `python examples/transient-chain/repeat_catalogs.py out/items/*/catalog.parquet --out repeat.json` (`:379`).
- **Needs:** the CPU profile and Matplotlib. The GPU is optional: the calls follow CuPy inputs (`:7`, `:411`).
- **Silent trap:** "A term without its inputs is left out; that does not establish that its physical contribution is zero" (`:212`). The repeat test: "A bias that every exposure shares passes the test unseen" (`:382`). The bars assume the variance planes are right and the PSF model matches (`:388`, `:391`).
- **Evidence:** the chain's `summary.json` holds `uq_terms`, `uq.excluded`, `uq.correlation` (`closed_form`, `measured`, `source`), `uq.kernel_mismatch`, and the counts `uq.undefined_factor` and `uq.rotated_grid`. The catalogue has `<q>_err_<term>`, `uq_window_masked` and `uq_corr_measured`. The library calls return `positions_used` and `n_rotated` (`:249-256`, `:109`, `:139`).

### xDR / Core reading beyond FITS (`G/read-fits.qmd`)
- **For:** reads images from FITS files into CPU (NumPy) or GPU (CuPy) arrays, with a receipt naming the reader that actually ran.
- **Input:** 2-D image HDUs only, so tables and cubes are not listed (`:9`, `:31`). xDR decodes uncompressed images or `GZIP_1`/`GZIP_2` tile-compressed ones. It rejects `RICE_1`, `HCOMPRESS_1`, `PLIO_1`, quantised images, `BSCALE`/`BZERO`/`BLANK` and `.fits.gz` (`:163-166`).
  - **Beyond FITS:** HDF5 via Legate was removed. Use plain `h5py` and move arrays to the GPU yourself (`docs/components/xdr.md:229-238`). VDIF is not read here; see xBeam.
- **First run:** `inspect_fits_images("sample/target.fits")` (`:27`). It reports `xdr_unsupported_reason` per HDU without decoding.
- **Needs:** the CPU profile for Astropy. For xDR: the `gpu` profile plus a native extension built with `bash src/cuphoton/xdr/src/build.sh`, which needs C++17, the CUDA and cuFile headers and a thread-safe CFITSIO (`:185-189`).
- **Silent trap:** a section read "does not shift its WCS" (`:101`). One unsupported HDU makes the whole multi-HDU call fall back to Astropy (`:159`). CPU runs of xFit, xPois and xRep turn `auto` into `astropy`, so the receipt says `requested_reader: astropy` (`:252`). The receipt records requested xDR options, "not the engine that ran" (`:218`), and not whether GDS ran (`:67`).
- **Evidence:** `result.metadata()` holds `reader`, `requested_reader`, `location`, `fallback_reason`, `hdus`, `decoded_bytes` and `xdr_options` (`:59-65`). Commands list one receipt per read under `fits_reads` in `summary.json` (`:238`).
