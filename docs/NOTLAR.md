# ALFA Robotics 8084 – Logo Notları

## Güncel durum (2026-11-12)
- **Güncel sürüm: `Yeniden Olusturulan/ALFA 8084 - Amblem v10.ai` ve `ALFA 8084 - Yazi Logo v10.ai`** (önizleme PNG'leri yanında). v8 / v6 ve öncekiler karşılaştırma için duruyor; v9 numarası kullanılmadı. Kök klasördeki iki `.ai` özgün dosyalardır, dokunulmadı.
- Dışa aktarım: `Yeniden Olusturulan/v10 disa aktarim/` – PDF (baskı, Acrobat 7), SVG, PNG 512/1024/2048/4096 px (saydam). Yazılar yol; hiçbir dosyada font yok (baskıcıda font gerekmez). Kılavuz daire dışa aktarılmadı. Betik: `kaynak/export_v10.jsx` (Illustrator PNG ölçeği en fazla %776 olduğundan 4096 px PDF'ten üretildi).
- v10 madde madde karar turuyla yapıldı; tüm kararlar ve gerekçeler: `docs/DEVIR v10-2.md` (karar kaydı). Değerlendirme raporu: `docs/Logo Degerlendirme Raporu v10.md`.
- Doğrulama: eş merkez raporu `kaynak/olc.py` – tüm kontroller geçti; `diff.py` – iki `.ai` dosyası önizlemeyle piksel düzeyinde aynı (fark > 32: 0).
- Depo: GitHub `ozgurum35/Alfa-Robotics-8084-Logo` (public). Font (Classic Robot) lisans nedeniyle depoda yok; `.ai` üretimi Windows + Illustrator ister.
- Açık konular (rapordan): koyu zemin sürümü, ≤ 64 px sade sürüm, tek renk sürümler, CMYK/Pantone, font ticari lisansı. Kılavuz daire gizli katmanda; kullanıcı sonunda kaldırılmasını isteyebilir. Burun ön yüzü–çerçeve dış köşesi (`RXN` 3 pt) değiştirilmedi.

## v10 kararları (özet)
- Renkler: Lacivert `#003A6F`, Açık Mavi `#63C4F2` (özgün `#80CFF4` ile v8 `#47B9EF` arası), Buz `#D0E9E8` (özgünle aynı).
- İç hat kuralı: iç kavis = dış kavis − kontur; verilemiyorsa iç köşe 1 pt. Çene çevresi 10 pt; kurdun altı ve 8084 üstü şerit 8 pt; çerçeve 14 pt.
- "Özgündeki gibi" denen yerler özgün düğümlerle birebir: göz (hattan ayrık), sol yele kıvrımı, boyun bıçağı (+ boğaz hattı bıçak ucuna varır, 4 pt sağa), sol buz yele (sol kenarı çerçeve iç yayında, 8 pt yukarı, uç 6 pt uzun), kulak (üst basamak düzeltildi), sırt çizgisi tek kavis.
- ROBOTICS: özgün gibi yatay %117 (eğim 17,2°), bandın üst köşelerinde başlar/biter. 8084: 18,5 pt. Kalkan 6 teğet noktalı daireye oturur. Kesim köşeleri keskin.

## Tasarım kararları (v5–v8, bir kısmı v10'da değişti)
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
