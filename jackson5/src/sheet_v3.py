import skia
from gfx import paint, text_center, font, lin_grad, shader_paint
from character import Character, base_pose, outfits, DESIGNS, MICHAEL_OUTFITS, outfits84, LINEUP84, JOE_OUTFIT, JOE84_OUTFIT
import choreo
Wd, Hd = 3000, 2400
s = skia.Surface(Wd, Hd); c = s.getCanvas()
c.drawRect(skia.Rect.MakeWH(Wd, Hd), shader_paint(lin_grad((0, 0), (0, Hd), ['#f3e6cf', '#e2cfae'])))
L = dict(key=(-0.55, -0.83), amb='#fff1dc', amb_a=0.1, rim='#fff6e0', line='#3a1e1a', floor_shadow=0.25)
text_center(c, 'STORY V3 - MICHAEL THROUGH THE YEARS / THE JACKSONS 1984', Wd / 2, 80, font('spartan', 56), paint('#3a1e1a'))
base = 520
ages = [('michael', outfits('home')['michael'], 'CHILD 1960s'), ('michael72', MICHAEL_OUTFITS['michael72'], 'TEEN 1972'),
        ('michael79', MICHAEL_OUTFITS['michael79'], '1979'), ('michael84', MICHAEL_OUTFITS['michael82'], '1982-84'),
        ('joe', JOE_OUTFIT, 'JOE 1960s'), ('joe84', JOE84_OUTFIT, 'JOE 1984')]
for i, (k, o, lab) in enumerate(ages):
    x = 250 + i * 500
    P = base_pose(smile=0.6)
    if k.startswith('joe'):
        P.update(smile=-0.4, brow=-0.8, blink=0.25)
    Character(k).draw(c, x, 1080, base * DESIGNS[k].height * 0.62, P, o, L, 1.0)
    text_center(c, lab, x, 1140, font('spartan_b', 36), paint('#3a1e1a'))
O = outfits84()
for i, k in enumerate(LINEUP84):
    x = 260 + i * 500
    P = base_pose(smile=0.7)
    if k == 'michael84':
        choreo.hat_pose(1, P, start=0)
        P['_x'] = 0
    Character(k).draw(c, x, 2260, base * DESIGNS[k].height * 0.62, P, O[k], L, 1.0)
    text_center(c, DESIGNS[k].name.upper() + ' 84', x, 2330, font('spartan_b', 34), paint('#3a1e1a'))
s.makeImageSnapshot().save('../build/sheet_v3.png', skia.kPNG)
print('ok')
