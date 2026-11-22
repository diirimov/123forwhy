"""0:17.8-0:33.4  MOTOWN 25 (zombie foot -> white sock, the glove, the fedora, the moonwalk, flashes) and BEAT IT
(the sliding foot wipes the stage into an LA street; two groups; Michael steps between them; the dance)."""
import math
import numpy as np
import skia
from ev_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, back_out, font, text_center, noise1, poly_path, smooth_path,
                       T, E, base_pose, blend, pose, draw, place_head, skel, bg, u_of, cap, stamp, Cam, Layer, crowd, particles,
                       silhouette, floor_reflection, spin_morph, flash_burst, fog, B_of, GOLD, moonwalk_legs, loafer, ik_side)
from bi_common import la_street
from bi_act4 import routine, D_OUT
import bi_cast as K

M_FOOT, M_SOCK, M_GLOVE, M_HAT, M_FEET, M_FULL, M_SPIN, B_WIPE, B_STEP, B_DANCE1, B_DANCE2, END = (
    DB(10), DB(10) + 0.5, DB(10) + HALF, DB(11), DB(12), DB(13), DB(14), DB(15), DB(16), DB(17), DB(18), DB(19))
FLASH_T = [21.676, 22.535, 23.394, 24.253, 25.124]       # strongest snare hits in the moonwalk section


def motown_stage(c, t, floor_y, spot_x=W / 2, spot_w=420, audience=True):
    """Motown 25 TV stage: deep blue backdrop with light columns, a glossy black floor, one hard spotlight"""
    bg(c, ['#04061a', '#0a1040', '#141a5a'], (0, 0), (0, floor_y))
    for k in range(9):
        x = 60 + k * 120
        c.drawRect(skia.Rect.MakeXYWH(x, H * 0.12, 18, floor_y - H * 0.12), paint((0.5, 0.6, 1.0, 0.18)))
        for j in range(12):
            on = (k + j + int(T.beat_at(t))) % 4 == 0
            c.drawCircle(x + 9, H * 0.14 + j * (floor_y - H * 0.16) / 12, 7, paint((0.8, 0.85, 1, 0.9 if on else 0.3)))
    c.drawRect(skia.Rect.MakeLTRB(0, floor_y, W, H), shader_paint(lin_grad((0, floor_y), (0, H), ['#14162a', '#04040a'])))
    beam(c, spot_x, -150, spot_x, floor_y + 40, 40, spot_w, '#ffffff', 0.38, blur=30)
    c.drawOval(skia.Rect.MakeXYWH(spot_x - spot_w * 0.75, floor_y - 30, spot_w * 1.5, 110), paint((1, 1, 1, 0.42), blur=24))
    if audience:
        c.save()
        c.translate(W / 2, H * 1.0)
        crowd(c, t, 2, 0.6, '#04040e', '#9fb8ff', width=1800, seed=25, y0=-40, row_gap=120, scale0=1.0, beat_phase=T.beat_at(t))
        c.restore()


def foot_match(c, t):
    """a zombie's shuffling foot in the fog ... match cut on the beat: the same foot is now a black loafer and a
    glittering white sock on the Motown stage"""
    sock = t >= M_SOCK
    if not sock:
        bg(c, ['#06080e', '#141c2a'])
        fog(c, t, H * 0.55, H * 0.9, 0.35)
    else:
        motown_stage(c, t, H * 0.78, spot_x=W * 0.5, spot_w=520, audience=False)
    fy = H * 0.78
    s = 2.1
    k = (B_of(t) % 1)
    lift = math.sin(math.pi * clamp((k - 0.15) / 0.5)) if k > 0.15 else 0.0
    heel = (W * 0.42 + 120 * k, fy - 18 * s - 60 * s * lift)
    ankle = (heel[0] + 20 * s, heel[1] - 60 * s)
    if not sock:
        loafer(c, heel, 0.12 * lift, s * 1.3, -1, shoe='#3a3a30')
        c.drawPath(smooth_path([(ankle[0] - 80, ankle[1] - 20), (ankle[0] + 70, ankle[1] - 30), (ankle[0] + 90, -100), (ankle[0] - 100, -100)], True, 0.3),
                   paint('#4a4a3a'))
        for j in range(5):            # torn trouser hem
            x = ankle[0] - 80 + j * 40
            c.drawPath(poly_path([(x, ankle[1] - 20), (x + 20, ankle[1] + 30 + 20 * (j % 2)), (x + 40, ankle[1] - 20)]), paint('#4a4a3a'))
        c.drawRect(skia.Rect.MakeXYWH(ankle[0] - 40, ankle[1] - 10, 90, 60), paint('#7a8a6a'))
    else:
        loafer(c, heel, 0.12 * lift, s * 1.3, -1)
        c.drawRect(skia.Rect.MakeXYWH(ankle[0] - 70, ankle[1] - 230, 150, 250), paint('#f4f4f8'))
        rng = np.random.default_rng(4)
        for q in range(26):
            tw = 0.5 + 0.5 * math.sin(t * 10 + q)
            c.drawCircle(ankle[0] - 60 + rng.uniform(0, 140), ankle[1] - 220 + rng.uniform(0, 230), 4 + 4 * tw, paint((1, 1, 1, tw)))
            if q % 5 == 0:
                glow(c, ankle[0] - 60 + rng.uniform(0, 140), ankle[1] - 200 + rng.uniform(0, 200), 26 * tw, '#ffffff', 0.6)
        c.drawPath(smooth_path([(ankle[0] - 90, ankle[1] - 220), (ankle[0] + 100, ankle[1] - 230), (ankle[0] + 110, -100), (ankle[0] - 110, -100)], True, 0.3),
                   shader_paint(lin_grad((ankle[0] - 100, 0), (ankle[0] + 100, 0), ['#2a2a36', '#121016', '#060608'])))
        k2 = 1 - smoothstep(M_SOCK, M_SOCK + 0.18, t)
        if k2 > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 1, 1, 0.6 * k2), blend=skia.BlendMode.kPlus))


def glove(c, t):
    """the single white glove: fingers flex open in the spotlight, rhinestones catching fire"""
    u = u_of(t, M_GLOVE, M_HAT)
    motown_stage(c, t, H * 1.3, spot_x=W / 2, spot_w=700, audience=False)
    from bi_act4 import hand_ecu
    c.save()
    c.translate(W / 2, H * 0.62)
    c.rotate(-12 + 10 * ease_io(u))
    open_ = ease_out(clamp(u / 0.5), 2)
    c.scale(1.0 + 0.15 * ease_io(u), 1.0 + 0.15 * ease_io(u))
    hand_ecu(c, 0, 0, 1.9, -1, '#9a6646', True, '#d8d8e0', '#121016', t)
    c.restore()
    for j in range(10):
        a = j / 10 * 2 * math.pi + t * 2
        glow(c, W / 2 + math.cos(a) * 320, H * 0.4 + math.sin(a) * 320, 30, '#ffffff', 0.4 * open_)


def hat_on(c, t):
    """the black fedora comes down onto his head on the guitar accent; the brim tilts; the eyes disappear"""
    u = u_of(t, M_HAT, M_FEET)
    motown_stage(c, t, H * 1.2, spot_x=W / 2, spot_w=700, audience=False)
    down = ease_out(clamp((t - M_HAT + 0.1) / 0.35), 3)
    P = pose(E.M83, [(0, 'hat_tip', dict(start=B_of(M_HAT)))], t)
    P.update(hnod=0.014 * down, ey=-0.4, brow=-0.4, smile=0.05)
    h = 2500 * (1 + 0.08 * ease_io(u))
    gx, gy = place_head(E.M83, P, h, (W / 2, H * 0.45))
    out = E.O_MOTOWN if down > 0.98 else E.O_MOTOWN_NOHAT
    S = draw(c, E.M83, gx, gy, h, P, out, E.L_SPOT, t, shadow=False)
    if down <= 0.98:                       # the hat on its way down, in his hand
        hx, hy = S['head']
        r = S['hr']
        yy = hy - r * 1.6 - (1 - down) * 500
        c.drawOval(skia.Rect.MakeXYWH(hx - r * 1.6, yy + r * 0.2, r * 3.2, r * 0.45), paint('#101014'))
        c.drawPath(smooth_path([(hx - r * 0.95, yy + r * 0.35), (hx - r * 0.85, yy - r * 0.5), (hx, yy - r * 0.65), (hx + r * 0.85, yy - r * 0.5),
                                (hx + r * 0.95, yy + r * 0.35)], True, 0.4), paint('#101014'))
    if 0 < t - (M_HAT + 0.25) < 0.2:
        glow(c, W / 2, H * 0.3, 500, '#ffffff', 0.4 * (1 - (t - M_HAT - 0.25) / 0.2))


def feet_moon(c, t):
    """spotlight on the feet: the moonwalk in profile - toe planted, flat foot gliding back, heel-drop, swap"""
    u = u_of(t, M_FEET, M_FULL)
    fy = H * 0.74
    cam_x = -60 * ease_io(u)
    hipx = W * 0.66 + 1000 * 0.75 * 0.32 * (-1) * (B_of(t) - B_of(M_FEET)) * 0 + 0
    start = B_of(M_FEET)
    travel = 0.3 * 1000 * 1.05 * (B_of(t) - start)
    sx = W * 0.75 - travel * 0.0
    c.save()
    c.translate(-(-travel) * 0.0, 0)
    motown_stage(c, t, fy, spot_x=W * 0.5, spot_w=600, audience=False)
    c.restore()
    # the camera tracks him: legs stay centred while the floor reflections stream past
    for k in range(12):
        x = ((k * 140 + travel * 0.8) % (W + 280)) - 140
        c.drawLine(x, fy + 30, x - 120, H, paint((0.6, 0.7, 1, 0.08), style='stroke', width=6))
    hx, hy = moonwalk_legs(c, t, W * 0.4 + travel, fy, 1.05, start, dirn=-1, stride=0.3)
    # the cut is a tracking shot: we offset the whole rig back to centre
    flash_burst(c, t, FLASH_T[:2], n=18, seed=3, area=(0, H * 0.1, W, H * 0.5))


def full_moon(c, t):
    """the whole figure: moonwalking across the Motown stage, camera tracking, flashes going off all over the house"""
    u = u_of(t, M_FULL, M_SPIN)
    floor_y = H * 0.7
    start = B_of(M_FULL)
    P = pose(E.M83, [(0, 'moonwalk2', dict(start=start, dirn=-1, stride=0.075))], t)
    h = 980
    body_x = P['x'] * h
    cam_dx = body_x * 0.85
    c.save()
    c.translate(-cam_dx * 0.4, 0)
    motown_stage(c, t, floor_y, spot_x=W * 0.62 + body_x * 0.6 + cam_dx * 0.4, spot_w=360, audience=False)
    c.restore()
    x = W * 0.62 - cam_dx
    floor_reflection(c, lambda: draw(c, E.M83, x, floor_y, h, P, E.O_MOTOWN, E.L_SPOT, t, False), floor_y, 0.22)
    draw(c, E.M83, x, floor_y, h, P, E.O_MOTOWN, E.L_SPOT, t)
    c.save()
    c.translate(W / 2, H * 1.0)
    crowd(c, t, 3, 0.8, '#04040e', '#9fb8ff', width=1800, seed=26, y0=-80, row_gap=120, scale0=1.05, beat_phase=T.beat_at(t))
    c.restore()
    flash_burst(c, t, FLASH_T[2:4], n=30, seed=5, area=(0, H * 0.55, W, H))


def spin_toe(c, t):
    """out of the moonwalk: a spin, then up onto his toes - and the house erupts"""
    u = u_of(t, M_SPIN, B_WIPE)
    floor_y = H * 0.72
    motown_stage(c, t, floor_y, spot_x=W / 2, spot_w=380, audience=True)
    sched = [(0, 'moonwalk2', dict(start=B_of(M_SPIN) - 4, dirn=-1)), (M_SPIN + 0.2 * BEAT, 'spin', dict(start='auto', length=1.0)),
             (M_SPIN + 1.3 * BEAT, 'toe_stand', dict(start='auto')), (M_SPIN + 3.2 * BEAT, 'hat_pose', dict(start='auto'))]
    P = pose(E.M83, sched, t)
    P['x'] = 0
    h = 1180 * (1 + 0.06 * ease_io(u))
    floor_reflection(c, lambda: draw(c, E.M83, W / 2, floor_y, h, P, E.O_MOTOWN, E.L_SPOT, t, False), floor_y, 0.22)
    draw(c, E.M83, W / 2, floor_y, h, P, E.O_MOTOWN, E.L_SPOT, t)
    flash_burst(c, t, [FLASH_T[4], M_SPIN + 1.3 * BEAT], n=34, seed=7, area=(0, H * 0.7, W, H))


# ----------------------------------------------------------------------------- BEAT IT
def foot_wipe(c, t):
    """transformation: a gliding white-socked foot crosses the frame - behind it the stage becomes an LA street;
    the two groups walk in from both sides"""
    u = u_of(t, B_WIPE, B_STEP)
    wipe = ease_io(clamp((t - B_WIPE) / 0.55))
    edge = W + 200 - (W + 600) * wipe
    la_street(c, t, cam_dx=-40 * u)
    hz = H * 0.55
    for side, grp, outs in ((-1, ['x0', 'x2', 'x8', 'x10'], K.O_GROUP_A), (1, ['x1', 'x3', 'x9', 'x11'], K.O_GROUP_B)):
        for i, k in enumerate(grp):
            depth = [0.0, 0.6, 1.0, 1.5][i]
            gy = hz + 170 + depth * 190
            h = 520 + depth * 170
            P = pose(k, [(0, 'walk', dict(start=B_of(B_WIPE), dirn=-side, speed=0.17))], t + i * 0.07)
            P.update(brow=0.7, smile=-0.2, hyaw=-side * 0.2)
            draw(c, k, W / 2 + side * (420 + i * 120), gy, h, P, outs[i % 4], dict(E.K.L_STREET, rim='#ff5ab4' if side < 0 else '#5ae0ff'), t)
    if wipe < 1:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-10, -10, edge, H + 10))
        motown_stage(c, t, H * 0.72, spot_x=W / 2, spot_w=380, audience=True)
        c.restore()
        fy = H * 0.86
        heel = (edge + 100, fy - 40)
        loafer(c, heel, 0.0, 2.6, -1)
        c.drawRect(skia.Rect.MakeXYWH(heel[0] - 60, fy - 440, 180, 300), paint('#f4f4f8'))
        c.drawPath(smooth_path([(heel[0] - 90, fy - 420), (heel[0] + 140, fy - 420), (heel[0] + 160, -200), (heel[0] - 110, -200)], True, 0.3),
                   paint('#121016'))
        c.drawRect(skia.Rect.MakeXYWH(edge + 260, 0, 600, H), paint((0.9, 0.95, 1, 0.12), blur=40))


def step_between(c, t):
    """the groups face off; out of the dark between them Michael walks in, and stops them with open hands"""
    u = u_of(t, B_STEP, B_DANCE1)
    la_street(c, t, cam_dx=-40 - 20 * u)
    gy = H * 0.84
    for side, grp, outs in ((-1, ['x0', 'x2', 'x8'], K.O_GROUP_A), (1, ['x1', 'x3', 'x9'], K.O_GROUP_B)):
        for i, k in enumerate(grp):
            P = pose(k, [(0, 'arms_folded' if i else 'stare', {})], t + i)
            P.update(brow=0.8, smile=-0.3, hyaw=-side * 0.45, tw=-side * 0.35, ex=-side * 0.8)
            draw(c, k, W / 2 + side * (300 + i * 150), gy - i * 60, 1100 - i * 120, P, outs[i], dict(E.K.L_STREET, rim='#ff5ab4' if side < 0 else '#5ae0ff'), t)
    a = ease_io(u_of(t, B_STEP, 28.95))
    h = 600 + 700 * a
    walking = a < 0.98
    P = pose(E.M83, [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))], t)
    P.update(hyaw=0, tw=0, brow=-0.3, smile=0.05)
    stop = ease_out(smoothstep(28.95, 29.35, t), 2)
    if not walking:
        P.update(lfx=-0.09, rfx=0.09, lfy=0, rfy=0, dip=0.0)
    P.update(lsh=P['lsh'] * (1 - stop) + 1.45 * stop, lel=P['lel'] * (1 - stop) + 0.05 * stop, rsh=P['rsh'] * (1 - stop) + 1.45 * stop,
             rel=P['rel'] * (1 - stop) + 0.05 * stop, lhand='open' if stop > 0.5 else 'relaxed', rhand='open' if stop > 0.5 else 'relaxed')
    draw(c, E.M83, W / 2, gy - 120 + 120 * a, h, P, E.O_BEATIT, dict(E.K.L_STREET, rim='#ffffff'), t)


def street_dance(c, t, angle=0):
    from bi_act4 import formation, stage_floor, DANCERS
    u = u_of(t, B_DANCE1 if angle == 0 else B_DANCE2, B_DANCE2 if angle == 0 else END)
    t0 = B_DANCE1
    if angle == 0:
        cam = Cam(-120 + 240 * ease_io(u), -560, 0.9 + 0.1 * ease_io(u), 0)
    else:
        cam = Cam(260 - 420 * ease_io(u), -620, 1.05, 4)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a080e'))
    with Layer(c, cam, 0.55, t):
        c.save()
        c.translate(-W / 2, -H * 0.82)
        la_street(c, t, cam_dx=0)
        c.restore()
    with Layer(c, cam, 1.0, t):
        c.drawRect(skia.Rect.MakeLTRB(-2400, -330, 2400, 1400), shader_paint(lin_grad((0, -330), (0, 900), ['#1a1424', '#08080e'])))
        for k in range(-6, 7):
            c.drawRect(skia.Rect.MakeXYWH(k * 300 - 60, -200 + 40 * math.sin(t * 3 + k), 120, 600),
                       paint(alpha(['#ff4ab4', '#4ae0ff'][k % 2], 0.06), blur=20, blend=skia.BlendMode.kPlus))
        if angle == 0:
            pos = [(0, 1.0), (-330, 0.86), (330, 0.86), (-640, 0.74), (640, 0.74), (-930, 0.64), (930, 0.64)]
        else:
            pos = [(0, 1.0)] + [(-300 - i * 230, 1.0 - i * 0.08) for i in range(4)] + [(300 + i * 260, 1.06 + i * 0.04) for i in range(2)]
        mj = routine(t0) if angle == 0 else routine(t0)[:7] + [(B_DANCE2 + 1.45 * BEAT, 'spin', dict(start='auto')),
                                                              (B_DANCE2 + 2.6 * BEAT, 'toe_stand', dict(start='auto')),
                                                              (B_DANCE2 + 3.3 * BEAT, 'point_hit', dict(start='auto', side=1))]
        formation(c, t, cam, pos, 1000, t0, mj_extra=mj, mj_out=E.O_BEATIT)
    if angle == 1:
        c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (W, 0), [(0, 0, 0, 0.35), (0, 0, 0, 0), (0, 0, 0, 0.35)])))
    k = 1 - smoothstep(B_DANCE1, B_DANCE1 + 0.2, t)
    if angle == 0 and k > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.85, 0.8, 0.5 * k), blend=skia.BlendMode.kPlus))


SHOTS = [(M_FOOT, foot_match), (M_GLOVE, glove), (M_HAT, hat_on), (M_FEET, feet_moon), (M_FULL, full_moon), (M_SPIN, spin_toe),
         (B_WIPE, foot_wipe), (B_STEP, step_between), (B_DANCE1, lambda c, t: street_dance(c, t, 0)),
         (B_DANCE2, lambda c, t: street_dance(c, t, 1))]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    cap(c, t, M_FEET + 0.15, M_SPIN + 1.2, ['ONE MOVE', 'CHANGED EVERYTHING.'], y=300, size=88, accent=(1, GOLD))
    cap(c, t, B_WIPE + 0.4, B_DANCE1 - 0.1, ['BEAT IT — 1983'], y=300, size=96, col=(1.0, 0.4, 0.38))
