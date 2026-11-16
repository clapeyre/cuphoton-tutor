"""Turn every item of one or more transient-chain runs into an xLens sample, and export the dashboard.

    python watch_runs.py <state-dir> <report.html> <run-output-dir> [<run-output-dir> ...]

Each item's summary.json (out/items/<item>/summary.json) becomes one sample: what the run
measured, plus findings for the problems that don't stop a run but should stop a reader.
"""
import json
import shutil
import sys
from pathlib import Path

import pandas as pd
from cuphoton.core.artifacts import file_sha256
from cuphoton.xlens import Artifact, Dashboard, Finding, Measurement, Monitor, Sample

state_dir, report, runs = Path(sys.argv[1]), Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]]
items = sorted(p.resolve() for run in runs for p in run.glob("items/*/summary.json"))
base = Path.cwd()


def analyze(path: Path) -> Sample:
    s = json.loads(path.read_text())
    catalog = pd.read_parquet(path.parent / "catalog.parquet")
    x = s["diagnostics"]["xpois"]
    chi2_dof = x["chi2"] / x["dof"] if x.get("dof") else None
    corr = (s["uq"].get("correlation") or {}).get("measured", {}).get("psf_flux")
    reads = s["diagnostics"]["read"].get("receipts", [])
    fallbacks = [r.get("fallback_reason") for r in reads if r.get("fallback_reason")]
    uq_rate = float(catalog["uq_valid"].mean()) if len(catalog) else None
    findings = []
    excluded = s["uq"].get("excluded", {})
    if any("PSF width" in why for why in excluded.values()):
        findings.append(Finding("no_psf_width", "No PSF width: psf_flux is NaN and the error budget is fit-only. Set xfit.psf_sigma_px.",
                                category="processing", severity="error"))
    if chi2_dof is not None and chi2_dof > 3:
        findings.append(Finding("kernel_fit_poor", f"Kernel fit chi2/dof {chi2_dof:.1f} on {x['fit_pixel_count']} pixels: fluxes may be biased.",
                                category="data_quality", severity="error"))
    if uq_rate is not None and uq_rate < 0.8:
        findings.append(Finding("uq_valid_low", f"Only {uq_rate:.0%} of rows have a full error budget.", category="data_quality"))
    if fallbacks:
        findings.append(Finding("read_fallback", "; ".join(sorted(set(fallbacks))), category="processing", severity="info"))
    return Sample(
        id=f"{path.parts[-4]}/{path.parent.name}",
        sequence=items.index(path),
        measurements={
            "candidates": Measurement(len(catalog)),
            "kernel_chi2_dof": Measurement(chi2_dof),
            "kernel_fit_pixels": Measurement(x.get("fit_pixel_count"), "px"),
            "corr_factor_psf_flux": Measurement(corr, status="valid" if corr is not None else "unavailable"),
            "uq_valid_fraction": Measurement(uq_rate),
            "wall": Measurement(s.get("wall_sec"), "s"),
        },
        findings=tuple(findings),
        metadata={"uq_terms": s.get("uq_terms"), "psf_sigma_source": s.get("psf_sigma_source"), "config_sha256": s.get("config_sha256")},
        artifacts=(Artifact("summary", str(path.relative_to(base)), file_sha256(path), "application/json"),),
    )


shutil.rmtree(state_dir, ignore_errors=True)  # a new monitor needs an empty directory
monitor = Monitor(state_dir, run_id="m101-chain")
monitor.replay(items, analyze)
for sample in monitor.samples:
    print(f"{sample.id:45s} {sample.measurements['kernel_chi2_dof'].value or float('nan'):6.2f}  {[f.code for f in sample.findings]}")
print("ingestion errors:", monitor.snapshot()["errors"])
print("report:", Dashboard(monitor, title="Transient chain on M101").export(report))
