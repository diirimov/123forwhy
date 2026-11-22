"""0:00-0:17.8  GARY REHEARSALS -> JACKSON 5 ON TV -> the spin that grows him up -> OFF THE WALL disco ->
red spotlight becomes the moon -> THRILLER street, zombies, record -> TVs around the world."""
import math
import numpy as np
import skia
from ev_common import *  # noqa: F401,F403
from ev_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, back_out, font, text_center, noise1, poly_path, smooth_path,
                       T, E, base_pose, blend, pose, draw, place_head, skel, bg, u_of, cap, stamp, Cam, Layer, crowd, particles,
                       silhouette, floor_reflection, spin_morph, flash_burst, moon, fog, B_of, GOLD)
from v2_common import room_wall, room_floor, lamp, wall_shadow, wall_clock, GY
from bi_act1 import j5_world
from bi_common import vinyl, tv_set

G_FEET, G_ROOM, J5_TV, J5_SPIN, OTW, TH_MOON, TH_TURN, TH_GROUP, TH_WORLD, END = (0.0, DB(0) + HALF / 2 + 0.17, DB(1), DB(3),
                                                                                 DB(5), DB(6), DB(7), DB(8), DB(9), DB(10))
J5 = ['jackie', 'tito', 'michael', 'jermaine', 'marlon']
L_NIGHT = dict(key=(0.6, -0.6), amb='#5a6a9a', amb_a=0.35, rim='#ffcf8a', line='#140c10', floor_shadow=0.45)


# ----------------------------------------------------------------------------- GARY, INDIANA
def gary_feet(c, t):
    """close on the boy's small shoes striking the boards on every beat; brothers' feet behind; a long shadow slides in"""
    from ev_common import stomp_legs
    bg(c, ['#1a1008', '#24140a', '#3a2412'])
    fy = H * 0.8
    c.drawRect(skia.Rect.MakeLTRB(0, fy - 10, W, H), shader_paint(lin_grad((0, fy), (0, H), ['#5a3418', '#2a180c'])))
    for k in range(-10, 11):
        c.drawLine(W / 2 + k * 90, fy, W / 2 + k * 300, H + 100, paint((0.1, 0.05, 0.02, 0.6), style='stroke', width=5))
    for k in range(8):
        c.drawLine(0, fy + 25 + k * k * 6, W, fy + 25 + k * k * 6, paint((0.1, 0.05, 0.02, 0.3), style='stroke', width=2))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, fy - 10), shader_paint(lin_grad((0, 0), (0, fy), ['#1a120e', '#3a281c'])))
    c.drawRect(skia.Rect.MakeLTRB(0, fy - 220, W, fy - 10), paint('#4a2e1a'))
    glow(c, W * 0.8, H * 0.35, 800, '#ffb060', 0.35)
    lp = skia.Paint()                                   # brothers' feet, soft focus behind
    lp.setImageFilter(skia.ImageFilters.Blur(9, 9))
    c.saveLayer(None, lp)
    for dx, pc in ((-300, '#4a5a3a'), (330, '#6a3a3a')):
        stomp_legs(c, t, W / 2 + dx * 1.3, fy - 160, 0.9, pants=pc, phase=0.0)
    c.restore()
    stomp_legs(c, t, W / 2 - 120, fy, 2.0, pants='#7a6a8a', shoe='#3a2416')
    ph = T.beat_at(t) % 1
    if ph < 0.35:                                       # dust on every strike
        for j in range(9):
            glow(c, W / 2 - 60 + (j - 4) * 40, fy - 20 - 120 * ph, 34, '#e8c89a', 0.45 * (1 - ph / 0.35))
    sweep = ease_out(clamp(t / 0.9), 2)
    edge = W * 1.15 - W * 0.8 * sweep
    c.drawPath(poly_path([(edge, fy - 40), (W + 400, fy - 60), (W + 400, H + 50), (edge - 420, H + 50)]), paint((0.02, 0.01, 0.0, 0.62), blur=24))
    c.drawPath(poly_path([(edge - 60, fy + 10), (edge + 160, fy - 20), (edge + 190, fy + 40), (edge - 90, fy + 60)]),
               paint((0.02, 0.01, 0.0, 0.62), blur=12))


def gary_room(c, t):
    """night rehearsal: five brothers drilling the steps under one bulb; Joe watches, arms folded; the clock says late"""
    u = u_of(t, G_ROOM, J5_TV)
    cam = Cam(-60, 260, 1.45 + 0.15 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.7, t):
        room_wall(c, t, door=0.0, night=1.0)
        wall_clock(c, 520, -560, 70, 11.6)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 0.0)
        for i, (k, x) in enumerate(zip(J5, (-430, -215, 0, 215, 430))):
            P = pose(k, [(0, 'step_touch', dict(width=0.05))], t, ripple=0.04 * i)
            P.update(brow=0.6, smile=0.0, sweat=0.5, fear=0.15)
            draw(c, k, x, GY + 40, 380 * E.DESIGNS[k].height, P, E.O_KID_HOME[k], L_NIGHT, t)
    with Layer(c, cam, 1.35, t):
        Pj = pose('joe', [(0, 'arms_folded', {})], t)
        draw(c, 'joe', 330, GY + 320, 360 * 1.66 * 1.15, Pj, E.O_JOE, dict(L_NIGHT, amb_a=0.6), t)
        lamp(c, -760, on=0.6)


# ----------------------------------------------------------------------------- JACKSON 5 ON TV
def j5_tv(c, t):
    """on the beat the bare room becomes a TV studio: lights, cameras, an audience on its feet"""
    u = u_of(t, J5_TV, J5_SPIN)
    cam = Cam(-260 + 260 * ease_io(u), -330 - 100 * ease_io(u), 0.85 + 0.5 * ease_io(u), -2 + 2 * ease_io(u))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1a0a1a'))
    with Layer(c, cam, 1.0, t):
        j5_world(c, t)
    beat = T.beat_at(t)
    c.save()
    c.translate(W / 2, H * 0.86)
    crowd(c, t, 2, 0.9, '#140a14', '#ffd8a0', width=1600, seed=55, y0=0, row_gap=120, scale0=1.0, beat_phase=beat)
    c.restore()
    for sd in (-1, 1):                     # TV cameras framing the audience
        x = W / 2 + sd * 420
        c.drawRoundRect(skia.Rect.MakeXYWH(x - 110, H * 0.72, 220, 140), 16, 16, paint('#141216'))
        c.drawCircle(x - sd * 120, H * 0.72 + 70, 46, paint('#2a2a30'))
        glow(c, x + sd * 80, H * 0.72 + 20, 16, '#ff2a1a', 0.9)
        text_center(c, 'TV', x, H * 0.72 + 90, font('spartan_b', 40), paint('#3a3a40'))
    # the transformation: a white studio-light bloom opening out of the room
    k = 1 - smoothstep(J5_TV, J5_TV + 0.3, t)
    if k > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.95, 0.85, k)))


def j5_spin(c, t):
    """young Michael spins - and with every turn he grows: 1970 -> 1972 -> 1979, as the TV stage becomes a disco"""
    u = u_of(t, J5_SPIN, OTW)
    t_spin = DB(4) + 0.5 * BEAT              # anticipation on the vocal entry, the spin rides through the break
    from character import MICHAEL_OUTFITS
    stages = [('michael', E.O_KID_TV['michael'], 560), ('michael72', MICHAEL_OUTFITS['michael72'], 560), ('michael79', E.O_OTW, 560)]
    seq = [stages[0], stages[0], stages[1], stages[1], stages[2]]
    us = clamp((t - t_spin) / (OTW - t_spin - 0.05))
    s = 2.5 * (0.85 * us + 0.15 * ease_io(us))          # near-constant spin speed: back views flash past, never linger
    key, out, hh = seq[min(len(seq) - 1, int(math.floor(s * 2 + 0.5)))]
    disco = smoothstep(t_spin + 0.3, OTW - 0.1, t)
    cam = Cam(0, -520 - 60 * disco, 1.75 - 0.45 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1a0a1a'))
    with Layer(c, cam, 1.0, t):
        j5_world(c, t, cast=False)
        if disco > 0:
            c.save()
            lp = skia.Paint()
            lp.setAlphaf(disco)
            c.saveLayer(None, lp)
            disco_world(c, t, people=False)
            c.restore()
            c.restore()
        for i, (k, x) in enumerate(zip(J5, (-560, -280, 0, 280, 560))):
            if k == 'michael':
                continue
            a = 1 - disco
            clear = ease_io(smoothstep(t_spin - 0.6, t_spin, t))    # brothers step out of his way before the spin
            x = x + (560 if x > 0 else -560) * clear
            if a > 0.02:
                P = pose(k, [(0, 'groove', dict(amp=0.8))], t)
                P.update(lsh=P['lsh'] * (1 - clear) + 0.2 * clear, lel=P['lel'] * (1 - clear) + 0.3 * clear,
                         rsh=P['rsh'] * (1 - clear) + 0.2 * clear, rel=P['rel'] * (1 - clear) + 0.3 * clear,
                         ex=-0.6 if x > 0 else 0.6, smile=0.8)
                c.save()
                lp = skia.Paint()
                lp.setAlphaf(a)
                c.saveLayer(None, lp)
                draw(c, k, x, 0, 540 * E.DESIGNS[k].height, P, E.O_KID_TV[k], E.L_TV, t)
                c.restore()
                c.restore()
        if t < t_spin:
            P = pose('michael', [(0, 'step_touch', dict(width=0.04)), (t_spin - 2 * BEAT, 'point_hit', dict(start='auto', side=1))], t, sing=1.0)
        else:
            P = pose(key, [(0, 'spin', dict(start=B_of(t_spin), length=1.0))], t)
            P['spin'] = s
            k_ = ease_out(clamp((t - t_spin) / 0.15), 2)          # arms open out and stay out for the whole spin
            P.update(lsh=0.3 + 0.95 * k_, lel=-0.6 + 0.75 * k_, rsh=0.3 + 0.95 * k_, rel=-0.6 + 0.75 * k_,
                     lhand='open', rhand='open', smile=0.9)
        blur = 0.0 if t < t_spin else 16.0 * math.sin(math.pi * clamp((t - t_spin) / (OTW - t_spin)))
        if blur > 0.5:
            lp = skia.Paint()
            lp.setImageFilter(skia.ImageFilters.Blur(blur, 1.0))
            c.saveLayer(None, lp)
        draw(c, key, 0, 0, hh * E.DESIGNS[key].height, P, out, E.L_TV, t)
        if blur > 0.5:
            c.restore()
    if t > t_spin:                             # spiral of light around the spinning figure, hiding the change of age
        a = math.sin(math.pi * clamp((t - t_spin) / (OTW - t_spin)))
        for j in range(24):
            ang = j / 24 * 2 * math.pi + t * 9
            r = 260 + 60 * math.sin(t * 5 + j)
            glow(c, W / 2 + math.cos(ang) * r, H * 0.58 + math.sin(ang) * r * 0.35 - 300 * (j % 3), 40, ['#ffd060', '#ff9ad8', '#9fd8ff'][j % 3], 0.5 * a)
    k = 1 - smoothstep(OTW - 0.15, OTW, t)
    if t > OTW - 0.15:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.95, 0.9, 0.7 * (1 - k)), blend=skia.BlendMode.kPlus))


# ----------------------------------------------------------------------------- OFF THE WALL
def disco_world(c, t, people=True):
    """1979 disco: lit floor tiles, mirror ball, a dancing crowd (world coords: floor at y=0)"""
    beat = T.beat_at(t)
    c.drawRect(skia.Rect.MakeLTRB(-2400, -2600, 2400, 0), shader_paint(lin_grad((0, -2000), (0, 0), ['#14041e', '#3a0a3a', '#5a1a3a'])))
    for i in range(9):
        x = -1600 + i * 400
        beam(c, 0, -1500, x, 0, 10, 220, ['#ff4ab4', '#ffd040', '#4ae0ff'][i % 3], 0.16, blur=30)
    cx, cy = 0, -1500
    c.drawLine(cx, -2600, cx, cy - 150, paint('#2a2a30', style='stroke', width=6))
    c.drawCircle(cx, cy, 150, shader_paint(rad_grad((cx - 50, cy - 50), 200, ['#ffffff', '#a8a8b8', '#3a3a48'])))
    for k in range(40):
        a = k / 40 * 2 * math.pi + t * 1.5
        for j in range(4):
            x = cx + math.cos(a) * 150 * (0.3 + 0.22 * j)
            y = cy + math.sin(a) * 150 * (0.3 + 0.22 * j)
            if math.cos(a) > 0:
                c.drawRect(skia.Rect.MakeXYWH(x - 9, y - 9, 18, 18), paint((1, 1, 1, 0.3 + 0.6 * ((k + j + int(t * 6)) % 3 == 0))))
    rng = np.random.default_rng(3)
    for k in range(70):          # mirror-ball spots sweeping the room
        a = rng.uniform(0, 6.28) + t * 0.8
        r = rng.uniform(300, 2000)
        glow(c, cx + math.cos(a) * r, cy + 600 + math.sin(a) * r * 0.5, 14, '#ffffff', 0.6)
    for i in range(-8, 9):       # light-up floor
        for j in range(5):
            x0 = i * 220
            y0 = j * 90
            on = (i + j + int(beat)) % 3 == 0
            col = ['#ff4ab4', '#ffd040', '#4ae0ff', '#7aff8a'][(i + j * 2) % 4]
            c.drawPath(poly_path([(x0 * (1 + j * 0.25), y0), ((x0 + 220) * (1 + j * 0.25), y0),
                                  ((x0 + 220) * (1 + (j + 1) * 0.25), y0 + 90), (x0 * (1 + (j + 1) * 0.25), y0 + 90)]),
                       paint(alpha(col, 0.75 if on else 0.25)))
    if people:
        for i, x in enumerate((-900, -650, 650, 900, -1150, 1150)):
            k = f'x{i + 2}'
            P = pose(k, [(0, 'groove' if i % 2 else 'step_touch', {})], t + i * 0.1)
            silhouette(c, lambda k=k, x=x, P=P: draw(c, k, x, -60 - 30 * (i // 2), 900, P, E.K.O_DANCERS[i % 6], E.L_DISCO, t, False),
                       color=(0.12, 0.03, 0.14, 1), halo=(1, 0.5, 0.9, 0.7), halo_blur=10)


def otw(c, t):
    """Off the Wall: tuxedo, white socks, a kick and a spin on a light-up floor"""
    u = u_of(t, OTW, TH_MOON)
    cam = Cam(-80 + 160 * ease_io(u), -560, 0.92 + 0.08 * ease_io(u), 2 * math.sin(u * 3))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14041e'))
    with Layer(c, cam, 1.0, t):
        disco_world(c, t)
        sched = [(0, 'pose_hold', {}), (OTW + 0.3 * BEAT, 'step_touch', dict(width=0.06)), (OTW + 1.95 * BEAT, 'kick', dict(side=1)),
                 (OTW + 2.95 * BEAT, 'point_hit', dict(start='auto', side=1))]
        P = pose(E.M79, sched, t, sing=1.0)
        draw(c, E.M79, 0, 0, 560 * E.DESIGNS[E.M79].height * 1.1, P, E.O_OTW, E.L_DISCO, t)
    vinyl(c, W * 0.86, H * 1.0, 330, (t - OTW) * 220, label='OFF THE WALL', sub='MICHAEL JACKSON 1979')
    # transformation B: his white spotlight turns red and rises...
    red = smoothstep(TH_MOON - 0.55, TH_MOON, t)
    beam(c, W / 2, -100, W / 2, H * 0.83, 40, 300, mix('#ffffff', '#ff2a2a', red), 0.3 + 0.2 * red, blur=30)
    if red > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0.6, 0.0, 0.05, 0.4 * red), blend=skia.BlendMode.kMultiply))


# ----------------------------------------------------------------------------- THRILLER
def street_th(c, t, moon_xy=(W * 0.5, H * 0.2), moon_r=170, red=0.0):
    bg(c, ['#04060e', '#0c1424', '#1a2236'])
    rng = np.random.default_rng(8)
    for i in range(90):
        glow(c, rng.uniform(0, W), rng.uniform(0, H * 0.45), 3, '#ffffff', 0.5)
    moon(c, *moon_xy, moon_r, red)
    hz = H * 0.6
    for k, (x, w, h) in enumerate(((-60, 300, 520), (260, 260, 380), (560, 300, 600), (880, 280, 420))):   # old houses
        c.drawRect(skia.Rect.MakeXYWH(x, hz - h, w, h), paint('#080a12'))
        c.drawPath(poly_path([(x - 20, hz - h), (x + w / 2, hz - h - 140), (x + w + 20, hz - h)]), paint('#080a12'))
        for j in range(2):
            if (k + j) % 2 == 0:
                c.drawRect(skia.Rect.MakeXYWH(x + 50 + j * 120, hz - h + 120, 60, 80), paint((1, 0.8, 0.4, 0.55)))
    for k in range(14):                  # iron fence
        x = k * 80
        c.drawLine(x, hz + 40, x, hz - 120, paint('#06080e', style='stroke', width=8))
        c.drawPath(poly_path([(x - 12, hz - 120), (x + 12, hz - 120), (x, hz - 150)]), paint('#06080e'))
    c.drawLine(0, hz - 90, W, hz - 90, paint('#06080e', style='stroke', width=8))
    c.drawRect(skia.Rect.MakeLTRB(0, hz + 40, W, H), shader_paint(lin_grad((0, hz), (0, H), ['#141c2a', '#06080e'])))
    c.drawLine(W * 0.85, H * 0.95, W * 0.85, H * 0.32, paint('#06080e', style='stroke', width=16))
    glow(c, W * 0.85, H * 0.32, 140, '#e8f0ff', 0.5)


def zombies_emerge(c, t, gy, h0, rise_t0, turn_t, count=6, spread=170, facing=None, sched=None, energy=1.0, dz=0.0):
    keys = [f'z{i}' for i in range(count)]
    for i, k in enumerate(keys):
        side = -1 if i % 2 else 1
        rank = i // 2
        x = W / 2 + side * (230 + rank * spread)
        y = gy - 70 * rank
        hh = h0 * (1 - 0.1 * rank)
        rise = ease_out(clamp((t - rise_t0 - 0.12 * i) / 0.6), 2)
        P = pose(k, sched or [(0, 'zombie', {})], t + 0.05 * i)
        turn = clamp((t - turn_t - 0.04 * i) / 0.3) if turn_t is not None else 1.0
        P['spin'] = 0.5 * (1 - ease_io(turn)) if facing is None else facing
        c.save()
        p = skia.Path()
        p.addRect(skia.Rect.MakeLTRB(-200, -200, W + 200, y + 6))
        c.clipPath(p)
        draw(c, k, x, y + (1 - rise) * hh * 0.9, hh, P, E.O_ZOMBIE[i], E.L_ZOMBIE, t, shadow=False)
        c.restore()


def th_moon(c, t):
    """the red light rises into a full moon over a foggy street; the red jacket glows; the ground starts to move"""
    u = u_of(t, TH_MOON, TH_TURN)
    rise = ease_io(clamp(u / 0.45))
    mx, my = W / 2, H * (0.48 - 0.3 * rise)
    street_th(c, t, (mx, my), 120 + 60 * rise, red=1 - rise * 0.85)
    fog(c, t, H * 0.55, H * 0.8, 0.28)
    zombies_emerge(c, t, H * 0.66, 760, TH_MOON + 0.6, None, facing=0.5)
    P = pose(E.M83, [(0, 'look_down', {})], t)
    P['spin'] = 0.5 * (1 - ease_io(smoothstep(0.55, 0.85, u)))       # he turns from the moon to face us
    P.update(brow=-0.4, smile=0.1)
    draw(c, E.M83, W / 2, H * 0.94, 1250, P, E.O_THRILLER, dict(E.L_MOON, rim='#ffb0b0'), t)
    fog(c, t, H * 0.85, H * 1.05, 0.22)


def th_turn(c, t):
    """the zombies turn toward the camera on one accent; Michael snaps his head on the next"""
    u = u_of(t, TH_TURN, TH_GROUP)
    street_th(c, t, (W * 0.5, H * 0.18), 180, 0.15)
    fog(c, t, H * 0.55, H * 0.8, 0.3)
    zombies_emerge(c, t, H * 0.68, 820, TH_TURN - 5, TH_TURN + 0.05, sched=[(0, 'zombie', {})])
    snap_t = DB(7) + 3 * BEAT
    P = pose(E.M83, [(0, 'groove', dict(amp=0.5, arms=False)), (snap_t - 0.05, 'head_snap', dict(start='auto', side=1))], t)
    P.update(brow=-0.5)
    h = 2000 * (1 + 0.05 * ease_io(u))
    gx, gy = place_head(E.M83, P, h, (W / 2, H * 0.4))
    draw(c, E.M83, gx, gy, h, P, E.O_THRILLER, dict(E.L_MOON, rim='#ffb0b0'), t, shadow=False)
    fog(c, t, H * 0.9, H * 1.1, 0.25)


def th_group(c, t):
    """the whole group locks in: Michael at the point, the dead behind him, every claw on the same accent"""
    u = u_of(t, TH_GROUP, TH_WORLD)
    cam = Cam(0, -560, 0.95 + 0.1 * ease_io(u), -2 + 4 * ease_io(u))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#04060e'))
    acc = 14.745
    sched = [(0, 'zombie', {}), (acc - 0.06, 'claw_pose', dict(start=B_of(acc))), (acc + 1.6 * BEAT, 'zombie', {}),
             (DB(9) - 1.05 * BEAT, 'claw_pose', dict(start=B_of(DB(9) - BEAT)))]
    with Layer(c, cam, 0.6, t):
        c.save()
        c.translate(-W / 2, -H * 0.75)
        street_th(c, t, (W * 0.5, H * 0.2), 200, 0.1)
        c.restore()
    with Layer(c, cam, 1.0, t):
        c.drawRect(skia.Rect.MakeLTRB(-2000, -120, 2000, 1400), shader_paint(lin_grad((0, -120), (0, 900), ['#1a2232', '#06080e'])))
        pos = [(x, z) for x, z in ((-300, 0.86), (300, 0.86), (-580, 0.76), (580, 0.76), (-840, 0.68), (840, 0.68))]
        for i, (x, z) in sorted(enumerate(pos), key=lambda q: q[1][1]):
            k = f'z{i}'
            P = pose(k, sched, t)
            draw(c, k, x, -(1 - z) * 420, 980 * z, P, E.O_ZOMBIE[i], E.L_ZOMBIE, t)
        P = pose(E.M83, sched, t)
        P.update(brow=-0.6, smile=0.1, mopen=0.0)
        draw(c, E.M83, 0, 0, 1000, P, E.O_THRILLER, dict(E.L_MOON, rim='#ffb0b0'), t)
    fog(c, t, H * 0.75, H * 1.05, 0.3)


def th_world(c, t):
    """the Thriller record spins faster - and becomes a ring of TV screens circling the globe"""
    u = u_of(t, TH_WORLD, END)
    bg(c, ['#04040e', '#0a0a1e'])
    k = ease_in(clamp(u / 0.45), 2)
    m = ease_io(smoothstep(0.35, 0.75, u))
    # globe
    if m > 0:
        R = 330 * m
        c.drawCircle(W / 2, H * 0.52, R, shader_paint(rad_grad((W / 2 - R * 0.3, H * 0.52 - R * 0.3), R * 1.4, ['#2a4a8a', '#0a1a3a', '#040814'])))
        for j in range(-3, 4):
            c.drawOval(skia.Rect.MakeXYWH(W / 2 - R * math.cos(j * 0.4), H * 0.52 - R, 2 * R * abs(math.cos(j * 0.4 + t)), 2 * R),
                       paint((0.5, 0.7, 1, 0.25 * m), style='stroke', width=2))
        for j in range(-2, 3):
            yy = H * 0.52 + j * R * 0.33
            ww = math.sqrt(max(0, R * R - (yy - H * 0.52) ** 2))
            c.drawLine(W / 2 - ww, yy, W / 2 + ww, yy, paint((0.5, 0.7, 1, 0.25 * m), style='stroke', width=2))
        glow(c, W / 2, H * 0.52, R * 1.4, '#4a8aff', 0.25 * m)
    # ring of TVs orbiting
    n = 10
    for i in range(n):
        a = i / n * 2 * math.pi + t * 0.9
        rx, ry = 400 * m, 640 * m
        x, y = W / 2 + math.cos(a) * rx - 110, H * 0.52 + math.sin(a) * ry - 90
        if m > 0.05:
            sc = 1.1 + 0.35 * math.sin(a)
            c.save()
            c.translate(x + 110, y + 90)
            c.scale(sc * m, sc * m)
            c.translate(-110, -90)
            tv_set(c, 0, 0, 220, 180, lambda scr: thriller_screen(c, scr, t + i * 0.03), t, wood=i % 2 == 0)
            c.restore()
    # the record (leaves as the TVs arrive)
    if m < 1:
        c.save()
        c.translate(W / 2, H * 0.52)
        s = (1 - m) * (1 + 0.4 * k)
        c.scale(s, s)
        vinyl(c, 0, 0, 470, (t - TH_WORLD) * (200 + 1400 * k), label='THRILLER', sub='MICHAEL JACKSON 1982')
        c.restore()


def thriller_screen(c, scr, t):
    c.drawRect(scr, shader_paint(lin_grad((0, scr.top()), (0, scr.bottom()), ['#0a1424', '#1a2236'])))
    c.drawCircle(scr.centerX() + scr.width() * 0.3, scr.top() + scr.height() * 0.25, scr.width() * 0.12, paint('#f4f0dc'))
    hh = scr.height() * 0.62
    gy = scr.bottom() - scr.height() * 0.06
    for i, dx in enumerate((-0.3, 0.3)):
        P = pose(f'z{i}', [(0, 'zombie', {})], t)
        draw(c, f'z{i}', scr.centerX() + dx * scr.width(), gy - 8, hh * 0.85, P, E.O_ZOMBIE[i], E.L_ZOMBIE, t, False)
    P = pose(E.M83, [(0, 'zombie', {})], t)
    draw(c, E.M83, scr.centerX(), gy, hh, P, E.O_THRILLER, E.L_MOON, t, False)


SHOTS = [(G_FEET, gary_feet), (G_ROOM, gary_room), (J5_TV, j5_tv), (J5_SPIN, j5_spin), (OTW, otw), (TH_MOON, th_moon),
         (TH_TURN, th_turn), (TH_GROUP, th_group), (TH_WORLD, th_world)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    cap(c, t, 0.25, J5_TV + 1.6, ['HE WAS JUST A CHILD…'], y=300, size=88)
    cap(c, t, DB(4) - 0.2, TH_MOON - 0.1, ['BUT HE DREAMED BIGGER.'], y=300, size=88, col=GOLD)
    cap(c, t, TH_MOON + 0.35, TH_GROUP - 0.15, ['THRILLER — 1982'], y=300, size=96, col=(1.0, 0.4, 0.38))
