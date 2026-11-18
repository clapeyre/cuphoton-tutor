# cuPhoton Learn as a Brev launchable

How to publish the course as an NVIDIA Brev launchable: one GPU instance per
learner, the course on a secure link, the learner's own model key entered on
the page. Brev's options are described in its docs
(https://docs.nvidia.com/brev/concepts/launchables); what's below is what
this course needs from them.

## Settings

- **Compute:** VM mode (not a container), Ubuntu with NVIDIA drivers and
  CUDA. A GPU with at least 16 GB: the course was built on an RTX 4070 Ti
  SUPER (16 GB). **At least 4 vCPUs and 16 GB of RAM** (the g4dn.xlarge
  below is the one configuration the course has been run on; the default
  1 to 2 vCPU, 1.8 to 3.7 GB T4 shapes are too small: the server, the tutor
  and a CUDA Python process run together, and the install builds the page
  and xDR's reader). 8 GB is untested; the floor is not a measured one.
  Disk: 60 GB or more (the two Python environments take about
  15 GB, plus the checkout, the course data and the learner's work).
- **Code:** "I have code files in a git repository":
  `https://github.com/clapeyre/cuphoton-tutor` (public).
- **Setup script:** `tools/brev-setup.sh`, which clones the course, runs
  `tools/install.sh` (starting the server) and adds an `@reboot` line. Paste
  it, or this, which fetches it:

  ```bash
  #!/bin/bash
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/clapeyre/cuphoton-tutor/main/tools/brev-setup.sh)"
  ```

  If Brev clones the repository itself, run `tools/brev-setup.sh` from that
  clone with `CUPHOTON_LEARN_DIR` set to it.
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
3. The server listens on Brev's mesh address (interface `wt0`, NetBird),
   which is how the secure link's proxy reaches the instance: not on
   127.0.0.1 (the proxy gets a 503) and not on the public interface.
   `tools/serve.sh` looks the address up at each start, waiting for the mesh
   at boot; `HOST` in the environment or `.env` overrides it.

## Tested on a Brev T4 (18 Nov)

`g4dn.xlarge` (AWS, Tesla T4 16 GB, 4 vCPUs, 16 GB RAM, Ubuntu 22.04,
$0.63/h), setup script above run as is:

- **Install time: about 5 minutes** from a cold instance (307 s), every
  smoke check passing: CuPy and PyTorch on the T4, xDR's reader built.
  A second run takes about a minute (each step skips what's there).
- **Passwordless sudo: yes**, so xDR's build tools install.
- **Reboot: the server comes back** (the `@reboot` line), listening within
  a minute of boot.
- **Secure link:** a server on 127.0.0.1 gives a 503 through the link; on
  the mesh address the page, the setup form (a POST) and the tutor's
  WebSocket all work through it, the lock included, and it survives a reboot.
- The first version of the script failed on its last line (an empty crontab
  makes `grep -v` exit 1 under `pipefail`); fixed above.

## Still to check

- That every module runs on a T4 (4.6 trains a classifier with PyTorch; 6.3
  and 8.3 run on the GPU): run the course once there.
