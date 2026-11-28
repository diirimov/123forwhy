"""Medieval cast: king, knight, merchant, bishop, peasant, jester, nobleman, townsfolk. Front-view toon rigs."""
import math
from core import *
from core import _hash
from rig import solve, props
from skel import draw_shape, ellipse, OW, draw_crown

SKIN = '#e8b896'
SKIN_SH = '#c98d6c'

CAST = {
    'king': dict(pr=props(thigh=225, shin=215, torso=330, shw=122, hipw=72, uarm=180, farm=165, head=239, neck=16),
                 skin='#e6b48f', robe='#9e1b2c', robe_dk='#5e0d18', trim='#f4efe4', hose='#6b1220', shoe='#2a160e',
                 sleeve='#9e1b2c', length=0.98, belly=40, hair='#d9d4cc', beard='full'),
    'knight': dict(pr=props(thigh=250, shin=240, torso=340, shw=132, hipw=62, uarm=190, farm=172, head=232, neck=16),
                   skin='#dca782', robe='#c9b48a', robe_dk='#8c7650', hose='#5a4a3a', shoe='#3a2a1c',
                   sleeve='#c9b48a', length=0.5, belly=0, hair='#6b3f22', beard='stubble'),
    'merchant': dict(pr=props(thigh=215, shin=205, torso=320, shw=118, hipw=80, uarm=175, farm=160, head=246, neck=16),
                     skin='#efc09c', robe='#2f6b45', robe_dk='#173d27', trim='#7a4b2a', hose='#5a1626',
                     shoe='#1d120c', sleeve='#2f6b45', length=0.62, belly=75, hair='#2a1a12', beard='mustache',
                     hat='chaperon', hatc='#7a1f2b'),
    'bishop': dict(pr=props(thigh=275, shin=265, torso=360, shw=100, hipw=52, uarm=195, farm=180, head=229, neck=16),
                   skin='#e4b392', robe='#f1ead8', robe_dk='#b9ae94', trim=GOLD, chas='#5b3a7a', hose='#ddd3bc',
                   shoe='#3a1f40', sleeve='#f1ead8', length=1.0, belly=0, hair='#bdb6ad', beard='none', hat='mitre'),
    'peasant': dict(pr=props(thigh=245, shin=235, torso=320, shw=104, hipw=50, uarm=185, farm=170, head=217, neck=16),
                    skin='#c98f68', robe='#7a5a3a', robe_dk='#4e3824', hose='#8a7458', shoe='#3b2a1c',
                    sleeve='#6b4e33', length=0.45, belly=0, hair='#5a3a1e', beard='stubble', hat='straw', patches=True),
    'jester': dict(pr=props(thigh=240, shin=230, torso=310, shw=100, hipw=50, uarm=185, farm=170, head=217, neck=16),
                   skin='#efc4a2', robe=BURG, robe2=GOLD, robe_dk='#3d0e15', hose=GOLD, hose2=BURG, shoe=BURG,
                   sleeve=BURG, sleeve2=GOLD, length=0.42, belly=0, hair='#9a3a1a', beard='none', hat='jester'),
    'noble': dict(pr=props(thigh=255, shin=245, torso=330, shw=112, hipw=54, uarm=188, farm=172, head=220, neck=16),
                  skin='#ebbf9d', robe='#24457a', robe_dk='#12264a', trim=GOLD, hose='#1a1a24', shoe='#120c0a',
                  sleeve='#2e5a9e', length=0.4, belly=0, hair='#3a2414', beard='goatee', hat='beret', hatc='#5a1626'),
    'woman': dict(pr=props(thigh=235, shin=225, torso=305, shw=96, hipw=58, uarm=175, farm=160, head=214, neck=16),
                  skin='#eec3a3', robe='#3f5a3a', robe_dk='#22331f', trim='#e8e0cc', hose='#3f5a3a',
                  shoe='#2a1a10', sleeve='#3f5a3a', length=1.0, belly=0, hair='#6a3a1a', beard='none',
                  hat='wimple'),
    'townsman': dict(pr=props(thigh=245, shin=235, torso=320, shw=106, hipw=54, uarm=185, farm=170, head=217, neck=16),
                     skin='#d9a07a', robe='#6a3a2a', robe_dk='#3a1e14', hose='#4a4038', shoe='#2a1a10',
                     sleeve='#6a3a2a', length=0.5, belly=10, hair='#3a2a1a', beard='full', hat='hood',
                     hatc='#4a5a3a'),
}


def variant(base, **kw):
    d = dict(CAST[base])
    d.update(kw)
    return d


def limb(c, a, b, r1, r2, col, frame, ow=OW):
    p = capsule(a, b, r1, r2)
    c.drawPath(p, stroke(INK, ow * 2))
    c.drawPath(p, fill(col))
    return p


def mitten(c, wr, a, col, frame, scale=1.0, curl=0.3):
    with Save(c):
        c.translate(*wr)
        c.rotate(math.degrees(a))
        h = smooth_poly([(-4, -15), (26, -17), (44, -8), (46, 8), (28, 16), (-4, 14)])
        c.drawPath(h, stroke(INK, OW * 2))
        c.drawPath(h, fill(col))
        th = capsule((10, -12), (24, -28), 7)
        c.drawPath(th, stroke(INK, OW * 2))
        c.drawPath(th, fill(col))
        for k in range(3):
            c.drawLine(30, -6 + k * 6, 44, -5 + k * 6.5, stroke(INK, 1.4, 0.7))


def face(c, hc, hang, S, ch, frame, expr):
    """cartoon medieval face. expr: dict(fear, joy, look(x), blink, mouth_open)"""
    fear = expr.get('fear', 0.0)
    joy = expr.get('joy', 0.0)
    look = expr.get('look', 0.0)
    trance = expr.get('trance', 0.0)
    turn = expr.get('turn', 0.0)
    mo = expr.get('mouth', 0.0)
    skin = ch['skin']
    fx = turn * 0.1 * S
    with Save(c):
        c.translate(*hc)
        c.rotate(math.degrees(hang))
        # ears
        for s in (-1, 1):
            e = ellipse(s * 0.34 * S, 0.04 * S, 0.06 * S, 0.1 * S)
            c.drawPath(e, stroke(INK, OW * 2))
            c.drawPath(e, fill(skin))
        hd = smooth_poly([(-0.33 * S, -0.15 * S), (-0.27 * S, -0.43 * S), (0, -0.5 * S), (0.27 * S, -0.43 * S),
                          (0.33 * S, -0.15 * S), (0.31 * S, 0.18 * S), (0.18 * S, 0.42 * S), (0, 0.48 * S),
                          (-0.18 * S, 0.42 * S), (-0.31 * S, 0.18 * S)])
        c.drawPath(hd, stroke(INK, OW * 2))
        c.drawPath(hd, fill(skin))
        with Save(c):
            c.clipPath(hd, doAntiAlias=True)
            q = skia.Path(hd)
            q.offset(-0.08 * S, -0.03 * S)
            c.drawPath(skia.Op(hd, q, skia.PathOp.kDifference_PathOp) or skia.Path(), fill(SKIN_SH, 0.55))
            for s in (-1, 1):
                c.drawPath(ellipse(s * 0.2 * S + fx, 0.16 * S, 0.07 * S, 0.045 * S), fill('#e07a6a', 0.35))
        # eyes
        er = 0.075 * S * (1 + 0.35 * fear)
        for s in (-1, 1):
            ex, ey = s * 0.13 * S + fx, -0.02 * S
            w = ellipse(ex, ey, er * 0.82, er)
            c.drawPath(w, fill('#fbf7ee'))
            c.drawPath(w, stroke(INK, 2.6))
            pr_ = er * (0.42 - 0.15 * fear)
            px = ex + look * er * 0.4 + turn * er * 0.3
            c.drawPath(ellipse(px, ey + er * 0.05, pr_, pr_), fill('#1c120e'))
            c.drawPath(ellipse(px - pr_ * 0.35, ey - pr_ * 0.3, pr_ * 0.3, pr_ * 0.3), fill('#ffffff'))
            # lids: trance = heavy lids
            lid = trance * 0.6 + expr.get('blink', 0) + (0.25 if joy > 0.5 else 0) - fear * 0.3
            if lid > 0.02:
                with Save(c):
                    c.clipPath(w, doAntiAlias=True)
                    c.drawRect(skia.Rect.MakeLTRB(ex - er, ey - er, ex + er, ey - er + 2 * er * clamp(lid)),
                               fill(skin))
                    c.drawLine(ex - er, ey - er + 2 * er * clamp(lid), ex + er, ey - er + 2 * er * clamp(lid),
                               stroke(INK, 2.4))
            # brows: fear = raised inner, worried
            bp = P()
            by = ey - er - 0.05 * S - fear * 0.04 * S
            bp.moveTo(ex - s * 0.08 * S, by + (-0.03 * S * fear if True else 0) + 0.02 * S * joy)
            bp.quadTo(ex, by - 0.03 * S, ex + s * 0.08 * S, by + 0.025 * S * fear - 0.01 * S * joy)
            c.drawPath(bp, stroke(INK, 4.5))
        # nose
        n = P()
        n.moveTo(fx * 1.3 + 0.01 * S, 0.02 * S)
        n.quadTo(fx * 1.3 + 0.07 * S, 0.14 * S, fx * 1.3 - 0.02 * S, 0.16 * S)
        c.drawPath(n, stroke(INK, 2.6))
        # mouth
        my = 0.29 * S
        mw = 0.1 * S
        if mo > 0.15 or fear > 0.6:
            o = max(mo, fear * 0.6)
            mp = ellipse(fx, my, mw * (0.7 + 0.3 * joy), 0.03 * S + o * 0.07 * S)
            c.drawPath(mp, fill('#4a1418'))
            c.drawPath(mp, stroke(INK, 2.6))
            if joy > 0.3:
                c.drawRect(skia.Rect.MakeXYWH(fx - mw * 0.6, my - 0.03 * S - o * 0.05 * S, mw * 1.2, 0.025 * S),
                           fill('#ffffff'))
        else:
            mp = P()
            curve = 0.05 * S * (joy - fear * 0.8 - 0.2 * trance)
            mp.moveTo(fx - mw, my - curve * 0.3)
            mp.quadTo(fx, my + curve, fx + mw, my - curve * 0.3)
            c.drawPath(mp, stroke(INK, 3.2))
        # beards / hair
        b = ch.get('beard', 'none')
        hairc = ch['hair']
        if b == 'full':
            bd = smooth_poly([(-0.3 * S, 0.08 * S), (-0.27 * S, 0.35 * S), (-0.12 * S, 0.6 * S), (0, 0.66 * S),
                              (0.12 * S, 0.6 * S), (0.27 * S, 0.35 * S), (0.3 * S, 0.08 * S), (0.16 * S, 0.3 * S),
                              (0.06 * S, 0.24 * S), (-0.06 * S, 0.24 * S), (-0.16 * S, 0.3 * S)])
            c.drawPath(bd, stroke(INK, OW * 2))
            c.drawPath(bd, fill(hairc))
            for k in range(6):
                c.drawLine(-0.15 * S + k * 0.06 * S, 0.36 * S, -0.13 * S + k * 0.055 * S, 0.52 * S,
                           stroke(INK, 1.4, 0.5))
            # mouth over beard
            mp = P()
            mp.moveTo(fx - mw * 0.8, my + 0.01 * S)
            mp.quadTo(fx, my + 0.03 * S + (mo + fear * 0.5) * 0.06 * S, fx + mw * 0.8, my + 0.01 * S)
            c.drawPath(mp, stroke('#3a1210', 4))
        if b in ('mustache', 'full', 'goatee'):
            for s in (-1, 1):
                m = P()
                m.moveTo(fx, 0.22 * S)
                m.cubicTo(fx + s * 0.08 * S, 0.17 * S, fx + s * 0.16 * S, 0.22 * S,
                          fx + s * 0.2 * S, 0.14 * S + (0.02 * S if b == 'mustache' else 0.05 * S))
                c.drawPath(m, stroke(INK, 9))
                c.drawPath(m, stroke(hairc, 5.5))
        if b == 'goatee':
            g = smooth_poly([(-0.06 * S, 0.38 * S), (0.06 * S, 0.38 * S), (0, 0.55 * S)])
            c.drawPath(g, stroke(INK, OW * 2))
            c.drawPath(g, fill(hairc))
        if b == 'stubble':
            for k in range(26):
                a_ = k * 2.4
                rr = 0.28 * S + 0.06 * S * _hash(k, 3)
                x, y = math.cos(a_ * 0.25 + 0.4) * rr * 0.9, 0.12 * S + abs(math.sin(a_ * 0.25 + 0.4)) * rr * 0.9
                if y > 0.18 * S:
                    c.drawPath(ellipse(x, y, 1.6, 1.6), fill(INK, 0.4))


def hat(c, hc, hang, S, ch, frame, t, sway=0.0):
    h = ch.get('hat', None)
    hairc = ch['hair']
    with Save(c):
        c.translate(*hc)
        c.rotate(math.degrees(hang))
        if h in (None, 'straw', 'beret', 'chaperon', 'jester') or ch.get('beard') in ('full',):
            # hair cap
            hp = smooth_poly([(-0.36 * S, 0.02 * S), (-0.34 * S, -0.35 * S), (0, -0.56 * S), (0.34 * S, -0.35 * S),
                              (0.36 * S, 0.02 * S), (0.27 * S, -0.3 * S), (0, -0.38 * S), (-0.27 * S, -0.3 * S)])
            if h != 'wimple':
                c.drawPath(hp, stroke(INK, OW * 2))
                c.drawPath(hp, fill(hairc))
        if h == 'straw':
            br = ellipse(0, -0.36 * S, 0.62 * S, 0.13 * S)
            c.drawPath(br, stroke(INK, OW * 2))
            c.drawPath(br, fill('#d8b25a'))
            cr = smooth_poly([(-0.3 * S, -0.38 * S), (-0.24 * S, -0.66 * S), (0.24 * S, -0.66 * S), (0.3 * S, -0.38 * S)])
            c.drawPath(cr, stroke(INK, OW * 2))
            c.drawPath(cr, fill('#c99e46'))
            for k in range(9):
                c.drawLine(-0.55 * S + k * 0.14 * S, -0.38 * S, -0.5 * S + k * 0.13 * S, -0.3 * S,
                           stroke('#8a6a28', 1.5))
            c.drawRect(skia.Rect.MakeXYWH(-0.29 * S, -0.46 * S, 0.58 * S, 0.06 * S), fill('#7a3a1a'))
        elif h == 'beret':
            br = smooth_poly([(-0.42 * S, -0.3 * S), (-0.3 * S, -0.62 * S), (0.25 * S, -0.66 * S), (0.5 * S, -0.42 * S),
                              (0.3 * S, -0.3 * S)])
            c.drawPath(br, stroke(INK, OW * 2))
            c.drawPath(br, fill(ch['hatc']))
            fp = P()
            fp.moveTo(0.25 * S, -0.55 * S)
            fp.cubicTo(0.5 * S, -0.95 * S, 0.8 * S, -0.9 * S, 0.95 * S + clamp(sway / 60.0, -1, 1) * 0.1 * S, -0.7 * S)
            c.drawPath(fp, stroke(INK, 16))
            c.drawPath(fp, stroke('#f2ecdc', 10))
        elif h == 'chaperon':
            cp = smooth_poly([(-0.45 * S, -0.22 * S), (-0.4 * S, -0.6 * S), (0, -0.75 * S), (0.42 * S, -0.62 * S),
                              (0.47 * S, -0.22 * S), (0.2 * S, -0.3 * S), (-0.2 * S, -0.3 * S)])
            c.drawPath(cp, stroke(INK, OW * 2))
            c.drawPath(cp, fill(ch['hatc']))
            tail = P()
            tail.moveTo(0.4 * S, -0.5 * S)
            tail.cubicTo(0.75 * S, -0.4 * S, 0.7 * S, 0.2 * S, 0.55 * S + clamp(sway / 60.0, -1, 1) * 0.1 * S, 0.5 * S)
            c.drawPath(tail, stroke(INK, 26))
            c.drawPath(tail, stroke(ch['hatc'], 18))
        elif h == 'hood':
            hd = smooth_poly([(-0.48 * S, 0.5 * S), (-0.5 * S, -0.3 * S), (0, -0.66 * S), (0.5 * S, -0.3 * S),
                              (0.48 * S, 0.5 * S), (0.34 * S, 0.1 * S), (0.3 * S, -0.32 * S), (0, -0.46 * S),
                              (-0.3 * S, -0.32 * S), (-0.34 * S, 0.1 * S)])
            c.drawPath(hd, stroke(INK, OW * 2))
            c.drawPath(hd, fill(ch['hatc']))
        elif h == 'wimple':
            wp = smooth_poly([(-0.44 * S, 0.62 * S), (-0.46 * S, -0.2 * S), (-0.3 * S, -0.58 * S), (0, -0.64 * S),
                              (0.3 * S, -0.58 * S), (0.46 * S, -0.2 * S), (0.44 * S, 0.62 * S), (0.32 * S, 0.3 * S),
                              (0.33 * S, -0.3 * S), (0, -0.44 * S), (-0.33 * S, -0.3 * S), (-0.32 * S, 0.3 * S)])
            c.drawPath(wp, stroke(INK, OW * 2))
            c.drawPath(wp, fill(ch.get('trim', '#efe8d6')))
            c.drawLine(-0.28 * S, 0.42 * S, 0.28 * S, 0.42 * S, stroke(INK, 2))
        elif h == 'jester':
            for k, (ex, ey, col) in enumerate([(-0.78, -0.55, BURG), (0.0, -1.05, GOLD), (0.78, -0.55, BURG)]):
                sw = math.sin(t * 6 + k * 1.7) * 0.06 * S + clamp(sway / 60.0, -1, 1) * 0.12 * S
                tip = (ex * S + sw, ey * S + abs(sw) * 0.3)
                pp = smooth_poly([(-0.32 * S + k * 0.2 * S, -0.3 * S), (ex * 0.6 * S, (ey * 0.75) * S - 0.05 * S),
                                  tip, (ex * 0.45 * S + 0.08 * S, ey * 0.55 * S), (-0.12 * S + k * 0.22 * S, -0.42 * S)],
                                 True, 0.4)
                c.drawPath(pp, stroke(INK, OW * 2))
                c.drawPath(pp, fill(col))
                c.drawPath(ellipse(tip[0], tip[1], 0.06 * S, 0.06 * S), stroke(INK, OW * 2))
                c.drawPath(ellipse(tip[0], tip[1], 0.06 * S, 0.06 * S), fill('#ffd75e'))
            band = skia.Rect.MakeXYWH(-0.37 * S, -0.38 * S, 0.74 * S, 0.1 * S)
            c.drawRoundRect(band, 8, 8, stroke(INK, OW * 2))
            c.drawRoundRect(band, 8, 8, fill(GOLD))
        elif h == 'mitre':
            m = poly([(-0.3 * S, -0.3 * S), (-0.26 * S, -0.85 * S), (0, -1.12 * S), (0.26 * S, -0.85 * S),
                      (0.3 * S, -0.3 * S)])
            c.drawPath(m, stroke(INK, OW * 2))
            c.drawPath(m, fill('#f6f0e0'))
            c.drawRect(skia.Rect.MakeXYWH(-0.04 * S, -1.05 * S, 0.08 * S, 0.75 * S), fill(GOLD))
            c.drawRect(skia.Rect.MakeXYWH(-0.3 * S, -0.42 * S, 0.6 * S, 0.08 * S), fill(GOLD))
            c.drawPath(m, stroke(INK, 2))


def robe_path(J, pr, ch, flare=1.0, sway=0.0):
    """tunic/robe from shoulders to hem, hem follows knees/ankles"""
    L = ch['length']
    shL, shR = J['shL'], J['shR']
    hipL, hipR = J['hipL'], J['hipR']
    kneeL, kneeR = J['kneeL'], J['kneeR']
    ankL, ankR = J['ankL'], J['ankR']
    belly = ch.get('belly', 0)
    waistL = mid(shL, hipL, 0.62)
    waistR = mid(shR, hipR, 0.62)

    def hemp(hip, knee, ank, u):
        if u <= 0.5:
            return mid(hip, knee, u * 2)
        return mid(knee, ank, (u - 0.5) * 2)
    hL = hemp(hipL, kneeL, ankL, L)
    hR = hemp(hipR, kneeR, ankR, L)
    fl = (28 + 60 * L) * flare
    pts = [add(shL, (6, -6)), add(shR, (-6, -6)), add(shR, (10, 40)), add(waistR, (belly * 0.6 + 6, 0)),
           add(hipR, (belly * 0.35 + 18, 10)), (hR[0] + fl + sway, hR[1] + 8),
           (lerp(hL[0], hR[0], 0.5) + sway * 0.7, max(hL[1], hR[1]) + 14),
           (hL[0] - fl + sway, hL[1] + 8), add(hipL, (-belly * 0.35 - 18, 10)), add(waistL, (-belly * 0.6 - 6, 0)),
           add(shL, (-10, 40))]
    return smooth_poly(pts, True, 0.35), (hL, hR)


def draw_human(c, J, pr, pose, ch, frame, t, expr=None, armor=None, sway=0.0, props_=None):
    """J from rig.solve. armor: dict piece->(dx,dy,rot,alpha) for knight; None = full armor attached, False = none"""
    expr = expr or {}
    S = pr['head']
    is_knight = armor is not None
    hose = ch['hose']
    hose2 = ch.get('hose2', hose)
    # legs
    for s in ('L', 'R'):
        col = hose if s == 'L' else hose2
        limb(c, J['hip' + s], J['knee' + s], 30, 26, col, frame)
        limb(c, J['knee' + s], J['ank' + s], 26, 20, col, frame)
        sg = -1 if s == 'L' else 1
        ft = J['foot' + s]
        shoe = capsule(J['ank' + s], add(ft, (sg * 12, 0)), 18, 13)
        if ch.get('hat') == 'jester':
            tip = add(ft, (sg * 40, -26))
            shoe = skia.Op(shoe, capsule(add(ft, (sg * 6, 0)), tip, 10, 4), skia.PathOp.kUnion_PathOp) or shoe
        c.drawPath(shoe, stroke(INK, OW * 2))
        c.drawPath(shoe, fill(ch['shoe']))
        if is_knight:
            draw_armor_leg(c, J, s, frame, armor)
    # body / robe
    rp, hems = robe_path(J, pr, ch, sway=sway)
    c.drawPath(rp, stroke(INK, OW * 2))
    if ch.get('robe2'):
        c.drawPath(rp, fill(ch['robe']))
        with Save(c):
            c.clipPath(rp, doAntiAlias=True)
            mx = J['neck'][0]
            c.drawRect(skia.Rect.MakeLTRB(mx, -2000, mx + 800, 200), fill(ch['robe2']))
            # diamonds
            for i in range(-6, 7):
                for j in range(-14, 2):
                    x = mx + i * 46 + (j % 2) * 23
                    y = J['neck'][1] + 60 + (j + 14) * 40
                    d = poly([(x, y - 18), (x + 12, y), (x, y + 18), (x - 12, y)])
                    c.drawPath(d, fill(ch['robe'] if x > mx else ch['robe2'], 0.6))
    else:
        c.drawPath(rp, lin_grad((J['shL'][0], 0), (J['shR'][0], 0), [ch['robe'], ch['robe'], ch['robe_dk']],
                                [0, 0.55, 1.0]))
    with Save(c):
        c.clipPath(rp, doAntiAlias=True)
        # folds
        for k in range(5):
            u = (k + 0.5) / 5
            top = mid(J['hipL'], J['hipR'], u)
            bot = mid(hems[0], hems[1], u)
            fp = P()
            fp.moveTo(top[0], top[1] - 40)
            fp.quadTo(lerp(top[0], bot[0], 0.5) + sway * 0.2, lerp(top[1], bot[1], 0.5), bot[0] + (u - 0.5) * 60,
                      bot[1])
            c.drawPath(fp, stroke(INK, 2.0, 0.35))
        # belt
        wl, wr_ = mid(J['shL'], J['hipL'], 0.66), mid(J['shR'], J['hipR'], 0.66)
        belly = ch.get('belly', 0)
        bp = P()
        bp.moveTo(wl[0] - 80, wl[1])
        bp.quadTo(mid(wl, wr_)[0], mid(wl, wr_)[1] + 10 + belly * 0.25, wr_[0] + 80, wr_[1])
        if ch.get('hat') == 'straw':
            c.drawPath(bp, stroke('#b89a5a', 10))
        elif ch.get('hat') != 'wimple' and 'chas' not in ch:
            c.drawPath(bp, stroke('#2a1a10', 16))
            bc = mid(wl, wr_)
            c.drawRect(skia.Rect.MakeXYWH(bc[0] - 12, bc[1] - 10 + belly * 0.12, 24, 20), fill(GOLD))
        if 'trim' in ch and ch.get('hat') not in ('wimple',) and 'chas' not in ch:
            # hem trim
            hp = P()
            hp.moveTo(hems[0][0] - 200, hems[0][1] + 6)
            hp.lineTo(hems[1][0] + 200, hems[1][1] + 6)
            c.drawPath(hp, stroke(ch['trim'], 26))
        if 'chas' in ch:
            n = J['neck']
            ch_p = smooth_poly([add(J['shL'], (10, 0)), add(J['shR'], (-10, 0)), add(J['shR'], (20, 260)),
                                (n[0], n[1] + 520), add(J['shL'], (-20, 260))], True, 0.3)
            c.drawPath(ch_p, fill(ch['chas']))
            c.drawPath(ch_p, stroke(INK, 3))
            c.drawRect(skia.Rect.MakeXYWH(n[0] - 14, n[1] + 10, 28, 480), fill(GOLD))
            c.drawLine(n[0] - 90, n[1] + 140, n[0] + 90, n[1] + 140, stroke(GOLD, 26, cap=skia.Paint.kButt_Cap))
        if ch.get('hat') == 'wimple':
            ap = poly([add(mid(J['hipL'], J['hipR']), (-70, -40)), add(mid(J['hipL'], J['hipR']), (70, -40)),
                       (hems[1][0] - 20, hems[1][1]), (hems[0][0] + 20, hems[0][1])])
            c.drawPath(ap, fill('#e9e2cf'))
            c.drawPath(ap, stroke(INK, 3))
        if ch.get('patches'):
            for k, (u, v) in enumerate(((0.3, 0.5), (0.7, 0.75))):
                q = mid(mid(J['shL'], J['hipL'], v), mid(J['shR'], J['hipR'], v), u)
                r = skia.Rect.MakeXYWH(q[0] - 22, q[1] - 18, 44, 36)
                c.drawRect(r, fill('#5e4630'))
                c.drawRect(r, stroke(INK, 2))
    if ch.get('hat') == 'jester':
        # zigzag hem bells
        for k in range(7):
            u = k / 6
            q = mid(hems[0], hems[1], u)
            q = (lerp(hems[0][0] - 60, hems[1][0] + 60, u), q[1] + 18)
            c.drawPath(ellipse(q[0], q[1], 11, 11), stroke(INK, OW * 2))
            c.drawPath(ellipse(q[0], q[1], 11, 11), fill('#ffd75e'))
    if 'trim' in ch and ch.get('hat') is None and 'chas' not in ch and ch.get('beard') == 'full':
        # ermine collar (king)
        col = smooth_poly([add(J['shL'], (-24, -10)), add(J['neck'], (0, -10)), add(J['shR'], (24, -10)),
                           add(J['shR'], (10, 60)), add(J['neck'], (0, 90)), add(J['shL'], (-10, 60))], True, 0.4)
        c.drawPath(col, stroke(INK, OW * 2))
        c.drawPath(col, fill('#f6f1e6'))
        for k in range(9):
            q = add(J['neck'], ((k - 4) * 30, 20 + (k % 3) * 18))
            c.drawPath(ellipse(q[0], q[1], 4, 7), fill('#111111'))
    if is_knight:
        draw_armor_body(c, J, frame, armor)
    # neck
    limb(c, J['neck'], add(J['headc'], (0, S * 0.3)), 24, 24, ch['skin'], frame)
    # arms
    for s in ('L', 'R'):
        col = ch['sleeve'] if s == 'L' else ch.get('sleeve2', ch['sleeve'])
        puff = 34 if ch.get('hat') == 'beret' else 28
        limb(c, J['sh' + s], J['elb' + s], puff, 24, col, frame)
        limb(c, J['elb' + s], J['wr' + s], 23, 19, col, frame)
        if ch.get('hat') == 'beret' or 'trim' in ch:
            cuffc = ch.get('trim', GOLD)
            q = J['wr' + s]
            c.drawPath(ellipse(q[0], q[1], 20, 20), stroke(INK, OW * 2))
            c.drawPath(ellipse(q[0], q[1], 20, 20), fill(cuffc))
        if is_knight:
            draw_armor_arm(c, J, s, frame, armor)
        gcol = '#9aa3ad' if (is_knight and armor.get('vamb' + s, (0, 0, 0, 1))[3] > 0.5) else ch['skin']
        mitten(c, J['wr' + s], J['hand%sa' % s], gcol, frame)
    if props_:
        for fn in props_:
            fn(c, J)
    # head
    hc, hang = J['headc'], J['hang']
    face(c, hc, hang, S, ch, frame, dict(expr, turn=pose['turn']))
    hat(c, hc, hang, S, ch, frame, t, sway)
    if ch.get('crown', 0) > 0:
        draw_crown(c, add(hc, rot((0, -S * 0.5), hang)), hang, 0.95, frame, ch['crown'])
    if ch.get('hat') == 'mitre':
        pass
    if is_knight:
        draw_helm(c, J, pr, frame, armor, t)


# ------------------------------------------------------------------ knight armor (detachable pieces)
STEEL = '#aeb7c2'
STEEL_DK = '#5d6773'


def _piece(c, path, frame, off, pivot):
    """off = (dx, dy, rot, alpha)"""
    dx, dy, r, a = off
    if a <= 0.01:
        return
    with Save(c):
        c.translate(dx, dy)
        c.rotate(math.degrees(r), pivot[0], pivot[1])
        c.drawPath(path, stroke(INK, OW * 2, a))
        p = lin_grad((pivot[0] - 60, pivot[1] - 60), (pivot[0] + 60, pivot[1] + 60), ['#e8eef4', STEEL, STEEL_DK])
        p.setAlphaf(a)
        c.drawPath(path, p)
        c.drawPath(path, stroke('#ffffff', 2.0, 0.5 * a))


def draw_armor_leg(c, J, s, frame, armor):
    kn, an, hip = J['knee' + s], J['ank' + s], J['hip' + s]
    _piece(c, capsule(kn, an, 30, 24), frame, armor.get('greave' + s, (0, 0, 0, 1)), mid(kn, an))
    _piece(c, capsule(hip, kn, 34, 30), frame, armor.get('cuisse' + s, (0, 0, 0, 1)), mid(hip, kn))
    _piece(c, ellipse(kn[0], kn[1], 26, 24), frame, armor.get('cuisse' + s, (0, 0, 0, 1)), kn)


def draw_armor_body(c, J, frame, armor):
    shL, shR, n = J['shL'], J['shR'], J['neck']
    hipL, hipR = J['hipL'], J['hipR']
    bp = smooth_poly([add(shL, (12, 0)), add(shR, (-12, 0)), add(shR, (6, 120)), add(hipR, (20, -40)),
                      add(mid(hipL, hipR), (0, -20)), add(hipL, (-20, -40)), add(shL, (-6, 120))], True, 0.3)
    off = armor.get('breast', (0, 0, 0, 1))
    _piece(c, bp, frame, off, mid(shL, hipR))
    if off[3] > 0.5:
        with Save(c):
            c.translate(off[0], off[1])
            c.rotate(math.degrees(off[2]), *mid(shL, hipR))
            c.drawLine(n[0], n[1] + 20, n[0], n[1] + 260, stroke(STEEL_DK, 4))
            # red cross tabard
            c.drawRect(skia.Rect.MakeXYWH(n[0] - 70, n[1] + 120, 140, 26), fill('#a0141f'))
            c.drawRect(skia.Rect.MakeXYWH(n[0] - 13, n[1] + 40, 26, 180), fill('#a0141f'))
    fa = smooth_poly([add(hipL, (-40, -30)), add(hipR, (40, -30)), add(hipR, (52, 70)), add(hipL, (-52, 70))], True, 0.2)
    _piece(c, fa, frame, armor.get('fauld', (0, 0, 0, 1)), mid(hipL, hipR))


def draw_armor_arm(c, J, s, frame, armor):
    sh, el, wr = J['sh' + s], J['elb' + s], J['wr' + s]
    _piece(c, capsule(el, wr, 26, 22), frame, armor.get('vamb' + s, (0, 0, 0, 1)), mid(el, wr))
    _piece(c, capsule(sh, el, 30, 26), frame, armor.get('vamb' + s, (0, 0, 0, 1)), mid(sh, el))
    _piece(c, ellipse(sh[0], sh[1] - 4, 46, 38), frame, armor.get('paul' + s, (0, 0, 0, 1)), sh)


def draw_helm(c, J, pr, frame, armor, t):
    off = armor.get('helm', (0, 0, 0, 1))
    if off[3] <= 0.01:
        return
    hc, hang = J['headc'], J['hang']
    S = pr['head']
    with Save(c):
        c.translate(off[0], off[1])
        c.rotate(math.degrees(off[2]), *hc)
        c.translate(*hc)
        c.rotate(math.degrees(hang))
        hp = poly([(-0.42 * S, -0.55 * S), (0.42 * S, -0.55 * S), (0.45 * S, 0.5 * S), (-0.45 * S, 0.5 * S)])
        hp = smooth_poly([(-0.42 * S, -0.52 * S), (0, -0.62 * S), (0.42 * S, -0.52 * S), (0.46 * S, 0.0),
                          (0.44 * S, 0.52 * S), (0, 0.58 * S), (-0.44 * S, 0.52 * S), (-0.46 * S, 0.0)], True, 0.25)
        c.drawPath(hp, stroke(INK, OW * 2))
        c.drawPath(hp, lin_grad((-0.4 * S, -0.5 * S), (0.4 * S, 0.5 * S), ['#eef3f8', STEEL, STEEL_DK]))
        c.drawRect(skia.Rect.MakeXYWH(-0.38 * S, -0.08 * S, 0.76 * S, 0.07 * S), fill('#0d0d12'))
        c.drawRect(skia.Rect.MakeXYWH(-0.03 * S, -0.55 * S, 0.06 * S, 1.1 * S), fill(STEEL_DK))
        for k in range(5):
            for j in range(2):
                c.drawPath(ellipse(0.12 * S + j * 0.08 * S, 0.1 * S + k * 0.07 * S, 4, 4), fill('#0d0d12'))
        # plume
        pl = P()
        pl.moveTo(0, -0.6 * S)
        sw = math.sin(t * 5) * 0.1 * S
        pl.cubicTo(-0.1 * S, -1.0 * S, 0.4 * S + sw, -1.1 * S, 0.6 * S + sw, -0.75 * S)
        c.drawPath(pl, stroke(INK, 34))
        c.drawPath(pl, stroke('#b3192a', 26))
