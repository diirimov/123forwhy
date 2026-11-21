"""V3 0:48-1:09  ONE LAST TOUR -> DODGER STADIUM, DEC 9 1984 -> THE ANNOUNCEMENT -> THE FINAL DECISION."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, font, text_center, noise1, ellipse_path)
from world import Cam, cam_path, Layer, CHARS, particles, silhouette, crowd, light_rig
from character import (outfits84, LINEUP84, DESIGNS, JOE84_OUTFIT, base_pose, outfits)
import choreo
import timing as T
from v3_common import cap, pose, draw_char, place_head
from v2_common import room_wall, room_floor, lamp, GY as ROOM_GY, wall_clock, L_NIGHT

DB = T.db
BEAT = T.PERIOD
T_BACK = DB(19)        # 48.45 backstage
T_FOLLOW = DB(20)      # 50.89 Michael follows them toward the stage
T_STADIUM = DB(21)     # 53.34 Dodger Stadium
T_FINISH = DB(22)      # 55.78 the last song ends, the stadium roars
T_SPEAK = DB(23)       # 58.22 the announcement
T_REACT = DB(24)       # 60.65 brothers' reactions
T_JOE = DB(24) + 2 * BEAT
T_EXIT = DB(25)        # 63.09 he lowers the mic and walks off
T_SHOE = DB(25) + 2 * BEAT
T_CHILDSHOE = T_SHOE + BEAT
T_ROOM = DB(26)        # 65.53 the empty rehearsal room
T_FINAL = DB(26) + 2 * BEAT
START = T_BACK
O84 = outfits84()
SGY = 330
# stage positions for the six-brother line-up, Michael centre-front
POS84 = {'jackie84': (-560, -30), 'tito84': (-340, -50), 'jermaine84': (-130, -20), 'michael84': (90, 40),
         'marlon84': (320, -40), 'randy84': (540, -20)}
BASE = 360
L_STAGE = dict(key=(-0.25, -0.97), amb='#e8e0ff', amb_a=0.18, rim='#9fd8ff', line='#1a1024', floor_shadow=0.5)
L_BACK = dict(key=(0.8, -0.6), amb='#7a8aa8', amb_a=0.42, rim='#cfe6ff', line='#141018', floor_shadow=0.45)


def H84(k):
    return BASE * DESIGNS[k].height


# --------------------------------------------------------------------------- backstage corridor
def corridor(c, t, vp=(W / 2, H * 0.42), glow_end=1.0):
    vx, vy = vp
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14121a'))
    # far opening: the stage light
    ow, oh = 230, 340
    opening = skia.Rect.MakeXYWH(vx - ow / 2, vy - oh * 0.6, ow, oh)
    c.drawRect(opening, shader_paint(lin_grad((0, opening.top()), (0, opening.bottom()), ['#ffffff', '#cfe0ff', '#8aa8ff'])))
    glow(c, vx, vy, 700, '#cfe0ff', 0.55 * glow_end)
    # walls / ceiling / floor as perspective trapezoids
    def quad(pts, cols):
        c.drawPath(poly_path(pts), shader_paint(lin_grad(pts[0], pts[2], cols)))
    L_, R_, T_, B_ = opening.left(), opening.right(), opening.top(), opening.bottom()
    quad([(0, 0), (L_, T_), (L_, B_), (0, H)], ['#2a2a34', '#4a4a58'])                   # left wall
    quad([(W, 0), (R_, T_), (R_, B_), (W, H)], ['#24242e', '#44445a'])                   # right wall
    quad([(0, 0), (W, 0), (R_, T_), (L_, T_)], ['#101016', '#2a2a36'])                   # ceiling
    quad([(0, H), (W, H), (R_, B_), (L_, B_)], ['#1a1a20', '#3a3a48'])                   # floor
    # floor sheen toward the light
    c.drawPath(poly_path([(vx - 60, B_), (vx + 60, B_), (vx + 360, H), (vx - 360, H)]), paint((0.75, 0.82, 1.0, 0.16), blur=20))
    # caged ceiling bulbs receding
    for k in range(6):
        z = 1 / (1 + k * 0.75)
        x = vx + (0 - vx) * z * 0.0
        y = vy + (60 - vy) * z
        glow(c, vx, y, 140 * z, '#ffe8b0', 0.5)
        c.drawCircle(vx, y, 12 * z, paint('#fff6d8'))
    # cable bundles along the floor edges + wall stripes
    for side in (-1, 1):
        x0 = 0 if side < 0 else W
        xe = L_ if side < 0 else R_
        c.drawLine(x0 + side * -40, H - 30, xe, B_ - 4, paint('#0c0c10', style='stroke', width=14))
        c.drawLine(x0 + side * -10, H * 0.62, xe, vy + 20, paint((0.9, 0.8, 0.2, 0.5), style='stroke', width=8))
    # road cases (stencilled) near camera, left
    for i, (x, y, w, h, lab) in enumerate([(40, 1380, 330, 300, 'THE JACKSONS'), (60, 1180, 250, 210, 'VICTORY TOUR 84')]):
        c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), 10, 10, paint('#1a1a20'))
        c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), 10, 10, paint('#5a5a66', style='stroke', width=6))
        for cx_ in (x + 12, x + w - 12):
            c.drawRect(skia.Rect.MakeXYWH(cx_ - 8, y, 16, h), paint('#3a3a44'))
        text_center(c, lab, x + w / 2, y + h / 2 + 10, font('bebas', 44 if i == 0 else 34), paint((0.92, 0.92, 0.95, 0.85)))
    return opening


def persp(vp, base_y, z):
    """screen position/scale for something standing at depth z (1 = near the camera, 0 = at the far opening)"""
    vx, vy = vp
    return vx, vy + (base_y - vy) * z, z


def backstage(c, t):
    u = clamp((t - T_BACK) / (T_FOLLOW - T_BACK))
    vp = (W / 2 + 30 * u, H * 0.42)
    c.save()
    s = 1.0 + 0.05 * ease_io(u)
    c.translate(W / 2, H / 2)
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    corridor(c, t, vp)
    # five brothers walk away from us toward the light (back view), staggered
    order = ['jackie84', 'tito84', 'jermaine84', 'marlon84', 'randy84']
    figs = []
    for i, k in enumerate(order):
        prog = clamp((t - T_BACK + 1.6 - i * 0.42) / 3.4)      # 0 near .. 1 far
        z = 0.82 - 0.62 * ease_in(prog, 1.1)
        lane = [-0.5, 0.9, -0.2, 0.55, -0.85][i] * 210 * z
        figs.append((z, k, lane, prog))
    figs.sort(key=lambda f: f[0])
    for z, k, lane, prog in figs:
        x, y, sc = persp(vp, H * 1.12, z)
        P = pose(k, [(0, 'walk_away', dict(start=0.0, speed=0.0))], t)
        draw_char(c, k, x + lane, y, H84(k) * 2.4 * sc, P, O84[k], L_BACK, t, shadow=False)
    # Joe (1984) by the wall, observing the preparations
    P = pose('joe84', [(0, 'arms_folded', dict(stern=0.8, look=0.5))], t)
    draw_char(c, 'joe84', W * 0.8, H * 0.86, 840, P, JOE84_OUTFIT, L_BACK, t, shadow=False)
    # Michael in the foreground, alone, watching his brothers go
    P = pose('michael84', [(0, 'stare', dict(sad=0.3))], t)
    P.update(hyaw=0.35, ex=0.75, ey=-0.1, brow=0.35, smile=0.05, blink=0.2)
    draw_char(c, 'michael84', W * 0.24, H * 1.38, 1750, P, O84['michael84'], dict(L_BACK, rim='#e6f0ff'), t, shadow=False)
    c.restore()
    cap(c, t, T_BACK + 0.2, T_FOLLOW - 0.05, ['BUT IN 1984…'], y=300, size=86)


def follow(c, t):
    """behind Michael as he walks after them into the light"""
    u = clamp((t - T_FOLLOW) / (T_STADIUM - T_FOLLOW))
    vp = (W / 2, H * 0.42)
    c.save()
    s = 1.0 + 0.35 * ease_in(u, 1.5)
    c.translate(W / 2, H * 0.42)
    c.scale(s, s)
    c.translate(-W / 2, -H * 0.42)
    corridor(c, t, vp, glow_end=1 + u)
    z = 0.92 - 0.25 * u
    x, y, sc = persp(vp, H * 1.12, z)
    P = pose('michael84', [(0, 'walk_away', dict(start=0.0, speed=0.0))], t)
    draw_char(c, 'michael84', x + 20, y, H84('michael84') * 2.6 * sc, P, O84['michael84'], L_BACK, t, shadow=False)
    c.restore()
    if u > 0.75:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0.9, 0.94, 1.0, ease_in((u - 0.75) / 0.25, 2))))
    cap(c, t, T_FOLLOW + 0.15, T_STADIUM - 0.1, ['HE RETURNED FOR', 'ONE MORE TOUR.'], y=300, size=86)


# --------------------------------------------------------------------------- Dodger Stadium, 1984
_PIC = {}


def _tier_picture(key, rx, ry_top, ry_bot, n, seed, cols, dot=(5, 9)):
    if key in _PIC:
        return _PIC[key]
    rng = np.random.default_rng(seed)
    rec = skia.PictureRecorder()
    cc = rec.beginRecording(skia.Rect.MakeLTRB(-rx - 50, -ry_bot - 50, rx + 50, ry_bot + 50))
    for i in range(n):
        a = rng.uniform(math.pi * 1.02, math.pi * 1.98)
        rr = rng.uniform(0, 1)
        ry = ry_top + (ry_bot - ry_top) * rr
        rxx = rx * (ry / ry_bot)
        x, y = math.cos(a) * rxx, math.sin(a) * ry
        d = rng.uniform(*dot) * (0.7 + 0.5 * rr)
        cc.drawCircle(x, y, d, paint(cols[i % len(cols)]))
    pic = rec.finishRecordingAsPicture()
    _PIC[key] = pic
    return pic


def stadium_bg(c, t, beat, flash=1.0):
    # night sky, hills, palms
    c.drawRect(skia.Rect.MakeLTRB(-4000, -4000, 4000, 4000), shader_paint(lin_grad((0, -2400), (0, 200),
               ['#05061a', '#14143a', '#3a2450'])))
    rng = np.random.default_rng(84)
    for i in range(80):
        c.drawCircle(rng.uniform(-3000, 3000), rng.uniform(-2600, -1400), rng.uniform(1, 2.5), paint((1, 1, 1, 0.6)))
    hills = smooth_path([(-3200, -700), (-2200, -1050), (-1300, -880), (-400, -1120), (600, -900), (1500, -1080), (2400, -860),
                         (3200, -980), (3200, -500), (-3200, -500)], True, 0.4)
    c.drawPath(hills, paint('#120e22'))
    for i in range(140):         # city lights on the hills
        x = rng.uniform(-3000, 3000)
        c.drawCircle(x, rng.uniform(-860, -620), 2.5, paint((1, 0.85, 0.5, 0.7)))
    for x in (-2500, -2300, -1900, 2000, 2350, 2600):
        c.drawLine(x, -620, x + 20, -1050, paint('#0a0814', style='stroke', width=14))
        for k in range(7):
            a = k / 7 * math.pi * 2
            c.drawLine(x + 20, -1050, x + 20 + math.cos(a) * 110, -1050 + math.sin(a) * 50 + 30, paint('#0a0814', style='stroke', width=10))
    # stadium bowl: four tiers, thousands of fans (cached pictures), wavy pavilion roofs, light standards
    tiers = [('t4', 2700, 980, 1180, 2600, ['#3a3458', '#4a3a5a', '#2e2a4a', '#5a4a6a']),
             ('t3', 2500, 760, 960, 2400, ['#4a3a62', '#5a4870', '#3a3456', '#6a5478']),
             ('t2', 2300, 560, 740, 2200, ['#5a4a72', '#6a5a80', '#4a4064', '#7a6488']),
             ('t1', 2100, 360, 540, 2000, ['#6a5a84', '#7a6a90', '#5a5078', '#8a76a0'])]
    for i, (key, rx, r0, r1, n, cols) in enumerate(tiers):
        band = skia.Path()
        band.addOval(skia.Rect.MakeLTRB(-rx, -r1, rx, r1))
        inner = skia.Path()
        inner.addOval(skia.Rect.MakeLTRB(-rx * r0 / r1, -r0, rx * r0 / r1, r0))
        ring = skia.Op(band, inner, skia.PathOp.kDifference_PathOp)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-4000, -4000, 4000, -40))
        c.drawPath(ring, paint(['#1a1630', '#201a38', '#262040', '#2c2448'][i]))
        c.drawPicture(_tier_picture(key, rx, r0 + 10, r1 - 10, n, 900 + i, cols))
        c.drawOval(skia.Rect.MakeLTRB(-rx, -r1, rx, r1), paint('#d8d0e8', style='stroke', width=6))
        c.restore()
    # camera flashes twinkling across the stands
    for i in range(70):
        if (i * 7919 + int(t * 12)) % 23 == 0:
            a = math.pi * (1.05 + 0.9 * ((i * 0.618) % 1))
            r = 400 + (i * 37) % 700
            glow(c, math.cos(a) * r * 2.2, math.sin(a) * r, 50, '#ffffff', 0.9 * flash)
    # wavy outfield pavilion roofs (Dodger Stadium signature)
    for side in (-1, 1):
        pts = []
        for k in range(13):
            x = side * (1900 + k * 70)
            pts.append((x, -1230 - (40 if k % 2 else 0)))
        c.drawPath(poly_path(pts + [(pts[-1][0], -1150), (pts[0][0], -1150)]), paint('#d8d4e0'))
    # light standards on the rim
    for x in (-2400, -1400, 1400, 2400):
        c.drawRect(skia.Rect.MakeXYWH(x - 8, -1500, 16, 300), paint('#1a1828'))
        c.drawRect(skia.Rect.MakeXYWH(x - 90, -1560, 180, 70), paint('#2a2838'))
        glow(c, x, -1525, 260, '#f4f0ff', 0.55)
        for k in range(6):
            c.drawCircle(x - 70 + k * 28, -1525, 10, paint('#ffffff'))


def stage84(c, t, beat, kick=0.0):
    """Victory Tour-scale stage: deck, risers, two lighting towers, an arched overhead truss"""
    # towers
    for side in (-1, 1):
        x = side * 980
        c.drawRect(skia.Rect.MakeXYWH(x - 90, -1350, 180, 1700), paint('#16141e'))
        for k in range(17):
            y = -1340 + k * 100
            c.drawLine(x - 90, y, x + 90, y + 100, paint('#2e2a3a', style='stroke', width=5))
            c.drawLine(x + 90, y, x - 90, y + 100, paint('#2e2a3a', style='stroke', width=5))
        for k in range(8):
            y = -1250 + k * 140
            on = 0.5 + 0.5 * abs(math.sin(beat * math.pi / 2 + k * 0.6 + side))
            col = ['#ff3a6a', '#3ac8ff', '#ffd24a', '#b05aff'][k % 4]
            glow(c, x - side * 100, y, 90, col, 0.45 * on)
            c.drawCircle(x - side * 100, y, 16, paint(mix(col, '#ffffff', 0.5)))
    # arched truss
    arch = skia.Path()
    arch.moveTo(-980, -1250)
    arch.cubicTo(-700, -1650, 700, -1650, 980, -1250)
    c.drawPath(arch, paint('#1c1a26', style='stroke', width=70))
    c.drawPath(arch, paint('#3a3648', style='stroke', width=8))
    for k in range(15):
        u = k / 14
        x = -980 + 1960 * u
        y = -1250 - 400 * math.sin(math.pi * u) * 0.75
        col = ['#ffffff', '#9fd8ff', '#ffd8a0'][k % 3]
        glow(c, x, y + 30, 70, col, 0.6)
        c.drawCircle(x, y + 30, 13, paint('#ffffff'))
    # backdrop: dark, with a starburst of bulbs
    c.drawRect(skia.Rect.MakeLTRB(-880, -1150, 880, SGY - 120), shader_paint(lin_grad((0, -1150), (0, SGY), ['#0c0a18', '#1c1630'])))
    for k in range(40):
        a = k / 40 * 2 * math.pi
        for j in range(5):
            r = 120 + j * 110
            on = (k + j + int(beat * 2)) % 6 == 0
            c.drawCircle(math.cos(a) * r, -520 + math.sin(a) * r * 0.75, 6 if on else 4,
                         paint((1, 0.9, 0.7, 0.95 if on else 0.35)))
    # risers (drums / keys) and deck
    c.drawRect(skia.Rect.MakeLTRB(-760, SGY - 160, 760, SGY - 60), paint('#1e1a2c'))
    c.drawRect(skia.Rect.MakeLTRB(-1100, SGY - 60, 1100, SGY + 260), shader_paint(lin_grad((0, SGY - 60), (0, SGY + 260),
               ['#2a2438', '#0c0a12'])))
    c.drawRect(skia.Rect.MakeLTRB(-1100, SGY + 230, 1100, SGY + 260), paint('#c8c0e0'))
    for k in range(-10, 11):
        glow(c, k * 105, SGY + 240, 50, '#f0e8ff', 0.4)


def stadium_beams(c, t, beat, a=1.0):
    for i in range(8):
        bx = -900 + i * 260
        sweep = math.sin(t * 0.8 + i * 0.9) * 600
        col = ['#ffffff', '#9fd8ff', '#ffd8a0', '#d0a0ff'][i % 4]
        beam(c, bx, -1500, bx * 0.4 + sweep, SGY + 900, 25, 260, col, 0.22 * a, blur=40)


def lineup(c, t, sched_fn, L, keys=None):
    for k in sorted(POS84, key=lambda k: POS84[k][1]):
        if keys and k not in keys:
            continue
        x, dy = POS84[k]
        P = pose(k, sched_fn(k), t, ripple={'jackie84': 0.03, 'tito84': 0.05, 'marlon84': 0.04, 'randy84': 0.07}.get(k, 0.0),
                 sing=1.0 if k == 'michael84' else None)
        draw_char(c, k, x, SGY + dy, H84(k), P, O84[k], L, t)
        if k == 'michael84' and not P.get('mic'):
            mx = x + 75
            c.drawLine(mx, SGY + dy, mx, SGY + dy - H84(k) * 0.6, paint('#101014', style='stroke', width=6))
            c.drawCircle(mx, SGY + dy - H84(k) * 0.62, 14, paint('#9a9aa6'))


def sched_show(k):
    side = -1 if k in ('jackie84', 'tito84', 'jermaine84') else 1
    if k == 'michael84':
        return [(0, 'moonwalk', dict(start='auto', dirn=-1, speed=0.0)), (T_STADIUM + 2 * BEAT, 'spin', dict(start='auto')),
                (T_STADIUM + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=1)),
                (T_FINISH - 0.05, 'hat_pose', dict(start='auto')),
                (T_FINISH + 1.4, 'mic_speak', dict(look=-0.7))]
    return [(0, 'step_touch', {}), (T_STADIUM + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=side)),
            (T_FINISH - 0.05, 'cheer', {}), (T_FINISH + 1.5, 'nod_slow', dict(look=0.6 * (1 if side < 0 else -1)))]


def stadium_wide(c, t):
    beat = T.beat_at(t)
    u = clamp((t - T_STADIUM) / (T_FINISH - T_STADIUM))
    cam = Cam(0, -380 + 180 * ease_io(u), 0.34 + 0.12 * ease_io(u), -2 + 2 * u)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#05061a'))
    with Layer(c, cam, 0.35, t):
        stadium_bg(c, t, beat)
    with Layer(c, cam, 1.0, t):
        stage84(c, t, beat)
        stadium_beams(c, t, beat)
        lineup(c, t, sched_show, L_STAGE)
    with Layer(c, cam, 1.25, t):
        crowd(c, t, 7, 1.0, '#08061a', '#b89aff', width=6400, seed=1984, y0=700, row_gap=120, scale0=1.0,
              beat_phase=beat, lighters=False)
    fl = 1 - smoothstep(T_STADIUM, T_STADIUM + 0.4, t)
    if fl > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0.9, 0.94, 1.0, fl)))
    cap(c, t, T_STADIUM + 0.35, T_FINISH + 0.1, ['LOS ANGELES', 'DECEMBER 9, 1984'], y=300, size=80)


def finish(c, t):
    """the last song ends: the roar; the camera drifts in toward Michael at the microphone"""
    beat = T.beat_at(t)
    u = clamp((t - T_FINISH) / (T_SPEAK - T_FINISH))
    cam = Cam(70 * ease_io(u), -120 + 120 * ease_io(u), 0.62 + 0.5 * ease_io(u), 0)
    if t - T_FINISH < 0.3:
        cam.shake = 0.6
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#05061a'))
    with Layer(c, cam, 0.35, t):
        stadium_bg(c, t, beat)
    with Layer(c, cam, 1.0, t):
        stage84(c, t, beat)
        stadium_beams(c, t, beat, 1.0 - 0.5 * u)
        lineup(c, t, sched_show, L_STAGE)
    with Layer(c, cam, 1.3, t):
        crowd(c, t, 6, 1.0, '#08061a', '#b89aff', width=6400, seed=1985, y0=760, row_gap=120, scale0=1.0,
              beat_phase=beat, lighters=True)


def speak(c, t):
    """stillness. Michael at the microphone, looks to his brothers, then out to the crowd, and says it."""
    beat = T.beat_at(t)
    u = clamp((t - T_SPEAK) / (T_REACT - T_SPEAK))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.3), H, ['#2a2450', '#0e0c22', '#05061a'])))
    rng = np.random.default_rng(7)
    for i in range(90):        # out-of-focus stadium lights & lighters behind him
        x, y = rng.uniform(-100, W + 100), rng.uniform(H * 0.1, H * 0.75)
        glow(c, x, y, rng.uniform(20, 70), ['#ffd8a0', '#9fd8ff', '#ffffff'][i % 3], 0.18 + 0.12 * math.sin(t * 2 + i))
    beam(c, W / 2 - 200, -200, W / 2, H * 0.7, 60, 520, '#f4f0ff', 0.35, blur=50)
    look = -0.8 * (1 - smoothstep(0.05, 0.3, u))          # to his brothers ... then out to the audience
    P = pose('michael84', [(0, 'mic_speak', dict(look=look))], t)
    talk = smoothstep(0.32, 0.38, u) * (1 - smoothstep(0.9, 0.97, u))
    P['mopen'] = talk * (0.15 + 0.3 * abs(math.sin(t * 10.5)) * (0.6 + 0.4 * math.sin(t * 3.1)))
    P['mshape'] = 'ah'
    P['brow'] = 0.35 + 0.2 * talk
    P['smile'] = 0.15
    P['blink'] = 0.0 if 0.2 < u < 0.8 else P['blink']
    h = 2800 * (1 + 0.12 * ease_io(u))
    gx, gy = place_head('michael84', P, h, (W / 2 + 10, H * 0.4))
    draw_char(c, 'michael84', gx, gy, h, P, O84['michael84'], dict(L_STAGE, rim='#cfe6ff', amb_a=0.12), t, shadow=False)
    cap(c, t, T_SPEAK + 0.85, T_REACT + 2.2, ['THIS WILL BE OUR', 'LAST TOUR TOGETHER.'], y=1440, size=86)


def react(c, t):
    """restrained reactions: Jermaine looks down, Marlon nods, Jackie's hand to his chest, Tito and Randy watch Michael"""
    beat = T.beat_at(t)
    u = clamp((t - T_REACT) / (T_JOE - T_REACT))
    cam = Cam(-230 + 60 * u, 80, 1.55, 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#05061a'))
    with Layer(c, cam, 0.35, t):
        stadium_bg(c, t, beat, flash=0.4)
    with Layer(c, cam, 1.0, t):
        stage84(c, t, beat)
        sch = {'jackie84': [(0, 'hand_chest', dict(look=0.8))], 'tito84': [(0, 'nod_slow', dict(look=0.8))],
               'jermaine84': [(0, 'look_down', {})], 'marlon84': [(0, 'nod_slow', dict(look=-0.8))],
               'randy84': [(0, 'stare', dict(sad=0.3))], 'michael84': [(0, 'mic_speak', dict(look=0.0))]}
        def s(k):
            return sch[k]
        lineup(c, t, s, dict(L_STAGE, amb_a=0.25))
    cap(c, t, T_SPEAK + 0.85, T_REACT + 2.2, ['THIS WILL BE OUR', 'LAST TOUR TOGETHER.'], y=1440, size=86)


def joe_watch(c, t):
    """Joe, near the side of the stage, watching - his face hard to read"""
    u = clamp((t - T_JOE) / (T_EXIT - T_JOE))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (W, 0), ['#05050c', '#10102a', '#3a3a6a'])))
    # spill from the stage on the right, scaffold edge
    beam(c, W + 200, H * 0.2, W * 0.2, H * 0.5, 120, 500, '#cfe0ff', 0.25, blur=50)
    c.drawRect(skia.Rect.MakeXYWH(W * 0.82, 0, 70, H), paint('#14121c'))
    for k in range(20):
        c.drawLine(W * 0.82, k * 100, W * 0.82 + 70, k * 100 + 100, paint('#2a2838', style='stroke', width=5))
    P = pose('joe84', [(0, 'arms_folded', dict(stern=0.55, look=0.75))], t)
    P['hyaw'] = 0.35
    P['blink'] = 0.25 + (0.6 if 0.62 < u < 0.7 else 0.0)
    P['smile'] = -0.25
    h = 2200 * (1 + 0.06 * u)
    gx, gy = place_head('joe84', P, h, (W * 0.44, H * 0.38))
    draw_char(c, 'joe84', gx, gy, h, P, JOE84_OUTFIT, dict(L_BACK, key=(0.9, -0.4), rim='#cfe0ff', amb_a=0.5), t, shadow=False)


def exit_(c, t):
    """he lowers the microphone, takes one last look at his brothers, and walks into the dark wing"""
    beat = T.beat_at(t)
    u = clamp((t - T_EXIT) / (T_SHOE - T_EXIT))
    cam = Cam(160 + 160 * u, 60, 1.25, 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#05061a'))
    with Layer(c, cam, 0.35, t):
        stadium_bg(c, t, beat, flash=0.3)
    with Layer(c, cam, 1.0, t):
        stage84(c, t, beat)
        def s(k):
            if k == 'michael84':
                return [(0, 'lower_mic', dict(start=T.beat_at(T_EXIT) - T.PHASE, look=-0.8)),
                        (T_EXIT + 0.75, 'walk_away', dict(start='auto', speed=0.22))]
            return [(0, 'stare', dict(sad=0.2))]
        lineup(c, t, s, dict(L_STAGE, amb_a=0.25))
        # the dark wing he walks into
        c.drawRect(skia.Rect.MakeLTRB(900, -1600, 2400, 1400), shader_paint(lin_grad((900, 0), (1300, 0), [(0, 0, 0, 0), (0.01, 0.01, 0.03, 0.95)])))


def shoe(c, t, adult=True):
    """close-up of a stepping shoe; adult loafer + white sock in the dark corridor / the child's shoe on the rehearsal floor"""
    tt = t - (T_SHOE if adult else T_CHILDSHOE)
    step = ease_io(clamp(tt / 0.45))
    if adult:
        c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#0a0a10', '#1a1a24'])))
        c.drawRect(skia.Rect.MakeLTRB(0, H * 0.72, W, H), shader_paint(lin_grad((0, H * 0.72), (0, H), ['#2a2a34', '#121218'])))
        glow(c, W * 0.15, H * 0.5, 600, '#cfe0ff', 0.2)
    else:
        c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#2a1a12', '#4a2c18'])))
        for k in range(-12, 13):
            c.drawLine(W / 2 + k * 90, H * 0.6, W / 2 + k * 400, H + 200, paint((0.12, 0.06, 0.03, 0.5), style='stroke', width=5))
        c.drawRect(skia.Rect.MakeLTRB(0, 0, W, H * 0.6), shader_paint(lin_grad((0, 0), (0, H * 0.6), ['#3a2618', '#5a3a22'])))
        glow(c, W * 0.5, H * 0.75, 700, '#ffb060', 0.3)
    # the stepping foot (same screen position in both shots -> graphic match)
    fx = W * 0.62 - 420 * (1 - step)
    fy = H * 0.86 - 120 * math.sin(math.pi * step)
    ang = -10 * math.sin(math.pi * step)
    c.save()
    c.translate(fx, fy)
    c.rotate(ang)
    s = 1.0 if adult else 0.78
    c.scale(s, s)
    if adult:
        c.drawPath(limb_like([(-60, -520), (-40, -160)], 170), paint('#16141c'))            # trouser leg, short hem
        c.drawRect(skia.Rect.MakeXYWH(-110, -175, 150, 120), paint('#f4f4f8'))               # white sock
        for k in range(6):
            c.drawCircle(-90 + k * 25, -400 + (k * 53) % 200, 4, paint((1, 1, 1, 0.8)))       # sequins
        sh = smooth_path([(-130, -70), (60, -80), (250, -40), (280, 10), (-140, 20)], True, 0.5)
        c.drawPath(sh, shader_paint(lin_grad((0, -80), (0, 20), ['#3a3a44', '#08080c'])))
        c.drawArc(skia.Rect.MakeXYWH(40, -78, 190, 60), 200, 100, False, paint((1, 1, 1, 0.55), style='stroke', width=6))
    else:
        c.drawPath(limb_like([(-60, -560), (-40, -120)], 260), paint('#4a3a44'))           # little bell-bottom
        sh = smooth_path([(-120, -60), (40, -70), (210, -30), (230, 10), (-130, 20)], True, 0.5)
        c.drawPath(sh, shader_paint(lin_grad((0, -70), (0, 20), ['#7a4a2a', '#3a2010'])))
        c.drawLine(-40, -50, 120, -45, paint((0.9, 0.8, 0.6, 0.6), style='stroke', width=4))
    c.restore()
    c.drawOval(skia.Rect.MakeXYWH(fx - 220, H * 0.86 + 10, 520, 50), paint((0, 0, 0, 0.45), blur=18))


def limb_like(pts, w):
    from gfx import limb_outline
    return limb_outline(pts, [w * 0.8, w])


def empty_room(c, t):
    """the rehearsal room, empty now; the practice lamp slowly dims"""
    u = clamp((t - T_ROOM) / (T_FINAL - T_ROOM))
    cam = Cam(-20, 300, 1.55 - 0.15 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c0a10'))
    dim = 1 - 0.75 * ease_in(u, 1.4)
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=0.0, night=1.0, clock_t=23.2)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 0)
        glow(c, -20, ROOM_GY - 160, 560, '#ffcf8a', 0.5 * dim)
        c.drawOval(skia.Rect.MakeXYWH(-360, ROOM_GY - 10, 720, 140), paint((1, 0.8, 0.5, 0.25 * dim), blur=30))
    with Layer(c, cam, 1.4, t):
        lamp(c, -760, on=dim)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, 0.35 * (1 - dim))))


def final(c, t):
    """adult Michael, alone under one brilliant spotlight - the answer to the frightened boy in the first shot"""
    u = clamp((t - T_FINAL) / (T.DURATION - T_FINAL))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#030308'))
    on = ease_out(clamp(u / 0.18), 2)
    beam(c, W / 2, -300, W / 2, H * 0.82, 50, 380, '#fff8e8', 0.55 * on, blur=40)
    c.drawOval(skia.Rect.MakeXYWH(W / 2 - 360, H * 0.79, 720, 120), paint((1, 0.96, 0.85, 0.45 * on), blur=30))
    particles(c, t, 60, (W / 2 - 300, 0, W / 2 + 300, H * 0.8), 5, '#fff4d8', size=(1.2, 3), speed=(5, 14))
    P = pose('michael84', [(0, 'stare', dict(sad=0.0))], t)
    P.update(smile=0.25 * smoothstep(0.35, 0.7, u), brow=0.15, blink=0.0, ey=-0.25, lsh=0.12, lel=0.15, rsh=0.12, rel=0.15)
    h = 1250 * (1 + 0.08 * ease_io(u))
    draw_char(c, 'michael84', W / 2, H * 0.84, h, P, O84['michael84'],
              dict(key=(0.0, -1.0), amb='#fff2dc', amb_a=0.2, rim='#ffffff', line='#1a1018', floor_shadow=0.6), t)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.55), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.55)])))


def draw(c, t):
    if t < T_FOLLOW:
        backstage(c, t)
    elif t < T_STADIUM:
        follow(c, t)
    elif t < T_FINISH:
        stadium_wide(c, t)
    elif t < T_SPEAK:
        finish(c, t)
    elif t < T_REACT:
        speak(c, t)
    elif t < T_JOE:
        react(c, t)
    elif t < T_EXIT:
        joe_watch(c, t)
        cap(c, t, T_SPEAK + 0.85, T_REACT + 2.2, ['THIS WILL BE OUR', 'LAST TOUR TOGETHER.'], y=1440, size=86)
    elif t < T_SHOE:
        exit_(c, t)
    elif t < T_CHILDSHOE:
        shoe(c, t, adult=True)
    elif t < T_ROOM:
        shoe(c, t, adult=False)
    elif t < T_FINAL:
        empty_room(c, t)
    else:
        final(c, t)
    cap(c, t, T_SHOE + 0.1, T_FINAL - 0.05, ['HE GREW UP', 'IN THE GROUP.'], y=300, size=88)
    cap(c, t, T_FINAL + 0.35, T.DURATION + 1.0, ['BUT HIS FUTURE', 'WAS HIS OWN.'], y=300, size=92)
