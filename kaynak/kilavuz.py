# Logo usage guide (PDF) for the v10 logo family: which file where, formats, colours, clear space, minimum size, don'ts.
import os, shutil
import pymupdf
from PIL import Image, ImageDraw

ROOT = "D:/CLAUDE/Alfa Logo/Yeniden Olusturulan/v10 surum ailesi/"
OUT = ROOT + "ALFA 8084 - Logo Kullanim Kilavuzu.pdf"
IMG = "D:/CLAUDE/Alfa Logo/kaynak/v10_calisma/kilavuz_img/"
os.makedirs(IMG, exist_ok=True)
shutil.copy("C:/Windows/Fonts/segoeui.ttf", IMG + "segoeui.ttf")
shutil.copy("C:/Windows/Fonts/segoeuib.ttf", IMG + "segoeuib.ttf")
NAVY, WHITE, GREY = (0, 58, 111), (255, 255, 255), (242, 244, 246)


def thumb(rel, bg, name, h=200):
    im = Image.open(ROOT + rel).convert("RGBA")
    im.thumbnail((int(h * 1.6), h))
    c = Image.new("RGBA", (int(h * 1.7), h + 20), bg + (255,))
    c.alpha_composite(im, ((c.width - im.width) // 2, (c.height - im.height) // 2))
    c.convert("RGB").save(IMG + name)
    return name


V = [  # (folder, variant, background, where to use)
    ("Amblem", "Renkli", WHITE, "Ana logo. Beyaz ve açık renkli zeminler: web sitesi, belge, sunum, afiş, açık renk forma."),
    ("Amblem", "Koyu zemin", NAVY, "Lacivert, siyah, koyu renkli zeminler ve koyu fotoğraflar; koyu forma, tişört, pankart. Beyaz kenar logonun ayrılmasını sağlar."),
    ("Amblem", "Tek renk lacivert", WHITE, "Tek renk baskı: damga, fotokopi, nakış, lazer kazıma, tek renk serigrafi, açık zemin."),
    ("Amblem", "Tek renk beyaz", NAVY, "Koyu zeminde tek renk: beyaz serigrafi, folyo kesim, cam / araç etiketi, koyu kumaşa nakış."),
    ("Yazi Logo", "Renkli", WHITE, "Yazı logo. Yatay ve dar alanlar: antetli kâğıt, e-posta imzası, sunum alt bilgisi, robot gövdesi."),
    ("Yazi Logo", "Tek renk lacivert", WHITE, "Yazı logo, tek renk; açık zemin."),
    ("Yazi Logo", "Tek renk beyaz", NAVY, "Yazı logo, koyu zemin (lacivert, siyah, koyu fotoğraf)."),
    ("Simge", "Renkli", WHITE, "Yazısız simge: küçük alanlar, çıkartma, rozet, uygulama simgesi. Amblemin 30 mm / 128 px altına indiği her yerde."),
    ("Simge", "Koyu zemin", NAVY, "Simge, koyu zemin."),
    ("Simge", "Tek renk lacivert", WHITE, "Simge, tek renk; açık zemin."),
    ("Simge", "Tek renk beyaz", NAVY, "Simge, tek renk; koyu zemin."),
]
rows = []
for i, (f, v, bg, use) in enumerate(V):
    label = "Yazi Logo" if f == "Yazi Logo" else f
    t = thumb(f"{f}/{v}/ALFA 8084 - {label} v10 - {v} 1024px.png", bg, f"v{i}.png")
    rows.append(f'<tr><td class="im"><img src="{t}" width="150"/></td><td><b>{f.replace("Yazi", "Yazı")} – {v}</b><br/>{use}<br/>'
                f'<span class="path">{f}/{v}/</span></td></tr>')

# profile / favicon thumbs
thumb("Profil/ALFA 8084 - Profil beyaz 400px.png", WHITE, "p0.png")
thumb("Favicon/ALFA 8084 - Simge 512px.png", WHITE, "p1.png")
for n, c in (("s0.png", NAVY), ("s1.png", (99, 196, 242)), ("s2.png", (208, 233, 232))):
    Image.new("RGB", (120, 56), c).save(IMG + n)

# don'ts, made from the colour emblem
src = Image.open(ROOT + "Amblem/Renkli/ALFA 8084 - Amblem v10 - Renkli 512px.png").convert("RGBA")
def dont(img, bg, name):
    c = Image.new("RGBA", (300, 300), bg + (255,)); img.thumbnail((270, 270))
    c.alpha_composite(img, ((300 - img.width) // 2, (300 - img.height) // 2))
    d = ImageDraw.Draw(c); d.line((12, 12, 52, 52), fill=(210, 30, 40), width=8); d.line((52, 12, 12, 52), fill=(210, 30, 40), width=8)
    c.convert("RGB").save(IMG + name)
dont(src.resize((512, 330)), WHITE, "d0.png")
dont(src.rotate(25, expand=True, resample=Image.BICUBIC), WHITE, "d1.png")
r, g, b, a = src.split(); dont(Image.merge("RGBA", (b, r, g, a)), WHITE, "d2.png")
dont(src.copy(), NAVY, "d3.png")
sh = Image.new("RGBA", (560, 560), (0, 0, 0, 0)); blur = src.copy(); blur.putalpha(a.point(lambda v: v // 3))
sh.alpha_composite(Image.new("RGBA", src.size, (0, 0, 0, 0)), (0, 0))
shadow = Image.new("RGBA", src.size, (0, 0, 0, 255)); shadow.putalpha(a.point(lambda v: v // 2))
sh.alpha_composite(shadow, (30, 30)); sh.alpha_composite(src, (0, 0)); dont(sh, WHITE, "d4.png")
noise = Image.effect_noise((300, 300), 90).convert("L")
c = Image.merge("RGB", (noise.point(lambda v: v), noise.point(lambda v: 255 - v), noise.point(lambda v: v // 2))).convert("RGBA")
im = src.copy(); im.thumbnail((270, 270)); c.alpha_composite(im, (15, 15))
d = ImageDraw.Draw(c); d.line((12, 12, 52, 52), fill=(210, 30, 40), width=8); d.line((52, 12, 12, 52), fill=(210, 30, 40), width=8)
c.convert("RGB").save(IMG + "d5.png")

CSS = """
@font-face { font-family: tr; src: url(segoeui.ttf); }
@font-face { font-family: tr; font-weight: bold; src: url(segoeuib.ttf); }
* { font-family: tr; }
body { font-size: 9.5pt; color: #1d2733; line-height: 1.35; }
h1 { font-size: 22pt; color: #003A6F; margin: 0 0 4pt 0; }
h2 { font-size: 13pt; color: #003A6F; margin: 14pt 0 5pt 0; border-bottom: 1pt solid #63C4F2; }
p { margin: 3pt 0; }
table { border-collapse: collapse; width: 100%; }
td, th { border-bottom: 0.5pt solid #d5dbe1; padding: 4pt; vertical-align: middle; text-align: left; }
th { color: #003A6F; font-size: 9pt; }
td.im { width: 160pt; }
.path { color: #6b7785; font-size: 8pt; }
.sw { width: 60pt; height: 28pt; }
.note { color: #6b7785; font-size: 8.5pt; }
"""
HTML = f"""
<h1>ALFA Robotics 8084 – Logo Kullanım Kılavuzu</h1>
<p class="note">Sürüm v10 · 2026-11 · Bu kılavuz hangi logo dosyasının nerede kullanılacağını anlatır. Tüm dosyalar GitHub sürüm sayfasında.</p>

<h2>1. Hangi logo nerede?</h2>
<table>{''.join(rows)}</table>

<h2>2. Profil fotoğrafı ve web sitesi simgesi</h2>
<table>
<tr><td class="im"><img src="p0.png" width="150"/></td><td><b>Profil – beyaz / lacivert</b> (400 ve 1080 px kare)<br/>Instagram, X, LinkedIn, YouTube, WhatsApp profil fotoğrafı. Amblem yuvarlak kırpmaya sığacak şekilde ortalı.<br/><span class="path">Profil/</span></td></tr>
<tr><td class="im"><img src="p1.png" width="150"/></td><td><b>Favicon</b>: web sitesi sekme simgesi (<i>favicon.ico</i>, 16 / 32 / 48 px), iPhone ana ekran simgesi (<i>apple-touch-icon 180px</i>), 512 px uygulama simgesi.<br/><span class="note">16 px'te kurt ayrıntısı sınırlı görünür.</span><br/><span class="path">Favicon/</span></td></tr>
</table>

<h2>3. Hangi dosya biçimi?</h2>
<table>
<tr><th>Biçim</th><th>Ne için</th></tr>
<tr><td><b>PDF</b></td><td>Baskı ve matbaa: afiş, broşür, kartvizit, forma baskısı, pankart. Vektörel, her boyutta net. Matbaaya her zaman PDF verin.</td></tr>
<tr><td><b>SVG</b></td><td>Web sitesi; lazer kesim, folyo kesim (plotter) ve CNC yazılımları. Vektörel.</td></tr>
<tr><td><b>PNG</b></td><td>Word, PowerPoint, Canva, sosyal medya, mesajlaşma. Saydam zeminli. Boyut: 512 px küçük kullanım, 1024 px sunum ve web, 2048 px büyük ekran, 4096 px yüksek çözünürlüklü baskı (≈ 35 cm genişlik, 300 dpi). Kendi boyutundan büyütmeyin.</td></tr>
<tr><td><b>AI</b></td><td>Adobe Illustrator kaynak dosyası: yalnız düzenleme ve tasarımcıya / matbaaya kaynak olarak.</td></tr>
</table>

<h2>4. Renkler</h2>
<table>
<tr><td class="sw"><img src="s0.png" width="60"/></td><td><b>ALFA Lacivert</b> · HEX #003A6F · RGB 0 58 111 · ana renk</td></tr>
<tr><td class="sw"><img src="s1.png" width="60"/></td><td><b>ALFA Açık Mavi</b> · HEX #63C4F2 · RGB 99 196 242 · ikincil renk</td></tr>
<tr><td class="sw"><img src="s2.png" width="60"/></td><td><b>ALFA Buz</b> · HEX #D0E9E8 · RGB 208 233 232 · vurgu (kurt)</td></tr>
</table>
<p class="note">Baskı renk karşılıkları (CMYK / Pantone) henüz tanımlı değil. Önemli baskılarda matbaadan renk provası isteyin.</p>

<h2>5. Boşluk ve en küçük boyut</h2>
<p><b>Koruma alanı:</b> logonun her yanında, logonun uzun kenarının en az %10'u kadar boş alan bırakın. Dosyalardaki kenar boşluğu bu kadardır; dosyayı kırpmadan kullanın.</p>
<table>
<tr><th>Logo</th><th>Ekranda en küçük</th><th>Baskıda en küçük</th></tr>
<tr><td>Amblem</td><td>128 px genişlik</td><td>30 mm genişlik</td></tr>
<tr><td>Yazı logo</td><td>128 px genişlik</td><td>30 mm genişlik</td></tr>
<tr><td>Simge</td><td>32 px</td><td>10 mm</td></tr>
</table>
<p class="note">Bunun altında ROBOTICS ve 8084 okunmaz; daha küçük alanlarda simgeyi kullanın.</p>

<h2>6. Yapmayın</h2>
<table><tr>
<td><img src="d0.png" width="75"/><br/>Germeyin, sıkıştırmayın</td>
<td><img src="d1.png" width="75"/><br/>Döndürmeyin</td>
<td><img src="d2.png" width="75"/><br/>Renkleri değiştirmeyin</td>
</tr><tr>
<td><img src="d3.png" width="75"/><br/>Renkli logoyu koyu zemine koymayın (koyu zemin sürümünü kullanın)</td>
<td><img src="d4.png" width="75"/><br/>Gölge, parlama, degrade eklemeyin</td>
<td><img src="d5.png" width="75"/><br/>Karışık zemin ve fotoğrafın üstüne koymayın</td>
</tr></table>
<p class="note">Logonun parçalarını (kurt, ALFA, ROBOTICS, 8084) ayırıp yeniden düzenlemeyin; yeni bir kullanım gerekirse yeni sürüm hazırlanır.</p>
"""
story = pymupdf.Story(html=HTML, user_css=CSS, archive=pymupdf.Archive(IMG))
writer = pymupdf.DocumentWriter(OUT)
A4 = pymupdf.paper_rect("a4"); where = A4 + (40, 40, -40, -40)
more = True
while more:
    dev = writer.begin_page(A4); more, _ = story.place(where); story.draw(dev); writer.end_page()
writer.close()
print(OUT, len(pymupdf.open(OUT)), "sayfa")
