"""Beat It episode: shared captions, cut times, and set-dressing (studio gear, street, stage, screens)."""
import math
import numpy as np
import skia
import _paths  # noqa: F401
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, clamp, smoothstep,
                 ease_io, ease_out, ease_in, font, text_center, noise1, poly_path, smooth_path)
import timing as T
import bi_cast as K
from character import base_pose, DESIGNS
from world import CHARS, Cam, Layer, crowd, particles, silhouette
import choreo

DB = T.db
BEAT = T.PERIOD
HALF = 2 * BEAT
IVORY = (0.99, 0.96, 0.89)
GOLD = (1.0, 0.82, 0.38)
RED = (1.0, 0.32, 0.3)


# ----------------------------------------------------------------------------- characters
def pose(key, sched, t, **kw):
    return choreo.perform(sched, t, key, seed=DESIGNS[key].seed, **kw)


def draw(c, key, x, gy, h, P, outfit, L, t, shadow=True):
    return CHARS[key].draw(c, x, gy, h, P, outfit, L, t, shadow=shadow)


def place_head(key, P, h, head_xy):
    S0 = CHARS[key].skeleton(0, 0, h, P)
    return head_xy[0] - S0['head'][0], head_xy[1] - S0['head'][1]


def skel(key, x, gy, h, P):
    return CHARS[key].skeleton(x, gy, h, P)


def bg(c, cols, a=(0, 0), b=(0, H), pos=None):
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad(a, b, cols, pos)))


def u_of(t, t0, t1):
    return clamp((t - t0) / max(t1 - t0, 1e-6))


# ----------------------------------------------------------------------------- captions (TikTok/Shorts safe)
def cap(c, t, t0, t1, lines, y=300, size=80, accent=None, cx=W / 2 - 24, maxw=820, col=IVORY):
    """bold tracked serif caps on a soft scrim; eased fade/rise; fitted inside the safe zone (clear of the right rail)"""
    if not (t0 - 0.01 <= t <= t1 + 0.01):
        return
    lines = [s.replace('…', '...') for s in lines]
    a_in = smoothstep(t0, t0 + 0.34, t)
    a_out = 1 - smoothstep(t1 - 0.3, t1, t)
    a = min(a_in, a_out)
    if a <= 0:
        return
    rise = (1 - ease_out(a_in, 3)) * 22
    f = font('garamond_b', size)
    track = size * 0.07

    def width(s):
        return sum(f.measureText(ch) for ch in s) + track * (len(s) - 1)
    maxw_ = max(width(s) for s in lines)
    sc = min(1.0, maxw / maxw_)
    lh = size * 1.16 * sc
    top = y - size * 0.95 * sc + rise
    c.drawRoundRect(skia.Rect.MakeLTRB(cx - maxw_ * sc / 2 - 60, top - 30, cx + maxw_ * sc / 2 + 60, top + lh * len(lines) + 44),
                    56, 56, paint((0.02, 0.01, 0.02, 0.52 * a), blur=32))
    for i, s in enumerate(lines):
        yy = y + i * lh + rise
        c.save()
        c.translate(cx, yy)
        c.scale(sc, sc)
        x = -width(s) / 2
        cc = accent[1] if (accent and i == accent[0]) else col
        for ch in s:
            cw = f.measureText(ch)
            c.drawString(ch, x + 2, 4, f, paint((0.0, 0.0, 0.0, 0.8 * a), blur=6))
            c.drawString(ch, x, 0, f, paint((0.03, 0.01, 0.0, 0.7 * a), style='stroke', width=4.0))
            c.drawString(ch, x, 0, f, paint((*cc[:3], a)))
            x += cw + track
        c.restore()


def stamp(c, t, t0, t1, s, y=1560, size=40, cx=W / 2 - 24):
    """small tracked sans location/date stamp with rule lines"""
    a = min(smoothstep(t0, t0 + 0.3, t), 1 - smoothstep(t1 - 0.3, t1, t))
    if a <= 0:
        return
    f = font('spartan_b', size)
    w = sum(f.measureText(ch) for ch in s) + size * 0.25 * (len(s) - 1)
    c.drawRoundRect(skia.Rect.MakeLTRB(cx - w / 2 - 40, y - size - 18, cx + w / 2 + 40, y + 24), 30, 30,
                    paint((0, 0, 0, 0.45 * a), blur=18))
    text_center(c, s, cx, y, f, paint((*IVORY, a)), tracking=size * 0.25)
    grow = ease_out(smoothstep(t0, t0 + 0.6, t), 3)
    for sd in (-1, 1):
        c.drawLine(cx + sd * (w / 2 + 24), y - size * 0.35, cx + sd * (w / 2 + 24 + 90 * grow), y - size * 0.35,
                   paint((*GOLD, a), style='stroke', width=3))


# ----------------------------------------------------------------------------- studio gear
def reel(c, x, y, r, ang, tape=0.6, col='#b8b8c0'):
    c.drawCircle(x, y, r * (0.42 + 0.5 * tape), paint('#2a1c14'))          # tape pack
    for k in range(6):
        c.drawCircle(x, y, r * (0.42 + 0.08 * k * tape), paint((0.3, 0.2, 0.14, 0.4), style='stroke', width=1.2))
    c.drawCircle(x, y, r, paint(alpha(col, 0.35)))
    c.drawCircle(x, y, r, paint(col, style='stroke', width=r * 0.04))
    for k in range(3):
        a = math.radians(ang + k * 120)
        p = skia.Path()
        p.addCircle(x + math.cos(a) * r * 0.62, y + math.sin(a) * r * 0.62, r * 0.2)
        c.drawPath(p, paint('#141218'))
    c.drawCircle(x, y, r * 0.16, paint(col))
    c.drawCircle(x, y, r * 0.06, paint('#141218'))
    c.drawLine(x - r * 0.95, y - r * 0.2, x + r * 0.95, y - r * 0.25, paint((1, 1, 1, 0.08), style='stroke', width=r * 0.2, blur=r * 0.1))


def tape_machine(c, x, y, s, t, label=None, playing=True):
    """vintage 2-inch multitrack: two reels, head block, meter bridge"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 300 * s, y - 330 * s, 600 * s, 760 * s), 24 * s, 24 * s,
                    shader_paint(lin_grad((0, y - 330 * s), (0, y + 430 * s), ['#8a8478', '#5a5650', '#3a3632'])))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 300 * s, y - 330 * s, 600 * s, 760 * s), 24 * s, 24 * s,
                    paint('#1a1816', style='stroke', width=4 * s))
    spd = 260 if playing else 0
    reel(c, x - 150 * s, y - 150 * s, 125 * s, t * spd, 0.75)
    reel(c, x + 150 * s, y - 150 * s, 125 * s, t * spd * 1.2, 0.35)
    c.drawLine(x - 150 * s, y - 30 * s, x - 40 * s, y + 40 * s, paint('#2a1c14', style='stroke', width=8 * s))
    c.drawLine(x + 150 * s, y - 30 * s, x + 40 * s, y + 40 * s, paint('#2a1c14', style='stroke', width=8 * s))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 70 * s, y + 20 * s, 140 * s, 50 * s), 8 * s, 8 * s, paint('#c8c4bc'))
    for k in range(8):
        vu(c, x - 260 * s + k * 74 * s, y + 160 * s, 30 * s, T.env_at(['rms', 'low', 'snare', 'vocal'][k % 4], t + k * 0.03))
    for k in range(5):
        on = playing and k == 2
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 220 * s + k * 92 * s, y + 300 * s, 70 * s, 50 * s), 8 * s, 8 * s,
                        paint('#d83a2a' if on else '#2a2826'))
        if on:
            glow(c, x - 185 * s + k * 92 * s, y + 325 * s, 60 * s, '#ff4a2a', 0.6)
    if label:
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 180 * s, y + 380 * s, 360 * s, 40 * s), 4, 4, paint('#efe8d8'))
        text_center(c, label, x, y + 410 * s, font('spartan_b', 26 * s), paint('#2a1a12'))


def vu(c, x, y, r, level):
    """little round-shouldered VU meter with a needle that follows the music"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - r, y - r * 0.8, 2 * r, 1.4 * r), r * 0.2, r * 0.2,
                    shader_paint(rad_grad((x, y), r * 1.4, ['#ffe6a8', '#e8b860', '#8a5a20'])))
    glow(c, x, y, r * 1.6, '#ffb84a', 0.25)
    a = math.radians(-140 + 100 * clamp(level))
    c.drawLine(x, y + r * 0.5, x + math.cos(a) * r * 1.05, y + r * 0.5 + math.sin(a) * r * 1.05,
               paint('#1a0e08', style='stroke', width=max(1.2, r * 0.06)))
    c.drawArc(skia.Rect.MakeXYWH(x - r * 0.85, y - r * 0.35, r * 1.7, r * 1.7), 215, 110, False,
              paint((0.2, 0.1, 0.05, 0.6), style='stroke', width=max(1, r * 0.04)))


def console(c, x0, x1, y, depth, t, lit=1.0, seed=3):
    """mixing desk in perspective: channel strips, knobs, faders, LED meters (music-driven)"""
    rng = np.random.default_rng(seed)
    top = poly_path([(x0 + depth * 0.4, y), (x1 - depth * 0.4, y), (x1, y + depth), (x0, y + depth)])
    c.drawPath(top, shader_paint(lin_grad((0, y), (0, y + depth), ['#3a3634', '#24201e'])))
    n = 22
    for i in range(n):
        u = (i + 0.5) / n
        xt = x0 + depth * 0.4 + (x1 - x0 - depth * 0.8) * u
        xb = x0 + (x1 - x0) * u
        for j in range(7):
            v = j / 7
            kx, ky = xt + (xb - xt) * v, y + depth * v
            sz = 5 + 6 * v
            cc = ['#d83a2a', '#e8c040', '#3a8ad8', '#e8e4dc', '#e8e4dc', '#3ab87a', '#e8e4dc'][j]
            c.drawCircle(kx, ky + 6, sz, paint(cc))
        fx, fy = xt + (xb - xt) * 0.93, y + depth * 0.93
        lvl = T.env_at(['rms', 'low', 'snare', 'vocal'][i % 4], t + i * 0.011) * (0.6 + 0.4 * rng.random())
        c.drawRoundRect(skia.Rect.MakeXYWH(fx - 6, fy - 8 - 40 * lvl, 12, 14), 3, 3, paint('#d8d4cc'))
    # meter bridge
    c.drawRect(skia.Rect.MakeLTRB(x0 + depth * 0.4, y - 70, x1 - depth * 0.4, y), paint('#1a1816'))
    for i in range(n):
        u = (i + 0.5) / n
        xt = x0 + depth * 0.4 + (x1 - x0 - depth * 0.8) * u
        lvl = clamp(T.env_at(['rms', 'low', 'snare', 'vocal'][i % 4], t + i * 0.013) * 1.1 * lit)
        for k in range(10):
            on = k / 10 < lvl
            colr = '#3ae07a' if k < 6 else ('#ffd040' if k < 8 else '#ff4a3a')
            c.drawRect(skia.Rect.MakeXYWH(xt - 7, y - 12 - k * 5.5, 14, 4), paint(colr if on else '#202a22'))
        if lvl > 0.75:
            glow(c, xt, y - 50, 22, '#ffd040', 0.3 * lit)


def mic_stand(c, x, y, s, boom=True):
    """large-diaphragm studio condenser on a stand + pop filter"""
    c.drawLine(x, y, x, y + 900 * s, paint('#141418', style='stroke', width=14 * s))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 70 * s, y - 150 * s, 140 * s, 230 * s), 70 * s, 70 * s,
                    shader_paint(lin_grad((x - 70 * s, 0), (x + 70 * s, 0), ['#3a3a42', '#e8e8f2', '#7a7a84', '#2a2a30'])))
    for k in range(9):
        yy = y - 120 * s + k * 18 * s
        c.drawLine(x - 60 * s, yy, x + 60 * s, yy, paint((0.1, 0.1, 0.12, 0.45), style='stroke', width=2 * s))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 76 * s, y + 40 * s, 152 * s, 30 * s), 8, 8, paint('#c8c8d0'))


def amp_stack(c, x, y, s, t, glow_on=1.0):
    """guitar half-stack: head with knobs + 4x12 cab with grille"""
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 260 * s, y - 520 * s, 520 * s, 150 * s), 10 * s, 10 * s, paint('#141214'))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 240 * s, y - 455 * s, 480 * s, 60 * s), 6 * s, 6 * s, paint('#c8b890'))
    for k in range(8):
        c.drawCircle(x - 200 * s + k * 55 * s, y - 425 * s, 14 * s, paint('#141214'))
    glow(c, x + 210 * s, y - 490 * s, 30 * s, '#ff3a2a', 0.9 * glow_on)
    c.drawCircle(x + 210 * s, y - 490 * s, 8 * s, paint('#ff4a3a' if glow_on > 0.5 else '#401010'))
    cab = skia.Rect.MakeXYWH(x - 270 * s, y - 360 * s, 540 * s, 540 * s)
    c.drawRoundRect(cab, 12 * s, 12 * s, paint('#141214'))
    g = skia.Rect.MakeXYWH(x - 240 * s, y - 330 * s, 480 * s, 480 * s)
    c.drawRect(g, paint('#2a2620'))
    for k in range(0, 48):
        c.drawLine(g.left(), g.top() + k * 10 * s, g.right(), g.top() + k * 10 * s, paint((0.6, 0.55, 0.45, 0.12), style='stroke', width=2))
    pulse = T.env_at('low', t) * glow_on
    for i in range(2):
        for j in range(2):
            cx, cy = x - 120 * s + i * 240 * s, y - 210 * s + j * 240 * s
            c.drawCircle(cx, cy, 95 * s * (1 + 0.03 * pulse), paint((0, 0, 0, 0.35)))


def vinyl(c, x, y, r, ang, label='THRILLER', sub='MICHAEL JACKSON'):
    """a spinning record with a plain, generic label (no album artwork)"""
    c.drawCircle(x, y, r, paint('#0e0d10'))
    for k in range(28):
        c.drawCircle(x, y, r * (0.38 + 0.022 * k), paint((0.3, 0.3, 0.34, 0.45), style='stroke', width=1.2))
    for a0 in (25, 205):
        p = skia.Path()
        p.moveTo(x, y)
        p.arcTo(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0, 26, False)
        p.close()
        c.drawPath(p, paint((1, 1, 1, 0.1)))
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawCircle(0, 0, r * 0.33, paint('#ece4d4'))
    text_center(c, sub, 0, -r * 0.08, font('spartan', r * 0.06), paint('#2a1a14'))
    text_center(c, label, 0, r * 0.06, font('spartan', r * 0.1), paint('#8a1a1a'))
    c.drawCircle(0, 0, r * 0.025, paint('#111'))
    c.restore()


# ----------------------------------------------------------------------------- environments
def studio_room(c, t, warm=1.0, window=True):
    """the 1982 control room: acoustic panels, wood slats, a glass window into the live room"""
    bg(c, ['#2a2026', '#1c161a', '#120e10'])
    for k in range(14):
        x = -40 + k * 82
        c.drawRect(skia.Rect.MakeXYWH(x, 0, 60, H * 0.62), shader_paint(lin_grad((x, 0), (x + 60, 0), ['#4a3426', '#5e4430', '#3a281e'])))
    if window:
        wr = skia.Rect.MakeXYWH(120, 330, 840, 520)
        c.drawRect(wr, shader_paint(lin_grad((0, wr.top()), (0, wr.bottom()), ['#3a4a5a', '#24303a'])))
        for k in range(5):        # live room baffles + a drum kit glimpse
            c.drawRoundRect(skia.Rect.MakeXYWH(160 + k * 165, 470, 120, 300), 12, 12, paint((0.45, 0.5, 0.55, 0.35)))
        c.drawCircle(700, 720, 60, paint((0.75, 0.7, 0.6, 0.5)))
        c.drawCircle(810, 700, 45, paint((0.75, 0.7, 0.6, 0.5)))
        c.drawRect(wr, paint((1, 1, 1, 0.05)))
        c.drawLine(wr.left() + 80, wr.top(), wr.left() + 320, wr.bottom(), paint((1, 1, 1, 0.08), style='stroke', width=40, blur=10))
        c.drawRect(wr, paint('#20140e', style='stroke', width=26))
    glow(c, W * 0.5, 120, 500, '#ffcf88', 0.22 * warm)


def neon_sign(c, x, y, text, col, size, t, flick=0.0, seed=0):
    on = 1.0 if noise1(t * 9, seed) > flick - 1 + 0.2 else 0.25
    f = font('bebas', size)
    w = f.measureText(text)
    for b, a in ((34, 0.35), (14, 0.6)):
        c.drawString(text, x - w / 2, y, f, paint(alpha(col, a * on), blur=b, blend=skia.BlendMode.kPlus))
    c.drawString(text, x - w / 2, y, f, paint(mix(col, '#ffffff', 0.6 * on)))


def la_street(c, t, cam_dx=0.0, wet=1.0):
    """1983 downtown LA at night: brick warehouse with a loading door, neon, a streetlight, wet asphalt"""
    bg(c, ['#0a0a1e', '#1a1030', '#2a1430'], (0, 0), (0, H * 0.55))
    rng = np.random.default_rng(5)
    for i in range(70):
        glow(c, rng.uniform(0, W), rng.uniform(0, H * 0.25), 3, '#ffffff', 0.4)
    hz = H * 0.55
    c.save()
    c.translate(-cam_dx * 0.3, 0)
    for i in range(9):              # far skyline
        bx = -200 + i * 170
        bh = rng.uniform(200, 520)
        c.drawRect(skia.Rect.MakeXYWH(bx, hz - bh, 150, bh), paint('#141028'))
        for j in range(int(bh / 40)):
            for k in range(3):
                if rng.random() < 0.35:
                    c.drawRect(skia.Rect.MakeXYWH(bx + 18 + k * 44, hz - bh + 20 + j * 40, 20, 14), paint((1, 0.8, 0.45, 0.6)))
    c.restore()
    c.save()
    c.translate(-cam_dx, 0)
    # warehouse (centre) + side buildings
    wx0, wx1 = 180, 900
    c.drawRect(skia.Rect.MakeLTRB(wx0, hz - 640, wx1, hz + 10), shader_paint(lin_grad((0, hz - 640), (0, hz), ['#3a1e1c', '#2a1614'])))
    for j in range(32):
        for k in range(18):
            off = 20 if j % 2 else 0
            c.drawRect(skia.Rect.MakeXYWH(wx0 + off + k * 40, hz - 640 + j * 20, 38, 18), paint((0, 0, 0, 0.18), style='stroke', width=1.5))
    door = skia.Rect.MakeLTRB(400, hz - 330, 680, hz + 10)
    c.drawRect(door, paint('#0e0808'))
    for k in range(16):
        c.drawLine(door.left(), door.top() + k * 21, door.right(), door.top() + k * 21, paint((0.3, 0.25, 0.22, 0.5), style='stroke', width=3))
    c.drawRect(skia.Rect.MakeLTRB(door.left(), door.bottom() - 60, door.right(), door.bottom()), paint((1, 0.8, 0.5, 0.25), blur=20))
    for k in range(4):
        c.drawRect(skia.Rect.MakeXYWH(220 + k * 170, hz - 560, 110, 120), paint('#1a2430'))
        if k in (1, 2):
            c.drawRect(skia.Rect.MakeXYWH(220 + k * 170, hz - 560, 110, 120), paint((1, 0.75, 0.4, 0.35)))
    c.drawRect(skia.Rect.MakeLTRB(-400, hz - 900, wx0 - 10, hz + 10), paint('#1a1420'))
    c.drawRect(skia.Rect.MakeLTRB(wx1 + 10, hz - 820, W + 400, hz + 10), paint('#1c1622'))
    neon_sign(c, 40, hz - 520, 'HOTEL', '#ff4ab4', 120, t, 0.15, 1)
    neon_sign(c, 1010, hz - 430, 'LIQUOR', '#4ae0ff', 96, t, 0.05, 2)
    neon_sign(c, 540, hz - 380, 'WAREHOUSE 7', '#ffb04a', 58, t, 0.0, 3)
    # streetlight
    c.drawLine(960, hz + 30, 960, hz - 700, paint('#14121a', style='stroke', width=16))
    c.drawLine(960, hz - 700, 860, hz - 720, paint('#14121a', style='stroke', width=12))
    glow(c, 850, hz - 712, 160, '#ffd890', 0.7)
    beam(c, 850, hz - 712, 820, hz + 200, 20, 360, '#ffd890', 0.16, blur=30)
    c.restore()
    # wet road with reflections
    c.drawRect(skia.Rect.MakeLTRB(0, hz, W, H), shader_paint(lin_grad((0, hz), (0, H), ['#14101c', '#0a0a12'])))
    for (x, col, w) in ((40, '#ff4ab4', 160), (1010, '#4ae0ff', 160), (540, '#ffb04a', 120), (850, '#ffd890', 90)):
        xx = x - cam_dx
        for k in range(14):
            yy = hz + 30 + k * 60
            wob = 14 * math.sin(t * 3 + k * 1.3)
            c.drawRect(skia.Rect.MakeXYWH(xx - w / 2 + wob, yy, w * (1 - k * 0.03), 18), paint(alpha(col, 0.25 * wet * (1 - k / 16)), blur=8,
                                                                                         blend=skia.BlendMode.kPlus))
    for k in range(12):
        y = hz + 40 + k * k * 9
        c.drawLine(W / 2 - 4, y, W / 2 + 4, y + 30, paint((0.9, 0.8, 0.4, 0.4), style='stroke', width=6 + k))


def tv_set(c, x, y, w, h_, draw_screen, t, wood=True):
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h_), 24, 24, paint('#4a3424' if wood else '#2a2826'))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 6, y + 6, w - 12, h_ - 12), 20, 20, paint((1, 1, 1, 0.06), style='stroke', width=3))
    scr = skia.Rect.MakeXYWH(x + w * 0.07, y + h_ * 0.08, w * 0.68, h_ * 0.8)
    rr = skia.RRect.MakeRectXY(scr, w * 0.08, w * 0.08)
    c.save()
    c.clipRRect(rr, doAntiAlias=True)
    draw_screen(scr)
    for yy in range(int(scr.top()), int(scr.bottom()), 5):
        c.drawLine(scr.left(), yy, scr.right(), yy, paint((0, 0, 0, 0.14), style='stroke', width=2))
    c.drawOval(skia.Rect.MakeXYWH(scr.left() - scr.width() * 0.2, scr.top() - scr.height() * 0.4, scr.width() * 0.9, scr.height() * 0.7),
               paint((1, 1, 1, 0.08)))
    c.restore()
    for k in range(3):
        c.drawCircle(x + w * 0.87, y + h_ * (0.25 + 0.2 * k), w * 0.035, paint('#a89880'))


def beatit_screen(c, scr, t, seed=0):
    """what the TVs show: the music-video dance - red jacket in a dark warehouse, crew silhouettes behind"""
    c.drawRect(scr, shader_paint(lin_grad((0, scr.top()), (0, scr.bottom()), ['#2a1a2a', '#140a14'])))
    beam(c, scr.centerX(), scr.top() - 40, scr.centerX(), scr.bottom(), 10, scr.width() * 0.6, '#ffe8d0', 0.3, blur=10)
    hh = scr.height() * 0.62
    gy = scr.bottom() - scr.height() * 0.08
    for i, dx in enumerate((-0.32, 0.32)):
        P = pose(f'x{i + 4}', [(0, 'point_hit' if (T.beat_at(t) // 2) % 2 else 'step_touch', dict(start=math.floor(T.beat_at(t) - T.PHASE)))], t)
        silhouette(c, lambda: draw(c, f'x{i + 4}', scr.centerX() + dx * scr.width(), gy - 6, hh * 0.85, P, K.O_DANCERS[0], K.L_DARK, t, False),
                   color=(0.05, 0.03, 0.06, 1))
    P = pose(K.MJ, [(0, 'point_hit' if (T.beat_at(t) // 2) % 2 else 'step_touch', dict(start=math.floor(T.beat_at(t) - T.PHASE)))], t + seed * 0.0)
    draw(c, K.MJ, scr.centerX(), gy, hh, P, K.O_BEATIT, K.L_DARK, t, shadow=False)


def stage_world(c, t, energy=1.0, seed=7, beams=True):
    """a huge concert: deep blue sky, beams, truss, crowd to the horizon"""
    beat = T.beat_at(t)
    bg(c, ['#03031a', '#0c0c34', '#1a1250'])
    if beams:
        for i in range(9):
            x = W * (i + 0.5) / 9
            sw = 260 * math.sin(t * 0.8 + i)
            beam(c, x, H * 0.33, x + sw, -200, 18, 260, ['#ffffff', '#9fd8ff', '#ff9ad8'][i % 3], 0.2 * energy, blur=30)
    c.save()
    c.translate(W / 2, H * 0.52)
    crowd(c, t, 12, energy, '#05051a', '#a8b8ff', width=3600, seed=seed, y0=0, row_gap=120, scale0=0.6, beat_phase=beat,
          lighters=True)
    c.restore()
