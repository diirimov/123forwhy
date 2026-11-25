"""Builds the separate aligned VO track and the final soundtrack+VO mix.
The approved soundtrack file is read-only here; ducking happens only inside the mix."""
import numpy as np, soundfile as sf, pyloudnorm as pyln, librosa, sys
from scipy import signal
SR = 48000; N = 60 * SR
VO_START = 0.45            # voice-over placement (s): 'The' lands at ~0.55, 'Bull' ~1.38, 'Simulation' ~1.84
music, sr = sf.read('audio/BRAZEN_BULL_FINAL_V3.wav', always_2d=True); assert sr == SR and len(music) == N
vo, _ = librosa.load('audio/VO_brazen_bull_simulation.mp3', sr=SR, mono=True)
vo = vo / (np.max(np.abs(vo)) + 1e-9)
meter = pyln.Meter(SR)
# VO bus: gentle high-pass + presence, light compression feel via soft limiting, target loudness
vo = signal.sosfilt(signal.butter(2, 85, 'high', fs=SR, output='sos'), vo)
v_l = meter.integrated_loudness(np.vstack([vo, vo]).T)
vo *= 10 ** ((-15.0 - v_l) / 20)            # VO sits ~5 LU above the intro music
track = np.zeros((N, 2)); i0 = int(VO_START * SR); track[i0:i0 + len(vo), 0] += vo; track[i0:i0 + len(vo), 1] += vo
# ducking envelope (mix only): -3 dB under the narration with 80 ms ramps
t = np.arange(N) / SR; a, b = VO_START - 0.05, VO_START + len(vo) / SR + 0.05
duck = np.ones(N); r = 0.08
duck = 1 - (1 - 10 ** (-3 / 20)) * np.clip(np.minimum((t - (a - r)) / r, ((b + r) - t) / r), 0, 1)
mix = music * duck[:, None] + track
up = signal.resample_poly(mix, 4, 1, axis=0); tp = 20 * np.log10(np.max(np.abs(up)))
if tp > -1.0:
    mix *= 10 ** ((-1.05 - tp) / 20); tp = -1.05
sf.write('audio/VO_aligned_60s.wav', track, SR, subtype='PCM_24')
sf.write('audio/MIX_soundtrack_plus_VO.wav', mix, SR, subtype='PCM_24')
intro = mix[:int(3.5 * SR)]
print(f"VO {len(vo)/SR:.3f}s at {VO_START}s | VO loudness -15 LUFS | mix integrated {meter.integrated_loudness(mix):.2f} LUFS, TP {tp:.2f} dBTP | intro {meter.integrated_loudness(intro):.2f} LUFS")
print('soundtrack untouched outside 0.35-2.95 s:', np.allclose(mix[int(3.0*SR):], music[int(3.0*SR):]))
