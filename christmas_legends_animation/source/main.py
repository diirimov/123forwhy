"""Timeline, transitions, captions and the parallel frame renderer."""
import os, sys, math, subprocess, time, json
import numpy as np
import skia
from gfx import *
import film as F
from film import T, BEAT, STEP

DUR = 90.0; NFR = int(DUR * FPS)

SHOTS = [  # (t0, t1, fn, name)
    (0.0, T(3), F.s_open_fly, 'A0 village fly-through'),
    (T(3), T(5), F.s_nicholas, 'A1 Saint Nicholas + silhouettes'),
    (T(5), T(7), F.s_k1, 'K1 Krampus title / presents'),
    (T(7), T(9), F.s_k2, 'K2 snowball + shadow'),
    (T(9), T(11), F.s_k3, 'K3 KRAMPUS REVEAL'),
    (T(11), T(13), F.s_k4, 'K4 boy turns, terror'),
    (T(13), T(15), F.s_k5, 'K5 chase'),
    (T(15), T(17), F.s_k6, 'K6 good boy, Krampus nods'),
    (T(17), T(19), F.s_y1, 'Y1 Iceland / new clothes'),
    (T(19), T(21), F.s_y2, 'Y2 empty present'),
    (T(21), T(23), F.s_y3, 'Y3 YULE CAT REVEAL'),
    (T(23), T(25), F.s_y4, 'Y4 cat notices, run'),
    (T(25), T(27), F.s_y5, 'Y5 clothing transformation'),
    (T(27), T(29), F.s_y6, 'Y6 sniff, leaves, fall'),
    (T(29), T(31), F.s_w1, 'W1 cottage'),
    (T(31), T(33), F.s_w2, 'W2 knocks'),
    (T(33), T(35), F.s_w3, 'W3 MARI LWYD REVEAL'),
    (T(35), T(39, 8), F.s_w4, 'W4 rhyming contest'),
    (T(39, 8), T(41), F.s_w5, 'W5 celebration'),
    (T(41), DUR + 1, F.s_f, 'F finale'),
]
WHIPS = [T(11), T(13), T(35)]   # whip-pan cuts
WHIP_HALF = 0.13

def shot_at(t):
    for s in SHOTS:
        if s[0] <= t < s[1]: return s
    return SHOTS[-1]

def render_shot(fn, t):
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK); fn(c, t)
    return surf.makeImageSnapshot()

# ------------------------------------------------------------------ captions
CAPS = [  # (t_in, t_out, [lines], y, size)   words: '*' prefix red, '+' green, '^' gold
    (0.14, 3.62, ['*3 TERRIFYING', '+CHRISTMAS ^LEGENDS'], 420, 112),
    (T(3) + 0.18, T(5) - 0.1, ['CHRISTMAS WASN’T', 'ALWAYS *MERRY…'], 300, 92),
    (T(7) + 0.06, T(9) - 0.08, ['GOOD CHILDREN', 'GOT +PRESENTS.'], 400, 100),
    (T(9) + 0.06, T(11) - 0.08, ['NAUGHTY CHILDREN', 'GOT *KRAMPUS.'], 360, 100),
    (T(13) + 0.06, T(15) - 0.08, ['HE PUNISHED', 'MISBEHAVING CHILDREN.'], 400, 88),
    (T(19) + 0.06, T(21) - 0.08, ['EVERYONE NEEDED', '+NEW ^CLOTHES.'], 400, 100),
    (T(21) + 0.06, T(23) - 0.08, ['ACCORDING TO', '^ICELANDIC FOLKLORE…'], 300, 90),
    (T(23) + 0.06, T(25) - 0.08, ['NO NEW CLOTHES?', 'YOU MIGHT BE', 'ITS NEXT *MEAL.'], 300, 86),
    (T(31) + 0.06, T(33) - 0.08, ['IMAGINE HEARING', 'A KNOCK AT ^NIGHT…'], 400, 96),
    (T(33) + 0.06, T(35) - 0.08, ['AND FINDING', '*THIS.'], 360, 120),
    (T(35) + 0.06, T(37) - 0.08, ['THEY CHALLENGED YOU', 'TO A ^RHYMING ^CONTEST.'], 400, 88),
    (T(39, 8) + 0.06, T(41) - 0.55, ['THEN EVERYONE', '+CELEBRATED TOGETHER.'], 400, 90),
    (T(47) + 0.02, 90.5, ['STILL EXCITED', 'FOR ^CHRISTMAS?'], 430, 118),
]
SMALL = [(T(41) + 0.3, T(43) - 0.1, 'A (TOTALLY FICTIONAL) CHRISTMAS CROSSOVER', 250, 40)]
TITLES = [(T(5), T(7) - 0.06, '1. KRAMPUS', 'ALPINE FOLKLORE'),
          (T(17), T(19) - 0.06, '2. THE YULE CAT', 'ICELANDIC FOLKLORE · JÓLAKÖTTURINN'),
          (T(29), T(31) - 0.06, '3. MARI LWYD', 'WELSH MIDWINTER TRADITION')]
COLS = {'*': '#ff5a5f', '+': '#6ee08f', '^': '#ffd25a'}

def caption(c, t, t_in, t_out, lines, y0, size):
    if t < t_in or t > t_out + 0.2: return
    font = skia.Font(typeface('luckiest-guy-400.ttf'), size)
    out = ease_in(seg(t, t_out, t_out + 0.18))
    lh = size * 1.12
    widx = 0
    for li, line in enumerate(lines):
        words = line.split(' ')
        clean = [w_.lstrip('*+^') for w_ in words]
        space = font.measureText(' ')
        widths = [font.measureText(w_) for w_ in clean]
        total = sum(widths) + space * (len(words) - 1)
        # shrink overly long lines to the safe width
        sc = min(1.0, 900 / total)
        x = W / 2 - total * sc / 2
        y = y0 + li * lh * sc - out * 30
        for w_, cw, wd in zip(words, clean, widths):
            t_w = t_in + widx * 0.08 + li * 0.05
            k = ease_out_back(seg(t, t_w, t_w + 0.2), 2.2)
            a = int(255 * clamp(seg(t, t_w, t_w + 0.08)) * (1 - out))
            if a > 0:
                fill = COLS.get(w_[0], '#fff6e3')
                c.save(); c.translate(x + wd * sc / 2, y - size * 0.35 * sc); c.scale(sc * (0.6 + 0.4 * k), sc * (0.6 + 0.4 * k))
                draw_text(c, cw, 0, size * 0.35, size, 'luckiest-guy-400.ttf', fill, '#2a1530', size * 0.09, a, 'center', True,
                          glow_color=fill if fill != '#fff6e3' else None)
                c.restore()
            x += (wd + space) * sc; widx += 1

def small_caption(c, t, t_in, t_out, text, y, size):
    if t < t_in or t > t_out: return
    a = int(255 * min(seg(t, t_in, t_in + 0.25), 1 - seg(t, t_out - 0.25, t_out)))
    font = skia.Font(typeface('fredoka-600.ttf'), size)
    wdt = font.measureText(text) + 60
    c.drawPath(rrect(W / 2 - wdt / 2, y - size * 1.05, wdt, size * 1.55, size * 0.75), P('#140a24', int(a * 0.7)))
    draw_text(c, text, W / 2, y, size, 'fredoka-600.ttf', '#ffe9b8', '#140a24', 0, a, shadow=False, tracking=2)

def title_card(c, t, t_in, t_out, title, sub):
    if t < t_in or t > t_out + 0.25: return
    u = seg(t, t_in, t_in + 0.35); out = ease_in(seg(t, t_out, t_out + 0.25))
    a = int(255 * clamp(u * 3) * (1 - out))
    k = 1 + 0.5 * (1 - ease_out_back(u, 1.8))
    y = 430 - out * 40
    c.save(); c.translate(W / 2, y); c.scale(k, k)
    # banner plate
    c.drawPath(rrect(-470, -150, 940, 250, 40), P('#120820', int(a * 0.55), blur=18))
    size = 118 if len(title) < 13 else 100
    sh = lin((0, -size), (0, 10), ['#fff2b8', '#ffd25a', '#c98a1e'])
    draw_text(c, title, 0, 0, size, 'cinzel-decorative-900.ttf', '#ffd25a', '#2a1530', 9, a, shader=sh, glow_color='#ffb347')
    # flourish
    for sx in (-1, 1):
        c.drawLine(sx * 60, 48, sx * 380, 48, P('#ffd25a', a, stroke=4))
        c.drawPath(path_from([(sx * 390, 48), (sx * 404, 38), (sx * 418, 48), (sx * 404, 58)]), P('#ffd25a', a))
    c.drawPath(path_from([(0, 36), (12, 48), (0, 60), (-12, 48)]), P('#ff5a5f', a))
    draw_text(c, sub, 0, 110, 40 if len(sub) < 30 else 34, 'fredoka-600.ttf', '#fff6e3', '#2a1530', 5, a, tracking=4)
    c.restore()
    # sparkles on entrance
    if t - t_in < 0.6:
        for j in range(6):
            ang = j * 1.05 + t_in
            r_ = 300 + 250 * (t - t_in)
            F.sparkle(c, W / 2 + math.cos(ang) * r_, y + math.sin(ang) * r_ * 0.4, 26 * (1 - (t - t_in) / 0.6), 230)

# ------------------------------------------------------------------ transitions
def snow_swirl(c, t, tc, half=0.6):
    """white-out vortex of snow around a cut"""
    if abs(t - tc) > half: return
    u = 1 - abs(t - tc) / half
    c.drawRect(skia.Rect.MakeWH(W, H), P('#eef4ff', int(255 * ease_in(u) * 0.97)))
    r = random.Random(5)
    for k in range(160):
        ang0 = r.uniform(0, 6.28); rad_ = r.uniform(50, 1100)
        ang = ang0 + (t - tc) * 6 * (1.4 - rad_ / 1100)
        x = W / 2 + math.cos(ang) * rad_ * (1.2 - u * 0.4); y = H / 2 + math.sin(ang) * rad_ * 1.3
        c.drawCircle(x, y, r.uniform(4, 16) * (0.5 + u), P('#ffffff', int(255 * u)))
        c.drawLine(x, y, x - math.sin(ang) * 50, y + math.cos(ang) * 50, P('#ffffff', int(160 * u), stroke=5))

import random
def tail_wipe(c, t, t0, t1):
    if not (t0 <= t <= t1): return
    u = ease_in_out(seg(t, t0, t1))
    cx = lerp(W + 1700, -1700, u)
    pth = skia.Path(); pth.moveTo(cx + 900, H + 300)
    pth.cubicTo(cx + 200, H * 0.7, cx + 1100, H * 0.3, cx + 300, -300)
    c.drawPath(pth, P('#6a7ae0', 255, stroke=1960)); c.drawPath(pth, P(F.CAT, 255, stroke=1900))
    c.drawPath(pth, P('#7f9cff', 140, stroke=1900 + 30)) if False else None
    edge = skia.Path(pth);
    c.drawPath(pth, P('#2a2d4a', 255, stroke=1500)) if False else None

def whip(c, t, tc, imgA, imgB):
    u = seg(t, tc - WHIP_HALF, tc + WHIP_HALF)
    off = ease_in_out(u) * W * 1.15
    p = skia.Paint(); p.setAlphaf(1.0)
    c.drawImage(imgA, -off, 0)
    c.drawImage(imgB, W * 1.15 - off, 0)
    # streaks
    a = int(200 * math.sin(math.pi * u))
    r = random.Random(int(tc * 10))
    for k in range(40):
        y = r.uniform(0, H); x = r.uniform(-200, W)
        c.drawLine(x, y, x + r.uniform(200, 600), y, P('#ffffff', int(a * r.uniform(0.2, 0.7)), stroke=r.uniform(2, 10)))

def wreath_transition(c, t, render_next):
    """74.0 - 75.25: wreath spins in, its hole shows the finale square, then flies past"""
    t0, tc, t1 = 74.0, T(41), T(41) + 0.3
    if not (t0 <= t <= t1): return False
    if t < tc:
        u = ease_out(seg(t, t0, T(40, 12)))
        R = lerp(60, 560, u); rot = (t - t0) * 260
        hole = R * 0.78
        img = render_next(tc - 0.04)
        c.save(); p = skia.Path(); p.addCircle(W / 2, H * 0.5, hole); c.clipPath(p, doAntiAlias=True)
        c.drawImage(img, 0, 0); c.restore()
        F.wreath(c, W / 2, H * 0.5, R, rot)
        return False
    else:
        u = seg(t, tc, t1) ** 1.5
        F.wreath(c, W / 2, H * 0.5, lerp(560, 3200, u), (t - t0) * 260, int(255 * (1 - u)))
        return False

# ------------------------------------------------------------------ frame
def frame(t):
    surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK)
    s = shot_at(t)
    wc = [w_ for w_ in WHIPS if abs(t - w_) <= WHIP_HALF]
    if wc:
        tc = wc[0]
        A = shot_at(tc - 0.01); B = shot_at(tc + 0.01)
        whip(c, t, tc, render_shot(A[2], t), render_shot(B[2], t))
    else:
        s[2](c, t)
    # transitions
    snow_swirl(c, t, T(17), 0.55)
    tail_wipe(c, t, T(28, 13), T(29, 3))
    wreath_transition(c, t, lambda tt: render_shot(F.s_f, tt))
    # overlays
    vignette(c, 0.42)
    grain_overlay(c, t, 0.05)
    for (a, b, title, sub) in TITLES: title_card(c, t, a, b, title, sub)
    for cp in CAPS: caption(c, t, *cp)
    for sc in SMALL: small_caption(c, t, *sc)
    # final fade to black for the very last frames
    if t > DUR - 0.12: c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', int(255 * seg(t, DUR - 0.12, DUR))))
    return surf

def render_range(args):
    i0, i1, out = args
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
                             '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', '-r', str(FPS), out],
                            stdin=subprocess.PIPE)
    for i in range(i0, i1):
        surf = frame(i / FPS)
        arr = surf.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        proc.stdin.write(arr.tobytes())
    proc.stdin.close(); proc.wait()
    return out

if __name__ == '__main__':
    import multiprocessing as mp
    outdir = sys.argv[1]; os.makedirs(outdir, exist_ok=True)
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    b = int(sys.argv[3]) if len(sys.argv) > 3 else NFR
    chunk = 120
    jobs = [(i, min(i + chunk, b), os.path.join(outdir, f'chunk_{i:05d}.mp4')) for i in range(a, b, chunk)]
    t0 = time.time()
    with mp.Pool(4) as pool:
        for k, r in enumerate(pool.imap(render_range, jobs)):
            print(f'{k + 1}/{len(jobs)} {r} {time.time() - t0:.0f}s', flush=True)
    with open(os.path.join(outdir, 'list.txt'), 'w') as f:
        for j in jobs: f.write(f"file '{os.path.basename(j[2])}'\n")
