#!/bin/bash
# Make the GPU environment Module 03 onward uses: cuPhoton (the pinned checkout) with its gpu extra,
# plus Matplotlib for figures, in .envs/cuphoton-gpu. A few GB; needs network once.
#   tools/setup-gpu-env.sh [cuPhoton checkout]
set -euo pipefail
cd "$(dirname "$0")/.."
repo=$(pwd)
checkout=${1:-${CUPHOTON_DIR:-$HOME/cuphoton-overnight/cuPhoton}}
env_dir="$repo/.envs/cuphoton-gpu"
(cd "$checkout" && UV_PROJECT_ENVIRONMENT="$env_dir" uv sync --locked --extra gpu --no-dev)
uv pip install --python "$env_dir/bin/python" matplotlib==3.11.2
"$env_dir/bin/python" -c "import cupy as cp, cuphoton; a = cp.arange(10); cp.cuda.Device().synchronize(); print('GPU environment ready: cupy', cp.__version__, '· cuphoton', cuphoton.__version__)"
