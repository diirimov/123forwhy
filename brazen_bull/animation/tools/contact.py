import sys, glob
from PIL import Image, ImageDraw
out, cols, *files = sys.argv[1:]; cols = int(cols)
labels = [f.split('=')[1] if '=' in f else '' for f in files]; files = [f.split('=')[0] for f in files]
w, h = 360, 640; rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * h), (20, 20, 20)); d = ImageDraw.Draw(sheet)
for i, (f, l) in enumerate(zip(files, labels)):
    im = Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS); x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(im, (x, y)); d.rectangle([x, y, x + 70, y + 22], fill=(0, 0, 0)); d.text((x + 4, y + 4), l, fill=(255, 220, 120))
sheet.save(out)
