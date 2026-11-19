---
id: "4.1"
title: Meet the data
question: What's different about real survey data, and what does it change in the pipeline?
terms: [mask, variance plane, PSF]
guide: [read-fits]
---

Our data comes from **Pan-STARRS1**, a 1.8 m survey telescope in Hawaii that
imaged three quarters of the sky many times between 2010 and 2014. We have two
nights, 2011 April 22 and 2012 April 12, through the same red filter, of a
200″ × 200″ patch of the galaxy M101. For each night there are three files,
as the survey delivers them: the image, a variance map and a bit mask.
([Data credit](https://outerspace.stsci.edu/display/PANSTARRS/): Pan-STARRS1,
via the archive at STScI.)

Every survey prepares its images its own way, and writes it down in the FITS
headers. Before running anything on new data, you find out what was already
done to it, and which of your recipes still hold.

:::your-turn what-differs
title: What's different?
prompt: Ask the tutor about the files: headers, pixel values, masks, anything. Compared with the Module 01 pair ([1.1](#/1.1)), what was already done to these images, and what does each difference change in how we run the chain?
:::

:::your-turn noise-model
title: An honest noise model
prompt: In Module 01 ([1.2](#/1.2)) we made the variance as pixel value divided by gain. What would that give here, and what will you use instead? How would you check that your choice is right?
:::

:::closure
found: The survey already did several things: both nights are resampled onto the same sky grid (so alignment has nothing left to do), the sky has been subtracted (empty sky sits near zero), bad pixels are flagged with named bits, and each image comes with its own variance map. Module 01's recipe would put the noise of empty sky at about 1 count², where the real scatter is about 175: more than a hundred times too small. In our reference measurement, on empty-sky corners, the survey's variance map matched the scatter on the target (173 against 174 count²) and ran about 15% low on the reference (151 against 179). Where you call the sky empty moves these numbers: let in the galaxy's outskirts and the scatter grows.
matters: The recipes in tutorials are written for their data. A sky-subtracted image still carries the sky's noise; a mask's bits mean what that survey says they mean; a header's numbers apply to the product they came with. The habit is the same for any instrument: read what was done to the data, then check every assumption against the pixels themselves.
raises: With the noise model and masks settled, run the chain. What comes out?
:::
