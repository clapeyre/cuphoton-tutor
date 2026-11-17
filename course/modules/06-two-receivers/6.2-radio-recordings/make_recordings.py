"""6.2: three radio stations record one patch of noise-like sky; write their VDIF recordings and the job.

    python make_recordings.py <out dir> [--seconds N]

Run it from the course folder, not a copy: it holds the answer (the tutor reads it; the learner
shouldn't find it in their Files panel). Writes AA.vdif, BB.vdif, CC.vdif (two-bit, real sampling,
16 MHz, one 8 MHz band at 1.4 GHz) and job.json, a normalized xBeam job (schema version 1) whose
delay models are right and whose station clocks are all zero.

The truth: the wavefront reaches CC 0.9 us before AA and BB 2.3 us after AA (the job has these, in
its own sign convention), and BB's clock is also off: its samples are stamped 1.75 us late. The
job doesn't know about BB's clock. Each station records 20% sky and 80% receiver noise.
"""
import json
import pathlib
import sys

import numpy as np

out = pathlib.Path(sys.argv[1])
SECONDS = int(sys.argv[sys.argv.index("--seconds") + 1]) if "--seconds" in sys.argv else 1
out.mkdir(parents=True, exist_ok=True)
FS, PAYLOAD = 16_000_000, 8000                 # samples per second, payload bytes per frame
SPF = PAYLOAD * 4                               # two-bit samples per frame
LATE = {"AA": 0.0, "BB": 2.3e-6, "CC": -0.9e-6}  # geometric: when the wavefront arrives, after AA (s)
CLOCK = {"AA": 0.0, "BB": 1.75e-6, "CC": 0.0}   # extra lateness of the station's own clock (s)
RHO = 0.2

rng = np.random.default_rng(7)
n = FS * SECONDS
f = np.fft.rfftfreq(n, 1 / FS)
sky = np.fft.rfft(rng.normal(size=n))
for name in LATE:
    late = np.fft.irfft(sky * np.exp(-2j * np.pi * f * (LATE[name] + CLOCK[name])), n)
    x = np.sqrt(RHO) * late + np.sqrt(1 - RHO) * rng.normal(size=n)
    code = np.digitize(x / x.std(), [-0.98, 0.0, 0.98]).astype(np.uint8)   # offset binary, optimal 2-bit levels
    packed = (code[0::4] | code[1::4] << 2 | code[2::4] << 4 | code[3::4] << 6).astype(np.uint8)
    station = (ord(name[0]) << 8) | ord(name[1])
    with open(out / f"{name}.vdif", "wb") as fh:
        for k in range(n // SPF):
            second, number = divmod(k, FS // SPF)
            # VDIF header: seconds from the 2020-01-01 epoch (40); frame number; length in 8-byte units;
            # station code and two bits per sample (bits-1 in bits 26-30).
            words = [second, number | (40 << 24), (32 + PAYLOAD) // 8, station | (1 << 26), 0, 0, 0, 0]
            fh.write(np.asarray(words, dtype="<u4").tobytes())
            fh.write(packed[k * PAYLOAD:(k + 1) * PAYLOAD].tobytes())

names = list(LATE)
ident = {nm: i for i, nm in enumerate(names)}
zero = {"mjd": 58849, "seconds_of_day": 0}
job = {
    "schema_version": 1, "start_time": zero, "execution_duration_s": SECONDS,
    "integration_duration_s": 0.2, "subintegration_duration_s": 0.02, "fringe_approximation_order": 0,
    "stations": [{"identifier": ident[nm], "name": nm, "clock": {"epoch": zero, "coefficients_s": [0.0]}} for nm in names],
    "frequencies": [{"identifier": 0, "band_edge_hz": 1.4e9, "bandwidth_hz": FS / 2, "sideband": "USB", "channel_count": 128}],
    "datastreams": [{"identifier": ident[nm], "station_id": ident[nm], "sampling": "real", "quantization_bits": 2,
                     "frame_size_bytes": 32 + PAYLOAD, "source_files": [f"{nm}.vdif"], "sample_rate_hz": FS,
                     "recorded_bands": [{"identifier": 0, "frequency_id": 0, "polarization": "R"}]} for nm in names],
    "baselines": [{"identifier": k, "datastream_a_id": ident[a], "datastream_b_id": ident[b],
                   "products": [{"band_a_id": 0, "band_b_id": 0, "output_frequency_id": 0}]}
                  for k, (a, b) in enumerate([("AA", "BB"), ("AA", "CC"), ("BB", "CC")])],
    # The job's delay is how much EARLIER the station hears the wavefront than the reference (DiFX's sign).
    "scans": [{"identifier": "scan1", "start_offset_s": 0, "duration_s": SECONDS, "source_id": "SKY", "configuration_id": "c0",
               "station_models": [{"station_id": ident[nm], "epoch_offset_s": 0, "delay_coefficients_s": [-LATE[nm]],
                                   "u_coefficients_m": [0.0], "v_coefficients_m": [0.0], "w_coefficients_m": [0.0]}
                                  for nm in names]}],
    "write_autocorrelations": True, "output": {"format": "xbeam-v1"},
}
(out / "job.json").write_text(json.dumps(job, indent=2) + "\n")
print(f"wrote {', '.join(f'{nm}.vdif' for nm in names)} ({SECONDS} s each, {n * 2 // 8 / 1e6:.0f} MB) and job.json in {out}")
