# Test sheets for the v10 review report (size ladder, backgrounds, colour-vision, mono, avatar crop) + measurements.
import pymupdf, numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageOps
E = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/v10 disa aktarim/"
OUT = "D:/CLAUDE/Alfa Logo/kaynak/v10_calisma/rapor2/"
L = {"Amblem": E + "ALFA 8084 - Amblem v10.pdf", "Yazi": E + "ALFA 8084 - Yazi Logo v10.pdf"}
NAVY, SKY, ICE = (0, 58, 111), (99, 196, 242), (208, 233, 232)
FONT = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)

def render(pdf, width):
    pg = pymupdf.open(pdf)[0]; z = width / pg.rect.width
    p = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True)
    return Image.frombytes("RGBA", (p.width, p.height), p.samples)

def on(img, bg):
    b = Image.new("RGBA", img.size, bg + (255,)); b.alpha_composite(img); return b.convert("RGB")

def label(im, text, h=34):
    c = Image.new("RGB", (max(im.width, 10), im.height + h), "white"); c.paste(im, (0, h))
    ImageDraw.Draw(c).text((4, 4), text, fill=(30, 30, 30), font=FONT); return c

def row(ims, gap=24, bg="white"):
    W = sum(i.width for i in ims) + gap * (len(ims) + 1); H = max(i.height for i in ims) + 2 * gap
    c = Image.new("RGB", (W, H), bg); x = gap
    for i in ims: c.paste(i, (x, gap)); x += i.width + gap
    return c

def col(ims, gap=10):
    W = max(i.width for i in ims); H = sum(i.height for i in ims) + gap * (len(ims) - 1)
    c = Image.new("RGB", (W, H), "white"); y = 0
    for i in ims: c.paste(i, (0, y)); y += i.height + gap
    return c

# 1. size ladder: real pixels, shown x4 nearest
for k, pdf in L.items():
    ims = []
    for w in [16, 24, 32, 48, 64, 96, 128]:
        im = on(render(pdf, w), (255, 255, 255))
        ims.append(label(im.resize((im.width * 4, im.height * 4), Image.NEAREST), f"{w} px"))
    row(ims).save(OUT + f"1_boyut_{k}.png")

# 2. backgrounds
bgs = [("Beyaz", (255, 255, 255)), ("Açık gri", (245, 245, 245)), ("Lacivert", NAVY), ("Siyah", (17, 17, 17)), ("Açık mavi", SKY), ("Kırmızı", (200, 30, 45))]
for k, pdf in L.items():
    im = render(pdf, 300)
    row([label(on(im, c), n) for n, c in bgs], bg=(255, 255, 255)).save(OUT + f"2_zemin_{k}.png")

# 3. colour vision (Machado 2009, severity 1.0) + greyscale
M = {"Protanopi": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
     "Döteranopi": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
     "Tritanopi": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}
def lin(a): a = a / 255; return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
def srgb(a): a = np.clip(a, 0, 1); return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055) * 255
def cvd(rgb, m): a = lin(np.asarray(rgb, float)); return Image.fromarray(srgb(a @ np.array(m).T).astype(np.uint8))
im = on(render(L["Amblem"], 300), (255, 255, 255))
cells = [label(im, "Normal"), label(ImageOps.grayscale(im).convert("RGB"), "Gri ton")] + [label(cvd(im, m), n) for n, m in M.items()]
row(cells).save(OUT + "3_renk_gorme.png")

# 4. single colour: navy ink only (sky + ice become paper) and reversed white
a = np.asarray(im).astype(int)
def nearest(a):
    P = np.array([NAVY, SKY, ICE, (255, 255, 255)]); d = ((a[..., None, :] - P) ** 2).sum(-1); return d.argmin(-1)
idx = nearest(a)
mono = np.where(idx[..., None] == 0, NAVY, (255, 255, 255)).astype(np.uint8)
rev = np.where(idx[..., None] == 0, (255, 255, 255), NAVY).astype(np.uint8)
row([label(Image.fromarray(mono), "Tek renk: lacivert mürekkep"), label(Image.fromarray(rev), "Tek renk ters: beyaz")]).save(OUT + "4_tek_renk.png")

# 5. avatar crop (circle) 400 px
cells = []
for n, scale in [("Tam amblem", 1.0), ("Daireye sığdırılmış", 0.86)]:
    av = Image.new("RGB", (400, 400), "white"); e = render(L["Amblem"], int(400 * scale))
    av.paste(on(e, (255, 255, 255)), ((400 - e.width) // 2, (400 - e.height) // 2))
    m = Image.new("L", (400, 400), 0); ImageDraw.Draw(m).ellipse((0, 0, 399, 399), fill=255)
    out = Image.new("RGB", (400, 400), (230, 230, 230)); out.paste(av, (0, 0), m); cells.append(label(out, n))
row(cells).save(OUT + "5_profil.png")

# measurements
def lum(c): r, g, b = lin(np.array(c, float)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def cr(a, b): la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
pairs = {"Lacivert/beyaz": (NAVY, (255,) * 3), "Lacivert/açık mavi": (NAVY, SKY), "Lacivert/buz": (NAVY, ICE), "Açık mavi/beyaz": (SKY, (255,) * 3),
         "Buz/beyaz": (ICE, (255,) * 3), "Açık mavi/buz": (SKY, ICE), "Lacivert/siyah #111": (NAVY, (17,) * 3), "Lacivert/lacivert zemin": (NAVY, NAVY)}
for n, (x, y) in pairs.items(): print(f"kontrast {n}: {cr(x, y):.2f}")
big = on(render(L["Amblem"], 1200), (255, 255, 255)); idx = nearest(np.asarray(big).astype(int)); ink = (idx < 3).sum()
for i, n in enumerate(["lacivert", "açık mavi", "buz"]): print(f"alan {n}: {100 * (idx == i).sum() / ink:.1f} %")
# ROBOTICS cap height and 8084 height in px at given emblem widths (pt values from NOTLAR: ROBOTICS 13.5, 8084 18.5, art width 346 pt)
for w in [64, 120, 128, 200, 256]:
    s = w / 346.0; print(f"{w}px genişlik: ROBOTICS {13.5 * s:.1f}px, 8084 {18.5 * s:.1f}px, iç hat 8pt={8 * s:.1f}px")
for mm in [25, 35, 50]:
    s = mm / 25.4 * 72 / 346.0; print(f"baskı {mm} mm: ROBOTICS {13.5 * s * 25.4 / 72:.2f} mm, 8pt hat {8 * s * 25.4 / 72:.2f} mm")
