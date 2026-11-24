"""Candidate 4 - "Knocker-Upper"  (Eb major -> C minor, Charleston electro swing, tick-tock clock)
Personality: a big-interval 'da-da DAAAH' clarinet hook, a 'ring-ring-ring-ring'
repeated-note alarm-clock answer, Charleston brass hits, tick-tock woodblock
clock on every beat, and 'hey!' vocal answers. Section 2 = royal procession
in Ab with chimes and timpani; section 3 = C minor music-box mystery."""
from common import *

SW = dict(s8=0.6)

K1 = "!Eb5:1' G5:1' Bb5:4 C6:2 r:2 !Bb5:1' G5:1' Eb5:4"
K3 = "!F5:1' Ab5:1' C6:4 Db6:2 r:2 !C6:1' Ab5:1' F5:4"
K4 = "!D6:1' D6:1' D6:1' D6:1' C6:2 Bb5:2 Ab5:2 F5:2 D5:2 Bb4:2"
K7 = "!F5:1' Ab5:1' C6:4 Db6:2 !D6:1' D6:1' D6:1' D6:1' C6:2 Bb5:2"
K8 = "!Eb6:4_ Bb5:2 G5:2 Eb5:2 r:2 Bb4:1 C5:1 D5:2"
TA = "C6:1 Bb5:1 Ab5:1 G5:1 F5:1 Eb5:1 D5:1 C5:1 Bb4:2 D5:2 F5:2 Ab5:2"

EBMAJ = [nn('Eb4') + i for i in (0, 2, 4, 5, 7, 9, 10)]   # Eb mixolydian flavour (Db)
EBION = [nn('Eb4') + i for i in (0, 2, 4, 5, 7, 9, 11)]
CHARM = [nn('C4') + i for i in (0, 2, 3, 5, 7, 8, 11)]

BASS1 = "!0:2 r:2 7:2 r:2 12:2 r:2 7:1' 9:1 10:2"
BASS2 = "!0:2 12:1' r:1 7:2 12:1' r:1 !0:2 12:1' r:1 10:1 9:1 7:1 4:1"
BASS3 = "!0:3 0:1' r:2 -1:2 0:2 r:2 3:1' 2:1 -1:2"


def groove(S, b, kind):
    S.drum("X...X...X...X...", b, 'kick', decay=0.3)
    S.drum("....X.......X...", b, 'clap', gain=0.8, tone=1300)
    S.drum("x.......x.......", b, 'tick', gain=0.5, pan=-0.45)
    S.drum("....x.......x...", b, 'tick', gain=0.5, pan=0.45, tock=True)
    if kind != 's3':
        S.drum("..x...x...x...x.", b, 'hat', gain=0.55, decay=0.09, **SW)
        S.drum("x.gxx.gxx.gxx.gx", b, 'hat', gain=0.4, pan=0.2, **SW)
    if kind in ('s2', 'fin'):
        S.drum("..x...x...x...x.", b, 'tamb', gain=0.35, pan=-0.35, **SW)
    if kind == 's2':
        S.drum("x.gg..g.x.gg..gg", b, 'snare', gain=0.22, pan=0.15, **SW)
    if kind == 's3':
        S.drum("..o...o...o...o.", b, 'hat', gain=0.35, decay=0.06, **SW)
        S.drum("x..x..x.x..x..x.", b, 'castanet', gain=0.3, pan=0.45, **SW)
        S.drum("......x.......xx", b, 'bongo', gain=0.4, pan=-0.4, f=350, **SW)
    if kind == 'fin':
        S.drum("gogxgogxgogxgogx", b, 'shaker', gain=0.35, pan=0.35, s16=0.58)


def build():
    S = Song('Knocker-Upper', seed=44)
    std_cues(S)
    L = lambda s, b, tr=0, vel=0.8, **k: S.lead(seq(s, b, tr=tr, vel=vel), **{**SW, **k})
    hey = lambda b, step, note='Bb5', **k: S.vchop([(step, note, 2, 'Ei', 'h')], b, gain=1.6, **{**SW, **k})

    # ---------------- INTRO
    L(K1, 0, bus='vintage')
    S.lead(seq(K1, 0, tr=-12, vel=0.5), inst='piano', bus='vintage', pan=0.3, gain=1.2, **SW)
    S.drum("x...x...x...x...", 0, 'tick', bus='vintage', gain=0.5, pan=-0.3)
    S.place('vintage', S.I.crackle(int(3 * SR), 9), 0.0, 0.0, 0.6)
    S.place('tex', S.I.bell(nn('C7'), 0.6, dur=2 * SPB * 0.8), S.t(4), 0.3, 0.35)
    S.stabs("X.....X.", 'Bb7', 4, fall_last=True, length=0.2, **SW)
    L("r:4 Bb4:1' C5:1' D5:2", 4)
    S.drum("....xxXX", 4, 'snare', gain=0.3)
    S.place('drums', S.I.crash(0.9), S.t(D1), 0.0, 0.45)
    S.place('fx', S.I.impact(0.9), S.t(D1), 0.0, 0.7)

    # ---------------- DROP 1
    ch1 = [(6, 'Eb'), (10, 'C7'), (14, 'Fm7'), (18, 'Bb7'), (22, 'Eb'), (26, 'C7'), (30, 'Fm7'), (32, 'Bb7'), (34, 'Eb'), (38, 'Ab'), (40, 'Bb7')]
    plan = [K1, 'r1', K3, K4, K1, 'r2', K7, K8, TA]
    for i, b in enumerate(bars(D1, 9)):
        groove(S, b, 'd1')
        p = plan[i]
        sym = [c for c in ch1 if c[0] <= b][-1][1]
        if p == 'r1':
            S.stabs("X.....X.........", 'C7', b, **SW)
            hey(b, 10, 'G5'); S.drum("............x.x.", b, 'wood', gain=0.6, pan=0.3, f=1100)
            S.lead(seq("r:12 G5:1' E5:1' C5:2", b), inst='pluck', bus='keys', gain=0.9, pan=0.3, **SW)
        elif p == 'r2':
            S.stabs("X.....X...X.....", 'C7', b, **SW)
            hey(b, 10, 'G5'); hey(b, 12, 'Bb5')
            S.lead(seq("r:12 Bb5:1' G5:1' E5:2", b), inst='pluck', bus='keys', gain=0.9, pan=0.3, **SW)
        else:
            L(p, b)
            if i < 8:
                S.stabs("X.....X.........", sym, b, gain=0.6, **SW)
        if i < 8:
            if sym == 'Fm7' and b == 30:
                S.comp("....x...", 'Fm7', b, low=nn('G3'), **SW); S.comp("....x...", 'Bb7', b + 2, low=nn('G3'), **SW)
            else:
                S.comp("....x.......x...", sym, b, low=nn('G3'), **SW)
                S.comp("..x...x...x...x.", sym, b, low=nn('Bb4'), gain=0.5, **SW)
    S.stabs("X..X....", 'Ab', 38, **SW)
    S.stabs("o.x.xxXX", 'Bb7', 40, **SW)
    S.bassline(rseq(" | ".join([BASS1] * 8) + " | !0:2 12:2 7:2 12:2 !0:2 12:2 7:2 12:2", D1), ch1, **SW)
    turnaround_fill(S, 38, crash_next=False)

    # ---------------- BREAK: alarm bell rings, everyone freezes
    S.stabs("X.......", 'Eb', 42, fall_last=True, length=0.25, **SW)
    S.place('tex', S.I.bell(nn('C7'), 0.7, dur=SPB * 1.2), S.t(42.5), 0.3, 0.4)
    hey(42, 6, 'Eb6')
    S.drum("......xX", 42, 'kick', gain=0.8)
    S.place('drums', S.I.crash(1.0), S.t(S2), 0.0, 0.5)
    S.place('fx', S.I.impact(1.0), S.t(S2), 0.0, 0.8)

    # ---------------- SECTION 2: royal procession in Ab
    ch2 = [(44, 'Ab'), (48, 'Eb'), (52, 'Bb7'), (56, 'Eb'), (60, 'Ab'), (64, 'Eb'), (68, 'Fm7'), (70, 'Bb7'), (72, 'Eb'), (76, 'Ab'), (78, 'G7')]
    T1 = "!Ab5:3 G5:1 Ab5:4 Bb5:3 Ab5:1 G5:2 F5:2"
    T3 = "!F5:3 Eb5:1 D5:4 F5:3 Ab5:1 Bb5:4"
    T4 = "!Bb5:1' Bb5:1' Bb5:1' Bb5:1' G5:2 Eb5:2 r:2 Bb4:1 C5:1 Eb5:4"
    sec = lambda s, b, sc, v=(0, -2, -4): S.section(seq(s, b), list(v), sc, octave_double=True, **SW)
    for i, b in enumerate(bars(S2, 9)):
        groove(S, b, 's2')
        sym = [c for c in ch2 if c[0] <= b][-1][1]
        if i < 8:
            S.comp("....x.......x...", sym, b, low=nn('G3'), **SW)
            S.comp("..x...x...x...x.", sym, b, low=nn('Bb4'), gain=0.5, **SW)
            S.lead([dict(t=b, d=2, n=bass_root(sym, nn('E5')) + 12, v=0.6, gr=None, gl=False, fall=False, scoop=False, stac=False, ten=False)],
                   inst='glock', bus='tex', pan=0.4, gain=0.5)
    sec(T1, 44, EBION); L(K1, 48); S.stabs("X.....X.........", 'Eb', 48, gain=0.6, **SW)
    sec(T3, 52, EBMAJ); L(T4, 56)
    sec(T1, 60, EBION); L(K1, 64, tr=0); S.stabs("X.....X...X.....", 'Eb', 64, gain=0.6, **SW); hey(64, 12, 'Bb5')
    sec("!Ab5:2 C6:2 F6:2 C6:2", 68, EBION, (0, -2)); sec("!Bb5:2 D6:2 F6:2 D6:2", 70, EBMAJ, (0, -2))
    sec("!Eb6:4_ Bb5:2 G5:2 Bb5:3 Ab5:1 G5:2 r:2", 72, EBION, (0, -2))
    S.stabs("X..X..X.", 'Ab', 76, length=0.18, **SW)
    S.stabs("o.x.xxXX", 'G7', 78, **SW)
    L("!F#5:1 G5:1 F#5:1 G5:1 Ab5:1 B5:1 D6:1 F6:1 !G6:4 r:4", 76)
    for b, n in ((44, 'Ab2'), (60, 'Ab2'), (72, 'Eb2')):
        S.place('drums', S.I.timpani(nn(n), 0.9), S.t(b), 0.0, 0.5)
    for k, b in enumerate(np.arange(78, 80, 0.25)):
        S.place('drums', S.I.timpani(nn('G2'), 0.5 + 0.06 * k), S.t(b), 0.0, 0.3)
    S.drum("xxxxxxxxXXXXXXXX", 76, 'snare', gain=0.3)
    S.bassline(rseq(" | ".join([BASS2] * 9), S2), ch2, punch=1.5, **SW)
    S.place('fx', S.I.riser(4 * SPB, f1=12000), S.t(76))

    # ---------------- FAKE-OUT: alarm stops dead; a yawn; tiptoe music box
    S.vchop([(1, 'G5', 6, 'aou', 'h')], 80, bus='post', slide=-7, scoop=0.0)
    S.lead(seq("G4:1' C5:1' Eb5:1' G5:1'", 81), inst='musicbox', bus='post', gain=0.8)

    # ---------------- SECTION 3: C minor music box mystery
    ch3 = [(82, 'Cm'), (86, 'Cm'), (90, 'Ab7'), (94, 'G7b9'), (98, 'Cm'), (102, 'Fm'), (106, 'Ab7'), (110, 'G7b9'), (114, 'Ab7'), (116, 'G7b9')]
    M1 = "!C5:1' Eb5:1' G5:4 Ab5:2 r:2 !G5:1' Eb5:1' C5:4"
    M3 = "!Eb5:1' Gb5:1' C6:4 Db6:2 r:2 !C6:1' Ab5:1' Eb5:4"
    M4 = "!B5:1' B5:1' B5:1' B5:1' Ab5:2 G5:2 F5:2 D5:2 B4:2 G4:2"
    R2 = "r:2 G5:2 Ab5:2 B5:2 C6:4 r:2 B5:1 G5:1"
    RUN = "G4:1 Ab4:1 B4:1 C5:1 D5:1 Eb5:1 F5:1 G5:1 Ab5:1 B5:1 C6:1 D6:1 !Eb6:2 D6:1 B5:1"
    mel = [M1, R2, M3, M4, M1, R2, M3, M4, RUN]
    for i, b in enumerate(bars(S3, 9)):
        groove(S, b, 's3')
        sym = [c for c in ch3 if c[0] <= b][-1][1]
        m = mel[i]
        if i == 8:
            L(m, b)
        elif m is R2:
            S.lead(seq(m, b), inst='theremin', bus='tex', pan=0.2, gain=0.8)
            S.lead(seq(m, b, tr=-12), inst='mute', bus='brass', pan=-0.3, gain=0.6, **SW)
        else:
            S.lead(seq(m, b, tr=12), inst='musicbox', bus='lead', gain=0.5, pan=0.15, **SW)
            L(m, b, tr=-12, gain=0.9, bright_mul=0.85)
        if i < 8:
            r = bass_root(sym, nn('C4'))
            pz = [r, r + 7, r + 12, r + 7]
            S.lead([dict(t=b + k * 0.5, d=0.5, n=pz[k % 4], v=0.7 if k % 2 == 0 else 0.5, gr=None, gl=False, fall=False,
                         scoop=False, stac=True, ten=False) for k in range(8)], inst='pizz', bus='keys', pan=-0.35, gain=0.6, **SW)
    S.bassline(rseq(" | ".join([BASS3] * 8) + " | !0:2 12:2 0:2 12:2 !0:2 12:2 0:1 12:1 0:1 12:1", S3), ch3, punch=1.2, **SW)
    S.vchop([(14, 'G5', 2, 'u', None)], 94)
    S.vchop([(12, 'G5', 2, 'u', None), (14, 'Ab5', 2, 'u', None)], 110)
    turnaround_fill(S, 114, crash_next=False)

    # ---------------- FINAL
    ch4 = [(118, 'Eb'), (122, 'C7'), (126, 'Fm7'), (130, 'Bb7'), (134, 'Eb'), (138, 'Eb'), (140, 'Bb7'), (142, 'Bb7')]
    S.place('drums', S.I.crash(1.0, 1.8), S.t(FIN), 0.0, 0.55)
    S.place('fx', S.I.impact(1.0), S.t(FIN), 0.0, 0.9)
    S.place('tex', S.I.bell(nn('C7'), 0.6, dur=4 * SPB), S.t(FIN), 0.35, 0.25)
    S.place('drums', S.I.crash(0.8), S.t(134), 0.0, 0.4)
    plan = {118: (K1, EBION), 126: (K3, EBMAJ), 130: (K4, EBMAJ), 134: (K1, EBION)}
    for b in bars(FIN, 6):
        groove(S, b, 'fin')
        sym = [c for c in ch4 if c[0] <= b][-1][1]
        S.comp("....x.......x...", sym, b, low=nn('G3'), **SW)
        S.comp("..x...x...x...x.", sym, b, low=nn('Bb4'), gain=0.5, **SW)
        if b in plan:
            h, sc = plan[b]
            L(h, b, gain=1.1)
            S.section(seq(h, b), [-2, -4], sc, gain=0.7, **SW)
            S.stabs("X.....X.........", sym, b, gain=0.6, **SW)
    S.stabs("X.....X...X.X...", 'C7', 122, **SW)
    hey(122, 10, 'G5'); hey(122, 12, 'Bb5'); hey(122, 14, 'C6')
    S.lead(seq("r:12 G5:1' E5:1' C5:2", 122), inst='pluck', bus='keys', gain=0.9, pan=0.3, **SW)
    L("!Eb6:4_ Bb5:2 G5:2 !D6:1' D6:1' D6:1' D6:1' F6:4", 138, gain=1.1)
    S.stabs("X.....X.", 'Eb', 138, **SW)
    S.stabs("X..X..XX", 'Bb7', 140, **SW)
    S.drum("X.......", 142, 'kick')
    S.stabs("X.......", 'Bb7', 142, fall_last=True, length=0.3, **SW)
    hey(142, 0, 'Bb5')
    L("r:4 Bb4:1' C5:1' D5:2", 142)
    S.bassline(rseq(" | ".join([BASS2] * 6) + " | !0:4", FIN), ch4, punch=1.6, **SW)

    cfg = mixcfg(tex=dict(gain=0.32))
    return S, cfg, dict(tape_stop=(S.t(FAKE), 0.55, S.t(S3) - 0.01), automation=AUTO)
