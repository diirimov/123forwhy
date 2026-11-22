"""EVOLUTION edit: shared transformations (spin morphs), side-view moonwalk rig, stadium, fog/moon, flashes."""
import math
import numpy as np
import skia
import _paths  # noqa: F401
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, clamp, smoothstep, ease_io,
                 ease_out, ease_in, back_out, font, text_center, noise1, poly_path, smooth_path, limb_outline, ellipse_path, cel)
import timing as T
from character import base_pose, blend, DESIGNS
from world import CHARS, Cam, Layer, crowd, particles, silhouette, floor_reflection
import choreo
import ev_cast as E
from bi_common import cap, stamp, bg, u_of, pose, draw, place_head, skel, IVORY, GOLD

DB = T.db
BEAT = T.PERIOD
HALF = 2 * BEAT


def B_of(t):
    return T.beat_at(t) - T.PHASE


def spin_morph(t, t0, dur, stages, turns=2):
    """a spin that hides costume/age changes: returns (spin value 0..turns, stage index).
    the stage advances at each edge-on moment (spin fraction .25 / .75) - never a face mid-morph"""
    u = clamp((t - t0) / dur)
    s = ease_io(u) * turns
    edges = int(math.floor(s * 2 + 0.5))          # edge-on moments passed
    idx = min(len(stages) - 1, max(0, edges))
    return s, stages[idx]


def flash_burst(c, t, times, n=26, seed=0, area=(0, H * 0.45, W, H), life=0.35):
    """photographer flashes popping across the audience on given accents"""
    for j, tc in enumerate(times):
        k = t - tc
        if 0 <= k < life:
            rng = np.random.default_rng(seed + j)
            for i in range(n):
                d = rng.uniform(0, life * 0.5)
                kk = k - d
                if 0 <= kk < 0.12:
                    a = 1 - kk / 0.12
                    x, y = rng.uniform(area[0], area[2]), rng.uniform(area[1], area[3])
                    glow(c, x, y, rng.uniform(40, 110), '#ffffff', 0.9 * a)
                    c.drawCircle(x, y, 6, paint((1, 1, 1, a)))
            if k < 0.06:
                c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 1, 1, 0.35 * (1 - k / 0.06)), blend=skia.BlendMode.kPlus))


def moon(c, x, y, r, red=0.0):
    col = mix('#f4f0dc', '#ff3a2a', red)
    glow(c, x, y, r * 3.2, col, 0.45)
    c.drawCircle(x, y, r, shader_paint(rad_grad((x - r * 0.3, y - r * 0.3), r * 1.3, [mix(col, '#ffffff', 0.3), col, shade(col, -0.15)])))
    rng = np.random.default_rng(2)
    for k in range(7):
        a, rr = rng.uniform(0, 6.28), rng.uniform(0.1, 0.7) * r
        c.drawCircle(x + math.cos(a) * rr, y + math.sin(a) * rr, r * rng.uniform(0.06, 0.16), paint(alpha(shade(col, -0.2), 0.5)))


def fog(c, t, y0, y1, a=0.35, col=(0.75, 0.85, 0.8)):
    for k in range(6):
        y = y0 + (y1 - y0) * k / 5
        x = -400 + 300 * math.sin(t * 0.35 + k * 1.7)
        c.drawOval(skia.Rect.MakeXYWH(x, y - 110, W + 800, 220), paint((*col, a * (0.6 + 0.4 * math.sin(k))), blur=50))


def stadium(c, t, cam_z=1.0, cam_y=0.0, energy=1.0, tint='#a8b8ff', seed=1, gold=0.0, beams=True, rows=14):
    """huge open-air stadium at night: tiers ringed with lights, light towers, beams, a sea of fans (world: stage at y=0)"""
    beat = T.beat_at(t)
    c.drawRect(skia.Rect.MakeLTRB(-6000, -6000, 6000, 6000), shader_paint(lin_grad((0, -2600), (0, 0), ['#02020c', '#0a0a2a', mix('#1a1450', '#3a2a10', gold)])))
    rng = np.random.default_rng(seed)
    for tier in range(4):                     # bowl tiers with thousands of phone-less 80s/90s lights (lighters / flashes)
        y = -700 - tier * 260
        w = 2600 + tier * 900
        c.drawPath(poly_path([(-w, y), (w, y), (w * 1.05, y - 230), (-w * 1.05, y - 230)]), paint(mix('#0c0c22', '#000000', tier * 0.15)))
        for i in range(int(260 + tier * 120)):
            x = rng.uniform(-w, w)
            yy = y - rng.uniform(10, 220)
            tw = 0.5 + 0.5 * math.sin(t * rng.uniform(2, 6) + i)
            c.drawCircle(x, yy, 3 + 2 * tw, paint(alpha(['#ffd88a', '#ffffff', tint][i % 3], 0.35 + 0.5 * tw)))
    for sd in (-1, 1):                        # light towers
        for k in range(2):
            x = sd * (1500 + k * 900)
            c.drawLine(x, -500, x, -2400, paint('#14141c', style='stroke', width=40))
            for j in range(4):
                glow(c, x - 120 + j * 80, -2400, 60, '#ffffff', 0.9)
    if beams:
        for i in range(12):
            x = (i - 5.5) * 260
            sw = 500 * math.sin(t * 0.8 + i)
            beam(c, x, -360, x * 1.8 + sw, -3200, 24, 460, [mix('#ffffff', '#ffd060', gold), '#9fd8ff', '#ff9ad8'][i % 3], 0.17, blur=40)
    # stage
    c.drawRect(skia.Rect.MakeLTRB(-1100, -420, 1100, -360), paint('#1a1a24'))
    for k in range(-10, 11):
        glow(c, k * 105, -390, 24, ['#ffffff', '#ffd8a0', '#9fd8ff'][k % 3], 0.7)
    c.drawPath(poly_path([(-1200, 0), (1200, 0), (1350, 120), (-1350, 120)]), paint('#121220'))
    c.drawRect(skia.Rect.MakeLTRB(-1300, -30, 1300, 10), shader_paint(lin_grad((0, -30), (0, 10), ['#3a3a5a', '#141420'])))
    c.save()
    c.translate(0, 260)
    crowd(c, t, rows, energy, '#05051a', tint, width=7000, seed=seed * 10, y0=0, row_gap=110, scale0=0.55, beat_phase=beat, lighters=True)
    c.restore()


def sunglasses(c, S):
    hx, hy = S['head']
    r = S['hr']
    for sd in (-1, 1):
        rr = skia.Rect.MakeXYWH(hx + sd * r * 0.36 - r * 0.3, hy - r * 0.15, r * 0.6, r * 0.38)
        c.drawRoundRect(rr, r * 0.15, r * 0.15, shader_paint(lin_grad((0, rr.top()), (0, rr.bottom()), ['#3a3a44', '#0a0a10'])))
        c.drawLine(rr.left() + r * 0.08, rr.top() + r * 0.08, rr.left() + r * 0.25, rr.top() + r * 0.05, paint((1, 1, 1, 0.6), style='stroke', width=r * 0.04))
    c.drawLine(hx - r * 0.06, hy - r * 0.08, hx + r * 0.06, hy - r * 0.08, paint('#0a0a10', style='stroke', width=r * 0.05))


# ----------------------------------------------------------------------------- side-view moonwalk rig
def ik_side(hip, foot, L1, L2, knee_dir):
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    d = min(math.hypot(dx, dy), L1 + L2 - 1e-3)
    a = math.atan2(dy, dx)
    cb = clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1)
    b = math.acos(cb)
    ang = a - knee_dir * b
    return (hip[0] + math.cos(ang) * L1, hip[1] + math.sin(ang) * L1)


def loafer(c, heel, toe_pitch, s, dirn, sock='#f4f4f8', shoe='#0c0c10', sparkle=True, t=0.0):
    """profile loafer: heel point, pitch (radians, + = heel raised, rotating about the toe ball)"""
    L = 150 * s
    fwd = -dirn                       # toes point opposite to the direction of travel (he moves backward)
    c.save()
    ball = (heel[0] + fwd * L * 0.72 * math.cos(toe_pitch), heel[1] + L * 0.72 * math.sin(toe_pitch))
    c.translate(*ball)
    c.rotate(math.degrees(fwd * toe_pitch))
    c.scale(fwd, 1)
    p = smooth_path([(-L * 0.72, -46 * s), (-L * 0.2, -52 * s), (L * 0.22, -30 * s), (L * 0.35, -6 * s), (L * 0.3, 4 * s),
                     (-L * 0.76, 4 * s), (-L * 0.8, -20 * s)], True, 0.45)
    c.drawPath(p, shader_paint(lin_grad((0, -50 * s), (0, 4 * s), ['#3a3a44', shoe])))
    c.drawPath(p, paint('#000000', style='stroke', width=3))
    c.drawLine(-L * 0.6, -38 * s, L * 0.1, -36 * s, paint((1, 1, 1, 0.35), style='stroke', width=4 * s))
    c.restore()


def moonwalk_legs(c, t, cx, floor_y, s, start_beat, dirn=-1, pants='#121016', sock='#f4f4f8', stride=0.32, sparkle=True):
    """profile legs doing the moonwalk with real contact: the toe foot stays planted on its ball, the flat foot glides
    back past it, heel-drop swaps the weight every beat; hips travel backward at constant speed."""
    B = B_of(t)
    u = max(0.0, B - start_beat)
    k = int(math.floor(u))
    f = u - k
    S_ = stride * 1000 * s
    T_k = dirn * S_ * k
    glide = clamp((f - 0.08) / 0.84)
    flat = T_k - dirn * S_ + 2 * dirn * S_ * glide
    body = T_k + dirn * S_ * (f - 0.5)
    heel = 1 - clamp(f / 0.14)                 # heel-drop of the old toe foot / rise of the new toe foot
    toe_pitch_toe = 0.55 * (1 - heel) + 0.0 * heel
    toe_pitch_flat = 0.55 * heel
    feet = {k % 2: (T_k, toe_pitch_toe), 1 - k % 2: (flat, toe_pitch_flat)}
    hipx = cx + body
    hip_y = floor_y - 955 * s + 18 * s * heel - 8 * s * math.sin(math.pi * f)
    L1, L2 = 450 * s, 445 * s
    out = []
    for leg in (0, 1):
        fx, pitch = feet[leg]
        heel_pt = (cx + fx, floor_y - 20 * s - 150 * s * 0.72 * math.sin(pitch))
        ankle = (heel_pt[0] + dirn * -10 * s, heel_pt[1] - 60 * s)
        knee = ik_side((hipx, hip_y), ankle, L1, L2, -dirn)
        out.append((leg, heel_pt, ankle, knee, pitch))
    for leg, heel_pt, ankle, knee, pitch in sorted(out, key=lambda q: q[0]):
        shade_k = 0.75 if leg == 0 else 1.0
        sock_top = (ankle[0] + (knee[0] - ankle[0]) * 0.22, ankle[1] + (knee[1] - ankle[1]) * 0.22)
        c.drawPath(limb_outline([ankle, sock_top], [64 * s, 70 * s], True, False), paint(mix(sock, '#000000', 1 - shade_k)))
        if sparkle:
            rng = np.random.default_rng(leg)
            for q in range(10):
                v = rng.uniform(0, 1)
                px = ankle[0] + (sock_top[0] - ankle[0]) * v + rng.uniform(-24, 24) * s
                py = ankle[1] + (sock_top[1] - ankle[1]) * v
                tw = 0.5 + 0.5 * math.sin(t * 9 + q * 1.7 + leg)
                c.drawCircle(px, py, (3 + 3 * tw) * s, paint((1, 1, 1, 0.9 * tw)))
        loafer(c, heel_pt, pitch, s, dirn)
        pc = mix(pants, '#000000', 1 - shade_k)
        c.drawPath(limb_outline([(hipx, hip_y), knee, sock_top], [150 * s, 110 * s, 96 * s]), shader_paint(
            lin_grad((hipx - 80 * s, 0), (hipx + 80 * s, 0), [mix(pc, '#5a5a70', 0.25), pc, mix(pc, '#000000', 0.3)])))
        c.drawPath(limb_outline([(hipx, hip_y), knee, sock_top], [150 * s, 110 * s, 96 * s]), paint('#000000', style='stroke', width=3))
    # contact shadows: hard under the planted toe, soft under the gliding foot
    for leg, heel_pt, ankle, knee, pitch in out:
        x0 = heel_pt[0] - dirn * 60 * s
        c.drawOval(skia.Rect.MakeXYWH(x0 - 110 * s, floor_y - 12 * s, 220 * s, 24 * s), paint((0, 0, 0, 0.55 if pitch > 0.3 else 0.35), blur=8))
    # hem of the sequined jacket over the hips (the shot is framed on the legs)
    c.drawPath(smooth_path([(hipx - 120 * s, hip_y + 40 * s), (hipx + 130 * s, hip_y + 40 * s), (hipx + 150 * s, hip_y - 900 * s),
                            (hipx - 150 * s, hip_y - 900 * s)], True, 0.2), shader_paint(lin_grad((hipx - 150 * s, 0), (hipx + 150 * s, 0),
                                                                                                    ['#2a2a36', '#121016', '#060608'])))
    rng = np.random.default_rng(11)
    for q in range(30):
        tw = 0.5 + 0.5 * math.sin(t * 8 + q * 1.3)
        c.drawCircle(hipx + rng.uniform(-130, 130) * s, hip_y + rng.uniform(-880, 20) * s, (3 + 3 * tw) * s, paint((1, 0.95, 0.8, 0.8 * tw)))
    return hipx, hip_y


def stomp_legs(c, t, cx, floor_y, s, pants='#5a4a3a', shoe='#2a1a12', sock='#e8e0d0', facing=1, phase=0.0, flare=True):
    """profile legs drilling a step: feet alternate, each strikes the floor exactly on a beat (heel-toe contact)"""
    B = B_of(t) + phase
    out = []
    hip = (cx, floor_y - 900 * s)
    for leg in (0, 1):
        k = (B + leg) % 2                     # each foot: lifted during its off-beat, plants on the beat
        lift = math.sin(math.pi * clamp((k - 1.0) / 0.85)) if k >= 1.0 else 0.0
        fx = cx + facing * (-60 + 120 * leg) * s + facing * 40 * s * lift
        heel = (fx, floor_y - 18 * s - 170 * s * lift)
        pitch = 0.25 * lift
        ankle = (heel[0] + facing * 30 * s, heel[1] - 70 * s)
        hy = hip[1] + 12 * s * math.sin(math.pi * 2 * (B % 1))
        knee = ik_side((hip[0], hy), ankle, 430 * s, 420 * s, facing)
        out.append((leg, heel, ankle, knee, pitch, hy))
    for leg, heel, ankle, knee, pitch, hy in out:
        sh = 0.5 if leg == 0 else 1.0
        loafer(c, heel, pitch, s * 1.45, -facing, shoe=mix(shoe, '#000000', 1 - sh))
        pc = mix(pants, '#000000', 1 - sh)
        w_end = 150 * s if flare else 96 * s
        c.drawPath(limb_outline([(hip[0], hy), knee, (ankle[0], ankle[1] + 20 * s)], [150 * s, 110 * s, w_end]),
                   shader_paint(lin_grad((hip[0] - 80 * s, 0), (hip[0] + 80 * s, 0), [mix(pc, '#ffffff', 0.15), pc, mix(pc, '#000000', 0.3)])))
        c.drawPath(limb_outline([(hip[0], hy), knee, (ankle[0], ankle[1] + 20 * s)], [150 * s, 110 * s, w_end]),
                   paint('#120a06', style='stroke', width=5))
        if pitch < 0.02:
            c.drawOval(skia.Rect.MakeXYWH(heel[0] - 120 * s, floor_y - 12 * s, 240 * s, 24 * s), paint((0, 0, 0, 0.55), blur=8))
    return out
