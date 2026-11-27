"""
FOLLOW THE PIPER -- instruments.

  recorder()      sampled baroque recorders (alto lead, soprano 8va, tenor low) with
                  scoops, grace notes, trills, legato joins and controllable vibrato
  psaltery()      sampled bowed / spiccato / plucked psaltery (rhythmic medieval strings)
  strum()         sampled strumstick (plucked folk lute colour)
  gurdy_*()       physical bowed-string waveguide hurdy-gurdy: drone, keyed melody, buzzing chien
  bass()          clean physical synth bass (sine core, filtered harmonics, punch)
  kick() stomp()  synthesised + sampled drums; percussion() for VCSL hits
  voice()         source-filter human voice (glottal pulse + Klatt formant cascade):
                  choir(), hum(), chant(), breath(), laugh()
  bell()          tubular / hand bells
"""
import numpy as np
from numba import njit
from dsp import (SR, mtof, db, lp, hp, bp, peq, hs, ls, noise, pink, adsr, expdec, resample_play, rng,
                 softclip, onepole_lp, lp4)
import samples as S


# =========================================================================== recorder
def _cents_curve(n, scoop=0.0, scoop_t=0.05, vib=0.0, vib_rate=5.3, vib_delay=0.18, fall=0.0, fall_t=0.08,
                 drift=3.0, trill=None):
    t = np.arange(n) / SR
    c = np.zeros(n)
    if scoop:
        c += scoop * np.exp(-t / (scoop_t / 3))
    if vib:
        ramp = np.clip((t - vib_delay) / 0.25, 0, 1)
        ph = rng().uniform(0, 2 * np.pi)
        rate = vib_rate * (1 + 0.04 * np.sin(2 * np.pi * 0.7 * t))
        c += vib * ramp * np.sin(2 * np.pi * np.cumsum(rate) / SR + ph)
    if fall:
        tt = t - (n / SR - fall_t)
        c += np.where(tt > 0, fall * (tt / fall_t) ** 2, 0)
    if drift:
        w = onepole_lp(noise(n), 3.0)
        w /= (np.abs(w).max() + 1e-9)
        c += drift * w
    if trill is not None:      # (interval_semitones, rate_hz, start_s)
        iv, rate, st = trill
        sq = (np.sin(2 * np.pi * rate * np.maximum(t - st, 0)) > 0).astype(float) * (t > st)
        sq = onepole_lp(sq, 60)
        c += sq * iv * 100
    return c


def recorder(midi, dur, vel=1.0, which="alto", art=None, slur=False, scoop=0.0, vib=None, fall=0.0,
             trill=None, release=0.05, breath=0.0, tone=0.0, cents=0.0):
    """one recorder note. dur = sounding length (s) before release.
    slur: legato entry (skip the chiff, short fade-in) -- used for joined notes."""
    I = S.inst(which)
    if art is None:
        art = "stac" if dur < 0.13 and not slur else ("vib" if (dur > 0.55 and "vib" in I.zones and vib is None) else "sus")
    z = I.pick(art, midi)
    x = I.audio(z)
    ratio0 = mtof(midi) / z["f0"]
    n = int((dur + release) * SR)
    vib_amt = 0.0 if (vib is None or art == "vib") else vib
    c = _cents_curve(n, scoop=scoop, vib=vib_amt, fall=fall, trill=trill)
    ratio = ratio0 * 2 ** ((c + cents) / 1200)
    start = 0.0
    if slur:
        start = 0.045 * SR        # skip the articulation transient
    if art == "stac":
        # staccato samples are short: stretch decay with a sustain sample crossfade if needed
        y = resample_play(x, ratio, start=start)
    else:
        y = resample_play(x, ratio, start=start)
    # normalise by measured sustain level, register curve (recorders are louder up high)
    w = x[int(0.012 * SR):int(0.11 * SR)]
    ref = np.sqrt(np.mean(w ** 2))          # same early window for every articulation
    y = y / (ref + 1e-9) * 0.12
    reg = 1.0 + 0.012 * (midi - 76)
    y *= vel * reg
    env = np.ones(n)
    if slur:
        k = int(0.012 * SR); env[:k] = np.linspace(0, 1, k)
    R = int(release * SR)
    env[-R:] *= np.cos(np.linspace(0, np.pi / 2, R)) ** 2
    y *= env
    if breath > 0:              # extra breathy air on top (for the darker, closer Piper)
        b = bp(noise(n), 2600 + 300 * (midi - 72) / 12, 0.8) * adsr(n, 0.02, 0.1, 0.5, release)
        y += b * breath * 0.02 * vel
    if tone:
        y = hs(y, 3000, tone)
    return y


# =========================================================================== psaltery / strumstick
def psaltery(midi, dur, vel=1.0, art="spic", release=0.08):
    I = S.inst("psaltery")
    z = I.pick(art, midi)
    x = I.audio(z)
    ratio = mtof(midi) / z["f0"]
    n = int((dur + release) * SR)
    y = resample_play(x, ratio, n_out=n)
    ref = z["rms"] if art == "bow" else z["peak"] * 0.3
    y = y / (ref + 1e-9) * 0.1 * vel
    R = int(release * SR)
    y[-R:] *= np.cos(np.linspace(0, np.pi / 2, R)) ** 2
    return y


def strum(midi, dur, vel=1.0, layer="v3", release=0.12):
    I = S.inst("strum")
    z = I.pick(layer, midi)
    x = I.audio(z)
    ratio = mtof(midi) / z["f0"]
    n = int((dur + release) * SR)
    y = resample_play(x, ratio, n_out=n)
    y = y / (z["peak"] + 1e-9) * 0.35 * vel
    R = int(release * SR)
    y[-R:] *= np.cos(np.linspace(0, np.pi / 2, R)) ** 2
    return y


# =========================================================================== hurdy-gurdy (bowed waveguide)
@njit(cache=True)
def _bowed(f0, vbow, force, beta, seed, rosin):
    """STK-style bowed string: two fractional delay lines around the bow point, friction
    table junction, one-pole loss at the bridge. f0, vbow, force are per-sample arrays."""
    n = len(f0)
    np.random.seed(seed)
    maxl = 4096
    neck = np.zeros(maxl); brid = np.zeros(maxl)
    wn = 0; wb = 0
    out = np.zeros(n)
    lpz = 0.0
    lastb = 0.0
    lastn = 0.0
    for i in range(n):
        L = SR_C / f0[i] - 0.55
        ln = L * (1.0 - beta); lb = L * beta
        # read neck delay (fractional)
        rp = wn - ln
        while rp < 0:
            rp += maxl
        i0 = int(rp); fr = rp - i0
        nOut = neck[i0 % maxl] * (1 - fr) + neck[(i0 + 1) % maxl] * fr
        rp = wb - lb
        while rp < 0:
            rp += maxl
        i0 = int(rp); fr = rp - i0
        bOut = brid[i0 % maxl] * (1 - fr) + brid[(i0 + 1) % maxl] * fr
        # bridge reflection with loss
        lpz = 0.6 * bOut + 0.4 * lpz
        bridgeRefl = -lpz * 0.995
        nutRefl = -nOut
        sv = bridgeRefl + nutRefl
        vb = vbow[i] * (1.0 + rosin * (np.random.random() - 0.5))
        dv = vb - sv
        slope = 5.0 - 4.0 * force[i]
        tb = abs(dv * slope) + 0.75
        tb = tb ** -4.0
        if tb > 1.0:
            tb = 1.0
        nv = dv * tb
        neck[wn % maxl] = bridgeRefl + nv
        brid[wb % maxl] = nutRefl + nv
        wn = (wn + 1) % maxl; wb = (wb + 1) % maxl
        out[i] = bOut
    return out


SR_C = float(SR)


def _gurdy_body(y):
    y = hp(y, 90)
    y = peq(y, 280, 5, 2.0)
    y = peq(y, 520, 3, 2.5)
    y = peq(y, 1150, 4, 2.0)
    y = peq(y, 2300, 3, 2.0)
    y = peq(y, 3400, 2, 2.5)
    y = lp(y, 6500)
    return y


def gurdy_string(midi_curve, vbow, force=0.35, beta=0.127, seed=1, rosin=0.08):
    """midi_curve: per-sample midi pitch (allows keyed melody); returns mono"""
    f0 = mtof(midi_curve)
    y = _bowed(f0.astype(np.float64), vbow.astype(np.float64), np.full(len(f0), force), beta, seed, rosin)
    return _gurdy_body(y)


def wheel(n, level=0.22, crank_hz=2.27, wobble=0.18, attack=0.15, release=0.2):
    """bow velocity from the wheel: steady with a small once-per-revolution wobble"""
    t = np.arange(n) / SR
    v = level * (1 + wobble * np.sin(2 * np.pi * crank_hz * t + rng().uniform(0, 6.28)) ** 2 * 0.5)
    env = adsr(n, attack, 0.05, 1.0, release)
    return v * env


def chien(trompette, pulses, depth=1.0):
    """buzzing bridge: rhythmic crank accents make the 'dog' rattle on the trompette string.
    pulses: per-sample 0..1 accent envelope."""
    x = hp(trompette, 600)
    rattle = np.sign(x) * np.abs(x) ** 0.25
    rattle = bp(rattle, 2400, 0.9) + 0.5 * bp(rattle, 4200, 1.2)
    return rattle * pulses * depth * 0.35


# =========================================================================== bass
def bass(midi, dur, vel=1.0, bright=1.0, release=0.03, punch=1.0, sub=1.0):
    f = mtof(midi)
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    # pitch: tiny drop into the note for punch
    fc = f * 2 ** ((40 * punch * np.exp(-t / 0.012)) / 1200)
    ph = 2 * np.pi * np.cumsum(fc) / SR
    core = np.sin(ph) * sub
    # harmonics: band-limited saw through a decaying lowpass
    saw = np.zeros(n)
    kmax = int(min(40, (SR / 2.5) / f))
    for k in range(2, kmax + 1):
        saw += np.sin(k * ph) / k * (-1) ** k
    # decaying lowpass "pluck" without zipper noise: crossfade a bright and a dark copy
    dark = lp(saw, 180, 0.9)
    brt = lp(saw, 180 + 900 * bright * vel, 0.9)
    k = np.exp(-t / 0.07)
    sat = dark + (brt - dark) * k
    y = core + 0.95 * sat
    env = adsr(n, 0.003, 0.09, 0.72, release)
    y = np.tanh(2.0 * y * env) / np.tanh(2.0)
    # mid "knock" so the gallop reads on phones (2nd/3rd harmonic emphasis, a little 700 Hz grit)
    y = peq(y, 2 * f, 3.0, 1.2)
    y = peq(y, 3 * f, 1.0, 1.4)
    y = y + bp(np.tanh(4 * y), 750, 1.0) * 0.06 * bright
    return y * vel * 0.5


# =========================================================================== drums
def kick(vel=1.0, tune=52.0, decay=0.15, click=1.3, layer_skin=None):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = tune + (240 - tune) * np.exp(-t / 0.028) + 40 * np.exp(-t / 0.003)
    ph = 2 * np.pi * np.cumsum(f) / SR
    amp = np.exp(-t / decay) * (1 - np.exp(-t / 0.0008))
    amp *= 1 - 0.35 * np.clip((t - 0.12) / 0.15, 0, 1)          # tighten the tail so beats don't smear
    body = np.sin(ph) * amp
    body = np.tanh(body * 2.4) / np.tanh(2.4)                    # harmonics -> audible punch on small speakers
    ck = (hp(noise(n), 2500) * np.exp(-t / 0.004) * 0.3 + bp(noise(n), 1200, 1.2) * np.exp(-t / 0.006) * 0.25) * click
    knock = np.sin(2 * np.pi * 115 * t) * np.exp(-t / 0.035) * 0.35   # 100-200 Hz 'chest' punch
    beater = bp(noise(n), 2800, 1.4) * np.exp(-t / 0.007) * 0.35 * click + \
        np.sin(2 * np.pi * 1150 * t) * np.exp(-t / 0.012) * 0.12                # beater 'tok': the 1 on phones
    thump = lp(noise(n), 180) * np.exp(-t / 0.025) * 0.4
    y = body + ck + thump + knock + beater
    if layer_skin is not None:
        s = layer_skin[:n] if len(layer_skin) >= n else np.pad(layer_skin, (0, n - len(layer_skin)))
        y += hp(s, 120) * 0.7
    return y * vel * 0.9


def stomp(vel=1.0, crowd=6, spread=0.012):
    """group of synchronised foot stomps on a wooden floor"""
    n = int(0.5 * SR)
    out = np.zeros((n, 2))
    for k in range(crowd):
        d = int(abs(rng().normal(0, spread)) * SR) if k else 0
        t = np.arange(n - d) / SR
        f = rng().uniform(62, 88)
        boom = np.sin(2 * np.pi * np.cumsum(f + 60 * np.exp(-t / 0.01)) / SR) * np.exp(-t / 0.045)
        wood = bp(noise(n - d), rng().uniform(170, 260), 2.2) * np.exp(-t / 0.05) * 1.4
        scuff = hp(noise(n - d), 1500) * np.exp(-t / 0.008) * 0.12
        heel = lp(noise(n - d), 400) * np.exp(-t / 0.02) * 0.9
        g = rng().uniform(0.6, 1.0) / np.sqrt(crowd)
        one = (boom * 0.9 + wood + scuff + heel) * g
        p = 0.0 if k == 0 else rng().uniform(-0.7, 0.7)           # dancers spread across the floor
        th = (p + 1) * np.pi / 4
        out[d:, 0] += one * np.cos(th) * np.sqrt(2); out[d:, 1] += one * np.sin(th) * np.sqrt(2)
    return out * vel * 0.8


def snare_roll(dur, vel0=0.2, vel1=1.0, rate=16, kit_hits=None):
    """sample-based crescendo roll; rate in strokes per second"""
    n = int((dur + 0.6) * SR)
    out = np.zeros((n, 2))
    k = int(dur * rate)
    for i in range(k):
        t = i / rate
        v = vel0 + (vel1 - vel0) * (t / dur) ** 1.6
        h = kit_hits[rng().integers(len(kit_hits))]
        j = max(0, int((t + rng().normal(0, 0.002)) * SR))
        h2 = h if h.ndim == 2 else np.stack([h, h], 1)
        m = min(len(h2), n - j)
        if m > 0:
            out[j:j + m] += h2[:m] * v
    return out


# =========================================================================== voice (source-filter)
VOWELS = {   # Klatt-style formant (F, BW) for a male voice; scaled for others
    "a": ([700, 1220, 2600, 3300, 3750], [80, 90, 120, 150, 200]),
    "o": ([450, 800, 2620, 3300, 3750], [70, 80, 100, 150, 200]),
    "u": ([325, 700, 2530, 3300, 3750], [60, 80, 100, 150, 200]),
    "e": ([500, 1750, 2600, 3300, 3750], [70, 90, 110, 150, 200]),
    "i": ([300, 2200, 2950, 3400, 3900], [60, 90, 110, 150, 200]),
    "m": ([260, 1150, 2350, 3300, 3750], [50, 300, 200, 300, 300]),   # hum: nasal murmur
    "n": ([280, 1500, 2500, 3300, 3750], [50, 250, 200, 300, 300]),
    "h": ([700, 1220, 2600, 3300, 3750], [200, 200, 250, 300, 300]),
}
VOICE_SCALE = {"bass": 0.93, "bar": 1.0, "ten": 1.05, "alt": 1.13, "sop": 1.2, "child": 1.32}


@njit(cache=True)
def _voice_core(f0, amp, asp, F, BW, seed, oq, jitter, shimmer):
    """glottal Rosenberg pulse (flow derivative) + aspiration -> 5-formant cascade.
    F, BW: (5, n) per-sample formant tracks."""
    n = len(f0)
    np.random.seed(seed)
    out = np.zeros(n)
    ph = 0.0
    y1 = np.zeros(5); y2 = np.zeros(5)
    prev = 0.0
    jit = 0.0; shim = 1.0
    hpz = 0.0
    for i in range(n):
        ph += f0[i] * (1.0 + jit) / SR_C
        if ph >= 1.0:
            ph -= 1.0
            jit = (np.random.random() - 0.5) * 2 * jitter
            shim = 1.0 + (np.random.random() - 0.5) * 2 * shimmer
        tp = oq * 0.66; tn = oq * 0.34
        if ph < tp:
            g = 0.5 * (1 - np.cos(np.pi * ph / tp))
        elif ph < tp + tn:
            g = np.cos(0.5 * np.pi * (ph - tp) / tn)
        else:
            g = 0.0
        d = (g - prev) * 30.0          # flow derivative (radiation)
        prev = g
        # aspiration noise, louder during the open phase
        wn = np.random.random() - 0.5
        hpz = 0.75 * hpz + 0.25 * wn
        noi = (wn - hpz) * (0.4 + 0.6 * g)
        x = d * amp[i] * shim + noi * asp[i]
        # formant cascade (unity-DC-gain Klatt resonators)
        for k in range(5):
            r = np.exp(-np.pi * BW[k, i] / SR_C)
            B = 2 * r * np.cos(2 * np.pi * F[k, i] / SR_C)
            C = -r * r
            A = 1 - B - C
            yk = A * x + B * y1[k] + C * y2[k]
            y2[k] = y1[k]; y1[k] = yk
            x = yk
        out[i] = x
    return out


def _tracks(vseq, n, scale):
    """vseq: list of (t_sec, vowel) keyframes -> per-sample F/BW with smooth glides"""
    F = np.zeros((5, n)); BW = np.zeros((5, n))
    ts = [int(t * SR) for t, _ in vseq] + [n]
    for j, (t, v) in enumerate(vseq):
        a, b = ts[j], ts[j + 1]
        f, bw = VOWELS[v]
        F[:, a:b] = (np.array(f) * scale)[:, None]
        BW[:, a:b] = np.array(bw)[:, None]
    # glide between vowels (40 ms)
    k = int(0.04 * SR)
    from scipy.ndimage import uniform_filter1d
    F = uniform_filter1d(F, k, axis=1, mode="nearest")
    BW = uniform_filter1d(BW, k, axis=1, mode="nearest")
    return F, BW


def voice(midi_curve, amp_curve, vseq, kind="bar", breath=0.15, vib=25, vib_rate=5.4, seed=None,
          oq=0.6, jitter=0.012, shimmer=0.06, drift=10):
    """one singer. midi_curve, amp_curve: per-sample arrays."""
    n = len(midi_curve)
    seed = int(rng().integers(1 << 30)) if seed is None else seed
    r = np.random.default_rng(seed)
    t = np.arange(n) / SR
    rate = vib_rate * r.uniform(0.9, 1.1)
    vibc = vib * r.uniform(0.6, 1.2) * np.clip((t - 0.25) / 0.4, 0, 1) * np.sin(2 * np.pi * rate * t + r.uniform(0, 6))
    dr = onepole_lp(r.standard_normal(n), 1.5); dr = dr / (np.abs(dr).max() + 1e-9) * drift
    f0 = mtof(midi_curve + (vibc + dr + r.normal(0, 6)) / 100)
    scale = VOICE_SCALE[kind] * r.uniform(0.96, 1.04)
    F, BW = _tracks(vseq, n, scale)
    asp = amp_curve * breath
    y = _voice_core(f0.astype(np.float64), amp_curve.astype(np.float64), asp.astype(np.float64), F, BW,
                    seed % (2 ** 31 - 1), oq, jitter, shimmer)
    return hp(y, 70)


def _amp(n, a, r, sustain=1.0, swell=0.0):
    e = adsr(n, a, 0.05, sustain, r)
    if swell:
        e *= np.linspace(1 - swell, 1, n)
    return e


def choir(midis, dur, vowel_seq=(("a", 0.0),), kinds=None, voices_per=4, amp=1.0, attack=0.25, release=0.4,
          breath=0.2, spread=0.03, vib=22, swell=0.0, gliss=None):
    """chord pad of many singers. midis: list of pitches (one part each).
    vowel_seq: ((vowel, frac_time), ...). Returns stereo."""
    n = int((dur + release) * SR)
    out = np.zeros((n, 2))
    for pi, m in enumerate(midis):
        kind = kinds[pi] if kinds else ("bass" if m < 52 else "ten" if m < 60 else "alt" if m < 67 else "sop")
        for v in range(voices_per):
            off = abs(rng().normal(0, spread))
            k = int(off * SR)
            mc = np.full(n - k, float(m))
            if gliss is not None:
                mc += np.linspace(0, gliss, n - k)
            ac = _amp(n - k, attack * rng().uniform(0.8, 1.2), release, swell=swell) * amp
            vs = [(fr * dur, vw) for vw, fr in vowel_seq]
            y = voice(mc, ac, vs, kind=kind, breath=breath, vib=vib)
            p = rng().uniform(-0.8, 0.8)
            th = (p + 1) * np.pi / 4
            out[k:, 0] += y * np.cos(th); out[k:, 1] += y * np.sin(th)
    return out / np.sqrt(len(midis) * voices_per) * 0.5


def hum(notes, total, kinds=("bar", "ten", "alt"), voices_per=3, amp=1.0, spread=0.012):
    """rhythmic group humming: notes = [(t, dur, midi)] relative; legato 'mm' syllables"""
    n = int((total + 0.4) * SR)
    out = np.zeros((n, 2))
    for kind in kinds:
        for v in range(voices_per):
            mc = np.zeros(n); ac = np.zeros(n)
            last = notes[0][2]
            for (t, d, m) in notes:
                a = int((t + rng().normal(0, spread)) * SR); a = max(a, 0)
                b = min(n, a + int(d * SR))
                oc = -12 if kind in ("bar", "bass") else 0
                mc[a:] = m + oc
                seg = b - a
                if seg > 10:
                    e = adsr(seg, 0.03, 0.06, 0.8, min(0.08, d * 0.4))
                    ac[a:b] = np.maximum(ac[a:b], e)
                last = m
            mc[mc == 0] = last
            from scipy.ndimage import uniform_filter1d
            mc = uniform_filter1d(mc, int(0.025 * SR))
            y = voice(mc, ac * amp, [(0, "m")], kind=kind, breath=0.08, vib=12, oq=0.7)
            y = lp(y, 1400)
            p = rng().uniform(-0.6, 0.6); th = (p + 1) * np.pi / 4
            out[:, 0] += y * np.cos(th); out[:, 1] += y * np.sin(th)
    return out / np.sqrt(len(kinds) * voices_per)


def chant(syllables, total, kinds=("bar", "ten", "alt"), voices_per=3, amp=1.0, spread=0.01):
    """wordless group chant: syllables = [(t, dur, midi, 'hV' or 'V' or 'mV')]"""
    n = int((total + 0.5) * SR)
    out = np.zeros((n, 2))
    for kind in kinds:
        for v in range(voices_per):
            mc = np.zeros(n); ac = np.zeros(n); asp = np.zeros(n)
            vseq = [(0.0, "m")]
            last = syllables[0][2]
            for (t, d, m, syl) in syllables:
                a = max(0, int((t + rng().normal(0, spread)) * SR)); b = min(n, a + int(d * SR))
                oc = -12 if kind in ("bar", "bass") else 0
                mc[a:] = m + oc
                cons = syl[0] if len(syl) > 1 else ""
                vw = syl[-1]
                seg = b - a
                if seg < 20:
                    continue
                e = adsr(seg, 0.012, 0.08, 0.55, min(0.07, d * 0.4))
                ac[a:b] = np.maximum(ac[a:b], e)
                if cons == "h":
                    k = int(0.045 * SR)
                    asp[max(0, a - k):a] += np.linspace(0, 1.2, min(k, a))
                    vseq.append((a / SR - 0.045, "h"))
                elif cons == "m":
                    vseq.append((a / SR, "m"))
                    a = a + int(0.05 * SR)
                vseq.append((a / SR, vw))
            mc[mc == 0] = last
            from scipy.ndimage import uniform_filter1d
            mc = uniform_filter1d(mc, int(0.02 * SR))
            vseq = sorted([(max(0.0, tt), vv) for tt, vv in vseq], key=lambda q: q[0])
            y = voice(mc, ac * amp, vseq, kind=kind, breath=0.22, vib=8, oq=0.55)
            # inject the 'h' aspiration through the same voice filter (cheap: filtered noise)
            y += bp(noise(n), 1400, 0.7) * onepole_lp(asp, 40) * 0.025 * amp
            p = rng().uniform(-0.7, 0.7); th = (p + 1) * np.pi / 4
            out[:, 0] += y * np.cos(th); out[:, 1] += y * np.sin(th)
    return out / np.sqrt(len(kinds) * voices_per)


def breath(dur=0.32, people=6, inhale=True, amp=1.0, spread=0.008):
    """synchronised group breath (inhale: rising hiss; exhale: short 'hah' burst)"""
    n = int((dur + 0.2) * SR)
    out = np.zeros((n, 2))
    for k in range(people):
        d = int(abs(rng().normal(0, spread)) * SR)
        m = n - d
        t = np.arange(m) / SR
        if inhale:
            e = np.clip(t / dur, 0, 1) ** 1.7 * (t < dur)
            e[int(dur * SR) - 200:int(dur * SR)] *= np.linspace(1, 0, 200) if int(dur * SR) <= m else 1
            w = noise(m)
            y = bp(w, rng().uniform(1000, 1500), 1.3) * 0.7 + bp(w, rng().uniform(2600, 3400), 2.0) * 0.5 + \
                bp(w, 500, 1.5) * 0.3
        else:
            e = adsr(m, 0.008, 0.05, 0.4, 0.12, sus_len=dur * 0.4)
            w = noise(m)
            y = bp(w, rng().uniform(700, 1000), 1.2) + bp(w, 1700, 1.5) * 0.6
        y *= e
        p = rng().uniform(-0.8, 0.8); th = (p + 1) * np.pi / 4
        out[d:, 0] += y * np.cos(th); out[d:, 1] += y * np.sin(th)
    return out / np.sqrt(people) * amp * 0.25


def laugh(n_ha=6, f_start=330, f_end=250, rate=7.5, kind="child", amp=1.0, breathy=0.6):
    """breathy 'ha-ha-ha' with falling pitch; mono"""
    ha = 1.0 / rate
    total = n_ha * ha + 0.45
    n = int(total * SR)
    mc = np.zeros(n); ac = np.zeros(n)
    t = np.arange(n) / SR
    fcur = 69 + 12 * np.log2(np.linspace(f_start, f_end, n) / 440)
    for i in range(n_ha):
        a = int(i * ha * SR * rng().uniform(0.95, 1.05)); L = int(ha * SR * 0.62)
        if a + L >= n:
            break
        v = 1.0 - 0.6 * i / n_ha
        e = np.sin(np.linspace(0, np.pi, L)) ** 0.7
        ac[a:a + L] = e * v
    # each 'ha' has its own pitch peak
    mc = fcur + 1.5 * np.sin(2 * np.pi * rate * t) ** 2
    # final inhale
    y = voice(mc, ac * amp, [(0, "a"), (n_ha * ha * 0.6, "e")], kind=kind, breath=breathy * 3, vib=0,
              oq=0.45, jitter=0.03, shimmer=0.15)
    inh = breath(0.3, people=1, inhale=True, amp=amp * 0.9)[:, 0]
    k = int(n_ha * ha * SR) + int(0.06 * SR)
    m = min(len(inh), n - k)
    if m > 0:
        y[k:k + m] += inh[:m]
    return y


# =========================================================================== bells
def bell(note_label="D4", vel=1.0, shift=0.0, which="chimes", length=6.0):
    import glob, os
    if which == "chimes":
        ps = sorted(glob.glob(os.path.join(S.VCSL, f"Idiophones/Struck Idiophones/Tubular Bells 1/chimes_{note_label}_f*_*.wav")))
        if not ps:
            ps = sorted(glob.glob(os.path.join(S.VCSL, f"Idiophones/Struck Idiophones/Tubular Bells 1/chimes_{note_label}_*.wav")))
        x = S.onset_trim(S.load(ps[0], mono=False), 0.02)
    else:
        ps = sorted(glob.glob(os.path.join(S.VCSL, "Idiophones/Struck Idiophones/Hand Bells, Nepalese/*.wav")))
        x = S.onset_trim(S.load(ps[int(note_label) % len(ps)], mono=False), 0.02)
    if shift:
        r = 2 ** (shift / 12)
        x = np.stack([resample_play(x[:, c], r) for c in range(2)], 1)
    n = min(len(x), int(length * SR))
    x = x[:n] / (np.abs(x).max() + 1e-9) * vel
    x[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))[:, None] if n > SR else 1
    return x
