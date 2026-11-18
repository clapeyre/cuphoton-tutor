# cuPhoton Learn as a Brev launchable

How to publish the course as an NVIDIA Brev launchable: one GPU instance per
learner, the course on a secure link, the learner's own model key entered on
the page. Brev's options are described in its docs
(https://docs.nvidia.com/brev/concepts/launchables); what's below is what
this course needs from them.

## Settings

- **Compute:** VM mode (not a container), Ubuntu with NVIDIA drivers and
  CUDA. A GPU with at least 16 GB: the course was built on an RTX 4070 Ti
  SUPER (16 GB). Disk: 60 GB or more (the two Python environments take about
  15 GB, plus the checkout, the course data and the learner's work).
- **Code:** "I have code files in a git repository":
  `https://github.com/clapeyre/cuphoton-tutor` (public).
- **Setup script:**

  ```bash
  #!/bin/bash
  set -euo pipefail
  [ -d ~/cuphoton-tutor ] || git clone https://github.com/clapeyre/cuphoton-tutor.git ~/cuphoton-tutor
  cd ~/cuphoton-tutor
  tools/install.sh
  # Start the server again after a reboot.
  (crontab -l 2>/dev/null | grep -v cuphoton-tutor; echo "@reboot cd $HOME/cuphoton-tutor && PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin tools/serve.sh") | crontab -
  ```

  If Brev clones the repository itself, point the script at that folder
  instead of cloning again.
- **Network:** one **secure link** on port **8765**, named "cuPhoton Learn",
  shown as the call to action. Do **not** also open 8765 as a TCP port: the
  tutor runs shell commands on the instance.

## What the learner does

1. Deploys the launchable and waits for the setup script (see "To check",
   below, for how long).
2. Opens the secure link. Their browser now owns the course: other browsers
   get a "this course is open in another browser" page (`server/access.ts`).
3. The setup page asks for the tutor's model: Anthropic API, NVIDIA API
   catalog, NVIDIA inference hub, or any OpenAI-compatible server. One test
   call, then the course opens. The key stays on the instance, in
   `learner/endpoint.json`.
4. To use another device: the admin page (the "Admin" link) copies the
   access link.

## Access, in layers

1. Brev's secure link: Brev authentication in front of the port. The docs
   don't say who passes it (the deployer, their organization, anyone signed
   in), and new launchables default to "anyone with the link".
2. The course's own lock: the first browser to open it owns it; everything
   else needs its cookie or the access link (`learner/access-link.txt` on the
   instance). This is what actually keeps a shell from being shared.
3. The server listens on 127.0.0.1 unless `HOST` says otherwise.

## To check on the first real launchable

- Does the secure link reach a server on 127.0.0.1, or does it need
  `HOST=0.0.0.0`? If the page doesn't load, set `HOST=0.0.0.0` in `.env` and
  run `tools/serve.sh` (the access lock still applies).
- How long `tools/install.sh` takes on a fresh instance. It passed end to
  end on the author's machine from a fresh clone (18 Nov: every smoke check,
  xDR built, the setup page and the lock working), but with a warm uv cache,
  so its time says nothing about a cold instance, which downloads several GB.
- Whether the setup script runs with passwordless sudo (for xDR's build
  tools). Without it xDR's GPU reader isn't built, and lesson 3.3 teaches the
  Astropy fallback.
- The smallest GPU that runs every module: run the course once (4.6 trains a
  classifier with PyTorch; 6.3 and 8.3 run on the GPU).
- That a reboot brings the server back (the `@reboot` line).
