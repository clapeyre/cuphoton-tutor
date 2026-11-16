"""v3 - What the matching kernel does.  Real data: v3.npz (fitted kernel, 27 basis images), v1.npz (stamps)."""
from common import *

VID = "v3-kernel"
ACC = "#ffb000"


class V3(Scene):
    def construct(self):
        T = timings(VID)
        k3 = np.load(DATA / "v3.npz")
        d1 = np.load(DATA / "v1.npz")
        kernel, basis, coeffs = k3["kernel"], k3["basis_kernels"], k3["coeffs"]
        s_ref = float(d1["psfsig"][0]) * 0.26 / 0.27  # the reference's PSF width in target pixels
        s_tgt = float(d1["psfsig"][1])
        s_k = float(np.sqrt(s_tgt ** 2 - s_ref ** 2))

        # ---------- s1: blur adds in quadrature
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        ax = Axes(x_range=[-6, 6, 2], y_range=[0, 0.4, 0.1], x_length=10, y_length=4.2, tips=False,
                  axis_config={"include_ticks": False}).shift(DOWN * 0.6)
        g = lambda s: (lambda x: np.exp(-x ** 2 / (2 * s ** 2)) / (np.sqrt(2 * np.pi) * s))
        narrow = ax.plot(g(s_ref), color=WHITE, x_range=[-6, 6])
        small = ax.plot(g(s_k), color=ACC, x_range=[-6, 6])
        wide = ax.plot(g(s_tgt), color=BLUE_B, x_range=[-6, 6])
        ln = label(f"sharp star, width {s_ref:.2f} px", 26).to_corner(UL, buff=0.6)
        lk = label(f"smearing shape, width {s_k:.2f} px", 26, ACC).next_to(ln, DOWN, aligned_edge=LEFT, buff=0.2)
        lw = label(f"result, width {s_tgt:.2f} px", 26, BLUE_B).next_to(lk, DOWN, aligned_edge=LEFT, buff=0.2)
        t.at("Take a narrow bump"); t.play(FadeIn(ax), Create(narrow), FadeIn(ln), run_time=0.8)
        t.at("a small Gaussian"); t.play(Create(small), FadeIn(lk), run_time=0.7)
        t.at("you get a wider bump"); t.play(ReplacementTransform(narrow.copy(), wide), FadeIn(lw), run_time=1.0)
        eq = label(f"{s_ref:.2f}²  +  {s_k:.2f}²  =  {s_tgt:.2f}²", 36, ACC).to_corner(UR, buff=0.7)
        t.at("their squares do"); t.play(FadeIn(eq), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: that shape is the kernel
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        y, x = (int(v) for v in d1["star"])
        r = 10
        ref_st = d1["aligned"][y - r:y + r + 1, x - r:x + r + 1]
        tgt_st = d1["target"][y - r:y + r + 1, x - r:x + r + 1]
        hi = float(np.nanmax(tgt_st))
        A = to_image(ref_st, "gray", 0, float(np.nanmax(ref_st)), 3.2).shift(LEFT * 4.6 + DOWN * 0.2)
        B = to_image(tgt_st, "gray", 0, hi, 3.2).shift(RIGHT * 4.6 + DOWN * 0.2)
        K = to_image(kernel, "gray", float(kernel.min()), float(kernel.max()), 2.0).shift(DOWN * 0.2)
        la = label("reference (sharper)", 26).next_to(A, UP, buff=0.25)
        lb = label("target", 26).next_to(B, UP, buff=0.25)
        lK = label("the matching kernel", 26, ACC).next_to(K, UP, buff=0.25)
        a1 = Arrow(A.get_right(), K.get_left(), buff=0.2, color=ACC); a2 = Arrow(K.get_right(), B.get_left(), buff=0.2, color=ACC)
        t.at("a small image"); t.play(FadeIn(K), FadeIn(lK), run_time=0.6)
        t.at("Convolve the sharper"); t.play(FadeIn(A), FadeIn(la), GrowArrow(a1), run_time=0.7)
        t.at("every star takes on"); t.play(GrowArrow(a2), FadeIn(B), FadeIn(lb), run_time=0.7)
        unk = label("unknown in advance: found from the two pictures", 26, GREY_B).to_edge(DOWN, buff=0.6)
        t.at("We don't know"); t.play(FadeIn(unk), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: built from a few shapes
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        img = lambda a, h: to_image(a, "gray", -float(np.abs(a).max()), float(np.abs(a).max()), h)
        base = Group(*[img(basis[i], 1.7) for i in (0, 15, 21)]).arrange(RIGHT, buff=0.5).shift(UP * 1.6 + LEFT * 2.6)
        bl = VGroup(*[label(f"width {w}", 22).next_to(b, DOWN, buff=0.15) for w, b in zip((0.7, 1.4, 2.8), base)])
        var = Group(*[img(basis[i], 1.0) for i in (1, 6, 16, 19, 22, 25)]).arrange(RIGHT, buff=0.25).shift(DOWN * 1.0 + LEFT * 2.6)
        vl = label("and simple variations of each", 22, GREY_B).next_to(var, DOWN, buff=0.2)
        t.at("a few Gaussian shapes"); t.play(LaggedStart(*[FadeIn(b) for b in base], lag_ratio=0.3), FadeIn(bl), run_time=1.0)
        t.at("simple variations"); t.play(LaggedStart(*[FadeIn(v) for v in var], lag_ratio=0.15), FadeIn(vl), run_time=1.0)
        wl = label(f"{len(coeffs)} weights, fitted by least squares", 26, ACC).to_edge(DOWN, buff=0.4).shift(LEFT * 2.6)
        t.at("fits the weights"); t.play(FadeIn(wl), run_time=0.5)
        K2 = to_image(kernel, "gray", float(kernel.min()), float(kernel.max()), 3.2).shift(RIGHT * 4.4 + UP * 0.2)
        lK2 = label("the kernel xPois found", 26, ACC).next_to(K2, UP, buff=0.25)
        arr = Arrow(var.get_right() + UP * 1.2, K2.get_left(), color=ACC, buff=0.3)
        t.at("What you get back"); t.play(GrowArrow(arr), FadeIn(K2), FadeIn(lK2), run_time=0.9)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: read the kernel
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        K3 = to_image(kernel, "gray", float(kernel.min()), float(kernel.max()), 3.6).shift(LEFT * 4.0 + UP * 0.4)
        prof = kernel[kernel.shape[0] // 2]
        n = len(prof)
        ax = Axes(x_range=[0, n - 1, 3], y_range=[min(0, float(prof.min())) - 0.02, float(prof.max()) * 1.15, 0.05],
                  x_length=5.2, y_length=3.0, tips=False, axis_config={"include_ticks": False}).shift(RIGHT * 2.6 + UP * 0.6)
        curve = VMobject(color=ACC, stroke_width=4).set_points_as_corners([ax.c2p(i, float(v)) for i, v in enumerate(prof)])
        pl = label("a cut through the middle", 22, GREY_B).next_to(ax, DOWN, buff=0.15)
        t.at("Two things to look at"); t.play(FadeIn(K3), run_time=0.5)
        t.at("a compact blob"); t.play(FadeIn(ax), Create(curve), FadeIn(pl), run_time=1.2)
        tot = label(f"sum = {float(kernel.sum()):.3f}", 40, ACC).shift(DOWN * 1.9 + LEFT * 4.0)
        t.at("add up to about one"); t.play(FadeIn(tot), run_time=0.5)
        fs = label("the flux scale between the two nights", 26).next_to(tot, DOWN, buff=0.2)
        t.at("That sum is"); t.play(FadeIn(fs), run_time=0.5)
        card = label("the sharper image is the one you blur; never sharpen the other", 26, GREY_B).to_edge(DOWN, buff=0.35).shift(RIGHT * 1.5)
        t.at("If the target were"); t.play(FadeIn(card), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: ask
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        prompt = label("\"Show me the kernel, and its sum.\"", 40, ACC)
        frame = SurroundingRectangle(prompt, color=ACC, buff=0.4, corner_radius=0.15)
        t.at("ask to see"); t.play(FadeIn(frame), FadeIn(prompt), run_time=0.6)
        t.rest()
