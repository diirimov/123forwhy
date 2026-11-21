#!/usr/bin/env python3
"""
Frame renderer + encoder.

  python3 render.py stills 0.5 3 6 ...         -> build/stills.png contact sheet (QA)
  python3 render.py test  START END            -> build/test.mp4 (with audio)
  python3 render.py final                      -> output/FINAL_JACKSON5_ANIMATION.mp4 + _SILENT.mp4
"""
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).parent))
import timing as T  # noqa: E402
from gfx import W, H, post  # noqa: E402
import importlib  # noqa: E402
timeline = importlib.import_module(os.environ.get('TIMELINE', 'timeline'))

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
OUT = ROOT / 'output'


def render_frame(i):
    t = i / T.FPS
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    timeline.draw(c, t, surf)
    post(c, i, **timeline.grade(t))
    img = surf.makeImageSnapshot()
    return np.asarray(img.toarray(colorType=skia.kRGBA_8888_ColorType))[:, :, :3].copy()


def _chunk(args):
    a, b, path = args
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(T.FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '14',
                            '-pix_fmt', 'yuv420p', '-tune', 'animation', path], stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(render_frame(i).tobytes())
    enc.stdin.close()
    enc.wait()
    return path


def encode(f0, f1, name, workers=4, audio=True, silent_name=None):
    BUILD.mkdir(exist_ok=True)
    n = f1 - f0
    per = max(1, -(-n // (workers * 3)))
    jobs = [(a, min(a + per, f1), str(BUILD / f'chunk_{a:05d}.mp4')) for a in range(f0, f1, per)]
    t0 = time.time()
    with Pool(workers) as pool:
        done = 0
        for p in pool.imap(_chunk, jobs):
            done += 1
            print(f'  chunk {done}/{len(jobs)}  {time.time() - t0:.0f}s', flush=True)
    lst = BUILD / 'chunks.txt'
    lst.write_text(''.join(f"file '{j[2]}'\n" for j in jobs))
    silent = str(OUT / silent_name) if silent_name else str(BUILD / f'{name}_silent.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy',
                    '-movflags', '+faststart', silent], check=True)
    if audio:
        a0 = T.SONG_IN + f0 / T.FPS
        dur = n / T.FPS
        fade_st = max(0.0, T.DURATION - T.FADE - f0 / T.FPS)
        af = f'afade=t=in:st=0:d=0.02,afade=t=out:st={fade_st:.3f}:d={T.FADE:.3f}'
        dips = getattr(timeline, 'AUDIO_DIPS', [])
        if dips:
            off = f0 / T.FPS
            terms = ['(1-{:.3f}*clip((t+{o:.4f}-{a:.3f})/0.12\\,0\\,1)*(1-clip((t+{o:.4f}-{b:.3f})/0.12\\,0\\,1)))'
                     .format(1 - g, o=off, a=a_, b=b_) for a_, b_, g in dips]
            af = f"volume='{'*'.join(terms)}':eval=frame," + af
        out = str(OUT / ('JACKSON5_STORY_V2_FINAL.mp4' if name == 'FINAL_JACKSON5_STORY_V2' else f'{name}.mp4')) if name.startswith('FINAL') else str(BUILD / f'{name}.mp4')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-ss', f'{a0:.4f}', '-t', f'{dur:.4f}',
                        '-i', str(ROOT / 'audio' / 'source.mp3'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', af, '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out],
                       check=True)
        print('wrote', out)
    for j in jobs:
        os.remove(j[2])


def stills(times, out=BUILD / 'stills.png', scale=0.25):
    cols = min(len(times), 6)
    rows = -(-len(times) // cols)
    w, h = int(W * scale), int(H * scale)
    sheet = skia.Surface(cols * w, rows * h)
    sc = sheet.getCanvas()
    for n, t in enumerate(times):
        i = int(round(t * T.FPS))
        arr = render_frame(i)
        rgba = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
        img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
        sc.drawImageRect(img, skia.Rect.MakeXYWH((n % cols) * w, (n // cols) * h, w, h),
                         skia.SamplingOptions(skia.FilterMode.kLinear))
    sheet.makeImageSnapshot().save(str(out), skia.kPNG)
    print('wrote', out)


def single(t, out=BUILD / 'frame.png'):
    arr = render_frame(int(round(t * T.FPS)))
    rgba = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
    skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType).save(str(out), skia.kPNG)
    print('wrote', out)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stills':
        stills([float(x) for x in sys.argv[2:]])
    elif mode == 'frame':
        single(float(sys.argv[2]), BUILD / (sys.argv[3] if len(sys.argv) > 3 else 'frame.png'))
    elif mode == 'test':
        a, b = float(sys.argv[2]), float(sys.argv[3])
        encode(int(a * T.FPS), int(b * T.FPS), sys.argv[4] if len(sys.argv) > 4 else 'test')
    elif mode == 'final':
        OUT.mkdir(exist_ok=True)
        encode(0, T.NFRAMES, 'FINAL_JACKSON5_ANIMATION', silent_name='FINAL_JACKSON5_SILENT.mp4')
    elif mode == 'final_v2':
        OUT.mkdir(exist_ok=True)
        encode(0, T.NFRAMES, 'FINAL_JACKSON5_STORY_V2', silent_name='JACKSON5_STORY_V2_SILENT.mp4')
