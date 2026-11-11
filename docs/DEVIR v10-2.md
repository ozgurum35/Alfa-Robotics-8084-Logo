# ALFA 8084 Logo – Devir Belgesi 2 (v10, madde madde karar turu)

Tarih: 2026-11-11. Önce `docs/DEVIR v10.md` (13 maddenin özgün tarifi, değişmeyecek kararlar, üretim adımları), sonra bu belge okunmalı. Bu belge onun üstüne gelen durumu anlatır.

## GÜNCEL DURUM (2026-11-12, GitHub'a taşınırken) – önce bunu oku
- Proje GitHub'a taşındı: `ozgurum35/Alfa-Robotics-8084-Logo`. Kullanıcı devamı "Logo tasarımına devam" (bulut) oturumunda istiyor.
- Karar turu: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16 kapandı ve `kaynak/` içine **uygulandı** (ayrıntı: aşağıdaki "Karar kaydı").
- Kullanıcı "buradan devam, önemli aşamalarda GitHub'a da aktar" dedi. En sona yeni madde: **burun** (henüz bakılmadı).
- **Açık:** (a) [kapandı: 18,5 pt] Madde 13: 8084 kenar payı – kullanıcı 1 pt'yi gördü (19,75 pt, şu an kaynakta `NUM_CLEAR = 1.0`) ve "1,5'a göre de bakalım" dedi; 1,5 pt varyantı: `kaynak/v10_calisma/m13_c1.5.pdf` → **19,50 pt** (1 pt → 19,75 pt); karşılaştırma `soru13c.png` kullanıcıya gönderildi, cevap bekleniyor. Kullanıcıya iki seçeneği göster, sor. (b) **Kulak** (yeni madde): `soruK.png` gönderildi (A: v10/v8 yumuşatılmış 5 pt aşağı, B: özgün `W["B"]` birebir – varyant `mK_o.pdf`), cevap bekleniyor. Öneri B (kullanıcı "özgün" kararlarını hep birebir istiyor). (c) Madde 15 (6 teğet daire, `HW` çözücü – ilk taslakta yapıldı, sorulmadı). (d) Buz rengi `#D0E9E8` (ilk taslakta uygulandı, sorulmadı).
- Sonra: uygula → `gv.sh` ile her madde → `olc.py` güncelle ve eş merkez kuralını ölç → Illustrator COM + JSX ile `Amblem v10.ai` / `Yazi Logo v10.ai` (artboard 416, `e5.clip` güncellenmeli; Windows + Illustrator gerekir, bulutta yapılamaz) → `diff.py` → önizlemeleri gönder → `NOTLAR.md`.
- Bulut ortamı notu: font depoda yok (lisans). `run.sh` fontu `ALFA_FONT` ortam değişkeninden okur; font yoksa PDF üretilemez – kullanıcıdan font dosyasını iste veya yerel oturumda çalış. Varyantlar ve kararlar için `kaynak/v10_calisma/*.pdf` hazır.
- Çalışma biçimi (kullanıcı): her madde tek tek, görselle (özgün / v10 / seçenekler); kendi önerini de çiz ve söyle; tek soru sor. "Özgündeki gibi" = özgün düğümler birebir, yorum yok. Görselleri her zaman kullanıcıya gönder (Remote Control ile takip ediyor).

## Durum (önceki oturumdan)
- v10 `.ai` dosyaları **üretilmedi**. Kullanıcı ilk taslağı görünce "çoğu istediğim şey olmamış" dedi ve `.ai` üretimini durdurdu.
- Kullanıcının istediği yöntem: **her maddeyi tek tek, görselle sor**; kullanıcı madde madde karar verir; **tüm maddeler bitince** uygulamaya/`.ai` üretimine geçilir. Toplu tablo istemiyor.
- v8 dosyaları ve özgün dosyalar değişmedi. v8 kaynağı: `kaynak/wolf5_block_v8.py`, `kaynak/mk5_v8.py` (0 piksel fark doğrulandı).

## Kullanıcının sonradan eklediği istekler (DEVIR v10'daki 13 maddeye ek)
- 14: ROBOTICS özgündeki gibi kenarlara yakın başlasın ve bitsin.
- 15: Sanal daire dış konturun sol ve sağ uçlarına da teğet olsun (6 teğet nokta: burun, alt uç, iki A bacağı, kalkanın iki üst köşesi).
- 16: Kurdun bakışı özgüne göre yumuşak kalmış; daha keskin ve vahşi görünsün.

## Madde 1 – KARAR VERİLDİ: göz ayrık olan (sağdaki seçenek)
Kullanıcı 2026-11-11'de "Göz ayrık olan" dedi. `kaynak/wolf5_block.py` zaten bu durumda; madde 1 ve 3 kapandı. Aşağıdaki metin sorunun geçmişidir.

Kullanıcının cevabı: "Özgünün aynısı. Göz sadece çizgiye girmesin." İki seçenek görselle gönderildi (`kaynak/v10_calisma/soru1b.png`): solda özgün (göz baş hattına açılıyor), sağda özgün hat birebir + göz ayrı biçim, hattan 4,5 pt aşağıda. Kullanıcı ikisi arasında karar verecek; karar sonradan geldi (yukarıda). `kaynak/wolf5_block.py` şu an sağdaki seçenek durumunda.
- Uygulama: baş üst hattı özgün düğümlerle (`W["H"]` 33, 34, 35, 0, 3, 4, 5, 6), sonra `Qi`'den burun zinciri. Göz: `W["H"]` 0–3, kaydırma `_s = (5, 4.5)`, üstü hafif yay.
- Çıkarılacak ders: kullanıcı "özgündeki gibi" dediğinde yorumlamadan özgün düğümleri birebir kullan; kendi yorumunu (kubbeli baş, kaş çizgisi, gözü 18 pt kaydırma) eklemek reddedildi.

## Karar kaydı (madde madde, bu turda)
- Madde 2: **A – 5 pt** (`LIPR = 5.0`, ilk taslaktaki gibi). Görsel: `kaynak/v10_calisma/soru2.png`.
- Madde 16: **A** – madde 1'deki ayrık göz olduğu gibi (üstü hafif yay, `bow -0.08`); düz üstlü keskin göz (B) seçilmedi. `soru16.png`.
- Madde 4: **v10** – özgün düğümler, kanca 8 pt yukarı (`HK = V(0, -8)`). `soru4.png`.
- Madde 5: **1,5 pt** (kullanıcının kendi değeri; `skyR` içinde `nR - 2: 1.5`, uygulandı). `soru5.png`.
- Madde 6: **B – dış 5 pt, buz sivri** (`RJT = 5.0`, uygulandı). Kullanıcı ek olarak: "eş merkezli lacivert alan o kadar kalın olmasına gerek yok" → ön yüz lacivert kalınlığı (`WJF`, 10 pt) incelecek; seçenekler `soru6b.png`. Karar: **ön yüz 5 pt** (`WJF = 5.0`, uygulandı).
- Madde 7: **çene çevresi her yerde 8 pt** (ağız tarafı, ön yüz, alt ve boğaz: `WJT, WJF, WJU = 8, 8, 8`); alt köşe dış 10 / iç 2 pt eş merkez (`RJB = 10`); üst köşe dış 5 / iç 1 pt (kural). Bu madde 6'daki 5 pt ön yüzün yerine geçti. Uygulandı; `soru7*.png`, `sonuc7.png`. Not: DEVIR v10 madde 10'daki "9 pt şerit = çene/boğaz hattı" artık 8 pt'ye karşılık geliyor; madde 10'da sorulacak.
- Madde 8: **A – 1 pt** (`skyR` `3: 1.0`). Kullanıcı ek olarak: altındaki şerit (kurdun altı) ile 8084 panelinin üstündeki şerit eşit ve **özgündeki gibi ince** olsun (madde 13'ün 14 pt kararı değişiyor). Ölçüm (`kaynak/runs.py`): özgünde ikisi de ~7 pt (dikey 7,25–7,3), v10'da 14. Kurdun altı artık `LW`'ye bağlı (`PIN = PU + LW * nUp`). Seçenekler `soru8b.png` (7 / 8 pt); 8084: LW 7 → 12,75, LW 8 → 12,5 pt (kaba tarama).
  Karar: **B – 8 pt** (`LW = 8.0`, uygulandı; kurdun altı ve 8084 üstü eşit).
- Madde 9 (soruldu, `soru9.png`): özgünde boğaz hattı bıçağın ucuna (`W["H"][20]`) varıyor; v10'da boğaz hattı ~10 pt sağda, arada buz dil kalıyor. Bıçağı 14 pt sağa almak boğazla kesişip kıymık bıraktı (başarısız); 7 pt seçenek olarak gösterildi.
  Kullanıcı: "özgündekinin aynısı". Uygulama: boğaz hattı iki yay (a9 6°, a10 30°), yarıçapları doğrusal çözümle (`R9, R10`) bulunuyor ve hat tam olarak özgün düğüm 20'de (bıçak ucu) bitiyor; düz uzantı `Ln(P5, E)` kaldırıldı, `left` düğüm 21'den başlıyor. Buz dil bıçak ucunda sivri kapanıyor. Ardından kullanıcı "biraz daha sağa al" dedi → `BS` (bıçak + uç kaydırma, kesime paralel; dik kaydırma uçta çentik bırakıyordu). Seçenekler 4 / 7 pt: `soru9b.png`. Kullanıcı "özgündeki gibi iç içe geçsin" → `TT` (boğaz ucu bıçağın sağ kenarında yukarı). Karar: **D – `BS` 4 pt kesime paralel, `TT = 0.2`** (birleşme ~8 pt yukarıda; `TT = 0.4` boğazı kırdı). Uygulandı. `soru9c.png`.
- Madde 10 (soruldu, `soru10.png`): A taslak (iki uçlu, `WM` 9), B aynı biçim `WM` 8, C tek uçlu dar alev (`FPX` 74, Y4 kaldırıldı). Tek uçlu `FPX` 84 denemesi yelelere taştı (başarısız).
  Karar: **özgünün aynısı** (DEVIR v10'daki "yukarı büyüsün, çentiğe paralel şerit" kararı geri alındı), **ama sol kenarı açık mavi çentiğin sol kenarının hayali devamına otursun**. O çizgi çerçevenin iç kenarı `shI[4]` (dış kontura eş merkezli). Ölçüm: özgün yelenin sol kenarı bu yaya paralel, 5,8 pt içeride. Uygulama (`FUR_ORIG = True`): özgün `W["Y"]` düğümleri radyal 5,8 pt dışa kaydırıldı, sol kenar tam bu yay (düğüm 0 ve 2 yaya izdüşürüldü). Uygulandı.
- Madde 11 (soruldu, `soru11.png`): uç yay boyunca uzatılıyor (`TIPD`; sağ kenar üst uçtan (düğüm 4) tek yay `TIPK -0.08`, düğüm 3 düşer). Uç 6 / 11 pt seçenekleri. Kesim altı da lacivert olduğundan "aşma" az okunuyor. Başarısız: tutamakları kaydırmak / düğüm 3'ü tutmak sağ kenarda kırık bıraktı.
  Karar: **uç 6 pt uzun (`TIPD = 6`), yele yay boyunca 8 pt yukarı (`FUP = 8`, sol kenar yayda kalır)**. Uygulandı. `soru11c.png`.
- Madde 12: **keskin** (dört kesim köşesi + iç açık mavi köşeler; "Tamam"). `soru12.png`.
- Madde 13 (soruldu, `soru13.png`): şerit artık 8 pt (madde 8 kararı). 8084'ün küçük kalma nedeni tarama alanıydı (merkezden yalnızca ±8 pt). `mk5.py`'de tarama değişti: kaba (boyut 0,5, du ±12, dn −18..14, adım 2) + dar ince tarama (±2 pt, adım 0,5; boyut 0,25). Sonuç 16,25 pt (v8 16,75), tarama ~36 sn.
  Karar: **kenar payı 1 pt, yazı sığan en büyük** (`NUM_CLEAR = 1.0`). İnce tarama penceresi genişletildi (boyut +3, dn −3..+9): **8084 = 19,75 pt**, gerçek pay 1,43 pt. Uygulandı. `sonuc13.png`.
  Son karar: **8084 = 18,5 pt** (`NUM_CAPFIX = 18.5`; panel kenarına payın en geniş olduğu yerde, pay 3,44 pt). Uygulandı. `sonuc13.png`.
- Kullanıcı yeni madde ekledi: **kulak** – kullanıcı "sol uç" diyor (kulağın sola uzanan ucu, `W["B"]`; ilk görselde yanlış yer gösterilmişti). Karar: **B – özgün düğümler, özgün yerinde**, "ama üstteki çizgiler birbirini takip etmiyor, girinti çıkıntı var" → (1) kulak üst hattı düğüm 15'teki basamak kaldırılıp tek kavis (`W["B"][14].o = (100, 116.3)`, `del W["B"][15]`, `fair` ve 5 pt kaydırma yok); (2) üstteki açık mavi alanın alt kenarı kulak üst hattının 8 pt paraleli (`SKY_EAR`, `WE = 8`, Tiller–Hanson öteleme; t 0,85'ten sonra teğet doğruyla çerçeveye). `soruK3.png`. Sonra kullanıcı (2) için "özgün gibi olsun, özgündeki gibi kavisli gelsin sola doğru" dedi → `SKY_EAR = False` (paralel öteleme geri alındı); sırt çizgisi köşeden çerçeveye **tek kavis** (`BACK1`, özgün W["G"] düğüm 2 ve 0 teğetleriyle; çerçeve dışa taşındığı için özgün kısa uç parça kırık yapıyordu). Uygulandı, **onaylandı** ("Tamam"). `soruK5.png`.
- Madde 15 (soruldu, `soru15.png`): `HW` çözücüyle kalkan her yanda ~7 pt genişledi, üst köşeler daireye teğet (burun, alt uç, iki A bacağı, iki üst köşe; R 194,06). **Onaylandı** ("Güzel oldu").
- Değerlendirme raporu: `docs/Logo Degerlendirme Raporu v10.md` (UI/UX Pro Max kuralları). Buz zaten özgün `#D0E9E8`; açık mavi seçenekleri `soruR.png` (A `#47B9EF`, B `#63C4F2` öneri, C özgün `#80CFF4`; `mk5.py` SKY satırı). Karar bekleniyor. Sonra: burun. v10'da v8 hali (yumuşatılmış, 5 pt aşağı); seçenek: özgün düğümler birebir. `soruK.png`.
- **Genel kural (kullanıcı):** iç kontur kavisi = dış kavis − kontur; kontur kalın olduğu için eş merkezli kavis verilemiyorsa iç köşe **1 pt** kavis alır (sivri değil). Çenede `JIN = max(..., 1.0)` olarak uygulandı.
- Madde 14 (ROBOTICS): kullanıcı "harfler daha geniş; ROBOTICS özgündeki gibi olsun" dedi. Ölçüm (özgün `orig_v2.pdf`, bant yönünde): harf yüksekliği aynı (~13,3 pt), ama özgünde harfler **%17 geniş** (O 19,9 / v10 17,0 pt), eğim 17,2° (15° × 1,17 ile tutarlı) ve harf arası 11–12 pt (v10 17,2 pt). Yani özgün ROBOTICS, Classic Robot Bold Italic'in yatayda ~%117 ölçeklenmiş hali. `mk5.py`'ye `ROB_SX` (yatay ölçek) eklendi; 1.0'da çıktı birebir aynı (piksel doğrulandı). Ölçüm betiği: scratchpad `rob2.py` (bant köşeleri elle verilir).
  Karar: **özgündeki gibi (`ROB_SX = 1.17`), ama yazı bandın üst köşelerinde başlayıp bitsin.** Uygulama: `ROB_M, ROB_DU = 6.385, 0.505` → üst köşelerde boşluk 4,36 pt = harf üstü/altı boşluk (`kaynak/rob_olc.py` ile ölçüldü). Harf arası 14 pt (özgün 11,6; bant v10'da daha uzun). **Onaylandı** ("Tamam"). `soru14b.png`.
- Kullanıcı isteği (bu turda): her maddede kendi önerimi de söyle ve çiz.

## Kalan maddeler için ilk taslakta yapılanlar ve kendi değerlendirmem
Karşılaştırma sayfaları (özgün / v8 / ilk taslak): `kaynak/v10_calisma/karsilastirma_1..5.png`. İlk taslağın kurt kodu: `kaynak/v10_calisma/wolf5_block_taslak1.py`.

| # | İlk taslakta yapılan | Değerlendirme / öneri |
|---|---|---|
| 2 Burun–üst dudak köşesi | kavis 2 → 5 pt (`LIPR`) | oldu |
| 3 Kapalı göz | madde 1 ile birlikte çözülüyor | – |
| 16 Bakış | göze sivri kaş çizgisi eklenmişti; madde 1 kararıyla kaldırıldı | özgün hat geri geldiği için büyük olasılıkla çözüldü; kullanıcıya sor |
| 4 Sol yele kıvrımı | özgün düğümler (`W["H"]` 24–32); kanca 8 pt yukarı (`HK`), çünkü kesim çizgisi özgünden yukarıda | oldu |
| 5 Ağız köşesi mavi uç | kavis 2,5 → 1 pt | oldu |
| 6 Çene ön üst ucu | buz ucu sivri, dış 2 pt (`RJT`) | fazla sert, çene kutu gibi; öneri: buz 1,5 / dış 4, ön yüz özgündeki gibi hafif kavisli |
| 7 Çene alt köşesi | buz sivri, dış 9 pt (`RJB`), ön yüz 105° (`JF`) | sivri buz köşe mekanik; öneri: buz 2 / dış 10 (eş merkez kuralından küçük sapma, kullanıcıya söyle) |
| 8 Boğaz altı mavi uç | kavis 3 → 1 pt | oldu |
| 9 Boyun bıçağı | özgün düğümler (`W["H"]` 20–23) | oldu; özgünde tabanı boğaz hattına bitişikti, burada 12 pt buz kalıyor |
| 10 Çentik–yele arası | çentik alt kenarı gerçek yay (`notchA`), yele üstü eş merkezli 9 pt (`topF`); yele iki uçlu | şerit oldu, biçim hantal; öneri: tek uçlu dar alev |
| 11 Yele alt ucu | uç alt şeride 7 pt giriyor (`FZD`) | orada her yer lacivert olduğundan "aşma" az okunuyor |
| 12 Kesim köşeleri | `RCUT` yuvarlatmaları kaldırıldı, dört dış + iç köşe keskin | oldu |
| 13 8084 şeridi | `LW` 14 pt; 8084 16,75 → 11,75 pt (ince taramayla en fazla 12,75) | yazı zayıf; kullanıcıya sor: 12,75'i kabul mü, şerit 10 pt mi |
| 14 ROBOTICS | `ROB_M` 15 → 6,5 pt | kenarlar oldu, harf arası çok açıldı; öneri: `ROB_CAP` 13,5 → 15 |
| 15 6 teğet | `HW` çözücüyle ≈161 (her yan +7 pt); köşe boşluğu 0 | oldu; 8084 paneli de biraz genişledi |
| Buz rengi | `#D0E9E8` | oldu |

Eş merkez kuralı ölçümü için `kaynak/olc.py` yazıldı ama madde 1 değişince alın–burun satırı geçersiz kaldı; çalıştırmadan önce güncellenmeli. **Eş merkez ölçümü henüz yapılmadı.**

## Araçlar (bu turda eklendi, hepsi `kaynak/` içinde)
- `run.sh`: `mk5.py` + `design5.py` çalıştırır.
- `gv.sh x0 y0 x1 y1 zoom ad`: güncel `emblem_check.pdf` için ızgaralı yakın görünüm (artboard kayması otomatik).
- `soru.py out.png "baslik" x0 y0 x1 y1 yukseklik "Etiket=pdf" ...`: soru görseli (özgün için `v10_calisma/orig_v2.pdf`, v8 için `Amblem v8.ai`; diğer pdf'ler 416 pt artboard varsayar: kayma 19,5 / 9,39).
- `sheet.py`: 15 maddelik karşılaştırma sayfaları.
- Artboard artık 416 pt (daire R 194,06); `.ai` doğrulamasında `e5.clip` buna göre güncellenmeli.

## Başarısız yöntemler (bu turdan)
- Başın arka çizgisini çerçevenin üst iç yayına teğet kubbe yapmak; düz yayla burun hattına teğet karıştırmak (ikisi de reddedildi, özgün hat istendi).
- Kapalı gözü 18 pt sağa kaydırmak ve sivri kaş çizgisi eklemek.
- 16 maddeyi tek tabloda sormak (kullanıcı tek tek, görselle istiyor).
- 8084 için tüm boyutlarda ince tarama (dakikalar sürüyor; yalnızca dar aralıkta dene).

## İlk yapılacak iş
1. Madde 1 kapandı (göz ayrık olan). Madde 2'den başla.
2. Sırayla 2, 3/16, 4, … 15 ve buz rengi: her biri için özgün / v8 / seçenek(ler) görselini `soru.py` ile üret, SendUserFile ile gönder, tek soru sor, cevabı bekle. Öneri varsa onu da ayrı panel olarak çiz.
3. Tüm kararlar gelince uygula, eş merkez kuralını ölç, `Amblem v10.ai` ve `Yazi Logo v10.ai` üret, piksel karşılaştırmasıyla doğrula, `docs/NOTLAR.md` güncelle.
