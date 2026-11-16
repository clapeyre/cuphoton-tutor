# v4 — Where your data lives: host and device

Opens Module 03 (top of 3.1). Must not give away 3.2's prediction (which calls
return NumPy and which CuPy) or 3.4's (timing without a synchronize): it never
names a function's return type and never mentions queuing. Data:
media/scenes/data_v4.py, real times on this machine's GPU for the 2048 × 2048
float64 image of 3.4 (33.6 MB): copy up 2.6 ms, xRep on the device 21.6 ms, copy
back 4.0 ms (synchronized, warm, median of 20). The CPU xRep figure (8.8 s) is
3.4's real run.

Subtitle: "two thousand and forty-eight" -> "2048"
Subtitle: "x rep" -> "xRep"

## s1 — Two memories
**Visual:** two boxes, "host: the computer's memory" and "device: the GPU's
memory", joined by a narrow bridge labelled "copy". An image tile sits on the
host side.
**Narration:** A GPU machine has two memories. The computer's own, which GPU
programmers call the host, and the GPU's, called the device. A narrow bridge joins
them. Anything the GPU works on has to cross it first, and the result has to
cross back before ordinary code can use it.

## s2 — What the bridge costs
**Visual:** a timing card for one real image, two thousand and forty-eight pixels
square: the tile crosses up (2.6 ms), x rep runs on the device (21.6 ms), the
tile crosses back (4.0 ms). Beside it, faint: the same x rep on the CPU, 8.8 s.
**Narration:** Here is one real image, two thousand and forty-eight pixels on a
side. Copying it up takes under three milliseconds. x rep then aligns it on the
GPU in about twenty-two. Copying the result back takes four. Against the CPU's
nine seconds the copies are nothing. Against the GPU's own work, they're not.

## s3 — Once, or at every stage
**Visual:** a chain of four stages. Top row: the tile crosses up and back around
every stage; a time bar grows by about seven milliseconds of copying per stage.
Bottom row: the tile crosses up once, runs all four stages on the device, and
comes back once; its copy bar stays at one round trip.
**Narration:** So it matters how often the data crosses. If every stage sends its
result home and the next one sends it back up, a four-stage chain pays the round
trip four times. If the data stays on the device from the first stage to the
last, it pays once.

## s4 — Where each result lands
**Visual:** a cuPhoton call as a box with an arrow out; a question mark over where
the arrow lands, host or device. The agent's code appears faintly behind.
**Narration:** Every cuPhoton call decides where its result lands, and the choice
differs from call to call. Your agent writes the code, and the code runs either
way. Only knowing where each result lives tells you whether the data crossed once,
or at every step.

## s5 — Ask
**Visual:** a prompt card: "Where does each result live?"
**Narration:** So ask your agent where each result lives.
