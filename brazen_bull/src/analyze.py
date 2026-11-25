"""Technical 'listening' tools: loudness curve, peak hunting, spectral balance,
stereo/mono checks, phone-speaker translation, spectrograms, onset-vs-grid."""
import sys
import json
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 48000
SECS = dict(intro=(0, 3.53), groove=(3.53, 14.12), escal=(14.12, 24.71), predrop=(24.71, 26.47),
            drop1=(26.47, 40.59), breakdown=(40.59, 47.65), drop2=(47.65, 58.24), outro=(58.24, 60))
BANDS = [(20, 60, "sub"), (60, 120, "bass"), (120, 300, "lowmid"), (300, 1000, "mid"), (1000, 3000, "upmid"),
         (3000, 6000, "presence"), (6000, 12000, "brill"), (12000, 20000, "air")]


def band_db(x, lo, hi):
    sos = signal.butter(4, [lo, min(hi, 23000)], btype="band", fs=SR, output="sos")
    y = signal.sosfilt(sos, x)
    return 10 * np.log10(np.mean(y ** 2) + 1e-12)


def report(path, out_png=None):
    x, sr = sf.read(path, always_2d=True)
    assert sr == SR
    x = x.T
    m = pyln.Meter(SR)
    info = sf.info(path)
    print(f"file: {info.samplerate} Hz, {info.channels} ch, {info.subtype}, {info.frames} frames = {info.frames / SR:.6f} s")
    print(f"integrated LUFS {m.integrated_loudness(x.T):.2f}")
    up = signal.resample_poly(x, 4, 1, axis=-1)
    print(f"sample peak {20 * np.log10(np.max(np.abs(x))):.2f} dBFS, true peak {20 * np.log10(np.max(np.abs(up))):.2f} dBTP")
    print(f"clipped samples (>=0.999): {int(np.sum(np.abs(x) >= 0.999))}")
    mono = x.mean(0)
    side = (x[0] - x[1]) / 2
    print(f"L/R correlation {np.corrcoef(x[0], x[1])[0, 1]:.3f}, side/mid ratio {10 * np.log10(np.mean(side ** 2) / np.mean(mono ** 2)):.1f} dB")
    # short-term loudness (3 s) every 0.5 s
    st = []
    for t in np.arange(0, 57.01, 1.0):
        seg = x[:, int(t * SR):int((t + 3) * SR)]
        st.append(m.integrated_loudness(seg.T) if seg.shape[1] > SR * 0.5 else -70)
    print("short-term LUFS (3 s windows @1 s):", " ".join(f"{v:.0f}" for v in st))
    print("section | LUFS | crest dB | " + " ".join(b[2] for b in BANDS))
    for name, (a, b) in SECS.items():
        seg = x[:, int(a * SR):int(b * SR)]
        mm = seg.mean(0)
        l = m.integrated_loudness(seg.T) if seg.shape[1] > SR * 0.4 else -70
        crest = 20 * np.log10(np.max(np.abs(mm)) / (np.sqrt(np.mean(mm ** 2)) + 1e-12))
        tot = 10 * np.log10(np.mean(mm ** 2) + 1e-12)
        bands = [band_db(mm, lo, hi) - tot for lo, hi, _ in BANDS]
        print(f"{name:9s} {l:6.1f} {crest:6.1f}  " + " ".join(f"{v:6.1f}" for v in bands))
    # phone speaker sim: HPF 350 Hz + LPF 12k, compare loudness drop
    sos = signal.butter(4, [350, 12000], btype="band", fs=SR, output="sos")
    ph = signal.sosfilt(sos, x, axis=-1)
    print(f"phone-speaker sim loudness: {m.integrated_loudness(ph.T):.2f} LUFS (full {m.integrated_loudness(x.T):.2f})")
    # mono compatibility
    print(f"mono fold-down loudness: {m.integrated_loudness(np.vstack([mono, mono]).T):.2f}")
    if out_png:
        fig, axs = plt.subplots(3, 1, figsize=(22, 13), gridspec_kw=dict(height_ratios=[3, 1, 1]))
        f, t, S = signal.spectrogram(mono, SR, nperseg=4096, noverlap=3072)
        axs[0].pcolormesh(t, f, 10 * np.log10(S + 1e-12), vmin=-130, vmax=-30, shading="auto", cmap="magma")
        axs[0].set_yscale("symlog", linthresh=200)
        axs[0].set_ylim(30, 20000)
        for nme, (a, b) in SECS.items():
            axs[0].axvline(a, color="cyan", lw=0.8)
            axs[0].text(a + 0.1, 15000, nme, color="cyan")
        env = np.sqrt(signal.lfilter([0.002], [1, -0.998], mono ** 2))
        tt = np.arange(len(mono)) / SR
        axs[1].plot(tt[::48], 20 * np.log10(env[::48] + 1e-9), lw=0.5)
        axs[1].set_ylim(-60, 0)
        axs[1].set_xlim(0, 60)
        axs[2].plot(np.arange(len(st)) + 1.5, st, "o-")
        axs[2].set_xlim(0, 60)
        axs[2].set_ylabel("ST LUFS")
        plt.tight_layout()
        plt.savefig(out_png, dpi=70)


def zoom_png(path, t0, t1, out_png):
    x, _ = sf.read(path, always_2d=True)
    seg = x[int(t0 * SR):int(t1 * SR)].mean(1)
    f, t, S = signal.spectrogram(seg, SR, nperseg=2048, noverlap=1792)
    plt.figure(figsize=(20, 8))
    plt.pcolormesh(t + t0, f, 10 * np.log10(S + 1e-12), vmin=-130, vmax=-30, shading="auto", cmap="magma")
    plt.yscale("symlog", linthresh=200)
    plt.ylim(30, 20000)
    beat = 60 / 136
    for b in np.arange(np.ceil(t0 / beat), t1 / beat):
        plt.axvline(b * beat, color="w", lw=0.4 if b % 4 else 1.2, alpha=0.6)
    plt.tight_layout()
    plt.savefig(out_png, dpi=70)


if __name__ == "__main__":
    report(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
