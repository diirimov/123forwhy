#!/usr/bin/env python3
"""Visual QA: spectrogram + short-term loudness curve with section markers -> output/analysis.png"""
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine.score import SECTIONS, beat_to_sec, BAR  # noqa: E402

x, sr = sf.read(HERE / 'output' / 'soundtrack_final.wav')
mono = x.mean(1)
f, t, Sx = spectrogram(mono, sr, nperseg=4096, noverlap=3072)
meter = pyln.Meter(sr, block_size=0.4)
hop = int(0.1 * sr); win = int(3.0 * sr)
st_t, st_l = [], []
for i in range(0, len(mono) - win, hop):
    try:
        st_l.append(meter.integrated_loudness(x[i:i + win])); st_t.append((i + win / 2) / sr)
    except Exception:
        pass
fig, ax = plt.subplots(2, 1, figsize=(14, 7), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
ax[0].pcolormesh(t, f, 10 * np.log10(Sx + 1e-14), shading='auto', cmap='magma', vmin=-130, vmax=-40)
ax[0].set_yscale('symlog', linthresh=200); ax[0].set_ylim(30, 20000); ax[0].set_ylabel('Hz')
ax[1].plot(st_t, st_l, color='k'); ax[1].set_ylabel('LUFS (3 s)'); ax[1].set_xlabel('s'); ax[1].grid(alpha=.3)
for b0, b1, name, _ in SECTIONS:
    s = beat_to_sec(b0 * BAR)
    for a in ax:
        a.axvline(s, color='c', lw=1)
    ax[0].text(s + .2, 15000, name, color='w', fontsize=8)
plt.tight_layout(); plt.savefig(HERE / 'output' / 'analysis.png', dpi=90)
print('wrote output/analysis.png')
