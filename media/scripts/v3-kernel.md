# v3 — What the matching kernel does

Opens 1.4 (L2 layer). Must not give away 1.4's turns: it never states the
kernel's size or footprint (`nan-edge`: why the 9-px frame) and never says what a
wrong kernel leaves (`perfect-kernel`: rings). Real data throughout. Data to generate:
media/scenes/data_v3.py (real kernel, basis images, 27 fitted weights).

Facts checked against a real CPU run on the sample pair (overnight run): the
kernel sums to 1.013; its effective width is 1.39 px against the quadrature
estimate sqrt(1.8^2 - 1.2^2) = 1.38 px (1.2 × 0.26/0.27 in target pixels); the reference is the SHARPER image
(PSF sigma 1.2 px vs 1.8 px), so the kernel blurs the reference. The basis is
three Gaussians (sigma 0.7, 1.4, 2.8 px) each multiplied by low-order polynomial
terms (degrees 4, 2, 2): 27 fitted weights in total, not three. The video says
"a few Gaussian shapes, each with simple variations"; do not say "three weights".

## s1 — Blur adds in quadrature (≈25 s)
**Visual (1D toy, but with the real widths):** a narrow Gaussian (sigma 1.2) and a
small Gaussian (sigma 1.38) side by side; the convolution animation slides one
across the other; the result is a wide Gaussian (sigma 1.8). Labels show
1.2² + 1.38² ≈ 1.8² (rounded).
**Narration:** Blurring twice is just blurring once, more. Take a narrow bump and
smear it with a small Gaussian, and you get a wider bump. The widths don't add,
their squares do. So to turn a sharp star into a blurrier one, there is always a
small smearing shape that does it.

## s2 — That shape is the kernel (≈25 s)
**Visual:** reference star and target star as 2D images (real stamps, from the
aligned reference and target around an unchanged star); an arrow labeled "kernel"
from the first to the second; the real kernel image shown between them (no size stated).
**Narration:** In two dimensions the smearing shape is a small image, the matching
kernel. Convolve the sharper picture with it and every star takes on the other
night's blur. We don't know the kernel in advance, so xPois has to find it from
the pictures themselves.

## s3 — Built from a few shapes (≈30 s)
**Visual:** the three Gaussian basis shapes (sigma 0.7, 1.4, 2.8, the real
basis_kernels at polynomial degree 0) shown as heat maps; each is nudged by simple
variations (the polynomial terms, a few shown as small sign-changing patterns);
weights slide; the weighted sum morphs into the real fitted kernel.
**Narration:** xPois builds the kernel from a few Gaussian shapes of different
widths, each with some simple variations. It then fits the weights by least
squares, so that the blurred reference matches the target as closely as the noise
allows. What you get back is one small image: the kernel xPois actually found.

## s4 — Read the kernel (≈25 s)
**Visual:** the real kernel as a heat map with a profile through the middle; a
counter "sum = 1.013"; caption "flux scale". Then a one-line card: "the sharper
image is the one you blur, never sharpen the other" (no second animation).
**Narration:** Two things to look at. First, it's a compact blob with no strange
structure, so the blur was matched with a smooth shape. Second, the numbers add up
to about one. That sum is the flux scale between the two nights: near one means the
brightness agreed. If the target were the sharper image, you would blur the target instead, never sharpen. For this pair, the reference is the sharper one.

## s5 — What to ask your agent (≈10 s)
**Visual:** prompt card: "Show me the kernel and its sum."
**Narration:** So whenever your agent matches two images, ask to see the kernel,
and its sum.
