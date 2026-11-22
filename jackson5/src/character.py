"""
Character designs + rig + renderer for the five brothers.

Coordinates: a character stands with feet on ground point (gx, gy); all body dimensions are
fractions of the character's height h (px).  Skia y grows downward.
Arm angles: measured from straight down, positive = swung outward (away from the body).
Forearm absolute angle = shoulder angle + elbow angle (same convention).
"""
import math
from dataclasses import dataclass, field
import numpy as np
import skia
from gfx import (paint, cel, smooth_path, limb_outline, ellipse_path, shade, mix, alpha, tint,
                 rad_grad, lin_grad, shader_paint, poly_path, hexc, glow)

HAIR = '#1d1410'
HAIR_HI = '#4a362a'


@dataclass
class Design:
    name: str
    height: float        # relative to Michael = 1.0
    head: float          # head radius / h
    skin: str
    afro: tuple          # (rx, ry) in head radii
    face_w: float = 0.86
    jaw: float = 0.5     # 0 round .. 1 square/long
    eye: float = 1.0
    eye_sp: float = 0.36
    brow_w: float = 1.0
    nose_w: float = 1.0
    lip: str = '#7a3f38'
    shoulders: float = 0.23
    leg: float = 0.47
    sideburns: bool = False
    mustache: float = 0.0
    seed: int = 1
    sig: str = '#7b3fa0'   # signature colour
    smile_bias: float = 0.0
    hair: str = 'afro'     # 'afro' | 'short'
    hair_cy: float = 0.30  # hair mass centre above head centre (head radii)
    bump: float = 1.0      # afro lobe amplitude
    hair_col: str = '#1d1410'
    glasses: str = None    # frame colour (Beat It episode: Quincy Jones)
    beard: float = 0.0


BROTHERS = {
    'jackie':   Design('Jackie', 1.30, 0.088, '#8a5a3b', (1.30, 1.22), face_w=0.80, jaw=0.85, eye=0.86, eye_sp=0.35,
                       brow_w=1.05, nose_w=1.05, shoulders=0.235, leg=0.49, sideburns=True, seed=11, sig='#1f8a8a'),
    'tito':     Design('Tito', 1.22, 0.092, '#6c442e', (1.38, 1.25), face_w=0.88, jaw=0.75, eye=0.88, eye_sp=0.36,
                       brow_w=1.2, nose_w=1.1, shoulders=0.245, leg=0.48, sideburns=True, mustache=0.6, seed=22,
                       sig='#c98a1b'),
    'jermaine': Design('Jermaine', 1.17, 0.095, '#7a4c33', (1.62, 1.48), face_w=0.86, jaw=0.6, eye=0.95, eye_sp=0.37,
                       brow_w=1.0, nose_w=1.0, shoulders=0.235, leg=0.475, seed=33, sig='#a3263a', smile_bias=0.25),
    'marlon':   Design('Marlon', 1.10, 0.098, '#8f5e3f', (1.25, 1.2), face_w=0.84, jaw=0.45, eye=1.0, eye_sp=0.36,
                       brow_w=0.9, nose_w=0.95, shoulders=0.225, leg=0.47, seed=44, sig='#3c8a3a'),
    'michael':  Design('Michael', 1.00, 0.112, '#945f3e', (1.55, 1.46), face_w=0.86, jaw=0.25, eye=1.16, eye_sp=0.37,
                       brow_w=0.85, nose_w=0.9, shoulders=0.215, leg=0.455, seed=55, sig='#6b2fa0', smile_bias=0.15),
}
ORDER = ['jackie', 'tito', 'michael', 'jermaine', 'marlon']   # classic stage line-up, Michael centre

# Joe Jackson + non-family supporting characters (never drawn with an afro, so they can't read as a sixth brother)
ADULTS = {
    'joe': Design('Joe', 1.66, 0.074, '#664230', (1.04, 1.0), face_w=0.9, jaw=1.0, eye=0.78, eye_sp=0.33, brow_w=1.5,
                  nose_w=1.15, lip='#55302a', shoulders=0.27, leg=0.5, mustache=0.9, seed=66, sig='#4e3b2e',
                  hair='short', hair_cy=0.12, bump=0.15),
    'dj': Design('DJ', 1.55, 0.078, '#7a5034', (1.08, 1.04), face_w=0.9, jaw=0.7, eye=0.9, eye_sp=0.35, brow_w=1.1,
                 shoulders=0.26, leg=0.49, mustache=0.5, seed=77, sig='#d0622a', hair='short', hair_cy=0.14, bump=0.2,
                 smile_bias=0.4),
    'kid1': Design('Kid', 1.0, 0.11, '#7a5034', (1.04, 1.0), seed=81, hair='short', hair_cy=0.12, bump=0.2),
    'kid2': Design('Kid', 0.9, 0.115, '#8a5a3a', (1.04, 1.0), seed=82, hair='short', hair_cy=0.12, bump=0.2),
}
# Michael through the years (heights relative to 10-year-old Michael = 1.0)
MICHAEL_AGES = {
    'michael72': Design('Michael', 1.22, 0.098, '#945f3e', (1.72, 1.58), face_w=0.84, jaw=0.3, eye=1.12, eye_sp=0.36,
                        brow_w=0.85, nose_w=0.9, shoulders=0.215, leg=0.46, seed=56, sig='#6b2fa0', smile_bias=0.15),
    'michael79': Design('Michael', 1.52, 0.074, '#95603f', (1.32, 1.26), face_w=0.82, jaw=0.5, eye=1.05, eye_sp=0.35,
                        brow_w=0.85, nose_w=0.82, shoulders=0.21, leg=0.5, seed=57, sig='#6b2fa0', smile_bias=0.1),
    'michael84': Design('Michael', 1.62, 0.072, '#9a6646', (1.42, 1.62), face_w=0.8, jaw=0.6, eye=1.05, eye_sp=0.34,
                        brow_w=0.8, nose_w=0.76, lip='#7a3f3c', shoulders=0.205, leg=0.51, seed=58, sig='#6b2fa0',
                        hair='curl', hair_cy=-0.3, bump=0.7, hair_col='#140c0a'),
}
# The Jacksons, 1984 Victory Tour line-up (six brothers incl. Randy). Adult proportions, curls/short hair - never the child models.
BROTHERS84 = {
    'jackie84': Design('Jackie', 1.70, 0.071, '#8a5a3b', (1.32, 1.45), face_w=0.82, jaw=0.85, eye=0.85, brow_w=1.05,
                       nose_w=1.05, shoulders=0.235, leg=0.5, mustache=0.6, seed=111, sig='#1f8a8a', hair='curl', hair_cy=-0.18, bump=0.6),
    'tito84': Design('Tito', 1.66, 0.071, '#6c442e', (1.12, 1.12), face_w=0.9, jaw=0.95, eye=0.85, brow_w=1.2,
                     nose_w=1.1, shoulders=0.25, leg=0.49, mustache=0.95, seed=122, sig='#c98a1b', hair='short', hair_cy=0.15, bump=0.3),
    'jermaine84': Design('Jermaine', 1.70, 0.071, '#7a4c33', (1.42, 1.62), face_w=0.86, jaw=0.7, eye=0.92, brow_w=1.0,
                         shoulders=0.24, leg=0.5, mustache=0.35, seed=133, sig='#a3263a', hair='curl', hair_cy=-0.3, bump=0.7, smile_bias=0.25),
    'marlon84': Design('Marlon', 1.60, 0.071, '#8f5e3f', (1.3, 1.4), face_w=0.84, jaw=0.6, eye=0.95, brow_w=0.95,
                       shoulders=0.225, leg=0.5, mustache=0.5, seed=144, sig='#3c8a3a', hair='curl', hair_cy=-0.15, bump=0.6),
    'randy84': Design('Randy', 1.64, 0.071, '#90603f', (1.34, 1.45), face_w=0.84, jaw=0.5, eye=1.0, brow_w=0.95,
                      shoulders=0.225, leg=0.5, seed=155, sig='#3a5ad0', hair='curl', hair_cy=-0.2, bump=0.6, smile_bias=0.1),
}
ADULTS['joe84'] = Design('Joe', 1.68, 0.07, '#664230', (1.04, 1.0), face_w=0.92, jaw=1.0, eye=0.76, eye_sp=0.33, brow_w=1.45,
                         nose_w=1.15, lip='#55302a', shoulders=0.285, leg=0.49, mustache=0.9, seed=67, sig='#4e3b2e',
                         hair='short', hair_cy=0.12, bump=0.15, hair_col='#7a726c')
DESIGNS = dict(BROTHERS, **ADULTS, **MICHAEL_AGES, **BROTHERS84)
LINEUP84 = ['jackie84', 'tito84', 'jermaine84', 'michael84', 'marlon84', 'randy84']


@dataclass
class Outfit:
    shirt: str
    pants: str
    shoes: str = '#1a1210'
    vest: str = None
    collar: str = None       # big 70s collar colour (None = shirt colour)
    fringe: bool = False
    turtleneck: bool = False
    jumpsuit: bool = False
    belt: str = None
    stripes: str = None
    sparkle: bool = False
    hat: str = None
    tie: str = None
    flare: bool = True
    glove: int = 0           # +1 = sparkly glove on the screen-right hand
    socks: str = None
    military: str = None     # gold/silver frogging + epaulettes colour
    bowtie: str = None
    zips: bool = False       # zippered leather jacket (Beat It, 1983)
    under: str = None        # undershirt colour showing in an open jacket front
    chevron: str = None      # Thriller-style V stripes on a leather jacket
    buckles: str = None      # Bad-era straps and buckles


def outfits(era):
    """Era wardrobes; each brother keeps his signature colour across eras for recognisability."""
    o = {}
    for k, d in BROTHERS.items():
        s = d.sig
        if era == 'home':
            o[k] = Outfit(shirt=mix(s, '#d9c7a8', 0.45), pants=mix('#5a4a3a', s, 0.15), stripes=shade(s, -0.1),
                          collar=mix(s, '#f0e6d0', 0.6))
        elif era == 'club':
            o[k] = Outfit(shirt='#efe6d6', pants='#1d1418', vest='#9e1b2a', collar='#f6efe2', belt='#1a1214')
        elif era == 'studio':
            o[k] = Outfit(shirt=mix(s, '#3a2a40', 0.2), pants=mix('#2a2230', s, 0.2), turtleneck=True)
        elif era == 'tv':
            o[k] = Outfit(shirt=mix(s, '#ffffff', 0.15), pants=shade(s, -0.25), vest=mix(s, '#f2c14e', 0.55),
                          fringe=True, collar='#fff4dc')
        elif era == 'arena':
            o[k] = Outfit(shirt='#f4efe6', pants='#f4efe6', jumpsuit=True, belt='#d9a92b', collar='#f4efe6',
                          vest=None, sparkle=True, stripes=s)
    return o


def outfits84():
    o = {}
    for k in BROTHERS84:
        s = BROTHERS84[k].sig
        o[k] = Outfit(shirt=mix(s, '#d8d8e8', 0.25), pants='#ecebf2', collar=mix(s, '#ffffff', 0.5), sparkle=True,
                      flare=False, belt='#c8c8d8', shoes='#e8e8f0', military='#dcdce8')
    o['michael84'] = Outfit(shirt='#16141c', pants='#16141c', collar='#2a2a36', sparkle=True, flare=False, glove=1,
                            socks='#f4f4f8', military='#d9b24a', shoes='#0c0c10')
    return o


MICHAEL_OUTFITS = {
    'michael72': Outfit(shirt='#c8642a', pants='#5a3a2a', collar='#f2e0c0'),
    'michael79': Outfit(shirt='#141218', pants='#141218', collar='#f4f0e8', bowtie='#0c0a0e', flare=False, socks='#f4f4f8',
                        shoes='#0c0c10'),
    'michael82': Outfit(shirt='#16141c', pants='#16141c', collar='#2a2a36', sparkle=True, flare=False, glove=1,
                        socks='#f4f4f8', military='#d9b24a', shoes='#0c0c10'),
}
JOE84_OUTFIT = Outfit(shirt='#3a3a46', pants='#2a2a30', collar='#ece6d8', tie='#5a1a2a', hat='#4a4448', shoes='#141010',
                      flare=False)

JOE_OUTFIT = Outfit(shirt='#4e3b2e', pants='#26221f', collar='#ece6d8', tie='#6a1c1c', hat='#2a2623', shoes='#141010',
                    flare=False)
DJ_OUTFIT = Outfit(shirt='#d0622a', pants='#2a2430', collar='#f4d06a', stripes='#a8481a')


# ----------------------------------------------------------------------------- pose
POSE_KEYS = ['x', 'dip', 'lean', 'hip', 'tw', 'htilt', 'hyaw', 'hnod', 'lsh', 'lel', 'rsh', 'rel',
             'lfx', 'lfy', 'rfx', 'rfy', 'smile', 'mopen', 'brow', 'ex', 'ey', 'blink', 'spin', 'squash',
             'hair_dx', 'hair_dy', 'fringe', 'y', 'strum', 'fear', 'sweat']


def base_pose(**kw):
    p = dict(x=0.0, y=0.0, dip=0.0, lean=0.0, hip=0.0, tw=0.0, htilt=0.0, hyaw=0.0, hnod=0.0,
             lsh=0.18, lel=0.25, rsh=0.18, rel=0.25,
             lfx=-0.075, lfy=0.0, rfx=0.075, rfy=0.0,
             smile=0.6, mopen=0.0, brow=0.0, ex=0.0, ey=0.0, blink=0.0, spin=0.0, squash=0.0,
             hair_dx=0.0, hair_dy=0.0, fringe=0.0, strum=0.0, fear=0.0, sweat=0.0, headphones=False,
             lhand='relaxed', rhand='relaxed', mshape='smile', instrument=None, mic=False)
    p.update(kw)
    return p


def blend(a, b, t):
    out = dict(a)
    for k in POSE_KEYS:
        out[k] = a[k] + (b[k] - a[k]) * t
    if t > 0.5:
        for k in ('lhand', 'rhand', 'mshape', 'instrument', 'mic'):
            out[k] = b[k]
    return out


# ----------------------------------------------------------------------------- IK
def ik2(root, target, L1, L2, bend_sign):
    rx, ry = root
    dx, dy = target[0] - rx, target[1] - ry
    d = min(math.hypot(dx, dy), (L1 + L2) * 0.999)
    d = max(d, abs(L1 - L2) + 1e-3)
    base = math.atan2(dy, dx)
    a = math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    ang = base + bend_sign * a
    joint = (rx + L1 * math.cos(ang), ry + L1 * math.sin(ang))
    ex = (rx + dx / math.hypot(dx, dy) * d if math.hypot(dx, dy) > 0 else rx,
          ry + dy / math.hypot(dx, dy) * d if math.hypot(dx, dy) > 0 else ry)
    return joint, ex


def arm_angles_from_target(side, shoulder, target, L1, L2):
    """side -1 = screen-left arm. returns (sh, el) in the outward-from-down convention (elbow hangs low)."""
    best = None
    for bend in (1, -1):
        elbow, wrist = ik2(shoulder, target, L1, L2, bend)
        if best is None or elbow[1] > best[0][1]:
            best = (elbow, wrist)
    elbow, wrist = best
    def ang(p, q):
        return math.atan2((q[0] - p[0]) * side, q[1] - p[1])
    sh = ang(shoulder, elbow)
    fa = ang(elbow, wrist)
    return sh, fa - sh


# ----------------------------------------------------------------------------- renderer
class Character:
    def __init__(self, key):
        self.key = key
        self.d = DESIGNS[key]
        rng = np.random.default_rng(self.d.seed)
        n = 26
        self.afro_bumps = rng.uniform(0.0, 1.0, n)
        self.curls = [(rng.uniform(0, 2 * np.pi), rng.uniform(0.15, 0.95), rng.uniform(0, 2 * np.pi),
                       rng.uniform(0.6, 1.3)) for _ in range(140)]

    # ---- skeleton
    def skeleton(self, gx, gy, h, P):
        d = self.d
        leg = d.leg * h
        thigh, shin = leg * 0.51, leg * 0.53
        dip = P['dip'] * h
        pel = (gx + P['x'] * h + P['hip'] * h, gy + P['y'] * h - leg + dip)
        lean = P['lean']
        torso = 0.255 * h
        chest = (pel[0] + math.sin(lean) * torso, pel[1] - math.cos(lean) * torso)
        hipw = 0.05 * h
        lhip = (pel[0] - hipw, pel[1])
        rhip = (pel[0] + hipw, pel[1])
        lfoot = (gx + P['x'] * h + P['lfx'] * h, gy + P['y'] * h + P['lfy'] * h)
        rfoot = (gx + P['x'] * h + P['rfx'] * h, gy + P['y'] * h + P['rfy'] * h)
        lknee, lankle = ik2(lhip, lfoot, thigh, shin, 1)
        rknee, rankle = ik2(rhip, rfoot, thigh, shin, -1)
        # foreshorten knee lateral offset (front view: knees mostly bend toward camera)
        def fs(hp, kn, an):
            mx = (hp[0] + an[0]) / 2
            return (mx + (kn[0] - mx) * 0.55, kn[1])
        lknee = fs(lhip, lknee, lankle)
        rknee = fs(rhip, rknee, rankle)
        shw = d.shoulders * h * 0.5 * (1 - 0.18 * abs(P['tw']))
        ca, sa = math.cos(lean), math.sin(lean)
        def rot(dx, dy):
            return (chest[0] + dx * ca - dy * sa, chest[1] + dx * sa + dy * ca)
        lsh = rot(-shw, 0.018 * h)
        rsh = rot(shw, 0.018 * h)
        neck = rot(P['tw'] * 0.01 * h, -0.03 * h)
        hr = d.head * h
        ht = lean * 0.6 + P['htilt']
        head = (neck[0] + math.sin(ht) * hr * 1.05 + P['hyaw'] * 0.05 * h,
                neck[1] - math.cos(ht) * hr * 1.05 + P['hnod'] * h)
        ua, fa = 0.155 * h, 0.145 * h
        arms = {}
        for side, s_, sh, el in ((-1, lsh, P['lsh'], P['lel']), (1, rsh, P['rsh'], P['rel'])):
            a1 = sh + (lean if side > 0 else -lean) * 0.5
            a2 = a1 + el
            elbow = (s_[0] + side * math.sin(a1) * ua, s_[1] + math.cos(a1) * ua)
            wrist = (elbow[0] + side * math.sin(a2) * fa, elbow[1] + math.cos(a2) * fa)
            arms[side] = (s_, elbow, wrist, a2)
        return dict(pel=pel, chest=chest, lhip=lhip, rhip=rhip, lknee=lknee, rknee=rknee, lfoot=lankle,
                    rfoot=rankle, lsh=lsh, rsh=rsh, neck=neck, head=head, hr=hr, ht=ht, arms=arms, h=h,
                    ua=ua, fa=fa)

    # ---- main draw
    def draw(self, canvas, gx, gy, h, P, outfit, L, t=0.0, shadow=True):
        """L: lighting dict(key=(dx,dy), amb=colour, amb_a, rim=colour, line=colour, floor_shadow=a)"""
        d = self.d
        sp = math.cos(P['spin'] * 2 * math.pi)
        back = sp < 0
        if shadow and L.get('floor_shadow', 0.35) > 0:
            canvas.drawOval(skia.Rect.MakeXYWH(gx + P['x'] * h - 0.17 * h, gy + P['y'] * h - 0.022 * h, 0.34 * h, 0.044 * h),
                            paint((0.05, 0.02, 0.05, L.get('floor_shadow', 0.35)), blur=0.02 * h))
        canvas.save()
        sx = max(abs(sp), 0.42) * (1 if sp >= 0 else -1)
        cx = gx + P['x'] * h
        canvas.translate(cx, gy)
        canvas.scale(sx, 1 + P['squash'])
        canvas.translate(-cx, -gy)
        smear = abs(sp) < 0.55
        if smear:
            lp = skia.Paint()
            lp.setImageFilter(skia.ImageFilters.Blur(0.03 * h * (1 - abs(sp) / 0.55) + 0.1, 0.1))
            canvas.saveLayer(None, lp)
        S = self.skeleton(gx, gy, h, P)
        P = dict(P, _t=t)
        if P.get('instrument'):
            self._inst_geom(S, P)
            ua, fa = S['ua'], S['fa']
            for side, tgt in ((-1, S['strum_pt']), (1, S['fret_pt'])):
                sh_pt = S['lsh'] if side < 0 else S['rsh']
                a, e = arm_angles_from_target(side, sh_pt, tgt, ua, fa)
                a1 = a
                el_ = (sh_pt[0] + side * math.sin(a1) * ua, sh_pt[1] + math.cos(a1) * ua)
                wr_ = (el_[0] + side * math.sin(a1 + e) * fa, el_[1] + math.cos(a1 + e) * fa)
                S['arms'][side] = (sh_pt, el_, wr_, a1 + e)
            P = dict(P, lhand='fist', rhand='relaxed')
        col = lambda c: tint(c, L['amb'], L.get('amb_a', 0.25))
        line = L.get('line', '#2a1418')
        lw = max(1.2, 0.0055 * h)
        self._afro(canvas, S, P, col, L, back_layer=True)
        self._legs(canvas, S, P, outfit, col, L, line, lw)
        far, near = (1, -1) if not back else (-1, 1)
        if P.get('instrument'):
            self._torso(canvas, S, P, outfit, col, L, line, lw, back, t)
            self._neck_head(canvas, S, P, col, L, line, lw, back, t)
            self._instrument(canvas, S, P, col, L, line, lw, t)
            self._arm(canvas, S, 1, P, outfit, col, L, line, lw)
            self._arm(canvas, S, -1, P, outfit, col, L, line, lw)
        else:
            self._torso(canvas, S, P, outfit, col, L, line, lw, back, t)
            self._neck_head(canvas, S, P, col, L, line, lw, back, t)
            self._arm(canvas, S, -1, P, outfit, col, L, line, lw)
            self._arm(canvas, S, 1, P, outfit, col, L, line, lw)
        if outfit.hat:
            self._hat(canvas, S, P, outfit, col, L, line, lw)
        if P.get('headphones'):
            hx, hy = S['head']
            r = S['hr']
            canvas.drawArc(skia.Rect.MakeXYWH(hx - r * 1.08, hy - r * 1.25, r * 2.16, r * 1.9), 180, 180, False,
                           paint('#1a1a1e', style='stroke', width=r * 0.14))
            for side in (-1, 1):
                canvas.drawRoundRect(skia.Rect.MakeXYWH(hx + side * r * 1.0 - r * 0.2, hy - r * 0.2, r * 0.4, r * 0.55),
                                     r * 0.15, r * 0.15, paint('#26262c'))
        if smear:
            canvas.restore()
        canvas.restore()
        return S

    # ---- parts
    def _afro(self, canvas, S, P, col, L, back_layer=True, front=False):
        d = self.d
        hx, hy = S['head']
        r = S['hr']
        rx, ry = d.afro[0] * r, d.afro[1] * r
        cx = hx + P['hair_dx'] * S['h'] - P['hyaw'] * 0.08 * r
        cy = hy - d.hair_cy * r + P['hair_dy'] * S['h']
        pts = []
        ph = self.afro_bumps
        lobes = 15
        for i in range(120):
            th = i / 120 * 2 * math.pi
            bump = (1 + d.bump * (0.028 * math.sin(2 * th + ph[0] * 6) + 0.02 * math.sin(3 * th + ph[1] * 6)
                    + 0.03 * abs(math.sin(lobes * th / 2 + ph[2] * 3)) * (0.7 + 0.6 * ph[int(i / 120 * len(ph))])))
            pts.append((cx + math.cos(th) * rx * bump, cy + math.sin(th) * ry * bump * (1 + 0.04 * P['dip'])))
        if d.hair in ('shag', 'longcurl'):     # shoulder-length hair (feathered / long curls)
            pts = []
            for i in range(90):
                th = i / 90 * 2 * math.pi
                c_, s_ = math.cos(th), math.sin(th)
                if s_ < 0:           # crown
                    x_, y_ = c_ * rx, cy + s_ * ry
                else:                # long sides falling past the jaw, ragged ends
                    wob = 0.08 * math.sin(i * 2.7 + ph[i % len(ph)] * 5) * r
                    x_ = c_ * (rx * (1.08 + 0.2 * s_)) + wob
                    y_ = cy + s_ * ry * (2.9 - 0.35 * abs(c_)) + abs(wob) * 1.5
                pts.append((cx + x_, y_))
        path = smooth_path(pts, True, 0.5)
        path.transform(skia.Matrix.RotateDeg(math.degrees(S['ht'] * 0.8), skia.Point(hx, hy)))
        kx, ky = L['key']
        base = col(d.hair_col)
        canvas.save()
        canvas.drawPath(path, shader_paint(rad_grad((cx + kx * rx * 0.45, cy + ky * ry * 0.45), max(rx, ry) * 1.25,
                                                    [shade(base, 0.22), base, shade(base, -0.4)], [0, 0.55, 1])))
        canvas.clipPath(path, doAntiAlias=True)
        cp = paint(alpha(col(mix(HAIR_HI, d.hair_col, 0.3) if d.hair_col != HAIR else HAIR_HI), 0.33), style='stroke',
                   width=max(1.0, r * 0.045))
        if d.hair in ('curl', 'longcurl'):     # glossy curls: tighter ringlets + specular sheen
            for k in range(26):
                a0 = k / 26 * 2 * math.pi
                hx_, hy_ = cx + math.cos(a0) * rx * 0.82, cy + math.sin(a0) * ry * 0.85
                canvas.drawArc(skia.Rect.MakeXYWH(hx_ - r * 0.16, hy_ - r * 0.16, r * 0.32, r * 0.32), 200, 230, False,
                               paint((0.9, 0.85, 0.8, 0.28), style='stroke', width=max(1.0, r * 0.05)))
            canvas.drawArc(skia.Rect.MakeXYWH(cx - rx * 0.7, cy - ry * 0.85, rx * 1.1, ry * 0.9), 200, 70, False,
                           paint((1, 0.95, 0.9, 0.35), style='stroke', width=r * 0.09, blur=r * 0.03))
        if d.hair == 'shag':
            sp_ = paint(alpha(col(shade(d.hair_col, 0.35)), 0.45), style='stroke', width=max(1.0, r * 0.035))
            for k in range(22):
                x0_ = cx + (-1 + 2 * k / 21) * rx * 0.95
                cp_ = skia.Path()
                cp_.moveTo(cx + (x0_ - cx) * 0.3, cy - ry * 0.9)
                cp_.quadTo(x0_ * 1.0 + (x0_ - cx) * 0.1, cy, x0_ + (x0_ - cx) * 0.15, cy + ry * 2.2)
                canvas.drawPath(cp_, sp_)
        for (th, rr, rot, sz) in (self.curls if d.hair not in ('shag',) else []):
            x = cx + math.cos(th) * rx * rr
            y = cy + math.sin(th) * ry * rr
            s = r * 0.07 * sz
            oval = skia.Rect.MakeLTRB(x - s, y - s, x + s, y + s)
            canvas.drawArc(oval, math.degrees(rot), 200, False, cp)
        # rim light on the side away from key light
        rim = skia.Path(path)
        rim.setFillType(skia.PathFillType.kInverseWinding)
        rim.offset(-kx * r * 0.09, -ky * r * 0.09)
        canvas.drawPath(rim, paint(alpha(L['rim'], 0.85), blur=r * 0.05))
        canvas.restore()
        self._afro_path = path

    def _legs(self, canvas, S, P, o, col, L, line, lw):
        h = S['h']
        pc = col(o.pants)
        kd = L['key']
        # seat
        pel = S['pel']
        seat = smooth_path([(S['lhip'][0] - 0.036 * h, pel[1] - 0.03 * h), (S['rhip'][0] + 0.036 * h, pel[1] - 0.03 * h),
                            (S['rhip'][0] + 0.03 * h, pel[1] + 0.045 * h), (pel[0], pel[1] + 0.07 * h),
                            (S['lhip'][0] - 0.03 * h, pel[1] + 0.045 * h)], True, 0.4)
        for side in (-1, 1):
            hip = S['lhip'] if side < 0 else S['rhip']
            knee = S['lknee'] if side < 0 else S['rknee']
            foot = S['lfoot'] if side < 0 else S['rfoot']
            hip2 = (hip[0] + side * 0.004 * h, hip[1] - 0.012 * h)
            ank = (foot[0], foot[1] - (0.062 if o.socks else 0.035) * h)
            # shoe first (pants flare covers it)
            shoe = ellipse_path(foot[0] + side * 0.012 * h, foot[1] - 0.016 * h, 0.05 * h, 0.022 * h, side * 0.12)
            cel(canvas, shoe, col(o.shoes), kd, -0.4, outline=line, ow=lw, hi=0.6)
            if o.socks:
                sock = limb_outline([(foot[0], foot[1] - 0.075 * h), (foot[0], foot[1] - 0.02 * h)], [0.05 * h, 0.048 * h], False, False)
                canvas.drawPath(sock, paint(col(o.socks)))
                cel(canvas, shoe, col(o.shoes), kd, -0.4, outline=line, ow=lw, hi=0.8)
            leg = limb_outline([hip2, knee, ank], [0.084 * h, 0.064 * h, 0.1 * h if o.flare else 0.066 * h])
            cel(canvas, leg, pc, kd, -0.3, outline=line, ow=lw)
            if o.jumpsuit and o.stripes:
                st = limb_outline([(hip2[0] + side * 0.035 * h, hip2[1]), (knee[0] + side * 0.03 * h, knee[1]),
                                   (ank[0] + side * 0.045 * h, ank[1])], [0.012 * h] * 3, False, False)
                canvas.drawPath(st, paint(col(o.stripes)))
            # crease at knee
            canvas.drawLine(knee[0] - 0.018 * h, knee[1] + 0.008 * h, knee[0] + 0.012 * h, knee[1] - 0.004 * h,
                            paint(alpha(shade(pc, -0.45), 0.6), style='stroke', width=lw * 0.8))
        cel(canvas, seat, pc, kd, -0.3, outline=None)

    def _torso(self, canvas, S, P, o, col, L, line, lw, back, t):
        h = S['h']
        kd = L['key']
        pel, ch = S['pel'], S['chest']
        lean = P['lean']
        ca, sa = math.cos(lean), math.sin(lean)
        def R(dx, dy, org=ch):
            return (org[0] + dx * ca - dy * sa, org[1] + dx * sa + dy * ca)
        shw = self.d.shoulders * h * 0.5 * (1 - 0.18 * abs(P['tw']))
        waist = 0.08 * h
        sc = col(o.shirt)
        tw = P['tw'] * 0.035 * h
        body = smooth_path([R(-shw * 0.55, -0.032 * h), R(-shw - 0.012 * h, 0.0), R(-shw * 0.97, 0.06 * h),
                            R(-waist - 0.004 * h, 0.17 * h), R(-waist - 0.012 * h, 0.27 * h), R(0 + tw, 0.285 * h),
                            R(waist + 0.012 * h, 0.27 * h), R(waist + 0.004 * h, 0.17 * h), R(shw * 0.97, 0.06 * h),
                            R(shw + 0.012 * h, 0.0), R(shw * 0.55, -0.032 * h), R(0 + tw, -0.04 * h)], True, 0.45)
        cel(canvas, body, sc, kd, -0.33, outline=line, ow=lw, hi=0.35)
        canvas.save()
        canvas.clipPath(body, doAntiAlias=True)
        if o.stripes and not o.jumpsuit:
            for k in range(-6, 9):
                y = 0.035 * k * h
                a, b = R(-shw * 1.3, y), R(shw * 1.3, y)
                canvas.drawLine(*a, *b, paint(alpha(col(o.stripes), 0.55), style='stroke', width=0.012 * h))
        if o.jumpsuit and o.stripes:
            for side in (-1, 1):
                a, b = R(side * shw * 0.75, -0.02 * h), R(side * waist * 0.55, 0.27 * h)
                canvas.drawLine(*a, *b, paint(col(o.stripes), style='stroke', width=0.016 * h))
        if o.vest and not back:
            vest = poly_path([R(-shw * 1.2, -0.04 * h), R(-0.03 * h + tw, -0.04 * h), R(tw, 0.14 * h),
                              R(0.03 * h + tw, -0.04 * h), R(shw * 1.2, -0.04 * h), R(shw * 1.2, 0.31 * h),
                              R(-shw * 1.2, 0.31 * h)])
            cel(canvas, vest, col(o.vest), kd, -0.35, outline=line, ow=lw * 0.9, hi=0.3)
        elif o.vest and back:
            canvas.drawRect(skia.Rect.MakeLTRB(ch[0] - shw * 1.3, ch[1] - 0.05 * h, ch[0] + shw * 1.3, ch[1] + 0.32 * h),
                            paint(col(shade(o.vest, -0.22))))
        if back:      # garment detail on the back: shoulder yoke, centre seam, side shading (never reads as bare skin)
            yc = col(shade(o.collar or o.shirt, -0.1))
            yoke = smooth_path([R(-shw * 1.1, -0.03 * h), R(shw * 1.1, -0.03 * h), R(shw * 0.9, 0.05 * h), R(0, 0.075 * h),
                                R(-shw * 0.9, 0.05 * h)], True, 0.3)
            canvas.drawPath(yoke, paint(yc))
            canvas.drawPath(yoke, paint(line, style='stroke', width=lw * 0.7))
            canvas.drawLine(*R(0, 0.075 * h), *R(0, 0.28 * h), paint(alpha(line, 0.6), style='stroke', width=lw * 0.8))
            for sd in (-1, 1):
                canvas.drawLine(*R(sd * shw * 0.55, 0.1 * h), *R(sd * waist * 0.6, 0.27 * h), paint(alpha(line, 0.3), style='stroke', width=lw * 0.6))
        if not back and not o.turtleneck:
            for k in range(4):
                bx, by = R(tw * 0.9, 0.04 * h + k * 0.055 * h)
                if not o.vest or k == 0:
                    canvas.drawCircle(bx, by, 0.006 * h, paint(shade(sc, -0.35)))
        if o.belt:
            a = R(-shw * 1.4, 0.245 * h)
            b = R(shw * 1.4, 0.245 * h)
            canvas.drawLine(*a, *b, paint(col(o.belt), style='stroke', width=0.028 * h, cap='butt'))
            bx, by = R(tw, 0.245 * h)
            canvas.drawRoundRect(skia.Rect.MakeXYWH(bx - 0.02 * h, by - 0.017 * h, 0.04 * h, 0.034 * h), 3, 3,
                                 paint(shade(col(o.belt), 0.35)))
        if o.sparkle:
            rng = np.random.default_rng(self.d.seed)
            for k in range(18):
                px, py = R(rng.uniform(-shw, shw), rng.uniform(-0.02, 0.27) * h)
                tw_ = 0.5 + 0.5 * math.sin(t * 7 + k * 1.7)
                canvas.drawCircle(px, py, 0.0045 * h * (0.5 + tw_), paint((1, 0.95, 0.75, 0.5 + 0.5 * tw_)))
        if o.zips and not back:
            zc = (0.86, 0.86, 0.9, 0.95)
            front = poly_path([R(tw - 0.03 * h, -0.04 * h), R(tw + 0.03 * h, -0.04 * h), R(tw + 0.05 * h, 0.3 * h), R(tw - 0.05 * h, 0.3 * h)])
            canvas.drawPath(front, paint(col(o.under or '#141218')))
            for sd in (-1, 1):
                a, b = R(tw + sd * 0.03 * h, -0.04 * h), R(tw + sd * 0.05 * h, 0.3 * h)
                canvas.drawLine(*a, *b, paint(zc, style='stroke', width=0.006 * h))
            for k in range(5):          # quilted horizontal ribs across the chest
                y = 0.0 + k * 0.022 * h
                for sd in (-1, 1):
                    a, b = R(tw + sd * 0.06 * h, y), R(sd * shw * 1.1, y - 0.01 * h)
                    canvas.drawLine(*a, *b, paint(alpha(shade(sc, -0.4), 0.7), style='stroke', width=0.004 * h))
            for sd in (-1, 1):          # diagonal pocket zips
                for k in range(2):
                    a, b = R(sd * 0.07 * h, 0.13 * h + k * 0.07 * h), R(sd * 0.13 * h, 0.1 * h + k * 0.07 * h)
                    canvas.drawLine(*a, *b, paint(zc, style='stroke', width=0.005 * h))
                    canvas.drawCircle(*b, 0.006 * h, paint(zc))
        if o.chevron and not back:
            cc_ = col(o.chevron)
            for k in range(2):
                for sd in (-1, 1):
                    a = R(sd * shw * 1.1, 0.0 + k * 0.05 * h)
                    b = R(tw + sd * 0.01 * h, 0.1 * h + k * 0.05 * h)
                    canvas.drawLine(*a, *b, paint(cc_, style='stroke', width=0.016 * h))
            canvas.drawLine(*R(tw, 0.0), *R(tw, 0.3 * h), paint((0.85, 0.85, 0.9, 0.9), style='stroke', width=0.005 * h))
        if o.buckles and not back:
            bc = col(o.buckles)
            for k, (y0, y1) in enumerate(((0.02, 0.12), (0.08, 0.18), (0.14, 0.24))):
                a, b = R(-shw * 1.1, y0 * h), R(shw * 1.1, y1 * h)
                canvas.drawLine(*a, *b, paint(col('#0a0a0c'), style='stroke', width=0.02 * h))
                mx_, my_ = (a[0] + b[0]) / 2 + (k - 1) * 0.04 * h, (a[1] + b[1]) / 2
                canvas.drawRect(skia.Rect.MakeXYWH(mx_ - 0.016 * h, my_ - 0.013 * h, 0.032 * h, 0.026 * h), paint(bc, style='stroke', width=0.005 * h))
            for sd in (-1, 1):
                canvas.drawCircle(*R(sd * 0.03 * h, 0.27 * h), 0.006 * h, paint(bc))
        if o.military and not back:
            gc = col(o.military)
            for k in range(5):
                y = 0.05 * h + k * 0.04 * h
                a, b = R(-waist * 0.95, y), R(waist * 0.95, y)
                canvas.drawLine(*a, *b, paint(gc, style='stroke', width=0.009 * h))
                for sx_ in (-1, 1):
                    canvas.drawCircle(*R(sx_ * waist * 0.98, y), 0.008 * h, paint(gc))
        canvas.restore()
        if o.military:
            for side in (-1, 1):
                ex_, ey_ = R(side * shw * 0.82, -0.012 * h)
                canvas.drawRoundRect(skia.Rect.MakeXYWH(ex_ - 0.04 * h, ey_ - 0.014 * h, 0.08 * h, 0.028 * h), 5, 5, paint(col(o.military)))
                for k in range(6):
                    fx_ = ex_ - 0.035 * h + k * 0.014 * h
                    canvas.drawLine(fx_, ey_ + 0.012 * h, fx_, ey_ + 0.03 * h, paint(col(o.military), style='stroke', width=0.004 * h))
        if o.fringe and not back:
            fl = paint(col(shade(o.vest, -0.1)), style='stroke', width=max(1.0, 0.005 * h))
            for k in range(15):
                u = -1 + 2 * k / 14
                x0, y0 = R(u * waist * 1.18, 0.30 * h)
                sw = P['fringe'] + 0.04 * math.sin(t * 9 + k)
                L_ = 0.06 * h
                canvas.drawLine(x0, y0, x0 + math.sin(sw) * L_, y0 + math.cos(sw) * L_, fl)
        # collar / neckline
        if not back:
            if o.turtleneck:
                tn = limb_outline([R(0, -0.03 * h), R(0, -0.075 * h)], [0.095 * h, 0.08 * h], False, False)
                cel(canvas, tn, sc, kd, -0.3, outline=line, ow=lw)
            else:
                cc = col(o.collar or o.shirt)
                vx = tw
                skin = col(self.d.skin)
                vneck = poly_path([R(-0.032 * h + vx, -0.036 * h), R(0.032 * h + vx, -0.036 * h), R(vx, 0.045 * h)])
                if o.bowtie:
                    canvas.drawPath(vneck, paint(col(o.collar)))
                    bx_, by_ = R(vx, -0.022 * h)
                    for sd in (-1, 1):
                        canvas.drawPath(poly_path([(bx_, by_), (bx_ + sd * 0.034 * h, by_ - 0.016 * h), (bx_ + sd * 0.034 * h, by_ + 0.016 * h)]),
                                        paint(col(o.bowtie)))
                    canvas.drawCircle(bx_, by_, 0.008 * h, paint(col(o.bowtie)))
                elif o.tie:
                    vneck = poly_path([R(-0.05 * h + vx, -0.04 * h), R(0.05 * h + vx, -0.04 * h), R(vx, 0.12 * h)])
                    canvas.drawPath(vneck, paint(col(o.collar)))
                    tie = poly_path([R(vx - 0.012 * h, -0.03 * h), R(vx + 0.012 * h, -0.03 * h), R(vx + 0.02 * h, 0.1 * h),
                                     R(vx, 0.125 * h), R(vx - 0.02 * h, 0.1 * h)])
                    cel(canvas, tie, col(o.tie), kd, -0.3, outline=line, ow=lw * 0.7)
                else:
                    canvas.drawPath(vneck, paint(col(o.under) if o.under else shade(skin, -0.25)))
                for side in (-1, 1):
                    wing = smooth_path([R(side * 0.012 * h + vx, -0.045 * h), R(side * 0.085 * h + vx, -0.03 * h),
                                        R(side * 0.115 * h + vx, 0.055 * h), R(side * 0.02 * h + vx, 0.03 * h)], True, 0.2)
                    cel(canvas, wing, cc, kd, -0.25, outline=line, ow=lw * 0.9)
        S['R'] = R

    def _neck_head(self, canvas, S, P, col, L, line, lw, back, t):
        d = self.d
        h = S['h']
        kd = L['key']
        skin = col(d.skin)
        hx, hy = S['head']
        r = S['hr']
        nk = S['neck']
        neck = limb_outline([(nk[0], nk[1] + 0.02 * h), (hx, hy + r * 0.55)], [0.06 * h, 0.055 * h], False, False)
        cel(canvas, neck, skin, kd, -0.35, outline=line, ow=lw)
        if back:
            self._afro(canvas, S, P, col, L)
            return
        yaw = P['hyaw']
        ht = S['ht']
        canvas.save()
        canvas.rotate(math.degrees(ht * 0.8), hx, hy)
        # ears
        for side in (-1, 1):
            ex = hx + side * r * d.face_w * (1.0 - 0.12 * side * yaw) + yaw * r * 0.05
            ear = ellipse_path(ex, hy + r * 0.08, r * 0.17, r * 0.25)
            cel(canvas, ear, skin, kd, -0.35, outline=line, ow=lw * 0.8)
            canvas.drawArc(skia.Rect.MakeXYWH(ex - r * 0.08, hy - r * 0.04, r * 0.16, r * 0.22), -60, 220, False,
                           paint(shade(skin, -0.4), style='stroke', width=lw * 0.8))
        # face shape
        fw = r * d.face_w
        j = d.jaw
        fx = yaw * r * 0.10
        pts = [(0, -1.02), (0.70, -0.82), (0.98, -0.25), (0.95, 0.22), (0.78 + 0.08 * j, 0.62), (0.42 + 0.05 * j, 0.93 + 0.06 * j),
               (0, 1.0 + 0.08 * j)]
        full = pts + [(-x, y) for (x, y) in pts[::-1][1:-1]]
        fp = [(hx + fx * (1 - abs(y)) * 0.5 + x * fw * (1 - 0.14 * yaw * (1 if x > 0 else -1)), hy + y * r) for x, y in full]
        face = smooth_path(fp, True, 0.5)
        cel(canvas, face, skin, kd, -0.3, outline=line, ow=lw, rim=alpha(L['rim'], 0.75), rim_w=r * 0.06, hi=0.35)
        # sideburns
        if d.sideburns:
            for side in (-1, 1):
                sbx = hx + side * fw * 0.93
                sb = smooth_path([(sbx, hy - r * 0.35), (sbx - side * r * 0.16, hy - r * 0.3), (sbx - side * r * 0.12, hy + r * 0.25),
                                  (sbx + side * r * 0.02, hy + r * 0.3)], True, 0.3)
                canvas.drawPath(sb, paint(col(d.hair_col)))
        cx = hx + yaw * r * 0.42
        # blush
        for side in (-1, 1):
            canvas.drawOval(skia.Rect.MakeXYWH(cx + side * r * 0.52 - r * 0.17, hy + r * 0.28, r * 0.34, r * 0.18),
                            paint(alpha(mix(skin, '#c0414a', 0.5), 0.22), blur=r * 0.07))
        self._eyes(canvas, S, P, cx, hx, hy, r, col, line, lw)
        # nose
        ny = hy + r * 0.40
        nw = r * 0.25 * d.nose_w
        canvas.drawOval(skia.Rect.MakeXYWH(cx - nw * 0.9, ny - r * 0.05, nw * 1.8, r * 0.17),
                        paint(alpha(shade(skin, -0.45), 0.55), blur=r * 0.04))
        for side in (-1, 1):
            canvas.drawArc(skia.Rect.MakeXYWH(cx + side * nw * 0.55 - r * 0.07, ny - r * 0.02, r * 0.14, r * 0.12),
                           200 if side < 0 else -20, 140 * side, False,
                           paint(shade(skin, -0.55), style='stroke', width=lw * 0.9))
        canvas.drawCircle(cx + nw * 0.15, ny - r * 0.06, r * 0.04, paint(alpha(shade(skin, 0.45), 0.7), blur=r * 0.02))
        self._mouth(canvas, P, cx, hy, r, skin, col, lw)
        if P.get('sweat', 0) > 0.05:
            a_ = P['sweat']
            for k, (sx_, sy_) in enumerate(((0.62, -0.42), (-0.7, -0.1), (0.75, 0.12))):
                yy = hy + sy_ * r + ((t * 0.35 + k * 0.37) % 1.0) * r * 0.25
                xx = cx + sx_ * r
                drop = smooth_path([(xx, yy - r * 0.09), (xx + r * 0.045, yy), (xx, yy + r * 0.04), (xx - r * 0.045, yy)], True, 0.5)
                canvas.drawPath(drop, paint((0.85, 0.93, 1.0, 0.75 * a_)))
                canvas.drawCircle(xx - r * 0.012, yy - r * 0.01, r * 0.012, paint((1, 1, 1, 0.9 * a_)))
        if d.beard > 0:
            bp_ = smooth_path([(cx - r * 0.62, hy + r * 0.45), (cx - r * 0.45, hy + r * 0.95), (cx, hy + r * 1.1),
                               (cx + r * 0.45, hy + r * 0.95), (cx + r * 0.62, hy + r * 0.45), (cx + r * 0.35, hy + r * 0.8),
                               (cx, hy + r * 0.86), (cx - r * 0.35, hy + r * 0.8)], True, 0.4)
            canvas.drawPath(bp_, paint(alpha(col(d.hair_col), 0.7 * d.beard)))
        if d.glasses:
            gyy = hy + r * 0.05
            for side in (-1, 1):
                gxx = cx + side * r * d.eye_sp * (1 - 0.22 * yaw * side)
                gw, gh = r * 0.27 * (1 - 0.2 * max(0, yaw * side)), r * 0.24
                rr_ = skia.Rect.MakeLTRB(gxx - gw, gyy - gh, gxx + gw, gyy + gh * 1.05)
                canvas.drawRoundRect(rr_, gh * 0.55, gh * 0.55, paint((0.75, 0.6, 0.45, 0.16)))
                canvas.drawRoundRect(rr_, gh * 0.55, gh * 0.55, paint(col(d.glasses), style='stroke', width=lw * 1.4))
                canvas.drawLine(gxx - gw * 0.5, gyy - gh * 0.6, gxx - gw * 0.1, gyy - gh * 0.75, paint((1, 1, 1, 0.5), style='stroke', width=lw))
            bx0 = cx - r * d.eye_sp + r * 0.27
            canvas.drawLine(bx0, gyy - r * 0.05, cx + r * d.eye_sp - r * 0.27, gyy - r * 0.05, paint(col(d.glasses), style='stroke', width=lw * 1.2))
        if d.mustache > 0:
            mp = smooth_path([(cx - r * 0.26, hy + r * 0.64), (cx, hy + r * 0.56), (cx + r * 0.26, hy + r * 0.64),
                              (cx, hy + r * 0.62)], True, 0.4)
            canvas.drawPath(mp, paint(alpha(col(d.hair_col), 0.75 * d.mustache)))
        canvas.restore()
        # hair (behind already drawn) -> front hairline over forehead
        canvas.save()
        canvas.rotate(math.degrees(ht * 0.8), hx, hy)
        hl = smooth_path([(hx - fw * 1.02, hy - r * 0.05), (hx - fw * 0.75, hy - r * 0.48),
                          (cx - r * 0.25, hy - r * 0.62), (cx + r * 0.25, hy - r * 0.62),
                          (hx + fw * 0.75, hy - r * 0.48), (hx + fw * 1.02, hy - r * 0.05),
                          (hx + fw * 1.3, hy - r * 1.4), (hx - fw * 1.3, hy - r * 1.4)], True, 0.35)
        canvas.restore()
        canvas.save()
        canvas.clipPath(hl, doAntiAlias=True)
        self._afro(canvas, S, P, col, L)
        canvas.restore()

    def _eyes(self, canvas, S, P, cx, hx, hy, r, col, line, lw):
        d = self.d
        ey = hy + r * 0.04
        fear = P.get('fear', 0.0)
        er = r * 0.2 * d.eye * (1 + 0.16 * fear)
        blink = P['blink'] * (1 - fear)
        yaw = P['hyaw']
        for side in (-1, 1):
            ex = cx + side * r * d.eye_sp * (1 - 0.22 * yaw * side)
            sx = er * (1 - 0.25 * max(0, yaw * side))
            sy = er * 0.78 * max(0.06, 1 - blink)
            if blink > 0.85:
                canvas.drawArc(skia.Rect.MakeXYWH(ex - sx, ey - er * 0.3, 2 * sx, er * 0.6), 10, 160, False,
                               paint(line, style='stroke', width=lw * 1.6))
                continue
            alm = smooth_path([(ex - sx, ey + sy * 0.12), (ex - sx * 0.45, ey - sy * 0.95), (ex + sx * 0.4, ey - sy),
                               (ex + sx, ey - sy * 0.05), (ex + sx * 0.35, ey + sy * 0.85), (ex - sx * 0.4, ey + sy * 0.8)],
                              True, 0.5)
            canvas.drawPath(alm, paint('#f3ebe2'))
            canvas.save()
            canvas.clipPath(alm, doAntiAlias=True)
            ir = er * 0.62 * (1 - 0.28 * fear)
            ix = ex + P['ex'] * sx * 0.38
            iy = ey + P['ey'] * sy * 0.3 + sy * 0.05
            canvas.drawCircle(ix, iy, ir, shader_paint(rad_grad((ix, iy + ir * 0.3), ir, ['#7a4a28', '#4a2a16', '#2a160c'],
                                                               [0, 0.6, 1])))
            canvas.drawCircle(ix, iy, ir * 0.48, paint('#0e0806'))
            canvas.drawRect(skia.Rect.MakeXYWH(ex - sx, ey - sy * 1.2, 2 * sx, sy * 0.55), paint((0.2, 0.1, 0.1, 0.22), blur=sy * 0.2))
            canvas.drawCircle(ix - ir * 0.33, iy - ir * 0.38, ir * 0.3, paint('#ffffff'))
            canvas.drawCircle(ix + ir * 0.35, iy + ir * 0.35, ir * 0.13, paint((1, 1, 1, 0.8)))
            canvas.restore()
            # upper lid (thick) + lash flick
            lid = skia.Path()
            lid.moveTo(ex - sx * 1.05, ey + sy * 0.1)
            lid.cubicTo(ex - sx * 0.5, ey - sy * 1.15, ex + sx * 0.45, ey - sy * 1.15, ex + sx * 1.05, ey - sy * 0.05)
            canvas.drawPath(lid, paint('#1a0e0c', style='stroke', width=lw * 1.45))
            fl = ex + side * sx * 1.05
            canvas.drawLine(fl, ey - sy * 0.02, fl + side * sx * 0.1, ey - sy * 0.18,
                            paint('#1a0e0c', style='stroke', width=lw * 0.9))
            canvas.drawArc(skia.Rect.MakeXYWH(ex - sx * 0.85, ey - sy * 1.7, sx * 1.7, sy * 1.2), 200, 140, False,
                           paint(alpha(shade(col(d.skin), -0.45), 0.6), style='stroke', width=lw * 0.8))
        # brows
        by = hy - r * 0.30 - P['brow'] * r * 0.09
        for side in (-1, 1):
            bx = cx + side * r * d.eye_sp * (1 - 0.2 * yaw * side)
            bw = r * 0.24
            inner = by + (0.03 - 0.06 * P['brow']) * r
            b = limb_outline([(bx - side * bw * 1.0, inner), (bx, by - r * 0.05), (bx + side * bw, by + r * 0.01)],
                             [r * 0.07 * d.brow_w, r * 0.08 * d.brow_w, r * 0.035 * d.brow_w])
            canvas.drawPath(b, paint(col(d.hair_col if d.hair_col != '#7a726c' else '#3a3430')))

    def _mouth(self, canvas, P, cx, hy, r, skin, col, lw):
        smile = min(1.0, P['smile'] + self.d.smile_bias * 0.3)
        op = P['mopen']
        my = hy + r * 0.66
        mw = r * (0.25 + 0.06 * smile) * (0.75 if P['mshape'] == 'o' else 1.0)
        lipc = col(self.d.lip)
        if op < 0.06:
            p = skia.Path()
            p.moveTo(cx - mw, my - smile * r * 0.06)
            p.quadTo(cx, my + smile * r * 0.12, cx + mw, my - smile * r * 0.06)
            canvas.drawPath(p, paint(shade(lipc, -0.4), style='stroke', width=lw * 1.4))
            canvas.drawOval(skia.Rect.MakeXYWH(cx - mw * 0.5, my + r * 0.07, mw, r * 0.07),
                            paint(alpha(shade(skin, 0.3), 0.5), blur=r * 0.02))
            for side in (-1, 1):
                canvas.drawCircle(cx + side * mw * 1.02, my - smile * r * 0.06, r * 0.018, paint(alpha(shade(skin, -0.5), 0.6)))
            return
        hgt = op * r * (0.42 if P['mshape'] in ('o', 'ah') else 0.3)
        top = my - r * 0.03 - smile * r * 0.03
        mp = skia.Path()
        if P['mshape'] == 'o':
            mp.addOval(skia.Rect.MakeXYWH(cx - mw * 0.7, top - hgt * 0.1, mw * 1.4, hgt * 1.15))
        else:
            mp.moveTo(cx - mw, top - smile * r * 0.04)
            mp.cubicTo(cx - mw * 0.4, top + r * 0.015, cx + mw * 0.4, top + r * 0.015, cx + mw, top - smile * r * 0.04)
            mp.cubicTo(cx + mw * 0.75, top + hgt * 0.9, cx - mw * 0.75, top + hgt * 0.9, cx - mw, top - smile * r * 0.04)
            mp.close()
        canvas.drawPath(mp, paint(lipc))
        inner = skia.Path(mp)
        m = skia.Matrix()
        m.setScale(0.88, 0.82, cx, top + hgt * 0.35)
        inner.transform(m)
        canvas.drawPath(inner, paint('#3b1214'))
        canvas.save()
        canvas.clipPath(inner, doAntiAlias=True)
        if P['mshape'] in ('grin', 'ah', 'smile'):
            canvas.drawRect(skia.Rect.MakeXYWH(cx - mw, top - r * 0.05, 2 * mw, r * 0.09 + hgt * 0.05), paint('#f4eee6'))
        canvas.drawOval(skia.Rect.MakeXYWH(cx - mw * 0.55, top + hgt * 0.55, mw * 1.1, hgt * 0.6), paint('#b9545a'))
        canvas.restore()

    def _arm(self, canvas, S, side, P, o, col, L, line, lw):
        h = S['h']
        kd = L['key']
        sh, el, wr, fa = S['arms'][side]
        sc = col(o.shirt)
        sleeve = limb_outline([sh, el, wr], [0.068 * h, 0.06 * h, 0.056 * h])
        cel(canvas, sleeve, sc, kd, -0.33, outline=line, ow=lw)
        if o.jumpsuit and o.stripes:
            canvas.drawPath(limb_outline([sh, el, wr], [0.012 * h] * 3, False, False), paint(col(o.stripes)))
        if o.buckles:
            for k in range(2):
                u_ = 0.3 + k * 0.45
                p0 = (sh[0] + (el[0] - sh[0]) * u_, sh[1] + (el[1] - sh[1]) * u_) if k == 0 else (el[0] + (wr[0] - el[0]) * 0.5, el[1] + (wr[1] - el[1]) * 0.5)
                canvas.drawLine(p0[0] - 0.034 * h, p0[1], p0[0] + 0.034 * h, p0[1] + 0.006 * h, paint('#0a0a0c', style='stroke', width=0.014 * h))
                canvas.drawRect(skia.Rect.MakeXYWH(p0[0] - 0.01 * h, p0[1] - 0.008 * h, 0.02 * h, 0.018 * h), paint(col(o.buckles), style='stroke', width=0.004 * h))
        if o.zips:
            for k in range(3):
                u_ = 0.2 + k * 0.12
                px_, py_ = sh[0] + (el[0] - sh[0]) * u_, sh[1] + (el[1] - sh[1]) * u_
                canvas.drawLine(px_ - 0.03 * h, py_, px_ + 0.03 * h, py_ + 0.004 * h, paint(alpha(shade(col(o.shirt), -0.45), 0.8), style='stroke', width=0.004 * h))
            canvas.drawLine(el[0], el[1], el[0] + (wr[0] - el[0]) * 0.7, el[1] + (wr[1] - el[1]) * 0.7,
                            paint((0.86, 0.86, 0.9, 0.9), style='stroke', width=0.005 * h))
        # cuff
        dx, dy = wr[0] - el[0], wr[1] - el[1]
        Ln = math.hypot(dx, dy) + 1e-9
        ux, uy = dx / Ln, dy / Ln
        cuff = limb_outline([(wr[0] - ux * 0.012 * h, wr[1] - uy * 0.012 * h), (wr[0] + ux * 0.004 * h, wr[1] + uy * 0.004 * h)],
                            [0.062 * h, 0.064 * h], False, False)
        cel(canvas, cuff, col(o.collar or o.shirt), kd, -0.25, outline=line, ow=lw * 0.8)
        gloved = o.glove == side
        self._hand(canvas, wr, (ux, uy), P['lhand' if side < 0 else 'rhand'], h,
                   col('#f2f2f8') if gloved else col(self.d.skin), kd, line, lw, side)
        if gloved:
            for k in range(7):
                tw_ = 0.5 + 0.5 * math.sin(P.get('_t', 0) * 9 + k * 2.1)
                gx_ = wr[0] + ux * (0.02 + 0.012 * k) * h + math.sin(k * 3) * 0.012 * h
                gy_ = wr[1] + uy * (0.02 + 0.012 * k) * h + math.cos(k * 3) * 0.012 * h
                canvas.drawCircle(gx_, gy_, 0.004 * h * (0.6 + tw_), paint((1, 1, 1, 0.9)))
                if k % 3 == 0:
                    glow(canvas, gx_, gy_, 0.03 * h * tw_, '#ffffff', 0.5)
        if P.get('mic') == side:
            mx, my = wr[0] + ux * 0.05 * h - side * uy * 0.0, wr[1] + uy * 0.05 * h
            canvas.drawLine(mx, my, mx + ux * 0.075 * h, my + uy * 0.075 * h, paint('#1a1a1e', style='stroke', width=0.022 * h))
            gx_, gy_ = mx + ux * 0.09 * h, my + uy * 0.09 * h
            canvas.drawCircle(gx_, gy_, 0.026 * h, shader_paint(rad_grad((gx_ - 0.008 * h, gy_ - 0.008 * h), 0.03 * h,
                                                                         ['#e8e8ee', '#8a8a96', '#2a2a30'])))

    def _hand(self, canvas, wr, u, shape, h, skin, kd, line, lw, side):
        ux, uy = u
        vx, vy = -uy * side, ux * side      # across the palm, thumb side toward body centre
        s = 0.052 * h
        def P_(a, b):
            return (wr[0] + ux * a * s + vx * b * s, wr[1] + uy * a * s + vy * b * s)
        palm = smooth_path([P_(0.05, -0.42), P_(0.75, -0.48), P_(0.95, 0.0), P_(0.75, 0.45), P_(0.1, 0.42)], True, 0.5)
        fingers = []
        if shape in ('open', 'relaxed', 'mic'):
            spread = 0.22 if shape == 'open' else 0.08
            curl = 0.55 if shape == 'relaxed' else (0.9 if shape == 'mic' else 1.0)
            for k, off in enumerate((-0.33, -0.11, 0.11, 0.33)):
                ln = [0.78, 0.9, 0.86, 0.68][k] * curl
                a = off * spread * 3
                fingers.append(([P_(0.8, off * 0.95), P_(0.8 + ln * math.cos(a), off * 0.95 + ln * math.sin(a))], 0.19))
            th = ([P_(0.25, 0.42), P_(0.55, 0.78 if shape == 'open' else 0.62)], 0.21)
        elif shape == 'point':
            fingers.append(([P_(0.8, -0.3), P_(1.85, -0.36)], 0.19))
            for off in (-0.08, 0.14, 0.33):
                fingers.append(([P_(0.8, off), P_(1.0, off)], 0.2))
            th = ([P_(0.3, 0.42), P_(0.75, 0.3)], 0.21)
        else:  # fist / snap
            for off in (-0.3, -0.1, 0.1, 0.3):
                fingers.append(([P_(0.8, off), P_(1.0, off)], 0.21))
            th = ([P_(0.3, 0.42), P_(0.85, 0.15 if shape == 'snap' else 0.25)], 0.22)
        for pts, w in fingers + [th]:
            f = limb_outline(pts, [w * s, w * s * 0.9])
            cel(canvas, f, skin, kd, -0.3, outline=line, ow=lw * 0.7)
        cel(canvas, palm, skin, kd, -0.3, outline=line, ow=lw * 0.8)
        for pts, w in fingers[:1] if shape == 'point' else []:
            pass

    def _inst_geom(self, S, P):
        h = S['h']
        lean = P['lean']
        ch = S['chest']
        ca, sa = math.cos(lean), math.sin(lean)
        cx = ch[0] + (-0.04 * h) * ca - (0.215 * h) * sa
        cy = ch[1] + (-0.04 * h) * sa + (0.215 * h) * ca
        ang = -24 + math.degrees(lean) * 0.8
        neck_len = {'guitar': 0.31 * h, 'strat': 0.30 * h}.get(P['instrument'], 0.40 * h)
        rad = math.radians(ang)
        ux, uy = math.cos(rad), math.sin(rad)
        S['inst'] = (cx, cy, ang, neck_len)
        f = 0.05 * h + neck_len * 0.72
        S['fret_pt'] = (cx + ux * f + uy * 0.03 * h, cy + uy * f - ux * 0.03 * h + 0.012 * h)
        st = P.get('strum', 0.0)
        S['strum_pt'] = (cx + 0.02 * h - uy * 0.0, cy - 0.02 * h + st * 0.05 * h)

    def _instrument(self, canvas, S, P, col, L, line, lw, t):
        h = S['h']
        kind = P['instrument']
        cx, cy, ang, neck_len = S['inst']
        a = S['rsh']
        canvas.drawLine(a[0] - 0.01 * h, a[1] + 0.005 * h, cx - 0.09 * h, cy + 0.03 * h,
                        paint(col('#2a1a12'), style='stroke', width=0.016 * h))
        canvas.save()
        canvas.translate(cx, cy)
        canvas.rotate(ang)
        if kind == 'strat':        # red double-cutaway, white/black tape stripes (early-80s rock)
            body = smooth_path([(0.06 * h, -0.07 * h), (0.0, -0.06 * h), (-0.05 * h, -0.085 * h), (-0.11 * h, -0.07 * h),
                                (-0.12 * h, 0.0), (-0.13 * h, 0.07 * h), (-0.07 * h, 0.1 * h), (0.0, 0.07 * h), (0.07 * h, 0.075 * h),
                                (0.03 * h, 0.03 * h), (0.03 * h, -0.03 * h)], True, 0.45)
            canvas.drawPath(body, shader_paint(rad_grad((-0.05 * h, -0.01 * h), 0.14 * h, [col('#ff3a2a'), col('#c4141a'), col('#5a0608')], [0, 0.6, 1])))
            canvas.save()
            canvas.clipPath(body, doAntiAlias=True)
            for k, (o_, a_, cc) in enumerate(((-0.1, 35, '#f4f0ea'), (-0.06, -30, '#141214'), (-0.02, 55, '#f4f0ea'),
                                              (0.02, -50, '#141214'), (-0.08, 80, '#f4f0ea'), (0.03, 15, '#f4f0ea'))):
                canvas.save()
                canvas.translate(o_ * h, 0.0)
                canvas.rotate(a_)
                canvas.drawRect(skia.Rect.MakeXYWH(-0.3 * h, -0.006 * h, 0.6 * h, 0.012 * h), paint(col(cc)))
                canvas.restore()
            canvas.restore()
            canvas.drawPath(body, paint(line, style='stroke', width=lw))
            canvas.drawRect(skia.Rect.MakeXYWH(-0.075 * h, -0.025 * h, 0.014 * h, 0.05 * h), paint('#e8e4dc'))
            canvas.drawCircle(-0.1 * h, 0.05 * h, 0.009 * h, paint('#e8e4dc'))
        elif kind == 'guitar':
            body = smooth_path([(0.02 * h, -0.075 * h), (-0.06 * h, -0.095 * h), (-0.11 * h, -0.07 * h), (-0.105 * h, 0.0),
                                (-0.13 * h, 0.075 * h), (-0.06 * h, 0.115 * h), (0.03 * h, 0.09 * h), (0.05 * h, 0.0)],
                               True, 0.5)
            canvas.drawPath(body, shader_paint(rad_grad((-0.04 * h, 0.01 * h), 0.13 * h,
                                                        [col('#f0a23a'), col('#b2501a'), col('#3a140a')], [0, 0.55, 1])))
            canvas.drawPath(body, paint(line, style='stroke', width=lw))
            for fx_ in (-0.095, -0.022):
                canvas.drawOval(skia.Rect.MakeXYWH(fx_ * h, -0.035 * h, 0.012 * h, 0.06 * h), paint('#1a0a06'))
            canvas.drawRect(skia.Rect.MakeXYWH(-0.07 * h, -0.02 * h, 0.012 * h, 0.04 * h), paint('#d8d0c0'))
        else:
            body = smooth_path([(0.03 * h, -0.06 * h), (-0.05 * h, -0.1 * h), (-0.09 * h, -0.05 * h), (-0.08 * h, 0.01 * h),
                                (-0.12 * h, 0.08 * h), (-0.05 * h, 0.11 * h), (0.04 * h, 0.08 * h), (0.06 * h, 0.0)], True, 0.5)
            cel(canvas, body, col('#e9e2d0'), (0, -1), -0.25, outline=line, ow=lw, hi=0.6)
            canvas.drawPath(smooth_path([(0.0, -0.04 * h), (-0.05 * h, -0.05 * h), (-0.07 * h, 0.04 * h), (0.0, 0.05 * h)], True, 0.4),
                            paint(col('#1c1414')))
        nk = poly_path([(0.04 * h, -0.012 * h), (0.04 * h + neck_len, -0.009 * h), (0.04 * h + neck_len, 0.009 * h),
                        (0.04 * h, 0.012 * h)])
        canvas.drawPath(nk, paint(col('#3a2416')))
        canvas.drawRoundRect(skia.Rect.MakeXYWH(0.04 * h + neck_len - 0.005 * h, -0.018 * h, 0.055 * h, 0.036 * h), 4, 4,
                             paint(col('#2a180e')))
        for k in range(4):
            yy = -0.007 * h + k * 0.0047 * h
            canvas.drawLine(-0.07 * h, yy, 0.04 * h + neck_len, yy, paint((0.95, 0.9, 0.8, 0.55), style='stroke', width=0.8))
        canvas.restore()

    def _hat(self, canvas, S, P, o, col, L, line, lw):
        hx, hy = S['head']
        r = S['hr']
        canvas.save()
        canvas.rotate(math.degrees(S['ht'] * 0.8 - 0.12), hx, hy)
        top = hy - r * (1.35 if self.d.hair == 'afro' else 0.95)
        brim = ellipse_path(hx, top + r * 0.35, r * 1.55, r * 0.22)
        crown = smooth_path([(hx - r * 0.95, top + r * 0.35), (hx - r * 0.85, top - r * 0.45), (hx, top - r * 0.62),
                             (hx + r * 0.85, top - r * 0.45), (hx + r * 0.95, top + r * 0.35)], False, 0.4)
        crown.close()
        cel(canvas, brim, col(o.hat), L['key'], -0.35, outline=line, ow=lw)
        cel(canvas, crown, col(o.hat), L['key'], -0.35, outline=line, ow=lw, hi=0.4)
        canvas.drawRect(skia.Rect.MakeLTRB(hx - r * 0.93, top + r * 0.12, hx + r * 0.93, top + r * 0.3), paint(col('#1a0e14')))
        canvas.restore()


def heights(base_px):
    return {k: BROTHERS[k].height * base_px for k in BROTHERS}
