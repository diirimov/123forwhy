"""Analyse DANSE_MACABRE_FINAL.wav -> data/beatmap.json (tempo, offset, beats, downbeats, bars, onsets, sections)."""
import numpy as np, soundfile as sf, json, os
from scipy.signal import butter, sosfilt, find_peaks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
y, sr = sf.read(os.path.join(ROOT, 'assets/audio/DANSE_MACABRE_FINAL.wav'))
m = y.mean(1)
HOP = 120  # 2.5 ms
nfft = 512


def stft_mag(x):
    n = (len(x) - nfft) // HOP
    idx = np.arange(nfft)[None, :] + HOP * np.arange(n)[:, None]
    return np.abs(np.fft.rfft(x[idx] * np.hanning(nfft), axis=1))


S = stft_mag(m)
freqs = np.fft.rfftfreq(nfft, 1 / sr)
L = np.log1p(S * 10)
flux = np.maximum(0, np.diff(L, axis=0))
onset = flux.sum(1)
low = flux[:, freqs < 150].sum(1)
mid = flux[:, (freqs > 1500) & (freqs < 8000)].sum(1)
fr = sr / HOP
t_on = (np.arange(len(onset)) + 1) * HOP / sr + nfft / 2 / sr


def norm(x):
    x = x - np.median(x)
    return np.maximum(x, 0) / (np.percentile(x, 99.5) + 1e-9)


onset, low, mid = norm(onset), norm(low), norm(mid)
# time-domain kick detector: 30-90 Hz envelope attack (bass notes are filtered + slower; kick has 150->46 Hz sweep)
kb = sosfilt(butter(4, [35, 110], 'bp', fs=sr, output='sos'), m)
env = np.sqrt(sosfilt(butter(2, 40, 'lp', fs=sr, output='sos'), kb ** 2).clip(0))
env = env[::HOP]
kick_on = norm(np.maximum(0, np.diff(env, prepend=env[0])) * (env > 0))
t_k = np.arange(len(kick_on)) * HOP / sr
# calibrate detector latency with a synthetic kick (sine sweep) placed at a known time
_n = np.arange(int(0.4 * sr)) / sr
_k = np.sin(2 * np.pi * np.cumsum(46 + 150 * np.exp(-_n / 0.028)) / sr) * np.exp(-_n / 0.17)
_x = np.zeros(sr); _x[int(0.5 * sr):int(0.5 * sr) + len(_k)] = _k
_e = np.sqrt(sosfilt(butter(2, 40, 'lp', fs=sr, output='sos'), sosfilt(butter(4, [35, 110], 'bp', fs=sr, output='sos'), _x) ** 2).clip(0))[::HOP]
_d = np.diff(_e, prepend=_e[0])
LATENCY = np.argmax(_d) * HOP / sr - 0.5
print('detector latency %.1f ms' % (LATENCY * 1000))
t_k = t_k - LATENCY
# tempo: autocorrelation of onset envelope, 90-180 BPM
ac = np.correlate(onset - onset.mean(), onset - onset.mean(), 'full')[len(onset) - 1:]
lags = np.arange(len(ac)) / fr
bpm_c = 60 / lags[1:]
sel = (bpm_c > 90) & (bpm_c < 180)
best = np.argmax(ac[1:][sel])
lag0 = lags[1:][sel][best]
# refine with comb fitting over a fine BPM grid and phase
best_score, bpm_best, off_best = -1, None, None
for bpm in np.arange(int(60 / lag0) - 4, int(60 / lag0) + 4, 0.01):
    period = 60 / bpm
    for off in np.arange(0, period, 0.002):
        tb = np.arange(off, 60, period)
        ii = np.clip(np.round((tb + LATENCY) * fr).astype(int), 0, len(kick_on) - 3)
        sc = (kick_on[ii] + kick_on[ii + 1] + kick_on[ii + 2]).sum()
        if sc > best_score:
            best_score, bpm_best, off_best = sc, bpm, off
    pass
period = 60 / bpm_best
beats = np.arange(off_best, 60.0 - 1e-6, period)
# downbeat phase: which beat-of-4 phase has most low+harmonic change energy averaged
def env_at(e, tt):
    ii = np.clip(np.round((tt - nfft / 2 / sr) * fr).astype(int) - 1, 0, len(e) - 1)
    w = np.stack([e[np.clip(ii + k, 0, len(e) - 1)] for k in range(-4, 5)]).max(0)
    return w
broad = norm(flux[:, freqs > 150].sum(1))
def chroma(seg):
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 16384))
    f = np.fft.rfftfreq(16384, 1 / sr)
    ok = (f > 60) & (f < 1500)
    pc = np.round(12 * np.log2(f[ok] / 440)).astype(int) % 12
    c = np.bincount(pc, weights=sp[ok] ** 2, minlength=12)
    return c / (np.linalg.norm(c) + 1e-9)
chs = [chroma(m[int(b * sr):int(b * sr) + int(period * sr)]) for b in beats[:-1]]
nov = [0.0] + [1 - float(np.dot(chs[i], chs[i - 1])) for i in range(1, len(chs))]
nov = np.array(nov + [0.0])
ph_scores = [nov[p::4].mean() for p in range(4)]
print('chord-change novelty by beat phase', np.round(ph_scores, 3))
dphase = int(np.argmax(ph_scores))
downbeats = beats[dphase::4]
# kick / percussion transients
pk, _ = find_peaks(kick_on, height=0.3, distance=int(0.1 * fr))
kicks = t_k[pk]
pk2, _ = find_peaks(mid, height=0.25, distance=int(0.05 * fr))
perc = t_on[pk2]
# loudness per bar
bars = []
for i, d in enumerate(downbeats):
    a, b = int(d * sr), int(min(60, d + 4 * period) * sr)
    seg = y[a:b]
    rms = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)
    lowr = 20 * np.log10(np.sqrt(np.mean(sosfilt(butter(4, 150, 'lp', fs=sr, output='sos'), seg.mean(1)) ** 2)) + 1e-9)
    nk = int(((kicks >= d - 0.02) & (kicks < d + 4 * period - 0.02)).sum())
    bars.append(dict(bar=i + 1, t=round(float(d), 4), rms_db=round(float(rms), 2), low_db=round(float(lowr), 2),
                     kicks=nk))
# composer-side knowledge (from the score that generated the track), verified against the detected grid
sections = [
    dict(name='intro_hook', bars=[1, 2]), dict(name='drop1', bars=[3, 8]), dict(name='call_response', bars=[9, 12]),
    dict(name='drop2', bars=[13, 20]), dict(name='build', bars=[21, 24]), dict(name='grand', bars=[25, 32]),
    dict(name='ending', bars=[33, 34])]
bar_t = lambda b: off_best + (b - 1) * 4 * period
for s in sections:
    s['start'] = round(bar_t(s['bars'][0]), 4)
    s['end'] = round(min(60.0, bar_t(s['bars'][1] + 1)), 4)
accent_steps = {'hook_syncopation': [(b, 7) for b in (1, 2, 3, 4, 13, 14, 17, 18, 25, 26, 29, 30)],
                'impacts': [(3, 0), (13, 0), (25, 0), (33, 12)],
                'phrase_fills': [(b, 12) for b in (8, 12, 16, 20, 28, 32)],
                'breath_before_grand': [(24, 12)], 'loop_knocks': [(34, 12), (34, 13), (34, 14), (34, 15)]}
step = period / 4
acc = {k: [round(bar_t(b) + s * step + (0.07 * step if s % 2 else 0), 4) for b, s in v] for k, v in accent_steps.items()}
# check: nearest detected onset to each impact
check = {str(t): round(float(np.min(np.abs(kicks - t))) * 1000, 1) for t in acc['impacts']}
out = dict(file='DANSE_MACABRE_FINAL.wav', duration=len(y) / sr, bpm=round(float(bpm_best), 3),
           beat_period=round(period, 6), beat_offset=round(float(off_best), 4), downbeat_phase=dphase,
           swing_16th_s=round(0.07 * step, 4), fps=60,
           beats=[round(float(b), 4) for b in beats], downbeats=[round(float(b), 4) for b in downbeats],
           beat_frames=[int(round(b * 60)) for b in beats], bars=bars, sections=sections, accents=acc,
           impact_onset_error_ms=check, kick_onsets=[round(float(k), 4) for k in kicks],
           perc_onsets=[round(float(k), 4) for k in perc])
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'data/beatmap.json'), 'w'), indent=1)
print('BPM %.3f offset %.4f s  downbeat phase %d  beats %d  kicks %d' % (bpm_best, off_best, dphase, len(beats), len(kicks)))
print('impact onset error ms', check)
for b in bars:
    print(b)
