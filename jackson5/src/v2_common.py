"""V2 shared pieces: documentary captions, cast/group drawing, Joe's cast shadows, the night rehearsal room."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, smooth_path, poly_path,
                 clamp, ease_io, ease_out, smoothstep, font, noise1)
from world import Layer, CHARS, particles
from character import Character, outfits, BROTHERS, JOE_OUTFIT, DJ_OUTFIT, DESIGNS
import choreo
import timing as T

DB = T.db
FIVE = ['jackie', 'tito', 'jermaine', 'marlon', 'michael']
JOE = Character('joe')
DJ = Character('dj')
KIDS = [Character('kid1'), Character('kid2')]


# ----------------------------------------------------------------------------- captions
IVORY = (0.98, 0.95, 0.88)


def caption(c, t, t0, t1, lines, y=330, size=80, gap=1.18):
    """premium documentary title: tracked ivory caps, soft shadow, eased fade + rise, max 2 lines, auto-fit width."""
    if not (t0 - 0.01 <= t <= t1 + 0.01):
        return
    a_in = smoothstep(t0, t0 + 0.42, t)
    a_out = 1 - smoothstep(t1 - 0.38, t1, t)
    a = min(a_in, a_out)
    if a <= 0:
        return
    rise = (1 - ease_out(a_in, 3)) * 26
    f = font('garamond', size)
    track = size * 0.085 + 3 * (1 - a_in)
    def width(s):
        return sum(f.measureText(ch) for ch in s) + track * (len(s) - 1)
    maxw = max(width(s) for s in lines)
    sc = min(1.0, 900 / maxw)
    for i, s in enumerate(lines):
        yy = y + i * size * gap * sc + rise
        c.save()
        c.translate(W / 2, yy)
        c.scale(sc, sc)
        w = width(s)
        x = -w / 2
        for ch in s:
            cw = f.measureText(ch)
            c.drawString(ch, x + 2, 3, f, paint((0.03, 0.01, 0.0, 0.75 * a), blur=7))
            c.drawString(ch, x, 0, f, paint((0.05, 0.02, 0.0, 0.55 * a), style='stroke', width=3.0))
            c.drawString(ch, x, 0, f, paint((*IVORY, a)))
            x += cw + track
        c.restore()
    # hairline rule under the block
    ln = 160 * ease_out(a_in, 3) * a_out
    yy = y + (len(lines) - 1) * size * gap * sc + size * 0.42 + rise
    c.drawLine(W / 2 - ln / 2, yy, W / 2 + ln / 2, yy, paint((1, 0.85, 0.55, 0.8 * a), style='stroke', width=2))


# ----------------------------------------------------------------------------- cast
def cast_pose(key, sched, t, ripple=0.0, sing=None, instrument=None, over=None):
    seed = DESIGNS[key].seed
    P = choreo.perform(sched, t, key, seed=seed, ripple=ripple, sing=sing, base_kw=dict(instrument=instrument))
    if over:
        P.update(over(t) if callable(over) else over)
    return P


def draw_cast(c, t, members, L, era, base_h=360):
    """members: list of dict(key, x, gy, sched, [ripple, sing, instrument, over, outfit, scale, light]). Drawn back-to-front."""
    O = outfits(era) if era else {}
    out = {}
    for m in sorted(members, key=lambda m: m['gy']):
        k = m['key']
        x = m['x'](t) if callable(m['x']) else m['x']
        P = cast_pose(k, m['sched'], t, m.get('ripple', 0.0), m.get('sing'), m.get('instrument'), m.get('over'))
        ch = JOE if k == 'joe' else (DJ if k == 'dj' else CHARS[k])
        o = m.get('outfit') or (JOE_OUTFIT if k == 'joe' else DJ_OUTFIT if k == 'dj' else O[k])
        h = base_h * DESIGNS[k].height * m.get('scale', 1.0)
        out[k] = ch.draw(c, x, m['gy'], h, P, o, m.get('light', L), t)
    return out


def five_check(members):
    n = sum(1 for m in members if m['key'] in FIVE)
    assert n in (0, 5) or all(m['key'] == 'michael' for m in members if m['key'] in FIVE), n
    return n


# ----------------------------------------------------------------------------- Joe's cast shadows
def floor_shadow(c, draw_fn, foot, length=2.2, squash=0.2, a=0.55, blur=10):
    """project a figure drawn standing at `foot` flat onto the floor, stretching toward screen-left/front"""
    x0, y0 = foot
    m = skia.Matrix.MakeAll(1, length, -length * y0, 0, -squash, y0 * (1 + squash), 0, 0, 1)
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(skia.Color4f(0.02, 0.01, 0.03, a).toColor(), skia.BlendMode.kSrcIn))
    p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
    c.saveLayer(None, p)
    c.concat(m)
    draw_fn()
    c.restore()


def wall_shadow(c, draw_fn, a=0.5, blur=14):
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(skia.Color4f(0.03, 0.01, 0.04, a).toColor(), skia.BlendMode.kSrcIn))
    p.setImageFilter(skia.ImageFilters.Blur(blur, blur))
    c.saveLayer(None, p)
    draw_fn()
    c.restore()


# ----------------------------------------------------------------------------- the night rehearsal room
GY = 560          # floor line
DOOR = (470, 760)     # door x-range on the back wall (world, depth-0.65 layer)
_rng = np.random.default_rng(1964)


def room_wall(c, t, door=0.0, night=1.0, clock_t=None):
    """back wall: wallpaper, wainscot, window (left), clock, photos, door (right) with hallway light."""
    c.drawRect(skia.Rect.MakeLTRB(-1600, -1500, 1600, GY), shader_paint(lin_grad((0, -1300), (0, GY),
               [mix('#5a3b2a', '#20202e', night * 0.6), mix('#8a5a36', '#2e2a34', night * 0.55),
                mix('#a5713f', '#3a3030', night * 0.5)])))
    for iy in range(-16, 12):
        for ix in range(-17, 18):
            x, y = ix * 90 + (iy % 2) * 45, iy * 90
            c.drawPath(poly_path([(x, y - 22), (x + 16, y), (x, y + 22), (x - 16, y)]), paint((0.95, 0.78, 0.5, 0.09)))
    c.drawRect(skia.Rect.MakeLTRB(-1600, GY - 230, 1600, GY), paint(mix('#5a3622', '#241a1a', night * 0.5)))
    c.drawRect(skia.Rect.MakeLTRB(-1600, GY - 240, 1600, GY - 224), paint(mix('#7a4c2e', '#30241e', night * 0.5)))
    for x in range(-1600, 1600, 140):
        c.drawRect(skia.Rect.MakeXYWH(x + 18, GY - 205, 104, 175), paint((0.2, 0.1, 0.05, 0.6), style='stroke', width=4))
    # window (left) - night outside
    wr = skia.Rect.MakeLTRB(-760, -760, -380, -240)
    c.drawRect(wr, shader_paint(lin_grad((0, -760), (0, -240), ['#111a33', '#25335a'])))
    for k in range(14):
        c.drawCircle(-740 + (k * 53) % 360, -740 + (k * 97) % 480, 2, paint((1, 1, 0.9, 0.6)))
    c.drawRect(wr, paint('#d8ccb4', style='stroke', width=16))
    c.drawLine(-570, -760, -570, -240, paint('#d8ccb4', style='stroke', width=10))
    for x in (-820, -320):
        cols = ['#5a1a12' if k % 2 else '#8a3a22' for k in range(8)]
        c.drawRect(skia.Rect.MakeLTRB(x - 60, -820, x + 60, -150), shader_paint(lin_grad((x - 60, 0), (x + 60, 0), cols)))
    # wall clock
    wall_clock(c, -60, -720, 105, clock_t if clock_t is not None else 21.6 + t / 3600)
    # photos
    for i, (x, y, w, h) in enumerate([(170, -760, 130, 160), (330, -700, 100, 130)]):
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint('#3a2214'))
        c.drawRect(skia.Rect.MakeXYWH(x + 10, y + 10, w - 20, h - 20), shader_paint(lin_grad((x, y), (x, y + h), ['#c8b490', '#8a7452'])))
        for k in range(2):
            px = x + w * (k + 1) / 3
            c.drawCircle(px, y + h * 0.42, 13, paint((0.3, 0.2, 0.12, 0.8), blur=1.5))
            c.drawOval(skia.Rect.MakeXYWH(px - 20, y + h * 0.55, 40, 36), paint((0.3, 0.2, 0.12, 0.8), blur=1.5))
    # door (right): frame, dark opening / open door with hallway light
    x0, x1 = DOOR
    top = -420
    c.drawRect(skia.Rect.MakeLTRB(x0 - 26, top - 26, x1 + 26, GY), paint('#e2d6c0'))
    hall = skia.Rect.MakeLTRB(x0, top, x1, GY)
    c.drawRect(hall, shader_paint(lin_grad((0, top), (0, GY), [mix('#1a1412', '#ffe2a8', door), mix('#120e0c', '#f0b060', door)])))
    if door > 0:
        glow(c, (x0 + x1) / 2, -100, 520, '#ffc070', 0.45 * door)
    # the door leaf swings inward (narrowing parallelogram)
    open_w = (x1 - x0) * (1 - 0.82 * door)
    leaf = poly_path([(x0, top), (x0 + open_w, top - 30 * door), (x0 + open_w, GY + 30 * door), (x0, GY)])
    c.drawPath(leaf, shader_paint(lin_grad((x0, 0), (x0 + open_w + 1, 0), ['#6a3a22', '#4a2616'])))
    c.drawCircle(x0 + open_w - 26, -60, 9, paint('#d9a94a'))
    # radio cabinet under the photos
    c.drawRoundRect(skia.Rect.MakeLTRB(120, GY - 230, 400, GY - 20), 12, 12, paint('#3e2414'))
    c.drawRect(skia.Rect.MakeLTRB(140, GY - 210, 380, GY - 150), paint('#24160c'))
    for k in range(3):
        c.drawRect(skia.Rect.MakeXYWH(150 + k * 80, GY - 130, 60, 90), paint('#5c3a22', style='stroke', width=4))


def wall_clock(c, x, y, r, hours):
    c.drawCircle(x, y, r + 14, paint('#4a2a16'))
    c.drawCircle(x, y, r, shader_paint(rad_grad((x - r * 0.3, y - r * 0.3), r * 1.4, ['#fff6e2', '#d8c8a8'])))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        L = 0.16 if k % 3 == 0 else 0.08
        c.drawLine(x + math.sin(a) * r * (0.92 - L), y - math.cos(a) * r * (0.92 - L), x + math.sin(a) * r * 0.92,
                   y - math.cos(a) * r * 0.92, paint('#2a1a10', style='stroke', width=5 if k % 3 == 0 else 3))
    ha = (hours % 12) / 12 * 2 * math.pi
    ma = (hours % 1) * 2 * math.pi
    c.drawLine(x, y, x + math.sin(ha) * r * 0.5, y - math.cos(ha) * r * 0.5, paint('#1a0e08', style='stroke', width=9))
    c.drawLine(x, y, x + math.sin(ma) * r * 0.78, y - math.cos(ma) * r * 0.78, paint('#1a0e08', style='stroke', width=6))
    c.drawCircle(x, y, 9, paint('#8a5a2a'))
    # pendulum
    sw = math.sin(hours * 2 * math.pi * 40) * 0.25
    px, py = x + math.sin(sw) * r * 1.2, y + r + math.cos(sw) * r * 1.2
    c.drawLine(x, y + r, px, py, paint('#8a6a3a', style='stroke', width=4))
    c.drawCircle(px, py, 18, paint('#c99a3a'))


def room_floor(c, door=0.0):
    c.drawRect(skia.Rect.MakeLTRB(-1600, GY - 6, 1600, GY + 1000), shader_paint(lin_grad((0, GY), (0, GY + 700), ['#4a2c18', '#22140a'])))
    for k in range(-22, 23):
        c.drawLine(k * 120, GY, k * 280, GY + 1000, paint((0.12, 0.06, 0.03, 0.45), style='stroke', width=3))
    for k in range(5):
        c.drawOval(skia.Rect.MakeXYWH(-560 + k * 18, GY + 20 + k * 8, 1000 - k * 36, 200 - k * 16),
                   paint(mix(['#7a3a2a', '#a8803a', '#4a5a6a', '#7a3a2a', '#a8803a'][k], '#1a1420', 0.35)))
    if door > 0:     # trapezoid of hallway light across the floor
        x0, x1 = DOOR
        lp = poly_path([(x0 * 0.85, GY + 4), (x1 * 0.95, GY + 4), (x1 * 0.4 - 200, GY + 900), (x0 * 0.2 - 900, GY + 900)])
        c.drawPath(lp, paint((1.0, 0.78, 0.45, 0.28 * door), blur=30, blend=skia.BlendMode.kPlus))


def lamp(c, x=-1000, on=1.0):
    c.drawRect(skia.Rect.MakeLTRB(x - 6, -480, x + 7, GY + 330), paint('#24180f'))
    shade_ = poly_path([(x - 70, -520), (x + 70, -520), (x + 110, -380), (x - 110, -380)])
    c.drawPath(shade_, shader_paint(lin_grad((0, -520), (0, -380), [mix('#6a5a40', '#f7d79a', on), mix('#5a4a30', '#e0a050', on)])))
    if on > 0:
        glow(c, x, -420, 520, '#ffbf6a', 0.5 * on)


L_NIGHT = dict(key=(-0.8, -0.6), amb='#7a86b8', amb_a=0.38, rim='#ffcf8a', line='#24141a', floor_shadow=0.45)
L_JOE_BACKLIT = dict(key=(0.6, -0.8), amb='#3a2a34', amb_a=0.55, rim='#ffd598', line='#120a0c', floor_shadow=0.0)
L_WARM = dict(key=(-0.75, -0.65), amb='#ffd9a0', amb_a=0.26, rim='#ffcf8a', line='#3a1c12', floor_shadow=0.4)
