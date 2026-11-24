"""THE DARKEST CHRISTMAS LEGENDS - composition (note events).
All times are in 16th-note steps from song start. 128 BPM, 48 bars, 4/4.
Event: (step, dur_steps, midi, vel 0..1)
"""
import random
random.seed(1225)

BARS = 48
EV = {}           # track name -> list of events
MARK = []         # (step, label) for markers / sync sheet

def add(tr, step, dur, pitch, vel=0.8):
    EV.setdefault(tr, []).append((float(step), float(dur), int(pitch), float(vel)))

def mark(bar, step, label):
    MARK.append(((bar - 1) * 16 + step, label))

def B(bar):  # first step of 1-indexed bar
    return (bar - 1) * 16

# ---------------------------------------------------------------- harmony
# chord per bar: (bass root midi, chord tones as pitch classes above root, quality)
D, Eb, E, F, G, A, Bb, Bn, C = 38, 39, 40, 41, 31, 33, 34, 35, 36
MIN, MAJ, DOM = (0, 3, 7), (0, 4, 7), (0, 4, 7, 10)
CH = {}
def setch(bar, root, q): CH[bar] = (root, q)
prog_main = [(D, MIN), (Bb, MAJ), (C, MAJ), (A, MAJ)]
prog_cat = [(D, MIN), (G, MIN), (C, MAJ), (A, MAJ)]
prog_mari1 = [(D, MIN), (Eb, MAJ), (D, MIN), (A, DOM)]
prog_mari2 = [(G, MIN), (Eb, MAJ), (C, MAJ), (A, DOM)]
prog_build = [(G, MIN), (Bb, MAJ), (C, MAJ), (Bn, DOM)]
prog_final = [(E, MIN), (C, MAJ), (D, MAJ), (Bn, MAJ)]
for i in range(4): setch(1 + i, *prog_main[i])
for k in range(3):
    for i in range(4): setch(5 + 4 * k + i, *prog_main[i])
for k in range(3):
    for i in range(4): setch(17 + 4 * k + i, *prog_cat[i])
for i in range(4): setch(29 + i, *prog_mari1[i])
for i in range(4): setch(33 + i, *prog_mari2[i])
for i in range(4): setch(37 + i, *prog_build[i])
for k in range(2):
    for i in range(4): setch(41 + 4 * k + i, *prog_final[i])
setch(47, D, MAJ)   # D (2 beats) -> B (2 beats), handled in bass
setch(48, E, MIN)

def tones(bar, octave_from=60, step=0):
    r, q = CH[bar]
    if bar == 47 and step >= 8: r, q = Bn, MAJ
    return [octave_from + ((r + iv) - octave_from) % 12 for iv in q]

# ---------------------------------------------------------------- THE HOOK
# 4-bar hook in D minor. (step, dur, midi)
HOOK = [
    [(0, 2, 69), (2, 1, 74), (3, 1, 74), (4, 2, 77), (6, 1, 76), (7, 1, 74), (8, 3, 81), (11, 1, 79), (12, 2, 77), (14, 2, 76)],
    [(0, 1, 77), (1, 1, 76), (2, 2, 74), (4, 2, 70), (6, 2, 74), (8, 4, 77)],
    [(0, 2, 69), (2, 1, 74), (3, 1, 74), (4, 2, 77), (6, 1, 76), (7, 1, 74), (8, 3, 84), (11, 1, 82), (12, 2, 81), (14, 2, 79)],
    [(0, 1, 79), (1, 1, 77), (2, 2, 76), (4, 2, 73), (6, 1, 76), (7, 1, 73), (8, 4, 69)],
]
# the cheeky "giggle" answer in the holes of hook bars 2 and 4
ANSWER = {1: [(12, 1, 82), (13, 1, 81), (14, 1, 77), (15, 1, 74)],
          3: [(12, 1, 88), (13, 1, 85), (14, 1, 81), (15, 1, 76)]}

def hook(tr, bar0, vel=0.85, transpose=0, octave=0, staccato=None, bars=(0, 1, 2, 3), accent=True):
    for i in bars:
        for (s, d, p) in HOOK[i]:
            dd = d if staccato is None else min(d, staccato)
            v = vel * (1.0 if (s % 4 == 0 or not accent) else 0.86)
            add(tr, B(bar0 + i) + s, dd, p + transpose + 12 * octave, v)

def answer(tr, bar0, vel=0.75, transpose=0, octave=0, which=(1, 3)):
    for i in which:
        for (s, d, p) in ANSWER[i]:
            add(tr, B(bar0 + i) + s, d, p + transpose + 12 * octave, vel * (1 if s == 12 else 0.85))

# Yule-Cat variant: same contour, staccato, every other note leaps up an octave
def cat_hook(tr, bar0, vel=0.85, transpose=0):
    for i in range(4):
        for j, (s, d, p) in enumerate(HOOK[i]):
            add(tr, B(bar0 + i) + s, 1, p + transpose + (12 if j % 2 == 1 else 0), vel * (1 if j % 2 == 0 else 0.8))
            if d >= 3:  # fill long notes with a pounce repeat
                add(tr, B(bar0 + i) + s + 2, 1, p + transpose + 12, vel * 0.7)

# Fiddle reel (chaotic Krampus variation), one 16-note figure per chord bar
REEL = {
    0: [69, 74, 77, 74, 81, 77, 74, 77, 76, 74, 73, 74, 69, 74, 77, 81],
    1: [82, 81, 77, 74, 70, 74, 77, 74, 82, 81, 77, 81, 79, 77, 76, 77],
    2: [79, 76, 72, 76, 79, 84, 79, 76, 77, 76, 74, 72, 74, 76, 77, 79],
    3: [81, 76, 73, 76, 81, 85, 88, 85, 81, 79, 77, 76, 73, 76, 73, 69],
}
def reel(tr, bar0, vel=0.78, transpose=0, nbars=4):
    for i in range(nbars):
        for s, p in enumerate(REEL[i]):
            add(tr, B(bar0 + i) + s, 1, p + transpose, vel * (1 if s % 4 == 0 else 0.78 if s % 2 == 0 else 0.68))

# Mari Lwyd melody: call (fiddle) & response (accordion / bells). Phrygian b2 = eerie.
MARI_CALL = {
    0: [(0, 2, 69), (2, 1, 74), (3, 1, 74), (4, 3, 77), (7, 1, 75), (8, 4, 74)],
    2: [(0, 2, 81), (2, 1, 82), (3, 1, 81), (4, 2, 77), (6, 2, 74), (8, 2, 75), (10, 2, 74), (12, 4, 73)],
}
MARI_RESP = {
    1: [(0, 1, 79), (1, 1, 77), (2, 2, 75), (4, 2, 70), (6, 2, 75), (8, 2, 79), (10, 2, 82), (12, 3, 79)],
    3: [(0, 1, 76), (2, 1, 73), (3, 1, 70), (4, 2, 69), (6, 1, 73), (7, 1, 76), (8, 2, 79), (10, 2, 76), (12, 2, 73), (14, 2, 69)],
}
MARI_CALL2 = {  # second half, over Gm Eb C A
    0: [(0, 2, 74), (2, 1, 79), (3, 1, 79), (4, 3, 82), (7, 1, 81), (8, 2, 79), (10, 2, 74), (12, 4, 70)],
    2: [(0, 2, 76), (2, 1, 79), (3, 1, 79), (4, 2, 84), (6, 2, 82), (8, 2, 81), (10, 2, 79), (12, 4, 76)],
}
MARI_RESP2 = {
    1: [(0, 1, 79), (1, 1, 75), (2, 2, 70), (4, 2, 75), (6, 2, 79), (8, 2, 82), (10, 2, 87), (12, 3, 82)],
    3: [(0, 1, 82), (1, 1, 81), (2, 1, 79), (3, 1, 76), (4, 2, 73), (6, 2, 76), (8, 1, 79), (9, 1, 76), (10, 1, 73), (11, 1, 70), (12, 4, 69)],
}
def phrase(tr, bar0, table, vel=0.8, transpose=0, octave=0):
    for i, notes in table.items():
        for (s, d, p) in notes:
            add(tr, B(bar0 + i) + s, d, p + transpose + 12 * octave, vel * (1 if s % 4 == 0 else 0.85))

# ---------------------------------------------------------------- BASS
# pattern entries: (step, dur, interval, slide_into)
BP_INTRO = [(2, 2, 0, 0), (6, 1, 0, 0), (7, 1, 12, 0), (10, 2, 0, 0), (14, 1, 0, 0), (15, 1, 12, 0)]
BP_KRAMPUS = [(1, 1, 0, 0), (2, 1, 12, 0), (3, 1, 0, 0), (5, 1, 0, 0), (6, 1, 12, 0), (7, 1, 0, 0),
              (9, 1, 0, 0), (10, 1, 12, 0), (11, 1, 0, 0), (13, 1, 0, 0), (14, 1, 10, 0), (15, 1, 12, 1)]
BP_CAT = [(2, 1, 0, 0), (3, 1, 12, 0), (6, 1, 0, 0), (7, 1, 12, 0), (9, 1, 7, 0), (10, 1, 0, 0),
          (11, 1, 12, 0), (13, 1, 0, 0), (14, 1, 7, 0), (15, 1, 12, 1)]
BP_MARI = [(2, 2, 0, 0), (5, 1, 12, 0), (6, 2, 0, 0), (10, 1, 0, 0), (11, 1, 12, 0), (13, 1, 7, 0), (14, 2, 'b7', 1)]
BP_FINAL = [(1, 1, 0, 0), (2, 1, 12, 0), (3, 1, 0, 0), (5, 1, 0, 0), (6, 1, 12, 0), (7, 1, 7, 0),
            (9, 1, 0, 0), (10, 1, 12, 0), (11, 1, 0, 0), (13, 1, 12, 0), (14, 1, 10, 0), (15, 1, 7, 1)]

BASS = []  # (step, dur, midi, vel, slide)
def bassbar(bar, pat, vel=0.9, root=None, q=None, only=None):
    r, qq = CH[bar]
    if root is not None: r = root
    if q is not None: qq = q
    major = 4 in qq
    for (s, d, iv, sl) in pat:
        if only is not None and not (only[0] <= s < only[1]): continue
        if iv == 'b7': iv = 10 if not major else 7
        if iv == 10 and major: iv = 7 if s % 2 else 10
        if iv == 3 and major: iv = 4
        v = vel * (1.0 if s % 4 in (1, 2) else 0.85)
        BASS.append((B(bar) + s, d, r + iv, v, sl))

# ================================================================ ARRANGEMENT
def drums_bar(bar, kick=True, clap=True, snare=False, hats='16', ohats=False, shaker=True, bells='8',
              tamb=False, stomp=False, wood=False, ghost=False):
    b = B(bar)
    if kick:
        for s in (0, 4, 8, 12): add('kick', b + s, 1, 36, 1.0 if s == 0 else 0.95)
    if clap:
        for s in (4, 12): add('clap', b + s, 1, 39, 0.95)
    if snare:
        for s in (4, 12): add('snare', b + s, 1, 38, 0.8)
    if ghost:
        add('snare', b + 15, 1, 38, 0.32)
        if bar % 2 == 0: add('snare', b + 3, 1, 38, 0.3)
    if hats == '16':
        for s in range(16):
            if ohats and s % 4 == 2: continue
            add('hat', b + s, 1, 42, [0.75, 0.38, 0.62, 0.42][s % 4])
    elif hats == '8':
        for s in range(0, 16, 2): add('hat', b + s, 1, 42, 0.7 if s % 4 == 2 else 0.45)
    elif hats == 'syn':  # syncopated cat hats
        for s in (0, 2, 3, 6, 7, 10, 11, 13, 14):
            add('hat', b + s, 1, 42, 0.75 if s in (2, 6, 10, 14) else 0.45)
    if ohats:
        for s in (2, 6, 10, 14): add('ohat', b + s, 1, 46, 0.7)
    if shaker:
        for s in range(16): add('shaker', b + s, 1, 82, [0.55, 0.3, 0.45, 0.32][s % 4])
    if bells == '8':
        for s in range(0, 16, 2): add('sleigh', b + s, 1, 0, 0.9 if s % 4 == 2 else 0.55)
    elif bells == '16':
        for s in range(16): add('sleigh', b + s, 1, 0, [0.6, 0.35, 0.95, 0.4][s % 4])
    elif bells == '24':
        for s in (4, 12): add('sleigh', b + s, 1, 0, 0.85)
    elif bells == 'off':
        for s in (2, 6, 10, 14): add('sleigh', b + s, 1, 0, 0.8)
    if tamb:
        for s in (4, 12): add('tamb', b + s, 1, 54, 0.85)
        if tamb == 'full':
            for s in (2, 6, 10, 14): add('tamb', b + s, 1, 54, 0.45)
    if stomp:
        for s in (4, 12): add('stomp', b + s, 1, 0, 1.0)
        if stomp == 'swagger': add('stomp', b + 10, 1, 0, 0.75)
    if wood:
        for s in (3, 6, 9, 11, 14): add('wood', b + s, 1, 76 if s in (3, 11) else 77, 0.8 if s in (6, 14) else 0.6)

def crash(bar, step=0, vel=0.9): add('crash', B(bar) + step, 8, 49, vel)

def fill_snare16(bar, start=8, end=16, v0=0.4, v1=1.0):
    n = end - start
    for i, s in enumerate(range(start, end)):
        add('snare', B(bar) + s, 1, 38, v0 + (v1 - v0) * i / max(1, n - 1))

def fill_toms(bar, steps, notes, vel=0.9):
    for s, n in zip(steps, notes): add('tom', B(bar) + s, 1, n, vel)

# ---------------------------------------------- 0:00 - 0:07.5  INTRO HOOK (bars 1-4)
mark(1, 0, "INTRO HOOK - groove + hook from beat 1")
for bar in range(1, 5):
    drums_bar(bar, clap=True, hats='8', shaker=True, bells='16', ohats=False)
    bassbar(bar, BP_INTRO, vel=0.8)
crash(1, 0, 0.6)
hook('glock', 1, 0.8)
hook('pluck', 1, 0.62)
answer('pizz', 1, 0.8)
# bar 4 turnaround: kick drops on beat 4, snare pickup + "hey" brass hit
EV['kick'] = [e for e in EV['kick'] if not (B(4) + 12 <= e[0] < B(5))]
fill_snare16(4, 12, 16, 0.45, 0.95)
mark(2, 12, "ANSWER - pizz giggle")
mark(4, 12, "PICKUP FILL - kick out, snare run -> DROP")

# ---------------------------------------------- 0:07.5 - 0:30  KRAMPUS DROP (bars 5-16)
mark(5, 0, "KRAMPUS DROP - full kick, rolling bass, fiddle hook")
for bar in range(5, 17):
    drums_bar(bar, snare=True, hats='16', ohats=True, bells='8', stomp='swagger' if bar >= 9 else True,
              tamb=False, ghost=bar >= 9)
    bassbar(bar, BP_KRAMPUS, vel=0.95)
crash(5); crash(9, 0, 0.8); crash(13, 0, 0.85)
# 5-8 hook on fiddle + pluck, glock answers; Krampus brass "DUN-DUN" growls in the holes
hook('fiddle', 5, 0.9); hook('pluck', 5, 0.55, octave=0)
answer('glock', 5, 0.8)
for bar in (6, 8):
    r = CH[bar][0]
    for s, v in ((12, 0.95), (14, 1.0)):
        add('brass_lo', B(bar) + s, 1.6, r + 12 - (1 if s == 14 else 0) + 0, v)
mark(6, 12, "KRAMPUS GROWL - low brass DUN-DUN")
mark(8, 12, "KRAMPUS GROWL - low brass DUN-DUN")
# 9-12 hook again, now with accordion oom-PAH offbeats, lute strums, brass stabs on the 'and'
hook('fiddle', 9, 0.92); hook('pluck', 9, 0.6); hook('glock', 9, 0.55, octave=0)
answer('pizz', 9, 0.85)
for bar in range(9, 13):
    for s in (2, 6, 10, 14):
        for p in tones(bar, 60): add('accordion', B(bar) + s, 1.2, p, 0.7)
for bar in range(5, 17):
    for s in (2, 3, 6, 10, 11, 14):
        for p in tones(bar, 55): add('lute', B(bar) + s + (0.0 if s % 2 == 0 else 0), 1, p, 0.62 if s % 4 == 2 else 0.45)
for bar in (10, 12):
    for s in (0, 3, 6):
        for p in tones(bar, 50): add('brass_lo', B(bar) + s, 1.4, p, 0.9)
mark(9, 0, "KRAMPUS 2 - accordion oom-PAH + stomps")
mark(10, 0, "BRASS STAB x3 (steps 0,3,6)")
mark(12, 0, "BRASS STAB x3 (steps 0,3,6)")
# 13-16 chaos: fiddle reel in 16ths, hook moves to glock+pluck an octave up, brass march
reel('fiddle', 13, 0.82)
hook('glock', 13, 0.72, bars=(0, 1, 2)); hook('pluck', 13, 0.5, bars=(0, 1, 2))
for bar in range(13, 17):
    for s in (0, 3, 6):
        for p in tones(bar, 50): add('brass_lo', B(bar) + s, 1.2, p, 0.8 if s else 0.92)
# bar 16: chromatic "Krampus is coming" descent then tom fill
for s, p in ((8, 45), (10, 44), (12, 43), (14, 42)):
    add('brass_lo', B(16) + s, 1.7, p, 1.0); add('brass_lo', B(16) + s, 1.7, p + 12, 0.85)
fill_toms(16, (8, 9, 10, 11, 12, 13, 14, 15), (50, 50, 48, 48, 45, 45, 43, 41), 0.95)
EV['clap'] = [e for e in EV['clap'] if not (B(16) + 12 <= e[0] < B(17))]
mark(13, 0, "KRAMPUS CHAOS - fiddle reel 16ths")
mark(16, 8, "KRAMPUS DESCENT - brass chromatic + tom fill")

# ---------------------------------------------- 0:30 - 0:52.5  YULE CAT (bars 17-28)
mark(17, 0, "YULE CAT - pizzicato hook variant, glock, bouncy bass")
for bar in range(17, 29):
    drums_bar(bar, snare=False, hats='syn', ohats=bar >= 21, bells='24', tamb=True, wood=True,
              shaker=True, ghost=bar >= 21)
    bassbar(bar, BP_CAT, vel=0.92)
crash(17); crash(21, 0, 0.75); crash(25, 0, 0.85)
cat_hook('pizz', 17, 0.92)
answer('glock', 17, 0.85)
# harp sparkle arpeggios up
for bar in range(17, 29):
    t = tones(bar, 72)
    seq = [t[0], t[1], t[2], t[0] + 12, t[1] + 12, t[2] + 12, t[0] + 24, t[2] + 12]
    for i, s in enumerate((0, 1, 2, 3, 8, 9, 10, 11)):
        add('harp', B(bar) + s, 2, seq[i], 0.42 + 0.04 * (i % 4))
# Cat glide "mee-OW" phrases (portamento lead), musical, in key
GLIDES = []  # (start_step, [(step_offset, midi), ...], dur_steps)
for bar in (20, 24):
    GLIDES.append((B(bar) + 12, [(0, 69), (1.2, 81), (2.6, 79), (4, 76)], 4))
GLIDES.append((B(28) + 10, [(0, 69), (1.5, 81), (3.0, 82), (4.5, 76), (6, 69)], 6))
mark(20, 12, "CAT GLIDE 'mee-OW' (lead glide)")
mark(24, 12, "CAT GLIDE 'mee-OW' (lead glide)")
# 21-24: glock carries the hook in pounce rhythm, pizz counterline, pluck accents
hook('glock', 21, 0.85, staccato=1)
for bar in range(21, 25):
    t = tones(bar, 60)
    for s in (0, 3, 6, 8, 11, 14):
        add('pizz', B(bar) + s, 1, t[(s // 3) % 3] + (12 if s in (6, 14) else 0), 0.8)
answer('pluck', 21, 0.6, octave=0)
# 25-28: everyone on the cat hook
cat_hook('pizz', 25, 0.95); hook('glock', 25, 0.8, staccato=1); hook('pluck', 25, 0.55, staccato=1)
for bar in (26, 27):
    for s in (12, 14):
        add('brass_lo', B(bar) + s, 1, CH[bar][0] + 12, 0.7)
# bar 28 = breath: drums & bass drop at step 10, glide sings alone, snare pickup
for tr in ('kick', 'clap', 'hat', 'ohat', 'wood', 'tamb', 'shaker', 'sleigh', 'snare'):
    EV[tr] = [e for e in EV.get(tr, []) if not (B(28) + 10 <= e[0] < B(29))]
BASS[:] = [e for e in BASS if not (B(28) + 10 <= e[0] < B(29))]
EV['pizz'] = [e for e in EV['pizz'] if not (B(28) + 10 <= e[0] < B(29))]
EV['glock'] = [e for e in EV['glock'] if not (B(28) + 10 <= e[0] < B(29))]
EV['pluck'] = [e for e in EV['pluck'] if not (B(28) + 10 <= e[0] < B(29))]
EV['harp'] = [e for e in EV['harp'] if not (B(28) + 8 <= e[0] < B(29))]
add('snare', B(28) + 14, 1, 38, 0.7); add('snare', B(28) + 15, 1, 38, 0.95)
mark(25, 0, "YULE CAT 2 - all-in cat hook")
mark(28, 10, "GAP - band stops, cat glide solo")
mark(28, 14, "PICKUP - snare 2 hits")

# ---------------------------------------------- 0:52.5 - 1:15  MARI LWYD (bars 29-40)
mark(29, 0, "MARI LWYD - eerie fiddle call / accordion response")
for bar in range(29, 37):
    drums_bar(bar, snare=True, hats='16' if bar >= 33 else '8', ohats=True, bells='off', tamb=bar >= 33, stomp=bar >= 33,
              ghost=True)
    bassbar(bar, BP_MARI, vel=0.92)
crash(29); crash(33, 0, 0.8)
phrase('fiddle', 29, MARI_CALL, 0.9)
phrase('accordion', 29, MARI_RESP, 0.85)
phrase('bells', 29, {1: [(12, 4, 87)], 3: [(12, 4, 81)]}, 0.6)
phrase('fiddle', 33, MARI_CALL2, 0.92)
phrase('accordion', 33, MARI_RESP2, 0.88)
phrase('glock', 33, MARI_RESP2, 0.5, octave=1)
for bar in range(29, 41):
    r, q = CH[bar]
    add('bells', B(bar), 8, 62 + (r - 62) % 12, 0.55)               # tubular bell toll on each downbeat
    for p in tones(bar, 55): add('choir', B(bar), 16, p, 0.45)       # haunted 'ooh' bed
    # celesta 16th "will-o-wisp" arps on the off-beat
    t = tones(bar, 79)
    for i, s in enumerate(range(2, 16, 4)):
        add('celesta', B(bar) + s, 1, t[i % 3], 0.5)
        add('celesta', B(bar) + s + 1, 1, t[(i + 1) % 3] + 12, 0.4)
for bar in range(29, 41):
    for s in (2, 6, 10, 14):
        for p in tones(bar, 55): add('lute', B(bar) + s, 1, p, 0.5)
mark(30, 0, "RESPONSE - accordion answers")
mark(31, 0, "CALL - fiddle (Phrygian Eb = eerie)")
mark(32, 12, "BELL ACCENT")
mark(33, 0, "MARI LWYD 2 - fiddle up a 4th, stomps + tambourine")
mark(36, 12, "PICKUP into build")
# 37-40 BUILD: hook head sequence rising, snare roll, riser, strings
mark(37, 0, "BUILD - snare roll, hook fragments rising")
for bar in range(37, 41):
    drums_bar(bar, clap=bar < 40, snare=False, hats='16', ohats=False, bells='16', shaker=True, tamb='full')
    bassbar(bar, BP_KRAMPUS, vel=0.88)
for i, bar in enumerate(range(37, 41)):
    rate = [4, 2, 1, 1][i]
    for s in range(0, 16, rate):
        if bar == 40 and s >= 12: break
        add('snare', B(bar) + s, 1, 38, 0.35 + 0.6 * (i * 16 + s) / 64)
BUILD_HEADS = {37: [79, 79, 82, 81, 79], 38: [82, 82, 86, 84, 82], 39: [84, 84, 88, 86, 84]}
BUILD_START = {37: 74, 38: 77, 39: 79}
for bar in (37, 38, 39):
    seq = [BUILD_START[bar]] + BUILD_HEADS[bar]
    for rep in (0, 8):
        for (s, d), pp in zip([(0, 2), (2, 1), (3, 1), (4, 2), (6, 1), (7, 1)], seq):
            add('fiddle', B(bar) + rep + s, d, pp - 12 + (12 if rep else 0), 0.85)
            add('glock', B(bar) + rep + s, d, pp, 0.6)
for (s, d, p) in [(0, 2, 78), (2, 2, 81), (4, 2, 83), (6, 2, 85), (8, 4, 87)]:
    add('fiddle', B(40) + s, d, p, 0.95); add('glock', B(40) + s, d, p, 0.7); add('pluck', B(40) + s, d, p - 12, 0.6)
for bar in range(37, 41):
    for p in tones(bar, 55) + [tones(bar, 67)[0]]:
        add('strings', B(bar), 16 if bar < 40 else 12, p, 0.55 + 0.1 * (bar - 37))
EV['kick'] = [e for e in EV['kick'] if not (B(40) + 12 <= e[0] < B(41))]
BASS[:] = [e for e in BASS if not (B(40) + 12 <= e[0] < B(41))]
EV['hat'] = [e for e in EV['hat'] if not (B(40) + 12 <= e[0] < B(41))]
EV['shaker'] = [e for e in EV['shaker'] if not (B(40) + 12 <= e[0] < B(41))]
EV['sleigh'] = [e for e in EV['sleigh'] if not (B(40) + 12 <= e[0] < B(41))]
EV['tamb'] = [e for e in EV['tamb'] if not (B(40) + 12 <= e[0] < B(41))]
RISER = (B(37), B(40) + 12)
mark(40, 0, "KEY-CHANGE PICKUP - B7, rising line")
mark(40, 12, "GAP - silence before MEGA DROP")

# ---------------------------------------------- 1:15 - 1:30  FINAL MEGA DROP (bars 41-48)  +2 semitones
mark(41, 0, "FINAL MEGA DROP - key change to E minor, everything in")
TR = 2
for bar in range(41, 48):
    drums_bar(bar, snare=True, hats='16', ohats=True, bells='16', tamb='full', stomp='swagger', ghost=True)
crash(41, 0, 1.0); crash(45, 0, 0.9)
for bar in range(41, 47): bassbar(bar, BP_FINAL, vel=1.0)
bassbar(47, BP_FINAL, vel=1.0, only=(0, 8))
bassbar(47, BP_FINAL, vel=1.0, root=Bn, q=MAJ, only=(8, 16))
hook('fiddle', 41, 0.95, transpose=TR); hook('glock', 41, 0.8, transpose=TR); hook('pluck', 41, 0.68, transpose=TR)
hook('pizz', 41, 0.7, transpose=TR, octave=-1, staccato=1)
answer('glock', 41, 0.9, transpose=TR, octave=0); answer('brass_hi', 41, 0.75, transpose=TR, octave=-1)
for bar in range(41, 48):
    for s in (0, 3, 6, 10):
        if bar == 47 and s >= 8: continue
        for p in tones(bar, 50, s): add('brass_lo', B(bar) + s, 1.3, p, 0.85)
    if bar == 47:
        for p in tones(bar, 60, 0): add('strings', B(bar), 8, p, 0.6)
        for p in tones(bar, 60, 8): add('strings', B(bar) + 8, 8, p, 0.65)
    else:
        for p in tones(bar, 60): add('strings', B(bar), 16, p, 0.6)
    for s in (2, 6, 10, 14):
        for p in tones(bar, 60, s): add('accordion', B(bar) + s, 1.1, p, 0.6)
    for s in (2, 3, 6, 10, 11, 14):
        for p in tones(bar, 55, s): add('lute', B(bar) + s, 1, p, 0.5)
# second half 45-48: fiddle reel (Krampus) + Mari response on accordion + cat glide
reel('fiddle', 45, 0.85, transpose=TR, nbars=2)
hook('glock', 45, 0.85, transpose=TR, bars=(0, 1)); hook('pluck', 45, 0.65, transpose=TR, bars=(0, 1))
phrase('bells', 45, {1: [(12, 4, 84)]}, 0.6)
GLIDES.append((B(44) + 12, [(0, 71), (1.2, 83), (2.6, 81), (4, 78)], 4))
mark(44, 12, "CAT GLIDE returns")
mark(45, 0, "MEGA DROP 2 - fiddle reel + hook stacked")
# bar 47: D -> B turnaround, hook bar 4 shape over it
for (s, d, p) in [(0, 2, 78), (2, 2, 81), (4, 2, 86), (6, 2, 83), (8, 2, 83), (10, 2, 87), (12, 2, 90), (14, 2, 87)]:
    add('fiddle', B(47) + s, d, p, 0.95); add('pluck', B(47) + s, d, p - 12, 0.6); add('glock', B(47) + s, d, p - 12, 0.75)
for s in (8, 12):
    for p in (59, 63, 66): add('brass_lo', B(47) + s, 2, p - 12, 0.95)
mark(47, 8, "TURNAROUND - B major (V)")
# bar 48 STOP-TIME ending:  tutti hits at 0, 3, 6 ; tom fill 8-11 ; FINAL HIT at 12
FINAL_HITS = (0, 3, 6, 12)
for s in FINAL_HITS:
    v = 1.0 if s in (0, 12) else 0.9
    add('kick', B(48) + s, 1, 36, 1.0); add('clap', B(48) + s, 1, 39, v); add('stomp', B(48) + s, 1, 0, v)
    add('sleigh', B(48) + s, 1, 0, 1.0)
    BASS.append((B(48) + s, 1.6 if s < 12 else 4, E, 1.0, 0))
    for p in tones(48, 52 + 0): add('brass_lo', B(48) + s, 1.5 if s < 12 else 4, p, v)
    for p in (64, 67, 71, 76): add('strings', B(48) + s, 1.5 if s < 12 else 4, p, v * 0.8)
    add('fiddle', B(48) + s, 1.5 if s < 12 else 4, 83 if s < 12 else 88, v)
    add('glock', B(48) + s, 1, 83 if s < 12 else 88, v)
    add('pluck', B(48) + s, 1.5, 71 if s < 12 else 76, 0.7)
    add('pizz', B(48) + s, 1, 52, v)
fill_toms(48, (8, 9, 10, 11), (50, 48, 45, 43), 1.0)
fill_snare16(48, 8, 12, 0.6, 1.0)
crash(48, 12, 1.0)
add('bells', B(48) + 12, 4, 76, 0.8)
mark(48, 0, "STOP-TIME HIT 1")
mark(48, 3, "STOP-TIME HIT 2")
mark(48, 6, "STOP-TIME HIT 3")
mark(48, 8, "FINAL FILL - toms")
mark(48, 12, "FINAL HIT - E minor tutti")

TOTAL_STEPS = BARS * 16
