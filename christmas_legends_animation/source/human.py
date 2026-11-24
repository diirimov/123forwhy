"""Articulated 2D cartoon human rig with expressive faces."""
import math
import skia
from gfx import *

INK = '#22142e'

DEFAULT_POSE = dict(x=0, y=0, s=1.0, face=1, lean=0.0, bob=0.0, sq=1.0, turn=0.0,
                    arm_l=(12, 10), arm_r=(12, 10), leg_l=(4, 0), leg_r=(4, 0),
                    head_tilt=0.0, look=(0.0, 0.0), eyes='open', blink=0.0, brows=(0.0, 0.0), brow_l=None,
                    mouth='smile', mouth_open=0.0, cheeks=0.0, sweat=0.0, hair_up=0.0, items=None, alpha=255)

class Human:
    def __init__(self, kind='adult', skin='#f2c29b', hair='#5a3420', hat='beanie', hat_col='#c8283a', pom='#ffffff',
                 coat='#2f6b4f', coat2=None, pants='#3a3550', boots='#4a2c22', scarf='#e8c547', mitt='#c8283a',
                 beard=None, hair_style='short', robe=False, sweater=None, patches=False, glasses=False, apron=None,
                 eye_col='#3b2a1a', nose='#e9a07f', bulk=0.0, seed=0):
        self.kind = kind
        if kind == 'kid':
            self.leg, self.torso, self.hr, self.tw = 64, 80, 64, 92
        elif kind == 'elder':
            self.leg, self.torso, self.hr, self.tw = 90, 112, 56, 104
        elif kind == 'big':
            self.leg, self.torso, self.hr, self.tw = 104, 138, 60, 140
        else:
            self.leg, self.torso, self.hr, self.tw = 104, 128, 56, 112
        self.skin, self.hair, self.hat, self.hat_col, self.pom = skin, hair, hat, hat_col, pom
        self.coat, self.coat2, self.pants, self.boots, self.scarf, self.mitt = coat, coat2 or shade_hex(coat, -0.25), pants, boots, scarf, mitt
        self.beard, self.hair_style, self.robe, self.sweater, self.patches = beard, hair_style, robe, sweater, patches
        self.glasses, self.apron, self.eye_col, self.nose_col, self.bulk, self.seed = glasses, apron, eye_col, nose, bulk, seed

    # ------------------------------------------------------------------
    def draw(self, c, **kw):
        p = dict(DEFAULT_POSE); p.update(kw)
        s = p['s']; a = p['alpha']
        c.save()
        c.translate(p['x'], p['y'] + p['bob'] * s)
        c.scale(s * p['face'], s)
        c.rotate(p['lean'])
        c.scale(1 / math.sqrt(p['sq']) * (1 + self.bulk * 0.0), p['sq'])
        leg, tor, hr, tw = self.leg, self.torso, self.hr, self.tw + self.bulk * 60
        hip_y = -leg
        neck_y = hip_y - tor
        # ground shadow
        c.save(); c.scale(1 / max(p['sq'], 0.5), 1)
        c.drawOval(skia.Rect.MakeLTRB(-tw * 0.7, -10, tw * 0.7, 12), P('#0b0820', int(a * 0.28), blur=6))
        c.restore()
        # legs
        if not self.robe:
            for side, lp in ((-1, p['leg_l']), (1, p['leg_r'])):
                hx = side * tw * 0.22
                pts = two_bone((hx, hip_y), side * lp[0], leg * 0.52, -side * lp[1], leg * 0.5)
                limb(c, pts, 30 if self.kind != 'kid' else 26, self.pants, INK, 4, a, highlight='#ffffff')
                self._boot(c, pts[2], side * (lp[0] - lp[1]), side, a)
        else:
            for side, lp in ((-1, p['leg_l']), (1, p['leg_r'])):
                hx = side * tw * 0.2
                pts = two_bone((hx, hip_y), side * lp[0], leg * 0.52, -side * lp[1], leg * 0.5)
                self._boot(c, pts[2], side * (lp[0] - lp[1]), side, a)
        # torso / coat
        self._torso(c, hip_y, neck_y, tw, p, a)
        # head
        c.save(); c.translate(0, neck_y - hr * 0.78); c.rotate(p['head_tilt'])
        self._head(c, hr, p, a)
        c.restore()
        # arms (on top)
        sh_y = neck_y + 18
        hands = {}
        for side, ap, key in ((-1, p['arm_l'], 'l'), (1, p['arm_r'], 'r')):
            sx = side * (tw * 0.44)
            L1 = (tor * 0.42) if self.kind != 'kid' else tor * 0.44
            pts = two_bone((sx, sh_y), side * ap[0], L1, side * ap[1], L1 * 0.95)
            limb(c, pts, 26 if self.kind != 'kid' else 22, self.coat, INK, 4, a, highlight='#ffffff')
            # cuff
            cx, cy = pts[2]
            c.drawCircle(cx, cy, 15 if self.kind != 'kid' else 13, P(INK, a))
            c.drawCircle(cx, cy, 11.5 if self.kind != 'kid' else 10, P(self.mitt, a))
            c.drawCircle(cx - 3, cy - 4, 4, P('#ffffff', int(a * 0.35)))
            ang = math.degrees(math.atan2(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]))
            hands[key] = (cx, cy, ang)
        if p['items']:
            for k, fn in p['items'].items():
                if k in hands: fn(c, *hands[k])
        c.restore()
        return hands

    def _boot(self, c, pt, ang, side, a):
        c.save(); c.translate(*pt); c.rotate(-ang * 0.3)
        b = skia.Path(); w = 26 if self.kind != 'kid' else 22
        b.moveTo(-w * 0.55, -12); b.lineTo(w * 0.55, -12); b.quadTo(w * 0.65 + 6, -2, w * 1.0, 4)
        b.quadTo(w * 1.1, 14, w * 0.6, 14); b.lineTo(-w * 0.6, 14); b.quadTo(-w * 0.8, 2, -w * 0.55, -12); b.close()
        if side < 0: c.scale(-1, 1) if False else None
        fill_outline(c, b, self.boots, INK, 3.5, a)
        c.drawLine(-w * 0.6, 11, w * 0.6, 11, P(shade_hex(self.boots, -0.35), a, stroke=4))
        c.restore()

    def _torso(self, c, hip_y, neck_y, tw, p, a):
        tor = hip_y - neck_y
        b = skia.Path()
        if self.robe:
            bot = -6
            b.moveTo(-tw * 0.32, neck_y + 4)
            b.cubicTo(-tw * 0.55, neck_y + tor * 0.4, -tw * 0.62, bot - 40, -tw * 0.7, bot)
            b.quadTo(0, bot + 10, tw * 0.7, bot)
            b.cubicTo(tw * 0.62, bot - 40, tw * 0.55, neck_y + tor * 0.4, tw * 0.32, neck_y + 4)
            b.quadTo(0, neck_y - 6, -tw * 0.32, neck_y + 4); b.close()
        else:
            flare = 0.62 if self.kind != 'kid' else 0.58
            b.moveTo(-tw * 0.36, neck_y + 6)
            b.cubicTo(-tw * 0.52, neck_y + tor * 0.35, -tw * 0.56, hip_y - 10, -tw * flare, hip_y + 14)
            b.quadTo(0, hip_y + 26, tw * flare, hip_y + 14)
            b.cubicTo(tw * 0.56, hip_y - 10, tw * 0.52, neck_y + tor * 0.35, tw * 0.36, neck_y + 6)
            b.quadTo(0, neck_y - 8, -tw * 0.36, neck_y + 6); b.close()
        base = self.sweater or self.coat
        shaded(c, b, base, (-0.6, -0.8), 0.18, INK, 4.5, a)
        c.save(); c.clipPath(b, doAntiAlias=True)
        if self.sweater:  # knitted pattern bands
            for k, yy in enumerate((neck_y + tor * 0.35, neck_y + tor * 0.62)):
                c.drawRect(skia.Rect.MakeLTRB(-tw, yy - 9, tw, yy + 9), P('#ffffff' if k == 0 else (self.scarf or '#c8283a'), int(a * 0.85)))
                for xx in range(-int(tw), int(tw), 22):
                    c.drawPath(path_from([(xx, yy), (xx + 7, yy - 6), (xx + 14, yy), (xx + 7, yy + 6)]), P(self.coat2, a))
        if self.robe:
            c.drawRect(skia.Rect.MakeLTRB(-16, neck_y, 16, 0), P('#f3e3b0', a))
            c.drawRect(skia.Rect.MakeLTRB(-16, neck_y, 16, 0), P('#b38a2e', a, stroke=3))
            for yy in range(int(neck_y + 30), 0, 46):
                c.drawPath(path_from([(0, yy - 10), (8, yy), (0, yy + 10), (-8, yy)]), P('#c8283a', a))
        elif not self.sweater:
            c.drawLine(0, neck_y + 10, 0, hip_y + 20, P(INK, int(a * 0.5), stroke=3))
            for k in range(3):
                yy = neck_y + tor * (0.3 + 0.22 * k)
                c.drawCircle(8, yy, 5, P('#e8c86a', a)); c.drawCircle(8, yy, 5, P(INK, a, stroke=2))
            # belt
            c.drawRect(skia.Rect.MakeLTRB(-tw, hip_y - 14, tw, hip_y + 2), P(shade_hex(self.coat, -0.45), a))
            c.drawRect(skia.Rect.MakeLTRB(-10, hip_y - 16, 10, hip_y + 4), P('#e8c86a', a, stroke=4))
        if self.apron:
            ap = rrect(-tw * 0.32, neck_y + tor * 0.3, tw * 0.64, tor * 0.85, 12)
            c.drawPath(ap, P(self.apron, a)); c.drawPath(ap, P(INK, a, stroke=3))
        if self.patches:
            for (px, py, pw, ph, pc) in ((-tw * 0.25, neck_y + tor * 0.2, 30, 26, '#8a6d4b'), (tw * 0.12, neck_y + tor * 0.58, 34, 28, '#6f7d8c'),
                                         (-tw * 0.05, neck_y + tor * 0.85, 26, 22, '#9b5b4a')):
                pp = rrect(px, py, pw, ph, 5); c.drawPath(pp, P(pc, a)); c.drawPath(pp, P(INK, a, stroke=2.5))
                for k in range(4):
                    c.drawLine(px + 4 + k * pw / 4, py - 3, px + 4 + k * pw / 4, py + 3, P('#e8dcc0', a, stroke=2))
            # holes
            c.drawOval(skia.Rect.MakeXYWH(tw * 0.18, neck_y + tor * 0.25, 16, 11), P('#1a1020', a))
        # shading under arms
        c.drawRect(skia.Rect.MakeLTRB(-tw, neck_y - 20, tw, neck_y + 22), P('#000000', int(a * 0.12), blur=8))
        c.restore()
        # scarf
        if self.scarf and not self.robe:
            sc = skia.Path(); sc.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-tw * 0.4, neck_y - 10, tw * 0.4, neck_y + 16), 14, 14))
            fill_outline(c, sc, self.scarf, INK, 3.5, a)
            tail = path_from([(tw * 0.12, neck_y + 8), (tw * 0.3, neck_y + 10), (tw * 0.34, neck_y + 60), (tw * 0.18, neck_y + 62)], True, 0.6)
            fill_outline(c, tail, self.scarf, INK, 3.5, a)
            for k in range(3):
                c.drawLine(tw * 0.2, neck_y + 22 + k * 12, tw * 0.32, neck_y + 22 + k * 12, P(shade_hex(self.scarf, -0.3), a, stroke=3))

    def _head(self, c, hr, p, a):
        turn = p['turn']
        fx = turn * hr * 0.28
        # back hair
        if self.hair_style in ('long', 'bob', 'bun'):
            hb = blob(0, hr * 0.15, hr * 1.12, hr * (1.15 if self.hair_style == 'long' else 0.95), 12, 0.04, self.seed)
            fill_outline(c, hb, self.hair, INK, 4, a)
        # ears
        for sx in (-1, 1):
            c.drawCircle(sx * hr * 0.95 + fx * 0.3, hr * 0.12, hr * 0.2, P(INK, a))
            c.drawCircle(sx * hr * 0.95 + fx * 0.3, hr * 0.12, hr * 0.2 - 3.5, P(self.skin, a))
        head = blob(0, 0, hr, hr * 1.02, 12, 0.0, 0)
        shaded(c, head, self.skin, (-0.5, -0.9), 0.12, INK, 4.5, a)
        # cheeks
        cb = int(a * (0.35 + 0.4 * p['cheeks']))
        for sx in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(sx * hr * 0.55 + fx - hr * 0.2, hr * 0.25, hr * 0.4, hr * 0.24), P('#ff7a7a', cb, blur=5))
        # beard (under mouth)
        if self.beard:
            bd = path_from([(-hr * 0.95, -hr * 0.05), (-hr * 0.9, hr * 0.6), (-hr * 0.5, hr * 1.25), (0, hr * 1.55),
                            (hr * 0.5, hr * 1.25), (hr * 0.9, hr * 0.6), (hr * 0.95, -hr * 0.05), (hr * 0.5, hr * 0.35),
                            (0, hr * 0.42), (-hr * 0.5, hr * 0.35)], True, 0.7)
            shaded(c, bd, self.beard, (-0.4, -1), 0.12, INK, 4, a)
            for k in range(5):
                xx = -hr * 0.6 + k * hr * 0.3
                c.drawLine(xx, hr * 0.6, xx * 0.7, hr * 1.1, P(shade_hex(self.beard, -0.15), a, stroke=3))
        self._face(c, hr, p, fx, a)
        if self.beard:  # moustache
            for sx in (-1, 1):
                m = path_from([(fx, hr * 0.32), (fx + sx * hr * 0.45, hr * 0.28), (fx + sx * hr * 0.6, hr * 0.42),
                               (fx + sx * hr * 0.3, hr * 0.5)], True, 0.8)
                fill_outline(c, m, self.beard, INK, 3, a)
        self._hair_hat(c, hr, p, fx, a)

    def _face(self, c, hr, p, fx, a):
        lx, ly = p['look']
        ex = hr * 0.36; ey = -hr * 0.02
        er_w, er_h = hr * 0.25, hr * 0.31
        mode = p['eyes']
        if mode == 'wide': er_w, er_h = hr * 0.31, hr * 0.4
        if mode == 'narrow': er_h = hr * 0.12
        blink = max(p['blink'], 1.0 if mode == 'closed' else 0.0)
        for sx in (-1, 1):
            cx = sx * ex + fx; cy = ey
            if mode == 'happy':
                arc = skia.Path(); arc.moveTo(cx - er_w, cy + 4); arc.quadTo(cx, cy - er_h * 1.1, cx + er_w, cy + 4)
                c.drawPath(arc, P(INK, a, stroke=6)); continue
            hgt = er_h * (1 - blink * 0.95)
            if hgt < 2.5:
                c.drawLine(cx - er_w, cy, cx + er_w, cy, P(INK, a, stroke=5)); continue
            eye = ellipse(cx, cy, er_w, hgt)
            c.drawPath(eye, P(INK, a, stroke=7)); c.drawPath(eye, P('#fffdf7', a))
            c.save(); c.clipPath(eye, doAntiAlias=True)
            ir = er_w * (0.72 if mode != 'wide' else 0.55)
            ix = cx + lx * er_w * 0.45; iy = cy + ly * er_h * 0.35
            c.drawCircle(ix, iy, ir, P(self.eye_col, a)); c.drawCircle(ix, iy, ir * 0.55, P('#120b10', a))
            c.drawCircle(ix - ir * 0.35, iy - ir * 0.4, ir * 0.32, P('#ffffff', a))
            c.drawCircle(ix + ir * 0.35, iy + ir * 0.3, ir * 0.14, P('#ffffff', int(a * 0.8)))
            # upper lid shadow
            c.drawRect(skia.Rect.MakeLTRB(cx - er_w, cy - hgt, cx + er_w, cy - hgt * 0.55), P('#000000', int(a * 0.12)))
            c.restore()
        if self.glasses:
            for sx in (-1, 1):
                c.drawCircle(sx * ex + fx, ey, er_w * 1.35, P('#4a3a2a', a, stroke=4))
            c.drawLine(-ex + fx + er_w * 1.35, ey, ex + fx - er_w * 1.35, ey, P('#4a3a2a', a, stroke=4))
        # brows
        bang, bh = p['brows']
        for sx in (-1, 1):
            ang = bang
            hh = bh
            if p['brow_l'] is not None and sx == -1: ang, hh = p['brow_l']
            cx = sx * ex + fx; cy = ey - er_h - hr * 0.16 - hh * hr * 0.2
            r_ = math.radians(ang * sx)
            dx = math.cos(r_) * hr * 0.22; dy = math.sin(r_) * hr * 0.22
            col_b = self.hair if not self.beard else self.beard
            c.drawLine(cx - dx, cy + dy, cx + dx, cy - dy, P(INK, a, stroke=13))
            c.drawLine(cx - dx, cy + dy, cx + dx, cy - dy, P(col_b, a, stroke=7))
        # nose
        c.drawOval(skia.Rect.MakeXYWH(fx - hr * 0.13 + p['turn'] * 4, hr * 0.12, hr * 0.26, hr * 0.2), P(self.nose_col, a))
        c.drawCircle(fx - hr * 0.04 + p['turn'] * 4, hr * 0.17, hr * 0.05, P('#ffffff', int(a * 0.6)))
        # mouth
        m = p['mouth']; mo = p['mouth_open']; my = hr * 0.5; mx = fx
        if m == 'smile':
            sp = skia.Path(); sp.moveTo(mx - hr * 0.28, my - 4); sp.quadTo(mx, my + hr * 0.22, mx + hr * 0.28, my - 4)
            c.drawPath(sp, P(INK, a, stroke=6))
        elif m == 'smirk':
            sp = skia.Path(); sp.moveTo(mx - hr * 0.2, my + 2); sp.quadTo(mx + hr * 0.1, my + hr * 0.12, mx + hr * 0.3, my - hr * 0.1)
            c.drawPath(sp, P(INK, a, stroke=6))
        elif m == 'flat':
            c.drawLine(mx - hr * 0.18, my + 2, mx + hr * 0.18, my + 2, P(INK, a, stroke=6))
        elif m == 'wavy':
            sp = skia.Path(); sp.moveTo(mx - hr * 0.3, my)
            for k in range(4): sp.quadTo(mx - hr * 0.3 + (k + 0.5) * hr * 0.15, my + (6 if k % 2 else -6), mx - hr * 0.3 + (k + 1) * hr * 0.15, my)
            c.drawPath(sp, P(INK, a, stroke=5))
        else:  # open mouths: grin, o, scream
            if m == 'grin':
                op = skia.Path(); op.moveTo(mx - hr * 0.36, my - 6); op.quadTo(mx, my - 2, mx + hr * 0.36, my - 6)
                op.quadTo(mx + hr * 0.2, my + hr * (0.25 + 0.2 * mo), mx, my + hr * (0.3 + 0.2 * mo))
                op.quadTo(mx - hr * 0.2, my + hr * (0.25 + 0.2 * mo), mx - hr * 0.36, my - 6); op.close()
            elif m == 'o':
                op = ellipse(mx, my + 6, hr * (0.12 + 0.06 * mo), hr * (0.14 + 0.12 * mo))
            else:  # scream
                op = path_from([(mx - hr * 0.3, my - 6), (mx + hr * 0.3, my - 6), (mx + hr * 0.24, my + hr * (0.35 + 0.35 * mo)),
                                (mx, my + hr * (0.45 + 0.4 * mo)), (mx - hr * 0.24, my + hr * (0.35 + 0.35 * mo))], True, 0.7)
            c.drawPath(op, P(INK, a, stroke=9)); c.drawPath(op, P('#5a1626', a))
            c.save(); c.clipPath(op, doAntiAlias=True)
            if m in ('grin', 'scream'):
                c.drawRect(skia.Rect.MakeLTRB(mx - hr, my - 10, mx + hr, my + hr * 0.08), P('#ffffff', a))
            c.drawOval(skia.Rect.MakeXYWH(mx - hr * 0.18, my + hr * 0.25 + hr * 0.25 * mo, hr * 0.36, hr * 0.3), P('#e8677a', a))
            c.restore()
        if p['sweat'] > 0:
            sa = int(a * p['sweat'])
            for (sx, sy, sz) in ((hr * 0.9, -hr * 0.5, 1.0), (-hr * 0.95, -hr * 0.2, 0.7)):
                d = path_from([(sx, sy - 16 * sz), (sx + 9 * sz, sy + 4 * sz), (sx, sy + 12 * sz), (sx - 9 * sz, sy + 4 * sz)], True, 0.9)
                c.drawPath(d, P('#bfe8ff', sa)); c.drawPath(d, P('#3a6f9a', sa, stroke=2.5))

    def _hair_hat(self, c, hr, p, fx, a):
        up = p['hair_up']
        if self.hair_style == 'short' or self.hair_style == 'bob':
            fr = path_from([(-hr * 0.98, -hr * 0.1), (-hr * 0.9, -hr * 0.7 - up * 30), (-hr * 0.3, -hr * 1.05 - up * 50),
                            (hr * 0.4, -hr * 1.02 - up * 50), (hr * 0.95, -hr * 0.55 - up * 30), (hr * 0.98, -hr * 0.1),
                            (hr * 0.6, -hr * 0.55), (hr * 0.1, -hr * 0.45), (-hr * 0.4, -hr * 0.6)], True, 0.8)
            fill_outline(c, fr, self.hair, INK, 4, a)
        if self.hair_style == 'spiky' or up > 0.3:
            for k in range(7):
                ang = math.radians(-90 + (k - 3) * 22)
                L = hr * (0.55 + 0.5 * up)
                b = (math.cos(ang) * hr * 0.75, math.sin(ang) * hr * 0.85)
                tip = (b[0] + math.cos(ang) * L, b[1] + math.sin(ang) * L)
                sp = path_from([(b[0] - 12, b[1] + 6), tip, (b[0] + 12, b[1] + 6)], True)
                fill_outline(c, sp, self.hair, INK, 3, a)
        if self.hair_style == 'bun':
            c.drawCircle(0, -hr * 1.05, hr * 0.35, P(INK, a)); c.drawCircle(0, -hr * 1.05, hr * 0.35 - 4, P(self.hair, a))
        hat = self.hat
        if hat == 'beanie':
            hp = skia.Path(); hp.moveTo(-hr * 1.02, -hr * 0.28 - up * 40)
            hp.cubicTo(-hr * 1.05, -hr * 1.5 - up * 40, hr * 1.05, -hr * 1.5 - up * 40, hr * 1.02, -hr * 0.28 - up * 40); hp.close()
            shaded(c, hp, self.hat_col, (-0.5, -1), 0.15, INK, 4.5, a)
            band = rrect(-hr * 1.08, -hr * 0.42 - up * 40, hr * 2.16, hr * 0.3, hr * 0.12)
            fill_outline(c, band, '#fdf6ea', INK, 4, a)
            c.drawCircle(hr * 0.1, -hr * 1.42 - up * 40, hr * 0.26, P(INK, a))
            c.drawPath(blob(hr * 0.1, -hr * 1.42 - up * 40, hr * 0.24, hr * 0.24, 9, 0.12, 2), P(self.pom, a))
        elif hat == 'stocking':
            hp = path_from([(-hr * 1.02, -hr * 0.3), (-hr * 0.6, -hr * 1.3), (hr * 0.3, -hr * 1.55), (hr * 1.2, -hr * 1.1),
                            (hr * 1.0, -hr * 0.6), (hr * 1.02, -hr * 0.3)], True, 0.7)
            shaded(c, hp, self.hat_col, (-0.5, -1), 0.15, INK, 4.5, a)
            c.drawPath(rrect(-hr * 1.08, -hr * 0.45, hr * 2.16, hr * 0.3, hr * 0.12), P(INK, a, stroke=8))
            c.drawPath(rrect(-hr * 1.08, -hr * 0.45, hr * 2.16, hr * 0.3, hr * 0.12), P('#fdf6ea', a))
            c.drawCircle(hr * 1.2, -hr * 1.0, hr * 0.22, P(INK, a)); c.drawCircle(hr * 1.2, -hr * 1.0, hr * 0.19, P('#fdf6ea', a))
        elif hat == 'mitre':
            hp = path_from([(-hr * 0.8, -hr * 0.5), (-hr * 0.85, -hr * 1.4), (0, -hr * 2.35), (hr * 0.85, -hr * 1.4), (hr * 0.8, -hr * 0.5)], True, 0.25)
            shaded(c, hp, '#c8283a', (-0.5, -1), 0.18, INK, 4.5, a)
            c.save(); c.clipPath(hp, doAntiAlias=True)
            c.drawRect(skia.Rect.MakeLTRB(-16, -hr * 2.4, 16, -hr * 0.4), P('#f0c64a', a))
            c.drawRect(skia.Rect.MakeLTRB(-hr, -hr * 0.75, hr, -hr * 0.5), P('#f0c64a', a))
            c.restore()
            cr = path_from([(0, -hr * 1.55), (12, -hr * 1.35), (0, -hr * 1.15), (-12, -hr * 1.35)])
            c.drawPath(cr, P('#fff4c2', a))
            # hair tufts under mitre
            for sx in (-1, 1):
                c.drawPath(blob(sx * hr * 0.85, -hr * 0.35, hr * 0.28, hr * 0.3, 8, 0.15, 3), P(INK, a, stroke=6))
                c.drawPath(blob(sx * hr * 0.85, -hr * 0.35, hr * 0.28, hr * 0.3, 8, 0.15, 3), P(self.beard or '#eeeeee', a))
        elif hat == 'bonnet':
            hp = skia.Path(); hp.moveTo(-hr * 1.15, hr * 0.2)
            hp.cubicTo(-hr * 1.3, -hr * 1.5, hr * 1.3, -hr * 1.5, hr * 1.15, hr * 0.2)
            hp.quadTo(hr * 0.9, -hr * 0.6, 0, -hr * 0.75); hp.quadTo(-hr * 0.9, -hr * 0.6, -hr * 1.15, hr * 0.2); hp.close()
            shaded(c, hp, self.hat_col, (-0.5, -1), 0.15, INK, 4.5, a)
            for sx in (-1, 1):
                c.drawLine(sx * hr * 0.95, hr * 0.15, sx * hr * 0.5, hr * 0.85, P(INK, a, stroke=9))
                c.drawLine(sx * hr * 0.95, hr * 0.15, sx * hr * 0.5, hr * 0.85, P('#f4e2c8', a, stroke=5))
        elif hat == 'flatcap':
            hp = skia.Path(); hp.moveTo(-hr * 1.0, -hr * 0.35)
            hp.cubicTo(-hr * 1.0, -hr * 1.25, hr * 0.9, -hr * 1.3, hr * 1.05, -hr * 0.55)
            hp.lineTo(hr * 1.45, -hr * 0.4); hp.quadTo(hr * 1.1, -hr * 0.25, hr * 0.9, -hr * 0.3); hp.close()
            shaded(c, hp, self.hat_col, (-0.5, -1), 0.15, INK, 4.5, a)
        elif hat == 'hood':
            pass

def shade_hex(h, k):
    c_ = shade(h, k)
    return '#%02x%02x%02x' % (skia.ColorGetR(c_), skia.ColorGetG(c_), skia.ColorGetB(c_))

# --------------------------------------------------------------------- motion helpers
def walk_pose(phase, speed=1.0, stride=26, arm=30):
    """phase in cycles. returns dict of limb angles + bob for a cartoon walk"""
    s = math.sin(2 * math.pi * phase)
    c_ = math.cos(2 * math.pi * phase)
    return dict(leg_l=(stride * s, max(0, -c_) * 35 * 0 + max(0, s) * 30), leg_r=(-stride * s, max(0, -s) * 30),
                arm_l=(-arm * s + 8, 15), arm_r=(arm * s + 8, 15), bob=-abs(c_) * 10)

def run_pose(phase, stride=50, arm=70):
    s = math.sin(2 * math.pi * phase); c_ = math.cos(2 * math.pi * phase)
    return dict(leg_l=(stride * s, 40 + 30 * max(0, s)), leg_r=(-stride * s, 40 + 30 * max(0, -s)),
                arm_l=(-arm * s + 10, 70), arm_r=(arm * s + 10, 70), bob=-abs(c_) * 22, lean=8)
