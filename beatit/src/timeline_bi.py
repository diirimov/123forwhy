"""Beat It episode edit: 0-60.000 s. Acts are modules; each owns its shots and captions."""
import _paths  # noqa: F401
import skia
from gfx import W, H, paint, smoothstep
import timing as T
import importlib

ACTS = []
for name, t0 in (('bi_act1', 0.0), ('bi_act2', T.db(10)), ('bi_act3', T.db(17)), ('bi_act4', T.db(24))):
    try:
        ACTS.append((t0, importlib.import_module(name)))
    except ModuleNotFoundError:
        pass

FADE_OUT = (59.32, 60.0)       # picture fade after the last downbeat (DB34 = 59.321)
AUDIO_GAIN_DB = -3.0           # source peaks at +2.2 dBTP; trim level only (no EQ/tempo/pitch change) so AAC can't clip
AUDIO_FADE = (59.0, 1.0)       # gentle tail fade so the edit ends on the last accent instead of a hard cut


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
    return dict(vignette=0.5, grain=0.06, warm=(1.0, 0.95, 0.88), warm_a=0.05)
