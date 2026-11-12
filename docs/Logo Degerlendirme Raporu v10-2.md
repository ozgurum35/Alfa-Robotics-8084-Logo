# ALFA Robotics 8084 – v10 Son Hal Değerlendirme Raporu (2)

Tarih: 2026-11-12 · İncelenen: `Amblem v10` ve `Yazi Logo v10` (yayınlanan son hal, renk `#63C4F2`) · Kural setleri: **UI/UX Pro Max** (10 kategori, `quick-reference.md` + `pro-rules.md`) ve **Brand / Design** skill'leri (`logo-usage-rules.md`, `approval-checklist.md`, logo ölçeklenebilirlik listesi).
Test görselleri: `kaynak/v10_calisma/rapor2/` · Betik: `kaynak/rapor2_test.py`.

## Özet (sonuç önce)

| # | Bulgu | Önem | Durum |
|---|---|---|---|
| 1 | **Koyu zeminde logo kayboluyor**: lacivert / siyah 1,65:1, lacivert / lacivert 1:1. ALFA ve dış kontur görünmüyor. | Yüksek | Test edildi |
| 2 | **Beyaz görünen yerler aslında saydam**: ROBOTICS harfleri ve ALFA çevresi zemin rengini alıyor (kırmızı zeminde ROBOTICS kırmızı). | Yüksek | Test edildi |
| 3 | **Simge (yazısız) sürüm yok**: 64 px'te ROBOTICS, 32 px'te 8084 ve kurt ayrıntısı kayboluyor; 16 px'te logo tanınmıyor. | Yüksek | Test edildi |
| 4 | **Tek renk sürüm yok**, ama tasarım buna çok uygun: lacivert mürekkep ve ters beyaz test görselinde temiz okunuyor. | Orta | Test edildi |
| 5 | **Baskı rengi tanımsız**: PDF'ler RGB; CMYK / Pantone karşılığı yok. | Orta | Doğrulandı (PDF) |
| 6 | **Kullanım kuralları yok**: en küçük boyut, koruma alanı, yanlış kullanımlar yazılı değil. | Orta | – |
| 7 | Açık zeminlerde kontrast, renk körlüğü, gri ton, renk oranı, efektsiz düz çizim, vektör dosyalar: **geçiyor**. | – | Test edildi |
| 8 | Classic Robot ticari lisansı (yasal konu). | Yasal | Doğrulandı (NOTLAR) |

## 1. UI/UX Pro Max – kategori kategori

Logo bir arayüz değil; kuralların uygulanabilir olanları uygulandı, uygulanmayanların nedeni yazıldı.

| Öncelik | Kategori | Uygulanan kurallar | Sonuç |
|---|---|---|---|
| 1 | Erişilebilirlik | `color-contrast`, `color-accessible-pairs`, `color-not-only`, `alt-text`, `icon-context`, ikon kontrastı 3:1 (pro-rules) | Açık zeminde geçer; koyu zeminde **kalır** (bulgu 1); SVG'de `<title>` yok |
| 2 | Dokunma ve etkileşim | – | Uygulanmaz (logo etkileşimli değil) |
| 3 | Performans | `image-optimization`, `image-dimension` | Geçer: SVG 11–17 KB; PNG'ler sabit boyutlu. WebP gerekmez (SVG daha iyi) |
| 4 | Stil seçimi | `style-match`, `consistency`, `effects-match-style`, `dark-mode-pairing`, `icon-style-consistent`, "Vector-Only Assets", "Correct Brand Logos" | Stil spor takımı amblemine uygun, iki logo tutarlı; **koyu sürüm eşi yok** (bulgu 1) |
| 5 | Yerleşim ve duyarlılık | `visual-hierarchy`, `content-priority`, `whitespace-balance` → duyarlı logo sistemi | Hiyerarşi doğru (ALFA > kurt > ROBOTICS > 8084); **küçük boyut sürümü yok** (bulgu 3) |
| 6 | Tipografi ve renk | `weight-hierarchy`, `letter-spacing`, `contrast-readability`, `color-semantic`, `color-dark-mode`, `color-not-decorative-only` | Geçer; renkler global örnek olarak tek yerden yönetiliyor. `color-dark-mode` kalır |
| 7 | Animasyon | – | Uygulanmaz (hareketli logo yok) |
| 8 | Formlar | – | Uygulanmaz |
| 9 | Gezinme | – | Uygulanmaz |
| 10 | Grafik ve veri | `pattern-texture` mantığı (renk olmadan ayırt edilme) | Geçer: biçimler lacivert hatlarla ayrılıyor, renk tek ayırıcı değil |

### 1.1 Kontrast (WCAG bağıl parlaklık, ölçüldü)

| Çift | Oran | Sonuç | Nerede |
|---|---|---|---|
| Lacivert / beyaz | 11,45 | AAA | ALFA, dış kontur, ROBOTICS |
| Lacivert / buz | 8,99 | AAA | kurt hatları |
| Lacivert / açık mavi `#63C4F2` | 5,84 | AA | 8084, gök alanları |
| Açık mavi / buz | 1,54 | – | yan yana gelmez (arada lacivert) |
| Açık mavi / beyaz | 1,96 | – | açık mavi her yerde lacivertle çevrili, sorun değil |
| **Lacivert / siyah `#111`** | **1,65** | **Kalır** (3:1 altı) | koyu zemin |
| **Lacivert / lacivert zemin** | **1,00** | **Kalır** | takım rengi zemin |

### 1.2 Renk görme ve gri ton (`3_renk_gorme.png`)
Protanopi, döteranopi ve tritanopi benzetimi (Machado 2009, tam şiddet) ve gri ton: üç rengin parlaklık sırası korunuyor, kurt, gök ve yazılar ayrışıyor. Tritanopide mavi turkuaza kayıyor, ama biçim bozulmuyor. *Test edildi (benzetim).*

### 1.3 Küçük boyut (`1_boyut_*.png`, gerçek pikseller ×4)

| Genişlik | Amblem | Yazı Logo |
|---|---|---|
| 128 px | her şey okunuyor (ROBOTICS ≈ 5 px) | her şey okunuyor |
| 96 px | ROBOTICS zorlanıyor | ROBOTICS zorlanıyor |
| 64 px | ROBOTICS okunmuyor, 8084 zor | ROBOTICS okunmuyor, ALFA / 8084 net |
| 48 px | ALFA okunuyor, kurt seçiliyor | ALFA / 8084 okunuyor |
| 32 px | kurt bir leke, ALFA zor | ALFA / 8084 zor |
| 16–24 px | tanınmıyor | tanınmıyor |

## 2. Brand / Design skill'leri – logo kuralları

| Kural | Durum | Not |
|---|---|---|
| Renk sürümleri: tam renk / ters / tek renk koyu / tek renk açık | **Yalnız tam renk var** | Bulgu 1, 4 |
| Sürümler: tam / yığılmış / yalnız simge / yalnız yazı | Amblem ve yığılmış yazı logo var; **simge yok**, yatay (amblem + yazı yan yana) yok | Bulgu 3 |
| Koruma alanı tanımlı | **Yok** | Beyaz zeminli dosyalarda %10 (≈ 36 pt) kullanıldı, kural değil |
| En küçük boyut (dijital tam logo 120 px, simge 24–32 px; baskı 35 mm) | **Tanımsız** | Ölçüm: 120 px'te ROBOTICS 4,7 px (sınırda); 35 mm baskıda ROBOTICS ≈ 1,4 mm, 8 pt iç hat 0,8 mm |
| Degrade, gölge, saydamlık, efekt yok | Geçer | düz, vektörel |
| Onaylı renkler | Geçer | 3 global örnek |
| Renk oranı 60/30/10 | Yakın geçer | lacivert %66, buz %19, açık mavi %15 |
| Ölçeklenebilirlik: 16 px'te tanınır | **Kalır** | bulgu 3 |
| Ölçeklenebilirlik: tek renkte çalışır | Geçer (test) | `4_tek_renk.png` |
| Profil fotoğrafı (daire kırpma) | Sınırda | tam boyutta kulak ve alt uç daireye çok yakın; %86 ölçekte rahat (`5_profil.png`) |
| Dosya biçimleri: SVG (web), PNG saydam, PDF (baskı) | Geçer | EPS yok (gerekmiyor) |
| Lisans / fikri mülkiyet | **Açık** | Classic Robot ticari lisansı |
| Kullanım kılavuzu (yanlış kullanım örnekleri) | **Yok** | bulgu 6 |

## 3. Bulguların ayrıntısı

**Bulgu 2 – saydam "beyazlar".** Saydam PNG / SVG / PDF'de ROBOTICS harfleri ve ALFA harflerinin arası boş (delik). Beyaz zeminde sorun yok; ama forma rengi, fotoğraf veya renkli afiş üstünde ROBOTICS zemin rengini alıyor (`2_zemin_*.png`, kırmızı örnek). Takım logolarında genelde istenen, yazının her zeminde beyaz kalması.

**Bulgu 3 – simge.** Amblemde dört katmanlı bilgi (kurt, ALFA, ROBOTICS, 8084) var; 64 px altı için tasarlanmamış. Favicon (16–32 px), uygulama simgesi ve küçük sosyal medya avatarları için ayrı bir "yalnız kalkan + kurt başı" sürümü gerekiyor.

**Bulgu 5 – baskı rengi.** PDF dolguları RGB (`0 / 0,227 / 0,435` vb.). Matbaa CMYK'ye kendisi çevirirse açık mavi `#63C4F2` matlaşabilir. CMYK ve en yakın Pantone karşılıkları tanımlanmalı. *Pantone eşleşmesi henüz yapılmadı; kartela ile doğrulanmalı.*

## 4. Önerilerim (öncelik sırasıyla)

1. **Koyu zemin sürümü** (bulgu 1): amblemin dışına **beyaz kenar** (≈ 8 pt, "çıkartma" etkisi); ALFA'nın dışarı taşan bacakları da bu kenarın içinde. Renkler değişmez. Yazı logo için **beyaz (ters)** sürüm.
2. **ROBOTICS ve iç boşlukları gerçek beyaz yap** (bulgu 2): saydam dosyalarda ROBOTICS harfleri beyaz dolgu olsun. Küçük, geri alınabilir değişiklik; görünüm beyaz zeminde aynı kalır.
3. **Simge sürümü** (bulgu 3): kalkan + kurt, yazısız. 16–32 px için ayrıca sadeleştirilmiş çizim (ince yele bıçakları azaltılmış). Favicon `.ico` + 180 / 512 px.
4. **Tek renk sürümler** (bulgu 4): lacivert ve beyaz, amblem + yazı logo. Test bunun neredeyse doğrudan çıktığını gösteriyor.
5. **CMYK + Pantone** tanımı ve CMYK baskı PDF'i (bulgu 5).
6. **Kısa kullanım kılavuzu** (1–2 sayfa PDF): renk kodları (HEX / RGB / CMYK / Pantone), en küçük boyut (öneri: amblem 128 px / 30 mm, yazı logo 128 px / 30 mm genişlik; altında simge), koruma alanı (öneri: x = ALFA yüksekliğinin yarısı ≈ 31 pt), yanlış kullanımlar.
7. **Profil fotoğrafı dosyaları**: 400 / 1080 px kare, amblem %86 ölçekte, daire kırpmaya hazır.
8. **SVG erişilebilirlik**: `<title>ALFA Robotics 8084</title>` ve `role="img"`; web'de alt metin "ALFA Robotics 8084 logosu".
9. (İsteğe bağlı) **Yatay sürüm**: amblem solda, ALFA / ROBOTICS / 8084 sağda – web başlığı, antetli kâğıt.
10. **Font lisansı**: ticari kullanım (sponsor, satılan forma) öncesi Classic Robot lisansı.

Tasarımın kendisinde (çizim, oran, renk) bu kurallara göre düzeltilmesi gereken bir hata bulmadım; öneriler **sürüm ailesi ve kullanım** üzerine.

## Doğrulama durumu
- Kontrast, renk oranı, küçük boyut, zeminler, renk görme benzetimi, tek renk, daire kırpma: **Test edildi** (`rapor2_test.py`).
- En küçük baskı boyutu (mm): **Hesaplandı**, baskıda denenmedi.
- Pantone karşılığı: **Yapılmadı.**
