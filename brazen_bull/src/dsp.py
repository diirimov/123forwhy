"""Core DSP toolkit for the Brazen Bull production engine.

Everything here is original code: band-limited oscillators, zero-delay-feedback
filters, physical-model strings, modal resonators, convolution reverbs and the
utilities the instrument and mixing layers are built from.
"""
import numpy as np
from numba import njit
from scipy import signal

SR = 48000
BPM = 136.0
BEAT = 60.0 / BPM
STEP = BEAT / 4.0          # 16th note
BAR = BEAT * 4.0
N_TOTAL = int(round(60.0 * SR))   # exactly 60 s

_rng = np.random.default_rng(20261125)


def rng():
    return _rng


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


def db(x):
    return 10.0 ** (x / 20.0)


def tarr(dur):
    return np.arange(int(round(dur * SR))) / SR


# ----------------------------------------------------------------------------
# Static filters (scipy)
# ----------------------------------------------------------------------------
def _sos(kind, f, order=2, q=None):
    f = np.clip(f, 5.0, SR * 0.49)
    if kind in ("lp", "hp"):
        return signal.butter(order, f, btype="low" if kind == "lp" else "high", fs=SR, output="sos")
    if kind == "bp":
        lo, hi = f
        return signal.butter(order, [max(lo, 5.0), min(hi, SR * 0.49)], btype="band", fs=SR, output="sos")
    raise ValueError(kind)


def lp(x, f, order=2):
    return signal.sosfilt(_sos("lp", f, order), x, axis=-1)


def hp(x, f, order=2):
    return signal.sosfilt(_sos("hp", f, order), x, axis=-1)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(_sos("bp", (lo, hi), order), x, axis=-1)


def lp0(x, f, order=2):
    """zero-phase lowpass (for offline envelopes / mastering)"""
    return signal.sosfiltfilt(_sos("lp", f, order), x, axis=-1)


def rbj(kind, f, q=0.707, gain_db=0.0):
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * f / SR
    cw, sw = np.cos(w0), np.sin(w0)
    alpha = sw / (2 * q)
    if kind == "peak":
        b = [1 + alpha * A, -2 * cw, 1 - alpha * A]
        a = [1 + alpha / A, -2 * cw, 1 - alpha / A]
    elif kind == "lowshelf":
        sA = np.sqrt(A)
        b = [A * ((A + 1) - (A - 1) * cw + 2 * sA * alpha), 2 * A * ((A - 1) - (A + 1) * cw),
             A * ((A + 1) - (A - 1) * cw - 2 * sA * alpha)]
        a = [(A + 1) + (A - 1) * cw + 2 * sA * alpha, -2 * ((A - 1) + (A + 1) * cw),
             (A + 1) + (A - 1) * cw - 2 * sA * alpha]
    elif kind == "highshelf":
        sA = np.sqrt(A)
        b = [A * ((A + 1) + (A - 1) * cw + 2 * sA * alpha), -2 * A * ((A - 1) + (A + 1) * cw),
             A * ((A + 1) + (A - 1) * cw - 2 * sA * alpha)]
        a = [(A + 1) - (A - 1) * cw + 2 * sA * alpha, 2 * ((A - 1) - (A + 1) * cw),
             (A + 1) - (A - 1) * cw - 2 * sA * alpha]
    elif kind == "bpf":
        b = [alpha, 0, -alpha]
        a = [1 + alpha, -2 * cw, 1 - alpha]
    elif kind == "notch":
        b = [1, -2 * cw, 1]
        a = [1 + alpha, -2 * cw, 1 - alpha]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    return b, a


def eq(x, kind, f, q=0.707, g=0.0):
    b, a = rbj(kind, f, q, g)
    return signal.lfilter(b, a, x, axis=-1)


# ----------------------------------------------------------------------------
# Time-varying TPT state-variable filter (Zavalishin) with optional drive
# ----------------------------------------------------------------------------
@njit(cache=True, fastmath=True)
def svf(x, cutoff, q, mode, drive):
    n = x.shape[0]
    out = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 1.0 / q
    for i in range(n):
        fc = cutoff[i]
        if fc < 10.0:
            fc = 10.0
        if fc > 0.45 * 48000.0:
            fc = 0.45 * 48000.0
        g = np.tan(np.pi * fc / 48000.0)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        xin = x[i]
        if drive > 0.0:
            xin = np.tanh(xin * drive) / drive
        v3 = xin - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if drive > 0.0:  # gentle saturation of the integrator state -> analog-ish growl
            ic1 = np.tanh(ic1 * 0.5) * 2.0
        if mode == 0:
            out[i] = v2
        elif mode == 1:
            out[i] = v1
        else:
            out[i] = xin - k * v1 - v2
    return out


def svf_lp(x, cutoff, q=0.707, drive=0.0):
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape).copy()
    return svf(np.ascontiguousarray(x, dtype=float), c, float(q), 0, float(drive))


def svf_bp(x, cutoff, q=1.0):
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape).copy()
    return svf(np.ascontiguousarray(x, dtype=float), c, float(q), 1, 0.0)


def svf_hp(x, cutoff, q=0.707):
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape).copy()
    return svf(np.ascontiguousarray(x, dtype=float), c, float(q), 2, 0.0)


# ----------------------------------------------------------------------------
# Band-limited wavetable oscillators
# ----------------------------------------------------------------------------
TBL = 4096
_NH = np.array([1, 2, 3, 4, 6, 8, 11, 16, 22, 32, 45, 64, 90, 128, 180, 256, 360, 512])


def _build_tables(kind):
    ph = np.arange(TBL) / TBL
    tabs = np.zeros((len(_NH), TBL + 1))
    for ti, nh in enumerate(_NH):
        w = np.zeros(TBL)
        for k in range(1, nh + 1):
            if kind == "square" and k % 2 == 0:
                continue
            sigma = np.sinc(k / (nh + 1))   # Lanczos sigma -> no Gibbs ringing
            w += sigma * np.sin(2 * np.pi * k * ph) / k
        w /= np.max(np.abs(w)) + 1e-12
        tabs[ti, :TBL] = w
        tabs[ti, TBL] = w[0]
    return tabs


SAW_T = _build_tables("saw")
SQR_T = _build_tables("square")
NH_ARR = _NH.astype(np.float64)


@njit(cache=True, fastmath=True)
def wt_osc(freq, tabs, nh, phase0):
    n = freq.shape[0]
    out = np.empty(n)
    ph = phase0
    nt = tabs.shape[0]
    for i in range(n):
        f = freq[i]
        maxh = 19000.0 / max(f, 1.0)
        ti = 0
        for j in range(nt):
            if nh[j] <= maxh:
                ti = j
        p = ph * 4096.0
        ip = int(p)
        fr = p - ip
        out[i] = tabs[ti, ip] * (1.0 - fr) + tabs[ti, ip + 1] * fr
        ph += f / 48000.0
        ph -= np.floor(ph)
    return out


def saw(freq, phase0=None):
    freq = np.ascontiguousarray(freq, dtype=float)
    p0 = _rng.random() if phase0 is None else phase0
    return wt_osc(freq, SAW_T, NH_ARR, p0)


def square(freq, phase0=None):
    freq = np.ascontiguousarray(freq, dtype=float)
    p0 = _rng.random() if phase0 is None else phase0
    return wt_osc(freq, SQR_T, NH_ARR, p0)


def sine_f(freq, phase0=0.0):
    return np.sin(2 * np.pi * (np.cumsum(freq) / SR + phase0))


# ----------------------------------------------------------------------------
# Physical-model string (extended Karplus-Strong, fractional delay, tunable loss)
# ----------------------------------------------------------------------------
@njit(cache=True, fastmath=True)
def ks_string(n, f, t60, s, exc):
    L = 48000.0 / f
    N = int(np.floor(L - s - 0.2))
    if N < 2:
        N = 2
    d = L - s - N
    c = (1.0 - d) / (1.0 + d)
    g = 10.0 ** (-3.0 / (t60 * f))
    buf = np.zeros(N)
    out = np.empty(n)
    ptr = 0
    lp1 = 0.0
    apx = 0.0
    apy = 0.0
    ne = exc.shape[0]
    for i in range(n):
        dl = buf[ptr]
        lo = g * ((1.0 - s) * dl + s * lp1)
        lp1 = dl
        ap = c * lo + apx - c * apy
        apx = lo
        apy = ap
        y = ap
        if i < ne:
            y += exc[i]
        buf[ptr] = y
        ptr += 1
        if ptr >= N:
            ptr = 0
        out[i] = y
    return out


# ----------------------------------------------------------------------------
# Modal resonator bank (vectorised): partials with individual decays
# ----------------------------------------------------------------------------
def modal(freqs, amps, decays, dur, detune_beat=0.0, phases=None, attack=0.0005):
    t = tarr(dur)
    out = np.zeros_like(t)
    for i, (f, a, d) in enumerate(zip(freqs, amps, decays)):
        if f >= SR * 0.45:
            continue
        ph = _rng.random() * 2 * np.pi if phases is None else phases[i]
        env = np.exp(-t / d)
        if detune_beat > 0:
            out += a * env * 0.5 * (np.sin(2 * np.pi * (f - detune_beat) * t + ph) +
                                    np.sin(2 * np.pi * (f + detune_beat) * t + ph * 1.3))
        else:
            out += a * env * np.sin(2 * np.pi * f * t + ph)
    na = max(int(attack * SR), 1)
    out[:na] *= np.linspace(0, 1, na)
    return out


# ----------------------------------------------------------------------------
# Noise generators
# ----------------------------------------------------------------------------
def white(n):
    return _rng.standard_normal(n)


def pink(n):
    w = _rng.standard_normal(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w) * 8.0


def brown(n):
    w = _rng.standard_normal(n)
    return signal.lfilter([1.0], [1.0, -0.997], w) * 0.06


def smooth_random(n, rate_hz, seed_scale=1.0):
    """slowly varying random control signal in [-1, 1]"""
    k = max(int(n * rate_hz / SR) + 4, 4)
    pts = _rng.uniform(-1, 1, k)
    x = np.linspace(0, k - 3.0001, n)
    i = np.floor(x).astype(int)
    fr = x - i
    p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
    # Catmull-Rom
    return 0.5 * ((2 * p1) + (-p0 + p2) * fr + (2 * p0 - 5 * p1 + 4 * p2 - p3) * fr ** 2 +
                  (-p0 + 3 * p1 - 3 * p2 + p3) * fr ** 3) * seed_scale


# ----------------------------------------------------------------------------
# Envelopes / shaping
# ----------------------------------------------------------------------------
def adsr(n, a, d, s, r, gate_len=None):
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    g_n = n - r_n if gate_len is None else min(int(gate_len * SR), n)
    env = np.zeros(n)
    idx = 0
    if a_n > 0:
        seg = min(a_n, n)
        env[:seg] = np.linspace(0, 1, a_n, endpoint=False)[:seg] ** 0.8
        idx = seg
    if idx < g_n:
        seg = min(d_n, g_n - idx)
        if seg > 0:
            env[idx:idx + seg] = s + (1 - s) * np.exp(-np.arange(seg) / max(d_n / 4.0, 1))
            idx += seg
        if idx < g_n:
            env[idx:g_n] = env[idx - 1] if idx > 0 else s
            idx = g_n
    last = env[idx - 1] if idx > 0 else 0.0
    rem = n - idx
    if rem > 0:
        env[idx:] = last * np.exp(-np.arange(rem) / max(r_n / 5.0, 1))
    return env


def fade(x, fi=0.002, fo=0.005):
    x = x.copy()
    a, b = int(fi * SR), int(fo * SR)
    if a > 0:
        x[..., :a] *= np.linspace(0, 1, a)
    if b > 0:
        x[..., -b:] *= np.linspace(1, 0, b)
    return x


def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def wavefold(x, amt):
    return np.sin(x * amt * np.pi / 2)


def normalize(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def pitch_shift_resample(x, semis):
    """tape-style pitch shift (formants move too) - used for monstrous layers"""
    r = 2.0 ** (semis / 12.0)
    n_out = int(len(x) / r)
    src = np.arange(n_out) * r
    return np.interp(src, np.arange(len(x)), x)


# ----------------------------------------------------------------------------
# Stereo helpers
# ----------------------------------------------------------------------------
def pan(x, p):
    """constant-power pan, p in [-1, 1]; returns (2, n)"""
    th = (p + 1) * np.pi / 4
    return np.vstack([x * np.cos(th), x * np.sin(th)])


def to_st(x):
    return np.vstack([x, x]) if x.ndim == 1 else x


def widen(st, amt):
    m = (st[0] + st[1]) * 0.5
    s = (st[0] - st[1]) * 0.5 * amt
    return np.vstack([m + s, m - s])


def haas(x, ms, p=0.0):
    d = int(ms * SR / 1000)
    y = np.concatenate([np.zeros(d), x])[:len(x)]
    return np.vstack([x, y]) if p <= 0 else np.vstack([y, x])


def chorus(x, depth_ms=6.0, rate=0.35, mix=0.5, base_ms=12.0):
    n = len(x)
    t = np.arange(n) / SR
    out = []
    for ph in (0.0, np.pi * 0.66):
        d = (base_ms + depth_ms * 0.5 * (1 + np.sin(2 * np.pi * rate * t + ph))) * SR / 1000
        idx = np.arange(n) - d
        y = np.interp(idx, np.arange(n), x, left=0.0)
        out.append((1 - mix) * x + mix * y)
    return np.vstack(out)


# ----------------------------------------------------------------------------
# Reverb: synthesised stereo impulse responses (multiband decay) + FFT convolution
# ----------------------------------------------------------------------------
def make_ir(rt60_low, rt60_mid, rt60_high, length, predelay_ms=10.0, er_density=12,
            width=1.0, bright=9000.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    chans = []
    for ch in range(2):
        nz = r.standard_normal(n)
        lo = lp(nz, 250.0, 2)
        hi = hp(nz, 3500.0, 2)
        mid = nz - lo - hi
        def dec(rt):
            return np.exp(-6.9078 * t / rt)
        ir = lo * dec(rt60_low) + mid * dec(rt60_mid) + hi * dec(rt60_high)
        # soft onset (diffusion build-up)
        build = 1 - np.exp(-t / 0.012)
        ir *= build
        # early reflections
        for k in range(er_density):
            tt = r.uniform(0.004, 0.07)
            ii = int(tt * SR)
            if ii < n:
                ir[ii] += r.uniform(-1, 1) * 2.2 * np.exp(-tt / 0.05)
        ir = lp(ir, bright, 2)
        pd = int(predelay_ms * SR / 1000)
        ir = np.concatenate([np.zeros(pd), ir])[:n]
        chans.append(ir)
    ir = np.vstack(chans)
    ir = widen(ir, width)
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


def convolve_st(x_st, ir):
    x_st = to_st(x_st)
    out = np.zeros((2, x_st.shape[1] + ir.shape[1] - 1))
    # true-stereo-ish: L->L, R->R plus a little cross feed for density
    for c in range(2):
        out[c] += signal.fftconvolve(x_st[c], ir[c])
        out[c] += 0.25 * signal.fftconvolve(x_st[1 - c], ir[1 - c])
    return out[:, :x_st.shape[1]]


def pingpong(x_st, delay_s, fb, n_taps=6, lp_f=5000.0, hp_f=300.0):
    x_st = to_st(x_st)
    n = x_st.shape[1]
    mono = (x_st[0] + x_st[1]) * 0.5
    mono = hp(lp(mono, lp_f), hp_f)
    out = np.zeros((2, n))
    d = int(delay_s * SR)
    g = 1.0
    sig = mono
    for k in range(1, n_taps + 1):
        g *= fb
        sh = k * d
        if sh >= n:
            break
        ch = (k - 1) % 2
        out[ch, sh:] += g * sig[:n - sh]
        if k % 2 == 0:
            sig = lp(sig, lp_f * 0.85)
    return out
