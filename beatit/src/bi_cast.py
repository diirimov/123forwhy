"""Beat It episode cast: Michael 1982-83 (same adult design as the V3 finale), Quincy Jones, Eddie Van Halen,
dancers, the two street groups, the film crew and fans. All registered into the shared engine."""
import _paths  # noqa: F401
import numpy as np
from character import Design, Outfit, DESIGNS, Character, MICHAEL_OUTFITS, outfits
import world

MJ = 'michael84'          # adult Michael, 1982-84 (continuity with the Jackson 5 V3 finale)
KID = 'michael'           # Jackson 5 era Michael

NEW = {
    'quincy': Design('Quincy', 1.64, 0.072, '#6e4632', (1.06, 1.0), face_w=0.9, jaw=0.75, eye=0.86, eye_sp=0.35, brow_w=1.1,
                     nose_w=1.1, lip='#5a3028', shoulders=0.25, leg=0.49, mustache=0.85, beard=0.5, glasses='#2a1e18',
                     hair='short', hair_cy=0.12, bump=0.2, hair_col='#2a2420', seed=201, sig='#3a5068', smile_bias=0.35),
    'eddie': Design('Eddie', 1.58, 0.074, '#ebc3a2', (1.22, 1.0), face_w=0.84, jaw=0.6, eye=0.95, eye_sp=0.35, brow_w=0.95,
                    nose_w=0.72, lip='#b0675e', shoulders=0.23, leg=0.5, hair='shag', hair_cy=0.18, bump=0.4,
                    hair_col='#6b4526', seed=202, sig='#c4141a', smile_bias=0.7),
}
SKINS = ['#5a3a28', '#7a5034', '#8f5e3f', '#a8724c', '#c9946a', '#6c442e', '#4a2e20', '#b98058', '#e0b08a', '#946040']
rng = np.random.default_rng(83)
for i in range(16):
    k = f'x{i}'
    NEW[k] = Design('Extra', float(rng.uniform(1.52, 1.72)), 0.071, SKINS[i % len(SKINS)], [(1.08, 1.02), (1.3, 1.35), (1.08, 1.02), (1.3, 1.22)][i % 4],
                    face_w=float(rng.uniform(0.82, 0.92)), jaw=float(rng.uniform(0.4, 1.0)), eye=float(rng.uniform(0.82, 0.98)),
                    brow_w=float(rng.uniform(0.9, 1.3)), shoulders=float(rng.uniform(0.22, 0.26)), leg=0.49,
                    mustache=float(rng.choice([0, 0, 0.5, 0.8])), seed=300 + i,
                    hair=['short', 'curl', 'short', 'afro'][i % 4], hair_cy=[0.12, -0.15, 0.12, 0.25][i % 4],
                    bump=[0.2, 0.6, 0.2, 0.5][i % 4])
for i, (sk, h) in enumerate([('#7a5034', 0.9), ('#c9946a', 0.85), ('#5a3a28', 0.95)]):
    NEW[f'fan{i}'] = Design('Fan', h, 0.112, sk, (1.3, 1.25) if i != 1 else (1.04, 1.0), seed=400 + i,
                            hair='afro' if i != 1 else 'short', hair_cy=0.25 if i != 1 else 0.12, bump=0.4, smile_bias=0.5,
                            hair_col='#1d1410' if i != 1 else '#5a3a1e')
DESIGNS.update(NEW)
world.CHARS.update({k: Character(k) for k in NEW})

O_STUDIO = Outfit(shirt='#d9c9a6', pants='#25222c', collar='#efe6d6', flare=False, socks='#f4f4f8', shoes='#0c0c10',
                  stripes='#c4b08a')
O_BEATIT = Outfit(shirt='#c3121c', pants='#141216', collar='#a50e18', zips=True, under='#121014', flare=False,
                  socks='#f4f4f8', shoes='#0c0c10')
O_TEE = Outfit(shirt='#1e1c22', pants='#141216', collar='#2a2830', flare=False, socks='#f4f4f8', shoes='#0c0c10')
O_STAGE = MICHAEL_OUTFITS['michael82']
O_QUINCY = Outfit(shirt='#3a5068', pants='#2a2a30', collar='#e8e0d0', flare=False, vest='#5a4636')
O_EDDIE = Outfit(shirt='#ece8e0', pants='#2c3e5e', collar='#ece8e0', flare=False, stripes='#d23a2a', shoes='#e8e4dc')
O_J5 = outfits('tv')
# the two street groups and the dancers (no gang colours named or emphasised; just two distinct crews)
O_GROUP_A = [Outfit(shirt='#e9e4da', pants='#2a3448', vest=v, collar='#e9e4da', flare=False) for v in
             ('#1c181a', '#2a2224', '#1a1a20', '#302826')]
O_GROUP_B = [Outfit(shirt=s, pants='#1c1a1e', collar=s, flare=False, stripes=st) for s, st in
             (('#4a6a8a', '#3a5674'), ('#5a5a62', '#4a4a52'), ('#6a4a3a', '#5a3a2a'), ('#3a4a5a', '#2a3a4a'))]
O_DANCERS = [Outfit(shirt=s, pants=p, collar=s, flare=False, vest=v, socks='#f4f4f8') for s, p, v in
             (('#1a1a1e', '#2a3448', None), ('#e9e4da', '#141216', '#2a2224'), ('#5a1a22', '#1a1a1e', None),
              ('#2a3a4a', '#1a1a1e', '#1c181a'), ('#d8d0c0', '#2a3448', None), ('#3a3a40', '#141216', '#5a1a22'))]
O_CREW = Outfit(shirt='#5a5248', pants='#2a2a30', collar='#5a5248', flare=False, hat='#2a3448')
O_FANS = [Outfit(shirt='#e06a2a', pants='#2a3a5a', collar='#f4d06a', stripes='#c4501a'),
          Outfit(shirt='#3a8a5a', pants='#3a2a2a', collar='#e8e0d0'),
          Outfit(shirt='#c4141a', pants='#141216', collar='#a50e18', zips=True, under='#141216')]   # kid in a copy-cat jacket

L_STUDIO = dict(key=(-0.5, -0.85), amb='#ffcf98', amb_a=0.18, rim='#ffe2b0', line='#24140e', floor_shadow=0.4)
L_DARK = dict(key=(0.0, -1.0), amb='#8a9ac8', amb_a=0.25, rim='#ffe8c8', line='#120c14', floor_shadow=0.45)
L_NEON = dict(key=(0.6, -0.7), amb='#7a4aa8', amb_a=0.3, rim='#ff5ab4', line='#120a18', floor_shadow=0.5)
L_STREET = dict(key=(-0.6, -0.7), amb='#3a6a9a', amb_a=0.3, rim='#5ae0ff', line='#0a0c14', floor_shadow=0.5)
L_STAGE = dict(key=(-0.2, -0.98), amb='#e0e8ff', amb_a=0.15, rim='#ffffff', line='#141020', floor_shadow=0.45)
L_WARM = dict(key=(-0.3, -0.95), amb='#ffd8a8', amb_a=0.2, rim='#ffe8c0', line='#2a1410', floor_shadow=0.45)
L_TV70 = dict(key=(-0.3, -0.9), amb='#ffe0b0', amb_a=0.15, rim='#fff0d0', line='#2a1410', floor_shadow=0.4)
