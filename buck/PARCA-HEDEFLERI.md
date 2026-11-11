# Parça Kriterleri ve Aday Parçalar — Ana Güç Devresi

**Tarih:** 11 Kasım 2026
**Durum:** Parçalar **kesinleşmedi**. Aşağıdaki liste "olabilir" listesidir: kriterlerle yapılan dış araştırmanın adayları, LTspice köşe testindeki paya göre sıralanmıştır. Şematik, listenin başındaki **1. sıra adayların** veri sayfası değerlerini taşır; bu bir satın alma kararı değildir. Kriterleri sağlayan başka bir parça aynı yolla (bkz. "Parça değiştiğinde") 1. sıraya geçebilir.
**Sınıf:** analitik hesap (`hesap.py`) + LTspice, ideal elemanlar (`dogrula.py`). Fiziksel ölçüm yok.

Çalışma noktası: Vin 20 / 22,2 / **24,6** / 25,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz. Seçim süreci ve test sonuçları: [OPTIMIZASYON.md](OPTIMIZASYON.md).

## Aday parçalar (kesin seçim değil)

### 1. sıra — şematikte kullanılan değerler

| Eleman | Parça | Veri sayfası değeri | Şematikte | Stok ve fiyat (11.11.2026) |
|---|---|---|---|---|
| **L1** | Würth **74435583300** (WE-HCI, yüzey montaj, ekranlı) | 33 µH ±%20; Irms 11,5 A; Isat 12,5 A (−%10, tipik); DCR 13,2 mΩ ±%10 (maks 14,52 mΩ); 9 A'de düşüm ≈ %3–5 | 33 µH, `Rser=14.5m` | Digi-Key 260 adet, 7,34 $ |
| **Cout** | Nichicon **UHE1E102MHD6TO** | 1000 µF ±%20; 25 V; 105 °C; ESR 35 mΩ (100 kHz, maks); ripple akımı 1,90 A | 1000 µF, `Rser=35m` | Mouser 336 adet, 1,22 € |
| **Cin1, Cin2** | 2 × TDK **B41859D7108M000** | 1000 µF ±%20; 35 V; 105 °C; 16 × 20 mm; empedans 15 mΩ (100 kHz, 20 °C), 38 mΩ (−10 °C); ripple akımı 3,25 A/adet → 6,5 A | 2 × 1000 µF, `Rser=15m` | Farnell Türkiye 2.914 adet, 2,31 € + KDV |
| **S1** | STMicroelectronics **STP100N6F7** (TO-220) | 60 V; RDS(on) 5,6 mΩ maks (VGS 10 V, 25 °C); ID 100 A; Qg 30 nC tipik | `Ron=5.6m` | Digi-Key 2.105 adet, 2,08 $ |
| **D1** | STMicroelectronics **STPS40M60CT** (TO-220AB, iki bacak paralel) | 60 V; 2 × 20 A; VF maks 0,46 V @ 5 A/bacak, 25 °C; 3,75 A/bacakta ≈ 0,42–0,45 V | `Vf=0.38 Ron=8m` (7,5 A'de 0,44 V) | Digi-Key 1.010 adet, 2,81 $ |

**Neden bu set 1. sırada (LTspice köşe testi; köşe = bobin +%20, Cout −%20, ESR alt kenarda):**

| Bobin | Çıkış kondansatörü | Ripple anma / köşe | S2E kalkışı, köşe | O1 yük adımı, köşe | Sonuç |
|---|---|---|---|---|---|
| **33 µH (74435583300)** | **Nichicon UHE, 35 mΩ** | 65 / 96 mV | 10,58–11,32 V | 10,01–11,81 V | **Geçti (1. sıra)** |
| 33 µH (74435583300) | 18 mΩ'luk aday (KEMET ESY, Chemi-Con KZH) | 39 / 54 mV | 10,54–11,39 V | 9,98–11,79 V | Geçti; 73 W'ta 0,5 V salınım |
| 47 µH (7443783533470) | Nichicon UHE, 35 mΩ | 46 / 69 mV | 10,57–11,37 V | 9,86–11,93 V | Geçti; 12 V'a 0,07 V pay |
| 47 µH (7443783533470) | 18 mΩ'luk aday | 24 / 33 mV | 9,24–12,83 V | 9,62–12,24 V | **Kaldı**; 2,6–3,6 V salınım |

- **Cout için 35 mΩ'luk parça bilerek öne alındı.** Veri sayfasındaki ESR en yüksek değerdir; gerçek parça bunun altındadır. Bu testte ESR alt kenarı veri sayfası değerinin %60'ı alındı (**varsayım**; üretici alt değer vermez). 35 mΩ'luk parçada gerçek değer kabul penceresinin (15–35 mΩ) ortasına düşer; 18 mΩ'luk parçada pencerenin altına inebilir.
- **S1 için en düşük dirençli değil, en düşük kapı yüklü aday öne alındı.** İletim kaybı 5,6 mΩ'da zaten 0,15 W'tır; 30 nC kapı yükü sonraki aşamada sürücüyü kolaylaştırır ve anahtarlama kaybını düşürür.
- **L1 için 33 µH**, 47 µH'den daha geniş sönüm payı verir. 1. sıradaki parça yüzey montajdır ve doyma akımı (12,5 A) kriterin hemen üstündedir; stoku bol olduğu için öne alındı. Delikli 7443783533330 elektriksel olarak daha iyidir (aşağıda 2. sıra).

**Doğrulama durumu:**
- TDK B41859D7108M000 değerleri üretici veri sayfasından doğrulandı (DATASHEET).
- Diğer dört parçanın değerleri dış araştırma raporundan alındı; veri sayfaları bu depoda çalışan araçla metin olarak okunamadı. Bir aday kesinleştirilmeden önce özellikle Nichicon'un 35 mΩ ve Würth'ün 12,5 A doyma değeri veri sayfasından teyit edilmelidir.
- D1 modeli (0,38 V + 8 mΩ) raporda verilen iki noktadan çıkarıldı; **yaklaşıktır**.

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

Parantez içindeki "hedef", parça seçilmeden önce şematikte kullanılan değerdir. Ron, Vf ve DCR için hedef, kabul sınırının kendisidir: daha iyi parça yalnız kaybı azaltır, başka bir şeyi bozmaz.

### L1 — bobin

| Kriter | Değer | Neden |
|---|---|---|
| Endüktans | **33–47 µH**, tolerans ≤ ±%20 (hedef 33 µH) | 33 µH'de akım ripple'ı %25. 22 µH'de CCM sınırı 1,4 A'e çıkar, tipik yük (≈ 1,2 A) kesintili iletimde kalır ve açık çevrim testinde çıkış 8,8 V'a düşer. 47 µH üstü Cout 1000 µF ile sönümü zayıflatır. Güncel şematik değerleriyle tolerans köşesi testinde 33 µH geçti, 39 µH kaldı (12,06 V), 47 µH 0,04 V payla ve yalnız 20 ms'lik S2E kalkış darbesi varsayımıyla geçti ([OPTIMIZASYON.md](OPTIMIZASYON.md) §4.4). Doğrulanmış değer 33 µH'dir; 39–47 µH için aralık yeniden karar bekliyor. |
| Doyma akımı (Isat) | ≥ 12 A; 9 A'de endüktans düşümü ≤ %10 | Tepe akım en kötü köşede 8,9 A; %30 pay. Köşe testleri toleransla birlikte toplam −%30'a kadar koşuldu. |
| Isıl akım (Irms) | ≥ 9 A | 7,5 A sürekli; %20 pay. |
| DCR | ≤ 15 mΩ (hedef 15 mΩ) | Bakır kaybı 0,85 W. Her +5 mΩ ≈ +0,28 W. 20 mΩ'a kadar kabul edilebilir (verim −%0,3). |
| Yapı | Ekranlı veya toroid güç bobini, 100 kHz'e uygun çekirdek | Çekirdek kaybı modelde yoktur; tezgâhta sıcaklık ölçülmelidir. |

Tek parça bulunamazsa eşdeğer kurulumlar (elektriksel olarak aynı):
- **İki eş bobin paralel:** her biri 68–100 µH, Isat ≥ 6 A, Irms ≥ 4,5 A, DCR ≤ 30 mΩ → toplam 34–50 µH.
- **İki eş bobin seri:** her biri 18–22 µH, Isat ≥ 12 A, Irms ≥ 9 A, DCR ≤ 7,5 mΩ → toplam 36–44 µH.

### Cout — çıkış kondansatörü

| Kriter | Değer | Neden |
|---|---|---|
| Kapasite | **1000 µF** ±%20 (hedef 1000 µF) | Sabit güç yüküyle LC sönümü ve yük adımı. 680 µF en kötü köşede 12,06 V'a çıktı; 1000 µF ile aynı köşe 11,81 V. Yaygın standart değer. |
| ESR (100 kHz) | **15–35 mΩ** (hedef 25 mΩ) | Alt sınır: ESR sönüm elemanıdır; altında köşede salınım büyür. Üst sınır: ripple (35 mΩ'da köşede ≈ 100 mV t-t). **Çok düşük ESR'li polimer tek başına uymaz; genel amaçlı (düşük ESR olmayan) elektrolitik de uymaz.** |
| Gerilim | ≥ 25 V | Çıkış 11 V; soft-start olmadan sert kalkışta 17 V'a çıkar. 16 V'luk parça yetmez. |
| Ripple akımı | ≥ 1 A RMS (100 kHz) | Devrede 0,55 A. |
| Tip | 105 °C, düşük empedanslı alüminyum elektrolitik, radyal | — |

Eşdeğer: 2 × 470 µF paralel, her biri ESR 30–70 mΩ, ripple akımı ≥ 0,5 A.

### Cin — giriş kondansatörleri

| Kriter | Değer | Neden |
|---|---|---|
| Toplam ripple akımı anma değeri | **≥ 4,5 A RMS** (100 kHz), paralel adetlerin toplamı | Devrede 3,8 A RMS; %20 pay. Boyutu belirleyen budur, kapasite değil. |
| Gerilim | ≥ 35 V | Giriş 26 V; batarya takılırken tepe ≈ 28 V. |
| Toplam kapasite | ≥ 440 µF (hedef 2 × 1000 µF) | 440 µF'ta giriş ripple'ı ≈ 125 mV t-t. 2 × 1000 µF / 35 V, ripple akımı şartını iki adetle sağlayan yaygın değerdir. |
| ESR (100 kHz) | ≤ 40 mΩ/adet (hedef 20 mΩ) | Giriş ripple'ının büyük kısmı ESR'dendir. |
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

1) Güç bobini (buck çıkış bobini, 100 kHz)
   - Endüktans 33–47 µH, tolerans ≤ ±%20
   - Doyma akımı Isat ≥ 12 A ve 9 A'de endüktans düşümü ≤ %10 (veri sayfasındaki L–I eğrisinden veya iki noktadan yaz)
   - Isıl akım Irms ≥ 9 A
   - DCR ≤ 15 mΩ (20 mΩ'a kadar olanları ayrı listele)
   - Ekranlı veya toroid
   Tek parça yoksa şu iki kurulumdan birine uygun parça ara:
   a) paralel bağlanacak 2 adet: 68–100 µH, Isat ≥ 6 A, Irms ≥ 4,5 A, DCR ≤ 30 mΩ
   b) seri bağlanacak 2 adet: 18–22 µH, Isat ≥ 12 A, Irms ≥ 9 A, DCR ≤ 7,5 mΩ

2) Çıkış kondansatörü
   - 1000 µF ±%20, ≥ 25 V, 105 °C, radyal alüminyum elektrolitik
   - 100 kHz ESR (veya empedans) 15–35 mΩ arasında — alt sınır da şarttır
   - 100 kHz ripple akımı ≥ 1 A RMS

3) Giriş kondansatörü (2 adet paralel kullanılacak)
   - ≥ 35 V, 105 °C, radyal alüminyum elektrolitik, 470–1000 µF
   - 100 kHz ripple akımı adet başına ≥ 2,25 A RMS (toplam ≥ 4,5 A)
   - 100 kHz ESR ≤ 40 mΩ

4) N-kanal güç MOSFET'i
   - VDS ≥ 55 V, RDS(on) ≤ 12 mΩ (VGS = 10 V, 25 °C, maksimum değer), ID ≥ 30 A
   - Toplam kapı yükü Qg ≤ 160 nC (değeri yaz; düşük olan tercih)
   - TO-220

5) Schottky diyot
   - VRRM ≥ 45 V (60 V tercih), IF(AV) ≥ 15 A toplam
   - İleri gerilim VF ≤ 0,58 V, 7,5 A toplam akımda, 25 °C (çift diyotta bacak başına 3,75 A; veri sayfası eğrisinden oku)
   - TO-220 veya TO-247

Sonucu her kalem için tablo olarak ver: parça numarası, üretici, kriter değerleri (veri sayfasından), satıcı, stok, fiyat, teslim süresi, bağlantılar.
```

## Parça değiştiğinde

1. Veri sayfası değerini `buck/ltspice/sematik_uret.py`, `buck/hesap.py` ve `buck/dogrula.py` (`SECILEN`) içine yaz.
2. `python buck/ltspice/sematik_uret.py`, `python buck/hesap.py`, `python buck/dogrula.py secilen` ve `pencere` koş.
3. Sonuçlar 9–12 V ve ripple ≤ 165 mV içinde kalıyorsa parça uygundur; bu dosyadaki "Aday parçalar" tabloları, [OPTIMIZASYON.md](OPTIMIZASYON.md) §5, README ve yol haritası yenilenir.

## Sonraki aşamalar için notlar

- **Kapı sürücüsü:** S1 üst taraftaki N-MOSFET'tir; kapısı anahtar düğümünün 10–12 V üstüne sürülmelidir (bootstrap'lı üst taraf sürücüsü). STP100N6F7'nin kapı yükü 30 nC (tipik): 100 kHz ve 12 V'ta sürücü gücü ≈ 0,04 W; yaygın 0,3–1 A'lik sürücüler yeterlidir.
- **Kontrol:** Ton aralığı 2,3–5,7 µs (yük 0,24–7,5 A, giriş 20–26 V); DCM/CCM geçişi ≈ 0,95 A; f0 ≈ 0,88 kHz, ESR sıfırı ≈ 6,4 kHz. Yumuşak kalkış zorunlu (sert kalkış 52 A / 17 V; L1 12,5 A'de doyar, gerçek tepe daha yüksek olur).
- **Isı:** D1 ≈ 1,8 W, S1 ≈ 0,15 W iletim + anahtarlama kaybı (modelde yok), L1 ≈ 0,8 W bakır + çekirdek. D1 soğutucu ister.
- **Akım ölçümü:** Bu aşamada yok; koruma/kontrol için sonraki aşamada eklenir.
- **Montaj:** Anahtarlama çevrimi (Cin → S1 → D1 → Cin) kısa tutulmalıdır.
