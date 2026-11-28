"""DANSE MACABRE - Everyone Must Dance. Score, arrangement and mix."""
import numpy as np, soundfile as sf, sys, json
import synth as S
from synth import SR

BPM = 136
BEAT = 60 / BPM
STEP = BEAT / 4
BARS = 34
LEN_S = BARS * 16 * STEP  # 60.0 s
N = int(round(LEN_S * SR))
TAIL = int(3 * SR)
NT = N + TAIL
SWING = 0.07 * STEP


def T(bar, step=0.0):
    """bar 1-indexed, step in 16ths (may be fractional / >16)"""
    a = (bar - 1) * 16 + step
    t = a * STEP
    fs = a - np.floor(a)
    if abs(fs) < 1e-9 and int(a) % 2 == 1:
        t += SWING
    return t


# ------------------------------------------------------------------ harmony
CH = {1: 'Dm', 2: 'Bb', 3: 'Dm', 4: 'Bb', 5: 'Gm', 6: 'A', 7: 'Gm', 8: 'A', 9: 'Bb', 10: 'C', 11: 'Dm', 12: 'A',
      13: 'Dm', 14: 'Bb', 15: 'Gm', 16: 'A', 17: 'Dm', 18: 'Bb', 19: 'Eb', 20: 'A', 21: 'Bb', 22: 'C', 23: 'Dm',
      24: 'A', 25: 'Dm', 26: 'Bb', 27: 'Gm', 28: 'A', 29: 'Dm', 30: 'Bb', 31: 'Eb', 32: 'A', 33: 'Dm', 34: 'Dm'}
VOICE = {'Dm': [62, 65, 69], 'Bb': [62, 65, 70], 'Gm': [62, 67, 70], 'A': [61, 64, 69], 'C': [60, 64, 67],
         'Eb': [63, 67, 70]}
ROOT = {'Dm': 38, 'Bb': 34, 'Gm': 31, 'A': 33, 'C': 36, 'Eb': 39}
FIFTH = {'Dm': 7, 'Bb': 7, 'Gm': 7, 'A': 7, 'C': 7, 'Eb': 7}
THIRD = {'Dm': 3, 'Bb': 4, 'Gm': 3, 'A': 4, 'C': 4, 'Eb': 4}

# ------------------------------------------------------------------ the HOOK (4 bars, 16th grid)
# (step, dur, midi, vel, accent)
HOOK = [
    [(0, 2, 69, .92, .6), (2, 1, 74, .74, 0), (3, 1, 76, .74, 0), (4, 2, 77, .9, .3), (6, 1, 74, .78, 0),
     (7, 3, 81, 1.0, 1), (10, 1, 79, .74, 0), (11, 1, 77, .76, 0), (12, 2, 76, .86, .2), (14, 2, 73, .9, .4)],
    [(0, 2, 69, .92, .5), (2, 1, 74, .74, 0), (3, 1, 76, .74, 0), (4, 2, 77, .9, .3), (6, 1, 74, .78, 0),
     (7, 3, 82, 1.0, 1), (10, 1, 81, .74, 0), (11, 1, 79, .76, 0), (12, 2, 77, .86, .2), (14, 2, 74, .86, .2)],
    [(0, 1, 79, .95, .8), (1, 1, 79, .62, 0), (2, 1, 82, .82, .2), (3, 2, 81, .92, .6), (5, 1, 79, .74, 0),
     (6, 2, 77, .86, .2), (8, 1, 76, .74, 0), (9, 1, 77, .76, 0), (10, 2, 79, .9, .4), (12, 2, 74, .84, .1),
     (14, 2, 70, .86, .3)],
    [(0, 3, 73, 1.0, 1), (3, 1, 76, .74, 0), (4, 2, 79, .9, .3), (6, 1, 77, .84, .2), (7, 1, 76, .74, 0),
     (8, 2, 73, .84, .2), (10, 1, 74, .74, 0), (11, 3, 76, .95, .8), (14, 1, 74, .7, 0), (15, 1, 73, .76, 0)],
]
# drop-1 tag: bar 4 variant with a climbing run into the call-and-response
HOOK4_RUN = [(0, 3, 73, 1.0, 1), (3, 1, 76, .74, 0), (4, 2, 79, .9, .3), (6, 1, 77, .84, .2), (7, 1, 76, .74, 0),
             (8, 1, 73, .8, 0), (9, 1, 74, .74, 0), (10, 1, 76, .78, 0), (11, 1, 77, .8, 0), (12, 1, 79, .84, 0),
             (13, 1, 81, .88, 0), (14, 2, 82, .95, .6)]
# Neapolitan (Eb) twist for drop 2 / grand
HOOK3_NEAP = [(0, 1, 82, .95, .8), (1, 1, 82, .62, 0), (2, 1, 87, .9, .5), (3, 2, 86, .92, .6), (5, 1, 82, .74, 0),
              (6, 2, 79, .86, .2), (8, 1, 75, .8, .3), (9, 1, 77, .76, 0), (10, 2, 79, .9, .4), (12, 2, 82, .86, .2),
              (14, 2, 75, .9, .5)]
# grand finale: bar 4 with a fiery turn
HOOK4_FIRE = [(0, 3, 73, 1.0, 1), (3, 1, 76, .78, 0), (4, 1, 79, .9, .3), (5, 1, 82, .9, .3), (6, 1, 81, .84, .2),
              (7, 1, 79, .74, 0), (8, 1, 77, .84, .2), (9, 1, 76, .74, 0), (10, 1, 74, .8, 0), (11, 3, 76, .98, 1),
              (14, 1, 74, .7, 0), (15, 1, 73, .78, 0)]

# call & response (fiddle calls, harpsichord answers an octave up)
CALL = {
    9: [(0, 2, 77, .9, .5), (2, 1, 74, .74, 0), (3, 1, 77, .78, 0), (4, 3, 82, 1.0, 1), (7, 1, 81, .7, 0)],
    10: [(0, 2, 79, .9, .5), (2, 1, 76, .74, 0), (3, 1, 79, .78, 0), (4, 3, 84, 1.0, 1), (7, 1, 82, .7, 0)],
    11: [(0, 2, 81, .9, .5), (2, 1, 77, .74, 0), (3, 1, 81, .78, 0), (4, 3, 86, 1.0, 1), (7, 1, 84, .7, 0)],
    12: [(0, 2, 85, 1.0, 1), (2, 1, 81, .78, 0), (3, 1, 79, .76, 0), (4, 2, 77, .86, .2), (6, 1, 76, .76, 0),
         (7, 1, 74, .76, 0), (8, 2, 73, .9, .4), (10, 1, 74, .76, 0), (11, 1, 76, .8, 0), (12, 4, 81, .95, .6, 'trem')],
}
RESP = {
    9: [(8, 1, 86), (9, 1, 84), (10, 1, 82), (11, 1, 81), (12, 2, 82), (14, 2, 77)],
    10: [(8, 1, 88), (9, 1, 86), (10, 1, 84), (11, 1, 82), (12, 2, 84), (14, 2, 79)],
    11: [(8, 1, 89), (9, 1, 88), (10, 1, 86), (11, 1, 84), (12, 2, 81), (14, 2, 77)],
    12: [(8, 1, 81), (9, 1, 85), (10, 1, 88), (11, 1, 91), (12, 1, 88), (13, 1, 85), (14, 1, 81), (15, 1, 76)],
}

fiddle = []      # lead
fiddle_oct = []  # octave-up double (grand)
viola = []       # octave-down (grand)
markers = []


def add_bar(dst, bar, notes, shift=0, velmul=1.0):
    for nt in notes:
        st, du, m, v, acc = nt[:5]
        trem = len(nt) > 5 and nt[5] == 'trem'
        t0 = T(bar, st)
        t1 = T(bar, st + du)
        dst.append(dict(start=t0, dur=t1 - t0, midi=m + shift, vel=v * velmul, accent=acc, trem=trem))


def hook(dst, bar, variant='plain', shift=0, velmul=1.0):
    b4 = {'plain': HOOK[3], 'run': HOOK4_RUN, 'fire': HOOK4_FIRE}
    add_bar(dst, bar, HOOK[0], shift, velmul)
    add_bar(dst, bar + 1, HOOK[1], shift, velmul)
    add_bar(dst, bar + 2, HOOK3_NEAP if variant in ('neap', 'neapfire') else HOOK[2], shift, velmul)
    add_bar(dst, bar + 3, HOOK4_FIRE if variant in ('fire', 'neapfire') else b4.get(variant, HOOK[3]), shift, velmul)


# ---- INTRO bars 1-2: hook immediately (first half), Death's tritone double-stop on the downbeat
add_bar(fiddle, 1, HOOK[0])
add_bar(fiddle, 2, HOOK[1])
# ---- DROP 1 bars 3-8
hook(fiddle, 3)
add_bar(fiddle, 7, HOOK[2])
add_bar(fiddle, 8, HOOK4_RUN)
# ---- CALL & RESPONSE bars 9-12
for b in range(9, 13):
    add_bar(fiddle, b, CALL[b])
# ---- DROP 2 bars 13-20
hook(fiddle, 13)
hook(fiddle, 17, 'neap')
# ---- BUILD bars 21-24 : motif cell climbing, tremolo
BUILD = {
    21: [(0, 2, 70, .8, .4), (2, 1, 74, .7, 0), (3, 1, 77, .72, 0), (4, 4, 82, .85, .5, 'trem'),
         (8, 2, 70, .82, .4), (10, 1, 74, .72, 0), (11, 1, 77, .74, 0), (12, 4, 82, .88, .5, 'trem')],
    22: [(0, 2, 72, .84, .4), (2, 1, 76, .74, 0), (3, 1, 79, .76, 0), (4, 4, 84, .88, .5, 'trem'),
         (8, 2, 72, .86, .4), (10, 1, 76, .76, 0), (11, 1, 79, .78, 0), (12, 4, 84, .9, .5, 'trem')],
    23: [(0, 2, 74, .88, .5), (2, 1, 77, .78, 0), (3, 1, 81, .8, 0), (4, 2, 86, .92, .6), (6, 2, 74, .86, .4),
         (8, 1, 77, .8, 0), (9, 1, 81, .82, 0), (10, 2, 86, .94, .6), (12, 1, 77, .84, 0), (13, 1, 81, .86, 0),
         (14, 2, 86, .96, .7)],
    24: [(0, 4, 85, 1.0, 1, 'trem'), (4, 4, 88, 1.0, .6, 'trem'), (8, 4, 91, 1.0, .6, 'trem')],
}
for b, nn in BUILD.items():
    add_bar(fiddle, b, nn)
# ---- GRAND DANCE bars 25-32
hook(fiddle, 25, 'fire')
hook(fiddle, 29, 'neapfire')
hook(viola, 25, 'fire', -12, 0.8)
hook(viola, 29, 'neapfire', -12, 0.8)
hook(fiddle_oct, 25, 'fire', 12, 0.4)
hook(fiddle_oct, 29, 'neapfire', 12, 0.55)
# ---- ENDING bars 33-34
END33 = [(0, 2, 69, .95, .6), (2, 1, 74, .78, 0), (3, 1, 76, .78, 0), (4, 2, 77, .92, .3), (6, 1, 74, .8, 0),
         (7, 3, 81, 1.0, 1), (10, 1, 76, .85, .3), (11, 1, 73, .9, .3), (12, 4, 74, 1.0, 1)]
add_bar(fiddle, 33, END33)
add_bar(viola, 33, END33, -12, 0.8)
# Death's tritone double-stops (A + Eb) - the devil's tuning
tritone = [dict(start=T(1, 0), dur=T(1, 2) - T(1, 0), midi=75, vel=0.55, accent=0.6, trem=False),
           dict(start=T(25, 0), dur=T(25, 2) - T(25, 0), midi=75, vel=0.6, accent=0.6, trem=False),
           dict(start=T(34, 0), dur=T(34, 7) - T(34, 0), midi=75, vel=0.6, accent=0.8, trem=True)]
fiddle.append(dict(start=T(34, 0), dur=T(34, 7) - T(34, 0), midi=69, vel=0.75, accent=1, trem=True))

# ------------------------------------------------------------------ harpsichord
harp = []  # (t, midi, dur, vel, pan)


def H(bar, st, m, du=1, v=0.7, p=None):
    harp.append((T(bar, st), m, T(bar, st + du) - T(bar, st), v, p if p is not None else np.random.uniform(-.35, .35)))


np.random.seed(5)
for b in range(3, 9):  # drop 1: gothic oom-pah, offbeat chords + low pulse
    c = CH[b]
    v = VOICE[c]
    H(b, 0, ROOT[c] + 12, 2, .75, -.2)
    H(b, 8, ROOT[c] + 12 + 7 if c != 'A' else ROOT[c] + 12 + 7, 2, .7, -.2)
    for st in (2, 6, 10, 14):
        for i, m in enumerate(v):
            H(b, st + i * 0.06, m, 1, .5 + .1 * (st in (6, 14)), .5 - .5 * i)
for b in range(9, 13):  # answer phrases
    for st, du, m in RESP[b]:
        H(b, st, m, du, .85, .15)
    for i, m in enumerate(VOICE[CH[b]]):
        H(b, 0 + i * 0.08, m - 12, 4, .5, -.3)
ARP = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 2, 3, 2]


def arp_bar(b, octave=0, vel=.62, pan=0):
    v = VOICE[CH[b]] + [VOICE[CH[b]][0] + 12]
    for st in range(16):
        m = v[ARP[st]] + octave
        acc = 1.15 if st % 4 == 0 else (1.05 if st in (3, 7, 11) else 1.0)
        H(b, st, m, 1, vel * acc, pan + 0.55 * np.sin(st * 1.7))


for b in range(13, 21):
    arp_bar(b)
for b in range(21, 25):
    arp_bar(b, 0, .38 + .1 * (b - 21))
for b in range(25, 33):
    arp_bar(b, 12, .5)
    H(b, 0, ROOT[CH[b]] + 24, 4, .6, -.3)
    H(b, 8, ROOT[CH[b]] + 24, 4, .5, -.3)
for i, m in enumerate([62, 65, 69, 74]):
    H(33, 12 + i * 0.08, m, 8, .95, 0)

# ------------------------------------------------------------------ bass
bass = []


def B(bar, st, m, du, v=1.0, op=1.0):
    bass.append(dict(start=T(bar, st), dur=T(bar, st + du) - T(bar, st) - 0.008, midi=m, vel=v, open=op))


def approach(c, nc):
    r, nr = ROOT[c], ROOT[nc]
    if nr == r:
        return r + 12
    return nr + (1 if nr < r else -1)


for b in range(3, 9):  # drop1: galloping offbeat
    c = CH[b]; r = ROOT[c]
    for st, du, iv, v in [(2, 1, 0, .95), (3, 1, 0, .8), (6, 2, 12, .9), (10, 1, 0, .95), (11, 1, 0, .8),
                          (14, 2, 7, .9)]:
        B(b, st, r + iv, du, v, .7)
for b in range(9, 13):  # lighter, sustained but still pulsing
    c = CH[b]; r = ROOT[c]
    for st, du, iv, v in [(2, 2, 0, .8), (6, 2, 0, .7), (10, 2, 0, .8), (14, 2, 12, .75)]:
        B(b, st, r + iv, du, v, .45)
ROLL = [(1, 0, .7), (2, 0, .9), (3, 12, .85), (5, 0, .7), (6, 0, .9), (7, 12, .85), (9, 0, .7), (10, 0, .9),
        (11, 12, .85), (13, 7, .8), (14, 'a5', .9), (15, 'ap', .85)]


def roll_bar(b, op):
    c = CH[b]; r = ROOT[c]
    nc = CH.get(b + 1, 'Dm')
    for st, iv, v in ROLL:
        if iv == 'a5':
            m = r + (10 if c in ('Dm', 'Gm', 'A') else 7)
        elif iv == 'ap':
            m = approach(c, nc)
        else:
            m = r + iv
        B(b, st, m, 1, v, op)


for b in range(13, 21):
    roll_bar(b, 0.9)
for b in range(21, 23):
    r = ROOT[CH[b]]
    for st, du, iv, v in [(2, 2, 0, .8), (6, 2, 12, .75), (10, 2, 0, .8), (14, 1, 12, .75), (15, 1, 7, .7)]:
        B(b, st, r + iv, du, v, .3 + .2 * (b - 21))
for st in range(0, 16, 2):  # bar 23-24: 8ths then 16ths pedal
    B(23, st, ROOT['Dm'] + (12 if st % 4 == 2 else 0), 1, .85, .9)
for st in range(0, 12):
    B(24, st, ROOT['A'] + (12 if st % 2 else 0), 1, .7 + st * .02, .6 + st * 0.05)
for b in range(25, 33):
    roll_bar(b, 1.15)
for st, du, iv, v in [(1, 1, 0, .7), (2, 1, 0, .9), (3, 1, 12, .85), (5, 1, 0, .7), (6, 1, 0, .9), (7, 1, 12, .85),
                      (9, 1, 0, .8), (10, 1, 12, .9)]:
    B(33, st, 38 + iv, du, v, 1.1)
B(33, 12, 38, 6, 1.0, 1.3)  # final hit
B(34, 12, 33, 1, .6, .5)  # pickup back into the loop: A ... -> D
B(34, 14, 37, 1, .7, .6)

# ------------------------------------------------------------------ drums & percussion events
ev = {k: [] for k in ['kick', 'snare', 'hatc', 'hato', 'wood', 'bone', 'rattle', 'chain', 'knock', 'xylo', 'bell',
                      'impact', 'riser', 'down', 'rev']}


def E(kind, bar, st, *args):
    ev[kind].append((T(bar, st),) + args)


# intro: heartbeat kick, coffin knocks on 2 & 4, rattle fill
for b in (1, 2):
    for st in (0, 8):
        E('kick', b, st, .55, 'soft')
    for st in (4, 12):
        E('knock', b, st, .9)
E('knock', 2, 14, .6); E('knock', 2, 15, .75)
E('rattle', 2, 8, .5, .5)
for st in range(8, 16):
    E('snare', 2, st, .12 + .05 * (st - 8))
E('riser', 1, 8, T(3, 0) - T(1, 8))

# main grooves
for b in range(3, 34):
    sec = 'd1' if b <= 8 else 'cr' if b <= 12 else 'd2' if b <= 20 else 'bu' if b <= 24 else 'gr' if b <= 32 else 'end'
    if sec == 'end':
        for st in (0, 4, 8, 12):
            E('kick', b, st, 1.0, 'full')
        for st in (4,):
            E('snare', b, st, .9)
        E('hato', b, 2, .7); E('hato', b, 6, .7); E('hato', b, 10, .7)
        continue
    if sec == 'bu':
        k = b - 21
        steps = [0, 4, 8, 12] if k < 2 else list(range(0, 16, 2)) if k == 2 else list(range(0, 12))
        for st in steps:
            E('kick', b, st, .85 + .03 * k, 'full')
        if k < 3:
            for st in (4, 12):
                E('snare', b, st, .8)
        else:
            for st in range(0, 12):
                E('snare', b, st, .25 + st * .05)
            for st in (12, 13, 14, 15):
                E('knock', b, st, .7 + .1 * (st - 12))
        for st in (2, 6, 10, 14):
            E('hato', b, st, .5 + .1 * k)
        for st in range(1, 16, 2):
            E('bone', b, st, .25 + .1 * k, 1.0 + .15 * (st % 4 == 3))
        continue
    for st in (0, 4, 8, 12):
        E('kick', b, st, 1.0, 'full')
    # turnaround drops: remove last kick in phrase ends for air
    if b in (8,) :
        ev['kick'].pop()
    E('snare', b, 4, .85 if sec != 'cr' else .6)
    E('snare', b, 12, .9 if sec != 'cr' else .7)
    for st in (2, 6, 10, 14):
        E('hato', b, st, .55 if sec == 'd1' else .65)
    if sec in ('d2', 'gr'):
        for st in (1, 3, 5, 7, 9, 11, 13, 15):
            E('hatc', b, st, .3 + .15 * (st % 4 == 3))
    if sec in ('d1', 'cr'):
        for st, p in [(3, 1.0), (6, 1.35), (11, 1.0), (14, 1.35)]:
            E('wood', b, st, .55, p)
    if sec in ('d2', 'gr'):
        # skeleton percussion: bone clicks syncopated + rattles on offbeats
        for st, v in [(3, .7), (6, .45), (9, .5), (11, .75), (14, .45), (15, .55)]:
            E('bone', b, st, v, 1.0 + .3 * (st in (6, 14)))
        E('rattle', b, 6, .25, .35); E('rattle', b, 14, .3, .4)
        E('wood', b, 7, .5, 1.35)
        E('chain', b, 7, .45 if sec == 'd2' else .6)
    if sec == 'gr':
        E('chain', b, 12, .5)
        for st, p in [(3, 1.0), (10, 1.35)]:
            E('wood', b, st, .5, p)
    # coffin "knock-knock" at the end of every 2nd bar
    if b % 2 == 0 and b not in (12, 20, 32):
        E('knock', b, 13, .55); E('knock', b, 15, .7)
    # phrase-end fills
    if b in (8, 12, 16, 20, 28, 32):
        E('rattle', b, 12, .45, .55)
        for st in (12, 13, 14, 15):
            E('snare', b, st, .3 + .12 * (st - 12))
# remove downbeat kick on beat 4 of bar 12 / 20 for anticipation
# drops & impacts
for b in (3, 13, 25):
    E('impact', b, 0, 1.0 if b == 25 else .75)
E('impact', 33, 12, 1.0)
E('down', 3, 0, 1.6); E('down', 13, 0, 1.6); E('down', 25, 0, 2.0); E('down', 33, 12, 2.0)
E('riser', 11, 0, T(13, 0) - T(11, 0))
E('riser', 21, 0, T(25, 0) - T(21, 0))
E('rev', 12, 8, T(13, 0) - T(12, 8))
E('rev', 24, 8, T(25, 0) - T(24, 8))
E('rev', 34, 8, T(35, 0) - T(34, 8))
E('rev', 8, 12, T(9, 0) - T(8, 12))
# ending: last beat knocks back into the loop
for st, v in [(12, .55), (13, .65), (14, .8), (15, .95)]:
    E('knock', 34, st, v)
E('rattle', 34, 4, .6, .9)
E('chain', 33, 12, .9)

# bells
E('bell', 1, 0, 74, .9, 'hi'); E('bell', 1, 0, 50, .6, 'lo')
for b in (3, 13, 25):
    E('bell', b, 0, 74, .9, 'hi'); E('bell', b, 0, 50, .9, 'lo')
E('bell', 9, 0, 70, .55, 'hi'); E('bell', 11, 0, 74, .55, 'hi')
for b in list(range(13, 21)) + list(range(25, 33)):
    off = (b - 13) % 4 if b < 21 else (b - 25) % 4
    if off == 0:
        E('bell', b, 7, 81, .4, 'sm')
    elif off == 1:
        E('bell', b, 7, 82 if CH[b] == 'Bb' else 81, .4, 'sm')
E('bell', 21, 0, 70, .5, 'hi'); E('bell', 23, 0, 74, .6, 'hi')
for st in (0, 4, 8):
    E('bell', 24, st, 69, .45 + .1 * st / 4, 'hi')
E('bell', 33, 12, 74, 1.0, 'hi'); E('bell', 33, 12, 50, 1.0, 'lo'); E('bell', 33, 12, 62, .7, 'hi')
E('bell', 34, 8, 81, .3, 'sm')

# bone xylophone (skeleton xylophone) - drop2 + grand, unexpected syncopated melodic accents
XY = [(2, 2), (3, 1), (6, 0), (10, 2), (11, 3), (14, 1)]
for b in list(range(13, 21)) + list(range(25, 33)):
    v = VOICE[CH[b]] + [VOICE[CH[b]][0] + 12]
    for st, i in XY:
        E('xylo', b, st, v[i] + 12, .5 + .15 * (st in (3, 11)))
# xylophone answer lick in the Neapolitan bar
for st, m in [(12, 87), (13, 86), (14, 82), (15, 79)]:
    E('xylo', 19, st, m, .7)
    E('xylo', 31, st, m, .75)

# ------------------------------------------------------------------ organ / strings / winds
organ = []  # (t, midis, dur, vel)


def O(bar, st, du, midis, v):
    organ.append((T(bar, st), midis, T(bar, st + du) - T(bar, st), v))


O(3, 0, 6, [50, 57, 62, 65, 69], .8)
O(13, 0, 6, [50, 57, 62, 65, 69], .8)
for b in range(21, 25):
    c = CH[b]
    O(b, 0, 16, [x - 12 for x in VOICE[c]] + VOICE[c], .35 + .12 * (b - 21))
for b in range(25, 33):
    c = CH[b]
    O(b, 0, 16, [x - 12 for x in VOICE[c]] + [VOICE[c][0]], .42)
O(33, 12, 14, [38, 50, 57, 62, 65, 69, 74], 1.0)
O(1, 0, 3, [50, 57, 62], .35)

strings = []  # (t, midi, dur, vel, stacc)


def Sx(bar, st, du, m, v, stc=False):
    strings.append((T(bar, st), m, T(bar, st + du) - T(bar, st), v, stc))


for b in range(13, 21):  # staccato sinister stabs
    for st in (6, 14):
        for m in VOICE[CH[b]]:
            Sx(b, st, 1, m - 12, .55, True)
# build: rising sustained + run
for b in range(21, 25):
    for m in VOICE[CH[b]]:
        Sx(b, 0, 16, m, .35 + .1 * (b - 21))
RUN = [69, 70, 73, 74, 76, 77, 79, 81, 82, 85, 86, 88]
for i, m in enumerate(RUN):
    Sx(24, 4 + i * 0.75, 0.75, m - 12, .45 + .03 * i, True)
# grand: pedal counter-line + chords
PED = {'Dm': 74, 'Bb': 74, 'Gm': 74, 'A': 73, 'Eb': 75}
for b in range(25, 33):
    Sx(b, 0, 16, PED[CH[b]], .45)
    Sx(b, 0, 16, PED[CH[b]] - 12, .4)
    for m in VOICE[CH[b]]:
        Sx(b, 0, 16, m - 12, .3)
for m in [50, 57, 62, 65, 69, 74]:
    Sx(33, 12, 12, m, .8)

recorder = []
shawm = []


def W(dst, bar, st, du, m, v):
    dst.append(dict(start=T(bar, st), dur=T(bar, st + du) - T(bar, st), midi=m, vel=v))


def flourish(dst, bar, st, notes, v=.6, d=0.5):
    for i, m in enumerate(notes):
        W(dst, bar, st + i * d, d * (1.6 if i == len(notes) - 1 else 0.9), m, v * (0.8 + 0.2 * i / len(notes)))


flourish(recorder, 2, 12, [86, 88, 89, 91, 93], .55, 0.5)
recorder[-1]['dur'] = T(3, 2) - recorder[-1]['start']
flourish(recorder, 8, 12, [93, 91, 89, 88, 86, 85, 86, 89], .5, 0.5)
# variation: recorder trill on bar 12 tail
for i in range(8):
    W(recorder, 12, 8 + i * 0.5, 0.45, 88 if i % 2 == 0 else 89, .45)
flourish(recorder, 16, 12, [86, 88, 89, 91, 93, 94, 93, 91], .5, 0.5)
flourish(recorder, 20, 13, [89, 91, 93, 94, 97], .55, 0.5)
flourish(recorder, 28, 12, [86, 88, 89, 91, 93, 94, 93, 91], .55, 0.5)
flourish(recorder, 32, 12, [93, 94, 97, 94, 93, 91, 89, 88], .55, 0.5)
# grand: shawm doubles the hook one octave down - medieval bite
hook(shawm, 25, 'fire', -12, .42)
hook(shawm, 29, 'neapfire', -12, .42)
for nt in shawm:
    nt.pop('accent'); nt.pop('trem')
# shawm stabs in the Neapolitan bar of drop 2
for st in (0, 3, 6):
    W(shawm, 19, st, 1.5, 63, .45); W(shawm, 19, st, 1.5, 70, .35)


# ------------------------------------------------------------------ RENDER
def render():
    stems = {}
    print('fiddle...', flush=True)
    fid = S.render_bowed(fiddle, NT, vib_depth=0.2, bright=1.05, seed=1)
    tri = S.render_bowed(tritone, NT, vib_depth=0.1, bright=1.0, seed=2) * 0.8
    fid2 = S.render_bowed([dict(d, start=d['start'] + 0.012) for d in fiddle if d['start'] > T(25, 0) - 0.01], NT,
                          vib_rate=6.1, vib_depth=0.16, bright=0.95, seed=3)
    foct = S.render_bowed(fiddle_oct, NT, vib_rate=5.9, vib_depth=0.18, bright=0.8, seed=4)
    vla = S.render_bowed(viola, NT, vib_rate=5.4, vib_depth=0.18, bright=1.0, seed=5, kind='viola')
    stems['fiddle'] = S.pan(fid + tri, 0.0)
    stems['fiddle2'] = np.stack([fid2 * 0.9, fid2 * 0.35], 1) * 0.55 + np.stack([foct * .3, foct * .8], 1) * 0.7
    stems['viola'] = S.pan(vla, -0.25)
    print('harpsichord...', flush=True)
    h = np.zeros((NT, 2))
    for i, (t, m, du, v, p) in enumerate(harp):
        sig = S.harpsi_note(m, du, v, 100 + i)
        S.place(h, S.pan(sig, float(np.clip(p, -1, 1))), t)
    sb = S.soundboard_ir()
    h[:, 0] = S.fftconvolve(h[:, 0], sb)[:NT]
    h[:, 1] = S.fftconvolve(h[:, 1], sb)[:NT]
    stems['harpsi'] = h
    print('hurdy-gurdy...', flush=True)
    gate = np.zeros(NT)

    def g_on(b0, b1, lvl, fade=0.05):
        i0, i1 = int(T(b0, 0) * SR), int(T(b1, 0) * SR)
        gate[i0:i1] = lvl
    g_on(1, 3, .7); g_on(3, 9, .8); g_on(9, 13, .25); g_on(13, 21, .85); g_on(21, 25, .9); g_on(25, 33, 1.0)
    g_on(33, 35, .9)
    gate = S.lp(gate, 8)
    # final bar: drone fades
    i0 = int(T(34, 0) * SR)
    gate[i0:] *= np.exp(-np.arange(NT - i0) / (0.6 * SR))
    bsteps = []
    for b in range(1, 35):
        base = (b - 1) * 16
        if 9 <= b <= 12:
            continue
        st = (2, 6, 10, 14) if b < 25 or b > 32 else (2, 6, 10, 14, 15)
        bsteps += [base + s for s in st]
    swingf = lambda s: SWING if int(s) % 2 == 1 else 0
    dl = S.hurdy_drone(NT, [50, 57, 62], bsteps, STEP, seed=7, gate=gate, swing=swingf)
    dr = S.hurdy_drone(NT, [50, 57, 62], bsteps, STEP, seed=8, gate=gate, swing=swingf)
    stems['drone'] = np.stack([dl, dr], 1)
    print('organ, strings, winds...', flush=True)
    o = np.zeros((NT, 2))
    for i, (t, ms, du, v) in enumerate(organ):
        a = S.organ_chord(ms, du, v, 10 + i)
        b_ = S.organ_chord(ms, du, v, 50 + i)
        S.place(o, np.stack([a, b_], 1), t)
    stems['organ'] = o
    st_ = np.zeros((NT, 2))
    for i, (t, m, du, v, stc) in enumerate(strings):
        a = S.strings_note(m, du, v, 200 + i, attack=0.012 if stc else 0.09, release=0.08 if stc else 0.3,
                           stacc=stc, voices=5)
        b_ = S.strings_note(m, du, v, 600 + i, attack=0.012 if stc else 0.09, release=0.08 if stc else 0.3,
                            stacc=stc, voices=5)
        S.place(st_, np.stack([a, b_], 1), t)
    stems['strings'] = st_
    rec = S.wind_line(recorder, NT, 'recorder', 1)
    shw = S.wind_line(shawm, NT, 'shawm', 2)
    stems['winds'] = S.pan(rec, 0.35) + S.pan(shw, -0.3) * 0.8
    print('bass...', flush=True)
    sub, mid = S.bass_line(bass, NT)
    stems['sub'] = np.stack([sub, sub], 1)
    stems['bassmid'] = np.stack([mid, mid], 1)
    print('drums...', flush=True)
    kk = np.zeros((NT, 2)); sn = np.zeros((NT, 2)); hh = np.zeros((NT, 2)); pc = np.zeros((NT, 2))
    bl = np.zeros((NT, 2)); fx = np.zeros((NT, 2))
    for i, (t, v, kind) in enumerate(ev['kick']):
        k = S.kick(v, i)
        if kind == 'soft':
            k = S.lp(k, 500)
        S.place(kk, S.pan(k, 0), t)
    for i, (t, v) in enumerate(ev['snare']):
        S.place(sn, S.pan(S.snare(v, i), 0), t)
    for i, (t, v) in enumerate(ev['hatc']):
        S.place(hh, S.pan(S.hat(False, v, i), 0.3), t)
    for i, (t, v) in enumerate(ev['hato']):
        S.place(hh, S.pan(S.hat(True, v, 1000 + i), -0.2), t)
    for i, (t, v, p) in enumerate(ev['wood']):
        S.place(pc, S.pan(S.woodblock(p, v, i), -0.45 if p > 1.1 else 0.4), t)
    for i, (t, v, p) in enumerate(ev['bone']):
        S.place(pc, S.pan(S.bone_click(p, v, 3000 + i), 0.55 if i % 2 else -0.55), t)
    for i, (t, v, L) in enumerate(ev['rattle']):
        r = S.bone_rattle(L, v, 4000 + i)
        S.place(pc, np.stack([r, S.bone_rattle(L, v, 4500 + i)], 1), t)
    for i, (t, v) in enumerate(ev['chain']):
        S.place(pc, np.stack([S.chain_hit(v, 5000 + i), S.chain_hit(v, 5500 + i)], 1), t)
    for i, (t, v) in enumerate(ev['knock']):
        S.place(pc, S.pan(S.coffin_knock(v, 6000 + i), -0.1), t)
    for i, (t, m, v) in enumerate(ev['xylo']):
        S.place(pc, S.pan(S.bone_xylo(m, v, 7000 + i), 0.35), t)
    for i, (t, m, v, kind) in enumerate(ev['bell']):
        L = {'hi': 4.5, 'lo': 6.0, 'sm': 2.0}[kind]
        b_ = S.bell(m, v * (0.5 if kind == 'sm' else 1), 8000 + i, L, dark=0.8)
        S.place(bl, S.pan(b_, {'hi': 0.2, 'lo': -0.1, 'sm': 0.45}[kind]), t)
    for i, (t, v) in enumerate(ev['impact']):
        S.place(fx, S.pan(S.impact(i) * v, 0), t)
    for i, (t, L) in enumerate(ev['riser']):
        r = S.riser(L, 9000 + i)
        S.place(fx, np.stack([r, S.riser(L, 9100 + i)], 1) * 0.8, t)
    for i, (t, L) in enumerate(ev['down']):
        S.place(fx, np.stack([S.downlifter(L, 9200 + i), S.downlifter(L, 9300 + i)], 1), t)
    for i, (t, L) in enumerate(ev['rev']):
        S.place(fx, S.reverse_swell(9400 + i, L, 74), t)
    stems.update(kick=kk, snare=sn, hats=hh, perc=pc, bells=bl, fx=fx)
    return stems


if __name__ == '__main__':
    stems = render()
    np.savez('stems.npz', **stems)
    json.dump({'kick_times': [e[0] for e in ev['kick'] if e[2] == 'full']}, open('meta.json', 'w'))
    print('done')
