"""SCENE 2 - THE FIRST DREAM. Small club (shy start -> spotlight -> confidence) -> curtain transformation -> grand theater."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, smoothstep, noise1, font, text_center)
from world import Cam, cam_path, Layer, CHARS, particles, crowd
from character import outfits, BROTHERS
import choreo
import timing as T

DB = T.db
T0 = DB(4) - 0.45          # whip-pan lands at DB(4)
T_CURTAIN = DB(7)          # curtains close exactly on this downbeat, reopen in the grand theater
OUT = outfits('club')
GY = 420
POS = {'tito': (-330, -20, 0.95), 'jackie': (-170, -40, 0.96), 'michael': (0, 30, 1.0), 'marlon': (170, -40, 0.96),
       'jermaine': (335, -20, 0.95)}
BASE_H = 360


def sched():
    d = DB
    S = {}
    S['michael'] = [(0, 'shy', {}), (d(5), 'mic_sing', dict(amp=0.6)), (d(6), 'mic_sing', dict(amp=1.2)),
                    (d(6) + 4 * T.PERIOD - 0.12, 'spin', dict(start='auto', length=0.75)),
                    (T_CURTAIN + 0.3, 'point_hit', dict(start='auto', side=1)), (T_CURTAIN + 1.5, 'step_touch', {})]
    for k in ('jackie', 'marlon'):
        S[k] = [(0, 'groove', dict(amp=0.45, snap=True)), (d(5), 'groove', dict(amp=0.9)), (d(6), 'step_touch', {}),
                (T_CURTAIN + 0.3, 'point_hit', dict(start='auto', side=-1 if k == 'jackie' else 1)),
                (T_CURTAIN + 1.5, 'step_touch', {})]
    S['tito'] = [(0, 'play', dict(amp=0.6)), (d(5), 'play', {})]
    S['jermaine'] = [(0, 'play', dict(amp=0.6)), (d(5), 'play', dict(amp=1.2))]
    return S


SCHED = sched()
RIP = {'jackie': 0.04, 'marlon': 0.08, 'michael': 0.0, 'tito': 0.0, 'jermaine': 0.0}


def band(c, t, L, scale=1.0, gy=GY, spot=None):
    for k in sorted(POS, key=lambda k: POS[k][1]):
        x, dy, s = POS[k]
        P = choreo.perform(SCHED[k], t, k, seed=BROTHERS[k].seed, ripple=RIP[k], sing=1.0 if k == 'michael' else None,
                           base_kw=dict(instrument='guitar' if k == 'tito' else 'bass' if k == 'jermaine' else None))
        if k == 'michael' and t < DB(5):
            P['mopen'] = min(P['mopen'], 0.25)
        h = BASE_H * BROTHERS[k].height * s * scale
        LL = L
        if spot is not None and k != 'michael':
            LL = dict(L, amb='#5a2a40', amb_a=0.55 * spot)
        CHARS[k].draw(c, x * scale, gy + dy * scale, h, P, OUT[k], LL, t)
        if k == 'michael':
            _mic_stand(c, x * scale + 70 * scale, gy + dy * scale, h, P)


def _mic_stand(c, x, gy, h, P):
    if P.get('mic'):
        return
    top = gy - h * 0.62
    c.drawLine(x, gy, x, top, paint('#18141a', style='stroke', width=6))
    c.drawPath(poly_path([(x - 40, gy), (x + 40, gy), (x, gy - 22)]), paint('#18141a'))
    c.drawCircle(x, top - 12, 16, paint('#9a9aa6'))


LIGHT_CLUB = dict(key=(-0.3, -0.95), amb='#ff9a8a', amb_a=0.3, rim='#ffb0a0', line='#3a1018', floor_shadow=0.45)
LIGHT_THEATER = dict(key=(0.2, -0.98), amb='#ffd2a0', amb_a=0.22, rim='#ffe2a0', line='#3a1a14', floor_shadow=0.4)


# --------------------------------------------------------------------------- club set
def club_bg(c, t, beat):
    # intimate club: dark brick wall, hand-painted banner, small riser stage
    c.drawRect(skia.Rect.MakeLTRB(-1600, -1500, 1600, GY), paint('#3a1414'))
    for row in range(-30, 12):
        y = row * 46
        off = 60 if row % 2 else 0
        for k in range(-16, 17):
            x = k * 120 + off
            shade_k = (math.sin(k * 12.9898 + row * 78.233) * 43758.5453) % 1
            c.drawRoundRect(skia.Rect.MakeXYWH(x + 3, y + 3, 114, 40), 4, 4,
                            paint(mix('#6a2218', '#8a3424', shade_k * 0.8)))
    c.drawRect(skia.Rect.MakeLTRB(-1600, -1500, 1600, GY), shader_paint(rad_grad((0, -200), 1300,
               [(0, 0, 0, 0), (0.05, 0, 0.02, 0.75)])))
    # painted banner
    ban = skia.Rect.MakeLTRB(-430, -960, 430, -790)
    c.drawRect(ban, paint('#e9d6a8'))
    c.drawRect(ban, paint('#7a1e1a', style='stroke', width=10))
    text_center(c, 'AMATEUR NIGHT', 0, -850, font('spartan', 86), paint('#9a1c22'))
    text_center(c, 'TONIGHT  -  LOCAL TALENT', 0, -805, font('spartan_b', 30), paint('#3a1a14'), tracking=3)
    # small red side drapes
    for side in (-1, 1):
        x = side * 760
        cols = ['#5a0a16' if k % 2 else '#8e1a28' for k in range(6)]
        c.drawRect(skia.Rect.MakeLTRB(x - 150, -1300, x + 150, GY), shader_paint(lin_grad((x - 150, 0), (x + 150, 0), cols)))
    # string of bulbs (sway)
    for k in range(-14, 15):
        x = k * 70
        y = -880 + 40 * math.cos(k / 14 * math.pi / 2) ** 2 * -1 + 6 * math.sin(t * 2 + k)
        on = 0.55 + 0.45 * math.sin(beat * math.pi + k * 0.9) ** 2
        glow(c, x, y, 55, '#ffcf7a', 0.5 * on)
        c.drawCircle(x, y, 9, paint(mix('#ffcf7a', '#ffffff', 0.5 * on)))
    # stage platform
    c.drawRect(skia.Rect.MakeLTRB(-1000, GY - 10, 1000, GY + 150), shader_paint(lin_grad((0, GY), (0, GY + 150),
               ['#6a3a22', '#3a1e12'])))
    for k in range(-10, 11):
        c.drawLine(k * 100, GY, k * 120, GY + 150, paint((0.1, 0.05, 0.02, 0.5), style='stroke', width=2))
    c.drawRect(skia.Rect.MakeLTRB(-1000, GY + 140, 1000, GY + 190), paint('#2a120c'))
    for k in range(-9, 10):       # footlights
        x = k * 110
        glow(c, x, GY + 150, 70, '#ffb35a', 0.6)
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 26, GY + 142, 52, 22), 6, 6, paint('#1a0c08'))


def club_fg(c, t, energy, beat):
    # tables with candles + audience backs (foreground)
    c.drawRect(skia.Rect.MakeLTRB(-1600, 600, 1600, 1600), paint('#14060a'))
    for x in (-520, 40, 560):
        c.drawOval(skia.Rect.MakeXYWH(x - 170, 640, 340, 60), paint('#2a0e12'))
        glow(c, x, 640, 90, '#ffaa4a', 0.7)
        c.drawRect(skia.Rect.MakeXYWH(x - 8, 610, 16, 30), paint('#f0e0c0'))
    crowd(c, t, 2, energy, '#120408', '#ff8a6a', width=2600, seed=31, y0=760, row_gap=150, scale0=1.6,
          beat_phase=beat)


# --------------------------------------------------------------------------- grand theater set
def theater_bg(c, t, beat):
    c.drawRect(skia.Rect.MakeLTRB(-2400, -2400, 2400, GY), shader_paint(lin_grad((0, -2000), (0, GY), ['#1a0608', '#3a0c12', '#5a1418'])))
    # proscenium arch (gold) + deep stage curtain
    cols = ['#6a0c16' if k % 2 else '#9a1c28' for k in range(30)]
    c.drawRect(skia.Rect.MakeLTRB(-700, -1300, 700, GY), shader_paint(lin_grad((-700, 0), (700, 0), cols)))
    arch = skia.Path()
    arch.addRect(skia.Rect.MakeLTRB(-1700, -2000, 1700, GY + 200))
    inner = skia.Path()
    inner.moveTo(-640, GY + 200)
    inner.lineTo(-640, -760)
    inner.cubicTo(-640, -1160, 640, -1160, 640, -760)
    inner.lineTo(640, GY + 200)
    inner.close()
    frame = skia.Op(arch, inner, skia.PathOp.kDifference_PathOp)
    c.drawPath(frame, shader_paint(lin_grad((0, -1700), (0, GY), ['#8a5a1a', '#e2b24a', '#8a5a1a', '#c99a3a'])))
    for k in range(-9, 10):
        a = k / 9 * 1.25
        c.drawCircle(math.sin(a) * 700, -820 - math.cos(a) * 360, 14, paint('#fff0b0'))
    # gold pilasters
    for side in (-1, 1):
        c.drawRect(skia.Rect.MakeLTRB(side * 690 - 40, -760, side * 690 + 40, GY), shader_paint(lin_grad(
            (side * 690 - 40, 0), (side * 690 + 40, 0), ['#8a5a1a', '#f0c868', '#8a5a1a'])))
    # boxes / balconies on both sides
    for side in (-1, 1):
        for row in range(3):
            y = -1080 + row * 330
            x = side * 960
            c.drawRoundRect(skia.Rect.MakeXYWH(x - 200, y, 400, 160), 30, 30, paint('#3a0810'))
            glow(c, x, y + 60, 160, '#ffb060', 0.2)
            c.drawRect(skia.Rect.MakeXYWH(x - 210, y + 120, 420, 40), shader_paint(lin_grad((0, y + 120), (0, y + 160),
                       ['#f0c060', '#8a5a1a'])))
            for k in range(5):
                hx = x - 160 + k * 80
                c.drawCircle(hx, y + 100 - 6 * abs(math.sin(beat * math.pi + k)), 26, paint('#14060a'))
    # chandelier
    glow(c, 0, -1450, 360, '#ffe0a0', 0.5)
    c.drawLine(0, -2000, 0, -1480, paint('#c99a3a', style='stroke', width=4))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        c.drawCircle(math.cos(a) * 150, -1450 + math.sin(a) * 45, 11, paint('#fff4d0'))
        c.drawLine(0, -1500, math.cos(a) * 150, -1450 + math.sin(a) * 45, paint('#c99a3a', style='stroke', width=2))
    # stage floor
    c.drawRect(skia.Rect.MakeLTRB(-1400, GY - 10, 1400, GY + 260), shader_paint(lin_grad((0, GY), (0, GY + 260), ['#7a4a26', '#3a2010'])))
    for k in range(-14, 15):
        x = k * 100
        glow(c, x, GY + 240, 80, '#ffc070', 0.55)


def spotlight(c, x, gy, top_y, strength, w=230):
    beam(c, x - 300, top_y, x, gy - 120, 60, w, '#fff0d0', 0.55 * strength, blur=30)
    c.drawOval(skia.Rect.MakeXYWH(x - w * 1.1, gy - 40, w * 2.2, 90), paint((1, 0.92, 0.75, 0.35 * strength), blur=30))


def curtains(c, close, col_a='#8e1a28', col_b='#4e0812'):
    """foreground stage curtains sweeping in from both sides (close 0..1)"""
    for side in (-1, 1):
        edge = side * (W * 0.62 * (1 - close))
        x_out = side * W * 1.2
        r = skia.Rect.MakeLTRB(min(edge, x_out), -H, max(edge, x_out), H)
        cols = [col_b if k % 2 else col_a for k in range(16)]
        c.drawRect(r, shader_paint(lin_grad((r.left(), 0), (r.right(), 0), cols)))
        c.drawRect(skia.Rect.MakeLTRB(edge - 30, -H, edge + 30, H) if side > 0 else skia.Rect.MakeLTRB(edge - 30, -H, edge + 30, H),
                   paint((0, 0, 0, 0.35), blur=25))


def draw(c, t):
    beat = T.beat_at(t)
    if t < T_CURTAIN + 0.02:
        club(c, t, beat)
    else:
        theater(c, t, beat)
    # curtain transition (screen space): sweep closed on the downbeat, reopen onto the grand theater
    close = smoothstep(T_CURTAIN - 0.55, T_CURTAIN, t) if t < T_CURTAIN else 1 - ease_out((t - T_CURTAIN) / 0.75, 2.2)
    if close > 0.001:
        c.save()
        c.translate(W / 2, H / 2)
        curtains(c, close)
        c.restore()


def club(c, t, beat):
    spot = smoothstep(DB(5) - 0.08, DB(5) + 0.06, t)
    energy = 0.15 + 0.85 * smoothstep(DB(6) - 0.5, DB(6) + 1.0, t)
    keys = [(T0, Cam(0, 120, 1.4), None), (DB(5), Cam(30, 60, 1.65), ease_io),
            (DB(6), Cam(-10, 140, 1.45), lambda u: ease_out(u, 3)), (T_CURTAIN, Cam(0, 110, 1.3), ease_io)]
    cam = cam_path(keys, t)
    if DB(5) <= t < DB(5) + 0.3:
        cam.shake = 0.5 * (1 - (t - DB(5)) / 0.3)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14040a'))
    dark = 1 - 0.45 * spot
    L = dict(LIGHT_CLUB)
    with Layer(c, cam, 0.7, t):
        club_bg(c, t, beat)
        c.drawRect(skia.Rect.MakeLTRB(-2000, -2000, 2000, 2000), paint((0.05, 0.0, 0.03, 0.45 * spot)))
    with Layer(c, cam, 1.0, t):
        if spot > 0:
            spotlight(c, 0, GY + 30, -1400, spot)
        band(c, t, L, spot=spot)
    with Layer(c, cam, 1.5, t):
        club_fg(c, t, energy, beat)


def theater(c, t, beat):
    u = (t - T_CURTAIN) / (DB(8) - T_CURTAIN)
    cam = cam_path([(T_CURTAIN, Cam(0, 80, 1.35), None), (DB(8), Cam(0, -330, 0.6), lambda v: ease_out(v, 2.2))], t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14040a'))
    with Layer(c, cam, 0.85, t):
        theater_bg(c, t, beat)
    with Layer(c, cam, 1.0, t):
        for x in (-300, 300):
            beam(c, x * 3, -2200, x * 0.3, GY - 100, 50, 260, '#fff2d0', 0.4, blur=40)
        band(c, t, LIGHT_THEATER)
        particles(c, t, 40, (-900, -1400, 900, 300), 77, '#ffe6a0', size=(1.5, 3), speed=(5, 15))
    with Layer(c, cam, 1.45, t):
        crowd(c, t, 4, 0.9, '#100306', '#ffb070', width=3600, seed=52, y0=620, row_gap=110, scale0=1.1,
              beat_phase=beat, lighters=False)
