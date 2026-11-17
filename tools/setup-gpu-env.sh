#!/bin/bash
# Make the GPU environment Module 03 onward uses: cuPhoton (the pinned checkout) with its gpu and catalog
# and ximage extras (xImage: PyTorch, pydantic, Zarr) and xDR's native GPU FITS reader (3.3), the transient-chain example (Module 05), and Matplotlib for
# figures, in .envs/cuphoton-gpu. A few GB; needs network once.
#   tools/setup-gpu-env.sh [cuPhoton checkout]
# The xDR build needs a C++17 compiler, the CUDA and cuFile headers (CUDA_HOME, else /usr/local/cuda or
# /opt/cuda) and a thread-safe CFITSIO (docs/components/xdr.md, "Install"). If it fails, everything else
# still works: reads fall back to Astropy, and 3.3's tutor notes say how to teach it that way.
set -euo pipefail
cd "$(dirname "$0")/.."
repo=$(pwd)
checkout=${1:-${CUPHOTON_DIR:-$HOME/cuphoton-overnight/cuPhoton}}
env_dir="$repo/.envs/cuphoton-gpu"
(cd "$checkout" && UV_PROJECT_ENVIRONMENT="$env_dir" uv sync --locked --inexact --extra gpu --extra catalog --extra ximage --no-dev)
uv pip install --python "$env_dir/bin/python" matplotlib==3.11.2 -e "$checkout/examples/transient-chain"
"$env_dir/bin/python" -c "import cupy as cp, cuphoton, pandas, pyarrow, transient_chain; a = cp.arange(10); cp.cuda.Device().synchronize(); print('GPU environment ready: cupy', cp.__version__, '· cuphoton', cuphoton.__version__)"

# xDR's native extension: a separate build, after the sync (which installs cuPhoton without it)
if [[ -z ${CUDA_HOME:-} ]]; then
    for d in /usr/local/cuda /opt/cuda; do [[ -f $d/include/cufile.h || -f $d/targets/x86_64-linux/include/cufile.h ]] && CUDA_HOME=$d && break; done
fi
if CUDA_HOME=${CUDA_HOME:-} PYTHON="$env_dir/bin/python" bash "$checkout/src/cuphoton/xdr/src/build.sh" >"$env_dir/xdr-build.log" 2>&1 \
    && "$env_dir/bin/python" -c "from cuphoton.xdr.nvcomp_batch import cpp_helper_available as a; raise SystemExit(0 if a() else 1)"; then
    echo "xDR native reader built: FITS files can be decoded on the GPU"
else
    echo "WARNING: xDR's native reader did not build (log: $env_dir/xdr-build.log). Reads will fall back to Astropy;" >&2
    echo "         see docs/components/xdr.md, 'Install', in the checkout. Everything else works." >&2
fi
