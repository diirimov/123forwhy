"""Render MEDIEVAL_JOBS_V2_FINAL (+ stems, beat map).  python3 render_v2.py"""
import json, time, subprocess
from song_v2 import *  # noqa
from studio import glue_comp, limiter, lufs, reverb, pingpong, sidechain_curve

OUT = os.path.join(HERE, '..')
TARGET = -11.0


def process_bus(name, B, sc):
    c = MIX.get(name, {})
    x = B
    for eq in c.get('eq', []):
        x = filt(x, *eq)
    if c.get('drive'):
        d = c['drive']; x = np.tanh(d * x) / d
    if c.get('haas'):
        d = int(c['haas'] * SR); side = np.zeros_like(x[1]); side[d:] = x[1][:-d]
        x = np.stack([x[0], 0.45 * x[1] + 0.75 * side])
    x = x * c.get('gain', 1.0)
    if c.get('sc'):
        x = x * (1 - c['sc'] * (1 - sc))
    return x, c


def render():
    t0 = time.time()
    S = build()
    print(f'composed in {time.time()-t0:.0f}s')
    N = S.N
    sc = sidechain_curve(N, S.kicks, depth=1.0, rel=0.11)
    stems = {}
    for stem, names in STEMS.items():
        dry = np.zeros((2, N)); rv = np.zeros((2, N)); rv2 = np.zeros((2, N)); dl = np.zeros((2, N))
        for nm_ in names:
            if nm_ not in S.buses:
                continue
            x, c = process_bus(nm_, S.buses[nm_], sc)
            dry += x; rv += x * c.get('rv', 0); rv2 += x * c.get('rv2', 0); dl += x * c.get('dl', 0)
        wet = np.zeros((2, N))
        if np.abs(rv).max() > 0:
            wet += reverb(rv, t60=1.5, predelay=0.02, damp=0.45) * 1.2
        if np.abs(rv2).max() > 0:
            wet += reverb(rv2, t60=0.6, predelay=0.008, damp=0.6, lo_cut=200)
        if np.abs(dl).max() > 0:
            wet += pingpong(dl, SPB * 0.75, fb=0.38, taps=5)
        rsc = 1 - 0.4 * (1 - sc)
        y = dry + wet * rsc
        L = int(DUR * SR)
        tail = y[:, L:]
        y = y[:, :L].copy(); y[:, :tail.shape[1]] += tail
        stems[stem] = y
    mix = sum(stems.values())
    pad = SR
    g0 = 10 ** ((-18.0 - lufs(mix)) / 20)          # gain-stage the raw mix to -18 LUFS before the chain
    def master(x, g):
        z = np.concatenate([x[:, -pad:], x, x[:, :pad]], axis=1) * g0
        z = hp(z, 25, 0.6)
        z = filt(z, 'peak', 3200, 0.7, 2.0)
        z = filt(z, 'peak', 280, 1.0, 1.0)
        z = filt(z, 'hs', 10000, 0.7, 1.0)
        z = glue_comp(z, thresh_db=-16, ratio=1.5, att=0.015, rel=0.2)
        return limiter(z * g, ceiling=0.89)[:, pad:-pad]
    g = 1.0
    for _ in range(5):
        y = master(mix, g); Lm = lufs(y); g *= 10 ** ((TARGET - Lm) / 20)
    y = master(mix, g)
    pre = np.concatenate([mix[:, -pad:], mix, mix[:, :pad]], axis=1)[:, pad:-pad] * g0 * g
    w = 2400
    e = lambda z: np.array([np.abs(z[:, i:i + w]).max() for i in range(0, z.shape[1] - w, w)])
    gr = 20 * np.log10(e(y) + 1e-9) - 20 * np.log10(e(pre) + 1e-9)
    print('limiter+glue GR dB p50/p90/p99/min:', np.round(np.percentile(gr, [50, 10, 1]), 1), round(gr.min(), 1))
    g = g0 * g
    Lm = lufs(y)
    print(f'master LUFS {Lm:.2f}  peak {20*np.log10(np.abs(y).max()):.2f} dBFS  gain {20*np.log10(g):.1f} dB')
    write_wav24(os.path.join(OUT, 'MEDIEVAL_JOBS_V2_FINAL.wav'), y)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(OUT, 'MEDIEVAL_JOBS_V2_FINAL.wav'),
                    '-codec:a', 'libmp3lame', '-b:a', '320k', '-metadata', 'title=Medieval Jobs V2 (Hey-ya Village Dance)',
                    os.path.join(OUT, 'MEDIEVAL_JOBS_V2_FINAL.mp3')], check=True)
    # stems: same gain as the master, un-limited; common trim so nothing clips
    sd = os.path.join(OUT, 'stems'); os.makedirs(sd, exist_ok=True)
    st = {k: v * g for k, v in stems.items()}
    nov = sum(v for k, v in st.items() if k != 'Vocal_Chants')
    peak = max([np.abs(v).max() for v in st.values()] + [np.abs(sum(st.values())).max(), np.abs(nov).max()])
    trim = min(1.0, 0.89 / peak)
    for k, v in st.items():
        write_wav24(os.path.join(sd, f'{k}.wav'), v * trim)
    write_wav24(os.path.join(sd, 'Mix_No_Vocals.wav'), nov * trim)
    print(f'stems trim {20*np.log10(trim):.1f} dB; stem rms:', {k: round(20*np.log10(np.sqrt(np.mean(v**2))+1e-12), 1) for k, v in st.items()})
    return S, y, trim


def beat_map(S, trim):
    beats = [dict(n=i, time=round(i * SPB, 4), bar=i // 4, beat_in_bar=i % 4 + 1, downbeat=i % 4 == 0) for i in range(163)]
    bars_ = [dict(bar=b, start=round(b * BAR, 4), end=round(min((b + 1) * BAR, DUR), 4)) for b in range(41)]
    sections = [dict(name=n, start_beat=a, end_beat=b, start=round(a * SPB, 4), end=round(b * SPB, 4)) for n, (a, b) in SEC.items()]
    evs = sorted(S.events, key=lambda e: e['time'])
    for e in evs:
        e['time'] = round(max(0.0, e['time']), 4)
    m = dict(title='Medieval Jobs V2 - Hey-ya Village Dance', bpm=BPM, time_signature='4/4', sample_rate=SR,
             duration=DUR, beat_seconds=SPB, bar_seconds=BAR, loop='seamless: 65.000 s wraps to 0.000 (tail is 2.5 beats)',
             stems_trim_db=round(20 * np.log10(trim), 2),
             sections=sections,
             drops=[e for e in evs if e['type'] == 'drop'],
             transitions=[e for e in evs if e['type'] == 'transition'],
             impacts=[e for e in evs if e['type'] == 'impact'],
             vocal_accents=[e for e in evs if e['type'] == 'vocal'],
             melody_cues=[e for e in evs if e['type'] in ('melody', 'fanfare')],
             accents_and_sfx=[e for e in evs if e['type'] in ('accent', 'sfx')],
             bars=bars_, beats=beats)
    with open(os.path.join(OUT, 'BEAT_MAP.json'), 'w') as f:
        json.dump(m, f, indent=1)
    print('beat map:', {k: len(v) for k, v in m.items() if isinstance(v, list)})


if __name__ == '__main__':
    S, y, trim = render()
    beat_map(S, trim)
