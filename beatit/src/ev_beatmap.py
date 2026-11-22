"""Beat map for the 60 s Beat It edit -> output/EVOLUTION_BEAT_MAP.json + .md
beats/downbeats (smoothed grid), kick & snare hits ranked by strength, guitar accents, vocal entries,
chorus-like sections, breaks."""
import _paths  # noqa
import json
import numpy as np
import librosa
from scipy.signal import find_peaks
import timing as T
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
y, sr = librosa.load(ROOT / 'audio' / 'source.wav', sr=22050, mono=True)
hop = 256
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
Hs, Ps = librosa.decompose.hpss(S)
tt = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
def flux(M):
    d = np.diff(np.log1p(M), axis=1)
    o = np.concatenate([[0], np.maximum(d, 0).sum(0)])
    return o / (np.percentile(o, 99) + 1e-9)
kick = flux(Ps[(f > 35) & (f < 130)])
snare = flux(Ps[(f > 1500) & (f < 6000)]) * 0.5 + flux(Ps[(f > 180) & (f < 400)]) * 0.5
guitar = flux(Hs[(f > 900) & (f < 4500)])
rms = librosa.feature.rms(S=S)[0]
rms = rms / rms.max()
voc = Hs[(f > 300) & (f < 3400)].sum(0)
voc = np.convolve(voc, np.ones(9) / 9, 'same')
voc = voc / np.percentile(voc, 98)

def hits(o, dist=0.18, top=None, pct=80):
    pk, pr = find_peaks(o, distance=int(dist * sr / hop), height=np.percentile(o, pct))
    out = sorted([(float(tt[p]), float(o[p])) for p in pk], key=lambda x: -x[1])
    return sorted(out[:top] if top else out)

def grid_pos(t):
    b = T.beat_at(t) - T.PHASE
    return f'bar {int(b // 4) + 1} beat {int(b % 4) + 1}' + ('' if abs(b - round(b)) < 0.12 else ' (off-beat)')

kicks = hits(kick, 0.2, pct=75)
snares = hits(snare, 0.2, pct=75)
k_strength = np.array([s for _, s in kicks])
s_strength = np.array([s for _, s in snares])
strong_k = [(round(t, 3), round(s, 2)) for t, s in kicks if s >= np.percentile(k_strength, 70)]
strong_s = [(round(t, 3), round(s, 2)) for t, s in snares if s >= np.percentile(s_strength, 70)]
gtr = [(round(t, 3), round(s, 2)) for t, s in hits(guitar, 0.35, top=24, pct=90)]
# vocal entries: vocal energy rises above 0.45 after >= 0.35 s below 0.25
ent, low_since = [], None
for i, v in enumerate(voc):
    if v < 0.25:
        low_since = low_since if low_since is not None else tt[i]
    elif v > 0.45 and low_since is not None:
        if tt[i] - low_since >= 0.35:
            ent.append(round(float(tt[i]), 3))
        low_since = None
# breaks: rms 0.25 s windows well below the local level
win = int(0.25 * sr / hop)
rw = np.array([rms[i:i + win].mean() for i in range(0, len(rms) - win, win // 2)])
rt = tt[::win // 2][:len(rw)]
med = np.median(rw)
brk = []
for t0, v in zip(rt, rw):
    if v < 0.45 * med and (not brk or t0 - brk[-1][1] > 0.4):
        brk.append([round(float(t0), 2), round(float(t0 + 0.25), 2)])
    elif v < 0.45 * med:
        brk[-1][1] = round(float(t0 + 0.25), 2)
# chorus-like sections: 2-bar windows with the highest sustained vocal energy
bars = [(T.db(n), T.db(n + 2)) for n in range(0, 33, 2)]
vbar = [(a, b, float(voc[(tt >= a) & (tt < b)].mean())) for a, b in bars]
thr = np.percentile([v for _, _, v in vbar], 70)
chorus = [(round(a, 3), round(b, 3)) for a, b, v in vbar if v >= thr]

out = dict(duration=60.0, bpm=round(60 / T.PERIOD, 2), beat_period=round(T.PERIOD, 4), downbeat_phase=T.PHASE,
           beats=[round(float(b), 3) for b in T.BEATS], downbeats=[round(T.db(n), 3) for n in range(35)],
           strong_kicks=strong_k, strong_snares=strong_s, guitar_accents=gtr, vocal_entries=ent, breaks=brk,
           chorus_sections=chorus)
(ROOT / 'output' / 'EVOLUTION_BEAT_MAP.json').write_text(json.dumps(out, indent=1))
md = ['# Beat It (60 s edit) - beat map', '', f'- Tempo: **{out["bpm"]} BPM** (beat {out["beat_period"]} s, bar {4 * T.PERIOD:.3f} s), 4/4, '
      f'grid smoothed from librosa beat tracking; first downbeat {T.db(0):.3f} s.', '- Times in seconds from the first sample.', '',
      '## Downbeats (bar starts)', '', ', '.join(f'{n + 1}: {T.db(n):.3f}' for n in range(35)), '',
      '## Breaks (energy drops - used for reveals / transformations)', ''] + [f'- {a:.2f}-{b:.2f} s ({grid_pos(a)})' for a, b in brk] + [
      '', '## Vocal entries', ''] + [f'- {t:.3f} s ({grid_pos(t)})' for t in ent] + [
      '', '## Chorus-like sections (highest sustained vocal energy, 2-bar windows)', ''] + [f'- {a:.3f}-{b:.3f} s' for a, b in chorus] + [
      '', '## Strongest kick hits', ''] + [f'- {t:.3f} s  strength {s:.2f}  ({grid_pos(t)})' for t, s in strong_k] + [
      '', '## Strongest snare hits', ''] + [f'- {t:.3f} s  strength {s:.2f}  ({grid_pos(t)})' for t, s in strong_s] + [
      '', '## Guitar / harmonic accents (top 24)', ''] + [f'- {t:.3f} s  strength {s:.2f}  ({grid_pos(t)})' for t, s in gtr]
(ROOT / 'output' / 'EVOLUTION_BEAT_MAP.md').write_text('\n'.join(md) + '\n')
print('bpm', out['bpm'], '| breaks', brk, '\nvocal entries', ent, '\nchorus', chorus)
print('strong kicks', len(strong_k), strong_k[:40])
print('strong snares', len(strong_s), strong_s[:40])
print('guitar', gtr)
