# Logo usage guide (A4 PDF) for the v10 logo family: which file for which job (with links that open the file
# on GitHub), variants, colours (HEX / RGB / CMYK / Pantone), clear space, minimum size, don'ts.
# usage: python kilavuz.py [tag]   (links point to the files at this git tag, default v10.1)
import os, shutil, sys
from urllib.parse import quote
import pymupdf
from PIL import Image, ImageDraw, ImageFont

TAG = sys.argv[1] if len(sys.argv) > 1 else "v10.2"
REPO = "https://github.com/ozgurum35/Alfa-Robotics-8084-Logo"
REL = "Yeniden Olusturulan/v10 surum ailesi/"
ROOT = "D:/CLAUDE/Alfa Logo/" + REL
OUT = ROOT + "ALFA 8084 - Logo Kullanim Kilavuzu.pdf"
IMG = "D:/CLAUDE/Alfa Logo/kaynak/v10_calisma/kilavuz_img/"
os.makedirs(IMG, exist_ok=True)
for f in ("segoeui.ttf", "segoeuib.ttf"):
    shutil.copy("C:/Windows/Fonts/" + f, IMG + f)
NAVY, SKY, ICE, WHITE = (0, 58, 111), (99, 196, 242), (208, 233, 232), (255, 255, 255)
EM, WM, YT = "Amblem", "Yazi Logo", "Yatay Logo"


def fname(folder, variant, suffix):
    label = "Yazi Logo" if folder == WM else folder
    return f"{folder}/{variant}/ALFA 8084 - {label} v10 - {variant}{suffix}"


def url(rel):  # opens / downloads the file itself
    assert os.path.exists(ROOT + rel), rel
    return f"{REPO}/raw/{TAG}/{quote(REL + rel)}"


def tree(rel):  # opens the folder on GitHub (all formats of one variant)
    assert os.path.isdir(ROOT + rel), rel
    return f"{REPO}/tree/{TAG}/{quote(REL + rel)}"


def links(folder, variant, kinds=("ai", "pdf", "cmyk", "svg", "png")):
    L = {"ai": ("AI", ".ai"), "pdf": ("PDF", ".pdf"), "cmyk": ("Baskı CMYK PDF", " - Baski CMYK.pdf"), "svg": ("SVG", ".svg"),
         "png": ("PNG 1024", " 1024px.png"), "png2": ("PNG 2048", " 2048px.png"), "png4": ("PNG 4096", " 4096px.png"), "png5": ("PNG 512", " 512px.png")}
    return " · ".join(f'<a href="{url(fname(folder, variant, L[k][1]))}">{L[k][0]}</a>' for k in kinds)


def card(src, bg, name, size=(520, 300), border=False):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((size[0] - 40, size[1] - 40))
    c = Image.new("RGBA", size, bg + (255,))
    c.alpha_composite(im, ((size[0] - im.width) // 2, (size[1] - im.height) // 2))
    if border:
        ImageDraw.Draw(c).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=(210, 216, 222), width=2)
    c.convert("RGB").save(IMG + name)
    return name


# ---------- images ----------
VARIANTS = [  # folder, variant, background, title, where
    (EM, "Renkli", WHITE, "Amblem – Renkli (ana logo)",
     ["Beyaz ve açık renkli zeminler", "Web sitesi, belge, sunum, afiş", "Açık renk forma ve tişört"]),
    (EM, "Koyu zemin", NAVY, "Amblem – Koyu zemin",
     ["Lacivert, siyah, koyu renkli zeminler", "Koyu forma, tişört, pankart", "Koyu fotoğraf üstü; beyaz kenar logoyu ayırır"]),
    (EM, "Tek renk lacivert", WHITE, "Amblem – Tek renk lacivert",
     ["Tek renk baskı, damga, fotokopi", "Nakış, lazer kazıma, serigrafi", "Açık zemin"]),
    (EM, "Tek renk beyaz", NAVY, "Amblem – Tek renk beyaz",
     ["Koyu zeminde tek renk", "Beyaz serigrafi, folyo kesim", "Cam / araç etiketi, koyu kumaşa nakış"]),
    (WM, "Renkli", WHITE, "Yazı Logo – Renkli",
     ["ROBOTICS harfleri beyaz dolgulu", "Yatay ve dar alanlar", "Antetli kâğıt, e-posta imzası", "Sunum alt bilgisi, robot gövdesi"]),
    (WM, "Tek renk lacivert", WHITE, "Yazı Logo – Tek renk lacivert",
     ["ROBOTICS harfleri boş (zemin görünür)", "Tek renk baskı, açık zemin", "Lazer kazıma, damga"]),
    (WM, "Tek renk beyaz", NAVY, "Yazı Logo – Tek renk beyaz",
     ["Koyu zemin: lacivert, siyah, koyu fotoğraf", "Koyu forma, beyaz serigrafi"]),
    (YT, "Renkli", WHITE, "Yatay Logo – Renkli",
     ["Amblem ve yazı yan yana", "Web sitesi başlığı, e-posta imzası", "Antetli kâğıt, sunum, afiş başlığı"]),
    (YT, "Koyu zemin", NAVY, "Yatay Logo – Koyu zemin",
     ["Beyaz kenarlı amblem + beyaz yazı", "Koyu web teması, banner, pankart", "Sosyal medya kapak görseli, koyu forma"]),
    (YT, "Tek renk lacivert", WHITE, "Yatay Logo – Tek renk lacivert",
     ["Tek renk baskı, açık zemin", "Lazer kazıma, damga, belge"]),
    (YT, "Tek renk beyaz", NAVY, "Yatay Logo – Tek renk beyaz",
     ["Koyu zeminde tek renk", "Beyaz serigrafi, folyo kesim, nakış"]),
]
cards = []
for i, (f, v, bg, title, where) in enumerate(VARIANTS):
    cards.append((card(ROOT + fname(f, v, " 1024px.png"), bg, f"v{i}.png", border=bg == WHITE), title, where,
                  links(f, v) + " · " + links(f, v, ("png4",)), tree(f"{f}/{v}")))
yatay_cards = cards[7:]; cards = cards[:7]
prof = " · ".join(f'<a href="{url("Profil/ALFA 8084 - Profil " + c + " " + s + "px.png")}">{c.capitalize()} {s}</a>'
                  for c in ("beyaz", "lacivert") for s in ("400", "1080"))
cards.append((card(ROOT + "Profil/ALFA 8084 - Profil beyaz 1080px.png", (236, 240, 244), "p7.png"), "Profil fotoğrafı",
              ["Instagram, X, LinkedIn, YouTube, WhatsApp", "Kare; yuvarlak kırpmaya hazır", "Beyaz ve lacivert zeminli"], prof, tree("Profil")))
card(ROOT + fname(EM, "Koyu zemin", " 512px.png"), NAVY, "logo_head.png", size=(200, 200))

# clear space diagram
src = Image.open(ROOT + fname(EM, "Renkli", " 2048px.png")).convert("RGBA")   # artboard already has the 10% margin
cs = Image.new("RGBA", src.size, WHITE + (255,)); cs.alpha_composite(src)
d = ImageDraw.Draw(cs); W, H = src.size; m = round(max(W, H) / 1.2 * 0.10)
for x in range(0, W, 28):
    d.line((x, m, min(x + 14, W), m), fill=(230, 0, 120), width=4); d.line((x, H - m, min(x + 14, W), H - m), fill=(230, 0, 120), width=4)
for y in range(0, H, 28):
    d.line((m, y, m, min(y + 14, H)), fill=(230, 0, 120), width=4); d.line((W - m, y, W - m, min(y + 14, H)), fill=(230, 0, 120), width=4)
fnt = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 64)
for (x, y) in ((m // 2, H // 2), (W - m // 2, H // 2), (W // 2, m // 2), (W // 2, H - m // 2)):
    d.text((x, y), "x", fill=(230, 0, 120), font=fnt, anchor="mm")
ImageDraw.Draw(cs).rectangle((0, 0, W - 1, H - 1), outline=(190, 198, 206), width=6)
cs.convert("RGB").resize((W // 4, H // 4), Image.LANCZOS).save(IMG + "clear.png")

for n, c in (("s0.png", NAVY), ("s1.png", SKY), ("s2.png", ICE)):
    Image.new("RGB", (160, 110), c).save(IMG + n)

# don'ts (made from the colour emblem)
base = Image.open(ROOT + fname(EM, "Renkli", " 512px.png")).convert("RGBA")
def mark(c):
    dr = ImageDraw.Draw(c); dr.ellipse((236, 10, 290, 64), fill=(210, 30, 40))
    dr.line((250, 24, 276, 50), fill=WHITE, width=7); dr.line((276, 24, 250, 50), fill=WHITE, width=7)
    dr.rectangle((0, 0, 299, 299), outline=(210, 216, 222), width=2)
    return c
def dont(img, bg, name):
    c = bg.copy() if isinstance(bg, Image.Image) else Image.new("RGBA", (300, 300), bg + (255,))
    img = img.copy(); img.thumbnail((250, 250))
    c.alpha_composite(img, ((300 - img.width) // 2, (300 - img.height) // 2))
    mark(c).convert("RGB").save(IMG + name)
dont(base.resize((512, 300)), WHITE, "d0.png")
dont(base.rotate(25, expand=True, resample=Image.BICUBIC), WHITE, "d1.png")
r, g, b, a = base.split(); dont(Image.merge("RGBA", (b, r, g, a)), WHITE, "d2.png")
dont(base, NAVY, "d3.png")
sh = Image.new("RGBA", (base.width + 40, base.height + 40), (0, 0, 0, 0))
shadow = Image.new("RGBA", base.size, (0, 0, 0, 255)); shadow.putalpha(a.point(lambda v: v // 2))
sh.alpha_composite(shadow, (34, 34)); sh.alpha_composite(base, (0, 0)); dont(sh, WHITE, "d4.png")
noise = Image.effect_noise((300, 300), 90).convert("L")
dont(base, Image.merge("RGB", (noise, noise.point(lambda v: 255 - v), noise.point(lambda v: v // 2))).convert("RGBA"), "d5.png")

# ---------- pages ----------
CSS = """
@font-face { font-family: tr; src: url(segoeui.ttf); }
@font-face { font-family: tr; font-weight: bold; src: url(segoeuib.ttf); }
* { font-family: tr; }
body { font-size: 9.5pt; color: #1d2733; line-height: 1.35; }
h2 { font-size: 14pt; color: #003A6F; margin: 0 0 6pt 0; }
h3 { font-size: 10.5pt; color: #003A6F; margin: 4pt 0 2pt 0; }
p { margin: 3pt 0 6pt 0; }
a { color: #0a6fb8; text-decoration: none; font-weight: bold; }
table { border-collapse: collapse; width: 100%; }
td, th { padding: 4pt 5pt; vertical-align: top; text-align: left; }
th { color: #ffffff; background-color: #003A6F; font-size: 9pt; }
tr.z td { background-color: #f2f5f8; }
td.c { width: 50%; padding: 0 8pt 10pt 0; }
td.t { width: 192pt; padding: 3pt 4pt; vertical-align: middle; }
ul { margin: 2pt 0 2pt 0; padding-left: 12pt; }
.lk { font-size: 8.5pt; }
.note { color: #5b6775; font-size: 8.5pt; }
.f { color: #003A6F; font-weight: bold; }
"""


def grid(items):
    rows = []
    for k in range(0, len(items), 2):
        cells = []
        for img, title, where, lk, folder in items[k:k + 2]:
            lis = "".join(f"<li>{w}</li>" for w in where)
            cells.append(f'<td class="c"><a href="{folder}"><img src="{img}" width="245"/></a><h3><a href="{folder}">{title} ›</a></h3><ul>{lis}</ul>'
                         f'<div class="lk"><a href="{folder}">Klasörü aç</a> &nbsp;|&nbsp; Dosya: {lk}</div></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table>" + "".join(rows) + "</table>"


def lk(folder, variant, kind):
    return links(folder, variant, (kind,))


NEED = [
    ("Matbaa: afiş, broşür, kartvizit, davetiye", "Amblem / Renkli", lk(EM, "Renkli", "cmyk")),
    ("Açık renk forma, tişört baskısı", "Amblem / Renkli", lk(EM, "Renkli", "cmyk")),
    ("Koyu renk forma, tişört, pankart", "Amblem / Koyu zemin", lk(EM, "Koyu zemin", "cmyk")),
    ("Tek renk serigrafi, damga (+ Pantone 654 C)", "Tek renk lacivert / beyaz", lk(EM, "Tek renk lacivert", "cmyk") + " · " + lk(EM, "Tek renk beyaz", "cmyk")),
    ("Nakış (forma, şapka, çanta)", "Tek renk lacivert / beyaz", lk(EM, "Tek renk lacivert", "ai") + " · " + lk(EM, "Tek renk beyaz", "ai")),
    ("Lazer kesim / kazıma, folyo kesim, CNC", "Tek renk lacivert", lk(EM, "Tek renk lacivert", "svg")),
    ("Web sitesi başlığı (açık / koyu tema)", "Yatay Renkli / Koyu zemin", lk(YT, "Renkli", "svg") + " · " + lk(YT, "Koyu zemin", "svg")),
    ("Banner, pankart, sosyal medya kapak görseli", "Yatay Renkli / Koyu zemin", lk(YT, "Renkli", "png4") + " · " + lk(YT, "Koyu zemin", "png4")),
    ("Sunum, Word, Canva (açık / koyu slayt)", "Renkli / Koyu zemin", lk(EM, "Renkli", "png") + " · " + lk(EM, "Koyu zemin", "png")),
    ("Sosyal medya profil fotoğrafı", "Profil", f'<a href="{url("Profil/ALFA 8084 - Profil beyaz 1080px.png")}">Beyaz 1080</a> · <a href="{url("Profil/ALFA 8084 - Profil lacivert 1080px.png")}">Lacivert 1080</a>'),
    ("Sosyal medya gönderisi, video", "Renkli / Koyu zemin", lk(EM, "Renkli", "png2") + " · " + lk(EM, "Koyu zemin", "png2")),
    ("E-posta imzası, antetli kâğıt", "Yatay Logo / Renkli", lk(YT, "Renkli", "png5") + " · " + lk(YT, "Renkli", "cmyk")),
    ("Robot gövdesi, çıkartma (sticker)", "Amblem / Koyu zemin", lk(EM, "Koyu zemin", "cmyk")),
    ("Tasarımcıya, düzenleme için", "Amblem / Renkli", lk(EM, "Renkli", "ai")),
]
FOLD = {"Amblem / Renkli": "Amblem/Renkli", "Amblem / Koyu zemin": "Amblem/Koyu zemin", "Tek renk lacivert": "Amblem/Tek renk lacivert",
        "Profil": "Profil", "Yazı Logo / Renkli": "Yazi Logo/Renkli", "Yatay Logo / Renkli": "Yatay Logo/Renkli"}
def ver(b):
    if b in FOLD:
        return f'<a href="{tree(FOLD[b])}">{b}</a>'
    if b == "Tek renk lacivert / beyaz":
        return f'<a href="{tree("Amblem/Tek renk lacivert")}">Tek renk lacivert</a> / <a href="{tree("Amblem/Tek renk beyaz")}">beyaz</a>'
    if b == "Yatay Renkli / Koyu zemin":
        return f'Yatay <a href="{tree("Yatay Logo/Renkli")}">Renkli</a> / <a href="{tree("Yatay Logo/Koyu zemin")}">Koyu zemin</a>'
    if b == "Renkli / Koyu zemin":
        return f'<a href="{tree("Amblem/Renkli")}">Renkli</a> / <a href="{tree("Amblem/Koyu zemin")}">Koyu zemin</a>'
    raise KeyError(b)
THUMB = {"Amblem / Renkli": [("t0.png", "Amblem/Renkli")], "Amblem / Koyu zemin": [("t1.png", "Amblem/Koyu zemin")],
         "Tek renk lacivert": [("t2.png", "Amblem/Tek renk lacivert")],
         "Tek renk lacivert / beyaz": [("t2.png", "Amblem/Tek renk lacivert"), ("t3.png", "Amblem/Tek renk beyaz")],
         "Renkli / Koyu zemin": [("t0.png", "Amblem/Renkli"), ("t1.png", "Amblem/Koyu zemin")],
         "Profil": [("pw.png", "Profil"), ("pn.png", "Profil")], "Yazı Logo / Renkli": [("t4.png", "Yazi Logo/Renkli")],
         "Yatay Logo / Renkli": [("t5.png", "Yatay Logo/Renkli")],
         "Yatay Renkli / Koyu zemin": [("t5.png", "Yatay Logo/Renkli"), ("t6.png", "Yatay Logo/Koyu zemin")]}
# tight thumbnails for the need table: logo cropped to its ink, on a 240x150 card
for n, src, bg in (("t0.png", fname(EM, "Renkli", " 512px.png"), WHITE), ("t1.png", fname(EM, "Koyu zemin", " 512px.png"), NAVY),
                   ("t2.png", fname(EM, "Tek renk lacivert", " 512px.png"), WHITE), ("t3.png", fname(EM, "Tek renk beyaz", " 512px.png"), NAVY),
                   ("t4.png", fname(WM, "Renkli", " 512px.png"), WHITE), ("t5.png", fname(YT, "Renkli", " 512px.png"), WHITE),
                   ("t6.png", fname(YT, "Koyu zemin", " 512px.png"), NAVY), ("pw.png", "Profil/ALFA 8084 - Profil beyaz 400px.png", WHITE),
                   ("pn.png", "Profil/ALFA 8084 - Profil lacivert 400px.png", NAVY)):
    im = Image.open(ROOT + src).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox()) if "Profil" not in src else im
    c = Image.new("RGBA", (240, 150), bg + (255,)); im.thumbnail((216, 132))
    c.alpha_composite(im, ((240 - im.width) // 2, (150 - im.height) // 2))
    if bg == WHITE: ImageDraw.Draw(c).rectangle((0, 0, 239, 149), outline=(210, 216, 222), width=2)
    c.convert("RGB").save(IMG + n)
def thumbs(b):
    return "".join(f'<a href="{tree(f)}"><img src="{im}" width="92"/></a> ' for im, f in THUMB[b])
def need_table(rows):
    r = "".join(f'<tr class="{"z" if i % 2 else ""}"><td class="t">{thumbs(b)}</td><td>{a}</td><td>{ver(b)}</td><td>{c}</td></tr>' for i, (a, b, c) in enumerate(rows))
    return f'<table><tr><th style="width:192pt">Logo</th><th>İhtiyaç</th><th>Sürüm (klasörü açar)</th><th>Dosya (dosyayı açar)</th></tr>{r}</table>'
HALF = 6  # large thumbnails: the table runs over two pages

PAGES = [
    ("Hangi işe hangi dosya?", f"""
<p>İhtiyacınızı bulun ve <b>mavi bağlantıya</b> tıklayın (internet gerekir): <b>Sürüm</b> sütunu o sürümün klasörünü (bütün biçimler) GitHub'da açar, <b>Dosya</b> sütunu dosyanın kendisini açar veya indirir.
Aynı dosyalar ZIP paketinde de aynı klasör adlarıyla bulunur. Her sürüm <b>.ai</b>, <b>.pdf</b>, <b>Baski CMYK.pdf</b>, <b>.svg</b> ve
<b>512 / 1024 / 2048 / 4096 px .png</b> olarak vardır; hepsine sayfa 3–5'teki bağlantılardan ulaşabilirsiniz. Resme tıklamak da klasörü açar.</p>
{need_table(NEED[:HALF])}
"""),
    ("Hangi işe hangi dosya? (devam)", need_table(NEED[HALF:])),
    ("Logo sürümleri – Amblem", f"<p>Amblem takımın ana logosudur. Zeminin rengine göre sürümü seçin; bağlantılar dosyayı açar.</p>{grid(cards[:4])}"),
    ("Logo sürümleri – Yazı Logo ve Profil", f"<p>Yazı logo, amblemin sığmadığı yatay ve dar alanlar içindir.</p>{grid(cards[4:8])}"),
    ("Logo sürümleri – Yatay Logo", f"<p>Yatay logo amblem ile yazı logoyu yan yana birleştirir: geniş ve alçak alanlar (site başlığı, imza, banner) içindir. "
     f"Yazı, amblem yüksekliğinin %72'si; aradaki boşluk %16'sıdır. Parçaları kendiniz yan yana dizmeyin, bu dosyaları kullanın.</p>{grid(yatay_cards)}"),
    ("Renkler", """
<table>
<tr><th></th><th>Renk</th><th>HEX</th><th>RGB</th><th>CMYK<br/>(kuşe kâğıt)</th><th>Pantone<br/>(en yakın)</th></tr>
<tr><td><img src="s0.png" width="56"/></td><td><b>ALFA Lacivert</b><br/>ana renk</td><td>#003A6F</td><td>0 58 111</td><td>100 82 36 23</td><td><b>654 C</b><br/><span class="note">fark çok küçük</span></td></tr>
<tr class="z"><td><img src="s1.png" width="56"/></td><td><b>ALFA Açık Mavi</b><br/>ikincil renk</td><td>#63C4F2</td><td>99 196 242</td><td>58 4 1 0</td><td><b>297 C</b><br/><span class="note">fark fark edilebilir</span></td></tr>
<tr><td><img src="s2.png" width="56"/></td><td><b>ALFA Buz</b><br/>vurgu (kurt)</td><td>#D0E9E8</td><td>208 233 232</td><td>22 2 12 0</td><td><b>9502 C</b><br/><span class="note">fark küçük</span></td></tr>
</table>
<p class="note">CMYK değerleri Coated FOGRA39 (Avrupa kuşe kâğıt baskı standardı) için hesaplanmıştır ve Baskı CMYK PDF dosyalarında tanımlıdır.
Pantone eşleşmeleri ekran renginden hesaplanmış en yakın Solid Coated renklerdir (ΔE2000: 654 C 0,6 · 297 C 2,6 · 9502 C 1,6); resmî değildir.
Pantone ile baskı yaptıracaksanız (serigrafi, tekstil) baskıdan önce Pantone kartelasında renkleri gözle doğrulayın. Önemli baskılarda matbaadan renk provası isteyin.</p>
"""),
    ("Dosya biçimleri ve boyut", """<table>
<tr><th>Biçim</th><th>Ne için</th></tr>
<tr><td class="f">Baskı CMYK PDF</td><td>Matbaa ve tekstil baskısı. Renkler baskı mürekkebine (CMYK) göre tanımlı. Matbaaya her zaman bunu verin.</td></tr>
<tr class="z"><td class="f">PDF</td><td>Ekran renkli (RGB) vektör dosya: dijital belge, ofis yazıcısı.</td></tr>
<tr><td class="f">SVG</td><td>Web sitesi; lazer, folyo kesim ve CNC yazılımları. Vektör, her boyutta net.</td></tr>
<tr class="z"><td class="f">PNG</td><td>Ofis programları, Canva, sosyal medya, mesajlaşma. Saydam zemin. 512 px küçük, 1024 px sunum ve web, 2048 px büyük ekran, 4096 px yüksek çözünürlük. Kendi boyutundan büyütmeyin.</td></tr>
<tr><td class="f">AI</td><td>Adobe Illustrator kaynağı: düzenleme, nakışçıya ve tasarımcıya kaynak.</td></tr>
</table>
<h2 style="margin-top:12pt">Koruma alanı ve en küçük boyut</h2>
<table><tr><td style="width:240pt"><img src="clear.png" width="230"/></td><td>
<p><b>Koruma alanı (x):</b> logonun her yanında, logonun uzun kenarının en az %10'u kadar boş alan bırakın (yatay logoda yüksekliğin %10'u). Bu alana yazı, çizgi veya başka logo girmez.</p>
<p>Dosyalardaki kenar boşluğu tam bu kadardır; dosyayı kırpmadan kullanın.</p></td></tr></table>
<table>
<tr><th>Logo</th><th>Ekranda en az</th><th>Baskıda en az</th></tr>
<tr><td>Amblem</td><td>128 px genişlik</td><td>30 mm genişlik</td></tr>
<tr class="z"><td>Yazı Logo</td><td>128 px genişlik</td><td>30 mm genişlik</td></tr>
<tr><td>Yatay Logo</td><td>220 px genişlik</td><td>50 mm genişlik</td></tr>
</table>
<p class="note">Daha küçükte ROBOTICS ve 8084 okunmaz. Nakışta en az 60 mm önerilir (ince çizgiler iplikte kaybolur).</p>"""),
    ("Yapmayın", """
<p>Logo her yerde aynı görünmelidir. Aşağıdakiler logoyu bozar; bunun yerine uygun sürümü kullanın.</p>
<table>
<tr><td><img src="d0.png" width="150"/><br/><b>Germeyin, sıkıştırmayın.</b> Boyutu orantılı değiştirin.</td>
<td><img src="d1.png" width="150"/><br/><b>Döndürmeyin.</b></td>
<td><img src="d2.png" width="150"/><br/><b>Renkleri değiştirmeyin.</b> Yalnız ALFA renkleri.</td></tr>
<tr><td><img src="d3.png" width="150"/><br/><b>Renkli logoyu koyu zemine koymayın.</b> Koyu zemin sürümünü kullanın.</td>
<td><img src="d4.png" width="150"/><br/><b>Gölge, parlama, degrade eklemeyin.</b></td>
<td><img src="d5.png" width="150"/><br/><b>Karışık zemine koymayın.</b> Sade bir alan seçin.</td></tr>
</table>
<p class="note" style="margin-top:10pt">Logonun parçalarını (kurt, ALFA, ROBOTICS, 8084) ayırıp yeniden düzenlemeyin, logoya kontur veya başka öğe eklemeyin.
Yeni bir kullanım gerekirse yeni sürüm hazırlanır. Yazı tipi: Classic Robot (Pixel Sagas) – kişisel ve ticari olmayan kullanımda ücretsiz; ticari kullanımda lisans gerekir.</p>"""),
]

doc = pymupdf.open()
A4 = pymupdf.paper_rect("a4")
arch = pymupdf.Archive(IMG)
for n, (title, body) in enumerate(PAGES, 1):
    pg = doc.new_page(width=A4.width, height=A4.height)
    pg.draw_rect(pymupdf.Rect(0, 0, A4.width, 78), color=None, fill=tuple(c / 255 for c in NAVY))
    pg.draw_rect(pymupdf.Rect(0, 78, A4.width, 81), color=None, fill=tuple(c / 255 for c in SKY))
    pg.insert_image(pymupdf.Rect(A4.width - 100, 6, A4.width - 34, 72), filename=IMG + "logo_head.png")
    pg.insert_htmlbox(pymupdf.Rect(40, 16, A4.width - 110, 76),
                      f'<div style="color:#9fd9f6;font-size:9pt">ALFA ROBOTICS 8084 · LOGO KULLANIM KILAVUZU · {TAG}</div>'
                      f'<div style="color:#ffffff;font-size:20pt;font-weight:bold">{title}</div>', css=CSS, archive=arch)
    spare, scale = pg.insert_htmlbox(pymupdf.Rect(40, 98, A4.width - 40, A4.height - 46), body, css=CSS, archive=arch, scale_low=1)
    if spare < 0:
        raise SystemExit(f"sayfa {n} taştı: {title}")
    pg.insert_htmlbox(pymupdf.Rect(40, A4.height - 34, A4.width - 40, A4.height - 18),
                      f'<div style="font-size:8pt;color:#8a95a1">ALFA Robotics 8084 – Logo Kullanım Kılavuzu · '
                      f'<a href="{REPO}/releases/tag/{TAG}">GitHub sürüm sayfası</a> · Sayfa {n} / {len(PAGES)}</div>', css=CSS, archive=arch)
doc.set_metadata({"title": "ALFA Robotics 8084 – Logo Kullanım Kılavuzu", "author": "ALFA Robotics 8084", "subject": f"Logo {TAG}"})
doc.save(OUT, garbage=4, deflate=True)
print(OUT, len(doc), "sayfa,", sum(len(p.get_links()) for p in doc), "bağlantı")
