"""Painted gothic environments (layered for parallax) + animated environment elements."""
import math
from core import *
from core import _hash

_CACHE = {}


class Cam:
    def __init__(self, x, y, zoom=1.0, rot=0.0, ref=(0, 0)):
        self.x, self.y, self.zoom, self.rot, self.ref = x, y, zoom, rot, ref

    def apply(self, c, d=1.0):
        rx, ry = self.ref
        cx = rx + (self.x - rx) * d
        cy = ry + (self.y - ry) * d
        z = 1 + (self.zoom - 1) * (0.35 + 0.65 * d) if d < 1 else self.zoom * (1 + (d - 1) * 0.25)
        c.translate(W / 2, H / 2)
        if self.rot:
            c.rotate(math.degrees(self.rot) * min(1, d + 0.3))
        c.scale(z, z)
        c.translate(-cx, -cy)


def surface(w, h):
    s = skia.Surface(int(w), int(h))
    s.getCanvas().clear(skia.ColorTRANSPARENT)
    return s


def cached(key, fn):
    if key not in _CACHE:
        _CACHE[key] = fn()
    return _CACHE[key]


def draw_img(c, img, x, y):
    c.drawImage(img, x, y, skia.SamplingOptions(skia.FilterMode.kLinear), None)


# ------------------------------------------------------------------ generic painted elements
def sky(c, x0, y0, w, h, cols, stars=0, seed=1):
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), lin_grad((0, y0), (0, y0 + h), cols))
    r = rnd(seed)
    for i in range(stars):
        x, y = r.uniform(x0, x0 + w), r.uniform(y0, y0 + h * 0.6)
        s = r.uniform(0.8, 2.6)
        c.drawPath(ellipse(x, y, s, s), fill('#fff6dc', r.uniform(0.3, 0.9)))


def moon(c, x, y, r, glow=1.0):
    c.drawPath(ellipse(x, y, r * 3.2, r * 3.2), rad_grad((x, y), r * 3.2, [hexc('#f6e7b8', 0.35 * glow),
                                                                          hexc('#c9b6d8', 0.12 * glow),
                                                                          hexc('#c9b6d8', 0.0)]))
    c.drawPath(ellipse(x, y, r, r), rad_grad((x - r * 0.3, y - r * 0.3), r * 1.3, ['#fffbe8', '#f1dfae', '#d8bf86']))
    rr = rnd(77)
    for i in range(9):
        a, d = rr.uniform(0, 6.28), rr.uniform(0, 0.75)
        cr = rr.uniform(0.05, 0.16) * r
        c.drawPath(ellipse(x + math.cos(a) * d * r, y + math.sin(a) * d * r, cr, cr), fill('#c6ad78', 0.45))
    c.drawPath(ellipse(x, y, r, r), stroke('#8a7450', 3, 0.6))


def cloud(c, x, y, w, col, a=0.8):
    for k in range(5):
        cx = x + (k - 2) * w * 0.18
        cy = y + math.sin(k * 1.7) * w * 0.04
        rr = w * (0.18 + 0.06 * math.cos(k * 2.1))
        c.drawPath(ellipse(cx, cy, rr * 1.4, rr * 0.7), fill(col, a))
    c.drawPath(ellipse(x, y + w * 0.08, w * 0.55, w * 0.1), fill(col, a))


def house(c, x, base, w, h, r, wall='#d8c7a3', roof='#6e2f26', lit=0.7, frame=0, light_on=1.0):
    """timber-framed medieval house, base = ground y"""
    top = base - h
    # jetty upper floor
    c.drawRect(skia.Rect.MakeXYWH(x, top + h * 0.45, w, h * 0.55), fill(wall))
    c.drawRect(skia.Rect.MakeXYWH(x - 12, top, w + 24, h * 0.47), fill(wall))
    # timber
    tc = '#3a2618'
    for rect in [(x, top + h * 0.45, w, h * 0.55), (x - 12, top, w + 24, h * 0.47)]:
        c.drawRect(skia.Rect.MakeXYWH(*rect), stroke(tc, 9))
    n = max(2, int(w / 70))
    for i in range(n + 1):
        xx = x - 12 + (w + 24) * i / n
        c.drawLine(xx, top, xx, top + h * 0.47, stroke(tc, 8))
        if i < n:
            x2 = x - 12 + (w + 24) * (i + 1) / n
            if r.random() < 0.6:
                c.drawLine(xx, top + h * 0.47, x2, top, stroke(tc, 6))
    c.drawLine(x - 12, top + h * 0.235, x + w + 12, top + h * 0.235, stroke(tc, 6))
    # roof
    rh = h * r.uniform(0.45, 0.75)
    rp = poly([(x - 34, top + 6), (x + w / 2, top - rh), (x + w + 34, top + 6)])
    c.drawPath(rp, fill(roof))
    with Save(c):
        c.clipPath(rp, doAntiAlias=True)
        for k in range(int(rh / 18) + 2):
            yy = top - rh + k * 18
            c.drawLine(x - 40, yy, x + w + 40, yy, stroke('#000000', 2, 0.25))
        c.drawRect(skia.Rect.MakeXYWH(x + w / 2, top - rh, w, rh + 10), fill('#000000', 0.22))
    c.drawPath(rp, stroke(INK, 5))
    # chimney
    if r.random() < 0.5:
        cx = x + w * r.uniform(0.6, 0.8)
        c.drawRect(skia.Rect.MakeXYWH(cx, top - rh * 0.7, 26, rh * 0.5), fill('#5a4034'))
        c.drawRect(skia.Rect.MakeXYWH(cx, top - rh * 0.7, 26, rh * 0.5), stroke(INK, 4))
    # windows
    for fl, (yy, hh) in enumerate([(top + h * 0.08, h * 0.16), (top + h * 0.55, h * 0.18)]):
        for i in range(n):
            if r.random() < 0.25:
                continue
            ww = (w + 24) / n * 0.42
            xx = x - 12 + (w + 24) * (i + 0.5) / n - ww / 2
            on = r.random() < lit
            col = '#ffcf6a' if on else '#1d2236'
            wr = skia.Rect.MakeXYWH(xx, yy, ww, hh)
            if on:
                c.drawRect(skia.Rect.MakeXYWH(xx - 25, yy - 25, ww + 50, hh + 50),
                           fill('#ffb347', 0.18 * light_on, blur=18))
            c.drawRect(wr, fill(col if light_on > 0.5 or not on else '#1d2236'))
            c.drawLine(xx + ww / 2, yy, xx + ww / 2, yy + hh, stroke(tc, 4))
            c.drawLine(xx, yy + hh / 2, xx + ww, yy + hh / 2, stroke(tc, 4))
            c.drawRect(wr, stroke(INK, 4))
    # door
    dw = min(70, w * 0.3)
    dx = x + w * r.uniform(0.15, 0.6)
    dp = skia.Path()
    dp.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(dx, base - 130, dw, 130), dw / 2, dw / 2))
    c.drawPath(dp, fill('#3b2414'))
    c.drawPath(dp, stroke(INK, 4))
    # outline
    c.drawRect(skia.Rect.MakeXYWH(x, top + h * 0.45, w, h * 0.55), stroke(INK, 4))


def gravestone(c, x, base, w, h, kind, tilt, r, moss=0.4):
    with Save(c):
        c.rotate(tilt, x, base)
        if kind == 0:
            p = skia.Path()
            p.moveTo(x - w / 2, base)
            p.lineTo(x - w / 2, base - h + w / 2)
            p.arcTo(skia.Rect.MakeXYWH(x - w / 2, base - h, w, w), 180, 180, False)
            p.lineTo(x + w / 2, base)
            p.close()
        elif kind == 1:
            t = w * 0.28
            p = poly([(x - t / 2, base), (x - t / 2, base - h * 0.62), (x - w / 2, base - h * 0.62),
                      (x - w / 2, base - h * 0.62 - t), (x - t / 2, base - h * 0.62 - t), (x - t / 2, base - h),
                      (x + t / 2, base - h), (x + t / 2, base - h * 0.62 - t), (x + w / 2, base - h * 0.62 - t),
                      (x + w / 2, base - h * 0.62), (x + t / 2, base - h * 0.62), (x + t / 2, base)])
        else:
            p = poly([(x - w / 2, base), (x - w / 2, base - h * 0.8), (x - w * 0.3, base - h), (x + w * 0.3, base - h),
                      (x + w / 2, base - h * 0.8), (x + w / 2, base)])
        c.drawPath(p, lin_grad((x - w / 2, 0), (x + w / 2, 0), ['#a9a7b4', '#7c7a8c', '#4a4858']))
        with Save(c):
            c.clipPath(p, doAntiAlias=True)
            c.drawPath(ellipse(x - w * 0.2, base - h * 0.15, w * 0.5, h * 0.3), fill('#4f6a3a', moss))
            if kind != 1:
                for k in range(3):
                    c.drawLine(x - w * 0.25, base - h * (0.55 - k * 0.1), x + w * 0.25, base - h * (0.55 - k * 0.1),
                               stroke('#3a3848', 3, 0.7))
            c.drawLine(x + w * 0.1, base - h, x - w * 0.05, base - h * 0.6, stroke('#2a2836', 2.5, 0.7))
        c.drawPath(p, stroke(INK, 5))


def tree(c, x, base, h, r, col='#17142a'):
    def branch(x0, y0, a, L, wdt, depth):
        x1, y1 = x0 + math.cos(a) * L, y0 + math.sin(a) * L
        bp = skia.Path()
        bp.moveTo(x0, y0)
        bp.quadTo((x0 + x1) / 2 + r.uniform(-1, 1) * L * 0.2, (y0 + y1) / 2, x1, y1)
        c.drawPath(bp, stroke(col, wdt))
        if depth > 0:
            for k in range(2 + (depth > 2)):
                branch(x1, y1, a + r.uniform(-0.75, 0.75), L * r.uniform(0.55, 0.78), wdt * 0.62, depth - 1)
    branch(x, base, -math.pi / 2 + r.uniform(-0.15, 0.15), h * 0.38, h * 0.07, 5)


def cathedral(c, x, base, s, col='#1c1a33', lit=1.0, rose=True, detail=True):
    """gothic cathedral facade, x = center, s = scale"""
    def R(a, b, w, h):
        c.drawRect(skia.Rect.MakeXYWH(x + a * s, base - b * s, w * s, h * s), fill(col))
    # towers
    for sx in (-1, 1):
        tx = x + sx * 220 * s
        c.drawRect(skia.Rect.MakeXYWH(tx - 80 * s, base - 820 * s, 160 * s, 820 * s), fill(col))
        sp = poly([(tx - 92 * s, base - 820 * s), (tx, base - 1250 * s), (tx + 92 * s, base - 820 * s)])
        c.drawPath(sp, fill(col))
        for k in range(3):
            wy = base - (700 - k * 220) * s
            wp = skia.Path()
            wp.moveTo(tx - 22 * s, wy + 90 * s)
            wp.lineTo(tx - 22 * s, wy + 20 * s)
            wp.quadTo(tx, wy - 20 * s, tx + 22 * s, wy + 20 * s)
            wp.lineTo(tx + 22 * s, wy + 90 * s)
            wp.close()
            c.drawPath(wp, fill('#ffcf6a' if (k + (sx > 0)) % 2 == 0 and lit > 0 else '#0e0d1c', 0.9 * lit + 0.1))
        # pinnacles
        for px in (-80, 80):
            c.drawPath(poly([(tx + px * s - 12 * s, base - 820 * s), (tx + px * s, base - 900 * s),
                             (tx + px * s + 12 * s, base - 820 * s)]), fill(col))
    # nave
    c.drawRect(skia.Rect.MakeXYWH(x - 140 * s, base - 640 * s, 280 * s, 640 * s), fill(col))
    c.drawPath(poly([(x - 150 * s, base - 640 * s), (x, base - 820 * s), (x + 150 * s, base - 640 * s)]), fill(col))
    if rose:
        rc = (x, base - 470 * s)
        c.drawPath(ellipse(rc[0], rc[1], 95 * s, 95 * s), fill('#ffb347', 0.25 * lit, blur=30 * s))
        c.drawPath(ellipse(rc[0], rc[1], 82 * s, 82 * s), fill('#2b1c4a'))
        cols = ['#c8303c', '#3b62c4', '#e6b23c', '#3a9a5c']
        for k in range(12):
            a0 = k * math.pi / 6
            pp = skia.Path()
            pp.moveTo(*rc)
            pp.arcTo(skia.Rect.MakeXYWH(rc[0] - 76 * s, rc[1] - 76 * s, 152 * s, 152 * s), math.degrees(a0), 30,
                     False)
            pp.close()
            c.drawPath(pp, fill(cols[k % 4], 0.35 + 0.6 * lit))
            c.drawPath(pp, stroke('#120d1c', 3 * s))
        c.drawPath(ellipse(rc[0], rc[1], 22 * s, 22 * s), fill('#ffe39a', 0.4 + 0.6 * lit))
        c.drawPath(ellipse(rc[0], rc[1], 82 * s, 82 * s), stroke('#120d1c', 6 * s))
    # portal
    pp = skia.Path()
    pp.moveTo(x - 75 * s, base)
    pp.lineTo(x - 75 * s, base - 170 * s)
    pp.quadTo(x - 70 * s, base - 300 * s, x, base - 330 * s)
    pp.quadTo(x + 70 * s, base - 300 * s, x + 75 * s, base - 170 * s)
    pp.lineTo(x + 75 * s, base)
    pp.close()
    c.drawPath(pp, fill('#0b0a14'))
    c.drawPath(pp, fill('#ff9a3c', 0.25 * lit))


def cobbles(c, x0, y0, w, h, r, col='#5a5266', dk='#2e2a38', persp=True):
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), lin_grad((0, y0), (0, y0 + h), [dk, col]))
    rows = 26
    yy = y0
    for i in range(rows):
        u = i / rows
        rh = (8 + 40 * u ** 1.4) if persp else 30
        sw = rh * 2.0
        off = r.uniform(0, sw)
        xx = x0 - off
        while xx < x0 + w:
            ww = sw * r.uniform(0.75, 1.15)
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(xx + 2, yy + 2, ww - 4, rh - 3), rh * 0.4, rh * 0.4)
            p = skia.Path()
            p.addRRect(rr)
            v = r.uniform(-0.12, 0.12)
            c.drawPath(p, fill(tohex(col, '#ffffff', 0.08 + v) if v > 0 else tohex(col, '#000000', -v)))
            c.drawPath(p, stroke('#1a1620', 1.8, 0.8))
            xx += ww
        yy += rh
        if yy > y0 + h:
            break


# ================================================================== ENVIRONMENT BUILDERS
def cemetery_layers():
    def build():
        L = {}
        EW, EH = 2600, 3000
        # sky
        s = surface(EW, EH)
        c = s.getCanvas()
        sky(c, 0, 0, EW, EH, ['#0b1030', '#1d2550', '#4a3a6a', '#7a5a7a'], 260, 3)
        moon(c, 1300, 820, 300)
        L['sky'] = s.makeImageSnapshot()
        # far: hills + church + town silhouettes
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(11)
        hp = smooth_poly([(0, 1900), (400, 1780), (900, 1840), (1400, 1760), (1900, 1830), (2600, 1770),
                          (2600, 3000), (0, 3000)], True, 0.3)
        c.drawPath(hp, fill('#262447'))
        cathedral(c, 1850, 1840, 0.55, '#1f1d3a', 1.0)
        for i in range(10):
            x = 60 + i * 130 + r.uniform(-30, 30)
            if 1550 < x < 2150:
                continue
            house(c, x, 1860, r.uniform(90, 130), r.uniform(150, 230), r, '#3a3456', '#2a2240', 0.4)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, EW, EH), fill('#2a2a5a', 0.18))
        L['far'] = s.makeImageSnapshot()
        # mid: trees, fence, gravestones
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(12)
        gp = smooth_poly([(0, 2050), (700, 2000), (1300, 2040), (2000, 1990), (2600, 2030), (2600, 3000), (0, 3000)],
                         True, 0.3)
        c.drawPath(gp, lin_grad((0, 2000), (0, 2600), ['#2c3a3a', '#182222']))
        tree(c, 240, 2060, 900, r, '#14122a')
        tree(c, 2380, 2040, 1000, r, '#14122a')
        tree(c, 700, 2030, 520, r, '#1a1830')
        # iron fence
        for i in range(60):
            x = i * 45
            c.drawLine(x, 2010, x, 1880, stroke('#0e0c18', 6))
            c.drawPath(poly([(x - 9, 1890), (x, 1862), (x + 9, 1890)]), fill('#0e0c18'))
        c.drawLine(0, 1910, EW, 1910, stroke('#0e0c18', 6))
        c.drawLine(0, 1990, EW, 1990, stroke('#0e0c18', 6))
        for i in range(16):
            x = r.uniform(0, EW)
            gravestone(c, x, 2060 + r.uniform(0, 60), r.uniform(70, 110), r.uniform(110, 170), r.integers(0, 3),
                       r.uniform(-8, 8), r, 0.3)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, EW, EH), fill('#20204a', 0.12))
        L['mid'] = s.makeImageSnapshot()
        # ground (main plane)
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(13)
        g = smooth_poly([(0, 2150), (900, 2120), (1700, 2140), (2600, 2120), (2600, 3000), (0, 3000)], True, 0.3)
        c.drawPath(g, lin_grad((0, 2120), (0, 3000), ['#3a4a3c', '#2a3a2e', '#1a2420']))
        # dirt mounds (graves)
        for x in (520, 1300, 2080):
            c.drawPath(ellipse(x, 2420, 230, 60), fill('#3a2e26'))
            c.drawPath(ellipse(x, 2410, 210, 45), fill('#4a3a2e'))
        for i in range(500):
            x, y = r.uniform(0, EW), r.uniform(2140, 3000)
            hh = r.uniform(8, 22) * (0.5 + (y - 2140) / 900)
            gl = skia.Path()
            gl.moveTo(x, y)
            gl.quadTo(x + r.uniform(-6, 6), y - hh * 0.6, x + r.uniform(-10, 10), y - hh)
            c.drawPath(gl, stroke(r.choice(['#4e6a46', '#3c5438', '#5f7a4e']), 2.5))
        for (x, kind) in ((300, 0), (900, 2), (1700, 1), (2300, 0)):
            gravestone(c, x, 2330, 160, 260, kind, r.uniform(-7, 7), r, 0.5)
        L['ground'] = s.makeImageSnapshot()
        return L
    return cached('cemetery', build)


def throne_layers():
    def build():
        L = {}
        EW, EH = 2400, 3000
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(21)
        # stone walls
        c.drawRect(skia.Rect.MakeXYWH(0, 0, EW, EH), lin_grad((0, 0), (0, EH), ['#2a2030', '#3d2e38', '#241a22']))
        for yy in range(0, 2300, 70):
            off = (yy // 70 % 2) * 70
            for xx in range(-off, EW, 140):
                c.drawRect(skia.Rect.MakeXYWH(xx + 3, yy + 3, 134, 64), fill(tohex('#4a3a44', '#000000',
                                                                                  r.uniform(0, 0.35))))
        # arches / pillars
        for px in (300, 900, 1500, 2100):
            c.drawRect(skia.Rect.MakeXYWH(px - 70, 300, 140, 2000), lin_grad((px - 70, 0), (px + 70, 0),
                                                                             ['#5a4a54', '#7a6672', '#3a2c36']))
            c.drawRect(skia.Rect.MakeXYWH(px - 70, 300, 140, 2000), stroke(INK, 5))
        # stained glass windows between pillars
        for wx in (600, 1800):
            wp = skia.Path()
            wp.moveTo(wx - 150, 1300)
            wp.lineTo(wx - 150, 700)
            wp.quadTo(wx - 140, 420, wx, 360)
            wp.quadTo(wx + 140, 420, wx + 150, 700)
            wp.lineTo(wx + 150, 1300)
            wp.close()
            c.drawPath(wp, fill('#ffcf6a', 0.25, blur=40))
            c.drawPath(wp, fill('#2a2040'))
            with Save(c):
                c.clipPath(wp, doAntiAlias=True)
                cols = ['#b3242f', '#2e56b0', '#e2b13a', '#2f8a52', '#7a3aa0']
                for i in range(12):
                    for j in range(20):
                        q = poly([(wx - 160 + i * 30, 360 + j * 50), (wx - 130 + i * 30, 360 + j * 50 + 15),
                                  (wx - 140 + i * 30, 410 + j * 50), (wx - 165 + i * 30, 400 + j * 50)])
                        c.drawPath(q, fill(cols[r.integers(0, 5)], 0.85))
                        c.drawPath(q, stroke('#120d18', 3))
            c.drawPath(wp, stroke(INK, 10))
        # banners
        for bx in (900, 1500):
            bp = poly([(bx - 110, 450), (bx + 110, 450), (bx + 110, 1200), (bx, 1300), (bx - 110, 1200)])
            c.drawPath(bp, fill(BURG))
            c.drawPath(bp, stroke(INK, 5))
            c.drawPath(poly([(bx - 80, 600), (bx + 80, 600), (bx + 70, 820), (bx, 900), (bx - 70, 820)]), fill(GOLD))
            c.drawPath(ellipse(bx, 720, 34, 34), fill(BURG))
        # floor
        c.drawRect(skia.Rect.MakeXYWH(0, 2050, EW, 950), lin_grad((0, 2050), (0, 3000), ['#3a2c2a', '#5a4436']))
        for i in range(-10, 30):
            c.drawLine(1200 + i * 60, 2050, 1200 + i * 260 - 2600, 3000, stroke('#2a1e1a', 3))
        for k in range(12):
            yy = 2050 + (k / 12) ** 1.6 * 950
            c.drawLine(0, yy, EW, yy, stroke('#2a1e1a', 3))
        # red carpet + steps
        c.drawPath(poly([(1050, 2050), (1350, 2050), (1700, 3000), (700, 3000)]), fill('#8a1626'))
        c.drawPath(poly([(1050, 2050), (1350, 2050), (1700, 3000), (700, 3000)]), stroke(GOLD, 8))
        for k in range(3):
            c.drawRect(skia.Rect.MakeXYWH(700 - k * 60, 1980 + k * 40, 1000 + k * 120, 40), fill('#5a4a52'))
            c.drawRect(skia.Rect.MakeXYWH(700 - k * 60, 1980 + k * 40, 1000 + k * 120, 40), stroke(INK, 4))
        # gold piles
        for gx, gy in ((420, 2200), (1980, 2230), (300, 2500), (2150, 2550)):
            for k in range(140):
                a = r.uniform(0, math.pi)
                d = r.uniform(0, 1) ** 0.6
                x = gx + math.cos(a) * d * 160
                y = gy - math.sin(a) * d * 90
                c.drawPath(ellipse(x, y, 16, 9), fill(r.choice([GOLD, '#f0c75a', '#b8862a'])))
                c.drawPath(ellipse(x, y, 16, 9), stroke('#6a4a12', 1.5))
        L['room'] = s.makeImageSnapshot()
        # throne (separate so king can sit in front of back)
        s = surface(EW, EH)
        c = s.getCanvas()
        tx, ty = 1200, 1980
        back = smooth_poly([(tx - 230, ty), (tx - 240, ty - 700), (tx - 160, ty - 900), (tx, ty - 1010),
                            (tx + 160, ty - 900), (tx + 240, ty - 700), (tx + 230, ty)], True, 0.2)
        c.drawPath(back, stroke(INK, 10))
        c.drawPath(back, lin_grad((tx - 240, 0), (tx + 240, 0), ['#f3d27a', GOLD, GOLD_DK]))
        inner = smooth_poly([(tx - 160, ty - 300), (tx - 165, ty - 700), (tx, ty - 860), (tx + 165, ty - 700),
                             (tx + 160, ty - 300)], True, 0.2)
        c.drawPath(inner, fill('#8a1626'))
        c.drawPath(inner, stroke(INK, 6))
        for k in range(30):
            a = k * 0.21
            c.drawPath(ellipse(tx + math.cos(a * 3) * 90, ty - 600 + math.sin(a * 2) * 160, 6, 6), fill(GOLD, 0.5))
        seat = skia.Rect.MakeXYWH(tx - 260, ty - 330, 520, 120)
        c.drawRect(seat, fill('#a01a2c'))
        c.drawRect(seat, stroke(INK, 6))
        for sx in (-1, 1):
            arm = skia.Rect.MakeXYWH(tx + sx * 250 - 45, ty - 440, 90, 440)
            c.drawRect(arm, lin_grad((tx + sx * 250 - 45, 0), (tx + sx * 250 + 45, 0), ['#f3d27a', GOLD_DK]))
            c.drawRect(arm, stroke(INK, 6))
            c.drawPath(ellipse(tx + sx * 250, ty - 450, 55, 55), fill(GOLD))
            c.drawPath(ellipse(tx + sx * 250, ty - 450, 55, 55), stroke(INK, 6))
        L['throne'] = s.makeImageSnapshot()
        return L
    return cached('throne', build)


def courtyard_layers():
    def build():
        L = {}
        EW, EH = 2600, 3000
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(31)
        sky(c, 0, 0, EW, 2000, ['#0d1232', '#28305a', '#5a4670'], 180, 5)
        moon(c, 1900, 520, 170)
        # castle walls with crenellations and towers
        c.drawRect(skia.Rect.MakeXYWH(0, 1000, EW, 1100), lin_grad((0, 1000), (0, 2100), ['#4a4458', '#2e2a3a']))
        for x in range(0, EW, 90):
            c.drawRect(skia.Rect.MakeXYWH(x, 940, 55, 70), fill('#4a4458'))
        for yy in range(1010, 2100, 60):
            off = (yy // 60 % 2) * 60
            for xx in range(-off, EW, 120):
                c.drawRect(skia.Rect.MakeXYWH(xx, yy, 120, 60), stroke('#26222e', 3))
        for tx in (250, 2350):
            c.drawRect(skia.Rect.MakeXYWH(tx - 170, 600, 340, 1500), lin_grad((tx - 170, 0), (tx + 170, 0),
                                                                             ['#5a546a', '#3a3448']))
            c.drawPath(poly([(tx - 200, 600), (tx, 280), (tx + 200, 600)]), fill('#3a2040'))
            c.drawPath(poly([(tx - 200, 600), (tx, 280), (tx + 200, 600)]), stroke(INK, 6))
            c.drawRect(skia.Rect.MakeXYWH(tx - 170, 600, 340, 1500), stroke(INK, 6))
            for k in range(3):
                c.drawRect(skia.Rect.MakeXYWH(tx - 20, 750 + k * 330, 40, 100), fill('#ffcf6a'))
        # gate
        gp = skia.Path()
        gp.moveTo(1050, 2100)
        gp.lineTo(1050, 1500)
        gp.quadTo(1300, 1250, 1550, 1500)
        gp.lineTo(1550, 2100)
        gp.close()
        c.drawPath(gp, fill('#120f18'))
        with Save(c):
            c.clipPath(gp)
            for k in range(10):
                c.drawLine(1050 + k * 55, 1250, 1050 + k * 55, 2100, stroke('#3a3440', 10))
            for k in range(10):
                c.drawLine(1050, 1330 + k * 80, 1550, 1330 + k * 80, stroke('#3a3440', 10))
        c.drawPath(gp, stroke(INK, 8))
        # ground
        cobbles(c, 0, 2100, EW, 900, r, '#6a6070', '#363040')
        L['main'] = s.makeImageSnapshot()
        return L
    return cached('courtyard', build)


def treasure_layers():
    def build():
        L = {}
        EW, EH = 2400, 3000
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(41)
        # wooden plank walls
        c.drawRect(skia.Rect.MakeXYWH(0, 0, EW, EH), fill('#3a2416'))
        for x in range(0, EW, 110):
            c.drawRect(skia.Rect.MakeXYWH(x, 0, 110, 2100), fill(tohex('#5a3820', '#2a160c', r.uniform(0, 0.5))))
            c.drawLine(x, 0, x, 2100, stroke('#1e120a', 5))
            for k in range(3):
                y = r.uniform(100, 2000)
                c.drawPath(ellipse(x + 55, y, 9, 14), fill('#2a160c'))
        # small barred window with moonlight
        c.drawRect(skia.Rect.MakeXYWH(1500, 500, 300, 260), fill('#2a3a6a'))
        moon(c, 1680, 590, 50, 0.6)
        for k in range(4):
            c.drawLine(1500 + k * 75 + 37, 500, 1500 + k * 75 + 37, 760, stroke('#111111', 12))
        c.drawRect(skia.Rect.MakeXYWH(1500, 500, 300, 260), stroke(INK, 14))
        # shelves with sacks & coins
        for sy in (900, 1300):
            c.drawRect(skia.Rect.MakeXYWH(150, sy, 900, 36), fill('#6a4224'))
            c.drawRect(skia.Rect.MakeXYWH(150, sy, 900, 36), stroke(INK, 5))
            for k in range(6):
                x = 200 + k * 140
                sk = smooth_poly([(x, sy), (x + 110, sy), (x + 100, sy - 120), (x + 70, sy - 150), (x + 40, sy - 150),
                                  (x + 10, sy - 120)], True, 0.4)
                c.drawPath(sk, fill('#a88a5a'))
                c.drawPath(sk, stroke(INK, 4))
                c.drawLine(x + 30, sy - 135, x + 80, sy - 135, stroke('#5a3a1a', 6))
                c.drawPath(ellipse(x + 55, sy - 60, 20, 20), fill(GOLD))
        # door (left) with iron bands + lock
        d = skia.Rect.MakeXYWH(1900 - 1700, 1150, 420, 950)
        c.drawRect(skia.Rect.MakeXYWH(150, 1150, 460, 950), fill('#2a170c'))
        for k in range(5):
            c.drawRect(skia.Rect.MakeXYWH(170 + k * 86, 1170, 80, 930), fill('#6a4020'))
        for yy in (1300, 1650, 1950):
            c.drawRect(skia.Rect.MakeXYWH(150, yy, 460, 34), fill('#2c2c34'))
            for k in range(6):
                c.drawPath(ellipse(180 + k * 80, yy + 17, 7, 7), fill('#8a8a96'))
        c.drawRect(skia.Rect.MakeXYWH(150, 1150, 460, 950), stroke(INK, 8))
        # floor
        c.drawRect(skia.Rect.MakeXYWH(0, 2100, EW, 900), lin_grad((0, 2100), (0, 3000), ['#4a3020', '#6a4428']))
        for k in range(14):
            c.drawLine(k * 200 - 300, 3000, 1200 + (k - 7) * 60, 2100, stroke('#2e1c10', 4))
        # coin heaps
        for gx, gy, sc in ((1950, 2250, 1.3), (300, 2400, 1.0), (2200, 2600, 1.1)):
            for k in range(220):
                a = r.uniform(0, math.pi)
                dd = r.uniform(0, 1) ** 0.6
                x = gx + math.cos(a) * dd * 220 * sc
                y = gy - math.sin(a) * dd * 130 * sc
                c.drawPath(ellipse(x, y, 17, 10), fill(r.choice([GOLD, '#f0c75a', '#b8862a'])))
                c.drawPath(ellipse(x, y, 17, 10), stroke('#6a4a12', 1.5))
        # scales on a table
        c.drawRect(skia.Rect.MakeXYWH(1500, 1780, 500, 40), fill('#6a4224'))
        c.drawRect(skia.Rect.MakeXYWH(1520, 1820, 30, 280), fill('#4a2c18'))
        c.drawRect(skia.Rect.MakeXYWH(1950, 1820, 30, 280), fill('#4a2c18'))
        c.drawLine(1750, 1780, 1750, 1560, stroke(GOLD_DK, 10))
        c.drawLine(1620, 1580, 1880, 1580, stroke(GOLD_DK, 8))
        for x in (1620, 1880):
            c.drawPath(ellipse(x, 1680, 60, 16), fill(GOLD))
            c.drawLine(x, 1580, x - 50, 1680, stroke(GOLD_DK, 3))
            c.drawLine(x, 1580, x + 50, 1680, stroke(GOLD_DK, 3))
        L['main'] = s.makeImageSnapshot()
        return L
    return cached('treasure', build)


def cathedral_interior_layers():
    def build():
        L = {}
        EW, EH = 2400, 3000
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(51)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, EW, EH), lin_grad((0, 0), (0, EH), ['#14101e', '#2c2238', '#3a2c34']))
        # rose window
        rc = (1200, 700)
        c.drawPath(ellipse(*rc, 560, 560), fill('#ff9a4a', 0.16, blur=80))
        cols = ['#c8303c', '#3b62c4', '#e6b23c', '#3a9a5c', '#8a3ab0']
        for ring, (r0, r1, n) in enumerate([(0, 120, 8), (120, 300, 16), (300, 420, 24)]):
            for k in range(n):
                a0 = k * 360 / n
                pp = skia.Path()
                pp.addArc(skia.Rect.MakeXYWH(rc[0] - r1, rc[1] - r1, 2 * r1, 2 * r1), a0, 360 / n)
                pp.lineTo(*rc)
                pp.close()
                c.drawPath(pp, fill(cols[(k + ring) % 5], 0.9))
                c.drawPath(pp, stroke('#0c0812', 5))
        c.drawPath(ellipse(*rc, 420, 420), stroke('#0c0812', 18))
        c.drawPath(ellipse(*rc, 60, 60), fill('#ffe39a'))
        # gothic arches
        for k, ax in enumerate((150, 600, 1800, 2250)):
            ap = skia.Path()
            ap.moveTo(ax - 120, 2100)
            ap.lineTo(ax - 120, 1100)
            ap.quadTo(ax - 110, 800, ax, 700)
            ap.quadTo(ax + 110, 800, ax + 120, 1100)
            ap.lineTo(ax + 120, 2100)
            ap.close()
            c.drawPath(ap, fill('#0a0812'))
            c.drawPath(ap, stroke('#4a3a50', 26))
            c.drawPath(ap, stroke(INK, 5))
        for px in (370, 2030):
            c.drawRect(skia.Rect.MakeXYWH(px - 60, 0, 120, 2200), lin_grad((px - 60, 0), (px + 60, 0),
                                                                           ['#4a3a50', '#6a5a70', '#2a2030']))
        # light shafts
        for k in range(4):
            sp = poly([(1100 + k * 60, 700), (1180 + k * 60, 700), (700 + k * 250, 3000), (500 + k * 250, 3000)])
            c.drawPath(sp, fill('#ffd9a0', 0.05, blur=20))
        # floor + pews
        c.drawRect(skia.Rect.MakeXYWH(0, 2100, EW, 900), lin_grad((0, 2100), (0, 3000), ['#2c2430', '#4a3c44']))
        for k in range(8):
            yy = 2100 + (k / 8) ** 1.5 * 900
            c.drawLine(0, yy, EW, yy, stroke('#1e1820', 3))
        for row in range(4):
            yy = 2200 + row * 170
            for sx in (-1, 1):
                x0 = 1200 + sx * 260
                x1 = 1200 + sx * (1100 + row * 120)
                c.drawRect(skia.Rect.MakeLTRB(min(x0, x1), yy, max(x0, x1), yy + 60), fill('#4a2a18'))
                c.drawRect(skia.Rect.MakeLTRB(min(x0, x1), yy, max(x0, x1), yy + 60), stroke(INK, 4))
        # altar
        c.drawRect(skia.Rect.MakeXYWH(950, 1850, 500, 250), fill('#e8e0cc'))
        c.drawRect(skia.Rect.MakeXYWH(950, 1850, 500, 250), stroke(INK, 6))
        c.drawRect(skia.Rect.MakeXYWH(1185, 1500, 30, 350), fill(GOLD))
        c.drawRect(skia.Rect.MakeXYWH(1120, 1580, 160, 30), fill(GOLD))
        L['main'] = s.makeImageSnapshot()
        return L
    return cached('cathint', build)


def field_layers():
    def build():
        L = {}
        EW, EH = 2600, 3000
        s = surface(EW, EH)
        c = s.getCanvas()
        r = rnd(61)
        sky(c, 0, 0, EW, 2000, ['#0b1030', '#26305e', '#6a5a80', '#b08a7a'], 220, 7)
        moon(c, 700, 700, 220)
        hp = smooth_poly([(0, 1750), (600, 1700), (1300, 1760), (2000, 1690), (2600, 1740), (2600, 3000), (0, 3000)],
                         True, 0.3)
        c.drawPath(hp, fill('#2c2c4a'))
        # windmill silhouette
        wx, wy = 2000, 1700
        c.drawPath(poly([(wx - 60, wy), (wx - 40, wy - 300), (wx + 40, wy - 300), (wx + 60, wy)]), fill('#16142a'))
        L['mill_center'] = (wx, wy - 300)
        # far village
        for i in range(6):
            house(c, 200 + i * 140, 1760, 100, 150, r, '#3a3456', '#2a2240', 0.5)
        # field rows
        c.drawRect(skia.Rect.MakeXYWH(0, 1850, EW, 1150), lin_grad((0, 1850), (0, 3000), ['#5a5030', '#8a7438']))
        for k in range(30):
            yy = 1850 + (k / 30) ** 1.4 * 1150
            c.drawLine(0, yy, EW, yy + 20, stroke('#4a3e20', 3 + k * 0.3))
        # haystacks
        for hx, hy, hs in ((400, 2050, 1.0), (2200, 2000, 0.8)):
            hk = smooth_poly([(hx - 160 * hs, hy), (hx - 120 * hs, hy - 180 * hs), (hx, hy - 260 * hs),
                              (hx + 120 * hs, hy - 180 * hs), (hx + 160 * hs, hy)], True, 0.5)
            c.drawPath(hk, fill('#c9a24a'))
            c.drawPath(hk, stroke(INK, 5))
            for j in range(20):
                c.drawLine(hx + r.uniform(-120, 120) * hs, hy - r.uniform(0, 220) * hs,
                           hx + r.uniform(-120, 120) * hs, hy - r.uniform(0, 220) * hs, stroke('#8a6a28', 2))
        L['main'] = s.makeImageSnapshot()
        return L
    return cached('field', build)


def street_layers(variant=0):
    def build():
        L = {}
        EW, EH = 2600, 3000
        r = rnd(71 + variant)
        s = surface(EW, EH)
        c = s.getCanvas()
        sky(c, 0, 0, EW, 2000, ['#0c1134', '#2a3262', '#6a527a'], 200, 9)
        moon(c, 1300, 520, 200)
        cathedral(c, 1300, 1700, 0.75, '#22203e', 1.0)
        L['sky'] = s.makeImageSnapshot()
        s = surface(EW, EH)
        c = s.getCanvas()
        # houses on both sides, perspective-ish rows
        for side in (-1, 1):
            for k in range(5):
                u = k / 4
                w_ = 260 + 120 * u
                h_ = 520 + 380 * u
                x = 1300 + side * (260 + u * 900) - (w_ if side < 0 else 0)
                house(c, x, 1900 + u * 260, w_, h_, r, tohex('#d8c7a3', '#8a7a8a', 0.5 - u * 0.4),
                      r.choice(['#6e2f26', '#4a3a5a', '#5a3a2a']), 0.75)
        # hanging banners between houses
        for k in range(3):
            y = 1150 + k * 140
            bp = P()
            bp.moveTo(300 - k * 100, y)
            bp.quadTo(1300, y + 160, 2300 + k * 100, y)
            c.drawPath(bp, stroke('#2a1a10', 4))
            for j in range(12):
                t_ = (j + 0.5) / 12
                bx = (1 - t_) ** 2 * (300 - k * 100) + 2 * (1 - t_) * t_ * 1300 + t_ * t_ * (2300 + k * 100)
                by = (1 - t_) ** 2 * y + 2 * (1 - t_) * t_ * (y + 160) + t_ * t_ * y
                c.drawPath(poly([(bx - 26, by), (bx + 26, by), (bx, by + 60)]),
                           fill([BURG, GOLD, '#2e4a7a'][(j + k) % 3]))
        cobbles(c, 0, 1950, EW, 1050, r, '#6a6070', '#2e2a38')
        L['main'] = s.makeImageSnapshot()
        return L
    return cached('street%d' % variant, build)


def square_layers():
    def build():
        L = {}
        EW, EH = 3400, 3200
        r = rnd(81)
        s = surface(EW, EH)
        c = s.getCanvas()
        sky(c, 0, 0, EW, 2200, ['#0b1030', '#262e5e', '#5a4a78', '#8a6a80'], 320, 13)
        moon(c, 2500, 520, 230)
        L['sky'] = s.makeImageSnapshot()
        # cathedral with bell tower (bells drawn live)
        s = surface(EW, EH)
        c = s.getCanvas()
        cathedral(c, 1700, 1900, 1.15, '#2a2646', 1.0)
        L['cath'] = s.makeImageSnapshot()
        L['cath_dark'] = None
        # houses around the square (two depths)
        for name, lit in (('houses', 0.15), ('houses_lit', 1.0)):
            s = surface(EW, EH)
            c = s.getCanvas()
            rr = rnd(82)
            for k in range(6):
                for side in (-1, 1):
                    x = 1700 + side * (620 + k * 300) - (280 if side < 0 else 0)
                    house(c, x, 2000 + k * 40, 280, 600 + rr.uniform(0, 300), rr,
                          rr.choice(['#d8c7a3', '#cdb894', '#bfae9a', '#d2bfa0']),
                          rr.choice(['#6e2f26', '#4a3a5a', '#5a3a2a', '#3a4a5a']), 1.0, light_on=lit)
            L[name] = s.makeImageSnapshot()
        s = surface(EW, EH)
        c = s.getCanvas()
        cobbles(c, 0, 2050, EW, 1150, r, '#6e6474', '#33303e')
        # circular pavement pattern
        for k in range(5):
            c.drawPath(ellipse(1700, 2600, 300 + k * 160, (300 + k * 160) * 0.28), stroke('#2a2632', 6, 0.6))
        L['ground'] = s.makeImageSnapshot()
        return L
    return cached('square', build)


def rooftop_layers():
    def build():
        L = {}
        EW, EH = 2600, 3000
        r = rnd(91)
        s = surface(EW, EH)
        c = s.getCanvas()
        sky(c, 0, 0, EW, EH, ['#0a0e2a', '#232b58', '#5a4a78'], 300, 17)
        moon(c, 1300, 1150, 560, 1.2)
        L['sky'] = s.makeImageSnapshot()
        s = surface(EW, EH)
        c = s.getCanvas()
        # silhouette rooftops
        col = '#0c0a16'
        x = -100
        while x < EW:
            w_ = r.uniform(200, 380)
            h_ = r.uniform(250, 520)
            c.drawRect(skia.Rect.MakeXYWH(x, 2300 - h_ * 0.4, w_, 1000), fill(col))
            c.drawPath(poly([(x - 20, 2300 - h_ * 0.4), (x + w_ / 2, 2300 - h_), (x + w_ + 20, 2300 - h_ * 0.4)]),
                       fill(col))
            if r.random() < 0.6:
                c.drawRect(skia.Rect.MakeXYWH(x + w_ * 0.3, 2300 - h_ * 0.35, 30, 40), fill('#ffcf6a', 0.9))
            x += w_ - 20
        L['roofs'] = s.makeImageSnapshot()
        return L
    return cached('roof', build)


# ------------------------------------------------------------------ live elements
def candle(c, x, y, t, s=1.0, seed=0):
    c.drawRect(skia.Rect.MakeXYWH(x - 9 * s, y, 18 * s, 70 * s), fill('#efe6cf'))
    c.drawRect(skia.Rect.MakeXYWH(x - 9 * s, y, 18 * s, 70 * s), stroke(INK, 3))
    fl = 1 + 0.15 * noise1(t * 9, seed) + 0.1 * noise1(t * 23, seed + 4)
    sw = 4 * noise1(t * 6, seed + 9)
    c.drawPath(ellipse(x, y - 14 * s, 60 * s * fl, 60 * s * fl), fill('#ffb347', 0.22, blur=22 * s))
    fp = smooth_poly([(x - 7 * s, y - 4 * s), (x + sw * s, y - 34 * s * fl), (x + 7 * s, y - 4 * s), (x, y + 2 * s)],
                     True, 0.6)
    c.drawPath(fp, fill('#ffd27a'))
    c.drawPath(ellipse(x, y - 10 * s, 3.5 * s, 7 * s), fill('#fff6d8'))


def torch(c, x, y, t, s=1.0, seed=0):
    c.drawRect(skia.Rect.MakeXYWH(x - 8 * s, y, 16 * s, 90 * s), fill('#4a2c18'))
    fl = 1 + 0.2 * noise1(t * 8, seed)
    c.drawPath(ellipse(x, y - 30 * s, 160 * s * fl, 160 * s * fl), fill('#ff9a3c', 0.25, blur=40 * s))
    for k in range(3):
        sw = 10 * noise1(t * 7 + k, seed + k) * s
        fp = smooth_poly([(x - 22 * s, y), (x + sw, y - (60 + 20 * k) * s * fl), (x + 22 * s, y)], True, 0.6)
        c.drawPath(fp, fill(['#ff7a2a', '#ffb347', '#ffe08a'][k], 0.9))


def fog(c, t, y, w, seed=0, alpha=0.3, col='#9aa0c8', scale=1.0, speed=30):
    for k in range(7):
        x = ((k * 420 + t * speed * (0.6 + 0.4 * _hash(k, seed))) % (w + 900)) - 450
        rr = 260 * scale * (0.8 + 0.5 * _hash(k, seed + 2))
        c.drawPath(ellipse(x, y + 40 * math.sin(k * 1.3 + t * 0.3), rr * 2.2, rr * 0.55),
                   fill(col, alpha * (0.6 + 0.4 * _hash(k, seed + 5)), blur=70 * scale))


def dust(c, t, x0, y0, w, h, n=40, seed=0, col='#ffe6b0', alpha=0.6):
    for k in range(n):
        px = x0 + (_hash(k, seed) * w + t * 18 * (_hash(k, seed + 1) - 0.5) + 30 * math.sin(t * 0.7 + k)) % w
        py = y0 + (_hash(k, seed + 2) * h - t * 25 * _hash(k, seed + 3)) % h
        s = 1.5 + 3 * _hash(k, seed + 4)
        tw = 0.5 + 0.5 * math.sin(t * 3 + k)
        c.drawPath(ellipse(px, py, s, s), fill(col, alpha * tw))


def music_notes(c, t, x, y, n=5, seed=0, col='#f3d27a'):
    for k in range(n):
        ph = (t * 0.6 + _hash(k, seed)) % 1.0
        px = x + math.sin(ph * 6 + k) * 60 + (k - n / 2) * 50
        py = y - ph * 420
        a = math.sin(ph * math.pi)
        with Save(c):
            c.translate(px, py)
            c.rotate(math.sin(t * 3 + k) * 15)
            c.drawPath(ellipse(0, 0, 13, 10), fill(col, a))
            c.drawLine(11, 0, 11, -42, stroke(col, 4, a))
            if k % 2:
                c.drawLine(11, -42, 26, -30, stroke(col, 4, a))


def bell(c, x, y, ang_, s=1.0):
    with Save(c):
        c.translate(x, y)
        c.rotate(math.degrees(ang_))
        bp = smooth_poly([(-20 * s, 0), (-34 * s, 60 * s), (-60 * s, 120 * s), (60 * s, 120 * s), (34 * s, 60 * s),
                          (20 * s, 0)], True, 0.3)
        c.drawPath(bp, stroke(INK, 6))
        c.drawPath(bp, lin_grad((-60 * s, 0), (60 * s, 0), ['#f3d27a', GOLD, GOLD_DK]))
        c.drawPath(ellipse(0, 128 * s, 12 * s, 12 * s), fill(GOLD_DK))


def banner(c, x, y, w, h, t, col=BURG, emblem=GOLD, seed=0, wind=1.0):
    """hanging banner with cloth wave"""
    pts_l, pts_r = [], []
    n = 8
    for i in range(n + 1):
        u = i / n
        wv = math.sin(t * 3.2 - u * 4 + seed) * 18 * u * wind
        pts_l.append((x - w / 2 + wv, y + u * h))
        pts_r.append((x + w / 2 + wv * 1.1, y + u * h))
    tipx = x + math.sin(t * 3.2 - 4 + seed) * 18 * wind
    pts = pts_l + [(tipx, y + h + w * 0.4)] + pts_r[::-1]
    bp = poly(pts)
    c.drawPath(bp, fill(col))
    c.drawPath(bp, stroke(INK, 4))
    em = ellipse(x + math.sin(t * 3.2 - 2 + seed) * 10 * wind, y + h * 0.45, w * 0.25, w * 0.25)
    c.drawPath(em, fill(emblem))
    c.drawPath(em, stroke(INK, 3))
