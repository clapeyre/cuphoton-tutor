"""Shared helpers for the course videos (Manim CE)."""
import json
import os
from pathlib import Path

import numpy as np
from manim import *  # noqa
from matplotlib import colormaps

MEDIA = Path(__file__).resolve().parents[1]
RENDERS = Path(os.environ.get("MEDIA_RENDERS", MEDIA / "renders"))  # timings.json per video (narrate.py)
DATA = Path(os.environ.get("VIDEO_DATA", RENDERS / "data"))  # where data_*.py wrote its .npz (pipeline/data.sh)

BG = "#14161a"
config.background_color = BG
FONT = "Liberation Sans"


def timings(vid):
    return json.loads((RENDERS / vid / "timings.json").read_text())


def to_image(arr, cmap="magma", lo=None, hi=None, height=6.0, nan_color=(0, 0, 0)):
    """2-D array (origin lower, as imshow) -> ImageMobject of the given scene height."""
    a = np.asarray(arr, float)
    lo = np.nanpercentile(a, 1) if lo is None else lo
    hi = np.nanpercentile(a, 99.5) if hi is None else hi
    rgba = colormaps[cmap](np.clip((a - lo) / (hi - lo), 0, 1))
    rgb = (rgba[..., :3] * 255).astype(np.uint8)
    rgb[~np.isfinite(a)] = [int(c * 255) for c in nan_color]
    m = ImageMobject(rgb[::-1])  # ImageMobject row 0 is the top
    m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    m.height = height
    return m


def pix(img, shape, y, x):
    """Scene coordinates of pixel (y, x) in an ImageMobject built from an array of `shape`."""
    h, w = shape
    return img.get_center() + RIGHT * ((x + 0.5) / w - 0.5) * img.width + UP * ((y + 0.5) / h - 0.5) * img.height


def label(text, size=28, color=WHITE, **kw):
    return Text(text, font=FONT, font_size=size, color=color, **kw)


class Timed:
    """Tracks how much of a segment's duration the animations have used; `rest()` waits out the remainder."""

    def __init__(self, scene, seconds, words=None):
        self.scene, self.total = scene, seconds
        self.t0 = scene.renderer.time  # real rendered time; Manim truncates waits to whole frames
        self.words = words or []
        self._from = 0  # search position, so repeated phrases resolve in order

    @classmethod
    def seg(cls, scene, T, sid):
        """Timed for segment `sid` of timings.json, with its word timestamps."""
        return cls(scene, T[sid]["duration"], T[sid].get("words"))

    def when(self, phrase):
        """Start time (s) of the next occurrence of `phrase` in the narration."""
        norm = lambda x: "".join(ch for ch in x.lower() if ch.isalnum())
        target = [norm(w) for w in phrase.split() if norm(w)]
        ws = [(norm(w["w"]), w["start"]) for w in self.words if norm(w["w"])]  # skip punctuation tokens
        keys = [k for k, _ in ws]
        for i in range(self._from, len(keys) - len(target) + 1):
            if keys[i:i + len(target)] == target:
                self._from = i + 1
                return ws[i][1]
        raise KeyError(f"phrase not in narration: {phrase!r}")

    def at(self, phrase, lead=0.15):
        """Wait until the voice starts saying `phrase` (minus a small lead), so a
        visual appears as it is named, not after the sentence."""
        t = self.when(phrase) - lead
        if t > self.used + 1 / 30:
            self.wait(t - self.used)
        elif t < self.used - 0.25:
            print(f"WARNING: cue {phrase!r} at {t:.2f}s, but animations already used {self.used:.2f}s")

    @property
    def used(self):
        return self.scene.renderer.time - self.t0

    def play(self, *anims, run_time=1.0, **kw):
        self.scene.play(*anims, run_time=run_time, **kw)

    def wait(self, t):
        # Manim truncates a wait to whole frames; add half a frame so it rounds instead
        self.scene.wait(t + 0.5 / config.frame_rate)

    def rest(self):
        left = self.total - self.used
        if left > 0.5 / config.frame_rate:
            self.wait(left)
        elif left < -0.05:
            print(f"WARNING: segment over budget by {-left:.2f}s")
