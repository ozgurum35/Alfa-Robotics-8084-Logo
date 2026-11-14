# One ZIP with every wallpaper, laid out the way the user wants it (2026-11-14):
#   Masaustu/                      desktop, 3840x2160
#   Cep Telefonu/Hareketsiz/       phone stills, 2160x4680
#   Cep Telefonu/Hareketli/        phone videos (MP4) + Kapak gorselleri/ (their cover images)
# usage: python duvar_zip.py <out dir>   -> ALFA-8084-Duvar-Kagitlari.zip + Onizleme-Duvar-Kagitlari.jpg
import glob, os, sys, zipfile
from PIL import Image
import guncel_logo as g

R = g.ROOT
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
desk = sorted(glob.glob(R + "Masaustu Duvar Kagitlari/*.jpg"))
still = sorted(glob.glob(R + "Duvar Kagitlari/*.jpg"))
vid = sorted(glob.glob(R + "Hareketli Duvar Kagitlari/*.mp4")) + sorted(glob.glob(R + "Hareketli Duvar Kagidi/*.mp4"))
cover = [v[:-4] + " (kapak).jpg" for v in vid]
assert len(desk) == 28 and len(still) == 20 and len(vid) == 17 and all(os.path.exists(c) for c in cover), (len(desk), len(still), len(vid))
z = os.path.join(out, "ALFA-8084-Duvar-Kagitlari.zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as f:
    for x in desk: f.write(x, "Masaustu/" + os.path.basename(x))
    for x in still: f.write(x, "Cep Telefonu/Hareketsiz/" + os.path.basename(x))
    for x in vid: f.write(x, "Cep Telefonu/Hareketli/" + os.path.basename(x))
    for x in cover: f.write(x, "Cep Telefonu/Hareketli/Kapak gorselleri/" + os.path.basename(x))
print(z, os.path.getsize(z) // 2 ** 20, "MB |", len(desk), "masaustu,", len(still), "hareketsiz,", len(vid), "hareketli")

# preview: phone stills, animated covers, desktop
tw, th, dw, dh, m = 150, 325, 300, 169, 8
W = 10 * (tw + m) + m
rows_d = (len(desk) + 4) // 5
s = Image.new("RGB", (W, m + 2 * (th + m) + 2 * (th + m) + rows_d * (dh + m)), (24, 28, 34))
y = m
for k, x in enumerate(still): s.paste(Image.open(x).convert("RGB").resize((tw, th)), (m + (k % 10) * (tw + m), y + (k // 10) * (th + m)))
y += 2 * (th + m)
for k, x in enumerate(cover): s.paste(Image.open(x).convert("RGB").resize((tw, th)), (m + (k % 10) * (tw + m), y + (k // 10) * (th + m)))
y += 2 * (th + m)
dw = (W - 6 * m) // 5; dh = round(dw * 9 / 16)
for k, x in enumerate(desk): s.paste(Image.open(x).convert("RGB").resize((dw, dh)), (m + (k % 5) * (dw + m), y + (k // 5) * (dh + m)))
s = s.crop((0, 0, W, y + rows_d * (dh + m)))
s.save(os.path.join(out, "Onizleme-Duvar-Kagitlari.jpg"), quality=88)
