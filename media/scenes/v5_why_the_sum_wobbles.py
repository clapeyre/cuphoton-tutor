"""v5 - Why the sum wobbles.  Real data: v5.npz (xRep on pure noise, PS1 target blank sky; data_v5.py)."""
from common import *

VID = "v5-why-the-sum-wobbles"
ACC = "#ffb000"


def cell_grid(vals, size=1.0, lo=-2.5, hi=2.5, fs=24):
    """A 3x3 grid of grey squares with their values written in."""
    g = VGroup()
    for i in range(3):
        for j in range(3):
            v = float(vals[i, j])
            shade = np.clip((v - lo) / (hi - lo), 0, 1)
            col = ManimColor.from_rgb((shade, shade, shade))
            sq = Square(side_length=size, stroke_color=GREY_C, stroke_width=1.5, fill_color=col, fill_opacity=1)
            sq.move_to(RIGHT * (j - 1) * size + DOWN * (i - 1) * size)
            txt = label(f"{v:+.1f}", fs, BLACK if shade > 0.55 else WHITE).move_to(sq)
            g.add(VGroup(sq, txt))
    return g


class V5(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v5.npz")

        # ---------- s1: the puzzle
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        def card(lines, color):
            txt = VGroup(*[label(s, 30, color if k == 0 else WHITE) for k, s in enumerate(lines)]).arrange(DOWN, buff=0.25)
            box = RoundedRectangle(corner_radius=0.15, width=5.4, height=txt.height + 0.9, color=color)
            return VGroup(box, txt.move_to(box))
        left = card(["One pixel", "scatter / map: 0.9 to 1.07", "the map is right"], WHITE).shift(LEFT * 3.6)
        right = card(["A flux", "error bars 1.2 to 1.5×", "too small"], ACC).shift(RIGHT * 3.6)
        t.at("the fake stars"); t.play(FadeIn(right), run_time=0.6)
        t.at("one pixel at a time"); t.play(FadeIn(left), run_time=0.6)
        q = label("?", 120, ACC)
        t.at("How can"); t.play(FadeIn(q, scale=0.5), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: adding independent noise
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        boxes = d["iid_boxes"]
        grid = cell_grid(boxes[0]).shift(LEFT * 3.8 + UP * 0.3)
        cap = label("9 pixels, each ±1, independent", 28).next_to(grid, DOWN, buff=0.45)
        t.at("Start with nine"); t.play(FadeIn(grid), FadeIn(cap), run_time=0.6)
        line = NumberLine(x_range=[-9, 9, 3], length=6.4).shift(RIGHT * 3.0 + DOWN * 0.6)
        line.add(*[label(f"{v:+d}" if v else "0", 22).next_to(line.n2p(v), DOWN, buff=0.2) for v in range(-9, 10, 3)])
        sum_lbl = label("sum of the 9", 28).next_to(line, UP, buff=1.6)
        t.at("adds them up"); t.play(FadeIn(line), FadeIn(sum_lbl), run_time=0.5)
        dots = VGroup()
        for k in range(1, 11):
            new = cell_grid(boxes[k]).move_to(grid)
            s = float(boxes[k].sum())
            dot = Dot(line.n2p(np.clip(s, -9, 9)) + UP * (0.18 + 0.16 * (k % 5)), radius=0.07, color=WHITE)
            dots.add(dot)
            self.play(ReplacementTransform(grid, new), FadeIn(dot), run_time=0.32)
            grid = new
        band = VGroup(DashedLine(line.n2p(-3) + DOWN * 0.3, line.n2p(-3) + UP * 1.3, color=ACC),
                      DashedLine(line.n2p(3) + DOWN * 0.3, line.n2p(3) + UP * 1.3, color=ACC))
        rule = label("±3 = √9, not 9", 34, ACC).next_to(line, DOWN, buff=0.9)
        t.at("the square root of nine"); t.play(Create(band), FadeIn(rule), run_time=0.6)
        rule2 = label("error bar: add the variances, take the square root", 26).to_edge(DOWN, buff=0.35)
        t.at("Add the variances"); t.play(FadeIn(rule2), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: what resampling does
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        pin, pout = d["patch_in"][3:13, 3:13], d["patch_out"][3:13, 3:13]  # zoom: 10 x 10 pixels
        A = to_image(pin, "gray", -2.5, 2.5, 4.6).shift(LEFT * 3.4 + DOWN * 0.2)
        B = to_image(pout, "gray", -2.5, 2.5, 4.6).shift(RIGHT * 3.4 + DOWN * 0.2)
        la = label("pure noise", 28).next_to(A, UP, buff=0.3)
        lb = label("after xRep: shifted by half a pixel", 28).next_to(B, UP, buff=0.3)
        t.at("Now resample"); t.play(FadeIn(A), FadeIn(la), run_time=0.6)
        t.at("Here xRep"); t.play(FadeIn(B), FadeIn(lb), run_time=0.6)
        px = A.height / pin.shape[0]
        r0, c0 = 5, 4  # one input pixel (array row, col)
        hin = Square(side_length=px, color=ACC, stroke_width=7).move_to(pix(A, pin.shape, r0, c0))
        # input (r, c) feeds outputs (r-1..r, c-1..c), weight 0.37 each (the impulse response)
        outs = [(r0 - 1, c0 - 1), (r0 - 1, c0), (r0, c0 - 1), (r0, c0)]
        hout = VGroup(*[Square(side_length=px, color=ACC, stroke_width=7, fill_color=ACC, fill_opacity=0.25).move_to(pix(B, pout.shape, r, c)) for r, c in outs])
        w = float(d["impulse"][2, 2])
        wl = label(f"each of the four gets {w:.2f} of it", 26, ACC).next_to(B, DOWN, buff=0.3)
        arrow = Arrow(hin.get_right(), hout.get_left(), color=ACC, buff=0.1, stroke_width=3)
        t.at("Each output pixel"); t.play(Create(hin), run_time=0.4)
        t.at("one input pixel's noise"); t.play(GrowArrow(arrow), Create(hout), FadeIn(wl), run_time=0.8)
        # two neighbouring output pixels, and the input pixels each blends: (r..r+1, c..c+1)
        ra, ca = 2, 3
        o1 = Square(side_length=px, color=BLUE_B, stroke_width=8, fill_color=BLUE_B, fill_opacity=0.35).move_to(pix(B, pout.shape, ra, ca))
        o2 = Square(side_length=px, color=GREEN_B, stroke_width=8, fill_color=GREEN_B, fill_opacity=0.35).move_to(pix(B, pout.shape, ra, ca + 1))
        f1 = VGroup(*[Square(side_length=px * 0.9, color=BLUE_B, stroke_width=6, fill_color=BLUE_B, fill_opacity=0.3).move_to(pix(A, pin.shape, ra + a, ca + b)) for a in (0, 1) for b in (0, 1)])
        f2 = VGroup(*[Square(side_length=px * 0.7, color=GREEN_B, stroke_width=6, fill_color=GREEN_B, fill_opacity=0.3).move_to(pix(A, pin.shape, ra + a, ca + 1 + b)) for a in (0, 1) for b in (0, 1)])
        shared = label("the middle column feeds both", 26, WHITE).next_to(A, DOWN, buff=0.3)
        t.at("two neighbours"); t.play(FadeOut(hin), FadeOut(hout), FadeOut(arrow), FadeOut(wl), Create(o1), Create(o2), run_time=0.5)
        t.at("share part"); t.play(Create(f1), Create(f2), FadeIn(shared), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: shared noise doesn't cancel
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        ib, rb = d["iid_boxes"], d["res_boxes"]
        g1 = cell_grid(ib[20], 0.85, fs=20).shift(LEFT * 3.6 + UP * 0.9)
        g2 = cell_grid(rb[20], 0.85, fs=20).shift(RIGHT * 3.6 + UP * 0.9)
        h1 = label("independent", 30).next_to(g1, UP, buff=0.3)
        h2 = label("after xRep", 30, ACC).next_to(g2, UP, buff=0.3)
        t.play(FadeIn(g1), FadeIn(g2), FadeIn(h1), FadeIn(h2), run_time=0.5)
        p1 = label("each pixel: scatter 1.00", 26).next_to(g1, DOWN, buff=0.4)
        p2 = label(f"each pixel: scatter {float(d['res_pix']):.2f}", 26).next_to(g2, DOWN, buff=0.4)
        t.at("pixel by pixel"); t.play(FadeIn(p1), FadeIn(p2), run_time=0.5)
        for k in range(21, 29):
            n1 = cell_grid(ib[k], 0.85, fs=20).move_to(g1); n2 = cell_grid(rb[k], 0.85, fs=20).move_to(g2)
            self.play(ReplacementTransform(g1, n1), ReplacementTransform(g2, n2), run_time=0.3)
            g1, g2 = n1, n2
        s1 = label(f"sum: {float(d['iid_ratio'][1]):.2f} × the prediction", 30).next_to(p1, DOWN, buff=0.35)
        s2 = label(f"sum: {float(d['res_ratio'][1]):.2f} × the prediction", 30, ACC).next_to(p2, DOWN, buff=0.35)
        t.at("So the sum"); t.play(FadeIn(s1), FadeIn(s2), run_time=0.6)
        t.at("nothing wrong"); t.play(Indicate(p2, color=WHITE), run_time=0.8)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: the survey's images
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        c = d["ps1_corr"]
        cg = VGroup()
        for i in range(3):
            for j in range(3):
                v = 1.0 if (i, j) == (1, 1) else float(c[i, j])
                sq = Square(side_length=1.0, stroke_color=GREY_C, fill_color=ManimColor.from_rgb((v * 3 if v < 0.33 else 1,) * 3) if (i, j) != (1, 1) else WHITE, fill_opacity=1)
                sq.move_to(RIGHT * (j - 1) + DOWN * (i - 1))
                cg.add(VGroup(sq, label("1" if (i, j) == (1, 1) else f"{v:.2f}", 26, BLACK if (i, j) == (1, 1) or v > 0.17 else WHITE).move_to(sq)))
        cg.shift(LEFT * 4.3 + DOWN * 0.2)
        ct = label("noise shared with each neighbour", 26).next_to(cg, UP, buff=0.35)
        src = label("Pan-STARRS target night, blank sky", 22, GREY_B).next_to(cg, DOWN, buff=0.35)
        t.at("The survey's images"); t.play(FadeIn(cg), FadeIn(ct), FadeIn(src), run_time=0.6)
        t.at("about a fifth"); t.play(*[Indicate(cg[k], color=ACC) for k in (1, 3, 5, 7)], run_time=0.8)
        sizes, ratio = d["ps1_sizes"], d["ps1_ratio"]
        ax = Axes(x_range=[0, 12, 2], y_range=[0.6, 2.0, 0.2], x_length=6.0, y_length=4.2,
                  tips=False).shift(RIGHT * 2.9 + UP * 0.1)
        ax.add(*[label(str(v), 20).next_to(ax.c2p(v, 0.6), DOWN, buff=0.15) for v in range(0, 13, 2)])
        ax.add(*[label(f"{v:.1f}", 20).next_to(ax.c2p(0, v), LEFT, buff=0.15) for v in (0.6, 1.0, 1.4, 1.8)])
        xl = label("box size (pixels on a side)", 22).next_to(ax, DOWN, buff=0.2)
        yl = label("real scatter of the sum / predicted", 22).rotate(PI / 2).next_to(ax, LEFT, buff=0.1)
        one = DashedLine(ax.c2p(0, 1), ax.c2p(12, 1), color=GREY_B)
        curve = VMobject(color=ACC, stroke_width=4).set_points_as_corners([ax.c2p(float(s), float(r)) for s, r in zip(sizes, ratio)])
        dts = VGroup(*[Dot(ax.c2p(float(s), float(r)), color=ACC, radius=0.06) for s, r in zip(sizes, ratio)])
        t.at("the bigger the patch"); t.play(FadeIn(ax), FadeIn(xl), FadeIn(yl), Create(one), run_time=0.6)
        t.play(Create(curve), FadeIn(dts), run_time=1.6)
        end = label(f"{float(ratio[-1]):.1f}×", 28, ACC).next_to(dts[-1], UP, buff=0.15)
        t.play(FadeIn(end), run_time=0.3)
        fix = label("measure the factor on the image; widen the error bars by it", 28, ACC).to_edge(DOWN, buff=0.3)
        t.at("So you measure"); t.play(FadeIn(fix), run_time=0.6)
        t.rest()
