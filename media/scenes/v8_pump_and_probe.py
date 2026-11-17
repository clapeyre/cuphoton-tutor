"""v8 - Pump and probe.  Real data: v8.npz (the guide's xRay sample pair reduced to a trace and fitted by
linear prediction; a 64-row detector fitted row by row; data_v8.py)."""
from common import *

VID = "v8-pump-and-probe"
PUMP = "#ff5a4f"
XR = "#4fc3f7"
ACC = "#ffb000"
MODE_C = ["#76b900", "#c58cff"]


def curve(ax, x, y, color, sw=3):
    return VMobject(color=color, stroke_width=sw).set_points_as_corners([ax.c2p(float(a), float(b)) for a, b in zip(x, y)])


class V8(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v8.npz")

        # ---------- s1: a crystal rings
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        bell = VGroup(
            ArcBetweenPoints(LEFT * 0.7 + DOWN * 0.6, RIGHT * 0.7 + DOWN * 0.6, angle=-PI * 0.9, color=ACC, stroke_width=6),
            Line(LEFT * 0.85 + DOWN * 0.6, RIGHT * 0.85 + DOWN * 0.6, color=ACC, stroke_width=6)).shift(LEFT * 4 + UP * 0.6)
        arcs = VGroup(*[Arc(radius=0.9 + 0.35 * i, start_angle=-0.6, angle=1.2, color=GREY_B, stroke_width=3).move_arc_center_to(bell.get_center())
                        for i in range(3)])
        t.at("Strike a bell"); t.play(FadeIn(bell), run_time=0.5)
        t.play(Wiggle(bell, scale_value=1.05), LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3), run_time=1.0)
        grid = VGroup(*[Dot(RIGHT * (1.6 + 0.55 * i) + UP * (1.4 - 0.55 * j), radius=0.09, color=WHITE) for i in range(7) for j in range(6)])
        base = [g.get_center() for g in grid]
        ph = ValueTracker(0.0)
        amp = ValueTracker(0.0)
        for g, p0 in zip(grid, base):
            g.add_updater(lambda m, p0=p0: m.move_to(p0 + RIGHT * 0.12 * amp.get_value() * np.sin(ph.get_value())))
        cl = label("a crystal", 26).next_to(grid, DOWN, buff=0.35)
        t.at("Strike a crystal"); t.play(FadeIn(grid), FadeIn(cl), run_time=0.6)
        flash = Rectangle(width=4.2, height=3.8, color=PUMP, fill_color=PUMP, fill_opacity=0.35, stroke_width=0).move_to(grid)
        t.at("very short laser pulse"); t.play(FadeIn(flash, run_time=0.15)); t.play(FadeOut(flash), run_time=0.3)
        t.at("its atoms ring too"); t.play(amp.animate.set_value(1.0), ph.animate.increment_value(6 * PI), run_time=1.8, rate_func=linear)
        thz = label("terahertz: trillions of times a second", 26, ACC).to_edge(DOWN, buff=0.6)
        t.at("trillions of times"); t.play(FadeIn(thz), ph.animate.increment_value(5 * PI), run_time=1.2, rate_func=linear)
        cam = label("no camera is that fast", 26, GREY_B).next_to(thz, DOWN, buff=0.15)
        t.at("No camera"); t.play(FadeIn(cam), ph.animate.increment_value(4 * PI), amp.animate.set_value(0.4), run_time=1.0, rate_func=linear)
        for g in grid:
            g.clear_updaters()
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: pump, then probe
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        tl = NumberLine(x_range=[0, 6, 1], length=6, include_numbers=False, color=GREY_B).shift(UP * 2.6 + LEFT * 2.5)
        tl_l = label("time", 22, GREY_B).next_to(tl, RIGHT, buff=0.2)
        pump = Line(tl.n2p(0.5), tl.n2p(0.5) + UP * 0.6, color=PUMP, stroke_width=8)
        pump_l = label("pump (laser)", 22, PUMP).next_to(pump, UP, buff=0.1)
        t.at("A beamline uses two pulses"); t.play(Create(tl), FadeIn(tl_l), run_time=0.6)
        t.at("the pump"); t.play(Create(pump), FadeIn(pump_l), run_time=0.5)
        dly = ValueTracker(1.0)
        probe = always_redraw(lambda: Line(tl.n2p(0.5 + dly.get_value()), tl.n2p(0.5 + dly.get_value()) + UP * 0.6, color=XR, stroke_width=8))
        probe_l = always_redraw(lambda: label("probe (X-rays)", 22, XR).next_to(tl.n2p(0.5 + dly.get_value()) + UP * 0.6, UP, buff=0.1))
        brace = always_redraw(lambda: BraceBetweenPoints(tl.n2p(0.5), tl.n2p(0.5 + dly.get_value()), DOWN, color=ACC))
        brace_l = always_redraw(lambda: label("delay", 22, ACC).next_to(brace, DOWN, buff=0.05))
        t.at("An X-ray pulse"); t.play(FadeIn(probe), FadeIn(probe_l), run_time=0.5)
        t.at("a set delay later"); t.play(FadeIn(brace), FadeIn(brace_l), run_time=0.4)
        crystal = VGroup(*[Dot(LEFT * 4.6 + RIGHT * 0.3 * i + DOWN * (0.3 * j), radius=0.05) for i in range(5) for j in range(5)]).shift(DOWN * 0.3)
        det = Rectangle(width=1.6, height=2.0, color=WHITE).shift(RIGHT * 1.2 + DOWN * 0.9)
        det_l = label("detector", 22).next_to(det, DOWN, buff=0.15)
        beam_in = Arrow(LEFT * 6.8 + DOWN * 0.9, crystal.get_left() + LEFT * 0.05, color=XR, buff=0, stroke_width=5)
        rays = VGroup(*[Line(crystal.get_center(), det.get_left() + UP * (0.7 - 0.35 * i), color=XR, stroke_width=2) for i in range(5)])
        t.at("the X-rays it scatters"); t.play(FadeIn(crystal), Create(beam_in), FadeIn(det), FadeIn(det_l), run_time=0.7)
        t.play(Create(rays), run_time=0.5)
        rng = np.random.default_rng(3)
        def frame(k):
            img = rng.normal(0.5 + 0.3 * np.cos(1.3 * k), 0.08, (6, 5)).clip(0, 1)
            return VGroup(*[Square(0.3, stroke_width=0, fill_color=interpolate_color(ManimColor("#000000"), ManimColor(XR), float(v)), fill_opacity=1)
                            .move_to(det.get_center() + RIGHT * (0.3 * (i - 2)) + UP * (0.3 * (2.5 - j))) for j, row in enumerate(img) for i, v in enumerate(row)])
        f0 = frame(0)
        t.at("record where the atoms are"); t.play(FadeIn(f0), run_time=0.5)
        stack = VGroup()
        t.at("Then it repeats")
        for k in range(1, 6):
            fk = frame(k)
            ghost = f0.copy().scale(0.45).move_to(RIGHT * (3.4 + 0.42 * k) + DOWN * (0.6 + 0.12 * k))
            self.play(dly.animate.set_value(1.0 + 0.7 * k), Transform(f0, fk), FadeIn(ghost), run_time=0.45)
            stack.add(ghost)
        st_l = label("one frame per delay", 24, ACC).next_to(stack, DOWN, buff=0.25)
        t.at("one detector frame per delay"); t.play(FadeIn(st_l), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: laser on, laser off
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        delay, trace, on, off = d["delay"], d["trace"], d["on"], d["off"]
        ax1 = Axes(x_range=[0, 9.5, 2], y_range=[0.95, 1.07, 0.05], x_length=5.0, y_length=2.4, tips=False).shift(LEFT * 3.4 + UP * 1.2)
        on_n, off_n = on / off.mean(), off / off.mean()
        l_on = label("laser on", 22, PUMP).next_to(ax1, UP, buff=0.1).align_to(ax1, LEFT)
        l_off = label("laser off", 22, GREY_B).next_to(l_on, RIGHT, buff=0.4)
        x1l = label("delay (ps)", 20).next_to(ax1, DOWN, buff=0.1)
        y1l = label("brightness / monitor", 20).rotate(PI / 2).next_to(ax1, LEFT, buff=0.1)
        t.at("Frames taken without the laser"); t.play(FadeIn(ax1), FadeIn(x1l), FadeIn(y1l), FadeIn(l_off), Create(curve(ax1, delay, off_n, GREY_B, 2)), run_time=1.0)
        mon = label("each frame ÷ the beam monitor (i0)", 22, GREY_B).next_to(ax1, DOWN, buff=0.55)
        t.at("divided by a monitor"); t.play(FadeIn(mon), run_time=0.5)
        t.at("compare laser on"); t.play(FadeIn(l_on), Create(curve(ax1, delay, on_n, PUMP, 2)), run_time=1.0)
        ax2 = Axes(x_range=[0, 9.5, 2], y_range=[-0.02, 0.035, 0.01], x_length=5.0, y_length=2.6, tips=False).shift(RIGHT * 3.2 + UP * 0.2)
        x2l = label("delay (ps)", 20).next_to(ax2, DOWN, buff=0.1)
        tr_l = label("the trace: what the laser changed", 22, ACC).next_to(ax2, UP, buff=0.15)
        dots = VGroup(*[Dot(ax2.c2p(float(a), float(b)), radius=0.035, color=ACC) for a, b in zip(delay, trace)])
        t.at("delay by delay"); t.play(FadeIn(ax2), FadeIn(x2l), LaggedStart(*[FadeIn(p) for p in dots], lag_ratio=0.02), run_time=1.6)
        t.at("what's left"); t.play(FadeIn(tr_l), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: what xRay fits
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        ft, recon, modes, thz = d["fit_time"], d["recon"], d["modes"], d["thz"]
        ax = Axes(x_range=[0, 9.5, 2], y_range=[-0.02, 0.035, 0.01], x_length=8.0, y_length=2.6, tips=False).shift(UP * 1.7 + LEFT * 0.8)
        dots = VGroup(*[Dot(ax.c2p(float(a), float(b)), radius=0.035, color=GREY_B) for a, b in zip(delay, trace)])
        self.add(ax, dots)
        axm = [Axes(x_range=[0, 9.5, 2], y_range=[-0.025, 0.025, 0.01], x_length=8.0, y_length=1.3, tips=False).shift(DOWN * (0.6 + 1.5 * i) + LEFT * 0.8)
               for i in range(2)]
        t.at("damped oscillations"); t.play(*[FadeIn(a_) for a_ in axm], run_time=0.4)
        mcs = [curve(axm[i], ft, modes[i], MODE_C[i], 3) for i in range(2)]
        ml = [label(f"{thz[i]:.2f} THz", 24, MODE_C[i]).next_to(axm[i], RIGHT, buff=0.3) for i in range(2)]
        t.at("called modes"); t.play(Create(mcs[0]), Create(mcs[1]), FadeIn(ml[0]), FadeIn(ml[1]), run_time=1.2)
        words = ["a frequency", "a rate at which it dies away", "a strength"]
        wl = VGroup(*[label(w, 22, GREY_B) for w in words]).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(DR, buff=0.4)
        t.at("Each mode has a frequency"); t.play(FadeIn(wl[0]), run_time=0.3)
        t.at("a rate at which"); t.play(FadeIn(wl[1]), run_time=0.3)
        t.at("a strength"); t.play(FadeIn(wl[2]), run_time=0.3)
        fit = curve(ax, ft, recon, ACC, 4)
        t.at("together they follow"); t.play(Create(fit), run_time=1.2)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: every row, and this module
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        f_row, f_fit = d["f_row"], d["f_fit"]
        rows = len(f_row)
        detr = Rectangle(width=1.8, height=4.0, color=WHITE).shift(LEFT * 4.5 + UP * 0.3)
        axr = Axes(x_range=[0, 1.1, 0.25], y_range=[0, rows, 16], x_length=4.0, y_length=4.0, tips=False).shift(RIGHT * 0.2 + UP * 0.3)
        axr_x = label("frequency (THz)", 20).next_to(axr, DOWN, buff=0.1)
        axr_y = label("detector row", 20).rotate(PI / 2).next_to(axr, LEFT, buff=0.1)
        t.at("Each row of the detector"); t.play(FadeIn(detr), FadeIn(axr), FadeIn(axr_x), FadeIn(axr_y), run_time=0.6)
        bars = VGroup(*[Rectangle(width=1.8, height=4.0 / rows, stroke_width=0, fill_color=ACC, fill_opacity=0.0)
                        .move_to(detr.get_top() + DOWN * (4.0 / rows) * (r + 0.5)) for r in range(rows)])
        pts = VGroup(*[Dot(axr.c2p(float(f_fit[r]), rows - r - 0.5), radius=0.04, color=ACC) for r in range(rows)])
        self.add(bars)
        gpu = label("on a GPU: every row", 24, ACC).next_to(axr, UP, buff=0.2)
        t.at("rings at its own frequency")
        t.play(LaggedStart(*[AnimationGroup(bars[r].animate.set_fill(opacity=0.5), FadeIn(pts[r])) for r in range(rows)], lag_ratio=0.05), run_time=2.0)
        t.at("On a GPU"); t.play(FadeIn(gpu), run_time=0.4)
        t.at("In this module"); t.play(*[FadeOut(m) for m in self.mobjects], run_time=0.4)

        def card(num, txt):
            box = RoundedRectangle(corner_radius=0.15, width=3.9, height=1.7, color=WHITE)
            g = VGroup(label(num, 26, ACC), label(txt, 26)).arrange(DOWN, buff=0.2).move_to(box)
            return VGroup(box, g)

        cards = VGroup(card("7.1", "One trace"), card("7.2", "A mode goes missing"), card("7.3", "Every row on the GPU")).arrange(RIGHT, buff=0.4)
        t.at("fit one trace"); t.play(FadeIn(cards[0]), run_time=0.4)
        t.at("how a mode can go missing"); t.play(FadeIn(cards[1]), run_time=0.4)
        t.at("fit a whole detector"); t.play(FadeIn(cards[2]), run_time=0.4)
        q = label("a fit always returns modes: are they all there?", 30, ACC).to_edge(DOWN, buff=0.7)
        t.at("A fit always returns"); t.play(FadeIn(q), run_time=0.6)
        t.rest()
