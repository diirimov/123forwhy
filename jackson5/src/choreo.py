"""
Beat-locked choreography.  A move is f(B, P, **kw) where B = beat position relative to bar start
(B % 4 = beat-in-bar, integers fall exactly on the tracked beats).  Moves write into a pose dict.
perform() evaluates a timeline of moves for one character with crossfades, follow-through,
automatic blinks and audio-driven lip movement.
"""
import math
from gfx import clamp, ease_io, ease_out, back_out, noise1
from character import base_pose, blend
import timing as T

PI = math.pi


def dipcurve(f):
    """groove bounce: lowest just after the beat"""
    return 0.5 + 0.5 * math.cos(2 * PI * (f - 0.1))


def sway(B):
    """-1/+1 alternating each beat, smooth"""
    return math.sin(PI * (B - 0.5)) * -1


# ----------------------------------------------------------------------------- moves
def groove(B, P, amp=1.0, snap=True, arms=True):
    f = B % 1
    k = int(math.floor(B)) % 4
    s = math.cos(PI * B)              # +1 on even beats, -1 on odd
    P['dip'] = 0.02 * amp * dipcurve(f)
    P['hip'] = 0.014 * s * amp
    P['lean'] = -0.035 * s * amp
    P['htilt'] = 0.05 * math.cos(PI * (B - 0.15)) * amp
    P['hnod'] = 0.006 * dipcurve(f - 0.08) * amp
    P['lfy'] = -0.012 * max(0, -s) * amp
    P['rfy'] = -0.012 * max(0, s) * amp
    if arms:
        sn = math.exp(-((f if f < 0.5 else f - 1) / 0.16) ** 2) if (snap and k in (1, 3)) else 0.0
        P['lsh'] = 0.42 + 0.1 * s + 0.25 * sn
        P['lel'] = 1.25 + 0.25 * s + 0.4 * sn
        P['rsh'] = 0.42 - 0.1 * s + 0.25 * sn
        P['rel'] = 1.25 - 0.25 * s + 0.4 * sn
        hs = 'snap' if sn > 0.3 else 'relaxed'
        P['lhand'] = P['rhand'] = hs


def step_touch(B, P, amp=1.0, clap=True, width=0.055):
    f = B % 1
    n = int(math.floor(B))
    d = 1 if n % 2 == 0 else -1                       # direction of travel during this beat
    X0, X1 = -d * width * amp, d * width * amp
    body = X0 + (X1 - X0) * ease_io(f / 0.8)
    lead = X0 + (X1 - X0) * ease_out(f / 0.5, 2.5)
    trail = X0 + (X1 - X0) * ease_io((f - 0.3) / 0.55)
    lift_l = -0.035 * math.sin(PI * clamp(f / 0.5))
    lift_t = -0.03 * math.sin(PI * clamp((f - 0.3) / 0.55))
    P['x'] = body
    if d > 0:
        P['rfx'], P['rfy'] = 0.08 + lead - body, lift_l
        P['lfx'], P['lfy'] = -0.08 + trail - body + 0.05 * clamp((f - 0.3) / 0.55), lift_t
    else:
        P['lfx'], P['lfy'] = -0.08 + lead - body, lift_l
        P['rfx'], P['rfy'] = 0.08 + trail - body - 0.05 * clamp((f - 0.3) / 0.55), lift_t
    P['dip'] = 0.025 * amp * dipcurve(f - 0.35)
    P['lean'] = 0.07 * d * (1 - ease_io(f)) * amp
    P['hip'] = -0.015 * d
    P['htilt'] = -0.06 * d * (1 - f)
    k = n % 4
    if clap:
        c = 0.0
        if k in (1, 3):
            c = math.exp(-(f / 0.2) ** 2)
        if k in (0, 2):
            c = math.exp(-((1 - f) / 0.2) ** 2)
        P['lsh'] = 0.55 - 0.3 * c
        P['lel'] = 0.9 - 2.75 * c
        P['rsh'] = 0.55 - 0.3 * c
        P['rel'] = 0.9 - 2.75 * c
        P['lhand'] = P['rhand'] = 'open'
    else:
        P['lsh'] = 0.5 + 0.3 * d
        P['rsh'] = 0.5 - 0.3 * d
        P['lel'] = P['rel'] = 1.0


def point_hit(B, P, amp=1.0, side=1, start=0.0):
    """anticipation (dip + wind-up) then snap to a diagonal point, held"""
    u = B - start
    ant = clamp(1 - abs(u + 0.25) / 0.25)            # wind-up 1/4 beat before the hit
    hit = back_out(clamp(u / 0.3), 2.2)
    P['dip'] = 0.03 * ant + 0.012 * (1 - hit)
    hi, lo = ('rsh', 'rel') if side > 0 else ('lsh', 'lel')
    oh, ol = ('lsh', 'lel') if side > 0 else ('rsh', 'rel')
    P[hi] = 0.4 * (1 - hit) + 2.35 * hit - 0.3 * ant
    P[lo] = 0.8 * (1 - hit) + 0.08 * hit
    P[oh] = 0.85
    P[ol] = -1.75 * hit + 0.4 * (1 - hit)
    P['rhand' if side > 0 else 'lhand'] = 'point' if hit > 0.4 else 'fist'
    P['lhand' if side > 0 else 'rhand'] = 'fist'
    P['lean'] = 0.09 * side * hit
    P['htilt'] = 0.12 * side * hit
    P['ey'] = -0.5 * hit
    P['ex'] = 0.5 * side * hit
    P['lfx'], P['rfx'] = -0.1, 0.1
    P['smile'] = 1.0
    P['mopen'] = 0.35 * hit
    P['mshape'] = 'grin'


def spin(B, P, start=0.0, length=1.0):
    u = clamp((B - start) / length)
    P['spin'] = ease_io(u)
    P['lsh'] = P['rsh'] = 0.3
    P['lel'] = P['rel'] = -1.4
    P['lhand'] = P['rhand'] = 'fist'
    P['dip'] = 0.02 * math.sin(PI * u)
    P['lfx'], P['rfx'] = -0.04, 0.04


def arm_roll(B, P, amp=1.0):
    groove(B, P, amp, snap=False, arms=False)
    th = 2 * PI * B
    P['lsh'] = 0.3 + 0.12 * math.cos(th)
    P['lel'] = -1.55 + 0.35 * math.sin(th)
    P['rsh'] = 0.3 + 0.12 * math.cos(th + PI)
    P['rel'] = -1.55 + 0.35 * math.sin(th + PI)
    P['lhand'] = P['rhand'] = 'fist'


def shimmy(B, P, amp=1.0):
    f = B % 1
    P['lean'] = -0.06
    P['tw'] = 0.55 * math.sin(4 * PI * B) * amp
    P['dip'] = 0.03 + 0.012 * dipcurve(f)
    P['lsh'] = P['rsh'] = 1.15
    P['lel'] = P['rel'] = 0.55 + 0.2 * math.sin(4 * PI * B)
    P['lhand'] = P['rhand'] = 'open'
    P['lfx'], P['rfx'] = -0.11, 0.11
    P['htilt'] = -0.06
    P['smile'] = 1.0
    P['mopen'] = 0.5
    P['mshape'] = 'grin'
    P['ey'] = -0.3


def slide(B, P, start=0.0, dirn=1, dist=0.5, beats=4.0):
    """glide across the floor: body travels, feet alternate flat/toe (moonwalk-flavoured), lean against travel"""
    u = clamp((B - start) / beats)
    P['x'] = dirn * dist * ease_io(u)
    f = B % 1
    a = math.sin(PI * B)
    P['lfx'] = -0.06 + 0.05 * a * dirn
    P['rfx'] = 0.06 - 0.05 * a * dirn
    P['lfy'] = -0.03 * max(0, a)
    P['rfy'] = -0.03 * max(0, -a)
    P['dip'] = 0.035 + 0.01 * dipcurve(f)
    P['lean'] = -0.1 * dirn
    P['htilt'] = 0.08 * dirn
    P['hyaw'] = 0.4 * dirn
    P['tw'] = 0.4 * dirn
    lead_sh, lead_el = ('rsh', 'rel') if dirn > 0 else ('lsh', 'lel')
    tr_sh, tr_el = ('lsh', 'lel') if dirn > 0 else ('rsh', 'rel')
    P[lead_sh], P[lead_el] = 1.5 + 0.1 * a, 0.3
    P[tr_sh], P[tr_el] = 0.5, 1.6 + 0.2 * a
    P['lhand'] = P['rhand'] = 'open'
    P['smile'] = 0.9


def kick(B, P, side=1):
    f = B % 1
    groove(B, P, 1.0, snap=False)
    k = math.exp(-((f - 0.5) / 0.14) ** 2)
    if side > 0:
        P['rfx'] = 0.08 + 0.16 * k
        P['rfy'] = -0.16 * k
    else:
        P['lfx'] = -0.08 - 0.16 * k
        P['lfy'] = -0.16 * k
    P['lean'] = -0.08 * side * k
    P['lsh'] = P['rsh'] = 0.5 + 0.6 * k
    P['lel'] = P['rel'] = 0.9


def knee_drop(B, P, start=0.0):
    u = back_out(clamp((B - start) / 0.5), 1.4)
    P['dip'] = 0.16 * u
    P['lfx'], P['rfx'] = -0.12 - 0.04 * u, 0.12 + 0.05 * u
    P['rfy'] = 0.0
    P['lsh'] = P['rsh'] = 0.4 + 1.9 * u
    P['lel'] = P['rel'] = 0.25
    P['lhand'] = P['rhand'] = 'open'
    P['lean'] = -0.05 * u
    P['htilt'] = -0.15 * u
    P['ey'] = -0.7 * u
    P['smile'] = 0.9
    P['mopen'] = 0.8 * u
    P['mshape'] = 'ah'
    P['brow'] = 0.7 * u


def play(B, P, amp=1.0):
    """instrument player: groove + strum on 8ths with accented downstrokes"""
    groove(B, P, 0.7 * amp, snap=False, arms=False)
    f = (B * 2) % 1
    P['strum'] = -1 + 2 * ease_out(f / 0.35, 3) if f < 0.35 else 1 - 2 * ease_io((f - 0.35) / 0.65)
    P['strum'] *= 0.6 * amp
    P['lfx'], P['rfx'] = -0.1, 0.1


def mic_sing(B, P, side=1, amp=1.0):
    groove(B, P, 0.8 * amp, snap=False, arms=False)
    hs, he = ('rsh', 'rel') if side > 0 else ('lsh', 'lel')
    os_, oe = ('lsh', 'lel') if side > 0 else ('rsh', 'rel')
    P[hs], P[he] = 0.12, -2.55
    th = PI * B / 2
    P[os_] = 0.9 + 0.5 * math.sin(th) * amp
    P[oe] = 0.6 + 0.4 * math.cos(th)
    P['rhand' if side > 0 else 'lhand'] = 'mic'
    P['lhand' if side > 0 else 'rhand'] = 'open'
    P['mic'] = side
    P['htilt'] = -0.05


def shy(B, P):
    """uncertain: small sway, glances sideways, hands clasped"""
    groove(B, P, 0.35, snap=False, arms=False)
    P['lsh'] = P['rsh'] = 0.18
    P['lel'] = P['rel'] = -1.25
    P['lhand'] = P['rhand'] = 'relaxed'
    P['ex'] = 0.6 * math.sin(B * 0.6)
    P['brow'] = 0.5
    P['smile'] = 0.3
    P['hyaw'] = 0.25 * math.sin(B * 0.6)


def cheer(B, P, amp=1.0):
    f = B % 1
    P['dip'] = 0.03 * dipcurve(f) * amp
    P['lsh'] = P['rsh'] = 2.5 + 0.15 * math.sin(PI * B)
    P['lel'] = P['rel'] = 0.2
    P['lhand'] = P['rhand'] = 'open'
    P['smile'] = 1.0
    P['mopen'] = 0.6
    P['mshape'] = 'ah'
    P['ey'] = -0.4


def pose_hold(B, P, kind='final'):
    P['lsh'], P['lel'] = 2.2, 0.15
    P['rsh'], P['rel'] = 0.7, -1.6
    P['lhand'], P['rhand'] = 'open', 'fist'
    P['lfx'], P['rfx'] = -0.12, 0.1
    P['lean'] = -0.04
    P['htilt'] = -0.1
    P['ey'] = -0.4
    P['smile'] = 1.0
    P['mshape'] = 'grin'
    P['mopen'] = 0.25


def stumble(B, P, start=0.0):
    """misses a step: foot slides out, arms flail, catches balance"""
    u = B - start
    k = clamp(u / 0.35)
    rec = clamp((u - 0.45) / 0.6)
    slip = math.sin(PI * k) * (1 - rec)
    P['rfx'] = 0.08 + 0.2 * k * (1 - 0.6 * rec)
    P['rfy'] = -0.05 * math.sin(PI * k)
    P['lfx'] = -0.07
    P['lean'] = -0.26 * slip + 0.04 * rec
    P['dip'] = 0.11 * k * (1 - 0.5 * rec)
    P['lsh'], P['lel'] = 0.4 + 1.6 * slip, 0.5 + 0.6 * slip
    P['rsh'], P['rel'] = 0.4 + 1.2 * slip, 0.9
    P['lhand'] = P['rhand'] = 'open'
    P['brow'] = 0.9
    P['fear'] = 0.6 * k
    P['smile'] = 0.0
    P['mopen'] = 0.35 * slip
    P['mshape'] = 'o'
    P['htilt'] = 0.12 * slip


def freeze_fear(B, P, look=0.8):
    """frozen, shoulders up, eyes on the doorway; a small tremble"""
    tr = 0.004 * math.sin(B * 40)
    P['lsh'], P['lel'] = 0.08, -0.35
    P['rsh'], P['rel'] = 0.08, -0.35
    P['lhand'] = P['rhand'] = 'relaxed'
    P['lean'] = -0.035 + tr
    P['dip'] = 0.006
    P['lfx'], P['rfx'] = -0.06, 0.06
    P['fear'] = 1.0
    P['brow'] = 1.0
    P['smile'] = -0.1
    P['mopen'] = 0.12
    P['mshape'] = 'o'
    P['ex'] = look
    P['ey'] = -0.15
    P['hyaw'] = 0.25 * look
    P['blink'] = 0.0


def walk(B, P, start=0.0, dirn=1, speed=0.16):
    u = B - start
    ph = PI * u
    P['x'] = dirn * speed * u
    s = math.sin(ph)
    P['lfx'] = -0.05 + 0.06 * s * dirn
    P['rfx'] = 0.05 - 0.06 * s * dirn
    P['lfy'] = -0.035 * max(0, math.cos(ph))
    P['rfy'] = -0.035 * max(0, -math.cos(ph))
    P['dip'] = 0.012 * abs(math.cos(ph))
    P['lsh'], P['lel'] = 0.12 + 0.08 * s, 0.25 + 0.35 * max(0, s)
    P['rsh'], P['rel'] = 0.12 - 0.08 * s, 0.25 + 0.35 * max(0, -s)
    P['hyaw'] = 0.3 * dirn
    P['tw'] = 0.3 * dirn
    P['hip'] = 0.008 * s


def tired(B, P, depth=1.0):
    """exhausted: hands on knees, heavy breathing, sweat"""
    br = 0.5 + 0.5 * math.sin(B * PI * 0.9)
    P['dip'] = 0.07 * depth
    P['lean'] = 0.0
    P['hnod'] = 0.03 * depth + 0.006 * br
    P['lsh'], P['lel'] = 0.32, -0.55
    P['rsh'], P['rel'] = 0.32, -0.55
    P['lfx'], P['rfx'] = -0.1, 0.1
    P['lhand'] = P['rhand'] = 'open'
    P['brow'] = 0.55
    P['smile'] = 0.0
    P['mopen'] = 0.35 + 0.3 * br
    P['mshape'] = 'o'
    P['blink'] = 0.35
    P['sweat'] = 1.0
    P['ey'] = 0.3


def arms_folded(B, P, stern=1.0, look=0.0):
    br = math.sin(B * PI * 0.5)
    P['lsh'], P['lel'] = 0.32, -2.45
    P['rsh'], P['rel'] = 0.32, -2.45
    P['lhand'] = P['rhand'] = 'fist'
    P['lfx'], P['rfx'] = -0.07, 0.07
    P['dip'] = 0.003 * br
    P['brow'] = -0.9 * stern
    P['smile'] = -0.45 * stern
    P['blink'] = 0.28 * stern
    P['ex'] = look


def joe_point(B, P, start=0.0, side=-1):
    u = clamp((B - start) / 0.25)
    hit = back_out(u, 2.0)
    hs, he = ('lsh', 'lel') if side < 0 else ('rsh', 'rel')
    os_, oe = ('rsh', 'rel') if side < 0 else ('lsh', 'lel')
    P[hs], P[he] = 0.3 + 1.32 * hit, 0.05 + 0.6 * (1 - hit)
    P[os_], P[oe] = 0.35, -1.9
    P['lhand' if side < 0 else 'rhand'] = 'point'
    P['rhand' if side < 0 else 'lhand'] = 'fist'
    P['lean'] = 0.05 * side * hit
    P['brow'] = -1.0
    P['smile'] = -0.5
    P['blink'] = 0.2
    P['ex'] = 0.6 * side
    P['hyaw'] = 0.25 * side


def joe_clap(B, P, start=0.0):
    u = B - start
    c_ = math.exp(-(u / 0.12) ** 2) if u > -0.3 else 0.0
    open_ = clamp(-u / 0.3) if u < 0 else 0.0
    P['lsh'] = P['rsh'] = 0.5 + 0.3 * open_ - 0.25 * c_
    P['lel'] = P['rel'] = -1.2 - 1.3 * c_ + 0.8 * open_
    P['lhand'] = P['rhand'] = 'open'
    P['brow'] = -1.0
    P['smile'] = -0.5
    P['mopen'] = 0.4 * c_
    P['mshape'] = 'ah'
    P['dip'] = 0.01 * c_


def determined(B, P, start=0.0):
    """wipes his brow, sets his jaw, fists ready"""
    u = B - start
    w = clamp(u / 0.6)
    wipe = math.sin(PI * w)
    P['rsh'], P['rel'] = 0.4 + 0.9 * wipe, -2.2 * wipe + 0.4 * (1 - wipe)
    P['lsh'], P['lel'] = 0.5, -1.6 * clamp((u - 0.5) / 0.3)
    P['lhand'] = 'fist'
    P['rhand'] = 'open' if wipe > 0.2 else 'fist'
    P['brow'] = -0.65
    P['smile'] = 0.05
    P['sweat'] = 0.7
    P['ey'] = -0.1
    P['lfx'], P['rfx'] = -0.09, 0.09
    P['dip'] = 0.02


def jump_cheer(B, P, amp=1.0):
    f = B % 1
    P['y'] = -0.09 * amp * math.sin(PI * f) ** 1.5
    P['squash'] = 0.05 * math.cos(2 * PI * f) * amp
    P['lsh'] = P['rsh'] = 2.4 + 0.2 * math.sin(PI * B)
    P['lel'] = P['rel'] = 0.25
    P['lhand'] = P['rhand'] = 'open'
    P['smile'] = 1.0
    P['mopen'] = 0.8
    P['mshape'] = 'ah'
    P['brow'] = 0.6
    P['ey'] = -0.3
    P['lfx'], P['rfx'] = -0.06, 0.06


def stare(B, P, sad=1.0):
    br = math.sin(B * PI * 0.4)
    P['lsh'] = P['rsh'] = 0.1
    P['lel'] = P['rel'] = 0.15
    P['brow'] = 0.45 * sad
    P['smile'] = -0.15 * sad
    P['blink'] = 0.3 * sad
    P['ey'] = 0.1
    P['dip'] = 0.004 * br
    P['hnod'] = 0.005


def look_out(B, P):
    """back to camera, one hand on the window glass"""
    P['spin'] = 0.5
    P['rsh'], P['rel'] = 1.2, 1.4
    P['lsh'], P['lel'] = 0.15, 0.2
    P['rhand'] = 'open'
    P['dip'] = 0.004 * math.sin(B * PI * 0.5)


def wave(B, P):
    P['rsh'], P['rel'] = 2.3, 0.4 + 0.35 * math.sin(B * PI * 2)
    P['rhand'] = 'open'
    P['smile'] = 0.9


MOVES = dict(stumble=stumble, freeze_fear=freeze_fear, walk=walk, tired=tired, arms_folded=arms_folded,
             joe_point=joe_point, joe_clap=joe_clap, determined=determined, jump_cheer=jump_cheer, stare=stare,
             look_out=look_out, wave=wave,
             groove=groove, step_touch=step_touch, point_hit=point_hit, spin=spin, arm_roll=arm_roll, shimmy=shimmy,
             slide=slide, kick=kick, knee_drop=knee_drop, play=play, mic_sing=mic_sing, shy=shy, cheer=cheer,
             pose_hold=pose_hold)


# ----------------------------------------------------------------------------- evaluation
def _eval(schedule, t, key, base_kw):
    """schedule: list of (t_start, move_name, kwargs). Returns pose at edit time t."""
    B = T.beat_at(t) - T.PHASE
    cur = None
    prev = None
    for i, (ts, name, kw) in enumerate(schedule):
        if t >= ts:
            prev, cur = cur, (ts, name, kw)
    if cur is None:
        cur = schedule[0]
    def run(entry):
        P = base_pose(**base_kw)
        ts, name, kw = entry
        kw = dict(kw)
        if 'start' in kw and kw['start'] == 'auto':
            kw['start'] = T.beat_at(ts) - T.PHASE
        MOVES[name](B, P, **kw)
        return P
    P = run(cur)
    if prev is not None:
        xf = 0.22 * T.PERIOD
        u = (t - cur[0]) / xf
        if u < 1:
            P = blend(run(prev), P, ease_io(u))
    return P


def perform(schedule, t, key, seed=0, ripple=0.0, sing=None, base_kw=None, lag=0.11):
    """full pose with follow-through (hair/fringe drag), ripple delay, blinks and lip sync."""
    base_kw = base_kw or {}
    tt = t - ripple
    P = _eval(schedule, tt, key, base_kw)
    Pl = _eval(schedule, tt - lag, key, base_kw)
    vx = (P['x'] + P['hip'] + P['lean'] * 0.3) - (Pl['x'] + Pl['hip'] + Pl['lean'] * 0.3)
    P['hair_dx'] = -vx * 0.35
    P['hair_dy'] = (P['dip'] - Pl['dip']) * -0.5
    P['fringe'] = -vx * 6.0
    P['htilt'] += (Pl['lean'] - P['lean']) * 0.6
    # blinks
    per = 3.1 + (seed % 5) * 0.37
    ph = (t + seed * 0.73) % per
    if ph < 0.14:
        P['blink'] = max(P['blink'], math.sin(PI * ph / 0.14))
    # micro life
    P['ex'] += 0.15 * noise1(t * 0.7, seed)
    # lip sync
    if sing:
        v = T.env_at('vocal', t)
        amt = clamp((v - 0.25) * 1.6) * sing
        P['mopen'] = max(P['mopen'], amt)
        if amt > 0.1:
            P['mshape'] = 'o' if noise1(t * 6, seed + 3) > 0.35 else 'ah'
    return P
