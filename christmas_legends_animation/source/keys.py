import sys, skia, time, traceback
sys.argv=[sys.argv[0]]+sys.argv[1:]
from gfx import *
import main as M
times=[float(x) for x in sys.argv[2].split(',')]
out=sys.argv[1]
cols=4; tw,th=W//4,H//4
rows=(len(times)+cols-1)//cols
sheet=skia.Surface(tw*cols,th*rows); c=sheet.getCanvas(); c.clear(skia.ColorBLACK)
for i,t in enumerate(times):
    try:
        t0=time.time(); s=M.frame(t); dt=time.time()-t0
        im=s.makeImageSnapshot()
        c.save(); c.translate((i%cols)*tw,(i//cols)*th); c.scale(0.25,0.25); c.drawImage(im,0,0); c.restore()
        draw_text(c,f'{t:.2f}s',(i%cols)*tw+60,(i//cols)*th+40,30,'fredoka-600.ttf','#ffff00','#000000',3)
        print(f'{t:.2f} ok {dt:.2f}s')
    except Exception as e:
        traceback.print_exc(); print(t,'FAIL')
sheet.makeImageSnapshot().save(out)
