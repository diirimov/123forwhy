"""DSP building blocks: oscillators, filters, string models, drums, fx."""
import numpy as np
from numba import njit
import scipy.signal as ss

SR = 48000


# ---------------------------------------------------------------- primitives
@njit(cache=True)
def saw_blep(freq, phase0):
    n = len(freq)
    out = np.empty(n)
    ph = phase0
    for i in range(n):
        dt = freq[i] / 48000.0
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
        v = 2.0 * ph - 1.0
        if ph < dt:
            t = ph / dt
            v -= t + t - t * t - 1.0
        elif ph > 1.0 - dt:
            t = (ph - 1.0) / dt
            v -= t * t + t + t + 1.0
        out[i] = v
    return out


@njit(cache=True)
def svf(x, fc, q, mode):
    """TPT state-variable filter. mode 0=LP 1=BP 2=HP. fc per-sample array."""
    n = len(x)
    out = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 1.0 / q
    for i in range(n):
        f = fc[i]
        if f > 20000.0:
            f = 20000.0
        if f < 10.0:
            f = 10.0
        g = np.tan(np.pi * f / 48000.0)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            out[i] = v2
        elif mode == 1:
            out[i] = v1
        else:
            out[i] = x[i] - k * v1 - v2
    return out


@njit(cache=True)
def ks_string(excite, period, n, loss, damp_at, damp_loss, a):
    """Karplus-Strong with allpass fine tuning and a note-off damping point."""
    Lf = period - (1.0 - a) - 0.1
    L = int(Lf)
    frac = period - (1.0 - a) - L
    if frac < 0.15:
        L -= 1
        frac += 1.0
    c = (1.0 - frac) / (1.0 + frac)
    buf = np.zeros(L)
    out = np.empty(n)
    idx = 0
    prevd = 0.0
    apx = 0.0
    apy = 0.0
    ne = len(excite)
    for i in range(n):
        xin = excite[i] if i < ne else 0.0
        d = buf[idx]
        lp = a * d + (1.0 - a) * prevd
        prevd = d
        ap = c * lp + apx - c * apy
        apx = lp
        apy = ap
        g = loss if i < damp_at else damp_loss
        y = xin + g * ap
        buf[idx] = y
        idx += 1
        if idx >= L:
            idx = 0
        out[i] = y
    return out


@njit(cache=True)
def env_follow_gain(det, thr, ratio, att, rel):
    """Feed-forward compressor gain (linear) from a detector signal."""
    n = len(det)
    g = np.empty(n)
    e = 0.0
    for i in range(n):
        x = det[i]
        if x > e:
            e = att * e + (1 - att) * x
        else:
            e = rel * e + (1 - rel) * x
        ed = 20 * np.log10(e + 1e-9)
        over = ed - thr
        if over > 0:
            g[i] = 10 ** (-(over - over / ratio) / 20)
        else:
            g[i] = 1.0
    return g


@njit(cache=True)
def limiter_gain(greq, L, rel):
    n = len(greq)
    g1 = np.empty(n)
    # lookahead min
    for i in range(n):
        m = 1.0
        for j in range(i, min(n, i + L)):
            if greq[j] < m:
                m = greq[j]
        g1[i] = m
    g2 = np.empty(n)
    prev = 1.0
    for i in range(n):
        if g1[i] < prev:
            prev = g1[i]
        else:
            prev = prev + (g1[i] - prev) * (1 - rel)
        g2[i] = prev
    g3 = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += g2[i]
        if i >= L:
            acc -= g2[i - L]
            g3[i] = acc / L
        else:
            g3[i] = (acc + (L - i - 1) * 1.0) / L
            if g3[i] > g2[i]:
                g3[i] = g2[i]
    return g3


# ---------------------------------------------------------------- helpers
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def tarr(dur):
    return np.arange(int(dur * SR)) / SR


def biquad(x, kind, f, q=0.707, gain_db=0.0):
    """RBJ biquad applied with lfilter (x mono or (n,2))."""
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f / SR
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2 * q)
    if kind == 'lp':
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == 'hp':
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == 'bp':
        b = [al, 0, -al]; a = [1 + al, -2 * cw, 1 - al]
    elif kind == 'peak':
        b = [1 + al * A, -2 * cw, 1 - al * A]; a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == 'ls':
        sa = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + sa), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sa)]
        a = [(A + 1) + (A - 1) * cw + sa, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sa]
    elif kind == 'hs':
        sa = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + sa), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sa)]
        a = [(A + 1) - (A - 1) * cw + sa, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sa]
    b = np.array(b) / a[0]; a = np.array(a) / a[0]
    return ss.lfilter(b, a, x, axis=0)


def sat(x, drive):
    return np.tanh(x * drive) / np.tanh(drive)


def noise(n, rng):
    return rng.standard_normal(n)


# ---------------------------------------------------------------- drums
def kick(rng, v=1.0, tail=0.32, f_end=46.0):
    t = tarr(0.5)
    f = f_end + 190 * np.exp(-t / 0.016) + 40 * np.exp(-t / 0.08)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * (np.exp(-t / tail) * np.clip(t / 0.001, 0, 1))
    body *= np.where(t < 0.06, 1.0, np.exp(-(t - 0.06) / (tail * 0.6)) / np.exp(0) ) ** 0.5
    click = svf(noise(len(t), rng), np.full(len(t), 4500.0), 0.9, 1) * np.exp(-t / 0.0025) * 0.55
    knock = np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.004) * 0.15
    y = sat(body * 1.25 + click + knock, 1.6)
    y *= np.clip((0.5 - t) / 0.03, 0, 1)
    return y * v


def clap(rng, v=1.0):
    t = tarr(0.45)
    n = noise(len(t), rng)
    e = np.zeros(len(t))
    for k, off in enumerate([0.0, 0.009, 0.019, 0.027]):
        tt = np.clip(t - off, 0, None)
        e += (t >= off) * np.exp(-tt / (0.0045 if k < 3 else 0.11)) * (0.85 if k < 3 else 1.0)
    y = svf(n, np.full(len(t), 1350.0), 1.1, 1) * e * 2.2
    y += svf(n, np.full(len(t), 5200.0), 0.8, 2) * e * 0.25
    tone = np.sin(2 * np.pi * 205 * t) * np.exp(-t / 0.035) * 0.35
    return (y + tone) * v


def frame_drum(rng, v=1.0):
    """Bendir: low membrane with snare-wire buzz."""
    t = tarr(0.5)
    f = 64 + 30 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    buzz_src = noise(len(t), rng) * (1 + 0.7 * np.sign(np.sin(2 * np.pi * 52 * t)))
    buzz = svf(buzz_src, np.full(len(t), 2600.0), 0.9, 1) * np.exp(-t / 0.13) * 0.7
    return sat(body * 0.9 + buzz, 1.3) * v


def hat(rng, v=1.0, decay=0.035):
    t = tarr(max(0.12, decay * 6))
    met = np.zeros(len(t))
    for fr in [205.3, 304.4, 369.6, 522.7, 540.0, 800.0]:
        met += np.sign(np.sin(2 * np.pi * fr * 3.1 * t + rng.uniform(0, 6)))
    src = met * 0.25 + noise(len(t), rng)
    y = svf(src, np.full(len(t), 8500.0), 0.8, 2)
    y = svf(y, np.full(len(t), 11000.0), 0.7, 1) * 0.6 + y * 0.4
    return y * np.exp(-t / decay) * v * 0.6


def tamb(rng, v=1.0, decay=0.07, attack=0.003):
    t = tarr(0.35)
    jing = np.zeros(len(t))
    for _ in range(14):
        fr = rng.uniform(4800, 11500)
        jing += np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) * np.exp(-t / rng.uniform(0.03, 0.12))
    nz = svf(noise(len(t), rng), np.full(len(t), 7000.0), 0.6, 1)
    # jingle cluster: slightly smeared onset (multiple jingles hitting)
    env = np.clip(t / attack, 0, 1) * np.exp(-t / decay)
    rattle = 1 + 0.5 * np.sin(2 * np.pi * 38 * t)
    y = (jing * 0.09 + nz * 1.4) * env * rattle
    return y * v


def shaker(rng, v=1.0):
    t = tarr(0.12)
    env = np.clip(t / 0.012, 0, 1) * np.exp(-t / 0.035)
    return svf(noise(len(t), rng), np.full(len(t), 5500.0), 0.7, 1) * env * v * 1.3


def doum(rng, v=1.0):
    t = tarr(0.45)
    f = 82 + 45 * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.2) + 0.28 * np.sin(1.59 * ph) * np.exp(-t / 0.06) + 0.12 * np.sin(2.14 * ph) * np.exp(-t / 0.04)
    y += svf(noise(len(t), rng), np.full(len(t), 400.0), 0.7, 0) * np.exp(-t / 0.008) * 0.6
    return sat(y, 1.4) * v


def tek(rng, v=1.0, bright=3200.0):
    t = tarr(0.2)
    y = svf(noise(len(t), rng), np.full(len(t), bright), 1.3, 1) * np.exp(-t / 0.018) * 2.0
    for fr, a, d in [(735, 0.45, 0.05), (1180, 0.3, 0.035), (1690, 0.2, 0.025)]:
        y += a * np.sin(2 * np.pi * fr * t) * np.exp(-t / d)
    y += np.exp(-t / 0.0007) * noise(len(t), rng) * 0.5
    return y * v


def woodblock(rng, f0=1100.0, v=1.0):
    t = tarr(0.15)
    y = np.zeros(len(t))
    for r, a, d in [(1.0, 1.0, 0.045), (2.76, 0.35, 0.02), (5.4, 0.15, 0.01)]:
        y += a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t / d)
    y += noise(len(t), rng) * np.exp(-t / 0.001) * 0.4
    return y * v * 0.7


def stomp(rng, v=1.0):
    t = tarr(0.4)
    f = 52 + 50 * np.exp(-t / 0.025)
    low = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    nz = svf(noise(len(t), rng), np.full(len(t), 220.0), 0.8, 0) * np.exp(-t / 0.03) * 2.0
    wood = (np.sin(2 * np.pi * 182 * t) * 0.5 + np.sin(2 * np.pi * 318 * t) * 0.3) * np.exp(-t / 0.05)
    scuff = svf(noise(len(t), rng), np.full(len(t), 1800.0), 0.7, 1) * np.exp(-t / 0.012) * 0.4
    return sat(low + nz + wood + scuff, 1.5) * v


def zills(rng, v=1.0):
    t = tarr(1.4)
    y = np.zeros(len(t))
    for base in (1.0, 1.012):
        for fr, a, d in [(2830, 1.0, 0.9), (3610, 0.6, 0.6), (5120, 0.45, 0.45), (7350, 0.3, 0.3), (9900, 0.15, 0.2)]:
            y += a * np.sin(2 * np.pi * fr * base * t + rng.uniform(0, 6)) * np.exp(-t / d)
    y += noise(len(t), rng) * np.exp(-t / 0.003) * 0.6
    return y * v * 0.18


def crash(rng, v=1.0, dur=2.2):
    t = tarr(dur)
    y = np.zeros(len(t))
    for _ in range(70):
        fr = rng.uniform(2500, 13000)
        y += np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) * np.exp(-t / rng.uniform(0.4, 1.4))
    y = y * 0.03 + svf(noise(len(t), rng), np.full(len(t), 6000.0), 0.5, 2) * np.exp(-t / 0.7) * 0.8
    y *= np.clip(t / 0.002, 0, 1)
    return y * v


def impact(rng, v=1.0):
    t = tarr(1.3)
    f = 32 + 70 * np.exp(-t / 0.12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    boom = svf(noise(len(t), rng), np.full(len(t), 160.0), 0.7, 0) * np.exp(-t / 0.08) * 2.5
    return sat(sub + boom, 1.3) * v


def riser(rng, dur, v=1.0):
    t = tarr(dur)
    x = t / dur
    fc = 300 * (9000 / 300) ** (x ** 1.4)
    nz = svf(noise(len(t), rng), fc, 2.2, 1)
    f = mtof(50) * 2 ** (2.0 * x ** 1.2)
    saw = sum(saw_blep(f * 2 ** (d / 1200), rng.uniform()) for d in (-14, 0, 13)) / 3
    saw = svf(saw, fc * 0.6 + 400, 0.9, 0)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(4 + 12 * x ** 2) / SR)
    y = (nz * 1.3 + saw * 0.35) * (x ** 2.0) * trem
    return y * v


def downlifter(rng, dur, v=1.0):
    t = tarr(dur)
    x = t / dur
    fc = 7000 * (250 / 7000) ** x
    return svf(noise(len(t), rng), fc, 1.8, 1) * (1 - x) ** 1.5 * v


# ---------------------------------------------------------------- pitched
def lute_note(rng, midi, dur, v=1.0, bright=0.6):
    """Double-course lute pluck: two detuned KS strings + gut-ish body."""
    f = mtof(midi)
    ring = dur + 0.25
    n = int((ring + 0.6) * SR)
    damp_at = int(ring * SR)
    out = np.zeros(n)
    for det, gain, off in [(-2.5, 1.0, 0), (2.8, 0.8, int(0.0012 * SR))]:
        fr = f * 2 ** (det / 1200)
        period = SR / fr
        L = int(period)
        ex = noise(L, rng)
        # pluck brightness tied to velocity
        ex = svf(ex, np.full(L, 1500 + 6000 * bright * v), 0.7, 0)
        pos = max(1, int(L * 0.13))
        ex = ex - np.concatenate([np.zeros(pos), ex[:-pos]])
        loss = 0.9965 - 0.002 * max(0, (midi - 60) / 24)
        s = ks_string(ex, period, n - off, loss, damp_at, 0.90, 0.62)
        out[off:] += gain * s
    # gut / body resonances
    body = out * 0.7
    for fr, q, g in [(105, 3, 0.35), (210, 3.5, 0.3), (390, 3, 0.2), (2600, 1.2, 0.12)]:
        body += svf(out, np.full(n, fr), q, 1) * g
    body = biquad(body, 'hp', 80)
    tt = np.arange(n) / SR
    body *= np.clip((ring + 0.55 - tt) / 0.05, 0, 1)
    return body * v * 0.5


def bow_layer(rng, midi, dur, v=1.0):
    """Synth bowed string layer: sharpens attack of sampled fiddle."""
    t = tarr(dur + 0.06)
    f0 = mtof(midi)
    vib = 1 + 0.0045 * np.sin(2 * np.pi * 5.6 * t + rng.uniform(0, 6)) * np.clip((t - 0.12) / 0.15, 0, 1)
    f = f0 * vib * (1 + 0.004 * np.exp(-t / 0.03))
    x = saw_blep(f, rng.uniform()) + 0.5 * saw_blep(f * 1.003, rng.uniform())
    env = np.clip(t / 0.006, 0, 1) * (0.75 + 0.25 * np.exp(-t / 0.05)) * np.clip((dur + 0.06 - t) / 0.06, 0, 1)
    y = np.zeros(len(t))
    for fr, q, g in [(290, 2.5, 0.6), (520, 2.5, 0.5), (1150, 2, 0.5), (2800, 2.2, 0.7), (4200, 2.5, 0.35)]:
        y += svf(x, np.full(len(t), fr), q, 1) * g
    rosin = svf(noise(len(t), rng), np.full(len(t), 3500.0), 1.0, 1) * np.exp(-t / 0.018) * 0.5
    y = (y + rosin) * env
    return y * v * 0.35


def hurdy_note(rng, midi, dur, v=1.0):
    t = tarr(dur + 0.08)
    f0 = mtof(midi)
    wob = 1 + 0.002 * np.sin(2 * np.pi * 3.3 * t + rng.uniform(0, 6))
    x = saw_blep(f0 * wob, rng.uniform()) + saw_blep(f0 * wob * 1.0025, rng.uniform())
    # nasal pulse component
    x += 0.6 * np.sign(np.sin(2 * np.pi * np.cumsum(f0 * wob) / SR)) * 0.5
    env = np.clip(t / 0.012, 0, 1) * np.clip((dur + 0.08 - t) / 0.05, 0, 1)
    y = np.zeros(len(t))
    for fr, q, g in [(450, 2, 0.6), (1250, 3, 0.8), (2400, 3, 0.5), (3300, 4, 0.3)]:
        y += svf(x, np.full(len(t), fr), q, 1) * g
    return y * env * v * 0.25


def drone(rng, midis, n, v=1.0):
    t = np.arange(n) / SR
    y = np.zeros(n)
    for m in midis:
        f = mtof(m) * (1 + 0.0015 * np.sin(2 * np.pi * 0.3 * t + rng.uniform(0, 6)))
        y += saw_blep(f, rng.uniform())
    out = np.zeros(n)
    for fr, q, g in [(350, 1.5, 0.6), (900, 2.5, 0.5), (2300, 3, 0.35)]:
        out += svf(y, np.full(n, fr), q, 1) * g
    wheel = svf(noise(n, rng), np.full(n, 1800.0), 0.8, 1) * 0.04
    return (out + wheel) * v * 0.12


def chien_buzz(rng, midi, v=1.0):
    """Hurdy-gurdy trompette 'dog' buzz on a rhythmic wheel stroke."""
    t = tarr(0.16)
    f = mtof(midi)
    x = saw_blep(np.full(len(t), f), rng.uniform())
    rasp = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 47 * t))
    x = x * (0.4 + 0.6 * rasp) + svf(noise(len(t), rng), np.full(len(t), 2500.0), 1.0, 1) * 0.6 * rasp
    y = svf(x, np.full(len(t), 1800.0), 1.5, 1) + svf(x, np.full(len(t), 3200.0), 2.0, 1) * 0.5
    env = np.clip(t / 0.004, 0, 1) * np.exp(-t / 0.05)
    return y * env * v * 0.6


def bass_note(rng, midi, dur, v=1.0, cutoff=1.0, sub_gain=1.0):
    """Returns (mid, sub) arrays. Plucky filtered double-saw + sine sub."""
    t = tarr(dur + 0.03)
    f = mtof(midi)
    gate = np.clip(t / 0.002, 0, 1) * np.clip((dur + 0.03 - t) / 0.025, 0, 1)
    x = saw_blep(np.full(len(t), f * 2 ** (-6 / 1200)), rng.uniform()) + saw_blep(np.full(len(t), f * 2 ** (6 / 1200)), rng.uniform())
    x += 0.5 * np.sign(np.sin(2 * np.pi * f * t))  # square for hollow woody tone
    fc = (220 + 2600 * np.exp(-t / 0.07)) * cutoff
    mid = svf(x, fc, 1.6, 0)
    mid = sat(mid * 1.4, 1.8) * gate * (0.8 + 0.2 * np.exp(-t / 0.1))
    mid = biquad(mid, 'hp', 90)
    sub = np.sin(2 * np.pi * f * t) * gate * sub_gain
    return mid * v * 0.45, sub * v * 0.55


def supersaw(rng, midis, dur, v=1.0, fc_start=3500.0, fc_end=900.0, fdec=0.08, att=0.003, rel=0.06):
    t = tarr(dur + rel)
    L = np.zeros(len(t)); R = np.zeros(len(t))
    for m in midis:
        for k, d in enumerate((-22, -11, -4, 0, 5, 12, 21)):
            s = saw_blep(np.full(len(t), mtof(m) * 2 ** (d / 1200)), rng.uniform())
            pan = (k / 6.0)
            L += s * np.cos(pan * np.pi / 2); R += s * np.sin(pan * np.pi / 2)
    fc = fc_end + (fc_start - fc_end) * np.exp(-t / fdec)
    env = np.clip(t / att, 0, 1) * np.clip((dur + rel - t) / rel, 0, 1)
    L = svf(L, fc, 0.8, 0) * env; R = svf(R, fc, 0.8, 0) * env
    return np.stack([L, R], 1) * v * 0.06 / max(1, len(midis)) ** 0.5


# ---------------------------------------------------------------- fx
def make_ir(rng, rt, dur, pre=0.012, er=True, damp=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        nz = rng.standard_normal(n)
        lo = biquad(nz, 'lp', 900) * np.exp(-6.9 * t / rt)
        hi = biquad(nz, 'hp', 900) * np.exp(-6.9 * t / (rt * damp))
        ir[:, c] = lo + hi
    ir *= np.clip(t / 0.02, 0, 1)[:, None]
    p = int(pre * SR)
    ir = np.concatenate([np.zeros((p, 2)), ir])[:n]
    if er:
        for k in range(10):
            d = int(rng.uniform(0.004, 0.035) * SR)
            ir[d, rng.integers(0, 2)] += rng.uniform(0.3, 0.8) * rng.choice([-1, 1])
    ir = biquad(ir, 'hp', 180)
    return ir / np.sqrt((ir ** 2).sum() / 2)


def convolve(x, ir):
    return np.stack([ss.fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)


def pingpong(x, delay_s, fb=0.35, lp=4500, hp=300, wet=1.0):
    d = int(delay_s * SR)
    mono = biquad(biquad(x.mean(1), 'lp', lp), 'hp', hp)
    n = len(mono)
    L = np.zeros(n); R = np.zeros(n)
    sig = mono.copy()
    g = 1.0
    for k in range(1, 8):
        sh = d * k
        if sh >= n:
            break
        seg = np.zeros(n); seg[sh:] = sig[:n - sh] * g
        if k % 2:
            L += seg
        else:
            R += seg
        g *= fb
    return np.stack([L, R], 1) * wet


def pan2(x, p):
    """mono -> stereo, constant power; p in [-1,1]."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * np.sqrt(2)


def widen(x, w):
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2 * w
    return np.stack([m + s, m - s], 1)
