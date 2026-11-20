// cuPhoton's install checks, run by the engine's smoke test (tools/smoke.ts) after its own
// (course parses, product checkout pinned, nvidia-smi). Each course supplies its own: the
// environments its lessons need and what each lesson assumes about them.
import { spawnSync } from "node:child_process";
import path from "node:path";

type Report = (name: string, detail: string) => void;
export default function checks({ ok, bad, warn, config }: { ok: Report; bad: Report; warn: Report; config: { pythonBin: string; productDir: string; gpuPythonBin: string } }) {
  // The learner's Python: NumPy, Matplotlib, cuPhoton.
  const pyBin = config.pythonBin || path.join(config.productDir, ".venv", "bin");
  const py = path.join(pyBin, "python");
  const r = spawnSync(py, ["-c", "import numpy, matplotlib, scipy, cuphoton; print(cuphoton.__version__)"], { encoding: "utf8" });
  r.status === 0 ? ok("python", `${py} · cuphoton ${r.stdout.trim()}`) : bad("python", (r.stderr || r.error?.message || "").trim().split("\n").pop() ?? "");

  // Modules 00–02 expect the default environment to have no usable GPU; Module 03 on uses the GPU environment.
  const cupyCpuEnv = spawnSync(py, ["-c", "import cupy"], { encoding: "utf8" });
  cupyCpuEnv.status === 0 ? warn("default env", `${py} has CuPy: Module 02's fallback lessons assume it doesn't`) : ok("default env", "CPU only, as Modules 00–02 expect");
  const gpy = path.join(config.gpuPythonBin, "python");
  const cupy = spawnSync(gpy, ["-c", "import cupy as cp, cuphoton; a=cp.arange(10); cp.cuda.Device().synchronize(); print(int(a.sum()))"], { encoding: "utf8" });
  cupy.status === 0 && cupy.stdout.trim().endsWith("45") ? ok("gpu env", `${gpy} · CuPy runs on the GPU`) : bad("gpu env", `not usable (${gpy}); run tools/setup-gpu-env.sh. Needed from Module 03.`);
  const chain = spawnSync(gpy, ["-c", "import transient_chain, pandas, pyarrow, cuphoton.xlens"], { encoding: "utf8" });
  chain.status === 0 ? ok("chain", "transient chain, catalog extra and xLens in the GPU env") : bad("chain", `missing in ${gpy}; rerun tools/setup-gpu-env.sh. Needed for Module 05.`);
  const xdr = spawnSync(gpy, ["-c", "from cuphoton.xdr.nvcomp_batch import cpp_helper_available as a; import torch; print(a(), torch.cuda.is_available())"], { encoding: "utf8" });
  const [xdrOk, torchGpu] = xdr.stdout.trim().split(" ");
  xdrOk === "True" ? ok("xdr", "native GPU FITS reader built") : ok("xdr", `NOT built: reads fall back to Astropy; 3.3 teaches the fallback (rerun tools/setup-gpu-env.sh, see ${gpy.replace(/bin\/python$/, "xdr-build.log")})`);
  torchGpu === "True" ? ok("xscan", "PyTorch sees the GPU (4.6 trains on it)") : bad("xscan", `PyTorch can't see a GPU in ${gpy}; needed for 4.6.`);
  const tracks = spawnSync(gpy, ["-c", "import cuphoton.ximage.workflows, cuphoton.xray.detector_artifacts, cuphoton.xbeam, h5py"], { encoding: "utf8" });
  tracks.status === 0 ? ok("tracks", "xBeam, xRay and xImage (ximage extra) import in the GPU env") : bad("tracks", `an import failed in ${gpy}; rerun tools/setup-gpu-env.sh. Needed for Modules 06-08.`);
}
