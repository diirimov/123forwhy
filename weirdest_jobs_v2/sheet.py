import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 7
fs = sorted(glob.glob(d + '/*.jpg'), key=lambda p: float(os.path.basename(p)[1:-4]))
w, h = 270, 480
rows = (len(fs) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 24)), (0, 0, 0)); D = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    im = Image.open(f).resize((w, h)); x, y = (i % cols) * w, (i // cols) * (h + 24)
    S.paste(im, (x, y + 24)); D.text((x + 6, y + 4), os.path.basename(f)[1:-4] + 's', fill=(255, 255, 0))
S.save(out, quality=85)
