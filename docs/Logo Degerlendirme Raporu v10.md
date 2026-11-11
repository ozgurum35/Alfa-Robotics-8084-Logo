# ALFA Robotics 8084 – Amblem v10 Değerlendirme Raporu

Tarih: 2026-11-12 · İncelenen: `kaynak/emblem_check.pdf` (v10 kaynak durumu, `.ai` henüz üretilmedi) · Yöntem: UI/UX Pro Max skill kuralları + ölçüm.

## Özet (sonuç önce)
1. **Beyaz zeminde renk ve okunabilirlik iyi.** Tüm yazı/zemin çiftleri WCAG AA'yı (4,5:1) geçiyor. En zayıf çift 8084 / açık mavi: 5,15:1. *Test edildi.*
2. **Koyu zeminde lacivert yazılar kayboluyor** (ALFA, ROBOTICS bandı, dış kontur). Koyu zemin sürümü gerekli. *Test edildi.*
3. **Küçük boyut:** 128 px'te her şey okunuyor, 64 px'te ROBOTICS zor okunuyor, 32 px'te ROBOTICS ve 8084 okunmuyor. Favicon/sosyal medya profili için sadeleştirilmiş sürüm (yalnız kurt + kalkan) gerekli. *Test edildi.*
4. **Gri tonda** (tek renk baskı, fotokopi) ton farkları korunuyor; lacivert / açık mavi / buz ayrışıyor. *Test edildi.*
5. **Renk tonu:** Buz rengi zaten özgünle birebir aynı (`#D0E9E8`). Özgünden farklı olan **açık mavi**: v10'da `#47B9EF`, özgünde `#80CFF4`. Üç seçenek `kaynak/v10_calisma/soruR.png` içinde; öneri **ara ton `#63C4F2`** (aşağıda gerekçe). *Karar bekliyor.*

## Kapsam – skill kurallarının bu işe uygulanabilirliği
UI/UX Pro Max kuralları ekran arayüzleri içindir. Logo bir arayüz değil, ama kuralların bir kısmı doğrudan uygulanıyor:

| Öncelik | Kategori | Bu işte | Not |
|---|---|---|---|
| 1 | Erişilebilirlik | **Uygulandı** | `color-contrast`, `color-accessible-pairs`, `color-not-only` |
| 2 | Dokunma ve etkileşim | Uygulanmaz | Logo etkileşimli değil |
| 3 | Performans | Kısmen | Web kullanımında SVG/WebP önerisi (aşağıda) |
| 4 | Stil seçimi | **Uygulandı** | Ürün türüne uygunluk, tutarlılık |
| 5 | Yerleşim ve duyarlılık | **Uygulandı** | Küçük boyut ölçeklenmesi (duyarlı logo sistemi) |
| 6 | Tipografi ve renk | **Uygulandı** | `contrast-readability`, `weight-hierarchy`, `letter-spacing`, `color-dark-mode`, `color-semantic` |
| 7 | Animasyon | Uygulanmaz | |
| 8 | Formlar | Uygulanmaz | |
| 9 | Gezinme | Uygulanmaz | |
| 10 | Grafik ve veri | Uygulanmaz | |

Skill renk veritabanı araması ("sports team esports bold") genel bir spor kırmızısı paleti döndürdü; takımın kurumsal lacivert/mavi kimliğiyle ilgisi yok, **kullanılmadı** (doğrulanmış eşleşme yok).

## 1. Erişilebilirlik – kontrast (WCAG 2.x, ölçüldü)

| Ön plan / zemin | Oran | AA metin (4,5) | Nerede |
|---|---|---|---|
| Lacivert `#003A6F` / beyaz | 11,45 | Geçer (AAA) | ALFA, dış kontur |
| Beyaz / lacivert | 11,45 | Geçer (AAA) | ROBOTICS (bant içinde beyaz harf) |
| Lacivert / buz `#D0E9E8` | 8,99 | Geçer (AAA) | Kurt hatları |
| Lacivert / açık mavi v10 `#47B9EF` | 5,15 | Geçer (AA) | **8084**, gök alanları |
| Lacivert / ara ton `#63C4F2` | 5,84 | Geçer (AA) | öneri |
| Lacivert / özgün açık mavi `#80CFF4` | 6,62 | Geçer (AA) | özgün |
| Açık mavi v10 / buz | 1,75 | – | yan yana gelmez, arada lacivert var |
| Özgün açık mavi / buz | 1,36 | – | aynı |
| Buz / beyaz | 1,27 | – | kurt beyaz zemine değmez, lacivertle çevrili |

- `color-not-only`: Logo anlamı renge bağlı değil; gri tonda biçimler okunuyor. *Test edildi.*
- Renk körlüğü: Üç renk de mavi ailesinde ve parlaklıkları belirgin farklı; kırmızı-yeşil ayrımına dayanan bir şey yok. *Varsayım (simülasyon yapılmadı, parlaklık farkına dayanıyor).*

## 2. Tipografi ve okunabilirlik
- **ALFA** (62 pt, 18 pt çizgi): her boyutta en güçlü öğe; `weight-hierarchy` doğru – ALFA > ROBOTICS > 8084 sırası net.
- **ROBOTICS** (13,5 pt, yatay %117, eğim 17,2°, harf arası 14 pt): beyaz harf / lacivert bant 11,45:1. Geniş harf arası küçük boyutta harflerin dağılmasını engelliyor. Zayıf nokta boyut: 64 px'te harf yüksekliği ~2 px → okunmuyor. *Test edildi.*
- **8084** (18,5 pt, kenar payı 3,44 pt): 128 px ve üstünde net. Lacivert / açık mavi kontrastı en düşük yazı çifti (5,15:1); açık mavi açıldıkça artar.
- `letter-spacing`: ROBOTICS'te harf arası açık (14 pt / harf genişliği 20 pt). Uzaktan okunurluk için uygun; özgüne göre biraz açık (11,6 pt) – bant uzadığı için bilinçli karar.
- **Lisans riski:** Classic Robot fontu kişisel kullanımda ücretsiz, ticari kullanımda lisans ister. Forma, sponsor afişi vb. satılabilir ürünlerde lisans gerekir. *Doğrulanmış (font lisans dosyası, NOTLAR.md).*

## 3. Renk tonları
- Palet: lacivert `#003A6F` (ana), açık mavi (ikincil), buz `#D0E9E8` (vurgu). Tek renk ailesi, soğuk ve tutarlı; "kurt / buz" temasıyla uyumlu (`color-palette-from-product`).
- **Buz:** v10'da özgünle birebir aynı (`#D0E9E8`, özgün dosyadan ölçüldü). Değişiklik gerekmiyor.
- **Açık mavi seçenekleri** (`soruR.png`):
  - A `#47B9EF` (v10): canlı, doygun; 8084 kontrastı en düşük (5,15). Buz ile ayrışma en iyi (1,75).
  - **B `#63C4F2` (öneri):** özgüne yakın, 8084 kontrastı 5,84; buzdan hâlâ ayrışıyor (1,54). Ekranda ve baskıda dengeli.
  - C `#80CFF4` (özgün): en yumuşak; 8084 kontrastı en iyi (6,62), ama buzla ayrışma zayıf (1,36) – gri tonda gök ve kurt birbirine yaklaşıyor.
- `color-semantic`: Illustrator dosyasında renkler global renk örneği (Lacivert / Açık Mavi / Buz) olarak tanımlı – tek yerden yönetiliyor. *Kaynakta doğrulandı.*

## 4. Estetik ve görsel denge
- **Siluet:** Kalkan + uluyan kurt + eğik ALFA güçlü ve dinamik; sanal daire 6 noktada teğet (burun, alt uç, iki A bacağı, iki üst köşe) – kompozisyon bir daire içinde dengeli.
- **Kontur sistemi:** Çerçeve 14 pt, iç hatlar (çene, şeritler) 8 pt; iki kademeli tutarlı bir hiyerarşi. Eş merkez kuralı ve 1 pt alt sınır uygulanıyor (son ölçüm `.ai` üretiminde `olc.py` ile yapılacak). *Kısmen doğrulandı.*
- **Özgüne sadakat:** Göz, yele, kulak, boyun bıçağı özgün düğümlerle; "tasarımcı yorumu" en aza indi.
- **Zayıf noktalar:**
  - Kapalı göz küçük; 64 px altında kayboluyor, kurdun ifadesi küçük boyutta gidiyor.
  - Sol alttaki iki yele (buz) ve bıçaklar küçük boyutta birbirine karışıyor (128 px'te kabul edilebilir).
  - Dış kontur lacivert; koyu zeminde logo kenarı kayboluyor.

## 5. Öneriler (öncelik sırasıyla)
1. **Açık mavi tonunu seç** (öneri B `#63C4F2`).
2. **Koyu zemin sürümü:** dış kontur ve ALFA için beyaz dış hat (ör. 6–8 pt) veya beyaz zemin rozeti (`color-dark-mode`, `dark-mode-pairing`).
3. **Küçük boyut sürümü (≤ 64 px):** yalnız kalkan + kurt, ROBOTICS ve 8084 olmadan; favicon ve profil fotoğrafı için.
4. **Tek renk sürümleri:** tam lacivert ve tam beyaz (nakış, lazer, tek renk baskı için).
5. **Dışa aktarma seti:** SVG (web), PNG 1024/512/256, PDF (baskı); CMYK/Pantone karşılıkları tanımlanmalı (şu an yok).
6. **Font lisansı:** ticari kullanım öncesi Classic Robot lisansı alınmalı veya yazılar vektöre çevrilip lisans durumu netleştirilmeli.

## Doğrulama durumu
- Kontrast oranları: **Test edildi** (WCAG bağıl parlaklık formülüyle hesaplandı).
- Küçük boyut, gri ton, koyu zemin: **Test edildi** (`kaynak/v10_calisma/test_boyut.png`).
- Renk körlüğü: **Varsayım** (simülasyon yapılmadı).
- Eş merkez ölçümü: **Test edilmedi** (v10 `.ai` üretimi sırasında yapılacak).
