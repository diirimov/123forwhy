"""
Render, mix, master and export DANCING PLAGUE 1518 (extended dance version).

    python3 render.py [outdir]

Writes (into outdir, default ..):
  DANCING_PLAGUE_1518_EXTENDED.wav   48 kHz / 24-bit master
  DANCING_PLAGUE_1518_EXTENDED.mp3   320 kbps CBR
  stems/*.flac                       8 musical stems, post-fader, 24-bit (they sum to the pre-master mix)
  DANCING_PLAGUE_1518_BEATS.json     beat / downbeat / section timestamps
  DANCING_PLAGUE_1518_CUES.md        arrangement sheet
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import maximum_filter1d

import engine as E
import song as S
from engine import SR, filt, peq, shelf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, ".."))
NAME = "DANCING_PLAGUE_1518_EXTENDED"

LEVELS = {"kick": 1.85, "clap": 2.4, "tabor": 2.0, "tom": 1.8, "cym": 1.5,
          "riq": 3.3, "shaker": 3.6, "tick": 2.6, "frame": 2.4, "wood": 2.6,
          "bass": 3.4, "sub": 3.0, "drone": 1.5,
          "lute": 0.8, "chop": 0.25,
          "fiddle": 3.7, "fiddle2": 2.3, "gurdy": 1.7,
          "pipe": 3.6, "flute": 1.6,
          "fx": 1.2, "boom": 1.3}
DUCK = {"bass": 0.8, "sub": 0.75, "chop": 0.5, "drone": 0.55, "lute": 0.2, "fiddle2": 0.15, "gurdy": 0.15}
STEMS = ["drums", "percussion", "bass", "drone", "lute", "strings", "lead", "fx"]


def make_ir(sec, er=True, damp=6500, seed=7):
    r = np.random.default_rng(seed)
    n = int(sec * SR); t = np.arange(n) / SR; ir = np.zeros((n, 2))
    for c in range(2):
        nz = filt(r.normal(0, 1, n), "low", damp)
        ir[:, c] = nz * np.exp(-t / (sec / 6.9 * 2)) * np.minimum(1, t / 0.01)
        if er:
            for d, g in ((0.009, 0.5), (0.017, 0.35), (0.026, 0.3), (0.037, 0.22)):
                ir[int((d + 0.0023 * c) * SR), c] += g * 8
    ir = filt(ir, "high", 250)
    return ir / np.sqrt((ir ** 2).sum())


def mix(T):
    IR_ROOM = make_ir(1.3)
    IR_PLATE = np.vstack([np.zeros((int(0.015 * SR), 2)), make_ir(0.8, er=False, damp=8500, seed=9)])
    ke = filt(np.abs(T["kick"].buf[:, 0]), "low", 25); ke /= ke.max() + 1e-9
    sc = 1 - 0.6 * np.clip(ke * 2.5, 0, 1)
    stems = {s: np.zeros_like(T["kick"].buf) for s in STEMS}
    sends = {s: [np.zeros_like(T["kick"].buf), np.zeros_like(T["kick"].buf)] for s in STEMS}
    for k, tr in T.items():
        x = tr.buf * LEVELS[k]
        if k in DUCK:
            x = x * (1 - DUCK[k] + DUCK[k] * sc)[:, None]
        if k in ("bass", "sub"):
            x = filt(x, "high", 28)
        elif k not in ("kick", "tom", "boom"):
            x = filt(x, "high", 55 if k in ("drone", "frame") else 100)
        if k == "pipe":
            x = peq(x, 2600, 1.5, 1.0)              # presence so the hook reads on phone speakers
        stems[tr.stem] += x
        sends[tr.stem][0] += x * tr.rev
        sends[tr.stem][1] += x * tr.plate
    out = {}
    for s in STEMS:
        wet = np.stack([signal.fftconvolve(sends[s][0][:, c], IR_ROOM[:, c])[: len(stems[s])] for c in range(2)], 1)
        wet2 = np.stack([signal.fftconvolve(sends[s][1][:, c], IR_PLATE[:, c])[: len(stems[s])] for c in range(2)], 1)
        out[s] = stems[s] + wet + wet2 * 0.9
    return out


def master_eq(x):
    x = filt(x, "high", 28)
    x = shelf(x, 110, 2.5, high=False)   # weight, matched to the reference
    x = peq(x, 36, -2.0, 1.0)            # keep the very bottom from eating headroom
    x = peq(x, 85, 2.5, 1.0)             # kick / bass punch
    x = peq(x, 190, 1.5, 0.9)            # warmth
    x = peq(x, 180, -1.5, 0.8)
    x = peq(x, 330, -3.0, 0.8)           # de-mud (reference keeps the low-mids lean)
    x = peq(x, 650, -1.0, 1.0)
    x = peq(x, 1700, 1.8, 0.7)           # presence (reference 1-4 kHz)
    x = peq(x, 2500, 2.0, 0.6)           # clarity of pipe & fiddle, phone-speaker read
    x = shelf(x, 4000, 1.5)              # air of shakers / riq jingles (reference is denser up top)
    x = shelf(x, 11000, -1.0)            # but keep it warm, never fizzy
    return x


def glue(x, thr_db=-15, ratio=2.0, att=0.012, rel=0.15):
    lvl = np.sqrt(filt((x ** 2).mean(axis=1), "low", 12).clip(1e-12))
    g = 10 ** (-np.maximum(0, 20 * np.log10(lvl) - thr_db) * (1 - 1 / ratio) / 20)
    out = np.empty_like(g); prev = 1.0
    aa, ar = np.exp(-64 / (att * SR)), np.exp(-64 / (rel * SR))
    for i in range(0, len(g), 64):
        tgt = g[i:i + 64].min(); c = aa if tgt < prev else ar
        prev = c * prev + (1 - c) * tgt; out[i:i + 64] = prev
    return x * out[:, None]


def limiter(x, ceil=0.89, rel=0.06):
    up = signal.resample_poly(x, 4, 1, axis=0)
    pk = np.abs(up).max(axis=1)[: len(x) * 4].reshape(-1, 4).max(axis=1)
    pk = maximum_filter1d(pk, size=2 * int(0.003 * SR) + 1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    out = np.empty_like(g); prev = 1.0; ar = np.exp(-1 / (rel * SR))
    for i in range(len(g)):
        v = g[i]; prev = v if v < prev else ar * prev + (1 - ar) * v; out[i] = prev
    return x * np.minimum(filt(out, "low", 400), g)[:, None]


def stereo_width(x, amt=1.3):
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2
    s = filt(s, "high", 160) * amt
    return np.stack([m + s, m - s], 1)


def master(x, pre, drive):
    x = master_eq(x) * pre
    x = stereo_width(x)
    x = glue(x)
    x = np.tanh(x * 1.4) / np.tanh(1.4)
    x = limiter(x * drive)
    fade = np.ones(len(x)); nf = int(1.0 * SR)
    fade[-nf:] = np.linspace(1, 0, nf) ** 2
    return x * fade[:, None]


def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x)


def beats_json(path):
    beats = []
    for b in range(S.NBARS * 4 + 1):
        t = S.ts(b * 4)
        beats.append({"time": round(t, 4), "bar": b // 4 + 1, "beat": b % 4 + 1, "downbeat": b % 4 == 0})
    data = {
        "title": "Dancing Plague 1518 (Extended Dance Version)",
        "bpm": S.BPM, "time_signature": "4/4", "swing_16th": S.SWING,
        "bar_seconds": round(S.BAR, 6), "beat_seconds": round(S.BEAT, 6),
        "bars": S.NBARS, "music_end_seconds": round(S.ts(S.NBARS * 16), 4),
        "file_seconds": round(S.N / SR, 4),
        "beats": beats,
        "downbeats": [round(S.ts(b * 16), 4) for b in range(S.NBARS + 1)],
        "sections": [{"bar": b + 1, "time": round(S.ts(b * 16), 4), "name": n, "description": d}
                     for b, n, d in S.SECTIONS],
        "accents": [{"time": round(t, 4), "kind": k, "text": x} for t, k, x in sorted(S.ACCENTS)],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


def cues_md(path, lu, peak):
    with open(path, "w") as f:
        f.write("# DANCING PLAGUE 1518 -- extended dance version: cue sheet\n\n")
        f.write(f"{S.BPM} BPM, 4/4, {S.NBARS} bars, D (drone) with Phrygian/Dorian colour. 1 bar = {S.BAR:.4f} s, "
                f"1 beat = {S.BEAT:.4f} s. Music ends {S.ts(S.NBARS * 16):.2f} s, file {S.N / SR:.2f} s.\n\n")
        f.write(f"Master: {lu:.1f} LUFS integrated, true-peak ceiling {peak:.2f} dBFS.\n\n## Arrangement\n\n")
        f.write("| Bar | Time | Section | What happens |\n|---|---|---|---|\n")
        for b, n, d in S.SECTIONS:
            t = S.ts(b * 16)
            f.write(f"| {b + 1} | {int(t // 60)}:{t % 60:05.2f} | {n} | {d} |\n")


def main():
    os.makedirs(os.path.join(OUT, "stems"), exist_ok=True)
    print("building score ..."); T = S.build()
    print("mixing ...")
    stems = mix(T)
    full = sum(stems.values())
    pre = 0.5 / np.abs(master_eq(full)).max()
    drive = 10 ** ((-10.0 - lufs(master(full, pre, 1.0))) / 20)
    final = master(full, pre, drive)
    lu = lufs(final)
    up = signal.resample_poly(final, 4, 1, axis=0)
    tp = 20 * np.log10(np.abs(up).max())
    print(f"LUFS {lu:.2f}  true peak {tp:.2f} dBTP  length {len(final) / SR:.2f} s")
    wav = os.path.join(OUT, NAME + ".wav")
    sf.write(wav, final, SR, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "320k",
                    "-ar", "48000", "-id3v2_version", "3", "-metadata", "title=Dancing Plague 1518 (Extended Dance Version)",
                    os.path.join(OUT, NAME + ".mp3")], check=True)
    # stems: same pre-gain and drive as the master (pre-limiter), so they line up with the mix
    g = pre * drive
    for s, x in stems.items():
        y = x * g
        pk = np.abs(y).max()
        if pk > 0.99:
            y = y * 0.99 / pk
        sf.write(os.path.join(OUT, "stems", f"DP1518_STEM_{STEMS.index(s) + 1:02d}_{s.upper()}.flac"), y, SR, subtype="PCM_24")
    beats_json(os.path.join(OUT, "DANCING_PLAGUE_1518_BEATS.json"))
    cues_md(os.path.join(OUT, "DANCING_PLAGUE_1518_CUES.md"), lu, tp)
    print("done ->", OUT)


if __name__ == "__main__":
    main()
