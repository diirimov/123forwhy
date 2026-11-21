"""V3 0:00-0:17  THE HOOK (child <-> future superstar match cut) and THE PRESSURE (reusing V2's best rehearsal shots)."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, glow, beam, clamp, ease_io, ease_out, ease_in,
                 smoothstep, noise1, poly_path)
from world import particles
from character import outfits, JOE_OUTFIT, DESIGNS, base_pose, outfits84
import choreo
import timing as T
import v2_home as V2
from v2_common import JOE, floor_shadow, L_NIGHT, L_WARM
from v3_common import cap, remap, pose, draw_char, place_head

DB = T.db
BEAT = T.PERIOD
O = outfits('home')
O84 = outfits84()
H_FACE, H_FEET, H_JOE, H_FLASH, H_BACK, H_RESUME = 0.0, 0.95, DB(0), DB(0) + 2 * BEAT, DB(0) + 3 * BEAT, DB(1)
P_POV, P_OVER, P_TIRED = DB(2), DB(2) + 2 * BEAT, DB(3)
HB = 2 * BEAT
P_CLOCK, P_WINDOW, P_CALL, P_WORK, END = DB(4), DB(4) + HB, DB(5), DB(5) + HB, DB(6)
EYE_Y = H * 0.44


def child_face(c, t, fear=0.8, look=0.85, scale=1.0):
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W * 0.85, H * 0.35), H, ['#5a3a2a', '#1e1418', '#0a080c'])))
    P = base_pose()
    choreo.freeze_fear(0, P, look=look)
    P['fear'] = fear
    P['ex'] = look + 0.06 * math.sin(t * 11)
    P['blink'] = 0.9 if 0.55 < (t % 2.1) < 0.62 else 0.0
    h = 4300 * scale
    gx, gy = place_head('michael', P, h, (W / 2, EYE_Y))
    c.save()
    c.translate(1.2 * noise1(t * 30, 4), 0)
    draw_char(c, 'michael', gx, gy, h, P, O['michael'], dict(L_NIGHT, rim='#ffd598', amb_a=0.3, key=(0.8, -0.5)), t, shadow=False)
    c.restore()
    # warm doorway light raking from the right + the edge of a long shadow
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((W, 0), (W * 0.35, 0), [(1, 0.7, 0.35, 0.25), (0, 0, 0, 0)]),
                                                     blend=skia.BlendMode.kPlus))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, EYE_Y), H * 0.62, [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0.7)],
                                                             [0, 0.5, 1])))


def star_face(c, t):
    """the flash-forward: the same boy, grown, under a stadium's worth of light - framed identically"""
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H * 0.3), H, ['#3a3070', '#120e30', '#05061a'])))
    rng = np.random.default_rng(11)
    for i in range(80):
        glow(c, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(25, 80), ['#ffffff', '#9fd8ff', '#ffd8a0'][i % 3], 0.3)
    for k in range(5):
        beam(c, W * (0.1 + 0.2 * k), -200, W / 2, H * 0.6, 40, 300, '#ffffff', 0.25, blur=40)
    P = base_pose(smile=0.9, mopen=0.4, mshape='grin', brow=0.4, ey=-0.3, blink=0.0)
    h = 4300 * 0.62
    gx, gy = place_head('michael84', P, h, (W / 2, EYE_Y))
    draw_char(c, 'michael84', gx, gy, h, P, O84['michael84'], dict(key=(0, -1), amb='#ffffff', amb_a=0.1, rim='#ffffff',
                                                                     line='#1a1020', floor_shadow=0), t, shadow=False)


def feet_stop(c, t):
    """his shoes stop - a long shadow slides across the floor over them"""
    u = clamp((t - H_FEET) / (H_JOE - H_FEET))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#1a1210', '#3a2416'])))
    for k in range(-12, 13):
        c.drawLine(W / 2 + k * 90, H * 0.3, W / 2 + k * 420, H + 200, paint((0.1, 0.05, 0.02, 0.5), style='stroke', width=5))
    c.drawOval(skia.Rect.MakeXYWH(W * 0.1, H * 0.66, W * 0.85, 300), paint((1, 0.75, 0.4, 0.3), blur=60, blend=skia.BlendMode.kPlus))
    sched = [(0, 'step_touch', dict(width=0.07)), (H_FEET + 0.38, 'freeze_fear', dict(look=0.9))]
    P = pose('michael', sched, t)
    draw_char(c, 'michael', W / 2, H * 0.74, 2300, P, O['michael'], L_WARM, t)
    # a long shadow slides in from the doorway (right) across the boards and swallows his shoes
    sweep = ease_out(clamp((u - 0.1) / 0.6), 2)
    if sweep > 0:
        edge = W * 1.15 - W * 1.0 * sweep
        wedge = poly_path([(edge, H * 0.55), (W + 400, H * 0.5), (W + 400, H + 50), (edge - 260, H + 50)])
        c.drawPath(wedge, paint((0.02, 0.01, 0.03, 0.72), blur=24))
        hat = poly_path([(edge - 40, H * 0.58), (edge + 120, H * 0.56), (edge + 140, H * 0.6), (edge - 60, H * 0.62)])
        c.drawPath(hat, paint((0.02, 0.01, 0.03, 0.72), blur=14))


def joe_continue(c, t):
    V2.shot_joe_door(c, t, H_JOE, H_FLASH, sched=[(0, 'beckon', dict(side=-1))], push=(1.12, 1.22))


def joe_call_back(c, t):
    V2.shot_joe_door(c, t, P_CALL, P_WORK, sched=[(0, 'joe_point', dict(start='auto', side=-1))], push=(1.0, 1.1))


def resume(c, t):
    """he starts dancing again - stiff, careful - with his father's shadow on the wall behind the brothers"""
    from world import Cam, Layer
    from v2_common import room_wall, room_floor, lamp, draw_cast, wall_shadow, GY
    u = clamp((t - H_RESUME) / (P_POV - H_RESUME))
    cam = Cam(-20, 290, 1.9 - 0.35 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0a10'))
    with Layer(c, cam, 0.65, t):
        room_wall(c, t, door=1.0, night=1.0)
        def jf():
            JOE.draw(c, 120, GY + 230, 560 * DESIGNS['joe'].height * 1.45, base_pose(lsh=0.32, lel=-2.45, rsh=0.32, rel=-2.45),
                     JOE_OUTFIT, L_NIGHT, t, shadow=False)
        wall_shadow(c, jf, a=0.55, blur=10)
    with Layer(c, cam, 1.0, t):
        room_floor(c, 1.0)
        tense = lambda tt: dict(brow=0.75, fear=0.35, smile=0.0, ex=0.4)
        mem = V2.brothers(lambda k: [(0, 'play', dict(amp=0.8))] if k in V2.INSTR else [(0, 'step_touch', dict(amp=0.8))])
        for m in mem:
            m['over'] = tense
        draw_cast(c, t, mem, L_NIGHT, 'home')
    with Layer(c, cam, 1.4, t):
        lamp(c, -900, on=0.55)


SHOTS = [
    (H_FACE, lambda c, t: child_face(c, t, fear=0.6 + 0.4 * smoothstep(0.3, 0.9, t), look=0.85)),
    (H_FEET, feet_stop),
    (H_JOE, joe_continue),
    (H_FLASH, star_face),
    (H_BACK, lambda c, t: child_face(c, t, fear=1.0, look=0.5)),
    (H_RESUME, resume),
    (P_POV, remap(V2.shot_joe_room, V2.B_CLAP, P_POV)),            # Joe corrects them: clap, point to their marks
    (P_OVER, remap(V2.shot_overshoulder, P_OVER, P_OVER)),
    (P_TIRED, remap(V2.shot_tired, P_TIRED, P_TIRED)),
    (P_CLOCK, remap(V2.m_clock, V2.C_SHOTS[1], P_CLOCK)),
    (P_WINDOW, remap(V2.m_window, V2.C_SHOTS[3], P_WINDOW)),
    (P_CALL, joe_call_back),
    (P_WORK, remap(V2.m_back_to_work, V2.C_SHOTS[5], P_WORK)),
]


def _resume_override(fn):
    return fn


def draw(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)
    # the flash-forward: white bloom in and out of the future
    for tc, d in ((H_FLASH, 0.12), (H_BACK, 0.1)):
        k = 1 - abs(t - tc) / d
        if k > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.97, 0.92, 0.85 * k)))
    cap(c, t, H_JOE + 0.06, H_BACK - 0.05, ['HE MADE THEM STARS…'], y=300, size=88)
    cap(c, t, H_BACK + 0.2, P_POV - 0.1, ['BUT AT WHAT COST?'], y=1430, size=96)
    cap(c, t, P_POV + 0.25, P_CLOCK - 0.1, ['THEIR CHILDHOOD WAS', 'FILLED WITH REHEARSALS.'], y=300, size=82)
    cap(c, t, P_CLOCK + 0.2, END - 0.1, ['AND THEIR FATHER', 'DEMANDED PERFECTION.'], y=300, size=82)
