# ALFA 8084 Logo – Devir Belgesi (v10 için)

Tarih: 2026-11-11. Önceki oturum çok uzadığı için iş yeni oturuma devredildi. Önce bu belgeyi, sonra `docs/NOTLAR.md` dosyasını oku.

## Amaç
ALFA Robotics 8084 (FRC) kurtlu amblemini ve yazı logosunu profesyonel, "ip gibi" (teğet süreklilikli, paralel, simetrik, dengeli kontur kalınlıklı) vektör olarak yeniden çizmek. Çıktı: Illustrator `.ai` (yerel, düzenlenebilir yollar, global renk örnekleri).

## Aşama
- Güncel onaylı sürüm: `Yeniden Olusturulan/ALFA 8084 - Amblem v8.ai` ve `ALFA 8084 - Yazi Logo v6.ai`.
- Kullanıcı v8 üzerinde 13 yer işaretledi; her biri tek tek soruldu ve cevaplandı (aşağıda). Bunlar **henüz uygulanmadı**. Sıradaki iş: bu listeyi uygulayıp **v10** olarak kaydetmek (v9 numarası denenip silindi, kullanılmasın).
- İşaretli görsel: `Yeniden Olusturulan/ALFA 8084 - v8 isaretler.png` (numaralar bu görseldeki yerler).

## Uygulanacak liste (kullanıcının cevapları)

**Genel**
- İç ve dış hatlar her yerde eş merkezli: iç kavis yarıçapı = dış kavis − kontur kalınlığı (örnek: dış r10, kontur 2 → iç r8). Kontur kavisten kalınsa iç köşe sivri.
- Buz rengi eski tona dönsün: `#D0E9E8` (şimdiki `#EBF7FC`). Kullanıcı eskisini daha iyi buldu.
- Çerçeve boyunca açık mavi iç hat **eklenmeyecek** (denendi, kullanıcı "şimdiki gibi" dedi).

**Kurt**
1. Başın arka çizgisi çerçevenin iç kenarına teğet aksın (şimdi çerçeveye küçük bir köşeyle giriyor, üstünde lacivert çıkıntı var).
2. Burnun dikey ön yüzünün üst dudağa döndüğü köşe az yumuşasın; o bölgenin üst kısmı özgündeki gibi, yalnızca hatları biraz daha yumuşak.
3. Kapalı göz özgündeki virgül biçiminde kalsın; biraz daha aşağı ve biraz daha sağa, kontura (başın sol kenarına) değmeyecek.
4. Başın sol yanındaki yele kıvrımı (iki lacivert bıçak) özgündeki gibi, yalnızca hatlar yumuşak.
5. Ağız köşesindeki açık mavi ucun yuvarlaklığı azalsın.
6. Alt çenenin ön üst ucu sivriye yakın olsun, kavis küçülsün.
7. Alt çenenin alt köşesi daha sivri, kavis küçük; açısı özgüne yakın.
8. Boğazın altındaki açık mavi alanın sol alt ucu (kesime indiği yer) sivriye yakın, küçük kavisle bitsin.
9. Boyundaki lacivert bıçak özgündeki biçimine ve yerine dönsün.
10. Sol kenarda mavi çentik ile alttaki buz yele arasındaki lacivert alan çok kalın. Karar (tasarımcıya bırakıldı): buz yele yukarı büyüsün, üst kenarı çentiğin alt kenarına paralel; aralarında 9 pt'lik eşit lacivert şerit (dudak/çene/boğaz dış hattı ile aynı kalınlık). Yelenin sol kenarı çerçeveye 6,5 pt paralel kalsın.
11. Sol alttaki buz yelenin ucu iç konturu aşıyormuş gibi görünsün: uç çerçevenin iç kenarını geçip 14 pt'lik çerçevenin içine uzansın, dış kenara varmasın.

**Kalkan ve yazı**

12. Kesim çizgilerindeki dört köşe keskin olsun (şimdi 3 pt yuvarlak): 8084 panelinin sol ve sağ üst köşeleri, üst kalkanın sol ve sağ alt köşeleri. İç açık mavi alanların aynı köşeleri de keskin. Panel kenarı sağa uzamayacak.
13. 8084 panelinin üstündeki lacivert şerit, kurdun altındaki lacivert şeritle aynı kalınlıkta olsun: 14 pt (şimdi 6,5 pt, `LW` parametresi). 8084 biraz aşağı insin ve sığan en büyük boyutta olsun. Öncelik şeritte; yazı v8'den (16,75 pt) küçük kalırsa kullanıcıya söyle.

Daire (gizli kılavuz katmanı) bu turda kalsın; kullanıcı en sonda kaldırılmasını istiyor.

## Kararlar ve tercihler (değişmeyecekler)
- A düzeni: daire kalkan ekseninde, burun / alt uç / iki A bacağı daireye teğet. B düzeni (kare sınır, ortalanmış daire, v9) denendi ve reddedildi.
- Lacivert tek siluet; gök ve buz alanları üstünde. Lacivert lacivertin üstüne binmez.
- Ağız, çene ve soldaki göz/kulak özgün çizime benzer olmalı (kullanıcı birkaç kez "eskisine benzet" dedi).
- ROBOTICS / 8084: Classic Robot Bold Italic (`E:\2026 masaüstü\Classic Robot`), ölçek ve eğim bozulmadan.
- Her sürüm yeni numarayla kaydedilir; eskinin üstüne yazılmaz. Özgün dosyalara dokunulmaz.

## Kullanıcıyla çalışma biçimi
- Türkçe, kısa, sonuç önce. Kullanıcı tasarım kararlarını bana bırakıyor ama işaretli ekran görüntüleriyle geri bildirim veriyor.
- Belirsiz işaretlerde görselle göstermek iyi çalıştı (kullanıcı "görselle göster" diyor).
- Uzun işlerde ara durum bildir. Kullanıcı Remote Control üzerinden de takip ediyor; önizlemeleri SendUserFile ile gönder.

## Başarısız yöntemler
- Alt çeneyi döndürüp sıkıştırmak; ince çubuk çene; tam yuvarlak uçlu kalın çene; çene altında düz parça + dirsek; düz kama çene; ince hilal göz; badem göz + göz bebeği.
- Boşluk kapatmak için kalkanı genişletmek (köşeler daireden taştı).
- Kare sınır + ortalanmış daire (v9, `kaynak/patch9.py`).

## Önemli dosyalar ve nasıl üretilir
Tüm kaynak `kaynak/` klasöründe; v8 ile piksel düzeyinde aynı çıktıyı verdiği doğrulandı (0 fark).
- `mk5.py`: `design.py` (yazı, font, çıktı) + `wolf5_block.py` (kurt, gök alanları, lacivert siluet) → `design5.py` üretir. Yazı/kalkan parametre değişiklikleri `mk5.py` içindeki `rep(...)` satırlarında; kurt değişiklikleri `wolf5_block.py` içinde.
- `geo.py`: geometri kiti (doğru/yay, öteleme, kırpma, fillet, bezier). `logo1.json`: özgün kurt düğümleri (`W["G"]`, `W["H"]`, `W["B"]`, `W["Y"]`, `W["Z"]`, `W["D"]`).
- Çalıştırma (`kaynak` klasöründe):
  1. `python mk5.py`
  2. `python design5.py . "E:/2026 masaüstü/Classic Robot/Classic Robot Bold Italic.otf"` → `emblem.json`, `wordmark.json`, `emblem.png`, `emblem_check.pdf`
  3. `python mkjsx2.py build.jsx emblem.json "<hedef Amblem v10.ai>" wordmark.json "<hedef Yazi Logo v10.ai>"`
  4. PowerShell: `$ai = New-Object -ComObject Illustrator.Application; $ai.DoJavaScriptFile("<tam yol>\build.jsx")`
  5. Doğrulama: `python diff.py emblem_check.pdf "<Amblem v10.ai>" e5.clip d.png` (artboard boyutu değişirse `.clip` dosyasını güncelle).
- `gridview.py`: ızgaralı yakın önizleme (`python gridview.py emblem_check.pdf 19 9.33 x0 y0 x1 y1 zoom out.png`; 19 / 9.33 artboard kaydırması).
- Gerekli Python paketleri kurulu: pymupdf, pillow, numpy, fonttools.

## İlk yapılacak iş
1. Bu belgeyi ve `docs/NOTLAR.md` dosyasını oku; `kaynak/` ile v8'i yeniden üretip 0 fark olduğunu doğrula.
2. Listeyi kullanıcıya kısaca hatırlat ve "başla" onayı al (kullanıcı listeyi onaylamadan oturumu devretti).
3. Maddeleri uygula, her biri için ızgaralı önizlemeyle kontrol et; eş merkez kuralını ölçerek doğrula.
4. v10 `.ai` dosyalarını üret, piksel karşılaştırmasıyla doğrula, önizlemeleri gönder, `NOTLAR.md` dosyasını güncelle.
