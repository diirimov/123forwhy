"""V3 master edit: chapters, audio dips, grade."""
import timing as T
import v3_end
import v3_open
import v3_mid

CHAPTERS = [(0.0, v3_open), (v3_mid.START, v3_mid), (v3_end.START, v3_end)]
AUDIO_DIPS = [(v3_open.H_FEET + 0.1, v3_open.H_FLASH - 0.08, 0.25),     # -12 dB: the shadow, Joe's gesture
              (v3_end.T_SPEAK - 0.35, v3_end.T_EXIT - 0.1, 0.32)]    # -10 dB: the stadium holds its breath


def _chapter(t):
    ch = CHAPTERS[0][1]
    for t0, m in CHAPTERS:
        if t >= t0:
            ch = m
    return ch


def draw(c, t, surf=None):
    _chapter(t).draw(c, t)


def grade(t):
    if t >= v3_end.T_STADIUM and t < v3_end.T_SHOE:
        return dict(vignette=0.5, grain=0.06, warm=(0.95, 0.95, 1.0), warm_a=0.05)
    return dict(vignette=0.62, grain=0.08, warm=(1.0, 0.92, 0.82), warm_a=0.07)
