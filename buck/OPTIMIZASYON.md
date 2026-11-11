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

## 5. Seçilen tasarımın test sonuçları (SİM)

L 33 µH / 15 mΩ · Cout 680 µF / 25 mΩ · Cin 2 × 220 µF / 20 mΩ · Ron 10 mΩ · Vf 0,5 V + 10 mΩ · 100 kHz. Ton ayar doğruluğu ±5 mV; ripple 1 ms pencerede t-t.

### 5.1 Beş girişte kararlı durum, 7,5 A (Ton her girişte 11 V'a ayarlı = ideal regülasyon varsayımı)

| Vin V | Ton µs | Vo V | ΔVo mV | IL A | S1 rms A | D1 ort A | Cout rms A | P S1 W | P D1 W | P L1 W | Toplam W | η iletim % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 5,691 | 10,999 | 38,2 | 6,74–8,26 | 5,67 | 3,22 | 0,43 | 0,32 | 1,85 | 0,85 | 3,03 | 96,46 |
| 22,2 | 5,138 | 10,999 | 43,1 | 6,64–8,36 | 5,39 | 3,64 | 0,49 | 0,29 | 2,09 | 0,85 | 3,24 | 96,22 |
| **24,6** | 4,646 | 11,000 | 47,4 | 6,55–8,45 | 5,13 | 4,01 | 0,54 | 0,26 | 2,31 | 0,85 | 3,42 | 96,01 |
| 25,2 | 4,539 | 10,999 | 54,5 | 6,53–8,48 | 5,07 | 4,09 | 0,55 | 0,26 | 2,35 | 0,85 | 3,47 | 95,96 |
| 26 | 4,400 | 11,002 | 55,9 | 6,51–8,51 | 5,00 | 4,19 | 0,56 | 0,25 | 2,41 | 0,85 | 3,52 | 95,91 |

HESAP ile fark: Ton ≤ %0,3, ΔIL ≤ %1. Verim yalnız iletim kaybıdır; anahtarlama, çekirdek ve sürücü kayıpları **modelde yoktur**, gerçek verim daha düşük olacaktır.

![Kararlı durum](grafik/kararli.svg)

### 5.2 Gerçek yük senaryoları, 24,6 V (Ton 11 V'a ayarlı, sabit güç yükü)

| Senaryo | P W | I@11 V A | Ton µs | Kip | Vo V | ΔVo mV | IL tepe A |
|---|---|---|---|---|---|---|---|
| yalnız S2E çalışma | 2,64 | 0,24 | 2,305 | DCM | 11,003 | 24,7 | 0,95 |
| yalnız O1 boşta (TAHMİN) | 4,00 | 0,36 | 2,838 | DCM | 11,001 | 30,4 | 1,17 |
| yalnız O1 tipik (TAHMİN) | 10,00 | 0,91 | 4,495 | DCM | 11,018 | 48,5 | 1,85 |
| O1 boşta + S2E | 6,64 | 0,60 | 3,656 | DCM | 10,981 | 39,7 | 1,51 |
| O1 tipik + S2E | 12,64 | 1,15 | 4,583 | CCM | 11,000 | 48,3 | 2,09 |
| O1 tipik + S2E kalkış | 28,00 | 2,55 | 4,597 | CCM | 11,000 | 48,5 | 3,49 |
| yalnız O1 zarf | 55,00 | 5,00 | 4,621 | CCM | 11,001 | 56,2 | 5,96 |
| O1 zarf + S2E | 57,64 | 5,24 | 4,624 | CCM | 11,001 | 49,3 | 6,19 |
| O1 zarf + S2E kalkış | 73,00 | 6,64 | 4,638 | CCM | 11,000 | 51,6 | 7,59 |

Ripple her senaryoda S2E sınırının (±330 mV) çok altında. DCM'de gereken Ton yükle 2,3–4,5 µs arasında değişir: geri besleme bu aralığı kapsamalıdır.

### 5.3 Açık çevrim: Ton sabit (4,646 µs), kararlı çıkış [V]

| Vin V \ yük A | 0,24 | 0,6 | 1,15 | 2,5 | 5,24 | 7,5 |
|---|---|---|---|---|---|---|
| 20 | 13,69 | 10,54 | 9,02 | 8,99 | 8,94 | 8,89 |
| 22,2 | 15,20 | 11,71 | 10,04 | 10,01 | 9,95 | 9,90 |
| 24,6 | 16,85 | 12,98 | 11,15 | 11,12 | 11,06 | 11,00 |
| 25,2 | 17,26 | 13,30 | 11,43 | 11,40 | 11,33 | 11,27 |
| 26 | 17,81 | 13,72 | 11,80 | 11,77 | 11,70 | 11,64 |

O1'in 5–12 V aralığı yalnız 24,6 V civarında ve yük CCM'deyken sağlanır. **Açık çevrim O1 için hiçbir L/C değeriyle güvenli değildir.**

### 5.4 Yük adımları, 24,6 V, Ton sabit (kontrolcü tepki vermiyor: kötümser sınır)

| Adım | P W | Vmin V | Vmax V | Adım sırasında kararlı V | Salınım mV | IL tepe A |
|---|---|---|---|---|---|---|
| S2E kalkışı, O1 tipik | 12,6→28,0→12,6 | 10,67 | 11,29 | 10,96 | 48 | 4,6 |
| O1 tipik→zarf→tipik | 12,6→57,6→12,6 | 10,04 | 11,80 | 10,90 | 49 | 9,7 |
| S2E kalkışı, O1 zarf | 57,6→73,0→57,6 | 10,65 | 11,31 | 10,97 | 50 | 8,8 |
| O1 zarf→boşta→zarf | 57,6→6,6→57,6 | 10,11 | **15,35** | 15,27 | 171 | 9,8 |

İlk üç adımda çıkış kontrolcü olmadan bile 10,0–11,8 V içinde kalır. Son satır DCM yükselmesidir (§5.3) ve yalnız geri beslemeyle giderilir.

![Yük adımı](grafik/yuk_adimi.svg)

### 5.5 Yük atma, ideal kontrolcü sınırı (yük düştüğü anda duty = 0; en iyi durum)

| Vin V | 73 → 6,6 W | 82,5 → 2,6 W |
|---|---|---|
| 20 | 11,17 V | 11,21 V |
| 24,6 | 11,18 V | 11,22 V |
| 26 | 11,18 V | 11,22 V |

Bobindeki enerji Cout'a boşaldığında tepe en çok 11,22 V'tur; 12 V'a 0,78 V pay kalır. Gerçek kapalı çevrim, tepki gecikmesi kadar bunun üstüne çıkar; bu pay kontrol tasarımının bütçesidir.

### 5.6 Soğuk kalkış

| Vin V | Yük | Sert: IL tepe / Vo tepe | 5 ms duty rampası: IL tepe / Vo tepe |
|---|---|---|---|
| 20 | 7,5 A direnç | 45,6 A / 17,12 V | 9,8 A / 11,23 V |
| 22,2 | 7,5 A direnç | 45,7 A / 17,12 V | 9,8 A / 11,23 V |
| 24,6 | 7,5 A direnç | 45,8 A / 17,12 V | 9,9 A / 11,23 V |
| 25,2 | 7,5 A direnç | 45,8 A / 17,13 V | 10,0 A / 11,24 V |
| 26 | 7,5 A direnç | 45,8 A / 17,12 V | 10,0 A / 11,24 V |
| 24,6 | O1 tipik + S2E (12,6 W) | 47,7 A / 19,45 V | 5,3 A / 11,27 V |

Sert kalkış aşımı O1'in TVS çalışma gerilimini (16 V, ÇIKARIM) ve TPS62180 mutlak sınırını (17 V) aşar. Duty rampası bir **varsayımdır** (soft-start devresi tasarlanmadı); yalnız aşımın kaynağının basamak uyarımı olduğunu ve yumuşak kalkışla giderildiğini gösterir.

![Kalkış](grafik/kalkis.svg)

### 5.7 Giriş değişimi, Ton sabit, 57,6 W

| Vin V (1 ms rampa) | Vmin V | Vmax V | Ara kararlı V |
|---|---|---|---|
| 24,6 → 20 → 24,6 | 8,68 | 11,15 | 8,84 |
| 24,6 → 26 → 24,6 | 10,94 | 11,71 | 11,66 |
| 22,2 → 25,2 → 22,2 | 10,88 | **12,66** | 12,55 |

Çıkış girişi oransal izler (ΔVo ≈ D·ΔVin). 20 V'ta S2E'nin 9 V alt sınırının altına, batarya dolarken O1'in 12 V sınırının üstüne çıkar.

### 5.8 Tolerans köşeleri (L ±%20, Cout ±%20, ESR ±%20), 7,5 A

| Köşe | Vin V | ΔVo mV | IL tepe A | S2E kalkışı @zarf Vmin/Vmax | 73 W salınım mV | Yük atma sınırı V | Sert kalkış A / V | Rampalı kalkış A / V |
|---|---|---|---|---|---|---|---|---|
| anma | 24,6 | 47,4 | 8,45 | 10,65/11,31 | 50 | 11,18 | 45,8 / 17,1 | 9,9 / 11,23 |
| L−, C−, ESR+ | 26 | 73,9 | 8,74 | 10,64/11,32 | 76 | 11,22 | 45,5 / 16,9 | 9,9 / 11,19 |
| L+, C−, ESR− | 24,6 | 38,1 | 8,31 | 10,30/11,74 | 881 | 11,17 | 39,2 / 17,4 | 9,5 / 11,22 |
| L−, C+, ESR− | 26 | 56,2 | 8,76 | 10,71/11,25 | 50 | 11,14 | 54,8 / 17,2 | 10,5 / 11,23 |

En zayıf köşe L+, C−, ESR−: 73 W darbesinde 0,9 V t-t salınım var ama çıkış 12 V altında; sürekli zarfta (57,6 W) 171 mV. HESAP sınırı bu köşede 75 W.

### 5.9 Giriş tarafı (batarya 40 mΩ + kablo 1 µH / 10 mΩ — TAHMİN), 7,5 A

| Batarya V | ΔVin mV t-t | Cin toplam rms A | Cin ESR kaybı W |
|---|---|---|---|
| 20 | 122 | 3,73 | 0,14 |
| 24,6 | 125 | 3,77 | 0,14 |
| 26 | 125 | 3,76 | 0,14 |

26 V bataryanın sıcak takılması (anahtar kapalı): V(vin) tepe 28,1 V, batarya akımı tepe 265 A. Değerler tahmini kaynak empedansına bağlıdır.

## 6. Doğrulanamayanlar ve sonraki aşamaya kalanlar

**Geri besleme aşamasının çözmesi gerekenler (bu güç katıyla çözülemez):**
- Regülasyon: giriş 20–26 V ve yük 0,24–7,5 A aralığında 11 V; Ton 2,3–5,7 µs; DCM/CCM geçişi 0,95 A'de.
- Yumuşak kalkış: sert kalkış 46 A / 17–19 V; birkaç ms'lik rampa 10 A / 11,3 V'a indirir.
- Yük atma bütçesi: ideal sınır 11,22 V; 12 V'a kalan 0,78 V kontrol gecikmesine ve ayar toleransına paylaştırılacak.
- Tasarım verileri: f0 = 1,06 kHz, Z0 = 0,22 Ω, ESR sıfırı 9,4 kHz; yük sabit güç karakterli (negatif artımsal direnç, zarfta −2,1 Ω).
- Anahtar kısa devre kalırsa çıkış giriş gerilimine çıkar; O1 için bağımsız aşırı gerilim koruması ayrı bir konudur.

**Doğrulanmamış veriler:**
- O1'in gerçek tüketimi, kalkış akımı, mutlak maksimum gerilimi ve ripple toleransı yayımlanmamış; 4 / 10 W değerleri tahmindir. Ölçülmeli veya üreticiden istenmelidir.
- O1 giriş koruması (eFuse OVLO ≈ 14,7 V, TVS, TPS62180) v0.2 şemasının metin katmanından çıkarıldı; devre bağlantıları görülerek doğrulanmadı, eldeki kart revizyonu farklı olabilir. 12 V üstü için dayanım varsayılmamalıdır.
- S2E kalkış darbesinin süresi ve 11 V'taki değeri (datasheet 12 V verir); testlerde sabit güç varsayıldı.
- Batarya iç direnci ve kablo endüktansı tahmindir.

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
