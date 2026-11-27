"""
THE PIED PIPER OF HAMELIN -- new original soundtrack: score and arrangement (100 % instrumental).

136 BPM, 4/4, 37 bars (65.294 s) -- the same bar grid as the finished film, so every cut still lands
on a bar line. B minor with a Phrygian bII (C) and a harmonic-minor V (F#).

THE HOOK ("the taunt") is written for the alto recorder. It's half a bar of skipping long-short rhythm
(2+1+2+1+2 sixteenths), sol-mi-la-sol-mi: the playground taunt every child knows, made the Piper's own.
    T1   A5 . F#5 B5 . A5 F#5 .       (B5 and A5 land on off-16ths: the skip)
The flute only ever plays HALF a bar. The other half belongs to someone else: plucked strings,
then the hurdy-gurdy and fiddle, then the whole band. The same innocent tune keeps playing while the
ground moves under it:
    over Bm  -> mysterious      over C (bII) -> F# becomes a #11 / tritone rub: creepy
    over D   -> genuinely happy (the celebration)
    in Dm/Bb -> the taunt turns minor (F, Bb): the betrayal
Harmony of the hook: | Bm | C | Bm | G  F# |  (the F# bar pulls straight back into the hook: it loops).

Methods reused from the Dancing Plague production (dp_engine.py): four-on-the-floor club kick with a
47 Hz bloom; deep plucked bass with octave "pops"; legato gliding growl bass in the drops; riq on the
offbeat 8ths; shaker 16ths with 0.95/0.5/0.3 accents; frame-drum bounce on 3/6/11/14; clap + tabor
backbeat; woodblocks on 3/11 in the drops; lute power-chord chops on the offbeats; tabor rolls with a
power-1.6 crescendo; filtered-noise risers + reverse cymbal; stop hits; 52 % 16th swing; drone with
buzz on the offbeats; sub-heavy, lean-low-mid mix.
New here: the sampled baroque recorders, the sampled psaltery and strumstick, the physical bowed-string
hurdy-gurdy and fiddle, and the acoustic VCSL drums layered under the club kick, clap and riq.

Notes are (step, len, midi[, opt]) with 16th steps from the bar start.
"""
import os, sys
import numpy as np
from collections import defaultdict
from scipy.ndimage import uniform_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "follow_the_piper", "source"))
import dsp as D                       # noqa: E402  (studio DSP + sample engine from FOLLOW THE PIPER)
from dsp import SR                    # noqa: E402
import instruments as I               # noqa: E402
import samples as S                   # noqa: E402
import dp_engine as E                 # noqa: E402  (Dancing Plague synth models)

BPM = 136.0
BEAT = 60.0 / BPM
S16 = BEAT / 4
BAR = 4 * BEAT
NBARS = 37
LENGTH = NBARS * BAR
TAIL = 4.0
N = int(round((LENGTH + TAIL) * SR))
NLOOP = int(round(LENGTH * SR))
SWING = 0.52                          # DP: 52 % 16th swing

# ------------------------------------------------------------------ pitches
(F1s, G1, A1, Bb1, B1, C2, Cs2, D2, E2, F2, Fs2, G2, A2, B2, C3) = (30, 31, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 45, 47, 48)
(F4, Fs4, G4, A4, Bb4, B4, C5, Cs5, D5, Eb5, E5, F5, Fs5, G5, A5, As5, Bb5, B5, C6, Cs6, D6, E6, Fs6, G6) = \
    (65, 66, 67, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 81, 82, 82, 83, 84, 85, 86, 88, 90, 91)
As4, Ds5, Cs4, Fs3, E4, D4 = 70, 75, 61, 54, 64, 62

# ------------------------------------------------------------------ themes
T1 = [(0, 2, A5, "acc"), (2, 1, Fs5), (3, 2, B5), (5, 1, A5), (6, 2, Fs5)]                  # the taunt
T1_HOLES = [(0, 2, A5, "acc"), (3, 2, B5), (6, 3, Fs5, "fall")]                                # children missing
T2 = [(0, 2, D6, "acc"), (2, 1, B5), (3, 2, E6), (5, 1, D6), (6, 1, B5), (7, 1, A5)]          # taunt up a 4th
CAD = [(0, 1, B5, "acc"), (1, 1, C6), (2, 1, B5), (3, 2, G5), (5, 1, A5), (6, 2, Fs5)]        # over G, F# anticipated
PU = [(14, 1, Fs5), (15, 1, G5)]                                                               # pickup (G = b9 over F#)
TM = [(0, 2, A5, "acc"), (2, 1, F5), (3, 2, Bb5), (5, 1, A5), (6, 2, F5)]                     # the taunt in minor
T_D = T1                                                                                       # over D: happy
T_G = [(0, 2, B5, "acc"), (2, 1, G5), (3, 2, C6), (5, 1, B5), (6, 2, G5)]
GATE = [(0, 2, G5, "acc"), (2, 1, E5), (3, 2, A5), (5, 1, G5), (6, 2, E5), (8, 6, Fs5, "trillhang")]
SPELL = [(0, 2, Fs5, "acc"), (2, 1, G5), (3, 1, As5), (4, 2, B5), (6, 1, Cs6), (7, 1, D6), (8, 4, Cs6, "trill"),
         (12, 2, As5)]
FA = [(8, 1, A5, "acc"), (10, 1, Fs5), (11, 2, B5), (13, 1, A5), (14, 2, Fs5)]                # flute answers the gurdy
SMILE = [(0, 2, Bb5, "acc"), (2, 1, A5), (3, 2, G5), (5, 1, F5), (6, 2, D5), (8, 6, Cs5, "hangdark")]
NIGHT = [(0, 1, A4, "acc"), (1, 1, Cs5), (2, 1, E5), (3, 1, F5), (4, 1, E5), (5, 1, Cs5), (6, 1, D5), (7, 1, E5),
         (8, 1, F5), (9, 1, G5), (10, 1, F5), (11, 1, E5), (12, 1, Cs5), (13, 1, A4)]
TAG = [(0, 1, As5, "acc"), (1, 1, B5), (2, 1, C6), (3, 1, Cs6), (4, 3, D6, "acc"), (7, 1, Cs6), (8, 2, As5),
       (10, 2, Fs5)]
STUT = [(0, 1, A5, "acc"), (3, 1, B5), (6, 1, Fs5), (10, 2, F5, "fallbig")]
LOW_CAD = [(0, 1, B4, "acc"), (1, 1, C5), (2, 2, B4), (4, 2, G4), (6, 6, Fs4, "hang")]       # tenor, in the fog
GIGGLE = [(0, 1, A5, "acc"), (2, 1, Fs5), (3, 2, B5, "fall")]

# plucked answers (psaltery + lute), second half of the bar
ANS1 = [(8, 1, Fs5), (9, 1, Fs5), (10, 1, D5), (12, 1, E5), (13, 1, D5), (14, 2, B4)]
ANS2 = [(8, 1, G5), (9, 1, G5), (10, 1, E5), (12, 1, Fs5), (13, 1, E5), (14, 2, C5)]
ANS3 = [(8, 1, Fs5), (9, 1, Fs5), (10, 1, D5), (11, 1, E5), (12, 1, Fs5), (13, 1, A5), (14, 2, B5)]
ANS4 = [(8, 1, As4), (9, 1, Cs5), (10, 1, Fs5), (11, 1, Cs5), (12, 1, As4), (13, 1, Cs5)]
ANS_EM = [(8, 1, G5), (9, 1, G5), (10, 1, E5), (11, 1, Fs5), (12, 1, G5), (13, 1, B5), (14, 2, D6)]
CEL_D = [(8, 1, D6), (9, 1, D6), (10, 1, A5), (12, 1, B5), (13, 1, A5), (14, 2, Fs5)]
CEL_G = [(8, 1, D6), (9, 1, C6), (10, 1, B5), (11, 1, A5), (12, 2, G5), (14, 1, A5), (15, 1, A5)]
# the rats: chromatic-neighbour 16th scurry (hurdy-gurdy + fiddle unison)
RAT_B = [(8, 1, Fs5), (9, 1, F5), (10, 1, Fs5), (11, 1, D5), (12, 1, Cs5), (13, 1, D5), (14, 1, B4), (15, 1, As4)]
RAT_C = [(8, 1, G5), (9, 1, Fs5), (10, 1, G5), (11, 1, E5), (12, 1, Ds5), (13, 1, E5), (14, 1, C5), (15, 1, B4)]
# hurdy-gurdy calls of the stranger's groove (the flute answers them)
GB = {"Em": [(0, 1, B4), (1, 1, B4), (2, 1, A4), (3, 2, B4), (5, 1, D5), (6, 2, C5)],
      "Bm": [(0, 1, Fs4), (1, 1, Fs4), (2, 1, E4), (3, 2, Fs4), (5, 1, A4), (6, 2, G4)],
      "C": [(0, 1, G4), (1, 1, G4), (2, 1, Fs4), (3, 2, G4), (5, 1, B4), (6, 2, A4)]}
SNEER1 = [(8, 2, D5), (10, 1, Cs5), (11, 1, D5), (12, 4, A4)]
SNEER2 = [(8, 2, D5), (10, 1, C5), (11, 1, D5), (12, 4, F4)]

# chords: bass root, chop voicing (power chords: DP's open fifths), drone
CH = {"Bm": (B1, [59, 66, 71]), "C": (C2, [60, 67, 72]), "G": (G1, [55, 62, 67]), "F#": (F1s, [54, 61, 66]),
      "Em": (E2, [52, 59, 64]), "D": (D2, [62, 66, 69]), "Dm": (D2, [62, 65, 69]), "Bb": (Bb1, [58, 62, 65]),
      "Gm": (G1, [55, 62, 67]), "A": (A1, [57, 61, 64]), "Gmaj": (G1, [59, 62, 67])}

# ------------------------------------------------------------------ grid
def t_of(bar, step=0.0):
    st = float(step)
    pair = np.floor(st / 2); r = st - 2 * pair
    frac = r * SWING if r <= 1 else SWING + (r - 1) * (1 - SWING)
    return bar * BAR + (pair + frac) * 2 * S16


def hum(sd=0.003):
    return float(np.clip(D.rng().normal(0, sd), -2.5 * sd, 2.5 * sd))


class Track:
    def __init__(self, name):
        self.name = name
        self.buf = np.zeros((N, 2))

    def add(self, x, t, gain=1.0, pan=0.0):
        if x.ndim == 1:
            x = D.pan(x, pan)
        elif pan:
            x = x * np.array([np.sqrt(1 - max(0, pan)), np.sqrt(1 + min(0, pan))])
        i = max(0, int(round(t * SR)))
        m = min(len(x), N - i)
        if m > 0:
            self.buf[i:i + m] += x[:m] * gain


NAMES = ["flute", "flute8", "flute_lo", "pluck", "lute", "gurdy", "drone", "chien", "fiddle", "fdesc", "fsec",
         "chop", "bass", "growl", "sub", "kick", "kick_ac", "clap", "tabor", "snare", "riq", "tamb", "shaker",
         "frame", "wood", "darb", "toms", "big", "boom", "cym", "fx", "bells"]
T = {}
SECTIONS, ACCENTS, KICKS, FLUTE_NOTES, GAPS = [], [], [], [], []
EVENTS = defaultdict(list)


def reset():
    T.clear(); SECTIONS.clear(); ACCENTS.clear(); KICKS.clear(); EVENTS.clear(); FLUTE_NOTES.clear(); GAPS.clear()
    D.reseed(1284); E.reseed(1284)
    for k in NAMES:
        T[k] = Track(k)


def section(bar, name, desc):
    SECTIONS.append(dict(bar=bar, name=name, desc=desc))


def accent(t, kind, desc, strength=1.0):
    ACCENTS.append(dict(time=round(float(t), 4), type=kind, description=desc, strength=strength))


def ev(kind, t):
    EVENTS[kind].append(round(float(t), 4))


def gap(bar, s0, s1=16):
    """full-band silence (everything but the flute and the reverb tails)"""
    GAPS.append((t_of(bar, s0) - 0.004, t_of(bar, s1) - 0.006))
    accent(t_of(bar, s0), "gap", "Full-band silence: only the Piper's flute (or nothing)", 0.9)


# ------------------------------------------------------------------ sample kits (VCSL, CC0)
KIT = {}


def kits():
    if KIT:
        return KIT
    P = "Membranophones/Struck Membranophones/"
    Q = "Idiophones/Struck Idiophones/"
    G = {
        "clap": Q + "Claps/Clap_rr*.wav", "solo": Q + "Claps/SoloClap_*.wav",
        "tamb_hit": Q + "Tambourine 1/Tamb1_Hit_*.wav", "tamb_shake": Q + "Tambourine 1/Tamb1_Shake_*.wav",
        "shaker": Q + "Shaker, Small/Mid_Shaker*Faster_*.wav",
        "darb_doum": P + "Darbuka/Darbuka_1_*.wav", "darb_tek": P + "Darbuka/Darbuka_3_*.wav",
        "darb_ka": P + "Darbuka/Darbuka_5_*.wav",
        "frame_lo": P + "Frame Drum/HDrumL_HitMuted_*.wav", "frame_open": P + "Frame Drum/HDrumL_Hit_*.wav",
        "snare": P + "Snare Drum, Rope Tension/Hi/RopeSnare_hi_sn_*.wav",
        "snare_lo": P + "Snare Drum, Rope Tension/Low/RopeSnare_low_sn_*.wav",
        "bd": P + "Bass Drum 1/BDrumNew_hit_v5*.wav",
        "big": P + "Bass Drum 3 - Legacy/bdrum_ff*.wav", "big_m": P + "Bass Drum 3 - Legacy/bdrum_muted_ff*.wav",
        "timp": P + "Timpani 1/Hit/Timpani1_Hit_v4*.wav", "gong": Q + "Gong 1/gong_f.wav",
        "wood": Q + "Woodblock/wood_click_f_*.wav", "claves": Q + "Claves/Claves1_Hit_v2*.wav",
        "tom_lo": P + "Tom 2/Mallet/TomL_HitM_v4_*.wav", "tom_hi": P + "Tom 1/Mallet/TomH_HitM_v4_*.wav",
        "ratchet": Q + "Ratchet/Ratchet1_Fast_*.wav", "anvil": Q + "Anvil/Anvil_Hit2_*.wav",
    }
    for k, g in G.items():
        v = S.kit(g)
        assert v, k
        KIT[k] = [x / (np.abs(x).max() + 1e-9) for x in v]
    return KIT


def hit(trk, kitname, t, vel=1.0, pan=0.0, dur=None):
    K = kits()[kitname]
    x = K[D.rng().integers(len(K))]
    if dur is not None:
        n = min(len(x), int(dur * SR)); x = x[:n].copy(); r = min(n, int(0.03 * SR))
        x[-r:] *= (np.linspace(1, 0, r)[:, None] if x.ndim == 2 else np.linspace(1, 0, r))
    T[trk].add(x, t + hum(0.002), vel * D.rng().uniform(0.93, 1.04), pan)


# ------------------------------------------------------------------ melodic players
def flute(bar, notes, vel=1.0, which="alto", trk="flute", tr=0, legato=0.88, double8=0.0, low8=0.0, pan=0.0):
    prev_end = None
    for nt in notes:
        s, l, m = nt[:3]
        opt = nt[3] if len(nt) > 3 else ""
        m += tr
        t = t_of(bar, s) + hum(0.002)
        d = l * S16 * legato
        sc = 0.0; vib = None; fall = 0.0; trill = None
        v = vel * (1.0 if s % 4 == 0 else 0.94 if s % 2 == 0 else 0.9)
        slur = prev_end is not None and abs(prev_end - s) < 0.01 and l == 1 and opt != "acc"
        if opt == "acc":
            v *= 1.08; sc = -30
        elif opt == "fall":
            fall = -60; d = l * S16 * 0.9
        elif opt == "fallbig":
            fall = -170; d = l * S16 * 0.95
        elif opt == "trill":
            trill = (1, 11.0, 0.05); d = l * S16 * 0.96
        elif opt == "trillhang":
            trill = (1, 10.5, 0.2); d = l * S16 * 0.97
        elif opt in ("hang", "hangdark"):
            vib = 24 if opt == "hang" else 40; d = l * S16 * 0.97
            if opt == "hangdark":
                fall = -70
        if l == 1 and not slur and opt == "":
            d = S16 * 0.8                        # tongued 16ths: crisp, bouncy
        x = I.recorder(m, d, v, which=which, slur=slur, scoop=sc, vib=vib, fall=fall, trill=trill)
        T[trk].add(x, t, 1.0, pan)
        if trk in ("flute", "flute_lo"):
            FLUTE_NOTES.append(dict(time=round(float(t_of(bar, s)), 4), dur=round(l * S16, 4), midi=int(m),
                                    instrument=which))
        if double8 and m + 12 <= 95:
            y = I.recorder(m + 12, d, v * 0.9, which="sop", slur=slur, scoop=sc * 0.5, vib=vib, fall=fall, trill=trill)
            T["flute8"].add(y, t + 0.005, double8, 0.0)
        if low8:
            y = I.recorder(m - 12, d, v, which="tenor", slur=slur, vib=vib, fall=fall)
            T["flute_lo"].add(y, t + 0.004, low8, 0.0)
        prev_end = s + l


def pluck(bar, notes, vel=1.0, pan=-0.35, lute=0.55, tr=0):
    """plucked answer: sampled psaltery (bright, metallic-wire) + DP lute (gut body) a hair later"""
    for s, l, m, *_ in notes:
        m += tr
        t = t_of(bar, s) + hum(0.003)
        v = vel * (1.0 if s % 4 == 0 else 0.92 if s % 2 == 0 else 0.86)
        if m >= 69:
            T["pluck"].add(I.psaltery(m, l * S16 * 1.6, v, art="pluck"), t, 1.0, pan)
        else:
            T["pluck"].add(I.strum(m, l * S16 * 1.6, v * 0.9), t, 1.0, pan)
        if lute:
            T["lute"].add(E.lute(m - 12, l * S16 * 1.3, v * lute, 0.75), t + 0.004, 1.0, -pan)
        ev("pluck", t_of(bar, s))


def fiddle(bar, notes, vel=1.0, trk="fiddle", tr=0, players=1, pan=0.3, vib=16, legato=0.95, accent_=0.32):
    nn = [(s * S16 + (t_of(bar, s) - bar * BAR - s * S16), l * S16 * legato, m + tr, 1.0 if s % 4 == 0 else 0.9)
          for s, l, m, *_ in notes]
    total = max(a + b for a, b, _, _ in nn) + 0.05
    sd = int(bar * 131 + tr * 7 + len(notes) * 3 + players)
    if players > 1:
        x = I.fiddle_section(nn, total, players=players, vel=vel, seed=sd, vib=vib, accent=accent_)
        T[trk].add(x, bar * BAR, 1.0)
    else:
        x = I.fiddle(nn, total, vel=vel, seed=sd, vib=vib, accent=accent_)
        T[trk].add(x, bar * BAR, 1.0, pan)


GURDY_NOTES, CHIEN, DRONES = [], [], []


def gurdy(bar, notes, vel=0.9, tr=0):
    for s, l, m, *_ in notes:
        GURDY_NOTES.append((t_of(bar, s), l * S16 * 0.97, m + tr, vel))
        ev("gurdy", t_of(bar, s))


def buzz(bar, steps=(2, 6, 10, 14), vel=1.0):
    for s in steps:
        CHIEN.append((t_of(bar, s), vel * (1.0 if s % 8 == 6 else 0.8)))


def drone(bar0, bar1, mids, lev=1.0, fi=0.2, fo=0.3):
    DRONES.append((bar0 * BAR, bar1 * BAR, mids, lev, fi, fo))


def render_gurdy():
    """hurdy-gurdy: drone strings, buzzing trompette (chien) and keyed melody -- physical bowed waveguide"""
    for (t0, t1, mids, lev, fi, fo) in DRONES:
        n = int((t1 - t0 + fo) * SR)
        for j, m in enumerate(mids):
            v = I.wheel(n, level=0.2, crank_hz=BPM / 60 / 2, attack=fi, release=fo)
            y = I.gurdy_string(np.full(n, float(m)), v, force=0.3, beta=0.11 + 0.01 * j, seed=11 + j + int(t0 * 7))
            y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05 * lev
            T["drone"].add(y, t0, 1.0, (-0.35, 0.35, 0.0)[j % 3])
    if CHIEN:
        st = sorted(CHIEN)
        regions = [[st[0]]]
        for q in st[1:]:
            (regions.append([q]) if q[0] - regions[-1][-1][0] > BAR * 1.2 else regions[-1].append(q))
        L = int(0.2 * SR)
        kern = np.exp(-np.arange(L) / (0.04 * SR)) * (1 - np.exp(-np.arange(L) / (0.004 * SR)))
        kern *= np.cos(np.linspace(0, np.pi / 2, L)) ** 2
        for reg in regions:
            t0 = reg[0][0] - 0.15; t1 = reg[-1][0] + 0.45
            n = int((t1 - t0) * SR)
            pulses = np.zeros(n)
            for t, v in reg:
                i = int((t - t0) * SR); m = min(L, n - i)
                pulses[i:i + m] = np.maximum(pulses[i:i + m], v * kern[:m])
            vb = I.wheel(n, level=0.2, crank_hz=BPM / 60, attack=0.1, release=0.3) * (1 + 0.9 * pulses)
            tr = I.gurdy_string(np.full(n, float(Fs3 - 12 + 12)), vb, force=0.42, beta=0.13, seed=int(t0 * 97) % 9973)
            tr = tr / (np.sqrt(np.mean(tr ** 2)) + 1e-9) * 0.05
            T["chien"].add(I.chien(tr, pulses, 1.0) + tr * (0.1 + 0.25 * pulses), t0, 1.0, 0.4)
    if GURDY_NOTES:
        mel = sorted(GURDY_NOTES)
        phrases = [[mel[0]]]
        for nt in mel[1:]:
            pe = phrases[-1][-1][0] + phrases[-1][-1][1]
            (phrases.append([nt]) if nt[0] - pe > BEAT * 0.9 else phrases[-1].append(nt))
        for ph in phrases:
            t0 = ph[0][0] - 0.03; t1 = ph[-1][0] + ph[-1][1]
            n = int((t1 - t0 + 0.25) * SR)
            mc = np.full(n, float(ph[0][2])); amp = np.zeros(n); acc = np.zeros(n)
            for (t, d, m, v) in ph:
                a = int((t - t0) * SR); b = min(n, int((t - t0 + d) * SR))
                mc[a:] = m; amp[a:b] = v
                k = min(b - a, int(0.06 * SR))
                acc[a:a + k] = np.maximum(acc[a:a + k], np.exp(-np.arange(k) / (0.02 * SR)))
            mc = uniform_filter1d(mc, int(0.005 * SR))
            amp = uniform_filter1d(amp, int(0.02 * SR))
            vb = (0.08 + 0.2 * amp + 0.06 * acc) * I.adsr(n, 0.03, 0.05, 1.0, 0.15)
            y = I.gurdy_string(mc, vb, force=0.33, beta=0.12, seed=int(t0 * 100) % 9973)
            y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 0.05
            T["gurdy"].add(y * np.clip(amp * 1.5, 0, 1), t0, 1.0, -0.3)


def chops(bar, chords, steps=(2, 6, 10, 14), vel=1.0):
    """DP: lute power-chord strums on the offbeats (down/up alternating)"""
    for s in steps:
        c = chords if isinstance(chords, str) else (chords[0] if s < 8 else chords[1])
        x = E.strum(list(CH[c][1]), S16 * 1.15, vel * (1.0 if s % 8 == 6 else 0.85), down=(s % 4 == 2))
        T["chop"].add(x, t_of(bar, s) + hum(0.003), 1.0, 0.0)


# ------------------------------------------------------------------ bass (DP models)
def bass_pat(bar, pat, chords, vel=1.0):
    """pat: (step, len, interval, vel, pop). Plucked deep bass with octave pops."""
    for s, l, iv, v, pop in pat:
        c = chords if isinstance(chords, str) else (chords[0] if s < 8 else chords[1])
        m = CH[c][0] + iv
        T["bass"].add(E.deep_bass(m, l * S16 * 0.9, vel * v, pop=pop), t_of(bar, s) + hum(0.0015), 1.0, 0.0)
        ev("bass", t_of(bar, s))


B_HOOK = [(0, 2, 0, 1.0, False), (3, 1, 0, 0.7, False), (6, 2, 0, 0.9, False), (10, 2, 0, 0.9, False),
          (14, 1, 0, 0.8, False), (15, 1, 12, 0.6, True)]
B_BOUNCE = [(2, 2, 0, 1.0, False), (6, 1, 0, 0.9, False), (7, 1, 12, 0.65, True), (10, 2, 0, 1.0, False),
            (14, 1, 0, 0.85, False), (15, 1, 12, 0.7, True)]
B_BOUNCE2 = [(2, 1, 0, 1.0, False), (3, 1, 0, 0.7, False), (6, 2, 0, 0.95, False), (9, 1, 12, 0.6, True),
             (10, 2, 0, 0.95, False), (13, 1, 7, 0.75, False), (14, 1, 0, 0.9, False), (15, 1, 12, 0.65, True)]
B_HALF = [(0, 6, 0, 1.0, False), (10, 4, 0, 0.8, False), (15, 1, 12, 0.5, True)]

# drop: legato gliding growl (points = (step, midi)); the kick sidechain makes it pump
GROWL = {"Bm": [(0, B1), (3, B2), (4, B1), (7, D2), (8, B1), (10, Fs2), (12, B1), (14, A1)],
         "C": [(0, C2), (3, C3), (4, C2), (7, E2), (8, C2), (10, G2), (12, C2), (14, B1)],
         "GF#": [(0, G1), (3, G2), (4, G1), (7, B1), (8, F1s), (10, Fs2), (12, F1s), (14, As4 - 36)],
         "Em": [(0, E2), (3, E2 + 12), (4, E2), (7, G2), (8, E2), (10, B2), (12, E2), (14, D2)],
         "F#": [(0, F1s), (3, Fs2), (4, F1s), (7, As4 - 36), (8, Cs2), (10, Fs2), (12, F1s), (14, F1s)]}


def growl(bar, key, vel=1.0, upto=16):
    pts = [(t_of(bar, s) - bar * BAR, m) for s, m in GROWL[key] if s < upto]
    d = (t_of(bar, upto) - bar * BAR) - 0.01
    T["growl"].add(E.growl_bass(pts, d, vel), bar * BAR, 1.0, 0.0)
    for s, m in GROWL[key]:
        if s < upto:
            ev("bass", t_of(bar, s))
    # pops on the off-8ths (DP octave "pop")
    for s in (7, 15):
        if s < upto:
            m = [mm for ss, mm in GROWL[key] if ss <= s][-1]
            T["bass"].add(E.deep_bass(m + 12, S16 * 0.8, 0.45 * vel, pop=True), t_of(bar, s), 1.0, 0.0)


def sub_hold(bar, points, nbars=1, vel=1.0):
    d = nbars * BAR - 0.02
    T["sub"].add(E.sub_slide([(t_of(bar, s) - bar * BAR, m) for s, m in points], d, vel), bar * BAR, 1.0, 0.0)


# ------------------------------------------------------------------ drums & percussion
def kick(bar, steps=(0, 4, 8, 12), vel=1.0, acoustic=0.55):
    for s in steps:
        t = t_of(bar, s)
        T["kick"].add(E.club_kick(vel), t, 1.0, 0.0)
        if acoustic:
            hit("kick_ac", "bd", t, vel * acoustic, 0.0, dur=0.4)
        KICKS.append((t, vel)); ev("kick", t)


def clap(bar, steps=(4, 12), vel=1.0, tabor=0.7, snare=0.0):
    for s in steps:
        t = t_of(bar, s)
        hit("clap", "clap", t, vel, D.rng().uniform(-0.15, 0.15))
        T["clap"].add(E.clap(vel * 0.8), t + 0.002, 1.0, 0.0)
        if tabor:
            T["tabor"].add(E.tabor(vel * tabor), t, 1.0, 0.1)
        if snare:
            hit("snare", "snare", t, vel * snare, 0.05, dur=0.5)
        ev("clap", t)


def riq(bar, steps=(2, 6, 10, 14), vel=1.0, ghosts=False, tamb=0.35):
    for s in steps:
        t = t_of(bar, s)
        T["riq"].add(E.riq(vel * (1.0 if s % 8 == 6 else 0.9), long=(s % 8 == 6)), t + hum(0.002), 1.0, 0.25)
        if tamb:
            hit("tamb", "tamb_hit", t, vel * tamb, 0.55, dur=0.3)
        ev("riq", t)
    if ghosts:
        for s in (3, 11, 15):
            T["riq"].add(E.riq(vel * 0.35), t_of(bar, s) + hum(0.002), 1.0, 0.25)


def shaker(bar, vel=1.0, steps=range(16)):
    for s in steps:
        a = (0.95, 0.5, 0.3, 0.5)[s % 4] if s % 4 != 2 else 0.75     # DP accent shape, offbeat lifted
        hit("shaker", "shaker", t_of(bar, s), vel * a, -0.55)
        T["shaker"].add(E.shaker(vel * a * 0.6), t_of(bar, s), 1.0, 0.55)


def tamb16(bar, vel=1.0):
    for s in range(16):
        hit("tamb", "tamb_shake", t_of(bar, s), vel * (0.9 if s % 4 == 2 else 0.75 if s % 2 == 0 else 0.5), 0.6,
            dur=0.12)


def frame(bar, steps=(3, 6, 11, 14), vel=1.0):
    for s in steps:
        T["frame"].add(E.frame(vel * 0.9, 95, True), t_of(bar, s), 1.0, -0.2)
        hit("frame", "frame_lo", t_of(bar, s), vel * 0.6, -0.25)


def wood(bar, steps=(3, 11), vel=1.0, kind="wood", pan=0.4):
    for s in steps:
        hit("wood", kind, t_of(bar, s), vel, pan, dur=0.2)
        ev("wood", t_of(bar, s))


def darb_fill(bar, start=12, vel=1.0):
    for s in range(start, 16):
        hit("darb", "darb_tek" if s % 2 == 0 else "darb_ka", t_of(bar, s), vel * (0.6 + 0.4 * (s - start) / max(1, 15 - start)), 0.35)


def maqsum(bar, vel=1.0):
    for s, k, v in [(0, "darb_doum", 1.0), (3, "darb_tek", 0.8), (6, "darb_tek", 0.9), (8, "darb_doum", 0.95),
                    (11, "darb_ka", 0.5), (12, "darb_tek", 0.85), (14, "darb_ka", 0.6)]:
        hit("darb", k, t_of(bar, s), vel * v, 0.35)


def toms(bar, steps, vel=1.0):
    """descending tom fill (sampled mallet toms + DP synth toms)"""
    n = len(steps)
    for i, s in enumerate(steps):
        k = "tom_hi" if i < n / 2 else "tom_lo"
        hit("toms", k, t_of(bar, s), vel * (0.75 + 0.25 * i / max(1, n - 1)), 0.25 if k == "tom_hi" else -0.25, dur=0.7)
        T["toms"].add(E.tom(150 - 50 * i / max(1, n - 1), vel * 0.7), t_of(bar, s), 1.0, 0.0)
        ev("tom", t_of(bar, s))


def roll(bar, start, stop, vel=1.0):
    """DP tabor roll: 32nds with a power-1.6 crescendo"""
    tot = (stop - start) * 2
    for i in range(int(tot)):
        s = start + i / 2
        v = 0.18 + 0.75 * (i / tot) ** 1.6
        T["tabor"].add(E.tabor(v * vel), t_of(bar, s) + hum(0.0012), 1.0, 0.0)
        if i % 2 == 0:
            hit("snare", "snare_lo", t_of(bar, s), v * vel * 0.5, 0.0, dur=0.25)


def riser(bar, start, stop, vel=1.0):
    t0, t1 = t_of(bar, start), t_of(bar, stop)
    T["fx"].add(E.sweep(t1 - t0, vel, True), t0, 1.0, 0.0)
    rc = E.rev_cym(min(1.4, t1 - t0), 0.8 * vel)
    T["cym"].add(rc, t1 - len(rc) / SR, 1.0, 0.0)


def crash(bar, step=0, vel=1.0, boom_=True, gong=False):
    t = t_of(bar, step)
    T["cym"].add(E.crash(2.4, vel), t, 1.0, 0.0)
    if boom_:
        T["boom"].add(E.boom(vel * 0.9), t, 1.0, 0.0)
        hit("big", "big", t, vel * 0.8, 0.0, dur=1.5)
        ev("boom", t)
    if gong:
        hit("boom", "gong", t, vel * 0.5, 0.0, dur=4.0)
    ev("crash", t)


def stab(bar, steps, chord, vel=1.0):
    """unison stop hit: kick + big drum + bass + chord strum + clap + tom (DP stop_hits)"""
    for s in steps:
        t = t_of(bar, s)
        T["kick"].add(E.club_kick(vel), t, 1.0, 0.0); KICKS.append((t, vel))
        hit("big", "big_m", t, vel * 0.8, 0.0, dur=0.8)
        T["bass"].add(E.deep_bass(CH[chord][0], S16 * 1.6, vel, pop=True), t, 1.0, 0.0)
        T["chop"].add(E.strum(list(CH[chord][1]), S16 * 1.5, vel), t, 1.0, 0.0)
        hit("clap", "clap", t, vel * 0.8, 0.0)
        hit("toms", "tom_lo", t, vel * 0.8, -0.1, dur=0.7)
        ev("stab", t)


def fsec_chord(bar, step, midis, dur_steps, vel=1.0, players=2, swell=False, trem=False):
    for k, m in enumerate(midis):
        d = dur_steps * S16
        if trem:      # re-bowed 16th tremolo (DP's E-flat swell)
            nn = [(i * S16, S16 * 0.85, m, 0.8 + 0.2 * (i % 2 == 0)) for i in range(int(dur_steps))]
        else:
            nn = [(0.0, d, m, 1.0)]
        x = I.fiddle_section(nn, d, players=players, vel=vel, seed=bar * 17 + k + step, vib=12, accent=0.1 if trem else 0.0)
        if swell:
            x *= np.linspace(0.25, 1.0, len(x))[:, None] ** 1.5
        T["fsec"].add(x, t_of(bar, step), 1.0)


# ====================================================================== ARRANGEMENT
HARM = {}


def arrange():
    reset()
    kits()
    GURDY_NOTES.clear(); CHIEN.clear(); DRONES.clear()
    hook_chords = ["Bm", "C", "Bm", ("G", "F#")]

    # ---------------------------------------------------------------- 1-2  THE TAUNT (hook at 0.000 s)
    section(0, "hook", "The taunt: flute hook on the very first downbeat, plucked strings answer, kick + bass + riq "
                       "from beat one (no intro)")
    accent(0.0, "hook", "Flute hook (the taunt) + kick + bass on the first downbeat", 1.0)
    drone(0, 6, [B2 - 12 + 12, Fs3], 0.8, fi=0.05)
    for b, c, ans in ((0, "Bm", ANS1), (1, "C", ANS2)):
        HARM[b] = c
        flute(b, T1)
        pluck(b, ans, 0.95)
        kick(b, vel=0.92)
        bass_pat(b, B_HOOK, c, 0.95)
        riq(b, vel=0.85)
        wood(b, (3, 11), 0.5, "claves", 0.5)
        buzz(b, (6, 14), 0.8)
    shaker(1, 0.6)
    accent(t_of(0, 3), "syncopation", "B5 on the off-16th: the hook's skip", 0.7)

    # ---------------------------------------------------------------- 3-6  RATS (groove A)
    section(2, "rats", "Full groove: clap + tabor backbeat, shaker 16ths, frame-drum bounce, lute chops; the hook "
                       "climbs (T2) and turns on G-F#")
    crash(2, vel=0.7, boom_=False)
    for i, b in enumerate(range(2, 6)):
        c = hook_chords[i]
        HARM[b] = c
        kick(b)
        clap(b, vel=0.9)
        riq(b)
        shaker(b, 0.8)
        frame(b)
        chops(b, c, vel=0.8)
        buzz(b)
        bass_pat(b, B_BOUNCE if i % 2 == 0 else B_BOUNCE2, c)
    flute(2, T1); pluck(2, ANS1)
    flute(3, T1); pluck(3, ANS2)
    flute(4, T2); pluck(4, ANS3); fiddle(4, [(s, l, m - 12) for s, l, m, *_ in T2], 0.6, pan=0.3)
    flute(5, CAD); pluck(5, ANS4); flute(5, PU)
    fiddle(5, [(s, l, m - 12) for s, l, m, *_ in CAD], 0.6, pan=0.3)
    wood(4, (3, 7, 11), 0.7); wood(5, (3, 7, 11), 0.7)
    darb_fill(5, 12, 0.8)
    accent(t_of(4, 0), "lift", "Hook climbs a fourth (T2); fiddle doubles below", 0.6)

    # ---------------------------------------------------------------- 7  THE GATE (build + held breath)
    section(6, "gate", "Build: the taunt in C, then the tritone F#5 trill; ratchet + roll + riser; full-band "
                       "silence on the last two 16ths")
    HARM[6] = "C"
    flute(6, GATE)
    kick(6, (0, 4, 8))
    clap(6, (4,), 0.8)
    riq(6, (2, 6), 0.8)
    bass_pat(6, [(s, 1, 0, 0.55 + 0.03 * s, False) for s in range(0, 14, 2)], "C")
    fsec_chord(6, 8, [Fs4, C5], 6, 0.8, swell=True)
    x = kits()["ratchet"][0]; n = min(len(x), int(14 * S16 * SR))
    T["fx"].add(x[:n] * (np.linspace(0.05, 1.0, n) ** 2)[:, None], t_of(6, 0), 0.6, 0.0)
    toms(6, (8, 9, 10, 11, 12, 13), 0.85)
    roll(6, 8, 14, 0.9)
    riser(6, 0, 14, 0.8)
    gap(6, 14)

    # ---------------------------------------------------------------- 8-11  THE STRANGER (groove B: gurdy calls, flute answers)
    section(7, "stranger", "Role reversal: the hurdy-gurdy calls, the flute answers with the displaced taunt; "
                           "darbuka maqsum, bouncier syncopated bass; the bargain")
    crash(7, vel=0.85)
    accent(t_of(7, 0), "arrival", "The stranger arrives: boom + crash, gurdy riff", 0.85)
    drone(7, 11, [B2, Fs3], 0.7)
    for b, c in ((7, "Em"), (8, "Bm"), (9, "C")):
        HARM[b] = c
        gurdy(b, GB[c], 0.95)
        flute(b, FA, 0.95)
        kick(b)
        clap(b, (4, 12), 0.85, tabor=0.5)
        riq(b, vel=0.9)
        maqsum(b, 0.8)
        shaker(b, 0.6, steps=range(1, 16, 2))
        bass_pat(b, B_BOUNCE2, c)
        buzz(b, (6, 14))
    chops(8, "Bm", (2, 10), 0.7); chops(9, "C", (2, 6, 10, 14), 0.7)
    fiddle(9, [(8, 1, A4), (10, 1, Fs4), (11, 2, B4), (13, 1, A4), (14, 2, Fs4)], 0.6, pan=-0.3)
    pluck(8, [(14, 1, Fs5), (15, 1, E5)], 0.7)
    # 11: THE SPELL -- he raises the flute; everything pulls back into the drop
    HARM[10] = "F#"
    section(10, "spell", "He raises the flute: rising harmonic-minor run with a C#6 trill, roll + riser, "
                         "silence, pickup into the drop")
    flute(10, SPELL)
    flute(10, PU)
    kick(10, (0, 4, 8))
    riq(10, (2, 6), 0.8)
    sub_hold(10, [(0, F1s), (8, Fs2)], 1, 0.8)
    fsec_chord(10, 0, [As4, Cs5, Fs5], 14, 0.75, swell=True, trem=True)
    roll(10, 6, 14, 1.0)
    riser(10, 0, 14, 1.0)
    gap(10, 14)

    # ---------------------------------------------------------------- 12-16  DROP 1: THE RAT PROCESSION
    section(11, "drop_1", "DROP 1 -- the rat procession: flute taunt answered by a chromatic hurdy-gurdy + fiddle "
                          "16th scurry; gliding growl bass pumping against the kick; woodblocks on 3/11")
    crash(11, vel=1.0, gong=False)
    accent(t_of(11, 0), "drop", "DROP 1: rat procession", 1.0)
    drone(11, 16, [B2, Fs3], 0.6)
    plan = [(11, "Bm", T1, "rat", RAT_B), (12, "C", T1, "rat", RAT_C), (13, "Bm", T2, "pluck", ANS3),
            (14, ("G", "F#"), CAD, "pluck", ANS4), (15, "Bm", T1, "rat", RAT_B)]
    for b, c, fl, who, ans in plan:
        HARM[b] = c
        flute(b, fl, 1.0, low8=0.25 if b == 15 else 0.0)
        if who == "rat":
            gurdy(b, ans, 1.0)
            fiddle(b, ans, 0.75, pan=0.35, vib=0, legato=0.9, accent_=0.5)
        else:
            pluck(b, ans, 1.0)
            gurdy(b, ans, 0.6)
        kick(b, (0, 4, 8, 12) + ((14,) if b in (12, 14) else ()))
        clap(b, vel=1.0, snare=0.5)
        riq(b, ghosts=True)
        shaker(b, 0.9)
        frame(b, vel=0.9)
        wood(b, (3, 11), 0.8)
        chops(b, c, vel=0.9)
        buzz(b)
        growl(b, "GF#" if c == ("G", "F#") else c)
    flute(14, PU)
    darb_fill(14, 12, 0.9)
    accent(t_of(11, 8), "answer", "Hurdy-gurdy + fiddle rat scurry answers the flute", 0.8)
    accent(t_of(15, 0), "river", "The procession reaches the river: tenor recorder joins an octave below", 0.7)
    # 16: the rats go under -- one hit, then still water
    section(15, "river", "The procession reaches the river (tenor octave below)")
    section(16, "still_water", "Hit on C (bII) + gong, then near-silence: low drone, the flute's falling F5, "
                               "a tabor roll lifts into the celebration")
    HARM[16] = "C"
    crash(16, vel=0.95, gong=True)
    stab(16, (0,), "C", 0.95)
    T["kick"].add(E.club_kick(0.5), t_of(16, 8), 1.0, 0.0)
    flute(16, [(4, 2, Fs5, "acc"), (8, 4, F5, "fallbig")], 0.8)
    drone(16, 17, [C3 - 12 + 12, G2 + 12], 0.6, fi=0.05, fo=0.1)
    roll(16, 12, 16, 0.8)
    accent(t_of(16, 0), "hit", "The rats go under: hit + gong", 1.0)

    # ---------------------------------------------------------------- 17-18  CELEBRATION
    section(17, "celebration", "The town celebrates: the same taunt now over D and G -- genuinely happy; claps "
                               "on every beat, tambourine 16ths, fiddle + pluck answers")
    crash(17, vel=0.9, boom_=True)
    accent(t_of(17, 0), "celebration", "Celebration burst (D major)", 0.95)
    for b, c, fl, ans in ((17, "D", T_D, CEL_D), (18, "Gmaj", T_G, CEL_G)):
        HARM[b] = c
        flute(b, fl, 1.0)
        fiddle(b, ans, 0.75, pan=0.3, vib=10, legato=0.9)
        pluck(b, ans, 0.8)
        kick(b)
        clap(b, (0, 4, 8, 12) if b == 18 else (4, 12), 0.95, snare=0.4)
        tamb16(b, 0.8)
        riq(b, ghosts=True)
        frame(b)
        chops(b, c, vel=0.9)
        bass_pat(b, B_BOUNCE, c, 1.0)
    drone(17, 19, [D2 + 12, A2 + 12], 0.6, fi=0.05)
    wood(18, (3, 7, 11, 15), 0.7)

    # ---------------------------------------------------------------- 19-23  BETRAYAL
    section(19, "betrayal", "The council refuses to pay: the taunt turns minor (F, Bb) over Dm and Bb; half-time "
                            "drums, low fiddle sneers, tremolo strings; G minor with a C# tritone hang")
    accent(t_of(19, 0), "betrayal", "Betrayal: the hook turns minor; half-time", 0.9)
    T["boom"].add(E.boom(0.8), t_of(19, 0), 1.0, 0.0)
    drone(19, 23, [D2 + 12, A2 + 12], 0.55)
    for b, c in ((19, "Dm"), (20, "Bb"), (21, "Gm")):
        HARM[b] = c
        kick(b, (0, 10), 0.95)
        clap(b, (8,), 0.9, tabor=0.8, snare=0.6)
        riq(b, (6, 14), 0.75, tamb=0.2)
        shaker(b, 0.45, steps=(2, 6, 10, 14))
        hit("toms", "tom_lo", t_of(b, 12), 0.6, -0.2, dur=0.8)
        bass_pat(b, B_HALF, c, 1.0)
    flute(19, TM); fiddle(19, SNEER1, 0.8, tr=-12, pan=-0.25, vib=22)
    flute(20, TM); fiddle(20, SNEER2, 0.8, tr=-12, pan=-0.25, vib=22)
    fsec_chord(19, 8, [D4, A4], 8, 0.6, trem=True)
    fsec_chord(20, 8, [D4, F4], 8, 0.6, trem=True)
    flute(21, SMILE, 0.95)
    fsec_chord(21, 8, [Cs4, G4], 8, 0.7, trem=True, swell=True)
    accent(t_of(21, 8), "tritone", "C#5 hang over G minor: the smile fades", 0.8)
    # 23: he walks into the night -- flute alone in 16ths, heartbeat kick, then silence
    HARM[22] = "A"
    section(22, "into_the_night", "The Piper walks away: the flute alone in A harmonic 16ths over a heartbeat kick "
                                  "and a sub, riser, silence, pickup")
    flute(22, NIGHT, 0.9)
    flute(22, PU)
    kick(22, (0, 8), 0.7, acoustic=0.7)
    sub_hold(22, [(0, A1), (8, A1)], 1, 0.7)
    riser(22, 2, 14, 0.9)
    roll(22, 8, 14, 0.8)
    gap(22, 14)

    # ---------------------------------------------------------------- 24-31  DROP 2: THE CHILDREN
    section(23, "drop_2", "DROP 2 -- the children follow: taunt doubled by the soprano recorder an octave up, rat "
                          "scurry now with pluck + fiddle; tambourine 16ths, the biggest low end")
    crash(23, vel=1.05, gong=True)
    accent(t_of(23, 0), "drop", "DROP 2 (final drop): the children", 1.0)
    drone(23, 31, [B2, Fs3], 0.6)
    plan = [(23, "Bm", T1, "rat", RAT_B, 0.5), (24, "C", T1, "rat", RAT_C, 0.5), (25, "Bm", T2, "pluck", ANS3, 0.0),
            (26, ("G", "F#"), CAD, "pluck", ANS4, 0.45)]
    for b, c, fl, who, ans, d8 in plan:
        HARM[b] = c
        flute(b, fl, 1.0, double8=d8)
        if who == "rat":
            gurdy(b, ans, 1.0)
            fiddle(b, ans, 0.8, pan=0.35, vib=0, legato=0.9, accent_=0.5)
            pluck(b, ans[::2], 0.6, lute=0.3)
        else:
            pluck(b, ans, 1.0)
            gurdy(b, ans, 0.7)
            fiddle(b, [(s, l, m - 12) for s, l, m, *_ in fl], 0.6, pan=-0.3)
        kick(b, (0, 4, 8, 12) + ((14,) if b in (24,) else ()))
        clap(b, vel=1.0, snare=0.55)
        riq(b, ghosts=True)
        tamb16(b, 0.7)
        shaker(b, 0.7)
        frame(b)
        wood(b, (3, 7, 11), 0.8)
        chops(b, c, vel=0.95)
        buzz(b)
        growl(b, "GF#" if c == ("G", "F#") else c, 1.05)
    flute(26, PU)
    toms(26, (8, 9, 10, 11, 12, 13), 0.9)
    gap(26, 14)
    # 28-31: call & response tightens, fiddle descant, the TAG
    section(27, "climax", "Call and response tightens: gurdy imitates the taunt, then half-bar trades; a long "
                          "fiddle descant; Em lift; the chromatic TAG A#-B-C-C#-D")
    crash(27, vel=1.0)
    accent(t_of(27, 0), "climax", "Climax: trades + fiddle descant", 0.95)
    TR_FL = [(0, 2, A5, "acc"), (2, 1, Fs5), (3, 1, B5)]
    TR_GU = [(4, 2, G4), (6, 1, E4), (7, 1, A4)]
    clim = [(27, "Bm"), (28, "C"), (29, "Em"), (30, "F#")]
    for b, c in clim:
        HARM[b] = c
        kick(b, (0, 4, 8, 12) + ((14, 15) if b == 29 else ()))
        clap(b, vel=1.0, snare=0.6)
        riq(b, ghosts=True)
        tamb16(b, 0.8)
        shaker(b, 0.75)
        frame(b)
        wood(b, (3, 7, 11), 0.85)
        chops(b, c, vel=1.0, steps=(2, 6, 10, 14) if b != 30 else (2, 6, 10))
        buzz(b)
        growl(b, c, 1.05, upto=16 if b != 30 else 12)
    flute(27, T1, double8=0.5); gurdy(27, [(s + 8, l, m - 12) for s, l, m, *_ in T1], 1.0)
    pluck(27, [(s + 8, l, m - 12) for s, l, m, *_ in T1], 0.6, lute=0.3)
    flute(28, TR_FL, double8=0.5); gurdy(28, TR_GU, 1.0)
    flute(28, [(s + 8, l, m, *o) for s, l, m, *o in TR_FL], double8=0.5)
    gurdy(28, [(s + 8, l, m) for s, l, m in TR_GU], 1.0)
    flute(29, T2); pluck(29, ANS_EM, 1.0); gurdy(29, ANS_EM, 0.6, tr=-12)
    flute(30, TAG, double8=0.55)
    fiddle(27, [(0, 16, D6)], 0.55, trk="fdesc", players=2, vib=20)
    fiddle(28, [(0, 8, E6), (8, 8, G6)], 0.55, trk="fdesc", players=2, vib=20)
    fiddle(29, [(0, 8, G6), (8, 8, Fs6)], 0.55, trk="fdesc", players=2, vib=20)
    fiddle(30, [(0, 12, Fs6)], 0.6, trk="fdesc", players=2, vib=22)
    stab(30, (12,), "F#", 1.0)
    roll(30, 13, 16, 0.9)
    accent(t_of(30, 0), "tag", "Chromatic TAG A#5-B5-C6-C#6-D6", 0.9)

    # ---------------------------------------------------------------- 32  THE MOUNTAIN CLOSES
    HARM[31] = "C"
    section(31, "mountain", "Stutter: the taunt chopped into unison stabs (0, 3, 6, 10) as the children vanish; "
                            "the mountain seals in silence")
    flute(31, STUT, 1.0, double8=0.4)
    stab(31, (0, 3, 6, 10), "C", 1.0)
    crash(31, 0, 0.8, boom_=False)
    accent(t_of(31, 0), "stutter", "Stutter stabs: the passage closes", 0.95)
    gap(31, 12)

    # ---------------------------------------------------------------- 33-37  DISAPPEARANCE
    section(32, "disappearance", "Layers vanish: the hook with no band, the plucked answer with no flute, the taunt "
                                 "with holes in it, the Piper low in the fog, the last giggle and a pickup that "
                                 "loops back to the first bar")
    drone(32, 37, [B2, Fs3], 0.65, fi=0.4, fo=0.5)
    HARM.update({32: "Bm", 33: "C", 34: "Bm", 35: "G", 36: "F#"})
    flute(32, T1, 0.85); pluck(32, ANS1, 0.55, lute=0.3)
    riq(32, vel=0.5, tamb=0.0); shaker(32, 0.35, steps=range(2, 16, 4))
    sub_hold(32, [(0, B1)], 1, 0.5)
    pluck(33, ANS2, 0.65, lute=0.0)
    riq(33, (2, 6, 10, 14), 0.4, tamb=0.0); frame(33, (0, 8), 0.5)
    sub_hold(33, [(0, C2)], 1, 0.4)
    flute(34, T1_HOLES, 0.8)
    kick(34, (0, 8), 0.5, acoustic=0.8)
    sub_hold(34, [(0, B1)], 1, 0.45)
    flute(35, LOW_CAD, 0.95, which="tenor", trk="flute_lo")
    frame(35, (0, 8), 0.5); pluck(35, [(8, 2, B4), (10, 2, D5), (12, 4, G5)], 0.4, lute=0.4)
    sub_hold(35, [(0, G1)], 1, 0.4)
    flute(36, GIGGLE, 0.75)
    pluck(36, ANS4[:4], 0.45, lute=0.0)
    flute(36, PU, 0.85)
    sub_hold(36, [(8, F1s)], 1, 0.45)
    T["fx"].add(E.rev_cym(1.2, 0.5), NLOOP / SR - 1.2, 1.0, 0.0)
    accent(t_of(36, 14), "loop", "G5 pickup resolves into the first bar's A5 (seamless loop)", 0.6)

    render_gurdy()
    return T
