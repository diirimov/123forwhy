"""
THE PIED PIPER OF HAMELIN -- new soundtrack: mix, master, exports.

    python3 render.py <outdir> [--fresh] [--stems]

Writes PIED_PIPER_NEW_SOUNDTRACK.wav (48 kHz / 24-bit, -14 LUFS integrated, <= -1 dBTP) and
PIED_PIPER_NEW_SOUNDTRACK_SYNC.json.

Mix and master follow the Dancing Plague recipe (render.py on its branch): kick-envelope sidechain on
bass / chops / drones; per-track high-pass (28 Hz bass, 55-300 Hz elsewhere); flute presence lift;
short room + plate (15 ms pre-delay) for the band; DP master EQ (sub-heavy, lean low-mids, warm top);
side width above 160 Hz; glue compression 2:1; gentle tanh saturation; 4x-oversampled true-peak limiter.
"""
import os, sys, json, time, hashlib, pickle
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d

import song as SG
import dsp as D
import dp_engine as E
from dsp import SR

TARGET_LUFS = -14.0
CEIL_DBTP = -1.3
WAV = "PIED_PIPER_NEW_SOUNDTRACK.wav"
JSN = "PIED_PIPER_NEW_SOUNDTRACK_SYNC.json"

# gain dB, hp, lp, eq [(f, g, q)], comp, sends (room / plate / hall / dly), duck dB, width
MIX = {
    "flute":   dict(g=2.0, hp=260, lp=14000, eq=[(400, -1.5, 1.0), (1100, 1.0, 1.2), (2600, 1.5, 1.0), (9000, 1.0, 0.7)],
                    comp=(-22, 2.2, 0.004, 0.12), room=0.06, plate=0.20, hall=0.07, dly=0.10, duck=0, w=1.0),
    "flute8":  dict(g=-4.5, hp=700, lp=12000, eq=[(3500, -2.0, 1.0)], comp=(-24, 2.0, 0.005, 0.1),
                    room=0.0, plate=0.25, hall=0.12, dly=0.10, duck=0, w=1.0, haas=12),
    "flute_lo": dict(g=-1.0, hp=180, lp=9000, eq=[(1800, 1.5, 1.0)], comp=(-24, 2.0, 0.005, 0.1),
                    room=0.05, plate=0.2, hall=0.2, dly=0.05, duck=0, w=1.1),
    "pluck":   dict(g=0.0, hp=250, lp=13000, eq=[(700, -1.0, 1.0), (3200, 2.0, 0.9)], comp=(-22, 2.5, 0.002, 0.08),
                    room=0.10, plate=0.14, hall=0.05, dly=0.08, duck=-1, w=1.2),
    "lute":    dict(g=-3.5, hp=110, lp=8000, eq=[(250, -2.0, 1.0)], comp=(-22, 2.5, 0.003, 0.1),
                    room=0.10, plate=0.10, hall=0.0, dly=0.0, duck=-2, w=1.2),
    "gurdy":   dict(g=-1.5, hp=180, lp=7500, eq=[(1300, 2.0, 1.2), (3200, -2.0, 1.5)], comp=(-24, 2.5, 0.008, 0.12),
                    room=0.10, plate=0.12, hall=0.06, dly=0.0, duck=-1, w=1.0),
    "drone":   dict(g=-9.0, hp=90, lp=5000, eq=[(300, -2.0, 1.0), (750, 2.0, 1.4)], comp=(-26, 2.0, 0.02, 0.3),
                    room=0.10, plate=0.0, hall=0.12, dly=0.0, duck=-5, w=1.3),
    "chien":   dict(g=1.0, hp=300, lp=9000, eq=[(2400, 1.0, 1.0)], comp=(-22, 3.0, 0.002, 0.08),
                    room=0.12, plate=0.05, hall=0.0, dly=0.0, duck=-2, w=1.0),
    "fiddle":  dict(g=-1.5, hp=200, lp=9000, eq=[(1000, -1.5, 1.2), (2700, 1.0, 1.0)], comp=(-24, 2.5, 0.006, 0.12),
                    room=0.10, plate=0.16, hall=0.06, dly=0.0, duck=0, w=1.0),
    "fdesc":   dict(g=-6.0, hp=400, lp=9000, eq=[(2800, 1.0, 1.0)], comp=(-24, 2.0, 0.01, 0.2),
                    room=0.05, plate=0.2, hall=0.3, dly=0.0, duck=-2, w=1.4),
    "fsec":    dict(g=-4.0, hp=140, lp=8000, eq=[(350, -2.0, 1.0), (2600, 1.0, 1.0)], comp=(-26, 2.0, 0.01, 0.2),
                    room=0.08, plate=0.15, hall=0.25, dly=0.0, duck=-3, w=1.3),
    "chop":    dict(g=-2.5, hp=160, lp=9000, eq=[(300, -2.0, 1.0), (2800, 2.0, 1.0)], comp=(-22, 2.5, 0.002, 0.08),
                    room=0.12, plate=0.08, hall=0.0, dly=0.0, duck=-5, w=1.4),
    "bass":    dict(g=0.0, hp=28, lp=5000, eq=[(60, 1.0, 0.9), (250, -2.0, 1.0)], comp=(-18, 3.0, 0.003, 0.08),
                    room=0, plate=0, hall=0, dly=0, duck=-8, w=0.0),
    "growl":   dict(g=-1.0, hp=28, lp=3500, eq=[(250, -2.5, 1.0), (900, 1.5, 1.0)], comp=(-18, 3.0, 0.003, 0.08),
                    room=0, plate=0, hall=0, dly=0, duck=-12, w=0.0),
    "sub":     dict(g=-3.0, hp=25, lp=400, eq=[], comp=None, room=0, plate=0, hall=0, dly=0, duck=-8, w=0.0),
    "kick":    dict(g=-1.5, hp=28, lp=12000, eq=[(300, -3.0, 1.0), (3500, 1.5, 1.0)], comp=None,
                    room=0.02, plate=0, hall=0, dly=0, duck=0, w=0.0),
    "kick_ac": dict(g=-9.0, hp=45, lp=7000, eq=[(80, 1.0, 1.0), (400, -3.0, 1.0)], comp=(-20, 3.0, 0.002, 0.08),
                    room=0.10, plate=0, hall=0.03, dly=0, duck=0, w=0.6),
    "clap":    dict(g=-1.0, hp=250, lp=14000, eq=[(1200, 1.5, 1.0)], comp=(-20, 2.5, 0.002, 0.1),
                    room=0.22, plate=0.15, hall=0.0, dly=0, duck=0, w=1.3),
    "tabor":   dict(g=-3.0, hp=150, lp=12000, eq=[(220, 1.5, 1.2)], comp=(-20, 2.5, 0.002, 0.1),
                    room=0.2, plate=0.08, hall=0.0, dly=0, duck=0, w=1.0),
    "snare":   dict(g=-7.0, hp=150, lp=13000, eq=[(220, 2.0, 1.2), (5000, 1.5, 1.0)], comp=(-20, 3.0, 0.002, 0.1),
                    room=0.22, plate=0.1, hall=0.0, dly=0, duck=0, w=0.8),
    "riq":     dict(g=-1.0, hp=300, lp=15000, eq=[(620, 1.0, 1.5), (7000, 1.0, 0.8)], comp=(-22, 2.0, 0.002, 0.06),
                    room=0.12, plate=0.05, hall=0, dly=0, duck=-1, w=1.0),
    "tamb":    dict(g=-8.0, hp=900, lp=15000, eq=[], comp=(-24, 2.0, 0.002, 0.06),
                    room=0.12, plate=0, hall=0, dly=0, duck=-2, w=1.0),
    "shaker":  dict(g=-7.0, hp=1500, lp=15000, eq=[], comp=None, room=0.12, plate=0, hall=0, dly=0, duck=-2, w=1.2),
    "frame":   dict(g=-6.0, hp=55, lp=8000, eq=[(100, 1.5, 1.0), (400, -2.0, 1.0)], comp=(-22, 2.5, 0.003, 0.1),
                    room=0.18, plate=0, hall=0.04, dly=0, duck=-1, w=0.8),
    "wood":    dict(g=-6.0, hp=300, lp=14000, eq=[(1500, 1.0, 1.0)], comp=(-22, 2.5, 0.001, 0.06),
                    room=0.18, plate=0.05, hall=0.0, dly=0.0, duck=0, w=1.2),
    "darb":    dict(g=-6.0, hp=90, lp=14000, eq=[(300, -1.0, 1.0), (2500, 1.5, 1.0)], comp=(-22, 2.5, 0.002, 0.08),
                    room=0.15, plate=0, hall=0, dly=0, duck=-1, w=1.2),
    "toms":    dict(g=-3.0, hp=55, lp=10000, eq=[(110, 2.0, 1.0), (500, -2.0, 1.0), (3000, 1.5, 1.0)],
                    comp=(-20, 3.0, 0.002, 0.1), room=0.22, plate=0, hall=0.06, dly=0, duck=0, w=1.2),
    "big":     dict(g=-7.0, hp=30, lp=8000, eq=[(70, 2.0, 1.0), (400, -3.0, 1.0)], comp=(-20, 2.5, 0.004, 0.15),
                    room=0.12, plate=0, hall=0.12, dly=0, duck=0, w=1.0),
    "boom":    dict(g=-5.0, hp=28, lp=9000, eq=[], comp=None, room=0.05, plate=0, hall=0.15, dly=0, duck=0, w=1.0),
    "cym":     dict(g=-9.0, hp=2000, lp=15000, eq=[], comp=None, room=0.0, plate=0.1, hall=0.2, dly=0, duck=-2, w=1.4),
    "fx":      dict(g=-10.0, hp=200, lp=11000, eq=[], comp=None, room=0, plate=0, hall=0.4, dly=0, duck=0, w=1.3),
    "bells":   dict(g=-8.0, hp=200, lp=6500, eq=[], comp=None, room=0, plate=0, hall=0.8, dly=0, duck=-2, w=1.5),
}
NO_GAP = ("flute", "flute8", "flute_lo")

STEMS = {"drums": ["kick", "kick_ac", "clap", "tabor", "snare", "toms", "big", "boom"],
         "percussion": ["riq", "tamb", "shaker", "frame", "wood", "darb", "cym", "fx"],
         "bass": ["bass", "growl", "sub"],
         "flute": ["flute", "flute8", "flute_lo"],
         "plucked": ["pluck", "lute", "chop"],
         "gurdy_fiddle": ["gurdy", "drone", "chien", "fiddle", "fdesc", "fsec", "bells"]}


def chain(x, p):
    if p.get("hp"):
        x = D.hp(x, p["hp"])
    if p.get("lp"):
        x = D.lp(x, p["lp"])
    for f, g, q in p.get("eq", []):
        x = D.peq(x, f, g, q)
    if p.get("comp"):
        thr, ratio, att, rel = p["comp"]
        x = D.compress(x, thr, ratio, att, rel)
    if p.get("haas"):
        d = int(p["haas"] * SR / 1000); m = x.mean(axis=1)
        x = np.stack([m, np.concatenate([np.zeros(d), m])[:len(m)]], 1)
    if p.get("w", 1.0) != 1.0:
        x = D.width(x, p["w"])
    return x


def gaps_mask(n):
    g = np.ones(n)
    for t0, t1 in SG.GAPS:
        g[int(t0 * SR):int(t1 * SR)] = 0.0
    return uniform_filter1d(g, int(0.006 * SR))


def mix(T):
    t0 = time.time()
    ir_room = D.make_ir(0.8, predelay=0.006, damp_hi=7000, damp_lo=150, size=0.5, seed=21)
    ir_plate = D.make_ir(1.3, predelay=0.015, damp_hi=9500, damp_lo=250, er=False, size=0.3, seed=22, diffusion_ms=4)
    ir_hall = D.make_ir(2.8, predelay=0.03, damp_hi=5500, damp_lo=160, size=1.6, seed=23)
    kick_times = [t for t, v in SG.KICKS if v >= 0.6]
    gm = gaps_mask(SG.N)
    bus = {k: np.zeros((SG.N, 2)) for k in ("room", "plate", "hall", "dly")}
    out = {}
    for name, tr in T.items():
        p = MIX[name]; x = tr.buf
        if not np.any(x):
            continue
        x = chain(x, p) * D.db(p["g"])
        if p.get("duck"):
            x = D.duck(x, kick_times, p["duck"], att=0.002, hold=0.02, rel=0.13)
        if name not in NO_GAP:
            x = x * gm[:, None]
        for k in ("room", "plate", "hall", "dly"):
            if p.get(k):
                bus[k] += x * p[k]
        out[name] = x
    rooms = D.convolve_st(D.peq(D.hp(bus["room"], 150), 450, -2.0, 1.0), ir_room) * 0.5
    plates = D.convolve_st(D.peq(D.hp(bus["plate"], 300), 600, -2.5, 1.0), ir_plate) * 0.5
    dly = D.delay(D.hp(bus["dly"], 300), 3 * SG.S16, fb=0.35, mix=1.0, lpf=3800, hpf=400, n_rep=6) - bus["dly"]
    halls = D.convolve_st(D.peq(D.hp(bus["hall"] + dly * 0.3, 220), 500, -3.5, 0.9), ir_hall) * 0.4
    halls = D.duck(halls, kick_times, -3, rel=0.2)
    plates = D.duck(plates, kick_times, -2, rel=0.18)
    print(f"  mix {time.time() - t0:.1f}s")
    return out, dict(room=rooms, plate=plates, hall=halls, dly=dly * 0.5)


SECTION_GAIN = {"hook": -0.6, "rats": 0.0, "gate": 0.0, "stranger": -0.8, "spell": -0.5, "drop_1": 0.4,
                "river": 0.0, "still_water": -1.0, "celebration": 0.2, "betrayal": -0.6, "into_the_night": -0.8,
                "drop_2": 0.8, "climax": 1.0, "mountain": 0.6, "disappearance": -0.5}


def automate(x):
    g = np.zeros(len(x))
    for s in SG.SECTIONS:
        g[int(s["bar"] * SG.BAR * SR):] = SECTION_GAIN.get(s["name"], 0.0)
    g = uniform_filter1d(g, int(0.25 * SR))
    return x * D.db(g)[:, None]


def wrap_loop(x):
    y = x[:SG.NLOOP].copy(); tail = x[SG.NLOOP:]
    y[:len(tail)] += tail
    return y


def master_eq(x):
    """Dancing Plague master EQ, trimmed for a -14 LUFS master"""
    x = D.hp(x, 28)
    x = D.ls(x, 110, 2.0)
    x = D.peq(x, 36, -2.0, 1.0)
    x = D.peq(x, 85, 2.0, 1.0)
    x = D.peq(x, 190, 1.0, 0.9)
    x = D.peq(x, 330, -2.5, 0.8)
    x = D.peq(x, 650, -1.0, 1.0)
    x = D.peq(x, 1700, 1.5, 0.7)
    x = D.peq(x, 2500, 1.5, 0.6)
    x = D.hs(x, 4000, 1.2)
    x = D.hs(x, 11000, -1.0)
    return x


def stereo_width(x, w=1.3, fc=160):
    m = (x[:, 0] + x[:, 1]) / 2; s = (x[:, 0] - x[:, 1]) / 2
    s = D.hp(s, fc) * w + (s - D.hp(s, fc))
    return np.stack([m + s, m - s], 1)


def limiter(x, ceil_db=CEIL_DBTP, look=0.003, rel=0.09, os_=4):
    up = signal.resample_poly(x, os_, 1, axis=0)
    pk = np.abs(up).max(axis=1).reshape(-1, os_).max(axis=1)[:len(x)]
    pk = np.pad(pk, (0, len(x) - len(pk)), mode="edge")
    g = np.minimum(1.0, D.db(ceil_db) / np.maximum(pk, 1e-9))
    L = max(1, int(look * SR))
    g = minimum_filter1d(g, 2 * L + 1)
    g = D._smooth_gain(g, 0.0, np.exp(-1 / (rel * SR)))
    g = np.minimum(g, minimum_filter1d(g, 2 * L + 1))
    g = uniform_filter1d(g, L)
    return x * g[:, None], g


def master(x):
    x = master_eq(x)
    x = stereo_width(x)
    x = D.compress(x, -15, 2.0, 0.012, 0.15, knee=8)              # DP glue
    gain = 0.0
    for _ in range(8):
        y = x * D.db(gain)
        y = np.tanh(y * 1.15) / 1.15                               # DP-style gentle saturation
        y, g = limiter(y)
        lu = D.lufs(y)
        gain += TARGET_LUFS - lu
        if abs(TARGET_LUFS - lu) < 0.02:
            break
    tp = D.true_peak_db(y)
    if tp > CEIL_DBTP + 0.05:
        y *= D.db(CEIL_DBTP - tp)
    return y, D.lufs(y), D.true_peak_db(y), float(D.todb(g.min()))


def dither24(x):
    r = np.random.default_rng(7)
    return x + (r.random(x.shape) - r.random(x.shape)) / (2 ** 23)


def beat_energy(x):
    m = x.mean(axis=1); e = []
    for b in range(SG.NBARS * 4):
        a = int(b * SG.BEAT * SR); c = int((b + 1) * SG.BEAT * SR)
        e.append(np.sqrt(np.mean(m[a:c] ** 2)))
    e = D.todb(np.array(e))
    return np.clip((e - (e.max() - 15)) / 15, 0, 1)


def write_json(path, lu, tp, energy):
    fr = lambda t: int(round(t * 60))
    beats = [dict(index=b, time=round(b * SG.BEAT, 4), frame60=fr(b * SG.BEAT), bar=b // 4 + 1, beat=b % 4 + 1,
                  downbeat=(b % 4 == 0), energy=round(float(energy[b]), 3)) for b in range(SG.NBARS * 4)]
    secs = []
    for i, s in enumerate(SG.SECTIONS):
        end_bar = SG.SECTIONS[i + 1]["bar"] if i + 1 < len(SG.SECTIONS) else SG.NBARS
        secs.append(dict(name=s["name"], start=round(s["bar"] * SG.BAR, 4), end=round(end_bar * SG.BAR, 4),
                         start_bar=s["bar"] + 1, end_bar=end_bar, description=s["desc"]))
    harm = []
    for b in range(SG.NBARS):
        c = SG.HARM.get(b)
        if c is None:
            continue
        if isinstance(c, tuple):
            harm += [dict(bar=b + 1, time=round(b * SG.BAR, 4), chord=c[0]),
                     dict(bar=b + 1, time=round(b * SG.BAR + 2 * SG.BEAT, 4), chord=c[1])]
        else:
            harm.append(dict(bar=b + 1, time=round(b * SG.BAR, 4), chord=c.replace("Gmaj", "G")))
    gaps = [dict(start=round(a + 0.004, 4), end=round(b + 0.006, 4)) for a, b in SG.GAPS]
    data = dict(
        title="THE PIED PIPER OF HAMELIN -- new soundtrack", file=WAV, instrumental=True,
        bpm=SG.BPM, time_signature="4/4", swing="52 % on 16ths (odd 16ths late by 0.0044 s)",
        key="B minor (Phrygian bII = C, harmonic-minor V = F#); celebration in D major; betrayal in D minor",
        sample_rate=SR, bit_depth=24, channels=2, duration_seconds=round(SG.NLOOP / SR, 4),
        beat_seconds=round(SG.BEAT, 6), bar_seconds=round(SG.BAR, 6), sixteenth_seconds=round(SG.S16, 6),
        bars=SG.NBARS, first_beat=0.0, animation_fps=60,
        film_grid_note="Same 136 BPM / 37-bar grid as PIED_PIPER_FINAL_1080P60.mp4: every shot cut still sits on a "
                       "bar line. The two drops are at bar 12 (19.412 s, rat procession) and bar 24 (40.588 s, the "
                       "children).",
        drops=[dict(name="drop_1", time=round(11 * SG.BAR, 4), bar=12), dict(name="drop_2", time=round(23 * SG.BAR, 4), bar=24)],
        loop=dict(seamless=True, loop_start=0.0, loop_end=round(SG.NLOOP / SR, 4),
                  note="The reverb tail is folded onto the start; the last bar's F#5-G5 pickup lands on the first bar's A5."),
        loudness=dict(integrated_lufs=round(lu, 2), true_peak_dbtp=round(tp, 2)),
        sections=secs, harmony=harm, gaps=gaps,
        accents=sorted(SG.ACCENTS, key=lambda a: a["time"]),
        events={k: sorted(set(v)) for k, v in SG.EVENTS.items()},
        flute_notes=sorted(SG.FLUTE_NOTES, key=lambda d: d["time"]),
        beats=beats, downbeats=[round(b * SG.BAR, 4) for b in range(SG.NBARS)],
    )
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


def cached_arrange():
    h = hashlib.sha1()
    here = os.path.dirname(os.path.abspath(__file__))
    for f in ("song.py", "dp_engine.py"):
        h.update(open(os.path.join(here, f), "rb").read())
    for f in ("instruments.py", "dsp.py", "samples.py"):
        h.update(open(os.path.join(here, "..", "..", "follow_the_piper", "source", f), "rb").read())
    from samples import CACHE_DIR
    cp = os.path.join(CACHE_DIR, f"ppnew_{h.hexdigest()[:12]}.pkl")
    if os.path.exists(cp) and "--fresh" not in sys.argv:
        with open(cp, "rb") as f:
            st = pickle.load(f)
        SG.reset()
        for k, v in st["T"].items():
            SG.T[k].buf = v.astype(np.float64)
        for k in ("SECTIONS", "ACCENTS", "KICKS", "FLUTE_NOTES", "GAPS"):
            getattr(SG, k)[:] = st[k]
        SG.EVENTS.update(st["EVENTS"]); SG.HARM.update(st["HARM"])
        return SG.T
    T = SG.arrange()
    with open(cp, "wb") as f:
        pickle.dump(dict(T={k: v.buf.astype(np.float32) for k, v in T.items()}, SECTIONS=SG.SECTIONS,
                         ACCENTS=SG.ACCENTS, KICKS=SG.KICKS, FLUTE_NOTES=SG.FLUTE_NOTES, GAPS=SG.GAPS,
                         EVENTS=dict(SG.EVENTS), HARM=SG.HARM), f)
    return T


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    T = cached_arrange()
    print(f"arrange {time.time() - t0:.1f}s")
    dry, ret = mix(T)
    full = automate(sum(dry.values()) + sum(ret.values()))
    full = wrap_loop(full)
    y, lu, tp, gr = master(full)
    print(f"LUFS {lu:.2f}  TP {tp:.2f} dBTP  max limiter GR {gr:.2f} dB  len {len(y) / SR:.3f}s")
    sf.write(os.path.join(outdir, WAV), dither24(y), SR, subtype="PCM_24")
    write_json(os.path.join(outdir, JSN), lu, tp, beat_energy(y))
    if "--stems" in sys.argv:
        sd = os.path.join(outdir, "stems"); os.makedirs(sd, exist_ok=True)
        for st, names in STEMS.items():
            s = sum(dry[n] for n in names if n in dry)
            sf.write(os.path.join(sd, f"STEM_{st}.wav"), wrap_loop(s).astype(np.float32), SR, subtype="FLOAT")
    print(f"total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
