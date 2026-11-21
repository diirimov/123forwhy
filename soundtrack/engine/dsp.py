"""
DSP building blocks: band-limited oscillators, resonant filters, envelopes,
synth voices, drum synthesis, transition FX, convolution reverb, delay, sidechain.
All signals are float64 at SR. Mono = shape (n,), stereo = shape (2, n).
"""
import numpy as np
from numba import njit
from scipy.signal import oaconvolve, resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 48000
TWO_PI = 2 * np.pi


def hz(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


# ----------------------------------------------------------------------------- filters
@njit(cache=True)
def _svf(x, fc, res, mode, sr):
    """Zavalishin TPT state-variable filter with per-sample cutoff.
    mode 0 = lowpass, 1 = bandpass (unity peak), 2 = highpass."""
    n = x.shape[0]
    y = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 2.0 - 2.0 * res
    for i in range(n):
        f = fc[i]
        if f > sr * 0.45:
            f = sr * 0.45
        if f < 10.0:
            f = 10.0
        g = np.tan(np.pi * f / sr)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            y[i] = v2
        elif mode == 1:
            y[i] = v1 * k
        else:
            y[i] = x[i] - k * v1 - v2
    return y


def svf(x, fc, res=0.0, mode='lp', poles=2):
    x = np.ascontiguousarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([svf(c, fc, res, mode, poles) for c in x])
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape).copy()
    m = {'lp': 0, 'bp': 1, 'hp': 2}[mode]
    y = _svf(x, fc, float(res), m, float(SR))
    if poles == 4:
        y = _svf(y, fc, float(res) * 0.5, m, float(SR))
    return y


# ----------------------------------------------------------------------------- oscillators
def _phase(freq, n, phase0=0.0):
    inc = np.broadcast_to(np.asarray(freq, dtype=np.float64) / SR, (n,)).copy()
    ph = (phase0 + np.cumsum(inc) - inc) % 1.0
    return ph, inc


def _blep(t, dt):
    out = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    out[m] = x + x - x * x - 1.0
    m = t > 1.0 - dt
    x = (t[m] - 1.0) / dt[m]
    out[m] = x * x + x + x + 1.0
    return out


def saw(freq, n, phase0=0.0):
    t, dt = _phase(freq, n, phase0)
    return 2.0 * t - 1.0 - _blep(t, dt)


def square(freq, n, phase0=0.0):
    t, dt = _phase(freq, n, phase0)
    return np.where(t < 0.5, 1.0, -1.0) + _blep(t, dt) - _blep((t + 0.5) % 1.0, dt)


def sine(freq, n, phase0=0.0):
    t, _ = _phase(freq, n, phase0)
    return np.sin(TWO_PI * t)


# ----------------------------------------------------------------------------- envelopes / utils
def adsr(n_gate, a, d, s, r):
    A, D, R = max(1, int(a * SR)), max(1, int(d * SR)), max(8, int(r * SR))
    n_gate = max(n_gate, 1)
    t = np.arange(n_gate, dtype=np.float64)
    att = np.minimum(t / A, 1.0)
    dec = s + (1.0 - s) * np.exp(-np.maximum(t - A, 0.0) / (D / 4.0))
    env = np.where(t < A, att, dec)
    rel = env[-1] * np.exp(-np.arange(R) / (R / 5.0)) * np.linspace(1, 0, R)
    return np.concatenate([env, rel])


def pan(x, p):
    """equal-power pan, p in [-1, 1]"""
    th = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)]) * np.sqrt(2)


def soft(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-12))


class Track:
    def __init__(self, n):
        self.buf = np.zeros((2, n))

    def add(self, sig, start_s, gain=1.0):
        i0 = int(round(start_s * SR))
        if sig.ndim == 1:
            sig = np.stack([sig, sig])
        if i0 < 0:
            sig, i0 = sig[:, -i0:], 0
        n = min(sig.shape[1], self.buf.shape[1] - i0)
        if n > 0:
            self.buf[:, i0:i0 + n] += sig[:, :n] * gain


# ----------------------------------------------------------------------------- synth voices
def supersaw(freqs, n_gate, rng, voices=7, detune=0.16, cutoff=4000.0, attack=0.01,
             release=0.25, res=0.15, width=0.9, cutoff_env=None):
    """Chord of detuned saws -> stereo -> 4-pole lowpass."""
    env = adsr(n_gate, attack, 0.6, 0.85, release)
    n = env.size
    L = np.zeros(n)
    R = np.zeros(n)
    offs = np.linspace(-1, 1, voices) * detune
    amps = np.where(np.abs(offs) < 1e-9, 1.0, 0.72)
    pans = np.linspace(-width, width, voices)
    rng.shuffle(pans)
    for f in np.atleast_1d(freqs):
        for o, a, p in zip(offs, amps, pans):
            v = saw(f * 2 ** (o / 12), n, rng.random()) * a
            th = (p + 1) * np.pi / 4
            L += v * np.cos(th)
            R += v * np.sin(th)
    g = 1.0 / np.sqrt(voices * len(np.atleast_1d(freqs)))
    fc = cutoff if cutoff_env is None else cutoff_env(n)
    out = svf(np.stack([L, R]) * g, fc, res, 'lp', poles=4)
    return out * env


def pluck(f, n_gate, rng, bright=1.0):
    n = n_gate + int(0.35 * SR)
    t = np.arange(n) / SR
    o1 = saw(f, n, rng.random())
    oL = o1 + 0.55 * saw(f * 2 ** (9 / 1200), n, rng.random()) + 0.35 * square(f / 2, n)
    oR = o1 + 0.55 * saw(f * 2 ** (-9 / 1200), n, rng.random()) + 0.35 * square(f / 2, n)
    fc = f * 1.2 + 5200 * bright * np.exp(-t / 0.09) + 900 * np.exp(-t / 0.5)
    sig = svf(np.stack([oL, oR]), fc, 0.32, 'lp', poles=2)
    g = adsr(n_gate, 0.002, 0.05, 1.0, 0.09)
    g = np.pad(g, (0, max(0, n - g.size)))[:n]
    amp = np.exp(-t / 0.55) * g
    click = svf(rng.standard_normal(n) * np.exp(-t / 0.003), 3000, 0, 'hp') * 0.15
    return (sig + click) * amp * 0.5


def lead(f, n_gate, rng, cutoff=4200.0):
    env = adsr(n_gate, 0.008, 0.25, 0.8, 0.14)
    n = env.size
    t = np.arange(n) / SR
    vib = 1 + (2 ** (14 / 1200) - 1) * np.sin(TWO_PI * 5.4 * t) * np.clip((t - 0.28) / 0.25, 0, 1)
    out = supersaw([f], n_gate, rng, voices=5, detune=0.11, cutoff=cutoff, attack=0.008, release=0.14,
                   res=0.2, width=0.7, cutoff_env=lambda m: cutoff * (1 + 0.9 * np.exp(-np.arange(m) / SR / 0.12)))
    # vibrato applied as gentle AM+FM approximation is overkill; render vibrato voice on top
    core = saw(f * vib, n, rng.random())
    core = svf(core, cutoff * 0.8, 0.1, 'lp') * env * 0.35
    return out + core


def bass(f, n_gate, drive=1.0):
    env = adsr(n_gate, 0.003, 0.12, 0.85, 0.03)
    n = env.size
    t = np.arange(n) / SR
    sub = sine(f, n) * env
    mid = saw(f, n) + 0.5 * square(f * 1.003, n)
    fc = 220 + 1500 * drive * np.exp(-t / 0.07)
    mid = svf(mid, fc, 0.35, 'lp')
    mid = soft(mid * 1.5 * drive, 2.0)
    mid = svf(mid, 110, 0.0, 'hp') * env
    return sub * 0.9, mid * 0.45


# ----------------------------------------------------------------------------- drums
def kick(rng, heavy=False):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 52 + 200 * np.exp(-t / 0.026) + 45 * np.exp(-t / 0.11)
    body = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / (0.28 if heavy else 0.23))
    click = svf(rng.standard_normal(n) * np.exp(-t / 0.0035), 2500, 0.1, 'hp') * 0.3
    k = soft(body + click, 2.4)
    k *= np.clip((n - np.arange(n)) / (0.05 * SR), 0, 1)
    return k


def snare(rng):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    fb = 190 * (1 + 0.25 * np.exp(-t / 0.015))
    tone = 0.7 * np.sin(TWO_PI * np.cumsum(fb) / SR) * np.exp(-t / 0.07) \
        + 0.25 * np.sin(TWO_PI * 335 * t) * np.exp(-t / 0.045)
    nz = rng.standard_normal(n)
    nz = svf(svf(nz, 4200, 0.15, 'bp'), 900, 0, 'hp') * np.exp(-t / 0.16) * 1.1
    return soft(tone + nz, 1.4) * 0.9


def clap(rng):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    env = sum(np.where(t >= d, np.exp(-(t - d) / 0.0055), 0) for d in (0, 0.010, 0.021))
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) / 0.13) * 0.8, 0)
    nz = svf(rng.standard_normal(n), 1250, 0.35, 'bp')
    nz = svf(nz, 600, 0, 'hp')
    return nz * env * 1.3


_METAL = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0])


def hat(rng, open_=False):
    n = int((0.55 if open_ else 0.12) * SR)
    t = np.arange(n) / SR
    m = sum(square(f * 1.6, n, rng.random()) for f in _METAL) / 6
    m = m + 0.4 * rng.standard_normal(n)
    m = svf(svf(m, 9500, 0.2, 'bp'), 7000, 0.0, 'hp', poles=4)
    env = np.exp(-t / (0.16 if open_ else 0.028))
    return m * env * 1.4


def tom(rng, f0):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.55 * np.exp(-t / 0.05))
    body = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    nz = svf(rng.standard_normal(n), f0 * 6, 0.2, 'bp') * np.exp(-t / 0.04) * 0.3
    return soft(body + nz, 1.5)


def crash(rng, length=3.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    out = []
    for _ in range(2):
        m = sum(square(f * r, n, rng.random()) for f in _METAL for r in (2.3, 3.1)) / 12
        nz = rng.standard_normal(n)
        sig = svf(0.6 * m + 0.8 * nz, 4200, 0.0, 'hp', poles=4)
        sig = svf(sig, 13000 * np.exp(-t / 2.0) + 4000, 0.0, 'lp')
        env = 0.25 * np.exp(-t / 0.05) + 0.75 * np.exp(-t / 1.1)
        out.append(sig * env)
    return np.stack(out) * 0.9


# ----------------------------------------------------------------------------- transition FX
def impact(rng, size=1.0):
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    f = 42 + 70 * np.exp(-t / 0.07)
    boom = np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / (0.9 + 0.8 * size))
    st = []
    for _ in range(2):
        nz = svf(rng.standard_normal(n), 7000 * np.exp(-t / 0.12) + 150, 0.1, 'lp', poles=4)
        st.append(nz * np.exp(-t / 0.45) * 0.55)
    st = np.stack(st)
    out = soft(boom * 1.2, 1.3)[None] + st
    return out * size


def riser(rng, length, size=1.0):
    n = int(length * SR)
    x = np.arange(n) / n
    fc = 250 * (9000 / 250) ** (x ** 1.4)
    st = []
    for _ in range(2):
        st.append(svf(rng.standard_normal(n), fc, 0.55, 'bp'))
    st = np.stack(st)
    pitch = hz(48 + 36 * x ** 1.3)
    tone = svf(saw(pitch, n) + saw(pitch * 1.01, n), fc * 0.8, 0.3, 'lp') * 0.18
    amp = x ** 2.2
    fade_out = np.clip((n - np.arange(n)) / (0.01 * SR), 0, 1)
    return (st * 0.9 + tone[None]) * amp * fade_out * size


def downlifter(rng, length, size=1.0):
    n = int(length * SR)
    x = np.arange(n) / n
    fc = 7000 * (180 / 7000) ** x
    st = np.stack([svf(rng.standard_normal(n), fc, 0.5, 'bp') for _ in range(2)])
    return st * (1 - x) ** 2 * size * 0.8


def revcym(rng, length, size=1.0):
    c = crash(rng, length=max(length, 1.0) + 0.2)
    c = c[:, :int(length * SR)][:, ::-1]
    return c * size


def subdrop(size=1.0):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 40 + 55 * np.exp(-t / 0.35)
    return np.sin(TWO_PI * np.cumsum(f) / SR) * np.exp(-t / 0.9) * np.clip(t / 0.004, 0, 1) * size


# ----------------------------------------------------------------------------- space
def make_ir(rt60, predelay=0.02, damp=4000.0, seed=1, er=True):
    rng = np.random.default_rng(seed)
    n = int(rt60 * 1.1 * SR)
    t = np.arange(n) / SR
    dec = 10 ** (-3 * t / rt60)
    fc = damp + (14000 - damp) * np.exp(-t / (rt60 * 0.15))
    chans = []
    for _ in range(2):
        x = rng.standard_normal(n) * dec
        x = svf(x, fc, 0.0, 'lp')
        x = svf(x, 120, 0.0, 'hp')
        if er:
            for d, g in zip(rng.uniform(0.004, 0.05, 10), rng.uniform(0.2, 0.6, 10)):
                i = int(d * SR)
                x[i] += g * rng.choice([-1, 1]) * 8
        x *= np.clip(t / 0.004, 0, 1)
        chans.append(x)
    ir = np.stack(chans)
    ir = np.pad(ir, ((0, 0), (int(predelay * SR), 0)))
    return ir / np.sqrt(np.sum(ir ** 2) / 2)


def convolve(x, ir):
    n = x.shape[1]
    return np.stack([oaconvolve(x[c], ir[c])[:n] for c in range(2)])


def pingpong(x, delay_s, fb=0.45, taps=6, lp=4500.0, hp=300.0):
    mono = x.mean(0)
    d = int(round(delay_s * SR))
    out = np.zeros_like(x)
    tap = svf(mono, hp, 0, 'hp')
    for k in range(1, taps + 1):
        tap = svf(tap, lp, 0, 'lp') * (fb if k > 1 else 1.0)
        s = k * d
        if s >= mono.size:
            break
        out[k % 2, s:] += tap[:mono.size - s]
    return out


def duck_env(hit_times, n, depth=0.7, release=0.14, attack=0.004):
    """Sidechain gain curve from kick times (seconds)."""
    g = np.ones(n)
    t = np.arange(n) / SR
    for tk in hit_times:
        i0 = int(tk * SR)
        i1 = min(n, i0 + int(release * 6 * SR))
        if i0 >= n:
            continue
        tt = t[i0:i1] - tk
        shape = np.where(tt < attack, tt / attack, np.exp(-(tt - attack) / release))
        g[i0:i1] = np.minimum(g[i0:i1], 1 - depth * shape)
    pre = max(1, int(0.003 * SR))
    # smooth onset slightly earlier than the kick to avoid clicks
    return np.convolve(g, np.ones(pre) / pre, mode='same')


@njit(cache=True)
def _release(g, coef):
    out = np.empty_like(g)
    cur = 1.0
    for i in range(g.size):
        if g[i] < cur:
            cur = g[i]
        else:
            cur = cur + (g[i] - cur) * coef
        out[i] = cur
    return out


def limiter(x, ceiling_db=-1.0, lookahead=0.005, release=0.09):
    """Lookahead true-peak limiter (4x oversampled peak detection, no makeup gain)."""
    c = 10 ** (ceiling_db / 20)
    up = np.abs(resample_poly(x, 4, 1, axis=1)).max(0)
    pk = up[: x.shape[1] * 4].reshape(-1, 4).max(1)
    pk = np.pad(pk, (0, x.shape[1] - pk.size), constant_values=0)
    req = np.minimum(1.0, c / np.maximum(pk, 1e-12))
    L = max(2, int(lookahead * SR))
    hold = minimum_filter1d(req, size=L + 1, origin=-(L // 2))       # min over [i, i+L]
    hold = _release(hold, 1 - np.exp(-1 / (release * SR)))
    g = uniform_filter1d(hold, size=L, origin=(L - 1) // 2)           # mean over [i-L+1, i]
    g = np.minimum(g, hold)
    return x * g[None], g
