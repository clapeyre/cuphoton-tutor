"""v2 - It ran. Is it right?  Real data: quickstart summary.json (--profile auto, CPU host), v1.npz, v2.json."""
from common import *
import json

VID = "v2-it-ran"
ACC = "#ffb000"
MONO = "Liberation Mono"


def mono(text, size=22, color=WHITE):
    return Text(text, font=MONO, font_size=size, color=color)


class V2(Scene):
    def construct(self):
        T = timings(VID)
        d = np.load(DATA / "v1.npz")
        rows = json.loads((DATA / "v2.json").read_text())
        qs = json.loads((DATA / "quickstart_auto" / "summary.json").read_text())
        # ---------- s1
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        term = RoundedRectangle(corner_radius=0.12, width=9, height=4, color=GREY_B, fill_color="#0b0c0e", fill_opacity=1).shift(UP * 0.3)
        l1 = mono("$ agent: run the pipeline", 24, GREY_B).move_to(term.get_corner(UL) + RIGHT * 0.4 + DOWN * 0.6, aligned_edge=LEFT)
        l2 = mono("  align ... ok", 24, GREY_B).next_to(l1, DOWN, aligned_edge=LEFT)
        l3 = mono("  subtract ... ok", 24, GREY_B).next_to(l2, DOWN, aligned_edge=LEFT)
        l4 = mono("  done", 28, GREEN).next_to(l3, DOWN, aligned_edge=LEFT, buff=0.35)
        t.play(FadeIn(term), Write(l1), run_time=0.6)
        t.at("No errors"); t.play(FadeIn(l2), FadeIn(l3), run_time=0.5)
        t.at("a green light"); t.play(FadeIn(l4), run_time=0.4)
        tick = label("✓", 150, GREEN).move_to(term)
        t.at("tempting"); t.play(FadeOut(term), FadeOut(l1), FadeOut(l2), FadeOut(l3), FadeOut(l4), FadeIn(tick), run_time=0.8)
        q = label("?", 170, ACC).move_to(tick)
        t.at("But it ran"); t.play(Transform(tick, q), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        req = mono('"run this on the GPU"', 30, BLUE_B).to_edge(UP, buff=0.8)
        t.at("where did it"); t.play(FadeIn(req), run_time=0.5)
        r = qs["results"]
        lines = [("summary.json  (quickstart, --profile auto)", GREY_B),
                 (f'  "gpu_available": {str(qs["hardware"]["gpu_available"]).lower()},', ACC),
                 (f'  "torch": {{"cuda_available": {str(qs["hardware"]["torch"]["cuda_available"]).lower()}}},', WHITE)]
        for k in ("xrep", "xpois", "xscan"):
            lines.append((f'  "{k}": {{"backend": "{r[k]["backend"]}", "device": "{r[k]["device"]}"}},', ACC if r[k]["device"] == "cpu" else WHITE))
        grp = VGroup(*[mono(s, 22, c) for s, c in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        panel = RoundedRectangle(corner_radius=0.12, width=grp.width + 1.2, height=grp.height + 0.7, color=GREY_B, fill_color="#0b0c0e", fill_opacity=1).move_to(DOWN * 0.7)
        grp.move_to(panel)
        note = VGroup(label("backend auto: tries the GPU,", 38, ACC), label("falls back to the CPU", 38, ACC)).arrange(DOWN, buff=0.3).move_to(DOWN * 0.5)
        ok = label("run succeeds", 38, GREEN).next_to(note, DOWN, buff=0.5)
        t.at("auto"); t.play(FadeIn(note[0]), run_time=0.4)
        t.at("falls back"); t.play(FadeIn(note[1]), run_time=0.4)
        t.at("still succeeds"); t.play(FadeIn(ok), run_time=0.4)
        boxes = VGroup(*[SurroundingRectangle(grp[i], color=ACC, buff=0.06) for i in (1, 2, 4, 5)])
        small = VGroup(label("auto: tries the GPU, falls back to the CPU", 26, ACC)).to_edge(DOWN, buff=0.35)
        t.at("The only trace"); t.play(FadeOut(ok), ReplacementTransform(note, small), FadeIn(panel), FadeIn(grp), run_time=0.6)
        t.at("the receipt"); t.play(Create(boxes), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        good = to_image(d["z"], "RdBu_r", -6, 6, 4.6).shift(LEFT * 3.5 + UP * 0.3)
        bad = to_image(d["z_bad"], "RdBu_r", -6, 6, 4.6).shift(RIGHT * 3.5 + UP * 0.3)
        d1 = mono("done", 26, GREEN).next_to(good, DOWN, buff=0.3); d2 = mono("done", 26, GREEN).next_to(bad, DOWN, buff=0.3)
        t.at("Both of these"); t.play(FadeIn(good), FadeIn(bad), run_time=0.6)
        t.at("finished"); t.play(FadeIn(d1), FadeIn(d2), run_time=0.4)
        ok = label("blur matched", 26, WHITE).next_to(d1, DOWN, buff=0.25); no = label("kernel too narrow: rings", 26, ACC).next_to(d2, DOWN, buff=0.25)
        t.at("Only one"); t.play(FadeIn(ok), FadeIn(no), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        hdr = ["candidate (y, x)", "flux [DN]", "error [DN]", "converged", "uncertainty_valid"]
        stopped = [r_ for r_ in rows if r_["run"].startswith("solver stopped")]
        data = [[f"({r_['y']}, {r_['x']})", f"{r_['flux']:.0f}", "nan" if r_["error"] != r_["error"] else f"{r_['error']:.0f}",
                 str(r_["converged"]), str(r_["uncertainty_valid"])] for r_ in stopped]
        tab = Table(data, col_labels=[label(h, 22) for h in hdr], include_outer_lines=True,
                    element_to_mobject=lambda s: label(s, 26)).scale(0.7).shift(UP * 0.5)
        t.at("did the measurements"); t.play(FadeIn(tab), run_time=0.6)
        hl_c = VGroup(*[SurroundingRectangle(tab.get_entries((i, 4)), color=RED, buff=0.12) for i in (2, 3)])
        hl_u = VGroup(*[SurroundingRectangle(tab.get_entries((i, c)), color=RED, buff=0.12) for i in (2, 3) for c in (3, 5)])
        t.at("whether they did"); t.play(Create(hl_c), run_time=0.4)
        t.at("error bars"); t.play(Create(hl_u), run_time=0.4)
        cap = label("A fit stopped early: the flux looks fine, the error bar is nan", 26, ACC).to_edge(DOWN, buff=0.7)
        t.at("A number without"); t.play(FadeIn(cap), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        items = VGroup(label("1.  Where did it run?", 40), label("2.  Does it look right?", 40), label("3.  Did it converge?", 40)).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        card = RoundedRectangle(corner_radius=0.2, width=items.width + 1, height=items.height + 1, color=ACC).add(items.move_to(ORIGIN))
        t.play(FadeIn(card), run_time=0.5)
        prompt = Text('"Run it, and show me where it ran,\nthe difference image, and the fit status."', font=FONT, font_size=30, line_spacing=1.2)
        frame = RoundedRectangle(corner_radius=0.15, width=prompt.width + 0.8, height=prompt.height + 0.7, color=BLUE_B).shift(DOWN * 0.5)
        prompt.move_to(frame)
        tag = label("what you ask your agent", 24, BLUE_B).next_to(frame, UP, buff=0.2)
        t.at("make them part"); t.play(card.animate.scale(0.5).to_edge(UP, buff=0.5), run_time=0.8)
        t.play(FadeIn(tag), FadeIn(frame), run_time=0.4)
        t.at("run it"); t.play(FadeIn(prompt), run_time=0.5)
        t.rest()
