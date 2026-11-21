"""V3 shared: legible documentary captions (scrim), V2-shot remapping, generic cast helper."""
import math
import skia
from gfx import W, H, paint, shader_paint, lin_grad, rad_grad, smoothstep, ease_out, font, alpha
import timing as T
import v2_common
from world import CHARS
from character import DESIGNS
import choreo

IVORY = (0.99, 0.96, 0.89)


def cap(c, t, t0, t1, lines, y=300, size=78, accent=None):
    """bold tracked serif caps on a soft dark scrim; eased fade/rise; max 2 lines; auto-fit to 920 px"""
    if not (t0 - 0.01 <= t <= t1 + 0.01):
        return
    lines = [s.replace('\u2026', '...') for s in lines]     # the bold face has no ellipsis glyph
    a_in = smoothstep(t0, t0 + 0.38, t)
    a_out = 1 - smoothstep(t1 - 0.32, t1, t)
    a = min(a_in, a_out)
    if a <= 0:
        return
    rise = (1 - ease_out(a_in, 3)) * 22
    f = font('garamond_b', size)
    track = size * 0.07
    def width(s):
        return sum(f.measureText(ch) for ch in s) + track * (len(s) - 1)
    maxw = max(width(s) for s in lines)
    sc = min(1.0, 920 / maxw)
    lh = size * 1.16 * sc
    block_h = lh * len(lines)
    # scrim: soft dark band behind the text so it never melts into the picture
    top = y - size * 0.95 * sc + rise
    c.drawRoundRect(skia.Rect.MakeLTRB(W / 2 - maxw * sc / 2 - 70, top - 30, W / 2 + maxw * sc / 2 + 70, top + block_h + 46),
                    60, 60, paint((0.02, 0.01, 0.02, 0.5 * a), blur=34))
    for i, s in enumerate(lines):
        yy = y + i * lh + rise
        c.save()
        c.translate(W / 2, yy)
        c.scale(sc, sc)
        x = -width(s) / 2
        col = IVORY if not (accent and i == accent[0]) else accent[1]
        for ch in s:
            cw = f.measureText(ch)
            c.drawString(ch, x + 2, 4, f, paint((0.0, 0.0, 0.0, 0.8 * a), blur=6))
            c.drawString(ch, x, 0, f, paint((0.03, 0.01, 0.0, 0.7 * a), style='stroke', width=4.0))
            c.drawString(ch, x, 0, f, paint((*col[:3], a)))
            x += cw + track
        c.restore()


def remap(fn, src_t0, dst_t0):
    """reuse a V2 shot at a new place in the edit; lip-sync / VU meters follow the real music"""
    off = dst_t0 - src_t0
    def g(c, t):
        v2_common.CAPTIONS_OFF = True
        T.ENV_OFFSET = off
        try:
            fn(c, t - off)
        finally:
            T.ENV_OFFSET = 0.0
            v2_common.CAPTIONS_OFF = False
    return g


def pose(key, sched, t, **kw):
    return choreo.perform(sched, t, key, seed=DESIGNS[key].seed, **kw)


def draw_char(c, key, x, gy, h, P, outfit, L, t, shadow=True):
    return CHARS[key].draw(c, x, gy, h, P, outfit, L, t, shadow=shadow)


def place_head(key, P, h, head_xy):
    """return the (gx, gy) that puts this character's head centre at head_xy"""
    S0 = CHARS[key].skeleton(0, 0, h, P)
    return head_xy[0] - S0['head'][0], head_xy[1] - S0['head'][1]
