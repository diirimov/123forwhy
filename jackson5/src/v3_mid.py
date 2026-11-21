"""V3 0:17-0:48  THE RISE (V2 shots, recut) -> MICHAEL'S OWN PATH (growing up) -> THE SOLO SUPERSTAR (1979-1983)."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, glow, beam, clamp, ease_io, ease_out, ease_in,
                 back_out, smoothstep, noise1, poly_path, font, text_center)
from world import Cam, Layer, particles, silhouette, crowd
from character import outfits, DESIGNS, base_pose, MICHAEL_OUTFITS, Outfit
import choreo
import timing as T
import v2_rise as R2
import v2_fame as F2
import scene3
import scene4
from v3_common import cap, remap, pose, draw_char, place_head

DB = T.db
BEAT = T.PERIOD
HB = 2 * BEAT
R_APOLLO, R_INSIDE, R_SING, R_DJ, R_STORE, R_CITY, R_TV = DB(6), DB(7), DB(8), DB(8) + HB, DB(9), DB(9) + HB, DB(10)
M_LEAVE, M_GROW, M_STUDIO, M_STAGE79 = DB(11), DB(12), DB(13), DB(14)
S_RECORD, S_SIL, S_DANCE, S_CROWD, S_TVWALL, S_GLOVE, END = (DB(15), DB(15) + HB, DB(16), DB(17), DB(17) + HB,
                                                               DB(18), DB(19))
START = R_APOLLO
O72, O79, O82 = MICHAEL_OUTFITS['michael72'], MICHAEL_OUTFITS['michael79'], MICHAEL_OUTFITS['michael82']
O82_HAT = Outfit(**{**O82.__dict__, 'hat': '#0c0c10'})
O79_CASUAL = Outfit(shirt='#d8c4a0', pants='#5a4a3a', collar='#efe6d6', flare=True, stripes='#b8a07a')
L_WARMSTAGE = dict(key=(-0.3, -0.95), amb='#ffd8a8', amb_a=0.2, rim='#ffe8c0', line='#2a1410', floor_shadow=0.45)
L_COOL = dict(key=(-0.2, -0.98), amb='#e0e8ff', amb_a=0.15, rim='#cfe6ff', line='#141020', floor_shadow=0.45)


# --------------------------------------------------------------------------- MICHAEL'S OWN PATH
def leave(c, t):
    """the brothers bow out and walk into the wings; the teenage Michael stays by the microphone,
    looking across the dark stage at a single spotlight waiting for him"""
    u = clamp((t - M_LEAVE) / (M_GROW - M_LEAVE))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a0612'))
    c.save()
    c.translate(W / 2, H * 0.55)
    s = 0.95 + 0.08 * ease_io(u)
    c.scale(s, s)
    c.translate(-W / 2, -H * 0.55)
    # dimmed TV-show stage behind
    c.save()
    c.translate(W / 2, H * 0.42)
    c.scale(0.7, 0.7)
    scene4.opart(c, t, T.beat_at(t), cx=0, cy=-380, scale=0.9, hot=0.0)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0.02, 0.0, 0.04, 0.72)))
    gy = H * 0.8
    c.drawRect(skia.Rect.MakeLTRB(0, gy - 20, W, H), shader_paint(lin_grad((0, gy), (0, H), ['#24183a', '#0a0612'])))
    # the waiting spotlight, stage left
    beam(c, W * 0.16, -100, W * 0.16, gy + 20, 40, 170, '#fff4dc', 0.5, blur=30)
    c.drawOval(skia.Rect.MakeXYWH(W * 0.16 - 190, gy - 10, 380, 70), paint((1, 0.95, 0.8, 0.5), blur=20))
    # four brothers walk off into the right wing (silhouettes, backs to us)
    def bros():
        for i, k in enumerate(['jermaine', 'marlon', 'tito', 'jackie']):
            x = W * 0.68 + 60 + i * 110 + 520 * ease_in(clamp((t - M_LEAVE - i * 0.12) / 2.2), 1.3)
            P = pose(k, [(0, 'walk_away', dict(start=0.0, speed=0.0))], t + i * 0.15)
            draw_char(c, k, x, gy - 10 * i, 560 * DESIGNS[k].height * 1.1, P, outfits('tv')[k], L_COOL, t, shadow=False)
    silhouette(c, bros, color=(0.05, 0.03, 0.08, 1.0), halo=(0.6, 0.5, 0.9, 0.5), halo_blur=10)
    # teen Michael by the mic, turns his head toward the light
    look = -0.9 * smoothstep(0.25, 0.55, u)
    P = base_pose(hyaw=0.45 * look, ex=look, brow=0.4, smile=0.25 * smoothstep(0.6, 0.9, u), blink=0.0)
    P['tw'] = 0.3 * look
    draw_char(c, 'michael72', W * 0.52, gy + 40, 980, P, O72, dict(L_COOL, rim='#fff4dc', key=(-0.9, -0.4)), t)
    c.drawLine(W * 0.6, gy + 40, W * 0.6, gy - 560, paint('#101014', style='stroke', width=8))
    c.drawCircle(W * 0.6, gy - 575, 20, paint('#9a9aa6'))
    c.restore()


def grow(c, t):
    """he walks across the dark stage through three pools of light - and grows up as he goes: 1972, 1979, 1982"""
    u = clamp((t - M_GROW) / (M_STUDIO - M_GROW))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#06040c'))
    gy = H * 0.82
    pools = [W * 0.18, W * 0.5, W * 0.82]
    years = ['1972', '1979', '1982']
    stage = min(2, int(u * 3))
    for i, px in enumerate(pools):
        on = smoothstep(i / 3 - 0.08, i / 3 + 0.02, u)
        beam(c, px, -100, px, gy + 20, 30, 150, '#fff4dc', 0.42 * on, blur=26)
        c.drawOval(skia.Rect.MakeXYWH(px - 170, gy - 8, 340, 60), paint((1, 0.95, 0.8, 0.45 * on), blur=18))
        if on > 0:
            text_center(c, years[i], px, gy + 150, font('spartan_b', 64), paint((1, 0.9, 0.7, 0.85 * on)))
    x = W * 0.08 + (W * 0.84) * ease_io(u)
    key, outfit, hh = [('michael72', O72, 900), ('michael79', O79, 1060), ('michael84', O82, 1120)][stage]
    P = pose(key, [(0, 'walk', dict(start=0.0, speed=0.0))], t)
    P['hyaw'] = 0.35
    P['smile'] = 0.3 + 0.2 * stage
    draw_char(c, key, x, gy, hh, P, outfit, dict(L_COOL, rim='#fff4dc'), t)
    # a soft bloom hides each change of age as he enters a new pool
    for k in (1 / 3, 2 / 3):
        d = 1 - abs(u - k) / 0.05
        if d > 0:
            glow(c, x, gy - hh * 0.5, 700, '#fff4dc', 0.9 * d)


def studio(c, t):
    """recording his own music: headphones on, eyes closed, a producer listening behind the glass"""
    u = clamp((t - M_STUDIO) / (M_STAGE79 - M_STUDIO))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#2a3440', '#1a2028', '#141418'])))
    for k in range(6):
        c.drawRoundRect(skia.Rect.MakeXYWH(-80 + k * 210, 140, 180, 820), 14, 14, paint((0.35, 0.42, 0.48, 0.35)))
    # control-room window behind him with a producer silhouette nodding
    wr = skia.Rect.MakeXYWH(W * 0.55, 380, 420, 330)
    c.drawRect(wr, shader_paint(lin_grad((0, wr.top()), (0, wr.bottom()), ['#ffd89a', '#c88a4a'])))
    bob = 6 * abs(math.sin(math.pi * T.beat_at(t)))
    c.drawCircle(W * 0.55 + 220, 560 + bob, 60, paint('#1a1210'))
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.55 + 120, 610 + bob, 200, 140), 50, 50, paint('#1a1210'))
    c.drawRect(wr, paint('#3a2a20', style='stroke', width=18))
    glow(c, W * 0.3, H * 0.4, 600, '#ffd8a0', 0.25)
    P = pose('michael79', [(0, 'groove', dict(amp=0.5, arms=False))], t, sing=1.3)
    P.update(headphones=True, lsh=0.6, lel=-1.6, rsh=0.35, rel=-2.0, lhand='open', rhand='relaxed', blink=0.6, brow=0.5)
    h = 2300 * (1 + 0.06 * ease_io(u))
    gx, gy = place_head('michael79', P, h, (W * 0.42, H * 0.43))
    draw_char(c, 'michael79', gx, gy, h, P, O79_CASUAL, dict(L_WARMSTAGE, rim='#9fe8ff'), t, shadow=False)
    # big studio mic + pop filter in front (to the side, mouth stays visible)
    mx, my = W * 0.78, H * 0.52
    c.drawRoundRect(skia.Rect.MakeXYWH(mx - 80, my - 130, 160, 260), 80, 80, shader_paint(lin_grad((mx - 80, 0), (mx + 80, 0),
                    ['#3a3a42', '#e8e8f2', '#5a5a62', '#2a2a30'])))
    c.drawRect(skia.Rect.MakeXYWH(mx - 12, my + 130, 24, 800), paint('#141418'))


def stage79(c, t):
    """his own stage: tuxedo, white socks, a spin and a kick - and a crowd that is now there for him"""
    beat = T.beat_at(t)
    u = clamp((t - M_STAGE79) / (S_RECORD - M_STAGE79))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#2a0e08', '#5a1e10', '#1a0606'])))
    for k in range(24):                 # warm bulb wall
        a = k / 24 * math.pi
        for j in range(4):
            r = 300 + j * 120
            on = (k + j + int(beat * 2)) % 5 == 0
            c.drawCircle(W / 2 + math.cos(a) * r, H * 0.48 - math.sin(a) * r, 9 if on else 6,
                         paint((1, 0.85, 0.5, 0.95 if on else 0.4)))
    gy = H * 0.74
    c.drawRect(skia.Rect.MakeLTRB(0, gy - 30, W, H), shader_paint(lin_grad((0, gy), (0, H), ['#4a2010', '#140604'])))
    beam(c, W / 2, -100, W / 2, gy, 40, 260, '#fff0d0', 0.45, blur=36)
    sched = [(0, 'step_touch', {}), (M_STAGE79 + 2 * BEAT - 0.1, 'spin', dict(start='auto')),
             (M_STAGE79 + 3 * BEAT - 0.05, 'kick', dict(side=1))]
    P = pose('michael79', sched, t, sing=0.8)
    draw_char(c, 'michael79', W / 2, gy, 1050, P, O79, L_WARMSTAGE, t)
    c.save()
    c.translate(W / 2, H * 0.9)
    crowd(c, t, 2, 0.4 + 0.6 * u, '#140604', '#ffb070', width=1800, seed=79, y0=0, row_gap=130, scale0=1.2, beat_phase=beat)
    c.restore()


# --------------------------------------------------------------------------- THE SOLO SUPERSTAR
def record82(c, t):
    u = clamp((t - S_RECORD) / (S_SIL - S_RECORD))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.45), H * 0.8, ['#2a1a3a', '#0c0818'])))
    zoom = 1 + 3.0 * ease_in(clamp((u - 0.5) / 0.5), 3)
    c.save()
    c.translate(W / 2, H * 0.47)
    c.scale(zoom, zoom)
    c.drawCircle(0, 0, 470, paint('#111014'))
    for k in range(30):
        c.drawCircle(0, 0, 170 + k * 10, paint((0.3, 0.3, 0.34, 0.5), style='stroke', width=1.2))
    for a0 in (30, 210):
        p = skia.Path()
        p.moveTo(0, 0)
        p.arcTo(skia.Rect.MakeXYWH(-460, -460, 920, 920), a0, 24, False)
        p.close()
        c.drawPath(p, paint((1, 1, 1, 0.12)))
    c.rotate((t - S_RECORD) * 220)
    c.drawCircle(0, 0, 150, paint('#e8e2d8'))          # plain label - no album artwork
    text_center(c, 'MICHAEL JACKSON', 0, -40, font('spartan', 30), paint('#1a1414'))
    text_center(c, 'THRILLER', 0, 20, font('spartan', 48), paint('#8a1a1a'))
    text_center(c, '1982', 0, 70, font('spartan_b', 26), paint('#1a1414'))
    c.drawCircle(0, 0, 10, paint('#111'))
    c.restore()
    if u > 0.8:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 1, 1, ease_in((u - 0.8) / 0.2, 2))))


def sil82(c, t):
    """spotlights blast on: the early-80s silhouette - fedora, sequins, one glove"""
    u = clamp((t - S_SIL) / (S_DANCE - S_SIL))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.4), H * 0.9, ['#f4f6ff', '#8aa0ff', '#14183a'],
                                                             [0, 0.35, 1])))
    for k in range(7):
        a = -60 + k * 20
        beam(c, W / 2, H * 0.35, W / 2 + math.sin(math.radians(a)) * 2000, H * 0.35 + math.cos(math.radians(a)) * 2000 * -1,
             20, 300, '#ffffff', 0.25, blur=30)
    gy = H * 0.8
    P = pose('michael84', [(0, 'hat_pose', dict(start=T.beat_at(S_SIL) - T.PHASE))], t)
    def fig():
        draw_char(c, 'michael84', W / 2, gy, 1250, P, O82_HAT, L_COOL, t, shadow=False)
    silhouette(c, fig, color=(0.02, 0.02, 0.05, 1.0), halo=(1, 1, 1, 0.8), halo_blur=12)
    # the glove still sparkles through the silhouette
    S = __import__('world').CHARS['michael84'].skeleton(W / 2, gy, 1250, dict(P))
    wx, wy = S['arms'][1][2]
    for k in range(10):
        a = k / 10 * 2 * math.pi + t * 3
        glow(c, wx + math.cos(a) * 30, wy + math.sin(a) * 30, 28, '#ffffff', 0.6)
    glow(c, wx, wy, 90, '#ffffff', 0.7)


def dance82(c, t):
    beat = T.beat_at(t)
    u = clamp((t - S_DANCE) / (S_CROWD - S_DANCE))
    cam = Cam(0, 120, 1.35 - 0.2 * ease_io(u), 2 * math.sin(u * math.pi))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#06061a'))
    with Layer(c, cam, 0.6, t):
        c.drawRect(skia.Rect.MakeLTRB(-2400, -2400, 2400, 380), shader_paint(lin_grad((0, -1600), (0, 380), ['#06061a', '#1a1a4a'])))
        for i in range(9):
            x = -1600 + i * 400
            beam(c, x, -1600, x * 0.2 + 300 * math.sin(t + i), 420, 20, 220, ['#ffffff', '#9fd8ff', '#c8a0ff'][i % 3], 0.3, blur=36)
    with Layer(c, cam, 1.0, t):
        c.drawRect(skia.Rect.MakeLTRB(-1600, 330, 1600, 1400), shader_paint(lin_grad((0, 330), (0, 900), ['#2a2a4a', '#08081a'])))
        sched = [(0, 'moonwalk', dict(start=T.beat_at(S_DANCE) - T.PHASE, dirn=-1, speed=0.18)), (S_DANCE + 2 * BEAT - 0.1, 'spin', dict(start='auto')),
                 (S_DANCE + 3 * BEAT - 0.05, 'toe_stand', dict(start='auto'))]
        P = pose('michael84', sched, t)
        x0 = 330
        draw_char(c, 'michael84', x0, 380, 360 * DESIGNS['michael84'].height, P, O82, L_COOL, t)
    with Layer(c, cam, 1.4, t):
        crowd(c, t, 3, 1.0, '#05051a', '#9fb8ff', width=3200, seed=83, y0=700, row_gap=120, scale0=1.0, beat_phase=beat)


def crowd82(c, t):
    """the crowd becomes enormous - a tiny figure in one spotlight, a sea of people and flashbulbs"""
    beat = T.beat_at(t)
    u = clamp((t - S_CROWD) / (S_TVWALL - S_CROWD))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#05051a', '#14143a'])))
    beam(c, W / 2, -100, W / 2, H * 0.36, 20, 90, '#ffffff', 0.6, blur=20)
    P = pose('michael84', [(0, 'toe_stand', dict(start=0.0))], t)
    draw_char(c, 'michael84', W / 2, H * 0.36, 200, P, O82, L_COOL, t)
    c.save()
    c.translate(W / 2, H * 0.4)
    s = 0.5 + 0.1 * ease_io(u)
    c.scale(s, s)
    crowd(c, t, 11, 1.0, '#07071c', '#b8c8ff', width=3400, seed=820, y0=80, row_gap=150, scale0=0.75, beat_phase=beat, lighters=True)
    c.restore()
    rng = np.random.default_rng(int(t * 10))
    for i in range(10):
        glow(c, rng.uniform(0, W), rng.uniform(H * 0.4, H), 60, '#ffffff', 0.8)


def tvwall(c, t):
    """a wall of television sets, every screen showing the same dancing silhouette"""
    beat = T.beat_at(t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c0a10'))
    for r in range(5):
        for k in range(3):
            x, y = 40 + k * 340, 160 + r * 330
            c.drawRoundRect(skia.Rect.MakeXYWH(x, y, 320, 300), 26, 26, paint('#2a241e'))
            scr = skia.Rect.MakeXYWH(x + 22, y + 22, 230, 240)
            c.drawRoundRect(scr, 30, 30, shader_paint(rad_grad((scr.centerX(), scr.centerY()), 180, ['#b8d0ff', '#5a6aa8'])))
            c.save()
            c.clipRRect(skia.RRect.MakeRectXY(scr, 30, 30))
            P = pose('michael84', [(0, 'moonwalk', dict(start=0.0, dirn=-1, speed=0.0))], t + (r * 3 + k) * 0.04)
            silhouette(c, lambda: draw_char(c, 'michael84', scr.centerX(), scr.bottom() - 10, 200, P, O82, L_COOL, t, shadow=False),
                       color=(0.05, 0.05, 0.12, 1))
            for yy in range(int(scr.top()), int(scr.bottom()), 6):
                c.drawLine(scr.left(), yy, scr.right(), yy, paint((0, 0, 0, 0.12), style='stroke', width=2))
            c.restore()
            c.drawCircle(x + 286, y + 80, 12, paint('#8a7a6a'))
            c.drawCircle(x + 286, y + 130, 12, paint('#8a7a6a'))


def glove(c, t):
    """close-up: the single sparkling glove raised into the light"""
    u = clamp((t - S_GLOVE) / (END - S_GLOVE))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W * 0.6, H * 0.3), H, ['#2a2a5a', '#0a0a1a'])))
    beam(c, W * 0.6, -200, W * 0.55, H * 0.5, 30, 320, '#ffffff', 0.4, blur=40)
    P = base_pose(rsh=2.45 + 0.15 * ease_out(u, 2), rel=0.35, rhand='open', lsh=0.2, lel=0.2, hyaw=0.3, ey=-0.7, smile=0.2, blink=0.3)
    h = 1700
    gx, gy = place_head('michael84', P, h, (W * 0.4, H * 0.64))
    draw_char(c, 'michael84', gx, gy, h, P, O82, dict(L_COOL, rim='#ffffff'), t, shadow=False)
    S = __import__('world').CHARS['michael84'].skeleton(gx, gy, h, dict(P))
    wx, wy = S['arms'][1][2]
    for k in range(16):
        a = k / 16 * 2 * math.pi + t * 2
        r = 60 + 30 * math.sin(t * 5 + k)
        glow(c, wx + math.cos(a) * r, wy - 60 + math.sin(a) * r, 26, '#ffffff', 0.55)
    glow(c, wx, wy - 60, 200, '#ffffff', 0.45)


SHOTS = [
    (R_APOLLO, remap(R2.apollo_exterior, R2.E_APOLLO, R_APOLLO)),
    (R_INSIDE, remap(R2.apollo_inside, R2.E_INSIDE, R_INSIDE)),
    (R_SING, remap(F2.f_sing, F2.F_SING, R_SING)),
    (R_DJ, remap(F2.f_dj, F2.F_DJ, R_DJ)),
    (R_STORE, remap(F2.f_store, F2.F_STORE, R_STORE)),
    (R_CITY, remap(F2.f_city, F2.F_CITY, R_CITY)),
    (R_TV, remap(F2.g_tv, F2.G_TV, R_TV)),
    (M_LEAVE, leave), (M_GROW, grow), (M_STUDIO, studio), (M_STAGE79, stage79),
    (S_RECORD, record82), (S_SIL, sil82), (S_DANCE, dance82), (S_CROWD, crowd82), (S_TVWALL, tvwall), (S_GLOVE, glove),
]


def draw(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)
    for tc in (R_INSIDE, R_TV, M_LEAVE, S_DANCE, S_GLOVE):
        fl = 1 - smoothstep(tc, tc + 0.22, t)
        if 0 < fl < 1 and t >= tc:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.95, 0.88, 0.45 * fl)))
    cap(c, t, R_APOLLO + 0.2, R_INSIDE + 0.4, ['1967: AMATEUR NIGHT', 'AT THE APOLLO.'], y=300, size=80)
    cap(c, t, R_INSIDE + 0.7, R_STORE - 0.1, ['THEN FIVE BROTHERS', 'BECAME STARS.'], y=1440, size=86)
    cap(c, t, R_STORE + 0.15, M_LEAVE - 0.1, ['THEIR FIRST FOUR MOTOWN', 'SINGLES ALL HIT NO. 1.'], y=1440, size=82)
    cap(c, t, M_LEAVE + 0.4, M_STUDIO - 0.1, ['BUT MICHAEL WANTED', 'HIS OWN PATH.'], y=300, size=88)
    cap(c, t, M_STUDIO + 0.2, S_RECORD - 0.1, ['AND SOON, THE WORLD', 'KNEW HIS NAME.'], y=300, size=88)
    cap(c, t, S_RECORD + 0.2, S_CROWD - 0.1, ['1982: THRILLER', 'CHANGED EVERYTHING.'], y=300, size=90)
    cap(c, t, S_CROWD + 0.15, END - 0.1, ['HE WAS NOW A', 'GLOBAL SUPERSTAR.'], y=300, size=90)
