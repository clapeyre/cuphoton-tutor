#!/bin/bash
# Make the GPU environment Module 03 onward uses: cuPhoton (the pinned checkout) with its gpu and catalog
# extras, the transient-chain example (Module 05), and Matplotlib for figures, in .envs/cuphoton-gpu. A few GB; needs network once.
#   tools/setup-gpu-env.sh [cuPhoton checkout]
set -euo pipefail
cd "$(dirname "$0")/.."
repo=$(pwd)
checkout=${1:-${CUPHOTON_DIR:-$HOME/cuphoton-overnight/cuPhoton}}
env_dir="$repo/.envs/cuphoton-gpu"
(cd "$checkout" && UV_PROJECT_ENVIRONMENT="$env_dir" uv sync --locked --inexact --extra gpu --extra catalog --no-dev)
uv pip install --python "$env_dir/bin/python" matplotlib==3.11.2 -e "$checkout/examples/transient-chain"
"$env_dir/bin/python" -c "import cupy as cp, cuphoton, pandas, pyarrow, transient_chain; a = cp.arange(10); cp.cuda.Device().synchronize(); print('GPU environment ready: cupy', cp.__version__, '· cuphoton', cuphoton.__version__)"
