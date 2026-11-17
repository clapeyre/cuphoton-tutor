"""v9 - Many frames, one scene.  Real data: v9.npz (three frames of a close pair and a third source, each
with its own Gaussian PSF; xImage L2 snapshots after 1, 3, 10, 30, 75 steps and the loss per step;
data_v9.py)."""
from common import *

VID = "v9-many-frames"
ACC = "#ffb000"


def img(a, height, lo=None, hi=None):
    a = np.asarray(a, float)
    lo = np.percentile(a, 1) if lo is None else lo
    hi = a.max() if hi is None else hi
    return to_image(np.arcsinh(np.clip(a - lo, 0, None) / max((hi - lo) * 0.02, 1e-9)), cmap="magma", height=height)


class V9(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v9.npz")
        frames, psfs, med, snaps, loss = d["frames"], d["psfs"], d["median"], d["snaps"], d["loss"]
        steps = d["steps"]

        # ---------- s1: many frames
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        fr = Group(*[img(frames[..., k], 2.6) for k in range(3)]).arrange(RIGHT, buff=0.5).shift(UP * 0.7)
        ps = Group(*[img(psfs[..., k], 0.9, lo=0, hi=psfs.max()) for k in range(3)])
        for p, f in zip(ps, fr):
            p.next_to(f, DOWN, buff=0.35)
        t.at("Take several pictures"); t.play(LaggedStart(*[FadeIn(f) for f in fr], lag_ratio=0.4), run_time=1.5)
        pl = label("each frame's blur: its PSF", 24, ACC).next_to(ps, DOWN, buff=0.25)
        t.at("Each frame has its own blur"); t.play(LaggedStart(*[FadeIn(p) for p in ps], lag_ratio=0.3), FadeIn(pl), run_time=1.0)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: stacking keeps the blur
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        fr = Group(*[img(frames[..., k], 2.6) for k in range(3)]).arrange(RIGHT, buff=0.5).shift(UP * 0.7)
        self.add(fr)
        m = img(med, 3.2).shift(UP * 0.5)
        t.at("Stacking them"); t.play(*[f.animate.move_to(m).set_opacity(0.4) for f in fr], run_time=0.9)
        self.remove(*fr); self.add(m)
        ml = label("the median: less noise, same blur", 26).next_to(m, DOWN, buff=0.3)
        t.at("beats down the noise"); t.play(FadeIn(ml), run_time=0.5)
        pair = Circle(radius=0.55, color=ACC, stroke_width=4).move_to(pix(m, med.shape, 30.5 - 8, 31 - 8))
        t.at("Two sources close together"); t.play(Create(pair), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: working backwards
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        sc = img(snaps[0], 2.4, lo=0, hi=snaps[-1].max()).shift(LEFT * 4.6 + UP * 0.9)
        sc_l = label("scene (guess)", 22).next_to(sc, UP, buff=0.15)
        t.at("starts from a guess"); t.play(FadeIn(sc), FadeIn(sc_l), run_time=0.6)
        rows = Group()
        for k in range(3):
            pk = img(psfs[..., k], 0.55, lo=0, hi=psfs.max())
            fk = img(frames[..., k], 1.2)
            r = Group(label("⊛", 30), pk, label("vs", 22), fk).arrange(RIGHT, buff=0.25)
            rows.add(r)
        rows.arrange(DOWN, buff=0.3).shift(RIGHT * 0.2 + UP * 0.9)
        t.at("blurs the guess"); t.play(LaggedStart(*[FadeIn(r[:2]) for r in rows], lag_ratio=0.3), run_time=0.9)
        t.at("compares the result"); t.play(LaggedStart(*[FadeIn(r[2:]) for r in rows], lag_ratio=0.3), run_time=0.9)
        back = CurvedArrow(rows.get_bottom() + DOWN * 0.1 + LEFT * 0.5, sc.get_bottom() + DOWN * 0.1, angle=-TAU / 5, color=ACC)
        adj = label("adjust", 22, ACC).next_to(back, DOWN, buff=0.05)
        t.at("adjusts the scene"); t.play(Create(back), FadeIn(adj), run_time=0.7)
        ax = Axes(x_range=[0, 75, 25], y_range=[0, 2.0, 1], x_length=3.0, y_length=2.0, tips=False).shift(RIGHT * 4.9 + UP * 0.6)
        ax_l = label("loss (log)", 20).next_to(ax, UP, buff=0.1)
        ax_x = label("step", 20).next_to(ax, DOWN, buff=0.1)
        ll = np.log10(np.maximum(loss, 1))
        stepc = label("step 1", 24, ACC).next_to(sc, LEFT, buff=0.15)
        t.at("Step by step"); t.play(FadeIn(ax), FadeIn(ax_l), FadeIn(ax_x), FadeIn(stepc), run_time=0.5)
        prev = 0
        for s_, snap in zip(steps[1:], snaps[1:]):
            new = img(snap, 2.4, lo=0, hi=snaps[-1].max()).move_to(sc)
            seg = VMobject(color=ACC, stroke_width=3).set_points_as_corners([ax.c2p(i + 1, ll[i]) for i in range(prev, int(s_))])
            self.play(FadeTransform(sc, new), Create(seg), Transform(stepc, label(f"step {s_}", 24, ACC).move_to(stepc)), run_time=0.8)
            sc = new; prev = int(s_) - 1
        t.at("falls toward the noise"); t.play(Indicate(ax_l, color=ACC), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: one scene
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        m = img(med, 3.2).shift(LEFT * 2.6 + UP * 0.4)
        s = img(snaps[-1], 3.2, lo=0).shift(RIGHT * 2.6 + UP * 0.4)
        ml = label("median of the frames", 24).next_to(m, DOWN, buff=0.2)
        sl = label("xImage's scene", 24, ACC).next_to(s, DOWN, buff=0.2)
        t.at("What comes back"); t.play(FadeIn(m), FadeIn(ml), FadeIn(s), FadeIn(sl), run_time=0.8)
        pairs = [Circle(radius=0.6, color=ACC, stroke_width=4).move_to(pix(im_, med.shape, 30.5 - 8, 31 - 8)) for im_ in (m, s)]
        t.at("The pair"); t.play(*[Create(p) for p in pairs], run_time=0.6)
        card = VGroup(RoundedRectangle(corner_radius=0.12, width=5.2, height=0.8, color=GREY_B),
                      label("receipt: device · steps · loss", 24, GREY_B)).arrange(ORIGIN).to_edge(DOWN, buff=0.4)
        t.at("a receipt"); t.play(FadeIn(card), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: this module
        self.next_section("s5"); t = Timed.seg(self, T, "s5")

        def cardf(num, txt):
            box = RoundedRectangle(corner_radius=0.15, width=3.9, height=1.7, color=WHITE)
            g = VGroup(label(num, 26, ACC), label(txt, 26)).arrange(DOWN, buff=0.2).move_to(box)
            return VGroup(box, g)

        cards = VGroup(cardf("8.1", "A known scene"), cardf("8.2", "A star that\nwasn't there"), cardf("8.3", "Four nights of M101")).arrange(RIGHT, buff=0.4)
        t.at("reconstruct a scene you know"); t.play(FadeIn(cards[0]), run_time=0.4)
        t.at("look for what went wrong"); t.play(FadeIn(cards[1]), run_time=0.4)
        t.at("reconstruct the nights"); t.play(FadeIn(cards[2]), run_time=0.4)
        q = label("a sharp picture: is it a true one?", 30, ACC).to_edge(DOWN, buff=0.7)
        t.at("The question is"); t.play(FadeIn(q), run_time=0.6)
        t.rest()
