"""Analyse the approved soundtrack: tempo, beat grid, accents, per-bar energy, breaks -> edit_map.json"""
import json, numpy as np
from scipy.io import wavfile
from scipy import signal
sr, x = wavfile.read('../../music/MEDIEVAL_MEDICINE_V3_MASTER.wav'); x = x.astype(float).mean(1) / 32768
hop = 240  # 5 ms
f, t, Z = signal.stft(x, sr, nperseg=2048, noverlap=2048 - hop); M = np.abs(Z)
bands = {'low': (f < 150), 'mid': (f >= 150) & (f < 2000), 'high': f >= 2000}
flux = {k: np.maximum(0, np.diff(np.log1p(M[m] * 50), axis=1)).sum(0) for k, m in bands.items()}
tot = sum(v / v.max() for v in flux.values())
fps = sr / hop
# tempo via autocorrelation of onset strength
o = tot - signal.medfilt(tot, 41); o = np.maximum(o, 0)
ac = np.correlate(o, o, 'full')[len(o) - 1:]
lags = np.arange(len(ac)); bpm = 60 * fps / np.maximum(lags, 1); m = (bpm > 100) & (bpm < 160)
tempo = 60 * fps / lags[m][np.argmax(ac[m])]
# best beat phase for a fixed 132 BPM grid
B = 60 / 132; best = max(np.arange(0, B, 0.005), key=lambda ph: sum(o[int((ph + k * B) * fps)] for k in range(int((60 - ph) / B))))
# per-16th onset strength (low = kick/bass, high = percussion/claps)
S16 = B / 4
grid = []
for i in range(int((60 - best) / S16) - 1):
    tt = best + i * S16; a = int(tt * fps)
    w = slice(max(0, a - 4), a + 8)
    grid.append({'t': round(tt, 3), 'low': float(flux['low'][w].max()), 'mid': float(flux['mid'][w].max()), 'high': float(flux['high'][w].max())})
# per-bar energy and breaks
rms = lambda a, b: float(np.sqrt((x[int(a * sr):int(b * sr)] ** 2).mean()))
bars = [{'bar': i + 1, 't': round(best + i * 4 * B, 3), 'rms_db': round(20 * np.log10(rms(best + i * 4 * B, best + (i + 1) * 4 * B) + 1e-9), 1)} for i in range(33)]
# accents: strongest mid/high onsets that are not on the plain 4-on-floor kick
lowv = np.array([g['low'] for g in grid]); midv = np.array([g['mid'] for g in grid])
acc = [grid[i]['t'] for i in np.argsort(midv)[::-1][:60]]
# 'drops': sharpest rises in 1-bar energy
e = np.array([b['rms_db'] for b in bars]); rises = [bars[i]['t'] for i in np.argsort(np.diff(e))[::-1][:6] + 1]
dips = [b['t'] for b in bars if b['rms_db'] < np.median(e) - 2.5]
# quiet 100 ms windows (stop-time breaks)
w = int(0.1 * sr); q = [round(i / sr, 2) for i in range(0, len(x) - w, w) if 20 * np.log10(np.sqrt((x[i:i + w] ** 2).mean()) + 1e-9) < -24]
out = {'tempo_autocorr': round(float(tempo), 2), 'grid_phase_s': round(best, 3), 'bars': bars, 'energy_rises_at': sorted(rises), 'low_energy_bars_at': dips, 'quiet_100ms_windows': q, 'top_mid_accents': sorted(acc)}
json.dump(out, open('edit_map.json', 'w'), indent=1)
print('tempo', out['tempo_autocorr'], 'phase', out['grid_phase_s'])
print('bar energy dB:', ' '.join(f"{b['bar']}:{b['rms_db']}" for b in bars))
print('energy rises (drops) at', out['energy_rises_at'])
print('low-energy bars at', dips)
print('quiet windows', q)
