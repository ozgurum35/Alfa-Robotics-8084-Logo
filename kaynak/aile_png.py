# v10 logo family: PNGs from the PDFs made by aile_v10.jsx, SVG <title>, profile pictures and favicons.
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

# 3. favicons from the icon (colour); tiny sizes use the artboard without its margin
F = ROOT + "Favicon/"
os.makedirs(F, exist_ok=True)
ic = ROOT + "Simge/Renkli/ALFA 8084 - Simge v10 - Renkli.pdf"
big = square(ic, 512, 1.10, (0, 0, 0, 0))
big.save(F + "ALFA 8084 - Simge 512px.png")
square(ic, 180, 1.10, (255, 255, 255, 255)).convert("RGB").save(F + "apple-touch-icon 180px.png")
square(ic, 256, 1.20, (0, 0, 0, 0)).save(F + "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
for s in (16, 32, 48):
    square(ic, s * 8, 1.20, (0, 0, 0, 0)).resize((s, s), Image.LANCZOS).save(f"{F}favicon {s}px.png")
print("profil + favicon ok")
