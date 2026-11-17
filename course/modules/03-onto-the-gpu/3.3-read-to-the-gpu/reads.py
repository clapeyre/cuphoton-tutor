"""3.3: read the sample target three ways, then compressed two ways, and print each read's receipt.

    python reads.py <sample/target.fits>        (GPU environment; writes two compressed copies next to it)
"""
import os
import sys
import warnings

warnings.simplefilter("ignore")
import numpy as np
from astropy.io import fits
from cuphoton.core.arrays import array_module
from cuphoton.core.fits_io import inspect_fits_images, read_fits_images

f = sys.argv[1]


def show(label, path, hdu, **kw):
    try:
        r = read_fits_images(path, [hdu], **kw)
    except Exception as e:  # a named reader that can't run raises before it reads a pixel
        print(f"{label:34s} -> {type(e).__name__}: {e}")
        return None
    m = r.metadata()
    print(f"{label:34s} -> {array_module(r.arrays[0]).__name__:5s} reader {m['reader']}, requested {m['requested_reader']}, "
          f"location {m['location']}, fallback_reason {m['fallback_reason']!r}")
    a = r.arrays[0]
    return a.get() if hasattr(a, "get") else a


print("-- the plain file")
show("device=True,  reader='auto'", f, 0, device=True, reader="auto")
show("device=True,  reader='xdr'", f, 0, device=True, reader="xdr")
show("device=False (default reader)", f, 0)

orig = fits.getdata(f).astype(np.float32)
hdr = fits.getheader(f)
base = f[:-5]
copies = {"astropy default": (f"{base}-default.fits", {}),
          "GZIP_2, lossless": (f"{base}-gzip2.fits", dict(compression_type="GZIP_2", quantize_level=0))}
sky = 1.4826 * np.median(np.abs(orig - np.median(orig)))
print(f"\n-- compressed copies (original {os.path.getsize(f):,} bytes; sky noise {sky:.1f} counts)")
for name, (path, kw) in copies.items():
    fits.HDUList([fits.PrimaryHDU(), fits.CompImageHDU(orig, header=hdr, **kw)]).writeto(path, overwrite=True)
    info = inspect_fits_images(path)[0]
    print(f"\n{name}: {path}, {os.path.getsize(path):,} bytes, compression {info.compression}, "
          f"xdr_unsupported_reason {info.xdr_unsupported_reason!r}")
    a = show("device=True, reader='auto'", path, 1, device=True, reader="auto")
    show("device=True, reader='xdr'", path, 1, device=True, reader="xdr")
    d = np.abs(a - orig)
    print(f"{'pixels vs the original':34s} -> identical: {bool(np.all(d == 0))}, max |change| {d.max():.3f}, rms {np.sqrt(np.mean(d ** 2)):.3f}")
