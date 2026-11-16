---
id: "3.3"
title: Read straight to the GPU
question: Can a FITS file go straight onto the GPU, and how would you know if it didn't?
terms: [FITS reader]
---

In 2.4 you saw that reading a file and computing on it are separate choices,
each recorded in the receipt. cuPhoton's reading function,
`read_fits_images`, takes two settings: `device=True` asks for the image to
end up in GPU memory, and `reader` chooses the [[FITS reader]]: `astropy`, the
standard library, which decodes on the CPU; `xdr`, cuPhoton's own reader, which
can decode on the GPU itself; or `auto`, which uses xDR when it can.

xDR's GPU decoding is compiled code that has to be built when cuPhoton is
installed. Our GPU environment installed cuPhoton's `gpu` extra.

:::your-turn three-reads
title: Three ways to read
prompt: The tutor will read the sample target three ways: with device=True and reader auto, with device=True and reader xdr, and with device=False. For each, predict which reader runs and where the image ends up, or whether it fails. Then ask it to run them and show you the read receipts.
:::

:::closure
found: With reader auto and device=True, the image did end up on the GPU, but Astropy read it on the CPU and copied it across; the receipt says reader astropy, requested auto, location device, and gives the fallback reason: xDR's GPU parts aren't available. Asking for xdr by name failed with that reason. The gpu extra doesn't build xDR; that's a separate step.
matters: "It's on the GPU" doesn't mean "it was read on the GPU". For a few images it makes no difference; for a survey streaming terabytes, decoding on the CPU and copying can be the slowest part of the whole pipeline. The receipt's reader, location and fallback_reason fields are how you'd find out, and auto versus a named reader follows the same rule you learned for backends.
raises: Everything ran on the GPU. So how much faster is it?
:::
