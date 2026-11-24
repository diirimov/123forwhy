"""Render WEIRD_MEDIEVAL_JOBS_FINAL.wav / .mp3 + cue sheet.   python3 render_medieval.py [--stats]"""
import os, sys, json, time, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import weird_medieval as W
from weird_medieval import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
NAME = 'WEIRD_MEDIEVAL_JOBS_FINAL'

if __name__ == '__main__':
    t0 = time.time()
    S, cfg, kw = W.build()
    if '--stats' in sys.argv:
        for (nm_, a, b) in [('intro', 0, 6), ('drop1', D1, BRK), ('s2', S2, FAKE), ('s3', S3, FIN), ('fin', FIN, END)]:
            print(nm_.ljust(6), '  '.join(f'{k}:{20*np.log10(np.sqrt(np.mean((B[:, int(S.t(a)*SR):int(S.t(b)*SR)]*cfg.get(k, {}).get("gain", 1))**2))+1e-12):.0f}'
                                       for k, B in sorted(S.buses.items())))
    y, L = S.mixdown(cfg, **kw)
    wav = os.path.join(OUT, NAME + '.wav'); mp3 = os.path.join(OUT, NAME + '.mp3')
    write_wav24(wav, y)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-codec:a', 'libmp3lame', '-b:a', '320k',
                    '-metadata', 'title=Weird Medieval Jobs', '-metadata', 'album=3 Weirdest Jobs in History', mp3], check=True)
    bar_starts = [0, 4] + list(range(6, 42, 4)) + [42] + list(range(44, 80, 4)) + [80] + list(range(82, 118, 4)) + list(range(118, 142, 4)) + [142]
    cues = sorted(S.cues, key=lambda c: c['time'])
    with open(os.path.join(OUT, NAME + '_CUES.json'), 'w') as f:
        json.dump(dict(title='Weird Medieval Jobs', bpm=round(BPM, 3), duration=DUR, beat_seconds=round(SPB, 5),
                       every_beat='t = n * beat_seconds, n = 0..143', bar_downbeats=[round(b * SPB, 3) for b in bar_starts],
                       cues=cues), f, indent=1)
    print(f'{NAME}: {time.time()-t0:.1f}s  LUFS {L:.2f}  peak {20*np.log10(np.abs(y).max()):.2f} dBFS')
