"""Rebuild data/ from Pan-STARRS1 (PS1) DR2 single-epoch warps: SN 2011fe in M101, r band.

    python prepare_data.py            # needs network once; writes data/*.fits

Reference: 2011-04-22 (MJD 55673.44, 123 days before the explosion).
Target:    2012-04-12 (MJD 56029.51, 233 days after).
Both are 800 x 800 cutouts (0.25"/px) of sky cell 2381.053, from the PS1 cutout
service at STScI (https://ps1images.stsci.edu). For each: the image (counts,
sky-subtracted), the survey's variance map (.wt) and its bit mask (.mask).

Cleaning, nothing else: the cutout service stores mask value 0 (good) as NaN,
so masks are written back as integers with 0 = good, and pixels with no data
(NaN in the image) get the BLANK bit (8). Headers are kept as delivered.
"""
import io
import urllib.request
from pathlib import Path

import numpy as np
from astropy.io import fits

RA, DEC, SIZE = 210.774167, 54.273722, 800
CELL = "/rings.v3.skycell/2381/053/rings.v3.skycell.2381.053.wrp.r"
NIGHTS = {"reference": "55673_43927", "target": "56029_50937"}
out = Path(__file__).parent / "data"
out.mkdir(exist_ok=True)


def cutout(name):
    url = f"https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?ra={RA}&dec={DEC}&size={SIZE}&format=fits&red={CELL}.{name}.fits"
    with urllib.request.urlopen(url, timeout=300) as r:
        return fits.open(io.BytesIO(r.read()))[0]


for role, epoch in NIGHTS.items():
    image, variance, mask = cutout(epoch), cutout(epoch + ".wt"), cutout(epoch + ".mask")
    bits = np.nan_to_num(mask.data, nan=0).astype(np.int32)
    bits[~np.isfinite(image.data)] |= 8  # BLANK: no data
    fits.writeto(out / f"{role}.fits", image.data.astype(np.float32), image.header, overwrite=True)
    fits.writeto(out / f"{role}.var.fits", variance.data.astype(np.float32), variance.header, overwrite=True)
    fits.writeto(out / f"{role}.mask.fits", bits.astype(np.int32), mask.header, overwrite=True)
    print(role, epoch, "written")
