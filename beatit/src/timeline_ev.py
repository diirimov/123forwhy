"""THE EVOLUTION OF A KING - 60.000 s edit on the Beat It master. Acts are modules; each owns its shots and captions."""
import _paths  # noqa: F401
import importlib
import skia
from gfx import W, H, paint, smoothstep
import timing as T

ACTS = []
for name, t0 in (('ev_a1', 0.0), ('ev_a2', T.db(10)), ('ev_a3', T.db(19)), ('ev_a4', T.db(27))):
    try:
        ACTS.append((t0, importlib.import_module(name)))
    except ModuleNotFoundError as e:
        if e.name != name:
            raise

FADE_OUT = (59.32, 60.0)
AUDIO_GAIN_DB = -3.5           # the master peaks at +2.2 dBTP; level trim only so the AAC encode cannot clip
AUDIO_FADE = (59.0, 1.0)


def draw(c, t, surf=None):
    act = ACTS[0][1]
    for t0, m in ACTS:
        if t >= t0:
            act = m
    act.draw_act(c, t)
    for _, m in ACTS:
        m.captions(c, t)
    k = smoothstep(*FADE_OUT, t)
    if k > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, k)))


def grade(t):
    return dict(vignette=0.5, grain=0.05, warm=(1.0, 0.96, 0.9), warm_a=0.04)
