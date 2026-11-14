# ALFA Robotics 8084 – Logo

FRC takımı ALFA Robotics 8084'ün kurtlu amblemi ve yazı logosunun parametrik Python betikleriyle yeniden çizimi. Çıktı Illustrator `.ai` (düzenlenebilir yollar, global renk örnekleri).

## Klasörler
- `ALFA LOGO-2026.ai`, `ALFA LOGO 2-2026.ai` – özgün dosyalar (dokunulmaz).
- `Yeniden Olusturulan/` – üretilen sürümler. **Güncel logo: v11.1** (`ALFA 8084 - Amblem v11.1.ai`, `ALFA 8084 - Yazi Logo v11.1.ai`, hazır dosyalar `v11.1 surum ailesi/`). Eski sürümler karşılaştırma için durur. İndirmek için [Releases](https://github.com/ozgurum35/Alfa-Robotics-8084-Logo/releases) sayfasına bakın.
- `kaynak/` – parametrik kaynak ve araçlar (ayrıntı: `docs/DEVIR v10-2.md`).
- `kaynak/v10_calisma/` – v10 karar turunun soru/sonuç görselleri ve varyant PDF'leri.
- `docs/` – proje notları ve devir belgeleri. **Okuma sırası:** `docs/DEVIR v10.md` → `docs/DEVIR v10-2.md` → `docs/NOTLAR.md`.

## Gereksinimler
- Python 3.12, `pymupdf`, `pillow`, `numpy`, `fonttools`.
- Font: Classic Robot Bold Italic (`.otf`) – lisans nedeniyle depoda **yok**; yerelde `E:/2026 masaüstü/Classic Robot/`. Ortam değişkeni `ALFA_FONT` ile başka yol verilebilir.
- `.ai` üretimi: Windows + Adobe Illustrator (COM + JSX). Bulut ortamında yalnızca PDF/PNG önizleme üretilebilir (font varsa).

## Çalıştırma (`kaynak/` içinde)
```
sh run.sh                      # mk5.py + design5.py -> emblem.json, emblem_check.pdf, ...
sh gv.sh x0 y0 x1 y1 zoom ad   # ızgaralı yakın görünüm (tmp/ad.png)
sh var.sh out.pdf dosya 's/eski/yeni/'   # varyant üret, kaynağı geri yükle
python soru.py out.png "baslik" x0 y0 x1 y1 yukseklik "Etiket=pdf" ...
```
