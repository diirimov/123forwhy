"""DSP / instrument library for DANSE MACABRE. All original synthesis, no samples."""
import numpy as np
from numba import njit
from scipy.signal import fftconvolve, butter, sosfilt, sosfiltfilt

SR = 48000
RNG = np.random.default_rng(1347)


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=np.float64) - 69.0) / 12.0)


# ----------------------------------------------------------------- filters
def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'hp', fs=SR, output='sos'), x, axis=0)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'lp', fs=SR, output='sos'), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'bp', fs=SR, output='sos'), x, axis=0)


@njit(cache=True)
def svf(x, cutoff, q, mode):
    """TPT state-variable filter with per-sample cutoff. mode 0=lp 1=bp 2=hp"""
    n = x.shape[0]
    y = np.zeros(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 1.0 / q
    for i in range(n):
        fc = cutoff[i]
        if fc > 20000.0:
            fc = 20000.0
        if fc < 15.0:
            fc = 15.0
        g = np.tan(np.pi * fc / 48000.0)
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


@njit(cache=True)
def blep_saw(freq, phase0):
    n = freq.shape[0]
    out = np.zeros(n)
    ph = phase0
    for i in range(n):
        dt = freq[i] / 48000.0
        v = 2.0 * ph - 1.0
        # polyblep
        if ph < dt:
            t = ph / dt
            v -= t + t - t * t - 1.0
        elif ph > 1.0 - dt:
            t = (ph - 1.0) / dt
            v -= t * t + t + t + 1.0
        out[i] = v
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
    return out


@njit(cache=True)
def blep_pulse(freq, width, phase0):
    n = freq.shape[0]
    out = np.zeros(n)
    ph = phase0
    for i in range(n):
        dt = freq[i] / 48000.0
        v = 1.0 if ph < width else -1.0
        # rising edge at 0
        if ph < dt:
            t = ph / dt
            v += t + t - t * t - 1.0
        elif ph > 1.0 - dt:
            t = (ph - 1.0) / dt
            v += t * t + t + t + 1.0
        # falling edge at width
        p2 = ph - width
        if p2 < 0.0:
            p2 += 1.0
        if p2 < dt:
            t = p2 / dt
            v -= t + t - t * t - 1.0
        elif p2 > 1.0 - dt:
            t = (p2 - 1.0) / dt
            v -= t * t + t + t + 1.0
        out[i] = v
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
    return out


# ----------------------------------------------------------------- envelopes
def adsr(n, a, d, s, r, gate):
    """gate: samples of sustain-hold before release"""
    t = np.arange(n) / SR
    env = np.zeros(n)
    A = max(a, 1e-4)
    g = gate / SR
    env = np.where(t < A, t / A, s + (1 - s) * np.exp(-(t - A) / max(d, 1e-4)))
    rel = t > g
    if np.any(rel):
        lvl = env[min(int(g * SR), n - 1)]
        env = np.where(rel, lvl * np.exp(-(t - g) / max(r, 1e-4)), env)
    return env


# ----------------------------------------------------------------- reverb IRs
def make_ir(rt60, length, predelay, dark, er=True, seed=0, width=1.0):
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        noise = rng.standard_normal(n)
        # frequency dependent decay: split into bands with different rt
        bands = [(20, 300, rt60 * 1.15), (300, 1500, rt60), (1500, 5000, rt60 * 0.7 * dark + rt60 * 0.3),
                 (5000, 20000, rt60 * 0.35 * dark + 0.05)]
        acc = np.zeros(n)
        for lo, hi, rt in bands:
            b = bp(noise, lo, min(hi, 23000))
            acc += b * np.exp(-6.91 * t / rt)
        # fade-in for smooth onset
        acc *= np.clip(t / 0.012, 0, 1)
        ir[:, c] = acc
    if er:
        for k in range(14):
            dly = rng.uniform(0.004, 0.06)
            g = 0.6 * np.exp(-dly * 30) * rng.choice([-1, 1])
            idx = int(dly * SR)
            ir[idx, rng.integers(0, 2)] += g * 8
    pd = int(predelay * SR)
    ir = np.vstack([np.zeros((pd, 2)), ir])[:n]
    mid = (ir[:, 0] + ir[:, 1]) / 2
    side = (ir[:, 0] - ir[:, 1]) / 2 * width
    ir = np.stack([mid + side, mid - side], 1)
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


def convolve_st(x, ir):
    """x: mono or stereo; ir stereo -> stereo"""
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    out = np.zeros((x.shape[0] + ir.shape[0] - 1, 2))
    out[:, 0] = fftconvolve(x[:, 0], ir[:, 0])
    out[:, 1] = fftconvolve(x[:, 1], ir[:, 1])
    return out[:x.shape[0]]


def pan(x, p):
    """equal-power, p in [-1,1]"""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * np.sqrt(2)


def place(buf, sig, t0):
    i = int(round(t0 * SR))
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(buf.shape[0], i + sig.shape[0])
    if j > i:
        buf[i:j] += sig[:j - i]


# ================================================================= FIDDLE
def body_ir(seed=3, kind='violin'):
    rng = np.random.default_rng(seed)
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    if kind == 'violin':
        modes = [(275, 1.0, 0.020), (440, 0.7, 0.012), (520, 0.9, 0.015), (700, 0.6, 0.010),
                 (870, 0.5, 0.008), (1050, 0.55, 0.008), (1350, 0.45, 0.006), (1700, 0.4, 0.005),
                 (2100, 0.45, 0.004), (2500, 0.7, 0.004), (2900, 0.75, 0.0035), (3300, 0.6, 0.003),
                 (3900, 0.3, 0.0025), (4700, 0.15, 0.002), (6000, 0.08, 0.0015)]
    else:  # viola / lower body
        modes = [(220, 1.0, 0.022), (360, 0.8, 0.015), (450, 0.8, 0.014), (600, 0.6, 0.010),
                 (800, 0.5, 0.008), (1000, 0.5, 0.007), (1400, 0.4, 0.005), (1900, 0.4, 0.004),
                 (2400, 0.5, 0.004), (2800, 0.4, 0.003), (3500, 0.2, 0.0025)]
    ir = np.zeros(n)
    for f, g, d in modes:
        f2 = f * rng.uniform(0.97, 1.03)
        ir += g * np.sin(2 * np.pi * f2 * t + rng.uniform(0, 6.28)) * np.exp(-t / d)
    ir[0] += 1.5  # direct string
    ir /= np.sqrt(np.sum(ir ** 2))
    return ir


def render_bowed(notes, total_n, vib_rate=5.7, vib_depth=0.2, bright=1.0, seed=0, kind='violin',
                 noise_amt=0.018, max_harm_hz=15000):
    """Monophonic expressive bowed string.
    notes: list of dicts start, dur (s), midi, vel, [trem], [accent]
    returns mono signal."""
    rng = np.random.default_rng(seed)
    notes = sorted(notes, key=lambda n: n['start'])
    pitch = np.full(total_n, np.nan)
    amp = np.zeros(total_n)
    trem = np.zeros(total_n)
    vibd = np.zeros(total_n)
    scoop = np.zeros(total_n)
    prev_m = None
    prev_end = -10
    for idx, nt in enumerate(notes):
        s = int(nt['start'] * SR)
        e = int((nt['start'] + nt['dur']) * SR)
        nxt = notes[idx + 1]['start'] if idx + 1 < len(notes) else 1e9
        legato_next = (nxt - (nt['start'] + nt['dur'])) < 0.03
        connected = (nt['start'] - prev_end) < 0.03 and prev_m is not None
        L = e - s
        if L <= 0:
            continue
        t = np.arange(L) / SR
        m = nt['midi']
        pseg = np.full(L, float(m))
        if connected:
            g = 0.018 + 0.012 * rng.random()
            gl = np.clip(t / g, 0, 1)
            gl = gl * gl * (3 - 2 * gl)
            pseg = prev_m + (m - prev_m) * gl
        acc = nt.get('accent', 0.0)
        if acc > 0 or not connected:
            scoop[s:e] = -(0.25 + 0.3 * acc) * np.exp(-t / 0.03)
        pitch[s:e] = pseg
        vel = nt['vel']
        floor = 0.4 if connected else 0.0
        att = 0.010 if connected else 0.018
        a = np.where(t < att, floor + (1 - floor) * (t / att) ** 0.8, 1.0)
        # bow-stroke accent then settle, slight swell on long notes
        a = a * (0.78 + (0.22 + 0.35 * acc) * np.exp(-t / 0.07))
        if nt['dur'] > 0.3:
            a *= 1 + 0.12 * np.clip((t - 0.15) / nt['dur'], 0, 1)
        # stroke end taper
        tail = 0.03
        a *= np.clip((nt['dur'] - t) / tail, 0.55 if legato_next else 0.0, 1.0) ** 0.7
        amp[s:e] = a * vel
        if nt.get('trem', False):
            trem[s:e] = 1.0
        d = vib_depth * (1.0 if nt['dur'] > 0.25 else 0.35)
        vibd[s:e] = d * np.clip((t - 0.09) / 0.18, 0, 1)
        # release after non-legato
        if not legato_next:
            rl = int(0.09 * SR)
            r_end = min(total_n, e + rl)
            rt = np.arange(r_end - e) / SR
            lvl = amp[e - 1] if e - 1 >= 0 else 0
            amp[e:r_end] = np.maximum(amp[e:r_end], lvl * np.exp(-rt / 0.025))
            pitch[e:r_end] = np.where(np.isnan(pitch[e:r_end]), m, pitch[e:r_end])
        prev_m = m
        prev_end = nt['start'] + nt['dur']
    # fill nan pitch by holding
    valid = ~np.isnan(pitch)
    if not valid.any():
        return np.zeros(total_n)
    idxs = np.where(valid, np.arange(total_n), 0)
    np.maximum.accumulate(idxs, out=idxs)
    pitch = pitch[idxs]
    first = np.argmax(valid)
    pitch[:first] = pitch[first]
    # tremolo: 32nd-note bow changes
    step32 = 60 / 136 / 8
    tt = np.arange(total_n) / SR
    tremphase = (tt / step32) % 1.0
    tremenv = 0.55 + 0.45 * np.sin(np.pi * tremphase) ** 0.5
    amp = amp * (1 - trem + trem * tremenv)
    # vibrato LFO with drift
    drift = lp(rng.standard_normal(total_n), 0.7) * 40
    vrate = vib_rate * (1 + 0.06 * np.clip(drift, -2, 2))
    vph = 2 * np.pi * np.cumsum(vrate) / SR
    jitter = lp(rng.standard_normal(total_n), 30) * 0.9  # cents-ish random wander
    mid = pitch + vibd * np.sin(vph) + scoop + jitter * 0.04
    f0 = mtof(mid)
    phase = 2 * np.pi * np.cumsum(f0) / SR
    envn = np.clip(amp, 0, 1.4)
    out = np.zeros(total_n)
    fmin = f0[amp > 1e-3].min() if (amp > 1e-3).any() else 200
    K = int(max_harm_hz / fmin)
    roll = (0.11 - 0.06 * envn) / bright  # brighter when pressed harder
    active = amp > 1e-5
    ai = np.where(active)[0]
    if len(ai) == 0:
        return out
    lo_i, hi_i = ai[0], ai[-1] + 1
    ph = phase[lo_i:hi_i]
    fseg = f0[lo_i:hi_i]
    rseg = roll[lo_i:hi_i]
    acc = np.zeros(hi_i - lo_i)
    for k in range(1, K + 1):
        w = (1.0 / k) * np.exp(-(k - 1) * rseg * 0.6)
        # alternate sign / slight comb from bow position (~1/9 string)
        w = w * (0.55 + 0.45 * abs(np.sin(np.pi * k / 8.7)))
        top = np.clip((max_harm_hz - k * fseg) / 2000.0, 0, 1)
        acc += w * top * np.sin(k * ph + 0.3 * k)
    out[lo_i:hi_i] = acc
    out *= amp
    # bow noise (rosin), modulated by amplitude and tremolo
    nz = rng.standard_normal(total_n)
    nz = bp(nz, 1800, 9000) * (noise_amt + 0.03 * trem) * amp
    sig = out * 0.25 + nz
    sig = fftconvolve(sig, body_ir(seed + 11, kind))[:total_n]
    # tame harshness, keep air
    sig = sig - 0.22 * bp(sig, 3500, 6000)
    sig = hp(sig, 180 if kind == 'violin' else 110)
    return sig


# ================================================================= HARPSICHORD
@njit(cache=True)
def ks_string(freq, n, excite, loss, damp_at, damp_loss, bright):
    L = 48000.0 / freq - (1.0 - bright)
    N = int(L)
    frac = L - N
    if frac < 0.1:
        N -= 1
        frac += 1.0
    # allpass coefficient for fractional delay
    c = (1 - frac) / (1 + frac)
    buf = np.zeros(N + 2)
    m = excite.shape[0]
    for i in range(min(m, N + 2)):
        buf[i] = excite[i]
    out = np.zeros(n)
    ptr = 0
    ap_x1 = 0.0
    ap_y1 = 0.0
    lp1 = 0.0
    size = N + 2
    for i in range(n):
        x = buf[ptr]
        # one-zero lowpass (brightness)
        y = bright * x + (1 - bright) * lp1
        lp1 = x
        g = loss if i < damp_at else damp_loss
        y *= g
        # fractional allpass
        ap = c * y + ap_x1 - c * ap_y1
        ap_x1 = y
        ap_y1 = ap
        out[i] = x
        buf[ptr] = ap
        ptr += 1
        if ptr >= N:
            ptr = 0
    return out


def harpsi_note(midi, dur, vel, seed):
    rng = np.random.default_rng(seed)
    f = float(mtof(midi))
    n = int((dur + 1.6) * SR)
    sig = np.zeros(n)
    for reg, (mult, g, det) in enumerate([(1.0, 1.0, 0.0), (2.0, 0.42, 3.0), (1.0, 0.5, -4.0)]):
        ff = f * mult * 2 ** (det / 1200)
        if ff > 7000:
            continue
        P = max(4, int(SR / ff))
        ex = rng.uniform(-1, 1, P)
        # pluck position comb (plucked near the end -> bright, nasal)
        pp = max(1, int(P * 0.13))
        ex = ex - np.roll(ex, pp)
        loss = 0.9993 - 0.0009 * (ff / 2000)
        damp_at = int(dur * SR)
        s = ks_string(ff, n, ex, loss, damp_at, 0.985, 0.62 + 0.05 * reg)
        sig += g * s
    # plectrum click
    click = rng.standard_normal(200) * np.exp(-np.arange(200) / 25)
    sig[:200] += hp(click, 3000) * 0.4
    sig *= vel
    sig = hp(sig, 120)
    return sig


def soundboard_ir(seed=5):
    rng = np.random.default_rng(seed)
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    ir = np.zeros(n)
    for f in rng.uniform(150, 4000, 30):
        ir += rng.uniform(0.2, 1) * np.sin(2 * np.pi * f * t) * np.exp(-t / rng.uniform(0.005, 0.03))
    ir /= np.max(np.abs(ir))
    ir[0] += 4
    ir /= np.sqrt(np.sum(ir ** 2))
    return ir


# ================================================================= HURDY-GURDY drone + trompette buzz
def hurdy_drone(total_n, midis, buzz_steps, step_t, seed=7, wheel=1.0, gate=None, swing=None):
    rng = np.random.default_rng(seed)
    t = np.arange(total_n) / SR
    wow = 1 + 0.004 * np.sin(2 * np.pi * 0.31 * t) + 0.002 * lp(rng.standard_normal(total_n), 3) * 30
    out = np.zeros(total_n)
    for j, m in enumerate(midis):
        f = float(mtof(m)) * wow * 2 ** (rng.uniform(-3, 3) / 1200)
        s = blep_saw(f, rng.random()) * 0.6 + blep_pulse(f * 1.0015, 0.32, rng.random()) * 0.4
        out += s / len(midis)
    # nasal formants
    nas = svf(out, np.full(total_n, 1150.0), 3.0, 1) * 1.2 + svf(out, np.full(total_n, 2600.0), 4.0, 1) * 0.7
    out = lp(out, 1600) * 0.5 + nas
    # wheel rasp
    rasp = bp(rng.standard_normal(total_n), 2500, 7000) * 0.05
    # trompette/chien buzz: rhythmic, at the rate of the drone fundamental
    buzzenv = np.zeros(total_n)
    for st in buzz_steps:
        t0 = st * step_t + (swing(st) if swing else 0)
        i = int(t0 * SR)
        L = int(0.09 * SR)
        if i >= total_n:
            continue
        e = np.exp(-np.arange(L) / (0.035 * SR)) * np.clip(np.arange(L) / 60, 0, 1)
        j = min(total_n, i + L)
        buzzenv[i:j] = np.maximum(buzzenv[i:j], e[:j - i])
    f_b = float(mtof(midis[0]))
    buzz = blep_pulse(np.full(total_n, f_b), 0.08, 0.0)
    buzz = bp(buzz, 900, 5000) * buzzenv * 0.6
    sig = (out + rasp) * wheel + buzz
    if gate is not None:
        sig *= gate
    return hp(sig, 90)


# ================================================================= ORGAN
def organ_chord(midis, dur, vel, seed=0, bright=1.0):
    rng = np.random.default_rng(seed)
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    stops = [(0.5, 0.45), (1, 1.0), (2, 0.55), (3, 0.22), (4, 0.3), (6, 0.12 * bright), (8, 0.09 * bright)]
    for m in midis:
        f = float(mtof(m))
        for mult, g in stops:
            ff = f * mult
            if ff > 9000:
                continue
            det = 2 ** (rng.uniform(-2.5, 2.5) / 1200)
            pipe = np.zeros(n)
            for h, hg in [(1, 1), (2, 0.35), (3, 0.18), (4, 0.08)]:
                if ff * h < 12000:
                    pipe += hg * np.sin(2 * np.pi * ff * det * h * t + rng.uniform(0, 6))
            out += g * pipe
    env = np.clip(t / 0.045, 0, 1) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.18))
    trem = 1 + 0.03 * np.sin(2 * np.pi * 5.2 * t)
    chiff = bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t / 0.03) * 0.15
    out = out / (len(midis) * 2.5) * env * trem + chiff * np.clip(t / 0.003, 0, 1)
    return out * vel


# ================================================================= STRINGS ENSEMBLE
def strings_note(midi, dur, vel, seed=0, attack=0.08, release=0.25, voices=6, cutoff=3200, stacc=False):
    rng = np.random.default_rng(seed)
    n = int((dur + release * 4) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    f = float(mtof(midi))
    for v in range(voices):
        det = 2 ** (rng.uniform(-9, 9) / 1200)
        vib = 1 + 0.0025 * np.sin(2 * np.pi * rng.uniform(4.8, 6.2) * t + rng.uniform(0, 6))
        out += blep_saw(f * det * vib, rng.random())
    out /= voices
    env = np.clip(t / attack, 0, 1) ** 1.5 * np.where(t < dur, 1.0, np.exp(-(t - dur) / release))
    if stacc:
        env *= 1 + 0.6 * np.exp(-t / 0.03)
    cut = cutoff * (0.55 + 0.45 * np.clip(t / (attack * 2), 0, 1))
    out = svf(out, cut, 0.8, 0)
    out = out + 0.4 * bp(out, 700, 1400)
    return hp(out * env * vel, 150)


# ================================================================= WOODWIND (recorder / shawm)
def wind_line(notes, total_n, kind='recorder', seed=0):
    rng = np.random.default_rng(seed)
    out = np.zeros(total_n)
    for nt in notes:
        f = float(mtof(nt['midi']))
        dur = nt['dur']
        n = int((dur + 0.15) * SR)
        t = np.arange(n) / SR
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.3 * t) * np.clip((t - 0.1) / 0.2, 0, 1)
        ff = f * vib
        env = np.clip(t / 0.012, 0, 1) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.03))
        if kind == 'recorder':
            ph = 2 * np.pi * np.cumsum(ff) / SR
            s = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.22 * np.sin(3 * ph) + 0.05 * np.sin(5 * ph)
            breath = svf(rng.standard_normal(n), ff * 1.0, 6.0, 1) * 0.25 + hp(rng.standard_normal(n), 4000) * 0.03
            chiff = bp(rng.standard_normal(n), 2000, 8000) * np.exp(-t / 0.012) * 0.6
            s = s + breath + chiff
        else:  # shawm: nasal double reed
            s = blep_pulse(ff, 0.22, rng.random())
            s = svf(s, np.full(n, 1300.0), 2.5, 1) + 0.7 * svf(s, np.full(n, 2900.0), 3.0, 1) + 0.25 * lp(s, 900)
            s = np.tanh(1.6 * s) * 0.6
        place(out, s * env * nt['vel'], nt['start'])
    return hp(out, 250)


# ================================================================= BASS
def bass_line(notes, total_n, drive=1.6, seed=0, open_amt=1.0):
    """notes: start, dur, midi, vel. returns (sub, mid) mono arrays"""
    rng = np.random.default_rng(seed)
    sub = np.zeros(total_n)
    mid = np.zeros(total_n)
    for k, nt in enumerate(notes):
        f = float(mtof(nt['midi']))
        dur = nt['dur']
        n = int((dur + 0.06) * SR)
        t = np.arange(n) / SR
        env = np.clip(t / 0.004, 0, 1) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.015))
        # slight pitch punch
        fp = f * (1 + 0.04 * np.exp(-t / 0.012))
        ph = 2 * np.pi * np.cumsum(fp) / SR
        s = np.sin(ph) + 0.08 * np.sin(2 * ph)
        sub_env = env * (0.85 + 0.15 * np.exp(-t / 0.08))
        place(sub, s * sub_env * nt['vel'], nt['start'])
        m = 0.55 * blep_saw(fp * 1.004, 0.0) + 0.45 * blep_saw(fp * 0.996, 0.5) + 0.35 * blep_pulse(fp * 2, 0.4, 0.2)
        cut = 180 + (1400 * open_amt * nt.get('open', 1.0)) * np.exp(-t / 0.09) + 250 * open_amt
        m = svf(m, cut, 1.6, 0)
        m = np.tanh(drive * m)
        place(mid, m * env * nt['vel'], nt['start'])
    sub = lp(sub, 140, 4)
    mid = hp(lp(mid, 3500), 110, 3)
    return sub, mid


# ================================================================= DRUMS & FX one-shots
def kick(vel=1.0, seed=0):
    rng = np.random.default_rng(seed)
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 46 + 150 * np.exp(-t / 0.028) + 40 * np.exp(-t / 0.004)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.17) * np.clip(t / 0.0015, 0, 1)
    body = np.tanh(1.8 * body) / np.tanh(1.8)
    click = hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.0025) * 0.35
    knock = np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.003) * 0.2
    return (body + click + knock) * vel


def modal_hit(freqs, gains, decays, n_s=0.4, noise_len=0.002, seed=0, nlp=8000):
    rng = np.random.default_rng(seed)
    n = int(n_s * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f, g, d in zip(freqs, gains, decays):
        out += g * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / d)
    exc = lp(rng.standard_normal(n), nlp) * np.exp(-t / noise_len)
    out = out * np.clip(t / 0.0004, 0, 1) + exc * 0.3
    return out


def woodblock(pitch=1.0, vel=1.0, seed=0):
    f = np.array([780, 1950, 2900]) * pitch
    return hp(modal_hit(f, [1, 0.45, 0.2], [0.045, 0.018, 0.01], 0.2, 0.001, seed), 350, 3) * vel


def bone_click(pitch=1.0, vel=1.0, seed=0):
    rng = np.random.default_rng(seed)
    base = 2300 * pitch * rng.uniform(0.9, 1.1)
    f = base * np.array([1, 1.63, 2.37, 3.41])
    return hp(modal_hit(f, [1, 0.6, 0.4, 0.25], [0.012, 0.008, 0.006, 0.004], 0.08, 0.0006, seed, 12000), 900) * vel


def bone_xylo(midi, vel=1.0, seed=0):
    """pitched skeleton xylophone - hollow, dry, bony"""
    f = float(mtof(midi))
    fr = f * np.array([1, 3.93, 9.2, 2.76])
    s = modal_hit(fr, [1, 0.35, 0.12, 0.18], [0.06, 0.025, 0.01, 0.015], 0.3, 0.0008, seed, 10000)
    return hp(s, 400, 3) * vel


def bone_rattle(length=0.16, vel=1.0, seed=0, density=60):
    rng = np.random.default_rng(seed)
    n = int((length + 0.08) * SR)
    out = np.zeros(n)
    k = int(density * length * 3)
    times = rng.exponential(length / 2.5, k)
    times = times[times < length]
    for i, tt in enumerate(times):
        c = bone_click(rng.uniform(0.7, 1.6), rng.uniform(0.2, 1) * np.exp(-tt / length * 1.5), seed * 1000 + i)
        place(out, c, tt)
    return out * vel * 0.6


def chain_hit(vel=1.0, seed=0, length=0.12):
    rng = np.random.default_rng(seed)
    n = int((length + 0.3) * SR)
    out = np.zeros(n)
    for i in range(rng.integers(5, 9)):
        tt = rng.uniform(0, length) ** 1.3 / length ** 0.3
        fs = rng.uniform(2200, 9500, 7)
        hit = modal_hit(fs, rng.uniform(0.2, 1, 7), rng.uniform(0.02, 0.12, 7), 0.25, 0.0005, seed * 50 + i, 14000)
        place(out, hit * rng.uniform(0.3, 1), tt)
    return hp(out, 1800) * vel * 0.5


def coffin_knock(vel=1.0, seed=0):
    rng = np.random.default_rng(seed)
    f = np.array([118, 182, 255, 410, 640]) * rng.uniform(0.97, 1.03)
    s = modal_hit(f, [1, 0.8, 0.6, 0.35, 0.2], [0.07, 0.05, 0.04, 0.025, 0.015], 0.35, 0.0015, seed, 3000)
    # knuckle transient
    n = s.shape[0]
    t = np.arange(n) / SR
    s += bp(rng.standard_normal(n), 600, 3500) * np.exp(-t / 0.002) * 0.5
    return hp(s, 70) * vel


def snare(vel=1.0, seed=0):
    rng = np.random.default_rng(seed)
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * (185 + 60 * np.exp(-t / 0.01)) * t) * np.exp(-t / 0.05)
    nz = bp(rng.standard_normal(n), 1200, 9000) * np.exp(-t / 0.075)
    slap = bp(rng.standard_normal(n), 700, 2500) * np.exp(-t / 0.008) * 0.8
    s = tone * 0.6 + nz * 0.8 + slap
    s += bone_rattle(0.07, 0.6, seed + 77, 90)[:n] if n <= int(0.15 * SR) else np.pad(bone_rattle(0.07, 0.6, seed + 77, 90), (0, max(0, n - int(0.15 * SR))))[:n]
    return np.tanh(1.5 * s) * vel * 0.7


def hat(open_=False, vel=1.0, seed=0):
    rng = np.random.default_rng(seed)
    n = int((0.25 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    ratios = np.array([2, 3, 4.16, 5.43, 6.79, 8.21]) * 400
    sq = sum(np.sign(np.sin(2 * np.pi * r * t + rng.uniform(0, 6))) for r in ratios)
    s = hp(sq + rng.standard_normal(n) * 1.5, 7000)
    s *= np.exp(-t / (0.07 if open_ else 0.012))
    return s * vel * 0.25


def bell(midi, vel=1.0, seed=0, length=5.0, dark=1.0):
    """Church bell: minor-third tierce bell partials, nominal = midi"""
    rng = np.random.default_rng(seed)
    f = float(mtof(midi))
    n = int(length * SR)
    t = np.arange(n) / SR
    partials = [(0.5, 0.55, 3.8), (1.0, 0.7, 2.6), (1.2, 0.55, 2.0), (1.5, 0.35, 1.5), (2.0, 1.0, 1.4),
                (2.5, 0.35, 0.8), (2.61, 0.25, 0.7), (3.0, 0.3, 0.6), (4.0, 0.22, 0.45), (5.33, 0.12, 0.3),
                (6.7, 0.08, 0.2)]
    out = np.zeros(n)
    for r, g, d in partials:
        ff = f * r / 2.0  # so that nominal (2.0) == f
        if ff > 15000:
            continue
        beat = rng.uniform(0.3, 1.2)
        gg = g * (dark if r > 3 else 1.0)
        out += gg * (np.sin(2 * np.pi * (ff - beat / 2) * t) + np.sin(2 * np.pi * (ff + beat / 2) * t + 1)) * 0.5 \
            * np.exp(-t / (d * (1.2 if f < 300 else 1.0)))
    strike = bp(rng.standard_normal(n), 800, 6000) * np.exp(-t / 0.004) * 0.6
    out = out * np.clip(t / 0.001, 0, 1) + strike
    return out * vel * 0.5


def riser(length, seed=0, f0=300, f1=7000):
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    x = t / length
    cut = f0 * (f1 / f0) ** (x ** 1.6)
    s = svf(rng.standard_normal(n), cut, 4.0, 1)
    env = x ** 2.2
    # rising sine shimmer
    ph = 2 * np.pi * np.cumsum(220 * 2 ** (3 * x ** 1.5)) / SR
    shim = (np.sin(ph) + 0.5 * np.sin(1.5 * ph)) * 0.07 * env
    return (s * env * 0.35 + shim)


def downlifter(length=1.2, seed=0):
    rng = np.random.default_rng(seed)
    n = int(length * SR)
    t = np.arange(n) / SR
    x = t / length
    cut = 6000 * (0.03) ** x
    s = svf(rng.standard_normal(n), cut, 3.0, 1) * (1 - x) ** 2 * 0.3
    return s


def impact(seed=0):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = 32 + 60 * np.exp(-t / 0.06)
    ph = 2 * np.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-t / 0.6)
    rng = np.random.default_rng(seed)
    nz = lp(rng.standard_normal(n), 1500) * np.exp(-t / 0.25) * 0.25
    return boom * 0.8 + nz


def reverse_swell(sig_seed=0, length=0.9, midi=74):
    """reversed reverberant bell = supernatural inhale"""
    b = bell(midi, 1.0, sig_seed, length + 1.0)
    ir = make_ir(2.2, 2.5, 0.0, 0.8, False, sig_seed + 3)
    wet = convolve_st(b, ir)
    wet = wet[:int(length * SR)][::-1]
    t = np.arange(wet.shape[0]) / SR
    wet *= (t / length)[:, None] ** 1.5
    return wet


@njit(cache=True)
def brickwall(x, thr, look, rel):
    """x: (n,2). lookahead peak limiter, returns limited signal (delay-compensated)."""
    n = x.shape[0]
    peak = np.zeros(n)
    for i in range(n):
        a = abs(x[i, 0])
        b = abs(x[i, 1])
        peak[i] = a if a > b else b
    # required gain
    req = np.ones(n)
    for i in range(n):
        if peak[i] > thr:
            req[i] = thr / peak[i]
    # sliding minimum over lookahead window (forward-looking)
    from_min = np.ones(n)
    # simple O(n*look) is too slow; use deque-free block approach
    m = look
    # compute min over [i, i+m)
    # van Herk / Gil-Werman
    nb = (n + m - 1) // m
    pre = np.ones(nb * m)
    suf = np.ones(nb * m)
    pad = np.ones(nb * m)
    for i in range(n):
        pad[i] = req[i]
    for b in range(nb):
        s = b * m
        pre[s] = pad[s]
        for k in range(1, m):
            pre[s + k] = min(pre[s + k - 1], pad[s + k])
        suf[s + m - 1] = pad[s + m - 1]
        for k in range(m - 2, -1, -1):
            suf[s + k] = min(suf[s + k + 1], pad[s + k])
    for i in range(n):
        j = i + m - 1
        if j >= nb * m:
            from_min[i] = suf[i]
        else:
            from_min[i] = min(suf[i], pre[j])
    # smoothing: attack via linear ramp over lookahead (moving average), release exponential
    g = np.ones(n)
    cur = 1.0
    ra = np.exp(-1.0 / rel)
    for i in range(n):
        t = from_min[i]
        if t < cur:
            cur = t
        else:
            cur = t + (cur - t) * ra
        g[i] = cur
    # moving average over look to smooth attack (keeps g <= required since min window)
    out = np.zeros_like(x)
    acc = 0.0
    sm = np.zeros(n)
    for i in range(n):
        acc += g[i]
        if i >= m:
            acc -= g[i - m]
        sm[i] = acc / min(i + 1, m)
    # sm[i] averages g[i-m+1..i]; since from_min looks ahead m, sm at i+m-1 covers sample i safely
    for i in range(n):
        j = i + m - 1
        if j >= n:
            j = n - 1
        out[i, 0] = x[i, 0] * sm[j]
        out[i, 1] = x[i, 1] * sm[j]
    return out
