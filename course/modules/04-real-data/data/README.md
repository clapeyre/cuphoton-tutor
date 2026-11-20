# Data: SN 2011fe in M101, Pan-STARRS1 r band

Single-night Pan-STARRS1 (PS1) "warp" images of the same 200″ × 200″ patch
of M101, from PS1 DR2 via the STScI cutout service, with the survey's own
variance maps (`.var`) and bit masks (`.mask`). `../prepare_data.py` rebuilds
them.

| file | night | MJD | days from explosion |
|---|---|---|---|
| reference*.fits | 2011-04-22 | 55673.44 | −123 |
| target*.fits | 2012-04-12 | 56029.51 | +233 |
| reference-b*.fits | 2011-04-22 | 55673.45 | −123 (for stacking, 4.5) |
| reference-c*.fits | 2011-05-11 | 55692.33 | −104 (for stacking, 4.5) |

Changes from what the service delivers: masks are integers with 0 = good (the
service gives NaN for 0), and pixels with no data carry the BLANK bit (8).

Credit: The Pan-STARRS1 Surveys (PS1) and the PS1 public science archive have
been made possible through contributions by the Institute for Astronomy, the
University of Hawaii, the Pan-STARRS Project Office, the Max Planck Society and
its participating institutes, and many others; see
https://outerspace.stsci.edu/display/PANSTARRS/ for the full acknowledgement.
Chambers et al. 2016, arXiv:1612.05560.
