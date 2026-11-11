# Güç katı optimizasyonu ve doğrulama

**Tarih:** 11 Kasım 2026 · **Araç:** LTspice 26.1.1 (toplu kip), ideal anahtar/diyot, L/C + ESR/DCR · **Fiziksel ölçüm yok.**

Etiketler: **DATASHEET** üretici belgesi · **ÇIKARIM** üretici şemasından okunan, doğrulanmamış · **TAHMİN** yayımlanmış değer yok · **HESAP** `python buck/hesap.py` · **SİM** `python buck/dogrula.py`.

## 1. Sonuç

| Parametre | Eski | Önerilen | Gerekçe |
|---|---|---|---|
| Ana çalışma noktası (V1) | 22,2 V | **24,6 V** | Normal çalışma koşulu; test noktaları 20 / 22,2 / 24,6 / 25,2 / 26 V |
| Ton (100 kHz) | 5,14 µs | **4,65 µs** | 24,6 V'ta 11 V (SİM 11,008 V) |
| L1 | 33 µH, 15 mΩ | 33 µH, 15 mΩ (aynı) | Ripple %25; 22 µH %38'e, tepe akımı 9,4 A'e çıkarıyor; 47 µH sönümü bozuyor |
| Cout | 330 µF | **680 µF** | Sabit güç yüküyle LC sönümü; 330 ve 470 µF tolerans köşesinde salınıyor |
| Cout ESR | 15 mΩ (yalnız üst sınır) | **25 mΩ, pencere 20–30 mΩ** | ESR sönüm elemanıdır; alt sınır gerekir. Ripple 47 mV t-t, köşede 74 mV |
| Cin | 2 × 220 µF, 20 mΩ | aynı | 3,8 A RMS ve 125 mV t-t giriş ripple'ı (batarya modeliyle SİM); küçültmek için gerekçe yok |
| S1 Ron | 10 mΩ | aynı | İletim kaybı 0,26 W; anahtarlama kaybı modelde yok |
| D1 | 0,5 V + 10 mΩ | aynı | İletim kaybının 2,3 W'ı; daha düşük Vf parça aşamasında kazanç sağlar |
| fsw | 100 kHz | aynı | Tüm ripple/dinamik hedefler sağlanıyor; frekansı artırmanın bedeli (anahtarlama kaybı) bu modelle ölçülemez |
| Çıkış hedefi | 11 V / 7,5 A | aynı | Yük zarfı 6,64 A; pay %13. 11 V iki cihazın aralığında |
| .tran | 10 ms | 20 ms | 680 µF ile kalkış salınımı ~10 ms sürer |

Bu değerler güç katının **elektriksel temelidir**; devre açık çevrim kaldığı sürece gerçek O1/S2E bağlanamaz (bkz. §6).

**Parça seçimi sonrası (şematikteki son değerler):** "Önerilen" sütunu hedef değerlerdir. Parçalar seçildikten sonra şematiğe veri sayfası değerleri yazıldı: Cout ESR 28 mΩ, Cin 2 × 680 µF / 20 mΩ (ripple akımı anma değeri bu kapasiteyi gerektirdi), S1 Ron 11 mΩ, D1 0,46 V + 3,1 mΩ, Ton 4,63 µs. Parça listesi: [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md); bu değerlerle sonuçlar §5.

## 2. Yükler

| | T3 Gemstone O1 | SLAMTEC RPLIDAR S2E |
|---|---|---|
| Besleme aralığı | 5–12 V DC konnektör, 5 A — DATASHEET | 9–28 V, tipik 12 V — DATASHEET |
| 11 V uygun mu | Evet; üst çalışma sınırına 1 V pay | Evet; alt sınıra 2 V pay |
| Çalışma akımı | Yayımlanmamış. Zarf 5 A (giriş anma akımı); tipik 10 W, boşta 4 W — TAHMİN | 12 V'ta tipik 0,20 A, en çok 0,22 A — DATASHEET |
| Kalkış | Yayımlanmamış | 12 V'ta tipik 1,2 A, en çok 1,5 A; süre verilmemiş; "düşük gerilimde kalkış daha çok akım ister" — DATASHEET |
| Ripple sınırı | Yayımlanmamış | Besleme geriliminin %3'ü (11 V'ta ±330 mV) — DATASHEET |
| Mutlak maksimum | Yayımlanmamış | Yayımlanmamış (28 V çalışma üst sınırı) |
| Giriş koruması | DC girişte TPS259470 eFuse, aşırı gerilim bölücüsü 1 MΩ / 88,7 kΩ (1,2 V eşikle ≈ 14,7 V), SMAJ16CA TVS; arkasında TPS62180 (4–15 V çalışma, 17 V mutlak) — ÇIKARIM, v0.2 şeması | Bilinmiyor |

- Her iki cihazın girişinde DC-DC dönüştürücü var; bu yüzden testlerde **sabit güç yükü** olarak modellendi (S2E 2,64 W çalışma / 18 W kalkış, O1 4 / 10 / 55 W).
- 11 V'ta akım: S2E 0,24 A, S2E kalkış 1,64 A, O1 zarf 5 A → sürekli zarf 5,24 A, anlık zarf 6,64 A. **7,5 A hedefi yeterli**, artırmaya gerek yok.
- ArduPilot sayfası O1 DC girişini 5–12 V / **3 A** verir; üretici sayfaları 5 A. Zarf için 5 A kullanıldı.
- Tipik toplam yük (TAHMİN ≈ 1,2 A) bobinin CCM sınırına (0,95 A) çok yakındır; yalnız S2E veya boştaki O1 ile devre DCM'de çalışır. 7,5 A direnç tek başına temsil edici değildir.

Kaynaklar: [T3 Gemstone O1 ürün sayfası](https://t3gemstone.org/en/products/o1) · [O1 kart belgesi](https://docs.t3gemstone.org/en/boards/o1/introduction) · [O1 v0.2 şeması, s. 6–7](https://github.com/t3gemstone/hardware/blob/main/design/t3-gem-o1-v0_2.pdf) · [ArduPilot O1 sayfası](https://ardupilot.org/sub/docs/common-t3-gem-o1-overview.html) · [Waveshare RPLIDAR S2/S2E güç tablosu](https://www.waveshare.com/wiki/RPLIDAR_S2) (SLAMTEC datasheet tablosunun kopyası; SLAMTEC'in kendi PDF sunucusu bu oturumda erişim vermedi, önceki depo kaydı "datasheet S2E v1.5 s. 12" aynı değerleri veriyor) · [TPS25947](https://www.ti.com/lit/gpn/tps25947) · [TPS62180](https://www.ti.com/product/TPS62180).

## 3. Mevcut tasarımda bulunan sorunlar

1. **Yük modeli.** Tek doğrulama 7,5 A dirençti. Direnç LC'yi sönümler; sabit güç yükü sönümü azaltır. Eski değerlerle (33 µH / 330 µF / 15 mΩ) 57,6 W sabit güçte çıkış **2,9 V t-t sürekli salınıyor**, S2E kalkış darbesinde 8,97–13,29 V (SİM). HESAP sınırı: P < Vo²·C·(Rs+ESR)/L = 48 W.
2. **Hafif yük hiç incelenmemişti.** Sabit Ton'da 24,6 V girişte çıkış 0,6 A yükte 13,0 V, 0,24 A yükte 16,9 V'a çıkar (DCM; HESAP ve SİM aynı).
3. **Kalkış.** 34,7 A / 17,44 V yeniden doğrulandı (SİM). Neden: LC'ye basamak uygulanması; I tepe ≈ Vo/Z0, aşım yük sönümüne bağlı. Hafif yükte (12,6 W) aşım 21,0 V'a çıkar. L veya C seçimiyle giderilemez: taranan 9 adayın tamamında 17,2–17,6 V.
4. **Ana nokta ve test noktaları.** Hesap yalnız 20 / 22,2 / 26 V'u kapsıyordu; şematik 22,2 V'taydı.
5. **Duty.** `hesap.py` ideal D = Vo/Vin kullanıyordu; düşümlerle 24,6 V'ta Ton 4,47 değil 4,65 µs, ripple ≈ %4 daha büyük.
6. **Çıkış ripple sınırı** (%0,5 = 55 mV) cihazlardan türetilmemişti. S2E %3 ister; O1 için veri yok.
7. **Cout ESR hedefi tek taraflıydı** ("≤ 15 mΩ"). ESR düştükçe sönüm azalır.
8. **Cin simülasyonda etkisizdi:** V1 ideal kaynak olduğundan Cin akımı sıfırdır. Giriş tarafı ancak kaynak empedansıyla doğrulanabilir (§5.9).
9. Kayıp/verim hesabı yoktu.

## 4. Aday karşılaştırması

Tarama: L ∈ {22, 33, 47} µH × Cout ∈ {330, 470, 680} µF, ESR 15 mΩ, 24,6 V (SİM, `dogrula.py tarama`). Sütunlar: Ton sabitken S2E kalkış darbesi (57,6 → 73 → 57,6 W) sırasında çıkış ve darbe öncesi/sırası salınım.

| L µH | Cout µF | ΔIL A | ΔVo mV | Vmin/Vmax V | 57,6 W salınım mV | 73 W salınım mV | sert kalkış A / V |
|---|---|---|---|---|---|---|---|
| 22 | 330 | 2,85 | 45,9 | 10,15/11,84 | 103 | 1623 | 41,8 / 17,6 |
| 22 | 470 | 2,85 | 45,6 | 10,63/11,31 | 43 | 47 | 48,2 / 17,6 |
| 22 | 680 | 2,85 | 45,5 | 10,72/11,25 | 43 | 44 | 56,0 / 17,4 |
| 33 | 330 (eski) | 1,90 | 29,3 | 8,97/13,29 | 2913 | 4205 | 34,9 / 17,4 |
| 33 | 470 | 1,90 | 29,2 | 10,03/12,01 | 376 | 1364 | 40,4 / 17,6 |
| 33 | 680 | 1,90 | 29,0 | 10,64/11,30 | 34 | 64 | 47,0 / 17,6 |
| 47 | 330 | 1,33 | 20,8 | 8,28/14,23 | 4047 | 5945 | 29,8 / 17,2 |
| 47 | 470 | 1,33 | 20,6 | 8,87/13,29 | 3092 | 4411 | 34,5 / 17,4 |
| 47 | 680 | 1,33 | 20,4 | 10,16/11,84 | 455 | 1628 | 40,4 / 17,5 |

İletim verimi dokuz adayda da %96,0'dır; L ve Cout verimi ayırt etmez. Tolerans köşesinde (L +%20, Cout −%20) ESR 15 mΩ ile 33 µH / 680 µF de 57,6 W'ta 0,8 V t-t salındığı için ESR 25 mΩ'a alındı. En iyi üç aday, ESR 25 mΩ (pencere 20–30 mΩ) ile:

| | **A: 33 µH / 680 µF** (seçilen) | B: 22 µH / 470 µF | C: 33 µH / 470 µF | Eski: 33 / 330 / 15 mΩ |
|---|---|---|---|---|
| ΔIL @24,6 V | 1,90 A (%25) | 2,85 A (%38) | 1,90 A | 1,90 A |
| IL tepe, 26 V, L −%20 | 8,74 A | 9,36 A | 8,74 A | 8,75 A |
| CCM sınırı | 0,95 A | 1,43 A | 0,95 A | 0,95 A |
| ΔVo anma / köşe | 47 / 74 mV | 73 / 111 mV | 48 / 81 mV | 29 / 56 mV |
| S2E kalkışı, O1 zarfta: Vmin/Vmax | 10,65 / 11,31 V | 10,64 / 11,31 V | 10,62 / 11,42 V | 8,97 / 13,29 V |
| Salınım 57,6 / 73 W | 48 / 50 mV | 72 / 73 mV | 57 / 137 mV | 2913 / 4205 mV |
| Köşe (L+, C−, ESR−): salınım 57,6 / 73 W | 171 / 881 mV | 57 / 532 mV | 3065 / 4406 mV | — / 6281 mV |
| Köşe: Vmin/Vmax | 10,30 / 11,74 V | 10,45 / 11,48 V | 8,86 / 13,65 V | 8,20 / 14,93 V |
| Yük atma, ideal kontrolcü sınırı | 11,18 V | 11,17 V | 11,20 V | 11,16 V |
| Sert kalkış | 45,8 A / 17,1 V | 47,0 A / 17,1 V | 39,5 A / 17,2 V | 34,9 A / 17,4 V |

- **C elenir:** tolerans köşesinde sürekli zarf yükünde 3 V t-t salınır, 12 V'u aşar.
- **A ve B güvenlik ölçütlerini geçer.** B'nin köşe sönümü biraz daha iyi ve parçaları daha küçüktür; karşılığında akım ripple'ı %38 (köşede %49), tepe akımı 0,6 A, çıkış ripple'ı %55 daha yüksektir ve tipik yük (≈ 1,2 A) DCM içinde kalır.
- **A seçildi:** daha düşük akım/gerilim ripple'ı ve tepe akımı, CCM'in daha düşük yüke inmesi. 680 µF, köşede 12 V altında kalan en küçük standart değerdir; daha büyüğü yalnız sert kalkış akımını artırır.

### 4.1 Gerilim sabitliği öncelikli karşılaştırma (daha büyük L / Cout)

Soru: akım ripple'ı önemsenmeyip çıkış geriliminin giriş değişiminde sabit kalması öncelik yapılırsa değerler değişmeli mi? Aynı Z0'da daha büyük adaylar, ESR 25 mΩ, Ton sabit (SİM):

| | A: 33 µH / 680 µF | 47 µH / 1000 µF | 68 µH / 1500 µF | 33 µH / 1000 µF |
|---|---|---|---|---|
| Kararlı çıkış, 20 / 22,2 / 24,6 / 25,2 / 26 V giriş (7,5 A) | 8,89 / 9,90 / 11,00 / 11,27 / 11,64 V | aynı | aynı | aynı |
| Giriş 24,6 → 20 V rampası (57,6 W): Vmin / Vmax | 8,68 / 11,15 V | 8,14 / 11,59 V | 7,58 / 11,98 V | 8,53 / 11,27 V |
| Giriş 22,2 → 25,2 V rampası (57,6 W): Vmax | 12,66 V | 12,94 V | 13,32 V | 12,76 V |
| Çıkış ripple'ı anma / köşe | 47 / 74 mV | 33 / 52 mV | 23 / 36 mV | 47 / 74 mV |
| Sabit Ton'da 0,6 A yükte çıkış (24,6 V) | 12,98 V | 11,52 V | 11,17 V | 12,98 V |
| O1 tipik → zarf adımı: Vmin / Vmax | 10,04 / 11,80 V | 10,08 / 11,78 V | 10,11 / 11,75 V | 10,22 / 11,64 V |
| Köşe, S2E kalkışı @zarf: salınım 57,6 / 73 W | 171 / 881 mV | 83 / 434 mV | 152 / 411 mV | 36 / 54 mV |
| Sert kalkış | 45,8 A / 17,1 V | 46,1 A / 17,1 V | 46,5 A / 17,1 V | 53,3 A / 16,9 V |

- **Giriş değişiminin kararlı etkisi L ve Cout'tan bağımsızdır:** Vo ≈ D·Vin − düşümler; dört adayda da 20–26 V arasında 8,89–11,64 V. Parça değeriyle düzelmez; yalnız Ton girişe göre ayarlanırsa (ileri besleme veya geri besleme) sabit kalır.
- **Daha büyük L / Cout giriş geçişini kötüleştirir:** LC yavaşladığı için rampa sırasındaki aşım/çöküş büyür (68 µH / 1500 µF'ta 7,58–13,32 V).
- Büyük adayların kazancı ripple ve hafif yük yükselmesindedir; ikisi de zaten sınırların içinde veya geri beslemeyle giderilecek konulardır. **Seçim değişmedi (A).** Parça aşamasında yer varsa 33 µH / 1000 µF köşe sönümünü iyileştirir, karşılığı daha yüksek sert kalkış akımıdır.

## 5. Seçilen parçalarla test sonuçları (SİM)

Şematikteki değerler = seçilen parçaların veri sayfası değerleri ([PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md)): L 33 µH / 15 mΩ · Cout 680 µF / 28 mΩ · Cin 2 × 680 µF / 20 mΩ · Ron 11 mΩ · Vf 0,46 V + 3,1 mΩ · 100 kHz. Tablolar `python buck/dogrula.py secilen` çıktısıdır.

### 5.1 Kararlı durum, 7,5 A direnç yük, Ton her girişte 11 V'a ayarlı (ideal regülasyon varsayımı)

| Vin V | Ton µs | Vo V | ΔVo mV | IL A | S1 rms A | D1 ort A | Cout rms A | P S1 W | P D1 W | P L1 W | P toplam W | η iletim % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 5.675 | 11.001 | 42.4 | 6.74–8.26 | 5.66 | 3.24 | 0.43 | 0.35 | 1.56 | 0.85 | 2.77 | 96.75 |
| 22.2 | 5.120 | 11.001 | 53.2 | 6.64–8.37 | 5.39 | 3.65 | 0.48 | 0.32 | 1.77 | 0.85 | 2.94 | 96.56 |
| 24.6 | 4.629 | 10.999 | 58.6 | 6.56–8.46 | 5.12 | 4.02 | 0.53 | 0.29 | 1.94 | 0.85 | 3.09 | 96.39 |
| 25.2 | 4.519 | 10.999 | 53.7 | 6.54–8.46 | 5.06 | 4.10 | 0.54 | 0.28 | 1.98 | 0.85 | 3.12 | 96.35 |
| 26 | 4.382 | 11.000 | 61.4 | 6.51–8.51 | 4.99 | 4.21 | 0.56 | 0.27 | 2.03 | 0.85 | 3.17 | 96.30 |

Verim yalnız iletim kaybıdır; anahtarlama, çekirdek ve sürücü kayıpları **modelde yoktur**, gerçek verim daha düşük olacaktır. Ton ayar doğruluğu ±5 mV; ripple 1 ms pencerede t-t.

![Kararlı durum](grafik/kararli.svg)

### 5.2 Kararlı durum, gerçek yük senaryoları, 24,6 V, Ton 11 V'a ayarlı (sabit güç yükü)

| Senaryo | P W | I@11V A | Ton µs | Kip | Vo V | ΔVo mV | IL tepe A | η iletim % |
|---|---|---|---|---|---|---|---|---|
| yalnız S2E çalışma | 2.64 | 0.24 | 2.303 | DCM | 11.008 | 27.7 | 0.95 | 97.6 |
| yalnız O1 boşta (tahmin) | 4.00 | 0.36 | 2.835 | DCM | 10.993 | 34.3 | 1.17 | 97.5 |
| yalnız O1 tipik (tahmin) | 10.00 | 0.91 | 4.483 | DCM | 10.984 | 55.1 | 1.85 | 97.5 |
| O1 boşta + S2E | 6.64 | 0.60 | 3.653 | DCM | 10.976 | 44.4 | 1.51 | 97.5 |
| O1 tipik + S2E | 12.64 | 1.15 | 4.573 | CCM | 10.999 | 53.9 | 2.09 | 97.5 |
| O1 tipik + S2E kalkış | 28.00 | 2.55 | 4.585 | CCM | 10.999 | 54.1 | 3.49 | 97.3 |
| yalnız O1 zarf 5 A | 55.00 | 5.00 | 4.606 | CCM | 11.001 | 61.9 | 5.96 | 96.8 |
| O1 zarf + S2E | 57.64 | 5.24 | 4.608 | CCM | 11.000 | 54.9 | 6.18 | 96.8 |
| O1 zarf + S2E kalkış | 73.00 | 6.64 | 4.620 | CCM | 11.000 | 60.7 | 7.60 | 96.5 |

Ripple her senaryoda S2E sınırının (±330 mV) çok altında. DCM'de gereken Ton yükle 2,3–4,5 µs arasında değişir: geri besleme bu aralığı kapsamalıdır.

### 5.3 Açık çevrim: Ton sabit (24,6 V / 7,5 A'ya ayarlı), giriş ve yük değişince kararlı çıkış [V]

| Vin V \ yük A@11V | 0.24 | 0.6 | 1.15 | 2.5 | 5.24 | 7.5 |
|---|---|---|---|---|---|---|
| 20 | 13.67 | 10.52 | 9.01 | 8.99 | 8.94 | 8.90 |
| 22.2 | 15.18 | 11.69 | 10.03 | 10.00 | 9.94 | 9.90 |
| 24.6 | 16.82 | 12.96 | 11.14 | 11.11 | 11.05 | 11.00 |
| 25.2 | 17.23 | 13.28 | 11.42 | 11.39 | 11.32 | 11.27 |
| 26 | 17.78 | 13.70 | 11.79 | 11.76 | 11.69 | 11.64 |

O1'in 5–12 V aralığı yalnız 24,6 V civarında ve yük CCM'deyken sağlanır. **Açık çevrim O1 için hiçbir L/C değeriyle güvenli değildir.**

### 5.4 Yük adımları, 24,6 V, Ton sabit (kontrolcü tepki vermiyor = kötümser sınır)

| Adım | P W | Vmin V | Vmax V | ara kararlı V | ara salınım mV | son kararlı V | son salınım mV | IL tepe A |
|---|---|---|---|---|---|---|---|---|
| S2E kalkışı, O1 tipik | 12.6→28.0 | 10.68 | 11.29 | 10.97 | 53 | 10.99 | 53 | 4.6 |
| O1 tipik→zarf→tipik, S2E çalışıyor | 12.6→57.6 | 10.05 | 11.80 | 10.91 | 55 | 10.99 | 53 | 9.7 |
| S2E kalkışı, O1 zarf | 57.6→73.0 | 10.64 | 11.31 | 10.97 | 56 | 11.00 | 54 | 8.9 |
| O1 zarf→boşta→zarf, S2E çalışıyor | 57.6→6.6 | 10.11 | 15.31 | 15.22 | 174 | 11.00 | 55 | 9.8 |

İlk üç adımda çıkış kontrolcü olmadan bile 10,0–11,8 V içinde kalır. Son satır DCM yükselmesidir (§5.3) ve yalnız geri beslemeyle giderilir.

![Yük adımı](grafik/yuk_adimi.svg)

### 5.5 Yük atma, ideal kontrolcü sınırı (yük düştüğü anda duty = 0; en iyi durum)

| Vin V | 73→6,6 W Vtepe V | 82,5→2,6 W Vtepe V |
|---|---|---|
| 20 | 11.192 | 11.229 |
| 22.2 | 11.196 | 11.233 |
| 24.6 | 11.199 | 11.236 |
| 25.2 | 11.200 | 11.237 |
| 26 | 11.200 | 11.238 |

Bobindeki enerji Cout'a boşaldığında tepe en çok 11,24 V'tur; 12 V'a 0,76 V pay kalır. Gerçek kapalı çevrim, tepki gecikmesi kadar bunun üstüne çıkar; bu pay kontrol tasarımının bütçesidir.

### 5.6 Soğuk kalkış

| Vin V | Yük | sert: IL tepe A | sert: Vo tepe V | 5 ms duty rampası: IL tepe A | 5 ms duty rampası: Vo tepe V |
|---|---|---|---|---|---|
| 20 | 7,5 A direnç | 45.5 | 17.11 | 9.7 | 11.24 |
| 22.2 | 7,5 A direnç | 45.6 | 17.12 | 9.8 | 11.23 |
| 24.6 | 7,5 A direnç | 45.8 | 17.15 | 9.9 | 11.24 |
| 25.2 | 7,5 A direnç | 45.8 | 17.15 | 9.9 | 11.24 |
| 26 | 7,5 A direnç | 45.9 | 17.16 | 10.0 | 11.24 |
| 24.6 | O1 tipik + S2E (12,6 W) | 47.5 | 19.44 | 5.4 | 11.28 |

Sert kalkış aşımı O1'in TVS çalışma gerilimini (16 V, ÇIKARIM) ve TPS62180 mutlak sınırını (17 V) aşar. Model bobini doğrusal alır; gerçek 2300HT-330 bu akımda doyacağından tepe akım daha yüksek olur. Duty rampası bir **varsayımdır** (soft-start devresi tasarlanmadı); yalnız aşımın kaynağının basamak uyarımı olduğunu ve yumuşak kalkışla giderildiğini gösterir.

![Kalkış](grafik/kalkis.svg)

### 5.7 Giriş değişimi, Ton sabit, O1 zarf + S2E (57,6 W)

| Vin V (1 ms rampa) | Vmin V | Vmax V | ara kararlı V |
|---|---|---|---|
| 24.6→20→24.6 | 8.68 | 11.16 | 8.85 |
| 24.6→26→24.6 | 10.93 | 11.70 | 11.65 |
| 22.2→25.2→22.2 | 10.88 | 12.65 | 12.55 |

Çıkış girişi oransal izler (ΔVo ≈ D·ΔVin). 20 V'ta S2E'nin 9 V alt sınırının altına, batarya dolarken O1'in 12 V sınırının üstüne çıkar.

### 5.8 Tolerans köşeleri (L −%30/+%15, Cout ±%20, ESR ±%20), 7,5 A

| Köşe | Vin V | ΔVo mV | IL tepe A | zarf adım Vmin/Vmax | 73 W salınım mV | yük atma sınırı V | sert kalkış A/V | rampalı kalkış A/V |
|---|---|---|---|---|---|---|---|---|
| anma | 24.6 | 58.6 | 8.46 | 10.64/11.31 | 56 | 11.20 | 45.8/17.2 | 9.9/11.24 |
| ripple en kötü: L−, C−, ESR+ | 26 | 93.6 | 8.91 | 10.66/11.31 | 97 | 11.24 | 48.0/16.9 | 10.1/11.19 |
| Z0 en yüksek: L+, C−, ESR− | 24.6 | 43.2 | 8.34 | 10.45/11.48 | 720 | 11.17 | 39.9/17.4 | 9.5/11.22 |
| Z0 en düşük: L−, C+, ESR− | 26 | 63.1 | 8.91 | 10.72/11.24 | 64 | 11.15 | 58.1/17.2 | 10.7/11.22 |

L −%30, bobinin akım altındaki endüktans düşümünü (7,5–8,5 A'de ≈ −%17, doğrusal ara değer varsayımı) ve −%15 toleransı birlikte kapsar. En zayıf köşe L+, C−, ESR−: 73 W darbesinde 0,7 V t-t salınım var ama çıkış 12 V altında kalır.

### 5.9 Giriş tarafı, batarya+kablo modeli (VARSAYIM 40 mΩ + 1 µH/10 mΩ), 7,5 A

| Batarya V | Vo V | ΔVin mV t-t | Cin toplam rms A | Cin ESR kaybı W |
|---|---|---|---|---|
| 20 | 11.001 | 95 | 3.72 | 0.14 |
| 24.6 | 11.000 | 97 | 3.76 | 0.14 |
| 26 | 11.004 | 97 | 3.75 | 0.14 |

Batarya 26 V sıcak takma (anahtar kapalı): V(vin) tepe 26.0 V, batarya akımı tepe 329 A

Değerler tahmini kaynak empedansına bağlıdır. Cin toplam ripple akımı 3,76 A; iki kondansatörün toplam anma değeri 4,36 A.

## 6. Doğrulanamayanlar ve sonraki aşamaya kalanlar

**Geri besleme aşamasının çözmesi gerekenler (bu güç katıyla çözülemez):**
- Regülasyon: giriş 20–26 V ve yük 0,24–7,5 A aralığında 11 V; Ton 2,3–5,7 µs; DCM/CCM geçişi 0,95 A'de.
- Yumuşak kalkış: sert kalkış 46 A / 17–19 V; birkaç ms'lik rampa 10 A / 11,3 V'a indirir.
- Yük atma bütçesi: ideal sınır 11,24 V; 12 V'a kalan 0,76 V kontrol gecikmesine ve ayar toleransına paylaştırılacak.
- Tasarım verileri: f0 = 1,06 kHz, Z0 = 0,22 Ω, ESR sıfırı 8,4 kHz; yük sabit güç karakterli (negatif artımsal direnç, zarfta −2,1 Ω).
- Anahtar kısa devre kalırsa çıkış giriş gerilimine çıkar; O1 için bağımsız aşırı gerilim koruması ayrı bir konudur.

**Doğrulanmamış veriler:**
- O1'in gerçek tüketimi, kalkış akımı, mutlak maksimum gerilimi ve ripple toleransı yayımlanmamış; 4 / 10 W değerleri tahmindir. Ölçülmeli veya üreticiden istenmelidir.
- O1 giriş koruması (eFuse OVLO ≈ 14,7 V, TVS, TPS62180) v0.2 şemasının metin katmanından çıkarıldı; devre bağlantıları görülerek doğrulanmadı, eldeki kart revizyonu farklı olabilir. 12 V üstü için dayanım varsayılmamalıdır.
- S2E kalkış darbesinin süresi ve 11 V'taki değeri (datasheet 12 V verir); testlerde sabit güç varsayıldı.
- Batarya iç direnci ve kablo endüktansı tahmindir.
- L1 (Bourns 2300HT-330) endüktansının akımla değişimi iki veri sayfası noktasından doğrusal alındı; 100 kHz çekirdek kaybı bilinmiyor.
- L1, Cout ve Cin için Türkiye stoku doğrulanamadı; kondansatör empedans/ripple değerleri dağıtıcı listelerindendir.

**İdeal modelin kapsamadıkları:** anahtarlama kayıpları ve geçiş süreleri, diyot ters toparlanma/kapasitesi, bobin doyumu ve çekirdek kaybı, kondansatör ESL'i ve kapasitenin gerilim/sıcaklıkla değişimi, parazitik zil, ısıl davranış, EMI. Verim ve tepe gerilim/akım değerleri bu etkiler olmadan verilmiştir.

## 7. Tekrar üretme

```
python buck/hesap.py            # analitik özet
python buck/dogrula.py secilen  # §5 tabloları (≈ 15 dk)
python buck/dogrula.py tarama   # §4 taraması (≈ 15 dk)
python buck/dogrula.py mevcut   # eski değerlerle aynı testler
python buck/dogrula.py grafik   # buck/grafik/*.svg
```

LTspice yolu farklıysa `LTSPICE` ortam değişkeniyle verilir. Test netlistleri geçici klasörde üretilir; ana şematiğe `.meas`, `.param` veya yük modeli eklenmez.
