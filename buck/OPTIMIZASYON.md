# Güç katı optimizasyonu ve doğrulama

**Tarih:** 11 Kasım 2026 · **Araç:** LTspice 26.1.1 (toplu kip), ideal anahtar/diyot, L/C + ESR/DCR · **Fiziksel ölçüm yok.**

Etiketler: **DATASHEET** üretici belgesi · **ÇIKARIM** üretici şemasından okunan, doğrulanmamış · **TAHMİN** yayımlanmış değer yok · **HESAP** `python buck/hesap.py` · **SİM** `python buck/dogrula.py`.

Bu belge güncel kararı anlatır. Değerler parça numarasından bağımsızdır; parça kriterleri [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md) dosyasındadır.

## 1. Karar

| Parametre | Hedef (aday parçalardan önce) | Kabul aralığı | Neden | Kanıt |
|---|---|---|---|---|
| Ana çalışma noktası | 24,6 V | 20–26 V; test 20 / 22,2 / 24,6 / 25,2 / 26 V | 6S bataryanın normal çalışma gerilimi | §5.1 |
| Çıkış | 11 V / 7,5 A | — | 11 V iki yükün aralığında (O1 5–12 V, S2E 9–28 V); yük zarfı 6,64 A, pay %13 | §2 |
| fsw | 100 kHz | sabit | Ripple ve dinamik hedefler sağlanıyor; frekansı artırmanın bedeli (anahtarlama kaybı) ideal modelle ölçülemez | §5.1 |
| Ton | 4,59 µs | — | 24,6 V / 7,5 A'de 11 V (SİM 11,000 V, 19–20 ms) | §5.1 |
| L1 | 33 µH el sarım, 7,81 mΩ (@20 °C, HESAP) | 33 µH (47 µH yalnız satın alınan parça, S2E kalkış süresi ölçülünce; 39 µH ve 47 µH el sarım kaldı, §4.4); Isat ≥ 12 A; DCR 6,5–15 mΩ (el sarım hedefi 8–10) | Akım ripple'ı %25; CCM sınırı 0,95 A tipik yükün (≈ 1,2 A) altında. 22 µH elendi (tipik yük DCM'de, çıkış 8,8 V'a düşer). DCR alt sınırı: sönüm | §4.1, §4.4 |
| Cout | 1000 µF | 1000 µF ±%20; ≥ 25 V | Sabit güç yüküyle LC sönümü. 330 µF sürekli salınır; 680 µF en kötü köşede 12,06 V; 1000 µF aynı köşede 11,81 V | §4.1, §4.4 |
| Cout ESR | 25 mΩ | 15–35 mΩ | Alt sınır sönüm için, üst sınır ripple için | §4.2, §4.4 |
| Cin | 2 × 1000 µF, 20 mΩ | toplam ripple akımı ≥ 4,5 A; ≥ 35 V; ≥ 440 µF | 3,8 A RMS giriş ripple akımı parçanın boyunu belirler | §5.9 |
| S1 | Ron 12 mΩ | RDS(on) ≤ 12 mΩ; VDS ≥ 55 V | İletim kaybı 0,32 W | §5.1 |
| D1 | 0,5 V + 10 mΩ | VF ≤ 0,58 V @ 7,5 A; VRRM ≥ 45 V | İletim kaybının üçte ikisi (2,3 W) | §5.1 |

Geçmiş: başlangıç değerleri 22,2 V / Ton 5,14 µs / Cout 330 µF (15 mΩ) / Cin 2 × 220 µF idi. Cout önce 680 µF'a, tolerans köşesi ve standart değer bulunurluğu için 1000 µF'a alındı. L1, fsw ve çıkış hedefi baştan beri aynıdır.

**Aday parçalar (kesin seçim değil):** tablodaki "Hedef" sütunu aday parçalar belirlenmeden önce şematikte kullanılan değerlerdir. Şematik (1. sıra): L1 33 µH el sarım / 7,81 mΩ (Magnetics Kool Mµ 40µ `0077536A7`, 22 sarım; 2. sıra satın alma: Würth 74435583300, DCR 14,52 mΩ), Cout 1000 µF / 35 mΩ (Nichicon UHE1E102MHD6TO; **35 mΩ maks. empedanstır, ESR varsayımıdır**), Cin 2 × 1000 µF / 15 mΩ (TDK B41859D7108M000; 15 mΩ da maks. empedans), S1 5,6 mΩ (STP100N6F7), D1 0,38 V + 8 mΩ (STPS40M60CT), Ton 4,59 µs. Hepsi kabul aralıklarının içindedir; sıralama gerekçesi [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md) dosyasında, bu değerlerle sonuçlar §5'tedir.

Bu değerler güç katının **elektriksel temelidir**; devre açık çevrim kaldığı sürece gerçek O1/S2E bağlanamaz (§6).

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

## 4. Değerler nasıl seçildi

Ölçüt: gerçek yük senaryolarında (sabit güç) ve tolerans köşelerinde çıkışın **9–12 V** içinde kalması (S2E alt sınırı, O1 üst sınırı) ve ripple ≤ 165 mV t-t (çıkışın %1,5'i; S2E sınırı ±%3). Testlerde Ton sabittir: kontrolcünün hiç tepki vermediği kötümser durum.

### 4.1 İlk tarama: L × Cout (ESR 15 mΩ, 24,6 V)

`dogrula.py tarama`. Sütunlar: S2E kalkış darbesi (57,6 → 73 → 57,6 W) sırasında çıkış ve darbe öncesi/sırası salınım.

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

- İletim verimi dokuz adayda da %96,0'dır: **L ve Cout verimi ayırt etmez**, ayırt eden sönümdür.
- Sabit güç yükü LC'yi sönümsüzleştirir. Kararlılık sınırı (HESAP): P < Vo²·C·(Rs+ESR)/L. Cout/L oranı ve ESR büyüdükçe sınır yükselir.
- Sert kalkış aşımı tüm adaylarda 17,2–17,6 V: L/C ile giderilemez, yumuşak kalkış gerekir.

### 4.2 Cout ESR'sinin alt sınırı

33 µH / 680 µF, köşe L +%20 / Cout −%20, 57,6 W sabit güçte sürekli salınım (SİM):

| Cout ESR | 7,5 mΩ | 10 mΩ | 15 mΩ | 25 mΩ |
|---|---|---|---|---|
| Salınım t-t | 2480 mV | 2448 mV | 792 mV | 65 mV |

ESR, LC'nin sönüm direncidir. Bu yüzden "ESR ne kadar düşükse o kadar iyi" bu devrede **yanlıştır**; alt sınır konur.

### 4.3 Giriş değişimi ve daha büyük L / Cout

Ton sabit, ESR 25 mΩ (SİM):

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

- **Giriş değişiminin kararlı etkisi L ve Cout'tan bağımsızdır:** Vo ≈ D·Vin − düşümler. Parça değeriyle düzelmez; yalnız Ton girişe göre ayarlanırsa (ileri besleme veya geri besleme) sabit kalır.
- Çok büyük L / Cout giriş geçişini kötüleştirir (LC yavaşlar): 68 µH / 1500 µF'ta 7,58–13,32 V.
- 33 µH / 1000 µF, 33 µH / 680 µF'a göre yük adımında ve köşe sönümünde daha iyidir; bedeli daha yüksek sert kalkış akımıdır (yumuşak kalkışla zaten giderilir).

### 4.4 Kabul penceresi

`dogrula.py pencere`. Her L/Cout çifti için ESR penceresinin iki kenarı ve tolerans köşeleri (L −%30/+%20, Cout −%20) koşulur.

İlk deneme (Cout = 20 × L kuralı, ESR 20–35 mΩ):

| L µH | Cout µF | ΔIL A | IL tepe köşe A | ΔVo ESR 35 mΩ: anma / köşe mV | S2E kalkışı @zarf V | O1 tipik→zarf V | köşe: S2E kalkışı @zarf V | köşe: O1 tipik→zarf V | köşe salınım 57,6 / 73 W mV | köşe yük atma sınırı V | 9–12 V ve ≤165 mV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22 | 470 | 2.86 | 9.62 | 104 / 146 | 10.64–11.31 | 8.78–11.02 | 10.46–11.46 | 9.62–11.85 | 56 / 398 | 11.25 | KALDI |
| 33 | 680 | 1.89 | 8.91 | 66 / 98 | 10.64–11.31 | 10.03–11.80 | 10.38–11.67 | 9.78–12.06 | 130 / 717 | 11.24 | KALDI |
| 47 | 1000 | 1.33 | 8.51 | 46 / 75 | 10.70–11.31 | 10.07–11.79 | 10.67–11.24 | 9.84–11.88 | 83 / 367 | 11.23 | GEÇTİ |

- 22 µH / 470 µF: tipik yük (1,15 A) CCM sınırının (1,43 A) altında; Ton DCM'de ayarlıyken yük artınca çıkış 8,78 V'a düşer. **22 µH elendi.**
- 33 µH / 680 µF: en kötü köşede O1 tipik → zarf adımında 12,06 V. **680 µF elendi.**

Son pencere (Cout 1000 µF, ESR 15–35 mΩ), şematikteki 1. sıra değerleriyle (el sarım L1 DCR 7,81 mΩ, Ron 5,6 mΩ, Vf 0,38 V + 8 mΩ; 12 Kasım 2026 koşusu):

| L µH | Cout µF | ΔIL A | IL tepe köşe A | ΔVo ESR 35 mΩ: anma / köşe mV | S2E kalkışı @zarf V | O1 tipik→zarf V | köşe: S2E kalkışı @zarf V | köşe: O1 tipik→zarf V | köşe salınım 57,6 / 73 W mV | köşe yük atma sınırı V | 9–12 V ve ≤165 mV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 33 | 1000 | 1.90 | 8.93 | 70 / 104 | 10.64–11.28 | 10.07–11.56 | 10.48–11.48 | 9.99–11.85 | 152 / 1002 | 11.23 | GEÇTİ |
| 39 | 1000 | 1.60 | 8.71 | 55 / 89 | 10.68–11.26 | 10.15–11.71 | 9.47–12.81 | 9.91–12.62 | 1671 / 2994 | 11.21 | KALDI |
| 47 | 1000 | 1.32 | 8.49 | 46 / 68 | 10.64–11.38 | 10.09–11.92 | 9.24–12.86 | 9.64–12.27 | 2605 / 3619 | 11.23 | KALDI |

- **33 µH geçer** (şematik değeri); 12 V'a pay 0,15 V (O1 tipik → zarf adımı, köşe). Sönümü en zayıf köşede 73 W salınımı **1002 mV** (Würth DCR 14,52 mΩ ile 216 mV idi): düşük DCR sönümü azaltır.
- **39 µH ve 47 µH kalır:** köşede yük adımında 12,81 V (39 µH) ve 12,86 V (47 µH); 73 W salınımı 3 V'a varır. 47 µH, DCR 14,52 mΩ ile 0,04 V payla geçmişti; DCR 7,81 mΩ ile geçmez. 47 µH yalnız yüksek DCR'li satın alınan parçayla (Würth 7443783533470, DCR en çok 12,98 mΩ) ve S2E kalkış süresi gerçek sistemde ölçüldükten sonra değerlendirilebilir.
- Son sütundaki karar 9–12 V'u (dört yük adımı ve yük atma) ve 26 V köşe kararlı ripple'ını sınar; "köşe salınım" sütunu yalnız yazdırılır, karara girmez. Bu sütun 73 W darbesinin son 2 ms'sindeki toplam tepe-tepe değerdir (yavaş LC salınımı + anahtarlama ripple'ı).
- Seri direnç (DCR + D·Ron + (1−D)·Rd) 25,9 mΩ'dan (hedef değerler) 21,4 mΩ'a (Würth DCR) ve ≈ 14,8 mΩ'a (el sarım DCR) düştü: **daha düşük Ron / Vf / DCR kaybı azaltır ama sönümü de azaltır.**

Kullanıcı kararı (12.11.2026): L1 için **1. sıra el sarım 33 µH** (Kool Mµ 40µ, 22 sarım; DCR 7,81 mΩ nominal @20 °C, 9,5 mΩ sıcak köşe, 6,5 mΩ denenen en düşük sönüm köşesi; doğrulanmış DCR sınırı 6,5–15 mΩ, hedef 8–10 mΩ), **2. sıra satın alma**. 47 µH el sarım elendi (12,61 V). 47 µH yalnız satın alınan parçayla ve S2E kalkış süresi ölçüldükten sonra değerlendirilir. Ölçülebilir parça kriterleri: [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md).

## 5. Şematik değerleriyle test sonuçları (SİM)

1. sıra değerler ([PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md)): L 33 µH / 7,81 mΩ (el sarım, HESAP) · Cout 1000 µF / 35 mΩ (maks. empedans, ESR varsayımı) · Cin 2 × 1000 µF / 15 mΩ · Ron 5,6 mΩ · Vf 0,38 V + 8 mΩ · 100 kHz. Tablolar `python buck/dogrula.py secilen` çıktısıdır (12.11.2026).

### 5.1 Kararlı durum, 7,5 A direnç yük, Ton her girişte 11 V'a ayarlı (ideal regülasyon varsayımı)

| Vin V | Ton µs | Vo V | ΔVo mV | IL A | S1 rms A | D1 ort A | Cout rms A | P S1 W | P D1 W | P L1 W | P toplam W | η iletim % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 5.627 | 11.000 | 52.6 | 6.74–8.26 | 5.64 | 3.27 | 0.43 | 0.18 | 1.44 | 0.44 | 2.07 | 97.56 |
| 22.2 | 5.078 | 10.999 | 59.2 | 6.64–8.36 | 5.36 | 3.68 | 0.48 | 0.16 | 1.62 | 0.44 | 2.23 | 97.37 |
| 24.6 | 4.589 | 11.000 | 70.3 | 6.56–8.46 | 5.10 | 4.05 | 0.53 | 0.15 | 1.78 | 0.44 | 2.38 | 97.19 |
| 25.2 | 4.481 | 11.000 | 71.8 | 6.54–8.48 | 5.04 | 4.13 | 0.54 | 0.14 | 1.82 | 0.44 | 2.42 | 97.16 |
| 26 | 4.345 | 10.999 | 68.0 | 6.51–8.48 | 4.96 | 4.23 | 0.55 | 0.14 | 1.86 | 0.44 | 2.45 | 97.11 |

Verim yalnız iletim kaybıdır; anahtarlama, çekirdek ve sürücü kayıpları **modelde yoktur**, gerçek verim daha düşük olacaktır. Ton ayar doğruluğu ±5 mV; ripple 1 ms pencerede t-t.

![Kararlı durum](grafik/kararli.svg)

### 5.2 Kararlı durum, gerçek yük senaryoları, 24,6 V, Ton 11 V'a ayarlı (sabit güç yükü)

| Senaryo | P W | I@11V A | Ton µs | Kip | Vo V | ΔVo mV | IL tepe A | η iletim % |
|---|---|---|---|---|---|---|---|---|
| yalnız S2E çalışma | 2.64 | 0.24 | 2.299 | DCM | 11.007 | 34.3 | 0.95 | 98.0 |
| yalnız O1 boşta (tahmin) | 4.00 | 0.36 | 2.830 | DCM | 11.004 | 41.7 | 1.17 | 97.9 |
| yalnız O1 tipik (tahmin) | 10.00 | 0.91 | 4.474 | DCM | 11.002 | 66.7 | 1.85 | 97.9 |
| O1 boşta + S2E | 6.64 | 0.60 | 3.646 | DCM | 10.993 | 54.0 | 1.51 | 97.9 |
| O1 tipik + S2E | 12.64 | 1.15 | 4.552 | CCM | 10.999 | 66.8 | 2.09 | 97.9 |
| O1 tipik + S2E kalkış | 28.00 | 2.55 | 4.560 | CCM | 11.000 | 73.1 | 3.51 | 97.8 |
| yalnız O1 zarf 5 A | 55.00 | 5.00 | 4.577 | CCM | 11.000 | 73.9 | 5.96 | 97.5 |
| O1 zarf + S2E | 57.64 | 5.24 | 4.577 | CCM | 11.000 | 67.8 | 6.18 | 97.5 |
| O1 zarf + S2E kalkış | 73.00 | 6.64 | 4.586 | CCM | 11.002 | 68.6 | 7.58 | 97.3 |

Ripple her senaryoda S2E sınırının (±330 mV) çok altında. DCM'de gereken Ton yükle 2,3–4,5 µs arasında değişir: geri besleme bu aralığı kapsamalıdır.

### 5.3 Açık çevrim: Ton sabit (24,6 V / 7,5 A'ya ayarlı), giriş ve yük değişince kararlı çıkış [V]

| Vin V \ yük A@11V | 0.24 | 0.6 | 1.15 | 2.5 | 5.24 | 7.5 |
|---|---|---|---|---|---|---|
| 20 | 13.62 | 10.48 | 8.98 | 8.96 | 8.94 | 8.90 |
| 22.2 | 15.12 | 11.64 | 9.99 | 9.97 | 9.94 | 9.91 |
| 24.6 | 16.76 | 12.90 | 11.09 | 11.07 | 11.04 | 11.00 |
| 25.2 | 17.17 | 13.22 | 11.37 | 11.35 | 11.31 | 11.27 |
| 26 | 17.71 | 13.64 | 11.73 | 11.71 | 11.68 | 11.64 |

O1'in 5–12 V aralığı yalnız 24,6 V civarında ve yük CCM'deyken sağlanır. **Açık çevrim O1 için hiçbir L/C değeriyle güvenli değildir.**

### 5.4 Yük adımları, 24,6 V, Ton sabit (kontrolcü tepki vermiyor = kötümser sınır)

| Adım | P W | Vmin V | Vmax V | ara kararlı V | ara salınım mV | son kararlı V | son salınım mV | IL tepe A |
|---|---|---|---|---|---|---|---|---|
| S2E kalkışı, O1 tipik | 12.6→28.0 | 10.59 | 11.11 | 10.84 | 66 | 10.86 | 66 | 4.5 |
| O1 tipik→zarf→tipik, S2E çalışıyor | 12.6→57.6 | 10.09 | 11.52 | 10.80 | 67 | 10.86 | 66 | 9.5 |
| S2E kalkışı, O1 zarf | 57.6→73.0 | 10.69 | 11.26 | 10.98 | 68 | 11.00 | 67 | 8.8 |
| O1 zarf→boşta→zarf, S2E çalışıyor | 57.6→6.6 | 10.29 | 14.66 | 14.55 | 205 | 11.00 | 67 | 9.4 |

İlk üç adımda çıkış kontrolcü olmadan bile 9–12 V içinde kalır. Son satır DCM yükselmesidir (§5.3) ve yalnız geri beslemeyle giderilir.

![Yük adımı](grafik/yuk_adimi.svg)

### 5.5 Yük atma, ideal kontrolcü sınırı (yük düştüğü anda duty = 0; en iyi durum)

| Vin V | 73→6,6 W Vtepe V | 82,5→2,6 W Vtepe V |
|---|---|---|
| 20 | 11.223 | 11.267 |
| 22.2 | 11.226 | 11.269 |
| 24.6 | 11.228 | 11.272 |
| 25.2 | 11.228 | 11.272 |
| 26 | 11.229 | 11.273 |

Bobindeki enerji Cout'a boşaldığında oluşan tepe budur; 12 V'a kalan pay kontrol tasarımının bütçesidir. Gerçek kapalı çevrim, tepki gecikmesi kadar bunun üstüne çıkar.

### 5.6 Soğuk kalkış

| Vin V | Yük | sert: IL tepe A | sert: Vo tepe V | 5 ms duty rampası: IL tepe A | 5 ms duty rampası: Vo tepe V |
|---|---|---|---|---|---|
| 20 | 7,5 A direnç | 53.2 | 17.01 | 10.5 | 11.29 |
| 22.2 | 7,5 A direnç | 53.3 | 17.01 | 10.5 | 11.29 |
| 24.6 | 7,5 A direnç | 53.3 | 17.00 | 10.6 | 11.29 |
| 25.2 | 7,5 A direnç | 53.3 | 17.00 | 10.7 | 11.29 |
| 26 | 7,5 A direnç | 53.4 | 17.00 | 10.7 | 11.29 |
| 24.6 | O1 tipik + S2E (12,6 W) | 54.2 | 18.58 | 6.4 | 11.20 |

Sert kalkış aşımı O1'in TVS çalışma gerilimini (16 V, ÇIKARIM) ve TPS62180 mutlak sınırını (17 V) zorlar. Model bobini doğrusal alır; gerçek bobin bu akımda doyacağından tepe akım daha yüksek olur. Duty rampası bir **varsayımdır** (soft-start devresi tasarlanmadı); yalnız aşımın kaynağının basamak uyarımı olduğunu ve yumuşak kalkışla giderildiğini gösterir.

![Kalkış](grafik/kalkis.svg)

### 5.7 Giriş değişimi, Ton sabit, O1 zarf + S2E (57,6 W)

| Vin V (1 ms rampa) | Vmin V | Vmax V | ara kararlı V |
|---|---|---|---|
| 24.6→20→24.6 | 8.57 | 11.27 | 8.87 |
| 24.6→26→24.6 | 10.89 | 11.75 | 11.65 |
| 22.2→25.2→22.2 | 10.78 | 12.74 | 12.53 |

Çıkış girişi oransal izler (ΔVo ≈ D·ΔVin). 20 V'ta S2E'nin 9 V alt sınırının altına, batarya dolarken O1'in 12 V sınırının üstüne çıkar. L/Cout ile düzelmez (§4.3).

### 5.8 Tolerans köşeleri (L −%30/+%20, Cout ±%20, ESR 15/35 mΩ), 7,5 A

| Köşe | Vin V | ΔVo mV | IL tepe A | zarf adım Vmin/Vmax | 73 W salınım mV | yük atma sınırı V | sert kalkış A/V | rampalı kalkış A/V |
|---|---|---|---|---|---|---|---|---|
| anma | 24.6 | 70.3 | 8.46 | 10.69/11.26 | 68 | 11.23 | 53.3/17.0 | 10.6/11.29 |
| ripple en kötü: L−, C−, ESR 35 mΩ | 26 | 103.6 | 8.93 | 10.71/11.26 | 101 | 11.24 | 56.6/16.9 | 10.7/11.24 |
| sönüm en zayıf: L+, C−, ESR 15 mΩ | 24.6 | 29.5 | 8.31 | 10.48/11.48 | 1002 | 11.11 | 47.7/18.1 | 10.0/11.30 |
| Z0 en düşük: L−, C+, ESR 15 mΩ | 26 | 48.7 | 8.94 | 10.79/11.19 | 43 | 11.12 | 71.6/17.8 | 11.6/11.28 |

L −%30, −%20 toleransı ve tepe akımdaki endüktans düşümünü birlikte kapsar. ESR köşeleri kabul penceresinin kenarlarıdır (15 / 35 mΩ); seçilen kondansatörün veri sayfası değeri 35 mΩ'dur. Dört köşede de S2E kalkış darbesinde çıkış 9–12 V içindedir. Sönüm en zayıf köşede 73 W salınımı 1002 mV'a çıkar (12 V'a pay 0,52 V); DCR bu köşenin ana değişkenidir.

### 5.9 Giriş tarafı, batarya+kablo modeli (VARSAYIM 40 mΩ + 1 µH/10 mΩ), 7,5 A

| Batarya V | Vo V | ΔVin mV t-t | Cin toplam rms A | Cin ESR kaybı W |
|---|---|---|---|---|
| 20 | 11.000 | 70 | 3.73 | 0.10 |
| 24.6 | 11.000 | 72 | 3.76 | 0.11 |
| 26 | 11.000 | 72 | 3.74 | 0.10 |

Batarya 26 V sıcak takma (anahtar kapalı): V(vin) tepe 26.0 V, batarya akımı tepe 359 A

Değerler tahmini kaynak empedansına bağlıdır. İki TDK kondansatörün toplam ripple akımı anma değeri 6,5 A'dir.

## 6. Doğrulanamayanlar ve sonraki aşamaya kalanlar

**Geri besleme aşamasının çözmesi gerekenler (bu güç katıyla çözülemez):**
- Regülasyon: giriş 20–26 V ve yük 0,24–7,5 A aralığında 11 V; Ton 2,3–5,7 µs; DCM/CCM geçişi 0,95 A'de.
- Yumuşak kalkış: sert kalkış 53 A / 17 V (hafif yükte daha yüksek; L1 12,5 A'de doyar, gerçek tepe daha yüksek olur); birkaç ms'lik rampa 10–11 A / 11,3 V'a indirir.
- Yük atma bütçesi: ideal kontrolcü sınırı §5.5'te; 12 V'a kalan pay kontrol gecikmesine ve ayar toleransına paylaştırılacak.
- Tasarım verileri: f0 = 0,88 kHz, Z0 = 0,18 Ω, ESR sıfırı 4,5–10,6 kHz (ESR 35–15 mΩ); yük sabit güç karakterli (negatif artımsal direnç, zarfta −2,1 Ω).
- Anahtar kısa devre kalırsa çıkış giriş gerilimine çıkar; O1 için bağımsız aşırı gerilim koruması ayrı bir konudur.

**Doğrulanmamış veriler:**
- O1'in gerçek tüketimi, kalkış akımı, mutlak maksimum gerilimi ve ripple toleransı yayımlanmamış; 4 / 10 W değerleri tahmindir. Ölçülmeli veya üreticiden istenmelidir.
- O1 giriş koruması (eFuse OVLO ≈ 14,7 V, TVS, TPS62180) v0.2 şemasının metin katmanından çıkarıldı; devre bağlantıları görülerek doğrulanmadı, eldeki kart revizyonu farklı olabilir. 12 V üstü için dayanım varsayılmamalıdır.
- S2E kalkış darbesinin süresi ve 11 V'taki değeri (datasheet 12 V verir); testlerde sabit güç varsayıldı.
- Batarya iç direnci ve kablo endüktansı tahmindir.
- Parçalar kesinleşmedi. Würth, Nichicon ve TDK değerleri üretici PDF'inden okundu (12.11.2026); ST (STP100N6F7 Rev 2, STPS40M60C Rev 1) değerleri ayrı bir araştırma raporundan alındı, PDF'ler bu ortamda açılamadı. Nichicon 35 / 120 mΩ ve TDK 15 / 38 mΩ **en büyük empedanstır**, ESR değildir; üretici ESR yayımlamaz. Cout'un gerçek ESR'si ve sıcaklık davranışı ölçülmelidir.
- **Soğuk köşe (SİM, üst sınır varsayımı):** −10 °C'ta Zmax'ın tamamı ESR sayılırsa (Cout 120 mΩ, Cin 38 mΩ) köşe (26 V, L −%30, Cout −%20) çıkış ripple'ı 318 mV t-t olur (20 °C modelinde 104 mV); 165 mV ölçütü bu varsayımda **sağlanmaz**. Yük adımları 9–12 V içinde kalır (S2E kalkışı 10,61–11,35 V, O1 10,07–11,77 V). Gerçek ESR Zmax'tan düşüktür; kesin sayı ölçüm gerektirir. Kabul ölçütü değiştirilmedi.
- D1 (ST formülü VT0 0,395 V, RD 7 mΩ/diyot, iki diyot paralel): 24,6 V'ta HESAP 1,75 W (25 °C tipik); repo modeli 1,82 W; 125 °C tipik ≈ 1,29 W; 25 °C azami eğrisi ≈ 1,86 W. Repo modeli 25 °C tipikten ≈ 19 mV kötümser, azamiden ≈ 9 mV iyimserdir; azami VF garantisi değildir. Akım paylaşımı modelde yok.
- S1 (HESAP): 24,6 V'ta iletim 0,14 W (25 °C), ≈ 0,20 W (100 °C, RDS(on) eğrisi ≈ ×1,40, yaklaşık). Anahtarlama kaybı ST'nin 50 A/4,7 Ω koşullu geçiş sürelerinden üst sınır TAHMİN ≈ 0,65 W; gerçek değer 7,5 A ve sürücüye bağlıdır, Adım 3–4'te ele alınır.
- L1 sıcak DCR (HESAP, bakır 0,39 %/K varsayımı): 100 °C'ta 17,3 mΩ nominal, 19,1 mΩ azami; "DCR ≤ 15 mΩ" ölçütü 20 °C içindir.
- L1 el sarım (1. sıra kararı, 12.11.2026): Kool Mµ 40µ, 22 sarım, DCR 6,5 / 7,81 / 9,5 mΩ ile köşe testi geçti (salınım 1,6 / 1,1 / 0,74 V; Würth 14,5 mΩ'ta 0,22 V); 47 µH el sarım 12,61 V ile kaldı. Ayrıntı: [PARCA-HEDEFLERI.md](PARCA-HEDEFLERI.md). Fiziksel L(I), DCR ve sıcaklık ölçümü yok.
- `ton_ayarla()` yakınsama uyarısı eklendi: 20 V / 7,5 A'de kalan hata 155 mA; yük adımı yardımcılarında DCM'de 22–106 mA uyarısı görülüyor. Sonuçlar değişmedi, yakınsama iyileştirmesi ayrı iştir.

**İdeal modelin kapsamadıkları:** anahtarlama kayıpları ve geçiş süreleri, diyot ters toparlanma/kapasitesi, bobin doyumu ve çekirdek kaybı, kondansatör ESL'i ve kapasitenin gerilim/sıcaklıkla değişimi, parazitik zil, ısıl davranış, EMI. Verim ve tepe gerilim/akım değerleri bu etkiler olmadan verilmiştir.

## 7. Tekrar üretme

```
python buck/hesap.py            # analitik özet
python buck/dogrula.py secilen  # §5 tabloları (≈ 15 dk)
python buck/dogrula.py pencere  # §4.4 son pencere (≈ 12 dk)
python buck/dogrula.py tarama   # §4.1 taraması (≈ 15 dk)
python buck/dogrula.py mevcut   # en baştaki eski değerlerle aynı testler
python buck/dogrula.py grafik   # buck/grafik/*.svg
```

LTspice yolu farklıysa `LTSPICE` ortam değişkeniyle verilir. Test netlistleri geçici klasörde üretilir; ana şematiğe `.meas`, `.param` veya yük modeli eklenmez. §4.2, §4.3 ve §4.4'ün ilk tablosu tek seferlik koşulardır; aynı fonksiyonlarla (`yuk_adimi`, `giris_adimi`, `pencere`) farklı `CIFTLER` / ESR değerleri verilerek tekrarlanır.
