"""v7 - Two receivers, one signal.  Real data: v7.npz (two recordings sharing a faint signal 23 samples
apart, correlated with xBeam; data_v7.py)."""
from common import *

VID = "v7-two-receivers"
ACC = "#ffb000"
SIG = "#4fc3f7"
GROUND = -2.6


def dish(x, scale=1.0):
    """A radio dish on a stand, its focus point at the top."""
    bowl = Arc(radius=0.7 * scale, start_angle=PI + 0.35, angle=PI - 0.7, color=WHITE, stroke_width=5)
    stand = Line(DOWN * 0.05, DOWN * 0.75 * scale, color=GREY_B, stroke_width=4)
    g = VGroup(bowl, stand)
    g.move_to(RIGHT * x + UP * (GROUND + 0.55 * scale))
    return g


def trace(values, width, height, color=WHITE, sw=2):
    xs = np.linspace(-width / 2, width / 2, len(values))
    return VMobject(color=color, stroke_width=sw).set_points_as_corners(
        [np.array([x, v * height, 0]) for x, v in zip(xs, values)])


class V7(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v7.npz")

        # ---------- s1: one wave, two receivers
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        u = np.array([1.0, -2.0, 0]) / np.sqrt(5)      # the waves' direction of travel
        v = np.array([2.0, 1.0, 0]) / np.sqrt(5)       # along a wavefront
        src = VGroup(Dot(radius=0.16, color=ACC), Circle(radius=0.32, color=ACC, stroke_width=2)).move_to(-3.7 * u + LEFT * 2.6 + UP * 0.2)
        src_l = label("a distant source", 26, ACC).next_to(src, RIGHT, buff=0.3)
        ground = Line(LEFT * 7, RIGHT * 7, color=GREY_D).shift(UP * GROUND)
        dA, dB = dish(-3.0), dish(3.0)
        pA, pB = dA[0].get_center(), dB[0].get_center()
        t.at("Far away"); t.play(FadeIn(src), FadeIn(src_l), run_time=0.6)
        s = ValueTracker(-3.5)
        fronts = always_redraw(lambda: VGroup(*[
            Line((s.get_value() - k * 1.1) * u - 9 * v, (s.get_value() - k * 1.1) * u + 9 * v, color=SIG, stroke_width=3,
                 stroke_opacity=max(0.0, 1 - 0.18 * k)) for k in range(6)]))
        t.at("Two radio telescopes"); t.play(Create(ground), FadeIn(dA), FadeIn(dB), run_time=0.7)
        self.add(fronts)
        sA, sB = float(np.dot(pA, u)), float(np.dot(pB, u))
        t.at("each wavefront"); t.play(s.animate.set_value(sA), run_time=1.6, rate_func=linear)
        t.play(Indicate(dA, color=SIG, scale_factor=1.15), run_time=0.4)
        t.at("the other a moment later"); t.play(s.animate.set_value(sB), run_time=1.1, rate_func=linear)
        t.play(Indicate(dB, color=SIG, scale_factor=1.15), run_time=0.4)
        self.remove(fronts)
        front = Line(sA * u - 9 * v, sA * u + 9 * v, color=SIG, stroke_width=3)
        gap = Line(pB, pB - (sB - sA) * u, color=ACC, stroke_width=7)
        gap_l = label("extra path = delay", 28, ACC).next_to(gap, RIGHT, buff=0.2)
        t.at("That moment is the delay"); t.play(FadeIn(front), Create(gap), FadeIn(gap_l), run_time=0.8)
        turn = label("it depends on where the source is, and changes as the Earth turns", 24, GREY_B).to_edge(DOWN, buff=0.25)
        t.at("It depends on where"); t.play(FadeIn(turn), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: what a dish records
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        a, b, sh = d["a"], d["b"], d["shared"]
        delay = int(d["delay"])
        n0, n = 200, 120
        W, H = 10.0, 0.35
        tA = trace(a[n0:n0 + n], W, H).shift(UP * 1.6 + RIGHT * 0.9)
        tB = trace(b[n0:n0 + n], W, H).shift(DOWN * 1.0 + RIGHT * 0.9)
        lA = VGroup(dish(0, 0.55), label("dish A", 24)).arrange(DOWN, buff=0.1).next_to(tA, LEFT, buff=0.35)
        lB = VGroup(dish(0, 0.55), label("dish B", 24)).arrange(DOWN, buff=0.1).next_to(tB, LEFT, buff=0.35)
        t.at("It records the voltage"); t.play(FadeIn(lA), Create(tA), run_time=1.2)
        t.play(FadeIn(lB), Create(tB), run_time=1.0)
        k = np.sqrt(0.35)
        cA = trace(k * sh[delay + n0:delay + n0 + n], W, H, SIG, 4).move_to(tA)
        cB = trace(k * sh[n0:n0 + n], W, H, SIG, 4).move_to(tB)
        cA.shift(UP * (tA.get_center()[1] - cA.get_center()[1]) * 0)
        noise_l = label("mostly the receiver's own noise", 26).to_edge(UP, buff=0.3)
        t.at("Most of that voltage"); t.play(FadeIn(noise_l), run_time=0.5)
        hid_l = label("the source: the same faint pattern in both, shifted", 26, SIG).to_edge(DOWN, buff=0.35)
        t.at("The source is a faint pattern"); t.play(Create(cA), Create(cB), FadeIn(hid_l), run_time=1.2)
        t.at("By eye"); t.play(FadeOut(cA), FadeOut(cB), FadeOut(hid_l), run_time=0.8)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: slide, multiply, add
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        lags, rho = d["lags"], d["rho"]
        n0, n, W, H = 300, 90, 9.0, 0.2
        yA, yB, yP = 3.05, 1.85, 0.75
        A = trace(a[n0:n0 + n], W, H).shift(UP * yA + RIGHT * 0.6)
        la = label("A", 26).next_to(A, LEFT, buff=0.3)
        lb = label("B, shifted", 26).move_to(la.get_center() + DOWN * (yA - yB) + LEFT * 0.45)
        lp = label("A × B", 26, GREY_B).move_to(la.get_center() + DOWN * (yA - yP) + LEFT * 0.2)
        k = ValueTracker(float(lags[0]))
        reach = ValueTracker(float(lags[0]))  # how far the curve has been drawn
        xs = np.linspace(-W / 2, W / 2, n) + 0.6

        def b_now():
            sh_ = int(round(k.get_value()))
            return b[n0 + sh_:n0 + sh_ + n]

        B = always_redraw(lambda: trace(b_now(), W, H).shift(UP * yB + RIGHT * 0.6))
        P = always_redraw(lambda: VGroup(*[
            Line([x, yP, 0], [x, yP + p, 0], stroke_width=4, color=GREEN_C if p > 0 else RED_C)
            for x, p in zip(xs, np.clip(a[n0:n0 + n] * b_now(), -3, 3) * 0.17)]))
        ax = Axes(x_range=[-60, 60, 20], y_range=[-0.1, 0.4, 0.1], x_length=9.0, y_length=2.6, tips=False).shift(DOWN * 1.75 + RIGHT * 0.6)
        xl = label("shift (samples)", 22).next_to(ax.c2p(60, -0.1), DOWN, buff=0.15).align_to(ax, RIGHT)
        yl = label("sum of the products", 22).rotate(PI / 2).next_to(ax, LEFT, buff=0.15)
        zero = label("0", 20).next_to(ax.c2p(0, -0.1), DOWN, buff=0.12)
        t.at("slide one recording"); t.play(FadeIn(A), FadeIn(la), FadeIn(lb), run_time=0.5)
        self.add(B)
        t.at("multiply them"); t.play(FadeIn(lp), run_time=0.3)
        self.add(P)
        t.at("add up the products"); t.play(FadeIn(ax), FadeIn(xl), FadeIn(yl), FadeIn(zero), run_time=0.5)

        def curve_upto():
            m = lags <= reach.get_value()
            pts = [ax.c2p(float(l_), float(r_)) for l_, r_ in zip(lags[m], rho[m])]
            return VMobject(color=ACC, stroke_width=4).set_points_as_corners(pts) if len(pts) > 1 else VMobject()

        curve = always_redraw(curve_upto)
        dot = always_redraw(lambda: Dot(ax.c2p(k.get_value(), float(np.interp(k.get_value(), lags, rho))), color=ACC, radius=0.08))
        self.add(curve, dot)
        peak = int(d["peak"])
        t.at("Mostly"); t.play(k.animate.set_value(peak - 6), reach.animate.set_value(peak - 6), run_time=4.4, rate_func=linear)
        t.at("When the hidden patterns"); t.play(k.animate.set_value(peak), reach.animate.set_value(peak), run_time=1.0, rate_func=linear)
        t.play(k.animate.set_value(float(lags[-1])), reach.animate.set_value(float(lags[-1])), run_time=2.2, rate_func=linear)
        t.play(k.animate.set_value(peak), run_time=0.6)  # back to the peak, the recordings lined up
        self.remove(dot)
        pk = label("the peak: the delay", 26, ACC).next_to(ax.c2p(peak, float(rho.max())), RIGHT, buff=0.25)
        name = label("the cross-correlation", 28, ACC).move_to(ax.c2p(-58, 0.33), aligned_edge=LEFT)
        t.at("That curve"); t.play(FadeIn(name), run_time=0.5)
        t.at("Its peak"); t.play(FadeIn(pk), Flash(ax.c2p(peak, float(rho.max())), color=ACC), run_time=0.7)
        gpu = label("xBeam: the same sums, through Fourier transforms, on the GPU", 22, GREY_B).to_edge(DOWN, buff=0.1)
        t.at("x beam computes"); t.play(FadeIn(gpu), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: why line them up
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        earth = Circle(radius=2.4, color=BLUE_D, fill_color="#0d2a4a", fill_opacity=1, stroke_width=2).shift(LEFT * 3.2 + DOWN * 0.3)
        angs = [2.2, 1.45, 0.75, 0.05, -0.6]
        sites = VGroup(*[Dot(earth.get_center() + 2.4 * np.array([np.cos(a_), np.sin(a_), 0]), color=WHITE, radius=0.09) for a_ in angs])
        t.at("dishes thousands"); t.play(FadeIn(earth), FadeIn(sites), run_time=0.8)
        pairs = [(0, 3), (1, 4), (0, 2), (2, 4)]
        lines = VGroup(*[Line(sites[i].get_center(), sites[j].get_center(), color=ACC, stroke_width=2.5) for i, j in pairs])
        bl = label("baseline", 26, ACC).next_to(earth, UP, buff=0.3)
        t.at("each pair of dishes"); t.play(Create(lines), run_time=1.0)
        t.at("a baseline"); t.play(FadeIn(bl), run_time=0.4)
        big = DashedVMobject(Circle(radius=2.4, color=GREY_B), num_dashes=40).move_to(earth)
        big_l = label("one dish as wide as the baseline", 24, GREY_B).next_to(earth, DOWN, buff=0.25)
        t.at("as fine as a single dish"); t.play(Create(big), FadeIn(big_l), run_time=1.0)
        ring = VGroup(*[Annulus(inner_radius=0.9 - 0.04 * i, outer_radius=1.05 + 0.05 * i, color=ACC,
                                fill_opacity=0.5 - 0.09 * i, stroke_width=0) for i in range(5)]).shift(RIGHT * 3.6 + UP * 0.4)
        ring_l = label("a black hole's ring (sketch)", 24).next_to(ring, DOWN, buff=0.35)
        t.at("Event Horizon Telescope"); t.play(FadeIn(ring), FadeIn(ring_l), run_time=0.8)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: this module
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        any2 = label("any two receivers, one source", 32).to_edge(UP, buff=0.6)
        t.at("any two receivers"); t.play(FadeIn(any2), run_time=0.5)

        def card(num, txt):
            box = RoundedRectangle(corner_radius=0.15, width=3.9, height=1.7, color=WHITE)
            g = VGroup(label(num, 26, ACC), label(txt, 26)).arrange(DOWN, buff=0.2).move_to(box)
            return VGroup(box, g)

        cards = VGroup(card("7.1", "A known delay"), card("7.2", "Three radio stations"),
                       card("7.3", "Two gravitational-\nwave detectors")).arrange(RIGHT, buff=0.4).shift(DOWN * 0.1)
        t.at("find a delay you know"); t.play(FadeIn(cards[0]), run_time=0.4)
        t.at("correlate three radio stations"); t.play(FadeIn(cards[1]), run_time=0.4)
        t.at("measure that wave's delay"); t.play(FadeIn(cards[2]), run_time=0.4)
        q = label("every run gives a number: when do you believe it?", 30, ACC).to_edge(DOWN, buff=0.7)
        t.at("The question is"); t.play(FadeIn(q), run_time=0.6)
        t.rest()
