"""THE CRAZIEST MEDIEVAL DISEASES - composition + arrangement -> dry stereo tracks."""
import os, subprocess
import numpy as np
import mido, soundfile as sf
from dsp import *

BPM = 128
SPB = 22500          # samples per beat @48k
S16 = SPB // 4       # 5625
BAR = SPB * 4        # 90000 = 1.875 s
NBARS = 48
N = BAR * NBARS      # 4,320,000 = 90.000 s
TAIL = SR * 3
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'work'); os.makedirs(WORK, exist_ok=True)
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'

rng = np.random.default_rng(1518)

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def nm(s):
    acc = s[1] if s[1] in '#b' else ''
    o = int(s[1 + len(acc):])
    return 12 * (o + 1) + NOTE[s[0]] + (1 if acc == '#' else -1 if acc == 'b' else 0)


def mel(spec):
    out = []
    for tok in spec.split():
        st, ln, n = tok.split(':')
        out.append((float(st), float(ln), nm(n)))
    return out


def tr(bar):
    return 2 if bar >= 41 else 0


def pos(bar, step, swing=0.0, hum=0.0):
    s = (bar - 1) * BAR + step * S16
    if swing and abs(step - round(step)) < 1e-6 and int(round(step)) % 2 == 1:
        s += swing * S16
    if hum:
        s += rng.normal(0, hum * SR)
    return max(0, int(round(s)))


# ------------------------------------------------------------------ tracks
class Tracks(dict):
    def get(self, name):
        if name not in self:
            self[name] = np.zeros((N + TAIL, 2))
        return self[name]

    def add(self, name, start, sig, gain=1.0, pan=0.0):
        buf = self.get(name)
        if sig.ndim == 1:
            sig = pan2(sig, pan)
        end = min(len(buf), start + len(sig))
        if start >= len(buf):
            return
        buf[start:end] += sig[:end - start] * gain


T = Tracks()

# ------------------------------------------------------------------ harmony
CH = {
    'Dm': (38, [62, 65, 69]), 'C': (36, [60, 64, 67]), 'Bb': (34, [58, 62, 65]),
    'A': (33, [57, 61, 64]), 'Eb': (39, [58, 63, 67]), 'Gm': (31, [55, 58, 62]),
    'B': (35, [59, 63, 66]), 'D5': (38, [50, 57, 62])}

HOOK_CH = [[(0, 'Dm')], [(0, 'C')], [(0, 'Dm')], [(0, 'Bb'), (8, 'A')]]
chords = {}
for b in range(1, 17):
    chords[b] = HOOK_CH[(b - 1) % 4]
for b, c in zip(range(17, 25), ['Bb', 'C', 'Dm', 'A'] * 2):
    chords[b] = [(0, c)]
for b in range(25, 33):
    chords[b] = HOOK_CH[(b - 1) % 4]
for b, c in zip(range(33, 41), ['Dm', 'Eb', 'Dm', 'A', 'Gm', 'Eb', 'C', 'B']):
    chords[b] = [(0, c)]
for b in range(41, 48):
    chords[b] = HOOK_CH[(b - 41) % 4]
chords[48] = [(0, 'Bb'), (6, 'A'), (12, 'D5')]


def chord_at(bar, step):
    c = chords[bar][0][1]
    for st, name in chords[bar]:
        if step >= st:
            c = name
    return c


# ------------------------------------------------------------------ melodies (written in D minor)
H1 = mel("0:2:D5 3:2:A4 6:2:D5 8:2:F5 10:2:E5 12:2:D5 14:2:C5")
H1v = mel("0:2:D5 3:2:A4 6:2:D5 8:1:F5 9:1:G5 10:2:F5 12:2:E5 14:2:C5")
H2 = mel("0:2:D5 3:2:A4 6:2:D5 8:2:C5 10:2:A4 12:2:G4 14:2:A4")
H2d = mel("0:2:D5 3:2:A4 6:2:D5 8:2:C5 10:2:A4")          # leaves room for bass answer
H3 = mel("0:2:D5 3:2:A4 6:2:D5 8:2:F5 10:2:G5 12:1:A5 13:1:Bb5 14:2:A5")
H4 = mel("0:2:F5 3:2:D5 6:2:F5 8:2:E5 10:1:F5 11:1:E5 12:2:D5 14:2:C#5")
H4run = mel("0:2:F5 3:2:D5 6:2:F5 8:1:A5 9:1:G5 10:1:F5 11:1:E5 12:1:D5 13:1:E5 14:2:C#5")
H4stop = mel("0:2:F5 3:2:D5 6:2:F5 8:1:E5 9:1:F5 10:1:G5 11:1:A5 12:2:C#6")

lead = {}   # bar -> melody for main hook carriers
lead.update({1: H1, 2: H2, 3: H3, 4: H4, 5: H1v, 6: H2, 7: H3, 8: H4stop})
lead.update({9: H1, 10: H2d, 11: H3, 12: H4run, 13: H1v, 14: H2d, 15: H3, 16: H4})
lead.update({25: H1, 26: H2d, 27: H3, 28: H4run, 29: H1v, 30: H2d, 31: H3, 32: H4})
lead.update({41: H1, 42: H2d, 43: H3, 44: H4run, 45: H1v, 46: H2d, 47: H3})

CALL = {17: mel("0:3:D5 3:3:F5 6:2:Bb5 8:2:A5 10:2:F5 12:4:D5"),
        19: mel("0:3:F5 3:3:A5 6:2:D6 8:2:C6 10:2:A5 12:4:F5"),
        21: mel("0:3:D5 3:3:F5 6:2:Bb5 8:1:C6 9:1:Bb5 10:2:A5 12:2:F5 14:2:G5")}
ANSWER = {18: mel("2:1:E4 3:1:G4 6:2:C5 8:1:Bb4 9:1:A4 10:2:G4 12:2:E4 14:2:C4"),
          20: mel("2:1:E4 3:1:A4 6:2:C#5 8:1:E5 9:1:D5 10:2:C#5 12:2:A4 14:2:E4"),
          22: mel("2:1:G4 3:1:C5 6:2:E5 8:1:D5 9:1:C5 10:2:Bb4 12:1:A4 13:1:G4 14:2:E4")}
TIE23 = mel("0:2:D5 3:2:A4 6:2:D5 8:2:F5 10:2:A5 12:2:D6 14:2:C6")
FILL24 = mel("0:1:A4 3:1:A4 6:1:A4 8:1:C#5 10:1:E5 12:1:G5")

TW_H = {33: mel("0:2:D5 3:2:A4 6:2:D5 8:4:Eb5 12:4:D5"),
        35: mel("0:2:D5 3:2:A4 6:2:D5 8:2:F5 10:2:Eb5 12:4:D5"),
        37: mel("0:2:G5 3:2:D5 6:2:G5 8:2:Bb5 10:2:A5 12:4:G5"),
        39: mel("0:2:E5 3:2:C5 6:2:E5 8:2:G5 10:2:A5 12:2:G5 14:2:E5"),
        40: mel("0:2:D#5 2:2:E5 4:2:F#5 6:2:A5 8:1:B5 9:1:A5 10:1:G5 11:1:F#5")}
TW_L = {34: mel("0:2:G5 3:2:Eb5 6:2:Bb4 8:2:G4 10:2:Bb4 12:2:Eb5 14:2:D5"),
        36: mel("12:1:C#5 13:1:D5 14:1:E5 15:1:F5"),
        38: mel("0:2:G5 3:2:Eb5 6:2:Bb4 8:2:Eb5 10:2:F5 12:4:G5")}
END48 = mel("0:1:F5 3:1:F5 6:6:E5 12:4:D5")

COUNTER = [mel("0:6:A5 6:2:G5 8:8:F5"), mel("0:6:G5 6:2:F5 8:8:E5"),
           mel("0:6:F5 6:2:G5 8:4:A5 12:4:D6"), mel("0:8:D6 8:8:C#6")]

# scale for diatonic harmony (D natural minor, C# over A)
def third_below(m, chord):
    pcs = [2, 4, 5, 7, 9, 10, 1 if chord == 'A' else 0]
    below = [x for x in range(m - 5, m) if x % 12 in pcs]
    return below[-2]


# ------------------------------------------------------------------ event collectors
sf_parts = {'fiddle': [], 'fiddle2': [], 'recorder': [], 'nylon': []}


def sec(bar):
    if bar <= 8: return 'intro'
    if bar <= 16: return 'drop1'
    if bar <= 24: return 'var'
    if bar <= 32: return 'drop2'
    if bar <= 40: return 'twist'
    return 'final'


def play_lute(bar, m, gain=1.0, sw=0.08, nylon=True, pan=-0.22, oct_=0):
    for st, ln, n in m:
        p = pos(bar, st, sw, 0.003)
        dur = ln * S16 / SR
        v = gain * rng.uniform(0.88, 1.0) * (1.08 if st in (0, 3, 6) else 1.0)
        note = n + tr(bar) + oct_
        T.add('lute', p, lute_note(rng, note, dur, v, 0.65), 1.0, pan)
        if nylon:
            sf_parts['nylon'].append((p, int(ln * S16), note, int(min(127, 85 + 30 * v))))


def play_fiddle(bar, m, part='fiddle', gain=1.0, oct_=0, harm=False):
    for st, ln, n in m:
        p = pos(bar, st, 0.04, 0.004)
        c = chord_at(bar, st)
        note = (third_below(n, c) if harm else n) + oct_ + tr(bar)
        dur_s = int(ln * S16 * 0.92)
        vel = int(np.clip(rng.normal(104 if st in (0, 3, 6, 8) else 94, 5) * gain, 40, 127))
        sf_parts[part].append((p, dur_s, note, vel))
        T.add('bow', p, bow_layer(rng, note, dur_s / SR, vel / 127 * gain), 1.0, 0.2 if part == 'fiddle' else -0.35)


def play_hurdy(bar, m, gain=1.0, oct_=0):
    for st, ln, n in m:
        p = pos(bar, st, 0.0, 0.003)
        T.add('hurdy', p, hurdy_note(rng, n + oct_ + tr(bar), ln * S16 / SR * 0.95, gain * rng.uniform(0.92, 1.0)), 1.0, 0.05)


# ------------------------------------------------------------------ MELODIC LAYERS
for bar in range(1, 49):
    s = sec(bar)
    # lute hook
    if bar in lead and s in ('intro', 'drop1'):
        play_lute(bar, lead[bar], 1.0)
    # fiddle hook
    if bar in lead and (bar >= 5):
        play_fiddle(bar, lead[bar])
    if s in ('drop2', 'final') and bar in lead:
        play_fiddle(bar, lead[bar], 'fiddle2', 0.8, harm=True)
        for st, ln, n in COUNTER[(bar - 1) % 4]:
            sf_parts['recorder'].append((pos(bar, st, 0, 0.004), int(ln * S16 * 0.95), n + tr(bar), 88))
    if s == 'final' and bar in lead:
        play_hurdy(bar, lead[bar], 0.8, oct_=-12)
    # variation section call & response
    if bar in CALL:
        play_fiddle(bar, CALL[bar])
    if bar in ANSWER:
        play_lute(bar, ANSWER[bar], 1.1)
    if bar == 23:
        play_fiddle(23, TIE23); play_lute(23, TIE23, 0.9)
    if bar == 24:
        play_fiddle(24, FILL24); play_lute(24, FILL24, 1.0)
        play_hurdy(24, FILL24, 0.7, -12)
    # twist
    if bar in TW_H:
        play_hurdy(bar, TW_H[bar], 1.0)
        if bar in (39, 40):
            play_fiddle(bar, TW_H[bar], gain=0.9)
    if bar in TW_L:
        play_lute(bar, TW_L[bar], 1.1)
    if bar == 36:
        root, tones = CH['A']
        for n in tones + [tones[0] + 12]:
            T.add('lute', pos(36, 0), lute_note(rng, n, 0.3, 0.7, 0.8), 1.0, -0.2)
    # ending
    if bar == 48:
        play_fiddle(48, END48); play_fiddle(48, END48, 'fiddle2', 0.8, oct_=-12)
        play_hurdy(48, END48, 0.9, -12)
        for st, c, ln in [(0, 'Bb', 1), (3, 'Bb', 1), (6, 'A', 6), (12, 'D5', 4)]:
            root, tones = CH[c]
            for k, n in enumerate(tones + [tones[0] + 12]):
                T.add('lute', pos(48, st) + k * 180, lute_note(rng, n + 2, ln * S16 / SR, 0.75, 0.8), 1.0, -0.3 + 0.2 * k)

# lute 16th arpeggio drive (drop2 + final)
ARP = [0, 2, 1, 2, 3, 2, 1, 2, 0, 2, 1, 2, 3, 2, 1, 2]
ACC = {0, 3, 6, 8, 11, 14}
for bar in list(range(25, 33)) + list(range(41, 48)):
    for st in range(16):
        c = chord_at(bar, st)
        root, tones = CH[c]
        pool = [tones[0] - 12, tones[1] - 12, tones[2] - 12, tones[0]]
        n = pool[ARP[st]] + tr(bar)
        v = 0.55 if st in ACC else 0.32
        T.add('lutearp', pos(bar, st, 0.08, 0.002), lute_note(rng, n, 0.11, v, 0.5), 1.0, 0.35)

# ------------------------------------------------------------------ BASS
P1 = [(2, 2, 0), (5, 1, 0), (6, 2, 12), (10, 2, 0), (13, 1, 0), (14, 2, 7)]
P2 = [(st, 1, (12 if st in (3, 7, 11, 15) else 0)) for st in range(16) if st % 4 != 0]
PB = [(2, 2, 0), (6, 1, 0), (7, 1, 12), (10, 2, 0), (14, 2, 0)]
LICK = [(12, 1, 12), (13, 1, 10), (14, 1, 7), (15, 1, 4)]


def bass_hit(bar, st, ln, note, v=1.0, cutoff=1.0, sub=1.0):
    p = pos(bar, st, 0.03, 0.0015)
    mid, subw = bass_note(rng, note, ln * S16 / SR * 0.9, v * rng.uniform(0.93, 1.0), cutoff, sub)
    T.add('bass', p, mid, 1.0, 0.0)
    T.add('sub', p, subw, 1.0, 0.0)


for bar in range(1, 49):
    s = sec(bar)
    pat = None; cut = 1.0; sub = 1.0
    if bar < 5:
        pat, cut, sub = P1, 0.28 + 0.03 * bar, 0.0
    elif s == 'intro':
        pat, cut, sub = P1, 0.4 + 0.1 * (bar - 5), 0.35 * (bar - 4) / 4
        if bar == 8:
            pat = [x for x in P1 if x[0] < 12]
    elif s in ('drop1',):
        pat = P1
    elif s == 'var':
        pat = PB
    elif s in ('drop2', 'final'):
        pat = P2
    elif s == 'twist':
        if bar in (33, 34, 35):
            pat, cut = P1, 0.45
        elif bar == 36:
            pat = [(0, 2, 0)]
        else:
            pat, cut = P2, 0.4 + 0.25 * (bar - 37)
    if bar == 48:
        for st, c, ln in [(0, 'Bb', 1), (3, 'Bb', 1), (6, 'A', 5), (12, 'D5', 4)]:
            bass_hit(48, st, ln, CH[c][0] + 2, 1.1)
        continue
    has_lick = bar in lead and lead[bar] is H2d
    for st, ln, iv in pat:
        if has_lick and st >= 12:
            continue
        if bar in (8, 24, 32) and st >= 14:
            continue
        if bar == 40 and st >= 12:
            continue
        root = CH[chord_at(bar, st)][0] + tr(bar)
        bass_hit(bar, st, ln, root + iv, 1.0, cut, sub)
    if has_lick:
        root = CH[chord_at(bar, 12)][0] + tr(bar)
        for st, ln, iv in LICK:
            bass_hit(bar, st, ln, root + iv, 1.1, 1.3)
    if bar in ANSWER:  # bass doubles the lute answer two octaves down
        for st, ln, n in ANSWER[bar]:
            bass_hit(bar, st, ln, n - 24, 0.95, 1.2)
    if bar == 24:
        for st, ln, n in FILL24:
            bass_hit(24, st, ln, n - 24, 1.1, 1.3)

# ------------------------------------------------------------------ HARMONY LAYERS
for bar in list(range(25, 33)) + list(range(41, 48)):
    for st in (2, 6, 10, 14):
        if bar == 32 and st == 14:
            continue
        root, tones = CH[chord_at(bar, st)]
        notes = [x + tr(bar) for x in tones] + [tones[0] - 12 + tr(bar)]
        T.add('stabs', pos(bar, st, 0.03), supersaw(rng, notes, 0.11, 1.0, 5000, 1200, 0.05), 1.0)

for bar in range(33, 41):
    root, tones = CH[chord_at(bar, 0)]
    dur = BAR / SR
    if bar == 36:
        dur = 0.3
    T.add('pad', pos(bar, 0), supersaw(rng, [x - 12 for x in tones] + [tones[0]], dur, 1.0, 900 + 150 * (bar - 33), 600 + 120 * (bar - 33), 0.6, 0.05, 0.25), 1.0)

# hurdy-gurdy drones + chien buzz
for b0, b1, notes in [(25, 33, [50, 57]), (33, 39, [38, 45, 50]), (41, 48, [52, 59])]:
    n = (b1 - b0) * BAR
    d = drone(rng, notes, n, 1.0)
    fade = np.minimum(1, np.minimum(np.arange(n) / 2000, (n - np.arange(n)) / 4000))
    if b0 == 33:
        d[3 * BAR + 2 * S16:4 * BAR] *= 0.6  # bar 36 break: drone breathes on
    T.add('drone', pos(b0, 0), d * fade, 1.0)
for bar in list(range(25, 33)) + list(range(33, 41)) + list(range(41, 48)):
    steps = (2, 6, 10, 14) if sec(bar) != 'twist' else (6, 14)
    if bar in (36, 39, 40):
        continue
    for st in steps:
        if bar == 32 and st == 14:
            continue
        T.add('buzz', pos(bar, st, 0.0, 0.002), chien_buzz(rng, 62 + tr(bar), rng.uniform(0.8, 1.0)), 1.0, -0.1)

# ------------------------------------------------------------------ DRUMS & PERCUSSION
KICKS = []
for bar in range(1, 49):
    steps = [0, 4, 8, 12]
    if bar in (8, 24, 32, 40):
        steps = [0, 4, 8]
    if bar == 16:
        steps = [0, 4, 8, 12, 14]
    if bar == 36:
        steps = [0]
    if bar == 48:
        steps = [0, 3, 6, 12]
    for st in steps:
        p = pos(bar, st)
        v = 1.0 if sec(bar) not in ('intro',) else 0.9
        T.add('kick', p, kick(rng, v * (1.15 if (bar == 48 and st == 12) else 1.0)), 1.0)
        KICKS.append(p)

for bar in range(1, 49):
    s = sec(bar)
    drop = s in ('drop1', 'drop2', 'final')
    # ---- clap / backbeat
    clap_on = s in ('intro', 'drop1', 'drop2', 'final') or bar in (21, 22, 23, 37, 38)
    if bar == 48:
        clap_on = False
    if clap_on:
        for st in (4, 12):
            if bar in (8, 32) and st == 12:
                continue
            T.add('clap', pos(bar, st, 0, 0.001), clap(rng, rng.uniform(0.92, 1.0)), 1.0, 0)
            if drop:
                T.add('frame', pos(bar, st), frame_drum(rng, 0.8), 1.0, 0)
    if bar in (17, 18, 19, 20):
        T.add('frame', pos(bar, 12), frame_drum(rng, 0.9), 1.0, 0)
        T.add('frame', pos(bar, 4), frame_drum(rng, 0.7), 1.0, 0)
    if bar in (33, 34, 35):
        T.add('frame', pos(bar, 12), frame_drum(rng, 0.75), 1.0, 0)
    # ---- clap rolls / fills
    if bar == 16:
        for st in (14, 15):
            T.add('clap', pos(16, st), clap(rng, 0.7), 1.0, 0)
    if bar == 24:
        for k, st in enumerate([0, 2, 4, 6, 8, 9, 10, 11, 12, 13]):
            T.add('clap', pos(24, st), clap(rng, 0.45 + 0.055 * k), 1.0, 0)
            T.add('frame', pos(24, st), frame_drum(rng, 0.4 + 0.05 * k), 1.0, 0)
    if bar == 39:
        for k, st in enumerate(range(0, 16, 2)):
            T.add('clap', pos(39, st), clap(rng, 0.35 + 0.04 * k), 1.0, 0)
    if bar == 40:
        for k, st in enumerate(range(0, 12)):
            T.add('clap', pos(40, st), clap(rng, 0.55 + 0.04 * k), 1.0, 0)
            T.add('frame', pos(40, st), frame_drum(rng, 0.35 + 0.05 * k), 1.0, 0)
    # ---- stomps
    if s == 'intro':
        for st in ([0, 8] + ([6] if bar % 2 == 0 else [14])):
            if bar == 8 and st >= 12:
                continue
            T.add('stomp', pos(bar, st, 0.08, 0.002), stomp(rng, 0.9 if st in (0, 8) else 0.7), 1.0, 0)
    if bar in (23, 24, 31, 47):
        for st in (0, 3, 6, 8, 11):
            T.add('stomp', pos(bar, st), stomp(rng, 1.0), 1.0, 0)
    if bar == 48:
        for st in (0, 3, 6, 12):
            T.add('stomp', pos(48, st), stomp(rng, 1.0), 1.0, 0)
    # ---- hats
    if drop:
        for st in range(16):
            if bar in (8, 24, 32, 40) and st >= 14:
                continue
            v = 0.5 if st % 4 == 2 else (0.32 if st % 2 else 0.4)
            T.add('hat', pos(bar, st, 0.1, 0.0015), hat(rng, v * rng.uniform(0.85, 1.0)), 1.0, -0.18)
    if drop or bar in (5, 6, 7, 8):
        for st in (2, 6, 10, 14):
            if bar in (8, 24, 32) and st >= 14:
                continue
            T.add('ohat', pos(bar, st, 0.0, 0.001), hat(rng, 0.55 if drop else 0.35, 0.16), 1.0, 0.15)
    if bar in (37, 38, 39, 40):
        for st in range(0, 16, 2):
            if bar == 40 and st >= 12:
                continue
            T.add('hat', pos(bar, st, 0, 0.0015), hat(rng, 0.35), 1.0, -0.18)
    # ---- tambourine
    if bar != 36 and bar != 48:
        for st in range(16):
            if bar in (8, 24, 32) and st >= 14:
                continue
            if bar == 40 and st >= 12:
                continue
            if s == 'intro' or s == 'twist':
                if st % 2:
                    continue
                v = 0.75 if st % 4 == 2 else 0.4
            else:
                v = 0.6 if st % 4 == 2 else (0.25 if st % 2 else 0.35)
            if st == 0:
                v = 0.9  # bar accent hit
            T.add('tamb', pos(bar, st, 0.1, 0.002), tamb(rng, v * rng.uniform(0.85, 1.0), 0.09 if st == 0 else 0.06), 1.0, 0.4)
    # ---- shaker
    if s in ('drop2', 'final', 'twist') and bar not in (36, 48):
        for st in range(16):
            if bar in (32,) and st >= 14:
                continue
            if bar == 40 and st >= 12:
                continue
            T.add('shaker', pos(bar, st, 0.12, 0.002), shaker(rng, (0.5 if st % 2 == 0 else 0.3) * rng.uniform(0.8, 1.0)), 1.0, -0.45)
    # ---- hand drums (darbuka): doum / tek / ka
    if bar >= 5 and bar not in (36, 48):
        doums = [0, 6, 10]
        teks = [3, 8, 14]
        if s == 'var':
            doums = [0, 6, 10, 11]; teks = [2, 3, 8, 13, 14]
        for st in doums:
            if bar in (8, 24, 32, 40) and st >= 12:
                continue
            T.add('doum', pos(bar, st, 0.1, 0.002), doum(rng, (1.0 if st == 0 else 0.75) * rng.uniform(0.9, 1.0)), 1.0, 0)
        for k, st in enumerate(teks):
            if bar in (8, 24, 32, 40) and st >= 12:
                continue
            T.add('tek', pos(bar, st, 0.1, 0.002), tek(rng, 0.8 * rng.uniform(0.85, 1.0)), 1.0, 0.3 if k % 2 else -0.3)
        for st in range(1, 16, 2):
            if rng.uniform() < (0.55 if s == 'var' else 0.35):
                if bar in (8, 24, 32, 40) and st >= 12:
                    continue
                T.add('tek', pos(bar, st, 0.1, 0.002), tek(rng, rng.uniform(0.2, 0.35), 2400), 1.0, rng.uniform(-0.4, 0.4))
    # fills: darbuka rolls
    if bar in (8, 16, 24, 32, 40):
        start = 8 if bar != 40 else 4
        endst = 14 if bar in (8, 24, 32) else (12 if bar == 40 else 16)
        sts = np.arange(start, endst, 0.5 if bar in (24, 40) else 1.0)
        for k, st in enumerate(sts):
            T.add('tek', pos(bar, float(st)), tek(rng, 0.4 + 0.6 * k / len(sts)), 1.0, -0.35 + 0.7 * (k % 2))
            if st == int(st) and int(st) % 4 == 0:
                T.add('doum', pos(bar, float(st)), doum(rng, 0.9), 1.0, 0)
    if bar == 48:
        for k, st in enumerate(np.arange(8, 12, 0.5)):
            T.add('tek', pos(48, float(st)), tek(rng, 0.45 + 0.08 * k), 1.0, -0.3 + 0.6 * (k % 2))
            T.add('doum', pos(48, float(st)), doum(rng, 0.35 + 0.08 * k), 1.0, 0)
    # ---- woodblock clacks (walk cycles / tick-tock)
    if s == 'intro':
        for st, f0, pn in [(2, 1250, 0.5), (10, 930, -0.5)]:
            T.add('wood', pos(bar, st, 0, 0.001), woodblock(rng, f0, 0.8), 1.0, pn)
    if s == 'var':
        for k, st in enumerate((0, 3, 6)):
            T.add('wood', pos(bar, st, 0, 0.001), woodblock(rng, 1250 if k % 2 == 0 else 930, 0.6), 1.0, 0.5 if k % 2 == 0 else -0.5)
    if s == 'twist':
        for k, st in enumerate((2, 6, 10, 14)):
            if bar == 40 and st >= 12:
                continue
            T.add('wood', pos(bar, st, 0, 0.001), woodblock(rng, 1250 if k % 2 == 0 else 930, 0.55), 1.0, 0.5 if k % 2 == 0 else -0.5)
        if bar == 36:
            for k, st in enumerate((4, 6, 8, 10)):
                T.add('wood', pos(36, st), woodblock(rng, 1250 if k % 2 == 0 else 930, 0.9), 1.0, 0.5 if k % 2 == 0 else -0.5)
    # ---- zills: bar accents
    if (drop and (bar % 2 == 1 or s == 'final')) or bar in (17, 21, 33, 37):
        T.add('zills', pos(bar, 0), zills(rng, 0.9), 1.0, 0.3 if bar % 4 == 1 else -0.3)
    if bar == 36:
        T.add('zills', pos(36, 0), zills(rng, 1.0), 1.0, 0)

# ------------------------------------------------------------------ FX / transitions
for b in (9, 25, 41):
    T.add('crash', pos(b, 0), crash(rng, 0.9), 1.0)
    T.add('impact', pos(b, 0), impact(rng, 1.0), 1.0)
    rv = crash(rng, 0.6, SPB / SR)[::-1].copy()
    T.add('fx', pos(b, 0) - len(rv), rv, 1.0)
for b in (17, 33):
    T.add('crash', pos(b, 0), crash(rng, 0.55), 1.0)
    T.add('impact', pos(b, 0), impact(rng, 0.6), 1.0)
for b in (5, 13, 21, 29, 37, 45):   # 7.5 s developments
    T.add('crash', pos(b, 0), crash(rng, 0.35, 1.2), 1.0)
T.add('crash', pos(48, 12), crash(rng, 1.0, 1.0), 1.0)
T.add('impact', pos(48, 12), impact(rng, 1.1), 1.0)
T.add('zills', pos(48, 12), zills(rng, 1.2), 1.0)
for b_end, nbars, v in [(9, 2, 0.6), (17, 1, 0.4), (25, 2, 0.7), (41, 2, 0.75)]:
    ln = nbars * BAR - 2 * S16
    T.add('fx', pos(b_end, 0) - 2 * S16 - ln, riser(rng, ln / SR, v), 1.0)
T.add('fx', pos(33, 0), downlifter(rng, 2 * BAR / SR, 0.5), 1.0)
T.add('fx', pos(48, 6), riser(rng, 6 * S16 / SR, 0.5), 1.0)

# ------------------------------------------------------------------ SAMPLE-BASED PARTS (FluidSynth)
PROG = {'fiddle': 40, 'fiddle2': 40, 'recorder': 74, 'nylon': 24}
ANTICIP = {"fiddle": 0.015, "fiddle2": 0.015, 'recorder': 0.012, 'nylon': 0.004}


def render_sf(name, notes):
    mid = mido.MidiFile(ticks_per_beat=960)
    tk = mido.MidiTrack(); mid.tracks.append(tk)
    tk.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM)))
    tk.append(mido.Message('program_change', program=PROG[name], time=0))
    tk.append(mido.Message('control_change', control=7, value=110, time=0))
    tk.append(mido.Message('control_change', control=91, value=0, time=0))
    tk.append(mido.Message('control_change', control=93, value=0, time=0))
    ev = []
    for p, d, n, v in notes:
        a = int(round(p / (SPB / 960))); b = int(round((p + d) / (SPB / 960)))
        ev.append((a, 1, n, v)); ev.append((max(a + 1, b), 0, n, 0))
    ev.sort(key=lambda e: (e[0], e[1]))
    last = 0
    for t, on, n, v in ev:
        tk.append(mido.Message('note_on' if on else 'note_off', note=int(n), velocity=int(v), time=t - last))
        last = t
    path = os.path.join(WORK, name + '.mid'); mid.save(path)
    wav = os.path.join(WORK, name + '.wav')
    subprocess.run(['fluidsynth', '-ni', '-R', '0', '-C', '0', '-g', '0.6', '-r', '48000',
                    '-o', 'audio.file.format=float', '-F', wav, SF2, path], check=True, capture_output=True)
    y, sr = sf.read(wav)
    assert sr == SR
    shift = int((0.0045 + ANTICIP[name]) * SR)
    y = y[shift:]
    out = np.zeros((N + TAIL, 2)); m = min(len(y), len(out)); out[:m] = y[:m]
    return out


def build():
    for name, notes in sf_parts.items():
        if notes:
            T[name] = render_sf(name, notes)
    return T, KICKS


if __name__ == '__main__':
    build()
    print({k: float(np.abs(v).max()) for k, v in T.items()})
