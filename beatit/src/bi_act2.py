"""0:17.8-0:29.9  THE SECRET WEAPON: the phone rings at Eddie Van Halen's, the guitar is plugged in, the solo is cut,
strings become sound waves, meters jump - and later, Michael hears the playback (they are never shown in one room)."""
import math
import numpy as np
import skia
from bi_common import (W, H, DB, BEAT, HALF, paint, shader_paint, lin_grad, rad_grad, alpha, mix, glow, beam, clamp,
                       smoothstep, ease_io, ease_out, ease_in, font, text_center, noise1, poly_path, smooth_path, T, K,
                       base_pose, pose, draw, place_head, skel, bg, u_of, cap, particles, amp_stack, console,
                       tape_machine, reel, studio_room, mic_stand)

E_PHONE, E_TALK, E_JACK, E_PLAY, E_FING = DB(10), DB(11), DB(12), DB(13), DB(14)
E_SPKR = DB(14) + HALF
E_WAVE, E_DESK, E_LISTEN, END = DB(15), DB(15) + HALF, DB(16), DB(17)
L_HOME = dict(key=(-0.6, -0.75), amb='#ffc890', amb_a=0.2, rim='#ffe0b0', line='#24140e', floor_shadow=0.4)
L_RED = dict(key=(0.4, -0.9), amb='#ff7a5a', amb_a=0.25, rim='#ffd0a0', line='#1a0a0a', floor_shadow=0.45)
SKIN_E = '#ebc3a2'


def home_wall(c, t):
    """Eddie's place, 1982: wood panelling, a lamp, guitars hanging on the wall"""
    bg(c, ['#3a2216', '#2a180e', '#1a0e08'])
    for k in range(18):
        x = -30 + k * 64
        c.drawRect(skia.Rect.MakeXYWH(x, 0, 60, H), shader_paint(lin_grad((x, 0), (x + 60, 0), ['#6a4228', '#7e5232', '#5a361e'])))
        c.drawLine(x + 60, 0, x + 60, H, paint((0, 0, 0, 0.35), style='stroke', width=4))
    glow(c, W * 0.15, H * 0.25, 500, '#ffc070', 0.35)


def wall_guitar(c, x, y, s, ang, body='#c4141a', stripes=True):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-14, -520, 28, 440), paint('#c89a5a'))
    c.drawRect(skia.Rect.MakeXYWH(-24, -600, 48, 90), paint('#c89a5a'))
    g = smooth_path([(-28, -110), (-70, -190), (-100, -150), (-120, -60), (-175, 40), (-150, 160), (-40, 205), (90, 190),
                     (170, 110), (150, 10), (110, -60), (95, -140), (62, -150), (28, -110)], True, 0.45)
    c.drawPath(g, paint(body))
    if stripes:
        c.save()
        c.clipPath(g, doAntiAlias=True)
        for k, (o, a, cc) in enumerate(((-60, 30, '#f4f0ea'), (-20, -35, '#141214'), (30, 55, '#f4f0ea'), (60, -20, '#141214'))):
            c.save()
            c.translate(o, 20)
            c.rotate(a)
            c.drawRect(skia.Rect.MakeXYWH(-400, -10, 800, 20), paint(cc))
            c.restore()
        c.restore()
    c.drawPath(g, paint('#1a0a08', style='stroke', width=5))
    c.restore()


def phone(c, t):
    """the phone on the wall rings and rings - then a hand snatches the receiver"""
    u = u_of(t, E_PHONE, E_TALK)
    home_wall(c, t)
    wall_guitar(c, W * 0.8, H * 0.55, 1.0, 12)
    wall_guitar(c, W * 0.12, H * 0.7, 0.9, -8, body='#202024', stripes=False)
    c.save()
    s = 1.0 + 0.1 * ease_io(u)
    c.translate(W * 0.46, H * 0.5)
    c.scale(s, s)
    B = T.beat_at(t)
    ringing = t < E_PHONE + 1.05
    shake = 6 * math.sin(t * 90) if ringing and (B % 2) < 0.8 else 0
    # wall phone body
    c.drawRoundRect(skia.Rect.MakeXYWH(-50, -330, 340, 560), 40, 40, paint((0, 0, 0, 0.45), blur=24))
    c.drawRoundRect(skia.Rect.MakeXYWH(-60, -340, 340, 560), 40, 40, shader_paint(lin_grad((-60, 0), (280, 0), ['#efe2c4', '#d8c8a4', '#b8a680'])))
    c.drawRoundRect(skia.Rect.MakeXYWH(-200, -320, 120, 470), 30, 30, paint('#c8b890'))
    for i in range(4):
        for j in range(3):
            c.drawRoundRect(skia.Rect.MakeXYWH(10 + j * 80, -40 + i * 62, 60, 46), 10, 10, paint('#f6eedc'))
            text_center(c, '123456789*0#'[i * 3 + j], 40 + j * 80, -6 + i * 62, font('spartan_b', 28), paint('#4a3a2a'))
    lift = ease_out(smoothstep(E_PHONE + 1.05, E_PHONE + 1.45, t), 2)
    c.save()
    c.translate(shake, -lift * 900)
    c.rotate(-25 * lift)
    hs = smooth_path([(-150, -300), (-60, -330), (-40, -240), (-60, -110), (-50, 20), (-60, 100), (-150, 120), (-170, 30),
                      (-120, -110), (-170, -250)], True, 0.5)
    c.drawPath(hs, shader_paint(lin_grad((-170, 0), (-40, 0), ['#f4e8cc', '#d0bc94'])))
    c.drawPath(hs, paint('#5a4a32', style='stroke', width=4))
    if lift > 0.02:          # Eddie's hand round the receiver
        hand = smooth_path([(-30, -200), (40, -230), (90, -160), (80, -60), (20, -20), (-40, -60)], True, 0.5)
        c.drawPath(hand, paint(SKIN_E))
        c.drawPath(hand, paint('#3a2018', style='stroke', width=4))
        c.drawRect(skia.Rect.MakeXYWH(20, -240, 220, 200), paint('#ece8e0'))
    c.restore()
    # coiled cord
    cp = skia.Path()
    cp.moveTo(-110, 200)
    for k in range(30):
        cp.lineTo(-110 + 18 * math.sin(k * 1.4), 200 + k * 14 - lift * k * 20)
    c.drawPath(cp, paint('#d0bc94', style='stroke', width=8))
    c.restore()
    if ringing:                      # ring arcs on every other beat
        k = (B % 2)
        if k < 0.9:
            for j in range(3):
                r = 260 + j * 70 + 120 * k
                for sd in (-1, 1):
                    c.drawArc(skia.Rect.MakeXYWH(W * 0.46 - r, H * 0.42 - r, 2 * r, 2 * r), 90 - sd * 90 - 30, 60, False,
                              paint((1, 0.9, 0.6, 0.7 * (1 - k)), style='stroke', width=8))


def receiver(c, S, side=-1):
    """telephone handset at the ear (drawn over the head)"""
    hx, hy = S['head']
    r = S['hr']
    wx, wy = S['arms'][side][2]
    x = (wx + hx + side * r * 1.15) / 2
    c.save()
    c.translate(x, (wy + hy + r * 0.3) / 2)
    c.rotate(side * -14)
    p = smooth_path([(-r * 0.25, -r * 0.7), (r * 0.25, -r * 0.7), (r * 0.18, r * 0.2), (r * 0.3, r * 1.3), (-r * 0.3, r * 1.3),
                     (-r * 0.18, r * 0.2)], True, 0.5)
    c.drawPath(p, shader_paint(lin_grad((-r * 0.3, 0), (r * 0.3, 0), ['#f4e8cc', '#c8b48c'])))
    c.drawPath(p, paint('#5a4a32', style='stroke', width=r * 0.03))
    c.restore()


def talk(c, t):
    """Eddie on the phone: a slow, delighted grin"""
    u = u_of(t, E_TALK, E_JACK)
    home_wall(c, t)
    wall_guitar(c, W * 0.85, H * 0.6, 1.2, 10)
    wall_guitar(c, W * 0.1, H * 0.62, 1.1, -12, body='#e8e4dc', stripes=True)
    grin = smoothstep(0.25, 0.6, u)
    P = pose('eddie', [(0, 'nod_slow', dict(look=0.2))], t)
    P.update(lsh=1.2, lel=2.75, lhand='fist', rsh=0.2, rel=0.3, smile=0.3 + 0.7 * grin, mshape='grin' if grin > 0.4 else 'smile',
             mopen=0.35 * grin, brow=0.5 - 0.3 * grin, ey=-0.1)
    h = 2300 * (1 + 0.05 * ease_io(u))
    gx, gy = place_head('eddie', P, h, (W * 0.5, H * 0.42))
    S = draw(c, 'eddie', gx, gy, h, P, K.O_EDDIE, L_HOME, t, shadow=False)
    receiver(c, S, -1)
    hx, hy = S['head']
    cord = skia.Path()
    cord.moveTo(hx - S['hr'] * 1.2, hy + S['hr'] * 1.5)
    for k in range(18):
        cord.lineTo(hx - S['hr'] * 1.2 - k * 30 + 14 * math.sin(k * 1.7), hy + S['hr'] * 1.5 + k * 40)
    c.drawPath(cord, paint('#d0bc94', style='stroke', width=9))


def jack(c, t):
    """extreme close-up: the cable slides into the amp's input, the lamp glows, the volume goes all the way up"""
    u = u_of(t, E_JACK, E_PLAY)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c0a0a'))
    s = 1.0 + 0.15 * ease_io(u)
    c.save()
    c.translate(W / 2, H / 2)
    c.scale(s, s)
    c.rotate(-8)
    c.translate(-W / 2 - 760 * ease_io(smoothstep(0.42, 0.75, u)) + 240, -H / 2)
    panel = skia.Rect.MakeXYWH(-600, H * 0.3, W + 1600, H * 0.4)
    c.drawRect(panel, shader_paint(lin_grad((0, panel.top()), (0, panel.bottom()), ['#d8c8a0', '#c4b48a', '#9a8a68'])))
    c.drawRect(skia.Rect.MakeXYWH(-600, H * 0.3 - 140, W + 1600, 140), paint('#141214'))
    c.drawRect(skia.Rect.MakeXYWH(-600, H * 0.7, W + 1600, 300), paint('#141214'))
    labels = ['INPUT', 'PRESENCE', 'BASS', 'MIDDLE', 'TREBLE', 'VOLUME']
    on = smoothstep(E_JACK + 0.5, E_JACK + 0.6, t)
    turn = ease_io(smoothstep(E_JACK + 0.9, E_JACK + 1.55, t))
    for i, lab in enumerate(labels):
        x = 60 + i * 230
        text_center(c, lab, x, H * 0.39, font('spartan_b', 26), paint('#2a1e14'))
        if i == 0:
            c.drawCircle(x, H * 0.5, 54, paint('#9a9aa2'))
            c.drawCircle(x, H * 0.5, 30, paint('#141214'))
        else:
            ang = -135 + (270 if i == 5 else 170 + 20 * i) * (turn if i == 5 else 1)
            c.drawCircle(x + 4, H * 0.5 + 8, 66, paint((0, 0, 0, 0.4), blur=8))
            c.drawCircle(x, H * 0.5, 64, shader_paint(rad_grad((x - 20, H * 0.5 - 20), 80, ['#4a4448', '#141214'])))
            a = math.radians(ang - 90)
            c.drawLine(x, H * 0.5, x + math.cos(a) * 52, H * 0.5 + math.sin(a) * 52, paint('#f4eee0', style='stroke', width=8))
            for k in range(11):
                aa = math.radians(-225 + k * 27)
                c.drawLine(x + math.cos(aa) * 78, H * 0.5 + math.sin(aa) * 78, x + math.cos(aa) * 92, H * 0.5 + math.sin(aa) * 92,
                           paint('#2a1e14', style='stroke', width=4))
    text_center(c, '10', 60 + 5 * 230 + 100, H * 0.5 - 70, font('spartan_b', 34), paint((0.9, 0.2, 0.1, 0.3 + 0.7 * turn)))
    # jewel lamp
    glow(c, 60 + 5 * 230 + 40, H * 0.6, 90, '#ff2a1a', 0.9 * on)
    c.drawCircle(60 + 5 * 230 + 40, H * 0.6, 22, paint('#ff4a3a' if on > 0.5 else '#3a0c0c'))
    # cable + plug sliding in
    ins = ease_out(smoothstep(E_JACK + 0.05, E_JACK + 0.5, t), 3)
    px = 60 + 520 * (1 - ins)
    py = H * 0.5 - 420 * (1 - ins)
    ang = math.atan2(H * 0.5 - py + 1, 60 - px + 1)
    c.save()
    c.translate(px, py)
    c.rotate(-90)
    c.drawRect(skia.Rect.MakeXYWH(-16, -60, 32, 70), paint('#c8c8d0'))
    c.drawRoundRect(skia.Rect.MakeXYWH(-40, -260, 80, 210), 20, 20, shader_paint(lin_grad((-40, 0), (40, 0), ['#2a2a30', '#8a8a96', '#2a2a30'])))
    c.drawLine(0, -260, 0, -900, paint('#141418', style='stroke', width=36))
    c.restore()
    if 0 < t - (E_JACK + 0.5) < 0.25:
        k = 1 - (t - E_JACK - 0.5) / 0.25
        for j in range(12):
            a = j / 12 * 2 * math.pi
            glow(c, 60 + math.cos(a) * 120 * (1 - k), H * 0.5 + math.sin(a) * 120 * (1 - k), 18, '#ffe0a0', k)
    c.restore()


def play(c, t):
    """Eddie tears into the solo: low angle, hair flying, the half-stack behind him"""
    u = u_of(t, E_PLAY, E_FING)
    beat = T.beat_at(t)
    bg(c, ['#1a0606', '#3a0c0a', '#120404'])
    for i in range(7):
        x = W * (i + 0.5) / 7
        beam(c, x, -150, W / 2 + (x - W / 2) * 0.3, H * 0.9, 20, 260, ['#ff4a2a', '#ffb040', '#ffffff'][i % 3],
             0.18 + 0.15 * T.env_at('snare', t), blur=30)
    for k in range(6):
        c.drawRoundRect(skia.Rect.MakeXYWH(-80 + k * 220, H * 0.25, 180, H * 0.5), 18, 18, paint((0.3, 0.12, 0.1, 0.5)))
    amp_stack(c, W * 0.76, H * 0.74, 1.15, t)
    amp_stack(c, W * 0.18, H * 0.76, 0.95, t)
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(-4 + 3 * math.sin(u * math.pi))
    c.translate(-W / 2, -H / 2)
    P = pose('eddie', [(0, 'play', dict(amp=1.4))], t)
    P.update(instrument='strat', smile=1.0, mshape='grin', mopen=0.25 + 0.2 * T.env_at('snare', t), brow=0.2, htilt=-0.12,
             hair_dx=0.02 * math.sin(beat * math.pi), lean=-0.08, ey=0.5)
    h = 1850 * (1 + 0.08 * ease_io(u))
    draw(c, 'eddie', W * 0.5, H * 1.02, h, P, K.O_EDDIE, L_RED, t, shadow=False)
    c.restore()
    particles(c, t, 50, (0, 0, W, H), 41, '#ffc080', size=(2, 5), speed=(20, 60))


def fingers(c, t):
    """extreme close-up: two-hand tapping racing up the fretboard, strings shivering"""
    u = u_of(t, E_FING, E_SPKR)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0a0606'))
    c.save()
    c.translate(W / 2, H / 2)
    c.rotate(-28)
    c.translate(-140 * ease_io(u), 0)
    fb = skia.Rect.MakeXYWH(-1600, -230, 3200, 460)
    c.drawRect(fb, shader_paint(lin_grad((0, -230), (0, 230), ['#3a2214', '#5a361e', '#3a2214'])))
    for k in range(-12, 14):
        x = k * 140 - (k * k) * 1.5
        c.drawLine(x, -230, x, 230, paint('#d8d0c0', style='stroke', width=9))
        if k % 2 == 1:
            c.drawCircle(x - 70, 0, 16, paint('#efe8da'))
    amp = 3 + 14 * T.env_at('rms', t)
    for s_ in range(6):
        y0 = -190 + s_ * 76
        p = skia.Path()
        p.moveTo(-1600, y0)
        for x in range(-1600, 1601, 40):
            p.lineTo(x, y0 + amp * math.sin(x * 0.02 + t * 140 + s_) * (0.6 + 0.4 * math.sin(s_ + t * 7)))
        c.drawPath(p, paint(mix('#e8e4dc', '#c8a060', s_ / 6), style='stroke', width=4 + s_ * 1.2))
        c.drawPath(p, paint((1, 0.9, 0.6, 0.25), style='stroke', width=14, blur=8, blend=skia.BlendMode.kPlus))
    B = (T.beat_at(t) * 4)
    sixteenth = B - math.floor(B)
    tap_pos = [80, 360, 220, 500][int(math.floor(B)) % 4]
    down = 1 - ease_out(clamp(sixteenth / 0.4), 2)
    for (x, yy, sk, lab) in ((tap_pos, -60, SKIN_E, 'R'), (-380 + 40 * math.sin(B), 40, SKIN_E, 'L')):
        lift = 90 * (1 - down) if lab == 'R' else 30 * abs(math.sin(B * math.pi))
        c.save()
        c.translate(x, yy - 300 - lift)
        ol = paint('#4a2a1c', style='stroke', width=5)
        c.drawPath(smooth_path([(-60, 300), (60, 300), (200, -120), (120, -600), (-260, -600), (-200, -120)], True, 0.5),
                   paint((0, 0, 0, 0.35), blur=30))
        back = smooth_path([(-210, -620), (150, -620), (190, -260), (110, -110), (-40, -90), (-190, -200)], True, 0.5)
        c.drawPath(back, shader_paint(lin_grad((-200, 0), (190, 0), [mix(sk, '#000000', 0.18), sk, mix(sk, '#000000', 0.25)])))
        c.drawPath(back, ol)
        for j, (dx, ln) in enumerate(((-150, 120), (-80, 150), (100, 110))):     # curled fingers
            f_ = smooth_path([(dx - 38, -170), (dx + 38, -170), (dx + 34, -170 + ln), (dx, -140 + ln + 30), (dx - 34, -170 + ln)], True, 0.5)
            c.drawPath(f_, paint(mix(sk, '#000000', 0.1)))
            c.drawPath(f_, ol)
        finger = smooth_path([(-44, -160), (44, -160), (40, 230), (0, 262), (-40, 230)], True, 0.5)    # the tapping finger
        c.drawPath(finger, shader_paint(lin_grad((-44, 0), (44, 0), [mix(sk, '#000000', 0.12), mix(sk, '#ffffff', 0.12), sk])))
        c.drawPath(finger, ol)
        c.drawRoundRect(skia.Rect.MakeXYWH(-26, 178, 52, 62), 22, 22, paint('#f6e2d6'))
        for yy_ in (20, 110):
            c.drawArc(skia.Rect.MakeXYWH(-30, yy_, 60, 24), 20, 140, False, paint('#b0806a', style='stroke', width=4))
        c.drawRect(skia.Rect.MakeXYWH(-240, -760, 440, 160), paint('#ece8e0'))
        for k in range(3):
            c.drawLine(-240, -740 + k * 50, 200, -740 + k * 50, paint('#d23a2a', style='stroke', width=16))
        c.restore()
        if lab == 'R' and down > 0.7:
            glow(c, x, yy, 120, '#ffe0a0', 0.6 * down)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(rad_grad((W / 2, H / 2), H * 0.6, [(0, 0, 0, 0), (0, 0, 0, 0.6)])))


def speaker(c, t):
    """the 12-inch speaker cone pumps; dust jumps off the grille"""
    u = u_of(t, E_SPKR, E_WAVE)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c0a08'))
    low = T.env_at('low', t) + 0.6 * T.env_at('rms', t)
    cx, cy = W / 2, H * 0.48
    s = 1.0 + 0.08 * ease_io(u)
    R = 560 * s
    c.drawCircle(cx, cy, R + 60, paint('#1a1612'))
    c.drawCircle(cx, cy, R, shader_paint(rad_grad((cx, cy), R, ['#3a3430', '#22201c', '#141210'])))
    for k in range(9):
        rr = R * (0.25 + 0.085 * k) * (1 + 0.025 * low * (1 - k / 9))
        c.drawCircle(cx, cy, rr, paint((0.5, 0.45, 0.4, 0.18), style='stroke', width=3))
    dome = R * 0.24 * (1 + 0.06 * low)
    c.drawCircle(cx, cy, dome, shader_paint(rad_grad((cx - dome * 0.3, cy - dome * 0.3), dome * 1.3, ['#6a6460', '#1a1816'])))
    rng = np.random.default_rng(int(t * 60) // 3)
    for k in range(60):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.3, 1.0) * R
        jump = low * rng.uniform(10, 50)
        glow(c, cx + math.cos(a) * r, cy + math.sin(a) * r - jump, 4, '#ffe8c0', 0.6)
    # dynamic mic angled at the cone
    c.save()
    c.translate(W * 0.84, H * 0.2)
    c.rotate(35)
    c.drawRoundRect(skia.Rect.MakeXYWH(-50, 0, 100, 420), 30, 30, shader_paint(lin_grad((-50, 0), (50, 0), ['#2a2a30', '#6a6a76', '#1a1a20'])))
    c.drawRoundRect(skia.Rect.MakeXYWH(-46, 380, 92, 150), 40, 40, paint('#8a8a96'))
    c.restore()
    glow(c, cx, cy, R * 1.2, '#ff6a3a', 0.12 + 0.2 * low)


def waves(c, t):
    """six strings - then pure sound: the vibration becomes waves rolling toward the mixing desk"""
    u = u_of(t, E_WAVE, E_DESK)
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#06040c', '#0c0818', '#06040c'])))
    m = ease_io(u)
    for s_ in range(6):
        y0 = H * 0.32 + s_ * 120 * (1 - 0.3 * m)
        p = skia.Path()
        for i, x in enumerate(range(-40, W + 41, 12)):
            env = T.env_at(['rms', 'vocal', 'snare', 'low', 'rms', 'vocal'][s_], t - x / W * 0.4)
            a = (4 + 30 * m + 120 * m * env) * math.sin(x * (0.012 + 0.01 * s_ * m) - t * (8 + 10 * m) + s_)
            y = y0 + a
            (p.moveTo if i == 0 else p.lineTo)(x, y)
        col = mix('#f4e8cc', ['#ffcf6a', '#ff7a4a', '#ff4a8a', '#8a7aff', '#4ad8ff', '#7affc8'][s_], m)
        c.drawPath(p, paint(alpha(col, 0.35), style='stroke', width=18, blur=12, blend=skia.BlendMode.kPlus))
        c.drawPath(p, paint(col, style='stroke', width=4 + 2 * (1 - m)))
    if u < 0.3:              # the string nut/bridge fades out
        a = 1 - u / 0.3
        c.drawRect(skia.Rect.MakeXYWH(0, H * 0.28, 40, 720), paint((0.9, 0.85, 0.75, a)))
    particles(c, t, 40, (0, H * 0.2, W, H * 0.6), 77, '#ffffff', size=(1.5, 4), speed=(10, 40))


def desk(c, t):
    """the console lights up: every meter jumping with the solo"""
    u = u_of(t, E_DESK, E_LISTEN)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0e0c0c'))
    c.save()
    c.translate(W / 2, H * 0.4)
    s = 2.3 + 0.25 * ease_io(u)
    c.scale(s, s)
    c.rotate(-6)
    c.translate(-W / 2 - 60 * u, -H * 0.4)
    console(c, -200, W + 200, H * 0.4, 520, t, seed=8)
    c.restore()
    # a hand pushes the guitar fader up
    fy = H * 0.86 - 260 * ease_io(smoothstep(0.15, 0.7, u))
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.56 - 70, fy - 40, 140, 80), 16, 16, paint('#e8e4dc'))
    c.drawRect(skia.Rect.MakeXYWH(W * 0.56 - 8, H * 0.6, 16, H * 0.3), paint('#060606'))
    c.drawRect(skia.Rect.MakeXYWH(W * 0.56 - 30, fy + 40, 60, H * 0.86 - fy), paint((1, 0.7, 0.3, 0.35), blur=20, blend=skia.BlendMode.kPlus))
    c.drawRoundRect(skia.Rect.MakeXYWH(W * 0.56 - 70, fy - 40, 140, 80), 16, 16, paint('#e8e4dc'))
    c.drawLine(W * 0.56 - 60, fy, W * 0.56 + 60, fy, paint('#d23a2a', style='stroke', width=8))
    text_center(c, 'GTR SOLO', W * 0.56, fy + 90, font('spartan_b', 34), paint((1, 0.9, 0.6, 0.9)))
    glow(c, W / 2, H * 0.3, 700, '#ffb040', 0.12 + 0.15 * T.env_at('rms', t))


def listen(c, t):
    """later, in the control room: Michael hears the playback - and lifts one ear-cup in disbelief"""
    u = u_of(t, E_LISTEN, END)
    studio_room(c, t)
    c.drawRect(skia.Rect.MakeWH(W, H), paint((0.06, 0.02, 0.0, 0.3)))
    tape_machine(c, W * 0.2, H * 0.6, 0.75, t, label='BEAT IT - GTR SOLO')
    text_center(c, 'PLAYBACK', W * 0.2, H * 0.6 - 300, font('spartan_b', 30), paint((1, 0.3, 0.2, 0.6 + 0.4 * (math.sin(t * 8) > 0))))
    wow = smoothstep(E_LISTEN + 0.55, E_LISTEN + 0.85, t)
    P = pose(K.MJ, [(0, 'nod_slow', dict(look=-0.2))], t)
    P.update(blink=0.85 * (1 - wow), smile=0.35 + 0.65 * wow, mshape='grin' if wow > 0.5 else 'smile', mopen=0.45 * wow,
             brow=0.2 + 0.6 * wow, ey=-0.1, lsh=0.2 + 1.0 * wow, lel=0.2 + 2.55 * wow, lhand='open', rsh=0.25, rel=-0.6)
    if T.env_at('rms', t) > 0.5 and wow < 0.2:
        P['hnod'] += 0.008
    h = 2100
    gx, gy = place_head(K.MJ, P, h, (W * 0.62, H * 0.42))
    S = draw(c, K.MJ, gx, gy, h, P, K.O_STUDIO, K.L_STUDIO, t, shadow=False)
    hx, hy = S['head']
    r = S['hr']
    c.drawArc(skia.Rect.MakeXYWH(hx - r * 1.22, hy - r * 1.75, r * 2.44, r * 2.5), 195, 150, False, paint('#8a8a96', style='stroke', width=r * 0.16))
    for sd in (-1, 1):
        off = (r * 0.5 if sd < 0 else 0) * wow
        cup = skia.Rect.MakeXYWH(hx + sd * r * 1.08 - r * 0.24 + sd * off, hy - r * 0.25 - off * 0.6, r * 0.48, r * 0.62)
        c.drawRoundRect(cup, r * 0.18, r * 0.18, shader_paint(lin_grad((cup.left(), 0), (cup.right(), 0), ['#3a3a44', '#b8b8c4', '#2a2a30'])))
    console(c, -300, W + 300, H * 0.8, 400, t, seed=5)


SHOTS = [(E_PHONE, phone), (E_TALK, talk), (E_JACK, jack), (E_PLAY, play), (E_FING, fingers), (E_SPKR, speaker),
         (E_WAVE, waves), (E_DESK, desk), (E_LISTEN, listen)]


def draw_act(c, t):
    fn = SHOTS[0][1]
    for t0, f in SHOTS:
        if t >= t0:
            fn = f
    fn(c, t)
    for tc in (E_PLAY,):                 # one white-hot accent on the downbeat the solo hits
        k = 1 - smoothstep(tc, tc + 0.2, t)
        if 0 < k < 1 and t >= tc:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.9, 0.75, 0.5 * k)))


def captions(c, t):
    cap(c, t, E_PHONE + 0.25, E_JACK + 1.4, ['THEN EDDIE VAN HALEN', 'JOINED THE RECORD.'], y=300, size=86, accent=(0, (1.0, 0.5, 0.42)))
