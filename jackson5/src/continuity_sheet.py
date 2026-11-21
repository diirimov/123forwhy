"""V2 character continuity sheet: the five brothers in every era wardrobe + Joe Jackson (exactly five brothers)."""
import skia
from gfx import paint, text_center, font, lin_grad, shader_paint
from character import Character, base_pose, outfits, ORDER, BROTHERS, JOE_OUTFIT, DESIGNS
eras = [('home', 'GARY - REHEARSALS'), ('club', 'TALENT SHOWS / APOLLO'), ('tv', 'TV 1969-70'), ('arena', 'ARENA')]
Wd, Hd = 3000, 2700
s = skia.Surface(Wd, Hd); c = s.getCanvas()
c.drawRect(skia.Rect.MakeWH(Wd, Hd), shader_paint(lin_grad((0, 0), (0, Hd), ['#f3e6cf', '#e2cfae'])))
L = dict(key=(-0.55, -0.83), amb='#fff1dc', amb_a=0.1, rim='#fff6e0', line='#3a1e1a', floor_shadow=0.25)
text_center(c, 'THE JACKSON 5 - STORY V2 CONTINUITY SHEET', Wd / 2, 90, font('spartan', 62), paint('#3a1e1a'))
for r, (era, lab) in enumerate(eras):
    y = 700 + r * 590
    c.drawString(lab, 40, y + 62, font('spartan_b', 30), paint('#7a4a2a'))
    O = outfits(era)
    for i, k in enumerate(ORDER):
        P = base_pose(smile=0.7)
        if k == 'tito': P['instrument'] = 'guitar'
        if k == 'jermaine': P['instrument'] = 'bass'
        Character(k).draw(c, 260 + i * 420, y, 380 * BROTHERS[k].height, P, O[k], L)
        if r == 0:
            text_center(c, BROTHERS[k].name.upper(), 260 + i * 420, 165, font('spartan_b', 34), paint('#3a1e1a'))
j = Character('joe')
for i, (lab, P) in enumerate([('JOE - STERN', base_pose(smile=-0.45, brow=-0.9, blink=0.28, lsh=0.32, lel=-2.45, rsh=0.32, rel=-2.45, lhand='fist', rhand='fist')),
                              ('JOE - THE NOD', base_pose(smile=0.2, brow=-0.2, blink=0.15, lsh=0.32, lel=-2.45, rsh=0.32, rel=-2.45, lhand='fist', rhand='fist')),
                              ('JOE - BACK', base_pose(spin=0.5, lsh=0.14, lel=-0.55, rsh=0.14, rel=-0.55))]):
    x = 2420 + (i % 2) * 300 if i < 2 else 2570
    yy = 1000 if i < 2 else 2200
    j.draw(c, x, yy, 380 * DESIGNS['joe'].height * 0.85, P, JOE_OUTFIT, L)
    text_center(c, lab, x, yy + 50, font('spartan_b', 26), paint('#3a1e1a'))
text_center(c, 'Heights (relative): ' + '  '.join(f"{BROTHERS[k].name} {BROTHERS[k].height:.2f}" for k in ORDER) + f"   Joe {DESIGNS['joe'].height:.2f}",
            Wd / 2, Hd - 40, font('spartan_b', 30), paint('#3a1e1a'))
s.makeImageSnapshot().save('../output/CONTINUITY_SHEET_V2.png', skia.kPNG)
print('ok')
