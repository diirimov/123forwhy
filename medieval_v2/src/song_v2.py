"""MEDIEVAL JOBS V2 - 'Hey-ya Village Dance'.  A minor folk rave, 150 BPM, 65.0 s.

THE HOOK = a call-and-response between the flute and the whole village:
  flute (call):   pa . pa-PA . pa PAAH   pa . pa-PA . pa PAAH        A A E C A | G G D B G
  village (resp): HEY . ya-HEY . ya HOO   HEY . ya-HEY . ya HAA!     same rhythm, shouted back
Chords: | Am  G | F  E |  (2 bars = call + response)

Grid: beat = 0.4 s, bar = 1.6 s.  Sections (bars): intro 0-1, KNOCKER-UP 2-12, GROOM 13-23,
SIN-EATER 24-34, FINAL 35-39, tail 64.0-65.0 s (2.5 beats of knocks that loop into 0:00).
"""
from inst_v2 import *  # noqa
from inst_v2 import _onepole, _harm_sum  # noqa

SW = dict(s16=0.53)

# ------------------------------------------------------------------ melody book
CALL1 = "!A5:1' r:1 A5:1' E6:1' r:1 C6:1' A5:2 !G5:1' r:1 G5:1' D6:1' r:1 B5:1' G5:2"
CALL2 = "!A5:1' r:1 A5:1' E6:1' r:1 C6:1' A5:2 !B5:1' r:1 C6:1' D6:1' E6:1' F6:1' E6:2"
CALL3 = "!A5:1' r:1 A5:1' !(F6)E6:1' r:1 C6:1' (B5)A5:2 !G5:1' r:1 G5:1' !(E6)D6:1' r:1 B5:1' G5:2"
DARK1 = "!A4:1' r:1 A4:1' E5:1' r:1 C5:1' A4:2 !Bb4:1' r:1 Bb4:1' F5:1' r:1 D5:1' Bb4:2"
DARK2 = "!A4:1' r:1 A4:1' E5:1' r:1 C5:1' A4:2 !Bb4:1' r:1 D5:1' F5:1' A5:1' Bb5:1' A5:2"
BP1 = "!D5:2 F5:1 A5:1 D6:2 C6:1 A5:1 !E5:2 A5:1 C6:1 E6:2 D6:1 C6:1"
BP2 = "!C6:1 A5:1 F5:1 A5:1 C6:1 D6:1 C6:1 A5:1 !B5:1 G#5:1 E5:1 G#5:1 B5:2 E6:2"
ROY1 = "!F5:3 A5:1 C6:4 !E6:3 D6:1 C6:4"
ROY2 = "!D6:3 B5:1 G5:4 !G#5:2 B5:2 E6:4"
DBP1 = "!D5:3 E5:1 F5:2 E5:2 !D5:2 C5:2 Bb4:2 A4:2"
DBP2 = "!G#4:3 A4:1 Bb4:2 A4:2 !G#4:4 E4:4"
FAN = "!C5:1' E5:1' G5:1' C6:3 r:2"            # royal fanfare answer (first half of a bar)
FAN2 = "!G4:1' C5:1' E5:1' G5:1' C6:1' E6:3"
CLIMAX = "!A5:1' r:1 A5:1' E6:1' r:1 C6:1' A5:2 !E6:2 r:2 !A6:4"

AMIN = [nn('A4') + i for i in (0, 2, 3, 5, 7, 8, 10)]
CMAJ = [nn('C4') + i for i in (0, 2, 4, 5, 7, 9, 11)]

# village answer (male pitch; women sing an octave up).  (step, syllable, midi, len16)
SYL = {'HEY': ('h', 'ei', 'shout', 0.95), 'ya': ('y', 'a', 'sung', 0.55), 'HO': ('h', 'ou', 'shout', 0.9),
       'HA': ('h', 'a', 'shout', 1.0), 'HOO': ('h', 'u', 'shout', 0.85), 'OOH': ('', 'u', 'fall', 0.5),
       'WOO': ('w', 'u', 'rise', 0.8), 'HUH': ('h', '@', 'rise', 0.7), 'OHO': ('ʔ', 'o', 'laugh', 0.7),
       'HMM': ('m', 'm', 'sung', 0.4), 'AH': ('', 'a', 'sung', 0.45), 'HEYa': ('h', 'eia', 'shout', 0.9)}
ANS1 = [(0, 'HEY', 60, 1), (2, 'ya', 57, 1), (3, 'HEY', 60, 1), (5, 'ya', 57, 1), (6, 'HOO', 53, 2),
        (8, 'HEY', 59, 1), (10, 'ya', 56, 1), (11, 'HEY', 59, 1), (13, 'ya', 56, 1), (14, 'HA', 52, 2)]
ANS2 = ANS1[:5] + [(8, 'HEY', 59, 1), (9, 'HEY', 59, 1), (10, 'HEY', 59, 2), (12, 'HO', 56, 1), (13, 'HEY', 59, 1), (14, 'HA', 64, 2)]
ANS_DARK = [(0, 'HO', 57, 2), (3, 'HO', 57, 2), (6, 'HMM', 52, 2), (8, 'OOH', 64, 6)]

SEC = {'intro': (0, 8), 'knocker': (8, 52), 'groom': (52, 96), 'sin': (96, 140), 'final': (140, 160), 'tail': (160, 162.5)}

STEMS = {
    'Drums': ['kick', 'drums', 'folkdrums'],
    'Bass': ['bass'],
    'Vocal_Chants': ['vox', 'voxfx'],
    'Musical_SFX': ['msfx', 'bells', 'risers'],
    'Instrumental': ['flute', 'fiddle', 'hurdy', 'lute', 'brass', 'drone'],
}


def bar(b):
    return 4 * b


class Song2:
    def __init__(self, seed=2024):
        self.I = Inst2(seed)
        self.rng = np.random.default_rng(seed + 7)
        self.N = int((DUR + 4.0) * SR)
        self.buses = {}
        self.kicks = []
        self.events = []

    def t(self, beat, s16=0.53):
        return float(warp(beat, 0.5, s16)) * SPB

    def bus(self, name):
        if name not in self.buses:
            self.buses[name] = np.zeros((2, self.N))
        return self.buses[name]

    def place(self, name, sig, tsec, pan=0.0, gain=1.0):
        B = self.bus(name)
        i = int(round(tsec * SR))
        if sig.ndim == 1:
            nf = min(256, len(sig) // 4)
            if nf > 1:
                sig = sig.copy(); sig[-nf:] *= np.linspace(1, 0, nf)
            gl, gr = pan_gains(pan)
            sig = np.stack([sig * gl, sig * gr])
        if i < 0:   # wrap pre-roll (e.g. 'h' breath before beat 0) to the end of the loop
            L = int(DUR * SR)
            head = sig[:, :-i]
            B[:, L + i:L] += head * gain
            sig = sig[:, -i:]; i = 0
        n = min(sig.shape[1], self.N - i)
        if n > 0:
            B[:, i:i + n] += sig[:, :n] * gain

    def ev(self, beat, kind, label, tsec=None):
        self.events.append(dict(beat=round(beat, 4), time=round(self.t(beat) if tsec is None else tsec, 4), type=kind, label=label))

    # ------------------------------------------------------------ players
    def notes(self, s, b, tr=0, vel=0.8, harm=0, scale=AMIN):
        out = []
        for e in seq(s, b, tr=tr, vel=vel):
            n = e['n']
            if harm:
                sc = sorted(set(p % 12 for p in scale))
                pcs = sorted(p + 12 * o for o in range(0, 10) for p in sc)
                idx = max(i for i, q in enumerate(pcs) if q <= n)
                n = pcs[idx + harm]
            out.append(dict(e, n=n, gr=None if harm else e['gr']))
        return out

    def flute(self, s, b, tr=0, vel=0.85, gain=1.0, pan=0.05, harm=0, label=None, bus='flute'):
        prev = None
        for e in self.notes(s, b, tr, vel, harm):
            tt = self.t(e['t']) + self.rng.normal(0, 0.003)
            d = self.t(e['t'] + e['d']) - self.t(e['t'])
            y = self.I.flute(e['n'], d, e['v'] * (1 + self.rng.normal(0, 0.03)), grace=e['gr'], prev=prev, stac=e['stac'])
            self.place(bus, y, tt, pan, gain)
            prev = e['n']
        if label:
            self.ev(b, 'melody', label)

    def legato(self, kind, s, b, tr=0, vel=0.85, gain=1.0, pan=0.0, harm=0, scale=AMIN, drone=None, label=None):
        evs = self.notes(s, b, tr, vel, harm, scale)
        groups, cur = [], []
        for e in evs:
            if cur and abs(cur[-1]['t'] + cur[-1]['d'] - e['t']) > 1e-6:
                groups.append(cur); cur = []
            cur.append(e)
        if cur:
            groups.append(cur)
        for gph in groups:
            t0 = self.t(gph[0]['t'])
            nl = []
            for e in gph:
                ts = self.t(e['t']) - t0
                te = self.t(e['t'] + e['d']) - t0
                if e['stac']:
                    te = ts + (te - ts) * 0.6
                nl.append((ts, te - 0.004, e['n'], e['gr'], e['v']))
            total = nl[-1][1] + 0.15
            if kind == 'fiddle':
                y = self.I.fiddle(nl, total, drone=drone) * 3.0
                busn = 'fiddle'
            else:
                y = self.I.hurdy(nl, total)
                busn = 'hurdy'
            self.place(busn, y, t0, pan, gain)
        if label:
            self.ev(b, 'melody', label)

    def brass(self, s, b, tr=0, vel=0.9, gain=1.0, harm=(0, -2), scale=CMAJ, label=None, fall_last=False):
        for k, h in enumerate(harm):
            evs = self.notes(s, b, tr, vel, h, scale)
            for j, e in enumerate(evs):
                d = (self.t(e['t'] + e['d']) - self.t(e['t'])) * (0.6 if e['stac'] else 0.92)
                y = self.I.fanfare_note(e['n'], d, e['v'], fall=fall_last and j == len(evs) - 1)
                self.place('brass', y, self.t(e['t']) + self.rng.uniform(0, 0.008), [-0.35, 0.35, 0.0][k % 3], gain * (1.0 if k == 0 else 0.7))
        if label:
            self.ev(b, 'fanfare', label)

    def chant(self, items, b, group='full', gain=1.0, label=True, tr=0, bus='vox', effort_mul=1.0, spread=None):
        cfg = {'full': (6, 5, 0.016), 'big': (9, 7, 0.02), 'men': (7, 0, 0.016), 'women': (0, 6, 0.014),
               'solo': (1, 0, 0.0), 'ghost': (4, 3, 0.04)}[group]
        for step, syl, midi, l16 in items:
            cons, vw, contour, eff = SYL[syl]
            dur = l16 / 4 * SPB * (0.8 if contour == 'shout' else 0.95)
            bt = b + step / 4
            y = crowd(self.rng, cons, vw, midi + tr, dur, n_m=cfg[0], n_f=cfg[1], spread=cfg[2] if spread is None else spread,
                      contour=contour, effort=min(1.0, eff * effort_mul), oct_f=False, breath=0.14 if group != 'ghost' else 0.6,
                      vib=0.3 if contour == 'sung' else 0.0)
            pre = 0.055 if cons == 'h' else 0.012 if cons in 'db' else 0.0
            self.place(bus, y, self.t(bt) - pre, 0.0, gain)
            if label and syl in ('HEY', 'HO', 'HA', 'HOO', 'HUH', 'WOO', 'OHO', 'HEYa'):
                self.ev(bt, 'vocal', syl + '!')

    def drum(self, pattern, b, voice, bus='drums', gain=1.0, pan=0.0, label=None, **kw):
        for bt, v in hits(pattern, b):
            tt = self.t(bt) + self.rng.normal(0, 0.0012)
            vv = v * (1 + self.rng.normal(0, 0.05))
            y = getattr(self.I, voice)(vv, **kw)
            if voice == 'kick':
                self.kicks.append(tt)
                self.place('kick', y, tt, 0.0, gain)
            else:
                self.place(bus, y, tt, pan, gain)
            if label and v >= 0.99:
                self.ev(bt, 'accent', label)

    def strum(self, pattern, sym, b, gain=1.0, low=nn('A3'), length=0.12):
        notes = voicing(sym, low)
        notes = notes + [notes[0] + 12]
        for k, (bt, v) in enumerate(hits(pattern, b)):
            tt = self.t(bt)
            order = notes if k % 2 == 0 else notes[::-1]
            for j, n in enumerate(order):
                y = self.I.lute(n, length, v * 0.9, bright=0.85, t60=0.5)
                self.place('lute', y, tt + j * 0.008, 0.35 - 0.15 * j, gain / 2)

    def bassline(self, pattern, chords, b0, nbars, punch=1.3, growl=0.25, oct_low=nn('E1')):
        ev = rseq(" ".join([pattern] * nbars) if isinstance(pattern, str) else pattern, b0)
        cb = sorted(chords)
        for e in ev:
            sym = [c for c in cb if c[0] <= e['t'] + 1e-6][-1][1]
            n = bass_root(sym, oct_low) + 12 + e['s']
            if n > nn('B2'):
                n -= 12
            tt = self.t(e['t'])
            d = (self.t(e['t'] + e['d']) - tt) * (0.55 if e['stac'] else 0.85)
            y = self.I.synth_bass(n, d, e['v'], punch=punch, growl=growl)
            self.place('bass', y, tt, 0.0, 1.0)


def chord_at(chords, beat):
    return [c for c in sorted(chords) if c[0] <= beat + 1e-6][-1][1]


BASS = "r:2 !0:2 r:2 12:1' 12:1 r:2 !0:2 r:2 12:1' 7:1"
BASS_R = "r:2 !0:2 r:1 0:1 12:2 r:2 !0:2 r:1 7:1 12:1' 0:1"
BASS_D = "r:2 !0:2 r:2 0:1' 1:1 r:2 !0:2 r:2 12:1' 0:1"


def hook_chords(b, kind='main'):
    """Chord list for a 2-bar call+answer starting at beat b."""
    if kind == 'main':
        return [(b, 'Am'), (b + 2, 'G'), (b + 4, 'F'), (b + 6, 'E')]
    if kind == 'royal':
        return [(b, 'F'), (b + 2, 'G'), (b + 4, 'C'), (b + 6, 'E')]
    return [(b, 'Am'), (b + 2, 'Bb'), (b + 4, 'Am'), (b + 6, 'E')]


def groove(S, b, kind, i=0):
    """One bar of drums for a section kind."""
    S.drum("X...X...X...X...", b, 'kick', decay=0.24, f_end=52, f_start=210, click=0.8, drive=2.6)
    S.drum("X.......X.......", b, 'stomp', bus='folkdrums', gain=0.9)
    S.drum("....X.......X...", b, 'crowdclap', gain=1.0)
    if kind == 'knocker':
        S.drum("..x...x...x...x.", b, 'tamb', gain=0.5, pan=0.35)
        if i >= 2:
            S.drum("x.x...x..x.x..x." if i % 2 == 0 else "x.x...x..x.x.x..", b, 'glass_tap', bus='msfx', gain=0.9, pan=-0.3)
        if i >= 6:
            S.drum("...........x..x.", b, 'door_knock', bus='msfx', gain=0.7, pan=0.25)
    elif kind == 'groom':
        S.drum("..x...x...x...x.", b, 'tamb', gain=0.5, pan=0.35)
        S.drum("xgxgXgxgxgxgXgxg", b, 'coins', bus='msfx', gain=1.6, pan=-0.35, n=4, dur=0.05)
        S.drum("X.....x.X.....x.", b, 'davul', bus='folkdrums', gain=0.5)
        S.drum("......x.......xx", b, 'frame', bus='folkdrums', gain=0.5, pan=0.3, f=150)
    elif kind == 'sin':
        S.drum("..x...x...x...x.", b, 'whisper', bus='msfx', gain=0.7, pan=0.4, kind='s', dur=0.09)
        S.drum("......x.......x.", b, 'whisper', bus='msfx', gain=0.6, pan=-0.4, kind='sh', dur=0.15)
        S.drum("x..x..x...x.x...", b, 'frame', bus='folkdrums', gain=0.7, pan=-0.3, f=85)
        S.drum("X.......X..x....", b, 'davul', bus='folkdrums', gain=0.45)
    elif kind == 'final':
        S.drum("gxXxgxXxgxXxgxXx", b, 'tamb', gain=0.55, pan=0.35)
        S.drum("x.x...x..x.x..x.", b, 'glass_tap', bus='msfx', gain=0.8, pan=-0.35)
        S.drum("X.....x.X..x..x.", b, 'davul', bus='folkdrums', gain=0.55)
        S.drum("xgxgxgxgxgxgxgxg", b, 'coins', bus='msfx', gain=1.2, pan=0.4, n=3, dur=0.04)


def build():
    S = Song2()
    I = S.I
    sec_ev = [(0, 'section', 'INTRO: village HEY! + flute hook (voice-over space)'), (8, 'drop', 'DROP 1: KNOCKER-UP section'),
              (44, 'section', 'knocker B-part (fiddle reel)'), (48, 'transition', 'stop-time: HEY! HA! + knock-knock-knock + slide whistle'),
              (52, 'drop', 'DROP 2: GROOM OF THE STOOL (royal)'), (84, 'section', 'royal B-part'), (92, 'transition', 'TA-DA fanfare + tolling bell'),
              (96, 'drop', 'DROP 3: SIN-EATER (dark, bells)'), (128, 'section', 'dark B-part'), (136, 'transition', 'build: bells accelerate, HEY x4'),
              (140, 'drop', 'FINAL DROP'), (156, 'section', 'climax bar'), (160, 'transition', 'tail: final hit + knock-knock-knock -> loop')]
    for b, k, l in sec_ev:
        S.ev(b, k, l)

    # ================================================================ INTRO (bars 0-1)
    S.chant([(0, 'HEY', 62, 2)], 0, group='big')
    S.flute(CALL1, 0, gain=0.9, label='HOOK call (flute) - first statement')
    S.strum("x...x...x...x...", 'Am', 0, gain=0.6)
    S.drum("X.......X.......", 0, 'stomp', bus='folkdrums', gain=0.8)
    S.drum("....x.......x...", 0, 'crowdclap', gain=0.7)
    S.drum("x.x...x..x.x..x.", 4, 'glass_tap', bus='msfx', gain=0.9, pan=-0.3, label=None)
    S.ev(4, 'sfx', 'window taps (knocker-up groove preview)')
    S.place('drone', I.hurdy_drone([nn('A2'), nn('E3')], 2 * BAR), S.t(0), 0, 0.5)
    S.chant([(14, 'HA', 57, 2)], 4, group='full', gain=0.8)
    S.place('risers', I.reverse_swell(BAR * 0.95), S.t(4), 0, 0.8)

    # ================================================================ KNOCKER-UP (bars 2-12)
    ch = []
    S.place('risers', I.impact(1.0) * 0.8, S.t(8), 0, 0.7); S.place('drums', I.crash(0.8, 1.2), S.t(8), 0, 0.2)
    S.ev(8, 'impact', 'drop impact')
    calls = {2: (CALL1, 'HOOK call'), 4: (CALL1, 'HOOK call'), 6: (CALL2, 'HOOK call v2 (climbs)'), 8: (CALL3, 'HOOK call ornamented')}
    for k, bb in enumerate(range(2, 10, 2)):
        b = bar(bb)
        ch += hook_chords(b)
        s, lab = calls[bb]
        S.flute(s, b, label=lab)
        if bb >= 6:
            S.legato('fiddle', s, b, tr=-12, gain=0.6, pan=-0.25)
        ans = ANS2 if bb in (6, 8) else ANS1
        S.chant(ans, b + 4, group='full' if bb < 8 else 'big')
        S.ev(b + 4, 'melody', 'VILLAGE ANSWER (call-and-response)')
        if bb == 4:
            S.chant([(15, 'WOO', 69, 2)], b + 4, group='women', gain=0.7)
    ch += [(bar(10), 'Dm'), (bar(10) + 2, 'Am'), (bar(11), 'F'), (bar(11) + 2, 'E'), (bar(12), 'Am'), (bar(12) + 2, 'E')]
    for i, bb in enumerate(range(2, 13)):
        b = bar(bb)
        if bb < 12:
            groove(S, b, 'knocker', i)
            sym = chord_at(ch, b); sym2 = chord_at(ch, b + 2)
            S.strum("..x...x.", sym, b); S.strum("..x...x.", sym2, b + 2)
    S.legato('fiddle', BP1, bar(10), gain=1.0, pan=-0.15, drone=nn('A4'), label='fiddle reel B-part')
    S.flute(BP1, bar(10), tr=12, vel=0.5, gain=0.35)
    S.legato('fiddle', BP2, bar(11), gain=1.0, pan=-0.15, drone=nn('E5'))
    S.chant([(0, 'HO', 57, 1), (8, 'HO', 57, 1)], bar(10), group='men')
    S.chant([(0, 'HO', 57, 1), (8, 'HEY', 59, 1), (12, 'HEY', 59, 1), (14, 'HEY', 59, 1)], bar(11), group='men')
    # bar 12: stop-time transition
    b = bar(12)
    for st, sym in ((0, 'Am'), (3, 'Am')):
        S.drum("X", b + st / 4, 'kick'); S.drum("X", b + st / 4, 'stomp', bus='folkdrums')
        S.strum("X", sym, b + st / 4, gain=1.3)
    S.chant([(0, 'HEY', 60, 2), (3, 'HA', 64, 2)], b, group='big')
    S.drum("........X.X.X...", b, 'door_knock', bus='msfx', gain=1.0, label='KNOCK')
    S.chant([(12, 'HUH', 57, 2)], b, group='solo', gain=1.4)
    S.place('msfx', I.slide_whistle(True, 0.5), S.t(b + 3.2), 0.2, 0.8)
    S.ev(b + 3.2, 'sfx', 'slide whistle up')
    S.bassline(BASS, ch, bar(2), 10)

    # ================================================================ GROOM OF THE STOOL (bars 13-23)
    b0 = bar(13)
    S.place('msfx', I.door_slam(1.0), S.t(b0), 0, 0.9)
    S.place('drums', I.crash(0.9, 1.4), S.t(b0), 0, 0.25)
    S.place('folkdrums', I.timpani(nn('F2'), 1.0), S.t(b0), 0, 0.6)
    S.ev(b0, 'impact', 'PALACE DOORS slam + timpani')
    ch2 = []
    for k, bb in enumerate(range(13, 21, 2)):
        b = bar(bb)
        ch2 += hook_chords(b, 'royal')
        s = [CALL1, CALL3, CALL2, CALL1][k]
        S.flute(s, b, label='HOOK call (royal reharmonisation)')
        if k >= 1:
            S.legato('fiddle', s, b, tr=-12, gain=0.6, pan=-0.25)
        if k >= 2:
            S.legato('hurdy', s, b, tr=-12, harm=-2, gain=0.5, pan=0.2)
        # answer: fanfare (first half) + village (second half)
        S.brass(FAN if k % 2 == 0 else FAN2, b + 4, label='ROYAL FANFARE answers the hook')
        if k == 1:
            S.chant([(8, 'OOH', 64, 6)], b + 4, group='big')
        elif k == 3:
            S.chant([(8, 'OHO', 60, 4), (14, 'HA', 64, 2)], b + 4, group='men')
        else:
            S.chant([(8, 'HO', 56, 1), (10, 'HO', 56, 1), (12, 'HEY', 59, 1), (14, 'HA', 64, 2)], b + 4, group='big')
        S.place('msfx', I.coins(1.0, n=14, dur=0.25), S.t(b + 4 + 2.5), 0.4, 1.8)
        S.ev(b + 4 + 2.5, 'sfx', 'coin shower')
    ch2 += [(bar(21), 'F'), (bar(21) + 2, 'C'), (bar(22), 'G'), (bar(22) + 2, 'E'), (bar(23), 'C')]
    for i, bb in enumerate(range(13, 23)):
        b = bar(bb)
        groove(S, b, 'groom', i)
        S.strum("..x...x.", chord_at(ch2, b), b); S.strum("..x...x.", chord_at(ch2, b + 2), b + 2)
    S.brass(ROY1, bar(21), label='royal procession theme (trumpets)')
    S.legato('fiddle', ROY1, bar(21), gain=0.7, pan=-0.2)
    S.brass(ROY2, bar(22), scale=AMIN)
    S.legato('fiddle', ROY2, bar(22), gain=0.7, pan=-0.2)
    S.chant([(0, 'HEY', 60, 1), (8, 'HEY', 60, 1)], bar(21), group='full')
    S.chant([(0, 'HEY', 59, 1), (8, 'HO', 56, 1), (12, 'HO', 56, 1), (14, 'HEY', 59, 1)], bar(22), group='full')
    # bar 23: TA-DA + first toll of the bell
    b = bar(23)
    S.brass("!C5:1' C5:1' r:2 !C6:4 r:8", b, harm=(0, -2, -4), fall_last=True, label='TA-DA!')
    S.drum("X.X.....", b, 'kick'); S.drum("X.X.....", b, 'davul', bus='folkdrums', gain=0.7)
    S.chant([(2, 'HEY', 64, 2)], b, group='big')
    S.place('bells', I.church_bell(nn('A3'), 0.9, ring=2.5, big=True), S.t(b + 2), 0, 0.9)
    S.ev(b + 2, 'impact', 'first CHURCH BELL toll')
    S.place('risers', I.ghost_swell(2 * SPB, 1.0), S.t(b + 2), 0, 0.9)
    S.bassline(BASS_R, ch2, bar(13), 10, punch=1.5)

    # ================================================================ SIN-EATER (bars 24-34)
    b0 = bar(24)
    S.place('risers', I.impact(1.0), S.t(b0), 0, 0.9)
    S.place('bells', I.church_bell(nn('A2'), 1.0, ring=3.5, big=True), S.t(b0), 0, 0.8)
    S.place('msfx', I.crow(1.0), S.t(b0 + 0.5), 0.5, 0.6)
    S.ev(b0, 'impact', 'BELL + impact'); S.ev(b0 + 0.5, 'sfx', 'crow caws')
    S.place('drone', I.hurdy_drone([nn('A2'), nn('E3'), nn('A3')], 11 * BAR), S.t(b0), 0, 0.7)
    ch3 = []
    for k, bb in enumerate(range(24, 32, 2)):
        b = bar(bb)
        ch3 += hook_chords(b, 'dark')
        s = DARK1 if k % 2 == 0 else DARK2
        S.legato('fiddle', s, b, gain=0.9, pan=-0.1, label='HOOK in the dark (fiddle, phrygian)')
        S.legato('hurdy', s, b, tr=-12, gain=0.5, pan=0.15)
        if k >= 2:
            S.flute(s, b, tr=12, vel=0.6, gain=0.45)
        S.chant(ANS_DARK, b + 4, group='ghost', gain=0.9, spread=0.04)
        S.ev(b + 4, 'melody', 'ghost-choir answer')
        if k == 1:
            S.place('msfx', I.crunch(1.0), S.t(b + 4 + 3.5), -0.2, 0.9)
            S.ev(b + 4 + 3.5, 'sfx', 'bread CRUNCH')
    ch3 += [(bar(32), 'Dm'), (bar(32) + 2, 'Bb'), (bar(33), 'E'), (bar(34), 'F'), (bar(34) + 2, 'E')]
    bell_pat = [(0, 'A4', 1.0), (0.75, 'E4', 0.7), (1.5, 'A4', 0.8), (2, 'C5', 0.7), (2.75, 'E4', 0.6), (3.5, 'A4', 0.7)]
    for i, bb in enumerate(range(24, 34)):
        b = bar(bb)
        groove(S, b, 'sin', i)
        S.strum("..x...x.", chord_at(ch3, b), b, gain=0.7); S.strum("..x...x.", chord_at(ch3, b + 2), b + 2, gain=0.7)
        for off, nt, v in bell_pat:
            n = nn(nt) + (1 if (chord_at(ch3, b + off) == 'Bb' and nt == 'A4') else 0)
            S.place('bells', I.handbell(n, v) + 0.0, S.t(b + off), 0.3 if off % 1 else -0.3, 0.55)
        if bb % 2 == 0:
            S.place('bells', I.church_bell(nn('A3'), 0.7, ring=2.0), S.t(b), 0, 0.45)
        S.place('drone', I.chien(nn('A3'), 0.8), S.t(b + 1.5), 0.2, 0.9)
        S.place('drone', I.chien(nn('A3'), 0.8), S.t(b + 3.5), 0.2, 0.9)
    S.ev(bar(24), 'section', 'church-bell ostinato = rhythmic hook (3-3-2)')
    S.flute(DBP1, bar(32), label='dark B-part (low flute over bells)')
    S.legato('fiddle', DBP1, bar(32), tr=-12, gain=0.6)
    S.flute(DBP2, bar(33))
    S.legato('fiddle', DBP2, bar(33), tr=-12, gain=0.6)
    S.chant([(0, 'OOH', 64, 8)], bar(32), group='ghost', gain=0.7)
    S.chant([(0, 'OOH', 63, 8)], bar(33), group='ghost', gain=0.7)
    # bar 34: build
    b = bar(34)
    S.drum("x.x.x.x.xxxxXXXX", b, 'davul', bus='folkdrums', gain=0.5)
    S.drum("xxxxxxxxxxxxXXXX", b, 'tamb', gain=0.5, pan=0.3)
    for k in range(8):
        S.place('bells', I.handbell(nn('A4') + [0, 3, 7, 12, 7, 12, 15, 19][k], 0.5 + 0.06 * k), S.t(b + k * 0.5), 0, 0.6)
    S.chant([(8, 'HEY', 57, 1), (10, 'HEY', 59, 1), (12, 'HEY', 60, 1), (14, 'HEY', 64, 1)], b, group='big')
    S.place('risers', I.riser(4 * SPB, f0=400, f1=10000), S.t(b), 0, 0.6)
    S.place('msfx', I.creak(0.8, 1.0), S.t(b), -0.4, 6.0)
    S.ev(b, 'sfx', 'door creak')
    S.bassline(BASS_D, ch3, bar(24), 10, punch=1.2, growl=0.5)
    S.bassline("!0:2 12:2 0:2 12:2 !0:1 12:1 0:1 12:1 0:1 12:1 0:1 12:1", ch3, bar(34), 1)

    # ================================================================ FINAL (bars 35-39)
    b0 = bar(35)
    S.place('risers', I.impact(1.0), S.t(b0), 0, 1.0)
    S.place('drums', I.crash(1.0, 1.6), S.t(b0), 0, 0.3)
    S.place('bells', I.church_bell(nn('A3'), 1.0, ring=2.5, big=True), S.t(b0), 0, 0.7)
    S.ev(b0, 'impact', 'FINAL DROP impact + bell')
    ch4 = []
    for k, bb in enumerate((35, 37)):
        b = bar(bb)
        ch4 += hook_chords(b)
        s = CALL3 if k == 0 else CALL2
        S.flute(s, b, gain=1.05, label='HOOK call (flute + fiddle + hurdy)')
        S.legato('fiddle', s, b, tr=-12, gain=0.7, pan=-0.25)
        S.legato('hurdy', s, b, tr=-12, harm=-2, gain=0.5, pan=0.25)
        S.chant(ANS2, b + 4, group='big', gain=1.1)
        S.brass(FAN, b + 4, gain=0.6)
        S.ev(b + 4, 'melody', 'VILLAGE ANSWER + fanfare')
    ch4 += [(bar(39), 'Am'), (bar(39) + 2, 'E')]
    for i, bb in enumerate(range(35, 39)):
        b = bar(bb)
        groove(S, b, 'final', i)
        S.strum("..x...x.", chord_at(ch4, b), b); S.strum("..x...x.", chord_at(ch4, b + 2), b + 2)
        S.place('bells', I.handbell(nn('A5'), 0.6), S.t(b), -0.3, 0.5)
    S.place('drone', I.hurdy_drone([nn('A2'), nn('E3')], 5 * BAR), S.t(b0), 0, 0.5)
    # bar 39: climax - village sings the hook rhythm WITH the flute, then two tutti hits
    b = bar(39)
    S.flute(CLIMAX, b, gain=1.1, label='CLIMAX: village sings the hook with the flute')
    S.legato('fiddle', CLIMAX, b, tr=-12, gain=0.7)
    S.brass("r:8 !E5:2 r:2 !A5:4", b, scale=AMIN, harm=(0, -2, -4))
    S.chant([(0, 'HEY', 64, 1), (2, 'ya', 64, 1), (3, 'HEY', 69, 1), (5, 'ya', 67, 1), (6, 'HOO', 64, 2),
             (8, 'HEY', 69, 2), (12, 'HA', 69, 3)], b, group='big', gain=1.1)
    S.drum("X...X...X...X...", b, 'kick')
    S.drum("X.......X...X...", b, 'davul', bus='folkdrums', gain=0.7)
    S.drum("X.......X...X...", b, 'stomp', bus='folkdrums')
    S.drum("....X...........", b, 'crowdclap')
    S.drum("gxXxgxXxX...X...", b, 'tamb', gain=0.55, pan=0.35)
    S.strum("x.x.x.x.X...X...", 'Am', b)
    S.ev(b + 2, 'accent', 'tutti HIT'); S.ev(b + 3, 'accent', 'tutti HIT')
    S.bassline(BASS, ch4, bar(35), 4, punch=1.6)
    S.bassline("r:2 !0:2 r:2 12:2 !0:2 r:2 !0:4", ch4, b, 1, punch=1.6)

    # ================================================================ TAIL 64.0-65.0 (2.5 beats) -> loop
    b = 160
    S.drum("X", b, 'kick'); S.drum("X", b, 'davul', bus='folkdrums', gain=0.8)
    S.strum("X", 'Am', b, gain=1.3, length=0.5)
    S.place('bells', I.church_bell(nn('A3'), 0.6, ring=1.0), S.t(b), 0, 0.4)
    S.chant([(0, 'HEY', 69, 2)], b, group='big')
    S.drum("....x.x.X.", b, 'glass_tap', bus='msfx', gain=1.0)
    S.ev(b + 1, 'sfx', 'tap'); S.ev(b + 1.5, 'sfx', 'tap'); S.ev(b + 2, 'sfx', 'TAP -> loop')

    # beat map extras
    S.ev(162.5, 'loop', 'LOOP POINT = 0:00')
    return S


# ------------------------------------------------------------------ mixing
MIX = {
    'kick': dict(gain=0.46, eq=[('hp', 30, 0.7), ('peak', 62, 1.0, 2.5), ('peak', 350, 1.2, -4)]),
    'drums': dict(gain=0.65, sc=0.1, rv2=0.12, eq=[('hp', 200), ('lp', 13000)]),
    'folkdrums': dict(gain=0.4, sc=0.05, rv2=0.18, eq=[('hp', 45), ('peak', 300, 1.0, -2)]),
    'bass': dict(gain=0.52, sc=0.7, eq=[('hp', 32), ('lp', 2500), ('peak', 180, 1.0, 2)], drive=1.4),
    'flute': dict(gain=0.46, sc=0.12, rv=0.16, dl=0.08, eq=[('hp', 300), ('peak', 2600, 1.0, 1.5)]),
    'fiddle': dict(gain=0.42, sc=0.2, rv=0.16, eq=[('hp', 180)], haas=0.009),
    'hurdy': dict(gain=0.35, sc=0.3, rv=0.15, eq=[('hp', 150), ('peak', 260, 0.9, 2)], haas=0.012),
    'lute': dict(gain=0.75, sc=0.4, rv=0.1, rv2=0.1, eq=[('hp', 160)], haas=0.012),
    'brass': dict(gain=0.22, sc=0.2, rv=0.2, rv2=0.1, eq=[('hp', 150), ('lp', 9000)]),
    'drone': dict(gain=0.32, sc=0.5, rv=0.2, eq=[('hp', 70), ('lp', 5000)], haas=0.02),
    'vox': dict(gain=0.95, sc=0.1, rv=0.14, rv2=0.2, eq=[('hp', 140), ('peak', 250, 1.0, -2), ('peak', 3000, 1.0, 2)]),
    'msfx': dict(gain=0.5, sc=0.05, rv2=0.2, eq=[('hp', 120)]),
    'bells': dict(gain=0.4, sc=0.2, rv=0.35, eq=[('hp', 90)]),
    'risers': dict(gain=0.35, rv=0.3),
}
