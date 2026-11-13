"""Data for v0: the course's synthetic pair -> v0.npz.  Usage: python data_v0.py <sample_dir> [<outdir>]
sample_dir holds reference.fits and target.fits (tools/make_sample.py). Only needs numpy + astropy."""
import os, sys
from pathlib import Path
import numpy as np
from astropy.io import fits

sd = Path(sys.argv[1]); out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(os.environ.get("VIDEO_DATA", Path(__file__).resolve().parents[1] / "renders" / "data"))
ref = fits.getdata(sd / "reference.fits").astype(float); tgt = fits.getdata(sd / "target.fits").astype(float)
# a modest isolated star in the reference for the pixel-grid zoom
from scipy.ndimage import maximum_filter
bg = np.median(ref)
cand = np.argwhere((ref == maximum_filter(ref, 9)) & (ref > bg + 150) & (ref < bg + 900))
cand = [c for c in cand if 30 < c[0] < ref.shape[0] - 30 and 30 < c[1] < ref.shape[1] - 30]
y, x = cand[len(cand) // 2]
crop = np.rint(ref[y - 4:y + 5, x - 4:x + 5]).astype(int)
out.mkdir(parents=True, exist_ok=True)
np.savez(out / "v0.npz", ref=ref, tgt=tgt, crop=crop, star=np.array([y, x]))
print("star", y, x, "crop range", crop.min(), crop.max())
