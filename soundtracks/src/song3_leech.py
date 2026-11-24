"""Candidate 3 - "Leech Collector"  (A minor, UK garage 2-step x electro swing, heavy 16th shuffle)
Personality: skippy 2-step kicks, sub bass with glides, a staccato
'tip-tip-TAP' clarinet hook answered by pitched vocal chops (call & response).
Section 2 switches to four-on-the-floor with a royal C-major trumpet fanfare
and an 'ah' choir; section 3 is A phrygian-dominant with sitar, kalimba and saw."""
from common import *

SW = dict(s16=0.62)

G1 = "!E5:1' r:1 E5:1' A5:2 r:1 G5:1' E5:1' r:2 C5:1 D5:1 (D#5)E5:2 r:2"
G3 = "!F5:1' r:1 F5:1' A5:2 r:1 G5:1' F5:1' r:2 D5:1 E5:1 F5:2 r:2"
G4 = "!G#5:1' r:1 G#5:1' B5:2 r:1 A5:1' G#5:1' r:1 F5:1 E5:1 D5:1 (D#5)E5:4"
G7 = "!E5:1' r:1 E5:1' A5:2 r:1 G5:1' E5:1' r:2 C6:1 B5:1 A5:2 r:2"
G8 = "!G#5:2 B5:2 D6:2 F6:2 E6:4 r:2 D6:1 B5:1"
TA = "A5:1 G5:1 F5:1 E5:1 D5:1 C5:1 B4:1 A4:1 G#4:2 B4:2 D5:2 E5:2"

V2 = [(2, 'A5', 2, 'a', 'h'), (5, 'G5', 1, 'o', None), (6, 'E5', 2, 'o', None),
      (10, 'C6', 1, 'a', 'd'), (11, 'C6', 1, 'a', 'd'), (12, 'B5', 3, 'ao', None)]
V6 = [(2, 'C6', 2, 'a', 'h'), (5, 'B5', 1, 'o', None), (6, 'G5', 2, 'o', None),
      (10, 'E6', 1, 'a', 'd'), (11, 'D6', 1, 'a', 'd'), (12, 'E6', 3, 'Ei', None)]

AMIN = [nn('A4') + i for i in (0, 2, 3, 5, 7, 8, 10)]
CMAJ = [nn('C4') + i for i in (0, 2, 4, 5, 7, 9, 11)]
AHARM = [nn('A4') + i for i in (0, 2, 3, 5, 7, 8, 11)]

BASS1 = "!0:3 r:1 0:1 r:2 12:1' r:2 10:2~ 7:2 r:2"
BASS2 = "!0:2 r:1 0:1 12:1' r:1 0:1 r:1 !0:2 r:1 7:1 10:1' r:1 12:2~"
BASS3 = "!0:3 r:1 1:2 r:2 0:1' r:1 0:2 -1:2 r:2"


def groove(S, b, kind, alt):
    if kind in ('d1', 's3'):
        S.drum("X.........X....." if not alt else "X......x..X....x", b, 'kick', decay=0.32, f_end=49, **SW)
    else:
        S.drum("X...X...X...X...", b, 'kick', decay=0.3, f_end=46)
    S.drum("....X.......X...", b, 'clap', gain=0.75, tone=1150)
    S.drum("....x.......x...", b, 'snare', gain=0.35, tone=210, **SW)
    if kind != 's3':
        S.drum("gxgxgxgxgxgxgxgx", b, 'hat', gain=0.55, pan=0.25, **SW)
        S.drum("..o.......o.....", b, 'hat', gain=0.45, decay=0.1, pan=-0.2, **SW)
    S.drum("...x..x....x..x." if not alt else "...x..x....x.x..", b, 'rim', gain=0.4, pan=-0.35, **SW)
    if kind == 's2':
        S.drum("....x.......x...", b, 'tamb', gain=0.35, pan=0.4, **SW)
    if kind == 'fin':
        S.drum("gogxgogxgogxgogx", b, 'shaker', gain=0.4, pan=0.4, **SW)
        S.drum("....x.......x...", b, 'tamb', gain=0.35, pan=-0.4, **SW)
    if kind == 's3':
        S.drum("g.gxg.g.g.gxg.gx", b, 'shaker', gain=0.4, pan=0.35, **SW)
        S.drum("x..x..x.......x.", b, 'bongo', gain=0.4, pan=-0.45, f=380, **SW)
        S.drum("......x...x.x...", b, 'castanet', gain=0.3, pan=0.5, **SW)


def build():
    S = Song('Leech Collector', seed=33)
    std_cues(S)
    L = lambda s, b, tr=0, vel=0.8, **k: S.lead(seq(s, b, tr=tr, vel=vel), **{**SW, **k})
    PZ = lambda s, b, g=0.8, tr=0: S.lead(seq(s, b, tr=tr), inst='pizz', bus='keys', pan=-0.3, gain=g, **SW)

    # ---------------- INTRO
    L(G1, 0, bus='vintage')
    S.lead(seq(G1, 0, tr=-12, vel=0.6), inst='pizz', bus='vintage', pan=0.3, gain=0.7, **SW)
    S.drum("....x.......x...", 0, 'snap', bus='vintage', gain=0.6, pan=-0.3)
    S.place('vintage', S.I.crackle(int(3 * SR), 9), 0.0, 0.0, 0.6)
    S.stabs("..X.....", 'E7b9', 4, fall_last=True, length=0.22, **SW)
    S.vchop([(5, 'B5', 1, 'a', 'd'), (6, 'B5', 1, 'a', 'd')], 4)
    L("r:4 B4:1' C5:1' D5:2", 4)
    S.drum("....xxXX", 4, 'snare', gain=0.3)
    S.place('fx', S.I.riser(2 * SPB, f0=800), S.t(4))
    S.place('drums', S.I.crash(0.9), S.t(D1), 0.0, 0.45)
    S.place('fx', S.I.impact(0.9), S.t(D1), 0.0, 0.7)

    # ---------------- DROP 1 (2-step)
    ch1 = [(6, 'Am7'), (10, 'Am7'), (14, 'Dm9'), (18, 'E7b9'), (22, 'Am7'), (26, 'Am7'), (30, 'Fmaj7'), (34, 'E7b9'), (38, 'Dm7'), (40, 'E7b9')]
    plan = [G1, V2, G3, G4, G1, V6, G7, G8, TA]
    for i, b in enumerate(bars(D1, 9)):
        groove(S, b, 'd1', i % 2)
        p = plan[i]
        sym = [c for c in ch1 if c[0] <= b][-1][1]
        if isinstance(p, str):
            L(p, b)
            if i < 8:
                PZ(p, b, 0.45, -12)
        else:
            S.vchop(p, b, **SW)
            S.stabs("......x.......x.", sym, b, **SW)
        if i < 8:
            S.comp("...x..x....x..x.", sym, b, inst='piano', low=nn('G3'), gain=0.9, **SW)
    S.stabs("X..x....", 'Dm7', 38, **SW)
    S.stabs("o.x.xxXX", 'E7b9', 40, **SW)
    S.vchop([(0, 'A5', 1, 'a', 'd'), (1, 'A5', 1, 'a', 'd'), (2, 'A5', 1, 'a', 'd'), (3, 'A5', 1, 'a', 'd'),
             (4, 'C6', 2, 'o', None), (8, 'B5', 1, 'a', 'd'), (9, 'B5', 1, 'a', 'd'), (10, 'D6', 2, 'o', None)], 38, gain=0.8, **SW)
    S.bassline(rseq(" | ".join([BASS1] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:2 12:2", D1), ch1, upright=0.4, synth=1.0, growl=0.4, **SW)
    turnaround_fill(S, 38, crash_next=False)

    # ---------------- BREAK: vocal stutter + reversed-feel swoosh
    S.stabs("X.......", 'Am7', 42, fall_last=True, length=0.25, **SW)
    S.vchop([(2, 'E5', 1, 'a', 'd'), (3, 'E5', 1, 'a', 'd'), (4, 'A5', 1, 'a', 'd'), (5, 'C6', 2, 'ao', None)], 42, **SW)
    S.place('fx', S.I.swoosh(2 * SPB), S.t(42))
    S.drum("......xX", 42, 'kick', gain=0.8)
    S.place('drums', S.I.crash(1.0), S.t(S2), 0.0, 0.5)
    S.place('fx', S.I.impact(1.0), S.t(S2), 0.0, 0.8)

    # ---------------- SECTION 2: four-on-floor, royal C major fanfare + 'ah' choir
    ch2 = [(44, 'F'), (48, 'G'), (52, 'Em7'), (56, 'Am'), (60, 'F'), (64, 'G'), (68, 'E7'), (72, 'Am'), (76, 'Dm7'), (78, 'E7b9')]
    T1 = "!C5:1' r:1 C5:1' F5:2 r:1 E5:1' C5:1' r:2 A4:1 B4:1 C5:2 r:2"
    T2 = "!D5:4 r:4 !G5:1.3333 G5:1.3333 G5:1.3334 B5:4"
    T3 = "!B4:1' r:1 B4:1' E5:2 r:1 D5:1' B4:1' r:2 G4:1 A4:1 B4:2 r:2"
    sec = lambda s, b, sc: S.section(seq(s, b, tr=12), [0, -2, -4], sc, octave_double=True, **SW)
    for i, b in enumerate(bars(S2, 9)):
        groove(S, b, 's2', 0)
        sym = [c for c in ch2 if c[0] <= b][-1][1]
        if i < 8:
            S.comp("...x..x....x..x.", sym, b, inst='piano', low=nn('G3'), gain=0.9, **SW)
            for k, n in enumerate(voicing(sym, nn('E4'), 3)):
                S.place('vox', S.I.vox(n, 4 * SPB * 0.95, 0.5, vowels='ao', cons='h', scoop=0.2), S.t(b), [-0.5, 0, 0.5][k], 0.45)
    sec(T1, 44, CMAJ); sec(T2, 48, CMAJ); sec(T3, 52, CMAJ); L(G1, 56, gain=1.1)
    sec(T1, 60, CMAJ); sec(T2, 64, CMAJ)
    sec("!G#4:2 E4:2 B3:2 E4:2 G#4:2 B4:2 D5:4", 68, AHARM)
    sec("!A4:4_ E4:2 A4:2 C5:3 B4:1 A4:2 r:2", 72, AMIN)
    L("r:2 !C6:2\\ r:4 B5:1' A5:1' G5:1' E5:1' D5:2 C5:2", 48)
    L("r:2 !D6:2\\ r:4 C6:1' B5:1' A5:1' G5:1' E5:2 D5:2", 64)
    S.stabs("X..X..X.", 'Dm7', 76, length=0.18, **SW)
    S.stabs("o.x.xxXX", 'E7b9', 78, **SW)
    L("!G#5:1 A5:1 G#5:1 A5:1 B5:1 C6:1 D6:1 E6:1 F6:1 G#6:1 !A6:4 r:2", 76)
    for b, n in ((44, 'F2'), (60, 'F2'), (72, 'A2')):
        S.place('drums', S.I.timpani(nn(n), 0.9), S.t(b), 0.0, 0.5)
    for k, b in enumerate(np.arange(78, 80, 0.25)):
        S.place('drums', S.I.timpani(nn('E2'), 0.5 + 0.06 * k), S.t(b), 0.0, 0.3)
    S.drum("xxxxxxxxXXXXXXXX", 76, 'snare', gain=0.3)
    S.bassline(rseq(" | ".join([BASS2] * 9), S2), ch2, upright=0.5, synth=1.0, punch=1.6, growl=0.5, **SW)
    S.place('fx', S.I.riser(4 * SPB, f1=12000), S.t(76))

    # ---------------- FAKE-OUT: tape stop -> lone vocal 'hm?' -> kalimba tiptoe
    S.vchop([(2, 'E5', 3, 'u', None), (5, 'G#5', 2, 'u', None)], 80, bus='post', slide=1)
    S.lead(seq("E4:1' F4:1' G#4:1' B4:1'", 81), inst='kalimba', bus='post', gain=1.0)

    # ---------------- SECTION 3: A phrygian-dominant mystery
    ch3 = [(82, 'Am'), (86, 'Bb'), (90, 'Am'), (94, 'E7b9'), (98, 'Am'), (102, 'Bb'), (106, 'Dm'), (110, 'E7b9'), (114, 'Bb'), (116, 'E7b9')]
    M1 = "!E4:1' r:1 E4:1' A4:2 r:1 G#4:1' F4:1' r:2 E4:1 F4:1 G#4:2 r:2"
    M2 = "!F4:1' r:1 F4:1' Bb4:2 r:1 A4:1' F4:1' r:2 D4:1 E4:1 F4:2 r:2"
    M4 = "!G#4:1' r:1 G#4:1' B4:2 r:1 A4:1' G#4:1' r:1 F4:1 E4:1 D4:1 (D#4)E4:4"
    M7 = "!F4:1' r:1 F4:1' A4:2 r:1 G#4:1' F4:1' r:2 D4:1 E4:1 F4:2 r:2"
    RUN = "E4:1 F4:1 G#4:1 A4:1 B4:1 C5:1 D5:1 E5:1 F5:1 G#5:1 A5:1 B5:1 C6:1 D6:1 !E6:2"
    mel = [M1, M2, M1, M4, M1, M2, M7, M4, RUN]
    for i, b in enumerate(bars(S3, 9)):
        groove(S, b, 's3', i % 2)
        sym = [c for c in ch3 if c[0] <= b][-1][1]
        if i < 8:
            S.lead(seq(mel[i], b), inst='sitar', bus='lead', gain=0.9, pan=-0.1, **SW)
            if i in (2, 3, 6, 7):
                L(mel[i], b, gain=0.8, bright_mul=0.8)
            r = 57 + (chord(sym)[0] - 9) % 12
            notes = [r, r + 7, r + 12, r + 7 + 12, r + 12, r + 7]
            arp_ev = [dict(t=b + k * 0.75, d=0.5, n=notes[k % len(notes)] + (3 if chord(sym)[1][1] == 3 else 4) * (k % 3 == 2),
                           v=0.6, gr=None, gl=False, fall=False, scoop=False, stac=False, ten=False) for k in range(5)]
            S.lead(arp_ev, inst='kalimba', bus='tex', pan=0.45, gain=0.7, **SW)
        else:
            L(mel[i], b)
    S.vchop([(2, 'E5', 2, 'u', None), (6, 'F5', 2, 'u', None), (10, 'E5', 4, 'uo', None)], 86, gain=0.7, **SW)
    S.vchop([(2, 'E5', 2, 'u', None), (6, 'F5', 2, 'u', None), (10, 'G#5', 4, 'uo', None)], 102, gain=0.7, **SW)
    S.lead(seq("E6:16 | F6:16 | E6:16 | D6:8 B5:8 | E6:16 | F6:12 E6:4 | D6:16 | G#5:16", S3, vel=0.5),
           inst='saw', bus='tex', pan=-0.25, gain=0.6)
    S.bassline(rseq(" | ".join([BASS3] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:1 12:1 0:1 12:1", S3), ch3, upright=0.6, synth=1.0, growl=0.6, **SW)
    turnaround_fill(S, 114, crash_next=False)

    # ---------------- FINAL (four-on-floor + garage shuffle, everything)
    ch4 = [(118, 'Am7'), (122, 'Am7'), (126, 'Dm9'), (130, 'E7b9'), (134, 'Am7'), (138, 'Am7'), (140, 'E7b9'), (142, 'E7b9')]
    S.place('drums', S.I.crash(1.0, 1.8), S.t(FIN), 0.0, 0.55)
    S.place('fx', S.I.impact(1.0), S.t(FIN), 0.0, 0.9)
    S.place('drums', S.I.crash(0.8), S.t(134), 0.0, 0.4)
    plan = {118: (G1, AMIN), 122: V2, 126: (G3, AMIN), 130: (G4, AHARM), 134: (G1, AMIN), 138: V6}
    for i, b in enumerate(bars(FIN, 6)):
        groove(S, b, 'fin', i % 2)
        sym = [c for c in ch4 if c[0] <= b][-1][1]
        S.comp("...x..x....x..x.", sym, b, inst='piano', low=nn('G3'), gain=0.9, **SW)
        p = plan[b]
        if isinstance(p, tuple):
            L(p[0], b, gain=1.1)
            S.section(seq(p[0], b), [-2, -4], p[1], gain=0.7, **SW)
            PZ(p[0], b, 0.5, -12)
        else:
            S.vchop(p, b, gain=1.1, **SW)
            S.stabs("..X...X...X.X...", sym, b, **SW)
            S.lead(seq("r:2 E5:1' r:1 A5:1' r:3 C6:1' r:1 B5:1' r:1 G#5:2 r:1", b), inst='pluck', bus='keys', pan=0.3, gain=0.6, **SW)
    S.stabs("X..X..XX", 'E7b9', 140, **SW)
    S.drum("X.......", 142, 'kick')
    S.stabs("X.......", 'E7b9', 142, fall_last=True, length=0.3, **SW)
    S.vchop([(0, 'B5', 3, 'a', 'h')], 142)
    L("r:4 B4:1' C5:1' D5:2", 142)
    S.bassline(rseq(" | ".join([BASS2] * 6) + " | !0:4", FIN), ch4, upright=0.5, synth=1.0, punch=1.7, growl=0.5, **SW)

    cfg = mixcfg(keys=dict(gain=0.18), vox=dict(gain=0.24), tex=dict(gain=0.32), sub=dict(gain=0.32))
    return S, cfg, dict(tape_stop=(S.t(FAKE), 0.55, S.t(S3) - 0.01), automation=AUTO)
