"""Master edit: which scene draws at time t, transitions between scenes, and per-scene colour grade."""
import skia
from gfx import W, H, paint, smoothstep, clamp, ease_io
import timing as T
import scene1
import scene2
import scene3
import scene4
import scene5

DB = T.db
SCENES = [(0.0, scene1), (scene2.T0, scene2), (scene3.T0, scene3), (scene4.T0, scene4), (scene5.T0, scene5)]
WHIP = (scene2.T0 - 0.32, scene2.T0 + 0.13)      # whip pan Gary living room -> club stage


def _scene_at(t):
    scene = SCENES[0][1]
    for t0, s in SCENES:
        if t >= t0:
            scene = s
    return scene


def _offscreen(fn, t):
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    fn(c, t)
    return surf.makeImageSnapshot()


def draw(c, t, surf=None):
    if WHIP[0] <= t < WHIP[1]:
        u = (t - WHIP[0]) / (WHIP[1] - WHIP[0])
        e = ease_io(u)
        a = _offscreen(scene1.draw, t)
        b = _offscreen(scene2.draw, max(t, scene2.T0))
        blur = 160 * (1 - abs(2 * u - 1)) + 2
        p = skia.Paint()
        p.setImageFilter(skia.ImageFilters.Blur(blur, 2))
        c.drawImage(a, -e * W, 0, skia.SamplingOptions(), p)
        c.drawImage(b, (1 - e) * W, 0, skia.SamplingOptions(), p)
        return
    _scene_at(t).draw(c, t)


def grade(t):
    s = _scene_at(t)
    if s is scene1:
        return dict(vignette=0.6, grain=0.085, warm=(1.0, 0.88, 0.72), warm_a=0.10)     # amber / dusty blue
    if s is scene2:
        return dict(vignette=0.62, grain=0.08, warm=(1.0, 0.86, 0.82), warm_a=0.08)     # burgundy / theatrical gold
    if s is scene3:
        return dict(vignette=0.5, grain=0.07, warm=(1.0, 0.93, 0.86), warm_a=0.05)      # orange / purple / turquoise
    if s is scene4:
        return dict(vignette=0.45, grain=0.065, warm=(1.0, 0.95, 0.9), warm_a=0.04)
    return dict(vignette=0.5, grain=0.06, warm=(1.0, 0.94, 0.85), warm_a=0.05)
