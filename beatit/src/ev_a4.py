"""0:47.2-1:00  THE PRICE OF FAME (spotlight -> flash; photographers; headlines; alone backstage; the mirror) and
THE FINAL CHAPTER (2009 rehearsals in an empty arena; the orbit in which he becomes the boy again; the audiences he inspired)."""
import math
import numpy as np
import skia
from ev_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, back_out, font, text_center, noise1, poly_path, smooth_path,
                       T, E, base_pose, blend, pose, draw, place_head, skel, bg, u_of, cap, stamp, Cam, Layer, crowd, particles,
                       silhouette, floor_reflection, spin_morph, flash_burst, B_of, GOLD, stadium, sunglasses)
import bi_cast as K

F_SPOT, F_PHOTO, F_HEAD, F_GLASS, F_ALONE, F_MIRROR, R_ARENA, R_ORBIT, R_FINAL, END = (
    DB(27), DB(27) + HALF, DB(28), DB(28) + HALF, DB(29), DB(30), DB(31), DB(32), DB(33), 60.0)


def f_spot(c, t):
    """from the crowd: hands in the air, one white spotlight at the stage - it swells into the lens..."""
    u = u_of(t, F_SPOT, F_PHOTO)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#04040e'))
    with Layer(c, Cam(0, -700, 0.7, 0), 1.0, t):
        stadium(c, t, seed=6, rows=8)
        P = pose(E.M92, [(0, 'pose_hold', {})], t)
        S = draw(c, E.M92, 0, 0, 1000, P, E.O_HISTORY, E.L_STADIUM, t)
        sunglasses(c, S)
    beat = T.beat_at(t)
    c.save()
    c.translate(W / 2, H * 1.05)
    crowd(c, t, 2, 1.0, '#020208', '#c8d0ff', width=1600, seed=71, y0=-200, row_gap=180, scale0=2.2, beat_phase=beat)
    c.restore()
    k = ease_in(u, 3)                    # transformation G: the spotlight becomes a photographer's flash
    glow(c, W / 2, H * 0.42, 120 + 1600 * k, '#ffffff', 0.4 + 0.6 * k)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 1, 1, 0.85 * smoothstep(0.75, 1.0, u))))


def photographer(c, x, gy, h, flip, t, key, fire):
    P = base_pose(lsh=0.9, lel=-2.4, rsh=0.9, rel=-2.4, lhand='fist', rhand='fist', hyaw=0.4 * flip, tw=0.3 * flip, brow=0.4, smile=0.2)
    S = draw(c, key, x, gy, h, P, K.O_GROUP_B[1] if flip > 0 else K.O_CREW, E.L_SPOT, t, shadow=False)
    hx, hy = S['head']
    r = S['hr']
    c.drawRoundRect(skia.Rect.MakeXYWH(hx - r * 1.1, hy - r * 0.6, r * 2.2, r * 1.3), r * 0.2, r * 0.2, paint('#141418'))
    c.drawCircle(hx + flip * r * 0.2, hy, r * 0.5, paint('#2a2a34'))
    c.drawCircle(hx + flip * r * 0.2, hy, r * 0.3, paint((0.3, 0.4, 0.7, 0.8)))
    c.drawRect(skia.Rect.MakeXYWH(hx - r * 0.6, hy - r * 1.1, r * 0.8, r * 0.5), paint('#d8d8e0'))
    if fire > 0:
        glow(c, hx - r * 0.2, hy - r * 0.85, r * 4, '#ffffff', fire)
        c.drawCircle(hx - r * 0.2, hy - r * 0.85, r * 0.4, paint((1, 1, 1, fire)))


def f_photo(c, t):
    """he walks into a wall of photographers; flashes go off on every eighth note"""
    u = u_of(t, F_PHOTO, F_HEAD)
    bg(c, ['#0a0a12', '#141420'])
    a = ease_io(u)
    h = 1300 + 600 * a
    P = pose(E.M92, [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))], t)
    P.update(hyaw=0, tw=0, brow=0.2, smile=0.0)
    S = draw(c, E.M92, W / 2, H * 0.9 + 200 * a, h, P, E.O_HISTORY, E.L_SPOT, t)
    sunglasses(c, S)
    e8 = (T.beat_at(t) * 2)
    for i, (x, gy, hh, flip) in enumerate(((W * 0.08, H * 0.95, 1500, 1), (W * 0.92, H * 0.97, 1500, -1), (W * 0.22, H * 1.1, 1900, 1),
                                         (W * 0.8, H * 1.12, 1900, -1), (W * 0.02, H * 1.25, 2300, 1), (W * 0.98, H * 1.25, 2300, -1))):
        fire = max(0.0, 1 - ((e8 + i * 0.37) % 1) / 0.25)
        photographer(c, x, gy, hh, flip, t, f'x{i + 2}', fire)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 1, 1, 0.12 * max(0.0, 1 - (e8 % 1) / 0.2)), blend=skia.BlendMode.kPlus))
    if t - F_PHOTO < 0.15:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 1, 1, 0.85 * (1 - (t - F_PHOTO) / 0.15))))


HEADLINES = [('WORLD EDITION', 'KING OF POP', 'TOUR SELLS OUT WORLDWIDE'), ('EVENING EDITION', 'FANS CAMP OUT', 'FOR DAYS TO SEE HIM'),
             ('MORNING EDITION', 'EVERY MOVE', 'FOLLOWED BY CAMERAS')]


def newspaper(c, cx, cy, w, ang, s, head):
    c.save()
    c.translate(cx, cy)
    c.rotate(ang)
    c.scale(s, s)
    hgt = w * 1.3
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 14, -hgt / 2 + 20, w, hgt), paint((0, 0, 0, 0.5), blur=16))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -hgt / 2, w, hgt), paint('#efe8d6'))
    text_center(c, head[0], 0, -hgt / 2 + 80, font('garamond_b', 52), paint('#1a1410'))
    c.drawLine(-w / 2 + 30, -hgt / 2 + 105, w / 2 - 30, -hgt / 2 + 105, paint('#1a1410', style='stroke', width=4))
    text_center(c, head[1], 0, -hgt / 2 + 230, font('bebas', 150), paint('#141010'))
    text_center(c, head[2], 0, -hgt / 2 + 300, font('spartan_b', 38), paint('#2a1a14'))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 30, -hgt / 2 + 340, w * 0.55, w * 0.45), paint('#8a8478'))
    c.drawCircle(-w / 2 + 30 + w * 0.27, -hgt / 2 + 340 + w * 0.2, w * 0.1, paint('#4a4640'))
    for k in range(14):
        y = -hgt / 2 + 360 + k * 30
        x0 = -w / 2 + 50 + w * 0.57 if k < 9 else -w / 2 + 30
        c.drawLine(x0, y, w / 2 - 30, y, paint((0.3, 0.28, 0.25, 0.6), style='stroke', width=8))
    c.restore()


def f_head(c, t):
    """headlines spin in and stack, one per beat"""
    bg(c, ['#1a1410', '#0a0806'])
    for i, head in enumerate(HEADLINES):
        t0 = F_HEAD + i * BEAT * 0.95
        k = clamp((t - t0) / 0.35)
        if k <= 0:
            continue
        e = ease_out(k, 3)
        ang = (1 - e) * 540 + [-8, 6, -3][i]
        s = 0.2 + 0.8 * e
        newspaper(c, W / 2 + [-60, 70, 0][i], H * 0.52 + [-80, 40, 140][i], 760, ang, s, head)
    flash_burst(c, t, [F_HEAD + 0.1, F_HEAD + 0.55], n=8, seed=21, area=(0, 0, W, H))


def f_glass(c, t):
    """close: the flashes multiply in his dark glasses - and he lowers his head"""
    u = u_of(t, F_GLASS, F_ALONE)
    bg(c, ['#06060c', '#0c0c16'])
    down = ease_io(smoothstep(0.45, 0.9, u))
    P = base_pose(brow=0.45 + 0.3 * down, smile=0.0, hnod=0.02 * down, blink=0.0)
    h = 4200
    gx, gy = place_head(E.M92, P, h, (W / 2, H * 0.42 + 40 * down))
    S = draw(c, E.M92, gx, gy, h, P, E.O_HISTORY, dict(E.L_SPOT, amb_a=0.35), t, shadow=False)
    sunglasses(c, S)
    hx, hy = S['head']
    r = S['hr']
    e8 = T.beat_at(t) * 2
    for sd in (-1, 1):                     # reflections in the lenses
        for j in range(3):
            fire = max(0.0, 1 - ((e8 + j * 0.33 + sd * 0.2) % 1) / 0.3) * (1 - 0.6 * down)
            glow(c, hx + sd * r * 0.36 + (j - 1) * r * 0.12, hy - r * 0.02 + (j % 2) * r * 0.08, r * 0.1, '#ffffff', fire)
    for j in range(5):
        fire = max(0.0, 1 - ((e8 + j * 0.21) % 1) / 0.2) * (1 - down)
        glow(c, [0.1, 0.9, 0.2, 0.8, 0.5][j] * W, [0.15, 0.2, 0.85, 0.8, 0.05][j] * H, 300, '#ffffff', 0.5 * fire)


def f_alone(c, t):
    """backstage, after: a long corridor of road cases; the roar is a glow at the far end; he stands alone"""
    u = u_of(t, F_ALONE, F_MIRROR)
    bg(c, ['#0c0a0e', '#16121a'])
    vx, vy = W / 2, H * 0.42
    c.drawRect(skia.Rect.MakeXYWH(vx - 90, vy - 150, 180, 260), paint('#fff0d8'))
    glow(c, vx, vy - 20, 400, '#ffe0b0', 0.5 + 0.2 * T.env_at('rms', t))
    for sd in (-1, 1):                     # corridor walls in perspective
        c.drawPath(poly_path([(vx + sd * 90, vy - 150), (vx + sd * 900, -200), (vx + sd * 900, H + 200), (vx + sd * 90, vy + 110)]),
                   paint(mix('#1e1a22', '#0e0c10', 0.5 + 0.5 * sd)))
        for k in range(6):
            x0 = vx + sd * (130 + k * 80)
            s_ = 0.35 + k * 0.25
            c.drawRect(skia.Rect.MakeXYWH(x0 - 70 * s_ if sd > 0 else x0 - 70 * s_, vy + 110 - 120 * s_ + k * 60, 140 * s_, 120 * s_),
                       paint('#24202a'))
            c.drawRect(skia.Rect.MakeXYWH(x0 - 70 * s_, vy + 110 - 120 * s_ + k * 60, 140 * s_, 120 * s_),
                       paint('#6a6470', style='stroke', width=3))
    c.drawPath(poly_path([(vx - 90, vy + 110), (vx + 90, vy + 110), (vx + 900, H + 200), (vx - 900, H + 200)]), paint('#1a161c'))
    P = pose(E.M92, [(0, 'look_down', {})], t)
    P.update(lsh=0.15, lel=0.2, rsh=0.25, rel=-0.5, brow=0.6, smile=-0.15, blink=0.3 + 0.4 * (math.sin(t * 1.3) > 0.7))
    h = 1500 * (1 + 0.1 * ease_io(u))
    S = draw(c, E.M92, W * 0.38, H * 0.95, h, P, E.O_HISTORY, dict(E.L_SPOT, amb='#3a3448', amb_a=0.45, rim='#ffe0b0'), t)
    wx, wy = S['arms'][1][2]               # sunglasses in his hand now
    c.drawRoundRect(skia.Rect.MakeXYWH(wx - 30, wy + 10, 70, 26), 10, 10, paint('#0a0a10'))


def f_mirror(c, t):
    """the dressing-room mirror: bulbs around the frame; the face looking back is tired; the bulbs go out one by one"""
    u = u_of(t, F_MIRROR, R_ARENA)
    bg(c, ['#1a1410', '#0e0a08'])
    mr = skia.Rect.MakeXYWH(90, 330, W - 180, 1240)
    c.drawRect(mr.makeOutset(40, 40), paint('#2a1e16'))
    bulbs = []
    for k in range(7):
        bulbs.append((mr.left() + k * mr.width() / 6, mr.top() - 20))
    for k in range(1, 9):
        bulbs.append((mr.left() - 20, mr.top() + k * mr.height() / 9))
        bulbs.append((mr.right() + 20, mr.top() + k * mr.height() / 9))
    out_t = [F_MIRROR + 0.4 + i * 0.065 for i in range(len(bulbs))]
    lit = 0
    c.save()
    c.clipRect(mr)
    c.drawRect(mr, shader_paint(lin_grad((0, mr.top()), (0, mr.bottom()), ['#2a2420', '#14100e'])))
    P = base_pose(brow=0.65, smile=-0.1, ey=0.25, blink=0.35 + 0.65 * (0.4 < (t - F_MIRROR) % 1.4 < 0.55), hnod=0.008,
                  lsh=0.18, lel=0.2, rsh=0.18, rel=0.2)
    h = 2700
    gx, gy = place_head(E.M92, P, h, (W / 2, H * 0.45))
    on_frac = sum(1 for tt in out_t if t < tt) / len(out_t)
    L = dict(key=(0.0, -0.6), amb='#ffd8a8', amb_a=0.3 * on_frac + 0.1, rim='#ffe8c0', line='#1a1008', floor_shadow=0)
    draw(c, E.M92, gx, gy, h, P, E.O_HISTORY, L, t, shadow=False)
    c.drawRect(mr, paint((0, 0, 0, 0.55 * (1 - on_frac))))
    c.drawLine(mr.left() + 100, mr.top(), mr.left() + 500, mr.bottom(), paint((1, 1, 1, 0.05), style='stroke', width=120, blur=30))
    c.restore()
    for (bx, by), tt in zip(bulbs, out_t):
        on = t < tt
        c.drawCircle(bx, by, 22, paint('#fff4d8' if on else '#4a4038'))
        if on:
            glow(c, bx, by, 70, '#ffe0a0', 0.6)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, 0.6 * smoothstep(0.85, 1.0, u))))


# ----------------------------------------------------------------------------- 2009
def arena(c, t, pan=0.0, light=1.0):
    """an empty arena in rehearsal: rows of empty seats, a lighting desk with small lamps, one spotlight on the stage"""
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#03030a'))
    for r in range(14):
        y = H * 0.62 + r * r * 5 + r * 30
        sc = 0.4 + r * 0.08
        for k in range(-30, 30):
            x = W / 2 + (k * 70 * sc) - pan * sc * 400
            if -50 < x < W + 50:
                c.drawRoundRect(skia.Rect.MakeXYWH(x, y, 56 * sc, 40 * sc), 6, 6, paint((0.12, 0.12, 0.2, 0.9)))
    for k in range(-6, 7):
        c.drawRect(skia.Rect.MakeXYWH(W / 2 + k * 160 - pan * 140, H * 0.1, 8, H * 0.3), paint('#0a0a14'))
    c.drawRect(skia.Rect.MakeXYWH(-50, H * 0.1, W + 100, 14), paint('#10101c'))
    for k in range(10):
        glow(c, 60 + k * 110 - pan * 60, H * 0.1 + 20, 18, '#9fb8ff', 0.4)
    c.drawRect(skia.Rect.MakeLTRB(0, H * 0.55, W, H * 0.6), paint('#14141e'))
    beam(c, W / 2, -100, W / 2, H * 0.57, 30, 300, '#ffffff', 0.45 * light, blur=30)
    c.drawOval(skia.Rect.MakeXYWH(W / 2 - 240, H * 0.55, 480, 60), paint((1, 1, 1, 0.45 * light), blur=20))
    desk = H * 0.9
    c.drawRect(skia.Rect.MakeXYWH(W * 0.1 - pan * 300, desk, W * 0.8, 120), paint('#0a0a10'))
    for k in range(6):
        glow(c, W * 0.15 + k * 150 - pan * 300, desk - 10, 30, '#ffcf6a', 0.6)


def r_arena(c, t):
    """2009: a rehearsal, not a concert - an empty arena, one light; he walks into it"""
    u = u_of(t, R_ARENA, R_ORBIT)
    arena(c, t, pan=0.1 * ease_io(u))
    a = ease_io(u_of(t, R_ARENA, R_ARENA + 1.3))
    P = pose(E.M09, [(0, 'walk', dict(start=0.0, dirn=1, speed=0.0))] if a < 0.98 else [(0, 'nod_slow', {})], t)
    P.update(hyaw=0.2 * (1 - a), smile=0.3)
    draw(c, E.M09, W * 0.3 + W * 0.2 * a, H * 0.575, 560, P, E.O_TII, E.L_SPOT, t)
    for i, x in enumerate((W * 0.25, W * 0.7)):                 # two crew silhouettes at the desk
        P2 = base_pose(lsh=0.6, lel=-1.6, rsh=0.6, rel=-1.6)
        P2['spin'] = 0.5
        silhouette(c, lambda x=x, P2=P2: draw(c, f'x{4 + i}', x, H * 1.02, 900, P2, K.O_CREW, E.L_SPOT, t, False), color=(0.02, 0.02, 0.05, 1),
                   halo=(1, 0.8, 0.4, 0.3), halo_blur=8)
    if t - R_ARENA < 0.25:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0, 1 - (t - R_ARENA) / 0.25)))


def r_orbit(c, t):
    """transformation H: the camera orbits him once - for one breath he is the boy from the Jackson 5, same pose - then the King again"""
    u = u_of(t, R_ORBIT, R_FINAL)
    o0, o1 = 56.15, 57.5
    s = ease_io(clamp((t - o0) / (o1 - o0)))
    stage = 0 if s < 0.25 else (1 if s < 0.75 else 2)
    pan = 0.3 + 1.2 * s
    arena(c, t, pan=pan)
    sched = [(0, 'nod_slow', {}), (R_ORBIT + 0.25, 'arm_roll', {}), (o0 - 0.05, 'point_hit', dict(start=B_of(o0 - 0.3), side=1))]
    if stage == 1:
        key, out, h = 'michael', E.O_KID_TV['michael'], 900
    else:
        key, out, h = E.M09, E.O_TII, 900 * 1.62
    P = pose(key, sched, t)
    P['spin'] = s
    gy = H * 0.86
    if stage == 1:                         # the memory: warm 1970 stage colour bleeds in behind the boy
        a = math.sin(math.pi * clamp((s - 0.25) / 0.5))
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.55, 0.25, 0.25 * a), blend=skia.BlendMode.kPlus))
        for j in range(12):
            ang = j / 12 * 2 * math.pi + t
            glow(c, W / 2 + math.cos(ang) * 420, H * 0.45 + math.sin(ang) * 420, 60, ['#ffd060', '#ff7ab0', '#7ad8ff'][j % 3], 0.4 * a)
    beam(c, W / 2, -100, W / 2, gy, 40, 520, '#ffffff', 0.3, blur=40)
    floor_reflection(c, lambda: draw(c, key, W / 2, gy, h, P, out, E.L_SPOT, t, False), gy, 0.2)
    draw(c, key, W / 2, gy, h, P, out, E.L_SPOT, t)
    for k in (0.25, 0.75):                  # the edge-on moment is wrapped in light, never a half-morphed face
        d = 1 - abs(s - k) / 0.07
        if d > 0:
            glow(c, W / 2, gy - h * 0.5, 600, '#fff4dc', 0.75 * d)


def r_final(c, t):
    """he lifts his arm to the dark - and behind him rise the audiences of forty years; the light fades"""
    u = u_of(t, R_FINAL, END)
    arena(c, t, pan=1.5, light=1 - 0.6 * smoothstep(59.0, 59.9, t))
    rise = ease_out(clamp(u / 0.6), 2)
    beat = T.beat_at(t)
    c.save()                                # ghost audiences: one vast silhouette crowd climbing up the dark
    lp = skia.Paint()
    lp.setAlphaf(0.85 * rise)
    c.saveLayer(None, lp)
    for j, (y0, sc, col) in enumerate(((0.42, 0.6, '#6a7ab8'), (0.5, 0.8, '#8a6ab8'), (0.6, 1.0, '#b88a5a'))):
        c.save()
        c.translate(W / 2, H * (y0 + 0.25 * (1 - rise)))
        crowd(c, t, 3, 1.0, mix('#0a0a1e', col, 0.25), col, width=2600, seed=900 + j, y0=0, row_gap=90, scale0=sc, beat_phase=beat,
              lighters=True)
        c.restore()
    c.restore()
    c.restore()
    glow(c, W / 2, H * 0.45, 900, '#ffd8a0', 0.18 * rise)
    P = pose(E.M09, [(0, 'point_hit', dict(start=B_of(R_FINAL - 0.6), side=1)), (R_FINAL + 0.1, 'pose_hold', {})], t)
    P.update(smile=0.5, ey=-0.5)
    h = 900 * 1.62 * (1 - 0.18 * ease_io(u))
    gy = H * 0.86 - 60 * ease_io(u)
    beam(c, W / 2, -100, W / 2, gy, 40, 520, '#ffffff', 0.32 * (1 - smoothstep(59.0, 59.9, t)), blur=40)
    draw(c, E.M09, W / 2, gy, h, P, E.O_TII, dict(E.L_SPOT, rim='#ffe8c0'), t)


SHOTS = [(F_SPOT, f_spot), (F_PHOTO, f_photo), (F_HEAD, f_head), (F_GLASS, f_glass), (F_ALONE, f_alone), (F_MIRROR, f_mirror),
         (R_ARENA, r_arena), (R_ORBIT, r_orbit), (R_FINAL, r_final)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)


def captions(c, t):
    cap(c, t, F_SPOT + 0.25, F_ALONE - 0.12, ['THE WORLD LOVED HIM…'], y=300, size=86)
    cap(c, t, F_ALONE + 0.15, R_ARENA - 0.15, ['BUT FAME HAD A PRICE.'], y=300, size=86, col=(0.95, 0.85, 0.75))
    stamp(c, t, R_ARENA + 0.3, R_FINAL - 0.2, '2009 · REHEARSALS', y=1480, size=38)
    cap(c, t, R_ARENA + 0.35, R_FINAL - 0.1, ['1958 — 2009'], y=300, size=92)
    cap(c, t, R_FINAL + 0.15, 59.9, ['THE KING OF POP.'], y=300, size=108, col=GOLD)
