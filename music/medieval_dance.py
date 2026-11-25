"""
"Three Insane Medieval Medical Treatments" -- 60 s medieval dance instrumental.
Fully synthesized (no samples): lute, hurdy-gurdy, wooden flute, fiddle,
folk percussion, bass, stabs and transition FX.  136 BPM, D minor / D dorian.

Run:  python3 medieval_dance.py  -> writes medieval_dance.wav (48 kHz stereo)
"""
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
BPM = 136.0
BEAT = 60.0 / BPM
STEP = BEAT / 4            # 16th note
BAR = BEAT * 4
NBARS = 34                 # 34 bars @136 = 60.0 s
LENGTH = 60.0
N = int(LENGTH * SR)
rng = np.random.default_rng(1347)

# --------------------------------------------------------------------------- utils
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def t_of(bar, step=0.0):
    return bar * BAR + step * STEP

def swing(step):
    """light swing on off-16ths, for a human tavern bounce"""
    s = float(step)
    if int(round(s)) % 2 == 1 and abs(s - round(s)) < 1e-6:
        return s + 0.08
    return s

def human(sd=0.006):
    return float(np.clip(rng.normal(0, sd), -2.5 * sd, 2.5 * sd))

def sos_filt(x, kind, f, order=2):
    if kind == "bp":
        sos = signal.butter(order, [f[0] / (SR / 2), min(f[1] / (SR / 2), 0.99)], "bandpass", output="sos")
    else:
        sos = signal.butter(order, min(f / (SR / 2), 0.99), kind, output="sos")
    return signal.sosfilt(sos, x, axis=0)

def peak_eq(x, f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    alpha = np.sin(w0) / (2 * q)
    b = [1 + alpha * A, -2 * np.cos(w0), 1 - alpha * A]
    a = [1 + alpha / A, -2 * np.cos(w0), 1 - alpha / A]
    return signal.lfilter(b, a, x, axis=0)

def high_shelf(x, f0, gain_db):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR
    alpha = np.sin(w0) / 2 * np.sqrt(2); c = np.cos(w0); sa = 2 * np.sqrt(A) * alpha
    b = [A * ((A + 1) + (A - 1) * c + sa), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sa)]
    a = [(A + 1) - (A - 1) * c + sa, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sa]
    return signal.lfilter(b, a, x, axis=0)

def adsr(n, a, d, s, r, sustain_len=None):
    a_n, d_n, r_n = max(1, int(a * SR)), max(1, int(d * SR)), max(1, int(r * SR))
    env = np.zeros(n)
    hold = n - r_n if sustain_len is None else min(n, int(sustain_len * SR))
    i = 0
    seg = np.linspace(0, 1, a_n, endpoint=False)[: max(0, hold)]
    env[: len(seg)] = seg; i = len(seg)
    seg = np.linspace(1, s, d_n, endpoint=False)[: max(0, hold - i)]
    env[i:i + len(seg)] = seg; i += len(seg)
    if hold > i:
        env[i:hold] = s
    level = env[hold - 1] if hold > 0 else 0
    tail = n - hold
    if tail > 0:
        env[hold:] = level * np.exp(-np.arange(tail) / (r_n / 5))
    return env

class Track:
    def __init__(self, name, pan=0.0, rev=0.15, gain=1.0):
        self.name, self.pan, self.rev, self.gain = name, pan, rev, gain
        self.buf = np.zeros((N + SR * 4, 2))

    def add(self, sig, t, pan=None, gain=1.0):
        p = self.pan if pan is None else pan
        start = int(round(t * SR))
        if start < 0:
            sig = sig[-start:]; start = 0
        end = min(start + len(sig), len(self.buf))
        sig = sig[: end - start] * gain
        if sig.ndim == 1:
            l = np.cos((p + 1) * np.pi / 4); r = np.sin((p + 1) * np.pi / 4)
            self.buf[start:end, 0] += sig * l * 1.414
            self.buf[start:end, 1] += sig * r * 1.414
        else:
            self.buf[start:end] += sig

# --------------------------------------------------------------------------- instruments
def ks_pluck(freq, dur, bright=0.6, decay=0.996, pick=0.13):
    """Karplus-Strong, block-vectorised, then resampled to exact pitch."""
    P = max(8, int(SR / freq))
    real_f = SR / (P + 0.5)
    ratio = freq / real_f
    n_gen = int(dur * SR * ratio) + P + 2
    y = np.zeros(n_gen + 2 * P)
    # plucked-string displacement: triangle peaked at the pick position (+ a bit of noise)
    x = np.arange(P) / P
    pk = pick * rng.uniform(0.85, 1.15)
    exc = np.where(x < pk, x / pk, (1 - x) / (1 - pk))
    exc = exc - exc.mean()
    exc = exc / np.abs(exc).max() + rng.uniform(-0.12, 0.12, P)
    # brightness of the pick: lowpass the excitation (circular)
    k = int(1 + (1 - bright) * 3)
    exc = np.real(np.fft.ifft(np.fft.fft(exc) * np.fft.fft(np.ones(k) / k, P)))
    y[:P] = exc
    y[P] = exc[-1]
    pos = P + 1
    while pos < len(y):
        end = min(pos + P, len(y))
        y[pos:end] = decay * 0.5 * (y[pos - P:end - P] + y[pos - P - 1:end - P - 1])
        pos = end
    y = y[: n_gen]
    t_src = np.arange(int(dur * SR)) * ratio
    out = np.interp(t_src, np.arange(len(y)), y)
    return out

def lute_note(m, dur, vel=1.0, bright=0.6):
    f = mtof(m)
    ring = dur + 0.35
    a = ks_pluck(f, ring, bright=bright, decay=0.9965)
    b = ks_pluck(f * 1.0025, ring, bright=bright * 0.9, decay=0.996)   # paired course
    x = a + 0.7 * b
    # damp after the written length (finger lifts)
    env = np.ones(len(x))
    off = int(dur * SR)
    if off < len(x):
        env[off:] = np.exp(-np.arange(len(x) - off) / (0.07 * SR))
    x *= env
    x = peak_eq(x, 210, 3, 1.5)    # wooden body
    x = peak_eq(x, 420, 2, 2.0)
    x = peak_eq(x, 1300, 4, 1.4)
    x = peak_eq(x, 3000, 6, 1.0)   # gut-string snap
    return x * vel * 0.5

def lute_strum(midis, dur, vel=1.0, down=True, spread=0.012):
    notes = midis if down else midis[::-1]
    total = int((dur + 0.5 + spread * len(notes)) * SR)
    out = np.zeros(total)
    for i, m in enumerate(notes):
        s = lute_note(m, dur, vel * (1 - 0.06 * i), bright=0.5)
        o = int(i * spread * SR * rng.uniform(0.8, 1.2))
        out[o:o + len(s)] += s[: total - o]
    return out * 0.55

def bowed(freqs_fn, dur, n_harm=40, vib_rate=5.6, vib_depth=0.006, vib_delay=0.18,
          attack=0.04, release=0.08, rough=0.012, nasal=False):
    """Additive band-limited bowed string; freqs_fn(t) gives Hz over time (allows slides)."""
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    f = freqs_fn(t)
    vib_env = np.clip((t - vib_delay) / 0.25, 0, 1)
    rate = vib_rate * (1 + 0.04 * np.sin(2 * np.pi * 0.7 * t + rng.uniform(0, 6)))
    f = f * (1 + vib_depth * vib_env * np.sin(2 * np.pi * np.cumsum(rate) / SR))
    f = f * (1 + rough * 0.15 * sos_filt(rng.normal(0, 1, n), "low", 30) )
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.zeros(n)
    fmax = f.max()
    for h in range(1, n_harm + 1):
        if h * fmax > SR * 0.42:
            break
        amp = 1.0 / h
        if nasal and h % 2 == 0:
            amp *= 0.55
        x += amp * np.sin(h * ph + rng.uniform(0, 6.28))
    # bow noise
    noise = sos_filt(rng.normal(0, 1, n), "bp", (1500, 7000)) * 0.08
    x = x + noise * (0.5 + 0.5 * np.abs(np.sin(ph * 0.5)))
    env = adsr(n, attack, 0.12, 0.85, release, sustain_len=dur)
    # bow pressure swell
    env *= 0.9 + 0.1 * np.sin(np.pi * np.clip(t / max(dur, 1e-3), 0, 1))
    return x * env

def fiddle_note(m, dur, vel=1.0, slide_from=None, slide_time=0.09, vib=0.0065):
    f1 = mtof(m)
    if slide_from is not None:
        f0 = mtof(slide_from)
        def fn(t):
            k = np.clip(t / slide_time, 0, 1)
            k = k * k * (3 - 2 * k)
            return f0 * (f1 / f0) ** k
    else:
        def fn(t):
            return np.full_like(t, f1)
    x = bowed(fn, dur, vib_depth=vib if dur > 0.2 else 0.002, attack=0.025)
    for f0_, g, q in ((290, 6, 2.0), (480, 3, 2.5), (1050, 4, 1.8), (2800, 5, 1.5)):
        x = peak_eq(x, f0_, g, q)
    x = sos_filt(x, "high", 180)
    return x * vel * 0.10

def gurdy_note(m, dur, vel=1.0):
    f1 = mtof(m)
    x = bowed(lambda t: np.full_like(t, f1), dur, vib_depth=0.0012, vib_delay=0.3,
              attack=0.012, release=0.05, nasal=True)
    # keys hitting the string: tiny click
    click = sos_filt(rng.normal(0, 1, 400), "bp", (800, 3000)) * np.exp(-np.arange(400) / 60)
    x[:400] += click * 0.6
    for f0_, g, q in ((700, 7, 1.6), (1600, 6, 2.0), (3200, 3, 2.0)):
        x = peak_eq(x, f0_, g, q)
    x = sos_filt(x, "high", 220)
    return x * vel * 0.075

def gurdy_drone(t0, t1, midis=(50, 57), buzz_steps=None):
    """continuous drone strings + rhythmic 'trompette' buzz (dog bridge)."""
    dur = t1 - t0
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for m in midis:
        f = mtof(m) * (1 + 0.0015 * np.sin(2 * np.pi * 0.3 * t + rng.uniform(0, 6)))
        ph = 2 * np.pi * np.cumsum(f) / SR
        for h in range(1, 30):
            if h * mtof(m) > 9000:
                break
            out += (1.0 / h) * (0.6 if h % 2 == 0 else 1.0) * np.sin(h * ph)
    out = peak_eq(out, 800, 5, 1.5)
    out = sos_filt(out, "high", 120) * 0.022
    # trompette buzz on the rhythm
    if buzz_steps is not None:
        buzz = np.zeros(n)
        f = mtof(midis[0] + 12)
        ph = 2 * np.pi * f * t
        raw = np.sign(np.sin(ph)) * (np.abs(np.sin(ph)) ** 0.3)
        raw = raw + 0.5 * rng.normal(0, 1, n)
        raw = sos_filt(raw, "bp", (400, 4500))
        gate = np.zeros(n)
        for s, ln, v in buzz_steps:
            a = int((s * STEP - 0.0) * SR); b = int((s + ln) * STEP * SR)
            if a >= n:
                continue
            seg = np.arange(min(b, n) - a)
            gate[a:a + len(seg)] = np.maximum(gate[a:a + len(seg)],
                                             v * np.exp(-seg / (0.09 * SR)) * np.minimum(1, seg / 80))
        buzz = raw * gate * 0.05
        out = out + buzz
    fade = np.minimum(1, np.minimum(t / 0.05, (dur - t) / 0.05))
    return out * np.clip(fade, 0, 1)

def flute_note(m, dur, vel=1.0, chiff=1.0):
    f1 = mtof(m)
    n = int((dur + 0.12) * SR)
    t = np.arange(n) / SR
    vib_env = np.clip((t - 0.16) / 0.3, 0, 1)
    f = f1 * (1 + 0.007 * vib_env * np.sin(2 * np.pi * 5.2 * t))
    # slight pitch scoop into the note
    f = f * (1 - 0.012 * np.exp(-t / 0.025))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.28 * np.sin(2 * ph + 0.4) + 0.12 * np.sin(3 * ph + 1) + 0.04 * np.sin(4 * ph)
    breath = rng.normal(0, 1, n)
    breath_tone = sos_filt(breath, "bp", (f1 * 0.85, f1 * 1.2), order=2) * 0.9
    breath_air = sos_filt(breath, "bp", (2500, 9000)) * 0.05
    env = adsr(n, 0.035, 0.1, 0.8, 0.1, sustain_len=dur)
    env *= 1 + 0.06 * vib_env * np.sin(2 * np.pi * 5.2 * t + 1.0)
    ch = np.zeros(n)
    cn = min(n, int(0.04 * SR))
    ch[:cn] = sos_filt(rng.normal(0, 1, cn), "bp", (1500, 6000)) * np.exp(-np.arange(cn) / (0.008 * SR))
    y = (x + breath_tone * 0.6) * env + breath_air * env + ch * 0.25 * chiff
    y = peak_eq(y, 1200, -2, 1.0)
    return y * vel * 0.16

def bass_note(m, dur, vel=1.0, sub=False):
    f = mtof(m)
    n = int((dur + 0.06) * SR)
    t = np.arange(n) / SR
    # tiny pitch thump for a bouncing attack
    fi = f * (1 + 0.04 * np.exp(-t / 0.012))
    ph = 2 * np.pi * np.cumsum(fi) / SR
    x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    saw = sum(np.sin(h * ph) / h for h in range(1, 14) if h * f < 6000)
    # plucked/filter envelope
    fenv = np.exp(-t / 0.07)
    bright = sos_filt(saw, "low", 900) * 0.35 * fenv
    y = x + bright
    y = np.tanh(y * 1.4) / 1.1
    if sub:
        y = y + 0.18 * np.sin(ph * 0.5)
    env = adsr(n, 0.004, 0.09, 0.72, 0.05, sustain_len=dur)
    return y * env * vel * 0.30

# percussion ------------------------------------------------------------------
def kick(vel=1.0, heavy=False):
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 46 + 110 * np.exp(-t / 0.032)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / (0.22 if heavy else 0.2))
    click = sos_filt(rng.normal(0, 1, n), "bp", (1800, 6000)) * np.exp(-t / 0.004) * 0.35
    skin = sos_filt(rng.normal(0, 1, n), "bp", (150, 700)) * np.exp(-t / 0.03) * 0.3   # frame-drum skin
    y = np.tanh((body + click + skin) * 1.6)
    return y * vel * 0.55

def frame_drum(vel=1.0, pitch=95, open_=True):
    """bodhran / tabor style frame drum"""
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = pitch * (1 + 0.5 * np.exp(-t / 0.015))
    ph = 2 * np.pi * np.cumsum(f) / SR
    dec = 0.13 if open_ else 0.04
    tone = (np.sin(ph) + 0.4 * np.sin(1.59 * ph) + 0.2 * np.sin(2.14 * ph)) * np.exp(-t / dec)
    slap = sos_filt(rng.normal(0, 1, n), "bp", (300, 2500)) * np.exp(-t / 0.012)
    return (tone * 0.8 + slap * 0.5) * vel * 0.32

def tabor_snare(vel=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 205 * t * (1 + 0.15 * np.exp(-t / 0.01))) * np.exp(-t / 0.05)
    nz = rng.normal(0, 1, n)
    rattle = sos_filt(nz, "bp", (1200, 7500)) * np.exp(-t / 0.085)
    y = tone * 0.6 + rattle * 0.9
    return y * vel * 0.30

def clap(vel=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR
    nz = sos_filt(rng.normal(0, 1, n), "bp", (900, 4500))
    env = np.zeros(n)
    for k, off in enumerate((0.0, 0.009, 0.018, 0.026)):
        o = int(off * SR)
        env[o:] += np.exp(-(t[: n - o]) / (0.006 if k < 3 else 0.06)) * (0.7 if k < 3 else 1.0)
    return nz * env * vel * 0.32

def tambourine(vel=1.0, long=False):
    n = int((0.25 if long else 0.12) * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f in (5200, 6100, 7350, 8400, 9900, 11200):
        y += np.sin(2 * np.pi * f * rng.uniform(0.98, 1.02) * t + rng.uniform(0, 6))
    nz = sos_filt(rng.normal(0, 1, n), "high", 6000)
    env = np.exp(-t / (0.07 if long else 0.028))
    shimmer = 1 + 0.4 * np.sin(2 * np.pi * 38 * t)
    return (y * 0.12 + nz * 0.8) * env * shimmer * vel * 0.16

def shaker(vel=1.0):
    n = int(0.08 * SR); t = np.arange(n) / SR
    nz = sos_filt(rng.normal(0, 1, n), "bp", (4000, 12000))
    env = np.minimum(1, t / 0.008) * np.exp(-t / 0.022)
    return nz * env * vel * 0.12

def spoons(vel=1.0):
    n = int(0.06 * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 1350 * t) + 0.6 * np.sin(2 * np.pi * 2900 * t)) * np.exp(-t / 0.012)
    y += sos_filt(rng.normal(0, 1, n), "bp", (2000, 8000)) * np.exp(-t / 0.004) * 0.6
    return y * vel * 0.14

def doumbek(kind="doum", vel=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    if kind == "doum":
        f = 82 * (1 + 0.35 * np.exp(-t / 0.02))
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * 0.9
        y += sos_filt(rng.normal(0, 1, n), "low", 900) * np.exp(-t / 0.01) * 0.3
        return y * vel * 0.32
    f = 620
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 1.6 * f * t)) * np.exp(-t / 0.03)
    y += sos_filt(rng.normal(0, 1, n), "bp", (2500, 9000)) * np.exp(-t / 0.006) * 0.8
    return y * vel * 0.17

def tom(pitch=110, vel=1.0):
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = pitch * (1 + 0.45 * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.3 * np.sin(1.5 * ph)) * np.exp(-t / 0.25)
    y += sos_filt(rng.normal(0, 1, n), "bp", (200, 2000)) * np.exp(-t / 0.02) * 0.4
    return np.tanh(y * 1.3) * vel * 0.36

def crash(dur=2.2, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for _ in range(26):
        f = rng.uniform(3000, 13000)
        y += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * rng.uniform(0.2, 1)
    y = y * 0.04 + sos_filt(rng.normal(0, 1, n), "high", 4500)
    env = np.exp(-t / (dur * 0.33)) * np.minimum(1, t / 0.002)
    return y * env * vel * 0.13

def reverse_cymbal(dur=1.6, vel=1.0):
    c = crash(dur, vel)[::-1]
    n = len(c); t = np.arange(n) / SR
    c *= (t / dur) ** 1.5
    return c * 1.4

def riser(dur, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = rng.normal(0, 1, n)
    out = np.zeros(n)
    blk = 1024
    for i in range(0, n, blk):
        k = i / n
        fc = 600 + 7000 * k ** 2
        seg = nz[max(0, i - 256): i + blk]
        f = sos_filt(seg, "bp", (fc * 0.7, fc * 1.4))
        out[i:i + blk] = f[-len(out[i:i + blk]):]
    return out * (t / dur) ** 2 * vel * 0.14

def stab(midis, vel=1.0, dur=0.22):
    """short orchestral stab: string ensemble + low brass + timpani-ish thump"""
    n = int((dur + 0.35) * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for m in midis:
        for d in (-0.08, 0.0, 0.07):
            f = mtof(m) * 2 ** (d / 12)
            ph = 2 * np.pi * f * t + rng.uniform(0, 6)
            for h in range(1, 18):
                if h * f > 10000:
                    break
                y += np.sin(h * ph) / h
    env = adsr(n, 0.006, 0.08, 0.45, 0.18, sustain_len=dur)
    y = sos_filt(y, "low", 4200) * env / (len(midis) * 3)
    y = peak_eq(y, 600, 3, 1.0)
    thump = np.sin(2 * np.pi * np.cumsum(70 * (1 + 0.5 * np.exp(-t / 0.02))) / SR) * np.exp(-t / 0.18)
    return (y * 0.9 + thump * 0.2) * vel * 0.45

# --------------------------------------------------------------------------- composition
# 16th-step note lists: (step, length_in_16ths, midi)
HOOK = [
    [(0, 2, 74), (2, 1, 74), (3, 1, 76), (4, 2, 77), (6, 2, 74), (8, 2, 69), (10, 2, 77), (12, 2, 76), (14, 2, 73)],
    [(0, 3, 74), (3, 1, 73), (4, 2, 74), (6, 2, 76), (8, 4, 77), (12, 2, 76), (14, 2, 72)],
    [(0, 2, 70), (2, 1, 70), (3, 1, 72), (4, 2, 74), (6, 2, 70), (8, 2, 69), (10, 2, 72), (12, 2, 70), (14, 2, 69)],
    [(0, 2, 69), (2, 2, 67), (4, 2, 65), (6, 2, 64), (8, 2, 61), (10, 2, 64), (12, 4, 69)],
]
HOOK_CH = ["Dm", "Dm", "Bb", "A"]

FLUTE = [
    [(0, 3, 74), (3, 3, 77), (6, 2, 81), (8, 2, 79), (10, 2, 77), (12, 2, 76), (14, 2, 77)],
    [(0, 3, 76), (3, 3, 72), (6, 2, 79), (8, 4, 76), (12, 2, 72), (14, 2, 74)],
    [(0, 3, 74), (3, 3, 70), (6, 2, 77), (8, 2, 74), (10, 2, 72), (12, 2, 70), (14, 2, 72)],
    [(0, 3, 73), (3, 3, 69), (6, 2, 76), (8, 6, 73), (14, 2, 76)],
    [(0, 3, 77), (3, 3, 74), (6, 2, 81), (8, 2, 82), (10, 2, 81), (12, 2, 79), (14, 2, 77)],
    [(0, 3, 79), (3, 3, 76), (6, 2, 72), (8, 2, 76), (10, 2, 79), (12, 4, 84)],
    [(0, 2, 82), (2, 2, 81), (4, 2, 79), (6, 2, 77), (8, 2, 74), (10, 2, 79), (12, 2, 77), (14, 2, 76)],
    [(0, 4, 73), (4, 2, 76), (6, 2, 79), (8, 4, 81), (12, 4, 76)],
]
FLUTE_CH = ["Dm", "C", "Bb", "A", "Dm", "C", "Gm", "A"]

DRAMA = [
    [(0, 2, 62), (2, 1, 62), (3, 1, 64), (4, 2, 65), (6, 2, 62), (8, 2, 69), (10, 2, 65), (12, 2, 64), (14, 2, 61)],
    [(0, 3, 62), (3, 1, 61), (4, 2, 62), (6, 2, 65), (8, 4, 70), (12, 2, 69), (14, 2, 67)],
    [(0, 2, 67), (2, 1, 67), (3, 1, 69), (4, 2, 70), (6, 2, 67), (8, 2, 74), (10, 2, 70), (12, 2, 69), (14, 2, 67)],
    [(0, 4, 69), (4, 2, 73), (6, 2, 76), (8, 8, 73)],
]
DRAMA2_LAST = [(0, 2, 81), (2, 2, 79), (4, 2, 77), (6, 2, 76), (8, 2, 74), (10, 2, 73), (12, 2, 70), (14, 2, 69)]
DRAMA_CH = ["Dm", "Bb", "Gm", "A"]

CHORDS = {  # (bass root midi, lute voicing)
    "Dm": (38, [50, 57, 62, 65, 69]),
    "C":  (36, [48, 55, 60, 64, 67]),
    "Bb": (34, [46, 53, 58, 62, 65]),
    "A":  (33, [45, 52, 57, 61, 64]),
    "Gm": (31, [43, 50, 55, 58, 62]),
}

# section map ---------------------------------------------------------------
# bars 0-2 intro | 3-11 groove A | 12-20 flute B | 21-30 drama C | 31-33 climax
def chord_at(bar):
    if bar < 3:
        return ["Dm", "Dm", "A"][bar]
    if bar < 11:
        return HOOK_CH[(bar - 3) % 4]
    if bar == 11:
        return "A"
    if bar < 20:
        return FLUTE_CH[bar - 12]
    if bar == 20:
        return "A"
    if bar < 29:
        return DRAMA_CH[(bar - 21) % 4]
    if bar < 31:
        return "A"
    return ["Dm", "Dm", "Dm"][bar - 31]

# --------------------------------------------------------------------------- tracks
T = {
    "kick": Track("kick", 0.0, 0.03, 1.0),
    "frame": Track("frame", -0.15, 0.12, 1.0),
    "snare": Track("snare", 0.08, 0.18, 1.0),
    "clap": Track("clap", 0.0, 0.2, 0.8),
    "tamb": Track("tamb", 0.45, 0.12, 1.0),
    "shaker": Track("shaker", -0.45, 0.1, 1.0),
    "spoons": Track("spoons", 0.3, 0.12, 1.0),
    "doum": Track("doum", -0.3, 0.12, 1.0),
    "tom": Track("tom", 0.0, 0.2, 1.0),
    "cym": Track("cym", 0.0, 0.25, 1.0),
    "fx": Track("fx", 0.0, 0.3, 1.0),
    "bass": Track("bass", 0.0, 0.02, 1.0),
    "lute": Track("lute", -0.3, 0.22, 1.0),
    "strum": Track("strum", 0.35, 0.22, 1.0),
    "fiddle": Track("fiddle", 0.22, 0.28, 1.0),
    "gurdy": Track("gurdy", -0.12, 0.25, 1.0),
    "drone": Track("drone", 0.0, 0.3, 1.0),
    "flute": Track("flute", 0.12, 0.32, 1.0),
    "stab": Track("stab", 0.0, 0.3, 1.0),
}

def play_line(track, bar, notes, fn, vel=1.0, transpose=0, legato=0.92, pan=None, ornament=False, **kw):
    for i, (s, ln, m) in enumerate(notes):
        t = t_of(bar, swing(s)) + human(0.005)
        dur = ln * STEP * legato
        v = vel * (1.0 if s % 4 == 0 else 0.86) * rng.uniform(0.9, 1.05)
        sig = fn(m + transpose, dur, v, **kw)
        track.add(sig, t, pan=pan)
        if ornament and ln >= 2 and rng.random() < 0.28 and fn is not fiddle_note:
            # quick grace-note "cut" from above, folk style
            g = fn(m + transpose + 2, 0.035, v * 0.6, **kw)
            track.add(g, t - 0.04, pan=pan)

# ---- drums -------------------------------------------------------------------
def drums_bar(bar, style):
    st = lambda s: t_of(bar, swing(s)) + human(0.004)
    if style == "intro":
        for s in (0, 8):
            T["kick"].add(kick(0.75), st(s))
        for s in range(0, 16, 2):
            T["frame"].add(frame_drum(0.55 if s % 4 == 0 else 0.35, open_=s % 4 == 0), st(s))
        for s in (4, 12):
            T["frame"].add(frame_drum(0.6, pitch=130), st(s))
        for s in (2, 6, 10, 14):
            T["tamb"].add(tambourine(0.6), st(s))
        return
    heavy = style in ("drama", "climax")
    for s in (0, 4, 8, 12):
        T["kick"].add(kick(1.0 if s == 0 else 0.92, heavy=heavy), st(s))
    if style in ("B", "drama", "climax") and bar % 2 == 1:
        T["kick"].add(kick(0.62), st(14))
    if style == "drama" and bar % 4 == 3:
        T["kick"].add(kick(0.55), st(10))
    for s in (4, 12):
        T["snare"].add(tabor_snare(0.95 * rng.uniform(0.92, 1.05)), st(s))
        T["clap"].add(clap(0.8), st(s) + 0.003)
        if heavy:  # flam
            T["snare"].add(tabor_snare(0.35), st(s) - 0.022)
    # bodhran 16ths with tasty accents
    acc = {0: 0.8, 3: 0.75, 6: 0.7, 10: 0.75, 13: 0.7}
    for s in range(16):
        v = acc.get(s, 0.22 + 0.1 * rng.random())
        if style == "A" and s in (1, 9) and rng.random() < 0.5:
            continue
        T["frame"].add(frame_drum(v, pitch=92 if s in acc else 120, open_=s in acc), st(s))
    # tambourine: offbeat 8ths loud + 16th shimmer
    for s in range(16):
        if s % 4 == 2:
            T["tamb"].add(tambourine(0.95, long=(s == 14 and bar % 2 == 1)), st(s))
        elif s % 2 == 1:
            T["tamb"].add(tambourine(0.32 if style != "A" else 0.26), st(s))
    if style in ("A", "climax"):
        for s in (3, 7, 11, 15):
            T["spoons"].add(spoons(0.6 * rng.uniform(0.8, 1.1)), st(s))
    if style in ("B", "drama", "climax"):
        for s in range(16):
            T["shaker"].add(shaker(0.9 if s % 4 == 2 else 0.45), st(s))
    if style == "B":
        pat = {0: "doum", 3: "tek", 5: "tek", 6: "doum", 8: "tek", 10: "doum", 11: "tek", 13: "tek", 14: "tek", 15: "tek"}
        if bar % 2:
            pat.update({2: "tek", 9: "tek"})
        for s, k in pat.items():
            T["doum"].add(doumbek(k, 0.9 if k == "doum" else 0.6 + 0.3 * (s % 4 == 3)), st(s))
    if heavy:
        for s, p in ((3, 82), (11, 82)):
            T["tom"].add(tom(p, 0.55), st(s))
        if style == "climax":
            for s, k in ((0, "doum"), (6, "doum"), (10, "doum"), (3, "tek"), (13, "tek"), (15, "tek")):
                T["doum"].add(doumbek(k, 0.8), st(s))

def fill(bar, from_step=8, kind="toms"):
    """percussion fill over the end of a bar"""
    pitches = [150, 135, 120, 108, 96, 86, 76, 68]
    for i, s in enumerate(range(from_step, 16)):
        t = t_of(bar, s) + human(0.003)
        if kind == "toms":
            T["tom"].add(tom(pitches[i % len(pitches)], 0.55 + 0.05 * i), t)
        else:
            T["snare"].add(tabor_snare(0.35 + 0.04 * i), t)
            T["frame"].add(frame_drum(0.5, pitch=100 + 6 * i), t)

def snare_roll(bar0, nbars):
    total = nbars * 16
    for i in range(total):
        sub = 2 if i >= total // 2 else 1
        for j in range(sub):
            s = i + j / sub
            v = 0.2 + 0.7 * (i / total) ** 1.4
            T["snare"].add(tabor_snare(v), t_of(bar0, s) + human(0.002))
        if i % 4 == 0:
            T["kick"].add(kick(0.6 + 0.4 * i / total, heavy=True), t_of(bar0, i))

# ---- bass ----------------------------------------------------------------
BOUNCE = [(0, 1, 0), (2, 2, 12), (6, 1, 12), (7, 1, 0), (8, 1, 0), (10, 2, 12), (13, 1, 7), (14, 2, 12)]
BOUNCE_B = [(0, 1, 0), (2, 1, 12), (3, 1, 0), (6, 2, 12), (8, 1, 0), (10, 1, 12), (11, 1, 10), (12, 1, 7), (14, 2, 12)]

def bass_bar(bar, style):
    ch = chord_at(bar)
    root = CHORDS[ch][0] + 12  # D3 range: 50
    if style == "intro":
        T["bass"].add(bass_note(root - 12, BAR * 1.0, 0.7, sub=False), t_of(bar))
        return
    pat = BOUNCE_B if style in ("B",) else BOUNCE
    deep = style in ("drama", "climax")
    for s, ln, iv in pat:
        m = root - 12 + iv
        if ch == "A" and iv == 10:
            m = root - 12 + 11
        v = 1.0 if iv == 0 else 0.85
        T["bass"].add(bass_note(m, ln * STEP * 0.85, v, sub=deep and iv == 0), t_of(bar, swing(s)) + human(0.003))

# ---- lute accompaniment ---------------------------------------------------------
def lute_comp(bar, style):
    ch = CHORDS[chord_at(bar)][1]
    if style == "intro":
        for s in (0, 4, 8, 12):
            T["strum"].add(lute_strum(ch[1:], BEAT * 0.8, 0.55, down=True), t_of(bar, s) + human(0.006))
        return
    if style in ("A", "climax"):
        # offbeat skank strums: the tavern bounce
        for s in (2, 6, 10, 14):
            T["strum"].add(lute_strum(ch[1:], STEP * 1.4, 0.75, down=(s % 4 == 2)), t_of(bar, swing(s)) + human(0.006))
        for s in (0, 8):
            T["strum"].add(lute_strum(ch[:3], STEP * 1.5, 0.5), t_of(bar, s) + human(0.006))
    elif style == "B":
        arp = [ch[0], ch[2], ch[3], ch[4], ch[3], ch[2], ch[3], ch[1]]
        for i, m in enumerate(arp):
            for k in range(2):
                s = i * 2 + k
                note = arp[(i * 2 + k) % 8]
                T["lute"].add(lute_note(note, STEP * 1.6, 0.62 if s % 4 == 0 else 0.45), t_of(bar, swing(s)) + human(0.005), pan=-0.4)
    elif style == "drama":
        for s in (0, 3, 6, 10, 12, 14):
            T["strum"].add(lute_strum(ch[1:], STEP * 1.6, 0.8 if s in (0, 6, 12) else 0.55, down=s % 4 != 2), t_of(bar, s) + human(0.006))

# --------------------------------------------------------------------------- arrangement
# drone with rhythmic trompette across whole piece (changes with chords)
def drone_section(b0, b1, buzz=True, midis=(50, 57)):
    steps = []
    if buzz:
        for b in range(b0, b1):
            for s in (2, 6, 10, 14):
                steps.append(((b - b0) * 16 + s, 1.5, 1.0))
            steps.append(((b - b0) * 16 + 7, 0.8, 0.5))
            steps.append(((b - b0) * 16 + 15, 0.8, 0.5))
    T["drone"].add(gurdy_drone(t_of(b0), t_of(b1) + 0.05, midis, steps if buzz else None), t_of(b0))

# INTRO (bars 0-2): hook instantly, sparse enough for the spoken line
drone_section(0, 3, buzz=False)
play_line(T["gurdy"], 0, HOOK[0], gurdy_note, vel=0.85)
play_line(T["gurdy"], 1, HOOK[1], gurdy_note, vel=0.85)
play_line(T["lute"], 0, HOOK[0], lute_note, vel=0.55, transpose=-12, pan=-0.45)
play_line(T["lute"], 1, HOOK[1], lute_note, vel=0.55, transpose=-12, pan=-0.45)
play_line(T["gurdy"], 2, HOOK[3][:4], gurdy_note, vel=0.85)
for b in range(3):
    drums_bar(b, "intro")
    bass_bar(b, "intro")
    lute_comp(b, "intro")
# intro turnaround: lute run + string slide + reverse cymbal into the drop
for i, (s, m) in enumerate([(8, 61), (9, 64), (10, 67), (11, 69), (12, 70), (13, 69), (14, 67), (15, 64)]):
    T["lute"].add(lute_note(m, STEP * 0.9, 0.75), t_of(2, s) + human(0.003), pan=-0.3)
T["fiddle"].add(fiddle_note(81, BEAT * 1.6, 0.9, slide_from=69, slide_time=BEAT * 1.4), t_of(2, 9))
fill(2, 12, "snare")
T["fx"].add(reverse_cymbal(BEAT * 2.0, 1.0), t_of(3) - BEAT * 2.0)

# GROOVE A (bars 3-11)
drone_section(3, 12, buzz=True)
for b in range(3, 11):
    k = (b - 3) % 4
    play_line(T["lute"], b, HOOK[k], lute_note, vel=0.95, ornament=True, bright=0.75)
    if b >= 7:  # second pass: fiddle joins an octave up-ish & hurdy-gurdy in unison
        play_line(T["fiddle"], b, HOOK[k], fiddle_note, vel=0.75)
        play_line(T["gurdy"], b, HOOK[k], gurdy_note, vel=0.45, transpose=-12)
    drums_bar(b, "A")
    bass_bar(b, "A")
    lute_comp(b, "A")
T["cym"].add(crash(2.0, 0.9), t_of(3))
T["stab"].add(stab([50, 57, 62, 65], 0.9), t_of(3))
# bar 11: transition — rhythmic break + string slide + fill
drums_bar(11, "A")
bass_bar(11, "A")
lute_comp(11, "A")
for s, ln, m in [(0, 2, 69), (2, 2, 73), (4, 2, 76), (6, 2, 79)]:
    T["fiddle"].add(fiddle_note(m, ln * STEP * 0.9, 0.85), t_of(11, s) + human(0.004))
T["fiddle"].add(fiddle_note(81, BEAT * 2.0, 0.9, slide_from=76, slide_time=0.12), t_of(11, 8))
fill(11, 8, "toms")
T["fx"].add(reverse_cymbal(BEAT * 2.0), t_of(12) - BEAT * 2.0)
T["bass"].add(bass_note(45, STEP * 2, 1.1), t_of(11, 14))   # bass accent pickup

# FLUTE VARIATION B (bars 12-20)
drone_section(12, 21, buzz=True)
T["cym"].add(crash(2.2, 0.85), t_of(12))
T["stab"].add(stab([50, 57, 62, 65], 0.8), t_of(12))
for b in range(12, 20):
    play_line(T["flute"], b, FLUTE[b - 12], flute_note, vel=1.0, ornament=True)
    drums_bar(b, "B")
    bass_bar(b, "B")
    lute_comp(b, "B")
    # gurdy answers on the off-phrases (call & response)
    if (b - 12) % 2 == 1:
        ch = chord_at(b)
        ans = {"C": [79, 76, 72], "A": [76, 73, 69], "Gm": [74, 70, 67]}.get(ch, [77, 74, 69])
        for i, m in enumerate(ans):
            T["gurdy"].add(gurdy_note(m - 12, STEP * 1.6, 0.4), t_of(b, 13 + i) + human(0.004))
# bar 20: rhythmic break — kick/snare drop out, bodhran + doumbek keep it moving
for s in range(16):
    v = 0.45 + 0.4 * (s / 15)
    T["frame"].add(frame_drum(v, pitch=92 + 3 * s, open_=s % 2 == 0), t_of(20, s) + human(0.003))
for s, k in ((0, "doum"), (3, "tek"), (6, "doum"), (8, "tek"), (10, "doum"), (12, "tek"), (13, "tek"), (14, "tek"), (15, "tek")):
    T["doum"].add(doumbek(k, 0.8), t_of(20, s))
T["bass"].add(bass_note(45, BEAT * 1.8, 1.0), t_of(20))
T["bass"].add(bass_note(33, BEAT * 1.0, 1.1, sub=True), t_of(20, 12))
T["flute"].add(flute_note(81, BEAT * 1.5, 0.9), t_of(20))
for i, m in enumerate([79, 77, 76, 73]):
    T["flute"].add(flute_note(m, STEP * 0.9, 0.85, chiff=1.3), t_of(20, 8 + i))
T["fiddle"].add(fiddle_note(74, BEAT * 1.5, 0.9, slide_from=62, slide_time=BEAT * 1.2), t_of(20, 10))
T["stab"].add(stab([45, 52, 57, 61], 0.7, dur=0.12), t_of(20, 6))
T["fx"].add(reverse_cymbal(BEAT * 2.0, 1.1), t_of(21) - BEAT * 2.0)

# DRAMATIC SECTION C (bars 21-30)
drone_section(21, 29, buzz=True, midis=(50, 57, 62))
T["cym"].add(crash(2.6, 1.0), t_of(21))
T["stab"].add(stab([38, 50, 57, 62, 65], 1.05, dur=0.3), t_of(21))
for b in range(21, 29):
    k = (b - 21) % 4
    line = DRAMA[k]
    tr = 0 if b < 25 else 12
    if b == 28:
        line, tr = DRAMA2_LAST, 0
    play_line(T["fiddle"], b, line, fiddle_note, vel=0.95, transpose=tr)
    play_line(T["gurdy"], b, line, gurdy_note, vel=0.7, transpose=tr - 12 if tr else tr)
    if b >= 25:  # harmony in thirds below on lute
        play_line(T["lute"], b, line, lute_note, vel=0.55, transpose=tr - 12 - 3 if k != 3 else tr - 12 - 4)
    drums_bar(b, "drama")
    bass_bar(b, "drama")
    lute_comp(b, "drama")
    # orchestral stabs pushing the offbeats
    ch = CHORDS[chord_at(b)][1]
    for s in (6, 14) if b % 2 == 0 else (14,):
        T["stab"].add(stab(ch[:4], 0.6, dur=0.1), t_of(b, s) + human(0.003))
T["cym"].add(crash(2.0, 0.7), t_of(25))
T["stab"].add(stab([38, 50, 57, 62, 65], 0.9, dur=0.25), t_of(25))
# BUILD (bars 29-30): A pedal, snare roll, rising fiddle tremolo, riser
drone_section(29, 31, buzz=False, midis=(45, 52))
snare_roll(29, 2)
for s in range(32):
    m = [69, 69, 70, 69, 73, 73, 74, 73][s // 4] + (12 if s >= 24 else 0)
    T["fiddle"].add(fiddle_note(m, STEP * 0.8, 0.55 + 0.4 * s / 31), t_of(29, s) + human(0.002))
for b in (29, 30):
    for s in (0, 2, 4, 6, 8, 10, 12, 14):
        T["bass"].add(bass_note(33 + (12 if s % 4 == 2 else 0), STEP * 1.6, 0.9, sub=(s % 4 == 0)), t_of(b, s))
T["gurdy"].add(gurdy_note(69, BAR * 2 - STEP, 0.6), t_of(29))
T["fx"].add(riser(BAR * 2, 1.0), t_of(29))
T["stab"].add(stab([45, 52, 57, 61], 0.8, dur=0.12), t_of(30, 12))
T["stab"].add(stab([45, 52, 57, 61], 0.85, dur=0.12), t_of(30, 14))
T["fx"].add(reverse_cymbal(BEAT * 2.0, 1.2), t_of(31) - BEAT * 2.0)
T["fiddle"].add(fiddle_note(86, BEAT * 1.0, 0.9, slide_from=74, slide_time=BEAT * 0.9), t_of(30, 12))

# CLIMAX (bars 31-33): full hook tutti
drone_section(31, 34, buzz=True, midis=(50, 57, 62))
T["cym"].add(crash(2.4, 1.1), t_of(31))
T["stab"].add(stab([38, 50, 57, 62, 65, 69], 1.15, dur=0.3), t_of(31))
CLIMAX_END = [(0, 2, 69), (2, 2, 73), (4, 2, 76), (6, 2, 73), (8, 4, 74), (12, 1, 69), (13, 1, 73), (14, 1, 76), (15, 1, 73)]
for i, b in enumerate((31, 32, 33)):
    line = [HOOK[0], HOOK[1], CLIMAX_END][i]
    play_line(T["fiddle"], b, line, fiddle_note, vel=1.0)
    play_line(T["flute"], b, line, flute_note, vel=0.8, transpose=12 if i < 2 else 0)
    play_line(T["gurdy"], b, line, gurdy_note, vel=0.7, transpose=-12)
    play_line(T["lute"], b, line, lute_note, vel=0.85, bright=0.8)
    drums_bar(b, "climax")
    if b < 33:
        bass_bar(b, "climax")
        lute_comp(b, "climax")
T["cym"].add(crash(1.6, 0.8), t_of(32))
# final bar: big hit on beat 3 (resolution), then loop pickup groove keeps moving
for s in (0, 4):
    T["bass"].add(bass_note(33 + (12 if s else 0), STEP * 1.8, 1.0, sub=True), t_of(33, s))
T["stab"].add(stab([45, 52, 57, 61, 64], 0.9, dur=0.12), t_of(33, 6))
T["stab"].add(stab([38, 50, 57, 62, 65, 69], 1.2, dur=0.45), t_of(33, 8))
T["cym"].add(crash(1.9, 1.0), t_of(33, 8))
T["bass"].add(bass_note(38, STEP * 3.5, 1.15, sub=True), t_of(33, 8))
T["bass"].add(bass_note(45, STEP * 1.5, 0.9), t_of(33, 12))
T["bass"].add(bass_note(49, STEP * 1.5, 0.9), t_of(33, 14))
T["strum"].add(lute_strum(CHORDS["Dm"][1], BEAT * 1.5, 1.0), t_of(33, 8))
T["strum"].add(lute_strum(CHORDS["A"][1][1:], STEP * 1.5, 0.7), t_of(33, 14))

# --------------------------------------------------------------------------- mix
def kick_sidechain():
    env = np.zeros(len(T["kick"].buf))
    k = np.abs(T["kick"].buf[:, 0])
    k = sos_filt(k, "low", 30)
    k = k / (k.max() + 1e-9)
    return 1 - 0.5 * np.clip(k * 2.2, 0, 1)

def make_ir(seconds=1.3):
    n = int(seconds * SR); t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        nz = rng.normal(0, 1, n)
        nz = sos_filt(nz, "low", 6500)
        env = np.exp(-t / (seconds / 6.9 * 2.0)) * np.minimum(1, t / 0.012)
        ir[:, c] = nz * env
        # a few early reflections (wooden tavern)
        for d, g in ((0.011, 0.5), (0.019, 0.35), (0.029, 0.3), (0.041, 0.22)):
            ir[int((d + 0.002 * c) * SR), c] += g * 8
    ir = sos_filt(ir, "high", 250)
    return ir / np.sqrt((ir ** 2).sum())

sc = kick_sidechain()
bus = np.zeros_like(T["kick"].buf)
send = np.zeros_like(bus)
levels = {
    "kick": 1.2, "frame": 0.8, "snare": 1.0, "clap": 0.75, "tamb": 1.35, "shaker": 1.1,
    "spoons": 1.0, "doum": 0.75, "tom": 0.85, "cym": 0.6, "fx": 0.8, "bass": 1.35,
    "lute": 1.0, "strum": 0.75, "fiddle": 0.85, "gurdy": 0.8, "drone": 0.9, "flute": 0.85, "stab": 0.6,
}
ducked = {"bass": 1.0, "strum": 0.5, "drone": 0.6, "stab": 0.3, "gurdy": 0.25, "tamb": 0.3}
for name, tr in T.items():
    x = tr.buf * levels[name]
    if name in ducked:
        d = ducked[name]
        x = x * ((1 - d) + d * sc)[:, None]
    if name == "bass":
        x = sos_filt(x, "high", 30)
    elif name not in ("kick", "tom"):
        x = sos_filt(x, "high", 90 if name not in ("drone", "stab", "doum", "frame") else 45)
    bus += x
    send += x * tr.rev

ir = make_ir(1.4)
wet = np.stack([signal.fftconvolve(send[:, c], ir[:, c])[: len(send)] for c in range(2)], axis=1)
mix = bus + wet * 1.1

# tone shaping: warmth + air, a little low-mid cleanup
mix = peak_eq(mix, 280, -2.5, 0.9)
mix = peak_eq(mix, 90, 1.0, 0.8)
mix = sos_filt(mix, "high", 28)
mix = high_shelf(mix, 3500, 5.0)
mix = peak_eq(mix, 2500, 1.5, 1.0)

# glue compressor (RMS, gentle)
def compress(x, thresh_db=-16, ratio=2.2, att=0.01, rel=0.15):
    lvl = np.sqrt(sos_filt((x ** 2).mean(axis=1), "low", 12).clip(1e-12))
    db = 20 * np.log10(lvl)
    over = np.maximum(0, db - thresh_db)
    gr = -over * (1 - 1 / ratio)
    g = 10 ** (gr / 20)
    # smooth
    out = np.empty_like(g); prev = 1.0
    a_a, a_r = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    for i in range(0, len(g), 64):
        tgt = g[i:i + 64].min()
        coef = a_a if tgt < prev else a_r
        prev = coef ** 64 * prev + (1 - coef ** 64) * tgt
        out[i:i + 64] = prev
    return x * out[:, None]

mix = mix[:N]
peak = np.abs(mix).max()
mix = mix / peak * 0.6
mix = compress(mix)
mix = np.tanh(mix * 1.6) / np.tanh(1.6)   # soft saturation

# lookahead limiter
def limit(x, ceiling=0.84, look=0.003, rel=0.06):
    la = int(look * SR)
    up = signal.resample_poly(x, 4, 1, axis=0)       # true-peak (4x oversampled) detection
    pk = np.abs(up).max(axis=1)[: len(x) * 4].reshape(-1, 4).max(axis=1)
    from scipy.ndimage import maximum_filter1d
    pk = maximum_filter1d(pk, size=2 * la + 1)
    g = np.minimum(1.0, ceiling / np.maximum(pk, 1e-9))
    # release smoothing (instant attack thanks to lookahead window)
    out = np.empty_like(g); prev = 1.0
    a_r = np.exp(-1 / (rel * SR))
    for i in range(len(g)):
        v = g[i]
        prev = v if v < prev else a_r * prev + (1 - a_r) * v
        out[i] = prev
    out = sos_filt(out, "low", 400)
    return x * np.minimum(out, g)[:, None]

def loudness_gain(x, target=-10.5):
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(SR)
        l = meter.integrated_loudness(x)
        return 10 ** ((target - l) / 20), l
    except Exception:
        return 1.0, None

g, l0 = loudness_gain(mix)
mix = mix * g
mix = limit(mix)
# tiny fades so the file is click-free while still loop-friendly
fi, fo = int(0.004 * SR), int(0.03 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix[-fo:] *= np.linspace(1, 0.6, fo)[:, None]

import sys
out = sys.argv[1] if len(sys.argv) > 1 else "medieval_dance.wav"
wavfile.write(out, SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
print("written", out, "len", len(mix) / SR, "pre-loudness", l0)
