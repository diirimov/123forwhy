"""V2 master edit: story chapters, transitions, grade."""
import skia
from gfx import W, H, paint, smoothstep, ease_io
import timing as T
import v2_home
import v2_rise
import v2_fame

DB = T.db
CHAPTERS = [(0.0, v2_home), (v2_rise.START, v2_rise), (v2_fame.START, v2_fame)]
# (start, end, gain): -12 dB hush while Joe stands in the doorway; full band returns on his clap (DB1)
AUDIO_DIPS = [(v2_home.A_DOOR + 0.25, v2_home.B_CLAP - 0.12, 0.25),
              (v2_fame.H_MIRROR + 0.05, v2_fame.H_GOLD - 0.12, 0.5)]   # -6 dB: the quiet mirror moment


def _chapter(t):
    ch = CHAPTERS[0][1]
    for t0, m in CHAPTERS:
        if t >= t0:
            ch = m
    return ch


def draw(c, t, surf=None):
    _chapter(t).draw(c, t)


def grade(t):
    if v2_fame.H_MIRROR <= t < v2_fame.H_GOLD:
        return dict(vignette=0.75, grain=0.1, warm=(0.9, 0.92, 1.0), warm_a=0.10)
    if t < v2_home.END:
        return dict(vignette=0.72, grain=0.09, warm=(1.0, 0.88, 0.74), warm_a=0.10)
    return dict(vignette=0.55, grain=0.07, warm=(1.0, 0.92, 0.82), warm_a=0.07)
