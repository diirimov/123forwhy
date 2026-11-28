"""2D character rig (front view), IK solver and the Danse Macabre choreography system."""
import math
from core import *

# ------------------------------------------------------------------ proportions
BASE = dict(thigh=255, shin=245, ankle=22, torso=330, neck=46, head=150, shw=108, hipw=56, uarm=190,
            farm=172, hand=78, slim=1.0)


def props(**kw):
    d = dict(BASE)
    d.update(kw)
    return d


NEUTRAL = dict(px=0.0, py=20.0, lean=0.0, twist=0.0, hip=0.0, head=0.0, turn=0.0, jaw=0.0, nod=0.0, shL=0.0,
               shR=0.0, hLx=-40.0, hLy=330.0, hRx=40.0, hRy=330.0, fLx=-95.0, fLl=0.0, fRx=95.0, fRl=0.0,
               fLa=0.0, fRa=0.0, curl=0.3, eyes=0.0, elbdnL=0.35, elbdnR=0.35)


def ik2(a, t, l1, l2, bend):
    """two bone IK. bend=+1/-1 chooses side. returns (joint, end)"""
    dx, dy = t[0] - a[0], t[1] - a[1]
    d = math.hypot(dx, dy)
    d = min(max(d, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    base = math.atan2(dy, dx)
    cosA = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    A = math.acos(clamp(cosA, -1, 1))
    j = (a[0] + l1 * math.cos(base + bend * A), a[1] + l1 * math.sin(base + bend * A))
    e = (a[0] + d * math.cos(base), a[1] + d * math.sin(base))
    return j, e


def solve(pose, pr):
    """returns joint dict in local coords (ground origin, y down)."""
    p = pose
    leg = pr['thigh'] + pr['shin'] + pr['ankle']
    pel = (p['px'], -leg + p['py'])
    hip_a = p['hip']
    hipL = add(pel, rot((-pr['hipw'], 0), hip_a))
    hipR = add(pel, rot((pr['hipw'], 0), hip_a))
    lean = p['lean']
    neck = add(pel, rot((0, -pr['torso']), lean))
    chest = add(pel, rot((0, -pr['torso'] * 0.62), lean * 0.8))
    tw = p['twist']
    shw = pr['shw']
    shL = add(neck, rot((-shw * (1 - 0.18 * tw), 18 - p['shL']), lean))
    shR = add(neck, rot((shw * (1 + 0.18 * tw), 18 - p['shR']), lean))
    hang = lean + p['head']
    headc = add(neck, rot((0, -pr['neck'] - pr['head'] * 0.5 + p['nod']), lean * 0.6 + p['head'] * 0.3))
    # legs
    J = dict(pel=pel, hipL=hipL, hipR=hipR, neck=neck, chest=chest, shL=shL, shR=shR, headc=headc, hang=hang)
    for s, sg in (('L', -1), ('R', 1)):
        ank_t = (p['f%sx' % s], -pr['ankle'] - p['f%sl' % s])
        hip = J['hip' + s]
        # knees point outward: left leg bends to screen-left
        k1, ank = ik2(hip, ank_t, pr['thigh'], pr['shin'], 1)
        k2, _ = ik2(hip, ank_t, pr['thigh'], pr['shin'], -1)
        knee = k1 if (k1[0] - k2[0]) * sg > 0 else k2
        J['knee' + s], J['ank' + s] = knee, ank
        J['foot' + s] = add(ank, rot((sg * 62 * pr.get('foot', 1.0), 14), p['f%sa' % s] * sg))
        # arms
        sh = J['sh' + s]
        ht = (sh[0] + p['h%sx' % s], sh[1] + p['h%sy' % s])
        e1, wr = ik2(sh, ht, pr['uarm'], pr['farm'], 1)
        e2, _ = ik2(sh, ht, pr['uarm'], pr['farm'], -1)
        # elbows prefer outward and downward
        sc1 = (e1[0] - e2[0]) * sg + p.get('elbdn' + s, 0.35) * (e1[1] - e2[1])
        elb = e1 if sc1 > 0 else e2
        J['elb' + s], J['wr' + s] = elb, wr
        J['hand%sa' % s] = ang(elb, wr)
    return J


# ------------------------------------------------------------------ choreography
def K(**kw):
    d = {}
    d.update(kw)
    return d


# Signature "Danse Macabre" routine - 8 beats. Poses ARRIVE on the beat.
MACABRE = [
    K(fLx=-150, fRx=150, py=70, head=0.2, shR=38, hLx=-150, hLy=130, hRx=150, hRy=-60, jaw=0.3, lean=0.06, curl=0.8),
    K(fLx=-150, fRx=150, py=70, head=-0.2, shL=38, hLx=-150, hLy=-60, hRx=150, hRy=130, jaw=0.0, lean=-0.06, curl=0.8),
    K(fLx=-215, fRx=215, py=150, head=0.0, shL=18, shR=18, hLx=-175, hLy=-215, hRx=175, hRy=-215, jaw=0.65,
      curl=0.1),
    K(fLx=-70, fRx=215, fRl=175, fRa=0.4, py=25, lean=-0.2, head=-0.28, hLx=-170, hLy=-190, hRx=130, hRy=80,
      jaw=0.2, hip=0.15),
    K(fLx=-125, fRx=125, py=80, px=-45, twist=-1, lean=-0.1, head=-0.22, turn=-0.6, shL=30, hLx=-60, hLy=150,
      hRx=-190, hRy=40, jaw=0.0),
    K(fLx=-125, fRx=125, py=80, px=45, twist=1, lean=0.1, head=0.22, turn=0.6, shR=30, hLx=190, hLy=40, hRx=60,
      hRy=150, jaw=0.35),
    K(fLx=-115, fLl=95, fRx=115, fRl=95, py=-105, head=0.0, hLx=-230, hLy=-70, hRx=230, hRy=-70, jaw=0.85,
      fLa=-0.3, fRa=-0.3, curl=0.0),
    K(fLx=-175, fRx=175, py=120, head=0.38, jaw=0.0, hLx=-30, hLy=280, hRx=30, hRy=280, lean=0.08, curl=0.6, elbdnL=-2.0, elbdnR=-2.0),
]


def mirror_key(k):
    m = {}
    for a, v in k.items():
        if a in ('fLx', 'fRx', 'hLx', 'hRx'):
            pass
    sw = {'fLx': 'fRx', 'fRx': 'fLx', 'fLl': 'fRl', 'fRl': 'fLl', 'fLa': 'fRa', 'fRa': 'fLa', 'hLx': 'hRx',
          'hRx': 'hLx', 'hLy': 'hRy', 'hRy': 'hLy', 'shL': 'shR', 'shR': 'shL'}
    for a, v in k.items():
        b = sw.get(a, a)
        if a in ('fLx', 'fRx', 'hLx', 'hRx', 'px', 'lean', 'twist', 'head', 'turn', 'hip'):
            v = -v
        m[b] = v
    return m


MACABRE_M = [mirror_key(k) for k in MACABRE]

# "Bone shuffle" - alternating heel kicks with shoulder shimmy (used for crowds / variation)
SHUFFLE = [
    K(fLx=-110, fRx=150, fRl=70, fRa=0.6, py=60, lean=-0.1, head=0.15, shR=30, hLx=-160, hLy=60, hRx=60, hRy=230,
      jaw=0.2),
    K(fLx=-110, fRx=110, py=95, head=-0.12, shL=30, hLx=-90, hLy=220, hRx=170, hRy=40, jaw=0.0),
    K(fLx=-150, fLl=70, fLa=0.6, fRx=110, py=60, lean=0.1, head=-0.15, shL=30, hLx=-60, hLy=230, hRx=160, hRy=60,
      jaw=0.2),
    K(fLx=-110, fRx=110, py=95, head=0.12, shR=30, hLx=-170, hLy=40, hRx=90, hRy=220, jaw=0.0),
    K(fLx=-160, fRx=160, py=130, head=0.0, hLx=-200, hLy=-150, hRx=200, hRy=-150, jaw=0.7, curl=0.0),
    K(fLx=-160, fRx=160, py=60, twist=0.8, px=30, head=0.25, turn=0.5, hLx=-130, hLy=-200, hRx=190, hRy=-120,
      jaw=0.2),
    K(fLx=-160, fRx=160, py=60, twist=-0.8, px=-30, head=-0.25, turn=-0.5, hLx=-190, hLy=-120, hRx=130, hRy=-200,
      jaw=0.2),
    K(fLx=-130, fRx=130, py=110, head=0.0, hLx=-30, hLy=-260, hRx=30, hRy=-260, jaw=0.9, curl=0.0),
]

# Death's fiddler walk (backward strut, playing): 4 beats
FIDDLER = [
    K(fLx=-70, fRx=110, fRl=0, py=45, lean=0.05, head=0.12, jaw=0.15),
    K(fLx=-110, fLl=0, fRx=70, py=25, lean=-0.03, head=-0.05, jaw=0.0),
    K(fLx=-60, fRx=130, fRl=60, fRa=0.5, py=55, lean=0.1, head=0.2, jaw=0.3),
    K(fLx=-120, fRx=80, py=30, lean=-0.06, head=-0.1, jaw=0.0),
]

KEYS = list(NEUTRAL.keys())


def full(k):
    d = dict(NEUTRAL)
    d.update(k)
    return d


def _routine(name):
    if name == 'macabre':
        return [full(k) for k in MACABRE + MACABRE_M]
    if name == 'shuffle':
        return [full(k) for k in SHUFFLE]
    if name == 'fiddler':
        return [full(k) for k in FIDDLER]
    if name == 'grand':
        return [full(k) for k in MACABRE + SHUFFLE + MACABRE_M + [mirror_key(k) for k in SHUFFLE]]
    raise KeyError(name)


ROUT = {n: _routine(n) for n in ('macabre', 'shuffle', 'fiddler', 'grand')}


def sample_routine(name, b, snap=0.55, stiff=0.0):
    """value of routine at beat b (float). Poses arrive on integer beats with anticipation + follow-through."""
    R = ROUT[name]
    n = len(R)
    k = math.floor(b)
    u = b - k
    a = R[(k - 1) % n]
    cur = R[k % n]
    nxt = R[(k + 1) % n]
    out = {}
    w0 = snap  # transition starts at w0 within the beat interval
    s = clamp((u - w0) / (1 - w0))
    # anticipation: ease-in-back
    kk = 0.45 * (1 - stiff)
    e = s * s * ((kk + 1) * s - kk)
    e = lerp(e, s, stiff)
    for key in KEYS:
        v0, v1, vp = cur[key], nxt[key], a[key]
        v = v0 + (v1 - v0) * e
        # follow-through settle after arriving at cur
        if u < w0:
            v += (v0 - vp) * 0.16 * (1 - stiff) * math.sin(u / 0.22 * math.pi) * math.exp(-u / 0.16)
        out[key] = v
    # foot arcs: lift when a foot travels
    for f in ('L', 'R'):
        dx = abs(nxt['f%sx' % f] - cur['f%sx' % f])
        if dx > 8 and 0 < s < 1:
            out['f%sl' % f] += min(70, dx * 0.8) * math.sin(math.pi * s)
    return out


def dance(name, t, energy=1.0, delay=0.0, amp=1.0, stiff=0.0, groove=1.0, beat_off=0.0):
    """full pose at time t. layered timing for overlapping action."""
    b = beat(t) - delay + beat_off
    core_ = sample_routine(name, b, stiff=stiff)
    headp = sample_routine(name, b - 0.07 * (1 - stiff), stiff=stiff)
    armp = sample_routine(name, b - 0.05 * (1 - stiff), stiff=stiff)
    pose = {}
    for key in KEYS:
        v = core_[key]
        if key in ('head', 'turn', 'jaw', 'nod'):
            v = headp[key]
        if key[:2] in ('hL', 'hR'):
            v = armp[key]
        n0 = NEUTRAL[key]
        pose[key] = n0 + (v - n0) * amp * energy
    # groove: bounce down on every beat, small lift on the "and"
    ph = (b % 1.0)
    bounce = math.exp(-ph / 0.18) - 0.25
    pose['py'] += 22 * bounce * groove * energy
    pose['nod'] += -10 * math.exp(-max(0, ph - 0.06) / 0.2) * groove * energy
    return pose


def blend(p1, p2, t):
    return {k: lerp(p1[k], p2[k], t) for k in KEYS}


def pose(**kw):
    return full(kw)
