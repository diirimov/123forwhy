"""Synthesised, music-friendly SFX for the short, mixed UNDER the soundtrack.
   python3 audio/sfx_mix.py  -> out/sfx.wav, out/mix.wav (exactly 60.000 s, 48 kHz stereo)"""
import json, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SR = 48000
N = 60 * SR
rng = np.random.default_rng(7)

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def bp(x, lo, hi, o=2):
    return signal.sosfilt(signal.butter(o, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], 'band', output='sos'), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f / (SR / 2), 'low', output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f / (SR / 2), 'high', output='sos'), x)
def noise(n): return rng.normal(0, 1, n)
def sweep_noise(dur, f0, f1, q=0.6):
    n = int(dur * SR); x = noise(n); out = np.zeros(n); blk = 512
    for i in range(0, n, blk):
        k = i / n; fc = f0 * (f1 / f0) ** k
        seg = bp(x[max(0, i - 256):i + blk], fc * (1 - q / 2), fc * (1 + q / 2))
        out[i:i + blk] = seg[-len(out[i:i + blk]):]
    return out
def tone(f, dur, decay, partials=((1, 1),), drop=0.0):
    n = int(dur * SR); t = np.arange(n) / SR
    fi = f * (1 + drop * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(fi) / SR
    return sum(a * np.sin(k * ph) for k, a in partials) * np.exp(-t / decay)
def metal(dur=0.5, base=2100, dec=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * base * r * t + rng.uniform(0, 6)) * a * np.exp(-t / (dec * d)) for r, a, d in ((1, 1, 1), (1.62, .7, .8), (2.47, .5, .6), (3.71, .35, .45), (5.1, .2, .3)))
    y[:200] += noise(200) * np.exp(-np.arange(200) / 30) * 0.6
    return y

def make(kind):
    if kind == 'whoosh':
        x = sweep_noise(0.28, 300, 2600, 0.8); n = len(x); e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
        return x * e * 0.5
    if kind == 'swish': x = sweep_noise(0.16, 1200, 5000, 0.7); return x * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 2 * 0.35
    if kind == 'zip':
        x = sweep_noise(0.35, 500, 6000, 0.6); n = len(x); t = np.arange(n) / SR
        wh = np.sin(2 * np.pi * np.cumsum(900 + 2600 * (t / t[-1]) ** 2) / SR) * 0.25
        return (x * 0.6 + wh) * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    if kind in ('clink', 'glint'): return metal(0.6, 2300 if kind == 'clink' else 3200, 0.16) * (0.35 if kind == 'clink' else 0.22)
    if kind == 'shing':
        m = metal(0.7, 2800, 0.2) * 0.25; s = sweep_noise(0.25, 2500, 9000, 0.5) * np.sin(np.pi * np.linspace(0, 1, int(0.25 * SR))) * 0.35
        m[:len(s)] += s; return m
    if kind == 'tap': n = int(0.12 * SR); return (tone(950, 0.12, 0.02, ((1, 1), (2.3, .4))) + bp(noise(n), 800, 3000) * env(n, 0.001, 0.01) * 0.5) * 0.5
    if kind in ('book_slam', 'stamp'):
        n = int(0.5 * SR); low = tone(85 if kind == 'book_slam' else 110, 0.5, 0.09, drop=0.6)
        slap = bp(noise(n), 400, 4000) * env(n, 0.001, 0.03)
        return (low * 0.9 + slap * 0.7) * (0.8 if kind == 'book_slam' else 0.6)
    if kind == 'pop': return tone(800, 0.12, 0.035, ((1, 1), (2, .2)), drop=-0.6) * 0.35
    if kind == 'pop_big':
        y = tone(600, 0.25, 0.06, ((1, 1), (2, .25)), drop=-0.6) * 0.5
        sh = make('shimmer') * 0.6; out = np.zeros(max(len(y), len(sh))); out[:len(y)] += y; out[:len(sh)] += sh; return out
    if kind in ('plop', 'squelch'):
        n = int(0.18 * SR); t = np.arange(n) / SR
        y = np.sin(2 * np.pi * np.cumsum(420 * np.exp(-t * 10) + 160) / SR) * np.exp(-t / 0.05)
        return (y + lp(noise(n), 1500) * env(n, 0.002, 0.02) * 0.4) * (0.4 if kind == 'plop' else 0.3)
    if kind == 'gulp': n = int(0.16 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(180 + 500 * t / t[-1]) / SR) * np.sin(np.pi * t / t[-1]) * 0.3
    if kind == 'clunk': return (tone(220, 0.5, 0.12, ((1, 1), (2.4, .5), (3.9, .25))) + tone(70, 0.5, 0.1)) * 0.5
    if kind == 'freeze_hit':
        n = int(0.6 * SR); y = tone(60, 0.6, 0.14, drop=1.0) * 0.9 + bp(noise(n), 2000, 9000) * env(n, 0.001, 0.015) * 0.5
        y += metal(0.6, 1800, 0.25) * 0.08; return y * 0.6
    if kind in ('door', 'creak'):
        n = int(0.55 * SR); t = np.arange(n) / SR
        f = 140 + 60 * np.sin(2 * np.pi * 3 * t) + 25 * noise(n).cumsum() / np.sqrt(n)
        saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR)
        return bp(saw, 400, 2500) * np.sin(np.pi * t / t[-1]) * 0.18
    if kind == 'bonk':
        wood = tone(330, 0.4, 0.07, ((1, 1), (2.76, .5), (5.4, .2))) * 0.8
        n = int(0.7 * SR); t = np.arange(n) / SR
        boing = np.sin(2 * np.pi * np.cumsum(260 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3)) / SR) * np.exp(-t / 0.25) * 0.35
        thud = tone(70, 0.4, 0.1, drop=0.8) * 0.8
        out = np.zeros(n); out[:len(wood)] += wood; out += boing; out[:len(thud)] += thud; return out * 0.8
    if kind == 'thud': n = int(0.5 * SR); return (tone(55, 0.5, 0.12, drop=0.8) + lp(noise(n), 600) * env(n, 0.003, 0.06) * 0.6) * 0.7
    if kind in ('hit_low', 'drone_low'):
        if kind == 'hit_low': return tone(48, 1.0, 0.35, ((1, 1), (2, .3)), drop=0.5) * 0.55
        n = int(1.6 * SR); t = np.arange(n) / SR
        y = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((55, 1), (82.4, .5), (110, .3)))
        return lp(y * (1 + 0.2 * np.sin(2 * np.pi * 5 * t)), 400) * np.sin(np.pi * t / t[-1]) * 0.25
    if kind == 'unroll':
        n = int(0.4 * SR); y = np.zeros(n)
        for k in range(5): i = int(k * 0.07 * SR); m = int(0.05 * SR); y[i:i + m] += bp(noise(m), 300, 2500) * env(m, 0.002, 0.012)
        return y * 0.5
    if kind == 'shimmer':
        n = int(1.0 * SR); y = np.zeros(n)
        for k, f in enumerate((1174.7, 1396.9, 1760.0, 2349.3)):
            i = int(k * 0.06 * SR); seg = tone(f, (n - i) / SR, 0.35, ((1, 1), (2.01, .2), (3.98, .08))); y[i:] += seg[:n - i] * 0.18
        return y
    if kind == 'boing_small':
        n = int(0.35 * SR); t = np.arange(n) / SR
        return np.sin(2 * np.pi * np.cumsum(500 + 300 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6)) / SR) * np.exp(-t / 0.12) * 0.22
    if kind == 'riser_soft': x = sweep_noise(0.9, 300, 4000, 0.6); return x * np.linspace(0, 1, len(x)) ** 2 * 0.3
    if kind == 'cough_puff': n = int(0.18 * SR); return bp(noise(n), 300, 1800) * env(n, 0.01, 0.05) * 0.18
    if kind == 'impact_soft': n = int(0.3 * SR); return (bp(noise(n), 500, 5000) * env(n, 0.004, 0.06) * 0.5 + tone(90, 0.3, 0.08) * 0.4) * 0.6
    raise ValueError(kind)

PAN = {'whoosh': 0.0, 'swish': 0.2, 'clink': 0.25, 'glint': -0.25, 'shing': 0.2, 'pop': 0.15, 'plop': -0.15}

def main():
    cues = json.load(open(os.path.join(ROOT, 'out', 'sfx_cues.json')))
    cues.sort(key=lambda c: c['t'])
    # drop duplicates of the same kind within 150 ms
    kept, last = [], {}
    for c in cues:
        if c['kind'] in last and c['t'] - last[c['kind']] < 0.15: continue
        kept.append(c); last[c['kind']] = c['t']
    bus = np.zeros((N + SR, 2))
    for c in kept:
        y = make(c['kind']) * c.get('gain', 1)
        y = hp(y, 40)
        p = PAN.get(c['kind'], 0) * (1 if hash(round(c['t'], 2)) % 2 else -1)
        L, R = np.cos((p + 1) * np.pi / 4) * 1.414, np.sin((p + 1) * np.pi / 4) * 1.414
        i = int(round(c['t'] * SR))
        if i < 0: y = y[-i:]; i = 0
        m = min(len(y), len(bus) - i)
        bus[i:i + m, 0] += y[:m] * L; bus[i:i + m, 1] += y[:m] * R
    # small room so the effects sit in the same space as the music
    ir_n = int(0.5 * SR); t = np.arange(ir_n) / SR
    ir = np.stack([lp(rng.normal(0, 1, ir_n), 5000) * np.exp(-t / 0.09) for _ in range(2)], 1); ir /= np.sqrt((ir ** 2).sum())
    wet = np.stack([signal.fftconvolve(bus[:, c], ir[:, c])[:len(bus)] for c in range(2)], 1)
    sfx = (bus + wet * 0.25)[:N]
    sr, music = wavfile.read(os.path.join(ROOT, '..', 'music', 'MEDIEVAL_MEDICINE_V3_MASTER.wav'))
    music = music.astype(float) / 32768
    assert sr == SR and len(music) == N
    # SFX peaks sit ~12 dB under the music's peaks: the music stays the hero
    sfx = sfx * (10 ** (-13 / 20) / np.abs(sfx).max())
    mix = music + sfx
    # transparent look-ahead limiter only where a hit lands on a music peak (true-peak <= -1 dBTP)
    from scipy.ndimage import maximum_filter1d
    up = np.abs(signal.resample_poly(mix, 4, 1, axis=0)).max(1)[:len(mix) * 4].reshape(-1, 4).max(1)
    g = np.minimum(1, 0.88 / np.maximum(maximum_filter1d(up, 2 * int(0.003 * SR) + 1), 1e-9))
    gs = np.empty_like(g); prev = 1.0; ar = np.exp(-1 / (0.08 * SR))
    for i in range(len(g)):
        v = g[i]; prev = v if v < prev else ar * prev + (1 - ar) * v; gs[i] = prev
    mix = mix * np.minimum(lp(gs, 300), g)[:, None]
    pk = 1.0
    wavfile.write(os.path.join(ROOT, 'out', 'sfx.wav'), SR, (np.clip(sfx, -1, 1) * 32767).astype(np.int16))
    wavfile.write(os.path.join(ROOT, 'out', 'mix.wav'), SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
    print('cues', len(cues), 'kept', len(kept), 'sfx peak dBFS', round(20 * np.log10(np.abs(sfx).max() + 1e-9), 1), 'min limiter gain dB', round(20 * np.log10(g.min()), 2))

if __name__ == '__main__':
    main()
