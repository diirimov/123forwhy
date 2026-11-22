"""0:29.9-0:42.0  THE DARING MUSIC VIDEO: 1983 Los Angeles, two rival groups converge on a warehouse, the film crew,
professional dancers beside real gang members, the red leather jacket under a spotlight, Michael puts it on."""
import math
import numpy as np
import skia
from bi_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, font, text_center, noise1, poly_path, smooth_path, T, K,
                       base_pose, pose, draw, place_head, skel, bg, u_of, cap, stamp, particles, la_street, silhouette,
                       Cam, Layer)

V_LA, V_FEET, V_CREW, V_LINE, V_JACKET, V_REACH, V_SWING = DB(17), DB(18), DB(19), DB(20), DB(21), DB(22), DB(23)
V_WEAR = DB(23) + HALF
END = DB(24)
GROUP_A = ['x0', 'x2', 'x8', 'x10']
GROUP_B = ['x1', 'x3', 'x9', 'x11']
L_WH = dict(key=(0.0, -1.0), amb='#8a7aa8', amb_a=0.3, rim='#ffe0b8', line='#120c14', floor_shadow=0.5)


def tense(P, k=1.0):
    P.update(brow=0.7 * k, smile=-0.25 * k, mshape='smile', mopen=0.0)
    return P


def walker(key, t, dirn, speed=0.1, t0=0.0):
    P = pose(key, [(0, 'walk', dict(start=T.beat_at(t0) - T.PHASE, dirn=dirn, speed=speed))], t)
    return tense(P)


# ----------------------------------------------------------------------------- street
def street(c, t):
    """1983, downtown LA at night: two groups walk out of opposite sides of the street toward one warehouse"""
    u = u_of(t, V_LA, V_FEET)
    la_street(c, t, cam_dx=-60 * ease_io(u))
    hz = H * 0.55
    for side, grp, outs in ((-1, GROUP_A, K.O_GROUP_A), (1, GROUP_B, K.O_GROUP_B)):
        for i, k in enumerate(grp):
            depth = [0.0, 0.6, 1.0, 1.5][i]
            gy = hz + 170 + depth * 190
            h = 520 + depth * 170
            x0 = W / 2 + side * (360 + i * 120)
            P = walker(k, t + i * 0.07, -side, speed=0.2, t0=V_LA)
            P['hyaw'] = -side * 0.2
            x = x0 + P['x'] * h * 0 - side * 0          # walk() carries x inside the pose
            draw(c, k, x, gy, h, P, outs[i % len(outs)], dict(K.L_STREET, rim='#ff5ab4' if side < 0 else '#5ae0ff'), t)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, H * 0.75), (0, H), [(0, 0, 0, 0), (0, 0, 0, 0.5)])))


def feet(c, t):
    """ground level: sneakers and boots stride through neon puddles - from both directions"""
    u = u_of(t, V_FEET, V_CREW)
    bg(c, ['#0a0814', '#140e22', '#0a0a12'])
    gy = H * 0.86
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.62, W, H), shader_paint(lin_grad((0, H * 0.62), (0, H), ['#1a1224', '#0a080e'])))
    for x, col in ((W * 0.2, '#ff4ab4'), (W * 0.75, '#4ae0ff'), (W * 0.5, '#ffb04a')):
        for k in range(10):
            yy = H * 0.66 + k * 34
            c.drawRect(skia.Rect.MakeXYWH(x - 160 + 20 * math.sin(t * 4 + k), yy, 320 - k * 12, 14),
                       paint(alpha(col, 0.3 * (1 - k / 11)), blur=8, blend=skia.BlendMode.kPlus))
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.3, W, H * 0.66), shader_paint(lin_grad((0, 0), (W, 0), ['#ff3aa0', '#7a2a9a', '#2ad0ff'])))
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.3, W, H * 0.66), shader_paint(lin_grad((0, H * 0.3), (0, H * 0.66), [(0.04, 0.02, 0.08, 0.9), (0, 0, 0, 0.1), (0.04, 0.02, 0.08, 0.4)])))
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.62, W, H), shader_paint(lin_grad((0, H * 0.62), (0, H), [(0.6, 0.2, 0.6, 0.35), (0.05, 0.03, 0.08, 0.0)]),
                                                               ))
    glow(c, W * 0.5, H * 0.6, 700, '#ff7ad0', 0.25)
    for j, (k, dirn, x0, out, dly) in enumerate((('x8', 1, -500, K.O_GROUP_A[2], 0.2), ('x0', 1, -100, K.O_GROUP_A[0], 0.0),
                                                ('x1', -1, W + 100, K.O_GROUP_B[0], 0.35))):
        h = 3000 if j > 0 else 2300
        P = pose(k, [(0, 'walk', dict(start=T.beat_at(V_FEET) - T.PHASE, dirn=dirn, speed=0.12))], t + dly)
        P['hyaw'] = 0.3 * dirn
        gj = gy + (0 if j > 0 else -120)
        halo = (1, 0.5, 0.85, 0.9) if dirn > 0 else (0.5, 0.95, 1, 0.9)
        from world import floor_reflection
        fig = lambda k=k, x0=x0, gj=gj, h=h, P=P, out=out: draw(c, k, x0, gj, h, P, out, K.L_STREET, t, shadow=False)
        floor_reflection(c, lambda: silhouette(c, fig, color=(0.03, 0.02, 0.05, 1)), gj, 0.35)
        silhouette(c, fig, color=(0.03, 0.02, 0.05, 1), halo=halo, halo_blur=12)
        # splash rings where a heel lands
        S = skel(k, x0, gy, h, P)
        for fk in ('lfoot', 'rfoot'):
            fx, fy = S[fk]
            if fy > gy - 8:
                ph = (T.beat_at(t) % 1)
                c.drawOval(skia.Rect.MakeXYWH(fx - 120 * (0.5 + ph), gy - 16 * (0.5 + ph), 240 * (0.5 + ph), 32 * (0.5 + ph)),
                           paint((0.8, 0.9, 1.0, 0.4 * (1 - ph)), style='stroke', width=4))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.7), H * 0.6, [(0, 0, 0, 0), (0, 0, 0, 0.55)])))


# ----------------------------------------------------------------------------- warehouse set
def warehouse(c, t, dx=0.0, smoke=1.0):
    """interior: brick, steel columns, high windows with shafts of light, hanging work lamps, haze"""
    bg(c, ['#1a1216', '#120c10', '#0a0608'])
    c.save()
    c.translate(-dx, 0)
    for j in range(60):
        for k in range(-6, 26):
            off = 25 if j % 2 else 0
            c.drawRect(skia.Rect.MakeXYWH(-300 + off + k * 50, 120 + j * 22, 48, 20),
                       paint((0.35 + 0.05 * math.sin(j * 3.1 + k), 0.16, 0.12, 0.35)))
    for k in range(5):
        x = -200 + k * 420
        c.drawRect(skia.Rect.MakeXYWH(x, 0, 60, H), paint('#141014'))
        c.drawRect(skia.Rect.MakeXYWH(x + 6, 0, 10, H), paint((1, 1, 1, 0.06)))
        c.drawRect(skia.Rect.MakeXYWH(x + 120, 160, 200, 300), paint('#3a4a6a'))
        for g in range(3):
            c.drawLine(x + 120, 160 + g * 100, x + 320, 160 + g * 100, paint('#141014', style='stroke', width=8))
        beam(c, x + 220, 300, x + 520, H * 0.9, 120, 380, '#c8d0ff', 0.1 * smoke, blur=40)
    c.restore()
    for k in range(4):           # swinging work lamps
        x = W * (0.15 + 0.24 * k) - dx * 1.2
        sw = 30 * math.sin(t * 1.3 + k)
        c.drawLine(x, 0, x + sw, 380, paint('#0a0a0a', style='stroke', width=4))
        c.drawPath(poly_path([(x + sw - 50, 410), (x + sw + 50, 410), (x + sw + 20, 370), (x + sw - 20, 370)]), paint('#2a2a2a'))
        glow(c, x + sw, 420, 90, '#ffd890', 0.6)
        beam(c, x + sw, 410, x + sw * 3, H * 0.9, 40, 340, '#ffd890', 0.07, blur=30)
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.74, W, H), shader_paint(lin_grad((0, H * 0.74), (0, H), ['#2a2024', '#0e0a0c'])))
    for k in range(3):
        y = H * (0.55 + 0.1 * k)
        c.drawOval(skia.Rect.MakeXYWH(-300 + 200 * math.sin(t * 0.3 + k) - dx * 0.5, y - 120, W + 600, 240),
                   paint((0.7, 0.7, 0.8, 0.07 * smoke), blur=60))


def film_camera(c, x, y, s, t):
    """a 1980s 35mm cine camera on a dolly"""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-30, 0, 60, 520), paint('#1a1a1e'))
    c.drawRoundRect(skia.Rect.MakeXYWH(-220, 520, 440, 90), 20, 20, paint('#2a2a30'))
    for k in (-160, 160):
        c.drawCircle(k, 640, 50, paint('#141418'))
        c.drawCircle(k, 640, 18, paint('#5a5a66'))
    c.drawRoundRect(skia.Rect.MakeXYWH(-170, -160, 300, 180), 20, 20, paint('#24242a'))
    c.drawCircle(-60, -250, 110, paint('#1c1c22'))
    c.drawCircle(60, -250, 110, paint('#1c1c22'))
    reel_a = t * 200
    for cx in (-60, 60):
        c.drawCircle(cx, -250, 80, paint('#2a2a32'))
        a = math.radians(reel_a)
        c.drawLine(cx, -250, cx + math.cos(a) * 70, -250 + math.sin(a) * 70, paint('#4a4a56', style='stroke', width=8))
    c.drawRect(skia.Rect.MakeXYWH(-340, -120, 170, 100), paint('#2a2a30'))
    c.drawRect(skia.Rect.MakeXYWH(-420, -150, 80, 160), paint('#141418'))
    c.drawCircle(-340, -70, 34, paint((0.4, 0.5, 0.9, 0.5)))
    glow(c, 90, -120, 20, '#ff3a2a', 0.8 if (t * 2) % 1 < 0.6 else 0.2)
    c.restore()


def light_stand(c, x, y, s, aim_x, aim_y, on=1.0):
    c.drawLine(x, y, x, y - 700 * s, paint('#1a1a1e', style='stroke', width=12 * s))
    for k in (-1, 0, 1):
        c.drawLine(x, y, x + k * 120 * s, y + 60 * s, paint('#1a1a1e', style='stroke', width=10 * s))
    hx, hy = x, y - 720 * s
    c.drawRoundRect(skia.Rect.MakeXYWH(hx - 90 * s, hy - 80 * s, 180 * s, 160 * s), 20 * s, 20 * s, paint('#2a2a30'))
    glow(c, hx, hy, 130 * s, '#fff0d0', 0.8 * on)
    beam(c, hx, hy, aim_x, aim_y, 60 * s, 380 * s, '#fff0d0', 0.12 * on, blur=40)


def clapper(c, x, y, s, t, snap_t):
    k = clamp((t - (snap_t - 0.25)) / 0.25)
    ang = -28 * (1 - ease_in(k, 2))
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(-6)
    c.drawRect(skia.Rect.MakeXYWH(-230, 0, 460, 300), paint('#141414'))
    c.drawRect(skia.Rect.MakeXYWH(-230, 0, 460, 300), paint('#e8e4dc', style='stroke', width=6))
    f = font('spartan_b', 40)
    c.drawString('BEAT IT', -200, 70, f, paint('#f4f0e8'))
    c.drawString('SCENE 1', -200, 150, font('spartan_b', 32), paint('#f4f0e8'))
    c.drawString('TAKE 1', 40, 150, font('spartan_b', 32), paint('#f4f0e8'))
    c.drawString('LOS ANGELES 1983', -200, 240, font('spartan_b', 30), paint('#f4f0e8'))
    c.save()
    c.rotate(ang, -230, 0)
    c.drawRect(skia.Rect.MakeXYWH(-230, -60, 460, 56), paint('#141414'))
    for k_ in range(6):
        c.drawPath(poly_path([(-230 + k_ * 80, -60), (-190 + k_ * 80, -60), (-230 + k_ * 80 + 80, -4), (-270 + k_ * 80 + 80, -4)]),
                   paint('#f4f0e8'))
    c.restore()
    c.restore()
    if 0 <= t - snap_t < 0.12:
        glow(c, x, y, 200 * s, '#ffffff', 0.7)


def crew(c, t):
    """the film crew prepares: camera on a dolly, lights on stands, the slate snaps on the beat"""
    u = u_of(t, V_CREW, V_LINE)
    warehouse(c, t, dx=80 * ease_io(u))
    light_stand(c, W * 0.12, H * 0.82, 1.0, W * 0.55, H * 0.8)
    light_stand(c, W * 0.92, H * 0.8, 0.9, W * 0.45, H * 0.85, on=smoothstep(V_CREW + 0.2, V_CREW + 0.35, t))
    for i, (k, x) in enumerate((('x4', W * 0.13), ('x5', W * 0.8), ('x6', W * 0.95))):
        P = pose(k, [(0, 'groove', dict(amp=0.2, arms=False))], t + i)
        if i == 0:
            P.update(rsh=1.6, rel=-0.2, rhand='point', hyaw=0.3, ex=0.5)        # director points at the marks
        if i == 1:
            P.update(lsh=0.6, lel=-1.8, rsh=0.6, rel=-1.8, headphones=True)    # sound
        draw(c, k, x, H * 0.84, 820, P, K.O_CREW, L_WH, t)
    film_camera(c, W * 0.4 - 40 * ease_io(u), H * 0.6, 0.95, t)
    clapper(c, W * 0.72, H * 0.37 + 60 * (1 - ease_out(smoothstep(V_CREW, V_CREW + 0.35, t), 2)), 0.8, t, V_CREW + 2 * BEAT)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.55), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.5)])))


def lineup(c, t):
    """professional dancers stand shoulder to shoulder with real gang members; lights sweep, shadows cross the wall"""
    u = u_of(t, V_LINE, V_JACKET)
    dx = 260 * ease_io(u)
    warehouse(c, t, dx=dx * 0.5)
    sweep = W * (-0.3 + 1.6 * u)
    beam(c, sweep, -100, sweep + 200, H, 80, 500, '#ffffff', 0.18, blur=40)
    order = ['x2', 'x0', 'x3', 'x1', 'x12', 'x8', 'x13', 'x9']
    outs = [K.O_DANCERS[0], K.O_GROUP_A[0], K.O_DANCERS[1], K.O_GROUP_B[0], K.O_DANCERS[2], K.O_GROUP_A[2], K.O_DANCERS[3],
            K.O_GROUP_B[2]]
    gy = H * 0.86
    for i, (k, o) in enumerate(zip(order, outs)):
        x = -120 + i * 250 - dx
        P = pose(k, [(0, 'arms_folded' if i % 3 == 1 else 'stare', {})], t + i * 0.3)
        tense(P, 0.8)
        P['ex'] = 0.3 * math.sin(t * 0.8 + i)
        P['dip'] = 0.003 * math.sin(t * 1.6 + i)
        # the sweeping light pushes a long shadow across the bricks
        lx = sweep - x
        c.save()
        c.translate(x - lx * 0.4, 0)
        c.skew(-lx / 2000, 0)
        silhouette(c, lambda: draw(c, k, 0, gy - 140, 1150, P, o, L_WH, t, shadow=False), color=(0, 0, 0, 0.45))
        c.restore()
        lit = 0.15 + 0.85 * math.exp(-((x - sweep) / 380) ** 2)
        draw(c, k, x, gy, 1150, P, o, dict(L_WH, amb_a=0.55 - 0.3 * lit, rim='#ffffff' if lit > 0.5 else '#c8b0ff'), t)


def jacket_shape(c, x, y, s, sway=0.0, t=0.0, open_=1.0):
    """the red zippered leather jacket on a hanger"""
    c.save()
    c.translate(x, y)
    c.rotate(sway)
    c.scale(s, s)
    c.drawPath(smooth_path([(-10, -170), (-30, -210), (0, -240), (30, -215)], False, 0.5), paint('#c8c8d0', style='stroke', width=8))
    c.drawLine(-230, -60, 0, -150, paint('#5a3a20', style='stroke', width=18))
    c.drawLine(230, -60, 0, -150, paint('#5a3a20', style='stroke', width=18))
    red = shader_paint(lin_grad((-260, 0), (260, 0), ['#7a0a10', '#c4141c', '#e8303a', '#a00e16', '#6a080c']))
    ol = paint('#2a0606', style='stroke', width=6)
    for sd in (-1, 1):
        sl = smooth_path([(sd * 200, -80), (sd * 280, -20), (sd * 300, 300), (sd * 290, 560), (sd * 210, 570), (sd * 200, 300),
                          (sd * 180, 40)], True, 0.4)
        c.drawPath(sl, red)
        c.drawPath(sl, ol)
        for k in range(3):
            c.drawLine(sd * 205, 0 + k * 40, sd * 285, 10 + k * 40, paint((0.3, 0.02, 0.04, 0.7), style='stroke', width=5))
        c.drawLine(sd * 250, 280, sd * 255, 520, paint('#e0e0e8', style='stroke', width=6))
    body = smooth_path([(-200, -90), (-60, -130), (0, -110), (60, -130), (200, -90), (215, 200), (205, 470), (0, 490), (-205, 470),
                        (-215, 200)], True, 0.35)
    c.drawPath(body, red)
    c.save()
    c.clipPath(body, doAntiAlias=True)
    c.drawPath(poly_path([(-40 * open_, -110), (40 * open_, -110), (70 * open_, 500), (-70 * open_, 500)]), paint('#120a0c'))
    for k in range(6):
        y_ = -40 + k * 34
        c.drawLine(-200, y_, -60, y_ - 6, paint((0.3, 0.02, 0.04, 0.6), style='stroke', width=5))
        c.drawLine(60, y_ - 6, 200, y_, paint((0.3, 0.02, 0.04, 0.6), style='stroke', width=5))
    for sd in (-1, 1):
        for k in range(2):
            a, b = (sd * 80, 200 + k * 110), (sd * 170, 160 + k * 110)
            c.drawLine(*a, *b, paint('#e0e0e8', style='stroke', width=7))
            c.drawCircle(*b, 9, paint('#f4f4f8'))
        c.drawLine(sd * 40 * open_, -110, sd * 70 * open_, 490, paint('#e0e0e8', style='stroke', width=6))
    c.drawRect(skia.Rect.MakeXYWH(-220, 420, 440, 70), paint((0.2, 0.0, 0.02, 0.5)))
    c.restore()
    c.drawPath(body, ol)
    for sd in (-1, 1):
        col = smooth_path([(sd * 10, -125), (sd * 120, -140), (sd * 150, -60), (sd * 45 * open_ + sd * 10, 60)], True, 0.3)
        c.drawPath(col, paint('#a00e16'))
        c.drawPath(col, ol)
    rng = np.random.default_rng(3)
    for k in range(14):        # glints on the zips
        gx, gy = rng.uniform(-220, 220), rng.uniform(-80, 480)
        tw = 0.5 + 0.5 * math.sin(t * 6 + k * 2)
        glow(c, gx, gy, 14 * tw, '#ffffff', 0.5 * tw)
    c.restore()


def jacket(c, t):
    """the red leather jacket waits under a single spotlight"""
    u = u_of(t, V_JACKET, V_REACH)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#08060a'))
    beam(c, W / 2, -200, W / 2, H * 0.86, 60, 620, '#fff0dc', 0.32, blur=50)
    c.drawOval(skia.Rect.MakeXYWH(W / 2 - 420, H * 0.84, 840, 120), paint((1, 0.95, 0.85, 0.25), blur=30))
    c.drawLine(-100, H * 0.27, W + 100, H * 0.27, paint('#3a3a42', style='stroke', width=14))       # clothes rail
    particles(c, t, 60, (W * 0.25, 0, W * 0.5, H * 0.85), 13, '#fff0dc', size=(1.5, 4), speed=(5, 18))
    s = 1.25 + 0.3 * ease_io(u)
    jacket_shape(c, W / 2, H * 0.27 + 240 * s, s, sway=2.5 * math.sin(t * 1.4), t=t)
    c.drawRoundRect(skia.Rect.MakeXYWH(W / 2 + 150 * s, H * 0.27 + 110 * s, 110, 60), 8, 8, paint('#efe8d8'))
    c.drawString('M.J.', W / 2 + 150 * s + 18, H * 0.27 + 110 * s + 44, font('garamond_i', 40), paint('#2a1a12'))


def reach(c, t):
    """Michael steps out of the dark into the spotlight and reaches for it"""
    u = u_of(t, V_REACH, V_SWING)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#08060a'))
    beam(c, W * 0.62, -200, W * 0.55, H * 0.9, 60, 700, '#fff0dc', 0.28, blur=50)
    walk_u = ease_io(u_of(t, V_REACH, V_REACH + 1.1))
    h = 1000 + 500 * walk_u
    gy = H * 0.74 + H * 0.16 * walk_u
    walking = walk_u < 0.98
    P = pose(K.MJ, [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))], t)
    P.update(hyaw=0.25, tw=0.15, ex=0.6, brow=-0.35, smile=0.15)
    reach_k = ease_out(smoothstep(V_REACH + 1.0, V_REACH + 1.5, t), 2)
    if not walking:
        P.update(lfx=-0.08, rfx=0.08, lfy=0, rfy=0, dip=0.0)
    P.update(rsh=P['rsh'] * (1 - reach_k) + 1.55 * reach_k, rel=P['rel'] * (1 - reach_k) + 0.05 * reach_k,
             rhand='open' if reach_k < 0.9 else 'fist')
    mx = W * 0.27
    S = skel(K.MJ, mx, gy, h, P)
    wx, wy = S['arms'][1][2]
    jx, jy = W * 0.66, H * 0.34
    if reach_k > 0.9:          # once grabbed, the jacket follows his hand
        jx, jy = wx + 40, wy + 120
    def fig():
        draw(c, K.MJ, mx, gy, h, P, K.O_TEE, dict(K.L_DARK, rim='#fff0dc', key=(0.9, -0.4)), t, shadow=False)
    fig()
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (W, 0), [(0, 0, 0, 0.55), (0, 0, 0, 0.0), (0, 0, 0, 0.0)],
                                                             [0, 0.55, 1])))
    jacket_shape(c, jx, jy + 300, 1.05, sway=3 * math.sin(t * 1.4), t=t)


def swing(c, t):
    """one fluid move: the jacket swings round his back and onto his shoulders"""
    u = u_of(t, V_SWING, V_WEAR)
    warehouse(c, t, smoke=1.4)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, 0.35)))
    beam(c, W / 2, -200, W / 2, H, 60, 700, '#fff0dc', 0.25, blur=50)
    k = ease_io(u)
    P = base_pose(lsh=0.6 + 1.6 * math.sin(math.pi * k), lel=0.2, rsh=0.6 + 1.6 * math.sin(math.pi * k), rel=0.2,
                  lhand='fist', rhand='fist', brow=-0.4, smile=0.2, htilt=-0.08 * math.sin(math.pi * k), ey=-0.3)
    h = 1900
    gx, gy = place_head(K.MJ, P, h, (W / 2, H * 0.34))
    a = -170 + 170 * k               # jacket arcs from his right, over the head, onto the shoulders
    rr = 520 * (1 - k)
    jx = W / 2 + math.cos(math.radians(a)) * rr
    jy = H * 0.34 + 360 + math.sin(math.radians(a)) * rr * 0.6
    behind = k < 0.55
    if behind:
        lp = skia.Paint()
        lp.setImageFilter(skia.ImageFilters.Blur(18 * (1 - k), 4))
        c.saveLayer(None, lp)
        jacket_shape(c, jx, jy, 1.25, sway=-40 * (1 - k), t=t)
        c.restore()
    draw(c, K.MJ, gx, gy, h, P, K.O_TEE if k < 0.8 else K.O_BEATIT, dict(K.L_DARK, rim='#fff0dc'), t, shadow=False)
    if not behind and k < 0.8:
        jacket_shape(c, jx, jy, 1.25 * (1 - 0.2 * k), sway=-20 * (1 - k), t=t)
    if 0.72 < k < 0.88:
        glow(c, W / 2, H * 0.45, 600, '#ff6a5a', 0.4 * (1 - abs(k - 0.8) / 0.08))


def wear(c, t):
    """close: both hands snap the collar; chin down, eyes up into the lens"""
    u = u_of(t, V_WEAR, END)
    warehouse(c, t, smoke=1.6)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, 0.4)))
    beam(c, W / 2, -200, W / 2, H, 80, 900, '#ffe0d0', 0.28, blur=60)
    snap = ease_out(smoothstep(V_WEAR, V_WEAR + 0.25, t), 3)
    P = base_pose(lsh=0.5 + 0.1 * snap, lel=-2.35, rsh=0.5 + 0.1 * snap, rel=-2.35, lhand='fist', rhand='fist',
                  brow=-0.6, smile=0.05 + 0.3 * smoothstep(0.5, 0.9, u), hnod=0.01, ey=-0.65, blink=0.0)
    h = 2600 * (1 + 0.08 * ease_io(u))
    gx, gy = place_head(K.MJ, P, h, (W / 2, H * 0.42))
    draw(c, K.MJ, gx, gy, h, P, K.O_BEATIT, dict(K.L_DARK, rim='#ff7a6a', amb_a=0.2), t, shadow=False)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.42), H * 0.7, [(0, 0, 0, 0), (0, 0, 0, 0.55)])))


SHOTS = [(V_LA, street), (V_FEET, feet), (V_CREW, crew), (V_LINE, lineup), (V_JACKET, jacket), (V_REACH, reach),
         (V_SWING, swing), (V_WEAR, wear)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    stamp(c, t, V_LA + 0.15, V_CREW - 0.1, '1983 · LOS ANGELES', y=330, size=46)
    cap(c, t, V_CREW + 0.2, V_REACH - 0.1, ['REAL GANG MEMBERS.', 'ONE MESSAGE:', 'STOP THE VIOLENCE.'], y=290, size=80,
        accent=(2, (1.0, 0.42, 0.38)))
