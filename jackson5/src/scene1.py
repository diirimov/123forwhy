"""SCENE 1 - THE BEGINNING. Gary, Indiana at dusk -> through the window -> five brothers rehearsing."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, smooth_path, ellipse_path,
                 poly_path, clamp, ease_io, ease_out, ease_in, noise1, font, text_center, cel, smoothstep)
from world import Cam, cam_path, Layer, CHARS, silhouette, particles
from character import outfits, BROTHERS
import choreo
import timing as T

DB = T.db
OUT = outfits('home')

# --------------------------------------------------------------- exterior art
_rng = np.random.default_rng(1965)
STARS = [(x, y, s) for x, y, s in zip(_rng.uniform(-900, 900, 140), _rng.uniform(-2600, -900, 140), _rng.uniform(0.6, 2.2, 140))]


def sky(c, t, cam):
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H),
               ['#141a33', '#2b3557', '#5b5a74', '#c98a5a', '#f0b26a'], [0, 0.3, 0.55, 0.8, 1.0])))


def far_mill(c, t):
    # Gary steel mill on the horizon: stacks, furnace glow, smoke
    base = 260
    glow(c, 320, base - 20, 420, '#ff8a3a', 0.35)
    for i, (x, w, hgt) in enumerate([(-520, 40, 420), (-440, 34, 520), (-360, 46, 380), (260, 38, 470), (330, 30, 560),
                                     (420, 52, 360), (520, 36, 440)]):
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2, base - hgt, x + w / 2, base + 40), paint('#3a3348'))
        c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 4, base - hgt, x + w / 2 + 4, base - hgt + 14), paint('#453d54'))
        for k in range(7):
            age = (t * 0.35 + k / 7 + i * 0.13) % 1.0
            sx = x + age * 140 + math.sin(age * 5 + i) * 20
            sy = base - hgt - age * 380
            r = 26 + age * 110
            c.drawCircle(sx, sy, r, paint((0.55, 0.45, 0.5, 0.22 * (1 - age)), blur=r * 0.35))
    c.drawRect(skia.Rect.MakeLTRB(-700, base - 120, -250, base + 40), paint('#352f42'))
    c.drawRect(skia.Rect.MakeLTRB(200, base - 150, 700, base + 40), paint('#352f42'))
    for x in range(-680, 700, 60):
        if abs(x) > 230 and (x // 60) % 3:
            c.drawRect(skia.Rect.MakeXYWH(x, base - 70, 14, 10), paint((1.0, 0.65, 0.3, 0.7)))


def far_houses(c, t):
    rng = np.random.default_rng(3)
    x = -1100
    while x < 1100:
        w = rng.uniform(150, 230)
        hgt = rng.uniform(120, 170)
        y = 330
        col = '#2b2a3c'
        c.drawRect(skia.Rect.MakeLTRB(x, y - hgt, x + w, y + 60), paint(col))
        c.drawPath(poly_path([(x - 12, y - hgt), (x + w / 2, y - hgt - 70), (x + w + 12, y - hgt)]), paint('#24233a'))
        if rng.random() < 0.7:
            c.drawRect(skia.Rect.MakeXYWH(x + w * 0.3, y - hgt * 0.6, 26, 30), paint((1.0, 0.75, 0.4, 0.85)))
            glow(c, x + w * 0.3 + 13, y - hgt * 0.6 + 15, 40, '#ffb35a', 0.25)
        if rng.random() < 0.5:   # tree
            tx = x + w + 20
            for k in range(4):
                c.drawCircle(tx + rng.uniform(-30, 30), y - hgt - rng.uniform(0, 90), rng.uniform(45, 70), paint('#1f2333'))
        x += w + rng.uniform(40, 110)


WIN = (60, 40, 300, 230)   # window rect on the house (x, y, w, h) in world coords (centre-ish)


def house(c, t, interior_fn):
    # lawn & sidewalk
    c.drawRect(skia.Rect.MakeLTRB(-1400, 470, 1400, 1400), shader_paint(lin_grad((0, 470), (0, 1000), ['#3c4a2e', '#232a1c'])))
    c.drawRect(skia.Rect.MakeLTRB(-1400, 660, 1400, 760), paint('#6a6460'))
    c.drawRect(skia.Rect.MakeLTRB(-1400, 760, 1400, 1500), paint('#2c2a30'))
    # house body (white clapboard, warm dusk light)
    x0, x1, y0, y1 = -330, 470, -170, 470
    body = skia.Rect.MakeLTRB(x0, y0, x1, y1)
    c.drawRect(body, shader_paint(lin_grad((x0, 0), (x1, 0), ['#c9b9a6', '#e8d8c2', '#b9a894'])))
    for yy in range(int(y0), int(y1), 26):
        c.drawLine(x0, yy, x1, yy, paint((0.35, 0.28, 0.25, 0.35), style='stroke', width=2))
    c.drawRect(body, paint('#3a2a28', style='stroke', width=4))
    # roof
    roof = poly_path([(x0 - 50, y0 + 6), ((x0 + x1) / 2, y0 - 230), (x1 + 50, y0 + 6)])
    c.drawPath(roof, shader_paint(lin_grad((0, y0 - 230), (0, y0), ['#4a3a44', '#2c2430'])))
    c.drawPath(roof, paint('#1e161c', style='stroke', width=5))
    c.drawRect(skia.Rect.MakeLTRB(250, y0 - 210, 300, y0 - 80), paint('#6a3a2e'))       # chimney
    for k in range(5):
        age = (t * 0.3 + k / 5) % 1
        c.drawCircle(275 + age * 60, y0 - 220 - age * 200, 18 + age * 50, paint((0.8, 0.75, 0.8, 0.18 * (1 - age)), blur=20))
    # porch + door
    c.drawRect(skia.Rect.MakeLTRB(-300, 300, -150, 470), paint('#5a3426'))
    c.drawCircle(-170, 390, 6, paint('#d9a94a'))
    c.drawRect(skia.Rect.MakeLTRB(-330, 470, -110, 500), paint('#8a7a6a'))
    c.drawRect(skia.Rect.MakeLTRB(-350, 500, -90, 530), paint('#7a6a5a'))
    # porch light
    glow(c, -330, 270, 120, '#ffc070', 0.6)
    c.drawCircle(-330, 270, 10, paint('#fff0c0'))
    # big front window: warm interior with dancing silhouettes
    wx, wy, ww, wh = WIN
    wr = skia.Rect.MakeXYWH(wx - ww / 2, wy - wh / 2, ww, wh)
    c.save()
    c.clipRect(wr)
    interior_fn(c, wr)
    c.restore()
    c.drawRect(wr, paint('#efe6d6', style='stroke', width=14))
    c.drawLine(wx, wy - wh / 2, wx, wy + wh / 2, paint('#efe6d6', style='stroke', width=9))
    c.drawLine(wx - ww / 2, wy, wx + ww / 2, wy, paint('#efe6d6', style='stroke', width=9))
    c.drawRect(skia.Rect.MakeXYWH(wx - ww / 2 - 30, wy + wh / 2 + 4, ww + 60, 22), paint('#efe6d6'))
    # house number
    c.drawString('2300', -120, -60, font('spartan_b', 34), paint('#2a1e1a'))
    # bushes
    for bx in (-60, 160, 330, 420):
        for k in range(3):
            c.drawCircle(bx + k * 40 - 40, 440 - (k % 2) * 25, 55, paint(mix('#2e3e26', '#1a2216', k * 0.3)))


def window_glow(c, t, wr, energy):
    c.drawRect(wr, shader_paint(lin_grad((0, wr.top()), (0, wr.bottom()), ['#ffcf7a', '#f39a45'])))
    # curtains
    for side in (-1, 1):
        x = wr.left() if side < 0 else wr.right()
        c.drawPath(poly_path([(x, wr.top()), (x - side * -70, wr.top()), (x - side * -40, wr.bottom()), (x, wr.bottom())]),
                   paint((0.6, 0.2, 0.15, 0.7)))


def street_fg(c, t):
    # picket fence + mailbox + street lamp
    for i in range(-14, 15):
        x = i * 62
        c.drawPath(poly_path([(x - 20, 860), (x - 20, 700), (x, 676), (x + 20, 700), (x + 20, 860)]), paint('#d8ccbc'))
        c.drawPath(poly_path([(x - 20, 860), (x - 20, 700), (x, 676), (x + 20, 700), (x + 20, 860)]),
                   paint('#5a4a44', style='stroke', width=3))
    c.drawRect(skia.Rect.MakeLTRB(-1000, 730, 1000, 750), paint('#cfc2b0'))
    c.drawRect(skia.Rect.MakeLTRB(-1000, 800, 1000, 820), paint('#cfc2b0'))
    # street lamp
    c.drawRect(skia.Rect.MakeLTRB(-640, -420, -624, 900), paint('#1c1a20'))
    c.drawPath(poly_path([(-680, -420), (-580, -420), (-600, -380), (-660, -380)]), paint('#1c1a20'))
    glow(c, -630, -370, 260, '#ffd48a', 0.7)
    c.drawCircle(-630, -378, 16, paint('#fff4d0'))


def car_fg(c, t):
    # rear of a 60s sedan in the foreground right (depth > 1)
    body = smooth_path([(380, 1000), (420, 870), (560, 820), (900, 810), (980, 860), (1000, 1000)], True, 0.35)
    c.drawPath(body, shader_paint(lin_grad((400, 820), (400, 1000), ['#7a2a2a', '#3a1214'])))
    c.drawPath(smooth_path([(470, 860), (560, 830), (760, 826), (720, 862)], True, 0.3), paint((0.6, 0.75, 0.9, 0.35)))
    glow(c, 430, 930, 40, '#ff3a2a', 0.8)
    c.drawRect(skia.Rect.MakeLTRB(380, 960, 1000, 985), paint('#c8c8cc'))


# --------------------------------------------------------------- interior art
INT_GY = 560      # ground line of the living room in world coords
POS = {'tito': (-340, -10, 0.95), 'jackie': (-175, -30, 0.97), 'michael': (0, 40, 1.0), 'marlon': (175, -30, 0.97),
       'jermaine': (345, -10, 0.95)}
BASE_H = 360


def room_bg(c, t):
    # wallpaper
    c.drawRect(skia.Rect.MakeLTRB(-1400, -1300, 1400, INT_GY), shader_paint(lin_grad((0, -1200), (0, INT_GY),
               ['#5a3b2a', '#8a5a36', '#a5713f'])))
    for iy in range(-14, 12):
        for ix in range(-14, 15):
            x, y = ix * 90 + (iy % 2) * 45, iy * 90
            d = poly_path([(x, y - 22), (x + 16, y), (x, y + 22), (x - 16, y)])
            c.drawPath(d, paint((0.95, 0.78, 0.5, 0.10)))
            c.drawCircle(x + 45, y + 45, 4, paint((0.95, 0.8, 0.55, 0.12)))
    # wainscot
    c.drawRect(skia.Rect.MakeLTRB(-1400, INT_GY - 230, 1400, INT_GY), paint('#5a3622'))
    c.drawRect(skia.Rect.MakeLTRB(-1400, INT_GY - 240, 1400, INT_GY - 224), paint('#7a4c2e'))
    for x in range(-1400, 1400, 140):
        c.drawRect(skia.Rect.MakeXYWH(x + 18, INT_GY - 205, 104, 175), paint('#4e2e1c', style='stroke', width=4))
    # window (night) with curtains
    wr = skia.Rect.MakeLTRB(-640, -760, -260, -240)
    c.drawRect(wr, shader_paint(lin_grad((0, -760), (0, -240), ['#1d2a4a', '#3a4a70'])))
    for s in range(12):
        x, y = -620 + s * 31, -740 + (s * 97) % 300
        c.drawCircle(x, y, 2, paint((1, 1, 0.9, 0.7)))
    c.drawRect(wr, paint('#e8dcc4', style='stroke', width=16))
    c.drawLine(-450, -760, -450, -240, paint('#e8dcc4', style='stroke', width=10))
    c.drawRect(skia.Rect.MakeLTRB(-760, -830, -140, -800), paint('#3a2214'))
    for side, x in ((-1, -700), (1, -200)):
        top_w, bot_w = 110, 150
        cur = poly_path([(x - top_w / 2, -810), (x + top_w / 2, -810), (x + bot_w / 2 + side * 10, -150), (x - bot_w / 2 + side * 10, -150)])
        cols = []
        for k in range(9):
            cols.append('#6a2418' if k % 2 else '#b2482c')
        c.drawPath(cur, shader_paint(lin_grad((x - bot_w / 2, 0), (x + bot_w / 2, 0), cols)))
        c.drawRect(skia.Rect.MakeLTRB(x - 70, -420, x + 70, -398), paint('#d9a94a'))
    # family photos
    for i, (x, y, w, h) in enumerate([(120, -700, 140, 170), (300, -640, 110, 140), (460, -720, 160, 120)]):
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint('#3a2214'))
        c.drawRect(skia.Rect.MakeXYWH(x + 12, y + 12, w - 24, h - 24), shader_paint(lin_grad((x, y), (x, y + h),
                   ['#d8c4a0', '#9a8462'])))
        n = 3 if i == 1 else 2
        for k in range(n):
            px = x + w * (k + 1) / (n + 1)
            c.drawCircle(px, y + h * 0.42, 15, paint((0.32, 0.2, 0.13, 0.85), blur=1.5))
            c.drawOval(skia.Rect.MakeXYWH(px - 22, y + h * 0.55, 44, 40), paint((0.32, 0.2, 0.13, 0.85), blur=1.5))
    # record player cabinet + radio
    c.drawRoundRect(skia.Rect.MakeLTRB(560, INT_GY - 300, 900, INT_GY - 40), 12, 12, paint('#4a2a18'))
    c.drawRect(skia.Rect.MakeLTRB(580, INT_GY - 280, 880, INT_GY - 200), paint('#2a1a10'))
    rec = (720, INT_GY - 240)
    c.drawOval(skia.Rect.MakeXYWH(rec[0] - 110, rec[1] - 24, 220, 48), paint('#111'))
    c.drawOval(skia.Rect.MakeXYWH(rec[0] - 26, rec[1] - 6, 52, 12), paint('#d04a2a'))
    for k in range(3):
        c.drawRect(skia.Rect.MakeXYWH(600 + k * 90, INT_GY - 170, 60, 100), paint('#5c3a22', style='stroke', width=4))
    # sofa (left)
    c.drawRoundRect(skia.Rect.MakeLTRB(-900, INT_GY - 260, -480, INT_GY - 40), 40, 40, paint('#3f5a5a'))
    c.drawRoundRect(skia.Rect.MakeLTRB(-920, INT_GY - 150, -460, INT_GY - 10), 30, 30, paint('#355050'))
    # floor
    c.drawRect(skia.Rect.MakeLTRB(-1400, INT_GY - 6, 1400, INT_GY + 900), shader_paint(lin_grad((0, INT_GY), (0, INT_GY + 700),
               ['#6a4024', '#3a2414'])))
    for k in range(-20, 21):
        c.drawLine(k * 120, INT_GY, k * 260, INT_GY + 900, paint((0.15, 0.08, 0.04, 0.4), style='stroke', width=3))
    # braided rug
    for k in range(6):
        c.drawOval(skia.Rect.MakeXYWH(-520 + k * 18, INT_GY + 10 + k * 8, 1040 - k * 36, 200 - k * 16),
                   paint(['#8a3a2a', '#b8873a', '#4a5a6a', '#8a3a2a', '#b8873a', '#6a2a20'][k]))
    # amp
    c.drawRoundRect(skia.Rect.MakeLTRB(-560, INT_GY - 170, -430, INT_GY + 10), 8, 8, paint('#1c1612'))
    c.drawRect(skia.Rect.MakeLTRB(-548, INT_GY - 150, -442, INT_GY - 20), paint('#5a4a3a'))
    glow(c, -460, INT_GY - 160, 12, '#ff3a2a', 0.9)


def room_fg(c, t):
    # floor lamp (key light) + armchair edge in the foreground
    c.drawRect(skia.Rect.MakeLTRB(-735, -480, -722, INT_GY + 330), paint('#24180f'))
    shade_ = poly_path([(-800, -520), (-660, -520), (-620, -380), (-840, -380)])
    c.drawPath(shade_, shader_paint(lin_grad((0, -520), (0, -380), ['#f7d79a', '#e0a050'])))
    glow(c, -730, -420, 420, '#ffbf6a', 0.55)
    c.drawRoundRect(skia.Rect.MakeLTRB(520, INT_GY + 160, 1100, INT_GY + 700), 60, 60, paint('#2a1a14'))
    c.drawRoundRect(skia.Rect.MakeLTRB(560, INT_GY + 120, 1100, INT_GY + 260), 50, 50, paint('#3a2418'))


LIGHT_ROOM = dict(key=(-0.75, -0.65), amb='#ffd9a0', amb_a=0.28, rim='#ffcf8a', line='#3a1c12', floor_shadow=0.4)


def schedules():
    d = DB
    S = {}
    dancers = ['jackie', 'michael', 'marlon']
    for k in dancers:
        S[k] = [(0, 'groove', dict(amp=0.4 if k != 'michael' else 0.9)),
                (d(2), 'step_touch', {}),
                (d(3) - 0.15, 'point_hit', dict(start='auto', side=1 if k != 'jackie' else -1)),
                (d(3) + 0.9, 'groove', dict(amp=1.2)),
                (d(4) - 0.62, 'spin', dict(start='auto', length=1.0))]
    S['michael'][0] = (0, 'groove', dict(amp=1.0))
    S['tito'] = [(0, 'play', {})]
    S['jermaine'] = [(0, 'play', dict(amp=1.2))]
    return S


SCHED = schedules()
RIPPLE = {'jackie': 0.03, 'michael': 0.0, 'marlon': 0.06, 'tito': 0.0, 'jermaine': 0.0}


def band_pose(k, t):
    P = choreo.perform(SCHED[k], t, k, seed=BROTHERS[k].seed, ripple=RIPPLE[k],
                       base_kw=dict(instrument='guitar' if k == 'tito' else 'bass' if k == 'jermaine' else None))
    return P


def draw_band(c, t, yaw=0.0, L=LIGHT_ROOM, scale=1.0, sil=False):
    order = sorted(POS, key=lambda k: POS[k][1])
    for k in order:
        x, dy, s = POS[k]
        P = band_pose(k, t)
        P['hyaw'] = clamp(P['hyaw'] + yaw, -0.7, 0.7)
        P['tw'] = clamp(P['tw'] + yaw * 0.8, -0.8, 0.8)
        h = BASE_H * BROTHERS[k].height * s * scale
        CHARS[k].draw(c, x * scale, INT_GY + dy, h, P, OUT[k], L, t)


# --------------------------------------------------------------- the scene
T_WINDOW = DB(1) + 0.05          # push through window
T_INSIDE = DB(1) + 0.55


def draw(c, t):
    if t < T_INSIDE:
        exterior(c, t)
        if t > T_INSIDE - 0.5:      # bright flash through the glass
            u = smoothstep(T_INSIDE - 0.5, T_INSIDE, t)
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1.0, 0.82, 0.55, u)))
    else:
        interior(c, t)
        u = 1 - smoothstep(T_INSIDE, T_INSIDE + 0.35, t)
        if u > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1.0, 0.82, 0.55, u)))


def exterior(c, t):
    wx, wy = WIN[0], WIN[1]
    keys = [(0.0, Cam(0, -1500, 1.0), None), (DB(0), Cam(30, 120, 1.0), lambda u: ease_out(u, 2.4)),
            (T_WINDOW, Cam(wx * 0.7, wy + 40, 1.35), ease_io), (T_INSIDE, Cam(wx, wy, 9.0), lambda u: ease_in(u, 2.6))]
    cam = cam_path(keys, t)
    sky(c, t, cam)
    with Layer(c, cam, 0.0, t):
        for x, y, s in STARS:
            c.drawCircle(x, y + 1000, s, paint((1, 0.95, 0.85, 0.7 + 0.3 * math.sin(t * 2 + x))))
    with Layer(c, cam, 0.12, t):
        c.drawCircle(-300, -900, 60, paint('#f4e8cc'))
        glow(c, -300, -900, 220, '#f4e8cc', 0.25)
    with Layer(c, cam, 0.25, t):
        far_mill(c, t)
    with Layer(c, cam, 0.5, t):
        far_houses(c, t)
    lights_on = smoothstep(DB(0) - 0.05, DB(0) + 0.05, t)

    def interior_fn(cc, wr):
        cc.drawRect(wr, paint('#3a2a2a'))
        if lights_on > 0:
            cc.save()
            p = skia.Paint()
            p.setAlphaf(lights_on)
            cc.saveLayer(None, p)
            window_glow(cc, t, wr, 1)
            cc.save()
            cc.translate(wr.centerX(), wr.bottom() + 40)
            cc.scale(0.42, 0.42)
            cc.translate(0, -INT_GY)
            silhouette(cc, lambda: draw_band(cc, t, L=LIGHT_ROOM), color=(0.22, 0.09, 0.05, 0.92))
            cc.restore()
            cc.restore()
            cc.restore()
    with Layer(c, cam, 1.0, t):
        house(c, t, interior_fn)
        if lights_on > 0:
            glow(c, wx, wy, 380, '#ffb050', 0.35 * lights_on)
        particles(c, t, 26, (-700, 0, 700, 700), 4, '#ffe48a', size=(1.5, 3.5), speed=(6, 18))
    with Layer(c, cam, 1.35, t):
        street_fg(c, t)
    with Layer(c, cam, 1.7, t):
        car_fg(c, t)
    # location card
    a = smoothstep(DB(0) + 0.2, DB(0) + 0.8, t) * (1 - smoothstep(DB(1) - 0.6, DB(1) - 0.1, t))
    if a > 0:
        p = paint((1, 0.94, 0.82, a))
        text_center(c, 'Gary, Indiana', W / 2, 300, font('garamond_i', 92), p)
        text_center(c, '1 9 6 5', W / 2, 380, font('spartan_b', 40), paint((1, 0.8, 0.5, a)), tracking=6)


def interior(c, t):
    # orbit: camera arcs left->right around the band while characters turn against it
    u = clamp((t - T_INSIDE) / (DB(4) - T_INSIDE))
    orbit = math.sin((u - 0.5) * math.pi)       # -1..1
    zoom = 1.55 - 0.22 * smoothstep(T_INSIDE, DB(2), t) + 0.3 * smoothstep(DB(3) - 0.3, DB(3) + 0.2, t)
    cam = Cam(orbit * 110, 330 - 30 * u, zoom, -orbit * 1.5)
    if t > DB(3) - 0.05:
        cam.y = 300 + 60 * smoothstep(DB(3) - 0.05, DB(3) + 0.25, t)      # push to Michael on the group hit
        cam.shake = 0.6 * math.exp(-max(0, t - DB(3)) * 8)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#2a1a12'))
    with Layer(c, cam, 0.65, t):
        room_bg(c, t)
    with Layer(c, cam, 1.0, t):
        glow(c, -500, -100, 900, '#ffb060', 0.18)
        draw_band(c, t, yaw=-orbit * 0.35)
        particles(c, t, 30, (-600, -700, 600, 400), 9, '#ffdca0', size=(1, 2.5), speed=(4, 10))   # dust in lamp light
    with Layer(c, cam, 1.45, t):
        room_fg(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W * 0.25, H * 0.3), H * 0.8,
               [(1, 0.75, 0.45, 0.12), (0, 0, 0, 0)]), blend=skia.BlendMode.kPlus))
