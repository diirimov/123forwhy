"""
FOLLOW THE PIPER -- score and arrangement.

136 BPM, 4/4, 37 bars (65.294 s), A minor / harmonic minor with the Piper's tritone (D#).

The hook (alto recorder) is four bars on the 16th grid:
  CALL1    A4 . . E5 . . A5 . G#5 A5 E5 . D#5 - - -      tresillo rise, hangs on the tritone
  GIGGLE   (pause ...........) E6 . E6 . B5 -            the Piper's laugh; the crowd answers in the gap
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


NAMES = ["flute", "flute8", "flute_lo", "ghost", "gurdy", "drone", "chien", "strings", "bowpad", "pluck",
         "bass", "kick", "stomp", "clap", "snare", "tamb", "shaker", "darb", "frame", "boom",
         "bells", "choir", "chant", "hum", "breath", "laugh", "fx"]
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


def choir_chord(bar, step, midis, dur_steps, vowels=(("a", 0.0),), amp=1.0, voices_per=3, attack=0.25,
                release=0.5, trk="choir", swell=0.0, gliss=None, breath=0.2):
    x = I.choir(midis, dur_steps * S16, vowel_seq=vowels, voices_per=voices_per, amp=amp, attack=attack,
                release=release, swell=swell, gliss=gliss, breath=breath)
    T[trk].add(x, t_of(bar, step), 1.0)


def chant_answer(bar, sylls, amp=1.0, roots=(A3, E4, A4)):
    """sylls: [(step, len, syllable, interval_index_shift)] -- sung on root/fifth/octave"""
    total = 16 * S16
    out = None
    for ki, kind in enumerate(("bar", "ten", "alt")):
        sy = [(s * S16, l * S16, roots[ki] + 12 * (kind == "bar"), syl) for s, l, syl in sylls]
        x = I.chant(sy, total, kinds=(kind,), voices_per=3, amp=amp)
        out = x if out is None else out[:len(x)] + x[:len(out)]
    T["chant"].add(out, t_of(bar, 0), 1.0)
    EVENTS["chant"] += [t_of(bar, s) for s, l, syl in sylls]


def hum_line(bar, notes, amp=1.0, tr=-12):
    nn = [(s * S16, l * S16 * 0.95, m + tr) for s, l, m, *_ in notes]
    total = max(s + l for s, l, *_ in notes) * S16
    x = I.hum(nn, total, kinds=("bar", "ten", "alt"), voices_per=2, amp=amp)
    T["hum"].add(x, t_of(bar, 0), 1.0)


def breath_in(bar, step, dur_steps=3, amp=1.0, people=7):
    x = I.breath(dur_steps * S16, people=people, inhale=True, amp=amp)
    T["breath"].add(x, t_of(bar, step), 1.0)
    EVENTS["breath_in"].append(t_of(bar, step))


def breath_out(bar, step, amp=1.0, people=7, dur=0.18):
    x = I.breath(dur, people=people, inhale=False, amp=amp)
    T["breath"].add(x, t_of(bar, step) + 0.005, 1.0)


def laugh_at(t, amp=1.0, pan=0.5, kind="child", n_ha=6, f0=(360, 270)):
    x = I.laugh(n_ha=n_ha, f_start=f0[0], f_end=f0[1], kind=kind, amp=amp)
    T["laugh"].add(x, t, 1.0, pan)
    EVENTS["laugh"].append(t)


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


# =========================================================================== ARRANGEMENT
def arrange():
    reset()
    kits()
    gurdy_mel = []      # (t, dur, midi, vel)
    chien = []          # (t, vel)
    drone_plan = []

    def gm(bar, notes, vel=0.9, tr=0):
        for s, l, m in notes:
            gurdy_mel.append((t_of(bar, s), l * S16 * 0.98, m + tr, vel))

    def chien_bar(bar, vel=1.0, steps=(2, 6, 10, 14)):
        for s in steps:
            chien.append((t_of(bar, s), vel * (0.85 if s in (2, 10) else 0.7)))

    # ---------------------------------------------------------------- 0-3.5 s  INTRO: the hook, alone
    section(0, "intro_hook", "The Piper's call, alone over a breathing A drone and a heartbeat frame drum. "
                             "Narration space in the bar-2 pause.")
    play_flute(0, CALL1, 1.0, ghost=0.35)
    play_flute(1, GIGGLE, 0.95, ghost=0.45)
    bell_at(t_of(0, 0), "A", 0.55, pan=-0.6)
    drone_plan.append((0.0, t_of(2, 0) + 0.3, [A3 - 12, E4 - 12], 0.35, 0.9, 0.3))
    for b in (0, 1):
        frame_at(b, (0, 8), 0.4, "frame_hand")
    accent(0.0, "hook", "Flute hook starts at 0.000 s (A4)")
    accent(t_of(0, 12), "hook", "Tritone D#5 hang -- the Piper's signature note")
    accent(t_of(1, 6), "flute_giggle", "Flute 'giggle' E6 E6 B5", 0.6)

    # ---------------------------------------------------------------- 3.5-12.4 s  THE RATS AWAKEN
    section(2, "rats_awaken", "Stomps, claps, plucked strumstick, shaker; bass arrives, then kick and darbuka. "
                              "The hook completes its first full statement.")
    drone_plan.append((t_of(2, 0), t_of(14, 0), [A3 - 12, E4 - 12], 0.8, 0.4, 0.2))
    # bar 2: CALL2
    play_flute(2, CALL2, 1.0, ghost=0.25)
    stomp_at(2, (0, 8), 0.8); clap_at(2, (4, 12), 0.55)
    pluck_arp(2, "A", 0.8)
    play_bass(2, B_PRE, A1, 0.75, bright=0.6)
    shaker_16(2, 0.35, steps=(2, 6, 10, 14))
    accent(t_of(2, 0), "groove_in", "Stomps + claps + strumstick + bass enter")
    # bar 3: CAD_OPEN  F -> E
    play_flute(3, CAD_OPEN, 1.0)
    stomp_at(3, (0, 8), 0.85); clap_at(3, (4, 12), 0.6)
    pluck_arp(3, ("F", "E"), 0.8)
    play_bass(3, B_PRE, (F1, E1), 0.75, bright=0.6)
    shaker_16(3, 0.4)
    tamb_8ths(3, 0.45)
    # bar 4: CALL1 -- kick + darbuka
    play_flute(4, CALL1_ORN, 1.0)
    kick_at(4, (0, 4, 8, 12), 0.7, lowpass=900)
    stomp_at(4, (0, 8), 0.8); clap_at(4, (4, 12), 0.6)
    darb_maqsum(4, 0.55)
    pluck_arp(4, "A", 0.75)
    play_bass(4, B_PRE2, A1, 0.85, bright=0.8)
    shaker_16(4, 0.45); tamb_8ths(4, 0.5)
    accent(t_of(4, 0), "kick_in", "Kick (filtered) and darbuka enter")
    # bar 5: GIGGLE with the first crowd answer
    play_flute(5, GIGGLE, 1.0, ghost=0.3)
    kick_at(5, (0, 4, 8, 12), 0.75, lowpass=1300)
    stomp_at(5, (0, 8), 0.8); clap_at(5, (4, 12), 0.6)
    chant_answer(5, [(0, 2, "hu"), (3, 2, "ha")], amp=0.55)
    darb_maqsum(5, 0.6)
    strings_chop(5, "F", 0.55)
    play_bass(5, B_PRE2, F1, 0.85, bright=0.8)
    shaker_16(5, 0.5); tamb_8ths(5, 0.55)
    accent(t_of(5, 0), "crowd_answer", "First wordless crowd answer 'hu-HA' in the hook's pause")
    # bar 6: BUILD -- CALL2 cut off at beat 3, roll, inhale, 1-16th silence
    play_flute(6, CALL2[:4], 1.05)
    play_flute(6, [(8, 1, B5), (9, 1, C6), (10, 1, B5), (11, 1, C6), (12, 1, B5), (13, 1, C6)], 0.85, legato=0.8)
    kick_at(6, (0, 4, 8, 10, 12, 13, 14), 0.8, lowpass=2500)
    stomp_at(6, (0, 4, 8, 10, 12, 14), 0.85)
    T["snare"].add(I.snare_roll(6 * S16, 0.15, 0.85, rate=1 / S16 * 2, kit_hits=kits()["snare"]), t_of(6, 8))
    play_bass(6, [(0, 3, 0, 1.0), (6, 1, 12, 0.7), (8, 1, 0, 0.8), (10, 1, 0, 0.85), (12, 1, 0, 0.9), (14, 1, 0, 1.0)], A1, 0.85)
    breath_in(6, 12, 3.4, 0.9)
    darb_maqsum(6, 0.6, fill=True)
    strings_chop(6, "A", 0.6, steps=(2, 6))
    hit("fx", "gong_scrape", t_of(6, 0), 0.25, 0.0)
    accent(t_of(6, 8), "build", "Snare roll + crowd inhale into the drop")

    # ---------------------------------------------------------------- 12.4-24.7 s  FIRST DROP
    section(7, "first_drop", "The whole town dances: kick, galloping 'rat-run' bass, claps + rope snare, stomps, "
                             "tambourine, darbuka, psaltery chops, buzzing hurdy-gurdy, soprano octave.")
    seq = [(7, CALL1, "A", A1, "call"), (8, GIGGLE, "F", F1, "giggle"), (9, CALL2, "A", A1, "call"),
           (10, CAD_OPEN, ("F", "E"), (F1, E1), "cad"), (11, CALL1_ORN, "A", A1, "call"),
           (12, GIGGLE_CHAT, "F", F1, "giggle"), (13, CALL2, "A", A1, "call")]
    for bar, mel, ch, root, kind in seq:
        lvl = 0.92 if bar < 11 else 1.0
        play_flute(bar, mel, 1.05, double8=(0.28 if bar >= 11 else 0.0), ghost=0.12)
        if kind == "giggle":
            kick_at(bar, (0, 8, 12), 1.0)
            play_bass(bar, B_STOP, root, 1.0)
            stomp_at(bar, (0,), 1.0)
            clap_at(bar, (12,), 0.85, solo=True); snare_at(bar, (12,), 0.6)
            chant_answer(bar, [(0, 2, "hu"), (3, 2, "ha")] if bar == 8 else [(0, 2, "ho"), (3, 2, "ha")], amp=0.8)
            tamb_8ths(bar, 0.7, steps=(10, 14))
            strings_chop(bar, ch, 0.75, steps=(6, 10, 14))
            chien_bar(bar, 0.8, steps=(6, 10, 14))
            shaker_16(bar, 0.55, steps=range(6, 16))
            accent(t_of(bar, 1), "stop", "Band stop: the pause in the hook, crowd chant answers", 0.8)
        else:
            kick_at(bar, (0, 4, 8, 12), 1.0)
            play_bass(bar, B_GALLOP if bar % 2 else B_GALLOP2, root, 1.0)
            stomp_at(bar, (0, 8) if bar < 11 else (0, 3, 8), 0.95)
            clap_at(bar, (4, 12), 0.85, solo=(bar >= 11)); snare_at(bar, (4, 12), 0.6)
            tamb_16(bar, 0.6 * lvl)
            strings_chop(bar, ch, 0.65 if bar < 11 else 0.8)
            chien_bar(bar, 1.0)
            shaker_16(bar, 0.5)
        darb_maqsum(bar, 0.65, fill=(bar in (10, 13)))
        if bar in (9, 13):
            frame_at(bar, (0, 6, 8, 14), 0.7, "frame_open")
    gm(9, [(0, 8, E4), (8, 8, A4)]); gm(10, [(0, 8, A4), (8, 8, Ab4)])
    gm(11, [(0, 8, E5 - 12), (8, 8, A4)]); gm(12, [(6, 10, C5)]); gm(13, [(0, 8, E5), (8, 4, Ab5 - 12), (12, 4, B4)])
    boom(t_of(7, 0), 1.0); hit("boom", "bd2", t_of(7, 0), 0.8)
    bell_at(t_of(7, 0), "A", 0.8, pan=0.55)
    breath_out(7, 0, 0.8)
    accent(t_of(7, 0), "drop", "FIRST DROP downbeat", 1.0)
    for b in range(7, 14):
        accent(t_of(b, 0), "downbeat", f"bar {b + 1}", 0.5)
    hit("fx", "anvil", t_of(11, 0), 0.35, 0.6)
    accent(t_of(11, 0), "variation", "Ornamented hook + tresillo stomps + solo claps", 0.6)
    choir_chord(13, 0, [A3, E4, A4, C5], 16, (("a", 0), ("o", 0.7)), amp=0.55, attack=0.6, swell=0.6)

    # ---------------------------------------------------------------- 24.7-31.8 s  THE BETRAYAL
    section(14, "betrayal", "The expected cadence turns: Bb (bII) then Eb (tritone) under an A drone that refuses "
                            "to move. Half-time, a stop with only stomps, laughter in the dark; groove re-ignites on E.")
    # bar 14: Bb
    play_flute(14, BETRAY_FL, 1.0, ghost=0.4)
    kick_at(14, (0, 4, 8, 12), 1.0)
    play_bass(14, B_GALLOP, Bb1, 1.0)
    stomp_at(14, (0, 8), 0.9)
    strings_chop(14, "Bb", 0.7)
    tamb_8ths(14, 0.6)
    darb_maqsum(14, 0.55)
    hit("boom", "gong", t_of(14, 0), 0.55, 0.0)
    bell_at(t_of(14, 0), "Bb", 0.6, pan=-0.5)
    choir_chord(14, 0, [Bb4 - 12, D4, F4, A4], 16, (("o", 0), ("u", 0.6)), amp=0.6, attack=0.5, swell=0.5)
    accent(t_of(14, 0), "betrayal", "Harmony betrays: Bb under the hook, gong", 1.0)
    # bar 15: Eb (tritone), half-time
    play_flute(15, [(0, 6, Eb4, "hangdark"), (6, 2, E4), (8, 8, Eb4, "hangdark")], 0.9, which="tenor", trk="flute_lo",
               dark=True)
    kick_at(15, (0, 8), 1.0)
    play_bass(15, B_HALF, Eb2, 0.95)
    stomp_at(15, (0, 4, 8, 12), 0.9)
    clap_at(15, (12,), 0.6)
    choir_chord(15, 0, [Eb4 - 12, A3, Bb4 - 12, Eb4], 16, (("u", 0), ("o", 0.5)), amp=0.65, attack=0.3, swell=0.3)
    shaker_16(15, 0.35, steps=(2, 6, 10, 14))
    laugh_at(t_of(15, 11), 0.5, pan=0.65, n_ha=5, f0=(380, 290))
    accent(t_of(15, 0), "half_time", "Half-time on the tritone Eb, low tenor recorder", 0.8)
    accent(t_of(15, 11), "laugh", "Distant breathy laughter", 0.4)
    # bar 16: the rhythmic pause
    kick_at(16, (0,), 1.0)
    play_bass(16, B_HIT, Eb2, 1.0)
    boom(t_of(16, 0), 0.9)
    chant_answer(16, [(0, 2, "ha")], amp=0.9, roots=(Eb4 - 12, A3, Eb4))
    stomp_at(16, (4, 8, 12), 0.75)
    play_flute(16, [(10, 1, E6, "laugh"), (12, 1, E6, "laugh")], 0.55, ghost=0.8)
    breath_in(16, 13, 3, 0.7)
    accent(t_of(16, 0), "hit", "Unison hit, then the rhythmic pause (only stomps)", 0.9)
    accent(t_of(16, 2), "pause", "Silence except stomps", 0.7)
    # bar 17: groove re-ignites on E (dominant)
    kick_at(17, (0, 4, 8, 12), 0.95, lowpass=1500)
    play_bass(17, B_GALLOP, E1, 0.9)
    stomp_at(17, (0, 8), 0.9)
    tamb_16(17, 0.55)
    T["tamb"].add(kits()["tamb_roll"][0][:int(BAR * SR)] * np.linspace(0.1, 0.6, int(BAR * SR))[:, None], t_of(17, 0), 1.0, 0.4)
    play_flute(17, [(8, 2, E4), (10, 2, F4), (12, 2, F4 + 1), (14, 1, G4), (15, 1, Ab4)], 0.95, which="tenor", trk="flute_lo")
    bell_at(t_of(17, 0), "E", 0.45, pan=0.6)
    darb_maqsum(17, 0.5, fill=True)
    accent(t_of(17, 0), "regroove", "Groove re-ignites on E; chromatic creep E-F-F#-G-G#", 0.7)

    # ---------------------------------------------------------------- 31.8-40.6 s  THE PIPER RETURNS
    section(18, "piper_returns", "The hook returns darker and stranger: breathy flute with a detuned ghost unison, "
                                 "minor-9th rub (A against Bb), humming crowd doubling the tune, wrong-note giggle "
                                 "answered by laughter.")
    drone_plan.append((t_of(14, 0), t_of(18, 0), [A3 - 12, E4 - 12], 0.7, 0.05, 0.1))
    drone_plan.append((t_of(18, 0), t_of(23, 0), [A3 - 12, E4 - 12, Bb4 - 24], 0.85, 0.05, 0.05))
    ret = [(18, CALL1, A1), (19, GIGGLE_DARK, F1), (20, CALL2, A1), (21, CAD_OPEN, (F1, E1))]
    for k, (bar, mel, root) in enumerate(ret):
        play_flute(bar, mel, 0.92, dark=True, ghost=0.3)
        play_flute(bar, mel, 0.38, which="tenor", trk="flute_lo", tr=0, detune=-28)
        kick_at(bar, (0, 4, 8, 12), 0.9, lowpass=500 + 500 * k)
        play_bass(bar, B_LONG, root, 0.9, bright=0.5)
        stomp_at(bar, (0, 8), 0.75)
        shaker_16(bar, 0.4)
        frame_at(bar, (0, 6, 10), 0.5, "frame_lo")
        if k >= 2:
            tamb_8ths(bar, 0.4)
    hum_line(18, CALL1, 0.6); hum_line(20, CALL2, 0.62); hum_line(21, CAD_OPEN, 0.65)
    # psaltery high bowed rub A5 / Bb5
    for bar in (18, 20):
        T["bowpad"].add(I.psaltery(A5, BAR * 2 - 0.1, 0.5, art="bow"), t_of(bar, 0), 1.0, -0.6)
        T["bowpad"].add(I.psaltery(Bb5, BAR * 2 - 0.1, 0.42, art="bow"), t_of(bar, 2), 1.0, 0.6)
    choir_chord(18, 0, [A3, Bb4 - 12, E4], 32, (("u", 0), ("o", 0.5)), amp=0.4, attack=0.8, swell=0.4)
    choir_chord(20, 0, [A3, Bb4 - 12, E4, Ab4], 32, (("o", 0), ("u", 0.7)), amp=0.45, attack=0.6)
    laugh_at(t_of(19, 0) + 0.02, 0.7, pan=-0.55, n_ha=6, f0=(400, 300))
    laugh_at(t_of(19, 1) + 0.03, 0.4, pan=0.7, n_ha=5, f0=(330, 260), kind="alt")
    bell_at(t_of(18, 0), "A", 0.7, pan=-0.4)
    bell_at(t_of(18, 8), "A+", 0.45, pan=0.5)          # second toll a semitone sharp: wrong
    gm(20, [(0, 16, A4)], 0.6); gm(21, [(0, 8, A4), (8, 8, Ab4)], 0.7)
    accent(t_of(18, 0), "return", "The Piper returns (darker hook)", 1.0)
    accent(t_of(19, 10), "wrong_note", "Giggle lands on Bb5 instead of B5, bends down", 0.7)
    accent(t_of(19, 0), "laugh", "Children's breathy laughter answers the giggle", 0.6)
    # bar 22: BUILD 2 -- the Piper alone, then everything rushes in
    play_flute(22, [(0, 3, A4, "acc"), (3, 3, E5), (6, 2, A5)], 1.0, ghost=0.6)
    play_flute(22, [(8, 1, A4), (9, 1, E5), (10, 1, A5), (11, 1, E5), (12, 1, A5), (13, 1, Ab5), (14, 1, A5), (15, 1, B5)],
               0.95, legato=0.85)
    kick_at(22, (0,), 0.9)
    kick_at(22, (8, 10, 12, 13, 14, 15), 0.85)
    stomp_at(22, (8, 9, 10, 11, 12, 13, 14, 15), 0.9)
    play_bass(22, [(0, 6, 0, 0.9), (8, 1, 0, 0.8), (10, 1, 0, 0.85), (12, 1, 0, 0.9), (13, 1, 0, 0.9), (14, 1, 0, 1.0),
                   (15, 1, 12, 0.9)], E1, 0.9)
    T["snare"].add(I.snare_roll(8 * S16, 0.15, 1.0, rate=1 / S16 * 2, kit_hits=kits()["snare"]), t_of(22, 8))
    breath_in(22, 12, 4, 1.1, people=9)
    hit("fx", "gong_scrape", t_of(21, 8), 0.4, 0.0)
    accent(t_of(22, 0), "piper_alone", "The Piper alone: call head", 0.7)
    accent(t_of(22, 8), "build", "Stomps/kick 16ths, snare roll, crowd inhale", 0.9)

    # ---------------------------------------------------------------- 40.6-56.5 s  FINAL HYPNOTIC DROP
    section(23, "final_drop", "Strongest section: hook + soprano octave + hurdy-gurdy counter-line, chanting crowd, "
                              "choir, panting breaths, anvil sparks; second pass loses its pauses (obsession), "
                              "then a stuttering extra bar.")
    drone_plan.append((t_of(23, 0), t_of(32, 0), [A3 - 12, E4 - 12, A3], 1.0, 0.02, 0.1))
    seq = [(23, CALL1, "A", A1, "call"), (24, GIGGLE, "F", F1, "giggle"), (25, CALL2, "A", A1, "call"),
           (26, CAD_OPEN, ("F", "E"), (F1, E1), "cad"), (27, CALL1_ORN, "A", A1, "call"),
           (28, CALL1, "F", F1, "obsess"), (29, CALL2, "A", A1, "call"), (30, CAD_CLOSED, ("F", "E"), (F1, E1), "cad"),
           (31, OBSESS, "A", A1, "stutter")]
    for bar, mel, ch, root, kind in seq:
        second = bar >= 27
        play_flute(bar, mel, 1.1, double8=(0.42 if second else 0.34), ghost=0.15)
        if kind == "giggle":
            kick_at(bar, (0, 8, 12), 1.0)
            play_bass(bar, B_STOP, root, 1.0)
            stomp_at(bar, (0,), 1.0)
            chant_answer(bar, [(0, 2, "hu"), (3, 2, "ha")], amp=1.0)
            clap_at(bar, (12, 14), 0.9, solo=True); snare_at(bar, (12,), 0.7)
            tamb_16(bar, 0.5); strings_chop(bar, ch, 0.8, steps=(6, 10, 14)); chien_bar(bar, 0.9, steps=(6, 10, 14))
            shaker_16(bar, 0.55, steps=range(6, 16))
            accent(t_of(bar, 1), "stop", "Band stop + big crowd answer", 0.9)
        else:
            kick_at(bar, (0, 4, 8, 12), 1.0)
            pat = B_OBSESS if kind == "stutter" else (B_GALLOP if bar % 2 else B_GALLOP2)
            play_bass(bar, pat, root, 1.0)
            stomp_at(bar, (0, 3, 8, 11) if not second else (0, 3, 6, 8, 11, 14), 1.0)
            clap_at(bar, (4, 12) if not second else (4, 10, 12, 14), 0.9, solo=True)
            snare_at(bar, (4, 12), 0.7)
            tamb_16(bar, 0.7)
            strings_chop(bar, ch, 0.9)
            chien_bar(bar, 1.0, steps=(2, 6, 10, 14) if not second else (2, 3, 6, 10, 11, 14))
            shaker_16(bar, 0.55)
            if kind == "obsess":
                chant_answer(bar, [(0, 2, "hu"), (3, 2, "ha"), (6, 2, "hu"), (8, 1, "ha")], amp=0.75)
                accent(t_of(bar, 0), "obsession", "No pause anymore: the call repeats where the giggle was", 0.9)
            if kind == "stutter":
                chant_answer(bar, [(0, 1, "ha"), (4, 1, "ha"), (8, 1, "ha"), (12, 1, "ha")], amp=0.9)
                kick_at(bar, (14, 15), 0.8)
                accent(t_of(bar, 0), "stutter", "Obsessive stutter bar: 16th bass, 'HA' on every beat", 1.0)
        darb_maqsum(bar, 0.75, fill=(bar in (26, 30, 31)))
        if bar % 2 == 1:
            hit("fx", "anvil", t_of(bar, 14), 0.28, 0.65)
        if second and kind != "stutter":
            breath_out(bar, 6, 0.35, people=6, dur=0.08); breath_out(bar, 14, 0.4, people=6, dur=0.08)
        accent(t_of(bar, 0), "downbeat", f"bar {bar + 1}", 0.5)
    # choir pads follow harmony
    pads = {"A": [A3 - 12, E4 - 12, A3, C4, E4], "F": [F4 - 24, C4 - 12, A3, C4, F4], "E": [E4 - 24, B3 - 12, Ab4 - 12, B3, E4]}
    for bar, mel, ch, root, kind in seq:
        if isinstance(ch, tuple):
            choir_chord(bar, 0, pads[ch[0]], 8, (("a", 0),), amp=0.5, attack=0.15, release=0.2)
            choir_chord(bar, 8, pads[ch[1]], 8, (("a", 0), ("o", 0.5)), amp=0.5, attack=0.1, release=0.3)
        else:
            choir_chord(bar, 0, pads[ch], 16, (("a", 0), ("o", 0.6)), amp=0.5, attack=0.15, release=0.3)
    # eerie high harmonic choir in the second pass
    choir_chord(27, 0, [E5, A5 - 12 + 12], 64, (("i", 0), ("u", 0.5)), amp=0.32, attack=1.5, release=1.0, gliss=0.0,
                breath=0.35)
    # gurdy counter-line
    gm(23, [(0, 8, E5), (8, 8, A4)]); gm(24, [(6, 10, C5)]); gm(25, [(0, 8, E5), (8, 4, Ab4), (12, 4, B4)])
    gm(26, [(0, 8, C5), (8, 8, B4)]); gm(27, [(0, 6, A4), (6, 2, C5), (8, 8, E5)]); gm(28, [(0, 8, F5), (8, 8, E5)])
    gm(29, [(0, 8, E5), (8, 4, Ab4), (12, 4, B4)]); gm(30, [(0, 8, C5), (8, 4, B4), (12, 4, A4)])
    gm(31, [(0, 2, A4), (2, 2, E5), (4, 2, A4), (6, 2, E5), (8, 2, A4), (10, 2, Eb5), (12, 4, E5)])
    boom(t_of(23, 0), 1.0); hit("boom", "bd2", t_of(23, 0), 1.0)
    bell_at(t_of(23, 0), "A", 0.9, pan=-0.55); bell_at(t_of(23, 0) + 0.01, "E", 0.5, pan=0.6)
    bell_at(t_of(27, 0), "A", 0.6, pan=0.5)
    breath_out(23, 0, 1.0, people=9)
    accent(t_of(23, 0), "drop", "FINAL DROP downbeat", 1.0)
    accent(t_of(27, 0), "variation", "Second pass: stomps/claps double, panting breaths, high eerie choir", 0.8)
    laugh_at(t_of(31, 12), 0.45, pan=0.6, n_ha=4, f0=(420, 330))

    # ---------------------------------------------------------------- 56.5-65.3 s  THE DISAPPEARANCE
    section(32, "disappearance", "Layers vanish bar by bar while the pulse keeps walking; the flute is left alone, "
                                 "its last giggle and G#4 pickup lead straight back into the opening A4 (loop).")
    play_flute(32, CALL1, 1.0, ghost=0.3)
    kick_at(32, (0, 4, 8, 12), 0.95)
    play_bass(32, B_GALLOP, A1, 0.9)
    stomp_at(32, (0, 8), 0.9); clap_at(32, (4, 12), 0.75)
    tamb_8ths(32, 0.55); shaker_16(32, 0.45); darb_maqsum(32, 0.5)
    pluck_arp(32, "A", 0.6)
    bell_at(t_of(32, 0), "A", 0.55, pan=-0.6)
    accent(t_of(32, 0), "disappearance", "Choir, gurdy, strings and octave flute gone", 0.8)
    play_flute(33, GIGGLE, 0.95, ghost=0.4)
    kick_at(33, (0, 4, 8, 12), 0.8, lowpass=1200)
    stomp_at(33, (0, 8), 0.85); clap_at(33, (4, 12), 0.6)
    tamb_8ths(33, 0.45); shaker_16(33, 0.35, steps=(2, 6, 10, 14))
    laugh_at(t_of(33, 0) + 0.05, 0.45, pan=-0.7, n_ha=5, f0=(390, 300))
    accent(t_of(33, 0), "bass_out", "Bass gone; kick filtered; distant laugh", 0.6)
    play_flute(34, CALL2, 0.95, ghost=0.4)
    stomp_at(34, (0, 8), 0.8); clap_at(34, (4, 12), 0.5)
    shaker_16(34, 0.3, steps=(2, 6, 10, 14))
    hum_line(34, CALL2, 0.5)
    accent(t_of(34, 0), "kick_out", "Kick gone; only stomps, claps, humming", 0.6)
    play_flute(35, CAD_CLOSED, 0.95, ghost=0.5)
    stomp_at(35, (0, 8), 0.65)
    frame_at(35, (0, 8), 0.4, "frame_hand")
    hum_line(35, CAD_CLOSED, 0.38)
    accent(t_of(35, 0), "thin", "Stomps only, humming fades", 0.5)
    play_flute(36, LAST, 0.9, ghost=0.6)
    frame_at(36, (0, 8), 0.4, "frame_hand")
    drone_plan.append((t_of(32, 0), t_of(37, 0), [A3 - 12, E4 - 12], 0.45, 0.05, 2.5))
    accent(t_of(36, 6), "flute_alone", "The flute alone: last giggle", 0.6)
    accent(t_of(36, 14), "loop_pickup", "G#4 pickup resolves into the A4 at 0.000 s (seamless loop)", 0.8)

    # ---------------------------------------------------------------- hurdy-gurdy + chien render
    render_gurdy(drone_plan, gurdy_mel, chien, None)
    return T
