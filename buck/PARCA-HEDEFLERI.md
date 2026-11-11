# Seçilen Parçalar — Ana Güç Devresi

**Tarih:** 11 Kasım 2026
**Sınıf:** veri sayfası değerleri + LTspice (ideal elemanlar). Fiziksel ölçüm yok. Stok ve fiyatlar 11 Kasım 2026 sayfa görüntüleridir; **sipariş öncesi yeniden bakılmalıdır**.

Çalışma noktası: Vin 20 / 22,2 / **24,6** / 25,2 / 26 V → 11 V / 7,5 A (82,5 W), fsw = 100 kHz. Hedef değerlerin gerekçesi: [OPTIMIZASYON.md](OPTIMIZASYON.md).

## Parça listesi

| Eleman | Parça | Veri sayfası değeri (şematikte) | Devredeki zorlanma → pay | Bulunurluk |
|---|---|---|---|---|
| **S1** | STMicroelectronics **STP75NF75**, N-MOSFET, TO-220 | 75 V, 80 A, RDS(on) 9,5 mΩ tipik / **11 mΩ** maks (`Ron=11m`); Qg 117 nC, Qgd 47 nC, VGS(th) 2–4 V | 26 V (takma anında 28 V) → 2,7×; 5,7 A RMS | Özdisan: 5.340 stok, 52,69 TL + KDV |
| **D1** | IXYS/Littelfuse **DSB60C60HB**, çift Schottky, TO-247, iki bacak paralel | 60 V, 2 × 30 A; bacak başına VF0 0,46 V + 6,2 mΩ (150 °C) → paralel **0,46 V + 3,1 mΩ** (`Vf=0.46 Ron=3.1m`); 30 A'de 0,77 V (25 °C) / 0,67 V (125 °C) | 26 V → 2,3×; 4,2 A ortalama | Özdisan: 7.496 stok, 117,88 TL + KDV |
| **L1** | Bourns **2300HT-330-V-RC** (dikey) veya **-H-RC** (yatay), toroid, THT | **33 µH** ±%15 (0 A, 1 kHz); 13,6 A'de 23,0 µH; Idc 13,6 A (50 °C ısınma); DCR **15 mΩ** maks | 8,5 A tepe, 7,5 A RMS → 1,6× | Türkiye'de stok **bulunamadı**; Digi-Key / Mouser / Farnell (stok bu oturumda doğrulanamadı) |
| **Cout** | Rubycon **25ZLH680MEFC10X16**, 680 µF / 25 V, 10 × 16 mm | 100 kHz empedans **28 mΩ** maks (`Rser=28m`); ripple akımı 1,76 A; 105 °C, 10.000 saat | 11 V (sert kalkışta 17 V) ; 0,54 A RMS → 3,3× | Farnell: 671 stok (arama görüntüsü); Özdisan'da yok |
| **Cin1, Cin2** | 2 × Panasonic **EEUFR1V681B**, 680 µF / 35 V, 10 × 20 mm | 100 kHz empedans **20 mΩ** maks/adet (`Rser=20m`); ripple akımı 2,18 A/adet; 105 °C, 10.000 saat | 26 V (takmada 28 V) → 1,25×; toplam 3,77 A RMS / 4,36 A → 1,16× | Özdisan: listede 29,08 TL + KDV, **stok 0**, 22–23 hafta; Digi-Key / Mouser |
| **Rload** | 1,47 Ω, ≥ 100 W direnç bankası veya elektronik yük | 1,4667 Ω | 82,5 W sürekli | — |

Stoku doğrulanan iki parça (S1, D1) Türkiye'den aynı gün çıkar. L1 ve kondansatörler için yurt dışı dağıtıcı gerekir; aşağıdaki yedekler aynı hedefleri tutar.

## Yedekler

| Eleman | Yedek | Fark |
|---|---|---|
| S1 | IRF1010EPBF (60 V, 12 mΩ; Özdisan 685 stok) | Gerilim payı 2,1×; iletim kaybı +%9 |
| S1 | IRFZ44NPBF (55 V, 17,5 mΩ; Özdisan 6.658 stok, 10,21 TL + KDV) | İletim kaybı +%60 (≈ +0,17 W); kapı yükü yarı yarıya (Qg 63 nC), sürmesi kolay |
| D1 | DSB60C60PB (aynı çip, TO-220; Direnc.net'te listeli) | Isıl direnç daha yüksek |
| L1 | Bourns 2300HT-390 (39 µH, 13 A'de 26,7 µH, 17 mΩ) | Yük altında ≈ 32 µH; hafif yükte Z0 %9 yüksek |
| Cout | Panasonic EEUFR1E681L (680 µF / 25 V, 30 mΩ, 1,56 A) | Eşdeğer |
| Cout | Panasonic EEUFM1E681 (680 µF / 25 V, 19 mΩ, 2,18 A) | ESR pencerenin alt kenarında; sönüm payı azalır |
| Cin | Aynı seriden 3 adet | Ripple akımı payı 1,16× → 1,7× |

Çok düşük ESR'li (5–10 mΩ) polimer kondansatör Cout için **hedefi tutmaz**: LC sönümü zayıflar ([OPTIMIZASYON.md](OPTIMIZASYON.md) §4).

## Sonraki aşamalar için notlar

- **Kapı sürücüsü:** S1 üst taraftaki N-MOSFET'tir; kapısı anahtar düğümünün 10–12 V üstüne sürülmelidir (bootstrap'lı üst taraf sürücüsü). VGS(th) 2–4 V olduğundan lojik seviyeyle sürülmez. Qg 117 nC → 100 kHz ve 12 V'ta sürücü gücü ≈ 0,14 W; 50 ns altı geçiş için ≥ 1 A tepe akımlı sürücü gerekir. Sürücü zayıfsa IRFZ44N (Qg 63 nC) daha uygundur.
- **Kontrol:** Ton aralığı 2,3–5,7 µs (yük 0,24–7,5 A, giriş 20–26 V); DCM/CCM geçişi ≈ 0,95 A; f0 ≈ 1,06 kHz, ESR sıfırı ≈ 8,4 kHz. Yumuşak kalkış zorunlu (sert kalkış 46 A / 17 V; L1 bu akımda doyar, gerçek tepe daha yüksek olur).
- **Isı:** D1 ≈ 1,9 W (iletim, HESAP); S1 0,3 W iletim + anahtarlama kaybı (modelde yok). İkisi de soğutucu ister; TO-247 ve TO-220 aynı soğutucuya bağlanabilir (yalıtım pedi ile: D1 gövdesi katot, S1 gövdesi drain).
- **L1:** Demir tozu toroid; endüktans akımla düşer (7,5 A'de ≈ 27 µH, doğrusal ara değer **varsayımı**) ve 100 kHz çekirdek kaybı veri sayfasında yoktur. Tolerans köşeleri L −%30 / +%15 ile koşuldu. Tezgâhta sıcaklığı ölçülmelidir.
- **Akım ölçümü:** Bu aşamada yok. Koruma/kontrol için şönt veya bobin DCR'si üzerinden ölçüm sonraki aşamada eklenir.
- **Montaj:** Tüm parçalar delikli (THT) seçildi; delikli pertinaks veya tek katlı kartta el lehimine uygundur. Anahtarlama çevrimi (Cin → S1 → D1 → Cin) kısa tutulmalıdır.

## Notlar

- Şematik, `hesap.py` ve `dogrula.py` bu tablodaki değerleri kullanır. Parça değişirse üçü birlikte güncellenip `python buck/dogrula.py secilen` yeniden koşulur.
- Kaynaklar: [Bourns 2300HT](https://www.bourns.com/docs/Product-Datasheets/2300ht_series.pdf) · [IXYS DSB60C60HB](https://pdf.direnc.net/upload/dsb60c60hb-2x30a-60v-schottky-diyot-datasheet.pdf) (2013 ön sürüm) · [STP75NF75](https://www.ame.cz/STP75NF75-a2539231.pdf) · [Özdisan STP75NF75](https://www.ozdisan.com/en/p/discrete-mosfets-435/stm-stp75nf75-33966) · [Özdisan DSB60C60HB](https://www.ozdisan.com/en/p/Schottky-Diodes-385/ixys-dsb60c60hb-352439) · [Özdisan EEUFR1V681B](https://www.ozdisan.com/pasif-komponentler/kapasitorler/aluminyum-kapasitorler/EEUFR1V681B/1094372) · [Digi-Key 25ZLH680MEFC10X16](https://www.digikey.fi/en/products/detail/rubycon/25ZLH680MEFC10X16/3563722) · [Farnell 25ZLH680MEFC10X16](https://pl.farnell.com/en-PL/rubycon/25zlh680mefc10x16/cap-680-f-25v-20/dp/2811508).
- Kondansatör empedans ve ripple akımı değerleri dağıtıcı listelerinden alındı (Rubycon ve Panasonic PDF'leri bu oturumda okunamadı); sipariş öncesi üretici veri sayfasıyla karşılaştırılmalıdır.
- Açık çevrim: duty sabitken Vin veya yük değişirse çıkış 11 V'ta kalmaz. Gerçek O1 / S2E bağlanmaz.
