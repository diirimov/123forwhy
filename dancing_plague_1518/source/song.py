"""
Dancing Plague 1518 -- extended dance version: score and arrangement.

Everything melodic here was transcribed from the EP01 soundtrack (see
../TRANSCRIPTION.md): tempo 128.5 BPM, D drone with Phrygian/Dorian colour
(D Eb E F G A Bb C), recorder-like pipe on the hook, fiddle doubling,
hurdy-gurdy/bagpipe D-A drone, lute, warm four-on-the-floor kick with a riq
on the offbeats, and a deep bass that leans D -> Eb.

Notes are (step, length, midi) on the 16th grid; `gs` = global 16th index
(bar * 16 + step).
"""
import numpy as np
import engine as E
from engine import SR

BPM = 128.5
BEAT = 60.0 / BPM
S16 = BEAT / 4
BAR = 4 * BEAT
NBARS = 87
TAIL = 3.4                       # ring-out after the last bar line
SWING = 0.52                     # off-16ths land at 52 % of the 8th: human, still straight

# ============================================================================ grid
def ts(gs):
    """seconds of (fractional) global 16th index"""
    gs = float(gs)
    pair = np.floor(gs / 2); r = gs - 2 * pair
    frac = r * SWING if r <= 1 else SWING + (r - 1) * (1 - SWING)
    return (pair + frac) * 2 * S16


def at(bar, step=0):
    return bar * 16 + step


def dur(gs, length):
    return ts(gs + length) - ts(gs)


# ============================================================================ transcribed material
# D4=62 Eb4=63 E4=64 F4=65 G4=67 A4=69 Bb4=70 C5=72 C#5=73 D5=74 Eb5=75
HOOK = [(0, 3, 74), (3, 1, 72), (4, 2, 69), (6, 2, 67), (8, 4, 69), (12, 2, 62), (14, 2, 65),
        (16, 3, 67), (19, 1, 65), (20, 2, 64), (22, 2, 60)]                 # D C A G A D F | G F E C
ANSWER = [(0, 2, 70), (2, 2, 67), (4, 4, 69), (8, 2, 62), (10, 2, 63), (12, 3, 65), (15, 1, 63),
          (16, 2, 62), (18, 2, 60), (20, 2, 58), (22, 2, 60), (24, 8, 62)]  # Bb G A D Eb F Eb | D C Bb C D
ANSWER2 = [(0, 3, 74), (3, 1, 72), (4, 2, 70), (6, 2, 67), (8, 4, 69), (12, 2, 62), (14, 2, 63),
           (16, 3, 65), (19, 1, 63), (20, 2, 62), (22, 4, 60), (26, 2, 58), (28, 4, 62)]
TAG = [(4, 3, 73), (8, 3, 74), (12, 4, 75), (20, 2, 74), (24, 2, 70), (26, 2, 67), (28, 4, 62)]  # C# D Eb | D Bb G D


def hook_full(fill=False, end=8):
    """2-bar form (reference bars 19-20 / 37-38): D4 held on beat 3"""
    if fill:
        return HOOK + [(24, 4, 62), (28, 2, 74), (30, 1, 69), (31, 1, 72)]
    return HOOK + [(24, end, 62)]


def hook_pick():
    """32-step form with pickup (reference bars 12-16): starts on beat 4"""
    return HOOK + [(24, 6, 62), (30, 2, 69)]


GROOVE_LINE = [(0, 8, 74), (8, 8, 67), (16, 6, 69), (22, 10, 65), (32, 12, 70), (44, 4, 69)]   # bars 9-11 of ref
EB_SWELL = (6, 10, 63)          # bar 18 of the reference: re-bowed Eb4 pulling into the hook

# bass riffs (step, len, midi, vel, pop)
R_HOOK = [(0, 3, 38, 1.0, 0), (3, 1, 50, 0.7, 1), (4, 2, 38, 0.85, 0), (6, 2, 41, 0.9, 0), (8, 2, 41, 0.85, 0),
          (10, 4, 48, 0.9, 0), (14, 2, 38, 0.8, 0)]
R_ANS = [(0, 3, 38, 1.0, 0), (3, 1, 50, 0.7, 1), (4, 2, 38, 0.85, 0), (6, 2, 36, 0.85, 0), (8, 2, 39, 0.95, 0),
         (10, 2, 41, 0.85, 0), (12, 2, 39, 0.9, 0), (14, 2, 38, 0.8, 0)]


def r_groove(e):
    return [(0, 3, 38, 1.0, 0), (3, 1, 50, 0.7, 1), (4, 3, e, 0.95, 0), (7, 1, e + 12, 0.65, 1), (8, 2, e, 0.9, 0),
            (10, 4, 48, 0.85, 0), (14, 2, 38, 0.8, 0)]


R_HIT = [(0, 6, 38, 1.0, 0), (6, 2, 50, 0.75, 1), (8, 6, 38, 0.9, 0), (14, 2, 50, 0.7, 1)]
R_DRIVE = [(0, 2, 38, 1.0, 0), (2, 1, 50, 0.7, 1), (3, 1, 38, 0.8, 0), (4, 2, 38, 0.9, 0), (6, 2, 41, 0.9, 0),
           (8, 1, 41, 0.85, 0), (9, 1, 53, 0.65, 1), (10, 2, 48, 0.9, 0), (12, 2, 48, 0.8, 0), (14, 1, 38, 0.85, 0),
           (15, 1, 50, 0.7, 1)]
R_DRIVE_ANS = [(0, 2, 38, 1.0, 0), (2, 1, 50, 0.7, 1), (3, 1, 38, 0.8, 0), (4, 2, 38, 0.9, 0), (6, 2, 36, 0.9, 0),
               (8, 1, 39, 0.95, 0), (9, 1, 51, 0.65, 1), (10, 2, 41, 0.9, 0), (12, 2, 39, 0.85, 0),
               (14, 1, 38, 0.85, 0), (15, 1, 50, 0.7, 1)]
R_PEDAL_C = [(0, 6, 36, 0.9, 0), (6, 2, 48, 0.6, 1), (8, 6, 36, 0.85, 0), (14, 2, 48, 0.6, 1)]
R_SOFT = [(0, 6, 38, 0.75, 0), (6, 2, 50, 0.55, 1), (8, 6, 38, 0.7, 0), (14, 2, 50, 0.55, 1)]

POWER = {36: (48, 55, 60), 38: (50, 57, 62), 39: (51, 58, 63), 40: (50, 57, 62), 41: (53, 60, 65), 48: (48, 55, 60)}

# ============================================================================ tracks / stems
N = int(round((NBARS * BAR + TAIL) * SR))
SPEC = {   # name: (pan, room, plate, stem)
    "kick": (0, 0.0, 0, "drums"), "clap": (0.05, 0.08, 0.18, "drums"), "tabor": (-0.1, 0.1, 0.08, "drums"),
    "tom": (0, 0.14, 0, "drums"), "cym": (0, 0.16, 0, "drums"),
    "riq": (0.38, 0.08, 0.04, "percussion"), "shaker": (-0.55, 0.06, 0, "percussion"), "tick": (0.25, 0.04, 0, "percussion"),
    "frame": (-0.2, 0.1, 0, "percussion"), "wood": (0.4, 0.1, 0.05, "percussion"),
    "bass": (0, 0.0, 0, "bass"), "sub": (0, 0.0, 0, "bass"),
    "drone": (0, 0.2, 0, "drone"),
    "lute": (-0.4, 0.14, 0.05, "lute"), "chop": (0.45, 0.12, 0.05, "lute"),
    "fiddle": (0.3, 0.18, 0.1, "strings"), "fiddle2": (-0.5, 0.18, 0.1, "strings"), "gurdy": (-0.22, 0.16, 0.06, "strings"),
    "pipe": (0.0, 0.2, 0.12, "lead"), "flute": (0.4, 0.22, 0.12, "lead"),
    "fx": (0, 0.25, 0.05, "fx"), "boom": (0, 0.1, 0, "fx"),
}
T = {}
SECTIONS = []          # (bar, name, description)
ACCENTS = []           # (time, kind, text)


def reset():
    T.clear(); SECTIONS.clear(); ACCENTS.clear()
    E.reseed(1518)
    for k, (p, r, pl, st) in SPEC.items():
        T[k] = E.Track(N, p, r, pl, st)


def section(bar, name, txt):
    SECTIONS.append((bar, name, txt))


# ============================================================================ players
def vel_of(step, base):
    s = step % 16
    return base * (1.0 if s in (0, 8) else 0.93 if s in (4, 12) else 0.86 if s % 2 == 0 else 0.8) * E.rng.uniform(0.94, 1.04)


def lead(gs0, notes, vel=1.0, tr=0, inst="pipe", trk=None, legato=0.92, octave_flute=False, double=False):
    prev_end = None
    for s, l, m in notes:
        g = gs0 + s
        t = ts(g) + E.hum(0.003)
        d = dur(g, l) * legato
        v = vel_of(g, vel)
        slur = prev_end is not None and abs(prev_end - g) < 0.01 and l <= 1
        if inst == "pipe":
            T[trk or "pipe"].add(E.pipe(m + tr, d, v, slur=slur), t)
        elif inst == "fiddle":
            T[trk or "fiddle"].add(E.fiddle(m + tr, d, v, "legato" if l >= 2 else "spic", scoop=(l >= 3)), t)
        elif inst == "gurdy":
            T[trk or "gurdy"].add(E.gurdy(m + tr, d, v), t)
        elif inst == "flute":
            T[trk or "flute"].add(E.flute(m + tr, d, v, chiff=0.8), t)
        elif inst == "lute":
            T[trk or "lute"].add(E.lute(m + tr, d * 1.05, v * 1.1, 0.78), t)
        if octave_flute:
            T["flute"].add(E.flute(m + tr + 12, d, v * 0.55, chiff=0.6), t + 0.004)
        if double:
            T["fiddle2"].add(E.fiddle(m + tr, d, v * 0.7, "legato" if l >= 2 else "spic", det=-5),
                             t + 0.011 + E.hum(0.003))
        prev_end = g + l


def bassline(bar, riff, vel=1.0, tr=0):
    for s, l, m, v, pop in riff:
        g = at(bar, s)
        T["bass"].add(E.deep_bass(m + tr, dur(g, l) * 0.9, v * vel, pop=bool(pop)), ts(g) + E.hum(0.002))


def sub_drop(bar):
    """2-bar bass-drop unit (reference bars 31-34): long sub D2, leaning into Eb2 across the bar line"""
    t0 = ts(at(bar))
    pts = [(0.0, 38), (ts(at(bar, 12)) - t0, 39), (ts(at(bar + 1, 3)) - t0, 38), (ts(at(bar + 1, 14)) - t0, 36)]
    T["sub"].add(E.sub_slide(pts, 2 * BAR - 0.02, 1.0), t0)
    for b, s, m in ((bar, 0, 38), (bar, 12, 39), (bar + 1, 3, 38), (bar + 1, 14, 36)):
        T["bass"].add(E.deep_bass(m, S16 * 1.5, 0.55, pop=True), ts(at(b, s)))


DROP_PTS = {"hook": [(0, 38), (7, 41), (12, 48)], "ans": [(0, 38), (5, 41), (9, 40), (11, 39)]}


def drop_bass(bar, kind, vel=1.0):
    """legato gliding bass of the reference drop (bars 26-30): D2 -> F2 -> C3, answer D2 -> F2 -> E2 -> Eb2"""
    t0 = ts(at(bar))
    pts = [(ts(at(bar, s)) - t0, m) for s, m in DROP_PTS[kind]]
    T["sub"].add(E.growl_bass(pts, BAR - 0.01, vel), t0)
    for s in (0, 8):
        T["bass"].add(E.deep_bass(38 if s == 0 else dict(DROP_PTS[kind]).get(7, 41), S16 * 1.2, 0.45 * vel, pop=True),
                      ts(at(bar, s)))


TAG_BASS = [(0, 38), (4, 37), (8, 36), (12, 35), (16, 34), (24, 41), (28, 38)]   # D C# C B | Bb . F D


def tag_bass(bar, vel=1.0):
    """chromatic descent under the rising C#-D-Eb tag (reference bars 39-40): contrary motion"""
    t0 = ts(at(bar))
    pts = [(ts(at(bar) + s) - t0, m) for s, m in TAG_BASS]
    T["sub"].add(E.growl_bass(pts, 2 * BAR - 0.01, vel, gtime=0.06), t0)
    for s, m in TAG_BASS:
        T["bass"].add(E.deep_bass(m, S16 * 1.2, 0.45 * vel, pop=True), ts(at(bar) + s))


def chops(bar, steps=(2, 6, 10, 14), roots=None, vel=1.0):
    for s in steps:
        r = roots(s) if roots else 38
        ch = POWER.get(r, POWER[38])
        T["chop"].add(E.strum(list(ch), S16 * 1.2, vel * (1.0 if s % 8 == 6 else 0.85), down=(s % 4 == 2)),
                      ts(at(bar, s)) + E.hum(0.004))


def riff_root(riff):
    def f(step):
        r = 38
        for s, l, m, v, p in riff:
            if s <= step:
                r = m if m < 48 or m == 48 else r
        return r
    return f


def lute_arp(bar, pattern=(50, 57, 62, 57), vel=0.8, steps=(0, 2, 4, 6, 8, 10, 12, 14)):
    for i, s in enumerate(steps):
        m = pattern[i % len(pattern)]
        T["lute"].add(E.lute(m, S16 * 2.2, vel * (1.0 if s % 4 == 0 else 0.8) * E.rng.uniform(0.9, 1.05), 0.72),
                      ts(at(bar, s)) + E.hum(0.004))


def drone_span(b0, b1, midis=(50, 57), levels=None, buzz=True, fade=0.08):
    t0 = ts(at(b0))
    times = [(ts(at(b, s)) - t0, 1.0 if s % 4 == 2 else 0.55) for b in range(b0, b1) for s in (2, 6, 10, 14)] if buzz else []
    T["drone"].add(E.drone(ts(at(b1)) - t0 + 0.06, list(midis), levels, times, fade=fade), t0)


def swell(bar, step=6, length=10, m=63, vel=1.0):
    """re-bowed Eb4 tension (fiddle + gurdy), pulses on 8ths"""
    g = at(bar, step); d = dur(g, length)
    T["fiddle"].add(E.fiddle(m, d, vel * 1.1, "legato", trem=2 * S16), ts(g))
    T["fiddle2"].add(E.fiddle(m - 12, d, vel * 0.8, "legato", det=-4, trem=2 * S16), ts(g) + 0.01)
    T["gurdy"].add(E.gurdy(m, d, vel * 0.7), ts(g))


# ---------------------------------------------------------------------------- drums
def drums(bar, style, skip=()):
    S = lambda s: ts(at(bar, s)) + E.hum(0.0025)
    def k(s, v=1.0, long=False):
        if s not in skip:
            T["kick"].add(E.club_kick(v, long), S(s))
    def sh(base=1.0):
        for s in range(16):
            if s not in skip:
                T["shaker"].add(E.shaker((0.95 if s % 4 == 2 else 0.5 if s % 2 == 0 else 0.3) * base * E.rng.uniform(0.85, 1.1)), S(s))
    def rq(base=1.0, ghosts=False):
        for s in (2, 6, 10, 14):
            if s not in skip:
                T["riq"].add(E.riq(base * E.rng.uniform(0.92, 1.05), long=(s == 14 and bar % 2 == 1)), S(s))
        if ghosts:
            for s in (1, 5, 9, 13, 15):
                if s not in skip:
                    T["riq"].add(E.riq(0.28 * base), S(s))
    def frame_bounce(base=1.0):
        for s, v in ((3, 0.55), (6, 0.4), (11, 0.55), (14, 0.4), (7, 0.18), (15, 0.22)):
            if s not in skip:
                T["frame"].add(E.frame(v * base, 92 if v > 0.4 else 118, v > 0.4), S(s))
    def backbeat(v=1.0):
        for s in (4, 12):
            if s not in skip:
                T["clap"].add(E.clap(v * E.rng.uniform(0.92, 1.03)), S(s))
                T["tabor"].add(E.tabor(0.55 * v), S(s) + 0.002)

    if style == "intro_a":
        sh(0.7); rq(0.6)
        for s in (0, 8):
            T["frame"].add(E.frame(0.55, 88, True), S(s))
        return
    if style == "intro_b":
        sh(0.8); rq(0.75); k(0, 0.85); k(8, 0.8)
        for s in (3, 11):
            T["frame"].add(E.frame(0.45, 92, True), S(s))
        return
    if style == "break":
        k(0, 0.9); k(8, 0.85); sh(0.8); rq(0.8)
        for s in (4, 12):
            T["tabor"].add(E.tabor(0.35), S(s))
        return
    if style == "bassdrop":
        for s in (0, 4, 8, 12):
            k(s, 1.0, long=True)
        for s in range(16):
            if s not in skip:
                T["tick"].add(E.tick((1.0 if s % 2 == 0 else 0.6) * E.rng.uniform(0.85, 1.1)), S(s))
        for s in (2, 6, 10, 14):
            if s not in skip:
                T["shaker"].add(E.shaker(1.3), S(s)); T["shaker"].add(E.shaker(0.8), S(s) + S16 * 0.5)
        backbeat(0.7)
        if bar % 2 == 1:                       # swoosh into every second bar line (reference bass drop)
            sw = E.rev_cym(0.55, 0.9)
            T["cym"].add(sw, ts(at(bar + 1)) - len(sw) / SR)
        return
    # four-on-the-floor family
    for s in (0, 4, 8, 12):
        k(s, 1.0 if s in (0, 8) else 0.94)
    sh(1.0 if style != "light" else 0.8)
    rq(1.0, ghosts=style in ("climax", "final"))
    frame_bounce(0.8 if style == "light" else 1.0)
    if style != "light":
        backbeat(1.0 if style in ("climax", "final", "drop") else 0.85)
    if style in ("drop", "climax", "final"):
        for s in ((3, 11) if bar % 2 == 0 else (3, 9, 11)):
            if s not in skip:
                T["wood"].add(E.woodblock(0.7, hi=(s != 9)), S(s))
    if style in ("climax", "final") and bar % 2 == 1:
        k(15, 0.5)
    if style == "final" and bar % 4 == 3:
        k(10, 0.55); k(14, 0.6)


def crash_at(bar, step=0, vel=1.0, boom=True):
    t = ts(at(bar, step))
    T["cym"].add(E.crash(2.4, vel), t)
    if boom:
        T["boom"].add(E.boom(0.8 * vel), t)
    ACCENTS.append((t, "hit", f"crash/boom bar {bar + 1}"))


def tom_fill(bar, start=12, end=16, vel=1.0):
    ps = [170, 150, 132, 118, 104, 92, 82, 74]
    for i, s in enumerate(np.arange(start, end, 1.0)):
        T["tom"].add(E.tom(ps[i % 8], (0.55 + 0.08 * i) * vel), ts(at(bar, s)) + E.hum(0.002))


def roll(bar, nbars=1, start=0, stop=None, vel=1.0):
    total = nbars * 16 - start
    for i in range(total * 2):
        s = start + i / 2
        if stop is not None and s >= stop:
            break
        if i % 2 == 1 and i < total:
            continue
        v = 0.18 + 0.75 * (i / (total * 2)) ** 1.6
        T["tabor"].add(E.tabor(v * vel), ts(at(bar) + s) + E.hum(0.0015))
        if i % 2 == 0:
            T["frame"].add(E.frame(v * 0.45, 112, False), ts(at(bar) + s))


def phrase_fill(bar, vel=1.0):
    """tabor pickup on the last beat of a 4-bar phrase"""
    for i, s in enumerate((12, 13, 14, 15)):
        T["tabor"].add(E.tabor((0.35 + 0.13 * i) * vel), ts(at(bar, s)) + E.hum(0.002))
    T["riq"].add(E.riq(0.8 * vel, long=True), ts(at(bar, 14)))


def riser(bar, nbars=1, vel=1.0):
    d = nbars * BAR
    T["fx"].add(E.sweep(d, vel, True), ts(at(bar)))
    T["fx"].add(E.rev_cym(d * 0.6, 0.8 * vel), ts(at(bar + nbars)) - d * 0.6)


def stop_hits(bar, steps, roots, vel=1.0):
    for s, r in zip(steps, roots):
        t = ts(at(bar, s))
        T["kick"].add(E.club_kick(vel), t)
        T["bass"].add(E.deep_bass(r, S16 * 2.5, vel), t)
        T["chop"].add(E.strum(list(POWER[r]) + [POWER[r][0] + 12], S16 * 1.8, vel), t)
        T["clap"].add(E.clap(0.7 * vel), t)
        T["tom"].add(E.tom(95, 0.6 * vel), t)


# ============================================================================ ARRANGEMENT
def build():
    reset()

    # ---------------------------------------------------------------- INTRO 1-8
    section(0, "INTRO", "drone breathes in; the pipe states the hook exactly as in the original opening (on beat 2)")
    drone_span(0, 8, (50, 57, 62, 69), [0.7, 0.55, 0.6, 0.3], buzz=False, fade=1.2)
    t0 = ts(at(0, 4))
    pts = [(0.0, 43), (0.14, 41), (ts(at(1)) - t0, 38), (ts(at(1, 6)) - t0, 41), (ts(at(3, 8)) - t0, 38),
           (ts(at(3, 12)) - t0, 41), (ts(at(3, 14)) - t0, 48)]
    T["sub"].add(E.sub_slide(pts, ts(at(4)) - t0, 0.55), t0)          # original intro: G2 -> F2 glide, D2, F2
    for b in range(0, 2):
        drums(b, "intro_a")
        lute_arp(b, vel=0.45, steps=(0, 4, 8, 12))
    for b in range(2, 4):
        bassline(b, [(0, 2, 41, 0.45, 1), (8, 2, 41, 0.4, 1)] if b == 2 else [(0, 2, 41, 0.45, 1), (8, 2, 38, 0.45, 1)])
    for b in range(2, 4):
        drums(b, "intro_b")
    lead(at(0, 4), HOOK + [(24, 4, 62)], vel=0.8)
    lead(at(2, 2), [(0, 2, 69)] + [(s + 2, l, m) for s, l, m in HOOK] + [(26, 6, 62)], vel=0.85)
    for b in range(2, 4):
        lute_arp(b, vel=0.55)
    section(4, "INTRO B", "kick and bass arrive; fiddle answers with the Bb/Eb phrase; Eb swell pulls into the hit")
    for b in range(4, 8):
        drums(b, "four" if b >= 6 else "light", skip=(12, 13, 14, 15) if b == 7 else ())
        bassline(b, R_SOFT if b < 6 else R_HOOK, 0.8 if b < 6 else 0.9)
        lute_arp(b, vel=0.65)
    lead(at(4, 2), [(0, 2, 69), (2, 3, 74), (5, 1, 72), (6, 4, 69)], vel=0.8)
    lead(at(5, 4), ANSWER2[:-1] + [(28, 4, 62)], vel=0.9, inst="fiddle", double=True)
    lead(at(5, 4), ANSWER2[:-1] + [(28, 4, 62)], vel=0.55)
    swell(7, 8, 8, vel=0.9)
    roll(7, 1, start=8, vel=0.9)
    riser(6, 2, 0.9)

    # ---------------------------------------------------------------- GROOVE 9-12
    section(8, "GROOVE", "the big hit: full beat, D->E->Eb bass, fiddle + gurdy counter-line of the original bars 9-12")
    crash_at(8)
    drone_span(8, 16, (50, 57, 62), [0.9, 0.7, 0.35])
    for b in range(8, 12):
        drums(b, "four")
    bassline(8, R_HIT); bassline(9, r_groove(40)); bassline(10, r_groove(39)); bassline(11, r_groove(39))
    for b, rf in ((8, R_HIT), (9, r_groove(40)), (10, r_groove(39)), (11, r_groove(39))):
        chops(b, roots=riff_root(rf), vel=0.85)
    lead(at(8), GROOVE_LINE, vel=0.95, inst="fiddle", double=True, legato=0.97)
    lead(at(8), GROOVE_LINE, vel=0.6, inst="gurdy", legato=0.97)
    swell(11, 0, 12, vel=0.85)
    tom_fill(11, 14, 16, 0.7)

    # ---------------------------------------------------------------- HOOK A 13-16
    section(12, "HOOK A", "the hook x2 on pipe with its pickup, as in the original bars 12-16")
    for b in range(12, 16):
        drums(b, "four")
        bassline(b, R_HOOK)
        lute_arp(b, (50, 57, 62, 65), vel=0.6)
    lead(at(11, 12), hook_pick(), vel=1.0)
    lead(at(13, 12), hook_pick()[:-1] + [(30, 2, 74)], vel=1.0)
    lead(at(11, 12), hook_pick(), vel=0.5, inst="fiddle", trk="fiddle2", legato=0.9)
    lead(at(13, 12), hook_pick()[:-1], vel=0.5, inst="fiddle", trk="fiddle2", legato=0.9)

    # ---------------------------------------------------------------- OFFBEAT 17-18
    section(16, "OFFBEAT", "riq offbeats and lute riff carry the dance; re-bowed Eb4 swell (original bars 17-18)")
    drone_span(16, 18, (50, 57), [0.9, 0.7])
    for b in (16, 17):
        drums(b, "four")
        bassline(b, R_HOOK if b == 16 else R_ANS)
    lead(at(16), [(0, 2, 74), (2, 1, 72), (3, 1, 69), (4, 2, 67), (6, 2, 69), (8, 2, 62), (10, 2, 65), (12, 2, 67),
                  (14, 2, 64)], vel=0.8, inst="lute")
    lute_arp(17, (50, 57, 62, 57), vel=0.6, steps=(0, 2, 4))
    swell(17, 6, 10, vel=1.0)
    tom_fill(17, 12, 16, 0.8)

    # ---------------------------------------------------------------- HOOK + ANSWER 19-26
    section(18, "HOOK + ANSWER", "full statement (original bars 19-22) twice; second pass adds wooden flute an octave up")
    crash_at(18, vel=0.8)
    drone_span(18, 26, (50, 57, 62), [0.9, 0.7, 0.35])
    lead(at(18), hook_full(fill=True), vel=1.0, double=True)
    lead(at(20), ANSWER, vel=1.0, double=True)
    lead(at(22), hook_full(fill=True), vel=1.05, double=True, octave_flute=True)
    lead(at(24), ANSWER2, vel=1.05, double=True, octave_flute=True)
    for b in range(18, 26):
        drums(b, "four")
        rf = R_HOOK if b % 4 in (2, 3) or b == 25 else R_ANS
        rf = R_HOOK if b in (18, 19, 22, 23) else (R_ANS if b in (20, 24) else R_HOOK)
        bassline(b, rf)
        chops(b, roots=riff_root(rf), vel=0.7)
        lute_arp(b, (50, 57, 62, 57), vel=0.45, steps=(0, 4, 8, 12))

    # ---------------------------------------------------------------- TRANSITION 27-28
    section(26, "TRANSITION", "low lute line over toms, roll and riser (original bars 23-25, shortened)")
    drone_span(26, 28, (50, 57), [0.8, 0.6])
    drums(26, "light"); drums(27, "light", skip=tuple(range(12, 16)))
    bassline(26, R_ANS, 0.9); bassline(27, [(0, 3, 38, 1.0, 0), (3, 1, 50, 0.7, 1), (4, 4, 39, 0.9, 0), (8, 4, 41, 0.9, 0)])
    lead(at(26), [(0, 2, 70), (2, 2, 55), (4, 4, 57), (8, 2, 58), (10, 2, 60), (12, 4, 62), (16, 2, 63), (18, 2, 62),
                  (20, 2, 60), (22, 2, 58)], vel=0.9, inst="lute")
    lead(at(26), [(0, 2, 70), (2, 2, 55), (4, 4, 57), (8, 2, 58), (10, 2, 60), (12, 4, 62), (16, 2, 63), (18, 2, 62),
                  (20, 2, 60), (22, 2, 58)], vel=0.55, inst="fiddle", trk="fiddle2")
    tom_fill(26, 12, 16, 0.75)
    roll(27, 1, vel=1.0)
    riser(27, 1, 1.0)
    swell(27, 8, 8, vel=0.8)

    # ---------------------------------------------------------------- DROP 29-36
    section(28, "DROP", "the original drop: hook running straight into the Bb/Eb answer, whole band, woodblocks")
    crash_at(28)
    drone_span(28, 36, (50, 57, 62), [1.0, 0.75, 0.4])
    for b in range(28, 36):
        drums(b, "drop")
    for gs0 in (at(28, 8), at(32, 8)):
        lead(gs0, HOOK, vel=0.95, double=True)
        lead(gs0 + 24, ANSWER2, vel=0.95, double=True)
    lead(at(28), [(0, 8, 74)], vel=0.9, inst="fiddle", double=True)
    lead(at(32), [(0, 8, 69)], vel=0.8, inst="fiddle")
    for b in range(28, 36):
        kind = "hook" if b % 4 in (0, 1) else "ans"
        drop_bass(b, kind)
        chops(b, steps=(2, 6, 10, 14), roots=lambda s: 38, vel=0.7)
    tom_fill(35, 12, 16, 0.9)

    # ---------------------------------------------------------------- BASS DROP 37-44
    section(36, "BASS DROP", "sliding D->Eb sub, 16th ticks, A3 drone (original bars 31-34); fiddle sings the answer low")
    crash_at(36)
    drone_span(36, 44, (57, 62), [0.9, 0.5])
    for b in range(36, 44):
        drums(b, "bassdrop")
    for b in range(36, 44, 2):
        sub_drop(b)
    for b in range(36, 40):
        chops(b, steps=(2, 10), vel=0.6)
        lead(at(b, 12), [(0, 1, 74), (1, 1, 72), (2, 2, 69)], vel=0.75)        # pipe calls: D C A
    lead(at(40), ANSWER, vel=1.0, inst="fiddle", tr=-12, double=True, legato=0.97)
    lead(at(42), ANSWER2[:-1] + [(28, 4, 62)], vel=1.0, inst="fiddle", tr=-12, double=True, legato=0.97)
    lead(at(40), ANSWER, vel=0.55, inst="gurdy", legato=0.97)
    lead(at(42), ANSWER2, vel=0.55, inst="gurdy", legato=0.97)
    swell(43, 8, 8, vel=0.8)

    # ---------------------------------------------------------------- BREAK 45-46
    section(44, "BREAK", "short lift on a C pedal (original bars 35-36); the beat never stops")
    drone_span(44, 46, (48, 55), [0.8, 0.6])
    drums(44, "break"); drums(45, "break")
    bassline(44, R_PEDAL_C); bassline(45, R_PEDAL_C)
    for b in (44, 45):
        lute_arp(b, (57, 62, 65, 62), vel=0.7)
    lead(at(44, 4), [(0, 2, 69), (2, 2, 74), (4, 4, 72), (8, 2, 69), (10, 2, 67), (12, 4, 69)], vel=0.75)
    roll(45, 1, vel=1.1)
    riser(44, 2, 1.0)
    for s in (8, 10, 12, 13, 14, 15):
        T["kick"].add(E.club_kick(0.5 + 0.03 * s), ts(at(45, s)))

    # ---------------------------------------------------------------- CLIMAX 47-54
    section(46, "CLIMAX", "hook with flute 8va and fiddles, then the original C#-D-Eb tag, answer and hook again")
    crash_at(46)
    drone_span(46, 54, (50, 57, 62), [1.0, 0.8, 0.45])
    lead(at(46), hook_full(), vel=1.1, double=True, octave_flute=True)
    lead(at(48), TAG, vel=1.1, double=True, octave_flute=True)
    lead(at(50), ANSWER, vel=1.1, double=True, octave_flute=True)
    lead(at(52), hook_full(fill=True), vel=1.1, double=True, octave_flute=True)
    lead(at(46), hook_full() + [(32 + s, l, m) for s, l, m in TAG], vel=0.6, inst="gurdy", tr=-12)
    for b in range(46, 54):
        drums(b, "climax")
        rf = {46: R_DRIVE, 47: R_DRIVE, 48: None, 49: None, 50: R_DRIVE_ANS, 51: R_DRIVE, 52: R_DRIVE, 53: R_DRIVE}[b]
        if rf is None:
            chops(b, steps=(2, 6, 10, 14), roots=lambda s: 38, vel=0.75)
            continue
        bassline(b, rf)
        chops(b, roots=riff_root(rf), vel=0.9)
    tag_bass(48, 1.0)

    # ---------------------------------------------------------------- DEVELOPMENT 55-62
    section(54, "CALL & RESPONSE", "fiddle and pipe trade the answer and the hook head; groove counter-line returns")
    drone_span(54, 62, (50, 57), [0.9, 0.7])
    lead(at(54), ANSWER2, vel=1.0, inst="fiddle", double=True)
    lead(at(56), [(0, 3, 74), (3, 1, 72), (4, 2, 69), (6, 2, 67), (8, 4, 69)], vel=1.0)                 # pipe: hook head
    lead(at(56, 12), [(0, 2, 62), (2, 2, 65), (4, 3, 67), (7, 1, 65), (8, 2, 64), (10, 2, 60), (12, 4, 62)],
         vel=0.95, inst="fiddle", double=True)                                                          # fiddle finishes it
    lead(at(58), ANSWER, vel=1.0)
    lead(at(58), ANSWER, vel=0.6, inst="lute", tr=-12)
    lead(at(60), GROOVE_LINE[:4], vel=0.95, inst="fiddle", double=True, legato=0.97)
    lead(at(60), GROOVE_LINE[:4], vel=0.55, inst="gurdy", legato=0.97)
    swell(61, 6, 10, vel=1.0)
    for b in range(54, 62):
        drums(b, "four")
        rf = R_ANS if b in (54, 58) else (r_groove(40) if b == 60 else (r_groove(39) if b == 61 else R_HOOK))
        bassline(b, rf)
        chops(b, roots=riff_root(rf), vel=0.75)
        if b in (56, 57):
            lute_arp(b, (50, 57, 62, 65), vel=0.55)
    tom_fill(61, 12, 16, 0.85)

    # ---------------------------------------------------------------- FINAL HOOK 63-70
    section(62, "FINAL HOOK", "hook + answer twice with everything: pipe, flute 8va, fiddles, gurdy an octave down")
    crash_at(62)
    drone_span(62, 70, (50, 57, 62), [1.0, 0.8, 0.45])
    for i, b in enumerate((62, 66)):
        lead(at(b), hook_full(fill=True), vel=1.1, double=True, octave_flute=(i == 1))
        lead(at(b + 2), ANSWER if i == 0 else ANSWER2, vel=1.1, double=True, octave_flute=(i == 1))
        lead(at(b), hook_full(fill=True) + [(32 + s, l, m) for s, l, m in (ANSWER if i == 0 else ANSWER2)],
             vel=0.6, inst="gurdy", tr=-12)
    for b in range(62, 70):
        drums(b, "climax")
        rf = R_DRIVE_ANS if b in (64, 68) else R_DRIVE
        bassline(b, rf)
        chops(b, roots=riff_root(rf), vel=0.9)
    roll(69, 1, start=8, vel=0.9)

    # ---------------------------------------------------------------- LAST DANCE 71-78
    section(70, "LAST DANCE", "drop-style hook chain at full drive, tag, band punches into the outro")
    crash_at(70)
    drone_span(70, 78, (50, 57, 62), [1.0, 0.8, 0.5])
    for gs0 in (at(70, 8),):
        lead(gs0, HOOK, vel=1.12, double=True, octave_flute=True)
        lead(gs0 + 24, ANSWER2, vel=1.12, double=True, octave_flute=True)
        lead(gs0, HOOK + [(s + 24, l, m) for s, l, m in ANSWER2], vel=0.65, inst="gurdy", tr=-12)
    lead(at(70), [(0, 8, 74)], vel=0.9, inst="fiddle", double=True)
    lead(at(74), TAG, vel=1.12, double=True, octave_flute=True)
    for b in range(70, 76):
        drums(b, "final")
        if b in (74, 75):
            if b == 74:
                tag_bass(74, 1.05)
        else:
            drop_bass(b, "ans" if b in (72, 73) else "hook", 1.05)
            bassline(b, [(2, 1, 50, 0.6, 1), (10, 1, 50, 0.55, 1), (14, 1, 50, 0.6, 1)])
        chops(b, roots=lambda s: 38, vel=0.85)
    drums(76, "final", skip=(4, 6, 10, 14, 15)); drums(77, "final", skip=tuple(range(8, 16)))
    bassline(76, R_DRIVE_ANS)
    lead(at(76), [(0, 6, 62)], vel=1.0, double=True)
    stop_hits(76, (6, 10), (39, 38), 1.0)
    stop_hits(77, (0, 3, 6), (38, 39, 38), 1.0)
    lead(at(77, 8), [(0, 1, 74), (1, 1, 72), (2, 1, 70), (3, 1, 69), (4, 1, 67), (5, 1, 65), (6, 1, 63), (7, 1, 62)],
         vel=0.9)                                                    # pipe run down the Phrygian scale
    tom_fill(77, 8, 16, 1.0)

    # ---------------------------------------------------------------- OUTRO 79-88
    section(78, "OUTRO", "the groove keeps dancing: answer, hook, then the pipe alone on the last hook; final D")
    crash_at(78)
    drone_span(78, 86, (50, 57, 62), [1.0, 0.75, 0.4], fade=0.1)
    lead(at(78), ANSWER, vel=1.05, double=True)
    lead(at(80), hook_full(), vel=1.05, double=True, octave_flute=True)
    lead(at(82), ANSWER2, vel=1.0, double=True)
    lead(at(83, 12), hook_pick()[:-1] + [(24, 8, 62)], vel=0.95)
    for b in range(78, 86):
        drums(b, "four" if b < 84 else "light")
        rf = R_ANS if b in (78, 82) else R_HOOK
        bassline(b, rf, 1.0 if b < 84 else 0.85)
        if b < 84:
            chops(b, roots=riff_root(rf), vel=0.75)
        else:
            lute_arp(b, (50, 57, 62, 57), vel=0.6)
    # final cadence: band hit on D, ring-out
    t_end = ts(at(86))
    def ring(x, hold=0.35, tau=0.9):
        t = np.arange(len(x)) / SR
        return x * np.where(t < hold, 1.0, np.exp(-(t - hold) / tau))
    T["kick"].add(E.club_kick(1.0, long=True), t_end)
    T["boom"].add(E.boom(1.0), t_end)
    T["cym"].add(E.crash(3.8, 0.9), t_end)
    T["bass"].add(ring(E.deep_bass(38, 3.4, 1.0), 0.4, 0.8), t_end)
    T["chop"].add(ring(E.strum([50, 57, 62, 69, 74], 3.4, 1.0), 0.5, 1.0), t_end)
    T["lute"].add(ring(E.strum([50, 57, 62], 3.4, 0.9), 0.5, 1.0), t_end)
    T["pipe"].add(ring(E.pipe(74, 3.2, 0.9), 0.6, 0.7), t_end)
    T["fiddle"].add(ring(E.fiddle(62, 3.4, 1.0, "legato"), 0.6, 0.9), t_end)
    T["fiddle2"].add(ring(E.fiddle(50, 3.4, 0.9, "legato", det=-5), 0.6, 0.9), t_end + 0.01)
    T["flute"].add(ring(E.flute(86, 3.0, 0.5), 0.5, 0.7), t_end)
    T["riq"].add(E.riq(1.0, long=True), t_end)
    T["drone"].add(ring(E.drone(4.6, [50, 57, 62], [1.0, 0.8, 0.5], fade=0.3), 0.6, 0.9), t_end)
    for b in (15, 21, 31, 39, 49, 57, 65, 81):
        phrase_fill(b, 0.9)
    ACCENTS.append((t_end, "hit", "final D"))
    return T
