"""Articulated skeleton + DEATH (hooded cloak, antique fiddle) drawing."""
import math, bisect
from core import *
from rig import solve, props

OW = 4.2  # outline width


def bone(a, b, w, ka=1.0, kb=1.0):
    """long bone with condyle knobs at both ends (union path)"""
    p = capsule(a, b, w * 0.42, w * 0.42)
    d = ang(a, b)
    nx, ny = -math.sin(d), math.cos(d)
    for (pt, k, sgn) in ((a, ka, 1), (b, kb, -1)):
        if k <= 0:
            continue
        r = w * 0.36 * k
        off = w * 0.3
        inward = (math.cos(d) * r * 0.5 * sgn, math.sin(d) * r * 0.5 * sgn)
        for s in (-1, 1):
            q = (pt[0] + nx * off * s + inward[0], pt[1] + ny * off * s + inward[1])
            p = skia.Op(p, ellipse(q[0], q[1], r, r), skia.PathOp.kUnion_PathOp) or p
    return p


def draw_shape(c, path, frame, col=BONE, ow=OW, shade=None):
    c.drawPath(path, stroke(INK, ow * 2.0))
    c.drawPath(path, fill(col))
    if shade is not None:
        c.save()
        c.clipPath(path, doAntiAlias=True)
        c.drawPath(shade, fill(BONE_SH, 0.85))
        c.restore()


def shade_side(path, dx, dy):
    q = skia.Path(path)
    q.offset(dx, dy)
    return skia.Op(path, q, skia.PathOp.kDifference_PathOp) or skia.Path()


# ------------------------------------------------------------------ skull
def skull_paths(S, turn=0.0, grin=1.0):
    t = turn
    cr = smooth_poly([(-0.36 * S, -0.08 * S), (-0.33 * S, -0.34 * S), (-0.16 * S, -0.5 * S), (0.0, -0.53 * S),
                      (0.16 * S, -0.5 * S), (0.33 * S, -0.34 * S), (0.36 * S, -0.08 * S), (0.33 * S, 0.1 * S),
                      (0.25 * S, 0.17 * S), (0.2 * S, 0.33 * S), (0.0, 0.36 * S), (-0.2 * S, 0.33 * S),
                      (-0.25 * S, 0.17 * S), (-0.33 * S, 0.1 * S)])
    jaw = smooth_poly([(-0.28 * S, 0.12 * S), (-0.26 * S, 0.34 * S), (-0.17 * S, 0.5 * S), (0, 0.55 * S),
                       (0.17 * S, 0.5 * S), (0.26 * S, 0.34 * S), (0.28 * S, 0.12 * S), (0.2 * S, 0.3 * S),
                       (0, 0.36 * S), (-0.2 * S, 0.3 * S)])
    return cr, jaw


def draw_skull(c, hc, hang, S, frame, jaw=0.0, turn=0.0, eyes='ember', grin=1.0, crack=True, glow=0.0,
               brow=0.0, hood=False):
    with Save(c):
        c.translate(*hc)
        c.rotate(math.degrees(hang))
        t = clamp(turn, -1, 1)
        fx = t * 0.1 * S
        cr, jw = skull_paths(S)
        # jaw (behind cranium edge)
        jaw_drop = jaw * 0.13 * S
        with Save(c):
            c.translate(fx * 0.8, jaw_drop)
            c.rotate(t * 4)
            c.drawPath(jw, stroke(INK, OW * 2))
            c.drawPath(jw, fill(BONE))
            c.drawPath(shade_side(jw, -0.06 * S, -0.04 * S), fill(BONE_SH, 0.9))
            # lower teeth
            for i in range(-4, 5):
                x = i * 0.03 * S + fx * 0.2
                y = 0.31 * S - abs(i) * 0.006 * S * grin - (i * i) * 0.0025 * S * grin
                r = skia.Rect.MakeXYWH(x - 0.012 * S, y - 0.045 * S, 0.026 * S, 0.05 * S)
                c.drawRoundRect(r, 3, 3, fill('#fbf5e4'))
                c.drawRoundRect(r, 3, 3, stroke(INK, 1.6))
        # mouth cavity when open
        if jaw > 0.05:
            mp = ellipse(fx * 0.5, 0.3 * S + jaw_drop * 0.45, 0.15 * S, 0.02 * S + jaw_drop * 0.45)
            c.drawPath(mp, fill('#130b0e'))
        # cranium
        c.drawPath(cr, stroke(INK, OW * 2))
        c.drawPath(cr, fill(BONE))
        with Save(c):
            c.clipPath(cr, doAntiAlias=True)
            c.drawPath(ellipse(0.17 * S - fx * 0.5, 0.05 * S, 0.36 * S, 0.62 * S), fill(BONE_SH, 0.0))
            sh = shade_side(cr, -0.07 * S, 0.05 * S)
            c.drawPath(sh, fill(BONE_SH, 0.95))
            # temple hollows
            for s in (-1, 1):
                c.drawPath(ellipse(s * 0.3 * S + fx * 0.3, -0.02 * S, 0.06 * S, 0.12 * S), fill(BONE_DK, 0.35))
            # highlight
            c.drawPath(ellipse(-0.12 * S + fx * 0.3, -0.33 * S, 0.12 * S, 0.06 * S), fill('#fffaf0', 0.55))
        if crack:
            cp = poly([(0.08 * S, -0.52 * S), (0.11 * S, -0.43 * S), (0.07 * S, -0.37 * S), (0.12 * S, -0.3 * S)],
                      False)
            c.drawPath(cp, stroke(INK, 2.2))
        # brow ridge + eye sockets (mischievous slant)
        for s in (-1, 1):
            ex = s * 0.145 * S + fx
            sc = 1 - 0.35 * max(0, t * s)  # far eye compress
            sock = smooth_poly([(ex - s * 0.085 * S * sc, -0.03 * S + brow * 0.02 * S),
                                (ex - s * 0.02 * S * sc, -0.1 * S - (0.01 if s > 0 else 0) * S + brow * 0.03 * S),
                                (ex + s * 0.075 * S * sc, -0.075 * S - brow * 0.01 * S),
                                (ex + s * 0.09 * S * sc, 0.03 * S),
                                (ex + s * 0.01 * S * sc, 0.09 * S), (ex - s * 0.07 * S * sc, 0.06 * S)])
            c.drawPath(sock, fill('#120b10'))
            c.drawPath(sock, stroke(INK, 2.5))
            # brow line above socket
            bp = P()
            bp.moveTo(ex - s * 0.1 * S * sc, -0.07 * S + brow * 0.03 * S)
            bp.quadTo(ex, -0.15 * S - brow * 0.01 * S, ex + s * 0.1 * S * sc, -0.1 * S)
            c.drawPath(bp, stroke(BONE_DK, 3.0))
            if eyes == 'ember':
                pcx, pcy = ex + 0.012 * S * s + fx * 0.25, 0.005 * S
                c.drawPath(ellipse(pcx, pcy, 0.05 * S, 0.05 * S), fill('#ffb347', 0.35 + 0.3 * glow, blur=7))
                c.drawPath(ellipse(pcx, pcy, 0.022 * S, 0.026 * S), fill('#ffd27a'))
                c.drawPath(ellipse(pcx, pcy, 0.009 * S, 0.012 * S), fill('#fff6d8'))
            elif eyes == 'pale':
                pcx, pcy = ex + fx * 0.25, 0.01 * S
                c.drawPath(ellipse(pcx, pcy, 0.016 * S, 0.016 * S), fill('#cfe6ff', 0.9))
        # nose cavity
        nz = smooth_poly([(fx * 1.1, 0.1 * S), (fx * 1.1 - 0.04 * S, 0.2 * S), (fx * 1.1, 0.215 * S),
                          (fx * 1.1 + 0.04 * S, 0.2 * S)])
        c.drawPath(nz, fill('#160d10'))
        # cheekbones
        for s in (-1, 1):
            cp = P()
            cp.moveTo(s * 0.3 * S + fx * 0.4, 0.07 * S)
            cp.quadTo(s * 0.22 * S + fx * 0.4, 0.17 * S, s * 0.1 * S + fx, 0.17 * S)
            c.drawPath(cp, stroke(BONE_DK, 2.6))
        # upper teeth: grinning arc
        for i in range(-5, 6):
            x = i * 0.028 * S + fx * 0.6
            y = 0.255 * S - (i * i) * 0.0022 * S * grin
            r = skia.Rect.MakeXYWH(x - 0.0125 * S, y, 0.025 * S, 0.055 * S)
            c.drawRoundRect(r, 3, 3, fill('#fbf5e4'))
            c.drawRoundRect(r, 3, 3, stroke(INK, 1.6))


# ------------------------------------------------------------------ hands & feet
def draw_hand(c, wr, a, s, frame, curl=0.3, scale=1.0, col=BONE, spread=1.0):
    """skeletal hand at wrist wr pointing along angle a; s = side sign"""
    L = 26 * scale
    carp = ellipse(0, 0, 1, 1)
    with Save(c):
        c.translate(*wr)
        c.rotate(math.degrees(a))
        palm = smooth_poly([(0, -11 * scale), (30 * scale, -15 * scale), (34 * scale, 13 * scale), (0, 10 * scale)])
        c.drawPath(palm, stroke(INK, OW * 1.8))
        c.drawPath(palm, fill(col))
        for i, off in enumerate((-1.5, -0.5, 0.5, 1.5)):
            base = (32 * scale, off * 8 * scale)
            da = off * 0.17 * spread
            pts = [base]
            aa = da
            seg = [L * 0.95, L * 0.7, L * 0.5] if i in (1, 2) else [L * 0.8, L * 0.6, L * 0.45]
            for k, sl in enumerate(seg):
                aa += curl * 0.75 * s * 0 + curl * 0.7
                pts.append((pts[-1][0] + math.cos(aa) * sl, pts[-1][1] + math.sin(aa) * sl))
            for k in range(3):
                bp = capsule(pts[k], pts[k + 1], 4.3 * scale, 3.4 * scale)
                c.drawPath(bp, stroke(INK, OW * 1.6))
                c.drawPath(bp, fill(col))
        # thumb
        tb = [(6 * scale, -10 * s * scale)]
        aa = -0.9 * s
        for sl in (L * 0.7, L * 0.55):
            aa += 0.35 * s * curl
            tb.append((tb[-1][0] + math.cos(aa) * sl, tb[-1][1] + math.sin(aa) * sl))
        for k in range(2):
            bp = capsule(tb[k], tb[k + 1], 4.8 * scale, 3.6 * scale)
            c.drawPath(bp, stroke(INK, OW * 1.6))
            c.drawPath(bp, fill(col))


def draw_foot(c, ank, toe, frame, scale=1.0):
    d = ang(ank, toe)
    L = dist(ank, toe)
    with Save(c):
        c.translate(*ank)
        c.rotate(math.degrees(d))
        heel = ellipse(-4 * scale, 4 * scale, 15 * scale, 13 * scale)
        draw_shape(c, heel, frame)
        for i, off in enumerate((-1, 0, 1)):
            bp = capsule((6 * scale, off * 6 * scale), (L * 0.75, off * 9 * scale), 5.5 * scale, 4.5 * scale)
            draw_shape(c, bp, frame)
            tp = capsule((L * 0.75, off * 9 * scale), (L + 8 * scale, off * 12 * scale + 3 * scale), 4.2 * scale)
            draw_shape(c, tp, frame)


# ------------------------------------------------------------------ torso parts
def draw_pelvis(c, J, pr, pose, frame):
    pel = J['pel']
    hw = pr['hipw']
    with Save(c):
        c.translate(*pel)
        c.rotate(math.degrees(pose['hip']))
        wing = smooth_poly([(-hw - 48, -58), (-hw - 10, -78), (-16, -40), (-12, 10), (-30, 52), (-hw - 10, 40),
                            (-hw - 30, 6), (-hw - 55, -22)])
        wingR = smooth_poly([(x * -1, y) for x, y in [(-hw - 48, -58), (-hw - 10, -78), (-16, -40), (-12, 10),
                                                       (-30, 52), (-hw - 10, 40), (-hw - 30, 6), (-hw - 55, -22)]])
        sac = smooth_poly([(-22, -48), (22, -48), (14, 30), (0, 46), (-14, 30)])
        pub = smooth_poly([(-48, 36), (48, 36), (30, 62), (-30, 62)])
        for pth in (pub, wing, wingR, sac):
            c.drawPath(pth, stroke(INK, OW * 2))
        for pth in (pub, wing, wingR, sac):
            c.drawPath(pth, fill(BONE))
        for s in (-1, 1):
            c.drawPath(ellipse(s * 38, 38, 12, 15), fill('#1a1014'))
            c.drawPath(ellipse(s * 38, 38, 12, 15), stroke(INK, 2))
            c.drawPath(ellipse(s * (hw + 12), -20, 16, 22), fill(BONE_SH, 0.8))
        for k in range(3):
            c.drawPath(ellipse(0, -30 + k * 20, 4, 3), fill(BONE_DK))


def spine_pts(a, b, n, bend):
    pts = []
    m = mid(a, b)
    d = ang(a, b)
    ctrl = (m[0] + math.cos(d + math.pi / 2) * bend, m[1] + math.sin(d + math.pi / 2) * bend)
    for i in range(n):
        t = (i + 0.5) / n
        x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * ctrl[0] + t * t * b[0]
        y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * ctrl[1] + t * t * b[1]
        pts.append((x, y))
    return pts


def draw_vertebrae(c, pts, w, frame):
    for i, p in enumerate(pts):
        r = skia.Rect.MakeXYWH(p[0] - w / 2, p[1] - w * 0.28, w, w * 0.56)
        c.drawRoundRect(r, w * 0.2, w * 0.2, stroke(INK, OW * 1.8))
    for i, p in enumerate(pts):
        r = skia.Rect.MakeXYWH(p[0] - w / 2, p[1] - w * 0.28, w, w * 0.56)
        c.drawRoundRect(r, w * 0.2, w * 0.2, fill(BONE))
        c.drawRect(skia.Rect.MakeXYWH(p[0] - w * 0.85, p[1] - w * 0.1, w * 1.7, w * 0.2), fill(BONE_SH))


def draw_ribcage(c, J, pr, pose, frame):
    neck, pel = J['neck'], J['pel']
    lean = pose['lean']
    tw = pose['twist']
    T = pr['torso']
    shw = pr['shw'] * pr.get('slim', 1.0)
    top = add(neck, rot((tw * 10, T * 0.08), lean))
    # sternum
    st0 = add(neck, rot((tw * 22, T * 0.1), lean))
    st1 = add(neck, rot((tw * 26, T * 0.42), lean))
    widths = [0.62, 0.8, 0.9, 0.93, 0.9, 0.82, 0.68]
    ribs = []
    for i, wi in enumerate(widths):
        y = T * (0.1 + i * 0.062)
        for s in (-1, 1):
            comp = 1 - 0.22 * tw * s
            w = shw * wi * comp
            a = add(neck, rot((tw * 24 * (1 - i * 0.05), y), lean))
            c1 = add(neck, rot((s * w * 0.75 + tw * 10, y - T * 0.04), lean))
            c2 = add(neck, rot((s * w * 1.02, y + T * 0.05), lean))
            e = add(neck, rot((s * w * 0.92, y + T * 0.15 + i * 2), lean))
            rp = P()
            rp.moveTo(*a)
            rp.cubicTo(c1[0], c1[1], c2[0], c2[1], e[0], e[1])
            ribs.append(rp)
    # inner darkness of thoracic cavity
    cav = smooth_poly([add(neck, rot((x, y), lean)) for x, y in
                       [(-shw * 0.55, T * 0.12), (shw * 0.55, T * 0.12), (shw * 0.88, T * 0.38),
                        (shw * 0.62, T * 0.62), (0, T * 0.55), (-shw * 0.62, T * 0.62), (-shw * 0.88, T * 0.38)]])
    c.drawPath(cav, fill('#1a1220', 0.55))
    for rp in ribs:
        c.drawPath(rp, stroke(INK, 17, cap=skia.Paint.kRound_Cap))
    for rp in ribs:
        c.drawPath(rp, stroke(BONE, 9.5))
    for rp in ribs:
        q = stroke(BONE_SH, 3.0)
        c.drawPath(rp, q)
    stp = capsule(st0, st1, 11, 8)
    draw_shape(c, stp, frame)
    # clavicles
    for s in ('L', 'R'):
        sh = J['sh' + s]
        cl = P()
        cl.moveTo(*st0)
        m_ = mid(st0, sh)
        cl.quadTo(m_[0], m_[1] - 14, sh[0], sh[1])
        c.drawPath(cl, stroke(INK, 18))
        c.drawPath(cl, stroke(BONE, 10))


def draw_arm(c, J, s, pose, frame, scale=1.0, hand=True, col=BONE):
    sh, el, wr = J['sh' + s], J['elb' + s], J['wr' + s]
    sg = -1 if s == 'L' else 1
    hum = bone(sh, el, 30 * scale, 1.15, 1.0)
    draw_shape(c, hum, frame, col)
    # radius + ulna
    d = ang(el, wr)
    nx, ny = -math.sin(d) * 5 * scale, math.cos(d) * 5 * scale
    r1 = capsule((el[0] + nx, el[1] + ny), (wr[0] + nx * 1.4, wr[1] + ny * 1.4), 6.5 * scale, 8 * scale)
    r2 = capsule((el[0] - nx, el[1] - ny), (wr[0] - nx * 1.1, wr[1] - ny * 1.1), 7.5 * scale, 5.5 * scale)
    c.drawPath(r1, stroke(INK, OW * 1.9))
    c.drawPath(r2, stroke(INK, OW * 1.9))
    c.drawPath(r1, fill(col))
    c.drawPath(r2, fill(col))
    c.drawPath(ellipse(el[0], el[1], 13 * scale, 13 * scale), stroke(INK, OW * 1.6))
    c.drawPath(ellipse(el[0], el[1], 13 * scale, 13 * scale), fill(col))
    if hand:
        draw_hand(c, wr, J['hand%sa' % s], sg, frame, pose.get('curl', 0.3), scale)


def draw_leg(c, J, s, frame, scale=1.0):
    hip, kn, an, ft = J['hip' + s], J['knee' + s], J['ank' + s], J['foot' + s]
    fem = bone(hip, kn, 34 * scale, 1.2, 1.15)
    draw_shape(c, fem, frame)
    d = ang(kn, an)
    nx, ny = -math.sin(d), math.cos(d)
    sg = -1 if s == 'L' else 1
    tib = bone((kn[0] - nx * 3 * sg, kn[1] - ny * 3 * sg), (an[0], an[1]), 27 * scale, 1.15, 0.8)
    fib = capsule((kn[0] + nx * 13 * sg, kn[1] + ny * 13 * sg), (an[0] + nx * 10 * sg, an[1] + ny * 10 * sg),
                  5 * scale)
    draw_shape(c, fib, frame)
    draw_shape(c, tib, frame)
    # patella
    pk = mid(kn, J['hip' + s], 0.06)
    c.drawPath(ellipse(pk[0], pk[1], 12 * scale, 14 * scale), stroke(INK, OW * 1.6))
    c.drawPath(ellipse(pk[0], pk[1], 12 * scale, 14 * scale), fill('#f7efd9'))
    draw_foot(c, an, ft, frame, scale)


def draw_skeleton(c, J, pr, pose, frame, eyes='pale', crack=False, hand=True, glow=0.0, skip_arms=False,
                  head_scale=1.0, back_arm=None, grin=1.0, brow=0.0, skull_offset=(0, 0), skull_spin=0.0):
    """full articulated skeleton, front view"""
    for s in ('L', 'R'):
        draw_leg(c, J, s, frame)
    draw_pelvis(c, J, pr, pose, frame)
    # lumbar spine
    lum = spine_pts(add(J['pel'], (0, -40)), J['chest'], 5, pose['twist'] * 14)
    draw_vertebrae(c, lum, 26, frame)
    draw_ribcage(c, J, pr, pose, frame)
    # neck
    hc = J['headc']
    nk = spine_pts(J['neck'], add(hc, rot((0, pr['head'] * 0.38), J['hang'])), 3, 0)
    draw_vertebrae(c, nk, 20, frame)
    if not skip_arms:
        for s in ('L', 'R'):
            draw_arm(c, J, s, pose, frame, hand=hand)
    draw_skull(c, add(hc, skull_offset), J['hang'] + skull_spin, pr['head'] * head_scale, frame, pose['jaw'],
               pose['turn'], eyes=eyes, crack=crack, glow=glow, grin=grin, brow=brow)


# ================================================================== DEATH
DEATH_PR = props(thigh=290, shin=280, torso=360, neck=52, head=158, shw=112, hipw=50, uarm=212, farm=196, slim=0.92)


def bow_state(t):
    """bow position along the stick (0..1) and direction, synced to the real fiddle notes"""
    starts = [n['start'] for n in FIDDLE]
    i = bisect.bisect_right(starts, t) - 1
    if i < 0:
        return 0.5, 0, 0.0
    # direction alternates; accents restart a down-bow
    pos = 0.15
    d = 1
    for k in range(max(0, i - 40), i + 1):
        n = FIDDLE[k]
        if n['acc'] >= 0.8:
            d = 1
        travel = min(0.7, 0.12 + n['dur'] * 1.25)
        if k < i:
            pos = clamp(pos + d * travel, 0.05, 0.95)
            d = -d
    n = FIDDLE[i]
    travel = min(0.7, 0.12 + n['dur'] * 1.25)
    u = clamp((t - n['start']) / max(n['dur'], 0.05))
    cur = clamp(pos + d * travel * ease_out(u, 1.6), 0.05, 0.95)
    energy = math.exp(-(t - n['start']) / 0.12) if t - n['start'] < 0.5 else 0
    return cur, d, energy


def draw_fiddle(c, center, a, frame, scale=1.0, alpha=1.0):
    """antique fiddle: body centered at center, long axis angle a (neck direction)"""
    with Save(c):
        c.translate(*center)
        c.rotate(math.degrees(a))
        s = scale
        body = smooth_poly([(-95 * s, 0), (-88 * s, -38 * s), (-58 * s, -46 * s), (-30 * s, -36 * s),
                            (-14 * s, -24 * s), (2 * s, -30 * s), (30 * s, -40 * s), (52 * s, -30 * s),
                            (60 * s, 0), (52 * s, 30 * s), (30 * s, 40 * s), (2 * s, 30 * s), (-14 * s, 24 * s),
                            (-30 * s, 36 * s), (-58 * s, 46 * s), (-88 * s, 38 * s)])
        c.drawPath(body, stroke(INK, OW * 2))
        gp = lin_grad((-90 * s, -40 * s), (60 * s, 40 * s), ['#a8521c', '#6b2c10', '#3c170a'])
        c.drawPath(body, gp)
        # varnish highlight
        c.drawPath(ellipse(-55 * s, -14 * s, 28 * s, 12 * s), fill('#f0a050', 0.35))
        c.drawPath(ellipse(25 * s, -16 * s, 18 * s, 9 * s), fill('#f0a050', 0.3))
        # purfling
        inner = skia.Path(body)
        m = skia.Matrix()
        m.setScale(0.9, 0.86)
        inner.transform(m)
        c.drawPath(inner, stroke('#2a0f05', 1.6))
        # f-holes
        for sy in (-1, 1):
            fp = P()
            fp.moveTo(-40 * s, sy * 12 * s)
            fp.cubicTo(-30 * s, sy * 22 * s, -10 * s, sy * 6 * s, 6 * s, sy * 16 * s)
            c.drawPath(fp, stroke('#120603', 3.2))
        # fingerboard & neck
        nk = poly([(-10 * s, -7 * s), (150 * s, -5 * s), (150 * s, 5 * s), (-10 * s, 7 * s)])
        c.drawPath(nk, stroke(INK, OW * 2))
        c.drawPath(nk, fill('#1e1410'))
        # scroll + pegbox
        pb = poly([(150 * s, -7 * s), (186 * s, -9 * s), (186 * s, 9 * s), (150 * s, 7 * s)])
        c.drawPath(pb, stroke(INK, OW * 2))
        c.drawPath(pb, fill('#5b2810'))
        c.drawPath(ellipse(196 * s, 0, 14 * s, 13 * s), stroke(INK, OW * 2))
        c.drawPath(ellipse(196 * s, 0, 14 * s, 13 * s), fill('#6b2c10'))
        sp = P()
        sp.addCircle(196 * s, 0, 7 * s)
        c.drawPath(sp, stroke('#2a0f05', 2))
        for k in range(2):
            for sy in (-1, 1):
                c.drawRect(skia.Rect.MakeXYWH((160 + k * 14) * s, sy * 9 * s - (3 if sy < 0 else -3) * s - 3 * s,
                                              6 * s, 9 * s * sy if sy > 0 else 9 * s), fill('#2a1208'))
        # bridge, tailpiece, strings
        c.drawRect(skia.Rect.MakeXYWH(-28 * s, -14 * s, 5 * s, 28 * s), fill('#e8d4a8'))
        tp = poly([(-92 * s, -6 * s), (-60 * s, -9 * s), (-60 * s, 9 * s), (-92 * s, 6 * s)])
        c.drawPath(tp, fill('#140c08'))
        for k in range(4):
            y = (-4.5 + k * 3) * s
            c.drawLine(-62 * s, y * 1.4, 186 * s, y * 0.8, stroke('#e6dcc0', 1.0, 0.9))


def draw_bow(c, frog, a, frame, length=330, scale=1.0):
    tip = (frog[0] + math.cos(a) * length * scale, frog[1] + math.sin(a) * length * scale)
    c.drawLine(frog[0], frog[1], tip[0], tip[1], stroke(INK, 9 * scale))
    c.drawLine(frog[0], frog[1], tip[0], tip[1], stroke('#4a2412', 5 * scale))
    # hair (slightly offset)
    d = (-math.sin(a) * 9 * scale, math.cos(a) * 9 * scale)
    c.drawLine(frog[0] + d[0], frog[1] + d[1], tip[0] + d[0] * 0.4, tip[1] + d[1] * 0.4, stroke('#f4ecd8', 2.2))
    fr = capsule(frog, (frog[0] + math.cos(a) * 24 * scale, frog[1] + math.sin(a) * 24 * scale), 7 * scale)
    c.drawPath(fr, stroke(INK, 5))
    c.drawPath(fr, fill('#1d1210'))
    return tip


def cloak_paths(J, pr, sway, flutter, t, open_=0.0, length=1.0):
    """back cloak (behind body) and front flaps; sway/flutter = secondary motion"""
    shL, shR, pel = J['shL'], J['shR'], J['pel']
    neck = J['neck']
    hemY = 0 - 20 + (1 - length) * 300
    n = 11
    back = [add(shL, (-14, -8)), add(neck, (0, -22)), add(shR, (14, -8))]
    hem = []
    spread = 1.0 + 0.9 * open_
    for i in range(n):
        u = i / (n - 1)
        x0 = lerp(shR[0] + 110 * spread, shL[0] - 110 * spread, u)
        wave = math.sin(t * 5.5 + u * 7) * 10 * flutter + fbm(t * 1.3 + u * 3, 5) * 18 * flutter
        rag = (18 if i % 2 else -6) + 10 * noise1(i * 3.1, 9)
        hem.append((x0 + sway * (0.6 + 0.6 * math.sin(u * math.pi)) + wave * 0.4, hemY + rag + wave))
    sideR = add(shR, (70 * spread + sway * 0.4, (hemY - shR[1]) * 0.5))
    sideL = add(shL, (-70 * spread + sway * 0.4, (hemY - shL[1]) * 0.5))
    pts = back + [sideR] + hem + [sideL]
    return smooth_poly(pts, True, 0.45)


def draw_death(c, t, pose, frame, fiddle=True, bowing=True, crown=0.0, open_=0.0, sway=0.0, flutter=1.0,
               glow=0.6, hand_out=0.0, skull_spin=0.0, hood=True, eye_glow=0.0, fiddle_down=0.0):
    """Death, conductor of the dance. pose = rig pose dict (modified here for fiddle playing)."""
    pr = DEATH_PR
    p = dict(pose)
    bs = None
    if fiddle and bowing:
        pos, d, en = bow_state(t)
        bs = (pos, en)
        # violin hand (screen right) holds the scroll, bow hand (screen left) drives the bow
        p['hRx'], p['hRy'] = lerp(165, p['hRx'], fiddle_down), lerp(-35, p['hRy'], fiddle_down)
        p['head'] = lerp(p['head'] * 0.5 + 0.3, p['head'], fiddle_down)
    p['elbdnL'] = 4.0
    FA = -0.42  # fiddle long axis (neck up toward screen right)
    J = solve(p, pr)
    if fiddle and bowing:
        for _ in range(2):
            fid_c = add(J['shR'], (-64, 16))
            scroll = add(fid_c, rot((168, 0), FA))
            p['hRx'] = lerp(scroll[0] - J['shR'][0], pose['hRx'], fiddle_down)
            p['hRy'] = lerp(scroll[1] - J['shR'][1], pose['hRy'], fiddle_down)
            contact = add(fid_c, rot((-26, 0), FA))
            reach = 60 + 250 * bs[0]
            frog = (contact[0] - math.cos(0.22) * reach, contact[1] + math.sin(0.22) * reach * 0.6 + 30 * (1 - bs[0]))
            p['hLx'] = lerp(frog[0] - J['shL'][0], pose['hLx'], fiddle_down)
            p['hLy'] = lerp(frog[1] - J['shL'][1], pose['hLy'], fiddle_down)
            J = solve(p, pr)
    fid_c = add(J['shR'], (-64, 16))
    fid_a = FA
    # ---- back cloak
    cl = cloak_paths(J, pr, sway, flutter, t, open_)
    c.drawPath(cl, stroke(INK, OW * 2.2))
    gp = lin_grad((0, J['neck'][1]), (0, 0), ['#2a2236', '#120e1a', '#07060b'])
    c.drawPath(cl, gp)
    if open_ > 0.05:
        # crimson lining revealed
        with Save(c):
            c.clipPath(cl, doAntiAlias=True)
            inner = cloak_paths(J, pr, sway * 0.8, flutter, t + 0.1, open_ * 0.95, 0.96)
            c.drawPath(inner, fill(BURG, min(1, open_ * 1.4)))
            c.drawPath(inner, fill('#000000', 0.25))
    # cloak folds
    for k in range(5):
        u = (k + 0.5) / 5
        x = lerp(J['shL'][0] - 60, J['shR'][0] + 60, u)
        fp = P()
        fp.moveTo(lerp(J['shL'][0], J['shR'][0], u), J['neck'][1] + 40)
        fp.quadTo(x + sway * 0.3, -300, x + sway * 0.6 + math.sin(t * 3 + k) * 8, -40)
        c.drawPath(fp, stroke('#3a3048', 3.0, 0.7))
    # ---- skeleton body
    if hand_out > 0:
        pass
    draw_skeleton(c, J, pr, p, frame, eyes='ember', crack=True, skip_arms=True, glow=eye_glow,
                  skull_spin=skull_spin, grin=1.15)
    # front cloak flaps over shoulders, framing the ribcage
    for s, sg in (('L', -1), ('R', 1)):
        sh = J['sh' + s]
        fl = smooth_poly([add(sh, (-sg * 30, -16)), add(sh, (sg * 26, -8)),
                          add(sh, (sg * (40 + 60 * open_) + sway * 0.3, 200)),
                          add(sh, (sg * (50 + 90 * open_) + sway * 0.5, 420 + 20 * math.sin(t * 4 + sg))),
                          add(sh, (sg * (10 + 70 * open_) + sway * 0.5, 460)),
                          add(sh, (-sg * (8 - 40 * open_) + sway * 0.3, 250))], True, 0.4)
        c.drawPath(fl, stroke(INK, OW * 2))
        c.drawPath(fl, lin_grad(sh, add(sh, (0, 460)), ['#2c2438', '#100c16']))
        c.drawPath(fl, stroke('#5a4a6a', 2.0, 0.5))
    # arms (+fiddle)
    if fiddle:
        draw_fiddle(c, fid_c, fid_a, frame, 1.0)
    draw_arm(c, J, 'R', dict(p, curl=1.2), frame, hand=True)
    if fiddle and bowing:
        contact = add(fid_c, rot((-26, 0), fid_a))
        draw_bow(c, J['wrL'], ang(J['wrL'], contact), frame, 360)
    draw_arm(c, J, 'L', p, frame, hand=True)
    # hood
    if hood:
        hc = J['headc']
        S = pr['head']
        with Save(c):
            c.translate(*hc)
            c.rotate(math.degrees(J['hang'] * 0.8))
            hd = smooth_poly([(-0.52 * S, 0.55 * S), (-0.55 * S, -0.1 * S), (-0.4 * S, -0.55 * S),
                              (0.05 * S, -0.75 * S), (0.42 * S, -0.58 * S), (0.56 * S, -0.1 * S),
                              (0.52 * S, 0.55 * S), (0.36 * S, 0.62 * S), (0.4 * S, -0.1 * S), (0, -0.56 * S),
                              (-0.4 * S, -0.1 * S), (-0.36 * S, 0.62 * S)], True, 0.5)
            c.drawPath(hd, stroke(INK, OW * 2))
            c.drawPath(hd, lin_grad((0, -0.7 * S), (0, 0.6 * S), ['#3a3050', '#16121e']))
            rim = P()
            rim.moveTo(-0.38 * S, 0.5 * S)
            rim.quadTo(-0.45 * S, -0.5 * S, 0, -0.58 * S)
            rim.quadTo(0.45 * S, -0.5 * S, 0.38 * S, 0.5 * S)
            c.drawPath(rim, stroke('#6c5a84', 3.0, 0.8))
    if crown > 0:
        hc = J['headc']
        draw_crown(c, add(hc, rot((0, -pr['head'] * 0.62 - (0.15 * pr['head'] if hood else 0)), J['hang'])),
                   J['hang'] + 0.18, 0.8, frame, crown)
    return J


def draw_crown(c, at, a, scale, frame, alpha=1.0):
    with Save(c):
        c.translate(*at)
        c.rotate(math.degrees(a))
        s = scale * 1.0
        cr = poly([(-70 * s, 20 * s), (-78 * s, -40 * s), (-45 * s, -8 * s), (-22 * s, -55 * s), (0, -14 * s),
                   (22 * s, -55 * s), (45 * s, -8 * s), (78 * s, -40 * s), (70 * s, 20 * s)])
        c.drawPath(cr, stroke(INK, OW * 2, alpha))
        c.drawPath(cr, lin_grad((0, -55 * s), (0, 20 * s), ['#ffe08a', GOLD, GOLD_DK]))
        c.drawRect(skia.Rect.MakeXYWH(-70 * s, 4 * s, 140 * s, 16 * s), fill(GOLD_DK))
        for x, col in ((-40, '#b3122a'), (0, '#2a5fb3'), (40, '#1f8a4c')):
            c.drawPath(ellipse(x * s, 12 * s, 8 * s, 6 * s), fill(col))
        for x in (-78, -22, 22, 78):
            c.drawPath(ellipse(x * s, (-44 if abs(x) > 50 else -58) * s, 7 * s, 7 * s), fill('#fff2c0'))
