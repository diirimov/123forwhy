import sys, skia
sys.path.insert(0, '.')
from gfx import paint, text_center, font, lin_grad, shader_paint
from character import Character, base_pose, outfits
import choreo
moves = [('groove', {}), ('step_touch', {}), ('point_hit', dict(start=0)), ('spin', dict(start=0)), ('arm_roll', {}),
         ('shimmy', {}), ('slide', dict(start=0, dist=0.0)), ('kick', {}), ('knee_drop', dict(start=0)), ('mic_sing', {}),
         ('cheer', {}), ('pose_hold', {})]
phases = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5]
Wd, Hd = 6 * 260, len(moves) * 330
surf = skia.Surface(Wd, Hd); c = surf.getCanvas()
c.clear(skia.Color(240, 228, 205))
L = dict(key=(-0.55, -0.83), amb='#fff1dc', amb_a=0.1, rim='#fff6e0', line='#3a1e1a', floor_shadow=0.25)
O = outfits(sys.argv[1] if len(sys.argv) > 1 else 'tv')
m = Character('michael')
for i, (name, kw) in enumerate(moves):
    for j, b in enumerate(phases):
        P = base_pose(); choreo.MOVES[name](b + (1 if name in ('point_hit','spin','knee_drop') and j else 0) * 0 , P, **kw)
        m.draw(c, 130 + j * 260, 300 + i * 330, 260, P, O['michael'], L)
    c.drawString(name, 8, 30 + i * 330, font('spartan_b', 26), paint('#3a1e1a'))
surf.makeImageSnapshot().save('../build/moves.png', skia.kPNG)
