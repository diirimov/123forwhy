"""0:42.0-1:00  THE LEGEND IS BORN (entrance in the red jacket, the synchronised dance from three angles, the impact:
TVs, kids at home, record stores, No. 1) and THE EMOTIONAL ENDING (the concert, his hands - the boy's hands - the reveal)."""
import math
import numpy as np
import skia
from bi_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, font, text_center, noise1, poly_path, smooth_path, T, K,
                       base_pose, pose, draw, place_head, skel, bg, u_of, cap, particles, silhouette, crowd, tv_set,
                       beatit_screen, Cam, Layer, GOLD)
from bi_act3 import warehouse
import scene4

L_DOOR, L_FRONT, L_SIDE, L_CLOSE, I_TV = DB(24), DB(25), DB(26), DB(27), DB(28)
I_KIDS = DB(28) + HALF
I_STORE, I_CHART, E_STAGE, E_HANDS, E_RISE, END = DB(29), DB(30), DB(31), DB(32), DB(33), 60.0
DANCERS = ['x2', 'x3', 'x12', 'x13', 'x4', 'x5', 'x14', 'x15']
D_OUT = [K.O_DANCERS[i % len(K.O_DANCERS)] for i in range(8)]
L_PAY = dict(key=(-0.2, -0.95), amb='#c8b0e0', amb_a=0.18, rim='#ffe8d8', line='#140c12', floor_shadow=0.5)


def routine(t0):
    """the shared, beat-locked phrase every dancer hits together (Michael adds his own accents on top)"""
    return [(t0 - 0.3, 'point_hit', dict(start=T.beat_at(t0) - T.PHASE, side=1)),
            (t0 + BEAT * 0.95, 'step_touch', dict(width=0.06)),
            (t0 + BEAT * 2, 'kick', dict(side=1)),
            (t0 + BEAT * 2.95, 'point_hit', dict(start=T.beat_at(t0 + 3 * BEAT) - T.PHASE, side=-1)),
            (t0 + BEAT * 4, 'arm_roll', {}),
            (t0 + BEAT * 5, 'kick', dict(side=-1)),
            (t0 + BEAT * 6, 'shimmy', {}),
            (t0 + BEAT * 6.95, 'point_hit', dict(start=T.beat_at(t0 + 7 * BEAT) - T.PHASE, side=1)),
            (t0 + BEAT * 8, 'step_touch', dict(width=0.06)),
            (t0 + BEAT * 9, 'kick', dict(side=1)),
            (t0 + BEAT * 10, 'arm_roll', {}),
            (t0 + BEAT * 10.95, 'point_hit', dict(start=T.beat_at(t0 + 11 * BEAT) - T.PHASE, side=-1))]


def fierce(P):
    P.update(brow=-0.45, smile=0.15, mshape='smile')
    return P


# ----------------------------------------------------------------------------- THE LEGEND IS BORN
def door(c, t):
    """the warehouse doors glow; dancers wait in two lines; his silhouette walks out of the light"""
    u = u_of(t, L_DOOR, L_FRONT)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a080c'))
    dr = skia.Rect.MakeLTRB(W * 0.22, H * 0.18, W * 0.78, H * 0.72)
    dim = 0.55 if 43.45 < t < L_FRONT else 1.0
    c.drawRect(dr, shader_paint(rad_grad((W / 2, H * 0.55), H * 0.5, ['#fff8ec', '#ffd8b0', '#c86a4a'])))
    c.drawRect(dr, paint((0, 0, 0, 1 - dim)))
    for k in range(9):
        c.drawLine(dr.left(), dr.top() + k * 110, dr.right(), dr.top() + k * 110, paint((0.3, 0.2, 0.2, 0.5), style='stroke', width=6))
    c.drawRect(dr, paint('#1a1214', style='stroke', width=40))
    beam(c, W / 2, H * 0.45, W / 2, H * 1.1, 400, 1400, '#fff0dc', 0.22 * dim, blur=60)
    for k in range(4):
        c.drawOval(skia.Rect.MakeXYWH(-200 + 200 * math.sin(t * 0.5 + k), H * (0.5 + 0.1 * k), W + 400, 300),
                   paint((0.9, 0.85, 0.85, 0.08 * dim), blur=60))
    # Michael's silhouette walks out of the light toward us
    a = ease_io(u_of(t, L_DOOR, L_DOOR + 1.45))
    h = 520 + 380 * a
    gy = H * 0.72 + H * 0.06 * a
    P = pose(K.MJ, [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))], t)
    P.update(hyaw=0, tw=0)
    silhouette(c, lambda: draw(c, K.MJ, W / 2, gy, h, P, K.O_BEATIT, L_PAY, t, shadow=False), color=(0.06, 0.02, 0.03, 1),
               halo=(1, 0.85, 0.7, 0.8), halo_blur=16)
    # two lines of dancers wait (backs to us), framing the door
    for i in range(4):
        for sd in (-1, 1):
            k = DANCERS[i * 2 + (sd > 0)]
            x = W / 2 + sd * (300 + i * 170)
            gy_ = H * 0.8 + i * 120
            hh = 700 + i * 220
            P = pose(k, [(0, 'arms_folded', {})], t + i)
            P['spin'] = 0.5
            silhouette(c, lambda: draw(c, k, x, gy_, hh, P, D_OUT[i], L_PAY, t, shadow=False), color=(0.04, 0.02, 0.04, 1),
                       halo=(1, 0.8, 0.6, 0.4), halo_blur=8)


def formation(c, t, cam, pos, h0, routine_t0, mj_extra=None, mj_out=K.O_BEATIT, L=L_PAY):
    """draw the dance company in world coords: pos = list of (x, depth) incl. Michael at index 0"""
    items = []
    for i, (x, z) in enumerate(pos):
        key = K.MJ if i == 0 else DANCERS[(i - 1) % len(DANCERS)]
        out = mj_out if i == 0 else D_OUT[(i - 1) % len(D_OUT)]
        sched = routine(routine_t0) if (i > 0 or mj_extra is None) else mj_extra
        items.append((z, key, x, out, sched, i))
    for z, key, x, out, sched, i in sorted(items):
        P = pose(key, sched, t, ripple=0.0)
        fierce(P)
        hh = h0 * z * (K.DESIGNS[key].height / 1.62)
        draw(c, key, x, -(1 - z) * 420, hh, P, out, L, t)


def stage_floor(c, t):
    c.drawRect(skia.Rect.MakeLTRB(-2400, -2600, 2400, -300), shader_paint(lin_grad((0, -2600), (0, -300), ['#0a060c', '#2a1420'])))
    for k in range(-6, 7):
        x = k * 380
        beam(c, x, -1800, x * 0.4, 200, 30, 360, ['#ffffff', '#ff6a5a', '#ffd8a0'][k % 3], 0.14 + 0.1 * T.env_at('snare', t), blur=40)
    c.drawRect(skia.Rect.MakeLTRB(-2400, -320, 2400, 1400), shader_paint(lin_grad((0, -320), (0, 900), ['#3a2428', '#140a0e'])))
    for k in range(-14, 15):
        c.drawLine(k * 160, -320, k * 600, 1400, paint((0, 0, 0, 0.25), style='stroke', width=3))
    for k in range(3):
        c.drawOval(skia.Rect.MakeXYWH(-1600 + 300 * math.sin(t * 0.4 + k), -500 + k * 200, 3200, 300), paint((0.8, 0.75, 0.8, 0.08), blur=60))


def front(c, t):
    """THE HIT: everyone strikes on the same downbeat - Michael at the point of a V"""
    u = u_of(t, L_FRONT, L_SIDE)
    cam = Cam(0, -520, 0.82 + 0.12 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a060a'))
    with Layer(c, cam, 1.0, t):
        stage_floor(c, t)
        pos = [(0, 1.0), (-330, 0.86), (330, 0.86), (-640, 0.74), (640, 0.74), (-930, 0.64), (930, 0.64), (-1200, 0.56), (1200, 0.56)]
        mj = routine(L_FRONT)
        formation(c, t, cam, pos, 980, L_FRONT, mj_extra=mj)
    k = 1 - smoothstep(L_FRONT, L_FRONT + 0.25, t)
    if k > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.9, 0.85, 0.6 * k), blend=skia.BlendMode.kPlus))


def side(c, t):
    """low 3/4 angle tracking along the line: synchronised kicks; Michael spins and rises onto his toes"""
    u = u_of(t, L_SIDE, L_CLOSE)
    cam = Cam(-260 + 420 * ease_io(u), -600, 1.05, -4)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a060a'))
    with Layer(c, cam, 0.6, t):
        warehouse(c, t, dx=0, smoke=1.2)
    with Layer(c, cam, 1.0, t):
        c.drawRect(skia.Rect.MakeLTRB(-2400, -330, 2400, 1400), shader_paint(lin_grad((0, -330), (0, 900), ['#3a2428', '#140a0e'])))
        pos = [(0, 1.0)] + [(-300 - i * 230, 1.0 - i * 0.08) for i in range(4)] + [(300 + i * 260, 1.06 + i * 0.04) for i in range(2)]
        mj = routine(L_FRONT)[:5] + [(L_SIDE + 1.45 * BEAT, 'spin', dict(start='auto')),
                                     (L_SIDE + 2.6 * BEAT, 'toe_stand', dict(start='auto'))]
        formation(c, t, cam, pos, 1000, L_FRONT, mj_extra=mj)
    if L_SIDE + 1.45 * BEAT < t < L_SIDE + 2.45 * BEAT:
        glow(c, W / 2 - cam.x * 0.3, H * 0.45, 400, '#ff5a4a', 0.25)


def close(c, t):
    """follow-cam on Michael: shoulders, snap, point - the company a blur behind him"""
    u = u_of(t, L_CLOSE, I_TV)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a060a'))
    lp = skia.Paint()
    lp.setImageFilter(skia.ImageFilters.Blur(14, 14))
    c.saveLayer(None, lp)
    cam = Cam(100 * math.sin(u * math.pi), -560, 0.95, 0)
    with Layer(c, cam, 1.0, t):
        stage_floor(c, t)
        pos = [(-420, 0.85), (420, 0.85), (-760, 0.75), (760, 0.75), (-1050, 0.68), (1050, 0.68)]
        for i, (x, z) in enumerate(pos):
            key = DANCERS[i]
            P = pose(key, routine(L_FRONT), t)
            draw(c, key, x, -(1 - z) * 420, 980 * z, P, D_OUT[i], L_PAY, t)
    c.restore()
    sched = [(L_CLOSE - 0.1, 'shimmy', {}), (L_CLOSE + BEAT * 1.0, 'arm_roll', {}),
             (L_CLOSE + 1.95 * BEAT, 'point_hit', dict(start='auto', side=1)), (L_CLOSE + 3 * BEAT, 'pose_hold', {})]
    P = pose(K.MJ, sched, t)
    fierce(P)
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(-3 + 6 * ease_io(u))
    c.translate(-W / 2, -H / 2)
    h = 2300
    gx, gy = place_head(K.MJ, P, h, (W * 0.5 + 40 * math.sin(T.beat_at(t) * math.pi), H * 0.36))
    draw(c, K.MJ, gx, gy, h, P, K.O_BEATIT, dict(L_PAY, rim='#ff8a7a'), t, shadow=False)
    c.restore()
    if T.env_at('snare', t) > 0.55:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.5, 0.45, 0.07), blend=skia.BlendMode.kPlus))


# ----------------------------------------------------------------------------- THE IMPACT
def tvs(c, t):
    """an electronics store window: every television shows the video; people on the pavement stop to watch"""
    u = u_of(t, I_TV, I_KIDS)
    bg(c, ['#0c0c18', '#14142a'])
    s = 1.0 + 0.08 * ease_io(u)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(s, s)
    c.translate(-W / 2, -H / 2)
    for r in range(4):
        for k in range(3):
            x, y = 30 + k * 345, 260 + r * 330
            tv_set(c, x, y, 330, 300, lambda scr, rr=r, kk=k: beatit_screen(c, scr, t + (rr * 3 + kk) * 0.02, seed=rr * 3 + kk), t,
                   wood=(r + k) % 2 == 0)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (W, H), [(1, 1, 1, 0.0), (1, 1, 1, 0.07), (1, 1, 1, 0.0)])))
    text_center(c, 'ELECTRONICS', W / 2, 200, font('bebas', 110), paint((0.4, 0.9, 1.0, 0.9)))
    for i, (k, x) in enumerate((('x7', W * 0.2), ('fan1', W * 0.55), ('x10', W * 0.86))):
        P = pose(k, [(0, 'groove', dict(amp=0.4))], t + i)
        P['spin'] = 0.5
        hh = 1150 if not k.startswith('fan') else 850
        silhouette(c, lambda: draw(c, k, x, H * 1.2, hh, P, K.O_GROUP_B[1], K.L_STREET, t, shadow=False),
                   color=(0.02, 0.02, 0.05, 1), halo=(0.5, 0.7, 1.0, 0.5), halo_blur=10)


def kids(c, t):
    """at home: two kids copy the dance in front of the TV - one in a homemade red jacket"""
    u = u_of(t, I_KIDS, I_STORE)
    bg(c, ['#5a3a2a', '#4a2e20'])
    for k in range(14):                       # 80s wallpaper stripes
        c.drawRect(skia.Rect.MakeXYWH(k * 80, 0, 36, H * 0.72), paint((0.8, 0.55, 0.3, 0.18)))
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.72, W, H), shader_paint(lin_grad((0, H * 0.72), (0, H), ['#7a5a3a', '#3a2a1a'])))
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.55, H * 0.52, 520, 260), 60, 60, paint('#7a3a2a'))     # sofa
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.52, H * 0.6, 600, 200), 50, 50, paint('#8a4a32'))
    c.drawLine(W * 0.93, H * 0.72, W * 0.93, H * 0.4, paint('#2a1a12', style='stroke', width=10))
    c.drawPath(poly_path([(W * 0.86, H * 0.4), (W * 1.0, H * 0.4), (W * 0.97, H * 0.33), (W * 0.89, H * 0.33)]), paint('#f0d8a0'))
    glow(c, W * 0.93, H * 0.38, 200, '#ffd890', 0.5)
    tv_set(c, -60, H * 0.44, 420, 380, lambda scr: beatit_screen(c, scr, t), t)
    c.drawRect(skia.Rect.MakeXYWH(-60, H * 0.44 + 380, 420, 220), paint('#3a2414'))
    glow(c, 150, H * 0.52, 500, '#9fb8ff', 0.25)
    sched = routine(L_FRONT)
    for k, x, out in (('fan2', W * 0.45, K.O_FANS[2]), ('fan0', W * 0.75, K.O_FANS[0])):
        P = pose(k, sched, t + (0.06 if k == 'fan0' else 0))
        P.update(smile=1.0, mshape='grin', mopen=0.3)
        draw(c, k, x, H * 0.93, 900 * K.DESIGNS[k].height, P, out, K.L_WARM, t)


def sleeve(c, x, y, s, t):
    """a plain, generic LP sleeve (no reproduced artwork): black with type"""
    c.drawRect(skia.Rect.MakeXYWH(x + 8, y + 10, s, s), paint((0, 0, 0, 0.5), blur=10))
    c.drawRect(skia.Rect.MakeXYWH(x, y, s, s), paint('#121014'))
    c.drawRect(skia.Rect.MakeXYWH(x, y, s, s), paint((1, 1, 1, 0.12), style='stroke', width=3))
    text_center(c, 'MICHAEL JACKSON', x + s / 2, y + s * 0.2, font('spartan_b', s * 0.075), paint('#f4efe6'))
    text_center(c, 'THRILLER', x + s / 2, y + s * 0.88, font('bebas', s * 0.2), paint('#d8b040'))


def store(c, t):
    """record store window: Thriller everywhere, a line out of the door"""
    u = u_of(t, I_STORE, I_CHART)
    bg(c, ['#1a1420', '#0c0a10'])
    c.drawRect(skia.Rect.MakeLTRB(0, 430, W, 560), paint('#2a1418'))
    neon_y = 540
    f = font('bebas', 130)
    tw = f.measureText('RECORDS')
    for b, a in ((30, 0.5), (10, 0.8)):
        c.drawString('RECORDS', W / 2 - tw / 2, neon_y, f, paint((1, 0.3, 0.4, a), blur=b, blend=skia.BlendMode.kPlus))
    c.drawString('RECORDS', W / 2 - tw / 2, neon_y, f, paint('#ffd0d8'))
    win = skia.Rect.MakeLTRB(40, 580, W - 40, H * 0.8)
    c.drawRect(win, shader_paint(lin_grad((0, win.top()), (0, win.bottom()), ['#3a2a30', '#2a1e24'])))
    s = 1.0 + 0.06 * ease_io(u)
    c.save()
    c.clipRect(win)
    c.translate(W / 2, H * 0.45)
    c.scale(s, s)
    c.translate(-W / 2, -H * 0.45)
    for r in range(4):
        for k in range(4):
            sleeve(c, 90 + k * 235, 620 + r * 240, 200, t)
    c.drawRoundRect(skia.Rect.MakeXYWH(140, 1060, 800, 120), 14, 14, paint('#d8b040'))
    text_center(c, 'NEW  ·  THRILLER  ·  NOW IN STOCK', W / 2, 1138, font('spartan_b', 40), paint('#1a1014'))
    c.restore()
    c.drawRect(win, paint('#120c10', style='stroke', width=24))
    c.drawLine(win.left() + 100, win.top(), win.left() + 400, win.bottom(), paint((1, 1, 1, 0.06), style='stroke', width=60, blur=14))
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.8, W, H), paint('#141018'))
    for i, (k, x, o) in enumerate((('x7', W * 0.12, K.O_GROUP_A[1]), ('fan1', W * 0.34, K.O_FANS[1]), ('x14', W * 0.58, K.O_DANCERS[4]),
                                   ('x11', W * 0.82, K.O_GROUP_B[3]))):
        P = pose(k, [(0, 'groove', dict(amp=0.5))], t + i * 0.2)
        P.update(smile=0.9, hyaw=-0.3 if i % 2 else 0.3)
        if i == 2:
            P.update(rsh=1.4, rel=-1.2, rhand='open')
        hh = 1000 if k != 'fan1' else 800
        S = draw(c, k, x, H * 1.02, hh, P, o, K.L_WARM, t, shadow=False)
        if i == 2:
            wx, wy = S['arms'][1][2]
            sleeve(c, wx - 60, wy - 220, 180, t)


def chart(c, t):
    """the chart board: BEAT IT climbs into the No. 1 slot"""
    u = u_of(t, I_CHART, E_STAGE)
    bg(c, ['#0e0a18', '#1a1030'])
    beat = T.beat_at(t)
    c.save()
    c.translate(W / 2, H * 0.94)
    crowd(c, t, 3, 1.0, '#08061a', '#ffd080', width=1800, seed=99, y0=-200, row_gap=110, scale0=1.1, beat_phase=beat)
    c.restore()
    bd = skia.Rect.MakeXYWH(90, 420, W - 180, 1020)
    c.drawRoundRect(bd.makeOutset(14, 14), 30, 30, paint('#c8a040'))
    c.drawRoundRect(bd, 24, 24, shader_paint(lin_grad((0, bd.top()), (0, bd.bottom()), ['#1a1424', '#0e0a16'])))
    text_center(c, 'BILLBOARD', W / 2, bd.top() + 90, font('spartan_b', 48), paint('#d8b040'), tracking=12)
    text_center(c, 'HOT 100', W / 2, bd.top() + 200, font('bebas', 120), paint('#f4efe6'), tracking=6)
    text_center(c, '1983', W / 2, bd.top() + 256, font('spartan_b', 34), paint((0.8, 0.75, 0.65, 0.8)), tracking=10)
    climb = ease_io(smoothstep(I_CHART + 0.25, I_CHART + 1.0, t))
    pos_now = 3 - 2 * climb                    # BEAT IT: from No. 3 to No. 1
    row_y = lambda p: bd.top() + 320 + (p - 1) * 130
    for p in range(1, 6):
        y = row_y(p)
        c.drawRoundRect(skia.Rect.MakeXYWH(bd.left() + 40, y, bd.width() - 80, 104), 16, 16, paint((1, 1, 1, 0.05)))
        text_center(c, str(p), bd.left() + 110, y + 76, font('bebas', 80), paint((0.75, 0.7, 0.6, 0.8)))
    for p in (1, 2, 4, 5):                      # other entries: anonymous grey bars (no invented titles)
        y = row_y(p + climb if p < 3 else p)
        c.drawRoundRect(skia.Rect.MakeXYWH(bd.left() + 190, y + 30, 520 - 40 * p, 22), 10, 10, paint((0.55, 0.5, 0.6, 0.45)))
        c.drawRoundRect(skia.Rect.MakeXYWH(bd.left() + 190, y + 64, 320, 14), 7, 7, paint((0.55, 0.5, 0.6, 0.3)))
    y = row_y(pos_now)
    hl = smoothstep(0.6, 0.75, u)
    rr = skia.Rect.MakeXYWH(bd.left() + 30, y - 6, bd.width() - 60, 116)
    c.drawRoundRect(rr, 18, 18, paint((0.85, 0.62, 0.2, 0.35 + 0.55 * hl)))
    if hl > 0:
        glow(c, W / 2, y + 50, 500, '#ffd060', 0.4 * hl)
    c.drawString('BEAT IT', bd.left() + 190, y + 62, font('bebas', 76), paint('#ffffff'))
    c.drawString('MICHAEL JACKSON', bd.left() + 190, y + 98, font('spartan_b', 30), paint((1, 0.95, 0.85, 0.9)))
    if hl > 0.5:
        text_center(c, 'NO. 1', bd.right() - 130, y + 76, font('bebas', 86), paint((1, 0.95, 0.8, hl)))
        rng = np.random.default_rng(17)
        for k in range(120):                     # confetti
            x0 = rng.uniform(0, W)
            sp = rng.uniform(250, 600)
            yy = (rng.uniform(-H, 0) + (t - I_CHART - 1.0) * sp) % (H + 200) - 100
            col = ['#ffd040', '#ff5a5a', '#ffffff', '#6ad0ff'][k % 4]
            c.save()
            c.translate(x0 + 30 * math.sin(t * 3 + k), yy)
            c.rotate(t * 200 + k * 40)
            c.drawRect(skia.Rect.MakeXYWH(-8, -4, 16, 8), paint(col))
            c.restore()


# ----------------------------------------------------------------------------- THE ENDING
def concert(c, t, P, z, anchor):
    """the huge concert in world coords; z = zoom about Michael's head, which is drawn at `anchor` on screen"""
    beat = T.beat_at(t)
    gy, h = H * 0.56, 680
    S = skel(K.MJ, W / 2, gy, h, P)
    hx, hy = S['head']
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#03031a'))
    c.save()
    c.translate(*anchor)
    c.scale(z, z)
    c.translate(-hx, -hy)
    c.drawRect(skia.Rect.MakeLTRB(-3000, -3000, W + 3000, H + 3000), shader_paint(lin_grad((0, -2000), (0, gy), ['#02020e', '#0c0c34', '#1a1250'])))
    rng = np.random.default_rng(4)
    for i in range(160):
        glow(c, rng.uniform(-2500, W + 2500), rng.uniform(-1800, gy - 900), 3, '#ffffff', 0.5)
    for i in range(12):
        x = W / 2 + (i - 5.5) * 300
        sw = 300 * math.sin(t * 0.7 + i)
        beam(c, x, gy - 700, x + sw * 2, -2600, 20, 420, ['#ffffff', '#9fd8ff', '#ffd8a0'][i % 3], 0.18, blur=40)
    c.drawRect(skia.Rect.MakeLTRB(-2400, gy - 820, W + 2400, gy - 780), paint('#1a1a24'))        # truss
    for k in range(-30, 40):
        glow(c, W / 2 + k * 110, gy - 770, 26, ['#ffffff', '#ffd8a0', '#9fd8ff'][k % 3], 0.6)
    c.drawPath(poly_path([(-1400, gy + 20), (W + 1400, gy + 20), (W + 1600, gy + 140), (-1600, gy + 140)]), paint('#141420'))
    c.drawRect(skia.Rect.MakeLTRB(-1600, gy - 10, W + 1600, gy + 24), shader_paint(lin_grad((0, gy - 10), (0, gy + 24), ['#3a3a5a', '#141420'])))
    beam(c, W / 2, -2600, W / 2, gy + 10, 30, 330, '#ffffff', 0.55, blur=30)
    c.drawOval(skia.Rect.MakeXYWH(W / 2 - 240, gy - 20, 480, 60), paint((1, 1, 1, 0.45), blur=20))
    draw(c, K.MJ, W / 2, gy, h, P, K.O_STAGE, dict(K.L_STAGE, rim='#ffffff'), t)
    c.save()
    c.translate(W / 2, gy + 240)
    crowd(c, t, 16, 1.0, '#05051a', '#a8b8ff', width=7400, seed=820, y0=0, row_gap=110, scale0=0.5, beat_phase=beat, lighters=True)
    c.restore()
    for i in range(30):
        x = rng.uniform(-2000, W + 2000)
        glow(c, x, rng.uniform(gy + 200, gy + 1900), 30, '#ffffff', 0.4 * (noise1(t * 3 + i, i) > 0.5))
    c.restore()


def mj_still(t, look_down, rise=0.0):
    P = base_pose(lsh=0.22 + 0.32 * look_down, lel=0.2 - 1.85 * look_down, rsh=0.22 + 0.32 * look_down, rel=0.2 - 1.85 * look_down,
                  lhand='open', rhand='open', hnod=0.022 * look_down * (1 - rise) - 0.006 * rise, ey=0.8 * look_down * (1 - rise) - 0.35 * rise,
                  brow=0.35 * look_down * (1 - rise) - 0.1 * rise, smile=0.15 + 0.45 * rise, blink=0.0)
    P['dip'] = 0.002 * math.sin(t * 1.7)
    return P


def stage(c, t):
    """on a huge stage, after the song: he stands still in the light - and looks down at his hands"""
    u = u_of(t, E_STAGE, E_HANDS)
    look = ease_io(smoothstep(0.35, 0.8, u))
    from character import blend
    P0 = pose(K.MJ, [(0, 'pose_hold', {})], t)
    P = blend(P0, mj_still(t, look), ease_io(smoothstep(0.08, 0.38, u)))
    z = 1.0 + 1.3 * ease_io(u)
    anchor = (W / 2, H * (0.56 - 0.2 * ease_io(u)) - 600 * (1 - ease_io(u)) * 0)
    S = skel(K.MJ, W / 2, H * 0.56, 680, P)
    ax = W / 2 + (S['head'][0] - W / 2) * 1
    ay0 = S['head'][1]
    concert(c, t, P, z, (ax, ay0 + (H * 0.36 - ay0) * ease_io(u)))


def hand_ecu(c, cx, cy, s, side, skin, glove, cuff, sleeve, t):
    """big palm-up hand, fingers slightly curled; side=-1 left, +1 right"""
    c.save()
    c.translate(cx, cy)
    c.scale(side * s, s)
    col = '#f4f4f8' if glove else skin
    ln = paint('#2a1418', style='stroke', width=6)
    c.drawPath(smooth_path([(-220, 500), (-120, 120), (140, 90), (240, 480)], True, 0.5), paint(sleeve))
    c.drawPath(smooth_path([(-150, 150), (-110, 70), (130, 60), (170, 150)], True, 0.5), paint(cuff))
    palm = smooth_path([(-130, 80), (-150, -60), (-110, -190), (90, -200), (150, -80), (130, 80)], True, 0.5)
    c.drawPath(palm, shader_paint(rad_grad((0, -60), 220, [mix(col, '#ffffff', 0.12), col, mix(col, '#000000', 0.15)])))
    c.drawPath(palm, ln)
    for k, (fx, L) in enumerate(((-95, 220), (-30, 260), (35, 250), (95, 200))):
        f = smooth_path([(fx - 30, -180), (fx + 30, -185), (fx + 26 - k * 3, -180 - L), (fx - 4 - k * 3, -200 - L), (fx - 30 - k * 3, -180 - L)], True, 0.5)
        c.drawPath(f, paint(col))
        c.drawPath(f, ln)
        for j in (0.4, 0.72):
            yy = -180 - L * j
            c.drawLine(fx - 18 - k * 2, yy, fx + 14 - k * 2, yy, paint(alpha(mix(col, '#000000', 0.35), 0.6), style='stroke', width=4))
    th = smooth_path([(-130, 0), (-230, -80), (-290, -190), (-250, -210), (-160, -130), (-110, -80)], True, 0.5)
    c.drawPath(th, paint(col))
    c.drawPath(th, ln)
    c.drawArc(skia.Rect.MakeXYWH(-90, -130, 180, 120), 20, 140, False, paint(alpha(mix(col, '#000000', 0.3), 0.6), style='stroke', width=5))
    if glove:
        rng = np.random.default_rng(9)
        for k in range(40):
            x, y = rng.uniform(-140, 140), rng.uniform(-420, 60)
            tw = 0.5 + 0.5 * math.sin(t * 8 + k * 1.3)
            c.drawCircle(x, y, 4 + 4 * tw, paint((1, 1, 1, 0.9)))
            if k % 4 == 0:
                glow(c, x, y, 30 * tw, '#ffffff', 0.6)
    c.restore()


def hands(c, t):
    """his hands - and for one breath, the hands of the boy from the Jackson 5 - then his own again"""
    u = u_of(t, E_HANDS, E_RISE)
    m = smoothstep(56.35, 56.55, t) * (1 - smoothstep(56.95, 57.2, t))     # the memory, inside the musical break
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.4), H * 0.9, ['#20204a', '#0a0a1e', '#04040c'])))
    if m > 0:
        c.save()
        lp = skia.Paint()
        lp.setAlphaf(m)
        c.saveLayer(None, lp)
        c.drawRect(skia.Rect.MakeWH(W, H), paint('#c8502a'))
        scene4.opart(c, t, T.beat_at(t), cx=W / 2, cy=H * 0.35, scale=1.3, hot=0.2)
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.85, 0.6, 0.35)))
        c.restore()
        c.restore()
    beam(c, W / 2, -200, W / 2, H, 100, 900, '#ffffff', 0.18 * (1 - m), blur=60)
    particles(c, t, 50, (0, 0, W, H), 5, '#ffffff', size=(1.5, 4), speed=(6, 20))
    s = 1.0 + 0.06 * ease_io(u)
    breathe = 6 * math.sin(t * 2)
    ad = 1 - m
    if ad > 0.01:
        c.save()
        lp = skia.Paint()
        lp.setAlphaf(ad)
        c.saveLayer(None, lp)
        hand_ecu(c, W * 0.28, H * 0.68 + breathe, 1.25 * s, 1, '#9a6646', False, '#d9b24a', '#16141c', t)
        hand_ecu(c, W * 0.72, H * 0.68 - breathe, 1.25 * s, -1, '#9a6646', True, '#d9b24a', '#16141c', t)
        c.restore()
        c.restore()
    if m > 0.01:
        c.save()
        lp = skia.Paint()
        lp.setAlphaf(m)
        c.saveLayer(None, lp)
        hand_ecu(c, W * 0.33, H * 0.7, 0.85, 1, '#945f3e', False, '#fff4dc', '#8a4ab0', t)
        hand_ecu(c, W * 0.67, H * 0.7, 0.85, -1, '#945f3e', False, '#fff4dc', '#8a4ab0', t)
        c.restore()
        c.restore()
        glow(c, W / 2, H * 0.6, 700, '#ffd8a0', 0.3 * m)


def rise(c, t):
    """he raises his head - and the camera pulls back and back to reveal an audience to the horizon"""
    u = u_of(t, E_RISE, END)
    up = ease_io(smoothstep(E_RISE + 0.05, E_RISE + 0.75, t))
    P = mj_still(t, 1.0 - 0.75 * up, rise=up)
    pull = ease_io(smoothstep(E_RISE + 0.55, 59.7, t))
    z = 3.7 * (0.3 / 3.7) ** pull
    S = skel(K.MJ, W / 2, H * 0.56, 680, P)
    ay = H * 0.42 + (H * 0.36 - H * 0.42) * pull
    concert(c, t, P, z, (W / 2, ay))


SHOTS = [(L_DOOR, door), (L_FRONT, front), (L_SIDE, side), (L_CLOSE, close), (I_TV, tvs), (I_KIDS, kids), (I_STORE, store),
         (I_CHART, chart), (E_STAGE, stage), (E_HANDS, hands), (E_RISE, rise)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    cap(c, t, I_TV + 0.15, E_STAGE - 0.1, ['BEAT IT BECAME', 'A WORLDWIDE HIT.'], y=300, size=88, accent=(1, GOLD))
    cap(c, t, E_HANDS + 0.1, 59.9, ['FROM THE JACKSON 5…'], y=300, size=86)
    cap(c, t, E_RISE + 0.15, 59.9, ['TO THE KING OF POP.'], y=430, size=104, col=GOLD)
