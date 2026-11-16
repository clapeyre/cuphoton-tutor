"""v1 - Why you can't just subtract two pictures of the sky.  One section per narration segment.
Render: manim -qm v1_why_not_subtract.py V1   (see pipeline/render.sh)"""
from common import *

VID = "v1-why-not-subtract"
ACC = "#ffb000"


class V1(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v1.npz")
        tgt, ali, naive, alo, z, zb = (d[k] for k in ("target", "aligned", "naive", "aligned_only", "z", "z_bad"))
        peaks = d["peaks"]; shape = tgt.shape
        lo, hi = np.percentile(tgt, [1, 99.3])
        H = 5.6
        # ---------- s1
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        ref_img = to_image(ali, "gray", lo, hi, H).shift(UP * 0.2)
        tgt_img = to_image(tgt, "gray", lo, hi, H).move_to(ref_img)
        cap = label("Night 1: the reference", 30).to_edge(DOWN, buff=0.35)
        t.play(FadeIn(ref_img), FadeIn(cap), run_time=1.2)
        cap2 = label("Night 2: the target", 30).move_to(cap)
        t.at("Almost nothing")
        t.play(FadeOut(ref_img), FadeIn(tgt_img), Transform(cap, cap2), run_time=2.0)
        c_new = Circle(radius=0.4, color=GREEN).move_to(pix(tgt_img, shape, *peaks[1]))
        c_bright = Circle(radius=0.4, color=GREEN).move_to(pix(tgt_img, shape, *peaks[0]))
        t.at("a new point"); t.play(Create(c_new), run_time=0.6)
        t.at("a star that got"); t.play(Create(c_bright), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        nimg = to_image(naive, "gray", -400, 400, H).shift(UP * 0.2)
        cap = label("Night 2 minus night 1, no alignment", 30).to_edge(DOWN, buff=0.35)
        a = to_image(tgt, "gray", lo, hi, H).move_to(nimg)
        self.add(a)
        t.at("Here's what"); t.play(FadeOut(a), FadeIn(nimg), FadeIn(cap), run_time=1.0)
        # zoom on the strongest lobe pair
        sm = np.abs(naive); sm[:20] = 0; sm[-20:] = 0; sm[:, :20] = 0; sm[:, -20:] = 0
        y0, x0 = np.unravel_index(np.argmax(sm), sm.shape)
        crop = naive[y0 - 8:y0 + 9, x0 - 8:x0 + 9]
        zoom = to_image(crop, "gray", -400, 400, 5.4).shift(UP * 0.2)
        box = Square(side_length=H * 17 / 256 * 1.0, color=ACC).move_to(pix(nimg, shape, y0, x0))
        t.at("Every star"); t.play(Create(box), run_time=0.4)
        t.play(FadeOut(nimg), FadeOut(box), FadeIn(zoom), run_time=0.6)
        lab_b = label("bright", 26, RED_B).next_to(zoom, LEFT, buff=0.6); lab_d = label("dark", 26, BLUE_B).next_to(zoom, RIGHT, buff=0.6)
        t.at("bright half"); t.play(FadeIn(lab_b), run_time=0.4)
        t.at("dark half"); t.play(FadeIn(lab_d), run_time=0.4)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        n = 9
        th = np.radians(3.0)
        def lattice(rot, sh, sp):
            pts = [[(i - (n - 1) / 2) * sp, (j - (n - 1) / 2) * sp] for j in range(n) for i in range(n)]
            R = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]])
            return np.array([R @ p + sh for p in pts]).reshape(n, n, 2)
        def grid(L, color):
            g = VGroup()
            for k in range(n):
                g.add(VMobject(color=color, stroke_width=3).set_points_as_corners([[*L[k, i], 0] for i in range(n)]))
                g.add(VMobject(color=color, stroke_width=3).set_points_as_corners([[*L[i, k], 0] for i in range(n)]))
            return g
        g_ref = grid(lattice(th, np.array([0.5, 0.2]), 0.62), BLUE_B)
        g_tgt = grid(lattice(0.0, np.array([0.0, 0.0]), 0.6), ACC)
        c1 = label("Reference grid", 28, BLUE_B).to_edge(DOWN, buff=0.4)
        t.play(Create(g_tgt.copy().set_opacity(0.25)), Create(g_ref), FadeIn(c1), run_time=1.5)
        c2 = label("resample onto the target's grid", 28, ACC).move_to(c1)
        t.at("resample"); t.play(Transform(g_ref, g_tgt), Transform(c1, c2), run_time=2.0)
        a1 = to_image(ali, "gray", lo, hi, 4.8).shift(LEFT * 3.7 + UP * 0.1)
        a2 = to_image(tgt, "gray", lo, hi, 4.8).shift(RIGHT * 3.7 + UP * 0.1)
        l1 = label("Reference, aligned", 24).next_to(a1, DOWN); l2 = label("Target", 24).next_to(a2, DOWN)
        t.at("In cuPhoton")
        t.play(*[FadeOut(m) for m in self.mobjects], FadeIn(a1), FadeIn(a2), FadeIn(l1), FadeIn(l2), run_time=0.5)
        xr = label("xRep", 32, ACC).to_edge(UP, buff=0.3)
        t.at("xRep"); t.play(FadeIn(xr), run_time=0.3)
        sub = to_image(alo, "gray", -400, 400, 5.4).shift(UP * 0.2)
        l3 = label("Target minus aligned reference", 28).to_edge(DOWN, buff=0.35)
        t.at("Now subtract"); t.play(*[FadeOut(m) for m in (a1, a2, l1, l2, xr)], FadeIn(sub), FadeIn(l3), run_time=0.6)
        l4 = label("Target minus aligned reference: rings", 28).move_to(l3)
        t.at("a ring"); t.play(Transform(l3, l4), run_time=0.4)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        sy, sx = d["star"]; r = 8
        pr = d["prof_ref"][12 - r:12 + r + 1]; pt = d["prof_tgt"][12 - r:12 + r + 1]
        pr = pr / pr.sum(); pt = pt / pt.sum()  # equal flux: the brightness scale is fitted separately
        xs = np.arange(-r, r + 1)
        ax = Axes(x_range=[-r, r, 4], y_range=[-0.05, 0.3, 0.1], x_length=9, y_length=3.0,
                  axis_config={"include_tip": False, "font_size": 20}).shift(UP * 1.2 + LEFT * 0.5)
        ax2 = Axes(x_range=[-r, r, 4], y_range=[-0.1, 0.1, 0.1], x_length=9, y_length=1.6,
                   axis_config={"include_tip": False, "font_size": 20}).shift(DOWN * 2.0 + LEFT * 0.5)
        def curve(axes, ys, color):
            return axes.plot_line_graph(xs, ys, line_color=color, add_vertex_dots=False, stroke_width=4)
        c_ref = curve(ax, pr, BLUE_B); c_tgt = curve(ax, pt, ACC)
        k_ref = label("night 1: sharp", 24, BLUE_B).move_to(ax.c2p(-r + 3.2, 0.26)); k_tgt = label("night 2: blurrier", 24, ACC).move_to(ax.c2p(r - 3.2, 0.26))
        t.play(Create(ax), Create(ax2), run_time=0.8)
        t.at("blurred starlight"); t.play(Create(c_tgt), FadeIn(k_tgt), run_time=0.6)
        t.at("the other"); t.play(Create(c_ref), FadeIn(k_ref), run_time=0.6)
        diff0 = pt - pr
        c_d = curve(ax2, diff0, GREEN)
        kd = label("night 2 minus night 1", 22, GREEN).next_to(ax2, UP, buff=0.05).align_to(ax2, LEFT)
        t.at("Subtract a narrow"); t.play(Create(c_d), FadeIn(kd), run_time=1.0)
        # convolve the sharp profile by a growing Gaussian until it matches
        sig = ValueTracker(0.0)
        fine = np.arange(-r - 6, r + 7)  # padding for the convolution
        full = np.concatenate([np.zeros(6), pr, np.zeros(6)])
        def conv(s):
            if s < 0.05:
                return pr
            kk = np.exp(-0.5 * (np.arange(-6, 7) / s) ** 2); kk /= kk.sum()
            return np.convolve(full, kk, mode="same")[6:-6]
        c_ref2 = always_redraw(lambda: curve(ax, conv(sig.get_value()), BLUE_B))
        c_d2 = always_redraw(lambda: curve(ax2, pt - conv(sig.get_value()), GREEN))
        sl = always_redraw(lambda: label(f"blur width added: {sig.get_value():.2f} px", 24).to_edge(DOWN, buff=0.3))
        self.remove(c_ref, c_d); self.add(c_ref2, c_d2, sl)
        t.at("blur the sharper"); t.play(sig.animate.set_value(1.35), run_time=2.6, rate_func=smooth)
        res = VGroup(label("xPois fits:", 24), label("kernel", 24, ACC), label("+ brightness scale", 24), label("+ sky level", 24)).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.3)
        t.at("xPois fits"); t.play(FadeOut(sl), FadeIn(res[0]), run_time=0.4)
        t.at("kernel"); t.play(FadeIn(res[1]), run_time=0.3)
        t.at("brightness scale"); t.play(FadeIn(res[2]), run_time=0.3)
        t.at("sky level"); t.play(FadeIn(res[3]), run_time=0.3)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        zi = to_image(z, "gray", -6, 6, 6.0).shift(UP * 0.2)
        cap = label("Difference over its noise (z), from xPois", 28).to_edge(DOWN, buff=0.35)
        t.play(FadeIn(zi), FadeIn(cap), run_time=1.0)
        c1 = Circle(radius=0.38, color=BLACK, stroke_width=5).move_to(pix(zi, shape, *peaks[0]))
        c2 = Circle(radius=0.38, color=BLACK, stroke_width=5).move_to(pix(zi, shape, *peaks[1]))
        l1 = label("brighter", 28, WHITE).move_to(RIGHT * 4.6 + DOWN * 2.2); l2 = label("new", 28, WHITE).move_to(RIGHT * 4.6 + UP * 0.6)
        a1 = Line(l1.get_left(), c1.get_right(), color=WHITE, stroke_width=2); a2 = Line(l2.get_left(), c2.get_right(), color=WHITE, stroke_width=2)
        t.at("a star that got"); t.play(Create(c1), FadeIn(l1), Create(a1), run_time=0.6)
        t.at("a source that"); t.play(Create(c2), FadeIn(l2), Create(a2), run_time=0.6)
        fr = SurroundingRectangle(zi, color=ACC, buff=0.0, stroke_width=6)
        lf = label("no data beyond\nthe border:\n9 px frame", 24, ACC).move_to(LEFT * 4.9 + UP * 0.6)
        t.at("The empty frame"); t.play(Create(fr), FadeIn(lf), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s6
        self.next_section("s6"); t = Timed.seg(self, T, "s6")
        names = [("Align", "xRep"), ("Match &\nsubtract", "xPois"), ("Find", "xPois"), ("Measure", "xFit"), ("Decide", "xScan")]
        boxes = VGroup()
        for nm, mod in names:
            b = RoundedRectangle(corner_radius=0.15, width=2.2, height=1.4, color=ACC)
            b.add(label(nm, 26).move_to(b)); b.add(label(mod, 20, GREY_B).next_to(b, DOWN, buff=0.15))
            boxes.add(b)
        boxes.arrange(RIGHT, buff=0.45).move_to(ORIGIN + UP * 0.2)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.05, stroke_width=4, color=WHITE) for i in range(4)])
        for i, (b, word) in enumerate(zip(boxes, ["Align", "Match and subtract", "Find", "Measure", "Decide"])):
            t.at(word); t.play(FadeIn(b), *([Create(arrows[i - 1])] if i else []), run_time=0.4)
        # agent icon under the first box; person with magnifier above
        agent = VGroup(RoundedRectangle(corner_radius=0.1, width=0.9, height=0.7, color=BLUE_B), label("</>", 22, BLUE_B)).next_to(boxes[0], DOWN, buff=0.9)
        a_l = label("your agent types", 20, BLUE_B).next_to(agent, DOWN, buff=0.15)
        person = VGroup(Circle(radius=0.2, color=WHITE), Arc(radius=0.4, start_angle=0, angle=PI, color=WHITE).shift(DOWN * 0.45).rotate(0))
        person.arrange(DOWN, buff=0.05)
        mag = VGroup(Circle(radius=0.17, color=GREEN), Line(ORIGIN, DL * 0.2, color=GREEN).shift(DR * 0.17 + DOWN * 0.0)).scale(1)
        mag[1].put_start_and_end_on(mag[0].get_center() + DR * 0.12, mag[0].get_center() + DR * 0.38)
        you = VGroup(person, mag.next_to(person, RIGHT, buff=0.15)).next_to(boxes[0], UP, buff=0.7)
        y_l = label("you check", 20, GREEN).next_to(you, UP, buff=0.1)
        t.at("Your agent"); t.play(FadeIn(agent), FadeIn(a_l), run_time=0.5)
        t.at("Your job"); t.play(FadeIn(you), FadeIn(y_l), run_time=0.5)
        t.rest()
