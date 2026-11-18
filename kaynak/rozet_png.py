# PNGs of the badge sheets (kaynak/rozet.jsx) rendered from the RGB PDFs at 300 and 600 dpi, plus a check:
# logo diameter and centring of every badge, measured on the 600 dpi render.
import pymupdf
import numpy as np
from PIL import Image
from guncel_logo import VER, ROOT

OUT = f"{ROOT}Rozet {VER}/"
CENTRES = [(x, y) for y in (68.5, 148.5, 228.5) for x in (65.0, 145.0)]  # mm, rozet.jsx layout

for name, bg in (("Beyaz zemin", (255, 255, 255)), ("Lacivert zemin", (0, 58, 111))):
    base = f"{OUT}ALFA 8084 - Rozet A4 70 mm {VER} - {name}"
    # Illustrator's SVG has only a pt viewBox; give it the real A4 size so it prints / opens at 210 x 297 mm
    svg = open(base + ".svg", encoding="utf-8").read()
    if 'width="210mm"' not in svg:
        svg = svg.replace('viewBox="0 0 595.276 841.89"', 'width="210mm" height="297mm" viewBox="0 0 595.276 841.89"', 1)
        open(base + ".svg", "w", encoding="utf-8").write(svg)
    page = pymupdf.open(base + ".pdf")[0]
    for dpi in (300, 600):
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        pix.set_dpi(dpi, dpi)
        pix.save(f"{base} {dpi}dpi.png")
    im = np.asarray(Image.open(f"{base} 600dpi.png").convert("RGB")).astype(int)
    px = 600 / 25.4
    for cx, cy in CENTRES:
        x0, y0 = round((cx - 30) * px), round((cy - 30) * px)
        sub = im[y0:y0 + round(60 * px), x0:x0 + round(60 * px)]
        ys, xs = np.nonzero(np.abs(sub - bg).sum(2) > 60)
        d = np.hypot((xs + x0 + .5) / px - cx, (ys + y0 + .5) / px - cy)
        keep = d < 32  # leave out the cut ring and the paper outside the navy disc
        xs, d = xs[keep], d[keep]
        print(f"{name} ({cx:.0f},{cy:.0f}) mm: logo diameter {2 * d.max():.2f} mm, "
              f"horizontal bounds {(xs.min() + x0) / px - cx:+.2f} / {(xs.max() + x0) / px - cx:+.2f} mm")
