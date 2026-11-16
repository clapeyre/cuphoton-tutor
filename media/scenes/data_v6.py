"""Data for v6 (one image through the shipped chain): runs the transient chain on the Module 04 pair
with Module 05's final configuration, in the GPU environment, and keeps what the video shows.

    python data_v6.py <out dir>     (needs .envs/cuphoton-gpu: gpu + catalog extras + the example)
Writes <out>/chain_run/ and <out>/v6.json.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
data = repo / "course" / "modules" / "04-your-own-data" / "data"
cfg = repo / "course" / "modules" / "05-the-shipped-chain" / "5.1-configure" / "config-ps1.yaml"
gpy = Path(os.environ.get("LEARNER_GPU_PYTHON_BIN", repo / ".envs" / "cuphoton-gpu" / "bin")) / "python"
launch = Path(os.environ.get("CUPHOTON_DIR", Path.home() / "cuphoton-overnight" / "cuPhoton")) / "examples" / "transient-chain" / "launch.py"
sel = out / "chain_selections.json"
sel.write_text(json.dumps({"selections": [{
    "expnum": "m101-2012", "ccdnum": "skycell2381.053", "band": "r",
    "image": str(data / "target.fits"), "mask": str(data / "target.mask.fits"), "variance": str(data / "target.var.fits"),
    "template": str(data / "reference.fits"), "template_mask": str(data / "reference.mask.fits"),
    "template_variance": str(data / "reference.var.fits")}]}))
run = out / "chain_run"
if not (run / "catalog.parquet").exists():
    subprocess.run([str(gpy), str(launch), "--executor", "local", "--selections", str(sel), "--config", str(cfg),
                    "--set", "xfit.psf_sigma_px=1.57", "--set", "subtract.auto_stamp_mask=false",
                    "--output-dir", str(run)], check=True)
code = r'''
import json, sys, pandas as pd
from pathlib import Path
run = Path(sys.argv[1]); s = json.loads(next(run.glob("items/*/summary.json")).read_text())
c = pd.read_parquet(run / "catalog.parquet")
sn = c.loc[((c.x - 402) ** 2 + (c.y - 400) ** 2).idxmin()]
r = s["diagnostics"]["read"]["receipts"][0]
x = s["diagnostics"]["xpois"]
import numpy as np
from astropy.io import fits
t = np.nan_to_num(fits.getdata(sys.argv[2]).astype(float))
np.save(sys.argv[3], t.reshape(200, 4, 200, 4).mean(axis=(1, 3)))  # 800 -> 200 px thumbnail for the scene
print(json.dumps({
    "candidates": int(s["candidates"]), "timings": s["timings_sec"], "transfers": s["transfers"],
    "gpu": s.get("gpu"), "reader": r.get("reader"), "requested_reader": r.get("requested_reader"),
    "fallback": r.get("fallback_reason"), "uq_terms": s["uq_terms"], "chi2_dof": x["chi2"] / x["dof"],
    "sn": {k: (float(sn[k]) if k not in ("candidate_id", "fit_model") else str(sn[k])) for k in
           ("candidate_id", "x", "y", "peak_abs_sigma", "psf_flux", "psf_flux_err_fit", "psf_flux_err",
            "psf_flux_err_corr", "psf_flux_err_kfit", "fit_model", "quality_flags")},
    "rows": c[["x", "y", "sign"]].astype(int).values.tolist(),
}, default=str))
'''
res = subprocess.run([str(gpy), "-c", code, str(run), str(data / "target.fits"), str(out / "v6_target.npy")], check=True, capture_output=True, text=True)
(out / "v6.json").write_text(res.stdout)
print(res.stdout[:800])
