"""Music timing for the edit: smoothed beat grid, downbeats, audio envelopes, all in EDIT time (t=0 = first frame)."""
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FPS = 60
SONG_IN = 0.50                  # song time at edit t=0 (first sound of the piano glissando)
SONG_CUT = 67.976 + SONG_IN     # last downbeat used (song 68.476)
FADE = 1.22                     # musical fade after the last downbeat
DURATION = round(SONG_CUT - SONG_IN + FADE, 3)   # 69.198 s
NFRAMES = int(round(DURATION * FPS))

_a = json.load(open(ROOT / 'build' / 'analysis.json'))
_raw = np.array(_a['beats'])
# local linear regression over 9 beats removes 23 ms quantisation jitter, keeps real tempo drift
_idx = np.arange(len(_raw))
BEATS = np.empty_like(_raw)
for i in range(len(_raw)):
    lo, hi = max(0, i - 4), min(len(_raw), i + 5)
    k = np.polyfit(_idx[lo:hi], _raw[lo:hi], 1)
    BEATS[i] = k[0] * i + k[1]
BEATS = BEATS - SONG_IN                      # edit time
PHASE = int(_a['downbeat_phase'])           # BEATS[PHASE::4] are downbeats
PERIOD = float(np.median(np.diff(BEATS)))
DOWNBEATS = BEATS[PHASE::4]


def beat_at(t):
    """continuous beat index at edit time t (0 at BEATS[0]); downbeats are integers = PHASE mod 4"""
    if t <= BEATS[0]:
        return (t - BEATS[0]) / PERIOD
    if t >= BEATS[-1]:
        return len(BEATS) - 1 + (t - BEATS[-1]) / PERIOD
    i = int(np.searchsorted(BEATS, t) - 1)
    return i + (t - BEATS[i]) / (BEATS[i + 1] - BEATS[i])


def time_of_beat(b):
    if b <= 0:
        return BEATS[0] + b * PERIOD
    if b >= len(BEATS) - 1:
        return BEATS[-1] + (b - len(BEATS) + 1) * PERIOD
    i = int(math.floor(b))
    return BEATS[i] + (b - i) * (BEATS[i + 1] - BEATS[i])


def bar_at(t):
    """(bar index, beat-in-bar float 0..4) with bar 0 starting at the first downbeat"""
    b = beat_at(t) - PHASE
    return int(math.floor(b / 4)), b % 4


def db(n):
    """edit time of downbeat n"""
    return float(DOWNBEATS[n]) if n < len(DOWNBEATS) else float(DOWNBEATS[-1] + (n - len(DOWNBEATS) + 1) * 4 * PERIOD)


# ------------------------------------------------------------------ audio envelopes (per frame)
_env = None


def envelopes():
    """returns dict of per-frame arrays: rms, low (kick/bass), snare, vocal (0..1)"""
    global _env
    if _env is not None:
        return _env
    cache = ROOT / 'build' / 'envelopes.npz'
    if cache.exists():
        z = np.load(cache)
        _env = {k: z[k] for k in z.files}
        return _env
    import librosa
    from scipy.signal import butter, sosfiltfilt
    y, sr = librosa.load(ROOT / 'audio' / 'source.mp3', sr=22050, offset=SONG_IN, duration=DURATION + 0.5)
    H, P = librosa.effects.hpss(y)
    def env(x, smooth_ms):
        e = np.abs(x)
        k = max(1, int(sr * smooth_ms / 1000))
        e = np.convolve(e, np.ones(k) / k, 'same')
        fr = np.array([e[int(i / FPS * sr): int((i + 1) / FPS * sr)].mean() if int(i / FPS * sr) < len(e) else 0
                       for i in range(NFRAMES)])
        return fr / (np.percentile(fr, 98) + 1e-9)
    bp = lambda lo, hi, x: sosfiltfilt(butter(4, [lo, hi], 'bandpass', fs=sr, output='sos'), x)
    _env = dict(rms=np.clip(env(y, 60), 0, 1.2), low=np.clip(env(bp(40, 160, P), 40), 0, 1.2),
                snare=np.clip(env(bp(1800, 5000, P), 30), 0, 1.2), vocal=np.clip(env(bp(350, 2800, H), 45), 0, 1.2))
    np.savez(cache, **_env)
    return _env


def env_at(name, t):
    e = envelopes()[name]
    i = int(t * FPS)
    return float(e[min(max(i, 0), len(e) - 1)])
