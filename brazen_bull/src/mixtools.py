"""Mixing / mastering processors: compressor, sidechain pump, true-peak limiter,
loudness metering helpers."""
import numpy as np
from numba import njit
from scipy import signal
from dsp import SR, lp, hp, to_st


@njit(cache=True, fastmath=True)
def _comp_gain(det, thr, ratio, knee, att_c, rel_c):
    n = det.shape[0]
    g = np.empty(n)
    env = 0.0
    for i in range(n):
        lvl = 20.0 * np.log10(det[i] + 1e-9)
        over = lvl - thr
        if over <= -knee * 0.5:
            gr = 0.0
        elif over < knee * 0.5:
            gr = (1.0 / ratio - 1.0) * (over + knee * 0.5) ** 2 / (2.0 * knee)
        else:
            gr = (1.0 / ratio - 1.0) * over
        if gr < env:
            env = att_c * env + (1.0 - att_c) * gr
        else:
            env = rel_c * env + (1.0 - rel_c) * gr
        g[i] = 10.0 ** (env / 20.0)
    return g


def compress(x, thr=-18.0, ratio=3.0, att=0.005, rel=0.12, knee=6.0, makeup=0.0, rms_ms=5.0, key=None):
    x = to_st(x)
    k = x if key is None else to_st(key)
    det = np.max(np.abs(k), axis=0)
    if rms_ms > 0:
        a = np.exp(-1.0 / (rms_ms * 1e-3 * SR))
        det = np.sqrt(signal.lfilter([1 - a], [1, -a], det ** 2))
    att_c = np.exp(-1.0 / (att * SR))
    rel_c = np.exp(-1.0 / (rel * SR))
    g = _comp_gain(np.ascontiguousarray(det), thr, ratio, knee, att_c, rel_c)
    return x * g * 10 ** (makeup / 20.0), g


def pump_env(n, times, depth, rel, shape=2.0, att=0.0015):
    g = np.ones(n)
    L = int(rel * SR)
    curve = 1 - depth * (1 - np.linspace(0, 1, L)) ** shape
    A = max(int(att * SR), 1)
    for t in times:
        i0 = int(round(t * SR)) - A
        if i0 >= n:
            continue
        seg = np.concatenate([np.linspace(1, curve[0], A), curve])
        s0 = max(i0, 0)
        seg = seg[s0 - i0:]
        e = min(n, s0 + len(seg))
        g[s0:e] = np.minimum(g[s0:e], seg[:e - s0])
    return g


@njit(cache=True, fastmath=True)
def _release(gr, rel_c):
    n = gr.shape[0]
    out = np.empty(n)
    env = 1.0
    for i in range(n):
        t = gr[i]
        if t < env:
            env = t
        else:
            env = rel_c * env + (1.0 - rel_c) * t
        out[i] = env
    return out


@njit(cache=True, fastmath=True)
def _fwd_min(x, L):
    n = x.shape[0]
    out = np.empty(n)
    # simple O(n*L) with small L
    for i in range(n):
        m = x[i]
        e = i + L
        if e > n:
            e = n
        for j in range(i, e):
            if x[j] < m:
                m = x[j]
        out[i] = m
    return out


def true_peak_env(x, os=4):
    up = signal.resample_poly(x, os, 1, axis=-1)
    a = np.max(np.abs(up), axis=0)
    a = a[: (len(a) // os) * os].reshape(-1, os).max(axis=1)
    n = x.shape[1]
    if len(a) < n:
        a = np.pad(a, (0, n - len(a)))
    return a[:n]


def true_peak_db(x, os=4):
    up = signal.resample_poly(to_st(x), os, 1, axis=-1)
    return 20 * np.log10(np.max(np.abs(up)) + 1e-12)


def limiter(x, ceiling_db=-1.2, look_ms=1.5, rel_ms=90.0):
    x = to_st(x)
    ceil = 10 ** (ceiling_db / 20)
    pk = true_peak_env(x)
    gr = np.minimum(1.0, ceil / (pk + 1e-12))
    L = max(int(look_ms * 1e-3 * SR), 2)
    g = _release(gr, np.exp(-1.0 / (rel_ms * 1e-3 * SR)))
    g = _fwd_min(g, L)
    g = signal.lfilter(np.ones(L) / L, [1.0], g, zi=signal.lfiltic(np.ones(L) / L, [1.0], [], x=np.full(L, g[0])))[0]
    return x * g, g


def lr4_split(x, fc):
    sos = signal.butter(2, fc, btype="low", fs=SR, output="sos")
    low = signal.sosfilt(sos, signal.sosfilt(sos, x, axis=-1), axis=-1)
    return low, x - low
