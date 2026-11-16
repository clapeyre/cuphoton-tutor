"""Read an injection test of the transient chain: what came back, and are the error bars honest?

    python injection_figure.py <inj dir> <out.png> <run dir>[=label] [<run dir>[=label]]

<inj dir> holds truth.json from inject_chain.py; each run dir is a launch.py --output-dir run on
inj/selections.json. A fake counts as found when a candidate lies within 3 px. Prints, per flux
level: found, median measured/planted, mean and scatter of the pull against psf_flux_err (the
chain's error bar) and psf_flux_err_fit (xFit's alone). The figure has one row per run: left, the
measured/planted ratio of every found fake; right, the pull histograms against a unit Gaussian.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

inj, out = Path(sys.argv[1]), Path(sys.argv[2])
runs = [(Path(a.split("=")[0]), a.split("=")[1] if "=" in a else Path(a).name) for a in sys.argv[3:]]
truth = json.loads((inj / "truth.json").read_text())


def match(run):
    rows = []
    for exp, t in truth.items():
        cat = next(run.glob(f"items/*v{exp}/catalog.parquet"), None)
        if cat is None:
            continue
        c = pd.read_parquet(cat)
        for x, y, f in zip(t["x"], t["y"], t["flux"]):
            d = np.hypot(c.x - x, c.y - y)
            i = d.idxmin() if len(c) else None
            hit = i is not None and d[i] < 3
            rows.append(dict(f=f, found=hit, m=c.psf_flux[i] if hit else np.nan,
                             e=c.psf_flux_err[i] if hit else np.nan, ef=c.psf_flux_err_fit[i] if hit else np.nan))
    d = pd.DataFrame(rows)
    d["pull"] = (d.m - d.f) / d.e
    d["pull_fit"] = (d.m - d.f) / d.ef
    return d


def mad(p):
    p = p.dropna()
    return 1.4826 * np.median(np.abs(p - np.median(p)))


fig, axes = plt.subplots(len(runs), 2, figsize=(10, 3.4 * len(runs)), squeeze=False)
grid = np.linspace(-5, 5, 200)
for row, (run, label) in enumerate(runs):
    d = match(run)
    print(f"== {label} ({run})")
    for f, g in d.groupby("f"):
        h = g[g.found].dropna(subset=["m", "e"])
        print(f"  {f:6.0f}: found {g.found.sum()}/{len(g)}  measured/planted {np.nanmedian(h.m / f):.3f}  "
              f"pull mean {h.pull.mean():+.2f} scatter {mad(h.pull):.2f} (robust)  "
              f"| fit-only pull scatter {mad(h.pull_fit):.2f}  | quoted/fit {np.median(h.e / h.ef):.2f}")
    ax = axes[row, 0]
    levels = sorted(d.f.unique())
    for k, f in enumerate(levels):
        h = d[(d.f == f) & d.found]
        jitter = np.random.default_rng(k).uniform(-0.15, 0.15, len(h))
        ax.plot(np.full(len(h), k) + jitter, h.m / f, "o", ms=3, color="0.35", alpha=0.6)
        ax.plot([k - 0.3, k + 0.3], [np.nanmedian(h.m / f)] * 2, color="black", lw=2)
    ax.axhline(1, color="0.5", ls="--", lw=1)
    ax.set_xticks(range(len(levels)), [f"{f:.0f}" for f in levels])
    ax.set_ylim(0.6, 1.4)
    ax.set_xlabel("planted flux (counts)")
    ax.set_ylabel("measured / planted")
    ax.set_title(f"{label}: what came back (bar = median)")
    ax = axes[row, 1]
    h = d[d.found].dropna(subset=["pull"])
    ax.hist(h.pull.clip(-5, 5), bins=np.linspace(-5, 5, 41), density=True, color="0.6", label="pull, chain's error bar")
    ax.hist(h.pull_fit.clip(-5, 5), bins=np.linspace(-5, 5, 41), density=True, histtype="step", color="black",
            label="pull, xFit's error alone")
    ax.plot(grid, np.exp(-grid ** 2 / 2) / np.sqrt(2 * np.pi), color="0.2", ls="--", label="honest: mean 0, scatter 1")
    ax.axvline(0, color="0.5", lw=0.8)
    ax.set_xlabel("(measured − planted) / error bar   (clipped at ±5)")
    ax.set_title(f"pull: mean {h.pull.mean():+.2f}, scatter {mad(h.pull):.2f}")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
fig.tight_layout()
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=120)
print("wrote", out)
