"""Voice engine: glottal-source + cascade-formant male voices, gang shouts,
choir accents, rhythmic breaths, vocal chops and stylised horror voices
(bronze-resonated bull bellows, distant processed shrieks).

No recordings are used; every voice is synthesised and then processed.
"""
import numpy as np
from numba import njit
from dsp import (SR, rng, tarr, lp, hp, bp, eq, svf_lp, svf_bp, softclip, pan, to_st,
                 pitch_shift_resample, white, smooth_random, fade, normalize, mtof)

# ---------------------------------------------------------------------------
# Glottal source (Rosenberg pulse derivative with jitter / shimmer / subharmonics)
# ---------------------------------------------------------------------------
@njit(cache=True, fastmath=True)
def _glottal(f0, oq, jit, shim, subh, rv1, rv2):
    n = f0.shape[0]
    out = np.zeros(n)
    gate = np.zeros(n)
    ph = 0.0
    pj = 1.0
    pa = 1.0
    k = 0
    prev = 0.0
    nr = rv1.shape[0]
    for i in range(n):
        ph += f0[i] * pj / 48000.0
        if ph >= 1.0:
            ph -= 1.0
            k += 1
            pj = 1.0 + jit * rv1[k % nr]
            pa = 1.0 + shim * rv2[k % nr]
            if subh > 0.0 and (k % 2 == 1):
                pa *= (1.0 - subh)
                pj *= (1.0 + subh * 0.15)
        o = oq[i]
        tp = 0.66 * o
        tn = 0.34 * o
        if ph < tp:
            g = 0.5 * (1.0 - np.cos(np.pi * ph / tp))
        elif ph < tp + tn:
            g = np.cos(0.5 * np.pi * (ph - tp) / tn)
        else:
            g = 0.0
        g *= pa
        out[i] = g - prev
        prev = g
        gate[i] = 1.0 if ph < o else 0.2
    return out, gate


@njit(cache=True, fastmath=True)
def _formant_cascade(x, F, B):
    n = x.shape[0]
    nf = F.shape[0]
    y1 = np.zeros(nf)
    y2 = np.zeros(nf)
    out = np.empty(n)
    T = 1.0 / 48000.0
    for i in range(n):
        s = x[i]
        for k in range(nf):
            f = F[k, i]
            b = B[k, i]
            C = -np.exp(-2.0 * np.pi * b * T)
            Bc = 2.0 * np.exp(-np.pi * b * T) * np.cos(2.0 * np.pi * f * T)
            A = 1.0 - Bc - C
            y = A * s + Bc * y1[k] + C * y2[k]
            y2[k] = y1[k]
            y1[k] = y
            s = y
        out[i] = s
    return out


# male formants F1..F5 and bandwidths
VOW = {
    "a":  ([760, 1150, 2500, 3350, 3850], [85, 95, 130, 180, 220]),
    "ah": ([700, 1220, 2600, 3350, 3850], [90, 100, 140, 180, 220]),
    "e":  ([540, 1800, 2500, 3350, 3850], [70, 100, 140, 180, 220]),
    "i":  ([310, 2150, 2950, 3450, 3900], [55, 100, 150, 190, 230]),
    "o":  ([540, 850, 2400, 3300, 3800], [75, 85, 130, 180, 220]),
    "u":  ([330, 760, 2250, 3300, 3800], [65, 80, 130, 180, 220]),
    "uh": ([620, 1180, 2450, 3350, 3850], [90, 110, 150, 190, 230]),
    "m":  ([260, 1050, 2250, 3300, 3800], [120, 300, 400, 400, 400]),
    "ae": ([820, 1700, 2550, 3400, 3950], [90, 110, 150, 190, 230]),
}


def _tracks(keys, n, tract, bw_mul=1.0):
    """keys: list of (frac, vowel). returns F, B arrays (5, n) with smooth transitions"""
    F = np.zeros((5, n))
    B = np.zeros((5, n))
    x = np.linspace(0, 1, n)
    fr = np.array([k[0] for k in keys])
    for j in range(5):
        fv = np.array([VOW[k[1]][0][j] for k in keys], dtype=float)
        bv = np.array([VOW[k[1]][1][j] for k in keys], dtype=float)
        F[j] = np.interp(x, fr, fv) * tract
        B[j] = np.interp(x, fr, bv) * bw_mul
    # smooth the articulation (no robotic jumps)
    k = max(int(0.018 * SR), 3)
    win = np.hanning(k)
    win /= win.sum()
    for j in range(5):
        F[j] = np.convolve(np.pad(F[j], (k, k), mode="edge"), win, mode="same")[k:-k]
    return np.ascontiguousarray(F), np.ascontiguousarray(B)


def voice(dur, f0_curve, keys, tract=1.0, oq=0.55, jitter=0.012, shimmer=0.08,
          subharm=0.0, breath=0.18, h_len=0.045, h_gain=0.9, vib_rate=5.2, vib_cents=0.0,
          vib_delay=0.12, att=0.012, rel=0.06, drift_cents=8.0, bw_mul=1.0, seed=None):
    """One human-ish voice. f0_curve: callable(x in 0..1) -> Hz multiplier array or array."""
    r = np.random.default_rng(seed if seed is not None else rng().integers(1 << 30))
    nh = int(h_len * SR)
    nv = int(dur * SR)
    tail = int(0.06 * SR)
    n = nh + nv + tail
    x = np.linspace(0, 1, nv)
    f0 = f0_curve(x) if callable(f0_curve) else np.interp(x, np.linspace(0, 1, len(f0_curve)), f0_curve)
    # natural micro-drift + delayed vibrato
    t = np.arange(nv) / SR
    drift = smooth_random(nv, 6.0) * drift_cents
    vib = vib_cents * np.clip((t - vib_delay) / 0.12, 0, 1) * np.sin(2 * np.pi * vib_rate * t + r.uniform(0, 6.28))
    f0 = f0 * 2 ** ((drift + vib) / 1200.0)
    f0_full = np.concatenate([np.full(nh, f0[0]), f0, np.full(tail, f0[-1])])
    oq_arr = np.full(n, oq)
    rv1 = r.standard_normal(4096)
    rv2 = r.standard_normal(4096)
    src, gate = _glottal(np.ascontiguousarray(f0_full), oq_arr, jitter, shimmer, subharm, rv1, rv2)
    src = src / (np.max(np.abs(src)) + 1e-9)
    # envelopes
    venv = np.zeros(n)
    a_n = max(int(att * SR), 1)
    r_n = max(int(rel * SR), 1)
    core = np.ones(nv)
    core[:a_n] = np.linspace(0, 1, a_n) ** 1.5
    # slight decay over syllable (energy falls in shouts)
    core *= np.linspace(1.0, 0.72, nv)
    venv[nh:nh + nv] = core
    venv[nh + nv:nh + nv + min(r_n, tail)] = core[-1] * np.exp(-np.arange(min(r_n, tail)) / (r_n / 4.5))
    # voicing starts slightly before the h ends (co-articulation)
    hen = np.zeros(n)
    if nh > 0:
        hh = np.sin(np.linspace(0, np.pi, nh + int(0.02 * SR))) ** 0.7
        hen[:len(hh)] = hh[:n]
    noise = r.standard_normal(n)
    asp = noise * (h_gain * hen + breath * venv * gate)
    exc = src * venv * 1.0 + asp * 0.35
    F, B = _tracks(keys, n, tract, bw_mul)
    # aspiration region uses the first vowel's tract (h is voiceless vowel)
    y = _formant_cascade(np.ascontiguousarray(exc), F, B)
    y = hp(y, 70.0)
    return y / (np.max(np.abs(y)) + 1e-9)


def shout_curve(base, rise=1.06, fall=0.82, start=0.9):
    def c(x):
        up = start + (rise - start) * np.clip(x / 0.22, 0, 1) ** 0.6
        down = np.where(x > 0.35, (x - 0.35) / 0.65, 0.0)
        return base * up * (1 - (1 - fall) * down ** 1.4)
    return c


SYL = {
    # name: vowel keyframes, duration, h_len
    "HA":  ([(0, "a"), (0.6, "ah"), (1, "uh")], 0.17, 0.05),
    "HEY": ([(0, "e"), (0.45, "e"), (0.8, "i"), (1, "i")], 0.25, 0.05),
    "HO":  ([(0, "o"), (0.55, "o"), (1, "u")], 0.23, 0.05),
    "HUH": ([(0, "uh"), (1, "uh")], 0.11, 0.035),
    "OH":  ([(0, "o"), (1, "o")], 0.45, 0.0),
    "AH":  ([(0, "ah"), (1, "a")], 0.45, 0.0),
    "OO":  ([(0, "u"), (1, "u")], 0.8, 0.0),
}


def syllable(name, f0, tract=1.0, dur_mul=1.0, effort=1.0, seed=None, **kw):
    keys, dur, h = SYL[name]
    oq = kw.pop("oq", 0.62 - 0.2 * effort)        # pressed voice when shouting
    return voice(dur * dur_mul, shout_curve(f0), keys, tract=tract, oq=oq, h_len=h,
                 breath=kw.pop("breath", 0.14 + 0.1 * effort), seed=seed, **kw)


# ---------------------------------------------------------------------------
# Ensembles
# ---------------------------------------------------------------------------
def gang(name, f0, n_voices=8, t_spread=0.016, cents=28.0, width=0.85, effort=1.0,
         dur_mul=1.0, octave_down=0.35, fifth=0.0, seed=0):
    """Layered male gang shout. Returns stereo (2, n)."""
    r = np.random.default_rng(seed)
    parts = []
    maxlen = 0
    for v in range(n_voices):
        tract = r.uniform(0.9, 1.07)
        c = r.normal(0, cents)
        mult = 1.0
        if fifth > 0 and v % 4 == 3:
            mult = 1.5
        y = syllable(name, f0 * mult * 2 ** (c / 1200), tract=tract, effort=effort * r.uniform(0.85, 1.1),
                     dur_mul=dur_mul * r.uniform(0.93, 1.08), seed=int(r.integers(1 << 30)),
                     jitter=r.uniform(0.008, 0.02), shimmer=r.uniform(0.05, 0.12))
        off = int(abs(r.normal(0, t_spread)) * SR)
        y = np.concatenate([np.zeros(off), y]) * r.uniform(0.65, 1.0)
        p = r.uniform(-width, width)
        parts.append((y, p))
        maxlen = max(maxlen, len(y))
    if octave_down > 0:
        for v in range(2):
            y = syllable(name, f0 * 0.5 * 2 ** (r.normal(0, 10) / 1200), tract=r.uniform(0.92, 1.0),
                         effort=effort * 0.9, dur_mul=dur_mul, seed=int(r.integers(1 << 30)))
            parts.append((y * octave_down, (-0.25, 0.25)[v]))
            maxlen = max(maxlen, len(y))
    out = np.zeros((2, maxlen))
    for y, p in parts:
        out[:, :len(y)] += pan(y, p)
    return out / (np.max(np.abs(out)) + 1e-9)


def choir(name, notes_midi, per_note=3, dur_mul=1.0, effort=0.5, seed=0, width=0.9):
    r = np.random.default_rng(seed)
    parts = []
    maxlen = 0
    for m in notes_midi:
        for v in range(per_note):
            f = mtof(m) * 2 ** (r.normal(0, 9) / 1200)
            y = voice(SYL[name][1] * dur_mul, lambda x, f=f: f * (0.985 + 0.015 * np.clip(x / 0.1, 0, 1)),
                      SYL[name][0], tract=r.uniform(0.93, 1.06), oq=0.55, h_len=SYL[name][2],
                      breath=0.12, vib_cents=r.uniform(12, 22), vib_rate=r.uniform(4.8, 5.6), vib_delay=0.08,
                      att=0.04, rel=0.12, seed=int(r.integers(1 << 30)))
            off = int(abs(r.normal(0, 0.012)) * SR)
            y = np.concatenate([np.zeros(off), y]) * r.uniform(0.7, 1.0)
            parts.append((y, r.uniform(-width, width)))
            maxlen = max(maxlen, len(y))
    out = np.zeros((2, maxlen))
    for y, p in parts:
        out[:, :len(y)] += pan(y, p)
    return out / (np.max(np.abs(out)) + 1e-9)


def breath(kind="out", dur=0.13, tract=1.0, seed=None):
    """voiceless rhythmic breath ('huh' exhale / sharp inhale)"""
    r = np.random.default_rng(seed if seed is not None else rng().integers(1 << 30))
    n = int(dur * SR)
    x = r.standard_normal(n)
    if kind == "out":
        env = np.minimum(np.arange(n) / (0.008 * SR), 1) * np.exp(-np.arange(n) / (0.045 * SR))
        keys = [(0, "uh"), (1, "a")]
    else:
        env = (np.arange(n) / n) ** 1.6 * np.minimum((n - np.arange(n)) / (0.01 * SR), 1)
        keys = [(0, "i"), (1, "e")]
    F, B = _tracks(keys, n, tract, bw_mul=2.2)
    y = _formant_cascade(np.ascontiguousarray(x * env), F, B)
    y = hp(y, 300)
    return y / (np.max(np.abs(y)) + 1e-9)


def vocal_chop(midi, dur, vowel="ah", tract=0.88, seed=None):
    """pitched sustained vowel used as a processed vocal-chop instrument"""
    f = mtof(midi)
    keys = [(0, vowel), (1, vowel)]
    y = voice(dur, lambda x: f * np.ones_like(x), keys, tract=tract, oq=0.5, h_len=0.0, breath=0.1,
              vib_cents=0, att=0.004, rel=0.02, drift_cents=3, jitter=0.004, shimmer=0.03, seed=seed)
    return y


# ---------------------------------------------------------------------------
# Horror voices (stylised, processed; not realistic distress)
# ---------------------------------------------------------------------------
@njit(cache=True, fastmath=True)
def _comb_bank(x, delays, fbs, damp):
    n = x.shape[0]
    nc = delays.shape[0]
    out = np.zeros(n)
    maxd = 0
    for c in range(nc):
        if delays[c] > maxd:
            maxd = delays[c]
    buf = np.zeros((nc, maxd + 1))
    ptr = np.zeros(nc, dtype=np.int64)
    lpst = np.zeros(nc)
    for i in range(n):
        acc = 0.0
        for c in range(nc):
            d = delays[c]
            rd = ptr[c] - d
            if rd < 0:
                rd += maxd + 1
            yd = buf[c, rd]
            lpst[c] = (1.0 - damp) * yd + damp * lpst[c]
            y = x[i] + fbs[c] * lpst[c]
            buf[c, ptr[c]] = y
            ptr[c] += 1
            if ptr[c] > maxd:
                ptr[c] = 0
            acc += yd
        out[i] = acc / nc
    return out


def bronze_resonate(x, base_hz=92.0, fb=0.86, damp=0.35, mix=0.55):
    """runs a signal 'through the bronze body': inharmonic comb bank (bell-like ratios)"""
    ratios = np.array([1.0, 1.183, 1.506, 2.0, 2.66, 3.01])
    delays = (SR / (base_hz * ratios)).astype(np.int64)
    fbs = np.full(len(ratios), fb)
    wet = _comb_bank(np.ascontiguousarray(x), delays, fbs, damp)
    wet = hp(wet, 60)
    wet = wet / (np.max(np.abs(wet)) + 1e-9)
    dry = x / (np.max(np.abs(x)) + 1e-9)
    return (1 - mix) * dry + mix * wet


def bull_roar(dur=0.9, f_lo=58.0, f_hi=86.0, f_end=44.0, seed=0, bronze=0.55):
    """eerie bronze bull bellow: huge vocal tract, subharmonic growl, metal body"""
    r = np.random.default_rng(seed)

    def curve(x):
        up = f_lo + (f_hi - f_lo) * np.clip(x / 0.3, 0, 1) ** 0.7
        dn = np.where(x > 0.45, (x - 0.45) / 0.55, 0)
        return up * (1 - (1 - f_end / f_hi) * dn ** 1.3)

    keys = [(0, "m"), (0.12, "u"), (0.42, "a"), (0.75, "ah"), (1, "o")]
    layers = []
    for v in range(3):
        y = voice(dur * r.uniform(0.96, 1.04), lambda x: curve(x) * 2 ** (r.normal(0, 18) / 1200), keys,
                  tract=r.uniform(0.55, 0.64), oq=0.72, jitter=0.05, shimmer=0.22, subharm=0.42,
                  breath=0.55, h_len=0.06, h_gain=0.5, att=0.07, rel=0.25, bw_mul=1.5,
                  seed=int(r.integers(1 << 30)))
        layers.append(y)
    n = max(len(y) for y in layers)
    y = sum(np.pad(l, (0, n - len(l))) for l in layers)
    t = np.arange(n) / SR
    growl = 1 + 0.45 * np.sin(2 * np.pi * 29 * t + r.uniform(0, 6)) * np.clip(t / 0.15, 0, 1)
    y = y * growl
    y = softclip(y / (np.max(np.abs(y)) + 1e-9) * 3.0, 1.0)     # distortion
    y = bronze_resonate(y, base_hz=r.uniform(85, 98), mix=bronze)
    sub = pitch_shift_resample(y, -12)[:n]
    sub = lp(np.pad(sub, (0, n - len(sub))), 400)
    y = y + 0.45 * sub
    y = eq(y, "peak", 1800, 1.0, 3.0)      # metallic bite
    y = hp(y, 35)
    return fade(y / (np.max(np.abs(y)) + 1e-9), 0.01, 0.08)


def shriek(dur=0.55, f0=430.0, seed=0, layers=3, demon=0.5):
    """stylised distant shriek: pressed high voice, irregular vibrato, pitch-shifted ghost layers"""
    r = np.random.default_rng(seed)

    def curve(x):
        up = 0.78 + 0.34 * np.clip(x / 0.18, 0, 1) ** 0.5
        dn = np.where(x > 0.4, (x - 0.4) / 0.6, 0)
        return f0 * up * (1 - 0.32 * dn ** 1.2)

    keys = [(0, "ae"), (0.3, "a"), (0.7, "ah"), (1, "uh")]
    ys = []
    for v in range(layers):
        y = voice(dur * r.uniform(0.9, 1.1), lambda x: curve(x) * 2 ** (r.normal(0, 40) / 1200), keys,
                  tract=r.uniform(0.92, 1.02), oq=0.34, jitter=0.035, shimmer=0.16, subharm=0.12,
                  breath=0.55, h_len=0.02, vib_rate=r.uniform(6.5, 8.5), vib_cents=60, vib_delay=0.03,
                  att=0.03, rel=0.2, seed=int(r.integers(1 << 30)))
        ys.append(y)
    n = max(len(y) for y in ys)
    y = sum(np.pad(a, (0, n - len(a))) for a in ys)
    y = y / (np.max(np.abs(y)) + 1e-9)
    ghost = pitch_shift_resample(y, -7)
    ghost = np.pad(ghost, (0, max(0, n - len(ghost))))[:n]
    low = pitch_shift_resample(y, -12)
    low = np.pad(low, (0, max(0, n - len(low))))[:n]
    y = y + demon * 0.7 * ghost + demon * 0.5 * low
    y = softclip(y / (np.max(np.abs(y)) + 1e-9) * 2.2, 1.0)
    y = bp(y, 320, 5200)                         # distance band-limit
    y = eq(y, "peak", 2600, 1.2, -2.0)          # keep it from getting piercing
    return fade(y / (np.max(np.abs(y)) + 1e-9), 0.005, 0.06)
