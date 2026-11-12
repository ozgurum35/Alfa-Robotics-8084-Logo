# v10 logo family: PNGs from the PDFs made by aile_v10.jsx, SVG <title> and profile pictures.
import glob, os, re
import pymupdf
from PIL import Image

ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/v10 surum ailesi/"
NAVY = (0, 58, 111)


def render(pdf, width):
    page = pymupdf.open(pdf)[0]
    z = width / page.rect.width
    p = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True)
    return Image.frombytes("RGBA", (p.width, p.height), p.samples)


def square(pdf, size, fill, bg):
    """Logo centred on a square canvas; `fill` = share of the side the logo's longer edge takes."""
    page = pymupdf.open(pdf)[0]
    w = size * fill * page.rect.width / max(page.rect.width, page.rect.height)
    im = render(pdf, round(w))
    c = Image.new("RGBA", (size, size), bg)
    c.alpha_composite(im, ((size - im.width) // 2, (size - im.height) // 2))
    return c


# 1. transparent PNGs + SVG title for every variant
for pdf in sorted(glob.glob(ROOT + "*/*/*.pdf")):
    if pdf.endswith("CMYK.pdf"):
        continue
    base = pdf[:-4]
    for w in (512, 1024, 2048, 4096):
        render(pdf, w).save(f"{base} {w}px.png", optimize=True)
    svg = base + ".svg"
    s = open(svg, encoding="utf-8").read()
    if "<title>" not in s:
        name = os.path.basename(base).replace("ALFA 8084 - ", "ALFA Robotics 8084 ")
        s = re.sub(r"(<svg\b[^>]*?)>", r'\1 role="img" aria-labelledby="t">' + f'\n<title id="t">{name}</title>', s, count=1)
        open(svg, "w", encoding="utf-8", newline="\n").write(s)
    print(os.path.basename(base))

# 2. profile pictures: emblem fits inside a circular crop (86% of the side)
P = ROOT + "Profil/"
os.makedirs(P, exist_ok=True)
em = ROOT + "Amblem/Renkli/ALFA 8084 - Amblem v10 - Renkli.pdf"
emd = ROOT + "Amblem/Koyu zemin/ALFA 8084 - Amblem v10 - Koyu zemin.pdf"
for size in (400, 1080):
    # artboard has a 10% margin on each side: 0.86 / (1 - 2 * 0.0833) keeps the art at ~86% of the side
    square(em, size, 1.03, (255, 255, 255, 255)).convert("RGB").save(f"{P}ALFA 8084 - Profil beyaz {size}px.png")
    square(emd, size, 1.03, NAVY + (255,)).convert("RGB").save(f"{P}ALFA 8084 - Profil lacivert {size}px.png")

print("profil ok")
