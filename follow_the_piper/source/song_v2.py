"""
FOLLOW THE PIPER V2 -- score and arrangement (100 % instrumental).

Same hook, key, tempo and 37-bar form as V1 (song.py); re-arranged for more drive, groove and dread.
V1 helpers are copied here unchanged so V1 stays reproducible.

136 BPM, 4/4, 37 bars (65.294 s), A minor / harmonic minor with the Piper's tritone (D#).

The hook (alto recorder) is four bars on the 16th grid:
  CALL1    A4 . . E5 . . A5 . G#5 A5 E5 . D#5 - - -      tresillo rise, hangs on the tritone
  GIGGLE   (pause ...........) E6 . E6 . B5 -            the Piper giggles; the band answers in the gap
  CALL2    A4 . . E5 . . A5 . B5 C6 B5 . G#5 . E5 .
  CAD      F5 . . E5 . . C5 . B4 . C5 B4 G#4 - - -       open (G#) / closed (A)
Harmony: | Am | F | Am | F  E |

Notes are (step, length, midi[, opts]) with steps of a 16th relative to a bar start.
"""
import numpy as np
import dsp as D
from dsp import SR
import instruments as I
import samples as S

BPM = 136.0
BEAT = 60.0 / BPM
S16 = BEAT / 4
BAR = 4 * BEAT
NBARS = 37
LENGTH = NBARS * BAR                 # 65.294 s
TAIL = 4.0                           # rendered past the end, then wrapped onto the start (seamless loop)
N = int(round((LENGTH + TAIL) * SR))
NLOOP = int(round(LENGTH * SR))
SWING = 0.535                        # percussion 16ths only

# ------------------------------------------------------------------ pitches
A3, B3, C4, D4, Eb4, E4, F4, G4, Ab4 = 57, 59, 60, 62, 63, 64, 65, 67, 68
A4, Bb4, B4, C5, D5, Eb5, E5, F5, G5, Ab5, A5, Bb5, B5, C6, D6, E6 = 69, 70, 71, 72, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 86, 88
A1, Bb1, E1, F1, G1, Eb2 = 45, 46, 40, 41, 43, 51

# ------------------------------------------------------------------ melody
CALL1 = [(0, 3, A4, "acc"), (3, 3, E5), (6, 2, A5, "grace"), (8, 1, Ab5), (9, 1, A5), (10, 2, E5), (12, 4, Eb5, "hang")]
CALL1_ORN = [(0, 3, A4, "acc"), (3, 3, E5, "scoop"), (6, 2, A5, "grace"), (8, 1, B5), (9, 1, A5), (10, 1, E5), (11, 1, F5),
             (12, 4, Eb5, "hang")]
GIGGLE = [(6, 1, E6, "laugh"), (8, 1, E6, "laugh"), (10, 2, B5, "fall")]
GIGGLE_CHAT = [(6, 1, E6, "laugh"), (7, 1, D6), (8, 1, E6, "laugh"), (10, 2, B5), (12, 1, C6), (13, 1, B5), (14, 2, Ab5, "fall")]
GIGGLE_DARK = [(6, 1, E6, "laugh"), (8, 1, E6, "laugh"), (10, 3, Bb5, "fallbig")]
CALL2 = [(0, 3, A4, "acc"), (3, 3, E5), (6, 2, A5, "grace"), (8, 1, B5), (9, 1, C6), (10, 2, B5), (12, 2, Ab5), (14, 2, E5)]
CAD_OPEN = [(0, 3, F5, "acc"), (3, 3, E5), (6, 2, C5), (8, 2, B4), (10, 1, C5), (11, 1, B4), (12, 4, Ab4, "hang")]
CAD_CLOSED = [(0, 3, F5, "acc"), (3, 3, E5), (6, 2, C5), (8, 2, B4), (10, 2, Ab4), (12, 4, A4, "end")]
OBSESS = [(0, 2, A4), (2, 1, E5), (3, 1, A5), (4, 2, A4), (6, 1, E5), (7, 1, A5), (8, 1, Ab5), (9, 1, A5),
          (10, 1, E5), (11, 1, Eb5), (12, 1, E5), (13, 1, Eb5), (14, 1, E5), (15, 1, Ab5)]
BETRAY_FL = [(0, 3, F5, "acc"), (3, 3, E5), (6, 2, D5), (8, 2, Bb4), (10, 2, A4), (12, 4, Bb4, "hangdark")]
LAST = [(6, 1, E6, "laugh"), (8, 1, E6, "laugh"), (10, 2, B5, "fall"), (14, 2, Ab4, "pickup")]

# harmony roots per bar (bass midi; tuples = split bar at step 8)
ROOT = {}

# ------------------------------------------------------------------ grid helpers
def t_of(bar, step=0.0, swing=False):
    st = float(step)
    if swing:
        pair = np.floor(st / 2); r = st - 2 * pair
        frac = r * SWING if r <= 1 else SWING + (r - 1) * (1 - SWING)
        st = (pair + frac) * 2
    return bar * BAR + st * S16


def hum_t(sd=0.004):
    return D.rng().normal(0, sd)


# ------------------------------------------------------------------ tracks
class Track:
    def __init__(self, name):
        self.name = name
        self.buf = np.zeros((N, 2))

    def add(self, x, t, gain=1.0, pan=0.0):
        if x.ndim == 1:
            x = D.pan(x, pan)
        elif pan:
            x = D.width(x, 1.0)
            # balance
            x = x * np.array([np.sqrt(1 - max(0, pan)), np.sqrt(1 + min(0, pan))])
        i = max(0, int(round(t * SR)))          # never truncate an attack (keeps the loop seam clean)
        m = min(len(x), N - i)
        if m > 0:
            self.buf[i:i + m] += x[:m] * gain


NAMES = ["flute", "flute8", "flute_lo", "ghost", "fiddle", "fiddle_lo", "fsec", "gurdy", "drone", "chien",
         "strings", "ostinato", "pizz", "bowpad", "pluck", "bass", "sub", "kick", "bigdrum", "toms", "stomp", "clap",
         "snare", "tamb", "shaker", "darb", "frame", "wood", "cajon", "boom", "bells", "fx"]
T = {}
SECTIONS = []
ACCENTS = []
KICKS = []          # kick times for sidechain
from collections import defaultdict
EVENTS = defaultdict(list)
FLUTE_NOTES = []


def reset():
    T.clear(); SECTIONS.clear(); ACCENTS.clear(); KICKS.clear(); EVENTS.clear(); FLUTE_NOTES.clear()
    D.reseed(1284)
    for k in NAMES:
        T[k] = Track(k)


def section(bar, name, desc):
    SECTIONS.append(dict(bar=bar, name=name, desc=desc))


def accent(t, kind, desc, strength=1.0):
    ACCENTS.append(dict(time=round(float(t), 4), type=kind, description=desc, strength=strength))


# ------------------------------------------------------------------ kits (loaded once)
KIT = {}


def kits():
    if KIT:
        return KIT
    P = "Membranophones/Struck Membranophones/"
    Q = "Idiophones/Struck Idiophones/"
    KIT["clap"] = S.kit(Q + "Claps/Clap_rr*.wav")
    KIT["solo"] = S.kit(Q + "Claps/SoloClap_*.wav")
    KIT["tamb_hit"] = S.kit(Q + "Tambourine 1/Tamb1_Hit_*.wav") + S.kit(Q + "Tambourine 2/Tamb2_Hit_*.wav")
    KIT["tamb_shake"] = S.kit(Q + "Tambourine 1/Tamb1_Shake_*.wav") + S.kit(Q + "Tambourine 2/Tamb2_Shake_*.wav")
    KIT["tamb_roll"] = S.kit(Q + "Tambourine 1/Tamb1_Roll_v3*.wav")
    KIT["shaker"] = S.kit(Q + "Shaker, Small/Mid_Shaker*Faster_*.wav") + S.kit(Q + "Shaker, Small/Mid_ShakerDouble_*.wav")
    KIT["darb_doum"] = S.kit(P + "Darbuka/Darbuka_1_*.wav")
    KIT["darb_tek"] = S.kit(P + "Darbuka/Darbuka_3_*.wav") + S.kit(P + "Darbuka/Darbuka_4_*.wav")
    KIT["darb_ka"] = S.kit(P + "Darbuka/Darbuka_5_*.wav")
    KIT["frame_lo"] = S.kit(P + "Frame Drum/HDrumL_HitMuted_*.wav")
    KIT["frame_open"] = S.kit(P + "Frame Drum/HDrumL_Hit_*.wav")
    KIT["frame_hand"] = S.kit(P + "Frame Drum/HDrumL_Hand_*.wav") + S.kit(P + "Frame Drum/HDrumS_Hand_*.wav")
    KIT["snare"] = S.kit(P + "Snare Drum, Rope Tension/Hi/RopeSnare_hi_sn_*.wav")
    KIT["snare_lo"] = S.kit(P + "Snare Drum, Rope Tension/Low/RopeSnare_low_sn_*.wav")
    KIT["snare_ns"] = S.kit(P + "Snare Drum, Rope Tension/Low/RopeSnare_low_ns_*.wav")
    KIT["bd"] = S.kit(P + "Bass Drum 1/BDrumNew_hit_v5*.wav") + S.kit(P + "Bass Drum 1/BDrumNew_hit_v7*.wav")
    KIT["bd2"] = S.kit(P + "Bass Drum 2/bassdrum_hit_f*.wav")
    KIT["timp"] = S.kit(P + "Timpani 1/Hit/Timpani1_Hit_v4*.wav")
    KIT["gong"] = S.kit(Q + "Gong 1/gong_f.wav") + S.kit(Q + "Gong 1/gong_mf.wav")
    KIT["gong_scrape"] = S.kit(Q + "Gong 1/gong_scrape_mf.wav")
    KIT["anvil"] = S.kit(Q + "Anvil/Anvil_Hit2_*.wav")
    KIT["handbell"] = S.kit(Q + "Hand Bells, Nepalese/*.wav")
    # normalise each kit to unit peak (per hit), keep stereo
    for k, v in KIT.items():
        KIT[k] = [x / (np.abs(x).max() + 1e-9) for x in v]
    return KIT


def hit(trk, kitname, t, vel=1.0, pan=0.0, dur=None, pitch=0.0):
    K = kits()[kitname]
    x = K[D.rng().integers(len(K))]
    if dur is not None:
        n = min(len(x), int(dur * SR))
        x = x[:n].copy()
        r = min(n, int(0.03 * SR))
        x[-r:] *= np.linspace(1, 0, r)[:, None] if x.ndim == 2 else np.linspace(1, 0, r)
    if pitch:
        rr = 2 ** (pitch / 12)
        x = np.stack([D.resample_play(x[:, c], rr) for c in range(2)], 1) if x.ndim == 2 else D.resample_play(x, rr)
    v = vel * D.rng().uniform(0.92, 1.05)
    T[trk].add(x, t + hum_t(0.003), v, pan)


# ------------------------------------------------------------------ players
def play_flute(bar, notes, vel=1.0, which="alto", trk="flute", tr=0, legato=0.9, dark=False, ghost=0.0,
               detune=0.0, double8=0.0, pan=0.0):
    prev_end = None
    for nt in notes:
        s, l, m = nt[:3]
        opt = nt[3] if len(nt) > 3 else ""
        m = m + tr
        t = t_of(bar, s) + hum_t(0.003)
        d = l * S16 * legato
        sc = 0.0; vib = None; fall = 0.0; trill = None; v = vel
        slur = prev_end is not None and abs(prev_end - s) < 0.01 and l <= 1
        if s % 4 == 0:
            v *= 1.0
        elif s % 2 == 0:
            v *= 0.93
        else:
            v *= 0.88
        if opt == "acc":
            v *= 1.08; sc = -35
        if opt == "scoop":
            sc = -70
        if opt == "laugh":
            sc = -90; d = l * S16 * 0.62; v *= 0.95
        if opt == "fall":
            fall = -45
        if opt == "fallbig":
            fall = -160; d = l * S16 * 0.95
        if opt == "trillhang":
            trill = (1, 10.5, 0.22); d = l * S16 * 0.97; vib = None
        if opt in ("hang", "hangdark"):
            vib = 26 if opt == "hang" else 42; d = l * S16 * 0.97
            if opt == "hangdark":
                fall = -60
        if opt == "end":
            vib = 18; d = l * S16 * 1.0
        if opt == "pickup":
            sc = -40; d = l * S16 * 0.97
        if opt == "grace":
            # quick upper-neighbour-from-below grace into the note (G5 -> A5 style)
            g = I.recorder(m - 2, 0.034, v * 0.8, which=which, art="stac", release=0.012)
            T[trk].add(g, t - 0.034, 1.0, pan)
            slur = True
        x = I.recorder(m, d, v, which=which, slur=slur, scoop=sc, vib=vib, fall=fall, trill=trill,
                       breath=(1.0 if dark else 0.0), cents=detune)
        T[trk].add(x, t, 1.0, pan)
        if trk in ("flute", "flute_lo") and vel >= 0.5:
            FLUTE_NOTES.append(dict(time=round(float(t_of(bar, s)), 4), dur=round(l * S16, 4), midi=int(m),
                                    instrument=which, track=trk))
        if ghost:
            T["ghost"].add(x, t, ghost, 0.0)
        if double8 and m + 12 <= 96:
            y = I.recorder(m + 12, d, v * 0.9, which="sop", slur=slur, scoop=sc * 0.5, vib=vib, fall=fall)
            T["flute8"].add(y, t + 0.006, double8, 0.0)
        prev_end = s + l


def play_bass(bar, pat, root, vel=1.0, bright=1.0):
    """pat: list of (step, len, interval, vel) ; root midi (or (root1, root2) split at step 8)"""
    for s, l, iv, v in pat:
        r = root if np.isscalar(root) else (root[0] if s < 8 else root[1])
        m = r + iv
        x = I.bass(m, l * S16 * 0.92, vel * v, bright=bright)
        T["bass"].add(x, t_of(bar, s) + hum_t(0.002), 1.0, 0.0)


# bass patterns (step, len, interval, vel)
B_PRE = [(0, 3, 0, 1.0), (6, 2, 12, 0.7), (10, 2, 0, 0.85), (14, 2, 7, 0.7)]
B_PRE2 = [(0, 3, 0, 1.0), (6, 1, 12, 0.7), (10, 1, 0, 0.9), (11, 1, 0, 0.7), (14, 1, 0, 0.9), (15, 1, 12, 0.7)]
B_GALLOP = [(2, 1, 0, 0.9), (3, 1, 0, 0.78), (6, 1, 0, 0.88), (7, 1, 12, 0.72), (10, 1, 0, 0.9), (11, 1, 0, 0.78),
            (14, 1, 0, 0.88), (15, 1, 12, 0.74)]
B_GALLOP2 = [(2, 1, 0, 0.9), (3, 1, 0, 0.78), (6, 1, 0, 0.88), (7, 1, 0, 0.78), (10, 1, 0, 0.9), (11, 1, 12, 0.74),
             (14, 1, 7, 0.85), (15, 1, 12, 0.76)]
B_STOP = [(0, 2, 0, 1.0), (6, 1, 0, 0.95), (7, 1, 12, 0.7), (10, 1, 0, 1.0), (11, 1, 0, 0.72), (14, 1, 0, 0.95),
          (15, 1, 12, 0.72)]
B_HALF = [(0, 6, 0, 1.0), (8, 6, 0, 0.9)]
B_HIT = [(0, 3, 0, 1.0)]
B_LONG = [(0, 13, 0, 0.85), (14, 1, 12, 0.6), (15, 1, 0, 0.7)]
B_OBSESS = [(s, 1, (12 if s % 4 == 3 else 0), 1.0 if s % 2 == 0 else 0.75) for s in range(16)]


def kick_at(bar, steps, vel=1.0, lowpass=None):
    for s in steps:
        t = t_of(bar, s)
        x = I.kick(vel)
        if lowpass:
            x = D.lp(x, lowpass)
        T["kick"].add(x, t, 1.0, 0.0)
        KICKS.append((t, vel)); EVENTS["kick"].append(t)


def stomp_at(bar, steps, vel=1.0):
    for s in steps:
        T["stomp"].add(I.stomp(vel), t_of(bar, s) + hum_t(0.004), 1.0, 0.0)
        EVENTS["stomp"].append(t_of(bar, s))


def clap_at(bar, steps, vel=1.0, solo=False):
    for s in steps:
        hit("clap", "clap", t_of(bar, s), vel, D.rng().uniform(-0.15, 0.15))
        EVENTS["clap"].append(t_of(bar, s))
        if solo:
            hit("clap", "solo", t_of(bar, s) + 0.006, vel * 0.5, D.rng().choice([-0.6, 0.6]))


def snare_at(bar, steps, vel=1.0):
    for s in steps:
        hit("snare", "snare", t_of(bar, s), vel, 0.1)
        EVENTS["snare"].append(t_of(bar, s))


def tamb_8ths(bar, vel=1.0, steps=(2, 6, 10, 14)):
    for s in steps:
        hit("tamb", "tamb_hit", t_of(bar, s, True), vel, 0.62, dur=0.35)


def tamb_16(bar, vel=1.0):
    for s in range(16):
        v = vel * (0.85 if s % 4 == 2 else 0.8 if s % 4 == 0 else 0.5)
        hit("tamb", "tamb_shake", t_of(bar, s, True), v, 0.62, dur=0.12)


def shaker_16(bar, vel=1.0, steps=range(16)):
    for s in steps:
        v = vel * (0.9 if s % 2 == 1 else 0.6) * (1.15 if s % 4 == 2 else 1)
        hit("shaker", "shaker", t_of(bar, s, True), v, -0.68)


def darb_maqsum(bar, vel=1.0, fill=False):
    # doum . tek . . tek . . doum . tek . . tek . ka-ka
    pat = [(0, "darb_doum", 1.0), (2, "darb_tek", 0.8), (6, "darb_tek", 0.9), (8, "darb_doum", 0.95),
           (12, "darb_tek", 0.85)]
    if fill:
        pat = pat[:-1] + [(12, "darb_tek", 0.9), (13, "darb_ka", 0.6), (14, "darb_tek", 0.85), (15, "darb_ka", 0.7)]
    else:
        pat += [(14, "darb_ka", 0.5)]
    for s, k, v in pat:
        hit("darb", k, t_of(bar, s, True), vel * v, 0.38)


def frame_at(bar, steps, vel=1.0, kind="frame_lo"):
    for s in steps:
        hit("frame", kind, t_of(bar, s), vel, -0.25)


def boom(t, vel=1.0, kind="timp"):
    hit("boom", kind, t, vel, 0.0)
    EVENTS["boom"].append(t)


BELL_SHIFT = {"A": 3.0, "E": -2.0, "Bb": 4.0, "A+": 4.0}   # from the F#3 chime (strike note F#)


def bell_at(t, note="A", vel=1.0, shift=0.0, pan=-0.5, length=7.0):
    x = I.bell("F#3", vel, shift=BELL_SHIFT[note] + shift, length=length)
    T["bells"].add(x, t, 1.0, pan)
    EVENTS["bell"].append(t)


# chord tones for strings (psaltery spiccato dyads)
DYAD = {"A": (A4, E5), "F": (A4, C5), "E": (Ab4, B4), "Bb": (Bb4, D5), "Eb": (Bb4, Eb5), "Am_hi": (C5, E5)}


def strings_chop(bar, chords, vel=1.0, steps=(2, 6, 10, 14)):
    for s in steps:
        ch = chords if isinstance(chords, str) else (chords[0] if s < 8 else chords[1])
        for k, m in enumerate(DYAD[ch]):
            x = I.psaltery(m, S16 * 1.4, vel * 0.85 * (0.9 if k else 1.0) * (1.0 if s % 4 == 2 else 0.85), art="spic")
            T["strings"].add(x, t_of(bar, s, True) + hum_t(0.004), 1.0, 0.62 if k else -0.62)


def pluck_arp(bar, chord, vel=1.0, pat=None):
    tn = {"A": [57, 64, 69, 72], "F": [53, 60, 65, 69], "E": [52, 59, 64, 68], "Bb": [58, 62, 65, 70]}
    pat = pat or [(0, 0, 1.0), (2, 1, 0.6), (3, 2, 0.75), (6, 1, 0.7), (8, 3, 0.8), (10, 1, 0.6), (11, 2, 0.7), (14, 1, 0.65)]
    for s, idx, v in pat:
        c = chord if isinstance(chord, str) else (chord[0] if s < 8 else chord[1])
        m = tn[c][idx]
        x = I.strum(m, S16 * 2.5, vel * v)
        T["pluck"].add(x, t_of(bar, s, True) + hum_t(0.004), 1.0, -0.55)


# ------------------------------------------------------------------ hurdy-gurdy (rendered as continuous strings)
def render_gurdy(drone_plan, melody_notes, chien_steps, buzz_level):
    """drone_plan: list of (t0, t1, [midis], level); melody_notes: (t, dur, midi, vel);
    chien_steps: list of times for buzz strokes; buzz_level: function t->level"""
    # drones
    for (t0, t1, mids, lev, fi, fo) in drone_plan:
        a = int(t0 * SR); b = min(N, int(t1 * SR))
        n = b - a
        if n <= 0:
            continue
        for j, m in enumerate(mids):
            v = I.wheel(n, level=0.2, crank_hz=BPM / 60 / 2, attack=fi, release=fo)
            y = I.gurdy_string(np.full(n, float(m)), v, force=0.3, beta=0.11 + 0.01 * j, seed=11 + j + int(t0 * 7))
            y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05 * lev
            T["drone"].add(y, t0, 1.0, (-0.35, 0.35, 0.0, 0.15)[j % 4])
    # chien (buzz): the trompette string sounds continuously through each groove region; crank accents
    # make the 'dog' bridge rattle. Regions = runs of strokes with gaps shorter than a bar.
    if chien_steps:
        st = sorted(chien_steps)
        regions = [[st[0]]]
        for q in st[1:]:
            if q[0] - regions[-1][-1][0] > BAR * 1.2:
                regions.append([q])
            else:
                regions[-1].append(q)
        L = int(0.22 * SR)
        kern = np.exp(-np.arange(L) / (0.045 * SR)) * (1 - np.exp(-np.arange(L) / (0.004 * SR)))
        kern *= np.cos(np.linspace(0, np.pi / 2, L)) ** 2          # taper to zero: no cut-offs
        for reg in regions:
            t0 = reg[0][0] - 0.15; t1 = reg[-1][0] + 0.5
            a = int(t0 * SR); n = int((t1 - t0) * SR)
            pulses = np.zeros(n)
            for t, v in reg:
                i = int((t - t0) * SR)
                m = min(L, n - i)
                pulses[i:i + m] = np.maximum(pulses[i:i + m], v * kern[:m])
            vb = I.wheel(n, level=0.2, crank_hz=BPM / 60, attack=0.12, release=0.35) * (1 + 0.9 * pulses)
            tr = I.gurdy_string(np.full(n, float(A3)), vb, force=0.42, beta=0.13, seed=a % 9973)
            tr = tr / (np.sqrt(np.mean(tr ** 2)) + 1e-9) * 0.05
            bz = I.chien(tr, pulses, 1.0)
            T["chien"].add(bz + tr * (0.12 + 0.25 * pulses), t0, 1.0, 0.4)
    # keyed melody: continuous string with stepwise pitch, re-bowed per phrase
    if melody_notes:
        # group into phrases separated by > 1 beat gaps
        melody_notes = sorted(melody_notes)
        phrases = [[melody_notes[0]]]
        for nt in melody_notes[1:]:
            pe = phrases[-1][-1][0] + phrases[-1][-1][1]
            if nt[0] - pe > BEAT * 0.9:
                phrases.append([nt])
            else:
                phrases[-1].append(nt)
        for ph in phrases:
            t0 = ph[0][0]; t1 = ph[-1][0] + ph[-1][1]
            n = int((t1 - t0 + 0.25) * SR)
            mc = np.full(n, float(ph[0][2])); amp = np.zeros(n)
            for (t, d, m, v) in ph:
                a = int((t - t0) * SR); b = min(n, int((t - t0 + d) * SR))
                mc[a:] = m
                amp[a:b] = v
            from scipy.ndimage import uniform_filter1d
            mc = uniform_filter1d(mc, int(0.006 * SR))        # key-change glitch smoothing
            amp = uniform_filter1d(amp, int(0.04 * SR))
            vb = 0.08 + 0.2 * amp
            y = I.gurdy_string(mc, vb * I.adsr(n, 0.06, 0.05, 1.0, 0.2), force=0.33, beta=0.12, seed=int(t0 * 100))
            y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05
            T["gurdy"].add(y * np.clip(amp * 1.4, 0, 1), t0, 1.0, -0.45)




# =========================================================================== V2 helpers
GAPS = []            # (t0, t1): full-band silences (everything except the lead flute and reverb tails)


def kits2():
    K = kits()
    if "wood" in K:
        return K
    P = "Membranophones/Struck Membranophones/"
    Q = "Idiophones/Struck Idiophones/"
    add = {
        "wood": S.kit(Q + "Woodblock/wood_click_f_*.wav") + S.kit(Q + "Woodblock/wood_click_mp.wav"),
        "wood_pp": S.kit(Q + "Woodblock/wood_click_pp_*.wav"),
        "claves": S.kit(Q + "Claves/Claves1_Hit_v2*.wav") + S.kit(Q + "Claves/Claves1_Hit_v3*.wav"),
        "slit_hi": S.kit(Q + "Slit Drum/LogDrumHi_*.wav"),
        "slit_lo": S.kit(Q + "Slit Drum/LogDrumLo_*.wav"),
        "cajon_b": S.kit(Q + "Cajon/Cajon_hit1_f_*.wav"),
        "cajon_s": S.kit(Q + "Cajon/Cajon_hit3_f_*.wav") + S.kit(Q + "Cajon/Cajon_hit3_mp_*.wav"),
        "cajon_g": S.kit(Q + "Cajon/Cajon_hit2_pp_*.wav") + S.kit(Q + "Cajon/Cajon_hit3_p_*.wav"),
        "tom_lo": S.kit(P + "Tom 2/Mallet/TomL_HitM_v4_*.wav") + S.kit(P + "Tom 2/Mallet/TomL_HitM_v3_*.wav"),
        "tom_hi": S.kit(P + "Tom 1/Mallet/TomH_HitM_v4_*.wav") + S.kit(P + "Tom 1/Mallet/TomH_HitM_v3_*.wav"),
        "tom_rim": S.kit(P + "Tom 2/TomL_rimS_*.wav"),
        "big": S.kit(P + "Bass Drum 3 - Legacy/bdrum_ff*.wav") + S.kit(P + "Bass Drum 3 - Legacy/bdrum_fff_*.wav") + S.kit(P + "Bass Drum 1/BDrumNew_hit_v7*.wav"),
        "big_m": S.kit(P + "Bass Drum 3 - Legacy/bdrum_muted_ff*.wav") + S.kit(P + "Bass Drum 3 - Legacy/bdrum_muted_mf*.wav"),
        "ratchet": S.kit(Q + "Ratchet/Ratchet1_Fast_*.wav") + S.kit(Q + "Ratchet/Ratchet2_Fast_*.wav"),
    }
    for k, v in add.items():
        assert v, k
        K[k] = [x / (np.abs(x).max() + 1e-9) for x in v]
    return K


def gap(bar, s0, s1):
    GAPS.append((t_of(bar, s0) - 0.004, t_of(bar, s1) - 0.006))
    accent(t_of(bar, s0), "gap", "Full-band silence (only the Piper)", 0.9)


def fiddle_line(bar, notes, trk="fiddle", tr=0, vel=1.0, players=1, pan=0.25, seed=None, legato=0.97, vib=18):
    """notes: (step, len, midi[, opt]) from a bar (steps may run past 16)"""
    nn = [(s * S16, l * S16 * legato, m + tr, 1.0 if (s % 4 == 0) else 0.9) for s, l, m, *_ in notes]
    total = max(s + l for s, l, *_ in notes) * S16
    sd = int(bar * 131 + tr * 7 + (seed or 0))
    if players > 1:
        x = I.fiddle_section(nn, total, players=players, vel=vel, seed=sd, vib=vib)
        T[trk].add(x, t_of(bar, 0), 1.0)
    else:
        x = I.fiddle(nn, total, vel=vel, seed=sd, vib=vib)
        T[trk].add(x, t_of(bar, 0), 1.0, pan)


def fsec_chord(bar, step, midis, dur_steps, vel=1.0, players=2, swell=False):
    """sustained fiddle-section chord (one line per pitch) -- replaces V1's choir pads"""
    for k, m in enumerate(midis):
        d = dur_steps * S16
        nn = [(0.0, d, m, 1.0)]
        x = I.fiddle_section(nn, d, players=players, vel=vel, seed=bar * 17 + k + step, vib=14, accent=0.0)
        if swell:
            x *= np.linspace(0.25, 1.0, len(x))[:, None] ** 1.5
        T["fsec"].add(x, t_of(bar, step), 1.0)


def big_at(bar, steps, vel=1.0, muted=False):
    for s in steps:
        hit("bigdrum", "big_m" if muted else "big", t_of(bar, s), vel, 0.0, dur=1.2)
        EVENTS["big_drum"].append(t_of(bar, s))


def toms_tresillo(bar, vel=1.0, fill=False):
    """davul-style toms answering the kick with the hook's 3+3+2: lo s3, hi s6 | lo s11, hi s14"""
    pat = [(3, "tom_lo", 0.9), (6, "tom_hi", 0.8), (11, "tom_lo", 0.85), (14, "tom_hi", 0.75)]
    if fill:
        pat = [(3, "tom_lo", 0.9), (6, "tom_hi", 0.8), (10, "tom_hi", 0.75), (11, "tom_hi", 0.8), (12, "tom_lo", 0.85),
               (13, "tom_lo", 0.9), (14, "tom_lo", 1.0), (15, "tom_lo", 1.0)]
    for s, k, v in pat:
        hit("toms", k, t_of(bar, s, True), vel * v, -0.2 if k == "tom_lo" else 0.25, dur=0.7)
        EVENTS["tom"].append(t_of(bar, s))


def claves_at(bar, steps=(0, 3, 6, 10, 12), vel=1.0):
    for s in steps:
        hit("wood", "claves", t_of(bar, s, True), vel, 0.5, dur=0.25)
        EVENTS["claves"].append(t_of(bar, s))


def woodtick(bar, steps=(1, 5, 9, 13), vel=1.0, pan=-0.45):
    for s in steps:
        hit("wood", "wood_pp" if vel < 0.6 else "wood", t_of(bar, s, True), vel, pan, dur=0.2)


def slit_at(bar, pat, vel=1.0):
    for s, k in pat:
        hit("wood", "slit_lo" if k == "lo" else "slit_hi", t_of(bar, s), vel, -0.3 if k == "lo" else 0.3, dur=0.6)


def cajon_groove(bar, vel=1.0):
    for s, k, v in [(4, "cajon_s", 0.55), (7, "cajon_g", 0.5), (12, "cajon_s", 0.55), (13, "cajon_g", 0.4),
                    (15, "cajon_g", 0.55)]:
        hit("cajon", k, t_of(bar, s, True), vel * v, 0.15, dur=0.35)


def ratchet_build(bar, step, dur_steps, vel=0.8):
    x = kits2()["ratchet"][0]
    n = min(len(x), int(dur_steps * S16 * SR))
    y = x[:n] * (np.linspace(0.05, 1.0, n) ** 2)[:, None]
    y[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    T["fx"].add(y, t_of(bar, step), vel, 0.0)


def answer(bar, chord="A", steps=((0, 2), (3, 2)), vel=1.0, big=True):
    """the band answers the flute's pause (replaces V1's crowd chant): unison string stab + low toms +
    woodblock + bass, on the hook's own tresillo"""
    roots = {"A": (A3 - 12, [57, 64, 69]), "F": (F4 - 24, [53, 60, 65]), "E": (E4 - 24, [52, 59, 64]),
             "Eb": (Eb4 - 24, [51, 57, 63]), "Bb": (Bb4 - 24, [58, 62, 65])}
    r, tri = roots[chord]
    for i, (s, l) in enumerate(steps):
        v = vel * (0.85 if i == 0 else 1.0)
        nn = [(0.0, l * S16 * 0.8, m, 1.0) for m in tri[:1]]
        for k, m in enumerate(tri):
            x = I.fiddle([(0.0, l * S16 * 0.75, m, 1.0)], l * S16, vel=v * 1.1, seed=bar * 31 + s + k, vib=0,
                         accent=0.9)
            T["fsec"].add(x, t_of(bar, s), 1.0, (-0.5, 0.0, 0.5)[k])
        for m in (DYAD["A"] if chord == "A" else DYAD.get(chord, DYAD["A"])):
            T["strings"].add(I.psaltery(m, S16 * 1.2, v, art="spic"), t_of(bar, s), 1.0, 0.0)
        hit("toms", "tom_lo", t_of(bar, s), v, -0.1, dur=0.8)
        hit("wood", "wood", t_of(bar, s), v * 0.8, 0.35, dur=0.2)
        if big:
            hit("bigdrum", "big_m", t_of(bar, s), v * 0.8, 0.0, dur=0.8)
        T["bass"].add(I.bass2(r, l * S16 * 0.85, v), t_of(bar, s), 1.0, 0.0)
        T["sub"].add(I.sub(r, l * S16 * 0.85, v), t_of(bar, s), 1.0, 0.0)
        EVENTS["band_answer"].append(t_of(bar, s))


OST = {"A": [81, 76, 84, 76, 81, 76, 82, 76], "F": [81, 77, 84, 77, 81, 77, 82, 77], "E": [80, 76, 83, 76, 80, 76, 82, 76],
       "Bb": [82, 77, 86, 77, 82, 77, 81, 77]}


def ostinato(bar, chord, vel=1.0, steps=range(16)):
    """clockwork psaltery spiccato 16ths -- the Piper's spell; note 7 of each 8 is the Bb rub"""
    for s in steps:
        ch = chord if isinstance(chord, str) else (chord[0] if s < 8 else chord[1])
        m = OST[ch][s % 8]
        v = vel * (1.0 if s % 4 == 0 else 0.7 if s % 2 == 0 else 0.55)
        T["ostinato"].add(I.psaltery(m, S16 * 0.9, v, art="spic"), t_of(bar, s, True) + hum_t(0.002), 1.0,
                          0.45 if s % 2 else -0.45)


def pizz_echo(bar, notes, delay_steps=3, vel=0.7, tr=0, pan=0.6):
    """plucked psaltery echoes the flute's giggle a dotted-8th later (instrumental 'laughter')"""
    for s, l, m, *_ in notes:
        st = s + delay_steps
        T["pizz"].add(I.psaltery(m + tr, S16 * 1.5, vel, art="pluck"), t_of(bar, st), 1.0, pan)


def bass_line(bar, pat, root, vel=1.0, bright=1.0, sub_vel=0.0):
    for s, l, iv, v in pat:
        r = root if np.isscalar(root) else (root[0] if s < 8 else root[1])
        m = r + iv
        T["bass"].add(I.bass2(m, l * S16 * 0.9, vel * v, bright=bright), t_of(bar, s) + hum_t(0.0015), 1.0, 0.0)
        if sub_vel and iv == 0:
            T["sub"].add(I.sub(m, l * S16 * 0.85, sub_vel * v), t_of(bar, s), 1.0, 0.0)


B_ROLL = [(2, 1, 0, 0.9), (3, 1, 0, 0.78), (6, 1, 0, 0.88), (7, 1, 12, 0.72), (10, 1, 0, 0.9), (11, 1, 0, 0.78),
          (13, 1, 0, 0.8), (14, 1, 7, 0.88), (15, 1, 12, 0.85)]


# =========================================================================== V2 ARRANGEMENT
def arrange():
    reset()
    GAPS.clear()
    kits2()
    gurdy_mel = []
    chien = []
    drone_plan = []

    def gm(bar, notes, vel=0.9, tr=0):
        for s, l, m in notes:
            gurdy_mel.append((t_of(bar, s), l * S16 * 0.98, m + tr, vel))

    def chien_bar(bar, vel=1.0, steps=(2, 6, 10, 14)):
        for s in steps:
            chien.append((t_of(bar, s), vel * (0.85 if s in (2, 10) else 0.7)))

    # ================================================================ 0-3.5 s  THE HYPNOTIC HOOK
    section(0, "intro_hook", "A deep drum and a bell strike at 0.000 s with the Piper's call; buzzing hurdy-gurdy "
                             "drone, a wooden slit-drum heartbeat on the hook's 3+3+2, claves answer the pause.")
    play_flute(0, CALL1, 1.05, ghost=0.35)
    play_flute(1, GIGGLE, 1.0, ghost=0.45)
    pizz_echo(1, GIGGLE, 3, 0.45, pan=0.65)
    big_at(0, (0,), 0.75)
    hit("toms", "tom_lo", t_of(0, 0), 0.6, 0.0, dur=0.8)
    bell_at(t_of(0, 0), "A", 0.6, pan=-0.6)
    drone_plan.append((0.0, t_of(2, 0) + 0.3, [A3 - 12, E4 - 12], 0.5, 0.04, 0.3))
    chien_bar(0, 0.55, steps=(0,)); chien_bar(1, 0.5, steps=(0,))
    slit_at(0, [(0, "lo"), (3, "hi"), (6, "hi"), (8, "lo"), (11, "hi"), (14, "hi")], 0.55)
    slit_at(1, [(0, "lo"), (8, "lo"), (11, "hi"), (14, "hi")], 0.5)
    claves_at(1, (2, 3), 0.45)
    hit("tamb", "tamb_shake", t_of(1, 12), 0.35, 0.6, dur=0.3)
    accent(0.0, "hook", "Drum + bell + flute hook at 0.000 s (A4)", 1.0)
    accent(t_of(0, 12), "hook", "Tritone D#5 hang -- the Piper's signature note", 0.9)
    accent(t_of(1, 2), "wood", "Claves answer in the pause", 0.4)
    accent(t_of(1, 6), "flute_giggle", "Flute giggle E6 E6 B5, echoed by plucked psaltery", 0.6)

    # ================================================================ 3.5-12.4 s  THE RATS AWAKEN
    section(2, "rats_awaken", "Stomps, claps, strumstick, shaker and plucky bass; tambourine; then kick, toms on "
                              "the hook's tresillo and darbuka; the band answers the pause; ratchet + roll build "
                              "into a one-eighth silence.")
    drone_plan.append((t_of(2, 0), t_of(14, 0), [A3 - 12, E4 - 12], 0.8, 0.2, 0.2))
    play_flute(2, CALL2, 1.0, ghost=0.25)
    stomp_at(2, (0, 8), 0.85); clap_at(2, (4, 12), 0.6)
    pluck_arp(2, "A", 0.85)
    bass_line(2, B_PRE, A1, 0.8, bright=0.7)
    shaker_16(2, 0.4, steps=(2, 6, 10, 14))
    slit_at(2, [(0, "lo"), (3, "hi"), (6, "hi")], 0.45)
    accent(t_of(2, 0), "groove_in", "Stomps + claps + strumstick + bass enter", 0.8)
    play_flute(3, CAD_OPEN, 1.0)
    stomp_at(3, (0, 8), 0.9); clap_at(3, (4, 12), 0.65)
    pluck_arp(3, ("F", "E"), 0.85)
    bass_line(3, B_PRE, (F1, E1), 0.8, bright=0.7)
    shaker_16(3, 0.45); tamb_8ths(3, 0.5)
    woodtick(3, (14, 15), 0.6)
    play_flute(4, CALL1_ORN, 1.0)
    fiddle_line(4, CALL1_ORN, trk="fiddle", tr=-12, vel=0.5, pan=-0.3)
    kick_at(4, (0, 4, 8, 12), 0.8, lowpass=1200)
    stomp_at(4, (0, 8), 0.85); clap_at(4, (4, 12), 0.65)
    toms_tresillo(4, 0.6)
    darb_maqsum(4, 0.55)
    pluck_arp(4, "A", 0.75)
    bass_line(4, B_PRE2, A1, 0.9, bright=0.85)
    shaker_16(4, 0.45); tamb_8ths(4, 0.55)
    accent(t_of(4, 0), "kick_in", "Kick, toms (3+3+2) and darbuka enter; low fiddle shadows the flute", 0.8)
    play_flute(5, GIGGLE, 1.0, ghost=0.3)
    pizz_echo(5, GIGGLE, 3, 0.5)
    kick_at(5, (0, 4, 8, 12), 0.85, lowpass=1800)
    answer(5, "F", vel=0.7, big=False)
    stomp_at(5, (8,), 0.85); clap_at(5, (4, 12), 0.65)
    darb_maqsum(5, 0.6)
    strings_chop(5, "F", 0.6, steps=(6, 10, 14))
    bass_line(5, [(6, 1, 12, 0.7), (10, 1, 0, 0.9), (11, 1, 0, 0.7), (14, 1, 0, 0.9), (15, 1, 12, 0.7)], F1, 0.9)
    shaker_16(5, 0.5); tamb_8ths(5, 0.55)
    accent(t_of(5, 0), "band_answer", "First band answer in the hook's pause (strings + toms + wood + bass)", 0.8)
    # bar 6 BUILD
    play_flute(6, CALL2[:4], 1.05)
    play_flute(6, [(8, 1, B5), (9, 1, C6), (10, 1, B5), (11, 1, C6), (12, 1, B5), (13, 1, C6)], 0.9, legato=0.8)
    fiddle_line(6, [(8, 1, B4), (9, 1, C5), (10, 1, B4), (11, 1, C5), (12, 1, B4), (13, 1, C5)], trk="fsec", vel=0.6,
                players=2)
    kick_at(6, (0, 4, 8, 10, 12, 13), 0.85, lowpass=3000)
    stomp_at(6, (0, 4, 8, 10, 12, 13), 0.9)
    toms_tresillo(6, 0.7, fill=True)
    T["snare"].add(I.snare_roll(6 * S16, 0.15, 0.9, rate=1 / S16 * 2, kit_hits=kits()["snare"]), t_of(6, 8))
    ratchet_build(6, 6, 8, 0.6)
    bass_line(6, [(0, 3, 0, 1.0), (6, 1, 12, 0.7), (8, 1, 0, 0.8), (10, 1, 0, 0.85), (12, 1, 0, 0.9), (13, 1, 0, 1.0)], A1, 0.9)
    darb_maqsum(6, 0.6, fill=True)
    hit("fx", "gong_scrape", t_of(6, 0), 0.2, 0.0)
    gap(6, 14, 16)
    accent(t_of(6, 8), "build", "Ratchet + snare roll + tom fill into the drop", 0.9)

    # ================================================================ 12.4-24.7 s  FIRST DROP
    section(7, "first_drop", "The whole town dances: kick + big drum, galloping bass with sub, toms on 3+3+2, claps "
                             "and rope snare, tambourine 16ths, cajon, darbuka, psaltery chops, buzzing hurdy-gurdy; "
                             "a fiddle doubles the flute; every pause is answered by the band.")
    seq = [(7, CALL1, "A", A1, "call"), (8, GIGGLE, "F", F1, "giggle"), (9, CALL2, "A", A1, "call"),
           (10, CAD_OPEN, ("F", "E"), (F1, E1), "cad"), (11, CALL1_ORN, "A", A1, "call"),
           (12, GIGGLE_CHAT, "F", F1, "giggle"), (13, CALL2, "A", A1, "call")]
    for bar, mel, ch, root, kind in seq:
        late = bar >= 11
        play_flute(bar, mel, 1.08, double8=(0.3 if late else 0.0), ghost=0.12, legato=0.86)
        fiddle_line(bar, mel, trk="fiddle", vel=0.75 if late else 0.6, pan=0.3)
        if kind == "giggle":
            pizz_echo(bar, mel, 3, 0.55)
            kick_at(bar, (8, 12), 1.0)
            answer(bar, ch, vel=0.95)
            bass_line(bar, [(6, 1, 0, 0.9), (7, 1, 12, 0.7), (10, 1, 0, 0.95), (11, 1, 0, 0.75), (14, 1, 0, 0.9),
                            (15, 1, 12, 0.75)], root, 1.0, sub_vel=0.8)
            clap_at(bar, (12,), 0.9, solo=True); snare_at(bar, (12,), 0.7)
            tamb_8ths(bar, 0.7, steps=(10, 14))
            strings_chop(bar, ch, 0.75, steps=(10, 14))
            chien_bar(bar, 0.8, steps=(10, 14))
            shaker_16(bar, 0.55, steps=range(8, 16))
            stomp_at(bar, (8,), 0.9)
            accent(t_of(bar, 0), "band_answer", "Band answers the pause on 3+3+2 (strings, toms, wood, bass)", 0.9)
        else:
            kick_at(bar, (0, 4, 8, 12), 1.0)
            big_at(bar, (0,), 0.85 if bar in (7, 11) else 0.55)
            bass_line(bar, B_GALLOP if bar % 2 else B_GALLOP2, root, 1.0, sub_vel=0.8)
            stomp_at(bar, (0, 8) if not late else (0, 3, 8), 0.95)
            clap_at(bar, (4, 12), 0.85, solo=late); snare_at(bar, (4, 12), 0.65)
            toms_tresillo(bar, 0.75, fill=(bar == 10))
            tamb_16(bar, 0.65)
            cajon_groove(bar, 0.7)
            strings_chop(bar, ch, 0.7 if not late else 0.85)
            chien_bar(bar, 1.0)
            shaker_16(bar, 0.5)
        darb_maqsum(bar, 0.6, fill=(bar in (10, 13)))
        if bar in (9, 13):
            frame_at(bar, (0, 6, 8, 14), 0.7, "frame_open")
    gm(9, [(0, 8, E4), (8, 8, A4)]); gm(10, [(0, 8, A4), (8, 8, Ab4)])
    gm(11, [(0, 8, E5 - 12), (8, 8, A4)]); gm(12, [(6, 10, C5)]); gm(13, [(0, 8, E5), (8, 4, Ab5 - 12), (12, 4, B4)])
    boom(t_of(7, 0), 1.0)
    bell_at(t_of(7, 0), "A", 0.8, pan=0.55)
    hit("fx", "anvil", t_of(11, 0), 0.4, 0.6)
    fsec_chord(13, 0, [A3, E4, C5], 16, vel=0.7, swell=True)
    accent(t_of(7, 0), "drop", "FIRST DROP downbeat (kick + big drum + timpani + bell)", 1.0)
    accent(t_of(11, 0), "variation", "Soprano octave joins, ornamented hook, tresillo stomps, anvil", 0.7)
    for b in range(7, 14):
        accent(t_of(b, 0), "downbeat", f"bar {b + 1}", 0.5)

    # ================================================================ 24.7-31.8 s  THE BETRAYAL
    section(14, "betrayal", "The cadence turns: Bb (bII) then Eb (the tritone) under an A drone that will not move; "
                            "half-time toms; a unison hit and a silence with only stomps; the Piper's giggle echoes; "
                            "the groove re-ignites on E with a chromatic creep.")
    play_flute(14, BETRAY_FL, 1.0, ghost=0.4)
    fiddle_line(14, BETRAY_FL, trk="fiddle", tr=-12, vel=0.7, pan=-0.3)
    kick_at(14, (0, 4, 8, 12), 1.0)
    big_at(14, (0,), 0.9)
    bass_line(14, B_GALLOP, Bb1, 1.0, sub_vel=0.8)
    stomp_at(14, (0, 8), 0.9)
    strings_chop(14, "Bb", 0.7)
    tamb_8ths(14, 0.6)
    toms_tresillo(14, 0.7)
    hit("boom", "gong", t_of(14, 0), 0.55, 0.0)
    bell_at(t_of(14, 0), "Bb", 0.6, pan=-0.5)
    fsec_chord(14, 0, [D4, F4, Bb4 - 12, A4], 16, vel=0.6)
    accent(t_of(14, 0), "betrayal", "Harmony betrays: Bb under the hook, gong", 1.0)
    play_flute(15, [(0, 6, Eb4, "hangdark"), (6, 2, E4), (8, 8, Eb4, "hangdark")], 0.9, which="tenor", trk="flute_lo",
               dark=True)
    kick_at(15, (0, 8), 1.0)
    big_at(15, (0, 8), 0.7, muted=True)
    hit("toms", "tom_lo", t_of(15, 6), 0.8, -0.2, dur=0.7); hit("toms", "tom_lo", t_of(15, 14), 0.8, -0.2, dur=0.7)
    bass_line(15, B_HALF, Eb2, 0.95, sub_vel=0.8)
    stomp_at(15, (0, 4, 8, 12), 0.9)
    clap_at(15, (12,), 0.6)
    fsec_chord(15, 0, [Eb4 - 12, A3, Bb4 - 12, Eb4], 16, vel=0.65, swell=True)
    shaker_16(15, 0.35, steps=(2, 6, 10, 14))
    play_flute(15, [(12, 1, E6, "laugh"), (14, 1, E6, "laugh")], 0.45, ghost=0.9)
    accent(t_of(15, 0), "half_time", "Half-time on the tritone Eb, low tenor recorder, fiddles swell", 0.8)
    kick_at(16, (0,), 1.0)
    big_at(16, (0,), 1.0)
    bass_line(16, B_HIT, Eb2, 1.0, sub_vel=1.0)
    boom(t_of(16, 0), 0.9)
    answer(16, "Eb", steps=((0, 2),), vel=1.0, big=False)
    stomp_at(16, (4, 8, 12), 0.75)
    play_flute(16, [(10, 1, E6, "laugh"), (12, 1, E6, "laugh")], 0.55, ghost=0.8)
    pizz_echo(16, [(10, 1, E6), (12, 1, E6)], 3, 0.35, tr=-1, pan=-0.6)       # echo a semitone flat: wrong
    accent(t_of(16, 0), "hit", "Unison hit, then the rhythmic pause (only stomps)", 0.9)
    accent(t_of(16, 2), "pause", "Silence except stomps; the giggle echoes a semitone flat", 0.7)
    kick_at(17, (0, 4, 8, 12), 0.95, lowpass=1500)
    bass_line(17, B_GALLOP, E1, 0.9, sub_vel=0.6)
    stomp_at(17, (0, 8), 0.9)
    tamb_16(17, 0.55)
    T["tamb"].add(kits()["tamb_roll"][0][:int(BAR * SR)] * np.linspace(0.1, 0.6, int(BAR * SR))[:, None], t_of(17, 0), 1.0, 0.4)
    creep = [(8, 2, E4), (10, 2, F4), (12, 2, F4 + 1), (14, 1, G4), (15, 1, Ab4)]
    play_flute(17, creep, 0.95, which="tenor", trk="flute_lo")
    fiddle_line(17, creep, trk="fsec", vel=0.7, players=3)
    toms_tresillo(17, 0.7, fill=True)
    bell_at(t_of(17, 0), "E", 0.45, pan=0.6)
    darb_maqsum(17, 0.5, fill=True)
    accent(t_of(17, 0), "regroove", "Groove re-ignites on E; chromatic creep E-F-F#-G-G# in flute and fiddles", 0.7)

    # ================================================================ 31.8-40.6 s  THE PIPER RETURNS
    section(18, "piper_returns", "The hook returns darker and stranger: airy, shadowed flute with a ghost tenor 28 cents flat, "
                                 "a dark fiddle an octave below, A against Bb in drone and high psaltery, a clockwork "
                                 "psaltery ostinato begins; the giggle lands on Bb and its echo answers wrong.")
    drone_plan.append((t_of(14, 0), t_of(18, 0), [A3 - 12, E4 - 12], 0.7, 0.05, 0.1))
    drone_plan.append((t_of(18, 0), t_of(23, 0), [A3 - 12, E4 - 12, Bb4 - 24], 0.85, 0.05, 0.05))
    ret = [(18, CALL1, A1, "A"), (19, GIGGLE_DARK, F1, "F"), (20, CALL2, A1, "A"), (21, CAD_OPEN, (F1, E1), ("F", "E"))]
    for k, (bar, mel, root, ch) in enumerate(ret):
        play_flute(bar, mel, 0.95, dark=True, ghost=0.3)
        play_flute(bar, mel, 0.38, which="tenor", trk="flute_lo", tr=0, detune=-28)
        fiddle_line(bar, mel, trk="fiddle_lo", tr=-12, vel=0.75, pan=-0.35, vib=26)
        kick_at(bar, (0, 4, 8, 12), 0.9, lowpass=600 + 600 * k)
        bass_line(bar, B_LONG, root, 0.9, bright=0.55, sub_vel=0.7)
        stomp_at(bar, (0, 8), 0.75)
        shaker_16(bar, 0.4)
        woodtick(bar, (1, 5, 9, 13), 0.45 + 0.08 * k)
        ostinato(bar, ch, 0.25 + 0.08 * k)
        if k >= 1:
            toms_tresillo(bar, 0.45 + 0.1 * k)
        if k >= 2:
            tamb_8ths(bar, 0.45)
    pizz_echo(19, GIGGLE_DARK, 3, 0.5, tr=1, pan=0.65)        # the echo answers a semitone sharp
    for bar in (18, 20):
        T["bowpad"].add(I.psaltery(A5, BAR * 2 - 0.1, 0.5, art="bow"), t_of(bar, 0), 1.0, -0.6)
        T["bowpad"].add(I.psaltery(Bb5, BAR * 2 - 0.1, 0.42, art="bow"), t_of(bar, 2), 1.0, 0.6)
    fsec_chord(18, 0, [A3, Bb4 - 12, E4], 32, vel=0.5, swell=True)
    fsec_chord(20, 0, [A3, Bb4 - 12, E4, Ab4], 32, vel=0.55)
    bell_at(t_of(18, 0), "A", 0.7, pan=-0.4)
    bell_at(t_of(18, 8), "A+", 0.45, pan=0.5)
    gm(20, [(0, 16, A4)], 0.6); gm(21, [(0, 8, A4), (8, 8, Ab4)], 0.7)
    accent(t_of(18, 0), "return", "The Piper returns (darker hook); clockwork ostinato starts", 1.0)
    accent(t_of(19, 10), "wrong_note", "Giggle lands on Bb5 and bends down; its echo answers a semitone sharp", 0.7)
    # bar 22 BUILD 2
    play_flute(22, [(0, 3, A4, "acc"), (3, 3, E5), (6, 2, A5)], 1.0, ghost=0.6)
    play_flute(22, [(8, 1, A4), (9, 1, E5), (10, 1, A5), (11, 1, E5), (12, 1, A5), (13, 1, Ab5)], 0.95, legato=0.85)
    fiddle_line(22, [(8, 1, A4), (9, 1, E5), (10, 1, A5), (11, 1, E5), (12, 1, A5), (13, 1, Ab5)], trk="fsec",
                tr=-12, vel=0.7, players=3)
    ostinato(22, "E", 0.55, steps=range(0, 14))
    kick_at(22, (0,), 0.9)
    big_at(22, (0,), 0.8)
    kick_at(22, (8, 10, 12, 13), 0.85)
    stomp_at(22, (8, 9, 10, 11, 12, 13), 0.9)
    toms_tresillo(22, 0.85, fill=True)
    bass_line(22, [(0, 6, 0, 0.9), (8, 1, 0, 0.8), (10, 1, 0, 0.85), (12, 1, 0, 0.9), (13, 1, 0, 1.0)], E1, 0.9)
    T["snare"].add(I.snare_roll(6 * S16, 0.15, 1.0, rate=1 / S16 * 2, kit_hits=kits()["snare"]), t_of(22, 8))
    ratchet_build(22, 4, 10, 0.8)
    hit("fx", "gong_scrape", t_of(21, 8), 0.35, 0.0)
    gap(22, 14, 16)
    accent(t_of(22, 0), "piper_alone", "The Piper alone: call head", 0.7)
    accent(t_of(22, 8), "build", "Kick/stomp 16ths, tom fill, ratchet, snare roll -> silence", 0.9)

    # ================================================================ 40.6-56.5 s  FINAL HYPNOTIC DROP
    section(23, "final_drop", "Strongest section: flute + fiddle unison + soprano octave (+ low fiddle in the second "
                              "pass), kick + big drum, sub bass, toms, son-clave claves, woodblock clockwork, cajon, "
                              "tambourine, psaltery ostinato and chops, buzzing hurdy-gurdy counter-line; the second "
                              "pass loses its pause and ends in a stutter, then everything stops for the Piper.")
    drone_plan.append((t_of(23, 0), t_of(32, 0), [A3 - 12, E4 - 12, A3], 1.0, 0.02, 0.1))
    seq = [(23, CALL1, "A", A1, "call"), (24, GIGGLE, "F", F1, "giggle"), (25, CALL2, "A", A1, "call"),
           (26, CAD_OPEN, ("F", "E"), (F1, E1), "cad"), (27, CALL1_ORN, "A", A1, "call"),
           (28, CALL1, "F", F1, "obsess"), (29, CALL2, "A", A1, "call"), (30, CAD_CLOSED, ("F", "E"), (F1, E1), "cad"),
           (31, OBSESS, "A", A1, "stutter")]
    for bar, mel, ch, root, kind in seq:
        second = bar >= 27
        mel2 = [(s, l, m, ("trillhang" if o == "hang" and second else o)) for s, l, m, *rest in mel
                for o in [rest[0] if rest else ""]]
        play_flute(bar, mel2, 1.1, double8=(0.42 if second else 0.34), ghost=0.15, legato=0.86)
        fiddle_line(bar, mel, trk="fiddle", vel=0.85, pan=0.3)
        if second:
            fiddle_line(bar, mel, trk="fiddle_lo", tr=-12, vel=0.7, pan=-0.35)
        if kind == "giggle":
            pizz_echo(bar, mel, 3, 0.6)
            kick_at(bar, (8, 12), 1.0)
            answer(bar, ch, vel=1.0)
            bass_line(bar, [(6, 1, 0, 0.9), (7, 1, 12, 0.7), (10, 1, 0, 0.95), (11, 1, 0, 0.75), (14, 1, 0, 0.9),
                            (15, 1, 12, 0.75)], root, 1.0, sub_vel=0.9)
            clap_at(bar, (12, 14), 0.9, solo=True); snare_at(bar, (12,), 0.7)
            tamb_16(bar, 0.5); strings_chop(bar, ch, 0.8, steps=(10, 14)); chien_bar(bar, 0.9, steps=(10, 14))
            shaker_16(bar, 0.55, steps=range(8, 16))
            stomp_at(bar, (8,), 1.0)
            accent(t_of(bar, 0), "band_answer", "Band answers the pause (bigger)", 0.9)
        else:
            kick_at(bar, (0, 4, 8, 12), 1.0)
            big_at(bar, (0,), 0.9 if bar in (23, 27) else 0.6)
            pat = B_OBSESS if kind == "stutter" else (B_ROLL if bar in (26, 30) else (B_GALLOP if bar % 2 else B_GALLOP2))
            bass_line(bar, pat, root, 1.0, sub_vel=0.9)
            stomp_at(bar, (0, 3, 8, 11) if not second else (0, 3, 6, 8, 11, 14), 1.0)
            clap_at(bar, (4, 12) if not second else (4, 10, 12, 14), 0.9, solo=True)
            snare_at(bar, (4, 12), 0.7)
            toms_tresillo(bar, 0.85, fill=(bar in (26, 30)))
            claves_at(bar, vel=0.55 if not second else 0.7)
            cajon_groove(bar, 0.8)
            tamb_16(bar, 0.7)
            strings_chop(bar, ch, 0.9)
            chien_bar(bar, 1.0, steps=(2, 6, 10, 14) if not second else (2, 3, 6, 10, 11, 14))
            shaker_16(bar, 0.55)
            if second:
                woodtick(bar, (1, 5, 9, 13), 0.7)
            if kind == "obsess":
                answer(bar, "F", steps=((14, 2),), vel=0.8, big=False)
                accent(t_of(bar, 0), "obsession", "No pause anymore: the call repeats where the giggle was", 0.9)
            if kind == "stutter":
                for s in (0, 4, 8, 12):
                    answer(bar, "A", steps=((s, 1),), vel=0.75, big=(s == 0))
                accent(t_of(bar, 0), "stutter", "Obsessive stutter bar: 16th bass, band stabs on every beat", 1.0)
        ostinato(bar, ch if kind != "stutter" else "A", 0.5 if not second else 0.65,
                 steps=range(16) if kind != "giggle" else range(8, 16))
        darb_maqsum(bar, 0.7, fill=(bar in (26, 30, 31)))
        if bar % 2 == 1:
            hit("fx", "anvil", t_of(bar, 14), 0.3, 0.65)
        accent(t_of(bar, 0), "downbeat", f"bar {bar + 1}", 0.5)
    # fiddle-section harmony (replaces V1's choir pads)
    pads = {"A": [A3, E4, C5], "F": [F4 - 12, C4 + 12 - 12, A4], "E": [E4 - 12, B3, Ab4]}
    for bar, mel, ch, root, kind in seq:
        if kind == "stutter":
            continue
        if isinstance(ch, tuple):
            fsec_chord(bar, 0, pads[ch[0]], 8, vel=0.5); fsec_chord(bar, 8, pads[ch[1]], 8, vel=0.5)
        else:
            fsec_chord(bar, 0 if kind != "giggle" else 6, pads[ch], 16 if kind != "giggle" else 10, vel=0.5)
    T["bowpad"].add(I.psaltery(E5 + 12, BAR * 4 - 0.1, 0.35, art="bow"), t_of(27, 0), 1.0, 0.6)   # high eerie E6
    T["bowpad"].add(I.psaltery(Bb5, BAR * 2 - 0.1, 0.28, art="bow"), t_of(29, 0), 1.0, -0.6)    # and its Bb rub
    gm(23, [(0, 8, E5), (8, 8, A4)]); gm(24, [(6, 10, C5)]); gm(25, [(0, 8, E5), (8, 4, Ab4), (12, 4, B4)])
    gm(26, [(0, 8, C5), (8, 8, B4)]); gm(27, [(0, 6, A4), (6, 2, C5), (8, 8, E5)]); gm(28, [(0, 8, F5), (8, 8, E5)])
    gm(29, [(0, 8, E5), (8, 4, Ab4), (12, 4, B4)]); gm(30, [(0, 8, C5), (8, 4, B4), (12, 4, A4)])
    gm(31, [(0, 2, A4), (2, 2, E5), (4, 2, A4), (6, 2, E5), (8, 2, A4), (10, 2, Eb5)])
    boom(t_of(23, 0), 1.0)
    bell_at(t_of(23, 0), "A", 0.9, pan=-0.55); bell_at(t_of(23, 0) + 0.01, "E", 0.5, pan=0.6)
    bell_at(t_of(27, 0), "A", 0.6, pan=0.5)
    gap(26, 15, 16)
    gap(31, 12, 16)
    play_flute(31, [(13, 1, E5), (14, 1, Eb5), (15, 1, E5)], 0.6, ghost=0.7)     # the Piper alone in the gap
    accent(t_of(23, 0), "drop", "FINAL DROP downbeat", 1.0)
    accent(t_of(27, 0), "variation", "Second pass: flute trills, low fiddle, doubled stomps/claps, woodblock "
                                     "clockwork, high bowed E6", 0.8)

    # ================================================================ 56.5-65.3 s  THE DISAPPEARANCE
    section(32, "disappearance", "Layers vanish bar by bar while the pulse keeps walking; the flute is left alone with a "
                                 "high bowed A and a wooden heartbeat; its last giggle and G#4 pickup lead straight back "
                                 "into the opening (loop).")
    play_flute(32, CALL1, 1.0, ghost=0.3)
    fiddle_line(32, CALL1, trk="fiddle", tr=-12, vel=0.45, pan=-0.3)
    kick_at(32, (0, 4, 8, 12), 0.95)
    big_at(32, (0,), 0.8)
    bass_line(32, B_GALLOP, A1, 0.9, sub_vel=0.7)
    stomp_at(32, (0, 8), 0.9); clap_at(32, (4, 12), 0.75)
    toms_tresillo(32, 0.6)
    tamb_8ths(32, 0.55); shaker_16(32, 0.45); darb_maqsum(32, 0.5)
    ostinato(32, "A", 0.35)
    bell_at(t_of(32, 0), "A", 0.55, pan=-0.6)
    accent(t_of(32, 0), "disappearance", "Gurdy, strings, octave flute gone", 0.8)
    play_flute(33, GIGGLE, 0.95, ghost=0.4)
    pizz_echo(33, GIGGLE, 3, 0.4, pan=-0.65)
    kick_at(33, (0, 4, 8, 12), 0.8, lowpass=1000)
    stomp_at(33, (0, 8), 0.85); clap_at(33, (4, 12), 0.6)
    toms_tresillo(33, 0.45)
    tamb_8ths(33, 0.45); shaker_16(33, 0.35, steps=(2, 6, 10, 14))
    ostinato(33, "F", 0.25)
    accent(t_of(33, 0), "bass_out", "Bass gone; kick filtered; giggle echoed", 0.6)
    play_flute(34, CALL2, 0.95, ghost=0.4)
    stomp_at(34, (0, 8), 0.8); clap_at(34, (4, 12), 0.5)
    slit_at(34, [(0, "lo"), (3, "hi"), (6, "hi"), (8, "lo"), (11, "hi"), (14, "hi")], 0.5)
    ostinato(34, "A", 0.18, steps=range(0, 16, 2))
    accent(t_of(34, 0), "kick_out", "Kick gone; stomps, claps and the wooden heartbeat", 0.6)
    play_flute(35, CAD_CLOSED, 0.95, ghost=0.5)
    stomp_at(35, (0, 8), 0.65)
    slit_at(35, [(0, "lo"), (3, "hi"), (6, "hi"), (8, "lo")], 0.45)
    T["bowpad"].add(I.psaltery(A5 + 12 - 12, BAR * 2.2, 0.32, art="bow"), t_of(35, 0), 1.0, 0.4)
    accent(t_of(35, 0), "thin", "Stomps and slit drum only; a high bowed A hangs in the air", 0.5)
    play_flute(36, LAST, 0.9, ghost=0.6)
    slit_at(36, [(0, "lo"), (8, "lo"), (11, "hi"), (14, "hi")], 0.45)
    claves_at(36, (2, 3), 0.4)
    drone_plan.append((t_of(32, 0), t_of(37, 0), [A3 - 12, E4 - 12], 0.45, 0.05, 2.5))
    accent(t_of(36, 6), "flute_alone", "The flute alone: last giggle", 0.6)
    accent(t_of(36, 14), "loop_pickup", "G#4 pickup resolves into the A4 + drum at 0.000 s (seamless loop)", 0.8)

    render_gurdy(drone_plan, gurdy_mel, chien, None)
    return T
