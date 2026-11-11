"""Comparison sheets: original / v8 / new, one row per item."""
import sys, json, pymupdf
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; oyc = float(sys.argv[2]); R = float(sys.argv[3])
art = json.load(open("emblem.json")); side = art["width"]
srcs = [("Ozgun", S + "/orig_v2.pdf", 0.0, 0.0), ("v8", "../Yeniden Olusturulan/ALFA 8084 - Amblem v8.ai", 19.0, 9.33),
        ("Yeni (v10 taslak)", "emblem_check.pdf", side / 2 - 188.5, side / 2 - oyc)]
items = [("1 Basin arka cizgisi", 190, 45, 270, 100), ("2 Burun on yuzu - ust dudak", 265, 55, 320, 110),
         ("3 + 16 Kapali goz / bakis", 172, 55, 272, 125), ("4 Sol yele kivrimi", 158, 95, 218, 205),
         ("5 Agiz kosesi mavi uc", 268, 100, 312, 140), ("6 Cene on ust ucu", 285, 100, 330, 142),
         ("7 Cene alt kosesi", 275, 120, 330, 170), ("8 Bogaz alti mavi uc", 250, 155, 300, 195),
         ("9 Boyun bicagi", 205, 135, 265, 205), ("10 Centik - buz yele arasi", 30, 115, 115, 205),
         ("11 Buz yele alt ucu", 35, 190, 105, 255), ("12 Kesim koseleri (sag)", 265, 160, 360, 300),
         ("13 8084 paneli", 100, 285, 290, 400), ("14 ROBOTICS", 80, 240, 355, 350), ("15 Daire - 6 teget", -15, 0, 392, 400)]
font = ImageFont.truetype("arial.ttf", 22); fb = ImageFont.truetype("arialbd.ttf", 26)
PH = 380
rows = []
for nm, x0, y0, x1, y1 in items:
    ims = []
    for lab, pdf, ox, oy in srcs:
        pg = pymupdf.open(pdf)[0]
        if nm.startswith("15") and lab != "Ozgun":
            pg.draw_circle(pymupdf.Point(188.5 + ox, (oyc if lab.startswith("Yeni") else 198.17) + oy), R if lab.startswith("Yeni") else 193.6864, color=(0.9, 0, 0.47), width=0.6)
        z = PH / (y1 - y0)
        pm = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(x0 + ox, y0 + oy, x1 + ox, y1 + oy), alpha=False)
        im = Image.frombytes("RGB", (pm.w, pm.h), pm.samples)
        ims.append((lab, im))
    w = sum(i.width for _, i in ims) + 20 * 4
    row = Image.new("RGB", (w, PH + 80), "white"); d = ImageDraw.Draw(row)
    d.text((20, 6), nm, fill=(200, 0, 0), font=fb)
    x = 20
    for lab, im in ims:
        d.text((x, 44), lab, fill=(60, 60, 60), font=font); row.paste(im, (x, 76)); d.rectangle((x, 76, x + im.width - 1, 76 + PH - 1), outline=(170, 170, 170)); x += im.width + 20
    rows.append(row)
for k, grp in enumerate((rows[0:4], rows[4:8], rows[8:11], rows[11:13], rows[13:15])):
    W = max(r.width for r in grp); H = sum(r.height for r in grp)
    pgm = Image.new("RGB", (W, H), "white"); y = 0
    for r in grp:
        pgm.paste(r, (0, y)); y += r.height
    pgm.save("%s/karsilastirma_%d.png" % (S, k + 1)); print(pgm.size)
