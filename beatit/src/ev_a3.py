"""0:33.4-0:47.2  BAD (the red jacket spins into black buckles; subway; a spin opens into a stadium) ->
SMOOTH CRIMINAL (fedora thrown at the lens, caught in the white suit; the anti-gravity lean) -> DANGEROUS (gold, stillness, pyro)."""
import math
import numpy as np
import skia
from ev_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, back_out, font, text_center, noise1, poly_path, smooth_path,
                       T, E, base_pose, blend, pose, draw, place_head, skel, bg, u_of, cap, stamp, Cam, Layer, crowd, particles,
                       silhouette, floor_reflection, spin_morph, flash_burst, B_of, GOLD, stadium, sunglasses)
from bi_common import la_street
from bi_act4 import routine
import bi_cast as K

BAD_MORPH, SUBWAY, TO_STAD, STAD_WIDE, HAT_THROW, SC_CLUB, LEAN0, DANG, DANG_WIDE, END = (
    DB(19), DB(20), DB(21), DB(22), DB(23), DB(23) + HALF, 42.40, DB(25), 45.0, DB(27))
LEAN_DEEP = 43.42


def subway_world(c, t, train=True):
    """subway station (world coords, platform edge at y=0): white tiles, columns, flickering tubes, a train streaking past"""
    c.drawRect(skia.Rect.MakeLTRB(-2400, -2400, 2400, 0), paint('#c8d0c0'))
    for j in range(60):
        for k in range(-30, 30):
            c.drawRect(skia.Rect.MakeXYWH(k * 80, -2400 + j * 40, 78, 38), paint((0.3, 0.35, 0.3, 0.25), style='stroke', width=2))
    c.drawRect(skia.Rect.MakeLTRB(-2400, -980, 2400, -900), paint('#1a4a2a'))
    text_center(c, 'STATION', -300, -915, font('spartan_b', 60), paint('#f4f4ec'), tracking=12)
    text_center(c, 'STATION', 900, -915, font('spartan_b', 60), paint('#f4f4ec'), tracking=12)
    if train:
        x0 = ((t * 2600) % 5200) - 2600
        c.drawRect(skia.Rect.MakeLTRB(-2400, -760, 2400, -120), paint((0.4, 0.42, 0.45, 0.9)))
        for k in range(-6, 7):
            wx = x0 + k * 420
            c.drawRect(skia.Rect.MakeXYWH(wx, -640, 300, 220), paint((1, 0.95, 0.75, 0.75)))
        for k in range(14):
            y = -740 + k * 46
            c.drawLine(-2400, y, 2400, y, paint((1, 1, 1, 0.06), style='stroke', width=4))
    for k in range(-5, 6):
        x = k * 520
        c.drawRect(skia.Rect.MakeXYWH(x - 50, -2400, 100, 2400), shader_paint(lin_grad((x - 50, 0), (x + 50, 0), ['#2a4a32', '#4a7a52', '#1a3a22'])))
    for k in range(-5, 6):
        on = 1.0 if noise1(t * 7 + k, k) > -0.7 else 0.3
        c.drawRect(skia.Rect.MakeXYWH(k * 520 + 60, -1300, 360, 26), paint((1, 1, 0.95, on)))
        glow(c, k * 520 + 240, -1290, 220, '#f0fff0', 0.25 * on)
    c.drawRect(skia.Rect.MakeLTRB(-2400, -10, 2400, 1400), shader_paint(lin_grad((0, 0), (0, 900), ['#6a6a62', '#24241e'])))
    c.drawRect(skia.Rect.MakeLTRB(-2400, -12, 2400, 24), paint('#e8d040'))


def bad_morph(c, t):
    """transformation E: the red leather jacket spins - and comes round as black leather, straps and buckles"""
    u = u_of(t, BAD_MORPH, SUBWAY)
    s, (key, out) = spin_morph(t, BAD_MORPH + 0.05, 1.0, [(E.M83, E.O_BEATIT), (E.M83, E.O_BEATIT), (E.M87, E.O_BAD)], turns=1.5)
    mix_k = smoothstep(BAD_MORPH + 0.4, BAD_MORPH + 1.0, t)
    cam = Cam(0, -560, 1.25 + 0.15 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a0a0e'))
    with Layer(c, cam, 1.0, t):
        if mix_k < 1:
            c.save()
            c.translate(-W / 2, -H * 0.86)
            la_street(c, t)
            c.drawRect(skia.Rect.MakeLTRB(-W, H - 2, 2 * W, 3 * H), paint('#0a0a12'))
            c.restore()
        if mix_k > 0:
            c.save()
            lp = skia.Paint()
            lp.setAlphaf(mix_k)
            c.saveLayer(None, lp)
            subway_world(c, t)
            c.restore()
            c.restore()
        if t < BAD_MORPH + 1.05:
            P = pose(key, [(0, 'spin', dict(start=0))], t)
            P['spin'] = s
            P.update(lsh=1.3, lel=0.3, rsh=1.3, rel=0.3, lhand='open', rhand='open')
        else:
            P = pose(key, [(0, 'point_hit', dict(start=B_of(BAD_MORPH + 1.05), side=-1))], t)
            P.update(brow=-0.6, smile=0.15)
        draw(c, key, 0, 0, 1000, P, out, E.L_SUBWAY, t)
    if 0.25 < s % 1 < 0.75 or 0 < (t - BAD_MORPH) < 1.0:
        for j in range(18):
            a = j / 18 * 2 * math.pi + t * 10
            glow(c, W / 2 + math.cos(a) * 300, H * 0.55 + math.sin(a) * 120, 26, '#ffffff', 0.35 * math.sin(math.pi * u_of(t, BAD_MORPH, BAD_MORPH + 1.05)))


def subway(c, t):
    """Bad: an underground station, a train howling past, a crew in black behind him - kicks, spins, sharp points"""
    from bi_act4 import formation
    u = u_of(t, SUBWAY, TO_STAD)
    cam = Cam(-160 + 320 * ease_io(u), -600, 1.0, -2)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#1a1a18'))
    with Layer(c, cam, 0.8, t):
        subway_world(c, t)
    with Layer(c, cam, 1.0, t):
        pos = [(0, 1.0), (-360, 0.84), (360, 0.84), (-700, 0.72), (700, 0.72)]
        mj = [(0, 'kick', dict(side=1)), (SUBWAY + 0.95 * BEAT, 'point_hit', dict(start='auto', side=1)),
              (SUBWAY + 2 * BEAT, 'spin', dict(start='auto')), (SUBWAY + 2.95 * BEAT, 'point_hit', dict(start='auto', side=-1))]
        formation(c, t, cam, pos, 1000, SUBWAY - 4 * BEAT, mj_extra=mj, mj_out=E.O_BAD, L=E.L_SUBWAY)


def to_stadium(c, t):
    """a spin - and the station opens like an iris onto a stadium: tens of thousands of people"""
    u = u_of(t, TO_STAD, STAD_WIDE)
    iris = ease_io(clamp((t - TO_STAD - 0.1) / 0.55))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#04040e'))
    cam = Cam(0, -520, 1.1 - 0.15 * ease_io(u), 0)
    with Layer(c, cam, 1.0, t):
        if iris < 1:
            subway_world(c, t)
        if iris > 0:
            p = skia.Path()
            p.addCircle(0, -500, 3200 * iris)
            c.save()
            c.clipPath(p, doAntiAlias=True)
            stadium(c, t, seed=3)
            c.restore()
        sched = [(0, 'spin', dict(start=B_of(TO_STAD), length=1.0)), (TO_STAD + 1.05 * BEAT, 'cheer', {}),
                 (TO_STAD + 2.6 * BEAT, 'point_hit', dict(start='auto', side=1))]
        P = pose(E.M87, sched, t)
        draw(c, E.M87, 0, 0, 1000, P, E.O_BAD, E.L_STADIUM, t)
    if 0 < iris < 1:
        c.drawCircle(W / 2, H / 2 - 20, 3200 * iris * 0.55, paint((1, 1, 1, 0.6 * (1 - iris)), style='stroke', width=30, blur=20))


def stad_wide(c, t):
    """pull back and back: one small figure in the light, the whole stadium on its feet"""
    u = u_of(t, STAD_WIDE, HAT_THROW)
    z = 0.95 * (0.42 / 0.95) ** ease_io(u)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#02020c'))
    with Layer(c, Cam(0, -420 + 200 * ease_io(u), z, 0), 1.0, t):
        stadium(c, t, energy=1.0, seed=3, rows=16)
        P = pose(E.M87, [(0, 'cheer', {})], t)
        draw(c, E.M87, 0, 0, 1000, P, E.O_BAD, E.L_STADIUM, t)
        beam(c, 0, -3000, 0, 0, 30, 400, '#ffffff', 0.5, blur=30)
    flash_burst(c, t, [STAD_WIDE + 0.4, STAD_WIDE + 1.2], n=40, seed=9, area=(0, H * 0.5, W, H))


def hat_throw(c, t):
    """transformation F: he flicks the fedora straight at the lens - it spins up to fill the frame -"""
    u = u_of(t, HAT_THROW, SC_CLUB)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#04040e'))
    with Layer(c, Cam(0, -560, 1.35, 0), 1.0, t):
        stadium(c, t, seed=3, beams=True)
        P = pose(E.M87, [(0, 'point_hit', dict(start=B_of(HAT_THROW - 0.15), side=1))], t)
        P.update(brow=-0.5, smile=0.3)
        S = draw(c, E.M87, 0, 0, 1000, P, E.O_BAD, E.L_STADIUM, t)
    k = ease_in(clamp((t - HAT_THROW - 0.05) / 0.75), 2.4)
    hs = 70 + 2400 * k
    spin = (t - HAT_THROW) * 900
    hx, hy = W * 0.62 - (W * 0.12) * k, H * 0.36 + H * 0.12 * k
    white = smoothstep(0.55, 0.85, k)
    col = mix('#101014', '#f2f0ea', white)
    band = mix('#2a2a30', '#141216', white)
    c.save()
    c.translate(hx, hy)
    c.rotate(spin * 0.15)
    c.scale(1, 0.45 + 0.4 * k)
    c.drawCircle(0, 0, hs, paint(col))
    c.drawCircle(0, 0, hs * 0.62, paint(band))
    c.drawCircle(0, 0, hs * 0.55, paint(shade(col, -0.1)))
    c.drawArc(skia.Rect.MakeXYWH(-hs, -hs, 2 * hs, 2 * hs), 200, 80, False, paint((1, 1, 1, 0.3), style='stroke', width=hs * 0.05))
    c.restore()


def club_world(c, t):
    """1930s nightclub (world coords, floor y=0): blue smoke, chandeliers, ceiling fans, a piano, a bar"""
    c.drawRect(skia.Rect.MakeLTRB(-2400, -2400, 2400, 0), shader_paint(lin_grad((0, -2000), (0, 0), ['#0a1424', '#1a2a44', '#2a3a5a'])))
    for k in range(-6, 7):
        x = k * 400
        c.drawRect(skia.Rect.MakeXYWH(x - 30, -2400, 60, 2400), paint('#0e1828'))
        beam(c, x + 200, -1900, x + 600, 0, 30, 300, '#c8d8ff', 0.08, blur=40)
    for k in range(-2, 3):
        x = k * 700
        c.drawLine(x, -2400, x, -1700, paint('#c8b070', style='stroke', width=6))
        for j in range(8):
            glow(c, x + math.cos(j) * 90, -1680 + math.sin(j) * 30, 30, '#ffe0a0', 0.7)
        a = t * 6 + k
        for j in range(4):
            c.drawLine(x + 350, -1500, x + 350 + math.cos(a + j * 1.57) * 160, -1500 + math.sin(a + j * 1.57) * 20,
                       paint('#0a0e18', style='stroke', width=20))
    c.drawRoundRect(skia.Rect.MakeXYWH(900, -420, 560, 300), 40, 40, paint('#0a0a0e'))     # grand piano
    c.drawRect(skia.Rect.MakeXYWH(-1700, -500, 700, 380), paint('#2a1a12'))                # bar
    for k in range(8):
        glow(c, -1650 + k * 85, -470, 18, '#ffd890', 0.6)
    c.drawRect(skia.Rect.MakeLTRB(-2400, -10, 2400, 1400), shader_paint(lin_grad((0, 0), (0, 900), ['#2a2a3a', '#0a0a12'])))
    for k in range(-12, 13):
        c.drawLine(k * 200, 0, k * 600, 1400, paint((1, 1, 1, 0.04), style='stroke', width=3))
    for k in range(3):
        c.drawOval(skia.Rect.MakeXYWH(-1800 + 300 * math.sin(t * 0.3 + k), -900 + k * 280, 3600, 400), paint((0.7, 0.8, 1, 0.07), blur=60))


def sc_club(c, t):
    """the fedora comes down out of the lens into his hand - white suit - a kick, a spin - then the lean"""
    u = u_of(t, SC_CLUB, DANG)
    lean = ease_io(smoothstep(LEAN0, LEAN_DEEP, t))
    cam_rot = -16 * ease_io(smoothstep(LEAN_DEEP - 0.1, DANG, t))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#060a14'))
    c.save()
    c.translate(W / 2, H * 0.6)
    c.rotate(cam_rot)
    c.translate(-W / 2, -H * 0.6)
    cam = Cam(0, -560, 1.08 + 0.12 * lean, 0)
    with Layer(c, cam, 0.85, t):
        club_world(c, t)
    with Layer(c, cam, 1.0, t):
        # 1930s gangster dancers behind him lean too
        for i, (x, z) in enumerate(((-420, 0.8), (420, 0.8), (-760, 0.7), (760, 0.7))):
            k = f'x{12 + i}'
            Pd = pose(k, [(0, 'step_touch', {}), (LEAN0, 'lean_pose', {})], t)
            Pd['hyaw'], Pd['tw'] = 0.5, 0.4
            gy = -(1 - z) * 420
            h = 980 * z
            c.save()
            c.rotate(32 * lean, x, gy)
            out = K.O_GROUP_B[i % 4] if i % 2 else K.O_DANCERS[1]
            silhouette(c, lambda: draw(c, k, x, gy, h, Pd, out, E.L_SPOT, t, False), color=(0.04, 0.06, 0.12, 1),
                       halo=(0.6, 0.75, 1, 0.5), halo_blur=8)
            c.restore()
        catch = t < SC_CLUB + 0.45
        sched = [(0, 'hat_tip', dict(start=B_of(SC_CLUB))), (SC_CLUB + 1.0 * BEAT, 'kick', dict(side=1)),
                 (SC_CLUB + 2 * BEAT, 'spin', dict(start='auto')), (SC_CLUB + 3 * BEAT, 'point_hit', dict(start='auto', side=1)),
                 (LEAN0 - 0.05, 'lean_pose', {})]
        P = pose(E.M87, sched, t)
        if t >= LEAN0:
            P['hyaw'], P['tw'] = 0.55 * lean, 0.45 * lean
            P['brow'] = -0.4
        c.save()
        c.rotate(40 * lean, 0, 0)                    # rigid body pivoting about the ankles - heels anchored
        draw(c, E.M87, 0, 0, 1000, P, E.O_SC, E.L_SPOT, t)
        c.restore()
        if lean > 0.05:
            for sd in (-1, 1):
                glow(c, sd * 30, -4, 26, '#c8d8ff', 0.6 * lean)        # the anchor points under the heels
    c.restore()
    if t < SC_CLUB + 0.35:                       # the white hat coming back out of the lens
        k = 1 - ease_out(clamp((t - SC_CLUB) / 0.35), 2)
        hs = 70 + 2400 * k
        c.save()
        c.translate(W * 0.55, H * 0.35)
        c.scale(1, 0.45 + 0.4 * k)
        c.drawCircle(0, 0, hs, paint('#f2f0ea'))
        c.drawCircle(0, 0, hs * 0.62, paint('#141216'))
        c.drawCircle(0, 0, hs * 0.55, paint('#e2e0da'))
        c.restore()


def dangerous(c, t):
    """match cut out of the lean: gold, sunglasses, absolutely still - while a stadium screams"""
    u = u_of(t, DANG, DANG_WIDE)
    rot = 16 * (1 - ease_out(clamp(u / 0.35), 3))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#04040e'))
    c.save()
    c.translate(W / 2, H * 0.6)
    c.rotate(-rot)
    c.translate(-W / 2, -H * 0.6)
    with Layer(c, Cam(0, -700, 1.6 + 0.2 * ease_io(u), 0), 1.0, t):
        stadium(c, t, energy=1.0, seed=5, gold=0.7, tint='#ffd080')
        P = pose(E.M92, [(0, 'toe_stand', dict(start=B_of(DANG) - 2))], t)
        P.update(lsh=0.2, lel=-0.3, rsh=0.2, rel=-0.3, lhand='fist', rhand='fist', brow=-0.4, smile=0.0, blink=0.0, htilt=0.0)
        S = draw(c, E.M92, 0, 0, 1000, P, E.O_DANGEROUS, E.L_GOLD, t)
        sunglasses(c, S)
    c.restore()
    flash_burst(c, t, [DANG + 0.3, DANG + 0.75], n=40, seed=12, area=(0, H * 0.55, W, H))


def dang_wide(c, t):
    """on the strongest guitar hit: pyro - and he finally moves; the whole stadium in gold"""
    u = u_of(t, DANG_WIDE, END)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#04040e'))
    with Layer(c, Cam(0, -900, 0.78 - 0.08 * ease_io(u), 0), 1.0, t):
        stadium(c, t, energy=1.0, seed=5, gold=0.8, tint='#ffd080', rows=16)
        for k, x in enumerate((-1000, -600, 600, 1000)):               # pyro columns
            h = (900 + 300 * math.sin(t * 20 + k)) * (1 - clamp((t - DANG_WIDE) / 1.2) * 0.6)
            beam(c, x, -360, x, -360 - h, 60, 120, '#ffb040', 0.7, blur=20)
            glow(c, x, -360 - h, 160, '#ffd060', 0.8)
        P = pose(E.M92, routine(DANG_WIDE), t)
        S = draw(c, E.M92, 0, 0, 1000, P, E.O_DANGEROUS, E.L_GOLD, t)
        sunglasses(c, S)
    if t - DANG_WIDE < 0.15:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.85, 0.5, 0.6 * (1 - (t - DANG_WIDE) / 0.15)), blend=skia.BlendMode.kPlus))
    rng = np.random.default_rng(31)
    for i in range(70):                                               # golden confetti / sparks
        x0 = rng.uniform(0, W)
        sp = rng.uniform(200, 500)
        yy = (rng.uniform(-H, 0) + (t - DANG_WIDE) * sp) % (H + 200) - 100
        glow(c, x0 + 20 * math.sin(t * 3 + i), yy, 10, '#ffd060', 0.7)


SHOTS = [(BAD_MORPH, bad_morph), (SUBWAY, subway), (TO_STAD, to_stadium), (STAD_WIDE, stad_wide), (HAT_THROW, hat_throw),
         (SC_CLUB, sc_club), (DANG, dangerous), (DANG_WIDE, dang_wide)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    cap(c, t, TO_STAD + 0.3, HAT_THROW - 0.1, ['THE WORLD', 'BECAME HIS STAGE.'], y=300, size=90, accent=(1, GOLD))
    cap(c, t, DANG_WIDE + 0.15, END - 0.1, ['THE KING OF POP.'], y=300, size=100, col=GOLD)
