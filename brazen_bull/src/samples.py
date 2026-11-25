"""Sample-based sound design for V2: loads the supplied ElevenLabs effects, tunes them to
E Phrygian with Rubber Band (R3 engine), slices/chops/reverses/layers them, and keeps clean
isolated renders of every processed one-shot for animation sync."""
import os
import subprocess
import tempfile
import numpy as np
import soundfile as sf
from scipy import signal
from dsp import SR, BEAT, STEP, BAR, lp, hp, bp, eq, softclip, to_st, pan, fade, mtof, convolve_st, make_ir
from vocals import bronze_resonate

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(HERE, "..", "samples_original")
FILES = dict(
    wail="A_haunting_powerful_2",       # haunting ancient ritual vocal wail (D#5 -> C#5 fall)
    shriek="A_sudden_supernatura_1",    # supernatural horror shriek (G6)
    roar="A_terrifying_superna_1",      # supernatural bull roar (G#3 body, burst @1.67 s)
    door="A_massive_heavy_bron_3",      # heavy bronze door slam
    heart="Deep_cinematic_human_3",     # cinematic heartbeat (lub-dub, ~1 s period)
    fire="A_sudden_powerful_ci_2",      # fire ignition + flame whoosh
    scan="A_fast_cinematic_x-r_1",      # anatomical x-ray scanning transition
    impact="A_massive_dark_cinem_3",    # dark cinematic bronze impact
    shout=None,                         # male tribal shout (not supplied yet)
)
ISOLATED = {}      # name -> stereo array (clean processed one-shots for the animators)
_cache = {}
HALL = make_ir(3.0, 2.4, 1.3, 3.5, predelay_ms=20, seed=21, bright=6500)


def load(key):
    if key not in _cache:
        x, sr = sf.read(os.path.join(SRC_DIR, FILES[key] + ".wav"), always_2d=True)
        assert sr == SR
        x = hp(x.T.astype(float), 18.0, 2)
        _cache[key] = x / (np.max(np.abs(x)) + 1e-9)
    return _cache[key].copy()


def seg(x, t0, t1, fi=0.003, fo=0.03):
    y = to_st(x)[:, int(t0 * SR):int(t1 * SR)]
    return fade(y, fi, fo)


def rb(x, semis=0.0, stretch=1.0, formant=False, crisp=None):
    """Rubber Band R3 (--fine) pitch shift / time stretch. stretch = output/input length."""
    x = to_st(x)
    if abs(semis) < 1e-6 and abs(stretch - 1) < 1e-6:
        return x.copy()
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        sf.write(a, x.T, SR, subtype="FLOAT")
        cmd = ["rubberband", "-q", "--fine", "-t", f"{stretch:.6f}", "-p", f"{semis:.6f}"]
        if formant:
            cmd.append("-F")
        if crisp is not None:
            cmd += ["-c", str(crisp)]
        subprocess.run(cmd + [a, b], check=True, capture_output=True)
        y, _ = sf.read(b, always_2d=True)
    return y.T


def hf_onset(x, lo=0.0, hi=None, f=2500.0):
    """time of steepest high-frequency rise (transient) in [lo, hi] seconds"""
    m = to_st(x).mean(0)
    h = signal.sosfilt(signal.butter(4, f, "high", fs=SR, output="sos"), m)
    env = np.sqrt(signal.lfilter([0.004], [1, -0.996], h ** 2))
    d = np.diff(env, prepend=0)
    a = int(lo * SR)
    b = len(d) if hi is None else int(hi * SR)
    return (a + int(np.argmax(d[a:b]))) / SR


def iso(name, x):
    ISOLATED[name] = to_st(x).copy()
    return x


def norm(x, pk=1.0):
    return x * (pk / (np.max(np.abs(x)) + 1e-9))


# =============================================================================
# BULL ROAR - the signature motif (horror vocal x bass texture x transition)
# =============================================================================
def roar_signature():
    """returns (stereo, burst_time): roar tuned G#3 -> E3, sub-octave E2 body, bronze-body resonance,
    parallel drive. burst_time = the explosive transient used to lock it to the grid."""
    if "roar_sig" in _cache:
        return _cache["roar_sig"]
    x = seg(load("roar"), 0.0, 3.7, 0.002, 0.25)
    a = rb(x, -4.0)                                   # E3 body
    b = rb(x, -16.0)                                  # E2 sub-body
    b = softclip(lp(b, 320, 4) * 2.2, 1.0)
    n = min(a.shape[1], b.shape[1])
    a, b = a[:, :n], b[:, :n]
    brz = bronze_resonate(a.mean(0), base_hz=82.4, fb=0.84, mix=1.0)   # through the bronze body
    drv = bp(softclip(a * 4.0, 1.0), 180, 4500)       # parallel distortion for bite
    y = a + 0.75 * b + 0.35 * to_st(brz) + 0.35 * drv
    y = eq(y, "peak", 420, 1.0, -2.5)                 # de-mud
    y = eq(y, "peak", 2300, 1.1, 2.5)                 # snarl
    y = hp(y, 30)
    y = norm(y)
    burst = hf_onset(y, 1.58, 1.85)
    _cache["roar_sig"] = (y, burst)
    iso("roar_signature_E", y)
    return y, burst


def roar_burst(len_s=1.1):
    y, bt = roar_signature()
    pre = 0.06
    out = seg(y, bt - pre, bt + len_s, 0.004, 0.35)
    return iso("roar_burst", out), pre


def roar_bass_texture(n_bars=1, steps=(0, 2, 3, 6, 7, 10, 11, 14, 15), semis=-16.0):
    """the roar's harmonic body as a gated low growl locked to the bass rhythm (16ths)"""
    key = ("rbt", n_bars, tuple(steps))
    if key in _cache:
        return _cache[key]
    x = seg(load("roar"), 0.30, 1.62, 0.01, 0.02)
    L = n_bars * BAR
    y = rb(x, semis, stretch=L / (1.62 - 0.30))
    y = softclip(lp(y, 650, 4) * 3.0, 1.0)
    y = hp(eq(y, "peak", 160, 1.0, 3.0), 35)
    n = y.shape[1]
    g = np.zeros(n)
    for b in range(n_bars):
        for s in steps:
            i0 = int((b * BAR + s * STEP) * SR)
            ln = int(STEP * 0.85 * SR)
            if i0 >= n:
                continue
            e = np.exp(-np.arange(ln) / (ln * 0.45))
            e[: int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
            g[i0:i0 + ln] = np.maximum(g[i0:i0 + ln], e[: max(0, min(ln, n - i0))])
    out = norm(y * g)
    _cache[key] = out
    iso(f"roar_bass_texture_{n_bars}bar", out)
    return out


def roar_reverse(length):
    y, bt = roar_signature()
    src = seg(y, 0.25, bt + 0.25, 0.01, 0.05)
    src = np.pad(src, ((0, 0), (0, int(1.5 * SR))))
    wet = convolve_st(src, HALL)
    z = (0.6 * src + wet)[:, ::-1]
    n = int(length * SR)
    z = z[:, -n:] if z.shape[1] >= n else np.pad(z, ((0, 0), (n - z.shape[1], 0)))
    z = z * np.linspace(0, 1, n) ** 1.6
    return iso("roar_reverse_rise", norm(z))


def roar_low_tail(len_s=1.7):
    y, bt = roar_signature()
    t = seg(y, bt, bt + len_s + 0.5, 0.01, 0.6)
    t = rb(t, -5.0)
    t = softclip(lp(t, 500, 4) * 2.0, 1.0)
    return iso("roar_low_tail_ending", norm(t))


# =============================================================================
# RITUAL WAIL - call-and-response voice, choir and chops
# =============================================================================
WAIL_REF_HZ = 620.0      # steady pitch of the wail's sustained segment (0.45-0.95 s)


def wail_answer(semis=3.0, stretch=0.62):
    """falling wail phrase: tuned so the fall resolves onto E5 (Phrygian sigh). ~1 s long."""
    k = ("wa", semis, stretch)
    if k not in _cache:
        x = seg(load("wail"), 0.26, 1.95, 0.004, 0.18)
        y = rb(x, semis, stretch=stretch, formant=True)
        y = hp(y, 220)
        y = eq(y, "peak", 3000, 1.0, 2.0)
        _cache[k] = iso(f"wail_answer_{semis:+.0f}st", norm(y))
    return _cache[k]


def wail_full(semis=3.0):
    k = ("wf", semis)
    if k not in _cache:
        x = seg(load("wail"), 0.26, 5.6, 0.004, 0.6)
        y = rb(x, semis, formant=True)
        _cache[k] = iso("wail_full_intro", norm(lp(hp(y, 250), 3800)))
    return _cache[k]


def wail_dark(semis=-9.0, stretch=2.0):
    """breakdown transformation: slowed, lowered, no formant correction -> giant, ancient"""
    k = ("wd", semis, stretch)
    if k not in _cache:
        x = seg(load("wail"), 0.26, 3.9, 0.01, 0.5)
        y = rb(x, semis, stretch=stretch, formant=False)
        y = eq(hp(y, 120), "peak", 900, 1.0, 2.5)
        _cache[k] = iso("wail_dark_breakdown", norm(y))
    return _cache[k]


def wail_chop(midi, len_steps=1.0):
    k = ("wc", midi, len_steps)
    if k not in _cache:
        x = seg(load("wail"), 0.47, 0.47 + STEP * len_steps * 1.15 + 0.06, 0.002, 0.01)
        semis = 12 * np.log2(mtof(midi) / WAIL_REF_HZ)
        y = rb(x, semis, formant=True, crisp=6)
        n = int(STEP * len_steps * 0.92 * SR)
        y = y[:, :n]
        env = np.ones(n)
        r = int(0.012 * SR)
        env[-r:] = np.linspace(1, 0, r)
        env[: int(0.0015 * SR)] = np.linspace(0, 1, int(0.0015 * SR))
        y = softclip(hp(y * env, 300) * 1.6, 1.0)
        _cache[k] = norm(y)
    return _cache[k]


def wail_choir(notes, len_s=0.75):
    """stacked, formant-preserved wail voices tuned to a chord -> ritual choir accent"""
    k = ("wch", tuple(notes), len_s)
    if k not in _cache:
        x = seg(load("wail"), 0.30, 0.30 + len_s * 1.1, 0.01, 0.2)
        r = np.random.default_rng(len(notes) * 7 + int(sum(notes)))
        acc = None
        for i, m in enumerate(notes):
            for v in range(2):
                semis = 12 * np.log2(mtof(m) / WAIL_REF_HZ) + r.normal(0, 0.08)
                y = rb(x, semis, stretch=r.uniform(0.97, 1.03), formant=True).mean(0)
                y = np.concatenate([np.zeros(int(abs(r.normal(0, 0.008)) * SR)), y])
                st = pan(y, r.uniform(-0.85, 0.85))
                if acc is None:
                    acc = st
                else:
                    n = max(acc.shape[1], st.shape[1])
                    acc = np.pad(acc, ((0, 0), (0, n - acc.shape[1]))) + np.pad(st, ((0, 0), (0, n - st.shape[1])))
        acc = fade(acc[:, : int(len_s * SR)], 0.006, 0.25)
        _cache[k] = norm(hp(acc, 150))
        iso("wail_choir_" + "_".join(str(n) for n in notes), _cache[k])
    return _cache[k]


# =============================================================================
# SHRIEK
# =============================================================================
def shriek(kind="distant"):
    k = ("sh", kind)
    if k in _cache:
        return _cache[k]
    x = load("shriek")
    if kind == "distant":        # transitions / breaks
        y = seg(x, 0.03, 1.4, 0.002, 0.4)
        y = bp(y, 450, 7000)
    elif kind == "low":          # pitched-down ghost (breakdown)
        y = rb(seg(x, 0.03, 1.6, 0.002, 0.5), -7.0, stretch=1.2)
        y = bp(y, 300, 5000)
    elif kind == "stutter":      # 16th chop source
        y = seg(x, 0.06, 0.06 + STEP * 0.8, 0.002, 0.012)
        y = softclip(y * 2.0, 1.0)
    elif kind == "climax":
        y = seg(x, 0.03, 1.2, 0.002, 0.35)
        y = y + 0.6 * rb(y, -12.0)[:, : y.shape[1]]
        y = softclip(y * 1.5, 1.0)
    y = norm(y)
    _cache[k] = iso(f"shriek_{kind}", y)
    return y


def shriek_reverse(length):
    x = seg(load("shriek"), 0.03, 1.5, 0.002, 0.3)
    x = np.pad(x, ((0, 0), (0, int(1.6 * SR))))
    z = (0.5 * x + convolve_st(x, HALL))[:, ::-1]
    n = int(length * SR)
    z = z[:, -n:]
    z = z * np.linspace(0, 1, n) ** 2
    return iso("shriek_reverse_rise", norm(bp(z, 400, 8000)))


# =============================================================================
# STRUCTURAL SFX (onset-aligned one-shots)
# =============================================================================
def door():
    if "door" not in _cache:
        y = seg(load("door"), 0.0, 2.3, 0.0, 0.5)
        _cache["door"] = (iso("bronze_door_slam", norm(y)), hf_onset(y, 0, 0.2, 800))
    return _cache["door"]


def impact_sample(semis=0.0, len_s=4.0):
    k = ("imp", semis, len_s)
    if k not in _cache:
        y = seg(load("impact"), 0.0, len_s, 0.0, 1.0)
        if semis:
            y = rb(y, semis)
        _cache[k] = (iso(f"bronze_impact{'' if not semis else f'_{semis:+.0f}st'}", norm(y)), hf_onset(y, 0, 0.2, 800))
    return _cache[k]


def fire():
    if "fire" not in _cache:
        y = seg(load("fire"), 0.08, 2.6, 0.01, 0.6)
        _cache["fire"] = (iso("fire_ignition", norm(y)), hf_onset(y, 0, 0.5, 600))
    return _cache["fire"]


def scan():
    if "scan" not in _cache:
        y = seg(load("scan"), 0.0, 1.5, 0.0, 0.3)
        _cache["scan"] = (iso("anatomical_scan", norm(y)), hf_onset(y, 0, 0.3, 800))
    return _cache["scan"]


HEART_ONSETS = [0.0, 0.99, 2.0, 3.0, 4.0, 4.99, 5.97, 6.98]


def heart_unit(i):
    k = ("hu", i % len(HEART_ONSETS))
    if k not in _cache:
        t0 = HEART_ONSETS[i % len(HEART_ONSETS)]
        y = seg(load("heart"), max(t0 - 0.005, 0), t0 + 0.62, 0.002, 0.12)
        y = eq(y, "peak", 70, 1.0, 2.0)
        _cache[k] = (norm(y), 0.005 if t0 > 0 else 0.0)
        if i == 0:
            iso("heartbeat_unit", _cache[k][0])
    return _cache[k]


def export_isolated(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    names = []
    for name, x in ISOLATED.items():
        y = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-1.0 / 20)
        sf.write(os.path.join(out_dir, f"{name}.wav"), y.T, SR, subtype="PCM_24")
        names.append(name)
    return sorted(names)


# =============================================================================
# V3: ETHNIC MALE VOCAL (expressive haunting phrase) - natural slices, whole-slice transposition only
# =============================================================================
FILES["ethnic"] = "An_expressive_haunt_2"
# slice name: (start s, end s, reference MIDI pitch at the slice's start, description)
VOX_SLICES = {
    "att":  (0.30, 0.95, 54.5, "vowel attack - short rhythmic syllable"),
    "syl":  (1.96, 2.75, 55.9, "second syllable with its own natural articulation"),
    "rise": (1.00, 2.05, 54.9, "natural G -> G# rise (Hijaz colour)"),
    "fall": (2.30, 3.75, 55.6, "falling sigh - expressive tail"),
}


def vox_slice(kind, midi, len_s=None, cents=0.0):
    """Cut a natural slice, transpose it as a whole (formant-preserving) so its start lands on `midi`
    (+ a few cents of human variance). No per-note pitch correction, no distortion."""
    k = ("vx", kind, midi, None if len_s is None else round(len_s, 4), round(cents, 1))
    if k in _cache:
        return _cache[k]
    t0, t1, ref, _ = VOX_SLICES[kind]
    if len_s is not None:
        t1 = min(t1, t0 + len_s + 0.06)
    x = seg(load("ethnic"), t0, t1, 0.004, 0.0)
    semis = (midi - ref) + cents / 100.0
    y = rb(x, semis, formant=True) if abs(semis) > 0.02 else x
    n = y.shape[1] if len_s is None else min(y.shape[1], int((len_s + 0.02) * SR))
    y = y[:, :n]
    fo = min(int(0.045 * SR), n // 3)
    y[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
    y = hp(y, 85, 2)
    _cache[k] = norm(y)
    name = f"ethnic_vocal_{kind}_{midi}"
    if name not in ISOLATED:
        iso(name, _cache[k])
    return _cache[k]
