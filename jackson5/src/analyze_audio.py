"""Full-track audio analysis -> build/analysis.json (beats, downbeats, onsets, energy, vocal presence, sections)."""
import json, numpy as np, librosa
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
y, sr = librosa.load(HERE / 'audio/source.mp3', sr=22050, mono=True)
dur = len(y) / sr
hop = 512
H, P = librosa.effects.hpss(y)
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=hop, tightness=400)
bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
# low band (bass/kick) and snare band onset envelopes from the percussive part
S = np.abs(librosa.stft(P, hop_length=hop)); f = librosa.fft_frequencies(sr=sr)
low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[f < 150]), sr=sr, hop_length=hop)
snr = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[(f > 1500) & (f < 5000)]), sr=sr, hop_length=hop)
tfr = lambda t: np.clip(librosa.time_to_frames(t, sr=sr, hop_length=hop), 0, len(oenv) - 1)
# downbeat phase: which beat-of-4 has strongest bass and weakest snare (backbeat on 2/4)
score = []
for ph in range(4):
    sel = bt[ph::4]
    score.append(low[tfr(sel)].mean() - snr[tfr(sel)].mean())
phase = int(np.argmax(score))
downbeats = bt[phase::4]
# vocal presence: harmonic energy in 300-3400 Hz relative, smoothed
SH = np.abs(librosa.stft(H, hop_length=hop))
voc = SH[(f > 300) & (f < 3400)].sum(0); voc = np.convolve(voc, np.ones(20) / 20, 'same'); voc /= voc.max()
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; rms /= rms.max()
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
# structure: segment boundaries via chroma+mfcc agglomerative clustering on beat-synced features
chroma = librosa.feature.chroma_cqt(y=H, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=13)
feat = librosa.util.sync(np.vstack([chroma, mfcc / 50]), beats)
bounds = librosa.segment.agglomerative(feat, 14)
seg_t = sorted(set([0.0] + [float(bt[min(b, len(bt) - 1)]) for b in bounds if b > 0]))
# onsets
on = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=hop, units='time', backtrack=False)
strong = [float(t) for t in on if oenv[tfr(t)] > np.percentile(oenv, 85)]
per_sec = lambda arr: [round(float(arr[(times >= s) & (times < s + 1)].mean()), 3) for s in range(int(dur))]
out = dict(duration=dur, tempo=float(np.atleast_1d(tempo)[0]), beats=[round(float(b), 4) for b in bt],
           downbeat_phase=phase, downbeats=[round(float(b), 4) for b in downbeats], segments=seg_t,
           strong_onsets=strong, rms_per_sec=per_sec(rms), vocal_per_sec=per_sec(voc),
           low_onsets=[round(float(t), 3) for t in librosa.onset.onset_detect(onset_envelope=low, sr=sr, hop_length=hop, units='time')],
           snare_onsets=[round(float(t), 3) for t in librosa.onset.onset_detect(onset_envelope=snr, sr=sr, hop_length=hop, units='time')])
(HERE / 'build').mkdir(exist_ok=True)
json.dump(out, open(HERE / 'build/analysis.json', 'w'))
print('duration', round(dur, 2), 'tempo', out['tempo'], 'beats', len(bt), 'downbeat phase', phase, score)
print('first beats', out['beats'][:12]); print('downbeats', out['downbeats'][:20])
print('segments', [round(s, 1) for s in seg_t])
print('rms/s', out['rms_per_sec']); print('voc/s', out['vocal_per_sec'])
