"""Skia drawing toolkit: colours, smooth paths, cel-shaded fills, glows, gradients, text, grain."""
import math
import numpy as np
import skia

W, H = 1080, 1920


# ----------------------------------------------------------------------------- colour
def hexc(h, a=1.0):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def C(c):
    """tuple(r,g,b,a 0..1) or hex -> skia Color4f"""
    if isinstance(c, str):
        c = hexc(c)
    if len(c) == 3:
        c = (*c, 1.0)
    return skia.Color4f(*[float(min(1, max(0, v))) for v in c])


def mix(a, b, t):
    a = hexc(a) if isinstance(a, str) else a
    b = hexc(b) if isinstance(b, str) else b
    a = a if len(a) == 4 else (*a, 1)
    b = b if len(b) == 4 else (*b, 1)
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def shade(c, k):
    """k<0 darker (towards a cool deep tone), k>0 lighter (towards warm white)"""
    c = hexc(c) if isinstance(c, str) else c
    if k < 0:
        tgt = (0.10, 0.05, 0.12, c[3] if len(c) == 4 else 1)
        return mix(c, tgt, -k)
    return mix(c, (1.0, 0.97, 0.9, c[3] if len(c) == 4 else 1), k)


def tint(c, light, amt):
    """multiply-ish tint by scene light colour"""
    c = hexc(c) if isinstance(c, str) else c
    l = hexc(light) if isinstance(light, str) else light
    m = (c[0] * l[0], c[1] * l[1], c[2] * l[2], c[3] if len(c) == 4 else 1)
    return mix(c, m, amt)


def alpha(c, a):
    c = hexc(c) if isinstance(c, str) else c
    return (c[0], c[1], c[2], (c[3] if len(c) == 4 else 1) * a)


# ----------------------------------------------------------------------------- paint
def paint(c, aa=True, style='fill', width=1.0, blur=0.0, blend=None, cap='round'):
    p = skia.Paint(AntiAlias=aa, Color4f=C(c))
    if style == 'stroke':
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == 'round' else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend:
        p.setBlendMode(blend)
    return p


def lin_grad(p0, p1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)],
                                          [C(c).toColor() for c in cols], pos)


def rad_grad(c, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), max(r, 0.1), [C(c_).toColor() for c_ in cols], pos)


def shader_paint(shader, blend=None, a=1.0):
    p = skia.Paint(AntiAlias=True, Shader=shader)
    if a < 1:
        p.setAlphaf(a)
    if blend:
        p.setBlendMode(blend)
    return p


# ----------------------------------------------------------------------------- geometry
def smooth_path(pts, closed=True, tension=0.5):
    """Catmull-Rom through points -> cubic Bezier skia.Path"""
    pts = [tuple(map(float, p)) for p in pts]
    n = len(pts)
    path = skia.Path()
    if n < 2:
        return path
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        path.cubicTo(*c1, *c2, *p2)
    if closed:
        path.close()
    return path


def poly_path(pts, closed=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if closed:
        path.close()
    return path


def ellipse_path(cx, cy, rx, ry, rot=0.0):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    if rot:
        p.transform(skia.Matrix.RotateDeg(math.degrees(rot), skia.Point(cx, cy)))
    return p


def limb_outline(pts, widths, cap_start=True, cap_end=True):
    """Tapered smooth shape along a polyline with per-point widths (full width)."""
    pts = np.asarray(pts, float)
    widths = np.asarray(widths, float)
    n = len(pts)
    normals = []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        d = b - a
        L = np.hypot(*d) + 1e-9
        normals.append(np.array([-d[1], d[0]]) / L)
    left = [pts[i] + normals[i] * widths[i] / 2 for i in range(n)]
    right = [pts[i] - normals[i] * widths[i] / 2 for i in range(n)]
    ring = list(left)
    if cap_end:
        d = pts[-1] - pts[-2]
        d = d / (np.hypot(*d) + 1e-9)
        ring.append(pts[-1] + d * widths[-1] * 0.45)
    ring += right[::-1]
    if cap_start:
        d = pts[0] - pts[1]
        d = d / (np.hypot(*d) + 1e-9)
        ring.append(pts[0] + d * widths[0] * 0.45)
    return smooth_path(ring, closed=True, tension=0.55)


# ----------------------------------------------------------------------------- shaded fills
def cel(canvas, path, base, light_dir=(-0.6, -0.8), shadow_k=-0.32, offset=None, rim=None,
        outline=None, ow=2.0, rim_w=3.0, hi=None):
    """Illustrated shading: shadow fill, lit shape offset toward light, rim light, coloured outline."""
    b = path.getBounds()
    size = max(b.width(), b.height())
    off = offset if offset is not None else size * 0.12
    lx, ly = light_dir
    canvas.save()
    canvas.clipPath(path, doAntiAlias=True)
    canvas.drawPath(path, paint(shade(base, shadow_k)))
    lit = skia.Path(path)
    lit.offset(lx * off, ly * off)
    canvas.drawPath(lit, paint(base, blur=max(0.6, size * 0.012)))
    if hi is not None:
        h2 = skia.Path(path)
        h2.offset(lx * off * 2.2, ly * off * 2.2)
        canvas.drawPath(h2, paint(alpha(shade(base, 0.25), hi), blur=size * 0.06))
    if rim is not None:
        r = skia.Path(path)
        r.offset(-lx * rim_w * 1.2, -ly * rim_w * 1.2)
        inv = skia.Path(path)
        inv.setFillType(skia.PathFillType.kInverseWinding)
        inv.offset(-lx * rim_w * 1.2, -ly * rim_w * 1.2)
        canvas.drawPath(inv, paint(rim, blur=rim_w * 0.5))
    canvas.restore()
    if outline is not None:
        canvas.drawPath(path, paint(outline, style='stroke', width=ow))


def glow(canvas, x, y, r, c, a=1.0, blend=skia.BlendMode.kPlus):
    canvas.drawCircle(x, y, r, shader_paint(rad_grad((x, y), r, [alpha(c, a), alpha(c, a * 0.35), alpha(c, 0)],
                                                     [0, 0.35, 1]), blend=blend))


def beam(canvas, x0, y0, x1, y1, w0, w1, c, a=0.5, blur=20):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-9
    nx, ny = -dy / L, dx / L
    p = poly_path([(x0 + nx * w0, y0 + ny * w0), (x1 + nx * w1, y1 + ny * w1),
                   (x1 - nx * w1, y1 - ny * w1), (x0 - nx * w0, y0 - ny * w0)])
    pt = shader_paint(lin_grad((x0, y0), (x1, y1), [alpha(c, a), alpha(c, a * 0.4), alpha(c, 0)], [0, 0.6, 1]),
                      blend=skia.BlendMode.kScreen)
    pt.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    canvas.drawPath(p, pt)


# ----------------------------------------------------------------------------- text
_FONTS = {}


def font(name, size):
    paths = {
        'spartan': '/usr/share/fonts/opentype/league-spartan/LeagueSpartan-Black.otf',
        'spartan_b': '/usr/share/fonts/opentype/league-spartan/LeagueSpartan-Bold.otf',
        'garamond_i': '/usr/share/fonts/opentype/ebgaramond/EBGaramond12-Italic.otf',
        'garamond': '/usr/share/fonts/opentype/ebgaramond/EBGaramond12-Regular.otf',
        'bebas': '/usr/share/fonts/opentype/bebas-neue/BebasNeue-Bold.otf',
    }
    if name not in _FONTS:
        _FONTS[name] = skia.Typeface.MakeFromFile(paths[name])
    return skia.Font(_FONTS[name], size)


def text_center(canvas, s, x, y, f, p, tracking=0.0):
    if tracking == 0:
        w = f.measureText(s)
        canvas.drawString(s, x - w / 2, y, f, p)
        return
    widths = [f.measureText(ch) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    cx = x - total / 2
    for ch, w_ in zip(s, widths):
        canvas.drawString(ch, cx, y, f, p)
        cx += w_ + tracking


# ----------------------------------------------------------------------------- easing / motion
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smoothstep(e0, e1, x):
    t = clamp((x - e0) / (e1 - e0 + 1e-12))
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t, p=3):
    t = clamp(t)
    return 1 - (1 - t) ** p


def ease_in(t, p=3):
    t = clamp(t)
    return t ** p


def back_out(t, s=1.6):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def lerp(a, b, t):
    return a + (b - a) * t


def noise1(x, seed=0):
    """cheap smooth value noise, range ~[-1,1]"""
    i = math.floor(x)
    f = x - i
    def h(n):
        n = (n * 374761393 + seed * 668265263) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1
    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


# ----------------------------------------------------------------------------- post
_GRAIN = None


def grain_layer(seed):
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(7)
        _GRAIN = []
        for k in range(6):
            g = rng.normal(0, 1, (H // 2, W // 2))
            a = (np.clip(g * 22 + 128, 0, 255)).astype(np.uint8)
            rgba = np.dstack([a, a, a, np.full_like(a, 255)])
            _GRAIN.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))
    return _GRAIN[seed % len(_GRAIN)]


def post(canvas, frame, vignette=0.55, grain=0.07, warm=(1.0, 0.93, 0.82), warm_a=0.06):
    # film grain (overlay), vignette, gentle warm wash
    img = grain_layer(frame)
    p = skia.Paint(AntiAlias=False)
    p.setBlendMode(skia.BlendMode.kOverlay)
    p.setAlphaf(grain)
    canvas.drawImageRect(img, skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.FilterMode.kLinear), p)
    canvas.drawRect(skia.Rect.MakeWH(W, H), shader_paint(
        rad_grad((W / 2, H * 0.46), H * 0.72, [(0, 0, 0, 0), (0, 0, 0, 0), (0.02, 0, 0.03, vignette)], [0, 0.55, 1])))
    canvas.drawRect(skia.Rect.MakeWH(W, H), paint((*warm, warm_a), blend=skia.BlendMode.kMultiply))
