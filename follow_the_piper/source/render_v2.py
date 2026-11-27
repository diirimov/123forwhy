"""
FOLLOW THE PIPER V2 -- mix, master, exports (100 % instrumental re-arrangement of V1).

    python3 render_v2.py <outdir> [--stems] [--fresh]

Writes FOLLOW_THE_PIPER_V2.wav (48 kHz / 24-bit, -14 LUFS, <= -1 dBTP) and
FOLLOW_THE_PIPER_V2_SYNC.json. V1 (render.py / song.py) is untouched.
"""
import os, sys, json, time
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.ndimage import minimum_filter1d, uniform_filter1d
import dsp as D
from dsp import SR
import song_v2 as SG

TARGET_LUFS = -14.0
CEIL_DBTP = -1.25          # limiter ceiling (true peak, 4x oversampled); leaves margin under -1.0

# per-track mix: gain dB, hp, lp, eq [(f, g, q)], comp (thr, ratio, att, rel) or None,
#                sends room / plate / hall / delay, duck dB (kick sidechain), width
MIX = {
    "flute":    dict(g=3.0, hp=240, lp=14000, eq=[(380, -1.5, 1.0), (650, -1.5, 1.2), (2900, 2.5, 0.8), (9000, 1.0, 0.7)],
                     comp=(-22, 2.2, 0.004, 0.12), room=0.06, plate=0.20, hall=0.08, dly=0.10, duck=0, w=1.0),
    "flute8":   dict(g=-3.0, hp=600, lp=12000, eq=[(3500, -2.0, 1.0)], comp=(-24, 2.0, 0.005, 0.1),
                     room=0.0, plate=0.25, hall=0.12, dly=0.10, duck=0, w=1.0, haas=13),
    "flute_lo": dict(g=-3.0, hp=180, lp=9000, eq=[(1800, 1.5, 1.0)], comp=(-24, 2.0, 0.005, 0.1),
                     room=0.05, plate=0.22, hall=0.22, dly=0.05, duck=0, w=1.2),
    "ghost":    dict(g=-8.0, hp=900, lp=11000, eq=[], comp=None, room=0, plate=0.0, hall=1.0, dly=0.5,
                     duck=0, w=1.8, shimmer=12, dry=0.0),
    "gurdy":    dict(g=-3.0, hp=180, lp=7500, eq=[(1300, 2.0, 1.2), (3200, -2.0, 1.5)], comp=(-24, 2.5, 0.01, 0.15),
                     room=0.10, plate=0.12, hall=0.08, dly=0.0, duck=-2, w=1.0),
    "drone":    dict(g=-8.0, hp=70, lp=5000, eq=[(300, -2.0, 1.0), (1200, 1.0, 1.0)], comp=(-26, 2.0, 0.02, 0.3),
                     room=0.10, plate=0.0, hall=0.12, dly=0.0, duck=-4, w=1.3),
    "chien":    dict(g=4.0, hp=300, lp=9000, eq=[(2400, 1.0, 1.0)], comp=(-22, 3.0, 0.002, 0.08),
                     room=0.12, plate=0.05, hall=0.0, dly=0.0, duck=-1, w=1.0),
    "strings":  dict(g=-1.5, hp=300, lp=12000, eq=[(800, -1.5, 1.0), (4000, 1.5, 0.8)], comp=(-22, 2.5, 0.003, 0.1),
                     room=0.10, plate=0.15, hall=0.0, dly=0.0, duck=-3, w=1.3),
    "bowpad":   dict(g=-15.0, hp=400, lp=10000, eq=[], comp=None, room=0.0, plate=0.2, hall=0.35, dly=0.0,
                     duck=-2, w=1.6),
    "pluck":    dict(g=-2.0, hp=120, lp=11000, eq=[(250, -2.0, 1.0), (3000, 1.5, 0.9)], comp=(-22, 2.5, 0.003, 0.1),
                     room=0.10, plate=0.12, hall=0.05, dly=0.0, duck=-2, w=1.2),
    "bass":     dict(g=-3.0, hp=28, lp=4500, lp4=True, eq=[(60, 1.5, 0.9), (250, -2.0, 1.0)], comp=(-18, 3.0, 0.003, 0.08),
                     room=0, plate=0, hall=0, dly=0, duck=-10, w=0.0),
    "kick":     dict(g=-6.0, hp=28, lp=12000, eq=[(55, 1.5, 1.0), (300, -3.0, 1.0), (3000, 2.0, 1.0)],
                     comp=None, room=0.03, plate=0, hall=0, dly=0, duck=0, w=0.0),
    "stomp":    dict(g=-2.0, hp=40, lp=9000, eq=[(80, 2.0, 1.0), (450, -2.0, 1.0), (1100, 2.5, 1.0)], comp=(-20, 3.0, 0.002, 0.08),
                     room=0.22, plate=0, hall=0.04, dly=0, duck=-1, w=1.0),
    "clap":     dict(g=0.0, hp=250, lp=14000, eq=[(1200, 1.5, 1.0)], comp=(-20, 2.5, 0.002, 0.1),
                     room=0.25, plate=0.15, hall=0.0, dly=0, duck=0, w=1.4),
    "snare":    dict(g=-5.0, hp=150, lp=13000, eq=[(220, 2.0, 1.2), (5000, 1.5, 1.0)], comp=(-20, 3.0, 0.002, 0.1),
                     room=0.22, plate=0.1, hall=0.0, dly=0, duck=0, w=0.8),
    "tamb":     dict(g=-6.0, hp=900, lp=15000, eq=[(7000, 1.0, 0.8)], comp=(-24, 2.0, 0.002, 0.06),
                     room=0.12, plate=0, hall=0, dly=0, duck=-2, w=1.0),
    "shaker":   dict(g=-9.0, hp=1200, lp=15000, eq=[], comp=None, room=0.12, plate=0, hall=0, dly=0, duck=-2, w=1.0),
    "darb":     dict(g=-5.0, hp=90, lp=14000, eq=[(300, -1.0, 1.0), (2500, 1.5, 1.0)], comp=(-22, 2.5, 0.002, 0.08),
                     room=0.15, plate=0, hall=0, dly=0, duck=-1, w=1.2),
    "frame":    dict(g=-8.0, hp=45, lp=8000, eq=[(100, 2.0, 1.0)], comp=(-22, 2.5, 0.003, 0.1),
                     room=0.18, plate=0, hall=0.05, dly=0, duck=0, w=0.8),
    "boom":     dict(g=-8.0, hp=30, lp=9000, eq=[], comp=None, room=0.1, plate=0, hall=0.18, dly=0, duck=0, w=1.0),
    "bells":    dict(g=-7.0, hp=200, lp=6500, eq=[(2500, -2.0, 1.0)], comp=None, room=0, plate=0, hall=0.85,
                     dly=0.0, duck=-2, w=1.6, dry=0.45),
    "fiddle":   dict(g=-1.0, hp=200, lp=9000, eq=[(1000, -1.5, 1.2), (2700, 1.0, 1.0)], comp=(-24, 2.5, 0.006, 0.12),
                     room=0.10, plate=0.18, hall=0.06, dly=0.0, duck=0, w=1.0),
    "fiddle_lo": dict(g=-3.0, hp=120, lp=7000, eq=[(400, -1.5, 1.0)], comp=(-24, 2.5, 0.006, 0.12),
                     room=0.10, plate=0.15, hall=0.12, dly=0.0, duck=-1, w=1.0),
    "fsec":     dict(g=-5.0, hp=140, lp=8000, eq=[(350, -2.0, 1.0), (2600, 1.0, 1.0)], comp=(-26, 2.0, 0.01, 0.2),
                     room=0.08, plate=0.15, hall=0.30, dly=0.0, duck=-3, w=1.3),
    "ostinato": dict(g=-5.0, hp=500, lp=12000, eq=[(3500, 1.5, 1.0)], comp=(-24, 2.5, 0.002, 0.08),
                     room=0.10, plate=0.10, hall=0.10, dly=0.12, duck=-2, w=1.4),
    "pizz":     dict(g=-5.0, hp=400, lp=11000, eq=[], comp=None, room=0.05, plate=0.15, hall=0.35, dly=0.25,
                     duck=0, w=1.2),
    "sub":      dict(g=-7.0, hp=25, lp=200, eq=[], comp=None, room=0, plate=0, hall=0, dly=0, duck=-14, w=0.0),
    "bigdrum":  dict(g=-3.0, hp=30, lp=8000, eq=[(70, 2.0, 1.0), (400, -3.0, 1.0)], comp=(-20, 2.5, 0.004, 0.15),
                     room=0.12, plate=0, hall=0.12, dly=0, duck=0, w=1.0),
    "toms":     dict(g=-2.0, hp=55, lp=10000, eq=[(110, 2.0, 1.0), (500, -2.0, 1.0), (3000, 1.5, 1.0)],
                     comp=(-20, 3.0, 0.002, 0.1), room=0.22, plate=0, hall=0.06, dly=0, duck=0, w=1.2),
    "wood":     dict(g=-4.0, hp=300, lp=14000, eq=[(1500, 1.0, 1.0)], comp=(-22, 2.5, 0.001, 0.06),
                     room=0.18, plate=0.05, hall=0.0, dly=0.0, duck=0, w=1.2),
    "cajon":    dict(g=-5.0, hp=60, lp=12000, eq=[(2500, 1.5, 1.0)], comp=(-22, 2.5, 0.002, 0.08),
                     room=0.15, plate=0, hall=0, dly=0, duck=0, w=1.0),
    "fx":       dict(g=-10.0, hp=80, lp=9000, eq=[], comp=None, room=0, plate=0, hall=0.5, dly=0, duck=0, w=1.2),
}

STEMS = {"drums": ["kick", "bigdrum", "toms", "stomp", "clap", "snare", "boom"],
         "percussion": ["tamb", "shaker", "darb", "frame", "wood", "cajon"],
         "bass": ["bass", "sub"],
         "lead_flute": ["flute", "flute8", "flute_lo", "ghost"],
         "fiddles": ["fiddle", "fiddle_lo", "fsec"],
         "strings_gurdy": ["gurdy", "drone", "chien", "strings", "ostinato", "pizz", "bowpad", "pluck"],
         "bells_fx": ["bells", "fx"]}


def chain(x, p):
    if p.get("hp"):
        x = D.hp(x, p["hp"])
    if p.get("lp"):
        x = D.lp4(x, p["lp"]) if p.get("lp4") else D.lp(x, p["lp"])
    for f, g, q in p.get("eq", []):
        x = D.peq(x, f, g, q)
    if p.get("comp"):
        thr, ratio, att, rel = p["comp"]
        x = D.compress(x, thr, ratio, att, rel)
    if p.get("haas"):
        d = int(p["haas"] * SR / 1000)
        m = x.mean(axis=1)
        x = np.stack([m, np.concatenate([np.zeros(d), m])[:len(m)]], 1)
    if p.get("w", 1.0) != 1.0:
        x = D.width(x, p["w"])
    return x


def shimmer(x, semis):
    import pedalboard as pb
    board = pb.Pedalboard([pb.PitchShift(semitones=semis)])
    y = board(x.T.astype(np.float32), SR).T.astype(np.float64)
    return y[:len(x)]


def apply_gaps(x):
    if not SG.GAPS:
        return x
    g = np.ones(len(x))
    for t0, t1 in SG.GAPS:
        a, b = int(t0 * SR), int(t1 * SR)
        g[a:b] = 0.0
    g = uniform_filter1d(g, int(0.006 * SR))         # 6 ms edges: clean cut-off, no click
    return x * g[:, None]


def mix(T, kicks):
    t0 = time.time()
    ir_room = D.make_ir(0.75, predelay=0.006, damp_hi=7000, damp_lo=150, size=0.5, seed=11)
    ir_plate = D.make_ir(1.7, predelay=0.014, damp_hi=9500, damp_lo=250, er=False, size=0.3, seed=12,
                         diffusion_ms=4)
    ir_hall = D.make_ir(3.4, predelay=0.035, damp_hi=5200, damp_lo=160, size=1.8, seed=13)
    kick_times = [t for t, v in kicks if v >= 0.6]
    bus = {k: np.zeros((SG.N, 2)) for k in ("room", "plate", "hall", "dly")}
    out = {}
    for name, tr in T.items():
        p = MIX[name]
        x = tr.buf
        if not np.any(x):
            continue
        x = chain(x, p) * D.db(p["g"])
        if p.get("shimmer"):
            x = shimmer(x, p["shimmer"])
        if p.get("duck"):
            x = D.duck(x, kick_times, p["duck"], att=0.002, hold=0.02, rel=0.13)
        if name not in ("flute", "ghost", "flute_lo"):
            x = apply_gaps(x)
        dry = x * p.get("dry", 1.0)
        for k, key in (("room", "room"), ("plate", "plate"), ("hall", "hall"), ("dly", "dly")):
            if p.get(key):
                bus[k] += x * p[key]
        out[name] = dry
    # returns
    rooms = D.convolve_st(D.peq(D.hp(bus["room"], 150), 450, -2.0, 1.0), ir_room) * 0.55
    plates = D.convolve_st(D.peq(D.hp(bus["plate"], 300), 600, -2.5, 1.0), ir_plate) * 0.5
    dly = D.delay(D.hp(bus["dly"], 300), 3 * SG.S16, fb=0.38, mix=1.0, lpf=3800, hpf=400, n_rep=7) - bus["dly"]
    halls = D.convolve_st(D.peq(D.peq(D.hp(bus["hall"] + dly * 0.4, 220), 500, -3.5, 0.9), 3000, 1.5, 1.0), ir_hall) * 0.42
    halls = D.duck(halls, kick_times, -3, rel=0.2)
    plates = D.duck(plates, kick_times, -2, rel=0.18)
    returns = dict(room=rooms, plate=plates, hall=halls, dly=dly * 0.6)
    print(f"  mix {time.time() - t0:.1f}s")
    return out, returns


SECTION_GAIN = {"intro_hook": 1.0, "rats_awaken": 0.0, "first_drop": -0.7, "betrayal": -0.6, "piper_returns": -1.6,
                "final_drop": 0.4, "disappearance": 0.0}


def automate(x):
    """gentle section-level bus automation (shapes the energy arc; 0.4 s ramps)"""
    g = np.zeros(len(x))
    for s in SG.SECTIONS:
        a = int(s["bar"] * SG.BAR * SR)
        g[a:] = SECTION_GAIN.get(s["name"], 0.0)
    g = uniform_filter1d(g, int(0.4 * SR))
    return x * D.db(g)[:, None]


def wrap_loop(x):
    """fold everything after the loop point back onto the start (seamless loop)"""
    y = x[:SG.NLOOP].copy()
    tail = x[SG.NLOOP:]
    y[:len(tail)] += tail
    return y


def master_eq(x):
    x = D.hp(x, 24)
    x = D.peq(x, 52, 1.0, 0.9)
    x = D.peq(x, 320, -1.5, 0.8)
    x = D.peq(x, 3200, 1.0, 0.7)
    x = D.hs(x, 10000, 0.8)
    return x


def glue(x):
    return D.compress(x, -16, 1.8, 0.012, 0.15, knee=8)


def limiter(x, ceil_db=CEIL_DBTP, look=0.003, rel=0.09, os=4):
    up = signal.resample_poly(x, os, 1, axis=0)
    pk = np.abs(up).max(axis=1).reshape(-1, os).max(axis=1)[:len(x)]
    pk = np.pad(pk, (0, len(x) - len(pk)), mode="edge")
    c = D.db(ceil_db)
    g = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    L = max(1, int(look * SR))
    g = minimum_filter1d(g, 2 * L + 1)
    g = D._smooth_gain(g, 0.0, np.exp(-1 / (rel * SR)))
    g = np.minimum(g, minimum_filter1d(g, 2 * L + 1))
    g = uniform_filter1d(g, L)
    return x * g[:, None], g


def master(x):
    x = master_eq(x)
    x = glue(x)
    gain = 0.0
    for it in range(6):
        y = D.softclip(x * D.db(gain), 1.05) if False else x * D.db(gain)
        y, g = limiter(y)
        lu = D.lufs(y)
        gain += TARGET_LUFS - lu
        if abs(TARGET_LUFS - lu) < 0.02:
            break
    grdb = D.todb(g)
    hot = np.where(grdb < -1.0)[0]
    if len(hot):
        secs = np.unique((hot / SR).round(1))
        print(f"  limiter > 1 dB at {len(secs)} moments, e.g. {secs[:12].tolist()}")
    tp = D.true_peak_db(y)
    if tp > CEIL_DBTP + 0.05:
        y *= D.db(CEIL_DBTP - tp)
    return y, D.lufs(y), D.true_peak_db(y), float(D.todb(g.min()))


def dither24(x):
    lsb = 1.0 / (2 ** 23)
    r = np.random.default_rng(7)
    return x + (r.random(x.shape) - r.random(x.shape)) * lsb


def write_json(path, lu, tp, energy):
    beats = []
    for b in range(SG.NBARS * 4):
        t = b * SG.BEAT
        beats.append(dict(index=b, time=round(t, 4), bar=b // 4 + 1, beat=b % 4 + 1, downbeat=(b % 4 == 0),
                          energy=round(float(energy[b]), 3)))
    secs = []
    for i, s in enumerate(SG.SECTIONS):
        end_bar = SG.SECTIONS[i + 1]["bar"] if i + 1 < len(SG.SECTIONS) else SG.NBARS
        secs.append(dict(name=s["name"], start=round(s["bar"] * SG.BAR, 4), end=round(end_bar * SG.BAR, 4),
                         start_bar=s["bar"] + 1, end_bar=end_bar, description=s["desc"]))
    ev = {k: sorted(round(float(t), 4) for t in v) for k, v in SG.EVENTS.items()}
    data = dict(
        title="FOLLOW THE PIPER (V2)", version=2, instrumental=True,
        file="FOLLOW_THE_PIPER_V2.wav",
        bpm=SG.BPM, time_signature="4/4", key="A minor (harmonic minor, tritone D# colour)",
        sample_rate=SR, bit_depth=24, channels=2,
        duration_seconds=round(SG.NLOOP / SR, 4),
        beat_seconds=round(SG.BEAT, 6), bar_seconds=round(SG.BAR, 6), sixteenth_seconds=round(SG.S16, 6),
        bars=SG.NBARS, first_beat=0.0,
        loop=dict(seamless=True, loop_start=0.0, loop_end=round(SG.NLOOP / SR, 4),
                  note="Exactly 37 bars. The ending's reverb tail is folded onto the start, and the last bar's "
                       "G#4 pickup resolves into the opening A4, so the file loops sample-accurately."),
        narration_window=dict(start=0.0, end=round(2 * SG.BAR, 4),
                              note="Bars 1-2: the flute leads over a low buzzing drone, a deep drum + bell at 0.000 s and "
                            "a soft wooden slit-drum heartbeat. The flute is silent at 1.78-2.42 s and 3.10-3.53 s "
                            "(the hook's written pause); only light claves (1.99, 2.10 s), slit drum and the giggle "
                            "echo sit there."),
        loudness=dict(integrated_lufs=round(lu, 2), true_peak_dbtp=round(tp, 2)),
        sections=secs,
        accents=sorted(SG.ACCENTS, key=lambda a: a["time"]),
        events=ev,
        flute_notes=sorted(SG.FLUTE_NOTES, key=lambda d: d["time"]),
        beats=beats,
        downbeats=[round(b * SG.BAR, 4) for b in range(SG.NBARS)],
    )
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


def beat_energy(x):
    m = x.mean(axis=1)
    e = []
    for b in range(SG.NBARS * 4):
        a = int(b * SG.BEAT * SR); c = int((b + 1) * SG.BEAT * SR)
        e.append(np.sqrt(np.mean(m[a:c] ** 2)))
    e = np.array(e)
    e = D.todb(e)
    e = np.clip((e - (e.max() - 15)) / 15, 0, 1)      # 0 = 15 dB below the loudest beat, 1 = loudest
    return e


def cached_arrange():
    """re-use the arranged (pre-mix) tracks when the score/instrument code is unchanged"""
    import hashlib, pickle
    here = os.path.dirname(os.path.abspath(__file__))
    h = hashlib.sha1()
    for f in ("song_v2.py", "instruments.py", "dsp.py", "samples.py"):
        h.update(open(os.path.join(here, f), "rb").read())
    from samples import CACHE_DIR
    cp = os.path.join(CACHE_DIR, f"arrv2_{h.hexdigest()[:12]}.pkl")
    if os.path.exists(cp) and "--fresh" not in sys.argv:
        with open(cp, "rb") as f:
            st = pickle.load(f)
        SG.reset()
        for k, v in st["T"].items():
            SG.T[k].buf = v
        SG.SECTIONS[:] = st["S"]; SG.ACCENTS[:] = st["A"]; SG.KICKS[:] = st["K"]
        SG.EVENTS.update(st["E"]); SG.FLUTE_NOTES[:] = st["F"]; SG.GAPS[:] = st["G"]
        return SG.T
    T = SG.arrange()
    with open(cp, "wb") as f:
        pickle.dump(dict(T={k: v.buf.astype(np.float32) for k, v in T.items()}, S=SG.SECTIONS, A=SG.ACCENTS,
                         K=SG.KICKS, E=dict(SG.EVENTS), F=SG.FLUTE_NOTES, G=SG.GAPS), f)
    return T


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    stems = "--stems" in sys.argv
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    T = cached_arrange()
    print(f"arrange {time.time() - t0:.1f}s")
    dry, ret = mix(T, SG.KICKS)
    full = sum(dry.values()) + sum(ret.values())
    full = automate(full)
    full = wrap_loop(full)
    y, lu, tp, gr = master(full)
    print(f"LUFS {lu:.2f}  TP {tp:.2f} dBTP  max limiter GR {gr:.2f} dB  len {len(y) / SR:.3f}s")
    sf.write(os.path.join(outdir, "FOLLOW_THE_PIPER_V2.wav"), dither24(y), SR, subtype="PCM_24")
    write_json(os.path.join(outdir, "FOLLOW_THE_PIPER_V2_SYNC.json"), lu, tp, beat_energy(y))
    if stems:
        sd = os.path.join(outdir, "stems"); os.makedirs(sd, exist_ok=True)
        pre = D.db(0)
        # stems: dry tracks + their share of returns is not separable; export dry stems + a returns stem
        for st, names in STEMS.items():
            s = sum(dry[n] for n in names if n in dry)
            sf.write(os.path.join(sd, f"PIPER_STEM_{st}.wav"), wrap_loop(s), SR, subtype="PCM_24")
        sf.write(os.path.join(sd, "PIPER_STEM_reverbs.wav"), wrap_loop(sum(ret.values())), SR, subtype="PCM_24")
    print(f"total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
