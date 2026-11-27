"""
QA for FOLLOW THE PIPER renders.

    python3 qa.py <render_dir> [reference.wav]

Prints: loudness / true peak / clipping, short-term loudness per section, per-stem loudness per
section (balance), octave-band tonal balance vs. a reference, mono fold-down loss, phone-speaker
proxy loudness, loop seam continuity, and a flute pitch check against the score.
"""
import sys, os, json
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal

d = sys.argv[1]
ref = sys.argv[2] if len(sys.argv) > 2 else None
x, sr = sf.read(os.path.join(d, "FOLLOW_THE_PIPER_FINAL.wav"))
info = sf.info(os.path.join(d, "FOLLOW_THE_PIPER_FINAL.wav"))
J = json.load(open(os.path.join(d, "FOLLOW_THE_PIPER_SYNC.json")))
meter = pyln.Meter(sr)


def lu(y):
    try:
        return meter.integrated_loudness(y if y.ndim == 2 else np.stack([y, y], 1))
    except Exception:
        return -99


def tp(y):
    u = signal.resample_poly(y, 4, 1, axis=0)
    return 20 * np.log10(np.abs(u).max())


print(f"file: {info.samplerate} Hz, {info.subtype}, {info.channels} ch, {info.duration:.3f} s")
print(f"integrated {lu(x):.2f} LUFS | true peak {tp(x):.2f} dBTP | sample peak {20*np.log10(np.abs(x).max()):.2f} dBFS"
      f" | samples >= 0.999: {(np.abs(x) >= 0.999).sum()}")

# section loudness (momentary-ish: integrated within section)
print("\nsection loudness:")
for s in J["sections"]:
    a, b = int(s["start"] * sr), int(s["end"] * sr)
    print(f"  {s['name']:15s} {s['start']:6.2f}-{s['end']:6.2f}  {lu(x[a:b]):6.1f} LUFS")

# per-bar short-term loudness curve
bar = J["bar_seconds"]
curve = []
for i in range(J["bars"]):
    a, b = int(i * bar * sr), int((i + 1) * bar * sr)
    y = x[a:b]
    curve.append(10 * np.log10(np.mean(y ** 2) + 1e-12))
print("\nper-bar RMS dB:", " ".join(f"{c:.0f}" for c in curve))

# stems
sd = os.path.join(d, "stems")
if os.path.isdir(sd):
    print("\nstem loudness per section (LUFS, pre-master):")
    stems = sorted(f for f in os.listdir(sd) if f.endswith(".wav"))
    hdr = "  " + " " * 16 + " ".join(f"{s['name'][:9]:>9s}" for s in J["sections"])
    print(hdr)
    for f in stems:
        y, _ = sf.read(os.path.join(sd, f))
        row = []
        for s in J["sections"]:
            a, b = int(s["start"] * sr), int(s["end"] * sr)
            v = lu(y[a:b])
            row.append(f"{v:9.1f}" if v > -70 else "        -")
        print(f"  {f[11:-4]:16s}" + " ".join(row))


def bands(y):
    m = y.mean(1) if y.ndim == 2 else y
    f, P = signal.welch(m, sr, nperseg=8192)
    edges = [20, 40, 80, 160, 315, 630, 1250, 2500, 5000, 10000, 20000]
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (f >= lo) & (f < hi)
        out.append(10 * np.log10(P[sel].sum() + 1e-20))
    out = np.array(out)
    return out - out.max()


print("\noctave bands (dB rel. max)    20   40   80  160  315  630  1k2  2k5   5k  10k")
b = bands(x)
print("  piper (whole)          " + " ".join(f"{v:4.0f}" for v in b))
fd = [s for s in J["sections"] if s["name"] == "final_drop"][0]
bfd = bands(x[int(fd["start"] * sr):int(fd["end"] * sr)])
print("  piper (final drop)     " + " ".join(f"{v:4.0f}" for v in bfd))
if ref:
    r, rsr = sf.read(ref)
    if rsr != sr:
        r = signal.resample_poly(r, sr, rsr, axis=0)
    br = bands(r)
    print("  reference              " + " ".join(f"{v:4.0f}" for v in br))
    print("  difference (piper-ref) " + " ".join(f"{v:4.0f}" for v in b - br))

# mono + phone proxy
mono = x.mean(1)
print(f"\nmono fold-down: {lu(mono) - lu(x):+.2f} LU (stereo->mono)")
phone = signal.sosfilt(signal.butter(4, [350, 9000], "band", fs=sr, output="sos"), mono)
print(f"phone-speaker proxy (350 Hz-9 kHz) loudness: {lu(phone):.1f} LUFS ({lu(phone) - lu(x):+.1f} LU vs full)")
corr = np.corrcoef(x[:, 0], x[:, 1])[0, 1]
print(f"L/R correlation: {corr:.2f}")

# loop seam: compare end and start levels / discontinuity
k = int(0.01 * sr)
seam = np.concatenate([x[-k:], x[:k]])
jump = np.abs(x[0] - x[-1]).max()
print(f"loop seam sample jump: {jump:.5f}; RMS last 50ms {20*np.log10(np.sqrt(np.mean(x[-2400:]**2))+1e-12):.1f} dB,"
      f" first 50ms {20*np.log10(np.sqrt(np.mean(x[:2400]**2))+1e-12):.1f} dB")

# flute pitch check
fl = os.path.join(sd, "PIPER_STEM_lead_flute.wav")
if os.path.exists(fl):
    import librosa
    y, _ = sf.read(fl)
    m = y.mean(1)
    errs = []
    for n in J["flute_notes"]:
        if n["track"] != "flute" or n["dur"] < 0.2:
            continue
        a = int((n["time"] + 0.05) * sr); b = int((n["time"] + n["dur"] * 0.85) * sr)
        seg = m[a:b]
        if len(seg) < 2048:
            continue
        f0 = librosa.yin(seg, fmin=200, fmax=2000, sr=sr, frame_length=2048)
        e = 12 * np.log2(np.median(f0) / (440 * 2 ** ((n["midi"] - 69) / 12)))
        errs.append(e)
    errs = np.array(errs)
    print(f"flute pitch vs score: {len(errs)} notes, median {np.median(errs) * 100:+.0f} c, "
          f"worst {np.abs(errs).max() * 100:.0f} c, >30c: {(np.abs(errs) > 0.3).sum()}")
