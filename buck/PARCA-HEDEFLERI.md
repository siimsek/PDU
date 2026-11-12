# Parça Kriterleri ve Aday Parçalar — Ana Güç Devresi

**Tarih:** 12 Kasım 2026
**Durum:** Parçalar **kesinleşmedi**. Aşağıdaki liste "olabilir" listesidir: kriterlerle yapılan dış araştırmanın adayları, LTspice köşe testindeki paya göre sıralanmıştır. Şematik, listenin başındaki **1. sıra adayların** değerlerini taşır (L1 için el sarım hesabı, diğerleri veri sayfası); bu bir satın alma kararı değildir. Kriterleri sağlayan başka bir parça aynı yolla (bkz. "Parça değiştiğinde") 1. sıraya geçebilir.
**Sınıf:** analitik hesap (`hesap.py`) + LTspice, ideal elemanlar (`dogrula.py`). Fiziksel ölçüm yok.
**Dondurma durumu:** **FROZEN (simülasyon dondurması, 12 Kasım 2026)** — çıkış sönüm dalı (`Cd = 470 µF + seri Rd = 0,22 Ω`) eklendi, tüm köşe testleri geçti; gerilim sınıfları **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** olarak kararlaştırıldı ve simülasyon dondurması kullanıcı onayıyla tamamlandı. Parçalar ve bobin, bu belgedeki dondurulmuş hedef aralıklara göre seçilir / sarılır. Ayrıntı [OPTIMIZASYON.md](OPTIMIZASYON.md) §12.

**Seçim öncesi sınır (13.11.2026):** Bu değerler aday eleme hedefidir, fiziksel güvenlik veya tüm tolerans kombinasyonları için garanti değildir. Gerilim sınıfları yalnız varsayılan kaynak/kablo ve arıza modellerindeki tepelere dayanır: 31,1 V'a karşı 35 V yaklaşık %12,5, 46,5 V'a karşı 50 V yaklaşık %7,5 nominal pay bırakır; yaşlanma, sıcaklık, tolerans ve gerçek darbeler kapsanmaz. Çalışma sıcaklığı aralığı, ortam, ömür ve gerçek kaynak empedansı belirlenmeden nihai termal pay ve gerilim deratingi belirlenemez. Anahtarlama zili için S1/D1 gerilim payı ölçülmelidir; simüle edilen 9–12 V O1/S2E ölçütü genel modül spesifikasyonu değildir.

Seçim sırasında her aday için belirtilen L/C, ESR/DCR ve dal direncinin **çalışma sıcaklığı, frekans, DC akım/gerilim, tolerans ve yaşlanma dahil** durumu; kondansatör ripple akımı ve ömrü; bobin L(I), doyum ve sıcaklığı; S1 için VDS, VGS, sıcak RDS(on), Qg ve SOA; D1 için VRRM, ortalama/RMS/darbe akımı, sıcak VF ve kaçak; Rd için sıcak güç ve darbe dayanımı; soğutucu ve yalıtım için toplam ısıl yol doğrulanmalıdır. Veri yoksa sınır **doğrulanmadı** olarak kalır. Fiziksel ölçüm ve gerçek parçalarla yeniden simülasyon henüz yapılmadı.

Çalışma noktası: Vin 20 / 22,2 / **24,6** / 25,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz. Seçim süreci ve test sonuçları: [OPTIMIZASYON.md](OPTIMIZASYON.md).

## Aday parçalar (kesin seçim değil)

### 1. sıra — şematikte kullanılan değerler

| Eleman | Parça | Veri sayfası değeri | Şematikte | Stok ve fiyat (11.11.2026) |
|---|---|---|---|---|
| **L1** (1. sıra, el sarım) | Magnetics **Kool Mµ 40µ `0077536A7`** toroid, 22 sarım, 100 × 0,20 mm litz | 33,4 µH (AL 69 nH ±%8 → 30,7–36,1 µH); Ae 174 mm², le 126 mm, Ve 22 cm³; DC bias %80 @ 58,5 Oe, %50 @ 133 Oe; çekirdek kaybı en çok 900 mW/cm³ @ 100 kHz / 100 mT (DATASHEET, 0077536A7 rev. 6/1/2022). L(8,9 A) ≈ %97, L(12 A) ≈ %95, L(53 A) ≈ %59 (bias eğrisinden okuma); DCR 7,81 mΩ @20 °C (HESAP), 9,5 mΩ @75 °C; kayıp 0,58 W @20 °C / 0,72 W @100 °C sargı (bakır 0,44–0,58 W + çekirdek ≤ 0,14 W, HESAP) — **fiziksel ölçüm yok** | 33 µH, `Rser=7.81m` | Çekirdek ve tel ayrı temin; ölçüm gerekir |
| **L1** (2. sıra, satın alma) | Würth **74435583300** (WE-HCI, yüzey montaj, ekranlı) | 33 µH ±%20 (100 kHz, 10 mA); 30,5 µH tipik @ 11,5 A; Irms 11,5 A (ΔT 50 K); 10,6 A (ΔT 40 K); Isat 12,5 A (−%10) ve 15 A (−%30), **ikisi de tipik**; DCR 13,2 mΩ ±%10 @ 20 °C (maks 14,52 mΩ; sıcakta artar). 9 A'de düşüm ≈ %3 (L–I eğrisinden yaklaşık okuma, ikinci el rapor); çekirdek kaybı verisi datasheet'te yok | şematikte değil (el sarım 1. sırada) | Digi-Key 260 adet, 7,34 $ |
| **Cout** | Nichicon **UHE1E102MHD6TO** *(elektriksel R/C referansı; **25 V < yeni ≥35 V kriteri**)* | 1000 µF ±%20; 25 V; 105 °C; **empedans** en çok 35 mΩ (100 kHz, 20 °C) ve 120 mΩ (100 kHz, −10 °C) — ESR değildir; ripple akımı 1,90 A (105 °C, 100 kHz). **Not:** 12.11.2026 kararıyla Cout kriteri ≥ 35 V olduğundan kesin parça aşağıdaki ≥ 35 V adaylardan seçilecektir | 1000 µF, `Rser=35m` | Mouser 336 adet, 1,22 € |
| **Cd + Rd** (çıkış sönüm dalı) | Henüz 1. sıra seçilmedi *(doğrulanmış adaylar aşağıdaki listededir)* | Hedef aralık: **Cd = 470 µF ±%20, ≥ 35 V**, 105 °C elektrolitik; **Rd = 0,22 Ω** ayrık direnç (Cd ESR'si dahil toplam dal direnci **0,15–0,60 Ω**), ≥ 0,25 W (anlık darbe dayanımlı) | `Cd=470u`, `Rd=0.22` | Özdisan ve TME/Mouser/Digi-Key stoklu adaylar var |
| **Cin1, Cin2** | 2 × TDK **B41859D7108M000** *(elektriksel R/C referansı; **35 V < yeni ≥50 V kriteri**)* | 1000 µF ±%20; 35 V; 105 °C; 16 × 20 mm; empedans (Zmax) 15 mΩ (100 kHz, 20 °C), 38 mΩ (−10 °C) — ESR değildir, ESL ≈ 26 nH ≈ 16 mΩ reaktans aynı büyüklükte; ripple akımı 3,25 A/adet (105 °C, 100 kHz) → 6,5 A. **Not:** 12.11.2026 kararıyla Cin kriteri ≥ 50 V olduğundan kesin parça aşağıdaki ≥ 50 V adaylardan seçilecektir | 2 × 1000 µF, `Rser=15m` | Farnell Türkiye 2.914 adet, 2,31 € + KDV |
| **S1** | STMicroelectronics **STP100N6F7** (TO-220) | 60 V; RDS(on) 4,7 tipik / 5,6 mΩ maks (VGS 10 V, 50 A, 25 °C; en düşük değer yayımlanmamış); ID 100 A; Qg 30 / Qgs 12,6 / Qgd 5,9 nC tipik; Coss 970 pF @25 V; Rth(j-c) 1,2 K/W; Tj 175 °C | `Ron=5.6m` | Digi-Key 2.105 adet, 2,08 $ |
| **D1** | STMicroelectronics **STPS40M60CT** (TO-220AB, iki bacak paralel) | 60 V; 2 × 20 A; VF tipik/maks 0,430/0,460 V @ 5 A/bacak, 25 °C (125 °C: 0,325/0,355 V); IR maks 110 µA @25 °C, **85 mA @125 °C** (bacak başına, 60 V); Rth(j-c) toplam 0,95 K/W; Tj 150 °C | `Vf=0.38 Ron=8m` (7,5 A'de 0,44 V) | Digi-Key 1.010 adet, 2,81 $ |

**Neden bu set 1. sırada (LTspice köşe testi, 11.11.2026; köşe = bobin +%20, Cout −%20, ESR alt kenarda; Würth bobin DCR'siyle ve 20 ms'lik darbeyle — güncel 200 ms sonuçları [OPTIMIZASYON.md](OPTIMIZASYON.md) §4.4 ve §6'dadır):**

| Bobin | Çıkış kondansatörü | Ripple anma / köşe | S2E kalkışı, köşe | O1 yük adımı, köşe | Sonuç |
|---|---|---|---|---|---|
| **33 µH (74435583300)** | **Nichicon UHE, 35 mΩ** | 65 / 96 mV | 10,58–11,32 V | 10,01–11,81 V | **Geçti (1. sıra)** |
| 33 µH (74435583300) | 18 mΩ'luk aday (KEMET ESY, Chemi-Con KZH) | 39 / 54 mV | 10,54–11,39 V | 9,98–11,79 V | Geçti; 73 W'ta 0,5 V salınım |
| 47 µH (7443783533470) | Nichicon UHE, 35 mΩ | 46 / 69 mV | 10,57–11,37 V | 9,86–11,93 V | Geçti; 12 V'a 0,07 V pay |
| 47 µH (7443783533470) | 18 mΩ'luk aday | 24 / 33 mV | 9,24–12,83 V | 9,62–12,24 V | **Kaldı**; 2,6–3,6 V salınım |

- **Cout için 35 mΩ'luk parça bilerek öne alındı.** Veri sayfasındaki 35 mΩ **en büyük empedanstır** (|Z| 100 kHz'te), ESR değildir; üretici ESR için ne alt ne tipik değer verir. Modeldeki `Rser=35m` ve 15 mΩ alt kenar (35 mΩ'un ≈ %43'ü; eski %60 ifadesi tutmuyordu) **varsayımdır**, veri sayfası değeri değildir. Soğukta (−10 °C) Zmax 120 mΩ'dur; bu koşul simülasyonda yoktur. 15–35 mΩ penceresi bu parça için ancak 0,5–2 kHz ve 100 kHz'te, sıcaklığa göre ölçümle kanıtlanır.
- **S1 için en düşük dirençli değil, en düşük kapı yüklü aday öne alındı.** İletim kaybı 5,6 mΩ'da zaten 0,15 W'tır; 30 nC kapı yükü sonraki aşamada sürücüyü kolaylaştırır ve anahtarlama kaybını düşürür.
- **L1 için 33 µH**, 47 µH'den daha geniş sönüm payı verir. 1. sıra el sarım bobindir (hocanın önerisi; hazır bobinlerin Isat değeri garanti edilmez); satın alınan Würth 74435583300 2. sıradadır (Isat tipik).

**Doğrulama durumu:**
- Üretici PDF'inden okunup doğrulandı (DATASHEET, 12.11.2026; Würth rev. 002.001 2025-02-06, Nichicon CAT.8100M, TDK B41859): Würth 74435583300, Nichicon UHE1E102MHD6TO (seri PDF + parça sayfası), TDK B41859D7108M000. TDK sipariş kodu geri çekilen ürün listesinde yoktur (rapora göre; sayfa 1). Würth L–I eğrisi (eğriden, yaklaşık): 9 A'de ≈ 32,0 µH, 11,5 A'de 30,5 µH, 12,5 A'de ≈ 29,5 µH; bu "%3–5 düşüm" ifadesini destekler (düşük L köşesi −%30 bunu kapsar). Doğrulananlar ve koşulları yukarıdaki tabloda; Isat tipiktir, 35 / 15 mΩ en büyük empedanstır.
- **ST parçaları (DATASHEET, 12.11.2026):** STPS40M60C Doc ID 018813 Rev 1 (Mayıs 2011) PDF'i dağıtıcı kopyasından açılıp okundu (Tablo 2–4, Şekil 8–11). STP100N6F7'nin TO-220 belgesi (DocID027212) bu ortamda **açılamadı**; aynı kırmığın D²PAK sürümü STB100N6F7 DocID027210 Rev 2 (Ocak 2015) okundu, elektriksel tablolar oradan alındı. TO-220 kılıfına özgü Rth(j-amb) ve ayak ölçüleri **DOĞRULANAMADI**.
  - S1: V(BR)DSS ≥ 60 V; VGS(th) 2–4 V; RDS(on) 4,7 tipik / 5,6 mΩ maks (VGS 10 V, ID 50 A); Ciss 1980 / Coss 970 / Crss 86 pF (VDS 25 V); Qg 30 / Qgs 12,6 / Qgd 5,9 nC (VDD 30 V, ID 100 A); td(on) 21,6 / tr 55,5 / td(off) 28,6 / tf 15 ns (VDD 30 V, ID 50 A, RG 4,7 Ω); Rth(j-c) 1,2 K/W; Tj 175 °C; EAS 200 mJ. RDS(on) sıcaklık çarpanı (Şekil 10, eğriden): 100 °C ≈ ×1,4, 150 °C ≈ ×1,65. RDS(on) için **en düşük değer yayımlanmamıştır**; sönüm hesabında tipik 4,7 mΩ kullanıldı.
  - D1 (diyot başına): VF tipik/maks 5 A'de 0,430/0,460 V (25 °C), 0,325/0,355 V (125 °C); 10 A'de 0,470/0,505 V, 0,385/0,435 V; 20 A'de 0,540/0,595 V, 0,475/0,535 V. IR 25 µA tipik / 110 µA maks (25 °C), 85 mA maks (125 °C), VR 60 V. Rth(j-c) 1,40 K/W diyot başına, 0,95 K/W toplam, bağlaşım 0,50 K/W. İletim kaybı P = 0,395·IF(AV) + 0,007·IF²(RMS): tablodaki 125 °C **azami** VF'nin 20–40 A doğrusudur. Isıl kaçak koşulu (Tablo 2 dipnot 3): dPtot/dTj < 1/Rth(j-a). Eklem kapasitesi (Şekil 9, eğriden): ≈ 2,7 nF @1 V, ≈ 0,6 nF @25 V.
  - Yayımlanmayanlar: 3,75 A/bacak VF sayısı, 150 °C VF, 26 V'ta IR (Şekil 8 tipik eğrisinden ≈ 60 V değerinin yarısı, ÇIKARIM), Nichicon/TDK ESR ve ESR–frekans/sıcaklık eğrileri, UHE/B41859 SPICE modeli.
- Ron = 5,6 mΩ 25 °C, VGS = 10 V, ID = 50 A'de **azami** değerdir; eklem sıcaklığında artar ve ideal anahtar modeli sıcaklık, anahtarlama kaybı ve kapı yükünü içermez. Kayıp ve ısı kestirimi: [OPTIMIZASYON.md](OPTIMIZASYON.md) §9.
- D1 modeli (0,38 V + 8 mΩ) iki tipik noktadan çıkarıldı; **yaklaşıktır**. 7,5 A'de 0,44 V verir (kayıp yönünden 25 °C tipikten ≈ 20 mV kötümser). **Artımsal direnci iyimserdir:** iki bacak paralelken tablo noktalarından çiftin eğimi 25 °C tipik 4 mΩ, 125 °C tipik 6 mΩ'dur (10–20 A toplam); şematikteki 8 mΩ tek diyodun eğimidir. Sönüm hesabında bu yüzden ayrı bir "en az sönüm" seti (0,39 V + 4 mΩ) kullanılır ([OPTIMIZASYON.md](OPTIMIZASYON.md) §8). Şematik değeri kullanıcı kararı olmadan değiştirilmedi. Çift diyodun akım paylaşımı modelde yoktur.

### L1 için sıralama kararı (kullanıcı, 12.11.2026)

**1. sıra: el sarım bobin. 2. sıra: satın alma** (Würth 74435583300 ve aşağıdaki diğer adaylar). Neden: hazır bobinlerin doyma akımı (Isat) değerleri tipiktir, garanti edilmez; el sarımda Isat çekirdek verisinden hesaplanır ve ölçülür (hocanın önerisi). Şematik (33 µH, DCR 7,81 mΩ @20 °C) el sarım değerlerini taşır; sarılıp ölçülünce DCR güncellenir.

| Tasarım (ChatGPT raporu, HESAP; fiziksel ölçüm yok) | L0 | L(8,9 A) / L(12 A) | DCR 20 °C / 75 °C | Toplam kayıp (2,8 A ripple) | Sonuç |
|---|---|---|---|---|---|
| **Magnetics Kool Mµ 40µ `0077536A7`, 22 sarım, 100 × 0,20 mm litz** | 33,4 µH (AL 69 nH ±%8) | 32,3 / 31,6 µH (%96,7 / %94,6, üretici μ%–H fit'i) | 7,81 / 9,50 mΩ | rapor: ≈ 0,75 W (çekirdek 0,22 + bakır 0,53); bağımsız HESAP: çekirdek ≤ 0,14 W, bakır 0,44–0,54 W | **1. sıra**; bias ölçütünü rahat sağlar |
| Micrometals T130-52, 21 sarım | 34,8 µH | 28,6 / 25,2 µH (8,9 A'de %18 düşüm) | 5,45 / 6,63 mΩ | ≈ 2,5 W, ΔT ≈ 60–125 °C (TAHMİN) | Elenir: 9 A düşüm ölçütü ve kayıp |
| TDK N87 ETD39, ayarlı aralık, 18 sarım | hedef 32,4 µH | DOĞRULANAMADI | 8,5 / 10,4 mΩ | DOĞRULANAMADI | Ölçüm olmadan kabul edilemez |

Bağımsız kontrol (HESAP, 12.11.2026; çekirdek değerleri üretici veri sayfasından, rev. 6/1/2022): AL = μ0·μ·Ae/le = 69,4 nH; N = 22 → 33,4 µH; H(8,9 A) = 19,5 Oe → μ% ≈ %97; DCR20 = 7,8 mΩ (22 × 66,5 mm tel, 3,14 mm² bakır). **Çekirdek kaybı:** ΔB = volt·saniye / (N·Ae) = 13–17 mT t-t (20–26 V giriş); veri sayfasının azami noktası (900 mW/cm³ @ 100 kHz, 100 mT) B² ile ölçeklenince ≤ 0,09–0,14 W (ÇIKARIM: B üssü 2 alındı). Rapordaki 0,22 W **doğrulanamadı**: çekirdek kaybı akım ripple'ına değil volt·saniyeye bağlıdır, L −%30 köşesinde (ΔIL 2,8 A) ΔB değişmez. Diğer sayılar tutarlı çıktı. Çekirdek, bobin ve sarım Türkiye'de ayrı ayrı temin edilir (Magnetics `0077536A7` Farnell/Mouser/TME/RS'de bu kodla doğrulanamadı; Micrometals ve TDK çekirdekleri TME'de listeli).

**SİM köşe testi (20 °C, Cout Nichicon 35 mΩ, köşe: L −%30/+%20, Cout −%20; `pencere()` kararının 20 ms'lik darbeye bakan eski sürümü). Bu tablodaki "GEÇTİ" sonuçları 200 ms'lik darbeyle geçerli değildir: salınım sütunundaki 0,7–1,6 V değerleri sönmeyen salınımdır ([OPTIMIZASYON.md](OPTIMIZASYON.md) §6):**

| El sarım değişkeni | Köşe ripple | 73 W zarf adımı | 73 W salınım (57,6 / 73 W) | O1 adımı | Karar |
|---|---|---|---|---|---|
| 33 µH, DCR 9,5 mΩ (sıcak) | 96 mV | 10,53–11,43 V | 170 / 738 mV | 9,98–11,85 V | GEÇTİ |
| 33 µH, DCR 7,81 mΩ (20 °C) | 102 mV | 10,43–11,54 V | 309 / 1100 mV | 9,98–11,86 V | GEÇTİ |
| 33 µH, DCR 6,5 mΩ (tel/sarım toleransı alt sınırı) | 96 mV | 10,19–11,78 V | 567 / 1593 mV | 9,98–11,87 V | GEÇTİ (12 V'a 0,22 V pay) |
| **47 µH (26 sarım, 46,6 µH), DCR 9,2 mΩ** | 69 mV | 9,45–**12,61 V** | 2567 / 3165 mV | 9,65–12,24 V | **KALDI** |

Karşılaştırma: Würth 74435583300 (DCR 14,5 mΩ) 51 / 216 mV salınım verir. **Sonuç:** 33 µH el sarım simülasyonda geçer, ama DCR düştükçe sönüm zayıflar ve 73 W darbesinde salınım büyür; bu yüzden **DCR için alt sınır gerekir (≥ 6,5 mΩ, 20 °C; hedef 8–10 mΩ)**, ESR alt sınırıyla aynı nedenle. 47 µH el sarım DCR yüksek olmadığı için sönümsüz kalır ve kalır; 47 µH seçeneği yalnız satın alınan Würth 7443783533470 (DCR en çok 12,98 mΩ) ile denenebilir.

**Karar (kullanıcı, 12.11.2026):** şematiğe nominal DCR 7,81 mΩ (20 °C) yazıldı; 9,5 mΩ (75 °C) sıcak çalışma köşesi, 6,5 mΩ şimdiye kadar denenen en düşük sönüm köşesi. Doğrulanmış DCR sınırı 6,5–15 mΩ; el sarım hedefi 8–10 mΩ. Gerçek bobin sarılınca DCR ölçülüp model güncellenir. `secilen` ve `pencere` bu değerlerle yeniden koşuldu ([OPTIMIZASYON.md](OPTIMIZASYON.md) §4.4, §5). Fiziksel doğrulama adımları: 100 kHz'te L0 ve 4 telli DCR; 0 / 5 / 8,9 / 10,6 / 12 A DC bias'ta L(I) (8,9 A'de ≥ %90); 50 °C ortamda 7,5 A DC + 2,8 A ripple ile sıcaklık; 10–12 A kalkış darbesi.

### Diğer adaylar ve yeni gerilim sınıflarına göre doğrulanmış adaylar (12.11.2026)

Aşağıdaki adaylar üretici PDF veri sayfalarından (**DATASHEET**) ve 12.11.2026 tarihli satıcı sorgularından doğrulanmıştır. Japon/Kore/Koshin elektrolitik serilerinin veri sayfalarında **100 kHz ESR yayımlanmamıştır (`doğrulanamadı`)**; tablolardaki mΩ değerleri üretici belgesindeki **100 kHz maksimum empedans (`|Z|max`)** değeridir (yalnız KEMET `ESY` tekil şartnamesi `Resistance @ 100 kHz` başlığını kullanır). Şematikteki 1. sıra değerler kullanıcı kararı olmadan değiştirilmemiştir.

| Eleman | Sıra / Öncelik | Parça | Veri sayfası değerleri (DATASHEET) | Stok, fiyat ve not (12.11.2026) |
|---|---|---|---|---|
| **L1** | 2 (satın alma) | Würth `7443783533330` (delikli) | 33 µH; Isat 39 A; Irms 22 A; DCR 9,9 mΩ maks | Elektriksel olarak Würth SMD'den iyi; Digi-Key'de yalnız 18 adet |
| **L1** | 3 (satın alma) | Würth `7443783533470` (delikli) | 47 µH; Isat 32 A; DCR 13 mΩ maks | Sönüm dalıyla geçer ama kullanıcı kararıyla 33 µH tercih edilir. Digi-Key 645 adet |
| **L1** | 4 (satın alma) | Würth `7443763540470` (delikli) | 47 µH; Isat 31 A; DCR 6,4 mΩ maks | 3. sırayla aynı not; Digi-Key 838 adet, 21,43 $ |
| **Cout** (≥35 V) | Aday 1 (TR stoklu) | Panasonic **`EEUFS1V102L`** (`EEU-FS1V102L`) | 1000 µF ±%20; **35 V**; 105 °C / 10.000 sa; `Ø10×25 mm`, `P=5,0 mm` (THT); `|Z|max` **18 mΩ** @20 °C, **54 mΩ** @−10 °C (ESR doğrulanamadı); ripple **2,47 A** (`ABA0000C1255`) | **Özdisan 1.970 stok**, 43,73 TL + KDV. Soğuk (−10 °C Zmax) köşesinde bile SİM ripple **130,3 mV ≤ 165 mV** |
| **Cout** (≥35 V) | Aday 2 (TR stoklu) | Samwha **`LQ1V108M12020PL`** | 1000 µF ±%20; **35 V**; 105 °C / 10.000 sa; `Ø12,5×20 mm`, `P=5,0 mm` (THT); `|Z|max` **25 mΩ** @20 °C (ESR ve −10 °C 100 kHz Zmax doğrulanamadı); ripple **2,80 A** | **Özdisan 1.000 stok**, 17,28 TL + KDV. En dengeli 20 °C empedans |
| **Cout** (≥35 V) | Aday 3 | Panasonic **`EEUFC1V102`** | 1000 µF ±%20; **35 V**; −55…+105 °C / 5.000 sa, AEC-Q200; `Ø12,5×25 mm`, `P=5,0 mm`; `|Z|max` **30 mΩ** @20 °C, **60 mΩ** @−10 °C; ripple **1,945 A** | **TME 6.044 stok**, 1,44 $ (1+). −10 °C köşesinde SİM ripple **135,9 mV ≤ 165 mV** |
| **Cout** (≥35 V) | Aday 4 | Panasonic **`EEUFR1V102`** *(50 V: `EEUFR1H102`)* | 1000 µF ±%20; **35 V**; 105 °C / 10.000 sa; `Ø12,5×20 mm`, `P=5,0 mm`; `|Z|max` **18 mΩ** @20 °C, **45 mΩ** @−10 °C; ripple **2,60 A** | **TME 31.793 stok** (1,31 $), LCSC 553 stok (0,63 $). −10 °C köşesinde **107,1 mV** |
| **Cout** (≥35 V) | Aday 5 | Nichicon **`UHE1V102MHD`** *(veya NCC `EKY-350ELL102MK25S`)* | 1000 µF ±%20; **35 V**; 105 °C / 10.000 sa; `Ø12,5×25 mm`, `P=5,0 mm`; `|Z|max` **27 mΩ** @20 °C, **89 mΩ** @−10 °C; ripple **2,23 A** (`CAT.8100M`) | **LCSC 1.582 stok** (0,47 $), Digi-Key 7.699 stok (1,61 $). −10 °C Zmax tamamı ESR sayılırsa 195 mV |
| **Cout** (≥35 V) | Aday 6 | KEMET **`ESY108M035AL4AA`** *(veya Rubycon `35ZLH1000MEFC12.5X20`)* | 1000 µF ±%20; **35 V**; 105 °C / 5.000 sa; `Ø13×25 mm`, `P=5,0 mm`; `Resistance` **18 mΩ** @100 kHz, 20 °C (−10 °C doğrulanamadı); ripple **2,77 A** | LCSC 100 stok (1,38 $); Rubycon `35ZLH` (`17 mΩ` / `43 mΩ`, 2,48 A) LCSC 8.785 stok (0,36 $) |
| **Cd** (≥35 V) | Aday 1 (TR stoklu) | Koshin **`PKLH-050V471MG200`** *(63 V: `PKLH-063V471MH200-T/A5.0`)* | 470 µF ±%20; **50 V**; 105 °C / 3.000 sa; `Ø10×20 mm`, `P=5,0 mm` (THT); `|Z|max` **70 mΩ** @20 °C (−10 °C Zmax doğrulanamadı); ripple **1,27 A** (`DJJ-2875`) | **Özdisan 2.249 stok**, 6,07 TL + KDV (`63 V / 80 mΩ / 5.000 sa` sürümü Özdisan **5.265 stok**, 6,54 TL + KDV) |
| **Cd** (≥35 V) | Aday 2 | Panasonic **`EEUFR1V471`** *(50 V: `EEUFR1H471`)* | 470 µF ±%20; **35 V**; 105 °C / 8.000 sa; `Ø10×16 mm`, `P=5,0 mm` (THT); `|Z|max` **28 mΩ** @20 °C, **78 mΩ** @−10 °C (≤ 350 mΩ); ripple **1,79 A** | **TME 9.510 stok** (0,83 $), LCSC 705 stok (0,47 $); 50 V `EEUFR1H471` (`22 / 55 mΩ`) TME 5.450 stok |
| **Cd** (≥35 V) | Aday 3 | Nichicon **`UHE1V471MPD`** *(veya Rubycon `50ZLJ470M10X20`)* | 470 µF ±%20; **35 V**; 105 °C / 7.000 sa; `Ø10×20 mm`, `P=5,0 mm`; `|Z|max` **46 mΩ** @20 °C, **180 mΩ** @−10 °C; ripple **1,40 A** | **TME 561 stok** (0,67 $); Rubycon `50ZLJ470M10X20` (50 V, `37 / 110 mΩ`, 2,50 A) LCSC 13.555 stok |
| **Rd** (0,22 Ω) | Aday 1 (TR stoklu, THT) | YAGEO **`MFR200FTF73-0R22`** | **0,22 Ω ±%1**; **2 W** @70 °C; THT eksenel metal film (tel sarım değil), `Ø5,0×15,5 mm`, AEC-Q200; 5 s aşırı yük 12,5 W, periyodik darbe 32 W | **Özdisan 4.891 stok**, 0,085 $ + KDV. *(THT alternatif: Vishay `PR01000102207JA100` 0,6 W, Mouser 2.503 stok)* |
| **Rd** (0,22 Ω) | Aday 2 (SMD 2512) | Bourns **`CRM2512-FX-R220ELF`** | **0,22 Ω ±%1**; **2 W** @70 °C; 2512 bakır bazlı kalın film; doğrudan `<1 Ω` darbe eğrisi: 1 ms **0,12 J** (120 W), 10 ms **0,37 J** (37 W) | **Digi-Key 9.345 stok** (0,64 $). `½·Cd·ΔV² ≈ 0,06–0,22 J` darbe enerjisi grafikle kanıtlı |
| **Rd** (0,22 Ω) | Aday 3 (SMD 2512) | Vishay **`WSL2512R2200FEA`** *(veya YAGEO `RL2512FK-070R22L`)* | **0,22 Ω ±%1**; **0,94 W** (1 W anma, >0,1 Ω düşümlü); 2512 katı metal şerit (`0,5–5 nH`), AEC-Q200 | **LCSC 8.565 stok** (0,49 $), **Mouser 39.928 stok** (1,00 $); `RL2512` (1 W kalın film) DK 10.036 / Mouser 7.998 stok |
| **Cin** (≥50 V, 2×) | Aday 1 | 2 × Panasonic **`EEU-FR1H102`** (`EEUFR1H102`) | 1000 µF ±%20; **50 V**; 105 °C / 10.000 sa; `Ø16×25 mm`, `P=7,5 mm` (THT); `|Z|max` **16 mΩ** @20 °C, **40 mΩ** @−10 °C; ripple **3,32 A/adet → 6,64 A** (`ABA0000C1259`) | **TME 9.765 stok** (2,11 $), **Mouser 8.067 stok** (2,72 $), **Digi-Key 1.770 stok** |
| **Cin** (≥50 V, 2×) | Aday 2 | 2 × Panasonic **`EEU-FM1H102`** *(bantlı: `EEUFM1H102B`)* | 1000 µF ±%20; **50 V**; 105 °C / 7.000 sa; `Ø16×25 mm`, `P=7,5 mm`; `|Z|max` **16 mΩ** @20 °C, **40 mΩ** @−10 °C; ripple **3,32 A/adet → 6,64 A** (`ABA0000C1018`) | **Digi-Key 11.991 stok** (2,22 $), **TME 690 stok** (`B`, 1,93 $), Newark 12.723 stok |
| **Cin** (≥50 V, 2×) | Aday 3 | 2 × Nichicon **`UHW1H102MHD`** *(veya `UHE1H102MHD`)* | 1000 µF ±%20; **50 V**; 105 °C / 10.000 sa; `Ø12,5×30,5 mm`, `P=5,0 mm`; `|Z|max` **20 mΩ** @20 °C, **60 mΩ** @−10 °C; ripple **3,50 A/adet → 7,00 A** (`CAT.8100N`) | **Mouser 3.181 stok** (2,26 $), **LCSC 521 stok** (1,06 $); `UHE1H102MHD` (`21 mΩ`, 5,84 A) Mouser 3.828 stok |
| **Cin** (≥50 V, 2×) | Aday 4 | 2 × KEMET **`ESY108M050AM2AA`** *(veya Rubycon `50ZLJ1000M16X25`)* | 1000 µF ±%20; **50 V**; 105 °C / 5.000 sa; `Ø16×32 mm`, `P=7,5 mm`; ESR/Z **21 mΩ** (−10 °C doğrulanamadı); ripple **3,35 A/adet → 6,70 A** | Newark 1.786 stok (3,35 $), LCSC yalnız 10 stok; Rubycon `50ZLJ` (`22 mΩ`, 7,02 A) Mouser 455 stok |
| **S1** | 2 | Infineon `IPP034N08N5` | 80 V; 3,4 mΩ; Qg 87 nC maks | Gerilim payı en yüksek |
| **S1** | 3 | Infineon `IPP030N06NF2S` | 60 V; 3,05 mΩ; Qg 102 nC maks | En düşük direnç, en yüksek kapı yükü |
| **S1** | 4 (TR stoklu) | STMicroelectronics `STP75NF75` | 75 V; 11 mΩ; Qg 117 nC | **Türkiye stoklu** (Özdisan 5.340 adet) |
| **D1** | 2 | STMicroelectronics `STPS30L60CT` | 60 V; 2 × 15 A; ≈ 0,5 V @ 3,75 A/bacak | Digi-Key 856 adet |
| **D1** | 3 (TR stoklu) | IXYS `DSB60C60HB` (TO-247) | 60 V; 2 × 30 A; 0,46 V + 6,2 mΩ/bacak (150 °C) | **Türkiye stoklu** (Özdisan 7.496 adet) |
| **D1** | 4 | STMicroelectronics `STPS30L45CT` | 45 V; 2 × 15 A; ≈ 0,40–0,45 V | 45 V; gerilim payı dar |

**Yardımcı güç katı elemanları için doğrulanmış adaylar ([OPTIMIZASYON.md](OPTIMIZASYON.md) §9.2, §9.3, §9.5 hedeflerine göre):**

| Eleman | Hedef kriter | Doğrulanmış adaylar (DATASHEET + 12.11.2026 stok) |
|---|---|---|
| **Giriş seramik dekuplajı (MLCC)** | Hücreye yakın, 26 V DC bias'ta **toplam etkin ≥ 4,7 µF** (28 V tepede ve −%10 toleransta da güvenli), ≥ 50 V X7R/X7S | **(1) TR stoklu:** **3 × Samsung `CL31B475KBHNNNE`** (`1206`, `4,7 µF`, `50 V`, `X7R`; Samsung Component Library verisinde 26 V'ta −%54,37 → `2,145 µF/adet`, **3 adet = 6,43 µF** @26 V / `5,37 µF` @28 V min tol.; **Özdisan 1.164.610 stok**, 0,112 $/adet). **(2) 100 V tam paylı:** **2 × Murata `GRM32EC72A106KE05L`** (`1210`, `10 µF`, `100 V`, `X7S`; SimSurfing 26 V'ta −%49,07 → **2 adet = 10,19 µF**; **TME 24.032 stok**, 1,12 $) veya **2 × TDK `C3225X7S2A475K200AB`** (`1210`, `4,7 µF`, `100 V`, `X7S`; 26 V'ta −%38,2 → **2 adet = 5,81 µF**; Farnell 5.763 / TME 1.736 stok). **(3) 50 V 1210:** **2 × Samsung `CL32B106KBJNNNE`** (`10 µF`, `50 V`, `X7R`; 26 V'ta −%59,44 → **2 adet = 8,11 µF**; Digi-Key 855.576 / TME 239.718 stok). |
| **Ortak soğutucu (S1 + D1)** | Doğal taşınımda **Rth(s-a) ≤ 12 K/W** (hedef ≤ 8 K/W), dikey PCB lehim pinli, yan yana 2 × TO-220 sığacak genişlik (≥ 25–30 mm) | **(1) Aavid/Boyd `6380BG`** (**6,8 K/W**, `41,9×28,7×25,4 mm`, 2 lehim pini, *"dual TO-220"* uyumlu düz sırt — yan yana 2×M3 delinir; **Mouser 1.464 stok**, 2,01 $) veya **`6396B-P2G`** (**5,6 K/W**, **Mouser 3.106 stok**, 2,64 $). **(2) Hazır 2×M3 dişli:** **Fischer `SK 459 50 2 x TO 220 STIS`** (**5,6 K/W**, `50×20×50 mm`, fabrikasyon 2×M3 delikli + 2 lehim pini; Digi-Key 1.000 stok, ~10 gün sevk). |
| **TO-220 yalıtım + burç** | Gerçek TO-220 alanında (`≈ 1,0–1,2 cm²`) **Rth(c-s) ≤ 1,0 K/W**, elektriksel yalıtkan + M3 yüksük | **(1) Fischer `AOS 220`** ($\text{Al}_2\text{O}_3$ seramik TO-220 pul, `1,5 mm`, `25 W/m·K`, `15 kV`; ince termal macunla **0,20–0,80 K/W**; **TME 3.538 stok**, 1,00 $ + Özdisan `ALPA AL-701` macun 81 stok) + **Fischer `IB 6`** (M3 poliamid burç, `250 °C`, `30 kV/mm`, `Ø3,1/3,5 mm`; **TME 116.356 stok**, 0,03 $). **(2) Macunsuz:** **Bergquist `HI-FLOW THF 1600P` / `HF300P-0.001`** (TO-220 fikstüründe doğrudan **0,92 K/W @50 psi**, 5 kV) veya **Fischer `KAP 220 G`** (`0,077 mm` faz değişimli Kapton, **TME 1.963 stok**, 0,60 $). |
| **D1 RC sönümleyici (snubber)** | PCB'de yer ayrılacak: `4,7 Ω + 1 nF` veya `2,2 Ω + 2,2 nF` (`≥ 0,25–0,5 W` film direnç + **100 V C0G/NP0** MLCC) | **(1) `4,7 Ω + 1 nF`:** **Panasonic `ERJ8BQF4R7V`** (`4,7 Ω ±1%`, `0,5 W` 1206 anti-surge; **TME 1.258 stok**, 0,31 $) + **Murata `GRM2165C2A102JA01D`** (`1 nF ±5%`, `100 V C0G` 0805; **TME 3.922 stok**, 0,09 $). **(2) `2,2 Ω + 2,2 nF`:** **Vishay `CRCW12102R20JNEA`** (`2,2 Ω`, `0,5 W` 1210; **Mouser 9.645 stok**, 0,50 $) + **Murata `GRM3195C2A222JA01D`** (`1206`, Digi-Key 2.764 stok) veya `GRM2165C2A222JA01D` (`0805`, **TME 3.669 stok**). *(X7R yüksek `dv/dt`'de kapasite kayması ve dielektrik ısınma yaptığı için snubber'da C0G/NP0 kullanılır.)* |

**Yeni kondansatör aday kombinasyonlarının geçici LTspice köşe testi (SİM + HESAP, 12.11.2026; depo değiştirilmeden koşuldu):**
Koşullar: `L1 = 33 µH` (`−%30 / +%20`), `Cout = 1000 µF −%20`, `Cd = 470 µF −%20`, `Rd = 0,22 Ω`, en az sönüm yarıiletken/bobin köşesi (`DCR 6,5 mΩ`, `Ron 4,7 mΩ`, `D1 0,39 V + 4 mΩ`), 200 ms sabit güç darbesi:

| Aday seti (`Cout` + `Cd` + `Rd` + `Cin`) | HESAP `Pkritik` (en sert köşe) | ΔVo anma / 26 V köşe | 200 ms `57,6→73 W` köşe | 200 ms `41,25→82,5 W` köşe | −10 °C Zmax (3p yük atma / köşe ripple) | Karar |
|---|---|---|---|---|---|---|
| **Set 1 (TR+TME):** Samwha `LQ` 25 mΩ + Koshin `KLH` 70 mΩ + Yageo 0,22 Ω + 2×Pana `FR` 16 mΩ | 127,9 W (`ESRo 10 mΩ`) | 42,7 / 63,7 mV | 10,72–11,25 V, sönmüş | 10,26–11,66 V, sönmüş | doğrulanamadı | **GEÇTİ** |
| **Set 2 (TR+TME):** Panasonic `FS` 18 mΩ + Koshin `KLH` 70 mΩ + Yageo 0,22 Ω + 2×Pana `FR` 16 mΩ | 124,5 W (`ESRo 8 mΩ`) | 31,5 / 47,1 mV | 10,72–11,25 V, sönmüş | 10,26–11,66 V, sönmüş | **11,56 V / 130,3 mV** | **GEÇTİ** |
| **Set 3 (TME):** Panasonic `FC` 30 mΩ + Pana `FR` 28 mΩ + 0,22 Ω + 2×Pana `FR` 16 mΩ | 131,2 W (`ESRo 12 mΩ`) | 49,5 / 73,9 mV | 10,72–11,25 V, sönmüş | 10,26–11,66 V, sönmüş | **11,57 V / 135,9 mV** | **GEÇTİ** |
| **Set 4:** Nichicon `UHE` 27 mΩ + `UHE` 46 mΩ + 0,22 Ω + 2×Nichicon `UHW` 20 mΩ | 129,6 W (`ESRo 11 mΩ`) | 45,4 / 67,8 mV | 10,72–11,25 V, sönmüş | 10,26–11,66 V, sönmüş | 11,74 V / 195,0 mV | **GEÇTİ** *(20 °C)* |
| **Set 5:** Pana `FR` / KEMET `ESY` 18 mΩ + Pana `FR` 28 mΩ + 0,22 Ω + 2×KEMET `ESY` 21 mΩ | 124,5 W (`ESRo 8 mΩ`) | 31,2 / 46,7 mV | 10,72–11,25 V, sönmüş | 10,26–11,66 V, sönmüş | **11,49 V / 107,1 mV** | **GEÇTİ** |

- **Önemli bulgu:** `Cd + Rd` sönüm dalı sayesinde `18 mΩ` sınıfı `Cout` adayları da sıcak `ESR = 8 mΩ` köşesinde ≥ 124,5 W kritik güçle sönümlüdür; üstelik **Panasonic `EEUFS1V102L` (Özdisan stoklu), `EEUFC1V102` ve `EEUFR1V102`** ile −10 °C `|Z|max` değerinin tamamı ESR sayılsa bile 26 V köşe ripple'ı **107–136 mV ≤ 165 mV** içinde kalır (eski 25 V `UHE` referansındaki 318 mV soğuk aşımı kapanır).
- **İncelenip kriter dışı kalan (uymuyor) yakın parçalar:** Chemi-Con `EKZH250ELL102MJ25S` (`Cout` 25 V < 35 V) ve `Cin` için 35 V `ESY108M035AL4AA` (35 V < 50 V) yeni gerilim sınıfı kararıyla elendi; Samwha `WL1V108M` (`38 mΩ > 35 mΩ`) ve `WL1H108M` (`43 mΩ > 40 mΩ`, `1,6 A < 2,25 A`), Koshin `PKLH-035V102MH200` (`40 mΩ > 35 mΩ`), TDK `B41858C6477M000` (`Cd` `104 mΩ > 100 mΩ`), YAGEO `KNP` tel sarım `0,22 Ω` dirençler, Vishay `WSL2010R2200FEA` (`0,47 W < 0,50 W`), Samsung `CL31B106KBHNNNE` (`1206 10 µF 50 V`: 26 V'ta −%81 düşümle `1,895 µF/adet`), Fischer `SK 129/104` ve Ohmite `FA-T220` soğutucular (`16–17 mm` oluğa yan yana 2×TO-220 sığmaz), Aavid `578622B03200G` (`13,2 K/W > 12 K/W`), Bergquist `Sil-Pad 400 / 900S / K-10 / 2000` (gerçek TO-220 alanında `2,01–5,14 K/W > 1 K/W`) ve KLS `L-KLS8-0222-PTO-220A` burç (`Ø2,0 mm` delik, M3 vida geçmez) elenmiştir.
- 2. ve sonraki sıradaki adaylar ana şematiğe yazılıp tam test (`dogrula.py secilen`) koşulmamıştır; kullanıcı 1. sırayı belirlediğinde üç dosyaya yazılıp tam koşu yapılır.

Kaynaklar: [74435583300](https://www.we-online.com/en/components/products/datasheet/74435583300.pdf) · [UHE serisi](https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uhe.pdf) · [UHW serisi](https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uhw.pdf) · [Panasonic FS-A](https://cdn.ozdisan.com/public/product/assets/ABA0000C1255_fs_series.pdf) · [Panasonic FR-A](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1259.pdf) · [Panasonic FM-A](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1018.pdf) · [Panasonic FC-A](https://cdn.ozdisan.com/public/product/assets/FC_A_SERI_PANASONIC.pdf) · [Samwha LQ](https://cdn.ozdisan.com/public/product/assets/LQ%20SER%C4%B0ES.pdf) · [Koshin KLH 50V 470µF](https://cdn.ozdisan.com/public/product/assets/KLH-050V471MG200.pdf) · [B41859](https://www.tdk-electronics.tdk.com/inf/20/30/db/aec/B41859.pdf) · [YAGEO MFR](https://yageogroup.com/content/datasheet/asset/file/YAGEO-MFR_DATASHEET) · [Bourns CRM](https://www.bourns.com/docs/product-datasheets/crm.pdf) · [Vishay WSL](https://www.vishay.com/docs/30100/wsl.pdf) · [Samsung CL31B475KBHNNN](https://weblib.samsungsem.com/mlcc/mlcc-ec-data-sheet.do?partNumber=CL31B475KBHNNN) · [Murata GRM32EC72A106KE05](https://ds.murata.com/simsurfing/mlcc.html?oripartnumbers=%5B%22GRM32EC72A106KE05L%22%5D&partnumbers=%5B%22GRM32EC72A106KE05%22%5D) · [Boyd Heatsinks](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5880/BoydBoardLevelHeatsinksCatalog.pdf) · [Fischer Katalog](https://www.tme.eu/Document/f32987f5c8d637e03c14d438f4f9eb03/catalogfischer.pdf) · [STP100N6F7](https://www.st.com/resource/en/datasheet/stp100n6f7.pdf) · [STPS40M60C](https://www.st.com/resource/en/datasheet/stps40m60c.pdf).

## Kriterler

Parantez içindeki "hedef", parça seçilmeden önce şematikte kullanılan değerdir. Ron, Vf ve DCR için hedef, kabul sınırının kendisidir. Daha düşük Ron, Vf veya DCR kaybı azaltır ama sabit güç yüklü LC'nin seri direncini (sönümünü) de düşürür; 47 µH'de payı daraltır (bkz. [OPTIMIZASYON.md](OPTIMIZASYON.md) §4.4), bu yüzden "yalnız kaybı azaltır" denemez.

### L1 — bobin (sarım ve seçim hedef aralığı)

| Kriter | Değer | Neden |
|---|---|---|
| Endüktans (sarım / seçim hedefi) | **33 µH** (el sarım hedefi: **30,7–36,1 µH** [AL 69 nH ±%8, 22 sarım]; satın alınan parçada ±%20 = **26,4–39,6 µH** da doğrulanmıştır). 39 µH ve 47 µH anma değerleri tercih edilmez | 33 µH'de akım ripple'ı %25, CCM sınırı 0,94 A < tipik yük (≈ 1,2 A). 22 µH'de tipik yük DCM'de kalır (çıkış 8,8 V). `Cd = 470 µF + Rd = 0,22 Ω` sönüm dalıyla L +%20 (39,6 µH) köşesinde 200 ms ve 500 ms sabit güç darbeleri **10,72–11,25 V** içinde ve sönmüş olarak geçer ([OPTIMIZASYON.md](OPTIMIZASYON.md) §4.4, §6). |
| Doyma akımı (Isat) | ≥ 12 A; 8,9 A'de L/L0 ≥ %90 (el sarımda %97) | Tepe akım en kötü köşede 8,91 A; %30 pay. Köşe testleri toleransla birlikte toplam −%30'a (23,1 µH) kadar koşuldu. |
| Isıl akım (Irms) | ≥ 9 A | 7,5 A sürekli; %20 pay. |
| DCR (sarım / seçim hedefi) | **6,5–15 mΩ** @ 20 °C (**el sarım hedefi: 7,5–10 mΩ** @ 20 °C, sıcak 75–100 °C'ta 9,5–10,5 mΩ; satın alınan parça ≤ 15 mΩ) | Her +5 mΩ ≈ +0,28 W bakır kaybı ekler (7,81 mΩ'da 0,44 W). `Cd + Rd` sönüm dalı varken DCR 6,5 mΩ alt sınırında ve sıcak ESR 10 mΩ köşesinde bile `Pkritik = 126–134 W > 82,5 W`'tır ([OPTIMIZASYON.md](OPTIMIZASYON.md) §6.2, §10). |
| Yapı | Toroid toz çekirdek (el sarım, Kool Mµ 40µ) veya ekranlı güç bobini, 100 kHz'e uygun | Çekirdek kaybı ≤ 0,14 W (HESAP); sarıldıktan sonra L0, L(I), DCR ve sıcaklık ölçülür. |

Tek parça bulunamazsa eşdeğer kurulumlar (elektriksel olarak aynı):
- **İki eş bobin paralel:** her biri 68 µH, Isat ≥ 6 A, Irms ≥ 4,5 A, DCR 13–30 mΩ → toplam 34 µH.
- **İki eş bobin seri:** her biri 15–18 µH, Isat ≥ 12 A, Irms ≥ 9 A, DCR 3,5–7,5 mΩ → toplam 30–36 µH.

### Cout — ana çıkış kondansatörü (seçim hedef aralığı)

| Kriter | Değer | Neden |
|---|---|---|
| Kapasite | **1000 µF** ±%20 (800–1200 µF) | Yük adımı genliği ve 100 kHz filtreleme. Yaygın standart değer. |
| ESR / empedans (100 kHz, 20 °C) | **≤ 35 mΩ** (hedef 15–35 mΩ; sönüm dalı varken 10–35 mΩ aralığının tamamı kararlıdır) | Üst sınır ripple içindir: 35 mΩ'da 24,6 V anmada 55,7 mV t-t, 26 V `L −%30 / C −%20` köşesinde **83,1 mV t-t** (≤ 165 mV sınırı). Eskiden 15 mΩ altında sönüm yetmiyordu; paralel `Cd + Rd` sönüm dalı eklendiğinden **10 mΩ sıcak ESR köşesi bile 135 W Pkritik ile geçer** ([OPTIMIZASYON.md](OPTIMIZASYON.md) §6.2, §10). Yine de çok düşük ESR'li polimer yerine 15–35 mΩ düşük empedanslı elektrolitik ek sönüm payı verir. −10 °C'ta Zmax ≤ 120 mΩ tercih edilir. |
| Gerilim | **≥ 35 V** (kullanıcı kararı, 12.11.2026) | S1 kısa devre arızasında çıkış kararlı 24–26 V'a, LC geçişinde **27,3–31,1 V**'a çıkar; yüksüz açık çevrimde de giriş gerilimine tırmanır ([OPTIMIZASYON.md](OPTIMIZASYON.md) §9.4). 25 V anma aşılır; 35 V sınıfı bu arızayı kondansatör düzeyinde kapsar. |
| Ripple akımı | ≥ 1,0 A RMS (100 kHz, 105 °C) | Devrede 0,48 A RMS (sönüm dalı akımın %14'ünü paylaşır). |
| Tip | 105 °C, düşük empedanslı alüminyum elektrolitik, radyal | — |

Eşdeğer: 2 × 470 µF / ≥ 35 V paralel, her biri ESR ≤ 70 mΩ, ripple akımı ≥ 0,5 A.

### Cd ve Rd — çıkışa paralel RC sönüm dalı

| Eleman / Kriter | Değer | Neden |
|---|---|---|
| **Cd** kapasite | **470 µF** ±%20 (376–564 µF) | Sabit güç yükü (CPL) karşısında ≈ 0,9 kHz LC rezonansını sönümler; `Cout`'un yarısı mertebesinde kapasite en sert köşede `Pkritik ≥ 126 W > 82,5 W` sağlar ([OPTIMIZASYON.md](OPTIMIZASYON.md) §6, §10). |
| **Cd** gerilim | **≥ 35 V** (kullanıcı kararı, 12.11.2026) | `Cout` ile aynı düğümdedir (`Rd` üzerinden DC akım geçmez, kararlı hâlde tüm çıkış gerilimi `Cd` üzerindedir); S1 kısa devresinde 27,3–31,1 V görür. |
| **Cd** ESR (100 kHz, 20 °C) | **≤ 100 mΩ** (soğukta ≤ 350 mΩ) | Seri ayrık `Rd = 0,22 Ω` ile toplam direncin 0,15 / 0,22 / 0,35 / 0,60 Ω değerleri seçili model setlerinde sınandı (`dogrula.py kararlilik` §3); aradaki tüm kombinasyonlar kanıtlanmış değildir. Adayın sıcaklık ve frekans davranışı doğrulanmalıdır. |
| **Cd** ripple akımı | ≥ 0,3 A RMS (100 kHz, 105 °C) | Devrede 100 kHz ripple akımı 76 mA RMS'tir; yük adımlarında geçici sönüm akımı taşır. |
| **Rd** direnç | **0,22 Ω** ±%5 (veya ±%1); toplam `Rd + ESR(Cd)` hedefi **0,15–0,60 Ω** | `Z0 = √(L/Cout) ≈ 0,18 Ω` karakteristik empedansa uyumlu sönüm direnci; `Cd`'nin kendi ESR belirsizliğini bastırır, 100 kHz ripple'ı bozmaz. |
| **Rd** güç ve yapı | **≥ 0,25 W** (tercihen **0,5 W**, ör. 1206/1210/2010 SMD veya THT film direnç, düşük endüktanslı / tel sarım olmayan) | Kararlı hâlde DC akım sıfırdır, 100 kHz ripple kaybı yalnız **1,3 mW**'tır. Sert kalkış veya S1 kısa devresi darbesinde anlık enerji `½·Cd·ΔV² ≈ 0,06–0,22 J` (birkaç ms) harcar; 0,25–0,5 W darbe dayanımlı film direnç yeterlidir. |

### Cin — giriş kondansatörleri (seçim hedef aralığı)

| Kriter | Değer | Neden |
|---|---|---|
| Toplam ripple akımı anma değeri | **≥ 4,5 A RMS** (100 kHz, 105 °C), paralel adetlerin toplamı | Devrede 3,77 A RMS; %20 pay. Boyutu belirleyen budur, kapasite değil. |
| Gerilim | **≥ 50 V** (kullanıcı kararı, 12.11.2026) | 26 V bataryanın düşük dirençli / uzun kablolu kaynakla sıcak takılmasında tepe gerilim 35 V'u aşıp **45,3–46,5 V**'a çıkabilir (HESAP + SİM, [OPTIMIZASYON.md](OPTIMIZASYON.md) §9.4). 50 V sınıfı bu riski kondansatör düzeyinde kapatır (ör. listedeki 3. sıra aday KEMET ESY108M050AM2AA 50 V / 21 mΩ / 3,35 A). |
| Toplam kapasite | ≥ 440 µF (hedef 2 × 1000 µF) | 440 µF'ta giriş ripple'ı ≈ 125 mV t-t. 2 × 1000 µF / 50 V (veya 3 × 470–680 µF / 50 V) ripple akımı şartını sağlayan standart kurulumdur. |
| ESR (100 kHz) | ≤ 40 mΩ/adet (hedef 15–25 mΩ/adet) | Giriş ripple'ının büyük kısmı ESR'dendir. Hücreye yakın ayrıca etkin ≥ 4,7 µF / ≥ 50 V X7R seramik dekuplaj konacaktır ([OPTIMIZASYON.md](OPTIMIZASYON.md) §9.3, §9.5). |
| Tip | 105 °C, düşük empedanslı alüminyum elektrolitik | — |

### S1 — anahtar (N-kanal MOSFET)

| Kriter | Değer | Neden |
|---|---|---|
| VDS | ≥ 55 V (tercihen 60–100 V) | 26 V giriş, takma anında 28 V; zil payı. |
| RDS(on) @ VGS 10 V, 25 °C | **≤ 12 mΩ** (hedef 12 mΩ) | İletim kaybı 0,32 W. 18 mΩ'a kadar kabul edilebilir (+0,16 W). |
| ID (sürekli) | ≥ 30 A | 5,7 A RMS, 8,9 A tepe; ısıl pay. |
| Toplam kapı yükü Qg | ≤ 160 nC (tercihen ≤ 80 nC) | Sonraki aşamada sürücü akımını ve anahtarlama kaybını belirler. |
| Kılıf | TO-220 (soğutucuya bağlanabilir, delikli) | El montajı ve soğutma. |

### D1 — serbest geçiş diyodu (Schottky)

| Kriter | Değer | Neden |
|---|---|---|
| VRRM | ≥ 45 V (tercihen 60 V) | Ters gerilim 26–28 V. 45 V'ta pay 1,6×; zil ölçülmeden 60 V tercih edilir. |
| IF(AV) | ≥ 15 A toplam (çift diyotta iki bacak paralel) | Ortalama 4,2 A (26 V); düşük akım yoğunluğu Vf'yi düşürür. |
| VF @ 7,5 A toplam, 25 °C | **≤ 0,58 V** (hedef 0,5 V + 10 mΩ) | İletim kaybının üçte ikisi (2,3 W) diyottadır. Her 0,1 V ≈ 0,4 W. |
| Kılıf | TO-220 veya TO-247 | ≈ 2,3 W; soğutucu ister. |

### Rload — test yükü

1,47 Ω, ≥ 100 W direnç bankası veya elektronik yük (82,5 W sürekli). Gerçek O1 / S2E **bağlanmaz**.

## Türkiye'de bulunurluk (11–12 Kasım 2026 taraması)

Bu bölüm bilgi amaçlıdır; parça seçimi değildir. Stoklar o günkü sayfa görüntüleridir.

- **Cout (≥ 35 V, ≤ 35 mΩ, ≥ 1 A RMS) kriterini tutanlar (12.11.2026):** Panasonic `EEUFS1V102L` (35 V, `|Z|max = 18 mΩ` @20 °C / `54 mΩ` @−10 °C, 2,47 A; Özdisan 1.970 stok, 43,73 TL + KDV) ve Samwha `LQ1V108M12020PL` (35 V, `|Z|max = 25 mΩ` @20 °C, 2,80 A; Özdisan 1.000 stok, 17,28 TL + KDV). Özdisan'daki Samwha `WL1V108M` (`38 mΩ`) ve Koshin `PKLH-035V102MH200` (`40 mΩ`) üst sınırı aştığı için elendi.
- **Cd (470 µF, ≥ 35 V, ≤ 100 mΩ) ve Rd (0,22 Ω) kriterini tutanlar (12.11.2026):** Koshin `PKLH-050V471MG200` (50 V, `|Z|max = 70 mΩ`, 1,27 A; Özdisan 2.249 stok, 6,07 TL + KDV), Koshin `PKLH-063V471MH200-T/A5.0` (63 V, `|Z|max = 80 mΩ`, 1,525 A; Özdisan 5.265 stok) ve YAGEO `MFR200FTF73-0R22` (0,22 Ω ±%1, 2 W THT metal film; Özdisan 4.891 stok, 0,085 $ + KDV).
- **Cin (≥ 50 V, ≤ 40 mΩ/adet, ≥ 4,5 A toplam ripple) (12.11.2026):** Türkiye yerel satıcılarında kriterlerin tamamını aynı anda sağlayan stoklu parça **bulunamadı** (Özdisan'da Panasonic `EEUFR1H102B` ve `EEUFM1H102B` stok 0; Samwha `WL1H108M` hem `43 mΩ` hem `1,6 A/adet` ile eleniyor). Yurt dışı dağıtıcılarda (TME, Mouser, Digi-Key) Panasonic `EEU-FR1H102`, `EEU-FM1H102` ve Nichicon `UHW1H102MHD` yüksek stokludur.
- **Giriş seramik dekuplajı ve soğutucu (12.11.2026):** Özdisan'da Samsung `CL31B475KBHNNNE` (`1206`, `4,7 µF`, `50 V`, `X7R`) 1.164.610 adet stokludur (26 V'ta 3 adet paralel = 6,43 µF etkin). Özdisan'daki stoklu fason soğutucularda üretici `Rth` veri sayfası **doğrulanamadı**; `Rth ≤ 8 K/W` belgeli çift TO-220 soğutucular (Aavid `6380BG` / `6396B-P2G`, Fischer `SK 459`) ve TO-220 seramik pul + burç (`Fischer AOS 220` + `IB 6`) Mouser / TME / Digi-Key stoklarından listelendi.
- **S1 kriterini tutanlar (11.11.2026):** STP75NF75 (75 V, 11 mΩ; Özdisan 5.340 stok, 52,69 TL + KDV), IRF1010EPBF (60 V, 12 mΩ; Özdisan 685 stok). IRFZ44N (55 V, 17,5 mΩ; Özdisan 6.658 stok) yalnız "kabul edilebilir" sınırdadır.
- **D1 kriterini tutan (11.11.2026):** IXYS DSB60C60HB (60 V, 2 × 30 A, bacak başına 0,46 V + 6,2 mΩ @150 °C; Özdisan 7.496 stok, 117,88 TL + KDV).
- **L1 (11.11.2026):** Türkiye perakendesinde 10 A üstü güç bobinleri yalnız küçük değerlerde görüldü (ör. 4,7 µH / 12–15 A, 12 × 12 mm); 33 µH'de en yüksek 5 A (Direnc.net), 8 A / 58 mΩ (Özdisan). Kriteri tutan stoklu parça **bulunamadı**. Katalogda kriteri tutan örnek: Bourns 2300HT-330 (33 µH, 13,6 A, 15 mΩ; 13,6 A'de 23 µH) ve 2300HT-390 (39 µH, 13 A, 17 mΩ). Paralel/seri kurulum bu yüzden kriterlere eklendi.

## Araştırma istemi (başka bir araçla parça aramak için)

```
Aşağıdaki kriterleri sağlayan elektronik parçaları, Türkiye'den hızlı ve çok sayıda temin edilebilecek şekilde bul. Öncelik sırası: (1) Türkiye'de stoklu satıcılar (Özdisan, Direnc.net, Empa, Robotistan, Görsu Elektronik), (2) Türkiye'ye gönderen dağıtıcılar (Digi-Key, Mouser, Farnell, TME, LCSC).

Kurallar:
- Her öneri için üretici veri sayfasından kriter değerlerini tek tek yaz ve veri sayfası bağlantısını ver. Veri sayfasında bulamadığın değeri "doğrulanamadı" diye işaretle; tahmin etme.
- Her öneri için satıcı, BUGÜNKÜ stok adedi, birim fiyat, teslim süresi ve ürün sayfası bağlantısını ver. Stok göremediysen "stok doğrulanamadı" yaz.
- Kriterin tamamını sağlamayan parçayı önerme; hangi kriterde kaldığını belirterek "uymuyor" listesine yaz.
- Her kalem için en az 3 aday ver; en az 50 adet stoklu olanı öne al. Mümkünse delikli (THT) kılıf.

1) Güç bobini (buck çıkış bobini, 100 kHz) — satın alma alternatifi (1. sıra el sarım Kool Mµ 40µ 0077536A7, 22 sarım)
   - Endüktans 33 µH, tolerans ≤ ±%20
   - Doyma akımı Isat ≥ 12 A ve 9 A'de endüktans düşümü ≤ %10 (veri sayfasındaki L–I eğrisinden veya iki noktadan yaz)
   - Isıl akım Irms ≥ 9 A
   - DCR 6,5–15 mΩ (20 mΩ'a kadar olanları ayrı listele)
   - Ekranlı veya toroid

2) Ana çıkış kondansatörü (Cout)
   - 1000 µF ±%20, ≥ 35 V, 105 °C, radyal alüminyum elektrolitik
   - 100 kHz ESR (veya empedans) ≤ 35 mΩ (tercihen 15–35 mΩ)
   - 100 kHz ripple akımı ≥ 1 A RMS

3) Çıkış sönüm dalı (Cd + seri Rd)
   - Cd: 470 µF ±%20, ≥ 35 V, 105 °C, radyal alüminyum elektrolitik, 100 kHz ESR ≤ 100 mΩ, ripple akımı ≥ 0,3 A RMS
   - Rd: 0,22 Ω ±%5 (veya ±%1), ≥ 0,5 W, endüktanssız film direnç (THT veya 1210/2010 SMD)

4) Giriş kondansatörü (Cin — 2 veya 3 adet paralel kullanılacak)
   - ≥ 50 V, 105 °C, radyal alüminyum elektrolitik, toplam kapasite ≥ 1000 µF (ör. 2 × 1000 µF veya 3 × 680 µF)
   - 100 kHz toplam ripple akımı ≥ 4,5 A RMS (2 adette ≥ 2,25 A/adet; 3 adette ≥ 1,5 A/adet)
   - 100 kHz ESR ≤ 40 mΩ/adet

5) N-kanal güç MOSFET'i (S1)
   - VDS ≥ 55 V (60 V tercih), RDS(on) ≤ 12 mΩ (VGS = 10 V, 25 °C, maksimum değer), ID ≥ 30 A
   - Toplam kapı yükü Qg ≤ 160 nC (değeri yaz; düşük olan tercih)
   - TO-220

6) Schottky diyot (D1)
   - VRRM ≥ 45 V (60 V tercih), IF(AV) ≥ 15 A toplam
   - İleri gerilim VF ≤ 0,58 V, 7,5 A toplam akımda, 25 °C (çift diyotta bacak başına 3,75 A; veri sayfası eğrisinden oku)
   - TO-220 veya TO-247

Sonucu her kalem için tablo olarak ver: parça numarası, üretici, kriter değerleri (veri sayfasından), satıcı, stok, fiyat, teslim süresi, bağlantılar.
```

## Parça değiştiğinde

1. Veri sayfası değerini `buck/ltspice/sematik_uret.py`, `buck/hesap.py` ve `buck/dogrula.py` (`SECILEN`) içine yaz.
2. `python buck/ltspice/sematik_uret.py`, `python buck/hesap.py`, `python buck/dogrula.py secilen`, `pencere` ve `kararlilik` koş.
3. Sonuçlar 9–12 V ve ripple ≤ 165 mV içinde kalıyorsa ve 200 ms'lik sabit güç darbesinde salınım sönüyorsa parça uygundur; bu dosyadaki "Aday parçalar" tabloları, [OPTIMIZASYON.md](OPTIMIZASYON.md) §5, README ve yol haritası yenilenir.

## Sonraki aşamalar için notlar

Ölçülebilir arayüz şartlarının tam listesi: [OPTIMIZASYON.md](OPTIMIZASYON.md) §11.

- **Kapı sürücüsü:** S1 üst taraftaki N-MOSFET'tir; kapısı anahtar düğümünün ≈ 10 V üstüne sürülmelidir (bootstrap'lı üst taraf sürücüsü). STP100N6F7'nin kapı yükü 30 nC (tipik): 100 kHz ve 10 V'ta sürücü gücü ≈ 30 mW. Yüksüz / DCM'de bootstrap kondansatörünün yenilenmesi ayrıca ele alınmalıdır (anahtar düğümü toprağa inmeyebilir).
- **Kontrol:** Ton aralığı 2,1–5,6 µs (yük 0,24–7,5 A, giriş 20–26 V); DCM/CCM geçişi ≈ 0,94 A; ana LC f0 ≈ 0,88 kHz, Cd–Rd köşesi ≈ 1,54 kHz, ESR sıfırı ≥ 4,5 kHz. Yumuşak kalkış zorunlu (sert kalkış 61,5 A / 16,6 V; el sarım L1 bu akımda ≈ %53'e düşer, gerçek tepe daha yüksek olur). Çıkıştaki `Cd = 470 µF + Rd = 0,22 Ω` sönüm dalı bütün tolerans ve sıcaklık köşelerinde 82,5 W sabit güç yükünü doğal olarak sönümler; kapalı çevrim kompanzasyon tasarımında bu 3. derece filtre hesaba katılmalıdır.
- **Isı:** D1 1,4–1,9 W iletim + sıcakta ters kaçak (125 °C'ta ≈ 1 W'a kadar, azami); **soğutucusuz ısıl kaçağa gider**, soğutucu zorunlu. S1 ≈ 0,15–0,2 W iletim + 0,4–1,4 W anahtarlama (kestirim). L1 ≈ 0,6–0,7 W.
- **Akım ölçümü:** Bu aşamada yok; koruma/kontrol için sonraki aşamada eklenir.
- **Montaj:** Anahtarlama çevrimi (Cin → S1 → D1 → Cin) kısa tutulmalıdır; elektrolitiklerin ESL'i (≈ 26 nH/adet) yüzünden hücreye yakın seramik kondansatör gerekir.
