"""Render candidates:  python render.py [1 2 3 4]"""
import sys, os, json, time, subprocess, importlib
import numpy as np
from common import *

SONGS = {
    '1': ('song1_pickpocket', '01_Pickpocket_Shuffle'),
    '2': ('song2_ratcatcher', '02_Royal_Rat_Catcher'),
    '3': ('song3_leech', '03_Leech_Collector_Garage'),
    '4': ('song4_knocker', '04_Knocker_Upper_Charleston'),
}
OUT = os.path.join(os.path.dirname(__file__), '..')


def render(key, stats=True):
    mod, name = SONGS[key]
    t0 = time.time()
    S, cfg, kw = importlib.import_module(mod).build()
    if stats:
        a, b = int(S.t(D1) * SR), int(S.t(BRK) * SR)
        print(f'  bus RMS (drop 1, after gain):')
        for k, B in sorted(S.buses.items()):
            g = cfg.get(k, {}).get('gain', 1.0)
            seg = B[:, a:b] * g
            rms = np.sqrt(np.mean(seg ** 2)) + 1e-12
            print(f'    {k:8s} rms {20*np.log10(rms):6.1f} dB  peak {20*np.log10(np.abs(seg).max()+1e-12):6.1f} dB')
    y, L = S.mixdown(cfg, **kw)
    wav = os.path.join(OUT, f'{name}.wav')
    mp3 = os.path.join(OUT, f'{name}.mp3')
    write_wav24(wav, y)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', '320k',
                    '-metadata', f'title={S.title}', '-metadata', 'album=3 Weirdest Jobs in History (OST candidates)', mp3], check=True)
    cues = sorted(S.cues, key=lambda c: c['beat'])
    with open(os.path.join(OUT, 'cues', f'{name}_cues.json'), 'w') as f:
        bar_starts = [0, 4] + list(range(6, 42, 4)) + [42] + list(range(44, 80, 4)) + [80] + list(range(82, 118, 4)) + list(range(118, 142, 4)) + [142]
        json.dump(dict(title=S.title, bpm=round(BPM, 3), duration=DUR, beats=TOTAL_BEATS,
                       beat_seconds=round(SPB, 5), every_beat='t = n * beat_seconds (n = 0..143); swing does not move beats',
                       bar_downbeats=[round(b * SPB, 3) for b in bar_starts], cues=cues), f, indent=1)
    print(f'{name}: {time.time()-t0:.1f}s  LUFS {L:.2f}  peak {20*np.log10(np.abs(y).max()):.2f} dBFS')
    return y


if __name__ == '__main__':
    os.makedirs(os.path.join(OUT, 'cues'), exist_ok=True)
    for k in (sys.argv[1:] or list(SONGS)):
        render(k)
