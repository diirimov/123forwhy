import _paths  # noqa
import skia
from gfx import paint, shader_paint, lin_grad, font, text_center
from character import base_pose
import ev_cast as E
from world import CHARS
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / 'output'
cells = [(E.KID, E.O_KID_HOME['michael'], 'GARY 1960s'), (E.KID, E.O_KID_TV['michael'], 'JACKSON 5'), (E.M79, E.O_OTW, 'OFF THE WALL 1979'),
         (E.M83, E.O_THRILLER, 'THRILLER 1982-83'), (E.M83, E.O_MOTOWN, 'MOTOWN 25 1983'), (E.M83, E.O_BEATIT, 'BEAT IT 1983'),
         (E.M87, E.O_BAD, 'BAD 1987'), (E.M87, E.O_SC, 'SMOOTH CRIMINAL 1988'), (E.M92, E.O_DANGEROUS, 'DANGEROUS 1992'),
         (E.M92, E.O_HISTORY, 'HISTORY 1996'), (E.M09, E.O_TII, 'REHEARSALS 2009'), ('z1', E.O_ZOMBIE[1], 'ZOMBIE')]
Wd, Hd = 3000, 2700
s = skia.Surface(Wd, Hd)
c = s.getCanvas()
c.drawRect(skia.Rect.MakeWH(Wd, Hd), shader_paint(lin_grad((0, 0), (0, Hd), ['#f3e6d2', '#e6d4b8'])))
text_center(c, 'THE EVOLUTION OF A KING - MICHAEL THROUGH THE ERAS', Wd / 2, 80, font('spartan_b', 56), paint('#2a1410'))
for i, (k, o, lab) in enumerate(cells):
    col, row = i % 6, i // 6
    x, gy = 250 + col * 500, 1180 + row * 1300
    CHARS[k].draw(c, x, gy, 580 * E.DESIGNS[k].height * 1.0, base_pose(smile=0.6), o, E.L_STADIUM, 0.3)
    text_center(c, lab, x, gy + 80, font('spartan_b', 34), paint('#2a1410'))
s.makeImageSnapshot().save(str(OUT / 'MODEL_SHEET_EVOLUTION.png'), skia.kPNG)
print('ok')
