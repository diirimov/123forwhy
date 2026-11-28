"""Actor helpers: place characters on stage, shadows, crowds, bone assembly, emerging hands, particles."""
import math
from core import *
from core import _hash
import rig, skel, humans as Hm
from rig import solve, dance, blend, pose as mkpose, BASE
from skel import draw_death, draw_skeleton, draw_hand, DEATH_PR, bone, draw_shape, draw_skull


def shadow(c, x, y, w, a=0.45):
    c.drawPath(ellipse(x, y + 6, w, w * 0.16), fill('#05040a', a, blur=8))


def put(c, x, y, s, flip=False):
    c.translate(x, y)
    c.scale(-s if flip else s, s)


def death(c, x, y, s, t, frame, p=None, **kw):
    p = p or dance('fiddler', t)
    with Save(c):
        shadow(c, x, y, 190 * s)
        put(c, x, y, s)
        return skel.draw_death(c, t, p, frame, **kw)


def skeleton(c, x, y, s, t, frame, p=None, flip=False, pr=None, v=None, **kw):
    if v is not None and pr is None:
        pr = SKELS_PR[v % 4]
    pr = pr or BASE
    p = p or dance('macabre', t)
    with Save(c):
        shadow(c, x, y, 170 * s)
        put(c, x, y, s, flip)
        J = solve(p, pr)
        skel.draw_skeleton(c, J, pr, p, frame, **kw)
        return J


def human(c, kind, x, y, s, t, frame, p=None, expr=None, armor=None, ch=None, flip=False, sway=0.0, props_=None):
    ch = ch or Hm.CAST[kind]
    pr = ch['pr']
    p = p or dance('macabre', t, energy=0.7)
    with Save(c):
        shadow(c, x, y, 170 * s)
        put(c, x, y, s, flip)
        J = solve(p, pr)
        Hm.draw_human(c, J, pr, p, ch, frame, t, expr=expr, armor=armor, sway=sway, props_=props_)
        return J


SKELS = [dict(pr=rig.props(), eyes='pale'), dict(pr=rig.props(thigh=235, shin=225, torso=310, shw=100), eyes='pale'),
         dict(pr=rig.props(thigh=270, shin=260, torso=345, shw=114), eyes='pale'),
         dict(pr=rig.props(thigh=250, shin=240, torso=330, shw=118, hipw=62), eyes='ember')]


SKELS_PR = [d['pr'] for d in SKELS]


def crowd(c, t, frame, specs):
    """specs: list of dicts with kind,x,y,s,routine,delay,energy,amp,expr,flip ... drawn back-to-front"""
    for sp in sorted(specs, key=lambda d: d['y']):
        r_ = sp.get('routine', 'macabre')
        p = sp.get('pose') or dance(r_, t, energy=sp.get('energy', 1.0), delay=sp.get('delay', 0.0),
                                    amp=sp.get('amp', 1.0), stiff=sp.get('stiff', 0.0), beat_off=sp.get('boff', 0))
        if 'mod' in sp:
            p = sp['mod'](p)
        k = sp['kind']
        if k == 'death':
            death(c, sp['x'], sp['y'], sp['s'], t, frame, p, **sp.get('kw', {}))
        elif k == 'skel':
            v = SKELS[sp.get('v', 0) % len(SKELS)]
            skeleton(c, sp['x'], sp['y'], sp['s'], t, frame, p, flip=sp.get('flip', False), pr=v['pr'],
                     eyes=v['eyes'], **sp.get('kw', {}))
        else:
            human(c, k, sp['x'], sp['y'], sp['s'], t, frame, p, expr=sp.get('expr'), armor=sp.get('armor'),
                  ch=sp.get('ch'), flip=sp.get('flip', False), sway=sp.get('sway', 0.0))


# ------------------------------------------------------------------ emerging hand from the ground
def ground_hand(c, x, y, s, rise, t, frame, claw=0.0, seed=0):
    """forearm + hand bursting up out of ground at (x,y). rise 0..1"""
    if rise <= 0:
        return
    L = 330 * s
    with Save(c):
        c.clipRect(skia.Rect.MakeLTRB(x - 600 * s, y - 2000 * s, x + 600 * s, y + 6 * s))
        sway = math.sin(t * 5 + seed) * 0.12 * (1 - claw)
        base = (x, y + 80 * s)
        a = -math.pi / 2 + sway + (_hash(seed, 3) - 0.5) * 0.4
        wr = (base[0] + math.cos(a) * L * rise, base[1] + math.sin(a) * L * rise)
        el = (base[0], base[1])
        d = ang(el, wr)
        nx, ny = -math.sin(d) * 6 * s, math.cos(d) * 6 * s
        for (o, w1, w2) in ((1, 8, 9), (-1, 9, 7)):
            bp = capsule((el[0] + nx * o, el[1] + ny * o), (wr[0] + nx * o * 1.3, wr[1] + ny * o * 1.3), w1 * s,
                         w2 * s)
            c.drawPath(bp, stroke(INK, 8 * s))
            c.drawPath(bp, fill(BONE))
        skel.draw_hand(c, wr, a, 1, frame, curl=0.15 + 0.9 * claw, scale=1.5 * s, spread=1.4)
    # dirt lip
    c.drawPath(ellipse(x, y + 4 * s, 110 * s, 22 * s), fill('#2a1e16'))
    c.drawPath(ellipse(x, y, 95 * s, 15 * s), fill('#120c08'))


def dirt_burst(c, x, y, t, t0, s=1.0, n=26, seed=0, col='#4a3a2e'):
    dt = t - t0
    if dt < 0 or dt > 1.4:
        return
    for k in range(n):
        a = -math.pi / 2 + (_hash(k, seed) - 0.5) * 2.2
        v = (500 + 700 * _hash(k, seed + 1)) * s
        px = x + math.cos(a) * v * dt
        py = y + math.sin(a) * v * dt + 1400 * s * dt * dt
        r = (6 + 12 * _hash(k, seed + 2)) * s
        al = clamp(1 - dt / 1.4)
        c.drawPath(ellipse(px, py, r, r * 0.8), fill(col if k % 3 else '#6a5440', al))


def coins_burst(c, x, y, t, t0, s=1.0, n=40, seed=0, spread=1.0, up=1.0):
    dt = t - t0
    if dt < 0 or dt > 2.2:
        return
    for k in range(n):
        a = -math.pi / 2 + (_hash(k, seed) - 0.5) * 1.8 * spread
        v = (900 + 900 * _hash(k, seed + 1)) * s * up
        px = x + math.cos(a) * v * dt
        py = y + math.sin(a) * v * dt + 1800 * s * dt * dt
        spin = math.cos(dt * 14 + k)
        r = 20 * s
        with Save(c):
            c.translate(px, py)
            c.drawPath(ellipse(0, 0, r * abs(spin) + 3, r), fill(GOLD))
            c.drawPath(ellipse(0, 0, r * abs(spin) + 3, r), stroke('#6a4a12', 2.5))
            if abs(spin) > 0.6:
                c.drawPath(ellipse(-r * 0.3 * spin, -r * 0.3, r * 0.25, r * 0.25), fill('#fff2b0', 0.9))


def sparkle(c, x, y, t, t0, s=1.0, col='#ffe39a', n=12, seed=0):
    dt = t - t0
    if dt < 0 or dt > 0.8:
        return
    for k in range(n):
        a = k * 2 * math.pi / n + _hash(k, seed)
        d = (80 + 260 * ease_out(dt / 0.8)) * s * (0.6 + 0.4 * _hash(k, seed + 1))
        al = 1 - dt / 0.8
        px, py = x + math.cos(a) * d, y + math.sin(a) * d
        c.drawPath(poly([(px, py - 14 * s), (px + 4 * s, py), (px, py + 14 * s), (px - 4 * s, py)]), fill(col, al))


# ------------------------------------------------------------------ bone assembly
PARTS = ['legL', 'legR', 'pelvis', 'spine', 'armL', 'armR', 'skull']


def assembled_skeleton(c, x, y, s, t, frame, prog_fn, p=None, seed=0, pr=None):
    """prog_fn(part) -> 0..1 (1 = assembled). parts fly in from scattered positions on the ground."""
    pr = pr or BASE
    p = p or dance('macabre', t)
    J = solve(p, pr)
    with Save(c):
        shadow(c, x, y, 170 * s, 0.4)
        put(c, x, y, s)

        def off(part, k):
            u = prog_fn(part)
            if u >= 1:
                return None
            sx = (_hash(k, seed) - 0.5) * 900
            sy = 30 + 40 * _hash(k, seed + 1)
            e = ease_out_back(u, 1.2)
            tgt = {'legL': J['kneeL'], 'legR': J['kneeR'], 'pelvis': J['pel'], 'spine': J['chest'],
                   'armL': J['elbL'], 'armR': J['elbR'], 'skull': J['headc']}[part]
            # arc from ground position
            gx, gy = sx, sy
            px = lerp(gx, tgt[0], e)
            py = lerp(gy, tgt[1], e) - math.sin(clamp(u) * math.pi) * 260
            rot_ = (1 - e) * (_hash(k, seed + 2) - 0.5) * 6
            return (px - tgt[0], py - tgt[1], rot_, tgt)
        for k, part in enumerate(PARTS):
            o = off(part, k)
            if prog_fn(part) <= 0:
                continue
            with Save(c):
                if o:
                    c.translate(o[0], o[1])
                    c.rotate(math.degrees(o[2]), o[3][0], o[3][1])
                if part in ('legL', 'legR'):
                    skel.draw_leg(c, J, part[-1], frame)
                elif part == 'pelvis':
                    skel.draw_pelvis(c, J, pr, p, frame)
                elif part == 'spine':
                    lum = skel.spine_pts(add(J['pel'], (0, -40)), J['chest'], 5, p['twist'] * 14)
                    skel.draw_vertebrae(c, lum, 26, frame)
                    skel.draw_ribcage(c, J, pr, p, frame)
                    nk = skel.spine_pts(J['neck'], add(J['headc'], rot((0, pr['head'] * 0.38), J['hang'])), 3, 0)
                    skel.draw_vertebrae(c, nk, 20, frame)
                elif part in ('armL', 'armR'):
                    skel.draw_arm(c, J, part[-1], p, frame)
                elif part == 'skull':
                    skel.draw_skull(c, J['headc'], J['hang'], pr['head'], frame, p['jaw'], p['turn'], eyes='pale')
    return J
