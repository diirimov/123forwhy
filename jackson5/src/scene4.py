"""SCENE 4 - THE WORLD DISCOVERS THEM. 1969 TV variety stage: op-art backdrop, group choreography,
Michael's slide (tracking shot), silhouette sequence, close-up + spin that match-cuts into the arena."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, noise1, font, text_center)
from world import Cam, cam_path, Layer, CHARS, particles, silhouette, floor_reflection, light_rig
from character import outfits, BROTHERS
import choreo
import timing as T

DB = T.db
T0 = DB(13)
T_SLIDE = DB(14)
T_SIL = DB(16)
T_CLOSE = DB(17)
T_END = DB(18)
OUT = outfits('tv')
GY = 380
POS = {'tito': (-360, -30), 'jackie': (-185, -50), 'michael': (0, 30), 'marlon': (185, -50), 'jermaine': (360, -30)}
BASE_H = 360
PAL = ['#ff7a1a', '#7a2aa0', '#1ab8b8', '#ffc83a', '#e0306a']
LIGHT = dict(key=(-0.4, -0.9), amb='#ffe6c8', amb_a=0.15, rim='#5af0ff', line='#2a1028', floor_shadow=0.45)


def sched():
    d = DB
    S = {}
    for k in ('jackie', 'marlon'):
        side = -1 if k == 'jackie' else 1
        S[k] = [(0, 'step_touch', {}),
                (d(14), 'arm_roll', {}),
                (d(15), 'step_touch', dict(clap=True)),
                (d(16), 'point_hit', dict(start='auto', side=side)),
                (d(16) + 2 * T.PERIOD, 'spin', dict(start='auto', length=1.0)),
                (d(16) + 3 * T.PERIOD, 'shimmy', {}),
                (d(17), 'groove', dict(amp=1.2))]
    S['michael'] = [(0, 'step_touch', {}),
                    (d(14), 'slide', dict(start='auto', dirn=1, dist=0.75, beats=3.0)),
                    (d(14) + 3 * T.PERIOD, 'kick', dict(side=-1)),
                    (d(15), 'slide', dict(start='auto', dirn=-1, dist=0.75, beats=3.0)),
                    (d(15) + 3 * T.PERIOD, 'point_hit', dict(start='auto', side=1)),
                    (d(16), 'point_hit', dict(start='auto', side=1)),
                    (d(16) + 2 * T.PERIOD, 'spin', dict(start='auto', length=1.0)),
                    (d(16) + 3 * T.PERIOD, 'shimmy', {}),
                    (d(17), 'mic_sing', dict(amp=1.2)),
                    (d(17) + 3 * T.PERIOD, 'spin', dict(start='auto', length=1.0))]
    S['tito'] = [(0, 'play', dict(amp=1.2))]
    S['jermaine'] = [(0, 'play', dict(amp=1.2))]
    return S


SCHED = sched()
RIP = {'jackie': 0.035, 'marlon': 0.07, 'michael': 0.0, 'tito': 0.0, 'jermaine': 0.0}


def poses(t):
    out = {}
    for k in POS:
        out[k] = choreo.perform(SCHED[k], t, k, seed=BROTHERS[k].seed, ripple=RIP[k],
                                sing=1.0 if k == 'michael' else (0.4 if k == 'jermaine' else None),
                                base_kw=dict(instrument='guitar' if k == 'tito' else 'bass' if k == 'jermaine' else None))
    return out


def band(c, t, P, L, keys=None):
    for k in sorted(POS, key=lambda k: POS[k][1]):
        if keys and k not in keys:
            continue
        x, dy = POS[k]
        CHARS[k].draw(c, x, GY + dy, BASE_H * BROTHERS[k].height, P[k], OUT[k], L, t)


def opart(c, t, beat, cx=0, cy=-700, scale=1.0, hot=0.0):
    """concentric 60s op-art discs, rotating, pulsing on the beat"""
    pulse = 1 + 0.03 * math.exp(-(beat % 1) * 5)
    for k in range(14, 0, -1):
        r = k * 130 * scale * pulse
        col = PAL[k % len(PAL)]
        c.drawCircle(cx, cy, r, paint(mix(col, '#ff9a3a', hot)))
    c.save()
    c.rotate(t * 12, cx, cy)
    for k in range(16):
        a = k / 16 * 2 * math.pi
        p = poly_path([(cx, cy), (cx + math.cos(a) * 2200, cy + math.sin(a) * 2200),
                       (cx + math.cos(a + 0.1) * 2200, cy + math.sin(a + 0.1) * 2200)])
        c.drawPath(p, paint((1, 1, 1, 0.08)))
    c.restore()
    c.drawCircle(cx, cy, 150 * scale, paint('#fff1c8'))
    text_center(c, 'J5', cx, cy + 45 * scale, font('spartan', 140 * scale), paint(mix('#7a2aa0', '#ff7a1a', hot)))


def stage_set(c, t, beat, hot=0.0):
    c.drawRect(skia.Rect.MakeLTRB(-2400, -2600, 2400, GY), paint(mix('#1a0a2a', '#ff7a1a', hot)))
    opart(c, t, beat, hot=hot)
    # stepped risers + light rig
    light_rig(c, -1300, 1300, -1550, 9, t, PAL, beat)
    c.drawRect(skia.Rect.MakeLTRB(-1400, GY - 130, 1400, GY - 60), paint(mix('#2a1440', '#ff9a4a', hot)))
    for k in range(-13, 14):
        x = k * 100
        on = (k + int(beat * 2)) % 4 == 0
        c.drawRect(skia.Rect.MakeXYWH(x + 8, GY - 120, 84, 50), paint(alpha(PAL[(k + 13) % 5], 0.85 if on else 0.35)))
    # glossy floor with perspective lines
    c.drawRect(skia.Rect.MakeLTRB(-2400, GY - 60, 2400, GY + 1600), shader_paint(lin_grad((0, GY), (0, GY + 900),
               [mix('#2a1838', '#ff8a3a', hot * 0.7), '#0e0614'])))
    for k in range(-24, 25):
        c.drawLine(k * 70, GY - 60, k * 300, GY + 1400, paint((1, 1, 1, 0.07), style='stroke', width=3))


def tv_camera(c, x, y, s):
    """1969 studio TV camera on a pedestal (foreground framing device)"""
    c.drawRect(skia.Rect.MakeXYWH(x - 40 * s, y, 80 * s, 600 * s), paint('#1a1a1e'))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 220 * s, y - 220 * s, 380 * s, 230 * s), 24 * s, 24 * s, paint('#3a3a42'))
    c.drawRoundRect(skia.Rect.MakeXYWH(x - 220 * s, y - 220 * s, 380 * s, 230 * s), 24 * s, 24 * s, paint('#6a6a72', style='stroke', width=5))
    for k in range(4):
        a = k * 90
        lx = x + 160 * s + 60 * s * math.cos(math.radians(a)) * 0.3
        ly = y - 105 * s + 70 * s * math.sin(math.radians(a))
        c.drawRect(skia.Rect.MakeXYWH(lx, ly - 22 * s, 90 * s, 44 * s), paint('#222228'))
    glow(c, x - 180 * s, y - 190 * s, 26 * s, '#ff2a1a', 0.9)
    c.drawString('TV-2', x - 150 * s, y - 120 * s, font('spartan_b', 50 * s), paint('#d8d8e0'))


def draw(c, t):
    beat = T.beat_at(t)
    P = poses(t)
    hot = smoothstep(T_SIL - 0.08, T_SIL + 0.05, t) * (1 - smoothstep(T_CLOSE - 0.1, T_CLOSE, t))
    # ---------------- camera direction
    mx = P['michael']['x'] * BASE_H
    if t < T_SLIDE:
        cam = cam_path([(T0, Cam(0, -40, 0.72, -3), None), (T_SLIDE, Cam(0, -10, 0.92, 2), ease_io)], t)
    elif t < T_SIL:
        # tracking shot: follow Michael's slide, stage rotates under him
        u = (t - T_SLIDE) / (T_SIL - T_SLIDE)
        cam = Cam(mx * 0.85, 40, 1.35 + 0.1 * math.sin(u * math.pi), 4 * math.sin(u * 2 * math.pi))
    elif t < T_CLOSE:
        cam = cam_path([(T_SIL, Cam(0, -120, 0.78, 0), None), (T_CLOSE, Cam(0, -60, 0.86, -2), ease_io)], t)
    else:
        u = (t - T_CLOSE) / (T_END - T_CLOSE)
        cam = Cam(mx + 10, 90 + 20 * u, 2.6 + 1.0 * ease_io(u), -4 + 8 * ease_io(u))
    if abs(t - T_SIL) < 0.25:
        cam.shake = 0.7 * (1 - abs(t - T_SIL) / 0.25)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#100618'))
    with Layer(c, cam, 0.7, t):
        stage_set(c, t, beat, hot)
    with Layer(c, cam, 1.0, t):
        if hot > 0.5:
            # silhouette moment: band in black against the blazing orange sun-disc, gold halo
            silhouette(c, lambda: band(c, t, P, LIGHT), color=(0.07, 0.02, 0.06, 1.0), halo=(1.0, 0.85, 0.45, 0.9))
        else:
            floor_reflection(c, lambda: band(c, t, P, LIGHT), GY, 0.22)
            for i, x in enumerate((-500, -150, 150, 500)):
                beam(c, x * 2.2, -1700, x * 0.6, GY, 40, 200, PAL[(i + int(beat)) % 5], 0.33, blur=30)
            band(c, t, P, LIGHT)
        particles(c, t, 30, (-900, -1500, 900, 300), 41, '#ffe0f0', size=(1.5, 3), speed=(8, 20))
    if T0 <= t < T_SLIDE or T_SIL <= t < T_CLOSE:
        with Layer(c, cam, 1.6, t):
            tv_camera(c, 820, 480, 1.1)
    # flash-in from the explosion
    fl = 1 - smoothstep(T0, T0 + 0.35, t)
    if fl > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.97, 0.9, fl)))
