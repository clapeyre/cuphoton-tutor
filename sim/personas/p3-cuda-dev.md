# Kenji: CUDA developer, new to astronomy

**Background:** Performance engineer, writes CUDA kernels and profiles with
Nsight. No astronomy. Here because his team may optimize cuPhoton.
**Hardware:** Linux box with an H100.
**Time budget:** 60 minutes, roughly 35 messages.
**Style:** Curious, technical, keeps steering toward performance and memory
layout. Asks "why" a lot. Gets bored by science explanations unless they explain
a computational choice.

**Hidden beliefs:**
- float32 everywhere is fine and obviously faster, so he'll ask to cast inputs
  to float32 and assumes nothing downstream cares. (not catalogued)
- The published 14,900x number is the pipeline speedup. (catalogued: M-SPEEDUP)
- A mask is True where pixels are bad. (catalogued: M-MASK-POLARITY)
