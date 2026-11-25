"""
MEDIEVAL MEDICINE  V3 -- 60 s medieval club-dance soundtrack
for "Three Insane Medieval Medical Treatments".

132 BPM -> exactly 33 bars in 60.000 s, so the file loops seamlessly
(the reverb/decay that spills past 60 s is wrapped onto the start).
D dorian/aeolian, progression Dm | C | Bb | C-Dm  (i - bVII - bVI - bVII - i).

THE HOOK (4 bars): a tresillo "DUM . . DUM . . DAA" on the same note, then a falling
run -- three times (leap to A, G, then Bb), then a modal cadence F E D C | D.

All instruments are synthesised here (physical/additive models). The human reactions
are the supplied ElevenLabs recordings in music/vox/, chopped, EQ'd, compressed and
placed on the 16th grid like percussion.

    python3 medieval_medicine_v3.py [outdir]
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
BPM = 132.0
BEAT = 60.0 / BPM
S16 = BEAT / 4
BAR = 4 * BEAT
NBARS = 33
LENGTH = 60.0
N = int(round(LENGTH * SR))
PAD = 4 * SR
rng = np.random.default_rng(1518)          # the year of the Strasbourg dancing plague

# ============================================================================ DSP helpers
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

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


# ============================================================================ V3 grid
SWING = 0.54          # off-16th lands at 54% of the 8th: a light human push, still "club straight"

def ts(bar, step):
    """time in seconds of 16th step (0..15, may be fractional) in bar"""
    step = float(step)
    pair = np.floor(step / 2); r = step - 2 * pair
    frac = r * SWING if r <= 1 else SWING + (r - 1) * (1 - SWING)
    return bar * BAR + (pair + frac) * 2 * S16

def dur(bar, step, length):
    return ts(bar, step + length) - ts(bar, step)

# ============================================================================ V3 instruments
def club_kick(vel=1.0, long=False):
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 52 + 175 * np.exp(-t / 0.022) + 40 * np.exp(-t / 0.004)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.32 if long else 0.2))
    click = filt(rng.normal(0, 1, n), "bp", (2500, 9000)) * np.exp(-t / 0.0025) * 0.5
    knock = filt(rng.normal(0, 1, n), "bp", (180, 900)) * np.exp(-t / 0.018) * 0.35   # skin of a frame drum
    y = np.tanh((body * 1.25 + click + knock) * 1.7)
    return filt(y, "low", 9000) * vel * 0.6

def deep_bass(m, d, vel=1.0, pop=False, glide_from=None):
    """deep, bouncy plucked bass: clean sub fundamental + saturated growl that decays"""
    f = mtof(m)
    n = int((d + 0.06) * SR); t = np.arange(n) / SR
    fi = np.full(n, f)
    if glide_from is not None:
        k = np.clip(t / 0.07, 0, 1); k = k * k * (3 - 2 * k)
        fi = mtof(glide_from) * (f / mtof(glide_from)) ** k
    fi = fi * (1 + 0.035 * np.exp(-t / 0.01))                   # thumb thump
    ph = 2 * np.pi * np.cumsum(fi) / SR
    sub = np.sin(ph)
    growl = sum(np.sin(h * ph) / h ** (0.9 if pop else 1.2) for h in range(2, 12) if h * f < 7000)
    genv = np.exp(-t / (0.09 if pop else 0.06))
    growl = filt(growl, "low", 2400 if pop else 1300) * genv
    y = sub * 1.0 + np.tanh(growl * 2.2) * (0.55 if pop else 0.4)
    if pop:
        y[:250] += filt(rng.normal(0, 1, 250), "bp", (1500, 5000)) * np.exp(-np.arange(250) / 45) * 0.4
    e = np.minimum(1, t / 0.0025)
    k = int(d * SR)
    if k < n:
        e[k:] *= np.exp(-(t[k:] - t[k]) / 0.02)
    return y * e * vel * 0.36

def lute_v(m, d, vel=1.0, bright=0.78, trem=False):
    """lute with plectrum tremolo on long notes (medieval style, adds drive)"""
    x = lute(m, d, vel, bright)
    if trem and d > 2.5 * S16:
        k = int(1.5 * S16 * SR)
        r = lute(m, d - 1.5 * S16, vel * 0.55, bright * 0.9)
        x[k:k + len(r)] += r[: len(x) - k]
    return x

def flute_turn(top, t0, vel, step_s):
    """quick Irish-style cut / roll ornament leading into a note"""
    out = []
    for i, m in enumerate((top + 2, top, top - 2, top)):
        out.append((t0 + i * step_s, m, step_s * 0.9, vel * (0.7 if i < 3 else 1.0)))
    return out

def gurdy_drone(seconds, midis, buzz_times=()):
    n = int(seconds * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for m in midis:
        f = mtof(m) * (1 + 0.0015 * np.sin(2 * np.pi * 0.3 * t + rng.uniform(0, 6)))
        ph = 2 * np.pi * np.cumsum(f) / SR
        for h in range(1, 28):
            if h * mtof(m) > 9000:
                break
            out += (1 / h) * (0.6 if h % 2 == 0 else 1) * np.sin(h * ph)
    out = filt(peq(out, 800, 5, 1.5), "high", 120) * 0.02
    if len(buzz_times):
        ph = 2 * np.pi * mtof(midis[0] + 12) * t
        raw = filt(np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** 0.3 + 0.5 * rng.normal(0, 1, n), "bp", (400, 4500))
        g = np.zeros(n)
        for tt, v in buzz_times:
            a = int(tt * SR)
            if 0 <= a < n:
                seg = np.arange(min(n - a, int(0.2 * SR)))
                g[a:a + len(seg)] = np.maximum(g[a:a + len(seg)], v * np.exp(-seg / (0.07 * SR)) * np.minimum(1, seg / 60))
        out += raw * g * 0.045
    fd = np.clip(np.minimum(t / 0.06, (seconds - t) / 0.06), 0, 1)
    return out * fd

# ============================================================================ material
# (step, length, midi) on the 16th grid
H1 = [(0, 3, 74), (3, 3, 74), (6, 2, 81), (8, 2, 79), (10, 2, 77), (12, 2, 76), (14, 2, 77)]   # D D A~ G F E F
H2 = [(0, 3, 76), (3, 3, 76), (6, 2, 79), (8, 2, 77), (10, 2, 76), (12, 2, 74), (14, 2, 76)]   # E E G~ F E D E
H3 = [(0, 3, 74), (3, 3, 74), (6, 2, 82), (8, 2, 81), (10, 2, 79), (12, 2, 77), (14, 2, 79)]   # D D Bb~ A G F G
H4 = [(0, 2, 77), (2, 2, 76), (4, 2, 74), (6, 2, 72), (8, 4, 74)]                              # F E D C | D~
HOOK = [H1, H2, H3, H4]
# variation: same tresillo identity, the run now climbs and the register opens up
V1 = [(0, 3, 74), (3, 3, 74), (6, 2, 81), (8, 2, 77), (10, 2, 79), (12, 2, 81), (14, 2, 84)]   # D D A~ F G A C
V2 = [(0, 3, 76), (3, 3, 76), (6, 2, 84), (8, 2, 83), (10, 2, 79), (12, 2, 76), (14, 2, 79)]   # E E C~ B G E G (dorian B)
V3 = [(0, 3, 77), (3, 3, 77), (6, 2, 86), (8, 2, 84), (10, 2, 82), (12, 2, 81), (14, 2, 82)]   # F F D~ C Bb A Bb
V4 = [(0, 2, 84), (2, 2, 82), (4, 2, 81), (6, 2, 79), (8, 4, 81)]                              # C Bb A G | A~ (open)
VAR = [V1, V2, V3, V4]

ROOT = {"Dm": 38, "C": 36, "Bb": 34, "A": 33, "Gm": 43, "F": 41}
CHORD = {"Dm": [62, 65, 69], "C": [60, 64, 67], "Bb": [58, 62, 65], "A": [61, 64, 69], "Gm": [58, 62, 67], "F": [60, 65, 69]}

PROG4 = ["Dm", "C", "Bb", "C"]
def chord_at(bar, step=0):
    c = BAR_CHORD[bar]
    if c == "C>Dm":
        return "C" if step < 8 else "Dm"
    if c == "Bb>C":
        return "Bb" if step < 8 else "C"
    return c

BAR_CHORD = {}
for b in range(NBARS):
    BAR_CHORD[b] = PROG4[b % 4] if PROG4[b % 4] != "C" or b % 4 == 1 else "C>Dm"
BAR_CHORD.update({0: "Dm", 1: "C", 2: "Bb", 11: "Dm", 20: "Bb>C", 25: "Bb", 26: "C", 31: "Dm", 32: "C>Dm"})
# hook bars start at 3, 7, 12, 16, 21, 27 -> realign the 4-bar cycle to them
for start in (3, 7, 12, 16, 21, 27):
    for i, c in enumerate(["Dm", "C", "Bb", "C>Dm"]):
        BAR_CHORD[start + i] = c

# ============================================================================ tracks
T = {k: Track(*v) for k, v in {
    "kick": (0, 0.0, 0), "clap": (0, 0.05, 0.22), "snap": (0.2, 0.05, 0.2), "shaker": (-0.4, 0.06, 0),
    "tamb": (0.45, 0.08, 0), "frame": (-0.18, 0.1, 0), "wood": (0.35, 0.1, 0.05), "tom": (0, 0.14, 0),
    "cym": (0, 0.18, 0), "fx": (0, 0.2, 0), "bass": (0, 0.0, 0), "chop": (0.32, 0.12, 0.05),
    "lute": (-0.22, 0.14, 0.05), "fiddle": (0.2, 0.2, 0.08), "fiddle2": (-0.38, 0.2, 0.08),
    "flute": (0.12, 0.24, 0.1), "drone": (0, 0.22, 0),
}.items()}
ACCENTS = []          # (time, kind, description)  -> sync map for animation
def accent(t, kind, txt):
    ACCENTS.append((t, kind, txt))

def play(trk, bar, notes, fn, vel=1.0, tr=0, legato=0.9, pan=None, **kw):
    for s, l, m in notes:
        t = ts(bar, s) + (hum(0.004) if (bar, s) != (0, 0) else 0.0)
        d = max(0.05, dur(bar, s, l) * legato)
        strong = s in (0, 3, 6)          # tresillo hits get the weight
        v = vel * (1.0 if strong else 0.82 + 0.08 * (s % 4 == 0)) * rng.uniform(0.92, 1.04)
        trk.add(fn(m + tr, d, v, **kw), max(0.0, t), pan=pan)

def fiddle_line(bar, notes, vel=1.0, tr=0, double=True, art="spic"):
    for s, l, m in notes:
        t = ts(bar, s) + (hum(0.004) if (bar, s) != (0, 0) else 0.0)
        d = dur(bar, s, l) * (0.88 if art == "spic" else 0.97)
        v = vel * (1.0 if s in (0, 3, 6) else 0.85) * rng.uniform(0.92, 1.04)
        a = "legato" if (l >= 3 and art == "spic") else art          # dotted notes sing, runs bounce
        T["fiddle"].add(fiddle(m + tr, d, v, a, scoop=(s == 6 and l >= 2)), max(0.0, t))
        if double:
            T["fiddle2"].add(fiddle(m + tr, d, v * 0.75, a, det=-6), max(0.0, t + 0.012 + hum(0.003)))

def lute_line(bar, notes, vel=1.0, tr=0, pan=None):
    for s, l, m in notes:
        t = ts(bar, s) + (hum(0.004) if (bar, s) != (0, 0) else 0.0)
        v = vel * (1.0 if s in (0, 3, 6) else 0.8) * rng.uniform(0.92, 1.05)
        T["lute"].add(lute_v(m + tr, dur(bar, s, l) * 0.92, v, trem=(l >= 3)), max(0.0, t), pan=pan)

def flute_line(bar, notes, vel=1.0, tr=0, ornament=True):
    for i, (s, l, m) in enumerate(notes):
        t = ts(bar, s) + hum(0.004)
        if ornament and s in (0, 6) and l >= 2 and rng.random() < 0.6:
            T["flute"].add(flute(m + tr + 2, 0.035, vel * 0.5, chiff=0.6), t - 0.04)   # cut
        T["flute"].add(flute(m + tr, dur(bar, s, l) * 0.92, vel * (1.0 if s in (0, 3, 6) else 0.85)), t)

def flute_lick(bar, step, notes_up, vel=0.9):
    """fast 32nd/16th lick in a gap -- the playful accents"""
    for i, m in enumerate(notes_up):
        T["flute"].add(flute(m, S16 * 0.48, vel * (0.8 + 0.2 * (i == len(notes_up) - 1)), chiff=1.3, vib=False),
                       ts(bar, step) + i * S16 * 0.5 + hum(0.002))

# ---------------------------------------------------------------------------- rhythm section
def drums(bar, style, skip=(), keep_kick=False):
    S = lambda s: ts(bar, s) + hum(0.003)
    skipk = () if keep_kick else skip
    def k(s, v=1.0, long=False):
        if s not in skipk:
            T["kick"].add(club_kick(v, long), S(s))
    if style == "intro":
        for s in (0, 8):
            k(s, 0.85)
        for s in (4, 12):
            if s not in skip:
                T["clap"].add(clap(0.8), S(s)); T["snap"].add(snap(0.7), S(s))
        for s in range(16):
            if s not in skip:
                T["shaker"].add(shaker(0.9 if s % 4 == 2 else 0.35 + 0.1 * (s % 2 == 0)), S(s))
        for s in (3, 6, 11, 14):
            if s not in skip:
                T["frame"].add(frame(0.5, 92, True), S(s))
        return
    if style == "break":
        for s in (0, 8):
            k(s, 0.8)
        for s in (4, 12):
            T["snap"].add(snap(1.0), S(s))
        for s in range(16):
            T["shaker"].add(shaker(0.8 if s % 4 == 2 else 0.35), S(s))
        for s, v in ((3, 0.7), (6, 0.7), (7, 0.3), (10, 0.5), (11, 0.7), (14, 0.7), (15, 0.35)):
            T["frame"].add(frame(v, 95 if v > 0.6 else 120, v > 0.6), S(s))
        return
    for s in (0, 4, 8, 12):
        k(s, 1.0 if s in (0, 8) else 0.94)
    for s in (4, 12):
        if s not in skip:
            T["clap"].add(clap(rng.uniform(0.92, 1.03)), S(s))
            T["snap"].add(snap(0.5), S(s) + 0.003)
    for s in range(16):
        if s not in skip:
            T["shaker"].add(shaker((0.95 if s % 4 == 2 else 0.45 if s % 2 == 0 else 0.28) * rng.uniform(0.85, 1.1)), S(s))
    for s in (2, 6, 10, 14):
        if s not in skip:
            T["tamb"].add(tamb(0.85, long=(s == 14 and bar % 2 == 1)), S(s))
    # folk frame-drum bounce in tresillo against the four-on-the-floor
    for s, v in ((3, 0.55), (6, 0.45), (11, 0.55), (14, 0.45), (7, 0.2), (15, 0.25)):
        if s not in skip:
            T["frame"].add(frame(v, 92 if v > 0.4 else 118, v > 0.4), S(s))
    if style in ("var", "climax", "lock"):
        for s in ((3, 11) if bar % 2 == 0 else (3, 9, 11)):
            if s not in skip:
                T["wood"].add(woodblock(0.75, hi=(s != 9)), S(s))
    if style in ("climax", "lock"):
        for s in range(1, 16, 2):
            if s not in skip:
                T["tamb"].add(tamb(0.35), S(s))
        if bar % 2 == 1:
            k(15, 0.55)
    if style == "lock" and bar % 2 == 1:      # rhythmic variation: kick stutter
        k(10, 0.6); k(14, 0.7)

BASS_PATTERNS = {
    # (step, len, interval, vel, pop)
    "intro": [(0, 6, 0, 0.75, False), (6, 2, 12, 0.6, True), (8, 6, 0, 0.7, False), (14, 2, 12, 0.6, True)],
    "tres": [(0, 1, 0, 0.85, False), (3, 2, 0, 1.0, False), (6, 2, 12, 0.85, True), (8, 1, 0, 0.75, False),
             (10, 1, 12, 0.5, True), (11, 2, 7, 0.9, False), (14, 1, 10, 0.85, False), (15, 1, 12, 0.6, True)],
    "var": [(0, 1, 0, 0.9, False), (2, 1, 12, 0.6, True), (3, 2, 0, 1.0, False), (6, 1, 0, 0.8, False),
            (7, 1, 12, 0.65, True), (8, 1, 0, 0.8, False), (10, 1, 7, 0.8, False), (11, 2, 10, 0.9, False),
            (13, 1, 12, 0.7, True), (14, 2, 7, 0.85, False)],
    "lock": [(0, 3, 0, 1.0, False), (3, 3, 0, 1.0, False), (6, 2, 12, 0.95, True), (8, 2, 10, 0.85, False),
             (10, 2, 7, 0.85, False), (12, 2, 5, 0.8, False), (14, 2, 7, 0.85, False)],
    "drive": [(0, 1, 0, 1.0, False), (2, 1, 12, 0.7, True), (3, 1, 0, 0.85, False), (5, 1, 12, 0.75, True),
              (6, 2, 0, 0.95, False), (8, 1, 0, 1.0, False), (10, 1, 12, 0.7, True), (11, 1, 0, 0.85, False),
              (13, 1, 7, 0.8, False), (14, 1, 10, 0.85, False), (15, 1, 12, 0.7, True)],
}

def bassline(bar, kind, vel=1.0):
    for s, l, iv, v, pop in BASS_PATTERNS[kind]:
        r = ROOT[chord_at(bar, s)]
        m = r + iv
        if iv == 10 and chord_at(bar, s) in ("Bb", "C"):
            m = r + 9 if chord_at(bar, s) == "Bb" else r + 10
        glide = m - 5 if (kind in ("tres", "drive") and s == 3 and bar % 4 == 1) else None
        T["bass"].add(deep_bass(m, dur(bar, s, l) * 0.9, v * vel, pop=pop, glide_from=glide), ts(bar, s) + hum(0.002))

def chops(bar, steps=(2, 6, 10, 14), vel=1.0, inst="lute"):
    for s in steps:
        ch = CHORD[chord_at(bar, s)]
        T["chop"].add(strum([m - 12 for m in ch], S16 * 1.1, vel * (1.0 if s % 8 == 6 else 0.85),
                            down=(s % 4 == 2), inst=inst), ts(bar, s) + hum(0.004))

def fill(bar, start=12, kind="toms", vel=1.0, end=16):
    ps = [170, 150, 132, 118, 104, 92, 82, 74]
    for i, s in enumerate(np.arange(start, end, 1.0)):
        t = ts(bar, s) + hum(0.002)
        if kind == "toms":
            T["tom"].add(tom(ps[i % 8], (0.6 + 0.08 * i) * vel), t)
        else:
            T["clap"].add(clap((0.35 + 0.12 * i) * vel), t)
            T["frame"].add(frame(0.5, 100 + 8 * i, False), t)

def snare_roll(bar, nbars=1, start=0, stop=None):
    total = nbars * 16 - start
    for i in range(total * 2):
        s = start + i / 2
        if stop is not None and s >= stop:
            break
        b = bar + int(s // 16); ss = s % 16
        if i % 2 == 1 and i < total:      # 16ths first half, 32nds second half
            continue
        v = 0.2 + 0.75 * (i / (total * 2)) ** 1.5
        T["clap"].add(clap(v * 0.8), ts(b, ss) + hum(0.002))
        T["frame"].add(frame(v * 0.6, 110, False), ts(b, ss))

def stop_hits(bar, steps, notes=None, vel=1.0):
    """band-wide tresillo punches"""
    for s in steps:
        t = ts(bar, s)
        ch = CHORD[chord_at(bar, s)]
        T["kick"].add(club_kick(vel), t)
        T["bass"].add(deep_bass(ROOT[chord_at(bar, s)], S16 * 2, vel, pop=False), t)
        T["chop"].add(strum([m - 12 for m in ch] + [ch[0]], S16 * 1.6, vel), t)
        T["clap"].add(clap(0.7 * vel), t)

def drone_span(b0, b1, midis, buzz=True):
    t0 = ts(b0, 0)
    times = [(ts(b, s) - t0, 1.0 if s % 4 == 2 else 0.55) for b in range(b0, b1) for s in (2, 6, 10, 14, 3, 11)] if buzz else []
    T["drone"].add(gurdy_drone(ts(b1, 0) - t0 + 0.05, midis, times), t0)

# ============================================================================ ARRANGEMENT
MAP = []
def section(t, txt):
    MAP.append((t, txt))

# ---------- 0-3.6 s : the hook, immediately ----------
section(0.0, "HOOK at once: lute (tremolo) + fiddle, half-time kick, claps, frame-drum bounce")
for b, h in ((0, H1), (1, H2)):
    lute_line(b, h, 1.0)
    fiddle_line(b, h, 0.7, double=False)
    drums(b, "intro")
    bassline(b, "intro")
accent(ts(0, 6), "hit", "first hook leap (A5) -- signature moment")
accent(ts(1, 6), "hit", "hook leap #2 (G5)")
accent(ts(1, 14), "fill", "frame-drum pickup")

# ---------- 3.6-5.45 s : build ----------
section(ts(2, 0), "BUILD: hook bar 3 cut short, clap roll, riser, kick 8ths, bass drops out -> gasp")
lute_line(2, H3[:5], 1.0); fiddle_line(2, H3[:5], 0.8, double=False)
for s in range(0, 12, 2):
    T["kick"].add(club_kick(0.6 + 0.04 * s), ts(2, s))
snare_roll(2, 1, 0, stop=12)
T["bass"].add(deep_bass(34, dur(2, 0, 6), 0.8), ts(2, 0))
T["fx"].add(sweep(BAR, 1.2), ts(2, 0))
T["fx"].add(rev_cym(BEAT * 1.0, 1.0), ts(3, 0) - BEAT)
accent(ts(2, 0), "build", "build starts (roll + riser)")
accent(ts(2, 12), "vox", "GASP -- inhale before the drop")

# ---------- 5.45-21.8 s : main groove ----------
section(ts(3, 0), "DROP: full hook x2 -- fiddle (double-tracked) + lute, deep tresillo bass, four-on-the-floor")
T["cym"].add(crash(2.2, 1.0), ts(3, 0))
for i, b in enumerate(range(3, 11)):
    h = HOOK[i % 4]
    fiddle_line(b, h, 1.0)
    lute_line(b, h, 0.4, tr=-12, pan=-0.4)
    drums(b, "drop", skip=((12, 13, 14, 15) if b in (6, 10) else ()), keep_kick=True)
    bassline(b, "tres")
    chops(b, (2, 6, 10) if b in (6, 10) else (2, 6, 10, 14), vel=0.9)
    if b >= 7 and i % 4 < 3:
        accent(ts(b, 6), "hit", "hook leap")
    if b >= 7:   # second pass: flute answers on top
        if i % 4 in (0, 2):
            for s, m in ((12, 86), (14, 84)):
                T["flute"].add(flute(m, S16 * 1.6, 0.75), ts(b, s))
accent(ts(3, 0), "drop", "DROP (crash, full band)")
accent(ts(4, 6), "hit", "hook leap (bar 2)")
accent(ts(5, 6), "hit", "hook leap to Bb (bar 3)")
accent(ts(6, 8), "hit", "cadence lands on D")
accent(ts(6, 12), "vox", "chuckle x2 in the hook gap (call & response)")
T["cym"].add(crash(1.6, 0.8), ts(7, 0)); accent(ts(7, 0), "crash", "hook pass 2, flute joins")
accent(ts(8, 12), "lick", "flute answer")
accent(ts(9, 12), "lick", "flute answer")
flute_lick(10, 12, [74, 76, 77, 79, 81, 84], 0.9); accent(ts(10, 12), "lick", "flute run up into the stop")

# ---------- transition bar 11 ----------
section(ts(11, 0), "STOP-TIME: band punches the tresillo, toms, surprised 'oh!' -> variation")
stop_hits(11, (0, 3, 6))
for s, l, m in H1[:3]:
    T["fiddle"].add(fiddle(m, dur(11, s, l) * 0.7, 1.0, "spic"), ts(11, s))
    T["lute"].add(lute_v(m - 12, dur(11, s, l) * 0.7, 0.6), ts(11, s))
fill(11, 8, "toms", 0.9, end=12)
for s in range(16):
    T["shaker"].add(shaker(0.6 if s % 4 == 2 else 0.3), ts(11, s))
T["fx"].add(rev_cym(BEAT * 1.0, 1.1), ts(12, 0) - BEAT)
accent(ts(11, 0), "stop", "stop-time punch 1"); accent(ts(11, 3), "stop", "punch 2"); accent(ts(11, 6), "stop", "punch 3")
accent(ts(11, 8), "fill", "tom fill")
accent(ts(11, 12), "vox", "surprised 'oh!'")

# ---------- 21.8-38.2 s : variation ----------
section(ts(12, 0), "VARIATION: flute leads the hook with a climbing run + dorian B; new syncopated bass; woodblocks")
T["cym"].add(crash(2.2, 0.9), ts(12, 0))
for i, b in enumerate(range(12, 16)):
    flute_line(b, VAR[i], 1.0)
    fiddle_line(b, [(s, l, m) for s, l, m in VAR[i] if s < 8], 0.3, tr=-12, double=False)   # fiddle shadows the tresillo
    drums(b, "var", skip=((12, 13, 14, 15) if b == 15 else ()), keep_kick=True)
    bassline(b, "var")
    chops(b, (2, 6, 10) if b == 15 else (2, 6, 10, 14), vel=0.8)
accent(ts(12, 0), "crash", "variation starts")
accent(ts(13, 6), "hit", "flute leap to C6")
accent(ts(14, 6), "hit", "flute leap to D6 (highest point so far)")
accent(ts(15, 12), "vox", "chuckle x2 in the gap")

section(ts(16, 0), "MINI-BREAK: drums thin out, call & response -- lute plays the tresillo, flute answers the run")
for i, b in enumerate(range(16, 20)):
    h = HOOK[i]
    call = [(s, l, m) for s, l, m in h if s < 8]
    resp = [(s, l, m) for s, l, m in h if s >= 8]
    lute_line(b, call, 1.0)
    if b < 19:
        flute_line(b, resp, 0.95, tr=12)
    else:
        flute_line(b, h[4:], 0.95, tr=12)
        fiddle_line(b, h[:4], 0.8)
    if b < 18:
        drums(b, "break")
        bassline(b, "intro", 0.9)
        chops(b, (6, 14), 0.7, inst="pizz")
    else:
        drums(b, "var", skip=((12, 13, 14, 15) if b == 19 else ()))
        bassline(b, "var")
        chops(b, vel=0.8)
fill(17, 12, "claps", 1.0)
T["cym"].add(crash(1.8, 0.85), ts(18, 0))
flute_lick(19, 12, [81, 79, 77, 76, 74, 72, 74, 76], 0.85)
accent(ts(16, 0), "break", "drums thin out (call & response)")
for b in (16, 17, 18):
    accent(ts(b, 8), "lick", "flute answers the lute")
accent(ts(17, 12), "fill", "clap fill")
accent(ts(18, 0), "crash", "groove back in")
accent(ts(19, 12), "lick", "flute tumble")

# ---------- transition bar 20 ----------
section(ts(20, 0), "TRANSITION: bass solo riff over claps, 'oh!' on beat 4 -> climax block")
for s, l, iv, pop in ((0, 2, 0, False), (3, 1, 12, True), (4, 2, 10, False), (6, 1, 7, False), (7, 1, 12, True),
                      (8, 2, 0, False), (10, 1, 2, False)):
    r = ROOT[chord_at(20, s)]
    T["bass"].add(deep_bass(r + iv, dur(20, s, l) * 0.9, 1.0, pop=pop), ts(20, s))
for s in (4, 8):
    T["clap"].add(clap(1.0), ts(20, s))
for s in range(12):
    T["shaker"].add(shaker(0.8 if s % 4 == 2 else 0.35), ts(20, s))
T["kick"].add(club_kick(1.0), ts(20, 0)); T["kick"].add(club_kick(0.9), ts(20, 8))
T["fx"].add(rev_cym(BEAT * 1.0, 1.2), ts(21, 0) - BEAT)
accent(ts(20, 0), "break", "bass solo")
accent(ts(20, 12), "vox", "surprised 'oh!'")

# ---------- 38.2-54.5 s : stronger bass, rhythmic variations, climax ----------
section(ts(21, 0), "BASS LOCK: bass doubles the hook rhythm under fiddle + lute, hurdy-gurdy buzz, kick stutters")
T["cym"].add(crash(2.4, 1.0), ts(21, 0))
drone_span(21, 25, (50, 57))
for i, b in enumerate(range(21, 25)):
    h = HOOK[i]
    fiddle_line(b, h, 1.0)
    lute_line(b, h, 0.6, tr=-12, pan=-0.4)
    drums(b, "lock", skip=((12, 13, 14, 15) if b == 24 else ()))
    bassline(b, "lock", 1.05)
    chops(b, (2, 10), 0.8)
    accent(ts(b, 6), "hit", "hook leap over the bass lock")
    # flute: long high counter-notes
    T["flute"].add(flute([81, 79, 77, 79][i] + 12, dur(b, 0, 7), 0.6), ts(b, 0) + 0.02)
stop_hits(24, (12, 14), vel=0.9)
accent(ts(21, 0), "drop", "bass-lock section (crash)")
accent(ts(22, 10), "hit", "kick stutter")
accent(ts(24, 10), "hit", "kick stutter")
accent(ts(24, 12), "stop", "double punch")

section(ts(25, 0), "BUILD x2: hook head sequenced upward (D D A, E E Bb, F F C, G G D), roll, riser, gasp")
seq = [(25, 0, 74, 81), (25, 8, 76, 82), (26, 0, 77, 84), (26, 8, 79, 86)]
for b, s0, a, top in seq:
    cellnotes = ((0, 3, a), (3, 3, a), (6, 2, top)) if (b, s0) != (26, 8) else ((0, 2, a), (2, 1, a))   # last climb breaks off for the gasp
    for s, l, m in cellnotes:
        T["fiddle"].add(fiddle(m, dur(b, s0 + s, l) * 0.85, 1.0, "spic" if l < 3 else "legato"), ts(b, s0 + s))
        T["fiddle2"].add(fiddle(m, dur(b, s0 + s, l) * 0.85, 0.7, "spic" if l < 3 else "legato", det=-6), ts(b, s0 + s) + 0.012)
        T["lute"].add(lute_v(m - 12, dur(b, s0 + s, l) * 0.9, 0.7), ts(b, s0 + s))
        T["bass"].add(deep_bass(ROOT[chord_at(b, s0)] + (0 if s < 6 else 12), dur(b, s0 + s, l) * 0.85, 0.95, pop=s == 6), ts(b, s0 + s))
    accent(ts(b, s0), "hit", f"rising hook head ({['D','E','F','G'][seq.index((b, s0, a, top))]})")
for b in (25, 26):
    for s in ((0, 4, 8, 12) if b == 25 else (0, 4, 8)):
        T["kick"].add(club_kick(0.95), ts(b, s))
    for s in range(16):
        T["shaker"].add(shaker(0.7 if s % 4 == 2 else 0.3), ts(b, s))
snare_roll(26, 1, 0, stop=12)
T["fx"].add(sweep(BAR * 2 - S16 * 4, 1.3), ts(25, 0))
T["fx"].add(rev_cym(BEAT * 1.0, 1.3), ts(27, 0) - BEAT)
accent(ts(26, 12), "vox", "GASP -- inhale before the climax")

section(ts(27, 0), "CLIMAX: whole band on the hook -- fiddles + lute + flute 8va, driving 16th bass, hurdy-gurdy")
T["cym"].add(crash(2.6, 1.2), ts(27, 0))
drone_span(27, 31, (50, 57, 62))
for i, b in enumerate(range(27, 31)):
    h = HOOK[i]
    fiddle_line(b, h, 1.05)
    lute_line(b, h, 0.7, pan=-0.35)
    flute_line(b, h, 0.8, tr=12, ornament=False)
    drums(b, "climax", skip=((13, 14, 15) if b == 30 else ()))
    bassline(b, "drive", 1.05)
    chops(b, vel=0.95)
T["cym"].add(crash(1.8, 0.9), ts(29, 0))
accent(ts(27, 0), "drop", "CLIMAX (big crash)")
accent(ts(28, 6), "hit", "hook leap")
accent(ts(29, 0), "crash", "crash -- hook bar 3")
accent(ts(30, 8), "hit", "cadence lands on D")
fill(30, 12, "toms", 1.0); accent(ts(30, 12), "fill", "tom fill into the final phrase")

# ---------- 56.4-60 s : final phrase + loop seam ----------
section(ts(31, 0), "FINAL PHRASE: stop-time tresillo with chuckles, then the cadence F E D C | D and a pickup back to bar 1")
stop_hits(31, (0, 3, 6), vel=1.05)
for s, l, m in H1[:3]:
    fiddle_line(31, [(s, l, m)], 1.05)
    T["flute"].add(flute(m + 12, dur(31, s, l) * 0.7, 0.8), ts(31, s))
for s, l, m in H1[5:]:          # the run answers the chuckle: E F
    fiddle_line(31, [(s, l, m)], 0.95)
accent(ts(31, 8), "vox", "chuckle x2 between the punches and the run")
for s in range(16):
    T["shaker"].add(shaker(0.8 if s % 4 == 2 else 0.35), ts(31, s))
T["kick"].add(club_kick(0.9), ts(31, 12)); T["clap"].add(clap(0.9), ts(31, 12))
T["bass"].add(deep_bass(38, dur(31, 12, 2) * 0.9, 0.9), ts(31, 12))
T["bass"].add(deep_bass(41, dur(31, 14, 2) * 0.9, 0.8, pop=True), ts(31, 14))
accent(ts(31, 0), "stop", "final punch 1"); accent(ts(31, 3), "stop", "final punch 2"); accent(ts(31, 6), "stop", "final punch 3")
fiddle_line(32, H4, 1.1)
lute_line(32, H4, 0.8, pan=-0.35)
flute_line(32, H4, 0.85, tr=12, ornament=False)
drums(32, "climax", skip=(12, 13, 14, 15))
bassline(32, "drive", 1.05)
chops(32, (2, 6, 10), 0.95)
T["cym"].add(crash(1.5, 0.9), ts(32, 8))
fill(32, 12, "claps", 1.0)
T["kick"].add(club_kick(0.9), ts(32, 12))
T["bass"].add(deep_bass(45, dur(32, 12, 2) * 0.8, 0.9, pop=True), ts(32, 12))
T["bass"].add(deep_bass(37, dur(32, 14, 2) * 0.8, 0.9), ts(32, 14))      # C# -> D: pulls back into bar 1
accent(ts(32, 0), "hit", "final cadence F E D C")
accent(ts(32, 8), "crash", "lands on D (crash)")
accent(ts(32, 12), "fill", "clap pickup -> loops to 0:00")

# ============================================================================ HUMAN REACTIONS
def load_vox(name):
    sr, x = wavfile.read(os.path.join(HERE, "vox", name + ".wav"))
    x = x.astype(float) / 32768.0
    x = x.mean(axis=1) if x.ndim > 1 else x
    return signal.resample_poly(x, SR, sr) if sr != SR else x

def envelope(x, fc):
    sos = signal.butter(2, fc / (SR / 2), "low", output="sos")
    return np.sqrt(signal.sosfiltfilt(sos, x ** 2).clip(1e-12))

def audition(name, x):
    """objective look at each take: length, noise floor, clipping, voiced share, attack speed"""
    e = 20 * np.log10(envelope(x, 30)); pk = e.max()
    act = e > pk - 30
    on = np.argmax(e > pk - 20); peak_i = np.argmax(e)
    return dict(name=name, active_s=round(act.sum() / SR, 2), floor_db=round(np.percentile(e, 5) - pk, 1),
                clip=bool(np.abs(x).max() > 0.99), attack_ms=round((peak_i - on) / SR * 1000))

def vox_chain(x, presence=2.5):
    x = filt(x, "high", 110, order=2)
    x = peq(x, 330, -3.0, 1.0)
    x = peq(x, 3300, presence, 1.0)
    x = shelf(x, 9000, 1.5)
    e = envelope(x, 40); db = 20 * np.log10(e); thr = db.max() - 10
    x = x * 10 ** (-np.maximum(0, db - thr) * (1 - 1 / 3.5) / 20)    # 3.5:1, fast
    return x / np.abs(x).max()

def onset(x, rel_db=-20):
    e = envelope(x, 60)
    return int(np.argmax(20 * np.log10(e) > 20 * np.log10(e.max()) + rel_db))

def syllables(x):
    fr = int(0.005 * SR)
    e = np.array([np.sqrt((x[i:i + fr] ** 2).mean()) for i in range(0, len(x) - fr, fr)])
    db = 20 * np.log10(e + 1e-9); act = db > db.max() - 22
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
        s0 = max(0, a * fr - int(0.01 * SR))
        end = segs[k + 1][0] * fr - int(0.01 * SR) if k + 1 < len(segs) else min(len(x), b * fr + int(0.08 * SR))
        seg = x[s0:end].copy()
        fo = min(len(seg) // 3, int(0.035 * SR)); seg[-fo:] *= np.linspace(1, 0, fo) ** 2
        out.append(seg)
    return out

RAW = {k: load_vox(k) for k in ("gasp", "surprised", "chuckle", "sigh")}
AUDITION = [audition(k, v) for k, v in RAW.items()]
VOX = {k: vox_chain(v) for k, v in RAW.items() if k != "sigh"}   # sigh: auditioned, not selected (see notes)
SYL = syllables(VOX["chuckle"])
# rank chuckle syllables by punch (peak-to-rms) -> use the crispest ones as percussion
punch = [np.abs(s).max() / (np.sqrt((s ** 2).mean()) + 1e-9) * np.abs(s).max() for s in SYL]
BEST = [SYL[i] for i in np.argsort(punch)[::-1][:5]]

VOXT = Track(0, 0.0, 0.2)
EVENTS, VOX_LOG = [], []
SRC = {"gasp": "Short_natural_male_g_4 (gasp)", "surprised": "Short_natural_male_s_4 (surprised 'oh!')",
       "chuckle": "Short_mischievous_ma_1 (chuckle)"}

def place(name, x, bar, step, rel_db, pan=0.0, note=""):
    t_grid = ts(bar, step)
    t0 = t_grid - onset(x) / SR - 0.006      # attack a hair ahead of the grid, like a drummer
    EVENTS.append((x, t0, rel_db, pan))
    VOX_LOG.append((t_grid, t0, t0 + len(x) / SR, name, bar, step, note))

place("gasp", VOX["gasp"], 2, 12, -1.5, 0.0, "inhale into the first drop")
place("chuckle", BEST[0], 6, 12, -1.0, -0.15, "'heh' 1/2 -- answers the hook cadence")
place("chuckle", BEST[1], 6, 14, -3.0, 0.15, "'heh' 2/2")
place("surprised", VOX["surprised"], 11, 12, -1.0, 0.0, "'oh!' after the stop-time punches -> variation")
place("chuckle", BEST[2], 15, 12, -1.5, 0.15, "'heh' 1/2 -- answers the flute")
place("chuckle", BEST[3], 15, 14, -3.0, -0.15, "'heh' 2/2")
place("surprised", VOX["surprised"], 20, 12, -1.0, 0.05, "'oh!' over the bass solo -> bass-lock section")
place("gasp", VOX["gasp"], 26, 12, -1.0, 0.0, "inhale at the top of the build -> climax")
place("chuckle", BEST[0], 31, 8, -2.0, -0.12, "'heh' 1/2 -- between the final punches and the run")
place("chuckle", BEST[4], 31, 10, -2.5, 0.12, "'heh' 2/2")

def render_vox(ref):
    VOXT.buf[:] = 0
    for x, t0, rel_db, pan in EVENTS:
        e = envelope(x, 30); m = 20 * np.log10(e) > 20 * np.log10(e.max()) - 25
        g = ref * 10 ** (rel_db / 20) / np.sqrt((x[m] ** 2).mean())
        VOXT.add(x * g, t0, pan=pan)

# ============================================================================ MIX
LEVELS = {"kick": 1.15, "clap": 3.6, "snap": 5.0, "shaker": 4.2, "tamb": 2.8, "frame": 2.6, "wood": 3.5, "tom": 1.9,
          "cym": 2.2, "fx": 1.3, "bass": 1.7, "chop": 0.3, "lute": 1.0, "fiddle": 5.5, "fiddle2": 3.4,
          "flute": 2.7, "drone": 2.6}
DUCK = {"bass": 0.85, "chop": 0.6, "drone": 0.6, "tamb": 0.25, "lute": 0.2, "fiddle2": 0.15}

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

IR_ROOM = make_ir(1.2)
IR_PLATE = np.vstack([np.zeros((int(0.015 * SR), 2)), make_ir(0.7, er=False, damp=9000)])

def mixdown(with_vox):
    ke = filt(np.abs(T["kick"].buf[:, 0]), "low", 25); ke /= ke.max() + 1e-9
    sc = 1 - 0.6 * np.clip(ke * 2.5, 0, 1)
    bus = np.zeros((N + PAD, 2)); room = np.zeros_like(bus); plate = np.zeros_like(bus)
    for k, tr in T.items():
        x = tr.buf * LEVELS[k]
        if k in DUCK:
            x = x * (1 - DUCK[k] + DUCK[k] * sc)[:, None]
        if k == "bass":
            x = filt(x, "high", 30)
        elif k not in ("kick", "tom"):
            x = filt(x, "high", 55 if k in ("drone", "frame") else 110)
        bus += x; room += x * tr.rev; plate += x * tr.plate
    if with_vox:
        v = VOXT.buf
        ve = filt(np.abs(v[:, 0]), "low", 8); ve /= ve.max() + 1e-9
        bus *= (1 - 0.2 * np.clip(ve * 3, 0, 1))[:, None]          # band leans back ~2 dB under a reaction
        bus += v; plate += v * VOXT.plate
    wet = np.stack([signal.fftconvolve(room[:, c], IR_ROOM[:, c])[: len(room)] for c in range(2)], 1)
    wet2 = np.stack([signal.fftconvolve(plate[:, c], IR_PLATE[:, c])[: len(plate)] for c in range(2)], 1)
    x = bus + wet + wet2 * 0.9
    # seamless loop: whatever rings past 60 s is folded onto the start
    x[:PAD] += x[N:N + PAD]
    return x[:N]

def master_eq(x):
    x = filt(x, "high", 30)
    x = peq(x, 100, 1.5, 0.9)         # bass body
    x = peq(x, 300, -1.8, 0.9)        # de-mud
    x = peq(x, 3000, -0.8, 1.2)
    x = shelf(x, 6000, 2.5)           # air
    return x

def glue(x, thr_db=-14, ratio=2.0, att=0.01, rel=0.14):
    lvl = np.sqrt(filt((x ** 2).mean(axis=1), "low", 12).clip(1e-12))
    g = 10 ** (-np.maximum(0, 20 * np.log10(lvl) - thr_db) * (1 - 1 / ratio) / 20)
    out = np.empty_like(g); prev = 1.0
    aa, ar = np.exp(-64 / (att * SR)), np.exp(-64 / (rel * SR))
    for i in range(0, len(g), 64):
        tgt = g[i:i + 64].min(); c = aa if tgt < prev else ar
        prev = c * prev + (1 - c) * tgt; out[i:i + 64] = prev
    return x * out[:, None]

def limiter(x, ceil=0.87, rel=0.05):
    up = signal.resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(axis=1)[: len(x) * 4].reshape(-1, 4).max(axis=1)
    pk = maximum_filter1d(pk, size=2 * int(0.003 * SR) + 1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    out = np.empty_like(g); prev = 1.0; ar = np.exp(-1 / (rel * SR))
    for i in range(len(g)):
        v = g[i]; prev = v if v < prev else ar * prev + (1 - ar) * v; out[i] = prev
    return x * np.minimum(filt(out, "low", 400), g)[:, None]

def stereo_width(x, amt=1.15):
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2
    s = filt(s, "high", 180) * amt          # mono below 180 Hz, a little wider above
    return np.stack([m + s, m - s], 1)

def master(x, pre, drive):
    x = master_eq(x) * pre
    x = stereo_width(x)
    x = glue(x)
    x = np.tanh(x * 1.5) / np.tanh(1.5)
    return limiter(x * drive)

def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x)

def write(name, x):
    wavfile.write(os.path.join(OUT, name), SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))

if __name__ == "__main__":
    inst = mixdown(False)
    render_vox(np.sqrt((inst ** 2).mean()))
    full = mixdown(True)
    pre = 0.5 / np.abs(master_eq(full)).max()
    drive = 10 ** ((-9.5 - lufs(master(full, pre, 1.0))) / 20)
    final = master(full, pre, drive)
    assert final.shape == (N, 2)
    write("MEDIEVAL_MEDICINE_V3_MASTER.wav", final)
    write("_v3_instrumental_check.wav", master(inst, pre, drive))            # QA only
    v = VOXT.buf.copy()
    vw = np.stack([signal.fftconvolve(v[:, c] * VOXT.plate, IR_PLATE[:, c])[: len(v)] for c in range(2)], 1)
    v = v + vw * 0.9; v[:PAD] += v[N:N + PAD]; v = master_eq(v[:N]) * pre * drive
    write("MEDIEVAL_MEDICINE_V3_VOX_STEM.wav", v * min(1.0, 0.89 / np.abs(v).max()))
    with open(os.path.join(OUT, "MEDIEVAL_MEDICINE_V3_CUES.md"), "w") as f:
        f.write("# MEDIEVAL MEDICINE V3 -- cue sheet\n\n132 BPM, 4/4, 33 bars = 60.000 s, D minor (dorian/aeolian). "
                "1 bar = 1.818 s, 1 beat = 0.455 s. Loops seamlessly from 60.000 back to 0.000.\n\n")
        f.write("## Human reactions (vocal stem)\n\n| # | Grid time (s) | Audible (s) | Bar / beat | Source take | Role |\n|---|---|---|---|---|---|\n")
        for i, (tg, a, b, name, bar, step, note) in enumerate(sorted(VOX_LOG)):
            f.write(f"| {i + 1} | {tg:6.3f} | {a:6.3f} - {b:6.3f} | {bar + 1} / {step / 4 + 1:.2f} | {SRC[name]} | {note} |\n")
        f.write("\n## Audition notes\n\n| Take | Active (s) | Noise floor (dB rel. peak) | Clipping | Attack (ms) | Used |\n|---|---|---|---|---|---|\n")
        for a in AUDITION:
            used = "no -- slow 1 s exhale with a breathy pre-roll; it stalls the forward motion" if a["name"] == "sigh" else "yes"
            f.write(f"| {a['name']} | {a['active_s']} | {a['floor_db']} | {a['clip']} | {a['attack_ms']} | {used} |\n")
        f.write("\n## Arrangement\n\n")
        for t, txt in MAP:
            f.write(f"- **{t:6.2f} s** (bar {int(round(t / BAR)) + 1}) -- {txt}\n")
        f.write("\n## Sync accents for animation (every 2-3 s or closer)\n\n| Time (s) | Bar / beat | Type | What you hear |\n|---|---|---|---|\n")
        for t, kind, txt in sorted(ACCENTS):
            bar = int(t // BAR); beat = (t - bar * BAR) / BEAT + 1
            f.write(f"| {t:6.3f} | {bar + 1} / {beat:.2f} | {kind} | {txt} |\n")
    print("LUFS", round(lufs(final), 2), "events", len(VOX_LOG), "accents", len(ACCENTS))
