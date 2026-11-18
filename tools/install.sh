#!/bin/bash
# Install cuPhoton Learn on a fresh Linux GPU machine (a Brev launchable's setup script, a lab workstation).
# Safe to run again: each step skips what's already there.
#
#   tools/install.sh            then open the page: it asks for the tutor's model on first visit
#
# What it does, in order (about 15 GB on disk, mostly the two Python environments; network needed):
#   1. checks for an NVIDIA GPU, git and curl; installs uv and Node.js into ~/.local if missing
#   2. tries to install a C++ compiler and CFITSIO (for xDR's GPU FITS reader; optional, needs sudo)
#   3. clones cuPhoton at the commit the course is pinned to (course/course.yaml) into .cuphoton/
#   4. builds the CPU environment Modules 00-02 use (.cuphoton/.venv: no CuPy, CPU PyTorch)
#   5. builds the GPU environment Module 03 on uses (.envs/cuphoton-gpu, tools/setup-gpu-env.sh)
#   6. installs the app and builds the page (npm ci, npm run build)
#   7. runs the smoke test, then starts the server (tools/serve.sh) unless NO_START=1
#
# Environment: CUPHOTON_DIR (default .cuphoton in this repo), PORT (8765), HOST (127.0.0.1; a Brev secure
# link may need 0.0.0.0, see docs/LAUNCHABLE.md), NODE_MAJOR (24).
set -euo pipefail
cd "$(dirname "$0")/.."
repo=$(pwd)
say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
warn() { printf '\033[33mWARNING:\033[0m %s\n' "$*" >&2; }
export PATH="$HOME/.local/bin:$PATH"

say "1. Prerequisites"
command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || warn "no nvidia-smi: Modules 03 on need an NVIDIA GPU"
for c in git curl tar; do command -v $c >/dev/null || { echo "needs $c" >&2; exit 1; }; done
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 sh
fi
uv --version
node_major=${NODE_MAJOR:-24}
if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 22 ]; then
  arch=$(uname -m); case $arch in x86_64) arch=x64 ;; aarch64) arch=arm64 ;; esac
  base="https://nodejs.org/dist/latest-v${node_major}.x"
  file=$(curl -fsSL "$base/SHASUMS256.txt" | awk -v a="linux-$arch.tar.xz" '$2 ~ a"$" {print $2}')
  mkdir -p "$HOME/.local/node"
  curl -fsSL "$base/$file" | tar -xJ -C "$HOME/.local/node" --strip-components=1
  ln -sf "$HOME/.local/node/bin/node" "$HOME/.local/node/bin/npm" "$HOME/.local/node/bin/npx" "$HOME/.local/bin/"
fi
node --version

say "2. Build tools for xDR (optional)"
if command -v apt-get >/dev/null && sudo -n true 2>/dev/null; then
  pkgs=""; command -v g++ >/dev/null || pkgs="build-essential"
  pkg-config --exists cfitsio 2>/dev/null || pkgs="$pkgs libcfitsio-dev pkg-config"
  [ -n "$pkgs" ] && sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq $pkgs || true
else
  echo "no apt or no passwordless sudo: skipping (xDR's reader may not build; lessons fall back to Astropy)"
fi

say "3. cuPhoton at the course's commit"
checkout=${CUPHOTON_DIR:-$repo/.cuphoton}
commit=$(awk '/^ *commit:/ {print $2; exit}' course/course.yaml)
url=$(awk '/^ *repo:/ {print $2; exit}' course/course.yaml)
if [ ! -d "$checkout/.git" ]; then
  git clone --quiet "$url" "$checkout"
fi
if [ "$(git -C "$checkout" rev-parse HEAD)" != "$commit" ]; then
  git -C "$checkout" fetch --quiet origin "$commit" 2>/dev/null || git -C "$checkout" fetch --quiet origin
  git -C "$checkout" -c advice.detachedHead=false checkout --quiet "$commit"
fi
echo "$checkout at $(git -C "$checkout" rev-parse --short HEAD)"

say "4. CPU environment (Modules 00-02)"
# No CuPy here, and a CPU-only PyTorch: Module 02 teaches what happens when the GPU isn't there.
(cd "$checkout" && uv sync --locked --inexact --no-dev --extra ximage --extra catalog)
torch_v=$("$checkout/.venv/bin/python" -c "import torch; print(torch.__version__.split('+')[0])")
if ! "$checkout/.venv/bin/python" -c "import torch, sys; sys.exit(0 if torch.__version__.endswith('+cpu') else 1)"; then
  # The same version as the lock, from PyTorch's CPU index (its "+cpu" build); its dependencies are already there.
  uv pip install --python "$checkout/.venv/bin/python" --reinstall-package torch --no-deps "torch==$torch_v" --index-url https://download.pytorch.org/whl/cpu
fi
uv pip install --python "$checkout/.venv/bin/python" matplotlib==3.11.2
"$checkout/.venv/bin/python" -c "import numpy, scipy, matplotlib, cuphoton, torch; print('CPU environment ready: cuphoton', cuphoton.__version__, '· torch', torch.__version__)"

say "5. GPU environment (Module 03 on)"
tools/setup-gpu-env.sh "$checkout"

say "6. The app"
npm ci --no-audit --no-fund
npm run build --silent

# The server finds the checkout through CUPHOTON_DIR; keep it in .env (the key never goes there: the page asks).
touch .env
grep -q '^CUPHOTON_DIR=' .env || echo "CUPHOTON_DIR=$checkout" >> .env

say "7. Smoke test"
CUPHOTON_DIR=$checkout npm run smoke --silent || warn "a smoke check failed (above). A missing model is expected: the page asks for one."

if [ "${NO_START:-0}" != 1 ]; then
  say "Starting the server"
  CUPHOTON_DIR=$checkout tools/serve.sh
  echo
  echo "Open http://${HOST:-127.0.0.1}:${PORT:-8765} (or the launchable's secure link). The first browser to open it owns the course;"
  echo "the setup page asks for the tutor's model. The access link for other browsers will be in learner/access-link.txt."
fi
