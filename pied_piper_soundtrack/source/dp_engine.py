"""
[Copied unchanged from the Dancing Plague 1518 project (branch claude/epic-darwin-hshpai,
 dancing_plague_1518/source/engine.py) so its proven synth models can be reused here.]

Dancing Plague 1518 -- synthesis engine.

DSP helpers and instrument models used to rebuild the EP01 soundtrack.
Everything is synthesised (physical / additive models); no samples.
The core models (bowed fiddle, lute, club kick, deep bass, hurdy-gurdy drone,
mix/master chain) come from our earlier medieval soundtracks, whose low end
was already matched to the Dancing Plague reference. New here: the recorder-
like pipe that carries the hook, the riq (offbeat frame drum with jingles),
the sliding sub bass of the bass drop and a bagpipe-style D/A drone.
"""
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(1518)


def reseed(seed):
    global rng
    rng = np.random.default_rng(seed)


# ============================================================================ DSP helpers
def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def hum(sd=0.004):
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


def adsr(n, a, d, s, r, length):
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    k = int(length * SR)
    if k < n:
        e[k:] = e[k] * np.exp(-(t[k:] - t[k]) / r)
    return e


def smooth(k):
    return k * k * (3 - 2 * k)


class Track:
    """mono-or-stereo accumulation buffer with constant-power panning"""

    def __init__(self, n, pan=0.0, rev=0.1, plate=0.0, stem="misc"):
        self.pan, self.rev, self.plate, self.stem = pan, rev, plate, stem
        self.buf = np.zeros((n, 2))

    def add(self, x, t, pan=None, gain=1.0):
        p = self.pan if pan is None else pan
        s = int(round(t * SR))
        if s < 0:
            x = x[-s:]; s = 0
        e = min(s + len(x), len(self.buf))
        if e <= s:
            return
        x = x[: e - s] * gain
        if x.ndim == 1 and len(x) > 1200:
            # de-click: 0.4 ms attack ramp, 8 ms raised-cosine taper on the tail
            x = x.copy()
            a = 20; x[:a] *= np.linspace(0, 1, a)
            k = int(0.008 * SR); x[-k:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, k))
        if x.ndim == 1:
            self.buf[s:e, 0] += x * np.cos((p + 1) * np.pi / 4) * 1.4142
            self.buf[s:e, 1] += x * np.sin((p + 1) * np.pi / 4) * 1.4142
        else:
            self.buf[s:e] += x


# ============================================================================ strings
def ks(freq, dur, bright=0.7, decay=0.996, pick=0.13):
    """Karplus-Strong string, block vectorised, resampled to exact pitch"""
    P = max(8, int(SR / freq)); ratio = freq / (SR / (P + 0.5))
    n_gen = int(dur * SR * ratio) + 2 * P + 2
    y = np.zeros(n_gen + P)
    x = np.arange(P) / P
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


def lute(m, dur, vel=1.0, bright=0.7):
    """gut-strung lute: two slightly detuned courses + wooden body resonances"""
    f = mtof(m) * 2 ** (rng.normal(0, 2.5) / 1200)
    ring = dur + 0.4
    x = ks(f, ring, bright, 0.9965) + 0.65 * ks(f * 1.0022, ring, bright * 0.9, 0.996)
    off = int(dur * SR)
    if off < len(x):
        x[off:] *= np.exp(-np.arange(len(x) - off) / (0.06 * SR))
    for f0, g, q in ((200, 3, 1.5), (420, 2, 2), (1300, 4, 1.4), (3000, 5, 1.0)):
        x = peq(x, f0, g, q)
    return filt(x, "high", 70) * vel * 0.45


def strum(ms, dur, vel=1.0, down=True, spread=0.009):
    ms = ms if down else ms[::-1]
    tot = int((dur + 0.5 + spread * len(ms)) * SR); out = np.zeros(tot)
    for i, m in enumerate(ms):
        s = lute(m, dur, vel * (1 - 0.07 * i), 0.55)
        o = int(i * spread * SR * rng.uniform(0.7, 1.3))
        out[o:o + len(s)] += s[: tot - o]
    return out * 0.6


def bowed(fn, dur, harm=36, vib=0.006, vib_delay=0.15, vib_rate=5.7, att=0.03, rel=0.07,
          spic=False, swell=True, trem=0.0):
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
        y += (1.0 / h) * np.sin(h * ph + rng.uniform(0, 6.28))
    nz = filt(rng.normal(0, 1, n), "bp", (1800, 8000)) * 0.07
    y = y + nz * (0.6 + 0.4 * np.abs(np.sin(ph * 0.5)))
    if spic:
        e = np.minimum(1, t / 0.006) * np.exp(-t / max(0.05, dur * 0.55))
        k = int(dur * SR)
        if k < n:
            e[k:] *= np.exp(-(t[k:] - t[k]) / 0.03)
        sc = min(n, int(0.02 * SR))
        y[:sc] += filt(rng.normal(0, 1, sc), "bp", (800, 5000)) * np.exp(-np.arange(sc) / (0.004 * SR)) * 0.5
    else:
        e = adsr(n, att, 0.12, 0.86, rel, dur)
        if swell:
            e *= 0.88 + 0.12 * np.sin(np.pi * np.clip(t / max(dur, 1e-3), 0, 1))
        sc = min(n, int(0.03 * SR))
        y[:sc] += filt(rng.normal(0, 1, sc), "bp", (900, 4500)) * np.exp(-np.arange(sc) / (0.008 * SR)) * 0.25
    if trem:
        # re-bowed pulses every `trem` seconds (the E-flat "swell" of the original)
        e *= 1 - 0.45 * (0.5 - 0.5 * np.cos(2 * np.pi * t / trem))
    return y * e


def fiddle(m, dur, vel=1.0, art="legato", scoop=False, slide_from=None, stime=0.08, det=0.0, trem=0.0):
    f1 = mtof(m) * 2 ** ((det + rng.normal(0, 2)) / 1200)
    if slide_from is not None:
        f0 = mtof(slide_from)
        fn = lambda t: f0 * (f1 / f0) ** smooth(np.clip(t / stime, 0, 1))
    elif scoop:
        fn = lambda t: f1 * 2 ** (-0.8 / 12 * np.exp(-t / 0.03))
    else:
        fn = lambda t: np.full_like(t, f1)
    if art == "spic":
        x = bowed(fn, dur, vib=0.002, spic=True)
    else:
        x = bowed(fn, dur, vib=0.0055 if dur > 0.25 else 0.002, att=0.025, trem=trem)
    for f0, g, q in ((290, 6, 2), (480, 3, 2.5), (1050, 4, 1.8), (2800, 4, 1.5)):
        x = peq(x, f0, g, q)
    return filt(x, "high", 180) * vel * 0.085


def gurdy(m, dur, vel=1.0, det=0.0):
    """hurdy-gurdy melody string: bowed by a wheel -> steady, nasal, buzzy"""
    f1 = mtof(m) * 2 ** ((det + rng.normal(0, 1.5)) / 1200)
    n = int((dur + 0.08) * SR); t = np.arange(n) / SR
    f = f1 * (1 + 0.002 * np.sin(2 * np.pi * 4.6 * t + rng.uniform(0, 6)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.zeros(n)
    for h in range(1, 30):
        if h * f1 > SR * 0.42:
            break
        y += (1.0 / h ** 0.9) * (0.55 if h % 2 == 0 else 1.0) * np.sin(h * ph + 0.2 * h)
    y = np.tanh(y * 0.7)
    y += filt(rng.normal(0, 1, n), "bp", (1500, 6000)) * 0.05
    e = adsr(n, 0.012, 0.08, 0.85, 0.04, dur)
    for f0, g, q in ((700, 5, 1.4), (1600, 4, 1.6), (300, -2, 1.0)):
        y = peq(y, f0, g, q)
    return filt(y, "high", 160) * e * vel * 0.05


# ============================================================================ winds
def pipe(m, dur, vel=1.0, chiff=1.0, slur=False, vib=True):
    """wooden recorder / tabor pipe that carries the hook.
    Measured on the reference: fundamental-dominant, 2nd/3rd partials 13-25 dB down,
    breathy, quick tongued attacks, vibrato only on long notes."""
    f1 = mtof(m) * 2 ** (rng.normal(0, 2) / 1200)
    n = int((dur + 0.1) * SR); t = np.arange(n) / SR
    long_ = dur > 0.3
    ve = np.clip((t - 0.16) / 0.25, 0, 1) if (vib and long_) else np.zeros(n)
    scoop = 0.0 if slur else -0.010 * np.exp(-t / 0.018)
    f = f1 * (1 + 0.0055 * ve * np.sin(2 * np.pi * 5.4 * t + rng.uniform(0, 6))) * (1 + scoop)
    f = f * (1 + 0.0012 * filt(rng.normal(0, 1, n), "low", 18))
    ph = 2 * np.pi * np.cumsum(f) / SR
    hs = (1.0, 0.16, 0.13, 0.045, 0.05, 0.02, 0.015)
    x = sum(a * np.sin((h + 1) * ph + 0.5 * h) for h, a in enumerate(hs) if (h + 1) * f1 < SR * 0.42)
    br = rng.normal(0, 1, n)
    tone_n = filt(br, "bp", (f1 * 0.9, f1 * 1.12)) * 0.9            # airy core of the tone
    air = filt(br, "bp", (2200, 9000)) * 0.035
    e = adsr(n, 0.006 if slur else 0.014, 0.08, 0.82, 0.045, dur)
    e *= 1 + 0.05 * ve * np.sin(2 * np.pi * 5.4 * t + 1)
    y = (x + tone_n * 0.5 + air) * e
    if not slur:
        cn = min(n, int(0.03 * SR))
        ch = filt(rng.normal(0, 1, cn), "bp", (1400, 6000)) * np.exp(-np.arange(cn) / (0.006 * SR))
        ch += 0.35 * np.sin(2 * ph[:cn]) * np.exp(-np.arange(cn) / (0.008 * SR))   # brief overblow
        y[:cn] += ch * 0.32 * chiff
    y = peq(y, 1100, 2.0, 1.2)
    return y * vel * 0.16


def flute(m, dur, vel=1.0, chiff=1.0, vib=True):
    """transverse wooden flute (octave doubling in the climaxes)"""
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


def drone(seconds, midis, levels=None, buzz_times=(), fade=0.08):
    """bagpipe / hurdy-gurdy drone strings, slowly beating"""
    n = int(seconds * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    levels = levels or [1.0] * len(midis)
    for m, lv in zip(midis, levels):
        f = mtof(m) * (1 + 0.0012 * np.sin(2 * np.pi * rng.uniform(0.15, 0.35) * t + rng.uniform(0, 6)))
        ph = 2 * np.pi * np.cumsum(f) / SR
        for h in range(1, 26):
            if h * mtof(m) > 8000:
                break
            out += lv * (1 / h ** 1.05) * (0.6 if h % 2 == 0 else 1) * np.sin(h * ph + rng.uniform(0, 6))
    out = filt(peq(out, 750, 4, 1.4), "high", 110) * 0.02
    if len(buzz_times):
        ph = 2 * np.pi * mtof(midis[0] + 12) * t
        raw = filt(np.sign(np.sin(ph)) * np.abs(np.sin(ph)) ** 0.3 + 0.5 * rng.normal(0, 1, n), "bp", (400, 4500))
        g = np.zeros(n)
        for tt, v in buzz_times:
            a = int(tt * SR)
            if 0 <= a < n:
                seg = np.arange(min(n - a, int(0.2 * SR)))
                g[a:a + len(seg)] = np.maximum(g[a:a + len(seg)], v * np.exp(-seg / (0.07 * SR)) * np.minimum(1, seg / 60))
        out += raw * g * 0.04
    fd = np.clip(np.minimum(t / fade, (seconds - t) / fade), 0, 1)
    return out * fd


# ============================================================================ bass
def deep_bass(m, d, vel=1.0, pop=False, glide_from=None, gtime=0.07):
    """deep, bouncy plucked bass: clean sub fundamental + saturated growl that decays"""
    f = mtof(m)
    n = int((d + 0.06) * SR); t = np.arange(n) / SR
    fi = np.full(n, f)
    if glide_from is not None:
        k = smooth(np.clip(t / gtime, 0, 1))
        fi = mtof(glide_from) * (f / mtof(glide_from)) ** k
    fi = fi * (1 + 0.035 * np.exp(-t / 0.01))
    ph = 2 * np.pi * np.cumsum(fi) / SR
    sub = np.sin(ph)
    growl = sum(np.sin(h * ph) / h ** (0.9 if pop else 1.2) for h in range(2, 12) if h * f < 7000)
    genv = np.exp(-t / (0.09 if pop else 0.06))
    growl = filt(growl, "low", 2400 if pop else 1300) * genv
    body = 0.15 * np.sin(2 * ph + 0.3) + 0.05 * np.sin(3 * ph)
    y = sub * 1.0 + body + np.tanh(growl * 2.2) * (0.55 if pop else 0.4)
    if pop:
        y[:250] += filt(rng.normal(0, 1, 250), "bp", (1500, 5000)) * np.exp(-np.arange(250) / 45) * 0.4
    e = np.minimum(1, t / 0.0025)
    k = int(d * SR)
    if k < n:
        e[k:] *= np.exp(-(t[k:] - t[k]) / 0.02)
    return y * e * vel * 0.36


def sub_slide(points, d, vel=1.0):
    """sustained sub bass that slides between notes (bass-drop section).
    points: list of (time_in_note, midi)"""
    n = int((d + 0.05) * SR); t = np.arange(n) / SR
    fi = np.zeros(n)
    for i, (tt, m) in enumerate(points):
        a = int(tt * SR)
        fi[a:] = mtof(m)
    # 45 ms portamento between targets
    k = int(0.045 * SR)
    fi = np.convolve(np.pad(fi, (k, 0), mode="edge"), np.ones(k) / k, mode="valid")[:n]
    ph = 2 * np.pi * np.cumsum(fi) / SR
    y = np.sin(ph) + 0.28 * np.sin(2 * ph + 0.3) + 0.1 * np.sin(3 * ph)
    grit = np.tanh(3 * np.sin(ph)) - np.sin(ph)
    y += filt(grit, "low", 900) * 0.35
    e = np.minimum(1, t / 0.004) * np.clip((d + 0.05 - t) / 0.05, 0, 1)
    e *= 0.85 + 0.15 * np.exp(-t / 0.15)
    return y * e * vel * 0.34


# ============================================================================ drums & percussion
def club_kick(vel=1.0, long=False):
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 47 + 165 * np.exp(-t / 0.026) + 40 * np.exp(-t / 0.004)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.36 if long else 0.26))
    click = filt(rng.normal(0, 1, n), "bp", (2500, 9000)) * np.exp(-t / 0.0025) * 0.4
    knock = filt(rng.normal(0, 1, n), "bp", (160, 700)) * np.exp(-t / 0.014) * 0.24
    y = np.tanh((body * 1.25 + click + knock) * 1.7)
    return filt(y, "low", 9000) * vel * 0.6


def clap(vel=1.0):
    n = int(0.32 * SR); t = np.arange(n) / SR
    nz = filt(rng.normal(0, 1, n), "bp", (900, 5200))
    e = np.zeros(n)
    for k, off in enumerate((0.0, 0.008, 0.017, 0.025)):
        o = int(off * SR)
        e[o:] += np.exp(-t[: n - o] / (0.0055 if k < 3 else 0.075)) * (0.75 if k < 3 else 1)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04) * 0.45
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


def tick(vel=1.0):
    """tight 16th tick of the bass drop"""
    n = int(0.05 * SR); t = np.arange(n) / SR
    return filt(rng.normal(0, 1, n), "bp", (6000, 14000)) * np.exp(-t / 0.008) * vel * 0.12


def riq(vel=1.0, body_hz=622.0, long=False):
    """frame drum with jingles: the pitched offbeat 'tak' of the reference
    (~620 Hz skin tone decaying in ~40 ms + 4-9 kHz jingles)"""
    n = int((0.3 if long else 0.18) * SR); t = np.arange(n) / SR
    f = body_hz * (1 + 0.06 * np.exp(-t / 0.006))
    skin = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.032)
    skin += 0.35 * np.sin(2 * np.pi * np.cumsum(f * 1.58) / SR) * np.exp(-t / 0.018)
    slap = filt(rng.normal(0, 1, n), "bp", (1200, 4000)) * np.exp(-t / 0.006) * 0.5
    jing = sum(np.sin(2 * np.pi * fj * rng.uniform(0.985, 1.015) * t + rng.uniform(0, 6))
               for fj in (4300, 5300, 6050, 7400, 8650))
    jing = (jing * 0.1 + filt(rng.normal(0, 1, n), "bp", (4000, 10000))) * np.exp(-t / (0.09 if long else 0.05))
    jing *= 1 + 0.35 * np.sin(2 * np.pi * 34 * t)
    return (skin * 0.55 + slap + jing * 0.55) * vel * 0.2


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


def tabor(vel=1.0):
    """medieval snare drum (tabor with a gut snare) for rolls and backbeats"""
    n = int(0.25 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(205 * (1 + 0.3 * np.exp(-t / 0.01))) / SR
    head = (np.sin(ph) + 0.5 * np.sin(1.6 * ph)) * np.exp(-t / 0.05)
    snr = filt(rng.normal(0, 1, n), "bp", (1500, 7000)) * np.exp(-t / 0.07)
    return (head * 0.5 + snr * 0.7) * vel * 0.22


def crash(dur=2.2, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * rng.uniform(3000, 12000) * t + rng.uniform(0, 6)) * rng.uniform(0.2, 1) for _ in range(24))
    y = y * 0.04 + filt(rng.normal(0, 1, n), "bp", (3500, 11000))
    return y * np.exp(-t / (dur * 0.33)) * np.minimum(1, t / 0.002) * vel * 0.1


def rev_cym(dur, vel=1.0):
    c = crash(dur, vel)[::-1]; t = np.arange(len(c)) / SR
    return c * (t / dur) ** 1.5 * 1.5


def sweep(dur, vel=1.0, up=True):
    n = int(dur * SR); nz = rng.normal(0, 1, n); out = np.zeros(n); blk = 1024
    for i in range(0, n, blk):
        k = i / n if up else 1 - i / n
        fc = 400 + 6000 * k ** 2
        seg = filt(nz[max(0, i - 512): i + blk], "bp", (fc * 0.7, fc * 1.4))
        out[i:i + blk] = seg[-len(out[i:i + blk]):]
    t = np.arange(n) / dur / SR
    return out * ((t ** 2) if up else (1 - t) ** 2) * vel * 0.1


def boom(vel=1.0):
    """low impact under section downbeats"""
    n = int(1.4 * SR); t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    y += filt(rng.normal(0, 1, n), "low", 400) * np.exp(-t / 0.08) * 0.3
    return np.tanh(y * 1.4) * vel * 0.45


def growl_bass(points, d, vel=1.0, gtime=0.035):
    """legato gliding growl bass of the drop: every note change re-opens the tone
    (bright 'wah' that settles), portamento between notes, warm saturation.
    points: list of (time_in_phrase_seconds, midi)"""
    n = int((d + 0.06) * SR); t = np.arange(n) / SR
    fi = np.zeros(n); since = np.zeros(n)
    marks = sorted(points)
    for i, (tt, m) in enumerate(marks):
        a = int(tt * SR)
        b = int(marks[i + 1][0] * SR) if i + 1 < len(marks) else n
        fi[a:b] = mtof(m)
        since[a:b] = (np.arange(b - a)) / SR
    k = max(1, int(gtime * SR))
    fi = np.convolve(np.pad(fi, (k, 0), mode="edge"), np.ones(k) / k, mode="valid")[:n]
    ph = 2 * np.pi * np.cumsum(fi) / SR
    open_ = 0.25 + 0.75 * np.exp(-since / 0.11)
    y = np.sin(ph) * 1.0
    for h in range(2, 11):
        y += np.sin(h * ph + 0.2 * h) / h ** 1.15 * np.clip(open_ * 1.6 - (h - 2) * 0.1, 0, 1)
    y = np.tanh(y * 1.4)
    y = filt(y, "low", 1600)
    y += 0.5 * np.sin(ph)                     # clean sub under the growl
    e = np.minimum(1, t / 0.004) * np.clip((d + 0.06 - t) / 0.06, 0, 1)
    return y * e * vel * 0.3
