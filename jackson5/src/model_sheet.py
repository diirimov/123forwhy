"""Character model sheet: line-up, turnaround (front / 3/4 / back), expressions -> output/model_sheet.png"""
import sys, skia
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from gfx import paint, text_center, font, lin_grad, shader_paint
from character import Character, base_pose, outfits, ORDER, BROTHERS

def main(era='tv', out='output/model_sheet.png'):
    Wd, Hd = 2400, 2400
    surf = skia.Surface(Wd, Hd); c = surf.getCanvas()
    c.drawRect(skia.Rect.MakeWH(Wd, Hd), shader_paint(lin_grad((0, 0), (0, Hd), ['#f3e6cf', '#e2cfae'])))
    L = dict(key=(-0.55, -0.83), amb='#fff1dc', amb_a=0.1, rim='#fff6e0', line='#3a1e1a', floor_shadow=0.25)
    O = outfits(era)
    text_center(c, f'THE JACKSON 5 - MODEL SHEET ({era})', Wd / 2, 90, font('spartan', 64), paint('#3a1e1a'))
    base = 620
    for i, k in enumerate(ORDER):
        x = 260 + i * 470
        ch = Character(k)
        P = base_pose(smile=0.7)
        if k == 'tito': P['instrument'] = 'guitar'
        if k == 'jermaine': P['instrument'] = 'bass'
        ch.draw(c, x, 1050, base * BROTHERS[k].height, P, O[k], L)
        text_center(c, BROTHERS[k].name.upper(), x, 1120, font('spartan_b', 44), paint('#3a1e1a'))
    # turnaround Michael
    m = Character('michael')
    for i, (lab, kw) in enumerate([('FRONT', {}), ('3/4', dict(hyaw=0.55, tw=0.5)), ('3/4 L', dict(hyaw=-0.55, tw=-0.5)),
                                    ('BACK', dict(spin=0.5))]):
        x = 300 + i * 420
        m.draw(c, x, 2000, 600, base_pose(**kw), O['michael'], L)
        text_center(c, lab, x, 2060, font('spartan_b', 36), paint('#3a1e1a'))
    # expressions (head close-ups)
    exprs = [dict(smile=0.9, mopen=0.7, mshape='ah', brow=0.6), dict(smile=0.2, mopen=0.6, mshape='o', brow=0.9, ey=-0.5),
             dict(smile=0.0, brow=-0.6, ex=0.6), dict(smile=1.0, mopen=0.5, mshape='grin', blink=1.0)]
    for i, e in enumerate(exprs):
        cs = c.save()
        c.clipRect(skia.Rect.MakeXYWH(1900, 1180 + i * 300, 420, 290))
        m.draw(c, 2110, 1180 + i * 300 + 1350, 1400, base_pose(**e), O['michael'], L, shadow=False)
        c.restoreToCount(cs)
    surf.makeImageSnapshot().save(out, skia.kPNG)
    print('wrote', out)

if __name__ == '__main__':
    main(*(sys.argv[1:]))
