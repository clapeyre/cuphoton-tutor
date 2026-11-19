---
id: "3.3"
title: Read straight to the GPU
question: Can a FITS file go straight onto the GPU, and how would you know if it didn't?
terms: [FITS reader]
guide: [read-fits]
---

In 2.4 you saw that reading a file and computing on it are separate choices,
each recorded in the receipt. cuPhoton's reading function,
`read_fits_images`, takes two settings: `device=True` asks for the image to
end up in GPU memory, and `reader` chooses the [[FITS reader]]: `astropy`, the
standard library, which decodes on the CPU; `xdr`, cuPhoton's own reader, which
decodes on the GPU itself; or `auto`, which uses xDR when it can.

xDR's GPU decoding is compiled code. Installing cuPhoton's `gpu` extra doesn't
build it; our GPU environment builds it as a separate step.

:::your-turn three-reads
title: Three ways to read
prompt: The tutor will read the sample target three ways: with device=True and reader auto, with device=True and reader xdr, and with device=False. For each, predict which reader runs and where the image ends up, or whether it fails. Then ask it to run them and show you the read receipts.
:::

:::your-turn compressed
title: The same image, compressed
prompt: Survey archives usually store their images compressed. The tutor will save the sample target twice more, compressed with Astropy's default settings and compressed losslessly with GZIP_2, then read each with reader auto and device=True. For each, predict which reader runs, and whether the pixels come back exactly as in the original. If you have nothing to go on for a file, say what you would look at to find out.
:::

:::closure
found: xDR read the plain file into GPU memory, with reader auto or xdr, and with device=False Astropy read it into ordinary memory, since astropy is the default, not auto. Compressed, the results split. The GZIP_2 copy was 10% smaller, xDR read it on the GPU, and every pixel matched. Astropy's default compression made a file 3.4 times smaller, but xDR can't decode it (RICE_1, with the floats quantized), so auto fell back to Astropy without an error. Only the receipt said so. And the pixels had changed, by up to 0.3 counts against a sky noise of 8: Astropy rounds floats before it compresses them. Small, but not the same image.
matters: "It's on the GPU" doesn't mean "it was read on the GPU". A file format your reader can't decode makes auto fall back quietly, for every file of a survey that stores them that way. For a few images that costs nothing; for a survey streaming terabytes, decoding on the CPU and copying can be the slowest part of the whole pipeline. The receipt's reader and fallback_reason are how you'd find out, and naming the reader turns the fallback into an error you can't miss.
raises: The read, the alignment and the subtraction can all run on the GPU now. So how much faster is it?
:::
