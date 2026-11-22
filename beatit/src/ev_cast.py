"""EVOLUTION edit cast: Michael across 1968-2009 (one face, aging + era hair/costume), zombies, new beat-locked moves."""
import math
import _paths  # noqa: F401
import numpy as np
from character import Design, Outfit, DESIGNS, Character, MICHAEL_OUTFITS, outfits, JOE_OUTFIT
from gfx import clamp, ease_io, ease_out, back_out
import world
import choreo
import bi_cast as K   # registers Quincy/Eddie/extras/fans

D84 = DESIGNS['michael84']
def adult(name, skin, hair, afro, hair_cy, bump, nose, face_w, jaw, seed, hair_col='#140c0a', eye=1.05):
    return Design('Michael', 1.62, 0.072, skin, afro, face_w=face_w, jaw=jaw, eye=eye, eye_sp=0.34, brow_w=0.78, nose_w=nose,
                  lip='#8a4a46' if skin < '#c' else '#a8605a', shoulders=0.205, leg=0.51, seed=seed, sig='#6b2fa0',
                  hair=hair, hair_cy=hair_cy, bump=bump, hair_col=hair_col)

NEW = {
    'michael87': adult('m87', '#b07d5c', 'longcurl', (1.32, 1.05), -0.05, 0.6, 0.66, 0.79, 0.62, 59),
    'michael92': adult('m92', '#d0a688', 'longcurl', (1.26, 1.1), -0.02, 0.5, 0.6, 0.78, 0.6, 60),
    'michael09': adult('m09', '#e3c5ad', 'shag', (1.16, 1.02), 0.12, 0.3, 0.56, 0.74, 0.55, 61),
}
ZSKIN = ['#8a9a7a', '#7a8a6e', '#9aa488', '#6e7e66', '#8e9682', '#7c8c70']
for i in range(6):
    NEW[f'z{i}'] = Design('Zombie', 1.55 + 0.03 * (i % 3), 0.073, ZSKIN[i], [(1.1, 1.0), (1.3, 1.2), (1.08, 1.0)][i % 3],
                          face_w=0.84 + 0.03 * (i % 2), jaw=0.8, eye=0.8, brow_w=1.3, nose_w=1.0, lip='#4a4a3a',
                          shoulders=0.24, leg=0.49, seed=500 + i, hair=['short', 'afro', 'short'][i % 3],
                          hair_cy=[0.12, 0.25, 0.12][i % 3], bump=0.6, hair_col='#2a2a22')
DESIGNS.update(NEW)
world.CHARS.update({k: Character(k) for k in NEW})

KID, M79, M83, M87, M92, M09 = 'michael', 'michael79', 'michael84', 'michael87', 'michael92', 'michael09'
O_KID_HOME = outfits('home')
O_KID_TV = outfits('tv')
O_OTW = MICHAEL_OUTFITS['michael79']                                    # Off the Wall: tuxedo, white socks
O_THRILLER = Outfit(shirt='#c0121c', pants='#b0101a', collar='#c0121c', chevron='#141216', under='#141216', flare=False,
                    socks='#f4f4f8', shoes='#0c0c10')
O_MOTOWN = Outfit(shirt='#121016', pants='#121016', collar='#1c1a22', sparkle=True, flare=False, glove=1, socks='#f4f4f8',
                  shoes='#0c0c10', hat='#101014')
O_MOTOWN_NOHAT = Outfit(**{**O_MOTOWN.__dict__, 'hat': None})
O_BEATIT = K.O_BEATIT
O_BAD = Outfit(shirt='#141416', pants='#141416', collar='#1e1e22', buckles='#c8c8d2', flare=False, shoes='#0c0c10',
               glove=0, belt='#2a2a30')
O_SC = Outfit(shirt='#f2f0ea', pants='#f2f0ea', collar='#3a5a9a', tie='#f2f0ea', hat='#f2f0ea', flare=False, socks='#f4f4f8',
              shoes='#f0eee8')
O_SC_NOHAT = Outfit(**{**O_SC.__dict__, 'hat': None})
O_DANGEROUS = Outfit(shirt='#d8a83a', pants='#141216', collar='#f4d06a', military='#fff0c0', sparkle=True, flare=False,
                     belt='#c8c8d0', shoes='#0c0c10', socks='#f4f4f8')
O_HISTORY = Outfit(shirt='#141216', pants='#141216', collar='#1e1c22', military='#c8c8d0', flare=False, belt='#c8c8d0',
                   shoes='#0c0c10')
O_TII = Outfit(shirt='#9a9aa6', pants='#121014', collar='#c8c8d2', sparkle=True, flare=False, shoes='#0c0c10', under='#121014')
O_ZOMBIE = [Outfit(shirt=s, pants=p, collar=s, stripes=st, flare=False) for s, p, st in
            (('#5a5a46', '#3a3a30', '#4a4a3a'), ('#6a5a4a', '#2a2a2a', '#5a4a3a'), ('#4a5a5a', '#3a3a3a', '#3a4a4a'),
             ('#7a6a5a', '#30302a', '#6a5a4a'), ('#4a4a52', '#2a2a30', '#3a3a42'), ('#5a4a3a', '#3a3a30', '#4a3a2a'))]
JOE = 'joe'
O_JOE = JOE_OUTFIT

L_TV = dict(key=(-0.3, -0.9), amb='#ffe0b0', amb_a=0.15, rim='#fff0d0', line='#2a1410', floor_shadow=0.4)
L_DISCO = dict(key=(-0.2, -0.95), amb='#ff9ad8', amb_a=0.2, rim='#ffe8ff', line='#1a0a1a', floor_shadow=0.45)
L_MOON = dict(key=(0.5, -0.8), amb='#5a7aa8', amb_a=0.35, rim='#c8e0ff', line='#0a0c14', floor_shadow=0.5)
L_SPOT = dict(key=(0.0, -1.0), amb='#3a4a8a', amb_a=0.25, rim='#ffffff', line='#0c0a14', floor_shadow=0.5)
L_SUBWAY = dict(key=(-0.3, -0.9), amb='#a8c0a0', amb_a=0.25, rim='#e0ffe0', line='#0c120c', floor_shadow=0.5)
L_STADIUM = dict(key=(-0.2, -0.98), amb='#e0e8ff', amb_a=0.15, rim='#ffffff', line='#141020', floor_shadow=0.45)
L_GOLD = dict(key=(-0.2, -0.98), amb='#ffd890', amb_a=0.2, rim='#fff4d0', line='#1a1008', floor_shadow=0.45)
L_ZOMBIE = dict(key=(0.5, -0.8), amb='#6a8a7a', amb_a=0.45, rim='#b8ffd8', line='#0a100c', floor_shadow=0.5)


# ----------------------------------------------------------------------------- moves
def moonwalk_steps(B, start=0.0, dirn=-1, stride=0.075):
    """true moonwalk mechanics (pose units): one foot on its toe stays planted while the other, flat, glides past it;
    heel-drop swaps the roles on every beat; the body travels backward at a constant speed.
    returns body_x, (front/back foot world x), toe flags, heel-drop amount"""
    u = max(0.0, B - start)
    k = int(math.floor(u))
    f = u - k
    T_k = dirn * stride * k
    toe_foot = k % 2                    # 0 = left foot is the planted toe foot this beat, 1 = right
    glide = (f - 0.08) / 0.84
    glide = clamp(glide)
    flat_x = T_k - dirn * stride + 2 * dirn * stride * glide
    body = T_k + dirn * stride * (f - 0.5)
    heel = 1 - clamp(f / 0.12)          # heel-drop transition at the start of the beat
    return body, toe_foot, T_k, flat_x, heel


def moonwalk2(B, P, start=0.0, dirn=-1, stride=0.075, spread=0.02):
    body, toe_foot, xt, xf, heel = moonwalk_steps(B, start, dirn, stride)
    P['x'] = body
    lx, rx = (xt, xf) if toe_foot == 0 else (xf, xt)
    P['lfx'] = lx - body - spread
    P['rfx'] = rx - body + spread
    up = 0.028 * (1 - heel * 0.6)      # the toe foot's heel is up (ankle raised); the gliding foot stays flat
    P['lfy'] = -up if toe_foot == 0 else -0.004 * heel
    P['rfy'] = -up if toe_foot == 1 else -0.004 * heel
    P['hip'] = 0.012 * (1 if toe_foot == 1 else -1) * dirn * 0.5         # weight over the planted leg
    P['dip'] = 0.028 + 0.008 * heel
    P['lean'] = 0.05 * dirn
    P['hyaw'] = -0.35 * dirn
    P['tw'] = -0.35 * dirn
    P['lsh'], P['lel'] = 0.32, 0.55
    P['rsh'], P['rel'] = 0.3, -0.9
    P['lhand'], P['rhand'] = 'relaxed', 'fist'
    P['brow'] = -0.25
    P['smile'] = 0.15


def zombie(B, P, amp=1.0, start=0.0):
    """Thriller-inspired: claw hands raised at the sides, a stiff lateral shuffle, jerky head tilts, shoulder shrugs"""
    f = B % 1
    n = int(math.floor(B))
    d = 1 if n % 2 == 0 else -1
    step = ease_io(clamp(f / 0.5))
    P['x'] = 0.035 * amp * (d * (2 * step - 1))
    P['lfx'], P['rfx'] = -0.09, 0.09
    P['lfy'] = -0.03 * math.sin(math.pi * clamp(f / 0.45)) * (d > 0)
    P['rfy'] = -0.03 * math.sin(math.pi * clamp(f / 0.45)) * (d < 0)
    jerk = 1 if f < 0.18 else 0
    P['lsh'], P['lel'] = 1.25 + 0.15 * d, 1.35
    P['rsh'], P['rel'] = 1.25 - 0.15 * d, 1.35
    P['lhand'] = P['rhand'] = 'open'
    P['htilt'] = 0.18 * d * (0.6 + 0.4 * jerk)
    P['dip'] = 0.04 + 0.015 * (1 - step)
    P['lean'] = -0.04 * d
    P['tw'] = 0.2 * d
    P['brow'] = -0.7
    P['smile'] = -0.2
    P['mopen'] = 0.25
    P['mshape'] = 'ah'


def head_snap(B, P, start=0.0, side=1):
    u = clamp((B - start) / 0.18)
    choreo.groove(B, P, 0.4, snap=False, arms=False)
    P['hyaw'] = side * 0.55 * back_out(u, 2.0)
    P['ex'] = side * 0.9 * u
    P['htilt'] = -0.08 * side * u
    P['brow'] = -0.6
    P['smile'] = 0.1
    P['lsh'], P['lel'] = 0.5, -1.6
    P['rsh'], P['rel'] = 0.5, -1.6
    P['lhand'] = P['rhand'] = 'fist'


def claw_pose(B, P, start=0.0):
    """the group pose: weight low, both claws thrown forward/up on the accent"""
    u = back_out(clamp((B - start) / 0.25), 1.8)
    P['dip'] = 0.06 * u
    P['lfx'], P['rfx'] = -0.12, 0.12
    P['lsh'], P['lel'] = 0.6 + 1.3 * u, 0.9
    P['rsh'], P['rel'] = 0.6 + 1.3 * u, 0.9
    P['lhand'] = P['rhand'] = 'open'
    P['htilt'] = -0.1 * u
    P['lean'] = 0.02
    P['brow'] = -0.7
    P['ey'] = -0.4


def lean_pose(B, P):
    """rigid body, feet together, arms down - used inside the anti-gravity lean (the canvas pivots at the ankles)"""
    P['lfx'], P['rfx'] = -0.03, 0.03
    P['lfy'] = P['rfy'] = 0.0
    P['lsh'] = P['rsh'] = 0.12
    P['lel'] = P['rel'] = 0.1
    P['lhand'] = P['rhand'] = 'relaxed'
    P['dip'] = 0.0
    P['lean'] = 0.0
    P['brow'] = -0.3
    P['smile'] = 0.1


def hat_tip(B, P, start=0.0):
    """right hand to the hat brim, chin down"""
    u = ease_io(clamp((B - start) / 0.5))
    P['rsh'], P['rel'] = 0.4 + 0.85 * u, 0.2 + 2.25 * u
    P['rhand'] = 'open'
    P['lsh'], P['lel'] = 0.2, 0.3
    P['hnod'] = 0.012 * u
    P['ey'] = -0.5 * u
    P['brow'] = -0.4
    P['smile'] = 0.15


for name, fn in dict(moonwalk2=moonwalk2, zombie=zombie, head_snap=head_snap, claw_pose=claw_pose, lean_pose=lean_pose,
                     hat_tip=hat_tip).items():
    choreo.MOVES[name] = fn
