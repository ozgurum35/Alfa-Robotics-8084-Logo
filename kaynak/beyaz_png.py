# Render white-background PNGs from the PDFs made by export_v10_beyaz.jsx and print the margins (px).
import pymupdf
from PIL import Image, ImageChops

OUT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/v10 disa aktarim/beyaz zemin/"
for n in ["ALFA 8084 - Amblem v10", "ALFA 8084 - Yazi Logo v10"]:
    base = OUT + n + " beyaz zemin"
    page = pymupdf.open(base + ".pdf")[0]
    for w in [512, 1024, 2048, 4096]:
        z = w / page.rect.width
        f = f"{base} {w}px.png"
        page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False).save(f)
        im = Image.open(f).convert("RGB")
        W, H = im.size
        mask = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 8 else 0)
        l, t, r, b = mask.getbbox()
        print(f"{n} {W}x{H}  L {l}  T {t}  R {W - r}  B {H - b}")
