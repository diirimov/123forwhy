"""V2 engine: 48 kHz, 150 BPM grid, numba DSP kernels, human-like crowd voice synthesis.

Voice model: Rosenberg/LF-style glottal pulse (2x oversampled) with jitter + shimmer +
pulsed aspiration noise -> time-varying 5-formant Klatt cascade. Syllables have real
consonant onsets (h, y, w, d, b, m, ʔ), vowel glides, effort-dependent brightness and
shout / sung / sigh pitch contours. Crowds layer many such singers with individual
timing, tuning, formant scale, breathiness and placement.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'soundtracks', 'src'))
import studio
studio.SR = 48000
from studio import *          # noqa  (SR is now 48000 everywhere)
from studio import _harm_sum  # noqa
import numpy as np
from numba import njit
from scipy.signal import resample_poly

SR = 48000
BPM = 150.0
SPB = 60.0 / BPM          # 0.4 s
BAR = 4 * SPB             # 1.6 s
DUR = 65.0
TOTAL_BEATS = DUR / SPB   # 162.5


# ============================================================ numba kernels
@njit(cache=True)
def _glottal(f0, oq, amp, sr, seed, jitter, shimmer):
    np.random.seed(seed)
    N = f0.shape[0]
    out = np.zeros(N)
    ph = 0.0
    a_cur = 1.0
    jit = 0.0
    for n in range(N):
        f = f0[n] * (1.0 + jit)
        ph += f / sr
        if ph >= 1.0:
            ph -= 1.0
            a_cur = 1.0 + shimmer * np.random.randn()
            jit = jitter * np.random.randn()
        o = oq[n]
        op = o * 0.62
        if ph < op:
            g = 0.5 * (1.0 - np.cos(np.pi * ph / op))
        elif ph < o:
            g = np.cos(0.5 * np.pi * (ph - op) / (o - op))
        else:
            g = 0.0
        out[n] = g * a_cur * amp[n]
    # derivative of glottal flow = excitation
    d = np.zeros(N)
    for n in range(1, N):
        d[n] = out[n] - out[n - 1]
    return d, out


@njit(cache=True)
def _cascade(x, F, BW, sr):
    nf = F.shape[0]
    N = x.shape[0]
    y = x.copy()
    for k in range(nf):
        y1 = 0.0
        y2 = 0.0
        for n in range(N):
            c = -np.exp(-2.0 * np.pi * BW[k, n] / sr)
            b = 2.0 * np.exp(-np.pi * BW[k, n] / sr) * np.cos(2.0 * np.pi * F[k, n] / sr)
            a = 1.0 - b - c
            v = a * y[n] + b * y1 + c * y2
            y2 = y1
            y1 = v
            y[n] = v
    return y


@njit(cache=True)
def _onepole(x, a):
    y = np.zeros_like(x)
    s = 0.0
    for n in range(x.shape[0]):
        s = a * s + (1 - a) * x[n]
        y[n] = s
    return y


# ============================================================ vowels
VOWELS = {   # male formants F1..F5 (Hz) and bandwidths
    'a': ([740, 1180, 2500, 3350, 4100], [90, 110, 150, 220, 300]),
    'e': ([470, 1900, 2550, 3350, 4100], [70, 100, 140, 220, 300]),
    'i': ([290, 2250, 2950, 3450, 4100], [60, 100, 140, 220, 300]),
    'o': ([520, 860, 2450, 3300, 4100], [80, 90, 140, 220, 300]),
    'u': ([330, 760, 2300, 3200, 4100], [60, 80, 130, 220, 300]),
    'E': ([620, 1720, 2500, 3350, 4100], [80, 100, 140, 220, 300]),
    '@': ([520, 1450, 2500, 3350, 4100], [80, 100, 140, 220, 300]),
    'm': ([260, 1050, 2200, 3300, 4100], [120, 400, 400, 400, 400]),
}


def syllable(rng, cons, vowels, midi0, dur, contour='shout', effort=0.7, female=False, fscale=1.0,
             midi1=None, breath=0.12, vib=0.0, sr=SR):
    """One sung/shouted syllable -> mono float array.
    cons: '', 'h', 'y', 'w', 'd', 'b', 'm', 'ʔ'.  vowels: e.g. 'ei' (HEY), 'a' (HA), 'ou' (HO), 'u' (OOH).
    contour: 'shout' (effort rise then drop), 'sung' (scoop + hold), 'fall' (oooh glide down), 'rise', 'laugh'."""
    os_ = 2
    srr = sr * os_
    pre = {'h': 0.055, 'y': 0.0, 'w': 0.0, 'd': 0.012, 'b': 0.012, 'm': 0.05, 'ʔ': 0.0, '': 0.0}[cons]
    tail = 0.09
    N = int((pre + dur + tail) * srr)
    t = np.arange(N) / srr
    tv = np.clip((t - pre) / max(dur, 1e-3), 0, 1)       # 0..1 across the voiced part
    # --- pitch contour (midi)
    m1 = midi0 if midi1 is None else midi1
    p = midi0 + (m1 - midi0) * tv
    if contour == 'shout':
        p += 1.8 * smoothstep(0, 0.25, tv) - 4.5 * smoothstep(0.55, 1.0, tv) ** 1.5 - 1.5 * np.exp(-(t - pre).clip(0) / 0.03)
    elif contour == 'sung':
        p += -0.9 * np.exp(-(t - pre).clip(0) / 0.045) - 0.6 * smoothstep(0.85, 1.0, tv)
    elif contour == 'fall':
        p += 2.0 * np.exp(-(t - pre).clip(0) / 0.06) - 6.0 * smoothstep(0.2, 1.0, tv)
    elif contour == 'rise':
        p += -3 + 6.0 * smoothstep(0.0, 0.9, tv)
    elif contour == 'laugh':
        p += 2.5 * (np.sin(2 * np.pi * 7 * t) > 0)
    p += vib * smoothstep(0.15, 0.4, t - pre) * np.sin(2 * np.pi * 5.4 * t + rng.uniform(0, 6))
    p += 0.15 * _onepole(rng.standard_normal(N), np.exp(-1 / (0.05 * srr))) * 8   # slow wander
    f0 = mtof(p) * (2.0 if female else 1.0)
    # --- voicing amplitude
    att = {'h': 0.03, 'y': 0.02, 'w': 0.03, 'd': 0.006, 'b': 0.006, 'm': 0.02, 'ʔ': 0.004, '': 0.015}[cons]
    voiced = smoothstep(pre - 0.01, pre + att, t)
    if contour == 'shout':
        rel = smoothstep(pre + dur * 0.55, pre + dur + 0.03, t)
        voiced *= 1 - rel * 0.97
    else:
        voiced *= 1 - smoothstep(pre + dur - 0.03, pre + dur + 0.05, t)
    if contour == 'laugh':
        voiced *= 0.45 + 0.55 * (np.sin(2 * np.pi * 7 * t) > -0.3)
    if cons == 'm':
        voiced = np.maximum(voiced, 0.35 * smoothstep(0, 0.02, t) * (t < pre + 0.01))
    # --- glottal source; effort -> shorter open quotient = brighter
    oq = np.full(N, 0.72 - 0.3 * effort) + 0.08 * (1 - voiced)
    src, flow = _glottal(f0, oq, voiced, srr, int(rng.integers(1e9)), 0.006, 0.05)
    src *= 60.0 / np.sqrt(np.maximum(f0, 60) / 120)      # level-normalise across pitch
    # aspiration (pulsed with the glottis) + pre-aspiration for /h/
    nz = rng.standard_normal(N)
    asp = nz * (0.25 + 0.75 * flow) * voiced * breath * (1.2 if female else 1.0) * 3.0
    if cons == 'h':
        hamp = smoothstep(0, 0.02, t) * (1 - smoothstep(pre - 0.005, pre + 0.03, t))
        asp += nz * hamp * (0.9 + 0.8 * effort) * 1.6
    exc = src + asp
    # --- formant trajectories
    path = vowels
    if cons == 'y':
        path = 'i' + vowels
    elif cons == 'w':
        path = 'u' + vowels
    elif cons == 'm':
        path = 'm' + vowels
    k = len(path)
    pos = np.clip((t - pre + (0.04 if cons in 'yw' else 0)) / max(dur * (0.6 if k > 1 else 1), 1e-3), 0, 1) * (k - 1)
    if cons in ('y', 'w', 'm'):   # fast consonant transition, then remaining vowel glide
        pos = np.where(t - pre < 0.07, smoothstep(0, 0.07, t - pre) * 1.0,
                       1 + np.clip((t - pre - 0.07) / max(dur * 0.6, 1e-3), 0, 1) * (k - 2)) if k > 1 else pos
    i0 = np.floor(pos).astype(int).clip(0, k - 1)
    i1 = (i0 + 1).clip(0, k - 1)
    fr = pos - i0
    Ft = np.array([VOWELS[c][0] for c in path], dtype=float)
    Bt = np.array([VOWELS[c][1] for c in path], dtype=float)
    F = (Ft[i0].T * (1 - fr) + Ft[i1].T * fr)
    BW = (Bt[i0].T * (1 - fr) + Bt[i1].T * fr)
    fs = fscale * (1.16 if female else 1.0)
    F = F * fs
    F[0] *= 1 + 0.18 * effort                     # shouting opens the jaw: F1 up
    F[0] = np.maximum(F[0], f0 * 1.05)            # F1 tracks high pitches
    F = np.minimum(F, srr * 0.45)
    if cons in ('d', 'b'):
        burst = (hp(nz, 2500 if cons == 'd' else 300, 0.7) if True else nz) * np.exp(-np.clip(t - pre + 0.012, 0, None) / 0.004) * (t < pre + 0.01) * 2.0
        exc = exc + burst
    y = _cascade(exc.astype(np.float64), F.astype(np.float64), BW.astype(np.float64), float(srr))
    # gentle lip radiation (+6 dB/oct) already in derivative; tame the extreme top
    y = resample_poly(y, 1, os_)
    y = hp(y, 90)
    pk = np.abs(y).max() + 1e-9
    return y / pk * (0.55 + 0.45 * effort)


def crowd(rng, cons, vowels, midi0, dur, n_m=6, n_f=4, spread=0.016, contour='shout', effort=0.8,
          detune=0.18, midi1=None, vib=0.0, width=0.9, breath=0.14, oct_f=True, solo=None):
    """Village group: returns stereo (2, N)."""
    total = int((dur + 0.5) * SR)
    out = np.zeros((2, total))
    singers = [(False, i) for i in range(n_m)] + [(True, i) for i in range(n_f)]
    for female, i in singers:
        d = max(0.0, rng.normal(spread, spread * 0.8))
        m = midi0 + rng.normal(0, detune) - (12 if (female and oct_f) else 0)
        mm1 = None if midi1 is None else midi1 + (m - midi0)
        y = syllable(rng, cons, vowels, m, dur * rng.uniform(0.9, 1.08), contour, effort * rng.uniform(0.85, 1.1),
                     female, rng.uniform(0.93, 1.07), mm1, breath * rng.uniform(0.7, 1.4), vib)
        pan = rng.uniform(-width, width)
        gl, gr = pan_gains(pan)
        g = rng.uniform(0.7, 1.0)
        i0 = int(d * SR)
        n = min(len(y), total - i0)
        out[0, i0:i0 + n] += y[:n] * gl * g
        out[1, i0:i0 + n] += y[:n] * gr * g
    out /= np.sqrt(n_m + n_f)
    return out


def write_wav24(path, x, sr=SR):
    import wave
    y = np.clip(x, -1, 1)
    if y.ndim == 1:
        y = np.stack([y, y])
    q = (y.T.reshape(-1) * 8388607).astype('<i4')
    b = q.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(sr)
        w.writeframes(b)
