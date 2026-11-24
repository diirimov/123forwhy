"""Krampus, the Yule Cat and Mari Lwyd."""
import math, random
import skia
from gfx import *
from human import INK, shade_hex

# =====================================================================  KRAMPUS
KR = dict(x=0, y=0, s=1.0, face=1, lean=0.0, bob=0.0, sq=1.0, head_tilt=0.0, jaw=0.15, tongue=0.0,
          brow=(0, 0), brow_l=None, eyes='open', look=(0, 0), blink=0.0, pupil=1.0,
          arm_l=(25, 30), arm_r=(25, 30), leg_l=(10, 0), leg_r=(-6, 0), chain=0.0, alpha=255, eye_glow=1.0, smile=0.5,
          switch=True, silhouette=False)
FUR = '#2b1f1d'; FUR2 = '#4b3631'; FACE = '#8e3b2f'; MUZ = '#b8624a'; HORN = '#d9cbb0'

def horn_path(side, L=1.0):
    """ibex-like horn: sweeps up, then out, tip flaring outward"""
    spine = [(0, 0), (14, -80), (52, -160), (112, -222), (186, -252), (252, -246), (296, -212)]
    from gfx import path_from as _pf
    sp = _pf([(side * x * L, y * L) for x, y in spine], False, 1.0)
    meas = skia.PathMeasure(sp, False); tot = meas.getLength()
    po, pi = [], []
    for k in range(25):
        d = tot * k / 24
        pos, tan = meas.getPosTan(d)
        w = (52 * (1 - k / 24) ** 0.9 + 5) * L
        nx, ny = -tan.y(), tan.x()
        po.append((pos.x() + nx * w / 2, pos.y() + ny * w / 2)); pi.append((pos.x() - nx * w / 2, pos.y() - ny * w / 2))
    return path_from(po + pi[::-1], True, 0.0), po, pi

def draw_krampus(c, **kw):
    p = dict(KR); p.update(kw); a = p['alpha']; sil = p['silhouette']
    c.save(); c.translate(p['x'], p['y'] + p['bob'] * p['s']); c.scale(p['s'] * p['face'], p['s'])
    c.rotate(p['lean']); c.scale(1 / math.sqrt(p['sq']), p['sq'])
    def F(col_):
        return '#07060c' if sil else col_
    ow = 0 if sil else 5
    # shadow
    if not sil: c.drawOval(skia.Rect.MakeLTRB(-180, -14, 180, 16), P('#05040c', int(a * 0.35), blur=10))
    hip = (0, -300)
    # ---- goat legs (digitigrade)
    for side, lp in ((-1, p['leg_l']), (1, p['leg_r'])):
        hx = side * 62
        th = math.radians(side * lp[0] + 18 * side * 0)
        k1 = (hx + math.sin(math.radians(lp[0])) * 120 + 30, hip[1] + math.cos(math.radians(lp[0])) * 120)
        k2 = (k1[0] - 45 + math.sin(math.radians(lp[0] + lp[1])) * 30, k1[1] + 110)
        hf = (k2[0] + 10 + math.sin(math.radians(lp[0] + lp[1])) * 40, -18)
        leg = [(hx, hip[1]), k1, k2, hf]
        pth = skia.Path(); pth.moveTo(*leg[0]); pth.cubicTo(*leg[1], *leg[1], *leg[2]); pth.lineTo(*leg[3])
        if ow: c.drawPath(pth, P(INK, a, stroke=78 + ow * 2))
        c.drawPath(pth, P(F(FUR), a, stroke=78))
        # fur tufts
        if not sil:
            for t in (0.25, 0.55):
                tx = lerp(leg[0][0], leg[1][0], t * 2) if t < .5 else lerp(leg[1][0], leg[2][0], (t - .5) * 2)
                ty = lerp(leg[0][1], leg[1][1], t * 2) if t < .5 else lerp(leg[1][1], leg[2][1], (t - .5) * 2)
                c.drawLine(tx - 30, ty, tx - 44, ty + 16, P(FUR2, a, stroke=6))
        # hoof
        hp = path_from([(hf[0] - 30, hf[1] - 10), (hf[0] + 34, hf[1] - 10), (hf[0] + 40, hf[1] + 18), (hf[0] - 36, hf[1] + 18)], True, 0.3)
        fill_outline(c, hp, F('#151017'), INK, ow * 0.8, a)
        if not sil: c.drawLine(hf[0] + 2, hf[1] - 6, hf[0] + 4, hf[1] + 16, P('#000000', a, stroke=4))
    # ---- torso (shaggy barrel)
    tpts = [(-120, -270), (-150, -380), (-155, -480), (-120, -560), (-60, -600), (60, -600), (120, -560), (155, -480), (150, -380), (120, -270), (0, -245)]
    tp = path_from(fuzzy_edge(tpts, 16, 3, 11), True, 0.5)
    if sil:
        c.drawPath(tp, P('#07060c', a))
    else:
        c.drawPath(tp, P(INK, a, stroke=10))
        c.drawPath(tp, PS(rad((-50, -500), 260, [FUR2, FUR, '#160f10']), a))
        # chest fur strokes
        r_ = random.Random(5)
        for _ in range(26):
            x0 = r_.uniform(-120, 120); y0 = r_.uniform(-560, -290)
            c.drawLine(x0, y0, x0 + r_.uniform(-8, 8), y0 + r_.uniform(16, 30), P(FUR2 if r_.random() < .6 else '#120c0d', a, stroke=5))
        # belt + bells
        c.drawPath(path_from([(-150, -330), (0, -305), (150, -330)], False, 0.8), P('#120c10', a, stroke=26))
        for k, bx in enumerate((-110, -55, 0, 55, 110)):
            by = -320 + abs(bx) * -0.12 + 14
            sw = math.sin(p['chain'] * 2 * math.pi + k) * 8
            c.save(); c.translate(bx, by); c.rotate(sw)
            bl = path_from([(-16, -4), (16, -4), (20, 26), (-20, 26)], True, 0.5)
            fill_outline(c, bl, '#d9a62e', INK, 3, a)
            c.drawCircle(0, 28, 6, P(INK, a)); c.drawCircle(-6, 6, 4, P('#fff2b0', a))
            c.restore()
    # ---- chains across chest (catenary with links)
    if not sil:
        sway = math.sin(p['chain'] * 2 * math.pi) * 18
        for (x0, y0, x1, y1, sag) in ((-140, -540, 130, -400, 70), (-150, -420, 140, -360, 50)):
            for k in range(15):
                t = k / 14
                x = lerp(x0, x1, t); y = lerp(y0, y1, t) + sag * 4 * t * (1 - t) + sway * 4 * t * (1 - t)
                c.save(); c.translate(x, y); c.rotate((k % 2) * 90 + 20)
                c.drawOval(skia.Rect.MakeLTRB(-11, -6, 11, 6), P(INK, a, stroke=9))
                c.drawOval(skia.Rect.MakeLTRB(-11, -6, 11, 6), P('#9aa3b2', a, stroke=4.5))
                c.restore()
    # ---- head
    c.save(); c.translate(0, -600); c.rotate(p['head_tilt'])
    _krampus_head(c, p, a, sil)
    c.restore()
    # ---- arms (long, furry) with claws
    for side, ap in ((-1, p['arm_l']), (1, p['arm_r'])):
        sh = (side * 150, -490)
        pts = two_bone(sh, side * ap[0], 150, side * ap[1], 140)
        pth = skia.Path(); pth.moveTo(*pts[0]); pth.lineTo(*pts[1]); pth.lineTo(*pts[2])
        if ow: c.drawPath(pth, P(INK, a, stroke=62 + ow * 2))
        c.drawPath(pth, P(F(FUR), a, stroke=62))
        if not sil:
            c.drawPath(pth, P(FUR2, int(a * 0.5), stroke=18))
        hx, hy = pts[2]; ang = math.degrees(math.atan2(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]))
        c.save(); c.translate(hx, hy); c.rotate(-ang)
        hand = blob(0, 14, 34, 30, 9, 0.05, 4)
        fill_outline(c, hand, F('#3b2a33'), INK, ow * 0.8, a)
        for k in range(4):
            cx_ = -24 + k * 16
            cl = path_from([(cx_ - 6, 32), (cx_ + 6, 32), (cx_ + 2, 64)], True)
            fill_outline(c, cl, F('#e8dcc4'), INK, ow * 0.6, a)
        if side == 1 and p['switch']:
            # birch switch bundle
            for k in range(7):
                r_ = math.radians(-20 + k * 7)
                c.drawLine(0, 10, math.sin(r_) * 230, -math.cos(r_) * 230 + 10, P(INK, a, stroke=8))
                c.drawLine(0, 10, math.sin(r_) * 230, -math.cos(r_) * 230 + 10, P(F('#8a6a48'), a, stroke=4))
            c.drawRect(skia.Rect.MakeLTRB(-16, -30, 16, 0), P(F('#b0302a'), a))
        c.restore()
    c.restore()

def _krampus_head(c, p, a, sil):
    F = (lambda col_: '#07060c') if sil else (lambda col_: col_)
    ow = 0 if sil else 5
    # mane
    mane = path_from(fuzzy_edge([(-150, 20), (-170, -80), (-130, -200), (0, -250), (130, -200), (170, -80), (150, 20), (0, 50)], 22, 3, 7), True, 0.5)
    if not sil: c.drawPath(mane, P(INK, a, stroke=10))
    c.drawPath(mane, P(F('#1f1617'), a))
    # horns
    for side in (-1, 1):
        hp, po, pi = horn_path(side, 1.0)
        c.save(); c.translate(side * 55, -150)
        if ow: c.drawPath(hp, P(INK, a, stroke=10))
        if sil: c.drawPath(hp, P('#07060c', a))
        else:
            c.drawPath(hp, PS(lin((0, 0), (side * 300, -250), ['#7e6a54', HORN, '#f3ead6']), a))
            for k in range(2, 22, 2):
                c.drawLine(*po[k], *pi[k], P('#8a7660', a, stroke=4))
        c.restore()
    # ears
    for side in (-1, 1):
        ep = path_from([(side * 85, -120), (side * 200, -150), (side * 150, -95)], True, 0.5)
        fill_outline(c, ep, F(FACE), INK, ow, a)
        if not sil: c.drawPath(path_from([(side * 100, -118), (side * 175, -138), (side * 145, -105)], True, 0.5), P('#5e2420', a))
    # face (long goat-demon face)
    face = path_from([(-95, -170), (95, -170), (110, -60), (70, 60), (40, 120), (-40, 120), (-70, 60), (-110, -60)], True, 0.8)
    if sil:
        c.drawPath(face, P('#07060c', a))
    else:
        shaded(c, face, FACE, (-0.4, -1), 0.18, INK, 5, a)
        muz = path_from([(-60, 20), (60, 20), (55, 100), (0, 128), (-55, 100)], True, 0.8)
        c.drawPath(muz, P(MUZ, a))
    # eyes (always glowing, also in silhouette!)
    lx, ly = p['look']
    for side in (-1, 1):
        ex, ey = side * 48, -80
        mode = p['eyes']; hgt = 26 * (1 - p['blink'] * 0.9)
        if mode == 'narrow': hgt *= 0.45
        if mode == 'wide': hgt *= 1.35
        if p['eye_glow'] > 0:
            glow(c, ex, ey, 70, '#ffd34d', int(a * 0.55 * p['eye_glow']))
        eye = path_from([(ex - side * 30, ey + 6), (ex, ey - hgt), (ex + side * 34, ey - 4), (ex + side * 4, ey + hgt * 0.7)], True, 0.8)
        c.drawPath(eye, P(INK, a, stroke=7)); c.drawPath(eye, P('#ffd34d', a))
        c.save(); c.clipPath(eye, doAntiAlias=True)
        pr = 12 * p['pupil']
        c.drawOval(skia.Rect.MakeXYWH(ex + lx * 12 - pr * 0.5, ey + ly * 8 - pr, pr, pr * 2), P('#1a0505', a))
        c.drawCircle(ex + lx * 12 - 7, ey + ly * 8 - 8, 5, P('#ffffff', a))
        c.restore()
        # brows
        bang, bh = p['brow']
        if p['brow_l'] is not None and side == -1: bang, bh = p['brow_l']
        r_ = math.radians(bang * side)
        bx, by = ex, ey - 38 - bh * 28
        dx, dy = math.cos(r_) * 42, math.sin(r_) * 42
        c.drawLine(bx - dx, by + dy, bx + dx, by - dy, P(INK, a, stroke=24))
        c.drawLine(bx - dx, by + dy, bx + dx, by - dy, P(F('#1d1312'), a, stroke=15))
    if sil:
        return
    # nose
    c.drawOval(skia.Rect.MakeLTRB(-26, 28, 26, 52), P('#3a1514', a))
    for side in (-1, 1): c.drawCircle(side * 10, 42, 5, P('#120505', a))
    # mouth with fangs + jaw
    jaw = p['jaw']; sm = p['smile']
    mp = skia.Path(); mw = 70
    mp.moveTo(-mw, 72 - sm * 16); mp.quadTo(0, 82 + sm * 10, mw, 72 - sm * 16)
    mp.quadTo(mw * 0.6, 92 + jaw * 80, 0, 98 + jaw * 90); mp.quadTo(-mw * 0.6, 92 + jaw * 80, -mw, 72 - sm * 16); mp.close()
    c.drawPath(mp, P(INK, a, stroke=10)); c.drawPath(mp, P('#3a0a12', a))
    c.save(); c.clipPath(mp, doAntiAlias=True)
    for k in range(-3, 4):
        tx = k * 19
        c.drawPath(path_from([(tx - 8, 70), (tx + 8, 70), (tx, 90 + (12 if abs(k) == 2 else 0))], True), P('#fff7e6', a))
    for k in (-2, 2):
        c.drawPath(path_from([(k * 19 - 7, 110 + jaw * 85), (k * 19 + 7, 110 + jaw * 85), (k * 19, 88 + jaw * 75)], True), P('#fff7e6', a))
    c.restore()
    if p['tongue'] > 0:
        tl = p['tongue']
        tg = path_from([(-18, 95 + jaw * 60), (18, 95 + jaw * 60), (24, 95 + jaw * 60 + 140 * tl), (0, 110 + jaw * 60 + 170 * tl), (-24, 95 + jaw * 60 + 140 * tl)], True, 0.8)
        fill_outline(c, tg, '#d8304a', INK, 4, a)
        c.drawLine(0, 100 + jaw * 60, 0, 95 + jaw * 60 + 120 * tl, P('#a01f35', a, stroke=4))
    # goatee
    gt = path_from(fuzzy_edge([(-30, 120), (30, 120), (10, 200), (0, 215), (-10, 200)], 8, 3, 3), True, 0.6)
    c.drawPath(gt, P(INK, a, stroke=8)); c.drawPath(gt, P('#1d1312', a))

# =====================================================================  YULE CAT
YC = dict(x=0, y=0, s=1.0, face=1, head_tilt=0.0, eye_open=1.0, narrow=0.0, pupil=0.25, look=(0, 0), ear=0.0,
          mouth=0.0, tongue=0.0, nose=0.0, glow=1.0, paws=True, tail=0.0, alpha=255, body=True, rim='#7f9cff',
          confused=0.0, blink=0.0)
CAT = '#15131c'; CAT2 = '#24202f'

def draw_cat_head(c, p, a):
    # head (local coords, centre 0,0, radius ~ 260)
    ear_a = p['ear']
    for side in (-1, 1):
        c.save(); c.translate(side * 170, -170); c.rotate(side * (10 + ear_a * 25))
        ep = path_from([(-side * 90, 40), (side * 20, -190), (side * 120, 30)], True, 0.25)
        c.drawPath(ep, P(CAT, a)); c.drawPath(ep, P(p['rim'], int(a * 0.5), stroke=5))
        c.drawPath(path_from([(-side * 45, 20), (side * 18, -120), (side * 75, 20)], True, 0.25), P('#3b2236', a))
        c.restore()
    hpts = fuzzy_edge([(-300, 20), (-270, -160), (-150, -250), (0, -270), (150, -250), (270, -160), (300, 20),
                       (330, 120), (250, 200), (120, 250), (0, 255), (-120, 250), (-250, 200), (-330, 120)], 16, 3, 21)
    hp = path_from(hpts, True, 0.5)
    c.drawPath(hp, PS(rad((-60, -80), 380, [CAT2, CAT, '#0b0a10']), a))
    c.save(); c.clipPath(hp, doAntiAlias=True)
    rp = skia.Path(hp); rp.offset(16, 12)
    c.drawPath(hp, P(p['rim'], int(a * 0.55), stroke=14, blur=5))
    c.restore()
    # eyes
    lx, ly = p['look']; op = p['eye_open'] * (1 - p['narrow'] * 0.75) * (1 - p['blink'])
    for side in (-1, 1):
        ex, ey = side * 120, -30
        if p['glow'] > 0:
            glow(c, ex, ey, 210, '#ffcf3a', int(a * 0.45 * p['glow']))
        hgt = 78 * op
        tilt = side * (8 + 14 * p['narrow'])
        c.save(); c.translate(ex, ey); c.rotate(tilt)
        if hgt > 3:
            eye = path_from([(-95, 0), (0, -hgt), (95, 0), (0, hgt)], True, 0.95)
            c.drawPath(eye, P('#08070c', a, stroke=12))
            c.drawPath(eye, PS(rad((0, 0), 100, ['#fff6b0', '#ffd23a', '#f39a12']), a))
            c.save(); c.clipPath(eye, doAntiAlias=True)
            pw = 14 + 60 * p['pupil']
            px = lx * 40; py = ly * 20
            c.drawPath(path_from([(px, py - 90), (px + pw, py), (px, py + 90), (px - pw, py)], True, 0.9), P('#0a0606', a))
            c.drawCircle(px - 26, py - 30, 14, P('#ffffff', int(a * 0.9)))
            c.restore()
            # heavy lid when narrowing
            if p['narrow'] > 0:
                c.drawRect(skia.Rect.MakeLTRB(-110, -110, 110, -hgt * 0.3), P(CAT, a))
        else:
            c.drawLine(-90, 0, 90, 0, P('#ffd23a', a, stroke=6))
        c.restore()
    # brows for confusion
    if p['confused'] > 0:
        cf = p['confused']
        c.drawLine(-180, -150 - cf * 30, -70, -130, P(p['rim'], int(a * 0.8), stroke=10))
        c.drawLine(70, -125, 180, -110 + cf * 10, P(p['rim'], int(a * 0.8), stroke=10))
    # nose + mouth
    ny = 80 - p['nose'] * 6
    nose = path_from([(-28, ny - 10), (28, ny - 10), (0, ny + 18)], True, 0.6)
    c.drawPath(nose, P('#5a3a52', a)); c.drawCircle(-8, ny - 4, 5, P('#ffffff', int(a * 0.5)))
    mo = p['mouth']
    mp = skia.Path(); mp.moveTo(-80, ny + 50); mp.quadTo(-40, ny + 70, 0, ny + 24); mp.quadTo(40, ny + 70, 80, ny + 50)
    c.drawPath(mp, P(p['rim'], int(a * 0.6), stroke=6))
    if mo > 0:
        op_ = path_from([(-60, ny + 40), (60, ny + 40), (40, ny + 40 + 110 * mo), (-40, ny + 40 + 110 * mo)], True, 0.8)
        c.drawPath(op_, P('#3a1020', a))
        for sx in (-1, 1):
            c.drawPath(path_from([(sx * 50 - 8, ny + 42), (sx * 50 + 8, ny + 42), (sx * 48, ny + 42 + 40 * mo)], True), P('#fff8ea', a))
    if p['tongue'] > 0:
        t_ = p['tongue']
        tg = path_from([(-40, ny + 50), (40, ny + 50), (60 + 40 * t_, ny + 60 + 30 * t_), (30, ny + 90 + 30 * t_), (-30, ny + 80)], True, 0.8)
        c.drawPath(tg, P('#e04a6a', a)); c.drawPath(tg, P('#7a1a35', a, stroke=4))
    # whiskers
    for side in (-1, 1):
        for k in range(3):
            w0 = (side * 90, ny + 30 + k * 18)
            w1 = (side * (330 + k * 10), ny + 10 + k * 34 + p['nose'] * 6 * (k - 1))
            pp = skia.Path(); pp.moveTo(*w0); pp.quadTo(side * 220, w0[1] - 14, *w1)
            c.drawPath(pp, P('#cfd8ff', int(a * 0.75), stroke=4))

def draw_tail(c, base, t_phase, L=900, w=90, a=255, rim='#7f9cff', curl=1.0):
    pts = []
    for k in range(16):
        u = k / 15
        sw = math.sin(t_phase * 2 * math.pi - u * 2.2)
        x = base[0] + 120 * u + 160 * math.sin(u * 2.6) * curl + 90 * sw * u
        y = base[1] - L * u * 0.85 + 60 * u * u
        pts.append((x, y))
    pth = path_from(pts, False, 1.0)
    c.drawPath(pth, P('#000000', a, stroke=w + 6))
    for k, (ww, cc) in enumerate(((w, CAT),)):
        c.drawPath(pth, P(cc, a, stroke=ww))
    c.drawPath(pth, P(rim, int(a * 0.4), stroke=w * 0.14))
    c.drawCircle(*pts[-1], w * 0.5, P(CAT, a))

def draw_yule_cat(c, **kw):
    """towering cat seen from front: body + paws + head; head drawn at (0,-H)"""
    p = dict(YC); p.update(kw); a = p['alpha']
    c.save(); c.translate(p['x'], p['y']); c.scale(p['s'] * p['face'], p['s'])
    if p['body']:
        draw_tail(c, (260, -200), p['tail'], 1000, 110, a, p['rim'])
        body = path_from(fuzzy_edge([(-330, 0), (-360, -300), (-300, -600), (-200, -760), (200, -760), (300, -600), (360, -300), (330, 0)], 18, 3, 33), True, 0.5)
        c.drawPath(body, PS(rad((-80, -500), 600, [CAT2, CAT, '#08070c']), a))
        c.save(); c.clipPath(body, doAntiAlias=True); c.drawPath(body, P(p['rim'], int(a * 0.5), stroke=16, blur=6)); c.restore()
        # chest fluff
        fl = path_from(fuzzy_edge([(-150, -700), (150, -700), (120, -420), (0, -360), (-120, -420)], 18, 4, 9), True, 0.5)
        c.drawPath(fl, P(CAT2, a))
    if p['paws']:
        for side in (-1, 1):
            pw = blob(side * 190, -30, 120, 70, 10, 0.03, 8)
            c.drawPath(pw, P(CAT, a)); c.drawPath(pw, P(p['rim'], int(a * 0.5), stroke=5))
            for k in range(3):
                c.drawLine(side * 190 + (k - 1) * 40, -10, side * 190 + (k - 1) * 40, 30, P('#000000', a, stroke=6))
    c.save(); c.translate(0, -860); c.rotate(p['head_tilt'])
    draw_cat_head(c, p, a)
    c.restore()
    c.restore()

# =====================================================================  MARI LWYD
ML = dict(x=0, y=0, s=1.0, face=1, head_tilt=0.0, jaw=0.0, sway=0.0, ribbon=0.0, head_up=0.0, alpha=255,
          legs=0.0, bells=0.0, eye_glint=1.0, lean=0.0)
BONE = '#efe6d2'
RIB_COLS = ['#d62f3a', '#2f8f4e', '#f2c14e', '#3a7bd5', '#e86fa8', '#f08a24']

def _skull(c, p, a):
    # skull local: snout pointing right, cranium at left; size ~ 300 long
    jaw = p['jaw']
    # lower jaw (rotates around hinge at (-40, 40))
    c.save(); c.translate(-50, 30); c.rotate(jaw * 28)
    lj = path_from([(0, -6), (220, 10), (250, 26), (230, 48), (60, 46), (-10, 30)], True, 0.6)
    shaded(c, lj, BONE, (-0.3, -1), 0.16, INK, 5, a)
    for k in range(7):
        tx = 110 + k * 18
        c.drawPath(rrect(tx - 6, 2, 12, 18, 4), P('#fffaf0', a)); c.drawPath(rrect(tx - 6, 2, 12, 18, 4), P(INK, a, stroke=2.5))
    c.restore()
    # cranium + snout
    sk = path_from([(-150, -40), (-120, -120), (-40, -150), (60, -110), (170, -60), (240, -30), (262, 0), (250, 30),
                    (120, 40), (0, 50), (-90, 50), (-150, 20)], True, 0.7)
    shaded(c, sk, BONE, (-0.4, -1), 0.2, INK, 5, a)
    inner_shadow(c, sk, -8, 10, '#6d5f4a', 80, 10)
    # upper teeth
    for k in range(7):
        tx = 60 + k * 20
        c.drawPath(rrect(tx - 7, 30, 13, 20, 4), P('#fffaf0', a)); c.drawPath(rrect(tx - 7, 30, 13, 20, 4), P(INK, a, stroke=2.5))
    # nostril
    c.drawOval(skia.Rect.MakeXYWH(215, -24, 26, 16), P('#3a2c26', a))
    # suture lines
    c.drawPath(path_from([(-60, -140), (-40, -100), (-70, -60)], False, 0.8), P('#a8987a', a, stroke=3))
    # eye socket with glass bauble
    c.drawOval(skia.Rect.MakeXYWH(-70, -110, 90, 76), P('#2b211c', a))
    glow(c, -25, -72, 60, '#6effa0', int(a * 0.35 * p['eye_glint']))
    c.drawCircle(-25, -72, 30, P(INK, a)); c.drawCircle(-25, -72, 27, PS(rad((-35, -82), 30, ['#c9ffd8', '#2fae5a', '#0d4a26']), a))
    c.drawCircle(-36, -84, 8, P('#ffffff', a))
    # cloth ears
    for k, ex in enumerate((-110, -70)):
        ep = path_from([(ex - 18, -110), (ex - 30, -215), (ex + 20, -120)], True, 0.5)
        fill_outline(c, ep, '#1d1a2a' if k else '#2a2638', INK, 4, a)
    # rosettes / holly crown
    for k, (rx, ry) in enumerate(((-120, -95), (-90, -130), (-50, -140))):
        col_ = RIB_COLS[k * 2 % 6]
        for j in range(8):
            ang = j * math.pi / 4
            c.drawCircle(rx + math.cos(ang) * 12, ry + math.sin(ang) * 12, 9, P(col_, a))
        c.drawCircle(rx, ry, 9, P('#f2c14e', a)); c.drawCircle(rx, ry, 9, P(INK, a, stroke=2))

def draw_mari(c, **kw):
    p = dict(ML); p.update(kw); a = p['alpha']
    c.save(); c.translate(p['x'], p['y']); c.scale(p['s'] * p['face'], p['s']); c.rotate(p['lean'])
    t = p['sway']
    hx, hy = 40 + math.sin(t * 2 * math.pi) * 16, -560 - p['head_up'] * 60 + math.cos(t * 4 * math.pi) * 8
    # carrier legs under the sheet
    for side in (-1, 1):
        lg = math.sin(p['legs'] * 2 * math.pi + (0 if side < 0 else math.pi)) * 14
        c.drawLine(side * 40, -130, side * 40 + lg, -16, P(INK, a, stroke=34))
        c.drawLine(side * 40, -130, side * 40 + lg, -16, P('#2c2a3e', a, stroke=26))
        bt = rrect(side * 40 + lg - 24, -24, 52, 26, 10); fill_outline(c, bt, '#3b2418', INK, 3, a)
    # ribbons streaming from back of skull (behind sheet)
    for k in range(6):
        base = (hx - 120, hy - 60 + k * 14)
        pts = []
        for j in range(10):
            u = j / 9
            pts.append((base[0] - u * 260 - k * 10, base[1] + u * 300 + math.sin(p['ribbon'] * 6.28 + u * 5 + k) * 26 * u))
        pth = skia.Path(); pth.moveTo(*pts[0])
        for q in pts[1:]: pth.lineTo(*q)
        c.drawPath(pth, P(INK, a, stroke=22)); c.drawPath(pth, P(RIB_COLS[k], a, stroke=16))
    # white sheet drape (from skull down to the ground)
    wv = lambda u: math.sin(t * 2 * math.pi + u * 4) * 18
    sheet = path_from([(hx - 150, hy + 10), (hx + 60, hy + 30), (130 + wv(0.2), -320), (170 + wv(0.6), -120), (150 + wv(1), -70),
                       (70, -95 + wv(1.3) * 0.4), (0, -70), (-80, -95 + wv(1.7) * 0.4), (-160 + wv(2), -75), (-190 + wv(2.4), -160),
                       (-170 + wv(2.8), -350), (hx - 190, hy + 40)], True, 0.7)
    shaded(c, sheet, '#f4f1ea', (-0.6, -1), 0.14, INK, 5, a)
    c.save(); c.clipPath(sheet, doAntiAlias=True)
    for k in range(5):  # folds
        x0 = -140 + k * 65 + wv(k) * 0.5
        c.drawLine(x0, hy + 120, x0 + 15, -60, P('#c9c3d6', int(a * 0.6), stroke=10, blur=4))
    # decorative trim + bells
    c.drawPath(path_from([(-200, -110), (-60, -125), (60, -125), (200, -100)], False, 0.8), P('#d62f3a', a, stroke=16))
    c.restore()
    for k in range(5):
        bx = -140 + k * 70; by = -100 + math.sin(p['bells'] * 6.28 + k) * 3
        c.drawCircle(bx, by, 12, P(INK, a)); c.drawCircle(bx, by, 9, P('#e8c050', a)); c.drawCircle(bx - 3, by - 3, 3, P('#fff6c8', a))
    # skull on its pole
    c.save(); c.translate(hx, hy); c.rotate(p['head_tilt'])
    _skull(c, p, a)
    c.restore()
    c.restore()
