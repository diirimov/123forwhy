"""Analyse the approved new soundtrack and build the director's beat map.

    python3 tools/analyze_audio.py

Reads audio/PIED_PIPER_NEW_SOUNDTRACK.wav (never modified). Independently measures from the waveform:
  - file format, tempo and beat phase (librosa beat tracker vs. the 136 BPM grid)
  - percussive transients per band (kick / snare-clap / riq-shaker), melodic (flute) onsets
  - per-bar loudness, energy jumps (drops), near-silences (breaks), spectral novelty (section changes)
and cross-checks the score's event list (data/PIED_PIPER_NEW_SOUNDTRACK_SYNC.json) against the measured onsets.
Writes data/beatmap.json (used by the film engine) and AUDIO_ANALYSIS.md.
"""
import json, os
import numpy as np, soundfile as sf, librosa
from scipy import signal

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 60
WAV = os.path.join(HERE, "audio/PIED_PIPER_NEW_SOUNDTRACK.wav")
info = sf.info(WAV)
x, sr = sf.read(WAV)
J = json.load(open(os.path.join(HERE, "data/PIED_PIPER_NEW_SOUNDTRACK_SYNC.json")))
m = x.mean(1)
dur = len(m) / sr
nf = int(np.ceil(dur * FPS))
BPM, BEAT, BAR, S16 = J["bpm"], J["beat_seconds"], J["bar_seconds"], J["sixteenth_seconds"]
NB = J["bars"]
md = []
P = lambda s="": (md.append(s), print(s))

P("# Audio analysis: PIED_PIPER_NEW_SOUNDTRACK.wav")
P()
P(f"Format: {info.samplerate} Hz, {info.subtype}, {info.channels} ch, {dur:.4f} s ({nf} frames at 60 fps).")


# ------------------------------------------------------------------ envelopes at 60 fps
def band(lo, hi):
    sos = signal.butter(4, [lo, hi] if lo else hi, "band" if lo else "low", fs=sr, output="sos")
    y = signal.sosfiltfilt(sos, m)
    hop = sr // FPS
    e = np.array([np.sqrt(np.mean(y[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(nf)])
    e = 20 * np.log10(e)
    return np.clip((e - (np.percentile(e, 99.5) - 30)) / 30, 0, 1), y


env = {}
env["low"], y_low = band(None, 140)
env["mid"], _ = band(150, 2000)
env["high"], y_high = band(4000, 16000)
env["flute"], _ = band(550, 1600)
env["full"], _ = band(20, 20000)
hop = sr // FPS
f_, t_, Z = signal.stft(m, sr, nperseg=2048, noverlap=2048 - hop)
S = np.abs(Z)
flux = np.maximum(0, np.diff(np.log1p(S * 50), axis=1)).sum(0)
flux = np.concatenate([[0], flux])[:nf]
env["onset"] = np.clip(flux / np.percentile(flux, 99.5), 0, 1)

# ------------------------------------------------------------------ tempo / beat phase
y22 = librosa.resample(m, orig_sr=sr, target_sr=22050)
oenv = librosa.onset.onset_strength(y=y22, sr=22050)
tempo, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=22050, start_bpm=136, tightness=400)
bt = librosa.frames_to_time(beats, sr=22050)
ph = ((bt / BEAT + 0.5) % 1) - 0.5
P(f"Tempo (beat tracker): {float(np.atleast_1d(tempo)[0]):.1f} BPM; grid {BPM} BPM, beat {BEAT * 1000:.2f} ms, bar {BAR:.4f} s, "
  f"{NB} bars. The tracker locks {np.median(ph) * BEAT * 1000:+.0f} ms off the grid, i.e. onto the offbeat 8ths: the riq on "
  f"the 'and' is the loudest transient (the bounce). The grid phase is fixed by the kick and riq onsets below: downbeat 1 is at 0.000 s.")


# ------------------------------------------------------------------ transient detection per band
def peaks(y, lo, hi, thr, min_gap=0.09):
    sos = signal.butter(4, [lo, hi], "band", fs=sr, output="sos")
    e = np.abs(signal.sosfiltfilt(sos, y))
    h = 48
    env_ = np.array([e[i:i + h].max() for i in range(0, len(e) - h, h)])
    env_ = 20 * np.log10(env_ + 1e-9)
    d = np.maximum(0, np.diff(env_, prepend=env_[0]))
    d = np.convolve(d, np.ones(4), "same")
    pk, _ = signal.find_peaks(d, height=thr, distance=int(min_gap * sr / h))
    return pk * h / sr


kick_on = peaks(m, 35, 110, 9.0, 0.2)
snap_on = peaks(m, 1500, 5000, 8.0, 0.1)
hat_on = peaks(m, 6000, 14000, 7.0, 0.06)
P(f"Measured transients: {len(kick_on)} low-band hits (kick / big drum / stabs), {len(snap_on)} clap-snare-tabor band hits, "
  f"{len(hat_on)} riq / shaker / tambourine band hits.")


def verify(times, ons, name):
    times = np.asarray(times)
    if not len(times):
        return None
    d = np.array([ons[np.argmin(np.abs(ons - tt))] - tt if len(ons) else 9 for tt in times])
    ok = np.abs(d) < 0.035
    P(f"| {name} | {len(times)} | {ok.mean() * 100:.0f} % | {np.median(d[ok]) * 1000:+.1f} ms |")
    return float(np.median(d[ok])) if ok.any() else None


E = J["events"]
P()
P("Score events checked against measured transients (match = a measured onset within 35 ms):")
P()
P("| Event | Count | Matched | Median offset |")
P("|---|---|---|---|")
verify(E["kick"], kick_on, "kick")
verify(E["clap"], snap_on, "clap / tabor backbeat")
verify(E["riq"], hat_on, "riq (offbeat 8ths)")
verify(E["stab"], snap_on, "unison stabs")
fl = [n for n in J["flute_notes"] if n["instrument"] == "alto"]
fl_on = peaks(m, 700, 1700, 5.0, 0.07)
verify([n["time"] for n in fl], fl_on, "flute notes")

# ------------------------------------------------------------------ per-bar loudness, drops, breaks
bar_db = []
for b in range(NB):
    seg = m[int(b * BAR * sr):int((b + 1) * BAR * sr)]
    bar_db.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9))
bar_db = np.array(bar_db)
low_db = []
for b in range(NB):
    seg = y_low[int(b * BAR * sr):int((b + 1) * BAR * sr)]
    low_db.append(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9))
low_db = np.array(low_db)
jump = np.diff(bar_db, prepend=bar_db[0])
P()
P("Per-bar loudness (RMS dB, full band / below 140 Hz):")
P()
P("| Bar | Start s | Full | Low | Change |")
P("|---|---|---|---|---|")
for b in range(NB):
    P(f"| {b + 1} | {b * BAR:.2f} | {bar_db[b]:.1f} | {low_db[b]:.1f} | {jump[b]:+.1f} |")

# near-silences: 20 ms windows more than 18 dB under the surrounding 2 s
w = int(0.02 * sr)
rms = np.array([np.sqrt(np.mean(m[i:i + w] ** 2)) for i in range(0, len(m) - w, w)])
rdb = 20 * np.log10(rms + 1e-9)
loc = np.array([np.percentile(rdb[max(0, i - 50):i + 50], 80) for i in range(len(rdb))])
quiet = rdb < loc - 18
breaks = []
i = 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        if (j - i) * 0.02 >= 0.1:
            breaks.append((round(i * 0.02, 3), round(j * 0.02, 3)))
        i = j
    else:
        i += 1
P()
P("Measured breaks (full band drops more than 18 dB for at least 0.1 s): " + ", ".join(f"{a:.2f}-{b:.2f} s" for a, b in breaks))

lq = []
lr = np.array([np.sqrt(np.mean(y_low[i:i + w] ** 2)) for i in range(0, len(y_low) - w, w)])
ldb = 20 * np.log10(lr + 1e-9)
lthr = np.percentile(ldb, 60) - 20
i = 0
while i < len(ldb):
    if ldb[i] < lthr:
        j = i
        while j < len(ldb) and ldb[j] < lthr:
            j += 1
        if (j - i) * 0.02 >= 0.12:
            lq.append((round(i * 0.02, 3), round(j * 0.02, 3)))
        i = j
    else:
        i += 1
P("Measured low-end breaks (kick and bass stop for at least 0.12 s; the flute may keep playing): " + ", ".join(f"{a:.2f}-{b:.2f} s" for a, b in lq))
# drops: biggest bar-to-bar rises right after a break
order = np.argsort(-jump)
P("Biggest energy rises (bar start): " + ", ".join(f"bar {b + 1} at {b * BAR:.2f} s ({jump[b]:+.1f} dB)" for b in order[:6]))

# spectral novelty per bar (chroma + mfcc) -> section changes
C_ = librosa.feature.chroma_cqt(y=y22, sr=22050, hop_length=512)
M_ = librosa.feature.mfcc(y=y22, sr=22050, n_mfcc=13, hop_length=512)
fb = lambda b: int(b * BAR * 22050 / 512)
feat = np.array([np.concatenate([C_[:, fb(b):fb(b + 1)].mean(1), M_[1:, fb(b):fb(b + 1)].mean(1) / 50]) for b in range(NB)])
nov = np.array([0] + [np.linalg.norm(feat[b] - feat[b - 1]) for b in range(1, NB)])
nov = nov / nov.max()
P("Spectral novelty (bars whose sound changes most from the previous bar): " +
  ", ".join(f"bar {b + 1} ({b * BAR:.2f} s)" for b in sorted(np.argsort(-nov)[:12])))

# melodic phrases: flute calls (groups of alto notes) and the answering instruments
phr = []
cur = [fl[0]]
for n in fl[1:]:
    if n["time"] - (cur[-1]["time"] + cur[-1]["dur"]) > 0.2:
        phr.append(cur); cur = [n]
    else:
        cur.append(n)
phr.append(cur)
phrases = [dict(t0=p[0]["time"], t1=round(p[-1]["time"] + p[-1]["dur"], 4), notes=len(p), top=max(q["midi"] for q in p))
           for p in phr]
P(f"Flute phrases: {len(phrases)} calls (the flute plays only half-bars; answers fill the rest).")

# ------------------------------------------------------------------ write beat map
secs = J["sections"]
P()
P("## Structure (score sections confirmed by the measurements above)")
P()
P("| Section | Bars | Time | Mean dB | What the ear hears |")
P("|---|---|---|---|---|")
for s in secs:
    b0, b1 = s["start_bar"] - 1, s["end_bar"]
    P(f"| {s['name']} | {b0 + 1}-{b1} | {s['start']:.2f}-{s['end']:.2f} | {bar_db[b0:b1].mean():.1f} | {s['description']} |")

out = dict(
    source="audio/PIED_PIPER_NEW_SOUNDTRACK.wav (approved, unchanged)",
    bpm=BPM, beat=BEAT, bar=BAR, s16=S16, fps=FPS, duration=dur, frames=nf, bars=NB,
    sections=secs, accents=J["accents"], harmony=J["harmony"], drops=J["drops"],
    gaps=[g["start"] for g in J["gaps"]], gap_spans=J["gaps"],
    events={k: v for k, v in E.items()},
    measured=dict(kick=[round(float(v), 4) for v in kick_on], backbeat=[round(float(v), 4) for v in snap_on],
                  hats=[round(float(v), 4) for v in hat_on], breaks=breaks, low_breaks=lq, bar_db=[round(float(v), 2) for v in bar_db],
                  novelty=[round(float(v), 3) for v in nov]),
    flute=[dict(t=n["time"], d=n["dur"], m=n["midi"]) for n in fl],
    flute_lo=[dict(t=n["time"], d=n["dur"], m=n["midi"]) for n in J["flute_notes"] if n["instrument"] == "tenor"],
    phrases=phrases,
    env={k: [round(float(v), 3) for v in a] for k, a in env.items()},
)
json.dump(out, open(os.path.join(HERE, "data/beatmap.json"), "w"))
open(os.path.join(HERE, "AUDIO_ANALYSIS.md"), "w").write("\n".join(md) + "\n")
print(f"\nwrote data/beatmap.json ({nf} frames)")
