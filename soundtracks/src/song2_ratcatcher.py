"""Candidate 2 - "Royal Rat Catcher"  (F major -> D minor, funky house, straight-ish 16ths)
Personality: a sticky pentatonic 'da-da-DAH' pluck hook with a blue note,
the clarinet answers with sassy fall-offs, brass pushes every bar on the
'and of 4'. Section 2 = baroque harpsichord + trumpet fanfare + timpani;
section 3 = D harmonic-minor with musical saw, marimba and tuba."""
from common import *

SW = dict(s16=0.55)

P1 = "!C5:1 D5:1 F5:2' r:2 C5:1 D5:1 (G#5)A5:3 r:1 G5:1 F5:1 D5:2"
C2 = "r:2 !C6:2\\ r:2 A5:1 C6:1 r:1 A5:1 G5:1 F5:1 (Eb5)E5:2 C5:2"
P3 = "!F5:1 G5:1 Bb5:2' r:2 F5:1 G5:1 (C#6)D6:3 r:1 C6:1 Bb5:1 Ab5:2"
C4 = "r:2 !E5:2 G5:2 Bb5:2 (B5)C6:4 r:2 Bb5:1 G5:1"
C6 = "r:2 !C6:2\\ r:2 A5:1 C6:1 r:1 D6:1 C6:1 A5:1 G5:2 F5:2"
C8 = "!E6:1' r:1 C6:1' r:1 Bb5:1 G5:1 E5:1 C5:1 r:2 (C#5)D5:1 E5:1 G5:2 Bb5:2"
TA = "G5:1 F5:1 D5:1 F5:1 G5:2 Bb5:2 C6:1 Bb5:1 G5:1 E5:1 C5:2 E5:1 G5:1"

FMAJ = [nn('F4') + i for i in (0, 2, 4, 5, 7, 9, 10)]   # F mixolydian (Eb) for the bluesy brass
FION = [nn('F4') + i for i in (0, 2, 4, 5, 7, 9, 11)]
DHARM = [nn('D4') + i for i in (0, 2, 3, 5, 7, 8, 11)]

BASS1 = "!0:2 r:1 12:1' r:1 0:1 10:1 12:1' r:2 0:1' 12:1 r:1 7:1 10:1 12:1"
BASS2 = "!0:2 12:1' 0:1 r:1 0:1 12:1' 10:1 r:1 12:1' 0:2 7:1 10:1 12:2"
BASS3 = "!0:3 r:1 0:1 r:1 7:2 r:2 0:1' 0:1 -2:2 -1:2"


def groove(S, b, kind):
    S.drum("X...X...X...X...", b, 'kick', decay=0.26, f_end=48)
    S.drum("....X.......X...", b, 'clap', gain=0.8, tone=1400)
    if kind != 's3':
        S.drum("..X...X...X...X.", b, 'hat', gain=0.5, decay=0.11, **SW)
        S.drum("xgxgxgxgxgxgxgxg", b, 'shaker', gain=0.45, pan=0.35, **SW)
        S.drum("......g......g..", b, 'snare', gain=0.25, pan=-0.1, **SW)
    if kind in ('s2', 'fin'):
        S.drum("....x.......x..x", b, 'tamb', gain=0.4, pan=-0.35, **SW)
    if kind == 's2':
        S.drum("x.gg..g.x.gg..g.", b, 'snare', gain=0.2, pan=0.15, **SW)
    if kind == 's3':
        S.drum("..o...o...o...o.", b, 'hat', gain=0.35, decay=0.07, **SW)
        S.drum("x..x..x...x..x..", b, 'wood', gain=0.35, pan=0.5, f=780, **SW)
        S.drum("..x.....x.x...x.", b, 'bongo', gain=0.45, pan=-0.45, f=300, **SW)
        S.drum("g.g.g.ggg.g.g.gg", b, 'shaker', gain=0.35, pan=0.25, **SW)
    if kind == 'fin':
        S.drum("..g...g...g...g.", b, 'rim', gain=0.35, pan=0.4, **SW)


def arp(S, sym, b, low, bus='keys', gain=0.5, inst='harpsichord', steps=16, pan=-0.3):
    notes = voicing(sym, low) + [n + 12 for n in voicing(sym, low)]
    order = notes + notes[-2:0:-1]
    ev = [dict(t=b + k * 0.25, d=0.25, n=order[k % len(order)], v=0.75 if k % 4 == 0 else 0.55,
               gr=None, gl=False, fall=False, scoop=False, stac=False, ten=False) for k in range(steps)]
    S.lead(ev, inst=inst, bus=bus, pan=pan, gain=gain, **SW)


def build():
    S = Song('Royal Rat Catcher', seed=22)
    std_cues(S)
    L = lambda s, b, tr=0, vel=0.8, **k: S.lead(seq(s, b, tr=tr, vel=vel), **{**SW, **k})
    PL = lambda s, b, g=1.0, tr=0, pan=0.15: S.lead(seq(s, b, tr=tr), inst='pluck', bus='lead', pan=pan, gain=g * 1.25, **SW)

    def push(sym, b, v='X'):
        S.stabs("..............%s." % v, sym, b, length=0.16, **SW)

    # ---------------- INTRO
    S.lead(seq(P1, 0), inst='pluck', bus='vintage', gain=1.3, **SW)
    S.lead(seq(P1, 0, tr=12, vel=0.45), inst='clarinet', bus='vintage', gain=0.5, **SW)
    S.drum("x...x...x...x...", 0, 'snap', bus='vintage', gain=0.5, pan=-0.3)
    S.place('vintage', S.I.crackle(int(3 * SR), 9), 0.0, 0.0, 0.6)
    S.stabs("..X.....", 'C7', 4, fall_last=True, length=0.22, **SW)
    L("r:4 G4:1' A4:1' Bb4:2", 4)
    S.drum("....xxXX", 4, 'snare', gain=0.3)
    S.place('fx', S.I.riser(2 * SPB, f0=800), S.t(4))
    S.place('drums', S.I.crash(0.9), S.t(D1), 0.0, 0.45)
    S.place('fx', S.I.impact(0.9), S.t(D1), 0.0, 0.7)

    # ---------------- DROP 1
    ch1 = [(6, 'F'), (10, 'F'), (14, 'Bb7'), (18, 'C7'), (22, 'F'), (26, 'F'), (30, 'Bb7'), (34, 'C7'), (38, 'Gm7'), (40, 'C7')]
    seqs = [('p', P1), ('c', C2), ('p', P3), ('c', C4), ('p', P1), ('c', C6), ('p', P3), ('c', C8), ('u', TA)]
    nxt = ['F', 'Bb7', 'C7', 'F', 'F', 'Bb7', 'C7', 'Gm7']
    for i, b in enumerate(bars(D1, 9)):
        groove(S, b, 'd1')
        kind, s = seqs[i]
        if kind == 'p':
            PL(s, b)
            S.lead(seq(s, b, tr=-12, vel=0.4), inst='pluck', bus='keys', pan=-0.4, gain=0.6, **SW)
        elif kind == 'c':
            L(s, b)
        else:
            L(s, b); PL(s, b, 0.7, -12)
        sym = [c for c in ch1 if c[0] <= b][-1][1]
        if i < 8:
            S.comp("..x..x....x..x..", sym, b, inst='pluck', low=nn('A3'), gain=0.8, pan=0.4, **SW)
            push(nxt[i], b, 'X' if i % 2 else 'x')
    S.stabs("X..X....", 'Gm7', 38, **SW)
    S.stabs("o.x.xxXX", 'C7', 40, **SW)
    S.vchop([(12, 'C5', 2, 'ua', None), (14, 'F5', 2, 'a', 'h')], 18)
    S.vchop([(10, 'A5', 1, 'a', 'd'), (11, 'A5', 1, 'a', 'd'), (12, 'C6', 3, 'ao', 'h')], 34)
    S.bassline(rseq(" | ".join([BASS1] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:2 12:2", D1), ch1, **SW)
    turnaround_fill(S, 38, crash_next=False)

    # ---------------- BREAK (everything stops; pluck & clarinet trade one-beat licks)
    S.stabs("X.......", 'C7', 42, fall_last=True, length=0.25, **SW)
    PL("r:2 C6:1' Bb5:1' G5:1' r:3", 42, 0.9)
    L("r:5 E5:1 F5:1 F#5:1", 42)
    S.vchop([(4, 'G5', 1, 'a', 'b')], 42)
    S.drum("......xX", 42, 'kick', gain=0.8)
    S.place('drums', S.I.crash(1.0), S.t(S2), 0.0, 0.5)
    S.place('fx', S.I.impact(1.0), S.t(S2), 0.0, 0.8)

    # ---------------- SECTION 2: royal fanfare, harpsichord, timpani
    ch2 = [(44, 'Bb'), (48, 'F'), (52, 'Gm7'), (56, 'C7'), (60, 'Bb'), (64, 'F'), (68, 'Gm7'), (70, 'C7'), (72, 'F'), (76, 'Bb'), (78, 'C7')]
    T1 = "!F5:2 F5:1.3333 F5:1.3333 F5:1.3334 Bb5:4 r:2 D6:1 C6:1 Bb5:2"
    T3 = "!D6:2 D6:1.3333 D6:1.3333 D6:1.3334 Bb5:4 r:2 G5:1 A5:1 Bb5:2"
    sec = lambda s, b, sc: S.section(seq(s, b), [0, -2], sc, octave_double=True, **SW)
    for i, b in enumerate(bars(S2, 9)):
        groove(S, b, 's2')
        sym = [c for c in ch2 if c[0] <= b][-1][1]
        if i < 8:
            arp(S, sym, b, nn('F4'), gain=0.45)
            if i == 6:
                arp(S, 'C7', b + 2, nn('F4'), gain=0.45, steps=8)
    sec(T1, 44, FION); PL(P1, 48); L(P1, 48, tr=12, vel=0.5, gain=0.5)
    sec(T3, 52, FION); L(C4, 56)
    sec(T1, 60, FION); PL(P1, 64); L(P1, 64, tr=12, vel=0.5, gain=0.5)
    sec("!Bb5:2 A5:2 G5:2 D6:2", 68, FION); sec("!C6:2 Bb5:2 G5:2 E5:2", 70, FMAJ)
    sec("!F5:4_ C5:2 F5:2 A5:3 G5:1 F5:2 r:2", 72, FION)
    for b, s in ((48, 'F'), (56, 'C7'), (64, 'F')):
        S.stabs("..x.......x...X.", s, b, **SW)
    S.stabs("X..X..X.", 'Bb', 76, length=0.18, **SW)
    S.stabs("o.x.xxXX", 'C7', 78, **SW)
    L("!E5:1 F5:1 E5:1 F5:1 G5:1 A5:1 Bb5:1 C6:1 D6:1 E6:1 !F6:4 r:2", 76)
    for b, n in ((44, 'Bb1'), (60, 'Bb1'), (72, 'F2')):
        S.place('drums', S.I.timpani(nn(n) + 12, 0.9), S.t(b), 0.0, 0.5)
    for k, b in enumerate(np.arange(78, 80, 0.25)):
        S.place('drums', S.I.timpani(nn('C3'), 0.5 + 0.06 * k), S.t(b), 0.0, 0.3)
    S.drum("xxxxxxxxXXXXXXXX", 76, 'snare', gain=0.3)
    S.vchop([(2, 'F5', 2, 'o', 'h'), (6, 'A5', 2, 'o', 'h'), (10, 'C6', 4, 'oa', 'h')], 72)
    S.bassline(rseq(" | ".join([BASS2] * 9), S2), ch2, punch=1.6, **SW)
    S.place('fx', S.I.riser(4 * SPB, f1=12000), S.t(76))

    # ---------------- FAKE-OUT
    S.vchop([(1, 'C6', 1, 'a', 'd'), (2, 'Bb5', 1, 'a', 'd'), (3, 'G5', 4, 'u', None)], 80, bus='post', slide=-5)
    S.place('post', S.I.boing(nn('F3'), 0.6), S.t(80.5), -0.2, 0.6)
    S.lead(seq("A3:1' D4:1' F4:1' A4:1'", 81), inst='marimba', bus='post', gain=1.0)

    # ---------------- SECTION 3: D harmonic minor, saw + marimba + tuba
    ch3 = [(82, 'Dm'), (86, 'Dm'), (90, 'Bb'), (94, 'A7'), (98, 'Dm'), (102, 'Gm'), (106, 'Bb'), (110, 'A7b9'), (114, 'Bb'), (116, 'A7b9')]
    M1 = "!A4:1 Bb4:1 D5:2' r:2 A4:1 Bb4:1 (C#5)D5:3 r:1 C#5:1 Bb4:1 A4:2"
    M3 = "!D5:1 F5:1 Bb5:2' r:2 D5:1 F5:1 (G5)A5:3 r:1 G5:1 F5:1 D5:2"
    R2 = "r:2 F5:2\\ r:2 D5:1 F5:1 r:1 D5:1 C#5:1 Bb4:1 A4:2 r:2"
    R4 = "r:2 !E5:2 G5:2 Bb5:2 (B5)C#6:4 r:2 Bb5:1 G5:1"
    RUN = "A4:1 Bb4:1 C#5:1 D5:1 E5:1 F5:1 G5:1 A5:1 Bb5:1 C#6:1 D6:1 E6:1 !F6:2 E6:1 C#6:1"
    mel = [('m', M1), ('r', R2), ('m', M3), ('r', R4), ('m', M1), ('r', R2), ('m', M3), ('r', R4), ('u', RUN)]
    for i, b in enumerate(bars(S3, 9)):
        groove(S, b, 's3')
        k, s = mel[i]
        if k == 'm':
            S.lead(seq(s, b), inst='marimba', bus='lead', gain=1.1, pan=0.1, **SW)
            L(s, b, tr=-12, gain=0.8, bright_mul=0.8)
        elif k == 'r':
            S.lead(seq(s, b), inst='mute', bus='brass', gain=1.0, pan=0.3, **SW)
        else:
            L(s, b)
        sym = [c for c in ch3 if c[0] <= b][-1][1]
        if i < 8:
            r = bass_root(sym, nn('E1'))
            S.lead(seq(f"!{_n(r)}:6 {_n(r+7)}:2 {_n(r)}:4 {_n(r+7)}:2 {_n(r+12)}:2", b), inst='tuba', bus='bass', gain=0.3, **SW)
            S.comp("x.......x.......", sym, b, inst='vibes', low=nn('A4'), bus='tex', gain=0.45, length=0.6)
    S.lead(seq("D6:16 | C#6:16 | D6:8 F6:8 | E6:16 | A6:16 | G6:16 | F6:12 D6:4 | E6:16", 82, vel=0.55),
           inst='saw', bus='tex', pan=-0.2, gain=0.6)
    S.bassline(rseq(" | ".join([BASS3] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:1 12:1 0:1 12:1", S3), ch3, upright=0.9, synth=0.6, **SW)
    S.vchop([(14, 'A5', 2, 'u', None)], 94)
    S.vchop([(12, 'D5', 2, 'u', None), (14, 'C#5', 2, 'u', None)], 110)
    turnaround_fill(S, 114, crash_next=False)

    # ---------------- FINAL
    ch4 = [(118, 'F'), (122, 'F'), (126, 'Bb7'), (130, 'C7'), (134, 'F'), (138, 'F'), (140, 'C7'), (142, 'C7')]
    S.place('drums', S.I.crash(1.0, 1.8), S.t(FIN), 0.0, 0.55)
    S.place('fx', S.I.impact(1.0), S.t(FIN), 0.0, 0.9)
    S.place('drums', S.I.crash(0.8), S.t(134), 0.0, 0.4)
    plan = {118: ('p', P1), 122: ('c', C2), 126: ('p', P3), 130: ('c', C4), 134: ('p', P1)}
    nxt = {118: 'F', 122: 'Bb7', 126: 'C7', 130: 'F', 134: 'F'}
    for b in bars(FIN, 6):
        groove(S, b, 'fin')
        sym = [c for c in ch4 if c[0] <= b][-1][1]
        S.comp("..x..x....x..x..", sym, b, inst='pluck', low=nn('A3'), gain=0.8, pan=0.4, **SW)
        if b in plan:
            k, s = plan[b]
            if k == 'p':
                PL(s, b); L(s, b, tr=12, vel=0.6, gain=0.6)
                S.section(seq(s, b), [0, -2], FMAJ, gain=0.6, **SW)
            else:
                L(s, b, gain=1.1)
                S.stabs("X.....X.........", sym, b, **SW)
            push(nxt[b], b)
        if b != 138:
            arp(S, sym, b, nn('F5'), gain=0.25, pan=0.5)
    S.vchop([(2, 'F5', 2, 'Ei', 'h'), (6, 'A5', 2, 'Ei', 'h')], 122)
    S.vchop([(10, 'C6', 1, 'a', 'd'), (11, 'C6', 1, 'a', 'd'), (12, 'C6', 3, 'ao', 'h')], 130)
    L("!C6:2 A5:2 F5:2 C6:2 !Bb5:2 G5:2 E5:2 C5:2", 138, gain=1.1)
    PL("!C6:2 A5:2 F5:2 C6:2 !Bb5:2 G5:2 E5:2 C5:2", 138, 0.8, -12)
    S.stabs("X..X..X.", 'F', 138, **SW)
    S.stabs("X..X..XX", 'C7', 140, **SW)
    S.drum("X.......", 142, 'kick')
    S.stabs("X.......", 'C7', 142, fall_last=True, length=0.3, **SW)
    S.vchop([(0, 'G5', 3, 'a', 'h')], 142)
    L("r:4 G4:1' A4:1' Bb4:2", 142)
    S.bassline(rseq(" | ".join([BASS2] * 6) + " | !0:4", FIN), ch4, punch=1.7, **SW)

    cfg = mixcfg(lead=dict(gain=0.32), keys=dict(gain=0.7), vox=dict(gain=0.22), tex=dict(gain=0.3))
    return S, cfg, dict(tape_stop=(S.t(FAKE), 0.55, S.t(S3) - 0.01), automation=AUTO)


_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def _n(m):
    return f'{_NAMES[m % 12]}{m // 12 - 1}'
