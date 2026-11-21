"""Camera, parallax layers, character placement helpers, shared set pieces (crowds, lights, particles)."""
import math
from dataclasses import dataclass
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, smooth_path, ellipse_path,
                 clamp, ease_io, noise1, hexc, poly_path)
from character import Character, BROTHERS, ORDER

CHARS = {k: Character(k) for k in BROTHERS}


@dataclass
class Cam:
    x: float = 0.0
    y: float = 0.0
    z: float = 1.0
    rot: float = 0.0     # degrees
    shake: float = 0.0


def cam_lerp(a, b, u):
    return Cam(a.x + (b.x - a.x) * u, a.y + (b.y - a.y) * u, a.z * (b.z / a.z) ** u, a.rot + (b.rot - a.rot) * u)


def cam_path(keys, t):
    """keys: [(time, Cam, ease)] -> Cam at t (ease applied on the segment that ends at that key)"""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, c0, _), (t1, c1, e) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / max(t1 - t0, 1e-6)
            return cam_lerp(c0, c1, e(u) if e else ease_io(u))
    return keys[-1][1]


class Layer:
    """with Layer(canvas, cam, depth): draw in world coords. depth 1 = character plane, <1 far, >1 near."""
    def __init__(self, c, cam, depth=1.0, t=0.0):
        self.c, self.cam, self.d, self.t = c, cam, depth, t

    def __enter__(self):
        c, cam, d = self.c, self.cam, self.d
        self.n = c.save()
        sx = cam.shake * noise1(self.t * 31, 3) * 6 * d
        sy = cam.shake * noise1(self.t * 29, 7) * 6 * d
        c.translate(W / 2 + sx, H / 2 + sy)
        c.rotate(cam.rot * min(d, 1.5))
        s = 1 + (cam.z - 1) * d if cam.z >= 1 else cam.z ** d
        c.scale(s, s)
        c.translate(-cam.x * d, -cam.y * d)
        return c

    def __exit__(self, *a):
        self.c.restoreToCount(self.n)


def silhouette(c, draw_fn, color=(0.06, 0.03, 0.05, 1.0), halo=None, halo_blur=14):
    """render draw_fn() as a flat silhouette (optionally with a blurred glow halo behind)"""
    if halo is not None:
        p = skia.Paint()
        p.setColorFilter(skia.ColorFilters.Blend(skia.Color4f(*halo).toColor(), skia.BlendMode.kSrcIn))
        p.setImageFilter(skia.ImageFilters.Blur(halo_blur, halo_blur))
        c.saveLayer(None, p)
        draw_fn()
        c.restore()
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(skia.Color4f(*color).toColor(), skia.BlendMode.kSrcIn))
    c.saveLayer(None, p)
    draw_fn()
    c.restore()


def particles(c, t, n, box, seed, col, size=(2, 6), speed=(10, 30), drift=1.0, tw=True, up=True, blend=skia.BlendMode.kPlus):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    xs = rng.uniform(x0, x1, n)
    ys = rng.uniform(y0, y1, n)
    sp = rng.uniform(*speed, n)
    sz = rng.uniform(*size, n)
    ph = rng.uniform(0, 6.28, n)
    hgt = y1 - y0
    for i in range(n):
        y = ys[i] - sp[i] * t if up else ys[i] + sp[i] * t
        y = y0 + (y - y0) % hgt
        x = xs[i] + math.sin(t * 0.8 + ph[i]) * 18 * drift
        a = (0.5 + 0.5 * math.sin(t * 3 + ph[i] * 3)) if tw else 1.0
        glow(c, x, y, sz[i] * 3, col, a * 0.9, blend=blend)


# ----------------------------------------------------------------------------- crowd
_CROWD_CACHE = {}


def crowd_row(seed, width, scale, base_col, hi_col, density=1.0):
    """cached picture of one row of audience heads & shoulders (silhouette with rim light)"""
    key = (seed, width, scale, base_col, hi_col, density)
    if key in _CROWD_CACHE:
        return _CROWD_CACHE[key]
    rng = np.random.default_rng(seed)
    rec = skia.PictureRecorder()
    c = rec.beginRecording(skia.Rect.MakeLTRB(-width / 2 - 100, -260 * scale, width / 2 + 100, 140 * scale))
    x = -width / 2
    while x < width / 2:
        s = scale * rng.uniform(0.85, 1.15)
        hr = 34 * s
        afro = rng.random() < 0.55
        hy = -110 * s + rng.uniform(-14, 14) * s
        body = smooth_path([(x - 70 * s, 140 * scale), (x - 62 * s, -30 * s), (x - 30 * s, -62 * s), (x + 30 * s, -62 * s),
                            (x + 62 * s, -30 * s), (x + 70 * s, 140 * scale)], True, 0.4)
        col = mix(base_col, '#000000', rng.uniform(0, 0.35))
        c.drawPath(body, paint(col))
        c.drawCircle(x, hy, hr * (1.45 if afro else 1.0), paint(col))
        if not afro and rng.random() < 0.3:
            c.drawOval(skia.Rect.MakeXYWH(x - hr * 1.5, hy - hr * 0.9, hr * 3, hr * 0.5), paint(col))
            c.drawRoundRect(skia.Rect.MakeXYWH(x - hr * 0.9, hy - hr * 1.6, hr * 1.8, hr * 0.9), 8, 8, paint(col))
        rim = paint(alpha(hi_col, 0.85), style='stroke', width=5 * s)
        c.drawArc(skia.Rect.MakeXYWH(x - hr * (1.45 if afro else 1), hy - hr * (1.45 if afro else 1),
                                     2 * hr * (1.45 if afro else 1), 2 * hr * (1.45 if afro else 1)), 200, 120, False, rim)
        x += rng.uniform(95, 140) * s / density
    pic = rec.finishRecordingAsPicture()
    _CROWD_CACHE[key] = pic
    return pic


def crowd(c, t, rows, energy, base_col, hi_col, width=2600, seed=0, y0=0.0, row_gap=70, scale0=1.0, arms=True,
          beat_phase=0.0, lighters=False):
    """rows of audience from back (small) to front (big). energy 0..1 drives bounce + raised arms."""
    for r in range(rows):
        k = r / max(rows - 1, 1)
        sc = scale0 * (0.45 + 0.75 * k)
        y = y0 + r * row_gap * (0.6 + 0.8 * k)
        bounce = energy * 10 * sc * abs(math.sin(math.pi * (beat_phase + r * 0.07)))
        c.save()
        c.translate(0, y - bounce)
        col = mix(base_col, '#000000', 0.15 * (1 - k))
        c.drawPicture(crowd_row(seed + r, int(width), round(sc, 3), col, hi_col))
        if arms and energy > 0.15:
            rng = np.random.default_rng(seed * 100 + r)
            n = int(width / 110 * energy * 0.6)
            for i in range(n):
                ax = rng.uniform(-width / 2, width / 2)
                ph = rng.uniform(0, 6.28)
                sway = math.sin(t * 3 + ph) * 0.35
                L = 130 * sc
                bx, by = ax, -60 * sc
                tx, ty = bx + math.sin(sway) * L, by - math.cos(sway) * L
                c.drawLine(bx, by, tx, ty, paint(col, style='stroke', width=22 * sc))
                c.drawCircle(tx, ty, 14 * sc, paint(col))
                if lighters and i % 3 == 0:
                    glow(c, tx, ty - 22 * sc, 26 * sc, '#ffcf6b', 0.8)
        c.restore()


def floor_reflection(c, fn, gy, alpha_=0.25):
    c.save()
    c.translate(0, 2 * gy)
    c.scale(1, -1)
    p = skia.Paint()
    p.setAlphaf(alpha_)
    p.setImageFilter(skia.ImageFilters.Blur(4, 10))
    c.saveLayer(None, p)
    fn()
    c.restore()
    c.restore()


def light_rig(c, x0, x1, y, n, t, cols, beat=0.0, intensity=1.0):
    """truss with par-can lights"""
    c.drawRect(skia.Rect.MakeLTRB(x0, y - 14, x1, y + 14), paint('#1c1820'))
    for i in range(int((x1 - x0) / 40)):
        xx = x0 + i * 40
        c.drawLine(xx, y - 14, xx + 40, y + 14, paint('#2e2a34', style='stroke', width=3))
    for i in range(n):
        x = x0 + (i + 0.5) * (x1 - x0) / n
        col = cols[i % len(cols)]
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 22, y + 10, 44, 40), 8, 8, paint('#111015'))
        a = intensity * (0.6 + 0.4 * abs(math.sin(math.pi * (beat + i * 0.25))))
        glow(c, x, y + 48, 60, col, a)
        c.drawCircle(x, y + 46, 14, paint(mix(col, '#ffffff', 0.6)))
