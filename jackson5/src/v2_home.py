"""V2 0:00-0:19  THE FEAR -> THE FATHER -> A CHILDHOOD OF REHEARSALS (Gary, Indiana, the family's small living room)."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, font, noise1)
from world import Cam, cam_path, Layer, CHARS, particles, silhouette
from character import outfits, JOE_OUTFIT, DESIGNS, base_pose
import choreo
import timing as T
from v2_common import (caption, draw_cast, JOE, KIDS, GY, DOOR, room_wall, room_floor, lamp, wall_clock, floor_shadow,
                       wall_shadow, L_NIGHT, L_JOE_BACKLIT, L_WARM)

DB = T.db
O = outfits('home')
BEAT = T.PERIOD

# --------------------------------------------------------------------------- shot boundaries (tracked downbeats / half bars)
A_SLIP = 1.20               # Michael misses a step on the glissando
A_DOOR = 1.48               # door opens, light + shadow
A_JOE = DB(0)               # 1.89  band enters: cut to Joe in the doorway
A_EYES = DB(0) + 2 * BEAT   # 3.11  extreme close-up on Michael's eyes
B_CLAP = DB(1)              # 4.33  music returns full: Joe claps - "again"
B_WIDE = DB(2)              # 6.80  over-the-shoulder: the brothers rehearse under his eye
B_TIRED = DB(3)             # 9.27  final pose ... then exhaustion, Michael resets
C0 = DB(4)                  # 11.72 montage, a shot every half bar
HB = (DB(5) - DB(4)) / 2
C_SHOTS = [C0 + i * HB for i in range(6)] + [DB(7)]
END = DB(7)                 # 19.06

# brothers' positions in the room (depth-1 layer)
POS = {'tito': (-400, -40), 'jackie': (-215, -60), 'michael': (-20, 40), 'marlon': (190, -60), 'jermaine': (380, -40)}
INSTR = {'tito': 'guitar', 'jermaine': 'bass'}


def brothers(sched_for, light=L_NIGHT, keys=None, ripple=True, xoff=0.0, yoff=0.0, scale=1.0):
    mem = []
    for k, (x, dy) in POS.items():
        if keys and k not in keys:
            continue
        mem.append(dict(key=k, x=(x + xoff) * scale, gy=GY + dy * scale + yoff, sched=sched_for(k), instrument=INSTR.get(k),
                        ripple={'jackie': 0.03, 'marlon': 0.06}.get(k, 0.0) if ripple else 0.0, light=light))
    return mem


def sched_A(k):
    if k == 'michael':
        return [(0, 'step_touch', {}), (A_SLIP, 'stumble', dict(start='auto')), (A_DOOR + 0.18, 'freeze_fear', dict(look=0.9))]
    if k in INSTR:
        return [(0, 'play', dict(amp=0.6)), (A_DOOR + 0.1, 'freeze_fear', dict(look=0.9))]
    return [(0, 'step_touch', {}), (A_DOOR + 0.1, 'freeze_fear', dict(look=0.9))]


def sched_B(k):
    if k == 'michael':
        return [(0, 'step_touch', {}), (B_TIRED - 0.12, 'point_hit', dict(start='auto', side=1)),
                (B_TIRED + 0.7, 'tired', {}), (B_TIRED + 1.55, 'determined', dict(start='auto')),
                (DB(4) - 0.35, 'step_touch', {})]
    if k in INSTR:
        return [(0, 'play', dict(amp=0.9)), (B_TIRED + 0.7, 'tired', dict(depth=0.5))]
    side = -1 if k == 'jackie' else 1
    return [(0, 'step_touch', {}), (B_TIRED - 0.12, 'point_hit', dict(start='auto', side=side)), (B_TIRED + 0.7, 'tired', {})]


def joe_sched_A():
    return [(0, 'arms_folded', dict(look=-0.6))]


def joe_sched_B():
    return [(0, 'joe_clap', dict(start=T.beat_at(B_CLAP) - T.PHASE)),
            (B_CLAP + 0.55, 'joe_point', dict(start='auto', side=-1)),
            (B_CLAP + 1.9, 'arms_folded', dict(look=-0.5))]


def keystone(c, p=-0.00022, ox=W / 2, oy=H):
    """low-angle look: verticals converge upward"""
    m = skia.Matrix.MakeAll(1, 0, 0, 0, 1, 0, 0, p, 1)
    c.translate(ox, oy)
    c.concat(m)
    c.translate(-ox, -oy)


# --------------------------------------------------------------------------- A: THE FEAR
def shot_slip(c, t):
    door = smoothstep(A_DOOR, A_DOOR + 0.28, t)
    cam = cam_path([(0, Cam(-20, 300, 1.95, -1.5), None), (A_JOE, Cam(-10, 270, 2.25, 1.0), ease_io)], t)
    if A_SLIP + 0.1 < t < A_SLIP + 0.4:
        cam.shake = 0.35
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=door, night=1.0)
        # Joe's shadow rises on the wall behind Michael as the hallway light hits him
        if door > 0:
            grow = ease_out(smoothstep(A_DOOR, A_JOE, t), 2)
            def joe_fig():
                JOE.draw(c, -150 + 160 * (1 - grow), GY + 260, 560 * DESIGNS['joe'].height * (0.9 + 0.75 * grow),
                         base_pose(lsh=0.32, lel=-2.45, rsh=0.32, rel=-2.45), JOE_OUTFIT, L_NIGHT, t, shadow=False)
            wall_shadow(c, joe_fig, a=0.62 * door, blur=10)
    with Layer(c, cam, 1.0, t):
        room_floor(c, door)
        draw_cast(c, t, brothers(sched_A), L_NIGHT, 'home')
    with Layer(c, cam, 1.4, t):
        lamp(c, -900, on=0.55)
    # the hallway light spill across the frame
    if door > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((W, 0), (0, 0), [(1, 0.75, 0.4, 0.22 * door), (0, 0, 0, 0)]),
                                                         blend=skia.BlendMode.kPlus))


def shot_joe_door(c, t, u0=A_JOE, u1=A_EYES, sched=None, push=(1.0, 1.12)):
    """low angle: Joe framed in the bright doorway"""
    u = clamp((t - u0) / (u1 - u0))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c080a'))
    c.save()
    keystone(c)
    s = push[0] + (push[1] - push[0]) * ease_io(u)
    c.translate(W / 2, H * 0.62)
    c.scale(s, s)
    c.translate(-W / 2, -H * 0.62)
    # wall + door frame
    c.drawRect(skia.Rect.MakeLTRB(-400, -400, W + 400, H + 400), shader_paint(lin_grad((0, 0), (0, H), ['#1c141a', '#2a1c1c'])))
    dx0, dx1, dy0 = 150, W - 150, 120
    c.drawRect(skia.Rect.MakeLTRB(dx0 - 40, dy0 - 40, dx1 + 40, H + 300), paint('#3a2e28'))
    c.drawRect(skia.Rect.MakeLTRB(dx0, dy0, dx1, H + 300), shader_paint(lin_grad((0, dy0), (0, H), ['#fff0c8', '#ffcf80', '#e09a4a'])))
    glow(c, W / 2, H * 0.35, 900, '#ffd890', 0.55)
    # hallway: picture frame + coat rack silhouettes for depth
    c.drawRect(skia.Rect.MakeXYWH(dx0 + 60, 420, 150, 190), paint((0.55, 0.36, 0.2, 0.5)))
    c.drawRect(skia.Rect.MakeXYWH(dx1 - 160, 300, 18, 900), paint((0.45, 0.28, 0.16, 0.45)))
    gx, gy = W / 2 + 20, H + 40
    P = choreo.perform(sched or joe_sched_A(), t, 'joe', seed=66)
    P['hyaw'] = -0.15
    JOE.draw(c, gx, gy, 1720, P, JOE_OUTFIT, L_JOE_BACKLIT, t, shadow=False)
    c.restore()
    # dust in the light
    particles(c, t, 40, (150, 100, W - 150, H), 12, '#ffe6b0', size=(1.5, 3.2), speed=(6, 16))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.45), H * 0.75, [(0, 0, 0, 0), (0, 0, 0, 0.55)])))


def face_shot(c, t, key, P, eye_y=H * 0.45, h=5200, bg=None, light=L_NIGHT, outfit=None, gx=W / 2):
    """extreme close-up: place the character so the eye line sits at eye_y"""
    ch = CHARS[key] if key in CHARS else JOE
    S0 = ch.skeleton(0, 0, h, P)
    hx, hy = S0['head']
    gy = eye_y - hy - S0['hr'] * 0.04
    ch.draw(c, gx - hx, gy, h, P, outfit or O[key], light, t, shadow=False)


def shot_eyes(c, t):
    u = clamp((t - A_EYES) / (B_CLAP - A_EYES))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W * 0.8, H * 0.3), H, ['#5a3a2a', '#1a1218', '#0a080c'])))
    P = base_pose()
    choreo.freeze_fear(0, P, look=0.75 + 0.2 * math.sin(t * 9) * (u > 0.45))
    P['ex'] = 0.55 + 0.35 * smoothstep(0.1, 0.25, u) - 0.5 * smoothstep(0.55, 0.62, u) + 0.45 * smoothstep(0.72, 0.8, u)
    P['blink'] = 0.9 if 0.47 < u < 0.52 else 0.0
    P['hyaw'] = 0.12
    s = 5200 * (1.0 + 0.1 * ease_io(u))
    c.save()
    jit = 1.5 * noise1(t * 30, 2)
    c.translate(jit, 0)
    face_shot(c, t, 'michael', P, eye_y=H * 0.47, h=s, light=dict(L_NIGHT, rim='#ffd598', amb_a=0.3, key=(0.8, -0.5)))
    c.restore()
    # warm doorway light raking across from the right
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((W, 0), (W * 0.3, 0), [(1, 0.7, 0.35, 0.22), (0, 0, 0, 0)]),
                                                     blend=skia.BlendMode.kPlus))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.47), H * 0.6, [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0.7)],
                                                             [0, 0.5, 1])))


# --------------------------------------------------------------------------- B: THE FATHER
def shot_joe_room(c, t):
    shot_joe_door(c, t, B_CLAP, B_WIDE, sched=joe_sched_B(), push=(1.18, 1.32))
    lp = skia.Paint()
    lp.setImageFilter(skia.ImageFilters.Blur(9, 9))
    c.saveLayer(None, lp)
    for i, (k, x) in enumerate((('jackie', 150), ('michael', 560), ('marlon', 930))):
        P = cast_like(k, [(0, 'freeze_fear', dict(look=0.0))], t)
        P['spin'] = 0.5
        CHARS[k].draw(c, x, H * 1.55 + (60 if k == 'michael' else 0), 1500 * DESIGNS[k].height, P, O[k],
                      dict(L_NIGHT, amb='#1a1218', amb_a=0.8), t, shadow=False)
    c.restore()


def shot_overshoulder(c, t):
    u = clamp((t - B_WIDE) / (B_TIRED - B_WIDE))
    cam = Cam(-60 + 80 * ease_io(u), 230, 1.14, -1.0 + 2 * u)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=1.0, night=0.85)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 1.0)
        draw_cast(c, t, brothers(sched_B), dict(L_NIGHT, amb_a=0.3), 'home')
    with Layer(c, cam, 1.55, t):
        # Joe in the foreground, back to camera, arms folded, rim-lit by the hallway
        P = choreo.perform([(0, 'arms_folded', {})], t, 'joe', seed=66)
        P['spin'] = 0.5
        P.update(lsh=0.14, lel=-0.55, rsh=0.14, rel=-0.55, lhand='fist', rhand='fist')   # hands clasped behind his back
        JOE.draw(c, 250, GY + 700, 560 * DESIGNS['joe'].height, P, JOE_OUTFIT, L_JOE_BACKLIT, t, shadow=False)
    caption(c, t, B_CLAP + 0.6, B_WIDE + 2.2, ['THEIR FATHER', 'DEMANDED PERFECTION.'], y=300)


def shot_tired(c, t):
    u = clamp((t - B_TIRED) / (C0 - B_TIRED))
    cam = Cam(-40, 280, 1.85 + 0.25 * ease_io(u), 0.5)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=1.0, night=0.85)
        # Joe's shadow looming on the wall over the boys
        def jf():
            P = choreo.perform([(0, 'arms_folded', {})], t, 'joe', seed=66)
            JOE.draw(c, 260, GY + 200, 560 * DESIGNS['joe'].height * 1.35, P, JOE_OUTFIT, L_NIGHT, t, shadow=False)
        wall_shadow(c, jf, a=0.45, blur=12)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 1.0)

        def look(k):
            def f(tt):
                if k in ('jackie', 'marlon') and tt > B_TIRED + 1.1:
                    return dict(ex=0.85, hyaw=0.3, brow=0.8)      # nervous glance toward their father
                return {}
            return f
        mem = brothers(sched_B)
        for m in mem:
            m['over'] = look(m['key'])
        draw_cast(c, t, mem, dict(L_NIGHT, amb_a=0.3), 'home')


# --------------------------------------------------------------------------- C: A CHILDHOOD OF REHEARSALS (montage)
def m_feet(c, t):
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#1a1210', '#3a2416'])))
    c.save()
    for k in range(-12, 13):
        c.drawLine(W / 2 + k * 90, H * 0.35, W / 2 + k * 420, H + 200, paint((0.1, 0.05, 0.02, 0.5), style='stroke', width=5))
    c.restore()
    glow(c, W * 0.5, H * 0.75, 700, '#ffb060', 0.25)
    c.drawOval(skia.Rect.MakeXYWH(W * 0.1, H * 0.7, W * 0.85, 260), paint((1, 0.75, 0.4, 0.35), blur=60, blend=skia.BlendMode.kPlus))
    P = cast_like('michael', [(0, 'step_touch', dict(width=0.07))], t)
    P['sweat'] = 0
    CHARS['michael'].draw(c, W / 2 + 40, H * 0.76, 2300, P, O['michael'], L_WARM, t)
    # a brother's feet behind, out of focus
    lp = skia.Paint()
    lp.setImageFilter(skia.ImageFilters.Blur(10, 10))
    c.saveLayer(None, lp)
    P2 = cast_like('marlon', [(0, 'step_touch', dict(width=0.07))], t - 0.06)
    CHARS['marlon'].draw(c, W * 0.12, H * 0.6, 1900, P2, O['marlon'], L_NIGHT, t)
    c.restore()


def cast_like(k, sched, t, **kw):
    return choreo.perform(sched, t, k, seed=DESIGNS[k].seed, **kw)


def m_clock(c, t):
    u = clamp((t - C_SHOTS[1]) / HB)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#3a2a22', '#24181a'])))
    for iy in range(-2, 24):
        for ix in range(-1, 13):
            x, y = ix * 90 + (iy % 2) * 45, iy * 90
            c.drawPath(poly_path([(x, y - 22), (x + 16, y), (x, y + 22), (x - 16, y)]), paint((0.95, 0.78, 0.5, 0.08)))
    # dancers' shadows sweeping across the wallpaper behind the clock
    def band_sil():
        mem = [dict(key=k, x=x * 1.6 + W / 2 - 120, gy=H * 0.98, sched=[(0, 'step_touch', {})], instrument=None)
               for k, (x, dy) in POS.items() if k not in ('tito', 'jermaine')]
        draw_cast(c, t, mem, L_NIGHT, 'home', base_h=700)
    wall_shadow(c, band_sil, a=0.5, blur=16)
    hours = 19.6 + 3.4 * ease_in(u, 1.6)       # 7:36 pm -> 11:00 pm
    wall_clock(c, W / 2, H * 0.42, 300, hours)
    glow(c, W * 0.2, H * 0.2, 600, '#ffb060', 0.12)


def m_rehearse(c, t):
    u = clamp((t - C_SHOTS[2]) / HB)
    cam = Cam(60 - 80 * u, 260, 1.32, -1)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=0.0, night=1.0, clock_t=22.9 + t / 3600)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 0)
        def tired_over(tt):
            return dict(sweat=0.9, brow=0.45, smile=0.1, mopen=0.3, mshape='o')
        mem = brothers(lambda k: [(0, 'play', dict(amp=0.6))] if k in INSTR else [(0, 'step_touch', dict(amp=0.75))])
        for m in mem:
            m['over'] = tired_over
        draw_cast(c, t, mem, L_NIGHT, 'home')
    with Layer(c, cam, 1.4, t):
        lamp(c, -760, on=0.7)


def m_window(c, t):
    """Michael at the window; outside, other kids play in the last of the daylight"""
    u = clamp((t - C_SHOTS[3]) / HB)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#120c10'))
    # outside world (seen through the glass)
    wx0, wy0, wx1, wy1 = 110, 260, 970, 1250
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1))
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), shader_paint(lin_grad((0, wy0), (0, wy1), ['#f6b866', '#f08a4a', '#c86a52'])))
    glow(c, 760, 760, 260, '#fff0c0', 0.8)
    for k in range(7):     # row houses across the street
        x = wx0 - 40 + k * 150
        c.drawRect(skia.Rect.MakeLTRB(x, 760, x + 130, 1000), paint('#8a4a3a'))
        c.drawPath(poly_path([(x - 8, 760), (x + 65, 700), (x + 138, 760)]), paint('#6a3a30'))
    c.drawRect(skia.Rect.MakeLTRB(wx0, 990, wx1, wy1), paint('#b08a6a'))
    kids_t = t
    def kids():
        for i, (x, k, sched) in enumerate([(300, 0, [(0, 'jump_cheer', dict(amp=1.2))]), (560, 1, [(0, 'kick', dict(side=1))]),
                                           (800, 0, [(0, 'wave', {})])]):
            P = choreo.perform(sched, kids_t + i * 0.2, 'kid%d' % (k + 1), seed=80 + i)
            KIDS[k].draw(c, x, 1160, 330 * (1.0 if k == 0 else 0.92), P, outfits('home')['marlon'], L_WARM, kids_t)
        # jump rope arc + ball
        ph = (T.beat_at(kids_t)) % 1
        c.drawArc(skia.Rect.MakeXYWH(200, 860 + 220 * math.cos(ph * 2 * math.pi), 200, 300 - 280 * math.cos(ph * 2 * math.pi)),
                  0, 180, False, paint((0.2, 0.1, 0.1, 1), style='stroke', width=5))
        bx = 640 + 120 * math.sin(kids_t * 3)
        c.drawCircle(bx, 1150 - 160 * abs(math.sin(kids_t * 3)), 26, paint('#3a1a12'))
    silhouette(c, kids, color=(0.25, 0.1, 0.08, 1.0))
    c.restore()
    # window frame + glass reflection
    c.drawRect(skia.Rect.MakeLTRB(wx0, wy0, wx1, wy1), paint('#d8ccb4', style='stroke', width=36))
    c.drawLine(W / 2, wy0, W / 2, wy1, paint('#d8ccb4', style='stroke', width=22))
    c.drawPath(poly_path([(wx0 + 80, wy0), (wx0 + 260, wy0), (wx0 + 60, wy1), (wx0 - 120, wy1)]), paint((1, 1, 1, 0.07)))
    # dark interior wall around the window
    wall = skia.Path()
    wall.addRect(skia.Rect.MakeLTRB(0, 0, W, H))
    hole = skia.Path()
    hole.addRect(skia.Rect.MakeLTRB(wx0 - 18, wy0 - 18, wx1 + 18, wy1 + 18))
    c.drawPath(skia.Op(wall, hole, skia.PathOp.kDifference_PathOp), shader_paint(lin_grad((0, 0), (0, H), ['#2a1e1e', '#1a1214'])))
    c.drawRect(skia.Rect.MakeLTRB(wx0 - 60, wy1 + 10, wx1 + 60, wy1 + 60), paint('#cfc2a8'))
    # Michael from behind, hand on the glass, rim-lit by the sunset
    P = cast_like('michael', [(0, 'look_out', {})], t)
    CHARS['michael'].draw(c, W * 0.42 + 30 * u, H * 1.12, 1650, P, O['michael'],
                          dict(L_NIGHT, rim='#ffb070', key=(0.2, -1.0)), t, shadow=False)


def m_joe_door(c, t):
    shot_joe_door(c, t, C_SHOTS[4], C_SHOTS[5], push=(1.05, 1.15))


def m_back_to_work(c, t):
    u = clamp((t - C_SHOTS[5]) / (END - C_SHOTS[5]))
    cam = Cam(-20, 300, 2.9 - 0.6 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=0.0, night=1.0, clock_t=23.1)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 0)
        glow(c, -20, GY - 200, 520, '#ffcf8a', 0.3)       # a single pool of lamp light on Michael
        mem = [dict(key='michael', x=-20, gy=GY + 40, light=L_WARM,
                    sched=[(0, 'determined', dict(start='auto')), (C_SHOTS[5] + 0.5, 'step_touch', dict(amp=1.15))])]
        draw_cast(c, t, mem, L_WARM, 'home')


# --------------------------------------------------------------------------- dispatcher
def draw(c, t):
    if t < A_JOE:
        shot_slip(c, t)
    elif t < A_EYES:
        shot_joe_door(c, t)
    elif t < B_CLAP:
        shot_eyes(c, t)
    elif t < B_WIDE:
        shot_joe_room(c, t)
    elif t < B_TIRED:
        shot_overshoulder(c, t)
    elif t < C0:
        shot_tired(c, t)
    else:
        i = max(i for i, s in enumerate(C_SHOTS[:-1]) if t >= s)
        [m_feet, m_clock, m_rehearse, m_window, m_joe_door, m_back_to_work][i](c, t)
    # captions (screen space, TikTok-safe: centred, clear of the top 230 px and bottom UI)
    caption(c, t, 0.25, A_EYES - 0.05, ['BEFORE THE FAME…'], y=330, size=84)
    caption(c, t, A_EYES + 0.15, B_CLAP - 0.02, ['THERE WAS FEAR.'], y=1420, size=96)
    if B_CLAP <= t < B_WIDE:
        caption(c, t, B_CLAP + 0.6, B_WIDE + 2.2, ['THEIR FATHER', 'DEMANDED PERFECTION.'], y=300)
    caption(c, t, C0 + 0.3, C_SHOTS[3] - 0.1, ['WHILE OTHER KIDS PLAYED…'], y=300)
    caption(c, t, C_SHOTS[3] + 0.15, END - 0.1, ['THEY KEPT REHEARSING.'], y=300)
