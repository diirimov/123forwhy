"""Candidate 1 - "Pickpocket Shuffle"  (G minor, electro swing, swung 8ths)
Personality: classic electro-swing oom-pah bounce, tresillo-shaped descending
clarinet hook, brass 'BAP-BAP' answers, pluck echoes. Royal Bb-major brass in
section 2, G harmonic-minor 'snake charmer' mystery in section 3."""
from common import *

SW = dict(s8=0.62)

H1 = "!G5:3 F5:3 D5:2 (E5)F5:1 D5:1 C5:1 Bb4:1 r:2 G4:2"
H3 = "!G5:3 F5:3 Eb5:2 (F#5)G5:1 Eb5:1 C5:1 Bb4:1 r:2 C5:2"
H4 = "!A5:2 r:1 F#5:1' r:1 A5:1 C6:2 Bb5:1 A5:1 G5:1 F#5:1 D5:2 r:2"
H7 = "!G5:3 F5:3 Eb5:2 (E5)F5:1 G5:1 Bb5:1 C6:1 r:1 Db6:1 C6:2"
H8 = "!Bb5:2 A5:2 F#5:2 A5:1 (C#6)D6:3 r:2 C6:1 A5:1 F#5:1 r:1"
H9 = "Eb5:1 G5:1 C6:1 Eb6:1 D6:2 C6:1 Bb5:1 A5:1 C6:1 F#5:1 A5:1 D5:4"
ANS1 = "r:8 D5:1' r:1 Bb4:1' r:1 G4:2 A4:1 Bb4:1"
ANS2 = "r:8 G5:1' r:1 F5:1' r:1 D5:2 (C#5)D5:1 F5:1"

GMIN = [nn('G4') + i for i in (0, 2, 3, 5, 7, 8, 10)]
GHARM = [nn('G4') + i for i in (0, 2, 3, 5, 7, 8, 11)]
BMAJ = [nn('Bb4') + i for i in (0, 2, 4, 5, 7, 9, 11)]

BASS1 = "!0:3 12:1' r:2 7:2 !0:3 12:1' r:2 10:1 12:1"
BASS2 = "!0:2 12:1' 0:1 r:2 7:1' 12:1 !0:2 12:1' 0:1 r:2 10:1' 12:1"
BASS3 = "!0:2 r:1 0:1 r:2 1:2 0:2 r:2 -2:1 0:1 r:2"


def groove(S, b, kind='d1'):
    S.drum("X...x...X...x...", b, 'kick')
    S.drum("....X.......X...", b, 'clap', gain=0.8)
    if kind in ('d1', 's2', 'fin'):
        S.drum("..x...x...x...x.", b, 'hat', gain=0.55, decay=0.09, **SW)
        S.drum("x..gx..gx..gx..g", b, 'hat', gain=0.45, **SW)
    if kind in ('s2', 'fin'):
        S.drum("....x.......x...", b, 'tamb', gain=0.4, pan=0.35)
    if kind == 's2':
        S.drum("..g...gg..g...gg", b, 'snare', gain=0.22, pan=-0.2, **SW)
    if kind == 'fin':
        S.drum("gogxgogxgogxgogx", b, 'shaker', gain=0.35, pan=-0.4, s16=0.58)
        S.drum("...............x", b, 'rim', gain=0.4, pan=0.3)
    if kind == 's3':
        S.drum("..x..x.x..x..x.x", b, 'castanet', gain=0.35, pan=0.45, **SW)
        S.drum("x..x..x...x.x...", b, 'bongo', gain=0.4, pan=-0.45, f=440, **SW)
        S.drum("......x.......x.", b, 'bongo', gain=0.35, pan=-0.3, f=330, **SW)
        S.drum("gogxgogxgogxgogx", b, 'shaker', gain=0.3, pan=0.2, s16=0.58)


def build():
    S = Song('Pickpocket Shuffle', seed=11)
    std_cues(S)
    L = lambda s, b, tr=0, vel=0.8, **k: S.lead(seq(s, b, tr=tr, vel=vel), **{**SW, **k})

    # ---------------- INTRO 0-6 : gramophone-filtered hook, space for voice-over
    L(H1, 0, bus='vintage')
    S.lead(seq(H1, 0, tr=-12, vel=0.5), inst='pluck', bus='vintage', pan=0.3, gain=0.45, **SW)
    S.drum("....x.......x...", 0, 'snap', bus='vintage', gain=0.6, pan=-0.3)
    S.place('vintage', S.I.crackle(int(3 * SR), 9), 0.0, 0.0, 0.6)
    S.bassline(rseq("!0:3 r:5 7:3 r:5"), [(0, 'Gm')], synth=0, upright=0.7, **SW)
    S.stabs("..X.....", 'D7', 4, fall_last=True, length=0.22, **SW)
    L("r:4 D5:1' E5:1' F#5:2", 4)
    S.drum("....oxxX", 4, 'snare', gain=0.3)
    S.place('fx', S.I.riser(2 * SPB, f0=800), S.t(4))
    S.place('drums', S.I.crash(0.9), S.t(D1), 0.0, 0.45)
    S.place('fx', S.I.impact(0.9), S.t(D1), 0.0, 0.7)

    # ---------------- DROP 1 6-42
    ch1 = [(6, 'Gm'), (10, 'Gm'), (14, 'Cm'), (18, 'D7'), (22, 'Gm'), (26, 'Gm'), (30, 'Eb7'), (34, 'D7'), (38, 'Cm'), (40, 'D7')]
    hooks = [H1, None, H3, H4, H1, None, H7, H8, H9]
    for i, b in enumerate(bars(D1, 9)):
        groove(S, b, 'd1')
        if hooks[i]:
            L(hooks[i], b)
        sym = [c for c in ch1 if c[0] <= b][-1][1]
        if i < 8:
            S.comp("..x...x...x...x.", sym, b, low=nn('G3'), **SW)
    S.lead(seq(H1, 6, tr=-12, vel=0.45), inst='pluck', bus='keys', pan=0.35, gain=0.5, **SW)
    S.lead(seq(ANS1, 10), inst='pluck', bus='keys', pan=0.25, gain=0.9, **SW)
    S.lead(seq(ANS2, 26), inst='pluck', bus='keys', pan=0.25, gain=0.9, **SW)
    S.stabs("..X...X.........", 'Gm', 10, **SW)
    S.stabs("X.........x.....", 'D7', 18, **SW)
    S.stabs("..X...X...X.X...", 'Gm', 26, **SW)
    S.stabs("X......X........", 'D7', 34, **SW)
    S.stabs("X..x....", 'Cm', 38, **SW)
    S.stabs("o.x.xxXX", 'D7', 40, **SW)
    S.comp("x...x...", 'Cm', 38, low=nn('G3'), **SW)
    S.vchop([(14, 'D5', 2, 'a', 'h')], 18)
    S.vchop([(10, 'G5', 2, 'Ei', 'h'), (14, 'A5', 2, 'a', 'h')], 34)
    S.bassline(rseq(" | ".join([BASS1] * 8) + " | !0:2 12:2 7:2 12:2 !0:2 12:2 7:2 12:2", D1), ch1, **SW)
    turnaround_fill(S, 38, crash_next=False)

    # ---------------- BREAK 42-44 (stop-time)
    S.stabs("X.......", 'Gm', 42, fall_last=True, length=0.25, **SW)
    S.vchop([(3, 'G5', 2, 'a', 'h')], 42)
    L("r:4 Bb4:1 C5:1 D5:1 F5:1", 42)
    S.drum("......xX", 42, 'kick', gain=0.8)
    S.place('drums', S.I.crash(1.0), S.t(S2), 0.0, 0.5)
    S.place('fx', S.I.impact(1.0), S.t(S2), 0.0, 0.8)

    # ---------------- SECTION 2 44-80: royal brass (Bb major colour), heavier bass
    ch2 = [(44, 'Eb'), (48, 'Bb'), (52, 'Cm'), (56, 'D7'), (60, 'Eb'), (64, 'Bb'), (68, 'Cm'), (70, 'D7'), (72, 'Gm'), (76, 'Ab'), (78, 'D7')]
    T1 = "!G5:3 F5:3 Eb5:2 F5:1 G5:1 Bb5:1 G5:1 r:2 Eb5:2"
    T2 = "r:12 !F5:1.3333 F5:1.3333 F5:1.3334"
    T3 = "!G5:3 F5:3 Eb5:2 F5:1 G5:1 C6:1 G5:1 r:2 Eb5:2"
    T4 = "!F#5:2 r:1 F#5:1' r:1 A5:1 C6:2 r:1 D6:1 C6:1 A5:1 F#5:2 D5:2"
    C2 = "r:2 D6:1' r:1 Bb5:1' r:1 F5:2 G5:1 Bb5:1 D6:3 r:3"
    C6 = "r:2 Eb6:1' r:1 C6:1' r:1 G5:2 Bb5:1 C6:1 Eb6:3 r:3"
    for i, b in enumerate(bars(S2, 9)):
        groove(S, b, 's2')
        sym = [c for c in ch2 if c[0] <= b][-1][1]
        if i < 8:
            S.comp("..x...x...x...x.", sym, b, low=nn('G3'), **SW)
    sec = lambda s, b, sc: S.section(seq(s, b), [0, -2], sc, octave_double=True, **SW)
    sec(T1, 44, GMIN); sec(T2, 48, BMAJ); sec(T3, 52, GMIN); sec(T4, 56, GHARM)
    sec(T1, 60, GMIN); sec(T2, 64, BMAJ)
    sec("!G5:2 Eb5:2 C6:2 G5:2", 68, GMIN); sec("!A5:2 F#5:2 D6:2 A5:2", 70, GHARM)
    sec("!G5:4_ D5:2 G5:2 Bb5:3 A5:1 G5:2 r:2", 72, GMIN)
    L(C2, 48); L(C6, 64)
    L("r:8 C6:1 D6:1 Eb6:1 F6:1 (F#6)G6:4", 72)
    S.stabs("X..X..X.", 'Ab', 76, length=0.18, **SW)
    S.stabs("o.x.xxXX", 'D7', 78, **SW)
    L("!A5:1 Bb5:1 A5:1 Bb5:1 A5:1 Bb5:1 A5:1 Bb5:1 C6:1 D6:1 Eb6:1 F#6:1 !G6:4", 76)
    for b in (44, 60, 72):
        S.place('drums', S.I.timpani(nn('G2') if b == 72 else nn('Eb2'), 0.9), S.t(b), 0.0, 0.5)
    S.drum("xxxxxxxxXXXXXXXX", 76, 'snare', gain=0.3)
    for k, b in enumerate(np.arange(78, 80, 0.25)):
        S.place('drums', S.I.timpani(nn('D2'), 0.5 + 0.06 * k), S.t(b), 0.0, 0.3)
    S.vchop([(12, 'D5', 2, 'a', 'h'), (14, 'G5', 2, 'Ei', 'h')], 56)
    S.vchop([(2, 'Bb5', 2, 'o', 'h'), (6, 'G5', 2, 'o', 'h')], 64)
    S.bassline(rseq(" | ".join([BASS2] * 9), S2), ch2, punch=1.5, **SW)
    S.place('fx', S.I.riser(4 * SPB, f1=12000), S.t(76))

    # ---------------- FAKE-OUT 80-82 (tape stop, then a sly tiptoe)
    S.vchop([(2, 'E5', 2, 'a', 'h'), (4, 'C5', 3, 'o', None)], 80, bus='post')
    S.place('post', S.I.boing(nn('G3'), 0.6), S.t(80.25), 0.2, 0.6)
    S.lead(seq("D4:1' Eb4:1' F#4:1' r:1", 81), inst='pizz', bus='post', gain=0.9)
    S.drum("x.x.", 81, 'castanet', bus='post', gain=0.5, pan=0.4)

    # ---------------- SECTION 3 82-118: G harmonic minor mystery
    ch3 = [(82, 'Gm'), (86, 'Gm'), (90, 'Ab'), (94, 'D7b9'), (98, 'Gm'), (102, 'Eb'), (106, 'Ab'), (110, 'D7b9'), (114, 'Ab'), (116, 'D7b9')]
    M1 = "!G4:3 F#4:3 D4:2 Eb4:1 D4:1 C4:1 Bb3:1 r:2 G3:2"
    M3 = "!Ab4:3 G4:3 Eb4:2 F4:1 Eb4:1 C4:1 Ab3:1 r:2 C4:2"
    M4 = "!F#4:2 r:1 A4:1' r:1 C5:1 Eb5:3 D5:1 C5:1 A4:1 F#4:1 D4:3"
    M7 = "!Ab4:3 G4:3 Eb4:2 F4:1 G4:1 Ab4:1 C5:1 r:1 Eb5:1 D5:2"
    M8 = "!F#4:2 G4:2 A4:2 Bb4:1 (B4)C5:3 r:1 Eb5:1 D5:1 C5:1 A4:2"
    RUN = "D4:1 Eb4:1 F#4:1 G4:1 A4:1 Bb4:1 C5:1 D5:1 Eb5:1 F#5:1 G5:1 A5:1 Bb5:1 C6:1 !D6:2"
    mel = [M1, None, M3, M4, M1, None, M7, M8, RUN]
    pz = [0, -5, -4, -5, 0, -5, -6, -5]
    for i, b in enumerate(bars(S3, 9)):
        groove(S, b, 's3')
        if mel[i]:
            L(mel[i], b, bright_mul=0.85)
        sym = [c for c in ch3 if c[0] <= b][-1][1]
        root = 60 + chord(sym)[0]
        if root > 66:
            root -= 12
        if i < 8:
            S.lead([dict(t=b + k * 0.5, d=0.5, n=root + p + 12 if p < -5 else root + p + 12, v=0.7 if k % 2 == 0 else 0.5,
                         gr=None, gl=False, fall=False, scoop=False, stac=True, ten=False) for k, p in enumerate(pz)],
                   inst='pizz', bus='keys', pan=-0.35, gain=0.55, **SW)
            S.comp("x.......x.......", sym, b, inst='vibes', low=nn('D5'), bus='tex', gain=0.6, length=0.8)
    S.lead(seq("r:2 D5:1' Eb5:1' r:2 F#5:2 G5:3 r:1 F#5:1 Eb5:1 D5:2", 86), inst='mute', bus='brass', pan=0.3, gain=0.8, **SW)
    S.lead(seq("r:2 G5:1' Bb5:1' r:2 D6:2 Eb6:3 r:1 D6:1 Bb5:1 G5:2", 102), inst='mute', bus='brass', pan=0.3, gain=0.8, **SW)
    S.lead(seq(M1, 98, tr=12, vel=0.5), inst='mute', bus='brass', pan=-0.3, gain=0.45, **SW)
    S.lead(seq("G5:14 A5:2 | Bb5:16 | Ab5:16 | F#5:16 | G5:16 | G5:16 | Ab5:12 C6:4 | A5:16 | C6:8 D6:8", 82, vel=0.5),
           inst='theremin', bus='tex', pan=0.2, gain=0.55)
    S.bassline(rseq(" | ".join([BASS3] * 8) + " | !0:2 0:2 12:2 0:2 !0:2 12:2 0:1 12:1 0:1 12:1", S3), ch3, punch=1.2, **SW)
    S.vchop([(14, 'D5', 2, 'u', None)], 94)
    S.vchop([(14, 'D5', 2, 'u', None), (15, 'Eb5', 1, 'u', None)], 110)
    turnaround_fill(S, 114, crash_next=False)

    # ---------------- FINAL 118-144: everything, hook back on top
    ch4 = [(118, 'Gm'), (122, 'Gm'), (126, 'Cm'), (130, 'D7'), (134, 'Gm'), (138, 'Gm'), (140, 'D7'), (142, 'D7')]
    S.place('drums', S.I.crash(1.0, 1.8), S.t(FIN), 0.0, 0.55)
    S.place('fx', S.I.impact(1.0), S.t(FIN), 0.0, 0.9)
    S.place('drums', S.I.crash(0.8), S.t(134), 0.0, 0.4)
    fin_hooks = {118: (H1, GMIN), 126: (H3, GMIN), 130: (H4, GHARM), 134: (H1, GMIN)}
    for i, b in enumerate(bars(FIN, 6)):
        groove(S, b, 'fin')
        sym = [c for c in ch4 if c[0] <= b][-1][1]
        S.comp("..x...x...x...x.", sym, b, low=nn('G3'), **SW)
        if b in fin_hooks:
            h, sc = fin_hooks[b]
            L(h, b, gain=1.1)
            S.section(seq(h, b), [-2, -4], sc, gain=0.8, **SW)
    S.stabs("..X...X...X.X...", 'Gm', 122, **SW)
    S.vchop([(2, 'D5', 2, 'Ei', 'h'), (6, 'D5', 2, 'Ei', 'h'), (10, 'G5', 1, 'a', 'b'), (12, 'Bb5', 3, 'ao', 'h')], 122)
    S.lead(seq(ANS1, 122), inst='pluck', bus='keys', pan=0.25, gain=1.0, **SW)
    L("!G5:3 F5:3 D5:2 !A5:2 F#5:2 !D6:4", 138, gain=1.1)
    S.stabs("X..X..X.", 'Gm', 138, **SW)
    S.stabs("X..X..XX", 'D7', 140, **SW)
    S.vchop([(0, 'G5', 2, 'a', 'h'), (8, 'A5', 2, 'Ei', 'h')], 138)
    # 142-144: stop-time pickup that loops into the intro
    S.drum("X.......", 142, 'kick')
    S.stabs("X.......", 'D7', 142, fall_last=True, length=0.3, **SW)
    S.vchop([(0, 'A5', 3, 'a', 'h')], 142)
    L("r:4 D5:1' E5:1' F#5:2", 142)
    S.bassline(rseq(" | ".join([BASS2] * 6) + " | !0:4", FIN), ch4, punch=1.6, **SW)
    S.lead(seq(H1, 118, tr=-12, vel=0.5), inst='pluck', bus='keys', pan=-0.35, gain=0.5, **SW)
    S.lead(seq(H1, 134, tr=-12, vel=0.5), inst='pluck', bus='keys', pan=-0.35, gain=0.5, **SW)

    cfg = mixcfg()
    return S, cfg, dict(tape_stop=(S.t(FAKE), 0.55, S.t(S3) - 0.01), automation=AUTO)
