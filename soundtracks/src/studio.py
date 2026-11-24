"""
studio.py - a small, dependency-light music production engine (numpy + scipy).

Everything here is synthesised from scratch: additive / physical-model
instruments (clarinet, brass section, upright bass, Karplus-Strong plucks,
vintage piano, formant "vocal" chops, mallets), synthesised drums, FX,
and a mix/master chain (sidechain, convolution reverb, tempo delay,
glue compression, look-ahead limiter, LUFS targeting).

Global song grid (shared by all four candidates):
  144 beats in exactly 65.0 s  ->  132.92 BPM
"""
import re
import numpy as np
from collections import defaultdict
from scipy.signal import lfilter, fftconvolve
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

SR = 44100
TOTAL_BEATS = 144
DUR = 65.0
SPB = DUR / TOTAL_BEATS          # seconds per beat (0.4514)
BPM = 60.0 / SPB                 # 132.92
TAIL = 4.0                       # render tail that gets wrapped for the loop

# ----------------------------------------------------------------- pitch utils
_NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def nn(s):
    m = re.fullmatch(r'([A-G])([#b]?)(-?\d)', s)
    if not m:
        raise ValueError(f'bad note {s!r}')
    v = _NOTE[m[1]] + (1 if m[2] == '#' else -1 if m[2] == 'b' else 0)
    return v + 12 * (int(m[3]) + 1)


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


QUAL = {
    '': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10],
    'maj7': [0, 4, 7, 11], '6': [0, 4, 7, 9], 'm6': [0, 3, 7, 9],
    '9': [0, 4, 7, 10, 14], 'm9': [0, 3, 7, 10, 14], '7b9': [0, 4, 7, 10, 13],
    'dim7': [0, 3, 6, 9], '7#9': [0, 4, 7, 10, 15], 'sus4': [0, 5, 7],
    'aug': [0, 4, 8], 'mmaj7': [0, 3, 7, 11], 'maj9': [0, 4, 7, 11, 14],
    '69': [0, 4, 7, 9, 14], 'm11': [0, 3, 7, 10, 14, 17], '13': [0, 4, 10, 14, 21],
    '7sus4': [0, 5, 7, 10], 'dim': [0, 3, 6],
}


def chord(sym):
    m = re.fullmatch(r'([A-G][#b]?)(.*)', sym)
    root = _NOTE[m[1][0]] + (1 if m[1][1:] == '#' else -1 if m[1][1:] == 'b' else 0)
    return root % 12, QUAL[m[2]]


def voicing(sym, low, n=None, drop_root=False):
    """Close-position voicing with every tone in [low, low+12)."""
    root, iv = chord(sym)
    pcs = [(root + i) % 12 for i in iv]
    if drop_root and len(pcs) > 3:
        pcs = pcs[1:]
    out = sorted(low + ((pc - low) % 12) for pc in pcs)
    if n:
        out = out[-n:]
    return out


def bass_root(sym, low=nn('E1')):
    root, _ = chord(sym)
    return low + ((root - low) % 12)


# ----------------------------------------------------------- timing / grooves
def warp(beat, s8=0.5, s16=0.5):
    """Swing: s8 moves the off-8th inside each beat, s16 the off-16th inside each 8th."""
    b = np.floor(beat)
    u = beat - b
    if s8 != 0.5:
        u = np.where(u < 0.5, u / 0.5 * s8, s8 + (u - 0.5) / 0.5 * (1 - s8))
    if s16 != 0.5:
        e = np.floor(u * 2) / 2
        w = (u - e) * 2
        w = np.where(w < 0.5, w / 0.5 * s16, s16 + (w - 0.5) / 0.5 * (1 - s16))
        u = e + w / 2
    return b + u


def seq(s, start=0.0, tr=0, vel=0.8):
    """Melody notation. Tokens  [acc][(grace)]NOTE:DUR16[flags]  or r:DUR16, '|' checks bar.
    acc: ! accent  . soft  ? ghost.   flags: ~ glide-in  \\ fall-off  ^ scoop  ' staccato  _ tenuto"""
    ev, t = [], start
    for tok in s.split():
        if tok == '|':
            if abs(((t - start) / 4) - round((t - start) / 4)) > 1e-6:
                raise ValueError(f'bar check failed at {t - start} in {s[:60]}')
            continue
        m = re.fullmatch(r"([!.?]?)(?:\(([A-G][#b]?-?\d)\))?([A-G][#b]?-?\d|r):([\d.]+)([~\\^'_]*)", tok)
        if not m:
            raise ValueError(f'bad token {tok!r}')
        acc, grace, note, dur, fl = m.groups()
        d = float(dur) / 4.0
        if note != 'r':
            ev.append(dict(t=t, d=d, n=nn(note) + tr,
                           v={'!': 1.0, '.': 0.55, '?': 0.38, '': vel}[acc],
                           gr=(nn(grace) + tr) if grace else None,
                           gl='~' in fl, fall='\\' in fl, scoop='^' in fl,
                           stac="'" in fl, ten='_' in fl))
        t += d
    return ev


def rseq(s, start=0.0, vel=0.8):
    """Relative (semitone) sequence for basslines: tokens [acc]SEMI:DUR16 or r:DUR16, x = dead note."""
    ev, t = [], start
    for tok in s.split():
        if tok == '|':
            continue
        m = re.fullmatch(r"([!.?]?)(-?\d+|r|x):([\d.]+)([~'\\_]*)", tok)
        if not m:
            raise ValueError(f'bad token {tok!r}')
        acc, semi, dur, fl = m.groups()
        d = float(dur) / 4.0
        if semi != 'r':
            ev.append(dict(t=t, d=d, s=0 if semi == 'x' else int(semi), dead=semi == 'x',
                           v={'!': 1.0, '.': 0.55, '?': 0.38, '': vel}[acc],
                           gl='~' in fl, stac="'" in fl, fall='\\' in fl))
        t += d
    return ev


def hits(pattern, start=0.0):
    """16th step grid. X=1.0 x=0.8 o=0.55 g=0.32 . = rest. Spaces/| ignored."""
    p = pattern.replace(' ', '').replace('|', '')
    vel = {'X': 1.0, 'x': 0.8, 'o': 0.55, 'g': 0.32}
    return [(start + i * 0.25, vel[c]) for i, c in enumerate(p) if c in vel]


# --------------------------------------------------------------- dsp helpers
def _rbj(kind, f, q=0.707, gain_db=0.0):
    f = min(max(f, 10.0), SR * 0.49)
    w0 = 2 * np.pi * f / SR
    c, s = np.cos(w0), np.sin(w0)
    al = s / (2 * q)
    A = 10 ** (gain_db / 40)
    if kind == 'lp':
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == 'hp':
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == 'bp':
        b = [al, 0, -al]; a = [1 + al, -2 * c, 1 - al]
    elif kind == 'peak':
        b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
    elif kind in ('ls', 'hs'):
        sq = 2 * np.sqrt(A) * al
        if kind == 'ls':
            b = [A * ((A + 1) - (A - 1) * c + sq), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sq)]
            a = [(A + 1) + (A - 1) * c + sq, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sq]
        else:
            b = [A * ((A + 1) + (A - 1) * c + sq), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sq)]
            a = [(A + 1) - (A - 1) * c + sq, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sq]
    else:
        raise ValueError(kind)
    b, a = np.array(b), np.array(a)
    return b / a[0], a / a[0]


def filt(x, kind, f, q=0.707, gain_db=0.0):
    b, a = _rbj(kind, f, q, gain_db)
    return lfilter(b, a, x, axis=-1)


def lp(x, f, q=0.707): return filt(x, 'lp', f, q)
def hp(x, f, q=0.707): return filt(x, 'hp', f, q)
def bp(x, f, q=1.0): return filt(x, 'bp', f, q)


def tv_filter(x, kind, fc, q=0.9, block=256):
    """Time-varying biquad; fc is a function of time (s) -> Hz."""
    y = np.zeros_like(x)
    zi = np.zeros(2)
    for i in range(0, len(x), block):
        b, a = _rbj(kind, fc(i / SR), q)
        y[i:i + block], zi = lfilter(b, a, x[i:i + block], zi=zi)
    return y


def smoothstep(a, b, t):
    u = np.clip((t - a) / max(b - a, 1e-9), 0, 1)
    return u * u * (3 - 2 * u)


def env_gate(t, att, gate, rel, curve=True):
    a = np.clip(t / max(att, 1e-5), 0, 1)
    if curve:
        a = np.sin(a * np.pi / 2) ** 2
    r = np.where(t > gate, np.exp(-(t - gate) / max(rel, 1e-4)), 1.0)
    return a * r


def _harm_sum(ph, f0max, base, bright, maxk=64, fmax=16500, phis=None):
    """Sum_k base(k) * r^(k-1) * sin(k*ph); r = exp(-1/bright) works like a moving low-pass."""
    out = np.zeros_like(ph)
    r = np.exp(-1.0 / np.maximum(bright, 0.05))
    w = np.ones_like(ph)
    for k in range(1, maxk + 1):
        if k * f0max > fmax:
            break
        bk = base(k)
        if bk:
            off = phis[k] if phis is not None else 0.0
            out += bk * w * np.sin(k * ph + off)
        w = w * r
    return out


# ------------------------------------------------------------------ instruments
class Inst:
    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)

    def noise(self, n):
        return self.rng.standard_normal(n)

    # ---- clarinet: odd-harmonic additive reed model w/ breath, scoops, glides, falls
    def clarinet(self, n, dur, vel=0.8, prev=None, glide=False, grace=None, fall=False,
                 scoop=False, stac=False, ten=False, vib=1.0, bright_mul=1.0, rel=0.07):
        gate = dur * (0.5 if stac else 1.0 if ten else 0.9)
        gate = max(gate, 0.05)
        N = int((gate + rel * 6 + (0.25 if fall else 0)) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n))
        if glide and prev is not None:
            p += (prev - n) * np.exp(-t / 0.03)
        if grace is not None:
            p += (grace - n) * (1 - smoothstep(0.035, 0.06, t))
        if scoop or vel >= 0.99:
            p -= 0.55 * np.exp(-t / 0.035)
        p += 0.11 * vib * smoothstep(0.16, 0.42, t) * np.sin(2 * np.pi * 5.4 * t + self.rng.uniform(0, 6))
        p += 0.04 * np.sin(2 * np.pi * 0.7 * t + self.rng.uniform(0, 6))
        amp = env_gate(t, 0.012 if vel > 0.9 else 0.02, gate, rel)
        if fall:
            fs = smoothstep(gate - 0.04, gate + 0.22, t)
            p -= 5.0 * fs ** 1.6
            amp = env_gate(t, 0.012, gate + 0.2, 0.05) * (1 - 0.85 * fs)
        if dur > 0.35:
            amp *= 1 + 0.12 * smoothstep(0.1, dur, t)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        hi = f0.mean() > 700
        def base(k):
            return (1.0 / k) if k % 2 else (0.22 if hi else 0.09) / k
        bright = (1.6 + 4.2 * vel * amp + 2.5 * np.exp(-t / 0.03) * vel) * bright_mul
        tone = _harm_sum(ph, f0.max(), base, bright)
        br = bp(self.noise(N), 2400, 0.7) * 0.06 * vel * amp + hp(self.noise(N), 3000) * 0.05 * np.exp(-t / 0.012) * vel
        out = (tone + br) * amp * vel
        return out

    # ---- brass voice: saw-like additive with amplitude-linked brightness ("blat"), lip rise, falls
    def brass_voice(self, n, dur, vel=0.85, fall=False, kind='tpt', doit=False, sfz=True, rel=0.06):
        gate = max(dur, 0.04)
        N = int((gate + rel * 6 + (0.3 if fall else 0)) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n)) + self.rng.normal(0, 0.05)
        p -= 0.8 * np.exp(-t / 0.018)
        amp = env_gate(t, 0.01, gate, rel)
        if sfz:
            amp *= 0.62 + 0.38 * np.exp(-t / 0.11)
        if fall:
            fs = smoothstep(gate - 0.02, gate + 0.28, t)
            p -= 7.0 * fs ** 1.5
            amp = env_gate(t, 0.01, gate + 0.26, 0.05) * (1 - 0.9 * fs) * (0.62 + 0.38 * np.exp(-t / 0.11))
        if doit:
            p += 4.0 * smoothstep(gate - 0.05, gate + 0.18, t) ** 2
        if dur > 0.5:
            p += 0.1 * smoothstep(0.25, 0.6, t) * np.sin(2 * np.pi * 5.6 * t)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        k_bright = {'tpt': 11.0, 'tbn': 7.0, 'sax': 6.0, 'mute': 14.0, 'tuba': 3.5}[kind]
        bright = 1.0 + k_bright * vel * amp ** 1.6 + 5 * vel * np.exp(-t / 0.025)
        if kind == 'sax':
            base = lambda k: (1.0 / k) * (1.0 if k % 2 else 0.6)
        elif kind == 'mute':
            base = lambda k: (1.0 / k) * (0.25 if k < 3 else 1.0)
        else:
            base = lambda k: 1.0 / k
        out = _harm_sum(ph, f0.max(), base, bright) * amp * vel
        if kind == 'mute':  # harmon-mute: hollow & nasal
            out = (bp(out, 1700, 1.1) * 2.2 + 0.25 * out) * 0.85
        if kind in ('tpt', 'tbn'):
            out += bp(self.noise(N), 1500, 1.5) * 0.02 * amp * vel
        return out

    # ---- Karplus-Strong core (block vectorised) + pitch-exact resampling
    def ks(self, f, N, t60=1.0, bright=0.6, exc_len=None, exc=None):
        P = SR / f
        L = max(int(P - 0.5), 2)
        Pa = L + 0.5
        ratio = (SR / Pa) / f            # >1 -> loop pitched too high -> read slower
        Nr = int(N / ratio) + L + 4
        rho = 10 ** (-3.0 * Pa / (max(t60, 0.02) * SR))
        x = np.zeros(Nr)
        if exc is None:
            e = self.noise(L)
            a = 1 - bright
            e = lfilter([1 - a], [1, -a], e)
            e -= e.mean()
            x[:L] = e
        else:
            x[:len(exc)] = exc[:Nr]
        y = np.zeros(Nr + L + 1)
        s = L + 1
        for b0 in range(0, Nr, L):
            e1 = min(b0 + L, Nr)
            y[s + b0:s + e1] = x[b0:e1] + rho * 0.5 * (y[s + b0 - L:s + e1 - L] + y[s + b0 - L - 1:s + e1 - L - 1])
        y = y[s:]
        idx = np.arange(N) / ratio
        return np.interp(idx, np.arange(len(y)), y)

    def pluck(self, n, dur, vel=0.8, t60=0.9, bright=0.75, mute=0.0, body=True):
        """Funky plucked instrument (banjo/guitar hybrid)."""
        f = mtof(n)
        gate = max(dur, 0.06)
        N = int((gate + 0.25) * SR)
        t = np.arange(N) / SR
        y = self.ks(f, N, t60=t60 * (1 - 0.6 * mute), bright=bright * (0.55 + 0.45 * vel))
        y += 0.5 * self.ks(f * 1.0015, N, t60=t60 * 0.8, bright=bright * 0.8)
        y *= np.where(t > gate, np.exp(-(t - gate) / 0.03), 1.0)
        y *= 1 - np.exp(-t / 0.0007)
        if body:
            y = y + 0.6 * filt(y, 'peak', 1800, 1.2, 5) - 0.3 * lp(y, 200)
        return y * vel

    def harpsichord(self, n, dur, vel=0.8):
        f = mtof(n)
        N = int((max(dur, 0.1) + 0.6) * SR)
        t = np.arange(N) / SR
        y = self.ks(f, N, t60=1.6, bright=0.97) + 0.55 * self.ks(f * 2.002, N, t60=1.2, bright=0.95)
        y = hp(y, 180)
        y *= np.where(t > dur, np.exp(-(t - dur) / 0.12), 1.0)
        return y * vel * 0.8

    def pizz(self, n, dur, vel=0.8):
        f = mtof(n)
        N = int(0.6 * SR)
        y = self.ks(f, N, t60=0.35, bright=0.45)
        y = filt(y, 'peak', 450, 1.0, 4)
        return y * vel

    def sitar(self, n, dur, vel=0.8):
        """Buzzy pluck: KS + waveshaped 'jawari' buzz, for mysterious sections."""
        f = mtof(n)
        N = int((max(dur, 0.1) + 0.8) * SR)
        y = self.ks(f, N, t60=1.6, bright=0.9)
        buzz = np.tanh(6 * y) - np.tanh(2 * y)
        y = y + 0.4 * hp(buzz, 1500)
        t = np.arange(N) / SR
        p = 1 + 0.004 * smoothstep(0.1, 0.5, t) * np.sin(2 * np.pi * 4 * t)
        return y * vel * 0.8

    def upright(self, n, dur, vel=0.8, dead=False, glide_from=None):
        """Upright bass: dark KS string + finger thump, damped at note-off."""
        f = mtof(n)
        gate = max(dur, 0.05)
        N = int((gate + 0.12) * SR)
        t = np.arange(N) / SR
        if dead:
            y = lp(self.noise(N), 500) * np.exp(-t / 0.02) * 0.6
            y += np.sin(2 * np.pi * f * t) * np.exp(-t / 0.03) * 0.5
            return y * vel
        y = self.ks(f, N, t60=1.4, bright=0.22 + 0.25 * vel)
        y = y / (np.max(np.abs(y[:2000])) + 1e-9)
        ph = 2 * np.pi * np.cumsum(np.full(N, f) * (1 + 0.03 * np.exp(-t / 0.02))) / SR
        thump = (np.sin(ph) + 0.35 * np.sin(2 * ph)) * np.exp(-t / 0.18)
        y = 0.7 * y + 0.6 * thump + lp(self.noise(N), 900) * np.exp(-t / 0.006) * 0.4
        y *= np.where(t > gate, np.exp(-(t - gate) / 0.025), 1.0) * (1 - np.exp(-t / 0.002))
        return y * vel

    def synth_bass(self, n, dur, vel=0.8, glide_from=None, punch=1.0, growl=0.0):
        """Modern bass: clean sub + bouncy filter-enveloped saw layer."""
        gate = max(dur, 0.05)
        N = int((gate + 0.1) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n))
        if glide_from is not None:
            p += (glide_from - n) * np.exp(-t / 0.04)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        amp = env_gate(t, 0.003, gate, 0.025)
        sub = np.sin(ph) * amp
        bright = 1.5 + punch * 9 * np.exp(-t / 0.07) * vel + growl * (3 + 2 * np.sin(2 * np.pi * 6 * t))
        saw = _harm_sum(ph, f0.max(), lambda k: 1.0 / k, bright, fmax=6000) * amp
        y = 0.85 * sub + 0.45 * np.tanh(1.5 * saw)
        return y * vel

    def piano(self, n, dur, vel=0.7, strings_detune=1.2):
        """Vintage upright piano: inharmonic partials, per-partial decay, honky detune."""
        f0 = mtof(n)
        gate = max(dur, 0.05)
        N = int((gate + 0.25) * SR)
        t = np.arange(N) / SR
        B = 0.00025 * 2 ** ((n - 60) / 18)
        tau0 = 2.2 * 2 ** (-(n - 48) / 24)
        out = np.zeros(N)
        cents = strings_detune / 1200 * np.log(2)
        for k in range(1, 28):
            fk = k * f0 * np.sqrt(1 + B * k * k)
            if fk > 15000:
                break
            a = (1.0 / k ** 1.05) * np.exp(-(k - 1) / (2.5 + 9 * vel))
            tau = tau0 / (1 + 0.25 * k)
            e = np.exp(-t / tau) * (0.7 + 0.3 * np.exp(-t / 0.08))
            for sgn in (-1, 1):
                ph0 = self.rng.uniform(0, 6.28)
                out += 0.5 * a * e * np.sin(2 * np.pi * fk * np.exp(sgn * cents) * t + ph0)
        out += lp(self.noise(N), 2500) * np.exp(-t / 0.004) * 0.15 * vel
        out *= np.where(t > gate, np.exp(-(t - gate) / 0.07), 1.0) * (1 - np.exp(-t / 0.0008))
        return out * vel

    def mallet(self, n, dur, vel=0.8, kind='vibes'):
        f0 = mtof(n)
        table = {
            'vibes':    [(1, 1.0, 2.2), (3.93, 0.25, 0.7), (9.2, 0.07, 0.25)],
            'celesta':  [(1, 1.0, 1.3), (2.0, 0.3, 0.6), (3.0, 0.12, 0.3), (5.4, 0.05, 0.12)],
            'musicbox': [(1, 1.0, 1.6), (2.76, 0.35, 0.5), (5.4, 0.2, 0.18), (8.93, 0.08, 0.08)],
            'marimba':  [(1, 1.0, 0.55), (3.99, 0.35, 0.12), (9.86, 0.08, 0.04)],
            'kalimba':  [(1, 1.0, 0.9), (5.94, 0.2, 0.08), (2.0, 0.05, 0.3)],
            'glock':    [(1, 1.0, 1.5), (2.71, 0.4, 0.4), (5.1, 0.2, 0.15)],
        }[kind]
        L = max(p[2] for p in table)
        N = int(min(L * 2.5, 4.0) * SR)
        t = np.arange(N) / SR
        out = np.zeros(N)
        for r, a, tau in table:
            if r * f0 > 18000:
                continue
            out += a * np.sin(2 * np.pi * r * f0 * t + self.rng.uniform(0, 6)) * np.exp(-t / tau)
        if kind == 'vibes':
            out *= 1 - 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.5 * t))
        out *= 1 - np.exp(-t / 0.0006)
        out += hp(self.noise(N), 3000) * np.exp(-t / 0.002) * 0.2
        return out * vel

    def theremin(self, n, dur, vel=0.7, prev=None, glide=0.12):
        gate = dur
        N = int((gate + 0.3) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n))
        if prev is not None:
            p += (prev - n) * np.exp(-t / glide)
        p += 0.28 * smoothstep(0.05, 0.3, t) * np.sin(2 * np.pi * 6.2 * t)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        y = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
        y *= env_gate(t, 0.06, gate, 0.12)
        return y * vel

    def saw_blade(self, n, dur, vel=0.7, prev=None):
        """Bowed musical saw: pure sine, slow wide vibrato, swelling."""
        N = int((dur + 0.4) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n))
        if prev is not None:
            p += (prev - n) * np.exp(-t / 0.2)
        p += 0.35 * np.sin(2 * np.pi * 4.6 * t) * smoothstep(0, 0.4, t)
        ph = 2 * np.pi * np.cumsum(mtof(p)) / SR
        y = np.sin(ph) + 0.06 * np.sin(3 * ph)
        y *= env_gate(t, dur * 0.45, dur, 0.2)
        return y * vel

    # ---- formant "vocal" chops (nonverbal: ah / oh / hey / ooh / scat syllables)
    VOW = {
        'a': [(800, 90, 1.0), (1150, 100, 0.5), (2900, 140, 0.25), (3900, 160, 0.1)],
        'o': [(450, 70, 1.0), (800, 80, 0.55), (2830, 120, 0.1), (3800, 150, 0.05)],
        'e': [(400, 60, 1.0), (2050, 110, 0.42), (2600, 130, 0.3), (3500, 160, 0.1)],
        'i': [(290, 60, 1.0), (2300, 110, 0.3), (3000, 130, 0.25), (3700, 160, 0.1)],
        'u': [(330, 55, 1.0), (720, 70, 0.3), (2530, 110, 0.05), (3500, 150, 0.03)],
        'E': [(560, 70, 1.0), (1800, 100, 0.5), (2500, 130, 0.3), (3500, 160, 0.1)],
    }

    def vox(self, n, dur, vel=0.8, vowels='a', cons=None, slide=0.0, scoop=0.4, shift=1.12, vib=1.0):
        gate = max(dur, 0.04)
        N = int((gate + 0.3) * SR)
        t = np.arange(N) / SR
        p = np.full(N, float(n)) - scoop * np.exp(-t / 0.04)
        p += slide * smoothstep(0.02, gate, t)
        p += 0.15 * vib * smoothstep(0.15, 0.35, t) * np.sin(2 * np.pi * 5.6 * t)
        f0 = mtof(p)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        nv = len(vowels)
        u = np.clip(t / gate, 0, 1) * (nv - 1)
        i0 = np.minimum(np.floor(u).astype(int), nv - 1)
        i1 = np.minimum(i0 + 1, nv - 1)
        fr = u - i0
        tab = np.array([self.VOW[v] for v in vowels])  # (nv,4,3)
        F = (tab[i0, :, 0] * (1 - fr[:, None]) + tab[i1, :, 0] * fr[:, None]) * shift
        BW = tab[i0, :, 1] * (1 - fr[:, None]) + tab[i1, :, 1] * fr[:, None]
        A = tab[i0, :, 2] * (1 - fr[:, None]) + tab[i1, :, 2] * fr[:, None]
        out = np.zeros(N)
        for k in range(1, 60):
            if k * f0.max() > 9000:
                break
            fk = k * f0
            g = np.sum(A / (1 + ((fk[:, None] - F) / BW) ** 2), axis=1)
            out += g * np.sin(k * ph) / k ** 0.5
        att = 0.03 if cons == 'h' else 0.006
        amp = env_gate(t, att, gate, 0.05)
        out *= amp
        nz = self.noise(N)
        if cons == 'h':
            out += bp(nz, 1600, 0.6) * np.exp(-t / 0.03) * 0.35
        elif cons in ('b', 'd'):
            out += (hp(nz, 3500) if cons == 'd' else lp(nz, 600)) * np.exp(-t / 0.004) * 0.6
        out += bp(nz, 3000, 0.7) * amp * 0.03
        return out * vel

    # ------------------------------------------------------------- drums & perc
    def kick(self, vel=1.0, decay=0.30, f_end=46.0, f_start=230.0, click=1.0, drive=2.4):
        N = int(0.62 * SR)
        t = np.arange(N) / SR
        f = f_end + (f_start - f_end) * np.exp(-t / 0.020) + 28 * np.exp(-t / 0.10)
        ph = 2 * np.pi * np.cumsum(f) / SR
        body = np.sin(ph) * np.exp(-t / decay) * (1 - np.exp(-t / 0.0006))
        body *= np.where(t > decay * 1.6, np.exp(-(t - decay * 1.6) / 0.05), 1)
        cl = hp(self.noise(N), 3000) * np.exp(-t / 0.0022) * 0.5 + np.sin(2 * np.pi * 1600 * t) * np.exp(-t / 0.003) * 0.35
        y = np.tanh(drive * body) / np.tanh(drive) + click * cl
        return y * vel

    def clap(self, vel=1.0, tail=0.11, tone=1250):
        N = int(0.5 * SR)
        t = np.arange(N) / SR
        e = np.zeros(N)
        for i, off in enumerate((0.0, 0.0085, 0.0172, 0.026)):
            e += (t >= off) * np.exp(-np.maximum(t - off, 0) / 0.0045) * (0.75 if i < 3 else 1.0)
        e += (t >= 0.026) * np.exp(-np.maximum(t - 0.026, 0) / tail) * 0.5
        nz = self.noise(N)
        y = bp(nz, tone, 0.9) * 2.4 + bp(nz, tone * 2.1, 1.2) * 0.9
        return hp(y * e, 350) * vel

    def snare(self, vel=1.0, tone=190, snap=1.0, decay=0.14):
        N = int(0.45 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(tone * (1 + 0.5 * np.exp(-t / 0.01))) / SR
        body = (np.sin(ph) + 0.4 * np.sin(1.7 * ph)) * np.exp(-t / 0.07)
        nz = hp(self.noise(N), 1500) * np.exp(-t / decay) * snap
        y = 0.6 * body + 0.8 * nz
        return y * vel * (1 - np.exp(-t / 0.0005))

    def hat(self, vel=1.0, decay=0.035, open_=False):
        if open_:
            decay = 0.22
        N = int((decay * 7 + 0.01) * SR)
        t = np.arange(N) / SR
        metal = np.zeros(N)
        for fr in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0):
            metal += np.sign(np.sin(2 * np.pi * fr * 1.73 * t + self.rng.uniform(0, 6)))
        y = 0.5 * hp(metal, 7200, 1.0) + 0.6 * hp(self.noise(N), 8500)
        y *= np.exp(-t / decay) * (1 - np.exp(-t / 0.0004))
        return y * vel

    def shaker(self, vel=1.0):
        N = int(0.12 * SR)
        t = np.arange(N) / SR
        e = (1 - np.exp(-t / 0.008)) * np.exp(-t / 0.035)
        return bp(self.noise(N), 6500, 0.8) * e * vel * 1.4

    def tamb(self, vel=1.0):
        N = int(0.3 * SR)
        t = np.arange(N) / SR
        e = np.exp(-t / 0.06) * (1 + 0.6 * np.sin(2 * np.pi * 42 * t) ** 2)
        jing = hp(self.noise(N), 6500) * e
        jing += 0.3 * bp(self.noise(N), 9800, 3) * np.exp(-t / 0.1)
        return jing * vel

    def rim(self, vel=1.0):
        N = int(0.1 * SR)
        t = np.arange(N) / SR
        y = np.sin(2 * np.pi * 1750 * t) * np.exp(-t / 0.010) + 0.6 * np.sin(2 * np.pi * 520 * t) * np.exp(-t / 0.015)
        y += hp(self.noise(N), 2000) * np.exp(-t / 0.002)
        return y * vel * 0.8

    def wood(self, vel=1.0, f=900.0):
        N = int(0.15 * SR)
        t = np.arange(N) / SR
        y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.03) + 0.4 * np.sin(2 * np.pi * f * 2.63 * t) * np.exp(-t / 0.012)
        return y * vel * (1 - np.exp(-t / 0.0003))

    def snap(self, vel=1.0):
        N = int(0.15 * SR)
        t = np.arange(N) / SR
        y = bp(self.noise(N), 2300, 1.6) * np.exp(-t / 0.011) * 2.5 + hp(self.noise(N), 4000) * np.exp(-t / 0.002)
        return y * vel

    def crash(self, vel=1.0, decay=1.4):
        N = int(decay * 4 * SR)
        t = np.arange(N) / SR
        metal = np.zeros(N)
        for fr in (342, 521, 787, 1013, 1323, 1697, 2033):
            metal += np.sin(2 * np.pi * fr * t + self.rng.uniform(0, 6) + 3 * np.sin(2 * np.pi * fr * 1.41 * t))
        y = hp(self.noise(N), 4000) * 0.8 + hp(metal, 3000) * 0.15
        y *= np.exp(-t / decay) * (1 - np.exp(-t / 0.001))
        return y * vel

    def timpani(self, n, vel=1.0):
        f = mtof(n)
        N = int(1.6 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.04 * np.exp(-t / 0.05)) * np.ones(N)) / SR
        y = np.sin(ph) * np.exp(-t / 0.7) + 0.5 * np.sin(1.5 * ph) * np.exp(-t / 0.35) + 0.25 * np.sin(1.99 * ph) * np.exp(-t / 0.3)
        y += lp(self.noise(N), 1200) * np.exp(-t / 0.02) * 0.5
        return y * vel

    def bongo(self, vel=1.0, f=420.0):
        N = int(0.25 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(f * (1 + 0.25 * np.exp(-t / 0.008))) / SR
        y = np.sin(ph) * np.exp(-t / 0.07) + hp(self.noise(N), 2000) * np.exp(-t / 0.002) * 0.4
        return y * vel

    def castanet(self, vel=1.0):
        N = int(0.06 * SR)
        t = np.arange(N) / SR
        y = bp(self.noise(N), 3200, 3) * np.exp(-t / 0.006) * 3 + np.sin(2 * np.pi * 2100 * t) * np.exp(-t / 0.008)
        return y * vel

    def tick(self, vel=1.0, tock=False):
        f = 2600 if not tock else 1900
        N = int(0.05 * SR)
        t = np.arange(N) / SR
        y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.004) + hp(self.noise(N), 5000) * np.exp(-t / 0.001)
        return y * vel

    def bell(self, n, vel=1.0, ring=12.0, dur=0.6):
        """Alarm-clock bell: fast hammer tremolo on an inharmonic bell."""
        f = mtof(n)
        N = int((dur + 0.6) * SR)
        t = np.arange(N) / SR
        y = np.zeros(N)
        for r, a in ((1, 1), (2.32, 0.5), (4.25, 0.3), (6.63, 0.15)):
            y += a * np.sin(2 * np.pi * f * r * t)
        trem = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * ring * t))
        hammer = lfilter([1], [1, -0.995], trem * 0.01)
        e = np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.15)) * (0.6 + 0.4 * trem)
        return y * e * vel * 0.5

    # ---------------------------------------------------------------------- FX
    def riser(self, dur, vel=1.0, f0=300, f1=9000):
        N = int(dur * SR)
        t = np.arange(N) / SR
        nz = self.noise(N)
        y = tv_filter(nz, 'bp', lambda s: f0 * (f1 / f0) ** min(s / dur, 1), q=2.0)
        y *= smoothstep(0, dur, t) ** 2
        ph = 2 * np.pi * np.cumsum(mtof(60 + 24 * (t / dur) ** 2)) / SR
        y += 0.12 * np.sin(ph) * smoothstep(0, dur, t)
        return y * vel

    def impact(self, vel=1.0):
        N = int(2.0 * SR)
        t = np.arange(N) / SR
        ph = 2 * np.pi * np.cumsum(38 + 60 * np.exp(-t / 0.08)) / SR
        y = np.sin(ph) * np.exp(-t / 0.6)
        y += lp(self.noise(N), 400) * np.exp(-t / 0.15) * 0.3
        return np.tanh(1.5 * y) * vel

    def boing(self, n=nn('C3'), vel=1.0, dur=0.45):
        N = int(dur * SR)
        t = np.arange(N) / SR
        p = n + 14 * (1 - np.exp(-t / 0.08)) + 1.5 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.2)
        ph = 2 * np.pi * np.cumsum(mtof(p)) / SR
        y = (np.sin(ph) + 0.3 * np.sin(2 * ph + 0.5 * np.sin(ph))) * np.exp(-t / 0.18)
        return y * vel

    def swoosh(self, dur=0.5, vel=1.0, up=True):
        N = int(dur * SR)
        t = np.arange(N) / SR
        fc = (lambda s: 400 * (20 ** (s / dur))) if up else (lambda s: 8000 * (0.05 ** (s / dur)))
        y = tv_filter(self.noise(N), 'bp', fc, q=1.5) * np.sin(np.pi * t / dur) ** 2
        return y * vel

    def crackle(self, N, density=8.0, vel=1.0):
        y = np.zeros(N)
        k = int(N / SR * density)
        pos = self.rng.integers(0, N - 50, k)
        amp = self.rng.exponential(1.0, k)
        y[pos] = amp * self.rng.choice([-1, 1], k)
        y = hp(y, 1200) + 0.01 * bp(self.noise(N), 3000, 0.5)
        return y * vel


# ----------------------------------------------------------------------- mixer
def pan_gains(pan):
    a = (pan + 1) * np.pi / 4
    return np.cos(a) * np.sqrt(2), np.sin(a) * np.sqrt(2)


def make_ir(t60=1.5, predelay=0.018, damp=0.45, seed=3, er=True):
    rng = np.random.default_rng(seed)
    n = int(t60 * 1.3 * SR)
    t = np.arange(n) / SR
    ir = np.zeros((2, n + int(predelay * SR)))
    for ch in range(2):
        nz = rng.standard_normal(n)
        lo = lp(nz, 2500)
        hi = nz - lo
        r = lo * np.exp(-6.9 * t / t60) + hi * np.exp(-6.9 * t / (t60 * damp))
        r *= 1 - np.exp(-t / 0.006)
        if er:
            for _ in range(10):
                d = int(rng.uniform(0.003, 0.05) * SR)
                r[d] += rng.uniform(-1, 1) * 6
        ir[ch, int(predelay * SR):] = r
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


_IR_CACHE = {}


def reverb(x, t60=1.5, predelay=0.018, damp=0.45, lo_cut=250, hi_cut=9000):
    key = (t60, predelay, damp)
    if key not in _IR_CACHE:
        _IR_CACHE[key] = make_ir(t60, predelay, damp)
    ir = _IR_CACHE[key]
    x = hp(lp(x, hi_cut), lo_cut)
    y = np.stack([fftconvolve(x[0], ir[0])[:x.shape[1]], fftconvolve(x[1], ir[1])[:x.shape[1]]])
    return y


def pingpong(x, delay_s, fb=0.4, taps=5, hi_cut=4500, lo_cut=400):
    d = int(delay_s * SR)
    src = hp(lp(x.mean(axis=0), hi_cut), lo_cut)
    y = np.zeros_like(x)
    g = 1.0
    for k in range(1, taps + 1):
        g *= fb
        ch = (k - 1) % 2
        s = np.zeros(x.shape[1])
        s[k * d:] = src[:-k * d] if k * d < len(src) else 0
        y[ch] += g * s
        src = lp(src, hi_cut * 0.85)
    return y


def sidechain_curve(N, kick_times, depth=0.6, rel=0.14, att=0.004):
    g = np.ones(N)
    L = int(rel * 5 * SR)
    tt = np.arange(L) / SR
    for kt in kick_times:
        i = int(kt * SR)
        if i >= N:
            continue
        j = min(N, i + L)
        # smooth pre-dip so it doesn't click: interpolate down within 'att'
        g[i:j] = np.minimum(g[i:j], 1 - depth * np.exp(-np.maximum(tt[:j - i] - att, 0) / rel) *
                            np.clip(tt[:j - i] / att, 0, 1))
    return g


def glue_comp(x, thresh_db=-14, ratio=2.0, att=0.01, rel=0.15, dec=32):
    mono = np.max(np.abs(x), axis=0)
    blocks = len(mono) // dec
    m = mono[:blocks * dec].reshape(blocks, dec).max(axis=1)
    sr2 = SR / dec
    a_att = np.exp(-1 / (att * sr2)); a_rel = np.exp(-1 / (rel * sr2))
    env = np.zeros(blocks)
    e = 0.0
    for i in range(blocks):
        v = m[i]
        e = a_att * e + (1 - a_att) * v if v > e else a_rel * e + (1 - a_rel) * v
        env[i] = e
    lev = 20 * np.log10(np.maximum(env, 1e-6))
    over = np.maximum(lev - thresh_db, 0)
    gdb = -over * (1 - 1 / ratio)
    g = 10 ** (gdb / 20)
    gf = np.interp(np.arange(x.shape[1]), np.arange(blocks) * dec + dec / 2, g)
    return x * gf


def limiter(x, ceiling=0.891, look=0.003, rel=0.08, dec=8):
    a = np.max(np.abs(x), axis=0)
    L = int(look * SR)
    pk = maximum_filter1d(a, size=2 * L + 1)
    g = np.minimum(1.0, ceiling / np.maximum(pk, 1e-9))
    blocks = len(g) // dec
    gb = g[:blocks * dec].reshape(blocks, dec).min(axis=1)
    ar = np.exp(-1 / (rel * SR / dec))
    out = np.empty(blocks)
    cur = 1.0
    for i in range(blocks):
        v = gb[i]
        cur = v if v < cur else ar * cur + (1 - ar) * v
        out[i] = cur
    gf = np.interp(np.arange(len(g)), np.arange(blocks) * dec + dec / 2, out)
    gf = np.minimum(gf, minimum_filter1d(g, size=2 * L + 1))
    gf = uniform_filter1d(gf, size=max(L // 2, 1))
    y = x * gf
    return np.clip(y, -0.98, 0.98)


def lufs(x):
    y = filt(x, 'hs', 1681.97, 0.7072, 3.9998)
    y = filt(y, 'hp', 38.135, 0.5003)
    blk = int(0.4 * SR); hop = int(0.1 * SR)
    ms = []
    for i in range(0, y.shape[1] - blk, hop):
        ms.append(np.sum(np.mean(y[:, i:i + blk] ** 2, axis=1)))
    ms = np.array(ms)
    l = -0.691 + 10 * np.log10(ms + 1e-12)
    ms = ms[l > -70]
    rel = -0.691 + 10 * np.log10(ms.mean()) - 10
    l = -0.691 + 10 * np.log10(ms + 1e-12)
    return -0.691 + 10 * np.log10(ms[l > rel].mean())


class Song:
    """Holds buses, timing helpers and accent cues for one track."""

    def __init__(self, title, seed=1):
        self.title = title
        self.N = int((DUR + TAIL) * SR)
        self.buses = defaultdict(lambda: np.zeros((2, self.N)))
        self.kicks = []
        self.cues = []
        self.I = Inst(seed)
        self.rng = np.random.default_rng(seed + 100)

    # time
    def t(self, beat, s8=0.5, s16=0.5):
        return float(warp(beat, s8, s16)) * SPB

    def place(self, bus, sig, tsec, pan=0.0, gain=1.0):
        i = int(round(tsec * SR))
        B = self.buses[bus]
        nf = min(256, sig.shape[-1] // 4)
        if nf > 1:
            sig = sig.copy()
            sig[..., -nf:] *= np.linspace(1, 0, nf)
        if sig.ndim == 1:
            gl, gr = pan_gains(pan)
            sig = np.stack([sig * gl, sig * gr])
        if i < 0:
            sig = sig[:, -i:]; i = 0
        n = min(sig.shape[1], self.N - i)
        if n <= 0:
            return
        B[:, i:i + n] += sig[:, :n] * gain

    def cue(self, beat, label, kind='accent', tsec=None):
        self.cues.append(dict(beat=round(beat, 3), time=round(beat * SPB if tsec is None else tsec, 3), label=label, kind=kind))

    # -------- players
    def lead(self, ev, inst='clarinet', bus='lead', pan=0.0, gain=1.0, s8=0.5, s16=0.5, hum=0.004, **kw):
        prev = None
        prev_end = -10
        for e in ev:
            tt = self.t(e['t'], s8, s16) + self.rng.normal(0, hum)
            dsec = self.t(e['t'] + e['d'], s8, s16) - self.t(e['t'], s8, s16)
            v = e['v'] * (1 + self.rng.normal(0, 0.04))
            if inst == 'clarinet':
                legato = e['gl'] or (abs(e['t'] - prev_end) < 1e-6 and e['d'] >= 0.5)
                y = self.I.clarinet(e['n'], dsec, v, prev=prev, glide=e['gl'], grace=e['gr'],
                                    fall=e['fall'], scoop=e['scoop'], stac=e['stac'], ten=e['ten'], **kw)
            elif inst in ('tpt', 'tbn', 'sax', 'mute', 'tuba'):
                y = self.I.brass_voice(e['n'], dsec * (0.55 if e['stac'] else 0.92), v, fall=e['fall'], kind=inst,
                                       doit=e['scoop'], **kw)
            elif inst == 'pluck':
                y = self.I.pluck(e['n'], dsec * (0.5 if e['stac'] else 0.85), v, **kw)
            elif inst == 'harpsichord':
                y = self.I.harpsichord(e['n'], dsec, v)
            elif inst == 'pizz':
                y = self.I.pizz(e['n'], dsec, v)
            elif inst == 'sitar':
                y = self.I.sitar(e['n'], dsec, v)
            elif inst == 'piano':
                y = self.I.piano(e['n'], dsec * 0.9, v)
            elif inst in ('vibes', 'celesta', 'musicbox', 'marimba', 'kalimba', 'glock'):
                y = self.I.mallet(e['n'], dsec, v, kind=inst)
            elif inst == 'theremin':
                y = self.I.theremin(e['n'], dsec, v, prev=prev)
            elif inst == 'saw':
                y = self.I.saw_blade(e['n'], dsec, v, prev=prev)
            else:
                raise ValueError(inst)
            self.place(bus, y, tt, pan, gain)
            prev = e['n']
            prev_end = e['t'] + e['d']

    def section(self, ev, voices, scale, inst='tpt', bus='brass', gain=1.0, s8=0.5, s16=0.5, spread=0.7, octave_double=False):
        """Harmonised horn section. voices = list of diatonic offsets (0=melody, -2=third below, -4=fifth below...)."""
        sc = sorted(set(p % 12 for p in scale))
        def shift(n, steps):
            if steps == 0:
                return n
            pcs = []
            for o in range(-3, 4):
                pcs += [p + 12 * (n // 12 + o) for p in sc]
            pcs = sorted(pcs)
            # nearest scale degree at/below n
            idx = max(i for i, p in enumerate(pcs) if p <= n)
            return pcs[idx + steps]
        nv = len(voices)
        for vi, st in enumerate(voices):
            pan = (vi - (nv - 1) / 2) / max((nv - 1) / 2, 1) * spread
            ev2 = [dict(e, n=shift(e['n'], st), gr=(e['gr'] if st == 0 else None)) for e in ev]
            kind = inst if (vi < 2 or inst != 'tpt') else ('tbn' if vi >= 2 else 'tpt')
            self.lead(ev2, inst=kind, bus=bus, pan=pan, gain=gain * (1.0 if vi == 0 else 0.7), s8=s8, s16=s16, hum=0.006)
            if octave_double and vi == 0:
                ev3 = [dict(e, n=e['n'] - 12) for e in ev]
                self.lead(ev3, inst='tbn', bus=bus, pan=-pan * 0.5, gain=gain * 0.5, s8=s8, s16=s16, hum=0.006)

    def stabs(self, pattern, sym, start, low=nn('F4'), bus='brass', gain=1.0, length=0.2, fall_last=False,
              s8=0.5, s16=0.5, kinds=('tpt', 'tpt', 'sax', 'tbn'), cue=True):
        """Brass section chord stabs on a 16-step pattern."""
        notes = voicing(sym, low)
        hs = hits(pattern, start)
        for j, (b, v) in enumerate(hs):
            tt = self.t(b, s8, s16)
            fall = fall_last and j == len(hs) - 1
            for vi, n in enumerate(sorted(notes, reverse=True)):
                kind = kinds[min(vi, len(kinds) - 1)]
                pan = [-0.55, 0.55, -0.25, 0.25, 0.0][vi % 5]
                y = self.I.brass_voice(n, length * (2.5 if fall else 1.0), v * 0.85, fall=fall, kind=kind)
                self.place(bus, y, tt + self.rng.uniform(0, 0.009), pan, gain / np.sqrt(len(notes)))
            # bass trombone root
            r = bass_root(sym, nn('E2'))
            y = self.I.brass_voice(r, length, v * 0.8, kind='tbn', fall=fall)
            self.place(bus, y, tt + 0.004, 0.0, gain * 0.35)
            if cue and v >= 0.8:
                self.cue(b, f'brass stab ({sym})', tsec=tt)

    def comp(self, pattern, sym, start, inst='piano', low=nn('G3'), bus='keys', gain=1.0, length=0.15, s8=0.5, s16=0.5, pan=0.0, n=None):
        notes = voicing(sym, low, n)
        for b, v in hits(pattern, start):
            tt = self.t(b, s8, s16)
            for k, nt in enumerate(notes):
                if inst == 'piano':
                    y = self.I.piano(nt, length, v * 0.7)
                elif inst == 'pluck':
                    y = self.I.pluck(nt, length, v * 0.7, t60=0.5, mute=0.5)
                elif inst == 'harpsichord':
                    y = self.I.harpsichord(nt, length, v * 0.7)
                elif inst == 'vibes':
                    y = self.I.mallet(nt, length, v * 0.6, 'vibes')
                self.place(bus, y, tt + k * 0.004, pan, gain / np.sqrt(len(notes)))

    def bassline(self, ev, chords, upright=0.7, synth=0.7, s8=0.5, s16=0.5, low=nn('E1'), oct_up=12, punch=1.0, growl=0.0):
        """ev: rseq events; chords: list of (beat, sym). Layered upright + synth bass."""
        cb = sorted(chords)
        prev = None
        for e in ev:
            sym = [c for c in cb if c[0] <= e['t'] + 1e-6][-1][1]
            n = bass_root(sym, low) + e['s'] + oct_up
            tt = self.t(e['t'], s8, s16) + self.rng.normal(0, 0.002)
            dsec = (self.t(e['t'] + e['d'], s8, s16) - self.t(e['t'], s8, s16)) * (0.5 if e['stac'] else 0.9)
            v = e['v']
            if upright:
                y = self.I.upright(n, dsec, v, dead=e['dead'])
                self.place('bass', y, tt, 0.0, upright)
            if synth and not e['dead']:
                y = self.I.synth_bass(n - 12 if n >= nn('E2') + 7 else n, dsec, v,
                                      glide_from=(prev - 12 if (e['gl'] and prev) else None), punch=punch, growl=growl)
                self.place('sub', y, tt, 0.0, synth)
            prev = n

    def drum(self, pattern, start, voice, bus='drums', gain=1.0, pan=0.0, s8=0.5, s16=0.5, **kw):
        for b, v in hits(pattern, start):
            tt = self.t(b, s8, s16) + self.rng.normal(0, 0.0015)
            vv = v * (1 + self.rng.normal(0, 0.05))
            if voice == 'kick':
                y = self.I.kick(vv, **kw)
                self.kicks.append(tt)
                self.place('kick', y, tt, 0.0, gain)
                continue
            y = getattr(self.I, voice)(vv, **kw)
            self.place(bus, y, tt, pan, gain)

    def vchop(self, items, start, bus='vox', gain=1.0, s8=0.5, s16=0.5, pan=0.0, **kw):
        """items: list of (step16, note, dur16, vowels, cons)."""
        for step, note, d16, vw, cons in items:
            b = start + step / 4.0
            tt = self.t(b, s8, s16)
            dsec = d16 / 4.0 * SPB
            y = self.I.vox(nn(note) if isinstance(note, str) else note, dsec, 0.85, vowels=vw, cons=cons, **kw)
            self.place(bus, y, tt, pan, gain)

    # -------- mixdown
    def mixdown(self, cfg, tape_stop=None, target_lufs=-10.0, automation=None):
        N = self.N
        sc = sidechain_curve(N, self.kicks, depth=1.0)  # unit curve, scale per bus
        out = np.zeros((2, N))
        rv_send = np.zeros((2, N)); rv2_send = np.zeros((2, N)); dl_send = np.zeros((2, N))
        post = None
        for name, B in self.buses.items():
            c = cfg.get(name, {})
            x = B
            for eq in c.get('eq', []):
                x = filt(x, *eq)
            if c.get('drive'):
                d = c['drive']
                x = np.tanh(d * x) / d
            if c.get('haas'):
                d = int(c['haas'] * SR)
                side = np.zeros_like(x[1]); side[d:] = x[1][:-d]
                x = np.stack([x[0] * 1.0, 0.45 * x[1] + 0.75 * side])
            if c.get('width'):
                m = x.mean(axis=0); s = (x[0] - x[1]) / 2 * c['width']
                x = np.stack([m + s, m - s])
            x = x * c.get('gain', 1.0)
            depth = c.get('sc', 0.0)
            if depth:
                x = x * (1 - depth * (1 - sc))
            if name == 'post':
                post = x
                continue
            out += x
            rv_send += x * c.get('rv', 0.0)
            rv2_send += x * c.get('rv2', 0.0)
            dl_send += x * c.get('dl', 0.0)
        wet = reverb(rv_send, t60=1.6, predelay=0.02, damp=0.45) * 1.3
        wet2 = reverb(rv2_send, t60=0.55, predelay=0.008, damp=0.6, lo_cut=200)
        dl = pingpong(dl_send, SPB * 0.75, fb=0.42, taps=6)
        rsc = 1 - 0.55 * (1 - sc)
        out += (wet * 0.9 + wet2 * 0.8) * rsc + dl * 0.9 * rsc
        if automation:
            pts = sorted(automation)
            gcurve = np.ones(N)
            for (bt, gdb), nxt in zip(pts, pts[1:] + [(1e9, None)]):
                i0 = int(bt * SPB * SR); i1 = min(N, int(nxt[0] * SPB * SR)) if nxt[0] < 1e9 else N
                gcurve[i0:i1] = 10 ** (gdb / 20)
            gcurve = uniform_filter1d(gcurve, int(0.03 * SR))
            out = out * gcurve
        if tape_stop:
            t0, length, until = tape_stop
            out = apply_tape_stop(out, t0, length, until)
        if post is not None:
            out += post + reverb(post * 0.3, t60=1.6) * 0.8
        # loop wrap: fold the tail past 65 s onto the start
        L = int(DUR * SR)
        tail = out[:, L:]
        out = out[:, :L].copy()
        out[:, :tail.shape[1]] += tail
        # master chain on a circularly padded copy so the loop seam stays continuous
        pad = int(1.0 * SR)
        out = np.concatenate([out[:, -pad:], out, out[:, :pad]], axis=1)
        out = hp(out, 24, 0.6)
        out = filt(out, 'ls', 90, 0.7, 1.0)
        out = filt(out, 'peak', 3200, 0.7, 3.0)
        out = filt(out, 'lp', 17000, 0.7)
        out = glue_comp(out, thresh_db=-16, ratio=1.8, att=0.012, rel=0.18)
        out = np.tanh(out * 1.1) / 1.1
        g = 1.0
        for _ in range(4):
            y = limiter(out * g)
            L_now = lufs(y)
            g *= 10 ** ((target_lufs - L_now) / 20)
        y = limiter(out * g)[:, pad:-pad]
        return y, lufs(y)


def apply_tape_stop(x, t0, length, until):
    i0 = int(t0 * SR); n = int(length * SR); i2 = int(until * SR)
    tau = np.arange(n) / n
    rate = (1 - tau) ** 1.6
    pos = i0 + np.cumsum(rate)
    seg = np.stack([np.interp(pos, np.arange(x.shape[1]), x[c]) for c in range(2)])
    seg *= np.minimum(1, (1 - tau) * 4)
    seg = lp(seg, 6000)
    y = x.copy()
    y[:, i0:i0 + n] = seg
    y[:, i0 + n:i2] = 0
    return y


def write_wav24(path, x):
    import wave
    y = np.clip(x, -1, 1)
    q = (y.T.reshape(-1) * 8388607).astype('<i4')
    b = q.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR)
        w.writeframes(b)


# ---- per-instrument calibration so every voice leaves the factory at a sane level
_NORM = dict(kick=0.57, clap=0.33, snare=0.36, hat=0.66, shaker=0.7, tamb=0.38, rim=0.44, snap=0.46,
             castanet=0.44, bongo=0.63, crash=0.4, timpani=0.62, wood=0.78, tick=0.57,
             mute=0.85, pluck=0.6, upright=1.4, piano=3.0, pizz=1.5, harpsichord=0.6, vox=3.0,
             saw_blade=1.8, riser=0.7)
for _n, _g in _NORM.items():
    if _n == 'mute':
        continue
    _f = getattr(Inst, _n)
    def _w(self, *a, _f=_f, _g=_g, **k):
        return _f(self, *a, **k) * _g
    setattr(Inst, _n, _w)
