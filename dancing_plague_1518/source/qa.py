"""
QA against the reference soundtrack.

    python3 qa.py MASTER.wav REFERENCE_MUSIC.wav

- spectral balance (octave bands) of the loud sections, master vs reference
- loudness per 8 bars (no long quiet holes)
- hook identity: chroma correlation of the hook+answer (reference bars 19-22 vs extended bars 19-22,
  and vs every other 4-bar window, to show the hook is the best match)
- mono compatibility and a phone-speaker simulation (HPF 350 Hz + 1 kHz resonance)
"""
import sys
import numpy as np
import librosa
import soundfile as sf
import pyloudnorm as pyln
import scipy.signal as ss

M, R = sys.argv[1], sys.argv[2]
REF_BAR = 4 * 0.466694; REF_OFF = -0.006
BAR = 4 * 60 / 128.5

x, sr = sf.read(M)
r, rsr = sf.read(R)
meter = pyln.Meter(sr)
print(f"master: {len(x) / sr:.1f} s, LUFS {meter.integrated_loudness(x):.2f}, peak {20 * np.log10(np.abs(x).max()):.2f} dBFS")

bands = [(30, 60), (60, 120), (120, 250), (250, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000), (8000, 14000)]
def bal(sig, fs):
    f, P = ss.welch(sig, fs, nperseg=8192); tot = P.sum()
    return np.array([10 * np.log10(P[(f >= a) & (f < b)].sum() / tot) for a, b in bands])
bm = bal(x[int(28 * BAR * sr):int(36 * BAR * sr)].mean(1), sr)
br = bal(r[46 * rsr:62 * rsr].mean(1), rsr)
print("band        " + " ".join(f"{a}-{b}".rjust(9) for a, b in bands))
print("master drop " + " ".join(f"{v:9.1f}" for v in bm))
print("ref drop    " + " ".join(f"{v:9.1f}" for v in br))
print("diff        " + " ".join(f"{v:9.1f}" for v in bm - br))

print("\nloudness per 4 bars (LUFS short-term-ish):")
row = []
for b in range(0, 88, 4):
    seg = x[int(b * BAR * sr):int((b + 4) * BAR * sr)]
    row.append(f"{b + 1}:{meter.integrated_loudness(seg):.1f}")
print("  " + "  ".join(row))

# hook identity
def chroma_bars(y, fs, t0, nb, bar):
    y = librosa.resample(y, orig_sr=fs, target_sr=22050)
    C = librosa.feature.chroma_cqt(y=y[int(t0 * 22050):int((t0 + nb * bar) * 22050)], sr=22050, hop_length=256)
    k = int(nb * 16)
    idx = np.linspace(0, C.shape[1], k + 1).astype(int)
    return np.array([C[:, idx[i]:max(idx[i] + 1, idx[i + 1])].mean(1) for i in range(k)])
ref = chroma_bars(r.mean(1), rsr, REF_OFF + 18 * REF_BAR, 4, REF_BAR)
def corr(a, b):
    a = a - a.mean(1, keepdims=True); b = b - b.mean(1, keepdims=True)
    return float(np.mean(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9)))
xm = x.mean(1)
scores = []
for b0 in range(0, 84, 2):
    scores.append((corr(ref, chroma_bars(xm, sr, b0 * BAR, 4, BAR)), b0 + 1))
scores.sort(reverse=True)
print("\nhook+answer chroma match vs reference bars 19-22 (best windows):", [(round(s, 3), f"bar {b}") for s, b in scores[:6]])
print("worst windows:", [(round(s, 3), f"bar {b}") for s, b in scores[-3:]])
# reference against itself (repeat at bars 37-38) for scale
ref2 = chroma_bars(r.mean(1), rsr, REF_OFF + 36 * REF_BAR, 4, REF_BAR)
print("reference self-similarity (bars 19-22 vs its own 37-40):", round(corr(ref, ref2), 3))

# mono & phone
mono = xm
side = (x[:, 0] - x[:, 1]) / 2
print(f"\nside/mid RMS {np.sqrt((side ** 2).mean() / (mono ** 2).mean()):.3f}; "
      f"mono loss {meter.integrated_loudness(np.stack([mono, mono], 1)) - meter.integrated_loudness(x):.2f} dB")
sos = ss.butter(4, 350, "high", fs=sr, output="sos")
ph = ss.sosfilt(sos, mono)
print(f"phone sim: LUFS {pyln.Meter(sr).integrated_loudness(np.stack([ph, ph], 1)):.1f}; "
      f"lead band (600-3k) share in the hook {10 * np.log10(np.mean(ss.sosfilt(ss.butter(4, [600, 3000], 'band', fs=sr, output='sos'), ph[int(18 * BAR * sr):int(22 * BAR * sr)]) ** 2) / np.mean(ph[int(18 * BAR * sr):int(22 * BAR * sr)] ** 2)):.1f} dB")
