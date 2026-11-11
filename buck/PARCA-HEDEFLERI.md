# Parça Kriterleri — Ana Güç Devresi

**Tarih:** 11 Kasım 2026
**Durum:** Belirli bir parça numarası **seçilmedi**. Bu dosya, parça ararken sağlanması gereken ölçülebilir kriterleri ve her kriterin nedenini verir. Kriterleri sağlayan her parça kabul edilir; şematik parça numarasından bağımsızdır.
**Sınıf:** analitik hesap (`hesap.py`) + LTspice, ideal elemanlar (`dogrula.py`). Fiziksel ölçüm yok.

Çalışma noktası: Vin 20 / 22,2 / **24,6** / 25,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz. Seçim süreci ve test sonuçları: [OPTIMIZASYON.md](OPTIMIZASYON.md).

## Kriterler

"Şematik" sütunu LTspice şematiğindeki değerdir. Ron, Vf ve DCR için bu değer kabul sınırının kendisidir: daha iyi parça yalnız kaybı azaltır, başka bir şeyi bozmaz.

### L1 — bobin

| Kriter | Değer | Neden |
|---|---|---|
| Endüktans | **33–47 µH**, tolerans ≤ ±%20 (şematik 33 µH) | 33 µH'de akım ripple'ı %25. 22 µH'de CCM sınırı 1,4 A'e çıkar, tipik yük (≈ 1,2 A) kesintili iletimde kalır ve açık çevrim testinde çıkış 8,8 V'a düşer. 47 µH üstü Cout 1000 µF ile sönümü zayıflatır. 33, 39 ve 47 µH tolerans köşeleriyle doğrulandı. |
| Doyma akımı (Isat) | ≥ 12 A; 9 A'de endüktans düşümü ≤ %10 | Tepe akım en kötü köşede 8,9 A; %30 pay. Köşe testleri toleransla birlikte toplam −%30'a kadar koşuldu. |
| Isıl akım (Irms) | ≥ 9 A | 7,5 A sürekli; %20 pay. |
| DCR | ≤ 15 mΩ (şematik 15 mΩ) | Bakır kaybı 0,85 W. Her +5 mΩ ≈ +0,28 W. 20 mΩ'a kadar kabul edilebilir (verim −%0,3). |
| Yapı | Ekranlı veya toroid güç bobini, 100 kHz'e uygun çekirdek | Çekirdek kaybı modelde yoktur; tezgâhta sıcaklık ölçülmelidir. |

Tek parça bulunamazsa eşdeğer kurulumlar (elektriksel olarak aynı):
- **İki eş bobin paralel:** her biri 68–100 µH, Isat ≥ 6 A, Irms ≥ 4,5 A, DCR ≤ 30 mΩ → toplam 34–50 µH.
- **İki eş bobin seri:** her biri 18–22 µH, Isat ≥ 12 A, Irms ≥ 9 A, DCR ≤ 7,5 mΩ → toplam 36–44 µH.

### Cout — çıkış kondansatörü

| Kriter | Değer | Neden |
|---|---|---|
| Kapasite | **1000 µF** ±%20 (şematik 1000 µF) | Sabit güç yüküyle LC sönümü ve yük adımı. 680 µF en kötü köşede 12,06 V'a çıktı; 1000 µF ile aynı köşe 11,81 V. Yaygın standart değer. |
| ESR (100 kHz) | **15–35 mΩ** (şematik 25 mΩ) | Alt sınır: ESR sönüm elemanıdır; altında köşede salınım büyür. Üst sınır: ripple (35 mΩ'da köşede ≈ 100 mV t-t). **Çok düşük ESR'li polimer tek başına uymaz; genel amaçlı (düşük ESR olmayan) elektrolitik de uymaz.** |
| Gerilim | ≥ 25 V | Çıkış 11 V; soft-start olmadan sert kalkışta 17 V'a çıkar. 16 V'luk parça yetmez. |
| Ripple akımı | ≥ 1 A RMS (100 kHz) | Devrede 0,55 A. |
| Tip | 105 °C, düşük empedanslı alüminyum elektrolitik, radyal | — |

Eşdeğer: 2 × 470 µF paralel, her biri ESR 30–70 mΩ, ripple akımı ≥ 0,5 A.

### Cin — giriş kondansatörleri

| Kriter | Değer | Neden |
|---|---|---|
| Toplam ripple akımı anma değeri | **≥ 4,5 A RMS** (100 kHz), paralel adetlerin toplamı | Devrede 3,8 A RMS; %20 pay. Boyutu belirleyen budur, kapasite değil. |
| Gerilim | ≥ 35 V | Giriş 26 V; batarya takılırken tepe ≈ 28 V. |
| Toplam kapasite | ≥ 440 µF (şematik 2 × 1000 µF) | 440 µF'ta giriş ripple'ı ≈ 125 mV t-t. 2 × 1000 µF / 35 V, ripple akımı şartını iki adetle sağlayan yaygın değerdir. |
| ESR (100 kHz) | ≤ 40 mΩ/adet (şematik 20 mΩ) | Giriş ripple'ının büyük kısmı ESR'dendir. |
| Tip | 105 °C, düşük empedanslı alüminyum elektrolitik | — |

### S1 — anahtar (N-kanal MOSFET)

| Kriter | Değer | Neden |
|---|---|---|
| VDS | ≥ 55 V (tercihen 60–100 V) | 26 V giriş, takma anında 28 V; zil payı. |
| RDS(on) @ VGS 10 V, 25 °C | **≤ 12 mΩ** (şematik 12 mΩ) | İletim kaybı 0,32 W. 18 mΩ'a kadar kabul edilebilir (+0,16 W). |
| ID (sürekli) | ≥ 30 A | 5,7 A RMS, 8,9 A tepe; ısıl pay. |
| Toplam kapı yükü Qg | ≤ 160 nC (tercihen ≤ 80 nC) | Sonraki aşamada sürücü akımını ve anahtarlama kaybını belirler. |
| Kılıf | TO-220 (soğutucuya bağlanabilir, delikli) | El montajı ve soğutma. |

### D1 — serbest geçiş diyodu (Schottky)

| Kriter | Değer | Neden |
|---|---|---|
| VRRM | ≥ 45 V (tercihen 60 V) | Ters gerilim 26–28 V. 45 V'ta pay 1,6×; zil ölçülmeden 60 V tercih edilir. |
| IF(AV) | ≥ 15 A toplam (çift diyotta iki bacak paralel) | Ortalama 4,2 A (26 V); düşük akım yoğunluğu Vf'yi düşürür. |
| VF @ 7,5 A toplam, 25 °C | **≤ 0,58 V** (şematik 0,5 V + 10 mΩ) | İletim kaybının üçte ikisi (2,3 W) diyottadır. Her 0,1 V ≈ 0,4 W. |
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

## Parça bulunduğunda

1. Veri sayfası değerini `buck/ltspice/sematik_uret.py`, `buck/hesap.py` ve `buck/dogrula.py` (`SECILEN`) içine yaz.
2. `python buck/ltspice/sematik_uret.py`, `python buck/hesap.py`, `python buck/dogrula.py secilen` ve `pencere` koş.
3. Sonuçlar 9–12 V ve ripple ≤ 165 mV içinde kalıyorsa parça uygundur; [OPTIMIZASYON.md](OPTIMIZASYON.md) §5 yenilenir.

## Sonraki aşamalar için notlar

- **Kapı sürücüsü:** S1 üst taraftaki N-MOSFET'tir; kapısı anahtar düğümünün 10–12 V üstüne sürülmelidir (bootstrap'lı üst taraf sürücüsü). Qg 120 nC'lik bir parçada 100 kHz ve 12 V'ta sürücü gücü ≈ 0,15 W; 50 ns altı geçiş için ≥ 1 A tepe akımlı sürücü gerekir.
- **Kontrol:** Ton aralığı 2,3–5,7 µs (yük 0,24–7,5 A, giriş 20–26 V); DCM/CCM geçişi ≈ 0,95 A; f0 ≈ 0,88 kHz, ESR sıfırı ≈ 6,4 kHz. Yumuşak kalkış zorunlu (sert kalkış 53 A / 17 V).
- **Isı:** D1 ≈ 2,3 W, S1 ≈ 0,3 W iletim + anahtarlama kaybı (modelde yok). İkisi de soğutucu ister.
- **Akım ölçümü:** Bu aşamada yok; koruma/kontrol için sonraki aşamada eklenir.
- **Montaj:** Anahtarlama çevrimi (Cin → S1 → D1 → Cin) kısa tutulmalıdır.
