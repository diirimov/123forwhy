"""THE DARKEST CHRISTMAS LEGENDS - shot list, choreography, transitions, captions."""
import math, random, sys, os
import skia
from gfx import *
from world import *
from stages import stage, draw_stage, cam_apply, present, to_layer
from human import Human, INK, walk_pose, run_pose, shade_hex
from creatures import draw_krampus, draw_yule_cat, draw_cat_head, draw_mari, draw_tail, CAT

# ------------------------------------------------------------------ music clock
STEP = 60 / 128 / 4; BEAT = STEP * 4; BAR = BEAT * 4
SW = 0.07 * STEP
def T(bar, step=0.0):
    t = ((bar - 1) * 16 + step) * STEP
    if abs(step - round(step)) < 1e-9 and int(round(step)) % 2 == 1: t += SW
    return t
KICKS = [((b - 1) * 16 + s) * STEP for b in range(1, 49) for s in (0, 4, 8, 12)
         if not (b == 4 and s == 12) and not (b == 40 and s == 12) and not (b == 28 and s >= 10) and b != 48]
KICKS += [T(48, s) for s in (0, 3, 6, 12)]
KICKS.sort()
CLAPS = [T(b, s) for b in range(1, 48) for s in (4, 12) if not (b == 16 and s == 12) and not (b == 28 and s == 12) and b != 40]
def last_ev(t, evs):
    lo = None
    for e in evs:
        if e <= t + 1e-9: lo = e
        else: break
    return lo
def kick_pulse(t, tau=0.13):
    e = last_ev(t, KICKS); return 0.0 if e is None else math.exp(-(t - e) / tau)
def beat_no(t): return t / BEAT
def bob(t, amp=12, phase=0.0):
    """dance bounce landing on every beat (down on the beat)"""
    x = (t / BEAT + phase) % 1.0
    return -amp * math.sin(math.pi * x) ** 2 * 0 - amp * (1 - abs(math.cos(math.pi * x)))
def hop(t, times, h=60, dur=0.32):
    e = last_ev(t, times)
    if e is None or t - e > dur: return 0.0
    return -h * math.sin(math.pi * (t - e) / dur)
def pop(t, t0, dur=0.22):
    """scale 0 -> overshoot -> 1"""
    if t < t0: return 0.0
    return ease_out_back(seg(t, t0, t0 + dur), 2.4)
def punch(t, t0, amt=0.06, tau=0.18):
    return 1 + amt * decay(t, t0, tau)

# ------------------------------------------------------------------ cast
boy = Human('kid', hat='beanie', hat_col='#c8283a', coat='#3d7ec9', scarf='#f2c14e', hair='#7a4a22', seed=1)
girl = Human('kid', hat='none', hair='#3a2214', hair_style='bob', coat='#2f8f4e', scarf='#d62f3a', mitt='#f2c14e', seed=2)
kid2 = Human('kid', hat='beanie', hat_col='#f2c14e', pom='#d62f3a', coat='#8a3ab0', scarf='#4ac8ff', hair='#d8a050', seed=3)
kid3 = Human('kid', hat='stocking', hat_col='#2f8f4e', coat='#d97a2b', scarf='#ffffff', hair='#2a1a10', skin='#c98a5e', seed=4)
nick = Human('big', robe=True, hat='mitre', coat='#c8283a', beard='#f4f1ea', mitt='#f4f1ea', boots='#3a2418', skin='#f0c0a0')
lady = Human('elder', hat='bonnet', hat_col='#7a3b6e', coat='#5b3a6b', scarf='#d9a441', hair='#cfcfcf', hair_style='bun', glasses=True, apron='#efe6d8')
VILL = [Human('adult', hat='beanie', hat_col='#2f6b4f', coat='#b8452e', scarf='#f2c14e', hair='#4a2a18', seed=11),
        Human('adult', hat='none', hair='#e0b050', hair_style='long', coat='#3a6ab0', scarf='#ffffff', seed=12),
        Human('big', hat='flatcap', hat_col='#5a4a3a', coat='#5a7a3a', scarf='#d62f3a', beard='#6a4028', hair='#6a4028', seed=13),
        Human('adult', hat='stocking', hat_col='#d62f3a', coat='#7a3b6e', scarf='#4ac8ff', hair='#2a1a10', skin='#c98a5e', seed=14),
        Human('elder', hat='bonnet', hat_col='#2f6b4f', coat='#8a5a3a', scarf='#e86fa8', hair='#dddddd', hair_style='bun', seed=15),
        Human('kid', hat='beanie', hat_col='#3a7bd5', coat='#e8c547', scarf='#d62f3a', hair='#7a4a22', seed=16)]
jon = Human('adult', hat='none', hair='#c48a3a', sweater='#7d8b6a', patches=True, coat='#7d8b6a', scarf=None, beard='#c48a3a', pants='#4b4a5a', mitt='#e0b090', seed=21)
ice_w = Human('adult', hat='beanie', hat_col='#2f8f6e', coat='#d23c3c', hair='#e8d08a', hair_style='long', scarf='#f2c14e', sweater='#d23c3c', seed=22)
ice_m = Human('big', hat='none', hair='#2a2018', beard='#2a2018', coat='#3f7fbf', sweater='#3f7fbf', scarf='#ffffff', seed=23)
ice_k = Human('kid', hat='beanie', hat_col='#d23c3c', coat='#f2c14e', sweater='#f2c14e', scarf='#3f7fbf', hair='#f0d890', seed=24)
dai = Human('adult', hat='flatcap', hat_col='#5a5a6a', coat='#7a3b2e', hair='#8a8a8a', glasses=True, pants='#3a3550', scarf='#2f8f4e', mitt='#f0c0a0', seed=31)
wass = [Human('adult', hat='stocking', hat_col='#d62f3a', coat='#2f3f6a', scarf='#f2c14e', hair='#3a2214', seed=32),
        Human('big', hat='flatcap', hat_col='#3a2a20', coat='#5a3a2a', scarf='#d62f3a', beard='#8a5a30', hair='#8a5a30', seed=33),
        Human('adult', hat='bonnet', hat_col='#2f6b4f', coat='#6a2f4a', scarf='#ffffff', hair='#c0602a', hair_style='long', seed=34)]

# ------------------------------------------------------------------ props
def it_present(colr='#d62f3a', rib='#f2c14e', size=1.0):
    def f(c, x, y, ang):
        present(c, x, y + 40 * size, 80 * size, 64 * size, colr, rib)
    return f
def it_snowball(c, x, y, ang):
    c.drawCircle(x, y - 6, 20, P(INK)); c.drawCircle(x, y - 6, 17, PS(rad((x - 6, y - 12), 22, ['#ffffff', '#cfdcff'])))
def it_lantern(c, x, y, ang):
    c.drawLine(x, y, x, y + 30, P(INK, 255, stroke=4))
    glow(c, x, y + 60, 110, '#ffc35a', 170)
    c.drawPath(rrect(x - 20, y + 30, 40, 56, 8), P(INK)); c.drawPath(rrect(x - 16, y + 34, 32, 48, 6), P('#ffe39a'))
def it_mug(c, x, y, ang):
    c.drawPath(rrect(x - 18, y - 30, 36, 40, 6), P(INK)); c.drawPath(rrect(x - 15, y - 27, 30, 34, 5), P('#d62f3a'))
    c.drawCircle(x + 20, y - 12, 9, P(INK, 255, stroke=5))
def it_broom(c, x, y, ang):
    c.drawLine(x, y - 90, x + 10, y + 110, P(INK, 255, stroke=10)); c.drawLine(x, y - 90, x + 10, y + 110, P('#9a6a44', 255, stroke=6))
    bp = path_from([(x - 20, y + 100), (x + 40, y + 100), (x + 55, y + 170), (x - 35, y + 170)], True, 0.3)
    c.drawPath(bp, P(INK, 255, stroke=6)); c.drawPath(bp, P('#e8c86a'))
def it_basket(c, x, y, ang):
    bp = path_from([(x - 45, y), (x + 45, y), (x + 35, y + 55), (x - 35, y + 55)], True, 0.4)
    c.drawPath(bp, P(INK, 255, stroke=7)); c.drawPath(bp, P('#c08a4a'))
    for k in range(3): c.drawCircle(x - 20 + k * 20, y - 6, 14, P(('#d62f3a', '#f2c14e', '#2f8f4e')[k]))
def it_pane(c, x, y, ang):
    c.drawPath(rrect(x - 40, y - 60, 80, 90, 4), P(INK, 255, stroke=8)); c.drawPath(rrect(x - 40, y - 60, 80, 90, 4), P('#bfe3ff', 200))
    c.drawLine(x - 25, y - 40, x - 5, y - 55, P('#ffffff', 220, stroke=5))
def it_box_open(c, x, y, ang): pass

def notes(c, x, y, t, t0, dirx=1, n=3, colr='#ffe680', seed=0):
    """musical notes flying out (rhyme battle)"""
    if t < t0 or t > t0 + 0.9: return
    u = (t - t0) / 0.9; r = random.Random(seed)
    for k in range(n):
        dx = dirx * (60 + 260 * u + k * 50); dy = -80 * math.sin(u * 3 + k) - 120 * u - k * 30
        a = int(255 * (1 - u))
        nx, ny = x + dx, y + dy
        c.save(); c.translate(nx, ny); c.rotate(r.uniform(-20, 20))
        c.drawOval(skia.Rect.MakeLTRB(-16, -10, 16, 10), P(INK, a)); c.drawOval(skia.Rect.MakeLTRB(-13, -8, 13, 8), P(colr, a))
        c.drawLine(12, 0, 12, -50, P(INK, a, stroke=6)); c.drawLine(12, -50, 30, -38, P(INK, a, stroke=6))
        c.restore()

# ------------------------------------------------------------------ common post layers
SNOW = Snow(240, 7); SNOW2 = Snow(90, 19)
def snow_front(c, t, a=1.0, speed=1.0): SNOW.draw(c, t, 0.15, a, layer='front', speed=speed)
def snow_back(c, t, a=1.0, speed=1.0): SNOW.draw(c, t, 0.15, a, layer='back', speed=speed)
def darken(c, a, colr='#05030f'):
    if a > 0: c.drawRect(skia.Rect.MakeWH(W, H), P(colr, int(255 * clamp(a))))
def flash(c, t, t0, dur=0.25, colr='#ffffff', amt=0.85):
    if t0 <= t < t0 + dur: c.drawRect(skia.Rect.MakeWH(W, H), P(colr, int(255 * amt * (1 - (t - t0) / dur))))
def light_rays(c, x, y, t, a=0.25, colr='#ffe7a8'):
    for k in range(12):
        ang = k * math.pi / 6 + t * 0.4
        p = path_from([(x, y), (x + math.cos(ang - 0.08) * 1400, y + math.sin(ang - 0.08) * 1400), (x + math.cos(ang + 0.08) * 1400, y + math.sin(ang + 0.08) * 1400)], True)
        c.drawPath(p, PS(rad((x, y), 1400, [(colr, int(255 * a)), (colr, 0)])))
def shake(t, t0, amt=14, dur=0.3):
    if t < t0 or t > t0 + dur: return (0, 0)
    k = (1 - (t - t0) / dur) * amt
    return (math.sin(t * 90) * k, math.cos(t * 77) * k)

# ==================================================================  ACT 0
def s_open_fly(c, t):
    st = stage('opening'); lt = t
    camx = lerp(700, 2200, ease_in_out(lt / 3.75) * 0.85 + lt / 3.75 * 0.15)
    z = 1.0 + 0.06 * lt / 3.75
    cam = (camx, 1000, z * punch(t, 0.0, 0.05))
    def crowd(cc):
        # dancing villagers along the street (world coords, parallax 1)
        for k, v in enumerate(VILL * 2):
            x = 500 + k * 330 + (k % 3) * 40
            ph = (k % 4) * 0.25
            b = bob(t, 16)
            hands_up = (int(t / BEAT) + k) % 4 == 1
            v.draw(cc, x=x, y=1770 + (k % 2) * 60, s=1.15, bob=b, lean=math.sin((t / BEAT + k) * math.pi) * 6,
                   arm_l=(150, 20) if hands_up else (40 + 30 * math.sin(t * 6 + k), 60), arm_r=(150, 20) if hands_up else (40 + 30 * math.cos(t * 6 + k), 60),
                   leg_l=(10 * math.sin(t / BEAT * math.pi * 2 + k), 15), leg_r=(-10 * math.sin(t / BEAT * math.pi * 2 + k), 15),
                   mouth='grin' if k % 2 else 'smile', mouth_open=0.5, eyes='happy' if k % 3 == 0 else 'open', cheeks=1,
                   head_tilt=math.sin((t / BEAT + k * 0.5) * math.pi) * 8, face=1 if k % 2 else -1)
        # kids snowball fight in foreground
        throw_t = [0.47, 1.41, 2.34, 3.28]
        for k, kd in enumerate((girl, kid2, kid3)):
            x = 1000 + k * 520
            e = last_ev(t, throw_t)
            wind = 0 if e is None else clamp((t - e) / 0.2)
            kd.draw(cc, x=x, y=1900, s=1.35, bob=hop(t, throw_t[k % 2::2], 40), arm_r=(160 - 120 * wind, 20), arm_l=(30, 30),
                    mouth='grin', mouth_open=0.7, eyes='open', look=(0.6, -0.3), cheeks=1, face=1 if k != 1 else -1)
    snowfx = lambda cc: None
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={3: crowd})
    snow_front(c, t)

def s_nicholas(c, t):
    st = stage('square'); lt = t - 3.75
    z = 1.05 + 0.08 * ease_in_out(lt / 3.75)
    cam = (900, 1180, z * punch(t, T(4), 0.04) * punch(t, T(4, 4), 0.04) * punch(t, T(4, 8), 0.04))
    dim = 0.55 * ease_out(seg(t, T(4) - 0.1, T(4) + 0.3))
    def sil(cc):
        # three giant legends rise behind the rooftops on consecutive accents (screen space)
        a1 = ease_out_back(seg(t, T(4), T(4) + 0.3), 1.3); a2 = ease_out(seg(t, T(4, 4), T(4, 4) + 0.2)); a3 = ease_out_back(seg(t, T(4, 8), T(4, 8) + 0.3), 1.3)
        cc.save(); cc.translate(*shake(t, T(4), 10, 0.25))
        if a1 > 0:
            draw_krampus(cc, x=190, y=1450 + 420 * (1 - a1), s=1.05, silhouette=True, arm_l=(60, 40), arm_r=(60, 40), eyes='narrow', switch=False)
        if a2 > 0:
            cc.save(); cc.translate(560, 660); cc.scale(0.72, 0.72)
            for sx in (-1, 1):
                glow(cc, sx * 120, -30, 220, '#ffcf3a', int(150 * a2))
            draw_cat_head(cc, dict(eye_open=a2, narrow=0.25, pupil=0.12, look=(0.2, 0.6), ear=0.0, mouth=0, tongue=0, nose=0, glow=1.4,
                                   rim='#232a5a', confused=0, blink=0), 255)
            cc.restore()
        if a3 > 0:
            draw_mari(cc, x=880, y=1400 + 420 * (1 - a3), s=0.95, jaw=0.8 * bump(t, T(4, 8) + 0.1, 0.3) + 0.6 * bump(t, T(4, 12), 0.25), sway=t * 0.5, ribbon=t)
        cc.restore()
    def people(cc):
        darken_people = 0
        gift_t = [T(3, 0), T(3, 4), T(3, 8), T(3, 12)]
        kids = (girl, kid2, kid3, VILL[5])
        e = last_ev(t, gift_t); gi = gift_t.index(e) if e is not None else -1
        frozen = t >= T(4)
        look_back = t >= T(4, 12)
        nick.draw(cc, x=900, y=1820, s=1.55, bob=0 if frozen else bob(t, 8), arm_r=(70 + 30 * bump(t, e or 0, 0.3), 30), arm_l=(20, 20),
                  eyes='happy' if not frozen else ('wide' if look_back else 'open'), mouth='smile' if not frozen else 'o', mouth_open=0.4,
                  look=(-0.8, -0.5) if look_back else (0.4, 0), head_tilt=-8 if look_back else 0, sweat=1 if look_back else 0,
                  items={'r': it_present(('#d62f3a', '#2f8f4e', '#3a7bd5', '#f2c14e')[max(gi, 0) % 4])} if not frozen else None)
        for k, kd in enumerate(kids):
            x = 380 + k * 160 if k < 2 else 1240 + (k - 2) * 170
            got = k <= gi
            shiver = math.sin(t * 55 + k * 2) * 3 * seg(t, T(4), T(4) + 0.2) if frozen else 0
            kd.draw(cc, x=x + shiver, y=1880 + (k % 2) * 30, s=1.25, bob=hop(t, [gift_t[k]], 70) if not frozen else 0, sweat=seg(t, T(4, 4), T(4, 8)) if frozen else 0,
                    head_tilt=(-6 * math.sin((t - T(4)) * 9 + k)) if frozen else 0,
                    arm_l=(130, 30) if got and not frozen else (20, 20), arm_r=(130, 30) if got and not frozen else (20, 20),
                    mouth='grin' if (got and not frozen) else ('o' if frozen else 'smile'), mouth_open=0.6,
                    eyes='happy' if (got and not frozen) else ('wide' if frozen else 'open'), cheeks=1, face=1 if k < 2 else -1,
                    look=(0.5, -0.6) if frozen else (0.5, 0), items={'l': it_present(('#d62f3a', '#2f8f4e', '#3a7bd5', '#f2c14e')[k], size=0.7)} if got else None)
    draw_stage(c, st, cam, t, kick_pulse(t) * (1 - dim), beat=beat_no(t), light_alpha=1 - dim * 0.6,
               between={1: lambda cc: darken_layer(cc, dim * 0.6), 3: people}, screen={1: sil})
    snow_front(c, t)
    # red danger tint when silhouettes appear
    if dim > 0: c.drawRect(skia.Rect.MakeWH(W, H), PS(rad((W / 2, H * 0.4), H * 0.8, [('#3a0010', 0), ('#200010', int(140 * dim))])))
    flash(c, t, T(5), 0.3, '#ffffff', 0.9)

def darken_layer(cc, a):
    if a > 0: cc.drawRect(skia.Rect.MakeLTRB(-2000, -2000, 6000, 4000), P('#05030f', int(255 * a)))

# ==================================================================  ACT 1 : KRAMPUS (Alpine)
def alp_cam(x, y=1000, z=1.0): return (x, y, z)

def s_k1(c, t):  # 7.5 - 11.25  Nicholas gives presents to good children
    st = stage('alpine'); lt = t - T(5)
    z = 1.25 - 0.18 * ease_out(lt / 1.2)
    cam = alp_cam(1300 + lt * 40, 1080, z * punch(t, T(5), 0.08))
    gift_t = [T(5, 4), T(5, 12), T(6, 4), T(6, 8)]
    def people(cc):
        # background villagers walking with lanterns (different phases)
        for k in range(3):
            v = VILL[k]; x = 400 + ((t * 70 + k * 600) % 2400); ph = t * 1.1 + k * 0.33
            wp = walk_pose(ph); v.draw(cc, x=x, y=1610, s=0.85, **wp, mouth='smile', face=1, items={'r': it_lantern})
        e = last_ev(t, gift_t); gi = gift_t.index(e) if e is not None else -1
        nick.draw(cc, x=1300, y=1800, s=1.5, bob=bob(t, 6), arm_r=(75 + 35 * bump(t, e or 0, 0.3), 25), arm_l=(15, 20),
                  eyes='happy', mouth='smile', head_tilt=6 * math.sin(t * 3), items={'r': it_present(('#d62f3a', '#2f8f4e', '#3a7bd5', '#f2c14e')[max(gi, 0) % 4])})
        for k, kd in enumerate((girl, kid2, kid3)):
            got = k <= gi
            kd.draw(cc, x=1560 + k * 150, y=1860 + (k % 2) * 20, s=1.2, face=-1, bob=hop(t, [gift_t[k]], 80) + (0 if got else bob(t, 5)),
                    arm_l=(140, 20) if got else (25, 30), arm_r=(140, 20) if got else (25, 30), mouth='grin' if got else 'smile', mouth_open=0.6,
                    eyes='happy' if got else 'open', cheeks=1, items={'r': it_present(('#d62f3a', '#2f8f4e', '#3a7bd5')[k], size=0.7)} if got else None)
        # naughty boy peeks from behind snowman on the brass growl
        pk = ease_out_back(seg(t, T(6, 12), T(6, 12) + 0.15)) * (1 - seg(t, T(7) - 0.15, T(7)))
        snowman(cc, 900, 1840, 0.9)
        if pk > 0:
            boy.draw(cc, x=900 + 120 * pk, y=1860, s=1.1, mouth='grin', mouth_open=0.6, eyes='narrow', brows=(25, 0), look=(0.8, 0), lean=-12 * pk,
                     arm_r=(120, 40), items={'r': it_snowball}, face=1)
            snowman(cc, 900, 1840, 0.9)  # keep the boy half-hidden
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={2: people})
    snow_front(c, t)
    snow_burst(c, W / 2, 700, t, T(5), 70, 700, 3, size=1.4)

def s_k2(c, t):  # 11.25 - 15  snowball breaks window, smug, shadow grows
    st = stage('alpine'); lt = t - T(7)
    cam = alp_cam(2050 + lt * 25, 1150, 1.25 * punch(t, T(7, 8), 0.05))
    windup = seg(t, T(7), T(7, 4)); thrown = t >= T(7, 4)
    def scene(cc):
        # target window is house window in world; draw a big breakable window prop on the house wall
        wx, wy = 2350, 1300
        house(cc, 2170, 1560, 380, 400, 'chalet', '#c98b5a', '#7a2f2a', L=None, seed=77, lights=True, wreath=True, chimney=True, shutters='#2f6b4f')
        broken = t >= T(7, 8)
        cc.save()
        if not broken:
            window(cc, wx - 60, wy - 80, 120, 150, True, None, '#2f6b4f')
        else:
            cc.drawPath(rrect(wx - 60, wy - 80, 120, 150, 4), P(INK, 255, stroke=10)); cc.drawPath(rrect(wx - 60, wy - 80, 120, 150, 4), P('#1a1430'))
            for k in range(7):
                ang = k * 0.9; cc.drawLine(wx, wy, wx + math.cos(ang) * 70, wy + math.sin(ang) * 80, P('#bfe3ff', 255, stroke=4))
            # flying shards
            u = t - T(7, 8)
            if u < 1.0:
                r = random.Random(2)
                for k in range(14):
                    vx = r.uniform(-400, 400); vy = r.uniform(-500, -100)
                    sx, sy = wx + vx * u, wy + vy * u + 900 * u * u
                    cc.drawPath(path_from([(sx, sy), (sx + 14, sy + 4), (sx + 4, sy + 18)], True), P('#d8f0ff', int(255 * (1 - u))))
        cc.restore()
        snow_burst(cc, wx, wy, t, T(7, 8), 40, 260, 9)
        # snowball arc
        if thrown and t < T(7, 8):
            u = seg(t, T(7, 4), T(7, 8))
            sx = lerp(1950, wx, u); sy = lerp(1620, wy, u) - 380 * math.sin(math.pi * u)
            it_snowball(cc, sx, sy + 6, 0)
        smug = t >= T(7, 12)
        shadow = ease_in_out(seg(t, T(8), T(8, 14)))
        # creeping shadow of Krampus on the wall behind the boy
        if shadow > 0:
            cc.save(); cc.translate(1950, 1880); cc.scale(1, 1)
            draw_krampus(cc, x=-160, y=0, s=0.4 + 0.75 * shadow, silhouette=True, alpha=int(200 * shadow), arm_l=(70, 50), arm_r=(70, 50),
                         eye_glow=ease_out(seg(t, T(8, 12), T(8, 13))), eyes='narrow')
            cc.restore()
        pose = {}
        if not thrown:
            pose = dict(arm_r=(200 - 60 * (1 - windup), 50), lean=-10 * windup, items={'r': it_snowball}, mouth='smirk', eyes='narrow', brows=(20, 0))
        elif not smug:
            pose = dict(arm_r=(70, 10), lean=10, mouth='grin', mouth_open=0.4, eyes='open', look=(1, -0.3))
        else:
            pose = dict(arm_r=(140, 140), arm_l=(140, 140), mouth='grin', mouth_open=0.3, eyes='happy', cheeks=1, brows=(-10, 0.4),
                        bob=bob(t, 6), head_tilt=8 * math.sin(t * 6))
        boy.draw(cc, x=1950, y=1880, s=1.7, **pose)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={2: scene})
    # growl hits: lights flicker
    if T(8, 12) <= t < T(9): darken(c, 0.25 * (1 + math.sin(t * 60)) / 2)
    snow_front(c, t)

def s_k3(c, t):  # 15 - 18.75  KRAMPUS REVEAL
    st = stage('alpine'); lt = t - T(9)
    cam = alp_cam(2600, 1000, 1.0 * punch(t, T(9), 0.12) * punch(t, T(10), 0.05) * punch(t, T(10, 3), 0.05) * punch(t, T(10, 6), 0.06))
    sx, sy = shake(t, T(9), 22, 0.35)
    rise = ease_out_back(seg(t, T(9) - 0.05, T(9) + 0.35), 1.6)
    stab = [T(10, 0), T(10, 3), T(10, 6)]
    e = last_ev(t, stab); si = stab.index(e) if e is not None else -1
    stomp_t = [T(9, 4), T(9, 10), T(9, 12), T(10, 12)]
    def scene(cc):
        cc.save(); cc.translate(sx, sy)
        light_rays(cc, 2600, 900, t, 0.12, '#ff6a4a')
        poses = [dict(arm_l=(110, 40), arm_r=(110, 40), jaw=0.7, tongue=0.0, brow=(25, 0), eyes='wide'),
                 dict(arm_l=(160, 10), arm_r=(60, 80), jaw=0.3, tongue=0.8, brow=(15, 0.5), eyes='open', look=(0.5, 0.3)),
                 dict(arm_l=(30, 100), arm_r=(150, 10), jaw=0.9, tongue=0.3, brow=(30, 0), eyes='narrow'),
                 dict(arm_l=(170, 0), arm_r=(170, 0), jaw=1.0, tongue=1.0, brow=(30, 0.2), eyes='wide')]
        pz = poses[0] if si < 0 else poses[si + 1]
        legs = (10 + 20 * hop(t, stomp_t, 1, 0.25), -6)
        draw_krampus(cc, x=2600, y=1820 + (1 - rise) * 900, s=1.25 * punch(t, e or -9, 0.05), chain=t * 2.2, bob=hop(t, stomp_t, 40, 0.25),
                     leg_l=(10 - 30 * abs(hop(t, stomp_t[::2], 1, 0.25)), 0), leg_r=(-6 + 30 * abs(hop(t, stomp_t[1::2], 1, 0.25)), 0), **pz)
        # boy small in foreground (still smug, unaware)
        boy.draw(cc, x=2250, y=1900, s=1.2, mouth='grin', mouth_open=0.3, eyes='happy', arm_r=(140, 140), arm_l=(140, 140), bob=bob(t, 5))
        for s_ in stomp_t: snow_burst(cc, 2600, 1840, t, s_, 24, 300, int(s_ * 10), size=0.9)
        cc.restore()
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), light_alpha=0.8, between={1: lambda cc: darken_layer(cc, 0.35), 2: scene})
    c.drawRect(skia.Rect.MakeWH(W, H), PS(rad((W / 2, H * 0.45), H * 0.7, [('#ff3020', 0), ('#40000a', 110)])))
    snow_front(c, t)
    flash(c, t, T(9), 0.2, '#fff0e0', 0.7)

def s_k4(c, t):  # 18.75 - 22.5 boy turns, terror, chase begins
    lt = t - T(11)
    # close-up: boy face big, Krampus looming blurred behind
    st = stage('alpine')
    turn = ease_in_out(seg(t, T(11), T(12) - 0.05))
    terror = t >= T(12)
    z = 1.6 + 0.4 * ease_in_out(seg(t, T(11), T(12))) + (0.25 * ease_out(seg(t, T(12), T(12) + 0.15)) if terror else 0)
    cam = (2600, 1250, z)
    runoff = ease_in(seg(t, T(12, 9), T(13) - 0.02))
    def scene(cc):
        draw_krampus(cc, x=2780, y=2050, s=1.6, chain=t * 2, jaw=0.4 + 0.3 * math.sin(t * 8), tongue=0.6, eyes='narrow', brow=(25, 0),
                     arm_l=(90, 60), arm_r=(120, 30), look=(-0.6, 0.6), head_tilt=-10)
        darken_layer(cc, 0.2)
        if not terror:
            boy.draw(cc, x=2500, y=1900, s=1.6, turn=-turn, face=1 if turn < 0.5 else -1, eyes='open', look=(1 - 2 * turn, 0),
                     mouth='smirk' if turn < 0.4 else 'flat', head_tilt=-6 * turn, arm_r=(30, 30), arm_l=(30, 30),
                     brows=(0, 0.2 + turn * 0.4), sweat=seg(t, T(11, 12), T(12)))
        else:
            stabs = [T(12, 0), T(12, 3), T(12, 6)]
            e = last_ev(t, stabs); k = stabs.index(e) if e is not None else 0
            rp = run_pose(t * 3.5) if t > T(12, 9) else {}
            pz = dict(arm_l=(160, 20), arm_r=(160, 20), bob=0); pz.update(rp)
            boy.draw(cc, x=2500 - 900 * runoff, y=1900 + hop(t, stabs, 70, 0.2), s=1.6 * punch(t, e, 0.06), face=-1, eyes='wide', mouth='scream', mouth_open=1.0,
                     hair_up=min(1.0, k * 0.5 + 0.2), sweat=1, brows=(30, 1), **pz)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), light_alpha=0.8, between={2: scene})
    if terror:
        # comic speed lines
        a = int(160 * decay(t, T(12), 0.6))
        for k in range(18):
            ang = k * math.pi / 9 + 0.1
            c.drawLine(W / 2 + math.cos(ang) * 420, H * 0.55 + math.sin(ang) * 420, W / 2 + math.cos(ang) * 1300, H * 0.55 + math.sin(ang) * 1300, P('#ffffff', a, stroke=8))
    snow_front(c, t)

def s_k5(c, t):  # 22.5 - 26.25  CHASE through the village
    st = stage('alpine'); lt = t - T(13)
    speed = 620
    bx = 4400 - lt * speed  # boy world x (running left)
    cam = (bx + 170, 1000, 1.0)
    # events
    slide = (T(13, 4), T(13, 10)); jump = (T(13, 12), T(14))
    snowman_hit = T(14); doors = [T(14, 4), T(14, 8), T(14, 12), T(15)]
    def scene(cc):
        # houses doors slam: draw villagers leaning out & doors
        for k, dt in enumerate(doors):
            dx = bx - 320 - (dt - t) * speed * 0  # doors placed where boy passes at time dt
            wxp = 4400 - (dt - T(13)) * speed - 200
            shut = ease_out_back(seg(t, dt - 0.05, dt + 0.08), 2)
            # door frame
            cc.drawPath(rrect(wxp - 70, 1420, 140, 200, 10), P(INK)); cc.drawPath(rrect(wxp - 62, 1428, 124, 192, 8), P('#ffcf6e'))
            if shut < 1:
                VILL[k % 5].draw(cc, x=wxp, y=1620, s=0.75, mouth='o', mouth_open=0.8, eyes='wide', arm_l=(100, 40), arm_r=(100, 40))
            cc.save(); cc.translate(wxp - 62, 1428); cc.scale(max(0.08, 1 - (1 - shut) * 0.95) if shut > 0 else 0.08, 1)
            dp = rrect(0, 0, 124, 192, 8); cc.drawPath(dp, P(INK, 255, stroke=8)); cc.drawPath(dp, P(('#7a2f2a', '#2f6b4f', '#3f4a6a', '#6a2f22')[k]))
            cc.drawCircle(100, 100, 7, P('#f0c64a')); cc.restore()
            if t >= dt: snow_burst(cc, wxp, 1430, t, dt, 18, 160, k + 40, size=0.6)
        # ice patch & fence & snowman
        cc.drawOval(skia.Rect.MakeLTRB(4400 - (slide[0] - T(13)) * speed - 300, 1890, 4400 - (slide[1] - T(13)) * speed + 100, 1930), P('#bfe8ff', 220))
        fx = 4400 - (jump[0] - T(13)) * speed - 260
        fence(cc, fx - 60, fx + 140, 1900, 90)
        smx = 4400 - (snowman_hit - T(13)) * speed + 60
        # Krampus behind the boy
        kx = bx + 470 + 50 * math.sin(lt * 3)
        col_ = ease_out(seg(t, snowman_hit + 0.06, snowman_hit + 0.6)) if t >= snowman_hit else 0
        snowman(cc, smx, 1900, 1.1, col_)
        # boy
        sliding = slide[0] <= t < slide[1]; jumping = jump[0] <= t < jump[1]
        if sliding:
            pose = dict(leg_l=(-50, 0), leg_r=(40, 0), arm_l=(110, 20), arm_r=(80, 20), lean=-20, bob=0)
        elif jumping:
            u = seg(t, *jump); pose = dict(leg_l=(60, 90), leg_r=(-40, 60), arm_l=(150, 10), arm_r=(150, 10), lean=10, bob=-320 * math.sin(math.pi * u))
        else:
            pose = run_pose(t * 4.27)  # 2 steps per beat
        boy.draw(cc, x=bx, y=1910, s=1.35, face=-1, eyes='wide', mouth='scream', mouth_open=0.8 + 0.2 * math.sin(t * 20), hair_up=1.0, sweat=1, **pose)
        stomp = [k_ for k_ in KICKS if T(13) <= k_ < T(15)]
        kp = hop(t, stomp, 40, 0.22)
        draw_krampus(cc, x=kx, y=1930, s=0.95, face=-1, chain=t * 3, bob=kp, jaw=0.6, tongue=1.0, eyes='wide', brow=(20, 0.5),
                     arm_l=(100, 50), arm_r=(130, 60), lean=-8, leg_l=(35 * math.sin(t * 13.4), 0), leg_r=(-35 * math.sin(t * 13.4), 0))
        for k_ in stomp: snow_burst(cc, kx, 1930, t, k_, 10, 160, int(k_ * 100), size=0.7)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={2: scene})
    # speed lines across the frame
    for k in range(10):
        y = 300 + k * 160 + 40 * math.sin(k * 3.1)
        x = (k * 397 + t * 2600) % (W + 600) - 300
        c.drawLine(x, y, x + 260, y, P('#ffffff', 60, stroke=4))
    snow_front(c, t, speed=1.6)

def s_k6(c, t):  # 26.25 - 30  behaves perfectly, Krampus approves
    st = stage('alpine'); lt = t - T(15)
    cam = (1550, 1150, 1.08 * punch(t, T(16), 0.05))
    acts = [T(15, 0), T(15, 4), T(15, 8), T(15, 12)]
    e = last_ev(t, acts); ai = acts.index(e) if e is not None else 0
    def scene(cc):
        # repaired window on the left house
        window(cc, 1130, 1200, 120, 150, True, None, '#2f6b4f')
        if t >= acts[1]:
            for k in range(3): sparkle(cc, 1190 + 60 * math.cos(k * 2 + t), 1270 + 60 * math.sin(k * 2 + t * 1.3), 18 * pop(t, acts[1]), 220)
        lady.draw(cc, x=1620, y=1860, s=1.3, face=-1, mouth='smile', eyes='happy' if ai >= 3 else 'open', cheeks=1, bob=bob(t, 4),
                  arm_l=(50, 50), arm_r=(50, 50))
        poses = [dict(arm_l=(30, 120), arm_r=(30, 120), eyes='happy', mouth='smile', head_tilt=-8),
                 dict(arm_l=(150, 20), arm_r=(150, 20), items={'r': it_pane}, mouth='grin', mouth_open=0.3, eyes='open', look=(-0.6, -0.6)),
                 dict(arm_l=(60, 30), arm_r=(80, 20), items={'r': it_broom}, mouth='smile', eyes='happy', lean=8 * math.sin(t * 14)),
                 dict(arm_l=(80, 40), arm_r=(80, 40), items={'r': it_basket}, mouth='grin', mouth_open=0.3, eyes='happy', cheeks=1)]
        bx = [1330, 1180, 1300, 1420][ai]
        sc = 1.45 * (1 + 0.15 * (1 - ease_out_back(seg(t, e or 0, (e or 0) + 0.2), 2.5)) * 0)
        sq = 1 + 0.18 * decay(t, e or 0, 0.08)
        boy.draw(cc, x=bx, y=1880, s=1.45, sq=1 / sq, **poses[ai])
        # halo
        hx = bx; hy = 1880 - 1.45 * 300 - 20
        cc.drawOval(skia.Rect.MakeLTRB(hx - 55, hy - 14, hx + 55, hy + 14), P('#ffe680', 230, stroke=8)); glow(cc, hx, hy, 80, '#fff2a0', 110)
        snow_burst(cc, bx, 1700, t, e or 0, 16, 160, ai + 70, '#fff6c8', 0.6)
        # Krampus leans in from the right, raises brow, nods
        kin = ease_out_back(seg(t, T(16), T(16) + 0.3), 1.4)
        if kin > 0:
            nod = 10 * (bump(t, T(16, 4), 0.25) + bump(t, T(16, 8), 0.2) + bump(t, T(16, 12), 0.2))
            happy = t >= T(16, 8)
            draw_krampus(cc, x=2600 - 640 * kin, y=1960, s=1.1, face=-1, lean=-10, head_tilt=nod - 6, chain=t,
                         brow=(5, 0.2), brow_l=(-15, 1.2) if not happy else (-10, 0.6), eyes='open', look=(-0.8, 0.4),
                         jaw=0.05 if not happy else 0.3, smile=1.0 if happy else 0.2, tongue=0, arm_l=(20, 30), arm_r=(60, 90) if happy else (25, 30))
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={2: scene})
    snow_front(c, t)

# ==================================================================  ACT 2 : YULE CAT
def aurora(cc, t, a=1.0, w=2600):
    for k, (colr, yo, amp) in enumerate((('#3cffb0', 380, 70), ('#7affd8', 470, 50), ('#b07aff', 300, 60))):
        pth = skia.Path(); pts = []
        for i in range(0, w + 80, 80):
            pts.append((i, yo + math.sin(i * 0.004 + k + t * 0.5) * amp + math.sin(i * 0.011 + t * 0.8) * amp * 0.5))
        pth.moveTo(*pts[0])
        for q in pts[1:]: pth.lineTo(*q)
        cc.drawPath(pth, P(colr, int(90 * a), stroke=150, blur=50))
        cc.drawPath(pth, P(colr, int(80 * a), stroke=30, blur=14))

def s_y1(c, t):  # 30 - 33.75 establishing -> interior celebration
    lt = t - T(17)
    if t < T(18):
        st = stage('iceland')
        u = ease_in_out(seg(t, T(17), T(18)))
        cam = (1100, lerp(700, 1150, u), lerp(1.0, 1.25, u))
        def people(cc):
            for k, v in enumerate((ice_w, ice_k, ice_m)):
                v.draw(cc, x=800 + k * 260, y=1700 + (k % 2) * 30, s=1.0, bob=bob(t, 8), arm_l=(140, 20) if (int(t / BEAT) + k) % 2 else (40, 40),
                       arm_r=(140, 20) if (int(t / BEAT) + k) % 2 == 0 else (40, 40), mouth='grin', mouth_open=0.4, eyes='happy', cheeks=1)
        draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={0: lambda cc: aurora(cc, t), 2: people})
        snow_front(c, t)
        return
    st = stage('iceland_int')
    cam = (750, 1050, 1.08 * punch(t, T(18), 0.06))
    items_t = [T(18, 4), T(18, 8), T(18, 12)]
    def people(cc):
        e = last_ev(t, items_t)
        # three villagers unwrap new clothes on consecutive beats
        for k, (v, colr) in enumerate(((ice_w, '#d23c3c'), (ice_k, '#f2c14e'), (ice_m, '#3f7fbf'))):
            got = t >= items_t[k]
            x = 380 + k * 330
            v.draw(cc, x=x, y=1750 + (k == 1) * 40, s=1.25 * (1 + 0.08 * decay(t, items_t[k], 0.12)), bob=hop(t, [items_t[k]], 50) + bob(t, 4),
                   arm_l=(150, 20) if got else (60, 60), arm_r=(150, 20) if got else (60, 60), mouth='grin' if got else 'o', mouth_open=0.6,
                   eyes='happy' if got else 'open', cheeks=1, look=(0, -0.5))
            if got:
                for j in range(3): sparkle(cc, x - 80 + j * 80, 1750 - 1.25 * 360 - 40 * j, 22 * pop(t, items_t[k]), 230)
            else:
                present(cc, x, 1760, 110, 80, colr, '#ffffff', lid=0)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={0: people})
    fire_glow(c, 0.25)
    snow_front(c, t, 0.0)

def fire_glow(c, a=0.3, x=W * 0.5, y=H * 0.6, colr='#ff9a3a'):
    c.drawRect(skia.Rect.MakeWH(W, H), PS(rad((x, y), H * 0.8, [(colr, int(255 * a * 0.4)), (colr, 0)]), blend=skia.BlendMode.kScreen))

def s_y2(c, t):  # 33.75 - 37.5 Jon opens empty present, shrugs, walks out
    st = stage('iceland_int')
    cam = (650, 1250, 1.35)
    lid_t = T(19); peek_t = T(19, 4); flip_t = T(19, 8); shrug_t = T(20); walk_t = T(20, 4)
    def scene(cc):
        walking = t >= walk_t
        wx = 650 - (900 * seg(t, walk_t, T(20, 14))) if walking else 650
        shrug = shrug_t <= t < walk_t
        if t < flip_t:
            pose = dict(arm_l=(70, 70), arm_r=(70, 70), look=(0, 0.8), mouth='smile' if t < peek_t else 'o', eyes='open' if t < peek_t else 'wide', head_tilt=8)
        elif not shrug and not walking:
            pose = dict(arm_l=(150, 30), arm_r=(150, 30), look=(0, -0.6), mouth='flat', eyes='open', brows=(-15, 0.4))
        elif shrug:
            sh = bump(t, shrug_t, 0.45)
            pose = dict(arm_l=(80 + 30 * sh, 100), arm_r=(80 + 30 * sh, 100), mouth='wavy', eyes='open', brows=(-20, 0.6 + sh * 0.5), look=(0, -0.2), head_tilt=10 * sh)
        else:
            pose = dict(walk_pose(t * 2.13), mouth='flat', eyes='open', look=(-1, 0))
        jon.draw(cc, x=wx, y=1800, s=1.5, face=-1 if walking else 1, **pose)
        if not walking:
            lid = ease_out_back(seg(t, lid_t, lid_t + 0.2)) * (1 if t < flip_t else 0)
            flipped = t >= flip_t
            if not flipped:
                present(cc, 650, 1880, 160, 120, '#3a7bd5', '#ffffff', lid=lid)
            else:
                # box held upside down, moth flutters out
                u = t - flip_t
                cc.save(); cc.translate(650, 1620); cc.rotate(180 * ease_out(seg(t, flip_t, flip_t + 0.15)))
                present(cc, 0, 60, 160, 120, '#3a7bd5', '#ffffff', lid=0.0); cc.restore()
                if u < 2.0:
                    mx = 650 + 200 * u + 30 * math.sin(u * 20); my = 1640 - 180 * u + 20 * math.sin(u * 13)
                    wing = abs(math.sin(u * 40))
                    for sx in (-1, 1): cc.drawOval(skia.Rect.MakeLTRB(mx + sx * 2, my - 10 * wing, mx + sx * 26, my + 10 * wing), P('#a89a7a'))
                    cc.drawOval(skia.Rect.MakeLTRB(mx - 4, my - 9, mx + 4, my + 9), P(INK))

        # family in the background holding their new clothes, smiling
        ice_w.draw(cc, x=1150, y=1700, s=0.95, mouth='smile', eyes='happy', arm_l=(140, 30), arm_r=(140, 30), bob=bob(t, 5))
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={0: scene})
    # glowing eyes appear in the window on the cat-glide accent
    ey = ease_out(seg(t, T(20, 12), T(20, 13)))
    if ey > 0:
        c.save(); cam_apply(c, cam, 1.0)
        for sx in (-1, 1):
            glow(c, 750 + sx * 40, 640, 60, '#ffcf3a', int(220 * ey))
            c.drawOval(skia.Rect.MakeLTRB(750 + sx * 40 - 22, 640 - 12 * ey, 750 + sx * 40 + 22, 640 + 12 * ey), P('#ffd23a'))
            c.drawOval(skia.Rect.MakeLTRB(750 + sx * 40 - 4, 640 - 11 * ey, 750 + sx * 40 + 4, 640 + 11 * ey), P('#100808'))
        c.restore()
    fire_glow(c, 0.25)

def s_y3(c, t):  # 37.5 - 41.25 GIANT CAT REVEAL
    st = stage('iceland'); lt = t - T(21)
    tilt = ease_in_out(seg(t, T(21) + 0.1, T(22) + 0.4))
    cam = (1100, lerp(1350, 950, tilt), lerp(1.35, 0.92, tilt) * punch(t, T(21), 0.08) * punch(t, T(22), 0.04))
    def catlayer(cc):
        aurora(cc, t, 1.0)
        eyes = ease_out(seg(t, T(21) - 0.02, T(21) + 0.18))
        cxw, cyw = to_layer(540, 1640, (1100, 950, 0.92), 0.3)
        draw_yule_cat(cc, x=cxw, y=cyw, s=1.05, eye_open=eyes, pupil=0.15 + 0.5 * ease_out(seg(t, T(22), T(22) + 0.3)),
                      ear=0.3 * bump(t, T(21, 4), 0.2) + 0.3 * bump(t, T(21, 12), 0.2) + 0.3 * bump(t, T(22, 4), 0.2),
                      tail=t * 0.4, look=(0.0, 0.6), glow=1.3, head_tilt=4 * math.sin(t * 2))
    def people(cc):
        wp = walk_pose(t * 2.13)
        jon.draw(cc, x=900 + lt * 30, y=1800, s=0.8, **wp, mouth='flat', eyes='open', look=(1, 0))
    draw_stage(c, st, cam, t, kick_pulse(t) * 0.5, beat=beat_no(t), between={1: catlayer, 2: people})
    snow_front(c, t)
    flash(c, t, T(21), 0.18, '#fff6c0', 0.5)

def s_y4(c, t):  # 41.25 - 45 cat notices clothes; Jon runs
    lt = t - T(23)
    if t < T(23, 4):  # extreme close-up of cat eyes narrowing
        c.drawRect(skia.Rect.MakeWH(W, H), P('#05060c'))
        c.save(); c.translate(W / 2, H * 0.5); c.scale(2.4, 2.4)
        draw_cat_head(c, dict(eye_open=1, narrow=ease_in_out(seg(t, T(23), T(23, 3))), pupil=0.1, look=(0, 0.9), ear=0, mouth=0, tongue=0, nose=0,
                              glow=1.4, rim='#7f9cff', confused=0, blink=0), 255)
        c.restore(); return
    st = stage('iceland')
    run = t >= T(24)
    cam = (1100, 1250, 1.3 * punch(t, T(23, 8), 0.06))
    def catlayer(cc):
        aurora(cc, t, 0.8)
        lick = bump(t, T(24, 12), 0.45)
        cxw, cyw = to_layer(640, 1720, cam, 0.3)
        draw_yule_cat(cc, x=cxw, y=cyw, s=1.1, eye_open=1, narrow=0.5, pupil=0.12, look=(0.0, 0.8), tail=t * 0.6, mouth=0.3 * lick, tongue=lick,
                      head_tilt=-6, glow=1.2)
    def people(cc):
        if t < T(23, 8):
            pose = dict(look=(0, 1), head_tilt=12, arm_l=(40, 80), arm_r=(40, 80), mouth='flat', eyes='open')
        elif not run:
            pose = dict(look=(0, -1), eyes='wide', mouth='o', mouth_open=1, sweat=seg(t, T(23, 8), T(23, 12)), brows=(25, 1), arm_l=(120, 40), arm_r=(120, 40),
                        hair_up=0.4 * seg(t, T(23, 12), T(24)))
        else:
            pose = dict(run_pose(t * 4.27), eyes='wide', mouth='scream', mouth_open=1, sweat=1, hair_up=0.8)
        x = 900 - (700 * ease_in(seg(t, T(24), T(25)))) if run else 900
        jon.draw(cc, x=x, y=1880, s=1.4, face=-1 if run else 1, **pose)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={1: catlayer, 2: people})
    snow_front(c, t)

ITEM_T = [T(25, 0), T(25, 4), T(25, 8), T(25, 12), T(26, 0), T(26, 4), T(26, 8), T(26, 12)]
def bundled_jon(cc, x, y, s, level, t, pose=None, fall=0.0):
    """Jon wearing `level` extra items (0..8), level 8 = giant ball of clothes"""
    pose = pose or {}
    cc.save(); cc.translate(x - 150 * fall, y); cc.rotate(-70 * fall); cc.translate(-x, -y)
    lvl = level
    bulk = min(lvl, 7) * 0.12
    j = Human('adult', hat='beanie' if lvl >= 4 else 'none', hat_col='#d23c3c', pom='#ffffff', hair='#c48a3a',
              sweater=('#7d8b6a', '#d23c3c', '#2f8f4e', '#2f8f4e', '#2f8f4e', '#2f8f4e', '#2f8f4e', '#2f8f4e', '#2f8f4e')[lvl],
              patches=lvl == 0, coat='#7d8b6a' if lvl == 0 else ('#d23c3c' if lvl == 1 else '#2f8f4e'),
              scarf='#f2c14e' if lvl >= 3 else None, beard='#c48a3a', pants='#4b4a5a', mitt='#d23c3c' if lvl >= 2 else '#e0b090', bulk=bulk, seed=21)
    if lvl < 7:
        j.draw(cc, x=x, y=y, s=s, **pose)
        # extra scarves
        if lvl >= 5:
            for k in range(2 + (lvl - 5)):
                yy = y - s * (104 + 128 + 10) + k * 18 * s
                cc.drawPath(rrect(x - s * (70 + k * 6), yy - 12 * s, s * (140 + k * 12), 26 * s, 12 * s), P(INK))
                cc.drawPath(rrect(x - s * (66 + k * 6), yy - 9 * s, s * (132 + k * 12), 20 * s, 10 * s), P(('#d62f3a', '#3a7bd5', '#e86fa8')[k % 3]))
        if lvl >= 6:  # thick socks
            for sx in (-1, 1):
                cc.drawPath(rrect(x + sx * 25 * s - 22 * s, y - 60 * s, 44 * s, 56 * s, 14 * s), P(INK))
                cc.drawPath(rrect(x + sx * 25 * s - 19 * s, y - 57 * s, 38 * s, 50 * s, 12 * s), P('#f4f1ea'))
                for k in range(3): cc.drawLine(x + sx * 25 * s - 18 * s, y - (50 - k * 14) * s, x + sx * 25 * s + 18 * s, y - (50 - k * 14) * s, P('#d62f3a', 255, stroke=5 * s))
    else:
        # giant puffer-coat ball, only face and boots visible
        R = s * (170 if lvl == 7 else 205)
        cy = y - R * 0.92
        for sx in (-1, 1):
            cc.drawPath(rrect(x + sx * R * 0.35 - 40 * s, y - 40 * s, 80 * s, 46 * s, 18 * s), P(INK))
            cc.drawPath(rrect(x + sx * R * 0.35 - 36 * s, y - 36 * s, 72 * s, 38 * s, 16 * s), P('#f4f1ea'))
        ball = blob(x, cy, R, R * 0.95, 14, 0.04, 5)
        shaded(cc, ball, '#c8283a', (-0.5, -0.9), 0.25, INK, 6, 255)
        cc.save(); cc.clipPath(ball, doAntiAlias=True)
        for k in range(6):  # puffer quilting
            yy = cy - R + k * R * 0.36
            pth = skia.Path(); pth.moveTo(x - R, yy); pth.quadTo(x, yy + R * 0.18, x + R, yy)
            cc.drawPath(pth, P('#8a1525', 255, stroke=6 * s))
        cc.restore()
        # scarf pile + hat + face peeking
        fy = cy - R * 0.45
        cc.drawPath(rrect(x - R * 0.55, fy + 40 * s, R * 1.1, 60 * s, 28 * s), P(INK)); cc.drawPath(rrect(x - R * 0.52, fy + 44 * s, R * 1.04, 52 * s, 24 * s), P('#f2c14e'))
        cc.drawPath(ellipse(x, fy, 64 * s, 56 * s), P(INK)); cc.drawPath(ellipse(x, fy, 60 * s, 52 * s), P('#f2c29b'))
        for sx in (-1, 1):
            if pose.get('eyes') == 'closed':
                cc.drawLine(x + sx * 22 * s - 9 * s, fy - 4 * s, x + sx * 22 * s + 9 * s, fy - 4 * s, P(INK, 255, stroke=5 * s))
            else:
                cc.drawCircle(x + sx * 22 * s, fy - 6 * s, 11 * s, P('#ffffff')); cc.drawCircle(x + sx * 22 * s, fy - 4 * s, 6 * s, P(INK))
        cc.drawPath(path_from([(x - 60 * s, fy - 30 * s), (x, fy - 110 * s), (x + 60 * s, fy - 30 * s)], True, 0.8), P('#2f8f4e'))
        cc.drawCircle(x, fy - 112 * s, 18 * s, P('#ffffff'))
    cc.restore()

def s_y5(c, t):  # 45 - 48.75 clothing transformation on every beat
    st = stage('iceland')
    e = last_ev(t, ITEM_T); lvl = 0 if e is None else ITEM_T.index(e) + 1
    lvl = min(lvl, 8)
    cam = (1100, 1250, 1.45 * punch(t, e or -9, 0.035))
    def catlayer(cc):
        aurora(cc, t, 0.8)
        cxw, cyw = to_layer(560, 1700, cam, 0.3)
        draw_yule_cat(cc, x=cxw, y=cyw, s=1.1, eye_open=1, narrow=0.4, pupil=0.15, look=(0.0, 0.8), tail=t * 0.6, head_tilt=-4 + 6 * math.sin(t * 4), glow=1.1)
    def people(cc):
        sq = 1 + 0.25 * decay(t, e or -9, 0.07)
        bundled_jon(cc, 1100, 1930, 1.45, lvl, t, dict(sq=1 / sq, eyes='wide' if lvl < 4 else 'open', mouth='grin', mouth_open=0.3,
                                                       arm_l=(110, 20), arm_r=(110, 20), cheeks=1, look=(0, -0.4)))
        if e is not None:
            snow_burst(cc, 1100, 1600, t, e, 30, 300, lvl + 100, size=0.9)
            for k in range(4): sparkle(cc, 1100 + 260 * math.cos(k * 1.6 + lvl), 1500 + 200 * math.sin(k * 1.6 + lvl), 26 * bump(t, e, 0.35), 230)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={1: catlayer, 2: people})
    snow_front(c, t)

def s_y6(c, t):  # 48.75 - 52.5 the cat sniffs, loses interest, leaves; Jon falls over in the gap
    st = stage('iceland')
    cam = (1100, 1200, 1.0)
    leave = ease_in_out(seg(t, T(28, 0), T(28, 9)))
    gap = T(28, 10)
    def catlayer(cc):
        aurora(cc, t, 0.8)
    def people(cc):
        fall = ease_out_back(seg(t, gap, gap + 0.25), 1.3) if t >= gap else 0
        bundled_jon(cc, 830, 1900, 1.25, 8, t, dict(eyes='closed' if t < T(27, 12) else 'open'), fall=fall)
        if t >= gap: snow_burst(cc, 650, 1820, t, gap, 50, 420, 5, size=1.3)
        # cat head comes down to sniff
        down = ease_in_out(seg(t, T(27), T(27, 4))) * (1 - leave)
        sniff = 0.5 + 0.5 * math.sin(t * 2 * math.pi / STEP / 2) if T(27, 4) <= t < T(27, 12) else 0
        conf = ease_out(seg(t, T(27, 12), T(28)))
        hx = 1330 + 600 * leave; hy = lerp(300, 1180, down) - 500 * leave
        cc.save(); cc.translate(hx, hy); cc.scale(0.95, 0.95); cc.rotate(-14 - 8 * conf + 20 * leave)
        draw_cat_head(cc, dict(eye_open=1 - 0.5 * conf * (1 - leave), narrow=0.1, pupil=0.4 - 0.25 * conf, look=(-0.8 + conf * 1.4, 0.6 - conf * 1.2), ear=-0.3 * conf, mouth=0,
                               tongue=0, nose=sniff, glow=1.0, rim='#7f9cff', confused=conf * (1 - leave), blink=0), 255)
        cc.restore()
        if conf > 0 and leave < 0.6:
            draw_text(cc, '?', hx + 330, hy - 260, 180 * pop(t, T(27, 12)), 'luckiest-guy-400.ttf', '#ffe680', INK, 10, int(255 * (1 - leave)))
        # tail of the departing cat sweeping behind houses
        if leave > 0:
            draw_tail(cc, (1600 + 700 * leave, 1500), t * 0.8, 900, 110, 255)
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={1: catlayer, 2: people})
    snow_front(c, t)

# ==================================================================  ACT 3 : MARI LWYD
def fire(c, x, y, t, s=1.0, a=255):
    r = random.Random(3)
    glow(c, x, y - 60 * s, 300 * s, '#ff8a2a', int(a * 0.7))
    for layer, (colr, sc) in enumerate((('#ff5a1f', 1.0), ('#ffa02a', 0.72), ('#fff0a0', 0.42))):
        for k in range(5):
            ph = t * (6 + k) + k * 1.7
            fx = x + (k - 2) * 38 * s * sc
            h = (150 + 40 * math.sin(ph) + 30 * math.sin(ph * 1.7)) * s * sc
            w_ = 46 * s * sc
            fp = path_from([(fx - w_, y), (fx - w_ * 0.6, y - h * 0.5), (fx + 10 * math.sin(ph * 2) * s, y - h), (fx + w_ * 0.6, y - h * 0.45), (fx + w_, y)], True, 0.8)
            c.drawPath(fp, P(colr, int(a * 0.9)))
    for k in range(3):
        c.drawPath(rrect(x - 120 * s + k * 70 * s, y - 10 * s, 110 * s, 30 * s, 12 * s), P('#4a2a18', a))

def welsh_room(c, t, cam, door_open=0.0, knock=0.0, between_fn=None):
    st = stage('welsh_int')
    def inside(cc):
        fire(cc, 820, 1440, t, 1.0)
        # door on right wall
        dx, dy, dw, dh = 1170, 840, 260, 640
        sh = math.sin(t * 90) * 6 * knock
        cc.drawPath(rrect(dx, dy, dw, dh, 10), P('#05060f'))
        if door_open > 0:
            # night outside visible
            cc.save(); cc.clipPath(rrect(dx, dy, dw, dh, 10)); cc.drawRect(skia.Rect.MakeXYWH(dx, dy, dw, dh), PS(lin((0, dy), (0, dy + dh), ['#0b1440', '#3a4a8a'])))
            cc.restore()
        cc.save(); cc.translate(dx + sh, dy); cc.scale(max(0.05, 1 - door_open), 1)
        door = rrect(0, 0, dw, dh, 10)
        cc.drawPath(door, P(INK, 255, stroke=10)); cc.drawPath(door, PS(lin((0, 0), (dw, 0), ['#7a4a2e', '#5a321e', '#3a2014'])))
        for k in range(4): cc.drawLine(dw * (k + 1) / 5, 10, dw * (k + 1) / 5, dh - 10, P('#2a160c', 255, stroke=4))
        cc.drawRect(skia.Rect.MakeLTRB(0, dh * 0.2, dw, dh * 0.24), P('#2a1a10')); cc.drawRect(skia.Rect.MakeLTRB(0, dh * 0.72, dw, dh * 0.76), P('#2a1a10'))
        cc.drawCircle(30, dh * 0.5, 12, P('#e8c050'))
        # wreath
        cc.drawCircle(dw / 2, dh * 0.4, 50, P(INK, 255, stroke=30)); cc.drawCircle(dw / 2, dh * 0.4, 50, P('#2f7d46', 255, stroke=22))
        cc.drawPath(path_from([(dw / 2 - 16, dh * 0.4 + 46), (dw / 2 + 16, dh * 0.4 + 46), (dw / 2, dh * 0.4 + 80)], True), P('#d62f3a'))
        cc.restore()
        if between_fn: between_fn(cc)
    draw_stage(c, st, cam, t, 0, between={0: inside})
    # warm firelight
    c.drawRect(skia.Rect.MakeWH(W, H), PS(rad((W * 0.55, H * 0.72), H * 0.7, [('#ff9a3a', int(70 + 15 * math.sin(t * 9))), ('#ff9a3a', 0)]), blend=skia.BlendMode.kScreen))
    # snow outside the window
    c.save(); cam_apply(c, cam, 1.0); c.clipRect(skia.Rect.MakeXYWH(120, 520, 360, 420)); c.translate(120, 520); c.scale(0.35, 0.25)
    SNOW2.draw(c, t, 0.2, 1.0); c.restore()

def s_w1(c, t):  # 52.5 - 56.25 cosy cottage
    cam = (760, 1150, 1.15 + 0.05 * seg(t, T(29), T(31)))
    def scene(cc):
        armchair(cc, 520, 1700)
        sip = [T(29, 8), T(30, 8)]
        sp = bump(t, sip[0], 0.6) + bump(t, sip[1], 0.6)
        dai.draw(cc, x=520, y=1720, s=1.35, mouth='smile' if sp < 0.3 else 'o', mouth_open=0.2, eyes='happy' if sp > 0.3 else 'open', cheeks=1,
                 arm_r=(60 + 60 * sp, 110 - 20 * sp), arm_l=(30, 60), leg_l=(70, 70), leg_r=(70, 70), bob=-10 + bob(t, 3), look=(0.4, 0),
                 items={'r': it_mug}, head_tilt=-10 * sp)
        # steam from mug
        for k in range(3):
            ph = (t * 0.6 + k / 3) % 1
            glow(cc, 650 + math.sin(ph * 6 + k) * 12, 1260 - ph * 160, 30 + ph * 20, '#ffffff', int(90 * (1 - ph)))
        cat_sleep(cc, 860, 1560, t)
    welsh_room(c, t, cam, 0, 0, scene)

def armchair(cc, x, y):
    ch = path_from([(x - 170, y + 20), (x - 180, y - 300), (x - 120, y - 380), (x + 120, y - 380), (x + 180, y - 300), (x + 170, y + 20)], True, 0.5)
    shaded(cc, ch, '#7a2f3a', (-0.5, -1), 0.2, INK, 6)
    for sx in (-1, 1):
        arm = rrect(x + sx * 150 - 45, y - 210, 90, 230, 40); shaded(cc, arm, '#8a3a44', (-0.5, -1), 0.2, INK, 6)

def cat_sleep(cc, x, y, t):
    """small house cat sleeping by the fire (a cute callback)"""
    b = blob(x, y, 60, 34, 10, 0.02, 1); cc.drawPath(b, P(INK, 255, stroke=8)); cc.drawPath(b, P('#e08a3a'))
    cc.drawCircle(x - 50, y - 16, 26, P(INK)); cc.drawCircle(x - 50, y - 16, 23, P('#e08a3a'))
    for sx in (-1, 1): cc.drawPath(path_from([(x - 50 + sx * 6, y - 34), (x - 50 + sx * 22, y - 52), (x - 50 + sx * 24, y - 26)], True), P('#e08a3a'))
    zz = (t * 0.7) % 1
    draw_text(cc, 'z', x - 10 + zz * 30, y - 60 - zz * 60, 40, 'fredoka-600.ttf', '#ffffff', INK, 4, int(255 * (1 - zz)), shadow=False)

def s_w2(c, t):  # 56.25 - 60 knocks; walks to door
    knocks = [T(31, 4), T(31, 12), T(32, 4)]
    kn = max([decay(t, k_, 0.12) for k_ in knocks] + [0])
    walk = t >= T(32, 4)
    cam = (900 + 200 * ease_in_out(seg(t, T(32, 4), T(33))), 1150, 1.15 * punch(t, last_ev(t, knocks) or -9, 0.03))
    def scene(cc):
        armchair(cc, 520, 1700)
        startle = max([bump(t, k_, 0.3) for k_ in knocks] + [0])
        if not walk:
            dai.draw(cc, x=520, y=1720 - 60 * startle, s=1.35, mouth='o', mouth_open=0.6, eyes='wide' if startle > 0.2 else 'open', look=(1, -0.2),
                     arm_r=(80, 90), arm_l=(40, 60), leg_l=(70, 70), leg_r=(70, 70), items={'r': it_mug}, brows=(-10, 0.5), sweat=0.5 * startle)
        else:
            steps = [T(32, 4), T(32, 8), T(32, 12), T(33) - 0.01]
            u = seg(t, T(32, 4), T(33))
            wp = walk_pose((t - T(32, 4)) / BEAT * 0.5)
            dai.draw(cc, x=lerp(560, 1080, u), y=1760, s=1.35, **wp, mouth='flat', eyes='open', look=(1, 0), brows=(-12, 0.3))
        # knock dust & impact rings on the door
        for k_ in knocks:
            if k_ <= t < k_ + 0.4:
                u = (t - k_) / 0.4
                cc.drawCircle(1300, 1150, 60 + 140 * u, P('#ffe6b0', int(200 * (1 - u)), stroke=10))
                for j in range(6):
                    ang = j * 1.05; cc.drawCircle(1300 + math.cos(ang) * 160 * u, 1150 + math.sin(ang) * 160 * u, 8 * (1 - u), P('#d8c8a8', int(255 * (1 - u))))
        cat_sleep(cc, 860, 1560, t)
    welsh_room(c, t, cam, 0, kn, scene)

def s_w3(c, t):  # 60 - 63.75 door opens: MARI LWYD
    # POV through the open doorway: Mari Lwyd + wassail party lit by lanterns
    st = stage('welsh_ext')
    z = 1.35 * punch(t, T(33), 0.1)
    cam = (1000, 1080, z)
    jaw_t = [T(33, s) for s in (0, 2, 3, 4, 7, 8)] + [T(34, s) for s in (0, 1, 2, 4, 6, 8, 10, 12)] + [T(35, s) for s in (0, 2, 3, 4, 7, 8)]
    def scene(cc):
        for k, wv in enumerate(wass):
            x = 620 + k * 330 if k != 1 else 1400
            wv.draw(cc, x=x, y=1660, s=1.0, bob=bob(t, 8, k * 0.3), mouth='grin', mouth_open=0.4, eyes='happy', cheeks=1,
                    arm_r=(60, 60), arm_l=(130, 30), items={'r': it_lantern}, face=1 if k == 0 else -1)
        jw = max([bump(t, j_, 0.18) for j_ in jaw_t] + [0])
        draw_mari(cc, x=1000, y=1760, s=1.15, jaw=jw, sway=t * 0.6, ribbon=t * 0.8, bells=t * 2, legs=t * 2.13, head_tilt=-6 + 8 * math.sin(t * 2.1))
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={1: scene})
    snow_front(c, t)
    # doorframe in the foreground (we are inside)
    door_a = ease_in_out(seg(t, T(33) - 0.1, T(33) + 0.3))
    fr = 150 * (1 - door_a) + 90
    c.drawRect(skia.Rect.MakeLTRB(0, 0, fr, H), P('#2a160c')); c.drawRect(skia.Rect.MakeLTRB(W - fr, 0, W, H), P('#2a160c'))
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 170), P('#2a160c'))
    # swinging door leaf
    if door_a < 1:
        c.drawRect(skia.Rect.MakeLTRB(fr, 170, fr + (W - 2 * fr) * (1 - door_a), H), PS(lin((0, 0), (W, 0), ['#7a4a2e', '#3a2014'])))
    # homeowner in the foreground, from behind (startled jump)
    jump = bump(t, T(33) + 0.15, 0.4)
    c.save(); c.translate(W * 0.78, H + 120 - 60 * jump)
    dai.draw(c, x=0, y=0, s=1.9, mouth='scream', mouth_open=1, eyes='wide', arm_l=(160, 10), arm_r=(160, 10), hair_up=0.6 * jump, sweat=1, face=-1,
             look=(-1, -0.5))
    c.restore()

def s_w4(c, t):  # 63.75 - 75: contest (bars 35-38), surrender & celebration (39-40)
    st = stage('welsh_ext')
    if t < T(37):  # bars 35-36 challenge
        cam = (1150, 1180, 1.1)
        verses = [(T(35, 0), 1), (T(35, 8), -1), (T(36, 0), 1), (T(36, 8), -1)]
    elif t < T(39):  # bars 37-38 escalating back-and-forth
        side = 1 if int((t - T(37)) / (BEAT if t < T(38) else STEP * 2)) % 2 == 0 else -1
        cam = (1150 - 150 * side, 1180, 1.15 + 0.12 * seg(t, T(37), T(39)))
        verses = [(T(37, s), 1 if (s // 4) % 2 == 0 else -1) for s in range(0, 16, 4)] + [(T(38, s), 1 if (s // 2) % 2 == 0 else -1) for s in range(0, 16, 2)]
    else:
        cam = (1150, 1180, 1.1)
        verses = []
    e = None
    for (vt, sd) in verses:
        if vt <= t: e = (vt, sd)
    def scene(cc):
        surrender = t >= T(39)
        # wassail party + Mari on the left
        for k, wv in enumerate(wass):
            wv.draw(cc, x=640 + k * 150, y=1760 + (k % 2) * 40, s=0.95, bob=bob(t, 10 if surrender else 6, k * 0.3), mouth='grin', mouth_open=0.5,
                    eyes='happy', cheeks=1, arm_r=(150 if (e and e[1] == 1) or surrender else 60, 20), arm_l=(60, 60), items={'l': it_lantern})
        mj = 0
        if e and e[1] == 1: mj = bump(t, e[0], 0.22)
        if surrender: mj = 0.6 + 0.4 * math.sin(t * 13.4)
        draw_mari(cc, x=1000, y=1830, s=1.05, jaw=mj, sway=t * 0.8, ribbon=t, bells=t * 2, legs=t * 2.13 if surrender else 0,
                  head_tilt=(-12 * mj if e and e[1] == 1 else 6 * math.sin(t * 3)), head_up=0.4 * mj)
        # Dai in the doorway on the right
        cc.drawPath(rrect(1380, 1180, 230, 450, 8), P('#ffcf6e')); glow(cc, 1495, 1400, 280, '#ffb347', 120)
        my_turn = e and e[1] == -1
        if not surrender:
            esc = seg(t, T(37), T(39))
            dai.draw(cc, x=1495, y=1640, s=1.0 * (1 + 0.06 * (bump(t, e[0], 0.2) if my_turn else 0)), face=-1,
                     mouth='grin' if my_turn else 'o', mouth_open=0.6, eyes='open' if my_turn else 'wide', brows=(-15 if my_turn else 15, 0.4),
                     arm_l=(140 if my_turn else 40, 40), arm_r=(60, 90), sweat=esc, look=(-1, 0), head_tilt=8 if my_turn else -5)
        else:
            give = ease_out_back(seg(t, T(39), T(39) + 0.3))
            dai.draw(cc, x=1495 - 140 * seg(t, T(39, 4), T(39, 12)), y=1640, s=1.0, face=-1, mouth='grin', mouth_open=0.6, eyes='happy', cheeks=1,
                     arm_l=(150 * give, 10), arm_r=(150 * give, 10), bob=bob(t, 8))
        if e:
            if e[1] == 1: notes(cc, 1060, 1300, t, e[0], 1, 3, ('#ffe680', '#7affd8', '#ff9ad0')[int(e[0] * 7) % 3], int(e[0] * 10))
            else: notes(cc, 1420, 1300, t, e[0], -1, 3, '#ffd27a', int(e[0] * 10))
        # verse scroll bubbles (no words: musical + rhyme glyphs)
        if e and not surrender:
            bx = 1100 if e[1] == 1 else 1300; a = int(255 * bump(t, e[0], 0.45))
            bw = 300
            cc.drawPath(rrect(bx - bw / 2, 1000, bw, 130, 50), P(INK, a, stroke=10)); cc.drawPath(rrect(bx - bw / 2, 1000, bw, 130, 50), P('#fff6e3', a))
            cc.drawPath(path_from([(bx - 20 * e[1], 1125), (bx - 70 * e[1], 1190), (bx + 20 * e[1], 1125)], True), P('#fff6e3', a))
            draw_text(cc, '♪ ~ ♫ ~ ♪', bx, 1085, 58, 'fredoka-600.ttf', '#d62f3a', INK, 0, a, shadow=False) if False else None
            for j in range(3):
                nx = bx - 80 + j * 80
                cc.drawOval(skia.Rect.MakeLTRB(nx - 14, 1062, nx + 14, 1082), P(('#d62f3a', '#2f8f4e', '#3a7bd5')[j], a))
                cc.drawLine(nx + 12, 1072, nx + 12, 1022, P(INK, a, stroke=6))
    draw_stage(c, st, cam, t, kick_pulse(t), beat=beat_no(t), between={1: scene})
    snow_front(c, t)

def s_w5(c, t):  # 71.25 -> inside: everyone dances round the fire (bars 39 second half - 40)
    cam = (780, 1180, 1.12 * punch(t, T(40), 0.04))
    def scene(cc):
        dancers = [dai] + wass
        for k, d in enumerate(dancers):
            ang = (t / BAR) * math.pi + k * math.pi / 2
            x = 780 + math.cos(ang) * 420; y = 1780 + math.sin(ang) * 60
            d.draw(cc, x=x, y=y, s=1.05 + 0.1 * math.sin(ang), bob=bob(t, 14, k * 0.25), mouth='grin', mouth_open=0.6, eyes='happy', cheeks=1,
                   arm_l=(150, 20) if (int(t / BEAT) + k) % 2 else (90, 40), arm_r=(150, 20) if (int(t / BEAT) + k) % 2 == 0 else (90, 40),
                   leg_l=(20 * math.sin(t * 13.4 + k), 20), leg_r=(-20 * math.sin(t * 13.4 + k), 20), face=1 if math.sin(ang) > 0 else -1)
        draw_mari(cc, x=1180, y=1800, s=0.9, jaw=0.5 + 0.5 * math.sin(t * 13.4), sway=t, ribbon=t, bells=t * 3, legs=t * 2.13, head_tilt=10 * math.sin(t * 6.7))
        cat_sleep(cc, 860, 1560, t) if False else None
    welsh_room(c, t, cam, 0, 0, scene)

# ==================================================================  TRANSITION FX
def wreath(c, cx, cy, R, rot, a=255):
    c.save(); c.translate(cx, cy); c.rotate(rot)
    c.drawCircle(0, 0, R, P(INK, a, stroke=R * 0.42))
    c.drawCircle(0, 0, R, P('#1f6b3c', a, stroke=R * 0.36))
    r = random.Random(4)
    for k in range(48):
        ang = k * math.pi / 24; rr = R + r.uniform(-R * 0.15, R * 0.15)
        x, y = math.cos(ang) * rr, math.sin(ang) * rr
        c.drawPath(path_from([(x - R * 0.08, y), (x, y - R * 0.05), (x + R * 0.08, y), (x, y + R * 0.05)], True, 0.6), P(('#2f8f4e', '#185a30')[k % 2], a))
    for k in range(16):
        ang = k * math.pi / 8 + 0.2; x, y = math.cos(ang) * R * 1.05, math.sin(ang) * R * 1.05
        c.drawCircle(x, y, R * 0.045, P('#d62f3a', a)); c.drawCircle(x - R * 0.012, y - R * 0.012, R * 0.012, P('#ffffff', a))
    for k in range(8):
        ang = k * math.pi / 4; x, y = math.cos(ang) * R * 0.9, math.sin(ang) * R * 0.9
        glow(c, x, y, R * 0.12, ('#ffd84a', '#ff4a4a', '#4ac8ff')[k % 3], int(a * 0.8))
    # bow
    bw = path_from([(0, R * 0.95), (-R * 0.35, R * 0.75), (-R * 0.35, R * 1.2), (0, R * 1.02), (R * 0.35, R * 1.2), (R * 0.35, R * 0.75)], True, 0.6)
    c.drawPath(bw, P(INK, a, stroke=8)); c.drawPath(bw, P('#d62f3a', a))
    c.restore()

# ==================================================================  ACT 4 : FINALE
def finale_cast(cc, t, mode='dance', turn=0.0):
    """Krampus left, Mari centre-back, cat behind roofs right, villagers around"""
    stab = [T(48, 0), T(48, 3), T(48, 6), T(48, 12)]
    beat_i = int(t / BEAT)
    # villagers dancing in the back row
    for k, v in enumerate(VILL):
        x = 260 + k * 260
        v.draw(cc, x=x, y=1600, s=0.85, bob=bob(t, 14, k * 0.2), mouth='grin', mouth_open=0.6, eyes='happy', cheeks=1,
               arm_l=(150, 20) if (beat_i + k) % 2 else (60, 60), arm_r=(150, 20) if (beat_i + k) % 2 == 0 else (60, 60),
               leg_l=(15 * math.sin(t * 13.4 + k), 20), leg_r=(-15 * math.sin(t * 13.4 + k), 20))

def s_f(c, t):  # 75 - 90 FINALE
    st = stage('square')
    arrive_k = T(41, 4); arrive_m = T(41, 8); arrive_c = T(41, 12); pose_t = T(42)
    turn_t = T(47)
    if t < T(43):
        cam = (900, lerp(1000, 1180, ease_out(seg(t, T(41), T(42)))), lerp(0.88, 1.0, ease_out(seg(t, T(41), T(42)))) * punch(t, T(41), 0.08) * punch(t, pose_t, 0.05))
    elif t < T(45):  # dance: alternate wide / medium every bar
        bar_i = int((t - T(43)) / BAR)
        cam = [(900, 1200, 1.0), (750, 1350, 1.25)][bar_i % 2]
        cam = (cam[0] + 40 * math.sin(t), cam[1], cam[2] * punch(t, T(43 + bar_i), 0.04))
    elif t < T(47):  # spectacular payoff: orbit-ish moves
        u = (t - T(45)) / (2 * BAR)
        cam = (900 + 220 * math.sin(u * math.pi * 2), 1180 - 80 * u, 1.05 + 0.15 * math.sin(u * math.pi) * punch(t, T(46), 0.05))
    else:  # turn to camera, push in
        u = ease_in_out(seg(t, T(47), T(48)))
        hits = [T(48, 0), T(48, 3), T(48, 6), T(48, 12)]
        e = last_ev(t, hits)
        cam = (900, lerp(1180, 1300, u), lerp(1.05, 1.32, u) * punch(t, e or -9, 0.07 if e != T(48, 12) else 0.12))
    sx, sy = shake(t, T(48, 12), 18, 0.35)
    def catlayer(cc):
        # Yule cat behind the rooftops at right
        ca = ease_out_back(seg(t, arrive_c, arrive_c + 0.35), 1.4)
        if ca > 0:
            bounce = -abs(math.sin(t / BEAT * math.pi)) * 40 if t >= pose_t else 0
            facing = t >= turn_t
            cxw, cyw = to_layer(830, 1420, (900, 1180, 1.0), 0.3)
            draw_yule_cat(cc, x=cxw, y=cyw + (1 - ca) * 700 + bounce, s=0.72, eye_open=1, pupil=0.55 if not facing else 0.75, look=(0, 0.4) if not facing else (0, 0.2),
                          tail=t * (1.0 if t < pose_t else 2.13), head_tilt=(10 * math.sin(t / BEAT * math.pi)) if (pose_t <= t < turn_t) else 0, glow=1.0,
                          mouth=0.4 * bump(t, T(44, 12), 0.4) + (0.5 if t >= T(48, 12) else 0), tongue=0.6 * bump(t, T(44, 12), 0.4),
                          narrow=0.0, ear=0.4 * bump(t, T(44, 12), 0.4))
    def people(cc):
        cc.save(); cc.translate(sx, sy)
        finale_cast(cc, t)
        kx = lerp(-400, 640, ease_out_back(seg(t, arrive_k, arrive_k + 0.35), 1.3))
        mx_y = lerp(2400, 1900, ease_out_back(seg(t, arrive_m, arrive_m + 0.35), 1.3))
        dancing = pose_t <= t < turn_t
        facing = t >= turn_t
        hits = [T(48, 0), T(48, 3), T(48, 6), T(48, 12)]
        hi = sum(1 for h_ in hits if t >= h_)
        # Krampus footwork
        if t < pose_t:
            kp = dict(arm_l=(150, 10), arm_r=(150, 10), jaw=0.6, tongue=0.6, eyes='wide', brow=(10, 0.5))
        elif dancing:
            ph = t / STEP / 2
            kp = dict(arm_l=(120 + 40 * math.sin(t * 6.7), 40), arm_r=(120 - 40 * math.sin(t * 6.7), 40), jaw=0.3 + 0.3 * abs(math.sin(t * 6.7)), tongue=0.5,
                      leg_l=(35 * math.sin(ph * math.pi), 10), leg_r=(-35 * math.sin(ph * math.pi), 10), bob=bob(t, 22), lean=8 * math.sin(t * 3.35),
                      eyes='open', brow=(-5, 0.6), smile=1.0, look=(0.5 * math.sin(t * 3), 0))
        else:
            kp = dict(arm_l=(160 if hi >= 1 else 60, 20), arm_r=(160 if hi >= 4 else 80, 20), jaw=0.5 if hi >= 1 else 0.2, smile=1.0,
                      tongue=1.0 if hi >= 4 else 0.0, eyes='wide' if hi >= 1 else 'open', brow=(10, 0.6), look=(0, 0.3))
        draw_krampus(cc, x=kx, y=1960 + (kp.pop('bob', 0) if 'bob' in kp else 0), s=0.95 * (1 + 0.06 * decay(t, hits[0], 0.1) * (hi >= 1)), chain=t * 2, **kp)
        # Mari Lwyd centre
        mj = 0.5 + 0.5 * math.sin(t * 13.4) if dancing else (1.0 * bump(t, T(48, 3), 0.25) + (1.0 if hi >= 4 else 0))
        draw_mari(cc, x=1150, y=mx_y, s=0.92, jaw=clamp(mj), sway=t * (1.2 if dancing else 0.4), ribbon=t * 1.2, bells=t * 3, legs=t * 2.13 if dancing else 0,
                  head_tilt=(18 * math.sin(t / BEAT * math.pi) if dancing else -4), head_up=0.3 if facing else 0)
        # presents bouncing on the kicks during the payoff
        if T(45) <= t < T(48):
            for k in range(6):
                px = 160 + k * 160; ph = hop(t, KICKS, 90 + 30 * (k % 3), 0.4)
                present(cc, px, 2000 + ph, 80, 60, ('#d62f3a', '#2f8f4e', '#3a7bd5', '#f2c14e')[k % 4], '#ffffff', rot=10 * math.sin(t * 5 + k))
        for k_ in (arrive_k, arrive_m, arrive_c):
            snow_burst(cc, {arrive_k: 640, arrive_m: 1150, arrive_c: 1250}[k_], 1900, t, k_, 40, 380, int(k_ * 3), size=1.1)
        cc.restore()
    draw_stage(c, st, cam, t, kick_pulse(t) * 1.3, beat=beat_no(t) * 2, between={1: catlayer, 3: people})
    # fireworks / light bursts on bar downbeats during payoff
    for bt in (T(45), T(45, 8), T(46), T(46, 8), T(48, 12)):
        if bt <= t < bt + 1.0:
            u = (t - bt) / 1.0; r = random.Random(int(bt * 10))
            cx, cy = r.uniform(200, 880), r.uniform(250, 650)
            for k in range(22):
                ang = k * math.pi / 11; d = 260 * ease_out(u)
                colr = ('#ffd84a', '#ff4a6a', '#4affb0', '#7ac8ff')[k % 4]
                glow(c, cx + math.cos(ang) * d, cy + math.sin(ang) * d + 80 * u * u, 22 * (1 - u) + 4, colr, int(255 * (1 - u)))
    # spinning ornaments falling
    if T(45) <= t < T(48):
        r = random.Random(8)
        for k in range(10):
            x = r.uniform(80, 1000); y = ((t - T(45)) * r.uniform(300, 600) + r.uniform(-1200, 0)) % 2200 - 100
            c.save(); c.translate(x, y); c.rotate(t * 200 + k * 40)
            c.drawCircle(0, 0, 26, P(INK)); c.drawCircle(0, 0, 22, P(('#d62f3a', '#f2c14e', '#3a7bd5', '#2f8f4e')[k % 4]))
            c.drawRect(skia.Rect.MakeLTRB(-8, -34, 8, -22), P('#c0a040')); c.drawCircle(-7, -7, 6, P('#ffffff', 200))
            c.restore()
    snow_front(c, t, 1.0, 1.0)
    flash(c, t, T(41), 0.3, '#ffffff', 0.8)
    flash(c, t, T(48, 12), 0.35, '#fff6d0', 0.75)
    for h_ in (T(48, 0), T(48, 3), T(48, 6)):
        flash(c, t, h_, 0.12, '#ffffff', 0.35)
