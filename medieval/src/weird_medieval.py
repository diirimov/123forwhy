"""WEIRD MEDIEVAL JOBS - one 65 s medieval-folk x medieval-rave dance track.

Key: D Dorian (bright medieval minor, B natural) -> F major 'royal' -> D Phrygian 'dark' -> D Dorian finale.
Grid: 144 beats = exactly 65.000 s (132.92 BPM). Same section grid as the earlier candidates.

Hook (wooden flute):   "da-da DUM  da-da DUM  da-da-da-da DUM DUM"
Answer (hurdy-gurdy):  "DUM . . da DUM DUM  DUM . . da DUMMM"
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from medieval_inst import *  # noqa

INTRO, D1, BRK, S2, FAKE, S3, FIN, END = 0, 6, 42, 44, 80, 82, 118, 142
SW = dict(s16=0.54)


def bars(start, n):
    return [start + 4 * i for i in range(n)]


# ------------------------------------------------------------------ the melody book
A1 = "A4:1 D5:1 !F5:2 E5:1 D5:1 !A5:2 G5:1 F5:1 E5:1 D5:1 !C5:2 A4:2"
A1v = "A4:1 D5:1 !(G5)F5:2 E5:1 D5:1 !(B5)A5:2 G5:1 F5:1 E5:1 D5:1 !(D5)C5:2 A4:2"
A1x = "A4:1 D5:1 !F5:2 E5:1 D5:1 !A5:2 B5:1 A5:1 G5:1 F5:1 E5:1 F5:1 G5:1 E5:1"
B1 = "!E5:3 G5:1 E5:2 C5:2 !D5:3 E5:1 C5:4"
B1x = "!G5:3 A5:1 G5:2 E5:2 !F5:3 G5:1 E5:4"
A3 = "A4:1 D5:1 !G5:2 F5:1 G5:1 !B5:2 A5:1 G5:1 F5:1 E5:1 !D5:2 B4:2"
A3v = "A4:1 D5:1 !(A5)G5:2 F5:1 G5:1 !(C6)B5:2 A5:1 G5:1 F5:1 E5:1 !(E5)D5:2 B4:2"
B4 = "!C5:3 E5:1 D5:2 A4:2 !D5:6 r:2"
B4x = "!C5:3 E5:1 D5:2 A4:2 D5:1 E5:1 F5:1 G5:1 A5:1 B5:1 !C6:2"
TURN1 = "!D5:2 F5:2 Bb5:2 A5:2 !C6:2 B5:1 A5:1 G5:2 E5:2"

# royal (F major)
R1 = "C5:1 F5:1 !A5:2 G5:1 F5:1 !C6:2 Bb5:1 A5:1 G5:1 F5:1 !E5:2 C5:2"
R2 = "!G5:3 Bb5:1 G5:2 E5:2 !F5:3 G5:1 E5:4"
R3 = "C5:1 F5:1 !Bb5:2 A5:1 Bb5:1 !D6:2 C6:1 Bb5:1 A5:1 G5:1 !F5:2 D5:2"
R4 = "!E5:3 G5:1 F5:2 D5:2 !E5:6 r:2"
R6 = "!C6:3 D6:1 C6:2 G5:2 !A5:3 Bb5:1 G5:4"
R7 = "C5:1 F5:1 !Bb5:2 A5:1 Bb5:1 !D6:2 !C6:2 Bb5:1 A5:1 G5:2 E5:2"
R8 = "!F5:3 A5:1 G5:2 E5:2 !F5:6 r:2"
TURN2 = "G5:1 A5:1 Bb5:1 A5:1 G5:1 F5:1 E5:1 D5:1 !C#5:2 E5:2 A5:2 C#6:2"

# dark (D Phrygian)
K1 = "A4:1 D5:1 !F5:2 Eb5:1 D5:1 !A5:2 G5:1 F5:1 Eb5:1 D5:1 !C5:2 A4:2"
K2 = "!Eb5:3 G5:1 Eb5:2 C5:2 !D5:3 Eb5:1 C5:4"
K3 = "A4:1 D5:1 !F5:2 Eb5:1 F5:1 !Bb5:2 A5:1 G5:1 F5:1 Eb5:1 !D5:2 Bb4:2"
K4 = "!C#5:3 E5:1 D5:2 Bb4:2 !A4:6 r:2"
RUN3 = "D5:1 E5:1 F5:1 G5:1 A5:1 Bb5:1 C#6:1 D6:1 !E6:2 C#6:2 A5:2 E5:2"

ENDING = "!D6:3 !D6:3 !D6:2 C6:1 B5:1 A5:1 G5:1 F5:1 E5:1 D5:2"

DDOR = [nn('D4') + i for i in (0, 2, 3, 5, 7, 9, 10)]
FMAJ = [nn('F4') + i for i in (0, 2, 4, 5, 7, 9, 10)]


def dshift(n, steps, scale):
    sc = sorted(set(p % 12 for p in scale))
    pcs = sorted(p + 12 * o for o in range(0, 10) for p in sc)
    idx = max(i for i, p in enumerate(pcs) if p <= n)
    return pcs[idx + steps]


class Med(Song):
    def __init__(self):
        super().__init__('Weird Medieval Jobs', seed=1347)
        self.I = MInst(1347)

    # ---- players
    def flute(self, s, b, tr=0, vel=0.8, bus='flute', pan=0.08, gain=1.0, harm=0, scale=DDOR, cue=None):
        ev = seq(s, b, tr=tr, vel=vel)
        prev = None
        for e in ev:
            n = dshift(e['n'], harm, scale) if harm else e['n']
            gr = e['gr'] if not harm else None
            tt = self.t(e['t'], **SW) + self.rng.normal(0, 0.003)
            d = self.t(e['t'] + e['d'], **SW) - self.t(e['t'], **SW)
            y = self.I.flute(n, d, e['v'] * (1 + self.rng.normal(0, 0.03)), grace=gr, prev=prev, stac=e['stac'])
            self.place(bus, y, tt, pan, gain)
            prev = n
        if cue:
            self.cue(b, cue)

    def phrase(self, kind, s, b, tr=0, vel=0.85, bus=None, pan=0.0, gain=1.0, harm=0, scale=DDOR, cue=None, gap=0.0):
        ev = seq(s, b, tr=tr, vel=vel)
        bus = bus or {'pipe': 'pipes', 'hurdy': 'hurdy'}[kind]
        groups, cur = [], []
        for e in ev:
            if cur and abs(cur[-1]['t'] + cur[-1]['d'] - e['t']) > 1e-6:
                groups.append(cur); cur = []
            cur.append(e)
        if cur:
            groups.append(cur)
        for gph in groups:
            t0 = self.t(gph[0]['t'], **SW)
            notes = []
            for e in gph:
                n = dshift(e['n'], harm, scale) if harm else e['n']
                ts = self.t(e['t'], **SW) - t0
                te = self.t(e['t'] + e['d'], **SW) - t0 - (gap if e is gph[-1] else 0)
                if e['stac']:
                    te = ts + (te - ts) * 0.55
                gr = None if harm else e['gr']
                if kind == 'pipe' and gr is None and e['v'] >= 0.99 and not harm:
                    gr = n + 5  # bagpipe gracenote on accented notes
                notes.append((ts, te, n, gr, e['v']))
            total = notes[-1][1] + 0.1
            y = self.I.bagpipe(notes, total) if kind == 'pipe' else self.I.hurdy(notes, total)
            self.place(bus, y, t0, pan, gain)
        if cue:
            self.cue(b, cue)

    def chant(self, items, b, bus='chant', gain=1.0, pan=0.0, cue=True, **kw):
        """items: (step16, note, dur16, vowels)"""
        for step, note, d16, vw in items:
            tt = self.t(b + step / 4, **SW)
            y = self.I.chant(nn(note), d16 / 4 * SPB, 0.85, vowels=vw, cons='h', **kw)
            self.place(bus, y, tt, pan, gain)
            if cue and d16 <= 3:
                self.cue(b + step / 4, f'group shout "{vw.upper()}"', tsec=tt)

    def lute_arp(self, sym, b, pattern=(0, 2, 1, 2, 3, 2, 1, 2), acc=(0, 3, 6, 8, 11, 14), steps=16, gain=1.0, low=nn('D4')):
        notes = voicing(sym, low)
        pool = [notes[0] - 12, notes[0], notes[1], notes[-1]] if len(notes) >= 3 else notes
        for st in range(steps):
            n = pool[pattern[st % len(pattern)]]
            v = 0.85 if st in acc else 0.5
            y = self.I.lute(n, 0.12, v, bright=0.85, t60=0.7)
            self.place('lute', y, self.t(b + st / 4, **SW), -0.3, gain)

    def strum(self, pattern, sym, b, gain=1.0, low=nn('A3'), length=0.2):
        notes = voicing(sym, low) + [voicing(sym, low)[0] + 12]
        for k, (bt, v) in enumerate(hits(pattern, b)):
            up = k % 2 == 1
            order = notes[::-1] if up else notes
            tt = self.t(bt, **SW)
            for j, n in enumerate(order):
                y = self.I.lute(n, length, v * (0.7 if up else 1.0), bright=0.8, t60=0.9)
                self.place('lute', y, tt + j * 0.011, 0.3 - 0.12 * j, gain / 2)

    def hurdy_ost(self, sym, b, steps=16, gain=1.0, cue=False):
        root = bass_root(sym, nn('D4'))
        third = 3 if chord(sym)[1][1] == 3 else 4
        rel = [0, 7, 12, 7, 13 if sym == 'Dm' else 12 + 2, 12, 7, third]
        s = ' '.join(f"{'!' if k % 4 == 0 else ''}{_n(root + rel[k % 8])}:2" for k in range(steps // 2))
        self.phrase('hurdy', s, b, gain=gain, pan=-0.15, gap=0.01)

    def chien(self, pattern, b, gain=1.0, n=nn('D4')):
        for bt, v in hits(pattern, b):
            self.place('hurdy', self.I.chien(n, v), self.t(bt, **SW), 0.25, gain)


_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def _n(m):
    return f'{_NAMES[m % 12]}{m // 12 - 1}'


# ------------------------------------------------------------------ grooves
def groove(S, b, kind, i=0):
    d = lambda p, v, **k: S.drum(p, b, v, **{**SW, **k})
    if kind == 'intro':
        d("X.......X.......", 'stomp', bus='tribal', gain=1.0)
        d("....X.......X...", 'crowdclap', gain=0.9)
        d("..x...x...x...x.", 'tamb', gain=0.35, pan=0.4)
        return
    d("X...X...X...X...", 'kick', decay=0.27, f_end=50, f_start=200, click=0.7)
    if kind in ('d1', 'fin', 's2'):
        d("X.......X.......", 'stomp', bus='tribal', gain=0.9)
        d("....X.......X...", 'crowdclap', gain=1.0)
    if kind == 'd1':
        d("..x...x...x...x." if i < 4 else "gxXxgxXxgxXxgxXx", 'tamb', gain=0.4, pan=0.4)
        if i >= 2:
            d("x..x..x.x.x..x..", 'tek', pan=-0.35, gain=0.8)
            d("X.....X.........", 'doum', bus='tribal', pan=-0.2, gain=0.7)
    if kind == 's2':
        d("gxXxgxXxgxXxgxXx", 'tamb', gain=0.42, pan=0.4)
        d("X..x..X.X..x..X.", 'davul', bus='tribal', gain=0.55)
        d("..x...x...x...xx", 'frame', bus='tribal', gain=0.5, pan=-0.4, f=140)
        d("X...............", 'zill', gain=0.8, pan=0.5)
    if kind == 's3':
        d("X.......X.......", 'stomp', bus='tribal', gain=0.7)
        d("............X...", 'crowdclap', gain=0.9)
        d("X.tt..t.X.tt..t." .replace('t', 'x'), 'tek', pan=-0.4, gain=0.7)
        d("X..x..x.X.......", 'doum', bus='tribal', pan=-0.2, gain=0.8)
        d("x..x..x...x.x...", 'frame', bus='tribal', gain=0.7, pan=0.35, f=90)
        d("......x.......x.", 'frame', bus='tribal', gain=0.5, pan=-0.35, f=130)
        d("g.x.g.x.g.x.g.x.", 'shaker', gain=0.35, pan=0.3)
    if kind == 'fin':
        d("gxXxgxXxgxXxgxXx", 'tamb', gain=0.45, pan=0.4)
        d("X..x..X.X..x..X.", 'davul', bus='tribal', gain=0.6)
        d("x..x..x.x.x..x.x", 'tek', pan=-0.35, gain=0.8)
        d("X...............", 'zill', gain=0.8, pan=0.5)


BASS_A = "r:2 !0:1 0:1 r:2 12:2 r:2 !0:1 0:1 r:2 7:1 12:1"
BASS_R = "!0:1 r:1 12:1 r:1 0:1 12:1 r:1 0:1 r:1 12:1 0:1 r:1 7:1 r:1 12:1 0:1"
BASS_K = "!0:2 r:1 0:1 r:2 0:1 1:1 r:2 0:2 r:2 -2:1 0:1"


def build():
    S = Med()
    I = S.I
    for b, lab in [(0, 'INTRO: flute hook from frame 0, stomp-clap'), (4, 'pickup: hurdy-gurdy answer + davul 3-3-2 + HEY'),
                   (D1, 'DROP 1: kick + bouncy bass + full dance'), (BRK, 'BREAK: bagpipe groan + HEY! (stop-time)'),
                   (S2, 'SECTION 2: royal - bagpipes, lute, processional drums'), (FAKE, 'FAKE-OUT: band winds down, ghost chant'),
                   (S3, 'IMPACT -> SECTION 3: dark hypnotic hurdy-gurdy'), (114, 'build: chant HEY x4 + flute run'),
                   (FIN, 'FINAL DROP: everything'), (138, 'stop-time 3-3-2 ending hits'), (END, 'loop pickup -> 0:00')]:
        S.cue(b, lab, 'section')

    # ================================================================ INTRO 0-6
    groove(S, 0, 'intro')
    S.flute(A1, 0, cue='flute hook (call)')
    S.place('drone', I.hurdy_drone([nn('D3'), nn('A3')], 6 * SPB + 0.1), 0.0, 0.0, 0.7)
    S.phrase('hurdy', "!E5:3 G5:1 E5:2 C5:2", 4, cue='hurdy-gurdy answer')
    S.drum("X..X..X.", 4, 'davul', bus='tribal', gain=0.6)
    S.cue(4, 'davul hit'); S.cue(4.75, 'davul hit'); S.cue(5.5, 'davul hit')
    S.chant([(6, 'A3', 2, 'Ei')], 4)
    S.place('drums', I.shake(1.4 * SPB), S.t(4.6), 0.4, 0.8)

    # ================================================================ DROP 1 6-42
    ch1 = [(6, 'Dm'), (10, 'C'), (14, 'G'), (18, 'C'), (20, 'Dm'), (22, 'Dm'), (26, 'C'), (30, 'G'), (34, 'C'), (36, 'Dm'), (38, 'Bb'), (40, 'C')]
    S.place('tribal', I.boom(0.8), S.t(D1), 0, 0.6); S.place('drums', I.zill(1.0), S.t(D1), 0.4, 1.0)
    for i, b in enumerate(bars(D1, 9)):
        groove(S, b, 'd1', i)
    S.flute(A1, 6, cue='flute CALL')
    S.phrase('hurdy', B1, 10, cue='hurdy-gurdy ANSWER')
    S.flute(A3, 14, cue='flute CALL (higher)')
    S.phrase('hurdy', B4, 18, cue='hurdy-gurdy ANSWER (cadence)')
    S.flute(B4, 18, tr=12, vel=0.4, gain=0.35)
    S.flute(A1v, 22, cue='flute CALL with ornaments + lute enters')
    S.phrase('hurdy', B1, 26, cue='hurdy ANSWER')
    S.chant([(14, 'D4', 2, 'o')], 26)
    S.flute(A3v, 30, cue='flute CALL ornamented')
    S.phrase('hurdy', A3v, 30, harm=-2, gain=0.6)
    S.flute(B4x, 34, cue='flute + hurdy unison run')
    S.phrase('hurdy', B4x, 34, tr=-12, gain=0.8)
    S.flute(TURN1, 38, cue='turnaround fanfare')
    S.phrase('hurdy', TURN1, 38, harm=-2, gain=0.6)
    for b in bars(22, 4):
        sym = [c for c in ch1 if c[0] <= b][-1][1]
        S.lute_arp(sym, b, gain=0.8)
    S.strum("X.....X.", 'Bb', 38); S.strum("X.x.X.xX", 'C', 40)
    S.drum("........oooxxxXX", 38, 'frame', bus='tribal', gain=0.6, f=120)
    S.chant([(12, 'A3', 2, 'Ei')], 38)
    S.place('fx', I.riser(4 * SPB, f0=500, f1=7000), S.t(38), 0, 0.5)
    S.bassline(rseq(" | ".join([BASS_A] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:2 r:2", D1), ch1, upright=0, synth=1.0, growl=0.3, **SW)
    S.place('drone', I.hurdy_drone([nn('D3'), nn('A3')], 32 * SPB), S.t(D1), 0.0, 0.5)

    # ================================================================ BREAK 42-44
    S.place('pipes', I.bag_groan(nn('C5')), S.t(42) - 0.05, 0.1, 1.0)
    S.cue(42, 'bagpipe GROAN (bag inflates)')
    S.phrase('pipe', "r:4 !(G5)C6:1 A5:1 r:2", 42, cue=None)
    S.cue(43, 'bagpipe squawk')
    S.chant([(5, 'C4', 2, 'Ei')], 42)
    S.place('drums', I.shake(0.8 * SPB), S.t(43.15), 0.4, 0.9)
    S.drum("......xX", 42, 'davul', bus='tribal', gain=0.6)

    # ================================================================ SECTION 2 (royal, F major) 44-80
    ch2 = [(44, 'F'), (48, 'C'), (52, 'Bb'), (56, 'C'), (60, 'F'), (64, 'C'), (68, 'Bb'), (70, 'C'), (72, 'F'), (76, 'Gm'), (78, 'A')]
    S.place('tribal', I.boom(1.0), S.t(S2), 0, 0.7); S.place('drums', I.zill(1.0), S.t(S2), 0.4, 1.0)
    for i, b in enumerate(bars(S2, 9)):
        groove(S, b, 's2', i)
        sym = [c for c in ch2 if c[0] <= b][-1][1]
        if i < 8:
            if sym == 'Bb' and b == 68:
                S.strum("X..x..X.", 'Bb', b); S.strum("X..x..X.", 'C', b + 2)
            else:
                S.strum("X..x..X.X..x..X." if i % 2 == 0 else "X..x..X.X.x.X.xx", sym, b)
    S.place('drone', I.pipe_drone([nn('F2'), nn('F3'), nn('C4')], 32 * SPB), S.t(S2), 0.0, 0.8)
    S.phrase('pipe', R1, 44, scale=FMAJ, cue='BAGPIPES take the hook (royal)')
    S.flute(R2, 48, cue='flute ANSWER')
    S.phrase('pipe', R3, 52, cue='bagpipe CALL')
    S.phrase('hurdy', R4, 56, cue='hurdy-gurdy ANSWER')
    S.phrase('pipe', R1, 60, cue='bagpipe CALL + flute harmony')
    S.flute(R1, 60, harm=2, scale=FMAJ, gain=0.7)
    S.flute(R6, 64, cue='flute + hurdy ANSWER (high)')
    S.phrase('hurdy', R6, 64, harm=-2, scale=FMAJ, gain=0.7)
    S.phrase('pipe', R7, 68, cue='bagpipe CALL')
    S.flute(R7, 68, harm=2, scale=FMAJ, gain=0.6)
    for kind in ('pipe', 'hurdy'):
        S.phrase(kind, R8, 72, gain=1.0 if kind == 'pipe' else 0.7, tr=0 if kind == 'pipe' else -12)
    S.flute(R8, 72, tr=12, gain=0.6, cue='TUTTI royal cadence')
    S.chant([(0, 'F3', 6, 'a'), (8, 'C4', 2, 'Ei')], 72)
    S.flute(TURN2, 76, cue='turnaround run')
    S.phrase('hurdy', TURN2, 76, tr=-12, gain=0.8)
    S.strum("X..x..X.", 'Gm', 76); S.strum("X.x.XxXx", 'A', 78)
    S.drum("xxxxxxxxooooxxXX", 76, 'frame', bus='tribal', gain=0.6, f=120)
    S.drum("X.......X...X.X.", 76, 'davul', bus='tribal', gain=0.6)
    S.place('fx', I.riser(4 * SPB, f0=500, f1=9000), S.t(76), 0, 0.6)
    S.bassline(rseq(" | ".join([BASS_R] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:2 12:2", S2), ch2, upright=0, synth=1.0, punch=1.4, growl=0.4, **SW)

    # ================================================================ FAKE-OUT 80-82
    S.place('post', I.chant(nn('D3'), 3 * SPB, 0.6, vowels='uo', cons=None, voices=8, spread=0.05), S.t(80.3), 0.0, 0.8)
    wind = [(0, 0.9, nn('A4'), None, 0.8)]
    y = I.hurdy(wind, 1.0)
    tt = np.arange(len(y)) / SR
    y = y * np.exp(-tt / 0.35)
    S.place('post', y, S.t(80), 0.0, 0.6)
    S.cue(80, 'everything winds down (mystery)')
    S.place('post', I.tek(0.6), S.t(81), -0.3, 0.6); S.place('post', I.tek(0.5), S.t(81.5), 0.3, 0.6)
    S.cue(82, 'IMPACT (boom + zill + davul)')

    # ================================================================ SECTION 3 (dark, D Phrygian) 82-118
    ch3 = [(82, 'Dm'), (86, 'Eb'), (90, 'Dm'), (94, 'C'), (98, 'Dm'), (102, 'Eb'), (106, 'Bb'), (110, 'A'), (114, 'Bb'), (116, 'A')]
    S.place('tribal', I.boom(1.0), S.t(S3), 0, 0.9); S.place('drums', I.zill(1.0), S.t(S3), 0.4, 1.0)
    S.drum("X.......", 82, 'davul', bus='tribal', gain=0.8)
    S.place('drone', I.hurdy_drone([nn('D3'), nn('A3'), nn('D2')], 32 * SPB), S.t(S3), 0.0, 0.8)
    for i, b in enumerate(bars(S3, 9)):
        sym = [c for c in ch3 if c[0] <= b][-1][1]
        if i < 8:
            groove(S, b, 's3', i)
            S.hurdy_ost(sym, b, gain=0.75)
            S.chien("..x...x...x.x.x." if i % 2 else "..x...x...x...x.", b, gain=0.9)
    S.cue(82, 'hurdy-gurdy hypnotic ostinato + buzzing chien')
    S.chant([(0, 'D3', 14, 'uo')], 82, gain=0.6, cue=False)
    S.chant([(0, 'Eb3', 14, 'uo')], 86, gain=0.6, cue=False)
    S.flute(K1, 90, tr=-12, gain=0.9, cue='flute: dark version of the hook (low)')
    S.flute(K2, 94, tr=-12, gain=0.9)
    S.chant([(12, 'D4', 2, 'a')], 94)
    S.chant([(0, 'D3', 14, 'uo')], 98, gain=0.6, cue=False)
    S.chant([(0, 'Eb3', 14, 'uo')], 102, gain=0.6, cue=False)
    S.flute(K1, 98, gain=0.8, cue='flute dark hook (high)')
    S.flute(K2, 102, gain=0.8)
    S.flute(K3, 106, cue='flute + hurdy dark call')
    S.phrase('hurdy', K3, 106, tr=-12, gain=0.5)
    S.flute(K4, 110)
    S.chant([(12, 'A3', 2, 'a'), (14, 'A3', 2, 'a')], 110)
    S.phrase('pipe', "!A4:8 r:8", 110, gain=0.5, cue='bagpipe drone accent')
    # 114 build
    S.drum("X...X...X.X.XXXX", 114, 'kick', decay=0.25, f_end=52, f_start=190, click=0.7)
    S.drum("x.x.x.x.xxxxXXXX", 114, 'davul', bus='tribal', gain=0.45)
    S.drum("xxxxxxxxxxxxXXXX", 114, 'tamb', gain=0.4, pan=0.4)
    S.chant([(8, 'A3', 1, 'Ei'), (10, 'A3', 1, 'Ei'), (12, 'C#4', 1, 'Ei'), (14, 'E4', 1, 'Ei')], 114)
    S.flute(RUN3, 114, cue='flute run up')
    S.strum("X...X...", 'Bb', 114); S.strum("X.X.XxXx", 'A', 116)
    S.place('fx', I.riser(4 * SPB, f0=400, f1=10000), S.t(114), 0, 0.7)
    S.bassline(rseq(" | ".join([BASS_K] * 8) + " | !0:2 12:2 0:2 12:2 !0:1 12:1 0:1 12:1 0:1 12:1 0:1 12:1", S3), ch3,
               upright=0, synth=1.0, punch=1.1, growl=0.6, **SW)

    # ================================================================ FINAL 118-144
    ch4 = [(118, 'Dm'), (122, 'C'), (126, 'G'), (130, 'C'), (132, 'Dm'), (134, 'Dm'), (138, 'Dm'), (140, 'C'), (142, 'A')]
    S.place('tribal', I.boom(1.1), S.t(FIN), 0, 1.0); S.place('drums', I.zill(1.0), S.t(FIN), 0.4, 1.0)
    S.place('drums', I.crash(0.7, 1.5), S.t(FIN), 0.0, 0.25)
    for i, b in enumerate(bars(FIN, 5)):
        groove(S, b, 'fin', i)
        sym = [c for c in ch4 if c[0] <= b][-1][1]
        S.lute_arp(sym, b, gain=0.7)
    S.place('drone', I.pipe_drone([nn('D2'), nn('D3'), nn('A3')], 20 * SPB), S.t(FIN), 0.0, 0.9)
    S.place('drone', I.hurdy_drone([nn('D3'), nn('A3')], 24 * SPB), S.t(FIN), 0.0, 0.4)
    S.flute(A1, 118, cue='FINAL: flute + bagpipes hook in unison, hurdy harmony')
    S.phrase('pipe', A1, 118)
    S.phrase('hurdy', A1, 118, harm=-2, gain=0.7)
    S.phrase('pipe', B1x, 122, cue='bagpipe + hurdy ANSWER + HEY!')
    S.phrase('hurdy', B1, 122, gain=0.7)
    S.chant([(0, 'D4', 2, 'Ei'), (6, 'D4', 2, 'Ei')], 122)
    S.flute(A3v, 126, cue='flute + bagpipes CALL')
    S.phrase('pipe', A3, 126)
    S.phrase('hurdy', A3, 126, harm=-2, gain=0.7)
    S.flute(B4x, 130, cue='everyone: run up')
    S.phrase('pipe', B4x, 130)
    S.phrase('hurdy', B4x, 130, tr=-12, gain=0.8)
    S.flute(A1x, 134, cue='hook with whirlwind tail')
    S.phrase('pipe', A1x, 134)
    S.phrase('hurdy', A1x, 134, harm=-2, gain=0.7)
    S.chant([(12, 'A3', 1, 'Ei'), (14, 'A3', 1, 'Ei')], 134)
    # 138: stop-time 3-3-2 hits then flourish
    S.flute(ENDING, 138, cue='3-3-2 STOP HITS')
    S.phrase('pipe', ENDING, 138)
    S.phrase('hurdy', ENDING, 138, tr=-12, gain=0.8)
    for st in (0, 3, 6):
        S.drum("X", 138 + st / 4, 'kick', decay=0.3)
        S.drum("X", 138 + st / 4, 'davul', bus='tribal', gain=0.8)
        S.drum("X", 138 + st / 4, 'stomp', bus='tribal', gain=1.0)
        S.strum("X", 'Dm', 138 + st / 4, gain=1.2)
        S.cue(138 + st / 4, 'tutti hit')
    S.chant([(0, 'D4', 2, 'Ei'), (3, 'D4', 2, 'Ei'), (6, 'D4', 2, 'Ei')], 138, cue=False)
    S.drum("........X...X...", 138, 'kick', decay=0.27)
    S.drum("........gxXxgxXx", 138, 'tamb', gain=0.45, pan=0.4)
    S.drum("............X...", 138, 'crowdclap')
    S.lute_arp('C', 140, steps=8, gain=0.7)
    # 142-144: A-major hit + pickup -> loops into the intro hook
    S.drum("X.......", 142, 'kick'); S.drum("X.......", 142, 'davul', bus='tribal', gain=0.8)
    S.place('drums', I.zill(1.0), S.t(142), 0.4, 0.9)
    S.strum("X.......", 'A', 142, gain=1.2)
    S.chant([(0, 'C#4', 3, 'Ei')], 142)
    S.flute("r:4 E5:1 F5:1 E5:1 C#5:1", 142)
    S.phrase('pipe', "!A4:4 r:4", 142, gain=0.7)
    S.bassline(rseq(" | ".join([BASS_R] * 5) + " | !0:2 r:4 0:2 12:2 0:2 12:2 0:2 | !0:3 r:5", FIN), ch4,
               upright=0, synth=1.0, punch=1.6, growl=0.4, **SW)

    cfg = {
        'kick': dict(gain=0.62, eq=[('hp', 30, 0.7), ('peak', 60, 1.0, 2.0), ('peak', 380, 1.2, -3)]),
        'tribal': dict(gain=0.45, sc=0.1, rv2=0.2, eq=[('hp', 40), ('peak', 120, 1.0, 2)]),
        'drums': dict(gain=0.75, sc=0.12, rv2=0.15, eq=[('hp', 180), ('lp', 13000)], haas=0.007),
        'sub': dict(gain=0.3, sc=0.75, eq=[('lp', 1800), ('hp', 32)], drive=1.4),
        'flute': dict(gain=0.42, sc=0.15, rv=0.2, dl=0.1, eq=[('hp', 250), ('peak', 2500, 1.0, 1.5)]),
        'pipes': dict(gain=0.65, sc=0.2, rv=0.2, rv2=0.1, eq=[('hp', 250), ('lp', 9000)], haas=0.006),
        'hurdy': dict(gain=0.42, sc=0.3, rv=0.18, rv2=0.1, eq=[('hp', 150), ('peak', 260, 0.9, 3)], haas=0.01),
        'lute': dict(gain=0.75, sc=0.35, rv=0.15, rv2=0.12, eq=[('hp', 110), ('peak', 240, 0.9, 3)], haas=0.012),
        'chant': dict(gain=0.5, sc=0.25, rv=0.4, dl=0.1, eq=[('hp', 120)], haas=0.015),
        'drone': dict(gain=0.38, sc=0.45, rv=0.25, eq=[('hp', 60), ('peak', 250, 0.8, 2)], haas=0.02),
        'fx': dict(gain=0.25, rv=0.3),
        'post': dict(gain=0.35),
    }
    auto = [(0, 0.0), (D1, -1.5), (S2, -1.0), (S3, -2.5), (114, -1.5), (FIN, 0.5)]
    return S, cfg, dict(tape_stop=(S.t(FAKE), 0.4, S.t(S3) - 0.01), automation=auto)
