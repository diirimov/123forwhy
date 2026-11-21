"""SCENE 5 - FIVE BROTHERS, ONE LEGEND. Face -> group -> arena pull-back, crowd of thousands, final golden pose, title."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, noise1, font, text_center)
from world import Cam, cam_path, Layer, CHARS, particles, crowd, light_rig, floor_reflection
from character import outfits, BROTHERS
import choreo
import timing as T

DB = T.db
T0 = DB(18)
T_FINAL = DB(24)
T_SUB = DB(25)
OUT = outfits('arena')
GY = 380
POS = {'tito': (-360, -30), 'jackie': (-185, -50), 'michael': (0, 40), 'marlon': (185, -50), 'jermaine': (360, -30)}
BASE_H = 360
BEAM_COLS = ['#ff3a8a', '#3ac8ff', '#ffb83a', '#9a4aff', '#3affc0']
GOLD = '#ffc85a'


def sched():
    d = DB
    S = {}
    for k in ('jackie', 'marlon'):
        side = -1 if k == 'jackie' else 1
        S[k] = [(0, 'groove', dict(amp=1.1)),
                (d(19), 'step_touch', {}),
                (d(20), 'shimmy', {}),
                (d(21), 'arm_roll', {}),
                (d(22) - 0.1, 'spin', dict(start='auto', length=1.0)),
                (d(22) + T.PERIOD - 0.05, 'point_hit', dict(start='auto', side=side)),
                (d(22) + 2 * T.PERIOD, 'step_touch', {}),
                (d(23), 'kick', dict(side=side)),
                (d(24) - 0.05, 'cheer', {}),
                (d(24) + 2 * T.PERIOD, 'pose_hold', {})]
    S['michael'] = [(0, 'mic_sing', dict(amp=1.0)),
                    (d(19), 'step_touch', {}),
                    (d(20), 'slide', dict(start='auto', dirn=1, dist=0.25, beats=2.0)),
                    (d(20) + 2 * T.PERIOD, 'slide', dict(start='auto', dirn=-1, dist=0.25, beats=2.0)),
                    (d(21), 'arm_roll', dict(amp=1.3)),
                    (d(22) - 0.1, 'spin', dict(start='auto', length=1.0)),
                    (d(22) + T.PERIOD - 0.05, 'point_hit', dict(start='auto', side=1)),
                    (d(22) + 2 * T.PERIOD, 'shimmy', {}),
                    (d(23), 'kick', dict(side=1)),
                    (d(23) + 2 * T.PERIOD, 'spin', dict(start='auto', length=1.0)),
                    (d(24) - 0.08, 'knee_drop', dict(start='auto')),
                    (d(25), 'pose_hold', {})]
    S['tito'] = [(0, 'play', dict(amp=1.3)), (d(24) + 2 * T.PERIOD, 'play', dict(amp=0.5))]
    S['jermaine'] = [(0, 'play', dict(amp=1.3)), (d(24) + 2 * T.PERIOD, 'play', dict(amp=0.5))]
    return S


SCHED = sched()
RIP = {'jackie': 0.035, 'marlon': 0.07, 'michael': 0.0, 'tito': 0.0, 'jermaine': 0.0}


def poses(t):
    return {k: choreo.perform(SCHED[k], t, k, seed=BROTHERS[k].seed, ripple=RIP[k],
                              sing=1.0 if k == 'michael' else (0.5 if k in ('jermaine', 'jackie') else 0.3),
                              base_kw=dict(instrument='guitar' if k == 'tito' else 'bass' if k == 'jermaine' else None))
            for k in POS}


def light_for(t, beat, gold):
    hue = BEAM_COLS[int(beat) % len(BEAM_COLS)]
    rim = mix(hue, GOLD, gold)
    return dict(key=(-0.3, -0.95), amb=mix('#f0d8ff', '#ffe2a8', gold), amb_a=0.22, rim=rim, line='#24102a', floor_shadow=0.45)


def band(c, t, P, L):
    for k in sorted(POS, key=lambda k: POS[k][1]):
        x, dy = POS[k]
        CHARS[k].draw(c, x, GY + dy, BASE_H * BROTHERS[k].height, P[k], OUT[k], L, t)


_rng = np.random.default_rng(1971)
STAND = [(x, y, s) for x, y, s in zip(_rng.uniform(-2600, 2600, 900), _rng.uniform(-1500, 200, 900), _rng.uniform(0.6, 1.4, 900))]


def arena_bg(c, t, beat, gold):
    c.drawRect(skia.Rect.MakeLTRB(-4000, -4000, 4000, 4000), shader_paint(lin_grad((0, -2500), (0, 400),
               [mix('#0a0418', '#2a1808', gold), mix('#1a0a30', '#4a2a10', gold)])))
    # tiers of distant fans: dots + flashbulbs
    for i, (x, y, s) in enumerate(STAND):
        tier_y = y + abs(x) * 0.25
        col = mix(mix('#4a3a6a', BEAM_COLS[i % 5], 0.25), '#7a5a30', gold)
        c.drawCircle(x, tier_y, 12 * s, paint(alpha(col, 0.75)))
        c.drawCircle(x, tier_y + 16 * s, 14 * s, paint(alpha(col, 0.5)))
        if (i * 7919 + int(t * 9)) % 97 == 0:
            glow(c, x, tier_y, 60, '#ffffff', 0.9)
    # big backdrop lighting wall
    for row in range(7):
        for k in range(-11, 12):
            x, y = k * 110, -1450 + row * 120
            a = 0.35 + 0.65 * abs(math.sin(beat * math.pi / 2 + k * 0.35 + row * 0.5))
            col = mix(BEAM_COLS[(k + row) % 5], GOLD, gold)
            c.drawCircle(x, y, 26, paint(alpha(col, 0.25 + 0.55 * a)))
            glow(c, x, y, 70, col, 0.2 * a)
    light_rig(c, -1500, 1500, -1700, 11, t, [mix(cc, GOLD, gold) for cc in BEAM_COLS], beat)
    # stage
    c.drawRect(skia.Rect.MakeLTRB(-1600, GY - 40, 1600, GY + 220), shader_paint(lin_grad((0, GY), (0, GY + 220),
               ['#2a2030', '#0a0610'])))
    c.drawRect(skia.Rect.MakeLTRB(-1600, GY + 200, 1600, GY + 240), paint(mix('#ff3a8a', GOLD, gold)))


def beams(c, t, beat, gold, n=8):
    for i in range(n):
        base_x = -1300 + i * 2600 / (n - 1)
        sweep = math.sin(t * 0.9 + i * 0.8) * 700
        col = mix(BEAM_COLS[i % 5], GOLD, gold)
        beam(c, base_x, -1650, base_x * 0.3 + sweep, GY + 200, 30, 240, col, 0.32, blur=35)


def confetti(c, t, start, n=160, seed=3):
    rng = np.random.default_rng(seed)
    u = t - start
    if u < 0:
        return
    cols = ['#ffd24a', '#ffffff', '#ff5aa0', '#5ad8ff', '#ffb03a']
    for i in range(n):
        x0 = rng.uniform(-W * 0.6, W * 0.6)
        sp = rng.uniform(140, 320)
        ph = rng.uniform(0, 6.28)
        y = -H / 2 - 40 + sp * u - rng.uniform(0, 900)
        if y < -H / 2 - 60 or y > H / 2 + 60:
            continue
        x = x0 + math.sin(u * 2 + ph) * 60
        c.save()
        c.translate(W / 2 + x, H / 2 + y)
        c.rotate(math.degrees(u * 3 + ph))
        c.scale(1, abs(math.sin(u * 5 + ph)) + 0.15)
        c.drawRect(skia.Rect.MakeXYWH(-9, -5, 18, 10), paint(cols[i % 5]))
        c.restore()


def title(c, t):
    a = smoothstep(T_FINAL, T_FINAL + 0.5, t)
    if a <= 0:
        return
    cy = H * 0.2
    # glow plate
    c.drawRect(skia.Rect.MakeWH(W, H * 0.42), shader_paint(lin_grad((0, 0), (0, H * 0.42), [(0.05, 0.02, 0.0, 0.65 * a), (0, 0, 0, 0)])))
    f = font('spartan', 150)
    word = 'THE JACKSON 5'
    # letters drop in one by one, landing on 16ths after the downbeat
    widths = [f.measureText(ch) for ch in word]
    track = 6
    total = sum(widths) + track * (len(word) - 1)
    # scale to fit width
    sc = min(1.0, (W - 90) / total)
    x = W / 2 - total * sc / 2
    c.save()
    for i, (ch, w_) in enumerate(zip(word, widths)):
        ti = T_FINAL + i * T.PERIOD / 4 * 0.5
        u = clamp((t - ti) / 0.35)
        if u <= 0:
            x += (w_ + track) * sc
            continue
        yo = (1 - back_out(u, 2.0)) * -90
        al = min(1, u * 3)
        c.save()
        c.translate(x, cy + yo)
        c.scale(sc, sc)
        gp = shader_paint(lin_grad((0, -130), (0, 10), ['#fff6d8', '#ffd46a', '#c98a1a', '#ffe9a8'], [0, 0.45, 0.75, 1]))
        gp.setAlphaf(al)
        sh = paint((0.1, 0.03, 0.0, 0.7 * al), blur=8)
        c.drawString(ch, 6, 8, f, sh)
        glowp = paint((1, 0.8, 0.4, 0.55 * al), blur=22)
        c.drawString(ch, 0, 0, f, glowp)
        c.drawString(ch, 0, 0, f, gp)
        c.restore()
        x += (w_ + track) * sc
    c.restore()
    # light sweep across the title
    sw = clamp((t - T_FINAL - 0.8) / 1.2)
    if 0 < sw < 1:
        sx = -200 + sw * (W + 400)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(0, cy - 160 * sc, W, 190 * sc))
        c.drawPath(poly_path([(sx - 60, cy - 200), (sx + 20, cy - 200), (sx - 40, cy + 60), (sx - 120, cy + 60)]),
                   paint((1, 1, 0.9, 0.5), blur=10, blend=skia.BlendMode.kPlus))
        c.restore()
    # rule + subtitle
    b = smoothstep(T_SUB, T_SUB + 0.9, t)
    if b > 0:
        ln = (W * 0.6) * ease_out(b, 3)
        c.drawLine(W / 2 - ln / 2, cy + 50, W / 2 + ln / 2, cy + 50, paint((1, 0.83, 0.45, b), style='stroke', width=3))
        fs = font('garamond_i', 54)
        text_center(c, 'A story of five brothers', W / 2, cy + 130, fs, paint((1, 0.95, 0.85, b)))
        text_center(c, 'who changed music forever.', W / 2, cy + 196, fs, paint((1, 0.95, 0.85, b)))


def draw(c, t):
    beat = T.beat_at(t)
    P = poses(t)
    gold = smoothstep(T_FINAL - 0.2, T_FINAL + 0.6, t)
    L = light_for(t, beat, gold)
    mxw = P['michael']['x'] * BASE_H
    keys = [(T0, Cam(mxw + 5, 95, 5.2, -2), None),
            (DB(19), Cam(0, 40, 1.05, 0), lambda u: ease_io(u)),
            (DB(20), Cam(0, -280, 0.5, 0), lambda u: ease_io(u)),
            (DB(21), Cam(-120, -120, 0.68, -4), ease_io),
            (DB(22), Cam(120, -80, 0.78, 4), ease_io),
            (DB(23), Cam(0, 20, 1.02, 0), ease_io),
            (T_FINAL, Cam(0, -60, 0.82, 0), ease_io),
            (T.DURATION, Cam(0, -420, 0.5, 0), lambda u: ease_out(u, 2))]
    cam = cam_path(keys, t)
    for hit in (DB(22) + T.PERIOD, T_FINAL):
        if 0 <= t - hit < 0.3:
            cam.shake = 0.8 * (1 - (t - hit) / 0.3)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#08030f'))
    with Layer(c, cam, 0.55, t):
        arena_bg(c, t, beat, gold)
    with Layer(c, cam, 1.0, t):
        beams(c, t, beat, gold)
        floor_reflection(c, lambda: band(c, t, P, L), GY, 0.18) if cam.z < 1.5 else None
        if gold > 0:
            glow(c, 0, GY - 200, 900, GOLD, 0.35 * gold)
        band(c, t, P, L)
        particles(c, t, 40, (-1200, -1600, 1200, 300), 61, mix('#e8d8ff', GOLD, gold), size=(1.5, 3.5), speed=(8, 22))
    energy = 0.6 + 0.4 * smoothstep(DB(19), DB(20), t)
    with Layer(c, cam, 1.4, t):
        crowd(c, t, 5, energy, '#07030c', mix('#ff6ab0', GOLD, gold), width=4600, seed=88, y0=760, row_gap=105, scale0=1.05,
              beat_phase=beat, lighters=gold > 0.5)
        # stage spill washing over the front rows
        c.drawRect(skia.Rect.MakeLTRB(-4000, 640, 4000, 1500), shader_paint(lin_grad((0, 640), (0, 1300),
                   [alpha(mix('#c86aff', GOLD, gold), 0.35), (0, 0, 0, 0)]), blend=skia.BlendMode.kScreen))
    confetti(c, t, T_FINAL)
    title(c, t)
    # opening: arrives on Michael's face from the TV close-up (match cut on the spin), with a quick flash
    fl = 1 - smoothstep(T0, T0 + 0.18, t)
    if fl > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.9, 1.0, 0.6 * fl)))
