"""V2 0:19-0:39  FIVE BROTHERS, ONE DREAM (talent show) -> THE BREAKTHROUGH (Apollo, the road to Motown)."""
import math
import numpy as np
import skia
from gfx import (W, H, paint, shader_paint, lin_grad, rad_grad, alpha, mix, shade, glow, beam, smooth_path, poly_path,
                 clamp, ease_io, ease_out, ease_in, back_out, smoothstep, font, text_center, noise1)
from world import Cam, cam_path, Layer, CHARS, particles, silhouette, crowd
from character import outfits, JOE_OUTFIT, DESIGNS, base_pose
import choreo
import timing as T
import scene2
import scene3
from v2_common import caption, draw_cast, JOE, L_JOE_BACKLIT, L_WARM

DB = T.db
BEAT = T.PERIOD
D_WALK, D_SPOT, D_CONF, D_CROWD = DB(7), DB(8), DB(9), DB(10)
E_APOLLO, E_INSIDE, E_CONTRACT, E_STUDIO, END = DB(11), DB(12), DB(13), DB(14), DB(15)
START = D_WALK
STAGE_GY = 420
POS = {'tito': (-330, -20), 'jackie': (-170, -40), 'michael': (0, 30), 'marlon': (170, -40), 'jermaine': (335, -20)}
INSTR = {'tito': 'guitar', 'jermaine': 'bass'}
ENTER_ORDER = ['jermaine', 'marlon', 'tito', 'jackie', 'michael']


def walk_on(k, t):
    """walk in from stage left, one after another; Michael last"""
    i = ENTER_ORDER.index(k)
    t0 = D_WALK + i * 0.22
    t1 = t0 + 1.25
    x_final = POS[k][0]
    u = ease_out(clamp((t - t0) / (t1 - t0)), 1.6)
    return -900 + (x_final + 900) * u


def stage_band(t, era='club', light=None, sched=None, sing_m=1.0, walk=False, over=None):
    mem = []
    for k, (x, dy) in POS.items():
        s = sched(k) if sched else [(0, 'groove', {})]
        if walk:
            i = ENTER_ORDER.index(k)
            arrive = D_WALK + i * 0.22 + 1.25
            s = [(0, 'walk', dict(start=T.beat_at(D_WALK + i * 0.22) - T.PHASE, speed=0.0))] + \
                [(arrive, e[1], e[2]) for e in s[:1]] + s[1:]
        mem.append(dict(key=k, x=(lambda tt, k=k: walk_on(k, tt)) if walk else x, gy=STAGE_GY + dy, sched=s,
                        instrument=INSTR.get(k), sing=sing_m if k == 'michael' else None,
                        ripple={'jackie': 0.035, 'marlon': 0.07}.get(k, 0.0), over=(over(k) if over else None)))
    return mem


# --------------------------------------------------------------------------- D: talent show
def sched_D(k):
    if k == 'michael':
        return [(0, 'shy', {}), (D_SPOT, 'mic_sing', dict(amp=0.5)), (D_CONF, 'step_touch', {}),
                (D_CONF + 2 * BEAT - 0.1, 'spin', dict(start='auto', length=1.0)),
                (D_CONF + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=1)),
                (D_CROWD, 'mic_sing', dict(amp=1.3)), (D_CROWD + 2 * BEAT, 'kick', dict(side=1))]
    if k in INSTR:
        return [(0, 'play', dict(amp=0.6)), (D_CONF, 'play', dict(amp=1.2))]
    side = -1 if k == 'jackie' else 1
    return [(0, 'groove', dict(amp=0.4)), (D_CONF, 'step_touch', {}),
            (D_CONF + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=side)), (D_CROWD, 'arm_roll', {})]


def joe_wings(c, t, x, gy, h, look=-0.6, nod=False):
    P = choreo.perform([(0, 'arms_folded', dict(look=look))], t, 'joe', seed=66)
    if nod:     # a small, approving nod - pride and control in the same face
        k = smoothstep(D_CROWD + 1.1, D_CROWD + 1.5, t)
        P['hnod'] = 0.012 * math.sin(clamp((t - D_CROWD - 1.1) / 0.6) * math.pi)
        P['smile'] = -0.45 + 0.65 * k
        P['brow'] = -0.9 + 0.7 * k
        P['blink'] = 0.28 - 0.1 * k
    JOE.draw(c, x, gy, h, P, JOE_OUTFIT, L_JOE_BACKLIT, t, shadow=False)


def shot_walk_on(c, t):
    beat = T.beat_at(t)
    u = clamp((t - D_WALK) / (D_SPOT - D_WALK))
    cam = Cam(-60 + 60 * u, 120, 1.18, 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14040a'))
    with Layer(c, cam, 0.7, t):
        scene2.club_bg(c, t, beat)
        c.drawRect(skia.Rect.MakeLTRB(-2000, -2000, 2000, 2000), paint((0.05, 0.0, 0.03, 0.35)))
    def over(k):
        def f(tt):
            if k == 'michael' and tt > D_WALK + 4 * 0.22 + 1.25:
                return dict(hyaw=0.45, ex=0.9, brow=0.7, fear=0.35, smile=0.15)     # glances at his father in the wings
            return {}
        return f
    with Layer(c, cam, 1.0, t):
        draw_cast(c, t, stage_band(t, sched=sched_D, walk=True, over=over), scene2.LIGHT_CLUB, 'club')
    with Layer(c, cam, 1.45, t):
        joe_wings(c, t, 300, 720, 560 * 1.66)
        scene2.club_fg(c, t, 0.15, beat)


def shot_spot(c, t):
    beat = T.beat_at(t)
    u = clamp((t - D_SPOT) / (D_CONF - D_SPOT))
    cam = Cam(10, 140 - 30 * u, 2.05 + 0.25 * ease_io(u), 0)
    if t - D_SPOT < 0.25:
        cam.shake = 0.6 * (1 - (t - D_SPOT) / 0.25)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#0c0206'))
    with Layer(c, cam, 0.7, t):
        scene2.club_bg(c, t, beat)
        c.drawRect(skia.Rect.MakeLTRB(-2000, -2000, 2000, 2000), paint((0.03, 0.0, 0.02, 0.6)))
    with Layer(c, cam, 1.0, t):
        scene2.spotlight(c, 0, STAGE_GY + 30, -1400, 1.0)
        draw_cast(c, t, stage_band(t, sched=sched_D), scene2.LIGHT_CLUB, 'club')


def shot_confidence(c, t):
    beat = T.beat_at(t)
    u = clamp((t - D_CONF) / (D_CROWD - D_CONF))
    cam = Cam(-40 + 80 * ease_io(u), 110, 1.3 - 0.1 * u, 2 * math.sin(u * math.pi))
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14040a'))
    with Layer(c, cam, 0.7, t):
        scene2.club_bg(c, t, beat)
    with Layer(c, cam, 1.0, t):
        scene2.spotlight(c, 0, STAGE_GY + 30, -1400, 0.8)
        draw_cast(c, t, stage_band(t, sched=sched_D), scene2.LIGHT_CLUB, 'club')
    with Layer(c, cam, 1.5, t):
        scene2.club_fg(c, t, 0.4 + 0.6 * u, beat)


def shot_crowd(c, t):
    """the audience rises: reverse angle from the stage, then Joe's quiet nod"""
    beat = T.beat_at(t)
    u = clamp((t - D_CROWD) / (E_APOLLO - D_CROWD))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#2a0810', '#5a1420', '#1a0408'])))
    # stage-light haze toward the audience
    for i, x in enumerate((160, 540, 920)):
        beam(c, x, -100, x + (i - 1) * 260, H, 40, 380, '#ffcf9a', 0.18, blur=40)
    c.save()
    c.translate(W / 2, H * 0.25)
    s = 0.62 + 0.08 * ease_io(u)
    c.scale(s, s)
    crowd(c, t, 6, 1.0, '#1a0608', '#ffb080', width=2400, seed=301, y0=0, row_gap=180, scale0=1.25, beat_phase=beat)
    c.restore()
    # Joe in the wings (foreground right): arms folded ... a small nod
    joe_wings(c, t, W * 0.93, H * 1.12, 1350, look=-0.8, nod=True)
    for k in range(14):        # clapping hands raised in the foreground (bokeh)
        x = (k * 173) % W
        y = H * 0.82 + 40 * math.sin(k)
        cl = abs(math.sin(math.pi * (beat + k * 0.13)))
        glow(c, x, y - 20 * cl, 40, '#ffcf9a', 0.25)


# --------------------------------------------------------------------------- E: Apollo, the road to Motown
def apollo_exterior(c, t):
    u = clamp((t - E_APOLLO) / (E_INSIDE - E_APOLLO))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#0a0a22', '#1a1440', '#2a1a2a'])))
    c.save()
    c.translate(0, 260 * ease_io(u) - 120)       # crane up the façade
    # building façade
    c.drawRect(skia.Rect.MakeLTRB(0, -200, W, H + 400), shader_paint(lin_grad((0, 0), (0, H), ['#3a2a2a', '#5a3a2e'])))
    for row in range(10):
        for k in range(5):
            x, y = 60 + k * 210, -160 + row * 150
            lit = (row * 7 + k * 3) % 5 == 0
            c.drawRect(skia.Rect.MakeXYWH(x, y, 110, 90), paint('#ffd88a' if lit else '#1a1420'))
    # vertical blade sign A-P-O-L-L-O
    bx = W * 0.8
    c.drawRoundRect(skia.Rect.MakeXYWH(bx - 95, 40, 190, 960), 20, 20, paint('#2a0a10'))
    for i, ch in enumerate('APOLLO'):
        y = 150 + i * 150
        on = 0.75 + 0.25 * math.sin(t * 8 + i)
        glow(c, bx, y - 45, 140, '#ff3a4a', 0.35 * on)
        text_center(c, ch, bx, y, font('spartan', 140), paint(mix('#ff6a6a', '#ffffff', 0.35 * on)))
    # horizontal marquee with chaser bulbs
    my = 1060
    c.drawRect(skia.Rect.MakeLTRB(-20, my, W + 20, my + 330), paint('#f2e6c8'))
    for k in range(40):
        on = (k + int(t * 14)) % 3 == 0
        for yy in (my + 16, my + 314):
            c.drawCircle(k * 28 + 8, yy, 8, paint('#fff2b0' if on else '#9a7a3a'))
    text_center(c, 'AMATEUR NIGHT', W / 2, my + 120, font('spartan', 84), paint('#1a1414'))
    text_center(c, 'THE JACKSON 5', W / 2, my + 240, font('spartan', 96), paint('#a0141e'))
    glow(c, W / 2, my + 400, 700, '#ffd88a', 0.35)
    c.restore()
    # line of people on the sidewalk (silhouettes, foreground)
    c.save()
    c.translate(W / 2, H * 0.98)
    crowd(c, t, 1, 0.4, '#0c0810', '#ff6a6a', width=1800, seed=505, y0=0, row_gap=0, scale0=1.4, beat_phase=T.beat_at(t))
    c.restore()
    caption(c, t, E_APOLLO + 0.25, E_INSIDE + 0.2, ['HARLEM, 1967'], y=300, size=70)


def apollo_inside(c, t):
    beat = T.beat_at(t)
    u = clamp((t - E_INSIDE) / (E_CONTRACT - E_INSIDE))
    cam = Cam(0, -40 - 160 * ease_io(u), 0.95 - 0.25 * ease_io(u), 0)
    c.drawRect(skia.Rect.MakeWH(W, H), paint('#14040a'))
    with Layer(c, cam, 0.85, t):
        scene2.theater_bg(c, t, beat)
    def sched(k):
        if k in INSTR:
            return [(0, 'play', dict(amp=1.3))]
        side = 1 if k != 'jackie' else -1
        return [(0, 'step_touch', {}), (E_INSIDE + 2 * BEAT - 0.08, 'spin', dict(start='auto', length=1.0)),
                (E_INSIDE + 3 * BEAT - 0.05, 'point_hit', dict(start='auto', side=side))]
    with Layer(c, cam, 1.0, t):
        for x in (-300, 300):
            beam(c, x * 3, -2200, x * 0.3, STAGE_GY - 100, 50, 260, '#fff2d0', 0.4, blur=40)
        draw_cast(c, t, stage_band(t, sched=sched), scene2.LIGHT_THEATER, 'club')
    with Layer(c, cam, 1.45, t):
        crowd(c, t, 4, 1.0, '#100306', '#ffb070', width=3600, seed=52, y0=620, row_gap=110, scale0=1.1, beat_phase=beat)


def contract(c, t):
    """Joe at the kitchen table with the recording agreement; five heads peek round the door"""
    u = clamp((t - E_CONTRACT) / (E_STUDIO - E_CONTRACT))
    c.drawRect(skia.Rect.MakeWH(W, H), shader_paint(lin_grad((0, 0), (0, H), ['#2a1c18', '#4a3020'])))
    glow(c, W * 0.55, H * 0.22, 700, '#ffcf8a', 0.45)
    c.drawLine(W * 0.55, 0, W * 0.55, H * 0.15, paint('#1a1210', style='stroke', width=4))
    c.drawPath(poly_path([(W * 0.55 - 120, H * 0.15 + 90), (W * 0.55 + 120, H * 0.15 + 90), (W * 0.55 + 60, H * 0.15),
                          (W * 0.55 - 60, H * 0.15)]), paint('#d8a24a'))
    # doorway on the left with the five brothers peeking (stacked, smallest at the bottom)
    c.drawRect(skia.Rect.MakeLTRB(-20, 380, 280, H * 0.72), paint('#120c0a'))
    c.drawRect(skia.Rect.MakeLTRB(260, 360, 300, H * 0.72), paint('#6a4a30'))
    for i, k in enumerate(['jackie', 'tito', 'jermaine', 'marlon', 'michael']):
        P = base_pose(hyaw=0.55, ex=0.9, brow=0.7, smile=0.35 + 0.4 * smoothstep(0.6, 0.8, u), mopen=0.2 * smoothstep(0.6, 0.8, u),
                      mshape='grin', blink=0.0)
        hh = 800 * DESIGNS[k].height
        S0 = CHARS[k].skeleton(0, 0, hh, P)
        hy = 560 + i * 150
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(-50, 300, 282, H))
        CHARS[k].draw(c, 190 - S0['head'][0], hy - S0['head'][1], hh, P, outfits('home')[k], L_WARM, t, shadow=False)
        c.restore()
    # Joe seated behind the table
    P = choreo.perform([(0, 'arms_folded', {})], t, 'joe', seed=66)
    sign = smoothstep(0.35, 0.45, u)
    P.update(lsh=0.25, lel=-1.25, rsh=0.3 + 0.05 * math.sin(t * 30) * sign * (u < 0.75), rel=-1.4, lhand='open', rhand='fist',
             hnod=0.02, ey=0.75, ex=0.1, brow=-0.6, smile=-0.25 + 0.35 * smoothstep(0.72, 0.85, u), blink=0.25)
    S = JOE.draw(c, W * 0.6, H * 0.98, 1500, P, JOE_OUTFIT, L_WARM, t, shadow=False)
    # table (covers his legs) + the agreement + pen
    c.drawPath(poly_path([(-50, H * 0.72), (W + 50, H * 0.72), (W + 200, H + 50), (-200, H + 50)]),
               shader_paint(lin_grad((0, H * 0.72), (0, H), ['#6a3e22', '#3a2010'])))
    px, py = W * 0.58, H * 0.8
    paper = poly_path([(px - 230, py - 80), (px + 230, py - 80), (px + 280, py + 250), (px - 280, py + 250)])
    c.drawPath(paper, paint('#f4ecd8'))
    c.drawPath(paper, paint('#b8a888', style='stroke', width=2))
    text_center(c, 'RECORDING AGREEMENT', px, py - 30, font('garamond', 34), paint('#2a1a10'), tracking=2)
    for k in range(6):
        y = py + 20 + k * 28
        c.drawLine(px - 200 - k * 6, y, px + 200 + k * 6, y, paint((0.4, 0.35, 0.3, 0.5), style='stroke', width=2))
    # the signature writes itself
    sp = skia.Path()
    n = int(40 * clamp((u - 0.38) / 0.35))
    for i in range(n):
        x = px - 40 + i * 6
        y = py + 205 + 14 * math.sin(i * 0.9) - 4 * (i % 5 == 0)
        (sp.moveTo if i == 0 else sp.lineTo)(x, y)
    c.drawPath(sp, paint('#14204a', style='stroke', width=4))
    c.drawLine(px - 60, py + 225, px + 220, py + 225, paint('#2a1a10', style='stroke', width=2))
    wx, wy = S['arms'][1][2]
    c.drawLine(wx, wy, wx - 30, wy + 70, paint('#1a1a22', style='stroke', width=10))
    caption(c, t, E_CONTRACT + 0.2, E_STUDIO + 2.3, ['1968 —', 'THE ROAD TO MOTOWN.'], y=300, size=78)


def studio_arrival(c, t):
    beat = T.beat_at(t)
    u = clamp((t - E_STUDIO) / (END - E_STUDIO))
    scene3.control_room(c, t, beat, excite=0.0, push=0.15 + 0.5 * ease_io(u))
    caption(c, t, E_CONTRACT + 0.2, E_STUDIO + 2.3, ['1968 —', 'THE ROAD TO MOTOWN.'], y=300, size=78)


def draw(c, t):
    if t < D_SPOT:
        shot_walk_on(c, t)
    elif t < D_CONF:
        shot_spot(c, t)
    elif t < D_CROWD:
        shot_confidence(c, t)
    elif t < E_APOLLO:
        shot_crowd(c, t)
    elif t < E_INSIDE:
        apollo_exterior(c, t)
    elif t < E_CONTRACT:
        apollo_inside(c, t)
    elif t < E_STUDIO:
        contract(c, t)
    else:
        studio_arrival(c, t)
    caption(c, t, D_CONF + 0.4, E_APOLLO - 0.15, ['THEN THE WORLD', 'STARTED NOTICING.'], y=300)
    # flash on the downbeat cuts into the stage world
    for tc in (D_WALK, D_SPOT, E_INSIDE):
        fl = 1 - smoothstep(tc, tc + 0.22, t)
        if 0 < fl < 1 and t >= tc:
            c.drawRect(skia.Rect.MakeWH(W, H), paint((1, 0.92, 0.8, 0.45 * fl)))
