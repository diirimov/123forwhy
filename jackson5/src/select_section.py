"""Score every downbeat-aligned 65-70 s window and pick the strongest; writes build/selection.json."""
import json, numpy as np, librosa
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
a = json.load(open(HERE / 'build/analysis.json'))
y, sr = librosa.load(HERE / 'audio/source.mp3', sr=22050)
hop = 2205
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; rms /= rms.max()
T = lambda s: int(s * 10)
db = np.array(a['downbeats']); segs = np.array(a['segments'])
first_sound = float(np.argmax(rms > 0.02) / 10)
starts = [first_sound] + [d for d in db if d < a['duration'] - 66]
cands = []
for s in starts:
    for e in db:
        L = e - s
        if not (65 <= L <= 70):
            continue
        w = rms[T(s):T(e)]
        n = len(w)
        open_ = w[:30].mean()                       # first 3 s attention
        dev = w[int(.6 * n):].mean() - w[:int(.3 * n)].mean()
        climax = np.convolve(w[int(.6 * n):], np.ones(40) / 40, 'valid').max()
        end_gap = np.min(np.abs(segs - e))          # ending on a structural boundary
        start_gap = np.min(np.abs(segs - s))
        iconic = 1.0 if s < 1.0 else 0.0            # editorial: the song's famous piano-gliss intro
        score = 1.0 * open_ + 1.5 * dev + 1.0 * climax - 0.08 * end_gap - 0.05 * start_gap + 0.35 * iconic
        cands.append(dict(start=round(s, 3), end=round(e, 3), length=round(L, 2), opening=round(float(open_), 3),
                          development=round(float(dev), 3), climax=round(float(climax), 3),
                          end_to_boundary=round(float(end_gap), 2), iconic_intro=bool(iconic), score=round(float(score), 3)))
cands.sort(key=lambda c: -c['score'])
# keep best per distinct start region
shown, seen = [], []
for c in cands:
    if all(abs(c['start'] - s) > 8 for s in seen):
        shown.append(c); seen.append(c['start'])
for c in shown[:6]:
    print(c)
json.dump(dict(first_sound=first_sound, candidates=shown[:8], chosen=shown[0]), open(HERE / 'build/selection.json', 'w'), indent=1)
