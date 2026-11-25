"""
MEDIEVAL MEDICINE -- 60 s soundtrack for "Three Insane Medieval Medical Treatments"
Medieval folk x electro swing x dance funk.  134 BPM, D minor -> climax in E minor.

Everything musical is synthesised here from physical/additive models; the four
human reactions are the supplied ElevenLabs recordings (music/vox/*.wav), chopped,
processed (EQ, compression, short plate) and placed on the beat grid.

    python3 medieval_medicine.py [outdir]

writes  MEDIEVAL_MEDICINE_FINAL.wav, MEDIEVAL_MEDICINE_INSTRUMENTAL.wav,
        MEDIEVAL_MEDICINE_VOX_STEM.wav, MEDIEVAL_MEDICINE_VOX_TIMESTAMPS.md
"""
import os
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import maximum_filter1d

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
SR = 48000
BPM = 134.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
U = BEAT / 3                    # one swung-triplet unit (12 per bar)
LENGTH = 60.0
N = int(round(LENGTH * SR))
PAD = 3 * SR
rng = np.random.default_rng(20261125)

# ============================================================================ DSP helpers
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

SWING_PTS = [0.0, 0.34, 0.63, 1.0]     # soft electro-swing shuffle

def tu(bar, u):
    """time (s) of swung-triplet unit u (0..11, may be fractional) in bar"""
    u = float(u)
    b = int(np.floor(u / 3)); r = u - 3 * b
    i = min(int(r), 2); fr = r - i
    frac = SWING_PTS[i] + (SWING_PTS[i + 1] - SWING_PTS[i]) * fr
    return bar * BAR + (b + frac) * BEAT

def hum(sd=0.005):
    return float(np.clip(rng.normal(0, sd), -2.5 * sd, 2.5 * sd))

def filt(x, kind, f, order=2):
    nyq = SR / 2
    if kind == "bp":
        sos = signal.butter(order, [max(f[0], 10) / nyq, min(f[1] / nyq, 0.99)], "bandpass", output="sos")
    else:
        sos = signal.butter(order, min(f / nyq, 0.99), kind, output="sos")
    return signal.sosfilt(sos, x, axis=0)

def peq(x, f0, g, q):
    A = 10 ** (g / 40); w = 2 * np.pi * f0 / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return signal.lfilter(b, a, x, axis=0)

def shelf(x, f0, g, high=True):
    A = 10 ** (g / 40); w = 2 * np.pi * f0 / SR; c = np.cos(w)
    al = np.sin(w) / 2 * np.sqrt(2); sa = 2 * np.sqrt(A) * al
    if high:
        b = [A * ((A + 1) + (A - 1) * c + sa), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sa)]
        a = [(A + 1) - (A - 1) * c + sa, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sa]
    else:
        b = [A * ((A + 1) - (A - 1) * c + sa), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sa)]
        a = [(A + 1) + (A - 1) * c + sa, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sa]
    return signal.lfilter(b, a, x, axis=0)

def env_ar(n, att, rel_tau, hold=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(att, 1e-4))
    if hold is not None:
        k = int(hold * SR)
        if k < n:
            e[k:] *= np.exp(-(t[k:] - t[k]) / rel_tau)
    return e

def adsr(n, a, d, s, r, length):
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    k = int(length * SR)
    if k < n:
        e[k:] = e[k] * np.exp(-(t[k:] - t[k]) / r)
    return e

class Track:
    def __init__(self, pan=0.0, rev=0.1, plate=0.0, gain=1.0):
        self.pan, self.rev, self.plate, self.gain = pan, rev, plate, gain
        self.buf = np.zeros((N + PAD, 2))

    def add(self, x, t, pan=None, gain=1.0):
        p = self.pan if pan is None else pan
        s = int(round(t * SR))
        if s < 0:
            x = x[-s:]; s = 0
        e = min(s + len(x), len(self.buf))
        if e <= s:
            return
        x = x[: e - s] * gain
        if x.ndim == 1:
            self.buf[s:e, 0] += x * np.cos((p + 1) * np.pi / 4) * 1.4142
            self.buf[s:e, 1] += x * np.sin((p + 1) * np.pi / 4) * 1.4142
        else:
            self.buf[s:e] += x

# ============================================================================ instruments
def ks(freq, dur, bright=0.7, decay=0.996, pick=0.13, hammer=False):
    """Karplus-Strong string, block vectorised, resampled to exact pitch"""
    P = max(8, int(SR / freq)); ratio = freq / (SR / (P + 0.5))
    n_gen = int(dur * SR * ratio) + 2 * P + 2
    y = np.zeros(n_gen + P)
    x = np.arange(P) / P
    if hammer:
        exc = np.exp(-((x - pick) / 0.03) ** 2) - np.exp(-((x - pick - 0.06) / 0.03) ** 2)
        exc = exc / np.abs(exc).max() + rng.uniform(-0.25, 0.25, P)
    else:
        pk = pick * rng.uniform(0.85, 1.15)
        exc = np.where(x < pk, x / pk, (1 - x) / (1 - pk)); exc -= exc.mean()
        exc = exc / np.abs(exc).max() + rng.uniform(-0.1, 0.1, P)
    k = int(1 + (1 - bright) * 3)
    exc = np.real(np.fft.ifft(np.fft.fft(exc) * np.fft.fft(np.ones(k) / k, P)))
    y[:P] = exc; y[P] = exc[-1]
    pos = P + 1
    while pos < len(y):
        e = min(pos + P, len(y))
        y[pos:e] = decay * 0.5 * (y[pos - P:e - P] + y[pos - P - 1:e - P - 1])
        pos = e
    return np.interp(np.arange(int(dur * SR)) * ratio, np.arange(len(y)), y)

def pluck_add(freq, dur, n_h=24, tilt=1.0, d0=1.5, d1=0.9, pick=0.2, glide=None, gtime=0.06):
    """additive plucked string with frequency-dependent damping and optional glide"""
    n = int(dur * SR); t = np.arange(n) / SR
    if glide is not None:
        k = np.clip(t / gtime, 0, 1); k = k * k * (3 - 2 * k)
        f = glide * (freq / glide) ** k
    else:
        f = np.full(n, freq)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n)
    for h in range(1, n_h + 1):
        if h * freq > SR * 0.42:
            break
        a = abs(np.sin(np.pi * h * pick)) / h ** tilt
        y += a * np.exp(-t * (d0 + d1 * h ** 1.3)) * np.sin(h * ph * (1 + 0.0004 * h))
    return y

def lute(m, dur, vel=1.0, bright=0.7):
    f = mtof(m) * 2 ** (rng.normal(0, 2.5) / 1200)
    ring = dur + 0.4
    x = ks(f, ring, bright, 0.9965) + 0.65 * ks(f * 1.0022, ring, bright * 0.9, 0.996)
    off = int(dur * SR)
    if off < len(x):
        x[off:] *= np.exp(-np.arange(len(x) - off) / (0.06 * SR))
    for f0, g, q in ((200, 3, 1.5), (420, 2, 2), (1300, 4, 1.4), (3000, 5, 1.0)):
        x = peq(x, f0, g, q)
    return filt(x, "high", 70) * vel * 0.45

def strum(ms, dur, vel=1.0, down=True, spread=0.009, inst="lute"):
    ms = ms if down else ms[::-1]
    tot = int((dur + 0.5 + spread * len(ms)) * SR); out = np.zeros(tot)
    for i, m in enumerate(ms):
        s = lute(m, dur, vel * (1 - 0.07 * i), 0.55) if inst == "lute" else pizz(m, vel * (1 - 0.05 * i))
        o = int(i * spread * SR * rng.uniform(0.7, 1.3))
        out[o:o + len(s)] += s[: tot - o]
    return out * 0.6

def pizz(m, vel=1.0):
    f = mtof(m) * 2 ** (rng.normal(0, 3) / 1200)
    x = pluck_add(f, 0.45, n_h=18, tilt=1.25, d0=7, d1=1.6, pick=0.27)
    x += 0.5 * pluck_add(f * 1.003, 0.45, n_h=14, tilt=1.3, d0=8, d1=1.8, pick=0.3)
    x = peq(x, 280, 4, 1.4); x = peq(x, 1100, 3, 1.2)
    x[:200] += filt(rng.normal(0, 1, 200), "bp", (1500, 6000)) * np.exp(-np.arange(200) / 40) * 0.3
    return x * vel * 0.32

def dulcimer(m, vel=1.0):
    f = mtof(m)
    x = sum(ks(f * d, 1.6, 1.0, 0.9985, pick=0.09, hammer=True) for d in (1.0, 1.0016, 0.9987))
    x = peq(x, 2500, 4, 1.0); x = filt(x, "high", 150)
    return x * vel * 0.14

def bowed(fn, dur, harm=36, vib=0.006, vib_delay=0.15, vib_rate=5.7, att=0.03, rel=0.07,
          nasal=False, spic=False, swell=True):
    n = int((dur + rel + 0.05) * SR); t = np.arange(n) / SR
    f = fn(t)
    ve = np.clip((t - vib_delay) / 0.22, 0, 1)
    rate = vib_rate * (1 + 0.05 * np.sin(2 * np.pi * 0.6 * t + rng.uniform(0, 6)))
    f = f * (1 + vib * ve * np.sin(2 * np.pi * np.cumsum(rate) / SR + rng.uniform(0, 6)))
    f = f * (1 + 0.0015 * filt(rng.normal(0, 1, n), "low", 25))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n); fm = f.max()
    for h in range(1, harm + 1):
        if h * fm > SR * 0.42:
            break
        a = 1.0 / h
        if nasal and h % 2 == 0:
            a *= 0.55
        y += a * np.sin(h * ph + rng.uniform(0, 6.28))
    nz = filt(rng.normal(0, 1, n), "bp", (1800, 8000)) * 0.07
    y = y + nz * (0.6 + 0.4 * np.abs(np.sin(ph * 0.5)))
    if spic:
        e = np.minimum(1, t / 0.006) * np.exp(-t / max(0.05, dur * 0.55))
        k = int(dur * SR)
        if k < n:
            e[k:] *= np.exp(-(t[k:] - t[k]) / 0.03)
        # bow scratch at the start
        sc = min(n, int(0.02 * SR))
        y[:sc] += filt(rng.normal(0, 1, sc), "bp", (800, 5000)) * np.exp(-np.arange(sc) / (0.004 * SR)) * 0.5
    else:
        e = adsr(n, att, 0.12, 0.86, rel, dur)
        if swell:
            e *= 0.88 + 0.12 * np.sin(np.pi * np.clip(t / max(dur, 1e-3), 0, 1))
    return y * e

def fiddle(m, dur, vel=1.0, art="spic", scoop=False, slide_from=None, stime=0.1, det=0.0):
    f1 = mtof(m) * 2 ** ((det + rng.normal(0, 2)) / 1200)
    if slide_from is not None:
        f0 = mtof(slide_from)
        fn = lambda t: f0 * (f1 / f0) ** (lambda k: k * k * (3 - 2 * k))(np.clip(t / stime, 0, 1))
    elif scoop:
        fn = lambda t: f1 * 2 ** (-0.9 / 12 * np.exp(-t / 0.035))
    else:
        fn = lambda t: np.full_like(t, f1)
    if art == "spic":
        x = bowed(fn, dur, vib=0.002, spic=True)
    else:
        x = bowed(fn, dur, vib=0.0065 if dur > 0.25 else 0.003, att=0.03)
    for f0, g, q in ((290, 6, 2), (480, 3, 2.5), (1050, 4, 1.8), (2800, 5, 1.5)):
        x = peq(x, f0, g, q)
    return filt(x, "high", 190) * vel * 0.085

def flute(m, dur, vel=1.0, chiff=1.0, vib=True):
    f1 = mtof(m) * 2 ** (rng.normal(0, 2) / 1200)
    n = int((dur + 0.12) * SR); t = np.arange(n) / SR
    ve = np.clip((t - 0.14) / 0.25, 0, 1) if vib and dur > 0.22 else np.zeros(n)
    f = f1 * (1 + 0.007 * ve * np.sin(2 * np.pi * 5.3 * t)) * (1 - 0.012 * np.exp(-t / 0.02))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph + 0.4) + 0.13 * np.sin(3 * ph + 1) + 0.04 * np.sin(4 * ph)
    br = rng.normal(0, 1, n)
    tone_n = filt(br, "bp", (f1 * 0.85, f1 * 1.2))
    air = filt(br, "bp", (2500, 9000)) * 0.05
    e = adsr(n, 0.025, 0.09, 0.78, 0.07, dur) * (1 + 0.06 * ve * np.sin(2 * np.pi * 5.3 * t + 1))
    ch = np.zeros(n); cn = min(n, int(0.035 * SR))
    ch[:cn] = filt(rng.normal(0, 1, cn), "bp", (1500, 6500)) * np.exp(-np.arange(cn) / (0.007 * SR))
    y = (x + tone_n * 0.55 + air) * e + ch * 0.3 * chiff
    return peq(y, 1200, -2, 1.0) * vel * 0.15

def shawm(m, dur, vel=1.0, det=0.0):
    """medieval double-reed: the 'horn section' of the tavern"""
    f1 = mtof(m) * 2 ** ((det + rng.normal(0, 3)) / 1200)
    n = int((dur + 0.1) * SR); t = np.arange(n) / SR
    f = f1 * (1 + 0.004 * np.clip((t - 0.15) / 0.2, 0, 1) * np.sin(2 * np.pi * 5.0 * t)) \
        * (1 - 0.02 * np.exp(-t / 0.02))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n)
    for h in range(1, 40):
        if h * f1 > SR * 0.42:
            break
        y += np.sin(h * ph + 0.3 * h) / h ** 0.75
    y = np.tanh(y * 0.8)
    y += filt(rng.normal(0, 1, n), "bp", (1000, 4000)) * 0.05
    e = adsr(n, 0.012, 0.06, 0.7, 0.05, dur)
    for f0, g, q in ((1150, 8, 1.6), (2500, 5, 2), (450, -3, 1.0)):
        y = peq(y, f0, g, q)
    y = filt(y, "low", 7000); y = filt(y, "high", 200)
    return y * e * vel * 0.03

def bass(m, dur, vel=1.0, pop=False, slide_from=None, sub=0.0):
    f = mtof(m)
    x = pluck_add(f, dur + 0.08, n_h=26, tilt=1.05 if pop else 1.35, d0=1.2, d1=0.5 if pop else 0.9,
                  pick=0.12 if pop else 0.2, glide=None if slide_from is None else mtof(slide_from))
    n = len(x); t = np.arange(n) / SR
    x = np.tanh(x * 1.6)
    x += 0.35 * np.sin(2 * np.pi * f * t) * np.exp(-t * 1.5)          # body
    if sub:
        x += sub * np.sin(np.pi * f * t) * np.exp(-t * 2)
    if pop:
        x[:300] += filt(rng.normal(0, 1, 300), "bp", (1500, 5000)) * np.exp(-np.arange(300) / 50) * 0.5
    e = np.minimum(1, t / 0.003)
    k = int(dur * SR)
    if k < n:
        e[k:] *= np.exp(-(t[k:] - t[k]) / 0.025)
    return x * e * vel * 0.33

def gurdy_drone(dur, midis, buzz_units=None, bar0=0):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for m in midis:
        f = mtof(m) * (1 + 0.0015 * np.sin(2 * np.pi * 0.3 * t + rng.uniform(0, 6)))
        ph = 2 * np.pi * np.cumsum(f) / SR
        for h in range(1, 28):
            if h * mtof(m) > 9000:
                break
            out += (1 / h) * (0.6 if h % 2 == 0 else 1) * np.sin(h * ph)
    out = filt(peq(out, 800, 5, 1.5), "high", 120) * 0.02
    if buzz_units:
        ph = 2 * np.pi * mtof(midis[0] + 12) * t
        raw = filt(np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** 0.3 + 0.5 * rng.normal(0, 1, n), "bp", (400, 4500))
        g = np.zeros(n)
        for (b, u, v) in buzz_units:
            a = int((tu(b, u) - tu(bar0, 0)) * SR)
            if 0 <= a < n:
                seg = np.arange(min(n - a, int(0.25 * SR)))
                g[a:a + len(seg)] = np.maximum(g[a:a + len(seg)], v * np.exp(-seg / (0.08 * SR)) * np.minimum(1, seg / 80))
        out += raw * g * 0.04
    fd = np.clip(np.minimum(t / 0.08, (dur - t) / 0.08), 0, 1)
    return out * fd

# ---------------------------------------------------------------------------- drums
def kick(vel=1.0, tight=True):
    n = int(0.38 * SR); t = np.arange(n) / SR
    f = 54 + 130 * np.exp(-t / 0.028)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.17 if tight else 0.24))
    click = filt(rng.normal(0, 1, n), "bp", (2000, 7000)) * np.exp(-t / 0.003) * 0.4
    skin = filt(rng.normal(0, 1, n), "bp", (150, 800)) * np.exp(-t / 0.025) * 0.25
    return np.tanh((body + click + skin) * 1.8) * vel * 0.55

def clap(vel=1.0):
    n = int(0.32 * SR); t = np.arange(n) / SR
    nz = filt(rng.normal(0, 1, n), "bp", (900, 5200))
    e = np.zeros(n)
    for k, off in enumerate((0.0, 0.008, 0.017, 0.025)):
        o = int(off * SR)
        e[o:] += np.exp(-t[: n - o] / (0.0055 if k < 3 else 0.075)) * (0.75 if k < 3 else 1)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04) * 0.45      # tabor body under the clap
    rattle = filt(rng.normal(0, 1, n), "bp", (2500, 8000)) * np.exp(-t / 0.07) * 0.35
    return (nz * e + body + rattle) * vel * 0.3

def snap(vel=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    y = filt(rng.normal(0, 1, n), "bp", (1800, 4200)) * np.exp(-t / 0.012)
    y += np.sin(2 * np.pi * 2300 * t) * np.exp(-t / 0.006) * 0.4
    return y * vel * 0.3

def shaker(vel=1.0):
    n = int(0.09 * SR); t = np.arange(n) / SR
    return filt(rng.normal(0, 1, n), "bp", (4500, 13000)) * np.minimum(1, t / 0.009) * np.exp(-t / 0.024) * vel * 0.13

def tamb(vel=1.0, long=False):
    n = int((0.28 if long else 0.13) * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * rng.uniform(0.98, 1.02) * t + rng.uniform(0, 6)) for f in (5200, 6100, 7350, 8400, 9900, 11200))
    nz = filt(rng.normal(0, 1, n), "high", 6000)
    return (y * 0.12 + nz * 0.8) * np.exp(-t / (0.08 if long else 0.03)) * (1 + 0.4 * np.sin(2 * np.pi * 38 * t)) * vel * 0.15

def frame(vel=1.0, pitch=95, open_=True):
    n = int(0.3 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(pitch * (1 + 0.5 * np.exp(-t / 0.014))) / SR
    tone = (np.sin(ph) + 0.4 * np.sin(1.59 * ph) + 0.2 * np.sin(2.14 * ph)) * np.exp(-t / (0.12 if open_ else 0.035))
    slap = filt(rng.normal(0, 1, n), "bp", (300, 2500)) * np.exp(-t / 0.01)
    return (tone * 0.8 + slap * 0.5) * vel * 0.3

def woodblock(vel=1.0, hi=True):
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 1250 if hi else 880
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t / 0.022)
    y += filt(rng.normal(0, 1, n), "bp", (2000, 8000)) * np.exp(-t / 0.003) * 0.6
    return y * vel * 0.15

def tom(pitch=110, vel=1.0):
    n = int(0.55 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(pitch * (1 + 0.45 * np.exp(-t / 0.03))) / SR
    y = (np.sin(ph) + 0.3 * np.sin(1.5 * ph)) * np.exp(-t / 0.22)
    y += filt(rng.normal(0, 1, n), "bp", (200, 2000)) * np.exp(-t / 0.02) * 0.4
    return np.tanh(y * 1.3) * vel * 0.34

def crash(dur=2.2, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * rng.uniform(3000, 13000) * t + rng.uniform(0, 6)) * rng.uniform(0.2, 1) for _ in range(24))
    y = y * 0.04 + filt(rng.normal(0, 1, n), "high", 4500)
    return y * np.exp(-t / (dur * 0.33)) * np.minimum(1, t / 0.002) * vel * 0.12

def rev_cym(dur, vel=1.0):
    c = crash(dur, vel)[::-1]; t = np.arange(len(c)) / SR
    return c * (t / dur) ** 1.5 * 1.5

def sweep(dur, vel=1.0, up=True):
    n = int(dur * SR); nz = rng.normal(0, 1, n); out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        k = i / n if up else 1 - i / n
        fc = 500 + 7500 * k ** 2
        seg = filt(nz[max(0, i - 512): i + blk], "bp", (fc * 0.7, fc * 1.4))
        out[i:i + blk] = seg[-len(out[i:i + blk]):]
    t = np.arange(n) / dur / SR
    return out * ((t ** 2) if up else (1 - t) ** 2) * vel * 0.13

# ============================================================================ harmony / score
ROOTS = {"Dm": 38, "Gm": 43, "Bb": 46, "A7": 45, "Eb": 39, "Em": 40, "Am": 45, "C": 36, "B7": 47}
QUAL = {"Dm": "m", "Gm": "m", "Em": "m", "Am": "m", "Bb": "M", "Eb": "M", "C": "M", "A7": "7", "B7": "7"}
CHOP = {"Dm": [57, 62, 65], "Gm": [55, 58, 62], "Bb": [53, 58, 62], "A7": [55, 61, 64],
        "Eb": [55, 58, 63], "Em": [59, 64, 67], "Am": [57, 60, 64], "C": [55, 60, 64], "B7": [57, 63, 66]}
UP2 = {"Dm": "Em", "Gm": "Am", "Bb": "C", "A7": "B7"}

def chord_tones(ch):
    r = ROOTS[ch] % 12
    iv = {"m": (0, 3, 7), "M": (0, 4, 7), "7": (0, 4, 7, 10)}[QUAL[ch]]
    return [(r + i) % 12 for i in iv]

# melodic material: (unit, dur_units, midi)  -- 12 swung units per bar
CELL = [0, 2, 3, 5, 8, 9]          # "DA-da DA-daaa -da DA ." the hook rhythm
CELL_D = [1, 1, 2, 3, 1, 1]
def cell(pitches):
    return [(u, d, p) for u, d, p in zip(CELL, CELL_D, pitches)]

HOOK = [
    cell([74, 74, 77, 76, 73, 74]),                       # D D F E~ C# D
    cell([77, 77, 81, 79, 76, 77]),                       # F F A G~ E F
    cell([79, 79, 82, 81, 78, 79]),                       # G G Bb A~ F# G
    [(0, 1, 81), (1, 1, 79), (2, 1, 77), (3, 1, 76), (4, 1, 74), (5, 1, 73), (6, 2, 76), (9, 1, 69), (11, 1, 73)],
]
ANSWER3 = cell([77, 77, 82, 81, 79, 77])                  # over Bb
ANSWER4 = [(0, 1, 76), (1, 1, 77), (2, 1, 76), (3, 1, 74), (5, 1, 73), (6, 3, 74)]

FLUTE_A = [  # call (flute, beats 1-2) -> bass answers (beats 3-4)
    [(0, 1, 79), (1, 1, 77), (2, 1, 79), (3, 2, 82), (5, 1, 81)],
    [(0, 1, 81), (1, 1, 79), (2, 1, 77), (3, 2, 74), (5, 1, 77)],
    [(0, 1, 77), (2, 1, 79), (3, 1, 81), (5, 1, 82), (6, 3, 81), (9, 1, 79), (11, 1, 77)],
    [(0, 3, 76), (3, 1, 73), (5, 1, 76), (6, 1, 79), (8, 1, 76), (9, 2, 73)],
]
FLUTE_B = [
    [(0, 1, 79), (1, 1, 77), (2, 1, 79), (3, 2, 82), (5, 1, 84), (6, 1, 82), (8, 1, 81), (9, 2, 79)],
    [(0, 1, 86), (1, 1, 84), (2, 1, 82), (3, 2, 81), (5, 1, 77), (6, 2, 81), (9, 1, 77), (11, 1, 74)],
    [(0, 1, 79), (2, 1, 82), (3, 1, 79), (5, 1, 75), (6, 3, 74), (9, 1, 75), (11, 1, 74)],
    [(0, 1, 73), (1, 1, 76), (2, 1, 79), (3, 1, 82), (5, 1, 81)],
]

# ============================================================================ tracks
T = {k: Track(*v) for k, v in {
    "kick": (0, 0.02, 0), "clap": (0, 0.06, 0.25), "snap": (0.15, 0.05, 0.3), "shaker": (-0.4, 0.08, 0),
    "tamb": (0.45, 0.1, 0), "frame": (-0.2, 0.1, 0), "wood": (0.35, 0.12, 0.1), "tom": (0, 0.15, 0),
    "cym": (0, 0.2, 0), "fx": (0, 0.25, 0), "bass": (0, 0.0, 0), "chop": (0.3, 0.15, 0.05),
    "lute": (-0.25, 0.18, 0.05), "fiddle": (0.18, 0.22, 0.08), "fiddle2": (-0.35, 0.22, 0.08),
    "flute": (0.1, 0.26, 0.1), "shawm": (0, 0.2, 0.05), "dulc": (-0.3, 0.25, 0.1), "drone": (0, 0.25, 0),
    "pizz": (0.35, 0.15, 0.05),
}.items()}
CHORDS = {}          # bar -> chord name (for bass/chops)
MUTE_BASS = set()    # bars handled manually

def line(trk, bar, notes, fn, vel=1.0, tr=0, legato=0.9, pan=None, kw=None, accent_scoop=False, grace=0.0, double=None):
    kw = kw or {}
    for u, d, m in notes:
        t = tu(bar, u) + hum(0.0045)
        dur = max(0.06, (tu(bar, u + d) - tu(bar, u)) * legato)
        on = (u % 3 == 0)
        v = vel * (1.0 if on else 0.84) * rng.uniform(0.9, 1.05)
        extra = dict(kw)
        if accent_scoop and on and d >= 2 and fn is fiddle:
            extra["scoop"] = True
        trk.add(fn(m + tr, dur, v, **extra), t, pan=pan)
        if double is not None:
            dtrk, dpan, dvel = double
            dtrk.add(fn(m + tr, dur, v * dvel, **dict(extra, det=-7) if fn in (fiddle, shawm) else extra), t + 0.011 + hum(0.003), pan=dpan)
        if grace and d >= 2 and rng.random() < grace and fn in (flute, lute):
            T_ = trk
            T_.add(fn(m + tr + 2, 0.04, v * 0.55, **kw), t - 0.045, pan=pan)

def third_below(m, ch):
    tones = chord_tones(ch)
    scale = {2, 4, 5, 7, 9, 10, 1, 0}
    for d in (3, 4):
        if (m - d) % 12 in tones:
            return m - d
    for d in (3, 4):
        if (m - d) % 12 in scale:
            return m - d
    return m - 3

# ---------------------------------------------------------------------------- grooves
def drums(bar, style, skip=()):
    S = lambda u: tu(bar, u) + hum(0.0035)
    if style == "intro":
        for u in (3, 9):
            T["snap"].add(snap(0.9), S(u))
        for u in range(12):
            if u in skip:
                continue
            T["shaker"].add(shaker(0.85 if u % 3 == 2 else 0.4 if u % 3 == 0 else 0.25), S(u))
        for u in (0, 5, 8):
            T["frame"].add(frame(0.45, 90, True), S(u))
        return
    heavy = style in ("drama", "climax")
    for u in (0, 3, 6, 9):
        if u in skip:
            continue
        T["kick"].add(kick(1.0 if u == 0 else 0.93, tight=not heavy), S(u))
    for u in (3, 9):
        if u in skip:
            continue
        T["clap"].add(clap(0.95 * rng.uniform(0.92, 1.05)), S(u))
        T["snap"].add(snap(0.5), S(u) + 0.004)
    for u in range(12):
        if u in skip:
            continue
        v = 0.95 if u % 3 == 2 else 0.45 if u % 3 == 0 else 0.22
        T["shaker"].add(shaker(v * rng.uniform(0.85, 1.1)), S(u))
    for u in (2, 8):
        if u not in skip:
            T["tamb"].add(tamb(0.8, long=(u == 8 and bar % 2 == 1)), S(u))
    # bodhran ghost groove (funk ghost notes)
    for u, v in ((1, 0.25), (4, 0.3), (5, 0.55), (7, 0.25), (10, 0.35), (11, 0.6)):
        if u not in skip:
            T["frame"].add(frame(v, 115, False), S(u))
    if style == "funk":
        for u in ((5, 11) if bar % 2 == 0 else (4, 7, 11)):
            if u not in skip:
                T["wood"].add(woodblock(0.8, hi=u != 7), S(u))
    if heavy:
        for u in range(12):
            if u % 3 == 1 and u not in skip:
                T["tamb"].add(tamb(0.4), S(u))
        if bar % 2 == 1 and 11 not in skip:
            T["kick"].add(kick(0.55), S(10.5))
    if style == "climax":
        for u in (2, 8):
            if u not in skip:
                T["frame"].add(frame(0.7, 85, True), S(u))

def bass_groove(bar, ch, nxt, kind="funk", vel=1.0, sub=0.0):
    r = ROOTS[ch]; nr = ROOTS[nxt]
    S = lambda u: tu(bar, u) + hum(0.003)
    L = lambda u, d: (tu(bar, u + d) - tu(bar, u))
    if kind == "funk":
        third = 3 if QUAL[ch] == "m" else 4
        pat = [(0, 1.0, r, 1.0, False), (2, 0.5, r + 12, 0.55, True), (3, 0.8, r, 0.85, False),
               (5, 0.8, r + 12, 0.9, True), (6, 1.0, r + 7, 0.8, False), (8, 0.6, r + 10 if QUAL[ch] != "M" else r + 9, 0.75, False),
               (9, 0.9, r, 0.85, False), (10, 0.7, r + third, 0.7, False), (11, 0.7, nr - 1 if nr - 1 > r else nr + 1, 0.8, False)]
    elif kind == "answer":   # sparse under the flute call, riff in the gap
        pat = [(0, 1.0, r, 1.0, False), (3, 0.5, r, 0.5, False),
               (6, 0.8, r, 0.9, False), (7, 0.8, r + 3 if QUAL[ch] == "m" else r + 4, 0.75, False),
               (8, 0.8, r + 5, 0.8, False), (9, 0.8, r + 7, 0.9, False), (10, 0.8, r + 10, 0.8, False),
               (11, 0.8, r + 12, 0.95, True)]
    elif kind == "cell":     # bass locks to the hook rhythm
        pat = [(0, 1.0, r, 1.0, False), (2, 0.8, r, 0.7, False), (3, 1.0, r + 12, 0.9, True),
               (5, 2.5, r + 10 if QUAL[ch] != "M" else r + 11, 0.85, False), (8, 0.8, r + 7, 0.8, False),
               (9, 0.9, r, 0.9, False), (10, 0.7, r + 3 if QUAL[ch] == "m" else r + 4, 0.7, False),
               (11, 0.7, nr - 1 if nr - 1 > r else nr + 1, 0.8, False)]
    for u, d, m, v, pop in pat:
        slide = m - 2 if (u == 6 and kind == "funk" and bar % 4 == 1) else None
        T["bass"].add(bass(m, L(u, d) * 0.92, v * vel, pop=pop, slide_from=slide, sub=sub if u in (0, 9) else 0), S(u))

def chops(bar, ch, inst="lute", vel=1.0, units=(2, 5, 8, 11), tr=0):
    for u in units:
        ms = [m + tr for m in CHOP[ch]]
        T["chop" if inst == "lute" else "pizz"].add(strum(ms, U * 0.9, vel * (1 if u % 6 == 2 else 0.85), down=(u % 6 == 2), inst=inst), tu(bar, u) + hum(0.005))

def drone(b0, b1, midis, buzz=True):
    units = [(b, u, 1.0 if u % 3 == 2 else 0.5) for b in range(b0, b1) for u in (2, 5, 8, 11)] if buzz else None
    T["drone"].add(gurdy_drone(tu(b1, 0) - tu(b0, 0) + 0.1, midis, units, b0), tu(b0, 0))

def stab(trk, bar, u, ch, vel=1.0, dur_u=0.8, tr=0, top=True):
    ms = [m + tr + 12 for m in CHOP[ch]]
    d = (tu(bar, u + dur_u) - tu(bar, u))
    for i, m in enumerate(ms):
        trk.add(shawm(m, d, vel * 0.8, det=(i - 1) * 6), tu(bar, u) + hum(0.004), pan=(i - 1) * 0.3)

# ============================================================================ ARRANGEMENT
SECTION_LOG = []
def mark(t, txt):
    SECTION_LOG.append((t, txt))

prog = {}
for b, c in enumerate(["Dm", "Dm", "Gm", "A7"] * 2 + ["Dm", "Dm", "Bb", "A7"]):
    prog[b] = c
for b, c in zip(range(12, 22), ["Gm", "Dm", "Bb", "A7", "Gm", "A7", "Gm", "Dm", "Eb", "A7"]):
    prog[b] = c
for b, c in zip(range(22, 28), ["Dm", "Bb", "Gm", "A7", "Dm", "A7"]):
    prog[b] = c
for b, c in zip(range(28, 34), ["Em", "Em", "Am", "B7", "Em", "Em"]):
    prog[b] = c
nxt = lambda b: prog.get(b + 1, prog[b])

# ---------------- SECTION 1: "The Tavern"  (bars 0-11) ----------------
mark(0, "Hook on solo lute, swung snaps & shaker, bass enters")
for b in range(4):
    line(T["lute"], b, HOOK[b] if b < 3 else HOOK[3][:7], lute, vel=0.95, grace=0.3)
    drums(b, "intro", skip=(9, 10, 11) if b == 3 else ())
    if b >= 1:
        for u in ((0, 6) if b < 3 else (0,)):
            T["kick"].add(filt(kick(0.75), "low", 600), tu(b, u))
    # bass: round root notes + a cheeky fill answering each lute phrase
    r = ROOTS[prog[b]]
    T["bass"].add(bass(r, BEAT * 1.6, 0.8), tu(b, 0))
    if b < 3:
        for u, iv in ((9, 7), (10, 10), (11, 11)):
            T["bass"].add(bass(r + iv if b != 2 else r + iv - 12, U * 0.8, 0.7, pop=(u == 11)), tu(b, u) + hum(0.003))
T["fx"].add(rev_cym(BEAT * 1.2, 0.9), tu(4, 0) - BEAT * 1.2)
T["bass"].add(bass(45, BEAT * 0.9, 0.9, slide_from=40), tu(3, 3))
T["bass"].add(bass(33, BEAT * 0.4, 1.0, sub=0.5), tu(3, 6))
# --> GASP on beat 4 of bar 3 (lands in the silence before the drop)

mark(tu(4, 0), "DROP: fiddle takes the hook (double-tracked), lute chops, funk bass, full beat")
T["cym"].add(crash(2.0, 0.9), tu(4, 0))
for b in range(4, 8):
    line(T["fiddle"], b, HOOK[b - 4], fiddle, vel=1.0, legato=0.85, kw={"art": "spic"},
         double=(T["fiddle2"], -0.35, 0.7))
    line(T["lute"], b, HOOK[b - 4], lute, vel=0.22, tr=-12, pan=-0.45)
    drums(b, "groove")
    bass_groove(b, prog[b], nxt(b), "funk")
    chops(b, prog[b])
# call-and-response: shawm section answers the fiddle in the hook's gaps
for b in (4, 5, 6):
    stab(T["shawm"], b, 10, prog[b], 0.8, 0.6)
    stab(T["shawm"], b, 11, prog[b], 0.9, 0.6)

mark(tu(8, 0), "Answer phrase: wooden flute joins fiddle an octave up, pizzicato chops")
for b in (8, 9):
    line(T["fiddle"], b, HOOK[b - 8], fiddle, vel=0.95, legato=0.85, kw={"art": "spic"}, double=(T["fiddle2"], -0.35, 0.6))
    line(T["flute"], b, HOOK[b - 8], flute, vel=0.8, tr=12, grace=0.25)
    drums(b, "groove")
    bass_groove(b, prog[b], nxt(b), "funk")
    chops(b, prog[b], "pizz", 0.9)

mark(tu(10, 0), "STOP-TIME: band punches the hook cell, chuckle answers on the swung 8ths")
# bar 10: tutti hits on u0,u2,u3,u5 then the chuckle fills beats 3-4
for u, d, m in ANSWER3[:4]:
    t = tu(10, u)
    dd = min((tu(10, u + d) - t) * 0.8, U * 0.75)
    T["fiddle"].add(fiddle(m, dd, 1.0, "spic"), t); T["fiddle2"].add(fiddle(m, dd, 0.7, "spic", det=-7), t + 0.01)
    T["flute"].add(flute(m + 12, dd, 0.8), t)
    T["chop"].add(strum(CHOP["Bb"], dd, 0.9), t)
    T["bass"].add(bass(ROOTS["Bb"] + (12 if u in (3,) else 0), dd, 1.0, pop=(u == 3)), t)
    T["kick"].add(kick(0.9 if u in (0, 3) else 0.6), t)
    if u in (3,):
        T["clap"].add(clap(1.0), t)
stab(T["shawm"], 10, 5, "Bb", 0.9, 0.5)
for u in (6, 7, 8, 9, 10, 11):
    T["shaker"].add(shaker(0.8 if u % 3 == 2 else 0.45), tu(10, u))
def under_laugh(bar):
    """keep the pulse alive under the chuckle: muted bass ghosts, snaps, bodhran"""
    # hits sit BETWEEN the laugh syllables (u6, u8, u9) -> micro call & response
    for u, m in ((7, 46), (10, 45), (11, 46)):
        T["bass"].add(bass(m, U * 0.35, 0.5), tu(bar, u) + 0.005)
        T["frame"].add(frame(0.4, 110, False), tu(bar, u))
    T["snap"].add(snap(0.8), tu(bar, 10))
under_laugh(10)
# clap roll pickup into bar 11
for i, u in enumerate((10, 10.5, 11, 11.5)):
    T["clap"].add(clap(0.35 + 0.15 * i), tu(10, u))

mark(tu(11, 0), "Answer resolves to D; band breaks on beat 4 for the surprised 'Oh!'")
line(T["fiddle"], 11, ANSWER4, fiddle, vel=1.0, legato=0.85, kw={"art": "spic"}, double=(T["fiddle2"], -0.35, 0.6))
line(T["flute"], 11, ANSWER4, flute, vel=0.8, tr=12)
drums(11, "groove", skip=(9, 10, 11))
for u, d, m, v in ((0, 1, 45, 1.0), (2, 0.5, 57, 0.6), (3, 1, 45, 0.9), (5, 0.8, 57, 0.8), (6, 2, 38, 1.0)):
    T["bass"].add(bass(m, (tu(11, u + d) - tu(11, u)) * 0.9, v, pop=m > 50), tu(11, u))
chops(11, "A7", units=(2, 5)); chops(11, "Dm", units=(8,))
T["fx"].add(rev_cym(BEAT * 1.1, 1.0), tu(12, 0) - BEAT * 1.1)
T["fiddle"].add(fiddle(79, U * 1.2, 0.35, "legato", slide_from=67, stime=U * 1.0), tu(11, 10.5))

# ---------------- SECTION 2: "The Apothecary"  (bars 12-21) ----------------
mark(tu(12, 0), "SECTION 2: flute calls, funk bass answers (call & response), woodblock + pizzicato")
T["cym"].add(crash(2.2, 0.8), tu(12, 0))
for b in range(12, 16):
    line(T["flute"], b, FLUTE_A[b - 12], flute, vel=1.0, grace=0.35)
    drums(b, "funk")
    bass_groove(b, prog[b], nxt(b), "answer" if b != 14 else "funk", sub=0.2)
    chops(b, prog[b], "pizz", 0.85, units=(2, 8))
    chops(b, prog[b], "lute", 0.55, units=(5, 11))
# fiddle comment in bar 15 gap
for i, (u, m) in enumerate(((9, 76), (10, 79), (11, 82))):
    T["fiddle"].add(fiddle(m, U * 0.8, 0.75, "spic"), tu(15, u))

mark(tu(16, 0), "BREAK: drums drop out, hammered dulcimer triplets + bass solo, filter-swept build")
for b in (16, 17):
    ch = prog[b]
    tones = sorted(CHOP[ch] + [m + 12 for m in CHOP[ch]])
    seq = tones + tones[-2:0:-1]
    for u in range(12):
        T["dulc"].add(dulcimer(seq[u % len(seq)] + 12, 0.8 if u % 3 == 0 else 0.55), tu(b, u) + hum(0.004))
    for u in range(12):
        T["shaker"].add(shaker(0.7 if u % 3 == 2 else 0.3), tu(b, u))
    for u in (3, 9):
        T["snap"].add(snap(1.0), tu(b, u))
    r = ROOTS[ch]
    riff = [(0, 1.5, r, 1.0, False), (2, 0.8, r + 12, 0.7, True), (3, 0.8, r + 10, 0.8, False), (5, 0.8, r + 12, 0.85, True),
            (6, 1.5, r + 7, 0.8, False), (8, 0.8, r + 3 if QUAL[ch] == "m" else r + 4, 0.7, False), (9, 0.8, r + 5, 0.75, False)]
    if b == 17:
        riff = riff[:6]
    for u, d, m, v, pop in riff:
        T["bass"].add(bass(m, (tu(b, u + d) - tu(b, u)) * 0.9, v, pop=pop), tu(b, u) + hum(0.003))
for u in range(0, 9):     # kick returns, filtered, under bar 17
    T["kick"].add(filt(kick(0.5 + 0.05 * u), "low", 300 + 250 * u), tu(17, u * 1.0) if u % 3 == 0 else tu(17, u))
T["flute"].add(flute(81, BEAT * 1.8, 0.6), tu(16, 6))
T["fx"].add(sweep(BAR * 2 - BEAT, 1.0), tu(16, 0))
T["fx"].add(rev_cym(BEAT * 1.0, 1.0), tu(18, 0) - BEAT)
# --> GASP on beat 4 of bar 17

mark(tu(18, 0), "Re-entry: flute melody B with fiddle counter-line, shawm punches")
T["cym"].add(crash(2.0, 0.9), tu(18, 0))
FID_COUNTER = {18: [(0, 6, 70), (6, 6, 74)], 19: [(0, 6, 69), (6, 6, 65)], 20: [(0, 6, 67), (6, 6, 70)], 21: [(0, 5, 73)]}
for b in range(18, 22):
    notes = FLUTE_B[b - 18]
    line(T["flute"], b, notes, flute, vel=1.0, grace=0.3)
    line(T["fiddle"], b, FID_COUNTER[b], fiddle, vel=0.28, legato=0.97, kw={"art": "legato"})
    if b < 21:
        drums(b, "funk")
        bass_groove(b, prog[b], nxt(b), "funk", sub=0.2)
        chops(b, prog[b], "lute", 0.85)
        stab(T["shawm"], b, 5, prog[b], 0.7, 0.5)
        stab(T["shawm"], b, 11, prog[b], 0.75, 0.5)
mark(tu(21, 0), "Stop on A7 -- chuckle in the gap, shawm stab, drum pickup into Section 3")
drums(21, "funk", skip=tuple(range(6, 12)))
under_laugh(21)
for u in (6, 7, 8, 9):
    T["shaker"].add(shaker(0.8 if u % 3 == 2 else 0.45), tu(21, u))
for u, d, m, v in ((0, 1, 45, 1.0), (2, 0.5, 57, 0.6), (3, 1, 45, 0.9), (5, 0.8, 57, 0.8)):
    T["bass"].add(bass(m, (tu(21, u + d) - tu(21, u)) * 0.9, v, pop=m > 50), tu(21, u))
chops(21, "A7", units=(2, 5))
stab(T["shawm"], 21, 11, "A7", 1.0, 0.7)
T["bass"].add(bass(45, U * 0.8, 1.0, pop=True), tu(21, 11))
for i, (u, p) in enumerate(((10, 150), (10.5, 125), (11, 105), (11.5, 88))):
    T["tom"].add(tom(p, 0.55 + 0.1 * i), tu(21, u))
T["fx"].add(rev_cym(BEAT * 0.9, 1.1), tu(22, 0) - BEAT * 0.9)

# ---------------- SECTION 3: "The Cure"  (bars 22-33) ----------------
mark(tu(22, 0), "SECTION 3: dark hook on shawms + hurdy-gurdy drone, bass locks to the hook rhythm, soaring fiddle")
T["cym"].add(crash(2.4, 1.0), tu(22, 0))
drone(22, 26, (50, 57))
S3_HOOK = [HOOK[0], [(u, d, p - 4) for u, d, p in HOOK[1]], HOOK[2], HOOK[3][:8]]
S3_HOOK[1] = cell([74, 74, 77, 76, 74, 74])   # over Bb: D D F E~ D D
S3_HOOK[1] = [(u, d, p if p != 76 else 77) for u, d, p in S3_HOOK[1]]
FID_SOAR = {22: [(0, 6, 81), (6, 6, 77)], 23: [(0, 6, 86), (6, 6, 82)], 24: [(0, 6, 82), (6, 6, 79)], 25: [(0, 8, 85), (8, 4, 88)]}
for b in range(22, 26):
    ch = prog[b]
    notes = S3_HOOK[b - 22]
    line(T["shawm"], b, notes, shawm, vel=1.7, tr=-12, legato=0.8)
    line(T["shawm"], b, [(u, d, third_below(p, ch)) for u, d, p in notes], shawm, vel=1.1, tr=-12, legato=0.8, pan=-0.3)
    line(T["lute"], b, notes, lute, vel=0.3, pan=-0.35)
    line(T["fiddle"], b, FID_SOAR[b], fiddle, vel=0.42, legato=0.98, kw={"art": "legato"},
         double=(T["fiddle2"], -0.4, 0.55))
    drums(b, "drama")
    bass_groove(b, ch, nxt(b), "cell", sub=0.35)
    chops(b, ch, "pizz", 0.7, units=(2, 8))

mark(tu(26, 0), "BREAK: tutti stop-time on the hook cell, toms answer")
for u, d, m in HOOK[0]:
    t = tu(26, u); dd = (tu(26, u + d) - t) * 0.75
    T["fiddle"].add(fiddle(m, dd, 1.0, "spic"), t); T["fiddle2"].add(fiddle(m, dd, 0.7, "spic", det=-7), t + 0.01)
    T["shawm"].add(shawm(m - 12, dd, 0.9), t)
    T["chop"].add(strum(CHOP["Dm"], dd, 0.9), t)
    T["bass"].add(bass(38 if u % 3 == 0 else 50, dd, 1.0, pop=u % 3 != 0, sub=0.3 if u == 0 else 0), t)
    T["kick"].add(kick(0.9 if u % 3 == 0 else 0.55), t)
T["cym"].add(crash(1.2, 0.6), tu(26, 0))
for u, p in ((10, 140), (11, 110)):
    T["tom"].add(tom(p, 0.8), tu(26, u))
T["clap"].add(clap(1.0), tu(26, 3)); T["clap"].add(clap(1.0), tu(26, 9))

mark(tu(27, 0), "BUILD: snare/clap roll, chromatic bass climb, fiddle tremolo, riser")
for i in range(24):
    u = i * 0.5
    if u >= 9:
        break
    T["clap"].add(clap(0.25 + 0.6 * (i / 18) ** 1.3), tu(27, u) + hum(0.002))
for u in (0, 3, 6):
    T["kick"].add(kick(0.95), tu(27, u))
for i, m in enumerate((33, 34, 35, 36, 37, 38, 39, 40, 41)):
    T["bass"].add(bass(m + 12, U * 0.85, 0.75 + 0.03 * i, pop=i % 2 == 1), tu(27, i))
for i in range(18):
    u = i * 0.5
    T["fiddle"].add(fiddle(81 + (i // 6) * 2, U * 0.45, 0.45 + 0.03 * i, "spic"), tu(27, u))
T["fx"].add(sweep(BEAT * 3, 1.2), tu(27, 0))
drone(27, 28, (45, 57), buzz=False)
T["fx"].add(rev_cym(BEAT * 1.0, 1.2), tu(28, 0) - BEAT)
# --> SURPRISED 'Oh!' on beat 4 of bar 27, then key change

mark(tu(28, 0), "CLIMAX (+2, E minor): everyone on the hook, flute 8va, shawm punches, hurdy-gurdy drone")
T["cym"].add(crash(2.4, 1.15), tu(28, 0))
drone(28, 32, (52, 59))
for b in range(28, 32):
    ch = prog[b]
    notes = HOOK[b - 28]
    line(T["fiddle"], b, notes, fiddle, vel=1.0, tr=2, legato=0.85, kw={"art": "spic"}, double=(T["fiddle2"], -0.4, 0.75))
    line(T["flute"], b, notes, flute, vel=0.75, tr=14)
    line(T["lute"], b, notes, lute, vel=0.3, tr=-10, pan=-0.4)
    drums(b, "climax")
    bass_groove(b, ch, nxt(b) if b < 31 else "Em", "funk", sub=0.35)
    chops(b, ch)
    if b < 31:
        stab(T["shawm"], b, 10, ch, 0.9, 0.6)
        stab(T["shawm"], b, 11, ch, 1.0, 0.6)
T["cym"].add(crash(1.5, 0.8), tu(30, 0))

mark(tu(32, 0), "FINAL HIT on E minor -> sigh of relief -> lute button")
t_end = tu(32, 0)
for m in (64, 76, 88):
    T["fiddle"].add(fiddle(m, BEAT * 1.6, 0.5, "legato"), t_end)
T["flute"].add(flute(88, BEAT * 1.4, 0.8), t_end)
stab(T["shawm"], 32, 0, "Em", 1.2, 4.0)
T["chop"].add(strum([52, 59, 64, 67, 71, 76], BEAT * 2.5, 1.0), t_end)
T["bass"].add(bass(28, BEAT * 2.5, 1.2, sub=0.6), t_end)
T["kick"].add(kick(1.1, tight=False), t_end)
T["clap"].add(clap(1.0), t_end)
T["cym"].add(crash(2.6, 1.2), t_end)
T["tom"].add(tom(70, 0.9), t_end)
drone(32, 34, (52, 59), buzz=False)
# button (after the sigh): cheeky pluck on the last downbeat
t_btn = tu(33, 0)
T["lute"].add(lute(64, BEAT * 0.4, 0.9), t_btn)
T["lute"].add(lute(71, BEAT * 0.4, 0.7), t_btn + 0.012)
T["pizz"].add(pizz(76, 0.9), t_btn)
T["bass"].add(bass(40, BEAT * 0.4, 0.9), t_btn)
T["kick"].add(kick(0.6), t_btn)
T["snap"].add(snap(0.9), t_btn)

# ============================================================================ HUMAN REACTIONS
def load_vox(name):
    sr, x = wavfile.read(os.path.join(HERE, "vox", name + ".wav"))
    x = x.astype(float)
    x = x / (32768.0 if x.dtype != float or np.abs(x).max() > 1.5 else 1.0)
    x = x.mean(axis=1) if x.ndim > 1 else x
    if sr != SR:
        x = signal.resample_poly(x, SR, sr)
    return x

def vox_chain(x):
    x = filt(x, "high", 95, order=2)
    x = peq(x, 320, -2.5, 1.0)
    x = peq(x, 3200, 2.5, 1.0)
    x = shelf(x, 9000, 1.5)
    # gentle compression (3:1, fast)
    e = np.sqrt(filt(x ** 2, "low", 40).clip(1e-12))
    db = 20 * np.log10(e); thr = db.max() - 12
    g = 10 ** (-np.maximum(0, db - thr) * (1 - 1 / 3) / 20)
    x = x * g
    return x / np.abs(x).max()

def envelope(x, fc):
    sos = signal.butter(2, fc / (SR / 2), "low", output="sos")
    return np.sqrt(signal.sosfiltfilt(sos, x ** 2).clip(1e-12))

def onset(x, rel_db=-20):
    e = envelope(x, 60)
    return int(np.argmax(20 * np.log10(e) > 20 * np.log10(e.max()) + rel_db))

def syllables(x):
    """split the chuckle at the quiet valleys between laughs"""
    fr = int(0.005 * SR)
    e = np.array([np.sqrt((x[i:i + fr] ** 2).mean()) for i in range(0, len(x) - fr, fr)])
    db = 20 * np.log10(e + 1e-9); thr = db.max() - 22
    act = db > thr
    segs = []; i = 0
    while i < len(act):
        if act[i]:
            j = i
            while j < len(act) and act[j]:
                j += 1
            if j - i >= 6:
                segs.append((i, j))
            i = j
        else:
            i += 1
    out = []
    for k, (a, b) in enumerate(segs):
        s = max(0, a * fr - int(0.012 * SR))
        end = segs[k + 1][0] * fr - int(0.01 * SR) if k + 1 < len(segs) else min(len(x), b * fr + int(0.1 * SR))
        seg = x[s:end].copy()
        fo = min(len(seg) // 3, int(0.03 * SR))
        seg[-fo:] *= np.linspace(1, 0, fo)
        out.append(seg)
    return out

VOX = {k: vox_chain(load_vox(k)) for k in ("gasp", "surprised", "chuckle", "sigh")}
VOXT = Track(0, 0.0, 0.22)
VOX_LOG = []
SRC = {"gasp": "Short_natural_male_g_4 (gasp)", "surprised": "Short_natural_male_s_4 (surprised 'oh!')",
       "chuckle": "Short_mischievous_ma_1 (chuckle)", "sigh": "Short_natural_male_s_1 (sigh of relief)"}

EVENTS = []
def place(name, x, t_beat, rel_db, pan=0.0, anchor="onset", note=""):
    """put the sample so its perceptual onset (or voiced peak) lands on t_beat;
    level is set later relative to the measured loudness of the music bus"""
    a = onset(x) if anchor == "onset" else int(np.argmax(envelope(x, 12)))
    t0 = t_beat - a / SR
    EVENTS.append((name, x, t0, rel_db, pan))
    VOX_LOG.append((t_beat, t0, t0 + len(x) / SR, name, note))

def active_rms(x, rel=-25):
    e = envelope(x, 30); m = 20 * np.log10(e) > 20 * np.log10(e.max()) + rel
    return np.sqrt((x[m] ** 2).mean())

def render_vox(ref_rms):
    VOXT.buf[:] = 0
    for name, x, t0, rel_db, pan in EVENTS:
        g = ref_rms * 10 ** (rel_db / 20) / active_rms(x)
        VOXT.add(x * g, t0, pan=pan)

# 1. gasp on beat 4 of bar 3 -> into the drop
place("gasp", VOX["gasp"], tu(3, 9) - 0.01, -3.0, 0.0, note="beat 4 of bar 4, pickup into the drop")
# 2. chuckle chopped onto swung 8ths in the bar-10 stop-time
syl = syllables(VOX["chuckle"])
for k, u in enumerate((6, 8, 9)):
    s = syl[k + 1] if k + 1 < len(syl) else syl[-1]
    place("chuckle", s, tu(10, u) - 0.005, -1.0 if k == 0 else -3.0, pan=(-0.15, 0.15, 0.0)[k], note=f"syllable {k + 1}/3 of stop-time answer (bar 11, unit {u})")
# 3. surprised on beat 4 of bar 11 -> into section 2
place("surprised", VOX["surprised"], tu(11, 9) - 0.008, -1.0, note="beat 4 of bar 12, pickup into Section 2")
# 4. gasp at the end of the dulcimer break
place("gasp", VOX["gasp"], tu(17, 9) - 0.01, -1.5, pan=0.1, note="beat 4 of bar 18, end of the break")
# 5. chuckle in the bar-21 stop (answering the flute), 3 syllables
for k, u in enumerate((6, 8, 9)):
    s = syl[(k + 4) % len(syl)]
    place("chuckle", s, tu(21, u) - 0.005, -1.0 if k == 0 else -3.0, pan=(0.15, -0.15, 0.0)[k], note=f"syllable {k + 1}/3, stop before Section 3 (bar 22)")
# 6. surprised 'oh!' at the top of the build, right before the key change
place("surprised", VOX["surprised"], tu(27, 9) - 0.008, -1.0, note="beat 4 of bar 28, before the key change")
# 7. sigh of relief after the final hit (voiced peak on beat 3)
place("sigh", VOX["sigh"], tu(32, 6), -1.5, anchor="peak", note="after the final hit; voiced peak on beat 3 of bar 33")

# ============================================================================ MIX
LEVELS = {"kick": 1.15, "clap": 3.8, "snap": 6.0, "shaker": 4.5, "tamb": 3.0, "frame": 2.5, "wood": 4.0, "tom": 1.8,
          "cym": 2.2, "fx": 1.3, "bass": 1.25, "chop": 0.33, "lute": 1.0, "fiddle": 5.5, "fiddle2": 3.4,
          "flute": 2.7, "shawm": 8.0, "dulc": 3.4, "drone": 2.5, "pizz": 0.95}

def mixdown(include_vox, duck=True):
    kickenv = filt(np.abs(T["kick"].buf[:, 0]), "low", 30)
    kickenv /= kickenv.max() + 1e-9
    sc = 1 - 0.55 * np.clip(kickenv * 2.4, 0, 1)
    duck_amt = {"bass": 0.9, "chop": 0.6, "pizz": 0.5, "drone": 0.6, "shawm": 0.25, "dulc": 0.3, "lute": 0.2, "tamb": 0.25}
    lv = LEVELS
    bus = np.zeros((N + PAD, 2)); room = np.zeros_like(bus); plate = np.zeros_like(bus)
    for k, tr in T.items():
        x = tr.buf * lv[k]
        if k in duck_amt:
            x = x * (1 - duck_amt[k] + duck_amt[k] * sc)[:, None]
        if k == "bass":
            x = filt(x, "high", 32)
        elif k not in ("kick", "tom"):
            x = filt(x, "high", 50 if k in ("drone", "frame") else 100)
        bus += x; room += x * tr.rev; plate += x * tr.plate
    if include_vox:
        v = VOXT.buf.copy()
        if duck:   # music leans back ~2.5 dB under each reaction
            ve = filt(np.abs(v[:, 0]), "low", 8); ve /= ve.max() + 1e-9
            bus *= (1 - 0.25 * np.clip(ve * 3, 0, 1))[:, None]
        bus += v; plate += v * VOXT.plate
    wet = np.stack([signal.fftconvolve(room[:, c], IR_ROOM[:, c])[: len(room)] for c in range(2)], 1)
    wet2 = np.stack([signal.fftconvolve(plate[:, c], IR_PLATE[:, c])[: len(plate)] for c in range(2)], 1)
    return bus + wet * 1.0 + wet2 * 0.9

def make_ir(sec, er=True, damp=6500):
    n = int(sec * SR); t = np.arange(n) / SR; ir = np.zeros((n, 2))
    for c in range(2):
        nz = filt(rng.normal(0, 1, n), "low", damp)
        ir[:, c] = nz * np.exp(-t / (sec / 6.9 * 2)) * np.minimum(1, t / 0.01)
        if er:
            for d, g in ((0.009, 0.5), (0.017, 0.35), (0.026, 0.3), (0.037, 0.22)):
                ir[int((d + 0.0023 * c) * SR), c] += g * 8
    ir = filt(ir, "high", 250)
    return ir / np.sqrt((ir ** 2).sum())

IR_ROOM = make_ir(1.3)
IR_PLATE = make_ir(0.75, er=False, damp=9000)
pd = int(0.015 * SR); IR_PLATE = np.vstack([np.zeros((pd, 2)), IR_PLATE])

def master_pre(x):
    x = x[:N].copy()
    x = filt(x, "high", 36)
    x = peq(x, 280, -1.5, 0.9)
    x = peq(x, 95, 2.5, 0.8)
    x = peq(x, 3000, -1.0, 1.2)
    x = shelf(x, 9000, 1.0)
    return x

def glue(x, thr_db=-15, ratio=2.0, att=0.012, rel=0.16):
    lvl = np.sqrt(filt((x ** 2).mean(axis=1), "low", 12).clip(1e-12))
    g = 10 ** (-np.maximum(0, 20 * np.log10(lvl) - thr_db) * (1 - 1 / ratio) / 20)
    out = np.empty_like(g); prev = 1.0
    aa, ar = np.exp(-64 / (att * SR)), np.exp(-64 / (rel * SR))
    for i in range(0, len(g), 64):
        tgt = g[i:i + 64].min(); c = aa if tgt < prev else ar
        prev = c * prev + (1 - c) * tgt; out[i:i + 64] = prev
    return x * out[:, None]

def limiter(x, ceil=0.85, rel=0.06):
    up = signal.resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(axis=1)[: len(x) * 4].reshape(-1, 4).max(axis=1)
    pk = maximum_filter1d(pk, size=2 * int(0.003 * SR) + 1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    out = np.empty_like(g); prev = 1.0; ar = np.exp(-1 / (rel * SR))
    for i in range(len(g)):
        v = g[i]; prev = v if v < prev else ar * prev + (1 - ar) * v; out[i] = prev
    out = filt(out, "low", 400)
    return x * np.minimum(out, g)[:, None]

def master(x, pre_gain, drive_gain):
    x = master_pre(x) * pre_gain
    x = glue(x)
    x = np.tanh(x * 1.5) / np.tanh(1.5)
    x = limiter(x * drive_gain)
    fi, fo = int(0.003 * SR), int(0.35 * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    x[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
    return x

def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x)

def write(name, x):
    p = os.path.join(OUT, name)
    wavfile.write(p, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    return p

if __name__ == "__main__":
    inst = mixdown(False)
    ref = np.sqrt((inst[:N] ** 2).mean())          # loudness reference of the music bus
    render_vox(ref)
    full = mixdown(True)
    pre = 0.55 / np.abs(master_pre(full)).max()
    # calibrate the loudness drive on the full mix, reuse identical settings for the instrumental
    probe = master(full, pre, 1.0)
    drive = 10 ** ((-10.0 - lufs(probe)) / 20)
    final = master(full, pre, drive)
    instr = master(inst, pre, drive)
    # vocal stem: the processed reactions incl. their plate, at the same gain staging as in the final
    vstem = VOXT.buf.copy(); vwet = np.stack([signal.fftconvolve(vstem[:, c] * VOXT.plate, IR_PLATE[:, c])[: len(vstem)] for c in range(2)], 1)
    vstem = master_pre(vstem + vwet * 0.9) * pre * drive
    vstem = vstem * min(1.0, 0.89 / np.abs(vstem).max())
    assert len(final) == N == len(instr) == len(vstem)
    write("MEDIEVAL_MEDICINE_FINAL.wav", final)
    write("MEDIEVAL_MEDICINE_INSTRUMENTAL.wav", instr)
    write("MEDIEVAL_MEDICINE_VOX_STEM.wav", vstem)
    with open(os.path.join(OUT, "MEDIEVAL_MEDICINE_VOX_TIMESTAMPS.md"), "w") as f:
        f.write("# Human reaction placements -- MEDIEVAL_MEDICINE_FINAL.wav\n\n")
        f.write("134 BPM, 12 swung units per bar. 'On beat' = where the sound's attack (or voiced peak) is locked to the grid.\n\n")
        f.write("| # | On beat (s) | Audible from-to (s) | Bar / beat | Source file | Role |\n|---|---|---|---|---|---|\n")
        for i, (tb, a, b, name, note) in enumerate(sorted(VOX_LOG)):
            bar = int(tb // BAR); beat = (tb - bar * BAR) / BEAT + 1
            f.write(f"| {i + 1} | {tb:6.3f} | {max(0, a):6.3f} - {min(60, b):6.3f} | {bar + 1} / {beat:.2f} | {SRC[name]} | {note} |\n")
        f.write("\n## Arrangement map\n\n")
        for t, txt in SECTION_LOG:
            f.write(f"- **{t:5.2f} s** (bar {int(round(t / BAR)) + 1}) -- {txt}\n")
    print("final LUFS", round(lufs(final), 2), "instrumental LUFS", round(lufs(instr), 2), "vox events", len(VOX_LOG))
