"""Core drawing helpers (skia) for the Christmas Legends animation."""
import math, os, random
import numpy as np
import skia

W, H = 1080, 1920
FPS = 60
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'fonts')

# ------------------------------------------------------------------ colour
def hexc(h, a=255):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(a))

def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)

def mix(c1, c2, t, a=255):
    a1 = rgb(c1) if isinstance(c1, str) else np.array(c1, float)
    a2 = rgb(c2) if isinstance(c2, str) else np.array(c2, float)
    c = a1 + (a2 - a1) * max(0.0, min(1.0, t))
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(a))

def shade(h, k, a=255):
    """k<0 darker, k>0 lighter"""
    return mix(h, '#000000' if k < 0 else '#ffffff', abs(k), a)

def col(c, a=255):
    if isinstance(c, str): return hexc(c, a)
    if isinstance(c, int): return skia.ColorSetA(c, int(a))
    return c

# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def smooth(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_in_out(t): t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def ease_out_back(t, s=1.70158):
    t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def ease_out_elastic(t):
    t = clamp(t)
    if t in (0, 1): return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1
def seg(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 != t0 else float(t >= t0)
def bump(t, t0, dur):
    """0->1->0 hump"""
    x = seg(t, t0, t0 + dur); return math.sin(math.pi * x)
def decay(t, t0, tau):
    if t < t0: return 0.0
    return math.exp(-(t - t0) / tau)
def spring(t, t0, freq=3.0, damp=5.0):
    """0 before t0, then damped overshoot settling to 1"""
    if t < t0: return 0.0
    x = t - t0
    return 1 - math.exp(-damp * x) * math.cos(2 * math.pi * freq * x)

# ------------------------------------------------------------------ paints
def P(color='#ffffff', a=255, stroke=None, cap=skia.Paint.kRound_Cap, join=skia.Paint.kRound_Join, blur=0, aa=True,
      blend=None):
    p = skia.Paint(AntiAlias=aa, Color=col(color, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(cap); p.setStrokeJoin(join)
    if blur > 0: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None: p.setBlendMode(blend)
    return p

def lin(p0, p1, colors, pos=None, a=255):
    cs = [col(c, a) if not isinstance(c, tuple) else col(c[0], c[1]) for c in colors]
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], cs, pos)

def rad(c, r, colors, pos=None, a=255):
    cs = [col(c_, a) if not isinstance(c_, tuple) else col(c_[0], c_[1]) for c_ in colors]
    return skia.GradientShader.MakeRadial(skia.Point(*c), max(r, 0.1), cs, pos)

def PS(shader, a=255, blur=0, blend=None):
    p = skia.Paint(AntiAlias=True, Shader=shader)
    if a < 255: p.setAlphaf(a / 255)
    if blur > 0: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None: p.setBlendMode(blend)
    return p

# ------------------------------------------------------------------ paths
def path_from(points, closed=True, smooth_k=0.0):
    """polyline or Catmull-Rom smooth path through points"""
    p = skia.Path()
    if not points: return p
    if smooth_k <= 0:
        p.moveTo(*points[0])
        for q in points[1:]: p.lineTo(*q)
        if closed: p.close()
        return p
    pts = list(points)
    n = len(pts)
    p.moveTo(*pts[0])
    rng_ = range(n if closed else n - 1)
    for i in rng_:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]; p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[(i + 1) % n]
        k = smooth_k / 3
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        p.cubicTo(*c1, *c2, *p2)
    if closed: p.close()
    return p

def blob(cx, cy, rx, ry, n=10, jitter=0.0, seed=0, rot=0.0):
    r = random.Random(seed)
    pts = []
    for i in range(n):
        a = rot + 2 * math.pi * i / n
        k = 1 + r.uniform(-jitter, jitter)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    return path_from(pts, True, 1.0)

def ellipse(cx, cy, rx, ry):
    p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)); return p

def rrect(x, y, w, h, r):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p

def fuzzy_edge(points, amp=10, freq=3, seed=0, closed=True):
    """turn a polygon into a furry outline (zig-zag fur tufts)"""
    r = random.Random(seed); out = []
    n = len(points)
    for i in range(n if closed else n - 1):
        a = points[i]; b = points[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1]); steps = max(1, int(L / (40 / freq)))
        nx, ny = (b[1] - a[1]) / (L + 1e-9), -(b[0] - a[0]) / (L + 1e-9)
        for s in range(steps):
            t = s / steps
            x = a[0] + (b[0] - a[0]) * t; y = a[1] + (b[1] - a[1]) * t
            k = amp * (r.uniform(0.4, 1.0) if s % 2 else -0.2)
            out.append((x + nx * k, y + ny * k))
    return out

# ------------------------------------------------------------------ drawing
def fill_outline(c, path, fill, outline='#1d1430', ow=5, a=255, shader=None):
    if ow > 0:
        c.drawPath(path, P(outline, a, stroke=ow * 2))
    if shader is not None:
        c.drawPath(path, PS(shader, a))
    else:
        c.drawPath(path, P(fill, a))

def shaded(c, path, base, light=(0.0, -1.0), k=0.22, outline='#1d1430', ow=5, a=255, rim=None, rim_w=6):
    """fill with a soft directional gradient + optional rim light"""
    b = path.computeTightBounds()
    cx, cy = b.centerX(), b.centerY(); r = max(b.width(), b.height()) / 2 + 1
    p0 = (cx + light[0] * r, cy + light[1] * r); p1 = (cx - light[0] * r, cy - light[1] * r)
    if ow > 0: c.drawPath(path, P(outline, a, stroke=ow * 2))
    c.drawPath(path, PS(lin(p0, p1, [shade(base, k), col(base), shade(base, -k)], [0, 0.45, 1]), a))
    if rim:
        c.save(); c.clipPath(path, doAntiAlias=True)
        rp = skia.Path(path); rp.offset(-rim_w * 1.2, rim_w * 1.0)
        c.drawPath(path, P(rim, int(a * 0.55), stroke=rim_w * 2, blur=2))
        c.restore()

def inner_shadow(c, path, dx=6, dy=8, color='#000000', a=70, blur=6):
    c.save(); c.clipPath(path, doAntiAlias=True)
    sp = skia.Path(); sp.addRect(path.computeTightBounds().makeOutset(200, 200)); sp2 = skia.Path(path); sp2.offset(dx, dy)
    hole = skia.Op(sp, sp2, skia.PathOp.kDifference_PathOp)
    if hole: c.drawPath(hole, P(color, a, blur=blur))
    c.restore()

def glow(c, x, y, r, color, a=200):
    c.drawCircle(x, y, r, PS(rad((x, y), r, [(color, a), (color, int(a * 0.35)), (color, 0)], [0, 0.35, 1])))

def limb(c, pts, w, color, outline='#1d1430', ow=4, a=255, highlight=None):
    p = skia.Path(); p.moveTo(*pts[0])
    if len(pts) == 3:
        # smooth bend through the joint
        p.quadTo(pts[1][0], pts[1][1], pts[2][0], pts[2][1]) if False else None
        p.lineTo(*pts[1]); p.lineTo(*pts[2])
    else:
        for q in pts[1:]: p.lineTo(*q)
    if ow > 0: c.drawPath(p, P(outline, a, stroke=w + ow * 2))
    c.drawPath(p, P(color, a, stroke=w))
    if highlight:
        p2 = skia.Path(p); p2.offset(-w * 0.18, -w * 0.12)
        c.drawPath(p2, P(highlight, int(a * 0.35), stroke=w * 0.28))

def two_bone(base, a1, l1, a2, l2):
    """angles in degrees, 0 = straight down, positive = counter-clockwise (towards +x)"""
    r1 = math.radians(a1); j = (base[0] + math.sin(r1) * l1, base[1] + math.cos(r1) * l1)
    r2 = math.radians(a1 + a2); e = (j[0] + math.sin(r2) * l2, j[1] + math.cos(r2) * l2)
    return [base, j, e]

# ------------------------------------------------------------------ text
_tf = {}
def typeface(name):
    if name not in _tf: _tf[name] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, name))
    return _tf[name]

def text_width(s, font):
    return font.measureText(s)

def draw_text(c, s, x, y, size, face='luckiest-guy-400.ttf', fill='#fff6e3', outline='#2a1530', ow=10, a=255,
              align='center', shadow=True, shader=None, tracking=0.0, glow_color=None):
    font = skia.Font(typeface(face), size)
    font.setEdging(skia.Font.Edging.kAntiAlias)
    wdt = font.measureText(s) + tracking * (len(s) - 1)
    x0 = x - wdt / 2 if align == 'center' else (x - wdt if align == 'right' else x)
    def blob_at():
        if tracking == 0:
            return skia.TextBlob.MakeFromString(s, font)
        b = skia.TextBlobBuilder(); xs = 0.0; pos = []
        glyphs = font.textToGlyphs(s); widths = font.getWidths(glyphs)
        for g, wd in zip(glyphs, widths): pos.append(skia.Point(xs, 0)); xs += wd + tracking
        b.allocRunPos(font, glyphs, pos); return b.make()
    tb = blob_at()
    if tb is None: return wdt
    if glow_color:
        c.drawTextBlob(tb, x0, y, P(glow_color, int(a * 0.55), blur=size * 0.25))
    if shadow:
        c.drawTextBlob(tb, x0 + size * 0.03, y + size * 0.07, P('#0b0614', int(a * 0.55), stroke=ow * 2, blur=size * 0.05))
    if ow > 0:
        c.drawTextBlob(tb, x0, y, P(outline, a, stroke=ow * 2))
    if shader is not None:
        p = PS(shader, a); c.drawTextBlob(tb, x0, y, p)
    else:
        c.drawTextBlob(tb, x0, y, P(fill, a))
    return wdt

# ------------------------------------------------------------------ textures (cached)
_cache = {}
def noise_image(w=1080, h=1920, seed=3, scale=1.0):
    key = ('noise', w, h, seed)
    if key in _cache: return _cache[key]
    r = np.random.default_rng(seed)
    # paper grain: sum of a few octaves
    img = np.zeros((h, w), np.float32)
    for k, amp in ((1, 0.5), (3, 0.3), (9, 0.2)):
        small = r.standard_normal((h // k + 2, w // k + 2)).astype(np.float32)
        up = np.kron(small, np.ones((k, k), np.float32))[:h, :w]
        img += up * amp
    img = (img - img.min()) / (img.max() - img.min())
    a = (img * 255).astype(np.uint8)
    rgba = np.dstack([a, a, a, np.full_like(a, 255)])
    im = skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)
    _cache[key] = im
    return im

def grain_overlay(c, t, amount=0.07):
    im = noise_image()
    p = skia.Paint(); p.setAlphaf(amount); p.setBlendMode(skia.BlendMode.kOverlay)
    ox = (int(t * 60) * 37) % 200; oy = (int(t * 60) * 53) % 200
    c.save(); c.translate(-ox, -oy); c.scale(1.2, 1.2)
    c.drawImage(im, 0, 0, skia.SamplingOptions(), p); c.restore()

def vignette(c, strength=0.55, color='#0a0518'):
    c.drawRect(skia.Rect.MakeWH(W, H), PS(rad((W / 2, H * 0.46), H * 0.75,
                                             [(color, 0), (color, 0), (color, int(255 * strength))], [0, 0.55, 1])))

def picture(fn, w=W, h=H):
    rec = skia.PictureRecorder(); cc = rec.beginRecording(skia.Rect.MakeWH(w, h)); fn(cc)
    return rec.finishRecordingAsPicture()

def raster(fn, w, h, scale=1.0):
    surf = skia.Surface(int(w * scale), int(h * scale)); cc = surf.getCanvas(); cc.scale(scale, scale); fn(cc)
    return surf.makeImageSnapshot()
