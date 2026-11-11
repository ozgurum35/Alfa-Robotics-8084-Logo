# ALFA Robotics 8084 – Logo Notları

## Güncel durum (2026-11-12)
- **v10 karar turu sürüyor; güncel durum ve açık maddeler: `docs/DEVIR v10-2.md` başı.** Kararların çoğu `kaynak/` içine uygulandı, v10 `.ai` henüz üretilmedi.
- Depo: GitHub `ozgurum35/Alfa-Robotics-8084-Logo`. Font (Classic Robot) lisans nedeniyle depoda yok; `.ai` üretimi Windows + Illustrator ister.
- Güncel dosyalar: `Yeniden Olusturulan/ALFA 8084 - Amblem v8.ai` ve `ALFA 8084 - Yazi Logo v6.ai`. v9 (kare sınır, ortalanmış daire) denendi, kullanıcı beğenmedi; dosyaları silindi.
- v4–v7 dosyaları önceki turlar (karşılaştırma için duruyor). `*_v2.ai`: özgün çizimin yalnızca teknik temizliği. Kök klasördeki iki `.ai` özgün dosyalardır, dokunulmadı.
- Kaynak (v8 durumunda, `kaynak/` içinde tam ve doğrulanmış): `kaynak/mk5.py`, `design.py` (yazı, font, çıktı) ile `wolf5_block.py` (kurt) dosyalarından `design5.py` üretir. `geo.py` geometri kiti, `mkjsx2.py` Illustrator betiği üretir, `gridview.py` ızgaralı önizleme, `logo1.json` özgün kurt düğümleri.
- Devir belgesi: `docs/DEVIR v10.md` — v8 üzerinde 13 düzeltme kararlaştırıldı, henüz uygulanmadı; sıradaki sürüm v10.
- Değerlendirme raporu: `docs/Logo Degerlendirme Raporu v5.md` (kullanıcıyla birlikte değerlendirilecek, 7 açık karar).

## Tasarım kararları (v5)
- Yazı açısı 15° = Classic Robot italik açısı; harf gövdeleri tam dikey.
- Kalkan: yay + doğru, simetrik; çerçeve 14 pt gerçek öteleme; alt uç yarıçapı 20 pt. Alt panelin üst şeridi 6,5 pt (8084 alanı büyüsün diye).
- ALFA: yükseklik 62 pt, çizgi 18 pt, iki uzun dış A bacağı 21 pt (kullanıcı isteği), A bacakları ±24°, L = F genişliği. F kolları arası 6,5 pt.
- ROBOTICS 13,5 pt (bant 23 pt, kenar payı 15 pt); 8084 16,75 pt. Classic Robot Bold Italic, bozulmadan.
- Kurt başı doğru ve yaylardan kuruldu; burun dış hattı 14 pt tam öteleme. Ağız ve çene özgün çizime göre (v8, kullanıcı isteği): oyuk dudak, köşede iki tüy çentiği, çene dış hattı üstte 7, önde 10, altta ve boğazda 12 pt.
- Alın çerçevenin iç kenarına yaslı (çerçeve = dış hat).
- Kapalı göz özgün virgül biçiminde ama ayrı bir alan (hatla kesişmez, 3/6 pt kaydırıldı). Soldaki göz ve kulak özgün biçimin yumuşatılmış hali, 5 pt aşağıda (v8; badem göz denemesi geri alındı).
- Tek lacivert siluet; gök ve buz alanları üstünde. Lacivert lacivertin üstüne binmez.
- Burun–çerçeve birleşimlerindeki yuvarlatma 3 pt (kullanıcı küçük istedi).
- Yele 1 (sol alt) buz kaldı: kurdun siluetinin içinde; sol kenarı çerçeveye 6,5 pt paralel.
- Daire (A düzeni, kullanıcı buna döndü): kalkan ekseninde, R 193,7 pt; burun, alt uç ve iki A bacağı teğet. Boşluklar eşit değil (sol 40, sağ 10, üst 27, alt 0 pt). Gizli kılavuz katmanında; kullanıcı sonunda kaldırmak istiyor.
- Renkler: Lacivert #003A6F, Açık Mavi #47B9EF, Buz #EBF7FC (global renk örnekleri).

## Bilinenler / açık konular
- Koyu zemin, tek renk ve küçük boyut sürümleri yok; CMYK/Pantone tanımlı değil.
- Yele 2 (çift bıçak) özgün biçimin yumuşatılmış hali; baştan çizilmedi.
- Classic Robot lisansı: kişisel/ticari olmayan kullanım ücretsiz; ticari kullanım lisans gerektirir.
- Başarısız yöntemler: dış sınırı kare yapıp daireyi ortalamak (v9: A bacakları ±28° açıldı, kullanıcı güzel bulmadı; `patch9.py`); boşluk kapatmak için kalkanı genişletmek (köşeler daireden taştı, kurt bozuldu); alt çeneyi döndürüp sıkıştırmak; ince çubuk çene (kullanıcı beğenmedi); tam yuvarlak uçlu kalın çene (sopa gibi durdu); çene altında düz parça + dirsek, düz kama çene, ince hilal göz (kullanıcı beğenmedi, eskisine benzer istedi); dudak ve çene hatlarını 44° açıyla kurmak (ağız kapandı, 58° yapıldı).
