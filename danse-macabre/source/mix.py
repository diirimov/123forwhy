import numpy as np, soundfile as sf, json, sys
import pyloudnorm as pyln
from scipy.signal import resample_poly
from pedalboard import Pedalboard, Compressor, PeakFilter, LowShelfFilter, HighShelfFilter, HighpassFilter, \
    LowpassFilter, Chorus, Delay, Limiter, Gain
import synth as S
from synth import SR
from compose import N, NT, T, STEP

st = dict(np.load('stems.npz'))
meta = json.load(open('meta.json'))

# ---------------- sidechain envelope from kick hits
duck = np.zeros(NT)
L = int(0.30 * SR)
tt = np.arange(L) / SR
shape = np.where(tt < 0.004, tt / 0.004, np.exp(-(tt - 0.004) / 0.075))
for t in meta['kick_times']:
    i = int(t * SR)
    j = min(NT, i + L)
    duck[i:j] = np.maximum(duck[i:j], shape[:j - i])


def sc(x, depth):
    return x * (1 - depth * duck)[:, None]


def fx(x, board):
    return board(x.T.astype(np.float32), SR).T.astype(np.float64)


def db(g):
    return 10 ** (g / 20)


# ---------------- per-stem processing & levels (dB)
G = dict(fiddle=-3.0, fiddle2=-9.0, viola=-12.0, harpsi=-8.0, drone=-17.0, organ=-15.0, strings=-14.0,
         winds=-12.0, sub=-7.5, bassmid=-12.0, kick=-4.0, snare=-10.0, hats=-14.5, perc=-7.0, bells=-12.0, fx=-14.0)
if len(sys.argv) > 1:
    G.update(json.load(open(sys.argv[1])))

P = {}
P['fiddle'] = fx(st['fiddle'], Pedalboard([HighpassFilter(200), PeakFilter(450, -2.0, 1.0), PeakFilter(2900, 1.5, 1.2),
                                           PeakFilter(5200, -1.0, 2.0), HighShelfFilter(9000, 2.5),
                                           Compressor(-20, 2.5, 6, 90)]))
P['fiddle2'] = fx(st['fiddle2'], Pedalboard([HighpassFilter(250), PeakFilter(5000, -3, 1.5), Compressor(-20, 2, 8, 100)]))
P['viola'] = fx(st['viola'], Pedalboard([HighpassFilter(140), PeakFilter(300, -2, 1), PeakFilter(4000, -3, 1),
                                         Compressor(-20, 2, 8, 100)]))
P['harpsi'] = fx(st['harpsi'], Pedalboard([HighpassFilter(160), PeakFilter(3200, -1.5, 1), HighShelfFilter(9000, 1),
                                           Compressor(-22, 2.5, 3, 80)]))
P['drone'] = sc(fx(st['drone'], Pedalboard([HighpassFilter(110), PeakFilter(250, -3, 1), LowpassFilter(6000)])), .45)
P['organ'] = sc(fx(st['organ'], Pedalboard([HighpassFilter(120), PeakFilter(300, -3, 0.8), Chorus(0.4, 0.15, 7, 0.0, 0.3)])), .5)
P['strings'] = sc(fx(st['strings'], Pedalboard([HighpassFilter(160), PeakFilter(2500, 1, 1), LowpassFilter(9000)])), .4)
P['winds'] = fx(st['winds'], Pedalboard([HighpassFilter(300), PeakFilter(3000, -1, 1), Compressor(-18, 2, 5, 80)]))
P['sub'] = sc(st['sub'], .9)
P['bassmid'] = sc(fx(st['bassmid'], Pedalboard([HighpassFilter(100), PeakFilter(800, 2, 1), PeakFilter(250, -2, 1),
                                                LowpassFilter(4500), Compressor(-18, 3, 3, 60)])), .85)
P['kick'] = fx(st['kick'], Pedalboard([HighpassFilter(28), PeakFilter(55, 2, 1.2), PeakFilter(350, -4, 1.2),
                                       PeakFilter(3500, 2, 1.0)]))
P['snare'] = fx(st['snare'], Pedalboard([HighpassFilter(140), PeakFilter(220, 2, 1), Compressor(-18, 4, 2, 80)]))
P['hats'] = fx(st['hats'], Pedalboard([HighpassFilter(6000), LowpassFilter(15000)]))
P['perc'] = fx(st['perc'], Pedalboard([HighpassFilter(70), Compressor(-20, 3, 1, 60)]))
P['bells'] = sc(fx(st['bells'], Pedalboard([HighpassFilter(90), PeakFilter(2500, -2, 1), HighShelfFilter(8000, -2)])), .3)
P['fx'] = fx(st['fx'], Pedalboard([HighpassFilter(30), LowpassFilter(12000)]))

def softclip0(x, th):
    a = np.abs(x); y = x.copy(); o = a > th
    y[o] = np.sign(x[o]) * (th + (1 - th) * np.tanh((a[o] - th) / (1 - th)))
    return y


def haas(x, ms):
    d = int(ms * SR / 1000)
    return np.stack([x[:, 0], np.concatenate([np.zeros(d), x[:-d, 1]])], 1)
P['strings'] = haas(P['strings'], 9); P['organ'] = haas(P['organ'], 7)
for k in P:
    P[k] = P[k] * db(G[k])
P['kick'] = softclip0(P['kick'] / np.abs(P['kick']).max(), 0.5) * np.abs(P['kick']).max() * 1.2

# ---------------- reverb sends
hall = S.make_ir(2.3, 3.0, 0.022, 0.75, True, 21, 1.0)
room = S.make_ir(0.55, 0.9, 0.006, 0.8, True, 22, 0.8)
SEND_H = dict(fiddle=.22, fiddle2=.25, viola=.18, harpsi=.2, organ=.35, strings=.3, winds=.3, bells=.55, fx=.3,
              perc=.08, snare=.12, drone=.12)
SEND_R = dict(perc=.3, snare=.25, harpsi=.12, fiddle=.12, hats=.15, winds=.12)
hsum = sum(P[k] * v for k, v in SEND_H.items())
rsum = sum(P[k] * v for k, v in SEND_R.items())
hall_ret = S.convolve_st(S.hp(hsum, 250), hall)
hall_ret = S.lp(hall_ret, 7000)
hall_ret = sc(hall_ret, .55) * db(-6)
room_ret = sc(S.convolve_st(S.hp(rsum, 200), room), .3) * db(-7)
# tempo delay on fiddle (dotted 8th) - subtle
dly = fx(P['fiddle'] * 0.18, Pedalboard([HighpassFilter(500), LowpassFilter(5000), Delay(STEP * 3, 0.25, 1.0)]))
dly = np.stack([dly[:, 0], np.roll(dly[:, 1], int(STEP * SR))], 1)

mix = sum(P.values()) + hall_ret + room_ret + sc(dly, .4)

# ---------------- master
mix = S.hp(mix, 25)
master = Pedalboard([
    LowShelfFilter(60, 0.5),
    PeakFilter(300, -1.0, 0.7),
    PeakFilter(3500, 1.0, 0.7),
    HighShelfFilter(10000, 2.0),
    Compressor(-14, 1.8, 15, 150),
])
m = fx(mix, master)
# mid/side: mono below 120 Hz
mid = (m[:, 0] + m[:, 1]) / 2
side = (m[:, 0] - m[:, 1]) / 2
side = S.hp(side, 140) * 1.25 + S.hp(side, 400) * 0.45
m = np.stack([mid + side, mid - side], 1)
m = m[:N]
# fades for clean loop edges
f_in = int(0.002 * SR); f_out = int(0.012 * SR)
m[:f_in] *= np.linspace(0, 1, f_in)[:, None]
m[-f_out:] *= np.linspace(1, 0, f_out)[:, None]

meter = pyln.Meter(SR)
TARGET = -10.0


def softclip(x, th=0.8):
    a = np.abs(x)
    over = a > th
    y = x.copy()
    y[over] = np.sign(x[over]) * (th + (1 - th) * np.tanh((a[over] - th) / (1 - th)))
    return y


def master_at(g):
    y = m * db(g)
    y = softclip(y, 0.85)
    up = resample_poly(y, 4, 1, axis=0)
    up = S.brickwall(up, db(-1.15), int(0.0015 * SR * 4), 0.06 * SR * 4)
    y = resample_poly(up, 1, 4, axis=0)
    return y


lo, hi = -12.0, 12.0
for it in range(12):
    g = (lo + hi) / 2
    y = master_at(g)
    L = meter.integrated_loudness(y)
    if L > TARGET:
        hi = g
    else:
        lo = g
    if abs(L - TARGET) < 0.05:
        break
tp = 20 * np.log10(np.max(np.abs(resample_poly(y, 4, 1, axis=0))) + 1e-12)
if tp > -1.0:
    y *= db(-1.0 - tp - 0.02)
    tp = 20 * np.log10(np.max(np.abs(resample_poly(y, 4, 1, axis=0))))
print('input gain %.2f dB' % g)
print('LUFS %.2f  TruePeak %.2f dBTP  samplepeak %.2f' % (meter.integrated_loudness(y), tp,
                                                          20 * np.log10(np.max(np.abs(y)))))
out = sys.argv[2] if len(sys.argv) > 2 else 'mix.wav'
sf.write(out, y, SR, subtype='PCM_24')
np.save('mixpre.npy', mix[:N].astype(np.float32))
print('wrote', out, y.shape)
