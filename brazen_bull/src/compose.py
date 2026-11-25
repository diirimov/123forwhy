"""THE BRAZEN BULL - composition, arrangement, mix and master.

136 BPM, 4/4, 34 bars = exactly 60.000 s.  Key: E Phrygian (E F G A B C D), with an
E Phrygian-dominant (Hijaz: G#) twist in the final drop.

Bar map (1 bar = 1.7647 s):
  0-1   intro / opening hook        0.000 -  3.529
  2-7   first groove                3.529 - 14.118
  8-13  escalation                 14.118 - 24.706
  14    pre-drop                   24.706 - 26.471
  15-22 main drop                  26.471 - 40.588
  23-26 dark breakdown             40.588 - 47.647
  27-32 final drop                 47.647 - 58.235
  33    final impact / loop link   58.235 - 60.000
"""
import json
import sys
import time
import numpy as np
import soundfile as sf
import pyloudnorm as pyln

from dsp import (SR, BPM, BEAT, STEP, BAR, N_TOTAL, mtof, lp, hp, bp, eq, svf_lp, pan, to_st, widen,
                 chorus, haas, make_ir, convolve_st, pingpong, softclip, normalize, fade, db,
                 pitch_shift_resample)
import instruments as I
import vocals as V
from mixtools import compress, pump_env, limiter, true_peak_db, lr4_split

N = N_TOTAL
SWING = 0.085
RNG = np.random.default_rng(136)
EVENTS = []
KICKS = []


def T(bar, step=0.0):
    t = (bar * 16 + step) * STEP
    if abs(step - round(step)) < 1e-9 and int(round(step)) % 2 == 1:
        t += SWING * STEP
    return t


def ev(t, cat, name, **kw):
    EVENTS.append(dict(time=round(float(t), 4), category=cat, name=name, **kw))


def hum(ms=1.6):
    return RNG.normal(0, ms / 1000.0)


class Mix:
    def __init__(self):
        self.b = {}

    def bus(self, name):
        if name not in self.b:
            self.b[name] = np.zeros((2, N))
        return self.b[name]

    def add(self, name, x, t, g=1.0, p=0.0):
        st = pan(x, p) if x.ndim == 1 else x
        i0 = int(round(t * SR))
        s0 = 0
        if i0 < 0:
            s0 = -i0
            i0 = 0
        if i0 >= N:
            return
        L = min(st.shape[1] - s0, N - i0)
        if L <= 0:
            return
        self.bus(name)[:, i0:i0 + L] += g * st[:, s0:s0 + L]

    def add_ending_at(self, name, x, t_end, g=1.0, p=0.0):
        n = x.shape[-1]
        self.add(name, x, t_end - n / SR, g, p)


M = Mix()

# =============================================================================
# MUSICAL MATERIAL
# =============================================================================
E1, F1, G1, A1, B1, C2, D2, E2 = 28, 29, 31, 33, 35, 36, 38, 40
SCALE = [0, 1, 3, 5, 7, 8, 10]


def up_step(m):
    pc = (m - 4) % 12
    for s in SCALE + [12]:
        if s > pc:
            return m + (s - pc)
    return m + 1


# (step, midi, len_in_16ths, velocity)
HOOK = {
    "A": [(0, 64, 2, 1.0), (3, 65, 2, .92), (6, 64, 1, .95), (7, 62, 1, .62), (8, 64, 1, .72),
          (9, 67, 2, .98), (11, 65, 1, .6), (12, 64, 2, .9)],
    "B": [(0, 64, 1, .8), (1, 65, 1, .6), (2, 67, 1, .7), (3, 69, 2, 1.0), (6, 71, 1, 1.0), (7, 69, 1, .6),
          (8, 67, 1, .72), (9, 65, 2, .95), (11, 67, 1, .6), (12, 65, 1, .8), (13, 64, 1, .7)],
    "C": [(0, 64, 2, 1.0), (3, 65, 2, .92), (6, 64, 1, .95), (7, 62, 1, .62), (8, 64, 1, .72),
          (9, 67, 2, .98), (11, 69, 1, .7), (12, 72, 2, 1.0)],
    "D": [(0, 71, 1, 1.0), (1, 69, 1, .6), (2, 67, 1, .7), (3, 65, 2, 1.0), (6, 67, 1, .8), (7, 65, 1, .6),
          (8, 64, 2, 1.0)],
    # escalation answer: hook shifted up the mode (starts on A)
    "V": [(0, 69, 2, 1.0), (3, 71, 2, .92), (6, 69, 1, .95), (7, 67, 1, .62), (8, 69, 1, .72),
          (9, 72, 2, .98), (11, 71, 1, .6), (12, 69, 2, .9)],
    # D with a stuttering 32nd-note tail
    "Ds": [(0, 71, 1, 1.0), (1, 69, 1, .6), (2, 67, 1, .7), (3, 65, 2, 1.0), (6, 67, 1, .8), (7, 65, 1, .6),
           (8, 64, 2, 1.0)] + [(12 + k * 0.5, 64 + (12 if k % 4 == 3 else 0), 0.5, .85 + .05 * (k % 2)) for k in range(8)],
    # final-drop cross-rhythm: 3-step cells against the 4/4 grid
    "S": [(0, 64, 1, 1.0), (1, 65, 1, .7), (3, 64, 1, 1.0), (4, 65, 1, .7), (6, 64, 1, 1.0), (7, 67, 1, .75),
          (9, 64, 1, 1.0), (10, 69, 1, .8), (12, 71, 2, 1.0)],
    # Phrygian-dominant (Hijaz) surprise
    "H1": [(0, 64, 2, 1.0), (3, 65, 2, .92), (6, 68, 1, 1.0), (7, 65, 1, .62), (8, 64, 1, .72),
           (9, 68, 2, 1.0), (11, 69, 1, .7), (12, 71, 2, 1.0)],
    "H2": [(0, 72, 1, 1.0), (1, 71, 1, .7), (2, 69, 1, .75), (3, 68, 2, 1.0), (6, 65, 1, .8), (7, 68, 1, .7),
           (8, 64, 3, 1.0)],
}
RESP = {"A": [(14, "HEY")], "B": [(14, "HO")], "C": [(14, "HEY")], "D": [(10, "HA"), (12, "HA"), (14, "HO")],
        "V": [(14, "HEY")], "Ds": [(10, "HA")], "S": [(2, "HA"), (5, "HA"), (8, "HA"), (11, "HA"), (14, "HEY")],
        "H1": [(14, "HEY")], "H2": []}
CHANT_F0 = {"HEY": 196.0, "HO": 123.47, "HA": 164.81, "HUH": 130.0}


def play_hook(bar, pat, layers, oct_=0, gains=None, tag="hook"):
    gains = gains or {}
    for (st, m, ln, v) in HOOK[pat]:
        t = T(bar, st)
        dur = ln * STEP * 0.9
        mm = m + 12 * oct_
        if "bz" in layers:
            g = gains.get("bz", 1.0)
            M.add("bz", I.bouzouki(mm, dur, v, seed=int(RNG.integers(1e9))), t + hum(1.0), g * v, -0.32)
            M.add("bz", I.bouzouki(mm, dur, v * 0.95, seed=int(RNG.integers(1e9))), t + 0.007 + hum(1.5), g * v * 0.9, 0.34)
        if "bzi" in layers:   # intro teaser: separate dark, distant bus (voice-over space)
            M.add("bzi", I.bouzouki(mm, dur, v, seed=int(RNG.integers(1e9))), t + hum(1.0), gains.get("bzi", 1.0) * v, -0.2)
        if "bzlow" in layers:
            M.add("bz", I.bouzouki(mm - 12, dur, v, seed=int(RNG.integers(1e9))), t + hum(1.0), gains.get("bzlow", .6) * v, 0.0)
        if "aul" in layers:
            grace = up_step(mm) if (ln >= 2 and v >= 0.9 and RNG.random() < 0.6) else None
            M.add("aul", I.aulos(mm, dur * 1.05, v, seed=int(RNG.integers(1e9)), grace=grace), t, gains.get("aul", 1.0) * v, 0.12)
        if "aul8" in layers:
            M.add("aul", I.aulos(mm + 12, dur, v, seed=int(RNG.integers(1e9))), t, gains.get("aul8", 0.5) * v, -0.15)
        if "pl" in layers:
            M.add("pl", I.pluck_synth(mm, dur, v, seed=0), t, gains.get("pl", 1.0) * v, 0.0)
        if "ss" in layers:
            M.add("ss", I.supersaw(mm + 12, dur, v), t, gains.get("ss", 1.0) * v)
        if "chop" in layers and v >= 0.95 and ln >= 1:
            ch = V.vocal_chop(mm + 12, min(dur, STEP * 1.2), vowel="ah", seed=int(RNG.integers(1e9)))
            M.add("chop", ch, t, gains.get("chop", 1.0), RNG.uniform(-0.4, 0.4))
        if v >= 0.95:
            ev(t, "melodic_accent", f"{tag}_{pat}", midi=int(mm), velocity=v)
    ev(T(bar, 0), "hook_phrase", f"{tag}_{pat}", bar=bar)


def chant(bar, step, name, size=8, g=1.0, effort=1.0, f0=None, fifth=0.0, cat="male_chant"):
    t = T(bar, step)
    f = f0 or CHANT_F0[name]
    x = V.gang(name, f, n_voices=size, effort=effort, fifth=fifth, seed=int(RNG.integers(1e9)))
    M.add("vox", x, t - 0.045 + 0.012, g)   # 'H' onset is pre-roll: vowel lands on the grid
    ev(t, cat, name, voices=size)


def responses(bar, pat, size=8, g=1.0):
    for st, nm in RESP.get(pat, []):
        chant(bar, st, nm, size=size, g=g)


# =============================================================================
# DRUM PATTERNS
# =============================================================================
KICK_MAIN = I.kick("main", 1)
KICK_LONG = I.kick("long", 2)
KICK_FILT = lp(lp(I.kick("main", 3), 260), 260)
CLAP = [I.clap(s) for s in range(3)]
HAT_C = [I.hat(False, s) for s in range(4)]
HAT_O = [I.hat(True, s) for s in range(3)]
SHAK = [I.shaker(s) for s in range(4)]
DRB = {k: [I.darbuka(k, s) for s in range(3)] for k in "DTK"}
DAVUL = [I.davul(s) for s in range(2)]
TOMS = [I.tom(f, s) for s, f in enumerate([98, 123, 147, 165])]
TICKS = {f: [I.metal_tick(f, s) for s in range(2)] for f in (987.77, 1318.5, 1174.7)}
HEART = I.heartbeat(0)


def k_(bar, step, g=1.0, kind="main"):
    t = T(bar, step)
    if kind == "filt":
        M.add("perc", KICK_FILT, t, g * 0.9)
        ev(t, "pulse", "filtered_kick")
        return
    M.add("kick", KICK_MAIN if kind == "main" else KICK_LONG, t, g)
    KICKS.append(t)


def hats(bar, lvl=1.0, closed=True, open_=True, steps=range(16)):
    for s in steps:
        if open_ and s % 4 == 2:
            M.add("hats", HAT_O[s % 3], T(bar, s) + hum(), 0.55 * lvl * RNG.uniform(.9, 1), 0.18)
        elif closed:
            v = [0.55, 0.28, 0.0, 0.36][s % 4]
            if v > 0:
                M.add("hats", HAT_C[s % 4], T(bar, s) + hum(), v * lvl * RNG.uniform(.8, 1.05), -0.22)


def shaker(bar, lvl=1.0, steps=range(16)):
    for s in steps:
        v = [0.9, 0.45, 0.7, 0.5][s % 4] * RNG.uniform(0.8, 1.05)
        M.add("perc", SHAK[s % 4], T(bar, s) + hum(2.0), 0.22 * v * lvl, 0.45 if s % 2 else 0.3)


def darbuka(bar, lvl=1.0, busy=0):
    pat = [(0, "D", 1.0), (2, "T", .8), (6, "T", .75), (8, "D", .95), (12, "T", .85)]
    if busy >= 1:
        pat += [(3, "K", .4), (5, "K", .35), (10, "T", .5), (11, "K", .4), (14, "T", .6), (15, "K", .45)]
    if busy >= 2:
        pat += [(1, "K", .3), (7, "K", .35), (9, "K", .3), (13, "K", .4)]
    for s, k, v in pat:
        M.add("perc", DRB[k][int(RNG.integers(3))], T(bar, s) + hum(1.8), 0.5 * v * lvl * RNG.uniform(.85, 1.05),
              -0.35 if k != "D" else -0.1)


def metal_ticks(bar, lvl=1.0, dense=False):
    pat = [3, 6, 10, 13] if bar % 2 == 0 else [3, 6, 11, 14, 15]
    if dense:
        pat = sorted(set(pat + [1, 9]))
    for i, s in enumerate(pat):
        f = (1318.5, 987.77, 1174.7)[i % 3]
        M.add("metal", TICKS[f][i % 2], T(bar, s) + hum(1.0), 0.32 * lvl * RNG.uniform(.85, 1.05), (0.55, -0.55)[i % 2])


def clap(bar, lvl=1.0):
    for s in (4, 12):
        M.add("perc", CLAP[int(RNG.integers(3))], T(bar, s) + hum(1.0), 0.62 * lvl, 0.03)


def snare_roll(bar, start=0, lvl=1.0, density=(2, 1, 0.5)):
    """accelerating clap/tek roll across a bar"""
    pos = []
    s = start
    while s < 16:
        frac = s / 16
        d = density[0] if frac < 0.5 else (density[1] if frac < 0.8 else density[2])
        pos.append(s)
        s += d
    for i, s in enumerate(pos):
        v = 0.25 + 0.75 * (s / 16) ** 1.5
        M.add("perc", CLAP[i % 3], T(bar, s) if s == int(s) else (bar * 16 + s) * STEP, 0.45 * v * lvl, RNG.uniform(-.2, .2))
    ev(T(bar, start), "transition_sfx", "snare_roll")


def tom_fill(bar, steps=(12, 13, 14, 15), lvl=1.0):
    for i, s in enumerate(steps):
        M.add("perc", TOMS[3 - (i % 4)], T(bar, s) + hum(), 0.55 * lvl, (-.5, -.15, .15, .5)[i % 4])
    ev(T(bar, steps[0]), "transition_sfx", "tom_fill")


def davul(bar, steps, lvl=1.0):
    for s in steps:
        M.add("perc", DAVUL[s % 2], T(bar, s) + hum(), 0.55 * lvl, 0.0)
        ev(T(bar, s), "tribal_drum", "davul")


# =============================================================================
# BASS
# =============================================================================
GROOVE_BASS = [(2, 0, 1, 1), (3, 0, 1, .75), (6, 0, 1, 1), (7, 0, 1, .75), (10, 0, 1, 1), (11, 0, 1, .75),
               (14, 0, 1, 1), (15, 12, 1, .6)]
DROP_BASS = [(2, 0, 1, 1), (3, 0, 1, .8), (5, 12, 1, .7), (6, 0, 1, 1), (7, 0, 1, .75), (9, 7, 1, .65),
             (10, 0, 1, 1), (11, 0, 1, .8), (13, 12, 1, .7), (14, 0, 1, 1), (15, 1, 1, .8)]
DARK_BASS = [(2, 0, 2, .8), (6, 0, 1, .6), (10, 0, 2, .8), (14, 0, 1, .6)]


def bassline(bar, root, pat, kind, lvl=1.0, until=16):
    for s, off, ln, v in pat:
        if s >= until:
            continue
        o = off
        if off == 1 and root != E1:   # the b2 grit only on E
            o = 0
        m = root + o
        sub, mid = I.bass_note(m, ln * STEP * 0.92, kind=kind, vel=v)
        t = T(bar, s)
        M.add("sub", sub, t, 0.95 * v * lvl)
        M.add("bmid", mid, t, (1.5 if kind == "groove" else 0.75) * v * lvl)


def bass_impact(t, midi=E1, length=1.2, g=1.0):
    n = int(length * SR)
    tt = np.arange(n) / SR
    f = mtof(midi) * (1 + 1.2 * np.exp(-tt / 0.05))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.45) * np.minimum(tt / 0.002, 1)
    y = softclip(y * 1.5, 1.0)
    M.add("sub", y, t, 0.9 * g)
    M.add("bmid", hp(softclip(y * 5, 1.0), 90) * 0.3, t, g)
    ev(t, "bass_impact", "sub_drop", midi=midi)


# =============================================================================
# FX helpers
# =============================================================================
HALL = make_ir(3.2, 2.6, 1.4, 4.0, predelay_ms=22, seed=1, bright=7000)
DARK_HALL = make_ir(5.5, 4.5, 1.8, 6.0, predelay_ms=40, seed=2, bright=4200)
PLATE = make_ir(1.6, 1.5, 1.1, 2.0, predelay_ms=8, seed=3, bright=11000)
ROOM = make_ir(0.55, 0.5, 0.35, 0.8, predelay_ms=3, er_density=24, seed=4, bright=9000)


def impact(t, size=1.0, nominal=164.81, name="metal_impact", g=1.0):
    x = I.metal_impact(seed=int(RNG.integers(1e6)), nominal=nominal, size=size)
    M.add("impact", x, t, 0.95 * g)
    ev(t, "metallic_impact", name, size=size)


def bell(t, nominal=329.63, g=1.0, name="bronze_bell"):
    x = I.bronze_bell(nominal, 5.0, seed=int(RNG.integers(1e6)))
    M.add("impact", x, t, 0.6 * g, 0.0)
    ev(t, "metallic_impact", name, nominal_hz=nominal)


def clank(t, f=740.0, g=1.0, p=0.0):
    x = I.anvil(f, 0.9, seed=int(RNG.integers(1e6)), decay=0.25)
    M.add("metal", x, t, 0.5 * g, p)
    ev(t, "metallic_impact", "clank", freq=f)


def boom(t, g=1.0):
    M.add("impact", I.boom(2.4, seed=int(RNG.integers(1e6))), t, 0.8 * g)
    ev(t, "cinematic_boom", "boom")


def rev_metal(t_end, length=1.2, g=1.0):
    x = I.metal_impact(seed=int(RNG.integers(1e6)), size=0.3)
    wet = convolve_st(to_st(x[: int(2.5 * SR)]), HALL)
    st = to_st(x[: wet.shape[1]]) * 0.6 + wet
    n = int(length * SR)
    st = st[:, :n][:, ::-1].copy()
    st *= np.linspace(0, 1, n) ** 2.2
    M.add_ending_at("fx", st / (np.max(np.abs(st)) + 1e-9), t_end, 0.75 * g)
    ev(t_end - length, "transition_sfx", "reverse_metal_sweep", end=round(t_end, 4))


def whoosh(t_end, length=BEAT, up=True, g=1.0):
    x = I.whoosh(length, up=up, seed=int(RNG.integers(1e6)))
    if up:
        M.add_ending_at("fx", x, t_end, 0.42 * g)
        ev(t_end - length, "transition_sfx", "whoosh_up", end=round(t_end, 4))
    else:
        M.add("fx", x, t_end, 0.38 * g)
        ev(t_end, "transition_sfx", "whoosh_down")


def riser(t_end, length, g=1.0):
    x = I.riser(length, seed=int(RNG.integers(1e6)))
    M.add_ending_at("fx", x, t_end, 0.3 * g)
    ev(t_end - length, "transition_sfx", "riser", end=round(t_end, 4))


def roar(t, dur=0.9, g=1.0, p=0.0, reverse=False, name="bull_roar"):
    x = V.bull_roar(dur, seed=int(RNG.integers(1e6)))
    if reverse:
        x = np.pad(x, (0, int(1.6 * SR)))
        wet = convolve_st(to_st(x), HALL)
        st = (to_st(x) * 0.5 + wet)[:, ::-1].copy()
        st = st / (np.max(np.abs(st)) + 1e-9)
        st *= np.linspace(0, 1, st.shape[1]) ** 1.5
        M.add_ending_at("horror", st, t, 0.8 * g)
        ev(t - st.shape[1] / SR, "horror_vocal", "reverse_bull_roar", end=round(t, 4))
    else:
        M.add("horror", x, t, g, p)
        ev(t, "horror_vocal", name, duration=dur)


def scream(t, dur=0.5, g=1.0, p=0.0, reverse=False, f0=None, name="distant_shriek"):
    f0 = f0 or RNG.uniform(400, 480)
    x = V.shriek(dur, f0=f0, seed=int(RNG.integers(1e6)))
    if reverse:
        x = np.pad(x, (0, int(2.2 * SR)))
        wet = convolve_st(to_st(x), DARK_HALL)[:, : int(2.2 * SR)]
        st = (to_st(x)[:, : wet.shape[1]] * 0.4 + wet)[:, ::-1].copy()
        st = st / (np.max(np.abs(st)) + 1e-9)
        st *= np.linspace(0, 1, st.shape[1]) ** 2.0
        M.add_ending_at("horror", st, t, 0.65 * g)
        ev(t - st.shape[1] / SR, "horror_vocal", "reverse_shriek", end=round(t, 4))
    else:
        M.add("horror", x, t, 0.8 * g, p)
        ev(t, "horror_vocal", name, duration=dur)


def stutter_scream(bar, step, reps=3, g=1.0):
    x = V.shriek(0.35, f0=520, seed=int(RNG.integers(1e6)))
    chop = fade(x[: int(STEP * 0.8 * SR)], 0.002, 0.01)
    for k in range(reps):
        M.add("horror", chop * (0.9 ** k), T(bar, step + k), 0.7 * g, (-0.5, 0.5, 0.0)[k % 3])
    ev(T(bar, step), "horror_vocal", "stutter_scream_chop", repeats=reps)


def breaths(bar, steps, g=1.0):
    for i, s in enumerate(steps):
        kind = "out" if i % 2 == 0 else "in"
        x = V.breath(kind, 0.12 if kind == "out" else 0.09, tract=RNG.uniform(0.92, 1.05))
        M.add("vox", x, T(bar, s), (0.35 if kind == "out" else 0.22) * g, RNG.uniform(-0.5, 0.5))
    ev(T(bar, steps[0]), "male_chant", "rhythmic_breathing", count=len(steps))


def choir_hit(bar, step, notes=(52, 59, 64), name="OH", g=1.0, dur_mul=0.7):
    x = V.choir(name, list(notes), per_note=3, dur_mul=dur_mul, seed=int(RNG.integers(1e6)))
    M.add("vox", x, T(bar, step), 0.55 * g)
    ev(T(bar, step), "choir_accent", name, notes=list(notes))


SILENCES = []    # (t0, t1) - full mix silence
BREAKS = []      # (t0, t1) - music muted, vocals/fx keep going


def silence(t0, t1):
    SILENCES.append((t0, t1))
    ev(t0, "silence", "full_silence", end=round(t1, 4), duration=round(t1 - t0, 4))


def brk(t0, t1):
    BREAKS.append((t0, t1))
    ev(t0, "pause", "rhythmic_break", end=round(t1, 4), duration=round(t1 - t0, 4))


# =============================================================================
# ARRANGEMENT
# =============================================================================
def arrange():
    # ---------------- beds that span the track ----------------
    fire = I.fire_bed(N, seed=11)
    fire_lvl = np.interp(np.arange(N) / SR,
                         [0, 3.5, 14, 24.7, 26.4, 40.6, 41, 47.6, 58.2, 60],
                         [0.55, 0.35, 0.3, 0.45, 0.7, 0.35, 0.85, 0.9, 0.4, 0.6])
    M.bus("fire")[:] += fire * fire_lvl * 0.5

    drone = I.drone_resonance(N, root=E1, seed=5)
    dlev = np.interp(np.arange(N) / SR, [0, 3.5, 4, 24.7, 26.4, 26.5, 40.6, 47.0, 47.6, 58.2, 60],
                     [0.6, 0.6, 0.15, 0.3, 0.8, 0.12, 0.85, 0.9, 0.15, 0.4, 0.6])
    M.bus("drone")[:] += drone * dlev * 0.45

    # ================= INTRO (bars 0-1) =================
    impact(0.0, size=0.8, nominal=164.81, name="opening_bronze_impact")
    bell(0.0, 329.63, g=0.8, name="opening_bell")
    roar(0.05, dur=1.1, g=0.32, p=-0.2, name="distant_bull_roar_intro")
    for b in (0, 1):
        for s in (0, 4, 8, 12):
            k_(b, s, g=0.95 if s == 0 else 0.75, kind="filt")
        shaker(b, 0.55)
        hats(b, 0.35, closed=True, open_=False)
    for s in (14,):
        k_(1, s, 0.6, kind="filt")
    # melodic teaser: bouzouki states the hook through a dark filter + echo, aulos answers
    play_hook(0, "A", ["bzi"], gains={"bzi": 0.9}, tag="teaser")
    play_hook(1, "C", ["bzi", "aul"], gains={"bzi": 0.85, "aul": 0.3}, tag="teaser")
    breaths(1, [14, 15], g=0.8)
    clank(T(1, 6), 740, 0.6, 0.4)
    scream(T(2, 0), g=0.55, reverse=True)
    whoosh(T(2, 0), BEAT * 2, up=True)

    # ================= GROOVE (bars 2-7) =================
    gpats = ["A", "B", "C", "D", "A", "B"]
    for i, b in enumerate(range(2, 8)):
        for s in (0, 4, 8, 12):
            k_(b, s, 0.95 if s == 0 else 0.88)
        hats(b, 0.55 + 0.08 * i, closed=True, open_=i >= 1)
        shaker(b, 0.6 + 0.04 * i)
        darbuka(b, 0.8, busy=0 if i < 3 else 1)
        if i >= 2:
            clap(b, 0.75 + 0.05 * i)
        if i >= 3:
            metal_ticks(b, 0.6)
        root = [E1, E1, F1, E1, E1, E1][i]
        bassline(b, root, GROOVE_BASS, "groove", 0.8 + 0.03 * i)
        layers = ["bz", "pl"] + (["aul"] if i >= 2 else [])
        play_hook(b, gpats[i], layers, gains={"bz": 0.8, "pl": 0.55, "aul": 0.55})
        responses(b, gpats[i], size=5 + i // 2, g=0.75)
    bass_impact(T(2, 0), E1, 0.8, 0.8)
    impact(T(2, 0), size=0.6, name="groove_entry_impact", g=0.7)
    clank(T(4, 0), 659.25, 0.7, -0.3)
    clank(T(6, 0), 740, 0.7, 0.3)
    tom_fill(7, (12, 13, 14, 15), 0.9)
    whoosh(T(8, 0), BEAT, up=True)

    # ================= ESCALATION (bars 8-13) =================
    epats = ["A", "B", "V", "C", "A", "D"]
    for i, b in enumerate(range(8, 14)):
        until = 16
        if b == 9:
            until = 12
        if b == 11:
            until = 14
        for s in (0, 4, 8, 12):
            if s < until:
                k_(b, s, 1.0 if s == 0 else 0.94)
        hats(b, 0.95)
        shaker(b, 0.8)
        darbuka(b, 1.0, busy=1 if i < 4 else 2)
        clap(b, 1.0)
        metal_ticks(b, 0.85, dense=i >= 3)
        davul(b, [7, 10] if i % 2 == 0 else [3, 10], 0.75)
        root = [E1, E1, F1, E1, E1, D2 - 12][i]
        bassline(b, root, GROOVE_BASS if i < 3 else DROP_BASS, "groove", 1.0, until=until)
        lay = ["bz", "pl", "aul"] + (["aul8"] if i in (2, 4) else []) + (["chop"] if i >= 3 else [])
        play_hook(b, epats[i], lay, gains={"bz": 0.9, "pl": 0.55, "aul": 0.7, "aul8": 0.35, "chop": 0.45})
        if b not in (9, 11):
            responses(b, epats[i], size=8, g=0.78)
        if i >= 4:
            breaths(b, [2, 6, 10], g=0.7)
    # pad enters for width
    pad = I.dark_pad([40, 47, 52], 6 * BAR + 0.5, seed=3)
    M.add("pad", pad, T(8, 0), 0.22)
    # break 1: bar 9 beat 4 drops out -> "HO!" + clank
    brk(T(9, 12), T(10, 0))
    chant(9, 12, "HO", size=10, g=1.0, effort=1.1)
    clank(T(9, 12), 523.25, 1.0, 0.0)
    whoosh(T(10, 0), BEAT, up=True, g=0.8)
    # break 2: bar 11 last 8th -> distant shriek + bronze tick
    brk(T(11, 14), T(12, 0))
    scream(T(11, 14), dur=0.45, g=0.55, p=0.5, name="distant_shriek_break")
    clank(T(11, 14), 987.77, 0.6, -0.4)
    # build into pre-drop
    snare_roll(13, 8, 0.9, density=(1, 1, 0.5))
    riser(T(15, 0), BAR * 2)
    tom_fill(13, (14, 14.5, 15, 15.5), 0.7)

    # ================= PRE-DROP (bar 14) =================
    b = 14
    impact(T(b, 0), size=0.75, name="predrop_impact")
    bass_impact(T(b, 0), E1, 1.3, 1.0)
    roar(T(b, 0) + 0.01, dur=0.95, g=0.75, p=0.0, name="bronze_bull_roar_predrop")
    # hook fragment, thin and filtered (no drums) + breathing tension
    for (st, m, ln, v) in HOOK["A"][:5]:
        t = T(b, st)
        M.add("bz", lp(I.bouzouki(m, ln * STEP * 0.9, v, seed=int(RNG.integers(1e9))), 1800), t, 0.7 * v, 0.0)
    breaths(b, [4, 5, 6, 7, 8, 9, 10, 11], g=0.9)
    for s in range(0, 12, 2):
        M.add("perc", SHAK[s % 4], T(b, s), 0.2)
    rev_metal(T(b, 12), length=BEAT * 1.6, g=1.0)
    scream(T(b, 12), g=0.6, reverse=True)
    chant(b, 12, "HEY", size=12, g=1.25, effort=1.2, fifth=0.3, cat="power_vocal_accent")
    choir_hit(b, 12, notes=(52, 59, 64, 71), name="AH", g=0.6, dur_mul=0.5)
    silence(T(b, 14.25), T(15, 0))

    # ================= MAIN DROP (bars 15-22) =================
    dpats = ["A", "B", "C", "D", "A", "B", "C", "Ds"]
    roots = [E1, E1, F1, D2 - 12, E1, E1, F1, D2 - 12]
    for i, b in enumerate(range(15, 23)):
        until = 12 if b == 18 else 16
        for s in (0, 4, 8, 12):
            if s < until:
                k_(b, s, 1.0)
        hats(b, 1.0)
        shaker(b, 0.85)
        darbuka(b, 1.05, busy=2 if i >= 4 else 1)
        clap(b, 1.05)
        metal_ticks(b, 1.0, dense=True)
        davul(b, [7, 10], 0.8)
        bassline(b, roots[i], DROP_BASS, "drop", 1.05, until=until)
        lay = ["bz", "pl", "aul"]
        if i >= 4:
            lay += ["ss", "chop"]
        play_hook(b, dpats[i], lay, gains={"bz": 1.0, "pl": 0.75, "aul": 0.75, "ss": 0.55, "chop": 0.6})
        if b != 18:
            responses(b, dpats[i], size=9, g=1.0)
        if i % 2 == 1:
            breaths(b, [2, 6], g=0.55)
    impact(T(15, 0), size=1.1, name="drop1_impact")
    bass_impact(T(15, 0), E1, 1.0, 1.0)
    choir_hit(15, 0, name="OH", g=0.8)
    boom(T(15, 0), 0.8)
    # break before second half: bronze roar
    brk(T(18, 12), T(19, 0))
    roar(T(18, 12), dur=0.55, g=0.7, p=0.15, name="bull_roar_break")
    chant(18, 14, "HO", size=10, g=0.9)
    impact(T(19, 0), size=0.9, name="drop1_half_impact")
    scream(T(19, 0) + 0.02, dur=0.55, g=0.45, p=-0.55, name="distant_shriek_with_impact")
    choir_hit(19, 0, name="OH", notes=(52, 59, 64), g=0.7)
    # unexpected eerie echo between phrases
    scream(T(21, 4), dur=0.35, g=0.75, p=0.7, f0=360, name="eerie_echo_shriek")
    clank(T(17, 0), 659.25, 0.8, 0.4)
    clank(T(21, 0), 740, 0.8, -0.4)
    whoosh(T(23, 0), BEAT * 1.0, up=True)
    tom_fill(22, (14, 14.5, 15, 15.5), 0.6)

    # ================= DARK BREAKDOWN (bars 23-26) =================
    impact(T(23, 0), size=1.0, nominal=110.0, name="breakdown_bronze_impact")
    bell(T(23, 0), 164.81, 0.9, name="breakdown_deep_bell")
    whoosh(T(23, 0), BEAT * 2, up=False)
    # heartbeat accelerating
    hb = [(23, 0), (23, 8), (24, 0), (24, 8), (25, 0), (25, 4), (25, 8), (25, 12),
          (26, 0), (26, 4), (26, 8), (26, 10), (26, 12)]
    for b, s in hb:
        M.add("heart", HEART, T(b, s), 0.95)
        ev(T(b, s), "heartbeat", "lub_dub")
    for b in range(23, 27):
        shaker(b, 0.55)
        hats(b, 0.4, closed=True, open_=(b >= 25))
        darbuka(b, 0.5, busy=0)
        bassline(b, E1, DARK_BASS, "dark", 0.75, until=14 if b == 26 else 16)
        metal_ticks(b, 0.45)
    # transformed melody: half-time, low aulos with ornaments + bouzouki tremolo
    for half, (b0, pat) in enumerate(((23, "A"), (25, "C"))):
        for (st, m, ln, v) in HOOK[pat]:
            s2 = st * 2
            bb = b0 + int(s2 // 16)
            ss = s2 % 16
            t = T(bb, ss)
            dur = ln * 2 * STEP * 0.95
            M.add("aul", I.aulos(m - 12, dur, v, seed=int(RNG.integers(1e9)), grace=up_step(m - 12) if ln >= 2 else None),
                  t, 0.85 * v, 0.1)
            if ln >= 2:
                M.add("bz", I.bouzouki(m, dur, v * 0.7, seed=int(RNG.integers(1e9)), tremolo=True), t, 0.45, -0.3)
            if v >= 0.95:
                ev(t, "melodic_accent", f"breakdown_{pat}", midi=int(m - 12))
        ev(T(b0, 0), "hook_phrase", f"breakdown_halftime_{pat}", bar=b0)
    oo = V.choir("OO", [40, 47, 52], per_note=3, dur_mul=4.0, seed=7)
    M.add("vox", oo, T(23, 0), 0.2)
    oo2 = V.choir("OO", [41, 48, 53], per_note=3, dur_mul=4.0, seed=8)
    M.add("vox", oo2, T(25, 0), 0.2)
    ev(T(23, 0), "choir_accent", "low_oo_pad")
    scream(T(24, 4), dur=0.6, g=0.38, p=-0.6, name="distant_shriek_breakdown")
    roar(T(25, 8), dur=0.8, g=0.35, p=0.3, name="distant_bull_moan")
    breaths(24, [8, 10, 12, 14], 0.6)
    # build
    for s in (0, 4, 8, 10, 12):
        chant(26, s, "HA", size=7, g=0.75 + 0.03 * s)
    snare_roll(26, 0, 0.95, density=(2, 1, 0.5))
    for s in (8, 10, 12, 13):
        k_(26, s, 0.75)
    riser(T(26, 14), BAR * 1.75)
    roar(T(27, 0) - 0.12, reverse=True, g=0.8)
    silence(T(26, 14), T(27, 0) - 0.12)

    # ================= FINAL DROP (bars 27-32) =================
    fpats = ["A", "B", "C", "S", "H1", "H2"]
    roots = [E1, E1, F1, D2 - 12, E1, F1]
    for i, b in enumerate(range(27, 33)):
        until = 12 if b == 32 else 16
        for s in (0, 4, 8, 12):
            if s < until:
                k_(b, s, 1.0)
        hats(b, 1.05, steps=range(until))
        shaker(b, 0.95, steps=range(until))
        darbuka(b, 1.1, busy=2)
        if until == 16:
            clap(b, 1.1)
        else:
            M.add("perc", CLAP[0], T(b, 4), 0.68)
        metal_ticks(b, 1.1, dense=True)
        davul(b, [3, 7, 10] if i % 2 else [7, 10, 11], 0.9)
        bassline(b, roots[i], DROP_BASS, "final", 1.1, until=until)
        lay = ["bz", "bzlow", "pl", "aul", "aul8", "ss", "chop"]
        play_hook(b, fpats[i], lay, gains={"bz": 1.0, "bzlow": 0.45, "pl": 0.8, "aul": 0.75, "aul8": 0.35,
                                           "ss": 0.65, "chop": 0.65}, tag="final")
        responses(b, fpats[i], size=12, g=1.1)
    impact(T(27, 0), size=1.25, name="final_drop_impact")
    bell(T(27, 0), 329.63, 0.9)
    bass_impact(T(27, 0), E1, 1.2, 1.1)
    boom(T(27, 0), 1.0)
    roar(T(27, 0) + 0.02, dur=0.7, g=0.95, p=-0.1, name="bronze_bull_roar_final_drop")
    choir_hit(27, 0, notes=(40, 52, 59, 64), name="OH", g=0.9)
    choir_hit(29, 0, notes=(41, 53, 60, 65), name="OH", g=0.75)
    choir_hit(31, 0, notes=(40, 52, 56, 64), name="AH", g=0.85)      # E major colour (G#)
    clank(T(29, 0), 659.25, 0.9, 0.35)
    impact(T(31, 0), size=0.9, name="hijaz_turn_impact")
    stutter_scream(29, 6, reps=3, g=1.35)
    for b in (28, 30):
        tom_fill(b, (12, 13, 14, 15), 0.8)
    # finale of the drop: roar + shriek + gang HEY, then a 16th of silence
    roar(T(32, 12), dur=0.6, g=0.8, p=0.0, name="final_bronze_bull_roar")
    scream(T(32, 12) + 0.03, dur=0.4, g=0.5, p=0.6, name="final_shriek")
    chant(32, 12, "HEY", size=14, g=1.25, effort=1.25, fifth=0.3, cat="power_vocal_accent")
    rev_metal(T(32, 12), BEAT * 1.4, g=0.8)
    silence(T(32, 14.75), T(33, 0))

    # ================= FINAL IMPACT / LOOP LINK (bar 33) =================
    b = 33
    impact(T(b, 0), size=1.4, nominal=164.81, name="final_metallic_impact")
    bell(T(b, 0), 329.63, 1.0, name="final_bell")
    bass_impact(T(b, 0), E1, 1.6, 1.15)
    boom(T(b, 0), 1.1)
    k_(b, 0, 1.0, kind="long")
    chant(b, 0, "HO", size=14, g=1.2, effort=1.2, cat="power_vocal_accent")
    choir_hit(b, 0, notes=(40, 52, 59, 64), name="OH", g=0.9, dur_mul=1.0)
    for s in (4, 8, 12):
        k_(b, s, 0.85, kind="filt")
    shaker(b, 0.5, steps=range(4, 16))
    # the teaser motif returns -> seamless loop back to bar 0
    for (st, m, ln, v) in HOOK["A"][:5]:
        if st >= 3:
            M.add("bz", I.bouzouki(m, ln * STEP * 0.9, v, seed=int(RNG.integers(1e9))), T(b, st + 4), 0.5 * v, 0.0)
    ev(T(b, 7), "hook_phrase", "loop_teaser", bar=b)
    rev_metal(60.0, BEAT * 2.2, g=0.85)
    whoosh(60.0, BEAT, up=True, g=0.7)


# =============================================================================
# MIX
# =============================================================================
MUSIC_BUSES = ["kick", "perc", "hats", "metal", "sub", "bmid", "bz", "aul", "pl", "ss", "chop", "pad", "drone", "fire"]


def gate_env(spans, ramp=0.003, floor=0.0):
    g = np.ones(N)
    r = int(ramp * SR)
    for t0, t1 in spans:
        a, b = int(round(t0 * SR)), int(round(t1 * SR))
        g[a:b] = np.minimum(g[a:b], floor)
        if a - r > 0:
            g[a - r:a] = np.minimum(g[a - r:a], np.linspace(1, floor, r))
        if b + r < N:
            g[b:b + r] = np.minimum(g[b:b + r], np.linspace(floor, 1, r))
    return g


def mix(levels=None, report=False):
    L = dict(kick=1.0, rumble=0.42, sub=0.85, bmid=0.66, perc=0.8, hats=0.6, metal=0.75, bz=1.0, aul=0.4,
             pl=0.8, ss=0.8, chop=0.36, vox=1.2, horror=0.65, impact=0.55, fx=0.5, fire=0.13, drone=0.22,
             pad=0.4, heart=0.5, bzi=1.0)
    if levels:
        L.update(levels)
    B = M.b
    for k in L:
        M.bus(k)
    kick_pump = pump_env(N, KICKS, 1.0, 0.17, shape=1.6)
    music_pump = pump_env(N, KICKS, 0.45, 0.24, shape=2.0)
    deep_pump = pump_env(N, KICKS, 0.8, 0.3, shape=1.5)
    lead_pump = pump_env(N, KICKS, 0.22, 0.18, shape=2.0)
    brk_g = gate_env(BREAKS, floor=0.0)

    out = {}
    # --- drums ---
    kick = B["kick"].copy()
    out["kick"] = kick
    # tribal-techno rumble: reverberated kick, low-passed, driven, ducked against the kick
    rum = convolve_st(kick * 0.5, HALL)
    rum = hp(softclip(lp(rum, 160, 4) * 2.4, 1.0), 38)
    rum = (rum[0] + rum[1]) * 0.5
    rum_auto = np.interp(np.arange(N) / SR, [0, T(6, 0), T(6, 0) + 0.01, T(8, 0), T(15, 0), T(23, 0), T(27, 0), 60],
                         [0.0, 0.0, 0.45, 0.55, 1.0, 1.0, 1.1, 1.1])
    out["rumble"] = to_st(rum) * pump_env(N, KICKS, 1.0, 0.3, shape=1.2) * rum_auto
    perc = B["perc"]
    perc, _ = compress(perc, thr=-16, ratio=3, att=0.003, rel=0.08)
    out["perc"] = perc
    out["hats"] = eq(B["hats"], "highshelf", 9000, 0.7, -1.5)
    out["metal"] = B["metal"]
    out["heart"] = B["heart"]
    # --- bass ---
    sub = (B["sub"][0] + B["sub"][1]) * 0.5
    sub = lp(sub, 140, 4)
    out["sub"] = to_st(sub) * kick_pump
    bmid = B["bmid"]
    bmid = eq(bmid, "peak", 220, 1.0, 1.5)      # small-speaker growl
    bmid = eq(bmid, "peak", 900, 1.2, 1.0)
    bmid = widen(bmid, 0.6) * kick_pump
    out["bmid"] = bmid
    # --- melodic ---
    bz, _ = compress(B["bz"], thr=-22, ratio=4, att=0.0008, rel=0.06, knee=6, rms_ms=0.5, makeup=4)
    bz = eq(bz, "peak", 3200, 1.0, 1.5)
    out["bz"] = bz * lead_pump
    aul = eq(B["aul"], "peak", 600, 1.0, -2.0)
    out["aul"] = aul * lead_pump
    out["pl"] = eq(B["pl"], "peak", 400, 1.0, -2.5) * lead_pump
    out["ss"] = B["ss"] * deep_pump
    chop = B["chop"]
    chop = softclip(chop * 1.8, 1.0)
    chop = hp(eq(chop, "peak", 2500, 1.0, 3), 300)
    out["chop"] = chop * lead_pump
    out["pad"] = B["pad"] * deep_pump
    out["drone"] = B["drone"] * deep_pump
    out["fire"] = B["fire"] * (0.4 + 0.6 * deep_pump)
    # --- vocals ---
    vox = hp(B["vox"], 85, 2)
    vox = eq(vox, "peak", 320, 1.0, -2.5)
    vox = eq(vox, "peak", 2900, 0.9, 3.5)
    vox = eq(vox, "highshelf", 9000, 0.7, -2.0)
    vox = softclip(vox * 1.6, 1.0) / 1.2
    vox, _ = compress(vox, thr=-20, ratio=4, att=0.002, rel=0.09, makeup=3)
    out["vox"] = vox
    hor = hp(B["horror"], 70)
    out["horror"] = hor
    out["impact"] = B["impact"]
    bzi, _ = compress(B["bzi"], thr=-22, ratio=4, att=0.0008, rel=0.06, knee=6, rms_ms=0.5, makeup=4)
    out["bzi"] = lp(hp(bzi, 250), 2600, 2) * 0.8
    out["fx"] = B["fx"]

    for k in out:
        out[k] = out[k] * L.get(k, 1.0)
    for k in MUSIC_BUSES + ["rumble", "heart"]:
        if k in out:
            out[k] = out[k] * brk_g

    # --- section trim automation: groove sits back, escalation crescendos into the pre-drop ---
    tt = np.arange(N) / SR
    trim = np.interp(tt, [0, T(2, 0) - 0.01, T(2, 0), T(8, 0) - 0.01, T(8, 0), T(14, 0), 60],
                     [1.0, 1.0, 0.82, 0.88, 0.8, 1.0, 1.0])
    for k in out:
        if k not in ("impact", "fx", "horror"):
            out[k] = out[k] * trim
    # --- sends ---
    plate_send = 0.22 * out["bz"] + 0.12 * out["pl"] + 0.28 * out["aul"] + 0.2 * out["vox"] + 0.35 * out["chop"] + 0.15 * out["perc"] + 0.3 * out["metal"]
    hall_send = 0.6 * out["bzi"] + 0.18 * out["bz"] + 0.3 * out["aul"] + 0.22 * out["vox"] + 0.4 * out["impact"] + 0.3 * out["pad"] + 0.15 * out["ss"] + 0.25 * out["fx"]
    room_send = 0.3 * out["vox"] + 0.25 * out["perc"] + 0.2 * out["hats"]
    dark_send = 0.95 * out["horror"] + 0.12 * out["vox"]
    rv_plate = hp(convolve_st(plate_send, PLATE), 250) * music_pump
    rv_hall = hp(convolve_st(hall_send, HALL), 200) * (0.5 + 0.5 * music_pump)
    rv_room = hp(convolve_st(room_send, ROOM), 150)
    rv_dark = hp(convolve_st(dark_send, DARK_HALL), 150)
    dly_lead = pingpong(out["bz"] * 0.5 + out["aul"] * 0.4 + out["bzi"] * 1.2, STEP * 3, 0.42, n_taps=5, lp_f=4500) * music_pump
    dly_hor = pingpong(out["horror"], STEP * 3, 0.5, n_taps=6, lp_f=3500, hp_f=400)
    out["rv_plate"] = rv_plate * 0.55
    out["rv_hall"] = rv_hall * 0.5
    out["rv_room"] = rv_room * 0.4
    out["rv_dark"] = rv_dark * 0.55
    out["dly_lead"] = dly_lead * 0.28
    out["dly_hor"] = dly_hor * 0.35
    # horror dry signal is kept low -> distant
    out["horror"] = out["horror"] * 0.8

    mixsum = sum(out.values())
    mixsum = mixsum * gate_env(SILENCES, ramp=0.002, floor=0.0)
    return mixsum, out


# =============================================================================
# MASTER
# =============================================================================
def master(x, target_lufs=-14.0, tp_ceiling=-1.0):
    x = hp(x, 24, 2)
    # mono below 110 Hz (tight, controlled sub)
    low, high = lr4_split(x, 110.0)
    lm = (low[0] + low[1]) * 0.5
    x = np.vstack([lm, lm]) + high
    # tonal shaping
    x = eq(x, "lowshelf", 55, 0.7, -1.8)
    x = eq(x, "peak", 300, 0.8, -1.0)
    x = eq(x, "peak", 1400, 0.8, 0.8)
    x = eq(x, "highshelf", 7500, 0.6, 1.8)
    x = eq(x, "peak", 3500, 0.7, 0.8)
    # glue compression (gentle)
    x, g = compress(x, thr=-14, ratio=1.8, att=0.012, rel=0.16, knee=8, rms_ms=12)
    meter = pyln.Meter(SR)
    gain = 0.0
    for it in range(8):
        y = x * db(gain)
        y, lg = limiter(y, ceiling_db=tp_ceiling - 0.35, look_ms=1.5, rel_ms=80)
        lufs = meter.integrated_loudness(y.T)
        d = target_lufs - lufs
        if abs(d) < 0.05:
            break
        gain += d
    tp = true_peak_db(y)
    k = 0
    while tp > tp_ceiling - 0.05 and k < 5:
        y = y * db(tp_ceiling - 0.1 - tp)
        tp = true_peak_db(y)
        k += 1
    y = fade(y, 0.0, 0.002)   # end de-click (loop seam lands on the opening impact)
    return y, dict(lufs=float(meter.integrated_loudness(y.T)), true_peak=float(tp),
                   limiter_min_gain_db=float(20 * np.log10(lg.min() + 1e-12)),
                   comp_min_gain_db=float(20 * np.log10(g.min() + 1e-12)))


def write_wav24(path, x):
    r = np.random.default_rng(7)
    lsb = 1.0 / (2 ** 23)
    dith = (r.random(x.shape) - r.random(x.shape)) * lsb   # TPDF dither
    y = np.clip(x + dith, -1 + lsb, 1 - lsb)
    sf.write(path, y.T, SR, subtype="PCM_24")


SECTIONS = [
    ("intro_opening_hook", 0, 2, "Bronze impact + bell, distant bull roar, filtered pulse, hook teaser on dark bouzouki; voice-over space"),
    ("first_groove", 2, 8, "Kick, rolling bass, darbuka, hook on bouzouki + pluck + aulos, HEY/HO responses; layers add every 2 bars"),
    ("escalation", 8, 14, "Full gang chants, hook variation, vocal chops, davul, rhythmic breaks at bars 10 and 12, crescendo"),
    ("pre_drop", 14, 15, "Impact + bronze bull roar, filtered hook fragment, breathing, reverse metal sweep + reverse shriek, power HEY, hard silence"),
    ("main_drop", 15, 23, "Driven bass, full hook stack, choir accents, metallic percussion, horror accents; break before bar 20"),
    ("dark_breakdown", 23, 27, "Half-time low aulos hook, bouzouki tremolo, accelerating heartbeat, low choir, distant horror vocals, HA build"),
    ("final_drop", 27, 33, "Strongest hook, cross-rhythm stutter bar, Phrygian-dominant (G#) melodic twist, biggest chants, final roar"),
    ("final_impact_loop", 33, 34, "Final bronze impact + HO + choir, teaser motif returns, reverse metal swell into 0:00 for seamless replay"),
]


def build_beatmap(audio, info, path):
    fps = 60
    fr = lambda t: int(round(t * fps))
    beats = []
    for i in range(136):
        t = i * BEAT
        beats.append(dict(index=i, time=round(t, 4), frame=fr(t), bar=i // 4 + 1, beat=i % 4 + 1, downbeat=(i % 4 == 0)))
    sections = [dict(name=n, start=round(b0 * BAR, 4), end=round(b1 * BAR, 4), start_frame=fr(b0 * BAR),
                     end_frame=fr(b1 * BAR), bars=[b0 + 1, b1], description=d) for n, b0, b1, d in SECTIONS]
    cats = {}
    for e in sorted(EVENTS, key=lambda e: e["time"]):
        e = dict(e)
        e["frame"] = fr(e["time"])
        cat = e.pop("category")
        cats.setdefault(cat, []).append(e)
    # --- verification against the exported audio: kick onsets ---
    mono = audio.mean(0)
    # kick beater band (1.8-9 kHz click + body): onset = steepest rise of a 0.5 ms energy envelope
    from scipy import signal as _sg
    hb = _sg.sosfiltfilt(_sg.butter(4, [1800, 9000], btype="band", fs=SR, output="sos"), mono)
    env = _sg.filtfilt(np.ones(24) / 24, [1.0], hb ** 2)
    d = np.diff(env, prepend=env[0])
    offs = []
    for t in KICKS:
        a = int((t - 0.006) * SR)
        b = int((t + 0.006) * SR)
        if a < 0 or b > len(d):
            continue
        offs.append((a + int(np.argmax(d[a:b]))) / SR - t)
    offs = np.array(offs) * 1000
    ver = dict(kick_count=len(KICKS), detected_onset_offset_ms=dict(median=round(float(np.median(offs)), 2),
               max_abs=round(float(np.max(np.abs(offs))), 2)),
               note="Times are the musical grid positions used at render time (sample-accurate). Percussion carries "
                    "+/-2 ms humanisation and odd 16ths are swung by 8.5% of a 16th (~9.4 ms); swung times are already "
                    "included. Chant times mark the vowel (beat) onset; the breathy 'H' starts ~33 ms earlier.")
    bm = dict(
        track=dict(file="BRAZEN_BULL_FINAL.wav", duration_s=60.0, sample_rate=SR, bit_depth=24, channels=2,
                   bpm=BPM, time_signature="4/4", bars=34, beats=136, beat_s=round(BEAT, 6), bar_s=round(BAR, 6),
                   key="E Phrygian (final-drop twist: E Phrygian dominant / Hijaz, G#)", swing_16ths_pct=SWING * 100,
                   integrated_lufs=round(info["lufs"], 2), true_peak_dbtp=round(info["true_peak"], 2),
                   loop="seamless: ends with a reverse metal swell resolving into the 0.000 s bronze impact"),
        animation=dict(fps=fps, resolution="1080x1920", frame_formula="frame = round(time_s * 60)",
                       voice_over_window=dict(start=0.25, end=3.5, note="intro mix leaves 300 Hz-3 kHz space; groove starts 3.529 s")),
        sections=sections,
        drops=[dict(name="main_drop", time=round(15 * BAR, 4), frame=fr(15 * BAR)),
               dict(name="final_drop", time=round(27 * BAR, 4), frame=fr(27 * BAR))],
        breakdowns=[dict(name="dark_breakdown", start=round(23 * BAR, 4), end=round(27 * BAR, 4))],
        silences=[dict(start=round(a, 4), end=round(b, 4), duration=round(b - a, 4), start_frame=fr(a), end_frame=fr(b)) for a, b in SILENCES],
        rhythmic_breaks=[dict(start=round(a, 4), end=round(b, 4), duration=round(b - a, 4), start_frame=fr(a), end_frame=fr(b)) for a, b in BREAKS],
        beats=beats,
        downbeats=[b["time"] for b in beats if b["downbeat"]],
        kicks=[round(t, 4) for t in sorted(KICKS)],
        events=cats,
        verification=ver,
    )
    with open(path, "w") as f:
        json.dump(bm, f, indent=1)
    return ver


if __name__ == "__main__":
    t0 = time.time()
    arrange()
    print(f"arranged in {time.time() - t0:.1f}s, events={len(EVENTS)}", flush=True)
    mixed, stems = mix()
    print(f"mixed in {time.time() - t0:.1f}s peak={np.max(np.abs(mixed)):.2f}", flush=True)
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    np.save(f"{out_dir}/premaster.npy", mixed.astype(np.float32))
    secs = dict(intro=(0, 3.53), groove=(3.53, 14.12), escal=(14.12, 24.71), predrop=(24.71, 26.47),
                drop1=(26.47, 40.59), breakdown=(40.59, 47.65), drop2=(47.65, 58.24), outro=(58.24, 60))
    stem_rep = {}
    for k, v in stems.items():
        stem_rep[k] = {sn: round(float(10 * np.log10(np.mean(v[:, int(a * SR):int(b * SR)] ** 2) + 1e-12)), 1)
                       for sn, (a, b) in secs.items()}
    with open(f"{out_dir}/stems_db.json", "w") as f:
        json.dump(stem_rep, f, indent=1)
    for k in ("horror", "vox", "rumble", "sub", "bmid", "kick", "bz", "pl", "aul", "ss", "chop", "dly_hor", "rv_dark"):
        if k in stems:
            ss = stems[k]
            np.save(f"{out_dir}/stem_{k}.npy", ss.astype(np.float32))
    y, info = master(mixed)
    print("master:", info, flush=True)
    write_wav24(f"{out_dir}/BRAZEN_BULL_FINAL.wav", y)
    ver = build_beatmap(y, info, f"{out_dir}/BRAZEN_BULL_BEATMAP.json")
    print("beatmap verification:", ver["detected_onset_offset_ms"])
    with open(f"{out_dir}/events_raw.json", "w") as f:
        json.dump(dict(events=EVENTS, kicks=KICKS, silences=SILENCES, breaks=BREAKS, master=info), f)
    print(f"done in {time.time() - t0:.1f}s")
