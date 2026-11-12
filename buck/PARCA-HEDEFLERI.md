# Parça Kriterleri ve Aday Parçalar — Ana Güç Devresi

**Tarih:** 12 Kasım 2026
**Durum:** Parçalar **kesinleşmedi**. Aşağıdaki liste "olabilir" listesidir: kriterlerle yapılan dış araştırmanın adayları, LTspice köşe testindeki paya göre sıralanmıştır. Şematik, listenin başındaki **1. sıra adayların** değerlerini taşır (L1 için el sarım hesabı, diğerleri veri sayfası); bu bir satın alma kararı değildir. Kriterleri sağlayan başka bir parça aynı yolla (bkz. "Parça değiştiğinde") 1. sıraya geçebilir.
**Sınıf:** analitik hesap (`hesap.py`) + LTspice, ideal elemanlar (`dogrula.py`). Fiziksel ölçüm yok.
**Dondurma durumu:** **FROZEN (simülasyon dondurması, 12 Kasım 2026)** — çıkış sönüm dalı (`Cd = 470 µF + seri Rd = 0,22 Ω`) eklendi, tüm köşe testleri geçti; gerilim sınıfları **Cout ve Cd ≥ 35 V**, **Cin ≥ 50 V** olarak kararlaştırıldı ve simülasyon dondurması kullanıcı onayıyla tamamlandı. Parçalar ve bobin, bu belgedeki dondurulmuş hedef aralıklara göre seçilir / sarılır. Ayrıntı [OPTIMIZASYON.md](OPTIMIZASYON.md) §12.

Çalışma noktası: Vin 20 / 22,2 / **24,6** / 25,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz. Seçim süreci ve test sonuçları: [OPTIMIZASYON.md](OPTIMIZASYON.md).

## Aday parçalar (kesin seçim değil)

### 1. sıra — şematikte kullanılan değerler

| Eleman | Parça | Veri sayfası değeri | Şematikte | Stok ve fiyat (11.11.2026) |
|---|---|---|---|---|
| **L1** (1. sıra, el sarım) | Magnetics **Kool Mµ 40µ `0077536A7`** toroid, 22 sarım, 100 × 0,20 mm litz | 33,4 µH (AL 69 nH ±%8 → 30,7–36,1 µH); Ae 174 mm², le 126 mm, Ve 22 cm³; DC bias %80 @ 58,5 Oe, %50 @ 133 Oe; çekirdek kaybı en çok 900 mW/cm³ @ 100 kHz / 100 mT (DATASHEET, 0077536A7 rev. 6/1/2022). L(8,9 A) ≈ %97, L(12 A) ≈ %95, L(53 A) ≈ %59 (bias eğrisinden okuma); DCR 7,81 mΩ @20 °C (HESAP), 9,5 mΩ @75 °C; kayıp 0,58 W @20 °C / 0,72 W @100 °C sargı (bakır 0,44–0,58 W + çekirdek ≤ 0,14 W, HESAP) — **fiziksel ölçüm yok** | 33 µH, `Rser=7.81m` | Çekirdek ve tel ayrı temin; ölçüm gerekir |
| **L1** (2. sıra, satın alma) | Würth **74435583300** (WE-HCI, yüzey montaj, ekranlı) | 33 µH ±%20 (100 kHz, 10 mA); 30,5 µH tipik @ 11,5 A; Irms 11,5 A (ΔT 50 K); 10,6 A (ΔT 40 K); Isat 12,5 A (−%10) ve 15 A (−%30), **ikisi de tipik**; DCR 13,2 mΩ ±%10 @ 20 °C (maks 14,52 mΩ; sıcakta artar). 9 A'de düşüm ≈ %3 (L–I eğrisinden yaklaşık okuma, ikinci el rapor); çekirdek kaybı verisi datasheet'te yok | şematikte değil (el sarım 1. sırada) | Digi-Key 260 adet, 7,34 $ |
| **Cout** | Nichicon **UHE1E102MHD6TO** *(elektriksel R/C referansı; **25 V < yeni ≥35 V kriteri**)* | 1000 µF ±%20; 25 V; 105 °C; **empedans** en çok 35 mΩ (100 kHz, 20 °C) ve 120 mΩ (100 kHz, −10 °C) — ESR değildir; ripple akımı 1,90 A (105 °C, 100 kHz). **Not:** 12.11.2026 kararıyla Cout kriteri ≥ 35 V olduğundan kesin parça ≥ 35 V seçilecektir | 1000 µF, `Rser=35m` | Mouser 336 adet, 1,22 € |
| **Cd + Rd** (çıkış sönüm dalı) | Henüz aday seçilmedi (§12.2'de seçilecek) | Hedef aralık: **Cd = 470 µF ±%20, ≥ 35 V**, 105 °C elektrolitik; **Rd = 0,22 Ω** ayrık direnç (Cd ESR'si dahil toplam dal direnci **0,15–0,60 Ω**), ≥ 0,25 W (anlık darbe dayanımlı) | `Cd=470u`, `Rd=0.22` | Standart E12 değerler |
| **Cin1, Cin2** | 2 × TDK **B41859D7108M000** *(elektriksel R/C referansı; **35 V < yeni ≥50 V kriteri**)* | 1000 µF ±%20; 35 V; 105 °C; 16 × 20 mm; empedans (Zmax) 15 mΩ (100 kHz, 20 °C), 38 mΩ (−10 °C) — ESR değildir, ESL ≈ 26 nH ≈ 16 mΩ reaktans aynı büyüklükte; ripple akımı 3,25 A/adet (105 °C, 100 kHz) → 6,5 A. **Not:** 12.11.2026 kararıyla Cin kriteri ≥ 50 V olduğundan kesin parça ≥ 50 V seçilecektir (ör. 3. sıradaki 50 V aday) | 2 × 1000 µF, `Rser=15m` | Farnell Türkiye 2.914 adet, 2,31 € + KDV |
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

### Diğer adaylar (öncelik sırasıyla)

| Eleman | Sıra | Parça | Değerler | Not |
|---|---|---|---|---|
| L1 | 2 | Würth 7443783533330 (delikli) | 33 µH; Isat 39 A; Irms 22 A; DCR 9,9 mΩ maks | Elektriksel olarak 1. sıradan iyi; Digi-Key'de yalnız 18 adet |
| L1 | 3 | Würth 7443783533470 (delikli) | 47 µH; Isat 32 A; DCR 13 mΩ maks | **Yalnız** 35 mΩ'luk Cout ile; 12 V'a pay 0,07 V. Digi-Key 645 adet |
| L1 | 4 | Würth 7443763540470 (delikli) | 47 µH; Isat 31 A; DCR 6,4 mΩ maks | 3. sırayla aynı koşul; Digi-Key 838 adet, 21,43 $ |
| Cout | 2 | Chemi-Con EKZH250ELL102MJ25S | 1000 µF; 25 V; 18 mΩ; 2,25 A | Yalnız 33 µH ile; sönüm payı dar |
| Cout | 3 | KEMET ESY108M035AL4AA | 1000 µF; 35 V; 18 mΩ; 2,77 A | Yalnız 33 µH ile; sönüm payı dar. Digi-Key 3.882 adet |
| Cin | 2 | KEMET ESY108M035AL4AA | 1000 µF; 35 V; 18 mΩ; 2,77 A/adet | İki adet 5,54 A |
| Cin | 3 | KEMET ESY108M050AM2AA | 1000 µF; 50 V; 21 mΩ; 3,35 A/adet | İki adet 6,7 A; daha pahalı |
| S1 | 2 | Infineon IPP034N08N5 | 80 V; 3,4 mΩ; Qg 87 nC maks | Gerilim payı en yüksek |
| S1 | 3 | Infineon IPP030N06NF2S | 60 V; 3,05 mΩ; Qg 102 nC maks | En düşük direnç, en yüksek kapı yükü |
| S1 | 4 | STP75NF75 | 75 V; 11 mΩ; Qg 117 nC | **Türkiye stoklu** (Özdisan 5.340 adet) |
| D1 | 2 | STPS30L60CT | 60 V; 2 × 15 A; ≈ 0,5 V @ 3,75 A/bacak | Digi-Key 856 adet |
| D1 | 3 | IXYS DSB60C60HB (TO-247) | 60 V; 2 × 30 A; 0,46 V + 6,2 mΩ/bacak (150 °C) | **Türkiye stoklu** (Özdisan 7.496 adet) |
| D1 | 4 | STPS30L45CT | 45 V; 2 × 15 A; ≈ 0,40–0,45 V | 45 V; gerilim payı dar |

2. ve sonraki sıradaki adaylar şematiğe yazılıp tam test (`dogrula.py secilen`) koşulmamıştır; yalnız yukarıdaki köşe testinde veya kriter karşılaştırmasında değerlendirilmiştir.

Kaynaklar: [74435583300](https://www.we-online.com/en/components/products/datasheet/74435583300.pdf) · [UHE serisi](https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uhe.pdf) · [B41859](https://www.tdk-electronics.tdk.com/inf/20/30/db/aec/B41859.pdf) · [STP100N6F7](https://www.st.com/resource/en/datasheet/stp100n6f7.pdf) · [STPS40M60C](https://www.st.com/resource/en/datasheet/stps40m60c.pdf).

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
| **Cd** ESR (100 kHz, 20 °C) | **≤ 100 mΩ** (soğukta ≤ 350 mΩ) | Seri ayrık `Rd = 0,22 Ω` direnciyle toplanır; toplam dal direnci **0,15–0,60 Ω** penceresinde kaldığı sürece tüm köşeler sönümlüdür (`dogrula.py kararlilik` §3). Standart düşük empedanslı 105 °C radyal elektrolitik uygundur. |
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

## Türkiye'de bulunurluk (11 Kasım 2026 taraması)

Bu bölüm bilgi amaçlıdır; parça seçimi değildir. Stoklar o günkü sayfa görüntüleridir.

- **S1 kriterini tutanlar:** STP75NF75 (75 V, 11 mΩ; Özdisan 5.340 stok, 52,69 TL + KDV), IRF1010EPBF (60 V, 12 mΩ; Özdisan 685 stok). IRFZ44N (55 V, 17,5 mΩ; Özdisan 6.658 stok) yalnız "kabul edilebilir" sınırdadır.
- **D1 kriterini tutan:** IXYS DSB60C60HB (60 V, 2 × 30 A, bacak başına 0,46 V + 6,2 mΩ @150 °C; Özdisan 7.496 stok, 117,88 TL + KDV).
- **L1:** Türkiye perakendesinde 10 A üstü güç bobinleri yalnız küçük değerlerde görüldü (ör. 4,7 µH / 12–15 A, 12 × 12 mm); 33 µH'de en yüksek 5 A (Direnc.net), 8 A / 58 mΩ (Özdisan). Kriteri tutan stoklu parça **bulunamadı**. Katalogda kriteri tutan örnek: Bourns 2300HT-330 (33 µH, 13,6 A, 15 mΩ; 13,6 A'de 23 µH) ve 2300HT-390 (39 µH, 13 A, 17 mΩ). Paralel/seri kurulum bu yüzden kriterlere eklendi.
- **Cout / Cin:** Özdisan'da Panasonic FR/FM serisi listeli ama stok 0 (22–23 hafta). 1000 µF için ESR ve ripple akımı değerleri bu taramada doğrulanmadı.

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
