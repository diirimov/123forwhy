"""Model sheet for the Beat It episode -> output/MODEL_SHEET_BEAT_IT.png"""
import _paths  # noqa
import skia
from gfx import paint, shader_paint, lin_grad, font, text_center
from character import base_pose
import bi_cast as K
from world import CHARS
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'output'
OUT.mkdir(exist_ok=True)
cells = [(K.KID, K.O_J5['michael'], 'MICHAEL 1970'), (K.MJ, K.O_STUDIO, 'MICHAEL 1982 STUDIO'), (K.MJ, K.O_BEATIT, 'BEAT IT 1983'),
         (K.MJ, K.O_STAGE, 'STAGE 1983'), ('quincy', K.O_QUINCY, 'QUINCY JONES'), ('eddie', K.O_EDDIE, 'EDDIE VAN HALEN'),
         ('x0', K.O_GROUP_A[0], 'GROUP A'), ('x1', K.O_GROUP_B[0], 'GROUP B'), ('x2', K.O_DANCERS[0], 'DANCER'),
         ('x3', K.O_DANCERS[1], 'DANCER'), ('x4', K.O_CREW, 'CREW'), ('fan2', K.O_FANS[2], 'FAN 1983')]
Wd, Hd = 3000, 2600
s = skia.Surface(Wd, Hd)
c = s.getCanvas()
c.drawRect(skia.Rect.MakeWH(Wd, Hd), shader_paint(lin_grad((0, 0), (0, Hd), ['#f3e6d2', '#e6d4b8'])))
text_center(c, 'BEAT IT EPISODE - CAST', Wd / 2, 80, font('spartan_b', 56), paint('#2a1410'))
for i, (k, o, lab) in enumerate(cells):
    col, row = i % 6, i // 6
    x, gy = 250 + col * 500, 1150 + row * 1250
    P = base_pose(smile=0.6)
    if k == 'eddie':
        P.update(instrument='strat')
    CHARS[k].draw(c, x, gy, 560 * K.DESIGNS[k].height * 1.05, P, o, K.L_WARM, 0.3)
    text_center(c, lab, x, gy + 80, font('spartan_b', 36), paint('#2a1410'))
s.makeImageSnapshot().save(str(OUT / 'MODEL_SHEET_BEAT_IT.png'), skia.kPNG)
print('ok')
