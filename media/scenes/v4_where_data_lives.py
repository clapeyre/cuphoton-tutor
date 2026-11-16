"""v4 - Where your data lives: host and device.  Real data: v4.json (data_v4.py, this machine's GPU)."""
from common import *
import json

VID = "v4-where-data-lives"
ACC = "#ffb000"
MONO = "Liberation Mono"
CPU_XREP_S = 8.82  # 3.4's real CPU run (tutor notes), same image and spec


def mono(text, size=22, color=WHITE):
    return Text(text, font=MONO, font_size=size, color=color)


def tile(color=GREY_B):
    t = VGroup(*[Square(0.16, stroke_width=0, fill_color=interpolate_color(ManimColor(GREY_D), ManimColor(GREY_A), ((i * 7 + j * 3) % 10) / 10), fill_opacity=1)
                 .move_to(RIGHT * 0.16 * j + DOWN * 0.16 * i) for i in range(4) for j in range(4)])
    return VGroup(t, SurroundingRectangle(t, color=color, buff=0.02, stroke_width=2))


class V4(Scene):
    def construct(self):
        T = timings(VID)
        d = json.loads((DATA / "v4.json").read_text())
        up, xr, down = d["up_s"] * 1000, d["xrep_s"] * 1000, d["down_s"] * 1000

        # ---------- s1: two memories
        self.next_section("s1"); t = Timed.seg(self, T, "s1")
        host = RoundedRectangle(corner_radius=0.2, width=4.6, height=3.6, color=BLUE_B).shift(LEFT * 3.9)
        dev = RoundedRectangle(corner_radius=0.2, width=4.6, height=3.6, color=GREEN_B).shift(RIGHT * 3.9)
        hl = VGroup(label("host", 36, BLUE_B), label("the computer's memory", 24, GREY_B)).arrange(DOWN, buff=0.1).next_to(host, UP, buff=0.2)
        dl = VGroup(label("device", 36, GREEN_B), label("the GPU's memory", 24, GREY_B)).arrange(DOWN, buff=0.1).next_to(dev, UP, buff=0.2)
        bridge = VGroup(Line(host.get_right() + UP * 0.25, dev.get_left() + UP * 0.25, color=GREY_B), Line(host.get_right() + DOWN * 0.25, dev.get_left() + DOWN * 0.25, color=GREY_B))
        bl = label("copy", 26, GREY_B).next_to(bridge, DOWN, buff=0.35)
        img = tile().move_to(host)
        t.at("The computer's own"); t.play(Create(host), FadeIn(hl[0]), FadeIn(hl[1]), FadeIn(img), run_time=0.7)
        t.at("the GPU's"); t.play(Create(dev), FadeIn(dl), run_time=0.6)
        t.at("A narrow bridge"); t.play(Create(bridge), FadeIn(bl), run_time=0.6)
        t.at("has to cross it"); t.play(img.animate.move_to(dev), run_time=1.0)
        t.at("cross back"); t.play(img.animate.move_to(host), run_time=1.0)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s2: what the bridge costs
        self.next_section("s2"); t = Timed.seg(self, T, "s2")
        head = label(f"one real image: {d['N']} × {d['N']} pixels, {d['mbytes']:.0f} MB", 30).to_edge(UP, buff=0.6)
        t.at("Here is one"); t.play(FadeIn(head), run_time=0.5)
        scale = 0.32  # scene units per millisecond
        y = 0.8
        def bar(ms_, color, x0):
            return Rectangle(width=max(ms_ * scale, 0.04), height=0.6, stroke_width=0, fill_color=color, fill_opacity=1).move_to([x0, y, 0], aligned_edge=LEFT)
        x0 = -5.5
        b_up = bar(up, BLUE_B, x0); b_x = bar(xr, GREEN_B, b_up.get_right()[0]); b_dn = bar(down, BLUE_B, b_x.get_right()[0])
        l_up = VGroup(label("copy up", 22, BLUE_B), mono(f"{up:.1f} ms", 22)).arrange(DOWN, buff=0.08).next_to(b_up, DOWN, buff=0.2)
        l_x = VGroup(label("xRep on the GPU", 22, GREEN_B), mono(f"{xr:.1f} ms", 22)).arrange(DOWN, buff=0.08).next_to(b_x, DOWN, buff=0.2)
        l_dn = VGroup(label("copy back", 22, BLUE_B), mono(f"{down:.1f} ms", 22)).arrange(DOWN, buff=0.08).next_to(b_dn, DOWN, buff=0.2).shift(RIGHT * 0.5)
        t.at("Copying it up"); t.play(GrowFromEdge(b_up, LEFT), FadeIn(l_up), run_time=0.5)
        t.at("x rep then"); t.play(GrowFromEdge(b_x, LEFT), FadeIn(l_x), run_time=0.8)
        t.at("Copying the result back"); t.play(GrowFromEdge(b_dn, LEFT), FadeIn(l_dn), run_time=0.5)
        cpu = VGroup(label("the same xRep on the CPU:", 26, GREY_B), mono(f"{CPU_XREP_S:.1f} s", 26, GREY_B),
                     label(f"(a bar {CPU_XREP_S * 1000 / (up + xr + down):.0f} times longer)", 22, GREY_C)).arrange(RIGHT, buff=0.25).shift(DOWN * 1.9)
        t.at("Against the CPU's"); t.play(FadeIn(cpu), run_time=0.6)
        notnothing = label(f"copies: {up + down:.1f} ms against {xr:.1f} ms of GPU work", 28, ACC).shift(DOWN * 2.9)
        t.at("Against the GPU's own work"); t.play(FadeIn(notnothing), run_time=0.6)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s3: once, or at every stage
        self.next_section("s3"); t = Timed.seg(self, T, "s3")
        rt = up + down
        scale = 0.16  # s3 draws four stages: half the s2 scale, each stage drawn as half an xRep (schematic)
        def chain(yc, every):
            g = VGroup()
            x = -6.2
            for k in range(4):
                if every or k == 0:
                    c = Rectangle(width=rt / 2 * scale, height=0.5, stroke_width=0, fill_color=BLUE_B, fill_opacity=1).move_to([x, yc, 0], aligned_edge=LEFT); g.add(c); x = c.get_right()[0]
                s_ = Rectangle(width=xr * scale * 0.5, height=0.5, stroke_width=0, fill_color=GREEN_B, fill_opacity=1).move_to([x, yc, 0], aligned_edge=LEFT); g.add(s_); x = s_.get_right()[0]
                if every or k == 3:
                    c = Rectangle(width=rt / 2 * scale, height=0.5, stroke_width=0, fill_color=BLUE_B, fill_opacity=1).move_to([x, yc, 0], aligned_edge=LEFT); g.add(c); x = c.get_right()[0]
            return g
        top, bot = chain(1.2, True), chain(-1.4, False)
        lt = label(f"crossing at every stage: {4 * rt:.0f} ms of copies", 26).next_to(top, UP, buff=0.25).align_to(top, LEFT)
        lb = label(f"crossing once: {rt:.0f} ms of copies", 26, ACC).next_to(bot, UP, buff=0.25).align_to(bot, LEFT)
        key = VGroup(Square(0.25, fill_color=BLUE_B, fill_opacity=1, stroke_width=0), label("copy", 22), Square(0.25, fill_color=GREEN_B, fill_opacity=1, stroke_width=0), label("a stage on the GPU", 22)).arrange(RIGHT, buff=0.2).to_edge(DOWN, buff=0.5)
        t.at("how often the data crosses"); t.play(FadeIn(key), run_time=0.4)
        t.at("If every stage"); t.play(LaggedStart(*[GrowFromEdge(r, LEFT) for r in top], lag_ratio=0.5), FadeIn(lt), run_time=2.2)
        t.at("If the data stays"); t.play(LaggedStart(*[GrowFromEdge(r, LEFT) for r in bot], lag_ratio=0.5), FadeIn(lb), run_time=1.8)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s4: where each result lands
        self.next_section("s4"); t = Timed.seg(self, T, "s4")
        host = RoundedRectangle(corner_radius=0.2, width=3.6, height=2.2, color=BLUE_B).shift(LEFT * 4 + DOWN * 1.2)
        dev = RoundedRectangle(corner_radius=0.2, width=3.6, height=2.2, color=GREEN_B).shift(RIGHT * 4 + DOWN * 1.2)
        hl = label("host", 30, BLUE_B).move_to(host); dl = label("device", 30, GREEN_B).move_to(dev)
        call = VGroup(RoundedRectangle(corner_radius=0.15, width=3.2, height=1.0, color=WHITE), mono("a cuPhoton call", 24)).shift(UP * 1.8)
        call[1].move_to(call[0])
        a1 = DashedLine(call.get_bottom(), host.get_top(), color=GREY_B); a2 = DashedLine(call.get_bottom(), dev.get_top(), color=GREY_B)
        q = label("?", 72, ACC).move_to(DOWN * 0.6)
        t.at("Every cuPhoton call"); t.play(FadeIn(call), Create(host), Create(dev), FadeIn(hl), FadeIn(dl), run_time=0.7)
        t.at("where its result lands"); t.play(Create(a1), Create(a2), FadeIn(q), run_time=0.6)
        code = mono("result = stage(data, backend=\"cupy\")", 22, GREY_C).to_edge(UP, buff=0.3)
        t.at("Your agent writes"); t.play(FadeIn(code), run_time=0.5)
        t.rest()
        self.remove(*self.mobjects)

        # ---------- s5: ask
        self.next_section("s5"); t = Timed.seg(self, T, "s5")
        prompt = label("\"Where does each result live?\"", 40, ACC)
        frame = SurroundingRectangle(prompt, color=ACC, buff=0.4, corner_radius=0.15)
        t.play(FadeIn(frame), FadeIn(prompt), run_time=0.6)
        t.rest()
