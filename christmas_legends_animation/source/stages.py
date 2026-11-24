"""Stage sets: each returns layered skia Pictures + Lights for parallax camera work."""
import math, random
import skia
from gfx import *
from world import *
from human import INK, shade_hex

_STAGES = {}
def stage(name):
    if name not in _STAGES: _STAGES[name] = globals()['build_' + name]()
    return _STAGES[name]

class Stage:
    def __init__(self): self.layers = []  # (picture, parallax, Lights or None)
    def add(self, w, h, fn, par, lights=True, oy=0):
        L = Lights() if lights else None
        pic = picture(lambda c: fn(c, L), w, h)
        self.layers.append((pic, par, L, oy)); return L

def cam_apply(c, cam, par):
    cx, cy, z = cam
    xp = W / 2 + (cx - W / 2) * par; yp = H / 2 + (cy - H / 2) * par; zp = 1 + (z - 1) * par
    c.translate(W / 2, H / 2); c.scale(zp, zp); c.translate(-xp, -yp)

def to_layer(sx, sy, cam, par):
    cx, cy, z = cam
    xp = W / 2 + (cx - W / 2) * par; yp = H / 2 + (cy - H / 2) * par; zp = 1 + (z - 1) * par
    return ((sx - W / 2) / zp + xp, (sy - H / 2) / zp + yp)

def draw_stage(c, st, cam, t, pulse=0.0, upto=None, beat=None, light_alpha=1.0, between=None, start=0, screen=None):
    """draw layers; `between` = {layer_index: fn(c)} drawn right after that layer (inside its camera);
    `screen` = {layer_index: fn(c)} drawn after that layer in screen space"""
    for i, (pic, par, L, oy) in enumerate(st.layers):
        if i < start: continue
        if upto is not None and i > upto: break
        c.save(); cam_apply(c, cam, par); c.drawPicture(pic)
        if L is not None:
            draw_smoke(c, L, t, light_alpha); draw_lights(c, L, t, pulse, alpha=light_alpha, beat=beat)
        if between and i in between: between[i](c)
        c.restore()
        if screen and i in screen: screen[i](c)

def tree_big(c, x, gy, h, L, seed=5):
    pine(c, x, gy, h, True, '#1d5a3c', seed, decorated=True, L=L, star=True)
    # garland swoops
    for k in range(4):
        y0 = gy - h * (0.2 + 0.18 * k); w_ = h * 0.42 * (1 - (0.2 + 0.18 * k) * 0.8)
        pth = skia.Path(); pth.moveTo(x - w_, y0 - 20); pth.quadTo(x, y0 + 30, x + w_, y0 - 40)
        c.drawPath(pth, P('#f2c14e', 220, stroke=5))
    # presents under tree
    for k, (px, pw, ph, col_) in enumerate(((-150, 90, 70, '#d62f3a'), (-50, 70, 90, '#2f8f4e'), (60, 100, 60, '#3a7bd5'), (150, 70, 70, '#f2c14e'))):
        present(c, x + px, gy, pw, ph, col_, '#fff2c8' if k % 2 else '#f2c14e')

def present(c, x, gy, w, h, col_='#d62f3a', rib='#f2c14e', lid=0.0, rot=0.0):
    c.save(); c.translate(x, gy); c.rotate(rot)
    box = rrect(-w / 2, -h, w, h, 6)
    c.drawPath(box, P(INK, 255, stroke=8)); c.drawPath(box, PS(lin((-w / 2, -h), (w / 2, 0), [shade(col_, 0.15), col(col_), shade(col_, -0.25)])))
    c.drawRect(skia.Rect.MakeLTRB(-7, -h, 7, 0), P(rib))
    ly = -h - lid * 90
    c.save(); c.translate(0, ly); c.rotate(-lid * 35)
    lp = rrect(-w / 2 - 6, -16, w + 12, 18, 5)
    c.drawPath(lp, P(INK, 255, stroke=8)); c.drawPath(lp, P(shade_hex(col_, 0.1)))
    c.drawRect(skia.Rect.MakeLTRB(-7, -16, 7, 2), P(rib))
    for sx in (-1, 1):
        bw = path_from([(0, -16), (sx * 26, -38), (sx * 30, -16)], True, 0.8)
        c.drawPath(bw, P(INK, 255, stroke=5)); c.drawPath(bw, P(rib))
    c.restore()
    c.restore()

def distant_village(c, w, gy, L, seed=9, col_='#3b4680', n=None):
    r = random.Random(seed); x = -40
    while x < w:
        hw = r.uniform(70, 130); hh = r.uniform(60, 120)
        pth = path_from([(x, gy), (x, gy - hh), (x + hw / 2, gy - hh - hw * 0.45), (x + hw, gy - hh), (x + hw, gy)], True)
        c.drawPath(pth, P(col_))
        c.drawPath(path_from([(x - 4, gy - hh + 2), (x + hw / 2, gy - hh - hw * 0.45), (x + hw + 4, gy - hh + 2), (x + hw / 2, gy - hh - hw * 0.2)], True), P('#dfe7ff', 220))
        for k in range(r.randint(1, 3)):
            wx = x + r.uniform(10, hw - 24); wy = gy - r.uniform(20, hh - 20)
            if r.random() < 0.75:
                c.drawRect(skia.Rect.MakeXYWH(wx, wy, 12, 14), P('#ffcf6e'))
                glow(c, wx + 6, wy + 7, 22, '#ffb347', 90)
        x += hw + r.uniform(-10, 20)
    c.drawRect(skia.Rect.MakeLTRB(0, gy - 30, w, gy + 10), PS(lin((0, gy - 30), (0, gy + 10), [('#9fb0e0', 0), ('#9fb0e0', 200)])))

# ======================================================================= OPENING STREET
def build_opening():
    st = Stage(); w = 3400
    def l0(c, L):
        sky(c, w, H, '#0a0f36', '#28357a', '#8090c8', True, 11, (2300, 360, 80))
        mountains(c, w, 1130, 420, '#4b5a98', '#eef3ff', 4, 9, '#7f92cc')
    def l1(c, L):
        hills(c, w, 1180, 50, '#c4d0f2', 5)
        distant_village(c, w, 1190, L, 3)
        church(c, 1600, 1250, 240, 170, L, 21)
    def l2(c, L):
        ground(c, w, 1330, 700, seed=9)
        x = -60; r = random.Random(4); k = 0
        styles = [('timber', '#5a3420', '#4a5a7a'), ('chalet', '#c98b5a', '#7a2f2a'), ('stone', '#9d9586', '#3f4a6a'),
                  ('timber', '#6b2f2a', '#5a3a6a'), ('chalet', '#a8693e', '#2f4a3a'), ('iceland', '#3f7fbf', '#7a2f2a')]
        while x < w:
            stl, wall, roof = styles[k % len(styles)]
            ww = r.uniform(300, 380); hh = r.uniform(250, 330)
            house(c, x, 1350, ww, hh, stl, wall, roof, L=L, seed=30 + k, shutters='#2f6b4f' if k % 2 else '#7a2f2a')
            if k % 2 == 0: pine(c, x + ww + 30, 1360, 230, seed=k)
            x += ww + r.uniform(60, 110); k += 1
        for k in range(6):
            string_lights(c, 200 + k * 560, 1110, 520 + k * 560, 1120, 70, L, k, 12)
    def l3(c, L):
        for k in range(7):
            lamppost(c, 260 + k * 520, 1700, 360, L, k)
    st.add(w, H, l0, 0.15, False); st.add(w, H, l1, 0.35); st.add(w, H, l2, 0.7); st.add(w, H, l3, 1.0)
    st.w = w
    return st

# ======================================================================= ST NICHOLAS SQUARE (opening + finale)
def build_square():
    st = Stage(); w = 1800
    def l0(c, L):
        sky(c, w, H, '#090d33', '#25307a', '#7d8cc6', True, 21, (1300, 300, 70))
    def l1(c, L):
        hills(c, w, 1100, 40, '#c4d0f2', 6)
        distant_village(c, w, 1120, L, 8)
    def l2(c, L):
        ground(c, w, 1300, 700, seed=12, footprints=False)
        house(c, -40, 1310, 380, 380, 'timber', '#6b2f2a', '#3f4a6a', L=L, seed=61, shutters='#2f6b4f')
        church(c, 700, 1290, 320, 220, L, 64)
        house(c, 1380, 1310, 400, 360, 'timber', '#4a2f22', '#7a2f2a', L=L, seed=62, shutters='#7a2f2a')
        for k in range(5): string_lights(c, 300 + k * 260, 960, 560 + k * 260, 980, 80, L, k, 10)
    def l3(c, L):
        tree_big(c, 900, 1560, 700, L, 7)
        # market stalls
        for k, (sx, colr) in enumerate(((180, '#d62f3a'), (1460, '#2f8f4e'))):
            c.drawPath(rrect(sx - 150, 1430, 300, 140, 8), P(INK, 255, stroke=8)); c.drawPath(rrect(sx - 150, 1430, 300, 140, 8), P('#8a5a3a'))
            for j in range(6):
                c.drawPath(path_from([(sx - 170 + j * 57, 1330), (sx - 113 + j * 57, 1330), (sx - 120 + j * 57, 1420), (sx - 160 + j * 57, 1420)], True),
                           P(colr if j % 2 == 0 else '#fff4e6'))
            c.drawPath(path_from([(sx - 180, 1330), (sx + 180, 1330), (sx + 150, 1300), (sx - 150, 1300)], True), P('#ffffff'))
            string_lights(c, sx - 160, 1425, sx + 160, 1425, 20, L, k + 3, 8)
            lamppost(c, sx + (190 if k == 0 else -190), 1600, 260, L, k)
    st.add(w, H, l0, 0.1, False); st.add(w, H, l1, 0.3); st.add(w, H, l2, 0.65); st.add(w, H, l3, 1.0)
    st.w = w
    return st

# ======================================================================= ALPINE VILLAGE (Krampus)
def build_alpine():
    st = Stage(); w = 5200
    def l0(c, L):
        sky(c, w, H, '#0b1038', '#2a3678', '#7a86c0', True, 1, (900, 330, 70))
        mountains(c, w, 1150, 560, '#4c5d9c', '#eef3ff', 2, 12, '#7d90cc')
    def l1(c, L):
        hills(c, w, 1230, 70, '#c9d5f5', 3)
        distant_village(c, w, 1240, L, 5, '#3a4b86')
        church(c, 2350, 1320, 260, 180, L, 7)
        for k in range(14): pine(c, 150 + k * 380, 1330, 230 + (k % 3) * 40, seed=k)
    def l2(c, L):
        ground(c, w, 1320, 700, seed=3)
        x = -80; r = random.Random(9); k = 0
        while x < w:
            stl = 'chalet' if k % 3 != 2 else 'timber'
            ww = r.uniform(380, 460); hh = r.uniform(330, 400)
            house(c, x, 1560, ww, hh, stl, ('#c98b5a', '#b7774a', '#5a3420', '#a8693e')[k % 4], ('#7a2f2a', '#6a2a26', '#4a5a7a', '#2f4a3a')[k % 4],
                  L=L, seed=100 + k, shutters=('#2f6b4f', '#7a2f2a', '#2f4a6b')[k % 3])
            x += ww + r.uniform(140, 220); k += 1
        for k in range(9): string_lights(c, 400 + k * 560, 1180, 700 + k * 560, 1200, 70, L, k, 12)
        for k in range(10): lamppost(c, 330 + k * 520, 1640, 330, L, k)
    st.add(w, H, l0, 0.12, False); st.add(w, H, l1, 0.4); st.add(w, H, l2, 1.0)
    st.w = w
    return st

# ======================================================================= ICELAND
def build_iceland():
    st = Stage(); w = 2600
    def l0(c, L):
        sky(c, w, H, '#04122a', '#0f2f55', '#3f6a8f', True, 31, None)
    def l1(c, L):
        mountains(c, w, 1180, 300, '#304e78', '#e6f0ff', 31, 6, '#4f78a0')
        hills(c, w, 1240, 60, '#b8cde8', 8)
        distant_village(c, w, 1250, L, 12, '#2b4466')
    def l2(c, L):
        ground(c, w, 1330, 700, '#eaf2ff', '#aac0e4', seed=5)
        cols = [('#d23c3c', '#2a2f3a'), ('#f2c14e', '#7a2f2a'), ('#3f7fbf', '#2a2f3a'), ('#2f8f6e', '#7a2f2a'), ('#e8e2d6', '#c23a3a'), ('#d97a2b', '#2a2f3a')]
        x = -50
        for k in range(8):
            wall, roof = cols[k % 6]
            ww = 300 + (k % 3) * 40; hh = 260 + (k % 2) * 60
            house(c, x, 1470, ww, hh, 'iceland', wall, roof, L=L, seed=200 + k, shutters=None)
            x += ww + 70
        for k in range(4): string_lights(c, 300 + k * 600, 1130, 600 + k * 600, 1150, 60, L, k, 12)
    st.add(w, H, l0, 0.05, False); st.add(w, H, l1, 0.3); st.add(w, H, l2, 1.0)
    st.w = w
    return st

def build_iceland_int():
    st = Stage(); w = 1500
    def l0(c, L):
        # wooden wall
        c.drawRect(skia.Rect.MakeWH(w, H), PS(lin((0, 0), (0, H), ['#5a3524', '#7a4a2e', '#4a2a1a'])))
        for x in range(0, w, 90):
            c.drawLine(x, 0, x, H, P('#3a2014', 255, stroke=5)); c.drawLine(x + 6, 0, x + 6, H, P('#9a6a44', 90, stroke=2))
        # window with aurora + snow
        wx, wy, ww, wh = 520, 420, 460, 520
        c.drawPath(rrect(wx - 26, wy - 26, ww + 52, wh + 52, 12), P('#f2e6d0'))
        c.save(); c.clipPath(rrect(wx, wy, ww, wh, 6))
        c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), PS(lin((0, wy), (0, wy + wh), ['#04122a', '#16406a', '#3f6a8f'])))
        for k, (colr, yo) in enumerate((('#3cffb0', 0.3), ('#9a7aff', 0.2))):
            pth = skia.Path(); pth.moveTo(wx, wy + wh * yo)
            pth.cubicTo(wx + 150, wy + wh * (yo - 0.15), wx + 300, wy + wh * (yo + 0.15), wx + ww, wy + wh * (yo - 0.05))
            c.drawPath(pth, P(colr, 140, stroke=80, blur=30))
        for k in range(5):
            house(c, wx - 40 + k * 120, wy + wh - 10, 100, 80, 'iceland', ('#d23c3c', '#f2c14e', '#3f7fbf', '#2f8f6e', '#e8e2d6')[k], '#2a2f3a', seed=k, lights=False, wreath=False, chimney=False)
        c.restore()
        c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, P('#f2e6d0', 255, stroke=14)); c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, P('#f2e6d0', 255, stroke=14))
        snow_cap(c, [(wx - 26, wy + wh + 20), (wx + ww + 26, wy + wh + 20)], 18, 4)
        # bunting
        for k in range(10):
            x0 = 80 + k * 140
            c.drawPath(path_from([(x0, 230), (x0 + 120, 230), (x0 + 60, 320)], True), P(('#d62f3a', '#2f8f4e', '#f2c14e')[k % 3]))
        c.drawLine(60, 230, w, 230, P('#3a2014', 255, stroke=4))
        # floor + rug
        c.drawRect(skia.Rect.MakeLTRB(0, 1460, w, H), PS(lin((0, 1460), (0, H), ['#8a5a36', '#5a3520'])))
        for x in range(-200, w, 140): c.drawLine(x, 1460, x - 200, H, P('#4a2a18', 160, stroke=4))
        c.drawOval(skia.Rect.MakeLTRB(150, 1600, 1350, 1860), P('#9a2f35')); c.drawOval(skia.Rect.MakeLTRB(200, 1625, 1300, 1835), P('#f2c14e', 255, stroke=10))
        tree_big(c, 1230, 1520, 620, L, 13)
        # wall shelves with candles
        c.drawRect(skia.Rect.MakeLTRB(60, 760, 380, 790), P('#3a2014'))
        for k in range(3):
            c.drawPath(rrect(90 + k * 100, 690, 26, 70, 4), P('#f4ead2'))
            glow(c, 103 + k * 100, 670, 60, '#ffcf6e', 160); c.drawCircle(103 + k * 100, 675, 8, P('#fff0b0'))
    st.add(w, H, l0, 1.0)
    st.w = w
    return st

# ======================================================================= WALES
def build_welsh_int():
    st = Stage(); w = 1500
    def l0(c, L):
        # stone wall interior
        c.drawRect(skia.Rect.MakeWH(w, H), P('#6e6458'))
        r = random.Random(3)
        for row, yy in enumerate(range(0, 1500, 70)):
            for k in range(-1, int(w / 110) + 2):
                xx = k * 110 + (row % 2) * 55 + r.uniform(-6, 6)
                c.drawPath(rrect(xx + 4, yy + 4, 102, 62, 18), P(shade_hex('#8a7f70', r.uniform(-0.15, 0.1))))
        # wooden beams
        for x in (0, 740, 1440): c.drawRect(skia.Rect.MakeLTRB(x - 30, 0, x + 30, 1480), P('#3a2418'))
        c.drawRect(skia.Rect.MakeLTRB(0, 160, w, 230), P('#3a2418'))
        # window (left)
        wx, wy, ww, wh = 120, 520, 360, 420
        c.drawPath(rrect(wx - 24, wy - 24, ww + 48, wh + 48, 10), P('#4a2f20'))
        c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), PS(lin((0, wy), (0, wy + wh), ['#0b1440', '#2b3a7a', '#7080b8'])))
        c.save(); c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
        hills(c, w, wy + wh - 60, 40, '#c4d0f2', 2)
        pine(c, wx + 80, wy + wh - 20, 160, seed=1); pine(c, wx + 270, wy + wh - 10, 200, seed=2)
        c.restore()
        c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, P('#4a2f20', 255, stroke=12)); c.drawLine(wx, wy + wh / 2, wx + ww, wy + wh / 2, P('#4a2f20', 255, stroke=12))
        # fireplace (centre-right)
        fx = 820
        c.drawPath(rrect(fx - 260, 900, 520, 580, 10), P('#5c5248'))
        for row, yy in enumerate(range(900, 1480, 48)):
            for k in range(-1, 7):
                c.drawPath(rrect(fx - 260 + k * 88 + (row % 2) * 44, yy + 3, 84, 42, 10), P(shade_hex('#9a8c7a', r.uniform(-0.12, 0.1))))
        c.drawPath(_arch_(fx - 160, 1130, 320, 350), P('#170c08'))
        c.drawRect(skia.Rect.MakeLTRB(fx - 300, 880, fx + 300, 930), P('#3a2418'))
        # mantel decorations: stockings + candles + holly
        for k in range(3):
            sx = fx - 180 + k * 180
            stk = path_from([(sx - 26, 930), (sx + 26, 930), (sx + 26, 1030), (sx + 60, 1050), (sx + 50, 1085), (sx - 10, 1075), (sx - 26, 1040)], True, 0.4)
            c.drawPath(stk, P(INK, 255, stroke=8)); c.drawPath(stk, P(('#d62f3a', '#2f8f4e', '#d62f3a')[k]))
            c.drawPath(rrect(sx - 32, 925, 64, 24, 8), P('#ffffff'))
        for k in range(2):
            cx_ = fx - 240 + k * 480
            c.drawPath(rrect(cx_ - 12, 800, 24, 80, 4), P('#f4ead2')); glow(c, cx_, 785, 70, '#ffcf6e', 170); c.drawCircle(cx_, 790, 8, P('#fff0b0'))
        for k in range(9):
            hx = fx - 260 + k * 65
            c.drawCircle(hx, 875, 18, P('#2f7d46')); c.drawCircle(hx + 10, 880, 6, P('#d62f3a'))
        # door (right wall) - closed version drawn dynamically
        c.drawPath(rrect(1150, 820, 300, 660, 12), P('#3a2418'))
        # floor
        c.drawRect(skia.Rect.MakeLTRB(0, 1470, w, H), PS(lin((0, 1470), (0, H), ['#7a4e30', '#4a2c1a'])))
        for x in range(-300, w + 300, 150): c.drawLine(x, 1470, x * 1.4 - 300, H, P('#3a2014', 150, stroke=4))
        c.drawOval(skia.Rect.MakeLTRB(300, 1580, 1250, 1840), P('#2f5a7a')); c.drawOval(skia.Rect.MakeLTRB(340, 1600, 1210, 1820), P('#e8c050', 255, stroke=8))
    st.add(w, H, l0, 1.0)
    st.w = w
    return st

def _arch_(x, y, w, h):
    p = skia.Path(); p.moveTo(x, y + h); p.lineTo(x, y + w / 2); p.arcTo(skia.Rect.MakeXYWH(x, y, w, w), 180, 180, False)
    p.lineTo(x + w, y + h); p.close(); return p

def build_welsh_ext():
    st = Stage(); w = 2000
    def l0(c, L):
        sky(c, w, H, '#070b2e', '#1f2a6a', '#5a6aa8', True, 41, (380, 360, 60))
        hills(c, w, 1150, 90, '#aebde6', 4)
        distant_village(c, w, 1170, L, 21, '#2b3570')
    def l1(c, L):
        ground(c, w, 1300, 700, seed=21)
        # cottage wall with door on the right
        c.drawRect(skia.Rect.MakeLTRB(1180, 500, w, 1330), P('#8a7f70'))
        r = random.Random(5)
        for row, yy in enumerate(range(500, 1330, 52)):
            for k in range(-1, 12):
                xx = 1180 + k * 80 + (row % 2) * 40 + r.uniform(-4, 4)
                c.drawPath(rrect(xx + 3, yy + 3, 76, 46, 14), P(shade_hex('#a3998a', r.uniform(-0.12, 0.1))))
        c.drawPath(path_from([(1140, 520), (1180, 400), (w, 400), (w, 520)], True), P('#3f4a6a'))
        snow_cap(c, [(1140, 520), (w, 520)], 30, 2)
        window(c, 1700, 760, 160, 190, True, L, '#2f6b4f')
        pine(c, 400, 1320, 300, seed=9); pine(c, 760, 1330, 360, seed=10)
        fence(c, 0, 1100, 1380, 70)
        for k in range(3): lamppost(c, 240 + k * 420, 1460, 300, L, k)
    st.add(w, H, l0, 0.3); st.add(w, H, l1, 1.0)
    st.w = w
    return st
