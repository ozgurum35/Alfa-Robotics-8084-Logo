"""Raster mock-up: light-blue inner line along the frame where the wolf body merges with it."""
import sys, runpy, math
import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont

FONT = "E:/2026 masaüstü/Classic Robot/Classic Robot Bold Italic.otf"
sys.argv = ["design5.py", ".", FONT]
g = runpy.run_path("design5.py")
V, anchors, sample, shield = g["V"], g["anchors"], g["sample"], g["shield"]
WF, PIN, nUp, dU, Xd = g["WF"], g["PIN"], g["nUp"], g["dU"], g["Xd"]
LT, GAP = 3.5, 3.0
OFF = V(19.0, 9.33)
Z = 3.0
SKY, NAVY, ICE = (71, 185, 239), (0, 58, 111), (235, 247, 252)

pg = pymupdf.open("emblem_check.pdf")[0]
px = pg.get_pixmap(matrix=pymupdf.Matrix(Z, Z))
base = np.frombuffer(px.samples, np.uint8).reshape(px.h, px.w, px.n)[..., :3].copy()
H, W = base.shape[:2]


def poly_mask(pts):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon([tuple((p + OFF) * Z) for p in pts], fill=1)
    return np.array(im, bool)


yy, xx = np.mgrid[0:H, 0:W]
X, Y = xx / Z - OFF[0], yy / Z - OFF[1]
above = (X - PIN[0]) * nUp[0] + (Y - PIN[1]) * nUp[1]          # distance above the inner cut line
inner = poly_mask(sample(anchors(shield(WF)[0]), 40))
inner2 = poly_mask(sample(anchors(shield(WF + LT)[0]), 40))
inner3 = poly_mask(sample(anchors(shield(WF + LT + GAP)[0]), 40))
is_ice = np.abs(base.astype(int) - ICE).max(axis=2) < 40

ringL = inner & ~inner2 & (above > 0) & (X < 120) & (Y > 119.0)
gapL = inner2 & ~inner3 & (above > 0) & (X < 120) & (Y > 119.0) & is_ice
A = base.copy()
A[gapL] = NAVY
A[ringL] = SKY

along = (X - PIN[0]) * dU[0] + (Y - PIN[1]) * dU[1]
xd = (Xd - PIN) @ dU
bandB = inner & (above >= 0) & (above < LT) & (along < xd)
gapB = inner & (above >= LT) & (above < LT + GAP) & (along < xd) & is_ice
B = A.copy()
B[gapB] = NAVY
B[bandB] = SKY

# side by side, upper half only
y1 = int((262 + OFF[1]) * Z)
panels = [("Simdiki (v8)", base[:y1]), ("A: sadece sol kenar", A[:y1]), ("B: sol kenar + alt kesim", B[:y1])]
pad, top = 20, 50
out = Image.new("RGB", (len(panels) * (W + pad) + pad, y1 + top + pad), (255, 255, 255))
d = ImageDraw.Draw(out)
try:
    f = ImageFont.truetype("arial.ttf", 30)
except OSError:
    f = None
for k, (t, im) in enumerate(panels):
    x0 = pad + k * (W + pad)
    out.paste(Image.fromarray(im), (x0, top))
    d.text((x0 + 10, 10), t, fill=(0, 0, 0), font=f)
out.save("D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/ALFA 8084 - ic hat secenekleri.png")
print("ok", out.size)
