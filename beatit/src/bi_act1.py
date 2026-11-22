"""0:00-0:17.8  HOOK (child star -> 1982, the photograph, the unfinished sheet) and THE CHALLENGE (Thriller sessions,
Quincy Jones asks for a rock song, Michael imagines it, steps to the microphone)."""
import math
import numpy as np
import skia
from bi_common import *  # noqa: F401,F403
from bi_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, font, text_center, noise1, poly_path, smooth_path, T, K,
                       base_pose, pose, draw, place_head, skel, bg, u_of, cap, Cam, Layer, particles, crowd, silhouette,
                       studio_room, tape_machine, vinyl, console, mic_stand, reel)
import scene4

A_J5, A_FACE, A_PHOTO, A_SHEET, A_DECIDE = 0.0, DB(1), DB(2), DB(3), DB(4)
C_GEAR, C_ROOM, C_PITCH, C_DREAM, C_MIC, END = DB(5), DB(6), DB(7), DB(8), DB(9), DB(10)
EYE = (W / 2, H * 0.42)
HEAD_R = 250.0
J5 = ['jackie', 'tito', 'michael', 'jermaine', 'marlon']
J5_X = [-560, -280, 0, 280, 560]
L_STUDIO_DARK = dict(key=(0.05, -1.0), amb='#4a5a8a', amb_a=0.32, rim='#ffcf8a', line='#140c10', floor_shadow=0.0)


# ----------------------------------------------------------------------------- the Jackson 5 stage (also the photograph)
def j5_world(c, t, freeze=None):
    """1970 TV-show stage in world coords (stage floor at y=0). freeze: draw everyone at that time (a photograph)."""
    tt = t if freeze is None else freeze
    beat = T.beat_at(tt)
    c.drawRect(skia.Rect.MakeLTRB(-1600, -2400, 1600, 0), shader_paint(lin_grad((0, -1400), (0, 0), ['#5a1a4a', '#c8502a'])))
    scene4.opart(c, tt, beat, cx=0, cy=-720, scale=1.05, hot=0.15)
    for k in range(-9, 10):               # bulb arch
        a = math.pi * (0.5 + k / 22)
        on = (k + int(beat * 2)) % 3 == 0
        c.drawCircle(math.cos(a) * 760, -380 - math.sin(a) * 760, 12, paint((1, 0.9, 0.6, 1.0 if on else 0.45)))
    c.drawRect(skia.Rect.MakeLTRB(-1600, -10, 1600, 700), shader_paint(lin_grad((0, 0), (0, 600), ['#e8b070', '#7a3a1a'])))
    for k in range(-8, 9):
        c.drawLine(k * 160, 0, k * 420, 700, paint((0.4, 0.2, 0.1, 0.25), style='stroke', width=3))
    sched = lambda k: ([(0, 'step_touch', dict(width=0.05)), (DB(0) + 2 * BEAT - 0.05, 'point_hit', dict(start='auto', side=1)),
                        (DB(1) - 2.2 * BEAT, 'groove', dict(amp=0.8))] if k != 'michael' else
                       [(0, 'step_touch', dict(width=0.04)), (DB(0) + 2 * BEAT - 0.05, 'point_hit', dict(start='auto', side=-1)),
                        (DB(1) - 2.2 * BEAT, 'groove', dict(amp=0.6, arms=False))])
    for k, x in zip(J5, J5_X):
        P = pose(k, sched(k), tt, ripple=0.03 * abs(x) / 210, sing=1.0 if k == 'michael' else 0.3)
        if k == 'michael':
            P['ex'] *= 0.2
        draw(c, k, x, 0, 540 * K.DESIGNS[k].height, P, K.O_J5[k], K.L_TV70, tt)
    for i in range(7):
        glow(c, -900 + i * 300, -1250, 120, ['#ffe0a0', '#ff9ad8', '#9fd8ff'][i % 3], 0.5)


def j5_head(t):
    h = 540 * K.DESIGNS['michael'].height
    P = pose('michael', [(0, 'step_touch', dict(width=0.04)), (DB(0) + 2 * BEAT - 0.05, 'point_hit', dict(start='auto', side=-1)),
                         (DB(1) - 2.2 * BEAT, 'groove', dict(amp=0.6, arms=False))], t)
    S = skel('michael', 0, 0, h, P)
    return S['head'], S['hr']


def hook_j5(c, t):
    """open mid-performance - five brothers, bright 1970 TV stage - and push hard into Michael's face"""
    u = ease_in(u_of(t, 0.0, A_FACE - 0.02), 2.4)
    (hx, hy), hr = j5_head(t)
    z0, z1 = 1.0, HEAD_R / hr
    z = z0 * (z1 / z0) ** u
    tx, ty = hx, hy + (H / 2 - EYE[1]) / z
    cam = Cam(0 + (tx - 0) * u, -420 + (ty + 420) * u, z, 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1a0a1a'))
    with Layer(c, cam, 1.0, t):
        j5_world(c, t)
    # TV-camera lens flare sweep + pulsing stage glare
    k = 0.5 + 0.5 * math.sin(t * 3)
    glow(c, W * (0.2 + 0.6 * u), H * 0.15, 260, '#ffe8c0', 0.25 * k)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.8, 0.5, 0.06 + 0.05 * T.env_at('snare', t)), blend=skia.BlendMode.kPlus))


# ----------------------------------------------------------------------------- 1982: alone with the photograph
def photo(c, rect, t_freeze, aged=1.0):
    """a 1970 snapshot of the Jackson 5 on stage (white border, faded colour)"""
    c.save()
    c.drawRect(rect.makeOutset(26, 26), paint('#f2ebdc'))
    c.drawRect(rect.makeOutset(26, 26), paint((0, 0, 0, 0.25), style='stroke', width=2))
    c.clipRect(rect)
    lp = skia.Paint()
    m = [0.8, 0.25, 0.1, 0, 0.04, 0.15, 0.75, 0.1, 0, 0.02, 0.1, 0.2, 0.6, 0, 0.0, 0, 0, 0, 1, 0]
    lp.setColorFilter(skia.ColorFilters.Matrix(m))
    c.saveLayer(rect, lp)
    c.translate(rect.centerX(), rect.bottom() - rect.height() * 0.22)
    s = rect.width() / 1350
    c.scale(s, s)
    j5_world(c, t_freeze, freeze=t_freeze)
    c.restore()
    c.drawRect(rect, shader_paint(rad_grad((rect.centerX(), rect.centerY()), rect.width() * 0.75,
                                           [(0, 0, 0, 0), (0.2, 0.1, 0.0, 0.35 * aged)])))
    c.restore()


def adult_face(c, t):
    """match cut: same eye line, but 1982 - a dark studio, one overhead light, a photograph of his younger self"""
    u = u_of(t, A_FACE, A_PHOTO)
    bg(c, ['#0c0a12', '#100c14', '#08060a'])
    for k in range(8):
        c.drawRect(skia.Rect.MakeXYWH(-60 + k * 150, 0, 110, H), paint((0.35, 0.25, 0.18, 0.12)))
    beam(c, W / 2, -100, W / 2, H, 60, 900, '#ffe2b0', 0.22, blur=50)
    particles(c, t, 40, (W * 0.2, 0, W * 0.6, H), 21, '#ffe8c0', size=(1.5, 4), speed=(4, 14))
    look = smoothstep(0.05, 0.35, u)
    P = base_pose(lsh=0.42, lel=-1.72, rsh=0.42, rel=-1.72, lhand='relaxed', rhand='relaxed', smile=0.12 + 0.12 * u,
                  brow=0.25 + 0.15 * look, ey=0.75 * look, hnod=0.012 * look, blink=0.0)
    P['blink'] = 1.0 if 0.62 < u < 0.68 else 0.0
    P['dip'] = 0.002 * math.sin(t * 2)
    h = (HEAD_R / K.DESIGNS[K.MJ].head) * (1 - 0.56 * ease_out(u, 2.2))
    head = (EYE[0], EYE[1] - 60 * ease_io(u))
    gx, gy = place_head(K.MJ, P, h, head)
    S = draw(c, K.MJ, gx, gy, h, P, K.O_STUDIO, L_STUDIO_DARK, t, shadow=False)
    (lx, ly), (rx, ry) = S['arms'][-1][2], S['arms'][1][2]
    pw = 0.26 * h
    rect = skia.Rect.MakeXYWH((lx + rx) / 2 - pw / 2, (ly + ry) / 2 - pw * 0.5, pw, pw * 0.72)
    c.save()
    c.rotate(-4, rect.centerX(), rect.centerY())
    photo(c, rect, 1.6)
    c.restore()
    for (wx, wy), sd in (((lx, ly), -1), ((rx, ry), 1)):          # thumbs over the photo edge
        c.drawOval(skia.Rect.MakeXYWH(wx - sd * 0.01 * h - 0.016 * h, wy - 0.03 * h, 0.032 * h, 0.05 * h), paint('#8a5a3c'))
        c.drawOval(skia.Rect.MakeXYWH(wx - sd * 0.01 * h - 0.016 * h, wy - 0.03 * h, 0.032 * h, 0.05 * h),
                   paint('#2a1418', style='stroke', width=3))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.4), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.6)])))


def photo_insert(c, t):
    """the photograph fills the frame - then it lowers, and behind it lies an unfinished song"""
    u = u_of(t, A_PHOTO, A_SHEET)
    sheet_world(c, t, blur=24 * (1 - smoothstep(0.55, 0.95, u)) + 2, cam_u=0.0)
    drop = ease_in(smoothstep(0.45, 1.0, u), 2.2)
    c.save()
    c.translate(0, drop * H * 0.95)
    c.rotate(-3 + 2 * u + 5 * drop, W / 2, H / 2)
    s = 1.0 + 0.06 * u
    pr = skia.Rect.MakeXYWH(W / 2 - 430 * s, H * 0.34 - 300 * s, 860 * s, 620 * s)
    c.drawRect(pr.makeOutset(40, 40).makeOffset(16, 28), paint((0, 0, 0, 0.5), blur=30))
    photo(c, pr, 1.6)
    sweep = (u * 1.4) % 1.4
    c.save()
    c.clipRect(pr)
    c.drawLine(pr.left() + sweep * pr.width() * 1.2 - 200, pr.top(), pr.left() + sweep * pr.width() * 1.2, pr.bottom(),
               paint((1, 1, 1, 0.18), style='stroke', width=90, blur=30))
    c.restore()
    for sd in (-1, 1):
        x = pr.centerX() + sd * (pr.width() / 2 + 6)
        th = smooth_path([(x - 40, pr.bottom() - 40), (x + 40 * -sd, pr.bottom() - 120), (x + 60 * -sd, pr.bottom() - 30),
                          (x + 20 * -sd, pr.bottom() + 140), (x - 70 * -sd, pr.bottom() + 180)], True, 0.5)
        c.drawPath(th, paint('#8a5a3c'))
        c.drawPath(th, paint('#2a1418', style='stroke', width=4))
    c.restore()


# ----------------------------------------------------------------------------- the unfinished sheet
NOTES = [(0, 3), (1, 5), (2, 4), (3, 6), (4, 2), (5, 4), (6, 7), (7, 5), (8, 3), (9, 6)]


def sheet_world(c, t, blur=0.0, cam_u=0.0, write_from=None):
    """top-down: manuscript paper on the piano lid - title 'Beat It', a few bars written, the rest still empty"""
    if blur > 0.5:
        lp = skia.Paint()
        lp.setImageFilter(skia.ImageFilters.Blur(blur, blur))
        c.saveLayer(None, lp)
    bg(c, ['#0a0608', '#150c0c', '#0a0608'])
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(-6 + 4 * cam_u)
    s = 1.0 + 0.18 * cam_u
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    c.drawRect(skia.Rect.MakeLTRB(-400, H * 0.08, W + 400, H * 0.95), shader_paint(lin_grad((0, 0), (W, H), ['#1a0e0a', '#2a1a12', '#140a08'])))
    for k in range(9):
        c.drawLine(-400, H * 0.12 + k * 210, W + 400, H * 0.1 + k * 210, paint((1, 0.9, 0.7, 0.04), style='stroke', width=40, blur=20))
    pr = skia.Rect.MakeXYWH(110, 470, 860, 1300)
    c.drawRect(pr.makeOffset(20, 30), paint((0, 0, 0, 0.6), blur=26))
    c.drawRect(pr, shader_paint(lin_grad((pr.left(), 0), (pr.right(), 0), ['#efe4cc', '#f8f0dc', '#e8dcc0'])))
    c.drawString('Beat It', pr.left() + 250, pr.top() + 130, font('garamond_i', 104), paint('#1a1210'))
    c.drawString('M.J.', pr.right() - 150, pr.top() + 200, font('garamond_i', 46), paint('#3a2a20'))
    ink = paint('#2a1e18', style='stroke', width=2.2)
    staves = [pr.top() + 300 + k * 230 for k in range(5)]
    nb = 0 if write_from is None else max(0, int((T.beat_at(t) - T.beat_at(write_from)) * 1.0) + 1)
    for si, sy in enumerate(staves):
        for l in range(5):
            c.drawLine(pr.left() + 50, sy + l * 20, pr.right() - 50, sy + l * 20, ink)
        for b in range(5):
            bx = pr.left() + 50 + b * (pr.width() - 100) / 4
            c.drawLine(bx, sy, bx, sy + 80, ink)
        if si == 0:
            c.drawString('♯', pr.left() + 58, sy + 64, font('garamond_b', 70), paint('#2a1e18'))
        written = 10 if si == 0 else (nb if si == 1 else 0)
        for i, (k, p) in enumerate(NOTES[:written]):
            nx = pr.left() + 140 + k * 74
            ny = sy + 80 - p * 10
            c.save()
            c.rotate(-20, nx, ny)
            c.drawOval(skia.Rect.MakeXYWH(nx - 13, ny - 9, 26, 18), paint('#1a1210'))
            c.restore()
            c.drawLine(nx + 11, ny, nx + 11, ny - 62, paint('#1a1210', style='stroke', width=3))
        if si >= 2:
            for q in range(3):        # pencil sketch marks - unfinished
                qx = pr.left() + 150 + q * 220 + si * 30
                c.drawLine(qx, sy + 30, qx + 60, sy + 14, paint((0.35, 0.3, 0.28, 0.35), style='stroke', width=3))
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.44), H * 0.62, [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0.75)], [0, 0.45, 1])))
    if blur > 0.5:
        c.restore()


def sheet(c, t):
    u = u_of(t, A_SHEET, A_DECIDE)
    sheet_world(c, t, cam_u=ease_io(u), write_from=A_SHEET + 0.05)
    # the pencil writes a note on every beat
    b = T.beat_at(t) - T.beat_at(A_SHEET + 0.05)
    i = int(clamp(b, 0, 9))
    f = b - math.floor(b)
    k, p = NOTES[i]
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(-6 + 4 * ease_io(u))
    s = 1.0 + 0.18 * ease_io(u)
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    nx = 110 + 140 + k * 74 + 20 * math.sin(f * math.pi)
    ny = 470 + 300 + 230 + 80 - p * 10 - 30 * math.sin(f * math.pi) - 10
    c.save()
    c.translate(nx, ny)
    c.rotate(-35)
    c.drawRect(skia.Rect.MakeXYWH(-10, -560, 20, 520), paint((0, 0, 0, 0.35), blur=14))
    c.drawPath(poly_path([(0, 0), (-12, -40), (12, -40)]), paint('#e8c8a0'))
    c.drawPath(poly_path([(0, 0), (-4, -12), (4, -12)]), paint('#2a2a2a'))
    c.drawRect(skia.Rect.MakeXYWH(-12, -520, 24, 480), paint('#e8b830'))
    c.drawRect(skia.Rect.MakeXYWH(-12, -540, 24, 24), paint('#c8c8c8'))
    c.restore()
    # his hand (pinch grip on the pencil) + striped sweater cuff
    c.save()
    c.translate(nx, ny)
    c.rotate(-35)
    skin, ln = '#8f5a3a', paint('#2a1418', style='stroke', width=4)
    c.drawPath(smooth_path([(-30, -200), (40, -230), (150, -170), (190, -40), (120, 40), (10, 0), (-20, -60)], True, 0.5),
               paint((0, 0, 0, 0.35), blur=20))
    hand = smooth_path([(-26, -110), (-10, -190), (60, -235), (150, -200), (185, -90), (130, -10), (40, -30), (8, -60)], True, 0.5)
    c.drawPath(hand, paint(skin))
    c.drawPath(hand, ln)
    for k in range(3):              # curled fingers
        c.drawArc(skia.Rect.MakeXYWH(-30 + k * 22, -150 + k * 26, 70, 50), 90, 160, False, ln)
    thumb = smooth_path([(14, -40), (-24, -52), (-30, -84), (6, -90), (40, -70)], True, 0.5)
    c.drawPath(thumb, paint(mix(skin, '#ffffff', 0.08)))
    c.drawPath(thumb, ln)
    c.drawRoundRect(skia.Rect.MakeXYWH(60, -560, 250, 330), 50, 50, paint('#d9c9a6'))
    for k in range(4):
        c.drawLine(70, -520 + k * 70, 300, -530 + k * 70, paint('#b8a47e', style='stroke', width=10))
    c.restore()
    c.restore()


def decide(c, t):
    """he looks up from the paper - and makes up his mind; the overhead light swells"""
    u = u_of(t, A_DECIDE, C_GEAR)
    bg(c, ['#0a080e', '#0e0a10', '#060408'])
    flick = 1.0 if not (8.22 < t < 8.36 or 8.42 < t < 8.48) else 0.45
    swell = 1 + 0.8 * smoothstep(8.6, 9.15, t)
    beam(c, W / 2, -100, W / 2, H, 80, 1000, '#ffe2b0', 0.2 * flick * swell, blur=50)
    c.drawRoundRect(skia.Rect.MakeXYWH(-60, H * 0.72, W + 120, 120), 30, 30, paint('#120a0a'))      # piano edge
    for k in range(22):
        c.drawRect(skia.Rect.MakeXYWH(-40 + k * 52, H * 0.72 + 40, 46, 120), paint('#efe8da'))
    for k in range(22):
        if k % 7 not in (2, 6):
            c.drawRect(skia.Rect.MakeXYWH(-10 + k * 52, H * 0.72 + 40, 28, 74), paint('#100c0c'))
    up = smoothstep(0.08, 0.4, u)
    P = base_pose(lsh=0.12, lel=-0.15, rsh=0.12, rel=-0.15, ey=0.7 * (1 - up) - 0.1 * up, brow=0.3 - 0.75 * up,
                  smile=0.1 + 0.25 * smoothstep(0.55, 0.85, u), hnod=0.014 * (1 - up), blink=0.0)
    P['blink'] = 1.0 if 0.3 < u < 0.34 else 0.0
    h = 2400 * (1 + 0.12 * ease_io(u))
    gx, gy = place_head(K.MJ, P, h, (W / 2, H * 0.4))
    draw(c, K.MJ, gx, gy, h, P, K.O_STUDIO, dict(L_STUDIO_DARK, amb_a=0.32 - 0.1 * up), t, shadow=False)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.38), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.55)])))
    if t > 8.9:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.92, 0.8, 0.5 * smoothstep(8.9, 9.18, t)), blend=skia.BlendMode.kPlus))


# ----------------------------------------------------------------------------- THE CHALLENGE
def gear(c, t):
    """the Thriller sessions: a 24-track machine rolling, VU needles dancing, a record spinning"""
    u = u_of(t, C_GEAR, C_ROOM)
    dx = 140 * ease_io(u)
    studio_room(c, t, window=False)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, 0.35)))
    tape_machine(c, W * 0.42 - dx, H * 0.47, 1.05, t, label='THRILLER SESSIONS 1982')
    for k in range(3):
        from bi_common import vu
        vu(c, W * 0.86 - dx * 1.3, H * 0.3 + k * 170, 70, T.env_at(['vocal', 'low', 'snare'][k], t))
    # foreground turntable (parallax)
    c.drawRoundRect(skia.Rect.MakeXYWH(-120 - dx * 2, H * 0.72, W + 300, 700), 40, 40, paint('#1c1414'))
    vinyl(c, W * 0.58 - dx * 2, H * 0.92, 470, (t - C_GEAR) * 200)
    c.drawLine(W * 0.98 - dx * 2, H * 0.72, W * 0.7 - dx * 2, H * 0.86, paint('#c8c8d0', style='stroke', width=16))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, H * 0.6), (0, H), [(0, 0, 0, 0), (0.05, 0.02, 0.0, 0.25)])))


def room_people(c, t, u, mj_h=1300):
    pass


def control_room(c, t):
    """Quincy Jones walks into the control room with an idea"""
    u = u_of(t, C_ROOM, C_PITCH)
    studio_room(c, t)
    for k, x in enumerate((90, 980)):      # gold records on the wall
        c.drawCircle(x, 1000, 70, paint('#d8b040'))
        c.drawCircle(x, 1000, 20, paint('#8a6a20'))
    gy = H * 0.86
    # Michael at the desk, turns toward the door
    turn = smoothstep(0.2, 0.55, u)
    Pm = pose(K.MJ, [(0, 'groove', dict(amp=0.3, arms=False))], t)
    Pm.update(hyaw=-0.45 * turn, ex=-0.7 * turn, tw=-0.25 * turn, smile=0.2 + 0.3 * smoothstep(0.6, 0.9, u), lsh=0.5, lel=-0.9,
              rsh=0.5, rel=-0.9)
    draw(c, K.MJ, W * 0.72, gy, 1300, Pm, K.O_STUDIO, K.L_STUDIO, t, shadow=False)
    # Quincy walks in from the left
    xq = W * (-0.12 + 0.46 * ease_io(u_of(t, C_ROOM - 0.15, C_ROOM + 1.35)))
    walking = t < C_ROOM + 1.25
    Pq = pose('quincy', [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))] if walking else [(0, 'beckon', dict(side=1))], t)
    if not walking:
        Pq.update(brow=0.2, smile=0.8, mshape='grin', mopen=0.3, ex=0.6, hyaw=0.3)
    Pq['smile'] = max(Pq['smile'], 0.7)
    draw(c, 'quincy', xq, gy, 1300 * 1.64 / 1.62, Pq, K.O_QUINCY, K.L_STUDIO, t, shadow=False)
    console(c, -260, W + 260, H * 0.69, 560, t)


def pitch(c, t):
    """two-shot: Quincy plays air guitar - 'a rock song' - and Michael's smile grows"""
    u = u_of(t, C_PITCH, C_DREAM)
    studio_room(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0.1, 0.05, 0.0, 0.25)))
    cam_s = 1.0 + 0.06 * ease_io(u)
    c.save()
    c.translate(W / 2, H * 0.5)
    c.scale(cam_s, cam_s)
    c.translate(-W / 2, -H * 0.5)
    gy = H * 1.12
    B = T.beat_at(t)
    air = smoothstep(0.3, 0.42, u)
    st = math.sin(B * math.pi * 2)
    Pq = pose('quincy', [(0, 'groove', dict(amp=0.5, arms=False))], t)
    Pq.update(hyaw=0.35, ex=0.5, tw=0.2, smile=0.95, mshape='grin', mopen=0.35 + 0.15 * abs(st), brow=0.35,
              rsh=0.55 * (1 - air) + 0.75 * air, rel=-1.2 * (1 - air) + (-1.55 + 0.35 * st) * air,
              lsh=1.0 * (1 - air) + 1.35 * air, lel=-0.6 * (1 - air) - 0.35 * air, rhand='open' if air < 0.5 else 'fist',
              lhand='open' if air < 0.5 else 'fist')
    hq = 1900 * 1.64 / 1.62
    qx, qy = place_head('quincy', Pq, hq, (W * 0.3, H * 0.4))
    draw(c, 'quincy', qx, qy, hq, Pq, K.O_QUINCY, K.L_STUDIO, t, shadow=False)
    grin = smoothstep(0.35, 0.8, u)
    Pm = pose(K.MJ, [(0, 'nod_slow', dict(look=-0.7))], t)
    Pm.update(smile=0.2 + 0.8 * grin, mshape='grin' if grin > 0.5 else 'smile', mopen=0.25 * grin, brow=0.4 - 0.4 * grin,
              tw=-0.2, hyaw=-0.35, lsh=0.3, lel=-0.5, rsh=0.3, rel=-0.5)
    mx, my = place_head(K.MJ, Pm, 1900, (W * 0.74, H * 0.42))
    draw(c, K.MJ, mx, my, 1900, Pm, K.O_STUDIO, K.L_STUDIO, t, shadow=False)
    c.restore()
    # light accents on the air-guitar strums
    if air > 0.5:
        glow(c, W * 0.25, H * 0.75, 220, '#ffb050', 0.25 * T.env_at('snare', t))


def dream(c, t):
    """eyes closed, he hears it: the studio dissolves into electric guitars, explosive light and an enormous crowd"""
    u = u_of(t, C_DREAM, C_MIC)
    beat = T.beat_at(t)
    studio_room(c, t)
    rr = W * 1.6 * ease_out(smoothstep(0.02, 0.4, u), 2)
    if rr > 1:
        p = skia.Path()
        p.addCircle(W / 2, H * 0.4, rr)
        c.save()
        c.clipPath(p, doAntiAlias=True)
        bg(c, ['#14041a', '#3a0a2a', '#120420'])
        for i in range(11):
            a = -70 + i * 14 + 8 * math.sin(t * 2 + i)
            beam(c, W / 2, H * 0.58, W / 2 + math.sin(math.radians(a)) * 2200, H * 0.58 - math.cos(math.radians(a)) * 2200, 10, 300,
                 ['#ff3a6a', '#ffd040', '#ffffff', '#ff7a2a'][i % 4], 0.28, blur=26)
        for sd in (-1, 1):                      # giant guitar silhouettes in neon
            c.save()
            c.translate(W / 2 + sd * 420, H * 0.42)
            c.rotate(sd * 28)
            g = smooth_path([(40, -70), (-40, -60), (-110, -110), (-200, -80), (-210, 0), (-230, 90), (-150, 140), (-40, 100),
                             (60, 110), (30, 40), (40, -10)], True, 0.45)
            neck = poly_path([(40, -14), (520, -10), (520, 10), (40, 14)])
            head = poly_path([(520, -16), (610, -30), (620, 20), (520, 16)])
            for pth in (g, neck, head):
                c.drawPath(pth, paint((1, 0.2, 0.35, 0.9), style='stroke', width=14, blur=8))
                c.drawPath(pth, paint((1, 0.75, 0.8, 1), style='stroke', width=4))
            for k in range(4):
                c.drawLine(-150, -12 + k * 8, 520, -9 + k * 6, paint((1, 0.8, 0.85, 0.5), style='stroke', width=1.5))
            c.drawRect(skia.Rect.MakeXYWH(-120, -40, 22, 80), paint((1, 0.6, 0.7, 0.9)))
            c.restore()
        for tb in (14.8, 15.67):                 # pyro bursts on the accents
            k = t - tb
            if 0 < k < 0.7:
                for j in range(24):
                    a = j / 24 * 2 * math.pi
                    r = 600 * ease_out(k / 0.7, 2)
                    glow(c, W / 2 + math.cos(a) * r, H * 0.62 + math.sin(a) * r * 0.6, 40, '#ffd060', 0.8 * (1 - k / 0.7))
                c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.8, 0.5, 0.35 * (1 - k / 0.25) if k < 0.25 else 0), blend=skia.BlendMode.kPlus))
        c.save()
        c.translate(W / 2, H * 0.68)
        crowd(c, t, 6, 1.0, '#0a0414', '#ff8ab0', width=2600, seed=31, y0=0, row_gap=110, scale0=0.9, beat_phase=beat)
        c.restore()
        c.restore()
        c.drawCircle(W / 2, H * 0.4, rr, paint((1, 0.8, 0.9, 0.5), style='stroke', width=6, blur=6))
    P = pose(K.MJ, [(0, 'groove', dict(amp=0.35, arms=False))], t)
    P.update(blink=1.0, smile=0.55 + 0.35 * u, mshape='smile', brow=0.3, htilt=-0.06, hnod=-0.008, lsh=0.2, lel=0.2, rsh=0.2, rel=0.2)
    h = 2600
    gx, gy = place_head(K.MJ, P, h, (W / 2, H * 0.42))
    draw(c, K.MJ, gx, gy, h, P, K.O_STUDIO, dict(K.L_STUDIO, rim='#ff7ab0', amb='#c87aa8', amb_a=0.25), t, shadow=False)


def to_mic(c, t):
    """the vocal booth: headphones on, he walks to the microphone - confident"""
    u = u_of(t, C_MIC, END)
    bg(c, ['#2a1c14', '#1a120c'])
    for k in range(16):
        x = -60 + k * 76
        c.drawRect(skia.Rect.MakeXYWH(x, 0, 58, H), shader_paint(lin_grad((x, 0), (x + 58, 0), ['#5a3e28', '#7a5434', '#4a301e'])))
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.78, W, H), shader_paint(lin_grad((0, H * 0.78), (0, H), ['#3a2a20', '#1a120c'])))
    beam(c, W * 0.45, -100, W * 0.45, H, 60, 700, '#ffe6b8', 0.25, blur=40)
    a = ease_io(u_of(t, C_MIC, C_MIC + 1.25))
    h = 950 + 1050 * a
    gy = H * 0.8 + H * 0.32 * a
    walking = a < 0.98
    P = pose(K.MJ, [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))] if walking else [(0, 'groove', dict(amp=0.4, arms=False))], t)
    P.update(hyaw=0.0, tw=0.0, smile=0.6 + 0.3 * a, brow=-0.3, headphones=True, ex=0.0)
    if not walking:
        P.update(lsh=1.2, lel=2.75, lhand='open', rsh=0.25, rel=-0.4)
    S = draw(c, K.MJ, W * 0.42, gy, h, P, K.O_STUDIO, K.L_STUDIO, t, shadow=True)
    hx, hy = S['head']
    r = S['hr']
    c.drawArc(skia.Rect.MakeXYWH(hx - r * 1.22, hy - r * 1.75, r * 2.44, r * 2.5), 195, 150, False,
              paint('#8a8a96', style='stroke', width=r * 0.16))
    for sd in (-1, 1):
        cup = skia.Rect.MakeXYWH(hx + sd * r * 1.08 - r * 0.24, hy - r * 0.25, r * 0.48, r * 0.62)
        c.drawRoundRect(cup, r * 0.18, r * 0.18, shader_paint(lin_grad((cup.left(), 0), (cup.right(), 0), ['#3a3a44', '#b8b8c4', '#2a2a30'])))
    mic_stand(c, W * 0.8, H * 0.5 - 140 * a, 1.0 + 0.6 * a)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W * 0.45, H * 0.45), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.5)])))


SHOTS = [(A_J5, hook_j5), (A_FACE, adult_face), (A_PHOTO, photo_insert), (A_SHEET, sheet), (A_DECIDE, decide),
         (C_GEAR, gear), (C_ROOM, control_room), (C_PITCH, pitch), (C_DREAM, dream), (C_MIC, to_mic)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    cap(c, t, 0.35, A_PHOTO + 0.55, ['THE WORLD KNEW HIM', 'AS A CHILD STAR…'], y=300, size=84)
    cap(c, t, A_SHEET - 0.1, C_GEAR - 0.12, ['BUT HE WAS ABOUT TO', 'CHANGE MUSIC FOREVER.'], y=300, size=84, accent=(1, (1.0, 0.82, 0.38)))
    cap(c, t, C_GEAR + 0.2, C_PITCH - 0.08, ['1982. ONE ALBUM.', 'ONE HUGE AMBITION.'], y=300, size=86)
    cap(c, t, C_PITCH + 0.12, C_MIC - 0.1, ['PRODUCER QUINCY JONES', 'WANTED A ROCK SONG.'], y=300, size=80)
