"""Core helpers: canvas, paints, easing, noise, timing from the beat map."""
import json, math, os
import numpy as np
import skia

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 60
NFRAMES = 3600

BM = json.load(open(os.path.join(ROOT, 'data/beatmap.json')))
BPM = BM['bpm']
PERIOD = 60.0 / BPM
OFF = BM['beat_offset']
SWING = BM['swing_16th_s']
FIDDLE = json.load(open(os.path.join(ROOT, 'data/fiddle_notes.json')))


def beat(t):
    return (t - OFF) / PERIOD


def bar_t(bar, step=0.0):
    """time of bar (1-based) + 16th step"""
    a = (bar - 1) * 16 + step
    tt = OFF + a * PERIOD / 4
    if abs(a - round(a)) < 1e-9 and int(round(a)) % 2 == 1:
        tt += SWING
    return tt


# ------------------------------------------------------------------ math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def smoother(t):
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


def ease_out(t, p=3):
    t = clamp(t)
    return 1 - (1 - t) ** p


def ease_in(t, p=3):
    t = clamp(t)
    return t ** p


def ease_out_back(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_elastic(t):
    t = clamp(t)
    if t in (0, 1):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1


def ramp(t, a, b):
    return clamp((t - a) / (b - a)) if b != a else float(t >= a)


def pulse(t, t0, attack=0.02, decay=0.25):
    """envelope that hits 1 at t0 (fast attack) and decays"""
    if t < t0 - attack:
        return 0.0
    if t < t0:
        return smooth((t - (t0 - attack)) / attack)
    return math.exp(-(t - t0) / decay)


def _hash(i, seed=0):
    x = (int(i) * 374761393 + seed * 668265263) & 0xFFFFFFFF
    x = (x ^ (x >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((x ^ (x >> 16)) & 0xFFFFFF) / float(0xFFFFFF)


def noise1(x, seed=0):
    i = math.floor(x)
    f = x - i
    a, b = _hash(i, seed), _hash(i + 1, seed)
    return lerp(a, b, smooth(f)) * 2 - 1


def fbm(x, seed=0, oct=3):
    v, a, s = 0.0, 0.5, 1.0
    for o in range(oct):
        v += a * noise1(x * s, seed + o * 17)
        a *= 0.5
        s *= 2.0
    return v


def rnd(seed):
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ color / paint
def hexc(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(clamp(a) * 255))


def mixc(h1, h2, t, a=1.0):
    h1, h2 = h1.lstrip('#'), h2.lstrip('#')
    c1 = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
    c2 = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    c = [int(lerp(x, y, clamp(t))) for x, y in zip(c1, c2)]
    return skia.Color(c[0], c[1], c[2], int(clamp(a) * 255))


def tohex(h1, h2, t):
    h1, h2 = h1.lstrip('#'), h2.lstrip('#')
    c1 = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
    c2 = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(lerp(x, y, clamp(t))) for x, y in zip(c1, c2))


INK = '#1b1310'
BONE = '#efe4c8'
BONE_SH = '#c9b893'
BONE_DK = '#9c8a68'
GOLD = '#d9a93b'
GOLD_DK = '#8f6a1c'
BURG = '#7a1f2b'
MIDNIGHT = '#141b36'

_paint_cache = {}


def fill(color, alpha=1.0, blur=0.0):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kFill_Style)
    p.setColor(hexc(color, alpha) if isinstance(color, str) else color)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def stroke(color, width, alpha=1.0, cap=skia.Paint.kRound_Cap, blur=0.0):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width)
    p.setColor(hexc(color, alpha) if isinstance(color, str) else color)
    p.setStrokeCap(cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def boil(p, frame, dev=0.9, seg=7.0):
    """hand-drawn line boil: outline jitter that changes 15 times per second"""
    p.setPathEffect(skia.DiscretePathEffect.Make(seg, dev, int(frame // 4) * 7 + 3))
    return p


def lin_grad(p0, p1, colors, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)],
                                               [hexc(c) if isinstance(c, str) else c for c in colors], pos))
    return p


def rad_grad(c, r, colors, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(*c), r,
                                               [hexc(c_) if isinstance(c_, str) else c_ for c_ in colors], pos))
    return p


# ------------------------------------------------------------------ paths
def P():
    return skia.Path()


def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth_poly(pts, close=True, k=0.5):
    """Catmull-Rom through points -> cubic path"""
    p = skia.Path()
    n = len(pts)
    if n < 3:
        return poly(pts, close)
    pts = [tuple(q) for q in pts]
    p.moveTo(*pts[0])
    rng_ = range(n) if close else range(n - 1)
    for i in rng_:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
        p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if close:
        p.close()
    return p


def ellipse(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def capsule(a, b, r1, r2=None):
    """tapered capsule from a to b"""
    r2 = r1 if r2 is None else r2
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) + 1e-6
    nx, ny = -dy / L, dx / L
    ang = math.degrees(math.atan2(dy, dx))
    p = skia.Path()
    p.moveTo(ax + nx * r1, ay + ny * r1)
    p.lineTo(bx + nx * r2, by + ny * r2)
    p.arcTo(skia.Rect.MakeLTRB(bx - r2, by - r2, bx + r2, by + r2), ang + 90, -180, False)
    p.lineTo(ax - nx * r1, ay - ny * r1)
    p.arcTo(skia.Rect.MakeLTRB(ax - r1, ay - r1, ax + r1, ay + r1), ang - 90, -180, False)
    p.close()
    return p


def rot(pt, ang, c=(0, 0)):
    x, y = pt[0] - c[0], pt[1] - c[1]
    ca, sa = math.cos(ang), math.sin(ang)
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


def add(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mid(a, b, t=0.5):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def ang(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])


def ink_fill(c, path, color, frame, ow=4.0, alpha=1.0, boil_on=True):
    """outlined fill (outline drawn under-and-over for crisp toon look)"""
    c.drawPath(path, fill(color, alpha))
    sp = stroke(INK, ow, alpha)
    if boil_on:
        boil(sp, frame, 0.6, 9.0)
    c.drawPath(path, sp)


class Save:
    def __init__(self, c):
        self.c = c

    def __enter__(self):
        self.c.save()
        return self.c

    def __exit__(self, *a):
        self.c.restore()


# ------------------------------------------------------------------ fonts
FONTS = {}


def font(name, size):
    if name not in FONTS:
        FONTS[name] = skia.Typeface.MakeFromFile(os.path.join(ROOT, 'assets/fonts', name))
    f = skia.Font(FONTS[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f
