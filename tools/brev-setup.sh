#!/bin/bash
# Set up cuPhoton Learn on a Brev instance: the launchable's setup script, and what
# `brev exec <instance> @tools/brev-setup.sh` runs from a laptop (see README, "Run it").
# Clones the course (or updates it), installs everything, starts the server, and makes it start again
# after a reboot. Safe to run again. The server listens on Brev's mesh address (tools/serve.sh), which is
# what a Brev secure link (`brev ports open <instance> 8765 --protocol http`) reaches.
set -euo pipefail
repo=${CUPHOTON_LEARN_DIR:-$HOME/cuphoton-tutor}
if [ -d "$repo/.git" ]; then
  git -C "$repo" pull --quiet --ff-only || echo "couldn't update $repo; using it as it is"
else
  git clone --quiet https://github.com/clapeyre/cuphoton-tutor.git "$repo"
fi
cd "$repo"
tools/install.sh
# Start the server again after a reboot.
({ crontab -l 2>/dev/null || true; } | { grep -vF "$repo " || true; }
 echo "@reboot cd $repo && PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin tools/serve.sh") | crontab -
echo
echo "Done. Open the course through the instance's secure link on port 8765."
