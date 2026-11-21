"""V2 0:39-1:09  A NEW SOUND -> GLOBAL FAME -> THE PRICE OF FAME."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, font, text_center, noise1)
from world import Cam, cam_path, Layer, CHARS, particles, silhouette, crowd, floor_reflection, light_rig
from character import outfits, JOE_OUTFIT, DJ_OUTFIT, DESIGNS, base_pose
import choreo
import timing as T
import scene3
import scene4
import scene5
from v2_common import (caption, draw_cast, JOE, DJ, KIDS, GY, room_wall, room_floor, lamp, L_NIGHT, L_WARM, L_JOE_BACKLIT)

DB = T.db
BEAT = T.PERIOD
F_SING = DB(15)
F_DJ = DB(16)
F_CITY = DB(16) + 2 * BEAT
F_STORE = DB(17)
F_HOME = DB(17) + 2 * BEAT
G_TV = DB(19)
G_SIL = DB(20)
G_ARENA = DB(21)
G_SOLO = DB(22)
H_SMILE = DB(23)
H_MIRROR = DB(24)
H_GOLD = DB(25)
START = F_SING
STAGE_POS = {'tito': (-360, -30), 'jackie': (-185, -50), 'michael': (0, 30), 'marlon': (185, -50), 'jermaine': (360, -30)}
INSTR = {'tito': 'guitar', 'jermaine': 'bass'}
SGY = 380


def stage_cast(sched, era, light, gy=SGY, sing=1.0, xform=None):
    mem = []
    for k, (x, dy) in STAGE_POS.items():
        xx, yy = (xform(k, x, dy) if xform else (x, dy))
        mem.append(dict(key=k, x=xx, gy=gy + yy, sched=sched(k), instrument=INSTR.get(k), light=light,
                        sing=sing if k == 'michael' else (0.4 if k in ('jermaine', 'jackie') else None),
                        ripple={'jackie': 0.035, 'marlon': 0.07}.get(k, 0.0)))
    return mem


# --------------------------------------------------------------------------- F: A NEW SOUND
def f_sing(c, t):
    scene3.close_up(c, t, T.beat_at(t))


def f_dj(c, t):
    """a radio DJ drops the needle: the record now *means* something"""
    u = clamp((t - F_DJ) / (F_CITY - F_DJ))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#1a2a3a', '#2a1a2a'])))
    for k in range(6):
        c.drawRoundRect(skia.Rect.MakeXYWH(k * 200 - 60, 120, 170, 900), 16, 16, paint((0.3, 0.38, 0.45, 0.35)))
    # ON AIR light
    c.drawRoundRect(skia.Rect.MakeXYWH(W / 2 - 170, 330, 340, 110), 18, 18, paint('#2a0a0a'))
    glow(c, W / 2, 385, 260, '#ff2a1a', 0.55 + 0.2 * math.sin(t * 7))
    text_center(c, 'ON AIR', W / 2, 415, font('spartan', 80), paint('#ffd0c0'))
    P = choreo.perform([(0, 'groove', dict(amp=0.8, snap=True))], t, 'dj', seed=77)
    P.update(headphones=True, smile=1.0, mopen=0.45, mshape='grin', ey=0.4, ex=-0.2)
    P['rsh'], P['rel'] = 0.9 - 0.5 * ease_out(clamp(u / 0.4)), -1.2
    DJ.draw(c, W * 0.5, H * 1.05, 1500, P, DJ_OUTFIT, dict(L_WARM, rim='#7af0ff'), t, shadow=False)
    # boom mic
    c.drawLine(W * 0.95, 500, W * 0.66, 780, paint('#1a1a1e', style='stroke', width=16))
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.6, 740, 110, 170), 50, 50, paint('#3a3a42'))
    # console + turntable in the foreground: the needle lands on the record
    c.drawRect(skia.Rect.MakeLTRB(-20, H * 0.73, W + 20, H + 20), shader_paint(lin_grad((0, H * 0.73), (0, H), ['#5a4a3a', '#2a2018'])))
    rx, ry = W * 0.5, H * 0.86
    c.save()
    c.translate(rx, ry)
    c.scale(1.0, 0.42)
    scene3.record(c, 0, 0, 330, t * 200)
    c.restore()
    land = ease_out(clamp(u / 0.35), 3)
    ax, ay = W * 0.88, H * 0.78
    tip = (ax - 250 - 30 * land, ay + 60 + 50 * land)
    c.drawLine(ax, ay, tip[0], tip[1], paint('#d8d8e0', style='stroke', width=14))
    c.drawCircle(ax, ay, 36, paint('#8a8a96'))
    for k in range(3):           # sound rings when the needle hits
        r = (t - F_DJ - 0.35 - k * 0.2) * 900
        if r > 0:
            c.drawCircle(rx, ry - 80, r, paint((1, 0.85, 0.5, max(0, 0.5 - r / 1600)), style='stroke', width=6))


def f_city(c, t):
    """the song travels: radio waves over the rooftops, people dancing in lit windows"""
    u = clamp((t - F_CITY) / (F_STORE - F_CITY))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#0c1030', '#2a2050', '#6a3a5a'])))
    # radio tower
    tx, ty = W * 0.5, 520
    c.drawPath(poly_path([(tx - 90, 1100), (tx + 90, 1100), (tx + 8, ty), (tx - 8, ty)]), paint('#120e1a'))
    for k in range(8):
        y = ty + k * 72
        c.drawLine(tx - 10 - k * 10, y, tx + 10 + k * 10, y + 70, paint('#1e1828', style='stroke', width=4))
    glow(c, tx, ty - 10, 60, '#ff3a3a', 0.9 * (0.5 + 0.5 * math.sin(t * 6)))
    for k in range(5):
        r = ((t - F_CITY) * 520 + k * 260) % 1300
        c.drawCircle(tx, ty, r, paint((1, 0.8, 0.5, 0.45 * (1 - r / 1300)), style='stroke', width=5))
    # rooftops with lit windows, silhouettes dancing inside
    rng = np.random.default_rng(1969)
    x = -40
    wins = []
    while x < W + 40:
        w_ = rng.uniform(170, 260)
        top = rng.uniform(1050, 1250)
        c.drawRect(skia.Rect.MakeLTRB(x, top, x + w_, H + 20), paint('#160f1e'))
        for row in range(4):
            for col in range(2):
                wx, wy = x + 25 + col * (w_ / 2), top + 40 + row * 160
                lit = rng.random() < 0.6
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, w_ / 2 - 50, 110), paint('#ffcf7a' if lit else '#2a2230'))
                if lit:
                    wins.append((wx, wy, w_ / 2 - 50))
        x += w_ + rng.uniform(10, 30)
    for i, (wx, wy, ww) in enumerate(wins[:10]):
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, 110))
        def fig(i=i, wx=wx, wy=wy, ww=ww):
            P = choreo.perform([(0, 'groove' if i % 2 else 'step_touch', {})], t + i * 0.1, 'kid1', seed=90 + i)
            KIDS[i % 2].draw(c, wx + ww / 2, wy + 190, 230, P, outfits('home')['marlon'], L_WARM, t, shadow=False)
        silhouette(c, fig, color=(0.35, 0.16, 0.08, 1.0))
        c.restore()


def f_store(c, t):
    """record-store window: the single in the display, kids pointing at it"""
    u = clamp((t - F_STORE) / (F_HOME - F_STORE))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#4a2420'))
    for row in range(-1, 45):        # brick façade
        off = 40 if row % 2 else 0
        for k in range(-1, 14):
            c.drawRect(skia.Rect.MakeXYWH(k * 90 + off + 2, row * 44 + 2, 86, 40), paint(mix('#6a2e24', '#8a3e2e', ((k * 7 + row * 3) % 5) / 5)))
    # neon sign
    glow(c, W / 2, 300, 420, '#3af0ff', 0.35)
    text_center(c, 'RECORDS', W / 2, 340, font('spartan', 150), paint('#b0faff'))
    # shop window
    wx0, wy0, wx1, wy1 = 70, 470, W - 70, 1380
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), shader_paint(lin_grad((0, wy0), (0, wy1), ['#ffe2b0', '#e8b070'])))
    cols = ['#ff7a1a', '#7a2aa0', '#1ab8b8', '#ffc83a', '#e0306a', '#3a8a3a']
    for i in range(12):            # album sleeves: five silhouettes on bold colour
        r, cc = divmod(i, 4)
        x, y = wx0 + 40 + cc * 225, wy0 + 40 + r * 290
        pop = back_out(clamp((u * 1.6 - i * 0.05) / 0.4), 1.6)
        s = 200 * pop
        if s < 4:
            continue
        x += (200 - s) / 2
        y += (200 - s) / 2
        c.drawRect(skia.Rect.MakeXYWH(x, y, s, s), paint(cols[i % 6]))
        for j in range(5):
            hx = x + s * (0.18 + j * 0.16)
            hy = y + s * (0.56 - 0.06 * (j == 2))
            c.drawCircle(hx, hy, s * 0.07, paint('#1a0a10'))
            c.drawRect(skia.Rect.MakeXYWH(hx - s * 0.06, hy + s * 0.05, s * 0.12, s * 0.2), paint('#1a0a10'))
        c.drawString('J5', x + s * 0.08, y + s * 0.22, font('spartan', s * 0.18), paint('#fff4dc'))
    # "NEW!" placard
    c.save()
    c.rotate(-8, W * 0.78, wy0 + 30)
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.62, wy0 - 30, 300, 110), 14, 14, paint('#ffef6a'))
    text_center(c, 'NEW!', W * 0.62 + 150, wy0 + 50, font('spartan', 80), paint('#c0141e'))
    c.restore()
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), paint('#2a1a14', style='stroke', width=26))
    c.drawPath(poly_path([(wx0 + 100, wy0), (wx0 + 300, wy0), (wx0 + 60, wy1), (wx0 - 140, wy1)]), paint((1, 1, 1, 0.12)))
    # kids on the sidewalk in front, pointing (backs to us)
    def kids():
        for i, (x, k) in enumerate(((260, 0), (560, 1), (820, 0))):
            P = base_pose(spin=0.5)
            if i == 1:
                P.update(rsh=2.0, rel=0.2, rhand='point')
            else:
                P.update(lsh=0.3, lel=-0.6, rsh=0.3, rel=-0.6)
            P['y'] = -0.02 * abs(math.sin((t + i) * 5)) * (i == 2)
            KIDS[k].draw(c, x, H * 1.02, 900 * (1.0 if k == 0 else 0.92), P, outfits('home')['marlon'], L_WARM, t, shadow=False)
    silhouette(c, kids, color=(0.1, 0.05, 0.06, 1.0))


def f_home(c, t):
    """the brothers hear themselves on the radio at home"""
    u = clamp((t - F_HOME) / (G_TV - F_HOME))
    cam = Cam(40, 250, 1.14 + 0.1 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1a1210'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=1.0, night=0.3)
        # Joe in the doorway: arms folded ... and, for once, a hint of a smile
        P = choreo.perform([(0, 'arms_folded', dict(stern=0.35, look=-0.6))], t, 'joe', seed=66)
        P['smile'] = -0.1 + 0.4 * smoothstep(0.35, 0.6, u)
        JOE.draw(c, 330, GY, 560 * 1.66, P, JOE_OUTFIT, dict(L_WARM, amb_a=0.4), t, shadow=False)
        # the radio, dial glowing, sound rings
        glow(c, 260, GY - 190, 160, '#ffcf6a', 0.7)
        for k in range(3):
            r = ((t - F_HOME) * 300 + k * 120) % 360
            c.drawCircle(260, GY - 190, r, paint((1, 0.85, 0.5, 0.5 * (1 - r / 360)), style='stroke', width=4))
    with Layer(c, cam, 1.0, t):
        room_floor(c, 0.6)
        pos = {'tito': (-380, -40), 'jackie': (-195, -60), 'michael': (10, 40), 'marlon': (210, -60), 'jermaine': (400, -40)}
        mem = []
        for k, (x, dy) in pos.items():
            t0 = F_HOME + {'michael': 0.0, 'marlon': 0.12, 'jackie': 0.2, 'jermaine': 0.28, 'tito': 0.35}[k]
            mem.append(dict(key=k, x=x, gy=GY + dy, light=L_WARM,
                            sched=[(0, 'freeze_fear', dict(look=-0.8)), (t0, 'jump_cheer', dict(amp=1.0 if k == 'michael' else 0.8))],
                            over=(lambda tt: dict(fear=0.0, brow=0.9, smile=0.6, mopen=0.4, mshape='o')) if True else None))
        # first a beat of disbelief (eyes wide on the radio), then they explode with joy
        for m in mem:
            k0 = m['sched'][1][0]
            m['over'] = (lambda tt, k0=k0: dict(fear=0.0, brow=0.9, smile=0.6, mopen=0.45, mshape='o', ex=-0.9, hyaw=-0.3)
                         if tt < k0 else {})
        draw_cast(c, t, mem, L_WARM, 'home')


# --------------------------------------------------------------------------- G: GLOBAL FAME
def g_sched(k):
    if k in INSTR:
        return [(0, 'play', dict(amp=1.3))]
    side = -1 if k == 'jackie' else 1
    if k == 'michael':
        return [(0, 'step_touch', {}), (G_TV + 2 * BEAT - 0.1, 'spin', dict(start='auto', length=1.0)),
                (G_TV + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=1)),
                (G_SIL, 'arm_roll', dict(amp=1.3)), (G_SIL + 2 * BEAT, 'shimmy', {}),
                (G_ARENA, 'slide', dict(start='auto', dirn=1, dist=0.3, beats=2.0)),
                (G_ARENA + 2 * BEAT, 'slide', dict(start='auto', dirn=-1, dist=0.3, beats=2.0)),
                (G_SOLO, 'kick', dict(side=1)), (G_SOLO + 2 * BEAT - 0.1, 'spin', dict(start='auto', length=1.0)),
                (G_SOLO + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=1)),
                (H_SMILE, 'mic_sing', dict(amp=1.0))]
    return [(0, 'step_touch', {}), (G_TV + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=side)),
            (G_SIL, 'arm_roll', {}), (G_SIL + 2 * BEAT, 'kick', dict(side=side)),
            (G_ARENA, 'shimmy', {}), (G_SOLO, 'step_touch', {}),
            (G_SOLO + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=side))]


def g_tv(c, t):
    beat = T.beat_at(t)
    u = clamp((t - G_TV) / (G_SIL - G_TV))
    cam = Cam(-80 + 160 * ease_io(u), 0, 0.9 + 0.08 * u, -3 + 6 * u)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#100618'))
    with Layer(c, cam, 0.7, t):
        scene4.stage_set(c, t, beat, 0.0)
    with Layer(c, cam, 1.0, t):
        mem = stage_cast(g_sched, 'tv', scene4.LIGHT)
        floor_reflection(c, lambda: draw_cast(c, t, mem, scene4.LIGHT, 'tv'), SGY, 0.2)
        for i, x in enumerate((-500, -150, 150, 500)):
            beam(c, x * 2.2, -1700, x * 0.6, SGY, 40, 200, scene4.PAL[(i + int(beat)) % 5], 0.3, blur=30)
        draw_cast(c, t, mem, scene4.LIGHT, 'tv')
    with Layer(c, cam, 1.6, t):
        scene4.tv_camera(c, -820, 520, 1.1)
    caption(c, t, G_TV + 0.25, G_SIL + 0.6, ['FIVE BROTHERS.'], y=1450, size=92)


def g_sil(c, t):
    beat = T.beat_at(t)
    u = clamp((t - G_SIL) / (G_ARENA - G_SIL))
    cam = Cam(0, -100, 0.82 + 0.1 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#100618'))
    with Layer(c, cam, 0.7, t):
        scene4.stage_set(c, t, beat, 1.0)
    with Layer(c, cam, 1.0, t):
        mem = stage_cast(g_sched, 'tv', scene4.LIGHT)
        silhouette(c, lambda: draw_cast(c, t, mem, scene4.LIGHT, 'tv'), color=(0.07, 0.02, 0.06, 1.0), halo=(1.0, 0.85, 0.45, 0.9))
    caption(c, t, G_TV + 0.25, G_SIL + 0.6, ['FIVE BROTHERS.'], y=1450, size=92)


def arena(c, t, cam, gold=0.0, sched=g_sched, energy=1.0, conf=False):
    beat = T.beat_at(t)
    L = scene5.light_for(t, beat, gold)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#08030f'))
    with Layer(c, cam, 0.55, t):
        scene5.arena_bg(c, t, beat, gold)
    with Layer(c, cam, 1.0, t):
        scene5.beams(c, t, beat, gold)
        mem = stage_cast(sched, 'arena', L)
        if cam.z < 1.5:
            floor_reflection(c, lambda: draw_cast(c, t, mem, L, 'arena'), SGY, 0.18)
        if gold > 0:
            glow(c, 0, SGY - 200, 900, scene5.GOLD, 0.35 * gold)
        draw_cast(c, t, mem, L, 'arena')
        particles(c, t, 40, (-1200, -1600, 1200, 300), 61, mix('#e8d8ff', scene5.GOLD, gold), size=(1.5, 3.5), speed=(8, 22))
    with Layer(c, cam, 1.4, t):
        crowd(c, t, 5, energy, '#07030c', mix('#ff6ab0', scene5.GOLD, gold), width=4600, seed=88, y0=760, row_gap=105,
              scale0=1.05, beat_phase=beat, lighters=gold > 0.5)
        c.drawRect(skia.Rect.MakeLTRB(-4000, 640, 4000, 1500), shader_paint(lin_grad((0, 640), (0, 1300),
                   [alpha(mix('#c86aff', scene5.GOLD, gold), 0.35), (0, 0, 0, 0)]), blend=skia.BlendMode.kScreen))
    if conf:
        scene5.confetti(c, t, H_GOLD - 0.6)


def g_arena(c, t):
    u = clamp((t - G_ARENA) / (G_SOLO - G_ARENA))
    cam = Cam(-200 + 400 * ease_io(u), -260 + 120 * ease_io(u), 0.5 + 0.18 * ease_io(u), -4 + 8 * u)
    arena(c, t, cam)
    caption(c, t, G_ARENA + 0.3, G_SOLO + 2.0, ['ONE WORLDWIDE', 'SENSATION.'], y=300, size=88)


def g_solo(c, t):
    u = clamp((t - G_SOLO) / (H_SMILE - G_SOLO))
    cam = Cam(0, 60, 1.25 + 0.2 * ease_io(u), 2 * math.sin(u * math.pi))
    if 0 <= t - (G_SOLO + 3 * BEAT) < 0.25:
        cam.shake = 0.7
    arena(c, t, cam)
    caption(c, t, G_ARENA + 0.3, G_SOLO + 2.0, ['ONE WORLDWIDE', 'SENSATION.'], y=300, size=88)


# --------------------------------------------------------------------------- H: THE PRICE OF FAME
def _face(c, t, P, eye_y, h, outfit, L, gx=W / 2):
    m = CHARS['michael']
    S0 = m.skeleton(0, 0, h, P)
    m.draw(c, gx - S0['head'][0], eye_y - S0['head'][1] - S0['hr'] * 0.04, h, P, outfit, L, t, shadow=False)


def h_smile(c, t):
    """on stage: the huge smile, the roar - the camera pushes into his face"""
    u = clamp((t - H_SMILE) / (H_MIRROR - H_SMILE))
    beat = T.beat_at(t)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.4), H, ['#5a2a6a', '#24103a', '#08030f'])))
    rng = np.random.default_rng(3)
    for i in range(70):             # crowd-light bokeh behind him
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        col = scene5.BEAM_COLS[i % 5]
        glow(c, x, y, rng.uniform(30, 90), col, 0.25 + 0.2 * math.sin(t * 3 + i))
    P = base_pose(smile=1.0, mopen=0.55, mshape='grin', brow=0.5, ey=-0.2, hyaw=0.12)
    P['blink'] = 0.0
    P['htilt'] = 0.04 * math.sin(beat * math.pi)
    h = 2600 + 2200 * ease_in(u, 1.6)
    _face(c, t, P, H * 0.46, h, outfits('arena')['michael'], dict(scene5.light_for(t, beat, 0.0), amb_a=0.15))
    caption(c, t, H_SMILE + 0.35, H_MIRROR - 0.05, ['THE WORLD SAW', 'THEIR SMILES.'], y=300, size=88)


def h_mirror(c, t):
    """match cut: same framing - but it is the boy in the rehearsal room, alone, looking at his reflection"""
    u = clamp((t - H_MIRROR) / (H_GOLD - H_MIRROR))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c0a10'))
    pull = ease_io(clamp((u - 0.35) / 0.65))
    s = 1.0 - 0.62 * pull
    c.save()
    c.translate(W / 2, H * 0.46)
    c.scale(s, s)
    c.translate(-W / 2, -H * 0.46)
    # mirror: dark-wood frame, the reflection inside
    mr = skia.Rect.MakeLTRB(-120, -260, W + 120, H + 160)
    c.drawRect(skia.Rect.MakeLTRB(-1400, -1400, W + 1400, H + 1400), shader_paint(lin_grad((0, -1400), (0, H + 1400),
               ['#1a1420', '#2a1e1e', '#1a1214'])))
    for iy in range(-18, 40):
        for ix in range(-16, 28):
            x, y = ix * 90 + (iy % 2) * 45, iy * 90
            c.drawPath(poly_path([(x, y - 22), (x + 16, y), (x, y + 22), (x - 16, y)]), paint((0.95, 0.78, 0.5, 0.05)))
    c.drawRect(skia.Rect.MakeLTRB(mr.left() - 60, mr.top() - 60, mr.right() + 60, mr.bottom() + 60), paint('#3a2214'))
    c.save()
    c.clipRect(mr)
    c.drawRect(mr, shader_paint(lin_grad((0, mr.top()), (0, mr.bottom()), ['#2a2a3a', '#3a3040'])))
    glow(c, W * 0.2, H * 0.1, 700, '#ffcf8a', 0.18)
    P = base_pose(smile=-0.12, brow=0.45, blink=0.32, ey=0.05, sweat=0.4, hyaw=-0.05)
    P['blink'] = 0.32 + (0.6 if 0.55 < u < 0.6 else 0)
    _face(c, t, P, H * 0.46, 2600, outfits('home')['michael'], dict(L_NIGHT, amb_a=0.42, key=(-0.8, -0.4)))
    c.drawPath(poly_path([(0, 0), (260, 0), (-100, H), (-360, H)]), paint((1, 1, 1, 0.05)))
    c.restore()
    c.drawRect(mr, paint('#5a3a22', style='stroke', width=18))
    c.restore()
    # as we pull back: the small boy himself, back to camera, in front of the mirror
    if pull > 0:
        P2 = base_pose(spin=0.5, lsh=0.1, lel=0.1, rsh=0.1, rel=0.1)
        CHARS['michael'].draw(c, W / 2 + 10, H * 1.02 + 900 * (1 - pull), 1300, P2, outfits('home')['michael'],
                              dict(L_NIGHT, amb='#1a1420', amb_a=0.7, rim='#ffcf8a'), t, shadow=False)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.45), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.6)])))


def h_gold(c, t):
    """back on stage: five brothers together under golden light; the smile softens"""
    u = clamp((t - H_GOLD) / (T.DURATION - H_GOLD))
    cam = Cam(0, -80 - 260 * ease_out(u, 2), 0.95 - 0.4 * ease_out(u, 2), 0)

    def gold_sched(k):
        if k in INSTR:
            return [(0, 'play', dict(amp=0.4))]
        return [(0, 'pose_hold', {}), (H_GOLD + 2.6, 'stare', dict(sad=0.0))]
    arena(c, t, cam, gold=1.0, sched=gold_sched, energy=0.9, conf=True)
    caption(c, t, H_GOLD + 0.6, T.DURATION + 1.0, ['BUT FEW SAW THE', 'PRESSURE BEHIND THEM.'], y=300, size=96)


def draw(c, t):
    if t < F_DJ:
        f_sing(c, t)
        caption(c, t, F_SING + 0.3, F_CITY - 0.1, ['1969 —', 'I WANT YOU BACK.'], y=1430, size=84)
    elif t < F_CITY:
        f_dj(c, t)
        caption(c, t, F_SING + 0.3, F_CITY - 0.1, ['1969 —', 'I WANT YOU BACK.'], y=1430, size=84)
    elif t < F_STORE:
        f_city(c, t)
    elif t < F_HOME:
        f_store(c, t)
        caption(c, t, F_STORE + 0.15, G_TV - 0.1, ['THEIR FIRST', 'MOTOWN HIT.'], y=1440, size=84)
    elif t < G_TV:
        f_home(c, t)
        caption(c, t, F_STORE + 0.15, G_TV - 0.1, ['THEIR FIRST', 'MOTOWN HIT.'], y=1440, size=84)
    elif t < G_SIL:
        g_tv(c, t)
    elif t < G_ARENA:
        g_sil(c, t)
    elif t < G_SOLO:
        g_arena(c, t)
    elif t < H_SMILE:
        g_solo(c, t)
    elif t < H_MIRROR:
        h_smile(c, t)
    elif t < H_GOLD:
        h_mirror(c, t)
    else:
        h_gold(c, t)
    # white flash on the hard cuts into performance
    for tc in (G_TV, G_ARENA, H_GOLD):
        fl = 1 - smoothstep(tc, tc + 0.25, t)
        if 0 < fl < 1 and t >= tc:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.95, 0.85, 0.5 * fl)))
