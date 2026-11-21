"""
Composition: "Skybound" — original cinematic-electronic cue, 60 s.

Everything musical lives here as plain data (beats, MIDI pitches, velocities).
The renderer (build.py) turns it into audio; midi_export turns it into MIDI.

Key: D minor -> lifts to E minor for the finale, ends on E major (Picardy third).
Tempo: 144 BPM, 4/4. 36 bars x 1.6667 s = 60.000 s exactly.
"""
from dataclasses import dataclass, field
import numpy as np

BPM = 144.0
SPB = 60.0 / BPM            # seconds per beat
BAR = 4                     # beats per bar
N_BARS = 36
DURATION = N_BARS * BAR * SPB   # 60.0
SEED = 20261121

_PC = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
       'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def nm(name: str) -> int:
    """'C#5' -> 73"""
    p, o = (name[:2], name[2:]) if len(name) > 2 and name[1] in '#b' else (name[0], name[1:])
    return 12 * (int(o) + 1) + _PC[p]


def beat_to_sec(b: float) -> float:
    return b * SPB


@dataclass
class Note:
    start: float   # beats
    dur: float     # beats
    pitch: int     # MIDI
    vel: int       # 1..127


@dataclass
class Score:
    parts: dict = field(default_factory=dict)      # name -> [Note]
    drums: dict = field(default_factory=dict)      # name -> [(beat, vel)]
    fx: list = field(default_factory=list)         # dicts
    cc: dict = field(default_factory=dict)         # part -> [(beat, cc, value)]
    pad: list = field(default_factory=list)        # (start, dur, [pitches], vel, cutoff_hz, attack_s)
    sections: list = field(default_factory=list)
    chords: list = field(default_factory=list)

    def add(self, part, start, dur, pitch, vel):
        self.parts.setdefault(part, []).append(Note(start, dur, int(pitch), int(np.clip(vel, 1, 127))))

    def hit(self, drum, beat, vel):
        self.drums.setdefault(drum, []).append((beat, int(np.clip(vel, 1, 127))))


# --------------------------------------------------------------------------- harmony
PROG = (['Dm', 'Bb', 'F', 'C'] * 3 + ['Dm', 'Bb', 'F', 'A'] +      # bars 0-15
        ['Bb', 'Gm', 'Eb', 'A'] +                                  # 16-19 breakdown (Eb = Neapolitan)
        ['Dm', 'Bb', 'F', 'C'] + ['Dm', 'Bb', 'F', 'A'] +          # 20-27 climax
        ['C', 'D'] +                                               # 28-29 lift (bVI-bVII of E minor)
        ['Em', 'C', 'G', 'D'] +                                    # 30-33 finale, up a whole step
        ['E', 'E'])                                                # 34-35 Picardy ending
assert len(PROG) == N_BARS


def chord_pcs(sym):
    minor = sym.endswith('m')
    root = _PC[sym[:-1] if minor else sym]
    return root, [root, (root + (3 if minor else 4)) % 12, (root + 7) % 12]


def bass_note(sym):
    """Root placed in G1..F#2 (31..42)."""
    r, _ = chord_pcs(sym)
    m = 24 + r
    while m < 31:
        m += 12
    return m


def voice_lead(pcs, prev, lo=57, hi=74):
    """Closest triad voicing (to the previous one) inside [lo, hi]."""
    cands = []
    for base in range(lo, hi):
        if base % 12 not in pcs:
            continue
        v = sorted({base} | {next(m for m in range(base + 1, base + 13) if m % 12 == pc)
                             for pc in pcs if pc != base % 12})
        if v[-1] <= hi + 4:
            cands.append(v)
    if prev is None:
        return min(cands, key=lambda v: abs(np.mean(v) - (lo + hi) / 2))
    return min(cands, key=lambda v: sum(abs(a - b) for a, b in zip(v, prev)))


# --------------------------------------------------------------------------- melodic cells
R332 = [(0, .75), (.75, .75), (1.5, .5), (2, .75), (2.75, .75), (3.5, .5)]   # the hook rhythm


def cell(pitches, rhythm=R332):
    out = []
    for (s, d), p in zip(rhythm, pitches):
        out.append((s, d, nm(p)))
    return out


HOOK = {   # degree cells in D minor
    'i':   cell(['A4', 'D5', 'F5', 'E5', 'D5', 'C5']),
    'VI':  [(0, .75, nm('D5')), (.75, .75, nm('F5')), (1.5, 1.5, nm('A5')), (3, .5, nm('G5')), (3.5, .5, nm('F5'))],
    'III': cell(['C5', 'F5', 'A5', 'G5', 'F5', 'E5']),
    'VII': [(0, .75, nm('G5')), (.75, .75, nm('E5')), (1.5, .5, nm('C5')), (2, .75, nm('D5')), (2.75, 1.25, nm('E5'))],
    'V':   [(0, .75, nm('C#5')), (.75, .75, nm('E5')), (1.5, 1.5, nm('A5')), (3, .5, nm('G5')), (3.5, .5, nm('E5'))],
    'lift1': cell(['E5', 'G5', 'C6', 'B5', 'G5', 'E5']),
    'lift2': [(0, .75, nm('F#5')), (.75, .75, nm('A5')), (1.5, .5, nm('D6')), (2, .75, nm('E6')), (2.75, 1.25, nm('F#6'))],
}
BREAK = {  # breakdown motif (same rhythm, new harmony) for piano/celesta
    'Bb': cell(['F4', 'Bb4', 'D5', 'C5', 'Bb4', 'F4']),
    'Gm': cell(['D4', 'G4', 'Bb4', 'A4', 'G4', 'D4']),
    'Eb': cell(['G4', 'Bb4', 'Eb5', 'D5', 'Bb4', 'G4']),
    'A':  [(0, .75, nm('E4')), (.75, .75, nm('A4')), (1.5, 1.9, nm('C#5'))],   # ends early -> silence before drop
}
COUNTER = {  # horn / brass counter-line
    'i':   [(0, 1.5, nm('D4')), (1.5, 2.5, nm('A4'))],
    'VI':  [(0, 1.5, nm('Bb4')), (1.5, 1, nm('A4')), (2.5, 1.5, nm('F4'))],
    'III': [(0, 1.5, nm('A4')), (1.5, 2.5, nm('C5'))],
    'VII': [(0, 3, nm('G4')), (3, 1, nm('E4'))],
    'V':   [(0, 1.5, nm('A4')), (1.5, 2.5, nm('C#5'))],
    'lift1': [(0, 1.5, nm('G4')), (1.5, 2.5, nm('C5'))],
    'lift2': [(0, 1.5, nm('A4')), (1.5, 1.5, nm('D5')), (3, 1, nm('F#5'))],
}
DEG = ['i', 'VI', 'III', 'VII']

# melody plan per bar: (cell, transpose) or None
MEL = ([(d, 0) for d in DEG] * 3 + [('i', 0), ('VI', 0), ('III', 0), ('V', 0)] +
       [None] * 4 +
       [(d, 0) for d in DEG] + [('i', 0), ('VI', 0), ('III', 0), ('V', 0)] +
       [('lift1', 0), ('lift2', 0)] +
       [(d, 2) for d in DEG] + [None, None])
assert len(MEL) == N_BARS

SECTIONS = [
    (0, 4, 'HOOK', 'Hook stated immediately: pluck + celesta over filtered supersaw, sub swell'),
    (4, 8, 'MOMENTUM', 'Kick, clap and rolling sidechained bass enter; hook repeats'),
    (8, 16, 'BUILD', 'Strings, horn counter-line, 16th hats, arp and supersaw lead join; stop-time stabs in bar 16'),
    (16, 20, 'BREAKDOWN', 'Drums drop; piano + choir; Neapolitan Eb chord; timpani roll and riser; silent 8th before drop'),
    (20, 30, 'CLIMAX', 'Full band: supersaw lead, brass counter-line, choir, big drums; C-D tom lift'),
    (30, 34, 'FINALE', 'Hook returns a whole step higher in E minor'),
    (34, 36, 'ENDING', 'Final E-major hit (Picardy third) and decay to silence'),
]


# --------------------------------------------------------------------------- arrangement
def compose() -> Score:
    rng = np.random.default_rng(SEED)
    S = Score(sections=SECTIONS, chords=PROG)
    hv = lambda v, s=6: v + rng.integers(-s, s + 1)      # humanised velocity

    # ---------------- melody layers
    for bar, plan in enumerate(MEL):
        if plan is None:
            continue
        name, tr = plan
        b0 = bar * BAR
        for (s, d, p) in HOOK[name]:
            accent = 1.0 if s in (0, 1.5, 2) else 0.88
            p = p + tr
            if bar < 16 or bar >= 20:   # pluck everywhere the hook plays
                base = 78 if bar < 4 else 88 if bar < 8 else 96
                S.add('pluck', b0 + s, d * 0.92, p, hv(base * accent))
            if bar < 8 or bar >= 30:
                S.add('celesta', b0 + s, d, p + 12, hv(62 if bar < 8 else 80))
            if 8 <= bar < 16:
                S.add('lead', b0 + s, d * 0.98, p, hv(70 * accent))
            if bar >= 20:
                S.add('lead', b0 + s, d * 0.98, p, hv(110 * accent))
                S.add('lead_hi', b0 + s, d * 0.98, p + 12, hv(80 * accent))
        # counter line
        cname = name
        if bar >= 8 and bar < 16:
            for (s, d, p) in COUNTER[cname]:
                S.add('horns', b0 + s, d, p + tr - 12, hv(68 if bar < 12 else 80))
        if bar >= 20:
            for (s, d, p) in COUNTER[cname]:
                S.add('brass', b0 + s, d, p + tr, hv(96))
                S.add('horns', b0 + s, d, p + tr - 12, hv(92))

    # final note
    S.add('lead', 34 * BAR, 6, nm('G#5'), 112)
    S.add('lead_hi', 34 * BAR, 6, nm('E6'), 84)
    S.add('celesta', 34 * BAR, 4, nm('G#6'), 90)
    S.add('celesta', 34 * BAR, 4, nm('E7'), 80)
    for p in ('E4', 'G#4', 'B4'):
        S.add('brass', 34 * BAR, 3.5, nm(p), 112)

    # breakdown piano + celesta
    for i, sym in enumerate(['Bb', 'Gm', 'Eb', 'A']):
        b0 = (16 + i) * BAR
        for (s, d, p) in BREAK[sym]:
            S.add('piano', b0 + s + rng.uniform(-.01, .01), d * 1.05, p, hv(70 if i < 3 else 82, 8))
            S.add('celesta', b0 + s, d, p + 12, hv(46))
        r = bass_note(sym)
        S.add('piano', b0, 3.4 if i == 3 else 4, r, 64)
        S.add('piano', b0, 3.4 if i == 3 else 4, r + 12, 58)

    # bar 15 stop-time stabs (A major) on brass
    for s, d in ((0, .5), (1.5, .5), (3, .9)):
        for p in ('E4', 'A4', 'C#5'):
            S.add('brass', 60 + s, d, nm(p), 104)

    # ---------------- harmony: pad (supersaw), strings, choir
    prev = None
    for bar, sym in enumerate(PROG):
        root, pcs = chord_pcs(sym)
        v = voice_lead(pcs, prev)
        prev = v
        b0 = bar * BAR
        if bar < 4:
            S.pad.append((b0, 4, v, 0.55, 700 + 600 * bar, 0.25))
        elif bar < 15:
            S.pad.append((b0, 4, v, 0.7 if bar < 8 else 0.8, 2600 if bar < 8 else 3600, 0.01))
        elif bar == 15:
            for s, d in ((0, .5), (1.5, .5), (3, .9)):
                S.pad.append((b0 + s, d, v, 0.85, 4000, 0.003))
        elif bar < 20:
            S.pad.append((b0, 3.5 if bar == 19 else 4, v, 0.45, 1100, 0.35))
        elif bar < 34:
            S.pad.append((b0, 4, v + [v[0] + 12], 0.9, 6500, 0.005))
        elif bar == 34:
            S.pad.append((b0, 5, v + [v[0] + 12], 0.95, 6500, 0.003))

        # strings: low root + voiced triad
        if 8 <= bar < 34 and bar != 15:
            vel = 62 if bar < 12 else 74 if bar < 16 else 70 if bar < 20 else 92
            dur = 3.5 if bar == 19 else 4.02
            S.add('strings', b0, dur, bass_note(sym) + 12, hv(vel))
            for p in v:
                S.add('strings', b0, dur, p, hv(vel - 4))
            if bar >= 20:
                S.add('strings', b0, dur, v[-1] + 12, hv(vel - 8))
        if bar == 15:
            for s, d in ((0, .5), (1.5, .5), (3, .9)):
                for p in [bass_note(sym) + 12] + v:
                    S.add('strings', b0 + s, d, p, 100)
        if 16 <= bar < 34:
            dur = 3.5 if bar == 19 else 4.02
            for p in v:
                S.add('choir', b0, dur, p, hv(68 if bar < 20 else 74))
        if bar == 34:
            for p in [40, 52, 56, 59, 64, 68, 71]:
                S.add('strings', b0, 3.5, p, 112)
            for p in (64, 68, 71):
                S.add('choir', b0, 3.5, p, 96)

    # tremolo strings swell into the drop (bars 18-19)
    for bar in (18, 19):
        root, pcs = chord_pcs(PROG[bar])
        for p in voice_lead(pcs, None, 50, 66):
            S.add('tremolo', bar * BAR, 4 if bar == 18 else 3.5, p, 100)
    S.cc['tremolo'] = [(72 + i * 0.25, 11, int(30 + 97 * (i / 31) ** 1.6)) for i in range(32)]
    S.cc['strings'] = []
    for start in range(32, 64, 8):          # slow two-bar swells in BUILD
        S.cc['strings'] += [(start + i * .5, 11, int(80 + 40 * np.sin(np.pi * i / 16))) for i in range(16)]
    S.cc['strings'] += [(64, 11, 100), (80, 11, 120)]

    # ---------------- timpani
    def timp(beat, p, v):
        S.add('timpani', beat, 1.0, p, v)
    for bar in (16, 17, 18):
        timp(bar * BAR, bass_note(PROG[bar]) + 12, 92)
    for i in range(28):                         # roll on A, bar 19, 32nds crescendo (stops before the gap)
        timp(76 + i * 0.125, 45, int(28 + 90 * (i / 27) ** 1.4))
    timp(80, 50, 120); timp(80, 38, 110)
    timp(112, 48, 100)
    for i in range(32):                         # roll on D, bar 29
        timp(116 + i * 0.125, 50, int(40 + 80 * (i / 31) ** 1.3))
    timp(120, 52, 122); timp(120, 40, 112)
    timp(136, 52, 127); timp(136, 40, 120)

    # ---------------- bass
    for bar, sym in enumerate(PROG):
        r = bass_note(sym)
        b0 = bar * BAR
        if bar < 4:
            S.add('bass', b0, 4.0, r, 70)
        elif bar == 15:
            for s, d in ((0, .5), (1.5, .5), (3, .9)):
                S.add('bass', b0 + s, d, r, 120)
        elif 16 <= bar < 20:
            S.add('bass', b0, 3.5 if bar == 19 else 4.0, r, 74)
        elif bar < 34:
            drive = 88 if bar < 8 else 102 if bar < 20 else 118
            for beat in range(4):
                for k in (1, 2, 3):
                    p = r + (12 if (beat == 3 and k == 3) else 0)
                    S.add('bass', b0 + beat + k * .25, .22, p, hv(drive - (10 if k == 2 else 0), 4))
        elif bar == 34:
            S.add('bass', b0, 5.0, r, 124)

    # ---------------- arp (16ths, chord tones over two octaves)
    for bar, sym in enumerate(PROG):
        if not (8 <= bar < 15 or 20 <= bar < 34):
            continue
        root, pcs = chord_pcs(sym)
        tones = sorted(set(m for m in range(nm('A4'), nm('A6')) if m % 12 in pcs))
        pattern = [0, 1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4, 3, 2, 3]
        for i, idx in enumerate(pattern):
            p = tones[min(idx, len(tones) - 1)]
            S.add('arp', bar * BAR + i * .25, .2, p, hv(78 if i % 4 == 0 else 58, 5))

    # ---------------- drums
    for bar in range(N_BARS):
        b0 = bar * BAR
        groove = (4 <= bar < 15) or (20 <= bar < 34)
        if groove:
            for beat in range(4):
                if bar == 29 and beat >= 2:
                    continue
                S.hit('kick', b0 + beat, hv(118 if bar >= 20 else 108 if bar >= 8 else 98, 3))
            for beat in (1, 3):
                if bar in (29,):
                    continue
                S.hit('snare', b0 + beat, hv(112 if bar >= 20 else 102 if bar >= 8 else 90, 4))
                S.hit('clap', b0 + beat + 0.004, hv(104 if bar >= 20 else 92, 6))
            # hats
            if bar < 8:
                for e in range(8):
                    S.hit('hat_c', b0 + e * .5, hv(70 if e % 2 else 50))
            else:
                for s in range(16):
                    S.hit('hat_c', b0 + s * .25, hv([62, 34, 48, 34][s % 4], 6))
            for beat in range(4):
                S.hit('hat_o', b0 + beat + .5, hv(58 if bar < 20 else 66))
            if bar >= 20:   # ghost snares
                for g in (1.75, 3.25):
                    S.hit('snare', b0 + g, hv(30, 6))
        # transitions & fills
        if bar in (7, 11, 23):
            for i, t in enumerate(['tom_h', 'tom_h', 'tom_m', 'tom_l']):
                S.hit(t, b0 + 3 + i * .25, 90 + i * 8)
        if bar == 27:
            for i in range(8):
                S.hit('snare', b0 + 2 + i * .25, 60 + i * 8)
    # intro pickup and hats
    for e in range(4, 8):
        S.hit('hat_c', 8 + e * .5, 26 + e * 4)
    for e in range(8):
        S.hit('hat_c', 12 + e * .5, 40 + e * 3)
    for i in range(8):
        S.hit('snare', 14 + i * .25, 30 + i * 7)
    # bar 15 stop-time hits
    for s in (0, 1.5, 3):
        S.hit('kick', 60 + s, 124); S.hit('snare', 60 + s, 110); S.hit('crash', 60 + s, 80 if s < 3 else 100)
    # breakdown heartbeat
    for bar in (16, 17, 18):
        S.hit('kick', bar * BAR, 96)
        S.hit('kick', bar * BAR + 1.5, 60)
    # build into drop: snare roll bar 18-19
    for i in range(8):
        S.hit('snare', 72 + i * .5, 30 + i * 5)
    for i in range(8):                          # bar 19: 16ths then 32nds, stop at the silent 8th
        S.hit('snare', 76 + i * .25, 66 + i * 3)
    for i in range(12):
        S.hit('snare', 78 + i * .125, 90 + i * 3)
    # bar 28-29 tom lift
    for bar in (28, 29):
        for e in range(8):
            t = ['tom_l', 'tom_m'][e % 2]
            S.hit(t, bar * BAR + e * .5, 100 if e % 4 == 0 else 78)
    for i in range(16):
        S.hit('snare', 118 + i * .125, 60 + i * 4)
    for b in (116, 117):
        S.hit('kick', b, 118)
    # bar 33 fill into ending
    for i, t in enumerate(['tom_h', 'tom_h', 'tom_m', 'tom_m', 'tom_l', 'tom_l', 'snare', 'snare']):
        S.hit(t, 134 + i * .25, 96 + i * 3)
    # crashes
    for b, v in ((16, 70), (32, 100), (80, 124), (96, 104), (112, 104), (120, 124), (136, 127)):
        S.hit('crash', b, v)
    S.hit('kick', 136, 127)
    S.hit('snare', 136, 110)

    # ---------------- fx
    for b, size in ((0, .55), (16, .45), (32, .6), (64, .9), (80, 1.0), (112, .7), (120, 1.0), (136, 1.0)):
        S.fx.append(dict(kind='impact', beat=b, size=size))
    for a, b, lvl in ((8, 16, .5), (28, 32, .45), (68, 79.5, 1.0), (112, 120, .8)):
        S.fx.append(dict(kind='riser', beat=a, end=b, size=lvl))
    S.fx.append(dict(kind='downlifter', beat=64, end=72, size=.8))
    S.fx.append(dict(kind='downlifter', beat=136, end=142, size=.6))
    for b in (32, 80, 120):
        S.fx.append(dict(kind='revcym', beat=b - 4, end=b - (0.5 if b == 80 else 0), size=.7))
    S.fx.append(dict(kind='subdrop', beat=80, size=1.0))
    S.fx.append(dict(kind='subdrop', beat=136, size=1.0))
    S.fx.append(dict(kind='subdrop', beat=64, size=.7))

    for part in S.parts.values():
        part.sort(key=lambda n: n.start)
    return S


# --------------------------------------------------------------------------- cue points for the cue sheet
CUES = [
    (0, 'Impact + hook downbeat', 'Title card / first frame. Hook is the brand: put the logo or character reveal here.'),
    (16, 'Kick + bass drop in', 'First action beat / character starts moving.'),
    (32, 'Crash: BUILD begins', 'Scene change; new layer of the story.'),
    (48, 'Tom fill', 'Optional small visual accent (camera push).'),
    (60, 'Stop-time stab 1', 'Three synced band hits (bar 16): ideal for 3 quick cuts / punch-ins.'),
    (61.5, 'Stop-time stab 2', ''),
    (63, 'Stop-time stab 3', ''),
    (64, 'Impact + downlifter: BREAKDOWN', 'Emotional turn / problem revealed. Low density: best narration window.'),
    (72, 'Neapolitan Eb chord + tremolo swell', 'Tension rises; slow zoom.'),
    (79.5, 'Silent 8th note', 'Freeze frame / blackout before the reveal.'),
    (80, 'DROP: crash + sub drop + timpani', 'Main reveal / hero moment. Strongest sync point.'),
    (96, 'Crash: climax phrase 2', 'Second big action beat.'),
    (112, 'Tom lift C-D begins', 'Run-up / montage acceleration.'),
    (120, 'Key change to E minor', 'Final push / payoff scene.'),
    (134, 'Tom fill', 'Lead-in to end card.'),
    (136, 'Final E-major hit', 'End card / logo slam. Tail decays to silence at 60.0 s.'),
]
