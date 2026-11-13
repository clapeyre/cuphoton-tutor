"""Real cuPhoton CPU data for v2 (needs v1.npz from data_v1.py in the same outdir).
Saves v2.npz and v2.json: fitted fluxes with converged/uncertainty_valid flags, for the good fit and
for a fit limited to a few iterations, plus the quickstart summary excerpt."""
import json, sys
import numpy as np
from cuphoton.xfit import fit_single_sources
from cuphoton.xpois import window_stamps
from cuphoton.xfit import LMConfig

out = sys.argv[1] if len(sys.argv) > 1 else "."
d = np.load(f"{out}/v1.npz")
tgt = d["target"]; diff = d["difference"]; peaks = d["peaks"]; psf = float(d["psfsig"][1])
tv = np.clip(tgt, 0, None) / 2.0
z = d["z"]
cut = window_stamps(diff, peaks[:, ::-1].astype(float), 21)
var = window_stamps(d["marg_var"], peaks[:, ::-1].astype(float), 21)
valid = np.isfinite(cut) & np.isfinite(var) & (var > 0)
rows = []
for label, cfg in [("full solver", None), ("solver stopped after 3 evaluations", LMConfig(max_evaluations=3))]:
    r = fit_single_sources(cut, var, np.zeros((len(peaks), 2)), psf, mask=valid, **({"solver": cfg} if cfg else {}))
    flux = np.sign(r.parameters[:, 0]) * r.flux
    for p, f, e, c, u in zip(peaks, flux, r.flux_error, r.converged, r.uncertainty_valid):
        rows.append(dict(run=label, y=int(p[0]), x=int(p[1]), flux=float(f), error=float(e), converged=bool(c), uncertainty_valid=bool(u)))
json.dump(rows, open(f"{out}/v2.json", "w"), indent=1)
for r in rows: print(r)
