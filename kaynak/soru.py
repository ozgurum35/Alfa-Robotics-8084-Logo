"""One question sheet: soru.py out.png title x0 y0 x1 y1 height  label=pdf ..."""
import sys, pymupdf
from PIL import Image, ImageDraw, ImageFont
out, title = sys.argv[1], sys.argv[2]
x0, y0, x1, y1, PH = map(float, sys.argv[3:8])
OFF = {"ozgun": (0.0, 0.0), "v8": (19.0, 9.33)}
font = ImageFont.truetype("arialbd.ttf", 26); fb = ImageFont.truetype("arialbd.ttf", 30)
ims = []
for spec in sys.argv[8:]:
    lab, pdf = spec.split("=", 1)
    key = "ozgun" if "orig" in pdf else ("v8" if "v8" in pdf else None)
    import os
    if key:
        ox, oy = OFF[key]
    elif os.path.exists(pdf + ".off"):
        cx, cy = map(float, open(pdf + ".off").read().split()); ox, oy = 208.0 - cx, 208.0 - cy
    else:
        ox, oy = (19.5, 208.0 - 198.61)
    z = PH / (y1 - y0)
    pm = pymupdf.open(pdf)[0].get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0 + ox, y0 + oy, x1 + ox, y1 + oy), alpha=False)
    ims.append((lab, Image.frombytes("RGB", (pm.w, pm.h), pm.samples)))
cols = 2 if len(ims) == 4 else len(ims)
w, h = ims[0][1].size
rowsn = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + 20) + 20, 60 + rowsn * (h + 60)), "white"); d = ImageDraw.Draw(sheet)
d.text((20, 12), title, fill=(200, 0, 0), font=fb)
for k, (lab, im) in enumerate(ims):
    x, y = 20 + (k % cols) * (w + 20), 60 + (k // cols) * (h + 60)
    d.text((x, y + 6), lab, fill=(40, 40, 40), font=font); sheet.paste(im, (x, y + 44)); d.rectangle((x, y + 44, x + w - 1, y + 44 + h - 1), outline=(150, 150, 150))
sheet.save(out)
