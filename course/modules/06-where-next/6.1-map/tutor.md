# 6.1 · tutor notes

**Goal:** the learner places their own work on the map: which component takes
their data, where its guide chapter starts, and the first evidence they'd check
on its first run. Course exit (O7). No runs in this lesson: answer from the
briefs below, and read the cited file in the pinned checkout only when a
question goes beyond them.

## Your turn `your-data` (course exit)
- First understand their data: instrument, array shape and format, volume,
  what they want out of it. One question at a time if it's vague. If they'd
  rather not describe a real lab, let them pick a plausible one.
- Map it to a component (or to "none fits": say so plainly; cuPhoton is not a
  general array library). Name the guide chapter and the first command from
  the brief, verbatim.
- Ask what they'd check on its first run. Steer with the course's habits, on
  that component's terms: the receipt or summary that says what ran (Module
  02), what the step should give back (O2), the noise model (4.1), and a test
  with a known answer (4.4's injection test; for xBeam a known delay, for
  xImage a known scene, for xRay a synthetic trace with a known mode). Give
  them the component's silent-error trap from its brief once they've named
  their checks, as the thing to add.
- **Pass:** a component (or "none") with a reason tied to their data's shape,
  and at least two concrete first-run checks, one of which is evidence the run
  leaves behind. Settle with their plan in their words, then `reveal("6.1")`.
- Don't oversell: if something is CPU-only, needs a native build, or isn't
  shipped (no xScan checkpoint ships; HDF5 via Legate was removed), say so.

## Component briefs (pinned checkout ff4d260)

Paths are relative to the cuPhoton checkout; `G/` = `docs/guide/`. Every API
and command was checked against `src/cuphoton/` on 16 Nov 2026.

### Corrections worth knowing

- **No HDF5 via Legate.** `CHANGELOG.md:73-76`: "xDR's Legate-backed HDF5 loader has been removed. Use `h5py` for local HDF5 reads…". `docs/components/xdr.md:229-238`: `cuphoton.xdr.load_hdf5` and the `hdf5` extra are gone. "Legate" now survives only as the name of an xRay HDF5 layout, `legate-cube` (`docs/xray/README.md:160`, `src/cuphoton/xray/hdf5.py:161`).
- **VDIF is xBeam's format, not xDR/Core's.** There is no VDIF code in `src/cuphoton/xdr` or `src/cuphoton/core`. It lives in `src/cuphoton/xbeam/adapters/vdif/` and is covered in `G/correlate.qmd` (see xBeam below).
- **xDR stub:** `xdr.open_gpu` is exported, but it only raises `NotImplementedError` (`src/cuphoton/xdr/convenience.py:15-27`; also stated in `docs/components/xdr.md:226-227`).
- Only `examples/benchmarks/README.md` and `examples/transient-chain/README.md` exist. There is no `examples/xray/`.

---

### xImage: reconstruct (`G/reconstruct.qmd`)
- **For:** builds one sharp image from many already-aligned frames, each with its own blur (PSF) and noise.
- **Input:** a bundle (NPY directory, HDF5 file or Zarr store) holding `images` `(batch, y, x, frame)`, `variances` (same shape, finite and positive) and `psfs` `(psf_y, psf_x, channel, frame)`, which must be square, odd-sized and one channel. Optional: `masks` (bool, `True` = good pixel) and `exp_times`. Settings come from a strictly validated YAML file (`:41-47`, `:67`, `:71`).
- **First run:** `uv run --no-sync cuphoton ximage data-validate --base data` (`:241`). From Python: `validate_bundle(bundle)` (`:62`).
- **Needs:** the `ximage` extra (PyTorch, Photutils, Zarr). Runs on CPU or CUDA (`device: auto`). Needs the checkout for the example configs. Frames must already share one pixel grid (`:7-9`).
- **Silent trap:** "An empty list does not check every pixel value" (`:49`). Also, the evaluation compares against a median coadd made from the same frames, so "Similarity or sharpness alone therefore does not show that a reconstruction is accurate" (`:138`). The output image keeps a PSF border that you must crop, and it is in exposure-time-normalised units (`:122`).
- **Evidence:** a run directory holding `config.yaml` (resolved), `summary.json` (backend, device, dtype, version, input store, region, saved paths, `trace_summary`, timings), `artifacts/image.npy` and `trace/`. `evaluate-reconstruction` also writes `evaluation/evaluation_summary.json` (`:117-120`, `:247`).

### xRay: X-ray detector traces (`G/xray-traces.qmd`)
- **For:** pump-probe experiments. It turns laser-on and laser-off detector frame stacks into a trace over delay, then fits that trace as a sum of damped oscillations, optionally for every detector row.
- **Input:** a laser-on and laser-off pair of HDF5 files in one layout. `cropped-cube` holds `imgs` `(frame, y, x)`, `scan_var`, `i0`, `i0_ipm3`, `bin_count` (each `(frame,)`) and `ROI`. `legate-cube` holds `jungfrau1M_data` etc. Both files need the same frame shape and the same delays (`:38-49`; `docs/xray/README.md:157-161`).
- **First run:** `cuphoton xray doctor` (`:21`). Then `probe_hdf5_pair(...)` or `cuphoton xray data-probe` (`:86`, `:321`).
- **Needs:** the CPU profile (NumPy, h5py) for trace fitting. The default `detector-artifacts` backend needs the `gpu` profile, CuPy and a GPU. The structured backends need the native extension (`CUPHOTON_XRAY_BUILD_EXT=1`, Linux, C++17). `phonon-viz` needs `viz` (`:7-8`, `:325-330`).
- **Silent trap:** "A fast mode is missing from the fit… This can discard high-frequency modes even without noise" (`:329`). Also, `--components` defaults to 30, not the order the sweep chose (`:210`). Detector fits smooth and integrate, so they "differ from a fit of the tile trace" (`:190`). The fit assumes uniformly increasing delays: "check that condition" (`:111`).
- **Evidence:** `manifest.json` (inputs, ROI, settings, fit and failure counts), `fit_status.npy` (0 not processed, 1 fitted, 2 skipped, 3 failed) and `fit_diagnostics.npz` (`:218-224`). `extract-trace` writes an NPZ with a `summary` entry (`:304`).

### xBeam: correlate (`G/correlate.qmd`)
- **For:** measures how much two recordings of one source share, and at what delay, frequency by frequency (cross-spectra and lag correlations). Examples: two microphones, two radio telescopes.
- **Input:** uniformly sampled signals on one time grid. Use NumPy/CuPy vectors via `ArraySource`, or 1-D HDF5 datasets with scalar `sample_rate_hz` and `origin_seconds` attributes via `Hdf5Source` (`:9`, `:36-42`, `:123`). Radio path: a JSON job or DiFX `.input` file, plus file-backed, two-bit, non-legacy VDIF recordings with oversampling and decimation factors of one (`:251-254`).
- **First run:** `correlate_series(source, spec)` (`:52`). CLI: `cuphoton xbeam correlate-series series.json --output results.h5 --backend numpy` (`:224`). Radio: `cuphoton xbeam inspect-vdif AA.vdif --json` (`:260`).
- **Needs:** no extra on CPU. The GPU path needs `gpu` (or `io`) plus a GPU. `io_backend="cufile"` needs working GPUDirect Storage. `build-vdif-sidecar` defaults to `cufile`, so pass `--backend posix` without GDS (`:7-8`, `:199`, `:269`).
- **Silent trap:** "The lag peak is at the wrong place. The delay can exceed the window" (`:289`). Products are raw: "xBeam applies no taper, mean removal or normalization" (`:68`). "Do not average shard outputs" (`:161`).
- **Track:** Module 07, "Two receivers, one signal", teaches xBeam end to
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
