---
id: "2.4"
title: A command-line receipt
question: What does a command-line run record, and which choices are separate?
terms: [receipt]
guide: [concepts]
---

Every cuPhoton stage also runs from the command line, and each command-line run
writes a timestamped run directory with its own `summary.json`. For example,
xRep can put one image onto a standard sky grid:

```bash
cuphoton xrep reproject-image --input work/01/sample/target.fits --output-dir work/02/xrep-cli
```

A run involves two separate choices. Reading the FITS file is done by a
**FITS reader** (Astropy on the CPU, or cuPhoton's own reader that can load
straight into GPU memory). The arithmetic is done by the **backend**. The
receipt records each one, both as requested and as actually used.

:::your-turn reader-and-backend
title: Requested and used
prompt: Ask the tutor to run that command, leaving the reader and backend at their defaults (auto), and to show you the receipt. For the FITS reader and for the backend, what was requested, and what actually ran?
:::

:::closure
found: The receipt holds the backend request (auto) and what ran (cpu, on the cpu device), and separately the FITS read: Astropy, on the host, with no fallback reason, plus the image's shape and dtype. Asking for a backend this environment doesn't have (--backend cupy) fails loudly, as in Python, rather than quietly running elsewhere.
matters: Reading the file and doing the arithmetic are separate steps that can land on different hardware. In Module 03, a run can read on the GPU and compute on the CPU, or the reverse, and only these two fields will tell you.
raises: Now you can read receipts. Can you tell, from receipts alone, which of three runs didn't run where it was meant to?
:::
