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
  ({ crontab -l 2>/dev/null || true; } | { grep -v cuphoton-tutor || true; }; echo "@reboot cd $HOME/cuphoton-tutor && PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin tools/serve.sh") | crontab -
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

1. Brev's secure link: a Brev sign-in (Pomerium) in front of the port, which
   lets through only the emails the port authorizes (by default whoever
   opened it; `brev ports open … --protocol http --authorize EMAIL` adds
   more, `--public` removes the sign-in). Checked 18 Nov: a request without
   a Brev login is redirected to sign-in and never reaches the server. Note
   that new launchables default to "anyone with the link" for deploying.
2. The course's own lock: the first browser to open it owns it; everything
   else needs its cookie or the access link (`learner/access-link.txt` on the
   instance). This is what actually keeps a shell from being shared.
3. The server listens on 127.0.0.1 unless `HOST` says otherwise.

## Tested on a Brev T4 (18 Nov)

`g4dn.xlarge` (AWS, Tesla T4 16 GB, 4 vCPUs, 16 GB RAM, Ubuntu 22.04,
$0.63/h), setup script above run as is:

- **Install time: about 5 minutes** from a cold instance (307 s), every
  smoke check passing: CuPy and PyTorch on the T4, xDR's reader built.
  A second run takes about a minute (each step skips what's there).
- **Passwordless sudo: yes**, so xDR's build tools install.
- **Reboot: the server comes back** (the `@reboot` line), listening within
  a minute of boot.
- The first version of the script failed on its last line (an empty crontab
  makes `grep -v` exit 1 under `pipefail`); fixed above.

## Still to check

- Does the secure link reach a server on 127.0.0.1, or does it need
  `HOST=0.0.0.0`? This needs a signed-in browser. If the page doesn't load,
  set `HOST=0.0.0.0` in `.env` and run `tools/serve.sh` (the access lock
  still applies).
- That every module runs on a T4 (4.6 trains a classifier with PyTorch; 6.3
  and 8.3 run on the GPU): run the course once there.
