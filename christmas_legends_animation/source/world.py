"""Illustrated winter environments."""
import math, random
import numpy as np
import skia
from gfx import *
from human import INK, shade_hex

LINE = '#1b1430'

# ------------------------------------------------------------------ sky
def sky(c, w, h, top='#0e1440', mid='#2b3a7a', bot='#6f7fb8', stars=True, seed=1, moon=None, aurora=0.0, t=0.0):
    c.drawRect(skia.Rect.MakeWH(w, h), PS(lin((0, 0), (0, h), [top, mid, bot], [0, 0.55, 1])))
    if aurora > 0:
        for k, (colr, yo, amp) in enumerate((('#3cffb0', 0.16, 60), ('#7affd8', 0.22, 40), ('#b07aff', 0.12, 50))):
            pth = skia.Path(); pts = []
            for i in range(0, w + 60, 60):
                y = h * yo + math.sin(i * 0.004 + k + t * 0.4) * amp + math.sin(i * 0.011 + t * 0.7) * amp * 0.4
                pts.append((i, y))
            pth.moveTo(pts[0][0], pts[0][1])
            for q in pts[1:]: pth.lineTo(*q)
            c.drawPath(pth, P(colr, int(110 * aurora), stroke=90, blur=40))
            c.drawPath(pth, P(colr, int(70 * aurora), stroke=24, blur=12))
    if stars:
        r = random.Random(seed)
        for _ in range(int(w * h / 9000)):
            x, y = r.uniform(0, w), r.uniform(0, h * 0.55)
            s = r.choice((1.2, 1.6, 2.2, 3.0))
            c.drawCircle(x, y, s, P('#ffffff', int(r.uniform(90, 230))))
            if s >= 3: glow(c, x, y, 10, '#cfe0ff', 120)
    if moon:
        mx, my, mr = moon
        glow(c, mx, my, mr * 4, '#c8d8ff', 70)
        c.drawCircle(mx, my, mr, PS(rad((mx - mr * 0.3, my - mr * 0.3), mr * 1.3, ['#fffdf0', '#f4efd8', '#d9d2b8'])))
        for (dx, dy, rr) in ((0.3, 0.1, 0.18), (-0.25, 0.35, 0.12), (-0.1, -0.35, 0.1)):
            c.drawCircle(mx + dx * mr, my + dy * mr, rr * mr, P('#c9c1a2', 110))

def mountains(c, w, base_y, peak_h, col_='#5a6aa8', snow='#eef3ff', seed=2, n=5, fog='#8aa0d8', detail=True):
    r = random.Random(seed)
    xs = sorted([r.uniform(0, w) for _ in range(n)])
    for x in xs:
        ph = peak_h * r.uniform(0.6, 1.0); hw = ph * r.uniform(0.9, 1.4)
        top = (x, base_y - ph)
        ptsL = [(x - hw, base_y)]; ptsR = []
        for k in range(1, 6):
            t = k / 6
            ptsL.append((x - hw * (1 - t) + r.uniform(-15, 15), base_y - ph * t + r.uniform(-10, 10)))
        body = [(x - hw, base_y)] + ptsL[1:] + [top]
        for k in range(5, 0, -1):
            t = k / 6
            body.append((x + hw * (1 - t) + r.uniform(-15, 15), base_y - ph * t + r.uniform(-10, 10)))
        body.append((x + hw, base_y))
        mp = path_from(body, True)
        c.drawPath(mp, PS(lin((x - hw, base_y - ph), (x + hw, base_y), [shade(col_, 0.12), col(col_), shade(col_, -0.25)])))
        # shadow side
        sh = path_from([top] + body[len(ptsL) + 1:] + [(x, base_y)], True)
        c.drawPath(sh, P('#1a2050', 70))
        # snow cap
        cap = [top]
        for k in range(7):
            t = 0.33 + r.uniform(-0.05, 0.05)
            xx = x - hw * t + k * (2 * hw * t / 6); yy = base_y - ph * (1 - t) + (r.uniform(0, 40) if k % 2 else r.uniform(-10, 10))
            cap.append((xx, yy))
        capp = path_from([top] + cap[1:], True, 0.3)
        c.drawPath(capp, PS(lin((x - hw * 0.3, top[1]), (x + hw * 0.3, top[1] + ph * 0.35), [snow, shade_hex(snow, -0.12)])))
    c.drawRect(skia.Rect.MakeLTRB(0, base_y - peak_h * 0.25, w, base_y + 4), PS(lin((0, base_y - peak_h * 0.25), (0, base_y), [(fog, 0), (fog, 180)])))

def hills(c, w, base_y, amp, col_, seed=3, snow=True, top_col=None):
    r = random.Random(seed); pts = [(0, base_y + 400)]
    ph = r.uniform(0, 6)
    for x in range(0, w + 80, 80):
        pts.append((x, base_y - amp * (0.5 + 0.5 * math.sin(x * 0.0021 + ph)) - amp * 0.3 * math.sin(x * 0.007 + ph * 2)))
    pts.append((w, base_y + 400))
    hp = path_from(pts, True, 0.8)
    c.drawPath(hp, PS(lin((0, base_y - amp), (0, base_y + 200), [top_col or shade(col_, 0.2), col(col_)])))

# ------------------------------------------------------------------ buildings
WIN_LIGHT = '#ffcf6e'

class Lights:
    """records dynamic light positions while static art is drawn"""
    def __init__(self): self.windows = []; self.bulbs = []; self.lamps = []; self.smoke = []
    def shift(self, dx, dy):
        L = Lights()
        L.windows = [(x + dx, y + dy, w, h, k) for (x, y, w, h, k) in self.windows]
        L.bulbs = [(x + dx, y + dy, c_, k) for (x, y, c_, k) in self.bulbs]
        L.lamps = [(x + dx, y + dy, k) for (x, y, k) in self.lamps]
        L.smoke = [(x + dx, y + dy, k) for (x, y, k) in self.smoke]
        return L

def window(c, x, y, w, h, lit=True, L=None, shutters=None, k=0, frame='#f4efe2', arch=False):
    if lit:
        glow(c, x + w / 2, y + h / 2, max(w, h) * 1.3, '#ffb84d', 90)
    pth = rrect(x, y, w, h, 4) if not arch else _arch(x, y, w, h)
    c.drawPath(pth, P(LINE, 255, stroke=10))
    if lit:
        c.drawPath(pth, PS(rad((x + w / 2, y + h * 0.65), max(w, h), ['#fff2c0', WIN_LIGHT, '#e98a2e'])))
        # silhouette of curtain / plant
        c.save(); c.clipPath(pth, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeLTRB(x, y + h * 0.78, x + w, y + h), P('#c0612a', 160))
        c.restore()
    else:
        c.drawPath(pth, PS(lin((x, y), (x + w, y + h), ['#2a3a6a', '#141c3a'])))
    c.drawLine(x + w / 2, y, x + w / 2, y + h, P(frame, 255, stroke=5))
    c.drawLine(x, y + h / 2, x + w, y + h / 2, P(frame, 255, stroke=5))
    c.drawPath(pth, P(frame, 255, stroke=5))
    # snowy sill
    c.drawPath(rrect(x - 8, y + h - 2, w + 16, 12, 6), P('#f2f6ff'))
    c.drawPath(rrect(x - 8, y + h - 2, w + 16, 12, 6), P(LINE, 255, stroke=2.5))
    if shutters:
        for sx in (x - w * 0.42, x + w + 2):
            sp = rrect(sx, y - 2, w * 0.4, h + 4, 3)
            c.drawPath(sp, P(shutters)); c.drawPath(sp, P(LINE, 255, stroke=3))
            for k_ in range(3):
                c.drawLine(sx + 3, y + h * (0.25 + 0.25 * k_), sx + w * 0.4 - 3, y + h * (0.25 + 0.25 * k_), P(shade_hex(shutters, -0.3), 255, stroke=2))
    if L is not None and lit: L.windows.append((x, y, w, h, k))

def _arch(x, y, w, h):
    p = skia.Path(); p.moveTo(x, y + h); p.lineTo(x, y + w / 2); p.arcTo(skia.Rect.MakeXYWH(x, y, w, w), 180, 180, False)
    p.lineTo(x + w, y + h); p.close(); return p

def snow_cap(c, pts, thick=26, seed=0):
    """snow lying along a roof edge polyline"""
    r = random.Random(seed)
    top = [(x, y - 2) for x, y in pts]
    bot = []
    for i, (x, y) in enumerate(pts[::-1]):
        bot.append((x, y + thick * r.uniform(0.6, 1.1)))
    # drips/icicles
    sp = path_from(top + bot, True, 0.6)
    c.drawPath(sp, P(LINE, 255, stroke=6))
    c.drawPath(sp, PS(lin((0, pts[0][1] - 10), (0, pts[0][1] + thick), ['#ffffff', '#dfe8ff'])))
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        for k in range(int(math.hypot(x1 - x0, y1 - y0) / 55)):
            if r.random() < 0.5:
                t = r.random(); x = lerp(x0, x1, t); y = lerp(y0, y1, t) + thick * 0.7
                ln = r.uniform(12, 34)
                c.drawPath(path_from([(x - 5, y), (x + 5, y), (x, y + ln)], True), P('#e8f4ff', 230))

def house(c, x, gy, w, h, style='chalet', wall='#c98b5a', roof='#7a2f2a', trim='#f4efe2', L=None, seed=0,
          lights=True, wreath=True, chimney=True, lit_ratio=0.8, door_col='#6a2f22', shutters=None, depth=0.0):
    """x = left edge, gy = ground y. Returns door rect."""
    r = random.Random(seed)
    roof_h = h * (0.55 if style in ('chalet',) else 0.7 if style == 'iceland' else 0.6)
    over = w * (0.12 if style == 'chalet' else 0.06)
    wall_top = gy - h
    # chimney behind roof
    if chimney:
        cx = x + w * r.uniform(0.6, 0.78)
        ch = rrect(cx, wall_top - roof_h * 0.9, w * 0.11, roof_h * 0.7, 3)
        c.drawPath(ch, P(LINE, 255, stroke=8)); c.drawPath(ch, P('#7b5a4e' if style != 'stone' else '#6d6f7a'))
        for k in range(3):
            c.drawLine(cx, wall_top - roof_h * 0.9 + 14 + k * 18, cx + w * 0.11, wall_top - roof_h * 0.9 + 14 + k * 18, P(LINE, 120, stroke=2))
        c.drawPath(rrect(cx - 6, wall_top - roof_h * 0.9 - 14, w * 0.11 + 12, 18, 8), P('#ffffff'))
        if L is not None: L.smoke.append((cx + w * 0.055, wall_top - roof_h * 0.9 - 14, seed))
    # walls
    wp = rrect(x, wall_top, w, h, 3)
    c.drawPath(wp, P(LINE, 255, stroke=10))
    c.drawPath(wp, PS(lin((x, wall_top), (x + w, gy), [shade(wall, 0.1), col(wall), shade(wall, -0.22)])))
    c.save(); c.clipPath(wp, doAntiAlias=True)
    if style == 'chalet':  # horizontal logs
        for yy in range(int(wall_top) + 18, int(gy), 26):
            c.drawLine(x, yy, x + w, yy, P(shade_hex(wall, -0.3), 255, stroke=3))
            c.drawLine(x, yy + 4, x + w, yy + 4, P(shade_hex(wall, 0.15), 140, stroke=2))
        # stone base
        c.drawRect(skia.Rect.MakeLTRB(x, gy - h * 0.18, x + w, gy), P('#8d8f9e'))
        for k in range(int(w / 40) + 1):
            c.drawPath(rrect(x + k * 40 + (k % 2) * 10 - 10, gy - h * 0.17, 36, h * 0.08, 6), P('#a3a6b5'))
    elif style == 'timber':
        c.drawRect(skia.Rect.MakeLTRB(x, wall_top, x + w, gy), P('#efe2c8'))
        tb = shade_hex(wall, -0.4)
        for k in range(5):
            xx = x + w * k / 4
            c.drawLine(xx, wall_top, xx, gy, P(tb, 255, stroke=12))
        c.drawLine(x, wall_top + h * 0.5, x + w, wall_top + h * 0.5, P(tb, 255, stroke=12))
        for k in range(4):
            x0 = x + w * k / 4
            c.drawLine(x0, wall_top + h * 0.5, x0 + w / 4, wall_top, P(tb, 255, stroke=9))
    elif style == 'stone':
        for row, yy in enumerate(range(int(wall_top), int(gy), 30)):
            for k in range(-1, int(w / 48) + 2):
                xx = x + k * 48 + (row % 2) * 24 + r.uniform(-4, 4)
                c.drawPath(rrect(xx + 2, yy + 2, 44, 26, 9), P(shade_hex(wall, r.uniform(-0.12, 0.12))))
                c.drawPath(rrect(xx + 2, yy + 2, 44, 26, 9), P(LINE, 90, stroke=2))
    elif style == 'iceland':  # corrugated
        for xx in range(int(x), int(x + w), 14):
            c.drawLine(xx, wall_top, xx, gy, P(shade_hex(wall, -0.18), 255, stroke=3))
            c.drawLine(xx + 5, wall_top, xx + 5, gy, P(shade_hex(wall, 0.12), 180, stroke=2))
    # ambient occlusion under roof
    c.drawRect(skia.Rect.MakeLTRB(x, wall_top, x + w, wall_top + 40), PS(lin((0, wall_top), (0, wall_top + 40), [('#000000', 110), ('#000000', 0)])))
    c.restore()
    # windows
    nwin = max(1, int(w / 150))
    wy = wall_top + h * (0.22 if style != 'stone' else 0.3)
    ww = min(70, w / (nwin * 2.2)); wh = ww * 1.25
    door_x = x + w * 0.5 - w * 0.09
    for k in range(nwin):
        wx = x + (k + 0.5) * w / nwin - ww / 2
        if abs(wx + ww / 2 - (door_x + w * 0.09)) < ww and h < 300: continue
        window(c, wx, wy, ww, wh, lit=r.random() < lit_ratio, L=L, shutters=shutters, k=seed * 10 + k)
    if h > 260:
        for k in range(nwin):
            wx = x + (k + 0.5) * w / nwin - ww / 2
            if abs(wx + ww / 2 - (x + w / 2)) < ww * 0.9: continue
            window(c, wx, wy + wh + 40, ww, wh * 0.9, lit=r.random() < lit_ratio, L=L, shutters=shutters, k=seed * 10 + k + 5)
    # door
    dw, dh = w * 0.18, min(h * 0.5, 150)
    dx = x + w * 0.5 - dw / 2
    dp = _arch(dx, gy - dh, dw, dh)
    c.drawPath(dp, P(LINE, 255, stroke=10)); c.drawPath(dp, PS(lin((dx, gy - dh), (dx + dw, gy), [shade(door_col, 0.15), col(door_col), shade(door_col, -0.3)])))
    c.drawLine(dx + dw / 2, gy - dh + dw / 2, dx + dw / 2, gy, P(LINE, 120, stroke=3))
    c.drawCircle(dx + dw * 0.78, gy - dh * 0.45, 5, P('#f0c64a'))
    if wreath:
        wx_, wy_ = dx + dw / 2, gy - dh * 0.7
        c.drawCircle(wx_, wy_, dw * 0.28, P(LINE, 255, stroke=dw * 0.16))
        c.drawCircle(wx_, wy_, dw * 0.28, P('#2f7d46', 255, stroke=dw * 0.11))
        for k in range(6):
            ang = k * math.pi / 3
            c.drawCircle(wx_ + math.cos(ang) * dw * 0.28, wy_ + math.sin(ang) * dw * 0.28, 4, P('#e03a3a'))
        c.drawPath(path_from([(wx_ - 10, wy_ + dw * 0.25), (wx_ + 10, wy_ + dw * 0.25), (wx_, wy_ + dw * 0.4)], True), P('#d62f3a'))
    # porch light
    glow(c, dx - 18, gy - dh - 10, 60, '#ffbf5e', 120)
    c.drawCircle(dx - 18, gy - dh - 10, 8, P('#fff1b8'))
    if L is not None: L.lamps.append((dx - 18, gy - dh - 10, seed))
    # roof
    if style == 'iceland':
        rp = path_from([(x - over, wall_top + 6), (x + w / 2, wall_top - roof_h), (x + w + over, wall_top + 6)], True)
    elif style == 'stone':
        rp = path_from([(x - over, wall_top + 8), (x + w * 0.12, wall_top - roof_h * 0.85), (x + w * 0.88, wall_top - roof_h * 0.85), (x + w + over, wall_top + 8)], True)
    else:
        rp = path_from([(x - over, wall_top + 10), (x + w / 2, wall_top - roof_h), (x + w + over, wall_top + 10)], True)
    c.drawPath(rp, P(LINE, 255, stroke=10))
    c.drawPath(rp, PS(lin((x, wall_top - roof_h), (x + w, wall_top), [shade(roof, 0.12), col(roof), shade(roof, -0.3)])))
    c.save(); c.clipPath(rp, doAntiAlias=True)
    for k in range(-20, 30):  # shingles / planks
        yy = wall_top - roof_h + k * 22
        c.drawLine(x - over, yy, x + w + over, yy, P(shade_hex(roof, -0.3), 120, stroke=2))
    # thick snow on roof
    if style == 'stone':
        sp = path_from([(x - over, wall_top - roof_h * 0.25), (x + w * 0.12, wall_top - roof_h * 0.85), (x + w * 0.88, wall_top - roof_h * 0.85),
                        (x + w + over, wall_top - roof_h * 0.25)], True, 0.0)
    else:
        sp = path_from([(x - over, wall_top - roof_h * 0.15), (x + w / 2, wall_top - roof_h), (x + w + over, wall_top - roof_h * 0.15),
                        (x + w + over, wall_top - roof_h * 0.35), (x + w / 2, wall_top - roof_h * 0.45 - 30), (x - over, wall_top - roof_h * 0.35)], True, 0.0)
        sp = path_from([(x - over, wall_top - 10), (x + w / 2, wall_top - roof_h), (x + w + over, wall_top - 10),
                        (x + w + over - 30, wall_top - 30), (x + w / 2, wall_top - roof_h + 50), (x - over + 30, wall_top - 30)], True, 0.0)
    c.drawPath(sp, PS(lin((0, wall_top - roof_h), (0, wall_top), ['#ffffff', '#d7e2ff'])))
    c.restore()
    c.drawPath(rp, P(LINE, 255, stroke=5))
    # gable details / balcony (chalet)
    if style == 'chalet':
        c.drawLine(x - over, wall_top + 10, x + w / 2, wall_top - roof_h, P('#5a3420', 255, stroke=14))
        c.drawLine(x + w / 2, wall_top - roof_h, x + w + over, wall_top + 10, P('#5a3420', 255, stroke=14))
        by = wall_top + h * 0.5
        c.drawRect(skia.Rect.MakeLTRB(x - 14, by, x + w + 14, by + 12), P('#5a3420'))
        for xx in range(int(x - 10), int(x + w + 14), 20):
            c.drawLine(xx, by + 12, xx, by + 52, P('#6b3d24', 255, stroke=7))
        c.drawRect(skia.Rect.MakeLTRB(x - 14, by + 50, x + w + 14, by + 60), P('#5a3420'))
        snow_cap(c, [(x - 14, by), (x + w + 14, by)], 12, seed + 3)
        # heart cut-out in gable
        hx, hy = x + w / 2, wall_top - roof_h * 0.35
        c.drawPath(path_from([(hx, hy + 14), (hx - 16, hy - 2), (hx - 8, hy - 14), (hx, hy - 6), (hx + 8, hy - 14), (hx + 16, hy - 2)], True, 0.7), P('#ffd27a'))
    # snow on eaves edge
    if style == 'stone':
        snow_cap(c, [(x - over, wall_top + 8), (x + w + over, wall_top + 8)], 22, seed)
    # string lights along eaves
    if lights:
        n = int(w / 34)
        for k in range(n + 1):
            t = k / n
            bx = lerp(x - over * 0.5, x + w + over * 0.5, t)
            by = wall_top + 16 + 14 * math.sin(math.pi * t * 3) ** 2
            colr = ('#ff4a4a', '#ffd84a', '#4aff8a', '#4ac8ff', '#ff7ad9')[(k + seed) % 5]
            if L is not None: L.bulbs.append((bx, by, colr, k + seed))
            c.drawCircle(bx, by, 5.5, P(colr))
        pth = skia.Path(); pth.moveTo(x - over * 0.5, wall_top + 16)
        for k in range(n + 1):
            t = k / n; pth.lineTo(lerp(x - over * 0.5, x + w + over * 0.5, t), wall_top + 16 + 14 * math.sin(math.pi * t * 3) ** 2)
        c.drawPath(pth, P(LINE, 200, stroke=2))
    # snow drift at base
    drift = path_from([(x - 30, gy + 6), (x + w * 0.2, gy - 16), (x + w * 0.5, gy - 8), (x + w * 0.85, gy - 20), (x + w + 30, gy + 6)], True, 0.8)
    c.drawPath(drift, P('#eef3ff'))
    return (dx, gy - dh, dw, dh)

def church(c, x, gy, w, h, L=None, seed=0, onion=True, wall='#e9dcc2'):
    # tower
    tw = w * 0.45; tx = x + w / 2 - tw / 2; th = h * 1.6
    tp = rrect(tx, gy - th, tw, th, 4)
    c.drawPath(tp, P(LINE, 255, stroke=10)); c.drawPath(tp, PS(lin((tx, 0), (tx + tw, 0), [shade(wall, 0.1), col(wall), shade(wall, -0.25)])))
    # clock
    cx, cy = tx + tw / 2, gy - th + tw * 0.7
    c.drawCircle(cx, cy, tw * 0.28, P(LINE)); c.drawCircle(cx, cy, tw * 0.25, P('#fff4d6'))
    c.drawLine(cx, cy, cx, cy - tw * 0.18, P(LINE, 255, stroke=4)); c.drawLine(cx, cy, cx + tw * 0.12, cy, P(LINE, 255, stroke=4))
    glow(c, cx, cy, tw * 0.6, '#ffd27a', 60)
    window(c, tx + tw * 0.3, gy - th + tw * 1.15, tw * 0.4, tw * 0.6, True, L, arch=True, k=seed + 1)
    # onion dome / spire
    if onion:
        d = path_from([(tx - 6, gy - th), (tx + tw * 0.1, gy - th - tw * 0.6), (tx + tw / 2, gy - th - tw * 1.0), (tx + tw * 0.9, gy - th - tw * 0.6), (tx + tw + 6, gy - th)], True, 0.9)
        c.drawPath(d, P(LINE, 255, stroke=10)); c.drawPath(d, PS(lin((tx, 0), (tx + tw, 0), ['#6fa38a', '#3f7a64', '#244a3c'])))
        sp = path_from([(tx + tw / 2 - 8, gy - th - tw * 0.95), (tx + tw / 2, gy - th - tw * 1.7), (tx + tw / 2 + 8, gy - th - tw * 0.95)], True)
        c.drawPath(sp, P(LINE, 255, stroke=6)); c.drawPath(sp, P('#3f7a64'))
        c.drawLine(tx + tw / 2, gy - th - tw * 1.7, tx + tw / 2, gy - th - tw * 2.0, P('#f0c64a', 255, stroke=5))
        c.drawLine(tx + tw / 2 - 14, gy - th - tw * 1.88, tx + tw / 2 + 14, gy - th - tw * 1.88, P('#f0c64a', 255, stroke=5))
        snow_cap(c, [(tx + tw * 0.1, gy - th - tw * 0.6), (tx + tw / 2, gy - th - tw * 1.0), (tx + tw * 0.9, gy - th - tw * 0.6)], 16, seed)
    # nave
    house(c, x, gy, w, h, 'stone', wall='#b9b2a6', roof='#4a4f6a', L=L, seed=seed + 50, lights=False, wreath=True, chimney=False, door_col='#5a2a20')

def pine(c, x, gy, h, snow=True, col_='#1f4f3a', seed=0, decorated=False, L=None, star=False):
    r = random.Random(seed)
    w = h * 0.42
    c.drawRect(skia.Rect.MakeLTRB(x - h * 0.04, gy - h * 0.12, x + h * 0.04, gy), P('#4a2f22'))
    tiers = 4
    for k in range(tiers):
        t0 = k / tiers
        by = gy - h * 0.1 - h * 0.8 * t0
        tw_ = w * (1 - t0 * 0.75)
        ty = by - h * 0.38
        pts = [(x - tw_, by)]
        for j in range(1, 6):
            u = j / 6
            pts.append((x - tw_ + 2 * tw_ * u, by + (10 if j % 2 else -2)))
        pts += [(x + tw_, by), (x, ty)]
        tp = path_from([(x - tw_, by)] + pts[1:-1] + [(x + tw_, by), (x, ty)], True, 0.25)
        c.drawPath(tp, P(LINE, 255, stroke=8))
        c.drawPath(tp, PS(lin((x - tw_, ty), (x + tw_, by), [shade(col_, 0.15), col(col_), shade(col_, -0.35)])))
        if snow:
            sp = path_from([(x - tw_ * 0.55, by - h * 0.12), (x, ty + 6), (x + tw_ * 0.4, by - h * 0.15), (x + tw_ * 0.1, by - h * 0.1), (x - tw_ * 0.25, by - h * 0.07)], True, 0.7)
            c.drawPath(sp, P('#f4f8ff'))
        if decorated:
            for j in range(int(tw_ / 18)):
                u = r.uniform(-0.8, 0.8)
                bx = x + u * tw_; by_ = by - 14 - (1 - abs(u)) * h * 0.18 * r.random()
                colr = ('#ff4a4a', '#ffd84a', '#4aff8a', '#4ac8ff', '#ff7ad9')[j % 5]
                if L is not None: L.bulbs.append((bx, by_, colr, j + k * 7 + seed))
                if r.random() < 0.4:
                    c.drawCircle(bx, by_, h * 0.022, P(LINE)); c.drawCircle(bx, by_, h * 0.018, P(r.choice(['#d62f3a', '#f2c14e', '#3a7bd5'])))
                    c.drawCircle(bx - 3, by_ - 3, h * 0.006, P('#ffffff'))
                else:
                    c.drawCircle(bx, by_, 5, P(colr))
    if star:
        sx, sy = x, gy - h * 0.92
        glow(c, sx, sy, h * 0.12, '#ffe68a', 200)
        pts = []
        for k in range(10):
            rr = h * (0.05 if k % 2 == 0 else 0.022); ang = -math.pi / 2 + k * math.pi / 5
            pts.append((sx + math.cos(ang) * rr, sy + math.sin(ang) * rr))
        c.drawPath(path_from(pts), P(LINE, 255, stroke=6)); c.drawPath(path_from(pts), P('#ffe066'))
        if L is not None: L.lamps.append((sx, sy, 99))

def lamppost(c, x, gy, h=320, L=None, k=0):
    c.drawLine(x, gy, x, gy - h, P(LINE, 255, stroke=16)); c.drawLine(x, gy, x, gy - h, P('#2c2d3e', 255, stroke=10))
    c.drawPath(rrect(x - 26, gy - h - 60, 52, 60, 8), P(LINE)); c.drawPath(rrect(x - 21, gy - h - 55, 42, 50, 6), P('#ffe7a0'))
    c.drawPath(path_from([(x - 36, gy - h - 58), (x, gy - h - 92), (x + 36, gy - h - 58)], True), P('#2c2d3e'))
    c.drawPath(path_from([(x - 36, gy - h - 62), (x, gy - h - 96), (x + 36, gy - h - 62)], True, 0.3), P('#ffffff'))
    glow(c, x, gy - h - 30, 160, '#ffcf6e', 110)
    if L is not None: L.lamps.append((x, gy - h - 30, k))
    # garland ring
    c.drawCircle(x, gy - h * 0.55, 20, P('#2f7d46', 255, stroke=10)); c.drawCircle(x + 6, gy - h * 0.55 + 16, 7, P('#d62f3a'))

def snowman(c, x, gy, s=1.0, collapse=0.0, seed=0):
    """collapse 0..1 : body balls fall apart"""
    c.save(); c.translate(x, gy); c.scale(s, s)
    co = collapse
    balls = [(0, -60, 64, 0), (0, -165, 48, 1), (0, -245, 36, 2)]
    for i, (bx, by, br, k) in enumerate(balls):
        dx = co * (k - 1) * 90 * (1 if k != 1 else -0.6); dy = co * (-by - br) * min(1, co * 1.3)
        rot = co * (k - 1) * 40
        c.save(); c.translate(bx + dx, by + dy); c.rotate(rot)
        c.drawCircle(0, 0, br, P(LINE)); c.drawCircle(0, 0, br - 4, PS(rad((-br * 0.3, -br * 0.3), br * 1.2, ['#ffffff', '#e2eaff', '#b8c6ea'])))
        if k == 2:
            for sx in (-1, 1): c.drawCircle(sx * 12, -6, 5, P(LINE))
            c.drawPath(path_from([(0, 2), (34, 10), (0, 12)], True), P('#f28a2e'))
            c.drawPath(rrect(-30, -br - 4, 60, 12, 4), P('#2a2340'))
            c.drawPath(rrect(-20, -br - 40, 40, 40, 4), P('#2a2340'))
            c.drawRect(skia.Rect.MakeLTRB(-20, -br - 14, 20, -br - 6), P('#d62f3a'))
        if k == 1:
            for j in range(3): c.drawCircle(0, -20 + j * 18, 4.5, P(LINE))
            c.drawPath(rrect(-46, -br + 2, 92, 16, 8), P('#d62f3a')); c.drawPath(rrect(18, -br + 10, 16, 40, 6), P('#d62f3a'))
        c.restore()
    if co < 0.3:
        for sx in (-1, 1):
            c.drawLine(sx * 40, -170, sx * 105, -215, P('#5a3a28', 255, stroke=7))
    c.restore()

def fence(c, x0, x1, gy, h=80):
    for x in range(int(x0), int(x1), 46):
        pp = path_from([(x, gy), (x, gy - h), (x + 11, gy - h - 14), (x + 22, gy - h), (x + 22, gy)], True)
        c.drawPath(pp, P(LINE, 255, stroke=6)); c.drawPath(pp, P('#8a5a3a'))
        c.drawPath(rrect(x - 2, gy - h - 18, 26, 10, 5), P('#ffffff'))
    for yy in (gy - h * 0.75, gy - h * 0.35):
        c.drawRect(skia.Rect.MakeLTRB(x0, yy - 7, x1, yy + 7), P(LINE)); c.drawRect(skia.Rect.MakeLTRB(x0, yy - 5, x1, yy + 5), P('#9a6a48'))

def ground(c, w, gy, h, col_top='#eef3ff', col_bot='#b9c7ec', seed=4, footprints=True):
    pth = skia.Path(); pth.moveTo(0, gy)
    r = random.Random(seed)
    for x in range(0, w + 60, 60): pth.lineTo(x, gy + r.uniform(-6, 6))
    pth.lineTo(w, gy + h); pth.lineTo(0, gy + h); pth.close()
    c.drawPath(pth, PS(lin((0, gy), (0, gy + h), [col_top, col_bot])))
    # soft blue shadows / ruts
    for k in range(int(w / 260)):
        x = r.uniform(0, w); y = gy + r.uniform(30, h * 0.8)
        c.drawOval(skia.Rect.MakeXYWH(x, y, r.uniform(120, 300), r.uniform(10, 24)), P('#9fb0dd', 90))
    if footprints:
        for k in range(int(w / 70)):
            x = k * 70 + r.uniform(-8, 8); y = gy + 40 + 18 * math.sin(k * 0.6) + (14 if k % 2 else 0)
            c.drawOval(skia.Rect.MakeXYWH(x, y, 22, 10), P('#a9b8e2', 140))

def string_lights(c, x0, y0, x1, y1, sag, L, seed=0, n=14):
    pth = skia.Path()
    for k in range(n + 1):
        t = k / n; x = lerp(x0, x1, t); y = lerp(y0, y1, t) + sag * 4 * t * (1 - t)
        if k == 0: pth.moveTo(x, y)
        else: pth.lineTo(x, y)
        colr = ('#ff4a4a', '#ffd84a', '#4aff8a', '#4ac8ff', '#ff7ad9')[(k + seed) % 5]
        if k not in (0, n):
            L.bulbs.append((x, y + 8, colr, k + seed)); c.drawCircle(x, y + 8, 6, P(colr))
    c.drawPath(pth, P(LINE, 220, stroke=2.5))

# ------------------------------------------------------------------ dynamic lights
def draw_lights(c, L, t, pulse=0.0, bulb_scale=1.0, alpha=1.0, beat=None):
    for (x, y, colr, k) in L.bulbs:
        tw = 0.65 + 0.35 * math.sin(t * 5 + k * 1.7)
        if beat is not None:
            # chase pattern stepping on the beat
            tw = 0.45 + 0.55 * (1.0 if (int(beat) + k) % 3 == 0 else 0.35)
        a = clamp((tw + pulse * 0.5) * alpha, 0, 1)
        glow(c, x, y, 26 * bulb_scale * (1 + pulse * 0.6), colr, int(200 * a))
        c.drawCircle(x, y, 4.5 * bulb_scale, P('#ffffff', int(230 * a)))
    for (x, y, w, h, k) in L.windows:
        f = 0.75 + 0.25 * math.sin(t * 2.3 + k) * math.sin(t * 3.7 + k * 0.5) + pulse * 0.35
        glow(c, x + w / 2, y + h / 2, max(w, h) * 1.1, '#ffb347', int(80 * clamp(f * alpha, 0, 1.4) / 1.4))
    for (x, y, k) in L.lamps:
        glow(c, x, y, 120 + 30 * pulse, '#ffd27a', int(90 * alpha * (0.8 + 0.4 * pulse)))

def draw_smoke(c, L, t, alpha=1.0):
    for (x, y, k) in L.smoke:
        for j in range(6):
            ph = (t * 0.35 + j / 6 + k * 0.13) % 1.0
            sx = x + math.sin(ph * 5 + k) * 14 + ph * 60
            sy = y - ph * 220
            glow(c, sx, sy, 24 + ph * 40, '#c8d0ee', int(110 * (1 - ph) * alpha))

# ------------------------------------------------------------------ snowfall
class Snow:
    def __init__(self, n=260, seed=7, w=W, h=H):
        r = np.random.default_rng(seed)
        self.x = r.uniform(-100, w + 100, n); self.y0 = r.uniform(0, h, n)
        self.d = r.choice([0.35, 0.6, 1.0, 1.7], n, p=[0.4, 0.3, 0.2, 0.1])
        self.ph = r.uniform(0, 6.28, n); self.w = w; self.h = h
    def draw(self, c, t, wind=0.0, alpha=1.0, burst=0.0, layer=None, speed=1.0):
        for i in range(len(self.x)):
            d = self.d[i]
            if layer == 'back' and d > 0.7: continue
            if layer == 'front' and d <= 0.7: continue
            sp = 60 + 110 * d
            y = (self.y0[i] + t * sp * speed) % (self.h + 80) - 40
            x = (self.x[i] + math.sin(t * 0.9 + self.ph[i]) * 22 * d + wind * t * 80 * d) % (self.w + 200) - 100
            r_ = 2.2 * d + 1.2
            if d >= 1.7:
                c.drawCircle(x, y, r_ * 2.2, P('#ffffff', int(90 * alpha), blur=r_ * 1.2))
            else:
                c.drawCircle(x, y, r_, P('#ffffff', int((140 + 80 * d) * alpha / 1.2)))

def snow_burst(c, cx, cy, t, t0, n=40, spread=500, seed=0, color='#ffffff', size=1.0):
    if t < t0 or t > t0 + 1.2: return
    x_ = t - t0; r = random.Random(seed)
    for i in range(n):
        ang = r.uniform(0, 2 * math.pi); v = r.uniform(0.3, 1.0) * spread
        px = cx + math.cos(ang) * v * (1 - math.exp(-x_ * 4)); py = cy + math.sin(ang) * v * (1 - math.exp(-x_ * 4)) + 260 * x_ * x_
        a = int(255 * clamp(1 - x_ / 1.2))
        c.drawCircle(px, py, r.uniform(3, 9) * size * (1 - x_ * 0.5), P(color, a))

def sparkle(c, x, y, r_, a=255, colr='#fff6c8'):
    pts = []
    for k in range(8):
        rr = r_ if k % 2 == 0 else r_ * 0.22; ang = k * math.pi / 4
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    glow(c, x, y, r_ * 1.4, colr, int(a * 0.6))
    c.drawPath(path_from(pts), P(colr, a))
