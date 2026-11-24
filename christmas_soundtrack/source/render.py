"""Render + mix engine for THE DARKEST CHRISTMAS LEGENDS."""
import os, sys, subprocess, random, importlib
import numpy as np, soundfile as sf, mido
from numba import njit
from concurrent.futures import ThreadPoolExecutor
import pedalboard as pb
import scipy.signal as ss

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compose; importlib.reload(compose)
from compose import EV, BASS, MARK, GLIDES, RISER, B

SR = 48000; BPM = 128; STEP = 60 / BPM / 4
N = int(round(90 * SR)); PAD = SR * 3
SWING = 0.07 * STEP
WORK = os.path.join(HERE, 'work'); os.makedirs(WORK, exist_ok=True)
MSG = '/usr/share/sounds/sf2/MuseScore_General_Full.sf2'
AVL = '/usr/share/sounds/sf2/Black_Pearl_4_LV2.sf2'
rng = np.random.default_rng(2026)

def st2t(step, swing=True):
    t = step * STEP
    if swing and abs(step - round(step)) < 1e-6 and int(round(step)) % 2 == 1: t += SWING
    return t

def buf(): return np.zeros((2, N + PAD), np.float32)

def place(out, x, t, gain=1.0, pan=0.0):
    i = max(0, int(round(t * SR)))
    if x.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2); r = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
        x = np.stack([x * l, x * r])
    n = min(x.shape[1], out.shape[1] - i)
    if n > 0: out[:, i:i + n] += gain * x[:, :n]

# ======================================================== numba DSP primitives
@njit(cache=True)
def saw_blep(freq, sr, phase0):
    n = freq.shape[0]; out = np.zeros(n); ph = phase0
    for i in range(n):
        dt = freq[i] / sr
        v = 2.0 * ph - 1.0
        if ph < dt:
            t = ph / dt; v -= t + t - t * t - 1.0
        elif ph > 1.0 - dt:
            t = (ph - 1.0) / dt; v -= t * t + t + t + 1.0
        out[i] = v
        ph += dt
        if ph >= 1.0: ph -= 1.0
    return out

@njit(cache=True)
def svf(x, fc, q, sr, mode):
    n = x.shape[0]; out = np.zeros(n); ic1 = 0.0; ic2 = 0.0; k = 1.0 / q
    for i in range(n):
        f = fc[i]
        if f > sr * 0.45: f = sr * 0.45
        if f < 10.0: f = 10.0
        g = np.tan(np.pi * f / sr)
        a1 = 1.0 / (1.0 + g * (g + k)); a2 = g * a1; a3 = g * a2
        v3 = x[i] - ic2; v1 = a1 * ic1 + a2 * v3; v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1; ic2 = 2.0 * v2 - ic2
        if mode == 0: out[i] = v2
        elif mode == 1: out[i] = v1
        else: out[i] = x[i] - k * v1 - v2
    return out

def mtof(m): return 440.0 * 2 ** ((np.asarray(m, float) - 69) / 12)
def bp(x, lo, hi, order=2): return ss.sosfilt(ss.butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def hp(x, f, order=2): return ss.sosfilt(ss.butter(order, f, 'high', fs=SR, output='sos'), x)
def lp(x, f, order=2): return ss.sosfilt(ss.butter(order, f, 'low', fs=SR, output='sos'), x)

# ======================================================== synthesized drums
def kick_sample(v=1.0):
    t = np.arange(int(0.42 * SR)) / SR
    f = 49.0 + 150 * np.exp(-t / 0.026) + 380 * np.exp(-t / 0.004)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * (np.exp(-t / 0.19) * (t < 0.36) + 0.0) * (1 - np.exp(-t / 0.0006))
    body *= np.clip((0.42 - t) / 0.06, 0, 1)
    click = hp(rng.standard_normal(len(t)), 1800) * np.exp(-t / 0.0018) * 0.35
    knock = np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.012) * 0.25
    x = np.tanh(1.8 * (body + click + knock)) * 0.95
    return (x * v).astype(np.float32)

def clap_sample(v=1.0):
    L = int(0.35 * SR); t = np.arange(L) / SR; n = rng.standard_normal(L)
    env = np.zeros(L)
    for k, off in enumerate((0.0, 0.008, 0.017, 0.026)):
        tt = t - off; env += (tt >= 0) * np.exp(-np.clip(tt, 0, None) / 0.0035) * (0.8 if k < 3 else 1.0)
    tt = t - 0.026; env += (tt >= 0) * np.exp(-np.clip(tt, 0, None) / 0.10) * 0.55
    x = bp(n * env, 950, 5200, 2)
    body = np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.03) * 0.35
    x = x / (np.abs(x).max() + 1e-9) + body
    return (np.tanh(1.3 * x) * v).astype(np.float32)

HAT_F = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0]) * 1.32
def hat_sample(v=1.0, open_=False):
    L = int((0.35 if open_ else 0.08) * SR); t = np.arange(L) / SR
    m = sum(np.sign(np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))) for f in HAT_F)
    x = bp(m * 0.25 + rng.standard_normal(L) * 0.6, 7000, 13500, 2)
    dec = 0.16 if open_ else 0.022
    x *= np.exp(-t / dec) * (1 - np.exp(-t / 0.0004))
    x = x / (np.abs(x).max() + 1e-9)
    return (x * v * 0.9).astype(np.float32)

def stomp_sample(v=1.0):
    L = int(0.3 * SR); t = np.arange(L) / SR
    f = 62 + 70 * np.exp(-t / 0.02)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    wood = lp(rng.standard_normal(L), 900, 2) * np.exp(-t / 0.035) * 1.6
    slap = bp(rng.standard_normal(L), 1500, 4000) * np.exp(-t / 0.006) * 0.5
    x = np.tanh(1.5 * (thump + wood + slap))
    return (x * v).astype(np.float32)

BELL_P = np.array([2630., 3910., 4870., 5980., 7110., 8320.])
def jingle(st, amp, pan_rng=0.9):
    """one sleigh-bell shake = cluster of small jingles (stereo)"""
    L = int(0.25 * SR); out = np.zeros((2, L + int(0.05 * SR)))
    nj = rng.integers(7, 13)
    for _ in range(nj):
        off = abs(rng.normal(0, 0.007)); i = int(off * SR)
        t = np.arange(L) / SR
        base = rng.uniform(0.93, 1.07)
        x = np.zeros(L)
        for p in BELL_P:
            fr = p * base * rng.uniform(0.985, 1.015)
            x += np.sin(2 * np.pi * fr * t + rng.uniform(0, 6.28)) * np.exp(-t / rng.uniform(0.025, 0.075)) * rng.uniform(0.3, 1)
        x *= (1 - np.exp(-t / 0.0005))
        pan = rng.uniform(-pan_rng, pan_rng)
        out[0, i:i + L] += x * np.cos((pan + 1) * np.pi / 4)
        out[1, i:i + L] += x * np.sin((pan + 1) * np.pi / 4)
    rattle = bp(rng.standard_normal(out.shape[1]), 4000, 10000) * np.exp(-np.arange(out.shape[1]) / SR / 0.03) * 0.8
    out += rattle
    out /= (np.abs(out).max() + 1e-9)
    return (out * amp).astype(np.float32)

# ======================================================== bass synth
def render_bass():
    n = N + PAD
    freq = np.full(n, mtof(38)); gate = np.zeros(n); tsince = np.full(n, 10.0); velarr = np.zeros(n)
    ev = sorted(BASS, key=lambda e: e[0])
    prev = None
    for k, (s, d, p, v, sl) in enumerate(ev):
        t0 = st2t(s); i0 = int(round(t0 * SR)); i1 = min(n, int(round((t0 + d * STEP * 0.92) * SR)))
        f = mtof(p)
        seg = np.full(i1 - i0, f)
        if prev is not None and ev[k - 1][4] == 1 and False: pass
        # slide: if *previous* note asked to slide into this one, glide from previous pitch
        if k > 0 and ev[k - 1][4] == 1:
            fp = mtof(ev[k - 1][2]); gl = min(len(seg), int(0.06 * SR))
            seg[:gl] = fp * (f / fp) ** (np.arange(gl) / gl)
        freq[i0:i1] = seg; gate[i0:i1] = 1.0; tsince[i0:i1] = np.arange(i1 - i0) / SR; velarr[i0:i1] = v
        # sliding note itself also bends up at its end into next note handled by next note
        prev = p
    # amp envelope smoothing (2ms attack, 25ms release) via one-pole
    a = np.zeros(n); y = 0.0
    att = 1 - np.exp(-1 / (0.0015 * SR)); rel = 1 - np.exp(-1 / (0.02 * SR))
    a = _env_follow(gate * velarr, att, rel)
    saw = saw_blep(freq, SR, 0.0) + 0.55 * saw_blep(freq * 1.004, SR, 0.3)
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(freq / 2) / SR)) * 0.25
    raw = saw + sq
    cutoff = 140 + 2600 * np.exp(-tsince / 0.075) * (0.5 + 0.5 * velarr) + 220
    mid = svf(raw, cutoff, 1.6, SR, 0)
    mid = np.tanh(2.2 * mid) * a
    sub = np.sin(2 * np.pi * np.cumsum(freq) / SR) * a
    return mid.astype(np.float32), sub.astype(np.float32)

@njit(cache=True)
def _env_follow(x, att, rel):
    out = np.zeros(x.shape[0]); y = 0.0
    for i in range(x.shape[0]):
        c = att if x[i] > y else rel
        y += c * (x[i] - y); out[i] = y
    return out

# ======================================================== pluck lead (supersaw-ish)
def render_pluck(events):
    out = buf()
    for (s, d, p, v) in events:
        t0 = st2t(s); dur = d * STEP * 0.95; L = int((dur + 0.25) * SR); t = np.arange(L) / SR
        f = np.full(L, mtof(p))
        voices = []
        for det, ph in ((-0.11, 0.1), (0.0, 0.5), (0.11, 0.8)):
            voices.append(saw_blep(f * 2 ** (det / 12), SR, ph))
        sub = np.sin(2 * np.pi * f * t) * 0.4
        cut = 500 + 5200 * v * np.exp(-t / 0.10) + 600
        env = np.minimum(1, t / 0.002) * (0.35 + 0.65 * np.exp(-t / 0.16))
        env *= np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.05))
        Lx = svf(voices[0] * 0.8 + voices[1] * 0.5 + sub, cut, 0.9, SR, 0) * env
        Rx = svf(voices[2] * 0.8 + voices[1] * 0.5 + sub, cut, 0.9, SR, 0) * env
        place(out, np.stack([Lx, Rx]).astype(np.float32), t0, v * 0.5)
    return out

# ======================================================== cat glide lead
def render_glides():
    out = buf()
    for (s0, pts, dur) in GLIDES:
        t0 = st2t(s0, False); L = int((dur * STEP + 0.3) * SR); t = np.arange(L) / SR
        ts = np.array([q[0] * STEP for q in pts]); ms = np.array([q[1] for q in pts], float)
        # smooth (cosine) interpolation of pitch between points => sung portamento
        m = np.interp(t, ts, ms)
        m = lp(m - m[0], 18, 2) + m[0]
        vib = 0.18 * np.sin(2 * np.pi * 5.6 * t) * np.clip(t / 0.25, 0, 1)
        f = mtof(m + vib)
        ph = 2 * np.pi * np.cumsum(f) / SR
        tri = 2 / np.pi * np.arcsin(np.sin(ph)) + 0.25 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
        form = 700 + 1800 * np.clip((m - 66) / 16, 0, 1)
        x = tri * 0.7 + svf(saw_blep(f, SR, 0.0), form, 4.0, SR, 1) * 0.6
        env = np.minimum(1, t / 0.03) * np.where(t < dur * STEP, 1.0, np.exp(-(t - dur * STEP) / 0.06))
        place(out, (x * env).astype(np.float32), t0, 0.55, 0.0)
    return out

# ======================================================== riser
def render_riser():
    out = buf(); s0, s1 = RISER; t0 = st2t(s0, False); t1 = st2t(s1, False)
    L = int((t1 - t0) * SR); t = np.arange(L) / SR; r = t / t[-1]
    fc = 300 * (12000 / 300) ** (r ** 1.6)
    nl = svf(rng.standard_normal(L), fc, 2.5, SR, 1); nr = svf(rng.standard_normal(L), fc * 1.03, 2.5, SR, 1)
    amp = (r ** 2.2) * 0.5
    place(out, np.stack([nl * amp, nr * amp]).astype(np.float32), t0)
    return out

# ======================================================== soundfont renders
GM = {  # track: list of (sf2, bank, prog, channel, transpose, gain, humanize_ms, legato)
    'glock':     [(MSG, 0, 9, 0, 12, 1.0, 3, 0.9), (MSG, 0, 8, 0, 0, 0.35, 3, 0.9)],
    'pizz':      [(MSG, 20, 45, 0, 0, 1.0, 4, 0.9), (MSG, 30, 45, 0, 0, 0.35, 4, 0.9)],
    'fiddle':    [(MSG, 0, 110, 0, 0, 1.0, 6, 0.98), (MSG, 0, 40, 0, 0, 0.6, 7, 0.98)],
    'brass_lo':  [(MSG, 0, 61, 0, 0, 1.0, 6, 0.9), (MSG, 0, 57, 0, 0, 0.7, 6, 0.9)],
    'brass_hi':  [(MSG, 0, 56, 0, 0, 1.0, 5, 0.9)],
    'accordion': [(MSG, 8, 21, 0, 0, 1.0, 5, 0.85)],
    'lute':      [(MSG, 16, 25, 0, 0, 1.0, 5, 0.9), (MSG, 0, 24, 0, 0, 0.5, 6, 0.9)],
    'harp':      [(MSG, 0, 46, 0, 0, 1.0, 4, 1.0)],
    'bells':     [(MSG, 0, 14, 0, 0, 1.0, 2, 1.0)],
    'choir':     [(MSG, 0, 53, 0, 0, 1.0, 10, 1.0)],
    'celesta':   [(MSG, 0, 8, 0, 0, 1.0, 3, 0.9)],
    'strings':   [(MSG, 0, 48, 0, 0, 1.0, 8, 1.0), (MSG, 0, 49, 0, 0, 0.5, 8, 1.0)],
    'crash':     [(MSG, 128, 0, 9, 0, 1.0, 0, 1.0)],
    'tom':       [(AVL, 0, 0, 0, 0, 1.0, 3, 1.0)],
    'tamb':      [(MSG, 128, 0, 9, 0, 1.0, 3, 1.0)],
    'shaker':    [(MSG, 128, 0, 9, 0, 1.0, 3, 1.0)],
    'wood':      [(MSG, 128, 0, 9, 0, 1.0, 2, 1.0)],
    'snare':     [(AVL, 0, 0, 0, 0, 1.0, 2, 1.0)],
    'clapgm':    [(MSG, 128, 0, 9, 0, 1.0, 1, 1.0)],
}
TPB = 960
def tick(t): return int(round(t / (60 / BPM) * TPB))

def write_mid(fn, events, bank, prog, ch, transpose, hum_ms, legato, strum=0.0):
    mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo', tempo=int(60e6 / BPM)))
    msgs = []
    if ch != 9:
        msgs += [(0, mido.Message('control_change', channel=ch, control=0, value=bank)),
                 (0, mido.Message('program_change', channel=ch, program=prog))]
    msgs.append((0, mido.Message('control_change', channel=ch, control=7, value=110)))
    msgs.append((0, mido.Message('control_change', channel=ch, control=91, value=0)))
    msgs.append((0, mido.Message('control_change', channel=ch, control=93, value=0)))
    r = random.Random(hash((fn, prog)) & 0xffff)
    # chord strum: notes with same start get small offsets
    by_start = {}
    for e in events: by_start.setdefault(e[0], []).append(e)
    for s, grp in by_start.items():
        grp = sorted(grp, key=lambda e: e[2])
        for j, (s_, d, p, v) in enumerate(grp):
            t = st2t(s_) + r.gauss(0, hum_ms / 1000) + j * strum
            t = max(0.0, t)
            vel = int(np.clip(28 + v * 99 * r.uniform(0.93, 1.05), 1, 127))
            t_off = t + d * STEP * legato
            pp = p + transpose
            if ch != 9 and not (0 <= pp < 128): continue
            msgs.append((tick(t) + 2, mido.Message('note_on', channel=ch, note=pp, velocity=vel)))
            msgs.append((tick(t_off), mido.Message('note_off', channel=ch, note=pp, velocity=0)))
    msgs.sort(key=lambda m: (m[0], 0 if m[1].type in ('control_change', 'program_change') else (1 if m[1].type == 'note_off' else 2)))
    last = 0
    for tk, m in msgs:
        m.time = max(0, tk - last); last = max(last, tk); tr.append(m)
    mid.save(fn)

def fluid(mid, wav, sf2):
    subprocess.run(['fluidsynth', '-ni', '-q', '-R', '0', '-C', '0', '-g', '0.6', '-r', str(SR), '-O', 'float',
                    '-T', 'wav', '-F', wav, sf2, mid], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, _ = sf.read(wav, dtype='float32'); y = y.T
    out = np.zeros((2, N + PAD), np.float32); n = min(y.shape[1], N + PAD); out[:, :n] = y[:, :n]
    return out

def render_gm(name, events):
    layers = GM[name]; jobs = []
    for li, (sf2, bank, prog, ch, trn, g, hum, leg) in enumerate(layers):
        mf = os.path.join(WORK, f'{name}_{li}.mid'); wf = os.path.join(WORK, f'{name}_{li}.wav')
        strum = 0.007 if name in ('lute', 'accordion', 'harp') else 0.0
        evs = events
        if name == 'snare': evs = [(s, d, 38, v) for (s, d, p, v) in events]
        write_mid(mf, evs, bank, prog, ch, trn, hum, leg, strum)
        jobs.append((mf, wf, sf2, g))
    out = np.zeros((2, N + PAD), np.float32)
    for mf, wf, sf2, g in jobs: out += g * fluid(mf, wf, sf2)
    return name, out

# ======================================================== build all raw tracks
def build_raw():
    T = {}
    # synth drums
    for name, fn, vv in (('kick', kick_sample, 1.0), ('clapsyn', clap_sample, 1.0), ('stomp', stomp_sample, 1.0)):
        out = buf(); src = 'clap' if name == 'clapsyn' else name
        cache = {}
        for (s, d, p, v) in EV.get(src, []):
            x = fn(1.0) if name != 'kick' else cache.setdefault('k', fn(1.0))
            place(out, x, st2t(s) + (0.0 if name == 'kick' else rng.normal(0, 0.0015)), v * vv, 0.0)
        T[name] = out
    for name, op in (('hat', False), ('ohat', True)):
        out = buf()
        for (s, d, p, v) in EV.get(name, []):
            place(out, hat_sample(1.0, op), st2t(s) + rng.normal(0, 0.0015), v * rng.uniform(0.9, 1.05),
                  0.25 if not op else -0.2)
        T[name] = out
    out = buf()
    for (s, d, p, v) in EV.get('sleigh', []):
        place(out, jingle(s, 1.0), st2t(s) + rng.normal(0, 0.003) - 0.004, v * rng.uniform(0.85, 1.05))
    T['sleigh'] = out
    T['pluck'] = render_pluck(EV.get('pluck', []))
    T['glide'] = render_glides()
    T['riser'] = render_riser()
    mid, sub = render_bass()
    T['bass'] = np.stack([mid, mid]); T['sub'] = np.stack([sub, sub])
    # GM
    gm_ev = {k: EV[k] for k in GM if k in EV}
    gm_ev['clapgm'] = [(s, d, 39, v * 0.8) for (s, d, p, v) in EV['clap']]
    with ThreadPoolExecutor(4) as ex:
        for name, out in ex.map(lambda kv: render_gm(*kv), gm_ev.items()):
            T[name] = out
    return T

# ======================================================== mixing
def sidechain_env(depth, rel=0.11, hold=0.0):
    env = np.ones(N + PAD, np.float32)
    t = np.arange(int(0.4 * SR)) / SR
    shape = 1 - depth * np.where(t < 0.003, t / 0.003, np.exp(-np.clip(t - 0.003 - hold, 0, None) / rel))
    for (s, d, p, v) in EV['kick']:
        i = int(round(st2t(s) * SR)); n = min(len(shape), env.size - i)
        env[i:i + n] = np.minimum(env[i:i + n], shape[:n])
    return env

def norm(x, peak=0.5):
    m = np.abs(x).max(); return x if m < 1e-9 else x * (peak / m)

def fx(x, chain): return pb.Pedalboard(chain)(x, SR)

def panst(x, pan, width=1.0):
    m = (x[0] + x[1]) / 2; s = (x[0] - x[1]) / 2 * width
    l = m + s; r = m - s
    gl = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2); gr = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    return np.stack([l * gl, r * gr]).astype(np.float32)

def mix(T, gains=None):
    G = dict(kick=0.95, clapsyn=0.42, clapgm=0.22, snare=0.40, hat=0.16, ohat=0.12, shaker=0.20, tamb=0.22,
             stomp=0.42, wood=0.28, tom=0.45, crash=0.20, sleigh=0.20,
             bass=0.36, sub=0.55, pluck=0.30, glide=0.36, glock=0.42, fiddle=0.50, pizz=0.48, accordion=0.28,
             lute=0.30, brass_lo=0.40, brass_hi=0.30, harp=0.20, bells=0.26, choir=0.22, celesta=0.20,
             strings=0.26, riser=0.16)
    if gains: G.update(gains)
    sc_hard = sidechain_env(0.72, 0.075); sc_med = sidechain_env(0.45, 0.12); sc_soft = sidechain_env(0.22, 0.12)
    S = {}
    def P(name): return norm(T[name], 0.7)
    # --- drums
    S['kick'] = fx(P('kick'), [pb.HighpassFilter(28), pb.LowShelfFilter(60, 1.5), pb.PeakFilter(320, -3, 1.0)])
    S['clapsyn'] = panst(fx(P('clapsyn'), [pb.HighpassFilter(250), pb.Compressor(-14, 3, 2, 80)]), 0)
    S['clapgm'] = panst(fx(P('clapgm'), [pb.HighpassFilter(300)]), 0, 1.0)
    S['snare'] = fx(P('snare'), [pb.HighpassFilter(140), pb.PeakFilter(220, 2, 1.0), pb.PeakFilter(5000, 2, 0.8),
                                pb.Compressor(-16, 4, 3, 90), pb.Distortion(4)])
    S['hat'] = fx(P('hat'), [pb.HighpassFilter(5500)])
    S['ohat'] = fx(P('ohat'), [pb.HighpassFilter(5500), pb.HighShelfFilter(12000, -1)])
    S['shaker'] = panst(fx(P('shaker'), [pb.HighpassFilter(3500), pb.HighShelfFilter(11000, -3)]), -0.35)
    S['tamb'] = panst(fx(P('tamb'), [pb.HighpassFilter(2500), pb.HighShelfFilter(11000, -3)]), 0.4)
    S['stomp'] = fx(P('stomp'), [pb.HighpassFilter(45), pb.Compressor(-12, 3, 2, 80)])
    S['wood'] = panst(fx(P('wood'), [pb.HighpassFilter(400)]), -0.3, 1.0)
    S['tom'] = fx(P('tom'), [pb.HighpassFilter(70), pb.Compressor(-14, 3, 3, 90)])
    S['crash'] = fx(P('crash'), [pb.HighpassFilter(500), pb.HighShelfFilter(9000, -4)])
    S['sleigh'] = fx(P('sleigh'), [pb.HighpassFilter(1800), pb.LowpassFilter(15000), pb.PeakFilter(4500, 1.5, 1.0)])
    # --- bass
    S['bass'] = fx(P('bass'), [pb.HighpassFilter(85), pb.PeakFilter(700, 2.5, 1.0), pb.Compressor(-12, 3, 3, 60)]) * sc_hard
    S['sub'] = fx(P('sub'), [pb.LowpassFilter(130), pb.HighpassFilter(30)]) * sc_hard
    # --- leads & folk
    S['pluck'] = fx(P('pluck'), [pb.HighpassFilter(250), pb.Chorus(0.6, 0.15, 7, 0.1, 0.25),
                                 pb.Compressor(-14, 3, 2, 80)]) * sc_soft
    S['glide'] = fx(P('glide'), [pb.HighpassFilter(300), pb.Delay(STEP * 3, 0.25, 0.2)])
    S['glock'] = panst(fx(P('glock'), [pb.HighpassFilter(600), pb.HighShelfFilter(9000, -2)]), 0.15, 1.0)
    S['fiddle'] = panst(fx(P('fiddle'), [pb.HighpassFilter(220), pb.PeakFilter(2800, 2.0, 1.0), pb.PeakFilter(450, -2, 1),
                                         pb.Compressor(-18, 3, 5, 100), pb.Distortion(3), pb.HighShelfFilter(10000, -3)]), -0.08, 1.0)
    S['pizz'] = panst(fx(P('pizz'), [pb.HighpassFilter(140), pb.PeakFilter(3000, 1.5, 1.0), pb.Compressor(-16, 3, 3, 80)]), 0.25, 1.2)
    S['accordion'] = panst(fx(P('accordion'), [pb.HighpassFilter(220), pb.LowpassFilter(7500), pb.Compressor(-16, 2.5, 5, 100)]) * sc_med, -0.4, 0.8)
    S['lute'] = panst(fx(P('lute'), [pb.HighpassFilter(200), pb.PeakFilter(3500, 2, 1.0), pb.Compressor(-16, 3, 3, 80)]) * sc_soft, 0.42, 0.8)
    S['brass_lo'] = fx(P('brass_lo'), [pb.HighpassFilter(70), pb.Compressor(-14, 3, 5, 90), pb.Distortion(5),
                                       pb.LowpassFilter(7000)]) * sc_med
    S['brass_hi'] = panst(fx(P('brass_hi'), [pb.HighpassFilter(250)]), 0.3)
    S['harp'] = panst(fx(P('harp'), [pb.HighpassFilter(300)]), -0.2, 1.4)
    S['bells'] = fx(P('bells'), [pb.HighpassFilter(250), pb.HighShelfFilter(8000, -3)])
    S['choir'] = panst(fx(P('choir'), [pb.HighpassFilter(220), pb.LowpassFilter(8000)]) * sc_med, 0, 1.5)
    S['celesta'] = panst(fx(P('celesta'), [pb.HighpassFilter(700), pb.Delay(STEP * 3, 0.3, 0.25)]), 0.3, 1.3)
    S['strings'] = panst(fx(P('strings'), [pb.HighpassFilter(180), pb.Compressor(-16, 2, 10, 150)]) * sc_med, 0, 1.4)
    S['riser'] = fx(P('riser'), [pb.HighpassFilter(300), pb.LowpassFilter(13000)])
    for k in S: S[k] = (S[k] * G[k]).astype(np.float32)
    # --- send buses
    room_send = {'snare': .18, 'clapsyn': .2, 'clapgm': .15, 'pizz': .18, 'lute': .12, 'accordion': .12, 'fiddle': .14,
                 'stomp': .1, 'wood': .12, 'tom': .15, 'tamb': .1, 'brass_lo': .1, 'sleigh': .1}
    hall_send = {'glock': .35, 'fiddle': .22, 'pluck': .18, 'glide': .3, 'bells': .5, 'celesta': .45, 'choir': .5,
                 'harp': .35, 'strings': .3, 'brass_hi': .25, 'pizz': .12, 'crash': .15, 'accordion': .1}
    room_in = sum(S[k] * v for k, v in room_send.items()); hall_in = sum(S[k] * v for k, v in hall_send.items())
    room = fx(room_in, [pb.HighpassFilter(250), pb.Reverb(0.35, 0.6, 1.0, 0.0, 1.0)])
    hall = fx(hall_in, [pb.HighpassFilter(350), pb.Reverb(0.78, 0.55, 1.0, 0.0, 1.0), pb.LowpassFilter(9000)])
    hall = hall * sidechain_env(0.35, 0.15)
    delay_in = S['pluck'] * 0.25 + S['glock'] * 0.12
    dl = fx(delay_in, [pb.HighpassFilter(500), pb.LowpassFilter(6000), pb.Delay(STEP * 3, 0.35, 1.0)])
    dl = np.stack([dl[0], np.roll(dl[1], int(STEP * SR))])
    S['_room'] = (room * G.get('_room', 1.0)).astype(np.float32); S['_hall'] = (hall * G.get('_hall', 1.0)).astype(np.float32)
    S['_delay'] = (dl * G.get('_delay', 1.0)).astype(np.float32)
    return S

GROUPS = {
    'DRUMS': ['kick', 'clapsyn', 'clapgm', 'snare', 'hat', 'ohat', 'shaker', 'tamb', 'stomp', 'wood', 'tom', 'crash'],
    'SLEIGH_BELLS': ['sleigh'],
    'BASS': ['bass', 'sub'],
    'HOOK_LEADS': ['fiddle', 'glock', 'pluck', 'glide'],
    'FOLK_ORCHESTRA': ['pizz', 'accordion', 'lute', 'harp', 'brass_lo', 'brass_hi', 'strings'],
    'BELLS_ATMOS': ['bells', 'celesta', 'choir', 'riser'],
    'FX_RETURNS': ['_room', '_hall', '_delay'],
}

@njit(cache=True)
def _gain_curve(det, ceil, W, rel):
    n = det.shape[0]; g_raw = np.empty(n)
    for i in range(n): g_raw[i] = min(1.0, ceil / max(det[i], 1e-9))
    g1 = np.empty(n)
    # forward-looking running minimum (window W)
    for i in range(n):
        m = 1.0
        for j in range(i, min(n, i + W)):
            if g_raw[j] < m: m = g_raw[j]
        g1[i] = m
    # release smoothing
    g = 1.0
    for i in range(n):
        if g1[i] < g: g = g1[i]
        else: g += rel * (g1[i] - g)
        g1[i] = g
    # backward moving average (length W) -> click-free attack that lands before the peak
    out = np.empty(n); acc = 0.0
    for i in range(n):
        acc += g1[i]
        if i >= W: acc -= g1[i - W]
        out[i] = acc / min(i + 1, W)
    return out

def tp_limit(x, ceiling_db=-1.0, look_ms=1.5, rel_ms=90):
    ceil = 10 ** (ceiling_db / 20) * 0.985
    up = ss.resample_poly(x, 4, 1, axis=1)
    det = np.abs(up).max(0).reshape(-1, 4).max(1)[:x.shape[1]]
    W = int(look_ms * 1e-3 * SR); rel = 1 - np.exp(-1 / (rel_ms * 1e-3 * SR))
    g = _gain_curve(det.astype(np.float64), ceil, W, rel)
    return (x * g).astype(np.float32), g

ENERGY_DB = {}  # bar -> dB pre-master automation
for b in range(1, 5): ENERGY_DB[b] = -2.5
for b in range(5, 17): ENERGY_DB[b] = 0.0
for b in range(17, 29): ENERGY_DB[b] = -0.6
for b in range(29, 33): ENERGY_DB[b] = -1.8
for b in range(33, 37): ENERGY_DB[b] = -0.8
for i, b in enumerate(range(37, 41)): ENERGY_DB[b] = -2.2 + 0.6 * i
for b in range(41, 49): ENERGY_DB[b] = 1.2

def energy_curve():
    db = np.zeros(N + PAD)
    for b, v in ENERGY_DB.items():
        i0 = int(round((b - 1) * 16 * STEP * SR)); i1 = int(round(b * 16 * STEP * SR)); db[i0:i1] = v
    db[int(round(48 * 16 * STEP * SR)):] = ENERGY_DB[48]
    db = lp(db, 30, 1)  # ~ms smoothing so jumps are not clicks
    # build bars 37-40: continuous ramp instead of steps
    i0 = int(round(36 * 16 * STEP * SR)); i1 = int(round(39.75 * 16 * STEP * SR))
    db[i0:i1] = np.linspace(-2.2, 0.3, i1 - i0)
    return (10 ** (db / 20)).astype(np.float32)

def master(mixbus, target_lufs=-9.7):
    import pyloudnorm as pyln
    x = mixbus * energy_curve()
    x = fx(x.astype(np.float32), [pb.HighpassFilter(24), pb.PeakFilter(250, -1.0, 0.8), pb.PeakFilter(2800, 1.8, 0.7),
                    pb.HighShelfFilter(9500, 1.5), pb.HighShelfFilter(15000, 2.0), pb.Compressor(-12, 2.0, 20, 160)])
    x = x[:, :N].copy()
    fade = int(0.30 * SR)
    x[:, -fade:] *= (np.cos(np.linspace(0, np.pi / 2, fade)) ** 2).astype(np.float32)
    meter = pyln.Meter(SR); gain = 1.0
    for _ in range(4):
        y = x * gain
        y = np.tanh(y * 1.15) / 1.15            # soft clip stage (warm, catches transients)
        y, g = tp_limit(y, -1.0)
        lufs = meter.integrated_loudness(y.T.astype(np.float64))
        gain *= 10 ** ((target_lufs - lufs) / 20)
    y[:, -64:] *= np.linspace(1, 0, 64).astype(np.float32)
    up = ss.resample_poly(y, 4, 1, axis=1)
    print('true peak dBTP', 20 * np.log10(np.abs(up).max()), 'min limiter gain dB', 20 * np.log10(g.min()))
    return y.astype(np.float32), meter.integrated_loudness(y.T.astype(np.float64))
