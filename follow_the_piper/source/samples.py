"""
Sample library access (VCSL, CC0: https://github.com/sgossner/VCSL).

Every sample is loaded as mono or stereo float64 at 48 kHz, trimmed to its onset,
and, for pitched instruments, measured: true f0 (the VCSL recorder / strumstick /
psaltery names are written an octave below sounding pitch) and sustain RMS.
Results are cached in CACHE_DIR so renders are fast.
"""
import os, re, glob, pickle
import numpy as np
import soundfile as sf
from scipy import signal
from dsp import SR

VCSL = os.environ.get("VCSL_DIR", "/tmp/claude-0/-home-user-123forwhy/8945497b-2645-554e-ac44-9714760e77b0/scratchpad/vcsl")
CACHE_DIR = os.environ.get("PIPER_CACHE", os.path.join(os.path.dirname(VCSL), "piper_cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

_mem = {}


def load(path, mono=True):
    key = (path, mono)
    if key in _mem:
        return _mem[key]
    x, sr = sf.read(path, always_2d=True)
    x = x.astype(np.float64)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = signal.resample_poly(x, SR // g, sr // g, axis=0)
    if mono:
        x = x.mean(axis=1)
    _mem[key] = x
    return x


def onset_trim(x, thr=0.02, pre=0.002):
    a = np.abs(x if x.ndim == 1 else x.max(axis=1))
    i = int(np.argmax(a > thr * a.max()))
    i = max(0, i - int(pre * SR))
    return x[i:]


def measure_f0(x, fmin, fmax, t0=0.15, t1=0.9):
    import librosa
    seg = x[int(t0 * SR):int(t1 * SR)]
    if len(seg) < 4096:
        seg = x[int(0.03 * SR):]
    f0 = librosa.yin(seg.astype(float), fmin=fmin, fmax=fmax, sr=SR, frame_length=4096)
    return float(np.median(f0))


NOTE_RE = re.compile(r"_([A-G]#?)(\d)_")
PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def name_midi(fname):
    m = NOTE_RE.search(os.path.basename(fname))
    if not m:
        return None
    return 12 * (int(m.group(2)) + 1) + PC[m.group(1)]


class Pitched:
    """a multisampled pitched instrument; zones keyed by articulation"""

    def __init__(self, name, globs, fmin, fmax, octave_fix=12, trim_thr=0.02):
        self.name = name
        cp = os.path.join(CACHE_DIR, f"{name}.pkl")
        if os.path.exists(cp):
            with open(cp, "rb") as f:
                self.zones = pickle.load(f)
            return
        self.zones = {}
        for art, pat in globs.items():
            z = []
            for p in sorted(glob.glob(os.path.join(VCSL, pat), recursive=True)):
                m0 = name_midi(p)
                if m0 is None:
                    continue
                x = onset_trim(load(p), trim_thr)
                f0 = measure_f0(x, fmin, fmax)
                m_true = 69 + 12 * np.log2(f0 / 440)
                nominal = m0 + octave_fix
                if abs(m_true - nominal) > 0.8:      # measurement failed (octave error): trust the name
                    f0 = 440 * 2 ** ((nominal - 69) / 12)
                    m_true = nominal
                sus = x[int(0.15 * SR):int(0.9 * SR)]
                rms = np.sqrt(np.mean(sus ** 2)) if len(sus) > 1000 else np.sqrt(np.mean(x ** 2))
                peak = np.abs(x[:int(0.25 * SR)]).max()
                z.append(dict(path=p, midi=m_true, f0=f0, rms=rms, peak=peak, len=len(x) / SR))
            self.zones[art] = sorted(z, key=lambda d: d["midi"])
        with open(cp, "wb") as f:
            pickle.dump(self.zones, f)

    def pick(self, art, midi, prefer_down=False):
        z = self.zones[art]
        d = [abs(q["midi"] - midi) + (0.3 if (prefer_down and q["midi"] < midi) else 0) for q in z]
        return z[int(np.argmin(d))]

    def audio(self, zone):
        return onset_trim(load(zone["path"]), 0.02)


# --------------------------------------------------------------------------- unpitched kits
def kit(pattern, mono=False, trim=0.02):
    paths = sorted(glob.glob(os.path.join(VCSL, pattern)))
    out = []
    for p in paths:
        x = load(p, mono=mono)
        x = onset_trim(x, trim, pre=0.001)
        out.append(x)
    return out


_inst = {}


def inst(name):
    if name in _inst:
        return _inst[name]
    A = "Aerophones/Edge-blown Aerophones/"
    C = "Chordophones/"
    if name == "alto":
        o = Pitched("alto", {"sus": A + "Baroque Alto Recorder/**/AltRecorder_Sus_*.wav",
                             "vib": A + "Baroque Alto Recorder/**/AltRecorder_SusVib_*.wav",
                             "stac": A + "Baroque Alto Recorder/**/AltRecorder_Stac_*.wav"}, 250, 2000)
    elif name == "sop":
        o = Pitched("sop", {"sus": A + "Baroque Soprano Recorder/**/SopRecorder_Sus_*.wav",
                            "stac": A + "Baroque Soprano Recorder/**/SopRecorder_Stac_*.wav"}, 400, 2600)
    elif name == "tenor":
        o = Pitched("tenor", {"sus": A + "Baroque Tenor Recorder/**/TenRecorder_Sus_*.wav",
                              "vib": A + "Baroque Tenor Recorder/**/TenRecorder_SusVib_*.wav",
                              "stac": A + "Baroque Tenor Recorder/**/TenRecorder_Stac_*.wav"}, 200, 1400)
    elif name == "psaltery":
        o = Pitched("psaltery", {"bow": C + "Zithers/Psaltery, Bowed and Plucked/LongBow/*.wav",
                                 "spic": C + "Zithers/Psaltery, Bowed and Plucked/Spiccato/*.wav",
                                 "pluck": C + "Zithers/Psaltery, Bowed and Plucked/Pluck/*.wav"}, 180, 1600)
    elif name == "strum":
        o = Pitched("strum", {"v3": C + "Composite Chordophones/Strumstick/Finger/*_vl3_*.wav",
                              "v2": C + "Composite Chordophones/Strumstick/Finger/*_vl2_*.wav"}, 100, 1000)
    else:
        raise KeyError(name)
    _inst[name] = o
    return o
