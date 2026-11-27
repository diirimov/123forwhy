"""
FOLLOW THE PIPER -- core DSP: filters, envelopes, reverbs, saturation, dynamics.

Everything is float64 numpy at 48 kHz. Stereo signals are shaped (n, 2).
"""
import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(1284)       # 1284: the year the children of Hamelin vanished


def reseed(seed):
    global _rng
    _rng = np.random.default_rng(seed)


def rng():
    return _rng


# --------------------------------------------------------------------------- conversions
def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


def db(x):
    return 10.0 ** (x / 20.0)


def todb(x):
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-12))


# --------------------------------------------------------------------------- filters (RBJ biquads)
def _biquad(kind, f, q=0.707, gain_db=0.0):
    f = min(max(f, 5.0), SR * 0.49)
    w = 2 * np.pi * f / SR
    cw, sw = np.cos(w), np.sin(w)
    a = sw / (2 * q)
    A = 10 ** (gain_db / 40)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; aa = [1 + a, -2 * cw, 1 - a]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]; aa = [1 + a, -2 * cw, 1 - a]
    elif kind == "bp":
        b = [a, 0, -a]; aa = [1 + a, -2 * cw, 1 - a]
    elif kind == "peak":
        b = [1 + a * A, -2 * cw, 1 - a * A]; aa = [1 + a / A, -2 * cw, 1 - a / A]
    elif kind == "notch":
        b = [1, -2 * cw, 1]; aa = [1 + a, -2 * cw, 1 - a]
    elif kind == "ls":
        sA = np.sqrt(A)
        b = [A * ((A + 1) - (A - 1) * cw + 2 * sA * a), 2 * A * ((A - 1) - (A + 1) * cw),
             A * ((A + 1) - (A - 1) * cw - 2 * sA * a)]
        aa = [(A + 1) + (A - 1) * cw + 2 * sA * a, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - 2 * sA * a]
    elif kind == "hs":
        sA = np.sqrt(A)
        b = [A * ((A + 1) + (A - 1) * cw + 2 * sA * a), -2 * A * ((A - 1) + (A + 1) * cw),
             A * ((A + 1) + (A - 1) * cw - 2 * sA * a)]
        aa = [(A + 1) - (A - 1) * cw + 2 * sA * a, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - 2 * sA * a]
    else:
        raise ValueError(kind)
    b = np.array(b) / aa[0]; aa = np.array(aa) / aa[0]
    return b, aa


def bq(x, kind, f, q=0.707, g=0.0):
    b, a = _biquad(kind, f, q, g)
    return signal.lfilter(b, a, x, axis=0)


def lp(x, f, q=0.707):
    return bq(x, "lp", f, q)


def hp(x, f, q=0.707):
    return bq(x, "hp", f, q)


def bp(x, f, q=1.0):
    return bq(x, "bp", f, q)


def peq(x, f, g, q=1.0):
    return bq(x, "peak", f, q, g)


def ls(x, f, g, q=0.707):
    return bq(x, "ls", f, q, g)


def hs(x, f, g, q=0.707):
    return bq(x, "hs", f, q, g)


def lp4(x, f):
    return lp(lp(x, f, 0.54), f, 1.31)


def hp4(x, f):
    return hp(hp(x, f, 0.54), f, 1.31)


def onepole_lp(x, f):
    a = np.exp(-2 * np.pi * f / SR)
    return signal.lfilter([1 - a], [1, -a], x, axis=0)


def tv_lp(x, fc, q=0.707, block=64):
    """time-varying 2-pole lowpass, fc array per sample (state-variable, vectorised by blocks)"""
    n = len(x)
    y = np.zeros_like(x)
    zi = None
    for i in range(0, n, block):
        f = float(np.mean(fc[i:i + block]))
        b, a = _biquad("lp", f, q)
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0.0
        y[i:i + block], zi = signal.lfilter(b, a, x[i:i + block], zi=zi)
    return y


# --------------------------------------------------------------------------- envelopes
def adsr(n, a, d, s, r, sus_len=None):
    """sample-domain ADSR, times in seconds; sustain held until n - r"""
    env = np.zeros(n)
    A = max(1, int(a * SR)); D = max(1, int(d * SR)); R = max(1, int(r * SR))
    hold_end = n - R if sus_len is None else min(n, A + D + int(sus_len * SR))
    i = 0
    seg = min(A, n); env[:seg] = np.linspace(0, 1, A, endpoint=False)[:seg]; i = seg
    if i < n:
        seg = min(D, n - i); env[i:i + seg] = np.linspace(1, s, D, endpoint=False)[:seg]; i += seg
    if i < hold_end:
        env[i:hold_end] = s; i = hold_end
    if i < n:
        seg = n - i
        env[i:] = (env[i - 1] if i > 0 else s) * np.linspace(1, 0, seg)
    return env


def expdec(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def fade(x, fi=0.0, fo=0.0):
    x = x.copy()
    n = len(x)
    a = min(n, int(fi * SR)); b = min(n, int(fo * SR))
    if a > 1:
        w = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
        x[:a] = (x[:a].T * w).T
    if b > 1:
        w = np.cos(np.linspace(0, np.pi / 2, b)) ** 2
        x[-b:] = (x[-b:].T * w).T
    return x


# --------------------------------------------------------------------------- noise
def noise(n):
    return _rng.standard_normal(n)


def pink(n):
    w = _rng.standard_normal(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w) * 6


# --------------------------------------------------------------------------- stereo
def pan(x, p):
    """equal-power pan, p in [-1, 1]; mono in, stereo out"""
    th = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], axis=1)


def to_st(x):
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def width(x, w):
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2
    s = s * w
    return np.stack([m + s, m - s], axis=1)


def haas(x, ms, side=1):
    """mono -> stereo with a short delay on one side"""
    d = int(ms * SR / 1000)
    y = np.concatenate([np.zeros(d), x])[:len(x)]
    return np.stack([x, y], axis=1) if side > 0 else np.stack([y, x], axis=1)


# --------------------------------------------------------------------------- saturation / dynamics
def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def asym_sat(x, drive=1.5, bias=0.12):
    y = np.tanh(drive * (x + bias)) - np.tanh(drive * bias)
    return y / drive


def env_follow(x, att, rel):
    """peak envelope follower on |x| (mono), attack / release in seconds"""
    from numba import njit  # noqa
    return _envf(np.abs(x).astype(np.float64), np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR)))


try:
    from numba import njit

    @njit(cache=True)
    def _envf(x, aa, ar):
        y = np.empty_like(x)
        e = 0.0
        for i in range(len(x)):
            v = x[i]
            if v > e:
                e = aa * e + (1 - aa) * v
            else:
                e = ar * e + (1 - ar) * v
            y[i] = e
        return y

    @njit(cache=True)
    def _smooth_gain(g, aa, ar):
        y = np.empty_like(g)
        s = 1.0
        for i in range(len(g)):
            v = g[i]
            if v < s:
                s = aa * s + (1 - aa) * v
            else:
                s = ar * s + (1 - ar) * v
            y[i] = s
        return y
except Exception:  # pragma: no cover
    raise


def compress(x, thr_db=-18, ratio=3.0, att=0.005, rel=0.12, knee=6.0, makeup=0.0, sc=None):
    """feed-forward compressor; x mono or stereo; sc optional sidechain (mono)"""
    det = sc if sc is not None else (np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x))
    e = _envf(np.abs(det).astype(np.float64), np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR)))
    lv = todb(e)
    over = lv - thr_db
    gr = np.where(over <= -knee / 2, 0.0,
                  np.where(over >= knee / 2, over * (1 - 1 / ratio),
                           (1 - 1 / ratio) * (over + knee / 2) ** 2 / (2 * knee)))
    g = db(-gr + makeup)
    return (x.T * g).T if x.ndim == 2 else x * g


def duck(x, trig, depth_db=-8, att=0.003, hold=0.03, rel=0.16):
    """sidechain ducking curve from a list of trigger times (s), applied to x"""
    n = len(x)
    g = np.zeros(n)
    A = int(att * SR); H = int(hold * SR); R = int(rel * SR)
    shape = np.concatenate([np.linspace(0, 1, A, endpoint=False), np.ones(H),
                            (np.cos(np.linspace(0, np.pi, R)) + 1) / 2])
    for t in trig:
        i = int(t * SR)
        if i >= n:
            continue
        seg = shape[:n - i]
        g[i:i + len(seg)] = np.maximum(g[i:i + len(seg)], seg)
    gain = db(depth_db * g)
    return (x.T * gain).T if x.ndim == 2 else x * gain


# --------------------------------------------------------------------------- reverb (synthetic stereo IR, convolution)
def make_ir(rt60, predelay=0.012, damp_hi=6000, damp_lo=120, er=True, size=1.0, seed=3, bright_decay=True,
            diffusion_ms=None):
    r = np.random.default_rng(seed)
    n = int((rt60 * 1.15 + predelay) * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        w = r.standard_normal(n)
        env = np.exp(-6.9 * t / rt60)
        # slow attack of the diffuse tail (density build-up)
        att = diffusion_ms if diffusion_ms is not None else 18 * size
        env *= 1 - np.exp(-t / (att / 1000))
        tail = w * env
        if bright_decay:
            # frequency-dependent decay: split into bands that decay at different speeds
            lo = lp(tail, 900)
            hi = tail - lo
            hi *= np.exp(-6.9 * t / (rt60 * 0.45))
            tail = lo + hi
        tail = lp(tail, damp_hi)
        tail = hp(tail, damp_lo)
        d = int(predelay * SR)
        ir[d:, c] = tail[:n - d]
        if er:
            for k in range(9):
                tt = predelay * 0.3 + r.uniform(0.002, 0.045) * size
                i = int(tt * SR)
                if i < n:
                    ir[i, c] += r.uniform(0.25, 0.6) * (-1) ** r.integers(2) * np.exp(-tt * 18)
    ir /= np.sqrt((ir ** 2).sum(axis=0).mean())
    return ir


def convolve_st(x, ir):
    """x mono or stereo, ir stereo -> stereo (true stereo for mono; L->L, R->R for stereo)"""
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    out = np.zeros((len(x) + len(ir) - 1, 2))
    for c in range(2):
        out[:, c] = signal.fftconvolve(x[:, c], ir[:, c])
    # cross-feed a little for realism
    out = out * 0.93 + out[:, ::-1] * 0.07
    return out[:len(x)]


def delay(x, t, fb=0.3, mix=0.3, lpf=4000, hpf=200, pingpong=True, n_rep=8):
    """feedback delay rendered by summing taps (exact, no loop)"""
    x = to_st(x)
    d = int(t * SR)
    out = np.zeros_like(x)
    tap = x.copy()
    for k in range(1, n_rep + 1):
        tap = lp(hp(tap, hpf), lpf) * fb if k > 1 else lp(hp(tap, hpf), lpf)
        sh = np.zeros_like(x)
        if d * k < len(x):
            sh[d * k:] = tap[:len(x) - d * k] if k == 1 else tap[:len(x) - d * k]
        if pingpong and k % 2 == 1:
            sh = sh[:, ::-1]
        out += sh
        if k == 1:
            tap = tap
    return x + out * mix


# --------------------------------------------------------------------------- resampling playback
def resample_play(x, ratio, n_out=None, start=0.0):
    """play mono array x at time-varying speed `ratio` (scalar or array per output sample)"""
    if np.isscalar(ratio):
        if n_out is None:
            n_out = int((len(x) - start) / ratio)
        pos = start + np.arange(n_out) * ratio
    else:
        pos = start + np.concatenate([[0], np.cumsum(ratio[:-1])])
        n_out = len(ratio)
    pos = np.minimum(pos, len(x) - 2)
    i = pos.astype(np.int64)
    f = pos - i
    # cubic (Catmull-Rom) interpolation
    xm1 = x[np.maximum(i - 1, 0)]; x0 = x[i]; x1 = x[i + 1]; x2 = x[np.minimum(i + 2, len(x) - 1)]
    a = -0.5 * xm1 + 1.5 * x0 - 1.5 * x1 + 0.5 * x2
    b = xm1 - 2.5 * x0 + 2 * x1 - 0.5 * x2
    c = -0.5 * xm1 + 0.5 * x1
    return ((a * f + b) * f + c) * f + x0


def lufs(x):
    import pyloudnorm as pyln
    m = pyln.Meter(SR)
    return m.integrated_loudness(to_st(x))


def true_peak_db(x, os=4):
    y = signal.resample_poly(to_st(x), os, 1, axis=0)
    return todb(np.abs(y).max())
