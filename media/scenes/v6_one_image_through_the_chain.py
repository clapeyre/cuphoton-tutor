"""v6 - One image through the shipped chain.  Real data: v6.json, v6_target.npy (data_v6.py runs the chain)."""
from common import *
import json

VID = "v6-one-image-through-the-chain"
ACC = "#ffb000"
MONO = "Liberation Mono"


def mono(text, size=22, color=WHITE):
    return Text(text, font=MONO, font_size=size, color=color)


def ms(sec):
    return f"{sec * 1000:.0f} ms" if sec >= 0.001 else "<1 ms"


class V6(Scene):
    def construct(self):
        T = timings(VID)
        d = json.loads((DATA / "v6.json").read_text())
        thumb = np.load(DATA / "v6_target.npy")
        lo, hi = np.percentile(thumb, [30, 99.8])
        img = lambda h: to_image(np.arcsinh(np.clip(thumb - lo, 0, None) / (0.01 * (hi - lo))), "gray", 0, np.arcsinh(100), h)

        # ---------- s1: by hand, then by the thousand
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        names = ["xRep", "xPois", "detect", "xFit"]
        boxes = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.12, width=2.3, height=1.0, color=GREY_B), label(n, 30)) for n in names]).arrange(RIGHT, buff=0.5).shift(UP * 1.2)
        for b in boxes: b[1].move_to(b[0])
        calls = VGroup(*[label("one call", 22, GREY_B).next_to(b, DOWN, buff=0.2) for b in boxes])
        t.at("one call at a time"); t.play(LaggedStart(*[AnimationGroup(FadeIn(b), FadeIn(c)) for b, c in zip(boxes, calls)], lag_ratio=0.3), run_time=1.6)
        pair = Group(img(1.6), img(1.6)).arrange(RIGHT, buff=0.2).shift(DOWN * 1.8)
        t.at("one pair of images"); t.play(FadeIn(pair), run_time=0.5)
        stack = Group(*[img(1.6).shift(DOWN * 1.9 + LEFT * 1.2 + RIGHT * k * 0.22 + UP * k * 0.1) for k in range(12)])
        many = label("thousands of pairs a night", 30, ACC).next_to(stack, DOWN, buff=0.25)
        t.at("thousands of pairs"); t.play(ReplacementTransform(pair, stack), FadeIn(many), run_time=0.9)
        title = label("the transient chain", 44, ACC).move_to(UP * 1.2)
        t.at("one pipeline"); t.play(FadeOut(boxes), FadeOut(calls), FadeIn(title), run_time=0.7)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: one image through it
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        tm = d["timings"]
        stages = [("read", tm["read"], "reads the planes"), ("template", tm["template"], "puts the reference"),
                  ("refine + mask", tm["refine"] + tm["mask"], "on the target's grid"), ("xPois", tm["xpois"], "matches and subtracts"),
                  ("detect", tm["detect"], "finds the hotspots"), ("stamps", tm["stamps"], "cuts stamps"),
                  ("xFit", tm["xfit"], "fits them"), ("error budget", tm["uq"] + tm["uncertainty"], "builds an error bar")]
        gpu = RoundedRectangle(corner_radius=0.2, width=5.8, height=5.6, color=GREEN_B).shift(RIGHT * 0.3 + DOWN * 0.2)
        gl = label("GPU", 28, GREEN_B).next_to(gpu, UP, buff=0.15).align_to(gpu, LEFT)
        src = img(2.2).shift(LEFT * 5.0 + DOWN * 0.2)
        sl = label("target night (FITS)", 22).next_to(src, DOWN, buff=0.2)
        t.at("One worker"); t.play(FadeIn(src), FadeIn(sl), Create(gpu), FadeIn(gl), run_time=0.8)
        names_ = VGroup(*[label(n, 26) for n, _, _ in stages]).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        names_.move_to(gpu).shift(LEFT * 0.9)
        times_ = VGroup(*[mono(ms(sec), 22, GREY_B).move_to([gpu.get_right()[0] - 1.0, nm.get_center()[1], 0]) for nm, (_, sec, _) in zip(names_, stages)])
        rows = VGroup(*[VGroup(a, b) for a, b in zip(names_, times_)])
        dot = Dot(color=ACC, radius=0.12).next_to(rows[0], LEFT, buff=0.35)
        t.at("reads the planes"); t.play(FadeIn(rows[0]), FadeIn(dot), src.animate.set_opacity(0.4), run_time=0.4)
        for k in range(1, len(stages)):
            t.at(stages[k][2]); t.play(FadeIn(rows[k]), dot.animate.next_to(rows[k], LEFT, buff=0.35), run_time=0.35)
        stay = label("images stay on the GPU", 24, GREEN_B).next_to(gpu, DOWN, buff=0.2)
        t.at("stay on the GPU"); t.play(FadeIn(stay), Indicate(gpu, color=GREEN_B), run_time=0.7)
        tr = d["transfers"]
        out = VGroup(Arrow(gpu.get_right(), gpu.get_right() + RIGHT * 1.3, color=ACC, buff=0.05),
                     VGroup(label("one download:", 24, ACC), label(f"{tr['terminal_bytes'] / 1000:.1f} kB", 24, ACC),
                            label(f"intermediate files: {tr['intermediate_files']}", 20, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.12))
        out[1].next_to(out[0], RIGHT, buff=0.15)
        t.at("one small download"); t.play(GrowArrow(out[0]), FadeIn(out[1]), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: what comes back
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        sn = d["sn"]
        cat_t = label("catalog.parquet", 28, ACC).to_edge(UP, buff=0.5).shift(LEFT * 3.4)
        row = VGroup(mono(f"x {sn['x']:.0f}   y {sn['y']:.0f}", 24),
                     mono(f"psf_flux       {sn['psf_flux']:,.0f}", 24),
                     mono(f"psf_flux_err   {sn['psf_flux_err']:,.0f}", 24, ACC)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        terms = VGroup(mono(f"  _fit   {sn['psf_flux_err_fit']:,.0f}", 22, GREY_B), mono(f"  _corr  {sn['psf_flux_err_corr']:,.0f}", 22, GREY_B),
                       mono(f"  _kfit  {sn['psf_flux_err_kfit']:,.0f}", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        catg = VGroup(row, terms).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(cat_t, DOWN, buff=0.4).align_to(cat_t, LEFT)
        catbox = SurroundingRectangle(catg, color=GREY_B, buff=0.3, corner_radius=0.1)
        t.at("A catalog"); t.play(FadeIn(cat_t), Create(catbox), FadeIn(row[0]), run_time=0.6)
        t.at("a flux"); t.play(FadeIn(row[1]), run_time=0.3)
        t.at("an error bar"); t.play(FadeIn(row[2]), run_time=0.3)
        t.at("several terms"); t.play(LaggedStart(*[FadeIn(x) for x in terms], lag_ratio=0.3), run_time=0.9)
        sum_t = label("summary.json, every image", 28, ACC).to_edge(UP, buff=0.5).shift(RIGHT * 3.2)
        g = d["gpu"]
        lines = VGroup(mono(f'gpu: {g["name"].replace("NVIDIA GeForce ", "")}', 22),
                       mono(f'reader: {d["reader"]} (asked: {d["requested_reader"]})', 22),
                       mono(f'uq_terms: {", ".join(d["uq_terms"])}', 22),
                       mono(f'timings_sec: xpois {tm["xpois"]:.2f}, xfit {tm["xfit"]:.2f}, ...', 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        lines.next_to(sum_t, DOWN, buff=0.45).align_to(sum_t, LEFT).shift(LEFT * 0.6)
        sumbox = SurroundingRectangle(lines, color=GREY_B, buff=0.3, corner_radius=0.1)
        t.at("And a summary"); t.play(FadeIn(sum_t), Create(sumbox), run_time=0.5)
        for k, cue in enumerate(["which GPU", "which reader", "which error terms", "how long"]):
            t.at(cue); t.play(FadeIn(lines[k]), run_time=0.3)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: driven by a configuration
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        yaml = [(0, "survey:", WHITE), (1, "target: image, mask, variance", GREY_B), (2, "variance_kind: ...", GREY_B),
                (1, "template: on_target_grid: ...", GREY_B), (1, "mask_policy: ...", GREY_B),
                (0, "align: ...", WHITE), (0, "subtract: ...", WHITE), (0, "detect: ...", WHITE), (0, "stamps: ...", WHITE),
                (0, "xfit: ...", WHITE), (0, "uq: ...", WHITE)]
        def line_(s_, c):  # a trailing invisible "Íg" gives every line the same height and depth, so rows space evenly
            m = mono(s_ + " Íg", 24, c)
            m[-2:].set_opacity(0)
            return m
        ys = VGroup(*[line_(s_, c) for _, s_, c in yaml])
        for k, m in enumerate(ys):
            m.move_to(UP * (2.3 - k * 0.45), aligned_edge=LEFT).set_x(-6.4 + yaml[k][0] * 0.55, direction=LEFT)
        fname = label("config.yaml", 28, ACC).next_to(ys, UP, buff=0.35).align_to(ys, LEFT)
        frame = SurroundingRectangle(VGroup(ys, fname), color=GREY_B, buff=0.35, corner_radius=0.12)
        t.at("one configuration file"); t.play(FadeIn(fname), Create(frame), run_time=0.5)
        t.at("where each plane"); t.play(LaggedStart(*[FadeIn(x) for x in ys[:5]], lag_ratio=0.25), run_time=1.0)
        t.at("every stage's settings"); t.play(LaggedStart(*[FadeIn(x) for x in ys[5:]], lag_ratio=0.15), run_time=0.9)
        tag = VGroup(label("shipped values:", 30, ACC), label("chosen for another survey", 30, ACC)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(frame, RIGHT, buff=0.5).shift(UP * 0.5)
        t.at("It ships with"); t.play(FadeIn(tag), run_time=0.5)
        yours = label("yours is different", 28).next_to(tag, DOWN, buff=0.4)
        t.at("Yours is different"); t.play(FadeIn(yours), run_time=0.4)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: the question
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        q = VGroup(label("When the shipped pipeline says it's done,", 38), label("can you trust what it wrote,", 38),
                   label("on your data?", 38, ACC)).arrange(DOWN, buff=0.3)
        t.at("When the shipped"); t.play(FadeIn(q[0]), run_time=0.5)
        t.at("can you trust"); t.play(FadeIn(q[1]), run_time=0.4)
        t.at("on your data"); t.play(FadeIn(q[2]), run_time=0.4)
        t.rest()
