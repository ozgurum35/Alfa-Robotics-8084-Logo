# logo family (v11.1): PNGs from the PDFs made by aile_v10.jsx, SVG <title> and profile pictures.
import glob, os, re
import pymupdf
from PIL import Image

ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/v11.1 surum ailesi/"
NAVY = (0, 58, 111)


def render(pdf, width):
    page = pymupdf.open(pdf)[0]
    z = width / page.rect.width
    p = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True)
    return Image.frombytes("RGBA", (p.width, p.height), p.samples)


# emblem artboard and profile circle come from design5.py (kaynak/emblem.json): a square centred on the shield axis and
# midway between nose top and shield tip; "circle" = centre and radius RF of the frame circle, whose centre sits where
# nose top and shield tip are vertically, and both outer A tips horizontally, equally far from the profile circle.
import json
_E = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "emblem.json")))
SIDE_, (CX_, CY_, RF_) = float(_E["width"]), _E["circle"]


def profile(pdf, size, bg, border=0.0, reach=0.46):
    """Profile picture: frame circle centred on the canvas, radius = `reach` x side (profile circle = RF / 0.92 at the
    default). `border` = white outline (pt) of the dark version, kept inside the same circle."""
    k = reach * size / RF_                                # px per pt
    im = render(pdf, round(SIDE_ * k))
    c = Image.new("RGBA", (size, size), bg)
    c.alpha_composite(im, (round(size / 2 - CX_ * k), round(size / 2 - CY_ * k)))
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
    if "<title" not in s:
        name = os.path.basename(base).replace("ALFA 8084 - ", "ALFA Robotics 8084 ")
        s = re.sub(r"(<svg\b[^>]*?)>", r'\1 role="img" aria-labelledby="t">' + f'\n<title id="t">{name}</title>', s, count=1)
        open(svg, "w", encoding="utf-8", newline="\n").write(s)
    print(os.path.basename(base))

# 2. profile pictures: emblem centred on its landmarks inside the circular crop
P = ROOT + "Profil/"
os.makedirs(P, exist_ok=True)
em = ROOT + "Amblem/Renkli/ALFA 8084 - Amblem v11.1 - Renkli.pdf"
emd = ROOT + "Amblem/Koyu zemin/ALFA 8084 - Amblem v11.1 - Koyu zemin.pdf"
for size in (400, 1080, 2048, 4096):
    # artboard has a 10% margin on each side: 0.86 / (1 - 2 * 0.0833) keeps the art at ~86% of the side
    profile(em, size, (255, 255, 255, 255)).convert("RGB").save(f"{P}ALFA 8084 - Profil beyaz {size}px.png")
    profile(emd, size, NAVY + (255,), border=8.0).convert("RGB").save(f"{P}ALFA 8084 - Profil lacivert {size}px.png")

print("profil ok")
