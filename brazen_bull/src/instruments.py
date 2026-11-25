"""Instrument rack: drums, tribal percussion, basses, bouzouki/lyre (physical model),
aulos (double-reed wind), synth layers, bronze metals and integrated sound design.
All sounds are synthesised from first principles."""
import numpy as np
from functools import lru_cache
from dsp import (SR, BEAT, STEP, BAR, rng, tarr, mtof, lp, hp, bp, eq, svf_lp, svf_bp, svf_hp,
                 saw, square, sine_f, ks_string, modal, white, pink, brown, smooth_random,
                 adsr, fade, softclip, wavefold, normalize, pan, to_st, chorus, make_ir,
                 convolve_st)


# =============================================================================
# DRUMS
# =============================================================================
def kick(kind="main", seed=0):
    r = np.random.default_rng(seed)
    dur = 0.42 if kind != "long" else 0.75
    t = tarr(dur)
    f_end = 47.0
    f = f_end + 165 * np.exp(-t / 0.028) + 380 * np.exp(-t / 0.0035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR)
    hold = 0.05 if kind != "long" else 0.12
    dec = 0.19 if kind != "long" else 0.42
    env = np.where(t < hold, 1.0, np.exp(-(t - hold) / dec))
    env *= np.minimum(t / 0.0007, 1)
    body = softclip(body * env * 1.9, 1.2)
    # beater click + transient knock
    cl = white(len(t)) * np.exp(-t / 0.0022)
    cl = bp(cl, 1800, 9000) * 0.35
    knock = np.sin(2 * np.pi * 1900 * t) * np.exp(-t / 0.004) * 0.18
    # mid punch ~ 120 Hz (helps phone speakers)
    punch = np.sin(2 * np.pi * np.cumsum(118 + 60 * np.exp(-t / 0.01)) / SR) * np.exp(-t / 0.045) * 0.35
    k = body + cl + knock + punch
    k = hp(k, 28)
    return fade(normalize(k, 1.0), 0.0, 0.01)


def clap(seed=0):
    r = np.random.default_rng(seed)
    t = tarr(0.35)
    n = len(t)
    x = np.zeros(n)
    for i, off in enumerate([0.0, 0.0085, 0.017, 0.027]):
        o = int(off * SR)
        tt = t[:n - o]
        x[o:] += r.standard_normal(n - o) * np.exp(-tt / (0.0045 if i < 3 else 0.11)) * (0.8 if i < 3 else 1.0)
    x = bp(x, 900, 5200, 2)
    x = eq(x, "peak", 1500, 1.4, 4)
    body = np.sin(2 * np.pi * np.cumsum(205 + 40 * np.exp(-t / 0.01)) / SR) * np.exp(-t / 0.05) * 0.45
    snap = bp(r.standard_normal(n) * np.exp(-t / 0.09), 2500, 11000) * 0.35
    return normalize(x + body + snap)


def hat(open_=False, seed=0):
    r = np.random.default_rng(seed)
    dur = 0.32 if open_ else 0.07
    t = tarr(dur)
    fs = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0]) * 1.92
    x = np.zeros(len(t))
    for f in fs:
        x += np.sign(np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)))
    x = x / 6 + 0.6 * r.standard_normal(len(t))
    x = bp(x, 6500, 16000, 2)
    x = hp(x, 7000, 2)
    env = np.exp(-t / (0.11 if open_ else 0.016)) * np.minimum(t / 0.0004, 1)
    y = x * env
    y = eq(y, "highshelf", 11000, 0.7, -3)
    return normalize(y)


def shaker(seed=0):
    r = np.random.default_rng(seed)
    t = tarr(0.09)
    x = r.standard_normal(len(t))
    # grain clusters -> organic seed rattle
    grains = (r.random(len(t)) < 0.06).astype(float) * r.uniform(0.3, 1.0, len(t))
    x = 0.55 * x + 1.6 * grains * r.standard_normal(len(t))
    env = np.minimum(t / 0.012, 1) ** 1.5 * np.exp(-t / 0.028)
    y = bp(x * env, 4200, 13000, 2)
    return normalize(y)


def membrane(f1, dur, decay, strike_noise=0.4, pitch_drop=0.06, bright=1.0, seed=0):
    """circular membrane modal synthesis (frame drum / davul / darbuka)"""
    r = np.random.default_rng(seed)
    ratios = np.array([1.0, 1.594, 2.136, 2.296, 2.653, 2.918, 3.156, 3.501])
    amps = np.array([1.0, 0.55, 0.38, 0.3, 0.22, 0.16, 0.12, 0.08]) * np.array([1, bright, bright, bright ** 1.5, bright ** 2, bright ** 2, bright ** 2.5, bright ** 3])
    decs = decay * np.array([1.0, 0.55, 0.42, 0.36, 0.3, 0.26, 0.22, 0.2])
    t = tarr(dur)
    y = np.zeros(len(t))
    pd = 1 + pitch_drop * np.exp(-t / 0.03)
    for ra, a, d in zip(ratios, amps, decs):
        y += a * np.exp(-t / d) * np.sin(2 * np.pi * np.cumsum(f1 * ra * pd) / SR + r.uniform(0, 6.28))
    nz = r.standard_normal(len(t)) * np.exp(-t / 0.006)
    nz = bp(nz, f1 * 2, min(f1 * 25, 16000))
    y = y + strike_noise * nz * 3
    y *= np.minimum(t / 0.0006, 1)
    return normalize(y)


def darbuka(stroke, seed=0):
    r = np.random.default_rng(seed)
    if stroke == "D":          # doum: deep centre stroke
        y = membrane(112, 0.42, 0.16, strike_noise=0.25, pitch_drop=0.1, bright=0.7, seed=seed)
        y = eq(y, "peak", 112, 1.0, 3)
    elif stroke == "T":        # tek: sharp rim
        t = tarr(0.12)
        y = membrane(690, 0.12, 0.035, strike_noise=0.9, pitch_drop=0.02, bright=1.2, seed=seed)
        crack = bp(r.standard_normal(len(t)) * np.exp(-t / 0.004), 2500, 12000)
        y = y + 0.8 * normalize(crack)
        y = hp(y, 350)
    else:                      # ka: softer off-hand rim
        t = tarr(0.09)
        y = membrane(600, 0.09, 0.025, strike_noise=0.7, bright=1.0, seed=seed)
        y = hp(y, 400) * 0.8
    return normalize(y)


def davul(seed=0):
    """big tribal bass drum / frame drum"""
    y = membrane(68, 0.8, 0.3, strike_noise=0.35, pitch_drop=0.18, bright=0.6, seed=seed)
    t = tarr(0.8)
    thump = np.sin(2 * np.pi * np.cumsum(60 + 50 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.12)
    y = normalize(y + 0.8 * thump)
    return softclip(y * 1.4, 1.0)


def tom(f=140, seed=0):
    return membrane(f, 0.5, 0.18, strike_noise=0.45, pitch_drop=0.12, bright=0.8, seed=seed)


def heartbeat(seed=0):
    """'lub-dub' deep physiological pulse (two muffled thumps)"""
    out = np.zeros(int(0.6 * SR))
    for off, f, a in ((0.0, 58, 1.0), (0.155, 50, 0.72)):
        t = tarr(0.35)
        y = np.sin(2 * np.pi * np.cumsum(f + 35 * np.exp(-t / 0.018)) / SR) * np.exp(-t / 0.07)
        y *= np.minimum(t / 0.004, 1)
        nz = lp(white(len(t)) * np.exp(-t / 0.02), 300) * 0.4
        o = int(off * SR)
        out[o:o + len(t)] += a * (y + nz)
    out = lp(out, 260)
    return normalize(softclip(out * 1.5, 1.0))


# =============================================================================
# METALS & BRONZE
# =============================================================================
BELL_R = np.array([0.25, 0.5, 0.6, 0.75, 1.0, 1.26, 1.5, 2.0, 2.52, 2.67, 3.0, 3.36, 4.0])
BELL_A = np.array([0.55, 0.7, 0.75, 0.35, 1.0, 0.45, 0.5, 0.4, 0.28, 0.22, 0.2, 0.12, 0.1])
BELL_D = np.array([5.5, 4.0, 3.2, 2.2, 2.6, 1.7, 1.4, 1.0, 0.7, 0.6, 0.5, 0.38, 0.3])


def bronze_bell(nominal=329.63, dur=4.5, seed=0, decay_mul=1.0):
    r = np.random.default_rng(seed)
    fr = nominal * BELL_R * (1 + r.normal(0, 0.002, len(BELL_R)))
    y = modal(fr, BELL_A, BELL_D * decay_mul, dur, detune_beat=0.7)
    t = tarr(dur)
    strike = bp(r.standard_normal(len(t)) * np.exp(-t / 0.008), 800, 9000) * 0.9
    y = y + strike
    return normalize(y)


def anvil(f=880.0, dur=0.9, seed=0, decay=0.35):
    r = np.random.default_rng(seed)
    ratios = np.array([1.0, 2.756, 5.404, 8.933, 1.42, 3.61, 6.8])
    amps = np.array([1.0, 0.7, 0.45, 0.25, 0.35, 0.3, 0.15])
    decs = decay * np.array([1.0, 0.6, 0.35, 0.2, 0.7, 0.4, 0.25])
    y = modal(f * ratios * (1 + r.normal(0, 0.003, 7)), amps, decs, dur, detune_beat=1.5)
    t = tarr(dur)
    y += bp(r.standard_normal(len(t)) * np.exp(-t / 0.003), 2000, 14000) * 1.2
    return normalize(y)


def metal_tick(f=1318.5, seed=0):
    """small bronze clank for rhythmic metallic percussion"""
    y = anvil(f, 0.25, seed=seed, decay=0.07)
    return normalize(hp(y, 600))


def boom(dur=2.2, f0=62.0, f1=27.0, seed=0):
    r = np.random.default_rng(seed)
    t = tarr(dur)
    f = f1 + (f0 - f1) * np.exp(-t / 0.35)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.8) * np.minimum(t / 0.002, 1)
    nz = lp(r.standard_normal(len(t)) * np.exp(-t / 0.25), 180, 2) * 3
    y = softclip((y + nz) * 1.6, 1.0)
    # harmonics that survive phone speakers
    harm = bp(softclip(y * 4, 1.0), 90, 600) * 0.35
    return normalize(hp(y + harm, 22))


def metal_impact(seed=0, nominal=164.81, size=1.0):
    """heavy bronze hit: low bell + anvil + crash noise + boom"""
    r = np.random.default_rng(seed)
    dur = 4.0
    n = int(dur * SR)
    bell = np.pad(bronze_bell(nominal, dur, seed=seed, decay_mul=0.8), (0, 0))[:n]
    anv = np.zeros(n)
    a = anvil(nominal * 2.0, 1.6, seed=seed + 1, decay=0.5)
    anv[:len(a)] = a
    t = tarr(dur)
    crash = r.standard_normal(n) * np.exp(-t / 0.35) * np.minimum(t / 0.001, 1)
    crash = bp(crash, 900, 9000) * 0.5
    bm = np.zeros(n)
    b = boom(2.2, seed=seed)
    bm[:len(b)] = b
    y = 0.9 * bell + 0.6 * anv + 0.5 * crash + 0.9 * size * bm
    return normalize(y)


# =============================================================================
# SOUND DESIGN FX
# =============================================================================
def whoosh(dur, up=True, seed=0, q=2.2):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    x = r.standard_normal(n)
    xx = np.linspace(0, 1, n)
    c = 250 * (40 ** (xx if up else 1 - xx))
    y = svf_bp(x, c, q)
    env = np.sin(np.pi * np.clip(xx if not up else xx, 0, 1)) ** 1.5
    if up:
        env = xx ** 2.2 * (1 - np.clip((xx - 0.94) / 0.06, 0, 1))
    y = y * env
    p = np.linspace(-0.8, 0.8, n) if up else np.linspace(0.8, -0.8, n)
    th = (p + 1) * np.pi / 4
    st = np.vstack([y * np.cos(th), y * np.sin(th)])
    return st / (np.max(np.abs(st)) + 1e-9)


def riser(dur, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    xx = np.linspace(0, 1, n)
    nz = svf_bp(r.standard_normal(n), 400 * (25 ** xx), 1.4)
    f = 110 * 2 ** (2.0 * xx ** 1.6)
    tone = sum(saw(f * 2 ** (d / 1200)) for d in (-18, -6, 6, 18)) / 4
    tone = svf_lp(tone, 300 + 7000 * xx ** 2, 1.2)
    y = (0.7 * nz + 0.5 * tone) * xx ** 2.5
    st = np.vstack([y, np.concatenate([np.zeros(240), y])[:n]])
    return st / (np.max(np.abs(st)) + 1e-9)


def fire_bed(n, seed=0, crackle_rate=26.0):
    """fire: roaring low body, breathing flame whoosh, stereo crackles"""
    r = np.random.default_rng(seed)
    roar = brown(n)
    mod = 0.55 + 0.45 * smooth_random(n, 1.3)
    roar = svf_lp(roar * mod, 380 + 260 * (mod - 0.1), 0.8)
    flame = svf_bp(pink(n) * 0.25, 900 + 700 * smooth_random(n, 0.8), 0.9) * (0.5 + 0.5 * smooth_random(n, 2.2))
    st = np.vstack([roar + flame, np.roll(roar, 3511) + np.roll(flame, 1777)])
    # crackles
    cr = np.zeros((2, n))
    k = int(n / SR * crackle_rate)
    pos = r.integers(0, n - 400, k)
    for p in pos:
        L = r.integers(30, 260)
        amp = r.pareto(2.2) * 0.25
        g = r.standard_normal(L) * np.exp(-np.arange(L) / (L / 4))
        pp = r.uniform(-1, 1)
        th = (pp + 1) * np.pi / 4
        cr[0, p:p + L] += g * amp * np.cos(th)
        cr[1, p:p + L] += g * amp * np.sin(th)
    cr = bp(cr, 1400, 9000)
    out = st / (np.max(np.abs(st)) + 1e-9) + 0.7 * cr / (np.max(np.abs(cr)) + 1e-9)
    return out / (np.max(np.abs(out)) + 1e-9)


def drone_resonance(n, root=28, seed=0, sweep_period=BAR * 2):
    """distorted low-frequency resonance (bronze body hum)"""
    t = np.arange(n) / SR
    f = mtof(root)
    x = 0.6 * saw(np.full(n, f)) + 0.6 * saw(np.full(n, f * 1.004)) + 0.4 * saw(np.full(n, f * 1.5 * 0.998))
    c = 90 + 260 * (0.5 + 0.5 * np.sin(2 * np.pi * t / sweep_period - np.pi / 2)) ** 2
    y = svf_lp(x, c, 5.0, drive=1.5)
    y = softclip(wavefold(y * 0.9, 1.4) * 1.3, 1.0)
    y = hp(lp(y, 260, 4), 30)
    y = y + 0.12 * bp(y * 3, 120, 260)   # keep a controlled growl, no whistling upper harmonics
    st = np.vstack([y, np.roll(y, 600)])
    return st / (np.max(np.abs(st)) + 1e-9)


# =============================================================================
# BASS
# =============================================================================
def bass_note(midi, dur, kind="groove", vel=1.0, seed=0):
    """returns (sub, mid) mono arrays: clean sub sine + aggressive mid layer"""
    r = np.random.default_rng(seed)
    f = mtof(midi)
    n = int((dur + 0.03) * SR)
    t = np.arange(n) / SR
    gate = dur
    env = adsr(n, 0.002, 0.08, 0.85, 0.03, gate_len=gate)
    # sub (pure, mono-safe) with a touch of 2nd harmonic for translation
    sub = np.sin(2 * np.pi * f * t + 0.0) + 0.08 * np.sin(4 * np.pi * f * t)
    sub = sub * env
    # mid: detuned saws + square through driven resonant filter with envelope
    fr = np.full(n, f)
    if kind == "drop":
        x = 0.5 * saw(fr * 2 ** (-9 / 1200)) + 0.5 * saw(fr * 2 ** (9 / 1200)) + 0.5 * square(fr * 2.0 * 2 ** (4 / 1200))
        fenv = 180 + (2600 * vel) * np.exp(-t / 0.075)
        q, drive = 2.2, 2.4
    elif kind == "final":
        x = 0.5 * saw(fr * 2 ** (-12 / 1200)) + 0.5 * saw(fr * 2 ** (12 / 1200)) + 0.6 * square(fr * 2.0)
        fenv = 200 + (3400 * vel) * np.exp(-t / 0.09)
        q, drive = 2.6, 3.0
    elif kind == "dark":
        x = 0.6 * saw(fr) + 0.4 * square(fr * 2 ** (5 / 1200))
        fenv = 140 + 500 * vel * np.exp(-t / 0.1)
        q, drive = 1.4, 1.5
    else:  # groove
        x = 0.55 * saw(fr * 2 ** (-6 / 1200)) + 0.55 * saw(fr * 2 ** (6 / 1200))
        fenv = 160 + 1500 * vel * np.exp(-t / 0.06)
        q, drive = 1.6, 1.8
    mid = svf_lp(x, fenv, q, drive=drive)
    if kind in ("drop", "final"):
        mid = softclip(wavefold(mid * 0.8, 1.3 if kind == "drop" else 1.6) * 1.5, 1.0)
    mid = mid * env
    mid = hp(mid, 95, 2)
    return fade(sub, 0.0015, 0.008), fade(mid, 0.0015, 0.008)


# =============================================================================
# BOUZOUKI / LYRE  (physical model)
# =============================================================================
_body_cache = {}


def _string_exc(f, vel, r, pick_pos=0.18):
    L = int(SR / f)
    n = max(L, 32)
    e = r.uniform(-1, 1, n)
    # brightness by velocity
    e = lp(e, 1800 + 9000 * vel, 1)
    # pick position comb
    d = max(int(pick_pos * L), 1)
    e = e - np.concatenate([np.zeros(d), e])[:n]
    return e * vel


def bouzouki(midi, dur, vel=1.0, seed=0, tremolo=False, trem_rate=None):
    """double-course steel-string bouzouki: two detuned strings (+ octave string on low course),
    plectrum excitation, body resonances. tremolo=True for sustained tremolo picking."""
    r = np.random.default_rng(seed)
    f = float(mtof(midi))
    ring = dur + 0.6
    n = int(ring * SR)
    excs = []
    if tremolo:
        rate = trem_rate or (STEP / 2)
        times = np.arange(0, dur, rate)
    else:
        times = np.array([0.0])
    out = np.zeros(n)
    for course_det, amp in ((-2.2, 1.0), (2.6, 0.85)):
        ff = f * 2 ** (course_det / 1200)
        exc = np.zeros(n)
        for j, tt in enumerate(times):
            v = vel * (1.0 if j % 2 == 0 else 0.72) * r.uniform(0.9, 1.05)
            e = _string_exc(ff, v, r, pick_pos=r.uniform(0.12, 0.22))
            o = int(tt * SR) + (0 if course_det < 0 else int(r.uniform(0.0008, 0.0025) * SR))
            if o + len(e) < n:
                exc[o:o + len(e)] += e
        s = ks_string(n, ff, 1.7 if not tremolo else 1.1, 0.12, exc)
        out += amp * s
    if midi < 60:  # octave string on lower courses (bright shimmer)
        exc = np.zeros(n)
        e = _string_exc(f * 2, vel * 0.5, r)
        exc[:len(e)] = e
        out += 0.35 * ks_string(n, f * 2, 1.2, 0.1, exc)
    # damp after note-off (player mutes)
    off = int((dur + 0.02) * SR)
    if off < n:
        out[off:] *= np.exp(-np.arange(n - off) / (0.09 * SR))
    # body: wooden bowl resonances + bright steel presence
    out = eq(out, "peak", 210, 1.2, 4.5)
    out = eq(out, "peak", 480, 1.5, 2.5)
    out = eq(out, "peak", 2900, 1.0, 3.5)
    out = eq(out, "peak", 5200, 1.5, 2.0)
    out = hp(out, 110)
    out = out / (np.max(np.abs(out)) + 1e-9) * vel
    return fade(out, 0.0, 0.01)


# =============================================================================
# AULOS  (double-reed pipe: melody pipe + drone pipe)
# =============================================================================
def aulos(midi, dur, vel=1.0, seed=0, scoop=True, vib=True, grace=None, bright=1.0):
    r = np.random.default_rng(seed)
    f = float(mtof(midi))
    n = int((dur + 0.08) * SR)
    t = np.arange(n) / SR
    fr = np.full(n, f)
    if scoop:   # reed pitch bend into the note
        fr *= 2 ** ((-55 * np.exp(-t / 0.028)) / 1200)
    if grace is not None:   # quick upper-neighbour ornament (mordent)
        gm = float(mtof(grace))
        gl = int(0.045 * SR)
        fr[:gl] = gm
        fr[gl:gl + 220] = np.linspace(gm, f, 220)
    if vib:
        depth = 22 * np.clip((t - 0.13) / 0.15, 0, 1)
        fr *= 2 ** (depth * np.sin(2 * np.pi * 5.6 * t + r.uniform(0, 6)) / 1200)
    fr *= 2 ** (smooth_random(n, 5) * 4 / 1200)
    # reed: mix of saw and square -> buzzy nasal spectrum, then waveshaped
    x = 0.6 * saw(fr) + 0.5 * square(fr * 1.0005)
    x = softclip(x * 1.6, 1.0)
    # breath noise synchronised to pitch (reed turbulence)
    br = r.standard_normal(n) * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(fr) / SR))
    br = bp(br, 1800, 7000) * 0.18
    y = x + br
    # bore formants
    y = eq(y, "peak", 1150, 2.5, 7 * bright)
    y = eq(y, "peak", 2550, 3.0, 5 * bright)
    y = eq(y, "peak", 3900, 3.0, 2)
    y = eq(y, "notch", 1750, 2.0)
    y = lp(y, 7500)
    y = hp(y, 260)
    env = adsr(n, 0.018, 0.12, 0.82, 0.05, gate_len=dur)
    env *= 1 + 0.06 * np.sin(2 * np.pi * 5.6 * t)
    return fade(y * env * vel, 0.0, 0.01)


def aulos_drone(n, midi=52, seed=0):
    r = np.random.default_rng(seed)
    f = float(mtof(midi))
    t = np.arange(n) / SR
    fr = np.full(n, f) * 2 ** (smooth_random(n, 0.7) * 6 / 1200)
    x = softclip((0.6 * saw(fr) + 0.5 * square(fr)) * 1.4, 1.0)
    x = eq(x, "peak", 1100, 2.0, 5)
    x = eq(x, "peak", 2400, 3.0, 3)
    x = lp(hp(x, 200), 5000)
    return x * (0.85 + 0.15 * smooth_random(n, 0.4))


# =============================================================================
# SYNTH LAYERS
# =============================================================================
def pluck_synth(midi, dur, vel=1.0, seed=0, bright=1.0):
    """modern pluck that sharpens the hook's attack"""
    f = float(mtof(midi))
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    fr = np.full(n, f)
    x = 0.5 * saw(fr * 2 ** (-7 / 1200)) + 0.5 * saw(fr * 2 ** (7 / 1200)) + 0.35 * square(fr * 0.5)
    c = 380 + 5200 * bright * vel * np.exp(-t / 0.07)
    y = svf_lp(x, c, 1.8, drive=1.2)
    env = adsr(n, 0.001, 0.18, 0.25, 0.08, gate_len=dur)
    return fade(hp(y * env, 180), 0.0, 0.01)


def supersaw(midi, dur, vel=1.0, seed=0, cutoff=5200.0):
    """wide 7-voice supersaw, returns stereo"""
    r = np.random.default_rng(seed)
    f = float(mtof(midi))
    n = int((dur + 0.18) * SR)
    t = np.arange(n) / SR
    det = [-26, -15, -6, 0, 6, 15, 26]
    pans = [-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9]
    L = np.zeros(n)
    R = np.zeros(n)
    for d, p in zip(det, pans):
        v = saw(np.full(n, f * 2 ** (d / 1200)))
        th = (p + 1) * np.pi / 4
        L += v * np.cos(th)
        R += v * np.sin(th)
    env = adsr(n, 0.004, 0.2, 0.7, 0.12, gate_len=dur)
    c = cutoff * (0.55 + 0.45 * np.exp(-t / 0.12))
    L = svf_lp(L, c, 0.9) * env
    R = svf_lp(R, c, 0.9) * env
    st = hp(np.vstack([L, R]), 400)
    return fade(st / 7 * vel, 0.0, 0.01)


def dark_pad(midis, dur, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    R = np.zeros(n)
    for m in midis:
        f = float(mtof(m))
        for d in (-11, -4, 4, 11):
            v = saw(np.full(n, f * 2 ** (d / 1200)))
            p = r.uniform(-0.9, 0.9)
            th = (p + 1) * np.pi / 4
            L += v * np.cos(th)
            R += v * np.sin(th)
    c = 500 + 500 * (0.5 + 0.5 * np.sin(2 * np.pi * t / (BAR * 4)))
    L = svf_lp(L, c, 1.1)
    R = svf_lp(R, c, 1.1)
    env = np.minimum(t / 1.2, 1) * np.minimum((dur - t) / 0.8, 1)
    st = np.vstack([L, R]) * env
    return hp(st / (np.max(np.abs(st)) + 1e-9), 120)
