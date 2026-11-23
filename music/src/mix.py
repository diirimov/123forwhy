"""Mix + master. Usage: python3 mix.py OUT.wav"""
import sys, json
import numpy as np, soundfile as sf, pyloudnorm as pyln
import scipy.signal as ss
from dsp import *
import song
from song import N, BAR, S16, SPB, pos

T, KICKS = song.build()
rng = np.random.default_rng(7)

# active-RMS level targets (dBFS, pre-master)
LV = dict(kick=-11.5, sub=-13.0, bass=-16.0, clap=-21.0, frame=-25, stomp=-22, hat=-31, ohat=-29, tamb=-28,
          shaker=-32, doum=-21.5, tek=-24, wood=-25, zills=-31, crash=-31, impact=-21, fx=-27,
          lute=-19.0, nylon=-25, lutearp=-25, fiddle=-18.5, bow=-27, fiddle2=-23.5, recorder=-24.5,
          hurdy=-20.5, drone=-28, buzz=-27.5, stabs=-25, pad=-25)
if len(sys.argv) > 2:
    LV.update(json.loads(sys.argv[2]))

EQ = {
    'kick': [('hp', 28, .7), ('peak', 62, 1.2, 1.5), ('peak', 190, 1.2, -3.5), ('peak', 380, 1.5, -2.0), ('peak', 4000, 1.0, 1.5)],
    'sub': [('lp', 110, .7), ('hp', 28, .7)],
    'bass': [('peak', 140, 1.0, 1.5), ('peak', 650, 1.0, -2.0), ('peak', 1400, 1.2, 1.5)],
    'clap': [('hp', 220, .7), ('peak', 2500, 1, 1.5)],
    'frame': [('hp', 120, .7)],
    'stomp': [('hp', 45, .7), ('peak', 350, 1.5, -2)],
    'doum': [('hp', 55, .7)],
    'lute': [('hp', 95, .7), ('peak', 250, 1.2, -1.5), ('peak', 3200, 1.0, 2.5)],
    'nylon': [('hp', 150, .7), ('peak', 4000, 1.0, 2)],
    'lutearp': [('hp', 180, .7), ('peak', 3000, 1.0, 2)],
    'fiddle': [('hp', 190, .7), ('peak', 420, 1.4, -2.5), ('peak', 2700, 1.0, 2.0), ('hs', 9000, .7, 1.5)],
    'fiddle2': [('hp', 190, .7), ('peak', 420, 1.4, -2.5), ('peak', 2700, 1.0, 1.0)],
    'bow': [('hp', 250, .7)],
    'recorder': [('hp', 320, .7)],
    'hurdy': [('hp', 120, .7), ('peak', 1600, 1.0, 1.5)],
    'drone': [('hp', 110, .7)],
    'buzz': [('hp', 400, .7)],
    'stabs': [('hp', 200, .7)],
    'pad': [('hp', 150, .7)],
    'tamb': [('hp', 2500, .7)],
    'shaker': [('hp', 3000, .7)],
    'crash': [('hp', 2200, .7)],
    'wood': [('hp', 300, .7)],
    'zills': [('hp', 1800, .7)],
    'fx': [('hp', 150, .7)],
}
SC = dict(sub=0.92, bass=0.75, stabs=0.55, pad=0.6, drone=0.4, buzz=0.2, lutearp=0.25, hurdy=0.15, fiddle=0.12, fiddle2=0.15, recorder=0.12)
SEND_ROOM = dict(clap=0.28, frame=0.25, doum=0.18, tek=0.22, wood=0.3, stomp=0.3, tamb=0.12, hat=0.08, ohat=0.1, shaker=0.1)
SEND_HALL = dict(lute=0.22, nylon=0.2, fiddle=0.26, fiddle2=0.3, bow=0.2, recorder=0.35, hurdy=0.25, zills=0.45, stabs=0.18,
                 pad=0.3, lutearp=0.15, fx=0.35, buzz=0.12, crash=0.2, impact=0.15)
SEND_DLY = dict(lute=0.12, fiddle=0.12, recorder=0.18, hurdy=0.15, wood=0.12, lutearp=0.05)
WIDTH = dict(stabs=1.5, pad=1.6, drone=1.4, fiddle2=1.2, lutearp=1.2, crash=1.3, fx=1.3)
MONO = {'kick', 'sub', 'impact', 'doum'}

# ---------------------------------------------------------------- sidechain env
t = np.arange(N + song.TAIL)
sc = np.zeros(len(t))
L = int(0.16 * SR)
shape = (1 - np.arange(L) / L) ** 2.2
for k in KICKS:
    e = min(len(sc), k + L)
    sc[k:e] = np.maximum(sc[k:e], shape[:e - k])
sc = ss.lfilter([1 - 0.9], [1, -0.9], sc)  # ~0.2ms smoothing of the onset


def active_rms_db(x):
    m = x.mean(1)
    fr = int(0.05 * SR)
    nf = len(m) // fr
    p = (m[:nf * fr].reshape(nf, fr) ** 2).mean(1)
    if p.max() <= 0:
        return -200
    pdb = 10 * np.log10(p + 1e-20)
    act = p[pdb > pdb.max() - 30]
    return 10 * np.log10(act.mean())


def proc(name, x):
    for f in EQ.get(name, []):
        x = biquad(x, f[0], f[1], f[2], f[3] if len(f) > 3 else 0.0)
    if name in MONO:
        m = x.mean(1); x = np.stack([m, m], 1)
    if name in WIDTH:
        x = widen(x, WIDTH[name])
    return x


stems = {}
for name, x in T.items():
    x = proc(name, x)
    g = 10 ** ((LV.get(name, -30) - active_rms_db(x)) / 20)
    x = x * g
    if name in SC:
        x = x * (1 - SC[name] * sc)[:, None]
    stems[name] = x

# ---------------------------------------------------------------- busses
room_ir = make_ir(rng, 0.55, 1.0, 0.006, True, 0.45)
hall_ir = make_ir(rng, 1.7, 3.0, 0.022, True, 0.5)
room_in = sum(stems[k] * v for k, v in SEND_ROOM.items() if k in stems)
hall_in = sum(stems[k] * v for k, v in SEND_HALL.items() if k in stems)
dly_in = sum(stems[k] * v for k, v in SEND_DLY.items() if k in stems)
room = convolve(room_in, room_ir) * 0.5
hall = convolve(biquad(hall_in, 'hp', 250), hall_ir) * 0.5
hall = hall * (1 - 0.35 * sc)[:, None]
dly = pingpong(dly_in, 3 * S16 / SR, 0.38, 4200, 400)
dly = convolve(dly, room_ir) * 0.3 + dly * 0.7

# pre-drop gaps: mute dry instruments, keep reverb/fx tails breathing
dry_names = [k for k in stems if k not in ('fx', 'crash', 'impact')]
gate = np.ones(len(t))
for (b0, s0), (b1, s1) in [((8, 14), (9, 0)), ((24, 14), (25, 0)), ((40, 12), (41, 0))]:
    a, b = pos(b0, s0), pos(b1, s1)
    f = int(0.006 * SR)
    gate[a:b] = 0.0
    gate[a:a + f] = np.linspace(1, 0, f)
for k in dry_names:
    stems[k] = stems[k] * gate[:, None]

mix = sum(stems.values()) + room + hall + dly * 0.9

# section energy automation (dB per bar, pre-limiter)
SEC_DB = {}
for b in range(1, 49):
    if b <= 4: v = -2.5
    elif b <= 8: v = -2.5 + 0.35 * (b - 4)
    elif b <= 16: v = 0.0
    elif b <= 22: v = -1.2
    elif b <= 24: v = -0.6
    elif b <= 32: v = 0.9
    elif b <= 36: v = -1.6
    elif b <= 40: v = -1.6 + 0.4 * (b - 36)
    else: v = 1.2
    SEC_DB[b] = v
auto = np.ones(len(mix))
for b, v in SEC_DB.items():
    auto[(b - 1) * BAR:b * BAR] = 10 ** (v / 20)
auto[N:] = auto[N - 1]
auto = ss.filtfilt(*ss.butter(1, 20 / (SR / 2)), auto)
mix = mix * auto[:, None]

# ---------------------------------------------------------------- master
mix = biquad(mix, 'hp', 24, 0.7)
mix = biquad(mix, 'hs', 11000, 0.7, 1.5)
mix = biquad(mix, 'peak', 280, 0.9, -1.0)
# glue compressor
det = np.abs(biquad(mix.mean(1), 'hp', 120))
gc = env_follow_gain(det, -14.0 + 20 * np.log10(np.abs(mix).max() + 1e-9) * 0 , 2.0, np.exp(-1 / (0.012 * SR)), np.exp(-1 / (0.18 * SR)))
print('glue GR dB: median %.2f max %.2f' % (np.median(20*np.log10(gc)), (20*np.log10(gc)).min()))
mix = mix * gc[:, None]
mix = mix[:N]

meter = pyln.Meter(SR)
TARGET = -9.3
lu = meter.integrated_loudness(mix)
mix = mix * 10 ** ((TARGET - lu) / 20)
# soft clip the very top, then lookahead limiter
mix = np.where(np.abs(mix) > 0.8, np.sign(mix) * (0.8 + 0.2 * np.tanh((np.abs(mix) - 0.8) / 0.2)), mix)
ceil = 10 ** (-1.2 / 20)
for _ in range(3):
    upd = np.abs(ss.resample_poly(mix, 4, 1, axis=0)).max(1)
    peak = np.maximum(np.abs(mix).max(1), upd[:len(mix) * 4].reshape(len(mix), 4).max(1))
    greq = np.minimum(1.0, ceil / (peak + 1e-12))
    g = limiter_gain(greq, int(0.0015 * SR), np.exp(-1 / (0.06 * SR)))
    print('limiter GR dB: median %.2f p05 %.2f' % (np.median(20*np.log10(g)), np.percentile(20*np.log10(g), 5)))
    mix = mix * g[:, None]
    up = ss.resample_poly(mix, 4, 1, axis=0)
    tp = 20 * np.log10(np.abs(up).max())
    if tp <= -1.0:
        break
    mix *= 10 ** ((-1.05 - tp) / 20)
# final ring-out: exact end on last frame
fo = int(0.035 * SR)
mix[-fo:] *= (np.cos(np.linspace(0, np.pi / 2, fo)) ** 2)[:, None]
# silence safety at sample 0 (start hits immediately)
mix[:32] *= np.linspace(0, 1, 32)[:, None]

out = sys.argv[1] if len(sys.argv) > 1 else 'out.wav'
dith = (rng.uniform(-0.5, 0.5, mix.shape) + rng.uniform(-0.5, 0.5, mix.shape)) / (2 ** 23)
sf.write(out, np.clip(mix + dith, -1, 1), SR, subtype='PCM_24')
up = ss.resample_poly(mix, 4, 1, axis=0)
print('samples', len(mix), 'dur', len(mix) / SR)
print('LUFS-I %.2f  TP %.2f dBTP  peak %.2f' % (meter.integrated_loudness(mix), 20 * np.log10(np.abs(up).max()), 20 * np.log10(np.abs(mix).max())))
np.save(out + '.stemlv.npy', {k: active_rms_db(v[:N]) for k, v in stems.items()})
