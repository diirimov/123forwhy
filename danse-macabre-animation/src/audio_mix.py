"""Final audio: DANSE_MACABRE_FINAL.wav untouched in timing/pitch/content; temporarily lowered under the
opening narration only (restored to 100% by 5.6 s). Narration = exact provided file, gain only."""
import numpy as np, soundfile as sf, subprocess, os, pyloudnorm as pyln
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mus, sr = sf.read(os.path.join(ROOT, 'assets/audio/DANSE_MACABRE_FINAL.wav'))
tmp = os.path.join(ROOT, 'build/narr48.wav')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', os.path.join(ROOT, 'assets/audio/narration_opening.mp3'),
                '-ar', '48000', '-ac', '1', '-c:a', 'pcm_f32le', tmp], check=True)
nar, _ = sf.read(tmp)
meter = pyln.Meter(sr)
n_l = meter.integrated_loudness(nar)
N = len(mus)
t = np.arange(N) / sr
# ducking curve (dB): -9 dB under phrases 1-2, -5 dB under the title phrase (drop energy still felt), back to 0
pts = [(0.0, -14.0), (3.45, -14.0), (3.53, -9.0), (5.30, -9.0), (5.75, 0.0), (60.0, 0.0)]
g_db = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
duck = 10 ** (g_db / 20)
out = mus * duck[:, None]
# narration level: ~ -15 LUFS integrated so it sits clearly above the ducked bed
ng = 10 ** (-1.2 / 20)  # gain only (no processing of the voice)
nv = np.zeros(N)
nv[:min(N, len(nar))] = nar[:N] * ng
out = out + nv[:, None]
pk = np.abs(out).max()
print('narration LUFS %.1f gain %.1f dB, mix peak %.2f dBFS' % (n_l, 20 * np.log10(ng), 20 * np.log10(pk)))
if pk > 0.89:
    # never clip: scale only the narration (music stays untouched)
    raise SystemExit('peak too high')
sf.write(os.path.join(ROOT, 'build/final_audio.wav'), out, sr, subtype='PCM_24')
# verify: music after 5.75 s is bit-identical to the source
same = np.max(np.abs(out[int(5.8 * sr):] - mus[int(5.8 * sr):]))
print('max deviation from original soundtrack after 5.8 s:', same)
