"""DANSE MACABRE - shot list. Every shot is aligned to the analysed beat grid (bar_t)."""
import math
from core import *
from core import _hash
import env as E
from env import Cam, draw_img
import actors as A
from actors import death, skeleton, human, crowd, ground_hand, dirt_burst, coins_burst, sparkle
from rig import dance, blend, pose as mkpose, sample_routine, NEUTRAL, KEYS
import rig
import humans as Hm
import skel

B = bar_t
BEAT_ = PERIOD


def beats_since(t, t0):
    return (t - t0) / PERIOD


def kick_env(t, decay=0.12):
    """envelope that pops on every beat (kick)"""
    b = beat(t)
    ph = (b - math.floor(b)) * PERIOD
    return math.exp(-ph / decay)


def layers(c, cam, L, order):
    for name, d in order:
        img = L[name]
        if img is None:
            continue
        with Save(c):
            cam.apply(c, d)
            draw_img(c, img, 0, 0)


def shake(t, t0, amp=14, decay=0.25, seed=1):
    if t < t0:
        return (0, 0)
    e = math.exp(-(t - t0) / decay) * amp
    return (noise1((t - t0) * 40, seed) * e, noise1((t - t0) * 40, seed + 5) * e)


# ==================================================================== SCENE 01 - HOOK (0 - B3)
CEM_ORDER = [('sky', 0.12), ('far', 0.35), ('mid', 0.65), ('ground', 1.0)]


def s01_hook(c, t, f):
    L = E.cemetery_layers()
    # camera: frame 0 = low wide with huge moon; pushes in as Death rises; whip back on the drop
    rise = ease_in_out_rise(t)
    cx = 1300
    cy = lerp(1760, 1980, smooth(ramp(t, 1.3, 2.7)))
    zoom = lerp(1.0, 1.32, smoother(ramp(t, 1.0, 3.2)))
    sx, sy = shake(t, 0.0, 8, 0.35, 2)
    sx2, sy2 = shake(t, 0.78, 16, 0.22, 3)
    cam = Cam(cx + sx + sx2, cy + sy + sy2, zoom, 0.0, ref=(1300, 1800))
    layers(c, cam, L, CEM_ORDER[:3])
    with Save(c):
        cam.apply(c, 0.3)
        E.cloud(c, 700 + t * 30, 1150, 520, '#3a3a66', 0.55)
        E.cloud(c, 2100 - t * 20, 1320, 420, '#2e2e58', 0.5)
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['ground'], 0, 0)
        E.fog(c, t, 2280, 2600, 1, 0.16, '#8a90c0')
        # Death rises from the central grave
        gy = 2440
        if t >= 1.3:
            u = ease_out(ramp(t, 1.3, 2.55), 2.2)
            p = dict(NEUTRAL)
            p.update(py=lerp(900, 30, u), head=lerp(0.6, 0.0, u), lean=lerp(-0.25, 0.0, u))
            # skull snaps to camera on the 2.544 accent, then bow raised (anticipation)
            snap = ease_out_back(ramp(t, 2.544, 2.70))
            p['head'] = lerp(p['head'], -0.18, snap) + 0.1 * math.sin(t * 7) * (1 - snap)
            p['turn'] = lerp(-0.8, 0.0, snap)
            p['jaw'] = 0.25 * snap
            raise_bow = smooth(ramp(t, 2.8, 3.45))
            with Save(c):
                c.clipRect(skia.Rect.MakeLTRB(0, 0, 2600, gy + 10))
                A.put(c, 1300, gy, 0.9)
                skel.draw_death(c, t, p, f, fiddle=t > 2.6, bowing=t > 2.6, eye_glow=snap,
                                fiddle_down=1 - raise_bow if t > 2.6 else 1, sway=-40 * (1 - u), flutter=1.2)
            dirt_burst(c, 1300, gy, t, 1.3, 1.2, 40, 4)
        # the hand bursts out on the first accent
        if t < 2.2:
            hr = ease_out_back(ramp(t, 0.78, 0.98), 2.5)
            claw = smooth(ramp(t, 1.0, 1.3)) * (0.5 + 0.5 * math.sin(t * 9))
            ground_hand(c, 1330, 2452, 1.05, hr * (1 - smooth(ramp(t, 1.3, 1.6))), t, f, claw, 1)
        dirt_burst(c, 1330, 2452, t, 0.78, 1.0, 34, 1)
        # cracks glow beneath (before the burst)
        glow = 0.7 * smooth(ramp(t, 0.0, 0.7)) * (1 - ramp(t, 0.9, 1.4))
        c.drawPath(ellipse(1320, 2448, 170, 34), fill('#7ad0ff', 0.35 * glow, blur=26))
        for k in range(6):
            a = k * 1.05
            cp = P()
            cp.moveTo(1320, 2448)
            cp.lineTo(1320 + math.cos(a) * 150, 2448 + math.sin(a) * 24)
            c.drawPath(cp, stroke('#bfe8ff', 4, glow))
        # near foreground gravestones (shake with the bell)
        gs = math.sin(t * 40) * 3 * math.exp(-t / 0.5)
        r_ = rnd(3)
        E.gravestone(c, 720 + gs, 2620, 230, 420, 1, -6 + gs, r_, 0.6)
        E.gravestone(c, 1900 - gs, 2660, 260, 380, 0, 5, r_, 0.6)
    with Save(c):
        cam.apply(c, 1.25)
        E.fog(c, t * 1.4, 2650, 2600, 7, 0.22, '#a0a6cc', 1.2, 60)
    return dict(flash=0.35 * A_pulse(t, 0.78, 0.18))


def A_pulse(t, t0, d):
    return pulse(t, t0, 0.01, d)


def ease_in_out_rise(t):
    return smooth(ramp(t, 1.3, 2.6))


# ==================================================================== SCENE 02 - THE DEAD AWAKEN (B3 - B7)
def s02a_wide(c, t, f):
    """bar 3: the drop. whip-out to wide cemetery, Death fiddles, hands erupt on the beats"""
    L = E.cemetery_layers()
    lt = t - B(3)
    z = lerp(1.25, 0.78, ease_out(ramp(lt, 0, 0.45), 4))
    cy = lerp(2000, 1830, ease_out(ramp(lt, 0, 0.45), 4))
    sx, sy = shake(t, B(3), 22, 0.2, 7)
    cam = Cam(1300 + sx + 40 * math.sin(lt * 0.8), cy + sy, z, 0.0, ref=(1300, 1800))
    layers(c, cam, L, CEM_ORDER[:3])
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['ground'], 0, 0)
        E.fog(c, t, 2300, 2600, 2, 0.14)
        # hands + rising skeletons on beats 2,3,4
        for k, (hx, tb) in enumerate(((600, 1), (2000, 2), (950, 3), (1700, 3.5))):
            t0 = B(3) + tb * PERIOD
            ground_hand(c, hx, 2470, 0.7, ease_out_back(ramp(t, t0, t0 + 0.15), 2), t, f,
                        0.5 + 0.5 * math.sin(t * 8 + k), 10 + k)
            dirt_burst(c, hx, 2470, t, t0, 0.7, 20, 20 + k)
        p = dance('fiddler', t)
        death(c, 1300, 2500, 0.9, t, f, p, sway=12 * math.sin(t * 2), eye_glow=0.6)
    with Save(c):
        cam.apply(c, 1.25)
        r_ = rnd(4)
        sh = 6 * kick_env(t, 0.08)
        E.gravestone(c, 420, 2780 - sh, 260, 460, 0, -8 + sh, r_, 0.6)
        E.gravestone(c, 2250, 2800 - sh, 240, 420, 2, 7 - sh, r_, 0.6)
        E.fog(c, t * 1.3, 2700, 2600, 8, 0.2, '#a0a6cc', 1.2, 60)
    return dict(flash=0.5 * pulse(t, B(3), 0.01, 0.22))


def s02b_assemble(c, t, f):
    """bar 4: bones assemble on the percussion, a skull spins through the air onto a neck"""
    L = E.cemetery_layers()
    lt = t - B(4)
    cam = Cam(1300 - lt * 60, 1820, 1.0, 0.0, ref=(1300, 1800))
    layers(c, cam, L, CEM_ORDER)
    with Save(c):
        cam.apply(c, 1.0)
        E.fog(c, t, 2350, 2600, 3, 0.14)
        # skeleton A assembles part by part on 16th accents
        order = {'legL': 0, 'legR': 1, 'pelvis': 2, 'spine': 3, 'armL': 4, 'armR': 5, 'skull': 6}

        def prog(part, base_=B(4), step=0.75):
            t0 = base_ + order[part] * step * PERIOD * 0.5
            return ramp(t, t0 - 0.18, t0)
        A.assembled_skeleton(c, 900, 2560, 0.82, t, f, prog, dance('macabre', t, energy=ramp(t, B(4) + 1.6, B(4) + 1.75)),
                             seed=3)
        # skeleton B: headless, dancing; skull flies in, lands on the hook accent
        tl = bar_t(4, 7)
        u = ramp(t, tl - 0.75, tl)
        p = dance('shuffle', t)
        J = A.skeleton(c, 1700, 2560, 0.82, t, f, p, skull_offset=(0, -4000) if u < 1 else (0, 0),
                       skull_spin=0.0)
        if u < 1:
            # skull flight: from top-left, spinning, lands on neck
            hc = (1700 + J['headc'][0] * 0.82, 2560 + J['headc'][1] * 0.82)
            sx_, sy_ = 500, 1500
            px = lerp(sx_, hc[0], u)
            py = lerp(sy_, hc[1], u) - math.sin(u * math.pi) * 380
            with Save(c):
                c.translate(px, py)
                c.scale(0.82, 0.82)
                skel.draw_skull(c, (0, 0), u * 4 * math.pi, 150, f, 0.4, 0, eyes='pale')
        sparkle(c, 1700 + J['headc'][0] * 0.82, 2560 + J['headc'][1] * 0.82, t, tl, 1.0, '#e8f0ff')
    with Save(c):
        cam.apply(c, 1.3)
        E.fog(c, t * 1.3, 2750, 2600, 9, 0.18, '#a0a6cc', 1.2, 60)
    return {}


def s02c_feet(c, t, f):
    """bar 5: close-up of dancing feet on the grass"""
    L = E.cemetery_layers()
    lt = t - B(5)
    cam = Cam(1300 + lt * 90, 2470, 2.3, 0.0, ref=(1300, 1800))
    layers(c, cam, L, [('far', 0.35), ('mid', 0.65), ('ground', 1.0)])
    with Save(c):
        cam.apply(c, 1.0)
        specs = [dict(kind='skel', x=1050 + k * 260, y=2700, s=0.95, routine='macabre', delay=0.0, v=k) for k in range(4)]
        crowd(c, t, f, specs)
    with Save(c):
        cam.apply(c, 1.4)
        E.fog(c, t * 1.5, 2600, 2600, 11, 0.25, '#a0a6cc', 1.0, 90)
    return {}


def procession_specs(t, n=7, x0=1000, y0=2480, sp=230, rows=2, kinds=None, s=0.62, routine='macabre', delays=True):
    specs = []
    for r in range(rows):
        for k in range(n):
            x = x0 + k * sp + (r % 2) * sp * 0.5
            y = y0 + r * 130
            kind = 'skel' if not kinds else kinds[(k + r * 3) % len(kinds)]
            specs.append(dict(kind=kind, x=x, y=y, s=s * (1 + r * 0.08), routine=routine,
                              delay=(0.04 * ((k + r) % 3) if delays else 0), v=k + r, flip=(k % 2 == 1)))
    return specs


def s02d_procession(c, t, f):
    """bar 6: wide tracking shot - Death leads the growing crowd toward the town"""
    L = E.cemetery_layers()
    lt = t - B(6)
    cam = Cam(1150 + lt * 140, 2080, 0.78, 0.0, ref=(1300, 1800))
    layers(c, cam, L, CEM_ORDER)
    with Save(c):
        cam.apply(c, 1.0)
        E.fog(c, t, 2400, 2600, 4, 0.14)
        specs = procession_specs(t, 6, 650 + lt * 80, 2460, 250, 2)
        specs.append(dict(kind='death', x=1900 + lt * 80, y=2560, s=0.72, routine='fiddler'))
        crowd(c, t, f, specs)
    with Save(c):
        cam.apply(c, 1.3)
        E.fog(c, t * 1.3, 2800, 2600, 12, 0.2, '#a0a6cc', 1.2, 70)
    return {}


# ==================================================================== SCENE 03 - THE KING (B7 - B11)
THR_ORDER = [('room', 1.0)]


def king_pose_sit(t, fear=0.0):
    p = dict(NEUTRAL)
    p.update(py=225, fLx=-120, fRx=120, hLx=-150, hLy=150, hRx=110, hRy=60 - 40 * fear, lean=-0.05 * fear,
             head=0.04 * math.sin(t * 2), jaw=0)
    return p


def throne_bg(c, cam, t):
    L = E.throne_layers()
    with Save(c):
        cam.apply(c, 0.85)
        draw_img(c, L['room'], 0, 0)
        for k, (x, y) in enumerate(((300, 1500), (2100, 1500), (900, 1350), (1500, 1350))):
            E.candle(c, x, y, t, 1.2, k)
        E.dust(c, t, 0, 400, 2400, 2000, 50, 3, '#ffd9a0', 0.4)
    return L


def s03a_throne(c, t, f):
    lt = t - B(7)
    cam = Cam(1200, 1650 + lt * 20, 1.05 + lt * 0.03, ref=(1200, 1700))
    L = throne_bg(c, cam, t)
    appear = bar_t(7, 4)
    with Save(c):
        cam.apply(c, 1.0)
        # Death appears behind the throne in a puff of shadow on beat 2
        if t > appear - 0.05:
            u = ease_out_back(ramp(t, appear, appear + 0.3))
            p = dance('fiddler', t)
            p['head'] = 0.35 * math.sin(t * 3)
            with Save(c):
                c.clipRect(skia.Rect.MakeLTRB(0, 0, 2400, 1400 + 300 * u))
                death(c, 1200, 1900 + (1 - u) * 600, 0.8, t, f, p, fiddle=False, bowing=False, eye_glow=1.0)
            c.drawPath(ellipse(1200, 1300, 380 * (1 - ramp(t, appear, appear + 0.8)) + 1, 200), fill('#1a1428', 0.6 * (1 - ramp(t, appear, appear + 0.8)), blur=40))
        draw_img(c, L['throne'], 0, 0)
        fear = smooth(ramp(t, bar_t(7, 8), bar_t(7, 9)))
        p = king_pose_sit(t, fear)
        p['hRy'] = 60 - 120 * (1 - fear)  # goblet raised smugly
        ch = dict(Hm.CAST['king'], crown=1)
        J = human(c, 'king', 1200, 2000, 0.72, t, f, p, expr=dict(fear=fear, joy=0.6 * (1 - fear), look=0.6 * fear),
                  ch=ch)
        # goblet
        wr = (1200 + J['wrR'][0] * 0.72, 2000 + J['wrR'][1] * 0.72)
        if fear < 0.5:
            c.drawPath(poly([(wr[0] - 24, wr[1] - 60), (wr[0] + 24, wr[1] - 60), (wr[0] + 8, wr[1] - 20),
                             (wr[0] - 8, wr[1] - 20)]), fill(GOLD))
    return {}


def chest(c, x, y, s, open_=0.0, glow=1.0, f=0, shake_=0.0):
    with Save(c):
        c.translate(x + shake_, y)
        c.scale(s, s)
        body = skia.Rect.MakeXYWH(-160, -150, 320, 150)
        c.drawRect(body, stroke(INK, 10))
        c.drawRect(body, lin_grad((0, -150), (0, 0), ['#7a4a22', '#4a2a12']))
        for x_ in (-120, 0, 120):
            c.drawRect(skia.Rect.MakeXYWH(x_ - 12, -150, 24, 150), fill('#c9a04a'))
        c.drawRect(skia.Rect.MakeXYWH(-24, -110, 48, 50), fill('#2c2c34'))
        if open_ > 0:
            c.drawPath(ellipse(0, -160, 170, 60), fill('#ffd76a', 0.5 * glow * open_, blur=40))
            for k in range(30):
                c.drawPath(ellipse(-130 + (k % 10) * 28, -150 - (k // 10) * 12, 16, 9), fill(GOLD))
        with Save(c):
            c.rotate(-100 * open_, -160, -150)
            lid = skia.Path()
            lid.moveTo(-160, -150)
            lid.quadTo(0, -240, 160, -150)
            lid.close()
            c.drawPath(lid, stroke(INK, 10))
            c.drawPath(lid, fill('#6a3a1a'))
            c.drawLine(-160, -150, 160, -150, stroke('#c9a04a', 10))


def s03b_offer(c, t, f):
    """bar 8: the king offers treasure; Death wags a bony finger: no."""
    lt = t - B(8)
    cam = Cam(1200 - 60 * smooth(ramp(lt, 0, 1.6)), 1700, 1.25, ref=(1200, 1700))
    L = throne_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['throne'], 0, 0)
        # Death stands right, finger wag on beats (head shake)
        p = mkpose(fLx=-110, fRx=110, py=40, hLx=-130, hLy=300, hRx=60, hRy=-120, curl=0.9)
        b = beat(t)
        wag = math.sin(b * math.pi * 2) * 0.5
        p['hRx'] = 60 + 70 * wag
        p['head'] = 0.25 * wag
        p['jaw'] = 0.2 + 0.2 * abs(wag)
        p['lean'] = 0.05 * wag
        death(c, 1560, 2160, 0.78, t, f, p, fiddle=False, bowing=False, eye_glow=0.8)
        # king kneels offering the open chest
        pk = dict(NEUTRAL)
        pk.update(py=220, fLx=-140, fRx=140, hLx=60, hLy=90, hRx=-60, hRy=90, lean=0.12, head=0.1)
        human(c, 'king', 880, 2240, 0.72, t, f, pk, expr=dict(fear=0.9, look=0.8, mouth=0.4),
              ch=dict(Hm.CAST['king'], crown=1))
        chest(c, 1080, 2210, 0.7, smooth(ramp(t, B(8), B(8) + 0.25)), 1.0, f)
        sparkle(c, 1080, 2080, t, B(8) + 0.1, 0.8)
    return {}


def s03c_crown(c, t, f):
    """bar 9 (call & response): the crown flies up, Death catches it and crowns himself"""
    lt = t - B(9)
    cam = Cam(1200, 1650 - 120 * smooth(ramp(lt, 0, 0.8)) + 120 * smooth(ramp(lt, 0.9, 1.6)), 1.1, ref=(1200, 1700))
    L = throne_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['throne'], 0, 0)
        t_fly, t_catch, t_place = B(9), bar_t(9, 8), bar_t(9, 12)
        # king (no crown) left, terrified hands on head
        pk = mkpose(fLx=-120, fRx=120, py=60, hLx=80, hLy=-150, hRx=-80, hRy=-150, head=0.1 * math.sin(t * 9))
        human(c, 'king', 930, 2250, 0.7, t, f, pk, expr=dict(fear=1.0, look=0.5 + 0.5 * math.sin(t), mouth=0.8))
        # Death plays the response phrase
        placed = smooth(ramp(t, t_place - 0.1, t_place + 0.1))
        p = dance('fiddler', t)
        if t < t_place:
            catch = smooth(ramp(t, t_catch - 0.2, t_catch))
            p['hRx'], p['hRy'] = lerp(120, 60, catch), lerp(-80, -360, catch)
        J = death(c, 1560, 2250, 0.78, t, f, p, fiddle=True, bowing=t > t_place, crown=placed, eye_glow=0.8)
        if placed < 1:
            # crown arc
            u = ramp(t, t_fly, t_catch)
            st = (930, 2250 - 980 * 0.7)
            en = (1560 + J['wrR'][0] * 0.78, 2250 + J['wrR'][1] * 0.78)
            if t > t_catch:
                en2 = (1560 + J['headc'][0] * 0.78, 2250 + (J['headc'][1] - 140) * 0.78)
                v = smooth(ramp(t, t_catch, t_place))
                pos = mid(en, en2, v)
                spin = 0
            else:
                pos = (lerp(st[0], en[0], u), lerp(st[1], en[1], u) - math.sin(u * math.pi) * 620)
                spin = u * 4 * math.pi
            skel.draw_crown(c, pos, spin, 0.75, f)
            sparkle(c, pos[0], pos[1], t, t_catch, 0.8)
        if t > t_place:
            sparkle(c, 1560 + J['headc'][0] * 0.78, 2250 + (J['headc'][1] - 160) * 0.78, t, t_place, 1.0)
    return {}


def s03d_king_dance(c, t, f):
    lt = t - B(10)
    cam = Cam(1200 + 60 * math.sin(lt * 1.5), 1750, 0.95, ref=(1200, 1700))
    L = throne_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['throne'], 0, 0)
        pk = dance('shuffle', t, energy=0.75, stiff=0.3)
        human(c, 'king', 900, 2350, 0.7, t, f, pk, expr=dict(fear=0.6, joy=0.2, trance=0.3, mouth=0.2))
        death(c, 1500, 2320, 0.75, t, f, dance('fiddler', t), crown=1.0, eye_glow=0.7)
    return {}


# ==================================================================== SCENE 04 - THE KNIGHT (B11 - B15)
def court_bg(c, cam, t, bunting=False):
    L = E.courtyard_layers()
    with Save(c):
        cam.apply(c, 0.8)
        draw_img(c, L['main'], 0, 0)
        for k, x in enumerate((700, 1900)):
            E.torch(c, x, 1500, t, 1.2, k)
        if bunting:
            for k in range(2):
                y = 1200 + k * 160
                for j in range(16):
                    bx = 200 + j * 140
                    by = y + math.sin(j / 15 * math.pi) * 180
                    sw = math.sin(t * 4 + j) * 6
                    c.drawPath(poly([(bx - 40, by), (bx + 40, by), (bx + sw, by + 90)]), fill([BURG, GOLD, '#2e4a7a'][j % 3]))
        E.fog(c, t, 2200, 2600, 5, 0.1)
    return L


def knight_armor(t):
    """pieces fall away one by one on the drop-2 percussion hits"""
    hits = {'helm': B(13), 'paulL': bar_t(13, 3), 'paulR': bar_t(13, 4), 'breast': bar_t(13, 6),
            'vambL': bar_t(13, 8), 'vambR': bar_t(13, 11), 'fauld': bar_t(13, 12), 'cuisseL': bar_t(13, 14),
            'cuisseR': bar_t(13, 15), 'greaveL': bar_t(14, 0), 'greaveR': bar_t(14, 3)}
    arm = {}
    for k, (piece, th) in enumerate(hits.items()):
        dt = t - th
        if dt < 0:
            arm[piece] = (0, 0, 0, 1)
        else:
            dirx = (-1 if ('L' in piece[-1:]) else 1) * (300 + 200 * _hash(k, 4))
            if piece in ('helm', 'breast', 'fauld'):
                dirx = (1 if k % 2 else -1) * 260
            arm[piece] = (dirx * dt, -900 * dt + 2400 * dt * dt, dt * 7 * (1 if k % 2 else -1), clamp(1 - dt / 0.9))
    return arm, hits


def s04a_challenge(c, t, f):
    lt = t - B(11)
    cam = Cam(1300, 1900, 0.9 + 0.02 * lt, ref=(1300, 1950))
    court_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        # swings on the fiddle calls (steps 0 and 4), dodges by Death
        swings = [B(11), bar_t(11, 4), B(12), bar_t(12, 4)]
        k = max([i for i, s in enumerate(swings) if t >= s - 0.15] + [-1])
        pk = mkpose(fLx=-150, fRx=150, py=60, hLx=-60, hLy=150, hRx=120, hRy=-260, lean=0.0, head=0.05)
        if k >= 0:
            s0 = swings[k]
            u = clamp((t - (s0 - 0.15)) / 0.3)
            # anticipation (raise) then slash down-across
            pk['hRx'] = lerp(140, -160, ease_out(u, 3)) if k % 2 == 0 else lerp(-160, 160, ease_out(u, 3))
            pk['hRy'] = lerp(-280, 120, ease_out(u, 3))
            pk['lean'] = lerp(0.1, -0.15, u) * (1 if k % 2 == 0 else -1)
        J = human(c, 'knight', 1030, 2500, 0.74, t, f, pk, armor={})
        # sword in right hand
        wr = (1030 + J['wrR'][0] * 0.74, 2500 + J['wrR'][1] * 0.74)
        sa = J['handRa'] - 0.3
        tip = (wr[0] + math.cos(sa - 1.3) * 420, wr[1] + math.sin(sa - 1.3) * 420)
        c.drawLine(wr[0], wr[1], tip[0], tip[1], stroke(INK, 22))
        c.drawLine(wr[0], wr[1], tip[0], tip[1], stroke('#dfe6ee', 14))
        c.drawLine(wr[0] - 40 * math.cos(sa - 1.3 + 1.57), wr[1] - 40 * math.sin(sa - 1.3 + 1.57),
                   wr[0] + 40 * math.cos(sa - 1.3 + 1.57), wr[1] + 40 * math.sin(sa - 1.3 + 1.57), stroke(GOLD_DK, 14))
        # Death dodges: limbo lean / side-slip in rhythm
        p = dance('fiddler', t)
        dodge = 0
        for i, s0 in enumerate(swings):
            dodge += (1 if i % 2 == 0 else -1) * pulse(t, s0, 0.08, 0.3)
        p['lean'] = 0.5 * dodge
        p['px'] = 140 * dodge
        p['py'] += 80 * abs(dodge)
        skull_pop = pulse(t, bar_t(12, 4), 0.05, 0.25)
        death(c, 1580, 2480, 0.74, t, f, p, eye_glow=0.6, sway=-60 * dodge)
        if skull_pop > 0.05:
            pass
    return {}


def s04c_armor(c, t, f):
    """drop 2: armor flies off on every hit, rigid knight becomes fluid"""
    lt = t - B(13)
    sx, sy = shake(t, B(13), 20, 0.2, 9)
    cam = Cam(1300 + sx, 1900 + sy, 1.05 - 0.05 * lt, ref=(1300, 1950))
    court_bg(c, cam, t)
    arm, hits = knight_armor(t)
    with Save(c):
        cam.apply(c, 1.0)
        fluid = smooth(ramp(t, B(13), B(14) + 0.4))
        p = dance('macabre', t, energy=lerp(0.5, 1.0, fluid), stiff=1 - fluid, amp=lerp(0.6, 1.0, fluid))
        human(c, 'knight', 1050, 2550, 0.8, t, f, p, armor=arm, expr=dict(fear=0.6 * (1 - fluid), joy=0.6 * fluid,
                                                                             trance=0.2))
        for k, (piece, th) in enumerate(hits.items()):
            sparkle(c, 1050, 2100, t, th, 0.6, '#e8eef4', 6, k)
        death(c, 1750, 2500, 0.72, t, f, dance('fiddler', t), eye_glow=0.6)
    return dict(flash=0.45 * pulse(t, B(13), 0.01, 0.2))


def s04d_hand(c, t, f):
    """Death offers his hand; the knight takes it, they dance"""
    lt = t - B(14)
    cam = Cam(1300 + 40 * lt, 1950, 0.92, ref=(1300, 1950))
    court_bg(c, cam, t)
    arm, _ = knight_armor(t)
    with Save(c):
        cam.apply(c, 1.0)
        take = smooth(ramp(t, B(14), bar_t(14, 4)))
        pk = dance('macabre', t)
        pd = dance('fiddler', t)
        if take < 1:
            pd['hRx'], pd['hRy'] = lerp(pd['hRx'], -230, 1 - take * 0.3), lerp(pd['hRy'], 40, 1)
        human(c, 'knight', 1000, 2550, 0.8, t, f, pk, armor=arm, expr=dict(joy=0.7, trance=0.4, mouth=0.3))
        death(c, 1650, 2520, 0.75, t, f, pd, fiddle=take >= 1, bowing=take >= 1, eye_glow=0.6)
    return {}


# ==================================================================== SCENE 05 - THE MERCHANT (B15 - B19)
def treasure_bg(c, cam, t):
    L = E.treasure_layers()
    with Save(c):
        cam.apply(c, 0.85)
        draw_img(c, L['main'], 0, 0)
        E.candle(c, 1250, 1720, t, 1.3, 2)
        # moonbeam
        c.drawPath(poly([(1500, 500), (1800, 500), (1500, 2700), (900, 2700)]), fill('#bcd0ff', 0.06, blur=30))
        E.dust(c, t, 900, 500, 900, 2000, 40, 5, '#dfe8ff', 0.5)
    return L


def s05a_lock(c, t, f):
    lt = t - B(15)
    cam = Cam(1000, 1850, 1.0, ref=(1050, 1950))
    treasure_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        # door slam (bolt) on the downbeat
        slam = pulse(t, B(15), 0.01, 0.15)
        c.drawRect(skia.Rect.MakeXYWH(560, 1600 + 8 * slam, 120, 34), fill('#3a3a44'))
        c.drawRect(skia.Rect.MakeXYWH(560, 1600, 120, 34), stroke(INK, 4))
        b = beat(t) - beat(B(15))
        look = 0.0
        if b > 1:
            look = -1 if b < 2 else (1 if b < 3 else 0)
        p = mkpose(fLx=-110, fRx=110, py=50, hLx=-140 if b < 1 else 20, hLy=60 if b < 1 else 200,
                   hRx=-200 if b < 1 else -20, hRy=40 if b < 1 else 200, head=0.15 * look, turn=0.6 * look,
                   lean=-0.1 if b < 1 else 0.0)
        if b >= 3:
            p.update(hLx=60, hLy=230, hRx=-60, hRy=230, py=90, head=0.1 * math.sin(t * 10))
        human(c, 'merchant', 980, 2450, 0.8, t, f, p, expr=dict(fear=0.6, look=look, mouth=0.1))
        if b >= 3:
            chest(c, 980, 2300, 0.55, 0, 1, f)
    return dict(shake=slam)


def s05b_knock(c, t, f):
    lt = t - B(16)
    cam = Cam(1000, 2000, 1.45 + 0.06 * lt, ref=(1050, 1950))
    treasure_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        knocks = [bar_t(16, 4), bar_t(16, 8), bar_t(16, 13), bar_t(16, 15)]
        jolt = sum(pulse(t, k, 0.01, 0.12) for k in knocks)
        p = mkpose(fLx=-110, fRx=110, py=90 + 20 * jolt, hLx=60, hLy=230, hRx=-60, hRy=230,
                   head=0.12 * math.sin(t * 13) + 0.2 * jolt)
        human(c, 'merchant', 1000, 2450, 0.8, t, f, p, expr=dict(fear=0.5 + 0.5 * clamp(jolt), look=math.sin(t * 2),
                                                                  mouth=0.5 * jolt))
        chest(c, 1000, 2300 - 40 * jolt, 0.55, 0.15 * jolt, 1, f, 12 * jolt * math.sin(t * 60))
        # sweat drops
        for k in range(3):
            ph = (t * 1.6 + k * 0.33) % 1
            c.drawPath(ellipse(1100 + k * 30, 1680 + ph * 120, 7, 11), fill('#bfe0ff', 1 - ph))
    return {}


def s05c_burst(c, t, f):
    """hook returns: chest explodes open, a skeleton dances out, coins fountain on the beats"""
    lt = t - B(17)
    sx, sy = shake(t, B(17), 18, 0.2, 13)
    cam = Cam(1050 + sx, 1900 + sy, 1.0 - 0.05 * lt, ref=(1050, 1950))
    treasure_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        for k in range(4):
            coins_burst(c, 1150, 2250, t, B(17) + k * PERIOD, 0.9, 26, 30 + k, 1.0 + 0.3 * k)
        # skeleton rising from the chest
        u = ease_out_back(ramp(t, B(17), B(17) + 0.3))
        with Save(c):
            c.clipRect(skia.Rect.MakeLTRB(0, 0, 2400, 2260))
            A.skeleton(c, 1150, 2650 - 420 * u, 0.62, t, f, dance('macabre', t), eyes='ember')
        chest(c, 1150, 2330, 0.8, 1.0, 1.4, f)
        # merchant falls back in shock
        p = mkpose(fLx=-160, fRx=120, fRl=60, py=120, lean=-0.35, hLx=-180, hLy=-150, hRx=180, hRy=-180, head=-0.3,
                   jaw=0)
        human(c, 'merchant', 600, 2550, 0.8, t, f, p, expr=dict(fear=1.0, mouth=1.0))
    return dict(flash=0.4 * pulse(t, B(17), 0.01, 0.2))


def s05d_pulled(c, t, f):
    lt = t - B(18)
    cam = Cam(1100 - 90 * lt, 1950, 0.95, ref=(1050, 1950))
    treasure_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        coins_burst(c, 1300, 2200, t, B(18), 0.8, 20, 41, 1.4)
        pull = smooth(ramp(t, bar_t(18, 8), bar_t(18, 12)))
        pm = blend(mkpose(fLx=-110, fRx=110, py=60, hLx=-60, hLy=200, hRx=150, hRy=60), dance('shuffle', t, 0.85), pull)
        pm['hRx'], pm['hRy'] = 160, 0
        human(c, 'merchant', 1050 - 200 * pull, 2500, 0.8, t, f, pm, expr=dict(fear=0.6 * (1 - pull), joy=0.6 * pull,
                                                                               trance=0.4 * pull, mouth=0.3))
        A.skeleton(c, 1450 - 200 * pull, 2480, 0.7, t, f, dance('macabre', t), eyes='ember')
        death(c, 1850, 2520, 0.72, t, f, dance('fiddler', t), eye_glow=0.7)
    return {}


# ==================================================================== SCENE 06 - EVERYONE IS EQUAL (B19 - B23)
ARMS_UP = dict(hLx=-170, hLy=-230, hRx=170, hRy=-230)


def join_pose(t, t_join, base_pose, energy=1.0):
    """match-cut pose: everyone throws both arms up at the moment of joining, then dances"""
    u = ramp(t, t_join - 0.12, t_join)
    up = dict(base_pose)
    up.update(ARMS_UP)
    up['jaw'] = 0.6
    d = dance('macabre', t, energy=energy)
    if t < t_join - 0.12:
        return base_pose
    if t < t_join + PERIOD:
        return blend(base_pose, up, ease_out_back(u))
    return blend(up, d, smooth(ramp(t, t_join + PERIOD, t_join + 1.6 * PERIOD)))


def s06a_bishop(c, t, f):
    L = E.cathedral_interior_layers()
    lt = t - B(19)
    cam = Cam(1200, 1750 + 30 * lt, 1.0 + 0.03 * lt, ref=(1200, 1750))
    with Save(c):
        cam.apply(c, 0.85)
        draw_img(c, L['main'], 0, 0)
        for k, x in enumerate((990, 1410, 1000, 1400)):
            E.candle(c, x, 1780 if k < 2 else 1500, t, 1.1, k + 10)
        E.dust(c, t, 700, 500, 1000, 2000, 60, 8, '#ffe6b0', 0.5)
    with Save(c):
        cam.apply(c, 1.0)
        tj = bar_t(19, 8)
        base_ = mkpose(fLx=-90, fRx=90, py=30, hLx=60, hLy=120, hRx=-60, hRy=120, head=-0.15)
        p = join_pose(t, tj, base_)
        ch = Hm.CAST['bishop']
        human(c, 'bishop', 1080, 2450, 0.75, t, f, p, expr=dict(fear=0.3 if t < tj else 0.5, trance=0.5 if t > tj else 0.8,
                                                                 joy=0.3 if t > tj else 0, mouth=0.3 if t > tj else 0))
        # Death appears in the pews on the Neapolitan chord
        u = ease_out_back(ramp(t, B(19), B(19) + 0.25))
        if u > 0:
            death(c, 1560, 2380 + (1 - u) * 200, 0.62, t, f, dance('fiddler', t), eye_glow=0.8)
    return dict(flash=0.3 * pulse(t, B(19), 0.01, 0.2))


def s06b_peasant(c, t, f):
    L = E.field_layers()
    lt = t - B(20)
    cam = Cam(1300 - 40 * lt, 1950, 1.0, ref=(1300, 1950))
    with Save(c):
        cam.apply(c, 0.6)
        draw_img(c, L['main'], 0, 0)
        # windmill sails turning
        mc = L['mill_center']
        with Save(c):
            c.translate(*mc)
            c.rotate(t * 20)
            for k in range(4):
                c.rotate(90)
                c.drawRect(skia.Rect.MakeXYWH(-12, 0, 24, 230), fill('#16142a'))
                c.drawRect(skia.Rect.MakeXYWH(-40, 60, 60, 170), fill('#16142a'))
        E.fog(c, t, 2000, 2600, 6, 0.15)
    with Save(c):
        cam.apply(c, 1.0)
        tj = bar_t(20, 8)
        hoe = 0.5 + 0.5 * math.sin(beat(t) * math.pi)
        base_ = mkpose(fLx=-120, fRx=120, py=60, hLx=80, hLy=-40 + 120 * hoe, hRx=-40, hRy=-20 + 140 * hoe,
                       lean=0.1 * hoe, head=0.1)
        p = join_pose(t, tj, base_)
        J = human(c, 'peasant', 1100, 2450, 0.8, t, f, p, expr=dict(fear=0.2, trance=0.6 if t > tj else 0.2,
                                                                     joy=0.4 if t > tj else 0, mouth=0.3 if t > tj else 0))
        if t < tj:
            wr = (1100 + J['wrL'][0] * 0.8, 2450 + J['wrL'][1] * 0.8)
            c.drawLine(wr[0], wr[1] - 200, wr[0] + 40, wr[1] + 260, stroke('#5a3a1e', 14))
            c.drawPath(poly([(wr[0] + 20, wr[1] + 250), (wr[0] + 110, wr[1] + 270), (wr[0] + 30, wr[1] + 300)]),
                       fill('#8a8a96'))
        # Death pops up from the haystack
        u = ease_out_back(ramp(t, bar_t(20, 4), bar_t(20, 4) + 0.25))
        if u > 0:
            with Save(c):
                c.clipRect(skia.Rect.MakeLTRB(0, 0, 2600, 2380))
                death(c, 1580, 2700 - 330 * u, 0.66, t, f, dance('fiddler', t), eye_glow=0.8)
            hk = smooth_poly([(1330, 2400), (1390, 2230), (1580, 2120), (1770, 2230), (1830, 2400)], True, 0.5)
            c.drawPath(hk, fill('#c9a24a'))
            c.drawPath(hk, stroke(INK, 5))
    return {}


def s06c_jester(c, t, f):
    lt = t - B(21)
    cam = Cam(1300 + 40 * lt, 1900, 1.0, ref=(1300, 1950))
    court_bg(c, cam, t, bunting=True)
    with Save(c):
        cam.apply(c, 1.0)
        tj = bar_t(21, 8)
        # juggling: balls (skulls!) arc between hands
        base_ = mkpose(fLx=-110, fRx=110, py=40, hLx=-90, hLy=120 + 40 * math.sin(t * 12), hRx=90,
                       hRy=120 + 40 * math.sin(t * 12 + 3), head=-0.25)
        p = join_pose(t, tj, base_)
        J = human(c, 'jester', 1120, 2480, 0.78, t, f, p, expr=dict(joy=0.8, mouth=0.4, trance=0.2),
                  sway=20 * math.sin(t * 5))
        if t < tj + 0.1:
            for k in range(3):
                ph = (t * 1.8 + k / 3) % 1
                x = lerp(1120 - 120, 1120 + 120, ph if k % 2 else 1 - ph)
                y = 2000 - math.sin(ph * math.pi) * 380
                with Save(c):
                    c.translate(x, y)
                    c.scale(0.35, 0.35)
                    skel.draw_skull(c, (0, 0), ph * 6, 150, f, 0, 0, eyes='pale')
        u = ease_out_back(ramp(t, bar_t(21, 4), bar_t(21, 4) + 0.25))
        if u > 0:
            death(c, 1600 + (1 - u) * 600, 2460, 0.66, t, f, dance('fiddler', t), eye_glow=0.8)
        # growing procession behind
        crowd(c, t, f, [dict(kind='skel', x=300 + k * 160, y=2300, s=0.45, routine='macabre', v=k, delay=0.03 * k)
                        for k in range(4)])
    return {}


def s06d_noble(c, t, f):
    L = E.street_layers(0)
    lt = t - B(22)
    cam = Cam(1300 + 70 * lt, 1700, 0.9, ref=(1300, 1950))
    with Save(c):
        cam.apply(c, 0.3)
        draw_img(c, L['sky'], 0, 0)
    with Save(c):
        cam.apply(c, 0.8)
        draw_img(c, L['main'], 0, 0)
        E.fog(c, t, 2200, 2600, 3, 0.1)
    with Save(c):
        cam.apply(c, 1.0)
        tj = bar_t(22, 8)
        # proud walk (strut in place), then joins
        b = beat(t)
        stepL = (b % 2) < 1
        base_ = mkpose(fLx=-100 + (40 if stepL else -10), fRx=100 + (10 if stepL else -40), fLl=20 if not stepL else 0,
                       fRl=20 if stepL else 0, py=20, hLx=40, hLy=250, hRx=-40, hRy=250, head=-0.18, lean=-0.06)
        p = join_pose(t, tj, base_)
        # procession dancing in the background
        crowd(c, t, f, [dict(kind=k_, x=500 + i * 300, y=2250, s=0.42, routine='shuffle', v=i, delay=0.02 * i,
                             expr=dict(trance=0.5, joy=0.3))
                        for i, k_ in enumerate(['skel', 'king', 'skel', 'merchant', 'skel', 'bishop', 'skel'])])
        human(c, 'noble', 1180 + 70 * lt, 2550, 0.8, t, f, p, expr=dict(joy=0.3 if t < tj else 0.5,
                                                                          trance=0.2 if t < tj else 0.5, mouth=0.2))
        u = ease_out_back(ramp(t, bar_t(22, 4), bar_t(22, 4) + 0.25))
        if u > 0:
            death(c, 1720 + 70 * lt, 2530, 0.7, t, f, dance('fiddler', t), eye_glow=0.8)
    return {}


# ==================================================================== SCENE 07 - THE GRAND DROP (B23 - B27)
def fountain(c, x, y, t, s=1.0):
    with Save(c):
        c.translate(x, y)
        c.scale(s, s)
        c.drawPath(ellipse(0, 0, 420, 110), fill('#5a5466'))
        c.drawPath(ellipse(0, 0, 420, 110), stroke(INK, 8))
        c.drawPath(ellipse(0, -20, 380, 90), fill('#2a4a6a'))
        for k in range(10):
            ph = (t * 0.7 + k / 10) % 1
            c.drawPath(ellipse(0, -20, 380 * ph, 90 * ph), stroke('#9ac0e8', 3, (1 - ph) * 0.7))
        body = poly([(-420, 0), (-420, 90), (420, 90), (420, 0)])
        c.drawRect(skia.Rect.MakeXYWH(-420, 0, 840, 120), fill('#6a6476'))
        c.drawRect(skia.Rect.MakeXYWH(-420, 0, 840, 120), stroke(INK, 8))
        for k in range(8):
            c.drawLine(-420 + k * 120, 0, -420 + k * 120, 120, stroke('#3a3644', 4))
        c.drawRect(skia.Rect.MakeXYWH(-50, -380, 100, 380), fill('#6a6476'))
        c.drawRect(skia.Rect.MakeXYWH(-50, -380, 100, 380), stroke(INK, 7))
        c.drawPath(ellipse(0, -380, 180, 46), fill('#5a5466'))
        c.drawPath(ellipse(0, -380, 180, 46), stroke(INK, 7))
        for k in range(14):
            a = k / 14 * 2 * math.pi
            ph = (t * 1.5 + k * 0.13) % 1
            px = math.cos(a) * 170 * (0.3 + ph)
            py = -380 + ph * 380 * ph - 60 * math.sin(ph * math.pi)
            c.drawPath(ellipse(px, py, 6, 9), fill('#bfe0ff', 0.7 * (1 - ph)))


def square_scene_bg(c, cam, t, lit=0.0, bells=0.0):
    L = E.square_layers()
    with Save(c):
        cam.apply(c, 0.15)
        draw_img(c, L['sky'], 0, 0)
        E.cloud(c, 900 + t * 20, 800, 600, '#3a3a6a', 0.5)
    with Save(c):
        cam.apply(c, 0.45)
        draw_img(c, L['cath'], 0, 0)
        # swinging bells in the towers
        for k, sx in enumerate((-1, 1)):
            bx = 1700 + sx * 253
            sw = (0.55 * math.sin(beat(t) * math.pi + k * math.pi)) * bells
            E.bell(c, bx, 1080, sw, 0.9)
    with Save(c):
        cam.apply(c, 0.7)
        draw_img(c, L['houses'], 0, 0)
        if lit > 0:
            p = skia.Paint()
            p.setAlphaf(clamp(lit))
            c.drawImage(L['houses_lit'], 0, 0, skia.SamplingOptions(), p)
        for k, bx in enumerate((900, 2500)):
            c.drawLine(bx, 2100, bx, 1300, stroke('#2a1a10', 12))
            E.banner(c, bx + 60, 1320, 110, 380, t * (1 + 0.6 * bells), [BURG, '#2e4a7a'][k], GOLD, k, 1 + bells)
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['ground'], 0, 0)
    return L


def big_crowd(t, cx=1700, cy=2600, n_rows=4, per=7, sx=250, sy=150, s0=0.42, routine='grand', jitter=0.0,
              kinds=None, delay=0.0, energy=1.0, skip=None):
    kinds = kinds or ['skel', 'king', 'skel', 'peasant', 'skel', 'merchant', 'skel', 'jester', 'skel', 'knight',
                      'skel', 'bishop', 'woman', 'skel', 'noble', 'townsman']
    specs = []
    for r in range(n_rows):
        for k in range(per + r):
            x = cx + (k - (per + r - 1) / 2) * sx * (1 + r * 0.12)
            y = cy + r * sy
            if skip and skip(x, y):
                continue
            kind = kinds[(k * 3 + r * 5) % len(kinds)]
            sp = dict(kind=kind, x=x, y=y, s=s0 * (1 + r * 0.18), routine=routine, v=k + r,
                      delay=delay + jitter * _hash(k * 7 + r, 2), flip=((k + r) % 2 == 1), energy=energy,
                      expr=dict(trance=0.6, joy=0.4, mouth=0.3))
            if kind == 'knight':
                sp['armor'] = {'helm': (0, 0, 0, 0)}
            if kind == 'king':
                sp['ch'] = dict(Hm.CAST['king'], crown=1)
            specs.append(sp)
    return specs


def s07a_arrive(c, t, f):
    lt = t - B(23)
    cam = Cam(1700 - 300 + 200 * lt, 1850, 0.62, ref=(1700, 1900))
    square_scene_bg(c, cam, t, 0.0, 0.2)
    with Save(c):
        cam.apply(c, 1.0)
        fountain(c, 1700, 2450, t, 1.0)
        # the procession floods in from the left
        specs = big_crowd(t, 900 + 380 * lt, 2650, 3, 5, 230, 150, 0.5, 'macabre', 0.08)
        crowd(c, t, f, specs)
        death(c, 1500 + 160 * lt, 2560, 0.6, t, f, dance('fiddler', t), eye_glow=0.6)
    return {}


def s07b_leap(c, t, f):
    """kick roll: Death springs onto the fountain; the crowd crouches, waiting"""
    lt = t - B(24)
    tz = bar_t(24, 12)
    cam = Cam(1700, lerp(2000, 1800, smooth(ramp(t, B(24), tz))), lerp(0.75, 0.95, smooth(ramp(t, B(24), tz + 0.4))),
              ref=(1700, 1900))
    square_scene_bg(c, cam, t, 0.0, 0.0)
    with Save(c):
        cam.apply(c, 1.0)
        fountain(c, 1700, 2450, t, 1.0)
        # leap: crouch (anticipation) 0-0.4, jump arc to fountain top
        j0, j1 = bar_t(24, 4), bar_t(24, 8)
        u = ramp(t, j0, j1)
        x = lerp(1700, 1700, u)
        y = lerp(2650, 2070, ease_out(u, 2)) - math.sin(u * math.pi) * 420
        p = dance('fiddler', t)
        if t < j0:
            p.update(py=lerp(40, 180, smooth(ramp(t, B(24), j0))), hLx=-150, hLy=60, hRx=150, hRy=60)
        elif u < 1:
            p.update(py=-80, fLl=120, fRl=120, hLx=-200, hLy=-160, hRx=200, hRy=-160)
        else:
            land = pulse(t, j1, 0.01, 0.2)
            p.update(py=40 + 140 * land, hLx=-160, hLy=-40, hRx=160, hRy=-40)
            hold = smooth(ramp(t, tz - 0.25, tz))
            p['hRx'], p['hRy'] = lerp(160, 60, hold), lerp(-40, -420, hold)
            p['head'] = -0.25 * hold
        death(c, x, y, 0.72, t, f, p, fiddle=False, bowing=False, eye_glow=0.8 + hold_glow(t, tz), open_=0.0,
              sway=-30 * u)
        # crouching crowd around
        def crouch(pp):
            k = smooth(ramp(t, B(24), tz))
            pp['py'] += 90 * k
            pp['hLy'] = lerp(pp['hLy'], 120, k)
            pp['hRy'] = lerp(pp['hRy'], 120, k)
            return pp
        specs = big_crowd(t, 1700, 2750, 3, 6, 260, 160, 0.52, 'shuffle', 0.0,
                          skip=lambda x, y: abs(x - 1700) < 380 and y < 2900)
        for s_ in specs:
            s_['mod'] = crouch
        crowd(c, t, f, specs)
    return {}


def hold_glow(t, tz):
    return 0.6 * smooth(ramp(t, tz - 0.3, tz))


def s07c_breath(c, t, f):
    """one-beat silence: silhouette against the moon - then THE GRAND DROP"""
    tz = bar_t(24, 12)
    cam = Cam(1700, 1650, 1.25 + 0.15 * smooth(ramp(t, tz, B(25))), ref=(1700, 1900))
    L = E.square_layers()
    with Save(c):
        cam.apply(c, 0.15)
        draw_img(c, L['sky'], 0, 0)
    with Save(c):
        cam.apply(c, 0.45)
        draw_img(c, L['cath'], 0, 0)
    with Save(c):
        cam.apply(c, 1.0)
        # dark silhouette of Death raising the fiddle, framed by the moon direction
        c.drawRect(skia.Rect.MakeXYWH(0, 2000, 3400, 2000), fill('#07060c'))
        p = mkpose(fLx=-90, fRx=90, py=30, hLx=-170, hLy=-300, hRx=170, hRy=-330, head=-0.3)
        A.put(c, 1700, 2120, 0.8)
        skel.draw_death(c, t, p, f, fiddle=False, bowing=False, eye_glow=1.0)
    return dict(dim=0.35)


def s07d_drop(c, t, f):
    """THE GRAND DROP (42.353): cloak bursts open, windows ignite, bells swing, the whole square dances"""
    lt = t - B(25)
    sx, sy = shake(t, B(25), 26, 0.25, 21)
    # sweeping crane move through the square
    cx = 1700 + 420 * math.sin(lt * 0.55)
    cy = lerp(1650, 1900, smooth(ramp(lt, 0, 1.2)))
    z = lerp(1.05, 0.66, ease_out(ramp(lt, 0, 1.4), 3))
    cam = Cam(cx + sx, cy + sy, z, 0.02 * math.sin(lt * 0.9), ref=(1700, 1900))
    lit = smooth(ramp(t, B(25), B(25) + 0.5))
    square_scene_bg(c, cam, t, lit, 1.0)
    with Save(c):
        cam.apply(c, 1.0)
        fountain(c, 1700, 2450, t, 1.0)
        op = ease_out_back(ramp(t, B(25), B(25) + 0.35), 1.4)
        p = dance('fiddler', t)
        death(c, 1700, 2070, 0.72, t, f, p, open_=op, eye_glow=1.0, sway=30 * math.sin(t * 2), flutter=1.6)
        E.music_notes(c, t, 1700, 1500, 6, 3)
        specs = big_crowd(t, 1700, 2650, 4, 7, 250, 150, 0.46, 'grand', 0.0,
                          skip=lambda x, y: abs(x - 1700) < 380 and y < 2700)
        crowd(c, t, f, specs)
    with Save(c):
        cam.apply(c, 1.3)
        A.sparkle(c, 1700, 1700, t, B(25), 2.5, '#ffe39a', 24, 5)
    return dict(flash=0.7 * pulse(t, B(25), 0.01, 0.3))


# ==================================================================== SCENE 08 - THE GREAT DANCE (B27 - B33)
def street_bg(c, cam, t, variant=0):
    L = E.street_layers(variant)
    with Save(c):
        cam.apply(c, 0.3)
        draw_img(c, L['sky'], 0, 0)
    with Save(c):
        cam.apply(c, 0.8)
        draw_img(c, L['main'], 0, 0)
        E.fog(c, t, 2250, 2600, 3 + variant, 0.1)
    return L


def s08a_king_peasant(c, t, f):
    lt = t - B(27)
    cam = Cam(1300 + 120 * lt, 2000, 0.95, ref=(1300, 1950))
    street_bg(c, cam, t)
    with Save(c):
        cam.apply(c, 1.0)
        crowd(c, t, f, [dict(kind='skel', x=400 + i * 280 + 120 * lt, y=2300, s=0.45, routine='grand', v=i)
                        for i in range(8)])
        crowd(c, t, f, [dict(kind='king', x=1050 + 120 * lt, y=2600, s=0.78, routine='grand',
                             ch=dict(Hm.CAST['king'], crown=0), expr=dict(trance=0.5, joy=0.5, mouth=0.4)),
                        dict(kind='peasant', x=1600 + 120 * lt, y=2600, s=0.78, routine='grand',
                             expr=dict(trance=0.4, joy=0.7, mouth=0.4))])
    return {}


def s08b_knight_merchant(c, t, f):
    lt = t - B(28)
    cam = Cam(1300 - 100 * lt, 2000, 0.95, ref=(1300, 1950))
    street_bg(c, cam, t, 1)
    with Save(c):
        cam.apply(c, 1.0)
        crowd(c, t, f, [dict(kind=['skel', 'woman', 'skel', 'townsman'][i % 4], x=300 + i * 280, y=2300, s=0.45,
                             routine='grand', v=i, expr=dict(trance=0.6, joy=0.3)) for i in range(8)])
        arm, _ = knight_armor(99)
        crowd(c, t, f, [dict(kind='knight', x=1000, y=2600, s=0.78, routine='grand', armor=arm,
                             expr=dict(joy=0.7, trance=0.3, mouth=0.4)),
                        dict(kind='merchant', x=1600, y=2600, s=0.78, routine='grand',
                             expr=dict(joy=0.6, trance=0.4, mouth=0.4))])
    return {}


def s08b2_feet(c, t, f):
    """half-bar insert: dancing feet on cobblestones"""
    cam = Cam(1300 + 200 * (t - bar_t(28, 8)), 2560, 2.4, ref=(1300, 1950))
    street_bg(c, cam, t, 1)
    with Save(c):
        cam.apply(c, 1.0)
        arm, _ = knight_armor(99)
        crowd(c, t, f, [dict(kind=['skel', 'king', 'skel', 'jester', 'skel'][i], x=900 + i * 200, y=2720, s=0.8,
                             routine='grand', v=i, ch=dict(Hm.CAST['king'], crown=1) if i == 1 else None)
                        for i in range(5)])
    return {}


def balcony_musician(c, x, y, s, t, f, instr, seed):
    p = dance('shuffle', t, energy=0.5)
    b = beat(t)
    if instr == 'drum':
        hit = math.exp(-((b * 2) % 1) * PERIOD / 2 / 0.06)
        p.update(hLx=-40, hLy=lerp(120, 200, hit), hRx=40, hRy=lerp(200, 120, hit), head=0.15 * math.sin(b * math.pi))
    elif instr == 'horn':
        p.update(hLx=60, hLy=-60, hRx=-20, hRy=-50, head=-0.2, jaw=0.6)
    else:
        p.update(hLx=110, hLy=60, hRx=-60, hRy=100 + 30 * math.sin(t * 14), head=0.2)
    J = A.skeleton(c, x, y, s, t, f, p, v=seed, eyes='ember')
    wx, wy = x + J['wrL'][0] * s, y + J['wrL'][1] * s
    if instr == 'drum':
        c.drawPath(ellipse(x, y - 380 * s, 120 * s, 50 * s), fill('#8a2a1a'))
        c.drawRect(skia.Rect.MakeXYWH(x - 120 * s, y - 380 * s, 240 * s, 150 * s), fill('#8a2a1a'))
        c.drawRect(skia.Rect.MakeXYWH(x - 120 * s, y - 380 * s, 240 * s, 150 * s), stroke(INK, 4))
        c.drawPath(ellipse(x, y - 380 * s, 120 * s, 50 * s), fill('#e8dcc0'))
        c.drawPath(ellipse(x, y - 380 * s, 120 * s, 50 * s), stroke(INK, 4))
    elif instr == 'horn':
        hp = P()
        hp.moveTo(x + 20 * s, y - 860 * s)
        hp.quadTo(x + 200 * s, y - 900 * s, x + 330 * s, y - 1050 * s)
        c.drawPath(hp, stroke(INK, 30 * s))
        c.drawPath(hp, stroke(GOLD, 22 * s))
        c.drawPath(ellipse(x + 340 * s, y - 1060 * s, 50 * s, 50 * s), fill(GOLD_DK))
    else:
        c.drawPath(ellipse(wx - 60 * s, wy + 40 * s, 110 * s, 80 * s), fill('#a8521c'))
        c.drawPath(ellipse(wx - 60 * s, wy + 40 * s, 110 * s, 80 * s), stroke(INK, 4))
        c.drawLine(wx, wy, wx + 160 * s, wy - 120 * s, stroke('#3a1e10', 14 * s))


def s08c_orchestra(c, t, f):
    """jester with the skeleton orchestra on balconies & rooftops"""
    L = E.rooftop_layers()
    lt = t - B(29)
    cam = Cam(1300, 1900 - 60 * lt, 0.95, ref=(1300, 1950))
    with Save(c):
        cam.apply(c, 0.2)
        draw_img(c, L['sky'], 0, 0)
    with Save(c):
        cam.apply(c, 0.6)
        draw_img(c, L['roofs'], 0, 0)
    with Save(c):
        cam.apply(c, 1.0)
        # balcony
        c.drawRect(skia.Rect.MakeXYWH(250, 2050, 2100, 70), fill('#3a2a22'))
        for k in range(22):
            c.drawRect(skia.Rect.MakeXYWH(270 + k * 95, 2120, 22, 220), fill('#2a1e18'))
        c.drawRect(skia.Rect.MakeXYWH(250, 2340, 2100, 60), fill('#3a2a22'))
        c.drawRect(skia.Rect.MakeXYWH(250, 2050, 2100, 350), stroke(INK, 5))
        for k, (instr, x) in enumerate((('drum', 900), ('horn', 1620))):
            balcony_musician(c, x, 2050, 0.5, t, f, instr, k)
        human(c, 'jester', 1280, 2600, 0.85, t, f, dance('grand', t), expr=dict(joy=0.9, mouth=0.5),
              sway=20 * math.sin(t * 5))
        A.skeleton(c, 900, 2650, 0.75, t, f, dance('grand', t, delay=0.0), v=2, flip=True)
        A.skeleton(c, 1700, 2650, 0.75, t, f, dance('grand', t), v=1)
        E.music_notes(c, t, 1300, 1700, 6, 9)
    return {}


def s08d_overhead(c, t, f):
    """high-angle composition: a spinning ring of dancers around Death"""
    L = E.square_layers()
    lt = t - B(30)
    cam = Cam(1700, 2550, 0.72, 0.15 * math.sin(lt * 0.9), ref=(1700, 2500))
    with Save(c):
        cam.apply(c, 1.0)
        draw_img(c, L['ground'], 0, 0)
        c.drawPath(ellipse(1700, 2600, 900, 380), fill('#ffd27a', 0.08, blur=60))
        specs = []
        n = 12
        kinds = ['skel', 'king', 'skel', 'knight', 'skel', 'jester', 'skel', 'merchant', 'skel', 'peasant', 'skel', 'bishop']
        rot_ = beat(t) * 0.25
        for k in range(n):
            a = k / n * 2 * math.pi + rot_
            x = 1700 + math.cos(a) * 820
            y = 2620 + math.sin(a) * 360
            sp = dict(kind=kinds[k], x=x, y=y, s=0.38 + 0.12 * (math.sin(a) + 1) / 2, routine='grand', v=k,
                      expr=dict(trance=0.6, joy=0.4, mouth=0.3))
            if kinds[k] == 'knight':
                sp['armor'] = knight_armor(99)[0]
            specs.append(sp)
        specs.append(dict(kind='death', x=1700, y=2640, s=0.55, routine='fiddler', kw=dict(eye_glow=1.0, open_=0.6)))
        crowd(c, t, f, specs)
    return {}


def s08e_moon(c, t, f):
    """Neapolitan bar: silhouettes dancing against the giant moon on the rooftops"""
    L = E.rooftop_layers()
    lt = t - B(31)
    cam = Cam(1300 + 160 * lt, 1700, 0.85, ref=(1300, 1950))
    with Save(c):
        cam.apply(c, 0.2)
        draw_img(c, L['sky'], 0, 0)
    with Save(c):
        cam.apply(c, 1.0)
        # ridge line
        c.drawRect(skia.Rect.MakeXYWH(-500, 1830, 3600, 1600), fill('#0a0812'))
        sil = skia.Paint()
        sil.setColorFilter(skia.ColorFilters.Blend(hexc('#0a0812'), skia.BlendMode.kSrcIn))
        c.saveLayer(None, sil)
        specs = [dict(kind=k_, x=200 + i * 330 + 160 * lt, y=1840, s=0.5, routine='grand', v=i, delay=0.0)
                 for i, k_ in enumerate(['skel', 'king', 'skel', 'jester', 'skel', 'knight', 'skel', 'bishop'])]
        for sp in specs:
            if sp['kind'] == 'knight':
                sp['armor'] = knight_armor(99)[0]
        specs.append(dict(kind='death', x=1300 + 160 * lt, y=1840, s=0.62, routine='fiddler'))
        crowd(c, t, f, specs)
        c.restore()
    with Save(c):
        cam.apply(c, 1.3)
        E.fog(c, t, 2300, 2600, 14, 0.15, '#4a4a7a')
    return {}


def s08f_closeup(c, t, f):
    """extreme close-up: Death's grinning skull and the bow"""
    lt = t - B(32)
    cam = Cam(1300, 1440 - 40 * lt, 2.5 + 0.2 * lt, -0.04, ref=(1300, 1950))
    street_bg(c, cam, t, 0)
    with Save(c):
        cam.apply(c, 1.0)
        p = dance('fiddler', t)
        p['jaw'] = 0.3 + 0.3 * kick_env(t, 0.1)
        death(c, 1300, 2400, 0.85, t, f, p, eye_glow=1.0 + kick_env(t))
    return {}


def s08g_street(c, t, f):
    """wide street procession, Death leading toward camera"""
    lt = t - bar_t(32, 8)
    cam = Cam(1300, 1900, 0.72 + 0.04 * lt, ref=(1300, 1950))
    street_bg(c, cam, t, 0)
    with Save(c):
        cam.apply(c, 1.0)
        specs = big_crowd(t, 1300, 2300, 3, 6, 260, 140, 0.4, 'grand', 0.0)
        specs.append(dict(kind='death', x=1300, y=2800, s=0.75, routine='fiddler', kw=dict(eye_glow=1.0, open_=0.4)))
        crowd(c, t, f, specs)
    return {}


# ==================================================================== SCENE 09 - NOW IT'S YOUR TURN (B33 - 60)
def s09_final(c, t, f):
    hit = bar_t(33, 12)
    lt = t - B(33)
    z = lerp(0.62, 0.66, lt / 3.5)
    zz = smooth(ramp(t, hit + 0.3, 59.5))
    cam = Cam(1700, lerp(1950, 1700, zz), lerp(z, 1.45, ease_in(zz, 1.6)), ref=(1700, 1900))
    sx, sy = shake(t, hit, 24, 0.3, 31)
    cam.x += sx
    cam.y += sy
    square_scene_bg(c, cam, t, 1.0, 1.0 - smooth(ramp(t, hit, hit + 1)))
    frozen = t >= hit
    with Save(c):
        cam.apply(c, 1.0)
        fountain(c, 1700, 2450, t, 1.0)

        def freeze(pp, k=0):
            if not frozen:
                return pp
            fp = dance('grand', hit - 0.001)
            fp['turn'] = 0.0
            fp['head'] = lerp(fp['head'], 0.0, smooth(ramp(t, hit + 0.2, hit + 1.0)))
            fp['jaw'] = 0.0
            return fp
        specs = big_crowd(t, 1700, 2650, 4, 7, 250, 150, 0.46, 'grand', 0.0,
                          skip=lambda x, y: abs(x - 1700) < 380 and y < 2700)
        for s_ in specs:
            s_['mod'] = freeze
            if frozen:
                s_['expr'] = dict(trance=0.0, joy=0.0, fear=0.2, mouth=0.0)
        crowd(c, t, f, specs)
        # Death steps forward to the viewer, lowers the fiddle, tilts skull, extends a hand
        app = smooth(ramp(t, hit, 59.4))
        if not frozen:
            p = dance('fiddler', t)
            death(c, 1700, 2070, 0.72, t, f, p, open_=1.0, eye_glow=1.0)
        else:
            p = mkpose(fLx=-110, fRx=110, py=30, head=0.32 * smooth(ramp(t, hit + 0.4, hit + 0.9)), jaw=0.1,
                       hLx=-130, hLy=lerp(80, 120, app), hRx=lerp(150, 60, app), hRy=lerp(-40, -60, app),
                       curl=lerp(0.8, 0.2, app))
            y = lerp(2070, 2950, app)
            sc = lerp(0.72, 1.35, app)
            death(c, 1700, y, sc, t, f, p, fiddle=True, bowing=False, open_=1.0 - 0.6 * app, eye_glow=1.2)
    knocks = sum(pulse(t, bar_t(34, s_), 0.005, 0.08) for s_ in (12, 13, 14, 15))
    return dict(flash=0.6 * pulse(t, hit, 0.01, 0.3), knock=knocks)


# ==================================================================== SHOT LIST
SHOTS = [
    (0.0, B(3), s01_hook),
    (B(3), B(4), s02a_wide),
    (B(4), B(5), s02b_assemble),
    (B(5), B(6), s02c_feet),
    (B(6), B(7), s02d_procession),
    (B(7), B(8), s03a_throne),
    (B(8), B(9), s03b_offer),
    (B(9), B(10), s03c_crown),
    (B(10), B(11), s03d_king_dance),
    (B(11), B(13), s04a_challenge),
    (B(13), B(14), s04c_armor),
    (B(14), B(15), s04d_hand),
    (B(15), B(16), s05a_lock),
    (B(16), B(17), s05b_knock),
    (B(17), B(18), s05c_burst),
    (B(18), B(19), s05d_pulled),
    (B(19), B(20), s06a_bishop),
    (B(20), B(21), s06b_peasant),
    (B(21), B(22), s06c_jester),
    (B(22), B(23), s06d_noble),
    (B(23), B(24), s07a_arrive),
    (B(24), bar_t(24, 12), s07b_leap),
    (bar_t(24, 12), B(25), s07c_breath),
    (B(25), B(27), s07d_drop),
    (B(27), B(28), s08a_king_peasant),
    (B(28), bar_t(28, 8), s08b_knight_merchant),
    (bar_t(28, 8), B(29), s08b2_feet),
    (B(29), B(30), s08c_orchestra),
    (B(30), B(31), s08d_overhead),
    (B(31), B(32), s08e_moon),
    (B(32), bar_t(32, 8), s08f_closeup),
    (bar_t(32, 8), B(33), s08g_street),
    (B(33), 60.01, s09_final),
]


def shot_at(t):
    for i, (a, b, fn) in enumerate(SHOTS):
        if a <= t < b:
            return i, fn
    return len(SHOTS) - 1, SHOTS[-1][2]
