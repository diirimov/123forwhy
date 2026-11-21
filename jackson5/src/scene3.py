"""SCENE 3 - THE BREAKTHROUGH. Spinning vinyl -> recording studio (control room, close-ups, producers) -> hit-record explosion."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, noise1, font, text_center, cel, ellipse_path)
from world import Cam, cam_path, Layer, CHARS, particles
from character import Character, outfits, BROTHERS, base_pose
import choreo
import timing as T

DB = T.db
T0 = DB(8)                 # record drops on this downbeat
T_STUDIO = DB(9)
T_CLOSE = DB(10)
T_PROD = DB(11)
T_BOOM = DB(12)            # gold record -> explosion, peaks at DB(13)
T_END = DB(13)
OUT = outfits('studio')
LIGHT = dict(key=(-0.6, -0.8), amb='#ffd0a0', amb_a=0.25, rim='#9ff0ff', line='#2a1420', floor_shadow=0.35)


# --------------------------------------------------------------------------- record
def record(c, x, y, r, angle, gold=0.0, label='#e8692a'):
    base = mix('#141016', '#c9952a', gold)
    c.drawCircle(x, y, r, paint(base))
    for k in range(34):
        rr = r * (0.36 + 0.62 * k / 34)
        c.drawCircle(x, y, rr, paint(alpha(mix('#2a2430', '#ffe08a', gold), 0.45), style='stroke', width=1.2))
    # specular sweep (rotates against the spin so the vinyl reads as glossy)
    for k, a0 in enumerate((40, 220)):
        p = skia.Path()
        p.moveTo(x, y)
        p.arcTo(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), a0 - angle * 0.05, 26, False)
        p.close()
        c.drawPath(p, paint((1, 1, 1, 0.10 + 0.25 * gold), blur=r * 0.02))
    c.save()
    c.rotate(angle, x, y)
    lr = r * 0.34
    c.drawCircle(x, y, lr, paint(label))
    c.drawCircle(x, y, lr, paint(shade(label, -0.3), style='stroke', width=lr * 0.05))
    c.drawCircle(x, y, lr * 0.08, paint('#120c10'))
    f = font('spartan', lr * 0.2)
    text_center(c, 'THE JACKSON 5', x, y - lr * 0.38, f, paint('#2a1208'))
    text_center(c, 'I WANT YOU BACK', x, y + lr * 0.52, font('spartan_b', lr * 0.13), paint('#2a1208'))
    c.drawCircle(x + lr * 0.55, y, lr * 0.07, paint('#ffd060'))
    c.restore()


def scene_record(c, t):
    u = (t - T0) / (T_STUDIO - T0)
    ang = (t - T0) * 200 * (1 + u)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.45), H * 0.8, ['#7a2a8a', '#3a1450', '#12061e'])))
    # turntable plinth
    zoom = 1.0 + 4.0 * ease_in(clamp((u - 0.55) / 0.45), 3)
    c.save()
    c.translate(W / 2, H * 0.47)
    c.scale(zoom, zoom)
    c.rotate(-8 + 8 * u)
    c.drawRoundRect(skia.Rect.MakeXYWH(-520, -560, 1040, 1120), 40, 40, shader_paint(lin_grad((0, -560), (0, 560),
                    ['#5a3420', '#2a160c'])))
    c.drawRoundRect(skia.Rect.MakeXYWH(-520, -560, 1040, 1120), 40, 40, paint('#c9952a', style='stroke', width=6))
    c.drawCircle(0, 0, 470, paint('#1a1a20'))
    record(c, 0, 0, 450, ang)
    # tonearm lowering onto the record (lands on the first beat after the drop)
    land = ease_out(clamp((t - T0) / (T.PERIOD * 0.9)), 3)
    arm_ang = -38 + 20 * land
    c.save()
    c.translate(420, -420)
    c.rotate(arm_ang + 90)
    c.drawRoundRect(skia.Rect.MakeXYWH(-14, 0, 28, 520), 14, 14, paint('#cfcfd8'))
    c.drawRoundRect(skia.Rect.MakeXYWH(-30, 500, 60, 90), 10, 10, paint('#2a2a30'))
    c.restore()
    c.drawCircle(420, -420, 60, paint('#8a8a96'))
    c.restore()
    # light streak sweeping across on the downbeat
    k = math.exp(-((t - T0) / 0.15) ** 2)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.9, 0.7, 0.55 * k)))
    if u > 0.8:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.95, 0.85, ease_in((u - 0.8) / 0.2, 2))))


# --------------------------------------------------------------------------- studio
def vu(c, x, y, w, level, label):
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, w * 0.62), 8, 8, paint('#1a1410'))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 8, y + 8, w - 16, w * 0.62 - 16), 6, 6, shader_paint(lin_grad((x, y), (x, y + w * 0.6),
                    ['#fff2c8', '#f0c870'])))
    glow(c, x + w / 2, y + w * 0.3, w * 0.6, '#ffcf6a', 0.35)
    cx, cy = x + w / 2, y + w * 0.56
    for k in range(9):
        a = math.radians(-50 + k * 12.5)
        r0, r1 = w * 0.36, w * (0.42 if k % 2 == 0 else 0.4)
        col = '#c02a1a' if k > 6 else '#2a1a10'
        c.drawLine(cx + math.sin(a) * r0, cy - math.cos(a) * r0, cx + math.sin(a) * r1, cy - math.cos(a) * r1,
                   paint(col, style='stroke', width=2))
    a = math.radians(-50 + 100 * clamp(level))
    c.drawLine(cx, cy, cx + math.sin(a) * w * 0.42, cy - math.cos(a) * w * 0.42, paint('#1a0a06', style='stroke', width=3))
    text_center(c, label, cx, y + w * 0.5, font('spartan_b', w * 0.08), paint('#5a3a1a'))


def console(c, t):
    lvl = T.env_at('rms', t)
    low = T.env_at('low', t)
    voc = T.env_at('vocal', t)
    c.drawPath(poly_path([(-900, 420), (900, 420), (1100, 1300), (-1100, 1300)]), shader_paint(lin_grad((0, 420), (0, 1300),
               ['#5a4a3a', '#2a2018'])))
    c.drawRect(skia.Rect.MakeLTRB(-900, 400, 900, 430), paint('#8a7a5a'))
    for i, (lv, lab) in enumerate([(lvl * 0.9, 'MIX'), (low * 1.1, 'BASS'), (voc * 1.0, 'VOX'), (lvl * 0.8, 'BAND')]):
        vu(c, -560 + i * 290, 200, 260, lv + 0.04 * noise1(t * 20, i), lab)
    rng = np.random.default_rng(5)
    for row in range(4):
        for k in range(16):
            x = -820 + k * 108 + row * 12
            y = 520 + row * 150
            c.drawCircle(x, y, 22, paint('#2a2420'))
            a = rng.uniform(0, 6.28)
            c.drawLine(x, y, x + math.cos(a) * 18, y + math.sin(a) * 18, paint('#e8e0d0', style='stroke', width=3))
            on = (k + row) % 5 == 0
            glow(c, x + 34, y - 26, 16, '#ff5a2a' if on else '#5aff8a', 0.6 if on else 0.35 * (0.5 + lvl))
    for k in range(16):           # faders that ride the music
        x = -820 + k * 108
        c.drawRect(skia.Rect.MakeXYWH(x - 4, 1120, 8, 160), paint('#111'))
        fy = 1260 - 140 * clamp(0.4 + 0.5 * T.env_at('rms', t - k * 0.02) * (0.7 + 0.3 * math.sin(k)))
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 26, fy - 14, 52, 28), 4, 4, paint('#d8d0c0'))


def reel(c, x, y, r, ang):
    c.drawCircle(x, y, r, paint('#8a8a92'))
    c.drawCircle(x, y, r * 0.86, paint('#3a2a20'))
    c.save()
    c.rotate(ang, x, y)
    for k in range(3):
        a = k * 120
        c.save()
        c.rotate(a, x, y)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - r * 0.18, y - r * 0.75, r * 0.36, r * 0.45), 10, 10, paint('#c8c8d0'))
        c.restore()
    c.restore()
    c.drawCircle(x, y, r * 0.15, paint('#e0e0e8'))


def studio_room(c, t, beat, close=False):
    """the live room behind the glass: acoustic panels, warm light, the brothers at microphones"""
    c.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 1400, 300), shader_paint(lin_grad((0, -1200), (0, 300), ['#2a3a4a', '#4a5a5a', '#6a5a4a'])))
    for k in range(-8, 9):
        c.drawRoundRect(skia.Rect.MakeXYWH(k * 160 - 70, -900, 140, 560), 10, 10, paint(('#3a4a52' if k % 2 else '#56443a')))
    glow(c, -300, -700, 600, '#ffcf8a', 0.25)
    c.drawRect(skia.Rect.MakeLTRB(-1400, 300, 1400, 900), shader_paint(lin_grad((0, 300), (0, 900), ['#5a3a2a', '#2a1a12'])))
    gy = 300
    pos = [('tito', -330, -20), ('jackie', -170, -40), ('michael', 0, 20), ('jermaine', 170, -40), ('marlon', 330, -20)]
    for k, x, dy in sorted(pos, key=lambda p: p[2]):
        sched = SCHED[k]
        P = choreo.perform(sched, t, k, seed=BROTHERS[k].seed, sing=1.0 if k in ('michael', 'jermaine') else 0.5,
                           base_kw=dict(instrument='guitar' if k == 'tito' else None))
        h = 330 * BROTHERS[k].height
        CHARS[k].draw(c, x, gy + dy, h, P, OUT[k], LIGHT, t)
        if k in ('michael', 'jermaine', 'jackie', 'marlon'):
            mx = x + (55 if k != 'jermaine' else -55)
            top = gy + dy - h * 0.66
            c.drawLine(mx, gy + dy, mx, top, paint('#141418', style='stroke', width=5))
            c.drawRoundRect(skia.Rect.MakeXYWH(mx - 18, top - 46, 36, 56), 14, 14, shader_paint(lin_grad((mx - 18, 0), (mx + 18, 0),
                            ['#6a6a72', '#e8e8f0', '#6a6a72'])))


SCHED = {
    'michael': [(0, 'groove', dict(amp=0.9, snap=True))],
    'jermaine': [(0, 'groove', dict(amp=0.8, snap=True))],
    'jackie': [(0, 'groove', dict(amp=0.6, snap=True))],
    'marlon': [(0, 'groove', dict(amp=0.7, snap=True))],
    'tito': [(0, 'play', {})],
}


def producer(c, x, y, s, t, beat, kind, excite):
    """adult producer seen from behind / three-quarter, bobbing to the beat; jumps up when excited"""
    bob = 8 * s * abs(math.sin(math.pi * beat)) + excite * 40 * s
    y = y - bob
    c.drawPath(smooth_path([(x - 160 * s, y + 420 * s), (x - 140 * s, y + 60 * s), (x - 70 * s, y - 10 * s), (x + 70 * s, y - 10 * s),
                            (x + 140 * s, y + 60 * s), (x + 160 * s, y + 420 * s)], True, 0.4),
               paint('#2a2a3a' if kind == 0 else '#4a2a1a'))
    c.drawCircle(x, y - 90 * s, 82 * s, paint('#5a3a28'))
    if kind == 0:
        c.drawCircle(x, y - 115 * s, 92 * s, paint('#1a1210'))
        c.drawRect(skia.Rect.MakeXYWH(x - 120 * s, y - 120 * s, 40 * s, 30 * s), paint('#111'))     # headphones
        c.drawRect(skia.Rect.MakeXYWH(x + 80 * s, y - 120 * s, 40 * s, 30 * s), paint('#111'))
        c.drawArc(skia.Rect.MakeXYWH(x - 105 * s, y - 230 * s, 210 * s, 200 * s), 180, 180, False,
                  paint('#111', style='stroke', width=10 * s))
    else:
        c.drawArc(skia.Rect.MakeXYWH(x - 82 * s, y - 175 * s, 164 * s, 120 * s), 180, 180, True, paint('#2a1a12'))
    # arm: thumbs-up / fist pump when excited
    ax, ay = x + 120 * s, y + 60 * s
    a = math.radians(-160 * excite + 10)
    ex_, ey_ = ax + math.sin(a) * 130 * s, ay - math.cos(a) * 130 * s * (1 if excite > 0.1 else -1)
    c.drawLine(ax, ay, ex_, ey_, paint('#2a2a3a' if kind == 0 else '#4a2a1a', style='stroke', width=48 * s))
    c.drawCircle(ex_, ey_, 30 * s, paint('#5a3a28'))
    if excite > 0.3:
        c.drawRoundRect(skia.Rect.MakeXYWH(ex_ - 9 * s, ey_ - 60 * s, 18 * s, 40 * s), 8, 8, paint('#5a3a28'))


def control_room(c, t, beat, excite=0.0, push=0.0):
    cam = Cam(0, -120 + 150 * push, 0.9 + 0.5 * push)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#120c10'))
    with Layer(c, cam, 0.85, t):
        studio_room(c, t, beat)
    with Layer(c, cam, 1.0, t):
        # control room wall with the big window
        wall = skia.Path()
        wall.addRect(skia.Rect.MakeLTRB(-2000, -2000, 2000, 2000))
        win = skia.Path()
        win.addRoundRect(skia.Rect.MakeLTRB(-700, -1050, 700, 200), 30, 30)
        c.drawPath(skia.Op(wall, win, skia.PathOp.kDifference_PathOp), shader_paint(lin_grad((0, -1400), (0, 300),
                   ['#2a1a2a', '#3a2430'])))
        c.drawRoundRect(skia.Rect.MakeLTRB(-700, -1050, 700, 200), 30, 30, paint('#8a6a4a', style='stroke', width=26))
        for k in range(3):     # glass reflections
            x = -500 + k * 380 + 30 * math.sin(t * 0.5)
            c.drawPath(poly_path([(x, -1050), (x + 120, -1050), (x - 150, 200), (x - 270, 200)]), paint((0.8, 0.95, 1, 0.06)))
        reel(c, -860, -620, 150, t * 260)
        reel(c, -860, -260, 150, t * 240)
        c.drawRoundRect(skia.Rect.MakeLTRB(-1040, -820, -680, -60), 20, 20, paint('#5a4a3a', style='stroke', width=8))
        glow(c, 780, -900, 30, '#ff2a1a', 0.6 + 0.4 * math.sin(t * 6))
        text_center(c, 'ON AIR', 780, -830, font('spartan', 40), paint('#ff4a2a'))
    with Layer(c, cam, 1.25, t):
        console(c, t)
    with Layer(c, cam, 1.5, t):
        producer(c, -470, 420, 1.15, t, beat, 0, excite)
        producer(c, 520, 470, 1.2, t, beat + 0.5, 1, excite * 0.9)


def close_up(c, t, beat):
    """Michael singing at the mic, soft studio key light"""
    u = (t - T_CLOSE) / (T_PROD - T_CLOSE)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W * 0.35, H * 0.3), H * 0.9, ['#5a6a7a', '#2a3440', '#141a22'])))
    for k in range(5):
        c.drawRoundRect(skia.Rect.MakeXYWH(k * 260 - 120, 160, 200, 1100), 20, 20, paint((0.4, 0.5, 0.55, 0.15)))
    glow(c, 200, 400, 700, '#ffd0a0', 0.25)
    P = choreo.perform([(0, 'groove', dict(amp=0.5, arms=False))], t, 'michael', seed=5, sing=1.3)
    P['lsh'], P['lel'] = 0.5, -1.3
    P['rsh'], P['rel'] = 0.2, -2.0
    P['lhand'] = 'open'
    P['rhand'] = 'relaxed'
    P['ey'] = -0.2
    P['hyaw'] = 0.3 + 0.1 * math.sin(t)
    P['blink'] = max(P['blink'], 0.55 if T.env_at('vocal', t) > 0.7 else 0)
    s = 1.0 + 0.18 * ease_io(u)
    h = 2500 * s
    gx = W / 2 - 90
    gy = H * 0.5 + h * 0.86
    CHARS['michael'].draw(c, gx, gy, h, P, OUT['michael'], dict(LIGHT, rim='#aef4ff'), t, shadow=False)
    # foreground studio mic (big, out of focus edge)
    mx, my = W * 0.86, H * 0.66
    c.drawRoundRect(skia.Rect.MakeXYWH(mx - 95, my - 150, 190, 300), 95, 95, shader_paint(lin_grad((mx - 95, 0), (mx + 95, 0),
                    ['#3a3a42', '#e8e8f2', '#5a5a62', '#2a2a30'])))
    for k in range(9):
        c.drawLine(mx - 90, my - 110 + k * 26, mx + 90, my - 110 + k * 26, paint((0, 0, 0, 0.35), style='stroke', width=3))
    c.drawRect(skia.Rect.MakeXYWH(mx - 14, my + 150, 28, 700), paint('#141418'))
    # pop filter ring



# --------------------------------------------------------------------------- explosion
def explosion(c, t):
    u = clamp((t - T_BOOM) / (T_END - T_BOOM))
    beat = T.beat_at(t)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H / 2), H, ['#ff9a2a', '#a02a8a', '#1a6a7a', '#1a0a2a'],
                                                             [0, 0.35, 0.7, 1])))
    cx, cy = W / 2, H / 2
    # rotating rays (orange / purple / turquoise / gold)
    cols = ['#ff7a1a', '#7a2aa0', '#1ac0c0', '#ffd040']
    for k in range(24):
        a = k / 24 * 2 * math.pi + t * 0.6
        p = poly_path([(cx, cy), (cx + math.cos(a - 0.06) * 2400, cy + math.sin(a - 0.06) * 2400),
                       (cx + math.cos(a + 0.06) * 2400, cy + math.sin(a + 0.06) * 2400)])
        c.drawPath(p, paint(alpha(cols[k % 4], 0.35 + 0.25 * u), blend=skia.BlendMode.kScreen))
    # the record turns gold and grows
    r = 300 + 120 * back_out(clamp(u * 1.6), 1.8) + 30 * abs(math.sin(math.pi * beat))
    record(c, cx, cy, r, t * 420, gold=smoothstep(0.0, 0.5, u), label='#ffcf40')
    # rings + confetti burst on the last beats
    burst = clamp((u - 0.5) / 0.5)
    for k in range(4):
        rr = r + burst * (400 + k * 300)
        c.drawCircle(cx, cy, rr, paint(alpha(cols[k], 0.8 * (1 - burst)), style='stroke', width=26 * (1 - burst) + 2))
    rng = np.random.default_rng(9)
    for i in range(160):
        a = rng.uniform(0, 2 * math.pi)
        sp = rng.uniform(300, 1400)
        d = sp * burst
        x, y = cx + math.cos(a) * (r * 0.8 + d), cy + math.sin(a) * (r * 0.8 + d) + 400 * burst * burst
        c.save()
        c.rotate(rng.uniform(0, 360) + t * 400, x, y)
        c.drawRect(skia.Rect.MakeXYWH(x - 10, y - 5, 20, 10), paint(cols[i % 4]))
        c.restore()
    glow(c, cx, cy, 700, '#fff0c0', 0.6 * burst)
    if t > T_END - 0.18:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.97, 0.9, smoothstep(T_END - 0.18, T_END, t))))


def draw(c, t):
    beat = T.beat_at(t)
    if t < T_STUDIO:
        scene_record(c, t)
    elif t < T_CLOSE:
        u = (t - T_STUDIO) / (T_CLOSE - T_STUDIO)
        control_room(c, t, beat, push=ease_io(u) * 0.6)
        fl = 1 - smoothstep(T_STUDIO, T_STUDIO + 0.3, t)
        if fl > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.95, 0.85, fl)))
    elif t < T_PROD:
        close_up(c, t, beat)
    elif t < T_BOOM:
        ex = back_out(clamp((t - T_PROD) / 0.35), 2.0)
        control_room(c, t, beat, excite=ex, push=0.15)
    else:
        explosion(c, t)
