"""Build the director's beat map for the Pied Piper film from the approved soundtrack.

    python3 tools/beatmap.py

Reads audio/FOLLOW_THE_PIPER_V2.wav + data/FOLLOW_THE_PIPER_V2_SYNC.json, verifies the event times against the
waveform, and writes data/beatmap.json (events, sections, bars, per-frame band envelopes at 60 fps).
"""
import json, os
import numpy as np, soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 60
x, sr = sf.read(os.path.join(HERE, "audio/FOLLOW_THE_PIPER_V2.wav"))
J = json.load(open(os.path.join(HERE, "data/FOLLOW_THE_PIPER_V2_SYNC.json")))
m = x.mean(1)
dur = len(m) / sr
nf = int(np.ceil(dur * FPS))


def band(lo, hi):
    sos = signal.butter(4, [lo, hi] if lo else hi, "band" if lo else "low", fs=sr, output="sos")
    y = signal.sosfiltfilt(sos, m)
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(nf)])
    e = 20 * np.log10(e)
    e = np.clip((e - (np.percentile(e, 99.5) - 30)) / 30, 0, 1)
    return e


env = {"low": band(None, 150), "mid": band(150, 2000), "high": band(4000, 16000), "flute": band(500, 1800)}
full = band(20, 20000)
env["full"] = full
# onset envelope (spectral flux, per frame)
f, t, Z = signal.stft(m, sr, nperseg=2048, noverlap=2048 - sr // FPS)
S = np.abs(Z)
flux = np.maximum(0, np.diff(np.log1p(S * 50), axis=1)).sum(0)
flux = np.concatenate([[0], flux])[:nf]
flux = flux / np.percentile(flux, 99.5)
env["onset"] = np.clip(flux, 0, 1)


def verify(times, lo, hi, name):
    """median offset between event times and nearest band-limited onset peak"""
    sos = signal.butter(4, [lo, hi], "band", fs=sr, output="sos")
    y = np.abs(signal.sosfiltfilt(sos, m))
    hop = 48
    e = np.array([y[i:i + hop].max() for i in range(0, len(y) - hop, hop)])
    d = np.maximum(0, np.diff(e, prepend=e[0]))
    offs = []
    for tt in times:
        i = int(tt * sr / hop)
        w = d[max(0, i - 10):i + 30]
        if len(w):
            offs.append((np.argmax(w) - min(i, 10)) * hop / sr)
    offs = np.array(offs)
    print(f"  {name:12s} n={len(times):4d}  onset offset median {np.median(offs) * 1000:+5.1f} ms, "
          f"90% within {np.percentile(np.abs(offs), 90) * 1000:4.1f} ms")
    return float(np.median(offs))


E = J["events"]
print("verifying event times against the waveform:")
verify(E["kick"], 40, 120, "kick")
verify(E["clap"], 1000, 4000, "clap")
verify(E["tom"], 80, 400, "tom")
fl = [n for n in J["flute_notes"] if n["track"] == "flute"]
verify([n["time"] for n in fl], 400, 1500, "flute notes")

out = dict(
    source="audio/FOLLOW_THE_PIPER_V2.wav (approved V2, sha1 55ee5ee...)",
    bpm=J["bpm"], beat=J["beat_seconds"], bar=J["bar_seconds"], s16=J["sixteenth_seconds"], fps=FPS,
    duration=dur, frames=nf, bars=J["bars"],
    sections=J["sections"], accents=J["accents"], events=E,
    flute=[dict(t=n["time"], d=n["dur"], m=n["midi"]) for n in fl],
    flute_lo=[dict(t=n["time"], d=n["dur"], m=n["midi"]) for n in J["flute_notes"] if n["track"] == "flute_lo"],
    gaps=[a["time"] for a in J["accents"] if a["type"] == "gap"],
    env={k: [round(float(v), 3) for v in a] for k, a in env.items()},
)
json.dump(out, open(os.path.join(HERE, "data/beatmap.json"), "w"))
print(f"frames {nf}  duration {dur:.4f}s  flute notes {len(fl)}  gaps {out['gaps']}")
