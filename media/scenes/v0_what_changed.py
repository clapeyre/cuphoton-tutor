"""v0 - What changed in the sky?  One section per narration segment.
Render: pipeline/render.sh v0-what-changed v0_what_changed.py V0"""
from common import *

VID = "v0-what-changed"
ACC = "#ffb000"
SKY = "#8fb8ff"


def sky_frame(rng_seed, w=2.4, h=1.6, n=14, new=None, bright=None, color=WHITE):
    """Schematic star field in a rectangle (generic, not the course pair)."""
    rng = np.random.default_rng(rng_seed)
    pts = rng.uniform([-w / 2 + 0.15, -h / 2 + 0.15], [w / 2 - 0.15, h / 2 - 0.15], (n, 2))
    g = VGroup(Rectangle(width=w, height=h, color=GREY_B, stroke_width=3, fill_color="#0b0d12", fill_opacity=1))
    for i, p in enumerate(pts):
        r = 0.035 + 0.03 * rng.random()
        if bright == i:
            r *= 2.2
        g.add(Dot([p[0], p[1], 0], radius=r, color=color))
    if new is not None:
        g.add(Dot([new[0] * w / 2, new[1] * h / 2, 0], radius=0.06, color=color))
    return g, pts


def person_icon():
    head = Circle(radius=0.2, color=WHITE)
    body = Arc(radius=0.38, start_angle=0, angle=PI, color=WHITE).next_to(head, DOWN, buff=0.05)
    mag_c = Circle(radius=0.16, color=GREEN)
    mag_h = Line(mag_c.get_center() + DR * 0.115, mag_c.get_center() + DR * 0.34, color=GREEN)
    mag = VGroup(mag_c, mag_h).next_to(VGroup(head, body), RIGHT, buff=0.12)
    return VGroup(head, body, mag)


class V0(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v0.npz")
        ref, tgt, crop = d["ref"], d["tgt"], d["crop"]
        sy, sx = d["star"]
        rlo, rhi = np.percentile(ref, [1, 99.3]); tlo, thi = np.percentile(tgt, [1, 99.3])

        # One made-up star field, shared by s1 thumbnails, the s2 flipbook and s5
        W, H = 6.0, 4.0
        c0 = UP * 0.0
        rb = np.random.default_rng(3)
        base = rb.uniform([-W / 2 + 0.3, -H / 2 + 0.3], [W / 2 - 0.3, H / 2 - 0.3], (22, 2))
        sizes = 0.04 + 0.03 * rb.random(22)
        cands = [np.array([x, y]) for x in np.linspace(-2.4, 2.4, 25) for y in np.linspace(-1.4, 1.4, 15)]
        newp = max(cands, key=lambda c: np.min(np.linalg.norm(base - c, axis=1)))
        BR = 6  # the star that brightens
        # keep the brightening star away from the frame edge and the new point
        FD = int(np.argmin(np.linalg.norm(base - (-base[BR]), axis=1)))  # a star far from BR, fades
        if FD == BR: FD = (BR + 5) % len(base)
        # asteroid path: a straight run through the emptiest band, away from the new point
        mv0 = np.array([-2.2, -1.5]); mv1 = np.array([-0.4, -0.9])
        def mvpos(j):
            return mv0 + (mv1 - mv0) * j / 5
        def field(k, new=False, bright=False, faint=False, move=None):
            rr = np.random.default_rng(1000 + k)
            g = VGroup(Rectangle(width=W, height=H, color=GREY_B, stroke_width=3, fill_color="#0b0d12", fill_opacity=1))
            for i, p in enumerate(base):
                q = p + rr.normal(0, 0.012, 2)
                r = sizes[i] * (2.3 if (bright and i == BR) else 1.0)
                op = 1.0
                if faint and i == FD:
                    r *= 0.45; op = 0.45
                g.add(Dot([q[0], q[1], 0], radius=r, color=WHITE).set_opacity(op))
            for q in rr.uniform([-W / 2 + 0.05, -H / 2 + 0.05], [W / 2 - 0.05, H / 2 - 0.05], (40, 2)):
                g.add(Dot([q[0], q[1], 0], radius=0.014, color=GREY_C).set_opacity(0.5 * rr.random() + 0.2))
            if new:
                q = newp + rr.normal(0, 0.012, 2)
                g.add(Dot([q[0], q[1], 0], radius=0.065, color=WHITE))
            if move is not None:
                q = mvpos(move)
                g.add(Dot([q[0], q[1], 0], radius=0.05, color=WHITE))
            return g.move_to(c0)
        # ---------- s1: camera in the garden
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        ground = Line(LEFT * 7, RIGHT * 1.2, color=GREEN_E, stroke_width=4).shift(DOWN * 2.6)
        grass = VGroup(*[Line([x, -2.6, 0], [x + 0.08, -2.4, 0], color=GREEN_E, stroke_width=3) for x in np.arange(-6.8, 1.2, 0.35)])
        legs = VGroup(*[Line([-3.5, -1.0, 0], [-3.5 + dx, -2.6, 0], color=GREY_B, stroke_width=4) for dx in (-0.6, 0, 0.6)])
        cam = VGroup(Rectangle(width=0.9, height=0.55, color=WHITE, stroke_width=4),
                     Rectangle(width=0.35, height=0.35, color=WHITE, stroke_width=4).shift(UP * 0.4 + LEFT * 0.1),
                     ).move_to([-3.5, -0.75, 0]).rotate(PI / 2.6)
        bg_stars = VGroup(*[Dot([x, y, 0], radius=0.03, color=SKY) for x, y in
                            [(-6, 2.8), (-5.1, 1.5), (-4.4, 3.0), (-3.1, 2.2), (-2.2, 3.1), (-1.0, 2.0), (-0.2, 2.9), (0.6, 1.4), (-5.8, 0.4), (-1.6, 0.9)]])
        patch = DashedVMobject(Circle(radius=0.55, color=SKY, stroke_width=2).move_to([-2.4, 1.9, 0]))
        beam = VGroup(Line([-3.2, -0.5, 0], [-2.8, 1.45, 0], color=SKY, stroke_width=1.5),
                      Line([-3.2, -0.5, 0], [-2.0, 1.5, 0], color=SKY, stroke_width=1.5))
        cap = label("same camera, same patch of sky, every clear night", 26).to_edge(UP, buff=0.35)
        t.play(FadeIn(ground), FadeIn(grass), FadeIn(legs), FadeIn(cam), FadeIn(bg_stars), run_time=1.0)
        t.at("and point it"); t.play(Create(patch), Create(beam), run_time=0.8)
        t.at("Every clear night"); t.play(FadeIn(cap), run_time=0.6)
        t.at("you take a picture")
        slots = [RIGHT * 2.6 + UP * 1.7, RIGHT * 4.45 + UP * 1.7, RIGHT * 2.6 + DOWN * 0.3]
        names = ["night 1", "night 2", "night 3"]
        thumbs = []
        for i in range(3):
            f = field(i).scale(0.14)  # same stars every night, tiny jitter
            f.move_to([-2.4, 1.9, 0])
            flash = Flash(f.get_center(), color=WHITE, flash_radius=0.7, line_length=0.15)
            t.play(FadeIn(f, scale=0.6), flash, run_time=0.6)
            lab = label(names[i], 22)
            target_f = f.copy().scale(0.248 / 0.14).move_to(slots[i])
            lab.next_to(target_f, DOWN, buff=0.1)
            t.play(Transform(f, target_f), FadeIn(lab), run_time=0.9)
            thumbs.append(VGroup(f, lab))
            if i < 2:
                t.wait(0.2)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: flipbook of ONE star field
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        title = label("real changes in the sky", 36, ACC).to_edge(UP, buff=0.35)
        cap = label("a week of pictures of the same stars", 28).to_edge(DOWN, buff=0.45)
        cur = field(0)
        t.play(FadeIn(cur), FadeIn(cap), run_time=0.8)
        def show(k, hold, **kw):
            nonlocal cur
            self.remove(cur); cur = field(k, **kw); self.add(cur); t.wait(hold)
        state = {}
        rings = VGroup()
        nxt = [1]
        def flip_until(phrase, hold=0.45):
            """Keep flipping frames (current changes kept, rings on top) until the voice reaches `phrase`."""
            nonlocal cur
            tt = t.when(phrase) - 0.15
            while tt - t.used > hold:
                self.remove(cur); cur = field(nxt[0], **state); self.add(cur); self.bring_to_front(rings)
                nxt[0] += 1; t.wait(hold)
            t._from -= 1  # let t.at find the same phrase again
            t.at(phrase)
        def ring(xy):
            return Circle(radius=0.3, color=GREEN, stroke_width=5).move_to(np.array([xy[0], xy[1], 0]) + c0)
        def add_change(phrase, xy, **kw):
            nonlocal cur
            flip_until(phrase)
            state.update(kw)
            self.remove(cur); cur = field(nxt[0], **state); self.add(cur); nxt[0] += 1
            c = ring(xy); rings.add(c); self.add(rings); t.play(Create(c), run_time=0.3)
        # changes accumulate, each ringed as the voice names it
        add_change("brighter", base[BR], bright=True)
        add_change("fainter", base[FD], faint=True)
        add_change("a new point", newp, new=True)
        flip_until("or something moves")
        path = DashedLine(np.array([*mv0, 0]) + c0, np.array([*mv1, 0]) + c0, color=GREEN, stroke_width=3)
        self.add(path)
        for jj in range(6):
            self.remove(cur); state["move"] = jj; cur = field(nxt[0], **state); self.add(cur); nxt[0] += 1
            self.bring_to_front(rings, path); t.wait(0.3)
        flip_until("These real changes")
        t.play(FadeIn(title), FadeOut(rings), FadeOut(path), run_time=0.6)
        state.clear()
        flip_until("survey telescopes")
        cap2 = label("survey telescopes: large parts of the sky, every few nights", 28).to_edge(DOWN, buff=0.45)
        t.play(Transform(cap, cap2), run_time=0.6)
        # keep flipping gently so the picture is alive until the end
        k = 40
        while t.total - t.used > 0.6:
            show(k, 0.6); k += 1
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: what a picture is
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        img = to_image(ref, "magma", rlo, rhi, 5.4).shift(UP * 0.2)
        cap = label("a picture of the sky", 28).to_edge(DOWN, buff=0.4)
        t.play(FadeIn(img), FadeIn(cap), run_time=0.8)
        box = Square(side_length=5.4 * 9 / ref.shape[0] * 3, color=ACC, stroke_width=4).move_to(pix(img, ref.shape, sy, sx))
        t.play(Create(box), run_time=0.5)
        cell = 0.6; n = 9
        grid = VGroup()
        lo, hi = 90, 540
        cmap = colormaps["magma"]
        cells = {}
        for j in range(n):
            for i in range(n):
                v = crop[n - 1 - j, i]
                col = "#%02x%02x%02x" % tuple((np.array(cmap(np.clip((v - lo) / (hi - lo), 0, 1))[:3]) * 255).astype(int))
                sq = Square(side_length=cell, stroke_width=1.5, stroke_color=GREY_C, fill_color=col, fill_opacity=1)
                sq.move_to([(i - 4) * cell - 1.8, (j - 4) * cell + 0.1, 0])
                tx = label(str(v), 16, WHITE if v < 330 else BLACK).move_to(sq)
                grid.add(VGroup(sq, tx)); cells[(n - 1 - j, i)] = grid[-1]
        t.at("a grid of numbers")
        t.play(FadeOut(img), FadeOut(box), FadeOut(cap), FadeIn(grid, scale=0.4), run_time=1.0)

        def ctr(r, c):
            return np.array([(c - 4) * cell - 1.8, (4 - r) * cell + 0.1, 0])
        def tag(text, color, cells_rc, side, dist=1.0):
            """Outline the cells (r0,c0,r1,c1), then a label with a straight arrow that stops outside the grid."""
            r0, c0, r1, c1 = cells_rc
            lo_, hi_ = ctr(r1, c0), ctr(r0, c1)
            box = Rectangle(width=hi_[0] - lo_[0] + cell, height=hi_[1] - lo_[1] + cell, color=color, stroke_width=5).move_to((lo_ + hi_) / 2)
            lab = label(text, 24, color)
            if side == "R":
                y = box.get_center()[1]; edge = np.array([0.9, y, 0]); lab.move_to([3.2 + lab.width / 2 - 0.2, y, 0])
                arr = Arrow(lab.get_left() + LEFT * 0.1, edge + RIGHT * 0.02, buff=0.1, stroke_width=3, color=color)
                if box.get_right()[0] < 0.9:
                    arr = VGroup(arr, Line(edge, box.get_right(), color=color, stroke_width=2))
            elif side == "L":
                y = box.get_center()[1]; edge = np.array([-4.5, y, 0]); lab.move_to([-5.2 - lab.width / 2 + 0.2, y, 0])
                arr = Arrow(lab.get_right() + RIGHT * 0.1, edge, buff=0.1, stroke_width=3, color=color)
                if box.get_left()[0] > -4.5:
                    arr = VGroup(arr, Line(edge, box.get_left(), color=color, stroke_width=2))
            else:
                x = box.get_center()[0]; lab.move_to([x, -3.25, 0])
                arr = Arrow(lab.get_top(), [x, -2.62, 0], buff=0.05, stroke_width=3, color=color)
            return VGroup(box, lab, arr)
        tags = [tag("pixel value (counts)", SKY, (1, 8, 1, 8), "R"),
                tag("source", ACC, (2, 2, 6, 6), "R"),
                tag("background", GREEN_B, (7, 0, 8, 1), "L"),
                tag("noise", RED_B, (8, 4, 8, 5), "B")]
        for tg, cue in zip(tags, ("Each pixel value", "A star is", "Around it", "Even two pixels")):
            t.at(cue); t.play(FadeIn(tg), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)
        # ---------- s4: nights aren't identical
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        pw, ph = 3.0, 3.3
        centers = [LEFT * 4.65 + DOWN * 0.1, LEFT * 1.55 + DOWN * 0.1, RIGHT * 1.55 + DOWN * 0.1, RIGHT * 4.65 + DOWN * 0.1]
        def panel(title, c):
            fr = RoundedRectangle(corner_radius=0.12, width=pw, height=ph, color=GREY_B, stroke_width=2).move_to(c)
            tt = label(title, 24, ACC).next_to(fr, UP, buff=0.12)
            return fr, tt
        # 1 pointing
        fr, tt = panel("pointing", centers[0])
        a = Rectangle(width=1.5, height=1.0, color=GREY_B, stroke_width=3).move_to(centers[0] + UP * 0.1)
        b = Rectangle(width=1.5, height=1.0, color=SKY, stroke_width=4).move_to(centers[0] + UP * 0.1).shift(RIGHT * 0.3 + UP * 0.2).rotate(8 * DEGREES)
        n1 = label("night 1", 18, GREY_B).next_to(a, DOWN, buff=0.45).shift(LEFT * 0.4); n2 = label("night 2", 18, SKY).next_to(b, DOWN, buff=0.1).shift(RIGHT * 0.3 + DOWN * 0.38)
        p1 = VGroup(fr, tt, a, b, n1, n2)
        # 2 background
        fr, tt = panel("background", centers[1])
        strips = VGroup(*[Rectangle(width=2.4, height=1.8 / 12, stroke_width=0, fill_opacity=1,
                                    fill_color=interpolate_color(ManimColor("#05060c"), ManimColor("#5b6a8a"), k / 11)) for k in range(12)])
        strips.arrange(DOWN, buff=0).move_to(centers[1] + DOWN * 0.1)
        moon = Circle(radius=0.22, color="#f5e8a8", fill_color="#f5e8a8", fill_opacity=1).move_to(centers[1] + UP * 0.55 + RIGHT * 0.7)
        cm = Circle(radius=0.2, color="#05060c", fill_color="#05060c", fill_opacity=1, stroke_width=0).move_to(moon).shift(RIGHT * 0.12 + UP * 0.05)
        hz = label("dark -> hazy", 18, GREY_A).next_to(strips, DOWN, buff=0.1)
        p2 = VGroup(fr, tt, strips, moon, cm, hz)
        # 3 exposure time
        fr, tt = panel("exposure time", centers[2])
        def watch(c, sec, ang):
            ring = Circle(radius=0.5, color=WHITE, stroke_width=4).move_to(c)
            knob = Line(c + UP * 0.5, c + UP * 0.66, color=WHITE, stroke_width=5)
            hand = Line(c, c + 0.38 * np.array([np.sin(ang), np.cos(ang), 0]), color=ACC, stroke_width=4)
            return VGroup(ring, knob, hand, label(sec, 22).next_to(ring, DOWN, buff=0.15))
        w1 = watch(centers[2] + LEFT * 0.7 + UP * 0.2, "30 s", PI / 2 * 0.0 + 1.0); w2 = watch(centers[2] + RIGHT * 0.75 + UP * 0.2, "60 s", 2.1)
        vs = label("vs", 20, GREY_B).move_to(centers[2] + UP * 0.2)
        p3 = VGroup(fr, tt, w1, w2, vs)
        # 4 seeing
        fr, tt = panel("seeing", centers[3])
        waves = VGroup(*[FunctionGraph(lambda x, k=k: 0.07 * np.sin(5 * x + k * 1.3), x_range=[-1.2, 1.2], color=SKY, stroke_width=2.5).move_to(centers[3] + UP * (1.1 - k * 0.22)) for k in range(4)])
        sharp = Dot(centers[3] + DOWN * 0.2 + LEFT * 0.7, radius=0.05, color=WHITE)
        blob = VGroup(*[Circle(radius=r, stroke_width=0, fill_color=WHITE, fill_opacity=o) for r, o in ((0.3, 0.12), (0.2, 0.2), (0.1, 0.4))]).move_to(centers[3] + DOWN * 0.2 + RIGHT * 0.7)
        arr4 = Arrow(centers[3] + DOWN * 0.2 + LEFT * 0.35, centers[3] + DOWN * 0.2 + RIGHT * 0.3, buff=0, stroke_width=3, color=GREY_B, max_tip_length_to_length_ratio=0.3)
        pl = VGroup(label("sharp", 18, GREY_B).next_to(sharp, DOWN, buff=0.25), label("smeared", 18, GREY_B).next_to(blob, DOWN, buff=0.25))
        p4 = VGroup(fr, tt, waves, sharp, blob, arr4, pl)
        panels = [p1, p2, p3, p4]
        title4 = label("observing conditions", 36, ACC).to_edge(UP, buff=0.3)
        sub4 = label("how each picture was taken", 24, GREY_A).next_to(title4, DOWN, buff=0.12)
        def at(x):
            w = x - t.used
            if w > 0: t.wait(w)
        t.at("they weren't all taken"); t.play(FadeIn(sub4), run_time=0.6)
        t.at("the observing conditions"); t.play(FadeIn(title4), run_time=0.6)
        t.at("The camera may point"); t.play(FadeIn(p1), run_time=0.6)
        t.at("The moon"); t.play(FadeIn(p2), run_time=0.6)
        t.at("You might change"); t.play(FadeIn(p3), run_time=0.6)
        t.at("And starlight"); t.play(FadeIn(p4), run_time=0.6)
        psf = VGroup(label("PSF, point-spread function:", 26, ACC), label("the shape one point of light takes in the image", 26, ACC)).arrange(DOWN, buff=0.1).to_edge(DOWN, buff=0.4)
        t.at("The shape that one"); t.play(FadeIn(psf), run_time=0.6)
        # end: two reasons, side by side
        t.at("So two pictures")
        real = label("real changes in the sky", 36, ACC)
        obs = label("observing conditions", 36, SKY)
        real.move_to(LEFT * 3.4 + UP * 0.3); obs.move_to(RIGHT * 3.4 + UP * 0.3)
        div = Line(UP * 1.6, DOWN * 1.2, color=GREY_B, stroke_width=3)
        t.play(FadeOut(VGroup(p1, p2, p3, p4, psf, sub4)), FadeOut(title4), run_time=0.4)
        t.at("the sky really changed"); t.play(FadeIn(real), Create(div), run_time=0.5)
        t.at("the observing conditions did"); t.play(FadeIn(obs), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: two names
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        ri = field(30).scale(0.62).move_to(LEFT * 3.4 + UP * 0.5)
        ti = field(31).scale(0.62).move_to(RIGHT * 3.4 + UP * 0.5)
        l1 = label("reference image", 30, SKY).next_to(ri, DOWN, buff=0.3); s1_ = label("usually earlier, compared against", 22, GREY_A).next_to(l1, DOWN, buff=0.15)
        l2 = label("target image", 30, ACC).next_to(ti, DOWN, buff=0.3); s2_ = label("new, searched for changes", 22, GREY_A).next_to(l2, DOWN, buff=0.15)
        t.play(FadeIn(ri), FadeIn(l1), run_time=0.6)
        t.at("It's usually"); t.play(FadeIn(s1_), run_time=0.5)
        t.at("The new picture"); t.play(FadeIn(ti), FadeIn(l2), FadeIn(s2_), run_time=0.6)
        t.rest()
        # ---------- s6: in this module
        self.next_section("s6"); t = Timed.seg(self, T, "s6")
        def at(x):
            w = x - t.used
            if w > 0: t.wait(w)
        t.play(*[FadeOut(m) for m in (ri, ti, l1, l2, s1_, s2_)], run_time=0.6)
        title = label("Module 00: What changed in the sky?", 40, WHITE).to_edge(UP, buff=0.5)
        t.play(FadeIn(title), run_time=0.7)
        X0, X1 = -5.8, -3.7
        def row(name, color, y):
            return label(name, 32, color).move_to([X0, y, 0], aligned_edge=LEFT)
        def txt(s_, y, color=WHITE, size=30):
            return label(s_, size, color).move_to([X1, y, 0], aligned_edge=LEFT)
        r1 = VGroup(row("Start", GREEN_B, 1.5), txt("what a picture is made of", 1.5))
        r2 = VGroup(row("Do", ACC, 0.35), txt("find how two pictures differ", 0.6))
        r2b = txt("->  plan how to keep only the real changes", 0.05)
        r3 = VGroup(row("Finish", SKY, -0.95), txt("meet the cuPhoton stages that carry out your plan", -0.95))
        small = VGroup(label("made-up images", 24, GREY_A), label("·", 24, GREY_A), label("you won't write code", 24, GREY_A),
                       label("·", 24, GREY_A), label("no telescope data yet", 24, GREY_A)).arrange(RIGHT, buff=0.3).move_to([0, -1.95, 0])
        you = person_icon().scale(0.9).move_to(LEFT * 3.0 + DOWN * 2.95)
        yl = label("you think", 24, GREEN).next_to(you, RIGHT, buff=0.25)
        term = VGroup(RoundedRectangle(corner_radius=0.1, width=1.1, height=0.75, color=BLUE_B), label(">_", 28, BLUE_B))
        term[1].move_to(term[0]); term.move_to(RIGHT * 1.6 + DOWN * 2.95)
        al = label("your tutor types", 24, BLUE_B).next_to(term, RIGHT, buff=0.25)
        t.at("made-up pictures"); t.play(FadeIn(small[0]), run_time=0.5)
        t.at("You'll start"); t.play(FadeIn(r1, shift=RIGHT * 0.2), run_time=0.5)
        t.at("Then you'll find"); t.play(FadeIn(r2, shift=RIGHT * 0.2), run_time=0.5)
        t.at("work out a plan"); t.play(FadeIn(r2b, shift=RIGHT * 0.2), run_time=0.5)
        t.at("You'll finish"); t.play(FadeIn(r3, shift=RIGHT * 0.2), run_time=0.5)
        t.at("You won't write"); t.play(FadeIn(small[1:3]), run_time=0.5)
        t.at("no real telescope"); t.play(FadeIn(small[3:]), run_time=0.5)
        t.at("it does the typing"); t.play(FadeIn(term), FadeIn(al), run_time=0.5)
        t.at("you do the thinking"); t.play(FadeIn(you), FadeIn(yl), run_time=0.5)
        t.rest()
